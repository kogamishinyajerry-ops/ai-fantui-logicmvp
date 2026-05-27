#!/usr/bin/env python3
"""Validate the M24 PR preflight artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-pr-preflight")
PACKAGE_NAME = "multi_agent_pr_preflight_v0_1.json"
SCHEMA_NAME = "multi_agent_pr_preflight_v0_1.schema.json"
EXPECTED_ORDER = [
    "multi-agent-cursor-baseline",
    "project-manager-status",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
    "m24-pr-preflight",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M24 multi-agent PR preflight.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--package", dest="package_path", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _package_path(*, artifact_dir: Path, package_path: Path | None) -> Path:
    if package_path is not None:
        return package_path
    return artifact_dir / PACKAGE_NAME


def _artifact_exists(path_value: Any) -> bool:
    if not isinstance(path_value, str) or not path_value:
        return False
    path = Path(path_value)
    return path.exists() and path.stat().st_size > 0


def verify_multi_agent_pr_preflight(package_path: Path) -> dict[str, Any]:
    mismatches: list[str] = []
    try:
        payload = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "package_path": str(package_path),
            "schema_valid": False,
            "html_exists": False,
            "markdown_exists": False,
            "mismatches": [f"package could not be loaded: {exc}"],
        }

    schema = _load_json(PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"preflight schema validation failed{location}: {error.message}")

    package_order = payload.get("pathspec_packages", [])
    observed_order = [
        package.get("package_id")
        for package in package_order
        if isinstance(package, dict)
    ]
    if observed_order != EXPECTED_ORDER:
        mismatches.append(f"pathspec package order must be {EXPECTED_ORDER!r}")

    validation_plan = payload.get("validation_plan", [])
    command_ids = [
        item.get("command_id")
        for item in validation_plan
        if isinstance(item, dict)
    ]
    if len(validation_plan) != 18:
        mismatches.append("validation_plan must contain 18 commands")
    if len(command_ids) != len(set(command_ids)):
        mismatches.append("validation command ids must be unique")
    if not all(
        isinstance(item, dict) and item.get("package_id") in EXPECTED_ORDER
        for item in validation_plan
    ):
        mismatches.append("validation commands must map to known packages")

    stage_commands = payload.get("stage_commands", [])
    if len(stage_commands) != 7:
        mismatches.append("stage_commands must contain 7 explicit commands")
    if not any(isinstance(command, str) and "git add -f --" in command for command in stage_commands):
        mismatches.append("stage commands must include git add -f for ignored Claude agents")
    protected_markers = [
        "src/well_harness/controller.py",
        "src/well_harness/runner.py",
        "src/well_harness/demo_server.py",
        "src/well_harness/static/",
        "artifacts/",
        ".planning/",
    ]
    for command in stage_commands:
        if not isinstance(command, str):
            mismatches.append("stage commands must be strings")
            continue
        for marker in protected_markers:
            if marker in command:
                mismatches.append(f"stage command includes excluded marker {marker}")

    blockers = payload.get("blockers", [])
    if not any(
        isinstance(item, dict)
        and item.get("blocker_id") == "notion-control-plane-404"
        and item.get("status") == "external_blocker"
        for item in blockers
    ):
        mismatches.append("Notion 404 must remain an external blocker")

    pr_body = payload.get("pr_body", {})
    body = pr_body.get("body", "") if isinstance(pr_body, dict) else ""
    for marker in [
        "notion-control-plane-404",
        "git add -f --",
        "make verify-multi-agent-packaging-consolidation",
        "make verify-multi-agent-pr-preflight",
        "tests/test_multi_agent_pr_preflight.py",
        "docs/coordination/multi-agent-pr-preflight.md",
    ]:
        if marker not in body:
            mismatches.append(f"PR body missing marker: {marker}")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("preflight_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("preflight_markdown"))
    if not html_exists:
        mismatches.append("preflight_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("preflight_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["preflight_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent PR Preflight",
            "multi-agent-cursor-baseline",
            "ultrawork-monitor",
            "m23-packaging-consolidation",
            "notion-control-plane-404",
            "git add -f --",
        ]:
            if marker not in html:
                mismatches.append(f"preflight HTML missing marker: {marker}")

    return {
        "status": "pass" if not mismatches else "fail",
        "package_path": str(package_path),
        "schema_valid": not errors,
        "html_exists": html_exists,
        "markdown_exists": markdown_exists,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    result = verify_multi_agent_pr_preflight(
        _package_path(artifact_dir=args.artifact_dir, package_path=args.package_path),
    )
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for mismatch in result["mismatches"]:
            print(f"- {mismatch}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the M25 validation evidence artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-validation-evidence")
PACKAGE_NAME = "multi_agent_validation_evidence_v0_1.json"
SCHEMA_NAME = "multi_agent_validation_evidence_v0_1.schema.json"
EXPECTED_PACKAGES = [
    "multi-agent-cursor-baseline-v0-2",
    "project-manager-status",
    "candidate-review-runtime-export",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
    "m24-pr-preflight",
    "m25-validation-evidence",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M25 multi-agent validation evidence.")
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


def verify_multi_agent_validation_evidence(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"evidence schema validation failed{location}: {error.message}")

    observed_packages = [
        package.get("package_id")
        for package in payload.get("pathspec_packages", [])
        if isinstance(package, dict)
    ]
    if observed_packages != EXPECTED_PACKAGES:
        mismatches.append(f"pathspec package order must be {EXPECTED_PACKAGES!r}")

    validation_plan = payload.get("validation_plan", [])
    validation_results = payload.get("validation_results", [])
    if len(validation_plan) != 21:
        mismatches.append("validation_plan must contain 21 commands")
    if len(validation_results) != 21:
        mismatches.append("validation_results must contain 21 command results")
    plan_by_id = {
        item.get("command_id"): item
        for item in validation_plan
        if isinstance(item, dict)
    }
    for result in validation_results if isinstance(validation_results, list) else []:
        if not isinstance(result, dict):
            mismatches.append("validation result entries must be objects")
            continue
        plan_item = plan_by_id.get(result.get("command_id"))
        if plan_item is None:
            mismatches.append(f"unexpected command result id {result.get('command_id')}")
            continue
        if result.get("command") != plan_item.get("command"):
            mismatches.append(f"command result mismatch for {result.get('command_id')}")
        if result.get("status") != "pass" or result.get("exit_code") != 0:
            mismatches.append(f"command did not pass: {result.get('command_id')}")

    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        if summary.get("passed_command_count") != 21:
            mismatches.append("passed_command_count must be 21")
        if summary.get("failed_command_count") != 0:
            mismatches.append("failed_command_count must be 0")
        if summary.get("stage_command_count") != 9:
            mismatches.append("stage_command_count must be 9")
    else:
        mismatches.append("summary must be an object")

    stage_commands = payload.get("stage_commands", [])
    if len(stage_commands) != 9:
        mismatches.append("stage_commands must contain 9 explicit commands")
    if not any(isinstance(command, str) and "git add -f --" in command for command in stage_commands):
        mismatches.append("stage commands must include git add -f for ignored Claude agents")
    if not any(
        isinstance(command, str) and "tests/test_multi_agent_validation_evidence.py" in command
        for command in stage_commands
    ):
        mismatches.append("stage commands must include M25 validation evidence test")
    protected_markers = [
        "src/well_harness/controller.py",
        "src/well_harness/runner.py",
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

    note = payload.get("pr_evidence_note", "")
    for marker in ["21 validation commands passed", "notion-control-plane-404"]:
        if marker not in note:
            mismatches.append(f"PR evidence note missing marker: {marker}")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("evidence_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("evidence_markdown"))
    if not html_exists:
        mismatches.append("evidence_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("evidence_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["evidence_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Validation Evidence",
            "multi-agent-cursor-baseline-v0-2-01",
            "m24-pr-preflight-03",
            "m25-validation-evidence",
            "notion-control-plane-404",
            "21 validation commands passed",
        ]:
            if marker not in html:
                mismatches.append(f"evidence HTML missing marker: {marker}")

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
    result = verify_multi_agent_validation_evidence(
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

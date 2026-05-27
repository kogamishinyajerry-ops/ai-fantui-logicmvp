#!/usr/bin/env python3
"""Validate the M23 packaging consolidation artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-packaging-consolidation")
PACKAGE_NAME = "multi_agent_packaging_consolidation_v0_1.json"
SCHEMA_NAME = "multi_agent_packaging_consolidation_v0_1.schema.json"
EXPECTED_ORDER = [
    "multi-agent-cursor-baseline",
    "project-manager-status",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M23 packaging consolidation.")
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


def verify_multi_agent_packaging_consolidation(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"packaging schema validation failed{location}: {error.message}")

    package_order = payload.get("package_order", [])
    observed_order = [
        package.get("package_id")
        for package in package_order
        if isinstance(package, dict)
    ]
    if observed_order != EXPECTED_ORDER:
        mismatches.append(f"package order must be {EXPECTED_ORDER!r}")

    for package in package_order if isinstance(package_order, list) else []:
        if not isinstance(package, dict):
            mismatches.append("package_order entries must be objects")
            continue
        if package.get("missing_pathspecs"):
            mismatches.append(f"{package.get('package_id')} has missing pathspecs")
        for pathspec in package.get("pathspecs", []) + package.get("forced_pathspecs", []):
            if pathspec.startswith("artifacts/") or pathspec.startswith(".planning/"):
                mismatches.append(f"{package.get('package_id')} includes excluded pathspec {pathspec}")
            if pathspec in {
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/demo_server.py",
            }:
                mismatches.append(f"{package.get('package_id')} includes protected pathspec {pathspec}")

    excluded = payload.get("excluded_paths", [])
    for required in [
        "artifacts/**",
        "src/well_harness/controller.py",
        "src/well_harness/demo_server.py",
        "src/well_harness/static/**",
        ".planning/**",
    ]:
        if required not in excluded:
            mismatches.append(f"excluded_paths must include {required}")

    blockers = payload.get("blockers", [])
    if not any(
        isinstance(item, dict)
        and item.get("blocker_id") == "notion-control-plane-404"
        and item.get("status") == "external_blocker"
        for item in blockers
    ):
        mismatches.append("Notion 404 must remain an external blocker")

    stage_commands = payload.get("stage_commands", [])
    if not any(isinstance(command, str) and "git add -f --" in command for command in stage_commands):
        mismatches.append("stage commands must include git add -f for ignored Claude agents")
    if not any(
        isinstance(command, str) and "docs/coordination/multi-agent-operator-cockpit.md" in command
        for command in stage_commands
    ):
        mismatches.append("stage commands must include M22 cockpit doc")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("package_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("package_markdown"))
    if not html_exists:
        mismatches.append("package_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("package_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["package_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Packaging Consolidation",
            "multi-agent-cursor-baseline",
            "ultrawork-monitor",
            "m22-operator-cockpit",
            "notion-control-plane-404",
        ]:
            if marker not in html:
                mismatches.append(f"package HTML missing marker: {marker}")

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
    result = verify_multi_agent_packaging_consolidation(
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

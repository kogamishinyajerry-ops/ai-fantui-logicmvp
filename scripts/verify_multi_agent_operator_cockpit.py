#!/usr/bin/env python3
"""Validate the multi-agent operator cockpit package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-operator-cockpit")
COCKPIT_NAME = "multi_agent_operator_cockpit_v0_1.json"
SCHEMA_NAME = "multi_agent_operator_cockpit_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a multi-agent operator cockpit artifact.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory containing multi_agent_operator_cockpit_v0_1.json.",
    )
    parser.add_argument(
        "--cockpit",
        type=Path,
        default=None,
        help="Explicit cockpit JSON path. Overrides --artifact-dir.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cockpit_path(*, artifact_dir: Path, cockpit_path: Path | None) -> Path:
    if cockpit_path is not None:
        return cockpit_path
    return artifact_dir / COCKPIT_NAME


def _artifact_exists(path_value: Any) -> bool:
    if not isinstance(path_value, str) or not path_value:
        return False
    path = Path(path_value)
    return path.exists() and path.stat().st_size > 0


def verify_multi_agent_operator_cockpit(cockpit_path: Path) -> dict[str, Any]:
    mismatches: list[str] = []
    try:
        payload = _load_json(cockpit_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "cockpit_path": str(cockpit_path),
            "schema_valid": False,
            "html_exists": False,
            "markdown_exists": False,
            "mismatches": [f"cockpit could not be loaded: {exc}"],
        }

    schema = _load_json(PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"cockpit schema validation failed{location}: {error.message}")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("cockpit_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("cockpit_markdown"))
    if not html_exists:
        mismatches.append("cockpit_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("cockpit_markdown artifact must exist and be non-empty")
    for key in [
        "project_status_json",
        "project_status_html",
        "ultrawork_dashboard_json",
        "ultrawork_dashboard_html",
    ]:
        if not _artifact_exists(artifact_paths.get(key)):
            mismatches.append(f"{key} artifact must exist and be non-empty")

    blockers = payload.get("blockers", [])
    if any(
        isinstance(item, dict)
        and "notion" in str(item.get("blocker_id", "")).lower()
        for item in blockers
    ):
        mismatches.append("external planning blockers must not be recorded as active blockers")

    expected_agents = {
        "ChiefEngineerOrchestrator",
        "LogicIRRepairAgent",
        "EvidenceValidationAgent",
        "SafetyRequirementsReviewer",
        "PackagingPRReadinessAgent",
    }
    agent_team = payload.get("agent_team", {})
    if not isinstance(agent_team, dict):
        mismatches.append("agent_team must be present")
    else:
        active_agents = agent_team.get("active_agents", [])
        if isinstance(active_agents, list):
            names = {item.get("name") for item in active_agents if isinstance(item, dict)}
        else:
            names = set()
        if agent_team.get("mode") != "five_agent_context_cap":
            mismatches.append("agent_team.mode must be five_agent_context_cap")
        if agent_team.get("team_size") != 5 or names != expected_agents:
            mismatches.append("agent_team must define exactly five active agents")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict) or any(value != "pass" for value in gates.values()):
        mismatches.append("all cockpit gates must pass")

    boundary = payload.get("dependency_boundary", {})
    if not isinstance(boundary, dict):
        mismatches.append("dependency_boundary must be present")
    else:
        if boundary.get("controller_truth_modified") is not False:
            mismatches.append("controller truth boundary must remain false")
        if boundary.get("ui_layout_modified") is not False:
            mismatches.append("UI layout boundary must remain false")
        excluded = boundary.get("excluded_paths", [])
        for required in [
            "src/well_harness/controller.py",
            "src/well_harness/demo_server.py",
            "src/well_harness/static/**",
            ".planning/**",
            "artifacts/**",
        ]:
            if required not in excluded:
                mismatches.append(f"excluded_paths must include {required}")

    html_path = Path(str(artifact_paths.get("cockpit_html", "")))
    if html_exists:
        html = html_path.read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Operator Cockpit",
            "Project Manager Status",
            "UltraWork Monitor",
            "five_agent_context_cap",
            "PackagingPRReadinessAgent",
            "repo_github_local_artifacts",
            "RUN-QUEUE-011",
        ]:
            if marker not in html:
                mismatches.append(f"cockpit HTML missing marker: {marker}")

    return {
        "status": "pass" if not mismatches else "fail",
        "cockpit_path": str(cockpit_path),
        "schema_valid": not errors,
        "html_exists": html_exists,
        "markdown_exists": markdown_exists,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    result = verify_multi_agent_operator_cockpit(
        _cockpit_path(artifact_dir=args.artifact_dir, cockpit_path=args.cockpit),
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

#!/usr/bin/env python3
"""Validate the M29 merge-readiness packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-merge-readiness")
PACKAGE_NAME = "multi_agent_merge_readiness_v0_1.json"
SCHEMA_NAME = "multi_agent_merge_readiness_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M29 multi-agent merge readiness.")
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


def verify_multi_agent_merge_readiness(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"merge readiness schema validation failed{location}: {error.message}")

    if payload.get("status") not in {"ready_for_review", "ready_with_external_blocker"}:
        mismatches.append("readiness status must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("passed_command_count") != 19:
            mismatches.append("passed_command_count must be 19")
        if summary.get("failed_command_count") != 0:
            mismatches.append("failed_command_count must be 0")
        if summary.get("geometry_check_count") < 10:
            mismatches.append("geometry_check_count must cover five pages across two viewports")
        if summary.get("mergeable") != "MERGEABLE":
            mismatches.append("PR mergeability must be MERGEABLE")
        if summary.get("notion_blocker") != "external_blocker":
            mismatches.append("Notion blocker must remain external")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "validation_evidence",
            "geometry_gate",
            "pathspec_boundary",
            "notion_external_blocker",
            "pr_mergeability",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")
        if gates.get("review_state") not in {"pass", "warning"}:
            mismatches.append("review_state gate must be pass or warning")

    geometry_results = payload.get("geometry_results", [])
    if not isinstance(geometry_results, list) or len(geometry_results) < 10:
        mismatches.append("geometry_results must include at least ten entries")
    else:
        for item in geometry_results:
            if not isinstance(item, dict):
                mismatches.append("geometry result entries must be objects")
                continue
            if item.get("status") != "pass":
                mismatches.append(f"geometry result did not pass: {item.get('page')} {item.get('viewport')}")
            if int(item.get("overflow_px", 999)) > 1:
                mismatches.append(f"geometry overflow detected: {item.get('page')} {item.get('viewport')}")
            if not _artifact_exists(item.get("screenshot")):
                mismatches.append(f"geometry screenshot missing: {item.get('screenshot')}")

    blockers = payload.get("blockers", [])
    if not any(
        isinstance(item, dict)
        and item.get("blocker_id") == "notion-control-plane-404"
        and item.get("status") == "external_blocker"
        for item in blockers
    ):
        mismatches.append("Notion 404 must remain an external blocker")

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

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("readiness_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("readiness_markdown"))
    if not html_exists:
        mismatches.append("readiness_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("readiness_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["readiness_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Merge Readiness",
            "five_agent_context_cap",
            "PackagingPRReadinessAgent",
            "RUN-QUEUE-011",
            "19 validation commands passed",
            "notion-control-plane-404",
            "MERGEABLE",
        ]:
            if marker not in html:
                mismatches.append(f"readiness HTML missing marker: {marker}")

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
    result = verify_multi_agent_merge_readiness(
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

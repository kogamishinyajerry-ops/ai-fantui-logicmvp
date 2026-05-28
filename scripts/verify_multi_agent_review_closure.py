#!/usr/bin/env python3
"""Validate the M30 review-closure packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-review-closure")
PACKAGE_NAME = "multi_agent_review_closure_v0_1.json"
SCHEMA_NAME = "multi_agent_review_closure_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M30 multi-agent review closure.")
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


def verify_multi_agent_review_closure(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"review closure schema validation failed{location}: {error.message}")

    if payload.get("status") not in {"ready_for_owner_acceptance", "ready_with_warnings"}:
        mismatches.append("review closure status must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("latest_clean_codex_result_found") is not True:
            mismatches.append("latest clean Codex result must be recorded")
        if summary.get("actionable_thread_count") != 0:
            mismatches.append("actionable_thread_count must be zero")
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must exclude external planning surfaces")
        if summary.get("recommended_next_action") not in {
            "project_owner_acceptance_or_merge_when_authorized",
        }:
            mismatches.append("recommended_next_action must be owner acceptance or authorized merge")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "latest_head_review",
            "actionable_threads",
            "pr_mergeability",
            "control_plane_boundary",
            "pathspec_boundary",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")

    agent_team = payload.get("agent_team", {})
    if not isinstance(agent_team, dict):
        mismatches.append("agent_team must be present")
    else:
        active_agents = agent_team.get("active_agents", [])
        names = {
            item.get("name")
            for item in active_agents
            if isinstance(item, dict)
        } if isinstance(active_agents, list) else set()
        if agent_team.get("mode") != "five_agent_context_cap":
            mismatches.append("agent_team.mode must be five_agent_context_cap")
        if agent_team.get("team_size") != 5 or len(names) != 5:
            mismatches.append("agent_team must define exactly five active agents")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("review closure packet must not record active blockers")

    pathspec_package = payload.get("pathspec_package", {})
    if not isinstance(pathspec_package, dict):
        mismatches.append("pathspec_package must be present")
    else:
        pathspecs = pathspec_package.get("pathspecs", [])
        if "src/well_harness/multi_agent_review_closure.py" not in pathspecs:
            mismatches.append("pathspec package must include review-closure source")
        excluded = pathspec_package.get("excluded_paths", [])
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        stage_command = str(pathspec_package.get("stage_command", ""))
        if ".planning/notion_control_plane.json" in stage_command:
            mismatches.append("stage command must not stage Notion control-plane config")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("closure_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("closure_markdown"))
    if not html_exists:
        mismatches.append("closure_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("closure_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["closure_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Review Closure",
            "Latest Codex clean",
            "Actionable threads",
            "repo_github_local_artifacts_only",
            "project_owner_acceptance_or_merge_when_authorized",
        ]:
            if marker not in html:
                mismatches.append(f"closure HTML missing marker: {marker}")

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
    result = verify_multi_agent_review_closure(
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

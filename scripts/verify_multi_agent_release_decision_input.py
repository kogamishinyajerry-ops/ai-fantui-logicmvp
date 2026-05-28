#!/usr/bin/env python3
"""Validate the M31 release decision input."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-release-decision-input")
PACKAGE_NAME = "multi_agent_release_decision_input_v0_1.json"
SCHEMA_NAME = "multi_agent_release_decision_input_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M31 multi-agent release decision input.")
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


def verify_multi_agent_release_decision_input(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"release decision input schema validation failed{location}: {error.message}")

    if payload.get("status") not in {
        "ready_for_owner_decision",
        "ready_for_owner_decision_with_warnings",
    }:
        mismatches.append("release decision input must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("latest_clean_codex_result_found") is not True:
            mismatches.append("latest clean Codex result must be true")
        if summary.get("actionable_thread_count") != 0:
            mismatches.append("actionable_thread_count must be zero")
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must be repo_github_local_artifacts_only")
        if summary.get("recommended_owner_action") not in {
            "owner_acceptance_when_authorized",
            "owner_acceptance_or_wait_for_remote_checks",
        }:
            mismatches.append("recommended_owner_action must be owner-facing")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "review_closure",
            "review_closure_blockers",
            "latest_head_review",
            "actionable_reviews",
            "mergeability",
            "control_plane_boundary",
            "owner_authorization_boundary",
            "pathspec_boundary",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")

    options = payload.get("decision_options", [])
    if not isinstance(options, list) or not options:
        mismatches.append("decision_options must be non-empty")
    else:
        by_id = {item.get("option_id"): item for item in options if isinstance(item, dict)}
        if by_id.get("owner_acceptance", {}).get("enabled") is not True:
            mismatches.append("owner_acceptance option must be enabled")
        if by_id.get("merge_when_authorized", {}).get("enabled") is not False:
            mismatches.append("merge_when_authorized option must remain disabled")
        for item in options:
            if not isinstance(item, dict):
                mismatches.append("decision option entries must be objects")
                continue
            if item.get("automation_action") == "merge":
                mismatches.append("decision options must never automate merge")

    boundaries = payload.get("decision_boundaries", {})
    if not isinstance(boundaries, dict):
        mismatches.append("decision_boundaries must be present")
    else:
        expected = {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "notion_control_plane_changes": "out_of_scope",
        }
        for key, value in expected.items():
            if boundaries.get(key) != value:
                mismatches.append(f"{key} boundary must be {value}")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("release decision input must not record active blockers")

    pathspec_package = payload.get("pathspec_package", {})
    if not isinstance(pathspec_package, dict):
        mismatches.append("pathspec_package must be present")
    else:
        pathspecs = pathspec_package.get("pathspecs", [])
        if "src/well_harness/multi_agent_release_decision_input.py" not in pathspecs:
            mismatches.append("pathspec package must include M31 source")
        excluded = pathspec_package.get("excluded_paths", [])
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        if ".planning/notion_control_plane.json" in str(pathspec_package.get("stage_command", "")):
            mismatches.append("stage command must not stage Notion control-plane config")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("decision_input_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("decision_input_markdown"))
    if not html_exists:
        mismatches.append("decision_input_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("decision_input_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["decision_input_html"])).read_text(encoding="utf-8")
        html_markers = [
            "Multi-Agent Release Decision Input",
            "Recommended owner action",
            "Decision Options",
            "disabled",
            "repo_github_local_artifacts_only",
        ]
        if isinstance(summary, dict) and isinstance(summary.get("recommended_owner_action"), str):
            html_markers.append(summary["recommended_owner_action"])
        for marker in html_markers:
            if marker not in html:
                mismatches.append(f"decision input HTML missing marker: {marker}")

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
    result = verify_multi_agent_release_decision_input(
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

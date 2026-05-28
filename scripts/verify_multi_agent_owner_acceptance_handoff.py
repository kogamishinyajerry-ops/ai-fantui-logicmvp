#!/usr/bin/env python3
"""Validate the M32 owner acceptance handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-acceptance-handoff")
PACKAGE_NAME = "multi_agent_owner_acceptance_handoff_v0_1.json"
SCHEMA_NAME = "multi_agent_owner_acceptance_handoff_v0_1.schema.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M32 owner acceptance handoff.")
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


def verify_multi_agent_owner_acceptance_handoff(package_path: Path) -> dict[str, Any]:
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
        mismatches.append(f"owner acceptance handoff schema validation failed{location}: {error.message}")

    if payload.get("status") not in {
        "ready_for_owner_acceptance",
        "ready_for_owner_acceptance_with_warnings",
    }:
        mismatches.append("owner acceptance handoff must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must be repo_github_local_artifacts_only")
        if summary.get("handoff_mode") != "read_only_owner_acceptance_handoff":
            mismatches.append("handoff_mode must be read_only_owner_acceptance_handoff")
        if summary.get("current_actionable_thread_count") != 0:
            mismatches.append("current_actionable_thread_count must be zero")
        if summary.get("handoff_remote_checks_state") not in {
            "pass",
            "no_checks_reported",
            "pending_or_unknown",
        }:
            mismatches.append("handoff_remote_checks_state must be pass or warning-compatible")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "release_decision_input",
            "release_decision_blockers",
            "current_actionable_reviews",
            "pr_mergeability",
            "control_plane_boundary",
            "owner_authority_boundary",
            "pathspec_boundary",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")
        if gates.get("outdated_review_threads") not in {"pass", "warning"}:
            mismatches.append("outdated_review_threads gate must be pass or warning")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("owner acceptance handoff must not record active blockers")

    boundaries = payload.get("decision_boundaries", {})
    if not isinstance(boundaries, dict):
        mismatches.append("decision_boundaries must be present")
    else:
        expected = {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_final_decision": "external_manual_only",
            "notion_control_plane_changes": "out_of_scope",
        }
        for key, value in expected.items():
            if boundaries.get(key) != value:
                mismatches.append(f"{key} boundary must be {value}")

    checklist = payload.get("owner_acceptance_checklist", [])
    if not isinstance(checklist, list) or len(checklist) < 5:
        mismatches.append("owner_acceptance_checklist must include at least five items")
    else:
        checklist_ids = {item.get("item_id") for item in checklist if isinstance(item, dict)}
        for required in {
            "owner-review-pr-evidence",
            "owner-confirm-no-actionable-review",
            "owner-decide-remote-check-warning",
            "owner-preserve-boundary",
            "owner-final-decision-if-needed",
        }:
            if required not in checklist_ids:
                mismatches.append(f"owner_acceptance_checklist missing {required}")

    pathspec_package = payload.get("pathspec_package", {})
    if not isinstance(pathspec_package, dict):
        mismatches.append("pathspec_package must be present")
    else:
        pathspecs = pathspec_package.get("pathspecs", [])
        if "src/well_harness/multi_agent_owner_acceptance_handoff.py" not in pathspecs:
            mismatches.append("pathspec package must include M32 source")
        excluded = pathspec_package.get("excluded_paths", [])
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        if ".planning/notion_control_plane.json" in str(pathspec_package.get("stage_command", "")):
            mismatches.append("stage command must not stage Notion control-plane config")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("handoff_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("handoff_markdown"))
    if not html_exists:
        mismatches.append("handoff_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("handoff_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["handoff_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Owner Acceptance Handoff",
            "Owner Acceptance Checklist",
            "repo_github_local_artifacts_only",
            "external_manual_only",
            "notion_control_plane_changes",
        ]:
            if marker not in html:
                mismatches.append(f"handoff HTML missing marker: {marker}")

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
    result = verify_multi_agent_owner_acceptance_handoff(
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

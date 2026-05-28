#!/usr/bin/env python3
"""Validate the M33 owner decision request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-decision-request")
PACKAGE_NAME = "multi_agent_owner_decision_request_v0_1.json"
SCHEMA_NAME = "multi_agent_owner_decision_request_v0_1.schema.json"
TEMPLATE_NAME = "owner_decision_input_template_v0_1.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M33 owner decision request.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--package", type=Path, default=None)
    parser.add_argument("--schema", type=Path, default=PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_multi_agent_owner_decision_request(package_path: Path, schema_path: Path) -> dict[str, Any]:
    """Verify schema and deterministic M33 owner decision request boundaries."""
    payload = _load_json(package_path)
    schema = _load_json(schema_path)
    mismatches: list[str] = []
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    for error in errors:
        location = f" at {'/'.join(str(part) for part in error.path)}" if error.path else ""
        mismatches.append(f"owner decision request schema validation failed{location}: {error.message}")

    if payload.get("status") not in {
        "awaiting_owner_decision",
        "awaiting_owner_decision_with_warnings",
    }:
        mismatches.append("owner decision request must await an explicit owner decision, not record one")

    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        if summary.get("decision_request_mode") != "read_only_owner_decision_request":
            mismatches.append("decision_request_mode must be read_only_owner_decision_request")
        if summary.get("decision_input_required") is not True:
            mismatches.append("decision_input_required must be true")
        if summary.get("decision_recorded") is not False:
            mismatches.append("decision_recorded must remain false")
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must stay repo_github_local_artifacts_only")
    else:
        mismatches.append("summary must be an object")

    gates = payload.get("gates", {})
    if isinstance(gates, dict):
        for required in (
            "owner_acceptance_handoff",
            "m32_active_blockers",
            "owner_decision_input_required",
            "owner_decision_authority",
            "control_plane_boundary",
            "pathspec_boundary",
        ):
            if gates.get(required) not in {"pass", "warning"}:
                mismatches.append(f"{required} gate must pass or warn")
    else:
        mismatches.append("gates must be an object")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("owner decision request must not record active blockers")

    boundaries = payload.get("decision_boundaries", {})
    if isinstance(boundaries, dict):
        expected_boundaries = {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_decision_recording": "external_manual_input_only",
            "notion_control_plane_changes": "out_of_scope",
        }
        for key, expected in expected_boundaries.items():
            if boundaries.get(key) != expected:
                mismatches.append(f"decision_boundaries.{key} must be {expected}")
    else:
        mismatches.append("decision_boundaries must be an object")

    options = payload.get("decision_options", [])
    option_ids = {
        item.get("option_id")
        for item in options
        if isinstance(item, dict)
    } if isinstance(options, list) else set()
    for required in (
        "accept_when_authorized",
        "wait_for_remote_checks",
        "request_review_followup",
        "return_to_development",
    ):
        if required not in option_ids:
            mismatches.append(f"decision_options missing {required}")

    template = payload.get("decision_input_template", {})
    if isinstance(template, dict):
        if template.get("template_mode") is not True:
            mismatches.append("decision_input_template must stay in template_mode")
        attestation = template.get("attestation", {})
        if not isinstance(attestation, dict) or attestation.get("decision_is_explicit") is not False:
            mismatches.append("decision_input_template must not be an explicit owner decision")
        acknowledged = set(attestation.get("acknowledged_boundaries", [])) if isinstance(attestation, dict) else set()
        if "notion_control_plane_out_of_scope" not in acknowledged:
            mismatches.append("decision_input_template must acknowledge Notion is out of scope")
    else:
        mismatches.append("decision_input_template must be an object")

    artifact_paths = payload.get("artifact_paths", {})
    if isinstance(artifact_paths, dict):
        for key in ("request_json", "request_markdown", "request_html", "decision_input_template"):
            path_value = artifact_paths.get(key)
            if not path_value or not Path(path_value).exists():
                mismatches.append(f"artifact_paths.{key} must exist")
        template_path = Path(artifact_paths.get("decision_input_template") or package_path.parent / TEMPLATE_NAME)
        if template_path.exists():
            written_template = _load_json(template_path)
            if written_template != template:
                mismatches.append("written decision input template must match package payload")
    else:
        mismatches.append("artifact_paths must be an object")

    pathspec_package = payload.get("pathspec_package", {})
    if isinstance(pathspec_package, dict):
        pathspecs = pathspec_package.get("pathspecs", [])
        excluded = pathspec_package.get("excluded_paths", [])
        if "src/well_harness/multi_agent_owner_decision_request.py" not in pathspecs:
            mismatches.append("pathspec package must include owner decision request source")
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        if ".planning/notion_control_plane.json" in str(pathspec_package.get("stage_command", "")):
            mismatches.append("stage command must not stage Notion control-plane config")
    else:
        mismatches.append("pathspec_package must be an object")

    html_path = Path(artifact_paths.get("request_html", "")) if isinstance(artifact_paths, dict) else Path()
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        for marker in (
            "Multi-Agent Owner Decision Request",
            "Decision input required",
            "Decision recorded",
            "notion_control_plane_changes",
        ):
            if marker not in html:
                mismatches.append(f"HTML missing marker {marker!r}")

    return {
        "status": "pass" if not mismatches else "fail",
        "package_path": str(package_path),
        "schema_valid": not errors,
        "html_exists": html_path.exists(),
        "template_exists": (
            isinstance(artifact_paths, dict)
            and Path(artifact_paths.get("decision_input_template", "")).exists()
        ),
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    package_path = args.package or args.artifact_dir / PACKAGE_NAME
    result = verify_multi_agent_owner_decision_request(package_path, args.schema)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for mismatch in result["mismatches"]:
            print(f"- {mismatch}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

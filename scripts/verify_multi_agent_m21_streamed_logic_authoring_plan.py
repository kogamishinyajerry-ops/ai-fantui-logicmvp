#!/usr/bin/env python3
"""Verify the M21 streamed logic authoring specialist-team plan package."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import ACTIVE_AGENT_TEAM, FIVE_AGENT_TEAM_MODE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = (
    Path("/tmp/ai-fantui-multi-agent-m21-streamed-logic-authoring-plan")
    / "multi_agent_m21_streamed_logic_authoring_plan_v0_1.json"
)
EXPECTED_BOUNDARY_NON_CLAIMS = {
    "no C919 ETRAS correctness claim",
    "no controller truth promotion",
    "no production readiness claim",
    "no certification or DAL readiness claim",
    "no automatic requirements document mutation",
    "no whole-graph black-box generation acceptance",
}
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m21_streamed_logic_authoring_plan_v0_1.json.",
    )
    parser.add_argument("--package", dest="package_path", type=Path, default=DEFAULT_PACKAGE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _load_json(path: Path, mismatches: list[str]) -> dict[str, Any]:
    if not path.exists():
        mismatches.append(f"package missing: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        mismatches.append(f"package is not valid JSON: {exc}")
        return {}


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _restricted_diff() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *RESTRICTED_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ["<git status failed>"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _package_shape_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    expected = {
        "kind": "ai-fantui-multi-agent-m21-streamed-logic-authoring-plan",
        "package_id": "multi-agent-m21-streamed-logic-authoring-plan-v0.1",
        "status": "pass",
        "plan_status": "ready_for_m21_planning_review",
    }
    for key, value in expected.items():
        if package.get(key) != value:
            mismatches.append(f"{key} must be {value!r}")
            valid = False
    milestone = package.get("milestone", {})
    if not isinstance(milestone, dict) or milestone.get("id") != "M21-candidate":
        mismatches.append("milestone.id must be M21-candidate")
        valid = False
    return valid


def _activation_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if package.get("activation_status") != "blocked_until_project_owner_final_acceptance":
        mismatches.append("activation_status must remain blocked until project-owner final acceptance")
        valid = False
    gates = package.get("activation_gates", {})
    if not isinstance(gates, dict):
        mismatches.append("activation_gates must be an object")
        return False
    if gates.get("project_owner_final_decision") != "blocked":
        mismatches.append("project_owner_final_decision activation gate must be blocked")
        valid = False
    return valid


def _team_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    team = package.get("team_roster", [])
    if not isinstance(team, list):
        mismatches.append("team_roster must be a list")
        return False
    ids = [item.get("id") for item in team if isinstance(item, dict)]
    expected = [item["agent_id"] for item in ACTIVE_AGENT_TEAM]
    if ids != expected:
        mismatches.append("team_roster must define the five active agents in order")
        return False
    agent_team = package.get("agent_team", {})
    if not isinstance(agent_team, dict):
        mismatches.append("agent_team must be present")
        return False
    active_agent_ids = [
        item.get("agent_id")
        for item in agent_team.get("active_agents", [])
        if isinstance(item, dict)
    ]
    if agent_team.get("mode") != FIVE_AGENT_TEAM_MODE or agent_team.get("team_size") != 5:
        mismatches.append("agent_team must use five_agent_context_cap with team_size 5")
        return False
    if active_agent_ids != expected:
        mismatches.append("agent_team.active_agents must match team_roster")
        return False
    return True


def _workstreams_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    workstreams = package.get("workstreams", [])
    checks = package.get("acceptance_checks", [])
    valid = True
    if not isinstance(workstreams, list) or len(workstreams) != 6:
        mismatches.append("workstreams must contain six items")
        valid = False
    if not isinstance(checks, list) or len(checks) != 8:
        mismatches.append("acceptance_checks must contain eight items")
        valid = False
    check_ids = [item.get("id") for item in checks if isinstance(item, dict)]
    for required in (
        "one_edit_at_a_time",
        "active_edit_visible",
        "source_excerpt_visible",
        "user_confirm_commits",
        "requirements_edit_authorized",
        "truth_boundary_preserved",
    ):
        if required not in check_ids:
            mismatches.append(f"acceptance_checks must include {required}")
            valid = False
    return valid


def _reuse_anchors_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    anchors = package.get("reuse_anchors", [])
    if not isinstance(anchors, list):
        mismatches.append("reuse_anchors must be a list")
        return False
    ids = [item.get("id") for item in anchors if isinstance(item, dict)]
    valid = True
    for required in (
        "logic_stream_timeline",
        "drawing_replay_events",
        "active_node_wire_highlight",
        "source_provenance",
        "confirm_before_update",
        "server_confirmation_boundary",
    ):
        if required not in ids:
            mismatches.append(f"reuse_anchors must include {required}")
            valid = False
    for item in anchors:
        if not isinstance(item, dict):
            valid = False
            continue
        path = PROJECT_ROOT / str(item.get("path", ""))
        if not path.exists():
            mismatches.append(f"reuse anchor path must exist: {item.get('path')}")
            valid = False
    return valid


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if _restricted_diff():
        mismatches.append("restricted controller/intake paths must have no diff")
        valid = False
    non_claims = set(str(item) for item in package.get("non_claims", []))
    missing = EXPECTED_BOUNDARY_NON_CLAIMS.difference(non_claims)
    for claim in sorted(missing):
        mismatches.append(f"non_claims must include {claim}")
        valid = False
    return valid


def _artifacts_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    paths = package.get("artifact_paths", {})
    if not isinstance(paths, dict):
        mismatches.append("artifact_paths must be an object")
        return False
    valid = True
    for key in (
        "plan_json",
        "plan_markdown",
        "plan_doc",
        "streamed_authoring_target_doc",
        "generalized_panel_target_doc",
    ):
        path = Path(str(paths.get(key, "")))
        if not path.exists():
            mismatches.append(f"artifact_paths.{key} must exist")
            valid = False
    return valid


def verify_multi_agent_m21_streamed_logic_authoring_plan(
    package_path: Path = DEFAULT_PACKAGE_PATH,
) -> dict[str, Any]:
    mismatches: list[str] = []
    package = _load_json(package_path, mismatches)
    gates = {
        "package_shape": _gate_status(bool(package) and _package_shape_valid(package, mismatches)),
        "activation_block": _gate_status(bool(package) and _activation_valid(package, mismatches)),
        "specialist_team": _gate_status(bool(package) and _team_valid(package, mismatches)),
        "workstreams": _gate_status(bool(package) and _workstreams_valid(package, mismatches)),
        "reuse_anchors": _gate_status(bool(package) and _reuse_anchors_valid(package, mismatches)),
        "boundary": _gate_status(bool(package) and _boundary_valid(package, mismatches)),
        "artifacts": _gate_status(bool(package) and _artifacts_valid(package, mismatches)),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        and not mismatches
        else "fail"
    )
    gates["local_gate"] = status
    return {
        "kind": "ai-fantui-multi-agent-m21-streamed-logic-authoring-plan-verification",
        "status": status,
        "package": str(package_path),
        "plan_status": package.get("plan_status", ""),
        "activation_status": package.get("activation_status", ""),
        "deterministic_gates": gates,
        "mismatches": mismatches,
    }


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: M21 streamed logic authoring plan verified")
        print(f"activation_status: {payload['activation_status']}")
    else:
        print(
            "FAIL: M21 streamed logic authoring plan failed "
            f"({', '.join(payload['mismatches'])})"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = verify_multi_agent_m21_streamed_logic_authoring_plan(args.package_path)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

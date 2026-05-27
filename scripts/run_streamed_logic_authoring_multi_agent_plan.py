#!/usr/bin/env python3
"""Generate the M21 candidate multi-agent plan for streamed logic authoring."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-m21-streamed-logic-authoring-plan")
PLAN_JSON_NAME = "multi_agent_m21_streamed_logic_authoring_plan_v0_1.json"
PLAN_MARKDOWN_NAME = "streamed_logic_authoring_multi_agent_plan.md"
TARGET_DOC_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "engineer-in-the-loop-streamed-logic-authoring-target.md"
)
GENERALIZED_TARGET_DOC_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "generalized-logic-circuit-control-panel-target.md"
)
PLAN_DOC_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "streamed-logic-authoring-multi-agent-plan.md"
)
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the streamed logic authoring multi-agent plan.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


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


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _doc_contains(path: Path, markers: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in markers)


def _team_roster() -> list[dict[str, Any]]:
    return [
        {
            "id": "chief-engineer-orchestrator",
            "label": "ChiefEngineerOrchestrator",
            "responsibility": "owns sequencing, handoffs, stop conditions, and final integration",
            "write_scope": ["coordination docs", "plan artifacts"],
        },
        {
            "id": "logic-ir-repair-agent",
            "label": "LogicIRRepairAgent",
            "responsibility": "turns interpreted requirements into one atomic node or wire edit and preserves candidate IR boundaries",
            "write_scope": ["candidate graph-edit proposals", "candidate logic IR only"],
        },
        {
            "id": "evidence-validation-agent",
            "label": "EvidenceValidationAgent",
            "responsibility": "validates provenance, replayability, screenshot gates, simulation evidence, and non-claim boundaries",
            "write_scope": ["evidence and review artifacts"],
        },
        {
            "id": "safety-requirements-reviewer",
            "label": "SafetyRequirementsReviewer",
            "responsibility": "extracts source excerpts, assumptions, states, signals, guards, ambiguities, and requirements-edit authorization risk",
            "write_scope": ["candidate interpretation artifacts", "requirements edit proposals"],
        },
        {
            "id": "packaging-pr-readiness-agent",
            "label": "PackagingPRReadinessAgent",
            "responsibility": "packages read-only review handoff, pathspec boundaries, and project-owner evidence",
            "write_scope": ["read-only review results", "pathspec and handoff docs"],
        },
    ]


def _workstreams() -> list[dict[str, Any]]:
    return [
        {
            "id": "S1",
            "owner": "safety-requirements-reviewer",
            "title": "source quote and interpretation contract",
            "deliverable": "each proposed edit carries source excerpt, interpreted requirement, assumptions, and ambiguity note",
            "done_when": "fixture proposal contains source document quote and interpretation fields",
        },
        {
            "id": "S2",
            "owner": "logic-ir-repair-agent",
            "title": "atomic graph-edit proposal",
            "deliverable": "one node or wire edit is proposed at a time with upstream/downstream context",
            "done_when": "proposal schema rejects whole-graph commits and accepts one atomic edit",
        },
        {
            "id": "S3",
            "owner": "logic-ir-repair-agent",
            "title": "candidate graph commit boundary",
            "deliverable": "confirmed edit appends to candidate graph history without touching controller truth",
            "done_when": "accepted edit changes candidate graph only and records user decision",
        },
        {
            "id": "S4",
            "owner": "evidence-validation-agent",
            "title": "active node or wire highlight",
            "deliverable": "UI marks the current pending node or wire and shows source text beside it",
            "done_when": "browser evidence proves active edit highlight and confirm/reject controls",
        },
        {
            "id": "S5",
            "owner": "safety-requirements-reviewer",
            "title": "requirements edit authorization",
            "deliverable": "source document edits are separate proposals and require explicit approval",
            "done_when": "requirements update cannot be committed without authorization record",
        },
        {
            "id": "S6",
            "owner": "packaging-pr-readiness-agent",
            "title": "stream replay and review packet",
            "deliverable": "confirmed edit sequence can be replayed and packaged for external review",
            "done_when": "review packet lists every confirmed/rejected/revised edit with provenance",
        },
    ]


def _acceptance_checks() -> list[dict[str, str]]:
    return [
        {
            "id": "one_edit_at_a_time",
            "check": "whole-graph generation is not accepted as a streamed authoring commit",
        },
        {
            "id": "active_edit_visible",
            "check": "pending node or wire is highlighted before commit",
        },
        {
            "id": "source_excerpt_visible",
            "check": "requirements source excerpt and interpreted logic are visible beside the active edit",
        },
        {
            "id": "user_confirm_commits",
            "check": "user confirmation commits exactly one candidate graph edit",
        },
        {
            "id": "user_feedback_revises",
            "check": "rejection or feedback creates a revised proposal without losing provenance",
        },
        {
            "id": "requirements_edit_authorized",
            "check": "requirements document edits require explicit authorization",
        },
        {
            "id": "replayable_history",
            "check": "final candidate graph can be replayed from confirmed edit history",
        },
        {
            "id": "truth_boundary_preserved",
            "check": "no controller truth, certification, production, or deployment claim is made",
        },
    ]


def _reuse_anchors() -> list[dict[str, Any]]:
    return [
        {
            "id": "logic_stream_timeline",
            "path": "src/well_harness/static/logic_builder/index.html",
            "lines": [63, 72, 295],
            "use": "reuse existing task, generation, and drawing stream rails",
            "gap": "current behavior is replay/progress style, not hardened backend streaming",
        },
        {
            "id": "drawing_replay_events",
            "path": "src/well_harness/static/logic_builder/logic_builder.js",
            "lines": [382, 412],
            "use": "reuse node/wire/source-anchor replay event construction",
            "gap": "needs one-edit-at-a-time proposal state",
        },
        {
            "id": "active_node_wire_highlight",
            "path": "src/well_harness/static/logic_builder/logic_builder.js",
            "lines": [1245, 2239, 2764],
            "use": "reuse active/blocked/fault styling and selected node/wire state",
            "gap": "needs pending-edit focus distinct from runtime active state",
        },
        {
            "id": "source_provenance",
            "path": "src/well_harness/static/logic_builder/logic_builder.js",
            "lines": [828, 2041, 2178],
            "use": "reuse quote extraction and source/local/assumption provenance surfaces",
            "gap": "needs mandatory source excerpt beside every pending edit",
        },
        {
            "id": "confirm_before_update",
            "path": "src/well_harness/static/logic_builder/index.html",
            "lines": [582, 589],
            "use": "reuse interpretation summary and confirm/cancel controls",
            "gap": "reject is currently cancel/continue, not a persisted reject event",
        },
        {
            "id": "server_confirmation_boundary",
            "path": "src/well_harness/requirements_intake/logic_builder.py",
            "lines": [1679, 2576],
            "use": "reuse needs_user_confirmation and confirmed_by_user update guard",
            "gap": "needs streamed authoring proposal history and replay evidence",
        },
    ]


def _markdown_plan(payload: dict[str, Any]) -> str:
    team = "\n".join(
        f"- {member['label']}: {member['responsibility']}"
        for member in payload["team_roster"]
    )
    workstreams = "\n".join(
        f"- {item['id']} / {item['owner']}: {item['title']} - {item['deliverable']}"
        for item in payload["workstreams"]
    )
    checks = "\n".join(
        f"- {item['id']}: {item['check']}"
        for item in payload["acceptance_checks"]
    )
    anchors = "\n".join(
        f"- {item['id']}: `{item['path']}` lines {', '.join(str(line) for line in item['lines'])} - {item['use']}"
        for item in payload["reuse_anchors"]
    )
    gates = "\n".join(
        f"- {name}: `{status}`"
        for name, status in payload["deterministic_gates"].items()
    )
    return (
        "# Streamed Logic Authoring Multi-Agent Plan\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Plan status: `{payload['plan_status']}`\n\n"
        "## Claim\n\n"
        f"{payload['milestone']['claim']}\n\n"
        "## Specialist Team\n\n"
        f"{team}\n\n"
        "## Workstreams\n\n"
        f"{workstreams}\n\n"
        "## Acceptance Checks\n\n"
        f"{checks}\n\n"
        "## Reuse Anchors\n\n"
        f"{anchors}\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Boundary\n\n"
        "This package plans streamed candidate authoring only. It does not modify "
        "controller truth or claim C919 ETRAS correctness.\n"
    )


def run_streamed_logic_authoring_multi_agent_plan(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    plan_json_path = artifact_dir / PLAN_JSON_NAME
    plan_markdown_path = artifact_dir / PLAN_MARKDOWN_NAME
    restricted = _restricted_diff()
    target_doc_ok = _doc_contains(
        TARGET_DOC_PATH,
        [
            "Engineer-in-the-Loop Streamed Logic Authoring Target",
            "small graph edit",
            "Edit the requirements document only after explicit user authorization",
        ],
    )
    generalized_doc_ok = _doc_contains(
        GENERALIZED_TARGET_DOC_PATH,
        [
            "Generalized Logic Circuit Control Panel Target",
            "C919 ETRAS",
            "engineer-in-the-loop streamed authoring flow",
        ],
    )
    plan_doc_ok = _doc_contains(
        PLAN_DOC_PATH,
        [
            "Streamed Logic Authoring Multi-Agent Plan",
            "five-agent active team",
            "requirements document edits require explicit authorization",
        ],
    )
    team = _team_roster()
    workstreams = _workstreams()
    acceptance_checks = _acceptance_checks()
    reuse_anchors = _reuse_anchors()
    gates = {
        "streamed_authoring_target_doc": _gate_status(target_doc_ok),
        "generalized_panel_target_doc": _gate_status(generalized_doc_ok),
        "multi_agent_plan_doc": _gate_status(plan_doc_ok),
        "specialist_team_roster": _gate_status(len(team) == 5),
        "workstream_coverage": _gate_status(len(workstreams) == 6),
        "acceptance_checks": _gate_status(len(acceptance_checks) == 8),
        "non_claim_boundaries": _gate_status(not restricted),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        else "fail"
    )
    gates["local_gate"] = status
    payload = {
        "kind": "ai-fantui-multi-agent-m21-streamed-logic-authoring-plan",
        "version": 1,
        "package_id": "multi-agent-m21-streamed-logic-authoring-plan-v0.1",
        "status": status,
        "plan_status": "ready_for_m21_planning_review" if status == "pass" else "blocked",
        "activation_status": "blocked_until_project_owner_final_acceptance",
        "activation_gates": {
            "project_owner_final_decision": "blocked",
            "m20_cursor_idle": "referenced_not_executed",
            "m8_fast_gate_reference": "referenced_not_executed",
        },
        "milestone": {
            "id": "M21-candidate",
            "name": "工程师在场流式逻辑建模专职团队",
            "effort_unit": "施工队工时",
            "claim": (
                "planning-only specialist-team package for streamed candidate "
                "logic authoring; no controller truth promotion"
            ),
        },
        "operating_mode": {
            "mode": "five_agent_context_cap",
            "primary_executor": "Codex chief engineer dispatcher",
            "parallelism": "five capped agents own disjoint workstreams and artifacts",
            "review_policy": "spec review and evidence review before implementation promotion",
        },
        "agent_team": active_agent_team_payload(),
        "team_roster": team,
        "workstreams": workstreams,
        "acceptance_checks": acceptance_checks,
        "reuse_anchors": reuse_anchors,
        "non_claims": [
            "no C919 ETRAS correctness claim",
            "no controller truth promotion",
            "no production readiness claim",
            "no certification or DAL readiness claim",
            "no automatic requirements document mutation",
            "no whole-graph black-box generation acceptance",
        ],
        "artifact_paths": {
            "plan_json": str(plan_json_path),
            "plan_markdown": str(plan_markdown_path),
            "plan_doc": str(PLAN_DOC_PATH),
            "streamed_authoring_target_doc": str(TARGET_DOC_PATH),
            "generalized_panel_target_doc": str(GENERALIZED_TARGET_DOC_PATH),
        },
        "deterministic_gates": gates,
        "recommended_next_step": (
            "Use this package to open M21 as a multi-agent specialist-team "
            "implementation milestone after project-owner final acceptance."
        ),
    }
    _write_text(plan_markdown_path, _markdown_plan(payload))
    _write_json(plan_json_path, payload)
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: streamed logic authoring multi-agent plan generated")
        print(f"plan_status: {payload['plan_status']}")
        print(f"plan: {payload['artifact_paths']['plan_json']}")
    else:
        print("FAIL: streamed logic authoring multi-agent plan blocked")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = run_streamed_logic_authoring_multi_agent_plan(artifact_dir=args.artifact_dir)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

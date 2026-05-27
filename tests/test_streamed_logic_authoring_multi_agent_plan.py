from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_multi_agent_m21_streamed_logic_authoring_plan.py"
)
VERIFY_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_m21_streamed_logic_authoring_plan.py"
)
PLAN_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "streamed-logic-authoring-multi-agent-plan.md"
)
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
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_streamed_logic_authoring_multi_agent_plan_runner(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-multi-agent-m21-streamed-logic-authoring-plan"
    assert payload["package_id"] == "multi-agent-m21-streamed-logic-authoring-plan-v0.1"
    assert payload["status"] == "pass"
    assert payload["plan_status"] == "ready_for_m21_planning_review"
    assert payload["activation_status"] == "blocked_until_project_owner_final_acceptance"
    assert payload["activation_gates"] == {
        "project_owner_final_decision": "blocked",
        "m20_cursor_idle": "referenced_not_executed",
        "m8_fast_gate_reference": "referenced_not_executed",
    }
    assert payload["milestone"] == {
        "id": "M21-candidate",
        "name": "工程师在场流式逻辑建模专职团队",
        "effort_unit": "施工队工时",
        "claim": (
            "planning-only specialist-team package for streamed candidate "
            "logic authoring; no controller truth promotion"
        ),
    }
    assert payload["operating_mode"]["mode"] == "five_agent_context_cap"
    assert payload["agent_team"]["mode"] == "five_agent_context_cap"
    assert payload["agent_team"]["team_size"] == 5
    assert payload["deterministic_gates"] == {
        "streamed_authoring_target_doc": "pass",
        "generalized_panel_target_doc": "pass",
        "multi_agent_plan_doc": "pass",
        "specialist_team_roster": "pass",
        "workstream_coverage": "pass",
        "acceptance_checks": "pass",
        "non_claim_boundaries": "pass",
        "local_gate": "pass",
    }

    team_ids = [member["id"] for member in payload["team_roster"]]
    assert team_ids == [
        "chief-engineer-orchestrator",
        "logic-ir-repair-agent",
        "evidence-validation-agent",
        "safety-requirements-reviewer",
        "packaging-pr-readiness-agent",
    ]
    workstream_titles = [item["title"] for item in payload["workstreams"]]
    assert workstream_titles == [
        "source quote and interpretation contract",
        "atomic graph-edit proposal",
        "candidate graph commit boundary",
        "active node or wire highlight",
        "requirements edit authorization",
        "stream replay and review packet",
    ]
    check_ids = [item["id"] for item in payload["acceptance_checks"]]
    assert "one_edit_at_a_time" in check_ids
    assert "requirements_edit_authorized" in check_ids
    assert "truth_boundary_preserved" in check_ids
    anchor_ids = [item["id"] for item in payload["reuse_anchors"]]
    assert anchor_ids == [
        "logic_stream_timeline",
        "drawing_replay_events",
        "active_node_wire_highlight",
        "source_provenance",
        "confirm_before_update",
        "server_confirmation_boundary",
    ]
    assert "no whole-graph black-box generation acceptance" in payload["non_claims"]

    plan_json = Path(payload["artifact_paths"]["plan_json"])
    plan_markdown = Path(payload["artifact_paths"]["plan_markdown"])
    assert plan_json.exists()
    assert plan_json.name == "multi_agent_m21_streamed_logic_authoring_plan_v0_1.json"
    assert plan_markdown.exists()
    markdown = plan_markdown.read_text(encoding="utf-8")
    assert "Streamed Logic Authoring Multi-Agent Plan" in markdown
    assert "ChiefEngineerOrchestrator" in markdown
    assert "PackagingPRReadinessAgent" in markdown
    assert "requirements document edits require explicit authorization" in markdown
    assert "logic_stream_timeline" in markdown
    assert "server_confirmation_boundary" in markdown

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT_PATH),
            "--package",
            str(plan_json),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert verify_result.returncode == 0, verify_result.stderr
    verify_payload = json.loads(verify_result.stdout)
    assert verify_payload["status"] == "pass"
    assert verify_payload["activation_status"] == (
        "blocked_until_project_owner_final_acceptance"
    )
    assert verify_payload["deterministic_gates"] == {
        "package_shape": "pass",
        "activation_block": "pass",
        "specialist_team": "pass",
        "workstreams": "pass",
        "reuse_anchors": "pass",
        "boundary": "pass",
        "artifacts": "pass",
        "local_gate": "pass",
    }


def test_streamed_logic_authoring_multi_agent_plan_is_documented_and_wired() -> None:
    plan_doc = PLAN_DOC_PATH.read_text(encoding="utf-8")
    target_doc = TARGET_DOC_PATH.read_text(encoding="utf-8")
    generalized_doc = GENERALIZED_TARGET_DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Streamed Logic Authoring Multi-Agent Plan" in plan_doc
    assert "five-agent active team" in plan_doc
    assert "LogicIRRepairAgent" in plan_doc
    assert "requirements document edit proposals" in plan_doc
    assert "proposes one small graph edit at a time" in target_doc
    assert "explicit user authorization" in target_doc
    assert "engineer-in-the-loop streamed authoring flow" in generalized_doc
    assert "MULTI_AGENT_M21_STREAMED_LOGIC_AUTHORING_PLAN_ARTIFACT_DIR" in makefile
    assert "multi-agent-m21-streamed-logic-authoring-plan" in makefile
    assert "scripts/run_multi_agent_m21_streamed_logic_authoring_plan.py --format json" in makefile
    assert "scripts/verify_multi_agent_m21_streamed_logic_authoring_plan.py --format json" in makefile

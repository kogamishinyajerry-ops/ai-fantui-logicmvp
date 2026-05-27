from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from well_harness.multi_agent_operator_cockpit import (
    SCHEMA_ID,
    build_multi_agent_operator_cockpit,
    render_multi_agent_operator_cockpit_html,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "multi_agent_operator_cockpit_v0_1.schema.json"
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_operator_cockpit.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_operator_cockpit.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
COCKPIT_DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-operator-cockpit.md"
MVP_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "multi-agent-control-logic-engineering-system-mvp.md"
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _project_status_payload(tmp_path: Path) -> dict:
    return {
        "status": "pass",
        "recommended_next_step": "Do not continue M21 immediately. Use the project-owner acceptance review packet.",
        "completed": {
            "completed_count": 11,
            "last_completed_record_id": "RUN-QUEUE-011",
            "last_completed_task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
            "last_completed_queue_item_id": "queue-safety-output-command-conflict-repair",
        },
        "cursor": {
            "status": "pass",
            "state_status": "idle_no_open_approved_items",
        },
        "boundary": {
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "artifact_paths": {
            "summary_json": str(tmp_path / "project_manager_status_summary.json"),
            "summary_html": str(tmp_path / "project_manager_status_summary.html"),
        },
    }


def _ultrawork_payload(tmp_path: Path) -> dict:
    return {
        "status": "pass",
        "summary": {
            "open_approved_count": 1,
        },
        "selected_next_record": {
            "record_id": "RUN-QUEUE-011",
        },
        "gates": {
            "source_ledger_checker": "pass",
            "cursor_monotonicity": "pass",
            "resume_selection": "pass",
            "boundary": "pass",
            "local_gate": "pass",
        },
        "blockers": [
            {
                "blocker_id": "notion-control-plane-404",
                "status": "external_blocker",
                "message": "Notion control-plane HTTP 404 remains outside this cockpit slice.",
            }
        ],
        "artifact_paths": {
            "dashboard_json": str(tmp_path / "ultrawork_monitor_dashboard_v0_1.json"),
            "dashboard_html": str(tmp_path / "ultrawork_monitor_dashboard_v0_1.html"),
        },
    }


def test_multi_agent_operator_cockpit_schema_validates_payload(tmp_path: Path) -> None:
    project_status = _project_status_payload(tmp_path)
    ultrawork_dashboard = _ultrawork_payload(tmp_path)
    cockpit = build_multi_agent_operator_cockpit(
        project_status=project_status,
        ultrawork_dashboard=ultrawork_dashboard,
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(cockpit)
    assert cockpit["status"] == "pass"
    assert cockpit["milestone"]["id"] == "M22"
    assert cockpit["summary"]["completed_count"] == 11
    assert cockpit["summary"]["selected_next_record_id"] == "RUN-QUEUE-011"
    assert cockpit["agent_team"]["mode"] == "five_agent_context_cap"
    assert cockpit["agent_team"]["team_size"] == 5
    assert [item["name"] for item in cockpit["agent_team"]["active_agents"]] == [
        "ChiefEngineerOrchestrator",
        "LogicIRRepairAgent",
        "EvidenceValidationAgent",
        "SafetyRequirementsReviewer",
        "PackagingPRReadinessAgent",
    ]
    assert cockpit["dependency_boundary"]["controller_truth_modified"] is False
    assert cockpit["dependency_boundary"]["ui_layout_modified"] is False


def test_multi_agent_operator_cockpit_html_exposes_operator_views(tmp_path: Path) -> None:
    cockpit = build_multi_agent_operator_cockpit(
        project_status=_project_status_payload(tmp_path),
        ultrawork_dashboard=_ultrawork_payload(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_multi_agent_operator_cockpit_html(cockpit)

    assert "Multi-Agent Operator Cockpit" in html
    assert "five_agent_context_cap" in html
    assert "ChiefEngineerOrchestrator" in html
    assert "PackagingPRReadinessAgent" in html
    assert "Project Manager Status" in html
    assert "UltraWork Monitor" in html
    assert "RUN-QUEUE-011" in html
    assert "notion-control-plane-404" in html
    assert "src/well_harness/controller.py" in html
    assert "src/well_harness/demo_server.py" in html


def test_multi_agent_operator_cockpit_runner_and_checker_round_trip(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT),
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
        timeout=420,
    )
    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["artifact_paths"]["cockpit_html"] == str(
        tmp_path / "multi_agent_operator_cockpit_v0_1.html"
    )
    assert Path(payload["artifact_paths"]["project_status_html"]).exists()
    assert Path(payload["artifact_paths"]["ultrawork_dashboard_html"]).exists()

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--cockpit",
            payload["artifact_paths"]["cockpit_json"],
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert verify_result.returncode == 0, verify_result.stderr
    verify_payload = json.loads(verify_result.stdout)
    assert verify_payload == {
        "cockpit_path": payload["artifact_paths"]["cockpit_json"],
        "html_exists": True,
        "markdown_exists": True,
        "mismatches": [],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_operator_cockpit_is_wired_into_docs_and_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = COCKPIT_DOC_PATH.read_text(encoding="utf-8")
    mvp_doc = MVP_DOC_PATH.read_text(encoding="utf-8")

    assert "MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR" in makefile
    assert "multi-agent-operator-cockpit" in makefile
    assert "verify-multi-agent-operator-cockpit" in makefile
    assert "scripts/run_multi_agent_operator_cockpit.py --format json" in makefile
    assert "scripts/verify_multi_agent_operator_cockpit.py --format json" in makefile

    expected_pathspecs = [
        "docs/coordination/multi-agent-operator-cockpit.md",
        "docs/json_schema/multi_agent_operator_cockpit_v0_1.schema.json",
        "scripts/run_multi_agent_operator_cockpit.py",
        "scripts/verify_multi_agent_operator_cockpit.py",
        "src/well_harness/multi_agent_team.py",
        "src/well_harness/multi_agent_operator_cockpit.py",
        "tests/test_multi_agent_operator_cockpit.py",
    ]
    for pathspec in expected_pathspecs:
        assert pathspec in doc

    assert "src/well_harness/controller.py" in doc
    assert "src/well_harness/demo_server.py" in doc
    assert "src/well_harness/static/**" in doc
    assert ".planning/**" in doc
    assert "artifacts/**" in doc
    assert "five-agent active team" in doc
    assert "M22" in mvp_doc
    assert "five-agent active team" in mvp_doc
    assert "make multi-agent-operator-cockpit" in mvp_doc

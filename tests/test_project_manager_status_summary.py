from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_project_manager_status_summary.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _run_summary(tmp_path: Path) -> dict:
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
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _load_runner_module() -> ModuleType:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_project_manager_status_summary",
        RUN_SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_project_manager_status_summary_runner_emits_owner_readable_artifacts(
    tmp_path: Path,
) -> None:
    payload = _run_summary(tmp_path)

    assert payload["kind"] == "ai-fantui-project-manager-status-summary"
    assert payload["summary_id"] == "project-manager-status-summary-v0.1"
    assert payload["status"] == "pass"
    assert payload["as_of"] == "2026-05-27"
    assert payload["entrypoint"]["status"] == "formal_project_visibility_mvp_entrypoint"
    assert payload["entrypoint"]["acceptance_gate"] == "make project-visibility-mvp-gate"
    assert payload["entrypoint"]["html"].endswith("project_manager_status_summary.html")
    assert payload["current_mvp"]["name"] == "Multi-Agent Candidate Repair Pipeline MVP"
    assert payload["current_mvp"]["state"] == (
        "engineering_pipeline_mvp_complete_product_mvp_not_closed"
    )
    assert payload["completed"]["completed_count"] == 11
    assert payload["completed"]["last_completed_record_id"] == "RUN-QUEUE-011"
    assert payload["completed"]["last_completed_task_id"] == (
        "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"
    )
    assert payload["cursor"]["state_status"] == "idle_no_open_approved_items"
    assert payload["cursor"]["ready_for_resume"] is False
    assert payload["boundary"] == {
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "protected_paths_policy": (
            "no controller truth or requirements-intake UI edits in this slice"
        ),
    }
    assert payload["deterministic_gates"] == {
        "source_cursor": "pass",
        "queue_progress": "pass",
        "status_panel": "pass",
        "boundary": "pass",
        "summary_artifacts": "pass",
        "local_gate": "pass",
    }
    assert payload["recommended_next_step"].startswith("Do not continue M21 immediately.")
    assert [choice["id"] for choice in payload["next_stage_choices"]] == [
        "accept",
        "external_review",
        "demo_polish",
    ]
    assert payload["next_stage_choices"][0]["name"] == "Accept Customer Demo Evidence"
    assert payload["next_stage_choices"][0]["recommendation"] == (
        "unblocks_m21_after_external_evidence_acceptance"
    )
    assert payload["next_stage_choices"][0]["m21_queue_unblocked"] is True
    assert payload["next_stage_choices"][1]["name"] == "External Review"
    assert payload["next_stage_choices"][1]["recommendation"] == "keeps_m21_blocked"
    assert payload["next_stage_choices"][1]["m21_queue_unblocked"] is False
    assert payload["next_stage_choices"][2]["name"] == "Return to Demo Polish"
    assert any(
        record["record_id"] == "RUN-QUEUE-011"
        and record["source_finding_code"] == "CHECK_OUTPUT_COMMAND_CONFLICT_001"
        for record in payload["completed"]["records"]
    )

    summary_path = Path(payload["artifact_paths"]["summary_json"])
    markdown_path = Path(payload["artifact_paths"]["summary_markdown"])
    html_path = Path(payload["artifact_paths"]["summary_html"])
    cursor_path = Path(payload["artifact_paths"]["source_cursor_state"])
    ledger_path = Path(payload["artifact_paths"]["source_ledger"])
    assert summary_path.exists()
    assert markdown_path.exists()
    assert html_path.exists()
    assert cursor_path.exists()
    assert ledger_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["status"] == "pass"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Project Manager Status Summary" in markdown
    assert "RUN-QUEUE-011" in markdown
    assert "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001" in markdown
    assert "Do not continue M21 immediately." in markdown
    assert "Acceptance gate: `make project-visibility-mvp-gate`" in markdown
    assert (
        "| accept | Accept Customer Demo Evidence | "
        "unblocks_m21_after_external_evidence_acceptance |"
    ) in markdown
    assert "| external_review | External Review | keeps_m21_blocked |" in markdown
    assert "| demo_polish | Return to Demo Polish | keeps_m21_blocked |" in markdown
    assert "Controller truth modified: `False`" in markdown

    html = html_path.read_text(encoding="utf-8")
    assert "<title>Project Manager Status Summary</title>" in html
    assert "Accept Customer Demo Evidence" in html
    assert "M21 queue unblocked: True" in html
    assert "Return to Demo Polish" in html
    assert "RUN-QUEUE-011" in html
    assert "CHECK_OUTPUT_COMMAND_CONFLICT_001" in html
    assert "Acceptance gate: make project-visibility-mvp-gate" in html
    assert "Needs attention" not in html
    assert "On track" in html
    assert "src/well_harness/controller.py" not in html


def test_project_manager_status_summary_is_wired_into_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "PROJECT_MANAGER_STATUS_SUMMARY_ARTIFACT_DIR" in makefile
    assert "project-manager-status-summary" in makefile
    assert "scripts/run_project_manager_status_summary.py --format json" in makefile


def test_project_manager_status_summary_rejects_last_task_or_finding_drift(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_runner_module()
    completed_records = [
        {
            "record_id": f"RUN-QUEUE-{index:03d}",
            "queue_item_id": f"queue-item-{index:03d}",
            "task_id": f"TASK-{index:03d}",
            "status": "converged",
        }
        for index in range(1, 11)
    ]
    completed_records.append(
        {
            "record_id": "RUN-QUEUE-011",
            "queue_item_id": "queue-safety-output-command-conflict-repair",
            "task_id": "DRIFTED-TASK-ID",
            "status": "converged",
        }
    )
    cursor_payload = {
        "status": "pass",
        "state_status": "idle_no_open_approved_items",
        "cursor_position": {
            "last_completed_record_id": "RUN-QUEUE-011",
            "last_completed_queue_item_id": "queue-safety-output-command-conflict-repair",
        },
        "completed_records": completed_records,
        "resume_policy": {
            "next_action": "wait_for_append_only_queue_growth",
        },
        "artifact_paths": {
            "cursor_state": str(tmp_path / "cursor.json"),
            "source_ledger": str(tmp_path / "ledger.json"),
        },
        "aggregate": {
            "completed_count": 11,
            "open_approved_count": 0,
            "ready_for_resume": False,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
    }
    ledger_payload = {
        "run_records": [
            {
                "record_id": "RUN-QUEUE-011",
                "source_finding_code": "DRIFTED_FINDING_CODE",
            }
        ]
    }

    monkeypatch.setattr(
        module,
        "_run_cursor",
        lambda artifact_dir: {
            "returncode": 0,
            "stdout": json.dumps(cursor_payload),
            "stderr": "",
            "payload": cursor_payload,
        },
    )
    monkeypatch.setattr(
        module,
        "_load_source_ledger",
        lambda cursor: (ledger_payload, tmp_path / "ledger.json"),
    )

    payload = module.run_project_manager_status_summary(artifact_dir=tmp_path)

    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["queue_progress"] == "fail"
    assert payload["deterministic_gates"]["summary_artifacts"] == "pass"
    assert payload["deterministic_gates"]["local_gate"] == "fail"
    assert payload["checks"]["queue_progress"] == {
        "expected_last_completed_record_id": "RUN-QUEUE-011",
        "expected_last_completed_task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
        "expected_last_completed_source_finding_code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        "observed_last_completed_task_id": "DRIFTED-TASK-ID",
        "observed_last_completed_source_finding_code": "DRIFTED_FINDING_CODE",
    }

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_queue_cursor_state_v0_2.schema.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_queue_cursor_state_v0_2.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_queue_cursor_state_v0_2.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_queue_cursor_state_v0_2.schema.json"
)
EXPECTED_IDLE_COMPLETED_RECORD_IDS = [
    "RUN-QUEUE-001",
    "RUN-QUEUE-002",
    "RUN-QUEUE-003",
    "RUN-QUEUE-004",
    "RUN-QUEUE-005",
    "RUN-QUEUE-006",
    "RUN-QUEUE-007",
    "RUN-QUEUE-008",
    "RUN-QUEUE-009",
    "RUN-QUEUE-010",
    "RUN-QUEUE-011",
]
EXPECTED_OPEN_RECORD = {
    "record_id": "RUN-QUEUE-011",
    "queue_item_id": "queue-safety-output-command-conflict-repair",
    "task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
    "status": "approved_open",
}


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _run_cursor(tmp_path: Path, *, resume_mode: str = "idle") -> dict:
    command = [
        sys.executable,
        str(RUN_SCRIPT_PATH),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    ]
    if resume_mode != "idle":
        command.extend(["--resume-mode", resume_mode])
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=420,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _check_cursor(payload: dict) -> dict:
    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--cursor",
            str(payload["artifact_paths"]["cursor_state"]),
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
    assert check_result.returncode == 0, check_result.stderr
    return json.loads(check_result.stdout)


def test_queue_cursor_state_v0_2_schema_uses_v0_2_resume_policy() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    assert schema["properties"]["cursor_id"]["const"] == (
        "multi-agent-queue-cursor-state-v0.2"
    )
    assert schema["properties"]["source_ledger_id"]["const"] == (
        "multi-agent-queue-run-ledger-v0.2"
    )
    assert schema["properties"]["resume_policy"]["properties"]["policy_id"]["const"] == (
        "first-approved-open-item-v0.2"
    )


def test_queue_cursor_state_v0_2_idle_promotes_v0_9_ledger(
    tmp_path: Path,
) -> None:
    payload = _run_cursor(tmp_path / "idle")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)

    assert payload["status"] == "pass"
    assert payload["cursor_id"] == "multi-agent-queue-cursor-state-v0.2"
    assert payload["source_ledger_id"] == "multi-agent-queue-run-ledger-v0.2"
    assert payload["state_status"] == "idle_no_open_approved_items"
    assert payload["resume_policy"]["policy_id"] == "first-approved-open-item-v0.2"
    assert payload["cursor_position"] == {
        "last_completed_record_id": "RUN-QUEUE-011",
        "last_completed_queue_item_id": "queue-safety-output-command-conflict-repair",
        "next_record_id": "",
        "next_queue_item_id": "",
    }
    assert [record["record_id"] for record in payload["completed_records"]] == (
        EXPECTED_IDLE_COMPLETED_RECORD_IDS
    )
    assert payload["open_records"] == []
    assert payload["aggregate"] == {
        "source_ledger_record_count": 11,
        "completed_count": 11,
        "open_approved_count": 0,
        "blocked_count": 0,
        "ready_for_resume": False,
        "idle": True,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }

    check_payload = _check_cursor(payload)
    assert check_payload["status"] == "pass"
    assert check_payload["source_ledger_valid"] is True
    assert check_payload["resume_selection_valid"] is True
    assert check_payload["mismatches"] == []


def test_queue_cursor_state_v0_2_ready_to_resume_selects_v0_9_open_record(
    tmp_path: Path,
) -> None:
    payload = _run_cursor(tmp_path / "ready", resume_mode="ready-to-resume")

    assert payload["status"] == "pass"
    assert payload["state_status"] == "ready_to_resume"
    assert payload["cursor_position"] == {
        "last_completed_record_id": "RUN-QUEUE-010",
        "last_completed_queue_item_id": "queue-safety-unreachable-state-repair",
        "next_record_id": "RUN-QUEUE-011",
        "next_queue_item_id": "queue-safety-output-command-conflict-repair",
    }
    assert [record["record_id"] for record in payload["completed_records"]] == (
        EXPECTED_IDLE_COMPLETED_RECORD_IDS[:10]
    )
    assert payload["open_records"] == [EXPECTED_OPEN_RECORD]
    assert payload["selected_next_record"] == {
        "record_id": "RUN-QUEUE-011",
        "queue_item_id": "queue-safety-output-command-conflict-repair",
        "task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
        "status": "ready_to_resume",
    }
    assert payload["aggregate"] == {
        "source_ledger_record_count": 11,
        "completed_count": 10,
        "open_approved_count": 1,
        "blocked_count": 0,
        "ready_for_resume": True,
        "idle": False,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }

    check_payload = _check_cursor(payload)
    assert check_payload["status"] == "pass"
    assert check_payload["source_ledger_valid"] is True
    assert check_payload["resume_selection_valid"] is True
    assert check_payload["mismatches"] == []


def test_queue_cursor_state_v0_2_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-queue-cursor-state-v0-2" in makefile
    assert "scripts/run_multi_agent_queue_cursor_state_v0_2.py --format json" in makefile
    assert "verify-multi-agent-queue-cursor-state-v0-2" in makefile
    assert "multi-agent-queue-cursor-resume-state-v0-2" in makefile
    assert "MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE_V0_2 ?= ready-to-resume" in makefile

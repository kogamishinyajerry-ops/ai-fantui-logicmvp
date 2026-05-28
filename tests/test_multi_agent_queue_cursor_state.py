from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_queue_cursor_state_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "multi_agent_queue_cursor_state_v0_1.json"
)
READY_FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_queue_cursor_state_ready_to_resume_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_queue_cursor_state.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_queue_cursor_state.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_queue_cursor_state_v0_1.schema.json"
)
EXPECTED_COMPLETED_RECORDS = [
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
]
EXPECTED_OPEN_RECORD = {
    "record_id": "RUN-QUEUE-010",
    "queue_item_id": "queue-safety-unreachable-state-repair",
    "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
    "status": "approved_open",
}


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _normalize_cursor(payload: dict) -> dict:
    return {
        "$schema": payload["$schema"],
        "kind": payload["kind"],
        "status": payload["status"],
        "gate_id": payload["gate_id"],
        "cursor_id": payload["cursor_id"],
        "source_ledger_id": payload["source_ledger_id"],
        "source_ledger_gate_id": payload["source_ledger_gate_id"],
        "state_status": payload["state_status"],
        "resume_policy": payload["resume_policy"],
        "cursor_position": payload["cursor_position"],
        "selected_next_record": payload["selected_next_record"],
        "completed_records": payload["completed_records"],
        "open_records": payload["open_records"],
        "deterministic_gates": payload["deterministic_gates"],
        "aggregate": payload["aggregate"],
        "artifact_paths": {
            "cursor_state": "<cursor_state>",
            "source_ledger": "<source_ledger>",
        },
    }


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
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def idle_cursor_payload(tmp_path_factory: pytest.TempPathFactory) -> dict:
    return _run_cursor(tmp_path_factory.mktemp("idle-cursor"))


@pytest.fixture(scope="module")
def ready_cursor_payload(tmp_path_factory: pytest.TempPathFactory) -> dict:
    return _run_cursor(
        tmp_path_factory.mktemp("ready-cursor"),
        resume_mode="ready-to-resume",
    )


def test_queue_cursor_state_schema_validates_idle_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["cursor_id"] == "multi-agent-queue-cursor-state-v0.1"
    assert fixture["source_ledger_id"] == "multi-agent-queue-run-ledger-v0.1"
    assert fixture["state_status"] == "idle_no_open_approved_items"
    assert fixture["resume_policy"] == {
        "policy_id": "first-approved-open-item-v0.1",
        "next_action": "wait_for_append_only_queue_growth",
        "reason": "All approved queue run records are converged; wait for the next append-only queue item.",
    }
    assert fixture["cursor_position"] == {
        "last_completed_record_id": "RUN-QUEUE-010",
        "last_completed_queue_item_id": "queue-safety-unreachable-state-repair",
        "next_record_id": "",
        "next_queue_item_id": "",
    }
    assert [record["record_id"] for record in fixture["completed_records"]] == (
        EXPECTED_COMPLETED_RECORDS
    )
    assert fixture["open_records"] == []
    assert fixture["aggregate"] == {
        "source_ledger_record_count": 10,
        "completed_count": 10,
        "open_approved_count": 0,
        "blocked_count": 0,
        "ready_for_resume": False,
        "idle": True,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_queue_cursor_state_runner_and_checker_converge(
    idle_cursor_payload: dict,
) -> None:
    payload = idle_cursor_payload
    assert payload["status"] == "pass"
    assert payload["state_status"] == "idle_no_open_approved_items"
    assert payload["cursor_position"]["last_completed_record_id"] == "RUN-QUEUE-010"
    assert payload["cursor_position"]["next_record_id"] == ""
    assert payload["selected_next_record"] == {
        "record_id": "",
        "queue_item_id": "",
        "task_id": "",
        "status": "none",
    }
    assert payload["open_records"] == []
    assert payload["deterministic_gates"]["source_ledger_checker"] == "pass"
    assert payload["deterministic_gates"]["cursor_monotonicity"] == "pass"
    assert payload["deterministic_gates"]["completed_records"] == "pass"
    assert payload["deterministic_gates"]["resume_selection"] == "pass"
    assert payload["deterministic_gates"]["boundary"] == "pass"

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
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["cursor_schema_valid"] is True
    assert check_payload["source_ledger_valid"] is True
    assert check_payload["cursor_monotonicity_valid"] is True
    assert check_payload["resume_selection_valid"] is True
    assert check_payload["mismatches"] == []
    assert _normalize_cursor(payload) == json.loads(
        FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_queue_cursor_state_schema_validates_resume_fixture_for_v0_8_open_record() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(READY_FIXTURE_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["state_status"] == "ready_to_resume"
    assert fixture["resume_policy"] == {
        "policy_id": "first-approved-open-item-v0.1",
        "next_action": "resume_next_open_record",
        "reason": "An approved open queue run record exists; resume RUN-QUEUE-010 before appending more work.",
    }
    assert fixture["cursor_position"] == {
        "last_completed_record_id": "RUN-QUEUE-009",
        "last_completed_queue_item_id": "queue-safety-transition-endpoint-repair",
        "next_record_id": "RUN-QUEUE-010",
        "next_queue_item_id": "queue-safety-unreachable-state-repair",
    }
    assert [record["record_id"] for record in fixture["completed_records"]] == (
        EXPECTED_COMPLETED_RECORDS[:9]
    )
    assert fixture["open_records"] == [EXPECTED_OPEN_RECORD]
    assert fixture["selected_next_record"] == {
        "record_id": "RUN-QUEUE-010",
        "queue_item_id": "queue-safety-unreachable-state-repair",
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        "status": "ready_to_resume",
    }
    assert fixture["aggregate"] == {
        "source_ledger_record_count": 10,
        "completed_count": 9,
        "open_approved_count": 1,
        "blocked_count": 0,
        "ready_for_resume": True,
        "idle": False,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_queue_cursor_state_runner_and_checker_select_v0_8_open_record(
    ready_cursor_payload: dict,
) -> None:
    payload = ready_cursor_payload
    assert payload["status"] == "pass"
    assert payload["state_status"] == "ready_to_resume"
    assert payload["cursor_position"]["last_completed_record_id"] == "RUN-QUEUE-009"
    assert payload["cursor_position"]["next_record_id"] == "RUN-QUEUE-010"
    assert payload["open_records"] == [EXPECTED_OPEN_RECORD]
    assert payload["selected_next_record"] == {
        "record_id": "RUN-QUEUE-010",
        "queue_item_id": "queue-safety-unreachable-state-repair",
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        "status": "ready_to_resume",
    }
    assert payload["aggregate"]["ready_for_resume"] is True
    assert payload["aggregate"]["idle"] is False

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
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["source_ledger_valid"] is True
    assert check_payload["resume_selection_valid"] is True
    assert check_payload["mismatches"] == []
    assert _normalize_cursor(payload) == json.loads(
        READY_FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_queue_cursor_state_checker_rejects_false_completed_record(
    idle_cursor_payload: dict,
    tmp_path: Path,
) -> None:
    cursor_path = tmp_path / "multi_agent_queue_cursor_state_v0_1.json"
    cursor = json.loads(
        Path(idle_cursor_payload["artifact_paths"]["cursor_state"]).read_text(
            encoding="utf-8"
        )
    )
    cursor["completed_records"][9]["status"] = "pending"
    cursor_path.write_text(json.dumps(cursor), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--cursor",
            str(cursor_path),
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

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["completed_records_valid"] is False
    assert "RUN-QUEUE-010.completed_records.status must be converged" in payload[
        "mismatches"
    ]


def test_queue_cursor_state_checker_rejects_missing_open_record_after_v0_8(
    ready_cursor_payload: dict,
    tmp_path: Path,
) -> None:
    cursor_path = tmp_path / "multi_agent_queue_cursor_state_v0_1.json"
    cursor = json.loads(
        Path(ready_cursor_payload["artifact_paths"]["cursor_state"]).read_text(
            encoding="utf-8"
        )
    )
    cursor["open_records"] = []
    cursor["selected_next_record"] = {
        "record_id": "",
        "queue_item_id": "",
        "task_id": "",
        "status": "none",
    }
    cursor_path.write_text(json.dumps(cursor), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--cursor",
            str(cursor_path),
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

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["resume_selection_valid"] is False
    assert "open_records must contain the approved open resume record" in payload[
        "mismatches"
    ]


def test_queue_cursor_state_is_wired_into_make_and_task_contract() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-queue-cursor-state" in makefile
    assert "scripts/run_multi_agent_queue_cursor_state.py --format json" in makefile
    assert "scripts/verify_multi_agent_queue_cursor_state.py --format json" in makefile
    assert "multi-agent-queue-cursor-resume-state" in makefile

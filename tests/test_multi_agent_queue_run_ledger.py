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
    / "multi_agent_queue_run_ledger_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "multi_agent_queue_run_ledger_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_queue_run_ledger.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_queue_run_ledger.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_queue_run_ledger_v0_1.schema.json"
)
EXPECTED_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
    "queue-safety-undefined-signal-repair",
    "queue-evidence-boundary-review-repair",
    "queue-evidence-unknown-requirement-repair",
    "queue-evidence-ir-trace-unknown-requirement-repair",
    "queue-safety-transition-endpoint-repair",
    "queue-safety-unreachable-state-repair",
]


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _normalize_ledger(payload: dict) -> dict:
    return {
        "$schema": payload["$schema"],
        "kind": payload["kind"],
        "status": payload["status"],
        "gate_id": payload["gate_id"],
        "ledger_id": payload["ledger_id"],
        "source_queue_id": payload["source_queue_id"],
        "source_queue_gate_id": payload["source_queue_gate_id"],
        "selected_queue_item_id": payload["selected_queue_item_id"],
        "selected_task_id": payload["selected_task_id"],
        "run_count": payload["run_count"],
        "scheduler_decision": payload["scheduler_decision"],
        "append_only": payload["append_only"],
        "deterministic_gates": payload["deterministic_gates"],
        "aggregate": payload["aggregate"],
        "artifact_paths": {
            "ledger": "<ledger>",
            "source_queue_summary": "<source_queue_summary>",
        },
        "run_records": [
            {
                "record_id": record["record_id"],
                "sequence": record["sequence"],
                "queue_item_id": record["queue_item_id"],
                "slice_id": record["slice_id"],
                "source_finding_code": record["source_finding_code"],
                "task": record["task"],
                "preflight": {
                    "command": record["preflight"]["command"],
                    "gate_id": record["preflight"].get("gate_id", ""),
                    "returncode": record["preflight"]["returncode"],
                    "status": record["preflight"]["status"],
                },
                "approved_task_shell": record["approved_task_shell"],
                "repair": record["repair"],
                "review_export": {
                    "path": "<candidate_review_packet_export>",
                    "reviewer_status": record["review_export"]["reviewer_status"],
                    "finding_chain_statuses": record["review_export"][
                        "finding_chain_statuses"
                    ],
                },
                "boundary": record["boundary"],
            }
            for record in payload["run_records"]
        ],
    }


def test_queue_run_ledger_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["ledger_id"] == "multi-agent-queue-run-ledger-v0.1"
    assert fixture["source_queue_id"] == "approved-candidate-task-queue-v0.8"
    assert fixture["selected_queue_item_id"] == "queue-safety-unreachable-state-repair"
    assert fixture["selected_task_id"] == "TASK-CE-CHECK-UNREACHABLE-STATE-001"
    assert fixture["run_count"] == 10
    assert [record["queue_item_id"] for record in fixture["run_records"]] == (
        EXPECTED_QUEUE_ORDER
    )
    assert fixture["scheduler_decision"] == {
        "policy_id": "latest-approved-append-only-item-v0.1",
        "decision_status": "selected_approved_candidate",
        "selected_queue_item_id": "queue-safety-unreachable-state-repair",
        "selected_record_id": "RUN-QUEUE-010",
        "reason": "Use the newest append-only approved queue item after v0.8 checker passes.",
    }
    assert fixture["aggregate"] == {
        "record_count": 10,
        "source_queue_task_count": 10,
        "executed_limited": 10,
        "converged": 10,
        "child_review_exports_valid": True,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "open_findings": [],
        "ledger_append_only": True,
    }


def test_queue_run_ledger_runner_and_checker_converge(tmp_path: Path) -> None:
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
        timeout=260,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["source_queue_id"] == "approved-candidate-task-queue-v0.8"
    assert payload["selected_queue_item_id"] == "queue-safety-unreachable-state-repair"
    assert payload["selected_task_id"] == "TASK-CE-CHECK-UNREACHABLE-STATE-001"
    assert payload["deterministic_gates"]["source_queue_v0_8_checker"] == "pass"
    assert payload["deterministic_gates"]["scheduler_selection"] == "pass"
    assert payload["deterministic_gates"]["approved_task_shell_records"] == "pass"
    assert payload["deterministic_gates"]["child_review_exports"] == "pass"
    assert payload["deterministic_gates"]["boundary"] == "pass"
    assert payload["aggregate"]["ledger_append_only"] is True

    selected_record = payload["run_records"][9]
    assert selected_record["record_id"] == "RUN-QUEUE-010"
    assert selected_record["queue_item_id"] == "queue-safety-unreachable-state-repair"
    assert selected_record["source_finding_code"] == "CHECK_UNREACHABLE_STATE_001"
    assert selected_record["preflight"]["command"] == "make multi-agent-fast-construction-gate"
    assert selected_record["approved_task_shell"] == {
        "status": "executed_limited",
        "approval_status": "approved",
        "selected_task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
    }
    assert selected_record["repair"] == {
        "status": "pass",
        "reviewer_status": "converged",
        "finding_chain_statuses": ["converged"],
    }
    assert selected_record["review_export"]["reviewer_status"] == "converged"
    assert selected_record["boundary"]["controller_truth_modified"] is False
    assert selected_record["boundary"]["ui_layout_modified"] is False

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--ledger",
            str(payload["artifact_paths"]["ledger"]),
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
    assert check_payload["ledger_schema_valid"] is True
    assert check_payload["source_queue_valid"] is True
    assert check_payload["scheduler_valid"] is True
    assert check_payload["run_records_valid"] is True
    assert check_payload["child_review_exports_valid"] is True
    assert check_payload["mismatches"] == []
    assert _normalize_ledger(payload) == json.loads(
        FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_queue_run_ledger_checker_rejects_unapproved_record(tmp_path: Path) -> None:
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
        timeout=260,
    )
    assert result.returncode == 0, result.stderr

    ledger_path = tmp_path / "multi_agent_queue_run_ledger_v0_1.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["run_records"][9]["approved_task_shell"]["approval_status"] = "pending"
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--ledger",
            str(ledger_path),
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
    assert payload["run_records_valid"] is False
    assert (
        "RUN-QUEUE-010.approved_task_shell.approval_status must be approved"
        in payload["mismatches"]
    )


def test_queue_run_ledger_is_wired_into_make_ci_and_task_contract() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    workflow = GSD_AUTOMATION_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "multi-agent-queue-run-ledger" in makefile
    assert "scripts/run_multi_agent_queue_run_ledger.py --format json" in makefile
    assert "scripts/verify_multi_agent_queue_run_ledger.py --format json" in makefile
    assert "Run multi-agent queue run ledger" in workflow
    assert "Verify multi-agent queue run ledger" in workflow
    assert "Upload multi-agent queue run ledger" in workflow

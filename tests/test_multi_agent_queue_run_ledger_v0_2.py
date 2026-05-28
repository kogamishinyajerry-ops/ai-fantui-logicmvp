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
    / "multi_agent_queue_run_ledger_v0_2.schema.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_queue_run_ledger_v0_2.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_queue_run_ledger_v0_2.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_queue_run_ledger_v0_2.schema.json"
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
    "queue-safety-output-command-conflict-repair",
]


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_queue_run_ledger_v0_2_schema_has_v0_9_source_queue_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    assert schema["properties"]["ledger_id"]["const"] == (
        "multi-agent-queue-run-ledger-v0.2"
    )
    assert schema["properties"]["source_queue_id"]["const"] == (
        "approved-candidate-task-queue-v0.9"
    )
    assert "source_queue_v0_9_checker" in schema["properties"][
        "deterministic_gates"
    ]["required"]


def test_queue_run_ledger_v0_2_runner_and_checker_promote_v0_9(
    tmp_path: Path,
) -> None:
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
        timeout=360,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["status"] == "pass"
    assert payload["ledger_id"] == "multi-agent-queue-run-ledger-v0.2"
    assert payload["source_queue_id"] == "approved-candidate-task-queue-v0.9"
    assert payload["selected_queue_item_id"] == (
        "queue-safety-output-command-conflict-repair"
    )
    assert payload["selected_task_id"] == (
        "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"
    )
    assert payload["run_count"] == 11
    assert [record["queue_item_id"] for record in payload["run_records"]] == (
        EXPECTED_QUEUE_ORDER
    )
    assert payload["scheduler_decision"]["selected_record_id"] == "RUN-QUEUE-011"
    assert payload["deterministic_gates"]["source_queue_v0_9_checker"] == "pass"
    assert payload["aggregate"] == {
        "record_count": 11,
        "source_queue_task_count": 11,
        "executed_limited": 11,
        "converged": 11,
        "child_review_exports_valid": True,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "open_findings": [],
        "ledger_append_only": True,
    }

    selected_record = payload["run_records"][10]
    assert selected_record["record_id"] == "RUN-QUEUE-011"
    assert selected_record["source_finding_code"] == "CHECK_OUTPUT_COMMAND_CONFLICT_001"
    assert selected_record["repair"]["reviewer_status"] == "converged"

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
    assert check_payload["source_queue_valid"] is True
    assert check_payload["run_records_valid"] is True
    assert check_payload["aggregate_valid"] is True
    assert check_payload["mismatches"] == []


def test_queue_run_ledger_v0_2_checker_rejects_missing_v0_9_append(
    tmp_path: Path,
) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path / "source"),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=360,
    )
    payload = json.loads(run_result.stdout)
    payload["run_records"] = payload["run_records"][:-1]
    payload["run_count"] = 10
    payload["aggregate"]["record_count"] = 10
    bad_ledger_path = tmp_path / "bad-ledger.json"
    bad_ledger_path.write_text(json.dumps(payload), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--ledger",
            str(bad_ledger_path),
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
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "fail"
    assert any("run_records" in mismatch for mismatch in check_payload["mismatches"])


def test_queue_run_ledger_v0_2_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-queue-run-ledger-v0-2" in makefile
    assert "scripts/run_multi_agent_queue_run_ledger_v0_2.py --format json" in makefile
    assert "verify-multi-agent-queue-run-ledger-v0-2" in makefile
    assert "scripts/verify_multi_agent_queue_run_ledger_v0_2.py --format json" in makefile

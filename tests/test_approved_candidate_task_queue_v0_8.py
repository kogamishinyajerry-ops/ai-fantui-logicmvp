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
    / "approved_candidate_task_queue_summary_v0_8.schema.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_candidate_task_queue_v0_8.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_approved_candidate_task_queue_v0_8_artifact.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_summary_v0_8.schema.json"
)
V0_7_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
    "queue-safety-undefined-signal-repair",
    "queue-evidence-boundary-review-repair",
    "queue-evidence-unknown-requirement-repair",
    "queue-evidence-ir-trace-unknown-requirement-repair",
    "queue-safety-transition-endpoint-repair",
]
M20_QUEUE_ITEM_ID = "queue-safety-unreachable-state-repair"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_v0_8_queue_runner_and_checker_append_unreachable_state_repair_record(
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
        timeout=260,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(payload)

    assert payload["status"] == "pass"
    assert payload["queue_id"] == "approved-candidate-task-queue-v0.8"
    assert payload["queue_order"][:9] == V0_7_QUEUE_ORDER
    assert payload["queue_order"][9] == M20_QUEUE_ITEM_ID
    assert payload["task_count"] == 10
    assert payload["append_only"] == {
        "previous_queue_id": "approved-candidate-task-queue-v0.7",
        "previous_task_count": 9,
        "preserved_prefix_count": 9,
        "new_task_count": 1,
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "appended_record_id": "RUN-QUEUE-010",
    }
    assert payload["aggregate"] == {
        "task_count": 10,
        "passed": 10,
        "preflight_passed": 10,
        "executed_limited": 10,
        "converged": 10,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "fast_gate_used_for_new_item": True,
        "appended_record_id": "RUN-QUEUE-010",
    }

    new_item = payload["items"][9]
    assert new_item["queue_item_id"] == M20_QUEUE_ITEM_ID
    assert new_item["queue_contract"] == {
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "source_finding_code": "CHECK_UNREACHABLE_STATE_001",
        "task_class": "SafetyRepairTask",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_id": "APPROVAL-SAFETY-UNREACHABLE-STATE-REPAIR-SLICE-001",
        "readiness_command": "make multi-agent-fast-construction-gate",
        "runner_contract": "candidate_review_packet_export_v0_1",
    }
    assert new_item["selected_task"] == {
        "approval_status": "approved",
        "target_agent": "LogicIRRepairAgent",
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        "task_type": "repair_candidate_logic_ir",
    }
    assert new_item["approved_task_shell"] == {
        "status": "executed_limited",
        "approval_status": "approved",
        "selected_task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
    }
    assert new_item["execution"]["reviewer_status"] == "converged"
    assert new_item["execution"]["finding_chain_statuses"] == ["converged"]
    assert new_item["boundary"] == {
        "truth_effect": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }

    review_export_path = Path(new_item["artifact_paths"]["candidate_review_packet_export"])
    review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
    chain = review_export["review_packet"]["finding_chains"][0]
    assert chain["finding"]["code"] == "CHECK_UNREACHABLE_STATE_001"
    assert chain["approval"]["approval_id"] == (
        "APPROVAL-SAFETY-UNREACHABLE-STATE-REPAIR-SLICE-001"
    )
    assert chain["repair"]["actions"] == [
        {
            "action": "remove_candidate_state_stub",
            "state_id": "UNREACHABLE_REVIEW",
            "initial_state": "IDLE",
            "reason": "CHECK_UNREACHABLE_STATE_001",
        }
    ]
    assert chain["status"] == "converged"
    assert chain["convergence"]["after_findings"] == []

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--summary",
            str(payload["artifact_paths"]["queue_summary"]),
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
    assert check_payload["summary_schema_valid"] is True
    assert check_payload["append_only_valid"] is True
    assert check_payload["new_evidence_item_valid"] is True
    assert check_payload["fast_gate_valid"] is True
    assert check_payload["child_review_exports_valid"] is True
    assert check_payload["mismatches"] == []


def test_v0_8_queue_checker_rejects_missing_unreachable_state_item(
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
        timeout=260,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    summary_path = Path(payload["artifact_paths"]["queue_summary"])
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["items"] = summary["items"][:9]
    summary["queue_order"] = summary["queue_order"][:9]
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--summary",
            str(summary_path),
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
    assert any("queue_order" in mismatch for mismatch in check_payload["mismatches"])


def test_v0_8_queue_make_targets_are_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "approved-candidate-task-queue-v0-8" in makefile
    assert "verify-approved-candidate-task-queue-v0-8-artifact" in makefile
    assert "scripts/run_approved_candidate_task_queue_v0_8.py" in makefile
    assert "scripts/verify_approved_candidate_task_queue_v0_8_artifact.py" in makefile

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
    / "approved_candidate_task_queue_summary_v0_3.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "approved_candidate_task_queue_summary_v0_3.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_candidate_task_queue_v0_3.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_approved_candidate_task_queue_v0_3_artifact.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_summary_v0_3.schema.json"
)
V0_2_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
]
M9_QUEUE_ITEM_ID = "queue-safety-undefined-signal-repair"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _normalize_summary(payload: dict) -> dict:
    return {
        "$schema": payload["$schema"],
        "kind": payload["kind"],
        "status": payload["status"],
        "gate_id": payload["gate_id"],
        "queue_id": payload["queue_id"],
        "task_count": payload["task_count"],
        "ready_for_long_running_development": payload[
            "ready_for_long_running_development"
        ],
        "queue_order": payload["queue_order"],
        "append_only": payload["append_only"],
        "deterministic_gates": payload["deterministic_gates"],
        "aggregate": payload["aggregate"],
        "artifact_paths": {
            "queue_summary": "<queue_summary>",
            "prefix_v0_2_summary": "<prefix_v0_2_summary>",
        },
        "items": [
            {
                "queue_item_id": item["queue_item_id"],
                "slice_id": item["slice_id"],
                "status": item["status"],
                "queue_contract": item["queue_contract"],
                "preflight": {
                    "artifact_paths": {},
                    "command": item["preflight"]["command"],
                    "gate_id": item["preflight"].get("gate_id", ""),
                    "readiness_id": item["preflight"].get("readiness_id", ""),
                    "ready_for_long_running_development": item["preflight"].get(
                        "ready_for_long_running_development",
                        False,
                    ),
                    "ready_for_slice_preflight": item["preflight"].get(
                        "ready_for_slice_preflight",
                        False,
                    ),
                    "returncode": item["preflight"]["returncode"],
                    "status": item["preflight"]["status"],
                    "stderr": item["preflight"]["stderr"],
                },
                "execution": item["execution"],
                "approved_task_shell": item["approved_task_shell"],
                "selected_task": item["selected_task"],
                "boundary": item["boundary"],
                "artifact_paths": {
                    "candidate_review_packet": "<candidate_review_packet>",
                    "candidate_review_packet_export": "<candidate_review_packet_export>",
                    "repair_loop_result": "<repair_loop_result>",
                    "repaired_candidate_packet": "<repaired_candidate_packet>",
                },
            }
            for item in payload["items"]
        ],
    }


def test_v0_3_queue_summary_schema_validates_append_only_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["queue_id"] == "approved-candidate-task-queue-v0.3"
    assert fixture["task_count"] == 5
    assert fixture["queue_order"][:4] == V0_2_QUEUE_ORDER
    assert fixture["queue_order"][4] == M9_QUEUE_ITEM_ID
    assert fixture["append_only"] == {
        "previous_queue_id": "approved-candidate-task-queue-v0.2",
        "previous_task_count": 4,
        "preserved_prefix_count": 4,
        "new_task_count": 1,
        "template_id": "approved-candidate-repair-task-template-v0.1",
    }

    new_item = fixture["items"][4]
    assert new_item["queue_item_id"] == M9_QUEUE_ITEM_ID
    assert new_item["queue_contract"] == {
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "source_finding_code": "CHECK_UNDEFINED_SIGNAL_001",
        "task_class": "SafetyRepairTask",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_id": "APPROVAL-SAFETY-UNDEFINED-SIGNAL-REPAIR-SLICE-001",
        "readiness_command": "make multi-agent-fast-construction-gate",
        "runner_contract": "candidate_review_packet_export_v0_1",
    }
    assert new_item["preflight"]["command"] == "make multi-agent-fast-construction-gate"
    assert new_item["preflight"]["gate_id"] == "multi-agent-m8-fast-construction-gate"
    assert new_item["selected_task"] == {
        "approval_status": "approved",
        "target_agent": "LogicIRRepairAgent",
        "task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
        "task_type": "repair_candidate_logic_ir",
    }
    assert fixture["aggregate"] == {
        "task_count": 5,
        "passed": 5,
        "preflight_passed": 5,
        "executed_limited": 5,
        "converged": 5,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "fast_gate_used_for_new_item": True,
    }


def test_v0_3_queue_runner_and_checker_converge_with_fast_gate_item(
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
        timeout=220,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["queue_id"] == "approved-candidate-task-queue-v0.3"
    assert payload["queue_order"][:4] == V0_2_QUEUE_ORDER
    assert payload["queue_order"][4] == M9_QUEUE_ITEM_ID
    assert payload["task_count"] == 5
    assert payload["append_only"]["preserved_prefix_count"] == 4
    assert payload["append_only"]["new_task_count"] == 1
    assert payload["deterministic_gates"]["m8_fast_construction_gate"] == "pass"

    new_item = payload["items"][4]
    assert new_item["status"] == "pass"
    assert new_item["queue_contract"]["source_finding_code"] == "CHECK_UNDEFINED_SIGNAL_001"
    assert new_item["queue_contract"]["readiness_command"] == (
        "make multi-agent-fast-construction-gate"
    )
    assert new_item["preflight"]["command"] == "make multi-agent-fast-construction-gate"
    assert new_item["preflight"]["status"] == "pass"
    assert new_item["approved_task_shell"] == {
        "status": "executed_limited",
        "approval_status": "approved",
        "selected_task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
    }
    assert new_item["execution"]["reviewer_status"] == "converged"
    assert new_item["execution"]["finding_chain_statuses"] == ["converged"]
    assert new_item["boundary"]["controller_truth_modified"] is False
    assert new_item["boundary"]["ui_layout_modified"] is False

    review_export_path = Path(new_item["artifact_paths"]["candidate_review_packet_export"])
    assert review_export_path.exists()
    review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
    chain = review_export["review_packet"]["finding_chains"][0]
    assert chain["finding"]["code"] == "CHECK_UNDEFINED_SIGNAL_001"
    assert chain["approval"]["approval_id"] == (
        "APPROVAL-SAFETY-UNDEFINED-SIGNAL-REPAIR-SLICE-001"
    )
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
        timeout=90,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["summary_schema_valid"] is True
    assert check_payload["append_only_valid"] is True
    assert check_payload["new_safety_item_valid"] is True
    assert check_payload["fast_gate_valid"] is True
    assert check_payload["child_review_exports_valid"] is True
    assert check_payload["mismatches"] == []
    assert _normalize_summary(payload) == json.loads(
        FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_v0_3_queue_checker_rejects_new_item_without_fast_gate(tmp_path: Path) -> None:
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
        timeout=220,
    )
    assert result.returncode == 0, result.stderr

    summary_path = tmp_path / "approved_candidate_task_queue_summary_v0_3.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["items"][4]["queue_contract"]["readiness_command"] = (
        "make multi-agent-construction-readiness"
    )
    summary["items"][4]["preflight"]["command"] = "make multi-agent-construction-readiness"
    summary["aggregate"]["fast_gate_used_for_new_item"] = False
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
        timeout=90,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["fast_gate_valid"] is False
    assert "M9 queue item must use make multi-agent-fast-construction-gate" in payload[
        "mismatches"
    ]


def test_v0_3_queue_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "approved-candidate-task-queue-v0-3" in makefile
    assert "scripts/run_approved_candidate_task_queue_v0_3.py --format json" in makefile
    assert "verify-approved-candidate-task-queue-v0-3-artifact" in makefile

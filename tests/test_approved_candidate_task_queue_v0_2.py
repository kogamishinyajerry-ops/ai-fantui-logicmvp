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
    / "approved_candidate_task_queue_summary_v0_2.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "approved_candidate_task_queue_summary_v0_2.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_candidate_task_queue_v0_2.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_approved_candidate_task_queue_v0_2_artifact.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_summary_v0_2.schema.json"
)
V0_1_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
]
M7_QUEUE_ITEM_ID = "queue-requirement-ambiguity-repair"


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
            "queue_summary": "<queue_summary>"
        },
        "items": [
            {
                "queue_item_id": item["queue_item_id"],
                "slice_id": item["slice_id"],
                "status": item["status"],
                "queue_contract": item["queue_contract"],
                "preflight": {
                    "artifact_paths": item["preflight"]["artifact_paths"],
                    "command": item["preflight"]["command"],
                    "readiness_id": item["preflight"]["readiness_id"],
                    "status": item["preflight"]["status"],
                    "returncode": item["preflight"]["returncode"],
                    "ready_for_long_running_development": item["preflight"][
                        "ready_for_long_running_development"
                    ],
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


def test_v0_2_queue_summary_schema_validates_append_only_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["queue_id"] == "approved-candidate-task-queue-v0.2"
    assert fixture["task_count"] == 4
    assert fixture["queue_order"][:3] == V0_1_QUEUE_ORDER
    assert fixture["queue_order"][3] == M7_QUEUE_ITEM_ID
    assert fixture["append_only"] == {
        "previous_queue_id": "approved-candidate-task-queue-v0.1",
        "previous_task_count": 3,
        "preserved_prefix_count": 3,
        "new_task_count": 1,
        "template_id": "approved-candidate-repair-task-template-v0.1",
    }

    new_item = fixture["items"][3]
    assert new_item["queue_item_id"] == M7_QUEUE_ITEM_ID
    assert new_item["queue_contract"] == {
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "source_finding_code": "REQ_AMBIGUITY_UNRESOLVED",
        "task_class": "RequirementRepairTask",
        "target_agent": "RequirementRepairAgent",
        "task_type": "repair_structured_requirement_candidate",
        "approval_id": "APPROVAL-REQUIREMENT-AMBIGUITY-REPAIR-SLICE-001",
        "readiness_command": "make multi-agent-construction-readiness",
        "runner_contract": "candidate_review_packet_export_v0_1",
    }
    assert new_item["selected_task"] == {
        "approval_status": "approved",
        "target_agent": "RequirementRepairAgent",
        "task_id": "TASK-CE-REQ-AMBIGUITY-UNRESOLVED",
        "task_type": "repair_structured_requirement_candidate",
    }
    assert fixture["aggregate"] == {
        "task_count": 4,
        "passed": 4,
        "preflight_passed": 4,
        "executed_limited": 4,
        "converged": 4,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_v0_2_queue_runner_and_checker_converge_with_requirement_repair(
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
        timeout=160,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["queue_id"] == "approved-candidate-task-queue-v0.2"
    assert payload["queue_order"][:3] == V0_1_QUEUE_ORDER
    assert payload["queue_order"][3] == M7_QUEUE_ITEM_ID
    assert payload["task_count"] == 4
    assert payload["append_only"]["preserved_prefix_count"] == 3
    assert payload["append_only"]["new_task_count"] == 1

    new_item = payload["items"][3]
    assert new_item["status"] == "pass"
    assert new_item["queue_contract"]["task_class"] == "RequirementRepairTask"
    assert new_item["queue_contract"]["source_finding_code"] == "REQ_AMBIGUITY_UNRESOLVED"
    assert new_item["approved_task_shell"] == {
        "status": "executed_limited",
        "approval_status": "approved",
        "selected_task_id": "TASK-CE-REQ-AMBIGUITY-UNRESOLVED",
    }
    assert new_item["execution"]["reviewer_status"] == "converged"
    assert new_item["execution"]["finding_chain_statuses"] == ["converged"]
    assert new_item["boundary"]["controller_truth_modified"] is False
    assert new_item["boundary"]["ui_layout_modified"] is False

    review_export_path = Path(new_item["artifact_paths"]["candidate_review_packet_export"])
    assert review_export_path.exists()
    review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
    chain = review_export["review_packet"]["finding_chains"][0]
    assert chain["finding"]["code"] == "REQ_AMBIGUITY_UNRESOLVED"
    assert chain["approval"]["approval_id"] == (
        "APPROVAL-REQUIREMENT-AMBIGUITY-REPAIR-SLICE-001"
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
        timeout=60,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["summary_schema_valid"] is True
    assert check_payload["append_only_valid"] is True
    assert check_payload["new_requirement_item_valid"] is True
    assert check_payload["child_review_exports_valid"] is True
    assert check_payload["mismatches"] == []
    assert _normalize_summary(payload) == json.loads(
        FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_v0_2_queue_checker_rejects_broken_append_only_prefix(tmp_path: Path) -> None:
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
        timeout=160,
    )
    assert result.returncode == 0, result.stderr

    summary_path = tmp_path / "approved_candidate_task_queue_summary_v0_2.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["queue_order"][0], summary["queue_order"][1] = (
        summary["queue_order"][1],
        summary["queue_order"][0],
    )
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
        timeout=60,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["append_only_valid"] is False
    assert "v0.2 queue must preserve v0.1 queue order prefix" in payload["mismatches"]


def test_v0_2_queue_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "approved-candidate-task-queue-v0-2" in makefile
    assert "scripts/run_approved_candidate_task_queue_v0_2.py --format json" in makefile
    assert "verify-approved-candidate-task-queue-v0-2-artifact" in makefile

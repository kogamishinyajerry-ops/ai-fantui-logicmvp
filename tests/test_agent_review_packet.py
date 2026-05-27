from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from well_harness.agent_execution_plan import build_execution_plan_from_task_package
from well_harness.agent_execution_shell import build_execution_evidence_package
from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_safety_guardian_checks,
)
from well_harness.agent_repair_loop import (
    run_evidence_agent_repair_loop,
    run_safety_guardian_repair_loop,
)
from well_harness.agent_task_contract import build_chief_engineer_task_package


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/candidate_review_packet_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "candidate_review_packet_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "candidate_review_packet_v0_1.json"
EXPORT_SCHEMA_ID = "https://well-harness.local/json_schema/candidate_review_packet_export_v0_1.schema.json"
EXPORT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "candidate_review_packet_export_v0_1.schema.json"
EXPORT_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "candidate_review_packet_export_v0_1.json"
REFERENCE_EXPORT_PATH = (
    PROJECT_ROOT
    / "src"
    / "well_harness"
    / "reference_packets"
    / "candidate_review_packet_export_v0_1.json"
)
AGENT_OUTPUT_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_output_contract_v0_1.json"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _review_packet_module():
    try:
        return importlib.import_module("well_harness.agent_review_packet")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_review_packet module: {exc}")


def _logic_ir_packet() -> dict:
    return _load_json(AGENT_OUTPUT_FIXTURE_PATH)


def _approval(task_id: str) -> dict:
    return {
        "approval_id": "APPROVAL-REVIEW-PACKET-001",
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-20T00:00:00Z",
    }


def _artifacts_for_packet(packet: dict) -> tuple[dict, dict, dict, dict, dict]:
    safety = run_safety_guardian_checks(packet)
    evidence = run_evidence_agent_checks(packet)
    contracts = {"logic_ir": packet, "safety_guardian": safety, "evidence": evidence}
    task_package = build_chief_engineer_task_package(contracts)
    execution_plan = build_execution_plan_from_task_package(task_package)
    execution_evidence = build_execution_evidence_package(task_package)
    return contracts, task_package, execution_plan, execution_evidence, safety


def _transition_by_id(packet: dict, transition_id: str) -> dict:
    for transition in packet["agent_output"]["payload"]["logic_ir"]["transitions"]:
        if transition["id"] == transition_id:
            return transition
    raise AssertionError(f"missing transition {transition_id}")


def test_candidate_review_packet_schema_and_fixture_are_valid() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == "ai-fantui-candidate-review-packet"
    assert schema["x-well-harness-candidate-review-packet"]["schema_version"] == "0.1"
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert fixture["reviewer"]["agent_name"] == "CandidateReviewPacketAgent"
    assert fixture["reviewer"]["status"] == "blocked_pending_approval"
    assert fixture["boundary"]["truth_effect"] == "none"


def test_candidate_review_packet_export_schema_fixture_and_reference_are_valid() -> None:
    review = _review_packet_module()
    schema = _load_json(EXPORT_SCHEMA_PATH)
    fixture = _load_json(EXPORT_FIXTURE_PATH)
    reference = _load_json(REFERENCE_EXPORT_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == EXPORT_SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == "ai-fantui-candidate-review-packet-export"
    assert schema["x-well-harness-candidate-review-packet-export"]["schema_version"] == "0.1"
    Draft202012Validator.check_schema(schema)

    for packet in (fixture, reference):
        errors = sorted(
            Draft202012Validator(schema).iter_errors(packet),
            key=lambda error: list(error.path),
        )
        assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
        review.validate_candidate_review_packet_export(packet)
        assert packet["exporter"]["agent_name"] == "CandidateReviewPacketExportAgent"
        assert packet["exporter"]["export_route"] == "/logic-builder/candidate-review-packet.json"
        assert packet["review_packet"]["kind"] == "ai-fantui-candidate-review-packet"
        assert packet["boundary"]["truth_effect"] == "none"


def test_candidate_review_packet_export_builder_wraps_review_packet_for_external_review() -> None:
    review = _review_packet_module()
    packet = _load_json(FIXTURE_PATH)

    export_packet = review.build_candidate_review_packet_export(packet)

    review.validate_candidate_review_packet_export(export_packet)
    assert export_packet["kind"] == "ai-fantui-candidate-review-packet-export"
    assert export_packet["exporter"] == {
        "agent_name": "CandidateReviewPacketExportAgent",
        "schema_version": "0.1",
        "export_id": "latest-candidate-review-packet",
        "source_route": "/logic-builder",
        "export_route": "/logic-builder/candidate-review-packet.json",
        "storage": "reference_packet",
        "status": "available",
    }
    assert export_packet["review_packet"] == packet
    assert export_packet["review_packet_ref"] == {
        "schema": "https://well-harness.local/json_schema/candidate_review_packet_v0_1.schema.json",
        "kind": "ai-fantui-candidate-review-packet",
        "reviewer_status": "blocked_pending_approval",
    }
    assert export_packet["machine_readable"] is True
    assert export_packet["human_review_required"] is True


def test_review_packet_exposes_blocked_safety_chain_without_approval() -> None:
    review = _review_packet_module()
    packet = _logic_ir_packet()
    contracts, task_package, execution_plan, execution_evidence, _ = _artifacts_for_packet(packet)
    safety_loop = run_safety_guardian_repair_loop(packet)

    review_packet = review.build_candidate_review_packet(
        contracts,
        task_package=task_package,
        execution_plan=execution_plan,
        execution_evidence_package=execution_evidence,
        repair_loop_results=[safety_loop],
    )

    review.validate_candidate_review_packet(review_packet)
    assert review_packet["reviewer"]["status"] == "blocked_pending_approval"
    assert review_packet["summary"] == {
        "total_findings": 1,
        "loop_count": 1,
        "converged_loops": 0,
        "blocked_loops": 1,
        "needs_followup_loops": 0,
        "open_findings": ["CHECK_SAFETY_PRIORITY_001"],
    }
    assert review_packet["finding_chains"] == [
        {
            "loop_kind": "ai-fantui-safety-repair-loop",
            "status": "blocked_missing_approval",
            "finding": {
                "code": "CHECK_SAFETY_PRIORITY_001",
                "severity": "critical",
                "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
                "transition_id": "T004",
            },
            "approval": {
                "status": "missing",
                "approval_id": "",
                "approved_task_id": "",
                "approved_by": "",
            },
            "repair": {"actions": [], "performed": False},
            "before": {
                "safety_status": "fail",
                "evidence_status": "pass",
                "task_package_status": "tasks_ready_for_review",
                "execution_plan_status": "dry_run_ready",
                "execution_evidence_status": "blocked_missing_approval",
            },
            "after": {},
            "convergence": {},
        }
    ]


def test_review_packet_exposes_converged_safety_and_evidence_chains() -> None:
    review = _review_packet_module()
    safety_packet = _logic_ir_packet()
    contracts, task_package, execution_plan, execution_evidence, _ = _artifacts_for_packet(safety_packet)
    safety_loop = run_safety_guardian_repair_loop(
        safety_packet,
        approval=_approval("TASK-CE-CHECK-SAFETY-PRIORITY-001"),
    )
    evidence_packet = _logic_ir_packet()
    _transition_by_id(evidence_packet, "T004")["priority"] = "safety"
    evidence_packet["agent_output"]["payload"]["simulation_results"][1]["status"] = "fail"
    evidence_loop = run_evidence_agent_repair_loop(
        evidence_packet,
        approval=_approval("TASK-CE-EV-SIMULATION-RESULT-FAILED"),
    )

    review_packet = review.build_candidate_review_packet(
        contracts,
        task_package=task_package,
        execution_plan=execution_plan,
        execution_evidence_package=execution_evidence,
        repair_loop_results=[safety_loop, evidence_loop],
    )

    review.validate_candidate_review_packet(review_packet)
    assert review_packet["reviewer"]["status"] == "converged"
    assert review_packet["summary"]["loop_count"] == 2
    assert review_packet["summary"]["converged_loops"] == 2
    assert review_packet["summary"]["open_findings"] == []
    assert [chain["finding"]["code"] for chain in review_packet["finding_chains"]] == [
        "CHECK_SAFETY_PRIORITY_001",
        "EV_SIMULATION_RESULT_FAILED",
    ]
    assert review_packet["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "set_transition_priority",
            "transition_id": "T004",
            "from": "normal",
            "to": "safety",
            "reason": "CHECK_SAFETY_PRIORITY_001",
        }
    ]
    assert review_packet["finding_chains"][1]["repair"]["actions"] == [
        {
            "action": "set_simulation_result_status",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "from": "fail",
            "to": "pass",
            "reason": "EV_SIMULATION_RESULT_FAILED",
        }
    ]


def test_review_packet_reports_no_findings_when_candidate_is_clean() -> None:
    review = _review_packet_module()
    packet = _logic_ir_packet()
    _transition_by_id(packet, "T004")["priority"] = "safety"
    contracts, task_package, execution_plan, execution_evidence, _ = _artifacts_for_packet(packet)

    review_packet = review.build_candidate_review_packet(
        contracts,
        task_package=task_package,
        execution_plan=execution_plan,
        execution_evidence_package=execution_evidence,
        repair_loop_results=[],
    )

    review.validate_candidate_review_packet(review_packet)
    assert review_packet["reviewer"]["status"] == "no_findings"
    assert review_packet["summary"] == {
        "total_findings": 0,
        "loop_count": 0,
        "converged_loops": 0,
        "blocked_loops": 0,
        "needs_followup_loops": 0,
        "open_findings": [],
    }
    assert review_packet["finding_chains"] == []
    assert review_packet["source_artifacts"]["task_package_status"] == "no_tasks_required"
    assert review_packet["source_artifacts"]["execution_plan_status"] == "no_task_available"
    assert review_packet["source_artifacts"]["execution_evidence_status"] == "no_task_available"

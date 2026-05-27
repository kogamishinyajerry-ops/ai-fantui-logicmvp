from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/agent_output_contract_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "agent_output_contract_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_output_contract_v0_1.json"


def _load_schema() -> dict:
    assert SCHEMA_PATH.exists(), f"missing schema: {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_fixture() -> dict:
    assert FIXTURE_PATH.exists(), f"missing fixture: {FIXTURE_PATH}"
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _contract_module():
    try:
        return importlib.import_module("well_harness.agent_output_contract")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_output_contract module: {exc}")


def test_schema_document_declares_agent_output_contract_fields() -> None:
    schema = _load_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["type"] == "object"
    assert schema["properties"]["$schema"]["const"] == SCHEMA_ID

    contract_meta = schema["x-well-harness-agent-output-contract"]
    assert contract_meta["schema_name"] == "well_harness.agent_output_contract"
    assert contract_meta["schema_version"] == "0.1"
    assert contract_meta["boundary_fields"] == [
        "candidate_state",
        "truth_effect",
        "controller_truth_modified",
        "certification_claim",
    ]

    required_agent_fields = set(schema["$defs"]["agentOutput"]["required"])
    assert {
        "agent_name",
        "task_id",
        "input_artifacts",
        "output_artifacts",
        "assumptions",
        "open_issues",
        "confidence",
        "validation",
        "boundary",
        "human_review_required",
    } <= required_agent_fields


def test_fixture_is_schema_valid_candidate_logic_ir_packet() -> None:
    schema = _load_schema()
    fixture = _load_fixture()

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    agent_output = fixture["agent_output"]
    assert agent_output["agent_name"] == "LogicIRAgent"
    assert agent_output["boundary"] == {
        "candidate_state": "sandbox_candidate",
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
    }
    assert agent_output["validation"]["schema_valid"] is True
    assert agent_output["validation"]["deterministic_checks_passed"] is False
    assert agent_output["validation"]["failed_checks"][0]["code"] == "CHECK_SAFETY_PRIORITY_001"


def test_contract_validator_rejects_candidate_boundary_drift() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    unsafe = copy.deepcopy(payload)
    unsafe["agent_output"]["boundary"]["truth_effect"] = "controller_truth"

    with pytest.raises(contract.AgentOutputContractError, match="truth_effect"):
        contract.validate_agent_output_contract(unsafe)


def test_safety_guardian_reports_missing_safety_priority() -> None:
    contract = _contract_module()
    payload = _load_fixture()

    report = contract.run_safety_guardian_checks(payload)

    assert report["agent_name"] == "SafetyGuardianAgent"
    assert report["status"] == "fail"
    assert report["boundary"] == payload["agent_output"]["boundary"]
    assert report["findings"][0]["code"] == "CHECK_SAFETY_PRIORITY_001"
    assert report["findings"][0]["severity"] == "critical"
    assert report["findings"][0]["transition_id"] == "T004"


def test_evidence_agent_reports_requirement_to_ir_to_test_coverage() -> None:
    contract = _contract_module()
    payload = _load_fixture()

    report = contract.run_evidence_agent_checks(payload)

    assert report["agent_name"] == "EvidenceAgent"
    assert report["status"] == "pass"
    assert report["coverage"]["requirements"]["total"] == 2
    assert report["coverage"]["requirements"]["covered_by_ir"] == 2
    assert report["coverage"]["requirements"]["covered_by_tests"] == 2
    assert report["coverage"]["test_scenarios"]["with_results"] == 2
    assert report["trace_matrix"][0]["requirement_id"] == "REQ-START-001"
    assert report["trace_matrix"][0]["ir_elements"] == ["T001", "T003"]
    assert report["trace_matrix"][0]["test_cases"] == ["TC-NORMAL-START-001"]


def test_evidence_agent_fails_when_test_result_is_missing() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    missing_result = copy.deepcopy(payload)
    missing_result["agent_output"]["payload"]["simulation_results"] = [
        {"scenario_id": "TC-NORMAL-START-001", "status": "pass"}
    ]

    report = contract.run_evidence_agent_checks(missing_result)

    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "EV_TEST_RESULT_MISSING"
    assert report["findings"][0]["scenario_id"] == "TC-HOT-START-ABORT-001"


def test_safety_guardian_reports_same_state_transition_overlap() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    payload["agent_output"]["payload"]["logic_ir"]["transitions"].append(
        {
            "id": "T005",
            "from": "FUEL_ON",
            "to": "START_REQUESTED",
            "guard": "EGT > EGT_START_LIMIT",
            "guard_signals": ["EGT", "EGT_START_LIMIT"],
            "priority": "normal",
            "trace": {"requirements": ["REQ-SAFE-001"]},
        }
    )

    report = contract.run_safety_guardian_checks(payload)

    overlap_findings = [
        finding
        for finding in report["findings"]
        if finding["code"] == "CHECK_TRANSITION_OVERLAP_001"
    ]
    assert overlap_findings == [
        {
            "code": "CHECK_TRANSITION_OVERLAP_001",
            "severity": "high",
            "message": "Transitions T004 and T005 leave FUEL_ON with overlapping guards and no safety priority separation.",
            "state_id": "FUEL_ON",
            "transition_ids": "T004,T005",
        }
    ]


def test_safety_guardian_reports_unreachable_state() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    logic_ir = payload["agent_output"]["payload"]["logic_ir"]
    logic_ir["states"].append("SENSOR_DEGRADED")

    report = contract.run_safety_guardian_checks(payload)

    unreachable_findings = [
        finding
        for finding in report["findings"]
        if finding["code"] == "CHECK_UNREACHABLE_STATE_001"
    ]
    assert unreachable_findings == [
        {
            "code": "CHECK_UNREACHABLE_STATE_001",
            "severity": "high",
            "message": "State SENSOR_DEGRADED is not reachable from IDLE.",
            "state_id": "SENSOR_DEGRADED",
            "initial_state": "IDLE",
        }
    ]


def test_safety_guardian_reports_bad_transition_endpoint_and_output_conflict() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    transitions = payload["agent_output"]["payload"]["logic_ir"]["transitions"]
    transitions[2]["action"] = {"fuel_valve_cmd": "OPEN"}
    transitions.append(
        {
            "id": "T006",
            "from": "FUEL_ON",
            "to": "ABORTED",
            "guard": "EGT > EGT_START_LIMIT",
            "guard_signals": ["EGT", "EGT_START_LIMIT"],
            "priority": "normal",
            "action": {"fuel_valve_cmd": "CLOSE"},
            "trace": {"requirements": ["REQ-SAFE-001"]},
        }
    )
    transitions.append(
        {
            "id": "T_BAD_ENDPOINT",
            "from": "FUEL_ON",
            "to": "MISSING_STATE",
            "guard": "EGT_valid == false",
            "guard_signals": [],
            "priority": "normal",
            "trace": {"requirements": ["REQ-SAFE-001"]},
        }
    )

    report = contract.run_safety_guardian_checks(payload)

    endpoint_findings = [
        finding
        for finding in report["findings"]
        if finding["code"] == "CHECK_TRANSITION_ENDPOINT_001"
    ]
    assert endpoint_findings == [
        {
            "code": "CHECK_TRANSITION_ENDPOINT_001",
            "severity": "high",
            "message": "Transition T_BAD_ENDPOINT targets unknown state MISSING_STATE.",
            "transition_id": "T_BAD_ENDPOINT",
            "endpoint": "to",
            "state_id": "MISSING_STATE",
        }
    ]
    conflict_findings = [
        finding
        for finding in report["findings"]
        if finding["code"] == "CHECK_OUTPUT_COMMAND_CONFLICT_001"
    ]
    assert conflict_findings == [
        {
            "code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
            "severity": "critical",
            "message": "Transitions T004 and T006 can assign conflicting fuel_valve_cmd commands.",
            "state_id": "FUEL_ON",
            "transition_ids": "T004,T006",
            "signal_name": "fuel_valve_cmd",
            "left_value": "OPEN",
            "right_value": "CLOSE",
        }
    ]


def test_evidence_agent_reports_orphan_ir_unknown_test_cover_and_failed_result() -> None:
    contract = _contract_module()
    payload = _load_fixture()
    logic_ir = payload["agent_output"]["payload"]["logic_ir"]
    logic_ir["transitions"][0].pop("trace")
    payload["agent_output"]["payload"]["test_scenarios"][0]["covers"] = [
        "REQ-START-001",
        "REQ-UNKNOWN-999",
    ]
    payload["agent_output"]["payload"]["simulation_results"][1]["status"] = "fail"

    report = contract.run_evidence_agent_checks(payload)

    findings = {finding["code"]: finding for finding in report["findings"]}
    assert findings["EV_IR_ELEMENT_MISSING_REQUIREMENT_TRACE"] == {
        "code": "EV_IR_ELEMENT_MISSING_REQUIREMENT_TRACE",
        "severity": "high",
        "message": "IR element T001 has no requirement trace.",
        "ir_element_id": "T001",
        "element_kind": "transition",
    }
    assert findings["EV_TEST_COVERS_UNKNOWN_REQUIREMENT"] == {
        "code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        "severity": "warning",
        "message": "Test scenario TC-NORMAL-START-001 covers unknown requirement REQ-UNKNOWN-999.",
        "scenario_id": "TC-NORMAL-START-001",
        "requirement_id": "REQ-UNKNOWN-999",
    }
    assert findings["EV_SIMULATION_RESULT_FAILED"] == {
        "code": "EV_SIMULATION_RESULT_FAILED",
        "severity": "high",
        "message": "Simulation result for TC-HOT-START-ABORT-001 is fail.",
        "scenario_id": "TC-HOT-START-ABORT-001",
        "status": "fail",
    }

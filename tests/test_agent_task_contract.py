from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_safety_guardian_checks,
)


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/agent_task_contract_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "agent_task_contract_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_task_contract_v0_1.json"
AGENT_OUTPUT_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_output_contract_v0_1.json"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _task_contract_module():
    try:
        return importlib.import_module("well_harness.agent_task_contract")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_task_contract module: {exc}")


def _agent_outputs_with_findings() -> dict:
    logic_ir_packet = _load_json(AGENT_OUTPUT_FIXTURE_PATH)
    evidence_packet = copy.deepcopy(logic_ir_packet)
    evidence_packet["agent_output"]["payload"]["test_scenarios"][0]["covers"] = [
        "REQ-START-001",
        "REQ-UNKNOWN-999",
    ]
    evidence_packet["agent_output"]["payload"]["simulation_results"][1]["status"] = "fail"
    return {
        "logic_ir": logic_ir_packet,
        "safety_guardian": run_safety_guardian_checks(logic_ir_packet),
        "evidence": run_evidence_agent_checks(evidence_packet),
    }


def test_agent_task_schema_declares_candidate_development_task_contract() -> None:
    schema = _load_json(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["type"] == "object"
    assert schema["properties"]["$schema"]["const"] == SCHEMA_ID

    meta = schema["x-well-harness-agent-task-contract"]
    assert meta["schema_version"] == "0.1"
    assert meta["top_level_fields"] == ["$schema", "kind", "chief_engineer", "tasks"]
    required_task_fields = set(schema["$defs"]["agentTask"]["required"])
    assert {
        "task_id",
        "target_agent",
        "task_type",
        "priority",
        "status",
        "input_artifacts",
        "allowed_files",
        "forbidden_files",
        "change_boundary",
        "findings",
        "instructions",
        "done_when",
        "stop_if",
        "verification_commands",
        "human_review_required",
    } <= required_task_fields


def test_agent_task_fixture_is_schema_valid_and_candidate_bounded() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    task = fixture["tasks"][0]
    assert task["target_agent"] == "LogicIRRepairAgent"
    assert task["change_boundary"] == {
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
        "allowed_to_modify_controller_truth": False,
    }
    assert "src/well_harness/controller.py" in task["forbidden_files"]


def test_task_contract_validator_rejects_controller_truth_authorization() -> None:
    contract = _task_contract_module()
    fixture = _load_json(FIXTURE_PATH)
    unsafe = copy.deepcopy(fixture)
    unsafe["tasks"][0]["change_boundary"]["allowed_to_modify_controller_truth"] = True

    with pytest.raises(contract.AgentTaskContractError, match="controller truth"):
        contract.validate_agent_task_package(unsafe)


def test_chief_engineer_generates_reviewable_tasks_from_safety_and_evidence_findings() -> None:
    contract = _task_contract_module()

    package = contract.build_chief_engineer_task_package(
        _agent_outputs_with_findings(),
        source_artifact_id="LOGIC_DRAWING_CANDIDATE_v0.1",
    )

    contract.validate_agent_task_package(package)
    assert package["kind"] == "ai-fantui-chief-engineer-task-package"
    assert package["chief_engineer"]["agent_name"] == "ChiefEngineerAgent"
    assert package["chief_engineer"]["source_artifact_id"] == "LOGIC_DRAWING_CANDIDATE_v0.1"
    assert package["chief_engineer"]["status"] == "tasks_ready_for_review"
    assert package["chief_engineer"]["finding_counts"] == {
        "critical": 1,
        "high": 1,
        "warning": 1,
        "info": 0,
    }
    assert [task["task_id"] for task in package["tasks"]] == [
        "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
    ]
    first_task = package["tasks"][0]
    assert first_task["target_agent"] == "LogicIRRepairAgent"
    assert first_task["task_type"] == "repair_candidate_logic_ir"
    assert first_task["priority"] == "critical"
    assert first_task["status"] == "proposed"
    assert first_task["findings"][0]["code"] == "CHECK_SAFETY_PRIORITY_001"
    assert "src/well_harness/controller.py" in first_task["forbidden_files"]
    assert first_task["change_boundary"]["truth_effect"] == "none"
    assert first_task["change_boundary"]["controller_truth_modified"] is False
    assert first_task["human_review_required"] is True
    assert first_task["verification_commands"] == [
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_output_contract.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_task_contract.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_execution_plan.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_execution_shell.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_repair_loop.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_review_packet.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_development_slice.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_evidence_development_slice.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_approved_repair_slices_gate.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_repair_slices_artifact_checker.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_repair_slices_summary_schema.py",
        "make approved-repair-slices",
        "make missing-test-result-candidate-repair-slice",
        "make evidence-unknown-requirement-candidate-repair-slice",
        "make evidence-unknown-trace-candidate-repair-slice",
        "make safety-transition-endpoint-candidate-repair-slice",
        "make safety-unreachable-state-candidate-repair-slice",
        "make safety-output-command-conflict-candidate-repair-slice",
        "make verify-approved-repair-slices-artifact",
        "make multi-agent-construction-readiness",
        "make approved-candidate-task-queue",
        "make verify-approved-candidate-task-queue-artifact",
        "make verify-approved-candidate-task-queue-expansion-contract",
        "PYTHONPATH=src:. python3 scripts/verify_candidate_review_packet_export.py --format json",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_artifact_checker.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_expansion_contract.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_deliverable_plan.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m3_safety_evidence_value_pack.py",
        "make multi-agent-m3-safety-evidence-value-pack",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m4_external_review_handoff.py",
        "make multi-agent-m4-external-review-handoff",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m5_construction_control_plane.py",
        "make multi-agent-construction-control-plane",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m6_queue_extension_template.py",
        "make multi-agent-queue-extension-template",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_2.py",
        "make approved-candidate-task-queue-v0-2",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_3.py",
        "make approved-candidate-task-queue-v0-3",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_4.py",
        "make approved-candidate-task-queue-v0-4",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_5.py",
        "make approved-candidate-task-queue-v0-5",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_6.py",
        "make approved-candidate-task-queue-v0-6",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_7.py",
        "make approved-candidate-task-queue-v0-7",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_8.py",
        "make approved-candidate-task-queue-v0-8",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_9.py",
        "make approved-candidate-task-queue-v0-9",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_run_ledger.py",
        "make multi-agent-queue-run-ledger",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_cursor_state.py",
        "make multi-agent-queue-cursor-state",
        "make multi-agent-queue-cursor-resume-state",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_run_ledger_v0_2.py",
        "make multi-agent-queue-run-ledger-v0-2",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_cursor_state_v0_2.py",
        "make multi-agent-queue-cursor-state-v0-2",
        "make multi-agent-queue-cursor-resume-state-v0-2",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m8_fast_construction_gate.py",
        "make multi-agent-fast-construction-gate",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_candidate_review_packet_export_regression.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_requirements_intake_webui.py",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_editable_control_model.py",
        "git diff --check",
    ]
    assert any("controller truth" in item for item in first_task["stop_if"])


def test_chief_engineer_returns_noop_package_when_no_findings_exist() -> None:
    contract = _task_contract_module()
    logic_ir_packet = _load_json(AGENT_OUTPUT_FIXTURE_PATH)
    logic_ir_packet["agent_output"]["payload"]["logic_ir"]["transitions"][2]["priority"] = "safety"
    outputs = {
        "logic_ir": logic_ir_packet,
        "safety_guardian": run_safety_guardian_checks(logic_ir_packet),
        "evidence": run_evidence_agent_checks(logic_ir_packet),
    }

    package = contract.build_chief_engineer_task_package(outputs)

    contract.validate_agent_task_package(package)
    assert package["chief_engineer"]["status"] == "no_tasks_required"
    assert package["tasks"] == []

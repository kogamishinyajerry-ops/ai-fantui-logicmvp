"""M2 candidate-only requirement-to-IR demo chain."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.agent_output_contract import (
    build_agent_output_packet,
    run_evidence_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_repair_loop import run_safety_guardian_repair_loop
from well_harness.agent_review_packet import (
    build_candidate_review_packet,
    build_candidate_review_packet_export,
    validate_candidate_review_packet_export,
)
from well_harness.agent_task_contract import (
    build_chief_engineer_task_package,
    validate_agent_task_package,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m2-requirement-to-ir-demo"
)
M2_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m2_requirement_to_ir_demo_v0_1.schema.json"
)
M2_SCHEMA_NAME = "multi_agent_m2_requirement_to_ir_demo_v0_1.schema.json"
M2_PACKAGE_NAME = "multi_agent_m2_requirement_to_ir_demo_v0_1.json"
M2_PACKAGE_ID = "multi-agent-m2-requirement-to-ir-demo-v0.1"
M2_REVIEW_EXPORT_ID = "multi-agent-m2-requirement-to-ir-demo"
SOURCE_REQUIREMENT_ID = "engine-start-control-requirement-v0.1"
SOURCE_REQUIREMENT_TEXT = (
    "When the start switch is opened, engage the starter. "
    "When N2 reaches 25 percent, open the fuel valve and turn ignition on. "
    "If EGT exceeds 900 degC, abort the start. "
    "If no light-off is detected within 20 seconds, abort the start."
)
REQUIREMENT_IDS = [
    "REQ-START-001",
    "REQ-START-002",
    "REQ-SAFE-001",
    "REQ-SAFE-002",
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M2_SCHEMA_NAME)


def validate_m2_requirement_to_ir_demo_package(package: dict[str, Any]) -> None:
    """Validate the M2 demo package schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(f"M2 requirement-to-IR demo schema validation failed{location}: {exc.message}") from exc


def build_engine_start_requirement_fixture() -> dict[str, Any]:
    """Return the raw M2 source requirement fixture."""
    return {
        "fixture_id": SOURCE_REQUIREMENT_ID,
        "domain": "engine_start_control",
        "text": SOURCE_REQUIREMENT_TEXT,
    }


def build_engine_start_structured_requirements() -> list[dict[str, Any]]:
    """Deterministically structure the M2 engine-start requirement text."""
    return [
        {
            "id": "REQ-START-001",
            "text": "When the start switch is opened, engage the starter.",
            "type": "functional",
            "related_signals": ["start_switch", "starter_cmd"],
            "derived_logic": ["state_transition", "output_action"],
            "verifiability": "full",
        },
        {
            "id": "REQ-START-002",
            "text": "When N2 reaches 25 percent, open the fuel valve and turn ignition on.",
            "type": "functional",
            "related_signals": ["N2", "N2_FUEL_ON_THRESHOLD", "fuel_valve_cmd", "ignition_cmd"],
            "derived_logic": ["guarded_transition", "output_action"],
            "verifiability": "full",
        },
        {
            "id": "REQ-SAFE-001",
            "text": "If EGT exceeds 900 degC, abort the start.",
            "type": "safety",
            "related_signals": ["EGT", "EGT_START_LIMIT"],
            "derived_logic": ["safety_transition", "invariant"],
            "verifiability": "full",
        },
        {
            "id": "REQ-SAFE-002",
            "text": "If no light-off is detected within 20 seconds, abort the start.",
            "type": "timing_safety",
            "related_signals": ["light_off_detected", "start_elapsed_s", "START_TIMEOUT_S"],
            "derived_logic": ["timeout_transition", "invariant"],
            "verifiability": "partial",
            "ambiguity": ["light-off debounce time is not defined"],
        },
    ]


def _signals() -> list[dict[str, Any]]:
    return [
        {"name": "start_switch", "type": "boolean"},
        {"name": "starter_cmd", "type": "enum", "values": ["ENGAGE", "DISENGAGE"]},
        {"name": "N2", "type": "float", "unit": "percent", "range": [0, 120]},
        {"name": "N2_FUEL_ON_THRESHOLD", "type": "float", "unit": "percent"},
        {"name": "N2_STABILIZED_THRESHOLD", "type": "float", "unit": "percent"},
        {"name": "fuel_valve_cmd", "type": "enum", "values": ["OPEN", "CLOSE"]},
        {"name": "ignition_cmd", "type": "enum", "values": ["ON", "OFF"]},
        {"name": "EGT", "type": "float", "unit": "degC", "range": [-50, 1200]},
        {"name": "EGT_START_LIMIT", "type": "float", "unit": "degC"},
        {"name": "light_off_detected", "type": "boolean"},
        {"name": "start_elapsed_s", "type": "float", "unit": "s"},
        {"name": "START_TIMEOUT_S", "type": "float", "unit": "s"},
    ]


def _logic_ir() -> dict[str, Any]:
    return {
        "id": "ENG_START_CTRL_M2",
        "type": "state_machine",
        "initial_state": "IDLE",
        "states": [
            "IDLE",
            "STARTER_ENGAGED",
            "FUEL_IGNITION",
            "LIGHT_OFF_CONFIRMED",
            "STABILIZED",
            "ABORTED",
        ],
        "transitions": [
            {
                "id": "T001",
                "from": "IDLE",
                "to": "STARTER_ENGAGED",
                "guard": "start_switch == true",
                "guard_signals": ["start_switch"],
                "priority": "normal",
                "action": {"starter_cmd": "ENGAGE"},
                "trace": {"requirements": ["REQ-START-001"]},
            },
            {
                "id": "T002",
                "from": "STARTER_ENGAGED",
                "to": "FUEL_IGNITION",
                "guard": "N2 >= N2_FUEL_ON_THRESHOLD",
                "guard_signals": ["N2", "N2_FUEL_ON_THRESHOLD"],
                "priority": "normal",
                "action": {"fuel_valve_cmd": "OPEN", "ignition_cmd": "ON"},
                "trace": {"requirements": ["REQ-START-002"]},
            },
            {
                "id": "T003",
                "from": "FUEL_IGNITION",
                "to": "ABORTED",
                "guard": (
                    "EGT > EGT_START_LIMIT or "
                    "(start_elapsed_s > START_TIMEOUT_S and light_off_detected == false)"
                ),
                "guard_signals": [
                    "EGT",
                    "EGT_START_LIMIT",
                    "start_elapsed_s",
                    "START_TIMEOUT_S",
                    "light_off_detected",
                ],
                "priority": "normal",
                "safety_condition": True,
                "action": {
                    "fuel_valve_cmd": "CLOSE",
                    "starter_cmd": "DISENGAGE",
                    "ignition_cmd": "OFF",
                },
                "trace": {"requirements": ["REQ-SAFE-001", "REQ-SAFE-002"]},
            },
            {
                "id": "T004",
                "from": "FUEL_IGNITION",
                "to": "LIGHT_OFF_CONFIRMED",
                "guard": "light_off_detected == true",
                "guard_signals": ["light_off_detected"],
                "priority": "normal",
                "trace": {"requirements": ["REQ-START-002"]},
            },
            {
                "id": "T005",
                "from": "LIGHT_OFF_CONFIRMED",
                "to": "STABILIZED",
                "guard": "N2 >= N2_STABILIZED_THRESHOLD",
                "guard_signals": ["N2", "N2_STABILIZED_THRESHOLD"],
                "priority": "normal",
                "action": {"starter_cmd": "DISENGAGE"},
                "trace": {"requirements": ["REQ-START-002"]},
            },
        ],
        "invariants": [
            {
                "id": "INV001",
                "expression": "EGT > EGT_START_LIMIT implies eventually state == ABORTED",
                "trace": {"requirements": ["REQ-SAFE-001"]},
            },
            {
                "id": "INV002",
                "expression": (
                    "start_elapsed_s > START_TIMEOUT_S and light_off_detected == false "
                    "implies eventually state == ABORTED"
                ),
                "trace": {"requirements": ["REQ-SAFE-002"]},
            },
        ],
    }


def _test_scenarios() -> list[dict[str, Any]]:
    return [
        {"id": "TC-NORMAL-START-001", "covers": ["REQ-START-001", "REQ-START-002"]},
        {"id": "TC-HOT-START-ABORT-001", "covers": ["REQ-SAFE-001"]},
        {"id": "TC-NO-LIGHTOFF-TIMEOUT-001", "covers": ["REQ-SAFE-002"]},
    ]


def _simulation_results() -> list[dict[str, Any]]:
    return [
        {"scenario_id": "TC-NORMAL-START-001", "status": "pass"},
        {"scenario_id": "TC-HOT-START-ABORT-001", "status": "pass"},
        {"scenario_id": "TC-NO-LIGHTOFF-TIMEOUT-001", "status": "pass"},
    ]


def build_m2_candidate_agent_output() -> dict[str, Any]:
    """Build the candidate Logic IR packet produced by the M2 demo chain."""
    payload = {
        "requirements": build_engine_start_structured_requirements(),
        "signals": _signals(),
        "logic_ir": _logic_ir(),
        "test_scenarios": _test_scenarios(),
        "simulation_results": _simulation_results(),
    }
    packet = build_agent_output_packet(
        agent_name="LogicIRAgent",
        task_id="TASK-M2-REQ-TO-IR-001",
        input_artifacts=["ENGINE_START_REQUIREMENT_v0.1"],
        output_artifacts=["LOGIC_IR_M2_v0.1"],
        candidate_state="sandbox_candidate",
        payload=payload,
        assumptions=[
            "EGT_START_LIMIT is set to 900 degC from the source requirement text.",
            "Light-off debounce time is not defined and remains an open engineering question.",
        ],
        open_issues=[
            "Abort reset and restart policy is not defined.",
            "Light-off debounce and sensor validity policy require human review.",
        ],
        confidence_level="medium",
        confidence_reason=(
            "The M2 candidate is deterministic and traceable, but safety priority is "
            "intentionally failed before the approved repair loop."
        ),
        deterministic_checks_passed=False,
        failed_checks=[],
        human_review_required=True,
    )
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    findings = [
        item
        for report in (safety_report, evidence_report)
        for item in report.get("findings", [])
        if isinstance(item, dict)
    ]
    packet["agent_output"]["validation"]["failed_checks"] = findings
    packet["agent_output"]["validation"]["deterministic_checks_passed"] = not findings
    validate_agent_output_contract(packet)
    return packet


def _approval(task_id: str) -> dict[str, Any]:
    return {
        "approval_id": "APPROVAL-M2-REQ-TO-IR-DEMO-001",
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-21T00:00:00Z",
    }


def _finding_codes(report: dict[str, Any]) -> list[str]:
    return [
        str(item["code"])
        for item in report.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ]


def _finding_chain_statuses(review_export: dict[str, Any]) -> list[str]:
    chains = review_export.get("review_packet", {}).get("finding_chains", [])
    return [
        str(chain.get("status", ""))
        for chain in chains
        if isinstance(chain, dict)
    ]


def _selected_task_summary(task_package: dict[str, Any]) -> dict[str, Any]:
    tasks = task_package.get("tasks", [])
    selected = tasks[0] if isinstance(tasks, list) and tasks else {}
    return {
        "status": str(task_package.get("chief_engineer", {}).get("status", "")),
        "task_count": int(task_package.get("chief_engineer", {}).get("task_count", 0)),
        "selected_task_id": str(selected.get("task_id", "")),
        "selected_agent": str(selected.get("target_agent", "")),
    }


def _requirement_traceability_pass(evidence_report: dict[str, Any]) -> bool:
    coverage = evidence_report.get("coverage", {}).get("requirements", {})
    return (
        evidence_report.get("status") == "pass"
        and coverage.get("total") == 4
        and coverage.get("covered_by_ir") == 4
        and coverage.get("covered_by_tests") == 4
    )


def run_m2_requirement_to_ir_demo(
    *,
    artifact_dir: Path = DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Run Requirement -> IR -> Safety finding -> approved repair -> review export."""
    source_requirement = build_engine_start_requirement_fixture()
    candidate_packet = build_m2_candidate_agent_output()
    safety_report = run_safety_guardian_checks(candidate_packet)
    evidence_report = run_evidence_agent_checks(candidate_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": candidate_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="M2_REQUIREMENT_TO_IR_DEMO_v0.1",
    )
    validate_agent_task_package(task_package)
    selected_task = task_package["tasks"][0]
    repair_loop = run_safety_guardian_repair_loop(
        candidate_packet,
        approval=_approval(str(selected_task["task_id"])),
    )
    if repair_loop.get("status") != "converged":
        raise RuntimeError(f"M2 requirement-to-IR repair loop did not converge: {repair_loop.get('status')}")
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": candidate_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=repair_loop["before"]["execution_plan"],
        execution_evidence_package=repair_loop["before"]["execution_evidence_package"],
        repair_loop_results=[repair_loop],
    )
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=M2_REVIEW_EXPORT_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    source_path = artifact_dir / "source_requirement.json"
    candidate_packet_path = artifact_dir / "candidate_agent_output_contract_v0_1.json"
    safety_report_path = artifact_dir / "safety_guardian_report.json"
    evidence_report_path = artifact_dir / "evidence_agent_report.json"
    task_package_path = artifact_dir / "chief_engineer_task_package.json"
    repair_loop_path = artifact_dir / "repair_loop_result.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    package_path = artifact_dir / M2_PACKAGE_NAME

    for path, payload in [
        (source_path, source_requirement),
        (candidate_packet_path, candidate_packet),
        (safety_report_path, safety_report),
        (evidence_report_path, evidence_report),
        (task_package_path, task_package),
        (repair_loop_path, repair_loop),
        (review_export_path, review_export),
    ]:
        _write_json(path, payload)

    logic_ir = candidate_packet["agent_output"]["payload"]["logic_ir"]
    structured_requirements = candidate_packet["agent_output"]["payload"]["requirements"]
    gates = {
        "agent_output_contract": "pass",
        "requirement_traceability": "pass" if _requirement_traceability_pass(evidence_report) else "fail",
        "safety_finding_detected": (
            "pass" if _finding_codes(safety_report) == ["CHECK_SAFETY_PRIORITY_001"] else "fail"
        ),
        "approved_task_shell": (
            "pass"
            if repair_loop["before"]["execution_evidence_package"]["executor"]["status"]
            == "executed_limited"
            else "fail"
        ),
        "repair_loop_converged": "pass" if repair_loop.get("status") == "converged" else "fail",
        "candidate_review_export": (
            "pass"
            if review_export.get("review_packet", {}).get("reviewer", {}).get("status")
            == "converged"
            else "fail"
        ),
    }
    package = {
        "$schema": M2_SCHEMA_ID,
        "kind": "ai-fantui-multi-agent-m2-requirement-to-ir-demo",
        "package_id": M2_PACKAGE_ID,
        "status": "pass" if all(value == "pass" for value in gates.values()) else "fail",
        "milestone": {
            "id": "M2",
            "name": "Requirement to IR 最小产品演示包",
            "budget": 36,
            "effort_unit": "施工队工时",
            "claim": "candidate-only requirement-to-ir demo",
        },
        "source_requirement": source_requirement,
        "structured_requirements": {
            "ids": [str(item["id"]) for item in structured_requirements],
            "ambiguities": [
                "light-off debounce time is not defined",
                "abort reset and restart policy is not defined",
            ],
        },
        "pipeline": {
            "structured_requirement_count": len(structured_requirements),
            "signal_count": len(candidate_packet["agent_output"]["payload"]["signals"]),
            "candidate_ir": {
                "id": str(logic_ir["id"]),
                "state_count": len(logic_ir["states"]),
                "transition_count": len(logic_ir["transitions"]),
            },
            "safety_findings_before": _finding_codes(safety_report),
            "evidence_findings_before": _finding_codes(evidence_report),
        },
        "task_package": _selected_task_summary(task_package),
        "review_export": {
            "reviewer_status": str(review_packet["reviewer"]["status"]),
            "finding_chain_statuses": _finding_chain_statuses(review_export),
            "export_id": M2_REVIEW_EXPORT_ID,
        },
        "deterministic_gates": gates,
        "aggregate": {
            "open_findings": list(review_packet["summary"]["open_findings"]),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "ready_for_m2_review": review_packet["reviewer"]["status"] == "converged",
        },
        "artifact_paths": {
            "demo_package": str(package_path),
            "source_requirement": str(source_path),
            "candidate_agent_output": str(candidate_packet_path),
            "task_package": str(task_package_path),
            "candidate_review_packet_export": str(review_export_path),
        },
    }
    validate_m2_requirement_to_ir_demo_package(package)
    _write_json(package_path, package)
    return copy.deepcopy(package)

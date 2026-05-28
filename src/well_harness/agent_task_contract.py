"""Chief Engineer task contracts for candidate-only multi-agent work."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema


AGENT_TASK_CONTRACT_SCHEMA_ID = (
    "https://well-harness.local/json_schema/agent_task_contract_v0_1.schema.json"
)
AGENT_TASK_CONTRACT_SCHEMA_NAME = "agent_task_contract_v0_1.schema.json"
AGENT_TASK_PACKAGE_KIND = "ai-fantui-chief-engineer-task-package"
DEFAULT_SOURCE_ARTIFACT_ID = "AGENT_OUTPUT_CONTRACT_v0.1"
SEVERITY_ORDER = {"critical": 0, "high": 1, "warning": 2, "info": 3}
CHANGE_BOUNDARY = {
    "truth_effect": "none",
    "controller_truth_modified": False,
    "certification_claim": "none",
    "allowed_to_modify_controller_truth": False,
}
ALLOWED_FILES = [
    "src/well_harness/agent_output_contract.py",
    "src/well_harness/agent_task_contract.py",
    "src/well_harness/agent_execution_plan.py",
    "src/well_harness/agent_execution_shell.py",
    "src/well_harness/agent_repair_loop.py",
    "src/well_harness/agent_review_packet.py",
    "src/well_harness/agent_development_slice.py",
    "src/well_harness/agent_safety_evidence_value_pack.py",
    "src/well_harness/agent_external_review_handoff.py",
    "src/well_harness/agent_construction_control_plane.py",
    "src/well_harness/agent_queue_extension_template.py",
    "src/well_harness/agent_fast_construction_gate.py",
    "src/well_harness/demo_server.py",
    "src/well_harness/reference_packets/candidate_review_packet_export_v0_1.json",
    "src/well_harness/requirements_intake/analysis.py",
    "src/well_harness/requirements_intake/logic_builder.py",
    ".github/workflows/gsd-automation.yml",
    "Makefile",
    "scripts/verify_candidate_review_packet_export.py",
    "scripts/run_first_candidate_repair_slice.py",
    "scripts/run_evidence_candidate_repair_slice.py",
    "scripts/run_missing_test_result_candidate_repair_slice.py",
    "scripts/run_evidence_unknown_requirement_candidate_repair_slice.py",
    "scripts/run_evidence_unknown_trace_candidate_repair_slice.py",
    "scripts/run_safety_transition_endpoint_candidate_repair_slice.py",
    "scripts/run_safety_unreachable_state_candidate_repair_slice.py",
    "scripts/run_safety_output_command_conflict_candidate_repair_slice.py",
    "scripts/run_approved_repair_slices.py",
    "scripts/verify_approved_repair_slices_artifact.py",
    "scripts/verify_multi_agent_construction_readiness.py",
    "scripts/run_approved_candidate_task_queue.py",
    "scripts/verify_approved_candidate_task_queue_artifact.py",
    "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
    "scripts/run_multi_agent_m3_safety_evidence_value_pack.py",
    "scripts/verify_multi_agent_m3_safety_evidence_value_pack.py",
    "scripts/run_multi_agent_m4_external_review_handoff.py",
    "scripts/verify_multi_agent_m4_external_review_handoff.py",
    "scripts/run_multi_agent_m5_construction_control_plane.py",
    "scripts/verify_multi_agent_m5_construction_control_plane.py",
    "scripts/run_multi_agent_m6_queue_extension_template.py",
    "scripts/verify_multi_agent_m6_queue_extension_template.py",
    "scripts/run_approved_candidate_task_queue_v0_2.py",
    "scripts/verify_approved_candidate_task_queue_v0_2_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_3.py",
    "scripts/verify_approved_candidate_task_queue_v0_3_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_4.py",
    "scripts/verify_approved_candidate_task_queue_v0_4_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_5.py",
    "scripts/verify_approved_candidate_task_queue_v0_5_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_6.py",
    "scripts/verify_approved_candidate_task_queue_v0_6_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_7.py",
    "scripts/verify_approved_candidate_task_queue_v0_7_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_8.py",
    "scripts/verify_approved_candidate_task_queue_v0_8_artifact.py",
    "scripts/run_approved_candidate_task_queue_v0_9.py",
    "scripts/verify_approved_candidate_task_queue_v0_9_artifact.py",
    "scripts/run_multi_agent_queue_run_ledger.py",
    "scripts/verify_multi_agent_queue_run_ledger.py",
    "scripts/run_multi_agent_queue_cursor_state.py",
    "scripts/verify_multi_agent_queue_cursor_state.py",
    "scripts/run_multi_agent_queue_run_ledger_v0_2.py",
    "scripts/verify_multi_agent_queue_run_ledger_v0_2.py",
    "scripts/run_multi_agent_queue_cursor_state_v0_2.py",
    "scripts/verify_multi_agent_queue_cursor_state_v0_2.py",
    "scripts/run_multi_agent_m8_fast_construction_gate.py",
    "scripts/verify_multi_agent_m8_fast_construction_gate.py",
    "tests/test_agent_output_contract.py",
    "tests/test_agent_task_contract.py",
    "tests/test_agent_execution_plan.py",
    "tests/test_agent_execution_shell.py",
    "tests/test_agent_repair_loop.py",
    "tests/test_agent_review_packet.py",
    "tests/test_agent_development_slice.py",
    "tests/test_agent_evidence_development_slice.py",
    "tests/test_agent_approved_repair_slices_gate.py",
    "tests/test_approved_repair_slices_artifact_checker.py",
    "tests/test_approved_repair_slices_summary_schema.py",
    "tests/test_multi_agent_construction_readiness.py",
    "tests/test_approved_candidate_task_queue.py",
    "tests/test_approved_candidate_task_queue_artifact_checker.py",
    "tests/test_approved_candidate_task_queue_expansion_contract.py",
    "tests/test_multi_agent_deliverable_plan.py",
    "tests/test_multi_agent_m3_safety_evidence_value_pack.py",
    "tests/test_multi_agent_m4_external_review_handoff.py",
    "tests/test_multi_agent_m5_construction_control_plane.py",
    "tests/test_multi_agent_m6_queue_extension_template.py",
    "tests/test_approved_candidate_task_queue_v0_2.py",
    "tests/test_approved_candidate_task_queue_v0_3.py",
    "tests/test_approved_candidate_task_queue_v0_4.py",
    "tests/test_approved_candidate_task_queue_v0_5.py",
    "tests/test_approved_candidate_task_queue_v0_6.py",
    "tests/test_approved_candidate_task_queue_v0_7.py",
    "tests/test_approved_candidate_task_queue_v0_8.py",
    "tests/test_approved_candidate_task_queue_v0_9.py",
    "tests/test_multi_agent_queue_run_ledger.py",
    "tests/test_multi_agent_queue_cursor_state.py",
    "tests/test_multi_agent_queue_run_ledger_v0_2.py",
    "tests/test_multi_agent_queue_cursor_state_v0_2.py",
    "tests/test_multi_agent_m8_fast_construction_gate.py",
    "tests/test_candidate_review_packet_export_regression.py",
    "tests/test_requirements_intake_webui.py",
    "tests/fixtures/agent_output_contract_v0_1.json",
    "tests/fixtures/agent_task_contract_v0_1.json",
    "tests/fixtures/agent_execution_plan_v0_1.json",
    "tests/fixtures/agent_execution_evidence_v0_1.json",
    "tests/fixtures/candidate_review_packet_v0_1.json",
    "tests/fixtures/candidate_review_packet_export_v0_1.json",
    "tests/fixtures/approved_repair_slices_summary_v0_1.json",
    "tests/fixtures/approved_candidate_task_queue_summary_v0_1.json",
    "tests/fixtures/approved_candidate_task_queue_expansion_contract_v0_1.json",
    "tests/fixtures/multi_agent_m3_safety_evidence_value_pack_v0_1.json",
    "tests/fixtures/multi_agent_m4_external_review_handoff_v0_1.json",
    "tests/fixtures/multi_agent_m5_construction_control_plane_v0_1.json",
    "tests/fixtures/multi_agent_m6_queue_extension_template_v0_1.json",
    "tests/fixtures/approved_candidate_task_queue_summary_v0_2.json",
    "tests/fixtures/approved_candidate_task_queue_summary_v0_3.json",
    "tests/fixtures/multi_agent_queue_run_ledger_v0_1.json",
    "tests/fixtures/multi_agent_queue_cursor_state_v0_1.json",
    "tests/fixtures/multi_agent_queue_cursor_state_ready_to_resume_v0_1.json",
    "tests/fixtures/multi_agent_m8_fast_construction_gate_v0_1.json",
    "docs/json_schema/agent_output_contract_v0_1.schema.json",
    "docs/json_schema/agent_task_contract_v0_1.schema.json",
    "docs/json_schema/agent_execution_plan_v0_1.schema.json",
    "docs/json_schema/agent_execution_evidence_v0_1.schema.json",
    "docs/json_schema/candidate_review_packet_v0_1.schema.json",
    "docs/json_schema/candidate_review_packet_export_v0_1.schema.json",
    "docs/json_schema/approved_repair_slices_summary_v0_1.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_1.schema.json",
    "docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json",
    "docs/json_schema/multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json",
    "docs/json_schema/multi_agent_m4_external_review_handoff_v0_1.schema.json",
    "docs/json_schema/multi_agent_m5_construction_control_plane_v0_1.schema.json",
    "docs/json_schema/multi_agent_m6_queue_extension_template_v0_1.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_2.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_3.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_4.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_5.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_6.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_7.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_8.schema.json",
    "docs/json_schema/approved_candidate_task_queue_summary_v0_9.schema.json",
    "docs/json_schema/multi_agent_queue_run_ledger_v0_1.schema.json",
    "docs/json_schema/multi_agent_queue_cursor_state_v0_1.schema.json",
    "docs/json_schema/multi_agent_queue_run_ledger_v0_2.schema.json",
    "docs/json_schema/multi_agent_queue_cursor_state_v0_2.schema.json",
    "docs/json_schema/multi_agent_m8_fast_construction_gate_v0_1.schema.json",
    "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
    "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md",
]
FORBIDDEN_FILES = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake/requirements_intake.css",
    "src/well_harness/static/requirements_intake/requirements_intake.js",
    "src/well_harness/static/requirements_intake/index.html",
]
VERIFICATION_COMMANDS = [
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


class AgentTaskContractError(ValueError):
    """Raised when a Chief Engineer task package violates the contract."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / AGENT_TASK_CONTRACT_SCHEMA_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(package: dict[str, Any]) -> None:
    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        if "allowed_to_modify_controller_truth" in path:
            raise AgentTaskContractError(
                "agent task may not authorize controller truth modification"
            ) from exc
        raise AgentTaskContractError(
            f"agent task schema validation failed{location}: {exc.message}"
        ) from exc


def _non_empty_text(value: Any, default: str) -> str:
    text = str(value).strip() if value not in (None, "") else ""
    return text or default


def _severity(value: Any) -> str:
    text = str(value).strip().lower() if value not in (None, "") else ""
    return text if text in SEVERITY_ORDER else "info"


def _finding_code(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", _non_empty_text(value, "UNKNOWN-FINDING").upper()).strip("-")


def _finding_sort_key(finding: dict[str, Any]) -> tuple[int, str]:
    return (SEVERITY_ORDER[_severity(finding.get("severity"))], _finding_code(finding.get("code")))


def _normalize_finding(finding: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(finding)
    normalized["code"] = _non_empty_text(normalized.get("code"), "UNKNOWN_FINDING")
    normalized["severity"] = _severity(normalized.get("severity"))
    normalized["message"] = _non_empty_text(normalized.get("message"), "Finding requires engineering review.")
    return normalized


def _task_id_for_finding(finding: dict[str, Any]) -> str:
    code = _finding_code(finding.get("code"))
    if code == "EV-BOUNDARY-RESULT-REVIEW-REQUIRED":
        return "TASK-CE-EV-BOUNDARY-REVIEW-001"
    return f"TASK-CE-{code}"


def _task_route_for_finding(finding: dict[str, Any]) -> tuple[str, str]:
    code = _non_empty_text(finding.get("code"), "").upper()
    if code.startswith("CHECK_"):
        return "LogicIRRepairAgent", "repair_candidate_logic_ir"
    if code.startswith("REQ_"):
        return "RequirementRepairAgent", "repair_structured_requirement_candidate"
    if code == "EV_SIMULATION_RESULT_FAILED" or "TEST_RESULT" in code:
        return "SimulationTestRepairAgent", "repair_candidate_test_oracle"
    return "EvidenceRepairAgent", "repair_evidence_trace"


def _finding_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[_severity(finding.get("severity"))] += 1
    return counts


def _collect_findings(agent_outputs: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for report_name in ("safety_guardian", "evidence", "requirements"):
        report = agent_outputs.get(report_name)
        if not isinstance(report, dict):
            continue
        for finding in report.get("findings", []):
            if isinstance(finding, dict):
                normalized = _normalize_finding(finding)
                normalized["source_report"] = report_name
                findings.append(normalized)
    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for finding in findings:
        deduped[(finding["source_report"], finding["code"])] = finding
    return sorted(deduped.values(), key=_finding_sort_key)


def _task_instructions(finding: dict[str, Any], target_agent: str) -> list[str]:
    return [
        f"Address {finding['code']} using {target_agent} responsibilities only.",
        "Repair only candidate IR/task/evidence generation around the referenced finding.",
        "Keep the output candidate-only and do not modify controller truth or UI layout files.",
    ]


def _task_done_when(finding: dict[str, Any]) -> list[str]:
    return [
        f"tests/test_agent_task_contract.py contains or preserves a focused regression for {finding['code']}.",
        "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_task_contract.py exits 0.",
        "The generated task package validates against agent_task_contract_v0_1.",
    ]


def _task_stop_if() -> list[str]:
    return [
        "Any diff touches controller truth files such as src/well_harness/controller.py.",
        "Any diff changes UI layout files under src/well_harness/static/requirements_intake/.",
        "Existing tests start failing; do not fix by weakening tests.",
    ]


def _build_task(finding: dict[str, Any], source_artifact_id: str) -> dict[str, Any]:
    target_agent, task_type = _task_route_for_finding(finding)
    return {
        "task_id": _task_id_for_finding(finding),
        "target_agent": target_agent,
        "task_type": task_type,
        "priority": _severity(finding.get("severity")),
        "status": "proposed",
        "input_artifacts": [
            source_artifact_id,
            f"finding:{finding['code']}",
        ],
        "allowed_files": list(ALLOWED_FILES),
        "forbidden_files": list(FORBIDDEN_FILES),
        "change_boundary": dict(CHANGE_BOUNDARY),
        "findings": [finding],
        "instructions": _task_instructions(finding, target_agent),
        "done_when": _task_done_when(finding),
        "stop_if": _task_stop_if(),
        "verification_commands": list(VERIFICATION_COMMANDS),
        "human_review_required": True,
    }


def validate_agent_task_package(package: dict[str, Any]) -> None:
    """Validate schema and hard no-controller-truth task boundaries."""
    _schema_validate(package)
    for task in package.get("tasks", []):
        if not isinstance(task, dict):
            continue
        boundary = task.get("change_boundary")
        if not isinstance(boundary, dict):
            raise AgentTaskContractError("task.change_boundary must be an object")
        if boundary.get("allowed_to_modify_controller_truth") is not False:
            raise AgentTaskContractError("agent task may not authorize controller truth modification")
        for key, expected in CHANGE_BOUNDARY.items():
            if boundary.get(key) != expected:
                raise AgentTaskContractError(f"task.change_boundary.{key} must be {expected!r}")
        forbidden_files = task.get("forbidden_files")
        if not isinstance(forbidden_files, list) or "src/well_harness/controller.py" not in forbidden_files:
            raise AgentTaskContractError("agent task must forbid controller truth files")


def build_chief_engineer_task_package(
    agent_outputs: dict[str, Any],
    *,
    source_artifact_id: str = DEFAULT_SOURCE_ARTIFACT_ID,
) -> dict[str, Any]:
    """Build a reviewable next-task package from Safety/Evidence findings."""
    artifact_id = _non_empty_text(source_artifact_id, DEFAULT_SOURCE_ARTIFACT_ID)
    findings = _collect_findings(agent_outputs)
    tasks = [_build_task(finding, artifact_id) for finding in findings]
    package = {
        "$schema": AGENT_TASK_CONTRACT_SCHEMA_ID,
        "kind": AGENT_TASK_PACKAGE_KIND,
        "chief_engineer": {
            "agent_name": "ChiefEngineerAgent",
            "source_artifact_id": artifact_id,
            "status": "tasks_ready_for_review" if tasks else "no_tasks_required",
            "finding_counts": _finding_counts(findings),
            "task_count": len(tasks),
        },
        "tasks": tasks,
    }
    validate_agent_task_package(package)
    return package

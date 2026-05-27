"""M3 Safety/Evidence deterministic finding value pack."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_repair_loop import (
    run_evidence_agent_repair_loop,
    run_safety_guardian_repair_loop,
)
from well_harness.agent_requirement_to_ir_demo import build_m2_candidate_agent_output
from well_harness.agent_review_packet import (
    build_candidate_review_packet,
    build_candidate_review_packet_export,
    validate_candidate_review_packet,
    validate_candidate_review_packet_export,
)
from well_harness.agent_task_contract import build_chief_engineer_task_package


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m3-safety-evidence-value-pack"
)
M3_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json"
)
M3_SCHEMA_NAME = "multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json"
M3_PACKAGE_NAME = "multi_agent_m3_safety_evidence_value_pack_v0_1.json"
M3_PACKAGE_ID = "multi-agent-m3-safety-evidence-value-pack-v0.1"
M3_KIND = "ai-fantui-multi-agent-m3-safety-evidence-value-pack"

SAFETY_PRIORITY_SLICE_ID = "m3-safety-priority-repair"
SAFETY_UNDEFINED_SIGNAL_SLICE_ID = "m3-safety-undefined-signal-repair"
EVIDENCE_FAILED_RESULT_SLICE_ID = "m3-evidence-simulation-result-failed-repair"
EVIDENCE_MISSING_RESULT_SLICE_ID = "m3-evidence-test-result-missing-repair"
M3_SLICE_ORDER = [
    SAFETY_PRIORITY_SLICE_ID,
    SAFETY_UNDEFINED_SIGNAL_SLICE_ID,
    EVIDENCE_FAILED_RESULT_SLICE_ID,
    EVIDENCE_MISSING_RESULT_SLICE_ID,
]
SAFETY_FINDING_CLASSES = [
    "CHECK_SAFETY_PRIORITY_001",
    "CHECK_UNDEFINED_SIGNAL_001",
]
EVIDENCE_FINDING_CLASSES = [
    "EV_SIMULATION_RESULT_FAILED",
    "EV_TEST_RESULT_MISSING",
]
HOT_START_SCENARIO_ID = "TC-HOT-START-ABORT-001"
MISSING_SIGNAL_NAME = "EGT_START_LIMIT"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M3_SCHEMA_NAME)


def validate_m3_safety_evidence_value_pack(package: dict[str, Any]) -> None:
    """Validate the M3 package schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(f"M3 Safety/Evidence value pack schema validation failed{location}: {exc.message}") from exc


def _approval(task_id: str, *, approval_id: str) -> dict[str, Any]:
    return {
        "approval_id": approval_id,
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-21T00:00:00Z",
    }


def _transition(packet: dict[str, Any], transition_id: str) -> dict[str, Any]:
    transitions = (
        packet.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
        .get("transitions", [])
    )
    if not isinstance(transitions, list):
        raise RuntimeError("candidate packet has no transitions array")
    for transition in transitions:
        if isinstance(transition, dict) and transition.get("id") == transition_id:
            return transition
    raise RuntimeError(f"candidate packet missing transition {transition_id}")


def _simulation_result(packet: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    results = packet.get("agent_output", {}).get("payload", {}).get("simulation_results", [])
    if not isinstance(results, list):
        raise RuntimeError("candidate packet has no simulation_results array")
    for result in results:
        if isinstance(result, dict) and result.get("scenario_id") == scenario_id:
            return result
    raise RuntimeError(f"candidate packet missing simulation result {scenario_id}")


def _safety_clean_packet() -> dict[str, Any]:
    packet = build_m2_candidate_agent_output()
    loop_result = run_safety_guardian_repair_loop(
        packet,
        approval=_approval(
            "TASK-CE-CHECK-SAFETY-PRIORITY-001",
            approval_id="APPROVAL-M3-BASELINE-SAFETY-CLEAN-001",
        ),
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(f"M3 baseline safety repair did not converge: {loop_result.get('status')}")
    return copy.deepcopy(loop_result["repaired_packet"])


def _safety_priority_candidate() -> dict[str, Any]:
    return build_m2_candidate_agent_output()


def _undefined_signal_candidate() -> dict[str, Any]:
    packet = _safety_clean_packet()
    signals = packet["agent_output"]["payload"]["signals"]
    packet["agent_output"]["payload"]["signals"] = [
        signal
        for signal in signals
        if not (isinstance(signal, dict) and signal.get("name") == MISSING_SIGNAL_NAME)
    ]
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [],
    }
    return packet


def _failed_simulation_result_candidate() -> dict[str, Any]:
    packet = _safety_clean_packet()
    _simulation_result(packet, HOT_START_SCENARIO_ID)["status"] = "fail"
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [],
    }
    return packet


def _missing_simulation_result_candidate() -> dict[str, Any]:
    packet = _safety_clean_packet()
    results = packet["agent_output"]["payload"]["simulation_results"]
    packet["agent_output"]["payload"]["simulation_results"] = [
        result
        for result in results
        if not (isinstance(result, dict) and result.get("scenario_id") == HOT_START_SCENARIO_ID)
    ]
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [],
    }
    return packet


def _finding_chain_statuses(review_packet: dict[str, Any]) -> list[str]:
    chains = review_packet.get("finding_chains", [])
    return [
        str(chain.get("status", ""))
        for chain in chains
        if isinstance(chain, dict)
    ]


def _slice_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "slice_id": str(payload["slice_id"]),
        "status": str(payload["status"]),
        "selected_task_id": str(payload["selected_task"]["task_id"]),
        "selected_task_agent": str(payload["selected_task"]["target_agent"]),
        "selected_finding_code": str(payload["selected_finding_code"]),
        "repair_loop_kind": str(payload["repair_loop_kind"]),
        "reviewer_status": str(payload["reviewer_status"]),
        "finding_chain_statuses": list(payload.get("finding_chain_statuses", [])),
        "convergence": dict(payload.get("convergence", {})),
        "artifact_paths": dict(payload.get("artifact_paths", {})),
    }


def _run_slice(
    *,
    slice_id: str,
    before_packet: dict[str, Any],
    artifact_dir: Path,
    source_artifact_id: str,
    approval_id: str,
    loop_kind: str,
) -> dict[str, Any]:
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id=source_artifact_id,
    )
    if not task_package["tasks"]:
        raise RuntimeError(f"{slice_id} requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(str(selected_task["task_id"]), approval_id=approval_id)
    if loop_kind == "safety":
        loop_result = run_safety_guardian_repair_loop(before_packet, approval=approval)
    elif loop_kind == "evidence":
        loop_result = run_evidence_agent_repair_loop(before_packet, approval=approval)
    else:
        raise RuntimeError(f"unknown M3 loop kind: {loop_kind}")
    if loop_result.get("status") != "converged":
        raise RuntimeError(f"{slice_id} did not converge: {loop_result.get('status')}")

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=slice_id,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    before_packet_path = artifact_dir / "candidate_packet_before.json"
    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    safety_report_path = artifact_dir / "safety_guardian_report.json"
    evidence_report_path = artifact_dir / "evidence_agent_report.json"
    task_package_path = artifact_dir / "chief_engineer_task_package.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    slice_summary_path = artifact_dir / "slice_summary.json"

    for path, payload in [
        (before_packet_path, before_packet),
        (repaired_packet_path, repaired_packet),
        (safety_report_path, safety_report),
        (evidence_report_path, evidence_report),
        (task_package_path, task_package),
        (loop_result_path, loop_result),
        (review_packet_path, review_packet),
        (review_export_path, review_export),
    ]:
        _write_json(path, payload)

    payload = {
        "status": "pass",
        "slice_id": slice_id,
        "selected_finding_code": str(loop_result["selected_finding"]["code"]),
        "repair_loop_kind": str(loop_result["kind"]),
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "candidate_packet_before": str(before_packet_path),
            "repaired_candidate_packet": str(repaired_packet_path),
            "safety_guardian_report": str(safety_report_path),
            "evidence_agent_report": str(evidence_report_path),
            "task_package": str(task_package_path),
            "repair_loop_result": str(loop_result_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "slice_summary": str(slice_summary_path),
        },
    }
    _write_json(slice_summary_path, payload)
    return payload


def run_m3_safety_evidence_value_pack(
    *,
    artifact_dir: Path = DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Run four deterministic Safety/Evidence repair loops and emit one package."""
    safety_priority = _run_slice(
        slice_id=SAFETY_PRIORITY_SLICE_ID,
        before_packet=_safety_priority_candidate(),
        artifact_dir=artifact_dir / "safety-priority",
        source_artifact_id="M3_SAFETY_PRIORITY_REPAIR_v0.1",
        approval_id="APPROVAL-M3-SAFETY-PRIORITY-001",
        loop_kind="safety",
    )
    safety_undefined_signal = _run_slice(
        slice_id=SAFETY_UNDEFINED_SIGNAL_SLICE_ID,
        before_packet=_undefined_signal_candidate(),
        artifact_dir=artifact_dir / "safety-undefined-signal",
        source_artifact_id="M3_SAFETY_UNDEFINED_SIGNAL_REPAIR_v0.1",
        approval_id="APPROVAL-M3-SAFETY-UNDEFINED-SIGNAL-001",
        loop_kind="safety",
    )
    evidence_failed_result = _run_slice(
        slice_id=EVIDENCE_FAILED_RESULT_SLICE_ID,
        before_packet=_failed_simulation_result_candidate(),
        artifact_dir=artifact_dir / "evidence-failed-result",
        source_artifact_id="M3_EVIDENCE_FAILED_RESULT_REPAIR_v0.1",
        approval_id="APPROVAL-M3-EVIDENCE-FAILED-RESULT-001",
        loop_kind="evidence",
    )
    evidence_missing_result = _run_slice(
        slice_id=EVIDENCE_MISSING_RESULT_SLICE_ID,
        before_packet=_missing_simulation_result_candidate(),
        artifact_dir=artifact_dir / "evidence-missing-result",
        source_artifact_id="M3_EVIDENCE_MISSING_RESULT_REPAIR_v0.1",
        approval_id="APPROVAL-M3-EVIDENCE-MISSING-RESULT-001",
        loop_kind="evidence",
    )
    slice_payloads = [
        safety_priority,
        safety_undefined_signal,
        evidence_failed_result,
        evidence_missing_result,
    ]
    slices = [_slice_summary(payload) for payload in slice_payloads]
    open_findings: list[str] = []
    for item in slices:
        for finding in item["convergence"].get("after_findings", []):
            if isinstance(finding, str) and finding not in open_findings:
                open_findings.append(finding)

    passed_count = sum(1 for item in slices if item["status"] == "pass")
    converged_count = sum(1 for item in slices if item["reviewer_status"] == "converged")
    controller_truth_modified = any(
        item["convergence"].get("controller_truth_modified") is not False
        for item in slices
    )
    ui_layout_modified = any(
        item["convergence"].get("ui_layout_modified") is not False
        for item in slices
    )
    package_status = (
        "pass"
        if (
            passed_count == len(slices)
            and converged_count == len(slices)
            and not open_findings
            and not controller_truth_modified
            and not ui_layout_modified
        )
        else "fail"
    )
    gates = {
        "safety_priority_slice": "pass" if safety_priority.get("status") == "pass" else "fail",
        "safety_undefined_signal_slice": (
            "pass" if safety_undefined_signal.get("status") == "pass" else "fail"
        ),
        "evidence_failed_result_slice": (
            "pass" if evidence_failed_result.get("status") == "pass" else "fail"
        ),
        "evidence_missing_result_slice": (
            "pass" if evidence_missing_result.get("status") == "pass" else "fail"
        ),
        "review_packet_exports": "pass" if converged_count == len(slices) else "fail",
        "local_gate": package_status,
    }
    package_path = artifact_dir / M3_PACKAGE_NAME
    package = {
        "$schema": M3_SCHEMA_ID,
        "kind": M3_KIND,
        "package_id": M3_PACKAGE_ID,
        "status": package_status,
        "milestone": {
            "id": "M3",
            "name": "Safety/Evidence 工程价值增强包",
            "budget": 48,
            "effort_unit": "施工队工时",
            "claim": "candidate-only deterministic finding value pack",
        },
        "finding_classes": {
            "safety": list(SAFETY_FINDING_CLASSES),
            "evidence": list(EVIDENCE_FINDING_CLASSES),
        },
        "slice_order": list(M3_SLICE_ORDER),
        "slices": slices,
        "review_exports": {
            "count": len(slices),
            "reviewer_statuses": [str(item["reviewer_status"]) for item in slices],
            "finding_chain_statuses": [
                list(item.get("finding_chain_statuses", [])) for item in slices
            ],
            "export_ids": [str(item["slice_id"]) for item in slices],
        },
        "deterministic_gates": gates,
        "aggregate": {
            "slice_count": len(slices),
            "passed": passed_count,
            "converged": converged_count,
            "open_findings": open_findings,
            "controller_truth_modified": controller_truth_modified,
            "ui_layout_modified": ui_layout_modified,
        },
        "artifact_paths": {
            "package": str(package_path),
            "safety_priority_summary": str(
                artifact_dir / "safety-priority" / "slice_summary.json"
            ),
            "safety_undefined_signal_summary": str(
                artifact_dir / "safety-undefined-signal" / "slice_summary.json"
            ),
            "evidence_failed_result_summary": str(
                artifact_dir / "evidence-failed-result" / "slice_summary.json"
            ),
            "evidence_missing_result_summary": str(
                artifact_dir / "evidence-missing-result" / "slice_summary.json"
            ),
        },
    }
    validate_m3_safety_evidence_value_pack(package)
    _write_json(package_path, package)
    return copy.deepcopy(package)

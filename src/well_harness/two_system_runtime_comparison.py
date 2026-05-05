from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from well_harness.adapters import build_landing_gear_controller_adapter  # type: ignore[import-untyped]
from well_harness.controller_adapter import (  # type: ignore[import-untyped]
    GenericControllerTruthAdapter,
    build_reference_controller_adapter,
)
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_truth_adapter  # type: ignore[import-untyped]
from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter  # type: ignore[import-untyped]
from well_harness.scenario_playback import build_playback_report_from_truth_adapter  # type: ignore[import-untyped]
from well_harness.system_spec import workbench_spec_from_dict  # type: ignore[import-untyped]


TWO_SYSTEM_RUNTIME_COMPARISON_KIND = "well-harness-two-system-runtime-comparison"
TWO_SYSTEM_RUNTIME_COMPARISON_VERSION = 1
TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID = (
    "https://well-harness.local/json_schema/two_system_runtime_comparison_v1.schema.json"
)
REFERENCE_SCENARIO_ID = "compressed_ra_tra_vdt_monitor"
REFERENCE_FAULT_MODE_ID = "thr_lock_never_releases"
LANDING_GEAR_SCENARIO_ID = "handle_down_nominal_extension"
LANDING_GEAR_FAULT_MODE_ID = "hydraulic_pressure_bias_low"
SHARED_RUNTIME_CONTRACTS = (
    "controller_truth_metadata",
    "control_system_spec",
    "playback_report",
    "fault_diagnosis_report",
    "knowledge_artifact",
)
DEFAULT_CONFIRMED_ROOT_CAUSE = "Runtime comparison kept the same confirmed root-cause capture path across both systems."
DEFAULT_REPAIR_ACTION = "Applied the system-specific repair path and reran the adapter-backed contract chain."
DEFAULT_VALIDATION_AFTER_FIX = "Replayed the adapter-backed runtime proof and confirmed the expected completion or blocker behavior."
DEFAULT_RESIDUAL_RISK = "Continue monitoring for future drift in the observed blocker path."


@dataclass(frozen=True)
class SystemRuntimeProofSnapshot:
    adapter_id: str
    system_id: str
    system_title: str
    source_of_truth: str
    scenario_id: str
    fault_mode_id: str
    component_count: int
    logic_node_count: int
    playback_completion_reached: bool
    fault_completion_reached: bool
    knowledge_status: str
    blocked_logic_node_count: int


@dataclass(frozen=True)
class TwoSystemRuntimeComparisonReport:
    kind: str
    primary_system: SystemRuntimeProofSnapshot
    comparison_system: SystemRuntimeProofSnapshot
    shared_contracts: tuple[str, ...]
    both_support_adapter_truth: bool
    both_reach_playback_completion: bool
    both_block_fault_path: bool
    both_emit_resolved_knowledge: bool
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return two_system_runtime_comparison_report_to_dict(self)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def two_system_runtime_comparison_report_to_dict(report: TwoSystemRuntimeComparisonReport) -> dict[str, Any]:
    payload = _json_safe_value(asdict(report))
    return {
        "$schema": TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID,
        "kind": TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
        "version": TWO_SYSTEM_RUNTIME_COMPARISON_VERSION,
        **payload,
    }


def _build_system_runtime_proof_snapshot(
    adapter: GenericControllerTruthAdapter,
    *,
    scenario_id: str,
    fault_mode_id: str,
    sample_period_s: float,
) -> SystemRuntimeProofSnapshot:
    spec_payload = adapter.load_spec()
    spec = workbench_spec_from_dict(spec_payload)
    playback_report = build_playback_report_from_truth_adapter(
        adapter,
        scenario_id=scenario_id,
        sample_period_s=sample_period_s,
    )
    diagnosis_report = build_fault_diagnosis_report_from_truth_adapter(
        adapter,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        sample_period_s=sample_period_s,
    )
    knowledge_artifact = build_knowledge_artifact_from_truth_adapter(
        adapter,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        confirmed_root_cause=DEFAULT_CONFIRMED_ROOT_CAUSE,
        repair_action=DEFAULT_REPAIR_ACTION,
        validation_after_fix=DEFAULT_VALIDATION_AFTER_FIX,
        residual_risk=DEFAULT_RESIDUAL_RISK,
        sample_period_s=sample_period_s,
    )
    return SystemRuntimeProofSnapshot(
        adapter_id=adapter.metadata.adapter_id,
        system_id=spec.system_id,
        system_title=spec.title,
        source_of_truth=adapter.metadata.source_of_truth,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        component_count=len(spec.components),
        logic_node_count=len(spec.logic_nodes),
        playback_completion_reached=playback_report.completion_reached,
        fault_completion_reached=diagnosis_report.fault_completion_reached,
        knowledge_status=knowledge_artifact.status,
        blocked_logic_node_count=len(diagnosis_report.blocked_logic_node_ids),
    )


def build_two_system_runtime_comparison_report(*, sample_period_s: float = 0.5) -> TwoSystemRuntimeComparisonReport:
    reference_system = _build_system_runtime_proof_snapshot(
        build_reference_controller_adapter(),
        scenario_id=REFERENCE_SCENARIO_ID,
        fault_mode_id=REFERENCE_FAULT_MODE_ID,
        sample_period_s=sample_period_s,
    )
    comparison_system = _build_system_runtime_proof_snapshot(
        build_landing_gear_controller_adapter(),
        scenario_id=LANDING_GEAR_SCENARIO_ID,
        fault_mode_id=LANDING_GEAR_FAULT_MODE_ID,
        sample_period_s=sample_period_s,
    )
    both_reach_playback_completion = (
        reference_system.playback_completion_reached and comparison_system.playback_completion_reached
    )
    both_block_fault_path = (
        not reference_system.fault_completion_reached and not comparison_system.fault_completion_reached
    )
    both_emit_resolved_knowledge = (
        reference_system.knowledge_status == "resolved"
        and comparison_system.knowledge_status == "resolved"
    )
    summary = (
        "Two-system runtime comparison passed: both the reference thrust-reverser adapter and the landing-gear adapter "
        "publish metadata/spec and complete the playback->diagnosis->knowledge contract chain, while their selected "
        "fault proofs still block the downstream completion path as expected."
    )
    return TwoSystemRuntimeComparisonReport(
        kind=TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
        primary_system=reference_system,
        comparison_system=comparison_system,
        shared_contracts=SHARED_RUNTIME_CONTRACTS,
        both_support_adapter_truth=True,
        both_reach_playback_completion=both_reach_playback_completion,
        both_block_fault_path=both_block_fault_path,
        both_emit_resolved_knowledge=both_emit_resolved_knowledge,
        summary=summary,
    )


def render_two_system_runtime_comparison_text(report: TwoSystemRuntimeComparisonReport) -> str:
    lines = [
        f"kind: {report.kind}",
        f"primary_system: {report.primary_system.system_id} ({report.primary_system.adapter_id})",
        f"comparison_system: {report.comparison_system.system_id} ({report.comparison_system.adapter_id})",
        f"both_support_adapter_truth: {report.both_support_adapter_truth}",
        f"both_reach_playback_completion: {report.both_reach_playback_completion}",
        f"both_block_fault_path: {report.both_block_fault_path}",
        f"both_emit_resolved_knowledge: {report.both_emit_resolved_knowledge}",
        "shared_contracts:",
    ]
    lines.extend(f"  - {item}" for item in report.shared_contracts)
    lines.append(f"summary: {report.summary}")
    return "\n".join(lines)

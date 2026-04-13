from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from well_harness.adapters import LANDING_GEAR_CONTROLLER_METADATA, build_landing_gear_controller_adapter
from well_harness.controller_adapter import GenericControllerTruthAdapter
from well_harness.document_intake import load_intake_packet
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_truth_adapter
from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter
from well_harness.scenario_playback import ScenarioPlaybackReport, build_playback_report_from_truth_adapter
from well_harness.system_spec import AcceptanceScenarioSpec, ComponentSpec, workbench_spec_from_dict
from well_harness.workbench_bundle import build_workbench_bundle


SECOND_SYSTEM_SMOKE_KIND = "well-harness-second-system-smoke"
SECOND_SYSTEM_SMOKE_VERSION = 1
SECOND_SYSTEM_SMOKE_SCHEMA_ID = "https://well-harness.local/json_schema/second_system_smoke_v1.schema.json"
TRUTH_ADAPTER_PROOF_MODE = "truth_adapter"
INTAKE_PACKET_PROOF_MODE = "intake_packet"
ADAPTER_RUNTIME_PROOF_KIND = "adapter_runtime_proof"
DEFAULT_SECOND_SYSTEM_PACKET_PATH = Path(__file__).with_name("reference_packets") / "custom_reverse_control_v1.json"
DEFAULT_SECOND_SYSTEM_PROOF_MODE = TRUTH_ADAPTER_PROOF_MODE
DEFAULT_SECOND_SYSTEM_ADAPTER_ID = LANDING_GEAR_CONTROLLER_METADATA.adapter_id
DEFAULT_CONFIRMED_ROOT_CAUSE = "Pressure sensor bias was confirmed against the mixed-doc acceptance evidence."
DEFAULT_REPAIR_ACTION = "Recalibrated the pressure sensing path and revalidated the deployment threshold."
DEFAULT_VALIDATION_AFTER_FIX = "Replayed the second-system acceptance scenario and confirmed the monitored command path completed."
DEFAULT_RESIDUAL_RISK = "Continue watching for future hydraulic pressure drift under maintenance review."


@dataclass(frozen=True)
class SecondSystemSmokeReport:
    kind: str
    proof_mode: str
    adapter_id: str | None
    system_id: str
    system_title: str
    packet_path: str | None
    source_of_truth: str
    spec_schema_id: str | None
    bundle_kind: str
    ready_for_spec_build: bool
    selected_scenario_id: str | None
    selected_fault_mode_id: str | None
    playback_completion_reached: bool
    fault_completion_reached: bool
    knowledge_status: str | None
    smoke_passed: bool
    evidence_steps: tuple[str, ...]
    next_actions: tuple[str, ...]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return second_system_smoke_report_to_dict(self)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def second_system_smoke_report_to_dict(report: SecondSystemSmokeReport) -> dict[str, Any]:
    payload = _json_safe_value(asdict(report))
    return {
        "$schema": SECOND_SYSTEM_SMOKE_SCHEMA_ID,
        "kind": SECOND_SYSTEM_SMOKE_KIND,
        "version": SECOND_SYSTEM_SMOKE_VERSION,
        **payload,
    }


def _resolve_selected_id(
    requested_id: str | None,
    candidates: tuple[Any, ...],
    label: str,
    *,
    preferred_ids: tuple[str, ...] = (),
) -> str:
    candidate_ids = tuple(item.id for item in candidates)
    if not candidate_ids:
        raise ValueError(f"no {label} candidates are available")
    if requested_id is not None:
        if requested_id not in candidate_ids:
            raise ValueError(f"unknown {label}: {requested_id}")
        return requested_id
    for preferred_id in preferred_ids:
        if preferred_id in candidate_ids:
            return preferred_id
    if len(candidate_ids) == 1:
        return candidate_ids[0]
    raise ValueError(
        f"{label} is required because multiple {label}s are available: {', '.join(candidate_ids)}"
    )


def _scenario_by_id(scenarios: tuple[AcceptanceScenarioSpec, ...], scenario_id: str) -> AcceptanceScenarioSpec:
    for scenario in scenarios:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"unknown scenario: {scenario_id}")


def _component_value_for_snapshot(component: ComponentSpec, value: Any) -> Any:
    if component.state_shape == "binary":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value >= 0.5)
    if component.state_shape == "analog":
        if isinstance(value, bool):
            raise TypeError(f"component {component.id!r} expected a numeric value")
        if isinstance(value, (int, float)):
            return float(value)
    if component.state_shape == "discrete":
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)) and component.allowed_states:
            index = max(0, min(int(round(float(value))), len(component.allowed_states) - 1))
            return component.allowed_states[index]
    return value


def _final_snapshot_from_playback(
    report: ScenarioPlaybackReport,
    *,
    scenario: AcceptanceScenarioSpec,
    components: dict[str, ComponentSpec],
) -> dict[str, Any]:
    snapshot = {
        steady_signal.signal_id: _component_value_for_snapshot(
            components[steady_signal.signal_id],
            steady_signal.value,
        )
        for steady_signal in scenario.steady_signals
        if steady_signal.signal_id in components
    }
    for series in report.signal_series:
        if not series.points or series.id not in components:
            continue
        snapshot[series.id] = _component_value_for_snapshot(components[series.id], series.points[-1].value)
    return snapshot


def _truth_adapter_from_id(adapter_id: str) -> GenericControllerTruthAdapter:
    if adapter_id == DEFAULT_SECOND_SYSTEM_ADAPTER_ID:
        return build_landing_gear_controller_adapter()
    raise ValueError(f"unsupported second-system truth adapter: {adapter_id}")


def _build_truth_adapter_smoke_report(
    *,
    adapter_id: str,
    scenario_id: str | None = None,
    fault_mode_id: str | None = None,
    sample_period_s: float = 0.5,
) -> SecondSystemSmokeReport:
    adapter = _truth_adapter_from_id(adapter_id)
    spec_payload = adapter.load_spec()
    spec = workbench_spec_from_dict(spec_payload)
    selected_scenario_id = _resolve_selected_id(scenario_id, spec.acceptance_scenarios, "scenario")
    selected_fault_mode_id = _resolve_selected_id(
        fault_mode_id,
        spec.fault_modes,
        "fault mode",
        preferred_ids=("hydraulic_pressure_bias_low", "pressure_sensor_bias_low"),
    )
    scenario = _scenario_by_id(spec.acceptance_scenarios, selected_scenario_id)
    components = {component.id: component for component in spec.components}

    playback_report = build_playback_report_from_truth_adapter(
        adapter,
        scenario_id=selected_scenario_id,
        sample_period_s=sample_period_s,
    )
    baseline_runtime = adapter.evaluate_snapshot(
        _final_snapshot_from_playback(
            playback_report,
            scenario=scenario,
            components=components,
        )
    )
    diagnosis_report = build_fault_diagnosis_report_from_truth_adapter(
        adapter,
        scenario_id=selected_scenario_id,
        fault_mode_id=selected_fault_mode_id,
        sample_period_s=sample_period_s,
    )
    fault_runtime = adapter.evaluate_snapshot(
        _final_snapshot_from_playback(
            diagnosis_report.fault_report,
            scenario=scenario,
            components=components,
        )
    )
    knowledge_artifact = build_knowledge_artifact_from_truth_adapter(
        adapter,
        scenario_id=selected_scenario_id,
        fault_mode_id=selected_fault_mode_id,
        confirmed_root_cause=DEFAULT_CONFIRMED_ROOT_CAUSE,
        repair_action=DEFAULT_REPAIR_ACTION,
        validation_after_fix=DEFAULT_VALIDATION_AFTER_FIX,
        residual_risk=DEFAULT_RESIDUAL_RISK,
        sample_period_s=sample_period_s,
    )
    smoke_passed = all(
        (
            playback_report.completion_reached,
            baseline_runtime.completion_reached,
            not diagnosis_report.fault_completion_reached,
            not fault_runtime.completion_reached,
            knowledge_artifact.status == "resolved",
        )
    )
    evidence_steps = (
        "adapter_metadata",
        "control_system_spec",
        "runtime_truth_alignment",
        "playback_report",
        "fault_diagnosis_report",
        "knowledge_artifact",
    )
    summary = (
        f"Second-system smoke {'passed' if smoke_passed else 'failed'} for {knowledge_artifact.system_id}: "
        f"proof_mode={TRUTH_ADAPTER_PROOF_MODE}, adapter={adapter.metadata.adapter_id}, "
        f"scenario={selected_scenario_id}, fault_mode={selected_fault_mode_id}."
    )
    return SecondSystemSmokeReport(
        kind=SECOND_SYSTEM_SMOKE_KIND,
        proof_mode=TRUTH_ADAPTER_PROOF_MODE,
        adapter_id=adapter.metadata.adapter_id,
        system_id=knowledge_artifact.system_id,
        system_title=knowledge_artifact.system_title,
        packet_path=None,
        source_of_truth=adapter.metadata.source_of_truth,
        spec_schema_id=spec_payload.get("$schema") if isinstance(spec_payload, dict) else None,
        bundle_kind=ADAPTER_RUNTIME_PROOF_KIND,
        ready_for_spec_build=True,
        selected_scenario_id=selected_scenario_id,
        selected_fault_mode_id=selected_fault_mode_id,
        playback_completion_reached=playback_report.completion_reached and baseline_runtime.completion_reached,
        fault_completion_reached=diagnosis_report.fault_completion_reached or fault_runtime.completion_reached,
        knowledge_status=knowledge_artifact.status,
        smoke_passed=smoke_passed,
        evidence_steps=evidence_steps,
        next_actions=(
            "Connect this adapter-backed runtime proof to comparison or bundle-level second-system reporting.",
        ),
        summary=summary,
    )


def _build_intake_packet_smoke_report(
    *,
    packet_path: str | Path | None = None,
    scenario_id: str | None = None,
    fault_mode_id: str | None = None,
    sample_period_s: float = 0.5,
) -> SecondSystemSmokeReport:
    resolved_packet_path = Path(packet_path or DEFAULT_SECOND_SYSTEM_PACKET_PATH).expanduser().resolve()
    packet = load_intake_packet(resolved_packet_path)
    bundle = build_workbench_bundle(
        packet,
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        confirmed_root_cause=DEFAULT_CONFIRMED_ROOT_CAUSE,
        repair_action=DEFAULT_REPAIR_ACTION,
        validation_after_fix=DEFAULT_VALIDATION_AFTER_FIX,
        residual_risk=DEFAULT_RESIDUAL_RISK,
        sample_period_s=sample_period_s,
    )
    generated_spec = bundle.intake_assessment.get("generated_workbench_spec")
    spec_schema_id = generated_spec.get("$schema") if isinstance(generated_spec, dict) else None
    playback_completion_reached = bool(
        bundle.playback_report is not None and bundle.playback_report.completion_reached
    )
    fault_completion_reached = bool(
        bundle.fault_diagnosis_report is not None and bundle.fault_diagnosis_report.fault_completion_reached
    )
    knowledge_status = bundle.knowledge_artifact.status if bundle.knowledge_artifact is not None else None
    smoke_passed = all(
        (
            bundle.ready_for_spec_build,
            bundle.clarification_brief is not None,
            bundle.playback_report is not None,
            bundle.fault_diagnosis_report is not None,
            bundle.knowledge_artifact is not None,
            playback_completion_reached,
            not fault_completion_reached,
            knowledge_status == "resolved",
        )
    )
    evidence_steps = tuple(
        step
        for step, present in (
            ("intake_assessment", True),
            ("clarification_brief", bundle.clarification_brief is not None),
            ("playback_report", bundle.playback_report is not None),
            ("fault_diagnosis_report", bundle.fault_diagnosis_report is not None),
            ("knowledge_artifact", bundle.knowledge_artifact is not None),
        )
        if present
    )
    summary = (
        f"Second-system smoke {'passed' if smoke_passed else 'failed'} for {bundle.system_id}: "
        f"proof_mode={INTAKE_PACKET_PROOF_MODE}, bundle={bundle.bundle_kind}, scenario={bundle.selected_scenario_id or 'none'}, "
        f"fault_mode={bundle.selected_fault_mode_id or 'none'}."
    )
    return SecondSystemSmokeReport(
        kind=SECOND_SYSTEM_SMOKE_KIND,
        proof_mode=INTAKE_PACKET_PROOF_MODE,
        adapter_id=None,
        system_id=bundle.system_id,
        system_title=bundle.system_title,
        packet_path=str(resolved_packet_path),
        source_of_truth=packet.source_of_truth,
        spec_schema_id=spec_schema_id,
        bundle_kind=bundle.bundle_kind,
        ready_for_spec_build=bundle.ready_for_spec_build,
        selected_scenario_id=bundle.selected_scenario_id,
        selected_fault_mode_id=bundle.selected_fault_mode_id,
        playback_completion_reached=playback_completion_reached,
        fault_completion_reached=fault_completion_reached,
        knowledge_status=knowledge_status,
        smoke_passed=smoke_passed,
        evidence_steps=evidence_steps,
        next_actions=bundle.next_actions,
        summary=summary,
    )


def build_second_system_smoke_report(
    *,
    packet_path: str | Path | None = None,
    scenario_id: str | None = None,
    fault_mode_id: str | None = None,
    sample_period_s: float = 0.5,
    proof_mode: str | None = None,
    adapter_id: str | None = None,
) -> SecondSystemSmokeReport:
    resolved_proof_mode = (proof_mode or (INTAKE_PACKET_PROOF_MODE if packet_path else DEFAULT_SECOND_SYSTEM_PROOF_MODE))
    normalized_proof_mode = resolved_proof_mode.replace("-", "_")
    if normalized_proof_mode == TRUTH_ADAPTER_PROOF_MODE:
        return _build_truth_adapter_smoke_report(
            adapter_id=adapter_id or DEFAULT_SECOND_SYSTEM_ADAPTER_ID,
            scenario_id=scenario_id,
            fault_mode_id=fault_mode_id,
            sample_period_s=sample_period_s,
        )
    if normalized_proof_mode == INTAKE_PACKET_PROOF_MODE:
        return _build_intake_packet_smoke_report(
            packet_path=packet_path,
            scenario_id=scenario_id,
            fault_mode_id=fault_mode_id,
            sample_period_s=sample_period_s,
        )
    raise ValueError(f"unsupported second-system proof mode: {proof_mode}")


def render_second_system_smoke_text(report: SecondSystemSmokeReport) -> str:
    lines = [
        f"kind: {report.kind}",
        f"proof_mode: {report.proof_mode}",
        f"adapter_id: {report.adapter_id or '(none)'}",
        f"system: {report.system_id} - {report.system_title}",
        f"packet_path: {report.packet_path or '(none)'}",
        f"source_of_truth: {report.source_of_truth}",
        f"spec_schema_id: {report.spec_schema_id or '(none)'}",
        f"bundle_kind: {report.bundle_kind}",
        f"ready_for_spec_build: {report.ready_for_spec_build}",
        f"selected_scenario_id: {report.selected_scenario_id or '(none)'}",
        f"selected_fault_mode_id: {report.selected_fault_mode_id or '(none)'}",
        f"playback_completion_reached: {report.playback_completion_reached}",
        f"fault_completion_reached: {report.fault_completion_reached}",
        f"knowledge_status: {report.knowledge_status or '(none)'}",
        f"smoke_passed: {report.smoke_passed}",
        "evidence_steps:",
    ]
    lines.extend(f"  - {step}" for step in report.evidence_steps)
    lines.append("next_actions:")
    lines.extend(f"  - {step}" for step in report.next_actions)
    lines.append(f"summary: {report.summary}")
    return "\n".join(lines)

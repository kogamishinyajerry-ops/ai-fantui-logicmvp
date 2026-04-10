from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from well_harness.document_intake import ControlSystemIntakePacket, intake_packet_to_workbench_spec
from well_harness.scenario_playback import PlaybackSeries, ScenarioPlaybackReport, build_scenario_playback_report
from well_harness.system_spec import ComponentSpec, ControlSystemWorkbenchSpec, FaultModeSpec


@dataclass(frozen=True)
class ScopeObservation:
    id: str
    label: str
    kind: str
    baseline_end: float | None
    fault_end: float | None
    status: str
    note: str


@dataclass(frozen=True)
class FaultDiagnosisReport:
    system_id: str
    system_title: str
    scenario_id: str
    scenario_label: str
    fault_mode_id: str
    fault_kind: str
    target_component_id: str
    symptom: str
    baseline_completion_reached: bool
    fault_completion_reached: bool
    affected_signal_ids: tuple[str, ...]
    blocked_logic_node_ids: tuple[str, ...]
    suspected_root_cause: str
    reasoning_steps: tuple[str, ...]
    expected_sections: tuple[str, ...]
    scope_observations: tuple[ScopeObservation, ...]
    optimization_suggestion: str
    assumptions: tuple[str, ...]
    baseline_report: ScenarioPlaybackReport
    fault_report: ScenarioPlaybackReport

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _inactive_value(component: ComponentSpec) -> float:
    if component.allowed_range is not None:
        lower, upper = component.allowed_range
        if lower <= 0.0 <= upper:
            return 0.0
        return float(lower)
    if component.allowed_states:
        if "0" in component.allowed_states:
            return 0.0
        return float(component.allowed_states[0])
    return 0.0


def _active_value(component: ComponentSpec) -> float:
    if component.allowed_range is not None:
        _lower, upper = component.allowed_range
        return float(upper)
    if component.allowed_states:
        if "1" in component.allowed_states:
            return 1.0
        return float(component.allowed_states[-1])
    return 1.0


def _fault_mode_by_id(spec: ControlSystemWorkbenchSpec, fault_mode_id: str) -> FaultModeSpec:
    for fault_mode in spec.fault_modes:
        if fault_mode.id == fault_mode_id:
            return fault_mode
    raise ValueError(f"unknown fault mode: {fault_mode_id}")


def _series_by_id(report: ScenarioPlaybackReport) -> dict[str, PlaybackSeries]:
    return {series.id: series for series in (*report.signal_series, *report.logic_series)}


def _fault_override(
    component: ComponentSpec,
    fault_mode: FaultModeSpec,
) -> tuple[Callable[[float, float, ComponentSpec], float], str]:
    span = None
    if component.allowed_range is not None:
        lower, upper = component.allowed_range
        span = float(upper) - float(lower)

    if fault_mode.fault_kind == "bias_low":
        if span is not None and span > 0:
            shift = max(span * 0.25, 1.0)
            return (
                lambda _time_s, baseline_value, active_component: max(_inactive_value(active_component), baseline_value - shift),
                f"{fault_mode.target_component_id} uses a generic bias_low profile of -25% span.",
            )
        return (
            lambda _time_s, _baseline_value, active_component: _inactive_value(active_component),
            f"{fault_mode.target_component_id} falls back to its inactive value because no analog span is defined for bias_low.",
        )
    if fault_mode.fault_kind == "bias_high":
        if span is not None and span > 0:
            shift = max(span * 0.25, 1.0)
            return (
                lambda _time_s, baseline_value, active_component: min(_active_value(active_component), baseline_value + shift),
                f"{fault_mode.target_component_id} uses a generic bias_high profile of +25% span.",
            )
        return (
            lambda _time_s, _baseline_value, active_component: _active_value(active_component),
            f"{fault_mode.target_component_id} falls back to its active value because no analog span is defined for bias_high.",
        )
    if fault_mode.fault_kind in {"stuck_low", "open_circuit", "command_path_failure"}:
        return (
            lambda _time_s, _baseline_value, active_component: _inactive_value(active_component),
            f"{fault_mode.target_component_id} is forced to its inactive value for {fault_mode.fault_kind}.",
        )
    if fault_mode.fault_kind in {"stuck_high", "short_to_power"}:
        return (
            lambda _time_s, _baseline_value, active_component: _active_value(active_component),
            f"{fault_mode.target_component_id} is forced to its active value for {fault_mode.fault_kind}.",
        )
    if fault_mode.fault_kind == "latched_no_unlock":
        if span is not None and span > 0:
            margin = max(span * 0.01, 1.0)
            return (
                lambda _time_s, _baseline_value, active_component: max(
                    _inactive_value(active_component),
                    _active_value(active_component) - margin,
                ),
                f"{fault_mode.target_component_id} is held just below its unlock threshold.",
            )
        return (
            lambda _time_s, _baseline_value, active_component: _inactive_value(active_component),
            f"{fault_mode.target_component_id} falls back to its inactive value because no analog unlock span is defined.",
        )
    raise ValueError(
        f"fault kind {fault_mode.fault_kind!r} is not yet supported; clarify the injection semantics before replaying diagnostics."
    )


def _scope_observation(
    scope_id: str,
    *,
    spec: ControlSystemWorkbenchSpec,
    baseline_series: dict[str, PlaybackSeries],
    fault_series: dict[str, PlaybackSeries],
) -> ScopeObservation:
    component_labels = {component.id: component.label for component in spec.components}
    logic_labels = {logic_node.id: logic_node.label for logic_node in spec.logic_nodes}
    baseline = baseline_series.get(scope_id)
    fault = fault_series.get(scope_id)
    if baseline is None or fault is None:
        return ScopeObservation(
            id=scope_id,
            label=component_labels.get(scope_id, logic_labels.get(scope_id, scope_id)),
            kind="missing",
            baseline_end=None,
            fault_end=None,
            status="not_sampled",
            note="This scope item is not part of the sampled playback output for the chosen scenario.",
        )
    baseline_end = baseline.points[-1].value
    fault_end = fault.points[-1].value
    status = "diverged" if baseline_end != fault_end else "unchanged"
    return ScopeObservation(
        id=scope_id,
        label=baseline.label,
        kind=baseline.kind,
        baseline_end=baseline_end,
        fault_end=fault_end,
        status=status,
        note=(
            f"{scope_id} ends at {baseline_end:g} in baseline and {fault_end:g} under the injected fault."
            if status == "diverged"
            else f"{scope_id} ends at {baseline_end:g} in both baseline and faulted playback."
        ),
    )


def build_fault_diagnosis_report(
    spec: ControlSystemWorkbenchSpec,
    *,
    scenario_id: str,
    fault_mode_id: str,
    sample_period_s: float = 0.5,
) -> FaultDiagnosisReport:
    fault_mode = _fault_mode_by_id(spec, fault_mode_id)
    component_map = {component.id: component for component in spec.components}
    if fault_mode.target_component_id not in component_map:
        raise ValueError(f"fault target {fault_mode.target_component_id!r} not found in spec components")

    baseline_report = build_scenario_playback_report(
        spec,
        scenario_id=scenario_id,
        sample_period_s=sample_period_s,
    )
    override, assumption = _fault_override(component_map[fault_mode.target_component_id], fault_mode)
    fault_report = build_scenario_playback_report(
        spec,
        scenario_id=scenario_id,
        sample_period_s=sample_period_s,
        component_value_overrides={fault_mode.target_component_id: override},
    )

    baseline_series = _series_by_id(baseline_report)
    fault_series = _series_by_id(fault_report)
    affected_signal_ids = tuple(
        series.id
        for series in baseline_report.signal_series
        if baseline_series[series.id].points != fault_series[series.id].points
    )
    blocked_logic_node_ids = tuple(
        series.id
        for series in baseline_report.logic_series
        if max(point.value for point in baseline_series[series.id].points) > 0.0
        and max(point.value for point in fault_series[series.id].points) == 0.0
    )
    scope_observations = tuple(
        _scope_observation(
            scope_id,
            spec=spec,
            baseline_series=baseline_series,
            fault_series=fault_series,
        )
        for scope_id in fault_mode.reasoning_scope_component_ids
    )
    suspected_root_cause = (
        f"{fault_mode.target_component_id} under {fault_mode.fault_kind} keeps "
        f"{', '.join(blocked_logic_node_ids) or 'the monitored command path'} from reaching the baseline state."
    )
    reasoning_steps = [
        f"Baseline completion is {'reached' if baseline_report.completion_reached else 'not reached'}, while the injected-fault replay is {'reached' if fault_report.completion_reached else 'not reached'}.",
        f"Injected fault mode {fault_mode.id} targets {fault_mode.target_component_id} with {fault_mode.fault_kind}.",
    ]
    if affected_signal_ids:
        reasoning_steps.append(f"Affected monitored signals: {', '.join(affected_signal_ids)}.")
    if blocked_logic_node_ids:
        reasoning_steps.append(f"Logic nodes blocked by the injected fault: {', '.join(blocked_logic_node_ids)}.")
    reasoning_steps.append(f"Observed symptom under replay: {fault_mode.symptom}")

    return FaultDiagnosisReport(
        system_id=spec.system_id,
        system_title=spec.title,
        scenario_id=baseline_report.scenario_id,
        scenario_label=baseline_report.scenario_label,
        fault_mode_id=fault_mode.id,
        fault_kind=fault_mode.fault_kind,
        target_component_id=fault_mode.target_component_id,
        symptom=fault_mode.symptom,
        baseline_completion_reached=baseline_report.completion_reached,
        fault_completion_reached=fault_report.completion_reached,
        affected_signal_ids=affected_signal_ids,
        blocked_logic_node_ids=blocked_logic_node_ids,
        suspected_root_cause=suspected_root_cause,
        reasoning_steps=tuple(reasoning_steps),
        expected_sections=fault_mode.expected_diagnostic_sections,
        scope_observations=scope_observations,
        optimization_suggestion=fault_mode.optimization_prompt,
        assumptions=tuple(item for item in (*baseline_report.assumptions, *fault_report.assumptions, assumption) if item),
        baseline_report=baseline_report,
        fault_report=fault_report,
    )


def build_fault_diagnosis_report_from_intake_packet(
    packet: ControlSystemIntakePacket,
    *,
    scenario_id: str,
    fault_mode_id: str,
    sample_period_s: float = 0.5,
) -> FaultDiagnosisReport:
    return build_fault_diagnosis_report(
        intake_packet_to_workbench_spec(packet),
        scenario_id=scenario_id,
        fault_mode_id=fault_mode_id,
        sample_period_s=sample_period_s,
    )


def render_fault_diagnosis_text(report: FaultDiagnosisReport) -> str:
    lines = [
        f"system: {report.system_id} - {report.system_title}",
        f"scenario: {report.scenario_id} - {report.scenario_label}",
        f"fault_mode: {report.fault_mode_id} ({report.fault_kind}) target={report.target_component_id}",
        f"symptom: {report.symptom}",
        (
            "completion: "
            f"baseline={'yes' if report.baseline_completion_reached else 'no'} "
            f"fault={'yes' if report.fault_completion_reached else 'no'}"
        ),
        f"suspected_root_cause: {report.suspected_root_cause}",
    ]
    if report.affected_signal_ids:
        lines.append(f"affected_signals: {', '.join(report.affected_signal_ids)}")
    if report.blocked_logic_node_ids:
        lines.append(f"blocked_logic_nodes: {', '.join(report.blocked_logic_node_ids)}")
    lines.append("reasoning_steps:")
    lines.extend(f"  - {step}" for step in report.reasoning_steps)
    lines.append("scope_observations:")
    for observation in report.scope_observations:
        lines.append(
            f"  - {observation.id} [{observation.status}] "
            f"baseline_end={observation.baseline_end if observation.baseline_end is not None else 'n/a'} "
            f"fault_end={observation.fault_end if observation.fault_end is not None else 'n/a'} "
            f"{observation.note}"
        )
    lines.append(f"optimization: {report.optimization_suggestion}")
    if report.assumptions:
        lines.append("assumptions:")
        lines.extend(f"  - {item}" for item in report.assumptions)
    return "\n".join(lines)

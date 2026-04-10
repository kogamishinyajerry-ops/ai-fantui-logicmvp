from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from well_harness.document_intake import ControlSystemIntakePacket, intake_packet_to_workbench_spec
from well_harness.system_spec import (
    AcceptanceScenarioSpec,
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    SteadySignalSpec,
    TimedTransitionSpec,
)


@dataclass(frozen=True)
class PlaybackPoint:
    time_s: float
    value: float


@dataclass(frozen=True)
class PlaybackSeries:
    id: str
    label: str
    kind: str
    unit: str
    source: str
    points: tuple[PlaybackPoint, ...]


@dataclass(frozen=True)
class PlaybackEvent:
    time_s: float
    kind: str
    label: str
    details: str


@dataclass(frozen=True)
class ScenarioPlaybackReport:
    system_id: str
    system_title: str
    scenario_id: str
    scenario_label: str
    sample_period_s: float
    total_duration_s: float
    time_scale_factor: float
    completion_condition: str
    completion_reached: bool
    assumptions: tuple[str, ...]
    signal_series: tuple[PlaybackSeries, ...]
    logic_series: tuple[PlaybackSeries, ...]
    events: tuple[PlaybackEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _coerce_numeric(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "on"}:
            return 1.0
        if lowered in {"0", "false", "off"}:
            return 0.0
        return float(value)
    raise ValueError(f"unsupported signal value: {value!r}")


def _component_default_value(component: ComponentSpec) -> float:
    if component.allowed_range is not None:
        lower, upper = component.allowed_range
        if lower <= 0.0 <= upper:
            return 0.0
        return float(lower)
    if component.allowed_states:
        if "0" in component.allowed_states:
            return 0.0
        return _coerce_numeric(component.allowed_states[0])
    return 0.0


def _steady_signal_map(scenario: AcceptanceScenarioSpec) -> dict[str, SteadySignalSpec]:
    return {signal.signal_id: signal for signal in scenario.steady_signals}


def _transition_map(scenario: AcceptanceScenarioSpec) -> dict[str, tuple[TimedTransitionSpec, ...]]:
    signal_map: dict[str, list[TimedTransitionSpec]] = {}
    for transition in scenario.transitions:
        signal_map.setdefault(transition.signal_id, []).append(transition)
    return {key: tuple(sorted(items, key=lambda item: (item.start_s, item.end_s))) for key, items in signal_map.items()}


def _signal_value_at_time(
    component: ComponentSpec,
    time_s: float,
    *,
    steady_signals: dict[str, SteadySignalSpec],
    transitions: dict[str, tuple[TimedTransitionSpec, ...]],
) -> float:
    baseline = _coerce_numeric(steady_signals[component.id].value) if component.id in steady_signals else _component_default_value(component)
    active_value = baseline
    for transition in transitions.get(component.id, ()):
        if time_s < transition.start_s:
            return active_value
        if transition.start_s == transition.end_s:
            active_value = _coerce_numeric(transition.end_value)
            continue
        if transition.start_s <= time_s <= transition.end_s:
            progress = (time_s - transition.start_s) / (transition.end_s - transition.start_s)
            return _coerce_numeric(transition.start_value) + (
                (_coerce_numeric(transition.end_value) - _coerce_numeric(transition.start_value)) * progress
            )
        active_value = _coerce_numeric(transition.end_value)
    return active_value


def _evaluate_condition(condition: LogicConditionSpec, signal_values: dict[str, float]) -> bool:
    current_value = signal_values.get(condition.source_component_id, 0.0)
    threshold_value = condition.threshold_value
    if condition.comparison == "==":
        return current_value == _coerce_numeric(threshold_value)
    if condition.comparison == "!=":
        return current_value != _coerce_numeric(threshold_value)
    if condition.comparison == ">=":
        return current_value >= _coerce_numeric(threshold_value)
    if condition.comparison == "<=":
        return current_value <= _coerce_numeric(threshold_value)
    if condition.comparison == ">":
        return current_value > _coerce_numeric(threshold_value)
    if condition.comparison == "<":
        return current_value < _coerce_numeric(threshold_value)
    if condition.comparison == "between_exclusive":
        lower, upper = threshold_value
        return current_value > _coerce_numeric(lower) and current_value < _coerce_numeric(upper)
    if condition.comparison == "after_unlock":
        return current_value >= _coerce_numeric(threshold_value)
    return False


def _logic_active(logic_node: LogicNodeSpec, signal_values: dict[str, float]) -> bool:
    return all(_evaluate_condition(condition, signal_values) for condition in logic_node.conditions)


def _active_output_value(component: ComponentSpec, active: bool) -> float:
    if component.allowed_states:
        if active:
            if "1" in component.allowed_states:
                return 1.0
            return _coerce_numeric(component.allowed_states[-1])
        if "0" in component.allowed_states:
            return 0.0
        return _coerce_numeric(component.allowed_states[0])
    if component.allowed_range is not None:
        lower, upper = component.allowed_range
        if active:
            return float(upper)
        if lower <= 0.0 <= upper:
            return 0.0
        return float(lower)
    return 1.0 if active else 0.0


def _sample_times(total_duration_s: float, sample_period_s: float) -> tuple[float, ...]:
    step_count = max(int(round(total_duration_s / sample_period_s)), 1)
    samples = [round(index * sample_period_s, 6) for index in range(step_count + 1)]
    final_value = round(total_duration_s, 6)
    if samples[-1] != final_value:
        samples.append(final_value)
    return tuple(samples)


def _scenario_by_id(spec: ControlSystemWorkbenchSpec, scenario_id: str) -> AcceptanceScenarioSpec:
    for scenario in spec.acceptance_scenarios:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"unknown scenario: {scenario_id}")


def build_scenario_playback_report(
    spec: ControlSystemWorkbenchSpec,
    *,
    scenario_id: str,
    sample_period_s: float = 0.5,
) -> ScenarioPlaybackReport:
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be greater than 0.")
    scenario = _scenario_by_id(spec, scenario_id)
    components = {component.id: component for component in spec.components}
    logic_nodes = {logic_node.id: logic_node for logic_node in spec.logic_nodes}
    steady_signals = _steady_signal_map(scenario)
    transitions = _transition_map(scenario)
    downstream_component_ids = {
        component_id
        for logic_node in spec.logic_nodes
        for component_id in logic_node.downstream_component_ids
    }
    assumptions = sorted(
        {
            f"{signal_id} uses default baseline {_component_default_value(components[signal_id])} because the scenario does not define a steady state or transition."
            for signal_id in {
                *scenario.monitored_signal_ids,
                *{
                    condition.source_component_id
                    for logic_node in spec.logic_nodes
                    for condition in logic_node.conditions
                },
            }
            if signal_id in components and signal_id not in steady_signals and signal_id not in transitions and signal_id not in downstream_component_ids
        }
    )

    signal_points: dict[str, list[PlaybackPoint]] = {component_id: [] for component_id in scenario.monitored_signal_ids}
    logic_points: dict[str, list[PlaybackPoint]] = {logic_id: [] for logic_id in logic_nodes}
    events: list[PlaybackEvent] = []
    previous_logic_states: dict[str, bool] = {}
    previous_component_values: dict[str, float] = {}

    for time_s in _sample_times(scenario.total_duration_s, sample_period_s):
        component_values = {
            component_id: _signal_value_at_time(
                component,
                time_s,
                steady_signals=steady_signals,
                transitions=transitions,
            )
            for component_id, component in components.items()
        }
        logic_states: dict[str, bool] = {}
        for _ in range(len(logic_nodes) + 1):
            changed = False
            next_logic_states = {
                logic_id: _logic_active(logic_node, component_values)
                for logic_id, logic_node in logic_nodes.items()
            }
            updated_values = dict(component_values)
            for component_id in downstream_component_ids:
                component = components[component_id]
                component_active = any(
                    next_logic_states[logic_node.id]
                    for logic_node in spec.logic_nodes
                    if component_id in logic_node.downstream_component_ids
                )
                next_value = _active_output_value(component, component_active)
                if updated_values.get(component_id) != next_value:
                    updated_values[component_id] = next_value
                    changed = True
            if next_logic_states == logic_states and not changed:
                break
            logic_states = next_logic_states
            component_values = updated_values

        for component_id in scenario.monitored_signal_ids:
            component = components[component_id]
            signal_points[component_id].append(PlaybackPoint(time_s=time_s, value=round(component_values[component_id], 6)))
            previous_value = previous_component_values.get(component_id)
            current_value = component_values[component_id]
            if previous_value is not None and previous_value != current_value:
                events.append(
                    PlaybackEvent(
                        time_s=time_s,
                        kind="signal_change",
                        label=component.label,
                        details=f"{component.id} changed from {previous_value:g} to {current_value:g}.",
                    )
                )
        for logic_id, active in logic_states.items():
            logic_points[logic_id].append(PlaybackPoint(time_s=time_s, value=1.0 if active else 0.0))
            previous_state = previous_logic_states.get(logic_id)
            if previous_state is not None and previous_state != active:
                events.append(
                    PlaybackEvent(
                        time_s=time_s,
                        kind="logic_change",
                        label=logic_nodes[logic_id].label,
                        details=f"{logic_id} changed from {int(previous_state)} to {int(active)}.",
                    )
                )
        previous_logic_states = logic_states
        previous_component_values = {component_id: component_values[component_id] for component_id in scenario.monitored_signal_ids}

    for transition in scenario.transitions:
        events.append(
            PlaybackEvent(
                time_s=transition.start_s,
                kind="transition_start",
                label=transition.signal_id,
                details=f"{transition.signal_id} transition starts: {transition.note}",
            )
        )
        events.append(
            PlaybackEvent(
                time_s=transition.end_s,
                kind="transition_end",
                label=transition.signal_id,
                details=f"{transition.signal_id} transition ends at {transition.end_value:g}{transition.unit}.",
            )
        )

    signal_series = tuple(
        PlaybackSeries(
            id=component_id,
            label=components[component_id].label,
            kind=components[component_id].kind,
            unit=components[component_id].unit,
            source="derived_output" if component_id in downstream_component_ids else "scenario_input",
            points=tuple(signal_points[component_id]),
        )
        for component_id in scenario.monitored_signal_ids
    )
    logic_series = tuple(
        PlaybackSeries(
            id=logic_id,
            label=logic_node.label,
            kind="logic_node",
            unit="state",
            source="logic_evaluation",
            points=tuple(logic_points[logic_id]),
        )
        for logic_id, logic_node in logic_nodes.items()
    )
    completion_reached = False
    if "==" in scenario.completion_condition:
        component_id, value_text = scenario.completion_condition.split("==", 1)
        completion_signal_id = component_id.strip()
        if completion_signal_id in previous_component_values:
            completion_reached = previous_component_values[completion_signal_id] == _coerce_numeric(value_text.strip())

    return ScenarioPlaybackReport(
        system_id=spec.system_id,
        system_title=spec.title,
        scenario_id=scenario.id,
        scenario_label=scenario.label,
        sample_period_s=sample_period_s,
        total_duration_s=scenario.total_duration_s,
        time_scale_factor=scenario.time_scale_factor,
        completion_condition=scenario.completion_condition,
        completion_reached=completion_reached,
        assumptions=tuple(assumptions),
        signal_series=signal_series,
        logic_series=logic_series,
        events=tuple(sorted(events, key=lambda item: (item.time_s, item.kind, item.label))),
    )


def build_playback_report_from_intake_packet(
    packet: ControlSystemIntakePacket,
    *,
    scenario_id: str,
    sample_period_s: float = 0.5,
) -> ScenarioPlaybackReport:
    return build_scenario_playback_report(
        intake_packet_to_workbench_spec(packet),
        scenario_id=scenario_id,
        sample_period_s=sample_period_s,
    )


def render_playback_report_text(report: ScenarioPlaybackReport) -> str:
    lines = [
        f"system: {report.system_id} - {report.system_title}",
        f"scenario: {report.scenario_id} - {report.scenario_label}",
        (
            f"timeline: duration={report.total_duration_s:g}s "
            f"sample_period={report.sample_period_s:g}s "
            f"time_scale_factor={report.time_scale_factor:g}"
        ),
        f"completion_condition: {report.completion_condition}",
        f"completion_reached: {'yes' if report.completion_reached else 'no'}",
    ]
    if report.assumptions:
        lines.append("assumptions:")
        lines.extend(f"  - {item}" for item in report.assumptions)
    lines.append("signal snapshots:")
    for series in report.signal_series:
        lines.append(
            f"  - {series.id} [{series.unit}] source={series.source} "
            f"start={series.points[0].value:g} end={series.points[-1].value:g}"
        )
    lines.append("logic snapshots:")
    for series in report.logic_series:
        lines.append(f"  - {series.id} start={series.points[0].value:g} end={series.points[-1].value:g}")
    if report.events:
        lines.append("events:")
        lines.extend(f"  - t={event.time_s:g}s {event.kind}: {event.details}" for event in report.events[:12])
    return "\n".join(lines)

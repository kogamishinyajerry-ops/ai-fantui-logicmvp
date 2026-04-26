from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Tuple


@dataclass(frozen=True)
class SwitchWindow:
    name: str
    near_zero_deg: float
    deep_reverse_deg: float

    def contains(self, tra_deg: float) -> bool:
        low = min(self.near_zero_deg, self.deep_reverse_deg)
        high = max(self.near_zero_deg, self.deep_reverse_deg)
        return low <= tra_deg <= high


@dataclass(frozen=True)
class HarnessConfig:
    step_s: float = 0.1
    sw1_window: SwitchWindow = field(
        default_factory=lambda: SwitchWindow(
            name="SW1",
            near_zero_deg=-1.4,
            deep_reverse_deg=-6.2,
        )
    )
    sw2_window: SwitchWindow = field(
        default_factory=lambda: SwitchWindow(
            name="SW2",
            near_zero_deg=-5.0,
            deep_reverse_deg=-9.8,
        )
    )
    logic1_ra_ft_threshold: float = 6.0
    # PROP-20260426T075902988411-e27a6e (2026-04-26): "L2 SW2 应该 tighten".
    # Engineer-accepted tightening of L2's SW2 dependency: SW2 may
    # remain latched up to TRA = sw2_window.near_zero_deg (-5.0°),
    # but L2 should only honor SW2 when the lever is actually held
    # below this stricter threshold. This adds a 0.5° hysteresis
    # margin at the upper edge of the SW2 latch window so L2
    # deactivates 0.5° before SW2 itself resets.
    logic2_sw2_max_tra_deg: float = -5.5
    logic3_tra_deg_threshold: float = -11.74
    reverse_travel_min_deg: float = -32.0
    reverse_travel_max_deg: float = 0.0
    deploy_90_threshold_percent: float = 90.0
    tls_unlock_delay_s: float = 0.3
    pls_unlock_delay_s: float = 0.2
    deploy_rate_percent_per_s: float = 30.0


@dataclass(frozen=True)
class PilotFrame:
    duration_s: float
    radio_altitude_ft: float
    tra_deg: float
    engine_running: bool
    aircraft_on_ground: bool
    reverser_inhibited: bool
    eec_enable: bool
    n1k: float
    max_n1k_deploy_limit: float


@dataclass(frozen=True)
class PilotInputs:
    radio_altitude_ft: float
    tra_deg: float
    engine_running: bool
    aircraft_on_ground: bool
    reverser_inhibited: bool
    eec_enable: bool
    n1k: float
    max_n1k_deploy_limit: float


@dataclass(frozen=True)
class Scenario:
    name: str
    frames: Sequence[PilotFrame]


@dataclass(frozen=True)
class PlantSensors:
    tls_unlocked_ls: bool
    pls_unlocked_ls: Tuple[bool, bool, bool, bool]
    reverser_not_deployed_eec: bool
    reverser_fully_deployed_eec: bool
    deploy_90_percent_vdt: bool
    deploy_position_percent: float

    @property
    def all_pls_unlocked(self) -> bool:
        return all(self.pls_unlocked_ls)


@dataclass(frozen=True)
class ResolvedInputs:
    radio_altitude_ft: float
    tra_deg: float
    sw1: bool
    sw2: bool
    engine_running: bool
    aircraft_on_ground: bool
    reverser_inhibited: bool
    eec_enable: bool
    n1k: float
    max_n1k_deploy_limit: float
    tls_unlocked_ls: bool
    all_pls_unlocked_ls: bool
    reverser_not_deployed_eec: bool
    reverser_fully_deployed_eec: bool
    deploy_90_percent_vdt: bool


@dataclass(frozen=True)
class ControllerOutputs:
    logic1_active: bool
    logic2_active: bool
    logic3_active: bool
    logic4_active: bool
    tls_115vac_cmd: bool
    etrac_540vdc_cmd: bool
    eec_deploy_cmd: bool
    pls_power_cmd: bool
    pdu_motor_cmd: bool
    throttle_electronic_lock_release_cmd: bool


@dataclass(frozen=True)
class LogicConditionExplain:
    name: str
    current_value: Any
    comparison: str
    threshold_value: Any
    passed: bool


@dataclass(frozen=True)
class LogicExplain:
    logic_name: str
    active: bool
    conditions: Tuple[LogicConditionExplain, ...]

    @property
    def failed_conditions(self) -> Tuple[LogicConditionExplain, ...]:
        return tuple(condition for condition in self.conditions if not condition.passed)


@dataclass(frozen=True)
class ControllerExplain:
    logic1: LogicExplain
    logic2: LogicExplain
    logic3: LogicExplain
    logic4: LogicExplain

    def by_logic_name(self, logic_name: str) -> LogicExplain:
        if logic_name == "logic1":
            return self.logic1
        if logic_name == "logic2":
            return self.logic2
        if logic_name == "logic3":
            return self.logic3
        if logic_name == "logic4":
            return self.logic4
        raise KeyError(f"Unknown logic name: {logic_name}")


@dataclass(frozen=True)
class PlantDebugState:
    tls_powered_s: float
    pls_powered_s: float
    tls_unlocked_ls: bool
    pls_unlocked_ls: Tuple[bool, bool, bool, bool]
    deploy_position_percent: float

    @property
    def all_pls_unlocked_ls(self) -> bool:
        return all(self.pls_unlocked_ls)


@dataclass(frozen=True)
class TraceRow:
    time_s: float
    pilot: PilotInputs
    resolved_inputs: ResolvedInputs
    plant_sensors: PlantSensors
    plant_state: PlantDebugState
    controller_outputs: ControllerOutputs
    controller_explain: ControllerExplain

    @property
    def tra_deg(self) -> float:
        return self.pilot.tra_deg

    @property
    def sw1(self) -> bool:
        return self.resolved_inputs.sw1

    @property
    def sw2(self) -> bool:
        return self.resolved_inputs.sw2

    @property
    def tls_unlocked_ls(self) -> bool:
        return self.plant_sensors.tls_unlocked_ls

    @property
    def all_pls_unlocked_ls(self) -> bool:
        return self.plant_sensors.all_pls_unlocked

    @property
    def deploy_90_percent_vdt(self) -> bool:
        return self.plant_sensors.deploy_90_percent_vdt

    @property
    def deploy_position_percent(self) -> float:
        return self.plant_sensors.deploy_position_percent

    @property
    def logic1_active(self) -> bool:
        return self.controller_outputs.logic1_active

    @property
    def logic2_active(self) -> bool:
        return self.controller_outputs.logic2_active

    @property
    def logic3_active(self) -> bool:
        return self.controller_outputs.logic3_active

    @property
    def logic4_active(self) -> bool:
        return self.controller_outputs.logic4_active

    @property
    def tls_115vac_cmd(self) -> bool:
        return self.controller_outputs.tls_115vac_cmd

    @property
    def etrac_540vdc_cmd(self) -> bool:
        return self.controller_outputs.etrac_540vdc_cmd

    @property
    def eec_deploy_cmd(self) -> bool:
        return self.controller_outputs.eec_deploy_cmd

    @property
    def pls_power_cmd(self) -> bool:
        return self.controller_outputs.pls_power_cmd

    @property
    def pdu_motor_cmd(self) -> bool:
        return self.controller_outputs.pdu_motor_cmd

    @property
    def throttle_lock_release_cmd(self) -> bool:
        return self.controller_outputs.throttle_electronic_lock_release_cmd


@dataclass(frozen=True)
class FieldChange:
    field_name: str
    before: Any
    after: Any


@dataclass(frozen=True)
class TraceEvent:
    time_s: float
    changes: Tuple[FieldChange, ...]


@dataclass(frozen=True)
class LogicConditionPassChange:
    name: str
    before_passed: bool
    after_passed: bool
    before_current_value: Any
    after_current_value: Any
    comparison: str
    threshold_value: Any


@dataclass(frozen=True)
class TraceFieldValueChange:
    field_group: str
    field_name: str
    before_value: Any
    after_value: Any


@dataclass(frozen=True)
class LogicTransitionDiagnosis:
    time_s: float
    logic_name: str
    before_time_s: float
    after_time_s: float
    before_active: bool
    after_active: bool
    before_failed_conditions: Tuple[str, ...]
    after_failed_conditions: Tuple[str, ...]
    changed_conditions: Tuple[LogicConditionPassChange, ...]
    context_changes: Tuple[TraceFieldValueChange, ...]


DEFAULT_EVENT_FIELDS = (
    "sw1",
    "sw2",
    "tls_unlocked_ls",
    "all_pls_unlocked_ls",
    "deploy_90_percent_vdt",
    "logic1_active",
    "logic2_active",
    "logic3_active",
    "logic4_active",
    "tls_115vac_cmd",
    "etrac_540vdc_cmd",
    "eec_deploy_cmd",
    "pls_power_cmd",
    "pdu_motor_cmd",
    "throttle_lock_release_cmd",
)

DIAGNOSIS_CONTEXT_FIELDS = (
    ("controller_outputs", "tls_115vac_cmd"),
    ("controller_outputs", "etrac_540vdc_cmd"),
    ("controller_outputs", "eec_deploy_cmd"),
    ("controller_outputs", "pls_power_cmd"),
    ("controller_outputs", "pdu_motor_cmd"),
    ("controller_outputs", "throttle_lock_release_cmd"),
    ("plant_sensors", "tls_unlocked_ls"),
    ("plant_sensors", "all_pls_unlocked_ls"),
    ("plant_sensors", "deploy_90_percent_vdt"),
    ("plant_sensors", "deploy_position_percent"),
    ("plant_state", "tls_powered_s"),
    ("plant_state", "pls_powered_s"),
)


@dataclass
class SimulationResult:
    scenario_name: str
    rows: List[TraceRow]

    def events(self, fields: Sequence[str] | None = None) -> List[TraceEvent]:
        tracked_fields = tuple(fields or DEFAULT_EVENT_FIELDS)
        if not self.rows:
            return []

        previous_values = {
            field_name: _zero_like(getattr(self.rows[0], field_name))
            for field_name in tracked_fields
        }
        events: List[TraceEvent] = []

        for row in self.rows:
            changes = []
            for field_name in tracked_fields:
                current_value = getattr(row, field_name)
                previous_value = previous_values[field_name]
                if current_value != previous_value:
                    changes.append(
                        FieldChange(
                            field_name=field_name,
                            before=previous_value,
                            after=current_value,
                        )
                    )
                    previous_values[field_name] = current_value
            if changes:
                events.append(TraceEvent(time_s=row.time_s, changes=tuple(changes)))

        return events

    def logic_transition_diagnostics(self, logic_name: str | None = None) -> List[LogicTransitionDiagnosis]:
        logic_names = (logic_name,) if logic_name else ("logic1", "logic2", "logic3", "logic4")
        diagnostics: List[LogicTransitionDiagnosis] = []

        for before, after in zip(self.rows, self.rows[1:]):
            for current_logic_name in logic_names:
                before_explain = before.controller_explain.by_logic_name(current_logic_name)
                after_explain = after.controller_explain.by_logic_name(current_logic_name)
                if before_explain.active == after_explain.active:
                    continue

                diagnostics.append(
                    LogicTransitionDiagnosis(
                        time_s=after.time_s,
                        logic_name=current_logic_name,
                        before_time_s=before.time_s,
                        after_time_s=after.time_s,
                        before_active=before_explain.active,
                        after_active=after_explain.active,
                        before_failed_conditions=_failed_condition_names(before_explain),
                        after_failed_conditions=_failed_condition_names(after_explain),
                        changed_conditions=_changed_condition_passes(before_explain, after_explain),
                        context_changes=_context_field_changes(before, after),
                    )
                )

        return diagnostics


def _zero_like(value: Any) -> Any:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 0
    if isinstance(value, float):
        return 0.0
    if isinstance(value, tuple):
        return tuple(_zero_like(item) for item in value)
    return None


def _failed_condition_names(logic_explain: LogicExplain) -> Tuple[str, ...]:
    return tuple(condition.name for condition in logic_explain.failed_conditions)


def _changed_condition_passes(
    before_explain: LogicExplain,
    after_explain: LogicExplain,
) -> Tuple[LogicConditionPassChange, ...]:
    before_by_name = {condition.name: condition for condition in before_explain.conditions}
    changes = []

    for after_condition in after_explain.conditions:
        before_condition = before_by_name.get(after_condition.name)
        if before_condition is None or before_condition.passed == after_condition.passed:
            continue
        changes.append(
            LogicConditionPassChange(
                name=after_condition.name,
                before_passed=before_condition.passed,
                after_passed=after_condition.passed,
                before_current_value=before_condition.current_value,
                after_current_value=after_condition.current_value,
                comparison=after_condition.comparison,
                threshold_value=after_condition.threshold_value,
            )
        )

    return tuple(changes)


def _context_field_changes(before: TraceRow, after: TraceRow) -> Tuple[TraceFieldValueChange, ...]:
    changes = []
    for field_group, field_name in DIAGNOSIS_CONTEXT_FIELDS:
        before_value = _context_field_value(before, field_group, field_name)
        after_value = _context_field_value(after, field_group, field_name)
        if before_value == after_value:
            continue
        changes.append(
            TraceFieldValueChange(
                field_group=field_group,
                field_name=field_name,
                before_value=before_value,
                after_value=after_value,
            )
        )
    return tuple(changes)


def _context_field_value(row: TraceRow, field_group: str, field_name: str) -> Any:
    if field_group == "plant_state":
        return getattr(row.plant_state, field_name)
    return getattr(row, field_name)

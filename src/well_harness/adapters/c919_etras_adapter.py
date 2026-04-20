"""
C919 E-TRAS (Electric Thrust Reverser Actuation System) Controller Adapter

PDF traceability:
  20260417 C919反推控制逻辑需求文档.pdf (10 pages, Kogami GATE-P34-PLAN Approved 2026-04-20)

Covers:
  表1          — 11 component counts (actuators, locks, PMDU, TRCU, …)
  Figure 1     — E-TRAS schematic
  Step 1-10    — Landing → deploy → max reverse → stow → stowed-locked timeline
  §1.1.1 图 2  — EICU CMD2 (115VAC 3-phase to TRCU)
  §1.1.2 图 3  — EICU CMD3 (S-R flipflop for deploy-intent latch)
  §1.1.2 图 4  — TR_Command3_Enable (filtered CMD3 + over-temp check)
  §1.1.3 图 5  — FADEC Deploy Command (CMD1) with N1k / TR_WOW / TRA gating
  §1.1.3 ④    — TR_WOW persistence 2.25s TRUE / 120ms FALSE
  表 2         — MLG_WOW LGCU1/LGCU2 redundancy selection table

This adapter is a NEW sibling to `thrust_reverser_hardware_v1` / `reverse_diagnosis.py`.
It does NOT replace the simplified thrust-reverser baseline — both coexist.

Snapshot contract (keys required by evaluate_snapshot):
  === A/C inputs ===
    lgcu1_mlg_wow_value : bool   LGCU1 raw WOW value
    lgcu1_mlg_wow_valid : bool   LGCU1 validity flag
    lgcu2_mlg_wow_value : bool   LGCU2 raw WOW value
    lgcu2_mlg_wow_valid : bool   LGCU2 validity flag
    tr_inhibited        : bool   A/C-bus TR inhibition signal
  === Throttle ===
    tra_deg             : float  Throttle Resolver Angle (deg)
    atltla              : bool   Microswitch 1 (闭合 when TRA ∈ [-1.4°, -6.2°])
    apwtla              : bool   Microswitch 2 (闭合 when TRA ∈ [-5°, -9.8°])
  === TR sensors ===
    tr_position_percent : float  Actuator VDT position (0=stowed, 100=fully deployed)
    vdt_sensor_valid    : bool   VDT validity
    tls_ls_a_unlocked   : bool   TLS sensor A reports unlocked
    tls_ls_a_valid      : bool
    tls_ls_b_unlocked   : bool
    tls_ls_b_valid      : bool
    left_pylon_ls_a_unlocked  : bool
    left_pylon_ls_a_valid     : bool
    left_pylon_ls_b_unlocked  : bool
    left_pylon_ls_b_valid     : bool
    right_pylon_ls_a_unlocked : bool
    right_pylon_ls_a_valid    : bool
    right_pylon_ls_b_unlocked : bool
    right_pylon_ls_b_valid    : bool
    pls_ls_a_locked     : bool   Primary Lock System sensor A reports locked
    pls_ls_b_locked     : bool
    e_tras_over_temp_fault : bool  TRCU over-temperature fault word
    trcu_power_on       : bool   115VAC 3-phase is currently powering TRCU
  === Mode / Engine ===
    engine_running      : bool   Engine at or above idle
    n1k_percent         : float  Corrected fan speed
    fadec_maintenance_mode : bool
    tr_maintenance_command_from_ac : bool
    trcu_in_menu_mode   : bool
    tr_wow              : bool   FADEC-derived WOW (already filtered 2.25s/120ms)
  === Persistence-filter state (caller-maintained) ===
    comm2_timer_s                  : float  EICU internal Comm2 timer (PDF §1.1.1 ③)
    tr_position_deployed_confirm_s : float  duration tr_position_percent ≥ 80%
    tr_stowed_locked_confirm_s     : float  duration stow+lock conditions met
    lock_unlock_confirm_s          : float  duration lock-unlock fallback 1/2 ok
    prev_eicu_cmd3                 : bool   previous S-R latch output (for RS flipflop)

Returns GenericTruthEvaluation with computed EICU CMD2/CMD3, TR_Command3_Enable,
FADEC Deploy/Stow commands, active logic-node IDs, and blocked reasons.
"""
from __future__ import annotations

from typing import Any, Mapping

from well_harness.controller_adapter import (
    ControllerTruthMetadata,
    GenericTruthEvaluation,
)
from well_harness.system_spec import (
    AcceptanceScenarioSpec,
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    SteadySignalSpec,
    TimedTransitionSpec,
    default_workbench_clarification_questions,
    workbench_spec_to_dict,
)

# ---------------------------------------------------------------------------
# Adapter metadata
# ---------------------------------------------------------------------------
C919_ETRAS_SYSTEM_ID = "c919-etras"
C919_ETRAS_SOURCE_OF_TRUTH = "src/well_harness/adapters/c919_etras_adapter.py"
C919_ETRAS_DESCRIPTION = (
    "C919 Electric Thrust Reverser Actuation System (E-TRAS). Derives EICU CMD2, "
    "EICU CMD3 (S-R flipflop), TR_Command3_Enable, FADEC Deploy Command, and "
    "FADEC Stow Command from throttle position, MLG_WOW redundancy, engine N1k, "
    "actuator VDT position, and lock sensor array per "
    "20260417-C919反推控制逻辑需求文档.pdf. Includes TR_Inhibited safety block, "
    "400ms lock-unlock confirmation, 0.5s deployed confirmation, and 1s "
    "stowed-locked confirmation."
)

# ---------------------------------------------------------------------------
# PDF-derived constants (mirrored from config/hardware/c919_etras_hardware_v1.yaml)
# ---------------------------------------------------------------------------
# Throttle microswitch windows (PDF §Step2)
SW1_WINDOW_NEAR_ZERO_DEG = -1.4
SW1_WINDOW_DEEP_REVERSE_DEG = -6.2
SW2_WINDOW_NEAR_ZERO_DEG = -5.0
SW2_WINDOW_DEEP_REVERSE_DEG = -9.8

# TR_Deployed threshold (PDF §1.1.1 ④ / §Step4)
TR_DEPLOYED_POSITION_PERCENT = 80.0

# TRA thresholds
TRA_FWD_IDLE_THRESHOLD_DEG = -1.4         # PDF §1.1.2 图4 ②
TRA_REVERSE_IDLE_THRESHOLD_DEG = -11.74   # PDF §1.1.3 ⑥ / §Step2
TRA_STOW_POSITION_DEG = 0.0               # PDF §Step6

# Max N1k deploy limit (PDF §1.1.3 ⑤: 79-89% ambient-dependent; use mid-band default)
MAX_N1K_DEPLOY_LIMIT_PERCENT_MIN = 79.0
MAX_N1K_DEPLOY_LIMIT_PERCENT_MAX = 89.0
MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT = 84.0   # mid-band; traceability-matrix documented

# Max N1k stow limit (PDF §Step7: value not explicit; Q3-A assumption)
MAX_N1K_STOW_LIMIT_PERCENT = 30.0

# Persistence / confirmation times (PDF §1.1.x figures)
CONFIRMATION_0_5_S = 0.5                 # TR_Position deployed confirmation
COMM2_TIMER_LIMIT_S = 30.0               # EICU §1.1.1 ③
TR_STOWED_LOCKED_CONFIRM_S = 1.0         # §1.1.2 图4 ①
LOCK_CONFIRMATION_400MS_S = 0.4          # §1.1.3 ③
TR_WOW_TRUE_PERSIST_S = 2.25             # §1.1.3 ④
TR_WOW_FALSE_PERSIST_S = 0.12            # §1.1.3 ④

# Timeline (PDF §Step 1-10)
DEPLOY_TIME_MIN_S = 2.0
DEPLOY_TIME_MAX_S = 3.0
IDLE_TO_MAX_THRUST_S = 5.0
ENGINE_RPM_RAMP_DOWN_S = 7.5
STOW_TIME_S = 3.0
MAX_TO_FULLY_STOWED_TOTAL_S = 11.0
FADEC_CONFIRM_STOWED_S = 1.0


C919_ETRAS_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="c919-etras-controller-adapter",
    system_id=C919_ETRAS_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=C919_ETRAS_SOURCE_OF_TRUTH,
    description=C919_ETRAS_DESCRIPTION,
    truth_level="certified",  # P42: aligned with docs/provenance/adapter_truth_levels.yaml row "c919-etras" (P38 物理入库 · Appendix A resolved)
    status="In use",
)


# ---------------------------------------------------------------------------
# Helper: snapshot value extractors
# ---------------------------------------------------------------------------
def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
    """Return the value for key from snapshot, or raise KeyError."""
    if key not in snapshot:
        raise KeyError(f"missing snapshot value: {key}")
    return snapshot[key]


def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise TypeError(f"snapshot value {key!r} must be a bool-compatible value")


def _snapshot_float(snapshot: Mapping[str, Any], key: str) -> float:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        raise TypeError(f"snapshot value {key!r} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"snapshot value {key!r} must be numeric")


def _snapshot_str(snapshot: Mapping[str, Any], key: str) -> str:
    value = _require_snapshot_value(snapshot, key)
    if not isinstance(value, str):
        raise TypeError(f"snapshot value {key!r} must be a string")
    return value


# ---------------------------------------------------------------------------
# MLG_WOW redundancy selection (PDF 表 2)
# ---------------------------------------------------------------------------
def _select_mlg_wow(
    lgcu1_value: bool, lgcu1_valid: bool,
    lgcu2_value: bool, lgcu2_valid: bool,
) -> bool:
    """
    MLG_WOW redundancy selection per PDF 表 2.

    Policy (safety-conservative: default-FALSE when uncertain prevents unsafe
    reverser deployment while airborne):
      - both valid & agree      → use agreed value
      - both valid & disagree   → return FALSE (assume in-air; conservative)
      - only LGCU1 valid        → use LGCU1 value
      - only LGCU2 valid        → use LGCU2 value
      - both invalid            → return FALSE (assume in-air; conservative)
    """
    if lgcu1_valid and lgcu2_valid:
        if lgcu1_value == lgcu2_value:
            return lgcu1_value
        return False  # disagreement → conservative in-air
    if lgcu1_valid and not lgcu2_valid:
        return lgcu1_value
    if lgcu2_valid and not lgcu1_valid:
        return lgcu2_value
    return False  # both invalid → conservative in-air


# ---------------------------------------------------------------------------
# Lock state summary (PDF §1.1.3 ③)
# ---------------------------------------------------------------------------
def _tls_unlocked_confirmed(snapshot: Mapping[str, Any]) -> bool:
    """≥1 of 2 TLS sensors valid AND unlocked."""
    a_ok = _snapshot_bool(snapshot, "tls_ls_a_valid") and _snapshot_bool(snapshot, "tls_ls_a_unlocked")
    b_ok = _snapshot_bool(snapshot, "tls_ls_b_valid") and _snapshot_bool(snapshot, "tls_ls_b_unlocked")
    return a_ok or b_ok


def _pylon_locks_unlocked_confirmed(snapshot: Mapping[str, Any]) -> bool:
    """Each pylon needs ≥1 of 2 sensors valid AND unlocked (left AND right)."""
    left_a_ok = (
        _snapshot_bool(snapshot, "left_pylon_ls_a_valid")
        and _snapshot_bool(snapshot, "left_pylon_ls_a_unlocked")
    )
    left_b_ok = (
        _snapshot_bool(snapshot, "left_pylon_ls_b_valid")
        and _snapshot_bool(snapshot, "left_pylon_ls_b_unlocked")
    )
    right_a_ok = (
        _snapshot_bool(snapshot, "right_pylon_ls_a_valid")
        and _snapshot_bool(snapshot, "right_pylon_ls_a_unlocked")
    )
    right_b_ok = (
        _snapshot_bool(snapshot, "right_pylon_ls_b_valid")
        and _snapshot_bool(snapshot, "right_pylon_ls_b_unlocked")
    )
    return (left_a_ok or left_b_ok) and (right_a_ok or right_b_ok)


def _pls_both_locked(snapshot: Mapping[str, Any]) -> bool:
    """Primary Lock System: both A and B report locked (for stowed-locked check)."""
    return _snapshot_bool(snapshot, "pls_ls_a_locked") and _snapshot_bool(snapshot, "pls_ls_b_locked")


# ---------------------------------------------------------------------------
# Workbench spec builder
# ---------------------------------------------------------------------------
def build_c919_etras_workbench_spec() -> dict[str, Any]:
    spec = ControlSystemWorkbenchSpec(
        system_id=C919_ETRAS_SYSTEM_ID,
        title="C919 E-TRAS (Electric Thrust Reverser Actuation System)",
        objective=(
            "Model the C919 E-TRAS control logic chain: EICU CMD2 energizes TRCU "
            "when throttle is past FWD idle on ground and TR_Inhibited is clear; "
            "EICU CMD3 S-R-latches deploy intent; TR_Command3_Enable gates CMD3 "
            "with over-temperature fault and stowed-locked confirmation; FADEC "
            "Deploy Command issues when lock-unlocked confirmed ≥400ms, "
            "TR_Position≥80% confirmed ≥0.5s, engine running with N1k below deploy "
            "limit, TR_WOW true, and TRA<-11.74°; FADEC Stow Command withdraws "
            "upon TRA≥-1.4° toward forward idle."
        ),
        source_of_truth=C919_ETRAS_SOURCE_OF_TRUTH,
        components=(
            # ---- A/C / redundancy inputs ----
            ComponentSpec(
                id="mlg_wow",
                label="MLG_WOW (selected)",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description=(
                    "Selected main landing gear weight-on-wheels after LGCU1/LGCU2 "
                    "redundancy arbitration per PDF 表2."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="tr_inhibited",
                label="TR_Inhibited",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="A/C-bus electrical TR inhibition signal (PDF §1.1.1 ②).",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            # ---- Throttle ----
            ComponentSpec(
                id="tra_deg",
                label="Throttle Resolver Angle",
                kind="sensor",
                state_shape="analog",
                unit="deg",
                description=(
                    "Throttle Resolver Angle. Positive=forward thrust, negative=reverse. "
                    "TRA>-1.4°=FWD idle; TRA<-11.74°=reverse idle; TRA=0°=stow."
                ),
                allowed_range=(-32.0, 10.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="atltla",
                label="ATLTLA (SW1)",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description=(
                    "Microswitch 1 via 115VAC 1-phase relay. Closed when "
                    "TRA ∈ [-1.4°, -6.2°] (PDF §Step2)."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="apwtla",
                label="APWTLA (SW2)",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="Microswitch 2. Closed when TRA ∈ [-5°, -9.8°] (PDF §Step2).",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            # ---- TR device ----
            ComponentSpec(
                id="tr_position_percent",
                label="TR Position",
                kind="sensor",
                state_shape="analog",
                unit="percent",
                description=(
                    "Actuator VDT-measured TR deployment position. "
                    "0=stowed, 100=fully deployed. TR_Deployed=(position≥80%)."
                ),
                allowed_range=(0.0, 100.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="lock_state",
                label="Lock State (PLS+TLS+Pylon aggregate)",
                kind="sensor",
                state_shape="discrete",
                unit="state",
                description=(
                    "Aggregate of Primary Lock System, Tertiary Lock System, and "
                    "pylon lock sensors. Derived in adapter: "
                    "UNLOCKED_CONFIRMED=≥1/2 unlocked sensors valid on each of "
                    "TLS + left pylon + right pylon per PDF §1.1.3 ③; "
                    "STOWED_LOCKED=PLS both locked AND TR_Position≤ε."
                ),
                allowed_states=("UNKNOWN", "LOCKED", "UNLOCKED_CONFIRMED", "PARTIAL"),
                monitor_priority="required",
            ),
            # ---- Engine / mode ----
            ComponentSpec(
                id="engine_running",
                label="Engine Running",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="Engine at or above idle (PDF §1.1.2 ①).",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="n1k_percent",
                label="N1k Corrected Fan Speed",
                kind="sensor",
                state_shape="analog",
                unit="percent",
                description=(
                    "Corrected fan speed. Max N1k Deploy Limit 79-89% (ambient-dep); "
                    "Max N1k Stow Limit ≈30% (Q3-A assumption)."
                ),
                allowed_range=(0.0, 110.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="tr_wow",
                label="TR_WOW (FADEC-filtered)",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description=(
                    "FADEC-derived weight-on-wheels with 2.25s-TRUE / 120ms-FALSE "
                    "persistence (PDF §1.1.3 ④)."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="trcu_power_on",
                label="TRCU Power On (115VAC 3-phase)",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="115VAC 3-phase is currently powering TRCU input.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="e_tras_over_temp_fault",
                label="E-TRAS Over-Temp Fault",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="TRCU over-temperature fault word (PDF §1.1.2 图4 ④).",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            # ---- Computed commands (outputs of this controller) ----
            ComponentSpec(
                id="eicu_cmd2",
                label="EICU CMD2 (3-phase TRCU power)",
                kind="command",
                state_shape="binary",
                unit="state",
                description=(
                    "EICU command 2 — energize 115VAC 3-phase to TRCU (PDF §1.1.1 图2)."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="eicu_cmd3",
                label="EICU CMD3 (S-R latched deploy intent)",
                kind="command",
                state_shape="binary",
                unit="state",
                description=(
                    "EICU command 3 — S-R flipflop latching deploy intent. "
                    "Set by deploy entry conditions; reset by stowed-locked-1s (PDF §1.1.2 图3)."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="tr_command3_enable",
                label="TR_Command3_Enable",
                kind="command",
                state_shape="binary",
                unit="state",
                description=(
                    "TRCU-internal gated CMD3: CMD3=TRUE AND TRA above FWD idle AND "
                    "over-temp fault clear AND stowed-locked-1s clear (PDF §1.1.2 图4)."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="fadec_deploy_command",
                label="FADEC Deploy Command (CMD1)",
                kind="command",
                state_shape="binary",
                unit="state",
                description=(
                    "FADEC deploy command (PDF §1.1.3 图5). Gates on lock-unlocked-400ms, "
                    "TR_Position≥80%-0.5s, engine_running with N1k<max_deploy_limit, "
                    "TR_WOW, TR_Command3_Enable, and TRA<-11.74°."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="fadec_stow_command",
                label="FADEC Stow Command",
                kind="command",
                state_shape="binary",
                unit="state",
                description=(
                    "FADEC stow command. Active when TRA≥-1.4° (past FWD idle) and "
                    "deploy intent has been withdrawn."
                ),
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
        ),
        logic_nodes=(
            # LN1: EICU_CMD2 — energize TRCU
            LogicNodeSpec(
                id="ln_eicu_cmd2",
                label="LN-EICU-CMD2",
                description=(
                    "EICU commands 115VAC 3-phase to TRCU when the aircraft is on "
                    "ground, throttle has entered reverse region (ATLTLA OR APWTLA), "
                    "and TR_Inhibited is clear. Comm2 timer guards against "
                    "spurious single-pulse triggers (PDF §1.1.1 图2)."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="atltla_or_apwtla",
                        source_component_id="atltla",
                        comparison="==",
                        threshold_value=1,
                        note="ATLTLA OR APWTLA true — throttle is past reverse-region threshold (SW1 OR SW2 closed).",
                    ),
                    LogicConditionSpec(
                        name="mlg_wow_true",
                        source_component_id="mlg_wow",
                        comparison="==",
                        threshold_value=1,
                        note="Main-gear weight-on-wheels is TRUE — aircraft on ground.",
                    ),
                    LogicConditionSpec(
                        name="tr_not_inhibited",
                        source_component_id="tr_inhibited",
                        comparison="==",
                        threshold_value=0,
                        note="TR_Inhibited must be FALSE — A/C did not block TR operation.",
                    ),
                ),
                downstream_component_ids=("eicu_cmd2", "trcu_power_on"),
                evidence_priority="high",
            ),
            # LN2: EICU_CMD3 — S-R latched deploy intent
            LogicNodeSpec(
                id="ln_eicu_cmd3",
                label="LN-EICU-CMD3",
                description=(
                    "EICU CMD3 is an S-R flipflop latching deploy intent. "
                    "Set when ATLTLA true AND MLG_WOW true AND engine_running AND "
                    "NOT TR_Inhibited (PDF §1.1.2 图3 set-branch). "
                    "Reset when TR_Stowed_Locked confirmed for 1s (图4 ①) OR "
                    "TR_Inhibited becomes TRUE."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="atltla_latching",
                        source_component_id="atltla",
                        comparison="==",
                        threshold_value=1,
                        note="ATLTLA true — throttle in reverse region.",
                    ),
                    LogicConditionSpec(
                        name="mlg_wow_latching",
                        source_component_id="mlg_wow",
                        comparison="==",
                        threshold_value=1,
                        note="Ground confirmed.",
                    ),
                    LogicConditionSpec(
                        name="engine_running_latching",
                        source_component_id="engine_running",
                        comparison="==",
                        threshold_value=1,
                        note="Engine running (min idle).",
                    ),
                    LogicConditionSpec(
                        name="tr_not_inhibited_latching",
                        source_component_id="tr_inhibited",
                        comparison="==",
                        threshold_value=0,
                        note="Inhibit not asserted.",
                    ),
                ),
                downstream_component_ids=("eicu_cmd3",),
                evidence_priority="high",
            ),
            # LN3: TR_Command3_Enable — filtered CMD3
            LogicNodeSpec(
                id="ln_tr_command3_enable",
                label="LN-TR-CMD3-ENABLE",
                description=(
                    "TRCU filters EICU_CMD3 for over-temperature and stowed-locked "
                    "confirmation. Enable when EICU_CMD3 TRUE AND "
                    "e_tras_over_temp_fault FALSE AND NOT (tr_stowed_locked_confirm_s ≥ 1s). "
                    "TRA must be below FWD idle threshold (-1.4°) for enable to latch. "
                    "(PDF §1.1.2 图4)."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="eicu_cmd3_true",
                        source_component_id="eicu_cmd3",
                        comparison="==",
                        threshold_value=1,
                        note="EICU CMD3 latched true.",
                    ),
                    LogicConditionSpec(
                        name="not_over_temp",
                        source_component_id="e_tras_over_temp_fault",
                        comparison="==",
                        threshold_value=0,
                        note="No over-temperature fault.",
                    ),
                    LogicConditionSpec(
                        name="tra_below_fwd_idle",
                        source_component_id="tra_deg",
                        comparison="<",
                        threshold_value=TRA_FWD_IDLE_THRESHOLD_DEG,
                        note=f"TRA below FWD idle ({TRA_FWD_IDLE_THRESHOLD_DEG}°).",
                    ),
                ),
                downstream_component_ids=("tr_command3_enable",),
                evidence_priority="high",
            ),
            # LN4: FADEC Deploy Command (CMD1)
            LogicNodeSpec(
                id="ln_fadec_deploy_command",
                label="LN-FADEC-DEPLOY-CMD1",
                description=(
                    "FADEC Deploy Command asserts when: TR_Command3_Enable TRUE, "
                    "lock-unlocked fallback (≥1/2 sensors on TLS + each pylon) confirmed "
                    "≥400ms, TR_Position≥80% confirmed ≥0.5s, engine_running with "
                    "N1k<max_deploy_limit, TR_WOW TRUE, and TRA<-11.74°. "
                    "(PDF §1.1.3 图5)."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="tr_command3_enable_true",
                        source_component_id="tr_command3_enable",
                        comparison="==",
                        threshold_value=1,
                        note="Upstream enable latched.",
                    ),
                    LogicConditionSpec(
                        name="tr_position_deployed_confirmed",
                        source_component_id="tr_position_percent",
                        comparison=">=",
                        threshold_value=TR_DEPLOYED_POSITION_PERCENT,
                        note=(
                            "TR_Position ≥ 80% confirmed for ≥0.5s. "
                            "(Duration check performed by adapter against "
                            "snapshot['tr_position_deployed_confirm_s'].)"
                        ),
                    ),
                    LogicConditionSpec(
                        name="engine_running_deploy",
                        source_component_id="engine_running",
                        comparison="==",
                        threshold_value=1,
                        note="Engine running.",
                    ),
                    LogicConditionSpec(
                        name="n1k_below_deploy_limit",
                        source_component_id="n1k_percent",
                        comparison="<",
                        threshold_value=MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT,
                        note=(
                            f"N1k < Max Deploy Limit (default {MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT}%; "
                            f"envelope {MAX_N1K_DEPLOY_LIMIT_PERCENT_MIN}-{MAX_N1K_DEPLOY_LIMIT_PERCENT_MAX}%)."
                        ),
                    ),
                    LogicConditionSpec(
                        name="tr_wow_true_deploy",
                        source_component_id="tr_wow",
                        comparison="==",
                        threshold_value=1,
                        note="TR_WOW true (filtered 2.25s-TRUE / 120ms-FALSE).",
                    ),
                    LogicConditionSpec(
                        name="tra_at_or_below_reverse_idle",
                        source_component_id="tra_deg",
                        comparison="<=",
                        threshold_value=TRA_REVERSE_IDLE_THRESHOLD_DEG,
                        note=f"TRA ≤ reverse idle ({TRA_REVERSE_IDLE_THRESHOLD_DEG}°).",
                    ),
                ),
                downstream_component_ids=("fadec_deploy_command", "tr_position_percent"),
                evidence_priority="high",
            ),
            # LN5: FADEC Stow Command
            LogicNodeSpec(
                id="ln_fadec_stow_command",
                label="LN-FADEC-STOW-CMD",
                description=(
                    "FADEC Stow Command asserts when TRA has returned to forward region "
                    "(≥-1.4°) or when deploy intent is withdrawn, N1k below stow limit "
                    "(≈30%), and deploy command is not asserted (PDF §Step7)."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="tra_at_or_above_fwd_idle",
                        source_component_id="tra_deg",
                        comparison=">=",
                        threshold_value=TRA_FWD_IDLE_THRESHOLD_DEG,
                        note=f"TRA back at or past FWD idle ({TRA_FWD_IDLE_THRESHOLD_DEG}°).",
                    ),
                    LogicConditionSpec(
                        name="n1k_below_stow_limit",
                        source_component_id="n1k_percent",
                        comparison="<",
                        threshold_value=MAX_N1K_STOW_LIMIT_PERCENT,
                        note=f"N1k < Max Stow Limit ({MAX_N1K_STOW_LIMIT_PERCENT}%).",
                    ),
                    LogicConditionSpec(
                        name="engine_running_stow",
                        source_component_id="engine_running",
                        comparison="==",
                        threshold_value=1,
                        note="Engine still running.",
                    ),
                ),
                downstream_component_ids=("fadec_stow_command", "tr_position_percent"),
                evidence_priority="high",
            ),
        ),
        acceptance_scenarios=(
            # --- Scenario 1: nominal landing deploy (Step 1-5) ---
            AcceptanceScenarioSpec(
                id="nominal_landing_deploy",
                label="Nominal Landing Deploy (Step 1-5)",
                description=(
                    "Aircraft touches down (MLG_WOW→1), pilot pulls throttle from "
                    "FWD idle into reverse region. EICU CMD2 energizes TRCU. "
                    "TR_Position rises to 80%+ over 2-3s. Throttle advances to "
                    "reverse idle (-11.74°). FADEC issues Deploy Command (CMD1). "
                    "N1k ramps up toward max reverse thrust over 5s."
                ),
                time_scale_factor=1.0,
                total_duration_s=14.0,
                monitored_signal_ids=(
                    "mlg_wow",
                    "tra_deg",
                    "atltla",
                    "apwtla",
                    "tr_position_percent",
                    "eicu_cmd2",
                    "eicu_cmd3",
                    "tr_command3_enable",
                    "fadec_deploy_command",
                    "n1k_percent",
                    "tr_wow",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="mlg_wow",
                        start_s=0.0, end_s=0.1,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="Touchdown: MLG_WOW transitions 0→1 at Step 1.",
                    ),
                    TimedTransitionSpec(
                        signal_id="tra_deg",
                        start_s=0.5, end_s=2.0,
                        start_value=+5.0, end_value=SW1_WINDOW_DEEP_REVERSE_DEG,
                        unit="deg",
                        note="Pilot pulls throttle from FWD into SW1 window [-1.4°, -6.2°].",
                    ),
                    TimedTransitionSpec(
                        signal_id="atltla",
                        start_s=1.8, end_s=2.0,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="SW1 closes when TRA enters [-1.4°, -6.2°].",
                    ),
                    TimedTransitionSpec(
                        signal_id="eicu_cmd2",
                        start_s=2.0, end_s=2.1,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="EICU energizes 115VAC 3-phase to TRCU.",
                    ),
                    TimedTransitionSpec(
                        signal_id="eicu_cmd3",
                        start_s=2.1, end_s=2.2,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="EICU CMD3 S-R latch sets at deploy entry.",
                    ),
                    TimedTransitionSpec(
                        signal_id="tr_command3_enable",
                        start_s=2.2, end_s=2.3,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="TRCU-internal gated enable asserts (no over-temp, not yet stowed-locked).",
                    ),
                    TimedTransitionSpec(
                        signal_id="tr_position_percent",
                        start_s=2.3, end_s=5.0,
                        start_value=0.0, end_value=100.0,
                        unit="percent",
                        note="Actuator deploys over 2-3s (Step 3).",
                    ),
                    TimedTransitionSpec(
                        signal_id="tra_deg",
                        start_s=4.0, end_s=5.5,
                        start_value=SW1_WINDOW_DEEP_REVERSE_DEG,
                        end_value=TRA_REVERSE_IDLE_THRESHOLD_DEG,
                        unit="deg",
                        note="Pilot advances throttle to reverse idle (-11.74°) after TR_Deployed.",
                    ),
                    TimedTransitionSpec(
                        signal_id="fadec_deploy_command",
                        start_s=5.5, end_s=5.6,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="FADEC CMD1 asserts: all conditions met.",
                    ),
                    TimedTransitionSpec(
                        signal_id="n1k_percent",
                        start_s=5.6, end_s=10.6,
                        start_value=25.0, end_value=75.0,
                        unit="percent",
                        note="N1k ramps reverse-idle→max over ~5s (Step 5).",
                    ),
                ),
                completion_condition=(
                    "eicu_cmd2 == 1 and eicu_cmd3 == 1 and tr_command3_enable == 1 "
                    "and fadec_deploy_command == 1 and tr_position_percent >= 80.0"
                ),
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="tr_inhibited", value=0, unit="state",
                        note="TR_Inhibited clear throughout nominal deploy.",
                    ),
                    SteadySignalSpec(
                        signal_id="engine_running", value=1, unit="state",
                        note="Engine at or above idle.",
                    ),
                    SteadySignalSpec(
                        signal_id="tr_wow", value=1, unit="state",
                        note="TR_WOW latched true after 2.25s filter.",
                    ),
                    SteadySignalSpec(
                        signal_id="e_tras_over_temp_fault", value=0, unit="state",
                        note="No over-temperature during nominal deploy.",
                    ),
                ),
            ),
            # --- Scenario 2: nominal landing stow (Step 6-10) ---
            AcceptanceScenarioSpec(
                id="nominal_landing_stow",
                label="Nominal Landing Stow (Step 6-10)",
                description=(
                    "Pilot returns throttle from reverse idle to 0° (TRA=stow). N1k "
                    "ramps down ~7.5s. Deploy command withdraws; stow command asserts. "
                    "TR_Position returns 100→0% over ~3s. PLS locks and stowed-locked "
                    "persistence of 1s resets EICU CMD3 latch. Total max→fully-stowed ~11s."
                ),
                time_scale_factor=1.0,
                total_duration_s=14.0,
                monitored_signal_ids=(
                    "tra_deg",
                    "n1k_percent",
                    "tr_position_percent",
                    "fadec_deploy_command",
                    "fadec_stow_command",
                    "eicu_cmd3",
                    "tr_command3_enable",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="tra_deg",
                        start_s=0.0, end_s=0.5,
                        start_value=TRA_REVERSE_IDLE_THRESHOLD_DEG,
                        end_value=TRA_STOW_POSITION_DEG,
                        unit="deg",
                        note="Pilot moves throttle to 0° (stow position).",
                    ),
                    TimedTransitionSpec(
                        signal_id="n1k_percent",
                        start_s=0.5, end_s=8.0,
                        start_value=75.0, end_value=25.0,
                        unit="percent",
                        note="N1k ramps down ~7.5s (Step 6).",
                    ),
                    TimedTransitionSpec(
                        signal_id="fadec_deploy_command",
                        start_s=0.5, end_s=0.6,
                        start_value=1.0, end_value=0.0,
                        unit="state",
                        note="Deploy command withdraws as TRA returns to FWD.",
                    ),
                    TimedTransitionSpec(
                        signal_id="fadec_stow_command",
                        start_s=8.0, end_s=8.1,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="Stow command asserts when TRA≥-1.4° AND N1k<stow limit.",
                    ),
                    TimedTransitionSpec(
                        signal_id="tr_position_percent",
                        start_s=8.1, end_s=11.1,
                        start_value=100.0, end_value=0.0,
                        unit="percent",
                        note="Actuator retracts 100→0% over ~3s (Step 8).",
                    ),
                    TimedTransitionSpec(
                        signal_id="tr_command3_enable",
                        start_s=12.1, end_s=12.2,
                        start_value=1.0, end_value=0.0,
                        unit="state",
                        note="Stowed-locked confirmed 1s — TR_Command3_Enable resets.",
                    ),
                    TimedTransitionSpec(
                        signal_id="eicu_cmd3",
                        start_s=12.2, end_s=12.3,
                        start_value=1.0, end_value=0.0,
                        unit="state",
                        note="S-R latch reset by stowed-locked-1s edge.",
                    ),
                ),
                completion_condition=(
                    "fadec_deploy_command == 0 and fadec_stow_command == 1 "
                    "and tr_position_percent <= 5.0 and eicu_cmd3 == 0"
                ),
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="mlg_wow", value=1, unit="state",
                        note="Still on ground.",
                    ),
                    SteadySignalSpec(
                        signal_id="engine_running", value=1, unit="state",
                        note="Engine still running.",
                    ),
                    SteadySignalSpec(
                        signal_id="tr_inhibited", value=0, unit="state",
                        note="No inhibit.",
                    ),
                ),
            ),
            # --- Scenario 3: TR_Inhibited block ---
            AcceptanceScenarioSpec(
                id="tr_inhibited_block",
                label="TR_Inhibited Blocks Deploy",
                description=(
                    "A/C bus asserts TR_Inhibited=TRUE. Even with correct ground + "
                    "throttle into reverse, EICU CMD2 must remain 0 and the full deploy "
                    "chain is blocked (PDF §1.1.1 ②)."
                ),
                time_scale_factor=1.0,
                total_duration_s=6.0,
                monitored_signal_ids=(
                    "tr_inhibited",
                    "mlg_wow",
                    "atltla",
                    "eicu_cmd2",
                    "eicu_cmd3",
                    "fadec_deploy_command",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="mlg_wow",
                        start_s=0.0, end_s=0.1,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="Touchdown.",
                    ),
                    TimedTransitionSpec(
                        signal_id="atltla",
                        start_s=1.0, end_s=1.1,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="Throttle into SW1 window.",
                    ),
                ),
                completion_condition=(
                    "eicu_cmd2 == 0 and eicu_cmd3 == 0 and fadec_deploy_command == 0"
                ),
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="tr_inhibited", value=1, unit="state",
                        note="A/C-bus inhibit asserted throughout this scenario.",
                    ),
                    SteadySignalSpec(
                        signal_id="engine_running", value=1, unit="state",
                        note="Engine running.",
                    ),
                ),
            ),
            # --- Scenario 4: rejected takeoff (RTO) ---
            AcceptanceScenarioSpec(
                id="rejected_takeoff_deploy",
                label="Rejected Takeoff (RTO) Rapid Deploy",
                description=(
                    "MLG_WOW=1 throughout. Pilot aborts takeoff at ~80kt: TRA slams "
                    "from forward takeoff setting to reverse idle in <1s. TR deploys "
                    "rapidly with all latches transitioning in compressed timeline."
                ),
                time_scale_factor=0.6,
                total_duration_s=8.0,
                monitored_signal_ids=(
                    "tra_deg",
                    "atltla",
                    "apwtla",
                    "tr_position_percent",
                    "eicu_cmd2",
                    "eicu_cmd3",
                    "fadec_deploy_command",
                    "n1k_percent",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="tra_deg",
                        start_s=0.0, end_s=0.8,
                        start_value=+8.0, end_value=TRA_REVERSE_IDLE_THRESHOLD_DEG,
                        unit="deg",
                        note="Rapid throttle slam from +8° to -11.74°.",
                    ),
                    TimedTransitionSpec(
                        signal_id="atltla",
                        start_s=0.4, end_s=0.5,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="SW1 closes first (passing through its window).",
                    ),
                    TimedTransitionSpec(
                        signal_id="apwtla",
                        start_s=0.6, end_s=0.7,
                        start_value=0.0, end_value=1.0,
                        unit="state",
                        note="SW2 closes (passing through [-5°, -9.8°] window).",
                    ),
                    TimedTransitionSpec(
                        signal_id="tr_position_percent",
                        start_s=0.8, end_s=3.0,
                        start_value=0.0, end_value=100.0,
                        unit="percent",
                        note="Fast RTO deploy.",
                    ),
                    TimedTransitionSpec(
                        signal_id="n1k_percent",
                        start_s=2.0, end_s=5.0,
                        start_value=70.0, end_value=85.0,
                        unit="percent",
                        note="N1k climbs rapidly for max reverse thrust.",
                    ),
                ),
                completion_condition=(
                    "fadec_deploy_command == 1 and tr_position_percent >= 80.0"
                ),
                steady_signals=(
                    SteadySignalSpec(signal_id="mlg_wow", value=1, unit="state",
                                     note="Aircraft always on runway in RTO."),
                    SteadySignalSpec(signal_id="tr_inhibited", value=0, unit="state",
                                     note="Not inhibited during RTO."),
                    SteadySignalSpec(signal_id="engine_running", value=1, unit="state",
                                     note="Engines running."),
                    SteadySignalSpec(signal_id="tr_wow", value=1, unit="state",
                                     note="WOW firmly established before RTO."),
                ),
            ),
        ),
        fault_modes=(
            # Fault 1: TR stuck deployed
            FaultModeSpec(
                id="tr_stuck_deployed",
                target_component_id="tr_position_percent",
                fault_kind="stuck_high",
                symptom=(
                    "TRA has returned to FWD region (>-1.4°) and stow command is "
                    "asserted, but tr_position_percent remains ≥80% — actuator fails "
                    "to retract. Aircraft cannot safely accelerate post-landing."
                ),
                reasoning_scope_component_ids=(
                    "tra_deg",
                    "fadec_deploy_command",
                    "fadec_stow_command",
                    "tr_position_percent",
                    "lock_state",
                    "n1k_percent",
                ),
                expected_diagnostic_sections=("symptoms", "blocked_logic", "repair_hint"),
                optimization_prompt=(
                    "Consider adding a mechanical secondary retract spring or "
                    "cross-channel VDT plausibility to catch actuator mechanical jam earlier."
                ),
            ),
            # Fault 2: Lock sensor fallback failure
            FaultModeSpec(
                id="lock_sensor_fallback_failure",
                target_component_id="lock_state",
                fault_kind="open_circuit",
                symptom=(
                    "Both sensors (A and B) on TLS (or one pylon) are invalid. "
                    "The 400ms lock-unlock fallback path cannot confirm unlocked, "
                    "so FADEC Deploy Command never asserts. Deploy intent stalls."
                ),
                reasoning_scope_component_ids=(
                    "lock_state",
                    "tr_command3_enable",
                    "fadec_deploy_command",
                ),
                expected_diagnostic_sections=("symptoms", "upstream_checks", "repair_hint"),
                optimization_prompt=(
                    "PDF §1.1.3 ③ defines the ≥1/2 fallback; consider adding a third "
                    "independent proximity sensor on safety-critical locks to survive "
                    "dual-sensor-channel loss."
                ),
            ),
            # Fault 3: Over-temp emergency stop
            FaultModeSpec(
                id="e_tras_over_temp_emergency",
                target_component_id="e_tras_over_temp_fault",
                fault_kind="stuck_high",
                symptom=(
                    "TRCU reports over-temperature fault during deploy. "
                    "TR_Command3_Enable drops to 0 even though EICU CMD3 is latched. "
                    "FADEC withdraws Deploy Command; actuator may freeze mid-travel."
                ),
                reasoning_scope_component_ids=(
                    "e_tras_over_temp_fault",
                    "eicu_cmd3",
                    "tr_command3_enable",
                    "fadec_deploy_command",
                    "tr_position_percent",
                ),
                expected_diagnostic_sections=("symptoms", "blocked_logic", "repair_hint"),
                optimization_prompt=(
                    "Consider adding active TRCU cooling or a staged derate "
                    "(reduce N1k limit instead of hard-stopping) to preserve "
                    "landing safety margin during partial thermal events."
                ),
            ),
            # Fault 4: MLG_WOW redundancy disagree
            FaultModeSpec(
                id="mlg_wow_redundancy_disagree",
                target_component_id="mlg_wow",
                fault_kind="command_path_failure",
                symptom=(
                    "LGCU1 reports WOW=1, LGCU2 reports WOW=0 (or vice versa), both "
                    "marked valid. Conservative policy selects FALSE — aircraft is "
                    "treated as airborne, EICU CMD2 refuses to energize, deploy blocked."
                ),
                reasoning_scope_component_ids=(
                    "mlg_wow",
                    "eicu_cmd2",
                    "eicu_cmd3",
                    "fadec_deploy_command",
                ),
                expected_diagnostic_sections=("symptoms", "redundancy_analysis", "repair_hint"),
                optimization_prompt=(
                    "Consider a third-party ground-proximity corroboration "
                    "(radio altitude <5ft, ground speed match) to disambiguate "
                    "LGCU1/LGCU2 conflicts instead of failing safe to airborne."
                ),
            ),
            # Fault 5: VDT sensor bias low
            FaultModeSpec(
                id="vdt_sensor_bias_low",
                target_component_id="tr_position_percent",
                fault_kind="bias_low",
                symptom=(
                    "Actuator has physically extended past 80% but VDT reads <80% "
                    "due to sensor bias. FADEC Deploy Command refuses to assert "
                    "because tr_position_percent does not satisfy the 0.5s≥80% confirm. "
                    "N1k cannot ramp to max reverse thrust."
                ),
                reasoning_scope_component_ids=(
                    "tr_position_percent",
                    "fadec_deploy_command",
                    "tr_command3_enable",
                ),
                expected_diagnostic_sections=("symptoms", "upstream_checks", "repair_hint"),
                optimization_prompt=(
                    "Cross-check VDT against discrete limit switches on actuator stroke; "
                    "a large delta between analog and discrete senses indicates bias."
                ),
            ),
        ),
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=(
                "system_id",
                "scenario_id",
                "fault_mode_id",
                "observed_symptoms",
                "evidence_links",
                "tr_position_at_fault",
                "tra_at_fault",
                "n1k_at_fault",
                "mlg_wow_at_fault",
                "eicu_cmd3_at_fault",
            ),
            resolution_fields=(
                "confirmed_root_cause",
                "repair_action",
                "actuator_replaced",
                "lock_sensor_recalibrated",
                "vdt_recalibrated",
                "trcu_cooling_serviced",
                "validation_after_fix",
                "residual_risk",
            ),
            optimization_fields=(
                "suggested_logic_change",
                "reliability_gain_hypothesis",
                "redundancy_reduction_or_guardrail_note",
                "persistence_time_adjustment",
                "n1k_limit_adjustment",
            ),
        ),
        tags=(
            "c919",
            "e-tras",
            "thrust-reverser",
            "aviation",
            "redundant-sensors",
            "p34",
        ),
    )
    return workbench_spec_to_dict(spec)


# ---------------------------------------------------------------------------
# Controller adapter class
# ---------------------------------------------------------------------------
class C919ETRASControllerAdapter:
    """
    Truth adapter for the C919 E-TRAS control system.

    Derives EICU CMD2, EICU CMD3 (S-R latch), TR_Command3_Enable, FADEC Deploy
    Command, and FADEC Stow Command from the snapshot. All snapshot fields are
    required — see module docstring for the contract.
    """
    metadata = C919_ETRAS_CONTROLLER_METADATA

    def load_spec(self) -> dict[str, Any]:
        return build_c919_etras_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        # ---- Extract raw signals ----
        lgcu1_value = _snapshot_bool(snapshot, "lgcu1_mlg_wow_value")
        lgcu1_valid = _snapshot_bool(snapshot, "lgcu1_mlg_wow_valid")
        lgcu2_value = _snapshot_bool(snapshot, "lgcu2_mlg_wow_value")
        lgcu2_valid = _snapshot_bool(snapshot, "lgcu2_mlg_wow_valid")
        tr_inhibited = _snapshot_bool(snapshot, "tr_inhibited")

        tra_deg = _snapshot_float(snapshot, "tra_deg")
        atltla = _snapshot_bool(snapshot, "atltla")
        apwtla = _snapshot_bool(snapshot, "apwtla")

        tr_position_percent = _snapshot_float(snapshot, "tr_position_percent")
        _vdt_sensor_valid = _snapshot_bool(snapshot, "vdt_sensor_valid")  # extracted for completeness
        e_tras_over_temp_fault = _snapshot_bool(snapshot, "e_tras_over_temp_fault")
        trcu_power_on = _snapshot_bool(snapshot, "trcu_power_on")

        engine_running = _snapshot_bool(snapshot, "engine_running")
        n1k_percent = _snapshot_float(snapshot, "n1k_percent")
        tr_wow = _snapshot_bool(snapshot, "tr_wow")

        # Persistence / latch state
        comm2_timer_s = _snapshot_float(snapshot, "comm2_timer_s")
        tr_position_deployed_confirm_s = _snapshot_float(snapshot, "tr_position_deployed_confirm_s")
        tr_stowed_locked_confirm_s = _snapshot_float(snapshot, "tr_stowed_locked_confirm_s")
        lock_unlock_confirm_s = _snapshot_float(snapshot, "lock_unlock_confirm_s")
        prev_eicu_cmd3 = _snapshot_bool(snapshot, "prev_eicu_cmd3")

        # ---- Derived signals ----
        mlg_wow = _select_mlg_wow(lgcu1_value, lgcu1_valid, lgcu2_value, lgcu2_valid)
        tls_unlocked = _tls_unlocked_confirmed(snapshot)
        pylon_unlocked = _pylon_locks_unlocked_confirmed(snapshot)
        pls_locked = _pls_both_locked(snapshot)

        # Aggregate lock state (required by component)
        if pls_locked and tr_position_percent < 5.0:
            lock_state = "LOCKED"
        elif tls_unlocked and pylon_unlocked:
            lock_state = "UNLOCKED_CONFIRMED"
        elif tls_unlocked or pylon_unlocked:
            lock_state = "PARTIAL"
        else:
            lock_state = "UNKNOWN"

        # ---- EICU CMD2 (LN1) ----
        eicu_cmd2 = (
            (atltla or apwtla)
            and mlg_wow
            and not tr_inhibited
        )

        # ---- EICU CMD3 (LN2, S-R latch) ----
        set_cmd3 = (
            atltla
            and mlg_wow
            and engine_running
            and not tr_inhibited
        )
        # Reset: stowed-locked confirmed for 1s OR TR_Inhibited asserted
        reset_cmd3 = (
            tr_stowed_locked_confirm_s >= TR_STOWED_LOCKED_CONFIRM_S
            or tr_inhibited
        )
        if reset_cmd3:
            eicu_cmd3 = False
        elif set_cmd3:
            eicu_cmd3 = True
        else:
            eicu_cmd3 = prev_eicu_cmd3  # hold

        # ---- TR_Command3_Enable (LN3) ----
        stowed_locked_1s = tr_stowed_locked_confirm_s >= TR_STOWED_LOCKED_CONFIRM_S
        tr_command3_enable = (
            eicu_cmd3
            and not e_tras_over_temp_fault
            and tra_deg < TRA_FWD_IDLE_THRESHOLD_DEG
            and not stowed_locked_1s
        )

        # ---- FADEC Deploy Command (LN4) ----
        tr_deployed_confirmed = (
            tr_position_percent >= TR_DEPLOYED_POSITION_PERCENT
            and tr_position_deployed_confirm_s >= CONFIRMATION_0_5_S
        )
        lock_unlock_confirmed = (
            tls_unlocked
            and pylon_unlocked
            and lock_unlock_confirm_s >= LOCK_CONFIRMATION_400MS_S
        )
        n1k_in_deploy_envelope = n1k_percent < MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT

        fadec_deploy_command = (
            tr_command3_enable
            and lock_unlock_confirmed
            and tr_deployed_confirmed
            and engine_running
            and n1k_in_deploy_envelope
            and tr_wow
            and tra_deg <= TRA_REVERSE_IDLE_THRESHOLD_DEG
        )

        # ---- FADEC Stow Command (LN5) ----
        n1k_below_stow_limit = n1k_percent < MAX_N1K_STOW_LIMIT_PERCENT
        fadec_stow_command = (
            tra_deg >= TRA_FWD_IDLE_THRESHOLD_DEG
            and n1k_below_stow_limit
            and engine_running
            and not fadec_deploy_command
        )

        # ---- Active logic nodes ----
        active_logic_node_ids: list[str] = []
        if eicu_cmd2:
            active_logic_node_ids.append("ln_eicu_cmd2")
        if eicu_cmd3:
            active_logic_node_ids.append("ln_eicu_cmd3")
        if tr_command3_enable:
            active_logic_node_ids.append("ln_tr_command3_enable")
        if fadec_deploy_command:
            active_logic_node_ids.append("ln_fadec_deploy_command")
        if fadec_stow_command:
            active_logic_node_ids.append("ln_fadec_stow_command")

        # ---- Blocked reasons (most-actionable first) ----
        blocked_reasons: list[str] = []
        if tr_inhibited:
            blocked_reasons.append(
                "TR_Inhibited is TRUE — A/C bus blocks all thrust-reverser activation."
            )
        if not mlg_wow:
            blocked_reasons.append(
                "MLG_WOW is FALSE (LGCU1/LGCU2 redundancy) — aircraft treated as airborne; "
                "deploy chain blocked."
            )
        if e_tras_over_temp_fault:
            blocked_reasons.append(
                "E-TRAS over-temperature fault asserted — TR_Command3_Enable forced 0, "
                "FADEC Deploy withdrawn."
            )
        if not engine_running:
            blocked_reasons.append("Engine not running — deploy command gate fails.")
        if eicu_cmd3 and not tr_command3_enable and tra_deg >= TRA_FWD_IDLE_THRESHOLD_DEG:
            blocked_reasons.append(
                f"TRA ({tra_deg:.2f}°) at or above FWD idle ({TRA_FWD_IDLE_THRESHOLD_DEG}°) "
                f"— TR_Command3_Enable cannot latch."
            )
        if eicu_cmd3 and tr_command3_enable and not lock_unlock_confirmed:
            blocked_reasons.append(
                f"Lock-unlock fallback not confirmed for ≥{LOCK_CONFIRMATION_400MS_S}s "
                f"(tls={tls_unlocked}, pylon={pylon_unlocked}, confirm_s={lock_unlock_confirm_s:.3f})."
            )
        if eicu_cmd3 and tr_command3_enable and not tr_deployed_confirmed:
            blocked_reasons.append(
                f"TR_Position {tr_position_percent:.1f}% has not held ≥{TR_DEPLOYED_POSITION_PERCENT}% "
                f"for ≥{CONFIRMATION_0_5_S}s (confirm_s={tr_position_deployed_confirm_s:.3f})."
            )
        if (
            eicu_cmd3 and tr_command3_enable
            and not n1k_in_deploy_envelope
        ):
            blocked_reasons.append(
                f"N1k {n1k_percent:.1f}% at/above deploy limit "
                f"{MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT}% — FADEC Deploy gate fails."
            )
        if eicu_cmd3 and tr_command3_enable and not tr_wow:
            blocked_reasons.append(
                "TR_WOW (2.25s-TRUE / 120ms-FALSE filtered) not asserted — FADEC Deploy gate fails."
            )
        if eicu_cmd3 and tr_command3_enable and tra_deg > TRA_REVERSE_IDLE_THRESHOLD_DEG:
            blocked_reasons.append(
                f"TRA ({tra_deg:.2f}°) above reverse idle ({TRA_REVERSE_IDLE_THRESHOLD_DEG}°) "
                f"— FADEC Deploy Command does not assert."
            )

        # ---- Completion ----
        completion_reached = (
            eicu_cmd2
            and eicu_cmd3
            and tr_command3_enable
            and fadec_deploy_command
            and tr_position_percent >= TR_DEPLOYED_POSITION_PERCENT
        )

        summary = (
            "E-TRAS fully deployed: CMD2+CMD3+Command3_Enable+FADEC_Deploy all asserted, "
            f"TR_Position={tr_position_percent:.1f}%."
            if completion_reached
            else f"E-TRAS not deployed ({len(blocked_reasons)} blocker(s))."
        )

        return GenericTruthEvaluation(
            system_id=C919_ETRAS_SYSTEM_ID,
            active_logic_node_ids=tuple(active_logic_node_ids),
            asserted_component_values={
                "mlg_wow": mlg_wow,
                "tr_inhibited": tr_inhibited,
                "tra_deg": tra_deg,
                "atltla": atltla,
                "apwtla": apwtla,
                "tr_position_percent": tr_position_percent,
                "lock_state": lock_state,
                "engine_running": engine_running,
                "n1k_percent": n1k_percent,
                "tr_wow": tr_wow,
                "trcu_power_on": trcu_power_on,
                "e_tras_over_temp_fault": e_tras_over_temp_fault,
                "eicu_cmd2": eicu_cmd2,
                "eicu_cmd3": eicu_cmd3,
                "tr_command3_enable": tr_command3_enable,
                "fadec_deploy_command": fadec_deploy_command,
                "fadec_stow_command": fadec_stow_command,
            },
            completion_reached=completion_reached,
            blocked_reasons=tuple(blocked_reasons),
            summary=summary,
        )


def build_c919_etras_controller_adapter() -> C919ETRASControllerAdapter:
    """Factory function — call this to get a ready-to-use adapter instance."""
    return C919ETRASControllerAdapter()

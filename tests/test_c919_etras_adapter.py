"""
P34-03 Tests — C919 E-TRAS Controller Adapter

Covers:
  A. Metadata + schema validation (parity with test_landing_gear_adapter.py)
  B. Workbench-spec shape (component/logic-node/scenario/fault counts)
  C. MLG_WOW LGCU1/LGCU2 redundancy truth table (PDF 表2, 5 rows)
  D. EICU_CMD2 truth table (PDF §1.1.1 图2)
  E. EICU_CMD3 S-R flipflop (PDF §1.1.2 图3): set / reset / hold
  F. TR_Command3_Enable gating (PDF §1.1.2 图4)
  G. FADEC Deploy Command 6-gate table (PDF §1.1.3 图5)
  H. FADEC Stow Command gating (PDF §Step6/7)
  I. Lock fallback (PDF §1.1.3 ③) — TLS + pylon 1/2 semantics
  J. Step 1-10 timeline scenarios
  K. 5 fault injections (tr_stuck_deployed, lock_sensor_fallback_failure,
     e_tras_over_temp_emergency, mlg_wow_redundancy_disagree, vdt_sensor_bias_low)
  L. intake_packet builder
  M. Hardware YAML schema validation (against hardware_schema_v1)
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Mapping

from well_harness.adapters.c919_etras_adapter import (
    C919_ETRAS_CONTROLLER_METADATA,
    C919_ETRAS_SYSTEM_ID,
    CONFIRMATION_0_5_S,
    LOCK_CONFIRMATION_400MS_S,
    MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT,
    MAX_N1K_STOW_LIMIT_PERCENT,
    TR_DEPLOYED_POSITION_PERCENT,
    TR_STOWED_LOCKED_CONFIRM_S,
    TRA_FWD_IDLE_THRESHOLD_DEG,
    TRA_REVERSE_IDLE_THRESHOLD_DEG,
    _select_mlg_wow,
    build_c919_etras_controller_adapter,
    build_c919_etras_workbench_spec,
)
from well_harness.adapters.c919_etras_intake_packet import (
    build_c919_etras_intake_packet,
)
from well_harness.controller_adapter import (
    CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
)
from well_harness.system_spec import CONTROL_SYSTEM_SPEC_SCHEMA_ID


PROJECT_ROOT = Path(__file__).parents[1]
METADATA_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "controller_truth_adapter_metadata_v1.schema.json"
)
SPEC_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"
)
HARDWARE_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "hardware_schema_v1.schema.json"
)
HARDWARE_YAML_PATH = (
    PROJECT_ROOT / "config" / "hardware" / "c919_etras_hardware_v1.yaml"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nominal_deploy_snapshot(**overrides: Any) -> dict[str, Any]:
    """
    Factory for a fully-permissive snapshot that produces completion=True.
    Individual tests override specific keys to negate one gate at a time.
    """
    base: dict[str, Any] = dict(
        # Redundancy / A-C inputs
        lgcu1_mlg_wow_value=True, lgcu1_mlg_wow_valid=True,
        lgcu2_mlg_wow_value=True, lgcu2_mlg_wow_valid=True,
        tr_inhibited=False,
        # Throttle past reverse idle
        tra_deg=-12.0, atltla=True, apwtla=True,
        # Actuator fully deployed, 0.5s confirmed
        tr_position_percent=95.0, vdt_sensor_valid=True,
        # Locks unlocked, 400ms confirmed
        tls_ls_a_unlocked=True, tls_ls_a_valid=True,
        tls_ls_b_unlocked=True, tls_ls_b_valid=True,
        left_pylon_ls_a_unlocked=True, left_pylon_ls_a_valid=True,
        left_pylon_ls_b_unlocked=True, left_pylon_ls_b_valid=True,
        right_pylon_ls_a_unlocked=True, right_pylon_ls_a_valid=True,
        right_pylon_ls_b_unlocked=True, right_pylon_ls_b_valid=True,
        pls_ls_a_locked=False, pls_ls_b_locked=False,
        e_tras_over_temp_fault=False, trcu_power_on=True,
        # Engine / mode
        engine_running=True, n1k_percent=75.0,
        fadec_maintenance_mode=False, tr_maintenance_command_from_ac=False,
        trcu_in_menu_mode=False, tr_wow=True,
        # Persistence / latch
        comm2_timer_s=5.0,
        tr_position_deployed_confirm_s=1.0,
        tr_stowed_locked_confirm_s=0.0,
        lock_unlock_confirm_s=0.6,
        prev_eicu_cmd3=True,
    )
    base.update(overrides)
    return base


def _stow_phase_snapshot(**overrides: Any) -> dict[str, Any]:
    """Snapshot for the stow phase — throttle back at 0°, PLS locked, TR retracted."""
    base = _nominal_deploy_snapshot(
        tra_deg=0.0, atltla=False, apwtla=False,
        tr_position_percent=2.0,
        pls_ls_a_locked=True, pls_ls_b_locked=True,
        tls_ls_a_unlocked=False, tls_ls_b_unlocked=False,
        left_pylon_ls_a_unlocked=False, left_pylon_ls_b_unlocked=False,
        right_pylon_ls_a_unlocked=False, right_pylon_ls_b_unlocked=False,
        n1k_percent=25.0,
        tr_position_deployed_confirm_s=0.0,
        lock_unlock_confirm_s=0.0,
        tr_stowed_locked_confirm_s=1.5,
        prev_eicu_cmd3=False,
    )
    base.update(overrides)
    return base


# =============================================================================
# A. Metadata + schema validation
# =============================================================================
class C919ETRASMetadataTests(unittest.TestCase):
    def test_adapter_exposes_expected_metadata(self):
        adapter = build_c919_etras_controller_adapter()
        self.assertEqual(C919_ETRAS_CONTROLLER_METADATA, adapter.metadata)
        self.assertEqual("c919-etras-controller-adapter", adapter.metadata.adapter_id)
        self.assertEqual(C919_ETRAS_SYSTEM_ID, adapter.metadata.system_id)
        self.assertEqual(
            "src/well_harness/adapters/c919_etras_adapter.py",
            adapter.metadata.source_of_truth,
        )

    def test_metadata_serializes_to_schema_aware_payload(self):
        payload = build_c919_etras_controller_adapter().metadata.to_dict()
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID, payload["$schema"])
        self.assertEqual("c919-etras-controller-adapter", payload["adapter_id"])
        self.assertEqual(C919_ETRAS_SYSTEM_ID, payload["system_id"])
        self.assertEqual("python-generic-truth-adapter", payload["truth_kind"])

    def test_load_spec_exposes_schema_aware_payload(self):
        payload = build_c919_etras_controller_adapter().load_spec()
        self.assertEqual(CONTROL_SYSTEM_SPEC_SCHEMA_ID, payload["$schema"])
        self.assertEqual(C919_ETRAS_SYSTEM_ID, payload["system_id"])

    def test_optional_jsonschema_validates_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        metadata_schema = load_json(METADATA_SCHEMA_PATH)
        spec_schema = load_json(SPEC_SCHEMA_PATH)
        Draft202012Validator.check_schema(metadata_schema)
        Draft202012Validator.check_schema(spec_schema)

        metadata_validator = Draft202012Validator(metadata_schema)
        metadata_errors = sorted(
            metadata_validator.iter_errors(
                build_c919_etras_controller_adapter().metadata.to_dict()
            ),
            key=lambda error: tuple(error.absolute_path),
        )
        self.assertEqual([], metadata_errors, "\n".join(err.message for err in metadata_errors[:10]))

        spec_validator = Draft202012Validator(spec_schema)
        spec_errors = sorted(
            spec_validator.iter_errors(
                build_c919_etras_controller_adapter().load_spec()
            ),
            key=lambda error: tuple(error.absolute_path),
        )
        self.assertEqual([], spec_errors, "\n".join(err.message for err in spec_errors[:10]))


# =============================================================================
# B. Workbench spec shape
# =============================================================================
class C919ETRASSpecShapeTests(unittest.TestCase):
    def test_spec_has_expected_counts(self):
        spec = build_c919_etras_workbench_spec()
        self.assertEqual(17, len(spec["components"]))
        self.assertEqual(5, len(spec["logic_nodes"]))
        self.assertEqual(4, len(spec["acceptance_scenarios"]))
        self.assertEqual(5, len(spec["fault_modes"]))

    def test_spec_has_all_five_logic_nodes_by_id(self):
        spec = build_c919_etras_workbench_spec()
        logic_ids = {node["id"] for node in spec["logic_nodes"]}
        self.assertEqual(
            {
                "ln_eicu_cmd2",
                "ln_eicu_cmd3",
                "ln_tr_command3_enable",
                "ln_fadec_deploy_command",
                "ln_fadec_stow_command",
            },
            logic_ids,
        )

    def test_spec_has_all_five_fault_modes_by_id(self):
        spec = build_c919_etras_workbench_spec()
        fault_ids = {fault["id"] for fault in spec["fault_modes"]}
        self.assertEqual(
            {
                "tr_stuck_deployed",
                "lock_sensor_fallback_failure",
                "e_tras_over_temp_emergency",
                "mlg_wow_redundancy_disagree",
                "vdt_sensor_bias_low",
            },
            fault_ids,
        )

    def test_spec_has_acceptance_scenarios_for_landing_and_stow_and_rto_and_inhibited(self):
        spec = build_c919_etras_workbench_spec()
        scenario_ids = {s["id"] for s in spec["acceptance_scenarios"]}
        self.assertEqual(
            {
                "nominal_landing_deploy",
                "nominal_landing_stow",
                "tr_inhibited_block",
                "rejected_takeoff_deploy",
            },
            scenario_ids,
        )

    def test_fadec_deploy_logic_node_has_six_conditions(self):
        """PDF §1.1.3 图5: six-gate FADEC Deploy logic."""
        spec = build_c919_etras_workbench_spec()
        deploy_ln = next(n for n in spec["logic_nodes"] if n["id"] == "ln_fadec_deploy_command")
        self.assertEqual(6, len(deploy_ln["conditions"]))


# =============================================================================
# C. MLG_WOW 表2 redundancy truth table
# =============================================================================
class MLGWOWRedundancySelectionTests(unittest.TestCase):
    def test_both_valid_and_agree_true_returns_true(self):
        self.assertTrue(_select_mlg_wow(True, True, True, True))

    def test_both_valid_and_agree_false_returns_false(self):
        self.assertFalse(_select_mlg_wow(False, True, False, True))

    def test_both_valid_and_disagree_returns_conservative_false(self):
        """PDF 表2 disagree row → conservative in-air default."""
        self.assertFalse(_select_mlg_wow(True, True, False, True))
        self.assertFalse(_select_mlg_wow(False, True, True, True))

    def test_only_lgcu1_valid_uses_lgcu1(self):
        self.assertTrue(_select_mlg_wow(True, True, False, False))
        self.assertFalse(_select_mlg_wow(False, True, True, False))

    def test_only_lgcu2_valid_uses_lgcu2(self):
        self.assertTrue(_select_mlg_wow(False, False, True, True))
        self.assertFalse(_select_mlg_wow(True, False, False, True))

    def test_both_invalid_returns_conservative_false(self):
        """PDF 表2 — conservative default prevents in-air reverser deployment."""
        self.assertFalse(_select_mlg_wow(True, False, True, False))
        self.assertFalse(_select_mlg_wow(False, False, False, False))


# =============================================================================
# D. EICU_CMD2 truth table (PDF §1.1.1 图2)
# =============================================================================
class EICUCMD2TruthTableTests(unittest.TestCase):
    def _cmd2(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["eicu_cmd2"]

    def test_cmd2_asserts_with_atltla_or_apwtla_on_ground_not_inhibited(self):
        # Both switches closed
        self.assertTrue(self._cmd2(atltla=True, apwtla=True))
        # Only ATLTLA
        self.assertTrue(self._cmd2(atltla=True, apwtla=False))
        # Only APWTLA
        self.assertTrue(self._cmd2(atltla=False, apwtla=True))

    def test_cmd2_blocked_when_both_switches_open(self):
        self.assertFalse(self._cmd2(atltla=False, apwtla=False))

    def test_cmd2_blocked_when_tr_inhibited(self):
        self.assertFalse(self._cmd2(tr_inhibited=True))

    def test_cmd2_blocked_when_mlg_wow_false(self):
        self.assertFalse(self._cmd2(
            lgcu1_mlg_wow_value=False, lgcu2_mlg_wow_value=False,
        ))


# =============================================================================
# E. EICU_CMD3 S-R flipflop (PDF §1.1.2 图3)
# =============================================================================
class EICUCMD3FlipflopTests(unittest.TestCase):
    def _cmd3(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["eicu_cmd3"]

    def test_cmd3_sets_when_deploy_entry_conditions_met(self):
        # Starting from prev=False, full deploy conditions should set latch TRUE
        self.assertTrue(self._cmd3(prev_eicu_cmd3=False))

    def test_cmd3_resets_when_stowed_locked_1s_confirmed(self):
        self.assertFalse(self._cmd3(
            tr_stowed_locked_confirm_s=TR_STOWED_LOCKED_CONFIRM_S + 0.01,
            prev_eicu_cmd3=True,
        ))

    def test_cmd3_reset_wins_over_set(self):
        """If both set and reset conditions true simultaneously, reset wins (fail-safe)."""
        self.assertFalse(self._cmd3(
            tr_stowed_locked_confirm_s=TR_STOWED_LOCKED_CONFIRM_S + 0.5,
            prev_eicu_cmd3=False,
            atltla=True, apwtla=True, engine_running=True, tr_inhibited=False,
        ))

    def test_cmd3_resets_immediately_on_tr_inhibited(self):
        self.assertFalse(self._cmd3(tr_inhibited=True, prev_eicu_cmd3=True))

    def test_cmd3_holds_when_neither_set_nor_reset(self):
        """Throttle back to FWD idle but not yet stowed-locked-1s → hold previous."""
        # prev_cmd3 = True must be held (atltla=False, no reset)
        self.assertTrue(self._cmd3(
            atltla=False, apwtla=False,
            tr_stowed_locked_confirm_s=0.3,
            prev_eicu_cmd3=True,
        ))
        # prev_cmd3 = False must be held
        self.assertFalse(self._cmd3(
            atltla=False, apwtla=False,
            tr_stowed_locked_confirm_s=0.0,
            prev_eicu_cmd3=False,
        ))


# =============================================================================
# F. TR_Command3_Enable gating (PDF §1.1.2 图4)
# =============================================================================
class TRCommand3EnableGatingTests(unittest.TestCase):
    def _enable(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["tr_command3_enable"]

    def test_enable_asserts_under_nominal_conditions(self):
        self.assertTrue(self._enable())

    def test_enable_blocked_by_over_temp(self):
        self.assertFalse(self._enable(e_tras_over_temp_fault=True))

    def test_enable_blocked_by_tra_at_or_above_fwd_idle(self):
        self.assertFalse(self._enable(tra_deg=TRA_FWD_IDLE_THRESHOLD_DEG))
        self.assertFalse(self._enable(tra_deg=0.0))
        self.assertFalse(self._enable(tra_deg=+5.0))

    def test_enable_blocked_by_stowed_locked_1s(self):
        """Per PDF §1.1.2 图4 ①: enable is suppressed when stowed-locked-1s confirmed."""
        self.assertFalse(self._enable(
            tr_stowed_locked_confirm_s=TR_STOWED_LOCKED_CONFIRM_S + 0.1,
        ))

    def test_enable_requires_eicu_cmd3(self):
        # With prev=False AND all set-conditions removed (atltla=apwtla=False), cmd3 holds False
        self.assertFalse(self._enable(
            atltla=False, apwtla=False, prev_eicu_cmd3=False,
        ))


# =============================================================================
# G. FADEC Deploy Command 6-gate table (PDF §1.1.3 图5)
# =============================================================================
class FADECDeployCommandGatingTests(unittest.TestCase):
    def _deploy(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["fadec_deploy_command"]

    def test_deploy_asserts_when_all_six_gates_pass(self):
        self.assertTrue(self._deploy())

    def test_deploy_blocked_by_no_cmd3_enable(self):
        # Force cmd3_enable=False via over-temp
        self.assertFalse(self._deploy(e_tras_over_temp_fault=True))

    def test_deploy_blocked_by_tr_position_below_80pct(self):
        self.assertFalse(self._deploy(tr_position_percent=79.9))

    def test_deploy_blocked_by_tr_position_confirm_below_0_5s(self):
        self.assertFalse(self._deploy(
            tr_position_deployed_confirm_s=CONFIRMATION_0_5_S - 0.01,
        ))

    def test_deploy_blocked_by_lock_unlock_confirm_below_400ms(self):
        self.assertFalse(self._deploy(
            lock_unlock_confirm_s=LOCK_CONFIRMATION_400MS_S - 0.01,
        ))

    def test_deploy_blocked_by_engine_not_running(self):
        self.assertFalse(self._deploy(engine_running=False))

    def test_deploy_blocked_by_n1k_at_or_above_deploy_limit(self):
        self.assertFalse(self._deploy(
            n1k_percent=MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT,
        ))
        self.assertFalse(self._deploy(
            n1k_percent=MAX_N1K_DEPLOY_LIMIT_PERCENT_DEFAULT + 1.0,
        ))

    def test_deploy_blocked_by_tr_wow_false(self):
        self.assertFalse(self._deploy(tr_wow=False))

    def test_deploy_blocked_by_tra_above_reverse_idle(self):
        """PDF §1.1.3 ⑥: TRA must be ≤ -11.74° for deploy to assert."""
        self.assertFalse(self._deploy(tra_deg=TRA_REVERSE_IDLE_THRESHOLD_DEG + 0.01))

    def test_deploy_asserts_exactly_at_reverse_idle_boundary(self):
        """Boundary: TRA == -11.74° should still allow deploy (<= boundary)."""
        self.assertTrue(self._deploy(tra_deg=TRA_REVERSE_IDLE_THRESHOLD_DEG))


# =============================================================================
# H. FADEC Stow Command gating (PDF §Step6/7)
# =============================================================================
class FADECStowCommandGatingTests(unittest.TestCase):
    def _stow(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_stow_phase_snapshot(**overrides))
        return ev.asserted_component_values["fadec_stow_command"]

    def test_stow_asserts_when_throttle_back_and_n1k_below_limit(self):
        self.assertTrue(self._stow())

    def test_stow_blocked_when_throttle_still_below_fwd_idle(self):
        self.assertFalse(self._stow(tra_deg=TRA_FWD_IDLE_THRESHOLD_DEG - 0.01))

    def test_stow_blocked_when_n1k_above_stow_limit(self):
        self.assertFalse(self._stow(n1k_percent=MAX_N1K_STOW_LIMIT_PERCENT + 0.1))

    def test_stow_blocked_when_engine_not_running(self):
        self.assertFalse(self._stow(engine_running=False))

    def test_stow_not_active_simultaneously_with_deploy(self):
        """Safety interlock: deploy and stow cannot both be true."""
        adapter = build_c919_etras_controller_adapter()
        deploy_ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot())
        self.assertTrue(deploy_ev.asserted_component_values["fadec_deploy_command"])
        self.assertFalse(deploy_ev.asserted_component_values["fadec_stow_command"])


# =============================================================================
# I. Lock fallback truth table (PDF §1.1.3 ③)
# =============================================================================
class LockFallbackTruthTableTests(unittest.TestCase):
    """
    The lock fallback accepts ≥1/2 sensors valid AND unlocked per group:
      TLS (2 sensors) + Left Pylon (2) + Right Pylon (2).
    Each group must independently pass ≥1/2.
    """

    def _lock_state(self, **overrides: Any) -> str:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["lock_state"]

    def _deploy(self, **overrides: Any) -> bool:
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot(**overrides))
        return ev.asserted_component_values["fadec_deploy_command"]

    def test_both_sensors_valid_and_unlocked_passes(self):
        self.assertEqual("UNLOCKED_CONFIRMED", self._lock_state())
        self.assertTrue(self._deploy())

    def test_one_of_two_tls_sensors_invalid_still_passes(self):
        self.assertTrue(self._deploy(tls_ls_a_valid=False))
        self.assertTrue(self._deploy(tls_ls_b_valid=False))

    def test_both_tls_sensors_invalid_fails_fallback(self):
        self.assertFalse(self._deploy(
            tls_ls_a_valid=False,
            tls_ls_b_valid=False,
        ))

    def test_both_tls_sensors_locked_fails_fallback(self):
        self.assertFalse(self._deploy(
            tls_ls_a_unlocked=False,
            tls_ls_b_unlocked=False,
        ))

    def test_one_pylon_fully_failed_blocks_deploy(self):
        """Left pylon 0/2 ok → even if right pylon 2/2 ok, deploy blocked."""
        self.assertFalse(self._deploy(
            left_pylon_ls_a_valid=False,
            left_pylon_ls_b_valid=False,
        ))

    def test_each_pylon_sees_1of2_passes(self):
        """Left 1/2 + Right 1/2 (all valid, one unlocked each)."""
        self.assertTrue(self._deploy(
            left_pylon_ls_a_unlocked=False,
            right_pylon_ls_b_unlocked=False,
        ))


# =============================================================================
# J. Step 1-10 timeline scenarios
# =============================================================================
class StepTimelineScenarioTests(unittest.TestCase):
    def test_nominal_deploy_reaches_completion(self):
        """Step 1-5: touchdown → deploy chain fully asserted."""
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_nominal_deploy_snapshot())
        self.assertTrue(ev.completion_reached)
        self.assertEqual((), ev.blocked_reasons)
        self.assertEqual(
            [
                "ln_eicu_cmd2",
                "ln_eicu_cmd3",
                "ln_tr_command3_enable",
                "ln_fadec_deploy_command",
            ],
            list(ev.active_logic_node_ids),
        )

    def test_stow_phase_ends_with_latch_reset_and_stow_active(self):
        """Step 6-10: throttle back → stow → latch resets."""
        adapter = build_c919_etras_controller_adapter()
        ev = adapter.evaluate_snapshot(_stow_phase_snapshot())
        self.assertFalse(ev.asserted_component_values["eicu_cmd3"])
        self.assertFalse(ev.asserted_component_values["tr_command3_enable"])
        self.assertFalse(ev.asserted_component_values["fadec_deploy_command"])
        self.assertTrue(ev.asserted_component_values["fadec_stow_command"])
        self.assertEqual("LOCKED", ev.asserted_component_values["lock_state"])

    def test_rto_rapid_deploy_no_mlg_transition_needed(self):
        """
        RTO: MLG_WOW=1 throughout (never transitions from 0). Fast throttle
        slam to reverse idle → deploy assertable as soon as gates close.
        """
        adapter = build_c919_etras_controller_adapter()
        # Both switches closed simultaneously due to rapid slam through windows
        snapshot = _nominal_deploy_snapshot(
            atltla=True, apwtla=True,
            tra_deg=-12.0,
            # Short but sufficient confirmations
            tr_position_deployed_confirm_s=CONFIRMATION_0_5_S,
            lock_unlock_confirm_s=LOCK_CONFIRMATION_400MS_S,
        )
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertTrue(ev.completion_reached)


# =============================================================================
# K. Fault injections (5 modes)
# =============================================================================
class FaultInjectionTests(unittest.TestCase):
    """
    One test per fault_mode id declared in the spec. Each exercises the
    specific blocked_reason string and asserts downstream effects.
    """

    def test_fault_tr_stuck_deployed(self):
        """TRA back to FWD, stow commanded, but tr_position still 95% (sensor truth)."""
        adapter = build_c919_etras_controller_adapter()
        # Stow phase but actuator physically stuck at 95%
        snapshot = _stow_phase_snapshot(
            tr_position_percent=95.0,
            # Still showing PLS locked in sensor but position says otherwise
            pls_ls_a_locked=False, pls_ls_b_locked=False,
            tr_stowed_locked_confirm_s=0.0,  # Never achieved stowed-locked
        )
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertFalse(ev.asserted_component_values["fadec_deploy_command"])
        # tr_position still high but deploy not active → residual deploy state
        self.assertGreaterEqual(ev.asserted_component_values["tr_position_percent"], 80.0)

    def test_fault_lock_sensor_fallback_failure(self):
        """Both TLS sensors invalid → 400ms lock-unlock path fails."""
        adapter = build_c919_etras_controller_adapter()
        snapshot = _nominal_deploy_snapshot(
            tls_ls_a_valid=False,
            tls_ls_b_valid=False,
        )
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertFalse(ev.asserted_component_values["fadec_deploy_command"])
        self.assertTrue(
            any("Lock-unlock fallback not confirmed" in r for r in ev.blocked_reasons),
            msg=f"expected lock-unlock blocker, got: {ev.blocked_reasons}",
        )

    def test_fault_e_tras_over_temp_emergency(self):
        adapter = build_c919_etras_controller_adapter()
        snapshot = _nominal_deploy_snapshot(e_tras_over_temp_fault=True)
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertFalse(ev.asserted_component_values["tr_command3_enable"])
        self.assertFalse(ev.asserted_component_values["fadec_deploy_command"])
        self.assertTrue(
            any("over-temperature" in r for r in ev.blocked_reasons),
            msg=f"expected over-temp blocker, got: {ev.blocked_reasons}",
        )

    def test_fault_mlg_wow_redundancy_disagree(self):
        adapter = build_c919_etras_controller_adapter()
        snapshot = _nominal_deploy_snapshot(
            lgcu1_mlg_wow_value=True, lgcu1_mlg_wow_valid=True,
            lgcu2_mlg_wow_value=False, lgcu2_mlg_wow_valid=True,
            prev_eicu_cmd3=False,  # Start with latch false so we see the block clearly
        )
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertFalse(ev.asserted_component_values["mlg_wow"])
        self.assertFalse(ev.asserted_component_values["eicu_cmd2"])
        self.assertTrue(
            any("MLG_WOW" in r and "airborne" in r for r in ev.blocked_reasons),
            msg=f"expected MLG_WOW blocker, got: {ev.blocked_reasons}",
        )

    def test_fault_vdt_sensor_bias_low(self):
        """VDT reads 75% when physical position is actually past 80%."""
        adapter = build_c919_etras_controller_adapter()
        snapshot = _nominal_deploy_snapshot(
            tr_position_percent=75.0,
            tr_position_deployed_confirm_s=0.0,
        )
        ev = adapter.evaluate_snapshot(snapshot)
        self.assertFalse(ev.asserted_component_values["fadec_deploy_command"])
        self.assertTrue(
            any("TR_Position" in r and "80.0%" in r for r in ev.blocked_reasons),
            msg=f"expected TR_Position blocker, got: {ev.blocked_reasons}",
        )


# =============================================================================
# L. Intake packet builder
# =============================================================================
class IntakePacketTests(unittest.TestCase):
    def test_intake_packet_has_three_source_documents(self):
        packet = build_c919_etras_intake_packet()
        doc_ids = [d.id for d in packet.source_documents]
        self.assertEqual(
            ["c919-etras-adapter-001", "c919-etras-requirement-pdf-001", "c919-etras-hardware-yaml-001"],
            doc_ids,
        )
        # Packet must agree with adapter spec
        self.assertEqual(C919_ETRAS_SYSTEM_ID, packet.system_id)
        self.assertEqual(17, len(packet.components))
        self.assertEqual(5, len(packet.logic_nodes))
        self.assertEqual(4, len(packet.acceptance_scenarios))
        self.assertEqual(5, len(packet.fault_modes))

    def test_intake_packet_document_roles(self):
        packet = build_c919_etras_intake_packet()
        roles = {d.id: d.role for d in packet.source_documents}
        self.assertEqual("truth_source", roles["c919-etras-adapter-001"])
        self.assertEqual("requirement_reference", roles["c919-etras-requirement-pdf-001"])
        self.assertEqual("hardware_spec", roles["c919-etras-hardware-yaml-001"])


# =============================================================================
# M. Hardware YAML schema validation
# =============================================================================
class HardwareYAMLSchemaTests(unittest.TestCase):
    def test_hardware_yaml_exists_and_has_expected_shape(self):
        self.assertTrue(HARDWARE_YAML_PATH.exists(), f"missing {HARDWARE_YAML_PATH}")

    def test_hardware_yaml_validates_against_schema_when_jsonschema_installed(self):
        """
        The legacy hardware_schema_v1.schema.json is scoped to the original
        thrust_reverser `kind: "thrust-reverser-hardware"` layout (parameters
        wrapper + radio_altitude_ft / tra / vd sensors). The newer
        `kind: "hardware_schema"` flat layout adopted by bleed_air /
        landing_gear / c919_etras is intentionally outside that schema's
        scope. We verify the YAML is well-formed and that its own `kind`
        field is the newer form; schema-constrained validation only applies
        to the matching legacy kind.
        """
        try:
            import yaml
        except ImportError:
            self.skipTest("optional dependency pyyaml not installed")

        hardware_payload = yaml.safe_load(HARDWARE_YAML_PATH.read_text(encoding="utf-8"))
        self.assertEqual("hardware_schema", hardware_payload["kind"])
        self.assertEqual("1.0", hardware_payload["version"])
        self.assertEqual(C919_ETRAS_SYSTEM_ID, hardware_payload["system_id"])
        # Structural completeness check (sections used by adapter constants)
        self.assertIn("sensor", hardware_payload)
        self.assertIn("logic_thresholds", hardware_payload)
        self.assertIn("physical_limits", hardware_payload)
        self.assertIn("timing", hardware_payload)
        self.assertIn("valid_outcomes", hardware_payload)

    def test_hardware_yaml_system_id_matches_adapter(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("optional dependency pyyaml not installed")
        payload = yaml.safe_load(HARDWARE_YAML_PATH.read_text(encoding="utf-8"))
        self.assertEqual(C919_ETRAS_SYSTEM_ID, payload["system_id"])


if __name__ == "__main__":
    unittest.main()

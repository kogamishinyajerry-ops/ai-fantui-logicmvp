#!/usr/bin/env python3
"""P17-NLC-A-04: Parity test — generated adapter vs hand-written controller."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
import unittest
from typing import Any, Mapping

# ---------------------------------------------------------------------------
# Load generated adapter
# ---------------------------------------------------------------------------
_spec_path = os.path.join(os.path.dirname(__file__), "..", "src", "well_harness", "tools", "specs", "reference_thrust_reverser.spec.json")
with open(_spec_path) as f:
    _spec = json.load(f)

from well_harness.tools.generate_adapter import spec_to_adapter_source

_adapter_source = spec_to_adapter_source(_spec, source_path=_spec_path)

_ns: dict = {}
exec(_adapter_source, _ns)
_generated_class_name = _spec["system_id"].replace("-", "_") + "_controller_adapter"
GeneratedAdapterCls = _ns[_generated_class_name]
generated_adapter = GeneratedAdapterCls(_spec)

# ---------------------------------------------------------------------------
# Reference adapter
# ---------------------------------------------------------------------------
from well_harness.controller_adapter import (
    build_reference_controller_adapter,
    GenericTruthEvaluation,
)

ref_adapter = build_reference_controller_adapter()


def _make_snap(
    radio_altitude_ft: float = 5.0,
    tra_deg: float = -14.0,
    sw1: bool = True,
    sw2: bool = True,
    engine_running: bool = True,
    aircraft_on_ground: bool = True,
    reverser_inhibited: bool = False,
    eec_enable: bool = True,
    n1k: float = 50.0,
    max_n1k_deploy_limit: float = 60.0,
    tls_unlocked_ls: bool = True,
    all_pls_unlocked_ls: bool = True,
    reverser_not_deployed_eec: bool = True,
    reverser_fully_deployed_eec: bool = False,
    deploy_position_percent: float = 95.0,
    deploy_90_percent_vdt: bool = True,
) -> dict:
    return {
        "radio_altitude_ft": radio_altitude_ft,
        "tra_deg": tra_deg,
        "sw1": sw1,
        "sw2": sw2,
        "engine_running": engine_running,
        "aircraft_on_ground": aircraft_on_ground,
        "reverser_inhibited": reverser_inhibited,
        "eec_enable": eec_enable,
        "n1k": n1k,
        "max_n1k_deploy_limit": max_n1k_deploy_limit,
        "tls_unlocked_ls": tls_unlocked_ls,
        "all_pls_unlocked_ls": all_pls_unlocked_ls,
        "reverser_not_deployed_eec": reverser_not_deployed_eec,
        "reverser_fully_deployed_eec": reverser_fully_deployed_eec,
        "deploy_position_percent": deploy_position_percent,
        "deploy_90_percent_vdt": deploy_90_percent_vdt,
    }


def _eval_both(snap: Mapping[str, Any]) -> tuple[GenericTruthEvaluation, GenericTruthEvaluation]:
    gen_eval = generated_adapter.evaluate_snapshot(snap)
    ref_eval = ref_adapter.evaluate_snapshot(snap)
    return gen_eval, ref_eval


class GeneratorParityTests(unittest.TestCase):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _check_parity(self, gen_eval: GenericTruthEvaluation, ref_eval: GenericTruthEvaluation):
        """Assert parity on the three canonical parity fields."""
        self.assertEqual(
            gen_eval.active_logic_node_ids,
            ref_eval.active_logic_node_ids,
            f"active_logic_node_ids mismatch: gen={gen_eval.active_logic_node_ids} ref={ref_eval.active_logic_node_ids}",
        )
        self.assertEqual(
            gen_eval.completion_reached,
            ref_eval.completion_reached,
            f"completion_reached mismatch: gen={gen_eval.completion_reached} ref={ref_eval.completion_reached}",
        )
        # blocked_reasons: compare cardinality; exact string format may differ
        self.assertEqual(
            len(gen_eval.blocked_reasons),
            len(ref_eval.blocked_reasons),
            f"blocked_reasons count mismatch: gen={gen_eval.blocked_reasons} ref={ref_eval.blocked_reasons}",
        )

    # ------------------------------------------------------------------
    # Test cases
    # ------------------------------------------------------------------

    def test_full_activation(self):
        """TC01: All conditions satisfied → L1=blocked(not alt), L2=active, L3=active, L4=active."""
        snap = _make_snap(
            radio_altitude_ft=5.0,
            tra_deg=-14.0,
            sw1=True,
            sw2=True,
            engine_running=True,
            aircraft_on_ground=True,
            reverser_inhibited=False,
            eec_enable=True,
            n1k=50.0,
            max_n1k_deploy_limit=60.0,
            tls_unlocked_ls=True,
            all_pls_unlocked_ls=True,
            reverser_not_deployed_eec=True,
            reverser_fully_deployed_eec=False,
            deploy_90_percent_vdt=True,
        )
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_altitude_gate_blocked(self):
        """TC02: altitude >= 6 ft → L1 blocked by altitude."""
        snap = _make_snap(radio_altitude_ft=6.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_altitude_at_10ft(self):
        """TC03: altitude at 10 ft → L1 clearly blocked."""
        snap = _make_snap(radio_altitude_ft=10.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_at_exact_threshold_minus14(self):
        """TC04: TRA at exactly -14 deg → L3 active (at threshold)."""
        snap = _make_snap(tra_deg=-14.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_at_zero(self):
        """TC05: TRA at 0 deg (positive) → L3 blocked."""
        snap = _make_snap(tra_deg=0.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_positive_5deg(self):
        """TC06: TRA at +5 deg → L3 blocked."""
        snap = _make_snap(tra_deg=5.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_below_threshold_minus20(self):
        """TC07: TRA at -20 deg (below -14) → L3 active."""
        snap = _make_snap(tra_deg=-20.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_between_minus14_and_minus11_7(self):
        """TC08: TRA between -14 and -11.7 → L3 blocked (just above threshold)."""
        snap = _make_snap(tra_deg=-13.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tra_just_above_minus11_7(self):
        """TC09: TRA at -11.7 deg (just above threshold) → L3 blocked."""
        snap = _make_snap(tra_deg=-11.7)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_sw1_off(self):
        """TC10: sw1=False → L1 blocked."""
        snap = _make_snap(sw1=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_sw2_off(self):
        """TC11: sw2=False → L2 blocked, L3 inactive."""
        snap = _make_snap(sw2=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_engine_off(self):
        """TC12: engine_running=False → L4 blocked."""
        snap = _make_snap(engine_running=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_reverser_inhibited(self):
        """TC13: reverser_inhibited=True → L1 blocked."""
        snap = _make_snap(reverser_inhibited=True)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_eec_disabled(self):
        """TC14: eec_enable=False → L3 inactive (EEC deploy not enabled)."""
        snap = _make_snap(eec_enable=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_n1_too_high(self):
        """TC15: n1k > 60.0 → L3 blocked by N1."""
        snap = _make_snap(n1k=65.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_n1_at_60_boundary(self):
        """TC16: n1k at 60.0 (upper limit) → N1 gate should block."""
        snap = _make_snap(n1k=60.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_n1_below_lower_threshold(self):
        """TC17: n1k < 50.0 → L3 blocked by N1."""
        snap = _make_snap(n1k=45.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_n1_at_50_boundary(self):
        """TC18: n1k at exactly 50.0 (lower threshold) → N1 gate passes."""
        snap = _make_snap(n1k=50.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_vdt_below_90_percent(self):
        """TC19: VDT below 90% → L4 blocked by VDT."""
        snap = _make_snap(deploy_position_percent=50.0, deploy_90_percent_vdt=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_vdt_at_90_percent(self):
        """TC20: VDT at exactly 90% → VDT gate passes."""
        snap = _make_snap(deploy_position_percent=95.0, deploy_90_percent_vdt=True)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_aircraft_not_on_ground(self):
        """TC21: aircraft_on_ground=False → L4 blocked."""
        snap = _make_snap(aircraft_on_ground=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_tls_locked(self):
        """TC22: tls_unlocked_ls=False → L2 affected."""
        snap = _make_snap(tls_unlocked_ls=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_pls_not_all_unlocked(self):
        """TC23: all_pls_unlocked_ls=False → L2 affected."""
        snap = _make_snap(all_pls_unlocked_ls=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_reverser_fully_deployed(self):
        """TC24: reverser_fully_deployed_eec=True → L3 affected."""
        snap = _make_snap(reverser_fully_deployed_eec=True)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_multiple_blockers_sw1_and_engine(self):
        """TC25: sw1=False AND engine_running=False → multiple blockers."""
        snap = _make_snap(sw1=False, engine_running=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_multiple_blockers_sw1_and_sw2(self):
        """TC26: sw1=False AND sw2=False → L1 and L2 blocked."""
        snap = _make_snap(sw1=False, sw2=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_baseline_full_chain_minus14(self):
        """TC27: sw1=True, sw2=True, TRA=-14, others default → full activation chain."""
        snap = _make_snap(
            sw1=True, sw2=True, tra_deg=-14.0,
            radio_altitude_ft=5.0, engine_running=True,
            reverser_inhibited=False, eec_enable=True,
            n1k=50.0, tls_unlocked_ls=True, all_pls_unlocked_ls=True,
            reverser_not_deployed_eec=True, reverser_fully_deployed_eec=False,
            deploy_90_percent_vdt=True, aircraft_on_ground=True,
        )
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_sw1_true_sw2_false(self):
        """TC28: sw1=True, sw2=False → L2 blocked."""
        snap = _make_snap(sw1=True, sw2=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_reverser_not_deployed_eec_false(self):
        """TC29: reverser_not_deployed_eec=False (not in stowed state) → affects L3."""
        snap = _make_snap(reverser_not_deployed_eec=False)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    def test_max_n1k_deploy_limit_different(self):
        """TC30: non-default max_n1k_deploy_limit → L3 N1 gate may behave differently."""
        snap = _make_snap(max_n1k_deploy_limit=55.0, n1k=53.0)
        gen, ref = _eval_both(snap)
        self._check_parity(gen, ref)

    # ------------------------------------------------------------------
    # Bulk subTest runner (all cases in one test for CI efficiency)
    # ------------------------------------------------------------------

    def test_all_cases_via_subTest(self):
        """Run all 30 cases via subTest so one failure doesn't abort the run."""
        cases = [
            ("TC01_full_activation", dict(
                radio_altitude_ft=5.0, tra_deg=-14.0, sw1=True, sw2=True,
                engine_running=True, aircraft_on_ground=True, reverser_inhibited=False,
                eec_enable=True, n1k=50.0, max_n1k_deploy_limit=60.0,
                tls_unlocked_ls=True, all_pls_unlocked_ls=True,
                reverser_not_deployed_eec=True, reverser_fully_deployed_eec=False,
                deploy_position_percent=95.0, deploy_90_percent_vdt=True,
            )),
            ("TC02_altitude_gate_blocked", dict(radio_altitude_ft=6.0)),
            ("TC03_altitude_at_10ft", dict(radio_altitude_ft=10.0)),
            ("TC04_tra_at_exact_threshold_minus14", dict(tra_deg=-14.0)),
            ("TC05_tra_at_zero", dict(tra_deg=0.0)),
            ("TC06_tra_positive_5deg", dict(tra_deg=5.0)),
            ("TC07_tra_below_threshold_minus20", dict(tra_deg=-20.0)),
            ("TC08_tra_between_minus14_and_minus11_7", dict(tra_deg=-13.0)),
            ("TC09_tra_just_above_minus11_7", dict(tra_deg=-11.7)),
            ("TC10_sw1_off", dict(sw1=False)),
            ("TC11_sw2_off", dict(sw2=False)),
            ("TC12_engine_off", dict(engine_running=False)),
            ("TC13_reverser_inhibited", dict(reverser_inhibited=True)),
            ("TC14_eec_disabled", dict(eec_enable=False)),
            ("TC15_n1_too_high", dict(n1k=65.0)),
            ("TC16_n1_at_60_boundary", dict(n1k=60.0)),
            ("TC17_n1_below_lower_threshold", dict(n1k=45.0)),
            ("TC18_n1_at_50_boundary", dict(n1k=50.0)),
            ("TC19_vdt_below_90_percent", dict(deploy_position_percent=50.0, deploy_90_percent_vdt=False, sw2=False)),
            ("TC20_vdt_at_90_percent", dict(deploy_position_percent=95.0, sw2=False)),
            ("TC21_aircraft_not_on_ground", dict(aircraft_on_ground=False)),
            ("TC22_tls_locked", dict(tls_unlocked_ls=False)),
            ("TC23_pls_not_all_unlocked", dict(all_pls_unlocked_ls=False)),
            ("TC24_reverser_fully_deployed", dict(reverser_fully_deployed_eec=True)),
            ("TC25_multiple_blockers_sw1_and_engine", dict(sw1=False, engine_running=False)),
            ("TC26_multiple_blockers_sw1_and_sw2", dict(sw1=False, sw2=False)),
            ("TC27_baseline_full_chain_minus14", dict(
                sw1=True, sw2=True, tra_deg=-14.0,
                radio_altitude_ft=5.0, engine_running=True,
                reverser_inhibited=False, eec_enable=True,
                n1k=50.0, tls_unlocked_ls=True, all_pls_unlocked_ls=True,
                reverser_not_deployed_eec=True, reverser_fully_deployed_eec=False,
                deploy_position_percent=95.0, deploy_90_percent_vdt=True, aircraft_on_ground=True,
            )),
            ("TC28_sw1_true_sw2_false", dict(sw1=True, sw2=False)),
            ("TC29_reverser_not_deployed_eec_false", dict(reverser_not_deployed_eec=False)),
            ("TC30_max_n1k_deploy_limit_different", dict(max_n1k_deploy_limit=55.0, n1k=53.0)),
        ]

        for name, overrides in cases:
            with self.subTest(name=name):
                snap = _make_snap(**overrides)
                gen, ref = _eval_both(snap)
                self._check_parity(gen, ref)


if __name__ == "__main__":
    unittest.main(verbosity=2)

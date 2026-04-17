"""Boundary regression tests for cefc95f / 15a1b69 fixes.

Locks down the following behaviors that had no dedicated unit coverage:
  * sw1 latch threshold at tra_deg == -1.4   (sw1_window.near_zero_deg)
  * sw2 latch threshold at tra_deg == -5.0   (sw2_window.near_zero_deg)
  * vdt90 node causal gating: requires logic3_active even when
    deploy_position_percent >= 90.0
  * tra_lock allowed_reverse_min_deg dynamic lower bound:
        lock_deg when L4 blocked, config.reverse_travel_min_deg when unlocked

These tests are purely additive. They do not modify truth-engine semantics,
the lever-snapshot contract, or any existing test.
"""
import unittest

from well_harness.demo_server import lever_snapshot_payload
from well_harness.models import HarnessConfig
from well_harness.switches import LatchedThrottleSwitches, SwitchState


class Sw1ThresholdBoundaryTests(unittest.TestCase):
    """sw1_window: near_zero_deg=-1.4, deep_reverse_deg=-6.2 (models.py:25)."""

    def _fresh(self):
        return LatchedThrottleSwitches(HarnessConfig()), SwitchState(previous_tra_deg=0.0)

    def test_sw1_latches_exactly_at_threshold_minus_1_4(self):
        sw, state = self._fresh()
        self.assertTrue(sw.update(state, -1.4).sw1)

    def test_sw1_does_not_latch_just_above_threshold_minus_1_39(self):
        sw, state = self._fresh()
        self.assertFalse(sw.update(state, -1.39).sw1)

    def test_sw1_latches_just_below_threshold_minus_1_41(self):
        sw, state = self._fresh()
        self.assertTrue(sw.update(state, -1.41).sw1)


class Sw2ThresholdBoundaryTests(unittest.TestCase):
    """sw2_window: near_zero_deg=-5.0, deep_reverse_deg=-9.8 (models.py:32)."""

    def _fresh(self):
        return LatchedThrottleSwitches(HarnessConfig()), SwitchState(previous_tra_deg=0.0)

    def test_sw2_latches_exactly_at_threshold_minus_5_0(self):
        sw, state = self._fresh()
        self.assertTrue(sw.update(state, -5.0).sw2)

    def test_sw2_does_not_latch_just_above_threshold_minus_4_99(self):
        sw, state = self._fresh()
        self.assertFalse(sw.update(state, -4.99).sw2)

    def test_sw2_latches_just_below_threshold_minus_5_01(self):
        sw, state = self._fresh()
        self.assertTrue(sw.update(state, -5.01).sw2)


class Vdt90CausalGatingTests(unittest.TestCase):
    """Regression guard for demo_server.py:2859 —
    vdt90 node state must require BOTH deploy_90_percent_vdt AND logic3_active.
    """

    @staticmethod
    def _vdt90_state(payload: dict) -> str:
        for node in payload["nodes"]:
            if node["id"] == "vdt90":
                return node["state"]
        raise AssertionError("vdt90 node missing from snapshot")

    def _baseline_kwargs(self, **overrides):
        base = dict(
            tra_deg=-14.0,
            radio_altitude_ft=5.0,
            engine_running=True,
            aircraft_on_ground=True,
            reverser_inhibited=False,
            eec_enable=True,
            n1k=50.0,
            deploy_position_percent=95.0,
            feedback_mode="manual_feedback_override",
        )
        base.update(overrides)
        return base

    def test_vdt90_active_when_full_chain_satisfied(self):
        payload = lever_snapshot_payload(**self._baseline_kwargs())
        self.assertEqual(self._vdt90_state(payload), "active")

    def test_vdt90_inactive_when_l3_blocked_even_at_95_percent(self):
        # engine_running=False breaks L2 -> etrac_540v inactive -> L3 blocked.
        payload = lever_snapshot_payload(**self._baseline_kwargs(engine_running=False))
        self.assertEqual(self._vdt90_state(payload), "inactive")

    def test_vdt90_inactive_below_90_percent_even_when_chain_active(self):
        payload = lever_snapshot_payload(**self._baseline_kwargs(deploy_position_percent=89.9))
        self.assertEqual(self._vdt90_state(payload), "inactive")


class TraLockBoundaryTests(unittest.TestCase):
    """Regression guard for demo_server.py:2332 — allowed_reverse_min_deg
    switches between lock_deg (locked) and config.reverse_travel_min_deg (unlocked).
    """

    def test_tra_lock_clamps_and_reports_lock_deg_when_l4_blocked(self):
        # engine_running=False keeps L4 blocked. Request a deep TRA (-20 deg) that
        # must be clamped back to lock_deg (-14 deg).
        payload = lever_snapshot_payload(
            tra_deg=-20.0,
            engine_running=False,
        )
        lock = payload["tra_lock"]
        self.assertTrue(lock["locked"])
        self.assertTrue(lock["clamped"])
        self.assertFalse(lock["unlock_ready"])
        self.assertEqual(lock["allowed_reverse_min_deg"], lock["lock_deg"])

    def test_tra_lock_opens_deep_range_when_l4_satisfied(self):
        payload = lever_snapshot_payload(
            tra_deg=-14.0,
            radio_altitude_ft=5.0,
            engine_running=True,
            aircraft_on_ground=True,
            reverser_inhibited=False,
            eec_enable=True,
            n1k=50.0,
            deploy_position_percent=95.0,
            feedback_mode="manual_feedback_override",
        )
        lock = payload["tra_lock"]
        self.assertTrue(lock["unlock_ready"])
        self.assertFalse(lock["locked"])
        self.assertEqual(
            lock["allowed_reverse_min_deg"],
            lock["visual_reverse_min_deg"],
        )


if __name__ == "__main__":
    unittest.main()

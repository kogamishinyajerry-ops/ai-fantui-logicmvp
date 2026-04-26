"""Truth-engine change driven by proposal PROP-20260426T075902988411-e27a6e.

Engineer suggestion: "L2 SW2 应该 tighten" (Kogami, 2026-04-26)
System interpretation (rules): 在 L2 上对 SW2 收紧判据
Accepted by: Kogami at 2026-04-26T08:18:55Z
Brief:    .planning/dev_queue/PROP-20260426T075902988411-e27a6e.md
Proposal: .planning/proposals/PROP-20260426T075902988411-e27a6e.json

Implementation chosen (lowest-blast-radius interpretation):
add a TRA hysteresis margin at L2's SW2 dependency. SW2's own latch
in switches.py is unchanged — it still triggers on entry to the
[-9.8°, -5.0°] window and resets when TRA returns above -5.0°.
What changes is L2's interpretation of SW2: L2 now requires
tra_deg <= logic2_sw2_max_tra_deg (default -5.5°), 0.5° stricter
than the SW2 reset threshold.

This means as the pilot pulls back out of reverse, L2 deactivates
0.5° before SW2 itself resets — the "tightening" the engineer
asked for, surfaced cleanly as a new explain condition the panel
can highlight independently.

Locked here:
  1. Default config value matches the design (-5.5°)
  2. The new condition appears in L2's explain
  3. Behavior boundary at exactly tra_deg = -5.5° (passes) vs
     tra_deg = -5.4° (fails — the new tightening fires)
  4. Deep-reverse normal operation (TRA = -14°) is unaffected
"""

from __future__ import annotations

import pytest

from well_harness.controller import DeployController
from well_harness.models import HarnessConfig, ResolvedInputs


def _inputs(tra_deg: float, **overrides) -> ResolvedInputs:
    """Minimal L2-passing fixture: every L2 condition is True except
    those overridden + the new SW2 hysteresis check that depends on
    tra_deg."""
    base = dict(
        radio_altitude_ft=5.0,
        tra_deg=tra_deg,
        sw1=True,
        sw2=True,
        engine_running=True,
        aircraft_on_ground=True,
        reverser_inhibited=False,
        eec_enable=True,
        n1k=35.0,
        max_n1k_deploy_limit=60.0,
        tls_unlocked_ls=True,
        all_pls_unlocked_ls=True,
        reverser_not_deployed_eec=True,
        reverser_fully_deployed_eec=False,
        deploy_90_percent_vdt=False,
    )
    base.update(overrides)
    return ResolvedInputs(**base)


def _l2_explain(controller: DeployController, inputs: ResolvedInputs):
    return controller.explain(inputs).logic2


# ─── 1. Default config carries the new threshold ───────────────────


def test_default_config_carries_logic2_sw2_max_tra_deg():
    cfg = HarnessConfig()
    assert cfg.logic2_sw2_max_tra_deg == -5.5, (
        "default L2 SW2 hysteresis threshold drifted from the value "
        "approved in PROP-20260426T075902988411-e27a6e"
    )


# ─── 2. New condition appears in L2 explain ────────────────────────


def test_l2_explain_includes_sw2_hysteresis_condition():
    controller = DeployController()
    explain = _l2_explain(controller, _inputs(tra_deg=-14.0))
    names = [c.name for c in explain.conditions]
    assert "sw2_hysteresis_tra_deg" in names, (
        f"L2 explain missing the new sw2_hysteresis_tra_deg condition; "
        f"found: {names}"
    )


def test_l2_sw2_hysteresis_condition_carries_threshold_metadata():
    """The condition must surface its comparison + threshold so the
    workbench panel can render the hysteresis margin to engineers."""
    controller = DeployController()
    explain = _l2_explain(controller, _inputs(tra_deg=-14.0))
    cond = next(c for c in explain.conditions if c.name == "sw2_hysteresis_tra_deg")
    assert cond.comparison == "<="
    assert cond.threshold_value == -5.5
    assert cond.passed is True


# ─── 3. Boundary behavior — the heart of the "tighten" change ─────


@pytest.mark.parametrize(
    "tra_deg, should_pass",
    [
        # Deep reverse — well below the threshold, no behavior change
        (-14.0, True),
        # Right at the new hysteresis threshold — must still pass
        # (<= is inclusive, matching the existing comparison style)
        (-5.5, True),
        # 0.05° stricter than threshold — passes
        (-5.55, True),
        # 0.05° looser than threshold — FAILS (this is the new
        # "tightening" the engineer asked for)
        (-5.45, False),
        # Right at SW2 reset (-5.0°) — would have passed pre-PROP,
        # now fails because hysteresis kicks in 0.5° earlier
        (-5.0, False),
        # Forward of SW2 reset — fails on multiple grounds, but the
        # hysteresis condition is among them
        (-4.5, False),
    ],
)
def test_l2_sw2_hysteresis_boundary(tra_deg, should_pass):
    controller = DeployController()
    explain = _l2_explain(controller, _inputs(tra_deg=tra_deg))
    cond = next(c for c in explain.conditions if c.name == "sw2_hysteresis_tra_deg")
    assert cond.passed is should_pass, (
        f"L2 SW2 hysteresis condition at tra_deg={tra_deg} expected "
        f"passed={should_pass}, got passed={cond.passed} "
        f"(threshold={cond.threshold_value})"
    )


# ─── 4. L2 active output reflects the new condition ────────────────


def test_l2_deactivates_when_only_hysteresis_fails():
    """SW2 itself is True, all other L2 conditions are True, but TRA
    is in (-5.5°, -5.0°] → L2 must NOT activate. This is the visible
    behavior change the engineer asked for."""
    controller = DeployController()
    outputs, _ = controller.evaluate_with_explain(_inputs(tra_deg=-5.2))
    assert outputs.logic2_active is False, (
        "L2 still activates with TRA in the new hysteresis band — the "
        "PROP-e27a6e tightening is not in effect"
    )


def test_l2_activates_at_or_below_hysteresis_threshold():
    controller = DeployController()
    outputs, _ = controller.evaluate_with_explain(_inputs(tra_deg=-5.5))
    assert outputs.logic2_active is True


def test_l2_normal_deep_reverse_unaffected():
    """Regression guard: the change must NOT shift any L2 behavior in
    the operating zone (deep reverse, TRA = -14°)."""
    controller = DeployController()
    outputs, _ = controller.evaluate_with_explain(_inputs(tra_deg=-14.0))
    assert outputs.logic2_active is True


# ─── 5. Knob is configurable for follow-on tuning ──────────────────


def test_hysteresis_threshold_is_configurable():
    """A future engineer can dial the hysteresis tighter/looser
    without code edits — validates the config-driven design."""
    tighter = DeployController(HarnessConfig(logic2_sw2_max_tra_deg=-7.0))
    explain = _l2_explain(tighter, _inputs(tra_deg=-6.5))
    cond = next(c for c in explain.conditions if c.name == "sw2_hysteresis_tra_deg")
    assert cond.threshold_value == -7.0
    assert cond.passed is False, (
        "config override didn't propagate; L2 should reject TRA=-6.5° "
        "when the threshold is dialed to -7.0°"
    )

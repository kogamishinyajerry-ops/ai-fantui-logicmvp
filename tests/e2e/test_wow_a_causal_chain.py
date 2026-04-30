"""E2E Wow A — causal chain via truth engine (no LLM dependency).

The wow-A story is: given lever inputs that satisfy all deploy preconditions,
the truth engine produces a coherent activated chain (logic1 → logic2 → logic3
→ logic4 → thr_lock) over 19 nodes. LLM only narrates; the contract-bearing
observable is /api/lever-snapshot.

These tests pin the truth-engine contract end-to-end against a live
demo_server on :8799, independent of any MiniMax availability.
"""
from __future__ import annotations

import time

import pytest

EXPECTED_LOGIC_KEYS = {"logic1", "logic2", "logic3", "logic4"}
EXPECTED_NODE_COUNT = 19

# Domain semantics (probed from live demo_server post-a46e4e6 / 2ded020):
#   logic1 = landing-regime detector: RA < threshold AND on_ground AND NOT inhibited
#            AND reverser_not_deployed_eec; the last condition flips False once the
#            plant fully deploys, so logic1 may de-activate during BEAT_DEEP.
#   logic2 = TLS-unlock confirmation
#   logic3 = deep-reverse commit: TRA crossed lock threshold AND logic2 AND SW2 closed
#   logic4 = deploy-confirmed feedback: requires deploy_90_percent_vdt. Under
#           feedback_mode='auto_scrubber' the server-side canonical pullback
#           (demo_server._canonical_pullback_sequence, extended in commit a46e4e6)
#           holds the lever long enough for plant VDT to reach 100%, so the feedback
#           node flips True within a single /api/lever-snapshot call and logic4
#           latches. Under manual_feedback_override mode, logic4 activates only when
#           the caller supplies deploy_position_percent ≥ 90.
#
# Therefore wow-A locks what auto_scrubber delivers from a single POST:
#   - BEAT_EARLY   (tra_deg=-5.6) → logic1 + logic2 active; TRA enters the
#                                   tightened L2 SW2 hysteresis threshold
#                                   (≤ -5.5°) but never crosses the L3
#                                   threshold, so the plant remains at 0%
#                                   deploy and logic3/4 remain inactive.
#   - BEAT_DEEP    (tra_deg=-35) → logic2 + logic3 + logic4 active; the extended
#                                  canonical pullback runs the plant to 100%
#                                  deploy within ~4.4s, latching the full chain.
#                                  logic1 de-activates as reverser_not_deployed_eec
#                                  flips False mid-deploy.
#   - BEAT_BLOCKED (airborne)   → all four inactive (chain broken at logic1).
# These three beats together form the demo's causal-chain narrative.
BEAT_EARLY_PAYLOAD = {
    "tra_deg": -5.6, "radio_altitude_ft": 2,
    "engine_running": True, "aircraft_on_ground": True,
    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.8,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
}
BEAT_DEEP_PAYLOAD = {
    "tra_deg": -35, "radio_altitude_ft": 2,
    "engine_running": True, "aircraft_on_ground": True,
    "reverser_inhibited": False, "eec_enable": True, "n1k": 0.92,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
}
BEAT_BLOCKED_PAYLOAD = {
    **BEAT_EARLY_PAYLOAD,
    "radio_altitude_ft": 500,
    "aircraft_on_ground": False,
}


@pytest.mark.e2e
def test_wow_a_lever_snapshot_returns_19_nodes_with_contract_fields(demo_server, api_post):
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert isinstance(body, dict)
    assert "nodes" in body and isinstance(body["nodes"], list)
    assert len(body["nodes"]) == EXPECTED_NODE_COUNT
    for node in body["nodes"]:
        assert isinstance(node, dict)
        assert set(node.keys()) >= {"id", "state"}
        assert isinstance(node["id"], str) and node["id"]
        assert isinstance(node["state"], str)


@pytest.mark.e2e
def test_wow_a_lever_snapshot_exposes_four_logic_gates(demo_server, api_post):
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert "logic" in body
    logic = body["logic"]
    assert isinstance(logic, dict)
    assert set(logic.keys()) == EXPECTED_LOGIC_KEYS
    for key, gate in logic.items():
        assert isinstance(gate, dict), f"{key} must be a dict"
        assert "active" in gate, f"{key} missing 'active'"
        assert isinstance(gate["active"], bool), f"{key}.active must be bool"


@pytest.mark.e2e
def test_wow_a_beat_early_activates_logic1_and_logic2_only(demo_server, api_post):
    """Demo beat 1: SW2-window TRA + landing → logic1 + logic2 active, 3/4 pending."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_EARLY_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert active == {"logic1", "logic2"}, (
        f"BEAT_EARLY should activate exactly logic1+logic2, got {active}"
    )


@pytest.mark.e2e
def test_wow_a_beat_deep_activates_logic2_and_logic3(demo_server, api_post):
    """Demo beat 2: deep reverse under auto_scrubber drives the full chain.

    Per commit a46e4e6 ("fix(scrubber): extend canonical pullback hold to let
    plant VDT reach 90%"), feedback_mode='auto_scrubber' with tra_deg below
    logic3_tra_deg_threshold runs the in-server plant to 100% deploy within
    ~4.4s of simulated time. Inside a single /api/lever-snapshot call the
    feedback node deploy_90_percent_vdt flips True and logic4 latches.

    Test name retained for stability; the locked invariants are now:
      (a) at least logic2 + logic3 are active (deep-reverse commit), and
      (b) logic4 is also active under auto_scrubber (post-a46e4e6 reality).
    The "single POST cannot activate logic4 without feedback" invariant is
    a manual-mode concern; see manual_feedback_override path with
    deploy_position_percent < 90 to probe it.
    """
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert {"logic2", "logic3"} <= active, (
        f"BEAT_DEEP should at least activate logic2+logic3, got {active}"
    )
    assert logic["logic4"].get("active") is True, (
        "logic4 must activate under auto_scrubber's extended canonical pullback "
        "(plant VDT reaches 100% within the lever-snapshot window — see "
        "demo_server._canonical_pullback_sequence and commit a46e4e6)"
    )


@pytest.mark.e2e
def test_wow_a_beat_blocked_deactivates_entire_chain(demo_server, api_post):
    """Demo beat 3 (negative control): airborne → entire chain inactive."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_BLOCKED_PAYLOAD)
    assert status == 200
    logic = body["logic"]
    active = {k for k, v in logic.items() if v.get("active") is True}
    assert active == set(), (
        f"BEAT_BLOCKED (airborne) should deactivate every gate, got active={active}"
    )


@pytest.mark.e2e
def test_wow_a_truth_engine_is_deterministic(demo_server, api_post):
    """Same lever inputs → byte-identical logic dict across two calls."""
    status1, body1 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    status2, body2 = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status1 == 200 and status2 == 200
    assert body1["logic"] == body2["logic"]
    node_state_1 = {n["id"]: n["state"] for n in body1["nodes"]}
    node_state_2 = {n["id"]: n["state"] for n in body2["nodes"]}
    assert node_state_1 == node_state_2


@pytest.mark.e2e
def test_wow_a_response_under_500ms_warm(demo_server, api_post):
    """Rehearsal budget: truth engine must return in <500ms after warmup."""
    api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)  # warmup
    t0 = time.monotonic()
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    elapsed_ms = (time.monotonic() - t0) * 1000
    assert status == 200
    assert elapsed_ms < 500, f"lever-snapshot took {elapsed_ms:.0f}ms (budget 500ms)"


@pytest.mark.e2e
def test_wow_a_lever_snapshot_evidence_field_present(demo_server, api_post):
    """Evidence is the LLM-facing narrative source; must exist for wow A narration."""
    status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
    assert status == 200
    assert "evidence" in body
    assert "plant_state" in body
    assert "outputs" in body

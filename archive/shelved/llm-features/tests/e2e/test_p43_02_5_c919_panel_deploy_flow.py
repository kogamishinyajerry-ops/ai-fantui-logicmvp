"""P43-02.5 Delta 3 · C919 reference panel deploy-flow E2E (backend only).

Scripts Exit #25 "Unlock→deploy 完整链演示" as a backend-only integration
test (no DOM / no Playwright · plan §4 Exit #25 UI portion covered by
human-eye in Step B).

Uses existing tests/e2e/conftest.py subprocess+HTTP fixture scope:
- `demo_server` fixture boots demo_server on :8799
- `api_post` fixture returns (status, body) for POST /api/system-snapshot

Asserts the full deploy chain with Q6=B controls:
- 12 core inputs (TRA=-14 + atltla/apwtla=true + engine_running + tr_wow +
  LGCU 4 fields + tr_inhibited=false + N1K=35 + no over_temp_fault)
- 7 unlock/deploy gating (TLS A/B unlock + all-pylon unlock + PLS
  locked=false + tr_position=90% + trcu_power=true)
- Advance deploy latches (lock_unlock_confirm_s=0.4 +
  tr_position_deployed_confirm_s=0.5 + tr_stowed_locked_confirm_s=0.0)

Expected: all 4 ln_* in active_logic_node_ids, fadec_deploy_command=true,
completion_reached=true, blocked_reasons=[].

Whitelist authority: P43-00 v9 amend Delta 3 (pending Kogami approval).
"""
from __future__ import annotations

import pytest


DEPLOY_SNAPSHOT = {
    # 12 core inputs
    "tra_deg": -14.0,
    "atltla": True,
    "apwtla": True,
    "n1k_percent": 35.0,
    "engine_running": True,
    "tr_inhibited": False,
    "tr_wow": True,
    "lgcu1_mlg_wow_value": True, "lgcu1_mlg_wow_valid": True,
    "lgcu2_mlg_wow_value": True, "lgcu2_mlg_wow_valid": True,
    "e_tras_over_temp_fault": False,
    # 7 unlock/deploy gating
    "tls_ls_a_valid": True, "tls_ls_a_unlocked": True,
    "tls_ls_b_valid": True, "tls_ls_b_unlocked": True,
    "left_pylon_ls_a_valid": True, "left_pylon_ls_a_unlocked": True,
    "left_pylon_ls_b_valid": True, "left_pylon_ls_b_unlocked": True,
    "right_pylon_ls_a_valid": True, "right_pylon_ls_a_unlocked": True,
    "right_pylon_ls_b_valid": True, "right_pylon_ls_b_unlocked": True,
    "pls_ls_a_locked": False, "pls_ls_b_locked": False,
    "tr_position_percent": 90.0,
    "trcu_power_on": True,
    # readonly / default
    "vdt_sensor_valid": True,
    "prev_eicu_cmd3": False,
    "comm2_timer_s": 0.0,
    # Advance deploy latches (v4.2 §2c row 19)
    "lock_unlock_confirm_s": 0.4,
    "tr_position_deployed_confirm_s": 0.5,
    "tr_stowed_locked_confirm_s": 0.0,
}


@pytest.mark.e2e
def test_c919_panel_deploy_flow_all_logic_nodes_active(demo_server, api_post):
    """Exit #25 · Unlock→deploy 完整链 · 4 ln_* all active + completion_reached."""
    status, body = api_post(
        demo_server,
        "/api/system-snapshot",
        {"system_id": "c919-etras", "snapshot": DEPLOY_SNAPSHOT},
    )
    assert status == 200, f"expected 200, got {status}: {body}"
    truth = body.get("truth_evaluation", {})
    active = set(truth.get("active_logic_node_ids", []))
    expected = {
        "ln_eicu_cmd2",
        "ln_eicu_cmd3",
        "ln_tr_command3_enable",
        "ln_fadec_deploy_command",
    }
    assert expected <= active, (
        f"expected all 4 ln_* active, got {sorted(active)}\n"
        f"missing: {sorted(expected - active)}\n"
        f"blocked_reasons: {truth.get('blocked_reasons', [])}"
    )
    asserted = truth.get("asserted_component_values", {})
    assert asserted.get("fadec_deploy_command") is True
    assert truth.get("completion_reached") is True


@pytest.mark.e2e
def test_c919_panel_stow_latches_resets_cmd3(demo_server, api_post):
    """#19-alt · Stow latches button · tr_stowed_locked_confirm_s=1.0 → eicu_cmd3 reset."""
    stow_snapshot = dict(DEPLOY_SNAPSHOT)
    stow_snapshot["tr_stowed_locked_confirm_s"] = 1.0  # ≥ TR_STOWED_LOCKED_CONFIRM_S
    status, body = api_post(
        demo_server,
        "/api/system-snapshot",
        {"system_id": "c919-etras", "snapshot": stow_snapshot},
    )
    assert status == 200
    truth = body.get("truth_evaluation", {})
    asserted = truth.get("asserted_component_values", {})
    assert asserted.get("eicu_cmd3") is False, (
        "tr_stowed_locked_confirm_s ≥ threshold should reset eicu_cmd3 "
        f"(adapter:1285-1289) · got asserted={asserted}"
    )


@pytest.mark.e2e
def test_c919_panel_tr_inhibited_blocks_chain(demo_server, api_post):
    """Exit #24 · tr_inhibited=true · eicu_cmd2 blocked · fadec_deploy unreachable."""
    blocked_snap = dict(DEPLOY_SNAPSHOT)
    blocked_snap["tr_inhibited"] = True
    status, body = api_post(
        demo_server,
        "/api/system-snapshot",
        {"system_id": "c919-etras", "snapshot": blocked_snap},
    )
    assert status == 200
    truth = body.get("truth_evaluation", {})
    asserted = truth.get("asserted_component_values", {})
    assert asserted.get("eicu_cmd2") is False
    assert asserted.get("fadec_deploy_command") is False
    reasons = truth.get("blocked_reasons", [])
    # At least one reason mentions TR_Inhibited
    assert any("TR_Inhibited" in r for r in reasons), f"blocked_reasons: {reasons}"


@pytest.mark.e2e
def test_c919_operate_stub_returns_manual_steps(demo_server, api_post):
    """Step D1 T8 · operate endpoint returns stub (manual_steps) · no LLM call."""
    status, body = api_post(
        demo_server,
        "/api/chat/operate",
        {
            "system_id": "c919-etras",
            "question": "把 TRA 调到 -14°",
            "current_snapshot": {"snapshot": DEPLOY_SNAPSHOT},
        },
    )
    assert status == 200, f"expected 200 stub response, got {status}: {body}"
    assert body.get("action_type") == "manual_steps"
    assert body.get("parameter_overrides") == {}
    assert body.get("auto_apply") is False
    # reasoning mentions "panel"
    reasoning = body.get("reasoning", "")
    assert "panel" in reasoning.lower(), f"stub reasoning should point to panel: {reasoning}"


@pytest.mark.e2e
def test_c919_allowlist_unblocks_reason_endpoint(demo_server, api_post):
    """Step D1 T7 · /api/chat/reason accepts c919-etras (no 400 invalid_system_id)."""
    status, body = api_post(
        demo_server,
        "/api/chat/reason",
        {"system_id": "c919-etras", "question": "test", "current_snapshot": {}},
    )
    # Not 400 invalid_system_id (may be 400/500 for other validation reasons or 200 LLM OK)
    if status == 400:
        assert body.get("error") != "invalid_system_id", (
            f"T7 allowlist failed · c919-etras should not trigger invalid_system_id: {body}"
        )

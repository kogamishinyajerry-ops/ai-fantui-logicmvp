"""测试辅助：C919 E-TRAS Frozen V1.0 单元/集成测试共用 fixtures。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# P49-02a (2026-04-27): governance gate is ON by default in
# production; the test suite default is OFF so existing tests
# don't have to thread approval signals through every executor
# call. Tests that exercise the gate explicitly opt back in via
# a monkeypatch of WORKBENCH_GOVERNANCE_ENABLED to "1".
os.environ.setdefault("WORKBENCH_GOVERNANCE_ENABLED", "0")

from well_harness.adapters.c919_etras_frozen_v1 import LockInputs, RawInputs


# E11-14 (2026-04-25): /api/lever-snapshot requires actor + ticket_id +
# manual_override_signoff when feedback_mode = manual_feedback_override.
# Tests that exercise the override path (not the guard itself) use this
# helper to extend their request payload with a fixed sign-off triplet.
# Tests of the guard itself (negative cases) live in
# tests/test_lever_snapshot_manual_override_guard.py.
#
# ⚠ CANNED TEST FIXTURE — NOT REAL AUTHENTICATION. signed_by/ticket_id are
# placeholder strings that satisfy the structural guard. Replay/nonce/
# freshness checks are E11-16 scope.
MANUAL_OVERRIDE_SIGNOFF = {
    "actor": "TestSuite",
    "ticket_id": "WB-TEST",
    "manual_override_signoff": {
        "signed_by": "TestSuite",
        "signed_at": "2026-04-25T00:00:00Z",
        "ticket_id": "WB-TEST",
    },
}


def with_signoff_if_manual_override(payload: dict) -> dict:
    """Return payload with sign-off attached when feedback_mode = manual_feedback_override.

    Existing fields in payload take precedence (so a test setting actor=""
    can still produce a 409 when intentionally exercising the guard).
    """
    if isinstance(payload, dict) and payload.get("feedback_mode") == "manual_feedback_override":
        return {**MANUAL_OVERRIDE_SIGNOFF, **payload}
    return payload


def make_locks(
    *,
    tls: str = "locked",
    pl_l: str = "locked",
    pl_r: str = "locked",
    pls_l: str = "locked",
    pls_r: str = "locked",
) -> LockInputs:
    def pair(s: str):
        if s == "locked":
            return (True, False)
        if s == "unlocked":
            return (False, True)
        return (False, False)

    tl, tu = pair(tls)
    l_l, l_u = pair(pl_l)
    r_l, r_u = pair(pl_r)
    pl_ll, pl_lu = pair(pls_l)
    pl_rl, pl_ru = pair(pls_r)
    return LockInputs(
        tls_locked=tl, tls_unlocked=tu,
        pylon_lock_l_locked=l_l, pylon_lock_l_unlocked=l_u,
        pylon_lock_r_locked=r_l, pylon_lock_r_unlocked=r_u,
        pls_l_locked=pl_ll, pls_l_unlocked=pl_lu,
        pls_r_locked=pl_rl, pls_r_unlocked=pl_ru,
    )


def make_inputs(**overrides) -> RawInputs:
    defaults = dict(
        lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
        lgcu1_valid=True, lgcu2_valid=True,
        tra_deg=0.0,
        atltla=False, apwtla=False,
        tr_inhibited=False,
        engine_running=True,
        trcu_menu_mode=False,
        maintenance_cycle_on_going=False,
        tr_position_pct=0.0,
        n1k_pct=50.0,
        max_n1k_deploy_limit_pct=84.0,
        max_n1k_stow_limit_pct=72.0,
        etras_over_temp_fault=False,
        locks=make_locks(),
    )
    defaults.update(overrides)
    return RawInputs(**defaults)


@pytest.fixture
def inputs_factory():
    return make_inputs


@pytest.fixture
def locks_factory():
    return make_locks

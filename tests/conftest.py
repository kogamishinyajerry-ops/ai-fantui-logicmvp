"""测试辅助：C919 E-TRAS Frozen V1.0 单元/集成测试共用 fixtures。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from well_harness.adapters.c919_etras_frozen_v1 import LockInputs, RawInputs


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

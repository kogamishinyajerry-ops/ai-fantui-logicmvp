"""集成测试：S0→S10 正常全链路、互锁打断、故障断电。"""
from __future__ import annotations

import pytest

from well_harness.adapters.c919_etras_frozen_v1 import C919ReverseThrustSystem, FrozenConfig, SystemState


def _ticks_for(system: C919ReverseThrustSystem, make_inp, n: int, dt: float = 0.1):
    for _ in range(n):
        system.tick(make_inp(), dt)


class TestFullHappyPath:
    """S0 → S10 完整链路。"""

    def test_ground_landing_to_stowed_locked_power_off(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()

        # ---- 阶段 0：空中（未接地） ----
        air = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=False, lgcu2_mlg_wow=False,
            engine_running=True,
            tr_position_pct=0.0,
            locks=locks_factory(),
        )
        out = sys_.tick(air, 0.1)
        assert out.state == SystemState.S0_AIR_STOWED_LOCKED

        # ---- 阶段 1：接地，TR_WOW 滤波 2.25s 到位 → S1 ----
        on_ground_idle = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True, tr_position_pct=0.0,
            locks=locks_factory(),
        )
        for _ in range(30):  # 3s
            sys_.tick(on_ground_idle, 0.1)
        assert sys_.state == SystemState.S1_GROUND_ARMED

        # ---- 阶段 2：飞行员拉反推 → ATLTLA=1 进入 SW1 窗口 ----
        # 1) 首先 ATLTLA=1, 锁仍全 locked（CMD2 通电触发解锁） → S2
        pulling_sw1 = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-3.0, atltla=True, apwtla=False,
            tr_position_pct=0.0,
            locks=locks_factory(),
        )
        for _ in range(5):
            sys_.tick(pulling_sw1, 0.1)
        assert sys_.state == SystemState.S2_UNLOCK_POWER_ON

        # ---- 阶段 3：ATLTLA + APWTLA=1，锁已打开；CMD3 置位 → S3 ----
        pulling_sw2 = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-7.0, atltla=True, apwtla=True,
            tr_position_pct=0.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        for _ in range(5):
            sys_.tick(pulling_sw2, 0.1)
        assert sys_.state == SystemState.S3_TRCU_POWER_ON

        # ---- 阶段 4：FADEC Deploy（TRA 过反推慢车 -11.74°） → S4 ----
        deploying = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-15.0, atltla=True, apwtla=True,
            tr_position_pct=10.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        for _ in range(3):
            sys_.tick(deploying, 0.1)
        assert sys_.state == SystemState.S4_DEPLOYING

        # ---- 阶段 5：TR_Position 到 85% → S5 ----
        deployed = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-15.0, atltla=True, apwtla=True,
            tr_position_pct=85.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        out = sys_.tick(deployed, 0.1)
        assert sys_.state == SystemState.S5_DEPLOYED_IDLE_REVERSE
        # 此时 CMD2 必须断电（≥80%），CMD3 必须仍在（回杆还没发生）
        assert out.single_phase_unlock_power_on is False
        assert out.three_phase_trcu_power_on is True

        # ---- 阶段 6：最大反推（TRA ≤ -25°） → S6 ----
        max_rev = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-28.0, atltla=True, apwtla=True,
            tr_position_pct=100.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        sys_.tick(max_rev, 0.1)
        assert sys_.state == SystemState.S6_MAX_REVERSE

        # ---- 阶段 7：飞行员回杆（ATLTLA=0 AND APWTLA=0） → S7 ----
        throttle_back = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=-2.0, atltla=False, apwtla=False,
            tr_position_pct=100.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        sys_.tick(throttle_back, 0.1)
        assert sys_.state == SystemState.S7_DECEL_WAIT_STOW
        # 三相电仍必须保持
        assert sys_.cmd3.latch is True

        # ---- 阶段 8：Stow 条件达成（TRA≥0, N1k≤stow_limit） → S8 ----
        ready_stow = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=0.0, atltla=False, apwtla=False,
            tr_position_pct=100.0, n1k_pct=60.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        sys_.tick(ready_stow, 0.1)
        assert sys_.state == SystemState.S8_STOWING

        # ---- 阶段 9：TR_Position 回到 0 → S9 ----
        retracted = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=0.0, atltla=False, apwtla=False,
            tr_position_pct=0.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                                pls_l="unlocked", pls_r="unlocked"),
        )
        sys_.tick(retracted, 0.1)
        assert sys_.state == SystemState.S9_LOCK_CONFIRM

        # ---- 阶段 10：所有锁回位 + 1s → S10 ----
        re_locked = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=True,
            engine_running=True,
            tra_deg=0.0, atltla=False, apwtla=False,
            tr_position_pct=0.0,
            locks=locks_factory(),  # 默认全 locked
        )
        for _ in range(15):
            sys_.tick(re_locked, 0.1)
        assert sys_.state == SystemState.S10_STOWED_LOCKED_POWER_OFF
        # §9 验收#5：收起上锁确认后才切断三相电
        final_out = sys_.tick(re_locked, 0.1)
        assert final_out.three_phase_trcu_power_on is False


class TestSafetyPreemption:
    """TR_Inhibited / 过温 → 任意状态 → SF 抢占。"""

    def test_inhibit_forces_sf_from_s4(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        sys_.sm.force(SystemState.S4_DEPLOYING)
        inp = inputs_factory(
            tr_inhibited=True,
            tr_position_pct=30.0,
            locks=locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked"),
        )
        out = sys_.tick(inp, 0.1)
        assert out.state == SystemState.SF_ABORT_OR_FAULT

    def test_overtemp_forces_sf_and_kills_3phase(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        # 先把 CMD3 打开
        on_inp = inputs_factory(apwtla=True, engine_running=True,
                                 tr_position_pct=50.0,
                                 locks=locks_factory(tls="unlocked",
                                                     pl_l="unlocked",
                                                     pl_r="unlocked",
                                                     pls_l="unlocked",
                                                     pls_r="unlocked"))
        for _ in range(30):
            sys_.tick(on_inp, 0.1)
        # 过温
        hot = inputs_factory(apwtla=True, engine_running=True,
                              tr_position_pct=50.0,
                              etras_over_temp_fault=True,
                              locks=locks_factory(tls="unlocked",
                                                  pl_l="unlocked",
                                                  pl_r="unlocked",
                                                  pls_l="unlocked",
                                                  pls_r="unlocked"))
        out = sys_.tick(hot, 0.1)
        assert out.state == SystemState.SF_ABORT_OR_FAULT
        assert out.three_phase_trcu_power_on is False


class TestPlsInterlock:
    """§9 验收#7：PLS 未锁到位时不得进入最终断电态（S10）。"""

    def test_pls_missing_blocks_s10(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        sys_.sm.force(SystemState.S9_LOCK_CONFIRM)
        # TLS + 两吊挂锁 都 locked，但 PLS_R 未锁
        inp = inputs_factory(
            tr_position_pct=0.0,
            engine_running=True,
            locks=locks_factory(pls_r="unlocked"),
        )
        for _ in range(30):
            out = sys_.tick(inp, 0.1)
            assert out.state != SystemState.S10_STOWED_LOCKED_POWER_OFF


class TestWowConflictSafeSide:
    """§9 验收#2：WOW 双通道冲突不得误判为地面。"""

    def test_conflict_keeps_selected_false(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        conflict = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=True, lgcu2_mlg_wow=False,
            locks=locks_factory(),
        )
        for _ in range(30):
            out = sys_.tick(conflict, 0.1)
            assert out.selected_mlg_wow is False
            assert out.tr_wow is False

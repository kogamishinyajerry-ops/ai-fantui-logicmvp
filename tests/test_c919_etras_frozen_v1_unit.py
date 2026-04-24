"""单元测试：覆盖§9全部正常/冲突/抖动/保持/撤销/过温/PLS未锁场景"""
from __future__ import annotations

import pytest

from well_harness.adapters.c919_etras_frozen_v1 import (
    Cmd2Controller,
    Cmd3LatchController,
    C919ReverseThrustSystem,
    FrozenConfig,
    LockStatusAggregator,
    SystemState,
    TrWowFilter,
    compute_fadec_deploy_command,
    compute_fadec_stow_command,
    compute_selected_mlg_wow,
    derive_tr_command3_enable,
)


# ---------- §5.1 WOW selector ----------
class TestWowSelector:
    def test_both_valid_consistent_true(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=True, lgcu2_valid=True,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=True)
        assert compute_selected_mlg_wow(inp) is True

    def test_both_valid_consistent_false(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=True, lgcu2_valid=True,
                             lgcu1_mlg_wow=False, lgcu2_mlg_wow=False)
        assert compute_selected_mlg_wow(inp) is False

    def test_both_valid_conflict_forces_air(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=True, lgcu2_valid=True,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=False)
        assert compute_selected_mlg_wow(inp) is False  # 安全侧判空中

    def test_only_lgcu1_valid(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=True, lgcu2_valid=False,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=False)
        assert compute_selected_mlg_wow(inp) is True

    def test_only_lgcu2_valid(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=False, lgcu2_valid=True,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=True)
        assert compute_selected_mlg_wow(inp) is True

    def test_neither_valid(self, inputs_factory):
        inp = inputs_factory(lgcu1_valid=False, lgcu2_valid=False,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=True)
        assert compute_selected_mlg_wow(inp) is False


# ---------- §5.2 TR_WOW filter ----------
class TestTrWowFilter:
    def test_set_after_2p25s(self):
        f = TrWowFilter()
        # 2.0s -> still False
        for _ in range(20):
            assert f.tick(True, 0.1) is False
        # next tick crosses 2.25s
        assert f.tick(True, 0.3) is True

    def test_reset_after_120ms(self):
        f = TrWowFilter()
        for _ in range(23):
            f.tick(True, 0.1)
        assert f.state is True
        # drop
        assert f.tick(False, 0.05) is True   # 50ms < 120ms → hold
        assert f.tick(False, 0.05) is True   # 100ms < 120ms → hold
        assert f.tick(False, 0.05) is False  # 150ms >= 120ms → reset

    def test_jitter_holds_state(self):
        f = TrWowFilter()
        # 抖动：不足 Set/Reset 时间窗都应该保持前态
        for _ in range(50):
            f.tick(True, 0.01)
            f.tick(False, 0.01)
        assert f.state is False  # 从未持续 2.25s


# ---------- §5.3 CMD2 ----------
class TestCmd2:
    def test_cmd2_active_normal(self, inputs_factory):
        c = Cmd2Controller()
        inp = inputs_factory(atltla=True, tr_position_pct=10.0)
        assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is True

    def test_cmd2_blocked_by_inhibit(self, inputs_factory):
        c = Cmd2Controller()
        inp = inputs_factory(atltla=True, tr_inhibited=True)
        assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is False

    def test_cmd2_blocked_when_80pct(self, inputs_factory):
        c = Cmd2Controller()
        inp = inputs_factory(atltla=True, tr_position_pct=80.0)
        assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is False

    def test_cmd2_timer_30s_limit(self, inputs_factory):
        c = Cmd2Controller()
        inp = inputs_factory(atltla=True, tr_position_pct=10.0)
        for _ in range(299):
            assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is True
        # 30s reached → blocked
        assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is False

    def test_cmd2_timer_reset_on_rising_edge(self, inputs_factory):
        c = Cmd2Controller()
        high = inputs_factory(atltla=True, tr_position_pct=10.0)
        low = inputs_factory(atltla=False, tr_position_pct=10.0)
        for _ in range(320):  # 让计时器饱和
            c.tick(high, True, 0.1)
        # 上升沿前先拉低
        c.tick(low, True, 0.1)
        # 再拉高 → 计时器清零
        c.tick(high, True, 0.1)
        assert c.timer_s < 1.0


# ---------- §5.4 CMD3 ----------
class TestCmd3Latch:
    def _set_inp(self, factory):
        return factory(apwtla=True, engine_running=True, tr_inhibited=False)

    def test_set_by_rising_conditions(self, inputs_factory):
        c = Cmd3LatchController()
        inp = self._set_inp(inputs_factory)
        assert c.tick(inp, selected_mlg_wow=True, tr_command3_enable=True) is True

    def test_hold_after_apwtla_drops(self, inputs_factory):
        """冻结§2禁止项#3：回杆后 APWTLA=0 仍须保持。"""
        c = Cmd3LatchController()
        set_inp = self._set_inp(inputs_factory)
        c.tick(set_inp, selected_mlg_wow=True, tr_command3_enable=True)
        low_inp = inputs_factory(apwtla=False, engine_running=True)
        # tr_command3_enable 仍为 True（未收起未过温）→ 必须保持
        assert c.tick(low_inp, selected_mlg_wow=True, tr_command3_enable=True) is True

    def test_reset_by_stowed_and_locked(self, inputs_factory):
        c = Cmd3LatchController()
        set_inp = self._set_inp(inputs_factory)
        c.tick(set_inp, True, True)
        # 收起上锁 → tr_command3_enable=False → Reset
        e = derive_tr_command3_enable(True, False)
        assert e is False
        low_inp = inputs_factory(apwtla=False)
        assert c.tick(low_inp, True, tr_command3_enable=False) is False

    def test_reset_by_overtemp(self, inputs_factory):
        c = Cmd3LatchController()
        set_inp = self._set_inp(inputs_factory)
        c.tick(set_inp, True, True)
        e = derive_tr_command3_enable(False, True)
        assert e is False
        hot_inp = inputs_factory(apwtla=True, etras_over_temp_fault=True)
        assert c.tick(hot_inp, True, tr_command3_enable=False) is False

    # --- Codex CRITICAL 回归：锁死 v1.0 兜底行为（OPEN-Q-V2-01）---

    def test_airborne_apwtla_fault_does_not_energize_three_phase(
        self, inputs_factory, locks_factory
    ):
        """空中 APWTLA 故障不得上三相电（Codex 2026-04-24 CRITICAL 回归）。

        删除 v1.0 的 engine/WOW/inhibit 兜底后可复现错误通电 1s；本测试锁死
        兜底恢复后的正确行为——空中 + 全锁 + APWTLA=1 必须保持三相电断开。
        """
        sys_ = C919ReverseThrustSystem()
        airborne_with_apwtla = inputs_factory(
            lgcu1_valid=True, lgcu2_valid=True,
            lgcu1_mlg_wow=False, lgcu2_mlg_wow=False,  # airborne
            engine_running=False,                      # engine off
            tra_deg=-7.0, atltla=False, apwtla=True,   # APWTLA fault
            tr_position_pct=0.0,
            locks=locks_factory(),                     # 全 locked
        )
        for _ in range(15):  # 覆盖 1s stowed-and-locked dwell 窗口
            out = sys_.tick(airborne_with_apwtla, 0.1)
            assert out.three_phase_trcu_power_on is False, \
                "空中 APWTLA 故障不得在任何 tick 上三相电"

    def test_set_blocked_when_engine_off(self, inputs_factory):
        """engine_off + apwtla=True + enable=True → Set 不触发（v1.0 兜底）。"""
        c = Cmd3LatchController()
        inp = inputs_factory(apwtla=True, engine_running=False,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=True)
        assert c.tick(inp, selected_mlg_wow=True, tr_command3_enable=True) is False

    def test_set_blocked_when_inhibited(self, inputs_factory):
        """tr_inhibited=True + apwtla=True + enable=True → Set 不触发（v1.0 兜底）。"""
        c = Cmd3LatchController()
        inp = inputs_factory(apwtla=True, engine_running=True, tr_inhibited=True)
        assert c.tick(inp, selected_mlg_wow=True, tr_command3_enable=True) is False

    def test_set_blocked_when_airborne(self, inputs_factory):
        """selected_mlg_wow=False + apwtla=True + enable=True → Set 不触发（v1.0 兜底）。"""
        c = Cmd3LatchController()
        inp = inputs_factory(apwtla=True, engine_running=True)
        assert c.tick(inp, selected_mlg_wow=False, tr_command3_enable=True) is False

    def test_set_allowed_in_trcu_menu_mode_engine_off(self, inputs_factory):
        """维护工况：trcu_menu_mode=True + engine_off + apwtla=True → Set 触发。

        v1.0 Set 条件里 engine_running 与 trcu_menu_mode 是 OR 关系，维护台可以
        在发动机关停下测试三相电路（Codex round-2 补充用例）。
        """
        c = Cmd3LatchController()
        inp = inputs_factory(apwtla=True, engine_running=False, trcu_menu_mode=True,
                             lgcu1_mlg_wow=True, lgcu2_mlg_wow=True)
        assert c.tick(inp, selected_mlg_wow=True, tr_command3_enable=True) is True


# ---------- §5.5 Deploy ----------
class TestDeploy:
    def _args(self, factory, **kw):
        base = dict(engine_running=True, tra_deg=-12.0, n1k_pct=70.0,
                    max_n1k_deploy_limit_pct=84.0)
        base.update(kw)
        return factory(**base)

    def test_deploy_happy(self, inputs_factory):
        inp = self._args(inputs_factory)
        assert compute_fadec_deploy_command(inp, unlock_confirmed=True,
                                             tr_wow=True,
                                             tra_idle_reverse_deg=-11.74) is True

    def test_deploy_blocked_by_inhibit(self, inputs_factory):
        inp = self._args(inputs_factory, tr_inhibited=True)
        assert compute_fadec_deploy_command(inp, True, True, -11.74) is False

    def test_deploy_blocked_without_unlock(self, inputs_factory):
        inp = self._args(inputs_factory)
        assert compute_fadec_deploy_command(inp, False, True, -11.74) is False

    def test_deploy_blocked_without_tr_wow(self, inputs_factory):
        inp = self._args(inputs_factory)
        assert compute_fadec_deploy_command(inp, True, False, -11.74) is False

    def test_deploy_blocked_tra_not_past_idle(self, inputs_factory):
        inp = self._args(inputs_factory, tra_deg=-10.0)  # > -11.74
        assert compute_fadec_deploy_command(inp, True, True, -11.74) is False


# ---------- §5.6 Stow ----------
class TestStow:
    def test_stow_happy(self, inputs_factory):
        inp = inputs_factory(apwtla=False, tra_deg=0.0, n1k_pct=60.0,
                             max_n1k_stow_limit_pct=72.0)
        assert compute_fadec_stow_command(inp, True, False) is True

    def test_stow_blocked_by_apwtla_high(self, inputs_factory):
        inp = inputs_factory(apwtla=True, tra_deg=0.0, n1k_pct=60.0)
        assert compute_fadec_stow_command(inp, True, False) is False

    def test_stow_blocked_tra_below_zero(self, inputs_factory):
        inp = inputs_factory(apwtla=False, tra_deg=-5.0, n1k_pct=60.0)
        assert compute_fadec_stow_command(inp, True, False) is False

    def test_stow_blocked_no_3phase(self, inputs_factory):
        inp = inputs_factory(apwtla=False, tra_deg=0.0, n1k_pct=60.0)
        assert compute_fadec_stow_command(inp, False, False) is False

    def test_stow_blocked_already_stowed_and_locked(self, inputs_factory):
        inp = inputs_factory(apwtla=False, tra_deg=0.0, n1k_pct=60.0)
        assert compute_fadec_stow_command(inp, True, True) is False


# ---------- §5.7 Lock aggregator ----------
class TestLockAggregator:
    def test_unlock_confirmed_all_five_locks(self, locks_factory):
        # v2 §4.3: PLS 为主锁，全部五把锁均需 unlocked
        locks = locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                              pls_l="unlocked", pls_r="unlocked")
        assert LockStatusAggregator.compute_unlock_confirmed(locks) is True

    def test_unlock_not_confirmed_when_pls_locked(self, locks_factory):
        # PLS 任一未开锁 → 不得确认
        locks = locks_factory(tls="unlocked", pl_l="unlocked", pl_r="unlocked",
                              pls_l="locked", pls_r="unlocked")
        assert LockStatusAggregator.compute_unlock_confirmed(locks) is False

    def test_unlock_not_confirmed_when_tls_locked(self, locks_factory):
        locks = locks_factory(tls="locked", pl_l="unlocked", pl_r="unlocked",
                              pls_l="unlocked", pls_r="unlocked")
        assert LockStatusAggregator.compute_unlock_confirmed(locks) is False

    def test_stowed_and_locked_requires_1s_dwell(self, locks_factory):
        agg = LockStatusAggregator(stowed_locked_dwell_s=1.0)
        locks = locks_factory()  # 默认全 locked
        # 0.5s 不够
        for _ in range(10):
            assert agg.tick_stowed_and_locked(locks, 0.0, 0.05) is False
        # 再 0.5s → 达标
        for _ in range(10):
            agg.tick_stowed_and_locked(locks, 0.0, 0.05)
        assert agg.stowed_and_locked is True

    def test_stowed_and_locked_fails_when_pls_missing(self, locks_factory):
        """§9 验收#7：删 PLS 视为违背冻结基线；此处验证 PLS 任一未锁就不得确认。"""
        agg = LockStatusAggregator(stowed_locked_dwell_s=1.0)
        locks = locks_factory(pls_l="unlocked")
        for _ in range(100):
            agg.tick_stowed_and_locked(locks, 0.0, 0.05)
        assert agg.stowed_and_locked is False


# ---------- 冻结§9 验收：三相电保持 vs 回杆 ----------
class TestThreePhaseHoldOnThrottleBack:
    """回杆后三相供电必须保持至收起上锁确认完成（§9 验收#3）。"""

    def test_three_phase_holds_after_apwtla_drops(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        # 阶段1：建立 CMD3（地面 + engine + apwtla=1）
        on_inp = inputs_factory(apwtla=True, engine_running=True,
                                tr_position_pct=50.0,
                                locks=locks_factory(tls="unlocked",
                                                    pl_l="unlocked",
                                                    pl_r="unlocked"))
        # 等 TR_WOW=1（2.25s）
        for _ in range(30):
            sys_.tick(on_inp, 0.1)
        assert sys_.cmd3.latch is True

        # 阶段2：回杆 APWTLA=0，TR 还在展开位
        off_inp = inputs_factory(apwtla=False, engine_running=True,
                                  tr_position_pct=50.0,
                                  locks=locks_factory(tls="unlocked",
                                                      pl_l="unlocked",
                                                      pl_r="unlocked"))
        for _ in range(50):
            out = sys_.tick(off_inp, 0.1)
            assert out.three_phase_trcu_power_on is True, "回杆后不得立即掉三相电"


# ---------- 冻结§9 验收：过温保护 ----------
class TestOverTempProtection:
    def test_overtemp_forces_power_off_and_sf(self, inputs_factory, locks_factory):
        sys_ = C919ReverseThrustSystem()
        # 先建立 CMD3
        on_inp = inputs_factory(apwtla=True, engine_running=True,
                                tr_position_pct=50.0,
                                locks=locks_factory(tls="unlocked",
                                                    pl_l="unlocked",
                                                    pl_r="unlocked"))
        for _ in range(30):
            sys_.tick(on_inp, 0.1)

        # 过温故障
        hot_inp = inputs_factory(apwtla=True, engine_running=True,
                                  tr_position_pct=50.0,
                                  etras_over_temp_fault=True,
                                  locks=locks_factory(tls="unlocked",
                                                      pl_l="unlocked",
                                                      pl_r="unlocked"))
        out = sys_.tick(hot_inp, 0.1)
        assert out.three_phase_trcu_power_on is False
        assert out.state == SystemState.SF_ABORT_OR_FAULT


# ---------- §9 验收：80% 后 CMD2 撤销 ----------
class TestCmd2DroppedAt80Pct:
    def test_cmd2_off_at_80pct(self, inputs_factory):
        c = Cmd2Controller()
        inp = inputs_factory(atltla=True, tr_position_pct=85.0)
        assert c.tick(inp, selected_mlg_wow=True, dt_s=0.1) is False

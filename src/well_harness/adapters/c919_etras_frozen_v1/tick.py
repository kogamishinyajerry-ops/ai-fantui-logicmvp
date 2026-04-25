"""§7 周期执行：固定 12 步 tick() 编排"""
from __future__ import annotations

from typing import Optional

from .cmd2_controller import Cmd2Controller
from .cmd3_latch_controller import Cmd3LatchController, derive_tr_command3_enable
from .fadec_deploy_logic import compute_fadec_deploy_command
from .fadec_stow_logic import compute_fadec_stow_command
from .lock_status_aggregator import LockStatusAggregator
from .safety_interlock_manager import SafetyInterlockManager
from .signals import (
    FrozenConfig,
    Outputs,
    RawInputs,
    SystemState,
)
from .state_machine import StateMachine, StateMachineContext
from .telemetry_logger import TelemetryLogger
from .tr_wow_filter import TrWowFilter
from .wow_selector import compute_selected_mlg_wow


class C919ReverseThrustSystem:
    """冻结 V1.0 反推控制系统门面。"""

    def __init__(
        self,
        config: Optional[FrozenConfig] = None,
        logger: Optional[TelemetryLogger] = None,
        initial_state: SystemState = SystemState.S0_AIR_STOWED_LOCKED,
    ):
        self.config = config or FrozenConfig()
        self.logger = logger or TelemetryLogger()
        self._t_s = 0.0

        self.tr_wow_filter = TrWowFilter(
            set_delay_s=self.config.tr_wow_set_delay_s,
            reset_delay_s=self.config.tr_wow_reset_delay_s,
        )
        self.locks_agg = LockStatusAggregator(
            stowed_locked_dwell_s=self.config.stowed_and_locked_dwell_s,
        )
        self.cmd2 = Cmd2Controller(
            timer_limit_s=self.config.cmd2_timer_limit_s,
            tr_deployed_pct=self.config.tr_deployed_threshold_pct,
        )
        self.cmd3 = Cmd3LatchController()
        self.sm = StateMachine(initial=initial_state)
        self.safety = SafetyInterlockManager()

    @property
    def t_s(self) -> float:
        return self._t_s

    @property
    def state(self) -> SystemState:
        return self.sm.state

    def tick(self, inp: RawInputs, dt_s: Optional[float] = None) -> Outputs:
        dt = dt_s if dt_s is not None else self.config.step_s

        # Step 1 采样原始输入（已由调用方提供 inp）

        # Step 2 主轮载选择
        selected_mlg_wow = compute_selected_mlg_wow(inp)

        # Step 3 TR_WOW 滤波
        tr_wow = self.tr_wow_filter.tick(selected_mlg_wow, dt)

        # Step 4 锁聚合
        unlock_confirmed = LockStatusAggregator.compute_unlock_confirmed(inp.locks)
        tr_stowed_and_locked = self.locks_agg.tick_stowed_and_locked(
            inp.locks, inp.tr_position_pct, dt
        )

        # Step 5–6 CMD2 (计时器内部 tick)
        single_phase_unlock_power_on = self.cmd2.tick(inp, selected_mlg_wow, dt)

        # Step 7 派生 TR_Command3_Enable（FADEC→EICU 信号）
        tr_command3_enable = derive_tr_command3_enable(
            tr_stowed_and_locked, inp.etras_over_temp_fault
        )

        # Step 8 CMD3 锁存
        three_phase_trcu_power_on = self.cmd3.tick(
            inp, selected_mlg_wow, tr_command3_enable
        )

        # Step 9 Deploy
        fadec_deploy_command = compute_fadec_deploy_command(
            inp, unlock_confirmed, tr_wow, self.config.tra_idle_reverse_deg
        )

        # Step 10 Stow
        fadec_stow_command = compute_fadec_stow_command(
            inp,
            three_phase_trcu_power_on,
            tr_stowed_and_locked,
            self.config.tra_stow_threshold_deg,
        )

        # Step 11 状态机迁移（先 SF 抢占，再正常迁移）
        preempt = self.safety.preempt(self.sm.state, inp)
        if preempt is not None:
            self.sm.force(preempt)
        else:
            ctx = StateMachineContext(
                selected_mlg_wow=selected_mlg_wow,
                tr_wow=tr_wow,
                single_phase_unlock_power_on=single_phase_unlock_power_on,
                three_phase_trcu_power_on=three_phase_trcu_power_on,
                fadec_deploy_command=fadec_deploy_command,
                fadec_stow_command=fadec_stow_command,
                tr_stowed_and_locked=tr_stowed_and_locked,
                unlock_confirmed=unlock_confirmed,
            )
            self.sm.transition(inp, ctx)

        # Step 12 输出 + 日志
        outputs = Outputs(
            state=self.sm.state,
            selected_mlg_wow=selected_mlg_wow,
            tr_wow=tr_wow,
            single_phase_unlock_power_on=single_phase_unlock_power_on,
            three_phase_trcu_power_on=three_phase_trcu_power_on,
            unlock_confirmed=unlock_confirmed,
            fadec_deploy_command=fadec_deploy_command,
            fadec_stow_command=fadec_stow_command,
            tr_stowed_and_locked=tr_stowed_and_locked,
            tls_locked=inp.locks.tls_locked,
            tls_unlocked=inp.locks.tls_unlocked,
            pylon_lock_l_locked=inp.locks.pylon_lock_l_locked,
            pylon_lock_l_unlocked=inp.locks.pylon_lock_l_unlocked,
            pylon_lock_r_locked=inp.locks.pylon_lock_r_locked,
            pylon_lock_r_unlocked=inp.locks.pylon_lock_r_unlocked,
            pls_l_locked=inp.locks.pls_l_locked,
            pls_l_unlocked=inp.locks.pls_l_unlocked,
            pls_r_locked=inp.locks.pls_r_locked,
            pls_r_unlocked=inp.locks.pls_r_unlocked,
        )
        self.logger.log(self._t_s, outputs)
        self._t_s += dt
        return outputs

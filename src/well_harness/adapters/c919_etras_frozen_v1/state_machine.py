"""§6 状态机：S0..S10 + SF

迁移表严格对应冻结§6。SF 由 safety_interlock_manager 抢占（见 tick.py 中调用顺序）。
"""
from __future__ import annotations

from dataclasses import dataclass

from .signals import RawInputs, SystemState


@dataclass
class StateMachineContext:
    """状态机迁移所需的派生/输出快照。"""
    selected_mlg_wow: bool
    tr_wow: bool
    single_phase_unlock_power_on: bool
    three_phase_trcu_power_on: bool
    fadec_deploy_command: bool
    fadec_stow_command: bool
    tr_stowed_and_locked: bool
    unlock_confirmed: bool


class StateMachine:
    def __init__(self, initial: SystemState = SystemState.S0_AIR_STOWED_LOCKED):
        self._state = initial

    @property
    def state(self) -> SystemState:
        return self._state

    def force(self, s: SystemState) -> None:
        self._state = s

    def transition(self, inp: RawInputs, ctx: StateMachineContext) -> SystemState:
        s = self._state
        cfg_deployed_pct = 80.0

        # SF 恢复（仅从 SF → S10 当收起上锁且禁止/故障全部清除）
        if s == SystemState.SF_ABORT_OR_FAULT:
            if (not inp.tr_inhibited) and (not inp.etras_over_temp_fault) and ctx.tr_stowed_and_locked:
                self._state = SystemState.S10_STOWED_LOCKED_POWER_OFF
            return self._state

        if s == SystemState.S0_AIR_STOWED_LOCKED:
            # S0 → S1：地面且未抑制
            if ctx.selected_mlg_wow and (not inp.tr_inhibited):
                self._state = SystemState.S1_GROUND_ARMED

        elif s == SystemState.S1_GROUND_ARMED:
            if ctx.single_phase_unlock_power_on:
                self._state = SystemState.S2_UNLOCK_POWER_ON

        elif s == SystemState.S2_UNLOCK_POWER_ON:
            if ctx.three_phase_trcu_power_on:
                self._state = SystemState.S3_TRCU_POWER_ON

        elif s == SystemState.S3_TRCU_POWER_ON:
            if ctx.fadec_deploy_command:
                self._state = SystemState.S4_DEPLOYING

        elif s == SystemState.S4_DEPLOYING:
            if inp.tr_position_pct >= cfg_deployed_pct:
                self._state = SystemState.S5_DEPLOYED_IDLE_REVERSE

        elif s == SystemState.S5_DEPLOYED_IDLE_REVERSE:
            # S5 → S6：飞行员继续拉至最大反推（TRA 深反推）
            # 采用 TRA ≤ -25° 作为"最大反推区"（冻结未给具体阈值，保守）
            if inp.tra_deg <= -25.0:
                self._state = SystemState.S6_MAX_REVERSE

        elif s == SystemState.S6_MAX_REVERSE:
            # S6 → S7：飞行员回推，ATLTLA/APWTLA 归零
            if (not inp.atltla) and (not inp.apwtla):
                self._state = SystemState.S7_DECEL_WAIT_STOW

        elif s == SystemState.S7_DECEL_WAIT_STOW:
            if ctx.fadec_stow_command:
                self._state = SystemState.S8_STOWING

        elif s == SystemState.S8_STOWING:
            # S8 → S9：反推达到收起位并开始锁止确认（TR_Position==0）
            if inp.tr_position_pct == 0.0:
                self._state = SystemState.S9_LOCK_CONFIRM

        elif s == SystemState.S9_LOCK_CONFIRM:
            if ctx.tr_stowed_and_locked:
                self._state = SystemState.S10_STOWED_LOCKED_POWER_OFF

        # S10 是终态；若 selected_mlg_wow 再次变为假（回到空中）→ S0
        elif s == SystemState.S10_STOWED_LOCKED_POWER_OFF:
            if not ctx.selected_mlg_wow:
                self._state = SystemState.S0_AIR_STOWED_LOCKED

        return self._state

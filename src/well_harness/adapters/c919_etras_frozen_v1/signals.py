"""Frozen V1.0 信号字典 / 状态枚举 / Outputs"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SystemState(str, Enum):
    S0_AIR_STOWED_LOCKED = "S0_AIR_STOWED_LOCKED"
    S1_GROUND_ARMED = "S1_GROUND_ARMED"
    S2_UNLOCK_POWER_ON = "S2_UNLOCK_POWER_ON"
    S3_TRCU_POWER_ON = "S3_TRCU_POWER_ON"
    S4_DEPLOYING = "S4_DEPLOYING"
    S5_DEPLOYED_IDLE_REVERSE = "S5_DEPLOYED_IDLE_REVERSE"
    S6_MAX_REVERSE = "S6_MAX_REVERSE"
    S7_DECEL_WAIT_STOW = "S7_DECEL_WAIT_STOW"
    S8_STOWING = "S8_STOWING"
    S9_LOCK_CONFIRM = "S9_LOCK_CONFIRM"
    S10_STOWED_LOCKED_POWER_OFF = "S10_STOWED_LOCKED_POWER_OFF"
    SF_ABORT_OR_FAULT = "SF_ABORT_OR_FAULT"


@dataclass(frozen=True)
class FrozenConfig:
    step_s: float = 0.05
    tr_wow_set_delay_s: float = 2.25
    tr_wow_reset_delay_s: float = 0.120
    cmd2_timer_limit_s: float = 30.0
    tr_deployed_threshold_pct: float = 80.0
    stowed_and_locked_dwell_s: float = 1.0
    tra_idle_reverse_deg: float = -11.74
    tra_stow_threshold_deg: float = 0.0
    max_reverse_tra_deg: float = -32.0


@dataclass(frozen=True)
class LockInputs:
    """全部锁的原始 Locked/Unlocked 传感投票结果。冻结§3：TLS×1, PylonLock×2, PLS×2。"""
    tls_locked: bool
    tls_unlocked: bool
    pylon_lock_l_locked: bool
    pylon_lock_l_unlocked: bool
    pylon_lock_r_locked: bool
    pylon_lock_r_unlocked: bool
    pls_l_locked: bool
    pls_l_unlocked: bool
    pls_r_locked: bool
    pls_r_unlocked: bool


@dataclass(frozen=True)
class RawInputs:
    """§4 原始输入 snapshot（单时间步）。"""
    # LGCU WOW 两路
    lgcu1_mlg_wow: bool
    lgcu2_mlg_wow: bool
    lgcu1_valid: bool
    lgcu2_valid: bool

    # 油门台 / 解析
    tra_deg: float
    atltla: bool
    apwtla: bool

    # 系统模式
    tr_inhibited: bool
    engine_running: bool
    trcu_menu_mode: bool
    maintenance_cycle_on_going: bool

    # 反推位置 & N1k
    tr_position_pct: float
    n1k_pct: float
    max_n1k_deploy_limit_pct: float
    max_n1k_stow_limit_pct: float

    # 故障
    etras_over_temp_fault: bool

    # 锁
    locks: LockInputs


@dataclass(frozen=True)
class DerivedSignals:
    """§5 派生信号（tick 内计算）。"""
    selected_mlg_wow: bool
    tr_wow: bool
    unlock_confirmed: bool
    tr_stowed_and_locked: bool
    tr_command3_enable: bool


@dataclass(frozen=True)
class Outputs:
    """§8 对外最小输出合同。"""
    state: SystemState
    selected_mlg_wow: bool
    tr_wow: bool
    single_phase_unlock_power_on: bool          # CMD2 真实输出
    three_phase_trcu_power_on: bool             # CMD3 真实输出
    unlock_confirmed: bool
    fadec_deploy_command: bool
    fadec_stow_command: bool
    tr_stowed_and_locked: bool
    tls_locked: bool
    tls_unlocked: bool
    pylon_lock_l_locked: bool
    pylon_lock_l_unlocked: bool
    pylon_lock_r_locked: bool
    pylon_lock_r_unlocked: bool
    pls_l_locked: bool
    pls_l_unlocked: bool
    pls_r_locked: bool
    pls_r_unlocked: bool

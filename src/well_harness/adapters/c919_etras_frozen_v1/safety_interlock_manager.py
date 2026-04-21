"""§6 + §10 安全互锁：SF 抢占、禁止条件优先级

任何时刻：
  - TR_Inhibited == 1 → 任意状态立即迁入 SF_ABORT_OR_FAULT
  - E_TRAS_OverTemp_Fault == 1 → 任意状态立即迁入 SF_ABORT_OR_FAULT
SF 退出条件（保守）：两路禁止/故障均清除，且 TR_Stowed_And_Locked == TRUE 后回到 S10。
"""
from __future__ import annotations

from typing import Optional

from .signals import RawInputs, SystemState


class SafetyInterlockManager:
    @staticmethod
    def should_abort(inp: RawInputs) -> bool:
        return bool(inp.tr_inhibited or inp.etras_over_temp_fault)

    @staticmethod
    def can_recover_from_sf(inp: RawInputs, tr_stowed_and_locked: bool) -> bool:
        return (
            (not inp.tr_inhibited)
            and (not inp.etras_over_temp_fault)
            and tr_stowed_and_locked
        )

    @staticmethod
    def preempt(current: SystemState, inp: RawInputs) -> Optional[SystemState]:
        """若需 SF 抢占，返回 SF_ABORT_OR_FAULT，否则 None。"""
        if SafetyInterlockManager.should_abort(inp) and current != SystemState.SF_ABORT_OR_FAULT:
            return SystemState.SF_ABORT_OR_FAULT
        return None

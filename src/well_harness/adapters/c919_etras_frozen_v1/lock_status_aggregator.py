"""§5.7 锁聚合：Unlock_Confirmed + TR_Stowed_And_Locked(持续 1s 确认)"""
from __future__ import annotations

from .signals import LockInputs


class LockStatusAggregator:
    def __init__(self, stowed_locked_dwell_s: float = 1.0):
        self._dwell_limit = stowed_locked_dwell_s
        self._stowed_locked_acc_s = 0.0
        self._stowed_locked_latched = False

    @staticmethod
    def compute_unlock_confirmed(locks: LockInputs) -> bool:
        # §5.5 Deploy 的 Unlock_Confirmed：TLS + 两把吊挂锁的 Unlocked 传感均确认
        # （PLS 仅作为最终上锁确认的一部分，不参与解锁许可）
        return (
            locks.tls_unlocked
            and (not locks.tls_locked)
            and locks.pylon_lock_l_unlocked
            and (not locks.pylon_lock_l_locked)
            and locks.pylon_lock_r_unlocked
            and (not locks.pylon_lock_r_locked)
        )

    def tick_stowed_and_locked(
        self,
        locks: LockInputs,
        tr_position_pct: float,
        dt_s: float,
    ) -> bool:
        """§5.7：TR_Position==0 且 TLS / 两吊挂锁 / 两 PLS 均 Locked，持续 ≥1s。"""
        all_locked_and_stowed = (
            tr_position_pct == 0.0
            and locks.tls_locked and (not locks.tls_unlocked)
            and locks.pylon_lock_l_locked and (not locks.pylon_lock_l_unlocked)
            and locks.pylon_lock_r_locked and (not locks.pylon_lock_r_unlocked)
            and locks.pls_l_locked and (not locks.pls_l_unlocked)
            and locks.pls_r_locked and (not locks.pls_r_unlocked)
        )
        if all_locked_and_stowed:
            self._stowed_locked_acc_s += dt_s
            if self._stowed_locked_acc_s >= self._dwell_limit:
                self._stowed_locked_latched = True
        else:
            self._stowed_locked_acc_s = 0.0
            self._stowed_locked_latched = False
        return self._stowed_locked_latched

    @property
    def stowed_and_locked(self) -> bool:
        return self._stowed_locked_latched

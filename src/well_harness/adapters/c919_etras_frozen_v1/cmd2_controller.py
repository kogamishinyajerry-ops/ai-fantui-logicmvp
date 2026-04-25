"""§5.3 CMD2 单相解锁供电 + 30s 计时器

计时器语义（冻结派生）:
  - ATLTLA 上升沿(0→1) 时将计时器清零
  - ATLTLA == 1 持续期间按 dt 累加
  - ATLTLA == 0 时计时器保持（不再累加；下次上升沿才清零）
"""
from __future__ import annotations

from .signals import RawInputs


class Cmd2Controller:
    def __init__(self, timer_limit_s: float = 30.0, tr_deployed_pct: float = 80.0):
        self._limit = timer_limit_s
        self._deployed_pct = tr_deployed_pct
        self._timer_s = 0.0
        self._prev_atltla = False

    @property
    def timer_s(self) -> float:
        return self._timer_s

    def tick(self, inp: RawInputs, selected_mlg_wow: bool, dt_s: float) -> bool:
        # ATLTLA 上升沿 → 清零
        if inp.atltla and not self._prev_atltla:
            self._timer_s = 0.0
        if inp.atltla:
            self._timer_s += dt_s
        self._prev_atltla = inp.atltla

        single_phase_on = (
            inp.atltla
            and selected_mlg_wow
            and (not inp.tr_inhibited)
            and (self._timer_s < self._limit)
            and (inp.tr_position_pct < self._deployed_pct)
        )
        return bool(single_phase_on)

"""§5.2 TR_WOW 滤波：Set=2.25s, Reset=120ms, 其他保持"""
from __future__ import annotations


class TrWowFilter:
    def __init__(self, set_delay_s: float = 2.25, reset_delay_s: float = 0.120):
        self._set_delay = set_delay_s
        self._reset_delay = reset_delay_s
        self._true_acc_s = 0.0
        self._false_acc_s = 0.0
        self._state = False

    @property
    def state(self) -> bool:
        return self._state

    def tick(self, selected_mlg_wow: bool, dt_s: float) -> bool:
        if selected_mlg_wow:
            self._true_acc_s += dt_s
            self._false_acc_s = 0.0
            if self._true_acc_s >= self._set_delay:
                self._state = True
        else:
            self._false_acc_s += dt_s
            self._true_acc_s = 0.0
            if self._false_acc_s >= self._reset_delay:
                self._state = False
        return self._state

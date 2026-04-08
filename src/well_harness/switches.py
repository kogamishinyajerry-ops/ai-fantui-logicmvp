from __future__ import annotations

from dataclasses import dataclass

from well_harness.models import HarnessConfig, SwitchWindow


@dataclass(frozen=True)
class SwitchState:
    previous_tra_deg: float
    sw1: bool = False
    sw2: bool = False


class LatchedThrottleSwitches:
    """Resolve SW1 / SW2 from TRA using interval-triggered latch behavior.

    The document gives trigger windows, not a single exact actuation point, so
    this model triggers when the lever enters or crosses the window during
    reverse pull-back and resets when the lever is returned above the
    near-zero boundary.
    """

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()

    def update(self, state: SwitchState, tra_deg: float) -> SwitchState:
        sw1 = self._update_one(state.sw1, state.previous_tra_deg, tra_deg, self.config.sw1_window)
        sw2 = self._update_one(state.sw2, state.previous_tra_deg, tra_deg, self.config.sw2_window)
        return SwitchState(previous_tra_deg=tra_deg, sw1=sw1, sw2=sw2)

    @staticmethod
    def _update_one(previous_state: bool, previous_tra: float, tra_deg: float, window: SwitchWindow) -> bool:
        if previous_state:
            return tra_deg <= window.near_zero_deg
        if window.contains(tra_deg):
            return True
        if previous_tra > tra_deg:
            crossed_low = min(previous_tra, tra_deg) <= window.deep_reverse_deg
            crossed_high = max(previous_tra, tra_deg) >= window.near_zero_deg
            if crossed_low and crossed_high:
                return True
        return False

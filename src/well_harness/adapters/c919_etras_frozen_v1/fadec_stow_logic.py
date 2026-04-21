"""§5.6 FADEC Stow Command（冻结派生版）

FADEC_Stow_Command = TRUE 当且仅当：
  APWTLA == 0
  AND TRA >= 0deg
  AND N1k <= Max_N1k_Stow_Limit
  AND ThreePhaseTRCUPower_On == TRUE
  AND TR_Stowed_And_Locked == FALSE
"""
from __future__ import annotations

from .signals import RawInputs


def compute_fadec_stow_command(
    inp: RawInputs,
    three_phase_trcu_power_on: bool,
    tr_stowed_and_locked: bool,
    tra_stow_threshold_deg: float = 0.0,
) -> bool:
    return (
        (not inp.apwtla)
        and (inp.tra_deg >= tra_stow_threshold_deg)
        and (inp.n1k_pct <= inp.max_n1k_stow_limit_pct)
        and three_phase_trcu_power_on
        and (not tr_stowed_and_locked)
    )

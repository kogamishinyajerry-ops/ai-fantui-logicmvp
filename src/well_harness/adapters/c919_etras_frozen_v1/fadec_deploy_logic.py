"""§5.5 FADEC Deploy Command"""
from __future__ import annotations

from .signals import RawInputs


def compute_fadec_deploy_command(
    inp: RawInputs,
    unlock_confirmed: bool,
    tr_wow: bool,
    tra_idle_reverse_deg: float,
) -> bool:
    return (
        (inp.engine_running or inp.maintenance_cycle_on_going)
        and (not inp.tr_inhibited)
        and unlock_confirmed
        and tr_wow
        and (inp.n1k_pct <= inp.max_n1k_deploy_limit_pct)
        and (inp.tra_deg < tra_idle_reverse_deg)
    )

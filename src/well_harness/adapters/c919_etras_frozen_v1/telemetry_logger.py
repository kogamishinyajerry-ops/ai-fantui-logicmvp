"""日志合同：每 tick 结构化审计日志"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .signals import Outputs


class TelemetryLogger:
    def __init__(self, sink: Optional[List[Dict[str, Any]]] = None):
        self._sink: List[Dict[str, Any]] = sink if sink is not None else []

    def log(self, t_s: float, outputs: Outputs) -> Dict[str, Any]:
        rec = {
            "t_s": round(t_s, 6),
            "state": outputs.state.value,
            "Selected_MLG_WOW": outputs.selected_mlg_wow,
            "TR_WOW": outputs.tr_wow,
            "SinglePhaseUnlockPower_On": outputs.single_phase_unlock_power_on,
            "ThreePhaseTRCUPower_On": outputs.three_phase_trcu_power_on,
            "Unlock_Confirmed": outputs.unlock_confirmed,
            "FADEC_Deploy_Command": outputs.fadec_deploy_command,
            "FADEC_Stow_Command": outputs.fadec_stow_command,
            "TR_Stowed_And_Locked": outputs.tr_stowed_and_locked,
            "TLS_Locked": outputs.tls_locked,
            "TLS_Unlocked": outputs.tls_unlocked,
            "PylonLock_L_Locked": outputs.pylon_lock_l_locked,
            "PylonLock_L_Unlocked": outputs.pylon_lock_l_unlocked,
            "PylonLock_R_Locked": outputs.pylon_lock_r_locked,
            "PylonLock_R_Unlocked": outputs.pylon_lock_r_unlocked,
            "PLS_L_Locked": outputs.pls_l_locked,
            "PLS_L_Unlocked": outputs.pls_l_unlocked,
            "PLS_R_Locked": outputs.pls_r_locked,
            "PLS_R_Unlocked": outputs.pls_r_unlocked,
        }
        self._sink.append(rec)
        return rec

    @property
    def records(self) -> List[Dict[str, Any]]:
        return list(self._sink)

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in self._sink)

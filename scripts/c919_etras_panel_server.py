"""C919 E-TRAS 控制逻辑面板服务器 — 冻结版 V1.0（有状态 tick 模型）"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any, Dict
from urllib.parse import urlparse

# Add src/ to path for well_harness imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from well_harness.adapters.c919_etras_frozen_v1 import (
    C919ReverseThrustSystem,
    FrozenConfig,
    LockInputs,
    RawInputs,
    SystemState,
    TelemetryLogger,
)
from well_harness.adapters.c919_etras_frozen_v1.cmd3_latch_controller import Cmd3LatchController

PORT = 9191
STATIC = Path(__file__).resolve().parents[2] / "src" / "well_harness" / "static" / "c919_etras_panel"

_config = FrozenConfig()
_logger = TelemetryLogger()
_system = C919ReverseThrustSystem(config=_config, logger=_logger)
_lock = Lock()  # 线程安全


def _parse_inputs(body: Dict[str, Any]) -> RawInputs:
    def b(key: str, default: bool = False) -> bool:
        return bool(body.get(key, default))

    def f(key: str, default: float = 0.0) -> float:
        return float(body.get(key, default))

    locks_raw = body.get("locks", {})
    locks = LockInputs(
        tls_locked=bool(locks_raw.get("tls_locked", True)),
        tls_unlocked=bool(locks_raw.get("tls_unlocked", False)),
        pylon_lock_l_locked=bool(locks_raw.get("pylon_lock_l_locked", True)),
        pylon_lock_l_unlocked=bool(locks_raw.get("pylon_lock_l_unlocked", False)),
        pylon_lock_r_locked=bool(locks_raw.get("pylon_lock_r_locked", True)),
        pylon_lock_r_unlocked=bool(locks_raw.get("pylon_lock_r_unlocked", False)),
        pls_l_locked=bool(locks_raw.get("pls_l_locked", True)),
        pls_l_unlocked=bool(locks_raw.get("pls_l_unlocked", False)),
        pls_r_locked=bool(locks_raw.get("pls_r_locked", True)),
        pls_r_unlocked=bool(locks_raw.get("pls_r_unlocked", False)),
    )
    return RawInputs(
        lgcu1_mlg_wow=b("lgcu1_mlg_wow"),
        lgcu2_mlg_wow=b("lgcu2_mlg_wow"),
        lgcu1_valid=b("lgcu1_valid", True),
        lgcu2_valid=b("lgcu2_valid", True),
        tra_deg=f("tra_deg"),
        atltla=b("atltla"),
        apwtla=b("apwtla"),
        tr_inhibited=b("tr_inhibited"),
        engine_running=b("engine_running"),
        trcu_menu_mode=b("trcu_menu_mode"),
        maintenance_cycle_on_going=b("maintenance_cycle_on_going"),
        tr_position_pct=f("tr_position_pct"),
        n1k_pct=f("n1k_pct", 50.0),
        max_n1k_deploy_limit_pct=f("max_n1k_deploy_limit_pct", 84.0),
        max_n1k_stow_limit_pct=f("max_n1k_stow_limit_pct", 72.0),
        etras_over_temp_fault=b("etras_over_temp_fault"),
        locks=locks,
    )


def _build_tick_response(outputs, sys_ref: C919ReverseThrustSystem, inp: RawInputs) -> dict:
    tr_cmd3_enable = Cmd3LatchController.derive_tr_command3_enable(
        outputs.tr_stowed_and_locked, inp.etras_over_temp_fault
    )
    return {
        "t_s": round(sys_ref.t_s, 3),
        "state": outputs.state.value,
        "derived": {
            "selected_mlg_wow": outputs.selected_mlg_wow,
            "tr_wow": outputs.tr_wow,
            "tr_wow_acc_s": round(sys_ref.tr_wow_filter._true_acc_s, 3),
            "unlock_confirmed": outputs.unlock_confirmed,
            "tr_stowed_and_locked": outputs.tr_stowed_and_locked,
            "stowed_acc_s": round(sys_ref.locks_agg._stowed_locked_acc_s, 3),
            "tr_command3_enable": tr_cmd3_enable,
            "cmd3_latch": sys_ref.cmd3.latch,
            "cmd2_timer_s": round(sys_ref.cmd2.timer_s, 2),
        },
        "outputs": {
            "single_phase_unlock_power_on": outputs.single_phase_unlock_power_on,
            "three_phase_trcu_power_on": outputs.three_phase_trcu_power_on,
            "fadec_deploy_command": outputs.fadec_deploy_command,
            "fadec_stow_command": outputs.fadec_stow_command,
            "tr_stowed_and_locked": outputs.tr_stowed_and_locked,
            "unlock_confirmed": outputs.unlock_confirmed,
        },
        "locks": {
            "tls_locked": outputs.tls_locked,
            "tls_unlocked": outputs.tls_unlocked,
            "pylon_lock_l_locked": outputs.pylon_lock_l_locked,
            "pylon_lock_l_unlocked": outputs.pylon_lock_l_unlocked,
            "pylon_lock_r_locked": outputs.pylon_lock_r_locked,
            "pylon_lock_r_unlocked": outputs.pylon_lock_r_unlocked,
            "pls_l_locked": outputs.pls_l_locked,
            "pls_l_unlocked": outputs.pls_l_unlocked,
            "pls_r_locked": outputs.pls_r_locked,
            "pls_r_unlocked": outputs.pls_r_unlocked,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._serve_file(STATIC / "index.html", "text/html; charset=utf-8")
        elif path == "/api/state":
            with _lock:
                self._json({
                    "state": _system.state.value,
                    "t_s": round(_system.t_s, 3),
                    "cmd2_timer_s": round(_system.cmd2.timer_s, 2),
                    "cmd3_latch": _system.cmd3.latch,
                })
        elif path == "/api/log":
            with _lock:
                recs = _logger.records[-200:]
            self._json(recs)
        elif path == "/api/config":
            self._json({
                "step_s": _config.step_s,
                "tr_wow_set_delay_s": _config.tr_wow_set_delay_s,
                "tr_wow_reset_delay_s": _config.tr_wow_reset_delay_s,
                "cmd2_timer_limit_s": _config.cmd2_timer_limit_s,
                "tr_deployed_threshold_pct": _config.tr_deployed_threshold_pct,
                "stowed_and_locked_dwell_s": _config.stowed_and_locked_dwell_s,
                "tra_idle_reverse_deg": _config.tra_idle_reverse_deg,
                "tra_stow_threshold_deg": _config.tra_stow_threshold_deg,
            })
        else:
            self._404()

    def do_POST(self):
        global _system, _logger
        path = urlparse(self.path).path
        if path == "/api/tick":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body) if body else {}
                inp = _parse_inputs(data)
                dt = float(data.get("dt_s", _config.step_s))
                with _lock:
                    out = _system.tick(inp, dt)
                    resp = _build_tick_response(out, _system, inp)
                self._json(resp)
            except Exception as e:
                self._json({"error": str(e)}, 400)
        elif path == "/api/reset":
            with _lock:
                _logger = TelemetryLogger()
                _system = C919ReverseThrustSystem(config=_config, logger=_logger)
            self._json({"ok": True, "state": SystemState.S0_AIR_STOWED_LOCKED.value})
        else:
            self._404()

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _serve_file(self, path: Path, ct: str):
        if not path.exists():
            self._404(); return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(data))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(data))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _404(self):
        self.send_response(404); self.end_headers()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


if __name__ == "__main__":
    STATIC.mkdir(exist_ok=True)
    print(f"C919 E-TRAS 控制逻辑面板 V1.0 Frozen → http://localhost:{PORT}")
    with ThreadingHTTPServer(("", PORT), Handler) as srv:
        srv.serve_forever()

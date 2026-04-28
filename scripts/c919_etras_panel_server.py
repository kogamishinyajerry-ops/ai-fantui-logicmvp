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
_REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo root
sys.path.insert(0, str(_REPO_ROOT / "src"))

from well_harness.adapters.c919_etras_frozen_v1 import (
    C919ReverseThrustSystem,
    FrozenConfig,
    LockInputs,
    RawInputs,
    SystemState,
    TelemetryLogger,
)
from well_harness.adapters.c919_etras_frozen_v1.cmd3_latch_controller import (
    Cmd3LatchController,
    derive_tr_command3_enable,
)
from well_harness.timeline_engine import TimelinePlayer, parse_timeline
from well_harness.timeline_engine.validator import ValidationError as TimelineValidationError
from well_harness.timeline_engine.executors.c919_etras import C919ETRASExecutor

PORT = 9191
STATIC = _REPO_ROOT / "src" / "well_harness" / "static" / "c919_etras_panel"
# Phase UI-F (2026-04-22): shared unified-nav.css lives in parent static dir,
# served from /unified-nav.css on this server so panel pages can `<link>` it.
SHARED_STATIC_ROOT = _REPO_ROOT / "src" / "well_harness" / "static"

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
    tr_cmd3_enable = derive_tr_command3_enable(
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


# ---- Timeline-simulate endpoint (PR-3) -------------------------------------

_TIMELINE_MAX_DURATION_S = 600.0
_TIMELINE_MIN_STEP_S = 0.01
_TIMELINE_MAX_TICKS = 20_000
_TIMELINE_MAX_EVENTS = 500


def _handle_c919_timeline_simulate(request_payload: dict) -> dict:
    """Run a Timeline against the C919 E-TRAS executor and return trace JSON."""
    try:
        timeline = parse_timeline(request_payload)
    except TimelineValidationError as exc:
        return {"_status": 400, "error": "invalid_timeline", "field": exc.field, "message": exc.message}

    if timeline.system != "c919-etras":
        return {
            "_status": 400,
            "error": "unsupported_system",
            "message": f"this endpoint only runs C919 E-TRAS timelines; got system={timeline.system!r}",
        }
    if timeline.duration_s > _TIMELINE_MAX_DURATION_S:
        return {"_status": 400, "error": "timeline_too_long",
                "message": f"duration_s must be <= {_TIMELINE_MAX_DURATION_S}s"}
    if timeline.step_s < _TIMELINE_MIN_STEP_S:
        return {"_status": 400, "error": "timeline_step_too_small",
                "message": f"step_s must be >= {_TIMELINE_MIN_STEP_S}s"}
    tick_count = int(timeline.duration_s / timeline.step_s) + 1
    if tick_count > _TIMELINE_MAX_TICKS:
        return {"_status": 400, "error": "timeline_too_many_ticks",
                "message": f"duration_s/step_s would produce {tick_count} ticks; max {_TIMELINE_MAX_TICKS}"}
    if len(timeline.events) > _TIMELINE_MAX_EVENTS:
        return {"_status": 400, "error": "timeline_too_many_events",
                "message": f"events list has {len(timeline.events)} entries; max {_TIMELINE_MAX_EVENTS}"}

    try:
        executor = C919ETRASExecutor()
        trace = TimelinePlayer(timeline, executor).run()
    except (ValueError, TypeError) as exc:
        return {"_status": 400, "error": "invalid_timeline", "message": str(exc)}
    return _c919_timeline_trace_to_json(trace)


def _c919_timeline_trace_to_json(trace) -> dict:
    # TimelineOutcome.extra is populated by C919ETRASExecutor.summarize_outcome
    # (Codex PR-3 MAJOR #3 architecture fix). Fall back to computing here if
    # the player ran without summarize_outcome support.
    extra = trace.outcome.extra or {}
    frames = trace.frames
    c919_deployed = extra.get("deployed_successfully")
    if c919_deployed is None:
        c919_deployed = any(f.outputs.get("fadec_deploy_command") is True for f in frames)
    c919_reached = extra.get("reached_deployed_state")
    if c919_reached is None:
        c919_reached = any(
            f.outputs.get("state") in ("S5_DEPLOYED_IDLE_REVERSE", "S6_MAX_REVERSE") for f in frames
        )
    final_state = extra.get("final_state") or (frames[-1].outputs.get("state") if frames else None)
    tr_position_peak = extra.get("tr_position_peak_pct")
    if tr_position_peak is None:
        tr_position_peak = max((f.outputs.get("tr_position_pct", 0.0) for f in frames), default=0.0)

    return {
        "timeline": {
            "system": trace.timeline.system,
            "step_s": trace.timeline.step_s,
            "duration_s": trace.timeline.duration_s,
            "title": trace.timeline.title,
            "description": trace.timeline.description,
        },
        "frames": [
            {
                "tick": f.tick,
                "t_s": f.t_s,
                "phase": f.phase,
                "inputs": f.inputs,
                "outputs": f.outputs,
                "logic_states": f.logic_states,
                "active_faults": f.active_faults,
                "events_fired": f.events_fired,
            }
            for f in trace.frames
        ],
        "transitions": [
            {
                "tick": f.tick,
                "t_s": f.t_s,
                "phase": f.phase,
                "logic_states": f.logic_states,
                "active_faults": f.active_faults,
            }
            for f in trace.transitions
        ],
        "assertions": [
            {
                "at_s": a.at_s,
                "target": a.target,
                "expected": a.expected,
                "observed": a.observed,
                "passed": a.passed,
                "note": a.note,
            }
            for a in trace.assertions
        ],
        "outcome": {
            "deployed_successfully": c919_deployed,
            "reached_deployed_state": c919_reached,
            "final_state": final_state,
            "tr_position_peak_pct": tr_position_peak,
            "logic_first_active_t_s": trace.outcome.logic_first_active_t_s,
            "logic_first_blocked_t_s": trace.outcome.logic_first_blocked_t_s,
            "failure_cascade": trace.outcome.failure_cascade,
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
        elif path in ("/circuit", "/circuit.html"):
            self._serve_file(STATIC / "circuit.html", "text/html; charset=utf-8")
        elif path == "/unified-nav.css":
            # Serve shared unified-nav styles from parent static dir so pages
            # on this port can link to /unified-nav.css like pages on :8002.
            self._serve_file(SHARED_STATIC_ROOT / "unified-nav.css", "text/css; charset=utf-8")
        elif path == "/etras_chrome.css":
            # P56-01 (2026-04-28): the C919 panel + fan_console both link
            # the extracted shared chrome (color tokens, header bar, .btn,
            # .sec, .tog, scrollbar, etc.). The :9191 standalone server
            # must whitelist it the same way it does /unified-nav.css —
            # otherwise the live panel 404s and loses the extracted styles.
            self._serve_file(SHARED_STATIC_ROOT / "etras_chrome.css", "text/css; charset=utf-8")
        elif path == "/timeseries_chart.js":
            # Shared timeseries renderer used by the live chart on this panel.
            self._serve_file(SHARED_STATIC_ROOT / "timeseries_chart.js", "application/javascript; charset=utf-8")
        elif path in ("/timeline-sim.html", "/timeline-sim"):
            # PR-4: shared timeline-simulator UI; page auto-routes its POST to
            # port 9191 for c919-etras timelines, so access from either port works.
            self._serve_file(SHARED_STATIC_ROOT / "timeline-sim.html", "text/html; charset=utf-8")
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
        elif path == "/api/timeline-simulate":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError as e:
                self._json({"error": "invalid_json", "message": str(e)}, 400)
                return
            resp = _handle_c919_timeline_simulate(data)
            self._json(resp, code=resp.pop("_status", 200))
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

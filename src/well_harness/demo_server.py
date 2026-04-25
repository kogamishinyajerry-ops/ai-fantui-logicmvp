"""Small local UI server for the deterministic demo reasoning layer."""

from __future__ import annotations

import argparse
from dataclasses import replace
from functools import lru_cache
import json
import math
import re
from typing import Any
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
from well_harness.adapters.efds_adapter import build_efds_controller_adapter
from well_harness.adapters.c919_etras_adapter import build_c919_etras_controller_adapter
from well_harness.document_intake import (
    apply_safe_schema_repairs,
    assess_intake_packet,
    build_clarification_brief,
    intake_packet_from_dict,
    intake_packet_to_dict,
    intake_template_payload,
)
from well_harness.fantui_tick import FantuiTickSystem, parse_pilot_inputs
from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState
from well_harness.timeline_engine import (
    TimelinePlayer,
    ValidationError as TimelineValidationError,
    parse_timeline,
)
from well_harness.timeline_engine.executors.fantui import FantuiExecutor
from well_harness.workbench_bundle import (
    SandboxEscapeError,
    archive_workbench_bundle,
    build_workbench_bundle,
    load_workbench_archive_manifest,
    load_workbench_archive_restore_payload,
)
STATIC_DIR = Path(__file__).with_name("static")
REFERENCE_PACKET_DIR = Path(__file__).with_name("reference_packets")
REFERENCE_PACKET_PATH = REFERENCE_PACKET_DIR / "custom_reverse_control_v1.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "runs"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
# Server-side DoS guard: 10 MB, aligned with browser client limit.
_MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml; charset=utf-8",
    ".ico": "image/x-icon",
    ".png": "image/png",
}
SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
TRA_L4_LOCK_DEG = -14.0
MONITOR_TIMELINE_PATH = "/api/monitor-timeline"
WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
MONITOR_RA_START_FT = 7.0
MONITOR_RA_RATE_FT_PER_S = 1.0
MONITOR_TRA_START_S = 1.0
MONITOR_TRA_RATE_DEG_PER_S = 10.0
MONITOR_TRA_LOCK_DEG = -14.0
MONITOR_VDT_START_S = 2.4
MONITOR_VDT_RATE_PERCENT_PER_S = 50.0
MONITOR_ACTIVE_END_S = 4.4
MONITOR_TIMELINE_END_S = 7.0
MONITOR_TIMELINE_COMPRESSION_RATIO = 10.0
MONITOR_ENGINE_RUNNING = True
MONITOR_AIRCRAFT_ON_GROUND = True
MONITOR_REVERSER_INHIBITED = False
MONITOR_EEC_ENABLE = True

# Reverse diagnosis API (P19.6)
DIAGNOSIS_RUN_PATH = "/api/diagnosis/run"
# Monte Carlo reliability API (P19.7)
MONTE_CARLO_RUN_PATH = "/api/monte-carlo/run"
# Hardware schema discovery (P19.8)
HARDWARE_SCHEMA_PATH = "/api/hardware/schema"
SENSITIVITY_SWEEP_PATH = "/api/sensitivity-sweep"
# FANTUI stateful tick endpoints — live counterpart to C919 /api/tick.
# The existing /api/lever-snapshot stays stateless; this triad is separate
# so the two surfaces don't fight each other or share global state.
FANTUI_TICK_PATH = "/api/fantui/tick"
FANTUI_RESET_PATH = "/api/fantui/reset"
FANTUI_LOG_PATH = "/api/fantui/log"
FANTUI_STATE_PATH = "/api/fantui/state"
FANTUI_SET_VDT_PATH = "/api/fantui/set_vdt"

STATIC_ROUTE_ALIASES = {
    "/favicon.ico": "favicon.svg",
    "/apple-touch-icon.png": "apple-touch-icon.svg",
}

SENSITIVITY_SWEEP_DEFAULT_RA_VALUES = (2.0, 5.0, 10.0, 20.0, 40.0)
SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES = (-28.0, -20.0, -15.0, -11.0, -6.0)
SENSITIVITY_SWEEP_DEFAULT_OUTCOMES = (
    "logic1_active",
    "logic3_active",
    "thr_lock_active",
    "deploy_confirmed",
)
SENSITIVITY_SWEEP_ALLOWED_OUTCOMES = frozenset(
    {
        "logic1_active",
        "logic2_active",
        "logic3_active",
        "thr_lock_active",
        "deploy_confirmed",
        "tls_unlocked",
        "pls_unlocked",
    }
)

_SYSTEM_YAML_MAP = {
    "thrust-reverser": "thrust_reverser_hardware_v1.yaml",
    "landing-gear": "landing_gear_hardware_v1.yaml",
    "bleed-air": "bleed_air_hardware_v1.yaml",
    "c919-etras": "c919_etras_hardware_v1.yaml",
}

# Systems whose YAML format is loadable by load_thrust_reverser_hardware.
# Landing-gear and bleed-air YAMLs use a different schema and cannot be loaded
# by the thrust-reverser-specific engine; they are served via the generic loader
# in _handle_hardware_schema only.
_SUPPORTED_FOR_ANALYSIS = frozenset({"thrust-reverser"})

MONITOR_N1K = 35.0
MONITOR_MAX_N1K_DEPLOY_LIMIT = 60.0
LEVER_NUMERIC_INPUTS = {
    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
}
LEVER_BOOLEAN_INPUTS = {
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
}
LEVER_FEEDBACK_MODES = {
    "auto_scrubber",
    "manual_feedback_override",
}
LEVER_SNAPSHOT_FAULT_NODE_ALIASES = {
    "sw1_input": "sw1",
    "sw2_input": "sw2",
}
LEVER_SNAPSHOT_FAULT_NODES = {
    "sw1",
    "sw2",
    "radio_altitude_ft",
    "n1k",
    "tls115",
    "logic1",
    "logic2",
    "logic3",
    "logic4",
    "thr_lock",
    "vdt90",
    "sw1_input",
    "sw2_input",
}
LEVER_SNAPSHOT_FAULT_TYPES = {
    "stuck_off",
    "stuck_on",
    "sensor_zero",
    "logic_stuck_false",
    "cmd_blocked",
}
FAULT_INJECTION_REASON = "fault_injection"

# ── FANTUI stateful tick singleton ─────────────────────────────────────────
# Module-level state. ``FantuiTickSystem`` is itself thread-safe — see its
# internal ``_lock`` — so no outer lock is needed here. Restarting the server
# clears the state; ``POST /api/fantui/reset`` is the in-process reset.
# ``_FANTUI_LOCK`` is kept as an alias to the system's internal lock for
# backward-compatibility with any test that reached in directly.
_FANTUI_SYSTEM = FantuiTickSystem()
_FANTUI_LOCK = _FANTUI_SYSTEM._lock


class DemoRequestHandler(BaseHTTPRequestHandler):
    """Serve the static demo shell and a thin JSON API around DemoAnswer."""

    server_version = "WellHarnessDemo/1.0"

    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in STATIC_ROUTE_ALIASES:
            self._serve_static(STATIC_ROUTE_ALIASES[parsed.path])
            return
        if parsed.path == MONITOR_TIMELINE_PATH:
            self._send_json(200, monitor_timeline_payload())
            return
        if parsed.path == WORKBENCH_BOOTSTRAP_PATH:
            self._send_json(200, workbench_bootstrap_payload())
            return
        if parsed.path == SYSTEM_SNAPSHOT_PATH:
            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
            self._send_json(200, system_snapshot_payload(system_id))
            return
        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
            self._send_json(200, workbench_recent_archives_payload())
            return

        # Default entry: unified landing page with 2x3 card grid
        # (Phase A: chat.html shelved; Phase UI-C: root now serves index.html
        # instead of demo.html so user can reach all 6 surfaces.)
        if parsed.path in ("", "/"):
            self._serve_static("index.html")
            return

        if parsed.path in ("/demo.html", "/expert/demo.html"):
            self._serve_static("demo.html")
            return

        if parsed.path in ("/workbench/start", "/workbench/start.html"):
            self._serve_static("workbench_start.html")
            return

        if parsed.path in ("/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"):
            self._serve_static("workbench_bundle.html")
            return

        if parsed.path in ("/workbench", "/workbench.html", "/expert/workbench.html"):
            self._serve_static("workbench.html")
            return

        relative_path = unquote(parsed.path.lstrip("/"))
        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
            self._serve_static(relative_path)
            return

        # P19.8: Hardware schema discovery
        if parsed.path == HARDWARE_SCHEMA_PATH:
            system_id = parse_qs(parsed.query).get("system_id", ["thrust-reverser"])[0]
            self._handle_hardware_schema(system_id=system_id)
            return

        if parsed.path == FANTUI_LOG_PATH:
            # records() is internally locked; the copy it returns is
            # self-contained so JSON serialization can run unlocked.
            recs = _FANTUI_SYSTEM.records()
            self._send_json(200, recs)
            return

        if parsed.path == FANTUI_STATE_PATH:
            # Atomic snapshot — one lock acquisition covers all fields
            # so callers don't observe torn state.
            self._send_json(200, _FANTUI_SYSTEM.snapshot())
            return

        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in {
            "/api/demo",
            "/api/lever-snapshot",
            "/api/timeline-simulate",
            SYSTEM_SNAPSHOT_POST_PATH,
            WORKBENCH_BUNDLE_PATH,
            WORKBENCH_REPAIR_PATH,
            WORKBENCH_ARCHIVE_RESTORE_PATH,
            DIAGNOSIS_RUN_PATH,
            MONTE_CARLO_RUN_PATH,
            HARDWARE_SCHEMA_PATH,
            SENSITIVITY_SWEEP_PATH,
            FANTUI_TICK_PATH,
            FANTUI_RESET_PATH,
            FANTUI_SET_VDT_PATH,
        }:
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return

        # Guard: reject oversized payloads before reading
        if content_length and content_length > _MAX_DOCUMENT_BYTES:
            self._send_json(413, {"error": "payload_too_large", "message": f"Request body exceeds maximum of {_MAX_DOCUMENT_BYTES} bytes."})
            return

        # Guard: enforce Content-Type whitelist (defense-in-depth; browser enforces this too)
        content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
        allowed_types = {"application/json"}
        if content_type and content_type not in allowed_types:
            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json."})
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            request_payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(request_payload, dict):
            self._send_json(400, {"error": "invalid_json_object"})
            return

        if parsed.path == "/api/lever-snapshot":
            lever_inputs, error_payload = parse_lever_snapshot_request(request_payload)
            if error_payload is not None:
                # E11-14: parser may attach `_status` (e.g., 409 for manual_override_unsigned);
                # default to 400 for legacy parse errors.
                status_code = error_payload.pop("_status", 400)
                self._send_json(status_code, error_payload)
                return

            fault_injections = lever_inputs.pop("_fault_injections", None)
            self._send_json(
                200,
                lever_snapshot_payload(
                    **lever_inputs,
                    fault_injections=fault_injections,
                ),
            )
            return
        if parsed.path == "/api/timeline-simulate":
            result = _handle_timeline_simulate(request_payload)
            status = result.pop("_status", 200)
            self._send_json(status, result)
            return
        if parsed.path == FANTUI_TICK_PATH:
            status, result = _handle_fantui_tick(request_payload)
            self._send_json(status, result)
            return
        if parsed.path == FANTUI_RESET_PATH:
            _FANTUI_SYSTEM.reset()
            self._send_json(200, {"ok": True, "t_s": 0.0})
            return
        if parsed.path == FANTUI_SET_VDT_PATH:
            # E11-14 R2 (P2 BLOCKER #2, 2026-04-25): set_vdt is a test probe
            # that bypasses the /api/lever-snapshot sign-off contract. The
            # endpoint stays available for the fan-console debug UI but now
            # requires an explicit `test_probe_acknowledgment` field so a
            # caller cannot accidentally use it to inject manual feedback
            # while believing they're going through the authority chain.
            # The 409 message explains the alternative (use /api/lever-snapshot
            # with sign-off when authority semantics matter).
            ack = request_payload.get("test_probe_acknowledgment")
            if ack is not True:
                self._send_json(
                    409,
                    {
                        "error": "test_probe_unacknowledged",
                        "message": (
                            "/api/fantui/set_vdt is a test probe that bypasses the "
                            "manual_feedback_override authority chain. To use it from "
                            "tests/dev tooling, pass test_probe_acknowledgment=true. "
                            "For authoritative manual feedback, use /api/lever-snapshot "
                            "with feedback_mode=manual_feedback_override + sign-off."
                        ),
                        # E11-14 R3 (P2 R2 IMPORTANT #4 fix, 2026-04-25): every 409
                        # path must disclose the deferred replay/freshness gap so
                        # callers don't mistake structural validation for latched
                        # authorization. set_vdt's bypass nature is itself a live
                        # residual risk surface.
                        "residual_risk": (
                            "Test-probe bypass remains structural; "
                            "test_probe_acknowledgment=true is not authentication. "
                            "Replay/nonce/freshness validation and one-shot latching are "
                            "scoped to E11-16 (approval endpoint hardening)."
                        ),
                    },
                )
                return
            try:
                pct = float(request_payload.get("deploy_position_percent", 0))
            except (TypeError, ValueError):
                self._send_json(400, {"error": "deploy_position_percent must be a number"})
                return
            try:
                _FANTUI_SYSTEM.set_plant_position(pct)
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, _FANTUI_SYSTEM.snapshot())
            return
        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
            system_id = request_payload.get("system_id")
            snapshot = request_payload.get("snapshot")
            if not system_id:
                self._send_json(400, {"error": "missing system_id"})
                return
            if not isinstance(snapshot, dict):
                self._send_json(400, {"error": "snapshot must be a dict"})
                return
            result = system_snapshot_post_payload(system_id, snapshot)
            if result.get("error"):
                self._send_json(404, result)
                return
            self._send_json(200, result)
            return
        if parsed.path == WORKBENCH_BUNDLE_PATH:
            response_payload, error_payload = build_workbench_bundle_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == WORKBENCH_REPAIR_PATH:
            response_payload, error_payload = build_workbench_safe_repair_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == WORKBENCH_ARCHIVE_RESTORE_PATH:
            response_payload, error_payload = build_workbench_archive_restore_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        # P19.6: Reverse diagnosis run (uses already-parsed request_payload)
        if parsed.path == DIAGNOSIS_RUN_PATH:
            from well_harness.reverse_diagnosis import VALID_OUTCOMES, ReverseDiagnosisEngine
            outcome = str(request_payload.get("outcome", "")).strip()
            if outcome not in VALID_OUTCOMES:
                self._send_json(400, {
                    "error": f"Invalid outcome: {outcome!r}. "
                             f"Valid: {sorted(VALID_OUTCOMES)}"
                })
                return
            max_results = min(int(request_payload.get("max_results", 1000)), 1000)
            max_results = max(max_results, 0)
            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
            if system_id not in _SUPPORTED_FOR_ANALYSIS:
                self._send_json(400, {
                    "error": f"system_id {system_id!r} is not supported for diagnosis. "
                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
                })
                return
            yaml_path = self._hardware_yaml_path(system_id)
            try:
                engine = ReverseDiagnosisEngine(yaml_path)
                report = engine.diagnose_and_report(outcome, max_results=max_results)
                self._send_json(200, report)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
            return

        # P19.7: Monte Carlo reliability simulation
        if parsed.path == MONTE_CARLO_RUN_PATH:
            from well_harness.monte_carlo_engine import MonteCarloEngine, _reliability_result_to_dict
            n_trials_raw = request_payload.get("n_trials", 100)
            try:
                n_trials = int(n_trials_raw)
            except (TypeError, ValueError):
                self._send_json(400, {"error": "n_trials must be an integer"})
                return
            n_trials = max(1, min(n_trials, 10000))

            seed = None
            if "seed" in request_payload:
                try:
                    seed = int(request_payload["seed"])
                except (TypeError, ValueError):
                    self._send_json(400, {"error": "seed must be an integer"})
                    return

            system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
            if system_id not in _SUPPORTED_FOR_ANALYSIS:
                self._send_json(400, {
                    "error": f"system_id {system_id!r} is not supported for Monte Carlo. "
                             f"Currently supported: {sorted(_SUPPORTED_FOR_ANALYSIS)}"
                })
                return
            yaml_path = self._hardware_yaml_path(system_id)
            try:
                engine = MonteCarloEngine(yaml_path)
                result = engine.run(n_trials, seed=seed)
                self._send_json(200, _reliability_result_to_dict(result))
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
            return

        if parsed.path == SENSITIVITY_SWEEP_PATH:
            response_payload, error_payload = build_sensitivity_sweep_payload(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        prompt = str(request_payload.get("prompt", "")).strip()
        if not prompt:
            self._send_json(400, {"error": "missing_prompt"})
            return

        answer = answer_demo_prompt(prompt)
        self._send_json(200, demo_answer_to_payload(answer))

    # ── P19.6: Reverse diagnosis endpoint ─────────────────────────────────────

    def _hardware_yaml_path(self, system_id: str = "thrust-reverser") -> str:
        """Return the path to the hardware YAML config for the given system_id."""
        import pathlib as _pathlib
        import well_harness as _wh
        pkg_root = _pathlib.Path(_wh.__file__).parent
        repo_root = pkg_root.parent.parent
        filename = _SYSTEM_YAML_MAP.get(system_id)
        if filename is None:
            raise FileNotFoundError(
                f"Unknown system_id: {system_id!r}. Valid: {sorted(_SYSTEM_YAML_MAP)}"
            )
        return str(repo_root / "config" / "hardware" / filename)

    # ── P19.8: Hardware schema endpoint ───────────────────────────────────────

    def _handle_hardware_schema(self, system_id: str = "thrust-reverser") -> None:
        """Return the full hardware YAML as a JSON dict (P19.8)."""
        try:
            yaml_path = self._hardware_yaml_path(system_id)
            if system_id == "thrust-reverser":
                from well_harness.hardware_schema import (
                    _hardware_to_dict,
                    load_thrust_reverser_hardware,
                )

                hw = load_thrust_reverser_hardware(yaml_path)
                result = _hardware_to_dict(hw)
                result["system_id"] = system_id
            else:
                # Generic YAML loader for non-thrust-reverser systems
                import yaml

                with open(yaml_path, encoding="utf-8") as f:
                    result = yaml.safe_load(f)
                if not isinstance(result, dict):
                    raise ValueError(f"YAML root must be a dict, got {type(result).__name__}")
                result["system_id"] = system_id

            self._send_json(200, result)
        except FileNotFoundError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})

    def _serve_static(self, relative_path: str):
        static_root = STATIC_DIR.resolve()
        target_path = (static_root / relative_path).resolve()
        # Path must live inside static_root (traversal guard) and exist as a file.
        # Phase UI-F (2026-04-22): allow nested static paths like
        # /c919_etras_panel/circuit.html so the unified-nav can link to them.
        try:
            target_path.relative_to(static_root)
        except ValueError:
            self._send_json(404, {"error": "not_found"})
            return
        if not target_path.is_file():
            self._send_json(404, {"error": "not_found"})
            return

        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
        self._send_bytes(200, target_path.read_bytes(), content_type)

    def _send_json(self, status_code: int, payload: dict):
        # Compact JSON: no indentation (machine-to-machine API, not human-readable)
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status_code, response, "application/json; charset=utf-8")

    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def _clamp_tra(tra_deg: float, config: HarnessConfig) -> float:
    return max(config.reverse_travel_min_deg, min(config.reverse_travel_max_deg, tra_deg))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _parse_float_input(request_payload: dict, field_name: str, options: dict) -> tuple[float | None, dict | None]:
    raw_value = request_payload.get(field_name, options["default"])
    if isinstance(raw_value, bool):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    return _clamp(value, options["min"], options["max"]), None


def _parse_bool_input(request_payload: dict, field_name: str, default: bool) -> tuple[bool | None, dict | None]:
    raw_value = request_payload.get(field_name, default)
    if isinstance(raw_value, bool):
        return raw_value, None
    if isinstance(raw_value, str):
        normalized = raw_value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True, None
        if normalized in {"false", "0", "no", "off"}:
            return False, None
    return None, {
        "error": "invalid_lever_snapshot_input",
        "field": field_name,
        "message": f"{field_name} must be boolean.",
    }


def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
    if not isinstance(raw_value, str):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be a string.",
        }
    normalized = raw_value.strip()
    if normalized not in LEVER_FEEDBACK_MODES:
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
        }
    return normalized, None


# E11-14 (2026-04-25): server-side role guard for manual_feedback_override.
# When feedback_mode = manual_feedback_override, the request must include
# actor + ticket_id + manual_override_signoff. If any are missing/malformed,
# the endpoint returns 409 Conflict (paired with E11-13 UI affordance, this
# forms the "UI 看不到 + 服务端拒绝" two-line defense). Truth-engine red line
# stays put: no controller / runner / models / adapters/*.py changes.
def _validate_manual_override_signoff(request_payload: dict, feedback_mode: str) -> dict | None:
    """Return error_payload (with `_status` 409) if signoff is missing/invalid; else None.

    Only enforced when feedback_mode == "manual_feedback_override". For
    auto_scrubber, this returns None unconditionally (no extra fields needed).
    """
    if feedback_mode != "manual_feedback_override":
        return None

    actor = request_payload.get("actor")
    ticket_id = request_payload.get("ticket_id")
    signoff = request_payload.get("manual_override_signoff")

    def reject(field: str, message: str) -> dict:
        return {
            "_status": 409,
            "error": "manual_override_unsigned",
            "field": field,
            "message": message,
            "remediation": (
                "manual_feedback_override requires actor + ticket_id + manual_override_signoff. "
                "Acquire sign-off via Approval Center, or switch to auto_scrubber."
            ),
            # E11-14 R2 (P2 IMPORTANT #4, 2026-04-25): residual risk disclosure.
            # The current sign-off check is structural only — same triplet can
            # authorize multiple override payloads (replay) and signed_at is
            # not freshness-checked. One-shot latch / nonce / freshness is the
            # E11-16 approval-endpoint hardening scope. Until E11-16 lands,
            # this guard is "shape correct" not "latched authorization".
            "residual_risk": (
                "Sign-off is structural only. Replay across payloads is not blocked; "
                "signed_at is not freshness-validated. One-shot latch + nonce + "
                "server-issued approvals scoped to E11-16 (approval endpoint hardening)."
            ),
        }

    if not isinstance(actor, str) or not actor.strip():
        return reject("actor", "manual_feedback_override requires a non-empty actor string.")
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        return reject("ticket_id", "manual_feedback_override requires a non-empty ticket_id string.")

    if not isinstance(signoff, dict):
        return reject(
            "manual_override_signoff",
            "manual_feedback_override requires a manual_override_signoff object.",
        )
    signed_by = signoff.get("signed_by")
    signed_at = signoff.get("signed_at")
    signoff_ticket = signoff.get("ticket_id")
    if not isinstance(signed_by, str) or not signed_by.strip():
        return reject(
            "manual_override_signoff.signed_by",
            "manual_override_signoff.signed_by must be a non-empty string.",
        )
    if not isinstance(signed_at, str) or not signed_at.strip():
        return reject(
            "manual_override_signoff.signed_at",
            "manual_override_signoff.signed_at must be a non-empty timestamp string.",
        )
    if not isinstance(signoff_ticket, str) or not signoff_ticket.strip():
        return reject(
            "manual_override_signoff.ticket_id",
            "manual_override_signoff.ticket_id must be a non-empty string.",
        )
    if signoff_ticket.strip() != ticket_id.strip():
        return reject(
            "manual_override_signoff.ticket_id",
            "manual_override_signoff.ticket_id must match the request's ticket_id.",
        )

    # E11-14 R2 fix (P2 BLOCKER #1, 2026-04-25): actor must equal
    # manual_override_signoff.signed_by. Without this binding, an attacker
    # can submit `actor="Mallory"` with `signed_by="Kogami"` and the server
    # would accept it (P2 verified via live probe). Bind requester identity
    # to the signoff's signer.
    if signed_by.strip() != actor.strip():
        return reject(
            "actor",
            "actor must match manual_override_signoff.signed_by (impersonation guard).",
        )

    return None


def _normalize_fault_injection_node_id(node_id: str) -> str:
    normalized = str(node_id or "").strip()
    return LEVER_SNAPSHOT_FAULT_NODE_ALIASES.get(normalized, normalized)


def _fault_injection_map(fault_injections: list[dict] | None) -> dict[str, str]:
    fault_map: dict[str, str] = {}
    for fault in fault_injections or []:
        node_id = _normalize_fault_injection_node_id(fault.get("node_id", ""))
        fault_type = str(fault.get("fault_type", "")).strip()
        if node_id and fault_type:
            fault_map[node_id] = fault_type
    return fault_map


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _apply_switch_fault_injections(
    switch_state: SwitchState,
    fault_map: dict[str, str],
) -> SwitchState:
    sw1 = switch_state.sw1
    if fault_map.get("sw1") == "stuck_off":
        sw1 = False
    elif fault_map.get("sw1") == "stuck_on":
        sw1 = True

    sw2 = switch_state.sw2
    if fault_map.get("sw2") == "stuck_off":
        sw2 = False
    elif fault_map.get("sw2") == "stuck_on":
        sw2 = True

    if sw1 == switch_state.sw1 and sw2 == switch_state.sw2:
        return switch_state

    return SwitchState(
        previous_tra_deg=switch_state.previous_tra_deg,
        sw1=sw1,
        sw2=sw2,
    )


def _apply_sensor_fault_injections(sensors, fault_map: dict[str, str]):
    sensor_updates = {}

    if fault_map.get("tls115") == "sensor_zero":
        sensor_updates["tls_unlocked_ls"] = False

    if fault_map.get("vdt90") == "cmd_blocked":
        sensor_updates["deploy_90_percent_vdt"] = False

    if not sensor_updates:
        return sensors

    return replace(sensors, **sensor_updates)


def _apply_output_fault_injections(outputs, fault_map: dict[str, str]):
    output_updates = {}

    if fault_map.get("tls115") == "sensor_zero":
        output_updates["tls_115vac_cmd"] = False

    if fault_map.get("logic1") == "logic_stuck_false":
        output_updates["logic1_active"] = False
        output_updates["tls_115vac_cmd"] = False

    if fault_map.get("logic2") == "logic_stuck_false":
        output_updates["logic2_active"] = False
        output_updates["etrac_540vdc_cmd"] = False

    if fault_map.get("logic3") == "logic_stuck_false":
        output_updates["logic3_active"] = False
        output_updates["eec_deploy_cmd"] = False
        output_updates["pls_power_cmd"] = False
        output_updates["pdu_motor_cmd"] = False

    if fault_map.get("logic4") == "logic_stuck_false":
        output_updates["logic4_active"] = False
        output_updates["throttle_electronic_lock_release_cmd"] = False

    if fault_map.get("thr_lock") == "cmd_blocked":
        output_updates["throttle_electronic_lock_release_cmd"] = False

    if not output_updates:
        return outputs

    return replace(outputs, **output_updates)


def _fault_reason(fault_type: str) -> str:
    return f"{FAULT_INJECTION_REASON}:{fault_type}"


def _set_faulted_node_state(
    node_payload: dict | None,
    *,
    state: str,
    reason: str | None = None,
) -> None:
    if node_payload is None:
        return
    node_payload["state"] = state
    if state == "blocked":
        blocked_by = list(node_payload.get("blocked_by") or [])
        if reason:
            _append_unique(blocked_by, reason)
        node_payload["blocked_by"] = blocked_by
        return
    node_payload["blocked_by"] = []


def _apply_fault_injections_to_snapshot_payload(
    result: dict,
    fault_injections: list[dict] | None,
) -> dict:
    fault_map = _fault_injection_map(fault_injections)
    if not fault_map:
        return result

    nodes_by_id = {
        node["id"]: node
        for node in result.get("nodes", [])
        if isinstance(node, dict) and "id" in node
    }
    input_payload = result.get("input")
    hud_payload = result.get("hud")
    outputs_payload = result.get("outputs")
    logic_payload = result.get("logic")

    for node_id, fault_type in fault_map.items():
        reason = _fault_reason(fault_type)

        if node_id == "sw1":
            active = fault_type == "stuck_on"
            if isinstance(hud_payload, dict):
                hud_payload["sw1"] = active
            _set_faulted_node_state(
                nodes_by_id.get("sw1"),
                state="active" if active else "inactive",
            )
            continue

        if node_id == "sw2":
            active = fault_type == "stuck_on"
            if isinstance(hud_payload, dict):
                hud_payload["sw2"] = active
            _set_faulted_node_state(
                nodes_by_id.get("sw2"),
                state="active" if active else "inactive",
            )
            continue

        if node_id == "radio_altitude_ft" and fault_type == "sensor_zero":
            if isinstance(input_payload, dict):
                input_payload["radio_altitude_ft"] = 0.0
            if isinstance(hud_payload, dict):
                hud_payload["radio_altitude_ft"] = 0.0
            _set_faulted_node_state(nodes_by_id.get("radio_altitude_ft"), state="inactive")
            continue

        if node_id == "n1k" and fault_type == "sensor_zero":
            if isinstance(input_payload, dict):
                input_payload["n1k"] = 0.0
            if isinstance(hud_payload, dict):
                hud_payload["n1k"] = 0.0
            _set_faulted_node_state(nodes_by_id.get("n1k"), state="inactive")
            continue

        if node_id == "tls115" and fault_type == "sensor_zero":
            if isinstance(outputs_payload, dict):
                outputs_payload["tls_115vac_cmd"] = False
            _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
            continue

        if node_id in {"logic1", "logic2", "logic3", "logic4"} and fault_type == "logic_stuck_false":
            logic_entry = logic_payload.get(node_id) if isinstance(logic_payload, dict) else None
            if isinstance(logic_entry, dict):
                logic_entry["active"] = False
                failed_conditions = list(logic_entry.get("failed_conditions") or [])
                _append_unique(failed_conditions, reason)
                logic_entry["failed_conditions"] = failed_conditions

            if isinstance(outputs_payload, dict):
                outputs_payload[f"{node_id}_active"] = False

            _set_faulted_node_state(nodes_by_id.get(node_id), state="blocked", reason=reason)

            if node_id == "logic1":
                if isinstance(outputs_payload, dict):
                    outputs_payload["tls_115vac_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
            elif node_id == "logic2":
                if isinstance(outputs_payload, dict):
                    outputs_payload["etrac_540vdc_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("etrac_540v"), state="inactive")
            elif node_id == "logic3":
                if isinstance(outputs_payload, dict):
                    outputs_payload["eec_deploy_cmd"] = False
                    outputs_payload["pls_power_cmd"] = False
                    outputs_payload["pdu_motor_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("eec_deploy"), state="inactive")
                _set_faulted_node_state(nodes_by_id.get("pls_power"), state="inactive")
                _set_faulted_node_state(nodes_by_id.get("pdu_motor"), state="inactive")
            elif node_id == "logic4":
                if isinstance(outputs_payload, dict):
                    outputs_payload["throttle_electronic_lock_release_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
            continue

        if node_id == "thr_lock" and fault_type == "cmd_blocked":
            if isinstance(outputs_payload, dict):
                outputs_payload["throttle_electronic_lock_release_cmd"] = False
            _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
            continue

        if node_id == "vdt90" and fault_type == "cmd_blocked":
            if isinstance(hud_payload, dict):
                hud_payload["deploy_90_percent_vdt"] = False
            _set_faulted_node_state(nodes_by_id.get("vdt90"), state="blocked", reason=reason)

    result["active_fault_node_ids"] = list(fault_map.keys())
    result["fault_injections"] = fault_injections or []
    return result


_TIMELINE_MAX_DURATION_S = 600.0
_TIMELINE_MIN_STEP_S = 0.01
# Belt-and-braces cap so a user cannot request 600s / 0.01s = 60,000 ticks
# just because each individual bound is within range (Codex PR-2 MINOR #1).
_TIMELINE_MAX_TICKS = 20_000
_TIMELINE_MAX_EVENTS = 500


def _handle_fantui_tick(request_payload: dict) -> tuple[int, dict]:
    """Advance the FANTUI stateful tick system one step and return a snapshot.

    Paired with ``/api/fantui/reset`` and ``/api/fantui/log``. The response
    mirrors what /api/log emits so the same ``timeseries_chart.js`` module can
    render either panel's buffer.
    """
    try:
        pilot = parse_pilot_inputs(request_payload)
    except ValueError as exc:
        return 400, {"error": "invalid_input", "message": str(exc)}
    try:
        dt_s = float(request_payload.get("dt_s", 0.1))
    except (TypeError, ValueError):
        return 400, {"error": "invalid_dt_s"}
    # Guard: tick step must be positive, finite, and small enough to avoid
    # jumping over switch windows. 1.0s is a conservative ceiling.
    # ``math.isfinite`` rejects NaN / ±Inf before they can poison ``_t_s``
    # (Codex review, 2026-04-24, CRITICAL).
    if not math.isfinite(dt_s) or dt_s <= 0 or dt_s > 1.0:
        return 400, {"error": "dt_s_out_of_range", "message": "0 < dt_s <= 1.0"}

    rec, count = _FANTUI_SYSTEM.tick_with_count(pilot, dt_s)
    snapshot = rec.as_dict()
    snapshot["sample_count"] = count
    return 200, snapshot


def _handle_timeline_simulate(request_payload: dict) -> dict:
    """Run a Timeline against the FANTUI executor and return the trace as JSON.

    Returns `_status` key for the HTTP code to use (200 / 400).
    """
    try:
        timeline = parse_timeline(request_payload)
    except TimelineValidationError as exc:
        return {"_status": 400, "error": "invalid_timeline", "field": exc.field, "message": exc.message}

    if timeline.system != "fantui":
        return {
            "_status": 400,
            "error": "unsupported_system",
            "message": f"this endpoint only runs FANTUI timelines; got system={timeline.system!r}",
        }
    if timeline.duration_s > _TIMELINE_MAX_DURATION_S:
        return {
            "_status": 400,
            "error": "timeline_too_long",
            "message": f"duration_s must be <= {_TIMELINE_MAX_DURATION_S}s",
        }
    if timeline.step_s < _TIMELINE_MIN_STEP_S:
        return {
            "_status": 400,
            "error": "timeline_step_too_small",
            "message": f"step_s must be >= {_TIMELINE_MIN_STEP_S}s",
        }
    tick_count = int(timeline.duration_s / timeline.step_s) + 1
    if tick_count > _TIMELINE_MAX_TICKS:
        return {
            "_status": 400,
            "error": "timeline_too_many_ticks",
            "message": f"duration_s/step_s would produce {tick_count} ticks; max {_TIMELINE_MAX_TICKS}",
        }
    if len(timeline.events) > _TIMELINE_MAX_EVENTS:
        return {
            "_status": 400,
            "error": "timeline_too_many_events",
            "message": f"events list has {len(timeline.events)} entries; max {_TIMELINE_MAX_EVENTS}",
        }

    try:
        executor = FantuiExecutor()
        trace = TimelinePlayer(timeline, executor).run()
    except (ValueError, TypeError) as exc:
        # Runtime errors (unknown fault id, bad set_input value, …) get
        # surfaced as a 400 rather than a 500 so the UI can show the
        # validation message inline (Codex PR-2 MAJOR #3).
        return {
            "_status": 400,
            "error": "invalid_timeline",
            "message": str(exc),
        }
    return _timeline_trace_to_json(trace)


def _timeline_trace_to_json(trace) -> dict:
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
            "deployed_successfully": trace.outcome.deployed_successfully,
            "thr_lock_released": trace.outcome.thr_lock_released,
            "logic_first_active_t_s": trace.outcome.logic_first_active_t_s,
            "logic_first_blocked_t_s": trace.outcome.logic_first_blocked_t_s,
            "failure_cascade": trace.outcome.failure_cascade,
        },
    }


def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
    lever_inputs = {}
    for field_name, options in LEVER_NUMERIC_INPUTS.items():
        value, error_payload = _parse_float_input(request_payload, field_name, options)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    config = HarnessConfig()
    lever_inputs["tra_deg"] = _clamp_tra(lever_inputs["tra_deg"], config)

    for field_name, default in LEVER_BOOLEAN_INPUTS.items():
        value, error_payload = _parse_bool_input(request_payload, field_name, default)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
    if error_payload is not None:
        return None, error_payload
    lever_inputs["feedback_mode"] = feedback_mode

    # E11-14 R1 had the guard here; moved to the END of structural parsing
    # in R2 (P2 IMPORTANT #3, 2026-04-25): a malformed
    # deploy_position_percent="oops" + missing signoff used to return 409
    # manual_override_unsigned, masking the real 400. Authority guard now
    # runs on otherwise-well-formed manual-override requests only.

    deploy_position_percent, error_payload = _parse_float_input(
        request_payload,
        "deploy_position_percent",
        {"default": 0.0, "min": 0.0, "max": 100.0},
    )
    if error_payload is not None:
        return None, error_payload
    lever_inputs["deploy_position_percent"] = deploy_position_percent

    fault_injections = request_payload.get("fault_injections")
    if fault_injections is not None:
        if not isinstance(fault_injections, list):
            return None, {
                "error": "invalid_fault_injections",
                "message": "fault_injections must be a list",
            }
        normalized_faults = []
        for fault in fault_injections:
            if not isinstance(fault, dict):
                return None, {
                    "error": "invalid_fault_injections",
                    "message": "each fault_injection must be an object",
                }
            node_id = str(fault.get("node_id", "")).strip()
            fault_type = str(fault.get("fault_type", "")).strip()
            if node_id not in LEVER_SNAPSHOT_FAULT_NODES:
                return None, {
                    "error": "invalid_fault_injection_node",
                    "message": f"Unknown node_id: {node_id}",
                }
            if fault_type not in LEVER_SNAPSHOT_FAULT_TYPES:
                return None, {
                    "error": "invalid_fault_type",
                    "message": f"Unknown fault_type: {fault_type}",
                }
            normalized_faults.append(
                {
                    "node_id": _normalize_fault_injection_node_id(node_id),
                    "fault_type": fault_type,
                }
            )
        if normalized_faults:
            lever_inputs["_fault_injections"] = normalized_faults

    # E11-14 R2 (P2 IMPORTANT #3): authority guard runs AFTER structural
    # parsing so 400 (malformed) precedes 409 (unsigned). No-op for
    # auto_scrubber; returns 409 payload with `_status` hint when signoff
    # missing/invalid for manual_feedback_override.
    signoff_error = _validate_manual_override_signoff(request_payload, feedback_mode)
    if signoff_error is not None:
        return None, signoff_error

    return lever_inputs, None


def default_workbench_archive_root() -> Path:
    return (Path.cwd() / "artifacts" / "workbench-bundles").resolve()


def reference_workbench_packet_payload() -> dict:
    return json.loads(REFERENCE_PACKET_PATH.read_text(encoding="utf-8"))


def build_explain_runtime_payload() -> dict[str, Any]:
    # LLM features shelved in Phase A (2026-04-22). Return a stable idle payload
    # so workbench clients can still render the runtime panel without runtime error.
    return {
        "status": "shelved",
        "status_source": "runtime_config",
        "llm_backend": "",
        "llm_model": "",
        "response_source": "unknown",
        "cached_at": "",
        "observed_at_utc": "",
        "verified_cache_hits": 0,
        "expected_count": 0,
        "backend_match": None,
        "requested_backend": "",
        "requested_model": "",
        "detail": "LLM features shelved — see archive/shelved/llm-features/SHELVED.md.",
        "boundary_note": "这是 explain runtime / pitch 运维状态，不是新的控制真值。",
    }


def recent_workbench_archive_summaries(*, limit: int = 6) -> list[dict]:
    archive_root = default_workbench_archive_root()
    if not archive_root.is_dir():
        return []

    summaries: list[dict] = []
    for archive_dir in archive_root.iterdir():
        if not archive_dir.is_dir():
            continue
        manifest_path = archive_dir / "archive_manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = load_workbench_archive_manifest(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue

        bundle = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
        files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
        summaries.append(
            {
                "archive_dir": str(archive_dir.resolve()),
                "manifest_path": str(manifest_path.resolve()),
                "created_at_utc": manifest.get("created_at_utc"),
                "system_id": bundle.get("system_id"),
                "system_title": bundle.get("system_title"),
                "bundle_kind": bundle.get("bundle_kind"),
                "ready_for_spec_build": bundle.get("ready_for_spec_build"),
                "selected_scenario_id": bundle.get("selected_scenario_id"),
                "selected_fault_mode_id": bundle.get("selected_fault_mode_id"),
                "has_workspace_handoff": files.get("workspace_handoff_json") is not None,
                "has_workspace_snapshot": files.get("workspace_snapshot_json") is not None,
            }
        )

    summaries.sort(
        key=lambda item: (
            str(item.get("created_at_utc") or ""),
            str(item.get("archive_dir") or ""),
        ),
        reverse=True,
    )
    return summaries[:limit]


def workbench_bootstrap_payload() -> dict:
    return {
        "template_packet": intake_template_payload(),
        "reference_packet": reference_workbench_packet_payload(),
        "default_archive_root": str(default_workbench_archive_root()),
        "recent_archives": recent_workbench_archive_summaries(),
        "explain_runtime": build_explain_runtime_payload(),
    }


def workbench_recent_archives_payload() -> dict:
    return {
        "default_archive_root": str(default_workbench_archive_root()),
        "recent_archives": recent_workbench_archive_summaries(),
    }


def _optional_request_float_list(
    payload: dict,
    field_name: str,
    *,
    default: tuple[float, ...],
) -> tuple[tuple[float, ...], dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return default, None
    if not isinstance(raw_value, list) or not raw_value:
        return default, {
            "error": "invalid_sensitivity_sweep_request",
            "field": field_name,
            "message": f"{field_name} must be a non-empty list of finite numbers.",
        }

    normalized: list[float] = []
    for item in raw_value:
        if isinstance(item, bool):
            return default, {
                "error": "invalid_sensitivity_sweep_request",
                "field": field_name,
                "message": f"{field_name} must be numeric.",
            }
        try:
            value = float(item)
        except (TypeError, ValueError):
            return default, {
                "error": "invalid_sensitivity_sweep_request",
                "field": field_name,
                "message": f"{field_name} must be numeric.",
            }
        if not math.isfinite(value):
            return default, {
                "error": "invalid_numeric_value",
                "field": field_name,
                "message": f"{field_name} must contain only finite numbers.",
            }
        normalized.append(value)
    return tuple(normalized), None


def _stable_numeric_key(value: float) -> str:
    numeric = float(value)
    if numeric.is_integer():
        return str(int(numeric))
    return format(numeric, "g")


def _sensitivity_outcome_matches(snapshot: dict, outcome: str) -> bool:
    outputs = snapshot.get("outputs") if isinstance(snapshot.get("outputs"), dict) else {}
    hud = snapshot.get("hud") if isinstance(snapshot.get("hud"), dict) else {}
    if outcome == "logic1_active":
        return bool(outputs.get("logic1_active"))
    if outcome == "logic2_active":
        return bool(outputs.get("logic2_active"))
    if outcome == "logic3_active":
        return bool(outputs.get("logic3_active"))
    if outcome == "thr_lock_active":
        return bool(outputs.get("throttle_electronic_lock_release_cmd"))
    if outcome == "deploy_confirmed":
        return bool(hud.get("deploy_90_percent_vdt"))
    if outcome == "tls_unlocked":
        return bool(hud.get("tls_unlocked_ls"))
    if outcome == "pls_unlocked":
        return bool(hud.get("pls_unlocked_ls"))
    raise ValueError(f"Unsupported outcome: {outcome}")


def build_sensitivity_sweep_payload(request_payload: dict) -> tuple[dict | None, dict | None]:
    system_id = str(request_payload.get("system_id", "thrust-reverser")).strip() or "thrust-reverser"
    if system_id != "thrust-reverser":
        return None, {
            "error": "unsupported_system",
            "message": "sensitivity sweep currently supports only 'thrust-reverser'.",
        }

    radio_altitude_ft_values, error_payload = _optional_request_float_list(
        request_payload,
        "radio_altitude_ft_values",
        default=SENSITIVITY_SWEEP_DEFAULT_RA_VALUES,
    )
    if error_payload is not None:
        return None, error_payload

    tra_deg_values, error_payload = _optional_request_float_list(
        request_payload,
        "tra_deg_values",
        default=SENSITIVITY_SWEEP_DEFAULT_TRA_VALUES,
    )
    if error_payload is not None:
        return None, error_payload

    outcomes, error_payload = _optional_request_string_list(request_payload, "outcomes")
    if error_payload is not None:
        error_payload["error"] = "invalid_sensitivity_sweep_request"
        return None, error_payload
    requested_outcomes = outcomes or SENSITIVITY_SWEEP_DEFAULT_OUTCOMES
    invalid_outcomes = [
        outcome
        for outcome in requested_outcomes
        if outcome not in SENSITIVITY_SWEEP_ALLOWED_OUTCOMES
    ]
    if invalid_outcomes:
        return None, {
            "error": "invalid_sensitivity_outcome",
            "message": (
                f"Unsupported outcomes: {invalid_outcomes}. "
                f"Valid: {sorted(SENSITIVITY_SWEEP_ALLOWED_OUTCOMES)}"
            ),
        }

    matrix_counts: dict[str, dict[str, int]] = {}
    grid: dict[str, dict[str, dict[str, bool]]] = {}
    outcome_totals = {outcome: 0 for outcome in requested_outcomes}

    for radio_altitude_ft in radio_altitude_ft_values:
        ra_key = _stable_numeric_key(radio_altitude_ft)
        matrix_counts[ra_key] = {}
        grid[ra_key] = {}
        for tra_deg in tra_deg_values:
            tra_key = _stable_numeric_key(tra_deg)
            snapshot = lever_snapshot_payload(
                tra_deg=tra_deg,
                radio_altitude_ft=radio_altitude_ft,
                feedback_mode="manual_feedback_override",
                deploy_position_percent=100.0,
            )
            matched_outcomes = {
                outcome: _sensitivity_outcome_matches(snapshot, outcome)
                for outcome in requested_outcomes
            }
            matrix_counts[ra_key][tra_key] = sum(
                1 for is_matched in matched_outcomes.values() if is_matched
            )
            grid[ra_key][tra_key] = matched_outcomes
            for outcome, is_matched in matched_outcomes.items():
                if is_matched:
                    outcome_totals[outcome] += 1

    return {
        "system_id": system_id,
        "radio_altitude_ft_values": list(radio_altitude_ft_values),
        "tra_deg_values": list(tra_deg_values),
        "outcomes": list(requested_outcomes),
        "matrix_counts": matrix_counts,
        "outcome_totals": outcome_totals,
        "grid": grid,
        "scan_count": len(radio_altitude_ft_values) * len(tra_deg_values),
        "fixed_inputs": {
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": MONITOR_N1K,
            "max_n1k_deploy_limit": MONITOR_MAX_N1K_DEPLOY_LIMIT,
            "feedback_mode": "manual_feedback_override",
            "deploy_position_percent": 100.0,
        },
    }, None


def _optional_request_str(payload: dict, field_name: str) -> tuple[str | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, str):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a string when provided.",
        }
    normalized = raw_value.strip()
    return (normalized or None), None


def _optional_request_string_list(payload: dict, field_name: str) -> tuple[tuple[str, ...] | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, list) or any(not isinstance(item, str) for item in raw_value):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a list of strings when provided.",
        }
    return tuple(item.strip() for item in raw_value if item.strip()), None


def _optional_request_float(payload: dict, field_name: str, *, default: float) -> tuple[float, dict | None]:
    raw_value = payload.get(field_name, default)
    if isinstance(raw_value, bool):
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    if not math.isfinite(value):
        return default, {
            "error": "invalid_numeric_value",
            "field": field_name,
            "message": f"{field_name} must be a finite number.",
        }
    if value <= 0:
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be greater than zero.",
        }
    return value, None


def _optional_request_object(payload: dict, field_name: str) -> tuple[dict | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a JSON object when provided.",
        }
    return raw_value, None


def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    packet_payload = request_payload.get("packet_payload")
    if not isinstance(packet_payload, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": "packet_payload",
            "message": "packet_payload must be a JSON object.",
        }
    try:
        packet = intake_packet_from_dict(packet_payload)
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_packet",
            "field": "packet_payload",
            "message": str(exc),
        }

    scenario_id, error_payload = _optional_request_str(request_payload, "scenario_id")
    if error_payload is not None:
        return None, error_payload
    fault_mode_id, error_payload = _optional_request_str(request_payload, "fault_mode_id")
    if error_payload is not None:
        return None, error_payload
    observed_symptoms, error_payload = _optional_request_str(request_payload, "observed_symptoms")
    if error_payload is not None:
        return None, error_payload
    evidence_links, error_payload = _optional_request_string_list(request_payload, "evidence_links")
    if error_payload is not None:
        return None, error_payload
    confirmed_root_cause, error_payload = _optional_request_str(request_payload, "confirmed_root_cause")
    if error_payload is not None:
        return None, error_payload
    repair_action, error_payload = _optional_request_str(request_payload, "repair_action")
    if error_payload is not None:
        return None, error_payload
    validation_after_fix, error_payload = _optional_request_str(request_payload, "validation_after_fix")
    if error_payload is not None:
        return None, error_payload
    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
    if error_payload is not None:
        return None, error_payload
    suggested_logic_change, error_payload = _optional_request_str(request_payload, "suggested_logic_change")
    if error_payload is not None:
        return None, error_payload
    reliability_gain_hypothesis, error_payload = _optional_request_str(
        request_payload,
        "reliability_gain_hypothesis",
    )
    if error_payload is not None:
        return None, error_payload
    guardrail_note, error_payload = _optional_request_str(request_payload, "guardrail_note")
    if error_payload is not None:
        return None, error_payload
    sample_period_s, error_payload = _optional_request_float(
        request_payload,
        "sample_period_s",
        default=0.5,
    )
    if error_payload is not None:
        return None, error_payload
    workspace_handoff, error_payload = _optional_request_object(request_payload, "workspace_handoff")
    if error_payload is not None:
        return None, error_payload
    workspace_snapshot, error_payload = _optional_request_object(request_payload, "workspace_snapshot")
    if error_payload is not None:
        return None, error_payload
    if workspace_handoff is None and workspace_snapshot is not None:
        derived_handoff = workspace_snapshot.get("handoff")
        if isinstance(derived_handoff, dict):
            workspace_handoff = derived_handoff

    archive_bundle_raw = request_payload.get("archive_bundle", False)
    archive_bundle = isinstance(archive_bundle_raw, bool) and archive_bundle_raw is True
    try:
        bundle = build_workbench_bundle(
            packet,
            scenario_id=scenario_id,
            fault_mode_id=fault_mode_id,
            observed_symptoms=observed_symptoms,
            evidence_links=evidence_links or (),
            confirmed_root_cause=confirmed_root_cause,
            repair_action=repair_action,
            validation_after_fix=validation_after_fix,
            residual_risk=residual_risk,
            suggested_logic_change=suggested_logic_change,
            reliability_gain_hypothesis=reliability_gain_hypothesis,
            redundancy_reduction_or_guardrail_note=guardrail_note,
            sample_period_s=sample_period_s,
        )
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_selection",
            "message": str(exc),
        }

    archive = None
    if archive_bundle:
        archive = archive_workbench_bundle(
            bundle,
            default_workbench_archive_root(),
            workspace_handoff=workspace_handoff,
            workspace_snapshot=workspace_snapshot,
        )
    return {
        "bundle": bundle.to_dict(),
        "archive": archive.to_dict() if archive is not None else None,
        "archive_bundle": archive_bundle,
        "default_archive_root": str(default_workbench_archive_root()),
        "explain_runtime": build_explain_runtime_payload(),
    }, None


def build_workbench_safe_repair_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    packet_payload = request_payload.get("packet_payload")
    if not isinstance(packet_payload, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": "packet_payload",
            "message": "packet_payload must be a JSON object.",
        }
    if not request_payload.get("apply_all_safe", False):
        return None, {
            "error": "invalid_workbench_request",
            "field": "apply_all_safe",
            "message": "apply_all_safe must be true for safe schema repair requests.",
        }
    try:
        packet = intake_packet_from_dict(packet_payload)
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_packet",
            "field": "packet_payload",
            "message": str(exc),
        }

    repaired_packet, applied_suggestion_ids = apply_safe_schema_repairs(packet)
    if not applied_suggestion_ids:
        return None, {
            "error": "no_safe_schema_repairs",
            "message": "No safe schema repair suggestions are currently available for this packet.",
        }

    return {
        "packet_payload": intake_packet_to_dict(repaired_packet),
        "applied_suggestion_ids": list(applied_suggestion_ids),
        "intake_assessment": assess_intake_packet(repaired_packet),
        "clarification_brief": build_clarification_brief(repaired_packet),
    }, None


def build_workbench_archive_restore_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    manifest_path, error_payload = _optional_request_str(request_payload, "manifest_path")
    if error_payload is not None:
        return None, error_payload
    if manifest_path is None:
        return None, {
            "error": "invalid_workbench_request",
            "field": "manifest_path",
            "message": "manifest_path must be a non-empty string.",
        }

    # SECURITY: reject path traversal attempts in relative paths
    if not Path(manifest_path).is_absolute():
        if ".." in str(manifest_path):
            return None, {"error": "invalid_manifest_path", "message": "Relative manifest_path with traversal is not allowed."}

    try:
        restore_payload = load_workbench_archive_restore_payload(manifest_path)
    except FileNotFoundError as exc:
        return None, {
            "error": "workbench_archive_not_found",
            "field": "manifest_path",
            "message": str(exc),
        }
    except SandboxEscapeError as exc:
        return None, {"error": "sandbox_violation", "message": str(exc)}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return None, {
            "error": "invalid_workbench_archive",
            "field": "manifest_path",
            "message": str(exc),
        }

    restore_payload["default_archive_root"] = str(default_workbench_archive_root())
    return restore_payload, None


def _canonical_pullback_sequence(tra_deg: float, config: HarnessConfig) -> list[float]:
    """Return a tiny canonical pullback path for the interactive UI scrubber.

    When the pilot holds TRA in the deploy-cmd range (≤ logic3_tra_deg_threshold),
    hold the lever long enough for plant VDT to reach 90% under the default
    deploy rate. Without this, auto_scrubber shows L4 permanently blocked on
    `deploy_90_percent_vdt` because the scrubber window is too short for the
    plant to complete the deployment cycle.
    """
    target = _clamp_tra(tra_deg, config)
    if target >= 0.0:
        return [0.0]

    sequence: list[float] = []
    if target <= config.sw1_window.near_zero_deg:
        sequence.extend([-2.0] * 4)
    if target <= config.sw2_window.near_zero_deg:
        sequence.extend([-7.0] * 4)

    if target <= config.logic3_tra_deg_threshold:
        # Budget enough ticks for plant VDT to reach 90% (and a small margin
        # so L4 latches cleanly). deploy_rate_percent_per_s × step_s × N ≥ 100
        # → N ≥ 100 / (rate × step_s). +4 cushion covers L3-activation lag.
        deploy_ticks_needed = int(100.0 / max(1e-6, config.deploy_rate_percent_per_s * config.step_s)) + 4
        final_repeats = max(4, deploy_ticks_needed)
    else:
        final_repeats = 2
    sequence.extend([target] * final_repeats)
    return sequence


def _condition_payload(condition) -> dict:
    return {
        "name": condition.name,
        "current_value": condition.current_value,
        "comparison": condition.comparison,
        "threshold_value": condition.threshold_value,
        "passed": condition.passed,
    }


def _logic_payload(logic) -> dict:
    return {
        "logic_name": logic.logic_name,
        "active": logic.active,
        "failed_conditions": [condition.name for condition in logic.failed_conditions],
        "conditions": [_condition_payload(condition) for condition in logic.conditions],
    }


def _node(node_id: str, label: str, state: str, source: str, blocked_by: list[str] | None = None) -> dict:
    return {
        "id": node_id,
        "label": label,
        "state": state,
        "source": source,
        "blocked_by": blocked_by or [],
    }


def _logic_node_state(active: bool, completed: bool = False) -> str:
    return "active" if active or completed else "blocked"


def _lever_summary(
    tra_deg: float,
    inputs: ResolvedInputs,
    sensors,
    outputs,
    explain,
    feedback_mode: str,
    tra_lock: dict | None = None,
) -> dict:
    summary = None
    if not inputs.sw1:
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：拉杆还没进入 SW1 窗口，反推链路保持待命。",
            "blocker": "当前卡在 SW1：继续拉入 -1.4° 到 -6.2° 窗口会触发第一段链路。",
            "next_step": "下一步：把拉杆继续向反推方向拉到 SW1 window。",
        }
    elif not outputs.logic1_active and not sensors.tls_unlocked_ls:
        failed = ", ".join(condition.name for condition in explain.logic1.failed_conditions)
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1 已触发，但 L1 / TLS115 尚未放行。",
            "blocker": f"当前卡在 L1：{failed or 'logic1 条件未完全满足'}。",
            "next_step": "下一步：恢复 RA / inhibited / EEC feedback 等 L1 条件，或回到默认演示条件。",
        }
    elif not inputs.sw2:
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1 / L1 / TLS115 已点亮，正在建立 TLS 解锁反馈。",
            "blocker": "当前卡在 SW2：还没有进入 -5.0° 到 -9.8° 窗口。",
            "next_step": "下一步：继续拉到 SW2 window，点亮 L2 / 540V。",
        }
    elif not outputs.logic2_active:
        failed = ", ".join(condition.name for condition in explain.logic2.failed_conditions)
        blocker_text = f"当前卡在 L2：{failed or 'logic2 条件未完全满足'}。"
        l3_shared = {c.name for c in explain.logic2.failed_conditions} & {"engine_running", "aircraft_on_ground"}
        if l3_shared:
            blocker_text += "（L3 对这些信号独立检查，同步被阻塞。）"
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW2 已触发，但 L2 / 540V 尚未放行。",
            "blocker": blocker_text,
            "next_step": "下一步：恢复 engine / ground / inhibited / EEC enable 等 L2 条件。",
        }
    elif not outputs.logic3_active:
        failed = ", ".join(condition.name for condition in explain.logic3.failed_conditions)
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1、SW2 与 L2/540V 已点亮，L3 尚未放行。",
            "blocker": f"当前卡在 L3：{failed or 'logic3 条件未完全满足'}。",
            "next_step": "下一步：继续拉到 TRA <= -11.74°，并保持 N1K / TLS 等条件满足。",
        }
    elif not outputs.logic4_active:
        failed = ", ".join(condition.name for condition in explain.logic4.failed_conditions)
        next_step = "下一步：在受控轨迹中继续保持反推，等 deploy_90_percent_vdt / VDT90 反馈出现。"
        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
            next_step = "下一步：把 deploy feedback override 推到 >= 90%，演示 VDT90 -> L4 -> THR_LOCK。"
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：L3 已点亮，EEC / PLS / PDU 命令正在驱动受控演示轨迹。",
            "blocker": f"THR_LOCK 仍未释放：L4 还在等待 {failed or 'VDT90 / plant feedback'}。",
            "next_step": next_step,
        }
    elif feedback_mode == "manual_feedback_override":
        l1_post_deploy_note = (
            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落，L1 属于首次解锁门，已完成使命。）"
            if (not outputs.logic1_active
                and {c.name for c in explain.logic1.failed_conditions} <= {"reverser_not_deployed_eec"}
                and sensors.deploy_position_percent > 0)
            else ""
        )
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：manual feedback override 已把 VDT90 推到触发态，L4 / THR_LOCK 已点亮。",
            "blocker": "当前无 L4 blocker；这是 simplified plant feedback override 的诊断演示结果。" + l1_post_deploy_note,
            "next_step": "下一步：切回 auto scrubber，或降低 deploy feedback 观察 VDT90 / THR_LOCK 退回 blocked。",
        }
    else:
        l1_post_deploy_note = (
            "（L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落。）"
            if (not outputs.logic1_active
                and {c.name for c in explain.logic1.failed_conditions} <= {"reverser_not_deployed_eec"}
                and sensors.deploy_position_percent > 0)
            else ""
        )
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：L4 已满足，THR_LOCK release command 已触发。",
            "blocker": "当前无 L4 blocker。" + l1_post_deploy_note,
            "next_step": "下一步：查看证据或返回问答抽屉做诊断解释。",
        }

    if tra_lock and tra_lock["clamped"]:
        summary["blocker"] = (
            f"{summary['blocker']} TRA 深拉区仍未开放：请求 {tra_lock['requested_tra_deg']:.1f}° "
            f"已被限制在 {tra_lock['lock_deg']:.1f}°，当前只开放 {tra_lock['lock_deg']:.1f}° 到 0.0° 的自由拖动范围。"
        )
    return summary


def _simulate_lever_state(
    target_tra: float,
    *,
    config: HarnessConfig,
    radio_altitude_ft: float,
    engine_running: bool,
    aircraft_on_ground: bool,
    reverser_inhibited: bool,
    eec_enable: bool,
    n1k: float,
    max_n1k_deploy_limit: float,
    feedback_mode: str,
    deploy_position_percent: float,
    fault_injections: list[dict] | None = None,
) -> dict:
    controller_adapter = build_reference_controller_adapter(config)
    switches = LatchedThrottleSwitches(config)
    plant = SimplifiedDeployPlant(config)
    switch_state = SwitchState(previous_tra_deg=0.0)
    plant_state = PlantState()
    fault_map = _fault_injection_map(fault_injections)

    snapshot = None
    for tick, current_tra in enumerate(_canonical_pullback_sequence(target_tra, config)):
        switch_state = switches.update(switch_state, current_tra)
        switch_state = _apply_switch_fault_injections(switch_state, fault_map)
        sensors = plant_state.sensors(config)
        sensors = _apply_sensor_fault_injections(sensors, fault_map)
        pilot_inputs = PilotInputs(
            radio_altitude_ft=(
                0.0
                if fault_map.get("radio_altitude_ft") == "sensor_zero"
                else radio_altitude_ft
            ),
            tra_deg=current_tra,
            engine_running=engine_running,
            aircraft_on_ground=aircraft_on_ground,
            reverser_inhibited=reverser_inhibited,
            eec_enable=eec_enable,
            n1k=0.0 if fault_map.get("n1k") == "sensor_zero" else n1k,
            max_n1k_deploy_limit=max_n1k_deploy_limit,
        )
        resolved_inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        outputs, explain = controller_adapter.evaluate_with_explain(resolved_inputs)
        outputs = _apply_output_fault_injections(outputs, fault_map)
        snapshot = {
            "time_s": round(tick * config.step_s, 3),
            "plant_state": plant_state,
            "sensors": sensors,
            "pilot_inputs": pilot_inputs,
            "inputs": resolved_inputs,
            "outputs": outputs,
            "explain": explain,
        }
        plant_state = plant.advance(plant_state, outputs, config.step_s)

    assert snapshot is not None

    if feedback_mode == "manual_feedback_override":
        # In manual override mode the user directly drives the physical lever position.
        # deploy_position_percent is the target position set by the user — no longer
        # gated by pdu_motor_cmd, allowing VDT to be forced independently.
        deploy_position = deploy_position_percent
        manual_plant_state = PlantState(
            tls_powered_s=snapshot["plant_state"].tls_powered_s,
            pls_powered_s=snapshot["plant_state"].pls_powered_s,
            tls_unlocked_ls=snapshot["plant_state"].tls_unlocked_ls,
            pls_unlocked_ls=snapshot["plant_state"].pls_unlocked_ls,
            deploy_position_percent=deploy_position,
        )
        sensors = manual_plant_state.sensors(config)
        sensors = _apply_sensor_fault_injections(sensors, fault_map)
        pilot_inputs = snapshot["pilot_inputs"]
        inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=snapshot["inputs"].sw1,
            sw2=snapshot["inputs"].sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        controller_adapter = build_reference_controller_adapter(config)
        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
        outputs = _apply_output_fault_injections(outputs, fault_map)
        snapshot.update(
            {
                "plant_state": manual_plant_state,
                "sensors": sensors,
                "inputs": inputs,
                "outputs": outputs,
                "explain": explain,
            }
        )
    return snapshot


def _build_tra_lock_payload(
    *,
    config: HarnessConfig,
    requested_tra_deg: float,
    effective_tra_deg: float,
    lock_deg: float,
    boundary_unlock_ready: bool,
    deep_range_open: bool,
    unlock_blockers: list[str],
) -> dict:
    blocker_text = " / ".join(unlock_blockers) if unlock_blockers else "L4 条件"
    locked = not deep_range_open
    clamped = effective_tra_deg != requested_tra_deg
    allowed_reverse_min_deg = config.reverse_travel_min_deg if deep_range_open else lock_deg
    if deep_range_open:
        message = (
            f"L4 已满足：TRA 现在可以在 {config.reverse_travel_min_deg:.1f}° 到 0.0° 区间自由拖动。"
        )
    elif clamped:
        message = (
            f"L4 未满足：请求 {requested_tra_deg:.1f}° 已锁回 {lock_deg:.1f}°；"
            f"当前只能在 {lock_deg:.1f}° 到 0.0° 范围内拖动。"
        )
    else:
        message = (
            f"L4 未满足：当前自由拖动范围只开放 {lock_deg:.1f}° 到 0.0°；"
            f"满足 {blocker_text} 后，{config.reverse_travel_min_deg:.1f}° 到 {lock_deg:.1f}° 深拉区间才开放。"
        )
    return {
        "locked": locked,
        "clamped": clamped,
        "unlock_ready": deep_range_open,
        "boundary_unlock_ready": boundary_unlock_ready,
        "lock_deg": lock_deg,
        "requested_tra_deg": requested_tra_deg,
        "effective_tra_deg": effective_tra_deg,
        "allowed_reverse_min_deg": allowed_reverse_min_deg,
        "visual_reverse_min_deg": config.reverse_travel_min_deg,
        "deep_reverse_limit_deg": config.reverse_travel_min_deg,
        "unlock_logic": "logic4",
        "unlock_blockers": unlock_blockers,
        "message": message,
    }


def _monitor_ra_ft(time_s: float) -> float:
    return max(0.0, MONITOR_RA_START_FT - MONITOR_RA_RATE_FT_PER_S * time_s)


def _monitor_tra_deg(time_s: float) -> float:
    if time_s < MONITOR_TRA_START_S:
        return 0.0
    return max(MONITOR_TRA_LOCK_DEG, -(time_s - MONITOR_TRA_START_S) * MONITOR_TRA_RATE_DEG_PER_S)


def _monitor_vdt_percent(time_s: float) -> float:
    if time_s < MONITOR_VDT_START_S:
        return 0.0
    return min(100.0, (time_s - MONITOR_VDT_START_S) * MONITOR_VDT_RATE_PERCENT_PER_S)


def _monitor_series_definition() -> list[dict]:
    return [
        {"id": "ra", "label": "RA", "unit": "ft", "display_min": 0.0, "display_max": 7.0, "color": "#ff6f91", "category": "input"},
        {"id": "tra", "label": "TRA", "unit": "deg", "display_min": -32.0, "display_max": 0.0, "color": "#ffaa33", "category": "input"},
        {"id": "sw1", "label": "SW1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
        {"id": "logic1", "label": "L1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "tls", "label": "TLS", "unit": "V", "display_min": 0.0, "display_max": 115.0, "color": "#7dff9a", "category": "power"},
        {"id": "sw2", "label": "SW2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
        {"id": "logic2", "label": "L2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "etrac", "label": "ETRAC", "unit": "V", "display_min": 0.0, "display_max": 540.0, "color": "#86ffbf", "category": "power"},
        {"id": "logic3", "label": "L3", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "eec", "label": "EEC", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "pls", "label": "PLS", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "pdu", "label": "PDU", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "vdt", "label": "VDT", "unit": "%", "display_min": 0.0, "display_max": 100.0, "color": "#b69dff", "category": "sensor"},
        {"id": "logic4", "label": "L4", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "thr_lock", "label": "THR_LOCK", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ff8c7a", "category": "command"},
    ]


def _monitor_transition_time(rows: list[dict], field_name: str, target_value) -> float | None:
    for row in rows:
        if row[field_name] == target_value:
            return row["time_s"]
    return None


def _monitor_rows(config: HarnessConfig) -> list[dict]:
    controller_adapter = build_reference_controller_adapter(config)
    switches = LatchedThrottleSwitches(config)
    switch_state = SwitchState(previous_tra_deg=0.0)
    tls_powered_s = 0.0
    pls_powered_s = 0.0
    tls_unlocked_ls = False
    all_pls_unlocked_ls = False
    rows: list[dict] = []

    step_count = int(round(MONITOR_TIMELINE_END_S / config.step_s))
    for step_index in range(step_count + 1):
        time_s = round(step_index * config.step_s, 3)
        radio_altitude_ft = _monitor_ra_ft(time_s)
        tra_deg = _monitor_tra_deg(time_s)
        vdt_percent = _monitor_vdt_percent(time_s)
        switch_state = switches.update(switch_state, tra_deg)

        inputs = ResolvedInputs(
            radio_altitude_ft=radio_altitude_ft,
            tra_deg=tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=MONITOR_ENGINE_RUNNING,
            aircraft_on_ground=MONITOR_AIRCRAFT_ON_GROUND,
            reverser_inhibited=MONITOR_REVERSER_INHIBITED,
            eec_enable=MONITOR_EEC_ENABLE,
            n1k=MONITOR_N1K,
            max_n1k_deploy_limit=MONITOR_MAX_N1K_DEPLOY_LIMIT,
            tls_unlocked_ls=tls_unlocked_ls,
            all_pls_unlocked_ls=all_pls_unlocked_ls,
            reverser_not_deployed_eec=vdt_percent <= 0.0,
            reverser_fully_deployed_eec=vdt_percent >= 100.0,
            deploy_90_percent_vdt=vdt_percent >= config.deploy_90_threshold_percent,
        )
        outputs, explain = controller_adapter.evaluate_with_explain(inputs)

        rows.append(
            {
                "time_s": time_s,
                "ra": round(radio_altitude_ft, 3),
                "tra": round(tra_deg, 3),
                "sw1": 1.0 if inputs.sw1 else 0.0,
                "logic1": 1.0 if outputs.logic1_active else 0.0,
                "tls": 115.0 if outputs.tls_115vac_cmd else 0.0,
                "sw2": 1.0 if inputs.sw2 else 0.0,
                "logic2": 1.0 if outputs.logic2_active else 0.0,
                "etrac": 540.0 if outputs.etrac_540vdc_cmd else 0.0,
                "logic3": 1.0 if outputs.logic3_active else 0.0,
                "eec": 1.0 if outputs.eec_deploy_cmd else 0.0,
                "pls": 1.0 if outputs.pls_power_cmd else 0.0,
                "pdu": 1.0 if outputs.pdu_motor_cmd else 0.0,
                "vdt": round(vdt_percent, 3),
                "logic4": 1.0 if outputs.logic4_active else 0.0,
                "thr_lock": 1.0 if outputs.throttle_electronic_lock_release_cmd else 0.0,
                "logic4_failed_conditions": [condition.name for condition in explain.logic4.failed_conditions],
            }
        )

        tls_powered_s = tls_powered_s + config.step_s if outputs.tls_115vac_cmd else 0.0
        tls_unlocked_ls = tls_unlocked_ls or (
            outputs.tls_115vac_cmd and tls_powered_s >= config.tls_unlock_delay_s
        )

        pls_powered_s = pls_powered_s + config.step_s if outputs.pls_power_cmd else 0.0
        pls_ready = outputs.pls_power_cmd and pls_powered_s >= config.pls_unlock_delay_s
        all_pls_unlocked_ls = all_pls_unlocked_ls or pls_ready

        if not (
            outputs.tls_115vac_cmd
            or outputs.etrac_540vdc_cmd
            or outputs.pls_power_cmd
            or outputs.pdu_motor_cmd
        ):
            tls_unlocked_ls = False
            all_pls_unlocked_ls = False

    return rows


def monitor_timeline_payload() -> dict:
    config = HarnessConfig()
    rows = _monitor_rows(config)
    series = []
    for definition in _monitor_series_definition():
        samples = [[row["time_s"], row[definition["id"]]] for row in rows]
        series.append({**definition, "samples": samples})

    l4_ready_time = _monitor_transition_time(rows, "logic4", 1.0)
    events = [
        {
            "time_s": 0.0,
            "label": "流程开始",
            "detail": "RA 从 7.0 ft 起步；TRA=0°；VDT=0%。",
        },
        {
            "time_s": 1.0,
            "label": "RA=6.0 ft",
            "detail": "TRA 从 0° 开始以 10°/s 推向 -14°。",
        },
        {
            "time_s": 2.4,
            "label": "TRA=-14°",
            "detail": "碰到 L4 条件限位；VDT 开始以 50%/s 从 0% 变化。",
        },
        {
            "time_s": 4.2,
            "label": "VDT90",
            "detail": "VDT 达到 90%，L4 / THR_LOCK 首次满足。",
        },
        {
            "time_s": MONITOR_ACTIVE_END_S,
            "label": "监测结束",
            "detail": "VDT=100%，主动监测流程完成。",
        },
        {
            "time_s": MONITOR_TIMELINE_END_S,
            "label": "RA=0 ft",
            "detail": "展示保持段：RA 继续匀速降到 0 ft 后保持。",
        },
    ]

    return {
        "mode": "timeline_monitor",
        "title": "受控状态监控时间线",
        "time_start_s": 0.0,
        "time_end_s": MONITOR_TIMELINE_END_S,
        "active_end_s": MONITOR_ACTIVE_END_S,
        "compression_ratio": MONITOR_TIMELINE_COMPRESSION_RATIO,
        "step_s": config.step_s,
        "model_note": (
            "这条监控图按用户定义的 RA -> TRA -> VDT 受控时间线生成；"
            "整段时间已压缩为原来的 1/10；VDT 按现有 demo 反馈语义绘制为 0%-100% 监测量，"
            "控制逻辑仍由 DeployController 评估。"
        ),
        "timeline_summary": {
            "ra_start_ft": MONITOR_RA_START_FT,
            "ra_hits_six_ft_at_s": 1.0,
            "tra_lock_deg": MONITOR_TRA_LOCK_DEG,
            "tra_reaches_lock_at_s": 2.4,
            "vdt_reaches_90_percent_at_s": 4.2,
            "vdt_reaches_100_percent_at_s": MONITOR_ACTIVE_END_S,
            "ra_reaches_zero_ft_at_s": MONITOR_TIMELINE_END_S,
            "l4_ready_at_s": l4_ready_time,
        },
        "events": events,
        "series": series,
}


# ---------------------------------------------------------------------------
# Multi-system snapshot support (P13)
# ---------------------------------------------------------------------------
SYSTEM_REGISTRY = {
    "thrust-reverser": build_reference_controller_adapter,
    "landing-gear": build_landing_gear_controller_adapter,
    "bleed-air": build_bleed_air_controller_adapter,
    "efds": build_efds_controller_adapter,
    # P43-02.5 (2026-04-21): C919 E-TRAS · certified · P34+P38 真实 PDF 接入 ·
    # reference panel target for P43-05 AI panel generator validation
    "c919-etras": build_c919_etras_controller_adapter,
}

# Cache built (stateless) adapters — avoid per-request instantiation overhead.
# P43-02.5: bumped maxsize 4→5 to accommodate c919-etras without evicting others.
@lru_cache(maxsize=5)
def _cached_adapter(system_id: str) -> Any:
    builder = SYSTEM_REGISTRY.get(system_id)
    if builder is None:
        return None
    return builder()

SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"


def _default_snapshot_for_system(system_id: str) -> dict:
    """Return a minimal/default snapshot for each registered system."""
    if system_id == "thrust-reverser":
        return {
            "radio_altitude_ft": 5.0,
            "tra_deg": 0.0,
            "sw1": False,
            "sw2": False,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 35.0,
            "max_n1k_deploy_limit": 60.0,
            "tls_unlocked_ls": False,
            "all_pls_unlocked_ls": False,
            "reverser_not_deployed_eec": True,
            "reverser_fully_deployed_eec": False,
            "deploy_90_percent_vdt": False,
        }
    elif system_id == "landing-gear":
        return {
            "gear_handle_position": "UP",
            "hydraulic_pressure_psi": 0.0,
            "uplock_released": False,
            "gear_position_percent": 0.0,
            "downlock_engaged": False,
        }
    elif system_id == "bleed-air":
        return {
            "valve_position": "CLOSED",
            "inlet_pressure": 0.0,
            "outlet_pressure": 0.0,
            "control_unit_ready": True,
        }
    elif system_id == "efds":
        return {
            "sensor.alt.radar": 5000.0,
            "sensor.alt.baro": 5200.0,
            "sensor.temp.external": 15.0,
            "sensor.threat.mls": "IDLE",
            "sensor.g.load": 1.0,
            "logic.armed_relay": "OPEN",
            "logic.firing_channel": "READY",
            "logic.crosslink_validator": "FALSE",
            "pilot.arm_switch": "SAFE",
            "pilot.manual_dispense": "RELEASED",
            "pilot.altitude_override": "AUTO",
            "actuator.flare_array": 24.0,
            "actuator.limiter_valve": "REGULATED",
        }
    elif system_id == "c919-etras":
        # P43-02.5 (2026-04-21): C919 E-TRAS default snapshot · nominal pre-deploy
        # state (aircraft on ground · engines at idle · TR fully stowed · no faults).
        # 34 fields aligned with c919_etras_adapter.py _snapshot_* helper calls.
        # PDF §1.1.x traceability preserved via hardware YAML (SHA256-locked).
        return {
            # --- A/C inputs ---
            "tra_deg": 0.0,                         # PDF §Step1 · throttle at forward idle
            "n1k_percent": 35.0,                    # Engine N1K at idle (adapter MONITOR_N1K)
            "engine_running": True,
            "tr_inhibited": False,                  # A/C bus · not inhibited
            # --- LGCU 双余度 MLG_WOW input (PDF 表2) ---
            "lgcu1_mlg_wow_value": True,            # LGCU1 reports on-ground
            "lgcu1_mlg_wow_valid": True,
            "lgcu2_mlg_wow_value": True,            # LGCU2 reports on-ground
            "lgcu2_mlg_wow_valid": True,
            # --- Selected TR_WOW (adapter _select_mlg_wow output · pre-computed for default) ---
            "tr_wow": True,
            # --- TLS (Translating Lock Sleeve · 双余度) · stowed=locked → unlocked=False ---
            "tls_ls_a_valid": True,
            "tls_ls_a_unlocked": False,
            "tls_ls_b_valid": True,
            "tls_ls_b_unlocked": False,
            # --- PLS (Primary Lock Sleeve · 双余度) · stowed=locked=True ---
            "pls_ls_a_locked": True,
            "pls_ls_b_locked": True,
            # --- Pylon locks (left+right · each 双余度) · stowed=locked → unlocked=False ---
            "left_pylon_ls_a_valid": True,
            "left_pylon_ls_a_unlocked": False,
            "left_pylon_ls_b_valid": True,
            "left_pylon_ls_b_unlocked": False,
            "right_pylon_ls_a_valid": True,
            "right_pylon_ls_a_unlocked": False,
            "right_pylon_ls_b_valid": True,
            "right_pylon_ls_b_unlocked": False,
            # --- Actuator/state inputs (nominal no-action) ---
            "apwtla": False,                        # All-pylons-wow-to-long-aggregate
            "atltla": False,                        # All-tls-long-to-long-aggregate
            # --- Sensors ---
            "vdt_sensor_valid": True,
            "e_tras_over_temp_fault": False,
            "trcu_power_on": True,
            # --- TR position (fully stowed at rest) ---
            "tr_position_percent": 0.0,
            # --- Command history (no prior EICU_CMD3 firing) ---
            "prev_eicu_cmd3": False,
            # --- Timing confirmation counters (accumulated dwell at nominal state) ---
            "comm2_timer_s": 0.0,
            "lock_unlock_confirm_s": 0.0,
            "tr_position_deployed_confirm_s": 0.0,
            "tr_stowed_locked_confirm_s": 2.0,      # ≥ 1.0s (TR_STOWED_LOCKED_CONFIRM_S) · nominal
        }
    return {}


def _spec_to_nodes(spec: dict, truth_evaluation: Any = None) -> list[dict]:
    """Build a nodes array from spec.components + spec.logic_nodes.

    Nodes are ordered to reflect the control flow: input conditions first,
    then parallel logic gates, then merge gates, then final outputs.
    This ordering is derived from the spec's logic_node downstream relationships.
    """
    active_ids: set[str] = set()
    if truth_evaluation is not None:
        active_ids = set(truth_evaluation.active_logic_node_ids)

    # Separate components into inputs vs intermediate/output components
    components = spec.get("components", [])
    logic_nodes = spec.get("logic_nodes", [])

    # Identify which components are upstream inputs (no logic_node depends on them as downstream)
    downstream_ids: set[str] = set()
    for ln in logic_nodes:
        for cid in ln.get("downstream_component_ids", []):
            downstream_ids.add(cid)

    # Components that appear as downstream of logic nodes → intermediate/output nodes
    # Components that don't → upstream input nodes
    upstream_input_ids: set[str] = set()
    intermediate_output_ids: set[str] = set()
    for comp in components:
        cid = comp["id"]
        if cid in downstream_ids:
            intermediate_output_ids.add(cid)
        else:
            upstream_input_ids.add(cid)

    # Build ordered node list:
    # 1. Upstream input components (sensors/pilot inputs)
    # 2. Logic nodes in dependency order
    # 3. Intermediate/output components (commands/power)
    nodes: list[dict] = []

    # Sort logic nodes by dependency: nodes whose downstream_component_ids feed into other logic nodes come first
    # For thrust-reverser: L1 and L2 are parallel (no cross-dependency), L3 depends on both, L4 depends on L3
    # Build a dependency graph to determine order
    node_ids = {ln["id"] for ln in logic_nodes}
    resolved: list[dict] = []
    remaining = list(logic_nodes)
    while remaining:
        made_progress = False
        for i, ln in enumerate(remaining):
            deps_met = True
            for cid in ln.get("downstream_component_ids", []):
                # Check if this component feeds into any remaining logic node
                for remaining_ln in remaining[i + 1:]:
                    if cid in remaining_ln.get("downstream_component_ids", []):
                        deps_met = False
                        break
                if not deps_met:
                    break
            if deps_met:
                resolved.append(remaining.pop(i))
                made_progress = True
                break
        if not made_progress:
            # Fallback: append remaining in order
            resolved.extend(remaining)
            break

    # Layer 1: upstream input components
    for comp in components:
        if comp["id"] in upstream_input_ids:
            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))

    # Layer 2: logic nodes in dependency order
    for ln in resolved:
        state = "active" if ln["id"] in active_ids else "inactive"
        nodes.append(_node(ln["id"], ln["label"], state, "spec.logic_nodes"))

    # Layer 3: intermediate/output components (commands/power)
    for comp in components:
        if comp["id"] in intermediate_output_ids:
            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))

    return nodes


def system_snapshot_payload(system_id: str) -> dict:
    """Build the payload for GET /api/system-snapshot."""
    adapter = _cached_adapter(system_id)
    if adapter is None:
        return {"error": "unknown_system", "system_id": system_id}
    spec = adapter.load_spec()
    default_snapshot = _default_snapshot_for_system(system_id)
    truth_eval = adapter.evaluate_snapshot(default_snapshot)
    nodes = _spec_to_nodes(spec, truth_eval)
    return {
        "system_id": system_id,
        "title": spec.get("title", system_id),
        "spec": spec,
        "nodes": nodes,
        "truth_evaluation": truth_eval.to_dict(),
        "default_snapshot": default_snapshot,
    }


def system_snapshot_post_payload(system_id: str, snapshot: dict) -> dict:
    """Evaluate a user-modified snapshot for a given system. Used by non-thrust systems."""
    adapter = _cached_adapter(system_id)
    if adapter is None:
        return {"error": "unknown_system", "system_id": system_id}
    spec = adapter.load_spec()
    truth_eval = adapter.evaluate_snapshot(snapshot)
    nodes = _spec_to_nodes(spec, truth_eval)
    return {
        "system_id": system_id,
        "title": spec.get("title", system_id),
        "spec": spec,
        "nodes": nodes,
        "truth_evaluation": truth_eval.to_dict(),
        "snapshot": snapshot,
    }


def lever_snapshot_payload(
    tra_deg: float,
    radio_altitude_ft: float = 5.0,
    engine_running: bool = True,
    aircraft_on_ground: bool = True,
    reverser_inhibited: bool = False,
    eec_enable: bool = True,
    n1k: float = 35.0,
    max_n1k_deploy_limit: float = 60.0,
    feedback_mode: str = "auto_scrubber",
    deploy_position_percent: float = 0.0,
    fault_injections: list[dict] | None = None,
) -> dict:
    config = HarnessConfig()
    requested_tra = _clamp_tra(tra_deg, config)
    lock_deg = _clamp_tra(TRA_L4_LOCK_DEG, config)
    requested_snapshot = _simulate_lever_state(
        requested_tra,
        config=config,
        radio_altitude_ft=radio_altitude_ft,
        engine_running=engine_running,
        aircraft_on_ground=aircraft_on_ground,
        reverser_inhibited=reverser_inhibited,
        eec_enable=eec_enable,
        n1k=n1k,
        max_n1k_deploy_limit=max_n1k_deploy_limit,
        feedback_mode=feedback_mode,
        deploy_position_percent=deploy_position_percent,
        fault_injections=fault_injections,
    )
    lock_probe = _simulate_lever_state(
        lock_deg,
        config=config,
        radio_altitude_ft=radio_altitude_ft,
        engine_running=engine_running,
        aircraft_on_ground=aircraft_on_ground,
        reverser_inhibited=reverser_inhibited,
        eec_enable=eec_enable,
        n1k=n1k,
        max_n1k_deploy_limit=max_n1k_deploy_limit,
        feedback_mode=feedback_mode,
        deploy_position_percent=deploy_position_percent,
        fault_injections=fault_injections,
    )
    boundary_unlock_ready = lock_probe["outputs"].logic4_active
    effective_tra = (
        requested_tra
        if boundary_unlock_ready or requested_tra >= lock_deg
        else lock_deg
    )
    snapshot = (
        requested_snapshot
        if effective_tra == requested_tra
        else lock_probe
    )

    time_s = snapshot["time_s"]
    plant_debug_state = snapshot["plant_state"]
    sensors = snapshot["sensors"]
    pilot_inputs = snapshot["pilot_inputs"]
    inputs = snapshot["inputs"]
    outputs = snapshot["outputs"]
    explain = snapshot["explain"]
    deep_range_open = boundary_unlock_ready
    tra_lock = _build_tra_lock_payload(
        config=config,
        requested_tra_deg=requested_tra,
        effective_tra_deg=effective_tra,
        lock_deg=lock_deg,
        boundary_unlock_ready=boundary_unlock_ready,
        deep_range_open=deep_range_open,
        unlock_blockers=[condition.name for condition in lock_probe["explain"].logic4.failed_conditions],
    )
    logic1_completed = sensors.tls_unlocked_ls
    logic4_blockers = [condition.name for condition in explain.logic4.failed_conditions]
    logic3_blockers = [condition.name for condition in explain.logic3.failed_conditions]

    nodes = [
        # ── Input sensor / signal nodes ──────────────────────────────────────
        # These are the ground-level signals; their "active" state is
        # computed to match the condition thresholds used by the logic gates.
        _node("radio_altitude_ft", "RA", "active" if inputs.radio_altitude_ft < 6.0 else "inactive",
              "Input sensors: altitude < 6 ft threshold"),
        _node("reverser_inhibited", "REV_INH",
              "inactive" if not inputs.reverser_inhibited else "active",
              "Input signals: true = inhibit active (blocked)"),
        _node("engine_running", "ENG",
              "active" if inputs.engine_running else "inactive",
              "Input signals"),
        _node("aircraft_on_ground", "GND",
              "active" if inputs.aircraft_on_ground else "inactive",
              "Input signals"),
        _node("eec_enable", "EEC_EN",
              "active" if inputs.eec_enable else "inactive",
              "Input signals"),
        _node("sw1", "SW1", "active" if inputs.sw1 else "inactive", "LatchedThrottleSwitches"),
        _node("sw2", "SW2", "active" if inputs.sw2 else "inactive", "LatchedThrottleSwitches"),
        # ── Intermediate / output nodes ────────────────────────────────────────
        _node("logic1", "L1", _logic_node_state(outputs.logic1_active), "DeployController.explain(logic1)", [condition.name for condition in explain.logic1.failed_conditions]),
        _node("tls115", "TLS115", "active" if outputs.tls_115vac_cmd or sensors.tls_unlocked_ls else "inactive", "DeployController outputs"),
        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
        _node("logic2", "L2", _logic_node_state(outputs.logic2_active), "DeployController.explain(logic2)", [condition.name for condition in explain.logic2.failed_conditions]),
        _node("etrac_540v", "540V", "active" if outputs.etrac_540vdc_cmd else "inactive", "DeployController outputs"),
        _node("logic3", "L3", _logic_node_state(outputs.logic3_active), "DeployController.explain(logic3)", logic3_blockers),
        _node("eec_deploy", "EEC", "active" if outputs.eec_deploy_cmd else "inactive", "DeployController outputs"),
        _node("pls_power", "PLS", "active" if outputs.pls_power_cmd else "inactive", "DeployController outputs"),
        _node("pdu_motor", "PDU", "active" if outputs.pdu_motor_cmd else "inactive", "DeployController outputs"),
        _node("vdt90", "VDT90", "active" if sensors.deploy_90_percent_vdt and outputs.logic3_active else "inactive", "SimplifiedDeployPlant sensors + L3 causal gate"),
        _node("logic4", "L4", _logic_node_state(outputs.logic4_active), "DeployController.explain(logic4)", logic4_blockers),
        _node(
            "thr_lock",
            "THR_LOCK",
            "active"
            if outputs.throttle_electronic_lock_release_cmd
            else (
                "blocked"
                if explain.logic4.failed_conditions
                else "inactive"
            ),
            # Use explain.logic4.failed_conditions to determine "blocked" vs "inactive".
            # This correctly handles the causal chain: when L4 is blocked (has unmet
            # conditions like tra_deg), THR_LOCK is "blocked" (waiting on L4).
            # When L4 has no failed conditions but is simply not active, THR_LOCK is "inactive".
            "DeployController outputs",
            logic4_blockers if not outputs.throttle_electronic_lock_release_cmd else [],
        ),
    ]
    summary = _lever_summary(effective_tra, inputs, sensors, outputs, explain, feedback_mode, tra_lock)
    model_note = (
        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
        if feedback_mode == "auto_scrubber"
        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"
    )

    result = {
        "mode": (
            "canonical_pullback_scrubber"
            if feedback_mode == "auto_scrubber"
            else "manual_feedback_override"
        ),
        "model_note": model_note,
        "tra_lock": tra_lock,
        "input": {
            "requested_tra_deg": requested_tra,
            "tra_deg": effective_tra,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "feedback_mode": feedback_mode,
            "deploy_position_percent": deploy_position_percent,
        },
        "time_s": time_s,
        "hud": {
            "requested_tra_deg": requested_tra,
            "tra_deg": effective_tra,
            "sw1": inputs.sw1,
            "sw2": inputs.sw2,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "tls_unlocked_ls": sensors.tls_unlocked_ls,
            "pls_unlocked_ls": sensors.pls_unlocked_ls,
            "all_pls_unlocked_ls": sensors.all_pls_unlocked,
            "deploy_position_percent": sensors.deploy_position_percent,
            # In manual override mode: gate VDT90 display on L3 being active.
            # The user can force deploy_position_percent>=90 manually, but that
            # doesn't mean the causal chain is satisfied — VDT90 requires L3
            # (EEC deploy command) to be active first.
            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt and outputs.logic3_active if feedback_mode == "manual_feedback_override" else sensors.deploy_90_percent_vdt,
            "feedback_mode": feedback_mode,
        },
        "outputs": {
            "logic1_active": outputs.logic1_active,
            "logic2_active": outputs.logic2_active,
            "logic3_active": outputs.logic3_active,
            "logic4_active": outputs.logic4_active,
            "tls_115vac_cmd": outputs.tls_115vac_cmd,
            "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
            "eec_deploy_cmd": outputs.eec_deploy_cmd,
            "pls_power_cmd": outputs.pls_power_cmd,
            "pdu_motor_cmd": outputs.pdu_motor_cmd,
            "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
        },
        "logic": {
            "logic1": _logic_payload(explain.logic1),
            "logic2": _logic_payload(explain.logic2),
            "logic3": _logic_payload(explain.logic3),
            "logic4": _logic_payload(explain.logic4),
        },
        "plant_state": {
            "tls_powered_s": plant_debug_state.tls_powered_s,
            "pls_powered_s": plant_debug_state.pls_powered_s,
            "tls_unlocked_ls": plant_debug_state.tls_unlocked_ls,
            "pls_unlocked_ls": plant_debug_state.pls_unlocked_ls,
            "deploy_position_percent": plant_debug_state.deploy_position_percent,
        },
        "nodes": nodes,
        "summary": summary,
        "evidence": [
            "switches=LatchedThrottleSwitches.update(...)",
            "controller=DeployController.evaluate_with_explain(...)",
            "explain=DeployController.explain(...)",
            "plant=SimplifiedDeployPlant first-cut feedback model",
            "tra_lock=L4 gate at -14° before deeper reverse travel",
        ],
        "risks": [
            "PLS / VDT feedback comes from simplified first-cut plant timing.",
            "Manual feedback override is only a diagnostic demo control, not new control truth.",
            "THR_LOCK release must not be read as complete physical root-cause proof.",
        ],
    }
    return _apply_fault_injections_to_snapshot_payload(result, fault_injections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
    parser.add_argument(
        "--open",
        action="store_true",
        help=(
            "Open the local UI URL with Python's standard-library webbrowser.open; "
            "this is a launch convenience, not browser E2E automation."
        ),
    )
    return parser


def demo_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/index.html"


def open_browser(url: str, opener=webbrowser.open) -> bool:
    try:
        opened = bool(opener(url))
    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
        return False
    if not opened:
        print(f"Could not open browser automatically. Open {url} manually.")
    return opened


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
    host, port = server.server_address
    url = demo_url(host, port)
    print(f"Serving well-harness demo UI at {url}")
    if args.open:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping well-harness demo UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

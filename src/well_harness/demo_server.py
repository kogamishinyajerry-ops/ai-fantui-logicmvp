"""Small local UI server for the deterministic demo reasoning layer."""

from __future__ import annotations

import argparse
import os
import secrets
from dataclasses import replace
from datetime import datetime, timezone
from functools import lru_cache
import json
import math
import re
import threading
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
# P56-04 (2026-04-28): C919 sim engine. The c919_etras_panel/index.html
# POSTs /api/tick on every 100ms timer; until this phase that path 404'd
# on the unified server, so the panel's ▶仿真 button silently no-op'd.
from well_harness.c919_tick_api import (
    C919SimState,
    handle_c919_tick as _handle_c919_tick_api,
    reset_c919_system as _reset_c919_system_api,
)
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
# E11-06 (2026-04-26): state-of-the-world status bar endpoint.
WORKBENCH_STATE_OF_WORLD_PATH = "/api/workbench/state-of-world"
# P44-01 (2026-04-26): control-logic circuit fragment endpoint.
# Extracts the L1→L4 SVG block from fantui_circuit.html (single source of
# truth) so /workbench can mount the circuit panel as the page hero.
# P45-01 (2026-04-26): same endpoint now parameterized by ?system=<id>.
WORKBENCH_CIRCUIT_FRAGMENT_PATH = "/api/workbench/circuit-fragment"
# P51-02 (2026-04-27): Live Log Panel SSE endpoint. Streams events
# from the in-memory log_stream ring buffer (last 500 entries) so a
# demo observer sees the executor's activity in real time.
WORKBENCH_LOG_STREAM_PATH = "/api/workbench/log-stream"
# P51-03 (2026-04-27): persistent governance decision history.
# Returns newest-first list of decisions across all executions so the
# workbench can render a single audit table instead of rescanning
# per-exec audit JSONs.
WORKBENCH_GOVERNANCE_HISTORY_PATH = "/api/workbench/governance/history"

# P45-01 (2026-04-26): map system_id → circuit source file under
# STATIC_DIR. Systems present in the workbench dropdown but missing
# here fall through to a "circuit not yet wired" placeholder SVG so
# /workbench renders cleanly instead of erroring out. Adding a new
# system = drop a circuit HTML file in static/ and add an entry here.
_CIRCUIT_SOURCE_BY_SYSTEM: dict[str, str] = {
    "thrust-reverser": "fantui_circuit.html",
    # P54-07 (2026-04-28): wire the existing C919 E-TRAS circuit
    # SVG so the workbench's circuit view stops showing the
    # "not yet wired" placeholder when the toggle is on C919.
    # The SVG uses a different viewBox (0 0 1020 560) than the
    # thrust-reverser one (0 0 1000 640); the fragment extractor
    # below was made viewBox-agnostic for this.
    "c919-etras": "c919_etras_panel/circuit.html",
    #
    # FROZEN 2026-04-26: landing-gear + bleed-air-valve were removed
    # from the dropdown per user direction (not the demo's target
    # cases). Their per-system gate + signal synonyms below stay as
    # architectural demonstrators that the workbench is general
    # across systems; they're routable via direct ?system= query but
    # no engineer surface advertises them.
}
# Per-system gate anchors that MUST appear in the served fragment.
# Keyed by system_id; if missing → no sanity-check (placeholder
# systems can't fail this guard).
_CIRCUIT_REQUIRED_GATES: dict[str, tuple[str, ...]] = {
    "thrust-reverser": ("L1", "L2", "L3", "L4"),
}


def _circuit_placeholder_fragment(system_id: str) -> str:
    """Return a self-contained SVG fragment for systems whose circuit
    file isn't drafted yet. The fragment carries no gate anchors —
    workbench review-mode + interpreter both gracefully no-op when
    they find none. The placeholder is honest: it tells the engineer
    exactly which system isn't wired and invites a ticket."""
    safe_id = system_id.replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<svg viewBox="0 0 1000 640" xmlns="http://www.w3.org/2000/svg" '
        'data-circuit-system="placeholder" data-circuit-system-id="'
        f'{safe_id}">'
        '<rect width="1000" height="640" fill="#04111a"/>'
        '<rect x="180" y="200" width="640" height="240" rx="14" '
        'fill="rgba(79,184,255,0.06)" stroke="rgba(79,184,255,0.4)" '
        'stroke-width="1.5" stroke-dasharray="6 6"/>'
        '<text x="500" y="290" fill="#4fb8ff" font-size="22" '
        'font-weight="700" text-anchor="middle">'
        '🛠 控制逻辑面板尚未接入 · Circuit not yet wired'
        '</text>'
        '<text x="500" y="332" fill="#cdd6e0" font-size="14" '
        f'text-anchor="middle">系统 · system: {safe_id}</text>'
        '<text x="500" y="370" fill="rgba(206,223,236,0.7)" '
        'font-size="12" text-anchor="middle">'
        '该系统的 L1..Ln 逻辑链路还没有 SVG 蓝图。请通过下方 修改建议 '
        '提交工单，'
        '</text>'
        '<text x="500" y="390" fill="rgba(206,223,236,0.7)" '
        'font-size="12" text-anchor="middle">'
        'Claude Code 接到 dev-queue 简报后会补齐电路图。'
        '</text>'
        '<text x="500" y="420" fill="rgba(206,223,236,0.55)" '
        'font-size="11" text-anchor="middle" font-style="italic">'
        'Drop a circuit HTML file under static/ and register it in '
        '_CIRCUIT_SOURCE_BY_SYSTEM to wire this system.'
        '</text>'
        '</svg>'
    )
# P44-02 (2026-04-26): rule-based interpretation of free-form engineer
# modification suggestions. Engineer types text, server returns
# structured {affected_gates, change_kind, target_signals, summary}
# so the UI can highlight the affected SVG gate(s) and ask the engineer
# to confirm the interpretation matches intent before ticket submission.
WORKBENCH_INTERPRET_SUGGESTION_PATH = "/api/workbench/interpret-suggestion"
# P44-03 (2026-04-26): change-proposal persistence. POST creates a new
# proposal record (engineer-confirmed interpretation), GET lists all
# stored records for the workbench inbox + KOGAMI reviewer surface.
PROPOSALS_PATH = "/api/proposals"
# P48-06 (2026-04-27): skill-executor approval bridge.
# Workbench reads pending audit + writes approval signal files
# the CLI executor's polling callback consumes.
SKILL_EXECUTIONS_PATH = "/api/skill-executions"
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
# P56-04 (2026-04-28): C919 sim endpoints. Both bare and namespaced
# paths point at the same C919SimState — the bare paths are what the
# legacy panel HTML POSTs to (originally targeting the standalone
# :9191 server). Namespaced aliases let new code use the cleaner form
# without disturbing the panel.
C919_TICK_PATH = "/api/tick"
C919_TICK_PATH_NAMESPACED = "/api/c919/tick"
C919_RESET_PATH = "/api/reset"
C919_RESET_PATH_NAMESPACED = "/api/c919/reset"
_C919_SIM_STATE = C919SimState()

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
        if parsed.path == WORKBENCH_LOG_STREAM_PATH:
            self._serve_log_stream(parsed)
            return
        if parsed.path == WORKBENCH_GOVERNANCE_HISTORY_PATH:
            self._serve_governance_history(parsed)
            return
        if parsed.path == SYSTEM_SNAPSHOT_PATH:
            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
            self._send_json(200, system_snapshot_payload(system_id))
            return
        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
            self._send_json(200, workbench_recent_archives_payload())
            return
        if parsed.path == WORKBENCH_STATE_OF_WORLD_PATH:
            # E11-06 (2026-04-26): aggregated state-of-the-world for the
            # /workbench top-of-page status bar. Read-only — never mutates
            # truth-engine state. Fields are *advisory*: they reflect the
            # last-recorded evidence (git SHA + qa_report.md + freeze
            # packet), not a live test run.
            self._send_json(200, workbench_state_of_world_payload())
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

        # P44-01 (2026-04-26): control-logic circuit fragment for /workbench
        # hero. Returns the L1→L4 SVG block extracted from fantui_circuit.html.
        if parsed.path == WORKBENCH_CIRCUIT_FRAGMENT_PATH:
            self._serve_workbench_circuit_fragment()
            return

        # P44-03 (2026-04-26): change-proposals list endpoint.
        # P45-02 (2026-04-26): now accepts ?system=<id> so the workbench
        # inbox scopes to the currently-selected system.
        if parsed.path == PROPOSALS_PATH:
            qs = parse_qs(parsed.query)
            status_filter = qs.get("status", [None])[0]
            system_filter = qs.get("system", [None])[0]
            self._send_json(
                200,
                {
                    "proposals": list_proposals(
                        status_filter=status_filter,
                        system_filter=system_filter,
                    ),
                },
            )
            return

        # P49-01b (2026-04-27): per-proposal latest-audit lookup.
        # The workbench inbox renders one execution-state badge per
        # proposal card; rather than each card scanning the full
        # audit list, the server returns just the freshest record.
        # Returns 200 with audit JSON, or 204 if no audit exists yet
        # for this proposal.
        # P50-02c (2026-04-27): also handles /execution/timings for
        # the lightweight per-phase duration tooltip.
        if (
            parsed.path.startswith(PROPOSALS_PATH + "/")
            and (
                parsed.path.endswith("/execution")
                or parsed.path.endswith("/execution/timings")
            )
        ):
            self._handle_proposal_latest_execution(parsed.path)
            return

        # P48-06 (2026-04-27): skill-execution audit reads.
        #   GET /api/skill-executions             list all
        #   GET /api/skill-executions?proposal=X  filter by proposal
        #   GET /api/skill-executions/<exec_id>   single record
        #   GET /api/skill-executions/pending     ASKING-state records
        if parsed.path == SKILL_EXECUTIONS_PATH:
            qs = parse_qs(parsed.query)
            proposal_filter = qs.get("proposal", [None])[0]
            state_filter = qs.get("state", [None])[0]
            self._handle_list_skill_executions(
                proposal_filter=proposal_filter,
                state_filter=state_filter,
            )
            return
        if parsed.path == f"{SKILL_EXECUTIONS_PATH}/pending":
            self._handle_list_skill_executions(state_filter="ASKING")
            return
        # P50-02a (2026-04-27): aggregate metrics for the workbench
        # observability panel. Cheaper than fetching the full audit
        # list — the panel just renders 9 counts + a pass-rate +
        # a duration summary.
        if parsed.path == f"{SKILL_EXECUTIONS_PATH}/metrics":
            self._handle_skill_execution_metrics()
            return
        # P50-10 (2026-04-27): forensics bundle. Hands the user
        # a single zip containing audits + slo_history.jsonl +
        # manifest, for offline incident review or sharing with a
        # colleague.
        if parsed.path == f"{SKILL_EXECUTIONS_PATH}/forensics-bundle":
            qs = parse_qs(parsed.query)
            since = qs.get("since", [None])[0]
            limit_raw = qs.get("limit", [None])[0]
            limit = 100  # default cap
            if limit_raw is not None:
                try:
                    limit = max(0, int(limit_raw))
                except ValueError:
                    pass
            self._handle_forensics_bundle(since=since, limit=limit)
            return
        # P50-08b (2026-04-27): SLO transition timeline. Answers
        # "when did this start breaking?" by replaying every
        # GREEN→YELLOW/RED transition the metrics endpoint has
        # recorded.
        if parsed.path == f"{SKILL_EXECUTIONS_PATH}/slo-history":
            qs = parse_qs(parsed.query)
            limit_raw = qs.get("limit", [None])[0]
            limit = None
            if limit_raw is not None:
                try:
                    limit = max(0, int(limit_raw))
                except ValueError:
                    limit = None
            self._handle_slo_history(limit=limit)
            return
        if parsed.path.startswith(f"{SKILL_EXECUTIONS_PATH}/"):
            suffix = parsed.path[len(SKILL_EXECUTIONS_PATH) + 1:]
            # `pending` already handled above; everything else is treated
            # as an exec_id. Approve/reject suffixes are POST-only.
            if "/" not in suffix and suffix:
                self._handle_get_skill_execution(suffix)
                return

        # E11-07 (2026-04-26): Authority Contract banner link target.
        # Serves the v6.1 truth-engine red-line clause as plain text so
        # the banner's "v6.1 红线条款 →" link resolves to a real, in-repo
        # excerpt rather than a 404. Read-only; no truth-engine mutation.
        if parsed.path in ("/v6.1-redline", "/v6.1-redline.txt"):
            self._serve_v61_redline_excerpt()
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
        if parsed.path == WORKBENCH_INTERPRET_SUGGESTION_PATH:
            self._handle_interpret_suggestion()
            return
        if parsed.path == PROPOSALS_PATH:
            self._handle_create_proposal()
            return
        # P44-05 (2026-04-26): /api/proposals/<id>/accept|reject. We
        # match on the prefix + suffix here so the id segment is
        # opaque (matches whatever shape _new_proposal_id() produces).
        if parsed.path.startswith(PROPOSALS_PATH + "/") and (
            parsed.path.endswith("/accept") or parsed.path.endswith("/reject")
        ):
            self._handle_proposal_transition(parsed.path)
            return
        # P47-02 (2026-04-27): /api/proposals/<id>/landed and
        # /api/proposals/<id>/propose-revert.
        if parsed.path.startswith(PROPOSALS_PATH + "/") and parsed.path.endswith("/landed"):
            self._handle_proposal_landed(parsed.path)
            return
        if parsed.path.startswith(PROPOSALS_PATH + "/") and parsed.path.endswith(
            "/propose-revert"
        ):
            self._handle_proposal_propose_revert(parsed.path)
            return
        # P48-06 (2026-04-27): skill-execution approval bridge.
        #   POST /api/skill-executions/<exec_id>/approve
        #   POST /api/skill-executions/<exec_id>/reject
        # P49-01c (2026-04-27): cancel — abort a non-terminal exec.
        #   POST /api/skill-executions/<exec_id>/cancel
        # P49-02b (2026-04-27): governance gate UI bridge.
        #   POST /api/skill-executions/<exec_id>/governance-approve
        #   POST /api/skill-executions/<exec_id>/governance-reject
        if parsed.path.startswith(SKILL_EXECUTIONS_PATH + "/") and (
            parsed.path.endswith("/approve")
            or parsed.path.endswith("/reject")
            or parsed.path.endswith("/cancel")
            or parsed.path.endswith("/governance-approve")
            or parsed.path.endswith("/governance-reject")
        ):
            if parsed.path.endswith("/cancel"):
                self._handle_skill_execution_cancel(parsed.path)
            elif parsed.path.endswith("/governance-approve") or \
                    parsed.path.endswith("/governance-reject"):
                self._handle_skill_execution_governance(parsed.path)
            else:
                self._handle_skill_execution_approval(parsed.path)
            return
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
            C919_TICK_PATH,
            C919_TICK_PATH_NAMESPACED,
            C919_RESET_PATH,
            C919_RESET_PATH_NAMESPACED,
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
        # P56-04 (2026-04-28): C919 sim endpoints. The legacy bare
        # paths (/api/tick, /api/reset) are what the
        # c919_etras_panel/index.html JS POSTs to on every 100ms
        # timer; the namespaced /api/c919/* aliases coexist for new
        # code. Both routes share one C919SimState so successive
        # ticks accumulate FSM state across HTTP requests.
        if parsed.path in (C919_TICK_PATH, C919_TICK_PATH_NAMESPACED):
            status, result = _handle_c919_tick_api(
                _C919_SIM_STATE, request_payload,
            )
            self._send_json(status, result)
            return
        if parsed.path in (C919_RESET_PATH, C919_RESET_PATH_NAMESPACED):
            self._send_json(200, _reset_c919_system_api(_C919_SIM_STATE))
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

    def _serve_governance_history(self, parsed):
        """P51-03: GET /api/workbench/governance/history[?limit=N].
        Returns newest-first decision history persisted to disk by
        the orchestrator's governance gate. Survives restarts so a
        reviewer landing on the dashboard sees the full backlog,
        not just decisions from the current process lifetime."""
        from urllib.parse import parse_qs

        from well_harness.skill_executor.governance_history import (
            read_history,
        )

        qs = parse_qs(parsed.query)
        try:
            limit_raw = qs.get("limit", [None])[0]
            limit = int(limit_raw) if limit_raw is not None else None
        except (TypeError, ValueError):
            limit = None

        entries = read_history(limit=limit)
        self._send_json(
            200,
            {"decisions": [e.to_json() for e in entries]},
        )

    def _serve_log_stream(self, parsed):
        """P51-02: Server-Sent Events stream of the workbench log
        ring buffer. Holds the connection open for up to
        WORKBENCH_LOG_STREAM_DURATION_SEC seconds, polling the
        buffer every 0.5s and pushing new entries since the client's
        cursor. Browser auto-reconnects when the connection drops,
        carrying the cursor in `?since=N` so no events are lost.

        Bounded session length keeps stale tabs from holding threads
        forever — ThreadingHTTPServer spawns one thread per
        connection. Every reconnect picks up the next 60s window."""
        import json as _json
        import time as _time
        from urllib.parse import parse_qs

        from well_harness.skill_executor import log_stream

        qs = parse_qs(parsed.query)
        try:
            cursor = int(qs.get("since", ["0"])[0])
        except (TypeError, ValueError):
            cursor = 0

        # Header phase. Once written, we cannot send a JSON 4xx from
        # this handler. Test mode exits after ONE drain so a unit
        # test can call the endpoint without blocking.
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        # Close the underlying TCP connection at end of session so
        # http.client (and curl) actually return from .read(). The
        # browser EventSource doesn't care about Connection: keep-
        # alive — it manages its own auto-reconnect.
        self.send_header("Connection", "close")
        self.close_connection = True
        # CORS not needed (same-origin); skip ACAO so an external
        # page can't tap the live executor stream.
        self.end_headers()

        duration = float(
            os.environ.get("WORKBENCH_LOG_STREAM_DURATION_SEC", "60")
        )
        poll = float(
            os.environ.get("WORKBENCH_LOG_STREAM_POLL_SEC", "0.5")
        )
        deadline = _time.time() + duration
        try:
            while _time.time() < deadline:
                events = log_stream.events_since(cursor)
                for ev in events:
                    payload = _json.dumps(ev.to_json())
                    self.wfile.write(
                        f"data: {payload}\n\n".encode("utf-8")
                    )
                    self.wfile.flush()
                    cursor = ev.seq
                # Heartbeat comment so proxies don't time out and so
                # the test client can detect connection liveness.
                self.wfile.write(f": cursor={cursor}\n\n".encode("utf-8"))
                self.wfile.flush()
                _time.sleep(poll)
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected — totally normal for SSE. Don't
            # log; the caller is just navigating away.
            return

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

    def _serve_v61_redline_excerpt(self):
        """E11-07 (2026-04-26): serve the v6.1 truth-engine red-line clause
        as plain text. Sourced from .planning/constitution.md so the demo
        ships the same words the constitution does, with no drift risk."""
        repo_root = Path(__file__).resolve().parents[2]
        constitution = repo_root / ".planning" / "constitution.md"
        try:
            full_text = constitution.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            full_text = ""
        excerpt_lines = ["# v6.1 truth-engine red-line clause\n", ""]
        if full_text:
            # Pull the explicit "Forbidden（红线维持）" section. If the
            # exact heading drifts, fall back to a small static excerpt
            # so the link still resolves to *something* truthful.
            anchor = full_text.find("Forbidden（红线维持")
            if anchor != -1:
                end = full_text.find("\n## ", anchor)
                section = full_text[anchor:end] if end != -1 else full_text[anchor:]
                excerpt_lines.append(section.rstrip())
            else:
                excerpt_lines.append(
                    "Truth-engine 红线: controller / runner / models / "
                    "adapters/ are read-only by design. Workbench surfaces "
                    "may propose changes via ticket / proposal — they may "
                    "never mutate truth-engine values directly. See "
                    ".planning/constitution.md §v6.1 Solo Autonomy Delegation."
                )
        else:
            excerpt_lines.append(
                "Truth-engine 红线 source file (.planning/constitution.md) "
                "is not available in this checkout. The contract remains: "
                "controller / runner / models / adapters/ are read-only."
            )
        body = "\n".join(excerpt_lines).encode("utf-8")
        self._send_bytes(200, body, "text/plain; charset=utf-8")

    def _handle_interpret_suggestion(self):
        """P44-02 (2026-04-26): rule-based interpretation of a free-form
        engineer modification suggestion. POST body: {"text": "..."}.

        P45-03 (2026-04-26): now also supports an LLM strategy. POST
        body or query string:
          {"text": "...", "strategy": "rules" | "llm",
           "system_id": "thrust-reverser"}
        The default remains "rules" so every existing caller is
        unaffected. With strategy="llm", interpret_suggestion_text_llm
        is called; on any failure (no API key, network, parse error)
        it falls back to rules and tags the response with
        interpreter_strategy="llm_fallback_to_rules" + llm_error.

        Truth-engine red line preserved: this endpoint READS the
        engineer's text and returns a structured restatement; it
        never writes to controller / runner / models / adapters. The
        LLM call is an outbound HTTP request; the result is parsed
        and normalized to the same schema as the rules interpreter
        before being returned."""
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > 100_000:
            self._send_json(400, {"error": "empty_or_oversized_body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        text = payload.get("text", "")
        if not isinstance(text, str) or not text.strip():
            self._send_json(400, {"error": "missing_or_empty_text"})
            return
        if len(text) > 5000:
            self._send_json(400, {"error": "text_too_long", "max_chars": 5000})
            return
        # Strategy may come from POST body (preferred) or query string
        # (convenience). Unknown strategies fall back to "rules" rather
        # than 400 — being permissive here keeps the demo resilient if
        # a frontend version ships with a typoed value.
        strategy = str(payload.get("strategy") or "rules").strip().lower()
        if strategy not in ("rules", "llm"):
            strategy = "rules"
        system_id = str(payload.get("system_id") or "thrust-reverser").strip() or "thrust-reverser"
        if strategy == "llm":
            result = interpret_suggestion_text_llm(text, system_id=system_id)
        else:
            # P46-02: rules path now also honors system_id so the
            # engineer gets the right vocabulary on every system.
            result = interpret_suggestion_text(text, system_id=system_id)
            result["interpreter_strategy"] = "rules"
        self._send_json(200, result)

    def _handle_create_proposal(self):
        """P44-03 (2026-04-26): create a change-proposal record.

        POST body:
          {
            "source_text": "...",            (required, the engineer's
                                              original suggestion text)
            "interpretation": { ... },       (required, the structured
                                              interpretation the engineer
                                              just confirmed)
            "author_name": "Kogami / Engineer",   (optional, defaults to
                                              "anonymous")
            "author_role": "ENGINEER",       (optional, defaults to
                                              "ENGINEER")
            "ticket_id": "WB-E06-SHELL",     (optional, defaults to
                                              "ad-hoc")
            "system_id": "thrust-reverser"   (optional, defaults to
                                              "thrust-reverser")
          }

        Returns 201 with the persisted record.

        Truth-engine red line preserved: proposals are an adapter-only
        store under .planning/proposals/ — no truth-engine module is
        modified, no controller/runner/models/adapter is rewritten by
        accepting a proposal. P44-05 will wire ACCEPTED proposals into
        Claude Code's /gsd-execute-phase pipeline; that pipeline still
        writes through normal git/PR review, so truth never bypasses the
        constitutional gates."""
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > 200_000:
            self._send_json(400, {"error": "empty_or_oversized_body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        source_text = payload.get("source_text", "")
        interpretation = payload.get("interpretation")
        if not isinstance(source_text, str) or not source_text.strip():
            self._send_json(400, {"error": "missing_or_empty_source_text"})
            return
        if not isinstance(interpretation, dict):
            self._send_json(400, {"error": "missing_or_invalid_interpretation"})
            return
        # Schema sanity-check on interpretation: must carry the canonical
        # fields the UI showed the engineer for confirmation.
        for required_field in (
            "affected_gates",
            "target_signals",
            "change_kind",
            "summary_zh",
        ):
            if required_field not in interpretation:
                self._send_json(
                    400,
                    {
                        "error": "interpretation_missing_field",
                        "field": required_field,
                    },
                )
                return
        try:
            record = create_proposal(
                source_text=source_text,
                interpretation=interpretation,
                author_name=str(payload.get("author_name") or "anonymous"),
                author_role=str(payload.get("author_role") or "ENGINEER"),
                ticket_id=str(payload.get("ticket_id") or "ad-hoc"),
                system_id=str(payload.get("system_id") or "thrust-reverser"),
            )
        except OSError as exc:
            self._send_json(500, {"error": "proposal_persistence_failed", "detail": str(exc)})
            return
        self._send_json(201, record)

    def _handle_proposal_transition(self, raw_path: str):
        """P44-05 (2026-04-26): accept or reject a proposal.

        POST /api/proposals/<id>/accept  →  flips OPEN → ACCEPTED, writes
                                            a dev-queue brief Claude Code
                                            can pick up via /gsd-execute-phase
        POST /api/proposals/<id>/reject  →  flips OPEN → REJECTED

        Optional JSON body:
          {
            "actor": "Kogami",      (optional, defaults to "anonymous")
            "note":  "free text"    (optional, persisted to history;
                                     useful as rejection reason)
          }

        Returns 200 with the updated record. Errors:
          404 — proposal id not found
          409 — proposal already ACCEPTED or REJECTED
          400 — invalid path / json
        """
        # Path shape: /api/proposals/<id>/<action>
        suffix = raw_path[len(PROPOSALS_PATH) + 1 :]
        try:
            proposal_id, action = suffix.rsplit("/", 1)
        except ValueError:
            self._send_json(400, {"error": "invalid_proposal_action_path"})
            return
        if action not in ("accept", "reject") or not proposal_id:
            self._send_json(400, {"error": "invalid_proposal_action"})
            return
        new_status = "ACCEPTED" if action == "accept" else "REJECTED"
        # Body is optional — empty/missing is fine.
        actor = "anonymous"
        note: str | None = None
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 0:
            if length > 50_000:
                self._send_json(400, {"error": "oversized_body"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "invalid_json"})
                return
            if isinstance(payload, dict):
                actor = str(payload.get("actor") or "anonymous")
                raw_note = payload.get("note")
                note = str(raw_note) if isinstance(raw_note, str) and raw_note.strip() else None
        record, error_code = update_proposal_status(
            proposal_id,
            new_status=new_status,
            actor=actor,
            note=note,
        )
        if error_code == "not_found":
            self._send_json(404, {"error": "proposal_not_found", "id": proposal_id})
            return
        if error_code == "already_terminal":
            self._send_json(
                409,
                {
                    "error": "proposal_already_terminal",
                    "id": proposal_id,
                    "current_status": (record or {}).get("status"),
                },
            )
            return
        if error_code is not None or record is None:
            self._send_json(500, {"error": "proposal_transition_failed"})
            return
        # P49-01a (2026-04-27): close the trigger loop. On a successful
        # OPEN→ACCEPTED transition, hand off to the skill_executor as a
        # detached subprocess. Opt-in via WORKBENCH_AUTO_SPAWN_EXECUTOR;
        # disabled by default so existing dev workflows are unaffected.
        # Spawn failures never fail the accept call — the proposal IS
        # accepted regardless of whether the executor launched.
        spawn_info: dict | None = None
        if new_status == "ACCEPTED":
            try:
                spawn_result = _spawn_executor_for_proposal(
                    proposal_id,
                    repo_root=Path(__file__).resolve().parents[2],
                )
                spawn_info = {
                    "status": spawn_result.status.value,
                    "pid": spawn_result.pid,
                    "log": (
                        str(spawn_result.log_path)
                        if spawn_result.log_path
                        else None
                    ),
                    "note": spawn_result.note,
                }
            except _SpawnerError as exc:
                spawn_info = {"status": "error", "error": str(exc)}
        if spawn_info is not None:
            payload = dict(record)
            payload["spawn"] = spawn_info
            self._send_json(200, payload)
            return
        self._send_json(200, record)

    def _handle_proposal_landed(self, raw_path: str):
        """P47-02 (2026-04-27): record the truth-engine commit SHA that
        fulfills an ACCEPTED proposal. Called by the executor (Claude
        Code skill) after merging the truth-engine PR.

        POST /api/proposals/<id>/landed
        Body: {"sha": "abc1234[5678…]", "actor": "..."}  (actor optional)

        Errors:
          400 — bad path / json / sha format
          404 — proposal id not found
          409 — proposal not ACCEPTED, OR a different SHA already landed
        """
        suffix = raw_path[len(PROPOSALS_PATH) + 1 :]
        # Strip trailing /landed
        if not suffix.endswith("/landed"):
            self._send_json(400, {"error": "invalid_landed_path"})
            return
        proposal_id = suffix[: -len("/landed")]
        if not proposal_id:
            self._send_json(400, {"error": "invalid_proposal_id"})
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            self._send_json(400, {"error": "missing_body"})
            return
        if length > 50_000:
            self._send_json(400, {"error": "oversized_body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(payload, dict):
            self._send_json(400, {"error": "invalid_json_object"})
            return
        sha = payload.get("sha")
        actor = str(payload.get("actor") or "claude-code-executor")
        if not isinstance(sha, str) or not sha.strip():
            self._send_json(400, {"error": "missing_sha"})
            return
        record, error_code = record_proposal_landed(
            proposal_id, sha=sha, actor=actor
        )
        if error_code == "not_found":
            self._send_json(404, {"error": "proposal_not_found", "id": proposal_id})
            return
        if error_code == "invalid_sha":
            self._send_json(400, {"error": "invalid_sha_format"})
            return
        if error_code == "wrong_status":
            self._send_json(
                409,
                {
                    "error": "proposal_not_accepted",
                    "id": proposal_id,
                    "current_status": (record or {}).get("status"),
                },
            )
            return
        if error_code == "already_landed":
            self._send_json(
                409,
                {
                    "error": "proposal_already_landed",
                    "id": proposal_id,
                    "existing_sha": (record or {}).get("landed_truth_sha"),
                },
            )
            return
        if error_code is not None or record is None:
            self._send_json(500, {"error": "proposal_landed_failed"})
            return
        self._send_json(200, record)

    def _handle_proposal_propose_revert(self, raw_path: str):
        """P47-02 (2026-04-27): create a new revert proposal targeting
        an already-landed accepted proposal.

        POST /api/proposals/<id>/propose-revert
        Body: {"author_name": "Kogami"}  (optional)

        Errors:
          400 — bad path / json
          404 — original proposal id not found
          409 — original is not ACCEPTED-with-landed-sha, OR a revert is
                already in flight
        """
        suffix = raw_path[len(PROPOSALS_PATH) + 1 :]
        if not suffix.endswith("/propose-revert"):
            self._send_json(400, {"error": "invalid_revert_path"})
            return
        original_id = suffix[: -len("/propose-revert")]
        if not original_id:
            self._send_json(400, {"error": "invalid_proposal_id"})
            return
        author_name = "anonymous"
        author_role = "REVIEWER"
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 0:
            if length > 50_000:
                self._send_json(400, {"error": "oversized_body"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "invalid_json"})
                return
            if isinstance(payload, dict):
                author_name = str(payload.get("author_name") or "anonymous")
                author_role = str(payload.get("author_role") or "REVIEWER")
        record, error_code = create_revert_proposal(
            original_id,
            author_name=author_name,
            author_role=author_role,
        )
        if error_code == "not_found":
            self._send_json(404, {"error": "proposal_not_found", "id": original_id})
            return
        if error_code == "not_landed":
            self._send_json(
                409,
                {
                    "error": "original_not_landed",
                    "id": original_id,
                    "hint": "original must be ACCEPTED with a landed_truth_sha",
                },
            )
            return
        if error_code == "already_reverted":
            self._send_json(
                409,
                {
                    "error": "revert_already_in_flight",
                    "id": original_id,
                },
            )
            return
        if error_code is not None or record is None:
            self._send_json(500, {"error": "propose_revert_failed"})
            return
        self._send_json(201, record)

    # ─── P48-06 (2026-04-27): skill-execution approval bridge ────────

    def _handle_list_skill_executions(
        self,
        *,
        proposal_filter: str | None = None,
        state_filter: str | None = None,
    ) -> None:
        """GET /api/skill-executions[?proposal=X][?state=Y].

        Returns `{executions: [audit-record-as-dict, ...]}` newest
        first. Both filters are optional. The polling workbench UI
        uses `?state=ASKING` to find pending executions for the
        approval card.
        """
        try:
            from well_harness.skill_executor.audit import list_audits
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        records = list_audits(
            proposal_id=proposal_filter,
            state_filter=state_filter,
        )
        self._send_json(
            200,
            {"executions": [r.to_json() for r in records]},
        )

    def _handle_proposal_latest_execution(self, raw_path: str) -> None:
        """GET /api/proposals/<proposal_id>/execution.

        Returns the most recent skill_executor audit for the given
        proposal_id (newest first by exec_id). Used by the workbench
        inbox to render one state badge per proposal card without
        each card scanning the full audit list.

        Also handles /execution/timings: same audit but only the
        per-phase timings breakdown (cheaper response for the
        timing tooltip).

        200 — audit JSON for the freshest execution (or timings)
        204 — no audit exists yet for this proposal (the executor
              never ran, or was disabled)
        400 — malformed path
        """
        try:
            from well_harness.skill_executor.audit import list_audits
            from well_harness.skill_executor.phase_timings import (
                compute_phase_timings,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        # P50-02c: route /execution and /execution/timings together.
        # Both share the same audit lookup; only the response shape
        # differs.
        prefix = PROPOSALS_PATH + "/"
        timings_only = raw_path.endswith("/execution/timings")
        if timings_only:
            suffix_len = len("/execution/timings")
        elif raw_path.endswith("/execution"):
            suffix_len = len("/execution")
        else:
            self._send_json(400, {"error": "invalid_path"})
            return
        if not raw_path.startswith(prefix):
            self._send_json(400, {"error": "invalid_path"})
            return
        proposal_id = raw_path[len(prefix) : -suffix_len]
        if not proposal_id or "/" in proposal_id:
            self._send_json(400, {"error": "invalid_proposal_id"})
            return
        records = list_audits(proposal_id=proposal_id)
        if not records:
            # 204 No Content — semantically "no execution yet"
            self.send_response(204)
            self.end_headers()
            return
        latest = records[0]
        if timings_only:
            self._send_json(200, compute_phase_timings(latest).to_json())
            return
        # Default: full audit + a phase_timings sidecar block so
        # callers get both with one round-trip.
        payload = latest.to_json()
        payload["phase_timings"] = compute_phase_timings(latest).to_json()
        self._send_json(200, payload)

    def _handle_skill_execution_metrics(self) -> None:
        """GET /api/skill-executions/metrics. Returns aggregate
        Metrics JSON over every audit currently on disk. Empty input
        produces an all-zero response so the panel can render
        deterministically before the first execution.

        Side effect (P50-08b): if the SLO verdict has changed since
        the last poll, append an entry to slo_history.jsonl. The
        dashboard's 5s polling cadence drives the timeline
        resolution. Steady-state polls don't append.
        """
        try:
            from well_harness.skill_executor.audit import (
                audit_dir, list_audits,
            )
            from well_harness.skill_executor.metrics import compute_metrics
            from well_harness.skill_executor.slo_history import (
                record_transition,
            )
            from well_harness.skill_executor.slo_webhook import (
                dispatch_transition,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        records = list_audits()
        metrics = compute_metrics(records)
        # Record a transition if the verdict changed. Failure to
        # write the history line must NOT break the metrics
        # response — the dashboard takes precedence over the log.
        transition = None
        try:
            transition = record_transition(
                audit_dir(),
                current_status=metrics.slo_status,
                metrics=metrics,
            )
        except OSError:
            pass
        # P50-09: best-effort webhook dispatch on real transitions
        # (steady-state polls produced no transition → no fire).
        # P50-11: per-severity throttle suppresses repeat alerts
        # within an interval window so a flapping system doesn't
        # spam the operator. Throttle state is persisted to disk
        # next to slo_history.jsonl.
        # P50-12: every poll also flushes pending suppressed
        # events whose throttle window has expired into a single
        # digest webhook ("while you were silenced, these N
        # transitions happened"), so a flap-then-stable system
        # doesn't drop the regression silently.
        try:
            from well_harness.skill_executor.slo_webhook_throttle import (
                read_state, record_fire, record_suppressed,
                resolve_min_interval_sec, should_fire,
                take_digest_due, write_state,
            )
            from well_harness.skill_executor.slo_webhook import (
                dispatch_digest,
            )
            from datetime import datetime, timezone
            state = read_state(audit_dir())
            now_iso = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            min_interval = resolve_min_interval_sec()
            state_dirty = False

            # P50-12: flush any digests whose throttle window has
            # expired BEFORE processing the new transition. This
            # ordering means the digest covers events suppressed
            # in the prior window, not including the current one
            # (which gets its own normal throttle treatment).
            due = take_digest_due(
                state, now_iso=now_iso, min_interval_sec=min_interval,
            )
            for severity, events in due.items():
                try:
                    dispatch_digest(severity, events, ts=now_iso)
                except Exception:
                    # Even an unexpected dispatch_digest failure
                    # must not propagate. The events were already
                    # popped from state — accept the data loss to
                    # keep the dashboard responsive. Future P50-12b
                    # could retry-queue these.
                    pass
                state_dirty = True

            # New transition (P50-09 + P50-11 path)
            if transition is not None:
                decision = should_fire(
                    transition,
                    state=state,
                    now_iso=now_iso,
                    min_interval_sec=min_interval,
                )
                if decision.allow:
                    try:
                        dispatch_transition(transition)
                    except Exception:
                        pass
                    record_fire(
                        state,
                        to_severity=str(getattr(
                            transition, "to_severity", "",
                        )),
                        now_iso=now_iso,
                    )
                    state_dirty = True
                else:
                    # P50-12: stash the suppressed event so a
                    # future digest can recover it.
                    record_suppressed(state, transition=transition)
                    state_dirty = True

            if state_dirty:
                try:
                    write_state(audit_dir(), state)
                except OSError:
                    # Read-only fs / disk full: don't fail the
                    # request. Worst case the next poll might
                    # re-fire (effectively no throttle that one
                    # round) — better than no metrics response.
                    pass
        except Exception:
            # Defense in depth: even unexpected failures here
            # must not propagate to the metrics response.
            pass
        self._send_json(200, metrics.to_json())

    def _handle_slo_history(self, *, limit: int | None) -> None:
        """GET /api/skill-executions/slo-history[?limit=N].
        Returns the SLO transition log as a JSON array — newest-
        last (file-order). Frontend reverses for display."""
        try:
            from well_harness.skill_executor.audit import audit_dir
            from well_harness.skill_executor.slo_history import (
                load_history,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        transitions = load_history(audit_dir(), limit=limit)
        self._send_json(200, {
            "transitions": [t.to_json() for t in transitions],
            "count": len(transitions),
        })

    def _handle_forensics_bundle(
        self, *, since: str | None, limit: int,
    ) -> None:
        """GET /api/skill-executions/forensics-bundle.
        Streams a zip of audits + slo_history + manifest so an
        oncall can grab a snapshot of system state in one click
        for offline review or sharing with a colleague.

        Query params:
          - since: ISO timestamp; drop audits older than this
          - limit: cap on audit count (newest-first), default 100

        Always returns 200 with a zip body — empty audit dirs
        produce a small bundle with just the manifest + README.
        """
        try:
            from well_harness.skill_executor.audit import audit_dir
            from well_harness.skill_executor.forensics_bundle import (
                build_bundle,
                default_bundle_filename,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        try:
            zip_bytes, _manifest = build_bundle(
                audit_dir(), since=since, limit=limit,
            )
        except OSError:
            self._send_json(500, {"error": "bundle_build_failed"})
            return
        # Force a download with a UTC-stamped filename so the
        # operator's downloads folder doesn't collect collision-y
        # `bundle.zip` `bundle (1).zip` ladders.
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="{default_bundle_filename()}"',
        )
        self.send_header("Content-Length", str(len(zip_bytes)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(zip_bytes)

    def _handle_get_skill_execution(self, exec_id: str) -> None:
        """GET /api/skill-executions/<exec_id>. Returns the audit
        record, or 404 if not found / 400 if id malformed."""
        try:
            from well_harness.skill_executor.audit import read_audit
            from well_harness.skill_executor.errors import AuditSchemaError
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return
        try:
            record = read_audit(exec_id)
        except AuditSchemaError as exc:
            msg = str(exc).lower()
            if "not found" in msg:
                self._send_json(404, {"error": "audit_not_found", "id": exec_id})
                return
            if "invalid exec_id shape" in msg:
                self._send_json(400, {"error": "invalid_exec_id"})
                return
            self._send_json(400, {"error": "audit_schema_invalid", "detail": str(exc)})
            return
        self._send_json(200, record.to_json())

    def _handle_skill_execution_approval(self, raw_path: str) -> None:
        """POST /api/skill-executions/<exec_id>/{approve,reject}.

        Writes a single-line approval signal file the CLI executor's
        polling callback consumes. The audit must currently be in
        ASKING state — approving/rejecting an audit in any other
        state is a 409 conflict.

        Optional JSON body: {"actor": "Kogami", "note": "..."}
        Both fields are recorded back into the audit's most recent
        Ask entry so a reviewer reading the audit later sees who
        clicked.
        """
        try:
            from well_harness.skill_executor.audit import (
                audit_dir as audit_dir_resolver,
                read_audit,
                write_audit,
            )
            from well_harness.skill_executor.errors import AuditSchemaError
            from well_harness.skill_executor.models import (
                AskResponse,
                now_iso,
            )
            from well_harness.skill_executor.workbench_polling import (
                write_approval_signal,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return

        suffix = raw_path[len(SKILL_EXECUTIONS_PATH) + 1:]
        try:
            exec_id, action = suffix.rsplit("/", 1)
        except ValueError:
            self._send_json(400, {"error": "invalid_path"})
            return
        if action not in ("approve", "reject") or not exec_id:
            self._send_json(400, {"error": "invalid_action"})
            return

        # Optional body — capture actor / note for audit replay
        actor = "anonymous"
        note: str | None = None
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 0:
            if length > 50_000:
                self._send_json(400, {"error": "oversized_body"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "invalid_json"})
                return
            if isinstance(payload, dict):
                actor = str(payload.get("actor") or "anonymous")
                raw_note = payload.get("note")
                note = (
                    str(raw_note)
                    if isinstance(raw_note, str) and raw_note.strip()
                    else None
                )

        # Read current audit — must exist + be in ASKING
        try:
            record = read_audit(exec_id)
        except AuditSchemaError as exc:
            msg = str(exc).lower()
            if "not found" in msg or "invalid exec_id shape" in msg:
                self._send_json(404, {"error": "audit_not_found", "id": exec_id})
                return
            self._send_json(500, {"error": "audit_unreadable", "detail": str(exc)})
            return
        if record.state != "ASKING":
            self._send_json(
                409,
                {
                    "error": "execution_not_in_asking_state",
                    "id": exec_id,
                    "current_state": record.state,
                },
            )
            return

        # Patch the most-recent Ask entry with actor + note (the
        # CLI's polling callback will then read the approval signal,
        # write user_response back, persist the audit). Doing it
        # here lets the workbench-side click attribution survive
        # even if the CLI process crashes between read_audit and
        # the next write.
        if record.asks:
            ask = record.asks[-1]
            if ask.user_response is None:
                ask.user_actor = actor
                if note:
                    ask.note = note
                # user_response + user_responded_at are filled by
                # the CLI side after the signal is consumed; keep
                # them None here so the polling callback writes
                # the canonical timestamp.
                write_audit(record)

        # Drop the signal file the CLI's polling callback reads.
        target_audit_dir = audit_dir_resolver()
        try:
            write_approval_signal(
                audit_dir=target_audit_dir,
                exec_id=exec_id,
                response="approved" if action == "approve" else "rejected",
            )
        except OSError as exc:
            self._send_json(
                500,
                {"error": "signal_write_failed", "detail": str(exc)},
            )
            return

        self._send_json(
            202,
            {
                "exec_id": exec_id,
                "action": action,
                "signaled_at": now_iso(),
                "actor": actor,
            },
        )

    def _handle_skill_execution_cancel(self, raw_path: str) -> None:
        """POST /api/skill-executions/<exec_id>/cancel.

        Drops a cancel signal the orchestrator picks up at its next
        phase boundary. Distinct from /reject:
          - reject only works in ASKING state (rejecting a plan)
          - cancel works in any non-terminal state (PLANNING /
            ASKING / EDITING / TESTING / PR_OPEN) and signals "stop
            executing now"

        Optional JSON body: {"actor": "Kogami", "note": "..."}
        Both fields are written into the cancel-signal payload so
        the audit's abort_reason is informative.

        Returns 202 (signal queued) on success, 404 if no audit
        exists, 409 if the audit is already in a terminal state.
        """
        try:
            from well_harness.skill_executor.audit import (
                audit_dir as audit_dir_resolver,
                read_audit,
            )
            from well_harness.skill_executor.errors import AuditSchemaError
            from well_harness.skill_executor.models import now_iso
            from well_harness.skill_executor.states import (
                ExecutionState,
                is_terminal,
            )
            from well_harness.skill_executor.workbench_polling import (
                write_cancel_signal,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return

        suffix = raw_path[len(SKILL_EXECUTIONS_PATH) + 1:]
        try:
            exec_id, action = suffix.rsplit("/", 1)
        except ValueError:
            self._send_json(400, {"error": "invalid_path"})
            return
        if action != "cancel" or not exec_id:
            self._send_json(400, {"error": "invalid_action"})
            return

        actor = "anonymous"
        note: str = ""
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 0:
            if length > 50_000:
                self._send_json(400, {"error": "oversized_body"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "invalid_json"})
                return
            if isinstance(payload, dict):
                actor = str(payload.get("actor") or "anonymous")
                raw_note = payload.get("note")
                if isinstance(raw_note, str) and raw_note.strip():
                    note = raw_note.strip()

        try:
            record = read_audit(exec_id)
        except AuditSchemaError as exc:
            msg = str(exc).lower()
            if "not found" in msg or "invalid exec_id shape" in msg:
                self._send_json(404, {"error": "audit_not_found", "id": exec_id})
                return
            self._send_json(500, {"error": "audit_unreadable", "detail": str(exc)})
            return

        if is_terminal(ExecutionState(record.state)):
            self._send_json(
                409,
                {
                    "error": "execution_already_terminal",
                    "id": exec_id,
                    "current_state": record.state,
                },
            )
            return

        target_audit_dir = audit_dir_resolver()
        try:
            write_cancel_signal(
                audit_dir=target_audit_dir,
                exec_id=exec_id,
                actor=actor,
                note=note,
            )
        except OSError as exc:
            self._send_json(
                500,
                {"error": "signal_write_failed", "detail": str(exc)},
            )
            return

        self._send_json(
            202,
            {
                "exec_id": exec_id,
                "action": "cancel",
                "signaled_at": now_iso(),
                "actor": actor,
                "note": note,
                "current_state": record.state,
            },
        )

    def _handle_skill_execution_governance(self, raw_path: str) -> None:
        """POST /api/skill-executions/<exec_id>/governance-{approve,reject}.

        Bridges the workbench's governance card UI to the
        file-based IPC the orchestrator polls during
        GOVERNANCE_HOLD. Distinct from /approve and /reject:
          - /approve and /reject answer the ASKING-state plan ask
          - /governance-{approve,reject} answer the gate that
            sits between PLANNING and ASKING (P49-02a)

        Body (optional): {"actor": "...", "note": "..."}.
        Empty body still works; actor defaults to "anonymous".

        202 = signal queued. The orchestrator's poll loop picks
        it up at its next interval. 404 if no audit, 409 if the
        audit isn't in GOVERNANCE_HOLD.
        """
        try:
            from well_harness.skill_executor.audit import (
                audit_dir as audit_dir_resolver,
                read_audit,
            )
            from well_harness.skill_executor.errors import AuditSchemaError
            from well_harness.skill_executor.models import now_iso
            from well_harness.skill_executor.states import ExecutionState
            from well_harness.skill_executor.workbench_polling import (
                write_governance_approval,
                write_governance_reject,
            )
        except ImportError:
            self._send_json(500, {"error": "skill_executor_unavailable"})
            return

        suffix = raw_path[len(SKILL_EXECUTIONS_PATH) + 1:]
        try:
            exec_id, action = suffix.rsplit("/", 1)
        except ValueError:
            self._send_json(400, {"error": "invalid_path"})
            return
        if action not in ("governance-approve", "governance-reject") \
                or not exec_id:
            self._send_json(400, {"error": "invalid_action"})
            return

        actor = "anonymous"
        note: str = ""
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 0:
            if length > 50_000:
                self._send_json(400, {"error": "oversized_body"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "invalid_json"})
                return
            if isinstance(payload, dict):
                actor = str(payload.get("actor") or "anonymous")
                raw_note = payload.get("note")
                if isinstance(raw_note, str) and raw_note.strip():
                    note = raw_note.strip()

        try:
            record = read_audit(exec_id)
        except AuditSchemaError as exc:
            msg = str(exc).lower()
            if "not found" in msg or "invalid exec_id shape" in msg:
                self._send_json(
                    404, {"error": "audit_not_found", "id": exec_id},
                )
                return
            self._send_json(
                500, {"error": "audit_unreadable", "detail": str(exc)},
            )
            return

        # 409: the audit isn't paused at the gate. Trying to
        # approve/reject from any other state would be silent
        # (signal file written, never consumed) — surface the
        # state mismatch instead.
        if record.state != ExecutionState.GOVERNANCE_HOLD.value:
            self._send_json(
                409,
                {
                    "error": "not_in_governance_hold",
                    "id": exec_id,
                    "current_state": record.state,
                },
            )
            return

        target_audit_dir = audit_dir_resolver()
        writer = (
            write_governance_approval
            if action == "governance-approve"
            else write_governance_reject
        )
        try:
            writer(
                audit_dir=target_audit_dir,
                exec_id=exec_id,
                actor=actor,
                note=note,
            )
        except OSError as exc:
            self._send_json(
                500, {"error": "signal_write_failed", "detail": str(exc)},
            )
            return

        self._send_json(
            202,
            {
                "exec_id": exec_id,
                "action": action,
                "signaled_at": now_iso(),
                "actor": actor,
                "note": note,
                "current_state": record.state,
            },
        )

    def _serve_workbench_circuit_fragment(self):
        """P44-01 (2026-04-26) + P45-01 (2026-04-26): serve the SVG
        fragment that backs the /workbench page hero, parameterized by
        ?system=<id>. thrust-reverser (default) returns the L1→L4
        circuit extracted from fantui_circuit.html; other systems
        either map to their own circuit file when one exists, or
        return a clear "circuit not yet wired" placeholder SVG so the
        page still renders cleanly.

        The fragment intentionally OMITS the unified-nav header and
        the info-row / footer of the source page — /workbench wraps
        the SVG with its own engineer chrome (topbar, state-of-world
        bar, suggestion form, approval center)."""
        from urllib.parse import parse_qs as _parse_qs, urlparse as _urlparse
        parsed = _urlparse(self.path)
        system_id = (_parse_qs(parsed.query).get("system", ["thrust-reverser"])[0] or "thrust-reverser").strip()
        source_path = _CIRCUIT_SOURCE_BY_SYSTEM.get(system_id)
        if source_path is None:
            # System is recognized in the dropdown but has no circuit
            # file yet → return a placeholder SVG so the workbench
            # still renders something useful.
            self._send_bytes(
                200,
                _circuit_placeholder_fragment(system_id).encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        source = STATIC_DIR / source_path
        try:
            html = source.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            self._send_json(503, {"error": "circuit_source_unavailable", "system": system_id})
            return
        # P54-07 (2026-04-28): viewBox-agnostic SVG extraction. The
        # original P44-01 implementation hard-coded "0 0 1000 640" so
        # that C919's "0 0 1020 560" viewBox slipped through to the
        # placeholder branch. We now find the first `<svg ` tag
        # carrying a viewBox attribute, regardless of its dimensions,
        # which keeps thrust-reverser working unchanged while
        # unlocking c919-etras (and any future system that drafts a
        # circuit with its own canvas size).
        svg_match = re.search(r'<svg\s+[^>]*viewBox="[^"]+"', html)
        svg_start = svg_match.start() if svg_match else -1
        svg_end = html.find("</svg>", svg_start) if svg_start != -1 else -1
        if svg_start == -1 or svg_end == -1:
            self._send_json(503, {"error": "circuit_svg_block_not_found", "system": system_id})
            return
        fragment = html[svg_start : svg_end + len("</svg>")]
        # Sanity-check: every gate anchor declared for this system
        # must travel with the fragment, otherwise downstream
        # annotation binding silently breaks.
        for gate_id in _CIRCUIT_REQUIRED_GATES.get(system_id, ()):
            if f'data-gate-id="{gate_id}"' not in fragment:
                self._send_json(
                    503,
                    {
                        "error": "circuit_fragment_missing_gate_anchor",
                        "system": system_id,
                        "gate_id": gate_id,
                    },
                )
                return
        self._send_bytes(200, fragment.encode("utf-8"), "text/html; charset=utf-8")

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


# ─────────────────────────────────────────────────────────────────
# P44-02 (2026-04-26): rule-based interpretation of free-form
# engineer modification suggestions. Pure function, no side effects,
# no I/O, no truth-engine access — easy to unit-test independently of
# the HTTP handler.
#
# This is rule-based intentionally for the first slice: the rules are
# under git version control so behavior is deterministic and reviewable.
# A future P44-X may swap in an LLM-backed interpreter behind the same
# (text) -> dict signature.
# ─────────────────────────────────────────────────────────────────

# P46-02 (2026-04-26): per-system gate + signal vocabularies.
# Each system has its own gate ids (the P45-01 SVG fragment endpoint
# carries the matching data-gate-id="..." anchors; placeholder
# systems intentionally have no anchors so the interpreted gate
# won't glow on the SVG, but the ticket still flows). Adding a new
# system = drop entries in both _GATE_SYNONYMS_BY_SYSTEM and
# _SIGNALS_BY_SYSTEM.
#
# thrust-reverser carries the canonical L1..L4 vocabulary (was
# _GATE_SYNONYMS in P44-02; preserved here verbatim so all P44
# tests keep passing). The other three systems get small but
# domain-honest tables — placeholder SVGs from P45-01 carry no
# gate anchors yet, so the interpretation here populates the
# ticket payload + dev-queue brief but won't drive panel glow
# until those systems' real circuits are drafted.
_GATE_SYNONYMS_BY_SYSTEM: dict[str, dict[str, tuple[str, ...]]] = {
    "thrust-reverser": {
        "L1": ("L1", "l1", "逻辑门 1", "门 1", "tls_115vac_cmd", "TLS"),
        "L2": ("L2", "l2", "逻辑门 2", "门 2", "etrac_540vdc_cmd", "ETRAC"),
        "L3": ("L3", "l3", "逻辑门 3", "门 3", "eec_deploy_cmd", "pls_power_cmd", "pdu_motor_cmd", "EEC"),
        "L4": ("L4", "l4", "逻辑门 4", "门 4", "throttle_electronic_lock_release_cmd", "throttle_unlock"),
    },
    # FROZEN 2026-04-26 (landing-gear): kept for architectural demo
    # of the per-system vocabulary. Not exposed in the dropdown.
    "landing-gear": {
        "G1": ("G1", "g1", "主起放下", "主起落架放下", "main_gear_down_cmd", "MLG down"),
        "G2": ("G2", "g2", "主起收上", "主起落架收上", "main_gear_up_cmd", "MLG up"),
        "G3": ("G3", "g3", "前起放下", "前起落架放下", "nose_gear_down_cmd", "NLG down"),
        "G4": ("G4", "g4", "前起收上", "前起落架收上", "nose_gear_up_cmd", "NLG up"),
    },
    # FROZEN 2026-04-26 (bleed-air-valve): same as landing-gear above.
    "bleed-air-valve": {
        "V1": ("V1", "v1", "引气阀开启", "bleed_open_cmd", "bleed open", "PRSOV open"),
        "V2": ("V2", "v2", "引气阀关闭", "bleed_close_cmd", "bleed close", "PRSOV close"),
    },
    "c919-etras": {
        "E1": ("E1", "e1", "E-TRAS 解锁", "etras_unlock_cmd", "ETRAS unlock"),
        "E2": ("E2", "e2", "E-TRAS 部署", "etras_deploy_cmd", "ETRAS deploy"),
        "E3": ("E3", "e3", "E-TRAS 收回", "etras_stow_cmd", "ETRAS stow"),
    },
}

_SIGNALS_BY_SYSTEM: dict[str, tuple[str, ...]] = {
    "thrust-reverser": (
        "radio_altitude_ft",
        "SW1",
        "SW2",
        "reverser_inhibited",
        "reverser_not_deployed_eec",
        "engine_running",
        "aircraft_on_ground",
        "eec_enable",
        "tls_unlocked_ls",
        "n1k",
        "tra_deg",
        "deploy_90_percent_vdt",
    ),
    "landing-gear": (
        "wow", "weight_on_wheels",
        "gear_handle_position",
        "gear_door_position",
        "main_gear_lock_uplock",
        "main_gear_lock_downlock",
        "nose_gear_lock_uplock",
        "nose_gear_lock_downlock",
        "hyd_pressure_psi",
    ),
    "bleed-air-valve": (
        "bleed_pressure_psi",
        "bleed_temp_c",
        "engine_n2_pct",
        "apu_running",
        "anti_ice_on",
    ),
    "c919-etras": (
        "tra_deg", "throttle_electronic_lock_release_cmd",
        "etras_deploy_position_pct",
        "weight_on_wheels", "wow",
        "engine_running",
        "fadec_deploy_enable",
    ),
}


def _gate_synonyms_for(system_id: str) -> dict[str, tuple[str, ...]]:
    """Lookup with safe fallback — unknown system_ids resolve to the
    thrust-reverser table so the rules path never returns an empty
    vocabulary by accident."""
    return _GATE_SYNONYMS_BY_SYSTEM.get(system_id) or _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"]


def _signals_for(system_id: str) -> tuple[str, ...]:
    return _SIGNALS_BY_SYSTEM.get(system_id) or _SIGNALS_BY_SYSTEM["thrust-reverser"]


# Back-compat alias: a handful of P44/P45 tests still import
# _GATE_SYNONYMS / _KNOWN_TARGET_SIGNALS by name. Point both at the
# thrust-reverser entries so those tests keep passing without a
# rewrite. New code should use the per-system helpers above.
_GATE_SYNONYMS = _GATE_SYNONYMS_BY_SYSTEM["thrust-reverser"]
_KNOWN_TARGET_SIGNALS = _SIGNALS_BY_SYSTEM["thrust-reverser"]

# Verb-style hints that the engineer is proposing a change and what
# kind of change. Order matters — first match wins. Specific verbs
# (loosen / tighten / add / remove / tune) come BEFORE the generic
# `modify_condition` so phrases like "should be loosen for X" classify
# as loosen rather than modify.
_CHANGE_KIND_HINTS: tuple[tuple[str, str, str, str], ...] = (
    # (regex pattern, change_kind code, zh label, en label)
    (r"(放宽|放松|loosen|relax)", "loosen_condition", "放宽判据", "loosen condition"),
    (r"(收紧|加严|tighten|stricter|更严格)", "tighten_condition", "收紧判据", "tighten condition"),
    (r"(去掉|删除|移除|不再需要|drop|remove|delete|eliminate)", "remove_condition", "删除判据", "remove condition"),
    (r"(增加|加上|新增|添加|add|introduce|include)", "add_condition", "新增判据", "add condition"),
    (r"(调整|微调|tune|adjust|tweak)", "tune_condition", "调整判据", "tune condition"),
    (r"(应该改成|应改成|改成|应改为|改为|update|change to|set to|should be)", "modify_condition", "修改判据", "modify condition"),
    (r"(建议|suggest|propose|recommend)", "propose_change", "提出建议", "propose change"),
)


# P54-09 (2026-04-28): per-component breakdown + vocab hints.
# Extracted so the LLM normalizer can reuse them. Both helpers are
# pure functions over the canonical interpretation fields plus the
# active system_id (for per-system vocab tables).
def _confidence_breakdown_from_fields(
    affected_gates: list[str],
    target_signals: list[str],
    change_kind: str,
) -> dict[str, float]:
    return {
        "gate": 1.0 if affected_gates else 0.0,
        "signal": 1.0 if target_signals else 0.0,
        "change_kind": 1.0 if change_kind != "propose_change" else 0.0,
    }


def _vocabulary_hint_from_fields(
    affected_gates: list[str],
    target_signals: list[str],
    change_kind: str,
    system_id: str,
) -> dict[str, list[str]]:
    """Surface canonical vocab lists for any dimension that came up
    empty. Engineer rephrasing then has concrete words to try.
    Synonyms are intentionally NOT exposed — they're noisy and the
    canonical id (e.g. L1) is enough to anchor a rephrasing.
    """
    gate_vocab = _gate_synonyms_for(system_id)
    signal_vocab = _signals_for(system_id)
    hint: dict[str, list[str]] = {}
    if not affected_gates:
        hint["gate"] = list(gate_vocab.keys())
    if not target_signals:
        hint["signal"] = list(signal_vocab)
    if change_kind == "propose_change":
        # _CHANGE_KIND_HINTS tuple = (pattern, code, zh, en).
        # Filter on the code (index 1) — index 2 is the Chinese label,
        # so the prior implementation accidentally always included the
        # fallback "propose change" entry in the hint list, which
        # advertised the very degenerate verb that triggered the hint
        # (Codex P54-09 round-1 P3).
        hint["change_kind"] = sorted(
            {h[3] for h in _CHANGE_KIND_HINTS if h[1] != "propose_change"}
        )
    return hint


def interpret_suggestion_text(text: str, *, system_id: str = "thrust-reverser") -> dict:
    """Rule-based interpretation of an engineer modification suggestion.

    Returns a dict with the contract:
      - affected_gates: list[str]   gate ids drawn from the active
                                    system's vocabulary (L1..L4 for
                                    thrust-reverser, G1..G4 for
                                    landing-gear, etc.)
      - target_signals: list[str]   recognized input/output signal names
      - change_kind:    str         machine code, e.g. "modify_condition"
      - change_kind_zh: str         human label in Chinese
      - change_kind_en: str         human label in English
      - confidence:     float       in [0.0, 1.0] — heuristic
      - summary_zh:     str         system restatement in Chinese
      - summary_en:     str         system restatement in English
      - source_text:    str         echo of the input (for audit)

    P46-02: optional system_id selects per-system gate + signal
    vocabularies. Defaults to "thrust-reverser" so every existing
    caller (including all P44 tests) keeps working unchanged.
    Unknown system_ids fall back to the thrust-reverser table.

    The function is intentionally conservative: when no gate is
    detected, affected_gates is empty and confidence is low. The UI
    should still render the result and let the engineer either confirm
    (keeping the loose interpretation) or rewrite the suggestion.
    """
    import re

    if not isinstance(text, str):
        text = ""

    gate_vocab = _gate_synonyms_for(system_id)
    signal_vocab = _signals_for(system_id)

    # 1. Gate detection. Each gate id can match by its synonym list;
    #    we record gates in the order they appear in the vocab dict
    #    (Python 3.7+ preserves insertion order, which is the
    #    declared canonical order per system).
    affected_gates: list[str] = []
    for gate_id, synonyms in gate_vocab.items():
        for synonym in synonyms:
            if synonym in text:
                affected_gates.append(gate_id)
                break

    # 2. Target signal detection.
    target_signals: list[str] = []
    for signal in signal_vocab:
        if signal in text:
            target_signals.append(signal)

    # 3. Change kind detection. First match wins; falls back to
    #    "propose_change" so we always have a label.
    change_kind = "propose_change"
    change_kind_zh = "提出建议"
    change_kind_en = "propose change"
    for pattern, code, zh, en in _CHANGE_KIND_HINTS:
        if re.search(pattern, text, re.IGNORECASE):
            change_kind = code
            change_kind_zh = zh
            change_kind_en = en
            break

    # 4. Confidence heuristic. We weight gate detection most heavily
    #    (the panel highlight is only useful if we know which gate),
    #    then signal detection, then having an explicit change verb.
    confidence = 0.0
    if affected_gates:
        confidence += 0.5
    if target_signals:
        confidence += 0.3
    if change_kind != "propose_change":
        confidence += 0.2
    confidence = min(1.0, confidence)

    # P54-09 (2026-04-28): per-component confidence breakdown so the UI
    # can show three small bars (gate / signal / change-kind) instead
    # of a single opaque number, and surface "vocabulary hints" when a
    # dimension came up empty so the engineer knows how to rephrase
    # rather than guessing what the rules want.
    confidence_breakdown = _confidence_breakdown_from_fields(
        affected_gates, target_signals, change_kind
    )
    vocabulary_hint = _vocabulary_hint_from_fields(
        affected_gates, target_signals, change_kind, system_id
    )

    # 5. Summary restatement.
    gates_label = "、".join(affected_gates) if affected_gates else "(未识别)"
    signals_label = "、".join(target_signals) if target_signals else "(未识别)"
    summary_zh = (
        f"系统理解：你想在 {gates_label} 上对 {signals_label} 执行 "
        f"{change_kind_zh}（confidence={int(confidence * 100)}%）。"
    )
    gates_label_en = ", ".join(affected_gates) if affected_gates else "(none)"
    signals_label_en = ", ".join(target_signals) if target_signals else "(none)"
    summary_en = (
        f"System reading: you propose to {change_kind_en} on gate(s) "
        f"{gates_label_en}, target signal(s) {signals_label_en} "
        f"(confidence={int(confidence * 100)}%)."
    )

    return {
        "affected_gates": affected_gates,
        "target_signals": target_signals,
        "change_kind": change_kind,
        "change_kind_zh": change_kind_zh,
        "change_kind_en": change_kind_en,
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
        "vocabulary_hint": vocabulary_hint,
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "source_text": text,
    }


# ─────────────────────────────────────────────────────────────────
# P45-03 (2026-04-26): LLM-backed interpretation via MiniMax-M2.7.
# Same (text, system_id) → dict signature as the rules interpreter,
# so callers can swap strategies without touching downstream wiring.
# On any failure (no API key, network timeout, malformed response)
# the function falls back to the rules interpreter and tags the
# result with interpreter_strategy="llm_fallback_to_rules".
#
# Uses urllib.request from the stdlib so the workbench keeps zero
# pip dependencies. The LLM call is fully bounded: 30s timeout,
# narrow JSON schema, strict normalization.
# ─────────────────────────────────────────────────────────────────

MINIMAX_API_BASE = "https://api.minimaxi.com/v1"
MINIMAX_DEFAULT_MODEL = "MiniMax-M2.7-highspeed"
# MiniMax-M2.7-highspeed is a reasoning model: it emits a
# <think>...</think> block before the JSON answer and the
# reasoning portion can run 20-40s on prompts with multiple
# constraints. 60s leaves headroom so real engineer-typed
# suggestions don't trip the urllib timeout and quietly fall
# back to rules. The fallback semantics still apply if the call
# runs over — the engineer sees an amber "fell back to rules"
# badge instead of an error.
MINIMAX_REQUEST_TIMEOUT_SEC = 60.0


def _resolve_minimax_api_key() -> str | None:
    """Try several names for the MiniMax key in this order:
      1. MINIMAX_API_KEY env (the canonical name from the user's
         minimix.py wrapper)
      2. Minimax_API_key env (the actual variable name in the user's
         ~/.zshrc — preserve the exact case)
      3. ~/.minimax_key file (the fallback the user's wrapper reads
         when env is unset)
    Returns the trimmed key or None if no source has it."""
    for env_name in ("MINIMAX_API_KEY", "Minimax_API_key"):
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()
    fallback = Path(os.path.expanduser("~/.minimax_key"))
    try:
        if fallback.is_file():
            text = fallback.read_text(encoding="utf-8").strip()
            if text:
                return text
    except OSError:
        pass
    return None


def _llm_interpret_prompt(text: str, system_id: str) -> str:
    """Build the strict-JSON prompt the LLM must respond to. Naming
    the schema fields explicitly + asking for JSON-only output keeps
    the parse step trivial and the cost low.

    Codex P54-09 round-6 P1: the canonical vocabularies (gates +
    signals + change_kinds) are now read from the rules tables so
    the prompt and the post-LLM canonicalizer can never drift. The
    earlier hardcoded list said `tune_threshold`, `RA`, `TRA`,
    `SW3`, `tls_115vac_cmd` — none of which exist in the rules
    vocab — so a prompt-compliant LLM response was being filtered
    to empty by the canonicalizer. Now the prompt itself enumerates
    the very ids the canonicalizer accepts.
    """
    gate_ids = list(_gate_synonyms_for(system_id).keys())
    signals = list(_signals_for(system_id))
    change_kind_codes = [h[1] for h in _CHANGE_KIND_HINTS]
    # Codex round-7 P1: the schema example values must be drawn
    # from the active system_id's canonical vocab. The previous
    # version hardcoded "L1"/"SW1" — both thrust-reverser-specific.
    # MiniMax tends to copy literal example values, so a C919
    # request would return ["L1"]/["SW1"] and the canonicalizer
    # would strip them, leaving the engineer with a 0% result on
    # an otherwise-valid suggestion.
    gate_example = gate_ids[0] if gate_ids else "L1"
    signal_example = signals[0] if signals else "SW1"
    return (
        "你是 AI FANTUI 控制逻辑工作台的解读助手。\n"
        "工程师写下了对当前控制逻辑的修改建议；你的任务是把这段自然语言"
        "解读为结构化 JSON，让工作台能在 SVG 面板上高亮命中的逻辑门，并请"
        "工程师确认。\n\n"
        f"当前系统 system_id: {system_id}\n"
        f"已知逻辑门 ({system_id}): {', '.join(gate_ids) or '(暂无)'}。"
        "如果建议跨系统或没有命中任何门，affected_gates 可返回 []。\n"
        f"已知信号: {', '.join(signals) or '(暂无)'}。\n"
        f"已知 change_kind 取值（必须严格使用其中之一）: "
        f"{', '.join(change_kind_codes)}。\n\n"
        f'工程师的建议原文:\n"""{text}"""\n\n'
        "请只输出 JSON（不要 markdown 围栏、不要解释），字段精确匹配下表:\n"
        "{\n"
        f'  "affected_gates":   ["{gate_example}"|...],   // 命中的逻辑门 id 列表\n'
        f'  "target_signals":   ["{signal_example}"|...],  // 命中的信号名列表\n'
        '  "change_kind":      "tighten_condition"|...,\n'
        '  "change_kind_zh":   "收紧判据"|...,\n'
        '  "change_kind_en":   "tighten condition"|...,\n'
        '  "confidence":       0.0..1.0,\n'
        '  "summary_zh":       "中文一句话重述工程师的意图",\n'
        '  "summary_en":       "English one-sentence restatement"\n'
        "}\n"
    )


def _strip_json_fences(raw: str) -> str:
    """LLMs sometimes wrap JSON in ```json ... ``` even when told not
    to. Reasoning-style models (MiniMax-M2.7-highspeed) also emit a
    `<think>...</think>` block BEFORE the answer. Strip both so the
    JSON parser sees only the structured payload."""
    text = raw.strip()
    # Drop reasoning blocks. There can be more than one — peel each
    # `<think>...</think>` pair greedily.
    while True:
        start = text.find("<think>")
        if start < 0:
            break
        end = text.find("</think>", start)
        if end < 0:
            # Unterminated — drop everything from <think> onward as a
            # last-ditch recovery, then bail out of the loop.
            text = text[:start]
            break
        text = (text[:start] + text[end + len("</think>"):]).strip()
    if text.startswith("```"):
        # Drop opening fence (with optional language tag) + closing fence.
        text = text.split("```", 1)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _normalize_llm_interpretation(
    raw_dict: dict,
    source_text: str,
    *,
    system_id: str = "thrust-reverser",
) -> dict:
    """Coerce the LLM's response into the canonical schema +
    enforce types. Missing fields fall back to safe defaults so
    the UI never sees an undefined.

    P54-09 (2026-04-28): system_id is required to synthesize
    vocabulary_hint when the LLM misses a dimension — without it,
    AI-mode users would see breakdown bars at 0% with no rephrasing
    guidance, breaking the trust-flow promise (Codex round-1 P2).
    Defaults to thrust-reverser so existing tests remain
    backwards-compatible.
    """
    def _str_list(value) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if isinstance(item, (str, int))]
    confidence = raw_dict.get("confidence", 0.5)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.5
    affected_gates = _str_list(raw_dict.get("affected_gates"))
    target_signals = _str_list(raw_dict.get("target_signals"))
    change_kind = str(raw_dict.get("change_kind") or "propose_change")
    # Codex round-4 P2-1 + round-9 P2-1: canonicalize against the
    # per-system vocab. Drop true hallucinations ("L99", "BOGUS")
    # but RESOLVE synonyms (e.g. "TLS" → "L1", "逻辑门 1" → "L1",
    # "l1" → "L1") through the gate synonym table — otherwise an
    # LLM that emitted a valid alias would be reduced to [] even
    # though the rules interpreter would have accepted it.
    gate_vocab = _gate_synonyms_for(system_id)
    signal_vocab = _signals_for(system_id)
    # Build a synonym → canonical-id reverse index; canonical ids
    # are also their own synonym so the lookup is uniform.
    gate_alias_index: dict[str, str] = {}
    for canonical, syns in gate_vocab.items():
        gate_alias_index[canonical] = canonical
        for s in syns:
            gate_alias_index.setdefault(s, canonical)
    resolved_gates: list[str] = []
    seen: set[str] = set()
    for raw_g in affected_gates:
        canonical = gate_alias_index.get(raw_g)
        if canonical and canonical not in seen:
            resolved_gates.append(canonical)
            seen.add(canonical)
    affected_gates = resolved_gates
    # Signal vocab is a flat tuple of canonical names; keep strict
    # equality (synonyms aren't defined for signals in this repo).
    target_signals = [s for s in target_signals if s in signal_vocab]
    valid_change_kinds = {h[1] for h in _CHANGE_KIND_HINTS}
    raw_zh = str(raw_dict.get("change_kind_zh") or "提出建议")
    raw_en = str(raw_dict.get("change_kind_en") or "propose change")
    if change_kind not in valid_change_kinds:
        # Codex round-5 P2-2: when we coerce an out-of-taxonomy
        # change_kind to propose_change, the human-readable labels
        # must also reset to the fallback's labels — otherwise the
        # UI displays "tighten condition" while the stored code is
        # "propose_change", and downstream commit messages /
        # executor brief carry the contradictory pair.
        change_kind = "propose_change"
        raw_zh = "提出建议"
        raw_en = "propose change"
    # Codex round-6 P2: cap the LLM-reported overall confidence by
    # what the *canonicalized* fields actually warrant. Otherwise an
    # LLM that emitted ["L99"] (now filtered to []) and confidence=0.9
    # would still display 90% with the breakdown bars all at 0% —
    # contradicting the trust-flow UI's whole point. Use the same
    # weights the rules interpreter uses (0.5 / 0.3 / 0.2) so both
    # paths converge on the same scale.
    canonical_max = (
        (0.5 if affected_gates else 0.0)
        + (0.3 if target_signals else 0.0)
        + (0.2 if change_kind != "propose_change" else 0.0)
    )
    confidence = min(confidence, canonical_max)
    # Codex round-8 P2: if canonicalization actually changed anything
    # (filtered out hallucinated ids, coerced an unknown change_kind),
    # the LLM's summary text still describes the pre-sanitize world
    # ("…在 L99 上对 SW3 执行 tune_threshold…"). Persisting that into
    # the proposal store means /skill_executor decompose() also sees
    # the misleading sentence. Regenerate the summaries from the
    # canonicalized fields whenever the LLM-reported lists differ
    # from the post-canonical lists; otherwise keep the LLM's text
    # (it's typically richer than the rules template).
    raw_gates_in = _str_list(raw_dict.get("affected_gates"))
    raw_signals_in = _str_list(raw_dict.get("target_signals"))
    raw_kind_in = str(raw_dict.get("change_kind") or "propose_change")
    canonicalized = (
        raw_gates_in != affected_gates
        or raw_signals_in != target_signals
        or raw_kind_in != change_kind
    )
    if canonicalized:
        gates_label = "、".join(affected_gates) if affected_gates else "(未识别)"
        signals_label = "、".join(target_signals) if target_signals else "(未识别)"
        summary_zh = (
            f"系统理解：你想在 {gates_label} 上对 {signals_label} 执行 "
            f"{raw_zh}（confidence={int(confidence * 100)}%）。"
        )
        gates_label_en = ", ".join(affected_gates) if affected_gates else "(none)"
        signals_label_en = ", ".join(target_signals) if target_signals else "(none)"
        summary_en = (
            f"System reading: you propose to {raw_en} on gate(s) "
            f"{gates_label_en}, target signal(s) {signals_label_en} "
            f"(confidence={int(confidence * 100)}%)."
        )
    else:
        summary_zh = str(raw_dict.get("summary_zh") or "")
        summary_en = str(raw_dict.get("summary_en") or "")
    return {
        "affected_gates": affected_gates,
        "target_signals": target_signals,
        "change_kind": change_kind,
        "change_kind_zh": raw_zh,
        "change_kind_en": raw_en,
        "confidence": confidence,
        "confidence_breakdown": _confidence_breakdown_from_fields(
            affected_gates, target_signals, change_kind
        ),
        "vocabulary_hint": _vocabulary_hint_from_fields(
            affected_gates, target_signals, change_kind, system_id
        ),
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "source_text": source_text,
    }


def _call_minimax_chat_completion(prompt: str, *, api_key: str, model: str) -> str:
    """One-shot POST to MiniMax chat/completions. Returns the raw
    assistant content string. Raises urllib.error.URLError or
    ValueError on transport / parse failure — caller wraps both."""
    import urllib.request as _urlreq
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            # MiniMax-M2.7-highspeed is a reasoning model — its
            # <think>...</think> block can eat ~500 tokens before it
            # writes a single character of the answer. 4096 leaves
            # comfortable headroom for both the reasoning and the
            # ~200-token JSON payload.
            "max_tokens": 4096,
        }
    ).encode("utf-8")
    request = _urlreq.Request(
        f"{MINIMAX_API_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with _urlreq.urlopen(request, timeout=MINIMAX_REQUEST_TIMEOUT_SEC) as response:
        raw = response.read().decode("utf-8")
    parsed = json.loads(raw)
    choices = parsed.get("choices") or []
    if not choices:
        raise ValueError("llm_response_missing_choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("llm_response_missing_content")
    return content


def interpret_suggestion_text_llm(
    text: str,
    *,
    system_id: str = "thrust-reverser",
    model: str | None = None,
) -> dict:
    """LLM-backed counterpart to interpret_suggestion_text. Returns
    the same canonical schema PLUS:
      interpreter_strategy: "llm" | "llm_fallback_to_rules"
      llm_model:            the model name actually used (when llm)
      llm_error:            the failure reason (when fallback)
    On any failure the rules interpreter is invoked so the engineer
    always gets SOME interpretation."""
    api_key = _resolve_minimax_api_key()
    if not api_key:
        fallback = interpret_suggestion_text(text)
        fallback["interpreter_strategy"] = "llm_fallback_to_rules"
        fallback["llm_error"] = "missing_api_key"
        return fallback
    chosen_model = model or MINIMAX_DEFAULT_MODEL
    prompt = _llm_interpret_prompt(text, system_id)
    try:
        raw_content = _call_minimax_chat_completion(
            prompt, api_key=api_key, model=chosen_model,
        )
        cleaned = _strip_json_fences(raw_content)
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ValueError("llm_response_not_object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # Catches urllib.error.URLError (subclass of OSError),
        # timeouts, JSON parse errors, and our own ValueError raises.
        fallback = interpret_suggestion_text(text)
        fallback["interpreter_strategy"] = "llm_fallback_to_rules"
        fallback["llm_error"] = type(exc).__name__ + ": " + str(exc)[:200]
        return fallback
    result = _normalize_llm_interpretation(parsed, source_text=text, system_id=system_id)
    result["interpreter_strategy"] = "llm"
    result["llm_model"] = chosen_model
    return result


# ─────────────────────────────────────────────────────────────────
# P44-03 (2026-04-26): change-proposal persistence.
# Adapter-only store under .planning/proposals/{PROP-...}.json. One
# JSON file per proposal so git diffs are readable per-ticket and a
# proposal can be rolled back with a single `git revert`.
# Tests override the directory via the WORKBENCH_PROPOSALS_DIR env var.
# ─────────────────────────────────────────────────────────────────

_PROPOSALS_LOCK = threading.Lock()


def proposals_dir() -> Path:
    """Return the directory the proposal store writes to. Tests override
    via the WORKBENCH_PROPOSALS_DIR environment variable; production
    falls back to <repo>/.planning/proposals/. The directory is created
    on first call (parents=True, exist_ok=True)."""
    override = os.environ.get("WORKBENCH_PROPOSALS_DIR")
    if override:
        path = Path(override).expanduser()
    else:
        path = Path(__file__).resolve().parents[2] / ".planning" / "proposals"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _new_proposal_id() -> str:
    """Stable, sortable proposal id: PROP-YYYYMMDDTHHMMSSffffff-<6-hex>.
    Microsecond resolution keeps filename sort = creation order even when
    the same caller submits several proposals back-to-back."""
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    suffix = secrets.token_hex(3)
    return f"PROP-{now}-{suffix}"


def create_proposal(
    *,
    source_text: str,
    interpretation: dict,
    author_name: str = "anonymous",
    author_role: str = "ENGINEER",
    ticket_id: str = "ad-hoc",
    system_id: str = "thrust-reverser",
    kind: str = "modify",
    revert_of_proposal_id: str | None = None,
    revert_target_sha: str | None = None,
) -> dict:
    """Persist a new proposal record. Returns the record (with the
    server-assigned id, created_at, status="OPEN", and history seeded
    with a single 'submitted' entry). Thread-safe.

    Schema (locked by tests/test_workbench_p44_03_proposals.py +
    tests/test_workbench_p47_02_revert_proposals.py):
      id              str    PROP-YYYYMMDDTHHMMSS-{6-hex}
      created_at      str    ISO-8601 UTC, with 'Z' suffix
      status          str    one of: OPEN | ACCEPTED | REJECTED
      author_name     str
      author_role     str
      ticket_id       str
      system_id       str
      source_text     str    the engineer's original suggestion text
      interpretation  dict   the structured interpretation the engineer
                             confirmed (mirrors interpret_suggestion_text
                             output)
      history         list   [{at, actor, action, [note]}, ...] —
                             append-only audit trail
      kind            str    P47-02: "modify" (default) | "revert"
      revert_of_proposal_id  str | None  set when kind="revert" — the
                             id of the original proposal being reverted
      revert_target_sha      str | None  set when kind="revert" — the
                             truth-engine commit SHA being reverted
                             (i.e. the original proposal's
                             landed_truth_sha, which the skill will
                             treat as the diff to undo)
      landed_truth_sha       str | None  set by /landed endpoint when
                             the executor merges the truth-engine PR
                             that fulfills this proposal
    """
    if kind not in ("modify", "revert"):
        raise ValueError(f"invalid kind: {kind!r}")
    if kind == "revert":
        if not revert_of_proposal_id:
            raise ValueError("revert proposals require revert_of_proposal_id")
        if not revert_target_sha:
            raise ValueError("revert proposals require revert_target_sha")
    record = {
        "id": _new_proposal_id(),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "OPEN",
        "author_name": author_name,
        "author_role": author_role,
        "ticket_id": ticket_id,
        "system_id": system_id,
        "source_text": source_text,
        "interpretation": interpretation,
        "kind": kind,
        "revert_of_proposal_id": revert_of_proposal_id,
        "revert_target_sha": revert_target_sha,
        "landed_truth_sha": None,
        "history": [
            {
                "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "actor": author_name,
                "action": "submitted",
            }
        ],
    }
    with _PROPOSALS_LOCK:
        target = proposals_dir() / f"{record['id']}.json"
        target.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return record


# ─── P47-02 (2026-04-27): revert-as-proposal + landed-SHA tracking ──
#
# After the executor (Claude Code skill) merges a truth-engine PR that
# fulfills an accepted proposal, the skill calls
# `POST /api/proposals/<id>/landed { sha }` to record the merge SHA on
# the proposal record. Once recorded, the inbox card surfaces a
# "propose revert" button: clicking it calls
# `POST /api/proposals/<id>/propose-revert`, which creates a NEW
# proposal with kind="revert" + revert_target_sha=<the landed SHA>.
# That revert proposal goes through the standard accept-flow and
# produces a dev-queue brief telling the executor "treat the file
# contents at <parent-sha> as the target ground truth" — handing the
# user Q2(b) semantics: skill plans/asks/edits, doesn't blindly run
# `git revert`.


def record_proposal_landed(
    proposal_id: str,
    *,
    sha: str,
    actor: str = "claude-code-executor",
) -> tuple[dict | None, str | None]:
    """Record the truth-engine commit SHA that fulfills this proposal.
    Called by the skill after PR merge. Returns (record, error_code).
    error_code: None | "not_found" | "invalid_sha" | "wrong_status"
    | "already_landed".

    SHA validation is loose on purpose — accepts 7-40 hex chars so
    both short and full SHAs work. Tighter validation belongs in the
    skill.
    """
    if not sha or not isinstance(sha, str):
        return None, "invalid_sha"
    sha = sha.strip().lower()
    if not re.match(r"^[0-9a-f]{7,40}$", sha):
        return None, "invalid_sha"
    with _PROPOSALS_LOCK:
        record = _load_proposal_record(proposal_id)
        if record is None:
            return None, "not_found"
        if record.get("status") != "ACCEPTED":
            return record, "wrong_status"
        if record.get("landed_truth_sha"):
            # Idempotent guard — re-recording the same SHA is a no-op,
            # but trying to overwrite with a different SHA is rejected.
            if record["landed_truth_sha"].lower() == sha:
                return record, None
            return record, "already_landed"
        record["landed_truth_sha"] = sha
        record.setdefault("history", []).append(
            {
                "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "actor": actor or "claude-code-executor",
                "action": "landed",
                "note": f"truth-engine commit {sha}",
            }
        )
        _write_proposal_record(record)
    return record, None


def create_revert_proposal(
    original_proposal_id: str,
    *,
    author_name: str = "anonymous",
    author_role: str = "REVIEWER",
) -> tuple[dict | None, str | None]:
    """Create a new proposal that proposes reverting the truth-engine
    commit landed for `original_proposal_id`. Returns (record, error).
    error: None | "not_found" | "not_landed" | "already_reverted".

    Validation:
      - original must exist
      - original must be ACCEPTED with a landed_truth_sha
      - no prior revert proposal already targeting the same SHA may
        be OPEN or ACCEPTED (avoid duplicate revert work)

    The new revert proposal carries:
      - kind = "revert"
      - revert_of_proposal_id = <original id>
      - revert_target_sha     = <original.landed_truth_sha>
      - source_text = "Propose revert of PROP-XXX (commit SHA)"
      - interpretation = passthrough copy of the original's
        interpretation, with summary fields prefixed "[REVERT] ..." so
        the inbox card reads sensibly.
    """
    with _PROPOSALS_LOCK:
        original = _load_proposal_record(original_proposal_id)
        if original is None:
            return None, "not_found"
        if original.get("status") != "ACCEPTED":
            return None, "not_landed"
        target_sha = original.get("landed_truth_sha")
        if not target_sha:
            return None, "not_landed"
        # Guard: refuse to create a duplicate revert. Walk the proposals
        # directory looking for any open / accepted revert proposal with
        # the same revert_target_sha.
        for path in proposals_dir().glob("PROP-*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            if data.get("kind") != "revert":
                continue
            if data.get("revert_target_sha") != target_sha:
                continue
            if data.get("status") in ("OPEN", "ACCEPTED"):
                return None, "already_reverted"
    # Build the revert record OUTSIDE the lock — create_proposal
    # acquires the lock itself.
    orig_interp = original.get("interpretation") or {}
    revert_interp = {
        **orig_interp,
        "summary_zh": f"[REVERT] 撤销 {original_proposal_id} 的修改 · {orig_interp.get('summary_zh', '')}".strip(),
        "summary_en": f"[REVERT] undo {original_proposal_id} · {orig_interp.get('summary_en', '')}".strip(),
        "change_kind": "revert",
    }
    source_text = (
        f"Propose revert of {original_proposal_id} (truth-engine commit {target_sha}).\n"
        f"Original engineer suggestion was:\n"
        f"> {original.get('source_text', '').strip() or '(empty)'}"
    )
    record = create_proposal(
        source_text=source_text,
        interpretation=revert_interp,
        author_name=author_name,
        author_role=author_role,
        ticket_id=original.get("ticket_id", "ad-hoc"),
        system_id=original.get("system_id", "thrust-reverser"),
        kind="revert",
        revert_of_proposal_id=original_proposal_id,
        revert_target_sha=target_sha,
    )
    return record, None


def list_proposals(
    *,
    status_filter: str | None = None,
    system_filter: str | None = None,
) -> list[dict]:
    """Return all stored proposal records, newest first. Optional
    filters narrow the result set:
      status_filter:  e.g. 'OPEN'             — only that status
      system_filter:  e.g. 'thrust-reverser'  — only that system
    Bad / unreadable files are skipped silently; the directory is
    the truth, no in-memory cache."""
    records: list[dict] = []
    for path in sorted(proposals_dir().glob("PROP-*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if status_filter and data.get("status") != status_filter:
            continue
        if system_filter and data.get("system_id") != system_filter:
            continue
        records.append(data)
    return records


# ─── P44-05 (2026-04-26): accept / reject + dev-queue handoff ───────
#
# Reviewer-side mutations on a proposal. Two transitions only:
#     OPEN → ACCEPTED   ... + writes a dev-queue brief for Claude Code
#     OPEN → REJECTED   ... no dev-queue side-effect
# Re-accepting / re-rejecting an already-terminal proposal is rejected
# with a 409. Truth-engine red line preserved: this only mutates the
# proposal JSON + writes a markdown brief under .planning/dev_queue/;
# the actual code change still goes through Claude Code's normal
# /gsd-execute-phase workflow + git PR review.

DEV_QUEUE_BRIEF_VERSION = 1


def dev_queue_dir() -> Path:
    """Mirrors proposals_dir() but for the dev-queue handoff briefs.
    Tests override via WORKBENCH_DEV_QUEUE_DIR; production falls back
    to <repo>/.planning/dev_queue/. The directory is created on first
    call (parents=True, exist_ok=True)."""
    override = os.environ.get("WORKBENCH_DEV_QUEUE_DIR")
    if override:
        path = Path(override).expanduser()
    else:
        path = Path(__file__).resolve().parents[2] / ".planning" / "dev_queue"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_proposal_record(proposal_id: str) -> dict | None:
    """Read a single proposal record by id, or None if not found / bad
    JSON. Caller must hold _PROPOSALS_LOCK if mutating afterwards."""
    target = proposals_dir() / f"{proposal_id}.json"
    if not target.is_file():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _write_proposal_record(record: dict) -> None:
    """Persist the proposal back to disk (overwrite). Caller MUST hold
    _PROPOSALS_LOCK so concurrent reviewers don't race the audit
    trail."""
    target = proposals_dir() / f"{record['id']}.json"
    target.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_proposal_status(
    proposal_id: str,
    *,
    new_status: str,
    actor: str,
    note: str | None = None,
) -> tuple[dict | None, str | None]:
    """Transition a proposal's status. Returns (record, error_code).
    error_code is one of: None, "not_found", "invalid_status",
    "already_terminal". Allowed transitions: OPEN → ACCEPTED |
    REJECTED. Any history entry written includes actor + optional
    free-form note (e.g. rejection reason)."""
    if new_status not in ("ACCEPTED", "REJECTED"):
        return None, "invalid_status"
    with _PROPOSALS_LOCK:
        record = _load_proposal_record(proposal_id)
        if record is None:
            return None, "not_found"
        current = record.get("status")
        if current != "OPEN":
            return record, "already_terminal"
        record["status"] = new_status
        history_entry = {
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actor": actor or "anonymous",
            "action": "accepted" if new_status == "ACCEPTED" else "rejected",
        }
        if note:
            history_entry["note"] = note
        record.setdefault("history", []).append(history_entry)
        _write_proposal_record(record)
        if new_status == "ACCEPTED":
            # Side-effect: drop a markdown brief Claude Code can pick
            # up on its next /gsd-execute-phase. Failure to write the
            # brief should NOT fail the accept call — the proposal is
            # already mutated and the user expects the status flip to
            # be the source of truth. Log and move on.
            try:
                write_dev_queue_brief(record)
            except OSError:
                pass
    return record, None


def write_dev_queue_brief(record: dict) -> Path:
    """Write a markdown handoff brief Claude Code's /gsd-execute-phase
    can read in a later session. Returns the brief's path. Schema is
    locked by P44-05 tests + P47-02 tests (the markdown is an external
    contract)."""
    path = dev_queue_dir() / f"{record['id']}.md"
    interp = record.get("interpretation") or {}
    affected_gates = ", ".join(interp.get("affected_gates") or []) or "—"
    target_signals = ", ".join(interp.get("target_signals") or []) or "—"
    history = record.get("history") or []
    accepted_entry = next(
        (h for h in reversed(history) if h.get("action") == "accepted"),
        None,
    )
    accepted_at = accepted_entry["at"] if accepted_entry else "—"
    accepted_by = accepted_entry["actor"] if accepted_entry else "—"
    kind = record.get("kind") or "modify"
    if kind == "revert":
        brief = _write_revert_brief_body(
            record=record,
            interp=interp,
            affected_gates=affected_gates,
            target_signals=target_signals,
            accepted_at=accepted_at,
            accepted_by=accepted_by,
        )
    else:
        brief = (
            f"# Proposal {record['id']}\n"
            f"\n"
            f"<!-- dev_queue brief schema v{DEV_QUEUE_BRIEF_VERSION} —"
            f" generated by demo_server.write_dev_queue_brief; do not"
            f" hand-edit -->\n"
            f"\n"
            f"- **Kind**: modify\n"
            f"- **Status**: ACCEPTED ({accepted_at} by {accepted_by})\n"
            f"- **System**: {record.get('system_id', '—')}\n"
            f"- **Affected gates**: {affected_gates}\n"
            f"- **Target signals**: {target_signals}\n"
            f"- **Change kind**: {interp.get('change_kind', '—')}\n"
            f"- **Confidence**: {interp.get('confidence', '—')}\n"
            f"- **Submitted by**: {record.get('author_name', '—')}"
            f" ({record.get('author_role', '—')})\n"
            f"- **Ticket**: {record.get('ticket_id', '—')}\n"
            f"- **Created**: {record.get('created_at', '—')}\n"
            f"\n"
            f"## Engineer's original suggestion · 工程师原始建议\n"
            f"\n"
            f"> {record.get('source_text', '').strip() or '(empty)'}\n"
            f"\n"
            f"## System interpretation · 系统解读\n"
            f"\n"
            f"- Summary (zh): {interp.get('summary_zh', '—')}\n"
            f"- Summary (en): {interp.get('summary_en', '—')}\n"
            f"\n"
            f"## Handoff to Claude Code\n"
            f"\n"
            f"1. Open this brief and the linked proposal JSON at"
            f" `.planning/proposals/{record['id']}.json`.\n"
            f"2. Run `/gsd-execute-phase` to plan + implement the change"
            f" against the truth-engine code (controller / runner /"
            f" models / adapters).\n"
            f"3. After merging the truth-engine PR, record the merge SHA on"
            f" this proposal so the workbench can offer the revert path:\n"
            f"   ```\n"
            f"   curl -X POST http://localhost:8770/api/proposals/{record['id']}/landed \\\n"
            f"        -H 'Content-Type: application/json' \\\n"
            f"        -d '{{\"sha\": \"<merge-commit-sha>\", \"actor\": \"claude-code-executor\"}}'\n"
            f"   ```\n"
            f"4. Mark this brief complete by deleting it from"
            f" `.planning/dev_queue/` (the proposal JSON's status"
            f" remains the audit truth).\n"
        )
    path.write_text(brief, encoding="utf-8")
    return path


def _write_revert_brief_body(
    *,
    record: dict,
    interp: dict,
    affected_gates: str,
    target_signals: str,
    accepted_at: str,
    accepted_by: str,
) -> str:
    """P47-02: revert brief body. Different from a modify brief in
    two ways: (1) the executor's job is to re-create a target file
    state derived from `<revert_target_sha>~1`, not implement a
    free-form suggestion; (2) the brief explicitly references the
    original proposal so the audit trail stays linked."""
    target_sha = record.get("revert_target_sha", "—")
    original_id = record.get("revert_of_proposal_id", "—")
    return (
        f"# Proposal {record['id']} · REVERT\n"
        f"\n"
        f"<!-- dev_queue brief schema v{DEV_QUEUE_BRIEF_VERSION} (revert) —"
        f" generated by demo_server.write_dev_queue_brief; do not"
        f" hand-edit -->\n"
        f"\n"
        f"- **Kind**: revert\n"
        f"- **Status**: ACCEPTED ({accepted_at} by {accepted_by})\n"
        f"- **System**: {record.get('system_id', '—')}\n"
        f"- **Reverts proposal**: `{original_id}`\n"
        f"- **Reverts truth-engine commit**: `{target_sha}`\n"
        f"- **Affected gates** (inherited from original): {affected_gates}\n"
        f"- **Target signals** (inherited from original): {target_signals}\n"
        f"- **Submitted by**: {record.get('author_name', '—')}"
        f" ({record.get('author_role', '—')})\n"
        f"- **Ticket**: {record.get('ticket_id', '—')}\n"
        f"- **Created**: {record.get('created_at', '—')}\n"
        f"\n"
        f"## Why this revert was proposed · 提议理由\n"
        f"\n"
        f"> {record.get('source_text', '').strip() or '(empty)'}\n"
        f"\n"
        f"## Reverse-target state · 目标态\n"
        f"\n"
        f"The executor must restore truth-engine files affected by"
        f" commit `{target_sha}` to the state they had at"
        f" `{target_sha}~1` (the parent commit). To inspect the diff"
        f" that needs undoing:\n"
        f"\n"
        f"```\n"
        f"git show {target_sha}\n"
        f"git diff {target_sha}~1 {target_sha} -- <files>\n"
        f"```\n"
        f"\n"
        f"## Handoff to Claude Code\n"
        f"\n"
        f"1. Open this brief and the linked proposal JSON at"
        f" `.planning/proposals/{record['id']}.json`.\n"
        f"2. Inspect the original commit's diff; treat the file"
        f" contents at `{target_sha}~1` as the desired ground truth.\n"
        f"3. Plan/ask/implement the reversal via the standard"
        f" `/gsd-execute-phase-from-brief` flow — DO NOT just run"
        f" `git revert` blindly. The executor's planner-and-confirm"
        f" cycle must still apply (per Q2 user direction 2026-04-27)"
        f" so any incidental conflicts surface for the engineer to"
        f" resolve, not the bot.\n"
        f"4. After merging the revert PR, record its SHA on this"
        f" revert proposal:\n"
        f"   ```\n"
        f"   curl -X POST http://localhost:8770/api/proposals/{record['id']}/landed \\\n"
        f"        -H 'Content-Type: application/json' \\\n"
        f"        -d '{{\"sha\": \"<revert-merge-sha>\", \"actor\": \"claude-code-executor\"}}'\n"
        f"   ```\n"
        f"5. Mark this brief complete by deleting it from"
        f" `.planning/dev_queue/` (the proposal JSON's status remains"
        f" the audit truth).\n"
    )


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


# ─── E11-06: state-of-the-world helpers ──────────────────────────────


def _truth_engine_short_sha() -> str:
    """Return the short HEAD SHA of the working repo, or 'unknown' if
    git is unavailable. The bar copy must never crash the page."""
    import subprocess
    try:
        repo_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return "unknown"


# P47-01 (2026-04-27): multi-namespace panel-version chip.
#
# Three truth namespaces — each one is a set of files that, taken
# together, define one of the three "things the engineer sees on
# /workbench". The chip surfaces the latest commit that touched
# each namespace's file set, so an engineer can spot at a glance
# whether (e.g.) requirements-doc has drifted past logic-truth.
#
# P48-02 (2026-04-27): the namespace definition lifted to
# `well_harness.skill_executor.namespaces` so the planner can use
# the same source of truth when validating "this edit must fall
# within affected_namespaces". The local `_PANEL_NAMESPACES` alias
# is kept for backwards compatibility with existing tests.
from well_harness.skill_executor.namespaces import (
    PANEL_NAMESPACES as _PANEL_NAMESPACES,
)
from well_harness.skill_executor.executor_spawner import (
    SpawnStatus as _SpawnStatus,
    SpawnerError as _SpawnerError,
    spawn_executor_for_proposal as _spawn_executor_for_proposal,
)


def _namespace_head_info(files: tuple[str, ...]) -> dict:
    """Latest commit (short_sha + subject + ISO commit time) that
    touched ANY of the namespace's files. Returns 'unknown' fields
    if git is unavailable. Never crashes the page.

    `git log -1 --format=<fmt> -- <files>` is the canonical way to
    say "give me the most recent commit that touched any of these
    paths". Walks history, not just HEAD, so a namespace whose
    files weren't touched in the last commit still reports its
    own last-touch SHA accurately.
    """
    import subprocess
    repo_root = Path(__file__).resolve().parents[2]
    out = {
        "head_sha": "unknown",
        "head_subject": "—",
        "head_committed_at": "—",
    }
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%h%x09%s%x09%cI",
                "--",
                *files,
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return out
    if result.returncode != 0:
        return out
    line = (result.stdout or "").strip()
    if not line:
        # No commit yet touches this namespace (e.g. brand-new files).
        return out
    parts = line.split("\t", 2)
    if len(parts) >= 1 and parts[0]:
        out["head_sha"] = parts[0]
    if len(parts) >= 2 and parts[1]:
        out["head_subject"] = parts[1]
    if len(parts) >= 3 and parts[2]:
        out["head_committed_at"] = parts[2]
    return out


def _panel_namespaces_payload() -> list[dict]:
    """Compose the per-namespace head info for the state-of-world
    payload. One git invocation per namespace (3 total, ~6ms each
    on a warm cache)."""
    payload: list[dict] = []
    for ns in _PANEL_NAMESPACES:
        info = _namespace_head_info(ns["files"])
        payload.append(
            {
                "namespace": ns["namespace"],
                "label_zh": ns["label_zh"],
                "label_en": ns["label_en"],
                "files": list(ns["files"]),
                "head_sha": info["head_sha"],
                "head_subject": info["head_subject"],
                "head_committed_at": info["head_committed_at"],
                "head_source": "git log -1 --format -- <files>",
            }
        )
    return payload


def _read_recent_evidence_lines() -> dict:
    """Parse the most-recent evidence stamp out of the coordination
    qa_report. Returns three optional fields. Falls back to empty
    strings if the file is missing or malformed; the bar then renders
    "—" instead of crashing."""
    repo_root = Path(__file__).resolve().parents[2]
    qa_report = repo_root / "docs" / "coordination" / "qa_report.md"
    out = {
        "recent_e2e_label": "",
        "adversarial_label": "",
        "last_executed_evidence": "",
    }
    try:
        text = qa_report.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return out
    # Match e.g. "175 tests OK"
    m = re.search(r"(\d+)\s*tests?\s*OK", text)
    if m:
        out["recent_e2e_label"] = f"{m.group(1)} tests OK"
    # Match e.g. "8/8 shared validation checks pass"
    m = re.search(r"(\d+/\d+)\s*shared validation", text)
    if m:
        out["adversarial_label"] = f"{m.group(1)} shared validation pass"
    # Match the most recent execution evidence backtick block
    m = re.search(r"最近成功执行证据：`([^`]+)`", text)
    if m:
        out["last_executed_evidence"] = m.group(1)
    return out


def _open_known_issues_count() -> int:
    """Count files in docs/known-issues/ (or /known_issues/). Returns 0
    if the directory does not exist."""
    repo_root = Path(__file__).resolve().parents[2]
    for candidate in ("known-issues", "known_issues"):
        directory = repo_root / "docs" / candidate
        if directory.is_dir():
            return sum(
                1
                for entry in directory.iterdir()
                if entry.is_file() and entry.suffix in {".md", ".txt"}
            )
    return 0


def workbench_state_of_world_payload() -> dict:
    """E11-06: aggregate read-only fields for the /workbench status bar.

    Honest about its advisory nature: every field has a `source` label
    so the user can trace where a given value came from, and the
    `kind: "advisory"` flag is the contract that this is NOT a live
    truth-engine reading."""
    evidence = _read_recent_evidence_lines()
    return {
        "kind": "advisory",
        "truth_engine_sha": _truth_engine_short_sha(),
        "truth_engine_sha_source": "git rev-parse --short HEAD",
        # P47-01: per-namespace last-touch lineage so the engineer can
        # see whether (e.g.) requirements drifted past logic_truth.
        "panel_namespaces": _panel_namespaces_payload(),
        "recent_e2e_label": evidence["recent_e2e_label"] or "—",
        "recent_e2e_source": "docs/coordination/qa_report.md",
        "adversarial_label": evidence["adversarial_label"] or "—",
        "adversarial_source": "docs/coordination/qa_report.md",
        "open_known_issues_count": _open_known_issues_count(),
        "open_known_issues_source": "docs/known-issues/ (file count)",
        "last_executed_evidence": evidence["last_executed_evidence"] or "—",
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
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

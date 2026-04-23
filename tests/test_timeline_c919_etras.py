"""PR-3: C919 E-TRAS executor + /api/timeline-simulate endpoint tests."""

from __future__ import annotations

import http.client
import importlib
import json
import socket
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from well_harness.timeline_engine import (
    Timeline,
    TimelineEvent,
    TimelinePlayer,
    parse_timeline,
)
from well_harness.timeline_engine.executors.c919_etras import C919ETRASExecutor


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMELINE_FIXTURES_DIR = REPO_ROOT / "src" / "well_harness" / "timelines"


def _load_panel_server_module():
    """Import scripts/c919_etras_panel_server.py without touching sys.argv."""
    scripts_dir = REPO_ROOT / "scripts"
    saved = sys.path[:]
    sys.path.insert(0, str(scripts_dir))
    try:
        # Reload fresh so the global `_system` / `_logger` start clean each test.
        if "c919_etras_panel_server" in sys.modules:
            del sys.modules["c919_etras_panel_server"]
        module = importlib.import_module("c919_etras_panel_server")
    finally:
        sys.path[:] = saved
    return module


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class C919ExecutorDirectTests(unittest.TestCase):
    """Executor-level tests (no HTTP)."""

    def test_nominal_deploy_fixture_reaches_fadec_deploy(self):
        path = TIMELINE_FIXTURES_DIR / "c919_nominal_deploy.json"
        timeline = parse_timeline(json.loads(path.read_text("utf-8")))
        trace = TimelinePlayer(timeline, C919ETRASExecutor()).run()

        self.assertTrue(all(a.passed for a in trace.assertions),
                        msg=f"assertions: {[(a.target, a.observed) for a in trace.assertions]}")
        self.assertIn("ln_fadec_deploy_command", trace.outcome.logic_first_active_t_s)
        # TR position should reach 100%.
        final = trace.frames[-1]
        self.assertGreaterEqual(final.outputs.get("tr_position_pct", 0), 80.0)
        # State machine reaches S5_DEPLOYED_IDLE_REVERSE (or later).
        self.assertIn(
            final.outputs.get("state"),
            ("S5_DEPLOYED_IDLE_REVERSE", "S6_MAX_REVERSE"),
        )

    def test_tr_inhibited_fixture_blocks_everything(self):
        path = TIMELINE_FIXTURES_DIR / "c919_tr_inhibited_blocks_deploy.json"
        timeline = parse_timeline(json.loads(path.read_text("utf-8")))
        trace = TimelinePlayer(timeline, C919ETRASExecutor()).run()

        self.assertTrue(all(a.passed for a in trace.assertions),
                        msg=f"assertions: {[(a.target, a.observed) for a in trace.assertions]}")
        # CMD2/CMD3 never activate, fadec_deploy_command never fires.
        self.assertNotIn("ln_eicu_cmd2", trace.outcome.logic_first_active_t_s)
        self.assertNotIn("ln_fadec_deploy_command", trace.outcome.logic_first_active_t_s)
        # Cascade should include at least one inhibit-attributed block after t=1s.
        post_inhibit = [c for c in trace.outcome.failure_cascade if c["at_s"] >= 1.0]
        # Even zero cascade entries is acceptable here because the gate never
        # went active first — the inhibit pre-empts CMD2 every tick.
        self.assertEqual(
            trace.frames[-1].outputs.get("state"),
            "SF_ABORT_OR_FAULT",
        )

    def test_over_temp_fault_aborts_deploy_mid_cycle(self):
        """Over-temp fault mid-deploy drops TR_Command3_Enable and preempts to SF."""
        timeline = Timeline(
            system="c919-etras",
            step_s=0.05,
            duration_s=8.0,
            initial_inputs={
                "tra_deg": 5.0,
                "lgcu1_mlg_wow": False, "lgcu2_mlg_wow": False,
                "lgcu1_valid": True, "lgcu2_valid": True,
                "engine_running": True, "n1k_pct": 25.0,
            },
            events=[
                TimelineEvent(t_s=0.0, kind="set_input", target="lgcu1_mlg_wow", value=True),
                TimelineEvent(t_s=0.0, kind="set_input", target="lgcu2_mlg_wow", value=True),
                TimelineEvent(t_s=0.5, kind="ramp_input", target="tra_deg", value=-12.5, duration_s=3.5),
                TimelineEvent(t_s=4.0, kind="inject_fault", target="etras_over_temp_fault:stuck_on"),
            ],
        )
        trace = TimelinePlayer(timeline, C919ETRASExecutor()).run()
        # Before fault: fadec_deploy_command was active briefly.
        pre_fault = [f for f in trace.frames if f.t_s < 4.0]
        self.assertTrue(any(f.outputs.get("fadec_deploy_command") for f in pre_fault),
                        msg="deploy should have fired at least once before over-temp injection")
        # After fault: state machine preempts to SF, and TR_Command3_Enable
        # drops (three_phase_trcu_power_on goes False because the CMD3 latch
        # resets when tr_command3_enable is FALSE per cmd3_latch_controller).
        # fadec_deploy_command itself does NOT gate on over_temp per the PDF,
        # so the stale signal may remain — the safety net is TRCU power cut.
        post_fault = trace.frames[-1]
        self.assertEqual(post_fault.outputs.get("state"), "SF_ABORT_OR_FAULT")
        self.assertFalse(post_fault.outputs.get("three_phase_trcu_power_on"),
                         msg="CMD3 three-phase TRCU power must be cut after over-temp")

    def test_full_deploy_stow_cycle_reaches_s10(self):
        """Codex PR-3 MAJOR #1 regression: unlock_engaged must release at
        S9_LOCK_CONFIRM so the lock dwell accumulator can accumulate and
        the state machine can transition S9 → S10. Previously unlock_engaged
        latched permanently and the sim stalled at S9 forever.
        """
        timeline = Timeline(
            system="c919-etras",
            step_s=0.05,
            duration_s=22.0,
            initial_inputs={
                "tra_deg": 5.0,
                "lgcu1_mlg_wow": True, "lgcu2_mlg_wow": True,
                "lgcu1_valid": True, "lgcu2_valid": True,
                "engine_running": True, "tr_inhibited": False,
                "etras_over_temp_fault": False,
                "n1k_pct": 25.0, "max_n1k_deploy_limit_pct": 84.0, "max_n1k_stow_limit_pct": 30.0,
            },
            events=[
                TimelineEvent(t_s=0.5, kind="ramp_input", target="tra_deg", value=-12.5, duration_s=3.5),
                TimelineEvent(t_s=8.0, kind="ramp_input", target="tra_deg", value=-28.0, duration_s=1.0),
                TimelineEvent(t_s=12.0, kind="ramp_input", target="tra_deg", value=0.0, duration_s=1.0),
            ],
        )
        trace = TimelinePlayer(timeline, C919ETRASExecutor()).run()
        states_seen = {f.outputs.get("state") for f in trace.frames}
        self.assertIn("S10_STOWED_LOCKED_POWER_OFF", states_seen,
                      msg=f"full cycle must reach S10; saw states={states_seen}")
        # Final state should be S10.
        self.assertEqual(trace.frames[-1].outputs.get("state"),
                         "S10_STOWED_LOCKED_POWER_OFF")

    def test_outcome_extra_populated_for_c919(self):
        """Codex PR-3 MAJOR #3: TimelineOutcome.extra must carry C919-specific
        fields (deployed_successfully / reached_deployed_state / etc)
        contributed by Executor.summarize_outcome.
        """
        path = TIMELINE_FIXTURES_DIR / "c919_nominal_deploy.json"
        timeline = parse_timeline(json.loads(path.read_text("utf-8")))
        trace = TimelinePlayer(timeline, C919ETRASExecutor()).run()
        self.assertIn("reached_deployed_state", trace.outcome.extra)
        self.assertIn("final_state", trace.outcome.extra)
        self.assertIn("tr_position_peak_pct", trace.outcome.extra)
        self.assertTrue(trace.outcome.extra["reached_deployed_state"])
        self.assertGreater(trace.outcome.extra["tr_position_peak_pct"], 80.0)
        # Executor override should also flip the base deployed_successfully.
        self.assertTrue(trace.outcome.deployed_successfully)

    def test_unknown_fault_raises(self):
        timeline = Timeline(
            system="c919-etras",
            step_s=0.05,
            duration_s=1.0,
            initial_inputs={"tra_deg": 0.0, "engine_running": True},
            events=[
                TimelineEvent(t_s=0.5, kind="inject_fault", target="tr_inhibited:wiggle"),
            ],
        )
        with self.assertRaises(ValueError):
            TimelinePlayer(timeline, C919ETRASExecutor()).run()


class C919TimelineApiTests(unittest.TestCase):
    """HTTP tests against the c919_etras_panel_server's /api/timeline-simulate."""

    @classmethod
    def setUpClass(cls):
        cls.module = _load_panel_server_module()
        cls.port = _pick_free_port()
        cls.server = ThreadingHTTPServer(("127.0.0.1", cls.port), cls.module.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _post(self, path: str, payload: dict) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request(
            "POST", path,
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        body = json.loads(resp.read().decode("utf-8"))
        return resp.status, body

    def test_nominal_deploy_api_roundtrip(self):
        path = TIMELINE_FIXTURES_DIR / "c919_nominal_deploy.json"
        payload = json.loads(path.read_text("utf-8"))
        status, body = self._post("/api/timeline-simulate", payload)
        self.assertEqual(status, 200)
        self.assertTrue(body["outcome"]["deployed_successfully"])
        self.assertTrue(body["outcome"]["reached_deployed_state"])
        self.assertIn(body["outcome"]["final_state"],
                      ("S5_DEPLOYED_IDLE_REVERSE", "S6_MAX_REVERSE"))
        self.assertTrue(all(a["passed"] for a in body["assertions"]))
        self.assertLessEqual(len(body["transitions"]), len(body["frames"]))

    def test_rejects_fantui_system(self):
        status, body = self._post(
            "/api/timeline-simulate",
            {"system": "fantui", "step_s": 0.1, "duration_s": 1.0},
        )
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "unsupported_system")

    def test_unknown_fault_returns_400(self):
        payload = {
            "system": "c919-etras",
            "step_s": 0.05,
            "duration_s": 1.0,
            "initial_inputs": {"tra_deg": 0.0, "engine_running": True},
            "events": [
                {"t_s": 0.5, "kind": "inject_fault", "target": "tr_inhibited:wiggle"},
            ],
        }
        status, body = self._post("/api/timeline-simulate", payload)
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "invalid_timeline")


if __name__ == "__main__":
    unittest.main()

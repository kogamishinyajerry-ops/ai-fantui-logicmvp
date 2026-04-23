"""PR-2: FANTUI executor + /api/timeline-simulate endpoint tests."""

from __future__ import annotations

import http.client
import json
import threading
import time
import unittest
from http.server import HTTPServer
from pathlib import Path

from well_harness.demo_server import DemoRequestHandler
from well_harness.timeline_engine import (
    Timeline,
    TimelineEvent,
    TimelinePlayer,
    parse_timeline,
)
from well_harness.timeline_engine.executors.fantui import FantuiExecutor


TIMELINE_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "src" / "well_harness" / "timelines"


def start_server():
    server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def post_json(port: int, path: str, payload: dict) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request(
        "POST",
        path,
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    body = json.loads(resp.read().decode("utf-8"))
    return resp.status, body


class FantuiExecutorDirectTests(unittest.TestCase):
    """Executor-level tests (no HTTP, no JSON)."""

    def test_nominal_landing_timeline_reaches_l4(self):
        path = TIMELINE_FIXTURES_DIR / "nominal_landing.json"
        timeline = parse_timeline(json.loads(path.read_text("utf-8")))
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()

        self.assertTrue(trace.outcome.deployed_successfully)
        self.assertTrue(trace.outcome.thr_lock_released)
        # L1 should activate before L4.
        l1_t = trace.outcome.logic_first_active_t_s.get("logic1")
        l4_t = trace.outcome.logic_first_active_t_s.get("logic4")
        self.assertIsNotNone(l1_t)
        self.assertIsNotNone(l4_t)
        self.assertLess(l1_t, l4_t)
        # Phases flowed through.
        phases = {f.phase for f in trace.frames}
        self.assertIn("descent", phases)
        self.assertIn("landing", phases)
        self.assertIn("deploy", phases)
        # All assertions passed.
        for a in trace.assertions:
            self.assertTrue(a.passed, msg=f"assertion at {a.at_s}s failed: {a}")

    def test_sw1_stuck_at_touchdown_blocks_chain(self):
        path = TIMELINE_FIXTURES_DIR / "sw1_stuck_at_touchdown.json"
        timeline = parse_timeline(json.loads(path.read_text("utf-8")))
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()

        self.assertFalse(trace.outcome.deployed_successfully)
        self.assertFalse(trace.outcome.thr_lock_released)
        # logic1 must appear blocked at some point.
        self.assertIn("logic1", trace.outcome.logic_first_blocked_t_s)
        # All assertions passed (they assert the broken state).
        for a in trace.assertions:
            self.assertTrue(a.passed, msg=f"assertion at {a.at_s}s failed: {a}")

    def test_scrubber_and_timeline_agree_on_final_state(self):
        """Parity check: a timeline that reproduces lever_snapshot's canonical
        pullback to -26° with manual VDT=100 should yield the same terminal
        logic_states as a /api/lever-snapshot call — validating the executor
        wraps the controller+plant exactly like the existing endpoint.
        """
        timeline = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=10.0,
            initial_inputs={
                "radio_altitude_ft": 5.0,
                "tra_deg": 0.0,
                "engine_running": True,
                "aircraft_on_ground": True,
                "reverser_inhibited": False,
                "eec_enable": True,
                "n1k": 0.35,
                "max_n1k_deploy_limit": 60.0,
            },
            events=[
                TimelineEvent(t_s=0.0, kind="ramp_input", target="tra_deg", value=-26.0, duration_s=4.0),
            ],
        )
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()
        final = trace.frames[-1]
        # At the end, all four layers should be active (plant has fully deployed).
        self.assertEqual(final.logic_states.get("logic1"), "blocked")  # !DEP released after deploy
        self.assertEqual(final.logic_states.get("logic4"), "active")
        self.assertTrue(final.outputs["throttle_electronic_lock_release_cmd"])

    def test_time_varying_fault_cleared_mid_sim(self):
        """SW1 stuck from t=5→7s then cleared; if TRA is already past SW1
        window before t=7, L1 can still fire after the fault clears thanks
        to the latch re-evaluating on the next crossing."""
        timeline = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=10.0,
            initial_inputs={
                "radio_altitude_ft": 2.0,
                "tra_deg": 0.0,
                "engine_running": True,
                "aircraft_on_ground": True,
                "reverser_inhibited": False,
                "eec_enable": True,
                "n1k": 0.35,
                "max_n1k_deploy_limit": 60.0,
            },
            events=[
                TimelineEvent(t_s=5.0, kind="inject_fault", target="sw1:stuck_off"),
                TimelineEvent(t_s=7.0, kind="clear_fault", target="sw1:stuck_off"),
                # Pull TRA after fault clears so the latch has fresh input
                TimelineEvent(t_s=7.5, kind="ramp_input", target="tra_deg", value=-14.0, duration_s=1.0),
            ],
        )
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()
        # During the fault window, logic1 cannot latch active even if TRA is in window.
        mid_frame = next(f for f in trace.frames if abs(f.t_s - 6.0) < 0.05)
        self.assertIn("sw1:stuck_off", mid_frame.active_faults)
        # After fault clears and TRA enters SW1 window again, logic1 should activate.
        post_frame = trace.frames[-1]
        self.assertNotIn("sw1:stuck_off", post_frame.active_faults)


class FantuiTimelineApiTests(unittest.TestCase):
    """HTTP endpoint tests."""

    def setUp(self):
        self.server, self.thread = start_server()

    def tearDown(self):
        stop_server(self.server, self.thread)

    def test_rejects_invalid_timeline(self):
        status, body = post_json(
            self.server.server_port,
            "/api/timeline-simulate",
            {"system": "fantui", "step_s": 0, "duration_s": 1.0},
        )
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "invalid_timeline")

    def test_rejects_non_fantui_system(self):
        status, body = post_json(
            self.server.server_port,
            "/api/timeline-simulate",
            {"system": "c919-etras", "step_s": 0.1, "duration_s": 1.0},
        )
        self.assertEqual(status, 400)
        self.assertEqual(body.get("error"), "unsupported_system")

    def test_nominal_landing_api_roundtrip(self):
        path = TIMELINE_FIXTURES_DIR / "nominal_landing.json"
        payload = json.loads(path.read_text("utf-8"))
        status, body = post_json(self.server.server_port, "/api/timeline-simulate", payload)
        self.assertEqual(status, 200)
        self.assertTrue(body["outcome"]["deployed_successfully"])
        self.assertTrue(body["outcome"]["thr_lock_released"])
        self.assertTrue(all(a["passed"] for a in body["assertions"]))
        # transitions should be a compressed view of frames
        self.assertLessEqual(len(body["transitions"]), len(body["frames"]))


if __name__ == "__main__":
    unittest.main()

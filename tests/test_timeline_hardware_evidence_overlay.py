from __future__ import annotations

import http.client
import json
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path

from well_harness.demo_server import DemoRequestHandler
from well_harness.timeline_engine import TimelinePlayer, parse_timeline
from well_harness.timeline_engine.executors.fantui import FantuiExecutor


TIMELINE_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "src" / "well_harness" / "timelines"


def nominal_timeline_payload() -> dict:
    path = TIMELINE_FIXTURES_DIR / "nominal_landing.json"
    return json.loads(path.read_text("utf-8"))


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


class TimelineHardwareEvidenceOverlayTests(unittest.TestCase):
    def test_fantui_timeline_outcome_includes_read_only_hardware_overlay(self):
        timeline = parse_timeline(nominal_timeline_payload())
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()

        overlay = trace.outcome.extra["hardware_evidence_overlay"]

        self.assertEqual(overlay["system_id"], "thrust-reverser")
        self.assertEqual(overlay["truth_level_impact"], "none")
        self.assertTrue(overlay["read_only"])
        self.assertEqual(overlay["lru_count"], 11)
        self.assertEqual(overlay["signal_binding_count"], 18)
        self.assertEqual(overlay["total_evidence_gap_field_count"], 141)

    def test_overlay_references_signal_and_lru_ids_without_truth_gating(self):
        timeline = parse_timeline(nominal_timeline_payload())
        trace = TimelinePlayer(timeline, FantuiExecutor()).run()
        overlay = trace.outcome.extra["hardware_evidence_overlay"]

        tls_binding = next(
            item for item in overlay["signal_bindings"] if item["signal_id"] == "tls_115vac_cmd"
        )

        self.assertEqual(tls_binding["source_hardware_id"], "etrac")
        self.assertEqual(tls_binding["peer_hardware_id"], "tls")
        self.assertEqual(tls_binding["cable"]["status"], "evidence_gap")
        self.assertEqual(tls_binding["connector"]["status"], "evidence_gap")
        self.assertEqual(tls_binding["feeds_logic_nodes"], ["L1"])
        self.assertTrue(trace.outcome.deployed_successfully)

    def test_timeline_api_serializes_hardware_overlay_under_outcome_extra(self):
        server, thread = start_server()
        try:
            status, body = post_json(server.server_port, "/api/timeline-simulate", nominal_timeline_payload())
        finally:
            stop_server(server, thread)

        self.assertEqual(status, 200)
        overlay = body["outcome"]["extra"]["hardware_evidence_overlay"]
        self.assertEqual(overlay["system_id"], "thrust-reverser")
        self.assertEqual(overlay["hardware_path"], "config/hardware/thrust_reverser_hardware_v1.yaml")
        self.assertEqual(overlay["signal_bindings"][0]["evidence_status"], "evidence_gap")


if __name__ == "__main__":
    unittest.main()

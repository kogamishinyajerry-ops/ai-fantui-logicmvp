from __future__ import annotations

import http.client
import json
import threading
import unittest
from http.server import HTTPServer

from well_harness.demo_server import DemoRequestHandler


def start_server():
    server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def get_json(port: int, path: str) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = json.loads(resp.read().decode("utf-8"))
    return resp.status, body


class HardwareEvidenceApiTests(unittest.TestCase):
    def setUp(self):
        self.server, self.thread = start_server()

    def tearDown(self):
        stop_server(self.server, self.thread)

    def test_default_hardware_evidence_endpoint_returns_thrust_reverser_report(self):
        status, body = get_json(self.server.server_port, "/api/hardware/evidence")

        self.assertEqual(status, 200)
        self.assertEqual(body["schema_version"], "hardware_evidence_report.v1")
        self.assertEqual(body["status"], "pass")
        self.assertEqual(body["hardware_summary"]["system_id"], "thrust-reverser")
        self.assertEqual(body["coverage"]["lru_inventory"]["actual_count"], 11)
        self.assertEqual(body["coverage"]["signal_bindings"]["actual_count"], 18)
        self.assertEqual(body["evidence_gaps"]["total_field_count"], 141)
        self.assertEqual(body["truth_level_impact"], "none")

    def test_explicit_thrust_reverser_query_matches_default_endpoint(self):
        default_status, default_body = get_json(self.server.server_port, "/api/hardware/evidence")
        explicit_status, explicit_body = get_json(
            self.server.server_port,
            "/api/hardware/evidence?system_id=thrust-reverser",
        )

        self.assertEqual(default_status, 200)
        self.assertEqual(explicit_status, 200)
        self.assertEqual(explicit_body, default_body)

    def test_frozen_system_request_returns_non_mutating_error(self):
        status, body = get_json(
            self.server.server_port,
            "/api/hardware/evidence?system_id=c919-etras",
        )

        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "hardware_evidence_unsupported_system")
        self.assertEqual(body["requested_system_id"], "c919-etras")
        self.assertTrue(body["read_only"])
        self.assertFalse(body["mutation_performed"])
        self.assertEqual(body["truth_level_impact"], "none")

    def test_unknown_system_request_returns_non_mutating_error(self):
        status, body = get_json(
            self.server.server_port,
            "/api/hardware/evidence?system_id=fake-system",
        )

        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "hardware_evidence_unsupported_system")
        self.assertEqual(body["requested_system_id"], "fake-system")
        self.assertFalse(body["mutation_performed"])


if __name__ == "__main__":
    unittest.main()

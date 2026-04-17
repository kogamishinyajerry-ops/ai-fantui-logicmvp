"""
Tests for P19.14/P19.15/P19.16 multi-system hardware YAML support:
- POST /api/diagnosis/run with system_id parameter
- POST /api/monte-carlo/run with system_id parameter
- GET  /api/hardware/schema with system_id query param
- Invalid system_id returns HTTP 400

Diagnosis and Monte Carlo engines are thrust-reverser-specific; they return 400
for landing-gear and bleed-air. The hardware schema endpoint supports all systems.

Uses the same _TestServer pattern as test_p19_api_endpoints.py.
"""
from __future__ import annotations

import http.client
import json
import socket
import threading
import time
from typing import Optional

import pytest


class _TestServer:
    """Starts demo_server on a random port, yields (host, port), shuts down on exit."""

    def __init__(self, timeout: float = 5.0):
        self._thread: Optional[threading.Thread] = None
        self.host = "127.0.0.1"
        self.port: Optional[int] = None
        self._server = None
        self.timeout = timeout

    def __enter__(self):
        from http.server import ThreadingHTTPServer
        from well_harness.demo_server import DemoRequestHandler

        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        self.port = sock.getsockname()[1]
        sock.close()

        self._server = ThreadingHTTPServer((self.host, self.port), DemoRequestHandler)
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()
        time.sleep(0.1)
        return self

    def __exit__(self, *args):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=2.0)

    def request(self, method: str, path: str, body=None, headers=None):
        """Make an HTTP request and return (status_code, json_data)."""
        headers = headers or {}
        if body is not None and isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        if isinstance(body, str):
            body = body.encode("utf-8")

        conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        try:
            conn.connect()
            conn.request(method, path, body=body, headers=headers)
            resp = conn.getresponse()
            status = resp.status
            raw = resp.read()
            try:
                data = json.loads(raw.decode("utf-8")) if raw else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = raw.decode("utf-8", errors="replace")
            return status, data
        finally:
            conn.close()


@pytest.fixture
def server():
    with _TestServer() as s:
        yield s


# ── Diagnosis with system_id ─────────────────────────────────────────────────

class TestDiagnosisSystemId:
    """system_id parameter for POST /api/diagnosis/run.

    The ReverseDiagnosisEngine is thrust-reverser-specific. Landing-gear and
    bleed-air return 400 with a clear message; thrust-reverser works normally.
    """

    def test_thrust_reverser_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active", "system_id": "thrust-reverser"},
        )
        assert status == 200
        assert data["outcome"] == "logic1_active"

    def test_landing_gear_returns_400_not_supported(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active", "system_id": "landing-gear"},
        )
        assert status == 400
        assert "error" in data
        assert "landing-gear" in data["error"]
        assert "not supported" in data["error"]

    def test_bleed_air_returns_400_not_supported(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active", "system_id": "bleed-air"},
        )
        assert status == 400
        assert "error" in data
        assert "bleed-air" in data["error"]
        assert "not supported" in data["error"]

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active", "system_id": "invalid-system"},
        )
        assert status == 400
        assert "error" in data
        assert "invalid-system" in data["error"]

    def test_default_is_thrust_reverser(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active"},
        )
        assert status == 200
        assert data["outcome"] == "logic1_active"


# ── Monte Carlo with system_id ───────────────────────────────────────────────

class TestMonteCarloSystemId:
    """system_id parameter for POST /api/monte-carlo/run.

    The MonteCarloEngine is thrust-reverser-specific. Landing-gear and
    bleed-air return 400 with a clear message; thrust-reverser works normally.
    """

    def test_thrust_reverser_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "thrust-reverser"},
        )
        assert status == 200
        assert "success_rate" in data

    def test_landing_gear_returns_400_not_supported(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "landing-gear"},
        )
        assert status == 400
        assert "error" in data
        assert "landing-gear" in data["error"]
        assert "not supported" in data["error"]

    def test_bleed_air_returns_400_not_supported(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "bleed-air"},
        )
        assert status == 400
        assert "error" in data
        assert "bleed-air" in data["error"]
        assert "not supported" in data["error"]

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "unknown-system"},
        )
        assert status == 400
        assert "error" in data
        assert "unknown-system" in data["error"]

    def test_default_is_thrust_reverser(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10},
        )
        assert status == 200
        assert "success_rate" in data


# ── Hardware schema with system_id ──────────────────────────────────────────

class TestHardwareSchemaSystemId:
    """system_id query parameter for GET /api/hardware/schema.

    The hardware schema endpoint supports all onboarded systems via a generic
    YAML loader for non-thrust-reverser systems.
    """

    def test_landing_gear_returns_200(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=landing-gear")
        assert status == 200
        assert data["system_id"] == "landing-gear"

    def test_bleed_air_returns_200(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=bleed-air")
        assert status == 200
        assert data["system_id"] == "bleed-air"

    def test_thrust_reverser_returns_200(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=thrust-reverser")
        assert status == 200
        assert data["system_id"] == "thrust-reverser"

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=fake-system")
        assert status == 400
        assert "error" in data
        assert "fake-system" in data["error"]

    def test_default_is_thrust_reverser(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema")
        assert status == 200
        assert data["system_id"] == "thrust-reverser"

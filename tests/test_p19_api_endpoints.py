"""
Tests for P19.6/P19.7/P19.8 API endpoints:
- POST /api/diagnosis/run
- POST /api/monte-carlo/run
- GET  /api/hardware/schema

Uses a live DemoServer on a random port with a daemon thread — no Flask test client
needed since DemoServer extends http.server.HTTPServer.
"""
from __future__ import annotations

import http.client
import json
import socket
import threading
import time
from typing import Optional

import pytest


# ─── Test server lifecycle ──────────────────────────────────────────────────────


class _TestServer:
    """Starts demo_server on a random port, yields (host, port), shuts down on exit."""

    def __init__(self, timeout: float = 5.0):
        self._thread: Optional[threading.Thread] = None
        self.host = "127.0.0.1"
        self.port: Optional[int] = None
        self._server = None
        self.timeout = timeout

    def __enter__(self):
        # Import here so test collection works without the server running
        from http.server import ThreadingHTTPServer
        from well_harness.demo_server import DemoRequestHandler

        # Find a free port
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        self.port = sock.getsockname()[1]
        sock.close()

        self._server = ThreadingHTTPServer((self.host, self.port), DemoRequestHandler)
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()
        # Give the server a moment to start
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


# ─── POST /api/diagnosis/run ─────────────────────────────────────────────────


class TestDiagnosisRun:
    """test_diagnosis_run — P19.6 diagnosis endpoint."""

    def test_valid_outcome_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run", body={"outcome": "logic1_active"}
        )
        assert status == 200
        assert data["outcome"] == "logic1_active"
        assert "total_combos_found" in data
        assert "grid_resolution" in data
        assert "timestamp" in data
        assert isinstance(data["results"], list)

    def test_max_results_limit(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/diagnosis/run",
            body={"outcome": "logic1_active", "max_results": 3},
        )
        assert status == 200
        assert data["total_combos_found"] <= 3

    def test_invalid_outcome_returns_400(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/diagnosis/run",
            body={"outcome": "not_a_valid_outcome"},
        )
        assert status == 400
        assert "error" in data
        assert "Valid" in data["error"]

    def test_pls_unlocked_satisfiable(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run", body={"outcome": "pls_unlocked"}
        )
        assert status == 200
        assert data["outcome"] == "pls_unlocked"
        assert isinstance(data["results"], list)

    def test_empty_body_default(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run", body={}
        )
        # Empty string for outcome should fail validation
        assert status == 400


# ─── POST /api/monte-carlo/run ───────────────────────────────────────────────


class TestMonteCarloRun:
    """test_monte_carlo_run — P19.7 Monte Carlo endpoint."""

    def test_valid_run_returns_200(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/monte-carlo/run",
            body={"n_trials": 10, "seed": 42},
        )
        assert status == 200
        assert data["n_trials"] == 10
        assert "success_rate" in data
        assert "failure_modes" in data
        assert "mtbf_cycles" in data
        assert "sw1_window_crossings_mean" in data

    def test_seed_reproducibility(self, server) -> None:
        _, d1 = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 5, "seed": 99}
        )
        _, d2 = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 5, "seed": 99}
        )
        assert d1["n_failures"] == d2["n_failures"]

    def test_n_trials_must_be_integer(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/monte-carlo/run",
            body={"n_trials": "not_an_int"},
        )
        assert status == 400
        assert "error" in data

    def test_n_trials_capped_at_10000(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/monte-carlo/run",
            body={"n_trials": 99999},
        )
        assert status == 200
        assert data["n_trials"] <= 10000

    def test_seed_must_be_integer(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/monte-carlo/run",
            body={"n_trials": 10, "seed": "bad"},
        )
        assert status == 400


# ─── GET /api/hardware/schema ────────────────────────────────────────────────


class TestHardwareSchema:
    """test_hardware_schema — P19.8 hardware schema endpoint."""

    def test_returns_200(self, server) -> None:
        status, _ = server.request("GET", "/api/hardware/schema")
        assert status == 200

    def test_returns_json_dict(self, server) -> None:
        _, data = server.request("GET", "/api/hardware/schema")
        assert isinstance(data, dict)

    def test_has_expected_top_level_keys(self, server) -> None:
        _, data = server.request("GET", "/api/hardware/schema")
        for key in ("kind", "version", "system_id", "sensor",
                    "logic_thresholds", "physical_limits", "timing"):
            assert key in data, f"Missing key: {key}"

    def test_logic_thresholds_are_floats(self, server) -> None:
        _, data = server.request("GET", "/api/hardware/schema")
        lt = data["logic_thresholds"]
        assert isinstance(lt["logic1_ra_ft_threshold"], float)
        assert isinstance(lt["logic3_tra_deg_threshold"], float)
        assert isinstance(lt["deploy_90_threshold_percent"], float)

    def test_switch_windows_present(self, server) -> None:
        _, data = server.request("GET", "/api/hardware/schema")
        pl = data["physical_limits"]
        assert "sw1_window" in pl
        assert "near_zero_deg" in pl["sw1_window"]
        assert "deep_reverse_deg" in pl["sw1_window"]

    def test_exposes_lru_inventory_and_signal_carrier_bindings(self, server) -> None:
        _, data = server.request("GET", "/api/hardware/schema")
        assert len(data["lru_inventory"]) == 11
        assert len(data["signal_carrier_bindings"]) == 18
        assert data["lru_inventory"][0]["id"] == "etrac"
        binding_ids = {row["signal_id"] for row in data["signal_carrier_bindings"]}
        assert "deploy_90_percent_vdt" in binding_ids
        assert "throttle_electronic_lock_release_cmd" in binding_ids


# ─── POST /api/sensitivity-sweep ─────────────────────────────────────────────


class TestSensitivitySweep:
    """test_sensitivity_sweep — regression guard for the chat sensitivity panel."""

    def test_returns_200_with_default_grid(self, server) -> None:
        status, data = server.request("POST", "/api/sensitivity-sweep", body={})
        assert status == 200
        assert data["system_id"] == "thrust-reverser"
        assert data["scan_count"] == 25
        assert data["radio_altitude_ft_values"] == [2.0, 5.0, 10.0, 20.0, 40.0]
        assert data["tra_deg_values"] == [-28.0, -20.0, -15.0, -11.0, -6.0]
        assert "matrix_counts" in data
        assert "outcome_totals" in data
        assert data["matrix_counts"]["2"]["-28"] >= 0

    def test_rejects_unsupported_system(self, server) -> None:
        status, data = server.request(
            "POST",
            "/api/sensitivity-sweep",
            body={"system_id": "landing-gear"},
        )
        assert status == 400
        assert data["error"] == "unsupported_system"

"""Shared fixtures for P20.0 e2e tests.

Boots well_harness.demo_server as a subprocess on port 8799, waits until
/api/lever-snapshot responds, then yields a base_url to the tests.

All tests in this package must carry @pytest.mark.e2e so the default
pytest run (639 passed) is not affected. Opt-in via: pytest -m e2e
"""
from __future__ import annotations

import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8799
BASE_URL = f"http://127.0.0.1:{PORT}"
READY_TIMEOUT_S = 10.0


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, deadline_s: float) -> bool:
    probe_payload = json.dumps({
        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
        "aircraft_on_ground": True, "reverser_inhibited": False,
        "eec_enable": True, "n1k": 0.5,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
    }).encode()
    start = time.monotonic()
    while time.monotonic() - start < deadline_s:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            c.request("POST", "/api/lever-snapshot", body=probe_payload,
                      headers={"Content-Type": "application/json"})
            resp = c.getresponse()
            resp.read()
            c.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.15)
    return False


def _spawn_server(port: int, home_override: str | None = None) -> subprocess.Popen:
    env = os.environ.copy()
    # Force module discovery via PYTHONPATH so HOME overrides don't break
    # user-site resolution of the editable-installed well_harness package.
    src_path = str(REPO_ROOT / "src")
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing_pp if existing_pp else "")
    if home_override is not None:
        env["HOME"] = home_override
    proc = subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return proc


def _kill_server(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait(timeout=2.0)


@pytest.fixture(scope="session")
def demo_server():
    """Boot demo_server on :8799 for the whole e2e session."""
    if not _port_free(PORT):
        pytest.fail(f"Port {PORT} is already in use; cannot start e2e demo_server")
    proc = _spawn_server(PORT)
    try:
        if not _wait_ready(PORT, READY_TIMEOUT_S):
            _kill_server(proc)
            pytest.fail(f"demo_server did not become ready on :{PORT} within {READY_TIMEOUT_S}s")
        yield BASE_URL
    finally:
        _kill_server(proc)


@pytest.fixture(scope="function")
def no_minimax_key_server(tmp_path):
    """Boot a second demo_server with HOME pointing at an empty tmp dir.

    Forces `_get_minimax_api_key()` to return '' so LLM endpoints fall into
    the `minimax_api_key_missing` error branch (resilience scenario).
    """
    port = 8798
    if not _port_free(port):
        pytest.fail(f"Port {port} is already in use")
    empty_home = tmp_path / "no_minimax_home"
    empty_home.mkdir()
    proc = _spawn_server(port, home_override=str(empty_home))
    try:
        if not _wait_ready(port, READY_TIMEOUT_S):
            _kill_server(proc)
            pytest.fail(f"no-key demo_server did not become ready on :{port}")
        yield f"http://127.0.0.1:{port}"
    finally:
        _kill_server(proc)


@pytest.fixture
def api_post() -> Callable[[str, str, dict, float], tuple[int, object]]:
    """Return a helper that POSTs JSON and returns (status, parsed_body)."""
    def _post(base_url: str, path: str, payload: dict, timeout: float = 15.0):
        host = base_url.replace("http://", "").split(":")[0]
        port = int(base_url.rsplit(":", 1)[1])
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        try:
            conn.request(
                "POST", path,
                body=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw
            return resp.status, body
        finally:
            conn.close()
    return _post

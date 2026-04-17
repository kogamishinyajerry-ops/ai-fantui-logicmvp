---
phase: P19
plan: P19-17
type: execute
wave: 1
depends_on: [P16]
files_created:
  - tests/test_p19_api_multisystem.py
files_modified: []
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — deterministic tests"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "POST /api/diagnosis/run with system_id=landing-gear returns HTTP 200"
    - "POST /api/diagnosis/run with system_id=bleed-air returns HTTP 200"
    - "POST /api/diagnosis/run with system_id=invalid-system returns HTTP 400"
    - "POST /api/monte-carlo/run with system_id=landing-gear returns HTTP 200"
    - "POST /api/monte-carlo/run with system_id=bleed-air returns HTTP 200"
    - "POST /api/monte-carlo/run with system_id=invalid-system returns HTTP 400"
    - "GET /api/hardware/schema?system_id=landing-gear returns HTTP 200"
    - "GET /api/hardware/schema?system_id=bleed-air returns HTTP 200"
    - "GET /api/hardware/schema?system_id=invalid-system returns HTTP 400"
    - "All 619+ existing tests continue to pass (no regression)"
  artifacts:
    - path: tests/test_p19_api_multisystem.py
      provides: "API tests for multi-system support + invalid system_id → 400"
exit_criteria:
  - "test -f tests/test_p19_api_multisystem.py"
  - "python3 -m pytest tests/test_p19_api_multisystem.py -v 2>&1 | tail -20 (all pass)"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.17 — Analysis API Multi-System + Error Coverage Tests

### Context

P19.14 added multi-system selector, P19.15 added YAML files, P19.16 added error handling. None of these have dedicated API tests. P19.17 adds `tests/test_p19_api_multisystem.py` covering:
- Each endpoint with `system_id=landing-gear` and `system_id=bleed-air`
- Each endpoint with `system_id=invalid-system` returning HTTP 400

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `demo_server.py` — no logic changes, only new test file
- Existing tests — no modifications

### Implementation

#### `tests/test_p19_api_multisystem.py`

Reuse the `_TestServer` fixture from `test_p19_api_endpoints.py` (copy the helper class into this file to keep it self-contained):

```python
"""
Tests for P19.14/P19.15/P19.16 multi-system hardware YAML support:
- POST /api/diagnosis/run with system_id parameter
- POST /api/monte-carlo/run with system_id parameter
- GET  /api/hardware/schema with system_id query param
- Invalid system_id returns HTTP 400

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
    """system_id parameter for POST /api/diagnosis/run."""

    def test_landing_gear_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "lg_extended", "system_id": "landing-gear"}
        )
        assert status == 200
        assert data["outcome"] == "lg_extended"

    def test_bleed_air_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "bau_open", "system_id": "bleed-air"}
        )
        assert status == 200
        assert data["outcome"] == "bau_open"

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active", "system_id": "invalid-system"}
        )
        assert status == 400
        assert "error" in data
        assert "invalid-system" in data["error"]

    def test_thrust_reverser_default_still_works(self, server) -> None:
        status, data = server.request(
            "POST", "/api/diagnosis/run",
            body={"outcome": "logic1_active"}
        )
        assert status == 200
        assert data["outcome"] == "logic1_active"


# ── Monte Carlo with system_id ───────────────────────────────────────────────

class TestMonteCarloSystemId:
    """system_id parameter for POST /api/monte-carlo/run."""

    def test_landing_gear_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "landing-gear"}
        )
        assert status == 200
        assert "success_rate" in data

    def test_bleed_air_returns_200(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "bleed-air"}
        )
        assert status == 200
        assert "success_rate" in data

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10, "system_id": "unknown-system"}
        )
        assert status == 400
        assert "error" in data
        assert "unknown-system" in data["error"]

    def test_thrust_reverser_default_still_works(self, server) -> None:
        status, data = server.request(
            "POST", "/api/monte-carlo/run",
            body={"n_trials": 10}
        )
        assert status == 200
        assert "success_rate" in data


# ── Hardware schema with system_id ──────────────────────────────────────────

class TestHardwareSchemaSystemId:
    """system_id query parameter for GET /api/hardware/schema."""

    def test_landing_gear_returns_200(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=landing-gear")
        assert status == 200
        assert data["system_id"] == "landing-gear"

    def test_bleed_air_returns_200(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=bleed-air")
        assert status == 200
        assert data["system_id"] == "bleed-air"

    def test_invalid_system_returns_400(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema?system_id=fake-system")
        assert status == 400
        assert "error" in data
        assert "fake-system" in data["error"]

    def test_thrust_reverser_default_still_works(self, server) -> None:
        status, data = server.request("GET", "/api/hardware/schema")
        assert status == 200
        # Default is thrust-reverser
        assert data["system_id"] == "thrust-reverser"
```

### Tasks

#### Task 1: Create `tests/test_p19_api_multisystem.py`

Write the test file above.

#### Task 2: Verify new tests pass

```bash
python3 -m pytest tests/test_p19_api_multisystem.py -v
```

#### Task 3: Verify no regression

```bash
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed (should be 619 + N new tests)
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Deterministic pytest tests |
| No breaking changes to existing API contracts | ✓ Only additive tests |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify both:
1. `python3 -m pytest tests/test_p19_api_multisystem.py -v` — all pass
2. `python3 -m pytest -x --tb=short -q 2>&1 | tail -3` — 619+ passed

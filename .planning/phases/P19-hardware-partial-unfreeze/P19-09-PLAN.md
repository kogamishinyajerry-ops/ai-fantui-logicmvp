---
phase: P19
plan: P19-09
type: execute
wave: 1
depends_on: [P19-06, P19-07, P19-08]
files_created:
  - tests/test_p19_api_endpoints.py
files_modified: []
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure HTTP/JSON tests"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "Tests cover all 3 new endpoints: /api/diagnosis/run, /api/monte-carlo/run, /api/hardware/schema"
    - "Tests cover valid inputs, invalid inputs (bad outcome, bad n_trials), and 404 for unknown paths"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: tests/test_p19_api_endpoints.py
      provides: "pytest API tests for P19.6/P19.7/P19.8 endpoints"
      min_lines: 80
  key_constraints:
    - "Use Flask test client (app.test_client()) — no real HTTP server needed"
    - "Import demo_server module directly for test client"
    - "Tests are additive — no modification of existing test files"
exit_criteria:
  - "python3 -m pytest tests/test_p19_api_endpoints.py -x -q passes (≥10 test cases)"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.9 — API Tests for P19.6/P19.7/P19.8 Endpoints

### Context

P19.6 added `POST /api/diagnosis/run`, P19.7 added `POST /api/monte-carlo/run`,
P19.8 added `GET /api/hardware/schema`. No tests exist for these endpoints.
P19.9 adds pytest coverage.

### Implementation

#### `tests/test_p19_api_endpoints.py`

```python
"""
Tests for P19.6/P19.7/P19.8 API endpoints:
- POST /api/diagnosis/run
- POST /api/monte-carlo/run
- GET  /api/hardware/schema

Uses Flask test client — no live server required.
"""
from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from well_harness import demo_server


# ─── Test client fixture ────────────────────────────────────────────────────────


@pytest.fixture
def client():
    """Flask test client for demo_server."""
    app = demo_server.DemoServer("", 0)
    return app.test_client()


# ─── Helpers ─────────────────────────────────────────────────────────────────


YAML_PATH = "config/hardware/thrust_reverser_hardware_v1.yaml"


# ─── POST /api/diagnosis/run ─────────────────────────────────────────────────


class TestDiagnosisRun:
    """test_diagnosis_run — P19.6 diagnosis endpoint."""

    def test_valid_outcome_returns_200(self, client) -> None:
        resp = client.post(
            "/api/diagnosis/run",
            json={"outcome": "logic1_active"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "outcome" in data
        assert data["outcome"] == "logic1_active"
        assert "total_combos_found" in data
        assert "grid_resolution" in data
        assert "timestamp" in data
        assert "results" in data

    def test_max_results_limit(self, client) -> None:
        resp = client.post(
            "/api/diagnosis/run",
            json={"outcome": "logic1_active", "max_results": 3},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_combos_found"] <= 3

    def test_invalid_outcome_returns_400(self, client) -> None:
        resp = client.post(
            "/api/diagnosis/run",
            json={"outcome": "not_a_valid_outcome"},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
        assert "Valid" in data["error"]

    def test_unknown_outcome_error_message_lists_valid(self, client) -> None:
        resp = client.post(
            "/api/diagnosis/run",
            json={"outcome": "xyz_unknown"},
        )
        assert resp.status_code == 400
        assert "Valid" in resp.get_json()["error"]

    def test_pls_unlocked_is_satisfiable(self, client) -> None:
        resp = client.post(
            "/api/diagnosis/run",
            json={"outcome": "pls_unlocked"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["outcome"] == "pls_unlocked"
        assert isinstance(data["results"], list)


# ─── POST /api/monte-carlo/run ───────────────────────────────────────────────


class TestMonteCarloRun:
    """test_monte_carlo_run — P19.7 Monte Carlo endpoint."""

    def test_valid_run_returns_200(self, client) -> None:
        resp = client.post(
            "/api/monte-carlo/run",
            json={"n_trials": 10, "seed": 42},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "n_trials" in data
        assert data["n_trials"] == 10
        assert "success_rate" in data
        assert "failure_modes" in data
        assert "mtbf_cycles" in data
        assert "sw1_window_crossings_mean" in data

    def test_n_trials_default(self, client) -> None:
        resp = client.post(
            "/api/monte-carlo/run",
            json={},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "n_trials" in data

    def test_seed_reproducibility(self, client) -> None:
        resp1 = client.post("/api/monte-carlo/run", json={"n_trials": 5, "seed": 99})
        resp2 = client.post("/api/monte-carlo/run", json={"n_trials": 5, "seed": 99})
        assert resp1.get_json()["n_failures"] == resp2.get_json()["n_failures"]

    def test_n_trials_must_be_integer(self, client) -> None:
        resp = client.post(
            "/api/monte-carlo/run",
            json={"n_trials": "not_an_int"},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_n_trials_capped_at_10000(self, client) -> None:
        resp = client.post(
            "/api/monte-carlo/run",
            json={"n_trials": 99999},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["n_trials"] <= 10000

    def test_seed_must_be_integer(self, client) -> None:
        resp = client.post(
            "/api/monte-carlo/run",
            json={"n_trials": 10, "seed": "bad"},
        )
        assert resp.status_code == 400


# ─── GET /api/hardware/schema ────────────────────────────────────────────────


class TestHardwareSchema:
    """test_hardware_schema — P19.8 hardware schema endpoint."""

    def test_returns_200(self, client) -> None:
        resp = client.get("/api/hardware/schema")
        assert resp.status_code == 200

    def test_returns_json_dict(self, client) -> None:
        data = client.get("/api/hardware/schema").get_json()
        assert isinstance(data, dict)

    def test_has_expected_top_level_keys(self, client) -> None:
        data = client.get("/api/hardware/schema").get_json()
        assert "kind" in data
        assert "version" in data
        assert "system_id" in data
        assert "sensor" in data
        assert "logic_thresholds" in data
        assert "physical_limits" in data
        assert "timing" in data

    def test_logic_thresholds_are_floats(self, client) -> None:
        data = client.get("/api/hardware/schema").get_json()
        lt = data["logic_thresholds"]
        assert isinstance(lt["logic1_ra_ft_threshold"], float)
        assert isinstance(lt["logic3_tra_deg_threshold"], float)
        assert isinstance(lt["deploy_90_threshold_percent"], float)

    def test_switch_windows_present(self, client) -> None:
        data = client.get("/api/hardware/schema").get_json()
        pl = data["physical_limits"]
        assert "sw1_window" in pl
        assert "near_zero_deg" in pl["sw1_window"]
        assert "deep_reverse_deg" in pl["sw1_window"]
```

### Tasks

#### Task 1: Create `tests/test_p19_api_endpoints.py`

Write the test file as defined above.

#### Task 2: Verify exit gates

```bash
# Gate 1: New tests pass
python3 -m pytest tests/test_p19_api_endpoints.py -x -q

# Gate 2: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 614+ passed (604 + ≥10 new)
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ Test-only |
| No LLM calls | ✓ HTTP/JSON tests |
| No breaking changes | ✓ Additive tests |

### Exit Gate

Verify both gates above.

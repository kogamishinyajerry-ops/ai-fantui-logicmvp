"""E2E Wow B — Monte Carlo reliability simulation.

Locks the observable contract of /api/monte-carlo/run against a live
demo_server on :8799: return shape, value ranges, timing budget, and
deterministic seeding.
"""
from __future__ import annotations

import time

import pytest

EXPECTED_TOP_KEYS = {
    "n_trials", "n_failures", "success_rate",
    "mean_cycles_to_failure", "mtbf_cycles", "seed",
    "failure_modes", "sw1_window_crossings_mean", "sw2_window_crossings_mean",
}

# From src/well_harness/monte_carlo_engine.py failure-mode enum
EXPECTED_FAILURE_MODE_KEYS = {
    "ra_sensor_failure", "sw1_missed", "sw2_missed", "tra_stall",
}


def _run(api_post, base_url, n_trials, seed=42):
    return api_post(base_url, "/api/monte-carlo/run",
                    {"system_id": "thrust-reverser", "n_trials": n_trials, "seed": seed})


@pytest.mark.e2e
def test_wow_b_monte_carlo_returns_contract_shape(demo_server, api_post):
    status, body = _run(api_post, demo_server, 1000)
    assert status == 200
    assert isinstance(body, dict)
    missing = EXPECTED_TOP_KEYS - set(body.keys())
    assert not missing, f"monte-carlo response missing keys: {missing}"


@pytest.mark.e2e
def test_wow_b_10k_trials_under_5s(demo_server, api_post):
    """Rehearsal budget: 10k iters must complete well inside the demo window."""
    t0 = time.monotonic()
    status, body = _run(api_post, demo_server, 10000)
    elapsed = time.monotonic() - t0
    assert status == 200
    assert elapsed < 5.0, f"10k MC took {elapsed:.2f}s (budget 5s)"
    assert body["n_trials"] == 10000


@pytest.mark.e2e
def test_wow_b_success_rate_in_unit_interval(demo_server, api_post):
    status, body = _run(api_post, demo_server, 2000)
    assert status == 200
    sr = body["success_rate"]
    assert isinstance(sr, (int, float))
    assert 0.0 <= sr <= 1.0, f"success_rate={sr} not in [0,1]"
    # Consistency: n_failures + successes = n_trials
    assert body["n_failures"] + round(sr * body["n_trials"]) == body["n_trials"] or \
           abs(body["n_failures"] - (1 - sr) * body["n_trials"]) < 1


@pytest.mark.e2e
def test_wow_b_failure_modes_is_nonempty_dict_with_expected_keys(demo_server, api_post):
    status, body = _run(api_post, demo_server, 5000)
    assert status == 200
    modes = body["failure_modes"]
    assert isinstance(modes, dict) and modes
    assert set(modes.keys()) == EXPECTED_FAILURE_MODE_KEYS, (
        f"failure_modes keys changed: {set(modes.keys())}"
    )
    for k, v in modes.items():
        assert isinstance(v, (int, float)), f"{k} must be numeric, got {type(v).__name__}"
        assert v >= 0, f"{k}={v} negative"


@pytest.mark.e2e
def test_wow_b_is_deterministic_under_fixed_seed(demo_server, api_post):
    """Same seed → byte-identical body (critical for rehearsal repeatability)."""
    s1, b1 = _run(api_post, demo_server, 1000, seed=42)
    s2, b2 = _run(api_post, demo_server, 1000, seed=42)
    assert s1 == 200 and s2 == 200
    assert b1 == b2, "Monte Carlo must be deterministic under fixed seed"


@pytest.mark.e2e
def test_wow_b_n_trials_zero_is_clamped_to_min(demo_server, api_post):
    """Known clamp behavior: n_trials=0 is auto-clamped to 1 (graceful, not 400).

    If this changes (e.g. strict 400), update P20.1 contract layer.
    """
    status, body = _run(api_post, demo_server, 0)
    assert status == 200
    assert body["n_trials"] >= 1


@pytest.mark.e2e
def test_wow_b_n_trials_overflow_is_clamped_to_max(demo_server, api_post):
    status, body = _run(api_post, demo_server, 1_500_000)
    assert status == 200
    assert body["n_trials"] <= 10000

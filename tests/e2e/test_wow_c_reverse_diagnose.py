"""E2E Wow C — reverse diagnosis parameter-combination search.

Locks /api/diagnosis/run contract: valid outcome returns a list of parameter
snapshots that satisfy the target, invalid outcome returns a structured 400.

Note: The current response shape does NOT include probabilities or
suggested_action fields. Those are candidates for P20.1 contract expansion.
"""
from __future__ import annotations

import pytest

VALID_OUTCOMES = {
    "logic3_active", "logic1_active", "thr_lock_active",
    "deploy_confirmed", "tls_unlocked", "pls_unlocked",
}

# Keys guaranteed by ParameterSnapshot dataclass in reverse_diagnosis.py
EXPECTED_RESULT_KEYS = {
    "radio_altitude_ft", "tra_deg",
    "sw1_closed", "sw2_closed",
    "tls_unlocked", "pls_unlocked",
}


@pytest.mark.e2e
def test_wow_c_deploy_confirmed_returns_nonempty_results(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 10,
    })
    assert status == 200
    assert isinstance(body, dict)
    assert body["outcome"] == "deploy_confirmed"
    assert body["total_combos_found"] >= 1
    assert isinstance(body["results"], list) and len(body["results"]) >= 1
    assert len(body["results"]) <= 10


@pytest.mark.e2e
def test_wow_c_each_result_carries_required_parameter_keys(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 5,
    })
    assert status == 200
    for idx, snap in enumerate(body["results"]):
        assert isinstance(snap, dict), f"result[{idx}] must be a dict"
        missing = EXPECTED_RESULT_KEYS - set(snap.keys())
        assert not missing, f"result[{idx}] missing keys: {missing}"


@pytest.mark.e2e
def test_wow_c_response_has_reproducibility_metadata(demo_server, api_post):
    """grid_resolution + timestamp must be present (audit trail for rehearsal)."""
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "logic3_active",
    })
    assert status == 200
    assert "grid_resolution" in body
    assert isinstance(body["grid_resolution"], int)
    assert body["grid_resolution"] > 0
    assert "timestamp" in body and isinstance(body["timestamp"], str)


@pytest.mark.e2e
@pytest.mark.parametrize("outcome", sorted(VALID_OUTCOMES))
def test_wow_c_all_valid_outcomes_return_200(demo_server, api_post, outcome):
    """Every documented outcome must be reachable (no regression in enum coverage)."""
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": outcome,
        "max_results": 1,
    })
    assert status == 200
    assert body["outcome"] == outcome


@pytest.mark.e2e
def test_wow_c_invalid_outcome_returns_structured_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "banana_outcome",
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body
    assert "Invalid outcome" in body["error"]
    # Error message must name the valid set so operators can self-recover.
    for valid in VALID_OUTCOMES:
        assert valid in body["error"]


@pytest.mark.e2e
def test_wow_c_missing_outcome_returns_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body


@pytest.mark.e2e
def test_wow_c_max_results_bound_is_respected(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 3,
    })
    assert status == 200
    assert len(body["results"]) <= 3

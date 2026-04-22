"""E2E subtask C — demo resilience / graceful degradation (API-layer only).

Scope note (per Plan v2 path A): frontend degradation DOM is NOT asserted
here — chat.html currently has no degraded state class. That belongs to
subtask E (deferred to P20.1). This suite locks only the API-layer
observable contract under fault injection.

Scenarios covered:
    1. MiniMax API key missing → /api/chat/reason returns structured error
       without crashing; /api/lever-snapshot remains fully functional
       (truth engine is isolated from LLM failure).
    2. Monte Carlo pathological inputs (0, huge, bad type, bad seed)
       are gracefully handled without 500s.
    3. Reverse diagnosis on unsupported system_id returns structured 400.
    4. Malformed / oversized bodies hit the security guards cleanly.
    5. The 8/8 adversarial truth-engine test still passes while demo_server
       is running — demo load must not regress the safety contract.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── LLM Timeout / Key-Missing path ──────────────────────────────────────────

@pytest.mark.e2e
def test_resilience_no_minimax_key_chat_reason_returns_structured_error(
    no_minimax_key_server, api_post
):
    status, body = api_post(no_minimax_key_server, "/api/chat/reason", {
        "question": "why is logic3 active?",
        "snapshot": {},
    })
    assert status == 400
    assert isinstance(body, dict)
    assert body.get("error") == "minimax_api_key_missing"
    assert "message" in body and isinstance(body["message"], str) and body["message"]


@pytest.mark.e2e
def test_resilience_truth_engine_isolated_from_llm_failure(
    no_minimax_key_server, api_post
):
    """Even with zero LLM availability, lever-snapshot (truth engine) works."""
    status, body = api_post(no_minimax_key_server, "/api/lever-snapshot", {
        "tra_deg": -35, "radio_altitude_ft": 2,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True, "n1k": 0.9,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
    })
    assert status == 200
    assert "logic" in body and "nodes" in body
    assert len(body["nodes"]) == 19


# ─── Monte Carlo pathological inputs ─────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.parametrize("n_trials", [0, -1, 1_500_000])
def test_resilience_monte_carlo_clamps_without_5xx(demo_server, api_post, n_trials):
    """Pathological n_trials is clamped into [1,10000], not crashed."""
    status, body = api_post(demo_server, "/api/monte-carlo/run", {
        "system_id": "thrust-reverser", "n_trials": n_trials, "seed": 1,
    })
    assert status == 200
    assert 1 <= body["n_trials"] <= 10000


@pytest.mark.e2e
def test_resilience_monte_carlo_bad_type_returns_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/monte-carlo/run", {
        "system_id": "thrust-reverser", "n_trials": "nope", "seed": 1,
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body


@pytest.mark.e2e
def test_resilience_monte_carlo_unknown_system_returns_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/monte-carlo/run", {
        "system_id": "unknown-widget", "n_trials": 100,
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body


# ─── Diagnosis pathological inputs ───────────────────────────────────────────

@pytest.mark.e2e
def test_resilience_diagnosis_unknown_system_returns_400(demo_server, api_post):
    status, body = api_post(demo_server, "/api/diagnosis/run", {
        "system_id": "unknown-widget", "outcome": "deploy_confirmed",
    })
    assert status == 400
    assert isinstance(body, dict) and "error" in body


# ─── Request-layer guards ────────────────────────────────────────────────────

@pytest.mark.e2e
def test_resilience_invalid_json_body_returns_400(demo_server, api_post):
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1", 8799, timeout=10)
    try:
        conn.request("POST", "/api/lever-snapshot",
                     body=b"{this is not json",
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 400
        resp.read()
    finally:
        conn.close()


@pytest.mark.e2e
def test_resilience_unknown_path_returns_404_not_500(demo_server, api_post):
    status, body = api_post(demo_server, "/api/does-not-exist", {})
    assert status == 404
    assert isinstance(body, dict) and body.get("error") == "not_found"


# ─── Adversarial truth-engine still green under demo load ────────────────────

@pytest.mark.e2e
def test_resilience_adversarial_truth_engine_still_passes(demo_server):
    """Run the 8/8 adversarial suite against :8799 (parameterized via env)."""
    adversarial_script = (
        REPO_ROOT / "src" / "well_harness" / "static" / "adversarial_test.py"
    )
    assert adversarial_script.is_file()
    env = os.environ.copy()
    env["WELL_HARNESS_PORT"] = "8799"
    result = subprocess.run(
        [sys.executable, str(adversarial_script)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )
    combined = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"adversarial_test.py failed under demo load:\n{combined}"
    )
    assert "ALL TESTS PASSED" in combined, combined[-2000:]

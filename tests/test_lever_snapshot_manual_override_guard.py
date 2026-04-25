"""E11-14 — server-side role guard for manual_feedback_override.

Locks the contract: /api/lever-snapshot requires actor + ticket_id +
manual_override_signoff when feedback_mode = manual_feedback_override.
Returns 409 Conflict when any are missing/malformed; auto_scrubber path
is unaffected.

Per E11-00-PLAN §3 row E11-14: this is the second line of defense paired
with E11-13's UI affordance. Truth-engine red line maintained — no
controller/runner/models/adapters changes.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest

from well_harness.demo_server import DemoRequestHandler


VALID_BASE_PAYLOAD = {
    "tra_deg": -14.0,
    "radio_altitude_ft": 5.0,
    "n1k": 0.5,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "deploy_position_percent": 95.0,
}

VALID_SIGNOFF = {
    "actor": "TestActor",
    "ticket_id": "WB-TEST-1",
    "manual_override_signoff": {
        "signed_by": "TestActor",
        "signed_at": "2026-04-25T12:00:00Z",
        "ticket_id": "WB-TEST-1",
    },
}


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(
        "POST",
        path,
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = connection.getresponse()
    body = json.loads(response.read().decode("utf-8") or "{}")
    return response.status, body


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


def test_auto_scrubber_unaffected_by_guard(server) -> None:
    """auto_scrubber path: no actor/ticket required, returns 200."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "auto_scrubber"}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 200, f"auto_scrubber should bypass guard, got {status}: {body}"
    assert "nodes" in body


def test_manual_override_with_valid_signoff_returns_200(server) -> None:
    """manual_feedback_override + valid sign-off triplet → 200."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override", **VALID_SIGNOFF}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 200, f"valid sign-off should pass guard, got {status}: {body}"


def test_manual_override_missing_actor_returns_409(server) -> None:
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["actor"] = ""
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("error") == "manual_override_unsigned"
    assert body.get("field") == "actor"


def test_manual_override_missing_ticket_id_returns_409(server) -> None:
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["ticket_id"] = ""
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("error") == "manual_override_unsigned"
    assert body.get("field") == "ticket_id"


def test_manual_override_missing_signoff_object_returns_409(server) -> None:
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload["actor"] = "TestActor"
    payload["ticket_id"] = "WB-TEST-1"
    # no manual_override_signoff key at all
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("error") == "manual_override_unsigned"
    assert body.get("field") == "manual_override_signoff"


def test_manual_override_signoff_missing_signed_by_returns_409(server) -> None:
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["manual_override_signoff"] = {**VALID_SIGNOFF["manual_override_signoff"], "signed_by": ""}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("field") == "manual_override_signoff.signed_by"


def test_manual_override_signoff_ticket_mismatch_returns_409(server) -> None:
    """signoff.ticket_id MUST equal request ticket_id; mismatch is rejected."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["manual_override_signoff"] = {
        **VALID_SIGNOFF["manual_override_signoff"],
        "ticket_id": "WB-DIFFERENT",
    }
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("field") == "manual_override_signoff.ticket_id"


def test_remediation_message_present_on_409(server) -> None:
    """409 response includes a remediation message pointing to Approval Center."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert "Approval Center" in body.get("remediation", "")
    assert "auto_scrubber" in body.get("remediation", "")


# ─── P2 R1 IMPORTANT #5: contract gap tests (R2 fixes) ───────────────────────


def test_actor_signed_by_mismatch_returns_409(server) -> None:
    """P2 BLOCKER #1 R2 fix: actor must equal manual_override_signoff.signed_by.

    Without this binding, an attacker submits actor=Mallory + signed_by=Kogami
    (matching ticket_id) and impersonates Kogami. Live-verified by P2 in R1.
    """
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["actor"] = "Mallory"  # different from signed_by="TestActor"
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("field") == "actor"
    assert "impersonation" in body.get("message", "")


def test_400_precedes_409_when_other_fields_malformed(server) -> None:
    """P2 IMPORTANT #3 R2 fix: 400 (malformed) precedes 409 (unsigned).

    A request with malformed deploy_position_percent + missing signoff used
    to return 409 manual_override_unsigned (masking the real 400). After
    R2 the guard runs after structural parsing; malformed numeric fields
    surface as 400 first.
    """
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload["deploy_position_percent"] = "oops"  # malformed
    # signoff intentionally missing
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 400, (
        f"Expected 400 for malformed payload (precedes 409), got {status}: {body}"
    )
    assert body.get("error") == "invalid_lever_snapshot_input"


def test_residual_risk_disclosure_present_on_409(server) -> None:
    """P2 IMPORTANT #4 R2 mitigation: 409 response discloses replay residual risk.

    Replay/nonce/freshness hardening is deferred to E11-16. The guard
    response must explicitly disclose this so callers don't mistake
    structural validation for latched authorization.
    """
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    risk = body.get("residual_risk", "")
    assert "Replay" in risk or "replay" in risk
    assert "E11-16" in risk


def test_signoff_non_dict_returns_409(server) -> None:
    """signoff field must be a dict; string/list/null all 409."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload["actor"] = "TestActor"
    payload["ticket_id"] = "WB-TEST-1"
    payload["manual_override_signoff"] = "not-a-dict"
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("field") == "manual_override_signoff"


def test_signoff_signed_at_empty_returns_409(server) -> None:
    """signed_at must be non-empty string. Note: freshness validation is
    E11-16 scope; this only locks the structural non-empty check."""
    payload = {**VALID_BASE_PAYLOAD, "feedback_mode": "manual_feedback_override"}
    payload.update(VALID_SIGNOFF)
    payload["manual_override_signoff"] = {**VALID_SIGNOFF["manual_override_signoff"], "signed_at": ""}
    status, body = _post(server, "/api/lever-snapshot", payload)
    assert status == 409
    assert body.get("field") == "manual_override_signoff.signed_at"


# ─── P2 R1 BLOCKER #2 R2 fix: /api/fantui/set_vdt test-probe acknowledgment ──


def test_set_vdt_requires_test_probe_acknowledgment(server) -> None:
    """P2 BLOCKER #2 R2 fix: /api/fantui/set_vdt is a test probe; without
    explicit test_probe_acknowledgment=true it returns 409 explaining the
    bypass and pointing callers to /api/lever-snapshot for authoritative
    manual feedback."""
    status, body = _post(server, "/api/fantui/set_vdt", {"deploy_position_percent": 73})
    assert status == 409
    assert body.get("error") == "test_probe_unacknowledged"
    assert "test probe" in body.get("message", "").lower()
    assert "/api/lever-snapshot" in body.get("message", "")


def test_set_vdt_with_acknowledgment_succeeds(server) -> None:
    """When the caller acknowledges the bypass nature, set_vdt works as before."""
    status, body = _post(
        server,
        "/api/fantui/set_vdt",
        {"deploy_position_percent": 73, "test_probe_acknowledgment": True},
    )
    assert status == 200
    assert body.get("deploy_position_percent") == pytest.approx(73, abs=0.01)

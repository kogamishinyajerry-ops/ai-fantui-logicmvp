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

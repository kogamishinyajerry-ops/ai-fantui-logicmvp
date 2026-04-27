"""P49-01a — accept endpoint spawns skill_executor.

Locks down: when a proposal flips OPEN→ACCEPTED via the workbench
HTTP endpoint, the demo_server invokes the spawner. Behavior is
gated by WORKBENCH_AUTO_SPAWN_EXECUTOR; the response carries a
`spawn` field so callers can observe what happened.

These tests stub the actual subprocess fork — they verify the
*plumbing* between accept-handler and spawner, not Popen itself
(that's covered by test_skill_executor_p49_01a_spawner.py).
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    create_proposal,
    interpret_suggestion_text,
)
from well_harness.skill_executor.executor_spawner import (
    SpawnResult,
    SpawnStatus,
)


@pytest.fixture(autouse=True)
def _isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "dev_queue"))
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "skill_executions")
    )
    yield


def _start_demo_server() -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture
def server():
    srv = _start_demo_server()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post_json(server, path, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    payload = json.dumps(body) if body is not None else ""
    headers = {"Content-Type": "application/json"} if body is not None else {}
    conn.request("POST", path, body=payload, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(raw) if raw else {}


def _make_open_proposal(text="L2 SW2 应该 tighten") -> dict:
    interp = interpret_suggestion_text(text)
    return create_proposal(
        source_text=text,
        interpretation=interp,
        author_name="Engineer-A",
        author_role="ENGINEER",
        ticket_id="WB-P49-01A-TEST",
    )


# ─── 1. Default OFF — env var not set ────────────────────────────────


def test_accept_response_includes_spawn_disabled_by_default(
    server, monkeypatch
):
    monkeypatch.delenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", raising=False)
    p = _make_open_proposal()
    status, body = _post_json(server, f"/api/proposals/{p['id']}/accept")
    assert status == 200
    assert body["status"] == "ACCEPTED"
    assert "spawn" in body
    assert body["spawn"]["status"] == "disabled"


# ─── 2. Enabled — accept handler spawns and surfaces status ─────────


def test_accept_with_spawn_enabled_surfaces_spawned_status(
    server, monkeypatch
):
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")

    captured = {}

    def fake_spawn(proposal_id, *, repo_root):
        captured["proposal_id"] = proposal_id
        captured["repo_root"] = repo_root
        return SpawnResult(
            status=SpawnStatus.SPAWNED,
            proposal_id=proposal_id,
            pid=99999,
            marker_path=Path("/tmp/fake.spawn"),
            log_path=Path("/tmp/fake.log"),
            cmd=["python", "-m", "well_harness.skill_executor"],
        )

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        fake_spawn,
    )

    p = _make_open_proposal()
    status, body = _post_json(server, f"/api/proposals/{p['id']}/accept")
    assert status == 200
    assert body["spawn"]["status"] == "spawned"
    assert body["spawn"]["pid"] == 99999
    assert body["spawn"]["log"] == "/tmp/fake.log"
    assert captured["proposal_id"] == p["id"]


# ─── 3. Reject does NOT spawn ───────────────────────────────────────


def test_reject_response_has_no_spawn_field(server, monkeypatch):
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")

    def must_not_be_called(*a, **kw):
        raise AssertionError("spawner must not run on reject")

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        must_not_be_called,
    )

    p = _make_open_proposal()
    status, body = _post_json(server, f"/api/proposals/{p['id']}/reject")
    assert status == 200
    assert body["status"] == "REJECTED"
    assert "spawn" not in body


# ─── 4. Spawner OSError doesn't fail the accept ─────────────────────


def test_spawn_failure_returns_200_with_error_in_spawn_field(
    server, monkeypatch
):
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")

    from well_harness.skill_executor.executor_spawner import SpawnerError

    def boom(*a, **kw):
        raise SpawnerError("simulated fork failure")

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        boom,
    )

    p = _make_open_proposal()
    status, body = _post_json(server, f"/api/proposals/{p['id']}/accept")
    # The proposal IS accepted regardless — spawn is best-effort
    assert status == 200
    assert body["status"] == "ACCEPTED"
    assert body["spawn"]["status"] == "error"
    assert "simulated fork failure" in body["spawn"]["error"]


# ─── 5. Already-terminal proposal: no spawn ─────────────────────────


def test_re_accepting_already_accepted_does_not_spawn(server, monkeypatch):
    monkeypatch.setenv("WORKBENCH_AUTO_SPAWN_EXECUTOR", "1")
    spawn_calls = {"n": 0}

    def fake_spawn(proposal_id, *, repo_root):
        spawn_calls["n"] += 1
        return SpawnResult(
            status=SpawnStatus.SPAWNED,
            proposal_id=proposal_id,
            pid=1,
        )

    monkeypatch.setattr(
        "well_harness.demo_server._spawn_executor_for_proposal",
        fake_spawn,
    )

    p = _make_open_proposal()
    # First accept should spawn
    _post_json(server, f"/api/proposals/{p['id']}/accept")
    assert spawn_calls["n"] == 1
    # Second accept hits 409 already_terminal — must NOT re-spawn
    status2, body2 = _post_json(server, f"/api/proposals/{p['id']}/accept")
    assert status2 == 409
    assert spawn_calls["n"] == 1

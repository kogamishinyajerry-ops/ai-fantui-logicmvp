"""P47-03 — multi-agent end-to-end loop integration test.

User direction (2026-04-27, Q3): test the full engineer → reviewer →
executor → revert flow as one continuous HTTP integration test, so a
regression in any single step (interpret-suggestion / create proposal /
accept / write brief / record landed SHA / propose revert) breaks CI
loudly.

Three roles, all simulated via HTTP against a live demo_server in a
thread:
  - **Engineer**  — POST /api/workbench/interpret-suggestion, then
                    POST /api/proposals (rules strategy; LLM path is
                    covered by p45-03 and skipped here to keep CI
                    deterministic and offline).
  - **Reviewer**  — POST /api/proposals/<id>/accept (accept), or
                    POST /api/proposals/<id>/reject.
  - **Executor**  — POST /api/proposals/<id>/landed (after a real
                    /gsd-execute-phase-from-brief run; here we just
                    record a fake SHA so the inbox lights up the
                    revert affordance).

The companion "real subagent" e2e is a manual runbook at
`docs/runbooks/multi_agent_e2e.md` (P47-03b); it exercises the same
endpoints through actual Claude subagents but is too budget-heavy to
run on every CI tick.
"""

from __future__ import annotations

import http.client
import json
import re
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    dev_queue_dir,
    proposals_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ─── Test fixtures ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _isolate_dirs(tmp_path, monkeypatch):
    """Each test gets a clean proposals + dev-queue tree so the live
    .planning/ never gets polluted."""
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "props"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "queue"))
    yield


def _start_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


@pytest.fixture
def server():
    s, t = _start_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


def _post(server, path: str, body: dict | None) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    raw = json.dumps(body or {}).encode("utf-8")
    conn.request(
        "POST",
        path,
        body=raw,
        headers={"Content-Type": "application/json", "Content-Length": str(len(raw))},
    )
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        parsed = {"raw": data}
    return resp.status, parsed


def _get(server, path: str) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        parsed = {"raw": data}
    return resp.status, parsed


# ─── Helper: full role-flow primitives ────────────────────────────────


def _engineer_interpret(server, *, text: str, system_id: str = "thrust-reverser") -> dict:
    status, body = _post(
        server,
        "/api/workbench/interpret-suggestion",
        {
            "text": text,
            "system_id": system_id,
            "strategy": "rules",
        },
    )
    assert status == 200, body
    return body


def _engineer_submit(
    server,
    *,
    text: str,
    interpretation: dict,
    author: str = "Alice",
    system_id: str = "thrust-reverser",
) -> dict:
    status, body = _post(
        server,
        "/api/proposals",
        {
            "source_text": text,
            "interpretation": interpretation,
            "author_name": author,
            "author_role": "ENGINEER",
            "system_id": system_id,
        },
    )
    assert status == 201, body
    return body


def _reviewer_accept(server, proposal_id: str, *, actor: str = "Reviewer") -> dict:
    status, body = _post(
        server,
        f"/api/proposals/{proposal_id}/accept",
        {"actor": actor},
    )
    assert status == 200, body
    return body


def _executor_record_landed(server, proposal_id: str, *, sha: str) -> dict:
    status, body = _post(
        server,
        f"/api/proposals/{proposal_id}/landed",
        {"sha": sha, "actor": "claude-code-executor"},
    )
    assert status == 200, body
    return body


def _engineer_request_revert(server, proposal_id: str, *, author: str = "Bob") -> dict:
    status, body = _post(
        server,
        f"/api/proposals/{proposal_id}/propose-revert",
        {"author_name": author},
    )
    assert status == 201, body
    return body


# ─── 1. Each role's HTTP primitive in isolation ───────────────────────


def test_engineer_interpret_returns_structured_interpretation(server):
    interp = _engineer_interpret(server, text="L2 SW2 should tighten")
    # Structural smoke: rules strategy must return change_kind +
    # at least one affected_gate.
    assert "change_kind" in interp
    assert isinstance(interp.get("affected_gates"), list)


def test_engineer_can_submit_proposal(server):
    interp = _engineer_interpret(server, text="L2 SW2 should tighten")
    rec = _engineer_submit(server, text="L2 SW2 should tighten", interpretation=interp)
    assert rec["status"] == "OPEN"
    assert rec["kind"] == "modify"
    assert rec["author_name"] == "Alice"


def test_reviewer_can_accept(server):
    interp = _engineer_interpret(server, text="L2 SW2 should tighten")
    rec = _engineer_submit(server, text="L2 SW2 should tighten", interpretation=interp)
    accepted = _reviewer_accept(server, rec["id"])
    assert accepted["status"] == "ACCEPTED"
    # Side-effect: dev-queue brief must exist.
    brief = dev_queue_dir() / f"{rec['id']}.md"
    assert brief.is_file()


def test_executor_can_record_landed_sha(server):
    interp = _engineer_interpret(server, text="L2 SW2 should tighten")
    rec = _engineer_submit(server, text="L2 SW2 should tighten", interpretation=interp)
    _reviewer_accept(server, rec["id"])
    landed = _executor_record_landed(server, rec["id"], sha="abc1234")
    assert landed["landed_truth_sha"] == "abc1234"
    # The landed event must show up in the audit trail.
    actions = [h["action"] for h in landed.get("history", [])]
    assert "submitted" in actions
    assert "accepted" in actions
    assert "landed" in actions


def test_engineer_can_request_revert_after_landed(server):
    interp = _engineer_interpret(server, text="L2 SW2 should tighten")
    rec = _engineer_submit(server, text="L2 SW2 should tighten", interpretation=interp)
    _reviewer_accept(server, rec["id"])
    _executor_record_landed(server, rec["id"], sha="abc1234")
    revert = _engineer_request_revert(server, rec["id"], author="Bob")
    assert revert["kind"] == "revert"
    assert revert["revert_of_proposal_id"] == rec["id"]
    assert revert["revert_target_sha"] == "abc1234"
    assert revert["status"] == "OPEN"


# ─── 2. Full happy-path E2E loop in one test ──────────────────────────


def test_e2e_full_modify_loop(server):
    """Engineer submits → reviewer accepts → executor lands →
    workbench shows landed proposal in inbox with the right SHA."""
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    proposal = _engineer_submit(
        server,
        text="L2 SW2 应该 tighten",
        interpretation=interp,
        author="Alice",
    )
    _reviewer_accept(server, proposal["id"], actor="Kogami")
    _executor_record_landed(server, proposal["id"], sha="ec6f4fc")

    # Engineer reloads inbox — proposal should be ACCEPTED + landed.
    status, body = _get(server, "/api/proposals")
    assert status == 200
    proposals = body["proposals"] if isinstance(body, dict) and "proposals" in body else body
    assert isinstance(proposals, list)
    found = next((p for p in proposals if p["id"] == proposal["id"]), None)
    assert found is not None
    assert found["status"] == "ACCEPTED"
    assert found["landed_truth_sha"] == "ec6f4fc"
    assert found["kind"] == "modify"


def test_e2e_full_modify_then_revert_loop(server):
    """Same as above, then engineer proposes revert → reviewer
    accepts revert → executor records revert SHA → original
    proposal is "shadowed" by the revert chain."""
    # Modify arc
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    orig = _engineer_submit(server, text="L2 SW2 应该 tighten", interpretation=interp)
    _reviewer_accept(server, orig["id"])
    _executor_record_landed(server, orig["id"], sha="abc1234")

    # Revert arc
    revert = _engineer_request_revert(server, orig["id"], author="Bob")
    accepted_revert = _reviewer_accept(server, revert["id"], actor="Kogami")
    assert accepted_revert["kind"] == "revert"
    revert_brief = dev_queue_dir() / f"{revert['id']}.md"
    assert revert_brief.is_file()
    body = revert_brief.read_text(encoding="utf-8")
    # Brief must reference both the original and the target SHA.
    assert orig["id"] in body
    assert "abc1234" in body
    # And tell the executor NOT to use blind git revert (Q2 rule).
    assert "DO NOT just run" in body or "do not just run" in body.lower()

    # Executor simulates merging the revert PR
    landed_revert = _executor_record_landed(server, revert["id"], sha="def5678")
    assert landed_revert["landed_truth_sha"] == "def5678"


# ─── 3. State-of-world payload stays consistent through the loop ──────


def test_state_of_world_namespaces_consistent_during_loop(server):
    status, payload = _get(server, "/api/workbench/state-of-world")
    assert status == 200
    namespaces_pre = [ns["namespace"] for ns in payload["panel_namespaces"]]

    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    proposal = _engineer_submit(server, text="x", interpretation=interp)
    _reviewer_accept(server, proposal["id"])
    _executor_record_landed(server, proposal["id"], sha="abc1234")

    status, payload = _get(server, "/api/workbench/state-of-world")
    assert status == 200
    namespaces_post = [ns["namespace"] for ns in payload["panel_namespaces"]]
    # Same namespaces, same order — proposal lifecycle does NOT
    # change the truth-engine commit graph (those endpoints are
    # write-only on the proposal side).
    assert namespaces_pre == namespaces_post == [
        "logic_truth",
        "requirements",
        "simulation_workbench",
    ]


# ─── 4. Multi-system flows ─────────────────────────────────────────────


@pytest.mark.parametrize("system_id", ["thrust-reverser", "c919-etras"])
def test_e2e_multi_system_modify_loop(server, system_id):
    """Both demoed systems can drive the full loop. Frozen systems
    (landing-gear / bleed-air-valve) are out of dropdown but their
    backend still routes — that's covered by the dropdown-freeze
    test, not here."""
    interp = _engineer_interpret(server, text="something should tighten", system_id=system_id)
    proposal = _engineer_submit(
        server,
        text="something should tighten",
        interpretation=interp,
        system_id=system_id,
    )
    assert proposal["system_id"] == system_id
    _reviewer_accept(server, proposal["id"])
    _executor_record_landed(server, proposal["id"], sha="aaaa1111")
    revert = _engineer_request_revert(server, proposal["id"])
    assert revert["system_id"] == system_id  # revert inherits system


# ─── 5. Multiple engineers don't collide ───────────────────────────────


def test_concurrent_independent_proposals_keep_distinct_ids(server):
    """Two near-simultaneous submissions from different engineers
    must produce distinct proposal ids and independent records.
    Microsecond resolution in the id generator (P44-03 fix) is
    what guarantees this."""
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    rec_a = _engineer_submit(server, text="A", interpretation=interp, author="Alice")
    rec_b = _engineer_submit(server, text="B", interpretation=interp, author="Bob")
    assert rec_a["id"] != rec_b["id"]
    # Both must read back independently.
    status, body = _get(server, "/api/proposals")
    proposals = body["proposals"] if isinstance(body, dict) and "proposals" in body else body
    ids = {p["id"] for p in proposals}
    assert rec_a["id"] in ids
    assert rec_b["id"] in ids


# ─── 6. Revert chain audit trail ───────────────────────────────────────


def test_revert_proposal_audit_trail_links_back_to_origin(server):
    """The revert proposal's source_text must contain the original id
    so a reader of just the JSON record can follow the chain without
    cross-referencing two files."""
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    orig = _engineer_submit(server, text="L2 SW2 应该 tighten", interpretation=interp)
    _reviewer_accept(server, orig["id"])
    _executor_record_landed(server, orig["id"], sha="abc1234")
    revert = _engineer_request_revert(server, orig["id"])
    assert orig["id"] in revert["source_text"]
    assert "abc1234" in revert["source_text"]
    # change_kind reflects the revert kind too
    assert revert["interpretation"]["change_kind"] == "revert"


# ─── 7. Reject path doesn't trigger landed/revert affordances ─────────


def test_rejected_proposal_cannot_be_landed(server):
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    rec = _engineer_submit(server, text="x", interpretation=interp)
    status, body = _post(server, f"/api/proposals/{rec['id']}/reject", {"actor": "R"})
    assert status == 200
    # Now the executor tries to land it — should 409.
    status, body = _post(
        server,
        f"/api/proposals/{rec['id']}/landed",
        {"sha": "abc1234"},
    )
    assert status == 409


def test_rejected_proposal_cannot_be_reverted(server):
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    rec = _engineer_submit(server, text="x", interpretation=interp)
    _post(server, f"/api/proposals/{rec['id']}/reject", {"actor": "R"})
    status, body = _post(
        server,
        f"/api/proposals/{rec['id']}/propose-revert",
        {},
    )
    # Original is REJECTED, not ACCEPTED → 409 not_landed
    assert status == 409
    assert body["error"] == "original_not_landed"


# ─── 8. Smoke: brief schema fields the executor expects are present ───


def test_modify_brief_carries_executor_handoff_fields(server):
    interp = _engineer_interpret(server, text="L2 SW2 应该 tighten")
    rec = _engineer_submit(server, text="L2 SW2 应该 tighten", interpretation=interp)
    _reviewer_accept(server, rec["id"], actor="Kogami")
    brief = (dev_queue_dir() / f"{rec['id']}.md").read_text(encoding="utf-8")
    # Schema-version comment for forward compat
    assert "dev_queue brief schema v" in brief
    # Critical handoff fields the skill's Step 2 reads
    assert "Affected gates" in brief
    assert "Change kind" in brief
    assert "Submitted by" in brief
    # Step 8 recipe
    assert "/api/proposals/" in brief
    assert "/landed" in brief


# ─── 9. Sanity: docstring-locked test count for run-output checks ─────


def test_p47_03_module_test_count_baseline():
    """Lock the test count in the docstring + this assertion so an
    accidental delete of a coverage test fires a clear failure."""
    # 9 sections; not all sections produce equal counts. The most
    # robust pin is "this module reports >= N tests at collect
    # time"; the parametrized multi_system test contributes 2.
    # Counting by sections: 5 + 2 + 1 + 2 + 1 + 1 + 2 + 1 = 15
    # plus this self-test = 16 collected. Use a lower-bound pin so
    # adding tests later doesn't break this.
    import importlib
    module = importlib.import_module(__name__.replace(".", "/").replace("/", "."))
    test_funcs = [
        attr for attr in dir(module)
        if attr.startswith("test_") and callable(getattr(module, attr))
    ]
    assert len(test_funcs) >= 15, (
        f"P47-03 module dropped below 15 tests ({len(test_funcs)}); "
        f"the multi-agent loop coverage may be incomplete"
    )

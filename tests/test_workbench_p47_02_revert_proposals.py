"""P47-02 — revert-as-proposal + landed-SHA tracking.

User direction (2026-04-27, Q2): revert MUST go through the full
proposal flow (suggestion → review → executor), not be a one-click
git-revert. This phase wires:

  1. proposals carry kind ∈ {modify, revert} and a landed_truth_sha
     field (set by /landed once the executor merges the truth-engine PR)
  2. POST /api/proposals/<id>/landed records the merge SHA
  3. POST /api/proposals/<id>/propose-revert creates a NEW proposal
     with kind="revert" and revert_target_sha pointing at the original
     commit; that proposal walks the standard accept-flow and produces
     a revert-flavored dev-queue brief

The skill (gsd-execute-phase-from-brief) reads the revert brief, plans
the reversal, asks the engineer, edits, and merges — same plan/ask/edit
machinery as a modify, just with `<target_sha>~1` as ground truth.

Locks down:
  - schema additions don't break create_proposal call sites that
    pre-date P47-02 (they default kind="modify")
  - landed-SHA is idempotent (same SHA twice is OK; different SHA
    rejected)
  - duplicate revert proposals targeting the same SHA are rejected
  - HTTP endpoints return correct status codes for each error path
  - revert dev-queue brief points to the parent SHA, references the
    original PROP id, and tells the executor to plan/ask/edit (NOT
    blind git revert)
"""

from __future__ import annotations

import http.client
import json
import os
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    create_proposal,
    create_revert_proposal,
    dev_queue_dir,
    proposals_dir,
    record_proposal_landed,
    update_proposal_status,
    write_dev_queue_brief,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


@pytest.fixture(autouse=True)
def _isolate_dirs(tmp_path, monkeypatch):
    """Each test gets its own proposals_dir + dev_queue_dir so the
    real .planning/ tree is never touched."""
    props = tmp_path / "props"
    queue = tmp_path / "queue"
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(props))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(queue))
    yield


def _make_modify_record(*, source_text="L2 should tighten") -> dict:
    return create_proposal(
        source_text=source_text,
        interpretation={
            "change_kind": "tighten_condition",
            "affected_gates": ["L2"],
            "target_signals": ["SW2"],
            "summary_zh": "紧 L2 SW2",
            "summary_en": "tighten L2 SW2",
            "confidence": 0.85,
        },
        author_name="Alice",
    )


def _accept_and_land(record: dict, sha: str = "abc1234ef") -> dict:
    accepted, _ = update_proposal_status(record["id"], new_status="ACCEPTED", actor="Reviewer")
    landed, err = record_proposal_landed(record["id"], sha=sha)
    assert err is None
    return landed


# ─── 1. Schema additions don't break old call sites ───────────────────


def test_create_proposal_default_kind_is_modify():
    rec = _make_modify_record()
    assert rec["kind"] == "modify"
    assert rec["revert_of_proposal_id"] is None
    assert rec["revert_target_sha"] is None
    assert rec["landed_truth_sha"] is None


def test_create_proposal_invalid_kind_raises():
    with pytest.raises(ValueError):
        create_proposal(
            source_text="x",
            interpretation={},
            kind="explode",
        )


def test_create_proposal_revert_requires_origin_and_target_sha():
    with pytest.raises(ValueError):
        create_proposal(
            source_text="x",
            interpretation={},
            kind="revert",
        )
    with pytest.raises(ValueError):
        create_proposal(
            source_text="x",
            interpretation={},
            kind="revert",
            revert_of_proposal_id="PROP-foo",
            # missing revert_target_sha
        )


# ─── 2. record_proposal_landed ─────────────────────────────────────────


def test_record_landed_happy_path():
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    landed, err = record_proposal_landed(rec["id"], sha="abc1234")
    assert err is None
    assert landed["landed_truth_sha"] == "abc1234"
    assert any(h["action"] == "landed" for h in landed["history"])


def test_record_landed_rejects_unknown_proposal():
    landed, err = record_proposal_landed("PROP-does-not-exist", sha="abc1234")
    assert landed is None
    assert err == "not_found"


def test_record_landed_rejects_non_accepted_proposal():
    rec = _make_modify_record()
    # Still OPEN — landed is illegal here.
    landed, err = record_proposal_landed(rec["id"], sha="abc1234")
    assert err == "wrong_status"


@pytest.mark.parametrize("bad_sha", ["", "   ", "xyz", "abc12", "g" * 7, "abc1234!"])
def test_record_landed_rejects_invalid_sha(bad_sha):
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    _, err = record_proposal_landed(rec["id"], sha=bad_sha)
    assert err == "invalid_sha"


def test_record_landed_idempotent_same_sha():
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    record_proposal_landed(rec["id"], sha="abc1234")
    again, err = record_proposal_landed(rec["id"], sha="abc1234")
    assert err is None
    assert again["landed_truth_sha"] == "abc1234"


def test_record_landed_rejects_different_sha():
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    record_proposal_landed(rec["id"], sha="abc1234")
    again, err = record_proposal_landed(rec["id"], sha="def5678")
    assert err == "already_landed"


# ─── 3. create_revert_proposal ─────────────────────────────────────────


def test_revert_proposal_happy_path():
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234")
    rev, err = create_revert_proposal(orig["id"], author_name="Reviewer")
    assert err is None
    assert rev["kind"] == "revert"
    assert rev["revert_of_proposal_id"] == orig["id"]
    assert rev["revert_target_sha"] == "abc1234"
    assert rev["status"] == "OPEN"
    # Inherits system + ticket from the original
    assert rev["system_id"] == orig["system_id"]
    assert rev["ticket_id"] == orig["ticket_id"]
    # Source text references the original explicitly so an audit trail
    # reader can follow the chain without opening the JSON.
    assert orig["id"] in rev["source_text"]


def test_revert_proposal_rejects_unknown_origin():
    rev, err = create_revert_proposal("PROP-unknown")
    assert rev is None
    assert err == "not_found"


def test_revert_proposal_rejects_non_accepted_origin():
    orig = _make_modify_record()  # Still OPEN
    rev, err = create_revert_proposal(orig["id"])
    assert rev is None
    assert err == "not_landed"


def test_revert_proposal_rejects_origin_without_landed_sha():
    orig = _make_modify_record()
    update_proposal_status(orig["id"], new_status="ACCEPTED", actor="R")
    # Skip landed step
    rev, err = create_revert_proposal(orig["id"])
    assert rev is None
    assert err == "not_landed"


def test_revert_proposal_rejects_duplicate():
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234")
    create_revert_proposal(orig["id"])
    rev2, err = create_revert_proposal(orig["id"])
    assert rev2 is None
    assert err == "already_reverted"


def test_revert_proposal_allowed_after_first_revert_rejected():
    """If the first revert ticket gets REJECTED, a second revert
    proposal targeting the same SHA should be allowed (the revert
    decision was never actually approved)."""
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234")
    rev1, _ = create_revert_proposal(orig["id"])
    update_proposal_status(rev1["id"], new_status="REJECTED", actor="R")
    rev2, err = create_revert_proposal(orig["id"])
    assert err is None
    assert rev2["kind"] == "revert"


# ─── 4. Dev-queue brief for revert kind ───────────────────────────────


def test_revert_brief_references_original_and_target_sha():
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234")
    rev, _ = create_revert_proposal(orig["id"])
    update_proposal_status(rev["id"], new_status="ACCEPTED", actor="Reviewer")
    brief_path = dev_queue_dir() / f"{rev['id']}.md"
    assert brief_path.is_file()
    body = brief_path.read_text(encoding="utf-8")
    # Distinct title flag so a glance at the brief tells the executor
    # this is a revert task.
    assert "REVERT" in body
    # Must point at the original proposal id and the target SHA.
    assert orig["id"] in body
    assert "abc1234" in body
    # Must instruct the executor to use plan/ask/edit (Q2(b)), not
    # blind git revert.
    assert "DO NOT just run" in body or "do not just run" in body.lower()


def test_modify_brief_carries_landed_sha_recording_recipe():
    """The modify brief must teach the executor how to call the new
    /landed endpoint after PR merge — without that, the revert path
    never lights up."""
    orig = _make_modify_record()
    update_proposal_status(orig["id"], new_status="ACCEPTED", actor="R")
    brief_path = dev_queue_dir() / f"{orig['id']}.md"
    body = brief_path.read_text(encoding="utf-8")
    assert "/landed" in body
    assert orig["id"] in body


# ─── 5. HTTP endpoints ─────────────────────────────────────────────────


def _start_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _post(server, path: str, body: dict | None) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    payload = json.dumps(body or {}).encode("utf-8")
    conn.request(
        "POST",
        path,
        body=payload,
        headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
    )
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"raw": raw}
    return resp.status, parsed


@pytest.fixture
def server():
    s, t = _start_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


def test_http_landed_happy_path(server):
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    status, body = _post(
        server,
        f"/api/proposals/{rec['id']}/landed",
        {"sha": "abc1234", "actor": "claude-code"},
    )
    assert status == 200, body
    assert body["landed_truth_sha"] == "abc1234"


def test_http_landed_rejects_open_proposal(server):
    rec = _make_modify_record()
    status, body = _post(
        server,
        f"/api/proposals/{rec['id']}/landed",
        {"sha": "abc1234"},
    )
    assert status == 409
    assert body["error"] == "proposal_not_accepted"


def test_http_landed_rejects_invalid_sha(server):
    rec = _make_modify_record()
    update_proposal_status(rec["id"], new_status="ACCEPTED", actor="R")
    status, body = _post(
        server,
        f"/api/proposals/{rec['id']}/landed",
        {"sha": "not-hex"},
    )
    assert status == 400
    assert body["error"] == "invalid_sha_format"


def test_http_landed_rejects_unknown_proposal(server):
    status, body = _post(
        server,
        "/api/proposals/PROP-does-not-exist/landed",
        {"sha": "abc1234"},
    )
    assert status == 404


def test_http_propose_revert_happy_path(server):
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234ef")
    status, body = _post(
        server,
        f"/api/proposals/{orig['id']}/propose-revert",
        {"author_name": "Reviewer"},
    )
    assert status == 201, body
    assert body["kind"] == "revert"
    assert body["revert_of_proposal_id"] == orig["id"]
    assert body["revert_target_sha"] == "abc1234ef"


def test_http_propose_revert_rejects_unlanded(server):
    orig = _make_modify_record()
    update_proposal_status(orig["id"], new_status="ACCEPTED", actor="R")
    # No landed call made.
    status, body = _post(server, f"/api/proposals/{orig['id']}/propose-revert", {})
    assert status == 409
    assert body["error"] == "original_not_landed"


def test_http_propose_revert_rejects_duplicate(server):
    orig = _make_modify_record()
    _accept_and_land(orig, sha="abc1234")
    _post(server, f"/api/proposals/{orig['id']}/propose-revert", {})
    status, body = _post(server, f"/api/proposals/{orig['id']}/propose-revert", {})
    assert status == 409
    assert body["error"] == "revert_already_in_flight"


# ─── 6. Frontend (smoke checks against the static files) ──────────────


def test_workbench_js_carries_propose_revert_function():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function proposeRevertProposal" in js
    # Wires the correct endpoint pattern
    assert "/propose-revert" in js


def test_workbench_js_renders_revert_kind_badge():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    # Badge uses the data-proposal-kind attribute
    assert 'data-proposal-kind="revert"' in js


def test_workbench_js_renders_landed_sha_chip():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "landed_truth_sha" in js


def test_workbench_js_propose_revert_button_only_for_landed_modify():
    """The button must be conditional on kind=modify + ACCEPTED + landed.
    Smoke check: the rendered template uses all three predicates."""
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert 'kind === "modify"' in js
    assert 'p.status === "ACCEPTED"' in js
    assert "p.landed_truth_sha" in js


def test_workbench_css_carries_revert_styles():
    css = WORKBENCH_CSS.read_text(encoding="utf-8")
    assert ".workbench-annotation-inbox-item-kind-badge" in css
    assert ".workbench-annotation-inbox-item-revert-banner" in css
    assert ".workbench-propose-revert-button" in css
    # Per-kind row left-border styling
    assert '.workbench-annotation-inbox-item[data-proposal-kind="revert"]' in css

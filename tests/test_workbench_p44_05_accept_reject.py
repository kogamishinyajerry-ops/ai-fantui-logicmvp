"""P44-05 — accept / reject + dev-queue handoff.

Reviewer-side mutations on a proposal:
  POST /api/proposals/<id>/accept  →  status OPEN → ACCEPTED, history
                                      append, dev-queue brief written
  POST /api/proposals/<id>/reject  →  status OPEN → REJECTED, history
                                      append (with optional note), no
                                      dev-queue brief

Truth-engine red line: this is still adapter-only. Status flips and
the dev-queue markdown both live outside controller / runner / models /
adapters / demo_server's truth surface. The actual code change still
goes through normal git/PR review by Claude Code's /gsd-execute-phase
in a separate session.
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
    create_proposal,
    dev_queue_dir,
    interpret_suggestion_text,
    update_proposal_status,
    write_dev_queue_brief,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── Test isolation: every test gets fresh proposals + dev_queue dirs.


@pytest.fixture(autouse=True)
def _isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "dev_queue"))
    yield


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


@pytest.fixture
def server():
    srv, _ = _start_demo_server()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post_json(server, path, body: dict | None):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    payload = json.dumps(body) if body is not None else ""
    headers = {"Content-Type": "application/json"} if body is not None else {}
    conn.request("POST", path, body=payload, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    try:
        return resp.status, json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _make_open_proposal(text="L2 SW2 应该 tighten") -> dict:
    interp = interpret_suggestion_text(text)
    return create_proposal(
        source_text=text,
        interpretation=interp,
        author_name="Engineer-A",
        author_role="ENGINEER",
        ticket_id="WB-P44-05-TEST",
    )


# ─── 1. update_proposal_status (unit) ───────────────────────────────


def test_accept_transitions_open_to_accepted_and_appends_history():
    p = _make_open_proposal()
    record, err = update_proposal_status(p["id"], new_status="ACCEPTED", actor="Kogami")
    assert err is None
    assert record is not None
    assert record["status"] == "ACCEPTED"
    last = record["history"][-1]
    assert last["action"] == "accepted"
    assert last["actor"] == "Kogami"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", last["at"])


def test_reject_transitions_and_carries_note():
    p = _make_open_proposal()
    record, err = update_proposal_status(
        p["id"], new_status="REJECTED", actor="Kogami", note="conflicts with safety case"
    )
    assert err is None
    assert record["status"] == "REJECTED"
    last = record["history"][-1]
    assert last["action"] == "rejected"
    assert last["note"] == "conflicts with safety case"


def test_invalid_status_rejected():
    p = _make_open_proposal()
    record, err = update_proposal_status(p["id"], new_status="BOGUS", actor="x")
    assert err == "invalid_status"
    assert record is None


def test_not_found_returns_not_found():
    record, err = update_proposal_status("PROP-doesnotexist", new_status="ACCEPTED", actor="x")
    assert err == "not_found"
    assert record is None


def test_already_terminal_blocks_re_transition():
    p = _make_open_proposal()
    update_proposal_status(p["id"], new_status="ACCEPTED", actor="Kogami")
    record, err = update_proposal_status(p["id"], new_status="ACCEPTED", actor="Kogami")
    assert err == "already_terminal"
    assert record is not None and record["status"] == "ACCEPTED"


def test_accept_writes_dev_queue_brief_with_required_fields():
    p = _make_open_proposal("L1 上的 SW1 应该 add filter")
    update_proposal_status(p["id"], new_status="ACCEPTED", actor="Kogami")
    brief_path = dev_queue_dir() / f"{p['id']}.md"
    assert brief_path.is_file(), "dev-queue brief was not written on accept"
    text = brief_path.read_text(encoding="utf-8")
    # Lock the schema fields the brief must carry — these are the
    # contract Claude Code's /gsd-execute-phase will rely on.
    assert f"# Proposal {p['id']}" in text
    assert "**Status**: ACCEPTED" in text
    assert "by Kogami" in text
    assert "**Affected gates**:" in text
    assert "**Target signals**:" in text
    assert "**Change kind**:" in text
    assert "## Engineer's original suggestion · 工程师原始建议" in text
    assert "## System interpretation · 系统解读" in text
    assert "## Handoff to Claude Code" in text
    assert "/gsd-execute-phase" in text


def test_reject_does_not_write_dev_queue_brief():
    p = _make_open_proposal()
    update_proposal_status(p["id"], new_status="REJECTED", actor="Kogami")
    assert not (dev_queue_dir() / f"{p['id']}.md").exists(), (
        "rejected proposals must NOT generate a dev-queue brief"
    )


def test_write_dev_queue_brief_returns_path_and_is_idempotent():
    p = _make_open_proposal()
    p["status"] = "ACCEPTED"
    p["history"].append({
        "at": "2026-04-26T08:30:00Z", "actor": "Kogami", "action": "accepted",
    })
    path1 = write_dev_queue_brief(p)
    path2 = write_dev_queue_brief(p)
    assert path1 == path2
    assert path1.is_file()


# ─── 2. POST /api/proposals/<id>/accept (HTTP) ─────────────────────


def test_post_accept_happy_path(server):
    p = _make_open_proposal()
    status, body = _post_json(
        server,
        f"/api/proposals/{p['id']}/accept",
        {"actor": "Kogami"},
    )
    assert status == 200
    assert body["status"] == "ACCEPTED"
    assert body["history"][-1]["action"] == "accepted"
    assert body["history"][-1]["actor"] == "Kogami"
    assert (dev_queue_dir() / f"{p['id']}.md").is_file()


def test_post_reject_with_note(server):
    p = _make_open_proposal()
    status, body = _post_json(
        server,
        f"/api/proposals/{p['id']}/reject",
        {"actor": "Kogami", "note": "duplicate of WB-001"},
    )
    assert status == 200
    assert body["status"] == "REJECTED"
    assert body["history"][-1]["note"] == "duplicate of WB-001"


def test_post_accept_without_body_uses_anonymous_actor(server):
    p = _make_open_proposal()
    status, body = _post_json(server, f"/api/proposals/{p['id']}/accept", None)
    assert status == 200
    assert body["status"] == "ACCEPTED"
    assert body["history"][-1]["actor"] == "anonymous"


def test_post_accept_unknown_id_returns_404(server):
    status, body = _post_json(server, "/api/proposals/PROP-doesnotexist/accept", {})
    assert status == 404
    assert body["error"] == "proposal_not_found"


def test_post_accept_already_accepted_returns_409(server):
    p = _make_open_proposal()
    _post_json(server, f"/api/proposals/{p['id']}/accept", {})
    status, body = _post_json(server, f"/api/proposals/{p['id']}/accept", {})
    assert status == 409
    assert body["error"] == "proposal_already_terminal"
    assert body["current_status"] == "ACCEPTED"


def test_post_invalid_action_returns_404(server):
    p = _make_open_proposal()
    # /finalize is not a known action — falls through to the
    # do_POST 404 catch-all (the prefix-match in do_POST gates on
    # exactly /accept|/reject endings).
    status, _ = _post_json(server, f"/api/proposals/{p['id']}/finalize", {})
    assert status == 404


def test_post_accept_invalid_json_returns_400(server):
    p = _make_open_proposal()
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("POST", f"/api/proposals/{p['id']}/accept", body="{not json",
                 headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 400
    assert json.loads(raw)["error"] == "invalid_json"


def test_get_proposals_reflects_accepted_status(server):
    p = _make_open_proposal()
    _post_json(server, f"/api/proposals/{p['id']}/accept", {"actor": "Kogami"})
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("GET", "/api/proposals")
    resp = conn.getresponse()
    body = json.loads(resp.read().decode("utf-8"))
    conn.close()
    assert resp.status == 200
    assert body["proposals"][0]["status"] == "ACCEPTED"


# ─── 3. Frontend wiring (HTML + CSS + JS anchors) ───────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Action button row markup the renderer emits.
        "workbench-annotation-inbox-item-actions",
        'data-proposal-action="accept"',
        'data-proposal-action="reject"',
        # Bilingual labels with the agreed checkmark/x glyphs.
        "✅ 通过 · Accept",
        "✕ 驳回 · Reject",
        # Function the buttons call.
        "function transitionProposal(",
        # Path construction targets the new endpoint.
        "${PROPOSALS_PATH}/${encodeURIComponent(proposalId)}/${action}",
        # Reject prompts for an optional reason captured into history.
        '"驳回理由（可选）· Rejection reason (optional):"',
        # Card click handler must skip clicks on action buttons.
        '"[data-proposal-action]"',
    ],
)
def test_workbench_js_wires_accept_reject(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing accept/reject wiring: {needle}"


@pytest.mark.parametrize(
    "needle",
    [
        # Action row hidden by default; only Review Mode reveals it.
        ".workbench-annotation-inbox-item-actions",
        "display: none;",
        # CSS gate that flips them on.
        'body[data-review-mode="on"] .workbench-annotation-inbox-item[data-status="OPEN"] .workbench-annotation-inbox-item-actions',
    ],
)
def test_workbench_css_gates_actions_on_review_mode(needle):
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    assert needle in css, f"workbench.css missing accept/reject gating: {needle}"


# ─── 4. Truth-engine red-line guard ─────────────────────────────────


def test_p44_05_does_not_leak_into_truth_engine():
    """Accept / reject mutate proposal JSON + write a markdown brief
    under .planning/dev_queue/. They MUST NOT touch controller /
    runner / models / adapters. demo_server.py is the legitimate
    home for the new HTTP wiring + helpers, so it's excluded here
    (the truth engine itself is the controller/runner/models tree)."""
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "update_proposal_status",
        "write_dev_queue_brief",
        "dev_queue_dir",
        "transitionProposal",
        "/api/proposals/",
        "data-proposal-action",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P44-05 token "
                f"'{token}' — accept/reject must stay in the demo "
                f"server + workbench static layer"
            )

"""P44-03 — change-proposal persistence and inbox.

This sub-phase wires the engineer-side intent capture loop end-to-end:
  1. POST /api/proposals persists a confirmed interpretation as a JSON
     record under .planning/proposals/{PROP-...}.json (one file per
     proposal so git diffs are readable per-ticket; rollback = git
     revert).
  2. GET /api/proposals returns the persisted records, newest first,
     with optional ?status=OPEN filtering.
  3. The /workbench inbox loads the list at boot and refreshes after
     every confirmed submit so the engineer sees the new ticket appear
     immediately below the suggestion form.

Truth-engine red line preserved: proposals are an adapter-only store.
controller / runner / models / adapters/ are NOT modified by accepting
or rejecting a proposal — the actual change still goes through normal
Claude Code /gsd-execute-phase + git PR review (P44-05 wiring).
"""

from __future__ import annotations

import http.client
import json
import os
import re
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    create_proposal,
    interpret_suggestion_text,
    list_proposals,
    proposals_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


# ─── Test isolation: every test gets its own proposals dir via env var.


@pytest.fixture(autouse=True)
def _isolated_proposals_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    yield


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get_json(server: ThreadingHTTPServer, path: str) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    raw = response.read().decode("utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"raw": raw}
    return response.status, parsed


def _post_json(
    server: ThreadingHTTPServer, path: str, payload: dict
) -> tuple[int, dict]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(
        "POST",
        path,
        body=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
    )
    response = connection.getresponse()
    raw = response.read().decode("utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"raw": raw}
    return response.status, parsed


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. proposals_dir + create_proposal + list_proposals (unit) ──────


def test_proposals_dir_honors_env_override():
    target = proposals_dir()
    assert target.is_dir()
    # Comes from the autouse fixture's tmp path
    assert "proposals" in str(target)


def test_create_proposal_round_trips_to_disk(tmp_path):
    interp = interpret_suggestion_text("L2 的 SW2 应该 tighten 一下")
    record = create_proposal(
        source_text="L2 的 SW2 应该 tighten 一下",
        interpretation=interp,
        author_name="Kogami / Engineer",
        ticket_id="WB-E06-SHELL",
    )
    assert record["status"] == "OPEN"
    assert record["author_name"] == "Kogami / Engineer"
    assert record["ticket_id"] == "WB-E06-SHELL"
    assert record["interpretation"] == interp
    assert record["source_text"] == "L2 的 SW2 应该 tighten 一下"
    # Lock the id format so callers can rely on sortability.
    assert re.fullmatch(r"PROP-\d{8}T\d{12}-[0-9a-f]{6}", record["id"])
    # Lock the ISO-8601 UTC format.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", record["created_at"])
    # File must be on disk.
    target = proposals_dir() / f"{record['id']}.json"
    assert target.is_file()
    on_disk = json.loads(target.read_text(encoding="utf-8"))
    assert on_disk == record
    # History seeded with one entry.
    assert len(record["history"]) == 1
    assert record["history"][0]["action"] == "submitted"


def test_list_proposals_returns_newest_first():
    interp = interpret_suggestion_text("L1 测试")
    a = create_proposal(source_text="第一个", interpretation=interp)
    b = create_proposal(source_text="第二个", interpretation=interp)
    c = create_proposal(source_text="第三个", interpretation=interp)
    listed = list_proposals()
    assert [r["id"] for r in listed] == [c["id"], b["id"], a["id"]]


def test_list_proposals_filters_by_status():
    interp = interpret_suggestion_text("L3 调整")
    a = create_proposal(source_text="open one", interpretation=interp)
    # Manually flip a record's status to ACCEPTED on disk so the filter
    # test exercises a real different-status row, not a synthetic dict.
    target = proposals_dir() / f"{a['id']}.json"
    raw = json.loads(target.read_text(encoding="utf-8"))
    raw["status"] = "ACCEPTED"
    target.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    create_proposal(source_text="still open", interpretation=interp)
    open_only = list_proposals(status_filter="OPEN")
    accepted_only = list_proposals(status_filter="ACCEPTED")
    assert len(open_only) == 1 and open_only[0]["status"] == "OPEN"
    assert len(accepted_only) == 1 and accepted_only[0]["status"] == "ACCEPTED"


def test_list_proposals_skips_corrupt_files():
    interp = interpret_suggestion_text("L1 健全检查")
    a = create_proposal(source_text="ok", interpretation=interp)
    # Drop a malformed file alongside the good one
    (proposals_dir() / "PROP-20260101T000000-000000.json").write_text(
        "{not json", encoding="utf-8"
    )
    listed = list_proposals()
    assert len(listed) == 1 and listed[0]["id"] == a["id"]


# ─── 2. POST /api/proposals (HTTP) ──────────────────────────────────


def test_proposals_post_happy_path(server):
    interp = interpret_suggestion_text("L1 的 SW1 应该改成持续 50ms")
    status, body = _post_json(
        server,
        "/api/proposals",
        {
            "source_text": "L1 的 SW1 应该改成持续 50ms",
            "interpretation": interp,
            "author_name": "Kogami / Engineer",
            "author_role": "ENGINEER",
            "ticket_id": "WB-E06-SHELL",
            "system_id": "thrust-reverser",
        },
    )
    assert status == 201, body
    assert body["status"] == "OPEN"
    assert body["interpretation"]["affected_gates"] == ["L1"]
    assert body["author_name"] == "Kogami / Engineer"
    # Round-trip via GET
    list_status, list_body = _get_json(server, "/api/proposals")
    assert list_status == 200
    assert any(r["id"] == body["id"] for r in list_body["proposals"])


@pytest.mark.parametrize(
    "payload,error_code",
    [
        ({}, "missing_or_empty_source_text"),
        ({"source_text": ""}, "missing_or_empty_source_text"),
        ({"source_text": "x"}, "missing_or_invalid_interpretation"),
        ({"source_text": "x", "interpretation": "not a dict"}, "missing_or_invalid_interpretation"),
        (
            {"source_text": "x", "interpretation": {"affected_gates": []}},
            "interpretation_missing_field",
        ),
    ],
)
def test_proposals_post_validates_payload(server, payload, error_code):
    status, body = _post_json(server, "/api/proposals", payload)
    assert status == 400, body
    assert body["error"] == error_code


def test_proposals_post_assigns_default_metadata(server):
    interp = interpret_suggestion_text("L4 调整")
    _, body = _post_json(
        server,
        "/api/proposals",
        {"source_text": "raw", "interpretation": interp},
    )
    assert body["author_name"] == "anonymous"
    assert body["author_role"] == "ENGINEER"
    assert body["ticket_id"] == "ad-hoc"
    assert body["system_id"] == "thrust-reverser"


# ─── 3. GET /api/proposals (HTTP) ───────────────────────────────────


def test_proposals_get_empty(server):
    status, body = _get_json(server, "/api/proposals")
    assert status == 200
    assert body == {"proposals": []}


def test_proposals_get_returns_newest_first(server):
    interp = interpret_suggestion_text("L1 测试")
    a = create_proposal(source_text="第一", interpretation=interp)
    b = create_proposal(source_text="第二", interpretation=interp)
    status, body = _get_json(server, "/api/proposals")
    assert status == 200
    ids = [r["id"] for r in body["proposals"]]
    assert ids == [b["id"], a["id"]]


def test_proposals_get_filters_by_status_query(server):
    interp = interpret_suggestion_text("L1 测试")
    a = create_proposal(source_text="open", interpretation=interp)
    target = proposals_dir() / f"{a['id']}.json"
    raw = json.loads(target.read_text(encoding="utf-8"))
    raw["status"] = "REJECTED"
    target.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    create_proposal(source_text="still open", interpretation=interp)
    status, body = _get_json(server, "/api/proposals?status=OPEN")
    assert status == 200
    assert all(r["status"] == "OPEN" for r in body["proposals"])
    assert len(body["proposals"]) == 1
    status, body = _get_json(server, "/api/proposals?status=REJECTED")
    assert status == 200
    assert len(body["proposals"]) == 1
    assert body["proposals"][0]["status"] == "REJECTED"


# ─── 4. /workbench HTML inbox container in place ────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="annotation-inbox"',
        'id="annotation-inbox-list"',
        'id="annotation-inbox-refresh-btn"',
        'data-inbox-state="loading"',
        # P53-02 (2026-04-27): inbox aside lost its inner header
        # ("已提交工单" + "审核队列" h2 + "↻ 刷新 · Refresh" button).
        # The wrapping #workbench-tool-approve drawer header now
        # carries the "审批中心 · Approval Center" title; the inbox
        # is just one section inside it. Refresh button is still
        # present (id preserved for JS) but with a shorter label.
        "工单 · Proposals",
        "↻ 刷新",
        "载入中… · loading…",
    ],
)
def test_workbench_html_carries_inbox_container(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"missing P44-03 inbox anchor: {anchor}"


# ─── 5. workbench.js wires submit -> POST + load + render ───────────


@pytest.mark.parametrize(
    "js_anchor",
    [
        'const PROPOSALS_PATH = "/api/proposals";',
        "function installProposalInbox",
        "function loadProposalsInbox",
        "function renderProposalsInbox",
        "async function submitSuggestionTicket",
        # Submit must POST and re-fetch the inbox
        'method: "POST"',
        "await loadProposalsInbox();",
        # Boot wires the installer
        "installProposalInbox();",
        # Empty-state copy and item-row markup hooks
        "暂无已提交工单",
        "workbench-annotation-inbox-item",
        "data-proposal-id=",
    ],
)
def test_workbench_js_wires_inbox(js_anchor: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert js_anchor in js, f"missing P44-03 JS hook: {js_anchor}"


# ─── 6. End-to-end via HTTP server: submit then list ────────────────


def test_proposals_endpoint_submit_then_list(server):
    interp = interpret_suggestion_text("L2 的 SW2 应该 tighten")
    create_status, created = _post_json(
        server,
        "/api/proposals",
        {
            "source_text": "L2 的 SW2 应该 tighten",
            "interpretation": interp,
            "author_name": "Kogami / Engineer",
        },
    )
    assert create_status == 201
    list_status, list_body = _get_json(server, "/api/proposals")
    assert list_status == 200
    assert len(list_body["proposals"]) == 1
    record = list_body["proposals"][0]
    assert record["id"] == created["id"]
    assert record["interpretation"]["affected_gates"] == ["L2"]
    assert record["interpretation"]["change_kind"] == "tighten_condition"


# ─── 7. Truth-engine red line preserved ─────────────────────────────


def test_p44_03_does_not_leak_into_truth_engine() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    well_harness_dir = repo_root / "src" / "well_harness"
    backend_paths: list[Path] = [
        well_harness_dir / "controller.py",
        well_harness_dir / "runner.py",
        well_harness_dir / "models.py",
    ]
    adapters_dir = well_harness_dir / "adapters"
    if adapters_dir.is_dir():
        backend_paths.extend(
            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
        )
    # Phrases that must never appear ANYWHERE in the truth engine —
    # these are workbench helpers / UI strings that have no business
    # being imported or rendered by controller / runner / models /
    # adapters.
    hard_block_phrases = [
        "create_proposal",
        "list_proposals",
        "proposals_dir",
        "_handle_create_proposal",
        "WORKBENCH_PROPOSALS_DIR",
        "已提交工单",
        "annotation-inbox-refresh-btn",
    ]
    # Phrases that are workbench-side noise in CODE but legitimate in
    # COMMENTS — audit references like
    # `# PROP-20260426T075902988411-e27a6e: tighten L2 SW2`
    # are exactly what /gsd-execute-phase-from-brief Step 7 asks for
    # so `git log --grep="{PROP-ID}"` finds the implementing commit
    # (P44-06 rollback hints rely on this). Flag only when the phrase
    # appears in actual source, not inside a `# ...` comment.
    code_only_phrases = [
        "PROP-",
    ]

    def _strip_python_line_comments(source: str) -> str:
        """Drop everything after the first un-quoted `#` on each line.
        Cheap heuristic — good enough for this guard since the
        truth-engine files don't have `#` characters inside string
        literals at risk of false positives. Refine if that ever
        changes."""
        out_lines = []
        for line in source.splitlines():
            comment = line.find("#")
            if comment >= 0:
                line = line[:comment]
            out_lines.append(line)
        return "\n".join(out_lines)

    for backend in backend_paths:
        text = backend.read_text(encoding="utf-8")
        for phrase in hard_block_phrases:
            assert phrase not in text, (
                f"P44-03 phrase {phrase!r} unexpectedly leaked into "
                f"{backend.relative_to(repo_root)} — truth-engine red-line breach"
            )
        code_text = _strip_python_line_comments(text)
        for phrase in code_only_phrases:
            assert phrase not in code_text, (
                f"P44-03 phrase {phrase!r} unexpectedly leaked into "
                f"{backend.relative_to(repo_root)} OUTSIDE a comment — "
                f"truth-engine red-line breach (audit references in "
                f"`# ...` comments are allowed; in code is not)"
            )

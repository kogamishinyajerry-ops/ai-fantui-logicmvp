"""P45-02 — per-system inbox filtering.

P45-01 wired multi-system circuit routing so switching the dropdown
re-paints the panel. This phase finishes the scoping by also
filtering the proposals inbox to the currently-selected system.
Without this, a thrust-reverser ticket would show up when the
engineer is looking at landing-gear — confusing scope leakage.

Backend: list_proposals() gains a system_filter kwarg; GET
/api/proposals accepts ?system=<id> (combinable with ?status=).

Frontend: loadProposalsInbox passes the dropdown's current value;
dropdown's change event re-loads inbox alongside the circuit.

Truth-engine red line preserved: pure adapter-layer addition; no
controller / runner / models / adapters changes.
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
    list_proposals,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


@pytest.fixture(autouse=True)
def _isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(tmp_path / "dev_queue"))
    yield


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _seed(system_id: str, *, status: str = "OPEN") -> dict:
    interp = interpret_suggestion_text("L2 SW2 应该 tighten")
    record = create_proposal(
        source_text="L2 SW2 应该 tighten",
        interpretation=interp,
        author_name="Engineer",
        system_id=system_id,
    )
    if status != "OPEN":
        # Mutate via the same disk path so we don't depend on the
        # accept/reject endpoint here (orthogonal concern).
        from well_harness.demo_server import proposals_dir
        path = proposals_dir() / f"{record['id']}.json"
        record["status"] = status
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def _get(server, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("GET", path)
    resp = conn.getresponse()
    body = json.loads(resp.read().decode("utf-8"))
    conn.close()
    return resp.status, body


# ─── 1. list_proposals system_filter (unit) ─────────────────────────


def test_list_proposals_system_filter_narrows_results():
    _seed("thrust-reverser")
    _seed("landing-gear")
    _seed("c919-etras")
    only_tr = list_proposals(system_filter="thrust-reverser")
    assert len(only_tr) == 1
    assert only_tr[0]["system_id"] == "thrust-reverser"
    only_lg = list_proposals(system_filter="landing-gear")
    assert len(only_lg) == 1
    assert only_lg[0]["system_id"] == "landing-gear"


def test_list_proposals_system_filter_no_match_returns_empty():
    _seed("thrust-reverser")
    assert list_proposals(system_filter="bleed-air-valve") == []


def test_list_proposals_combines_status_and_system_filters():
    _seed("thrust-reverser", status="OPEN")
    _seed("thrust-reverser", status="ACCEPTED")
    _seed("landing-gear", status="OPEN")
    only_tr_open = list_proposals(status_filter="OPEN", system_filter="thrust-reverser")
    assert len(only_tr_open) == 1
    assert only_tr_open[0]["system_id"] == "thrust-reverser"
    assert only_tr_open[0]["status"] == "OPEN"


def test_list_proposals_no_filters_returns_everything():
    _seed("thrust-reverser")
    _seed("landing-gear")
    _seed("c919-etras")
    assert len(list_proposals()) == 3


# ─── 2. GET /api/proposals?system= (HTTP) ──────────────────────────


def test_get_proposals_filters_by_system_query(server):
    _seed("thrust-reverser")
    _seed("landing-gear")
    status, body = _get(server, "/api/proposals?system=landing-gear")
    assert status == 200
    assert len(body["proposals"]) == 1
    assert body["proposals"][0]["system_id"] == "landing-gear"


def test_get_proposals_combines_status_and_system(server):
    _seed("thrust-reverser", status="OPEN")
    _seed("thrust-reverser", status="ACCEPTED")
    _seed("landing-gear", status="OPEN")
    status, body = _get(
        server, "/api/proposals?status=OPEN&system=thrust-reverser"
    )
    assert status == 200
    assert len(body["proposals"]) == 1
    p = body["proposals"][0]
    assert p["status"] == "OPEN"
    assert p["system_id"] == "thrust-reverser"


def test_get_proposals_unknown_system_returns_empty_list(server):
    _seed("thrust-reverser")
    status, body = _get(server, "/api/proposals?system=bogus-system-xyz")
    assert status == 200
    assert body["proposals"] == []


# ─── 3. Frontend wiring (JS anchors) ───────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Inbox fetch URL must carry the system param.
        '`${PROPOSALS_PATH}?system=${encodeURIComponent(system)}`',
        # The list mount records its current system so reviewers /
        # tests can identify scope.
        "list.dataset.inboxSystem = system;",
        # Header refresh helper exists by name.
        "function refreshInboxHeaderForSystem(system)",
        # Header text contract — bilingual + names the system.
        "`审核队列 · Review Queue · ${system}`",
        # Dropdown change must re-load BOTH the circuit AND the inbox
        # (P45-01 + P45-02 stacked).
        "reloadWorkbenchCircuitHero();",
        "loadProposalsInbox();",
    ],
)
def test_workbench_js_wires_per_system_inbox(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing P45-02 wiring: {needle}"


# ─── 4. Truth-engine red line ──────────────────────────────────────


def test_p45_02_does_not_leak_into_truth_engine():
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "system_filter",
        "refreshInboxHeaderForSystem",
        "inboxSystem",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P45-02 token "
                f"'{token}' — per-system inbox filtering must stay "
                f"in the workbench layer"
            )

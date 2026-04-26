"""E11-15b — Chinese-first h2 / button / caption sweep (iter 2).

Continues the E11-15 eyebrow sweep: 7 remaining English-only h1/h2/button/
caption strings on /workbench are bilingualized as `<中文> · <English>`,
preserving the English suffix so existing test locks (e.g. dual-route
checks for `Control Logic Workbench</h1>`) continue to pass.

In-scope strings (file:line in pre-sweep workbench.html):
- :18  h1   Control Logic Workbench           → 控制逻辑工作台 · Control Logic Workbench
- :281 btn  Load Active Ticket                → 加载当前工单 · Load Active Ticket
- :282 btn  Snapshot Current State            → 快照当前状态 · Snapshot Current State
- :334 h2   Review Queue                      → 审核队列 · Review Queue
- :349 btn  Approval Center                   → 审批中心 · Approval Center
- :351 cap  Approval actions are Kogami-only. → 审批操作仅限 Kogami · Approval actions are Kogami-only.
- :380 h2   Kogami Proposal Triage            → Kogami 提案审批 · Kogami Proposal Triage

Out of scope (deliberately preserved or deferred):
- API remediation message in demo_server.py:743 — backend contract,
  locked by tests/test_lever_snapshot_manual_override_guard.py:151.
- Approval lane h3s "Pending"/"Accept"/"Reject" + lane buttons
  ("Accept Proposal"/"Reject Proposal") — functional approval-flow
  strings, deferred to a focused approval-flow polish sub-phase.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. New bilingual strings POSITIVELY locked ──────────────────────


@pytest.mark.parametrize(
    "bilingual",
    [
        "<h1>控制逻辑工作台 · Control Logic Workbench</h1>",
        ">加载当前工单 · Load Active Ticket<",
        ">快照当前状态 · Snapshot Current State<",
        "<h2>审核队列 · Review Queue</h2>",
        "审批中心 · Approval Center",
        "审批操作仅限 Kogami · Approval actions are Kogami-only.",
        "Kogami 提案审批 · Kogami Proposal Triage",
    ],
)
def test_workbench_html_carries_bilingual_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing bilingual string: {bilingual}"


# ─── 2. Stale English-only strings are gone ──────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        "<h1>Control Logic Workbench</h1>",
        ">Load Active Ticket<",
        ">Snapshot Current State<",
        "<h2>Review Queue</h2>",
        "<h2 id=\"approval-center-title\">Kogami Proposal Triage</h2>",
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only string still present: {stale}"


# ─── 3. English suffixes preserved for existing test locks ───────────
#
# E11-15b deliberately keeps the English token at the end of each
# bilingual string, so existing exact-substring tests (e.g.
# test_workbench_dual_route's `Control Logic Workbench</h1>` check)
# keep passing without modification.


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        "Control Logic Workbench</h1>",
        "Load Active Ticket</button>",
        "Snapshot Current State</button>",
        "Review Queue</h2>",
        "Approval Center\n",  # button text fragment, newline preserved
        "Approval actions are Kogami-only.",
        "Kogami Proposal Triage</h2>",
    ],
)
def test_e11_15b_preserves_english_suffix(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15b broke English suffix invariant: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="approval-center-entry"',
        'id="approval-center-panel"',
        'id="approval-center-title"',
        'id="annotation-inbox"',
        'class="workbench-toolbar-button is-primary"',
        'data-role="KOGAMI"',
        'data-approval-role="KOGAMI"',
    ],
)
def test_e11_15b_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15b broke structural anchor: {anchor}"


# ─── 5. Live-served route reflects the sweep ─────────────────────────


def test_workbench_route_serves_bilingual_strings(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert "控制逻辑工作台 · Control Logic Workbench" in html
    assert "审核队列 · Review Queue" in html
    assert "审批中心 · Approval Center" in html
    assert "审批操作仅限 Kogami" in html
    assert "Kogami 提案审批" in html
    assert "加载当前工单" in html
    assert "快照当前状态" in html


# ─── 6. Truth-engine red line — API remediation untouched ────────────
#
# The Approval Center remediation message in demo_server.py is a
# backend API contract locked by test_lever_snapshot_manual_override_guard.
# The HTML sweep MUST NOT bilingualize that string; the API stays English.


def test_e11_15b_does_not_touch_api_remediation_message() -> None:
    """The 409 remediation message is API contract, not display copy."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
        encoding="utf-8"
    )
    # The original English-only remediation text MUST still be there.
    assert (
        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
        in demo_server
    )
    # No Chinese leak into the API layer.
    assert "审批中心" not in demo_server
    assert "审批操作" not in demo_server

"""E11-15d — approval-flow polish: bilingualize 3 lane h3s + 2 lane buttons + 1 body copy.

Closes the last English-only surface in the workbench demo (the
Approval Center lane labels + buttons + pending-lane body copy).
Functional approval-flow strings are now `<中文> · <English>`,
preserving English suffixes for any downstream substring locks
(none currently exist in tests).

Out of scope:
- API remediation message in demo_server.py:743 — backend contract
  (locked by tests/test_lever_snapshot_manual_override_guard.py:151).
- Approval Center entry button + Kogami-only caption (already
  bilingualized by E11-15b PR #25).
- approval-center-title h2 (already bilingualized by E11-15b PR #25).
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
        "<h3>待审 · Pending</h3>",
        "<h3>通过 · Accept</h3>",
        "<h3>驳回 · Reject</h3>",
        "通过提案 · Accept Proposal",
        "驳回提案 · Reject Proposal",
        "已提交的标注提案在被通过或驳回前在此排队 · Submitted annotation proposals wait here before acceptance or rejection.",
    ],
)
def test_workbench_html_carries_bilingual_approval_flow_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing bilingual approval-flow string: {bilingual}"


# ─── 2. Stale English-only strings are gone ──────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        "<h3>Pending</h3>",
        "<h3>Accept</h3>",
        "<h3>Reject</h3>",
        ">Accept Proposal<",
        ">Reject Proposal<",
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only approval-flow string still present: {stale}"


# ─── 3. English suffixes preserved for future substring locks ────────


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        "Pending</h3>",
        "Accept</h3>",
        "Reject</h3>",
        "Accept Proposal</button>",
        "Reject Proposal</button>",
        "before acceptance or rejection.",  # tail of the body copy
    ],
)
def test_e11_15d_preserves_english_suffix(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15d broke English suffix invariant: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'data-approval-lane="pending"',
        'data-approval-lane="accept"',
        'data-approval-lane="reject"',
        'data-approval-action="accept"',
        'data-approval-action="reject"',
        'class="workbench-approval-grid"',
    ],
)
def test_e11_15d_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15d broke structural anchor: {anchor}"


# ─── 5. Live-served route reflects the polish ────────────────────────


def test_workbench_route_serves_bilingual_approval_flow(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert "待审 · Pending" in html
    assert "通过 · Accept" in html
    assert "驳回 · Reject" in html
    assert "通过提案 · Accept Proposal" in html
    assert "驳回提案 · Reject Proposal" in html
    assert "已提交的标注提案在被通过或驳回前在此排队" in html


# ─── 6. Truth-engine red line — API remediation untouched ────────────


def test_e11_15d_does_not_touch_api_remediation_message() -> None:
    """The 409 remediation message is API contract, not display copy."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_server = (repo_root / "src" / "well_harness" / "demo_server.py").read_text(
        encoding="utf-8"
    )
    assert (
        "Acquire sign-off via Approval Center, or switch to auto_scrubber."
        in demo_server
    )
    # Approval-flow Chinese strings must NOT leak into backend
    new_strings = [
        "待审", "通过 · Accept", "驳回 · Reject",
        "通过提案", "驳回提案", "已提交的标注提案",
    ]
    for new_string in new_strings:
        assert new_string not in demo_server, (
            f"E11-15d Chinese {new_string!r} unexpectedly leaked into demo_server.py"
        )


# ─── 7. P2 R1 IMPORTANT closure: surface inventory honesty guard ─────


def test_e11_15d_surface_inventory_does_not_overclaim_closure() -> None:
    """P2 R1 IMPORTANT closure: an earlier draft of E11-15d-SURFACE-INVENTORY.md
    claimed `last English-only surface` and `uniformly Chinese-first`,
    but P2 verified `/workbench` still has English-only `Hide for session`,
    `Truth Engine — Read Only`, `No proposals submitted yet.`, and
    `Pending Kogami sign-off`. The doc was corrected to defer those to
    a future E11-15e sub-phase. This guard prevents the overclaim from
    being reintroduced silently."""
    repo_root = Path(__file__).resolve().parents[1]
    surface_inventory = (
        repo_root
        / ".planning"
        / "phases"
        / "E11-workbench-engineer-first-ux"
        / "E11-15d-SURFACE-INVENTORY.md"
    )
    text = surface_inventory.read_text(encoding="utf-8")
    forbidden_overclaims = [
        "last English-only surface",
        "uniformly Chinese-first",
    ]
    for phrase in forbidden_overclaims:
        # The doc's leading blockquote (lines starting `>`) explicitly
        # references the forbidden phrases as part of explaining why
        # they were removed. Skip those lines to avoid self-reference
        # false-positives — the guard cares about fresh claims, not
        # the historical-correction note.
        for line in text.splitlines():
            if phrase in line and not line.lstrip().startswith(">"):
                raise AssertionError(
                    f"E11-15d-SURFACE-INVENTORY contains forbidden overclaim "
                    f"phrase {phrase!r} on line: {line!r}"
                )

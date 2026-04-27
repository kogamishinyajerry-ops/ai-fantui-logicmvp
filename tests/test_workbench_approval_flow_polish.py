"""E11-15d — approval-flow polish: bilingualize 3 lane h3s + 2 lane buttons + 1 body copy.

Bilingualizes the Approval Center lane labels + buttons + pending-lane
body copy (6 strings only). Functional approval-flow strings are now
`<中文> · <English>`, preserving English suffixes for any downstream
substring locks (none currently exist in tests).

This is one slice in a multi-sub-phase Chinese-first thread; it does
NOT finish the workbench Chinese-first work. P2 R2 IMPORTANT closure:
earlier docstring overclaimed "Closes the last English-only surface" —
corrected. See E11-15d-SURFACE-INVENTORY.md for the (non-exhaustive)
list of English-only surfaces still remaining on /workbench.

Out of scope:
- API remediation message in demo_server.py:743 — backend contract
  (locked by tests/test_lever_snapshot_manual_override_guard.py:151).
- Approval Center entry button + Kogami-only caption (already
  bilingualized by E11-15b PR #25).
- approval-center-title h2 (already bilingualized by E11-15b PR #25).
- Trust-banner dismiss / authority headline / inbox placeholder /
  pending-signoff strong / WOW h3s / topbar chip labels / state-of-world
  labels / system options / `Manual (advisory)` / boot placeholders /
  reference-packet block — deferred to future E11-15e Tier-A bundle.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler

# P54-00 (2026-04-27): the entire #approval-center-panel surface
# (3-lane pending/accept/reject grid + Accept Proposal / Reject
# Proposal buttons) was removed. The bilingual-string contract this
# file locked in no longer applies — per-card approve/reject buttons
# rendered by workbench.js are the new approval surface.
pytestmark = pytest.mark.skip(
    reason=(
        "Obsolete after P54-00: approval-center 3-lane panel removed; "
        "per-card buttons replace it"
    )
)


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


def test_e11_15d_artifacts_do_not_overclaim_closure() -> None:
    """P2 R1 + R2 IMPORTANT closure: earlier drafts of the E11-15d
    SURFACE-INVENTORY, the PERSONA-ROTATION-STATE entry, and this test
    module's docstring all claimed `last English-only surface` and/or
    `uniformly Chinese-first`. P2 verified `/workbench` still has many
    English-only surfaces outside this slice (`Hide for session`,
    `Truth Engine — Read Only`, `No proposals submitted yet.`,
    `Pending Kogami sign-off`, WOW h3s, topbar chips, state-of-world
    labels, etc.). All three artifacts were corrected to defer those
    to E11-15e. This guard scans ALL three artifacts to prevent the
    overclaim from being reintroduced silently in any of them.
    """
    repo_root = Path(__file__).resolve().parents[1]
    artifacts = [
        repo_root
        / ".planning"
        / "phases"
        / "E11-workbench-engineer-first-ux"
        / "E11-15d-SURFACE-INVENTORY.md",
        repo_root
        / ".planning"
        / "phases"
        / "E11-workbench-engineer-first-ux"
        / "PERSONA-ROTATION-STATE.md",
        # Self-scan: this test file's own docstring header is included.
        Path(__file__),
    ]
    forbidden_overclaims = [
        "last English-only surface",
        "uniformly Chinese-first",
    ]
    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8")
        for phrase in forbidden_overclaims:
            # The forbidden phrase is a CLAIM problem, not a literal-mention
            # problem. Exempt lines where the phrase appears inside a quoted
            # context (Markdown blockquote, backticks anywhere on line, or
            # double-quotes anywhere on line) — those are literal references
            # to the phrase, not fresh assertions of the claim. Bare unquoted
            # mentions still fail the guard.
            for line_no, line in enumerate(text.splitlines(), 1):
                if phrase not in line:
                    continue
                if line.lstrip().startswith(">"):
                    continue
                # If the line carries any quote or backtick, the phrase is
                # most likely being referenced as a literal historical note,
                # not asserted as a fresh claim.
                if "`" in line or '"' in line:
                    continue
                raise AssertionError(
                    f"{artifact.name}:{line_no} contains forbidden overclaim "
                    f"phrase {phrase!r}: {line!r}"
                )

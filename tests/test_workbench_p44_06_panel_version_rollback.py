"""P44-06 — panel version chip + rollback hints.

The chip surfaces "what version of the panel am I looking at?" =
truth-engine HEAD SHA + count of ACCEPTED proposals. Click → jump to
the inbox so the engineer can skim the decision history. The
rollback-hints expander lives inside each ACCEPTED ticket card and
reveals the exact git commands the engineer would run themselves to
revert that proposal's commit. The workbench never executes git
mutations — pure read-only instruction.

Truth-engine red line: this is a frontend-only feature. Backend
already exposes truth_engine_sha via /api/workbench/state-of-world
(P19); P44-06 adds NO new server endpoints.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── 1. Backend (already-existing endpoint, sanity check) ──────────


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


def test_state_of_world_payload_carries_truth_engine_sha(server):
    """The chip reads truth_engine_sha from this endpoint. If the
    contract changes (rename/removal) the chip silently breaks, so
    we lock the field name here."""
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("GET", "/api/workbench/state-of-world")
    resp = conn.getresponse()
    body = json.loads(resp.read().decode("utf-8"))
    conn.close()
    assert resp.status == 200
    assert "truth_engine_sha" in body
    assert isinstance(body["truth_engine_sha"], str)


# ─── 2. HTML anchors ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Topbar chip with the documented id.
        'id="workbench-panel-version-chip"',
        # The chip is also a class hook for CSS theming.
        "workbench-panel-version-chip",
        # Loading-state attribute the JS flips after fetch.
        'data-panel-version-state="loading"',
        # The label slot the JS swaps text into.
        "data-panel-version-label",
        # Bilingual chip eyebrow + initial label.
        "📜 面板版本 · Panel Version",
        "载入中… · loading…",
    ],
)
def test_workbench_html_carries_panel_version_chip(needle):
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert needle in html, f"workbench.html missing panel-version hook: {needle}"


# ─── 3. CSS hooks ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        ".workbench-panel-version-chip",
        '.workbench-panel-version-chip[data-panel-version-state="ready"]',
        '.workbench-panel-version-chip[data-panel-version-state="error"]',
        # Rollback hints block hidden by default; expander toggles it.
        ".workbench-rollback-hints",
        '.workbench-rollback-hints[data-rollback-state="open"]',
        ".workbench-rollback-toggle",
    ],
)
def test_workbench_css_carries_panel_version_and_rollback_rules(needle):
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    assert needle in css, f"workbench.css missing P44-06 rule: {needle}"


# ─── 4. JS wiring ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Path constant — only one source of truth for the SoW endpoint.
        'const STATE_OF_WORLD_PATH = "/api/workbench/state-of-world";',
        # SHA cache so the chip can refresh without re-fetching.
        "let _panelVersionSha = null;",
        # Function names locked by contract.
        "function installPanelVersionChip()",
        "function refreshPanelVersionChip()",
        "function renderRollbackHints(proposal)",
        # Boot wiring: shell installer must wire the chip on first paint.
        "installPanelVersionChip();",
        # Chip refresh must fire after every inbox load so the count
        # tracks ACCEPTED transitions in real time.
        "refreshPanelVersionChip();",
        # Rollback hints embedded in ACCEPTED card render path.
        "renderRollbackHints(p)",
        'data-rollback-toggle-for=',
        'data-rollback-hints-for=',
        # The two git commands surfaced to the engineer.
        'git log --oneline --all --grep="${id}"',
        "git revert &lt;sha-from-above&gt;",
        # The dev-queue brief filename mirrors the proposal id.
        ".planning/dev_queue/${id}.md",
        # Read-only disclaimer must be in the hints copy.
        "Workbench is read-only and will never run git for you",
    ],
)
def test_workbench_js_wires_panel_version_and_rollback(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing P44-06 wiring: {needle}"


# ─── 5. Truth-engine red-line guard ─────────────────────────────────


def test_p44_06_does_not_leak_into_truth_engine():
    """Panel-version chip + rollback hints are 100% frontend-only.
    No new server endpoints, no controller / runner / models /
    adapters changes. demo_server.py is excluded because the
    pre-existing state-of-world endpoint is the data source — but
    we do scan it for any P44-06 token to make sure we didn't
    accidentally bolt new server wiring on for this sub-phase."""
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "panel_version",
        "panel-version",
        "rollback_hints",
        "rollback-hints",
        "renderRollbackHints",
        "installPanelVersionChip",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P44-06 token "
                f"'{token}' — panel-version chip must stay in the "
                f"workbench static layer"
            )
    # Also assert demo_server.py didn't gain any P44-06 server-side
    # helper (the chip MUST consume the existing state-of-world
    # endpoint, not a new one).
    demo_server = (SRC_DIR / "demo_server.py").read_text(encoding="utf-8")
    for token in ("panel_version", "rollback_hints", "renderRollbackHints"):
        assert token not in demo_server, (
            f"demo_server.py grew P44-06 token '{token}' — chip must "
            f"reuse /api/workbench/state-of-world, not introduce new "
            f"endpoints"
        )

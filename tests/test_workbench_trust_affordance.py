"""E11-13 — manual_feedback_override UI trust-affordance regression lock.

Locks the chip + banner + copy strings so future workbench shell edits
don't silently regress the trust affordance. Per E11-13-SURFACE-INVENTORY.md
all 7 surface claims are anchored at known DOM ids; this test validates
both static-file invariants and live-served HTML.

Per v2.3 §UI-COPY-PROBE: the banner copy is a positive claim about the
authority boundary; if the banner ships with text drift, the test catches
it before merge.
"""

from __future__ import annotations

import http.client
import re
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
    body = response.read().decode("utf-8")
    return response.status, body


def test_static_html_has_feedback_mode_chip() -> None:
    """Chip DOM + initial state attributes are present in workbench.html."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-feedback-mode"' in html
    assert 'data-feedback-mode="manual_feedback_override"' in html
    assert 'data-mode-authority="advisory"' in html
    assert "Manual (advisory)" in html


def test_static_html_has_trust_banner() -> None:
    """Trust banner DOM + advisory copy + dismiss control + scope definition.

    P1-R2 fix (Finding #6 not-resolved at R2 first attempt): scope definition
    must appear BEFORE the advisory framing in DOM/reading order. P1-R2 NIT:
    "override observed" jargon removed (didn't appear elsewhere on page).
    """
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-trust-banner"' in html
    assert "advisory" in html
    assert "Truth engine readings" in html
    assert "data-trust-banner-dismiss" in html
    assert "Hide for session" in html
    # Scope-definition clause present
    assert 'workbench-trust-banner-scope' in html
    assert 'What "manual feedback" means here' in html
    # P1-R2 NIT fix: jargon "override observed" removed
    assert "override observed" not in html
    # P1-R2 BLOCKER fix: scope definition appears BEFORE the advisory headline
    scope_idx = html.index("workbench-trust-banner-scope")
    advisory_idx = html.index("That mode is advisory.")
    assert scope_idx < advisory_idx, (
        "Scope clause must precede advisory framing per P1-R2 finding #6 fix"
    )


def test_static_css_has_feedback_mode_styling() -> None:
    """CSS exists for both manual + truth_engine chip variants and banner."""
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    assert ".workbench-feedback-mode-chip" in css
    assert '.workbench-feedback-mode-chip[data-feedback-mode="truth_engine"]' in css
    assert ".workbench-trust-banner" in css
    assert '.workbench-trust-banner[data-feedback-mode="truth_engine"]' in css
    assert ".workbench-trust-banner-dismiss" in css


def test_static_js_has_feedback_mode_handler() -> None:
    """JS install function + setFeedbackMode API present and called on boot."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "installFeedbackModeAffordance" in js
    assert "setFeedbackMode" in js
    assert 'workbench-trust-banner-dismissed' in js
    install_call_idx = js.index("installFeedbackModeAffordance();")
    boot_call_idx = js.index("bootWorkbenchShell();")
    assert boot_call_idx < install_call_idx, "affordance install must follow shell boot"


def test_topbar_grid_accommodates_third_chip() -> None:
    """Topbar grid-template-columns accepts the new feedback-mode chip column."""
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    match = re.search(
        r"\.workbench-collab-topbar\s*\{[^}]*?grid-template-columns:\s*([^;]+);",
        css,
        re.DOTALL,
    )
    assert match, "topbar grid-template-columns rule not found"
    template = match.group(1)
    column_tokens = [t for t in re.split(r"\s+", template.strip()) if t]
    auto_count = column_tokens.count("auto")
    assert auto_count >= 3, (
        f"expected ≥3 'auto' columns to fit identity + ticket + feedback-mode chips; "
        f"got {auto_count} in '{template.strip()}'"
    )


def test_workbench_route_serves_chip_and_banner() -> None:
    """Live-served /workbench HTML contains chip + banner + copy strings."""
    server, thread = _start_demo_server()
    try:
        status, body = _get(server, "/workbench")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert 'id="workbench-feedback-mode"' in body
    assert 'data-feedback-mode="manual_feedback_override"' in body
    assert 'id="workbench-trust-banner"' in body
    assert "That mode is advisory." in body
    assert "Truth engine readings" in body
    assert "Hide for session" in body
    # P1-R2 fix: scope definition before advisory framing
    assert 'What "manual feedback" means here' in body


def test_bundle_route_does_not_serve_shell_chip() -> None:
    """`/workbench/bundle` (legacy 验收台) must NOT contain the shell-only chip/banner."""
    server, thread = _start_demo_server()
    try:
        status, body = _get(server, "/workbench/bundle")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert 'id="workbench-feedback-mode"' not in body
    assert 'id="workbench-trust-banner"' not in body

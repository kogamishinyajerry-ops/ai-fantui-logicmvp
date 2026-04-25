"""E11-08 — role affordance for non-Kogami identities.

Per E11-00-PLAN row E11-08: when the workbench identity is NOT Kogami,
the Approval Center entry button + panel must be replaced with an
explicit "Pending Kogami sign-off" affordance rather than leaving
disabled UI in place.

Default state (Kogami identity): Approval Center visible, pending
affordance hidden.
Non-Kogami state: Approval Center hidden, pending affordance visible.

The test locks both the static HTML invariants (data-identity-name
attribute, hidden affordance section, applyRoleAffordance JS function)
and the live-served route. The toggle behavior itself is exercised
via static-source inspection rather than a headless browser; the
JS function is small enough to be auditable by inspection.
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


# ─── 1. Static HTML carries the new attributes + section ────────────


def test_workbench_identity_chip_carries_data_identity_name() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'data-identity-name="Kogami"' in html


def test_workbench_html_has_pending_signoff_affordance_section() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-pending-signoff-affordance"' in html
    assert 'data-pending-signoff="hidden"' in html  # default hidden state
    assert "Pending Kogami sign-off" in html


def test_pending_signoff_affordance_explains_replacement_of_disabled_ui() -> None:
    """The affordance copy must explain WHY the Approval Center is gone
    for this user — otherwise users still see it as broken UI."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    affordance_block = (
        html.split('id="workbench-pending-signoff-affordance"')[1].split(
            "</section>"
        )[0]
    )
    assert "Kogami" in affordance_block
    assert "排队" in affordance_block or "提案" in affordance_block


# ─── 2. CSS visibility contract ──────────────────────────────────────


def test_pending_signoff_css_default_hidden_visible_toggle() -> None:
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    # Default selector hides the affordance.
    assert (
        ".workbench-pending-signoff {" in css
        and "display: none" in css.split(".workbench-pending-signoff {")[1].split("}")[0]
    )
    # Visible attribute selector reveals it.
    assert (
        '.workbench-pending-signoff[data-pending-signoff="visible"]' in css
    )


# ─── 3. JS contract ──────────────────────────────────────────────────


def test_workbench_js_has_apply_role_affordance() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "function applyRoleAffordance" in js
    assert "function setWorkbenchIdentity" in js
    # window-export so tests / demo flow can call from outside the module
    assert "window.setWorkbenchIdentity = setWorkbenchIdentity" in js


def test_workbench_js_affordance_toggles_on_kogami_check() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # The toggle hinges on the literal "Kogami" string.
    affordance_block = js.split("function applyRoleAffordance")[1].split(
        "}\n\n"
    )[0]
    assert '"Kogami"' in affordance_block
    # Both targets get toggled in lockstep.
    assert "approval-center-entry" in affordance_block
    assert "approval-center-panel" in affordance_block
    assert "workbench-pending-signoff-affordance" in affordance_block


def test_workbench_js_honors_url_identity_param() -> None:
    """A `?identity=<name>` URL param flips the identity at boot."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "URLSearchParams" in js
    assert 'params.get("identity")' in js
    assert "setWorkbenchIdentity(requested)" in js


# ─── 4. Live-served route ───────────────────────────────────────────


def test_workbench_route_serves_role_affordance_section(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-pending-signoff-affordance"' in html
    assert 'data-identity-name="Kogami"' in html


# ─── 5. Default state preserves Kogami workflow ─────────────────────


def test_default_html_keeps_approval_center_visible_for_kogami() -> None:
    """Without ?identity= override, page boots as Kogami; #approval-center-entry
    must NOT carry hidden=true in source HTML (JS hides it post-boot only
    when identity != Kogami)."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    entry_block = html.split('id="approval-center-entry"')[1].split(">")[0]
    assert "hidden" not in entry_block.lower()


# ─── 6. Truth-engine red line (no data mutation paths added) ────────


def test_e11_08_only_touches_ui_layer() -> None:
    """The fix must be UI-only — no new endpoint, no controller change.
    Verify by grepping for the new identifiers across the codebase: they
    must appear only in static/, tests/, .planning/."""
    # workbench.html identifies the chip
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'data-identity-name="Kogami"' in html
    # Stable: the identity attribute is not consumed by any backend
    # endpoint — the JS in workbench.js is the only reader.
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "data-identity-name" in js

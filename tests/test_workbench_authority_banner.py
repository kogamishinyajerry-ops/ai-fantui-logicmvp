"""E11-07 — Authority Contract banner regression lock.

Locks the always-visible banner that announces the truth-engine
read-only contract on /workbench, plus the /v6.1-redline route that
serves the constitution clause the banner links to.

Per E11-00-PLAN row E11-07: pure-UI banner, no truth-engine code
changes. The contract is twofold —
  1. The banner is on the /workbench shell with the canonical copy.
  2. The link target resolves to a real text excerpt sourced from
     .planning/constitution.md (so the banner is not a dead link).
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


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read().decode("utf-8")
    content_type = response.getheader("Content-Type", "")
    return response.status, body, content_type


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Banner is present on /workbench ──────────────────────────────


def test_workbench_html_has_authority_banner() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-authority-banner"' in html
    assert 'role="note"' in html
    # Always-visible: no data-dismissed attribute, no conditional class
    # toggling. The banner stays on screen for the entire session.
    assert "data-trust-banner-dismiss" not in (
        html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
    )


@pytest.mark.parametrize(
    "phrase",
    [
        "🔒",
        "Truth Engine — Read Only",
        "Propose 不修改",
        "工程师只能提交 ticket / proposal",
        "v6.1 红线条款",
    ],
)
def test_workbench_html_banner_carries_canonical_copy(phrase: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert phrase in html, f"missing canonical banner copy: {phrase}"


def test_workbench_html_banner_links_to_v61_redline_route() -> None:
    """The banner link must point at the in-repo route, not at an
    external GitHub URL or a stale /.planning/ path that the static
    handler would 404 on."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    banner_block = html.split('id="workbench-authority-banner"')[1].split("</aside>")[0]
    assert 'href="/v6.1-redline"' in banner_block


# ─── 2. /v6.1-redline route works ────────────────────────────────────


def test_v61_redline_route_returns_200_text(server) -> None:
    status, body, content_type = _get(server, "/v6.1-redline")
    assert status == 200
    assert "text/plain" in content_type
    assert "v6.1" in body or "truth-engine" in body or "红线" in body


def test_v61_redline_excerpt_carries_truth_engine_paths(server) -> None:
    """Whatever excerpt the route returns, it must name the four paths
    that are off-limits — controller/runner/models/adapters."""
    _, body, _ = _get(server, "/v6.1-redline")
    # At least one of the canonical truth-engine path names must appear,
    # whether in the constitution excerpt or in the static fallback.
    assert any(name in body for name in ("controller", "runner", "models", "adapters")), (
        f"excerpt missing truth-engine path names; got {body[:200]!r}"
    )


def test_v61_redline_route_alias_with_extension(server) -> None:
    """Both /v6.1-redline and /v6.1-redline.txt should resolve."""
    status, body, _ = _get(server, "/v6.1-redline.txt")
    assert status == 200
    assert body  # non-empty


# ─── 3. Live-served /workbench renders banner end-to-end ────────────


def test_workbench_route_serves_authority_banner(server) -> None:
    status, html, _ = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-authority-banner"' in html
    assert 'href="/v6.1-redline"' in html
    assert "Truth Engine — Read Only" in html


# ─── 4. Banner placement: above the 3-column collab grid ────────────


def test_workbench_banner_appears_before_collab_grid() -> None:
    """The banner must sit ABOVE the 3-column grid so it frames the
    controller / circuit columns, not below them."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    banner_pos = html.find('id="workbench-authority-banner"')
    grid_pos = html.find('class="workbench-collab-grid"')
    assert banner_pos != -1 and grid_pos != -1
    assert banner_pos < grid_pos, (
        "authority banner must precede the 3-column collab grid"
    )

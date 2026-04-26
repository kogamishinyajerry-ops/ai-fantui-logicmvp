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


# ─── 1. Truth-engine read-only chip is present on /workbench ────────
# P44-02: the bilingual authority banner was replaced with a small chip
# in the topbar so the circuit hero fits in the first viewport. The
# /v6.1-redline route still resolves so the chip's link is live.


def test_workbench_html_has_truth_engine_chip() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-truth-engine-chip"' in html
    assert "🔒 真值引擎只读" in html
    assert 'href="/v6.1-redline"' in html
    # The old multi-line banner must be gone.
    assert 'id="workbench-authority-banner"' not in html
    # Banner-only sentence ("Propose 不修改 ...") was carried only by the
    # full banner; if it leaks back in, the bigger chrome is back too.
    assert "Propose 不修改" not in html


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


# ─── 3. Live-served /workbench renders the chip end-to-end ──────────


def test_workbench_route_serves_truth_engine_chip(server) -> None:
    status, html, _ = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-truth-engine-chip"' in html
    assert 'href="/v6.1-redline"' in html
    assert "真值引擎只读" in html


# ─── 4. Chip placement: above the circuit hero ──────────────────────


def test_workbench_truth_engine_chip_appears_before_circuit_hero() -> None:
    """P44-02 (replaces banner-before-hero ordering test): the chip
    must sit ABOVE the circuit hero so the read-only contract is visible
    before the engineer interacts with the panel."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    chip_pos = html.find('id="workbench-truth-engine-chip"')
    hero_pos = html.find('id="workbench-circuit-hero"')
    assert chip_pos != -1 and hero_pos != -1
    assert chip_pos < hero_pos, (
        "truth-engine chip must precede the circuit hero so the read-only "
        "contract is visible before the engineer scrolls into the panel"
    )

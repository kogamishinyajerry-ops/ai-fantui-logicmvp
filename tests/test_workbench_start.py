"""E11-02 — onboarding landing /workbench/start.

These tests lock the public contract introduced by sub-phase E11-02:

* `/workbench/start` returns a 200 HTML response with a 5-tile selector.
* Each persona-aligned tile carries a stable `id` + `data-persona` +
  `data-intent` so future E2E coverage and ticket templates can target it.
* Each tile deep-links into `/workbench` with an `intent=` query parameter
  (and optional `#fragment`) — preserving the existing workbench shell
  contract while letting the onboarding page steer behavior.

Truth-engine surfaces are NOT touched by E11-02, only static assets and
the demo_server route table.
"""

from __future__ import annotations

import http.client
import re
import threading
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


class _TileCollector(HTMLParser):
    """Collect <a class="ws-tile"> attribute maps keyed by id."""

    def __init__(self) -> None:
        super().__init__()
        self.tiles: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = {key: value or "" for key, value in attrs}
        classes = attr_map.get("class", "").split()
        if "ws-tile" not in classes:
            return
        tile_id = attr_map.get("id", "")
        if tile_id:
            self.tiles[tile_id] = attr_map


def _parse_start_tiles() -> dict[str, dict[str, str]]:
    parser = _TileCollector()
    parser.feed((STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8"))
    return parser.tiles


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


@pytest.mark.parametrize("path", ["/workbench/start", "/workbench/start.html"])
def test_workbench_start_route_serves_html(path: str) -> None:
    server, thread = _start_demo_server()
    try:
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200, f"{path} did not return 200"
    assert "Workbench" in body
    assert 'id="workbench-start-main"' in body
    assert "ws-tile" in body


def test_workbench_start_static_assets_resolve() -> None:
    server, thread = _start_demo_server()
    try:
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        connection.request("GET", "/workbench_start.css")
        response = connection.getresponse()
        css_body = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert ".ws-tile" in css_body, "stylesheet missing tile selector"


def test_workbench_start_has_five_persona_tiles() -> None:
    tiles = _parse_start_tiles()
    expected_ids = {
        "ws-tile-learn-demo",
        "ws-tile-engineer-probe",
        "ws-tile-customer-repro",
        "ws-tile-approval-review",
        "ws-tile-vv-trace",
    }
    assert expected_ids <= set(tiles), (
        f"missing persona tiles: {expected_ids - set(tiles)}"
    )


def test_workbench_start_tiles_carry_persona_metadata() -> None:
    tiles = _parse_start_tiles()
    expected_persona = {
        "ws-tile-learn-demo":      "P1",
        "ws-tile-engineer-probe":  "P2",
        "ws-tile-customer-repro":  "P5",
        "ws-tile-approval-review": "KOGAMI",
        "ws-tile-vv-trace":        "P4",
    }
    for tile_id, persona in expected_persona.items():
        attrs = tiles[tile_id]
        assert attrs.get("data-persona") == persona, (
            f"{tile_id}: expected data-persona={persona}, got {attrs.get('data-persona')!r}"
        )
        assert attrs.get("data-intent"), f"{tile_id}: missing data-intent"


def test_workbench_start_tiles_deep_link_into_workbench() -> None:
    tiles = _parse_start_tiles()
    for tile_id, attrs in tiles.items():
        href = attrs.get("href", "")
        assert href.startswith("/workbench?intent="), (
            f"{tile_id}: href {href!r} must deep-link into /workbench with intent= query"
        )
        intent = attrs.get("data-intent", "")
        assert f"intent={intent}" in href, (
            f"{tile_id}: data-intent {intent!r} must match href intent= value"
        )


def test_workbench_start_displays_redline_section() -> None:
    """Truth-engine boundary must be visible on the onboarding page itself —
    no user should reach the workbench without first seeing what is read-only."""
    body = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
    assert "ws-redline" in body
    assert "controller.py" in body
    assert re.search(r"19[- ]node truth engine", body), (
        "onboarding page must call out the 19-node truth engine as read-only"
    )
    assert "wow_a fixture" in body

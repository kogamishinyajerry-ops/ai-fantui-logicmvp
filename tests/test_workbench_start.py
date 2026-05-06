"""/workbench/start onboarding landing contract.

These tests lock the public start-page contract:

* `/workbench/start` returns a 200 HTML response with a 5-persona +
  1-role (Kogami) tile selector — 6 entries total.
* Each tile carries a stable `id` + `data-persona` + `data-intent`.
* Each tile deep-links into `/workbench` with an `intent=` query
  parameter. Hash fragments may only point at ids that actually exist
  in `workbench.html` (no dead anchors that drop users at the page top).
* Arbitrary `?intent=` payloads must NOT be reflected by `/workbench`.
* The truth-engine red-line is visible on the onboarding page itself.

Truth-engine surfaces are NOT touched by this start page.
"""

from __future__ import annotations

import http.client
import re
import threading
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pytest

from well_harness.demo_server import DemoRequestHandler  # type: ignore[import-untyped]


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


class _IdCollector(HTMLParser):
    """Collect every element id in an HTML file."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.add(value)


def _parse_start_tiles() -> dict[str, dict[str, str]]:
    parser = _TileCollector()
    parser.feed((STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8"))
    return parser.tiles


def _parse_workbench_ids() -> set[str]:
    parser = _IdCollector()
    parser.feed((STATIC_DIR / "workbench.html").read_text(encoding="utf-8"))
    return parser.ids


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


def test_workbench_start_has_six_entry_tiles() -> None:
    """5 personas (P1-P5) + 1 role (KOGAMI Approval) = 6 entries."""
    tiles = _parse_start_tiles()
    expected_ids = {
        "ws-tile-learn-demo",       # P1
        "ws-tile-engineer-probe",   # P2
        "ws-tile-demo-stage",       # P3
        "ws-tile-customer-repro",   # P5
        "ws-tile-approval-review",  # KOGAMI (role, not persona)
        "ws-tile-vv-trace",         # P4
    }
    assert expected_ids <= set(tiles), (
        f"missing entry tiles: {expected_ids - set(tiles)}"
    )
    extras = set(tiles) - expected_ids
    assert not extras, f"unexpected extra tiles: {extras}"


def test_workbench_start_tiles_carry_persona_metadata() -> None:
    tiles = _parse_start_tiles()
    expected_persona = {
        "ws-tile-learn-demo":      "P1",
        "ws-tile-engineer-probe":  "P2",
        "ws-tile-demo-stage":      "P3",
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


def test_workbench_start_tile_hash_targets_exist_or_absent() -> None:
    """Dead hash fragments must not return.

    Tiles may either omit a hash fragment, or use one that resolves to a real
    id in workbench.html. No dead anchors allowed — they make the tile lie
    about 'landing at the starter task'.
    """
    tiles = _parse_start_tiles()
    workbench_ids = _parse_workbench_ids()
    for tile_id, attrs in tiles.items():
        href = attrs.get("href", "")
        fragment = urlparse(href).fragment
        if fragment:
            assert fragment in workbench_ids, (
                f"{tile_id}: hash fragment #{fragment!r} not present in workbench.html "
                f"(would drop user at page top instead of starter task)"
            )


def test_workbench_route_ignores_arbitrary_intent_param() -> None:
    """R1-F4 verbatim: `/workbench` must not reflect arbitrary intent= payloads."""
    server, thread = _start_demo_server()
    try:
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        connection.request("GET", "/workbench?intent=%3Csvg%20onload%3Dalert(1)%3E")
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert "Control Logic Workbench" in body
    assert "<svg onload=alert(1)>" not in body


def test_workbench_start_displays_redline_section() -> None:
    """Truth-engine boundary must be visible on the onboarding page itself —
    no user should reach the workbench without first seeing what is read-only."""
    body = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
    assert "ws-redline" in body
    assert "controller.py" in body
    assert re.search(r"19[- ]node truth engine", body), (
        "onboarding page must call out the 19-node truth engine as read-only"
    )
    assert "参考场景与证据包" in body


def test_workbench_start_copy_matches_current_surface_truth() -> None:
    """The start page must not expose stale internal roadmap claims."""
    body = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
    forbidden_fragments = {
        "E11",
        "本期",
        "起手卡片已上线",
        "起手卡 已在",
        "workbench</code> 顶部「起手卡」",
        "角色判定逻辑未实现",
        "没有 approval-action handler",
        "后才上线",
    }

    for fragment in forbidden_fragments:
        assert fragment not in body

    assert "当前主面板顶部是控制逻辑电路" in body
    assert "浏览器入口不能绕过证据链" in body


def test_workbench_start_explains_persona_vs_role_axis() -> None:
    """R1-F3 mitigation: page must explain that KOGAMI is a role lane (not a
    persona) so the surface isn't mis-sold as 'persona-aligned'."""
    body = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
    assert 'class="ws-axes"' in body, "missing role-vs-persona axis explainer"
    assert "KOGAMI" in body
    assert "persona" in body.lower()

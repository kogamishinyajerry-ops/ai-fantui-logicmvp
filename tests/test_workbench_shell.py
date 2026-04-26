from __future__ import annotations

import http.client
import threading
from html.parser import HTMLParser
from pathlib import Path

from http.server import ThreadingHTTPServer

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.data_attrs: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        element_id = attr_map.get("id")
        if element_id:
            self.ids.add(element_id)
            self.data_attrs[element_id] = {
                key: value for key, value in attr_map.items() if key.startswith("data-")
            }


def parse_workbench_ids() -> IdCollector:
    parser = IdCollector()
    parser.feed((STATIC_DIR / "workbench.html").read_text(encoding="utf-8"))
    return parser


def start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_workbench_route_serves_shell() -> None:
    server, thread = start_demo_server()
    try:
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        connection.request("GET", "/workbench")
        response = connection.getresponse()
        html = response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert "Control Logic Workbench" in html
    # P44-01: the workbench is centered on the control logic panel hero,
    # not the prior empty 3-column shell. Lock the new hero placeholder.
    assert 'id="workbench-circuit-hero"' in html
    assert 'data-circuit-fragment-endpoint="/api/workbench/circuit-fragment"' in html


def test_workbench_shell_has_circuit_hero() -> None:
    """P44-01 (replaces test_workbench_shell_has_three_independent_columns):
    the workbench must mount a single circuit-hero region as the page
    body, not the previous 3-column collab grid."""
    ids = parse_workbench_ids().ids

    assert "workbench-circuit-hero" in ids
    assert "workbench-circuit-hero-mount" in ids
    assert "workbench-circuit-hero-title" in ids
    # The old per-column ids must NOT appear (regression guard).
    assert "workbench-control-panel" not in ids
    assert "workbench-document-panel" not in ids
    assert "workbench-circuit-panel" not in ids


def test_workbench_shell_has_identity_ticket_and_system_topbar() -> None:
    ids = parse_workbench_ids().ids

    assert "workbench-topbar" in ids
    assert "workbench-identity" in ids
    assert "workbench-ticket" in ids
    assert "workbench-system-select" in ids


def test_workbench_shell_has_annotation_inbox_skeleton() -> None:
    ids = parse_workbench_ids().ids

    assert "annotation-inbox" in ids
    assert "annotation-inbox-list" in ids


def test_workbench_shell_has_kogami_approval_entry() -> None:
    parser = parse_workbench_ids()

    assert "approval-center-entry" in parser.ids
    assert parser.data_attrs["approval-center-entry"].get("data-role") == "KOGAMI"


def test_workbench_javascript_exposes_circuit_hero_hydrator() -> None:
    """P44-01 (replaces failure-isolation hooks for the prior 3-column
    boot): the workbench JS must expose a single circuit-hero hydrator
    that fetches the SVG fragment endpoint and injects it into the
    hero mount. The previous per-column boot functions are gone."""
    script = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")

    assert "function bootWorkbenchCircuitHero" in script
    assert "function bootWorkbenchShell" in script
    assert "/api/workbench/circuit-fragment" in script
    # Per-column boot functions removed; their presence implies the wrong
    # abstraction is back.
    assert "function bootWorkbenchControlPanel" not in script
    assert "function bootWorkbenchDocumentPanel" not in script
    assert "function bootWorkbenchCircuitPanel" not in script

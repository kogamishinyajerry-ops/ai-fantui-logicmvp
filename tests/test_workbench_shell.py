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
    assert 'id="workbench-control-panel"' in html


def test_workbench_shell_has_three_independent_columns() -> None:
    ids = parse_workbench_ids().ids

    assert "workbench-control-panel" in ids
    assert "workbench-document-panel" in ids
    assert "workbench-circuit-panel" in ids


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


def test_workbench_javascript_exposes_failure_isolation_hooks() -> None:
    script = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")

    assert "bootWorkbenchControlPanel" in script
    assert "bootWorkbenchDocumentPanel" in script
    assert "bootWorkbenchCircuitPanel" in script
    assert "bootWorkbenchColumnSafely" in script

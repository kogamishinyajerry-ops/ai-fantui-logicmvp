"""E11-09 — dual-route fix locks /workbench shell vs /workbench/bundle split.

Before E11-09 (PR #13), `/workbench` served a single 1078-line file with
TWO `<h1>` headings: "Control Logic Workbench" (Epic-06..10 shell) +
"Workbench Bundle 验收台" (legacy bundle). The product-identity split
was 3 of 5 personas' BLOCKER #1 in E11-01 baseline review.

After E11-09:
- `/workbench` serves shell only (1 h1: "Control Logic Workbench")
- `/workbench/bundle` serves the legacy bundle page (1 h1: "Workbench
  Bundle 验收台")

This test file locks the contract so any regression is caught at CI time
rather than user time.
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


@pytest.mark.parametrize("path", ["/workbench", "/workbench.html", "/expert/workbench.html"])
def test_workbench_route_serves_shell_only(path: str) -> None:
    """`/workbench` (and aliases) serve the Epic-06..10 shell with exactly 1 h1."""
    server, thread = _start_demo_server()
    try:
        status, body = _get(server, path)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert "<title>Control Logic Workbench</title>" in body
    h1_count = len(re.findall(r"<h1[ >]", body))
    assert h1_count == 1, f"{path} must have exactly 1 h1, found {h1_count}"
    assert "Control Logic Workbench</h1>" in body
    # Bundle h1 must NOT leak onto the shell page
    assert "Workbench Bundle 验收台</h1>" not in body
    # Shell-essential ids still present (regression guard)
    assert 'id="workbench-control-panel"' in body
    assert 'id="approval-center-entry"' in body


@pytest.mark.parametrize("path", ["/workbench/bundle", "/workbench/bundle.html", "/workbench_bundle.html"])
def test_workbench_bundle_route_serves_bundle_only(path: str) -> None:
    """`/workbench/bundle` (and aliases) serve the legacy 验收台 with exactly 1 h1."""
    server, thread = _start_demo_server()
    try:
        status, body = _get(server, path)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert "<title>Well Harness Workbench Bundle 验收台</title>" in body
    h1_count = len(re.findall(r"<h1[ >]", body))
    assert h1_count == 1, f"{path} must have exactly 1 h1, found {h1_count}"
    assert 'id="workbench-page-title"' in body
    assert "Workbench Bundle 验收台</h1>" in body
    # Shell h1 must NOT leak onto the bundle page
    assert "Control Logic Workbench</h1>" not in body
    # Bundle-essential UI present (regression guard)
    assert 'data-workbench-preset="ready_archived"' in body
    assert "一键预设验收卡" in body


def test_shell_and_bundle_files_share_no_h1() -> None:
    """Static-file invariant: each file has exactly 1 h1 and they don't overlap."""
    shell_html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    bundle_html = (STATIC_DIR / "workbench_bundle.html").read_text(encoding="utf-8")

    assert len(re.findall(r"<h1[ >]", shell_html)) == 1, "shell file must have exactly 1 h1"
    assert len(re.findall(r"<h1[ >]", bundle_html)) == 1, "bundle file must have exactly 1 h1"
    assert "Control Logic Workbench</h1>" in shell_html
    assert "Workbench Bundle 验收台</h1>" in bundle_html
    # Cross-file leakage guard
    assert "Workbench Bundle 验收台</h1>" not in shell_html
    assert "Control Logic Workbench</h1>" not in bundle_html


def test_workbench_js_has_bundle_sentinel_guard() -> None:
    """E11-09 R1 BLOCKER fix: workbench.js is shared between /workbench (shell)
    and /workbench/bundle (bundle) but its DOMContentLoaded handler used to
    unconditionally bind bundle-only elements (e.g. #workbench-packet-json,
    #load-reference-packet, #run-workbench-bundle), throwing
    `Cannot read properties of null (reading 'addEventListener')` on the
    shell page.

    The fix is a sentinel guard that detects whether bundle DOM is present
    by probing for `#workbench-packet-json` (the bundle's textarea input),
    early-returning on the shell page before installToolbarHandlers /
    updateWorkflowUI / loadBootstrapPayload run.

    This test is a structural-static check — it does NOT execute JS. A real
    JS-boot smoke test (jsdom or headless browser) is deferred to E11-11
    e2e coverage sub-phase per v2.3 §C-Opus governance-weight calibration.
    """
    js_text = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")

    # 1. Sentinel probe must be present
    assert 'getElementById("workbench-packet-json")' in js_text, (
        "missing E11-09 sentinel probe — bundle/shell discriminator removed?"
    )

    # 2. Early-return must be present
    assert "if (!onBundlePage)" in js_text, (
        "missing E11-09 onBundlePage early-return guard"
    )

    # 3. Guard must precede the bundle installers in DOMContentLoaded handler
    sentinel_pos = js_text.index('getElementById("workbench-packet-json")')
    install_toolbar_call_pos = js_text.index("installToolbarHandlers();", sentinel_pos)
    update_workflow_call_pos = js_text.index("updateWorkflowUI();", sentinel_pos)
    load_bootstrap_call_pos = js_text.index("loadBootstrapPayload()", sentinel_pos)

    assert sentinel_pos < install_toolbar_call_pos, (
        "E11-09 guard must precede installToolbarHandlers"
    )
    assert sentinel_pos < update_workflow_call_pos, (
        "E11-09 guard must precede updateWorkflowUI"
    )
    assert sentinel_pos < load_bootstrap_call_pos, (
        "E11-09 guard must precede loadBootstrapPayload"
    )

    # 4. Shell-essential boot calls (bootWorkbenchShell, installViewModeHandlers)
    #    must appear BEFORE the guard so they still run on /workbench.
    shell_boot_pos = js_text.index("bootWorkbenchShell();")
    view_mode_pos = js_text.index("installViewModeHandlers();")
    assert shell_boot_pos < sentinel_pos, (
        "bootWorkbenchShell must run on /workbench (before bundle guard)"
    )
    assert view_mode_pos < sentinel_pos, (
        "installViewModeHandlers must run on /workbench (before bundle guard)"
    )

"""E11-11 — JS-boot smoke tests for /workbench (Playwright + Chromium).

Closes deferred JS verification debt accumulated across:
- E11-08 (role affordance — applyRoleAffordance + setWorkbenchIdentity +
  ?identity= URL param parsing — only structural-static tests until now)
- E11-13 (bundle/shell sentinel guard — only static-source check until now)
- E11-15c (Chinese-first DOM rendering — only HTML-string assertions
  until now; this verifies the strings actually render in a real DOM)

Marked `@pytest.mark.e2e` (the suite is deselected by the default
addopts in pyproject.toml `-m 'not e2e'`). Runs only when invoked
explicitly via `pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py`.

Reuses the session-scoped `demo_server` fixture from
`tests/e2e/conftest.py` which boots `well_harness.demo_server` on
port 8799 (the port must be free).

Reproducible install (clean checkout):
    pip install -e '.[dev,e2e]'
    playwright install chromium
    pytest -m e2e tests/e2e/test_workbench_js_boot_smoke.py

Skips gracefully if Playwright Python driver is missing
(`pytest.importorskip`); skips per-fixture if the Chromium browser
binary is missing.
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.e2e

# Skip the whole module if Playwright sync API or its browsers are missing.
playwright_sync_api = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"chromium browser not installed: {exc}")
        try:
            yield b
        finally:
            b.close()


def _new_page_with_error_capture(browser):
    page = browser.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    return page, errors


def _goto_shell_workbench(page, url: str):
    """Wait for deterministic DOM readiness instead of global network quiet."""
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("#workbench-identity", state="attached")
    page.wait_for_function(
        """
        () => typeof window.setWorkbenchIdentity === 'function'
          && document.getElementById('workbench-identity')
        """
    )


def _goto_bundle_workbench(page, url: str):
    """The bundle page has its own deterministic readiness sentinel."""
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("#workbench-packet-json", state="attached")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-packet-json')
          && document.querySelector('[data-workbench-preset]')
        """
    )


# ─── E11-08 closure: identity affordance JS toggle (4 tests) ─────────


def test_default_identity_kogami_renders_identity_chip(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    state = page.evaluate(
        """
        () => ({
          identityAttr: document.getElementById('workbench-identity')
            ?.getAttribute('data-identity-name'),
          identityText: document.getElementById('workbench-identity')?.textContent.trim(),
        })
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert state["identityAttr"] == "Kogami"
    assert "Kogami / Engineer" in state["identityText"]


def test_engineer_identity_url_param_updates_identity_chip(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench?identity=Engineer")
    state = page.evaluate(
        """
        () => ({
          identityAttr: document.getElementById('workbench-identity')
            ?.getAttribute('data-identity-name'),
          identityText: document.getElementById('workbench-identity')?.textContent.trim(),
        })
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert state["identityAttr"] == "Engineer"
    assert "Engineer / Engineer" in state["identityText"]


def test_set_workbench_identity_window_function_toggles_dom(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    after = page.evaluate(
        """
        () => {
          const ok = window.setWorkbenchIdentity('Engineer');
          return {
            ok,
            identityAttr: document.getElementById('workbench-identity')
              ?.getAttribute('data-identity-name'),
            identityText: document.getElementById('workbench-identity')?.textContent.trim(),
          };
        }
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert after["ok"] is True
    assert after["identityAttr"] == "Engineer"
    assert "Engineer / Engineer" in after["identityText"]


def test_set_workbench_identity_blank_returns_false(demo_server, browser):
    page, _ = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    result = page.evaluate("() => window.setWorkbenchIdentity('   ')")
    assert result is False


# ─── E11-13 closure: bundle/shell sentinel guard (2 tests) ───────────


def test_shell_workbench_boots_without_js_errors(demo_server, browser):
    """E11-13 R1 BLOCKER fix: the shell page must not throw on bundle-only
    DOM (the sentinel `getElementById("workbench-packet-json")` early-returns
    before bundle-bound handlers run)."""
    page, errors = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.wait_for_timeout(500)
    assert errors == [], f"shell boot threw JS errors: {errors}"


def test_bundle_workbench_boots_without_js_errors(demo_server, browser):
    """E11-13: the bundle page must boot fully — sentinel guard does NOT
    block it because #workbench-packet-json IS present on /workbench/bundle."""
    page, errors = _new_page_with_error_capture(browser)
    _goto_bundle_workbench(page, f"{demo_server}/workbench/bundle")
    page.wait_for_timeout(500)
    assert errors == [], f"bundle boot threw JS errors: {errors}"


# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────


def test_workbench_renders_chinese_first_headers_in_dom(demo_server, browser):
    """E11-15/15b/15c locked HTML-string contracts; this verifies the
    actual rendered DOM after browser parse + JS boot also delivers
    Chinese-first across every header surface."""
    page, _ = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    headers = page.evaluate(
        """
        () => ({
          h1: document.querySelector('.workbench-collab-brand h1')?.textContent.trim(),
          identityLabel: document.querySelector('#workbench-identity span')?.textContent.trim(),
          newH2: document.querySelector('#workbench-tool-new-title')?.textContent.trim(),
          simH2: document.querySelector('#workbench-sim-panel-title')?.textContent.trim(),
          cockpitH2: document.querySelector('#workbench-cockpit-panel-title')?.textContent.trim(),
          specH2: document.querySelector('#workbench-spec-panel-title')?.textContent.trim(),
          proposalH2: document.querySelector('#workbench-suggestion-flow-title')?.textContent.trim(),
          approvalH2: document.querySelector('#workbench-tool-approve-title')?.textContent.trim(),
          monitorH2: document.querySelector('#workbench-tool-monitor-title')?.textContent.trim(),
        })
        """
    )
    # h1: "控制逻辑工作台 · Control Logic Workbench"
    assert headers["h1"].startswith("控制逻辑工作台"), headers["h1"]
    assert "Control Logic Workbench" in headers["h1"]
    # compact topbar identity label remains Chinese-first.
    assert headers["identityLabel"].startswith("身份"), headers["identityLabel"]
    # current tool and panel h2s: Chinese-first per workbench shell contract.
    assert headers["newH2"].startswith("新建逻辑控制电路"), headers["newH2"]
    assert headers["simH2"].startswith("反推仿真模拟"), headers["simH2"]
    assert headers["cockpitH2"].startswith("反推演示舱"), headers["cockpitH2"]
    assert headers["specH2"].startswith("反推需求文档"), headers["specH2"]
    assert headers["proposalH2"].startswith("提交修改建议"), headers["proposalH2"]
    assert headers["approvalH2"].startswith("审批中心"), headers["approvalH2"]
    assert headers["monitorH2"].startswith("运行监控"), headers["monitorH2"]


def test_workbench_buttons_render_chinese_first_in_dom(demo_server, browser):
    """E11-15b bilingualized 2 control-panel buttons + the Approval Center
    entry button. Verify rendered text starts with the Chinese half."""
    page, _ = _new_page_with_error_capture(browser)
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    button_texts = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('button.workbench-toolbar-button'))
          .map(b => b.textContent.trim())
        """
    )
    nav_texts = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('.workbench-dock-btn-label'))
          .map(b => b.textContent.trim())
        """
    )
    # Find current Chinese-first workbench commands by their Chinese prefix.
    has_create = any(t.startswith("+ 创建电路") for t in button_texts)
    has_interpret = any(t.startswith("解读建议") for t in button_texts)
    has_approval_nav = "审批" in nav_texts
    assert has_create, f"missing 创建电路 button; got: {button_texts}"
    assert has_interpret, f"missing 解读建议 button; got: {button_texts}"
    assert has_approval_nav, f"missing 审批 nav button; got: {nav_texts}"


def test_workbench_evidence_archive_exports_gate_claims_and_blockers(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-prepare-archive-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-evidence-archive-output');
          return output && output.value.includes('well-harness-workbench-evidence-archive');
        }
        """
    )
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())

    blocker_gates = {blocker["gate"] for blocker in archive["known_blockers"]}
    assert errors == [], f"page JS errors: {errors}"
    assert archive["kind"] == "well-harness-workbench-evidence-archive"
    assert archive["archive_scope"] == "local_draft_download"
    assert archive["gate_claims"]["mypy_strict_clean"] == "not_claimed"
    assert archive["gate_claims"]["e2e_49_49"] == "not_claimed"
    assert "PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json" in blocker_gates
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"
    assert archive["red_line_metadata"]["dal_pssa_impact"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False
    assert archive["red_line_metadata"]["live_linear_mutation"] is False
    assert archive["checksums"]["gate_claims_checksum"]
    assert archive["checksums"]["known_blockers_checksum"]


def test_workbench_interface_binding_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    first_binding = draft["hardware_bindings"][0]
    logic1 = next(node for node in draft["nodes"] if node["id"] == "logic1")
    assert first_binding["owner_kind"] == "node"
    assert first_binding["owner_id"] == "logic1"
    assert first_binding["hardware_id"] == "TR-LRU-001"
    assert first_binding["cable"] == "CBL-TR-A"
    assert first_binding["connector"] == "J1"
    assert first_binding["port_local"] == "logic1:out"
    assert first_binding["port_peer"] == "TR-LRU-001:J1"
    assert first_binding["evidence_status"] == "ui_draft"
    assert first_binding["truth_effect"] == "none"
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-001"

    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.fill("#workbench-draft-json-buffer", json.dumps(draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_binding = round_trip["hardware_bindings"][0]
    assert round_trip_binding["hardware_id"] == "TR-LRU-001"
    assert round_trip_binding["cable"] == "CBL-TR-A"
    assert round_trip_binding["connector"] == "J1"
    assert round_trip_binding["port_local"] == "logic1:out"
    assert round_trip_binding["port_peer"] == "TR-LRU-001:J1"

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["hardware_bindings"][0]["hardware_id"] == "TR-LRU-001"
    assert archive["hardware_bindings"][0]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_bindings_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False

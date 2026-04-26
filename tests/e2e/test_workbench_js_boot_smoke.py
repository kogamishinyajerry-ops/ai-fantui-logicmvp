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


# ─── E11-08 closure: role affordance JS toggle (4 tests) ─────────────


def test_default_identity_kogami_shows_approval_center(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    state = page.evaluate(
        """
        () => ({
          identityAttr: document.getElementById('workbench-identity')
            ?.getAttribute('data-identity-name'),
          entryHidden: document.getElementById('approval-center-entry')?.hidden,
          panelHidden: document.getElementById('approval-center-panel')?.hidden,
          affState: document.getElementById('workbench-pending-signoff-affordance')
            ?.getAttribute('data-pending-signoff'),
        })
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert state["identityAttr"] == "Kogami"
    assert state["entryHidden"] is False
    assert state["panelHidden"] is False
    assert state["affState"] == "hidden"


def test_engineer_identity_url_param_swaps_to_pending_affordance(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench?identity=Engineer", wait_until="networkidle")
    state = page.evaluate(
        """
        () => ({
          identityAttr: document.getElementById('workbench-identity')
            ?.getAttribute('data-identity-name'),
          entryHidden: document.getElementById('approval-center-entry')?.hidden,
          entryAriaDisabled: document.getElementById('approval-center-entry')
            ?.getAttribute('aria-disabled'),
          panelHidden: document.getElementById('approval-center-panel')?.hidden,
          affState: document.getElementById('workbench-pending-signoff-affordance')
            ?.getAttribute('data-pending-signoff'),
        })
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert state["identityAttr"] == "Engineer"
    assert state["entryHidden"] is True
    assert state["entryAriaDisabled"] == "true"
    assert state["panelHidden"] is True
    assert state["affState"] == "visible"


def test_set_workbench_identity_window_function_toggles_dom(demo_server, browser):
    page, errors = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    after = page.evaluate(
        """
        () => {
          const ok = window.setWorkbenchIdentity('Engineer');
          return {
            ok,
            affState: document.getElementById('workbench-pending-signoff-affordance')
              ?.getAttribute('data-pending-signoff'),
            entryHidden: document.getElementById('approval-center-entry')?.hidden,
          };
        }
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert after["ok"] is True
    assert after["affState"] == "visible"
    assert after["entryHidden"] is True


def test_set_workbench_identity_blank_returns_false(demo_server, browser):
    page, _ = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    result = page.evaluate("() => window.setWorkbenchIdentity('   ')")
    assert result is False


# ─── E11-13 closure: bundle/shell sentinel guard (2 tests) ───────────


def test_shell_workbench_boots_without_js_errors(demo_server, browser):
    """E11-13 R1 BLOCKER fix: the shell page must not throw on bundle-only
    DOM (the sentinel `getElementById("workbench-packet-json")` early-returns
    before bundle-bound handlers run)."""
    page, errors = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    page.wait_for_timeout(500)
    assert errors == [], f"shell boot threw JS errors: {errors}"


def test_bundle_workbench_boots_without_js_errors(demo_server, browser):
    """E11-13: the bundle page must boot fully — sentinel guard does NOT
    block it because #workbench-packet-json IS present on /workbench/bundle."""
    page, errors = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench/bundle", wait_until="networkidle")
    page.wait_for_timeout(500)
    assert errors == [], f"bundle boot threw JS errors: {errors}"


# ─── E11-15c closure: Chinese-first DOM render (2 tests) ─────────────


def test_workbench_renders_chinese_first_headers_in_dom(demo_server, browser):
    """E11-15/15b/15c locked HTML-string contracts; this verifies the
    actual rendered DOM after browser parse + JS boot also delivers
    Chinese-first across every header surface."""
    page, _ = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    headers = page.evaluate(
        """
        () => ({
          h1: document.querySelector('.workbench-collab-brand h1')?.textContent.trim(),
          pageEyebrow: document.querySelector('.workbench-collab-brand .eyebrow')?.textContent.trim(),
          probeH2: document.querySelector('#workbench-control-panel h2')?.textContent.trim(),
          docH2: document.querySelector('#workbench-document-panel h2')?.textContent.trim(),
          circuitH2: document.querySelector('#workbench-circuit-panel h2')?.textContent.trim(),
          reviewH2: document.querySelector('#annotation-inbox h2')?.textContent.trim(),
          approvalH2: document.querySelector('#approval-center-title')?.textContent.trim(),
        })
        """
    )
    # h1: "控制逻辑工作台 · Control Logic Workbench"
    assert headers["h1"].startswith("控制逻辑工作台"), headers["h1"]
    assert "Control Logic Workbench" in headers["h1"]
    # eyebrow: "工程师工作区" (E11-15c — distinct from h1)
    assert headers["pageEyebrow"] == "工程师工作区"
    # column h2s: Chinese-first per E11-15c
    assert headers["probeH2"].startswith("探针与追踪"), headers["probeH2"]
    assert headers["docH2"].startswith("标注与提案"), headers["docH2"]
    assert headers["circuitH2"].startswith("移交与跟踪"), headers["circuitH2"]
    # inbox + approval h2: bilingual per E11-15b
    assert headers["reviewH2"].startswith("审核队列"), headers["reviewH2"]
    assert headers["approvalH2"].startswith("Kogami 提案审批"), headers["approvalH2"]


def test_workbench_buttons_render_chinese_first_in_dom(demo_server, browser):
    """E11-15b bilingualized 2 control-panel buttons + the Approval Center
    entry button. Verify rendered text starts with the Chinese half."""
    page, _ = _new_page_with_error_capture(browser)
    page.goto(f"{demo_server}/workbench", wait_until="networkidle")
    button_texts = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('button.workbench-toolbar-button'))
          .map(b => b.textContent.trim())
        """
    )
    # Find the 3 known bilingual buttons by their Chinese prefix.
    has_load = any(t.startswith("加载当前工单") for t in button_texts)
    has_snapshot = any(t.startswith("快照当前状态") for t in button_texts)
    has_approval = any(t.startswith("审批中心") for t in button_texts)
    assert has_load, f"missing 加载当前工单 button; got: {button_texts}"
    assert has_snapshot, f"missing 快照当前状态 button; got: {button_texts}"
    assert has_approval, f"missing 审批中心 button; got: {button_texts}"

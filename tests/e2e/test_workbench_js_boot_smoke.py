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

import csv
import io
import json
from pathlib import Path
from typing import Any, Iterator

import pytest

pytestmark = pytest.mark.e2e

# Skip the whole module if Playwright sync API or its browsers are missing.
playwright_sync_api = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402
from well_harness.workbench_large_graph_stress_pack import (  # noqa: E402
    large_sandbox_stress_pack,
)

_OPEN_PAGES: list[Any] = []
_ARTIFACT_DIR = Path("artifacts/workbench-goal-canvas-panel")


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


@pytest.fixture(autouse=True)
def close_open_pages_after_test() -> Iterator[None]:
    yield
    while _OPEN_PAGES:
        page = _OPEN_PAGES.pop()
        try:
            if not page.is_closed():
                page.close()
        except Exception:
            pass


def _new_page_with_error_capture(browser):
    page = browser.new_page()
    _OPEN_PAGES.append(page)
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    return page, errors


def _open_workbench_inspector_mode(page: Any, mode: str) -> None:
    if mode not in {"node", "run", "evidence", "handoff"}:
        raise ValueError(f"unknown workbench inspector mode: {mode}")
    page.wait_for_selector("#workbench-evidence-inspector", state="attached")
    page.evaluate(
        """
        (mode) => {
          const inspector = document.getElementById('workbench-evidence-inspector');
          if (!inspector) return;
          inspector.setAttribute('data-inspector-open', 'true');
          inspector.setAttribute('data-inspector-mode-active', mode);
          document.body.setAttribute('data-workbench-inspector-open', 'true');
          for (const button of document.querySelectorAll('[data-inspector-mode]')) {
            const isActive = button.getAttribute('data-inspector-mode') === mode;
            button.setAttribute('aria-selected', isActive ? 'true' : 'false');
            button.setAttribute('tabindex', isActive ? '0' : '-1');
          }
          for (const panel of document.querySelectorAll('[data-inspector-panel]')) {
            const isActive = panel.getAttribute('data-inspector-panel') === mode;
            panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
          }
        }
        """,
        mode,
    )
    page.click(f'[data-inspector-mode="{mode}"]')
    page.wait_for_function(
        """
        (mode) => {
          const inspector = document.getElementById('workbench-evidence-inspector');
          const panel = document.querySelector(`[data-inspector-panel="${mode}"]`);
          return inspector
            && panel
            && inspector.getAttribute('data-inspector-open') === 'true'
            && inspector.getAttribute('data-inspector-mode-active') === mode
            && panel.getAttribute('aria-hidden') === 'false';
        }
        """,
        arg=mode,
    )


def _close_workbench_inspector(page: Any) -> None:
    page.evaluate(
        """
        () => {
          document.getElementById('workbench-evidence-inspector')
            ?.setAttribute('data-inspector-open', 'false');
          document.body.setAttribute('data-workbench-inspector-open', 'false');
        }
        """
    )


def _click_workbench_inspector_control(
    page: Any,
    mode: str,
    selector: str,
    *args: Any,
    close_after: bool = False,
    **kwargs: Any,
) -> Any:
    _open_workbench_inspector_mode(page, mode)
    result = page.click(selector, *args, **kwargs)
    if close_after:
        _close_workbench_inspector(page)
    return result


def _fill_workbench_inspector_control(
    page: Any,
    mode: str,
    selector: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    _open_workbench_inspector_mode(page, mode)
    return page.fill(selector, *args, **kwargs)


def _select_workbench_inspector_control(
    page: Any,
    mode: str,
    selector: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    _open_workbench_inspector_mode(page, mode)
    return page.select_option(selector, *args, **kwargs)


def _check_workbench_inspector_control(
    page: Any,
    mode: str,
    selector: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    _open_workbench_inspector_mode(page, mode)
    return page.check(selector, *args, **kwargs)


def _wait_for_workbench_inspector_control(
    page: Any,
    mode: str,
    selector: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    _open_workbench_inspector_mode(page, mode)
    return page.wait_for_selector(selector, *args, **kwargs)


def _click_with_workbench_inspector_closed(
    page: Any,
    selector: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    _close_workbench_inspector(page)
    return page.click(selector, *args, **kwargs)


def _fill_workbench_handoff_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _fill_workbench_inspector_control(page, "handoff", selector, *args, **kwargs)


def _click_workbench_handoff_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _click_workbench_inspector_control(
        page,
        "handoff",
        selector,
        *args,
        close_after=selector == "#workbench-export-draft-btn",
        **kwargs,
    )


def _wait_for_workbench_handoff_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _wait_for_workbench_inspector_control(page, "handoff", selector, *args, **kwargs)


def _select_workbench_handoff_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _select_workbench_inspector_control(page, "handoff", selector, *args, **kwargs)


def _check_workbench_handoff_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _check_workbench_inspector_control(page, "handoff", selector, *args, **kwargs)


def _fill_workbench_evidence_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _fill_workbench_inspector_control(page, "evidence", selector, *args, **kwargs)


def _click_workbench_evidence_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _click_workbench_inspector_control(page, "evidence", selector, *args, **kwargs)


def _select_workbench_evidence_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _select_workbench_inspector_control(page, "evidence", selector, *args, **kwargs)


def _wait_for_workbench_evidence_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _wait_for_workbench_inspector_control(page, "evidence", selector, *args, **kwargs)


def _check_workbench_evidence_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _check_workbench_inspector_control(page, "evidence", selector, *args, **kwargs)


def _fill_workbench_run_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _fill_workbench_inspector_control(page, "run", selector, *args, **kwargs)


def _click_workbench_run_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _click_workbench_inspector_control(page, "run", selector, *args, **kwargs)


def _select_workbench_run_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _select_workbench_inspector_control(page, "run", selector, *args, **kwargs)


def _check_workbench_run_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _check_workbench_inspector_control(page, "run", selector, *args, **kwargs)


def _wait_for_workbench_run_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _wait_for_workbench_inspector_control(page, "run", selector, *args, **kwargs)


def _fill_workbench_node_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _fill_workbench_inspector_control(page, "node", selector, *args, **kwargs)


def _click_workbench_node_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _click_workbench_inspector_control(page, "node", selector, *args, **kwargs)


def _select_workbench_node_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _select_workbench_inspector_control(page, "node", selector, *args, **kwargs)


def _check_workbench_node_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _check_workbench_inspector_control(page, "node", selector, *args, **kwargs)


def _wait_for_workbench_node_control(page: Any, selector: str, *args: Any, **kwargs: Any) -> Any:
    return _wait_for_workbench_inspector_control(page, "node", selector, *args, **kwargs)


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


def _set_draft_buffer_value(page: Any, draft_json: str) -> None:
    page.evaluate(
        """
        (draftJson) => {
          const buffer = document.getElementById('workbench-draft-json-buffer');
          buffer.value = draftJson;
          buffer.dispatchEvent(new Event('input', { bubbles: true }));
        }
        """,
        draft_json,
    )


def _set_archive_buffer_value(page: Any, archive_json: str) -> None:
    page.evaluate(
        """
        (archiveJson) => {
          const buffer = document.getElementById('workbench-evidence-archive-output');
          buffer.value = archiveJson;
          buffer.dispatchEvent(new Event('input', { bubbles: true }));
        }
        """,
        archive_json,
    )


def _click_workbench_port_handle(page: Any, owner_id: str, direction: str) -> None:
    selector = (
        f'[data-port-handle-owner-id="{owner_id}"]'
        f'[data-port-handle-direction="{direction}"]'
    )
    handle = page.locator(selector)
    handle.scroll_into_view_if_needed()
    handle.dispatch_event("click")


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


def test_workbench_canvas_first_default_and_explicit_reference_proof_load(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    first_load = page.evaluate(
        """
        () => {
          const required = [
            'ra_ft', 'sw1', 'not_inhibited', 'not_deployed', 'logic1',
            'tls_unlocked', 'sw2', 'engine_running', 'aircraft_on_ground',
            'eec_enable', 'logic2', 'n1k_limit', 'tra_deploy',
            'pls_unlocked', 'logic3', 'vdt90', 'logic4', 'thr_lock',
          ];
          const visibleReferenceNodes = required.filter((id) => {
            const node = document.querySelector(`[data-editable-node-id="${id}"]`);
            if (!node) return false;
            const rect = node.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          });
          const guide = document.querySelector('#workbench-canvas-first-guide');
          const guideRect = guide ? guide.getBoundingClientRect() : null;
          const edgePaths = Array.from(document.querySelectorAll('[data-editable-edge-id]'));
          const visibleProofButtons = Array.from(document.querySelectorAll('[data-reference-proof-target]'))
            .filter((button) => {
              const rect = button.getBoundingClientRect();
              return rect.width > 0 && rect.height > 0;
            })
            .map((button) => button.getAttribute('data-reference-proof-target'));
          return {
            title: document.querySelector('#workbench-circuit-hero-title')?.textContent.trim() || '',
            circuitTitle: document.querySelector('#workbench-reference-circuit-title')?.textContent.trim() || '',
            graph: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-graph') || '',
            mode: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-proof-mode') || '',
            canvasHeight: document.querySelector('#workbench-editable-canvas')?.getBoundingClientRect().height || 0,
            onboardingState: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') || '',
            onboardingPanelHidden: Boolean(document.querySelector('#workbench-goal-canvas-panel')?.hidden),
            reopenGuideVisible: (() => {
              const button = document.querySelector('#workbench-open-onboarding-guide-btn');
              if (!button || button.hidden) return false;
              const rect = button.getBoundingClientRect();
              return rect.width > 0 && rect.height > 0;
            })(),
            onboardingHighlightCount: document.querySelectorAll('[data-onboarding-highlight="true"]').length,
            canvasNoteCount: document.querySelectorAll('.workbench-editable-canvas-note').length,
            requiredCount: required.length,
            visibleReferenceNodes,
            edgeCount: edgePaths.length,
            visibleProofButtons,
            startText: document.querySelector('#workbench-canvas-first-start-btn')?.textContent.trim() || '',
            loadText: document.querySelector('#workbench-load-reference-proof-btn')?.textContent.trim() || '',
            guideText: guide?.textContent || '',
            guideHeight: guideRect ? guideRect.height : 0,
            guideStripCount: document.querySelectorAll('#workbench-reference-circuit-guide-strip li').length,
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert first_load["title"].startswith("控制逻辑画布工作台")
    assert first_load["circuitTitle"] == "C919 E-TRAS / 反推逻辑控制电路"
    assert first_load["graph"] == "c919-etras-thrust-reverser-proof"
    assert first_load["mode"] == "default_visible"
    assert first_load["canvasHeight"] >= 340
    assert first_load["onboardingState"] == "collapsed"
    assert first_load["onboardingPanelHidden"] is True
    assert first_load["reopenGuideVisible"] is True
    assert first_load["onboardingHighlightCount"] == 0
    assert first_load["canvasNoteCount"] == 0
    assert len(first_load["visibleReferenceNodes"]) == first_load["requiredCount"]
    assert first_load["edgeCount"] >= 18
    assert set(first_load["visibleProofButtons"]) == {"logic1", "logic3", "logic4", "thr_lock"}
    assert "新建空白电路" in first_load["startText"]
    assert "重置参考图" in first_load["loadText"]
    assert "看全图" in first_load["guideText"]
    assert "点节点" in first_load["guideText"]
    assert "运行" in first_load["guideText"]
    assert "空白" in first_load["guideText"]
    assert first_load["guideStripCount"] == 4
    assert 0 < first_load["guideHeight"] <= 92

    page.click("#workbench-load-reference-proof-btn")
    rendered = page.evaluate(
        """
        () => {
          const required = [
            'ra_ft', 'sw1', 'not_inhibited', 'not_deployed', 'logic1',
            'tls_unlocked', 'sw2', 'engine_running', 'aircraft_on_ground',
            'eec_enable', 'logic2', 'n1k_limit', 'tra_deploy',
            'pls_unlocked', 'logic3', 'vdt90', 'logic4', 'thr_lock',
          ];
          const nodes = required.map((id) => document.querySelector(`[data-editable-node-id="${id}"]`));
          const visibleNodes = nodes.filter((node) => {
            if (!node) return false;
            const rect = node.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          });
          const nodeTexts = Array.from(document.querySelectorAll('.workbench-editable-node'))
            .map((node) => node.textContent.trim());
          const edgePaths = Array.from(document.querySelectorAll('[data-editable-edge-id]'));
          const nodeSummaries = nodes.map((node) => ({
            id: node?.getAttribute('data-editable-node-id') || '',
            visible: node?.querySelector('span')?.textContent.trim() || '',
            short: node?.getAttribute('data-node-short-label') || '',
            full: node?.getAttribute('data-node-label') || '',
            title: node?.getAttribute('title') || '',
            aria: node?.getAttribute('aria-label') || '',
          }));
          const portHandles = Array.from(document.querySelectorAll('.workbench-port-handle'))
            .map((handle) => ({
              owner: handle.getAttribute('data-port-handle-owner-id') || '',
              direction: handle.getAttribute('data-port-handle-direction') || '',
              short: handle.getAttribute('data-port-short-label') || '',
              signalShort: handle.getAttribute('data-port-signal-short-label') || '',
              signal: handle.getAttribute('data-signal-id') || '',
              title: handle.getAttribute('title') || '',
              aria: handle.getAttribute('aria-label') || '',
            }));
          const edgeSummaries = edgePaths.map((path) => ({
            id: path.getAttribute('data-editable-edge-id') || '',
            full: path.getAttribute('data-edge-label') || '',
            display: path.getAttribute('data-edge-display-label') || '',
            routeMode: path.getAttribute('data-route-mode') || '',
            routeGuide: path.getAttribute('data-route-guide') || '',
            routeGuideEffect: path.getAttribute('data-route-guide-effect') || '',
            routeGuideTruthEffect: path.getAttribute('data-route-guide-truth-effect') || '',
            segmentCount: Number.parseInt(path.getAttribute('data-route-segment-count') || '0', 10) || 0,
            laneAxis: path.getAttribute('data-route-lane-axis') || '',
            laneX: path.getAttribute('data-route-lane-x') || '',
            laneY: path.getAttribute('data-route-lane-y') || '',
            routeDirection: path.getAttribute('data-route-direction') || '',
          }));
          const routeGuides = Array.from(document.querySelectorAll('.workbench-edge-route-guide'))
            .map((guide) => ({
              edgeId: guide.getAttribute('data-route-guide-edge-id') || '',
              editableEdgeId: guide.getAttribute('data-editable-edge-id') || '',
              routeGuide: guide.getAttribute('data-route-guide') || '',
              segmentCount: Number.parseInt(guide.getAttribute('data-route-segment-count') || '0', 10) || 0,
              truthEffect: guide.getAttribute('data-route-guide-truth-effect') || '',
              ariaHidden: guide.getAttribute('aria-hidden') || '',
              focusable: guide.getAttribute('focusable') || '',
              d: guide.getAttribute('d') || '',
            }));
          return {
            title: document.querySelector('#workbench-circuit-hero-title')?.textContent.trim() || '',
            graph: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-graph') || '',
            mode: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-proof-mode') || '',
            requiredCount: required.length,
            visibleCount: visibleNodes.length,
            nodeTexts,
            nodeSummaries,
            portHandles,
            edgeCount: edgePaths.length,
            edgePaths: edgePaths.map((path) => path.getAttribute('d') || ''),
            edgeSummaries,
            routeGuides,
            proofButtonCount: document.querySelectorAll('[data-reference-proof-target]').length,
          };
        }
        """
    )

    assert rendered["title"].startswith("控制逻辑画布工作台")
    assert rendered["graph"] == "c919-etras-thrust-reverser-proof"
    assert rendered["mode"] == "default_visible"
    assert rendered["visibleCount"] == rendered["requiredCount"]
    assert rendered["edgeCount"] >= 18
    assert rendered["proofButtonCount"] == 4
    op_only_labels = {"IN", "OUT", "AND", "OR", "CMP", "BTW", "DLY", "LAT", "LCH"}
    assert all(text not in op_only_labels for text in rendered["nodeTexts"])
    assert all(item["visible"] and item["visible"] == item["short"] for item in rendered["nodeSummaries"])
    assert all(len(item["visible"]) <= 7 for item in rendered["nodeSummaries"])
    assert any(item["visible"] == "高度<6ft" for item in rendered["nodeSummaries"])
    assert any(item["visible"] == "THR锁" for item in rendered["nodeSummaries"])
    assert any("无线电高度低于 6 英尺" in item["full"] for item in rendered["nodeSummaries"])
    assert any("油门锁释放指令" in item["full"] for item in rendered["nodeSummaries"])
    assert all(item["full"] and item["full"] in item["title"] for item in rendered["nodeSummaries"])
    assert all(item["full"] and item["full"] in item["aria"] for item in rendered["nodeSummaries"])
    assert len(rendered["portHandles"]) >= rendered["requiredCount"] * 2
    assert all(item["short"].startswith(("IN:", "OUT:")) for item in rendered["portHandles"])
    assert any(item["short"] == "OUT:RA<6" for item in rendered["portHandles"])
    assert any(item["short"] == "IN:TRA" for item in rendered["portHandles"])
    assert all(item["signalShort"] for item in rendered["portHandles"])
    assert all("信号" in item["aria"] and "端口" in item["title"] for item in rendered["portHandles"])
    assert all(item["display"] for item in rendered["edgeSummaries"])
    assert all(len(item["display"]) <= 10 for item in rendered["edgeSummaries"])
    assert all(item["full"] for item in rendered["edgeSummaries"])
    assert all(item["routeMode"] == "orthogonal" for item in rendered["edgeSummaries"])
    assert len(rendered["routeGuides"]) == rendered["edgeCount"]
    assert all(not item["editableEdgeId"] for item in rendered["routeGuides"])
    assert all(item["routeGuide"] == "orthogonal_lane_guide" for item in rendered["edgeSummaries"])
    assert all(item["routeGuideEffect"] == "display_only" for item in rendered["edgeSummaries"])
    assert all(item["routeGuideTruthEffect"] == "none" for item in rendered["edgeSummaries"])
    assert all(item["segmentCount"] >= 3 for item in rendered["edgeSummaries"])
    assert all(item["laneAxis"] in {"x", "y", "mixed"} for item in rendered["edgeSummaries"])
    assert all(item["routeDirection"] in {"forward", "reverse"} for item in rendered["edgeSummaries"])
    assert all(item["routeGuide"] == "orthogonal_lane_guide" for item in rendered["routeGuides"])
    assert all(item["truthEffect"] == "none" for item in rendered["routeGuides"])
    assert all(item["ariaHidden"] == "true" and item["focusable"] == "false" for item in rendered["routeGuides"])
    assert all("C" not in item["d"] and "L" in item["d"] for item in rendered["routeGuides"])
    assert all("C" not in path for path in rendered["edgePaths"])
    assert all("L" in path for path in rendered["edgePaths"])

    page.click('[data-reference-proof-target="logic4"]')
    highlighted = page.evaluate(
        """
        () => ({
          buttonPressed: document.querySelector('[data-reference-proof-target="logic4"]')
            ?.getAttribute('aria-pressed'),
          highlightedNodes: Array.from(document.querySelectorAll('[data-proof-highlight="true"]'))
            .map((node) => node.getAttribute('data-editable-node-id'))
            .filter(Boolean),
          highlightedEdges: Array.from(document.querySelectorAll('[data-edge-proof-highlight="true"]'))
            .map((edge) => edge.getAttribute('data-editable-edge-id'))
            .filter(Boolean),
          inspectorTarget: document.querySelector('#workbench-inspector-node-id')?.textContent.trim(),
          ruleSummary: document.querySelector('#workbench-inspector-rule-summary')?.textContent.trim() || '',
          detail: document.querySelector('#workbench-inspector-evidence-detail')?.textContent || '',
          status: document.querySelector('#workbench-graph-validation-status')?.textContent || '',
        })
        """
    )
    assert highlighted["buttonPressed"] == "true"
    assert {"logic1", "logic2", "logic3", "logic4", "vdt90"}.issubset(set(highlighted["highlightedNodes"]))
    assert len(highlighted["highlightedEdges"]) >= 4
    assert highlighted["inspectorTarget"] == "logic4"
    assert "VDT 达到 90% 展开" in highlighted["ruleSummary"]
    assert "90% 展开" in highlighted["detail"]
    assert "proof path logic4" in highlighted["status"]

    page.click("#workbench-start-empty-draft-btn")
    empty_canvas_state = page.evaluate(
        """
        () => ({
          mode: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-proof-mode') || '',
          highlightedNodes: document.querySelectorAll('[data-proof-highlight="true"]').length,
          highlightedEdges: document.querySelectorAll('[data-edge-proof-highlight="true"]').length,
          pressedProofButtons: document.querySelectorAll('[data-reference-proof-target][aria-pressed="true"]').length,
          authoringMode: (() => {
            const buffer = document.querySelector('#workbench-draft-json-buffer');
            try {
              return JSON.parse(buffer?.value || '{}').canvas_authoring_mode || '';
            } catch (error) {
              return '';
            }
          })(),
        })
        """
    )
    assert empty_canvas_state["mode"] == "empty_authoring"
    assert empty_canvas_state["highlightedNodes"] == 0
    assert empty_canvas_state["highlightedEdges"] == 0
    assert empty_canvas_state["pressedProofButtons"] == 0
    assert empty_canvas_state["authoringMode"] == "empty_authoring"


def test_workbench_system_toggle_updates_adapter_backed_runtime_proof_rail(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    initial = page.evaluate(
        """
        () => {
          const rail = document.getElementById('workbench-runtime-generalization-proof');
          return {
            system: rail?.getAttribute('data-runtime-proof-system') || '',
            adapter: document.getElementById('workbench-runtime-proof-adapter-id')?.textContent.trim() || '',
            source: document.getElementById('workbench-runtime-proof-source')?.textContent.trim() || '',
            contracts: document.getElementById('workbench-runtime-proof-contracts')?.textContent.trim() || '',
            boundary: document.getElementById('workbench-runtime-proof-boundary')?.textContent.trim() || '',
            uiOnlyTruthPath: rail?.getAttribute('data-ui-only-truth-path') || '',
            truthEffect: rail?.getAttribute('data-truth-effect') || '',
            controllerTruthModified: rail?.getAttribute('data-controller-truth-modified') || '',
          };
        }
        """
    )

    assert initial["system"] == "thrust-reverser"
    assert initial["adapter"] == "reference-deploy-controller"
    assert initial["source"] == "src/well_harness/controller.py"
    assert "playback_report" in initial["contracts"]
    assert "knowledge_artifact" in initial["contracts"]
    assert "truth_effect: none" in initial["boundary"]
    assert initial["uiOnlyTruthPath"] == "false"
    assert initial["truthEffect"] == "none"
    assert initial["controllerTruthModified"] == "false"

    page.click('[data-circuit-system="c919-etras"]')
    page.wait_for_function(
        """
        () => {
          const rail = document.getElementById('workbench-runtime-generalization-proof');
          return rail?.getAttribute('data-runtime-proof-system') === 'c919-etras'
            && document.getElementById('workbench-runtime-proof-adapter-id')?.textContent.trim()
              === 'c919-etras-controller-adapter';
        }
        """
    )
    c919 = page.evaluate(
        """
        () => {
          const rail = document.getElementById('workbench-runtime-generalization-proof');
          return {
            system: rail?.getAttribute('data-runtime-proof-system') || '',
            label: document.getElementById('workbench-runtime-proof-system-label')?.textContent.trim() || '',
            adapter: document.getElementById('workbench-runtime-proof-adapter-id')?.textContent.trim() || '',
            source: document.getElementById('workbench-runtime-proof-source')?.textContent.trim() || '',
            contracts: document.getElementById('workbench-runtime-proof-contracts')?.textContent.trim() || '',
            boundary: document.getElementById('workbench-runtime-proof-boundary')?.textContent.trim() || '',
            uiOnlyTruthPath: rail?.getAttribute('data-ui-only-truth-path') || '',
            truthEffect: rail?.getAttribute('data-truth-effect') || '',
            controllerTruthModified: rail?.getAttribute('data-controller-truth-modified') || '',
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert c919["system"] == "c919-etras"
    assert "C919 E-TRAS" in c919["label"]
    assert c919["adapter"] == "c919-etras-controller-adapter"
    assert c919["source"] == "src/well_harness/adapters/c919_etras_adapter.py"
    assert "controller_truth_metadata" in c919["contracts"]
    assert "fault_diagnosis_report" in c919["contracts"]
    assert "UI-only truth path: false" in c919["boundary"]
    assert c919["uiOnlyTruthPath"] == "false"
    assert c919["truthEffect"] == "none"
    assert c919["controllerTruthModified"] == "false"


def test_workbench_new_engineer_onboarding_guide_highlights_full_flow(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    collapsed = page.evaluate(
        """
        () => ({
          panelHidden: Boolean(document.querySelector('#workbench-goal-canvas-panel')?.hidden),
          state: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') || '',
          reopenVisible: (() => {
            const button = document.querySelector('#workbench-open-onboarding-guide-btn');
            if (!button || button.hidden) return false;
            const rect = button.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          })(),
          highlightedCount: document.querySelectorAll('[data-onboarding-highlight="true"]').length,
        })
        """
    )
    assert collapsed == {
        "panelHidden": True,
        "state": "collapsed",
        "reopenVisible": True,
        "highlightedCount": 0,
    }

    page.click("#workbench-open-onboarding-guide-btn")
    page.wait_for_function(
        "() => !document.querySelector('#workbench-goal-canvas-panel')?.hidden"
    )

    initial = page.evaluate(
        """
        () => {
          const statusChip = document.querySelector('.workbench-editable-status-chip');
          const bg = statusChip ? getComputedStyle(statusChip).backgroundColor : '';
          const rgb = (bg.match(/\\d+(?:\\.\\d+)?/g) || []).slice(0, 3).map(Number);
          const brightness = rgb.length === 3 ? Math.round((rgb[0] + rgb[1] + rgb[2]) / 3) : 0;
          return {
            skin: document.querySelector('#workbench-editable-shell')?.getAttribute('data-workbench-skin') || '',
            density: document.querySelector('#workbench-editable-status-bar')?.getAttribute('data-status-density') || '',
            brightness,
            panelHidden: Boolean(document.querySelector('#workbench-goal-canvas-panel')?.hidden),
            panelState: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') || '',
            reopenHidden: Boolean(document.querySelector('#workbench-open-onboarding-guide-btn')?.hidden),
            activeStep: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-active-step') || '',
            progress: document.querySelector('#workbench-onboarding-progress')?.textContent.trim() || '',
            actionText: document.querySelector('#workbench-onboarding-action-btn')?.textContent.trim() || '',
            steps: Array.from(document.querySelectorAll('[data-onboarding-step]'))
              .map((step) => step.getAttribute('data-onboarding-step')),
            highlightedIds: Array.from(document.querySelectorAll('[data-onboarding-highlight="true"]'))
              .map((node) => node.id || node.getAttribute('data-editable-node-id') || node.getAttribute('data-reference-proof-target') || node.getAttribute('data-editor-tool') || ''),
          };
        }
        """
    )
    assert errors == [], f"page JS errors: {errors}"
    assert initial["skin"] == "cockpit-editor"
    assert initial["density"] == "compact"
    assert initial["brightness"] < 70
    assert initial["panelHidden"] is False
    assert initial["panelState"] == "expanded"
    assert initial["reopenHidden"] is True
    assert initial["activeStep"] == "overview"
    assert initial["progress"] == "1 / 7"
    assert initial["actionText"] == "高亮全图"
    assert initial["steps"] == [
        "overview",
        "inspect_node",
        "proof_path",
        "blank_canvas",
        "add_node",
        "wire",
        "run_sandbox",
    ]
    assert "workbench-editable-canvas" in initial["highlightedIds"]

    page.click("#workbench-close-onboarding-guide-btn")
    closed = page.evaluate(
        """
        () => ({
          panelHidden: Boolean(document.querySelector('#workbench-goal-canvas-panel')?.hidden),
          state: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') || '',
          reopenHidden: Boolean(document.querySelector('#workbench-open-onboarding-guide-btn')?.hidden),
          highlightedCount: document.querySelectorAll('[data-onboarding-highlight="true"]').length,
        })
        """
    )
    assert closed == {
        "panelHidden": True,
        "state": "collapsed",
        "reopenHidden": False,
        "highlightedCount": 0,
    }
    page.click("#workbench-open-onboarding-guide-btn")
    page.wait_for_function(
        "() => document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') === 'expanded'"
    )

    page.click("#workbench-onboarding-next-btn")
    inspect_step = page.evaluate(
        """
        () => ({
          activeStep: document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-active-step') || '',
          progress: document.querySelector('#workbench-onboarding-progress')?.textContent.trim() || '',
          highlightedIds: Array.from(document.querySelectorAll('[data-onboarding-highlight="true"]'))
            .map((node) => node.id || node.getAttribute('data-editable-node-id') || ''),
        })
        """
    )
    assert inspect_step["activeStep"] == "inspect_node"
    assert inspect_step["progress"] == "2 / 7"
    assert "logic1" in inspect_step["highlightedIds"]

    page.click("#workbench-onboarding-action-btn")
    assert page.locator("#workbench-inspector-node-id").inner_text() == "logic1"

    page.click("#workbench-onboarding-next-btn")
    assert page.locator("#workbench-goal-canvas-panel").get_attribute("data-onboarding-active-step") == "proof_path"
    page.click("#workbench-onboarding-action-btn")
    assert page.locator('[data-reference-proof-target="logic4"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#workbench-inspector-node-id").inner_text() == "logic4"
    assert "VDT 达到 90% 展开" in page.locator("#workbench-inspector-rule-summary").inner_text()

    page.click("#workbench-onboarding-next-btn")
    assert page.locator("#workbench-goal-canvas-panel").get_attribute("data-onboarding-active-step") == "blank_canvas"
    page.click("#workbench-onboarding-action-btn")
    page.wait_for_function(
        "() => document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-proof-mode') === 'empty_authoring'",
    )
    assert page.locator('[data-editable-node-id="logic1"]').count() == 0

    page.click("#workbench-onboarding-next-btn")
    assert page.locator("#workbench-goal-canvas-panel").get_attribute("data-onboarding-active-step") == "add_node"
    page.click("#workbench-onboarding-action-btn")
    page.wait_for_function("() => document.querySelectorAll('.workbench-editable-node').length === 1")

    page.click("#workbench-onboarding-next-btn")
    assert page.locator("#workbench-goal-canvas-panel").get_attribute("data-onboarding-active-step") == "wire"
    page.click("#workbench-onboarding-action-btn")
    assert page.locator('[data-editor-tool="edge"]').get_attribute("aria-pressed") == "true"
    assert "edge" in page.locator("#workbench-graph-validation-status").inner_text().lower()

    page.click("#workbench-onboarding-next-btn")
    assert page.locator("#workbench-goal-canvas-panel").get_attribute("data-onboarding-active-step") == "run_sandbox"
    page.click("#workbench-onboarding-action-btn")
    assert page.locator("#workbench-evidence-inspector").get_attribute("data-inspector-mode-active") == "run"
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-diff-verdict')?.textContent.trim();
          return ['equivalent', 'divergent', 'invalid_model', 'invalid_scenario'].includes(verdict);
        }
        """
    )


def test_workbench_reference_visual_edges_and_outsider_tutorial_are_readable(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    visual = page.evaluate(
        """
        () => {
          const edgePaths = Array.from(document.querySelectorAll('[data-editable-edge-id]'));
          const nodes = Array.from(document.querySelectorAll('[data-reference-proof-node]'));
          const nodeRects = nodes.map((node) => ({
            id: node.getAttribute('data-editable-node-id') || '',
            rect: node.getBoundingClientRect(),
          }));
          const overlapSamples = [];
          for (const path of edgePaths) {
            if (typeof path.getTotalLength !== 'function' || typeof path.getPointAtLength !== 'function') {
              continue;
            }
            const matrix = path.getScreenCTM();
            if (!matrix) continue;
            const sourceId = path.getAttribute('data-edge-source-id') || '';
            const targetId = path.getAttribute('data-edge-target-id') || '';
            const length = path.getTotalLength();
            for (const ratio of [0.2, 0.35, 0.5, 0.65, 0.8]) {
              const point = path.getPointAtLength(length * ratio);
              const screenPoint = new DOMPoint(point.x, point.y).matrixTransform(matrix);
              for (const item of nodeRects) {
                if (!item.id || item.id === sourceId || item.id === targetId) continue;
                const rect = item.rect;
                const inset = 3;
                if (
                  screenPoint.x > rect.left + inset
                  && screenPoint.x < rect.right - inset
                  && screenPoint.y > rect.top + inset
                  && screenPoint.y < rect.bottom - inset
                ) {
                  overlapSamples.push({
                    edge: path.getAttribute('data-editable-edge-id') || '',
                    node: item.id,
                    x: Math.round(screenPoint.x),
                    y: Math.round(screenPoint.y),
                  });
                }
              }
            }
          }
          const styles = edgePaths.map((path) => {
            const style = getComputedStyle(path);
            return {
              edge: path.getAttribute('data-editable-edge-id') || '',
              source: path.getAttribute('data-edge-source-id') || '',
              target: path.getAttribute('data-edge-target-id') || '',
              strokeWidth: Number.parseFloat(style.strokeWidth || '0') || 0,
              dash: style.strokeDasharray,
            };
          });
          const explainerText = document.querySelector('#workbench-outsider-circuit-explainer')?.textContent || '';
          const guideDetail = document.querySelector('#workbench-onboarding-detail')?.textContent || '';
          return {
            mode: document.querySelector('#workbench-editable-canvas')?.getAttribute('data-reference-proof-mode') || '',
            edgeCount: edgePaths.length,
            minStrokeWidth: Math.min(...styles.map((item) => item.strokeWidth)),
            dashedEdges: styles.filter((item) => !['none', '0px'].includes(item.dash)).map((item) => `${item.edge}:${item.dash}`),
            missingEndpoints: styles.filter((item) => !item.source || !item.target).map((item) => item.edge),
            overlapSamples,
            explainerText,
            guideDetail,
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert visual["mode"] == "default_visible"
    assert visual["edgeCount"] >= 18
    assert visual["minStrokeWidth"] >= 3
    assert visual["dashedEdges"] == []
    assert visual["missingEndpoints"] == []
    assert visual["overlapSamples"] == []
    for copy in (
        "这个逻辑电路究竟在实现什么功能",
        "为什么这么画",
        "输入信号开始每一步会发生什么",
        "预期会如何触发",
        "如果遇到故障会发生什么",
        "仿真按钮按下之后会看到什么",
        "仿真有什么价值",
        "THR_LOCK",
    ):
        assert copy in visual["explainerText"]
    assert "这个电路的功能" in visual["guideDetail"]


def test_workbench_cockpit_editor_skin_keeps_canvas_primary_and_export_raw_fields(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1440, "height": 980})
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
          window.localStorage.removeItem('well-harness-workbench-onboarding-guide-open-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    desktop = page.evaluate(
        """
        () => {
          const rectFor = (selector) => {
            const element = document.querySelector(selector);
            if (!element) return { width: 0, height: 0, left: 0, right: 0, top: 0, bottom: 0 };
            const rect = element.getBoundingClientRect();
            return {
              width: rect.width,
              height: rect.height,
              left: rect.left,
              right: rect.right,
              top: rect.top,
              bottom: rect.bottom,
            };
          };
          const shell = document.querySelector('#workbench-editable-shell');
          const canvas = document.querySelector('#workbench-editable-canvas');
          const scenarioSelect = document.querySelector('#workbench-sandbox-scenario-select');
          const selectedOptionText = scenarioSelect
            ? scenarioSelect.options[scenarioSelect.selectedIndex]?.textContent.trim() || ''
            : '';
          const shellRect = rectFor('#workbench-editable-shell');
          const canvasRect = rectFor('#workbench-editable-canvas');
          const statusRect = rectFor('#workbench-editable-status-bar');
          const toolbarRect = rectFor('#workbench-editor-toolbar');
          const inspectorRect = rectFor('#workbench-evidence-inspector');
          const coachRect = rectFor('#workbench-cockpit-guide-coach');
          return {
            skin: shell?.getAttribute('data-workbench-skin') || '',
            hudRole: document.querySelector('#workbench-editable-status-bar')?.getAttribute('data-hud-role') || '',
            hudPrimary: document.querySelector('#workbench-editable-status-bar')?.getAttribute('data-hud-primary') || '',
            shellRect,
            canvasRect,
            canvasAreaRatio: shellRect.width && shellRect.height
              ? (canvasRect.width * canvasRect.height) / (shellRect.width * shellRect.height)
              : 0,
            statusHeight: statusRect.height,
            toolbarWidth: toolbarRect.width,
            inspectorOpen: document.querySelector('#workbench-evidence-inspector')?.getAttribute('data-inspector-open') || '',
            inspectorWidth: inspectorRect.width,
            coachVisible: Boolean(document.querySelector('#workbench-cockpit-guide-coach')) && coachRect.width > 0 && coachRect.height > 0,
            coachText: document.querySelector('#workbench-cockpit-guide-coach')?.textContent || '',
            revision: document.querySelector('#workbench-workspace-document-revision')?.textContent.trim() || '',
            lastAction: document.querySelector('#workbench-canvas-last-action')?.textContent.trim() || '',
            scenarioText: selectedOptionText,
            scenarioValue: scenarioSelect?.value || '',
            debugScenario: document.querySelector('#workbench-selected-debug-scenario')?.textContent.trim() || '',
            debugVerdict: document.querySelector('#workbench-selected-debug-verdict')?.textContent.trim() || '',
            debugLink: document.querySelector('#workbench-selected-debug-link-status')?.textContent.trim() || '',
            debugHardware: document.querySelector('#workbench-selected-debug-hardware')?.textContent.trim() || '',
            nodeCount: document.querySelectorAll('[data-reference-proof-node]').length,
            edgeCount: document.querySelectorAll('[data-editable-edge-id]').length,
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert desktop["skin"] == "cockpit-editor"
    assert desktop["hudRole"] == "cockpit-status"
    assert desktop["hudPrimary"] == "canvas"
    assert desktop["canvasAreaRatio"] >= 0.72
    assert desktop["statusHeight"] <= 48
    assert desktop["toolbarWidth"] <= 54
    assert desktop["inspectorOpen"] == "false"
    assert desktop["inspectorWidth"] <= 4
    assert desktop["coachVisible"] is True
    assert "新手" in desktop["coachText"]
    assert "C919 E-TRAS" in desktop["coachText"]
    assert desktop["revision"] == "本地草稿"
    assert desktop["lastAction"] == "初始化"
    assert desktop["scenarioText"] == "名义着陆"
    assert desktop["scenarioValue"] == "nominal_landing"
    assert desktop["debugScenario"] == "名义着陆"
    assert desktop["debugVerdict"] == "未运行"
    assert desktop["debugLink"] == "仅选择"
    assert "证据缺口" in desktop["debugHardware"]
    assert desktop["nodeCount"] >= 18
    assert desktop["edgeCount"] >= 18

    page.click("#workbench-open-command-palette-btn")
    page.click('[data-command-palette-command="export_draft"]')
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["selected_scenario_id"] == "nominal_landing"
    assert any(
        node.get("id") == "logic1"
        and node.get("hardware_binding", {}).get("evidence_status") == "evidence_gap"
        for node in draft.get("nodes", [])
    )

    page.click("#workbench-open-onboarding-guide-btn")
    page.wait_for_function(
        "() => document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') === 'expanded'"
    )
    assert page.locator("#workbench-cockpit-guide-coach").is_visible()
    page.click("#workbench-close-onboarding-guide-btn")
    page.wait_for_function(
        "() => document.querySelector('#workbench-goal-canvas-panel')?.getAttribute('data-onboarding-state') === 'collapsed'"
    )
    assert page.locator("#workbench-open-onboarding-guide-btn").is_visible()

    page.set_viewport_size({"width": 390, "height": 920})
    page.wait_for_timeout(200)
    mobile = page.evaluate(
        """
        () => {
          const shell = document.querySelector('#workbench-editable-shell')?.getBoundingClientRect();
          const canvas = document.querySelector('#workbench-editable-canvas')?.getBoundingClientRect();
          const toolbar = document.querySelector('#workbench-editor-toolbar')?.getBoundingClientRect();
          const inspector = document.querySelector('#workbench-evidence-inspector')?.getBoundingClientRect();
          return {
            canvasAreaRatio: shell && canvas ? (canvas.width * canvas.height) / (shell.width * shell.height) : 0,
            toolbarWidth: toolbar ? toolbar.width : 0,
            inspectorWidth: inspector ? inspector.width : 0,
            coachVisible: (() => {
              const coach = document.querySelector('#workbench-cockpit-guide-coach');
              if (!coach || coach.hidden) return false;
              const rect = coach.getBoundingClientRect();
              return rect.width > 0 && rect.height > 0;
            })(),
          };
        }
        """
    )
    assert mobile["canvasAreaRatio"] >= 0.66
    assert mobile["toolbarWidth"] <= 52
    assert mobile["inspectorWidth"] <= 4
    assert mobile["coachVisible"] is True


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

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
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
    assert archive["gate_claims"]["hard_hold_policy"] == "required"
    assert archive["gate_claims"]["default_pytest"] == "warning"
    assert archive["gate_claims"]["mypy_strict_clean"] == "not_claimed"
    assert archive["gate_claims"]["e2e_49_49"] == "not_claimed"
    assert "workbench Tier 0 hard holds" in blocker_gates
    assert "PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json" in blocker_gates
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"
    assert archive["red_line_metadata"]["dal_pssa_impact"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False
    assert archive["red_line_metadata"]["live_linear_mutation"] is False
    assert archive["checksums"]["gate_claims_checksum"]
    assert archive["checksums"]["known_blockers_checksum"]


def test_workbench_release_maturity_rail_renders_local_operations_gates(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.wait_for_selector("#workbench-release-maturity-rail")
    rail = page.locator("#workbench-release-maturity-rail")

    assert errors == [], f"page JS errors: {errors}"
    assert rail.get_attribute("data-release-maturity-scope") == "local_only"
    assert rail.get_attribute("data-release-maturity-truth-effect") == "none"
    assert rail.get_attribute("data-release-maturity-controller-truth-modified") == "false"
    assert rail.get_attribute("data-release-maturity-certification-claim") == "none"
    assert page.locator('[data-release-gate-id="local_smoke"]').get_attribute("data-release-gate-status") == "rerun_required"
    assert page.locator('[data-release-gate-id="targeted_e2e"]').get_attribute("data-release-gate-status") == "warning"
    assert page.locator('[data-release-gate-id="full_gsd"]').get_attribute("data-release-gate-status") == "warning"
    assert page.locator('[data-release-gate-id="mypy_strict_clean"]').get_attribute("data-release-gate-status") == "not_claimed"
    assert page.locator('[data-release-gate-id="controller_truth"]').get_attribute("data-release-gate-status") == "pass"
    assert "仅本地证据" in rail.inner_text()
    assert "controller truth unchanged" in rail.inner_text()


def test_workbench_release_readiness_packet_exports_local_only_gate_evidence(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _click_workbench_handoff_control(page, "#workbench-generate-release-readiness-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-release-readiness-output');
          return output && output.value.includes('well-harness-workbench-release-readiness-packet');
        }
        """
    )
    packet = json.loads(page.locator("#workbench-release-readiness-output").input_value())

    assert errors == [], f"page JS errors: {errors}"
    assert packet["kind"] == "well-harness-workbench-release-readiness-packet"
    assert packet["version"] == "workbench-release-readiness.v1"
    assert packet["scope"] == "local_only"
    assert packet["release_maturity_snapshot"]["truth_effect"] == "none"
    assert packet["gate_status_counts"]["not_claimed"] >= 1
    assert packet["gate_status_counts"]["blocked"] >= 1
    assert packet["controller_truth_modified"] is False
    assert packet["certification_claim"] == "none"
    assert packet["truth_effect"] == "none"
    assert "PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json" in packet["local_operator_commands"]
    assert "full strict mypy clean" in " ".join(packet["not_claimed_gates"])
    assert packet["checksums"]["release_maturity_snapshot_checksum"]


def test_workbench_interface_binding_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-001")
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "partial"
    assert (
        page.locator('[data-editable-node-id="logic1"]').get_attribute("data-binding-quality")
        == "partial"
    )

    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-TR-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J1")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-001:J1")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "complete"
    assert (
        page.locator('[data-editable-node-id="logic1"]').get_attribute("data-binding-quality")
        == "complete"
    )
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
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
    assert first_binding["binding_quality"] == "complete"
    assert draft["binding_coverage"]["complete"] == 1
    assert draft["binding_coverage"]["truth_effect"] == "none"
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-001"

    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_binding = round_trip["hardware_bindings"][0]
    assert round_trip_binding["hardware_id"] == "TR-LRU-001"
    assert round_trip_binding["cable"] == "CBL-TR-A"
    assert round_trip_binding["connector"] == "J1"
    assert round_trip_binding["port_local"] == "logic1:out"
    assert round_trip_binding["port_peer"] == "TR-LRU-001:J1"
    assert round_trip["binding_coverage"]["complete"] == 1

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["hardware_bindings"][0]["hardware_id"] == "TR-LRU-001"
    assert archive["hardware_bindings"][0]["truth_effect"] == "none"
    assert archive["binding_coverage"]["complete"] == 1
    assert archive["binding_coverage"]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_bindings_checksum"]
    assert archive["checksums"]["binding_coverage_checksum"]


def test_workbench_connector_pin_map_applies_round_trips_and_archives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-PIN")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-TR-PIN")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-PIN")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-PIN:J-PIN")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_evidence_control(page, "#workbench-export-connector-pin-map-btn")
    pin_map = json.loads(page.locator("#workbench-connector-pin-map-output").input_value())
    assert pin_map["kind"] == "well-harness-workbench-connector-pin-map"
    assert pin_map["truth_effect"] == "none"
    row = pin_map["rows"][0]
    assert row["owner_kind"] == "node"
    assert row["owner_id"] == "logic1"
    assert row["pin_local"] == "evidence_gap"
    assert row["pin_peer"] == "evidence_gap"
    row["pin_local"] = "A1"
    row["pin_peer"] = "B7"
    row["source_ref"] = "ui_draft.connector_pin_map.test"
    _fill_workbench_evidence_control(page, "#workbench-connector-pin-map-output", json.dumps(pin_map))
    _click_workbench_evidence_control(page, "#workbench-apply-connector-pin-map-btn")
    assert "Applied 1 connector/pin row" in page.locator("#workbench-connector-pin-map-status").inner_text()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["connector_pin_map"]["rows"][0]["pin_local"] == "A1"
    assert draft["connector_pin_map"]["rows"][0]["pin_peer"] == "B7"
    assert draft["hardware_bindings"][0]["pin_local"] == "A1"
    assert draft["hardware_bindings"][0]["pin_peer"] == "B7"
    logic1 = next(node for node in draft["nodes"] if node["id"] == "logic1")
    assert logic1["hardware_binding"]["pin_local"] == "A1"
    assert logic1["hardware_binding"]["pin_peer"] == "B7"

    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_evidence_control(page, "#workbench-export-connector-pin-map-btn")
    imported_map = json.loads(page.locator("#workbench-connector-pin-map-output").input_value())
    assert imported_map["rows"][0]["pin_local"] == "A1"
    assert imported_map["rows"][0]["pin_peer"] == "B7"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["connector_pin_map"]["rows"][0]["pin_local"] == "A1"
    assert archive["connector_pin_map"]["truth_effect"] == "none"
    assert archive["checksums"]["connector_pin_map_checksum"]


def test_workbench_hardware_interface_designer_validates_round_trips_and_archives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    invalid_payload = {
        "$schema": "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json",
        "kind": "well-harness-editable-hardware-interface-design",
        "version": 1,
        "design_id": "ui-hw-design-invalid",
        "system_id": "sandbox",
        "candidate_state": "sandbox_candidate",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "runtime_truth_effect": "none",
        "lrus": [
            {
                "id": "LRU-DUP",
                "display_name": "LRU Duplicate A",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
            {
                "id": "LRU-DUP",
                "display_name": "LRU Duplicate B",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
        ],
        "cables": [],
        "connectors": [],
        "ports": [],
        "pins": [],
        "bindings": [],
        "evidence_gaps": [],
        "evidence_metadata": {
            "sample_pack_role": "hardware_interface_design",
            "source_refs": ["ui_draft.hardware_interface_designer.e2e"],
        },
        "boundaries": {
            "runtime_scope": "sandbox_only",
            "hardware_truth_effect": "none",
            "certified_truth_modified": False,
            "dal_pssa_impact": "none",
        },
    }
    _fill_workbench_evidence_control(page, "#workbench-hardware-interface-design-output", json.dumps(invalid_payload))
    _click_workbench_evidence_control(page, "#workbench-validate-hardware-interface-design-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-hardware-interface-design-validation-output')
          ?.value.includes('duplicate_hardware_interface_id')
        """
    )
    invalid_report = json.loads(
        page.locator("#workbench-hardware-interface-design-validation-output").input_value()
    )
    assert invalid_report["status"] == "fail"
    assert any(finding["code"] == "duplicate_hardware_interface_id" for finding in invalid_report["findings"])

    valid_payload = {
        "$schema": "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json",
        "kind": "well-harness-editable-hardware-interface-design",
        "version": 1,
        "design_id": "ui-hw-design-e2e",
        "system_id": "thrust-reverser",
        "candidate_state": "sandbox_candidate",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "runtime_truth_effect": "none",
        "lrus": [
            {
                "id": "LRU-A",
                "display_name": "LRU A",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
            {
                "id": "LRU-B",
                "display_name": "LRU B",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
        ],
        "cables": [
            {
                "id": "CABLE-A-B",
                "display_name": "Cable A B",
                "source_lru_id": "LRU-A",
                "target_lru_id": "LRU-B",
                "cable_type": "harness",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            }
        ],
        "connectors": [
            {
                "id": "CONN-A",
                "display_name": "Connector A",
                "lru_id": "LRU-A",
                "connector_type": "MIL-DTL-38999",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
            {
                "id": "CONN-B",
                "display_name": "Connector B",
                "lru_id": "LRU-B",
                "connector_type": "MIL-DTL-38999",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
        ],
        "ports": [
            {
                "id": "PORT-A-1",
                "display_name": "A out",
                "connector_id": "CONN-A",
                "direction": "output",
                "signal_id": "sig_a_b",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
            {
                "id": "PORT-B-1",
                "display_name": "B in",
                "connector_id": "CONN-B",
                "direction": "input",
                "signal_id": "sig_a_b",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
        ],
        "pins": [
            {
                "id": "PIN-A-1",
                "connector_id": "CONN-A",
                "pin_number": "A1",
                "port_id": "PORT-A-1",
                "signal_id": "sig_a_b",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
            {
                "id": "PIN-B-1",
                "connector_id": "CONN-B",
                "pin_number": "B1",
                "port_id": "PORT-B-1",
                "signal_id": "sig_a_b",
                "evidence_status": "ui_draft",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            },
        ],
        "bindings": [
            {
                "id": "BIND-A-B",
                "signal_id": "sig_a_b",
                "source_port_id": "PORT-A-1",
                "target_port_id": "PORT-B-1",
                "cable_id": "CABLE-A-B",
                "redundancy_status": "single",
                "evidence_status": "ui_draft",
                "truth_effect": "none",
                "source_ref": "ui_draft.hardware_interface_designer.e2e",
            }
        ],
        "evidence_gaps": [],
        "evidence_metadata": {
            "sample_pack_role": "hardware_interface_design",
            "source_refs": ["ui_draft.hardware_interface_designer.e2e"],
        },
        "boundaries": {
            "runtime_scope": "sandbox_only",
            "hardware_truth_effect": "none",
            "certified_truth_modified": False,
            "dal_pssa_impact": "none",
        },
    }
    _fill_workbench_evidence_control(page, "#workbench-hardware-interface-design-output", json.dumps(valid_payload))
    _click_workbench_evidence_control(page, "#workbench-apply-hardware-interface-design-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-hardware-interface-design-status')
          ?.textContent.includes('Applied hardware/interface design')
        """
    )

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert draft["hardware_interface_designer"]["kind"] == "well-harness-editable-hardware-interface-design"
    assert draft["hardware_interface_designer"]["runtime_truth_effect"] == "none"
    assert draft["hardware_interface_designer"]["bindings"][0]["id"] == "BIND-A-B"
    assert draft["hardware_interface_designer_validation"]["status"] == "pass"
    assert draft["hardware_interface_designer_validation"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.evaluate(
        """
        (draftJson) => {
          const buffer = document.getElementById('workbench-draft-json-buffer');
          buffer.value = draftJson;
          buffer.dispatchEvent(new Event('input', { bubbles: true }));
        }
        """,
        draft_json,
    )
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["hardware_interface_designer"]["bindings"][0]["id"] == "BIND-A-B"
    assert imported["hardware_interface_designer_validation"]["status"] == "pass"

    stale_validation_draft = dict(imported)
    stale_validation_draft["hardware_interface_designer_validation"] = dict(
        imported["hardware_interface_designer_validation"]
    )
    stale_validation_draft["hardware_interface_designer_validation"]["counts"] = {
        **imported["hardware_interface_designer_validation"]["counts"],
        "lrus": 999,
    }
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(stale_validation_draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    recomputed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert recomputed["hardware_interface_designer_validation"]["counts"]["lrus"] == 2

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["hardware_interface_designer"]["runtime_truth_effect"] == "none"
    assert archive["hardware_interface_designer_validation"]["truth_effect"] == "none"
    assert archive["hardware_interface_designer"]["bindings"][0]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_interface_designer_checksum"]
    assert archive["checksums"]["hardware_interface_designer_validation_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_hardware_evidence_v2_tracks_selected_node_and_edge(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _wait_for_workbench_evidence_control(page, "#workbench-hardware-evidence-v2")
    assert page.locator("#workbench-hardware-evidence-v2-target").inner_text() == "node:logic1"

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-V2:J-V2")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    node_fields = page.locator("#workbench-hardware-evidence-v2-fields").inner_text()
    assert "TR-LRU-V2" in node_fields
    assert "J-V2" in node_fields
    assert "LOCAL PIN" in node_fields
    assert "evidence_gap" in node_fields
    assert "truth_effect: none" in node_fields
    assert "1 row(s)" in page.locator("#workbench-hardware-evidence-v2-pin-rows").inner_text()

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "EDGE-LRU-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "EDGE-CBL-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "EDGE-J-V2")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "logic2:in")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    assert page.locator("#workbench-hardware-evidence-v2-target").inner_text() == "edge:edge_logic1_logic2"
    edge_fields = page.locator("#workbench-hardware-evidence-v2-fields").inner_text()
    assert "EDGE-LRU-V2" in edge_fields
    assert "EDGE-J-V2" in edge_fields
    assert "LOCAL PIN" in edge_fields
    assert "evidence_gap" in edge_fields

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    assert "Hardware evidence v2:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Hardware evidence v2:" in page.locator("#workbench-linear-handoff-output").input_value()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["hardware_evidence_v2"]["target_kind"] == "edge"
    assert draft["hardware_evidence_v2"]["target_id"] == "edge_logic1_logic2"
    assert draft["hardware_evidence_v2"]["selected_binding"]["hardware_id"] == "EDGE-LRU-V2"
    assert draft["hardware_evidence_v2"]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["hardware_evidence_v2"]["target_kind"] == "edge"
    assert archive["hardware_evidence_v2"]["truth_effect"] == "none"
    assert archive["changerequest_proof_packet"]["hardware_evidence_v2_summary"]["target"] == "edge:edge_logic1_logic2"
    assert archive["checksums"]["hardware_evidence_v2_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_hardware_evidence_attachment_v2_covers_generic_graph_owners(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Attachable deploy cell")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "input")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy request")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_request_cmd")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-value-type", "boolean")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-evidence-status", "ui_draft")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "output")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy allowed")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_allowed_status")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-value-type", "boolean")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-evidence-status", "evidence_gap")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")

    hardware_design = {
        "$schema": "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json",
        "kind": "well-harness-editable-hardware-interface-design",
        "version": 1,
        "design_id": "ui-hw-attachment-v2",
        "system_id": "thrust-reverser",
        "candidate_state": "sandbox_candidate",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "runtime_truth_effect": "none",
        "lrus": [{"id": "LRU-ATTACH-A", "display_name": "Attach LRU A", "evidence_status": "ui_draft"}],
        "cables": [{
            "id": "CABLE-ATTACH-A",
            "display_name": "Attach cable",
            "source_lru_id": "LRU-ATTACH-A",
            "target_lru_id": "LRU-ATTACH-A",
            "cable_type": "harness",
            "evidence_status": "ui_draft",
        }],
        "connectors": [{
            "id": "CONN-ATTACH-A",
            "display_name": "Attach connector",
            "lru_id": "LRU-ATTACH-A",
            "connector_type": "MIL-DTL-38999",
            "evidence_status": "ui_draft",
        }],
        "ports": [
            {
                "id": "PORT-ATTACH-OUT",
                "display_name": "Attach out",
                "connector_id": "CONN-ATTACH-A",
                "direction": "output",
                "signal_id": "deploy_request_cmd",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
            },
            {
                "id": "PORT-ATTACH-IN",
                "display_name": "Attach in",
                "connector_id": "CONN-ATTACH-A",
                "direction": "input",
                "signal_id": "deploy_allowed_status",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
            },
        ],
        "pins": [
            {
                "id": "PIN-ATTACH-A1",
                "connector_id": "CONN-ATTACH-A",
                "pin_number": "A1",
                "port_id": "PORT-ATTACH-OUT",
                "signal_id": "deploy_request_cmd",
                "evidence_status": "ui_draft",
            },
            {
                "id": "PIN-ATTACH-A2",
                "connector_id": "CONN-ATTACH-A",
                "pin_number": "A2",
                "port_id": "PORT-ATTACH-IN",
                "signal_id": "deploy_allowed_status",
                "evidence_status": "ui_draft",
            },
        ],
        "bindings": [{
            "id": "BIND-ATTACH-A",
            "signal_id": "deploy_request_cmd",
            "source_port_id": "PORT-ATTACH-OUT",
            "target_port_id": "PORT-ATTACH-IN",
            "cable_id": "CABLE-ATTACH-A",
            "redundancy_status": "single",
            "evidence_status": "ui_draft",
            "truth_effect": "none",
        }],
        "evidence_gaps": [],
        "evidence_metadata": {"sample_pack_role": "hardware_interface_design", "source_refs": ["ui_draft.attachment_v2"]},
        "boundaries": {
            "runtime_scope": "sandbox_only",
            "hardware_truth_effect": "none",
            "certified_truth_modified": False,
            "dal_pssa_impact": "none",
        },
    }
    _fill_workbench_evidence_control(page, "#workbench-hardware-interface-design-output", json.dumps(hardware_design))
    _click_workbench_evidence_control(page, "#workbench-apply-hardware-interface-design-btn")

    page.locator('[data-editable-node-id="draft_node_1"]').click()
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "LRU-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CABLE-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "CONN-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "draft_node_1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "PORT-ATTACH-OUT")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id^="edge_component_two_stage_interlock"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "LRU-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CABLE-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "CONN-ATTACH-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "PORT-ATTACH-OUT")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "PORT-ATTACH-IN")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    attachment = draft["hardware_evidence_attachment_v2"]
    owner_kinds = {row["owner_kind"] for row in attachment["attachments"]}

    assert errors == [], f"page JS errors: {errors}"
    assert attachment["kind"] == "well-harness-workbench-hardware-evidence-attachment"
    assert attachment["version"] == "workbench-hardware-evidence-attachment.v2"
    assert attachment["candidate_state"] == "sandbox_candidate"
    assert attachment["truth_effect"] == "none"
    assert {"node", "port", "edge", "subsystem_group"}.issubset(owner_kinds)
    assert attachment["validation"]["status"] in {"pass", "warn"}
    assert attachment["validation"]["duplicate_attachment_id_count"] == 0
    assert attachment["validation"]["broken_reference_count"] == 0
    assert attachment["validation"]["evidence_gap_count"] >= 1
    assert any(row["owner_key"] == "node:draft_node_1" for row in attachment["attachments"])
    assert any(row["owner_key"] == "port:draft_node_1:out" for row in attachment["attachments"])
    assert any(row["owner_key"].startswith("edge:edge_component_two_stage_interlock") for row in attachment["attachments"])
    assert any(row["owner_key"].startswith("subsystem_group:subsystem_") for row in attachment["attachments"])

    _set_draft_buffer_value(page, json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["hardware_evidence_attachment_v2"]["attachment_count"] == attachment["attachment_count"]

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["hardware_evidence_attachment_v2"]["truth_effect"] == "none"
    assert archive["hardware_evidence_attachment_v2"]["attachment_count"] == attachment["attachment_count"]
    assert archive["checksums"]["hardware_evidence_attachment_v2_checksum"]
    assert archive["foundation_review_archive"]["sections"]["hardware_evidence_attachment_v2"]["status"] == "present"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_command_palette_executes_editor_commands_and_records_workspace_metadata(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.wait_for_function("() => document.querySelectorAll('.workbench-editable-node').length === 0")
    initial_node_count = page.locator(".workbench-editable-node").count()
    page.keyboard.press("Control+K")
    page.wait_for_selector("#workbench-command-palette:not([hidden])")
    page.fill("#workbench-command-palette-filter", "create")
    page.click('[data-command-palette-command="create_node"]')
    page.wait_for_function(
        f"() => document.querySelectorAll('.workbench-editable-node').length === {initial_node_count + 1}",
    )
    assert page.locator("#workbench-command-palette").get_attribute("hidden") is not None

    page.keyboard.press("Control+K")
    page.fill("#workbench-command-palette-filter", "duplicate")
    page.click('[data-command-palette-command="duplicate_selection"]')
    page.wait_for_function(
        f"() => document.querySelectorAll('.workbench-editable-node').length === {initial_node_count + 2}",
    )

    page.keyboard.press("Control+K")
    page.fill("#workbench-command-palette-filter", "wire")
    page.click('[data-command-palette-command="wire_edge"]')
    assert page.locator('[data-editor-tool="edge"]').get_attribute("aria-pressed") == "true"

    page.keyboard.press("Control+K")
    page.fill("#workbench-command-palette-filter", "debug")
    page.click('[data-command-palette-command="debug_selection"]')

    page.keyboard.press("Control+K")
    page.fill("#workbench-command-palette-filter", "archive")
    page.click('[data-command-palette-command="prepare_archive"]')
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    actions = [entry["action"] for entry in archive["workspace_document"]["action_log"]]

    assert errors == [], f"page JS errors: {errors}"
    assert "command_palette.create_node" in actions
    assert "command_palette.duplicate_selection" in actions
    assert "command_palette.wire_edge" in actions
    assert "command_palette.debug_selection" in actions
    assert "command_palette.prepare_archive" in actions
    assert archive["workspace_document"]["truth_effect"] == "none"
    assert archive["canvas_interaction_summary"]["last_action"] == "command_palette.prepare_archive"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_review_archive_restore_v3_round_trips_regression_bundle(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    page.locator('[data-editable-edge-id^="edge_component_two_stage_interlock"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "LRU-RESTORE-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CABLE-RESTORE-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "CONN-RESTORE-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "draft_node_1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "draft_node_2:in")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _select_workbench_run_control(page, "#workbench-sandbox-scenario-select", "nominal_landing")
    _click_workbench_run_control(page, "#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-diff-verdict')?.textContent.trim();
          return ['equivalent', 'divergent', 'invalid_model', 'invalid_scenario'].includes(verdict);
        }
        """
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output
            && output.value.includes('well-harness-workbench-sandbox-test-run-report')
            && output.value.includes('sandbox_runner_trace_kernel');
        }
        """
    )
    page.keyboard.press("Control+K")
    page.fill("#workbench-command-palette-filter", "debug")
    page.click('[data-command-palette-command="debug_selection"]')

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    expected_node_count = archive["editable_graph_document"]["node_count"]
    expected_edge_count = archive["editable_graph_document"]["edge_count"]

    assert archive["review_archive_regression_bundle_v3"]["kind"] == "well-harness-workbench-review-archive-regression-bundle"
    assert archive["review_archive_regression_bundle_v3"]["full_e2e_49_49_claim"] == "not_claimed"
    assert archive["review_archive_regression_bundle_v3"]["mypy_strict_clean_claim"] == "not_claimed"
    assert archive["review_archive_regression_bundle_v3"]["restore_review_checklist"]["kind"] == (
        "well-harness-workbench-archive-restore-review-checklist"
    )
    assert archive["review_archive_regression_bundle_v3"]["restore_review_checklist"]["status"] == "pass"
    assert archive["review_archive_regression_bundle_v3"]["restore_review_checklist"]["items"]["graph_review"]["status"] == "pass"
    assert archive["review_archive_regression_bundle_v3"]["restore_review_checklist"]["items"]["checksums_review"]["status"] == "pass"
    assert archive["checksums"]["review_archive_regression_bundle_v3_checksum"]

    page.click("#workbench-start-empty-draft-btn")
    page.wait_for_function("() => document.querySelectorAll('.workbench-editable-node').length === 0")
    _set_archive_buffer_value(page, json.dumps(archive))
    _click_workbench_handoff_control(page, "#workbench-restore-review-archive-btn")

    validation = json.loads(page.locator("#workbench-review-archive-restore-output").input_value())
    bundle = json.loads(page.locator("#workbench-regression-bundle-output").input_value())
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    restored = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    assert errors == [], f"page JS errors: {errors}"
    assert validation["status"] == "pass", json.dumps(validation.get("findings"), sort_keys=True)
    assert validation["checksum_mismatch_count"] == 0
    assert validation["red_line_status"] == "pass"
    assert bundle["restore_validation_status"] == "pass"
    assert bundle["restore_review_checklist"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["graph_review"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["tests_review"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["traces_review"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["evidence_review"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["checksums_review"]["status"] == "pass"
    assert bundle["restore_review_checklist"]["items"]["handoff_review"]["status"] == "pass"
    assert bundle["restored_graph"]["node_count"] == expected_node_count
    assert bundle["restored_graph"]["edge_count"] == expected_edge_count
    assert bundle["full_e2e_49_49_claim"] == "not_claimed"
    assert bundle["mypy_strict_clean_claim"] == "not_claimed"
    assert restored["editable_graph_document"]["node_count"] == expected_node_count
    assert restored["editable_graph_document"]["edge_count"] == expected_edge_count
    assert restored["hardware_evidence_attachment_v2"]["attachment_count"] >= 1
    assert page.locator("#workbench-archive-review-checklist-status").inner_text() == "通过"
    assert page.locator('[data-archive-review-check="graph"]').get_attribute("data-check-status") == "pass"
    assert page.locator('[data-archive-review-check="checksums"]').get_attribute("data-check-status") == "pass"
    assert page.locator('[data-archive-review-check="handoff"]').get_attribute("data-check-status") == "pass"
    assert page.locator("#workbench-archive-status").inner_text().startswith("Restored local review archive")

    mutated_archive = json.loads(json.dumps(archive))
    mutated_archive["editable_graph_document"]["node_count"] = expected_node_count + 1
    _set_archive_buffer_value(page, json.dumps(mutated_archive))
    _click_workbench_handoff_control(page, "#workbench-restore-review-archive-btn")
    mismatch_validation = json.loads(page.locator("#workbench-review-archive-restore-output").input_value())
    mismatch = next(
        finding
        for finding in mismatch_validation["findings"]
        if finding.get("section") == "editable_graph_document"
    )

    assert mismatch_validation["status"] == "fail"
    assert mismatch_validation["checksum_mismatch_count"] >= 1
    assert mismatch["checksum_key"] == "editable_graph_document_checksum"
    assert mismatch["checksum_path"] == "checksums.editable_graph_document_checksum"
    assert mismatch["expected_checksum"] == archive["checksums"]["editable_graph_document_checksum"]
    assert mismatch["actual_checksum"] != mismatch["expected_checksum"]
    assert mismatch["evidence_path"] == "editable_graph_document"
    assert mismatch["truth_effect"] == "none"
    mismatch_bundle = json.loads(page.locator("#workbench-regression-bundle-output").input_value())
    assert mismatch_bundle["restore_review_checklist"]["status"] == "fail"
    assert mismatch_bundle["restore_review_checklist"]["items"]["checksums_review"]["status"] == "fail"
    assert mismatch_bundle["restore_review_checklist"]["items"]["checksums_review"]["path"] == (
        "checksums.editable_graph_document_checksum"
    )
    assert page.locator("#workbench-archive-review-checklist-status").inner_text() == "阻塞"
    assert page.locator('[data-archive-review-check="checksums"]').get_attribute("data-check-status") == "fail"
    assert "checksums.editable_graph_document_checksum" in page.locator(
        '[data-archive-review-check="checksums"]'
    ).inner_text()
    assert page.locator("#workbench-archive-status").inner_text().startswith("Review archive restore blocked")


def test_workbench_selected_debug_timeline_tracks_selection_diff_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _wait_for_workbench_run_control(page, "#workbench-selected-debug-timeline")
    assert page.locator("#workbench-selected-debug-target").inner_text() == "node:logic1"
    assert page.locator("#workbench-selected-debug-verdict").inner_text() == "未运行"
    assert page.locator("#workbench-selected-debug-link-status").inner_text() == "仅选择"

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "EDGE-LRU-DEBUG")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "EDGE-CBL-DEBUG")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "EDGE-J-DEBUG")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "logic2:in")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    assert page.locator("#workbench-selected-debug-target").inner_text() == "edge:edge_logic1_logic2"
    assert "EDGE-LRU-DEBUG" in page.locator("#workbench-selected-debug-hardware").inner_text()
    assert "logic1 -> logic2" in page.locator("#workbench-selected-debug-context").inner_text()

    _select_workbench_run_control(page, "#workbench-sandbox-scenario-select", "nominal_landing")
    _click_workbench_run_control(page, "#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-sandbox-timeline-strip')
            ?.getAttribute('data-debug-verdict');
          return ['equivalent', 'divergent', 'invalid_model', 'invalid_scenario'].includes(verdict);
        }
        """
    )
    assert (
        page.locator("#workbench-sandbox-timeline-strip")
        .get_attribute("data-selected-target")
        == "edge:edge_logic1_logic2"
    )
    assert (
        page.locator("#workbench-sandbox-timeline-strip")
        .get_attribute("data-debug-truth-effect")
        == "none"
    )

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["selected_debug_timeline"]["target_kind"] == "edge"
    assert draft["selected_debug_timeline"]["target_id"] == "edge_logic1_logic2"
    assert draft["selected_debug_timeline"]["scenario_id"] == "nominal_landing"
    assert draft["selected_debug_timeline"]["hardware_overlay"]["hardware_id"] == "EDGE-LRU-DEBUG"
    assert draft["selected_debug_timeline"]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    assert "Selected debug timeline:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Selected debug timeline:" in page.locator("#workbench-linear-handoff-output").input_value()

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["selected_debug_timeline"]["target_kind"] == "edge"
    assert archive["selected_debug_timeline"]["truth_effect"] == "none"
    assert archive["changerequest_proof_packet"]["selected_debug_timeline_summary"]["target"] == "edge:edge_logic1_logic2"
    assert archive["checksums"]["selected_debug_timeline_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_diff_review_v2_tracks_diff_handoff_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _wait_for_workbench_run_control(page, "#workbench-diff-review-v2")
    diff_review_panel = page.locator("#workbench-diff-review-v2")
    assert diff_review_panel.get_attribute("data-review-verdict") == "not_run"
    assert diff_review_panel.get_attribute("data-review-readiness") == "run_required"
    assert diff_review_panel.get_attribute("data-review-archive-state") == "not_archive_ready"
    assert diff_review_panel.get_attribute("data-review-certification-claim") == "none"

    page.click("#workbench-derive-draft-btn")
    _select_workbench_run_control(page, "#workbench-sandbox-scenario-select", "nominal_landing")
    _click_workbench_run_control(page, "#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-diff-review-v2')
            ?.getAttribute('data-review-verdict');
          return ['equivalent', 'divergent', 'invalid_model', 'invalid_scenario'].includes(verdict);
        }
        """
    )
    verdict = diff_review_panel.get_attribute("data-review-verdict")
    readiness = diff_review_panel.get_attribute("data-review-readiness")
    expected_readiness = {
        "equivalent": "ready",
        "divergent": "review_required",
        "invalid_model": "blocked",
        "invalid_scenario": "blocked",
    }[verdict]
    assert readiness == expected_readiness
    assert diff_review_panel.get_attribute("data-review-archive-state") == "archive_ready"
    assert page.locator("#workbench-diff-review-v2-scenario").inner_text() == "名义着陆"
    assert (
        page.locator("#workbench-diff-review-v2")
        .get_attribute("data-review-truth-effect")
        == "none"
    )

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    review = draft["candidate_baseline_diff_review_v2"]
    assert review["kind"] == "well-harness-workbench-candidate-baseline-diff-review-v2"
    assert review["candidate_state"] == "sandbox_candidate"
    assert review["verdict"] == verdict
    assert review["review_readiness"] == expected_readiness
    assert review["archive_state"] == "archive_ready"
    assert review["certification_claim"] == "none"
    assert review["controller_truth_modified"] is False
    assert review["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    assert "Diff review v2:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Diff review v2:" in page.locator("#workbench-linear-handoff-output").input_value()

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["candidate_baseline_diff_review_v2"]["verdict"] == verdict
    assert archive["candidate_baseline_diff_review_v2"]["certification_claim"] == "none"
    assert archive["candidate_baseline_diff_review_v2"]["truth_effect"] == "none"
    assert archive["changerequest_proof_packet"]["candidate_baseline_diff_review_v2_summary"]["verdict"] == verdict
    assert archive["checksums"]["candidate_baseline_diff_review_v2_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_journey_acceptance_bundle_derivation_binding_sandboxrun_handoff_archive(
    demo_server: str, browser: Any
) -> None:
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-derive-draft-btn")
    _select_workbench_run_control(page, "#workbench-sandbox-scenario-select", "nominal_landing")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-ACCEPTANCE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-TR-ACCEPTANCE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-ACCEPT")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-ACCEPTANCE:J-ACCEPT")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "complete"

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    binding = draft["hardware_bindings"][0]
    assert draft["kind"] == "well-harness-workbench-ui-draft"
    assert draft["system_id"] == "thrust-reverser"
    assert draft["draft_state"] == "derived"
    assert draft["truth_level_impact"] == "none"
    assert draft["dal_pssa_impact"] == "none"
    assert draft["controller_truth_modified"] is False
    assert binding["owner_kind"] == "node"
    assert binding["owner_id"] == "logic1"
    assert binding["hardware_id"] == "TR-LRU-ACCEPTANCE"
    assert binding["cable"] == "CBL-TR-ACCEPTANCE"
    assert binding["connector"] == "J-ACCEPT"
    assert binding["port_local"] == "logic1:out"
    assert binding["port_peer"] == "TR-LRU-ACCEPTANCE:J-ACCEPT"
    assert binding["evidence_status"] == "ui_draft"
    assert binding["truth_effect"] == "none"

    _click_workbench_run_control(page, "#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-diff-verdict')?.textContent.trim();
          return verdict && verdict !== 'running' && verdict !== 'not_run';
        }
        """
    )
    verdict = page.locator("#workbench-diff-verdict").inner_text()
    assert verdict in {"equivalent", "divergent", "invalid_model", "invalid_scenario"}
    assert page.locator("#workbench-diff-scenario").inner_text() == "nominal_landing"

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-pr-proof-output');
          return output && output.value.includes('Candidate state: sandbox_candidate');
        }
        """
    )
    linear_body = page.locator("#workbench-linear-handoff-output").input_value()
    pr_proof = page.locator("#workbench-pr-proof-output").input_value()
    changerequest_packet = json.loads(page.locator("#workbench-changerequest-packet-output").input_value())
    handoff_status = page.locator("#workbench-handoff-status").inner_text()
    assert "Candidate state: sandbox_candidate" in pr_proof
    assert "Certification claim: none" in pr_proof
    assert "Truth-level impact: none" in pr_proof
    assert "No live Linear mutation" in pr_proof
    assert "No live Linear mutation" in handoff_status
    assert "## Red Lines" in linear_body
    assert "## Test Delta" in linear_body
    assert "Diagnostic repair actions:" in linear_body
    assert changerequest_packet["kind"] == "well-harness-workbench-changerequest-handoff-packet"
    assert (
        changerequest_packet["$schema"]
        == "https://well-harness.local/json_schema/workbench_changerequest_handoff_v1.schema.json"
    )
    assert changerequest_packet["candidate_state"] == "sandbox_candidate"
    assert changerequest_packet["certification_claim"] == "none"
    assert changerequest_packet["truth_effect"] == "none"
    assert changerequest_packet["live_linear_mutation"] is False
    assert changerequest_packet["runtime_mutates_truth"] is False
    assert changerequest_packet["serialization"]["canonicalization"] == "json.sort_keys.separators.v1"
    assert changerequest_packet["metadata"]["test_delta"]["e2e_49_49"] == "not_claimed"
    assert changerequest_packet["red_line_metadata"]["controller_truth_modified"] is False

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-evidence-archive-output');
          return output && output.value.includes('well-harness-workbench-evidence-archive');
        }
        """
    )
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    packet = archive["changerequest_proof_packet"]
    handoff_packet = archive["changerequest_handoff_packet"]
    red_lines = archive["red_line_metadata"]
    checksums = archive["checksums"]

    assert errors == [], f"page JS errors: {errors}"
    assert archive["kind"] == "well-harness-workbench-evidence-archive"
    assert archive["archive_scope"] == "local_draft_download"
    assert archive["diff_summary"]["verdict"] == verdict
    assert archive["diff_summary"]["scenario_id"] == "nominal_landing"
    assert archive["diff_summary"].get("missing_diff_fallback") is not True
    assert packet["candidate_state"] == "sandbox_candidate"
    assert packet["certification_claim"] == "none"
    assert packet["truth_level_impact"] == "none"
    assert packet["dal_pssa_impact"] == "none"
    assert packet["controller_truth_modified"] is False
    assert packet["frozen_assets_modified"] is False
    assert packet["truth_effect"] == "none"
    assert packet["linear"]["live_mutation"] is False
    assert packet["sandbox_diff"]["verdict"] == verdict
    assert handoff_packet["kind"] == "well-harness-workbench-changerequest-handoff-packet"
    assert handoff_packet["truth_scope"] == "evidence_only"
    assert handoff_packet["metadata"]["sandbox_verdict"] == verdict
    assert handoff_packet["metadata"]["test_delta"]["mypy_strict_clean"] == "not_claimed"
    assert handoff_packet["live_linear_mutation"] is False
    assert handoff_packet["truth_effect"] == "none"
    assert red_lines["truth_level_impact"] == "none"
    assert red_lines["dal_pssa_impact"] == "none"
    assert red_lines["controller_truth_modified"] is False
    assert red_lines["live_linear_mutation"] is False
    assert archive["gate_claims"]["e2e_49_49"] == "not_claimed"
    assert archive["gate_claims"]["mypy_strict_clean"] == "not_claimed"
    assert archive["gate_claims"]["hard_hold_policy"] == "required"
    assert archive["gate_claims"]["default_pytest"] == "warning"
    assert archive["known_blockers"]
    assert checksums["manifest_checksum"]
    assert checksums["diff_summary_checksum"]
    assert checksums["changerequest_proof_packet_checksum"]
    assert checksums["changerequest_handoff_packet_checksum"]
    assert checksums["gate_claims_checksum"]
    assert checksums["known_blockers_checksum"]


def test_workbench_hardware_palette_creates_and_applies_sandbox_bindings(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    _wait_for_workbench_evidence_control(page, '[data-hardware-palette-id="lru:etrac"]')

    _select_workbench_evidence_control(page, "#workbench-hardware-palette-action", "apply-binding")
    _click_workbench_evidence_control(page, '[data-hardware-palette-id="lru:etrac"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    lru_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in lru_draft["nodes"] if node["id"] == "logic1")

    assert logic1["hardware_binding"]["hardware_id"] == "etrac"
    assert logic1["hardware_binding"]["source_ref"].startswith("docs/thrust_reverser/")
    assert lru_draft["hardware_palette"]["source"] == "read_only_hardware_evidence_api"
    assert lru_draft["hardware_palette"]["truth_effect"] == "none"
    assert lru_draft["controller_truth_modified"] is False

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _select_workbench_run_control(page, "#workbench-port-value-type", "number")
    page.click("#workbench-apply-port-contract-btn")
    _open_workbench_inspector_mode(page, "evidence")
    page.locator('[data-hardware-palette-id^="signal:SW1"]').first.click()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    edge_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    edge = next(item for item in edge_draft["edges"] if item["id"] == "edge_logic1_logic2")
    assert edge["signal_id"] == "SW1"
    assert edge["value_type"] == "number"
    assert edge["hardware_binding"]["hardware_id"] == "external_throttle_resolver"
    assert edge["hardware_binding"]["truth_effect"] == "none"

    _select_workbench_evidence_control(page, "#workbench-hardware-palette-action", "create-node")
    _open_workbench_inspector_mode(page, "evidence")
    page.locator('[data-hardware-palette-id^="signal:SW1"]').first.click()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    node_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    palette_node = next(node for node in node_draft["nodes"] if node["id"] == "draft_node_1")

    assert errors == [], f"page JS errors: {errors}"
    assert palette_node["draftNode"] is True
    assert palette_node["sourceRef"].startswith("ui_draft.hardware_palette.signal.signal:SW1")
    assert palette_node["hardware_binding"]["hardware_id"] == "external_throttle_resolver"
    assert palette_node["hardware_binding"]["truth_effect"] == "none"
    assert palette_node["port_contract"]["input_signal_id"] == "SW1"
    assert palette_node["port_contract"]["truth_effect"] == "none"
    assert node_draft["truth_level_impact"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["hardware_palette"]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_palette_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_typed_port_contract_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_run_control(page, "#workbench-port-input-signal", "logic1_candidate_input")
    _fill_workbench_run_control(page, "#workbench-port-output-signal", "logic1_candidate_output")
    _select_workbench_run_control(page, "#workbench-port-value-type", "number")
    _fill_workbench_run_control(page, "#workbench-port-unit", "deg")
    _check_workbench_run_control(page, "#workbench-port-required")
    page.click("#workbench-apply-port-contract-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    logic1 = next(node for node in draft["nodes"] if node["id"] == "logic1")
    typed_ports = {port["id"]: port for port in draft["typed_ports"]}
    assert logic1["port_contract"]["input_signal_id"] == "logic1_candidate_input"
    assert logic1["port_contract"]["output_signal_id"] == "logic1_candidate_output"
    assert logic1["port_contract"]["value_type"] == "number"
    assert logic1["port_contract"]["unit"] == "deg"
    assert logic1["port_contract"]["required"] is True
    assert typed_ports["logic1:out"]["signal_id"] == "logic1_candidate_output"
    assert typed_ports["logic1:out"]["value_type"] == "number"
    assert typed_ports["logic1:out"]["unit"] == "deg"
    assert typed_ports["logic1:out"]["required"] is True
    assert draft["port_contract_summary"]["total_ports"] >= 2
    assert draft["port_contract_summary"]["truth_effect"] == "none"
    assert draft["port_compatibility_report"]["status"] == "warn"
    assert draft["port_compatibility_report"]["truth_effect"] == "none"
    assert any(
        issue["code"] == "value_type_mismatch"
        for issue in draft["port_compatibility_report"]["issues"]
    )
    assert (
        page.locator('[data-editable-edge-id="edge_logic1_logic2"]')
        .get_attribute("data-port-compatibility")
        == "warn"
    )

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    edge_detail = page.locator("#workbench-inspector-evidence-detail").inner_text()
    assert "Port compatibility" in edge_detail
    assert "warn" in edge_detail

    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_logic1 = next(node for node in round_trip["nodes"] if node["id"] == "logic1")
    assert round_trip_logic1["port_contract"]["output_signal_id"] == "logic1_candidate_output"
    assert round_trip["port_contract_summary"]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["typed_ports"]
    assert archive["port_contract_summary"]["truth_effect"] == "none"
    assert archive["port_compatibility_report"]["status"] == "warn"
    assert archive["port_compatibility_report"]["truth_effect"] == "none"
    assert archive["checksums"]["typed_ports_checksum"]
    assert archive["checksums"]["port_contract_summary_checksum"]
    assert archive["checksums"]["port_compatibility_report_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_interface_matrix_exports_node_and_edge_design_rows(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-MATRIX-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-MATRIX-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-MATRIX-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-MATRIX-A:J-MATRIX-A")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-MATRIX-B")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-MATRIX-B")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-MATRIX-B")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_evidence_control(page, "#workbench-export-interface-matrix-btn")
    matrix = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    rows = matrix["rows"]
    node_row = next(row for row in rows if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    edge_row = next(row for row in rows if row["owner_kind"] == "edge" and row["owner_id"] == "edge_logic1_logic2")

    assert errors == [], f"page JS errors: {errors}"
    assert matrix["kind"] == "well-harness-workbench-interface-matrix"
    assert matrix["row_count"] >= 2
    assert matrix["truth_effect"] == "none"
    assert node_row["hardware_id"] == "TR-LRU-MATRIX-A"
    assert node_row["cable"] == "CBL-MATRIX-A"
    assert node_row["connector"] == "J-MATRIX-A"
    assert node_row["binding_quality"] == "complete"
    assert node_row["local_typed_port"]["port_id"] == "logic1:out"
    assert node_row["local_typed_port"]["truth_effect"] == "none"
    assert edge_row["hardware_id"] == "TR-LRU-MATRIX-B"
    assert edge_row["port_local"] == "logic1:out"
    assert edge_row["port_peer"] == "logic2:in:ui_edge:logic1"
    assert edge_row["binding_quality"] == "complete"
    assert edge_row["peer_typed_port"]["port_id"] == "logic2:in:ui_edge:logic1"
    assert "Exported" in page.locator("#workbench-interface-matrix-status").inner_text()

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    assert "Interface matrix:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Interface matrix:" in page.locator("#workbench-linear-handoff-output").input_value()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["interface_matrix"]["row_count"] == matrix["row_count"]
    assert draft["interface_matrix"]["truth_effect"] == "none"
    assert draft["changerequest_proof_packet"]["interface_matrix_summary"]["row_count"] == matrix["row_count"]

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["interface_matrix"]["row_count"] == matrix["row_count"]
    assert archive["interface_matrix"]["truth_effect"] == "none"
    assert archive["changerequest_proof_packet"]["interface_matrix_summary"]["row_count"] == matrix["row_count"]
    assert archive["checksums"]["interface_matrix_checksum"]
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"


def test_workbench_interface_matrix_import_applies_sandbox_bindings_and_rejects_truth_claims(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-BEFORE:J-BEFORE")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "EDGE-LRU-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "EDGE-CBL-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "EDGE-J-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_evidence_control(page, "#workbench-export-interface-matrix-btn")
    matrix = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    for row in matrix["rows"]:
        if row["owner_kind"] == "node" and row["owner_id"] == "logic1":
            row["hardware_id"] = "TR-LRU-APPLIED"
            row["cable"] = "evidence_gap"
            row["connector"] = "J-APPLIED"
            row["port_peer"] = "TR-LRU-APPLIED:J-APPLIED"
        if row["owner_kind"] == "edge" and row["owner_id"] == "edge_logic1_logic2":
            row["hardware_id"] = "EDGE-LRU-APPLIED"
            row["cable"] = "EDGE-CBL-APPLIED"
            row["connector"] = "EDGE-J-APPLIED"
    matrix["rows"].append({
        "row_id": "interface:ghost",
        "owner_kind": "node",
        "owner_id": "ghost_node",
        "hardware_id": "GHOST-LRU",
        "cable": "GHOST-CBL",
        "connector": "GHOST-J",
        "port_local": "ghost:out",
        "port_peer": "ghost:peer",
        "evidence_status": "ui_draft",
        "truth_effect": "none",
    })
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-output", json.dumps(matrix))
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    status = page.locator("#workbench-interface-matrix-status").inner_text()
    assert "Applied 2 matrix row(s), deselected 0, no-op 0, skipped 1" in status

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in draft["nodes"] if node["id"] == "logic1")
    edge = next(item for item in draft["edges"] if item["id"] == "edge_logic1_logic2")
    assert errors == [], f"page JS errors: {errors}"
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-APPLIED"
    assert logic1["hardware_binding"]["cable"] == "evidence_gap"
    assert logic1["hardware_binding"]["connector"] == "J-APPLIED"
    assert logic1["hardware_binding"]["truth_effect"] == "none"
    assert edge["hardware_binding"]["hardware_id"] == "EDGE-LRU-APPLIED"
    assert edge["hardware_binding"]["connector"] == "EDGE-J-APPLIED"
    assert edge["hardware_binding"]["truth_effect"] == "none"
    assert draft["interface_matrix"]["coverage"]["complete"] >= 1

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    archive_node = next(row for row in archive["interface_matrix"]["rows"] if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    assert archive_node["hardware_id"] == "TR-LRU-APPLIED"
    assert archive["checksums"]["interface_matrix_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False

    rejected = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    rejected["rows"][0]["truth_effect"] = "certified"
    rejected["rows"][0]["hardware_id"] = "SHOULD-NOT-APPLY"
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-output", json.dumps(rejected))
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "truth_effect must be none" in page.locator("#workbench-interface-matrix-status").inner_text()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    after_reject = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in after_reject["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-APPLIED"


def test_workbench_interface_matrix_csv_tsv_bridge_round_trips_sandbox_rows(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-CSV-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-CSV-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-CSV-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-CSV-BEFORE:J-CSV-BEFORE")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_evidence_control(page, "#workbench-export-interface-matrix-btn")
    _click_workbench_evidence_control(page, "#workbench-export-interface-matrix-csv-btn")
    exported_csv = page.locator("#workbench-interface-matrix-csv-output").input_value()
    assert "row_id,owner_kind,owner_id,hardware_id,cable,connector,port_local,port_peer,evidence_status,truth_effect,source_ref" in exported_csv

    rows = list(csv.DictReader(io.StringIO(exported_csv)))
    logic1_row = next(row for row in rows if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    logic1_row["hardware_id"] = "TR-LRU-CSV,APPLIED"
    logic1_row["cable"] = ""
    logic1_row["connector"] = 'J-CSV-"A"'
    logic1_row["port_peer"] = "TR-LRU-CSV:J-CSV-A"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-csv-output", buffer.getvalue())
    _click_workbench_evidence_control(page, "#workbench-import-interface-matrix-csv-btn")
    report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert report["status"] == "warn"
    assert report["truth_effect"] == "none"
    assert report["evidence_gap_field_count"] >= 1
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "Applied 1 matrix row(s)" in page.locator("#workbench-interface-matrix-status").inner_text()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    csv_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in csv_draft["nodes"] if node["id"] == "logic1")
    assert errors == [], f"page JS errors: {errors}"
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-CSV,APPLIED"
    assert logic1["hardware_binding"]["cable"] == "evidence_gap"
    assert logic1["hardware_binding"]["connector"] == 'J-CSV-"A"'
    assert logic1["hardware_binding"]["truth_effect"] == "none"

    tsv_header = "\t".join([
        "row_id",
        "owner_kind",
        "owner_id",
        "hardware_id",
        "cable",
        "connector",
        "port_local",
        "port_peer",
        "evidence_status",
        "truth_effect",
        "source_ref",
    ])
    tsv_row = "\t".join([
        "interface:tsv:logic1",
        "node",
        "logic1",
        "TR-LRU-TSV-APPLIED",
        "",
        "J-TSV-APPLIED",
        "logic1:out",
        "TR-LRU-TSV-APPLIED:J-TSV-APPLIED",
        "ui_draft",
        "none",
        "ui_draft.tsv.logic1",
    ])
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-csv-output", f"{tsv_header}\n{tsv_row}\n")
    _click_workbench_evidence_control(page, "#workbench-import-interface-matrix-csv-btn")
    assert "Matrix validation warn" in page.locator("#workbench-interface-matrix-status").inner_text()
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    tsv_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_tsv = next(node for node in tsv_draft["nodes"] if node["id"] == "logic1")
    assert logic1_tsv["hardware_binding"]["hardware_id"] == "TR-LRU-TSV-APPLIED"
    assert logic1_tsv["hardware_binding"]["cable"] == "evidence_gap"
    assert logic1_tsv["hardware_binding"]["connector"] == "J-TSV-APPLIED"
    assert logic1_tsv["hardware_binding"]["truth_effect"] == "none"

    rejected_row = tsv_row.replace("TR-LRU-TSV-APPLIED", "SHOULD-NOT-APPLY", 1).replace("\tnone\t", "\tcertified\t")
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-csv-output", f"{tsv_header}\n{rejected_row}\n")
    _click_workbench_evidence_control(page, "#workbench-import-interface-matrix-csv-btn")
    failed_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert failed_report["status"] == "fail"
    assert failed_report["truth_effect_violation_count"] >= 1
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "Matrix validation failed" in page.locator("#workbench-interface-matrix-status").inner_text()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    rejected_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in rejected_draft["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-TSV-APPLIED"


def test_workbench_interface_matrix_validation_previews_without_mutating_draft(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-PREVIEW-BEFORE:J-PREVIEW-BEFORE")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "EDGE-LRU-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "EDGE-CBL-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "EDGE-J-PREVIEW-BEFORE")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "logic1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    _click_workbench_evidence_control(page, "#workbench-export-interface-matrix-btn")
    matrix = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    for row in matrix["rows"]:
        if row["owner_kind"] == "node" and row["owner_id"] == "logic1":
            row["hardware_id"] = "TR-LRU-PREVIEW-EDITED"
            row["cable"] = "evidence_gap"
            row["connector"] = "J-DUP"
            row["port_local"] = "logic1:out"
            row["port_peer"] = "TR-LRU-PREVIEW-EDITED:J-DUP"
        if row["owner_kind"] == "edge" and row["owner_id"] == "edge_logic1_logic2":
            row["hardware_id"] = "TR-LRU-PREVIEW-EDITED"
            row["cable"] = "CBL-DUP"
            row["connector"] = "J-DUP"
            row["port_local"] = "logic1:out"
            row["port_peer"] = "TR-LRU-PREVIEW-EDITED:J-DUP"
    matrix["rows"].append({
        "row_id": "interface:ghost-preview",
        "owner_kind": "edge",
        "owner_id": "ghost_edge",
        "hardware_id": "GHOST-LRU",
        "cable": "GHOST-CBL",
        "connector": "GHOST-J",
        "port_local": "ghost:out",
        "port_peer": "ghost:in",
        "evidence_status": "ui_draft",
        "truth_effect": "none",
    })

    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-output", json.dumps(matrix))
    _click_workbench_evidence_control(page, "#workbench-validate-interface-matrix-btn")
    report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert report["kind"] == "well-harness-workbench-interface-matrix-validation-report"
    assert report["status"] == "warn"
    assert report["truth_effect"] == "none"
    assert report["applyable_row_count"] >= 2
    assert report["skipped_row_count"] >= 1
    assert report["missing_owner_count"] == 1
    assert report["evidence_gap_field_count"] >= 1
    assert report["duplicate_interface_reuse_count"] >= 1
    assert report["typed_port_conflict_count"] >= 1
    assert report["changed_row_count"] >= 2
    assert report["noop_row_count"] == 0
    node_preview = next(row for row in report["rows"] if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    assert node_preview["current_binding"]["hardware_id"] == "TR-LRU-PREVIEW-BEFORE"
    assert node_preview["candidate_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"
    assert node_preview["field_deltas"]["hardware_id"]["current"] == "TR-LRU-PREVIEW-BEFORE"
    assert node_preview["field_deltas"]["hardware_id"]["candidate"] == "TR-LRU-PREVIEW-EDITED"
    assert set(node_preview["changed_fields"]) >= {"hardware_id", "cable", "connector", "port_peer"}
    assert node_preview["change_count"] >= 4
    ghost_preview = next(row for row in report["rows"] if row["owner_id"] == "ghost_edge")
    assert ghost_preview["current_binding"] is None
    assert ghost_preview["candidate_binding"]["hardware_id"] == "GHOST-LRU"
    assert "Matrix validation warn" in page.locator("#workbench-interface-matrix-status").inner_text()
    review = page.locator("#workbench-interface-matrix-review")
    assert review.get_attribute("data-review-state") == "warn"
    logic1_review = review.locator('[data-interface-matrix-review-owner-id="logic1"]')
    assert logic1_review.get_attribute("data-row-status") == "applyable"
    assert logic1_review.get_attribute("data-row-action") == "apply"
    assert "hardware_id" in logic1_review.inner_text()
    assert "TR-LRU-PREVIEW-BEFORE -> TR-LRU-PREVIEW-EDITED" in logic1_review.inner_text()
    ghost_review = review.locator('[data-interface-matrix-review-owner-id="ghost_edge"]')
    assert ghost_review.get_attribute("data-row-status") == "skipped"
    assert ghost_review.get_attribute("data-row-action") == "skip"
    node_checkbox = logic1_review.locator('[data-interface-matrix-review-select="true"]')
    edge_review = review.locator('[data-interface-matrix-review-owner-id="edge_logic1_logic2"]')
    edge_checkbox = edge_review.locator('[data-interface-matrix-review-select="true"]')
    ghost_checkbox = ghost_review.locator('[data-interface-matrix-review-select="true"]')
    assert node_checkbox.is_checked()
    assert edge_checkbox.is_checked()
    assert ghost_checkbox.is_disabled()
    edge_checkbox.uncheck()
    assert not edge_checkbox.is_checked()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    preview_only_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in preview_only_draft["nodes"] if node["id"] == "logic1")
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-BEFORE"
    assert preview_only_draft["interface_matrix_validation"]["status"] == "warn"

    _click_workbench_handoff_control(page, "#workbench-generate-handoff-btn")
    pr_proof = page.locator("#workbench-pr-proof-output").input_value()
    change_request_packet = json.loads(page.locator("#workbench-changerequest-packet-output").input_value())
    assert "Interface matrix validation: 警告" in pr_proof
    assert (
        change_request_packet["changerequest_proof_packet"]["interface_matrix_validation_summary"]["status"]
        == "warn"
    )
    assert "Interface matrix validation:" in page.locator("#workbench-linear-handoff-output").input_value()

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["interface_matrix_validation"]["status"] == "warn"
    assert archive["checksums"]["interface_matrix_validation_checksum"]
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"

    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "Applied 1 matrix row(s), deselected 1, no-op 0, skipped 1" in page.locator("#workbench-interface-matrix-status").inner_text()
    post_apply_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert post_apply_report["changed_row_count"] == 0
    assert post_apply_report["noop_row_count"] >= 2
    node_noop = next(row for row in post_apply_report["rows"] if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    assert node_noop["status"] == "no_op"
    assert node_noop["action"] == "none"
    assert node_noop["changed_fields"] == []
    assert node_noop["change_count"] == 0
    assert node_noop["current_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"
    assert node_noop["candidate_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"
    noop_review = review.locator('[data-interface-matrix-review-owner-id="logic1"]')
    assert noop_review.get_attribute("data-row-status") == "no_op"
    assert noop_review.get_attribute("data-row-action") == "none"
    assert "none" in noop_review.inner_text()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    after_apply = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_apply = next(node for node in after_apply["nodes"] if node["id"] == "logic1")
    edge_after_apply = next(item for item in after_apply["edges"] if item["id"] == "edge_logic1_logic2")
    assert logic1_after_apply["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"
    assert edge_after_apply["hardware_binding"]["hardware_id"] == "EDGE-LRU-PREVIEW-BEFORE"

    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "Applied 0 matrix row(s), deselected 0, no-op 2, skipped 0" in page.locator("#workbench-interface-matrix-status").inner_text()
    second_apply_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert second_apply_report["changed_row_count"] == 0
    assert second_apply_report["noop_row_count"] >= 2
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    after_second_apply = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_second_apply = next(node for node in after_second_apply["nodes"] if node["id"] == "logic1")
    assert logic1_after_second_apply["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"

    rejected = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    rejected["rows"][0]["truth_effect"] = "certified"
    rejected["rows"][0]["hardware_id"] = "SHOULD-NOT-APPLY"
    _fill_workbench_evidence_control(page, "#workbench-interface-matrix-output", json.dumps(rejected))
    _click_workbench_evidence_control(page, "#workbench-validate-interface-matrix-btn")
    failed_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert failed_report["status"] == "fail"
    assert failed_report["truth_effect_violation_count"] >= 1
    assert review.get_attribute("data-review-state") == "fail"
    reject_review = review.locator('[data-interface-matrix-review-owner-id="logic1"]')
    assert reject_review.get_attribute("data-row-status") == "reject"
    assert reject_review.get_attribute("data-row-action") == "none"
    _click_workbench_evidence_control(page, "#workbench-apply-interface-matrix-btn")
    assert "Matrix validation failed" in page.locator("#workbench-interface-matrix-status").inner_text()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    after_reject = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in after_reject["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"


def test_workbench_operation_catalog_adds_typed_sandbox_node(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="between"]')
    assert page.locator("#workbench-op-catalog-status").inner_text() == "BTW · 数值"
    page.click('[data-editor-tool="node"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    node = next(item for item in draft["nodes"] if item["id"] == "draft_node_1")
    typed_ports = {port["id"]: port for port in draft["typed_ports"]}
    assert errors == [], f"page JS errors: {errors}"
    assert node["op"] == "between"
    assert node["op_catalog_entry"] == "between"
    assert node["op_catalog_version"] == "editable-control-ops.v1"
    assert node["sourceRef"].startswith("ui_draft.op_catalog.between.")
    assert node["port_contract"]["value_type"] == "number"
    assert node["port_contract"]["required"] is True
    assert typed_ports["draft_node_1:in"]["value_type"] == "number"
    assert typed_ports["draft_node_1:out"]["signal_id"] == "draft_node_1_between_output"
    assert draft["operation_catalog"]["version"] == "editable-control-ops.v1"
    assert draft["operation_catalog"]["selected_op"] == "between"
    assert draft["operation_catalog"]["truth_effect"] == "none"
    assert set(draft["operation_catalog"]["approved_ops"]) == {
        "input",
        "output",
        "and",
        "or",
        "compare",
        "between",
        "delay",
        "latch",
    }

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["operation_catalog"]["selected_op"] == "between"
    assert archive["operation_catalog"]["truth_effect"] == "none"
    assert archive["checksums"]["operation_catalog_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_empty_canvas_palette_round_trips_sandbox_primitives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    empty_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert empty_draft["canvas_authoring_mode"] == "empty_authoring"
    assert empty_draft["nodes"] == []
    assert empty_draft["edges"] == []
    assert empty_draft["editable_graph_document"]["node_count"] == 0
    assert empty_draft["editable_graph_document"]["truth_effect"] == "none"

    page.click('[data-op-catalog-op="input"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="output"]')
    page.click('[data-editor-tool="node"]')
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    node_ops = {node["id"]: node["op"] for node in draft["nodes"]}

    assert draft["canvas_authoring_mode"] == "empty_authoring"
    assert node_ops == {
        "draft_node_1": "input",
        "draft_node_2": "compare",
        "draft_node_3": "output",
    }
    assert all(node_id not in node_ops for node_id in ["logic1", "logic2", "logic3", "logic4"])
    assert draft["workspace_document"]["truth_effect"] == "none"
    assert draft["workspace_document"]["action_count"] >= 4
    assert draft["editable_graph_document"]["version"] == "workbench-editable-graph-document.v2"
    assert draft["editable_graph_document"]["node_count"] == 3
    assert draft["editable_graph_document"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.evaluate(
        """
        (draftJson) => {
          const buffer = document.getElementById('workbench-draft-json-buffer');
          buffer.value = draftJson;
          buffer.dispatchEvent(new Event('input', { bubbles: true }));
        }
        """,
        draft_json,
    )
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_ops = {node["id"]: node["op"] for node in imported["nodes"]}
    assert imported["canvas_authoring_mode"] == "empty_authoring"
    assert imported_ops == node_ops
    assert imported["editable_graph_document"]["node_count"] == 3

    _open_workbench_inspector_mode(page, "run")
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output
            && output.value.includes('well-harness-workbench-sandbox-test-run-report')
            && output.value.includes('sandbox_runner_trace_kernel');
        }
        """
    )
    run_report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    assert run_report["truth_effect"] == "none"
    assert run_report["candidate_state"] == "sandbox_candidate"
    assert run_report["sandbox_runner_trace_kernel"]["truth_effect"] == "none"

    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["canvas_authoring_mode"] == "empty_authoring"
    assert archive["editable_graph_document"]["node_count"] == 3
    assert archive["editable_graph_document"]["version"] == "workbench-editable-graph-document.v2"
    assert archive["editable_graph_document"]["truth_effect"] == "none"
    assert archive["truth_effect"] == "none"
    assert archive["candidate_state"] == "sandbox_candidate"
    assert archive["certification_claim"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False

    _set_archive_buffer_value(page, json.dumps(archive))
    _click_workbench_handoff_control(page, "#workbench-restore-review-archive-btn")
    validation = json.loads(page.locator("#workbench-review-archive-restore-output").input_value())
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    restored = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    restored_ops = {node["id"]: node["op"] for node in restored["nodes"]}
    assert validation["status"] == "pass", json.dumps(validation.get("findings"), sort_keys=True)
    assert restored["canvas_authoring_mode"] == "empty_authoring"
    assert restored_ops == node_ops
    assert all(node_id not in restored_ops for node_id in ["logic1", "logic2", "logic3", "logic4"])


def test_workbench_goal_canvas_panel_geometry_evidence(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    evidence: dict[str, Any] = {}

    for label, viewport in {
        "desktop": {"width": 1440, "height": 980},
        "narrow": {"width": 390, "height": 920},
    }.items():
        page.set_viewport_size(viewport)
        _goto_shell_workbench(page, f"{demo_server}/workbench")
        page.click("#workbench-start-empty-draft-btn")
        page.click('[data-op-catalog-op="input"]')
        page.click('[data-editor-tool="node"]')
        page.click('[data-op-catalog-op="compare"]')
        page.click('[data-editor-tool="node"]')
        page.click('[data-op-catalog-op="output"]')
        page.click('[data-editor-tool="node"]')
        page.screenshot(path=str(_ARTIFACT_DIR / f"{label}-goal-canvas-panel.png"), full_page=False)
        evidence[label] = page.evaluate(
            """
            () => {
              const box = (selector) => {
                const node = document.querySelector(selector);
                if (!node) return null;
                const rect = node.getBoundingClientRect();
                return {
                  left: rect.left,
                  top: rect.top,
                  right: rect.right,
                  bottom: rect.bottom,
                  width: rect.width,
                  height: rect.height,
                };
              };
              return {
                viewport: {
                  width: window.innerWidth,
                  height: window.innerHeight,
                  scrollHeight: document.documentElement.scrollHeight,
                  scrollWidth: document.documentElement.scrollWidth,
                  bodyScrollHeight: document.body.scrollHeight,
                  bodyScrollWidth: document.body.scrollWidth,
                    },
                    panel: box('#workbench-goal-canvas-panel'),
                    reopenGuide: box('#workbench-open-onboarding-guide-btn'),
                    toolbar: box('#workbench-editor-toolbar'),
                canvas: box('#workbench-editable-canvas'),
                inspector: box('#workbench-evidence-inspector'),
                inspectorScroll: {
                  clientHeight: document.querySelector('#workbench-evidence-inspector')?.clientHeight || 0,
                  scrollHeight: document.querySelector('#workbench-evidence-inspector')?.scrollHeight || 0,
                },
                main: box('.workbench-editable-main'),
                nodeBoxes: Array.from(document.querySelectorAll('.workbench-editable-node')).map((node) => {
                  const rect = node.getBoundingClientRect();
                  return {
                    width: rect.width,
                    height: rect.height,
                    left: rect.left,
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                  };
                }),
                nodeCount: document.querySelectorAll('.workbench-editable-node').length,
                portHandleCount: document.querySelectorAll('.workbench-port-handle').length,
                archiveVisible: Boolean(document.querySelector('#workbench-evidence-archive')),
                debugVisible: Boolean(document.querySelector('#workbench-selected-debug-timeline')),
              };
            }
            """
        )

    (_ARTIFACT_DIR / "goal-canvas-panel-geometry.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    assert errors == [], f"page JS errors: {errors}"
    for label, data in evidence.items():
        assert data["panel"] is not None, label
        assert data["panel"]["width"] == 0, label
        assert data["reopenGuide"]["width"] > 0, label
        assert data["canvas"]["width"] > 0 and data["canvas"]["height"] > 0, label
        assert data["main"]["height"] <= data["viewport"]["height"] - 120, label
        assert data["viewport"]["bodyScrollHeight"] <= data["viewport"]["height"] + 120, label
        assert data["viewport"]["bodyScrollWidth"] <= data["viewport"]["width"] + 2, label
        assert data["toolbar"]["left"] >= data["canvas"]["left"], label
        assert data["toolbar"]["right"] <= data["canvas"]["left"] + 72, label
        assert data["inspector"]["right"] <= data["viewport"]["width"] + 2, label
        assert data["inspectorScroll"]["scrollHeight"] >= data["inspectorScroll"]["clientHeight"], label
        assert all(node["width"] <= 150 for node in data["nodeBoxes"]), label
        assert all(node["height"] <= 90 for node in data["nodeBoxes"]), label
        assert all(
            node["left"] >= data["canvas"]["left"] and node["right"] <= data["canvas"]["right"]
            for node in data["nodeBoxes"]
        ), label
        assert all(
            node["top"] >= data["canvas"]["top"] and node["bottom"] <= data["canvas"]["bottom"]
            for node in data["nodeBoxes"]
        ), label
        if label == "desktop":
            assert data["canvas"]["width"] >= data["viewport"]["width"] * 0.78, label
            assert data["inspector"]["top"] >= data["canvas"]["top"], label
            assert data["inspector"]["bottom"] <= data["canvas"]["bottom"] + 2, label
            assert 0 <= data["inspector"]["width"] <= 4, label
        else:
            assert data["canvas"]["width"] >= data["viewport"]["width"] * 0.79, label
            assert data["inspector"]["top"] >= data["canvas"]["top"], label
            assert data["inspector"]["bottom"] <= data["canvas"]["bottom"] + 2, label
            assert 0 <= data["inspector"]["width"] <= 4, label
        assert data["nodeCount"] == 3, label
        assert data["portHandleCount"] >= 6, label
        assert data["archiveVisible"] is True, label
        assert data["debugVisible"] is True, label


def test_workbench_inspector_modes_reduce_default_density(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1440, "height": 980})
    page.goto(f"{demo_server}/workbench", wait_until="domcontentloaded")
    page.evaluate("localStorage.clear()")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    def inspector_state() -> dict[str, Any]:
        return page.evaluate(
            """
            () => {
              const isVisible = (node) => {
                if (!node) return false;
                const style = window.getComputedStyle(node);
                return style.display !== 'none'
                  && style.visibility !== 'hidden'
                  && node.getClientRects().length > 0;
              };
              const box = (selector) => {
                const node = document.querySelector(selector);
                if (!node) return null;
                const rect = node.getBoundingClientRect();
                return {
                  left: rect.left,
                  top: rect.top,
                  right: rect.right,
                  bottom: rect.bottom,
                  width: rect.width,
                  height: rect.height,
                };
              };
              return {
                activeMode: document.querySelector('#workbench-evidence-inspector')
                  ?.getAttribute('data-inspector-mode-active'),
                selectedTabs: Array.from(document.querySelectorAll('[data-inspector-mode]'))
                  .filter((button) => button.getAttribute('aria-selected') === 'true')
                  .map((button) => button.getAttribute('data-inspector-mode')),
                tabLabels: Array.from(document.querySelectorAll('[data-inspector-mode]'))
                  .map((button) => button.textContent.trim()),
                visiblePanels: Array.from(document.querySelectorAll('[data-inspector-panel]'))
                  .filter((panel) => isVisible(panel))
                  .map((panel) => panel.getAttribute('data-inspector-panel')),
                nodeVisible: isVisible(document.querySelector('#workbench-inspector-node-panel')),
                runVisible: isVisible(document.querySelector('#workbench-sandbox-test-bench')),
                evidenceVisible: isVisible(document.querySelector('#workbench-hardware-palette')),
                handoffVisible: isVisible(document.querySelector('.workbench-draft-json-exchange')),
                canvas: box('#workbench-editable-canvas'),
                inspector: box('#workbench-evidence-inspector'),
                main: box('.workbench-editable-main'),
                viewport: { width: window.innerWidth, height: window.innerHeight },
              };
            }
            """
        )

    state = inspector_state()
    assert errors == [], f"page JS errors: {errors}"
    assert state["activeMode"] == "node"
    assert state["selectedTabs"] == ["node"]
    assert state["tabLabels"] == ["节点详情", "运行结果", "硬件证据", "交付包"]
    assert state["visiblePanels"] == []
    assert state["nodeVisible"] is False
    assert state["runVisible"] is False
    assert state["evidenceVisible"] is False
    assert state["handoffVisible"] is False
    assert state["inspector"]["width"] <= 4

    page.click('[data-editable-node-id="logic1"]')
    state = inspector_state()
    assert state["visiblePanels"] == ["node"]
    assert state["nodeVisible"] is True

    _open_workbench_inspector_mode(page, "evidence")
    state = inspector_state()
    assert state["activeMode"] == "evidence"
    assert state["selectedTabs"] == ["evidence"]
    assert state["visiblePanels"] == ["evidence"]
    assert state["evidenceVisible"] is True

    _open_workbench_inspector_mode(page, "run")
    state = inspector_state()
    assert state["activeMode"] == "run"
    assert state["visiblePanels"] == ["run"]
    assert state["runVisible"] is True

    _open_workbench_inspector_mode(page, "handoff")
    state = inspector_state()
    assert state["activeMode"] == "handoff"
    assert state["visiblePanels"] == ["handoff"]
    assert state["handoffVisible"] is True

    page.set_viewport_size({"width": 390, "height": 920})
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#workbench-identity", state="attached")
    page.click('[data-editable-node-id="logic1"]')
    _open_workbench_inspector_mode(page, "node")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-evidence-inspector')
          ?.getBoundingClientRect().width >= 290
        """
    )
    narrow = inspector_state()
    assert narrow["activeMode"] == "node"
    assert narrow["inspector"]["width"] >= 290
    assert narrow["inspector"]["top"] >= narrow["canvas"]["top"]
    assert narrow["inspector"]["bottom"] <= narrow["canvas"]["bottom"] + 2
    assert narrow["main"]["height"] <= narrow["viewport"]["height"] - 120


def test_workbench_component_library_inserts_reusable_sandbox_template(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    assert "2ST" in page.locator("#workbench-component-library-status").inner_text()
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    created_nodes = [node for node in draft["nodes"] if node["id"].startswith("draft_node_")]
    created_edges = [
        edge for edge in draft["edges"]
        if edge["id"].startswith("edge_component_two_stage_interlock")
    ]
    assert errors == [], f"page JS errors: {errors}"
    assert [node["id"] for node in created_nodes] == ["draft_node_1", "draft_node_2"]
    assert len(created_edges) == 1
    assert draft["component_library"]["version"] == "editable-component-library.v1"
    assert draft["component_library"]["last_template_id"] == "two_stage_interlock"
    assert draft["component_library"]["truth_effect"] == "none"
    assert {
        node["component_template"]["template_id"] for node in created_nodes
    } == {"two_stage_interlock"}
    assert all(
        node["component_template"]["candidate_state"] == "sandbox_candidate"
        for node in created_nodes
    )
    assert created_edges[0]["component_template"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_nodes = [node for node in imported["nodes"] if node["id"].startswith("draft_node_")]
    assert [node["component_template"]["template_id"] for node in imported_nodes] == [
        "two_stage_interlock",
        "two_stage_interlock",
    ]

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["component_library"]["last_template_id"] == "two_stage_interlock"
    assert archive["component_library"]["truth_effect"] == "none"
    assert archive["checksums"]["component_library_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_subsystem_group_rename_ungroup_round_trips_sandbox_metadata(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    before_group = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    before_edge_ids = [edge["id"] for edge in before_group["edges"]]
    before_port_ids = [port["id"] for port in before_group["typed_ports"]]

    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Deploy interlock")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    grouped = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    subsystem = grouped["subsystem_groups"][0]
    draft_nodes = [node for node in grouped["nodes"] if node["id"].startswith("draft_node_")]

    assert errors == [], f"page JS errors: {errors}"
    assert subsystem["name"] == "Deploy interlock"
    assert subsystem["node_ids"] == ["draft_node_1", "draft_node_2"]
    assert subsystem["truth_effect"] == "none"
    assert [node["subsystem_group"]["group_id"] for node in draft_nodes] == [subsystem["id"], subsystem["id"]]
    assert [edge["id"] for edge in grouped["edges"]] == before_edge_ids
    assert [port["id"] for port in grouped["typed_ports"]] == before_port_ids
    assert page.locator(".workbench-subsystem-overlay").count() == 1
    overlay = page.locator(".workbench-subsystem-overlay")
    assert overlay.get_attribute("data-subsystem-node-count") == "2"
    assert overlay.get_attribute("data-truth-effect") == "none"
    assert overlay.get_attribute("data-subsystem-active") == "true"
    assert overlay.get_attribute("data-subsystem-workflow-state") == "grouped"
    assert overlay.get_attribute("data-subsystem-name") == "Deploy interlock"
    assert page.locator("#workbench-subsystem-editor").get_attribute("data-subsystem-workflow-state") == "grouped"
    assert page.locator("#workbench-subsystem-editor").get_attribute("data-subsystem-selected-count") == "2"
    assert page.locator("#workbench-subsystem-selection-count").inner_text() == "已选 2"
    assert page.locator("#workbench-subsystem-active-name").inner_text() == "Deploy interlock"
    assert page.locator("#workbench-subsystem-workflow-state").inner_text() == "已封装"
    assert "Deploy interlock" in overlay.inner_text()
    assert "2 draft node(s)" in overlay.inner_text()
    assert "truth effect none" in overlay.inner_text()
    assert "Sandbox metadata. Truth effect none." in (overlay.get_attribute("title") or "")
    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-subsystem-active") == "true"
    assert page.locator('[data-editable-node-id="draft_node_2"]').get_attribute("data-subsystem-active") == "true"
    status = page.locator("#workbench-subsystem-status")
    assert "Created Deploy interlock with 2 draft node(s)" in status.inner_text()
    assert status.get_attribute("data-status-tone") == "success"
    page.locator('[data-editable-node-id="logic1"]').click()
    assert overlay.get_attribute("data-subsystem-active") == "false"
    page.locator('[data-editable-node-id="draft_node_1"]').hover()
    assert overlay.get_attribute("data-subsystem-active") == "true"
    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-subsystem-active") == "true"
    page.locator('[data-editable-node-id="logic1"]').hover()
    assert overlay.get_attribute("data-subsystem-active") == "false"
    page.locator('[data-editable-node-id="draft_node_1"]').click()

    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Deploy interlock v2")
    _click_workbench_node_control(page, "#workbench-rename-subsystem-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    renamed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert renamed["subsystem_groups"][0]["name"] == "Deploy interlock v2"
    assert "Deploy interlock v2" in page.locator(".workbench-subsystem-overlay").inner_text()
    assert page.locator(".workbench-subsystem-overlay").get_attribute("data-subsystem-active") == "true"
    assert page.locator(".workbench-subsystem-overlay").get_attribute("data-subsystem-workflow-state") == "renamed"
    assert page.locator(".workbench-subsystem-overlay").get_attribute("data-subsystem-name") == "Deploy interlock v2"
    assert page.locator("#workbench-subsystem-editor").get_attribute("data-subsystem-workflow-state") == "renamed"
    assert page.locator("#workbench-subsystem-active-name").inner_text() == "Deploy interlock v2"
    assert page.locator("#workbench-subsystem-workflow-state").inner_text() == "已重命名"
    assert "Renamed subsystem" in status.inner_text()
    assert "Deploy interlock v2" in status.inner_text()
    assert status.get_attribute("data-status-tone") == "success"
    assert all(
        node["subsystem_group"]["name"] == "Deploy interlock v2"
        for node in renamed["nodes"]
        if node["id"].startswith("draft_node_")
    )

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["subsystem_groups"][0]["name"] == "Deploy interlock v2"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["subsystem_groups"][0]["truth_effect"] == "none"
    assert archive["checksums"]["subsystem_groups_checksum"]

    _click_workbench_node_control(page, "#workbench-ungroup-subsystem-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    ungrouped = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert ungrouped["subsystem_groups"] == []
    assert [edge["id"] for edge in ungrouped["edges"]] == before_edge_ids
    assert [port["id"] for port in ungrouped["typed_ports"]] == before_port_ids
    assert all("subsystem_group" not in node for node in ungrouped["nodes"] if node["id"].startswith("draft_node_"))
    assert page.locator("#workbench-subsystem-editor").get_attribute("data-subsystem-workflow-state") == "ungrouped"
    assert page.locator("#workbench-subsystem-selection-count").inner_text() == "已选 2"
    assert page.locator("#workbench-subsystem-active-name").inner_text() == "无"
    assert page.locator("#workbench-subsystem-workflow-state").inner_text() == "已解除"
    assert "Ungrouped Deploy interlock v2" in status.inner_text()
    assert status.get_attribute("data-status-tone") == "success"

    page.keyboard.press("Control+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    undo = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert undo["subsystem_groups"][0]["name"] == "Deploy interlock v2"

    page.keyboard.press("Control+Shift+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    redo = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert redo["subsystem_groups"] == []
    assert redo["truth_level_impact"] == "none"


def test_workbench_captures_and_reinserts_subsystem_template(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Reusable deploy cell")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")
    _click_with_workbench_inspector_closed(page, "#workbench-capture-subsystem-template-btn")
    assert "captured" in page.locator("#workbench-component-library-status").inner_text().lower()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    captured = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    library = captured["component_library"]
    captured_templates = library["captured_templates"]
    template_id = captured_templates[0]["id"]

    assert errors == [], f"page JS errors: {errors}"
    assert library["captured_template_count"] == 1
    assert library["truth_effect"] == "none"
    assert captured_templates[0]["candidate_state"] == "sandbox_candidate"
    assert captured_templates[0]["truth_effect"] == "none"
    assert captured_templates[0]["subsystem"]["name"] == "Reusable deploy cell"
    assert captured_templates[0]["subsystem"]["node_ids"] == ["draft_node_1", "draft_node_2"]
    assert [node["original_node_id"] for node in captured_templates[0]["nodes"]] == [
        "draft_node_1",
        "draft_node_2",
    ]
    assert captured_templates[0]["edges"][0]["source_index"] == 0
    assert captured_templates[0]["edges"][0]["target_index"] == 1

    _click_with_workbench_inspector_closed(page, "#workbench-insert-captured-template-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    inserted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft_nodes = [node for node in inserted["nodes"] if node["id"].startswith("draft_node_")]
    inserted_nodes = [node for node in draft_nodes if node["id"] in {"draft_node_3", "draft_node_4"}]
    inserted_edges = [
        edge for edge in inserted["edges"]
        if edge.get("component_template", {}).get("template_id") == template_id
    ]

    assert [node["id"] for node in inserted_nodes] == ["draft_node_3", "draft_node_4"]
    assert {node["component_template"]["template_id"] for node in inserted_nodes} == {template_id}
    assert len(inserted_edges) == 1
    assert inserted_edges[0]["source"] == "draft_node_3"
    assert inserted_edges[0]["target"] == "draft_node_4"
    assert inserted["component_library"]["captured_template_count"] == 1
    assert inserted["component_library"]["last_template_id"] == template_id
    assert inserted["component_library"]["captured_templates"][0]["truth_effect"] == "none"
    assert any(
        group["name"] == "Reusable deploy cell copy"
        and group["node_ids"] == ["draft_node_3", "draft_node_4"]
        and group["truth_effect"] == "none"
        for group in inserted["subsystem_groups"]
    )

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["component_library"]["captured_templates"][0]["id"] == template_id
    assert imported["component_library"]["captured_templates"][0]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["component_library"]["captured_template_count"] == 1
    assert archive["component_library"]["captured_templates"][0]["truth_effect"] == "none"
    assert archive["checksums"]["component_library_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_subsystem_interface_contract_round_trips_and_templates(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Ported deploy cell")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")

    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "input")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy request")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_request_cmd")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-value-type", "boolean")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-evidence-status", "ui_draft")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")

    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "output")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy allowed")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_allowed_status")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-value-type", "boolean")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-evidence-status", "evidence_gap")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    contracted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    group = contracted["subsystem_groups"][0]
    contracts = contracted["subsystem_interface_contracts"]

    assert errors == [], f"page JS errors: {errors}"
    assert group["interface_contracts"][0]["direction"] == "input"
    assert group["interface_contracts"][0]["signal_id"] == "deploy_request_cmd"
    assert group["interface_contracts"][0]["truth_effect"] == "none"
    assert group["interface_contracts"][1]["direction"] == "output"
    assert group["interface_contracts"][1]["evidence_status"] == "evidence_gap"
    assert contracts["port_count"] == 2
    assert contracts["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["subsystem_groups"][0]["interface_contracts"][0]["label"] == "Deploy request"

    _click_with_workbench_inspector_closed(page, "#workbench-capture-subsystem-template-btn")
    _click_with_workbench_inspector_closed(page, "#workbench-insert-captured-template-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    inserted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    copied_group = next(
        group for group in inserted["subsystem_groups"]
        if group["name"] == "Ported deploy cell copy"
    )
    copied_ports = copied_group["interface_contracts"]

    assert len(copied_ports) == 2
    assert copied_ports[0]["group_id"] == copied_group["id"]
    assert copied_ports[0]["signal_id"] == "deploy_request_cmd"
    assert copied_ports[0]["truth_effect"] == "none"
    assert copied_ports[0]["id"].startswith(f"{copied_group['id']}:input:")
    assert copied_ports[1]["id"].startswith(f"{copied_group['id']}:output:")

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["subsystem_interface_contracts"]["port_count"] == 4
    assert archive["subsystem_interface_contracts"]["truth_effect"] == "none"
    assert archive["checksums"]["subsystem_interface_contracts_checksum"]
    assert archive["component_library"]["captured_templates"][0]["subsystem"]["interface_contracts"][0]["truth_effect"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_workspace_document_round_trips_with_archive_checksum(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Documented deploy cell")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "input")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy request")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_request_cmd")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    exported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    workspace_document = exported["workspace_document"]

    assert errors == [], f"page JS errors: {errors}"
    assert workspace_document["kind"] == "well-harness-workbench-workspace-document"
    assert workspace_document["version"] == "workbench-workspace-document.v1"
    assert workspace_document["candidate_state"] == "sandbox_candidate"
    assert workspace_document["truth_effect"] == "none"
    assert workspace_document["revision_id"].startswith("ui_draft_")
    assert workspace_document["action_count"] >= 3
    assert workspace_document["undo_depth"] >= 3
    assert workspace_document["redo_depth"] == 0
    assert (
        page.locator("#workbench-workspace-document-revision")
        .get_attribute("data-workspace-revision-id")
        == workspace_document["revision_id"]
    )

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["workspace_document"]["document_id"] == workspace_document["document_id"]
    assert imported["workspace_document"]["action_count"] >= workspace_document["action_count"]

    page.click('[data-editor-tool="undo"]')
    page.click('[data-editor-tool="redo"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    revised = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert revised["workspace_document"]["revision_id"].startswith("ui_draft_")
    assert revised["workspace_document"]["undo_depth"] >= 1

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["workspace_document"]["truth_effect"] == "none"
    assert archive["checksums"]["workspace_document_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_editable_graph_document_round_trips_export_import_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    _fill_workbench_node_control(page, "#workbench-subsystem-name", "Canonical graph cell")
    _click_workbench_node_control(page, "#workbench-create-subsystem-btn")
    _select_workbench_node_control(page, "#workbench-subsystem-interface-direction", "output")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-label", "Deploy command")
    _fill_workbench_node_control(page, "#workbench-subsystem-interface-signal-id", "deploy_cmd")
    _click_workbench_node_control(page, "#workbench-add-subsystem-interface-port-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    exported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    graph = exported["editable_graph_document"]

    assert errors == [], f"page JS errors: {errors}"
    assert graph["kind"] == "well-harness-workbench-editable-graph-document"
    assert graph["version"] == "workbench-editable-graph-document.v2"
    assert "workbench-editable-graph-document.v1" in graph["accepted_import_versions"]
    assert graph["canonical_model"]["schema_version"] == "workbench-editable-graph-canonical-model.v1"
    assert graph["canonical_model"]["nodes"] == exported["nodes"]
    assert graph["canonical_model"]["edges"] == exported["edges"]
    assert graph["canonical_model"]["ports"] == exported["ports"]
    assert graph["canonical_model"]["typed_ports"] == exported["typed_ports"]
    assert graph["dom_adapter"]["kind"] == "workbench-editable-graph-dom-adapter-boundary"
    assert graph["dom_adapter"]["source_of_truth"] == "editable_graph_document.canonical_model"
    assert graph["dom_adapter"]["top_level_compatibility"] is True
    assert graph["candidate_state"] == "sandbox_candidate"
    assert graph["truth_effect"] == "none"
    assert graph["workspace_revision_id"] == exported["workspace_document"]["revision_id"]
    assert graph["node_count"] == len(exported["nodes"])
    assert graph["draft_node_count"] == len([node for node in exported["nodes"] if node.get("draftNode")])
    assert graph["edge_count"] == len(exported["edges"])
    assert graph["port_count"] == len(exported["ports"])
    assert graph["typed_port_count"] == len(exported["typed_ports"])
    assert graph["subsystem_group_count"] == len(exported["subsystem_groups"])
    assert graph["component_template_count"] == len(exported["component_library"]["captured_templates"])
    assert graph["selected_state"]["node_ids"] == sorted(exported["selected_node_ids"])
    assert graph["position_digest"].startswith("ui_draft_")
    assert graph["node_digest"].startswith("ui_draft_")
    assert graph["edge_digest"].startswith("ui_draft_")
    assert graph["port_digest"].startswith("ui_draft_")

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_graph = imported["editable_graph_document"]
    assert imported_graph["truth_effect"] == "none"
    assert imported_graph["version"] == "workbench-editable-graph-document.v2"
    assert imported_graph["node_count"] == graph["node_count"]
    assert imported_graph["edge_count"] == graph["edge_count"]
    assert imported_graph["port_count"] == graph["port_count"]
    assert imported_graph["subsystem_group_count"] == graph["subsystem_group_count"]
    for digest_field in [
        "position_digest",
        "node_digest",
        "edge_digest",
        "port_digest",
        "subsystem_digest",
        "component_library_digest",
    ]:
        assert imported_graph[digest_field] == graph[digest_field]

    legacy_v1 = json.loads(json.dumps(imported))
    legacy_v1["editable_graph_document"]["version"] = "workbench-editable-graph-document.v1"
    legacy_v1["editable_graph_document"].pop("canonical_model")
    legacy_v1["editable_graph_document"].pop("dom_adapter")
    legacy_v1["editable_graph_document"].pop("accepted_import_versions")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(legacy_v1))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    migrated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    migrated_graph = migrated["editable_graph_document"]
    assert migrated_graph["version"] == "workbench-editable-graph-document.v2"
    assert migrated_graph["node_count"] == graph["node_count"]
    assert migrated_graph["edge_count"] == graph["edge_count"]
    assert migrated_graph["canonical_model"]["nodes"] == imported_graph["canonical_model"]["nodes"]

    canonical_only = dict(imported)
    canonical_only.pop("nodes")
    canonical_only.pop("edges")
    canonical_only.pop("ports")
    canonical_only.pop("typed_ports")
    canonical_only.pop("subsystem_groups")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(canonical_only))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    rebuilt = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    rebuilt_graph = rebuilt["editable_graph_document"]
    assert rebuilt_graph["version"] == "workbench-editable-graph-document.v2"
    assert rebuilt_graph["node_count"] == graph["node_count"]
    assert rebuilt_graph["edge_count"] == graph["edge_count"]
    assert rebuilt_graph["canonical_model"]["nodes"] == imported_graph["canonical_model"]["nodes"]
    assert rebuilt_graph["dom_adapter"]["top_level_compatibility"] is True

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    first_archive_checksum = archive["checksums"]["editable_graph_document_checksum"]
    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    second_archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["editable_graph_document"]["truth_effect"] == "none"
    assert archive["editable_graph_document"]["node_count"] == imported_graph["node_count"]
    assert first_archive_checksum
    assert second_archive["checksums"]["editable_graph_document_checksum"] == first_archive_checksum
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_captured_template_remaps_overlapping_ids_and_preserves_rules(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    for _ in range(10):
        page.click('[data-component-template-id="single_and_gate"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft["component_library"]["last_template_id"] = "captured_subsystem_template_overlap"
    draft["component_library"]["captured_templates"] = [
        {
            "id": "captured_subsystem_template_overlap",
            "kind": "well-harness-workbench-captured-subsystem-template",
            "version": 1,
            "template_version": "editable-captured-subsystem-template.v1",
            "label": "Overlap capture",
            "short_label": "CAP",
            "checksum": "stale-imported-checksum",
            "subsystem": {
                "id": "subsystem_overlap_capture",
                "name": "Overlap capture",
                "node_ids": ["draft_node_1", "draft_node_10"],
                "candidate_state": "sandbox_candidate",
                "source_ref": "ui_draft.subsystem_group.overlap",
                "truth_effect": "none",
            },
            "nodes": [
                {
                    "original_node_id": "draft_node_1",
                    "label": "Captured source one",
                    "op": "and",
                    "rule_count": "1",
                    "hardware_binding": {
                        "hardware_id": "TR-LRU-001",
                        "port_local": "draft_node_1:A1",
                        "port_peer": "draft_node_10:B1",
                        "evidence_status": "ui_draft",
                    },
                    "port_contract": {
                        "input_signal_id": "draft_node_1_input_signal",
                        "output_signal_id": "draft_node_1_output_signal",
                        "value_type": "boolean",
                        "required": False,
                        "truth_effect": "none",
                    },
                    "rules": [
                        {
                            "name": "draft_node_1_rule",
                            "source_signal_id": "draft_node_1_signal",
                            "comparison": "==",
                            "threshold_value": True,
                        }
                    ],
                    "candidate_state": "sandbox_candidate",
                    "truth_effect": "none",
                },
                {
                    "original_node_id": "draft_node_10",
                    "label": "Captured source ten",
                    "op": "compare",
                    "rule_count": "2",
                    "hardware_binding": {
                        "hardware_id": "TR-LRU-010",
                        "port_local": "draft_node_10:A1",
                        "port_peer": "draft_node_1:B1",
                        "evidence_status": "ui_draft",
                    },
                    "port_contract": {
                        "input_signal_id": "draft_node_10_input_signal",
                        "output_signal_id": "draft_node_10_output_signal",
                        "value_type": "number",
                        "required": True,
                        "truth_effect": "none",
                    },
                    "rules": [
                        {
                            "name": "draft_node_10_lower",
                            "source_signal_id": "draft_node_10_lower_signal",
                            "comparison": ">=",
                            "threshold_value": -32,
                        },
                        {
                            "name": "draft_node_10_upper",
                            "source_signal_id": "draft_node_10_upper_signal",
                            "comparison": "<=",
                            "threshold_value": 0,
                        },
                    ],
                    "candidate_state": "sandbox_candidate",
                    "truth_effect": "none",
                },
            ],
            "edges": [
                {
                    "original_edge_id": "edge_overlap",
                    "source_index": 0,
                    "target_index": 1,
                    "source_port_id": "draft_node_1:out",
                    "target_port_id": "draft_node_10:in",
                    "signal_id": "draft_node_1_to_draft_node_10",
                    "value_type": "boolean",
                    "required": True,
                    "candidate_state": "sandbox_candidate",
                    "truth_effect": "none",
                }
            ],
            "candidate_state": "sandbox_candidate",
            "certification_claim": "none",
            "truth_effect": "none",
        }
    ]

    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_with_workbench_inspector_closed(page, "#workbench-insert-captured-template-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    inserted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    node_12 = next(node for node in inserted["nodes"] if node["id"] == "draft_node_12")
    overlap_edge = next(
        edge for edge in inserted["edges"]
        if (edge.get("component_template") or {}).get("template_id") == "captured_subsystem_template_overlap"
    )
    captured_template = inserted["component_library"]["captured_templates"][0]

    assert errors == [], f"page JS errors: {errors}"
    assert captured_template["checksum"] != "stale-imported-checksum"
    assert node_12["port_contract"]["input_signal_id"] == "draft_node_12_input_signal"
    assert node_12["port_contract"]["output_signal_id"] == "draft_node_12_output_signal"
    assert node_12["hardware_binding"]["port_local"] == "draft_node_12:A1"
    assert node_12["hardware_binding"]["port_peer"] == "draft_node_11:B1"
    assert [rule["source_signal_id"] for rule in node_12["rules"]] == [
        "draft_node_12_lower_signal",
        "draft_node_12_upper_signal",
    ]
    assert overlap_edge["target_port_id"] == "draft_node_12:in"
    assert overlap_edge["signal_id"] == "draft_node_11_to_draft_node_12"
    assert "draft_node_110" not in json.dumps(inserted)


def test_workbench_rule_parameter_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="between"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_evidence_control(page, "#workbench-rule-name", "draft_tra_window")
    _fill_workbench_evidence_control(page, "#workbench-rule-source-signal", "tra_deg")
    _select_workbench_evidence_control(page, "#workbench-rule-comparison", "between_lower_inclusive")
    _fill_workbench_evidence_control(page, "#workbench-rule-threshold", "[-32,0]")
    page.click("#workbench-apply-rule-parameter-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())

    node = next(item for item in draft["nodes"] if item["id"] == "draft_node_1")
    assert errors == [], f"page JS errors: {errors}"
    assert node["rules"] == [
        {
            "name": "draft_tra_window",
            "source_signal_id": "tra_deg",
            "comparison": "between_lower_inclusive",
            "threshold_value": [-32, 0],
        }
    ]
    assert draft["rule_parameter_summary"]["total_rules"] == 1
    assert draft["rule_parameter_summary"]["truth_effect"] == "none"

    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    _fill_workbench_handoff_control(page, "#workbench-draft-json-buffer", json.dumps(draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_node = next(item for item in round_trip["nodes"] if item["id"] == "draft_node_1")
    assert round_trip_node["rules"][0]["threshold_value"] == [-32, 0]
    assert round_trip["rule_parameter_summary"]["total_rules"] == 1

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["model_json"]["nodes"][-1]["rules"][0]["comparison"] == "between_lower_inclusive"
    assert archive["rule_parameter_summary"]["total_rules"] == 1
    assert archive["rule_parameter_summary"]["truth_effect"] == "none"
    assert archive["checksums"]["rule_parameter_summary_checksum"]
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"


def test_workbench_named_draft_snapshot_save_restore_export_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _select_workbench_run_control(page, "#workbench-sandbox-scenario-select", "sw1_stuck_at_touchdown")
    page.fill("#workbench-custom-snapshot-json", '{"tra_deg": -12}')
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_handoff_control(page, "#workbench-draft-snapshot-name", "compare-candidate-a")
    _click_workbench_handoff_control(page, "#workbench-save-draft-snapshot-btn")
    assert "compare-candidate-a" in page.locator("#workbench-draft-snapshot-select").inner_text()

    page.click('[data-editor-tool="node"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    mutated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert len([node for node in mutated["nodes"] if node["id"].startswith("draft_node_")]) == 2

    _click_workbench_handoff_control(page, "#workbench-restore-draft-snapshot-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    restored = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft_nodes = [node for node in restored["nodes"] if node["id"].startswith("draft_node_")]
    assert errors == [], f"page JS errors: {errors}"
    assert [node["id"] for node in draft_nodes] == ["draft_node_1"]
    assert restored["selected_scenario_id"] == "sw1_stuck_at_touchdown"
    assert restored["custom_snapshot"] == {"tra_deg": -12}
    assert restored["draft_snapshot_manifest"]["snapshot_count"] == 1
    assert restored["draft_snapshot_manifest"]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["model_json"]["draft_snapshot_manifest"]["snapshot_count"] == 1
    assert archive["draft_snapshot_manifest"]["snapshot_count"] == 1
    assert archive["draft_snapshot_manifest"]["truth_level_impact"] == "none"
    assert archive["checksums"]["draft_snapshot_manifest_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_duplicate_keyboard_shortcuts_edit_sandbox_nodes(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_evidence_control(page, "#workbench-rule-name", "draft_tra_compare")
    _fill_workbench_evidence_control(page, "#workbench-rule-source-signal", "tra_deg")
    _select_workbench_evidence_control(page, "#workbench-rule-comparison", ">=")
    _fill_workbench_evidence_control(page, "#workbench-rule-threshold", "-11.74")
    page.click("#workbench-apply-rule-parameter-btn")
    _click_workbench_evidence_control(page, "#workbench-interface-hardware-id")
    _fill_workbench_evidence_control(page, "#workbench-interface-hardware-id", "TR-LRU-001")
    _fill_workbench_evidence_control(page, "#workbench-interface-cable", "CBL-TR-A")
    _fill_workbench_evidence_control(page, "#workbench-interface-connector", "J1")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-local", "draft_node_1:out")
    _fill_workbench_evidence_control(page, "#workbench-interface-port-peer", "TR-LRU-001:J1")
    _select_workbench_evidence_control(page, "#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    page.locator('[data-editable-node-id="draft_node_1"]').click()
    page.keyboard.press("Control+D")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    duplicated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft_nodes = [node for node in duplicated["nodes"] if node["id"].startswith("draft_node_")]

    assert errors == [], f"page JS errors: {errors}"
    assert [node["id"] for node in draft_nodes] == ["draft_node_1", "draft_node_2"]
    duplicate = draft_nodes[1]
    assert duplicate["sourceRef"].startswith("ui_draft.duplicate.draft_node_1.")
    assert duplicate["port_contract"]["input_port_id"] == "draft_node_2:in"
    assert duplicate["port_contract"]["output_port_id"] == "draft_node_2:out"
    assert duplicate["hardware_binding"]["hardware_id"] == "TR-LRU-001"
    assert duplicate["hardware_binding"]["port_local"] == "draft_node_2:out"
    assert duplicate["rules"][0]["source_signal_id"] == "tra_deg"

    page.keyboard.press("Control+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    undone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in undone["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1"
    ]

    page.keyboard.press("Control+Shift+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    redone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in redone["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1",
        "draft_node_2",
    ]

    page.keyboard.press("Delete")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    deleted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in deleted["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1"
    ]
    assert deleted["truth_level_impact"] == "none"


def test_workbench_multi_select_batch_duplicate_delete_and_undo(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-editor-tool="node"]')
    page.locator('[data-editable-node-id="draft_node_1"]').click(modifiers=["Shift"])
    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-multi-selected") == "true"
    assert page.locator('[data-editable-node-id="draft_node_2"]').get_attribute("data-multi-selected") == "true"

    page.keyboard.press("Control+D")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    duplicated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft_ids = [node["id"] for node in duplicated["nodes"] if node["id"].startswith("draft_node_")]

    assert errors == [], f"page JS errors: {errors}"
    assert draft_ids == ["draft_node_1", "draft_node_2", "draft_node_3", "draft_node_4"]
    assert duplicated["selected_node_ids"] == ["draft_node_3", "draft_node_4"]
    assert all(
        node["sourceRef"].startswith("ui_draft.duplicate.")
        for node in duplicated["nodes"]
        if node["id"] in {"draft_node_3", "draft_node_4"}
    )

    page.keyboard.press("Delete")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    removed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in removed["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1",
        "draft_node_2",
    ]

    page.keyboard.press("Control+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    restored = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in restored["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1",
        "draft_node_2",
        "draft_node_3",
        "draft_node_4",
    ]
    assert restored["truth_level_impact"] == "none"


def test_workbench_lasso_selects_and_group_moves_draft_nodes(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-editor-tool="node"]')
    page.click('[data-editor-tool="node"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    before = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    before_positions = {
        node["id"]: (node["x"], node["y"])
        for node in before["nodes"]
    }

    page.click('[data-editor-tool="select"]')
    page.locator('[data-editable-node-id="draft_node_1"]').scroll_into_view_if_needed()
    draft_node_1 = page.locator('[data-editable-node-id="draft_node_1"]').bounding_box()
    draft_node_2 = page.locator('[data-editable-node-id="draft_node_2"]').bounding_box()
    assert draft_node_1 is not None
    assert draft_node_2 is not None
    left = min(draft_node_1["x"], draft_node_2["x"]) - 44
    top = min(draft_node_1["y"], draft_node_2["y"]) - 44
    right = max(draft_node_1["x"] + draft_node_1["width"], draft_node_2["x"] + draft_node_2["width"]) + 44
    bottom = max(draft_node_1["y"] + draft_node_1["height"], draft_node_2["y"] + draft_node_2["height"]) + 44
    page.keyboard.down("Shift")
    try:
        page.mouse.move(left, top)
        page.mouse.down()
        page.mouse.move(right, bottom, steps=8)
        page.mouse.up()
    finally:
        page.keyboard.up("Shift")

    page.wait_for_function(
        """
        () => {
          const first = document.querySelector('[data-editable-node-id="draft_node_1"]');
          const second = document.querySelector('[data-editable-node-id="draft_node_2"]');
          return first?.getAttribute('data-multi-selected') === 'true'
            && second?.getAttribute('data-multi-selected') === 'true';
        }
        """
    )
    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-multi-selected") == "true"
    assert page.locator('[data-editable-node-id="draft_node_2"]').get_attribute("data-multi-selected") == "true"

    page.locator('[data-editable-node-id="draft_node_1"]').scroll_into_view_if_needed()
    draft_node_1 = page.locator('[data-editable-node-id="draft_node_1"]').bounding_box()
    assert draft_node_1 is not None
    page.mouse.move(draft_node_1["x"] + draft_node_1["width"] / 2, draft_node_1["y"] + draft_node_1["height"] / 2)
    page.mouse.down()
    page.mouse.move(
        draft_node_1["x"] + draft_node_1["width"] / 2 + 90,
        draft_node_1["y"] + draft_node_1["height"] / 2 + 45,
        steps=8,
    )
    page.mouse.up()

    before_draft_node_1_x, before_draft_node_1_y = before_positions["draft_node_1"]
    before_draft_node_2_x, before_draft_node_2_y = before_positions["draft_node_2"]
    page.wait_for_function(
        f"""
        () => {{
          const first = document.querySelector('[data-editable-node-id="draft_node_1"]');
          const second = document.querySelector('[data-editable-node-id="draft_node_2"]');
          if (!first || !second) return false;
          const firstStyle = window.getComputedStyle(first);
          const secondStyle = window.getComputedStyle(second);
          return (
            firstStyle.getPropertyValue('--node-x').trim() !== {json.dumps(before_draft_node_1_x)}
            || firstStyle.getPropertyValue('--node-y').trim() !== {json.dumps(before_draft_node_1_y)}
          ) && (
            secondStyle.getPropertyValue('--node-x').trim() !== {json.dumps(before_draft_node_2_x)}
            || secondStyle.getPropertyValue('--node-y').trim() !== {json.dumps(before_draft_node_2_y)}
          );
        }}
        """
    )

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    moved = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    moved_positions = {
        node["id"]: (node["x"], node["y"])
        for node in moved["nodes"]
    }

    assert errors == [], f"page JS errors: {errors}"
    assert set(moved["selected_node_ids"]) >= {"draft_node_1", "draft_node_2"}
    assert moved_positions["draft_node_1"] != before_positions["draft_node_1"]
    assert moved_positions["draft_node_2"] != before_positions["draft_node_2"]
    for node_id in sorted(set(before_positions) - {"draft_node_1", "draft_node_2"}):
        assert moved_positions[node_id] == before_positions[node_id]
    assert moved["truth_level_impact"] == "none"

    page.keyboard.press("Control+Z")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    undone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    undone_positions = {
        node["id"]: (node["x"], node["y"])
        for node in undone["nodes"]
        if node["id"] in {"draft_node_1", "draft_node_2"}
    }
    assert undone_positions["draft_node_1"] == before_positions["draft_node_1"]
    assert undone_positions["draft_node_2"] == before_positions["draft_node_2"]


def test_workbench_canvas_interaction_summary_tracks_high_freedom_actions(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    page.keyboard.press("Control+D")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    duplicated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    summary = duplicated["canvas_interaction_summary"]

    assert errors == [], f"page JS errors: {errors}"
    assert summary["kind"] == "well-harness-workbench-canvas-interaction-summary"
    assert summary["candidate_state"] == "sandbox_candidate"
    assert summary["truth_effect"] == "none"
    assert summary["selected_node_count"] == 2
    assert summary["selected_edge_count"] == 0
    assert summary["last_action"] == "batch_duplicate_nodes"
    assert summary["node_count"] >= 8
    assert summary["edge_count"] >= 4
    assert page.locator("#workbench-canvas-selected-node-count").inner_text() == "2"
    assert page.locator("#workbench-canvas-selected-edge-count").inner_text() == "0"
    assert page.locator("#workbench-canvas-last-action").inner_text() == "batch_duplicate_nodes"
    assert duplicated["workspace_document"]["action_count"] >= 2

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_summary = imported["canvas_interaction_summary"]
    assert imported_summary["last_action"] in {"import_draft", "batch_duplicate_nodes"}
    assert imported_summary["node_count"] == summary["node_count"]
    assert imported_summary["edge_count"] == summary["edge_count"]
    assert imported_summary["truth_effect"] == "none"

    page.keyboard.press("Delete")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    deleted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert deleted["canvas_interaction_summary"]["last_action"] == "batch_remove_nodes"
    assert deleted["canvas_interaction_summary"]["selected_node_count"] == 1

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["canvas_interaction_summary"]["truth_effect"] == "none"
    assert archive["canvas_interaction_summary"]["last_action"] == "batch_remove_nodes"
    assert archive["checksums"]["canvas_interaction_summary_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_port_handles_create_typed_draft_edge(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="between"]')
    page.click('[data-editor-tool="node"]')

    source_handle = page.locator(
        '[data-port-handle-owner-id="draft_node_1"][data-port-handle-direction="out"]'
    )
    target_handle = page.locator(
        '[data-port-handle-owner-id="draft_node_2"][data-port-handle-direction="in"]'
    )
    _click_workbench_port_handle(page, "draft_node_1", "out")
    assert source_handle.get_attribute("data-port-handle-armed") == "true"
    _click_workbench_port_handle(page, "draft_node_2", "in")

    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    edge = next(
        item for item in draft["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )

    assert errors == [], f"page JS errors: {errors}"
    assert edge["source_port_id"] == "draft_node_1:out"
    assert edge["target_port_id"] == "draft_node_2:in"
    assert edge["signal_id"] == "draft_node_1_compare_output__to__draft_node_2_between_input"
    assert edge["value_type"] == "number"
    assert edge["required"] is True
    assert edge["edge_label"] == "draft_node_1:out -> draft_node_2:in"
    assert edge["route_metadata"]["version"] == "workbench-edge-route-metadata.v1"
    assert edge["route_metadata"]["routing_mode"] == "orthogonal"
    assert edge["route_metadata"]["source_port_id"] == "draft_node_1:out"
    assert edge["route_metadata"]["target_port_id"] == "draft_node_2:in"
    assert edge["route_metadata"]["truth_effect"] == "none"
    assert edge["hardware_binding"]["truth_effect"] == "none"
    assert draft["port_contract_summary"]["edge_contracts"] >= 1
    assert draft["port_compatibility_report"]["status"] == "pass"
    assert draft["truth_level_impact"] == "none"
    edge_path = page.locator(f'[data-editable-edge-id="{edge["id"]}"]')
    assert edge_path.get_attribute("data-edge-label") == "draft_node_1:out -> draft_node_2:in"
    edge_display_label = edge_path.get_attribute("data-edge-display-label")
    assert edge_display_label
    assert len(edge_display_label) < len("draft_node_1:out -> draft_node_2:in")
    assert edge_path.get_attribute("data-route-mode") == "orthogonal"
    assert edge_path.get_attribute("data-route-guide") == "orthogonal_lane_guide"
    assert edge_path.get_attribute("data-route-guide-effect") == "display_only"
    assert edge_path.get_attribute("data-route-guide-truth-effect") == "none"
    assert int(edge_path.get_attribute("data-route-segment-count") or "0") >= 3
    assert edge_path.get_attribute("data-route-lane-axis") in {"x", "y", "mixed"}
    assert edge_path.get_attribute("data-route-direction") in {"forward", "reverse"}
    edge_path_d = edge_path.get_attribute("d")
    assert edge_path_d and "C" not in edge_path_d
    assert edge_path_d.count("L") >= 3
    route_guide = page.locator(f'.workbench-edge-route-guide[data-route-guide-edge-id="{edge["id"]}"]')
    assert route_guide.count() == 1
    assert route_guide.get_attribute("data-editable-edge-id") is None
    assert route_guide.get_attribute("data-route-guide") == "orthogonal_lane_guide"
    assert route_guide.get_attribute("data-route-guide-truth-effect") == "none"
    assert route_guide.get_attribute("d") == edge_path_d
    edge_label = page.locator(f'[data-editable-edge-label-id="{edge["id"]}"]')
    assert edge_label.get_attribute("data-edge-label") == "draft_node_1:out -> draft_node_2:in"
    assert edge_label.get_attribute("data-edge-display-label") == edge_display_label
    assert edge_label.text_content().strip() == edge_display_label
    assert edge_label.is_visible() is False

    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    after_duplicate_attempt = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    matching_edges = [
        item for item in after_duplicate_attempt["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    ]
    assert len(matching_edges) == 1

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_edge = next(
        item for item in imported["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )
    assert imported_edge["edge_label"] == edge["edge_label"]
    assert imported_edge["route_metadata"] == edge["route_metadata"]

    page.locator(f'[data-editable-edge-id="{imported_edge["id"]}"]').dispatch_event("click")
    assert page.locator(f'[data-editable-edge-label-id="{imported_edge["id"]}"]').is_visible() is True
    _open_workbench_inspector_mode(page, "evidence")
    edge_detail = page.locator("#workbench-inspector-evidence-detail").inner_text()
    assert "Route mode" in edge_detail
    assert "orthogonal" in edge_detail
    page.click('[data-editor-tool="disconnect"]')
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    disconnected = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert not [
        item for item in disconnected["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    ]

    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    archived_edge = next(
        item for item in archive["model_json"]["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )
    assert archived_edge["edge_label"] == "draft_node_1:out -> draft_node_2:in"
    assert archived_edge["route_metadata"]["truth_effect"] == "none"
    assert archive["port_compatibility_report"]["status"] == "pass"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_simulink_toolbar_tooltips_and_block_labels_render(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')

    rendered = page.evaluate(
        """
        () => {
          const node = document.querySelector('[data-editable-node-id="draft_node_1"]');
          const wireTool = document.querySelector('[data-editor-tool="edge"]');
          wireTool.focus();
          const tooltipStyle = window.getComputedStyle(wireTool, '::after');
          return {
            nodeText: node ? node.textContent.trim() : '',
            nodeDisplayText: node ? (node.querySelector('span')?.textContent.trim() || '') : '',
            nodeShortLabel: node
              ? (node.querySelector('.workbench-reference-node-op')?.textContent.trim() || '')
              : '',
            nodeTitle: node ? node.getAttribute('title') : '',
            nodeTooltip: node ? node.getAttribute('data-tooltip') : '',
            toolTooltip: wireTool ? wireTool.getAttribute('data-tooltip') : '',
            toolAria: wireTool ? wireTool.getAttribute('aria-label') : '',
            pseudoContent: tooltipStyle.content,
            pseudoOpacity: tooltipStyle.opacity,
            mainToolCount: document.querySelectorAll(
              '#workbench-editor-toolbar [data-tool-primary="true"]'
            ).length,
            deferredToolCount: document.querySelectorAll(
              '#workbench-editor-toolstrip [data-editor-tool], #workbench-editor-toolstrip [data-op-catalog-op], #workbench-editor-toolstrip [data-component-template-id]'
            ).length,
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert rendered["nodeShortLabel"] == "CMP"
    assert "Compare threshold" in rendered["nodeDisplayText"]
    assert "Compare threshold" in rendered["nodeTooltip"]
    assert "rules" not in rendered["nodeDisplayText"]
    assert rendered["toolTooltip"] == "连线：从输出端口拖到输入端口"
    assert rendered["toolAria"] == "连线：从输出端口拖到输入端口"
    assert "连线" in rendered["pseudoContent"]
    assert rendered["pseudoOpacity"] == "1"
    assert rendered["mainToolCount"] == 6
    assert rendered["deferredToolCount"] >= 12


def test_workbench_port_drag_preview_creates_route_diagnostics_edge(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1600, "height": 5600})
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="between"]')
    page.click('[data-editor-tool="node"]')

    source_handle = page.locator(
        '[data-port-handle-owner-id="draft_node_1"][data-port-handle-direction="out"]'
    )
    target_handle = page.locator(
        '[data-port-handle-owner-id="draft_node_2"][data-port-handle-direction="in"]'
    )
    source_handle.scroll_into_view_if_needed()
    target_handle.scroll_into_view_if_needed()
    source_box = source_handle.bounding_box()
    target_box = target_handle.bounding_box()
    assert source_box is not None
    assert target_box is not None
    assert page.evaluate(
        """
        ([x, y]) => document.elementFromPoint(x, y)
          ?.closest('.workbench-port-handle')
          ?.getAttribute('data-port-handle-owner-id')
        """,
        [source_box["x"] + source_box["width"] / 2, source_box["y"] + source_box["height"] / 2],
    ) == "draft_node_1"

    page.mouse.move(source_box["x"] + source_box["width"] / 2, source_box["y"] + source_box["height"] / 2)
    page.mouse.down()
    page.mouse.move(target_box["x"] + target_box["width"] / 2, target_box["y"] + target_box["height"] / 2, steps=8)
    assert page.locator("#workbench-editable-canvas").get_attribute("data-port-drag-state") == "preview"
    assert page.locator("#workbench-editable-canvas").get_attribute("data-port-drag-compatibility") == "pass"
    assert page.locator(".workbench-port-drag-preview").count() == 1
    page.mouse.up()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    edge = next(
        item for item in draft["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )

    assert errors == [], f"page JS errors: {errors}"
    assert edge["source_ref"] == "ui_draft.port_drag_wiring"
    assert edge["route_metadata"]["creation_tool"] == "port_drag_wiring"
    assert edge["route_metadata"]["compatibility_status"] == "pass"
    assert edge["route_metadata"]["source_port_id"] == "draft_node_1:out"
    assert edge["route_metadata"]["target_port_id"] == "draft_node_2:in"
    assert draft["port_compatibility_report"]["status"] == "pass"
    assert draft["canvas_interaction_summary"]["last_action"] == "connect_edge"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    archived_edge = next(
        item for item in archive["model_json"]["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )
    assert archived_edge["route_metadata"]["creation_tool"] == "port_drag_wiring"
    assert archived_edge["route_metadata"]["truth_effect"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_sandbox_scenario_test_bench_runs_exports_and_archives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="between"]')
    page.click('[data-editor-tool="node"]')
    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")

    _open_workbench_inspector_mode(page, "run")
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": False},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('well-harness-workbench-sandbox-test-run-report');
        }
        """
    )
    report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert report["kind"] == "well-harness-workbench-sandbox-test-run-report"
    assert report["version"] == "workbench-sandbox-test-run-report.v1"
    assert report["candidate_state"] == "sandbox_candidate"
    assert report["truth_effect"] == "none"
    assert report["certification_claim"] == "none"
    assert report["status"] == "pass"
    assert report["assertion_status"] == "pass"
    assert report["pass_count"] == 2
    assert report["fail_count"] == 0
    assert report["definition"]["kind"] == "well-harness-workbench-sandbox-test-bench"
    assert report["definition"]["truth_effect"] == "none"
    assert report["trace"][0]["tick"] == 0
    assert report["trace"][1]["tick"] == 1

    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["sandbox_test_bench"]["truth_effect"] == "none"
    assert draft["sandbox_test_run_report"]["assertion_status"] == "pass"
    assert draft["sandbox_test_run_report"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["sandbox_test_bench"]["assertion_count"] == 2
    assert imported["sandbox_test_run_report"]["assertion_status"] == "pass"

    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["sandbox_test_bench"]["tick_count"] == 2
    assert archive["sandbox_test_run_report"]["assertion_status"] == "pass"
    assert archive["checksums"]["sandbox_test_bench_checksum"]
    assert archive["checksums"]["sandbox_test_run_report_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_scenario_test_case_library_create_duplicate_select_run_export_import_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.click('[data-op-catalog-op="input"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="output"]')
    page.click('[data-editor-tool="node"]')
    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")

    _fill_workbench_run_control(page, "#workbench-test-case-name", "Power-on pass case")
    _fill_workbench_run_control(page, "#workbench-test-case-notes", "Library case should survive export/import/archive.")
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps([{"tick": 0, "inputs": {"draft_node_1:out": True, "draft_node_1": True}}]),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps([{"tick": 0, "target": "draft_node_2:out", "expected": True}]),
    )
    _fill_workbench_run_control(page, "#workbench-test-case-expected-outputs-json",
        json.dumps([{"tick": 0, "target": "draft_node_2:out", "expected": True}]),
    )
    _click_workbench_run_control(page, "#workbench-save-test-case-btn")
    _click_workbench_run_control(page, "#workbench-duplicate-test-case-btn")
    _fill_workbench_run_control(page, "#workbench-test-case-name", "Power-on duplicate run case")
    _click_workbench_run_control(page, "#workbench-save-test-case-btn")
    _select_workbench_run_control(page, "#workbench-test-case-library-select", label="Power-on pass case")
    assert page.locator("#workbench-test-case-name").input_value() == "Power-on pass case"
    _select_workbench_run_control(page, "#workbench-test-case-library-select", label="Power-on duplicate run case")
    assert page.locator("#workbench-test-case-name").input_value() == "Power-on duplicate run case"

    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('scenario_test_case_library_checksum');
        }
        """
    )
    report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert report["kind"] == "well-harness-workbench-sandbox-test-run-report"
    assert report["version"] == "workbench-sandbox-test-run-report.v1"
    assert report["status"] == "pass"
    assert report["test_case_id"] == report["active_test_case_id"]
    assert report["selected_test_case_id"] == report["active_test_case_id"]
    assert report["graph_document_version"] == "workbench-editable-graph-document.v2"
    assert report["graph_document_revision_id"]
    assert report["workspace_revision_id"]
    assert report["scenario_test_case_library_checksum"].startswith("ui_draft_")
    assert report["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    library = draft["scenario_test_case_library"]
    active_id = library["active_test_case_id"]
    assert library["kind"] == "well-harness-workbench-scenario-test-case-library"
    assert library["version"] == "workbench-scenario-test-case-library.v1"
    assert library["test_case_count"] == 2
    assert library["selected_test_case_id"] == active_id
    assert draft["sandbox_test_bench"]["test_case_id"] == active_id
    assert draft["sandbox_test_run_report"]["test_case_id"] == active_id
    assert draft["editable_graph_document"]["canonical_model"]["scenario_test_case_library"]["active_test_case_id"] == active_id

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["scenario_test_case_library"]["test_case_count"] == 2
    assert imported["scenario_test_case_library"]["active_test_case_id"] == active_id
    assert imported["sandbox_test_run_report"]["scenario_test_case_library_checksum"].startswith("ui_draft_")

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["scenario_test_case_library"]["test_case_count"] == 2
    assert archive["scenario_test_case_library"]["truth_effect"] == "none"
    assert archive["sandbox_test_run_report"]["test_case_id"] == active_id
    assert archive["checksums"]["scenario_test_case_library_checksum"]
    assert archive["foundation_review_archive"]["sections"]["scenario_test_case_library"]["status"] == "present"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_sandbox_runner_trace_kernel_records_node_port_edge_assertion_frames(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.click('[data-op-catalog-op="input"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.locator('[data-editable-node-id="draft_node_2"]').click()
    _fill_workbench_evidence_control(page, "#workbench-rule-threshold", "1")
    page.click("#workbench-apply-rule-parameter-btn")
    page.click('[data-op-catalog-op="output"]')
    page.click('[data-editor-tool="node"]')
    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")
    _click_workbench_port_handle(page, "draft_node_2", "out")
    _click_workbench_port_handle(page, "draft_node_3", "in")

    _fill_workbench_run_control(page, "#workbench-test-case-name", "Trace kernel compare case")
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1": False}},
                {"tick": 1, "inputs": {"draft_node_1": True}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_3:out", "expected": False},
                {"tick": 1, "target": "draft_node_3:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-save-test-case-btn")
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('sandbox_runner_trace_kernel');
        }
        """
    )
    report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    kernel = report["sandbox_runner_trace_kernel"]
    assert errors == [], f"page JS errors: {errors}"
    assert report["kind"] == "well-harness-workbench-sandbox-test-run-report"
    assert report["status"] == "pass"
    assert report["assertion_status"] == "pass"
    assert kernel["kind"] == "well-harness-workbench-sandbox-runner-trace-kernel"
    assert kernel["version"] == "workbench-sandbox-runner-trace-kernel.v2"
    assert kernel["evaluation_order"] == ["draft_node_1", "draft_node_2", "draft_node_3"]
    assert kernel["tick_count"] == 2
    assert kernel["trace_frame_count"] == 2
    assert kernel["finding_count"] == 0
    assert kernel["truth_effect"] == "none"
    assert report["trace"][0]["node_values"] == kernel["frames"][0]["node_values"]
    assert kernel["frames"][0]["assertion_results"][0]["status"] == "pass"
    assert kernel["frames"][1]["assertion_results"][0]["status"] == "pass"
    assert any(item["node_id"] == "draft_node_2" and item["output_value"] is False for item in kernel["frames"][0]["node_values"])
    assert any(item["node_id"] == "draft_node_2" and item["output_value"] is True for item in kernel["frames"][1]["node_values"])
    assert any(item["port_id"] == "draft_node_3:out" and item["value"] is True for item in kernel["frames"][1]["port_values"])
    assert any(item["source_node_id"] == "draft_node_2" and item["target_node_id"] == "draft_node_3" and item["value"] is True for item in kernel["frames"][1]["edge_values"])

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["sandbox_test_run_report"]["sandbox_runner_trace_kernel"]["trace_frame_count"] == 2
    assert draft["sandbox_test_run_report"]["sandbox_runner_trace_kernel_checksum"].startswith("ui_draft_")
    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["sandbox_test_run_report"]["sandbox_runner_trace_kernel"]["evaluation_order"] == [
        "draft_node_1",
        "draft_node_2",
        "draft_node_3",
    ]

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["sandbox_test_run_report"]["sandbox_runner_trace_kernel"]["truth_effect"] == "none"
    assert archive["checksums"]["sandbox_runner_trace_kernel_checksum"]
    assert archive["foundation_review_archive"]["sections"]["sandbox_runner_trace_kernel"]["status"] == "present"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_sandbox_runner_trace_kernel_reports_invalid_graph_findings(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _click_workbench_port_handle(page, "draft_node_1", "out")
    _click_workbench_port_handle(page, "draft_node_2", "in")
    _click_workbench_port_handle(page, "draft_node_2", "out")
    _click_workbench_port_handle(page, "draft_node_1", "in")
    page.evaluate(
        """
        () => {
          const node = document.querySelector('[data-editable-node-id="draft_node_1"]');
          node.setAttribute('data-node-op', 'python_eval');
          node.setAttribute('data-op-catalog-entry', 'python_eval');
        }
        """
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json", json.dumps([{"tick": 0, "inputs": {}}]))
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json", json.dumps([]))
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('cycle_detected');
        }
        """
    )
    report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    kernel = report["sandbox_runner_trace_kernel"]
    codes = {finding["code"] for finding in kernel["findings"]}
    assert errors == [], f"page JS errors: {errors}"
    assert report["status"] == "invalid_scenario"
    assert "unsupported_op" in codes
    assert "cycle_detected" in codes
    assert "missing_input" in codes
    assert kernel["finding_count"] >= 3
    assert all(finding["truth_effect"] == "none" for finding in kernel["findings"])
    assert kernel["candidate_state"] == "sandbox_candidate"
    assert kernel["certification_claim"] == "none"
    assert report["truth_effect"] == "none"
    assert report["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_large_sandbox_graph_trace_and_archive_checksums_are_stable(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    base_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    stress_pack = large_sandbox_stress_pack(base_draft)
    large_case = stress_pack["cases"]["pass"]
    large_draft = large_case["draft"]
    _set_draft_buffer_value(page, json.dumps(large_draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")

    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(large_case["inputs"]),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(large_case["assertions"]),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('sandbox_runner_trace_kernel');
        }
        """
    )
    first_report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    second_report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    first_kernel = first_report["sandbox_runner_trace_kernel"]
    second_kernel = second_report["sandbox_runner_trace_kernel"]

    assert errors == [], f"page JS errors: {errors}"
    assert first_report["status"] == "pass"
    assert second_report["status"] == "pass"
    assert first_report["sandbox_runner_trace_kernel_checksum"] == second_report["sandbox_runner_trace_kernel_checksum"]
    assert first_kernel == second_kernel
    assert first_kernel["evaluation_order"] == [f"draft_node_{index}" for index in range(1, 17)]
    assert first_kernel["tick_count"] == 3
    assert first_kernel["trace_frame_count"] == 3
    assert first_kernel["finding_count"] == 0
    assert len(first_kernel["frames"][2]["node_values"]) == 16
    assert len(first_kernel["frames"][2]["edge_values"]) == 15
    assert len(first_kernel["frames"][2]["port_values"]) == 32
    assert first_kernel["frames"][2]["assertion_results"][0]["status"] == "pass"
    assert first_kernel["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    first_archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    second_archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    stable_checksum_keys = [
        "editable_graph_document_checksum",
        "sandbox_test_bench_checksum",
        "sandbox_test_run_report_checksum",
        "sandbox_runner_trace_kernel_checksum",
        "foundation_review_archive_checksum",
        "foundation_review_archive_validation_checksum",
    ]
    assert first_archive["editable_graph_document"]["node_count"] == 16
    assert first_archive["editable_graph_document"]["edge_count"] == 15
    assert first_archive["sandbox_runner_trace_kernel"]["trace_frame_count"] == 3
    assert first_archive["foundation_review_archive"]["sections"]["sandbox_runner_trace_kernel"]["status"] == "present"
    assert first_archive["review_archive_restore_v3"]["checksum_mismatch_count"] == 0
    assert first_archive["red_line_metadata"]["controller_truth_modified"] is False
    for key in stable_checksum_keys:
        assert first_archive["checksums"][key]
        assert first_archive["checksums"][key] == second_archive["checksums"][key]


def test_workbench_large_sandbox_graph_invalid_findings_remain_structured(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    base_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    invalid_case = large_sandbox_stress_pack(base_draft)["cases"]["invalid_graph"]
    large_draft = invalid_case["draft"]
    _set_draft_buffer_value(page, json.dumps(large_draft))
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    page.evaluate(
        """
        ([nodeId, op]) => {
          const node = document.querySelector(`[data-editable-node-id="${nodeId}"]`);
          node.setAttribute('data-node-op', op);
          node.setAttribute('data-op-catalog-entry', op);
        }
        """,
        [invalid_case["unsupported_node_id"], invalid_case["unsupported_op"]],
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(invalid_case["inputs"]),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json", json.dumps(invalid_case["assertions"]))
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-test-bench-report-output');
          return output && output.value.includes('dangling_edge');
        }
        """
    )
    report = json.loads(page.locator("#workbench-test-bench-report-output").input_value())
    kernel = report["sandbox_runner_trace_kernel"]
    codes = {finding["code"] for finding in kernel["findings"]}

    assert errors == [], f"page JS errors: {errors}"
    assert report["status"] == "invalid_scenario"
    assert kernel["status"] == "invalid_scenario"
    assert set(invalid_case["expected_finding_codes"]).issubset(codes)
    assert kernel["finding_count"] >= 3
    assert kernel["candidate_state"] == "sandbox_candidate"
    assert kernel["certification_claim"] == "none"
    assert kernel["truth_effect"] == "none"
    assert all(finding["code"] and finding["message"] for finding in kernel["findings"])
    assert all(finding["severity"] in {"warning", "error"} for finding in kernel["findings"])
    assert all(finding["candidate_state"] == "sandbox_candidate" for finding in kernel["findings"])
    assert all(finding["truth_effect"] == "none" for finding in kernel["findings"])
    assert report["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_candidate_debugger_view_tracks_failing_assertion_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-candidate-debugger-status')?.textContent.trim() === 'fail'
        """
    )
    page.locator('[data-editable-node-id="draft_node_1"]').click()

    assert errors == [], f"page JS errors: {errors}"
    assert page.locator("#workbench-candidate-debugger-target").inner_text() == "node:draft_node_1"
    assert page.locator("#workbench-candidate-debugger-tick").inner_text() == "0"
    assert "expected=true observed=false" in page.locator("#workbench-candidate-debugger-assertion").inner_text()
    assert "draft_node_1:out=false" in page.locator("#workbench-candidate-debugger-observed").inner_text()
    assert page.locator("#workbench-candidate-debugger-trace").inner_text() == "available"

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    debugger_view = draft["candidate_debugger_view"]
    assert debugger_view["kind"] == "well-harness-workbench-candidate-debugger-view"
    assert debugger_view["target"]["owner_key"] == "node:draft_node_1"
    assert debugger_view["status"] == "fail"
    assert debugger_view["selected_tick"] == 0
    assert debugger_view["first_failing_assertion"]["target"] == "draft_node_1:out"
    assert debugger_view["observed_values"][0]["value"] is False
    assert debugger_view["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["candidate_debugger_view"]["target"]["owner_key"] == "node:draft_node_1"
    assert imported["candidate_debugger_view"]["first_failing_assertion"]["status"] == "fail"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["candidate_debugger_view"]["truth_effect"] == "none"
    assert archive["candidate_debugger_view"]["first_failing_assertion"]["target"] == "draft_node_1:out"
    assert archive["checksums"]["candidate_debugger_view_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_scenario_failure_explanation_links_assertion_frame_owner_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-failure-explanation-status')?.textContent.trim() === 'fail'
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert page.locator("#workbench-scenario-failure-explanation").get_attribute("data-explanation-status") == "fail"
    assert page.locator("#workbench-scenario-failure-explanation").get_attribute("data-explanation-truth-effect") == "none"
    assert "draft_node_1:out" in page.locator("#workbench-failure-explanation-assertion").inner_text()
    assert "tick=0" in page.locator("#workbench-failure-explanation-frame").inner_text()
    assert "node:draft_node_1" in page.locator("#workbench-failure-explanation-owner").inner_text()
    assert "port:draft_node_1:out" in page.locator("#workbench-failure-explanation-owner").inner_text()
    assert page.locator("#workbench-failure-explanation-current").inner_text() == "false"
    assert page.locator("#workbench-failure-explanation-expected").inner_text() == "true"
    assert "draft_node_1:in=2" in page.locator("#workbench-failure-explanation-upstream").inner_text()
    assert page.locator("#workbench-failure-explanation-truth-effect").inner_text() == "none"

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    explanation = draft["scenario_failure_explanation"]
    assert explanation["kind"] == "well-harness-workbench-scenario-failure-explanation"
    assert explanation["version"] == "workbench-scenario-failure-explanation.v1"
    assert explanation["status"] == "fail"
    assert explanation["assertion"]["target"] == "draft_node_1:out"
    assert explanation["timeline_frame"]["tick"] == 0
    assert explanation["target"]["owner_key"] == "node:draft_node_1"
    assert explanation["target"]["port_id"] == "draft_node_1:out"
    assert explanation["current_value"] is False
    assert explanation["expected_value"] is True
    assert explanation["upstream_dependencies"][0]["port_id"] == "draft_node_1:in"
    assert explanation["upstream_dependencies"][0]["value"] == 2
    assert explanation["candidate_state"] == "sandbox_candidate"
    assert explanation["certification_claim"] == "none"
    assert explanation["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["scenario_failure_explanation"]["target"]["owner_key"] == "node:draft_node_1"
    assert imported["scenario_failure_explanation"]["upstream_dependencies"][0]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["scenario_failure_explanation"]["truth_effect"] == "none"
    assert archive["scenario_failure_explanation"]["assertion"]["target"] == "draft_node_1:out"
    assert archive["checksums"]["scenario_failure_explanation_checksum"]
    assert archive["foundation_review_archive"]["sections"]["scenario_failure_explanation"]["status"] == "present"
    assert archive["review_archive_restore_v3"]["status"] == "pass"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_debug_probe_timeline_tracks_selected_node_over_trace_and_restore(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-candidate-debugger-status')?.textContent.trim() === 'fail'
        """
    )
    page.locator('[data-editable-node-id="draft_node_1"]').click()

    assert errors == [], f"page JS errors: {errors}"
    assert "draft_node_1:out=false @ tick 0" in page.locator("#workbench-candidate-debugger-observed").inner_text()
    assert "draft_node_1:out=true @ tick 1" in page.locator("#workbench-candidate-debugger-observed").inner_text()

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    probe = draft["debug_probe_timeline"]
    assert probe["kind"] == "well-harness-workbench-debug-probe-timeline"
    assert probe["version"] == "workbench-debug-probe-timeline.v3"
    assert probe["target"]["owner_key"] == "node:draft_node_1"
    assert probe["selected_tick"] == 0
    assert probe["watched_value_count"] == 4
    assert probe["watched_values"][0]["tick"] == 0
    assert probe["watched_values"][0]["port_id"] == "draft_node_1:out"
    assert probe["watched_values"][0]["value"] is False
    assert probe["watched_values"][1]["tick"] == 1
    assert probe["watched_values"][1]["port_id"] == "draft_node_1:out"
    assert probe["watched_values"][1]["value"] is True
    assert probe["first_failing_assertion"]["target"] == "draft_node_1:out"
    assert probe["assertion_link"]["target_owner_key"] == "node:draft_node_1"
    assert probe["selection_sync"]["graph_selection_owner_key"] == "node:draft_node_1"
    assert probe["selection_sync"]["timeline_selected_tick"] == 0
    assert probe["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["debug_probe_timeline"]["target"]["owner_key"] == "node:draft_node_1"
    assert imported["debug_probe_timeline"]["watched_values"][1]["value"] is True

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["debug_probe_timeline"]["truth_effect"] == "none"
    assert archive["debug_probe_timeline"]["watched_values"][0]["tick"] == 0
    assert archive["checksums"]["debug_probe_timeline_checksum"]
    assert archive["foundation_review_archive"]["sections"]["debug_probe_timeline"]["status"] == "present"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_preflight_analyzer_classifies_failed_candidate_and_archives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    _fill_workbench_run_control(page, "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    _fill_workbench_run_control(page, "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    _click_workbench_run_control(page, "#workbench-run-test-bench-btn")
    _click_workbench_run_control(page, "#workbench-run-preflight-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-preflight-classification')?.textContent.trim() === 'invalid_candidate'
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert page.locator("#workbench-preflight-findings-count").inner_text() != "0"
    assert "Fix failing sandbox assertions" in page.locator("#workbench-preflight-actions").inner_text()
    report = json.loads(page.locator("#workbench-preflight-output").input_value())
    assert report["kind"] == "well-harness-workbench-preflight-analyzer-report"
    assert report["version"] == "workbench-preflight-analyzer.v1"
    assert report["classification"] == "invalid_candidate"
    assert report["sandbox_test_run_report"]["status"] == "fail"
    assert report["candidate_model_hash"] == report["sandbox_test_run_report"]["model_hash"]
    assert any(finding["code"] == "sandbox_test_failed" for finding in report["findings"])
    assert report["candidate_state"] == "sandbox_candidate"
    assert report["certification_claim"] == "none"
    assert report["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["preflight_analyzer_report"]["classification"] == "invalid_candidate"
    assert draft["preflight_analyzer_report"]["candidate_model_hash"] == report["candidate_model_hash"]

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    _set_draft_buffer_value(page, draft_json)
    _click_workbench_handoff_control(page, "#workbench-import-draft-btn")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["preflight_analyzer_report"]["classification"] == "invalid_candidate"
    assert imported["preflight_analyzer_report"]["truth_effect"] == "none"

    _click_workbench_handoff_control(page, "#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["preflight_analyzer_report"]["classification"] == "invalid_candidate"
    assert archive["preflight_analyzer_report"]["findings"][0]["truth_effect"] == "none"
    assert archive["foundation_review_archive"]["kind"] == "well-harness-workbench-foundation-review-archive"
    assert archive["foundation_review_archive"]["version"] == "workbench-foundation-review-archive.v1"
    assert archive["foundation_review_archive"]["candidate_state"] == "sandbox_candidate"
    assert archive["foundation_review_archive"]["certification_claim"] == "none"
    assert archive["foundation_review_archive"]["truth_effect"] == "none"
    assert archive["foundation_review_archive"]["live_linear_mutation"] is False
    assert archive["foundation_review_archive"]["sections"]["editable_graph_document"]["status"] == "present"
    assert archive["foundation_review_archive"]["sections"]["sandbox_test_run_report"]["status"] == "present"
    assert archive["foundation_review_archive"]["sections"]["candidate_debugger_view"]["status"] == "present"
    assert archive["foundation_review_archive"]["sections"]["preflight_analyzer_report"]["status"] == "present"
    assert archive["foundation_review_archive"]["sections"]["hardware_interface_designer"]["status"] == "present"
    assert archive["foundation_review_archive"]["sections"]["changerequest_handoff_packet"]["status"] == "present"
    assert archive["foundation_review_archive"]["linear_ready"]["live_linear_mutation"] is False
    assert archive["foundation_review_archive_validation"]["status"] == "pass"
    assert archive["foundation_review_archive_validation"]["truth_effect"] == "none"
    assert archive["checksums"]["foundation_review_archive_checksum"]
    assert archive["checksums"]["foundation_review_archive_validation_checksum"]
    assert archive["checksums"]["preflight_analyzer_report_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_canvas_viewport_pan_zoom_fit_preserves_model_coordinates(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate(
        """
        () => {
          window.localStorage.removeItem('well-harness-editable-workbench-draft-v1');
          window.localStorage.removeItem('well-harness-editable-workbench-draft-snapshots-v1');
        }
        """
    )
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-editor-tool="node"]')
    page.click('[data-editor-tool="node"]')
    page.locator('[data-editable-node-id="draft_node_1"]').click(modifiers=["Shift"])
    _open_workbench_inspector_mode(page, "handoff")
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    before = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    before_positions = {
        node["id"]: (node["x"], node["y"])
        for node in before["nodes"]
        if node["id"] in {"draft_node_1", "draft_node_2"}
    }

    page.click('[data-viewport-tool="zoom-in"]')
    assert float(page.locator("#workbench-editable-canvas").get_attribute("data-viewport-scale") or "1") > 1

    canvas = page.locator("#workbench-editable-canvas").bounding_box()
    assert canvas is not None
    page.keyboard.down("Space")
    page.mouse.move(canvas["x"] + 120, canvas["y"] + 140)
    page.mouse.down()
    page.mouse.move(canvas["x"] + 180, canvas["y"] + 190)
    page.mouse.up()
    page.keyboard.up("Space")
    assert page.locator("#workbench-editable-canvas").get_attribute("data-viewport-pan-x") != "0"

    page.evaluate(
        """
        () => {
          const canvas = document.getElementById('workbench-editable-canvas');
          const rect = canvas.getBoundingClientRect();
          canvas.dispatchEvent(new WheelEvent('wheel', {
            bubbles: true,
            cancelable: true,
            ctrlKey: true,
            deltaY: -120,
            clientX: rect.left + rect.width / 2,
            clientY: rect.top + rect.height / 2,
          }));
        }
        """
    )
    assert float(page.locator("#workbench-editable-canvas").get_attribute("data-viewport-scale") or "1") > 1

    page.click('[data-viewport-tool="fit-selection"]')
    _click_workbench_handoff_control(page, "#workbench-export-draft-btn")
    fitted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    fitted_positions = {
        node["id"]: (node["x"], node["y"])
        for node in fitted["nodes"]
        if node["id"] in {"draft_node_1", "draft_node_2"}
    }

    assert errors == [], f"page JS errors: {errors}"
    assert fitted_positions == before_positions
    assert fitted["viewport_state"]["truth_effect"] == "none"
    assert fitted["viewport_state"]["coordinate_effect"] == "viewport_only"

    page.click('[data-viewport-tool="reset"]')
    assert page.locator("#workbench-editable-canvas").get_attribute("data-viewport-state") == "reset"


def test_workbench_canvas_dominates_viewport_and_direct_pan_zoom_tracks_mouse(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1440, "height": 980})
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("localStorage.clear()")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    first_screen = page.evaluate(
        """
        () => {
          const box = (selector) => {
            const node = document.querySelector(selector);
            if (!node) return null;
            const rect = node.getBoundingClientRect();
            return {
              left: rect.left,
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              width: rect.width,
              height: rect.height,
            };
          };
          const styleValue = (selector, prop) => {
            const node = document.querySelector(selector);
            return node ? window.getComputedStyle(node).getPropertyValue(prop) : "";
          };
          const guide = document.querySelector('#workbench-canvas-first-guide');
          return {
            viewport: { width: window.innerWidth, height: window.innerHeight },
            main: box('.workbench-editable-main'),
            canvas: box('#workbench-editable-canvas'),
            guide: box('#workbench-canvas-first-guide'),
            guideText: guide ? guide.innerText.replace(/\\s+/g, ' ').trim() : "",
            mainColumns: styleValue('.workbench-editable-main', 'grid-template-columns'),
            toolbarPosition: styleValue('#workbench-editor-toolbar', 'position'),
            inspectorPosition: styleValue('#workbench-evidence-inspector', 'position'),
          };
        }
        """
    )
    assert first_screen["canvas"]["width"] >= first_screen["viewport"]["width"] * 0.78
    assert first_screen["canvas"]["height"] >= first_screen["viewport"]["height"] * 0.62
    assert first_screen["guide"]["height"] <= 52
    assert len(first_screen["guideText"]) <= 80
    assert first_screen["toolbarPosition"] == "absolute"
    assert first_screen["inspectorPosition"] == "absolute"
    assert "280px" not in first_screen["mainColumns"]
    assert "360px" not in first_screen["mainColumns"]

    blank_point = page.evaluate(
        """
        () => {
          const canvas = document.querySelector('#workbench-editable-canvas');
          const rect = canvas.getBoundingClientRect();
          const candidates = [
            [0.50, 0.82],
            [0.72, 0.82],
            [0.18, 0.82],
            [0.50, 0.72],
            [0.86, 0.70],
          ];
          for (const [rx, ry] of candidates) {
            const x = rect.left + rect.width * rx;
            const y = rect.top + rect.height * ry;
            const target = document.elementFromPoint(x, y);
            if (
              target
              && target.closest('#workbench-editable-canvas')
              && !target.closest('.workbench-editable-node')
              && !target.closest('[data-editable-edge-id]')
              && !target.closest('button, input, textarea, select')
              && !target.closest('#workbench-editor-toolstrip')
              && !target.closest('#workbench-reference-proof-strip')
              && !target.closest('#workbench-canvas-first-guide')
            ) {
              return { x, y };
            }
          }
          return null;
        }
        """
    )
    assert blank_point is not None
    page.mouse.move(blank_point["x"], blank_point["y"])
    page.mouse.down()
    page.mouse.move(blank_point["x"] + 116, blank_point["y"] + 72)
    page.mouse.up()
    pan_state = page.evaluate(
        """
        () => {
          const canvas = document.querySelector('#workbench-editable-canvas');
          return {
            panX: Number(canvas.getAttribute('data-viewport-pan-x') || '0'),
            panY: Number(canvas.getAttribute('data-viewport-pan-y') || '0'),
          };
        }
        """
    )
    assert abs(pan_state["panX"]) >= 90
    assert abs(pan_state["panY"]) >= 50

    zoom_probe = page.evaluate(
        """
        () => {
          const canvas = document.querySelector('#workbench-editable-canvas');
          const rect = canvas.getBoundingClientRect();
          const anchor = { x: rect.width * 0.24, y: rect.height * 0.68 };
          const before = {
            scale: Number(canvas.getAttribute('data-viewport-scale') || '1'),
            panX: Number(canvas.getAttribute('data-viewport-pan-x') || '0'),
            panY: Number(canvas.getAttribute('data-viewport-pan-y') || '0'),
          };
          const worldBefore = {
            x: (anchor.x - before.panX) / before.scale,
            y: (anchor.y - before.panY) / before.scale,
          };
          canvas.dispatchEvent(new WheelEvent('wheel', {
            bubbles: true,
            cancelable: true,
            deltaY: -240,
            clientX: rect.left + anchor.x,
            clientY: rect.top + anchor.y,
          }));
          const after = {
            scale: Number(canvas.getAttribute('data-viewport-scale') || '1'),
            panX: Number(canvas.getAttribute('data-viewport-pan-x') || '0'),
            panY: Number(canvas.getAttribute('data-viewport-pan-y') || '0'),
          };
          const worldAfter = {
            x: (anchor.x - after.panX) / after.scale,
            y: (anchor.y - after.panY) / after.scale,
          };
          return {
            scaleBefore: before.scale,
            scaleAfter: after.scale,
            worldDeltaX: Math.abs(worldAfter.x - worldBefore.x),
            worldDeltaY: Math.abs(worldAfter.y - worldBefore.y),
          };
        }
        """
    )
    assert zoom_probe["scaleAfter"] > zoom_probe["scaleBefore"]
    assert zoom_probe["worldDeltaX"] <= 0.75
    assert zoom_probe["worldDeltaY"] <= 0.75
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_reference_graph_is_connected_named_and_guide_discoverable(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1440, "height": 980})
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("localStorage.clear()")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.wait_for_function("() => document.querySelectorAll('[data-editable-edge-id]').length >= 18")

    visual = page.evaluate(
        """
        () => {
          const rectOf = (selector) => {
            const node = document.querySelector(selector);
            if (!node) return null;
            const rect = node.getBoundingClientRect();
            return {
              left: rect.left,
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              width: rect.width,
              height: rect.height,
            };
          };
          const pointTouchesRect = (point, rect, tolerance = 7) => (
            Boolean(rect)
            && point.x >= rect.left - tolerance
            && point.x <= rect.right + tolerance
            && point.y >= rect.top - tolerance
            && point.y <= rect.bottom + tolerance
          );
          const edgeConnectivity = Array.from(document.querySelectorAll('[data-editable-edge-id]'))
            .map((path) => {
              const sourceId = path.getAttribute('data-edge-source-id') || '';
              const targetId = path.getAttribute('data-edge-target-id') || '';
              const sourceRect = rectOf(`[data-editable-node-id="${sourceId}"]`);
              const targetRect = rectOf(`[data-editable-node-id="${targetId}"]`);
              const matrix = typeof path.getScreenCTM === 'function' ? path.getScreenCTM() : null;
              if (!matrix || typeof path.getPointAtLength !== 'function' || typeof path.getTotalLength !== 'function') {
                return { id: path.getAttribute('data-editable-edge-id') || '', sourceConnected: false, targetConnected: false };
              }
              const start = new DOMPoint(path.getPointAtLength(0).x, path.getPointAtLength(0).y).matrixTransform(matrix);
              const end = new DOMPoint(
                path.getPointAtLength(path.getTotalLength()).x,
                path.getPointAtLength(path.getTotalLength()).y,
              ).matrixTransform(matrix);
              return {
                id: path.getAttribute('data-editable-edge-id') || '',
                sourceId,
                targetId,
                sourceConnected: pointTouchesRect(start, sourceRect),
                targetConnected: pointTouchesRect(end, targetRect),
                startGap: sourceRect ? Math.round(Math.max(0, start.x - sourceRect.right, sourceRect.left - start.x)) : 999,
                endGap: targetRect ? Math.round(Math.max(0, targetRect.left - end.x, end.x - targetRect.right)) : 999,
              };
            });
          const nodeLabels = Array.from(document.querySelectorAll('[data-reference-proof-node]'))
            .map((node) => ({
              id: node.getAttribute('data-editable-node-id') || '',
              text: node.innerText.replace(/\\s+/g, ' ').trim(),
              op: node.getAttribute('data-node-op') || '',
              label: node.getAttribute('data-node-label') || '',
            }));
          const opOnlyLabels = nodeLabels.filter((node) => (
            ['IN', 'OUT', 'AND', 'OR', 'CMP', 'BTW', 'DLY', 'LAT', 'LCH'].includes(node.text)
          ));
          const canvas = rectOf('#workbench-editable-canvas');
          const toolstrip = rectOf('#workbench-editor-toolstrip');
          const proofStrip = rectOf('#workbench-reference-proof-strip');
          const compactGuide = rectOf('#workbench-canvas-first-guide');
          const guideEntry = rectOf('#workbench-open-onboarding-guide-btn');
          return {
            canvas,
            toolstrip,
            proofStrip,
            compactGuide,
            guideEntry,
            guideEntryText: document.querySelector('#workbench-open-onboarding-guide-btn')?.innerText.trim() || '',
            guideEntryLabel: document.querySelector('#workbench-open-onboarding-guide-btn')?.getAttribute('aria-label') || '',
            edgeCount: edgeConnectivity.length,
            disconnectedEdges: edgeConnectivity
              .filter((edge) => !edge.sourceConnected || !edge.targetConnected)
              .slice(0, 8),
            nodeLabels,
            opOnlyLabels,
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert visual["edgeCount"] >= 18
    assert visual["disconnectedEdges"] == []
    assert visual["opOnlyLabels"] == []
    assert any("无线电高度" in node["label"] and "6" in node["label"] for node in visual["nodeLabels"])
    assert any("油门锁" in node["label"] for node in visual["nodeLabels"])
    assert any(node["text"].startswith("高度<6ft") for node in visual["nodeLabels"])
    assert any(node["text"].startswith("THR锁") for node in visual["nodeLabels"])
    assert "新手指引" in visual["guideEntryText"] or "新手指引" in visual["guideEntryLabel"]
    assert visual["guideEntry"]["width"] >= 80
    assert visual["guideEntry"]["height"] >= 30
    assert visual["toolstrip"]["top"] >= visual["canvas"]["bottom"] - 84
    assert visual["compactGuide"]["top"] >= visual["canvas"]["bottom"] - 132
    assert visual["proofStrip"]["top"] >= visual["canvas"]["bottom"] - 132


def test_workbench_reference_first_screen_is_chinese_connected_and_uncovered(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    page.set_viewport_size({"width": 1366, "height": 768})
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("localStorage.clear()")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.wait_for_function("() => document.querySelectorAll('[data-editable-edge-id]').length >= 18")

    first_screen = page.evaluate(
        """
        () => {
          const chinese = /[\\u4e00-\\u9fff]/;
          const nodeLabels = Array.from(document.querySelectorAll('[data-reference-proof-node]'))
            .map((node) => node.innerText.replace(/\\s+/g, ' ').trim());
          const forbiddenEnglishNodeWords = [
            'Radio altitude', 'Reverser', 'inhibited', 'deployed', 'gate',
            'feedback', 'Engine running', 'Aircraft on ground', 'enable',
            'below deploy limit', 'deploy window', 'release command',
          ];
          const visibleText = document.body.innerText.replace(/\\s+/g, ' ').trim();
          const forbiddenVisibleText = [
            'Evidence Inspector', 'Candidate label', 'Operation', 'Rule summary',
            'Run sandbox', 'ChangeRequest packet', 'Baseline loaded',
            'Draft editable', 'Selected Debug Timeline',
          ];
          const edgeStyles = Array.from(document.querySelectorAll('[data-editable-edge-id]'))
            .map((path) => {
              const style = getComputedStyle(path);
              return {
                id: path.getAttribute('data-editable-edge-id') || '',
                width: Number.parseFloat(style.strokeWidth || '0') || 0,
                stroke: style.stroke,
                markerEnd: style.markerEnd || path.getAttribute('marker-end') || '',
                rect: (() => {
                  const rect = path.getBoundingClientRect();
                  return {
                    left: rect.left,
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                    width: rect.width,
                    height: rect.height,
                  };
                })(),
              };
            });
          const inspector = document.querySelector('#workbench-evidence-inspector');
          const inspectorRect = inspector ? inspector.getBoundingClientRect() : null;
          const inspectorStyle = inspector ? getComputedStyle(inspector) : null;
          const outputNode = document.querySelector('[data-editable-node-id="thr_lock"]');
          const outputRect = outputNode ? outputNode.getBoundingClientRect() : null;
          return {
            nodeLabels,
            chineseNodeCount: nodeLabels.filter((label) => chinese.test(label)).length,
            forbiddenNodeLabels: nodeLabels.filter((label) => forbiddenEnglishNodeWords.some((word) => label.includes(word))),
            forbiddenVisibleText: forbiddenVisibleText.filter((word) => visibleText.includes(word)),
            edgeCount: edgeStyles.length,
            weakEdges: edgeStyles.filter((edge) => edge.width < 5 || !edge.markerEnd || edge.stroke === 'none').slice(0, 8),
            inspectorOpen: inspector?.getAttribute('data-inspector-open') || '',
            inspectorWidth: inspectorRect ? inspectorRect.width : 0,
            inspectorDisplay: inspectorStyle ? inspectorStyle.display : '',
            outputVisible: Boolean(outputRect && outputRect.left >= 0 && outputRect.right <= window.innerWidth && outputRect.top >= 0 && outputRect.bottom <= window.innerHeight),
          };
        }
        """
    )

    assert errors == [], f"page JS errors: {errors}"
    assert first_screen["chineseNodeCount"] >= 16
    assert first_screen["forbiddenNodeLabels"] == []
    assert first_screen["forbiddenVisibleText"] == []
    assert first_screen["edgeCount"] >= 18
    assert first_screen["weakEdges"] == []
    assert first_screen["inspectorOpen"] == "false"
    assert first_screen["inspectorWidth"] <= 4
    assert first_screen["outputVisible"] is True

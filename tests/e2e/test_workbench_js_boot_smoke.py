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
from typing import Any, Iterator

import pytest

pytestmark = pytest.mark.e2e

# Skip the whole module if Playwright sync API or its browsers are missing.
playwright_sync_api = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

_OPEN_PAGES: list[Any] = []


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
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "partial"
    assert (
        page.locator('[data-editable-node-id="logic1"]').get_attribute("data-binding-quality")
        == "partial"
    )

    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "complete"
    assert (
        page.locator('[data-editable-node-id="logic1"]').get_attribute("data-binding-quality")
        == "complete"
    )
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
    assert first_binding["binding_quality"] == "complete"
    assert draft["binding_coverage"]["complete"] == 1
    assert draft["binding_coverage"]["truth_effect"] == "none"
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
    assert round_trip["binding_coverage"]["complete"] == 1

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["hardware_bindings"][0]["hardware_id"] == "TR-LRU-001"
    assert archive["hardware_bindings"][0]["truth_effect"] == "none"
    assert archive["binding_coverage"]["complete"] == 1
    assert archive["binding_coverage"]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_bindings_checksum"]
    assert archive["checksums"]["binding_coverage_checksum"]


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
    page.select_option("#workbench-sandbox-scenario-select", "nominal_landing")
    page.fill("#workbench-interface-hardware-id", "TR-LRU-ACCEPTANCE")
    page.fill("#workbench-interface-cable", "CBL-TR-ACCEPTANCE")
    page.fill("#workbench-interface-connector", "J-ACCEPT")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-ACCEPTANCE:J-ACCEPT")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    assert page.locator("#workbench-interface-binding-quality").inner_text() == "complete"

    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-run-sandbox-btn")
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

    page.click("#workbench-generate-handoff-btn")
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
    handoff_status = page.locator("#workbench-handoff-status").inner_text()
    assert "Candidate state: sandbox_candidate" in pr_proof
    assert "Certification claim: none" in pr_proof
    assert "Truth-level impact: none" in pr_proof
    assert "No live Linear mutation" in pr_proof
    assert "No live Linear mutation" in handoff_status
    assert "Diagnostic repair actions:" in linear_body

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
    packet = archive["changerequest_proof_packet"]
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
    assert red_lines["truth_level_impact"] == "none"
    assert red_lines["dal_pssa_impact"] == "none"
    assert red_lines["controller_truth_modified"] is False
    assert red_lines["live_linear_mutation"] is False
    assert archive["gate_claims"]["e2e_49_49"] == "not_claimed"
    assert archive["gate_claims"]["mypy_strict_clean"] == "not_claimed"
    assert archive["known_blockers"]
    assert checksums["manifest_checksum"]
    assert checksums["diff_summary_checksum"]
    assert checksums["changerequest_proof_packet_checksum"]
    assert checksums["gate_claims_checksum"]
    assert checksums["known_blockers_checksum"]


def test_workbench_hardware_palette_creates_and_applies_sandbox_bindings(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.wait_for_selector('[data-hardware-palette-id="lru:etrac"]')

    page.select_option("#workbench-hardware-palette-action", "apply-binding")
    page.click('[data-hardware-palette-id="lru:etrac"]')
    page.click("#workbench-export-draft-btn")
    lru_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in lru_draft["nodes"] if node["id"] == "logic1")

    assert logic1["hardware_binding"]["hardware_id"] == "etrac"
    assert logic1["hardware_binding"]["source_ref"].startswith("docs/thrust_reverser/")
    assert lru_draft["hardware_palette"]["source"] == "read_only_hardware_evidence_api"
    assert lru_draft["hardware_palette"]["truth_effect"] == "none"
    assert lru_draft["controller_truth_modified"] is False

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.select_option("#workbench-port-value-type", "number")
    page.click("#workbench-apply-port-contract-btn")
    page.locator('[data-hardware-palette-id^="signal:SW1"]').first.click()
    page.click("#workbench-export-draft-btn")
    edge_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    edge = next(item for item in edge_draft["edges"] if item["id"] == "edge_logic1_logic2")
    assert edge["signal_id"] == "SW1"
    assert edge["value_type"] == "number"
    assert edge["hardware_binding"]["hardware_id"] == "external_throttle_resolver"
    assert edge["hardware_binding"]["truth_effect"] == "none"

    page.select_option("#workbench-hardware-palette-action", "create-node")
    page.locator('[data-hardware-palette-id^="signal:SW1"]').first.click()
    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["hardware_palette"]["truth_effect"] == "none"
    assert archive["checksums"]["hardware_palette_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_typed_port_contract_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-port-input-signal", "logic1_candidate_input")
    page.fill("#workbench-port-output-signal", "logic1_candidate_output")
    page.select_option("#workbench-port-value-type", "number")
    page.fill("#workbench-port-unit", "deg")
    page.check("#workbench-port-required")
    page.click("#workbench-apply-port-contract-btn")
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", json.dumps(draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_logic1 = next(node for node in round_trip["nodes"] if node["id"] == "logic1")
    assert round_trip_logic1["port_contract"]["output_signal_id"] == "logic1_candidate_output"
    assert round_trip["port_contract_summary"]["truth_effect"] == "none"

    page.click("#workbench-prepare-archive-btn")
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

    page.fill("#workbench-interface-hardware-id", "TR-LRU-MATRIX-A")
    page.fill("#workbench-interface-cable", "CBL-MATRIX-A")
    page.fill("#workbench-interface-connector", "J-MATRIX-A")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-MATRIX-A:J-MATRIX-A")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.fill("#workbench-interface-hardware-id", "TR-LRU-MATRIX-B")
    page.fill("#workbench-interface-cable", "CBL-MATRIX-B")
    page.fill("#workbench-interface-connector", "J-MATRIX-B")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.click("#workbench-export-interface-matrix-btn")
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

    page.click("#workbench-generate-handoff-btn")
    assert "Interface matrix:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Interface matrix:" in page.locator("#workbench-linear-handoff-output").input_value()

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["interface_matrix"]["row_count"] == matrix["row_count"]
    assert draft["interface_matrix"]["truth_effect"] == "none"
    assert draft["changerequest_proof_packet"]["interface_matrix_summary"]["row_count"] == matrix["row_count"]

    page.click("#workbench-prepare-archive-btn")
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

    page.fill("#workbench-interface-hardware-id", "TR-LRU-BEFORE")
    page.fill("#workbench-interface-cable", "CBL-BEFORE")
    page.fill("#workbench-interface-connector", "J-BEFORE")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-BEFORE:J-BEFORE")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.fill("#workbench-interface-hardware-id", "EDGE-LRU-BEFORE")
    page.fill("#workbench-interface-cable", "EDGE-CBL-BEFORE")
    page.fill("#workbench-interface-connector", "EDGE-J-BEFORE")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.click("#workbench-export-interface-matrix-btn")
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
    page.fill("#workbench-interface-matrix-output", json.dumps(matrix))
    page.click("#workbench-apply-interface-matrix-btn")
    status = page.locator("#workbench-interface-matrix-status").inner_text()
    assert "Applied 2 matrix row(s), skipped 1" in status

    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    archive_node = next(row for row in archive["interface_matrix"]["rows"] if row["owner_kind"] == "node" and row["owner_id"] == "logic1")
    assert archive_node["hardware_id"] == "TR-LRU-APPLIED"
    assert archive["checksums"]["interface_matrix_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False

    rejected = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    rejected["rows"][0]["truth_effect"] = "certified"
    rejected["rows"][0]["hardware_id"] = "SHOULD-NOT-APPLY"
    page.fill("#workbench-interface-matrix-output", json.dumps(rejected))
    page.click("#workbench-apply-interface-matrix-btn")
    assert "truth_effect must be none" in page.locator("#workbench-interface-matrix-status").inner_text()
    page.click("#workbench-export-draft-btn")
    after_reject = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in after_reject["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-APPLIED"


def test_workbench_operation_catalog_adds_typed_sandbox_node(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="between"]')
    assert page.locator("#workbench-op-catalog-status").inner_text() == "BTW · number"
    page.click('[data-editor-tool="node"]')
    page.click("#workbench-export-draft-btn")
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
        "and",
        "or",
        "compare",
        "between",
        "delay",
        "latch",
    }

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["operation_catalog"]["selected_op"] == "between"
    assert archive["operation_catalog"]["truth_effect"] == "none"
    assert archive["checksums"]["operation_catalog_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_rule_parameter_round_trips_through_export_import_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-op-catalog-op="between"]')
    page.click('[data-editor-tool="node"]')
    page.fill("#workbench-rule-name", "draft_tra_window")
    page.fill("#workbench-rule-source-signal", "tra_deg")
    page.select_option("#workbench-rule-comparison", "between_lower_inclusive")
    page.fill("#workbench-rule-threshold", "[-32,0]")
    page.click("#workbench-apply-rule-parameter-btn")
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", json.dumps(draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    round_trip = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    round_trip_node = next(item for item in round_trip["nodes"] if item["id"] == "draft_node_1")
    assert round_trip_node["rules"][0]["threshold_value"] == [-32, 0]
    assert round_trip["rule_parameter_summary"]["total_rules"] == 1

    page.click("#workbench-prepare-archive-btn")
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

    page.select_option("#workbench-sandbox-scenario-select", "sw1_stuck_at_touchdown")
    page.fill("#workbench-custom-snapshot-json", '{"tra_deg": -12}')
    page.click('[data-op-catalog-op="compare"]')
    page.click('[data-editor-tool="node"]')
    page.fill("#workbench-draft-snapshot-name", "compare-candidate-a")
    page.click("#workbench-save-draft-snapshot-btn")
    assert "compare-candidate-a" in page.locator("#workbench-draft-snapshot-select").inner_text()

    page.click('[data-editor-tool="node"]')
    page.click("#workbench-export-draft-btn")
    mutated = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert len([node for node in mutated["nodes"] if node["id"].startswith("draft_node_")]) == 2

    page.click("#workbench-restore-draft-snapshot-btn")
    page.click("#workbench-export-draft-btn")
    restored = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    draft_nodes = [node for node in restored["nodes"] if node["id"].startswith("draft_node_")]
    assert errors == [], f"page JS errors: {errors}"
    assert [node["id"] for node in draft_nodes] == ["draft_node_1"]
    assert restored["selected_scenario_id"] == "sw1_stuck_at_touchdown"
    assert restored["custom_snapshot"] == {"tra_deg": -12}
    assert restored["draft_snapshot_manifest"]["snapshot_count"] == 1
    assert restored["draft_snapshot_manifest"]["truth_effect"] == "none"

    page.click("#workbench-prepare-archive-btn")
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
    page.fill("#workbench-rule-name", "draft_tra_compare")
    page.fill("#workbench-rule-source-signal", "tra_deg")
    page.select_option("#workbench-rule-comparison", ">=")
    page.fill("#workbench-rule-threshold", "-11.74")
    page.click("#workbench-apply-rule-parameter-btn")
    page.click("#workbench-interface-hardware-id")
    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "draft_node_1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    page.locator('[data-editable-node-id="draft_node_1"]').click()
    page.keyboard.press("Control+D")
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
    undone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in undone["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1"
    ]

    page.keyboard.press("Control+Shift+Z")
    page.click("#workbench-export-draft-btn")
    redone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in redone["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1",
        "draft_node_2",
    ]

    page.keyboard.press("Delete")
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
    removed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert [node["id"] for node in removed["nodes"] if node["id"].startswith("draft_node_")] == [
        "draft_node_1",
        "draft_node_2",
    ]

    page.keyboard.press("Control+Z")
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
    before = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    before_positions = {
        node["id"]: (node["x"], node["y"])
        for node in before["nodes"]
        if node["id"] in {"logic3", "draft_node_1", "draft_node_2"}
    }

    page.locator('[data-editable-node-id="draft_node_1"]').scroll_into_view_if_needed()
    draft_node_1 = page.locator('[data-editable-node-id="draft_node_1"]').bounding_box()
    draft_node_2 = page.locator('[data-editable-node-id="draft_node_2"]').bounding_box()
    assert draft_node_1 is not None
    assert draft_node_2 is not None
    left = min(draft_node_1["x"], draft_node_2["x"]) - 44
    top = min(draft_node_1["y"], draft_node_2["y"]) - 44
    right = max(draft_node_1["x"] + draft_node_1["width"], draft_node_2["x"] + draft_node_2["width"]) + 44
    bottom = max(draft_node_1["y"] + draft_node_1["height"], draft_node_2["y"] + draft_node_2["height"]) + 44
    page.mouse.move(left, top)
    page.mouse.down()
    page.mouse.move(right, bottom, steps=8)
    page.mouse.up()

    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-multi-selected") == "true"
    assert page.locator('[data-editable-node-id="draft_node_2"]').get_attribute("data-multi-selected") == "true"

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

    page.click("#workbench-export-draft-btn")
    moved = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    moved_positions = {
        node["id"]: (node["x"], node["y"])
        for node in moved["nodes"]
        if node["id"] in {"logic3", "draft_node_1", "draft_node_2"}
    }

    assert errors == [], f"page JS errors: {errors}"
    assert set(moved["selected_node_ids"]) >= {"draft_node_1", "draft_node_2"}
    assert moved_positions["draft_node_1"] != before_positions["draft_node_1"]
    assert moved_positions["draft_node_2"] != before_positions["draft_node_2"]
    assert moved_positions["logic3"] == before_positions["logic3"]
    assert moved["truth_level_impact"] == "none"

    page.keyboard.press("Control+Z")
    page.click("#workbench-export-draft-btn")
    undone = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    undone_positions = {
        node["id"]: (node["x"], node["y"])
        for node in undone["nodes"]
        if node["id"] in {"draft_node_1", "draft_node_2"}
    }
    assert undone_positions["draft_node_1"] == before_positions["draft_node_1"]
    assert undone_positions["draft_node_2"] == before_positions["draft_node_2"]


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
    source_handle.click()
    assert source_handle.get_attribute("data-port-handle-armed") == "true"
    target_handle.click()

    page.click("#workbench-export-draft-btn")
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
    assert edge["hardware_binding"]["truth_effect"] == "none"
    assert draft["port_contract_summary"]["edge_contracts"] >= 1
    assert draft["truth_level_impact"] == "none"

    source_handle.click()
    target_handle.click()
    page.click("#workbench-export-draft-btn")
    after_duplicate_attempt = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    matching_edges = [
        item for item in after_duplicate_attempt["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    ]
    assert len(matching_edges) == 1


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
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
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

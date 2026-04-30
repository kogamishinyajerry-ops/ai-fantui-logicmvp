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
    page.mouse.move(right, bottom)
    page.mouse.up()

    assert page.locator('[data-editable-node-id="draft_node_1"]').get_attribute("data-multi-selected") == "true"
    assert page.locator('[data-editable-node-id="draft_node_2"]').get_attribute("data-multi-selected") == "true"

    draft_node_1 = page.locator('[data-editable-node-id="draft_node_1"]').bounding_box()
    assert draft_node_1 is not None
    page.mouse.move(draft_node_1["x"] + draft_node_1["width"] / 2, draft_node_1["y"] + draft_node_1["height"] / 2)
    page.mouse.down()
    page.mouse.move(draft_node_1["x"] + draft_node_1["width"] / 2 + 90, draft_node_1["y"] + draft_node_1["height"] / 2 + 45)
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

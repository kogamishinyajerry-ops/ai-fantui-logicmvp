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


def test_workbench_connector_pin_map_applies_round_trips_and_archives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-PIN")
    page.fill("#workbench-interface-cable", "CBL-TR-PIN")
    page.fill("#workbench-interface-connector", "J-PIN")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-PIN:J-PIN")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.click("#workbench-export-connector-pin-map-btn")
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
    page.fill("#workbench-connector-pin-map-output", json.dumps(pin_map))
    page.click("#workbench-apply-connector-pin-map-btn")
    assert "Applied 1 connector/pin row" in page.locator("#workbench-connector-pin-map-status").inner_text()

    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", json.dumps(draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-connector-pin-map-btn")
    imported_map = json.loads(page.locator("#workbench-connector-pin-map-output").input_value())
    assert imported_map["rows"][0]["pin_local"] == "A1"
    assert imported_map["rows"][0]["pin_peer"] == "B7"

    page.click("#workbench-prepare-archive-btn")
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
    page.fill("#workbench-hardware-interface-design-output", json.dumps(invalid_payload))
    page.click("#workbench-validate-hardware-interface-design-btn")
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
    page.fill("#workbench-hardware-interface-design-output", json.dumps(valid_payload))
    page.click("#workbench-apply-hardware-interface-design-btn")
    page.wait_for_function(
        """
        () => document.getElementById('workbench-hardware-interface-design-status')
          ?.textContent.includes('Applied hardware/interface design')
        """
    )

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert draft["hardware_interface_designer"]["kind"] == "well-harness-editable-hardware-interface-design"
    assert draft["hardware_interface_designer"]["runtime_truth_effect"] == "none"
    assert draft["hardware_interface_designer"]["bindings"][0]["id"] == "BIND-A-B"
    assert draft["hardware_interface_designer_validation"]["status"] == "pass"
    assert draft["hardware_interface_designer_validation"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", json.dumps(stale_validation_draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    recomputed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert recomputed["hardware_interface_designer_validation"]["counts"]["lrus"] == 2

    page.click("#workbench-prepare-archive-btn")
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

    page.wait_for_selector("#workbench-hardware-evidence-v2")
    assert page.locator("#workbench-hardware-evidence-v2-target").inner_text() == "node:logic1"

    page.fill("#workbench-interface-hardware-id", "TR-LRU-V2")
    page.fill("#workbench-interface-cable", "CBL-V2")
    page.fill("#workbench-interface-connector", "J-V2")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-V2:J-V2")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    node_fields = page.locator("#workbench-hardware-evidence-v2-fields").inner_text()
    assert "TR-LRU-V2" in node_fields
    assert "J-V2" in node_fields
    assert "LOCAL PIN" in node_fields
    assert "evidence_gap" in node_fields
    assert "truth_effect: none" in node_fields
    assert "1 row(s)" in page.locator("#workbench-hardware-evidence-v2-pin-rows").inner_text()

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.fill("#workbench-interface-hardware-id", "EDGE-LRU-V2")
    page.fill("#workbench-interface-cable", "EDGE-CBL-V2")
    page.fill("#workbench-interface-connector", "EDGE-J-V2")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "logic2:in")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    assert page.locator("#workbench-hardware-evidence-v2-target").inner_text() == "edge:edge_logic1_logic2"
    edge_fields = page.locator("#workbench-hardware-evidence-v2-fields").inner_text()
    assert "EDGE-LRU-V2" in edge_fields
    assert "EDGE-J-V2" in edge_fields
    assert "LOCAL PIN" in edge_fields
    assert "evidence_gap" in edge_fields

    page.click("#workbench-generate-handoff-btn")
    assert "Hardware evidence v2:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Hardware evidence v2:" in page.locator("#workbench-linear-handoff-output").input_value()

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["hardware_evidence_v2"]["target_kind"] == "edge"
    assert draft["hardware_evidence_v2"]["target_id"] == "edge_logic1_logic2"
    assert draft["hardware_evidence_v2"]["selected_binding"]["hardware_id"] == "EDGE-LRU-V2"
    assert draft["hardware_evidence_v2"]["truth_effect"] == "none"

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert archive["hardware_evidence_v2"]["target_kind"] == "edge"
    assert archive["hardware_evidence_v2"]["truth_effect"] == "none"
    assert archive["changerequest_proof_packet"]["hardware_evidence_v2_summary"]["target"] == "edge:edge_logic1_logic2"
    assert archive["checksums"]["hardware_evidence_v2_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_selected_debug_timeline_tracks_selection_diff_and_archive(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.wait_for_selector("#workbench-selected-debug-timeline")
    assert page.locator("#workbench-selected-debug-target").inner_text() == "node:logic1"
    assert page.locator("#workbench-selected-debug-verdict").inner_text() == "not_run"
    assert page.locator("#workbench-selected-debug-link-status").inner_text() == "selection_only"

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.fill("#workbench-interface-hardware-id", "EDGE-LRU-DEBUG")
    page.fill("#workbench-interface-cable", "EDGE-CBL-DEBUG")
    page.fill("#workbench-interface-connector", "EDGE-J-DEBUG")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "logic2:in")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    assert page.locator("#workbench-selected-debug-target").inner_text() == "edge:edge_logic1_logic2"
    assert "EDGE-LRU-DEBUG" in page.locator("#workbench-selected-debug-hardware").inner_text()
    assert "logic1 -> logic2" in page.locator("#workbench-selected-debug-context").inner_text()

    page.select_option("#workbench-sandbox-scenario-select", "nominal_landing")
    page.click("#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-selected-debug-verdict')?.textContent.trim();
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

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["selected_debug_timeline"]["target_kind"] == "edge"
    assert draft["selected_debug_timeline"]["target_id"] == "edge_logic1_logic2"
    assert draft["selected_debug_timeline"]["scenario_id"] == "nominal_landing"
    assert draft["selected_debug_timeline"]["hardware_overlay"]["hardware_id"] == "EDGE-LRU-DEBUG"
    assert draft["selected_debug_timeline"]["truth_effect"] == "none"

    page.click("#workbench-generate-handoff-btn")
    assert "Selected debug timeline:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Selected debug timeline:" in page.locator("#workbench-linear-handoff-output").input_value()

    page.click("#workbench-prepare-archive-btn")
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

    page.wait_for_selector("#workbench-diff-review-v2")
    assert page.locator("#workbench-diff-review-v2-status").inner_text() == "not_run"
    assert page.locator("#workbench-diff-review-v2-readiness").inner_text() == "run_required"
    assert page.locator("#workbench-diff-review-v2-archive-state").inner_text() == "not_archive_ready"
    assert page.locator("#workbench-diff-review-v2-claim").inner_text() == "none"

    page.click("#workbench-derive-draft-btn")
    page.select_option("#workbench-sandbox-scenario-select", "nominal_landing")
    page.click("#workbench-run-sandbox-btn")
    page.wait_for_function(
        """
        () => {
          const verdict = document.getElementById('workbench-diff-review-v2-status')?.textContent.trim();
          return ['equivalent', 'divergent', 'invalid_model', 'invalid_scenario'].includes(verdict);
        }
        """
    )
    verdict = page.locator("#workbench-diff-review-v2-status").inner_text()
    readiness = page.locator("#workbench-diff-review-v2-readiness").inner_text()
    expected_readiness = {
        "equivalent": "ready",
        "divergent": "review_required",
        "invalid_model": "blocked",
        "invalid_scenario": "blocked",
    }[verdict]
    assert readiness == expected_readiness
    assert page.locator("#workbench-diff-review-v2-archive-state").inner_text() == "archive_ready"
    assert page.locator("#workbench-diff-review-v2-scenario").inner_text() == "nominal_landing"
    assert (
        page.locator("#workbench-diff-review-v2")
        .get_attribute("data-review-truth-effect")
        == "none"
    )

    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-generate-handoff-btn")
    assert "Diff review v2:" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Diff review v2:" in page.locator("#workbench-linear-handoff-output").input_value()

    page.click("#workbench-prepare-archive-btn")
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
    assert "Applied 2 matrix row(s), deselected 0, no-op 0, skipped 1" in status

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


def test_workbench_interface_matrix_csv_tsv_bridge_round_trips_sandbox_rows(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-CSV-BEFORE")
    page.fill("#workbench-interface-cable", "CBL-CSV-BEFORE")
    page.fill("#workbench-interface-connector", "J-CSV-BEFORE")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-CSV-BEFORE:J-CSV-BEFORE")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.click("#workbench-export-interface-matrix-btn")
    page.click("#workbench-export-interface-matrix-csv-btn")
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
    page.fill("#workbench-interface-matrix-csv-output", buffer.getvalue())
    page.click("#workbench-import-interface-matrix-csv-btn")
    report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert report["status"] == "warn"
    assert report["truth_effect"] == "none"
    assert report["evidence_gap_field_count"] >= 1
    page.click("#workbench-apply-interface-matrix-btn")
    assert "Applied 1 matrix row(s)" in page.locator("#workbench-interface-matrix-status").inner_text()
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-interface-matrix-csv-output", f"{tsv_header}\n{tsv_row}\n")
    page.click("#workbench-import-interface-matrix-csv-btn")
    assert "Matrix validation warn" in page.locator("#workbench-interface-matrix-status").inner_text()
    page.click("#workbench-apply-interface-matrix-btn")
    page.click("#workbench-export-draft-btn")
    tsv_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_tsv = next(node for node in tsv_draft["nodes"] if node["id"] == "logic1")
    assert logic1_tsv["hardware_binding"]["hardware_id"] == "TR-LRU-TSV-APPLIED"
    assert logic1_tsv["hardware_binding"]["cable"] == "evidence_gap"
    assert logic1_tsv["hardware_binding"]["connector"] == "J-TSV-APPLIED"
    assert logic1_tsv["hardware_binding"]["truth_effect"] == "none"

    rejected_row = tsv_row.replace("TR-LRU-TSV-APPLIED", "SHOULD-NOT-APPLY", 1).replace("\tnone\t", "\tcertified\t")
    page.fill("#workbench-interface-matrix-csv-output", f"{tsv_header}\n{rejected_row}\n")
    page.click("#workbench-import-interface-matrix-csv-btn")
    failed_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert failed_report["status"] == "fail"
    assert failed_report["truth_effect_violation_count"] >= 1
    page.click("#workbench-apply-interface-matrix-btn")
    assert "Matrix validation failed" in page.locator("#workbench-interface-matrix-status").inner_text()
    page.click("#workbench-export-draft-btn")
    rejected_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in rejected_draft["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-TSV-APPLIED"


def test_workbench_interface_matrix_validation_previews_without_mutating_draft(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-PREVIEW-BEFORE")
    page.fill("#workbench-interface-cable", "CBL-PREVIEW-BEFORE")
    page.fill("#workbench-interface-connector", "J-PREVIEW-BEFORE")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-PREVIEW-BEFORE:J-PREVIEW-BEFORE")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.locator('[data-editable-edge-id="edge_logic1_logic2"]').dispatch_event("click")
    page.fill("#workbench-interface-hardware-id", "EDGE-LRU-PREVIEW-BEFORE")
    page.fill("#workbench-interface-cable", "EDGE-CBL-PREVIEW-BEFORE")
    page.fill("#workbench-interface-connector", "EDGE-J-PREVIEW-BEFORE")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "logic2:in:ui_edge:logic1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    page.click("#workbench-export-interface-matrix-btn")
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

    page.fill("#workbench-interface-matrix-output", json.dumps(matrix))
    page.click("#workbench-validate-interface-matrix-btn")
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

    page.click("#workbench-export-draft-btn")
    preview_only_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1 = next(node for node in preview_only_draft["nodes"] if node["id"] == "logic1")
    assert logic1["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-BEFORE"
    assert preview_only_draft["interface_matrix_validation"]["status"] == "warn"

    page.click("#workbench-generate-handoff-btn")
    assert "Interface matrix validation: warn" in page.locator("#workbench-pr-proof-output").input_value()
    assert "Interface matrix validation:" in page.locator("#workbench-linear-handoff-output").input_value()

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["interface_matrix_validation"]["status"] == "warn"
    assert archive["checksums"]["interface_matrix_validation_checksum"]
    assert archive["red_line_metadata"]["truth_level_impact"] == "none"

    page.click("#workbench-apply-interface-matrix-btn")
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

    page.click("#workbench-export-draft-btn")
    after_apply = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_apply = next(node for node in after_apply["nodes"] if node["id"] == "logic1")
    edge_after_apply = next(item for item in after_apply["edges"] if item["id"] == "edge_logic1_logic2")
    assert logic1_after_apply["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"
    assert edge_after_apply["hardware_binding"]["hardware_id"] == "EDGE-LRU-PREVIEW-BEFORE"

    page.click("#workbench-apply-interface-matrix-btn")
    assert "Applied 0 matrix row(s), deselected 0, no-op 2, skipped 0" in page.locator("#workbench-interface-matrix-status").inner_text()
    second_apply_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert second_apply_report["changed_row_count"] == 0
    assert second_apply_report["noop_row_count"] >= 2
    page.click("#workbench-export-draft-btn")
    after_second_apply = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_second_apply = next(node for node in after_second_apply["nodes"] if node["id"] == "logic1")
    assert logic1_after_second_apply["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"

    rejected = json.loads(page.locator("#workbench-interface-matrix-output").input_value())
    rejected["rows"][0]["truth_effect"] = "certified"
    rejected["rows"][0]["hardware_id"] = "SHOULD-NOT-APPLY"
    page.fill("#workbench-interface-matrix-output", json.dumps(rejected))
    page.click("#workbench-validate-interface-matrix-btn")
    failed_report = json.loads(page.locator("#workbench-interface-matrix-validation-output").input_value())
    assert failed_report["status"] == "fail"
    assert failed_report["truth_effect_violation_count"] >= 1
    assert review.get_attribute("data-review-state") == "fail"
    reject_review = review.locator('[data-interface-matrix-review-owner-id="logic1"]')
    assert reject_review.get_attribute("data-row-status") == "reject"
    assert reject_review.get_attribute("data-row-action") == "none"
    page.click("#workbench-apply-interface-matrix-btn")
    assert "Matrix validation failed" in page.locator("#workbench-interface-matrix-status").inner_text()
    page.click("#workbench-export-draft-btn")
    after_reject = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    logic1_after_reject = next(node for node in after_reject["nodes"] if node["id"] == "logic1")
    assert logic1_after_reject["hardware_binding"]["hardware_id"] == "TR-LRU-PREVIEW-EDITED"


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
        "input",
        "output",
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


def test_workbench_empty_canvas_palette_round_trips_sandbox_primitives(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click("#workbench-start-empty-draft-btn")
    page.click("#workbench-export-draft-btn")
    empty_draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert errors == [], f"page JS errors: {errors}"
    assert empty_draft["canvas_authoring_mode"] == "empty_authoring"
    assert empty_draft["nodes"] == []
    assert empty_draft["edges"] == []
    assert empty_draft["editable_graph_document"]["node_count"] == 0
    assert empty_draft["editable_graph_document"]["truth_effect"] == "none"

    page.click('[data-op-catalog-op="input"]')
    page.click('[data-editor-tool="node"]')
    page.click('[data-op-catalog-op="output"]')
    page.click('[data-editor-tool="node"]')
    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    node_ops = {node["id"]: node["op"] for node in draft["nodes"]}

    assert draft["canvas_authoring_mode"] == "empty_authoring"
    assert node_ops == {"draft_node_1": "input", "draft_node_2": "output"}
    assert all(node_id not in node_ops for node_id in ["logic1", "logic2", "logic3", "logic4"])
    assert draft["workspace_document"]["truth_effect"] == "none"
    assert draft["workspace_document"]["action_count"] >= 3
    assert draft["editable_graph_document"]["node_count"] == 2

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_ops = {node["id"]: node["op"] for node in imported["nodes"]}
    assert imported["canvas_authoring_mode"] == "empty_authoring"
    assert imported_ops == node_ops
    assert imported["editable_graph_document"]["node_count"] == 2

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["canvas_authoring_mode"] == "empty_authoring"
    assert archive["editable_graph_document"]["node_count"] == 2
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


def test_workbench_component_library_inserts_reusable_sandbox_template(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    assert "2ST" in page.locator("#workbench-component-library-status").inner_text()
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_nodes = [node for node in imported["nodes"] if node["id"].startswith("draft_node_")]
    assert [node["component_template"]["template_id"] for node in imported_nodes] == [
        "two_stage_interlock",
        "two_stage_interlock",
    ]

    page.click("#workbench-prepare-archive-btn")
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
    page.click("#workbench-export-draft-btn")
    before_group = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    before_edge_ids = [edge["id"] for edge in before_group["edges"]]
    before_port_ids = [port["id"] for port in before_group["typed_ports"]]

    page.fill("#workbench-subsystem-name", "Deploy interlock")
    page.click("#workbench-create-subsystem-btn")
    page.click("#workbench-export-draft-btn")
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

    page.fill("#workbench-subsystem-name", "Deploy interlock v2")
    page.click("#workbench-rename-subsystem-btn")
    page.click("#workbench-export-draft-btn")
    renamed = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert renamed["subsystem_groups"][0]["name"] == "Deploy interlock v2"
    assert all(
        node["subsystem_group"]["name"] == "Deploy interlock v2"
        for node in renamed["nodes"]
        if node["id"].startswith("draft_node_")
    )

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["subsystem_groups"][0]["name"] == "Deploy interlock v2"

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["subsystem_groups"][0]["truth_effect"] == "none"
    assert archive["checksums"]["subsystem_groups_checksum"]

    page.click("#workbench-ungroup-subsystem-btn")
    page.click("#workbench-export-draft-btn")
    ungrouped = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert ungrouped["subsystem_groups"] == []
    assert [edge["id"] for edge in ungrouped["edges"]] == before_edge_ids
    assert [port["id"] for port in ungrouped["typed_ports"]] == before_port_ids
    assert all("subsystem_group" not in node for node in ungrouped["nodes"] if node["id"].startswith("draft_node_"))

    page.keyboard.press("Control+Z")
    page.click("#workbench-export-draft-btn")
    undo = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert undo["subsystem_groups"][0]["name"] == "Deploy interlock v2"

    page.keyboard.press("Control+Shift+Z")
    page.click("#workbench-export-draft-btn")
    redo = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert redo["subsystem_groups"] == []
    assert redo["truth_level_impact"] == "none"


def test_workbench_captures_and_reinserts_subsystem_template(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_error_capture(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.click('[data-component-template-id="two_stage_interlock"]')
    page.fill("#workbench-subsystem-name", "Reusable deploy cell")
    page.click("#workbench-create-subsystem-btn")
    page.click("#workbench-capture-subsystem-template-btn")
    assert "captured" in page.locator("#workbench-component-library-status").inner_text().lower()

    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-insert-captured-template-btn")
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["component_library"]["captured_templates"][0]["id"] == template_id
    assert imported["component_library"]["captured_templates"][0]["truth_effect"] == "none"

    page.click("#workbench-prepare-archive-btn")
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
    page.fill("#workbench-subsystem-name", "Ported deploy cell")
    page.click("#workbench-create-subsystem-btn")

    page.select_option("#workbench-subsystem-interface-direction", "input")
    page.fill("#workbench-subsystem-interface-label", "Deploy request")
    page.fill("#workbench-subsystem-interface-signal-id", "deploy_request_cmd")
    page.select_option("#workbench-subsystem-interface-value-type", "boolean")
    page.select_option("#workbench-subsystem-interface-evidence-status", "ui_draft")
    page.click("#workbench-add-subsystem-interface-port-btn")

    page.select_option("#workbench-subsystem-interface-direction", "output")
    page.fill("#workbench-subsystem-interface-label", "Deploy allowed")
    page.fill("#workbench-subsystem-interface-signal-id", "deploy_allowed_status")
    page.select_option("#workbench-subsystem-interface-value-type", "boolean")
    page.select_option("#workbench-subsystem-interface-evidence-status", "evidence_gap")
    page.click("#workbench-add-subsystem-interface-port-btn")

    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["subsystem_groups"][0]["interface_contracts"][0]["label"] == "Deploy request"

    page.click("#workbench-capture-subsystem-template-btn")
    page.click("#workbench-insert-captured-template-btn")
    page.click("#workbench-export-draft-btn")
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

    page.click("#workbench-prepare-archive-btn")
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
    page.fill("#workbench-subsystem-name", "Documented deploy cell")
    page.click("#workbench-create-subsystem-btn")
    page.select_option("#workbench-subsystem-interface-direction", "input")
    page.fill("#workbench-subsystem-interface-label", "Deploy request")
    page.fill("#workbench-subsystem-interface-signal-id", "deploy_request_cmd")
    page.click("#workbench-add-subsystem-interface-port-btn")

    page.click("#workbench-export-draft-btn")
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
    assert page.locator("#workbench-workspace-document-revision").inner_text() == workspace_document["revision_id"]

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["workspace_document"]["document_id"] == workspace_document["document_id"]
    assert imported["workspace_document"]["action_count"] >= workspace_document["action_count"]

    page.click('[data-editor-tool="undo"]')
    page.click('[data-editor-tool="redo"]')
    page.click("#workbench-export-draft-btn")
    revised = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert revised["workspace_document"]["revision_id"].startswith("ui_draft_")
    assert revised["workspace_document"]["undo_depth"] >= 1

    page.click("#workbench-prepare-archive-btn")
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
    page.fill("#workbench-subsystem-name", "Canonical graph cell")
    page.click("#workbench-create-subsystem-btn")
    page.select_option("#workbench-subsystem-interface-direction", "output")
    page.fill("#workbench-subsystem-interface-label", "Deploy command")
    page.fill("#workbench-subsystem-interface-signal-id", "deploy_cmd")
    page.click("#workbench-add-subsystem-interface-port-btn")
    page.click("#workbench-export-draft-btn")
    exported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    graph = exported["editable_graph_document"]

    assert errors == [], f"page JS errors: {errors}"
    assert graph["kind"] == "well-harness-workbench-editable-graph-document"
    assert graph["version"] == "workbench-editable-graph-document.v1"
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_graph = imported["editable_graph_document"]
    assert imported_graph["truth_effect"] == "none"
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

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    first_archive_checksum = archive["checksums"]["editable_graph_document_checksum"]
    page.click("#workbench-prepare-archive-btn")
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
    page.click("#workbench-export-draft-btn")
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

    page.fill("#workbench-draft-json-buffer", json.dumps(draft))
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-insert-captured-template-btn")
    page.click("#workbench-export-draft-btn")
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
    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_summary = imported["canvas_interaction_summary"]
    assert imported_summary["last_action"] in {"import_draft", "batch_duplicate_nodes"}
    assert imported_summary["node_count"] == summary["node_count"]
    assert imported_summary["edge_count"] == summary["edge_count"]
    assert imported_summary["truth_effect"] == "none"

    page.keyboard.press("Delete")
    page.click("#workbench-export-draft-btn")
    deleted = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert deleted["canvas_interaction_summary"]["last_action"] == "batch_remove_nodes"
    assert deleted["canvas_interaction_summary"]["selected_node_count"] == 1

    page.click("#workbench-prepare-archive-btn")
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
    assert edge_path.get_attribute("data-route-mode") == "orthogonal"
    assert page.locator(f'[data-editable-edge-label-id="{edge["id"]}"]').text_content().strip() == "draft_node_1:out -> draft_node_2:in"

    source_handle.click()
    target_handle.click()
    page.click("#workbench-export-draft-btn")
    after_duplicate_attempt = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    matching_edges = [
        item for item in after_duplicate_attempt["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    ]
    assert len(matching_edges) == 1

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    imported_edge = next(
        item for item in imported["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )
    assert imported_edge["edge_label"] == edge["edge_label"]
    assert imported_edge["route_metadata"] == edge["route_metadata"]

    page.locator(f'[data-editable-edge-id="{imported_edge["id"]}"]').dispatch_event("click")
    edge_detail = page.locator("#workbench-inspector-evidence-detail").inner_text()
    assert "Route mode" in edge_detail
    assert "orthogonal" in edge_detail
    page.click('[data-editor-tool="disconnect"]')
    page.click("#workbench-export-draft-btn")
    disconnected = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert not [
        item for item in disconnected["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    ]

    page.locator(
        '[data-port-handle-owner-id="draft_node_1"][data-port-handle-direction="out"]'
    ).click()
    page.locator(
        '[data-port-handle-owner-id="draft_node_2"][data-port-handle-direction="in"]'
    ).click()
    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    archived_edge = next(
        item for item in archive["model_json"]["edges"]
        if item["source"] == "draft_node_1" and item["target"] == "draft_node_2"
    )
    assert archived_edge["edge_label"] == "draft_node_1:out -> draft_node_2:in"
    assert archived_edge["route_metadata"]["truth_effect"] == "none"
    assert archive["port_compatibility_report"]["status"] == "pass"
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
    page.locator(
        '[data-port-handle-owner-id="draft_node_1"][data-port-handle-direction="out"]'
    ).click()
    page.locator(
        '[data-port-handle-owner-id="draft_node_2"][data-port-handle-direction="in"]'
    ).click()

    page.fill(
        "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    page.fill(
        "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": False},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    page.click("#workbench-run-test-bench-btn")
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

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["sandbox_test_bench"]["truth_effect"] == "none"
    assert draft["sandbox_test_run_report"]["assertion_status"] == "pass"
    assert draft["sandbox_test_run_report"]["truth_effect"] == "none"

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["sandbox_test_bench"]["assertion_count"] == 2
    assert imported["sandbox_test_run_report"]["assertion_status"] == "pass"

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["sandbox_test_bench"]["tick_count"] == 2
    assert archive["sandbox_test_run_report"]["assertion_status"] == "pass"
    assert archive["checksums"]["sandbox_test_bench_checksum"]
    assert archive["checksums"]["sandbox_test_run_report_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False


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
    page.fill(
        "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    page.fill(
        "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    page.click("#workbench-run-test-bench-btn")
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

    page.click("#workbench-export-draft-btn")
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
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["candidate_debugger_view"]["target"]["owner_key"] == "node:draft_node_1"
    assert imported["candidate_debugger_view"]["first_failing_assertion"]["status"] == "fail"

    page.click("#workbench-prepare-archive-btn")
    archive = json.loads(page.locator("#workbench-evidence-archive-output").input_value())
    assert archive["candidate_debugger_view"]["truth_effect"] == "none"
    assert archive["candidate_debugger_view"]["first_failing_assertion"]["target"] == "draft_node_1:out"
    assert archive["checksums"]["candidate_debugger_view_checksum"]
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
    page.fill(
        "#workbench-test-bench-inputs-json",
        json.dumps(
            [
                {"tick": 0, "inputs": {"draft_node_1:in": 2, "draft_node_1": 2}},
                {"tick": 1, "inputs": {"draft_node_1:in": 8, "draft_node_1": 8}},
            ]
        ),
    )
    page.fill(
        "#workbench-test-bench-assertions-json",
        json.dumps(
            [
                {"tick": 0, "target": "draft_node_1:out", "expected": True},
                {"tick": 1, "target": "draft_node_1:out", "expected": True},
            ]
        ),
    )
    page.click("#workbench-run-test-bench-btn")
    page.click("#workbench-run-preflight-btn")
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

    page.click("#workbench-export-draft-btn")
    draft = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert draft["preflight_analyzer_report"]["classification"] == "invalid_candidate"
    assert draft["preflight_analyzer_report"]["candidate_model_hash"] == report["candidate_model_hash"]

    draft_json = page.locator("#workbench-draft-json-buffer").input_value()
    page.fill("#workbench-draft-json-buffer", draft_json)
    page.click("#workbench-import-draft-btn")
    page.click("#workbench-export-draft-btn")
    imported = json.loads(page.locator("#workbench-draft-json-buffer").input_value())
    assert imported["preflight_analyzer_report"]["classification"] == "invalid_candidate"
    assert imported["preflight_analyzer_report"]["truth_effect"] == "none"

    page.click("#workbench-prepare-archive-btn")
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

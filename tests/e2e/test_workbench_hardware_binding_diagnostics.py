"""JER-187 — Hardware binding diagnostics contracts for /workbench exports.

Focus: diagnostics section visibility and recomputation behavior for sandbox-only
hardware/interface binding evidence. These are intentionally contract-level e2e
checks to catch regression in the workbench evidence artifact shape.
"""

# mypy: ignore-errors

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.e2e

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


def _goto_shell_workbench(page, url: str):
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("#workbench-identity", state="attached")
    page.wait_for_function(
        """
        () => typeof window.setWorkbenchIdentity === 'function'
          && document.getElementById('workbench-identity')
        """
    )


def _clear_local_draft(page):
    page.evaluate("() => window.localStorage.removeItem('well-harness-editable-workbench-draft-v1')")


def _export_draft(page, buffer_id: str = "#workbench-draft-json-buffer"):
    page.click("#workbench-export-draft-btn")
    return json.loads(page.locator(buffer_id).input_value())


def _import_draft(page, payload: dict, buffer_id: str = "#workbench-draft-json-buffer"):
    page.fill(buffer_id, json.dumps(payload, ensure_ascii=False, indent=2))
    page.click("#workbench-import-draft-btn")


def _prepare_archive(page, output_id: str = "#workbench-evidence-archive-output"):
    page.click("#workbench-prepare-archive-btn")
    page.wait_for_function(
        """
        () => {
          const output = document.getElementById('workbench-evidence-archive-output');
          return output && output.value.includes('well-harness-workbench-evidence-archive');
        }
        """
    )
    return json.loads(page.locator(output_id).input_value())


def _collect_diagnostics(payload):
    return payload.get("hardware_binding_diagnostics")


def _assert_truth_neutral(diags) -> None:
    if isinstance(diags, dict):
        if "truth_effect" in diags:
            assert diags["truth_effect"] == "none", diags
    elif isinstance(diags, list):
        for item in diags:
            if isinstance(item, dict) and "truth_effect" in item:
                assert item["truth_effect"] == "none", item


def _extract_diagnostic_text(value):
    texts = []
    if isinstance(value, str):
        texts.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            texts.extend(_extract_diagnostic_text(v))
    elif isinstance(value, list):
        for item in value:
            texts.extend(_extract_diagnostic_text(item))
    return texts


def _diagnostic_matches(diags, required):
    texts = " ".join(_extract_diagnostic_text(diags)).lower()
    return all(item in texts for item in required)


def _evidence_gap_metric_present(diags) -> bool:
    if isinstance(diags, dict):
        for key in diags:
            low = str(key).lower()
            val = diags[key]
            if "evidence" in low and "gap" in low and ("count" in low or "density" in low):
                if isinstance(val, (int, float)) and val >= 0:
                    return True
            if isinstance(val, (dict, list)):
                if _evidence_gap_metric_present(val):
                    return True
    if isinstance(diags, list):
        return any(_evidence_gap_metric_present(item) for item in diags)
    return False


def _with_duplicate_binding_payload(draft_payload: dict) -> dict:
    node_ids = {
        node.get("id")
        for node in draft_payload.get("nodes", [])
        if isinstance(node, dict) and node.get("id")
    }
    assert "logic1" in node_ids and "logic2" in node_ids, "base payload missing logic1/logic2 nodes"

    # Keep one baseline binding on logic1 so we still exercise UI-origin data.
    base_payload = dict(draft_payload)
    base_payload["nodes"] = draft_payload.get("nodes", [])
    base_payload["edges"] = [
        {
            "id": "edge_logic1_logic2",
            "source": "logic1",
            "target": "logic2",
            "signal_id": "dup_sig_a",
            "hardware_binding": {
                "hardware_id": "TR-LRU-001",
                "cable": "CBL-TR-A",
                "connector": "J1",
                "port_local": "logic1:out",
                "port_peer": "TR-LRU-001:J1",
                "evidence_status": "ui_draft",
            },
        },
        {
            # Duplicate owner_id -> should be surfaced as duplicate-owner diagnostics.
            "id": "edge_logic1_logic2",
            "source": "logic1",
            "target": "logic2",
            "signal_id": "dup_sig_b",
            "hardware_binding": {
                "hardware_id": "TR-LRU-001",
                "cable": "CBL-TR-B",
                "connector": "J1",
                "port_local": "logic1:out",
                "port_peer": "TR-LRU-001:J1",
                "evidence_status": "ui_draft",
            },
        },
        {
            # Same connector/port key as first binding; keep one evidence_gap field
            # so diagnostics can report evidence_gap density/count.
            "id": "edge_logic1_logic2_gap",
            "source": "logic1",
            "target": "logic2",
            "signal_id": "gap_probe",
            "hardware_binding": {
                "hardware_id": "TR-LRU-001",
                "cable": "evidence_gap",
                "connector": "J1",
                "port_local": "logic1:out",
                "port_peer": "TR-LRU-001:J1",
                "evidence_status": "ui_draft",
            },
        },
    ]
    base_payload.pop("hardware_bindings", None)
    base_payload.pop("binding_coverage", None)
    base_payload.pop("checksums", None)
    return base_payload


def _stable_diagnostics_equal(a, b) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_workbench_export_and_archive_include_hardware_binding_diagnostics(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    draft = _export_draft(page)
    diagnostics = _collect_diagnostics(draft)
    assert diagnostics is not None, "workbench export missing hardware_binding_diagnostics"
    _assert_truth_neutral(diagnostics)

    archive = _prepare_archive(page)
    archive_diagnostics = _collect_diagnostics(archive)
    assert archive_diagnostics is not None, "workbench archive missing hardware_binding_diagnostics"
    _assert_truth_neutral(archive_diagnostics)
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_hardware_binding_diagnostics_detect_duplicate_owner_reuse_and_gap_density(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    # Seed one baseline binding and then inject a crafted duplicate/reuse/evidence-gap payload.
    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    diagnostic_payload["edges"][1]["source"] = "logic2"
    diagnostic_payload["edges"][1]["target"] = "logic3"
    _import_draft(page, diagnostic_payload)

    draft_round = _export_draft(page)
    diagnostics = _collect_diagnostics(draft_round)
    assert diagnostics is not None, "imported payload did not recompute diagnostics"
    _assert_truth_neutral(diagnostics)

    # Duplicate owner detection.
    assert _diagnostic_matches(diagnostics, ("duplicate", "owner")), (
        f"missing duplicate owner detection in diagnostics: {diagnostics}"
    )

    # Connector/port/interface key reuse detection.
    assert _diagnostic_matches(diagnostics, ("connector", "port")), (
        f"missing connector/port reuse detection in diagnostics: {diagnostics}"
    )
    assert "reuse" in " ".join(_extract_diagnostic_text(diagnostics)).lower() or _diagnostic_matches(
        diagnostics, ("shared",),
    ), f"missing key reuse signal in diagnostics: {diagnostics}"

    # Evidence-gap density / count detection.
    assert _evidence_gap_metric_present(diagnostics), (
        f"missing evidence_gap density/count metric in diagnostics: {diagnostics}"
    )
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_duplicate_edge_id_interaction_uses_edge_instance_index(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    diagnostic_payload["edges"][1]["source"] = "logic2"
    diagnostic_payload["edges"][1]["target"] = "logic3"
    _import_draft(page, diagnostic_payload)

    page.locator('[data-editable-edge-index="1"]').click(force=True)
    assert page.locator("#workbench-edge-signal-id").input_value() == "dup_sig_b"

    page.click('[data-editor-tool="disconnect"]')
    after_disconnect = _export_draft(page)
    remaining_signals = [
        edge.get("signal_id")
        for edge in after_disconnect.get("edges", [])
        if isinstance(edge, dict)
    ]
    assert "dup_sig_b" not in remaining_signals
    assert {"dup_sig_a", "gap_probe"}.issubset(set(remaining_signals))
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_selects_node_and_exports_focus(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    target = page.locator(
        '.workbench-binding-diagnostics-target'
        '[data-diagnostics-rule-id="evidence_gap_density"]'
        '[data-diagnostics-target-kind="node"]'
        '[data-diagnostics-target-id="logic1"]',
    ).first
    target.click()

    assert page.locator('[data-editable-node-id="logic1"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#workbench-interface-binding-owner").inner_text() == "node:logic1"
    assert target.get_attribute("aria-pressed") == "true"

    draft = _export_draft(page)
    focus = draft.get("diagnostic_focus")
    assert focus["state"] == "selected"
    assert focus["target_kind"] == "node"
    assert focus["target_id"] == "logic1"
    assert focus["truth_effect"] == "none"

    archive = _prepare_archive(page)
    assert archive["diagnostic_focus"]["target_id"] == "logic1"
    assert archive["diagnostic_focus"]["truth_effect"] == "none"
    assert archive["checksums"]["diagnostic_focus_checksum"]
    assert archive["red_line_metadata"]["controller_truth_modified"] is False
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_selects_duplicate_edge_instance(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    diagnostic_payload["edges"][1]["source"] = "logic2"
    diagnostic_payload["edges"][1]["target"] = "logic3"
    _import_draft(page, diagnostic_payload)

    edge_target = page.locator(
        '.workbench-binding-diagnostics-target'
        '[data-diagnostics-target-kind="edge"]'
        '[data-diagnostics-edge-index="1"]',
    ).first
    edge_target.click()

    assert page.locator('[data-editable-edge-index="1"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#workbench-interface-binding-owner").inner_text() == "edge:edge_logic1_logic2"
    assert page.locator("#workbench-edge-signal-id").input_value() == "dup_sig_b"
    assert edge_target.get_attribute("aria-pressed") == "true"

    draft_round = _export_draft(page)
    focus = draft_round.get("diagnostic_focus")
    assert focus["state"] == "selected"
    assert focus["target_kind"] == "edge"
    assert focus["target_id"] == "edge_logic1_logic2"
    assert focus["edge_index"] == 1
    assert focus["signal_id"] == "dup_sig_b"
    assert focus["truth_effect"] == "none"

    archive = _prepare_archive(page)
    assert archive["diagnostic_focus"]["target_kind"] == "edge"
    assert archive["diagnostic_focus"]["edge_index"] == 1
    assert archive["diagnostic_focus"]["truth_effect"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_ignores_stale_duplicate_edge_index(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    diagnostic_payload["edges"][1]["source"] = "logic2"
    diagnostic_payload["edges"][1]["target"] = "logic3"
    diagnostic_payload["edges"][1]["signal_id"] = "dup_sig_a"
    _import_draft(page, diagnostic_payload)

    page.evaluate(
        """
        () => {
          const list = document.getElementById('workbench-hardware-binding-diagnostics-list');
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'workbench-binding-diagnostics-target';
          button.setAttribute('data-diagnostics-focus', 'true');
          button.setAttribute('data-diagnostics-target-kind', 'edge');
          button.setAttribute('data-diagnostics-target-id', 'edge_logic1_logic2');
          button.setAttribute('data-diagnostics-owner-key', 'edge:edge_logic1_logic2');
          button.setAttribute('data-diagnostics-rule-id', 'connector_port_reuse');
          button.setAttribute('data-diagnostics-issue-target', 'stale-index-probe');
          button.setAttribute('data-diagnostics-edge-id', 'edge_logic1_logic2');
          button.setAttribute('data-diagnostics-edge-index', '0');
          button.setAttribute('data-diagnostics-signal-id', 'dup_sig_a');
          button.setAttribute('data-diagnostics-source-node-id', 'logic2');
          button.setAttribute('data-diagnostics-target-node-id', 'logic3');
          button.textContent = 'Stale focus probe';
          list.appendChild(button);
        }
        """
    )

    page.locator(".workbench-binding-diagnostics-target", has_text="Stale focus probe").click()

    assert page.locator('[data-editable-edge-index="1"]').get_attribute("aria-pressed") == "true"
    assert page.locator('[data-editable-edge-index="0"]').get_attribute("aria-pressed") == "false"
    assert page.locator("#workbench-interface-cable").input_value() == "CBL-TR-B"

    draft_round = _export_draft(page)
    focus = draft_round.get("diagnostic_focus")
    assert focus["target_kind"] == "edge"
    assert focus["edge_index"] == 1
    assert focus["signal_id"] == "dup_sig_a"
    assert focus["source_node_id"] == "logic2"
    assert focus["target_node_id"] == "logic3"
    assert focus["truth_effect"] == "none"
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_uses_route_and_signal_for_same_route_duplicates(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    _import_draft(page, diagnostic_payload)

    page.evaluate(
        """
        () => {
          const list = document.getElementById('workbench-hardware-binding-diagnostics-list');
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'workbench-binding-diagnostics-target';
          button.setAttribute('data-diagnostics-focus', 'true');
          button.setAttribute('data-diagnostics-target-kind', 'edge');
          button.setAttribute('data-diagnostics-target-id', 'edge_logic1_logic2');
          button.setAttribute('data-diagnostics-owner-key', 'edge:edge_logic1_logic2');
          button.setAttribute('data-diagnostics-rule-id', 'duplicate_ownership');
          button.setAttribute('data-diagnostics-issue-target', 'same-route-stale-index-probe');
          button.setAttribute('data-diagnostics-edge-id', 'edge_logic1_logic2');
          button.setAttribute('data-diagnostics-edge-index', '0');
          button.setAttribute('data-diagnostics-signal-id', 'dup_sig_b');
          button.setAttribute('data-diagnostics-source-node-id', 'logic1');
          button.setAttribute('data-diagnostics-target-node-id', 'logic2');
          button.textContent = 'Same route stale focus probe';
          list.appendChild(button);
        }
        """
    )

    page.locator(".workbench-binding-diagnostics-target", has_text="Same route stale focus probe").click()

    assert page.locator('[data-editable-edge-index="1"]').get_attribute("aria-pressed") == "true"
    assert page.locator('[data-editable-edge-index="0"]').get_attribute("aria-pressed") == "false"
    assert page.locator("#workbench-edge-signal-id").input_value() == "dup_sig_b"

    focus = _export_draft(page).get("diagnostic_focus")
    assert focus["edge_index"] == 1
    assert focus["signal_id"] == "dup_sig_b"
    assert focus["source_node_id"] == "logic1"
    assert focus["target_node_id"] == "logic2"
    assert focus["truth_effect"] == "none"
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_miss_clears_stale_focus(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    page.locator(
        '.workbench-binding-diagnostics-target'
        '[data-diagnostics-rule-id="evidence_gap_density"]'
        '[data-diagnostics-target-kind="node"]'
        '[data-diagnostics-target-id="logic1"]',
    ).first.click()
    assert _export_draft(page)["diagnostic_focus"]["state"] == "selected"

    page.evaluate(
        """
        () => {
          const list = document.getElementById('workbench-hardware-binding-diagnostics-list');
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'workbench-binding-diagnostics-target';
          button.setAttribute('data-diagnostics-focus', 'true');
          button.setAttribute('data-diagnostics-target-kind', 'node');
          button.setAttribute('data-diagnostics-target-id', 'missing_node');
          button.setAttribute('data-diagnostics-owner-key', 'node:missing_node');
          button.setAttribute('data-diagnostics-rule-id', 'evidence_gap_density');
          button.setAttribute('data-diagnostics-issue-target', 'missing-node-probe');
          button.setAttribute('data-diagnostics-node-id', 'missing_node');
          button.textContent = 'Missing node focus probe';
          list.appendChild(button);
        }
        """
    )
    page.locator(".workbench-binding-diagnostics-target", has_text="Missing node focus probe").click()

    draft_round = _export_draft(page)
    assert draft_round["diagnostic_focus"]["state"] == "none"
    assert draft_round["diagnostic_focus"]["truth_effect"] == "none"

    archive = _prepare_archive(page)
    assert archive["diagnostic_focus"]["state"] == "none"
    assert archive["diagnostic_focus"]["truth_effect"] == "none"
    assert archive["red_line_metadata"]["controller_truth_modified"] is False
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_binding_diagnostic_focus_clears_after_edge_disconnect_and_node_remove(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    draft = _export_draft(page)
    diagnostic_payload = _with_duplicate_binding_payload(draft)
    diagnostic_payload["edges"][1]["source"] = "logic2"
    diagnostic_payload["edges"][1]["target"] = "logic3"
    _import_draft(page, diagnostic_payload)

    page.locator(
        '.workbench-binding-diagnostics-target'
        '[data-diagnostics-target-kind="edge"]'
        '[data-diagnostics-edge-index="1"]',
    ).first.click()
    assert _export_draft(page)["diagnostic_focus"]["state"] == "selected"

    page.click('[data-editor-tool="disconnect"]')
    after_disconnect = _export_draft(page)
    assert after_disconnect["diagnostic_focus"]["state"] == "none"
    assert after_disconnect["diagnostic_focus"]["truth_effect"] == "none"

    page.click('[data-editor-tool="node"]')
    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")
    page.locator(
        '.workbench-binding-diagnostics-target'
        '[data-diagnostics-rule-id="evidence_gap_density"]'
        '[data-diagnostics-target-kind="node"]'
        '[data-diagnostics-target-id="draft_node_1"]',
    ).first.click()
    assert _export_draft(page)["diagnostic_focus"]["state"] == "selected"

    page.click('[data-editor-tool="remove"]')
    after_remove = _export_draft(page)
    assert after_remove["diagnostic_focus"]["state"] == "none"
    assert after_remove["diagnostic_focus"]["truth_effect"] == "none"
    assert after_remove["controller_truth_modified"] is False
    assert errors == [], f"page JS errors: {errors}"


def test_workbench_hardware_binding_diagnostics_recomputed_after_import_export_roundtrip(demo_server, browser):  # type: ignore[no-untyped-def]
    page, errors = _new_page_with_errors(browser)  # type: ignore[no-untyped-call]
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    _clear_local_draft(page)
    _goto_shell_workbench(page, f"{demo_server}/workbench")

    page.fill("#workbench-interface-hardware-id", "TR-LRU-001")
    page.fill("#workbench-interface-cable", "CBL-TR-A")
    page.fill("#workbench-interface-connector", "J1")
    page.fill("#workbench-interface-port-local", "logic1:out")
    page.fill("#workbench-interface-port-peer", "TR-LRU-001:J1")
    page.select_option("#workbench-interface-evidence-status", "ui_draft")
    page.click("#workbench-apply-interface-binding-btn")

    baseline = _export_draft(page)
    baseline["edges"] = [
        {
            "id": "edge_logic1_logic2",
            "source": "logic1",
            "target": "logic2",
            "signal_id": "trip_a",
            "hardware_binding": {
                "hardware_id": "TR-LRU-001",
                "cable": "CBL-TR-A",
                "connector": "J1",
                "port_local": "logic1:out",
                "port_peer": "TR-LRU-001:J1",
                "evidence_status": "ui_draft",
            },
        },
        {
            "id": "edge_logic1_logic2",
            "source": "logic1",
            "target": "logic2",
            "signal_id": "trip_b",
            "hardware_binding": {
                "hardware_id": "TR-LRU-001",
                "cable": "CBL-TR-B",
                "connector": "J1",
                "port_local": "logic1:out",
                "port_peer": "TR-LRU-001:J1",
                "evidence_status": "ui_draft",
            },
        },
    ]
    _import_draft(page, baseline)
    first = _export_draft(page)
    first_diags = _collect_diagnostics(first)
    assert first_diags is not None

    _import_draft(page, first)
    second = _export_draft(page)
    second_diags = _collect_diagnostics(second)
    assert second_diags is not None

    assert _stable_diagnostics_equal(first_diags, second_diags), (
        "hardware binding diagnostics are not stable across import/export roundtrip"
    )

    archive = _prepare_archive(page)
    archive_diags = _collect_diagnostics(archive)
    assert archive_diags is not None
    assert _stable_diagnostics_equal(first_diags, archive_diags), (
        "evidence archive diagnostics must match last exported diagnostics"
    )
    assert errors == [], f"page JS errors: {errors}"


def _new_page_with_errors(browser):
    page = browser.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    return page, errors

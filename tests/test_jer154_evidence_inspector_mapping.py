from __future__ import annotations

import json
from pathlib import Path

import pytest

from well_harness.hardware_evidence_report import build_hardware_evidence_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "hardware_evidence_report_v1.schema.json"
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def validator_for_hardware_evidence_report_schema():
    pytest.importorskip("jsonschema")
    from jsonschema import Draft202012Validator

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_hardware_evidence_report_indexes_signal_bindings_by_logic_node() -> None:
    payload = build_hardware_evidence_report(system_id="thrust-reverser")

    errors = list(validator_for_hardware_evidence_report_schema().iter_errors(payload))
    assert errors == []
    index = payload["evidence_index"]

    assert index["truth_effect"] == "none"
    assert index["lru_inventory_count"] == 11
    assert index["signal_binding_count"] == 18
    assert index["evidence_gap_count"] == 141
    assert len(index["lru_inventory"]) == 11
    assert len(index["signal_bindings"]) == 18

    logic3_bindings = index["logic_node_bindings"]["L3"]
    logic3_signal_ids = {binding["signal_id"] for binding in logic3_bindings}
    assert {
        "reverser_inhibited",
        "engine_running",
        "aircraft_on_ground",
        "tls_unlocked_ls",
        "n1k",
        "tra_deg",
        "eec_deploy_cmd",
        "pls_power_cmd",
        "pdu_motor_cmd",
    } <= logic3_signal_ids
    assert all(binding["truth_effect"] == "none" for binding in logic3_bindings)


def test_evidence_index_keeps_unknown_carriers_explicit() -> None:
    payload = build_hardware_evidence_report(system_id="thrust-reverser")
    bindings = payload["evidence_index"]["logic_node_bindings"]["L4"]
    tra_binding = next(binding for binding in bindings if binding["signal_id"] == "tra_deg")

    assert tra_binding["carrier_status"] == "evidence_gap"
    assert tra_binding["cable"] == {"status": "evidence_gap", "value": "TBD"}
    assert tra_binding["connector"] == {"status": "evidence_gap", "value": "TBD"}
    assert tra_binding["port_local"] == {"status": "evidence_gap", "value": "TBD"}
    assert tra_binding["port_peer"] == {"status": "evidence_gap", "value": "TBD"}
    assert tra_binding["display_status"] == "not_recorded"


def test_workbench_evidence_inspector_has_mapping_surface_and_no_live_mutation() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert 'id="workbench-inspector-evidence-detail"' in html
    assert 'id="workbench-inspector-signal-count"' in html
    assert "function normalizeInspectorLogicNodeId" in js
    assert "function renderInspectorEvidenceDetails" in js
    assert "logic_node_bindings" in js
    assert "not recorded" in js
    assert "truth_effect" in js
    assert "fetch(\"https://linear.app" not in js
    assert "api.linear.app" not in js

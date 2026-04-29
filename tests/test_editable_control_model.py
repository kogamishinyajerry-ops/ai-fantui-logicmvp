from __future__ import annotations

import copy

import pytest

from well_harness.editable_control_model import (
    EDITABLE_CONTROL_MODEL_DIFF_SCHEMA_ID,
    EDITABLE_CONTROL_MODEL_SCHEMA_ID,
    EditableControlModelValidationError,
    build_editable_control_model_diff_report,
    build_reference_editable_control_model,
    compare_editable_snapshot_to_baseline,
    editable_control_model_hash,
    evaluate_editable_snapshot,
    validate_editable_control_model,
    validate_editable_control_model_diff_report,
)


FULL_CHAIN_SNAPSHOT = {
    "radio_altitude_ft": 5.0,
    "tra_deg": -14.0,
    "sw1": True,
    "sw2": True,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "n1k": 50.0,
    "max_n1k_deploy_limit": 60.0,
    "tls_unlocked_ls": True,
    "all_pls_unlocked_ls": True,
    "reverser_not_deployed_eec": True,
    "reverser_fully_deployed_eec": False,
    "deploy_position_percent": 95.0,
    "deploy_90_percent_vdt": True,
}


def test_reference_seed_is_schema_valid_sandbox_candidate() -> None:
    payload = build_reference_editable_control_model()

    validate_editable_control_model(payload)

    assert payload["$schema"] == EDITABLE_CONTROL_MODEL_SCHEMA_ID
    assert payload["kind"] == "well-harness-editable-control-model"
    assert payload["version"] == 1
    assert payload["system_id"] == "thrust-reverser"
    assert payload["truth_status"] == "sandbox_candidate"
    assert payload["view_status"] == "derived_view"
    assert payload["boundaries"]["controller_truth_modified"] is False
    assert payload["boundaries"]["truth_level_impact"] == "none"
    assert payload["boundaries"]["dal_pssa_impact"] == "none"
    assert payload["evidence_metadata"]["baseline_adapter_id"] == "reference-deploy-controller"
    assert len(payload["nodes"]) >= 4
    assert len(payload["ports"]) >= len(payload["nodes"])
    assert payload["edges"]
    assert payload["hardware_bindings"]
    assert editable_control_model_hash(payload) == editable_control_model_hash(payload)


def test_reference_seed_includes_logic_rules_for_snapshot_runtime() -> None:
    payload = build_reference_editable_control_model()
    logic2 = next(node for node in payload["nodes"] if node["id"] == "logic2")

    assert logic2["op"] == "and"
    assert any(rule["name"] == "sw2_hysteresis_tra_deg" for rule in logic2["rules"])
    assert all(rule["source_signal_id"] for rule in logic2["rules"])


def test_validator_rejects_certified_truth_status() -> None:
    payload = build_reference_editable_control_model()
    payload["truth_status"] = "certified"

    with pytest.raises(EditableControlModelValidationError, match="truth_status"):
        validate_editable_control_model(payload)


def test_validator_rejects_dangling_edge_port() -> None:
    payload = build_reference_editable_control_model()
    missing_port_id = payload["edges"][0]["source_port_id"]
    payload["ports"] = [port for port in payload["ports"] if port["id"] != missing_port_id]

    with pytest.raises(EditableControlModelValidationError, match="source_port_id"):
        validate_editable_control_model(payload)


def test_validator_rejects_hardware_binding_that_affects_truth() -> None:
    payload = build_reference_editable_control_model()
    payload["hardware_bindings"][0]["truth_effect"] = "controls_truth"

    with pytest.raises(EditableControlModelValidationError, match="truth_effect"):
        validate_editable_control_model(payload)


def test_diff_report_schema_accepts_equivalent_payload() -> None:
    model = build_reference_editable_control_model()
    candidate = copy.deepcopy(model)
    candidate["model_id"] = "candidate-edited-copy"

    report = build_editable_control_model_diff_report(
        baseline_model=model,
        candidate_model=candidate,
        scenario_id="snapshot-default",
        verdict="equivalent",
    )

    validate_editable_control_model_diff_report(report)

    assert report["$schema"] == EDITABLE_CONTROL_MODEL_DIFF_SCHEMA_ID
    assert report["kind"] == "well-harness-editable-control-model-diff"
    assert report["baseline_run"]["truth_status"] == "sandbox_candidate"
    assert report["candidate_run"]["model_id"] == "candidate-edited-copy"
    assert report["scenario_result"]["scenario_id"] == "snapshot-default"
    assert report["verdict"] == "equivalent"


def test_diff_report_schema_rejects_certified_candidate_claim() -> None:
    model = build_reference_editable_control_model()
    candidate = copy.deepcopy(model)
    candidate["model_id"] = "candidate-cert-claim"
    candidate["truth_status"] = "certified"

    report = build_editable_control_model_diff_report(
        baseline_model=model,
        candidate_model=candidate,
        scenario_id="snapshot-default",
        verdict="equivalent",
    )

    with pytest.raises(EditableControlModelValidationError, match="truth_status"):
        validate_editable_control_model_diff_report(report)


def test_evaluate_editable_snapshot_matches_full_chain_candidate_rules() -> None:
    model = build_reference_editable_control_model()

    result = evaluate_editable_snapshot(model, FULL_CHAIN_SNAPSHOT)

    assert result["model_id"] == model["model_id"]
    assert result["truth_status"] == "sandbox_candidate"
    assert result["completion_reached"] is True
    assert set(result["active_logic_node_ids"]) == {"logic1", "logic2", "logic3", "logic4"}
    assert result["logic_states"]["logic4"]["state"] == "active"
    assert result["asserted_component_values"]["logic4"] is True


def test_compare_editable_snapshot_to_baseline_reports_equivalent_full_chain() -> None:
    model = build_reference_editable_control_model()

    report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)

    validate_editable_control_model_diff_report(report)
    assert report["verdict"] == "equivalent"
    assert report["first_divergence"] is None
    assert all(delta["status"] == "same" for delta in report["per_signal_delta"])


def test_compare_editable_snapshot_to_baseline_reports_intentional_threshold_drift() -> None:
    model = build_reference_editable_control_model()
    logic3 = next(node for node in model["nodes"] if node["id"] == "logic3")
    tra_rule = next(rule for rule in logic3["rules"] if rule["name"] == "tra_deg")
    tra_rule["threshold_value"] = -20.0

    report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)

    validate_editable_control_model_diff_report(report)
    assert report["verdict"] == "divergent"
    assert report["first_divergence"]["signal_id"] == "logic3"
    assert report["first_divergence"]["baseline_value"] is True
    assert report["first_divergence"]["candidate_value"] is False


def test_evaluate_editable_snapshot_rejects_unsafe_op_catalog_entry() -> None:
    model = build_reference_editable_control_model()
    logic1 = next(node for node in model["nodes"] if node["id"] == "logic1")
    logic1["op"] = "python_eval"

    with pytest.raises(EditableControlModelValidationError, match="op"):
        evaluate_editable_snapshot(model, FULL_CHAIN_SNAPSHOT)


def test_hardware_binding_edits_do_not_change_baseline_diff() -> None:
    model = build_reference_editable_control_model()
    model["hardware_bindings"][0]["hardware_id"] = "sandbox-edited-hardware"
    model["hardware_bindings"][0]["evidence_status"] = "evidence_gap"

    report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)

    assert report["verdict"] == "equivalent"
    assert report["hardware_evidence"]["truth_effect"] == "none"

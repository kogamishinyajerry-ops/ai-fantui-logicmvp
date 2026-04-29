from __future__ import annotations

import copy

import pytest

from well_harness.editable_control_model import (
    EDITABLE_CONTROL_MODEL_DIFF_SCHEMA_ID,
    EDITABLE_CONTROL_MODEL_SCHEMA_ID,
    EditableControlModelValidationError,
    build_editable_control_model_diff_report,
    build_reference_editable_control_model,
    editable_control_model_hash,
    validate_editable_control_model,
    validate_editable_control_model_diff_report,
)


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

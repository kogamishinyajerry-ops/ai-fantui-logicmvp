from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from well_harness.editable_hardware_interface_design import (
    EDITABLE_HARDWARE_INTERFACE_DESIGN_KIND,
    EDITABLE_HARDWARE_INTERFACE_DESIGN_SCHEMA_ID,
    EDITABLE_HARDWARE_INTERFACE_DESIGN_VERSION,
    EditableHardwareInterfaceDesignValidationError,
    canonicalize_editable_hardware_interface_design,
    clear_editable_hardware_interface_design_cache,
    editable_hardware_interface_design_hash,
    editable_hardware_interface_schema_hash,
    load_editable_hardware_interface_design,
    load_editable_hardware_interface_design_cached,
    validate_editable_hardware_interface_design,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "editable_hardware_interface_design_v1.schema.json"
)


def _valid_design() -> dict:
    return {
        "$schema": EDITABLE_HARDWARE_INTERFACE_DESIGN_SCHEMA_ID,
        "kind": EDITABLE_HARDWARE_INTERFACE_DESIGN_KIND,
        "version": EDITABLE_HARDWARE_INTERFACE_DESIGN_VERSION,
        "design_id": "thrust-reverser-interface-draft-v1",
        "system_id": "thrust-reverser",
        "candidate_state": "sandbox_candidate",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "runtime_truth_effect": "none",
        "lrus": [
            {
                "id": "TR-LRU-CTRL",
                "display_name": "TR Control Electronics",
                "quantity_per_engine": 1,
                "part_number": None,
                "location": None,
                "failure_rate_per_hour": None,
                "evidence_status": "evidence_gap",
                "source_ref": "workbench.hardware_interface_design",
            },
            {
                "id": "TR-LRU-ACT",
                "display_name": "TR Actuator Interface",
                "quantity_per_engine": 1,
                "part_number": None,
                "location": None,
                "failure_rate_per_hour": None,
                "evidence_status": "evidence_gap",
                "source_ref": "workbench.hardware_interface_design",
            },
        ],
        "cables": [
            {
                "id": "CBL-TR-001",
                "display_name": "TR command cable",
                "source_lru_id": "TR-LRU-CTRL",
                "target_lru_id": "TR-LRU-ACT",
                "cable_type": None,
                "evidence_status": "ui_draft",
                "source_ref": "workbench.hardware_interface_design",
            }
        ],
        "connectors": [
            {
                "id": "J-CTRL-1",
                "display_name": "Controller J1",
                "lru_id": "TR-LRU-CTRL",
                "connector_type": "evidence_gap",
                "evidence_status": "evidence_gap",
                "source_ref": "workbench.hardware_interface_design",
            },
            {
                "id": "J-ACT-1",
                "display_name": "Actuator J1",
                "lru_id": "TR-LRU-ACT",
                "connector_type": "evidence_gap",
                "evidence_status": "evidence_gap",
                "source_ref": "workbench.hardware_interface_design",
            },
        ],
        "ports": [
            {
                "id": "PORT-CTRL-CMD",
                "display_name": "PDU command out",
                "connector_id": "J-CTRL-1",
                "direction": "output",
                "signal_id": "pdu_motor_cmd",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
                "source_ref": "workbench.hardware_interface_design",
            },
            {
                "id": "PORT-ACT-CMD",
                "display_name": "PDU command in",
                "connector_id": "J-ACT-1",
                "direction": "input",
                "signal_id": "pdu_motor_cmd",
                "value_type": "boolean",
                "evidence_status": "ui_draft",
                "source_ref": "workbench.hardware_interface_design",
            },
        ],
        "pins": [
            {
                "id": "PIN-CTRL-1",
                "connector_id": "J-CTRL-1",
                "pin_number": "1",
                "port_id": "PORT-CTRL-CMD",
                "signal_id": "pdu_motor_cmd",
                "evidence_status": "ui_draft",
                "source_ref": "workbench.hardware_interface_design",
            },
            {
                "id": "PIN-ACT-1",
                "connector_id": "J-ACT-1",
                "pin_number": "1",
                "port_id": "PORT-ACT-CMD",
                "signal_id": "pdu_motor_cmd",
                "evidence_status": "ui_draft",
                "source_ref": "workbench.hardware_interface_design",
            },
        ],
        "bindings": [
            {
                "id": "BIND-PDU-CMD",
                "signal_id": "pdu_motor_cmd",
                "source_port_id": "PORT-CTRL-CMD",
                "target_port_id": "PORT-ACT-CMD",
                "cable_id": "CBL-TR-001",
                "redundancy_status": "unknown",
                "evidence_status": "ui_draft",
                "truth_effect": "none",
                "source_ref": "workbench.hardware_interface_design",
            }
        ],
        "evidence_gaps": [
            {
                "id": "GAP-TR-CTRL-PART",
                "subject_id": "TR-LRU-CTRL",
                "field_ref": "lrus.TR-LRU-CTRL.part_number",
                "severity": "medium",
                "impact": "part number unavailable for review packet",
                "proposed_fill": "capture from engineering BOM",
                "source_ref": "workbench.hardware_interface_design",
            }
        ],
        "evidence_metadata": {
            "sample_pack_role": "hardware_interface_design",
            "source_refs": ["workbench.hardware_interface_design"],
        },
        "boundaries": {
            "runtime_scope": "sandbox_only",
            "hardware_truth_effect": "none",
            "certified_truth_modified": False,
            "dal_pssa_impact": "none",
        },
    }


def test_schema_artifact_accepts_valid_design() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)

    jsonschema.Draft202012Validator(schema).validate(_valid_design())

    assert editable_hardware_interface_schema_hash() == editable_hardware_interface_schema_hash()


def test_load_valid_design_yaml_returns_typed_sandbox_model(tmp_path: Path) -> None:
    path = tmp_path / "hardware_interface_design.yaml"
    path.write_text(yaml.safe_dump(_valid_design(), sort_keys=False), encoding="utf-8")

    design = load_editable_hardware_interface_design(path)

    assert design.kind == EDITABLE_HARDWARE_INTERFACE_DESIGN_KIND
    assert design.candidate_state == "sandbox_candidate"
    assert design.truth_level_impact == "none"
    assert design.controller_truth_modified is False
    assert design.lrus[0].id == "TR-LRU-CTRL"
    assert design.connectors[0].lru_id == "TR-LRU-CTRL"
    assert design.bindings[0].truth_effect == "none"
    assert design.payload_hash == editable_hardware_interface_design_hash(_valid_design())


def test_validator_rejects_invalid_kind_or_version() -> None:
    design = _valid_design()
    design["kind"] = "thrust-reverser-hardware"

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="kind"):
        validate_editable_hardware_interface_design(design)

    design = _valid_design()
    design["version"] = 2

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="version"):
        validate_editable_hardware_interface_design(design)


def test_reference_integrity_rejects_dangling_connector_port_and_cable() -> None:
    design = _valid_design()
    design["ports"][0]["connector_id"] = "MISSING-J"

    with pytest.raises(
        EditableHardwareInterfaceDesignValidationError,
        match="connector_id references missing",
    ):
        validate_editable_hardware_interface_design(design)

    design = _valid_design()
    design["bindings"][0]["cable_id"] = "MISSING-CABLE"

    with pytest.raises(
        EditableHardwareInterfaceDesignValidationError,
        match="cable_id references missing",
    ):
        validate_editable_hardware_interface_design(design)


def test_evidence_gap_references_must_be_explicitly_marked() -> None:
    design = _valid_design()
    design["bindings"][0]["target_port_id"] = "evidence_gap"
    design["bindings"][0]["evidence_status"] = "evidence_gap"

    validate_editable_hardware_interface_design(design)

    design["bindings"][0]["evidence_status"] = "ui_draft"
    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="evidence_gap"):
        validate_editable_hardware_interface_design(design)


def test_duplicate_ids_are_rejected_within_and_across_collections() -> None:
    design = _valid_design()
    design["lrus"][1]["id"] = "TR-LRU-CTRL"

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="duplicate lru ids"):
        validate_editable_hardware_interface_design(design)

    design = _valid_design()
    design["ports"][0]["id"] = "J-CTRL-1"

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="duplicate id across"):
        validate_editable_hardware_interface_design(design)


def test_evidence_gap_records_require_minimum_review_fields() -> None:
    design = _valid_design()
    del design["evidence_gaps"][0]["proposed_fill"]

    with pytest.raises(
        EditableHardwareInterfaceDesignValidationError,
        match="proposed_fill",
    ):
        validate_editable_hardware_interface_design(design)


def test_deterministic_hash_is_stable_after_canonicalization() -> None:
    design = _valid_design()
    reordered = copy.deepcopy(design)
    reordered["evidence_metadata"] = {
        "source_refs": ["workbench.hardware_interface_design"],
        "sample_pack_role": "hardware_interface_design",
    }

    assert editable_hardware_interface_design_hash(design) == editable_hardware_interface_design_hash(
        canonicalize_editable_hardware_interface_design(design)
    )
    assert editable_hardware_interface_design_hash(design) == editable_hardware_interface_design_hash(
        reordered
    )


def test_cached_loader_reuses_sandbox_catalog_entry(tmp_path: Path) -> None:
    clear_editable_hardware_interface_design_cache()
    path = tmp_path / "hardware_interface_design.json"
    path.write_text(json.dumps(_valid_design()), encoding="utf-8")

    first = load_editable_hardware_interface_design_cached(str(path))
    second = load_editable_hardware_interface_design_cached(str(path))

    assert first is second
    assert first.payload_hash == second.payload_hash


def test_truth_claims_are_rejected_before_runtime_use() -> None:
    design = _valid_design()
    design["truth_level_impact"] = "certified"

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="truth_level_impact"):
        validate_editable_hardware_interface_design(design)

    design = _valid_design()
    design["bindings"][0]["truth_effect"] = "controls_truth"

    with pytest.raises(EditableHardwareInterfaceDesignValidationError, match="truth_effect"):
        validate_editable_hardware_interface_design(design)

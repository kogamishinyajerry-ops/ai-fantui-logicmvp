from __future__ import annotations

import pytest

from well_harness.hardware_registry import (
    ACTIVE_HARDWARE_SYSTEM_ID,
    FROZEN_HARDWARE_PATHS,
    HardwareRegistryError,
    hardware_evidence_summary_to_dict,
    load_hardware_evidence_summary,
)


def test_active_hardware_registry_loads_thrust_reverser_summary() -> None:
    summary = load_hardware_evidence_summary()

    assert summary.system_id == ACTIVE_HARDWARE_SYSTEM_ID
    assert summary.hardware_path == "config/hardware/thrust_reverser_hardware_v1.yaml"
    assert summary.kind == "thrust-reverser-hardware"
    assert summary.version == 1
    assert summary.lru_count == 11
    assert summary.signal_binding_count == 18


def test_registry_marks_hardware_metadata_read_only_and_non_truth_mutating() -> None:
    summary = load_hardware_evidence_summary()

    assert summary.read_only is True
    assert summary.truth_level_impact == "none"
    assert summary.dal_pssa_impact == "none"
    assert summary.controller_truth_source == "src/well_harness/controller.py"
    assert summary.controller_truth_modified is False


def test_registry_counts_explicit_evidence_gaps_without_inference() -> None:
    summary = load_hardware_evidence_summary()

    assert summary.lru_evidence_gap_field_count == 33
    assert summary.signal_evidence_gap_field_count == 108
    assert summary.total_evidence_gap_field_count == 141
    assert summary.inferred_field_count == 0


def test_registry_exposes_frozen_hardware_paths_as_read_protected() -> None:
    summary = load_hardware_evidence_summary()

    assert summary.frozen_hardware_paths == tuple(sorted(FROZEN_HARDWARE_PATHS))
    assert summary.hardware_path not in summary.frozen_hardware_paths
    assert summary.read_protected_hardware_paths == summary.frozen_hardware_paths


def test_registry_dict_output_is_deterministic_and_json_ready() -> None:
    payload = hardware_evidence_summary_to_dict(load_hardware_evidence_summary())

    assert list(payload) == [
        "system_id",
        "kind",
        "version",
        "hardware_path",
        "read_only",
        "truth_level_impact",
        "dal_pssa_impact",
        "controller_truth_source",
        "controller_truth_modified",
        "lru_count",
        "signal_binding_count",
        "lru_evidence_gap_field_count",
        "signal_evidence_gap_field_count",
        "total_evidence_gap_field_count",
        "inferred_field_count",
        "frozen_hardware_paths",
        "read_protected_hardware_paths",
    ]
    assert payload["system_id"] == "thrust-reverser"
    assert payload["frozen_hardware_paths"] == sorted(FROZEN_HARDWARE_PATHS)


def test_registry_rejects_non_active_system_ids() -> None:
    with pytest.raises(HardwareRegistryError, match="only supports thrust-reverser"):
        load_hardware_evidence_summary(system_id="c919-etras")

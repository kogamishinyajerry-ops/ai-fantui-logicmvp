"""
Read-only hardware evidence registry.

This module exposes metadata from the active thrust-reverser hardware YAML for
runtime and audit surfaces. It does not change controller truth semantics and
does not infer missing hardware evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from well_harness.hardware_schema import (
    LruInventoryItem,
    SignalCarrierBinding,
    load_thrust_reverser_hardware,
)


ACTIVE_HARDWARE_SYSTEM_ID = "thrust-reverser"
ACTIVE_HARDWARE_PATH = "config/hardware/thrust_reverser_hardware_v1.yaml"
FROZEN_HARDWARE_PATHS = (
    "config/hardware/bleed_air_hardware_v1.yaml",
    "config/hardware/c919_etras_hardware_v1.yaml",
    "config/hardware/landing_gear_hardware_v1.yaml",
)
CONTROLLER_TRUTH_SOURCE = "src/well_harness/controller.py"

_LRU_VALUE_REF_FIELDS = ("part_number", "location", "failure_rate_per_hour")
_SIGNAL_VALUE_REF_FIELDS = ("cable", "connector", "port_local", "port_peer")
_SIGNAL_STATUS_FIELDS = ("redundancy_status", "evidence_status")


class HardwareRegistryError(ValueError):
    """Raised when the read-only hardware registry cannot serve a request."""


@dataclass(frozen=True)
class HardwareEvidenceSummary:
    system_id: str
    kind: str
    version: int
    hardware_path: str
    read_only: bool
    truth_level_impact: str
    dal_pssa_impact: str
    controller_truth_source: str
    controller_truth_modified: bool
    lru_count: int
    signal_binding_count: int
    lru_evidence_gap_field_count: int
    signal_evidence_gap_field_count: int
    total_evidence_gap_field_count: int
    inferred_field_count: int
    frozen_hardware_paths: tuple[str, ...]
    read_protected_hardware_paths: tuple[str, ...]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _count_lru_evidence_gap_fields(items: tuple[LruInventoryItem, ...]) -> int:
    count = 0
    for item in items:
        for field_name in _LRU_VALUE_REF_FIELDS:
            value_ref = getattr(item, field_name)
            if value_ref.status == "evidence_gap":
                count += 1
    return count


def _count_signal_evidence_gap_fields(items: tuple[SignalCarrierBinding, ...]) -> int:
    count = 0
    for item in items:
        for field_name in _SIGNAL_VALUE_REF_FIELDS:
            value_ref = getattr(item, field_name)
            if value_ref.status == "evidence_gap":
                count += 1
        for field_name in _SIGNAL_STATUS_FIELDS:
            if getattr(item, field_name) == "evidence_gap":
                count += 1
    return count


def load_hardware_evidence_summary(
    system_id: str = ACTIVE_HARDWARE_SYSTEM_ID,
    *,
    project_root: str | Path | None = None,
) -> HardwareEvidenceSummary:
    """Load deterministic read-only evidence metadata for the active hardware line."""
    if system_id != ACTIVE_HARDWARE_SYSTEM_ID:
        raise HardwareRegistryError(
            f"Hardware evidence registry only supports thrust-reverser, got {system_id!r}"
        )

    root = Path(project_root) if project_root is not None else _project_root()
    hardware = load_thrust_reverser_hardware(root / ACTIVE_HARDWARE_PATH)

    lru_gap_count = _count_lru_evidence_gap_fields(hardware.lru_inventory)
    signal_gap_count = _count_signal_evidence_gap_fields(hardware.signal_carrier_bindings)
    frozen_paths = tuple(sorted(FROZEN_HARDWARE_PATHS))

    return HardwareEvidenceSummary(
        system_id=hardware.system_id,
        kind=hardware.kind,
        version=hardware.version,
        hardware_path=ACTIVE_HARDWARE_PATH,
        read_only=True,
        truth_level_impact="none",
        dal_pssa_impact="none",
        controller_truth_source=CONTROLLER_TRUTH_SOURCE,
        controller_truth_modified=False,
        lru_count=len(hardware.lru_inventory),
        signal_binding_count=len(hardware.signal_carrier_bindings),
        lru_evidence_gap_field_count=lru_gap_count,
        signal_evidence_gap_field_count=signal_gap_count,
        total_evidence_gap_field_count=lru_gap_count + signal_gap_count,
        inferred_field_count=0,
        frozen_hardware_paths=frozen_paths,
        read_protected_hardware_paths=frozen_paths,
    )


def hardware_evidence_summary_to_dict(summary: HardwareEvidenceSummary) -> dict[str, Any]:
    """Return a stable JSON-ready dict for API/report layers."""
    return {
        "system_id": summary.system_id,
        "kind": summary.kind,
        "version": summary.version,
        "hardware_path": summary.hardware_path,
        "read_only": summary.read_only,
        "truth_level_impact": summary.truth_level_impact,
        "dal_pssa_impact": summary.dal_pssa_impact,
        "controller_truth_source": summary.controller_truth_source,
        "controller_truth_modified": summary.controller_truth_modified,
        "lru_count": summary.lru_count,
        "signal_binding_count": summary.signal_binding_count,
        "lru_evidence_gap_field_count": summary.lru_evidence_gap_field_count,
        "signal_evidence_gap_field_count": summary.signal_evidence_gap_field_count,
        "total_evidence_gap_field_count": summary.total_evidence_gap_field_count,
        "inferred_field_count": summary.inferred_field_count,
        "frozen_hardware_paths": list(summary.frozen_hardware_paths),
        "read_protected_hardware_paths": list(summary.read_protected_hardware_paths),
    }

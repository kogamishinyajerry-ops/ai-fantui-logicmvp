from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


FAULT_TAXONOMY_KIND = "well-harness-fault-taxonomy"
FAULT_TAXONOMY_VERSION = 1
FAULT_TAXONOMY_SCHEMA_ID = "https://well-harness.local/json_schema/fault_taxonomy_v1.schema.json"


@dataclass(frozen=True)
class FaultTaxonomyEntry:
    fault_kind: str
    category: str
    label: str
    description: str
    default_effect: str


FAULT_TAXONOMY = (
    FaultTaxonomyEntry(
        fault_kind="bias_low",
        category="sensor_bias",
        label="Bias Low",
        description="Signal trends lower than the baseline profile without fully saturating inactive.",
        default_effect="decrease_from_baseline",
    ),
    FaultTaxonomyEntry(
        fault_kind="bias_high",
        category="sensor_bias",
        label="Bias High",
        description="Signal trends higher than the baseline profile without fully saturating active.",
        default_effect="increase_from_baseline",
    ),
    FaultTaxonomyEntry(
        fault_kind="stuck_low",
        category="stuck_state",
        label="Stuck Low",
        description="Signal or command remains at its inactive value.",
        default_effect="force_inactive",
    ),
    FaultTaxonomyEntry(
        fault_kind="stuck_high",
        category="stuck_state",
        label="Stuck High",
        description="Signal or command remains at its active value.",
        default_effect="force_active",
    ),
    FaultTaxonomyEntry(
        fault_kind="open_circuit",
        category="electrical_path",
        label="Open Circuit",
        description="Electrical path is broken so the target falls back to an inactive outcome.",
        default_effect="force_inactive",
    ),
    FaultTaxonomyEntry(
        fault_kind="short_to_power",
        category="electrical_path",
        label="Short To Power",
        description="Electrical path is shorted to power so the target is forced active.",
        default_effect="force_active",
    ),
    FaultTaxonomyEntry(
        fault_kind="latched_no_unlock",
        category="interlock_state",
        label="Latched No Unlock",
        description="Unlock-capable target remains just below its unlock-ready state.",
        default_effect="hold_below_unlock_threshold",
    ),
    FaultTaxonomyEntry(
        fault_kind="command_path_failure",
        category="command_path",
        label="Command Path Failure",
        description="Downstream command path fails, leaving the target inactive even when upstream logic is ready.",
        default_effect="force_inactive",
    ),
)


SUPPORTED_FAULT_KINDS = tuple(entry.fault_kind for entry in FAULT_TAXONOMY)


def validate_fault_kind(fault_kind: str) -> str:
    normalized = fault_kind.strip()
    if normalized in SUPPORTED_FAULT_KINDS:
        return normalized
    supported = ", ".join(SUPPORTED_FAULT_KINDS)
    raise ValueError(f"fault_kind must be one of: {supported}. Received: {fault_kind!r}")


def fault_taxonomy_to_dict() -> dict[str, Any]:
    return {
        "$schema": FAULT_TAXONOMY_SCHEMA_ID,
        "kind": FAULT_TAXONOMY_KIND,
        "version": FAULT_TAXONOMY_VERSION,
        "fault_kinds": [asdict(entry) for entry in FAULT_TAXONOMY],
    }

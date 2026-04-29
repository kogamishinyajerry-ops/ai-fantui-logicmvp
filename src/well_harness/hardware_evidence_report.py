from __future__ import annotations

from typing import Any

from well_harness.hardware_registry import (
    hardware_evidence_summary_to_dict,
    load_hardware_evidence_summary,
)


REPORT_SCHEMA_ID = "https://well-harness.local/json_schema/hardware_evidence_report_v1.schema.json"
EXPECTED_LRU_COUNT = 11
EXPECTED_SIGNAL_BINDING_COUNT = 18


def make_check(name: str, status: str, **details: Any) -> dict[str, Any]:
    check: dict[str, Any] = {"name": name, "status": status}
    if details:
        check["details"] = details
    return check


def coverage_status(expected_count: int, actual_count: int) -> str:
    return "pass" if expected_count == actual_count else "fail"


def build_hardware_evidence_report(system_id: str = "thrust-reverser") -> dict[str, Any]:
    summary = load_hardware_evidence_summary(system_id=system_id)
    summary_dict = hardware_evidence_summary_to_dict(summary)

    lru_status = coverage_status(EXPECTED_LRU_COUNT, summary.lru_count)
    signal_status = coverage_status(EXPECTED_SIGNAL_BINDING_COUNT, summary.signal_binding_count)
    evidence_gap_status = (
        "pass"
        if summary.total_evidence_gap_field_count
        == summary.lru_evidence_gap_field_count + summary.signal_evidence_gap_field_count
        and summary.inferred_field_count == 0
        else "fail"
    )
    boundary_status = (
        "pass"
        if summary.read_only
        and summary.truth_level_impact == "none"
        and summary.dal_pssa_impact == "none"
        and not summary.controller_truth_modified
        else "fail"
    )

    checks = [
        make_check(
            "lru_inventory_coverage",
            lru_status,
            expected_count=EXPECTED_LRU_COUNT,
            actual_count=summary.lru_count,
        ),
        make_check(
            "signal_binding_coverage",
            signal_status,
            expected_count=EXPECTED_SIGNAL_BINDING_COUNT,
            actual_count=summary.signal_binding_count,
        ),
        make_check(
            "evidence_gap_accounting",
            evidence_gap_status,
            lru_field_count=summary.lru_evidence_gap_field_count,
            signal_field_count=summary.signal_evidence_gap_field_count,
            total_field_count=summary.total_evidence_gap_field_count,
            inferred_field_count=summary.inferred_field_count,
        ),
        make_check(
            "read_only_boundaries",
            boundary_status,
            controller_truth_source=summary.controller_truth_source,
            frozen_hardware_paths=list(summary.frozen_hardware_paths),
        ),
    ]
    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"

    return {
        "$schema": REPORT_SCHEMA_ID,
        "schema_version": "hardware_evidence_report.v1",
        "generated_by": "well_harness.hardware_evidence_report",
        "adapter": "thrust-reverser",
        "layer": "L6",
        "truth_level_impact": "none",
        "status": status,
        "hardware_summary": summary_dict,
        "coverage": {
            "lru_inventory": {
                "status": lru_status,
                "expected_count": EXPECTED_LRU_COUNT,
                "actual_count": summary.lru_count,
            },
            "signal_bindings": {
                "status": signal_status,
                "expected_count": EXPECTED_SIGNAL_BINDING_COUNT,
                "actual_count": summary.signal_binding_count,
            },
        },
        "evidence_gaps": {
            "lru_field_count": summary.lru_evidence_gap_field_count,
            "signal_field_count": summary.signal_evidence_gap_field_count,
            "total_field_count": summary.total_evidence_gap_field_count,
            "inferred_field_count": summary.inferred_field_count,
        },
        "boundaries": {
            "read_only": summary.read_only,
            "controller_truth_modified": summary.controller_truth_modified,
            "truth_level_impact": summary.truth_level_impact,
            "dal_pssa_impact": summary.dal_pssa_impact,
            "frozen_hardware_paths": list(summary.frozen_hardware_paths),
        },
        "checks": checks,
    }

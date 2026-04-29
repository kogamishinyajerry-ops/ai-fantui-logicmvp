from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.hardware_registry import (  # noqa: E402
    hardware_evidence_summary_to_dict,
    load_hardware_evidence_summary,
)


OUTPUT_FORMATS = {"text", "json"}
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


def build_hardware_evidence_report() -> dict[str, Any]:
    summary = load_hardware_evidence_summary()
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
        "generated_by": "tools/validate_hardware_evidence_report.py",
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


def report_to_text(report: dict[str, Any]) -> list[str]:
    lines = [
        f"{'OK' if check['status'] == 'pass' else 'FAIL'} {check['name']}"
        for check in report["checks"]
    ]
    if report["status"] == "pass":
        lines.append("PASS: hardware evidence report is deterministic and read-only.")
    else:
        lines.append("FAIL: hardware evidence report has failing checks.")
    return lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_hardware_evidence_report.py [--format text|json]")


def emit_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for line in report_to_text(report):
        print(line)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = build_hardware_evidence_report()
    emit_report(report, output_format)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

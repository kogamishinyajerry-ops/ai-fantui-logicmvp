from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.hardware_schema import load_thrust_reverser_hardware


OUTPUT_FORMATS = {"text", "json"}
HARDWARE_PATH = PROJECT_ROOT / "config" / "hardware" / "thrust_reverser_hardware_v1.yaml"
FROZEN_HARDWARE_PATHS = {
    PROJECT_ROOT / "config" / "hardware" / "bleed_air_hardware_v1.yaml",
    PROJECT_ROOT / "config" / "hardware" / "c919_etras_hardware_v1.yaml",
    PROJECT_ROOT / "config" / "hardware" / "landing_gear_hardware_v1.yaml",
}
VALUE_REF_FIELDS = ("cable", "connector", "port_local", "port_peer")

EXPECTED_LRU_IDS = {
    "etrac",
    "pdu",
    "flexible_shafts",
    "mechanical_actuators",
    "tls",
    "pls",
    "vdt",
    "lock_sensors",
    "mdu",
    "cables",
    "mounting_brackets",
}

EXPECTED_SIGNAL_IDS = {
    "radio_altitude_ft",
    "SW1",
    "SW2",
    "reverser_inhibited",
    "reverser_not_deployed_eec",
    "engine_running",
    "aircraft_on_ground",
    "eec_enable",
    "tls_unlocked_ls",
    "n1k",
    "tra_deg",
    "deploy_90_percent_vdt",
    "tls_115vac_cmd",
    "etrac_540vdc_cmd",
    "eec_deploy_cmd",
    "pls_power_cmd",
    "pdu_motor_cmd",
    "throttle_electronic_lock_release_cmd",
}


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def make_check(name: str, status: str, **details: Any) -> dict[str, Any]:
    result = {"name": name, "status": status}
    result.update(details)
    return result


def validate_hardware_coupling() -> tuple[int, dict[str, Any], list[str]]:
    hw = load_thrust_reverser_hardware(HARDWARE_PATH)
    lrus = list(hw.lru_inventory)
    bindings = list(hw.signal_carrier_bindings)
    lru_ids = [item.id for item in lrus]
    signal_ids = [item.signal_id for item in bindings]

    checks: list[dict[str, Any]] = []

    missing_lrus = sorted(EXPECTED_LRU_IDS - set(lru_ids))
    extra_lrus = sorted(set(lru_ids) - EXPECTED_LRU_IDS)
    checks.append(
        make_check(
            "lru_inventory_coverage",
            "pass" if not missing_lrus and not extra_lrus and len(lrus) == len(EXPECTED_LRU_IDS) else "fail",
            expected_count=len(EXPECTED_LRU_IDS),
            actual_count=len(lrus),
            missing=missing_lrus,
            extra=extra_lrus,
            duplicates=duplicate_values(lru_ids),
        )
    )

    missing_signals = sorted(EXPECTED_SIGNAL_IDS - set(signal_ids))
    extra_signals = sorted(set(signal_ids) - EXPECTED_SIGNAL_IDS)
    checks.append(
        make_check(
            "signal_carrier_coverage",
            "pass"
            if not missing_signals and not extra_signals and len(bindings) == len(EXPECTED_SIGNAL_IDS)
            else "fail",
            expected_count=len(EXPECTED_SIGNAL_IDS),
            actual_count=len(bindings),
            missing=missing_signals,
            extra=extra_signals,
            duplicates=duplicate_values(signal_ids),
        )
    )

    incomplete_lru_refs = [
        item.id
        for item in lrus
        if item.part_number.status != "evidence_gap"
        or item.location.status != "evidence_gap"
        or item.failure_rate_per_hour.status != "evidence_gap"
    ]
    checks.append(
        make_check(
            "unknown_lru_fields_are_explicit_evidence_gaps",
            "pass" if not incomplete_lru_refs else "fail",
            offenders=sorted(incomplete_lru_refs),
        )
    )

    binding_gap_offenders: list[str] = []
    for binding in bindings:
        for field_name in VALUE_REF_FIELDS:
            field_value = getattr(binding, field_name)
            if field_value.status != "evidence_gap":
                binding_gap_offenders.append(f"{binding.signal_id}.{field_name}")
        if binding.evidence_status != "evidence_gap":
            binding_gap_offenders.append(f"{binding.signal_id}.evidence_status")
    checks.append(
        make_check(
            "unknown_signal_carriers_are_explicit_evidence_gaps",
            "pass" if not binding_gap_offenders else "fail",
            offenders=sorted(binding_gap_offenders),
        )
    )

    duplicate_lrus = duplicate_values(lru_ids)
    duplicate_signals = duplicate_values(signal_ids)
    checks.append(
        make_check(
            "ownership_rows_are_unique",
            "pass" if not duplicate_lrus and not duplicate_signals else "fail",
            duplicate_lru_ids=duplicate_lrus,
            duplicate_signal_ids=duplicate_signals,
        )
    )

    frozen_targets = [relative_path(path) for path in sorted(FROZEN_HARDWARE_PATHS)]
    checks.append(
        make_check(
            "frozen_hardware_write_scope",
            "pass",
            target=relative_path(HARDWARE_PATH),
            frozen_targets=frozen_targets,
            policy="checker reads only thrust_reverser_hardware_v1.yaml and never writes frozen hardware YAML",
        )
    )

    failed = [check for check in checks if check["status"] != "pass"]
    report = {
        "status": "pass" if not failed else "fail",
        "hardware_path": relative_path(HARDWARE_PATH),
        "lru_count": len(lrus),
        "signal_binding_count": len(bindings),
        "checks": checks,
    }

    text_lines = [
        f"{'OK' if check['status'] == 'pass' else 'FAIL'} {check['name']}"
        for check in checks
    ]
    if not failed:
        text_lines.append(
            "PASS: thrust-reverser hardware coupling inventory and signal bindings are deterministic."
        )
        return 0, report, text_lines

    text_lines.append("FAIL: thrust-reverser hardware coupling invariants did not pass.")
    return 1, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_thrust_reverser_hardware_coupling.py [--format text|json]")


def emit_report(report: dict[str, Any], text_lines: list[str], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for line in text_lines:
        print(line)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    exit_code, report, text_lines = validate_hardware_coupling()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

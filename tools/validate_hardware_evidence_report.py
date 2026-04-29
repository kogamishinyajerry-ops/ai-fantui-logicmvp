from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.hardware_evidence_report import build_hardware_evidence_report  # noqa: E402


OUTPUT_FORMATS = {"text", "json"}


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

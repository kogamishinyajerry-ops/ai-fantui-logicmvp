#!/usr/bin/env python3
"""Run all approved candidate repair slices and emit one aggregate summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_development_slice import (
    DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
    DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
    run_approved_repair_slices_gate,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Safety and Evidence approved candidate repair slices.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
        help="Directory where aggregate and child slice artifacts will be written.",
    )
    parser.add_argument(
        "--input-packet",
        type=Path,
        default=DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
        help="Candidate agent_output_contract_v0_1 packet to seed and repair.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = run_approved_repair_slices_gate(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"slice_count: {payload['aggregate']['slice_count']}")
        print(f"converged: {payload['aggregate']['converged']}")
        print(f"summary: {payload['artifact_paths']['summary']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

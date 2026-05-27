#!/usr/bin/env python3
"""Run the M8 fast construction gate package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_fast_construction_gate import (
    DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR,
    build_m8_fast_construction_gate,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M8 fast construction gate package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR,
        help="Directory where M8 fast-gate artifacts are written.",
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
    payload = build_m8_fast_construction_gate(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"ready_for_slice_preflight: {payload['aggregate']['ready_for_slice_preflight']}")
        print(f"fast_gate_package: {payload['artifact_paths']['fast_gate_package']}")
        print(f"queue_v0_2_summary: {payload['artifact_paths']['queue_v0_2_summary']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

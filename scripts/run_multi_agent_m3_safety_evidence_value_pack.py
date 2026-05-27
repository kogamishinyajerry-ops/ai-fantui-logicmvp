#!/usr/bin/env python3
"""Run the M3 Safety/Evidence deterministic finding value pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_safety_evidence_value_pack import (
    DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR,
    run_m3_safety_evidence_value_pack,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M3 Safety/Evidence value package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR,
        help="Directory where M3 value-pack artifacts are written.",
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
    payload = run_m3_safety_evidence_value_pack(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"slice_count: {payload['aggregate']['slice_count']}")
        print(f"converged: {payload['aggregate']['converged']}")
        print(f"package: {payload['artifact_paths']['package']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

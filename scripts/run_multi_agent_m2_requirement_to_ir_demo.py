#!/usr/bin/env python3
"""Run the M2 Requirement -> IR candidate-only demo chain."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_requirement_to_ir_demo import (
    DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR,
    run_m2_requirement_to_ir_demo,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M2 Requirement to IR demo package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR,
        help="Directory where M2 demo artifacts are written.",
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
    payload = run_m2_requirement_to_ir_demo(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"reviewer_status: {payload['review_export']['reviewer_status']}")
        print(f"demo_package: {payload['artifact_paths']['demo_package']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the M4 external review handoff package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_external_review_handoff import (
    DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR,
    build_m4_external_review_handoff,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M4 external review handoff package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR,
        help="Directory where M4 handoff artifacts are written.",
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
    payload = build_m4_external_review_handoff(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"readiness_status: {payload['review_summary']['readiness_status']}")
        print(f"handoff_package: {payload['artifact_paths']['handoff_package']}")
        print(f"human_review_report: {payload['artifact_paths']['human_review_report']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

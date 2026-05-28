#!/usr/bin/env python3
"""Validate the approved repair slices aggregate artifact and child exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_development_slice import (
    DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
    verify_approved_repair_slices_artifact,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify approved repair slices aggregate summary and child review exports.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
        help="Directory containing approved_repair_slices_summary.json.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Explicit aggregate summary path. Overrides --artifact-dir.",
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
    payload = verify_approved_repair_slices_artifact(
        artifact_dir=args.artifact_dir,
        summary_path=args.summary,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"summary_valid: {payload['summary_valid']}")
        print(f"summary_schema_valid: {payload['summary_schema_valid']}")
        print(f"child_review_exports_valid: {payload['child_review_exports_valid']}")
        print(f"summary: {payload['artifact_paths']['summary']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the approved Evidence candidate repair slice and emit review evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_development_slice import (
    DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
    DEFAULT_EVIDENCE_ARTIFACT_DIR,
    run_evidence_candidate_repair_slice,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the approved Evidence Agent candidate repair slice.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_ARTIFACT_DIR,
        help="Directory where slice evidence artifacts will be written.",
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
    payload = run_evidence_candidate_repair_slice(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"slice_id: {payload['slice_id']}")
        print(f"status: {payload['status']}")
        print(f"selected_task: {payload['selected_task']['task_id']}")
        print(f"reviewer_status: {payload['reviewer_status']}")
        print(f"artifact_dir: {args.artifact_dir}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

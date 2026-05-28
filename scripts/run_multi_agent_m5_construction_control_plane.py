#!/usr/bin/env python3
"""Run the M5 long-running construction control plane."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_construction_control_plane import (
    DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR,
    build_m5_construction_control_plane,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M5 construction control-plane package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR,
        help="Directory where M5 control-plane artifacts are written.",
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
    payload = build_m5_construction_control_plane(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"readiness_status: {payload['control_plane_summary']['readiness_status']}")
        print(f"entrypoint: {payload['control_plane_summary']['entrypoint']}")
        print(f"control_plane_package: {payload['artifact_paths']['control_plane_package']}")
        print(f"operator_runbook: {payload['artifact_paths']['operator_runbook']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

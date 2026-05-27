#!/usr/bin/env python3
"""Run the M6 approved queue extension template package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.agent_queue_extension_template import (
    DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR,
    build_m6_queue_extension_template,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M6 approved queue extension template package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR,
        help="Directory where M6 queue-extension template artifacts are written.",
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
    payload = build_m6_queue_extension_template(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"readiness_status: {payload['template_summary']['readiness_status']}")
        print(f"template_package: {payload['artifact_paths']['template_package']}")
        print(f"operator_template_guide: {payload['artifact_paths']['operator_template_guide']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

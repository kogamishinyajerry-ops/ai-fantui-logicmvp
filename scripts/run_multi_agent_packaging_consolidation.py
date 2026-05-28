#!/usr/bin/env python3
"""Generate the M23 multi-agent packaging consolidation artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.multi_agent_packaging_consolidation import (
    JSON_NAME,
    build_multi_agent_packaging_consolidation,
    write_multi_agent_packaging_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-packaging-consolidation")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M23 explicit-pathspec packaging consolidation artifact.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def run_multi_agent_packaging_consolidation(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict:
    payload = build_multi_agent_packaging_consolidation(project_root=PROJECT_ROOT)
    return write_multi_agent_packaging_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_packaging_consolidation(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"package: {payload['artifact_paths']['package_html']}")
        print(f"json: {payload['artifact_paths'].get('package_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the M24 multi-agent PR preflight artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.multi_agent_pr_preflight import (
    JSON_NAME,
    build_multi_agent_pr_preflight,
    write_multi_agent_pr_preflight_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-pr-preflight")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M24 validation and PR body preflight artifact.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def run_multi_agent_pr_preflight(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict:
    payload = build_multi_agent_pr_preflight(project_root=PROJECT_ROOT)
    return write_multi_agent_pr_preflight_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_pr_preflight(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"package: {payload['artifact_paths']['preflight_html']}")
        print(f"json: {payload['artifact_paths'].get('preflight_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

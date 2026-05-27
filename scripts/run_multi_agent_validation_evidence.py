#!/usr/bin/env python3
"""Generate the M25 multi-agent validation evidence artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from well_harness.multi_agent_validation_evidence import (
    JSON_NAME,
    build_multi_agent_validation_evidence,
    write_multi_agent_validation_evidence_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-validation-evidence")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate M25 evidence by running the M24 validation plan.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--command-results", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _load_command_results(path: Path | None) -> list[dict] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_multi_agent_validation_evidence(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    command_results_path: Path | None = None,
) -> dict:
    payload = build_multi_agent_validation_evidence(
        project_root=PROJECT_ROOT,
        command_results=_load_command_results(command_results_path),
    )
    return write_multi_agent_validation_evidence_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_validation_evidence(
        artifact_dir=args.artifact_dir,
        command_results_path=args.command_results,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"package: {payload['artifact_paths']['evidence_html']}")
        print(f"json: {payload['artifact_paths'].get('evidence_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

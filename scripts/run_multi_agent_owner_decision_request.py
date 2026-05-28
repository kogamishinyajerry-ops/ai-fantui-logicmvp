#!/usr/bin/env python3
"""Generate the M33 owner decision request."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from well_harness.multi_agent_owner_decision_request import (
    JSON_NAME,
    build_multi_agent_owner_decision_request,
    write_multi_agent_owner_decision_request_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-decision-request")
DEFAULT_OWNER_ACCEPTANCE_HANDOFF = (
    Path("/tmp/ai-fantui-multi-agent-owner-acceptance-handoff")
    / "multi_agent_owner_acceptance_handoff_v0_1.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate M33 owner decision request.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--owner-acceptance-handoff", type=Path, default=DEFAULT_OWNER_ACCEPTANCE_HANDOFF)
    parser.add_argument("--refresh-owner-acceptance-handoff", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    env.setdefault("AI_FANTUI_QUEUE_PREFLIGHT_MODE", "fixture")
    return env


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_owner_acceptance_handoff(owner_acceptance_handoff: Path) -> None:
    artifact_dir = owner_acceptance_handoff.parent
    result = subprocess.run(
        [
            "python3",
            "scripts/run_multi_agent_owner_acceptance_handoff.py",
            "--refresh-release-decision-input",
            "--artifact-dir",
            str(artifact_dir),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def run_multi_agent_owner_decision_request(
    *,
    artifact_dir: Path,
    owner_acceptance_handoff_path: Path,
    refresh_owner_acceptance_handoff: bool = False,
) -> dict[str, Any]:
    """Generate and write the M33 owner decision request package."""
    if refresh_owner_acceptance_handoff:
        _run_owner_acceptance_handoff(owner_acceptance_handoff_path)
    owner_acceptance_handoff = _load_json(owner_acceptance_handoff_path)
    return write_multi_agent_owner_decision_request_artifacts(
        build_multi_agent_owner_decision_request(
            owner_acceptance_handoff=owner_acceptance_handoff,
        ),
        artifact_dir=artifact_dir,
    )


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_owner_decision_request(
        artifact_dir=args.artifact_dir,
        owner_acceptance_handoff_path=args.owner_acceptance_handoff,
        refresh_owner_acceptance_handoff=args.refresh_owner_acceptance_handoff,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"request: {payload['artifact_paths'].get('request_html') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())

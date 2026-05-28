#!/usr/bin/env python3
"""Generate the read-only multi-agent operator cockpit package."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.multi_agent_operator_cockpit import (
    JSON_NAME,
    build_multi_agent_operator_cockpit,
    write_multi_agent_operator_cockpit_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-operator-cockpit")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the M22 multi-agent operator cockpit package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory where cockpit artifacts will be written.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    env.setdefault("AI_FANTUI_QUEUE_PREFLIGHT_MODE", "fixture")
    return env


def _run_json(command: list[str], *, timeout: int = 300) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not emit JSON: {' '.join(command)}\n{result.stderr}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(command)}")
    return payload


def run_multi_agent_operator_cockpit(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    project_status = _run_json(
        [
            sys.executable,
            "scripts/run_project_manager_status_summary.py",
            "--artifact-dir",
            str(artifact_dir / "project-manager-status"),
            "--format",
            "json",
        ],
    )
    ultrawork_dashboard = _run_json(
        [
            sys.executable,
            "scripts/run_ultrawork_monitor_dashboard.py",
            "--resume-mode",
            "ready-to-resume",
            "--artifact-dir",
            str(artifact_dir / "ultrawork-monitor"),
            "--format",
            "json",
        ],
    )
    cockpit = build_multi_agent_operator_cockpit(
        project_status=project_status,
        ultrawork_dashboard=ultrawork_dashboard,
    )
    return write_multi_agent_operator_cockpit_artifacts(cockpit, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_operator_cockpit(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"cockpit: {payload['artifact_paths']['cockpit_html']}")
        print(f"json: {payload['artifact_paths'].get('cockpit_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

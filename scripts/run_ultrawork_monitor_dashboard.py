#!/usr/bin/env python3
"""Generate the UltraWork-style multi-agent monitor dashboard."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.ultrawork_monitor_dashboard import (
    JSON_NAME,
    build_ultrawork_monitor_dashboard,
    write_ultrawork_dashboard_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-ultrawork-monitor-dashboard")
CURSOR_NAME = "multi_agent_queue_cursor_state_v0_2.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an UltraWork-style multi-agent monitor dashboard.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory where dashboard artifacts will be written.",
    )
    parser.add_argument(
        "--cursor",
        type=Path,
        default=None,
        help="Existing multi_agent_queue_cursor_state_v0_2.json to render.",
    )
    parser.add_argument(
        "--resume-mode",
        choices=("idle", "ready-to-resume"),
        default="idle",
        help="Cursor scenario to generate when --cursor is not supplied.",
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_cursor(*, artifact_dir: Path, resume_mode: str) -> Path:
    cursor_artifact_dir = artifact_dir / "source-cursor"
    command = [
        sys.executable,
        "scripts/run_multi_agent_queue_cursor_state_v0_2.py",
        "--artifact-dir",
        str(cursor_artifact_dir),
        "--resume-mode",
        resume_mode,
        "--format",
        "json",
    ]
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"cursor runner did not emit JSON: {result.stderr}") from exc
    if result.returncode != 0 or payload.get("status") != "pass":
        raise RuntimeError(f"cursor runner failed: {payload.get('status')}")
    cursor_path = Path(str(payload.get("artifact_paths", {}).get("cursor_state", "")))
    if not cursor_path.exists():
        cursor_path = cursor_artifact_dir / CURSOR_NAME
    return cursor_path


def run_ultrawork_monitor_dashboard(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    cursor_path: Path | None = None,
    resume_mode: str = "idle",
) -> dict[str, Any]:
    if cursor_path is None:
        cursor_path = _run_cursor(artifact_dir=artifact_dir, resume_mode=resume_mode)
    cursor = _load_json(cursor_path)
    dashboard = build_ultrawork_monitor_dashboard(
        cursor,
        source_cursor_path=str(cursor_path),
    )
    return write_ultrawork_dashboard_artifacts(dashboard, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_ultrawork_monitor_dashboard(
        artifact_dir=args.artifact_dir,
        cursor_path=args.cursor,
        resume_mode=args.resume_mode,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"summary: {payload['summary']['status']} / {payload['summary']['next_action']}")
        print(f"dashboard: {payload['artifact_paths']['dashboard_html']}")
        print(f"json: {payload['artifact_paths'].get('dashboard_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

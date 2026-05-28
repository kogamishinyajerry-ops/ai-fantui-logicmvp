#!/usr/bin/env python3
"""Generate the M31 multi-agent release decision input."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from well_harness.multi_agent_release_decision_input import (
    JSON_NAME,
    build_multi_agent_release_decision_input,
    write_multi_agent_release_decision_input_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-release-decision-input")
DEFAULT_REVIEW_CLOSURE_PATH = (
    Path("/tmp/ai-fantui-multi-agent-review-closure")
    / "multi_agent_review_closure_v0_1.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate M31 release decision input from an M30 review closure packet.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--review-closure", type=Path, default=DEFAULT_REVIEW_CLOSURE_PATH)
    parser.add_argument("--refresh-review-closure", action="store_true")
    parser.add_argument("--pr-number", type=int, default=270)
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


def _refresh_review_closure(path: Path, *, pr_number: int) -> None:
    result = subprocess.run(
        [
            "python3",
            "scripts/run_multi_agent_review_closure.py",
            "--format",
            "json",
            "--artifact-dir",
            str(path.parent),
            "--pr-number",
            str(pr_number),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def run_multi_agent_release_decision_input(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    review_closure_path: Path = DEFAULT_REVIEW_CLOSURE_PATH,
    refresh_review_closure: bool = False,
    pr_number: int = 270,
) -> dict[str, Any]:
    if refresh_review_closure or not review_closure_path.exists():
        _refresh_review_closure(review_closure_path, pr_number=pr_number)
    review_closure = _load_json(review_closure_path)
    payload = build_multi_agent_release_decision_input(review_closure=review_closure)
    return write_multi_agent_release_decision_input_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_release_decision_input(
        artifact_dir=args.artifact_dir,
        review_closure_path=args.review_closure,
        refresh_review_closure=args.refresh_review_closure,
        pr_number=args.pr_number,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"decision_input: {payload['artifact_paths']['decision_input_html']}")
        print(
            "json: "
            f"{payload['artifact_paths'].get('decision_input_json') or args.artifact_dir / JSON_NAME}"
        )
    return 0 if payload.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())

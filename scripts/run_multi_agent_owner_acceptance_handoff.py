#!/usr/bin/env python3
"""Generate the M32 owner acceptance handoff."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from well_harness.multi_agent_owner_acceptance_handoff import (
    JSON_NAME,
    build_multi_agent_owner_acceptance_handoff,
    write_multi_agent_owner_acceptance_handoff_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-acceptance-handoff")
DEFAULT_RELEASE_DECISION_INPUT = (
    Path("/tmp/ai-fantui-multi-agent-release-decision-input")
    / "multi_agent_release_decision_input_v0_1.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate M32 owner acceptance handoff.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--release-decision-input", type=Path, default=DEFAULT_RELEASE_DECISION_INPUT)
    parser.add_argument("--refresh-release-decision-input", action="store_true")
    parser.add_argument("--pr-status-json", type=Path, default=None)
    parser.add_argument("--review-threads-json", type=Path, default=None)
    parser.add_argument("--pr-number", type=int, default=271)
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


def _run_release_decision_input(release_decision_input: Path) -> None:
    artifact_dir = release_decision_input.parent
    result = subprocess.run(
        [
            "python3",
            "scripts/run_multi_agent_release_decision_input.py",
            "--refresh-review-closure",
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
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def _run_json(command: list[str], *, timeout: int = 120) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    if result.returncode != 0:
        return {
            "number": 0,
            "url": "",
            "state": "UNKNOWN",
            "mergeStateStatus": "UNKNOWN",
            "headRefOid": "",
            "statusCheckRollup": [],
            "reviews": [],
            "comments": [],
            "error": result.stderr.strip() or result.stdout.strip(),
        }
    return json.loads(result.stdout)


def _load_pr_status(pr_status_json: Path | None, *, pr_number: int) -> dict[str, Any]:
    if pr_status_json is not None:
        return _load_json(pr_status_json)
    return _run_json(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,url,state,mergeStateStatus,headRefOid,statusCheckRollup,reviews,comments",
        ],
    )


def _load_review_threads(review_threads_json: Path | None, *, pr_number: int) -> list[dict[str, Any]]:
    if review_threads_json is not None:
        payload = _load_json(review_threads_json)
        nodes = payload.get("nodes", payload)
        return nodes if isinstance(nodes, list) else []
    query = (
        "query($owner:String!, $name:String!, $number:Int!) { "
        "repository(owner:$owner, name:$name) { "
        "pullRequest(number:$number) { "
        "reviewThreads(first:100) { nodes { "
        "id isResolved isOutdated path line startLine "
        "comments(first:20) { nodes { author { login } createdAt body commit { oid } url } } "
        "} } } } }"
    )
    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            "owner=kogamishinyajerry-ops",
            "-f",
            "name=ai-fantui-logicmvp",
            "-F",
            f"number={pr_number}",
            "-f",
            f"query={query}",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        return []
    payload = json.loads(result.stdout)
    return payload["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]


def run_multi_agent_owner_acceptance_handoff(
    *,
    artifact_dir: Path,
    release_decision_input_path: Path,
    refresh_release_decision_input: bool = False,
    pr_status_json: Path | None = None,
    review_threads_json: Path | None = None,
    pr_number: int = 271,
) -> dict[str, Any]:
    """Generate and write the M32 owner acceptance handoff package."""
    if refresh_release_decision_input:
        _run_release_decision_input(release_decision_input_path)
    release_decision_input = _load_json(release_decision_input_path)
    pr_status = _load_pr_status(pr_status_json, pr_number=pr_number)
    review_threads = _load_review_threads(review_threads_json, pr_number=pr_number)
    return write_multi_agent_owner_acceptance_handoff_artifacts(
        build_multi_agent_owner_acceptance_handoff(
            release_decision_input=release_decision_input,
            pr_status=pr_status,
            review_threads=review_threads,
        ),
        artifact_dir=artifact_dir,
    )


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_owner_acceptance_handoff(
        artifact_dir=args.artifact_dir,
        release_decision_input_path=args.release_decision_input,
        refresh_release_decision_input=args.refresh_release_decision_input,
        pr_status_json=args.pr_status_json,
        review_threads_json=args.review_threads_json,
        pr_number=args.pr_number,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"package: {payload['artifact_paths']['handoff_json']}")
        print(f"html: {payload['artifact_paths']['handoff_html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

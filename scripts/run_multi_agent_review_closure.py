#!/usr/bin/env python3
"""Generate the M30 multi-agent review-closure packet."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from well_harness.multi_agent_review_closure import (
    JSON_NAME,
    build_multi_agent_review_closure,
    write_multi_agent_review_closure_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-review-closure")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate M30 review-closure artifacts from PR status and review threads.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--pr-status-json", type=Path, default=None)
    parser.add_argument("--review-threads-json", type=Path, default=None)
    parser.add_argument("--pr-number", type=int, default=270)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    env.setdefault("AI_FANTUI_QUEUE_PREFLIGHT_MODE", "fixture")
    return env


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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
        loaded = _load_json(pr_status_json)
        if isinstance(loaded, dict):
            return loaded
        raise TypeError("pr status fixture must be a JSON object")
    return _run_json(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,url,state,mergeStateStatus,headRefOid,statusCheckRollup,reviews,comments",
        ],
        timeout=120,
    )


def _run_graphql_threads(*, pr_number: int) -> list[dict[str, Any]]:
    query = """
query($owner:String!,$repo:String!,$number:Int!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$number){
      reviewThreads(first:100){
        nodes{
          isResolved
          isOutdated
          path
          line
          startLine
          comments(first:20){
            nodes{
              author{login}
              body
              createdAt
              commit{oid}
            }
          }
        }
      }
    }
  }
}
"""
    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            "owner=kogamishinyajerry-ops",
            "-F",
            "repo=ai-fantui-logicmvp",
            "-F",
            f"number={pr_number}",
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
    nodes = (
        payload.get("data", {})
        .get("repository", {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes", [])
    )
    return nodes if isinstance(nodes, list) else []


def _load_review_threads(review_threads_json: Path | None, *, pr_number: int) -> list[dict[str, Any]]:
    if review_threads_json is not None:
        loaded = _load_json(review_threads_json)
        if isinstance(loaded, dict):
            loaded = loaded.get("reviewThreads", loaded.get("nodes", []))
        if isinstance(loaded, list):
            return [item for item in loaded if isinstance(item, dict)]
        raise TypeError("review threads fixture must be a JSON array or object with reviewThreads")
    return _run_graphql_threads(pr_number=pr_number)


def run_multi_agent_review_closure(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    pr_status_json: Path | None = None,
    review_threads_json: Path | None = None,
    pr_number: int = 270,
) -> dict[str, Any]:
    pr_status = _load_pr_status(pr_status_json, pr_number=pr_number)
    review_threads = _load_review_threads(review_threads_json, pr_number=pr_number)
    payload = build_multi_agent_review_closure(
        pr_status=pr_status,
        review_threads=review_threads,
    )
    return write_multi_agent_review_closure_artifacts(payload, artifact_dir=artifact_dir)


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_review_closure(
        artifact_dir=args.artifact_dir,
        pr_status_json=args.pr_status_json,
        review_threads_json=args.review_threads_json,
        pr_number=args.pr_number,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"closure: {payload['artifact_paths']['closure_html']}")
        print(f"json: {payload['artifact_paths'].get('closure_json') or args.artifact_dir / JSON_NAME}")
    return 0 if payload.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())

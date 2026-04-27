"""CLI entry for the skill executor.

Usage:

    # Foreground execution — waits for workbench approval inline
    python3 -m well_harness.skill_executor execute PROP-XXX

    # With explicit repo root (defaults to current dir)
    python3 -m well_harness.skill_executor execute PROP-XXX --repo-root /path/to/repo

    # Auto-approve (DANGER — for CI/dogfood, NOT for engineer use)
    python3 -m well_harness.skill_executor execute PROP-XXX --auto-approve

    # Show audit details for an existing execution
    python3 -m well_harness.skill_executor show EXEC-XXX

The `execute` subcommand walks the orchestrator pipeline. While in
ASKING state, it prints a clear "waiting for workbench approval"
message and polls every second. The user goes to /workbench, sees
the pending ask card on the proposal, and clicks Approve/Reject.

Exit codes:
  0 — success (LANDED or PR_OPEN)
  1 — pipeline aborted (user reject, test gate, etc.)
  2 — pipeline failed (planner error, git error, etc.)
  3 — bad invocation (missing PROP id, invalid args)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from well_harness.skill_executor.audit import audit_dir as default_audit_dir
from well_harness.skill_executor.audit import read_audit
from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.orchestrator import execute_proposal
from well_harness.skill_executor.states import ExecutionState
from well_harness.skill_executor.workbench_polling import (
    WorkbenchApprovalCallback,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-executor",
        description="Execute an accepted workbench proposal "
                    "through the standardized skill executor pipeline.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    execute = sub.add_parser(
        "execute",
        help="Run a proposal through the executor pipeline.",
    )
    execute.add_argument(
        "proposal_id",
        help="The PROP-XXX id to execute. Must be ACCEPTED.",
    )
    execute.add_argument(
        "--repo-root",
        default=".",
        help="Repo root (default: cwd).",
    )
    execute.add_argument(
        "--audit-dir",
        default=None,
        help="Where to write EXEC-*.json audits "
             "(default: <repo>/.planning/skill_executions).",
    )
    execute.add_argument(
        "--auto-approve",
        action="store_true",
        help="DANGER: skip ASKING approval. Use only for CI/dogfood.",
    )
    execute.add_argument(
        "--skip-pr",
        action="store_true",
        help="Don't open a PR (test mode). Branch + commit still happen.",
    )
    execute.add_argument(
        "--skip-push",
        action="store_true",
        help="Don't push the branch (test mode).",
    )
    execute.add_argument(
        "--approval-timeout-sec",
        type=float,
        default=3600.0,
        help="ASKING-state polling timeout (default: 3600s = 1 hour).",
    )
    execute.add_argument(
        "--poll-interval-sec",
        type=float,
        default=1.0,
        help="ASKING-state polling interval (default: 1.0s).",
    )

    show = sub.add_parser(
        "show",
        help="Print an existing audit record by EXEC id.",
    )
    show.add_argument(
        "exec_id",
        help="EXEC-XXX id to inspect.",
    )

    args = parser.parse_args(argv)
    if args.cmd == "execute":
        return _run_execute(args)
    if args.cmd == "show":
        return _run_show(args)
    parser.print_help()
    return 3


def _run_execute(args) -> int:
    repo_root = Path(args.repo_root).resolve()
    audit_dir = (
        Path(args.audit_dir).expanduser().resolve()
        if args.audit_dir
        else repo_root / ".planning" / "skill_executions"
    )
    audit_dir.mkdir(parents=True, exist_ok=True)

    callback = None
    if not args.auto_approve:
        callback = WorkbenchApprovalCallback(
            audit_dir=audit_dir,
            poll_interval_sec=args.poll_interval_sec,
            timeout_sec=args.approval_timeout_sec,
        )

    print(f"Executing proposal {args.proposal_id}…")
    print(f"  repo_root: {repo_root}")
    print(f"  audit_dir: {audit_dir}")
    if args.auto_approve:
        print("  ⚠ auto-approve enabled — skipping ASK")
    else:
        print("  ⏳ on ASKING state, will poll for workbench approval "
              f"every {args.poll_interval_sec}s "
              f"(timeout {args.approval_timeout_sec}s)")
    print()

    result = execute_proposal(
        proposal_id=args.proposal_id,
        repo_root=repo_root,
        audit_dir=audit_dir,
        approval_callback=callback,
        auto_approve=args.auto_approve,
        skip_pr=args.skip_pr,
        skip_push=args.skip_push,
    )

    record = result.record
    print()
    print(f"Execution finished — state: {record.state}")
    print(f"  exec_id:  {record.exec_id}")
    print(f"  audit:    {audit_dir / (record.exec_id + '.json')}")
    if record.branch:
        print(f"  branch:   {record.branch}")
    if record.commits:
        print(f"  commits:  {record.commits}")
    if record.pr_url:
        print(f"  pr:       {record.pr_url}")
    if record.abort_reason:
        print(f"  reason:   {record.abort_reason}")

    state = record.state
    if state in (ExecutionState.LANDED.value, ExecutionState.PR_OPEN.value):
        return 0
    if state == ExecutionState.ABORTED.value:
        return 1
    return 2


def _run_show(args) -> int:
    try:
        record = read_audit(args.exec_id)
    except SkillExecutorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    import json
    print(json.dumps(record.to_json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

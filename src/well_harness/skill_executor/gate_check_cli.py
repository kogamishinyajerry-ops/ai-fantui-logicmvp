"""CLI entry point for the PR-merge gate.

Designed to be invoked from a GitHub Action:

    python3 -m well_harness.skill_executor.gate_check_cli verify-pr \\
        --body-file pr-body.txt \\
        --changed-files-file pr-changed.txt \\
        --repo-root .

Exit code 0 = pass (or gate not required), 1 = block. stdout
contains a human-readable verdict the workflow surfaces as a PR
comment.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from well_harness.skill_executor.gate_check import (
    GateCheckResult,
    check_pr_audit_compliance,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-executor-gate-check",
        description="Verify a PR's EXEC-id audit stamp against the "
                    "audit JSON in the repo tree.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    verify = sub.add_parser(
        "verify-pr",
        help="Run the PR audit gate against a single PR.",
    )
    verify.add_argument(
        "--body-file",
        required=True,
        help="Path to a file containing the PR body text.",
    )
    verify.add_argument(
        "--changed-files-file",
        required=True,
        help=(
            "Path to a file listing the PR's changed files, one per "
            "line. Generate via `gh pr view --json files -q "
            "'.files[].path'` or `git diff --name-only`."
        ),
    )
    verify.add_argument(
        "--repo-root",
        default=".",
        help="Repo root for resolving audit paths. Default: cwd.",
    )

    args = parser.parse_args(argv)
    if args.cmd != "verify-pr":
        parser.print_help()
        return 2

    try:
        body = Path(args.body_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read body file: {exc}", file=sys.stderr)
        return 2
    try:
        changed_raw = Path(args.changed_files_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read changed-files file: {exc}", file=sys.stderr)
        return 2
    changed_files = [
        line.strip() for line in changed_raw.splitlines() if line.strip()
    ]

    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=changed_files,
        repo_root=Path(args.repo_root),
    )
    _print_result(result)
    return 0 if result.ok else 1


def _print_result(result: GateCheckResult) -> None:
    """Human-readable report. Format is stable enough for a GitHub
    Action to copy into a PR comment without further processing."""
    print("# Skill-Executor PR Audit Gate")
    print()
    if result.ok and not result.gate_required:
        print("✅ **Pass — gate not required**")
        print()
        print("This PR does not touch any truth-engine namespace "
              "files, so the executor audit gate does not apply.")
        return
    if result.ok:
        print("✅ **Pass — audit chain validated**")
    else:
        print("❌ **Block — audit chain failed**")
    print()
    print("**Files matched against PANEL_NAMESPACES:**")
    for f in result.matched_files:
        print(f"- `{f}`")
    print()
    if result.stamp:
        print("**Parsed stamp:**")
        print(f"- Exec-Id: `{result.stamp.get('exec_id', '—')}`")
        print(f"- Proposal: `{result.stamp.get('proposal', '—')}`")
        print(f"- Audit: `{result.stamp.get('audit', '—')}`")
        print(
            f"- Skill-Executor-Version: "
            f"`{result.stamp.get('skill_executor_version', '—')}`"
        )
        print()
    print("**Reasons:**")
    for r in result.reasons:
        print(f"- {r}")


if __name__ == "__main__":
    sys.exit(main())

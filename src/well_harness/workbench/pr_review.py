from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

from well_harness.collab.restricted_auth import RestrictedAuthError, validate_push_attempt


_DIFF_GIT_RE = re.compile(r"^diff --git a/(.*?) b/(.*?)$")
_PLUS_PATH_RE = re.compile(r"^\+\+\+ b/(.*?)$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extract_changed_files(diff_text: str) -> list[str]:
    changed: list[str] = []
    seen: set[str] = set()
    for line in diff_text.splitlines():
        match = _DIFF_GIT_RE.match(line)
        if match:
            path = match.group(2)
        else:
            plus_match = _PLUS_PATH_RE.match(line)
            if not plus_match:
                continue
            path = plus_match.group(1)
            if path == "/dev/null":
                continue
        if path not in seen:
            changed.append(path)
            seen.add(path)
    return changed


def review_pr_diff(ticket: dict[str, Any], diff_text: str) -> dict[str, Any]:
    changed_files = extract_changed_files(diff_text)
    findings: list[dict[str, str]] = []
    verdict = "accepted"
    if not changed_files:
        verdict = "rejected"
        findings.append({"severity": "blocking", "message": "No changed files could be extracted from the PR diff."})
    else:
        try:
            validate_push_attempt(
                ticket,
                engineer=str(ticket.get("Authorized Engineer") or ""),
                changed_files=changed_files,
            )
        except RestrictedAuthError as exc:
            verdict = "rejected"
            findings.append({"severity": "blocking", "message": str(exc)})

    return {
        "ticket_id": ticket.get("Task", ""),
        "source_proposal": ticket.get("Source Proposal", ""),
        "pr_url": ticket.get("PR URL", ""),
        "verdict": verdict,
        "changed_files": changed_files,
        "findings": findings,
        "reviewed_at": _utc_now(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a Workbench ticket against a candidate PR diff.")
    parser.add_argument("ticket", help="Path to the ticket JSON payload.")
    parser.add_argument("diff", help="Path to the unified diff, or '-' for stdin.")
    args = parser.parse_args(argv)

    ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
    if args.diff == "-":
        diff_text = sys.stdin.read()
    else:
        diff_text = Path(args.diff).read_text(encoding="utf-8")
    report = review_pr_diff(ticket, diff_text)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "accepted" else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

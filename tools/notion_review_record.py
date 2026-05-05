#!/usr/bin/env python3
"""Write Notion documentation records for review evidence.

Notion is treated as a documentation and evidence record center only. This
tool does not mention users, does not trigger bots, and does not claim Notion AI
or Opus has reviewed anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence, cast


PAGE_ID_RE = re.compile(r"([0-9a-fA-F]{32})")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


@dataclass(frozen=True)
class NotionApiError(Exception):
    status: int
    body: str

    def __str__(self) -> str:
        return f"Notion API error {self.status}: {self.body}"


def extract_notion_page_id(value: str) -> str:
    compact = value.replace("-", "")
    match = PAGE_ID_RE.search(compact)
    if not match:
        raise ValueError(f"Could not find a Notion page id in {value!r}")
    return match.group(1).lower()


def _pr_label(pr_url: str) -> str:
    match = re.search(r"/pull/(\d+)(?:\b|$)", pr_url)
    if match:
        return f"PR #{match.group(1)}"
    return "target PR"


def build_review_record_text(
    *,
    pr_url: str,
    linear: str,
    decision: str,
    evidence: Sequence[str],
) -> str:
    evidence_text = "; ".join(evidence) if evidence else "none recorded"
    return (
        f"DOCUMENTATION_RECORD: {_pr_label(pr_url)} ({pr_url}) / {linear}. "
        f"Decision: {decision} "
        f"Evidence: {evidence_text}. "
        "Notion is documentation only; this record does not trigger Notion AI, "
        "Opus, CFDJerry, or any reviewer workflow."
    )


def build_plain_text_comment_payload(*, page_id: str, comment_text: str) -> Dict[str, Any]:
    return {
        "parent": {"page_id": page_id},
        "rich_text": [{"type": "text", "text": {"content": comment_text}}],
    }


def classify_notion_error(error: NotionApiError) -> str:
    body = error.body.lower()
    if error.status == 400 and "cannot mention bots" in body:
        return "bot_mention_unsupported"
    if error.status == 403 and "insufficient permissions" in body:
        return "comment_permission_denied"
    if "validation_error" in body:
        return "validation_error"
    return "notion_api_error"


def _notion_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def post_comment(payload: Mapping[str, Any], *, token: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        f"{NOTION_API_URL}/comments",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=_notion_headers(token),
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return cast(Dict[str, Any], json.loads(response.read().decode("utf-8")))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise NotionApiError(status=exc.code, body=body) from exc


def build_dry_run_report(
    *,
    target_page: str,
    pr_url: str,
    linear: str,
    decision: str,
    evidence: Sequence[str],
) -> Dict[str, Any]:
    page_id = extract_notion_page_id(target_page)
    record_text = build_review_record_text(
        pr_url=pr_url,
        linear=linear,
        decision=decision,
        evidence=evidence,
    )
    return {
        "mode": "dry_run",
        "notion_role": "documentation_record_only",
        "target_page_id": page_id,
        "review_execution_claim": "not_applicable",
        "prepared_payload": build_plain_text_comment_payload(
            page_id=page_id,
            comment_text=record_text,
        ),
    }


def execute_live_write(*, prepared_payload: Mapping[str, Any], token: str) -> Dict[str, Any]:
    try:
        response = post_comment(prepared_payload, token=token)
        return {"status": "posted", "id": response.get("id")}
    except NotionApiError as error:
        return {"status": classify_notion_error(error), "http_status": error.status}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-page", required=True)
    parser.add_argument("--pr-url", required=True)
    parser.add_argument("--linear", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--confirm-write", action="store_true")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser


def _print_text(report: Mapping[str, Any]) -> None:
    print(f"mode: {report['mode']}")
    print(f"notion_role: {report['notion_role']}")
    print(f"target_page_id: {report['target_page_id']}")
    print(f"review_execution_claim: {report['review_execution_claim']}")
    if "live_result" in report:
        print(f"live_result: {report['live_result']}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_dry_run_report(
        target_page=args.target_page,
        pr_url=args.pr_url,
        linear=args.linear,
        decision=args.decision,
        evidence=args.evidence,
    )

    if args.confirm_write:
        token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
        if not token:
            raise SystemExit("NOTION_API_KEY or NOTION_TOKEN is required for --confirm-write")
        report = dict(report)
        report["mode"] = "live"
        report["live_result"] = execute_live_write(
            prepared_payload=report["prepared_payload"],
            token=token,
        )

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

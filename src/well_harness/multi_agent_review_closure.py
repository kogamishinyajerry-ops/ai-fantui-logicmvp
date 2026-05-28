"""Read-only PR review-closure packet for the multi-agent lane."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_review_closure_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-review-closure"
CLOSURE_ID = "multi-agent-review-closure-v0.1"
JSON_NAME = "multi_agent_review_closure_v0_1.json"
MARKDOWN_NAME = "multi_agent_review_closure_v0_1.md"
HTML_NAME = "multi_agent_review_closure_v0_1.html"
CODEX_AUTHOR = "chatgpt-codex-connector"
M30_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-review-closure.md",
    "docs/json_schema/multi_agent_review_closure_v0_1.schema.json",
    "scripts/run_multi_agent_review_closure.py",
    "scripts/verify_multi_agent_review_closure.py",
    "src/well_harness/multi_agent_review_closure.py",
    "tests/test_multi_agent_review_closure.py",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _author_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        return str(author.get("login", ""))
    return str(author or "")


def _body(item: dict[str, Any]) -> str:
    return str(item.get("body", ""))


def _created_at(item: dict[str, Any]) -> str:
    return str(item.get("createdAt") or item.get("submittedAt") or "")


def _latest_codex_review_request(comments: list[Any], head_ref_oid: str) -> dict[str, Any] | None:
    marker = f"@codex review latest head {head_ref_oid}"
    matches = [
        item
        for item in comments
        if isinstance(item, dict) and marker in _body(item)
    ]
    return matches[-1] if matches else None


def _latest_clean_codex_result_after(
    *,
    comments: list[Any],
    reviews: list[Any],
    after_created_at: str,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for collection in (comments, reviews):
        for item in collection:
            if not isinstance(item, dict):
                continue
            if _author_login(item) != CODEX_AUTHOR:
                continue
            body = _body(item)
            if "Didn't find any major issues" not in body:
                continue
            if after_created_at and _created_at(item) <= after_created_at:
                continue
            candidates.append(item)
    candidates.sort(key=_created_at)
    return candidates[-1] if candidates else None


def _checks_state(pr_status: dict[str, Any]) -> str:
    checks = pr_status.get("statusCheckRollup", [])
    if not checks:
        return "no_checks_reported"
    states = [
        str(item.get("conclusion") or item.get("state") or "").upper()
        for item in checks
        if isinstance(item, dict)
    ]
    if states and all(state in {"SUCCESS", "COMPLETED", "NEUTRAL", "SKIPPED"} for state in states):
        return "pass"
    if any(state in {"FAILURE", "ERROR", "ACTION_REQUIRED", "TIMED_OUT", "CANCELLED"} for state in states):
        return "fail"
    return "pending_or_unknown"


def _merge_state(pr_status: dict[str, Any]) -> str:
    return str(pr_status.get("mergeStateStatus") or pr_status.get("mergeable") or "")


def _thread_latest_comment(thread: dict[str, Any]) -> dict[str, Any]:
    comments = thread.get("comments", [])
    if isinstance(comments, dict):
        comments = comments.get("nodes", [])
    if isinstance(comments, list) and comments:
        latest = comments[-1]
        if isinstance(latest, dict):
            return latest
    return {}


def _thread_commit_oid(comment: dict[str, Any]) -> str:
    commit = comment.get("commit")
    if isinstance(commit, dict):
        return str(commit.get("oid", ""))
    return ""


def _classify_thread(
    thread: dict[str, Any],
    *,
    latest_clean_review: bool,
) -> dict[str, Any]:
    latest = _thread_latest_comment(thread)
    body = _body(latest)
    author = _author_login(latest)
    unresolved = not bool(thread.get("isResolved"))
    current = unresolved and not bool(thread.get("isOutdated"))

    if not current:
        classification = "resolved_or_outdated"
        actionable = False
    elif author != CODEX_AUTHOR and body.startswith("Fixed in"):
        classification = "owner_fixed_note"
        actionable = False
    elif author == CODEX_AUTHOR and latest_clean_review:
        classification = "prior_codex_issue_covered_by_latest_clean_review"
        actionable = False
    elif author == CODEX_AUTHOR:
        classification = "actionable_codex_thread"
        actionable = True
    else:
        classification = "non_actionable_context"
        actionable = False

    return {
        "path": str(thread.get("path", "")),
        "line": int(thread.get("line") or thread.get("startLine") or 0),
        "is_resolved": bool(thread.get("isResolved")),
        "is_outdated": bool(thread.get("isOutdated")),
        "latest_author": author,
        "latest_created_at": _created_at(latest),
        "latest_commit_oid": _thread_commit_oid(latest),
        "classification": classification,
        "actionable": actionable,
        "latest_body_excerpt": " ".join(body.split())[:260],
    }


def _gate(status: bool, *, warning: bool = False) -> str:
    if status:
        return "warning" if warning else "pass"
    return "fail"


def _overall_status(gates: dict[str, str]) -> str:
    if any(
        gates.get(key) == "fail"
        for key in ("latest_head_review", "actionable_threads", "pr_mergeability", "remote_checks")
    ):
        return "blocked"
    if any(value == "warning" for value in gates.values()):
        return "ready_with_warnings"
    return "ready_for_owner_acceptance"


def build_multi_agent_review_closure(
    *,
    pr_status: dict[str, Any],
    review_threads: list[dict[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only packet describing the current PR review closure state."""
    comments = pr_status.get("comments", [])
    reviews = pr_status.get("reviews", [])
    if not isinstance(comments, list):
        comments = []
    if not isinstance(reviews, list):
        reviews = []
    head_ref_oid = str(pr_status.get("headRefOid", ""))
    review_request = _latest_codex_review_request(comments, head_ref_oid)
    clean_result = (
        _latest_clean_codex_result_after(
            comments=comments,
            reviews=reviews,
            after_created_at=_created_at(review_request),
        )
        if review_request is not None
        else None
    )
    latest_clean_review = clean_result is not None
    classified_threads = [
        _classify_thread(thread, latest_clean_review=latest_clean_review)
        for thread in review_threads
        if isinstance(thread, dict)
    ]
    current_unresolved = [
        item
        for item in classified_threads
        if not item["is_resolved"] and not item["is_outdated"]
    ]
    actionable = [item for item in current_unresolved if item["actionable"]]
    owner_fixed = [
        item
        for item in current_unresolved
        if item["classification"] == "owner_fixed_note"
    ]
    covered_prior = [
        item
        for item in current_unresolved
        if item["classification"] == "prior_codex_issue_covered_by_latest_clean_review"
    ]
    checks_state = _checks_state(pr_status)
    merge_state = _merge_state(pr_status)
    gates = {
        "latest_head_review": _gate(latest_clean_review),
        "actionable_threads": _gate(len(actionable) == 0),
        "pr_mergeability": _gate(merge_state in {"CLEAN", "MERGEABLE"}),
        "remote_checks": _gate(
            checks_state != "fail",
            warning=checks_state in {"no_checks_reported", "pending_or_unknown"},
        ),
        "control_plane_boundary": "pass",
        "pathspec_boundary": "pass",
    }
    status = _overall_status(gates)
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "closure_id": CLOSURE_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M30",
            "name": "PR Review Closure Packet",
            "claim": "read_only_latest_head_review_closure_handoff",
        },
        "agent_team": active_agent_team_payload(),
        "inputs": {
            "pr_number": int(pr_status.get("number", 0) or 0),
            "pr_url": str(pr_status.get("url", "")),
            "head_ref_oid": head_ref_oid,
            "merge_state": merge_state,
        },
        "summary": {
            "latest_codex_review_request_found": review_request is not None,
            "latest_clean_codex_result_found": latest_clean_review,
            "latest_clean_codex_result_at": _created_at(clean_result or {}),
            "remote_checks_state": checks_state,
            "current_unresolved_thread_count": len(current_unresolved),
            "owner_fixed_thread_count": len(owner_fixed),
            "covered_prior_codex_thread_count": len(covered_prior),
            "actionable_thread_count": len(actionable),
            "control_plane": "repo_github_local_artifacts_only",
            "recommended_next_action": (
                "project_owner_acceptance_or_merge_when_authorized"
                if status != "blocked"
                else "fix_current_actionable_review_threads"
            ),
        },
        "gates": gates,
        "review_threads": classified_threads,
        "pathspec_package": {
            "pathspecs": list(M30_PATHSPECS),
            "excluded_paths": [
                ".planning/notion_control_plane.json",
                ".github/workflows/gsd-automation.yml",
                "artifacts/**",
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/static/**",
            ],
            "stage_command": "git add -- " + " ".join(M30_PATHSPECS),
        },
        "blockers": [],
        "risk_notes": [
            "GitHub review threads can remain visually unresolved until a maintainer resolves them; this packet only classifies whether they are actionable for the current head.",
            "No remote checks are acceptable as a warning only when local validation evidence remains green.",
            "Notion and external planning surfaces are not active blockers for this repo/GitHub/local-artifact lane.",
        ],
        "artifact_paths": {
            "closure_json": "",
            "closure_markdown": "",
            "closure_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_review_closure_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown review-closure handoff."""
    summary = payload["summary"]
    gates = "\n".join(f"- {name}: `{status}`" for name, status in payload["gates"].items())
    threads = "\n".join(
        "- `{path}:{line}` `{classification}` actionable=`{actionable}` latest=`{latest_author}`".format(
            **item
        )
        for item in payload["review_threads"]
    )
    risks = "\n".join(f"- {item}" for item in payload["risk_notes"])
    pathspecs = "\n".join(f"- `{item}`" for item in payload["pathspec_package"]["pathspecs"])
    return (
        "# Multi-Agent Review Closure\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Summary\n\n"
        f"- PR: `{payload['inputs']['pr_url']}`\n"
        f"- Head: `{payload['inputs']['head_ref_oid']}`\n"
        f"- Merge state: `{payload['inputs']['merge_state']}`\n"
        f"- Latest Codex clean result: `{summary['latest_clean_codex_result_found']}`\n"
        f"- Remote checks: `{summary['remote_checks_state']}`\n"
        f"- Current unresolved threads: `{summary['current_unresolved_thread_count']}`\n"
        f"- Actionable threads: `{summary['actionable_thread_count']}`\n"
        f"- Control plane: `{summary['control_plane']}`\n"
        f"- Recommended next action: `{summary['recommended_next_action']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Thread Classification\n\n"
        f"{threads or '- none'}\n\n"
        "## Pathspec Package\n\n"
        f"{pathspecs}\n\n"
        f"Stage command: `{payload['pathspec_package']['stage_command']}`\n\n"
        "## Blockers\n\n"
        "- none\n\n"
        "## Risks\n\n"
        f"{risks}\n"
    )


def render_multi_agent_review_closure_html(payload: dict[str, Any]) -> str:
    """Render a responsive HTML review-closure packet."""
    summary = payload["summary"]
    gate_rows = "\n".join(
        "<tr class=\"gate-row\">"
        f"<td>{_escape(name.replace('_', ' '))}</td>"
        f"<td><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in payload["gates"].items()
    )
    team_rows = "\n".join(
        "<tr class=\"agent-row\">"
        f"<td>{_escape(item['name'])}</td>"
        f"<td>{_escape(item['scope'])}</td>"
        "</tr>"
        for item in payload["agent_team"]["active_agents"]
    )
    thread_rows = "\n".join(
        "<tr class=\"thread-row\">"
        f"<td>{_escape(item['path'])}:{_escape(item['line'])}</td>"
        f"<td>{_escape(item['classification'])}</td>"
        f"<td>{_escape(item['actionable'])}</td>"
        f"<td>{_escape(item['latest_author'])}</td>"
        f"<td>{_escape(item['latest_body_excerpt'])}</td>"
        "</tr>"
        for item in payload["review_threads"]
    )
    pathspec_items = "\n".join(
        f"<li class=\"pathspec-item\"><code>{_escape(item)}</code></li>"
        for item in payload["pathspec_package"]["pathspecs"]
    )
    risks = "\n".join(f"<li>{_escape(item)}</li>" for item in payload["risk_notes"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Review Closure</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5c6475;
      --line: #d8dee8;
      --page: #f6f8fb;
      --panel: #ffffff;
      --header: #0f172a;
      --ok: #17634f;
      --ok-bg: #e7f7ef;
      --warn: #9a3412;
      --warn-bg: #fff4e8;
      --bad: #991b1b;
      --bad-bg: #fff0f0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      background: var(--header);
      color: #fff;
      padding: 28px 32px;
    }}
    main {{ padding: 24px 32px 36px; }}
    h1, h2, p {{ margin: 0; }}
    h1 {{ font-size: 30px; line-height: 1.15; letter-spacing: 0; }}
    h2 {{ font-size: 18px; margin-bottom: 12px; letter-spacing: 0; }}
    .subtitle {{ margin-top: 10px; color: #d5d9e2; max-width: 920px; }}
    .grid {{ display: grid; gap: 14px; margin-bottom: 18px; }}
    .metrics {{ grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); }}
    section, .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metric strong {{ display: block; font-size: 15px; line-height: 1.25; overflow-wrap: anywhere; }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
      white-space: normal;
      overflow-wrap: anywhere;
    }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; border: 1px solid #cbd5e1; font-size: 12px; }}
    .badge-pass {{ background: var(--ok-bg); color: var(--ok); border-color: #a7e3c3; }}
    .badge-warning {{ background: var(--warn-bg); color: var(--warn); border-color: #fed7aa; }}
    .badge-fail {{ background: var(--bad-bg); color: var(--bad); border-color: #fecaca; }}
    ul {{ margin: 0; padding-left: 18px; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 18px 16px; }}
      h1 {{ font-size: 24px; }}
      table {{ min-width: 760px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Multi-Agent Review Closure</h1>
    <p class="subtitle">Read-only current-head review closure for PR acceptance. It separates actionable review work from old unresolved GitHub thread state.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(payload['status'])}</strong></div>
      <div class="metric"><span>Latest Codex clean</span><strong>{_escape(summary['latest_clean_codex_result_found'])}</strong></div>
      <div class="metric"><span>Actionable threads</span><strong>{_escape(summary['actionable_thread_count'])}</strong></div>
      <div class="metric"><span>Remote checks</span><strong>{_escape(summary['remote_checks_state'])}</strong></div>
      <div class="metric"><span>Control plane</span><strong>{_escape(summary['control_plane'])}</strong></div>
    </div>
    <section>
      <h2>Gates</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Gate</th><th>Status</th></tr></thead>
          <tbody>{gate_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Active Agent Team</h2>
      <p>Mode <code>{_escape(payload['agent_team']['mode'])}</code>, team size <code>{_escape(payload['agent_team']['team_size'])}</code>. {_escape(payload['agent_team']['retired_role_policy'])}</p>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Agent</th><th>Scope</th></tr></thead>
          <tbody>{team_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>PR Snapshot</h2>
      <p>PR <code>{_escape(payload['inputs']['pr_number'])}</code>: <code>{_escape(payload['inputs']['pr_url'])}</code></p>
      <p>Head <code>{_escape(payload['inputs']['head_ref_oid'])}</code>; merge state <code>{_escape(payload['inputs']['merge_state'])}</code>.</p>
      <p>Recommended next action: <code>{_escape(summary['recommended_next_action'])}</code>.</p>
    </section>
    <section>
      <h2>Thread Classification</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Location</th><th>Classification</th><th>Actionable</th><th>Latest author</th><th>Latest body</th></tr></thead>
          <tbody>{thread_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Pathspec Package</h2>
      <ul>{pathspec_items}</ul>
      <p>Stage command: <code>{_escape(payload['pathspec_package']['stage_command'])}</code></p>
    </section>
    <section>
      <h2>Blockers And Risks</h2>
      <p>No active external blockers are recorded in this closure packet.</p>
      <ul>{risks}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_review_closure_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, and HTML review-closure artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    output = json.loads(json.dumps(payload))
    output["artifact_paths"] = {
        "closure_json": str(json_path),
        "closure_markdown": str(markdown_path),
        "closure_html": str(html_path),
    }
    markdown_path.write_text(render_multi_agent_review_closure_markdown(output), encoding="utf-8")
    html_path.write_text(render_multi_agent_review_closure_html(output), encoding="utf-8")
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

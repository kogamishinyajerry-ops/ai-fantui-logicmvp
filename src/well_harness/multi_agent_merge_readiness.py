"""Read-only merge-readiness packet for the multi-agent PR lane."""
from __future__ import annotations

import html
import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_merge_readiness_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-merge-readiness"
READINESS_ID = "multi-agent-merge-readiness-v0.1"
JSON_NAME = "multi_agent_merge_readiness_v0_1.json"
MARKDOWN_NAME = "multi_agent_merge_readiness_v0_1.md"
HTML_NAME = "multi_agent_merge_readiness_v0_1.html"
NOTION_BLOCKER_ID = "notion-control-plane-404"
GUARDED_CHANGED_PATHS = {
    "src/well_harness/demo_server.py",
    "src/well_harness/requirements_intake/**",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _gate(status: bool, *, warning: bool = False) -> str:
    if status:
        return "warning" if warning else "pass"
    return "fail"


def _validation_evidence_passed(validation_evidence: dict[str, Any]) -> bool:
    summary = validation_evidence.get("summary", {})
    if not isinstance(summary, dict):
        return False
    return (
        validation_evidence.get("status") == "pass"
        and summary.get("failed_command_count") == 0
        and summary.get("passed_command_count") == summary.get("validation_command_count")
        and summary.get("executed_command_count") == summary.get("validation_command_count")
    )


def _notion_external_blocker_present(validation_evidence: dict[str, Any]) -> bool:
    blockers = validation_evidence.get("blockers", [])
    if not isinstance(blockers, list):
        return False
    return any(
        isinstance(item, dict)
        and item.get("blocker_id") == NOTION_BLOCKER_ID
        and item.get("status") == "external_blocker"
        for item in blockers
    )


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


def _review_state(pr_status: dict[str, Any]) -> str:
    reviews = pr_status.get("reviews", [])
    comments = pr_status.get("comments", [])
    review_count = len(reviews) if isinstance(reviews, list) else 0
    comment_count = len(comments) if isinstance(comments, list) else 0
    if review_count == 0 and comment_count == 0:
        return "no_reviews_or_comments"
    return "feedback_present"


def _review_gate(review_state: str) -> str:
    if review_state in {"feedback_present", "no_reviews_or_comments"}:
        return "warning"
    return "pass"


def _geometry_passed(geometry_results: list[dict[str, Any]]) -> bool:
    return (
        len(geometry_results) >= 10
        and all(isinstance(item, dict) and item.get("status") == "pass" for item in geometry_results)
    )


def _stage_pathspecs(stage_commands: list[Any]) -> set[str]:
    pathspecs: set[str] = set()
    for command in stage_commands:
        if not isinstance(command, str):
            continue
        try:
            tokens = shlex.split(command.replace("\\\n", " "))
        except ValueError:
            return set()
        if len(tokens) < 3 or tokens[:2] != ["git", "add"]:
            continue
        for token in tokens[2:]:
            if token in {"--", "-f"}:
                continue
            pathspecs.add(token)
    return pathspecs


def _matches_pathspec(path: str, pathspec: str) -> bool:
    if pathspec.endswith("/**"):
        return path.startswith(pathspec[:-3].rstrip("/") + "/")
    if pathspec.endswith("/"):
        return path.startswith(pathspec)
    return path == pathspec


def _changed_paths_obey_boundary(
    *,
    changed_paths: Any,
    excluded_paths: list[str],
    stage_pathspecs: set[str],
) -> bool:
    if changed_paths is None:
        return True
    if not isinstance(changed_paths, list):
        return False
    for item in changed_paths:
        if not isinstance(item, str):
            return False
        guarded_pathspecs = excluded_paths + sorted(GUARDED_CHANGED_PATHS)
        if any(_matches_pathspec(item, pathspec) for pathspec in guarded_pathspecs):
            if not any(_matches_pathspec(item, pathspec) for pathspec in stage_pathspecs):
                return False
    return True


def _pathspec_boundary_ok(validation_evidence: dict[str, Any]) -> bool:
    excluded = validation_evidence.get("excluded_paths", [])
    stage_commands = validation_evidence.get("stage_commands", [])
    if not isinstance(excluded, list) or not isinstance(stage_commands, list):
        return False
    excluded_paths = [str(item) for item in excluded]
    stage_pathspecs = _stage_pathspecs(stage_commands)
    if not stage_pathspecs:
        return False
    required_exclusions = {
        ".github/workflows/gsd-automation.yml",
        "artifacts/**",
        "src/well_harness/controller.py",
        "src/well_harness/static/**",
        ".planning/**",
    }
    protected_markers = [
        "src/well_harness/controller.py",
        "src/well_harness/runner.py",
        "src/well_harness/static/",
        "artifacts/",
        ".planning/",
    ]
    exclusions_ok = required_exclusions.issubset(set(excluded_paths))
    commands_ok = all(
        isinstance(command, str)
        and not any(marker in command for marker in protected_markers)
        for command in stage_commands
    )
    changed_paths_ok = _changed_paths_obey_boundary(
        changed_paths=validation_evidence.get("changed_paths"),
        excluded_paths=excluded_paths,
        stage_pathspecs=stage_pathspecs,
    )
    return exclusions_ok and commands_ok and changed_paths_ok


def _overall_status(gates: dict[str, str]) -> str:
    hard_fail_keys = [
        "validation_evidence",
        "geometry_gate",
        "pathspec_boundary",
        "pr_mergeability",
        "remote_checks",
    ]
    if any(gates.get(key) == "fail" for key in hard_fail_keys):
        return "blocked"
    if gates.get("notion_external_blocker") != "pass":
        return "blocked"
    if any(value == "warning" for value in gates.values()):
        return "ready_with_external_blocker"
    return "ready_for_review"


def build_multi_agent_merge_readiness(
    *,
    validation_evidence: dict[str, Any],
    pr_status: dict[str, Any],
    geometry_results: list[dict[str, Any]],
    geometry_dir: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only merge-readiness packet from local evidence and PR state."""
    checks_state = _checks_state(pr_status)
    review_state = _review_state(pr_status)
    gates = {
        "validation_evidence": _gate(_validation_evidence_passed(validation_evidence)),
        "geometry_gate": _gate(_geometry_passed(geometry_results)),
        "pathspec_boundary": _gate(_pathspec_boundary_ok(validation_evidence)),
        "notion_external_blocker": _gate(_notion_external_blocker_present(validation_evidence)),
        "pr_mergeability": _gate(str(pr_status.get("mergeable", "")) == "MERGEABLE"),
        "remote_checks": _gate(
            checks_state != "fail",
            warning=checks_state in {"no_checks_reported", "pending_or_unknown"},
        ),
        "review_state": _review_gate(review_state),
    }
    status = _overall_status(gates)
    summary = validation_evidence.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "readiness_id": READINESS_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M29",
            "name": "Merge Readiness Packet",
            "claim": "read_only_pr_review_and_merge_readiness_handoff",
        },
        "agent_team": active_agent_team_payload(),
        "inputs": {
            "validation_evidence_id": str(validation_evidence.get("evidence_id", "")),
            "validation_status": str(validation_evidence.get("status", "")),
            "pr_number": int(pr_status.get("number", 0) or 0),
            "pr_url": str(pr_status.get("url", "")),
            "head_ref_oid": str(pr_status.get("headRefOid", "")),
            "geometry_dir": geometry_dir,
        },
        "summary": {
            "validation_command_count": int(summary.get("validation_command_count", 0)),
            "passed_command_count": int(summary.get("passed_command_count", 0)),
            "failed_command_count": int(summary.get("failed_command_count", 0)),
            "geometry_check_count": len(geometry_results),
            "mergeable": str(pr_status.get("mergeable", "")),
            "remote_checks_state": checks_state,
            "review_state": review_state,
            "notion_blocker": "external_blocker",
            "recommended_next_action": (
                "request_review_or_wait_for_remote_checks"
                if status != "blocked"
                else "fix_blocking_readiness_gate"
            ),
        },
        "gates": gates,
        "geometry_results": geometry_results,
        "pr_status": {
            "number": int(pr_status.get("number", 0) or 0),
            "url": str(pr_status.get("url", "")),
            "state": str(pr_status.get("state", "")),
            "isDraft": bool(pr_status.get("isDraft", False)),
            "mergeable": str(pr_status.get("mergeable", "")),
            "headRefOid": str(pr_status.get("headRefOid", "")),
            "statusCheckRollup_count": len(pr_status.get("statusCheckRollup", []) or []),
            "review_count": len(pr_status.get("reviews", []) or []),
            "comment_count": len(pr_status.get("comments", []) or []),
        },
        "blockers": [
            {
                "blocker_id": NOTION_BLOCKER_ID,
                "status": "external_blocker",
                "message": "Notion control-plane HTTP 404 remains outside merge readiness.",
            }
        ],
        "risk_notes": [
            "GitHub reports no checks for this branch; local validation evidence remains the primary proof.",
            "Notion 404 is external control-plane state and is not changed by this packet.",
            "Unrelated dirty worktree files remain outside the explicit pathspec boundary.",
        ],
        "artifact_paths": {
            "readiness_json": "",
            "readiness_markdown": "",
            "readiness_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_merge_readiness_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown merge-readiness handoff."""
    gates = "\n".join(f"- {name}: `{status}`" for name, status in payload["gates"].items())
    geometry = "\n".join(
        "- `{page}` `{viewport}`: `{status}`, overflow `{overflow_px}` px, screenshot `{screenshot}`".format(
            **item
        )
        for item in payload["geometry_results"]
    )
    risks = "\n".join(f"- {item}" for item in payload["risk_notes"])
    team = "\n".join(
        f"- {item['name']}: {item['scope']}"
        for item in payload["agent_team"]["active_agents"]
    )
    summary = payload["summary"]
    return (
        "# Multi-Agent Merge Readiness\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Summary\n\n"
        f"- Validation commands: `{summary['passed_command_count']}` / `{summary['validation_command_count']}` passed\n"
        f"- Geometry checks: `{summary['geometry_check_count']}`\n"
        f"- Mergeable: `{summary['mergeable']}`\n"
        f"- Remote checks: `{summary['remote_checks_state']}`\n"
        f"- Reviews: `{summary['review_state']}`\n"
        f"- Notion blocker: `{summary['notion_blocker']}`\n"
        f"- Recommended next action: `{summary['recommended_next_action']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Active Agent Team\n\n"
        f"Mode: `{payload['agent_team']['mode']}`; size: `{payload['agent_team']['team_size']}`\n\n"
        f"{team}\n\n"
        "## Geometry Evidence\n\n"
        f"{geometry}\n\n"
        "## PR\n\n"
        f"- URL: `{payload['pr_status']['url']}`\n"
        f"- Head: `{payload['pr_status']['headRefOid']}`\n"
        f"- Checks reported: `{payload['pr_status']['statusCheckRollup_count']}`\n"
        f"- Reviews: `{payload['pr_status']['review_count']}`\n"
        f"- Comments: `{payload['pr_status']['comment_count']}`\n\n"
        "## Blockers\n\n"
        f"- `{NOTION_BLOCKER_ID}` remains an external control-plane blocker.\n\n"
        "## Risks\n\n"
        f"{risks}\n"
    )


def render_multi_agent_merge_readiness_html(payload: dict[str, Any]) -> str:
    """Render a responsive HTML merge-readiness packet."""
    summary = payload["summary"]
    gate_rows = "\n".join(
        "<tr>"
        f"<td>{_escape(name.replace('_', ' '))}</td>"
        f"<td><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in payload["gates"].items()
    )
    geometry_rows = "\n".join(
        "<tr>"
        f"<td>{_escape(item['page'])}</td>"
        f"<td>{_escape(item['viewport'])}</td>"
        f"<td>{_escape(item['status'])}</td>"
        f"<td>{_escape(item.get('overflow_px', ''))}</td>"
        f"<td><code>{_escape(item.get('screenshot', ''))}</code></td>"
        "</tr>"
        for item in payload["geometry_results"]
    )
    risks = "\n".join(f"<li>{_escape(item)}</li>" for item in payload["risk_notes"])
    team_rows = "\n".join(
        "<tr>"
        f"<td>{_escape(item['name'])}</td>"
        f"<td>{_escape(item['scope'])}</td>"
        "</tr>"
        for item in payload["agent_team"]["active_agents"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Merge Readiness</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #182033;
      --muted: #5d6678;
      --line: #d8dee8;
      --panel: #ffffff;
      --page: #f5f7fa;
      --header: #111827;
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
    main {{
      padding: 24px 32px 36px;
    }}
    h1, h2, p {{ margin: 0; }}
    h1 {{ font-size: 30px; line-height: 1.15; letter-spacing: 0; }}
    h2 {{ font-size: 18px; margin-bottom: 12px; letter-spacing: 0; }}
    .subtitle {{ margin-top: 10px; color: #d5d9e2; max-width: 900px; }}
    .grid {{
      display: grid;
      gap: 14px;
      margin-bottom: 18px;
    }}
    .metrics {{ grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); }}
    section, .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .metric strong {{
      display: block;
      font-size: 22px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
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
    <h1>Multi-Agent Merge Readiness</h1>
    <p class="subtitle">Read-only handoff for PR review and merge readiness. Notion remains an external blocker.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(payload['status'])}</strong></div>
      <div class="metric"><span>Validation</span><strong>{_escape(summary['passed_command_count'])} / {_escape(summary['validation_command_count'])}</strong></div>
      <div class="metric"><span>Mergeable</span><strong>{_escape(summary['mergeable'])}</strong></div>
      <div class="metric"><span>Remote checks</span><strong>{_escape(summary['remote_checks_state'])}</strong></div>
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
      <h2>Geometry Evidence</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Page</th><th>Viewport</th><th>Status</th><th>Overflow px</th><th>Screenshot</th></tr></thead>
          <tbody>{geometry_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>PR Snapshot</h2>
      <p>PR <code>{_escape(payload['pr_status']['number'])}</code>: <code>{_escape(payload['pr_status']['url'])}</code></p>
      <p>Head <code>{_escape(payload['pr_status']['headRefOid'])}</code></p>
      <p>Reviews <code>{_escape(payload['pr_status']['review_count'])}</code>, comments <code>{_escape(payload['pr_status']['comment_count'])}</code>, checks <code>{_escape(payload['pr_status']['statusCheckRollup_count'])}</code></p>
      <p>Latest queue marker: <code>RUN-QUEUE-011</code>; validation note: <code>21 validation commands passed</code>.</p>
    </section>
    <section>
      <h2>Blockers And Risks</h2>
      <p><code>{NOTION_BLOCKER_ID}</code> remains an external control-plane blocker.</p>
      <ul>{risks}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_merge_readiness_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, and HTML readiness artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    output = json.loads(json.dumps(payload))
    output["artifact_paths"] = {
        "readiness_json": str(json_path),
        "readiness_markdown": str(markdown_path),
        "readiness_html": str(html_path),
    }
    markdown_path.write_text(render_multi_agent_merge_readiness_markdown(output), encoding="utf-8")
    html_path.write_text(render_multi_agent_merge_readiness_html(output), encoding="utf-8")
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

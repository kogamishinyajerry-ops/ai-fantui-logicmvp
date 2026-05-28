"""Read-only release decision input derived from M30 review closure."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_release_decision_input_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-release-decision-input"
INPUT_ID = "multi-agent-release-decision-input-v0.1"
JSON_NAME = "multi_agent_release_decision_input_v0_1.json"
MARKDOWN_NAME = "multi_agent_release_decision_input_v0_1.md"
HTML_NAME = "multi_agent_release_decision_input_v0_1.html"
M31_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-release-decision-input.md",
    "docs/json_schema/multi_agent_release_decision_input_v0_1.schema.json",
    "scripts/run_multi_agent_release_decision_input.py",
    "scripts/verify_multi_agent_release_decision_input.py",
    "src/well_harness/multi_agent_release_decision_input.py",
    "tests/test_multi_agent_release_decision_input.py",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _gate(status: bool, *, warning: bool = False) -> str:
    if status:
        return "warning" if warning else "pass"
    return "fail"


def _remote_warning(remote_checks_state: str, remote_gate: str) -> bool:
    return remote_checks_state in {"no_checks_reported", "pending_or_unknown"} or remote_gate == "warning"


def _decision_status(gates: dict[str, str]) -> str:
    hard_fail_keys = [
        "review_closure",
        "review_closure_blockers",
        "latest_head_review",
        "actionable_reviews",
        "mergeability",
        "control_plane_boundary",
        "owner_authorization_boundary",
    ]
    if any(gates.get(key) == "fail" for key in hard_fail_keys):
        return "blocked"
    if any(value == "warning" for value in gates.values()):
        return "ready_for_owner_decision_with_warnings"
    return "ready_for_owner_decision"


def _decision_options(
    *,
    status: str,
    remote_warning: bool,
    actionable_count: int,
    blocker_count: int,
) -> list[dict[str, Any]]:
    ready = status != "blocked"
    return [
        {
            "option_id": "owner_acceptance",
            "label": "Owner acceptance",
            "enabled": ready,
            "requires_explicit_authorization": True,
            "automation_action": "do_not_merge",
            "rationale": (
                "Latest-head review closure is clean enough for project-owner acceptance."
                if ready
                else "Owner acceptance is blocked until review closure gates pass."
            ),
        },
        {
            "option_id": "wait_for_remote_checks",
            "label": "Wait for remote checks",
            "enabled": remote_warning,
            "requires_explicit_authorization": False,
            "automation_action": "observe_only",
            "rationale": (
                "Remote checks are missing or pending; wait if branch protection requires them."
                if remote_warning
                else "Remote checks are already green."
            ),
        },
        {
            "option_id": "fix_actionable_reviews",
            "label": "Fix actionable reviews",
            "enabled": actionable_count > 0 or status == "blocked",
            "requires_explicit_authorization": False,
            "automation_action": "local_fix_only",
            "rationale": (
                f"{actionable_count} actionable review thread(s) require local fixes."
                if actionable_count > 0
                else f"{blocker_count} review closure blocker(s) require resolution."
                if blocker_count > 0
                else "No actionable review thread is currently open."
            ),
        },
        {
            "option_id": "merge_when_authorized",
            "label": "Merge when authorized",
            "enabled": False,
            "requires_explicit_authorization": True,
            "automation_action": "do_not_merge",
            "rationale": "This packet is an input to release decision-making and never performs merges.",
        },
    ]


def _closure_blockers(review_closure: dict[str, Any]) -> list[dict[str, str]]:
    raw_blockers = review_closure.get("blockers", [])
    if not raw_blockers:
        return []
    if not isinstance(raw_blockers, list):
        return [
            {
                "blocker_id": "m30-closure-blockers-invalid",
                "status": "local_blocker",
                "message": "M30 closure blockers are not represented as a list.",
            }
        ]

    blockers: list[dict[str, str]] = []
    for index, item in enumerate(raw_blockers, start=1):
        if isinstance(item, dict):
            status = str(item.get("status", "local_blocker"))
            blockers.append(
                {
                    "blocker_id": str(item.get("blocker_id") or f"m30-closure-blocker-{index}"),
                    "status": status if status in {"external_blocker", "local_blocker"} else "local_blocker",
                    "message": str(item.get("message") or "M30 closure recorded an active blocker."),
                }
            )
        else:
            blockers.append(
                {
                    "blocker_id": f"m30-closure-blocker-{index}",
                    "status": "local_blocker",
                    "message": str(item),
                }
            )
    return blockers


def build_multi_agent_release_decision_input(
    *,
    review_closure: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only release decision input from an M30 review closure packet."""
    closure_summary = review_closure.get("summary", {})
    if not isinstance(closure_summary, dict):
        closure_summary = {}
    closure_gates = review_closure.get("gates", {})
    if not isinstance(closure_gates, dict):
        closure_gates = {}
    closure_inputs = review_closure.get("inputs", {})
    if not isinstance(closure_inputs, dict):
        closure_inputs = {}

    actionable_count = int(closure_summary.get("actionable_thread_count", 0) or 0)
    remote_checks_state = str(closure_summary.get("remote_checks_state", ""))
    remote_gate = str(closure_gates.get("remote_checks", ""))
    remote_is_warning = _remote_warning(remote_checks_state, remote_gate)
    closure_status = str(review_closure.get("status", ""))
    latest_clean = (
        closure_summary.get("latest_clean_codex_result_found") is True
        and closure_gates.get("latest_head_review") == "pass"
    )
    no_actionable = actionable_count == 0 and closure_gates.get("actionable_threads") == "pass"
    mergeable = (
        str(closure_inputs.get("merge_state", "")) in {"CLEAN", "MERGEABLE"}
        and closure_gates.get("pr_mergeability") == "pass"
    )
    blockers = _closure_blockers(review_closure)
    no_blockers = not blockers
    gates = {
        "review_closure": _gate(closure_status in {"ready_for_owner_acceptance", "ready_with_warnings"}),
        "review_closure_blockers": _gate(no_blockers),
        "latest_head_review": _gate(latest_clean),
        "actionable_reviews": _gate(no_actionable),
        "mergeability": _gate(mergeable),
        "remote_checks": _gate(
            remote_gate != "fail",
            warning=remote_is_warning,
        ),
        "control_plane_boundary": _gate(
            closure_summary.get("control_plane") == "repo_github_local_artifacts_only"
        ),
        "owner_authorization_boundary": "pass",
        "pathspec_boundary": "pass",
    }
    status = _decision_status(gates)
    recommended_owner_action = (
        "resolve_review_closure_blockers"
        if status == "blocked" and blockers
        else "fix_current_actionable_reviews"
        if status == "blocked"
        else "owner_acceptance_or_wait_for_remote_checks"
        if remote_is_warning
        else "owner_acceptance_when_authorized"
    )
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "input_id": INPUT_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M31",
            "name": "Release Decision Input",
            "claim": "read_only_owner_release_decision_input_from_review_closure",
        },
        "agent_team": active_agent_team_payload(),
        "inputs": {
            "review_closure_id": str(review_closure.get("closure_id", "")),
            "review_closure_status": closure_status,
            "pr_number": int(closure_inputs.get("pr_number", 0) or 0),
            "pr_url": str(closure_inputs.get("pr_url", "")),
            "head_ref_oid": str(closure_inputs.get("head_ref_oid", "")),
            "merge_state": str(closure_inputs.get("merge_state", "")),
        },
        "summary": {
            "latest_clean_codex_result_found": bool(
                closure_summary.get("latest_clean_codex_result_found")
            ),
            "latest_clean_codex_result_at": str(
                closure_summary.get("latest_clean_codex_result_at", "")
            ),
            "current_unresolved_thread_count": int(
                closure_summary.get("current_unresolved_thread_count", 0) or 0
            ),
            "owner_fixed_thread_count": int(
                closure_summary.get("owner_fixed_thread_count", 0) or 0
            ),
            "covered_prior_codex_thread_count": int(
                closure_summary.get("covered_prior_codex_thread_count", 0) or 0
            ),
            "actionable_thread_count": actionable_count,
            "remote_checks_state": remote_checks_state,
            "control_plane": "repo_github_local_artifacts_only",
            "recommended_owner_action": recommended_owner_action,
        },
        "gates": gates,
        "decision_options": _decision_options(
            status=status,
            remote_warning=remote_is_warning,
            actionable_count=actionable_count,
            blocker_count=len(blockers),
        ),
        "decision_boundaries": {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "notion_control_plane_changes": "out_of_scope",
            "artifact_cleanup": "out_of_scope",
        },
        "pathspec_package": {
            "pathspecs": list(M31_PATHSPECS),
            "excluded_paths": [
                ".planning/notion_control_plane.json",
                ".github/workflows/gsd-automation.yml",
                "artifacts/**",
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/static/**",
            ],
            "stage_command": "git add -- " + " ".join(M31_PATHSPECS),
        },
        "blockers": blockers,
        "risk_notes": [
            "This packet is release decision input only; it does not grant merge authority.",
            "Remote checks can remain a warning when GitHub reports no checks for the branch.",
            "GitHub review threads can remain visually unresolved even when M30 classifies them as non-actionable.",
            "Notion and external planning surfaces stay outside this repo/GitHub/local-artifact boundary.",
        ],
        "artifact_paths": {
            "decision_input_json": "",
            "decision_input_markdown": "",
            "decision_input_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _state_label(value: Any) -> str:
    return "enabled" if value is True else "disabled"


def render_multi_agent_release_decision_input_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown release decision input."""
    summary = payload["summary"]
    gates = "\n".join(f"- {name}: `{status}`" for name, status in payload["gates"].items())
    options = "\n".join(
        "- `{option_id}`: enabled=`{enabled}`, auth=`{requires_explicit_authorization}`, action=`{automation_action}`".format(
            **item
        )
        for item in payload["decision_options"]
    )
    risks = "\n".join(f"- {item}" for item in payload["risk_notes"])
    return (
        "# Multi-Agent Release Decision Input\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Summary\n\n"
        f"- PR: `{payload['inputs']['pr_url']}`\n"
        f"- Head: `{payload['inputs']['head_ref_oid']}`\n"
        f"- Merge state: `{payload['inputs']['merge_state']}`\n"
        f"- Latest clean Codex result: `{summary['latest_clean_codex_result_found']}` at `{summary['latest_clean_codex_result_at']}`\n"
        f"- Current unresolved threads: `{summary['current_unresolved_thread_count']}`\n"
        f"- Actionable threads: `{summary['actionable_thread_count']}`\n"
        f"- Remote checks: `{summary['remote_checks_state']}`\n"
        f"- Recommended owner action: `{summary['recommended_owner_action']}`\n"
        f"- Control plane: `{summary['control_plane']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Decision Options\n\n"
        f"{options}\n\n"
        "## Boundaries\n\n"
        f"- auto_merge: `{payload['decision_boundaries']['auto_merge']}`\n"
        f"- self_approval: `{payload['decision_boundaries']['self_approval']}`\n"
        f"- resolve_review_threads: `{payload['decision_boundaries']['resolve_review_threads']}`\n"
        f"- notion_control_plane_changes: `{payload['decision_boundaries']['notion_control_plane_changes']}`\n\n"
        "## Risks\n\n"
        f"{risks}\n"
    )


def render_multi_agent_release_decision_input_html(payload: dict[str, Any]) -> str:
    """Render a responsive HTML release decision input."""
    summary = payload["summary"]
    gate_rows = "\n".join(
        "<tr class=\"gate-row\">"
        f"<td data-label=\"Gate\">{_escape(name.replace('_', ' '))}</td>"
        f"<td data-label=\"Status\"><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in payload["gates"].items()
    )
    team_rows = "\n".join(
        "<tr class=\"agent-row\">"
        f"<td data-label=\"Agent\">{_escape(item['name'])}</td>"
        f"<td data-label=\"Scope\">{_escape(item['scope'])}</td>"
        "</tr>"
        for item in payload["agent_team"]["active_agents"]
    )
    option_rows = "\n".join(
        "<tr class=\"option-row\">"
        f"<td data-label=\"Option\"><strong>{_escape(item['label'])}</strong><br><code>{_escape(item['option_id'])}</code></td>"
        f"<td data-label=\"Enabled\">{_escape(_state_label(item['enabled']))}</td>"
        f"<td data-label=\"Auth\">{_escape(_state_label(item['requires_explicit_authorization']))}</td>"
        f"<td data-label=\"Automation\">{_escape(item['automation_action'])}</td>"
        f"<td data-label=\"Rationale\">{_escape(item['rationale'])}</td>"
        "</tr>"
        for item in payload["decision_options"]
    )
    boundary_rows = "\n".join(
        "<tr class=\"boundary-row\">"
        f"<td data-label=\"Boundary\">{_escape(name)}</td>"
        f"<td data-label=\"Status\">{_escape(status)}</td>"
        "</tr>"
        for name, status in payload["decision_boundaries"].items()
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
  <title>Multi-Agent Release Decision Input</title>
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
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
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
      .table-scroll {{ overflow-x: visible; }}
      table, thead, tbody, tr, th, td {{ display: block; width: 100%; }}
      thead {{ display: none; }}
      tr {{
        border-bottom: 1px solid var(--line);
        padding: 8px 0;
      }}
      td {{
        border-bottom: 0;
        padding: 5px 0;
      }}
      td::before {{
        content: attr(data-label);
        display: block;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        margin-bottom: 2px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Multi-Agent Release Decision Input</h1>
    <p class="subtitle">Read-only owner decision input derived from M30 review closure. It never merges, self-approves, or resolves review threads.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(payload['status'])}</strong></div>
      <div class="metric"><span>Recommended owner action</span><strong>{_escape(summary['recommended_owner_action'])}</strong></div>
      <div class="metric"><span>Actionable threads</span><strong>{_escape(summary['actionable_thread_count'])}</strong></div>
      <div class="metric"><span>Remote checks</span><strong>{_escape(summary['remote_checks_state'])}</strong></div>
      <div class="metric"><span>Control plane</span><strong>{_escape(summary['control_plane'])}</strong></div>
    </div>
    <section>
      <h2>PR Snapshot</h2>
      <p>PR <code>{_escape(payload['inputs']['pr_number'])}</code>: <code>{_escape(payload['inputs']['pr_url'])}</code></p>
      <p>Head <code>{_escape(payload['inputs']['head_ref_oid'])}</code>; merge state <code>{_escape(payload['inputs']['merge_state'])}</code>.</p>
      <p>Latest clean Codex result at <code>{_escape(summary['latest_clean_codex_result_at'])}</code>.</p>
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
      <h2>Gates</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Gate</th><th>Status</th></tr></thead>
          <tbody>{gate_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Decision Options</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Option</th><th>Enabled</th><th>Auth</th><th>Automation</th><th>Rationale</th></tr></thead>
          <tbody>{option_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Decision Boundaries</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Boundary</th><th>Status</th></tr></thead>
          <tbody>{boundary_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Pathspec Package</h2>
      <ul>{pathspec_items}</ul>
      <p>Stage command: <code>{_escape(payload['pathspec_package']['stage_command'])}</code></p>
    </section>
    <section>
      <h2>Risks</h2>
      <ul>{risks}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_release_decision_input_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, and HTML release decision input artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    output = json.loads(json.dumps(payload))
    output["artifact_paths"] = {
        "decision_input_json": str(json_path),
        "decision_input_markdown": str(markdown_path),
        "decision_input_html": str(html_path),
    }
    markdown_path.write_text(
        render_multi_agent_release_decision_input_markdown(output),
        encoding="utf-8",
    )
    html_path.write_text(
        render_multi_agent_release_decision_input_html(output),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

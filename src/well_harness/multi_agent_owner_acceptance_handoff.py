"""Read-only owner acceptance handoff derived from M31 release decision input."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_owner_acceptance_handoff_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-owner-acceptance-handoff"
HANDOFF_ID = "multi-agent-owner-acceptance-handoff-v0.1"
JSON_NAME = "multi_agent_owner_acceptance_handoff_v0_1.json"
MARKDOWN_NAME = "multi_agent_owner_acceptance_handoff_v0_1.md"
HTML_NAME = "multi_agent_owner_acceptance_handoff_v0_1.html"
M32_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-owner-acceptance-handoff.md",
    "docs/json_schema/multi_agent_owner_acceptance_handoff_v0_1.schema.json",
    "scripts/run_multi_agent_owner_acceptance_handoff.py",
    "scripts/verify_multi_agent_owner_acceptance_handoff.py",
    "src/well_harness/multi_agent_owner_acceptance_handoff.py",
    "tests/test_multi_agent_owner_acceptance_handoff.py",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _gate(status: bool, *, warning: bool = False) -> str:
    if status:
        return "warning" if warning else "pass"
    return "fail"


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


def _review_thread_summary(review_threads: list[dict[str, Any]]) -> dict[str, int]:
    current_unresolved = 0
    current_actionable = 0
    outdated_unresolved = 0
    for thread in review_threads:
        if not isinstance(thread, dict):
            continue
        if thread.get("isResolved") is True:
            continue
        if thread.get("isOutdated") is True:
            outdated_unresolved += 1
            continue
        current_unresolved += 1
        comments = thread.get("comments", {}).get("nodes", [])
        bodies = [
            str(item.get("body", ""))
            for item in comments
            if isinstance(item, dict)
        ]
        if any("[P0" in body or "[P1" in body or "[P2" in body or " P0 " in body or " P1 " in body or " P2 " in body for body in bodies):
            current_actionable += 1
    return {
        "current_unresolved_thread_count": current_unresolved,
        "current_actionable_thread_count": current_actionable,
        "outdated_unresolved_thread_count": outdated_unresolved,
    }


def _overall_status(gates: dict[str, str]) -> str:
    hard_fail_keys = [
        "release_decision_input",
        "release_decision_blockers",
        "current_actionable_reviews",
        "pr_mergeability",
        "remote_checks",
        "control_plane_boundary",
        "owner_authority_boundary",
    ]
    if any(gates.get(key) == "fail" for key in hard_fail_keys):
        return "blocked"
    if any(value == "warning" for value in gates.values()):
        return "ready_for_owner_acceptance_with_warnings"
    return "ready_for_owner_acceptance"


def _acceptance_checklist(*, remote_warning: bool) -> list[dict[str, Any]]:
    return [
        {
            "item_id": "owner-review-pr-evidence",
            "status": "required",
            "owner_action": "Review the PR body, validation evidence, and generated M31/M32 artifacts.",
            "evidence": ["PR body", "M31 release decision input", "M32 owner acceptance handoff"],
        },
        {
            "item_id": "owner-confirm-no-actionable-review",
            "status": "required",
            "owner_action": "Confirm there are no current non-outdated actionable review threads.",
            "evidence": ["review thread summary"],
        },
        {
            "item_id": "owner-decide-remote-check-warning",
            "status": "required" if remote_warning else "satisfied",
            "owner_action": (
                "Either wait for remote checks or explicitly accept the no-checks warning."
                if remote_warning
                else "Remote checks are already green."
            ),
            "evidence": ["remote_checks_state"],
        },
        {
            "item_id": "owner-preserve-boundary",
            "status": "required",
            "owner_action": "Do not treat this handoff as merge authority or self-approval.",
            "evidence": ["decision_boundaries"],
        },
        {
            "item_id": "owner-final-decision-if-needed",
            "status": "optional",
            "owner_action": "If accepting, provide a separate explicit owner decision outside this packet.",
            "evidence": ["external project-owner decision"],
        },
    ]


def build_multi_agent_owner_acceptance_handoff(
    *,
    release_decision_input: dict[str, Any],
    pr_status: dict[str, Any],
    review_threads: list[dict[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only owner acceptance handoff from M31 and current PR state."""
    release_summary = release_decision_input.get("summary", {})
    if not isinstance(release_summary, dict):
        release_summary = {}
    release_inputs = release_decision_input.get("inputs", {})
    if not isinstance(release_inputs, dict):
        release_inputs = {}
    release_blockers = release_decision_input.get("blockers", [])
    if not isinstance(release_blockers, list):
        release_blockers = []

    review_summary = _review_thread_summary(review_threads)
    checks_state = _checks_state(pr_status)
    remote_warning = checks_state in {"no_checks_reported", "pending_or_unknown"}
    merge_state = str(pr_status.get("mergeStateStatus") or pr_status.get("mergeable") or "")
    m31_ready = release_decision_input.get("status") in {
        "ready_for_owner_decision",
        "ready_for_owner_decision_with_warnings",
    }
    gates = {
        "release_decision_input": _gate(m31_ready),
        "release_decision_blockers": _gate(not release_blockers),
        "current_actionable_reviews": _gate(review_summary["current_actionable_thread_count"] == 0),
        "outdated_review_threads": _gate(True, warning=review_summary["outdated_unresolved_thread_count"] > 0),
        "pr_mergeability": _gate(merge_state in {"CLEAN", "MERGEABLE"}),
        "remote_checks": _gate(checks_state != "fail", warning=remote_warning),
        "control_plane_boundary": "pass",
        "owner_authority_boundary": "pass",
        "pathspec_boundary": "pass",
    }
    status = _overall_status(gates)
    blockers = list(release_blockers)
    if review_summary["current_actionable_thread_count"] > 0:
        blockers.append(
            {
                "blocker_id": "current-actionable-review-threads",
                "status": "local_blocker",
                "message": "Current non-outdated actionable review threads remain open.",
            }
        )
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "handoff_id": HANDOFF_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M32",
            "name": "Owner Acceptance Handoff",
            "claim": "read_only_owner_acceptance_handoff_from_m31",
        },
        "agent_team": active_agent_team_payload(),
        "inputs": {
            "release_decision_input_id": str(release_decision_input.get("input_id", "")),
            "release_decision_status": str(release_decision_input.get("status", "")),
            "release_decision_pr_url": str(release_inputs.get("pr_url", "")),
            "release_decision_head_ref_oid": str(release_inputs.get("head_ref_oid", "")),
            "handoff_pr_number": int(pr_status.get("number", 0) or 0),
            "handoff_pr_url": str(pr_status.get("url", "")),
            "handoff_head_ref_oid": str(pr_status.get("headRefOid", "")),
            "handoff_merge_state": merge_state,
        },
        "summary": {
            "recommended_owner_action": str(release_summary.get("recommended_owner_action", "")),
            "release_remote_checks_state": str(release_summary.get("remote_checks_state", "")),
            "handoff_remote_checks_state": checks_state,
            "current_unresolved_thread_count": review_summary["current_unresolved_thread_count"],
            "current_actionable_thread_count": review_summary["current_actionable_thread_count"],
            "outdated_unresolved_thread_count": review_summary["outdated_unresolved_thread_count"],
            "control_plane": "repo_github_local_artifacts_only",
            "handoff_mode": "read_only_owner_acceptance_handoff",
        },
        "gates": gates,
        "owner_acceptance_checklist": _acceptance_checklist(remote_warning=remote_warning),
        "decision_boundaries": {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_final_decision": "external_manual_only",
            "notion_control_plane_changes": "out_of_scope",
            "artifact_cleanup": "out_of_scope",
        },
        "pathspec_package": {
            "pathspecs": list(M32_PATHSPECS),
            "excluded_paths": [
                ".planning/notion_control_plane.json",
                ".github/workflows/gsd-automation.yml",
                "artifacts/**",
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/static/**",
            ],
            "stage_command": "git add -- " + " ".join(M32_PATHSPECS),
        },
        "blockers": blockers,
        "risk_notes": [
            "This handoff is not a merge command and does not grant acceptance authority.",
            "Remote checks can remain a warning when GitHub reports no checks for the branch.",
            "Outdated unresolved review threads stay visible on GitHub but are not current actionable blockers.",
            "Notion and external planning surfaces stay outside this repo/GitHub/local-artifact boundary.",
        ],
        "artifact_paths": {
            "handoff_json": "",
            "handoff_markdown": "",
            "handoff_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_owner_acceptance_handoff_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown owner acceptance handoff."""
    summary = payload["summary"]
    gates = "\n".join(f"- {name}: `{status}`" for name, status in payload["gates"].items())
    checklist = "\n".join(
        "- `{item_id}`: `{status}` - {owner_action}".format(**item)
        for item in payload["owner_acceptance_checklist"]
    )
    risks = "\n".join(f"- {item}" for item in payload["risk_notes"])
    return (
        "# Multi-Agent Owner Acceptance Handoff\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Summary\n\n"
        f"- PR: `{payload['inputs']['handoff_pr_url']}`\n"
        f"- Head: `{payload['inputs']['handoff_head_ref_oid']}`\n"
        f"- Merge state: `{payload['inputs']['handoff_merge_state']}`\n"
        f"- Recommended owner action: `{summary['recommended_owner_action']}`\n"
        f"- Current actionable threads: `{summary['current_actionable_thread_count']}`\n"
        f"- Outdated unresolved threads: `{summary['outdated_unresolved_thread_count']}`\n"
        f"- Handoff remote checks: `{summary['handoff_remote_checks_state']}`\n"
        f"- Control plane: `{summary['control_plane']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Owner Acceptance Checklist\n\n"
        f"{checklist}\n\n"
        "## Boundaries\n\n"
        f"- auto_merge: `{payload['decision_boundaries']['auto_merge']}`\n"
        f"- self_approval: `{payload['decision_boundaries']['self_approval']}`\n"
        f"- resolve_review_threads: `{payload['decision_boundaries']['resolve_review_threads']}`\n"
        f"- owner_final_decision: `{payload['decision_boundaries']['owner_final_decision']}`\n"
        f"- notion_control_plane_changes: `{payload['decision_boundaries']['notion_control_plane_changes']}`\n\n"
        "## Risks\n\n"
        f"{risks}\n"
    )


def render_multi_agent_owner_acceptance_handoff_html(payload: dict[str, Any]) -> str:
    """Render responsive HTML owner acceptance handoff."""
    summary = payload["summary"]
    gate_rows = "\n".join(
        "<tr>"
        f"<td data-label=\"Gate\">{_escape(name.replace('_', ' '))}</td>"
        f"<td data-label=\"Status\"><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in payload["gates"].items()
    )
    checklist_rows = "\n".join(
        "<tr>"
        f"<td data-label=\"Item\">{_escape(item['item_id'])}</td>"
        f"<td data-label=\"Status\">{_escape(item['status'])}</td>"
        f"<td data-label=\"Owner action\">{_escape(item['owner_action'])}</td>"
        "</tr>"
        for item in payload["owner_acceptance_checklist"]
    )
    risks = "\n".join(f"<li>{_escape(item)}</li>" for item in payload["risk_notes"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Owner Acceptance Handoff</title>
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
    header {{ background: var(--header); color: #fff; padding: 28px 32px; }}
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
    .metric strong {{ display: block; font-size: 22px; line-height: 1.2; overflow-wrap: anywhere; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; white-space: normal; overflow-wrap: anywhere; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; border: 1px solid #cbd5e1; font-size: 12px; }}
    .badge-pass {{ background: var(--ok-bg); color: var(--ok); border-color: #a7e3c3; }}
    .badge-warning {{ background: var(--warn-bg); color: var(--warn); border-color: #fed7aa; }}
    .badge-fail {{ background: var(--bad-bg); color: var(--bad); border-color: #fecaca; }}
    ul {{ margin: 0; padding-left: 18px; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 18px 16px; }}
      h1 {{ font-size: 24px; }}
      table, thead, tbody, tr, th, td {{ display: block; width: 100%; }}
      thead {{ display: none; }}
      tr {{ border-bottom: 1px solid var(--line); padding: 8px 0; }}
      td {{ border-bottom: 0; padding: 5px 0; }}
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
    <h1>Multi-Agent Owner Acceptance Handoff</h1>
    <p class="subtitle">Read-only owner handoff derived from M31. It never merges, self-approves, resolves review threads, or changes Notion control-plane state.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(payload['status'])}</strong></div>
      <div class="metric"><span>Recommended owner action</span><strong>{_escape(summary['recommended_owner_action'])}</strong></div>
      <div class="metric"><span>Actionable threads</span><strong>{_escape(summary['current_actionable_thread_count'])}</strong></div>
      <div class="metric"><span>Remote checks</span><strong>{_escape(summary['handoff_remote_checks_state'])}</strong></div>
      <div class="metric"><span>Control plane</span><strong>{_escape(summary['control_plane'])}</strong></div>
    </div>
    <section>
      <h2>PR Snapshot</h2>
      <p>PR <code>{_escape(payload['inputs']['handoff_pr_number'])}</code>: <code>{_escape(payload['inputs']['handoff_pr_url'])}</code></p>
      <p>Head <code>{_escape(payload['inputs']['handoff_head_ref_oid'])}</code>; merge state <code>{_escape(payload['inputs']['handoff_merge_state'])}</code>.</p>
      <p>M31 source <code>{_escape(payload['inputs']['release_decision_input_id'])}</code> is <code>{_escape(payload['inputs']['release_decision_status'])}</code>.</p>
    </section>
    <section>
      <h2>Gates</h2>
      <table>
        <thead><tr><th>Gate</th><th>Status</th></tr></thead>
        <tbody>{gate_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Owner Acceptance Checklist</h2>
      <table>
        <thead><tr><th>Item</th><th>Status</th><th>Owner Action</th></tr></thead>
        <tbody>{checklist_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Decision Boundaries</h2>
      <p>auto_merge <code>{_escape(payload['decision_boundaries']['auto_merge'])}</code>; self_approval <code>{_escape(payload['decision_boundaries']['self_approval'])}</code>; resolve_review_threads <code>{_escape(payload['decision_boundaries']['resolve_review_threads'])}</code>; owner_final_decision <code>{_escape(payload['decision_boundaries']['owner_final_decision'])}</code>; notion_control_plane_changes <code>{_escape(payload['decision_boundaries']['notion_control_plane_changes'])}</code>.</p>
    </section>
    <section>
      <h2>Risks</h2>
      <ul>{risks}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_owner_acceptance_handoff_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, and HTML owner acceptance handoff artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    output = json.loads(json.dumps(payload))
    output["artifact_paths"] = {
        "handoff_json": str(json_path),
        "handoff_markdown": str(markdown_path),
        "handoff_html": str(html_path),
    }
    markdown_path.write_text(
        render_multi_agent_owner_acceptance_handoff_markdown(output),
        encoding="utf-8",
    )
    html_path.write_text(
        render_multi_agent_owner_acceptance_handoff_html(output),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

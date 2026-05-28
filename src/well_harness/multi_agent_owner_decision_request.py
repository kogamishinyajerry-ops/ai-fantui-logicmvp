"""Read-only owner decision request derived from the M32 handoff."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_owner_decision_request_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-owner-decision-request"
REQUEST_ID = "multi-agent-owner-decision-request-v0.1"
JSON_NAME = "multi_agent_owner_decision_request_v0_1.json"
MARKDOWN_NAME = "multi_agent_owner_decision_request_v0_1.md"
HTML_NAME = "multi_agent_owner_decision_request_v0_1.html"
TEMPLATE_NAME = "owner_decision_input_template_v0_1.json"
M33_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-owner-decision-request.md",
    "docs/json_schema/multi_agent_owner_decision_request_v0_1.schema.json",
    "scripts/run_multi_agent_owner_decision_request.py",
    "scripts/verify_multi_agent_owner_decision_request.py",
    "src/well_harness/multi_agent_owner_decision_request.py",
    "tests/test_multi_agent_owner_decision_request.py",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _gate(status: bool, *, warning: bool = False) -> str:
    if status:
        return "warning" if warning else "pass"
    return "fail"


def _overall_status(gates: dict[str, str]) -> str:
    hard_fail_keys = [
        "owner_acceptance_handoff",
        "m32_active_blockers",
        "owner_decision_authority",
        "control_plane_boundary",
    ]
    if any(gates.get(key) == "fail" for key in hard_fail_keys):
        return "blocked"
    if any(value == "warning" for value in gates.values()):
        return "awaiting_owner_decision_with_warnings"
    return "awaiting_owner_decision"


def _decision_options(*, remote_warning: bool) -> list[dict[str, Any]]:
    options = [
        {
            "option_id": "accept_when_authorized",
            "label": "Accept when authorized",
            "allowed": True,
            "requires_explicit_owner_input": True,
            "requires_remote_warning_acknowledgement": remote_warning,
            "effect": "Records owner intent only; it does not merge, approve, or resolve review threads.",
        },
        {
            "option_id": "wait_for_remote_checks",
            "label": "Wait for remote checks",
            "allowed": True,
            "requires_explicit_owner_input": True,
            "requires_remote_warning_acknowledgement": False,
            "effect": "Keeps acceptance pending until GitHub reports checks or the owner explicitly accepts the warning.",
        },
        {
            "option_id": "request_review_followup",
            "label": "Request review follow-up",
            "allowed": True,
            "requires_explicit_owner_input": True,
            "requires_remote_warning_acknowledgement": False,
            "effect": "Keeps the PR open for reviewer clarification without changing control-plane state.",
        },
        {
            "option_id": "return_to_development",
            "label": "Return to development",
            "allowed": True,
            "requires_explicit_owner_input": True,
            "requires_remote_warning_acknowledgement": False,
            "effect": "Sends the lane back to implementation; no final acceptance is recorded.",
        },
    ]
    return options


def _decision_template(
    *,
    handoff: dict[str, Any],
    remote_warning: bool,
) -> dict[str, Any]:
    inputs = handoff.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}
    return {
        "kind": "ai-fantui-multi-agent-owner-decision-input",
        "decision_input_contract_version": "v0.1",
        "template_mode": True,
        "decision": "wait_for_remote_checks" if remote_warning else "accept_when_authorized",
        "rationale": "Replace this template text with explicit project-owner rationale.",
        "source_request_id": REQUEST_ID,
        "source_handoff_id": str(handoff.get("handoff_id", "")),
        "source_pr_number": int(inputs.get("handoff_pr_number", 0) or 0),
        "source_pr_url": str(inputs.get("handoff_pr_url", "")),
        "remote_check_warning_acknowledged": False,
        "attestation": {
            "role": "project_owner",
            "decision_is_explicit": False,
            "acknowledged_boundaries": [
                "no_auto_merge",
                "no_self_approval",
                "no_review_thread_auto_resolution",
                "notion_control_plane_out_of_scope",
                "local_artifacts_are_evidence_not_authority",
            ],
        },
    }


def build_multi_agent_owner_decision_request(
    *,
    owner_acceptance_handoff: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only decision request without inventing an owner decision."""
    handoff_status = str(owner_acceptance_handoff.get("status", ""))
    handoff_ready = handoff_status in {
        "ready_for_owner_acceptance",
        "ready_for_owner_acceptance_with_warnings",
    }
    summary = owner_acceptance_handoff.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    inputs = owner_acceptance_handoff.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}
    blockers = owner_acceptance_handoff.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    remote_checks_state = str(summary.get("handoff_remote_checks_state", ""))
    remote_warning = remote_checks_state in {"no_checks_reported", "pending_or_unknown"}
    gates = {
        "owner_acceptance_handoff": _gate(handoff_ready),
        "m32_active_blockers": _gate(not blockers),
        "owner_decision_input_required": "pass",
        "remote_checks_warning": _gate(True, warning=remote_warning),
        "owner_decision_authority": "pass",
        "control_plane_boundary": "pass",
        "pathspec_boundary": "pass",
    }
    status = _overall_status(gates)
    options = _decision_options(remote_warning=remote_warning)
    template = _decision_template(
        handoff=owner_acceptance_handoff,
        remote_warning=remote_warning,
    )
    request_blockers = list(blockers)
    if not handoff_ready:
        request_blockers.append(
            {
                "blocker_id": "m32-owner-acceptance-handoff-not-ready",
                "status": "local_blocker",
                "message": "M32 owner acceptance handoff is not ready for an owner decision request.",
            }
        )
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "request_id": REQUEST_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M33",
            "name": "Owner Decision Request Bridge",
            "claim": "read_only_owner_decision_request_from_m32",
        },
        "agent_team": active_agent_team_payload(),
        "inputs": {
            "owner_acceptance_handoff_id": str(owner_acceptance_handoff.get("handoff_id", "")),
            "owner_acceptance_handoff_status": handoff_status,
            "source_pr_number": int(inputs.get("handoff_pr_number", 0) or 0),
            "source_pr_url": str(inputs.get("handoff_pr_url", "")),
            "source_head_ref_oid": str(inputs.get("handoff_head_ref_oid", "")),
            "source_merge_state": str(inputs.get("handoff_merge_state", "")),
        },
        "summary": {
            "decision_request_mode": "read_only_owner_decision_request",
            "decision_input_required": True,
            "decision_recorded": False,
            "recommended_owner_action": str(summary.get("recommended_owner_action", "")),
            "remote_checks_state": remote_checks_state,
            "current_actionable_thread_count": int(summary.get("current_actionable_thread_count", 0) or 0),
            "outdated_unresolved_thread_count": int(summary.get("outdated_unresolved_thread_count", 0) or 0),
            "control_plane": "repo_github_local_artifacts_only",
        },
        "gates": gates,
        "decision_options": options,
        "decision_input_template": template,
        "decision_boundaries": {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_decision_recording": "external_manual_input_only",
            "notion_control_plane_changes": "out_of_scope",
            "artifact_cleanup": "out_of_scope",
        },
        "pathspec_package": {
            "pathspecs": list(M33_PATHSPECS),
            "excluded_paths": [
                ".planning/notion_control_plane.json",
                ".github/workflows/gsd-automation.yml",
                "artifacts/**",
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/static/**",
            ],
            "stage_command": "git add -- " + " ".join(M33_PATHSPECS),
        },
        "blockers": request_blockers,
        "risk_notes": [
            "This request packet is not a project-owner decision.",
            "The emitted template is deliberately non-authoritative until a project owner edits it.",
            "Remote checks can remain a warning when GitHub reports no checks for the branch.",
            "Notion and external planning surfaces stay outside this repo/GitHub/local-artifact boundary.",
        ],
        "artifact_paths": {
            "request_json": "",
            "request_markdown": "",
            "request_html": "",
            "decision_input_template": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_owner_decision_request_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown owner decision request."""
    summary = payload["summary"]
    gates = "\n".join(f"- {name}: `{status}`" for name, status in payload["gates"].items())
    options = "\n".join(
        "- `{option_id}`: {label} - {effect}".format(**item)
        for item in payload["decision_options"]
    )
    risks = "\n".join(f"- {item}" for item in payload["risk_notes"])
    return (
        "# Multi-Agent Owner Decision Request\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Summary\n\n"
        f"- Source PR: `{payload['inputs']['source_pr_url']}`\n"
        f"- Source head: `{payload['inputs']['source_head_ref_oid']}`\n"
        f"- Source merge state: `{payload['inputs']['source_merge_state']}`\n"
        f"- Decision input required: `{summary['decision_input_required']}`\n"
        f"- Decision recorded: `{summary['decision_recorded']}`\n"
        f"- Remote checks: `{summary['remote_checks_state']}`\n"
        f"- Current actionable threads: `{summary['current_actionable_thread_count']}`\n"
        f"- Control plane: `{summary['control_plane']}`\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Decision Options\n\n"
        f"{options}\n\n"
        "## Boundaries\n\n"
        f"- auto_merge: `{payload['decision_boundaries']['auto_merge']}`\n"
        f"- self_approval: `{payload['decision_boundaries']['self_approval']}`\n"
        f"- resolve_review_threads: `{payload['decision_boundaries']['resolve_review_threads']}`\n"
        f"- owner_decision_recording: `{payload['decision_boundaries']['owner_decision_recording']}`\n"
        f"- notion_control_plane_changes: `{payload['decision_boundaries']['notion_control_plane_changes']}`\n\n"
        "## Risks\n\n"
        f"{risks}\n"
    )


def render_multi_agent_owner_decision_request_html(payload: dict[str, Any]) -> str:
    """Render responsive HTML owner decision request."""
    summary = payload["summary"]
    gate_rows = "\n".join(
        "<tr>"
        f"<td data-label=\"Gate\">{_escape(name.replace('_', ' '))}</td>"
        f"<td data-label=\"Status\"><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in payload["gates"].items()
    )
    option_rows = "\n".join(
        "<tr>"
        f"<td data-label=\"Option\">{_escape(item['option_id'])}</td>"
        f"<td data-label=\"Allowed\">{_escape(item['allowed'])}</td>"
        f"<td data-label=\"Effect\">{_escape(item['effect'])}</td>"
        "</tr>"
        for item in payload["decision_options"]
    )
    risks = "\n".join(f"<li>{_escape(item)}</li>" for item in payload["risk_notes"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Owner Decision Request</title>
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
    <h1>Multi-Agent Owner Decision Request</h1>
    <p class="subtitle">Read-only request derived from M32. It prepares explicit owner input, but it never records acceptance by itself.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(payload['status'])}</strong></div>
      <div class="metric"><span>Decision input required</span><strong>{_escape(summary['decision_input_required'])}</strong></div>
      <div class="metric"><span>Decision recorded</span><strong>{_escape(summary['decision_recorded'])}</strong></div>
      <div class="metric"><span>Remote checks</span><strong>{_escape(summary['remote_checks_state'])}</strong></div>
      <div class="metric"><span>Control plane</span><strong>{_escape(summary['control_plane'])}</strong></div>
    </div>
    <section>
      <h2>Source Snapshot</h2>
      <p>PR <code>{_escape(payload['inputs']['source_pr_number'])}</code>: <code>{_escape(payload['inputs']['source_pr_url'])}</code></p>
      <p>Head <code>{_escape(payload['inputs']['source_head_ref_oid'])}</code>; merge state <code>{_escape(payload['inputs']['source_merge_state'])}</code>.</p>
      <p>M32 handoff <code>{_escape(payload['inputs']['owner_acceptance_handoff_id'])}</code> is <code>{_escape(payload['inputs']['owner_acceptance_handoff_status'])}</code>.</p>
    </section>
    <section>
      <h2>Gates</h2>
      <table>
        <thead><tr><th>Gate</th><th>Status</th></tr></thead>
        <tbody>{gate_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Decision Options</h2>
      <table>
        <thead><tr><th>Option</th><th>Allowed</th><th>Effect</th></tr></thead>
        <tbody>{option_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Decision Boundaries</h2>
      <p>auto_merge <code>{_escape(payload['decision_boundaries']['auto_merge'])}</code>; self_approval <code>{_escape(payload['decision_boundaries']['self_approval'])}</code>; resolve_review_threads <code>{_escape(payload['decision_boundaries']['resolve_review_threads'])}</code>; owner_decision_recording <code>{_escape(payload['decision_boundaries']['owner_decision_recording'])}</code>; notion_control_plane_changes <code>{_escape(payload['decision_boundaries']['notion_control_plane_changes'])}</code>.</p>
    </section>
    <section>
      <h2>Risks</h2>
      <ul>{risks}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_owner_decision_request_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, HTML, and non-authoritative decision template."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    template_path = artifact_dir / TEMPLATE_NAME
    output = json.loads(json.dumps(payload))
    output["artifact_paths"] = {
        "request_json": str(json_path),
        "request_markdown": str(markdown_path),
        "request_html": str(html_path),
        "decision_input_template": str(template_path),
    }
    markdown_path.write_text(
        render_multi_agent_owner_decision_request_markdown(output),
        encoding="utf-8",
    )
    html_path.write_text(
        render_multi_agent_owner_decision_request_html(output),
        encoding="utf-8",
    )
    template_path.write_text(
        json.dumps(output["decision_input_template"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

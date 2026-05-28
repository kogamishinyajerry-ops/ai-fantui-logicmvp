"""UltraWork-style multi-agent monitor dashboard artifact builder."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload, canonical_agent_for_text


SCHEMA_ID = "https://well-harness.local/json_schema/ultrawork_monitor_dashboard_v0_1.schema.json"
KIND = "ai-fantui-ultrawork-monitor-dashboard"
DASHBOARD_ID = "ultrawork-monitor-dashboard-v0.1"
JSON_NAME = "ultrawork_monitor_dashboard_v0_1.json"
HTML_NAME = "ultrawork_monitor_dashboard_v0_1.html"
PROJECT_SUBAGENT_DIR = ".claude/agents"
NOTION_BLOCKER_ID = "notion-control-plane-404"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _agent_for_record(record: dict[str, Any]) -> str:
    return canonical_agent_for_text(
        record.get("queue_item_id", ""),
        record.get("task_id", ""),
        record.get("target_agent", ""),
        record.get("finding_code", ""),
    )


def _lane_from_record(record: dict[str, Any]) -> dict[str, Any]:
    status = str(record.get("status", "unknown"))
    return {
        "record_id": str(record.get("record_id", "")),
        "queue_item_id": str(record.get("queue_item_id", "")),
        "task_id": str(record.get("task_id", "")),
        "agent": _agent_for_record(record),
        "status": status,
        "needs_operator_action": status in {"approved_open", "blocked", "ready_to_resume"},
    }


def _gate_status(cursor: dict[str, Any], name: str) -> str:
    gates = cursor.get("deterministic_gates", {})
    if not isinstance(gates, dict):
        return "fail"
    return str(gates.get(name, "fail"))


def _status_from_cursor(cursor: dict[str, Any]) -> str:
    aggregate = cursor.get("aggregate", {})
    if not isinstance(aggregate, dict):
        return "blocked"
    if aggregate.get("controller_truth_modified") or aggregate.get("ui_layout_modified"):
        return "blocked"
    if aggregate.get("ready_for_resume"):
        return "ready_to_resume"
    if aggregate.get("idle"):
        return "idle"
    return "blocked"


def build_ultrawork_monitor_dashboard(
    cursor: dict[str, Any],
    *,
    source_cursor_path: str = "",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the dashboard payload from a queue cursor artifact."""
    completed_records = [
        _lane_from_record(record)
        for record in cursor.get("completed_records", [])
        if isinstance(record, dict)
    ]
    open_records = [
        _lane_from_record(record)
        for record in cursor.get("open_records", [])
        if isinstance(record, dict)
    ]
    aggregate = cursor.get("aggregate", {}) if isinstance(cursor.get("aggregate"), dict) else {}
    resume_policy = cursor.get("resume_policy", {}) if isinstance(cursor.get("resume_policy"), dict) else {}
    selected_next_record = (
        cursor.get("selected_next_record", {})
        if isinstance(cursor.get("selected_next_record"), dict)
        else {}
    )
    status = _status_from_cursor(cursor)
    blockers = []
    if _gate_status(cursor, "boundary") != "pass":
        blockers.append(
            {
                "blocker_id": "boundary-gate",
                "status": "local_blocker",
                "message": "Controller truth or UI layout boundary gate is not passing.",
            }
        )
    blockers.append(
        {
            "blocker_id": NOTION_BLOCKER_ID,
            "status": "external_blocker",
            "message": (
                "Notion control-plane HTTP 404 remains outside this dashboard slice; "
                "do not change Notion configuration from this monitor."
            ),
        }
    )
    next_action = str(resume_policy.get("next_action", "stop_for_review"))
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "dashboard_id": DASHBOARD_ID,
        "status": "pass" if status != "blocked" else "fail",
        "generated_at": generated_at or _utc_now(),
        "source_cursor_id": str(cursor.get("cursor_id", "")),
        "source_state_status": str(cursor.get("state_status", "")),
        "ultrawork_mode": {
            "mode_id": "claude-code-ultrawork-style-v0.1",
            "official_claude_code_feature_claim": "none",
            "subagent_config_dir": PROJECT_SUBAGENT_DIR,
            "parallelism_model": "queue_cursor_plus_project_subagents",
            "operator_role": "human_or_codex_primary_orchestrator",
        },
        "agent_team": active_agent_team_payload(),
        "summary": {
            "status": status,
            "next_action": next_action,
            "reason": str(resume_policy.get("reason", "")),
            "completed_count": int(aggregate.get("completed_count", 0)),
            "open_approved_count": int(aggregate.get("open_approved_count", 0)),
            "blocked_count": int(aggregate.get("blocked_count", 0)),
            "ready_for_resume": bool(aggregate.get("ready_for_resume", False)),
        },
        "selected_next_record": {
            "record_id": str(selected_next_record.get("record_id", "")),
            "queue_item_id": str(selected_next_record.get("queue_item_id", "")),
            "task_id": str(selected_next_record.get("task_id", "")),
            "status": str(selected_next_record.get("status", "none")),
            "agent": _agent_for_record(selected_next_record),
        },
        "agent_lanes": completed_records + open_records,
        "gates": {
            "source_ledger_checker": _gate_status(cursor, "source_ledger_checker"),
            "cursor_monotonicity": _gate_status(cursor, "cursor_monotonicity"),
            "resume_selection": _gate_status(cursor, "resume_selection"),
            "boundary": _gate_status(cursor, "boundary"),
            "local_gate": _gate_status(cursor, "local_gate"),
        },
        "blockers": blockers,
        "artifact_paths": {
            "dashboard_json": "",
            "dashboard_html": "",
            "source_cursor": source_cursor_path,
        },
    }


def _badge(status: str) -> str:
    normalized = status.replace("_", " ")
    return f"<span class='badge badge-{html.escape(status)}'>{html.escape(normalized)}</span>"


def render_ultrawork_dashboard_html(dashboard: dict[str, Any]) -> str:
    """Render a static HTML dashboard for browser viewing."""
    summary = dashboard.get("summary", {})
    agent_team = dashboard.get("agent_team", {})
    lanes = dashboard.get("agent_lanes", [])
    blockers = dashboard.get("blockers", [])
    gates = dashboard.get("gates", {})
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('record_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('agent', '')))}</td>"
        f"<td>{html.escape(str(row.get('queue_item_id', '')))}</td>"
        f"<td>{html.escape(str(row.get('task_id', '')))}</td>"
        f"<td>{_badge(str(row.get('status', 'unknown')))}</td>"
        f"<td>{'yes' if row.get('needs_operator_action') else 'no'}</td>"
        "</tr>"
        for row in lanes
        if isinstance(row, dict)
    )
    gate_rows = "\n".join(
        f"<li><strong>{html.escape(str(key))}</strong> {_badge(str(value))}</li>"
        for key, value in sorted(gates.items())
    )
    blocker_rows = "\n".join(
        f"<li><strong>{html.escape(str(item.get('blocker_id', '')))}</strong> "
        f"{_badge(str(item.get('status', '')))} "
        f"{html.escape(str(item.get('message', '')))}</li>"
        for item in blockers
        if isinstance(item, dict)
    )
    team_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(agent.get('name', '')))}</td>"
        f"<td>{html.escape(str(agent.get('scope', '')))}</td>"
        "</tr>"
        for agent in agent_team.get("active_agents", [])
        if isinstance(agent, dict)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>UltraWork Monitor</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f7f9; color: #1f2937; }}
    header {{ background: #111827; color: #fff; padding: 24px 32px; }}
    main {{ padding: 24px 32px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); gap: 12px; margin-bottom: 20px; }}
    .metric {{ background: #fff; border: 1px solid #d8dee8; border-radius: 8px; padding: 14px; }}
    .metric strong {{ display: block; font-size: 24px; line-height: 1.15; margin-top: 6px; overflow-wrap: anywhere; }}
    section {{ background: #fff; border: 1px solid #d8dee8; border-radius: 8px; padding: 18px; margin-bottom: 18px; }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; border: 1px solid #cbd5e1; font-size: 12px; background: #f8fafc; }}
    .badge-pass, .badge-converged, .badge-idle {{ background: #ecfdf3; color: #166534; border-color: #bbf7d0; }}
    .badge-ready_to_resume, .badge-approved_open {{ background: #fff7ed; color: #9a3412; border-color: #fed7aa; }}
    .badge-external_blocker, .badge-blocked, .badge-fail {{ background: #fef2f2; color: #991b1b; border-color: #fecaca; }}
    code {{ background: #eef2f7; color: #1f2937; padding: 2px 5px; border-radius: 4px; }}
    header code {{ background: #273449; color: #f8fafc; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 18px 16px; }}
      .metric strong {{ font-size: 20px; }}
      section {{ padding: 14px; }}
      table {{ min-width: 760px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>UltraWork Monitor</h1>
    <p>Dashboard ID: <code>{html.escape(str(dashboard.get('dashboard_id', '')))}</code></p>
    <p>Generated: {html.escape(str(dashboard.get('generated_at', '')))}</p>
  </header>
  <main>
    <div class="grid">
      <div class="metric">Status<strong>{html.escape(str(summary.get('status', '')))}</strong></div>
      <div class="metric">Next action<strong>{html.escape(str(summary.get('next_action', '')))}</strong></div>
      <div class="metric">Active team<strong>{html.escape(str(agent_team.get('team_size', 0)))}</strong></div>
      <div class="metric">Completed<strong>{html.escape(str(summary.get('completed_count', 0)))}</strong></div>
      <div class="metric">Open approved<strong>{html.escape(str(summary.get('open_approved_count', 0)))}</strong></div>
    </div>
    <section>
      <h2>Active Agent Team</h2>
      <p>Mode: <code>{html.escape(str(agent_team.get('mode', '')))}</code>. {html.escape(str(agent_team.get('retired_role_policy', '')))}</p>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Agent</th><th>Scope</th></tr></thead>
          <tbody>{team_rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Resume Decision</h2>
      <p>{html.escape(str(summary.get('reason', '')))}</p>
      <p>Selected record: <code>{html.escape(str(dashboard.get('selected_next_record', {}).get('record_id', '')))}</code></p>
    </section>
    <section>
      <h2>Agent Lanes</h2>
      <div class="table-scroll">
        <table>
          <thead><tr><th>Run</th><th>Agent</th><th>Queue Item</th><th>Task</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Gates</h2>
      <ul>{gate_rows}</ul>
    </section>
    <section>
      <h2>Blockers</h2>
      <ul>{blocker_rows}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_ultrawork_dashboard_artifacts(
    dashboard: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON and HTML artifacts and return the updated dashboard payload."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    html_path = artifact_dir / HTML_NAME
    payload = json.loads(json.dumps(dashboard))
    payload["artifact_paths"]["dashboard_json"] = str(json_path)
    payload["artifact_paths"]["dashboard_html"] = str(html_path)
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    html_path.write_text(render_ultrawork_dashboard_html(payload), encoding="utf-8")
    return payload

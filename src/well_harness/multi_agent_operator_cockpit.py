"""Read-only multi-agent operator cockpit artifact builder."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_team import active_agent_team_payload


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_operator_cockpit_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-operator-cockpit"
COCKPIT_ID = "multi-agent-operator-cockpit-v0.1"
JSON_NAME = "multi_agent_operator_cockpit_v0_1.json"
MARKDOWN_NAME = "multi_agent_operator_cockpit_v0_1.md"
HTML_NAME = "multi_agent_operator_cockpit_v0_1.html"


VISIBLE_PROGRESS_CARDS: tuple[dict[str, str], ...] = (
    {
        "label": "Visible product work",
        "value": "Project cockpit first",
        "detail": "Default next slices should expose progress in a local UI before adding more governance packets.",
    },
    {
        "label": "Simplified agent flow",
        "value": "5 active agents",
        "detail": "Legacy role names remain task labels; they are not extra active participants.",
    },
    {
        "label": "UltraWork position",
        "value": "Monitor only",
        "detail": "UltraWork is a read-only signal source, not the main development narrative.",
    },
    {
        "label": "Release boundary",
        "value": "Owner decides",
        "detail": "Acceptance still requires an explicit project-owner decision outside this packet.",
    },
)

SIMPLIFIED_DELIVERY_FLOW: tuple[dict[str, str], ...] = (
    {
        "step": "1",
        "label": "Ship a visible UI or product slice",
        "gate": "Focused unit tests for the touched surface.",
    },
    {
        "step": "2",
        "label": "Run the smallest deterministic gate",
        "gate": "Use full suite only for milestone, PR, or release boundaries.",
    },
    {
        "step": "3",
        "label": "Open it locally and check geometry",
        "gate": "Desktop and mobile screenshots must be nonblank with no horizontal overflow.",
    },
    {
        "step": "4",
        "label": "Package only explicit pathspecs",
        "gate": "No unrelated docs, artifacts, control-plane files, or controller truth changes.",
    },
    {
        "step": "5",
        "label": "Ask for owner decision only when needed",
        "gate": "Do not invent acceptance, merge approval, or review-thread resolution.",
    },
)

NEXT_VISIBLE_SLICE = (
    "Default to a workbench or demo UI improvement next: make the change visible locally, "
    "validate the touched surface, then package only that slice."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path(payload: dict[str, Any], *keys: str) -> str:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return str(current or "")


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _all_gate_values_pass(gates: dict[str, Any]) -> bool:
    return all(value == "pass" for value in gates.values())


def _copy_blockers(ultrawork_dashboard: dict[str, Any]) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    for item in ultrawork_dashboard.get("blockers", []):
        if isinstance(item, dict):
            copied.append(
                {
                    "blocker_id": str(item.get("blocker_id", "")),
                    "status": str(item.get("status", "")),
                    "message": str(item.get("message", "")),
                }
            )
    return copied


def _copy_agent_team(ultrawork_dashboard: dict[str, Any]) -> dict[str, Any]:
    agent_team = ultrawork_dashboard.get("agent_team", {})
    if not isinstance(agent_team, dict):
        return active_agent_team_payload()
    active_agents = agent_team.get("active_agents", [])
    if not isinstance(active_agents, list) or len(active_agents) != 5:
        return active_agent_team_payload()
    return {
        "mode": str(agent_team.get("mode", "")),
        "team_size": int(agent_team.get("team_size", 0) or 0),
        "active_agents": [
            {
                "agent_id": str(agent.get("agent_id", "")),
                "name": str(agent.get("name", "")),
                "scope": str(agent.get("scope", "")),
            }
            for agent in active_agents
            if isinstance(agent, dict)
        ],
        "retired_role_policy": str(agent_team.get("retired_role_policy", "")),
    }


def build_multi_agent_operator_cockpit(
    *,
    project_status: dict[str, Any],
    ultrawork_dashboard: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build an operator-facing cockpit payload from existing read-only artifacts."""
    project_gates = project_status.get("deterministic_gates", {})
    ultrawork_gates = ultrawork_dashboard.get("gates", {})
    if not isinstance(project_gates, dict):
        project_gates = {}
    if not isinstance(ultrawork_gates, dict):
        ultrawork_gates = {}

    boundary = project_status.get("boundary", {})
    if not isinstance(boundary, dict):
        boundary = {}
    controller_truth_modified = bool(boundary.get("controller_truth_modified", True))
    ui_layout_modified = bool(boundary.get("ui_layout_modified", True))
    project_status_ok = project_status.get("status") == "pass"
    ultrawork_status_ok = ultrawork_dashboard.get("status") == "pass"
    local_boundary_ok = not controller_truth_modified and not ui_layout_modified

    gates = {
        "project_status": _gate_status(project_status_ok),
        "ultrawork_monitor": _gate_status(ultrawork_status_ok),
        "queue_cursor": _gate_status(_path(project_status, "cursor", "status") == "pass"),
        "operator_boundary": _gate_status(local_boundary_ok),
    }
    status = "pass" if _all_gate_values_pass(gates) else "fail"
    completed_count = int(_path(project_status, "completed", "completed_count") or 0)
    open_approved_count = int(_path(ultrawork_dashboard, "summary", "open_approved_count") or 0)
    latest_record_id = _path(project_status, "completed", "last_completed_record_id")
    selected_next_record_id = _path(ultrawork_dashboard, "selected_next_record", "record_id")

    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "cockpit_id": COCKPIT_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M22",
            "name": "Multi-Agent Operator Cockpit",
            "claim": "read_only_operator_dashboard_package",
            "activation_status": "ready_for_pr_packaging_m21_implementation_still_owner_gated",
        },
        "agent_team": _copy_agent_team(ultrawork_dashboard),
        "summary": {
            "headline": (
                "Project progress is visible; the multi-agent lane is capped at five "
                "and UltraWork is monitor-only."
            ),
            "project_status": str(project_status.get("status", "")),
            "ultrawork_status": str(ultrawork_dashboard.get("status", "")),
            "completed_count": completed_count,
            "open_approved_count": open_approved_count,
            "latest_completed_record_id": latest_record_id,
            "selected_next_record_id": selected_next_record_id,
            "recommended_next_step": str(project_status.get("recommended_next_step", "")),
        },
        "operator_views": [
            {
                "view_id": "project-manager-status",
                "label": "Project Manager Status",
                "status": str(project_status.get("status", "")),
                "html": _path(project_status, "artifact_paths", "summary_html"),
                "json": _path(project_status, "artifact_paths", "summary_json"),
            },
            {
                "view_id": "ultrawork-monitor",
                "label": "UltraWork Monitor",
                "status": str(ultrawork_dashboard.get("status", "")),
                "html": _path(ultrawork_dashboard, "artifact_paths", "dashboard_html"),
                "json": _path(ultrawork_dashboard, "artifact_paths", "dashboard_json"),
            },
        ],
        "gates": gates,
        "blockers": _copy_blockers(ultrawork_dashboard),
        "dependency_boundary": {
            "controller_truth_modified": controller_truth_modified,
            "ui_layout_modified": ui_layout_modified,
            "control_plane_source": "repo_github_local_artifacts",
            "pathspec_package": "docs/coordination/multi-agent-operator-cockpit.md",
            "excluded_paths": [
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
                "src/well_harness/demo_server.py",
                "src/well_harness/requirements_intake/**",
                "src/well_harness/static/**",
                ".planning/**",
                "artifacts/**",
            ],
        },
        "artifact_paths": {
            "cockpit_json": "",
            "cockpit_markdown": "",
            "cockpit_html": "",
            "project_status_json": _path(project_status, "artifact_paths", "summary_json"),
            "project_status_html": _path(project_status, "artifact_paths", "summary_html"),
            "ultrawork_dashboard_json": _path(ultrawork_dashboard, "artifact_paths", "dashboard_json"),
            "ultrawork_dashboard_html": _path(ultrawork_dashboard, "artifact_paths", "dashboard_html"),
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_operator_cockpit_markdown(cockpit: dict[str, Any]) -> str:
    """Render a concise Markdown handoff for the cockpit package."""
    summary = cockpit["summary"]
    gates = "\n".join(f"- {name}: `{status}`" for name, status in cockpit["gates"].items())
    blockers = "\n".join(
        f"- {item['blocker_id']} ({item['status']}): {item['message']}"
        for item in cockpit["blockers"]
    ) or "- none"
    team = "\n".join(
        f"- {item['name']}: {item['scope']}"
        for item in cockpit["agent_team"]["active_agents"]
    )
    views = "\n".join(
        f"- {view['label']}: `{view['html']}`"
        for view in cockpit["operator_views"]
    )
    excluded = "\n".join(
        f"- `{path}`" for path in cockpit["dependency_boundary"]["excluded_paths"]
    )
    return (
        "# Multi-Agent Operator Cockpit\n\n"
        f"Status: `{cockpit['status']}`\n\n"
        "## Summary\n\n"
        f"- Completed queue records: `{summary['completed_count']}`\n"
        f"- Resume-sample open approved records: `{summary['open_approved_count']}`\n"
        f"- Latest completed record: `{summary['latest_completed_record_id']}`\n"
        f"- Selected next record: `{summary['selected_next_record_id']}`\n"
        f"- Recommended next step: {summary['recommended_next_step']}\n\n"
        "## Operator Views\n\n"
        f"{views}\n\n"
        "## Active Agent Team\n\n"
        f"Mode: `{cockpit['agent_team']['mode']}`; size: `{cockpit['agent_team']['team_size']}`\n\n"
        f"{team}\n\n"
        "## Gates\n\n"
        f"{gates}\n\n"
        "## Blockers\n\n"
        f"{blockers}\n\n"
        "## Excluded Paths\n\n"
        f"{excluded}\n"
    )


def render_multi_agent_operator_cockpit_html(cockpit: dict[str, Any]) -> str:
    """Render a responsive static HTML cockpit."""
    summary = cockpit["summary"]
    progress_cards = "\n".join(
        "<article class=\"progress-card\">"
        f"<span>{_escape(item['label'])}</span>"
        f"<strong>{_escape(item['value'])}</strong>"
        f"<p>{_escape(item['detail'])}</p>"
        "</article>"
        for item in VISIBLE_PROGRESS_CARDS
    )
    flow_steps = "\n".join(
        "<li>"
        f"<strong>{_escape(item['step'])}. {_escape(item['label'])}</strong>"
        f"<span>{_escape(item['gate'])}</span>"
        "</li>"
        for item in SIMPLIFIED_DELIVERY_FLOW
    )
    views = "\n".join(
        "<article class=\"view-card\">"
        f"<span>{_escape(view['label'])}</span>"
        f"<strong>{_escape(view['status'])}</strong>"
        f"<code>{_escape(view['html'])}</code>"
        "</article>"
        for view in cockpit["operator_views"]
    )
    gates = "\n".join(
        "<tr>"
        f"<td>{_escape(name.replace('_', ' '))}</td>"
        f"<td><span class=\"badge badge-{_escape(status)}\">{_escape(status)}</span></td>"
        "</tr>"
        for name, status in cockpit["gates"].items()
    )
    blockers = "\n".join(
        "<li>"
        f"<strong>{_escape(item['blocker_id'])}</strong> "
        f"<span class=\"badge badge-{_escape(item['status'])}\">{_escape(item['status'])}</span> "
        f"{_escape(item['message'])}"
        "</li>"
        for item in cockpit["blockers"]
    ) or "<li>No active blockers.</li>"
    team = "\n".join(
        "<tr>"
        f"<td>{_escape(item['name'])}</td>"
        f"<td>{_escape(item['scope'])}</td>"
        "</tr>"
        for item in cockpit["agent_team"]["active_agents"]
    )
    excluded = "\n".join(
        f"<li><code>{_escape(path)}</code></li>"
        for path in cockpit["dependency_boundary"]["excluded_paths"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Project Progress Cockpit</title>
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
    .subtitle {{ margin-top: 10px; color: #d5d9e2; max-width: 880px; }}
    .grid {{
      display: grid;
      gap: 14px;
      margin-bottom: 18px;
    }}
    .metrics {{ grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); }}
    .views, .progress {{ grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr)); }}
    section, .metric, .view-card, .progress-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric span, .view-card span, .progress-card span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .metric strong, .view-card strong, .progress-card strong {{
      display: block;
      font-size: 22px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }}
    .progress-card p {{
      margin-top: 8px;
      color: var(--muted);
    }}
    code {{
      display: inline-block;
      max-width: 100%;
      overflow-wrap: anywhere;
      background: #eef2f7;
      border-radius: 4px;
      padding: 2px 5px;
      color: #1f2937;
    }}
    .view-card code {{ margin-top: 8px; font-size: 12px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      overflow-wrap: anywhere;
    }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
      border: 1px solid var(--line);
      background: #f8fafc;
    }}
    .badge-pass {{ color: var(--ok); background: var(--ok-bg); }}
    .badge-fail {{ color: var(--bad); background: var(--bad-bg); }}
    .badge-external_blocker {{ color: var(--bad); background: var(--bad-bg); }}
    ul {{ margin: 0; padding-left: 20px; }}
    li + li {{ margin-top: 8px; }}
    .decision {{
      border-left: 5px solid var(--warn);
      background: var(--warn-bg);
    }}
    .flow {{
      counter-reset: flow;
      list-style: none;
      padding: 0;
      display: grid;
      gap: 10px;
    }}
    .flow li {{
      display: grid;
      gap: 5px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }}
    .flow span {{
      color: var(--muted);
    }}
    @media (max-width: 720px) {{
      header, main {{ padding: 20px 16px; }}
      h1 {{ font-size: 24px; }}
      .metric strong, .view-card strong {{ font-size: 20px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Project Progress Cockpit</h1>
    <p class="subtitle">{_escape(summary['headline'])}</p>
    <p class="subtitle">M22 Multi-Agent Operator Cockpit is now presented as a smaller project-progress surface.</p>
  </header>
  <main>
    <div class="grid metrics">
      <div class="metric"><span>Status</span><strong>{_escape(cockpit['status'])}</strong></div>
      <div class="metric"><span>Completed</span><strong>{_escape(summary['completed_count'])}</strong></div>
      <div class="metric"><span>Resume sample open</span><strong>{_escape(summary['open_approved_count'])}</strong></div>
      <div class="metric"><span>Selected next</span><strong>{_escape(summary['selected_next_record_id'])}</strong></div>
    </div>
    <section>
      <h2>What Is Actually Moving</h2>
      <div class="grid progress">{progress_cards}</div>
    </section>
    <section>
      <h2>Simplified Delivery Flow</h2>
      <ol class="flow">{flow_steps}</ol>
    </section>
    <section class="grid decision">
      <h2>Next Visible Slice</h2>
      <p>{_escape(NEXT_VISIBLE_SLICE)}</p>
    </section>
    <section class="grid decision">
      <h2>Owner Gate Note</h2>
      <p>{_escape(summary['recommended_next_step'])}</p>
    </section>
    <section>
      <h2>Operator Views</h2>
      <div class="grid views">{views}</div>
    </section>
    <section>
      <h2>Active Agent Team</h2>
      <p>Mode <code>{_escape(cockpit['agent_team']['mode'])}</code>, team size <code>{_escape(cockpit['agent_team']['team_size'])}</code>. {_escape(cockpit['agent_team']['retired_role_policy'])}</p>
      <table><tbody>{team}</tbody></table>
    </section>
    <section>
      <h2>Gates</h2>
      <table><tbody>{gates}</tbody></table>
    </section>
    <section>
      <h2>Blockers</h2>
      <ul>{blockers}</ul>
    </section>
    <section>
      <h2>Excluded Paths</h2>
      <p>Control boundary <code>{_escape(cockpit['dependency_boundary']['control_plane_source'])}</code>.</p>
      <ul>{excluded}</ul>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_operator_cockpit_artifacts(
    cockpit: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write JSON, Markdown, and HTML artifacts and return the final payload."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    payload = json.loads(json.dumps(cockpit))
    payload["artifact_paths"]["cockpit_json"] = str(json_path)
    payload["artifact_paths"]["cockpit_markdown"] = str(markdown_path)
    payload["artifact_paths"]["cockpit_html"] = str(html_path)
    markdown_path.write_text(
        render_multi_agent_operator_cockpit_markdown(payload),
        encoding="utf-8",
    )
    html_path.write_text(
        render_multi_agent_operator_cockpit_html(payload),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload

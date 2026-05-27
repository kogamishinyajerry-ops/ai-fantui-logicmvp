#!/usr/bin/env python3
"""Generate a project-owner status summary from queue cursor artifacts."""
from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-project-manager-status-summary")
STATUS_PANEL_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-manager-status-panel.md"
ACCEPTANCE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "project-visibility-mvp-acceptance.md"
)
SUMMARY_JSON_NAME = "project_manager_status_summary.json"
SUMMARY_MARKDOWN_NAME = "project_manager_status_summary.md"
SUMMARY_HTML_NAME = "project_manager_status_summary.html"
SUMMARY_KIND = "ai-fantui-project-manager-status-summary"
SUMMARY_ID = "project-manager-status-summary-v0.1"
PROJECT_VISIBILITY_GATE_COMMAND = "make project-visibility-mvp-gate"
CURRENT_MVP_NAME = "Multi-Agent Candidate Repair Pipeline MVP"
CURRENT_QUEUE_ID = "approved-candidate-task-queue-v0.8"
LAST_COMPLETED_RECORD_ID = "RUN-QUEUE-010"
LAST_COMPLETED_TASK_ID = "TASK-CE-CHECK-UNREACHABLE-STATE-001"
LAST_COMPLETED_QUEUE_ITEM_ID = "queue-safety-unreachable-state-repair"
LAST_COMPLETED_SOURCE_FINDING_CODE = "CHECK_UNREACHABLE_STATE_001"
EXPECTED_STATE_STATUS = "idle_no_open_approved_items"
EXPECTED_COMPLETED_COUNT = 10


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate JSON and Markdown project-owner status artifacts.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_cursor(artifact_dir: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_multi_agent_queue_cursor_state.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "source-cursor-state"),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _status_panel_check() -> dict[str, Any]:
    if not STATUS_PANEL_PATH.exists():
        return {
            "status": "fail",
            "path": str(STATUS_PANEL_PATH),
            "mismatches": ["project-manager-status-panel.md is missing"],
        }
    text = STATUS_PANEL_PATH.read_text(encoding="utf-8")
    required_markers = [
        CURRENT_MVP_NAME,
        CURRENT_QUEUE_ID,
        LAST_COMPLETED_RECORD_ID,
        LAST_COMPLETED_TASK_ID,
        EXPECTED_STATE_STATUS,
        "Do not continue M21 immediately.",
    ]
    mismatches = [
        f"missing marker: {marker}"
        for marker in required_markers
        if marker not in text
    ]
    return {
        "status": "pass" if not mismatches else "fail",
        "path": str(STATUS_PANEL_PATH),
        "date": _panel_date(text),
        "mismatches": mismatches,
    }


def _panel_date(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Date:"):
            return line.split("Date:", 1)[1].strip()
    return ""


def _cursor_record_with_finding(
    record: dict[str, Any],
    ledger_records_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    record_id = str(record.get("record_id", ""))
    ledger_record = ledger_records_by_id.get(record_id, {})
    return {
        "record_id": record_id,
        "queue_item_id": str(record.get("queue_item_id", "")),
        "task_id": str(record.get("task_id", "")),
        "source_finding_code": str(ledger_record.get("source_finding_code", "")),
        "status": str(record.get("status", "")),
    }


def _load_source_ledger(cursor_payload: dict[str, Any]) -> tuple[dict[str, Any], Path | None]:
    source_path_text = cursor_payload.get("artifact_paths", {}).get("source_ledger", "")
    if not source_path_text:
        return {}, None
    source_path = Path(str(source_path_text))
    if not source_path.exists():
        return {}, source_path
    return _load_json(source_path), source_path


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _next_stage_choices() -> list[dict[str, Any]]:
    return [
        {
            "id": "accept",
            "name": "Accept Customer Demo Evidence",
            "recommendation": "unblocks_m21_after_external_evidence_acceptance",
            "final_acceptance": "granted_for_customer_demo_mvp_evidence_only",
            "m21_queue_unblocked": True,
            "next_action": "start M21 as the streamed authoring specialist-team implementation milestone",
            "project_owner_meaning": "Accept the current evidence boundary without claiming production, certification, or controller truth readiness.",
        },
        {
            "id": "external_review",
            "name": "External Review",
            "recommendation": "keeps_m21_blocked",
            "final_acceptance": "not_granted",
            "m21_queue_unblocked": False,
            "next_action": "send the handoff packet to a read-only reviewer and ingest one verdict",
            "project_owner_meaning": "Ask for an independent evidence verdict before accepting or polishing the demo.",
        },
        {
            "id": "demo_polish",
            "name": "Return to Demo Polish",
            "recommendation": "keeps_m21_blocked",
            "final_acceptance": "not_granted",
            "m21_queue_unblocked": False,
            "next_action": "improve visible demo evidence before another owner decision",
            "project_owner_meaning": "Do not accept yet; improve the project-owner-facing demo evidence first.",
        },
    ]


def _markdown_summary(payload: dict[str, Any]) -> str:
    choices = "\n".join(
        "| {id} | {name} | {recommendation} | {final_acceptance} | {m21} | {meaning} |".format(
            id=choice["id"],
            name=choice["name"],
            recommendation=choice["recommendation"],
            final_acceptance=choice["final_acceptance"],
            m21=str(choice["m21_queue_unblocked"]),
            meaning=choice["project_owner_meaning"],
        )
        for choice in payload["next_stage_choices"]
    )
    completed = payload["completed"]
    not_completed = "\n".join(f"- {item}" for item in payload["not_completed"])
    risks = "\n".join(
        f"- {risk['id']} ({risk['level']}): {risk['summary']}"
        for risk in payload["risks"]
    )
    return (
        "# Project Manager Status Summary\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Formal Entry Point\n\n"
        f"- HTML: `{payload['entrypoint']['html']}`\n"
        f"- Acceptance gate: `{payload['entrypoint']['acceptance_gate']}`\n\n"
        "## Current MVP\n\n"
        f"- Name: `{payload['current_mvp']['name']}`\n"
        f"- State: `{payload['current_mvp']['state']}`\n"
        f"- Queue: `{payload['current_mvp']['queue_id']}`\n"
        f"- Cursor: `{payload['cursor']['state_status']}`\n\n"
        "## Completed\n\n"
        f"- Completed queue records: `{completed['completed_count']}`\n"
        f"- Latest completed record: `{completed['last_completed_record_id']}`\n"
        f"- Latest completed task: `{completed['last_completed_task_id']}`\n"
        f"- Latest queue item: `{completed['last_completed_queue_item_id']}`\n\n"
        "## Not Completed\n\n"
        f"{not_completed}\n\n"
        "## Risks\n\n"
        f"{risks}\n\n"
        "## Project Owner Decision Choices\n\n"
        "| Choice | Name | Recommendation | Final acceptance | M21 queue unblocked | Project-owner meaning |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"{choices}\n\n"
        "## Recommended Decision\n\n"
        f"{payload['recommended_next_step']}\n\n"
        "## Boundary\n\n"
        "- Controller truth modified: "
        f"`{payload['boundary']['controller_truth_modified']}`\n"
        "- Requirements-intake UI modified: "
        f"`{payload['boundary']['ui_layout_modified']}`\n"
    )


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _status_badge(status: str) -> str:
    class_name = "status-pass" if status == "pass" else "status-fail"
    label = "On track" if status == "pass" else "Needs attention"
    return f'<span class="badge {class_name}">{_escape(label)}</span>'


def _html_summary(payload: dict[str, Any]) -> str:
    completed = payload["completed"]
    cursor = payload["cursor"]
    current_mvp = payload["current_mvp"]
    completed_rows = "\n".join(
        "<tr>"
        f"<td>{_escape(record['record_id'])}</td>"
        f"<td>{_escape(record['source_finding_code'])}</td>"
        f"<td>{_escape(record['status'])}</td>"
        "</tr>"
        for record in completed["records"]
    )
    risks = "\n".join(
        "<li>"
        f"<strong>{_escape(risk['summary'])}</strong>"
        f"<span>{_escape(risk['control'])}</span>"
        "</li>"
        for risk in payload["risks"]
    )
    choices = "\n".join(
        "<article class=\"choice\">"
        f"<div class=\"choice-id\">{_escape(choice['id'])}</div>"
        "<div>"
        f"<h3>{_escape(choice['name'])}</h3>"
        f"<p>{_escape(choice['project_owner_meaning'])}</p>"
        f"<p>Final acceptance: {_escape(choice['final_acceptance'])}</p>"
        f"<p>M21 queue unblocked: {_escape(choice['m21_queue_unblocked'])}</p>"
        f"<span>{_escape(choice['recommendation'])}</span>"
        "</div>"
        "</article>"
        for choice in payload["next_stage_choices"]
    )
    not_completed = "\n".join(
        f"<li>{_escape(item)}</li>" for item in payload["not_completed"]
    )
    gate_rows = "\n".join(
        "<tr>"
        f"<td>{_escape(name.replace('_', ' '))}</td>"
        f"<td>{_escape(status)}</td>"
        "</tr>"
        for name, status in payload["deterministic_gates"].items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Project Manager Status Summary</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5b6474;
      --line: #d8dde7;
      --panel: #ffffff;
      --page: #f6f7f9;
      --accent: #0f766e;
      --accent-soft: #d9f3ee;
      --warn: #a16207;
      --warn-soft: #fff2c6;
      --risk: #b42318;
      --risk-soft: #ffe4df;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--page);
      color: var(--ink);
      line-height: 1.5;
    }}
    .shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 20px 40px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1, h2, h3, p {{
      margin: 0;
    }}
    h1 {{
      font-size: 30px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 17px;
      letter-spacing: 0;
      margin-bottom: 12px;
    }}
    h3 {{
      font-size: 15px;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin-top: 10px;
      color: var(--muted);
      max-width: 760px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      border-radius: 8px;
      padding: 5px 10px;
      font-weight: 700;
      white-space: nowrap;
      border: 1px solid transparent;
    }}
    .status-pass {{
      color: #075e54;
      background: var(--accent-soft);
      border-color: #98d8cc;
    }}
    .status-fail {{
      color: #8a1f16;
      background: var(--risk-soft);
      border-color: #ffb4a8;
    }}
    .grid {{
      display: grid;
      gap: 16px;
      margin-top: 18px;
    }}
    .metrics {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .two-col {{
      grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
    }}
    section, .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric span {{
      color: var(--muted);
      display: block;
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .metric strong {{
      display: block;
      font-size: 23px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }}
    .decision {{
      border-left: 5px solid var(--accent);
      background: #f9fbfb;
    }}
    .decision p {{
      font-size: 18px;
      font-weight: 700;
      color: #0b534b;
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
    }}
    li + li {{
      margin-top: 8px;
    }}
    .risk-list {{
      list-style: none;
      padding: 0;
    }}
    .risk-list li {{
      border-left: 4px solid var(--warn);
      background: var(--warn-soft);
      border-radius: 6px;
      padding: 10px 12px;
    }}
    .risk-list span {{
      display: block;
      color: var(--muted);
      margin-top: 3px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      overflow-wrap: anywhere;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .choices {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .choice {{
      display: grid;
      grid-template-columns: 38px minmax(0, 1fr);
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fcfcfd;
    }}
    .choice-id {{
      display: grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: var(--accent-soft);
      color: #075e54;
      font-weight: 800;
    }}
    .choice p {{
      color: var(--muted);
      margin-top: 4px;
    }}
    .choice span {{
      display: inline-block;
      margin-top: 8px;
      color: var(--warn);
      font-weight: 700;
      font-size: 12px;
    }}
    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 860px) {{
      header,
      .metrics,
      .two-col,
      .choices {{
        grid-template-columns: 1fr;
      }}
      .shell {{
        padding: 20px 14px 28px;
      }}
      h1 {{
        font-size: 24px;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div>
        <h1>Project Manager Status Summary</h1>
        <p class="subtitle">{_escape(payload['project_owner_message'])}</p>
      </div>
      <div>{_status_badge(payload['status'])}</div>
    </header>

    <div class="grid metrics">
      <div class="metric"><span>Current MVP</span><strong>{_escape(current_mvp['name'])}</strong></div>
      <div class="metric"><span>Queue records completed</span><strong>{_escape(completed['completed_count'])}</strong></div>
      <div class="metric"><span>Latest run</span><strong>{_escape(completed['last_completed_record_id'])}</strong></div>
      <div class="metric"><span>Cursor</span><strong>{_escape(cursor['state_status'])}</strong></div>
    </div>

    <section class="grid decision">
      <h2>Recommended Decision</h2>
      <p>{_escape(payload['recommended_next_step'])}</p>
    </section>

    <div class="grid two-col">
      <section>
        <h2>Completed Queue</h2>
        <table>
          <thead><tr><th>Record</th><th>Finding</th><th>Status</th></tr></thead>
          <tbody>{completed_rows}</tbody>
        </table>
      </section>
      <section>
        <h2>Not Completed</h2>
        <ul>{not_completed}</ul>
      </section>
    </div>

    <div class="grid two-col">
      <section>
        <h2>Main Risks</h2>
        <ul class="risk-list">{risks}</ul>
      </section>
      <section>
        <h2>Deterministic Gates</h2>
        <table>
          <thead><tr><th>Gate</th><th>Result</th></tr></thead>
          <tbody>{gate_rows}</tbody>
        </table>
      </section>
    </div>

    <section class="grid">
      <h2>Next Stage Choices</h2>
      <div class="choices">{choices}</div>
    </section>

    <footer>
      Source panel: {_escape(payload['artifact_paths']['status_panel'])}<br>
      Acceptance gate: {_escape(payload['entrypoint']['acceptance_gate'])}
    </footer>
  </main>
</body>
</html>
"""


def run_project_manager_status_summary(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / SUMMARY_JSON_NAME
    markdown_path = artifact_dir / SUMMARY_MARKDOWN_NAME
    html_path = artifact_dir / SUMMARY_HTML_NAME

    cursor_result = _run_cursor(artifact_dir)
    cursor_payload = cursor_result["payload"]
    source_ledger, source_ledger_path = _load_source_ledger(cursor_payload)
    source_records = [
        record
        for record in source_ledger.get("run_records", [])
        if isinstance(record, dict)
    ]
    source_records_by_id = {
        str(record.get("record_id", "")): record for record in source_records
    }
    panel_check = _status_panel_check()
    aggregate = cursor_payload.get("aggregate", {})
    cursor_position = cursor_payload.get("cursor_position", {})
    cursor_ok = (
        cursor_result["returncode"] == 0
        and cursor_payload.get("status") == "pass"
        and cursor_payload.get("state_status") == EXPECTED_STATE_STATUS
    )
    last_completed_record = next(
        (
            record
            for record in cursor_payload.get("completed_records", [])
            if isinstance(record, dict)
            and record.get("record_id") == LAST_COMPLETED_RECORD_ID
        ),
        {},
    )
    last_completed_ledger_record = source_records_by_id.get(LAST_COMPLETED_RECORD_ID, {})
    last_completed_task_ok = (
        last_completed_record.get("task_id") == LAST_COMPLETED_TASK_ID
    )
    last_completed_finding_ok = (
        last_completed_ledger_record.get("source_finding_code")
        == LAST_COMPLETED_SOURCE_FINDING_CODE
    )
    queue_progress_ok = (
        aggregate.get("completed_count") == EXPECTED_COMPLETED_COUNT
        and aggregate.get("open_approved_count") == 0
        and cursor_position.get("last_completed_record_id") == LAST_COMPLETED_RECORD_ID
        and cursor_position.get("last_completed_queue_item_id") == LAST_COMPLETED_QUEUE_ITEM_ID
        and last_completed_task_ok
        and last_completed_finding_ok
    )
    boundary_ok = (
        aggregate.get("controller_truth_modified") is False
        and aggregate.get("ui_layout_modified") is False
    )
    panel_ok = panel_check["status"] == "pass"

    deterministic_gates = {
        "source_cursor": _gate_status(cursor_ok),
        "queue_progress": _gate_status(queue_progress_ok),
        "status_panel": _gate_status(panel_ok),
        "boundary": _gate_status(boundary_ok),
        "summary_artifacts": "fail",
        "local_gate": "fail",
    }
    status = "fail"

    completed_records = [
        _cursor_record_with_finding(record, source_records_by_id)
        for record in cursor_payload.get("completed_records", [])
        if isinstance(record, dict)
    ]
    payload = {
        "schema_version": "0.1",
        "kind": SUMMARY_KIND,
        "summary_id": SUMMARY_ID,
        "status": status,
        "as_of": panel_check.get("date", ""),
        "project_owner_message": (
            "The Project Visibility MVP entrypoint and Customer Demo MVP closeout are gateable; "
            "the next step is a three-option project-owner decision packet."
        ),
        "current_mvp": {
            "name": CURRENT_MVP_NAME,
            "state": "engineering_pipeline_mvp_complete_product_mvp_not_closed",
            "queue_id": CURRENT_QUEUE_ID,
            "claim": "internal multi-agent engineering pipeline MVP",
            "non_claims": [
                "not a final customer-facing product MVP",
                "not a certification or DAL readiness claim",
                "not a trusted controller-truth promotion",
            ],
        },
        "entrypoint": {
            "status": "formal_project_visibility_mvp_entrypoint",
            "html": str(html_path),
            "acceptance_gate": PROJECT_VISIBILITY_GATE_COMMAND,
            "acceptance_doc": str(ACCEPTANCE_DOC_PATH),
        },
        "completed": {
            "completed_count": aggregate.get("completed_count", 0),
            "last_completed_record_id": cursor_position.get("last_completed_record_id", ""),
            "last_completed_task_id": LAST_COMPLETED_TASK_ID,
            "last_completed_queue_item_id": cursor_position.get("last_completed_queue_item_id", ""),
            "records": completed_records,
        },
        "cursor": {
            "status": cursor_payload.get("status", "fail"),
            "state_status": cursor_payload.get("state_status", ""),
            "ready_for_resume": aggregate.get("ready_for_resume", False),
            "open_approved_count": aggregate.get("open_approved_count", 0),
            "resume_policy": cursor_payload.get("resume_policy", {}),
        },
        "not_completed": [
            "No explicit project-owner final decision has been accepted yet.",
            "M21 streamed authoring is planning-ready but implementation-blocked.",
            "The generalized C919 ETRAS-style requirements-to-control-panel capability is documented but not implemented.",
            "No production, certification, DAL, or controller-truth claim is granted.",
            "The worktree remains dirty from accumulated construction-lane artifacts.",
        ],
        "risks": [
            {
                "id": "owner-decision-drift",
                "level": "medium",
                "summary": "M21 could be mistaken as already active if the final decision is skipped.",
                "control": "Keep M21 blocked until the project-owner final decision gate returns accepted.",
            },
            {
                "id": "candidate-truth-drift",
                "level": "medium",
                "summary": "Candidate repairs could become too semantic if expanded without review.",
                "control": "Keep repairs candidate-only until controller truth promotion is explicitly approved.",
            },
            {
                "id": "dirty-worktree-confusion",
                "level": "medium",
                "summary": "Untracked and modified construction files make project state harder to audit.",
                "control": "Use the artifact index and path-scoped summaries instead of broad repository status.",
            },
        ],
        "next_stage_choices": _next_stage_choices(),
        "recommended_next_step": (
            "Do not continue M21 immediately. Use the project-owner acceptance review packet, "
            "then choose accept, external_review, or demo_polish."
        ),
        "boundary": {
            "controller_truth_modified": aggregate.get("controller_truth_modified") is not False,
            "ui_layout_modified": aggregate.get("ui_layout_modified") is not False,
            "protected_paths_policy": "no controller truth or requirements-intake UI edits in this slice",
        },
        "deterministic_gates": deterministic_gates,
        "checks": {
            "cursor_returncode": cursor_result["returncode"],
            "queue_progress": {
                "expected_last_completed_record_id": LAST_COMPLETED_RECORD_ID,
                "expected_last_completed_task_id": LAST_COMPLETED_TASK_ID,
                "expected_last_completed_source_finding_code": LAST_COMPLETED_SOURCE_FINDING_CODE,
                "observed_last_completed_task_id": last_completed_record.get("task_id", ""),
                "observed_last_completed_source_finding_code": (
                    last_completed_ledger_record.get("source_finding_code", "")
                ),
            },
            "status_panel": panel_check,
        },
        "artifact_paths": {
            "summary_json": str(summary_path),
            "summary_markdown": str(markdown_path),
            "summary_html": str(html_path),
            "acceptance_doc": str(ACCEPTANCE_DOC_PATH),
            "status_panel": str(STATUS_PANEL_PATH),
            "source_cursor_state": str(
                cursor_payload.get("artifact_paths", {}).get("cursor_state", "")
            ),
            "source_ledger": str(source_ledger_path or ""),
        },
    }
    markdown_path.write_text(_markdown_summary(payload), encoding="utf-8")
    html_path.write_text(_html_summary(payload), encoding="utf-8")
    artifacts_ok = (
        markdown_path.exists()
        and markdown_path.stat().st_size > 0
        and html_path.exists()
        and html_path.stat().st_size > 0
    )
    payload["deterministic_gates"]["summary_artifacts"] = _gate_status(artifacts_ok)
    payload["status"] = (
        "pass"
        if all(
            value == "pass"
            for key, value in payload["deterministic_gates"].items()
            if key != "local_gate"
        )
        else "fail"
    )
    payload["deterministic_gates"]["local_gate"] = payload["status"]
    markdown_path.write_text(_markdown_summary(payload), encoding="utf-8")
    html_path.write_text(_html_summary(payload), encoding="utf-8")
    _write_json(summary_path, payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    payload = run_project_manager_status_summary(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"summary_id: {payload['summary_id']}")
        print(f"status: {payload['status']}")
        print(f"summary_json: {payload['artifact_paths']['summary_json']}")
        print(f"summary_markdown: {payload['artifact_paths']['summary_markdown']}")
        print(f"summary_html: {payload['artifact_paths']['summary_html']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

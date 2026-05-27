"""Read-only pathspec packaging consolidation for the multi-agent lane."""
from __future__ import annotations

import html
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_packaging_consolidation_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-packaging-consolidation"
PACKAGE_ID = "multi-agent-packaging-consolidation-v0.1"
JSON_NAME = "multi_agent_packaging_consolidation_v0_1.json"
MARKDOWN_NAME = "multi_agent_packaging_consolidation_v0_1.md"
HTML_NAME = "multi_agent_packaging_consolidation_v0_1.html"
NOTION_BLOCKER_ID = "notion-control-plane-404"


EXCLUDED_PATHS = [
    ".github/workflows/gsd-automation.yml",
    "artifacts/**",
    "src/well_harness/controller.py",
    "src/well_harness/runner.py",
    "src/well_harness/demo_server.py",
    "src/well_harness/requirements_intake/**",
    "src/well_harness/static/**",
    "tests/test_demo.py",
    "tests/test_requirements_intake_webui.py",
    "tests/test_validation_suite.py",
    "tools/run_gsd_validation_suite.py",
    ".planning/**",
]


PACKAGE_ORDER: list[dict[str, Any]] = [
    {
        "package_id": "multi-agent-cursor-baseline-v0-2",
        "label": "M27 Queue Ledger/Cursor v0.2 Baseline",
        "depends_on": [],
        "claim": (
            "v0.9 multi-agent queue state can be regenerated and verified "
            "through the v0.2 ledger/cursor baseline"
        ),
        "pathspecs": [
            "Makefile",
            "docs/coordination/multi-agent-continuation-checkpoint.md",
            "docs/json_schema/multi_agent_queue_cursor_state_v0_2.schema.json",
            "docs/json_schema/multi_agent_queue_run_ledger_v0_2.schema.json",
            "scripts/run_multi_agent_queue_cursor_state_v0_2.py",
            "scripts/verify_multi_agent_queue_cursor_state_v0_2.py",
            "scripts/run_multi_agent_queue_run_ledger_v0_2.py",
            "scripts/verify_multi_agent_queue_run_ledger_v0_2.py",
            "src/well_harness/agent_task_contract.py",
            "tests/test_agent_task_contract.py",
            "tests/test_multi_agent_queue_cursor_state_v0_2.py",
            "tests/test_multi_agent_queue_run_ledger_v0_2.py",
        ],
        "forced_pathspecs": [],
        "validation_commands": [
            "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_run_ledger_v0_2.py tests/test_multi_agent_queue_cursor_state_v0_2.py tests/test_agent_task_contract.py",
            "AI_FANTUI_QUEUE_PREFLIGHT_MODE=fixture make verify-multi-agent-queue-run-ledger-v0-2",
            "AI_FANTUI_QUEUE_PREFLIGHT_MODE=fixture make verify-multi-agent-queue-cursor-state-v0-2",
            "AI_FANTUI_QUEUE_PREFLIGHT_MODE=fixture make verify-multi-agent-queue-cursor-resume-state-v0-2",
        ],
    },
    {
        "package_id": "project-manager-status",
        "label": "Project Manager Status Package",
        "depends_on": ["multi-agent-cursor-baseline-v0-2"],
        "claim": "project owner can inspect a generated status artifact before M21 activation",
        "pathspecs": [
            "docs/coordination/project-manager-status-panel.md",
            "docs/coordination/project-visibility-mvp-acceptance.md",
            "scripts/run_project_manager_status_summary.py",
            "scripts/verify_project_visibility_mvp_acceptance.py",
            "tests/test_project_manager_status_summary.py",
            "tests/test_project_visibility_mvp_acceptance.py",
        ],
        "forced_pathspecs": [],
        "validation_commands": [
            "PYTHONPATH=src:. python3 -m pytest -q tests/test_project_manager_status_summary.py tests/test_project_visibility_mvp_acceptance.py",
            "make project-manager-status-summary",
            "make project-visibility-mvp-gate",
        ],
    },
    {
        "package_id": "ultrawork-monitor",
        "label": "UltraWork Monitor Package",
        "depends_on": ["multi-agent-cursor-baseline-v0-2"],
        "claim": "Claude Code subagent-style monitor is exposed through a read-only local HTML artifact",
        "pathspecs": [
            "docs/coordination/ultrawork-monitor-pathspec-package.md",
            "docs/json_schema/ultrawork_monitor_dashboard_v0_1.schema.json",
            "scripts/run_ultrawork_monitor_dashboard.py",
            "scripts/verify_ultrawork_monitor_dashboard.py",
            "src/well_harness/ultrawork_monitor_dashboard.py",
            "tests/test_ultrawork_monitor_dashboard.py",
        ],
        "forced_pathspecs": [
            ".claude/agents/ultrawork-orchestrator.md",
            ".claude/agents/ultrawork-logic-ir-agent.md",
            ".claude/agents/ultrawork-evidence-reviewer.md",
        ],
        "validation_commands": [
            "PYTHONPATH=src:. python3 -m pytest -q tests/test_ultrawork_monitor_dashboard.py",
            "make ultrawork-monitor-dashboard",
            "make verify-ultrawork-monitor-dashboard",
        ],
    },
    {
        "package_id": "m22-operator-cockpit",
        "label": "M22 Operator Cockpit Package",
        "depends_on": ["project-manager-status", "ultrawork-monitor"],
        "claim": "operator cockpit aggregates project status, UltraWork monitor, queue health, and blocker state",
        "pathspecs": [
            "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md",
            "docs/coordination/multi-agent-operator-cockpit.md",
            "docs/json_schema/multi_agent_operator_cockpit_v0_1.schema.json",
            "scripts/run_multi_agent_operator_cockpit.py",
            "scripts/verify_multi_agent_operator_cockpit.py",
            "src/well_harness/multi_agent_operator_cockpit.py",
            "tests/test_multi_agent_operator_cockpit.py",
        ],
        "forced_pathspecs": [],
        "validation_commands": [
            "PYTHONPATH=src:. python3 -m pytest -q tests/test_project_manager_status_summary.py tests/test_ultrawork_monitor_dashboard.py tests/test_multi_agent_operator_cockpit.py",
            "make multi-agent-operator-cockpit",
            "make verify-multi-agent-operator-cockpit",
        ],
    },
    {
        "package_id": "m23-packaging-consolidation",
        "label": "M23 Packaging Consolidation Gate",
        "depends_on": ["m22-operator-cockpit"],
        "claim": "the multi-agent PR boundary is staged in explicit dependency order",
        "pathspecs": [
            "docs/coordination/multi-agent-packaging-consolidation.md",
            "docs/json_schema/multi_agent_packaging_consolidation_v0_1.schema.json",
            "scripts/run_multi_agent_packaging_consolidation.py",
            "scripts/verify_multi_agent_packaging_consolidation.py",
            "src/well_harness/multi_agent_packaging_consolidation.py",
            "tests/test_multi_agent_packaging_consolidation.py",
        ],
        "forced_pathspecs": [],
        "validation_commands": [
            "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_packaging_consolidation.py",
            "make multi-agent-packaging-consolidation",
            "make verify-multi-agent-packaging-consolidation",
        ],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_status(pathspecs: list[str], *, project_root: Path) -> dict[str, str]:
    if not pathspecs:
        return {}
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", *pathspecs],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    statuses: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        statuses[path] = status.strip() or "clean"
    return statuses


def _path_exists(pathspec: str, *, project_root: Path) -> bool:
    return (project_root / pathspec).exists()


def _package_with_checks(package: dict[str, Any], *, project_root: Path) -> dict[str, Any]:
    pathspecs = list(package["pathspecs"])
    forced_pathspecs = list(package["forced_pathspecs"])
    statuses = _git_status(pathspecs, project_root=project_root)
    forced_statuses = {
        pathspec: ("ignored_present" if _path_exists(pathspec, project_root=project_root) else "missing")
        for pathspec in forced_pathspecs
    }
    missing = [
        pathspec
        for pathspec in pathspecs + forced_pathspecs
        if not _path_exists(pathspec, project_root=project_root)
    ]
    return {
        "package_id": package["package_id"],
        "label": package["label"],
        "depends_on": package["depends_on"],
        "claim": package["claim"],
        "pathspecs": pathspecs,
        "forced_pathspecs": forced_pathspecs,
        "validation_commands": package["validation_commands"],
        "missing_pathspecs": missing,
        "git_status": {
            "tracked_or_untracked": statuses,
            "forced_ignored": forced_statuses,
        },
        "ready_for_pathspec_staging": not missing,
    }


def _all_pathspecs(packages: list[dict[str, Any]]) -> list[str]:
    pathspecs: list[str] = []
    for package in packages:
        pathspecs.extend(package["pathspecs"])
        pathspecs.extend(package["forced_pathspecs"])
    return pathspecs


def _stage_commands(packages: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for package in packages:
        joined = " \\\n  ".join(package["pathspecs"])
        commands.append(f"git add -- \\\n  {joined}")
        if package["forced_pathspecs"]:
            forced = " \\\n  ".join(package["forced_pathspecs"])
            commands.append(f"git add -f -- \\\n  {forced}")
    return commands


def build_multi_agent_packaging_consolidation(
    *,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a read-only packaging plan for the multi-agent PR boundary."""
    packages = [
        _package_with_checks(package, project_root=project_root)
        for package in PACKAGE_ORDER
    ]
    all_missing = [
        pathspec
        for package in packages
        for pathspec in package["missing_pathspecs"]
    ]
    stageable = not all_missing
    pathspecs = _all_pathspecs(packages)
    status = "pass" if stageable else "fail"
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "package_id": PACKAGE_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M23",
            "name": "Packaging Consolidation",
            "claim": "read_only_explicit_pathspec_pr_boundary",
        },
        "summary": {
            "package_count": len(packages),
            "pathspec_count": len(pathspecs),
            "missing_pathspec_count": len(all_missing),
            "next_action": "stage_packages_in_order_with_explicit_pathspecs",
            "dirty_worktree_policy": "ignore_unrelated_dirty_files_and_stage_only_listed_pathspecs",
        },
        "package_order": packages,
        "stage_commands": _stage_commands(packages),
        "excluded_paths": EXCLUDED_PATHS,
        "blockers": [
            {
                "blocker_id": NOTION_BLOCKER_ID,
                "status": "external_blocker",
                "message": "Notion control-plane HTTP 404 remains outside this packaging slice.",
            }
        ],
        "pr_summary": {
            "title": "Add multi-agent operator cockpit and packaging boundary",
            "body_sections": [
                "Summary",
                "Validation",
                "Notion external blocker",
                "Pathspec packaging boundary",
                "Risks",
            ],
            "notion_blocker_note": "Notion 404 is preserved as an external control-plane blocker; this PR does not change Notion configuration.",
        },
        "artifact_paths": {
            "package_json": "",
            "package_markdown": "",
            "package_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_packaging_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown packaging instructions."""
    package_sections = []
    for package in payload["package_order"]:
        pathspecs = "\n".join(f"  {pathspec} \\" for pathspec in package["pathspecs"]).rstrip(" \\")
        forced = "\n".join(f"  {pathspec} \\" for pathspec in package["forced_pathspecs"]).rstrip(" \\")
        validations = "\n".join(f"- `{command}`" for command in package["validation_commands"])
        force_block = f"\nForced pathspecs:\n\n```sh\ngit add -f -- \\\n{forced}\n```\n" if forced else ""
        package_sections.append(
            f"### {package['label']}\n\n"
            f"Package ID: `{package['package_id']}`\n\n"
            f"Depends on: `{', '.join(package['depends_on']) or 'none'}`\n\n"
            f"Stage:\n\n```sh\ngit add -- \\\n{pathspecs}\n```\n"
            f"{force_block}\n"
            f"Validation:\n\n{validations}\n"
        )
    excluded = "\n".join(f"- `{path}`" for path in payload["excluded_paths"])
    return (
        "# Multi-Agent Packaging Consolidation\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Next action: `{payload['summary']['next_action']}`\n\n"
        "## Package Order\n\n"
        + "\n\n".join(package_sections)
        + "\n\n## Excluded Paths\n\n"
        f"{excluded}\n\n"
        "## Notion Blocker\n\n"
        f"- `{NOTION_BLOCKER_ID}` remains an external control-plane blocker.\n"
    )


def render_multi_agent_packaging_html(payload: dict[str, Any]) -> str:
    """Render a static packaging cockpit page."""
    cards = "\n".join(
        "<article class=\"package\">"
        f"<span>{_escape(package['package_id'])}</span>"
        f"<h2>{_escape(package['label'])}</h2>"
        f"<p>{_escape(package['claim'])}</p>"
        f"<p>Depends on: {_escape(', '.join(package['depends_on']) or 'none')}</p>"
        f"<p>Pathspecs: {_escape(len(package['pathspecs']) + len(package['forced_pathspecs']))}</p>"
        f"<p>Ready: {_escape(package['ready_for_pathspec_staging'])}</p>"
        "</article>"
        for package in payload["package_order"]
    )
    commands = "\n".join(f"<pre>{_escape(command)}</pre>" for command in payload["stage_commands"])
    excluded = "\n".join(f"<li><code>{_escape(path)}</code></li>" for path in payload["excluded_paths"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Packaging Consolidation</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5f6878;
      --line: #d8dee8;
      --page: #f6f7f9;
      --panel: #ffffff;
      --header: #111827;
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
    h1, h2, p {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 30px; line-height: 1.15; }}
    h2 {{ font-size: 18px; margin: 4px 0 8px; }}
    .subtitle {{ color: #d5d9e2; margin-top: 10px; }}
    .grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
      margin: 20px 0;
    }}
    section, .package {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .package span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .package p + p {{ margin-top: 6px; }}
    pre, code {{
      max-width: 100%;
      overflow-x: auto;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
      background: #eef2f7;
      border-radius: 5px;
      padding: 6px 8px;
      color: #1f2937;
    }}
    pre {{ margin: 10px 0 0; }}
    li + li {{ margin-top: 8px; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 20px 16px; }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Multi-Agent Packaging Consolidation</h1>
    <p class="subtitle">Stage the multi-agent lane in dependency order using explicit pathspecs only.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Status: <strong>{_escape(payload['status'])}</strong></p>
      <p>Packages: <strong>{_escape(payload['summary']['package_count'])}</strong></p>
      <p>Pathspecs: <strong>{_escape(payload['summary']['pathspec_count'])}</strong></p>
      <p>Missing pathspecs: <strong>{_escape(payload['summary']['missing_pathspec_count'])}</strong></p>
    </section>
    <div class="grid">{cards}</div>
    <section>
      <h2>Stage Commands</h2>
      {commands}
    </section>
    <section>
      <h2>Excluded Paths</h2>
      <ul>{excluded}</ul>
    </section>
    <section>
      <h2>External Blocker</h2>
      <p><code>{NOTION_BLOCKER_ID}</code> remains an external control-plane blocker.</p>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_packaging_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write packaging JSON, Markdown, and HTML artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    final_payload = json.loads(json.dumps(payload))
    final_payload["artifact_paths"]["package_json"] = str(json_path)
    final_payload["artifact_paths"]["package_markdown"] = str(markdown_path)
    final_payload["artifact_paths"]["package_html"] = str(html_path)
    markdown_path.write_text(render_multi_agent_packaging_markdown(final_payload), encoding="utf-8")
    html_path.write_text(render_multi_agent_packaging_html(final_payload), encoding="utf-8")
    json_path.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return final_payload

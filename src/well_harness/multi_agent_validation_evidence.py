"""Read-only validation evidence capture for the multi-agent lane."""
from __future__ import annotations

import html
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from well_harness.multi_agent_pr_preflight import build_multi_agent_pr_preflight


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_validation_evidence_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-validation-evidence"
EVIDENCE_ID = "multi-agent-validation-evidence-v0.1"
JSON_NAME = "multi_agent_validation_evidence_v0_1.json"
MARKDOWN_NAME = "multi_agent_validation_evidence_v0_1.md"
HTML_NAME = "multi_agent_validation_evidence_v0_1.html"
NOTION_BLOCKER_ID = "notion-control-plane-404"
M25_PACKAGE_ID = "m25-validation-evidence"
M25_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-validation-evidence.md",
    "docs/json_schema/multi_agent_validation_evidence_v0_1.schema.json",
    "scripts/run_multi_agent_validation_evidence.py",
    "scripts/verify_multi_agent_validation_evidence.py",
    "src/well_harness/multi_agent_validation_evidence.py",
    "tests/test_multi_agent_validation_evidence.py",
]
CLASSIFIED_CHANGED_PATHS = [
    "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
    "docs/json_schema/agent_*.schema.json",
    "docs/json_schema/approved_*.schema.json",
    "docs/json_schema/multi_agent_m*.schema.json",
    "docs/json_schema/multi_agent_queue_cursor_state_v0_1.schema.json",
    "docs/json_schema/multi_agent_queue_run_ledger_v0_1.schema.json",
    "pyproject.toml",
    "scripts/run_approved_*.py",
    "scripts/run_evidence_*.py",
    "scripts/run_first_candidate_repair_slice.py",
    "scripts/run_missing_test_result_candidate_repair_slice.py",
    "scripts/run_multi_agent_m*.py",
    "scripts/run_multi_agent_queue_cursor_state.py",
    "scripts/run_multi_agent_queue_run_ledger.py",
    "scripts/run_safety_*_candidate_repair_slice.py",
    "scripts/verify_approved_*.py",
    "scripts/verify_multi_agent_construction_readiness.py",
    "scripts/verify_multi_agent_m*.py",
    "scripts/verify_multi_agent_queue_cursor_state.py",
    "scripts/verify_multi_agent_queue_run_ledger.py",
    "src/well_harness/agent_*.py",
    "tests/fixtures/agent_*.json",
    "tests/fixtures/approved_*.json",
    "tests/fixtures/multi_agent_m*.json",
    "tests/fixtures/multi_agent_queue_*_v0_1.json",
    "tests/test_agent_*.py",
    "tests/test_approved_*.py",
    "tests/test_multi_agent_construction_readiness.py",
    "tests/test_multi_agent_deliverable_plan.py",
    "tests/test_multi_agent_m*.py",
    "tests/test_multi_agent_queue_cursor_state.py",
    "tests/test_multi_agent_queue_run_ledger.py",
]

CommandRunner = Callable[[str, Path], dict[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _output_tail(stdout: str, stderr: str, *, limit: int = 1200) -> str:
    combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part)
    return combined[-limit:] if combined else ""


def _run_command(command: str, project_root: Path) -> dict[str, Any]:
    started = time.time()
    result = subprocess.run(
        command,
        cwd=project_root,
        shell=True,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    return {
        "exit_code": result.returncode,
        "duration_seconds": round(time.time() - started, 2),
        "output_tail": _output_tail(result.stdout, result.stderr),
    }


def execute_validation_plan(
    validation_plan: list[dict[str, Any]],
    *,
    project_root: Path,
    command_runner: CommandRunner | None = None,
) -> list[dict[str, Any]]:
    """Execute validation commands in order and stop after the first failure."""
    runner = command_runner or _run_command
    results: list[dict[str, Any]] = []
    for item in validation_plan:
        command_result = runner(item["command"], project_root)
        status = "pass" if command_result["exit_code"] == 0 else "fail"
        evidence = {
            "command_id": item["command_id"],
            "package_id": item["package_id"],
            "command": item["command"],
            "status": status,
            "exit_code": command_result["exit_code"],
            "duration_seconds": command_result["duration_seconds"],
            "output_tail": command_result["output_tail"],
        }
        results.append(evidence)
        if status != "pass":
            break
    return results


def _m25_package(*, project_root: Path) -> dict[str, Any]:
    missing = [
        pathspec
        for pathspec in M25_PATHSPECS
        if not (project_root / pathspec).exists()
    ]
    return {
        "package_id": M25_PACKAGE_ID,
        "label": "M25 Validation Evidence Gate",
        "depends_on": ["m24-pr-preflight"],
        "pathspec_count": len(M25_PATHSPECS),
        "forced_pathspec_count": 0,
        "ready_for_pathspec_staging": not missing,
    }


def _m25_stage_command() -> str:
    joined = " \\\n  ".join(M25_PATHSPECS)
    return f"git add -- \\\n  {joined}"


def _normalize_results(command_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for result in command_results:
        exit_code = int(result["exit_code"])
        normalized.append(
            {
                "command_id": str(result["command_id"]),
                "package_id": str(result["package_id"]),
                "command": str(result["command"]),
                "status": "pass" if result.get("status") == "pass" and exit_code == 0 else "fail",
                "exit_code": exit_code,
                "duration_seconds": float(result.get("duration_seconds", 0.0)),
                "output_tail": str(result.get("output_tail", "")),
            }
        )
    return normalized


def _summary(
    *,
    preflight_payload: dict[str, Any],
    validation_results: list[dict[str, Any]],
    stage_commands: list[str],
    pathspec_packages: list[dict[str, Any]],
) -> dict[str, Any]:
    passed = sum(1 for result in validation_results if result["status"] == "pass")
    failed = sum(1 for result in validation_results if result["status"] == "fail")
    return {
        "dirty_worktree_policy": preflight_payload["summary"]["dirty_worktree_policy"],
        "executed_command_count": len(validation_results),
        "failed_command_count": failed,
        "package_count": len(pathspec_packages),
        "passed_command_count": passed,
        "stage_command_count": len(stage_commands),
        "validation_command_count": len(preflight_payload["validation_plan"]),
    }


def _status(summary: dict[str, Any], pathspec_packages: list[dict[str, Any]]) -> str:
    all_commands_passed = (
        summary["executed_command_count"] == summary["validation_command_count"]
        and summary["failed_command_count"] == 0
    )
    all_pathspecs_ready = all(package["ready_for_pathspec_staging"] for package in pathspec_packages)
    return "pass" if all_commands_passed and all_pathspecs_ready else "fail"


def build_multi_agent_validation_evidence(
    *,
    project_root: Path,
    command_results: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    """Build M25 evidence by recording the M24 validation plan results."""
    preflight_payload = build_multi_agent_pr_preflight(
        project_root=project_root,
        generated_at=generated_at,
    )
    validation_results = (
        _normalize_results(command_results)
        if command_results is not None
        else execute_validation_plan(
            preflight_payload["validation_plan"],
            project_root=project_root,
            command_runner=command_runner,
        )
    )
    pathspec_packages = preflight_payload["pathspec_packages"] + [
        _m25_package(project_root=project_root)
    ]
    stage_commands = preflight_payload["stage_commands"] + [_m25_stage_command()]
    summary = _summary(
        preflight_payload=preflight_payload,
        validation_results=validation_results,
        stage_commands=stage_commands,
        pathspec_packages=pathspec_packages,
    )
    status = _status(summary, pathspec_packages)
    pr_evidence_note = (
        f"{summary['passed_command_count']} validation commands passed; "
        f"{summary['failed_command_count']} failed. "
        f"`{NOTION_BLOCKER_ID}` remains an external control-plane blocker."
    )
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "evidence_id": EVIDENCE_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M25",
            "name": "Validation Evidence Capture",
            "claim": "read_only_pre_commit_validation_evidence",
        },
        "inputs": {
            "preflight_schema": preflight_payload["$schema"],
            "preflight_status": preflight_payload["status"],
            "preflight_id": preflight_payload["preflight_id"],
        },
        "summary": summary,
        "pathspec_packages": pathspec_packages,
        "validation_plan": preflight_payload["validation_plan"],
        "validation_results": validation_results,
        "stage_commands": stage_commands,
        "excluded_paths": preflight_payload["excluded_paths"],
        "classified_changed_pathspecs": CLASSIFIED_CHANGED_PATHS,
        "blockers": preflight_payload["blockers"],
        "pr_evidence_note": pr_evidence_note,
        "artifact_paths": {
            "evidence_json": "",
            "evidence_markdown": "",
            "evidence_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_validation_evidence_markdown(payload: dict[str, Any]) -> str:
    """Render Markdown validation evidence."""
    packages = "\n".join(
        "- `{package_id}`: {pathspec_count} pathspecs, ready `{ready_for_pathspec_staging}`".format(
            **package
        )
        for package in payload["pathspec_packages"]
    )
    results = "\n".join(
        "- `{command_id}` `{status}` exit `{exit_code}` in `{duration_seconds}`s".format(
            **result
        )
        for result in payload["validation_results"]
    )
    stages = "\n\n".join(f"```sh\n{command}\n```" for command in payload["stage_commands"])
    excluded = "\n".join(f"- `{path}`" for path in payload["excluded_paths"])
    classified = "\n".join(f"- `{path}`" for path in payload["classified_changed_pathspecs"])
    return (
        "# Multi-Agent Validation Evidence\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"{payload['pr_evidence_note']}\n\n"
        "## Packages\n\n"
        f"{packages}\n\n"
        "## Validation Results\n\n"
        f"{results}\n\n"
        "## Stage Commands\n\n"
        f"{stages}\n\n"
        "## Excluded Paths\n\n"
        f"{excluded}\n\n"
        "## Classified Changed Pathspecs\n\n"
        f"{classified}\n\n"
        "## Notion Blocker\n\n"
        f"- `{NOTION_BLOCKER_ID}` remains an external control-plane blocker.\n"
    )


def render_multi_agent_validation_evidence_html(payload: dict[str, Any]) -> str:
    """Render a static validation evidence cockpit page."""
    package_cards = "\n".join(
        "<article class=\"package\">"
        f"<span>{_escape(package['package_id'])}</span>"
        f"<h2>{_escape(package['label'])}</h2>"
        f"<p>Pathspecs: {_escape(package['pathspec_count'])}</p>"
        f"<p>Ready: {_escape(package['ready_for_pathspec_staging'])}</p>"
        "</article>"
        for package in payload["pathspec_packages"]
    )
    result_items = "\n".join(
        "<li>"
        f"<code>{_escape(result['command_id'])}</code>"
        f"<strong>{_escape(result['status'])}</strong>"
        f"<p>Exit { _escape(result['exit_code']) } in { _escape(result['duration_seconds']) }s</p>"
        f"<pre>{_escape(result['output_tail'])}</pre>"
        "</li>"
        for result in payload["validation_results"]
    )
    stage_commands = "\n".join(f"<pre>{_escape(command)}</pre>" for command in payload["stage_commands"])
    classified = "\n".join(
        f"<li><code>{_escape(path)}</code></li>"
        for path in payload["classified_changed_pathspecs"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Validation Evidence</title>
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
    main {{ padding: 24px 32px 36px; }}
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
    section + section {{ margin-top: 16px; }}
    .package span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
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
    li + li {{ margin-top: 10px; }}
    pre {{ margin: 10px 0 0; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 20px 16px; }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Multi-Agent Validation Evidence</h1>
    <p class="subtitle">{_escape(payload['pr_evidence_note'])}</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Status: <strong>{_escape(payload['status'])}</strong></p>
      <p>Passed: <strong>{_escape(payload['summary']['passed_command_count'])}</strong></p>
      <p>Failed: <strong>{_escape(payload['summary']['failed_command_count'])}</strong></p>
      <p>Stage commands: <strong>{_escape(payload['summary']['stage_command_count'])}</strong></p>
    </section>
    <div class="grid">{package_cards}</div>
    <section>
      <h2>Validation Results</h2>
      <ol>{result_items}</ol>
    </section>
    <section>
      <h2>Stage Commands</h2>
      {stage_commands}
    </section>
    <section>
      <h2>Classified Changed Pathspecs</h2>
      <ul>{classified}</ul>
    </section>
    <section>
      <h2>External Blocker</h2>
      <p><code>{NOTION_BLOCKER_ID}</code> remains an external control-plane blocker.</p>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_validation_evidence_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write validation evidence JSON, Markdown, and HTML artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    final_payload = json.loads(json.dumps(payload))
    final_payload["artifact_paths"]["evidence_json"] = str(json_path)
    final_payload["artifact_paths"]["evidence_markdown"] = str(markdown_path)
    final_payload["artifact_paths"]["evidence_html"] = str(html_path)
    markdown_path.write_text(render_multi_agent_validation_evidence_markdown(final_payload), encoding="utf-8")
    html_path.write_text(render_multi_agent_validation_evidence_html(final_payload), encoding="utf-8")
    json_path.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return final_payload

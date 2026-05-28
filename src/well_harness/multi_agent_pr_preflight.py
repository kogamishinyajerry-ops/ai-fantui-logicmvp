"""Read-only PR preflight packet for the multi-agent lane."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from well_harness.multi_agent_packaging_consolidation import (
    build_multi_agent_packaging_consolidation,
)


SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_pr_preflight_v0_1.schema.json"
KIND = "ai-fantui-multi-agent-pr-preflight"
PREFLIGHT_ID = "multi-agent-pr-preflight-v0.1"
JSON_NAME = "multi_agent_pr_preflight_v0_1.json"
MARKDOWN_NAME = "multi_agent_pr_preflight_v0_1.md"
HTML_NAME = "multi_agent_pr_preflight_v0_1.html"
M24_PACKAGE_ID = "m24-pr-preflight"
M24_PATHSPECS = [
    "Makefile",
    "docs/coordination/multi-agent-pr-preflight.md",
    "docs/json_schema/multi_agent_pr_preflight_v0_1.schema.json",
    "scripts/run_multi_agent_pr_preflight.py",
    "scripts/verify_multi_agent_pr_preflight.py",
    "src/well_harness/multi_agent_pr_preflight.py",
    "tests/test_multi_agent_pr_preflight.py",
]
M24_VALIDATION_COMMANDS = [
    "PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_pr_preflight.py",
    "make multi-agent-pr-preflight",
    "make verify-multi-agent-pr-preflight",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validation_plan(packaging_payload: dict[str, Any]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for package in packaging_payload["package_order"]:
        for index, command in enumerate(package["validation_commands"], start=1):
            plan.append(
                {
                    "command_id": f"{package['package_id']}-{index:02d}",
                    "package_id": package["package_id"],
                    "depends_on": package["depends_on"],
                    "command": command,
                    "evidence_required": "exit_code_0_with_fresh_output_before_commit",
                    "execution_mode": "manual_or_operator_run",
                }
            )
    return plan


def _self_package(*, project_root: Path) -> dict[str, Any]:
    missing = [
        pathspec
        for pathspec in M24_PATHSPECS
        if not (project_root / pathspec).exists()
    ]
    return {
        "package_id": M24_PACKAGE_ID,
        "label": "M24 PR Preflight Gate",
        "depends_on": ["m23-packaging-consolidation"],
        "pathspec_count": len(M24_PATHSPECS),
        "forced_pathspec_count": 0,
        "ready_for_pathspec_staging": not missing,
    }


def _pathspec_packages(
    packaging_payload: dict[str, Any],
    *,
    project_root: Path,
) -> list[dict[str, Any]]:
    packages = [
        {
            "package_id": package["package_id"],
            "label": package["label"],
            "depends_on": package["depends_on"],
            "pathspec_count": len(package["pathspecs"]),
            "forced_pathspec_count": len(package["forced_pathspecs"]),
            "ready_for_pathspec_staging": package["ready_for_pathspec_staging"],
        }
        for package in packaging_payload["package_order"]
    ]
    packages.append(_self_package(project_root=project_root))
    return packages


def _self_validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "command_id": f"{M24_PACKAGE_ID}-{index:02d}",
            "package_id": M24_PACKAGE_ID,
            "depends_on": ["m23-packaging-consolidation"],
            "command": command,
            "evidence_required": "exit_code_0_with_fresh_output_before_commit",
            "execution_mode": "manual_or_operator_run",
        }
        for index, command in enumerate(M24_VALIDATION_COMMANDS, start=1)
    ]


def _self_stage_command() -> str:
    joined = " \\\n  ".join(M24_PATHSPECS)
    return f"git add -- \\\n  {joined}"


def _build_pr_body(
    *,
    stage_commands: list[str],
    validation_plan: list[dict[str, Any]],
) -> str:
    validation_lines = "\n".join(
        f"- [ ] `{item['command']}`"
        for item in validation_plan
    )
    stage_lines = "\n\n".join(f"```sh\n{command}\n```" for command in stage_commands)
    return (
        "## Summary\n"
        "- Add the read-only UltraWork Monitor and M22 multi-agent operator cockpit artifacts.\n"
        "- Add the M23 explicit pathspec packaging boundary and M24 PR preflight packet.\n"
        "- Preserve controller truth and requirements-intake surfaces outside this PR boundary.\n\n"
        "## Validation\n"
        "Run these commands in package order before commit/PR update:\n\n"
        f"{validation_lines}\n\n"
        "## Control-plane boundary\n"
        "- Repo, GitHub, and local artifacts are the active control surfaces for this PR.\n"
        "- No external planning surface is required for merge readiness in this lane.\n\n"
        "## Pathspec packaging boundary\n"
        "Stage only these generated package groups, in order:\n\n"
        f"{stage_lines}\n\n"
        "## Browser / geometry gate\n"
        "- Open the generated HTML artifacts for M22, M23, and M24.\n"
        "- Capture desktop and mobile screenshots and confirm required labels render without horizontal overflow.\n\n"
        "## Risks\n"
        "- The worktree contains unrelated dirty files; use the explicit pathspec commands only.\n"
        "- Ignored `.claude/agents/*` files require the generated `git add -f --` command.\n"
        "- Keep `make verify-multi-agent-packaging-consolidation` and `make verify-multi-agent-pr-preflight` evidence in the PR body."
    )


def build_multi_agent_pr_preflight(
    *,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the read-only M24 validation and PR body preflight packet."""
    packaging_payload = build_multi_agent_packaging_consolidation(
        project_root=project_root,
        generated_at=generated_at,
    )
    validation_plan = _validation_plan(packaging_payload) + _self_validation_plan()
    pathspec_packages = _pathspec_packages(packaging_payload, project_root=project_root)
    stage_commands = packaging_payload["stage_commands"] + [_self_stage_command()]
    status = (
        "pass"
        if packaging_payload["status"] == "pass"
        and all(package["ready_for_pathspec_staging"] for package in pathspec_packages)
        else "fail"
    )
    return {
        "$schema": SCHEMA_ID,
        "kind": KIND,
        "preflight_id": PREFLIGHT_ID,
        "status": status,
        "generated_at": generated_at or _utc_now(),
        "milestone": {
            "id": "M24",
            "name": "PR Preflight",
            "claim": "read_only_validation_and_pr_body_preparation",
        },
        "summary": {
            "package_count": len(pathspec_packages),
            "validation_command_count": len(validation_plan),
            "stage_command_count": len(stage_commands),
            "next_action": "run_validations_then_stage_with_explicit_pathspecs",
            "dirty_worktree_policy": packaging_payload["summary"]["dirty_worktree_policy"],
        },
        "inputs": {
            "packaging_schema": packaging_payload["$schema"],
            "packaging_status": packaging_payload["status"],
            "packaging_package_id": packaging_payload["package_id"],
        },
        "pathspec_packages": pathspec_packages,
        "validation_plan": validation_plan,
        "stage_commands": stage_commands,
        "browser_geometry_gate": {
            "target_artifact": HTML_NAME,
            "required_markers": [
                "Multi-Agent PR Preflight",
                "multi-agent-cursor-baseline-v0-2",
                "ultrawork-monitor",
                "m23-packaging-consolidation",
                "repo-github-local-artifacts",
                "git add -f --",
            ],
            "viewports": [
                {"name": "desktop", "width": 1440, "height": 1000},
                {"name": "mobile", "width": 390, "height": 900},
            ],
        },
        "excluded_paths": packaging_payload["excluded_paths"],
        "blockers": packaging_payload["blockers"],
        "pr_body": {
            "title": packaging_payload["pr_summary"]["title"],
            "body": _build_pr_body(
                stage_commands=stage_commands,
                validation_plan=validation_plan,
            ),
            "control_plane_note": packaging_payload["pr_summary"]["control_plane_note"],
        },
        "artifact_paths": {
            "preflight_json": "",
            "preflight_markdown": "",
            "preflight_html": "",
        },
    }


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_multi_agent_pr_preflight_markdown(payload: dict[str, Any]) -> str:
    """Render a Markdown PR preflight packet."""
    packages = "\n".join(
        "- `{package_id}`: {pathspec_count} pathspecs, {forced_pathspec_count} forced".format(
            **package
        )
        for package in payload["pathspec_packages"]
    )
    validations = "\n".join(
        f"- `{item['command_id']}`: `{item['command']}`"
        for item in payload["validation_plan"]
    )
    stages = "\n\n".join(f"```sh\n{command}\n```" for command in payload["stage_commands"])
    excluded = "\n".join(f"- `{path}`" for path in payload["excluded_paths"])
    return (
        "# Multi-Agent PR Preflight\n\n"
        f"Status: `{payload['status']}`\n\n"
        "## Packages\n\n"
        f"{packages}\n\n"
        f"## Validation Plan\n\n"
        f"{payload['summary']['validation_command_count']} validation commands are required before commit.\n\n"
        f"{validations}\n\n"
        "## Stage Commands\n\n"
        f"{stages}\n\n"
        "## Excluded Paths\n\n"
        f"{excluded}\n\n"
        "## Control-Plane Boundary\n\n"
        "- Repo, GitHub, and local artifacts are the active control surfaces.\n\n"
        "## PR Body\n\n"
        f"{payload['pr_body']['body']}\n"
    )


def render_multi_agent_pr_preflight_html(payload: dict[str, Any]) -> str:
    """Render a static PR preflight cockpit page."""
    package_cards = "\n".join(
        "<article class=\"package\">"
        f"<span>{_escape(package['package_id'])}</span>"
        f"<h2>{_escape(package['label'])}</h2>"
        f"<p>Pathspecs: {_escape(package['pathspec_count'])}</p>"
        f"<p>Forced: {_escape(package['forced_pathspec_count'])}</p>"
        f"<p>Ready: {_escape(package['ready_for_pathspec_staging'])}</p>"
        "</article>"
        for package in payload["pathspec_packages"]
    )
    validation_items = "\n".join(
        "<li>"
        f"<code>{_escape(item['command_id'])}</code>"
        f"<pre>{_escape(item['command'])}</pre>"
        "</li>"
        for item in payload["validation_plan"]
    )
    stage_commands = "\n".join(f"<pre>{_escape(command)}</pre>" for command in payload["stage_commands"])
    gate_markers = "\n".join(
        f"<li><code>{_escape(marker)}</code></li>"
        for marker in payload["browser_geometry_gate"]["required_markers"]
    )
    pr_body = _escape(payload["pr_body"]["body"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent PR Preflight</title>
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
    li + li {{ margin-top: 10px; }}
    @media (max-width: 720px) {{
      header, main {{ padding: 20px 16px; }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Multi-Agent PR Preflight</h1>
    <p class="subtitle">Prepare validation evidence, stage commands, and PR body text before pathspec staging.</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <p>Status: <strong>{_escape(payload['status'])}</strong></p>
      <p>Packages: <strong>{_escape(payload['summary']['package_count'])}</strong></p>
      <p>Validation commands: <strong>{_escape(payload['summary']['validation_command_count'])}</strong></p>
      <p>Stage commands: <strong>{_escape(payload['summary']['stage_command_count'])}</strong></p>
    </section>
    <div class="grid">{package_cards}</div>
    <section>
      <h2>Validation Plan</h2>
      <ol>{validation_items}</ol>
    </section>
    <section>
      <h2>Stage Commands</h2>
      {stage_commands}
    </section>
    <section>
      <h2>Browser Geometry Gate</h2>
      <ul>{gate_markers}</ul>
    </section>
    <section>
      <h2>Control-Plane Boundary</h2>
      <p><code>repo-github-local-artifacts</code> is the active control boundary for this PR.</p>
    </section>
    <section>
      <h2>PR Body</h2>
      <pre>{pr_body}</pre>
    </section>
  </main>
</body>
</html>
"""


def write_multi_agent_pr_preflight_artifacts(
    payload: dict[str, Any],
    *,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Write PR preflight JSON, Markdown, and HTML artifacts."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / JSON_NAME
    markdown_path = artifact_dir / MARKDOWN_NAME
    html_path = artifact_dir / HTML_NAME
    final_payload = json.loads(json.dumps(payload))
    final_payload["artifact_paths"]["preflight_json"] = str(json_path)
    final_payload["artifact_paths"]["preflight_markdown"] = str(markdown_path)
    final_payload["artifact_paths"]["preflight_html"] = str(html_path)
    markdown_path.write_text(render_multi_agent_pr_preflight_markdown(final_payload), encoding="utf-8")
    html_path.write_text(render_multi_agent_pr_preflight_html(final_payload), encoding="utf-8")
    json_path.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return final_payload

"""Run GSD validation commands and mirror outcomes into the Notion control plane.

This script intentionally uses only the Python standard library so it can run
locally and in GitHub Actions without adding runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NOTION_VERSION = "2022-06-28"
DEFAULT_CONFIG_PATH = Path(".planning/notion_control_plane.json")
TEXT_LIMIT = 1800
DEFAULT_DATABASES = {
    "roadmap": "33cc6894-2bed-810a-a2ea-e4f095b44afa",
    "tasks": "33cc6894-2bed-81ea-bb1b-ef1bc904f407",
    "sessions": "33cc6894-2bed-8185-9e43-cb92dde87037",
    "qa": "33cc6894-2bed-81d4-8346-eed39942af18",
    "plans": "33cc6894-2bed-81f0-a918-e48f51a29f98",
    "runs": "33cc6894-2bed-8167-9618-fdcbb8849827",
    "gates": "33cc6894-2bed-812f-82fb-fbee3563adae",
    "gaps": "33cc6894-2bed-8155-8c86-c4f58295502e",
}
DATABASE_ENV = {
    "qa": "NOTION_GSD_QA_DATABASE_ID",
    "plans": "NOTION_GSD_PLAN_DATABASE_ID",
    "runs": "NOTION_GSD_RUN_DATABASE_ID",
    "gates": "NOTION_GSD_GATE_DATABASE_ID",
    "gaps": "NOTION_GSD_GAP_DATABASE_ID",
}
TITLE_PROPS = {
    "qa": "Run",
    "plans": "Plan",
    "runs": "Run",
    "gates": "Gate",
    "gaps": "Gap",
}


@dataclass(frozen=True)
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    ended_at: str


@dataclass(frozen=True)
class RunSummary:
    succeeded: bool
    status: str
    qa_result: str
    first_failed_command: str | None
    command_count: int
    output_digest: str


class NotionClient:
    def __init__(self, token: str):
        self.token = token

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            "https://api.notion.com" + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            raise RuntimeError(f"Notion API request failed: HTTP {error.code} {path}: {detail}") from error

    def upsert_page(
        self,
        database_id: str,
        title_prop: str,
        title: str,
        properties: dict[str, Any],
    ) -> str:
        existing = self.request(
            "POST",
            f"/v1/databases/{database_id}/query",
            {"filter": {"property": title_prop, "title": {"equals": title}}, "page_size": 1},
        ).get("results", [])
        page_properties = {title_prop: title_value(title), **properties}
        if existing:
            page_id = existing[0]["id"]
            self.request("PATCH", f"/v1/pages/{page_id}", {"properties": page_properties})
            return page_id
        page = self.request(
            "POST",
            "/v1/pages",
            {"parent": {"database_id": database_id}, "properties": page_properties},
        )
        return page["id"]


def rich_text(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": clip(text)}}] if text else []


def rich_text_value(text: str) -> dict[str, Any]:
    return {"rich_text": rich_text(text)}


def title_value(text: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": clip(text)}}]}


def select_value(name: str) -> dict[str, Any]:
    return {"select": {"name": name}}


def checkbox_value(value: bool) -> dict[str, Any]:
    return {"checkbox": value}


def date_value(value: str) -> dict[str, Any]:
    return {"date": {"start": value}}


def multi_select_value(names: list[str]) -> dict[str, Any]:
    return {"multi_select": [{"name": name} for name in names]}


def clip(text: str, limit: int = TEXT_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n...<truncated>"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_control_plane_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "databases": dict(DEFAULT_DATABASES),
            "default_plan": "P1-01 建立自动执行 / QA 回写闭环",
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
        }
    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    config.setdefault("databases", {})
    for key, value in DEFAULT_DATABASES.items():
        config["databases"].setdefault(key, value)
    config.setdefault("default_plan", "P1-01 建立自动执行 / QA 回写闭环")
    config.setdefault("default_review_gate", "OPUS-4.6 周期审查 Gate")
    return config


def database_id(config: dict[str, Any], key: str) -> str:
    env_name = DATABASE_ENV.get(key)
    if env_name and os.environ.get(env_name):
        return os.environ[env_name]
    return config["databases"][key]


def run_commands(commands: list[str], cwd: Path) -> list[CommandResult]:
    results: list[CommandResult] = []
    env = dict(os.environ)
    src_path = str(cwd / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
    for command in commands:
        started_at = utc_now()
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        ended_at = utc_now()
        results.append(
            CommandResult(
                command=command,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                started_at=started_at,
                ended_at=ended_at,
            )
        )
        if completed.returncode != 0:
            break
    return results


def summarize_results(results: list[CommandResult]) -> RunSummary:
    succeeded = all(result.returncode == 0 for result in results)
    first_failed = next((result.command for result in results if result.returncode != 0), None)
    digest_parts = []
    for result in results:
        digest_parts.append(f"$ {result.command}")
        digest_parts.append(f"exit={result.returncode}")
        if result.stdout.strip():
            digest_parts.append("stdout:\n" + result.stdout.strip())
        if result.stderr.strip():
            digest_parts.append("stderr:\n" + result.stderr.strip())
    return RunSummary(
        succeeded=succeeded,
        status="Succeeded" if succeeded else "Failed",
        qa_result="PASS" if succeeded else "FAIL",
        first_failed_command=first_failed,
        command_count=len(results),
        output_digest=clip("\n\n".join(digest_parts)),
    )


def command_list_text(commands: list[str]) -> str:
    return "\n".join(f"- {command}" for command in commands)


def write_notion_outcome(
    client: NotionClient,
    config: dict[str, Any],
    *,
    title: str,
    plan_id: str,
    commands: list[str],
    results: list[CommandResult],
    summary: RunSummary,
    opus_gate: bool,
) -> dict[str, str]:
    started_at = results[0].started_at if results else utc_now()
    ended_at = results[-1].ended_at if results else utc_now()
    written: dict[str, str] = {}

    written["plan"] = client.upsert_page(
        database_id(config, "plans"),
        TITLE_PROPS["plans"],
        plan_id,
        {
            "Status": select_value("Verified" if summary.succeeded else "Blocked"),
            "Autonomous": checkbox_value(True),
            "Summary": rich_text_value(
                f"{summary.status}. Commands: {summary.command_count}. First failure: {summary.first_failed_command or 'none'}"
            ),
            "Next Command": rich_text_value(
                "Continue automatic loop" if summary.succeeded else "Create fix plan from UAT Gap"
            ),
        },
    )
    written["run"] = client.upsert_page(
        database_id(config, "runs"),
        TITLE_PROPS["runs"],
        title,
        {
            "Plan ID": rich_text_value(plan_id),
            "Status": select_value(summary.status),
            "Executor": select_value("GitHub Action" if os.environ.get("GITHUB_ACTIONS") else "Codex"),
            "Started At": date_value(started_at),
            "Ended At": date_value(ended_at),
            "Artifacts": rich_text_value(os.environ.get("GITHUB_SERVER_URL", "")),
            "Notes": rich_text_value(summary.output_digest),
        },
    )
    written["qa"] = client.upsert_page(
        database_id(config, "qa"),
        TITLE_PROPS["qa"],
        f"{title} QA",
        {
            "Scope": multi_select_value(["Automation", "GSD"]),
            "Commands": rich_text_value(command_list_text(commands)),
            "Result": select_value(summary.qa_result),
            "Date": date_value(ended_at),
            "Summary": rich_text_value(summary.output_digest),
            "Blocking Issues": rich_text_value(summary.first_failed_command or ""),
        },
    )

    if not summary.succeeded:
        written["gap"] = client.upsert_page(
            database_id(config, "gaps"),
            TITLE_PROPS["gaps"],
            f"Automation failure: {plan_id}",
            {
                "Severity": select_value("major"),
                "Status": select_value("Open"),
                "Truth": rich_text_value("GSD automation commands should pass before the phase advances."),
                "Reason": rich_text_value(summary.output_digest),
                "Source Test": rich_text_value(summary.first_failed_command or "unknown"),
                "Fix Plan": rich_text_value("Generate a follow-up fix plan, then rerun tools/gsd_notion_sync.py."),
            },
        )

    if opus_gate:
        written["gate"] = client.upsert_page(
            database_id(config, "gates"),
            TITLE_PROPS["gates"],
            config["default_review_gate"],
            {
                "Scope": select_value("Phase"),
                "Trigger": select_value("After Execution"),
                "Status": select_value("Awaiting Opus 4.6"),
                "Reviewer": select_value("Opus 4.6"),
                "What To Review": rich_text_value(
                    f"Review automation run `{title}` for plan `{plan_id}` after machine checks completed."
                ),
                "Decision Notes": rich_text_value(""),
                "Next Action": rich_text_value("Manually trigger Opus 4.6 and write back Approved or Changes Requested."),
            },
        )

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GSD commands and sync status to Notion.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the Notion control-plane config JSON.",
    )
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    run_parser = subparsers.add_parser("run", help="Run validation commands and write the outcome to Notion.")
    run_parser.add_argument("--plan-id", help="GSD plan title to update in Notion.")
    run_parser.add_argument("--title", help="Execution run title.")
    run_parser.add_argument(
        "--command",
        action="append",
        required=True,
        help="Shell command to run. Repeat this flag to run multiple commands in order.",
    )
    run_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory for commands. Defaults to the current directory.",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run commands and print the computed outcome without writing to Notion.",
    )
    run_parser.add_argument(
        "--opus-gate",
        action="store_true",
        help="After writing the run, move the default review gate to Awaiting Opus 4.6.",
    )
    run_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser


def output_result(format_name: str, payload: dict[str, Any]) -> None:
    if format_name == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"GSD automation run: {payload['status']}")
    print(f"Commands: {payload['command_count']}")
    if payload.get("first_failed_command"):
        print(f"First failed command: {payload['first_failed_command']}")
    if payload.get("notion") == "skipped":
        print("Notion writeback: skipped")
    elif payload.get("notion") == "written":
        print("Notion writeback: written")


def handle_run(args: argparse.Namespace, config: dict[str, Any]) -> int:
    cwd = Path(args.cwd).resolve()
    plan_id = args.plan_id or config["default_plan"]
    title = args.title or f"{plan_id} automation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    results = run_commands(args.command, cwd)
    summary = summarize_results(results)
    payload: dict[str, Any] = {
        "title": title,
        "plan_id": plan_id,
        "status": summary.status,
        "qa_result": summary.qa_result,
        "command_count": summary.command_count,
        "first_failed_command": summary.first_failed_command,
        "notion": "skipped",
    }

    token = os.environ.get("NOTION_API_KEY")
    if not args.dry_run and token:
        written = write_notion_outcome(
            NotionClient(token),
            config,
            title=title,
            plan_id=plan_id,
            commands=args.command,
            results=results,
            summary=summary,
            opus_gate=args.opus_gate,
        )
        payload["notion"] = "written"
        payload["notion_pages"] = written
    output_result(args.format, payload)
    return 0 if summary.succeeded else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_control_plane_config(Path(args.config))
    if args.command_name == "run":
        return handle_run(args, config)
    parser.error(f"Unsupported command: {args.command_name}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

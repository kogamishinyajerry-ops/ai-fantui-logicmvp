"""Run GSD validation commands and mirror outcomes into the Notion control plane.

This script intentionally uses only the Python standard library so it can run
locally and in GitHub Actions without adding runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NOTION_VERSION = "2022-06-28"
DEFAULT_CONFIG_PATH = Path(".planning/notion_control_plane.json")
TEXT_LIMIT = 1800
DASHBOARD_SYNC_MARKER = "AUTO-SYNCED DASHBOARD SNAPSHOT"
DEFAULT_DATABASES = {
    "roadmap": "33cc6894-2bed-810a-a2ea-e4f095b44afa",
    "tasks": "33cc6894-2bed-81ea-bb1b-ef1bc904f407",
    "sessions": "33cc6894-2bed-8185-9e43-cb92dde87037",
    "qa": "33cc6894-2bed-81d4-8346-eed39942af18",
    "plans": "33cc6894-2bed-81f0-a918-e48f51a29f98",
    "runs": "33cc6894-2bed-8167-9618-fdcbb8849827",
    "gates": "33cc6894-2bed-812f-82fb-fbee3563adae",
    "gaps": "33cc6894-2bed-8155-8c86-c4f58295502e",
    "decisions": "33cc6894-2bed-8116-82de-e0f63f9f5f59",
    "assets": "33cc6894-2bed-818b-920a-fd13f828d23e",
}
DEFAULT_PAGES = {
    "dashboard": "33cc6894-2bed-8136-b5c9-f9ba5b4b44ec",
    "constitution": "33cc6894-2bed-8148-b2c5-ec68c440f5ef",
    "status": "33cc6894-2bed-8105-ae6a-d880cb399b73",
    "control_plane": "33cc6894-2bed-810d-875e-e4e0e464ee31",
    "opus_protocol": "33cc6894-2bed-8117-b8f5-eda203f3be18",
    "opus_brief": "33cc6894-2bed-819a-811c-f19885ee595a",
    "freeze_packet": "33ec6894-2bed-8151-a0a8-ff9a36aa8816",
}
DEFAULT_URLS = {
    "github_repo": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp",
    "github_actions": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions",
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


@dataclass(frozen=True)
class ReviewSnapshot:
    active_phase: str
    active_phase_goal: str
    active_phase_summary: str
    latest_verified_plan: str
    latest_success_run: str | None
    latest_failed_run: str | None
    latest_passing_qa: str | None
    gate_page_id: str | None
    gate_name: str
    gate_status: str
    ready_task_id: str | None
    ready_task: str | None
    open_gap_titles: tuple[str, ...]
    stale_gap_titles: tuple[str, ...]


@dataclass(frozen=True)
class CurrentReviewBrief:
    page_title: str
    review_required: bool
    intervention_kind: str
    review_target: str
    why_now: str
    gate_direction: str
    facts: tuple[str, ...]
    questions: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    writeback_steps: tuple[str, ...]
    copy_prompt: str


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

    def query_database(
        self,
        database_id: str,
        *,
        filter_payload: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"page_size": page_size}
        if filter_payload:
            payload["filter"] = filter_payload
        if sorts:
            payload["sorts"] = sorts
        return self.request("POST", f"/v1/databases/{database_id}/query", payload).get("results", [])

    def upsert_page(
        self,
        database_id: str,
        title_prop: str,
        title: str,
        properties: dict[str, Any],
    ) -> str:
        existing = self.query_database(
            database_id,
            filter_payload={"property": title_prop, "title": {"equals": title}},
            page_size=1,
        )
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

    def update_page_properties(self, page_id: str, properties: dict[str, Any]) -> None:
        self.request("PATCH", f"/v1/pages/{page_id}", {"properties": properties})

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/pages/{page_id}")

    def archive_page(self, page_id: str) -> None:
        self.request("PATCH", f"/v1/pages/{page_id}", {"archived": True})

    def list_block_children(self, block_id: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            path = f"/v1/blocks/{block_id}/children?page_size=100"
            if cursor:
                path += f"&start_cursor={cursor}"
            data = self.request("GET", path)
            items.extend(data.get("results", []))
            if not data.get("has_more"):
                return items
            cursor = data.get("next_cursor")

    def replace_page_body(self, page_id: str, blocks: list[dict[str, Any]]) -> None:
        for block in self.list_block_children(page_id):
            if block.get("archived") or block.get("in_trash"):
                continue
            self.request("DELETE", f"/v1/blocks/{block['id']}")
        if blocks:
            self.request(
                "PATCH",
                f"/v1/blocks/{page_id}/children",
                {"children": blocks, "position": {"type": "start"}},
            )


def notion_text(text: str, url: str | None = None) -> dict[str, Any]:
    text_obj: dict[str, Any] = {"content": clip(text)}
    if url:
        text_obj["link"] = {"url": url}
    return {"type": "text", "text": text_obj}


def rich_text(text: str) -> list[dict[str, Any]]:
    return [notion_text(text)] if text else []


def rich_text_value(text: str) -> dict[str, Any]:
    return {"rich_text": rich_text(text)}


def title_value(text: str) -> dict[str, Any]:
    return {"title": [notion_text(text)]}


def select_value(name: str) -> dict[str, Any]:
    return {"select": {"name": name}}


def checkbox_value(value: bool) -> dict[str, Any]:
    return {"checkbox": value}


def date_value(value: str) -> dict[str, Any]:
    return {"date": {"start": value}}


def multi_select_value(names: list[str]) -> dict[str, Any]:
    return {"multi_select": [{"name": name} for name in names]}


def paragraph_block(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(text)}}


def paragraph_parts_block(parts: list[dict[str, Any]]) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": parts}}


def callout_block(text: str, emoji: str = "🧠") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {"icon": {"type": "emoji", "emoji": emoji}, "rich_text": rich_text(text)},
    }


def heading_block(text: str) -> dict[str, Any]:
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich_text(text)}}


def bullet_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text)},
    }


def number_block(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": rich_text(text)},
    }


def divider_block() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def page_link_block(page_id_value: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "link_to_page",
        "link_to_page": {"type": "page_id", "page_id": page_id_value},
    }


def database_link_block(database_id_value: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "link_to_page",
        "link_to_page": {"type": "database_id", "database_id": database_id_value},
    }


def clip(text: str, limit: int = TEXT_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n...<truncated>"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def block_plain_text(block: dict[str, Any]) -> str:
    block_type = block.get("type")
    if not block_type:
        return ""
    payload = block.get(block_type, {})
    if not isinstance(payload, dict):
        return ""
    rich = payload.get("rich_text", [])
    if not isinstance(rich, list):
        return ""
    return "".join(item.get("plain_text", "") for item in rich)


def load_control_plane_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "databases": dict(DEFAULT_DATABASES),
            "pages": dict(DEFAULT_PAGES),
            "urls": dict(DEFAULT_URLS),
            "default_plan": "P1-01 建立自动执行 / QA 回写闭环",
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
            "legacy_review_artifacts": [],
        }
    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    config.setdefault("databases", {})
    for key, value in DEFAULT_DATABASES.items():
        config["databases"].setdefault(key, value)
    config.setdefault("pages", {})
    for key, value in DEFAULT_PAGES.items():
        config["pages"].setdefault(key, value)
    config.setdefault("urls", {})
    for key, value in DEFAULT_URLS.items():
        config["urls"].setdefault(key, value)
    config.setdefault("default_plan", "P1-01 建立自动执行 / QA 回写闭环")
    config.setdefault("default_review_gate", "OPUS-4.6 周期审查 Gate")
    config.setdefault("legacy_review_artifacts", [])
    return config


def database_id(config: dict[str, Any], key: str) -> str:
    env_name = DATABASE_ENV.get(key)
    if env_name and os.environ.get(env_name):
        return os.environ[env_name]
    return config["databases"][key]


def page_id(config: dict[str, Any], key: str) -> str:
    return config["pages"][key]


def config_url(config: dict[str, Any], key: str) -> str:
    return config["urls"][key]


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


def property_plain_value(prop: dict[str, Any] | None) -> Any:
    if not prop:
        return None
    prop_type = prop.get("type")
    if prop_type == "title":
        return "".join(item.get("plain_text", "") for item in prop["title"])
    if prop_type == "rich_text":
        return "".join(item.get("plain_text", "") for item in prop["rich_text"])
    if prop_type == "select":
        return prop["select"]["name"] if prop["select"] else None
    if prop_type == "status":
        return prop["status"]["name"] if prop["status"] else None
    if prop_type == "multi_select":
        return [item["name"] for item in prop["multi_select"]]
    if prop_type == "checkbox":
        return prop["checkbox"]
    if prop_type == "date":
        return prop["date"]["start"] if prop["date"] else None
    if prop_type == "url":
        return prop["url"]
    if prop_type == "number":
        return prop["number"]
    return None


def row_text(row: dict[str, Any] | None, property_name: str) -> str:
    if not row:
        return ""
    value = property_plain_value(row["properties"].get(property_name))
    return value if isinstance(value, str) else ""


def first_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[0] if rows else None


def build_superseded_gap_fix_plan(success_run_title: str, duplicate: bool = False) -> str:
    note = f"Superseded by successful run {success_run_title}."
    if duplicate:
        note += " Duplicate of sibling gap record."
    return note


def should_retire_legacy_review_artifacts(snapshot: ReviewSnapshot, brief: CurrentReviewBrief) -> bool:
    return snapshot.gate_status == "Approved" and not brief.review_required and not snapshot.open_gap_titles


def retire_legacy_review_artifacts(
    client: Any,
    config: dict[str, Any],
    *,
    snapshot: ReviewSnapshot,
    brief: CurrentReviewBrief,
) -> list[str]:
    if not should_retire_legacy_review_artifacts(snapshot, brief):
        return []

    retired_ids: list[str] = []
    for artifact in config.get("legacy_review_artifacts", []):
        page_id_value = artifact.get("id")
        if not page_id_value:
            continue
        page = client.get_page(page_id_value)
        if page.get("archived") or page.get("in_trash"):
            continue
        client.archive_page(page_id_value)
        retired_ids.append(page_id_value)
    return retired_ids


def resolve_superseded_failure_gaps(
    client: Any,
    config: dict[str, Any],
    *,
    plan_id: str,
    success_run_title: str,
) -> list[str]:
    rows = client.query_database(
        database_id(config, "gaps"),
        filter_payload={"property": TITLE_PROPS["gaps"], "title": {"equals": f"Automation failure: {plan_id}"}},
        page_size=20,
    )
    open_rows = [row for row in rows if row_text(row, "Status") != "Resolved"]
    resolved_ids: list[str] = []
    for index, row in enumerate(open_rows):
        client.update_page_properties(
            row["id"],
            {
                "Status": select_value("Resolved"),
                "Fix Plan": rich_text_value(build_superseded_gap_fix_plan(success_run_title, duplicate=index > 0)),
            },
        )
        resolved_ids.append(row["id"])
    return resolved_ids


def fetch_review_snapshot(client: NotionClient, config: dict[str, Any]) -> ReviewSnapshot:
    github_success_run_row = first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={
                "and": [
                    {"property": "Status", "select": {"equals": "Succeeded"}},
                    {"property": "Executor", "select": {"equals": "GitHub Action"}},
                ]
            },
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    github_failed_run_row = first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={
                "and": [
                    {"property": "Status", "select": {"equals": "Failed"}},
                    {"property": "Executor", "select": {"equals": "GitHub Action"}},
                ]
            },
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    active_phase_row = first_row(
        client.query_database(
            database_id(config, "roadmap"),
            filter_payload={"property": "Status", "select": {"equals": "Active"}},
            page_size=1,
        )
    )
    verified_plan_row = first_row(
        client.query_database(
            database_id(config, "plans"),
            filter_payload={"property": "Status", "select": {"equals": "Verified"}},
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    success_run_row = github_success_run_row or first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={"property": "Status", "select": {"equals": "Succeeded"}},
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    failed_run_row = github_failed_run_row or first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={"property": "Status", "select": {"equals": "Failed"}},
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    passing_qa_row = None
    if success_run_row and row_text(success_run_row, "Run"):
        passing_qa_row = first_row(
            client.query_database(
                database_id(config, "qa"),
                filter_payload={"property": TITLE_PROPS["qa"], "title": {"equals": f"{row_text(success_run_row, 'Run')} QA"}},
                page_size=1,
            )
        )
    if not passing_qa_row:
        passing_qa_row = first_row(
            client.query_database(
                database_id(config, "qa"),
                filter_payload={
                    "and": [
                        {"property": "Result", "select": {"equals": "PASS"}},
                        {"property": TITLE_PROPS["qa"], "title": {"contains": "GitHub GSD automation"}},
                    ]
                },
                sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
                page_size=1,
            )
        )
    if not passing_qa_row:
        passing_qa_row = first_row(
            client.query_database(
                database_id(config, "qa"),
                filter_payload={"property": "Result", "select": {"equals": "PASS"}},
                sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
                page_size=1,
            )
        )
    gate_rows = client.query_database(
        database_id(config, "gates"),
        filter_payload={"property": TITLE_PROPS["gates"], "title": {"equals": config["default_review_gate"]}},
        page_size=1,
    )
    gate_row = gate_rows[0] if gate_rows else first_row(
        client.query_database(
            database_id(config, "gates"),
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    ready_task_row = first_row(
        client.query_database(
            database_id(config, "tasks"),
            filter_payload={
                "and": [
                    {"property": "Status", "select": {"equals": "Ready"}},
                    {"property": "Gate Needed", "select": {"equals": "Opus 4.6"}},
                ]
            },
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    open_gap_rows = client.query_database(
        database_id(config, "gaps"),
        filter_payload={"property": "Status", "select": {"does_not_equal": "Resolved"}},
        sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
        page_size=20,
    )

    active_phase = row_text(active_phase_row, "Round") or "未识别活动 phase"
    latest_verified_plan = row_text(verified_plan_row, "Plan") or config["default_plan"]
    open_gap_titles = tuple(row_text(row, "Gap") for row in open_gap_rows if row_text(row, "Gap"))
    stale_gap_titles = tuple(
        title
        for title in open_gap_titles
        if latest_verified_plan and title == f"Automation failure: {latest_verified_plan}"
    )
    if not success_run_row:
        stale_gap_titles = ()

    return ReviewSnapshot(
        active_phase=active_phase,
        active_phase_goal=row_text(active_phase_row, "Goal"),
        active_phase_summary=row_text(active_phase_row, "Summary"),
        latest_verified_plan=latest_verified_plan,
        latest_success_run=row_text(success_run_row, "Run") or None,
        latest_failed_run=row_text(failed_run_row, "Run") or None,
        latest_passing_qa=row_text(passing_qa_row, "Run") or None,
        gate_page_id=gate_row["id"] if gate_row else None,
        gate_name=row_text(gate_row, "Gate") or config["default_review_gate"],
        gate_status=row_text(gate_row, "Status") or "Standby",
        ready_task_id=ready_task_row["id"] if ready_task_row else None,
        ready_task=row_text(ready_task_row, "Task") or None,
        open_gap_titles=open_gap_titles,
        stale_gap_titles=stale_gap_titles,
    )


def build_current_review_brief(
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    force_review: bool = False,
) -> CurrentReviewBrief:
    review_target = f"{snapshot.active_phase} / {snapshot.latest_verified_plan}"
    repo_url = config_url(config, "github_repo")
    actions_url = config_url(config, "github_actions")
    open_gap_count = len(snapshot.open_gap_titles)
    stale_gap_count = len(snapshot.stale_gap_titles)

    facts = [
        f"活动 phase：{snapshot.active_phase}",
        f"当前已验证 plan：{snapshot.latest_verified_plan}",
    ]
    if snapshot.latest_success_run:
        facts.append(f"最近成功执行证据：{snapshot.latest_success_run}")
    if snapshot.latest_failed_run:
        facts.append(f"最近失败历史证据：{snapshot.latest_failed_run}")
    if snapshot.ready_task:
        facts.append(f"当前人工任务：{snapshot.ready_task}")
    facts.append(f"当前 Gate 状态：{snapshot.gate_status}")

    if not force_review and open_gap_count == 0 and snapshot.gate_status != "Awaiting Opus 4.6" and not snapshot.ready_task:
        intervention_kind = "当前无需 Opus 审查"
        why_now = (
            "当前没有 open gap，默认 Review Gate 也不在 Awaiting Opus 4.6，且没有挂着等待人工触发的 Opus 任务。"
            "现在最正确的动作是继续自动开发，而不是为了例行检查去手动拉起一次主观审查。"
        )
        gate_direction = "保持当前 gate 状态不变；只有出现新的 blocker、Awaiting gate 或明确主观裁决需求时，才刷新 09C 并触发 Opus 4.6。"
        questions = (
            "当前是否真的存在新的 open gap、Awaiting gate，或必须依赖主观判断才能继续推进的问题？",
            "如果没有，是否应该继续自动开发并等待下一次真实触发条件，而不是重复发起审查？",
        )
        out_of_scope = (
            "不要为了“例行看一眼”而触发 Opus 4.6。",
            "不要重开已经 Approved 或 Standby 的 gate。",
            "不要引用本地终端文件或未同步到 GitHub 的信息。",
        )
        writeback_steps = (
            "保持 Review Gate 当前状态，不要覆盖既有裁决。",
            "继续自动开发，并等待新的 blocker / open gap / Awaiting gate 出现。",
            "只有在真的需要主观裁决时，再刷新 09C 并手动触发 Opus 4.6。",
        )
        copy_prompt = "当前无需触发 Notion AI Opus 4.6。继续自动开发，并等待新的 blocker、open gap、Awaiting gate 或主观裁决需求出现后，再刷新 09C。"
        review_required = False
    elif stale_gap_count > 0 and snapshot.latest_success_run:
        intervention_kind = "P1 phase readiness + 旧失败 Gap 裁决"
        why_now = (
            f"最新自动化证据 `{snapshot.latest_success_run}` 已成功，但 Notion 里仍有 {stale_gap_count} 条旧失败遗留的 "
            "Open UAT Gap 继续挂着。当前最需要 Opus 4.6 介入的不是泛化审代码，而是判断这些旧 gap 现在是否仍然构成真实阻塞，"
            "以及 P1 是否已经具备进入主观 phase-ready 审查的条件。"
        )
        gate_direction = (
            "这次 Opus 介入的目标，是给出“继续阻塞 / 解除旧 gap / 进入下一 phase”的判断，而不是重复做一轮机械 QA。"
        )
        questions = (
            f"`{snapshot.latest_verified_plan}` 在最新成功 run 与 QA 证据下，是否已经达到可被视为 Verified 的真实状态？",
            "当前仍然 Open 的旧失败 gap，属于仍有效的风险，还是已经被后续成功证据覆盖的历史残留？",
            "如果这些 gap 应被视为历史残留，控制塔应该如何清理或合并它们，避免它们继续错误地阻塞 phase 判断？",
            "在 Notion + GitHub-only 的证据边界下，当前这套 Opus 4.6 审查机制是否已经足够稳健？",
            "P1 在这次判断后应该进入什么下一步：Approved、Changes Requested，还是转入新的 cleanup / hardening phase？",
        )
        out_of_scope = (
            "不要要求查看本地终端文件、聊天上下文或未 push 到 GitHub 的本地改动。",
            "不要把历史 browser hand-check 文档重新当成当前审批规则。",
            "不要重复做已经由自动化 run 和 QA 覆盖的机械通过性检查。",
        )
        writeback_steps = (
            "在 Review Gate 回写 Approved 或 Changes Requested。",
            "如果判定旧 gap 已失效，明确写出哪些 gap 应该被 resolve / merge。",
            "如果判定仍有阻塞，明确最小补救动作，并生成新的 plan 或 task。",
        )
        copy_prompt = (
            "请你作为 Notion AI 内置 Opus 4.6，本次不要做泛化代码审查，而是做一次“P1 phase readiness + 旧失败 Gap 裁决”。"
            "只允许使用当前工作区里的 Notion 页面、相关数据库记录、GitHub 仓库 "
            f"{repo_url} 以及 GitHub Actions 入口 {actions_url} 作为证据。不要引用任何本地终端文件、聊天里的本地路径或未同步到 GitHub 的信息。"
            f"当前背景是：活动 phase 为 `{snapshot.active_phase}`，当前已验证 plan 为 `{snapshot.latest_verified_plan}`，"
            f"最近成功执行证据是 `{snapshot.latest_success_run}`，但 Notion 中仍有 {stale_gap_count} 条旧失败遗留的 Open UAT Gap。"
            "请重点阅读 00 项目宪法、01 当前状态、09 GSD 自动化控制平面、04A Review Gate、02A GSD Plan、02B Execution Run、05 QA / 验证、05A UAT Gap、06 证据与资产。"
            "请回答：1. 当前成功证据是否足以说明该 plan 已真实验证；2. 这些旧失败 gap 是否仍是 active blocker；"
            "3. 如果不是 blocker，应该怎样在控制塔中 resolve / merge；4. 当前 Opus 审查机制是否足够稳健；"
            "5. 接下来应该给出 Approved、Changes Requested，还是进入新的 cleanup phase；6. 给出一段可直接回写到 Review Gate 的结论。"
        )
        review_required = True
    elif open_gap_count > 0:
        intervention_kind = "失败阻塞分流审查"
        why_now = (
            "当前仍存在未解决的 open gap，而成功证据不足以覆盖它们。Opus 4.6 现在需要做的是判断这些阻塞究竟是实现错误、"
            "自动化配置问题，还是应该升级为更高层架构判断。"
        )
        gate_direction = "这次 Opus 介入的目标，是为 fix plan 定位最小正确路径。"
        questions = (
            "当前 open gap 中，哪一条是真正的 phase blocker？",
            "这些 blocker 属于 correctness、workflow/configuration，还是需要架构层判断？",
            "下一步是否应该先修实现、先修控制面，还是新增 cleanup phase？",
            "当前 Review Gate 是否应保持阻塞，直到新的 fix run 完成？",
        )
        out_of_scope = (
            "不要要求本地终端文件或未入库证据。",
            "不要重复做通用 UI 审美评论，除非它直接关系到 blocker。",
            "不要把历史 browser hand-check 文档当成当前 gate。",
        )
        writeback_steps = (
            "在 Review Gate 回写 Changes Requested 或明确阻塞判断。",
            "补新的 fix plan。",
            "等待新的自动化 run / QA 证据后再刷新 09C。",
        )
        copy_prompt = (
            "请你作为 Notion AI 内置 Opus 4.6，只使用当前工作区中的 Notion 页面、数据库记录、GitHub 仓库 "
            f"{repo_url} 和 GitHub Actions 入口 {actions_url} 进行一次失败阻塞分流审查。"
            f"当前活动 phase 是 `{snapshot.active_phase}`，存在 {open_gap_count} 条 open gap。"
            "请判断这些 gap 哪些是真正 blocker，它们属于 correctness、workflow/configuration 还是更高层架构问题，"
            "并给出最小修复路径与可直接回写 Review Gate 的结论。不要引用任何本地终端文件。"
        )
        review_required = True
    else:
        intervention_kind = "Phase 收口与下一步优先级审查"
        why_now = (
            f"自动化证据当前看起来稳定，未见仍然 open 的 gap。现在更适合让 Opus 4.6 判断：{snapshot.active_phase} 是否可以正式收口，"
            "以及下一阶段最值得投入的方向是什么。"
        )
        gate_direction = "这次 Opus 介入的目标，是给出 phase-ready 与 next-phase 优先级判断。"
        questions = (
            f"`{snapshot.latest_verified_plan}` 是否已经足够证明 `{snapshot.active_phase}` 可以结束？",
            "当前控制塔和 GitHub-only 的证据边界是否已经足以支撑后续节奏？",
            "下一阶段最值得优先投入的是 cleanup、UI/demo 质量，还是更深的 automation hardening？",
            "当前 Review Gate 是否应 Approved？",
        )
        out_of_scope = (
            "不要引用本地终端文件。",
            "不要把历史 browser hand-check 文档当成当前审批依据。",
            "不要提出与当前 phase 无关的大范围重构建议。",
        )
        writeback_steps = (
            "在 Review Gate 回写 Approved 或 Changes Requested。",
            "如果 Approved，明确下一 phase 的最优先方向。",
            "如果 Changes Requested，指出最小剩余缺口。",
        )
        copy_prompt = (
            "请你作为 Notion AI 内置 Opus 4.6，只使用当前工作区中的 Notion 页面、数据库记录、GitHub 仓库 "
            f"{repo_url} 和 GitHub Actions 入口 {actions_url}，做一次 phase 收口与下一步优先级审查。"
            f"当前活动 phase 是 `{snapshot.active_phase}`，当前已验证 plan 是 `{snapshot.latest_verified_plan}`。"
            "请判断当前 phase 是否应 Approved、是否还存在必须修正的缺口，以及下一阶段最值得投入的方向是什么。"
            "不要引用任何本地终端文件。"
        )
        review_required = True

    return CurrentReviewBrief(
        page_title="09C 当前 Opus 4.6 审查简报",
        review_required=review_required,
        intervention_kind=intervention_kind,
        review_target=review_target,
        why_now=why_now,
        gate_direction=gate_direction,
        facts=tuple(facts),
        questions=questions,
        out_of_scope=out_of_scope,
        writeback_steps=writeback_steps,
        copy_prompt=copy_prompt,
    )


def render_current_review_brief_blocks(brief: CurrentReviewBrief, snapshot: ReviewSnapshot, config: dict[str, Any]) -> list[dict[str, Any]]:
    prompt_heading = "可直接复制到 Notion AI 的当前请求" if brief.review_required else "当前不需要触发 Notion AI"
    next_steps_heading = "审查后如何回写" if brief.review_required else "现在该怎么做"
    blocks: list[dict[str, Any]] = [
        callout_block(
            "这不是固定提示词模板，而是根据当前 phase、run、gap、gate 状态生成的一次当前审查简报。只有当 09C 被刷新后，才应该触发 Notion AI Opus 4.6。",
            "🧭",
        ),
        heading_block("当前介入结论"),
        bullet_block(f"介入类型：{brief.intervention_kind}"),
        bullet_block(f"审查目标：{brief.review_target}"),
        bullet_block(brief.gate_direction),
        divider_block(),
        heading_block("为什么现在需要 Opus 4.6"),
        paragraph_block(brief.why_now),
        heading_block("当前事实"),
    ]
    blocks.extend(bullet_block(line) for line in brief.facts)
    blocks.extend(
        [
            divider_block(),
            heading_block("Opus 必须回答"),
        ]
    )
    blocks.extend(number_block(question) for question in brief.questions)
    blocks.extend(
        [
            divider_block(),
            heading_block("先打开这些证据面"),
            page_link_block(page_id(config, "constitution")),
            page_link_block(page_id(config, "status")),
            page_link_block(page_id(config, "control_plane")),
            page_link_block(page_id(config, "opus_protocol")),
            database_link_block(database_id(config, "plans")),
            database_link_block(database_id(config, "runs")),
            database_link_block(database_id(config, "qa")),
            database_link_block(database_id(config, "gates")),
            database_link_block(database_id(config, "gaps")),
            database_link_block(database_id(config, "assets")),
            paragraph_parts_block([notion_text("GitHub Repo / ai-fantui-logicmvp", config_url(config, "github_repo"))]),
            paragraph_parts_block([notion_text("GitHub Actions / GSD Automation Loop", config_url(config, "github_actions"))]),
            divider_block(),
            heading_block("不要做什么"),
        ]
    )
    blocks.extend(bullet_block(item) for item in brief.out_of_scope)
    blocks.extend(
        [
            divider_block(),
            heading_block(prompt_heading),
            paragraph_block(brief.copy_prompt),
            divider_block(),
            heading_block(next_steps_heading),
        ]
    )
    blocks.extend(number_block(step) for step in brief.writeback_steps)
    if snapshot.open_gap_titles:
        blocks.extend(
            [
                divider_block(),
                heading_block("当前仍在视野内的 Gap"),
            ]
        )
        blocks.extend(bullet_block(title) for title in snapshot.open_gap_titles[:8])
    return blocks


def render_dashboard_blocks(brief: CurrentReviewBrief, snapshot: ReviewSnapshot, config: dict[str, Any]) -> list[dict[str, Any]]:
    current_action = (
        "继续自动开发；当前无需手动触发 Opus 4.6。"
        if not brief.review_required
        else "打开 09C 当前 Opus 4.6 审查简报，并按其中当前请求手动触发 Opus 4.6。"
    )
    current_opus_state = (
        "当前无需 Opus 审查"
        if not brief.review_required
        else f"需要 Opus 4.6 介入：{brief.intervention_kind}"
    )
    blocks: list[dict[str, Any]] = [
        callout_block(
            f"{DASHBOARD_SYNC_MARKER} — 这个顶部快照由 repo-side sync 自动刷新；下方旧摘要若尚未同步，应以这里为准。",
            "🧭",
        ),
        heading_block("当前快照（自动同步）"),
        bullet_block(f"当前阶段：{snapshot.active_phase}"),
        bullet_block(f"当前已验证 Plan：{snapshot.latest_verified_plan}"),
        bullet_block(f"当前默认 Plan：{config.get('default_plan', snapshot.latest_verified_plan)}"),
        bullet_block(f"最近成功执行证据：{snapshot.latest_success_run or '暂无'}"),
        bullet_block(f"当前 Gate：{snapshot.gate_name}（{snapshot.gate_status}）"),
        bullet_block(f"当前 Opus 状态：{current_opus_state}"),
        bullet_block(f"当前唯一人工动作：{current_action}"),
        bullet_block(f"Open Gap 数量：{len(snapshot.open_gap_titles)}"),
        page_link_block(page_id(config, "status")),
        page_link_block(page_id(config, "opus_brief")),
        page_link_block(page_id(config, "freeze_packet")),
        divider_block(),
    ]
    return blocks


def upsert_dashboard_snapshot_section(
    client: NotionClient,
    dashboard_page_id: str,
    blocks: list[dict[str, Any]],
) -> None:
    children = client.list_block_children(dashboard_page_id)
    start_index = None
    end_index = None
    for index, block in enumerate(children):
        if block.get("type") == "callout" and block_plain_text(block).startswith(DASHBOARD_SYNC_MARKER):
            start_index = index
            end_index = index + 1
            while end_index < len(children) and children[end_index].get("type") != "divider":
                end_index += 1
            if end_index < len(children) and children[end_index].get("type") == "divider":
                end_index += 1
            break
    if start_index is not None and end_index is not None:
        for block in children[start_index:end_index]:
            if block.get("archived") or block.get("in_trash"):
                continue
            client.request("DELETE", f"/v1/blocks/{block['id']}")
    client.request(
        "PATCH",
        f"/v1/blocks/{dashboard_page_id}/children",
        {"children": blocks, "position": {"type": "start"}},
    )


def build_gate_update_properties(brief: CurrentReviewBrief, *, activate_gate: bool) -> dict[str, Any]:
    if activate_gate:
        return {
            "Status": select_value("Awaiting Opus 4.6"),
            "What To Review": rich_text_value(brief.why_now),
            "Next Action": rich_text_value("打开 09C 当前 Opus 4.6 审查简报，并把其中的当前请求复制到 Notion AI。"),
            "Decision Notes": rich_text_value("等待 Opus 4.6 基于当前审查简报给出 Approved 或 Changes Requested。"),
        }
    next_action = (
        "打开 09C 当前 Opus 4.6 审查简报，并把其中的当前请求复制到 Notion AI。"
        if brief.review_required
        else "继续自动开发；只有出现新的 gate / blocker / open gap 时，再刷新 09C 并手动触发 Opus 4.6。"
    )
    return {
        "What To Review": rich_text_value(brief.why_now),
        "Next Action": rich_text_value(next_action),
    }


def write_current_opus_review_brief(
    client: NotionClient,
    config: dict[str, Any],
    *,
    activate_gate: bool,
) -> dict[str, Any]:
    snapshot = fetch_review_snapshot(client, config)
    effective_snapshot = (
        ReviewSnapshot(
            active_phase=snapshot.active_phase,
            active_phase_goal=snapshot.active_phase_goal,
            active_phase_summary=snapshot.active_phase_summary,
            latest_verified_plan=snapshot.latest_verified_plan,
            latest_success_run=snapshot.latest_success_run,
            latest_failed_run=snapshot.latest_failed_run,
            latest_passing_qa=snapshot.latest_passing_qa,
            gate_page_id=snapshot.gate_page_id,
            gate_name=snapshot.gate_name,
            gate_status="Awaiting Opus 4.6",
            ready_task_id=snapshot.ready_task_id,
            ready_task=snapshot.ready_task,
            open_gap_titles=snapshot.open_gap_titles,
            stale_gap_titles=snapshot.stale_gap_titles,
        )
        if activate_gate
        else snapshot
    )
    brief = build_current_review_brief(effective_snapshot, config, force_review=activate_gate)
    brief_page_id = page_id(config, "opus_brief")
    client.update_page_properties(brief_page_id, {"title": title_value(brief.page_title)})
    client.replace_page_body(brief_page_id, render_current_review_brief_blocks(brief, effective_snapshot, config))
    dashboard_page_id = page_id(config, "dashboard")
    client.update_page_properties(dashboard_page_id, {"title": title_value("AI FANTUI LogicMVP 控制塔")})
    upsert_dashboard_snapshot_section(client, dashboard_page_id, render_dashboard_blocks(brief, effective_snapshot, config))

    if snapshot.gate_page_id:
        client.update_page_properties(
            snapshot.gate_page_id,
            build_gate_update_properties(brief, activate_gate=activate_gate),
        )
    if snapshot.ready_task_id:
        client.update_page_properties(
            snapshot.ready_task_id,
            {
                "Acceptance": rich_text_value("基于 09C 当前 Opus 4.6 审查简报，在 Notion AI 中触发当前所需介入，而不是使用固定模板。"),
                "Next Step": rich_text_value("打开 09C 当前 Opus 4.6 审查简报，按其中的当前介入请求执行。"),
            },
        )
    retired_artifact_ids = retire_legacy_review_artifacts(
        client,
        config,
        snapshot=snapshot,
        brief=brief,
    )

    return {
        "page_id": brief_page_id,
        "page_title": brief.page_title,
        "review_required": brief.review_required,
        "intervention_kind": brief.intervention_kind,
        "review_target": brief.review_target,
        "gate_status": "Awaiting Opus 4.6" if activate_gate else snapshot.gate_status,
        "open_gap_count": len(snapshot.open_gap_titles),
        "stale_gap_count": len(snapshot.stale_gap_titles),
        "latest_success_run": snapshot.latest_success_run,
        "latest_failed_run": snapshot.latest_failed_run,
        "why_now": brief.why_now,
        "retired_legacy_artifact_ids": retired_artifact_ids,
    }


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
) -> dict[str, Any]:
    started_at = results[0].started_at if results else utc_now()
    ended_at = results[-1].ended_at if results else utc_now()
    written: dict[str, Any] = {}

    artifact_url = ""
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID"):
        artifact_url = (
            f"{os.environ['GITHUB_SERVER_URL']}/"
            f"{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
        )
    elif os.environ.get("GITHUB_SERVER_URL"):
        artifact_url = os.environ["GITHUB_SERVER_URL"]

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
            "Artifacts": rich_text_value(artifact_url),
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
    else:
        resolved_gap_ids = resolve_superseded_failure_gaps(
            client,
            config,
            plan_id=plan_id,
            success_run_title=title,
        )
        if resolved_gap_ids:
            written["resolved_gaps"] = resolved_gap_ids
        if not opus_gate and config.get("pages", {}).get("opus_brief"):
            written["opus_review_brief"] = write_current_opus_review_brief(
                client,
                config,
                activate_gate=False,
            )

    if opus_gate:
        gate_page_id = client.upsert_page(
            database_id(config, "gates"),
            TITLE_PROPS["gates"],
            config["default_review_gate"],
            {
                "Scope": select_value("Phase"),
                "Trigger": select_value("After Execution"),
                "Status": select_value("Awaiting Opus 4.6"),
                "Reviewer": select_value("Opus 4.6"),
                "What To Review": rich_text_value("等待当前 09C 审查简报刷新后执行。"),
                "Decision Notes": rich_text_value(""),
                "Next Action": rich_text_value("刷新 09C 当前 Opus 4.6 审查简报，然后手动触发 Opus。"),
            },
        )
        written["gate"] = gate_page_id
        written["opus_review_brief"] = write_current_opus_review_brief(client, config, activate_gate=True)

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
        help="After writing the run, refresh the current Opus brief and move the default review gate to Awaiting Opus 4.6.",
    )
    run_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )

    review_parser = subparsers.add_parser(
        "prepare-opus-review",
        help="Read the current Notion/GitHub evidence state and refresh the current Opus 4.6 review brief.",
    )
    review_parser.add_argument(
        "--activate-gate",
        action="store_true",
        help="Move the default review gate to Awaiting Opus 4.6 after refreshing the current brief.",
    )
    review_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute the current review brief without writing back to Notion.",
    )
    review_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser


def output_run_result(format_name: str, payload: dict[str, Any]) -> None:
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
    if payload.get("opus_review_brief"):
        print(f"Current Opus brief: {payload['opus_review_brief']['intervention_kind']}")


def output_review_result(format_name: str, payload: dict[str, Any]) -> None:
    if format_name == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"Current Opus intervention: {payload['intervention_kind']}")
    print(f"Review target: {payload['review_target']}")
    print(f"Open gaps: {payload['open_gap_count']}")
    print(f"Stale gaps: {payload['stale_gap_count']}")
    print(f"Gate status: {payload['gate_status']}")
    print(f"Why now: {payload['why_now']}")


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
        if "opus_review_brief" in written:
            payload["opus_review_brief"] = written["opus_review_brief"]
    output_run_result(args.format, payload)
    return 0 if summary.succeeded else 1


def handle_prepare_opus_review(args: argparse.Namespace, config: dict[str, Any]) -> int:
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("NOTION_API_KEY is required for prepare-opus-review.")
    client = NotionClient(token)
    snapshot = fetch_review_snapshot(client, config)
    effective_snapshot = (
        snapshot
        if not args.activate_gate
        else ReviewSnapshot(
            active_phase=snapshot.active_phase,
            active_phase_goal=snapshot.active_phase_goal,
            active_phase_summary=snapshot.active_phase_summary,
            latest_verified_plan=snapshot.latest_verified_plan,
            latest_success_run=snapshot.latest_success_run,
            latest_failed_run=snapshot.latest_failed_run,
            latest_passing_qa=snapshot.latest_passing_qa,
            gate_page_id=snapshot.gate_page_id,
            gate_name=snapshot.gate_name,
            gate_status="Awaiting Opus 4.6",
            ready_task_id=snapshot.ready_task_id,
            ready_task=snapshot.ready_task,
            open_gap_titles=snapshot.open_gap_titles,
            stale_gap_titles=snapshot.stale_gap_titles,
        )
    )
    brief = build_current_review_brief(effective_snapshot, config, force_review=args.activate_gate)
    payload: dict[str, Any] = {
        "review_required": brief.review_required,
        "intervention_kind": brief.intervention_kind,
        "review_target": brief.review_target,
        "why_now": brief.why_now,
        "gate_status": effective_snapshot.gate_status,
        "open_gap_count": len(snapshot.open_gap_titles),
        "stale_gap_count": len(snapshot.stale_gap_titles),
        "latest_success_run": snapshot.latest_success_run,
        "latest_failed_run": snapshot.latest_failed_run,
    }
    if not args.dry_run:
        payload["notion"] = write_current_opus_review_brief(client, config, activate_gate=args.activate_gate)
    output_review_result(args.format, payload)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_control_plane_config(Path(args.config))
    if args.command_name == "run":
        return handle_run(args, config)
    if args.command_name == "prepare-opus-review":
        return handle_prepare_opus_review(args, config)
    parser.error(f"Unsupported command: {args.command_name}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Run GSD validation commands and mirror outcomes into the Notion control plane.

This script intentionally uses only the Python standard library so it can run
locally and in GitHub Actions without adding runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
FREEZE_PACKET_SYNC_MARKER = "AUTO-SYNCED FREEZE PACKET SNAPSHOT"
REPO_COORDINATION_PLAN_MARKER = "AUTO-SYNCED COORDINATION PLAN SNAPSHOT"
REPO_DEV_HANDOFF_MARKER = "AUTO-SYNCED DEV HANDOFF SNAPSHOT"
REPO_QA_REPORT_MARKER = "AUTO-SYNCED QA REPORT SNAPSHOT"
REPO_FREEZE_PACKET_MARKER = "AUTO-SYNCED REPO FREEZE PACKET SNAPSHOT"
DEFAULT_REPO_DOCS = {
    "coordination_plan": Path("docs/coordination/plan.md"),
    "dev_handoff": Path("docs/coordination/dev_handoff.md"),
    "qa_report": Path("docs/coordination/qa_report.md"),
    "freeze_packet": Path("docs/freeze/2026-04-10-freeze-demo-packet.md"),
}
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
ACTIVE_SYNC_PAGE_TITLES = {
    "status": "01 当前状态（自动同步）",
    "opus_brief": "09C 当前 Opus 4.6 审查简报",
    "freeze_packet": "10 Freeze Demo Packet",
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
DATABASE_LINK_LABELS = {
    "plans": "02A GSD Plan 数据库",
    "runs": "02B Execution Run 数据库",
    "qa": "05 QA / 验证数据库",
    "gates": "04A Review Gate 数据库",
    "gaps": "05A UAT Gap 数据库",
    "assets": "06 证据与资产数据库",
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
    latest_success_run_notes: str | None = None
    latest_passing_qa_summary: str | None = None


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


@dataclass(frozen=True)
class RepoDocSyncResult:
    path: str
    marker: str


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

    def create_child_page(self, parent_page_id: str, title: str) -> str:
        page = self.request(
            "POST",
            "/v1/pages",
            {
                "parent": {"page_id": parent_page_id},
                "properties": {"title": title_value(title)},
            },
        )
        return page["id"]

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


def is_missing_database_error(message: str) -> bool:
    return "Could not find database" in message or "HTTP 404 /v1/databases/" in message


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def markdown_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def notion_page_url(page_or_database_id: str) -> str:
    return f"https://www.notion.so/{page_or_database_id.replace('-', '')}"


def page_link_paragraph_block(config: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    return paragraph_parts_block([notion_text(label, notion_page_url(page_id(config, key)))])


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


def save_control_plane_config(config_path: Path, config: dict[str, Any]) -> None:
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def database_id(config: dict[str, Any], key: str) -> str:
    env_name = DATABASE_ENV.get(key)
    if env_name and os.environ.get(env_name):
        return os.environ[env_name]
    return config["databases"][key]


def database_page_id(config: dict[str, Any], key: str) -> str:
    return config["databases"][key]


def database_link_paragraph_block(config: dict[str, Any], key: str) -> dict[str, Any]:
    label = DATABASE_LINK_LABELS.get(key, key)
    return paragraph_parts_block([notion_text(label, notion_page_url(database_page_id(config, key)))])


def page_id(config: dict[str, Any], key: str) -> str:
    return config["pages"][key]


def config_url(config: dict[str, Any], key: str) -> str:
    return config["urls"][key]


def is_missing_page_error(message: str) -> bool:
    lowered = message.lower()
    return (
        "could not find page" in lowered
        or "could not find block" in lowered
        or ("/v1/pages/" in lowered and "http 404" in lowered)
        or ("/v1/blocks/" in lowered and "http 404" in lowered)
    )


def is_archived_page_write_error(message: str) -> bool:
    return "can't edit block that is archived" in message.lower()


def ensure_live_active_pages(
    client: NotionClient,
    config: dict[str, Any],
    *,
    config_path: Path,
) -> dict[str, dict[str, str]]:
    replacements: dict[str, dict[str, str]] = {}
    pages = config.get("pages", {})
    if "dashboard" not in pages:
        return replacements
    dashboard = client.get_page(page_id(config, "dashboard"))
    if dashboard.get("archived") or dashboard.get("in_trash"):
        raise RuntimeError("Dashboard page is archived; cannot create replacement active pages.")

    for key, title in ACTIVE_SYNC_PAGE_TITLES.items():
        if key not in pages:
            continue
        current_id = page_id(config, key)
        try:
            page = client.get_page(current_id)
        except RuntimeError as exc:
            if not is_missing_page_error(str(exc)):
                raise
            page = {"archived": True, "in_trash": True}
        if not page.get("archived") and not page.get("in_trash"):
            continue
        replacement_id = client.create_child_page(page_id(config, "dashboard"), title)
        replacement_page = client.get_page(replacement_id)
        if replacement_page.get("archived") or replacement_page.get("in_trash"):
            continue
        config["pages"][key] = replacement_id
        replacements[key] = {"old_id": current_id, "new_id": replacement_id}

    if replacements:
        save_control_plane_config(config_path, config)
    return replacements


def page_is_writable(client: NotionClient, config: dict[str, Any], key: str) -> bool:
    try:
        page = client.get_page(page_id(config, key))
    except RuntimeError as exc:
        if is_missing_page_error(str(exc)):
            return False
        raise
    return not page.get("archived") and not page.get("in_trash")


def active_page_unavailable_keys(client: NotionClient, config: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        key
        for key in ("status", "opus_brief", "freeze_packet")
        if key in config.get("pages", {}) and not page_is_writable(client, config, key)
    )


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


def derive_compact_success_summary(results: list[CommandResult]) -> str | None:
    tests_ok: int | None = None
    demo_smoke_count: int | None = None

    for result in results:
        if "unittest discover" in result.command:
            match = re.search(r"Ran\s+(\d+)\s+tests", result.stderr)
            if match:
                tests_ok = int(match.group(1))
        if "demo_path_smoke.py" in result.command and result.stdout.strip():
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                continue
            completed = payload.get("completed_scenarios")
            if isinstance(completed, int):
                demo_smoke_count = completed

    fragments: list[str] = []
    if tests_ok is not None:
        fragments.append(f"{tests_ok} tests OK")
    if demo_smoke_count is not None:
        fragments.append(f"{demo_smoke_count} demo smoke scenarios pass")
    fragments.append(f"{len(results)}/{len(results)} shared validation checks pass")
    if len(fragments) == 1:
        return fragments[0] + "."
    if len(fragments) == 2:
        return f"{fragments[0]} and {fragments[1]}."
    return ", ".join(fragments[:-1]) + f", and {fragments[-1]}."


def derive_compact_success_summary_from_text(text: str) -> str | None:
    tests_ok: int | None = None
    demo_smoke_count: int | None = None
    shared_check_count: int | None = None

    tests_match = re.search(r"Ran\s+(\d+)\s+tests", text)
    if tests_match:
        tests_ok = int(tests_match.group(1))
    smoke_match = re.search(r'"completed_scenarios"\s*:\s*(\d+)', text)
    if smoke_match:
        demo_smoke_count = int(smoke_match.group(1))
    checks_match = re.search(r'"command_count"\s*:\s*(\d+)', text)
    if checks_match:
        shared_check_count = int(checks_match.group(1))

    fragments: list[str] = []
    if tests_ok is not None:
        fragments.append(f"{tests_ok} tests OK")
    if demo_smoke_count is not None:
        fragments.append(f"{demo_smoke_count} demo smoke scenarios pass")
    if shared_check_count is not None:
        fragments.append(f"{shared_check_count}/{shared_check_count} shared validation checks pass")
    if not fragments:
        return None
    if len(fragments) == 1:
        return fragments[0] + "."
    if len(fragments) == 2:
        return f"{fragments[0]} and {fragments[1]}."
    return ", ".join(fragments[:-1]) + f", and {fragments[-1]}."


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
        latest_success_run_notes=row_text(success_run_row, "Notes") or None,
        latest_passing_qa_summary=row_text(passing_qa_row, "Summary") or None,
    )


def page_text_lines(client: NotionClient, page_id_value: str) -> list[str]:
    return [text.strip() for block in client.list_block_children(page_id_value) if (text := block_plain_text(block).strip())]


def page_prefixed_value(lines: list[str], prefix: str) -> str | None:
    normalized_prefixes = {prefix, prefix.lstrip("- ").lstrip("0123456789. ")}
    for line in lines:
        normalized_line = line.lstrip("- ").lstrip("0123456789. ")
        for candidate in normalized_prefixes:
            if normalized_line.startswith(candidate):
                return normalized_line[len(candidate) :].strip()
    return None


def markdown_prefixed_code_value(text: str, prefix: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(prefix)}`([^`\n]+)`", text)
    if match:
        return match.group(1).strip()
    return None


def parse_gate_line(text: str | None) -> tuple[str, str]:
    if not text:
        return "OPUS-4.6 周期审查 Gate", "Standby"
    if "（" in text and text.endswith("）"):
        gate_name, status = text.rsplit("（", 1)
        return gate_name.strip(), status[:-1].strip()
    if "(" in text and text.endswith(")"):
        gate_name, status = text.rsplit("(", 1)
        return gate_name.strip(), status[:-1].strip()
    return text.strip(), "Standby"


def parse_open_gap_titles(open_gap_text: str | None) -> tuple[str, ...]:
    if not open_gap_text:
        return ()
    digits = "".join(char for char in open_gap_text if char.isdigit())
    if digits == "" or int(digits) <= 0:
        return ()
    return tuple("Open gap requires follow-up" for _ in range(int(digits)))


def fetch_review_snapshot_from_repo_docs(cwd: Path, config: dict[str, Any]) -> ReviewSnapshot:
    freeze_path = cwd / DEFAULT_REPO_DOCS["freeze_packet"]
    if not freeze_path.exists():
        raise RuntimeError(f"Repo freeze packet missing: {freeze_path}")
    text = freeze_path.read_text(encoding="utf-8")

    active_phase = markdown_prefixed_code_value(text, "- 当前阶段：") or "未识别活动 phase"
    latest_verified_plan = markdown_prefixed_code_value(text, "- 当前已验证 Plan：") or config["default_plan"]
    latest_success_run = markdown_prefixed_code_value(text, "- 最近成功执行证据：")
    gate_name, gate_status = parse_gate_line(markdown_prefixed_code_value(text, "- 当前 Gate："))
    open_gap_titles = parse_open_gap_titles(markdown_prefixed_code_value(text, "- Open Gap 数量："))
    opus_state = markdown_prefixed_code_value(text, "- 当前 Opus 状态：") or "当前无需 Opus 审查"
    compact_summary = derive_compact_success_summary_from_text(text)

    ready_task = None
    if "无需" not in opus_state:
        ready_task = "打开 09C 当前 Opus 4.6 审查简报，并按其中当前请求手动触发 Opus 4.6。"

    return ReviewSnapshot(
        active_phase=active_phase,
        active_phase_goal="",
        active_phase_summary="Recovered from repo-side freeze packet because shared Notion databases/pages were unavailable.",
        latest_verified_plan=latest_verified_plan,
        latest_success_run=latest_success_run,
        latest_failed_run=None,
        latest_passing_qa=(f"{latest_success_run} QA" if latest_success_run else None),
        gate_page_id=None,
        gate_name=gate_name,
        gate_status=gate_status,
        ready_task_id=None,
        ready_task=ready_task,
        open_gap_titles=open_gap_titles,
        stale_gap_titles=(),
        latest_success_run_notes=compact_summary,
        latest_passing_qa_summary=(f"PASS. {compact_summary}" if compact_summary else None),
    )


def fetch_review_snapshot_from_pages(client: NotionClient, config: dict[str, Any]) -> ReviewSnapshot:
    dashboard_lines = page_text_lines(client, page_id(config, "dashboard"))
    brief_lines = page_text_lines(client, page_id(config, "opus_brief"))
    freeze_lines = page_text_lines(client, page_id(config, "freeze_packet"))
    status_lines = page_text_lines(client, page_id(config, "status"))

    active_phase = (
        page_prefixed_value(dashboard_lines, "- 当前阶段：")
        or page_prefixed_value(status_lines, "- 活动 phase：")
        or "未识别活动 phase"
    )
    latest_verified_plan = (
        page_prefixed_value(dashboard_lines, "- 当前已验证 Plan：")
        or page_prefixed_value(status_lines, "- 当前已验证 plan：")
        or config["default_plan"]
    )
    latest_success_run = (
        page_prefixed_value(dashboard_lines, "- 最近成功执行证据：")
        or page_prefixed_value(status_lines, "- 最近成功执行证据：")
    )
    latest_failed_run = page_prefixed_value(brief_lines, "- 最近失败历史证据：")
    latest_passing_qa_summary = (
        page_prefixed_value(freeze_lines, "- 当前 QA 摘要：")
        or page_prefixed_value(status_lines, "- QA 摘要：")
    )
    latest_success_run_notes = (
        page_prefixed_value(freeze_lines, "- 当前运行摘要：")
        or page_prefixed_value(status_lines, "- 运行摘要：")
    )
    gate_name, gate_status = parse_gate_line(
        page_prefixed_value(dashboard_lines, "- 当前 Gate：")
        or page_prefixed_value(status_lines, "- 当前 Gate：")
    )
    open_gap_titles = parse_open_gap_titles(
        page_prefixed_value(dashboard_lines, "- Open Gap 数量：")
        or page_prefixed_value(freeze_lines, "- Open Gap 数量：")
    )

    return ReviewSnapshot(
        active_phase=active_phase,
        active_phase_goal="",
        active_phase_summary="Derived from active control-plane pages because database access is unavailable.",
        latest_verified_plan=latest_verified_plan,
        latest_success_run=latest_success_run,
        latest_failed_run=latest_failed_run,
        latest_passing_qa=None,
        gate_page_id=None,
        gate_name=gate_name,
        gate_status=gate_status,
        ready_task_id=None,
        ready_task=None,
        open_gap_titles=open_gap_titles,
        stale_gap_titles=(),
        latest_success_run_notes=latest_success_run_notes,
        latest_passing_qa_summary=latest_passing_qa_summary,
    )


def fetch_review_snapshot_from_dashboard_page(client: NotionClient, config: dict[str, Any]) -> ReviewSnapshot:
    dashboard_lines = page_text_lines(client, page_id(config, "dashboard"))
    active_phase = page_prefixed_value(dashboard_lines, "- 当前阶段：") or "未识别活动 phase"
    latest_verified_plan = page_prefixed_value(dashboard_lines, "- 当前已验证 Plan：") or config["default_plan"]
    latest_success_run = page_prefixed_value(dashboard_lines, "- 最近成功执行证据：")
    gate_name, gate_status = parse_gate_line(page_prefixed_value(dashboard_lines, "- 当前 Gate："))
    open_gap_titles = parse_open_gap_titles(page_prefixed_value(dashboard_lines, "- Open Gap 数量："))

    return ReviewSnapshot(
        active_phase=active_phase,
        active_phase_goal="",
        active_phase_summary="Derived from the live dashboard page because separate active subpages are unavailable.",
        latest_verified_plan=latest_verified_plan,
        latest_success_run=latest_success_run,
        latest_failed_run=None,
        latest_passing_qa=None,
        gate_page_id=None,
        gate_name=gate_name,
        gate_status=gate_status,
        ready_task_id=None,
        ready_task=None,
        open_gap_titles=open_gap_titles,
        stale_gap_titles=(),
    )


def github_run_number(text: str | None) -> int:
    if not text:
        return -1
    match = re.search(r"GitHub GSD automation (\d+)", text)
    return int(match.group(1)) if match else -1


def should_prefer_page_snapshot(
    primary_snapshot: ReviewSnapshot,
    page_snapshot: ReviewSnapshot,
    config: dict[str, Any],
) -> bool:
    page_run = github_run_number(page_snapshot.latest_success_run)
    primary_run = github_run_number(primary_snapshot.latest_success_run)
    if page_run > primary_run:
        return True
    default_plan = config.get("default_plan")
    return bool(
        default_plan
        and page_snapshot.latest_verified_plan == default_plan
        and primary_snapshot.latest_verified_plan != default_plan
    )


def build_fallback_run_snapshot(
    client: NotionClient,
    config: dict[str, Any],
    *,
    cwd: Path,
    plan_id: str,
    title: str,
    results: list[CommandResult],
    summary: RunSummary,
) -> ReviewSnapshot:
    try:
        snapshot = fetch_review_snapshot_from_pages(client, config)
    except RuntimeError as exc:
        if not is_missing_page_error(str(exc)):
            raise
        snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
    compact_success = derive_compact_success_summary(results) if summary.succeeded else None
    if summary.succeeded:
        return ReviewSnapshot(
            active_phase=snapshot.active_phase,
            active_phase_goal=snapshot.active_phase_goal,
            active_phase_summary=snapshot.active_phase_summary,
            latest_verified_plan=plan_id,
            latest_success_run=title,
            latest_failed_run=snapshot.latest_failed_run,
            latest_passing_qa=f"{title} QA",
            gate_page_id=snapshot.gate_page_id,
            gate_name=snapshot.gate_name,
            gate_status=snapshot.gate_status,
            ready_task_id=snapshot.ready_task_id,
            ready_task=snapshot.ready_task,
            open_gap_titles=snapshot.open_gap_titles,
            stale_gap_titles=snapshot.stale_gap_titles,
            latest_success_run_notes=compact_success or summary.output_digest,
            latest_passing_qa_summary=(f"{summary.qa_result}. {compact_success}" if compact_success else summary.output_digest),
        )
    return ReviewSnapshot(
        active_phase=snapshot.active_phase,
        active_phase_goal=snapshot.active_phase_goal,
        active_phase_summary=snapshot.active_phase_summary,
        latest_verified_plan=snapshot.latest_verified_plan,
        latest_success_run=snapshot.latest_success_run,
        latest_failed_run=title,
        latest_passing_qa=snapshot.latest_passing_qa,
        gate_page_id=snapshot.gate_page_id,
        gate_name=snapshot.gate_name,
        gate_status=snapshot.gate_status,
        ready_task_id=snapshot.ready_task_id,
        ready_task=snapshot.ready_task,
        open_gap_titles=snapshot.open_gap_titles,
        stale_gap_titles=snapshot.stale_gap_titles,
        latest_success_run_notes=snapshot.latest_success_run_notes,
        latest_passing_qa_summary=snapshot.latest_passing_qa_summary,
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
            page_link_paragraph_block(config, "constitution", "00 项目宪法"),
            page_link_paragraph_block(config, "status", "01 当前状态（自动同步）"),
            page_link_paragraph_block(config, "control_plane", "09 GSD 自动化控制平面"),
            page_link_paragraph_block(config, "opus_protocol", "09A Opus 4.6 手动审查协议"),
            database_link_paragraph_block(config, "plans"),
            database_link_paragraph_block(config, "runs"),
            database_link_paragraph_block(config, "qa"),
            database_link_paragraph_block(config, "gates"),
            database_link_paragraph_block(config, "gaps"),
            database_link_paragraph_block(config, "assets"),
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


def render_dashboard_blocks(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
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
    ]
    if unavailable_page_keys:
        blocks.append(
            bullet_block(
                "当前控制面模式：dashboard-only degraded mode（dashboard 仍为 live truth，独立 status / 09C / freeze 子页当前不可直写）。"
            )
        )
        names = {
            "status": "01 当前状态（自动同步）",
            "opus_brief": "09C 当前 Opus 4.6 审查简报",
            "freeze_packet": "10 Freeze Demo Packet",
        }
        blocks.append(
            bullet_block(
                "当前受 Notion archived page 限制暂不可直写："
                + "、".join(names[key] for key in unavailable_page_keys if key in names)
                + "。当前请以本 dashboard、repo docs 与 GitHub 证据为准。"
            )
        )
    for key, label in (
        ("status", "01 当前状态（自动同步）"),
        ("opus_brief", "09C 当前 Opus 4.6 审查简报"),
        ("freeze_packet", "10 Freeze Demo Packet"),
    ):
        if key in unavailable_page_keys:
            continue
        blocks.append(page_link_paragraph_block(config, key, label))
    if config.get("urls", {}).get("github_repo"):
        blocks.append(paragraph_parts_block([notion_text("GitHub Repo / ai-fantui-logicmvp", config_url(config, "github_repo"))]))
    if config.get("urls", {}).get("github_actions"):
        blocks.append(paragraph_parts_block([notion_text("GitHub Actions / GSD Automation Loop", config_url(config, "github_actions"))]))
    return blocks


def render_freeze_packet_blocks(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    current_opus_state = (
        "当前无需 Opus 审查"
        if not brief.review_required
        else f"需要 Opus 4.6 介入：{brief.intervention_kind}"
    )
    blocks: list[dict[str, Any]] = [
        callout_block(
            f"{FREEZE_PACKET_SYNC_MARKER} — 这个顶部冻结摘要由 repo-side sync 自动刷新；下方旧文字若尚未同步，应以这里为准。",
            "🧊",
        ),
        heading_block("当前冻结基线（自动同步）"),
        bullet_block(f"当前阶段：{snapshot.active_phase}"),
        bullet_block(f"当前已验证 Plan：{snapshot.latest_verified_plan}"),
        bullet_block(f"最近成功执行证据：{snapshot.latest_success_run or '暂无'}"),
        bullet_block(f"当前 Gate：{snapshot.gate_name}（{snapshot.gate_status}）"),
        bullet_block(f"当前 Opus 状态：{current_opus_state}"),
        bullet_block(f"Open Gap 数量：{len(snapshot.open_gap_titles)}"),
    ]
    if snapshot.latest_passing_qa_summary:
        blocks.append(bullet_block(f"当前 QA 摘要：{snapshot.latest_passing_qa_summary}"))
    if snapshot.latest_success_run_notes:
        blocks.append(bullet_block(f"当前运行摘要：{snapshot.latest_success_run_notes}"))
    blocks.extend(
        [
            page_link_paragraph_block(config, "status", "01 当前状态（自动同步）"),
            page_link_paragraph_block(config, "constitution", "00 项目宪法"),
            page_link_paragraph_block(config, "opus_brief", "09C 当前 Opus 4.6 审查简报"),
            paragraph_parts_block([notion_text("GitHub Repo / ai-fantui-logicmvp", config_url(config, "github_repo"))]),
            paragraph_parts_block([notion_text("GitHub Actions / GSD Automation Loop", config_url(config, "github_actions"))]),
        ]
    )
    return blocks


def render_status_page_blocks(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    current_opus_state = (
        "当前无需 Opus 审查"
        if not brief.review_required
        else f"需要 Opus 4.6 介入：{brief.intervention_kind}"
    )
    current_action = (
        "继续自动开发；当前无需手动触发 Opus 4.6。"
        if not brief.review_required
        else "打开 09C 当前 Opus 4.6 审查简报，并按其中当前请求手动触发 Opus 4.6。"
    )
    blocks: list[dict[str, Any]] = [
        callout_block(
            "AUTO-SYNCED STATUS SNAPSHOT — 这个状态页由 repo-side sync 接管，用来替代受 archived-ancestor 限制的旧状态页。",
            "🚦",
        ),
        heading_block("当前轮次"),
        bullet_block(f"活动 phase：{snapshot.active_phase}"),
        bullet_block(f"当前已验证 plan：{snapshot.latest_verified_plan}"),
        bullet_block(f"当前 Gate：{snapshot.gate_name}（{snapshot.gate_status}）"),
        heading_block("当前结论"),
        bullet_block("当前 demo 基线已经由 GitHub-backed evidence 验证，可作为稳定的 freeze / demo packet 基线。"),
        bullet_block("dashboard 与 freeze packet 顶部快照已经进入 repo-side 自动同步路径。"),
        bullet_block(f"当前 Opus 状态：{current_opus_state}"),
        bullet_block("P7 的 spec-driven workbench foundation 已在 repo 中提前播种，但正式自动执行顺序暂时仍以 P6 为先。"),
        heading_block("当前回归"),
        bullet_block(f"最近成功执行证据：{snapshot.latest_success_run or '暂无'}"),
    ]
    if snapshot.latest_passing_qa_summary:
        blocks.append(bullet_block(f"QA 摘要：{snapshot.latest_passing_qa_summary}"))
    if snapshot.latest_success_run_notes:
        blocks.append(bullet_block(f"运行摘要：{snapshot.latest_success_run_notes}"))
    blocks.extend(
        [
            heading_block("当前关键边界"),
            bullet_block("不改 controller.py confirmed truth。"),
            bullet_block("不改 SimulationRunner。"),
            bullet_block("不新增另一套控制真值。"),
            bullet_block("不把 simplified plant 表述成完整实时物理模型。"),
            bullet_block("Opus 4.6 只使用 Notion + GitHub 证据面。"),
            heading_block("当前下一步"),
            bullet_block("继续收口剩余 stale wording，让 control tower summary surfaces 不再依赖手工维护。"),
            bullet_block("继续把历史 manual-browser-QA 表述降级成 presenter guidance，而不是当前审批规则。"),
            bullet_block(current_action),
            bullet_block("在 P6 收口前，不继续扩大 P7 的实现面。"),
            divider_block(),
            page_link_paragraph_block(config, "dashboard", "AI FANTUI LogicMVP 控制塔"),
            page_link_paragraph_block(config, "freeze_packet", "10 Freeze Demo Packet"),
            page_link_paragraph_block(config, "opus_brief", "09C 当前 Opus 4.6 审查简报"),
            page_link_paragraph_block(config, "constitution", "00 项目宪法"),
            paragraph_parts_block([notion_text("GitHub Repo / ai-fantui-logicmvp", config_url(config, "github_repo"))]),
            paragraph_parts_block([notion_text("GitHub Actions / GSD Automation Loop", config_url(config, "github_actions"))]),
        ]
    )
    return blocks


def render_repo_coordination_plan_markdown(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> str:
    current_action = (
        "继续自动开发；当前无需手动触发 Opus 4.6。"
        if not brief.review_required
        else "按 09C 当前审查简报手动触发 Opus 4.6。"
    )
    status_url = f"https://www.notion.so/{page_id(config, 'status')}"
    brief_url = f"https://www.notion.so/{page_id(config, 'opus_brief')}"
    freeze_url = f"https://www.notion.so/{page_id(config, 'freeze_packet')}"
    lines = [
        "## 当前自动同步快照",
        "",
        f"- 当前阶段：`{snapshot.active_phase}`",
        f"- 当前已验证 Plan：`{snapshot.latest_verified_plan}`",
        f"- 最近成功执行证据：`{snapshot.latest_success_run or '暂无'}`",
        f"- 当前 Gate：`{snapshot.gate_name} ({snapshot.gate_status})`",
        f"- 当前 Opus 状态：`{brief.intervention_kind}`",
    ]
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    lines.extend(
        [
            "- 当前结论：当前最高优先级是继续收口控制塔与 freeze/demo packet 的残余漂移，不是再加 demo 功能。",
            f"- 当前唯一人工动作：{current_action}",
            "",
            "## 当前关键边界",
            "",
            "- `controller.py` 仍然是唯一控制真值。",
            "- 不改 `SimulationRunner` 或现有 HTTP / CLI 契约。",
            "- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。",
            "- Opus 4.6 的主观审查仍然只使用 Notion + GitHub 证据面。",
            "",
            "## 当前证据入口",
            "",
            f"- {markdown_link('Notion 控制塔', config.get('root_page_url', 'https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec'))}",
        ]
    )
    if unavailable_page_keys:
        lines.append("- 单独的 status / 09C / freeze 页面当前受 Notion archived page 限制；请优先使用控制塔 dashboard 和 GitHub 证据面。")
    else:
        lines.extend(
            [
                f"- {markdown_link('01 当前状态（自动同步）', status_url)}",
                f"- {markdown_link('09C 当前 Opus 4.6 审查简报', brief_url)}",
                f"- {markdown_link('10 Freeze Demo Packet', freeze_url)}",
            ]
        )
    lines.extend(
        [
            f"- {markdown_link('GitHub Repo', config_url(config, 'github_repo'))}",
            f"- {markdown_link('GitHub Actions', config_url(config, 'github_actions'))}",
            "",
            "## 历史记录说明",
            "",
            "- 下方旧轮次记录保留作为历史快照，不再代表当前真值。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_repo_dev_handoff_markdown(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> str:
    status_url = f"https://www.notion.so/{page_id(config, 'status')}"
    brief_url = f"https://www.notion.so/{page_id(config, 'opus_brief')}"
    freeze_url = f"https://www.notion.so/{page_id(config, 'freeze_packet')}"
    lines = [
        "## 当前自动同步交接基线",
        "",
        f"- 活动 phase：`{snapshot.active_phase}`",
        f"- 当前已验证 Plan：`{snapshot.latest_verified_plan}`",
        f"- 最近成功执行证据：`{snapshot.latest_success_run or '暂无'}`",
    ]
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            "- 当前 demo 基线已经稳定，P6 的任务是把控制塔、freeze packet 和 repo-side handoff 资料统一到同一份 GitHub-backed 真值。",
            "- 当前不继续扩大 P7 的实现面；P7 groundwork 继续保留，但执行顺序仍以 P6 收口优先。",
            "",
            "## 恢复工作时先看",
            "",
            f"1. {markdown_link('AI FANTUI LogicMVP 控制塔', config.get('root_page_url', 'https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec'))}",
        ]
    )
    if unavailable_page_keys:
        lines.extend(
            [
                "2. 单独的 status / 09C / freeze 页面当前受 Notion archived page 限制；先以控制塔 dashboard 为准。",
                f"3. {markdown_link('GitHub Actions / GSD Automation Loop', config_url(config, 'github_actions'))}",
            ]
        )
    else:
        lines.extend(
            [
                f"2. {markdown_link('01 当前状态（自动同步）', status_url)}",
                f"3. {markdown_link('09C 当前 Opus 4.6 审查简报', brief_url)}",
                f"4. {markdown_link('10 Freeze Demo Packet', freeze_url)}",
                f"5. {markdown_link('GitHub Actions / GSD Automation Loop', config_url(config, 'github_actions'))}",
            ]
        )
    lines.extend(
        [
            "",
            "## 当前交接结论",
            "",
            f"- Opus 状态：`{brief.intervention_kind}`",
            "- 当前交接重点是保持 control-plane truth 收口，不是扩新功能。",
            "- 下方旧 Round 记录保留为历史上下文，不再当成当前执行指令。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_repo_qa_report_markdown(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> str:
    lines = [
        "## 当前自动同步 QA 基线",
        "",
        "- 结论：PASS；当前稳定基线由 GitHub-backed validation evidence 支撑。",
        f"- 当前阶段：`{snapshot.active_phase}`",
        f"- 当前已验证 Plan：`{snapshot.latest_verified_plan}`",
        f"- 最近成功执行证据：`{snapshot.latest_success_run or '暂无'}`",
        f"- 当前 Gate：`{snapshot.gate_name} ({snapshot.gate_status})`",
        f"- 当前 Opus 状态：`{brief.intervention_kind}`",
        f"- Open Gap 数量：`{len(snapshot.open_gap_titles)}`",
    ]
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            "- `manual browser QA` 不再是当前审批规则；相关历史记录只保留为 presenter guidance / 历史上下文。",
            "",
            "## 当前证据入口",
            "",
            f"- {markdown_link('GitHub Repo', config_url(config, 'github_repo'))}",
            f"- {markdown_link('GitHub Actions', config_url(config, 'github_actions'))}",
            f"- {markdown_link('Notion 控制塔', config.get('root_page_url', 'https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec'))}",
            "",
            "## 历史 QA 记录说明",
            "",
            "- 下方按 Round 保存的 QA 记录保留不删，但它们不是当前冻结基线。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_repo_freeze_packet_markdown(
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> str:
    status_url = f"https://www.notion.so/{page_id(config, 'status')}"
    brief_url = f"https://www.notion.so/{page_id(config, 'opus_brief')}"
    lines = [
        "## 当前自动同步冻结摘要",
        "",
        f"- 当前阶段：`{snapshot.active_phase}`",
        f"- 当前已验证 Plan：`{snapshot.latest_verified_plan}`",
        f"- 最近成功执行证据：`{snapshot.latest_success_run or '暂无'}`",
        f"- 当前 Gate：`{snapshot.gate_name} ({snapshot.gate_status})`",
        f"- 当前 Opus 状态：`{brief.intervention_kind}`",
        f"- Open Gap 数量：`{len(snapshot.open_gap_titles)}`",
    ]
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            "- 当前冻结包的职责是对齐 repo / GitHub / Notion 三个证据面，而不是继续加产品表面。",
            "",
            "## 当前冻结入口",
            "",
        ]
    )
    if unavailable_page_keys:
        lines.append("- 单独的 status / 09C 页面当前受 Notion archived page 限制；请优先使用控制塔 dashboard 和 GitHub 证据。")
    else:
        lines.extend(
            [
                f"- {markdown_link('01 当前状态（自动同步）', status_url)}",
                f"- {markdown_link('09C 当前 Opus 4.6 审查简报', brief_url)}",
            ]
        )
    lines.extend(
        [
            f"- {markdown_link('GitHub Repo', config_url(config, 'github_repo'))}",
            f"- {markdown_link('GitHub Actions', config_url(config, 'github_actions'))}",
            "",
            "## 历史正文说明",
            "",
            "- 下方正文保留为冻结说明，不再单独维护顶部状态摘要。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def managed_markdown_block(marker: str, body: str) -> str:
    return f"<!-- {marker} START -->\n{body.rstrip()}\n<!-- {marker} END -->\n"


def upsert_managed_markdown_section(existing: str, marker: str, body: str) -> str:
    start_tag = f"<!-- {marker} START -->"
    end_tag = f"<!-- {marker} END -->"
    managed = managed_markdown_block(marker, body)
    if start_tag in existing and end_tag in existing:
        before, remainder = existing.split(start_tag, 1)
        _, after = remainder.split(end_tag, 1)
        replacement = before.rstrip() + "\n\n" + managed
        if after.strip():
            replacement += "\n" + after.lstrip("\n")
        return replacement
    lines = existing.splitlines()
    if lines and lines[0].startswith("# "):
        head = "\n".join(lines[:1]).rstrip()
        tail = "\n".join(lines[1:]).lstrip("\n")
        replacement = head + "\n\n" + managed
        if tail:
            replacement += "\n" + tail
        return replacement
    return managed + ("\n" + existing.lstrip("\n") if existing.strip() else "")


def sync_repo_documents(
    cwd: Path,
    brief: CurrentReviewBrief,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> list[RepoDocSyncResult]:
    renderers = {
        "coordination_plan": (REPO_COORDINATION_PLAN_MARKER, render_repo_coordination_plan_markdown),
        "dev_handoff": (REPO_DEV_HANDOFF_MARKER, render_repo_dev_handoff_markdown),
        "qa_report": (REPO_QA_REPORT_MARKER, render_repo_qa_report_markdown),
        "freeze_packet": (REPO_FREEZE_PACKET_MARKER, render_repo_freeze_packet_markdown),
    }
    synced: list[RepoDocSyncResult] = []
    for key, relative_path in DEFAULT_REPO_DOCS.items():
        marker, renderer = renderers[key]
        path = cwd / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else f"# {relative_path.stem}\n"
        updated = upsert_managed_markdown_section(
            existing,
            marker,
            renderer(brief, snapshot, config, unavailable_page_keys=unavailable_page_keys),
        )
        path.write_text(updated, encoding="utf-8")
        synced.append(RepoDocSyncResult(path=str(path), marker=marker))
    return synced


def upsert_managed_page_section(
    client: NotionClient,
    page_id_value: str,
    blocks: list[dict[str, Any]],
    *,
    marker: str,
) -> None:
    children = client.list_block_children(page_id_value)
    start_index = None
    end_index = None
    for index, block in enumerate(children):
        if block.get("type") == "callout" and block_plain_text(block).startswith(marker):
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
        f"/v1/blocks/{page_id_value}/children",
        {"children": blocks, "position": {"type": "start"}},
    )


def upsert_dashboard_snapshot_section(
    client: NotionClient,
    dashboard_page_id: str,
    blocks: list[dict[str, Any]],
) -> None:
    upsert_managed_page_section(client, dashboard_page_id, blocks, marker=DASHBOARD_SYNC_MARKER)


def upsert_freeze_packet_snapshot_section(
    client: NotionClient,
    freeze_packet_page_id: str,
    blocks: list[dict[str, Any]],
) -> None:
    upsert_managed_page_section(client, freeze_packet_page_id, blocks, marker=FREEZE_PACKET_SYNC_MARKER)


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
    return write_current_opus_review_brief_from_snapshot(
        client,
        config,
        snapshot=snapshot,
        activate_gate=activate_gate,
    )


def write_current_opus_review_brief_from_snapshot(
    client: NotionClient,
    config: dict[str, Any],
    *,
    snapshot: ReviewSnapshot,
    activate_gate: bool,
) -> dict[str, Any]:
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
    unavailable_page_keys: list[str] = []
    if not page_is_writable(client, config, "opus_brief"):
        unavailable_page_keys.append("opus_brief")
        brief_page_id = None
    else:
        brief_page_id = page_id(config, "opus_brief")
        try:
            client.update_page_properties(brief_page_id, {"title": title_value(brief.page_title)})
            client.replace_page_body(brief_page_id, render_current_review_brief_blocks(brief, effective_snapshot, config))
        except RuntimeError as exc:
            if not (is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc))):
                raise
            unavailable_page_keys.append("opus_brief")
            brief_page_id = None
    dashboard_page_id = page_id(config, "dashboard")
    client.update_page_properties(dashboard_page_id, {"title": title_value("AI FANTUI LogicMVP 控制塔")})
    if not page_is_writable(client, config, "status"):
        unavailable_page_keys.append("status")
    if not page_is_writable(client, config, "freeze_packet"):
        unavailable_page_keys.append("freeze_packet")
    if "status" not in unavailable_page_keys:
        status_page_id = page_id(config, "status")
        try:
            client.update_page_properties(status_page_id, {"title": title_value("01 当前状态（自动同步）")})
            client.replace_page_body(status_page_id, render_status_page_blocks(brief, effective_snapshot, config))
        except RuntimeError as exc:
            if not (is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc))):
                raise
            unavailable_page_keys.append("status")
    if "freeze_packet" not in unavailable_page_keys:
        freeze_packet_page_id = page_id(config, "freeze_packet")
        try:
            client.update_page_properties(freeze_packet_page_id, {"title": title_value("10 Freeze Demo Packet")})
            client.replace_page_body(freeze_packet_page_id, render_freeze_packet_blocks(brief, effective_snapshot, config))
        except RuntimeError as exc:
            if not (is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc))):
                raise
            unavailable_page_keys.append("freeze_packet")
    client.replace_page_body(
        dashboard_page_id,
        render_dashboard_blocks(
            brief,
            effective_snapshot,
            config,
            unavailable_page_keys=tuple(unavailable_page_keys),
        ),
    )

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
        "skipped_page_keys": unavailable_page_keys,
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
    compact_success_summary = derive_compact_success_summary(results) if summary.succeeded else None

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
            "Notes": rich_text_value(compact_success_summary or summary.output_digest),
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
            "Summary": rich_text_value(f"{summary.qa_result}. {compact_success_summary}" if compact_success_summary else summary.output_digest),
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

    repo_docs_parser = subparsers.add_parser(
        "sync-repo-docs",
        help="Render the active repo-side coordination docs from the current Notion/GitHub-backed snapshot.",
    )
    repo_docs_parser.add_argument(
        "--cwd",
        default=".",
        help="Repo root whose coordination docs should be updated.",
    )
    repo_docs_parser.add_argument(
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
    elif payload.get("notion") == "partial":
        print(f"Notion writeback: partial ({payload.get('notion_error', 'database write failed')})")
    elif payload.get("notion") == "failed":
        print(f"Notion writeback: failed ({payload.get('notion_error', 'unknown error')})")
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


def output_repo_doc_sync_result(format_name: str, payload: dict[str, Any]) -> None:
    if format_name == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"Repo doc sync phase: {payload['active_phase']}")
    print(f"Latest verified plan: {payload['latest_verified_plan']}")
    print(f"Current Opus state: {payload['intervention_kind']}")
    print("Updated files:")
    for item in payload["files"]:
        print(f"- {item['path']}")


def handle_run(args: argparse.Namespace, config: dict[str, Any]) -> int:
    cwd = Path(args.cwd).resolve()
    config_path = Path(getattr(args, "config", DEFAULT_CONFIG_PATH))
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
        try:
            client = NotionClient(token)
            ensure_live_active_pages(client, config, config_path=config_path)
            written = write_notion_outcome(
                client,
                config,
                title=title,
                plan_id=plan_id,
                commands=args.command,
                results=results,
                summary=summary,
                opus_gate=args.opus_gate,
            )
        except Exception as exc:
            payload["notion"] = "failed"
            payload["notion_error"] = str(exc)
            if summary.succeeded:
                try:
                    fallback_snapshot = build_fallback_run_snapshot(
                        client,
                        config,
                        cwd=cwd,
                        plan_id=plan_id,
                        title=title,
                        results=results,
                        summary=summary,
                    )
                    payload["opus_review_brief"] = write_current_opus_review_brief_from_snapshot(
                        client,
                        config,
                        snapshot=fallback_snapshot,
                        activate_gate=False,
                    )
                except Exception as fallback_exc:
                    payload["notion_fallback"] = "failed"
                    payload["notion_fallback_error"] = str(fallback_exc)
                else:
                    payload["notion"] = "partial"
                    payload["notion_fallback"] = "written"
        else:
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
    config_path = Path(getattr(args, "config", DEFAULT_CONFIG_PATH))
    client = NotionClient(token)
    try:
        snapshot = fetch_review_snapshot(client, config)
    except RuntimeError as exc:
        if not is_missing_database_error(str(exc)):
            raise
        try:
            snapshot = fetch_review_snapshot_from_pages(client, config)
        except RuntimeError as page_exc:
            if not is_missing_page_error(str(page_exc)):
                raise
            snapshot = fetch_review_snapshot_from_repo_docs(Path.cwd().resolve(), config)
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
        replacements = ensure_live_active_pages(client, config, config_path=config_path)
        if replacements:
            payload["replaced_pages"] = replacements
        payload["notion"] = write_current_opus_review_brief_from_snapshot(
            client,
            config,
            snapshot=effective_snapshot,
            activate_gate=args.activate_gate,
        )
    output_review_result(args.format, payload)
    return 0


def handle_sync_repo_docs(args: argparse.Namespace, config: dict[str, Any]) -> int:
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("NOTION_API_KEY is required for sync-repo-docs.")
    client = NotionClient(token)
    snapshot: ReviewSnapshot | None = None
    try:
        snapshot = fetch_review_snapshot(client, config)
    except RuntimeError as exc:
        if not is_missing_database_error(str(exc)):
            raise
        snapshot = None
        for fetcher in (fetch_review_snapshot_from_pages, fetch_review_snapshot_from_dashboard_page):
            try:
                snapshot = fetcher(client, config)
                break
            except RuntimeError as page_exc:
                if not is_missing_page_error(str(page_exc)):
                    raise
        if snapshot is None:
            snapshot = fetch_review_snapshot_from_repo_docs(Path(args.cwd).resolve(), config)
    else:
        page_snapshot = None
        for fetcher in (fetch_review_snapshot_from_pages, fetch_review_snapshot_from_dashboard_page):
            try:
                page_snapshot = fetcher(client, config)
                break
            except RuntimeError as page_exc:
                if not is_missing_page_error(str(page_exc)):
                    raise
        if page_snapshot and should_prefer_page_snapshot(snapshot, page_snapshot, config):
            snapshot = page_snapshot
    brief = build_current_review_brief(snapshot, config)
    unavailable_page_keys = active_page_unavailable_keys(client, config)
    synced = sync_repo_documents(
        Path(args.cwd).resolve(),
        brief,
        snapshot,
        config,
        unavailable_page_keys=unavailable_page_keys,
    )
    payload = {
        "active_phase": snapshot.active_phase,
        "latest_verified_plan": snapshot.latest_verified_plan,
        "latest_success_run": snapshot.latest_success_run,
        "intervention_kind": brief.intervention_kind,
        "files": [{"path": item.path, "marker": item.marker} for item in synced],
    }
    output_repo_doc_sync_result(args.format, payload)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_control_plane_config(Path(args.config))
    if args.command_name == "run":
        return handle_run(args, config)
    if args.command_name == "prepare-opus-review":
        return handle_prepare_opus_review(args, config)
    if args.command_name == "sync-repo-docs":
        return handle_sync_repo_docs(args, config)
    parser.error(f"Unsupported command: {args.command_name}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

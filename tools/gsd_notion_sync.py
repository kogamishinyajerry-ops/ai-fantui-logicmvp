"""Run GSD validation commands and mirror outcomes into the Notion control plane.

This script intentionally uses only the Python standard library so it can run
locally and in GitHub Actions without adding runtime dependencies.
"""

from __future__ import annotations

import argparse
import contextlib
import http.client
import json
import os
import re
import signal
import subprocess
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NOTION_VERSION = "2022-06-28"
DEFAULT_CONFIG_PATH = Path(".planning/notion_control_plane.json")
TEXT_LIMIT = 1800
DEFAULT_NOTION_WRITEBACK_TIMEOUT_S = "60"
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
REPO_QA_HISTORY_DOCS = (
    Path("docs/freeze/2026-04-10-freeze-demo-packet.md"),
    Path("docs/freeze/archive/2026-04-10-freeze-demo-packet-history.md"),
    Path("docs/freeze/2026-04-09-freeze-snapshot.md"),
    Path("docs/coordination/qa_report.md"),
    Path("docs/coordination/archive/qa-report-history.md"),
)
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
# Fallback page IDs used only when notion_control_plane.json is absent or lacks a key.
# At runtime load_control_plane_config() uses setdefault(), so the JSON config always wins
# for any key it already defines. Drift between these values and the JSON config is a
# maintenance risk (stale fallbacks) but does NOT cause live writes to wrong pages during
# normal operation. Keep in sync with .planning/notion_control_plane.json pages section.
DEFAULT_PAGES = {
    "dashboard": "33cc6894-2bed-8136-b5c9-f9ba5b4b44ec",
    "constitution": "33cc6894-2bed-8148-b2c5-ec68c440f5ef",
    "status": "33fc6894-2bed-814f-b62a-e30a490f0041",
    "control_plane": "33cc6894-2bed-810d-875e-e4e0e464ee31",
    "opus_protocol": "33cc6894-2bed-8117-b8f5-eda203f3be18",
    "opus_brief": "33fc6894-2bed-81fd-b82d-e44b9988d1a4",
    "freeze_packet": "33fc6894-2bed-8182-81cf-ec90266f7596",
}
ACTIVE_SYNC_PAGE_TITLES = {
    "status": "01 当前状态（自动同步）",
    "opus_brief": "09C 当前 Opus 4.6 审查简报",
    "freeze_packet": "10 Freeze Demo Packet",
}
PRESERVED_CHILD_BLOCK_TYPES = {"child_page", "child_database"}
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
PHASE_HEADER_RE = re.compile(r"^## Phase P(\d+):\s+(.+)$")
PLAN_TITLE_RE = re.compile(r"^#\s*(P\d+-\d+)\s+Plan\s*-\s*(.+)$")
PHASE_STATUS_LINE_RE = re.compile(r"^Status:\s+(.+)$", re.IGNORECASE)
DONE_PHASE_STATUS_PREFIXES = (
    "done",
    "closed",
    "lifted",
    "executor 初审完成",
)
PLAN_FRONT_MATTER_ID_RE = re.compile(r"^plan:\s*(P\d+(?:-[A-Z0-9]+)+)\s*$", re.IGNORECASE)
PLAN_FRONT_MATTER_TITLE_RE = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)


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
    evidence_mode: str = "database_live"
    evidence_note: str | None = None


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


class NotionWritebackTimeout(RuntimeError):
    pass


def notion_http_timeout_s() -> float:
    return float(os.environ.get("NOTION_HTTP_TIMEOUT_S", "12"))


class NotionClient:
    def __init__(self, token: str, *, timeout: float | None = None):
        self.token = token
        self.timeout = timeout or notion_http_timeout_s()
        self._connection: http.client.HTTPSConnection | None = None

    def close(self) -> None:
        # Connection is per-request now; nothing to pool-close.
        pass

    def _new_connection(self) -> http.client.HTTPSConnection:
        return http.client.HTTPSConnection("api.notion.com", timeout=self.timeout)

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }
        for attempt in range(2):
            connection = self._new_connection()
            try:
                connection.request(method, path, body=body, headers=headers)
                response = connection.getresponse()
                raw = response.read()
                text = raw.decode("utf-8", "replace")
                connection.close()
                if 200 <= response.status < 300:
                    if not text.strip():
                        return {}
                    return json.loads(text)
                raise RuntimeError(f"Notion API request failed: HTTP {response.status} {path}: {text}")
            except (http.client.HTTPException, OSError, ssl.SSLError) as error:
                with contextlib.suppress(Exception):
                    connection.close()
                if attempt == 0:
                    continue
                raise RuntimeError(f"Notion API request failed: network error {path}: {error}") from error
            finally:
                with contextlib.suppress(Exception):
                    connection.close()

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
        # Preserve embedded child pages/databases on hub pages such as the root
        # dashboard; we only rebuild the writable narrative blocks around them.
        existing_blocks = [
            block
            for block in self.list_block_children(page_id)
            if not block.get("archived")
            and not block.get("in_trash")
            and block.get("type") not in PRESERVED_CHILD_BLOCK_TYPES
        ]
        if update_page_body_blocks_in_place(self, existing_blocks, blocks):
            return
        for block in existing_blocks:
            delete_block_if_present(self, block["id"])
        if blocks:
            self.request(
                "PATCH",
                f"/v1/blocks/{page_id}/children",
                {"children": blocks, "position": {"type": "start"}},
            )


# ---------------------------------------------------------------------------
# Phase-lifecycle helpers: sync ROADMAP.md phases <-> Roadmap DB
# ---------------------------------------------------------------------------


def get_roadmap_db_id(config: dict[str, Any]) -> str:
    """Return the Roadmap database ID from the control-plane config."""
    return config.get("databases", {}).get("roadmap", "")


def register_phase_if_missing(
    client: NotionClient,
    config: dict[str, Any],
    phase_id: str,
    phase_name: str,
    goal: str,
    status: str = "Active",
) -> bool:
    """Upsert a Phase entry in the Roadmap DB. Returns True if a new entry was created."""
    roadmap_db = get_roadmap_db_id(config)
    if not roadmap_db:
        return False
    rows = client.query_database(roadmap_db, page_size=100)
    # Index existing rows by Round title (match by prefix)
    existing: dict[str, tuple[str, str]] = {}
    for row in rows:
        props = row.get("properties", {})
        round_names = [t.get("plain_text", "") for t in props.get("Round", {}).get("title", [])]
        current_status = (props.get("Status", {}).get("select") or {}).get("name", "")
        for rn in round_names:
            existing[rn] = (row["id"], current_status)
    # Already registered?
    if phase_id in existing:
        return False
    client.request(
        "POST",
        "/v1/pages",
        {
            "parent": {"database_id": roadmap_db},
            "properties": {
                "Round": title_value(phase_id),
                "Status": select_value(status),
                "Goal": rich_text_value(goal[:500]),
            },
        },
    )
    return True


def close_phase_in_roadmap(
    client: NotionClient,
    config: dict[str, Any],
    phase_id: str,
) -> bool:
    """Find a phase by ID prefix in the Roadmap DB and update its Status to Done. Returns True if updated."""
    roadmap_db = get_roadmap_db_id(config)
    if not roadmap_db:
        return False
    rows = client.query_database(roadmap_db, page_size=100)
    for row in rows:
        props = row.get("properties", {})
        round_names = [t.get("plain_text", "") for t in props.get("Round", {}).get("title", [])]
        current_status = (props.get("Status", {}).get("select") or {}).get("name", "")
        for rn in round_names:
            if rn.startswith(phase_id) and current_status not in ("Done", "Deprecated"):
                client.update_page_properties(row["id"], {"Status": select_value("Done")})
                return True
    return False


def sync_roadmap_phases(
    config: dict[str, Any],
    roadmap_path: Path | None = None,
) -> dict[str, Any]:
    """Main entry point: read ROADMAP.md, sync Active/Done phases to Notion Roadmap DB.

    Returns a summary dict with keys: registered (list), closed (list), errors (list).
    """
    if not os.environ.get("NOTION_API_KEY"):
        return {"registered": [], "closed": [], "errors": ["NOTION_API_KEY not set"]}

    roadmap_path = roadmap_path or Path(".planning/ROADMAP.md")
    if not roadmap_path.exists():
        return {"registered": [], "closed": [], "errors": [f"{roadmap_path} not found"]}

    token = os.environ["NOTION_API_KEY"]
    client = NotionClient(token)
    result: dict[str, Any] = {"registered": [], "closed": [], "errors": []}

    try:
        md_text = roadmap_path.read_text(encoding="utf-8")
        lines = md_text.splitlines()

        # Parse phases: find "## Phase P{n}:" blocks and their Status line
        phases: list[dict[str, str]] = []
        i = 0
        while i < len(lines):
            m = PHASE_HEADER_RE.match(lines[i])
            if m:
                phase_num = m.group(1)
                phase_id = f"P{phase_num}"
                phase_name = m.group(2).strip()
                goal = ""
                status: str | None = None
                # Scan subsequent lines for Status and Goal
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## Phase "):
                    parsed_status = phase_status_from_line(lines[j])
                    if parsed_status:
                        status = parsed_status
                    if lines[j].startswith("Goal:"):
                        goal = lines[j][5:].strip()
                    j += 1
                phases.append({"id": phase_id, "name": phase_name, "goal": goal, "status": status or ""})
                i = j
            else:
                i += 1

        for phase in phases:
            phase_id = phase["id"]
            phase_name = phase["name"]
            goal = phase["goal"]
            status = phase["status"]

            if status == "Active":
                try:
                    created = register_phase_if_missing(client, config, phase_id, phase_name, goal, status)
                    if created:
                        result["registered"].append(phase_id)
                    else:
                        result.setdefault("already_registered", []).append(phase_id)
                except Exception as exc:  # pragma: no cover - network errors
                    result["errors"].append(f"register {phase_id}: {exc}")

            elif status == "Done":
                try:
                    closed = close_phase_in_roadmap(client, config, phase_id)
                    if closed:
                        result["closed"].append(phase_id)
                except Exception as exc:  # pragma: no cover - network errors
                    result["errors"].append(f"close {phase_id}: {exc}")

    finally:
        client.close()

    return result


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
    return "".join(
        item.get("plain_text") or item.get("text", {}).get("content", "")
        for item in rich
        if isinstance(item, dict)
    )


def rich_text_item_link(item: dict[str, Any]) -> str | None:
    href = item.get("href")
    if href:
        return href
    text = item.get("text")
    if not isinstance(text, dict):
        return None
    link = text.get("link")
    if not isinstance(link, dict):
        return None
    return link.get("url")


def block_render_signature(block: dict[str, Any]) -> tuple[str, tuple[tuple[str, str | None], ...]] | None:
    block_type = block.get("type")
    if not block_type:
        return None
    payload = block.get(block_type, {})
    if not isinstance(payload, dict):
        return None
    rich = payload.get("rich_text", [])
    if not isinstance(rich, list):
        return None
    signature = tuple(
        (
            item.get("plain_text") or item.get("text", {}).get("content", ""),
            rich_text_item_link(item),
        )
        for item in rich
        if isinstance(item, dict)
    )
    return (block_type, signature)


def block_patch_payload(block: dict[str, Any]) -> dict[str, Any] | None:
    block_type = block.get("type")
    if block_type in {"paragraph", "heading_2", "bulleted_list_item", "numbered_list_item"}:
        payload = block.get(block_type)
        if isinstance(payload, dict):
            return {block_type: {"rich_text": payload.get("rich_text", [])}}
        return None
    if block_type == "callout":
        payload = block.get("callout")
        if not isinstance(payload, dict):
            return None
        callout_payload: dict[str, Any] = {"rich_text": payload.get("rich_text", [])}
        if "icon" in payload:
            callout_payload["icon"] = payload["icon"]
        return {"callout": callout_payload}
    if block_type == "divider":
        return {"divider": {}}
    return None


def block_patch_signature(block: dict[str, Any]) -> tuple[str, tuple[Any, ...]] | None:
    block_type = block.get("type")
    if not block_type:
        return None
    if block_type in {"paragraph", "heading_2", "bulleted_list_item", "numbered_list_item"}:
        payload = block.get(block_type)
        if not isinstance(payload, dict):
            return None
        return (block_type, block_render_signature(block))
    if block_type == "callout":
        payload = block.get("callout", {})
        if not isinstance(payload, dict):
            return None
        icon = payload.get("icon")
        icon_signature: tuple[str, str] | None = None
        if isinstance(icon, dict):
            if icon.get("type") == "emoji" and icon.get("emoji"):
                icon_signature = ("emoji", icon["emoji"])
            elif icon.get("type") == "external":
                external = icon.get("external") or {}
                if external.get("url"):
                    icon_signature = ("external", external["url"])
        return (block_type, block_render_signature(block), icon_signature)
    if block_type == "divider":
        return (block_type, ())
    return None


def update_page_body_blocks_in_place(
    client: NotionClient,
    existing_blocks: list[dict[str, Any]],
    new_blocks: list[dict[str, Any]],
) -> bool:
    if len(existing_blocks) != len(new_blocks):
        return False
    existing_types = [block.get("type") for block in existing_blocks]
    new_types = [block.get("type") for block in new_blocks]
    if existing_types != new_types:
        return False
    patch_payloads = [block_patch_payload(block) for block in new_blocks]
    if any(payload is None for payload in patch_payloads):
        return False
    existing_signatures = [block_patch_signature(block) for block in existing_blocks]
    new_signatures = [block_patch_signature(block) for block in new_blocks]
    if any(signature is None for signature in existing_signatures + new_signatures):
        return False
    for existing_block, signature, payload in zip(existing_blocks, new_signatures, patch_payloads):
        if block_patch_signature(existing_block) == signature:
            continue
        client.request("PATCH", f"/v1/blocks/{existing_block['id']}", payload)
    return True


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


def active_phase_number_from_roadmap(cwd: Path) -> int | None:
    roadmap_path = cwd / ".planning" / "ROADMAP.md"
    if not roadmap_path.exists():
        return None
    current_phase_number: int | None = None
    for raw_line in roadmap_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = PHASE_HEADER_RE.match(line)
        if match:
            current_phase_number = int(match.group(1))
            continue
        if current_phase_number is not None and phase_status_from_line(line) == "Active":
            return current_phase_number
    return None


def active_phase_label_from_roadmap(cwd: Path) -> str | None:
    roadmap_path = cwd / ".planning" / "ROADMAP.md"
    if not roadmap_path.exists():
        return None
    current_phase_label: str | None = None
    for raw_line in roadmap_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = PHASE_HEADER_RE.match(line)
        if match:
            current_phase_label = f"P{match.group(1)} {match.group(2).strip()}"
            continue
        if current_phase_label is not None and phase_status_from_line(line) == "Active":
            return current_phase_label
    return None


def latest_phase_number_from_roadmap(cwd: Path) -> int | None:
    roadmap_path = cwd / ".planning" / "ROADMAP.md"
    if not roadmap_path.exists():
        return None
    latest_phase_number: int | None = None
    for raw_line in roadmap_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = PHASE_HEADER_RE.match(line)
        if match:
            latest_phase_number = int(match.group(1))
    return latest_phase_number


def latest_phase_label_from_roadmap(cwd: Path) -> str | None:
    roadmap_path = cwd / ".planning" / "ROADMAP.md"
    if not roadmap_path.exists():
        return None
    latest_phase_label: str | None = None
    for raw_line in roadmap_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = PHASE_HEADER_RE.match(line)
        if match:
            latest_phase_label = f"P{match.group(1)} {match.group(2).strip()}"
    return latest_phase_label


def current_phase_number_from_roadmap(cwd: Path) -> int | None:
    return active_phase_number_from_roadmap(cwd) or latest_phase_number_from_roadmap(cwd)


def current_phase_label_from_roadmap(cwd: Path) -> str | None:
    return active_phase_label_from_roadmap(cwd) or latest_phase_label_from_roadmap(cwd)


def phase_directory(cwd: Path, phase_number: int) -> Path | None:
    phases_root = cwd / ".planning" / "phases"
    if not phases_root.exists():
        return None
    prefixes = (
        f"{phase_number:02d}-",
        f"P{phase_number}-",
        f"P{phase_number:02d}-",
    )
    candidates = sorted(
        path
        for path in phases_root.iterdir()
        if path.is_dir() and any(path.name.startswith(prefix) for prefix in prefixes)
    )
    return candidates[0] if candidates else None


def local_phase_default_plan(cwd: Path) -> str | None:
    phase_number = current_phase_number_from_roadmap(cwd)
    if phase_number is None:
        return None
    phase_dir = phase_directory(cwd, phase_number)
    if phase_dir is None:
        return None
    plan_files = sorted(phase_dir.glob("*-PLAN.md"))
    if not plan_files:
        return None
    for plan_path in reversed(plan_files):
        plan_title = plan_display_title_from_file(plan_path)
        if plan_title:
            return plan_title
    return None


def effective_default_plan(config: dict[str, Any], *, cwd: Path | None = None) -> str:
    repo_cwd = cwd or Path.cwd()
    return local_phase_default_plan(repo_cwd) or config.get("default_plan", "P1-01 建立自动执行 / QA 回写闭环")


def normalize_phase_status(raw_status: str) -> str | None:
    status = raw_status.strip()
    if not status:
        return None
    lowered = status.casefold()
    if lowered.startswith("active"):
        return "Active"
    if lowered.startswith("deprecated"):
        return "Deprecated"
    if any(lowered.startswith(prefix) for prefix in DONE_PHASE_STATUS_PREFIXES):
        return "Done"
    return None


def phase_status_from_line(line: str) -> str | None:
    match = PHASE_STATUS_LINE_RE.match(line.strip())
    if not match:
        return None
    return normalize_phase_status(match.group(1))


def plan_display_title_from_file(path: Path) -> str | None:
    plan_id: str | None = None
    title: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines()[:40]:
        line = raw_line.strip()
        match = PLAN_TITLE_RE.match(line)
        if match:
            return f"{match.group(1)} {match.group(2).strip()}"
        plan_match = PLAN_FRONT_MATTER_ID_RE.match(line)
        if plan_match:
            plan_id = plan_match.group(1).strip()
        title_match = PLAN_FRONT_MATTER_TITLE_RE.match(line)
        if title_match:
            title = title_match.group(1).strip()
        if plan_id and title:
            return f"{plan_id} {title}"
    return None


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


def repo_blob_url(config: dict[str, Any], repo_relative_path: str) -> str:
    return f"{config_url(config, 'github_repo')}/blob/main/{repo_relative_path}"


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


def is_rate_limited_error(message: str) -> bool:
    lowered = message.lower()
    return "http 429" in lowered or "rate_limited" in lowered or "rate limited" in lowered


def delete_block_if_present(client: NotionClient, block_id: str) -> None:
    try:
        client.request("DELETE", f"/v1/blocks/{block_id}")
    except RuntimeError as exc:
        if is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc)):
            return
        raise


def archive_page_if_present(client: NotionClient, page_id_value: str) -> None:
    try:
        client.archive_page(page_id_value)
    except RuntimeError as exc:
        if is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc)):
            return
        raise


def _check_page_live(
    client: NotionClient,
    key: str,
    current_id: str,
) -> tuple[str, str, bool] | None:
    """Check if a page is live. Returns (key, id, needs_replacement) or None if page is live."""
    try:
        page = client.get_page(current_id)
    except RuntimeError as exc:
        if not is_missing_page_error(str(exc)):
            raise
        page = {"archived": True, "in_trash": True}
    if not page.get("archived") and not page.get("in_trash"):
        return None  # Page is live, no action needed
    return (key, current_id, True)


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

    # Phase 1: parallel GET for all pages to check live status
    pages_to_check: list[tuple[str, str, str]] = []  # (key, title, current_id)
    for key, title in ACTIVE_SYNC_PAGE_TITLES.items():
        if key not in pages:
            continue
        pages_to_check.append((key, title, page_id(config, key)))

    if pages_to_check:
        needs_replacement: list[tuple[str, str, str]] = []
        # Sequential check: preserves deterministic ordering so Phase 2
        # assignments match the needs_replacement list order.
        # (Archived pages are rare; parallelism here adds no meaningful benefit.)
        for key, title, current_id in pages_to_check:
            result = _check_page_live(client, key, current_id)
            if result is not None:
                needs_replacement.append((key, title, current_id))

        # Phase 2: sequential replacement for pages that need it (rare, config writes)
        for key, title, current_id in needs_replacement:
            replacement_id = client.create_child_page(page_id(config, "dashboard"), title)
            replacement_page = client.get_page(replacement_id)
            if replacement_page.get("archived") or replacement_page.get("in_trash"):
                continue
            config["pages"][key] = replacement_id
            replacements[key] = {"old_id": current_id, "new_id": replacement_id}

    if replacements:
        save_control_plane_config(config_path, config)
    return replacements


def _ensure_live_single_database(
    client: NotionClient,
    key: str,
    database_id_value: str,
) -> tuple[str, str] | None:
    """Check and restore a single database. Returns (key, id) if restored, None otherwise."""
    try:
        block = client.request("GET", f"/v1/blocks/{database_id_value}")
    except RuntimeError as exc:
        if is_missing_database_error(str(exc)) or is_missing_page_error(str(exc)):
            return None
        raise
    if not block.get("archived") and not block.get("in_trash"):
        return None
    restored_block = client.request(
        "PATCH",
        f"/v1/blocks/{database_id_value}",
        {"archived": False},
    )
    if restored_block.get("archived") or restored_block.get("in_trash"):
        return None
    return (key, database_id_value)


def ensure_live_databases(
    client: NotionClient,
    config: dict[str, Any],
) -> dict[str, str]:
    databases = config.get("databases", {})
    if not databases:
        return {}
    restored: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=min(len(databases), 8)) as executor:
        futures = {
            executor.submit(_ensure_live_single_database, client, key, db_id): key
            for key, db_id in databases.items()
        }
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                restored[result[0]] = result[1]
    return restored


def replace_active_sync_page(
    client: NotionClient,
    config: dict[str, Any],
    *,
    key: str,
    title: str,
    blocks: list[dict[str, Any]],
    config_path: Path | None = None,
) -> str:
    previous_id = config.get("pages", {}).get(key)
    if previous_id:
        try:
            page = client.get_page(previous_id)
            if not page.get("archived") and not page.get("in_trash"):
                if page_matches_rendered_blocks(client, previous_id, blocks):
                    return previous_id
                try:
                    rewrite_active_sync_page_body(
                        client,
                        previous_id,
                        title=title,
                        blocks=blocks,
                    )
                except NotionWritebackTimeout:
                    pass
                else:
                    return previous_id
        except RuntimeError as exc:
            if not is_missing_page_error(str(exc)):
                raise
    new_id = client.create_child_page(page_id(config, "dashboard"), title)
    if blocks:
        client.request(
            "PATCH",
            f"/v1/blocks/{new_id}/children",
            {"children": blocks, "position": {"type": "start"}},
        )
    config["pages"][key] = new_id
    if config_path is not None:
        save_control_plane_config(config_path, config)
    if previous_id and previous_id != new_id:
        try:
            page = client.get_page(previous_id)
        except RuntimeError as exc:
            if not is_missing_page_error(str(exc)):
                raise
        else:
            if not page.get("archived") and not page.get("in_trash"):
                archive_page_if_present(client, previous_id)
    return new_id


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


def rewrite_active_sync_page_body(
    client: NotionClient,
    page_id_value: str,
    *,
    title: str,
    blocks: list[dict[str, Any]],
) -> None:
    client.update_page_properties(page_id_value, {"title": title_value(title)})
    client.replace_page_body(page_id_value, blocks)


@contextlib.contextmanager
def notion_writeback_deadline(seconds: float | None):
    if not seconds or seconds <= 0 or not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        yield
        return

    def _raise_timeout(_signum, _frame):
        raise NotionWritebackTimeout(f"Notion writeback exceeded {seconds:g}s deadline.")

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


def prune_stale_active_sync_page_blocks(client: NotionClient, config: dict[str, Any]) -> list[str]:
    if "dashboard" not in config.get("pages", {}):
        return []
    current_page_ids = {
        page_id(config, key)
        for key in ACTIVE_SYNC_PAGE_TITLES
        if key in config.get("pages", {})
    }
    active_titles = set(ACTIVE_SYNC_PAGE_TITLES.values())
    deleted_block_ids: list[str] = []
    for block in client.list_block_children(page_id(config, "dashboard")):
        if block.get("archived") or block.get("in_trash"):
            continue
        if block.get("type") != "child_page":
            continue
        child_page = block.get("child_page") or {}
        if child_page.get("title") not in active_titles:
            continue
        if block["id"] in current_page_ids:
            continue
        delete_block_if_present(client, block["id"])
        deleted_block_ids.append(block["id"])
    return deleted_block_ids


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
    shared_check_count: int | None = None

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
        if "run_gsd_validation_suite.py" in result.command and result.stdout.strip():
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                continue
            command_count = payload.get("command_count")
            if isinstance(command_count, int) and command_count > 0:
                shared_check_count = command_count
            for entry in payload.get("results", []):
                if not isinstance(entry, dict):
                    continue
                name = entry.get("name")
                command = entry.get("command", "")
                stdout = entry.get("stdout", "")
                stderr = entry.get("stderr", "")
                if name == "unit_tests" or "unittest discover" in command:
                    match = re.search(r"Ran\s+(\d+)\s+tests", stderr)
                    if match:
                        tests_ok = int(match.group(1))
                if name == "demo_path_smoke" or "demo_path_smoke.py" in command:
                    try:
                        smoke_payload = json.loads(stdout)
                    except json.JSONDecodeError:
                        continue
                    completed = smoke_payload.get("completed_scenarios")
                    if isinstance(completed, int):
                        demo_smoke_count = completed

    fragments: list[str] = []
    if tests_ok is not None:
        fragments.append(f"{tests_ok} tests OK")
    if demo_smoke_count is not None:
        fragments.append(f"{demo_smoke_count} demo smoke scenarios pass")
    check_count = shared_check_count or len(results)
    fragments.append(f"{check_count}/{check_count} shared validation checks pass")
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
    if tests_ok is None:
        tests_match = re.search(r"(\d+)\s+tests OK", text)
        if tests_match:
            tests_ok = int(tests_match.group(1))
    smoke_match = re.search(r'"completed_scenarios"\s*:\s*(\d+)', text)
    if smoke_match:
        demo_smoke_count = int(smoke_match.group(1))
    if demo_smoke_count is None:
        smoke_match = re.search(r'\\"completed_scenarios\\"\s*:\s*(\d+)', text)
        if smoke_match:
            demo_smoke_count = int(smoke_match.group(1))
    if demo_smoke_count is None:
        smoke_match = re.search(r"(\d+)\s+demo smoke scenarios pass", text)
        if smoke_match:
            demo_smoke_count = int(smoke_match.group(1))
    if demo_smoke_count is None:
        smoke_match = re.search(r"(\d+)\s+scenarios pass", text)
        if smoke_match:
            demo_smoke_count = int(smoke_match.group(1))
    checks_match = re.search(r'"command_count"\s*:\s*(\d+)', text)
    if checks_match:
        shared_check_count = int(checks_match.group(1))
    if shared_check_count is None:
        checks_match = re.search(r"(\d+)/\1\s+shared validation checks pass", text)
        if checks_match:
            shared_check_count = int(checks_match.group(1))
    if shared_check_count is None:
        checks_match = re.search(r"(\d+)\s*/\s*(\d+)\s+pass", text)
        if checks_match and checks_match.group(1) == checks_match.group(2):
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


def success_summary_metrics(summary: str | None) -> tuple[int, int, int]:
    if not summary:
        return (0, 0, 0)
    tests_ok = 0
    demo_smoke_count = 0
    shared_check_count = 0

    tests_match = re.search(r"(\d+)\s+tests OK", summary)
    if tests_match:
        tests_ok = int(tests_match.group(1))
    smoke_match = re.search(r"(\d+)\s+demo smoke scenarios pass", summary)
    if smoke_match:
        demo_smoke_count = int(smoke_match.group(1))
    else:
        smoke_match = re.search(r"(\d+)\s+scenarios pass", summary)
        if smoke_match:
            demo_smoke_count = int(smoke_match.group(1))
    checks_match = re.search(r"(\d+)/\1\s+shared validation checks pass", summary)
    if checks_match:
        shared_check_count = int(checks_match.group(1))
    else:
        checks_match = re.search(r"(\d+)\s*/\s*(\d+)\s+pass", summary)
        if checks_match and checks_match.group(1) == checks_match.group(2):
            shared_check_count = int(checks_match.group(1))
    return tests_ok, demo_smoke_count, shared_check_count


def stronger_success_summary(*summaries: str | None) -> str | None:
    best_summary: str | None = None
    best_metrics = (0, 0, 0)
    for summary in summaries:
        metrics = success_summary_metrics(summary)
        if metrics > best_metrics:
            best_summary = summary
            best_metrics = metrics
    return best_summary


def compact_notion_run_notes(text: str | None) -> str | None:
    if not text:
        return None
    compact = derive_compact_success_summary_from_text(text)
    return compact or text


def compact_notion_qa_summary(text: str | None) -> str | None:
    if not text:
        return None
    compact = derive_compact_success_summary_from_text(text)
    if compact:
        return f"PASS. {compact}"
    return text


def strongest_repo_success_summary(cwd: Path, *seed_summaries: str | None) -> str | None:
    best_summary = stronger_success_summary(*seed_summaries)
    for relative_path in REPO_QA_HISTORY_DOCS:
        path = cwd / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        candidate = derive_compact_success_summary_from_text(text)
        best_summary = stronger_success_summary(best_summary, candidate)
    return best_summary


def should_preserve_prior_success_summary(current_summary: str | None, prior_summary: str | None) -> bool:
    if not current_summary or not prior_summary:
        return False
    return success_summary_metrics(prior_summary) > success_summary_metrics(current_summary)


def select_success_snapshot_evidence(
    snapshot: ReviewSnapshot,
    title: str,
    results: list[CommandResult],
    summary: RunSummary,
) -> tuple[str | None, str | None, str | None]:
    compact_success = derive_compact_success_summary(results)
    current_run_notes = compact_success or summary.output_digest
    current_qa_summary = f"{summary.qa_result}. {compact_success}" if compact_success else summary.output_digest
    current_passing_qa = f"{title} QA"

    if should_preserve_prior_success_summary(current_qa_summary, snapshot.latest_passing_qa_summary):
        carried_summary = snapshot.latest_passing_qa_summary
        carried_detail = carried_summary.removeprefix("PASS. ").strip() if carried_summary else ""
        current_run_notes = (
            "Focused control-plane maintenance run passed. "
            f"Carried forward the stronger shared validation baseline: {carried_detail}"
        )
        current_qa_summary = carried_summary
        current_passing_qa = snapshot.latest_passing_qa

    return current_run_notes, current_qa_summary, current_passing_qa


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


def row_last_edited_time(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    value = row.get("last_edited_time")
    return value if isinstance(value, str) else ""


def prefer_fresher_row(preferred_row: dict[str, Any] | None, candidate_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if preferred_row is None:
        return candidate_row
    if candidate_row is None:
        return preferred_row
    preferred_stamp = row_last_edited_time(preferred_row)
    candidate_stamp = row_last_edited_time(candidate_row)
    if preferred_stamp and candidate_stamp and candidate_stamp > preferred_stamp:
        return candidate_row
    return preferred_row


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
    latest_success_run_row = first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={"property": "Status", "select": {"equals": "Succeeded"}},
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
            page_size=1,
        )
    )
    latest_failed_run_row = first_row(
        client.query_database(
            database_id(config, "runs"),
            filter_payload={"property": "Status", "select": {"equals": "Failed"}},
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
    success_run_row = prefer_fresher_row(github_success_run_row, latest_success_run_row)
    failed_run_row = prefer_fresher_row(github_failed_run_row, latest_failed_run_row)
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
        latest_success_run_notes=compact_notion_run_notes(row_text(success_run_row, "Notes")),
        latest_passing_qa_summary=compact_notion_qa_summary(row_text(passing_qa_row, "Summary")),
        evidence_mode="database_live",
        evidence_note="共享 Notion 数据库可达；phase / run / QA / gate 取自实时数据库记录。",
    )


def page_text_lines(client: NotionClient, page_id_value: str) -> list[str]:
    return [
        text.strip()
        for block in client.list_block_children(page_id_value)
        if block.get("type") not in PRESERVED_CHILD_BLOCK_TYPES and (text := block_plain_text(block).strip())
    ]


def rendered_block_text_lines(blocks: list[dict[str, Any]]) -> list[str]:
    return [text.strip() for block in blocks if (text := block_plain_text(block).strip())]


def page_render_signatures(client: NotionClient, page_id_value: str) -> list[tuple[str, tuple[tuple[str, str | None], ...]]]:
    return [
        signature
        for block in client.list_block_children(page_id_value)
        if block.get("type") not in PRESERVED_CHILD_BLOCK_TYPES and (signature := block_render_signature(block)) is not None
    ]


def rendered_block_signatures(blocks: list[dict[str, Any]]) -> list[tuple[str, tuple[tuple[str, str | None], ...]]]:
    return [signature for block in blocks if (signature := block_render_signature(block)) is not None]


def page_matches_rendered_blocks(client: NotionClient, page_id_value: str, blocks: list[dict[str, Any]]) -> bool:
    return page_render_signatures(client, page_id_value) == rendered_block_signatures(blocks)


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
    strongest_summary = strongest_repo_success_summary(cwd, compact_summary)
    current_run_notes = markdown_prefixed_code_value(text, "- 当前运行摘要：")
    if strongest_summary and compact_summary and success_summary_metrics(strongest_summary) > success_summary_metrics(compact_summary):
        latest_success_run_notes = (
            "Focused control-plane maintenance run passed. "
            f"Stronger shared validation baseline remains {strongest_summary}"
        )
    else:
        latest_success_run_notes = current_run_notes or strongest_summary
    latest_passing_qa_summary = f"PASS. {strongest_summary}" if strongest_summary else None

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
        latest_success_run_notes=latest_success_run_notes,
        latest_passing_qa_summary=latest_passing_qa_summary,
        evidence_mode="repo_docs_fallback",
        evidence_note="共享 Notion 数据库与活跃控制面页面当前不可达；当前快照由 repo freeze packet 与 handoff docs 恢复。",
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
        evidence_mode="active_pages_fallback",
        evidence_note="共享 Notion 数据库当前不可达；当前快照由 dashboard 与活跃 status / 09C / freeze 页面恢复。",
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
        evidence_mode="dashboard_fallback",
        evidence_note="共享数据库与独立活跃子页当前不可达；dashboard 仍是当前 live truth。",
    )


def github_run_number(text: str | None) -> int:
    if not text:
        return -1
    match = re.search(r"GitHub GSD automation (\d+)", text)
    return int(match.group(1)) if match else -1


def snapshot_quality(snapshot: ReviewSnapshot) -> int:
    score = 0
    if snapshot.active_phase and snapshot.active_phase != "未识别活动 phase":
        score += 2
    if snapshot.latest_verified_plan:
        score += 1
    if snapshot.latest_success_run:
        score += 3
    if snapshot.gate_status and snapshot.gate_status != "Standby":
        score += 1
    if snapshot.latest_passing_qa_summary:
        score += 1
    if snapshot.latest_success_run_notes:
        score += 1
    return score


def snapshot_evidence_mode_label(snapshot: ReviewSnapshot) -> str:
    labels = {
        "database_live": "shared-database live mode",
        "active_pages_fallback": "active-page degraded mode",
        "dashboard_fallback": "dashboard-only degraded mode",
        "repo_docs_fallback": "repo-doc fallback mode",
        "local_timeout_fallback": "local timeout fallback mode",
    }
    return labels.get(snapshot.evidence_mode, snapshot.evidence_mode.replace("_", "-"))


def snapshot_evidence_mode_detail(snapshot: ReviewSnapshot) -> str:
    if snapshot.evidence_note:
        return snapshot.evidence_note
    defaults = {
        "database_live": "共享 Notion 数据库可达；phase / run / QA / gate 取自实时数据库记录。",
        "active_pages_fallback": "共享 Notion 数据库当前不可达；当前快照由 dashboard 与活跃 status / 09C / freeze 页面恢复。",
        "dashboard_fallback": "共享数据库与独立活跃子页当前不可达；dashboard 仍是当前 live truth。",
        "repo_docs_fallback": "共享数据库 / 活跃页面当前不可达；当前快照由 repo freeze packet 与 handoff docs 恢复。",
        "local_timeout_fallback": "Notion 写回在超时保护下未完成；当前快照由本地 repo 文档或 roadmap 恢复。",
    }
    return defaults.get(snapshot.evidence_mode, "当前快照来自非默认证据恢复路径。")


def snapshot_evidence_line(snapshot: ReviewSnapshot) -> str:
    return f"当前证据模式：{snapshot_evidence_mode_label(snapshot)}（{snapshot_evidence_mode_detail(snapshot)}）"


def snapshot_phase_number(snapshot: ReviewSnapshot) -> int | None:
    match = re.match(r"P(\d+)\b", snapshot.active_phase)
    if match:
        return int(match.group(1))
    match = re.match(r"P(\d+)-", snapshot.latest_verified_plan)
    if match:
        return int(match.group(1))
    return None


def snapshot_is_workbench_phase(snapshot: ReviewSnapshot) -> bool:
    phase_number = snapshot_phase_number(snapshot)
    return phase_number is not None and phase_number >= 7


def snapshot_is_runtime_generalization_phase(snapshot: ReviewSnapshot) -> bool:
    return snapshot_phase_number(snapshot) == 8


def development_guardrail_texts(snapshot: ReviewSnapshot) -> tuple[str, ...]:
    runtime_generalization_phase = snapshot_is_runtime_generalization_phase(snapshot)
    workbench_phase = snapshot_is_workbench_phase(snapshot)
    phase_specific_rule = (
        "P8 先把 adapter -> playback -> diagnosis -> knowledge 的 runtime proof 主链收口，再决定是否继续做 comparison / bundle-level proof。"
        if runtime_generalization_phase
        else (
            "P7 workbench 继续把 intake / playback / diagnosis / knowledge / follow-up 收成 engineer-facing workflow，不引入第二套隐藏规则引擎。"
            if workbench_phase
            else "非 P7/P8 收口阶段优先保持控制塔 / freeze / repo handoff 与 GitHub 证据对齐，不为了看起来忙而扩新表面。"
        )
    )
    return (
        "GitHub / repo 是实现真值；Notion 是控制面；`controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。",
        "`runner.py` / `SimulationRunner` 继续承担运行时编排职责；不要把 orchestration 重新塞回 controller truth、UI 或持久化层。",
        "新系统 truth 只能通过显式 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。",
        "FlyByWire / A320 资料只作为知识参考和设计启发，不直接复制成项目代码真值。",
        "一个切片只有在代码修改、目标验证命令、`gsd_notion_sync.py run` 写回，以及 `prepare-opus-review` 复核全部完成后，才算真正完成。",
        "共享数据库或独立子页不可达时，可以暂时依赖 repo-side synced snapshot 继续恢复上下文，但在 live writeback 回补前，不把控制面视为“已同步到最新”。",
        "任何 Notion 写回降级、部分失败或超时都应被当成 control-plane gap / blocker 处理，不能静默跳过后继续宣称已完成同步。",
        "Opus 4.6 只在显式 gate / blocker / subjective review need 时介入；没有 review need 时默认动作就是继续自动开发。",
        phase_specific_rule,
    )


def compact_development_guardrail_texts(snapshot: ReviewSnapshot) -> tuple[str, ...]:
    return (
        "GitHub / repo 是实现真值；Notion 是控制面；`controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。",
        "新系统 truth 只能通过 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。",
        "一个切片只有在代码 / 验证、`gsd_notion_sync.py run` 写回，以及 `prepare-opus-review` 复核完成后，才算收口。",
        "Notion 写回降级必须视为 control-plane gap；没有 review need 时默认继续自动开发。",
    )


def development_guardrail_blocks(snapshot: ReviewSnapshot) -> list[dict[str, Any]]:
    return [heading_block("当前开发架构与执行规则"), *[bullet_block(text) for text in development_guardrail_texts(snapshot)]]


def development_guardrail_markdown_lines(snapshot: ReviewSnapshot) -> list[str]:
    lines = ["## 当前开发架构与执行规则", ""]
    lines.extend(f"- {text}" for text in development_guardrail_texts(snapshot))
    lines.append("")
    return lines


def align_snapshot_with_local_phase(
    snapshot: ReviewSnapshot,
    *,
    cwd: Path,
) -> ReviewSnapshot:
    local_phase_label = current_phase_label_from_roadmap(cwd)
    local_phase_number = current_phase_number_from_roadmap(cwd)
    if local_phase_label is None or local_phase_number is None:
        return snapshot
    if snapshot.active_phase == local_phase_label:
        return snapshot
    current_phase_number = snapshot_phase_number(snapshot)
    if (
        snapshot.active_phase not in {"", "未识别活动 phase"}
        and current_phase_number is not None
        and current_phase_number >= local_phase_number
    ):
        return snapshot
    evidence_note = snapshot.evidence_note or snapshot_evidence_mode_detail(snapshot)
    correction_note = f"当前阶段已按本地 roadmap 纠偏为 `{local_phase_label}`。"
    if correction_note not in evidence_note:
        evidence_note = f"{evidence_note} {correction_note}".strip()
    active_phase_summary = snapshot.active_phase_summary or ""
    if "repo roadmap" not in active_phase_summary:
        active_phase_summary = (
            f"{active_phase_summary} Repo roadmap current phase override applied."
        ).strip()
    return replace(
        snapshot,
        active_phase=local_phase_label,
        active_phase_summary=active_phase_summary,
        evidence_note=evidence_note,
    )


def should_prefer_snapshot(
    primary_snapshot: ReviewSnapshot,
    candidate_snapshot: ReviewSnapshot,
    config: dict[str, Any],
) -> bool:
    candidate_run = github_run_number(candidate_snapshot.latest_success_run)
    primary_run = github_run_number(primary_snapshot.latest_success_run)
    if candidate_run > primary_run:
        return True
    default_plan = config.get("default_plan")
    if (
        default_plan
        and candidate_snapshot.latest_verified_plan == default_plan
        and primary_snapshot.latest_verified_plan != default_plan
    ):
        return True
    candidate_phase = snapshot_phase_number(candidate_snapshot)
    primary_phase = snapshot_phase_number(primary_snapshot)
    if candidate_phase is not None and primary_phase is not None and candidate_phase != primary_phase:
        return candidate_phase > primary_phase
    if candidate_run == primary_run and success_summary_metrics(candidate_snapshot.latest_passing_qa_summary) > success_summary_metrics(primary_snapshot.latest_passing_qa_summary):
        return True
    return snapshot_quality(candidate_snapshot) > snapshot_quality(primary_snapshot)


def should_prefer_page_snapshot(
    primary_snapshot: ReviewSnapshot,
    page_snapshot: ReviewSnapshot,
    config: dict[str, Any],
) -> bool:
    return should_prefer_snapshot(primary_snapshot, page_snapshot, config)


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
    else:
        try:
            repo_snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
        except RuntimeError:
            repo_snapshot = None
        if repo_snapshot and should_prefer_snapshot(snapshot, repo_snapshot, config):
            snapshot = repo_snapshot
    snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)
    if summary.succeeded:
        success_run_notes, passing_qa_summary, passing_qa = select_success_snapshot_evidence(
            snapshot,
            title,
            results,
            summary,
        )
        return replace(
            snapshot,
            latest_verified_plan=plan_id,
            latest_success_run=title,
            latest_failed_run=snapshot.latest_failed_run,
            latest_passing_qa=passing_qa,
            latest_success_run_notes=success_run_notes,
            latest_passing_qa_summary=passing_qa_summary,
        )
    return replace(
        snapshot,
        latest_failed_run=title,
    )


def build_local_run_snapshot(
    config: dict[str, Any],
    *,
    cwd: Path,
    plan_id: str,
    title: str,
    results: list[CommandResult],
    summary: RunSummary,
) -> ReviewSnapshot:
    try:
        snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
    except RuntimeError:
        snapshot = ReviewSnapshot(
            active_phase=current_phase_label_from_roadmap(cwd) or "未识别活动 phase",
            active_phase_goal="",
            active_phase_summary="Recovered locally because Notion writeback timed out before any durable shared write completed.",
            latest_verified_plan=config.get("default_plan", plan_id),
            latest_success_run=None,
            latest_failed_run=None,
            latest_passing_qa=None,
            gate_page_id=None,
            gate_name=config.get("default_review_gate", "OPUS-4.6 周期审查 Gate"),
            gate_status="Approved",
            ready_task_id=None,
            ready_task=None,
            open_gap_titles=(),
            stale_gap_titles=(),
            evidence_mode="local_timeout_fallback",
            evidence_note="Notion 写回在超时保护下未完成；当前快照由本地 repo 文档或 roadmap 恢复。",
        )
    snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)

    if summary.succeeded:
        success_run_notes, passing_qa_summary, passing_qa = select_success_snapshot_evidence(
            snapshot,
            title,
            results,
            summary,
        )
        return replace(
            snapshot,
            latest_verified_plan=plan_id,
            latest_success_run=title,
            latest_failed_run=snapshot.latest_failed_run,
            latest_passing_qa=passing_qa,
            latest_success_run_notes=success_run_notes,
            latest_passing_qa_summary=passing_qa_summary,
        )
    return replace(
        snapshot,
        latest_failed_run=title,
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
        snapshot_evidence_line(snapshot),
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
        bullet_block(snapshot_evidence_line(snapshot)),
    ]
    blocks.extend(
        [
            heading_block("当前开发规则"),
            *[bullet_block(text) for text in compact_development_guardrail_texts(snapshot)],
        ]
    )
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
    evidence_blocks: list[dict[str, Any]] = []
    available_databases = config.get("databases", {})
    evidence_keys = tuple(key for key in ("plans", "runs", "qa", "gates", "gaps", "assets") if key in available_databases)
    if evidence_keys:
        evidence_blocks = [divider_block(), heading_block("实时证据入口")]
        evidence_blocks.extend(database_link_paragraph_block(config, key) for key in evidence_keys)
    blocks.extend(
        [
            divider_block(),
            heading_block("文档定位"),
            bullet_block("这是 AI FANTUI LogicMVP 的 live control plane，而不只是一个临时状态页。"),
            bullet_block("首页负责统一当前真值、历史脉络、证据入口、人工 gate 边界和冻结入口。"),
            bullet_block("Notion 承担流程控制面、审计面和追溯面；代码真值始终保留在 GitHub / repo。"),
            bullet_block("当某些独立子页或数据库因权限 / archived 状态不可写时，dashboard 仍然是当前可依赖的第一入口。"),
            divider_block(),
            heading_block("设计原则"),
            bullet_block("GitHub / repo 是代码与实现真值，不在 Notion 存源码副本。"),
            bullet_block("GitHub Actions 与共享验证套件是自动执行证据面，不把本地终端输出当成主证据。"),
            bullet_block("Opus 4.6 只承担主观 gate / phase closeout 审查，不替代自动化验证。"),
            bullet_block("09C 只输出当下需要的介入请求；没有 review need 时，默认动作就是继续自动开发。"),
            divider_block(),
            heading_block("五层架构"),
            bullet_block("第 1 层 Control Plane：dashboard、Review Gate、Gap、状态页和冻结包。"),
            bullet_block("第 2 层 Execution Plane：本地执行器 + GitHub Actions + 共享 validation suite。"),
            bullet_block("第 3 层 Review Plane：09C 当前审查简报 + 手动触发的 Opus 4.6。"),
            bullet_block("第 4 层 Code Truth Plane：repo、测试、fixtures、控制逻辑与 workbench 代码。"),
            bullet_block("第 5 层 Artifact Plane：freeze packet、diagnosis artifact、knowledge artifact 与 repo archive。"),
            divider_block(),
            heading_block("真相源与职责边界"),
            bullet_block("控制逻辑、诊断逻辑和回归保护以 repo 为准；Notion 不复制这类代码真值。"),
            bullet_block("Notion 记录 phase / plan / gate / gap / 审查结论 / 证据入口，并负责把历史脉络组织成可审计视图。"),
            bullet_block("repo 文档是 handoff / archive 视图；真正审查时仍应回到 Notion 页面与 GitHub 证据面。"),
            bullet_block("Opus 4.6 审查请求必须只依赖 Notion 页面和 GitHub 仓库，不得引用本地终端文件。"),
            divider_block(),
            *development_guardrail_blocks(snapshot),
            *evidence_blocks,
            divider_block(),
            heading_block("历史总览（自动同步）"),
            bullet_block("P0：建立 AI FANTUI LogicMVP 控制塔，把 GitHub / repo 作为代码真值，把 Notion 作为控制面。"),
            bullet_block("P1：打通本地 / GitHub Actions / Notion 的执行、QA 与 Gap 回写闭环。"),
            bullet_block("P2：把 Opus 4.6 审查协议收成 Notion + GitHub-only 的证据边界。"),
            bullet_block("P3：压低控制面漂移，让 09C、Review Gate、legacy artifact retirement 与 GitHub 证据保持同步。"),
            bullet_block("P4：把 cockpit demo 收成 presenter-ready，统一首屏叙事、truth boundary 和解释面。"),
            bullet_block("P5：完成 edge-case hardening、L4 / TRA / VDT 语义修复，以及受控状态 timeline 监控。"),
            bullet_block("P6：修复控制塔与 freeze packet 的历史漂移，让 dashboard 成为 degraded mode 下的 live truth。"),
            bullet_block("P7：开始把项目扩成 spec-driven control analysis workbench，支持 intake、playback、fault diagnosis 和 knowledge capture。"),
            divider_block(),
            heading_block("P7 Workbench 历史"),
            bullet_block("P7-01：建立 reusable control-system spec foundation。"),
            bullet_block("P7-02：建立 mixed-doc / PDF intake packet 与 readiness assessment。"),
            bullet_block("P7-03：把 intake scenario 编译成 monitor-vs-time playback trace。"),
            bullet_block("P7-04：把 fault mode 注入 playback 并生成链路诊断报告。"),
            bullet_block("P7-05：把 diagnosis + repair outcome 收成 reusable knowledge artifact。"),
            bullet_block("P7-06：让未完成的新系统 intake packet 输出 engineer-facing clarification follow-up brief。"),
            bullet_block("P7-07：把 intake / playback / diagnosis / knowledge / follow-up 收成统一 engineer-facing bundle。"),
            divider_block(),
            heading_block("标准闭环"),
            number_block("按 roadmap / default plan 选择当前实现切片，在 repo 中完成代码、测试和验证命令。"),
            number_block("切片完成后立即执行 `gsd_notion_sync.py run`，把 Run / QA / Gap / Gate 与 dashboard、09C、freeze packet 同步回控制面。"),
            number_block("再执行 `prepare-opus-review` 复核当前 Gate / review need；如果没有 open gap 且 Gate 不在 Awaiting Opus 4.6，则继续自动开发。"),
            number_block("只有在 phase 收口、阻塞 gap、显式 gate 等场景下，才通过 09C 手动触发 Opus 4.6。"),
            number_block("任何 Notion 写回降级、部分失败或超时都要先作为 control-plane gap / blocker 处理，不能跳过后直接宣称完成。"),
            number_block("通过后的结论要回写 Review Gate / Gap / repo handoff，让历史链路保持可追溯。"),
        ]
    )
    if config.get("urls", {}).get("github_repo"):
        blocks.extend(
            [
                divider_block(),
                heading_block("历史资料入口"),
                paragraph_parts_block([notion_text("开发历史回顾（repo archive）", repo_blob_url(config, "docs/freeze/2026-04-09-development-history-review.md"))]),
                paragraph_parts_block([notion_text("冻结基线包（repo archive）", repo_blob_url(config, "docs/freeze/2026-04-10-freeze-demo-packet.md"))]),
                paragraph_parts_block([notion_text("P7 Phase Plans（repo archive）", repo_blob_url(config, ".planning/phases/07-build-a-spec-driven-control-analysis-workbench/"))]),
            ]
        )
    return blocks


def render_dashboard_snapshot_blocks(
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
        bullet_block(f"最近成功执行证据：{snapshot.latest_success_run or '暂无'}"),
        bullet_block(f"当前 Gate：{snapshot.gate_name}（{snapshot.gate_status}）"),
        bullet_block(f"当前 Opus 状态：{current_opus_state}"),
        bullet_block(f"当前唯一人工动作：{current_action}"),
        bullet_block(f"Open Gap 数量：{len(snapshot.open_gap_titles)}"),
        bullet_block(snapshot_evidence_line(snapshot)),
    ]
    if unavailable_page_keys:
        blocks.append(
            bullet_block(
                "当前控制面模式：dashboard-only degraded mode（dashboard 仍为 live truth，独立 status / 09C / freeze 子页当前不可直写）。"
            )
        )
    blocks.extend(
        [
            paragraph_parts_block([notion_text("GitHub Repo / ai-fantui-logicmvp", config_url(config, "github_repo"))]),
            paragraph_parts_block([notion_text("GitHub Actions / GSD Automation Loop", config_url(config, "github_actions"))]),
            divider_block(),
        ]
    )
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
        bullet_block(snapshot_evidence_line(snapshot)),
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
    workbench_phase = snapshot_is_workbench_phase(snapshot)
    runtime_generalization_phase = snapshot_is_runtime_generalization_phase(snapshot)
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
        bullet_block(snapshot_evidence_line(snapshot)),
        bullet_block(
            "P8 已成为当前主线，正在把 adapter-backed second-system runtime proof 接到 playback / diagnosis / knowledge 主链。"
            if runtime_generalization_phase
            else (
                "P7 已成为当前主线，正在把 intake / playback / diagnosis / knowledge / follow-up 收成统一 engineer-facing workflow。"
                if workbench_phase
                else "P7 的 spec-driven workbench foundation 已在 repo 中提前播种，但正式自动执行顺序暂时仍以 P6 为先。"
            )
        ),
        heading_block("当前回归"),
        bullet_block(f"最近成功执行证据：{snapshot.latest_success_run or '暂无'}"),
    ]
    if snapshot.latest_passing_qa_summary:
        blocks.append(bullet_block(f"QA 摘要：{snapshot.latest_passing_qa_summary}"))
    if snapshot.latest_success_run_notes:
        blocks.append(bullet_block(f"运行摘要：{snapshot.latest_success_run_notes}"))
    blocks.extend(
        [
            *development_guardrail_blocks(snapshot),
            heading_block("当前关键边界"),
            bullet_block("`controller.py` 仍然是 reference thrust-reverser 的 confirmed truth。"),
            bullet_block("`runner.py` / SimulationRunner 继续承担运行时编排，不把 orchestration 挪进 controller truth。"),
            bullet_block("新系统 truth 只能通过 adapter interface 接入，禁止绕过 adapter 新增 hardcoded truth。"),
            bullet_block("不把 simplified plant 表述成完整实时物理模型。"),
            bullet_block("FlyByWire / A320 资料只作为参考知识库，不作为代码复制源。"),
            bullet_block("Opus 4.6 只使用 Notion + GitHub 证据面。"),
            heading_block("当前下一步"),
            bullet_block(
                "继续把 adapter-backed runtime proof 接到 second-system smoke / comparison / bundle-level surface，证明第二系统主链已经真正跑通。"
                if runtime_generalization_phase
                else (
                    "继续把 intake / playback / diagnosis / knowledge / follow-up 收成可复用的 engineer-facing bundle 与 handoff 工作流。"
                    if workbench_phase
                    else "继续收口剩余 stale wording，让 control tower summary surfaces 不再依赖手工维护。"
                )
            ),
            bullet_block(
                "保持 controller truth、runner orchestration 与当前回归基线稳定；任何新系统 proof 都只能通过 adapter boundary 进入。"
                if runtime_generalization_phase
                else (
                    "保持 controller truth、demo API 契约与 freeze baseline 稳定，不把 P7 扩成第二套隐藏规则引擎。"
                    if workbench_phase
                    else "继续把历史 manual-browser-QA 表述降级成 presenter guidance，而不是当前审批规则。"
                )
            ),
            bullet_block(current_action),
            bullet_block(
                "必要时把新的 runtime proof artifact 同步回 repo / Notion 控制面，保持 engineer handoff 与审计链路可追溯。"
                if runtime_generalization_phase
                else (
                    "必要时把新的 workbench artifact 同步回 repo / Notion 控制面，保持 engineer handoff 与审计链路可追溯。"
                    if workbench_phase
                    else "在 P6 收口前，不继续扩大 P7 的实现面。"
                )
            ),
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
    workbench_phase = snapshot_is_workbench_phase(snapshot)
    runtime_generalization_phase = snapshot_is_runtime_generalization_phase(snapshot)
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
        f"- 当前证据模式：`{snapshot_evidence_mode_label(snapshot)}`",
    ]
    lines.append(f"- 证据模式说明：{snapshot_evidence_mode_detail(snapshot)}")
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    lines.extend(
        [
            (
                "- 当前结论：当前最高优先级是把 adapter-backed second-system runtime proof 接到主 smoke/validation 链，而不是回退成只做 contract 或 UI 表层。"
                if runtime_generalization_phase
                else (
                    "- 当前结论：当前最高优先级是把 spec-driven workbench 收成统一 engineer-facing workflow，而不是继续做 P6 控制面清理或新增 demo 表面。"
                    if workbench_phase
                    else "- 当前结论：当前最高优先级是继续收口控制塔与 freeze/demo packet 的残余漂移，不是再加 demo 功能。"
                )
            ),
            f"- 当前唯一人工动作：{current_action}",
            "",
            *development_guardrail_markdown_lines(snapshot),
            "## 当前关键边界",
            "",
            "- `controller.py` 仍然是 reference thrust-reverser 的唯一控制真值。",
            "- `runner.py` / `SimulationRunner` 继续承担运行时编排，不把 orchestration 回塞进 controller truth / UI / persistence。",
            "- 新系统 truth 只能通过 adapter interface 接入；禁止绕过 adapter 新增 hardcoded truth path。",
            "- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。",
            "- FlyByWire / A320 资料只作为参考知识库，不作为代码复制源。",
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
    workbench_phase = snapshot_is_workbench_phase(snapshot)
    runtime_generalization_phase = snapshot_is_runtime_generalization_phase(snapshot)
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
    lines.extend(
        [
            f"- 当前证据模式：`{snapshot_evidence_mode_label(snapshot)}`",
            f"- 证据模式说明：{snapshot_evidence_mode_detail(snapshot)}",
        ]
    )
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            (
                "- 当前 demo / freeze 基线已经稳定；当前主线已切到 P8 runtime generalization proof。"
                if runtime_generalization_phase
                else (
                    "- 当前 demo / freeze 基线已经稳定；当前主线已切到 P7 spec-driven workbench。"
                    if workbench_phase
                    else "- 当前 demo 基线已经稳定，P6 的任务是把控制塔、freeze packet 和 repo-side handoff 资料统一到同一份 GitHub-backed 真值。"
                )
            ),
            (
                "- 当前优先级是把 adapter-backed second-system proof 接到 smoke / comparison / bundle-level surface，而不是继续扩 demo 表面。"
                if runtime_generalization_phase
                else (
                    "- 当前优先级是让 engineer-facing onboarding / playback / diagnosis / knowledge 工具形成连续工作流，而不是继续扩 demo 表面。"
                    if workbench_phase
                    else "- 当前不继续扩大 P7 的实现面；P7 groundwork 继续保留，但执行顺序仍以 P6 收口优先。"
                )
            ),
            "",
            *development_guardrail_markdown_lines(snapshot),
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
            (
                "- 当前交接重点是保持 workbench bundle / playback / diagnosis / knowledge 链路可复用，不是回到零散单命令操作。"
                if workbench_phase
                else "- 当前交接重点是保持 control-plane truth 收口，不是扩新功能。"
            ),
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
        f"- 当前证据模式：`{snapshot_evidence_mode_label(snapshot)}`",
    ]
    lines.append(f"- 证据模式说明：{snapshot_evidence_mode_detail(snapshot)}")
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            "",
            "## 当前执行规则",
            "",
            *[f"- {text}" for text in development_guardrail_texts(snapshot)[:5]],
            "",
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
    workbench_phase = snapshot_is_workbench_phase(snapshot)
    runtime_generalization_phase = snapshot_is_runtime_generalization_phase(snapshot)
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
        f"- 当前证据模式：`{snapshot_evidence_mode_label(snapshot)}`",
    ]
    lines.append(f"- 证据模式说明：{snapshot_evidence_mode_detail(snapshot)}")
    if snapshot.latest_passing_qa_summary:
        lines.append(f"- 当前 QA 摘要：`{snapshot.latest_passing_qa_summary}`")
    if snapshot.latest_success_run_notes:
        lines.append(f"- 当前运行摘要：`{snapshot.latest_success_run_notes}`")
    lines.extend(
        [
            (
                "- 当前冻结包继续作为稳定 demo/reference baseline；当前工程主线已转向 P8 runtime generalization proof。"
                if runtime_generalization_phase
                else (
                    "- 当前冻结包继续作为稳定 demo/reference baseline；当前工程主线已转向 P7 workbench 扩展。"
                    if workbench_phase
                    else "- 当前冻结包的职责是对齐 repo / GitHub / Notion 三个证据面，而不是继续加产品表面。"
                )
            ),
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
    if not isinstance(children, list):
        children = []
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
            delete_block_if_present(client, block["id"])
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
    config_path: Path | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    snapshot = fetch_review_snapshot(client, config)
    if cwd is not None:
        snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)
    return write_current_opus_review_brief_from_snapshot(
        client,
        config,
        snapshot=snapshot,
        activate_gate=activate_gate,
        config_path=config_path,
        cwd=cwd,
    )


def write_current_opus_review_brief_from_snapshot(
    client: NotionClient,
    config: dict[str, Any],
    *,
    snapshot: ReviewSnapshot,
    activate_gate: bool,
    config_path: Path | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    base_snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd) if cwd is not None else snapshot
    effective_snapshot = (
        replace(base_snapshot, gate_status="Awaiting Opus 4.6")
        if activate_gate
        else base_snapshot
    )
    brief = build_current_review_brief(effective_snapshot, config, force_review=activate_gate)
    unavailable_page_keys: list[str] = []
    replaced_sync_page_keys: set[str] = set()
    if config_path is not None and "opus_brief" in config.get("pages", {}):
        previous_id = config.get("pages", {}).get("opus_brief")
        brief_page_id = replace_active_sync_page(
            client,
            config,
            key="opus_brief",
            title=brief.page_title,
            blocks=render_current_review_brief_blocks(brief, effective_snapshot, config),
            config_path=config_path,
        )
        if brief_page_id != previous_id:
            replaced_sync_page_keys.add("opus_brief")
    elif not page_is_writable(client, config, "opus_brief"):
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
    if config_path is None and not page_is_writable(client, config, "status"):
        unavailable_page_keys.append("status")
    if config_path is None and not page_is_writable(client, config, "freeze_packet"):
        unavailable_page_keys.append("freeze_packet")
    if config_path is not None and "status" in config.get("pages", {}):
        previous_id = config.get("pages", {}).get("status")
        status_page_id = replace_active_sync_page(
            client,
            config,
            key="status",
            title="01 当前状态（自动同步）",
            blocks=render_status_page_blocks(brief, effective_snapshot, config),
            config_path=config_path,
        )
        if status_page_id != previous_id:
            replaced_sync_page_keys.add("status")
    elif "status" not in unavailable_page_keys:
        status_page_id = page_id(config, "status")
        try:
            client.update_page_properties(status_page_id, {"title": title_value("01 当前状态（自动同步）")})
            client.replace_page_body(status_page_id, render_status_page_blocks(brief, effective_snapshot, config))
        except RuntimeError as exc:
            if not (is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc))):
                raise
            unavailable_page_keys.append("status")
    if config_path is not None and "freeze_packet" in config.get("pages", {}):
        previous_id = config.get("pages", {}).get("freeze_packet")
        freeze_packet_page_id = replace_active_sync_page(
            client,
            config,
            key="freeze_packet",
            title="10 Freeze Demo Packet",
            blocks=render_freeze_packet_blocks(brief, effective_snapshot, config),
            config_path=config_path,
        )
        if freeze_packet_page_id != previous_id:
            replaced_sync_page_keys.add("freeze_packet")
    elif "freeze_packet" not in unavailable_page_keys:
        freeze_packet_page_id = page_id(config, "freeze_packet")
        try:
            client.update_page_properties(freeze_packet_page_id, {"title": title_value("10 Freeze Demo Packet")})
            client.replace_page_body(freeze_packet_page_id, render_freeze_packet_blocks(brief, effective_snapshot, config))
        except RuntimeError as exc:
            if not (is_missing_page_error(str(exc)) or is_archived_page_write_error(str(exc))):
                raise
            unavailable_page_keys.append("freeze_packet")
    if config_path is not None and replaced_sync_page_keys:
        rewrite_active_sync_page_body(
            client,
            page_id(config, "opus_brief"),
            title=brief.page_title,
            blocks=render_current_review_brief_blocks(brief, effective_snapshot, config),
        )
        rewrite_active_sync_page_body(
            client,
            page_id(config, "status"),
            title="01 当前状态（自动同步）",
            blocks=render_status_page_blocks(brief, effective_snapshot, config),
        )
        rewrite_active_sync_page_body(
            client,
            page_id(config, "freeze_packet"),
            title="10 Freeze Demo Packet",
            blocks=render_freeze_packet_blocks(brief, effective_snapshot, config),
        )
    prune_stale_active_sync_page_blocks(client, config)
    upsert_dashboard_snapshot_section(
        client,
        dashboard_page_id,
        render_dashboard_snapshot_blocks(
            brief,
            effective_snapshot,
            config,
            unavailable_page_keys=tuple(unavailable_page_keys),
        ),
    )

    if snapshot.gate_page_id:
        client.update_page_properties(
        base_snapshot.gate_page_id,
            build_gate_update_properties(brief, activate_gate=activate_gate),
        )
    if base_snapshot.ready_task_id:
        client.update_page_properties(
            base_snapshot.ready_task_id,
            {
                "Acceptance": rich_text_value("基于 09C 当前 Opus 4.6 审查简报，在 Notion AI 中触发当前所需介入，而不是使用固定模板。"),
                "Next Step": rich_text_value("打开 09C 当前 Opus 4.6 审查简报，按其中的当前介入请求执行。"),
            },
        )
    retired_artifact_ids = retire_legacy_review_artifacts(
        client,
        config,
        snapshot=base_snapshot,
        brief=brief,
    )

    return {
        "page_id": brief_page_id,
        "page_title": brief.page_title,
        "review_required": brief.review_required,
        "intervention_kind": brief.intervention_kind,
        "review_target": brief.review_target,
        "gate_status": "Awaiting Opus 4.6" if activate_gate else base_snapshot.gate_status,
        "open_gap_count": len(base_snapshot.open_gap_titles),
        "stale_gap_count": len(base_snapshot.stale_gap_titles),
        "latest_success_run": base_snapshot.latest_success_run,
        "latest_failed_run": base_snapshot.latest_failed_run,
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
    config_path: Path | None = None,
    cwd: Path | None = None,
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

    # Parallel upsert for the three core records (plan, run, qa) — each is independent
    def _upsert_plan() -> tuple[str, str]:
        return ("plan", client.upsert_page(
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
        ))

    def _upsert_run() -> tuple[str, str]:
        return ("run", client.upsert_page(
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
        ))

    def _upsert_qa() -> tuple[str, str]:
        return ("qa", client.upsert_page(
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
        ))

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(_upsert_plan),
            executor.submit(_upsert_run),
            executor.submit(_upsert_qa),
        ]
        for future in as_completed(futures):
            key, page_id = future.result()
            written[key] = page_id

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
                config_path=config_path,
                cwd=cwd,
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
        written["opus_review_brief"] = write_current_opus_review_brief(
            client,
            config,
            activate_gate=True,
            config_path=config_path,
            cwd=cwd,
        )

    return written


def handle_sync_roadmap(args: argparse.Namespace, config: dict[str, Any]) -> int:
    """Standalone handler for the sync-roadmap CLI subcommand."""
    if not os.environ.get("NOTION_API_KEY"):
        raise SystemExit("NOTION_API_KEY is required for sync-roadmap.")
    cwd = Path(args.cwd).resolve()
    roadmap_path = (cwd / ".planning/ROADMAP.md").resolve()
    result = sync_roadmap_phases(config, roadmap_path=roadmap_path)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("registered"):
            print(f"Registered: {', '.join(result['registered'])}")
        if result.get("already_registered"):
            print(f"Already registered: {', '.join(result['already_registered'])}")
        if result.get("closed"):
            print(f"Closed: {', '.join(result['closed'])}")
        if result.get("errors"):
            for err in result["errors"]:
                print(f"ERROR: {err}", file=__import__("sys").stderr)
    return 0 if not result.get("errors") else 1


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

    roadmap_parser = subparsers.add_parser(
        "sync-roadmap",
        help="Sync ROADMAP.md phase lifecycle to the Notion Roadmap DB (register Active phases, close Done phases).",
    )
    roadmap_parser.add_argument(
        "--cwd",
        default=".",
        help="Repo root (used to resolve .planning/ROADMAP.md).",
    )
    roadmap_parser.add_argument(
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


def sync_repo_docs_from_snapshot(
    cwd: Path,
    snapshot: ReviewSnapshot,
    config: dict[str, Any],
    *,
    unavailable_page_keys: tuple[str, ...] = (),
) -> list[RepoDocSyncResult]:
    snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)
    return sync_repo_documents(
        cwd,
        build_current_review_brief(snapshot, config),
        snapshot,
        config,
        unavailable_page_keys=unavailable_page_keys,
    )


def handle_run(args: argparse.Namespace, config: dict[str, Any]) -> int:
    cwd = Path(args.cwd).resolve()
    config_path = Path(getattr(args, "config", DEFAULT_CONFIG_PATH))
    config["default_plan"] = effective_default_plan(config, cwd=cwd)
    plan_id = args.plan_id or config["default_plan"]
    title = args.title or f"{plan_id} automation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    writeback_timeout_s = float(os.environ.get("NOTION_WRITEBACK_TIMEOUT_S", DEFAULT_NOTION_WRITEBACK_TIMEOUT_S))
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
            with notion_writeback_deadline(writeback_timeout_s):
                restored_databases = ensure_live_databases(client, config)
                if restored_databases:
                    payload["restored_databases"] = restored_databases
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
                    config_path=config_path,
                    cwd=cwd,
                )
        except Exception as exc:
            payload["notion"] = "failed"
            payload["notion_error"] = str(exc)
            if summary.succeeded:
                try:
                    if isinstance(exc, NotionWritebackTimeout):
                        fallback_snapshot = build_local_run_snapshot(
                            config,
                            cwd=cwd,
                            plan_id=plan_id,
                            title=title,
                            results=results,
                            summary=summary,
                        )
                        payload["notion_fallback"] = "skipped_after_timeout"
                    else:
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
                            config_path=config_path,
                            cwd=cwd,
                        )
                        payload["notion_fallback"] = "written"
                    repo_docs = sync_repo_docs_from_snapshot(cwd, fallback_snapshot, config)
                except Exception as fallback_exc:
                    payload["notion_fallback"] = "failed"
                    payload["notion_fallback_error"] = str(fallback_exc)
                else:
                    payload["notion"] = "partial"
                    payload["repo_doc_sync"] = "written"
                    payload["repo_docs"] = [{"path": item.path, "marker": item.marker} for item in repo_docs]
        else:
            payload["notion"] = "written"
            payload["notion_pages"] = written
            if "opus_review_brief" in written:
                payload["opus_review_brief"] = written["opus_review_brief"]
            if summary.succeeded:
                try:
                    repo_snapshot = build_fallback_run_snapshot(
                        client,
                        config,
                        cwd=cwd,
                        plan_id=plan_id,
                        title=title,
                        results=results,
                        summary=summary,
                    )
                    try:
                        unavailable_page_keys = active_page_unavailable_keys(client, config)
                    except RuntimeError:
                        unavailable_page_keys = ()
                    repo_docs = sync_repo_docs_from_snapshot(
                        cwd,
                        repo_snapshot,
                        config,
                        unavailable_page_keys=unavailable_page_keys,
                    )
                except Exception as repo_exc:
                    payload["repo_doc_sync"] = "failed"
                    payload["repo_doc_sync_error"] = str(repo_exc)
                else:
                    payload["repo_doc_sync"] = "written"
                    payload["repo_docs"] = [{"path": item.path, "marker": item.marker} for item in repo_docs]
    output_run_result(args.format, payload)
    return 0 if summary.succeeded else 1


def handle_prepare_opus_review(args: argparse.Namespace, config: dict[str, Any]) -> int:
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("NOTION_API_KEY is required for prepare-opus-review.")
    config_path = Path(getattr(args, "config", DEFAULT_CONFIG_PATH))
    cwd = Path.cwd().resolve()
    client = NotionClient(token)
    prepare_timeout_s = float(
        os.environ.get(
            "NOTION_PREPARE_TIMEOUT_S",
            os.environ.get("NOTION_WRITEBACK_TIMEOUT_S", DEFAULT_NOTION_WRITEBACK_TIMEOUT_S),
        )
    )
    try:
        with notion_writeback_deadline(prepare_timeout_s):
            restored_databases = ensure_live_databases(client, config)
            snapshot = fetch_review_snapshot(client, config)
    except NotionWritebackTimeout:
        snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
    except RuntimeError as exc:
        if not (is_missing_database_error(str(exc)) or is_rate_limited_error(str(exc))):
            raise
        page_snapshot = None
        try:
            page_snapshot = fetch_review_snapshot_from_pages(client, config)
        except RuntimeError as page_exc:
            if not (is_missing_page_error(str(page_exc)) or is_rate_limited_error(str(page_exc))):
                raise
        try:
            repo_snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
        except RuntimeError:
            repo_snapshot = None
        if page_snapshot and repo_snapshot:
            snapshot = repo_snapshot if should_prefer_snapshot(page_snapshot, repo_snapshot, config) else page_snapshot
        elif page_snapshot:
            snapshot = page_snapshot
        elif repo_snapshot:
            snapshot = repo_snapshot
        else:
            raise RuntimeError("Unable to derive a review snapshot from pages or repo docs.")
    snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)
    effective_snapshot = (
        snapshot
        if not args.activate_gate
        else replace(snapshot, gate_status="Awaiting Opus 4.6")
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
    if 'restored_databases' in locals() and restored_databases:
        payload["restored_databases"] = restored_databases
    if not args.dry_run:
        try:
            with notion_writeback_deadline(prepare_timeout_s):
                restored_databases = ensure_live_databases(client, config)
                if restored_databases:
                    payload["restored_databases"] = restored_databases
                replacements = ensure_live_active_pages(client, config, config_path=config_path)
                if replacements:
                    payload["replaced_pages"] = replacements
                payload["notion"] = write_current_opus_review_brief_from_snapshot(
                    client,
                    config,
                    snapshot=effective_snapshot,
                    activate_gate=args.activate_gate,
                    config_path=config_path,
                    cwd=cwd,
                )
        except NotionWritebackTimeout as exc:
            payload["notion"] = {
                "timeout_fallback": True,
                "message": str(exc),
                "review_required": brief.review_required,
                "intervention_kind": brief.intervention_kind,
                "review_target": brief.review_target,
                "gate_status": effective_snapshot.gate_status,
            }
    output_review_result(args.format, payload)
    return 0


def handle_sync_repo_docs(args: argparse.Namespace, config: dict[str, Any]) -> int:
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("NOTION_API_KEY is required for sync-repo-docs.")
    client = NotionClient(token)
    cwd = Path(args.cwd).resolve()
    snapshot: ReviewSnapshot | None = None
    try:
        restored_databases = ensure_live_databases(client, config)
        snapshot = fetch_review_snapshot(client, config)
    except RuntimeError as exc:
        if not (is_missing_database_error(str(exc)) or is_rate_limited_error(str(exc))):
            raise
        page_snapshot = None
        for fetcher in (fetch_review_snapshot_from_pages, fetch_review_snapshot_from_dashboard_page):
            try:
                page_snapshot = fetcher(client, config)
                break
            except RuntimeError as page_exc:
                if not (is_missing_page_error(str(page_exc)) or is_rate_limited_error(str(page_exc))):
                    raise
        try:
            repo_snapshot = fetch_review_snapshot_from_repo_docs(cwd, config)
        except RuntimeError:
            repo_snapshot = None
        if page_snapshot and repo_snapshot:
            snapshot = repo_snapshot if should_prefer_snapshot(page_snapshot, repo_snapshot, config) else page_snapshot
        elif page_snapshot:
            snapshot = page_snapshot
        elif repo_snapshot:
            snapshot = repo_snapshot
        else:
            raise RuntimeError("Unable to derive a repo-doc snapshot from pages or repo docs.")
    else:
        page_snapshot = None
        for fetcher in (fetch_review_snapshot_from_pages, fetch_review_snapshot_from_dashboard_page):
            try:
                page_snapshot = fetcher(client, config)
                break
            except RuntimeError as page_exc:
                if not (is_missing_page_error(str(page_exc)) or is_rate_limited_error(str(page_exc))):
                    raise
        if page_snapshot and should_prefer_page_snapshot(snapshot, page_snapshot, config):
            snapshot = page_snapshot
    snapshot = align_snapshot_with_local_phase(snapshot, cwd=cwd)
    brief = build_current_review_brief(snapshot, config)
    try:
        unavailable_page_keys = active_page_unavailable_keys(client, config)
    except RuntimeError as exc:
        if not is_rate_limited_error(str(exc)):
            raise
        unavailable_page_keys = ()
    synced = sync_repo_documents(
        cwd,
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
    if 'restored_databases' in locals() and restored_databases:
        payload["restored_databases"] = restored_databases
    # Auto-sync ROADMAP.md phases to Notion Roadmap DB (non-blocking)
    try:
        roadmap_sync = sync_roadmap_phases(config)
        payload["roadmap_sync"] = roadmap_sync
    except Exception as exc:
        payload["roadmap_sync"] = {"registered": [], "closed": [], "errors": [str(exc)]}
    output_repo_doc_sync_result(args.format, payload)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = Path(args.config).resolve()
    config = load_control_plane_config(config_path)
    resolved_default_plan = effective_default_plan(config, cwd=config_path.parent.parent)
    if config.get("default_plan") != resolved_default_plan:
        config["default_plan"] = resolved_default_plan
        save_control_plane_config(config_path, config)
    else:
        config["default_plan"] = resolved_default_plan
    if args.command_name == "run":
        return handle_run(args, config)
    if args.command_name == "prepare-opus-review":
        return handle_prepare_opus_review(args, config)
    if args.command_name == "sync-repo-docs":
        return handle_sync_repo_docs(args, config)
    if args.command_name == "sync-roadmap":
        return handle_sync_roadmap(args, config)
    parser.error(f"Unsupported command: {args.command_name}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

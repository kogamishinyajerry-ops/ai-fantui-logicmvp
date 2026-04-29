from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tools.notion_review_record import (
    NotionApiError,
    build_plain_text_comment_payload,
    build_review_record_text,
    classify_notion_error,
    extract_notion_page_id,
)


def test_extract_notion_page_id_from_app_slug_url() -> None:
    page_id = extract_notion_page_id(
        "https://app.notion.com/p/REVIEW_REQUEST-CFDJerry-351c68942bed81e1b57fe3958e8baaa2"
    )

    assert page_id == "351c68942bed81e1b57fe3958e8baaa2"


def test_extract_notion_page_id_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="Notion page id"):
        extract_notion_page_id("not-a-page")


def test_build_review_record_text_is_docs_only() -> None:
    record = build_review_record_text(
        pr_url="https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/129",
        linear="JER-141,JER-142,JER-143,JER-144,JER-145",
        decision="Notion Opus review trigger abandoned; use GitHub/Linear review evidence.",
        evidence=("validation 24/24", "adversarial 8/8"),
    )

    assert "DOCUMENTATION_RECORD" in record
    assert "PR #129" in record
    assert "JER-141,JER-142,JER-143,JER-144,JER-145" in record
    assert "does not trigger Notion AI" in record
    assert "Notion is documentation only" in record
    assert "validation 24/24; adversarial 8/8" in record


def test_build_plain_text_comment_payload() -> None:
    payload = build_plain_text_comment_payload(
        page_id="351c68942bed81e1b57fe3958e8baaa2",
        comment_text="hello",
    )

    assert payload == {
        "parent": {"page_id": "351c68942bed81e1b57fe3958e8baaa2"},
        "rich_text": [{"type": "text", "text": {"content": "hello"}}],
    }


@pytest.mark.parametrize(
    "error,expected",
    [
        (
            NotionApiError(
                status=400,
                body='{"code":"validation_error","message":"Cannot mention bots. Mentioned bot id: 33ac"}',
            ),
            "bot_mention_unsupported",
        ),
        (
            NotionApiError(
                status=403,
                body='{"code":"restricted_resource","message":"Insufficient permissions for this endpoint."}',
            ),
            "comment_permission_denied",
        ),
    ],
)
def test_classify_notion_error(error: NotionApiError, expected: str) -> None:
    assert classify_notion_error(error) == expected


def test_cli_dry_run_outputs_documentation_record_without_token() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/notion_review_record.py",
            "--target-page",
            "https://app.notion.com/p/REVIEW_REQUEST-CFDJerry-351c68942bed81e1b57fe3958e8baaa2",
            "--pr-url",
            "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/129",
            "--linear",
            "JER-141,JER-142,JER-143,JER-144,JER-145",
            "--decision",
            "Notion Opus review trigger abandoned; use GitHub/Linear review evidence.",
            "--evidence",
            "validation 24/24",
            "--evidence",
            "adversarial 8/8",
            "--format",
            "json",
        ],
        check=True,
        cwd=".",
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["mode"] == "dry_run"
    assert payload["notion_role"] == "documentation_record_only"
    assert payload["target_page_id"] == "351c68942bed81e1b57fe3958e8baaa2"
    assert payload["review_execution_claim"] == "not_applicable"
    assert "mention" not in json.dumps(payload["prepared_payload"])

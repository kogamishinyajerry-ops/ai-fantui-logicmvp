from __future__ import annotations

import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "change_request_v0_1.schema.json"
DOC_PATH = PROJECT_ROOT / "docs" / "governance" / "change_request_schema_v0_1.md"


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def valid_bookkeeping_change_request() -> dict:
    return {
        "schema_version": "change_request.v0.1",
        "change_request_id": "CR-DRAFT-0001",
        "title": "Record Notion as docs-only evidence surface",
        "summary": "Documents a governance-surface clarification without changing truth behavior.",
        "authority": {
            "status": "draft_non_authoritative",
            "approval_required_before_execution": True,
            "approval_routes": ["kogami_charter"],
        },
        "origin": {
            "source": "linear",
            "source_ref": "JER-146",
            "created_by": "codex-daily-lane",
            "created_at": "2026-04-29",
        },
        "owner": {
            "name": "Codex Daily Lane",
            "role": "draft_author",
        },
        "status": "draft",
        "classification": "bookkeeping",
        "impacts": {
            "namespaces": ["governance"],
            "adapters": [],
            "truth_level_impact": "none",
        },
        "dal_impact": {
            "impact": "none",
            "rationale": "Documentation-only governance record; no system behavior or DAL claim changes.",
        },
        "evidence_anchors": [
            {
                "kind": "linear",
                "ref": "JER-146",
                "url": "https://linear.app/jerrykogami/issue/JER-146",
            }
        ],
        "decision_links": [],
    }


def validator_for_change_request_schema():
    pytest.importorskip("jsonschema")
    from jsonschema import Draft202012Validator

    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_valid_bookkeeping_change_request_passes_schema() -> None:
    validator = validator_for_change_request_schema()

    errors = list(validator.iter_errors(valid_bookkeeping_change_request()))

    assert errors == []


def test_dal_impacting_request_requires_escalation_fields() -> None:
    validator = validator_for_change_request_schema()
    payload = valid_bookkeeping_change_request()
    payload["classification"] = "dal_impacting"
    payload["dal_impact"] = {
        "impact": "potential",
        "rationale": "Would alter safety classification if executed.",
    }

    errors = list(validator.iter_errors(payload))

    assert any("escalation" in error.message for error in errors)


def test_dal_impacting_request_with_escalation_remains_draft() -> None:
    validator = validator_for_change_request_schema()
    payload = valid_bookkeeping_change_request()
    payload["classification"] = "dal_impacting"
    payload["dal_impact"] = {
        "impact": "potential",
        "rationale": "Would alter safety classification if executed.",
    }
    payload["escalation"] = {
        "required": True,
        "route": "kogami_charter",
        "reason": "Potential DAL impact must leave Codex lane before execution.",
    }

    errors = list(validator.iter_errors(payload))

    assert errors == []
    assert payload["authority"]["status"] == "draft_non_authoritative"


def test_change_request_schema_doc_marks_draft_non_authoritative() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "non-authoritative" in doc
    assert "does not approve DAL" in doc
    assert "does not promote truth-level" in doc

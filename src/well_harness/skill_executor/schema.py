"""Audit-record schema validator.

Used by:
  - `audit.write_audit()`  — refuses to persist a malformed record
  - `audit.read_audit()`   — refuses to load one
  - the P48-05 GitHub Action — refuses to merge PRs whose audit JSON
    breaks the schema

We deliberately don't pull `jsonschema` (extra dep, slow startup).
The validator is a hand-rolled traversal that asserts:
  - all REQUIRED top-level fields are present
  - each value has the expected primitive type
  - enum-valued fields parse back into their enum
  - schema_version equals AUDIT_SCHEMA_VERSION (1)
  - state value is one of ExecutionState
  - if plan is present, its file_edits are well-formed
  - if asks is non-empty, each entry is well-formed
"""

from __future__ import annotations

from typing import Any

from well_harness.skill_executor.errors import AuditSchemaError
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AskResponse,
    AuditSource,
    ExecutionKind,
)
from well_harness.skill_executor.states import ExecutionState


_REQUIRED_TOP_LEVEL: tuple[tuple[str, type], ...] = (
    ("exec_id", str),
    ("schema_version", int),
    ("proposal_id", str),
    ("kind", str),
    ("audit_source", str),
    ("started_at", str),
    ("state", str),
)

_REQUIRED_FILE_EDIT: tuple[str, ...] = ("path", "old_snippet", "new_snippet")
_REQUIRED_ASK: tuple[str, ...] = ("ask_id", "question")
_REQUIRED_TEST_RESULT: tuple[tuple[str, type], ...] = (
    ("passed", int),
    ("failed", int),
)


def validate_audit_dict(data: Any) -> None:
    """Raises AuditSchemaError with a precise reason on any
    deviation. Returns None on success — silence is the all-clear.

    The function is structured so the exception message points at
    the specific path inside the document (e.g.
    `plan.file_edits[2].path`). The CI gate passes that string
    through to the PR comment so a reviewer can fix the audit
    file directly."""
    if not isinstance(data, dict):
        raise AuditSchemaError(
            f"audit record must be a JSON object, got {type(data).__name__}"
        )

    for field, expected_type in _REQUIRED_TOP_LEVEL:
        if field not in data:
            raise AuditSchemaError(f"missing required field: {field!r}")
        if not isinstance(data[field], expected_type):
            raise AuditSchemaError(
                f"field {field!r}: expected {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )

    if data["schema_version"] != AUDIT_SCHEMA_VERSION:
        raise AuditSchemaError(
            f"schema_version: expected {AUDIT_SCHEMA_VERSION}, "
            f"got {data['schema_version']} — record was written against "
            f"a different version of the executor; migrate or refuse"
        )

    # Enum values
    try:
        ExecutionKind(data["kind"])
    except ValueError as exc:
        raise AuditSchemaError(
            f"kind: invalid value {data['kind']!r}; "
            f"must be one of {[k.value for k in ExecutionKind]}"
        ) from exc
    try:
        AuditSource(data["audit_source"])
    except ValueError as exc:
        raise AuditSchemaError(
            f"audit_source: invalid value {data['audit_source']!r}; "
            f"must be one of {[s.value for s in AuditSource]}"
        ) from exc
    try:
        ExecutionState(data["state"])
    except ValueError as exc:
        raise AuditSchemaError(
            f"state: invalid value {data['state']!r}; "
            f"must be one of {[s.value for s in ExecutionState]}"
        ) from exc

    # Optional but typed
    for field, expected in (
        ("finished_at", str),
        ("executor_version", str),
        ("executor_host", str),
        ("executor_user", str),
        ("llm_backend", str),
        ("branch", str),
        ("pr_url", str),
        ("landed_sha", str),
        ("abort_reason", str),
    ):
        if field in data and not isinstance(data[field], expected):
            raise AuditSchemaError(
                f"field {field!r}: expected {expected.__name__}, "
                f"got {type(data[field]).__name__}"
            )

    if "commits" in data:
        commits = data["commits"]
        if not isinstance(commits, list):
            raise AuditSchemaError(
                f"commits: expected list, got {type(commits).__name__}"
            )
        for i, sha in enumerate(commits):
            if not isinstance(sha, str):
                raise AuditSchemaError(
                    f"commits[{i}]: expected str, got {type(sha).__name__}"
                )

    # Plan (optional)
    if data.get("plan") is not None:
        _validate_plan(data["plan"])

    # Asks (optional list)
    asks = data.get("asks") or []
    if not isinstance(asks, list):
        raise AuditSchemaError(f"asks: expected list, got {type(asks).__name__}")
    for i, ask in enumerate(asks):
        _validate_ask(ask, index=i)

    # Tests (optional)
    if data.get("tests_before") is not None:
        _validate_test_result(data["tests_before"], path="tests_before")
    if data.get("tests_after") is not None:
        _validate_test_result(data["tests_after"], path="tests_after")

    # Events
    events = data.get("events") or []
    if not isinstance(events, list):
        raise AuditSchemaError(f"events: expected list, got {type(events).__name__}")
    for i, evt in enumerate(events):
        if not isinstance(evt, dict):
            raise AuditSchemaError(
                f"events[{i}]: expected object, got {type(evt).__name__}"
            )
        for field in ("at", "kind"):
            if field not in evt or not isinstance(evt[field], str):
                raise AuditSchemaError(
                    f"events[{i}].{field}: required string"
                )


def _validate_plan(plan: Any) -> None:
    if not isinstance(plan, dict):
        raise AuditSchemaError(f"plan: expected object, got {type(plan).__name__}")
    file_edits = plan.get("file_edits") or []
    if not isinstance(file_edits, list):
        raise AuditSchemaError(
            f"plan.file_edits: expected list, got {type(file_edits).__name__}"
        )
    for i, edit in enumerate(file_edits):
        if not isinstance(edit, dict):
            raise AuditSchemaError(
                f"plan.file_edits[{i}]: expected object, "
                f"got {type(edit).__name__}"
            )
        for field in _REQUIRED_FILE_EDIT:
            if field not in edit:
                raise AuditSchemaError(
                    f"plan.file_edits[{i}].{field}: required"
                )
            if not isinstance(edit[field], str):
                raise AuditSchemaError(
                    f"plan.file_edits[{i}].{field}: expected str, "
                    f"got {type(edit[field]).__name__}"
                )
    namespaces = plan.get("affected_namespaces") or []
    if not isinstance(namespaces, list):
        raise AuditSchemaError(
            f"plan.affected_namespaces: expected list, "
            f"got {type(namespaces).__name__}"
        )


def _validate_ask(ask: Any, *, index: int) -> None:
    if not isinstance(ask, dict):
        raise AuditSchemaError(
            f"asks[{index}]: expected object, got {type(ask).__name__}"
        )
    for field in _REQUIRED_ASK:
        if field not in ask or not isinstance(ask[field], str):
            raise AuditSchemaError(f"asks[{index}].{field}: required string")
    raw_resp = ask.get("user_response")
    if raw_resp is not None:
        try:
            AskResponse(raw_resp)
        except ValueError as exc:
            raise AuditSchemaError(
                f"asks[{index}].user_response: invalid value {raw_resp!r}; "
                f"must be one of {[r.value for r in AskResponse]} or null"
            ) from exc


def _validate_test_result(tr: Any, *, path: str) -> None:
    if not isinstance(tr, dict):
        raise AuditSchemaError(f"{path}: expected object, got {type(tr).__name__}")
    for field, expected in _REQUIRED_TEST_RESULT:
        if field not in tr:
            raise AuditSchemaError(f"{path}.{field}: required")
        if not isinstance(tr[field], int) or isinstance(tr[field], bool):
            raise AuditSchemaError(
                f"{path}.{field}: expected int, got {type(tr[field]).__name__}"
            )

"""On-disk persistence for ExecutionRecord audit JSONs.

Audit files live at `.planning/skill_executions/EXEC-<id>.json` and
are CHECKED INTO THE REPO (not gitignored, unlike proposals + dev_queue).
The reason: per Q3(b), the CI gate verifies that every PR carrying an
`Exec-Id: EXEC-XXX` stamp has its matching audit file in the same
PR's tree. If audits were gitignored, the gate couldn't see them.

Atomic writes via tmp+rename so a crash mid-write doesn't leave a
partial file. A read of a partial / malformed file raises
AuditSchemaError, never returns half-data.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path

from well_harness.skill_executor.errors import AuditSchemaError
from well_harness.skill_executor.models import (
    ExecutionRecord,
    deserialize_record,
    serialize_record,
)
from well_harness.skill_executor.schema import validate_audit_dict


AUDIT_DIR_NAME: str = ".planning/skill_executions"
# EXEC-YYYYMMDDTHHMMSSffffff-{6hex} — 8 digits, literal T, 12 digits,
# dash, 6 hex chars. Mirrors proposal id (P44-03 microsecond format).
_EXEC_ID_PATTERN = re.compile(r"^EXEC-\d{8}T\d{12}-[0-9a-f]{6}$")
_AUDIT_LOCK = threading.Lock()


def audit_dir() -> Path:
    """Resolve the audit directory.

    Order:
      1. WORKBENCH_SKILL_EXECUTIONS_DIR (test isolation override)
      2. <repo_root>/.planning/skill_executions/ (production)

    Created on first call (parents=True, exist_ok=True). Repo root
    is resolved from this file's location, three levels up.
    """
    override = os.environ.get("WORKBENCH_SKILL_EXECUTIONS_DIR")
    if override:
        path = Path(override).expanduser()
    else:
        path = Path(__file__).resolve().parents[3] / AUDIT_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_execution_id() -> str:
    """Generate `EXEC-YYYYMMDDTHHMMSSffffff-{6hex}`. Mirrors the
    proposal-id format (P44-03 microsecond resolution + secrets
    hex suffix) so two executions started in the same microsecond
    don't collide."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    suffix = secrets.token_hex(3)
    return f"EXEC-{timestamp}-{suffix}"


def _audit_path(exec_id: str) -> Path:
    """Map exec_id → file path. Validates the id shape so we can't
    trick the writer into creating a file outside the audit dir
    (e.g. exec_id='../foo' would escape if not validated)."""
    if not _EXEC_ID_PATTERN.match(exec_id):
        raise AuditSchemaError(
            f"invalid exec_id shape: {exec_id!r}; expected "
            f"EXEC-YYYYMMDDTHHMMSSffffff-{{6hex}}"
        )
    return audit_dir() / f"{exec_id}.json"


def write_audit(record: ExecutionRecord) -> Path:
    """Persist (or update) an audit record. Returns the file path.

    Validates the serialized form before writing — if the record
    would produce an invalid JSON shape, we refuse to write rather
    than save bad data the CI gate would later reject.

    Atomic: writes to a sibling tmp file then renames. The lock
    serializes concurrent writers in the same process; cross-
    process safety relies on filesystem rename atomicity.
    """
    target = _audit_path(record.exec_id)
    text = serialize_record(record)
    # Round-trip validate so we never persist a record that won't
    # parse. (Catches any to_json/from_json drift early.)
    parsed = json.loads(text)
    validate_audit_dict(parsed)
    with _AUDIT_LOCK:
        tmp = target.with_suffix(".json.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, target)
    return target


def read_audit(exec_id: str) -> ExecutionRecord:
    """Load and validate an audit by id. Raises AuditSchemaError
    if the file is missing, unparseable, or violates the schema.

    The validator runs against the raw dict before any
    dataclass-construction so a future schema_version mismatch
    surfaces as a clear error rather than a confusing field-missing
    crash deeper in dataclass code.
    """
    path = _audit_path(exec_id)
    if not path.is_file():
        raise AuditSchemaError(f"audit not found: {exec_id}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditSchemaError(f"audit unreadable: {exec_id}: {exc}") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AuditSchemaError(
            f"audit not valid JSON: {exec_id}: {exc}"
        ) from exc
    validate_audit_dict(parsed)
    return deserialize_record(text)


def list_audits(
    *,
    proposal_id: str | None = None,
    state_filter: str | None = None,
) -> list[ExecutionRecord]:
    """Return every audit record in the directory. Optional filters
    narrow the result set. Sorted newest-first by exec_id (which is
    timestamp-prefixed, so lexical sort = chronological reverse).

    Bad / unreadable audit files are SKIPPED with no error — a
    half-written file shouldn't break list views. The CI gate
    catches malformed audits at PR time; this lister stays
    permissive for runtime UI use.
    """
    out: list[ExecutionRecord] = []
    for path in sorted(audit_dir().glob("EXEC-*.json"), reverse=True):
        try:
            text = path.read_text(encoding="utf-8")
            parsed = json.loads(text)
            validate_audit_dict(parsed)
            record = deserialize_record(text)
        except (OSError, json.JSONDecodeError, AuditSchemaError):
            continue
        if proposal_id and record.proposal_id != proposal_id:
            continue
        if state_filter and record.state != state_filter:
            continue
        out.append(record)
    return out

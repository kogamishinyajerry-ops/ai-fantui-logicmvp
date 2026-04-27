"""P48-01 — skill executor audit persistence + schema validator.

Locks down: write+read round-trip, schema rejection of malformed
records, atomic write semantics, listing + filtering, exec_id
shape enforcement.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from well_harness.skill_executor.audit import (
    AUDIT_DIR_NAME,
    audit_dir,
    list_audits,
    new_execution_id,
    read_audit,
    write_audit,
)
from well_harness.skill_executor.errors import AuditSchemaError
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    FileEdit,
    PlannedChange,
    TestResult,
)
from well_harness.skill_executor.schema import validate_audit_dict
from well_harness.skill_executor.states import ExecutionState


@pytest.fixture(autouse=True)
def _isolate_audit_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


_UNSET = object()


def _stub_record(*, exec_id=_UNSET, **overrides) -> ExecutionRecord:
    """Helper to build a minimal valid ExecutionRecord. Override
    any field via kwargs. Pass `exec_id=""` (or any string) to
    inject literally that value — the sentinel means "I'm not
    setting this, generate one"."""
    base = dict(
        exec_id=new_execution_id() if exec_id is _UNSET else exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
    )
    base.update(overrides)
    return ExecutionRecord(**base)


# ─── 1. EXEC-id shape ──────────────────────────────────────────────────


def test_new_execution_id_format():
    eid = new_execution_id()
    assert re.match(r"^EXEC-\d{8}T\d{12}-[0-9a-f]{6}$", eid), (
        f"new_execution_id() returned {eid!r}; expected "
        f"EXEC-YYYYMMDDTHHMMSSffffff-{{6hex}}"
    )


def test_two_consecutive_ids_are_unique():
    ids = {new_execution_id() for _ in range(10)}
    assert len(ids) == 10


# ─── 2. Audit dir resolution ───────────────────────────────────────────


def test_audit_dir_uses_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "custom"))
    path = audit_dir()
    assert path == tmp_path / "custom"
    assert path.is_dir()


def test_audit_dir_constant_matches_layout():
    """The constant `.planning/skill_executions` is referenced from
    multiple places (this test, the gitignore allowance, the CI
    gate). Lock the canonical name here."""
    assert AUDIT_DIR_NAME == ".planning/skill_executions"


# ─── 3. Write + read round-trip ────────────────────────────────────────


def test_write_then_read_preserves_record():
    record = _stub_record()
    write_audit(record)
    rt = read_audit(record.exec_id)
    assert rt.exec_id == record.exec_id
    assert rt.kind == record.kind
    assert rt.audit_source == record.audit_source


def test_write_full_record_round_trip():
    record = _stub_record(
        plan=PlannedChange(
            rationale="r",
            file_edits=[FileEdit(path="x.py", old_snippet="a", new_snippet="b")],
            affected_namespaces=["logic_truth"],
        ),
        asks=[
            Ask(
                ask_id="ASK-1",
                question="q",
                user_response=AskResponse.APPROVED,
                user_responded_at="2026-04-27T12:03:00Z",
            )
        ],
        tests_before=TestResult(passed=1448, failed=0),
        tests_after=TestResult(passed=1450, failed=0),
        commits=["sha1", "sha2"],
        events=[
            ExecutionEvent(
                at="2026-04-27T12:00:00Z",
                kind="state_transition",
                from_state="INIT",
                to_state="PLANNING",
            )
        ],
    )
    write_audit(record)
    rt = read_audit(record.exec_id)
    assert rt.plan is not None
    assert len(rt.plan.file_edits) == 1
    assert rt.asks[0].user_response == AskResponse.APPROVED
    assert rt.tests_after.passed == 1450
    assert rt.commits == ["sha1", "sha2"]
    assert rt.events[0].from_state == "INIT"


def test_overwrite_is_idempotent():
    """Audits are mutable in-flight (state advances, asks resolve).
    The writer must accept an existing file, replacing it."""
    record = _stub_record()
    write_audit(record)
    record.state = ExecutionState.PLANNING.value
    write_audit(record)
    rt = read_audit(record.exec_id)
    assert rt.state == "PLANNING"


# ─── 4. EXEC-id shape enforcement ──────────────────────────────────────


@pytest.mark.parametrize(
    "bad_id",
    [
        "exec-foo",  # wrong prefix
        "EXEC-too-short-abc123",  # malformed timestamp
        "EXEC-20260427T120000123456-XYZ123",  # non-hex suffix
        "EXEC-20260427T120000123456",  # missing suffix
        "../EXEC-20260427T120000123456-abc123",  # path traversal
        "",
    ],
)
def test_write_rejects_malformed_exec_id(bad_id):
    record = _stub_record(exec_id=bad_id)
    with pytest.raises(AuditSchemaError):
        write_audit(record)


def test_read_rejects_malformed_exec_id():
    with pytest.raises(AuditSchemaError):
        read_audit("not-an-exec-id")


def test_read_missing_audit_raises():
    with pytest.raises(AuditSchemaError) as exc:
        read_audit("EXEC-20260427T120000000000-abc123")
    assert "not found" in str(exc.value)


# ─── 5. Validator rejects malformed records ────────────────────────────


def test_validator_rejects_missing_exec_id():
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict({})
    assert "exec_id" in str(exc.value)


def test_validator_rejects_unknown_state():
    record = _stub_record()
    js = record.to_json()
    js["state"] = "NEVER_HEARD_OF_IT"
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    assert "state" in str(exc.value)


def test_validator_rejects_unknown_kind():
    record = _stub_record()
    js = record.to_json()
    js["kind"] = "explode"
    with pytest.raises(AuditSchemaError):
        validate_audit_dict(js)


def test_validator_rejects_wrong_schema_version():
    record = _stub_record()
    js = record.to_json()
    js["schema_version"] = 999
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    assert "schema_version" in str(exc.value)


def test_validator_rejects_malformed_file_edit():
    record = _stub_record(
        plan=PlannedChange(rationale="r", file_edits=[]),
    )
    js = record.to_json()
    # Inject a malformed edit directly into the dict
    js["plan"]["file_edits"] = [{"path": "x.py"}]  # missing old/new snippet
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    assert "file_edits" in str(exc.value)


def test_validator_rejects_unknown_ask_response():
    record = _stub_record(
        asks=[Ask(ask_id="ASK-1", question="q")],
    )
    js = record.to_json()
    js["asks"][0]["user_response"] = "maybe"
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    assert "user_response" in str(exc.value)


def test_validator_accepts_minimum_record():
    record = _stub_record()
    validate_audit_dict(record.to_json())


def test_validator_accepts_backfill_record():
    """Backfill records have audit_source='backfill' and may go
    straight to LANDED without intermediate states populated."""
    record = _stub_record(
        audit_source=AuditSource.BACKFILL,
        kind=ExecutionKind.BACKFILL,
        state=ExecutionState.LANDED.value,
        landed_sha="ec6f4fc",
    )
    validate_audit_dict(record.to_json())


# ─── 6. Atomic write semantics ─────────────────────────────────────────


def test_no_temp_file_left_behind_on_success():
    """The atomic-write path uses a `.json.tmp` sibling that's
    renamed onto the target. Successful writes must leave no
    temp."""
    record = _stub_record()
    write_audit(record)
    target_dir = audit_dir()
    tmps = list(target_dir.glob("*.tmp"))
    assert tmps == []


def test_write_refuses_invalid_record_before_creating_file():
    """If validation fails (e.g. bad state value snuck in), the
    writer should NOT leave a half-written file."""
    record = _stub_record()
    # Fabricate an invalid state through the dataclass field
    record.state = "EXPLODE"
    with pytest.raises(AuditSchemaError):
        write_audit(record)
    target_dir = audit_dir()
    files = list(target_dir.glob("EXEC-*.json"))
    assert files == [], (
        f"writer left a file behind despite validation failure: {files}"
    )


# ─── 7. List + filter ─────────────────────────────────────────────────


def test_list_returns_newest_first():
    a = _stub_record()
    b = _stub_record()  # generated later → larger timestamp
    write_audit(a)
    write_audit(b)
    listed = list_audits()
    assert [r.exec_id for r in listed][:2] == [b.exec_id, a.exec_id]


def test_list_filters_by_proposal_id():
    a = _stub_record(proposal_id="PROP-aaa")
    b = _stub_record(proposal_id="PROP-bbb")
    write_audit(a)
    write_audit(b)
    listed = list_audits(proposal_id="PROP-aaa")
    assert len(listed) == 1
    assert listed[0].proposal_id == "PROP-aaa"


def test_list_filters_by_state():
    a = _stub_record(state=ExecutionState.LANDED.value)
    b = _stub_record(state=ExecutionState.ASKING.value)
    write_audit(a)
    write_audit(b)
    asking = list_audits(state_filter="ASKING")
    assert [r.exec_id for r in asking] == [b.exec_id]


def test_list_skips_unparseable_files():
    """A file that's not valid JSON shouldn't break list views
    (the CI gate catches these at PR time; runtime UI must stay
    permissive)."""
    write_audit(_stub_record())
    bad = audit_dir() / "EXEC-20260427T120000999999-deadbe.json"
    bad.write_text("{ not json", encoding="utf-8")
    listed = list_audits()
    # The valid record is still returned; the bad one is silently
    # skipped.
    assert len(listed) == 1


def test_list_skips_schema_invalid_files():
    """File parses as JSON but doesn't conform to schema — still
    skipped, not raised."""
    write_audit(_stub_record())
    bad = audit_dir() / "EXEC-20260427T120000999999-deadbe.json"
    bad.write_text(json.dumps({"hello": "world"}) + "\n", encoding="utf-8")
    listed = list_audits()
    assert len(listed) == 1


# ─── 8. Validator messages point at the failing path ──────────────────


def test_validator_error_message_pinpoints_field():
    """A reviewer reading a CI failure should see exactly which
    field broke. Check the message contains the field name."""
    js = _stub_record().to_json()
    js["commits"] = "should be a list"
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    assert "commits" in str(exc.value)


def test_validator_error_message_includes_path_for_nested_field():
    record = _stub_record(
        plan=PlannedChange(
            rationale="r",
            file_edits=[FileEdit(path="x.py", old_snippet="a", new_snippet="b")],
        ),
    )
    js = record.to_json()
    js["plan"]["file_edits"][0]["new_snippet"] = 123  # wrong type
    with pytest.raises(AuditSchemaError) as exc:
        validate_audit_dict(js)
    msg = str(exc.value)
    assert "plan.file_edits[0].new_snippet" in msg

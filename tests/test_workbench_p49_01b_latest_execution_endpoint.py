"""P49-01b — per-proposal latest-execution endpoint.

Locks down: GET /api/proposals/<id>/execution returns the freshest
audit (newest first by exec_id), or 204 if none, regardless of
state — so the workbench inbox can render a state badge for every
proposal that has been through the executor.

This is the backend half. The frontend half (workbench.js renders
9-state badges) is exercised in isolation via the JS module's
state-mapping helper.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "skill_executions")
    )
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"))
    yield


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _get(server, path):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("GET", path)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8") if resp.length is not None else ""
    conn.close()
    if not raw:
        return resp.status, None
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _make_audit(
    exec_id: str,
    *,
    proposal_id: str,
    state: str = ExecutionState.LANDED.value,
    kind: ExecutionKind = ExecutionKind.MODIFY,
) -> ExecutionRecord:
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=kind,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:01:00Z",
        state=state,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="test", file_edits=[]),
    )
    write_audit(rec)
    return rec


# ─── 1. No audit yet → 204 ───────────────────────────────────────────


def test_returns_204_when_no_audit_for_proposal(server):
    status, body = _get(server, "/api/proposals/PROP-noexec/execution")
    assert status == 204
    assert body is None


# ─── 2. One audit → returns it ──────────────────────────────────────


def test_returns_audit_when_one_exists(server):
    _make_audit(
        "EXEC-20260427T120000000000-aaaaaa",
        proposal_id="PROP-test",
        state=ExecutionState.ASKING.value,
    )
    status, body = _get(server, "/api/proposals/PROP-test/execution")
    assert status == 200
    assert body["proposal_id"] == "PROP-test"
    assert body["state"] == "ASKING"
    assert body["exec_id"] == "EXEC-20260427T120000000000-aaaaaa"


# ─── 3. Multiple audits → newest first ─────────────────────────────


def test_returns_newest_audit_when_multiple_exist(server):
    _make_audit(
        "EXEC-20260427T100000000000-aaaaaa",
        proposal_id="PROP-multi",
        state=ExecutionState.FAILED.value,
    )
    _make_audit(
        "EXEC-20260427T110000000000-bbbbbb",
        proposal_id="PROP-multi",
        state=ExecutionState.ABORTED.value,
    )
    _make_audit(
        "EXEC-20260427T120000000000-cccccc",
        proposal_id="PROP-multi",
        state=ExecutionState.LANDED.value,
    )
    status, body = _get(server, "/api/proposals/PROP-multi/execution")
    assert status == 200
    assert body["exec_id"] == "EXEC-20260427T120000000000-cccccc"
    assert body["state"] == "LANDED"


# ─── 4. Other proposals' audits don't leak ─────────────────────────


def test_filters_by_proposal_id(server):
    _make_audit(
        "EXEC-20260427T100000000000-aaaaaa",
        proposal_id="PROP-other",
        state=ExecutionState.LANDED.value,
    )
    status, body = _get(server, "/api/proposals/PROP-test/execution")
    assert status == 204
    assert body is None


# ─── 5. Returns audit regardless of state (NOT just ASKING) ───────


@pytest.mark.parametrize(
    "idx,state",
    [
        (1, ExecutionState.INIT.value),
        (2, ExecutionState.PLANNING.value),
        (3, ExecutionState.ASKING.value),
        (4, ExecutionState.EDITING.value),
        (5, ExecutionState.TESTING.value),
        (6, ExecutionState.PR_OPEN.value),
        (7, ExecutionState.LANDED.value),
        (8, ExecutionState.ABORTED.value),
        (9, ExecutionState.FAILED.value),
    ],
)
def test_endpoint_returns_audit_for_any_state(server, idx, state):
    """The badge must render for ALL 9 states. The /pending
    endpoint only shows ASKING; this one is the badge feed
    that reflects whatever state the executor is currently in."""
    _make_audit(
        f"EXEC-20260427T12000000000{idx}-aaaaaa",
        proposal_id="PROP-state-test",
        state=state,
    )
    status, body = _get(server, "/api/proposals/PROP-state-test/execution")
    assert status == 200
    assert body["state"] == state


# ─── 6. Bad path → 400 ────────────────────────────────────────────


def test_empty_proposal_id_returns_400(server):
    status, body = _get(server, "/api/proposals//execution")
    assert status == 400
    assert body["error"] == "invalid_proposal_id"


# ─── 7. Backfill audits also count ───────────────────────────────


def test_inbox_card_includes_execution_badge_slot():
    """The proposal card template must include a slot the badge
    refresher can target. Lock down the data-attribute so renames
    in workbench.js don't silently break the wiring."""
    js = (
        REPO_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "workbench.js"
    ).read_text(encoding="utf-8")
    assert 'data-execution-badge-for=' in js
    assert "workbench-execution-badge-slot" in js


def test_workbench_js_defines_all_9_states():
    """The state→info map must cover every ExecutionState the
    backend can emit, otherwise badges fall back to 'unknown'."""
    js = (
        REPO_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "workbench.js"
    ).read_text(encoding="utf-8")
    assert "EXECUTION_STATE_INFO" in js
    for state in [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
        "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ]:
        # Each state appears as a key in the info map
        assert f"{state}:" in js, f"missing state {state} in EXECUTION_STATE_INFO"


def test_workbench_css_defines_all_9_state_styles():
    """Every state's CSS class must have a color rule so reviewers
    can distinguish them at a glance."""
    css = (
        REPO_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "workbench.css"
    ).read_text(encoding="utf-8")
    for css_class in [
        "init", "planning", "asking", "editing", "testing",
        "pr-open", "landed", "aborted", "failed",
    ]:
        assert (
            f'data-execution-css="{css_class}"' in css
        ), f"missing CSS rule for execution-css={css_class}"


def test_workbench_js_exposes_render_helper_on_window():
    """The renderer is exposed on window so console debugging /
    future automated UI tests can call it directly."""
    js = (
        REPO_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "workbench.js"
    ).read_text(encoding="utf-8")
    assert "window.__WB_renderExecutionBadge" in js
    assert "window.__WB_EXECUTION_STATE_INFO" in js


def test_backfill_audit_returned_with_audit_source_marker(server):
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000000-bf1234",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-backfilled",
        kind=ExecutionKind.BACKFILL,
        audit_source=AuditSource.BACKFILL,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:00:00Z",
        state=ExecutionState.LANDED.value,
        executor_version="0.0-backfill",
        plan=PlannedChange(rationale="backfilled", file_edits=[]),
    )
    write_audit(rec)
    status, body = _get(server, "/api/proposals/PROP-backfilled/execution")
    assert status == 200
    assert body["audit_source"] == "backfill"
    assert body["kind"] == "backfill"

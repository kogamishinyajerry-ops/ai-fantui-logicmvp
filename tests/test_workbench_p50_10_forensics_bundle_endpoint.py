"""P50-10 — forensics bundle HTTP endpoint.

Locks down the wire-up: GET /api/skill-executions/forensics-bundle
returns 200 with Content-Type=application/zip + a download
filename, the body parses as a valid zip, and the contents match
what build_bundle would produce directly.
"""

from __future__ import annotations

import http.client
import io
import json
import threading
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.forensics_bundle import (
    BUNDLE_AUDITS_DIR,
    BUNDLE_HISTORY_NAME,
    BUNDLE_MANIFEST_NAME,
    BUNDLE_README_NAME,
)
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.slo_history import SLO_HISTORY_FILENAME
from well_harness.skill_executor.states import ExecutionState


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
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
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read()
    headers = dict(resp.getheaders())
    conn.close()
    return resp.status, headers, body


def _audit(exec_id, *, started_at="2026-04-27T12:00:00Z",
           state=ExecutionState.LANDED.value):
    write_audit(
        ExecutionRecord(
            exec_id=exec_id,
            schema_version=AUDIT_SCHEMA_VERSION,
            proposal_id="PROP-x",
            kind=ExecutionKind.MODIFY,
            audit_source=AuditSource.LIVE,
            started_at=started_at,
            finished_at="2026-04-27T12:01:00Z",
            state=state,
            executor_version="0.1-test",
            plan=PlannedChange(rationale="x", file_edits=[]),
        )
    )


# ─── 1. Empty audit dir → still returns valid zip ─────────────────


def test_empty_dir_returns_zip_with_manifest(server):
    status, headers, body = _get(
        server, "/api/skill-executions/forensics-bundle",
    )
    assert status == 200
    # Content-Type is zip
    ct = headers.get("Content-Type", "")
    assert ct == "application/zip"
    # Download filename header set
    cd = headers.get("Content-Disposition", "")
    assert "attachment" in cd
    assert "forensics_" in cd and ".zip" in cd
    # Body parses as a valid zip
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    names = zf.namelist()
    assert BUNDLE_MANIFEST_NAME in names
    assert BUNDLE_README_NAME in names
    assert BUNDLE_HISTORY_NAME in names


# ─── 2. Populated dir: audits land in zip ─────────────────────────


def test_populated_dir_includes_audits(server):
    _audit("EXEC-20260427T120000000001-aaaaaa")
    _audit("EXEC-20260427T120000000002-bbbbbb")
    status, _, body = _get(
        server, "/api/skill-executions/forensics-bundle",
    )
    assert status == 200
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    audit_files = [
        n for n in zf.namelist()
        if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
    ]
    assert len(audit_files) == 2
    # Manifest reports the same count
    manifest = json.loads(zf.read(BUNDLE_MANIFEST_NAME).decode("utf-8"))
    assert manifest["audit_count"] == 2


# ─── 3. limit query param ─────────────────────────────────────────


def test_limit_query_truncates(server):
    for i in range(5):
        _audit(f"EXEC-20260427T12000000{i:04d}-aaaaaa")
    _, _, body = _get(
        server, "/api/skill-executions/forensics-bundle?limit=2",
    )
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    audit_files = [
        n for n in zf.namelist()
        if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
    ]
    assert len(audit_files) == 2
    manifest = json.loads(zf.read(BUNDLE_MANIFEST_NAME).decode("utf-8"))
    assert manifest["limit_filter"] == 2


def test_invalid_limit_falls_back_to_default(server):
    """?limit=not-a-number → silently use default 100. Don't 400
    on a query-string typo."""
    _audit("EXEC-20260427T120000000001-aaaaaa")
    status, _, body = _get(
        server, "/api/skill-executions/forensics-bundle?limit=banana",
    )
    assert status == 200
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    manifest = json.loads(zf.read(BUNDLE_MANIFEST_NAME).decode("utf-8"))
    assert manifest["limit_filter"] == 100


# ─── 4. since query param ─────────────────────────────────────────


def test_since_query_drops_old_audits(server):
    _audit(
        "EXEC-20260427T110000000000-aaaaaa",
        started_at="2026-04-27T11:00:00Z",
    )
    _audit(
        "EXEC-20260427T130000000000-bbbbbb",
        started_at="2026-04-27T13:00:00Z",
    )
    _, _, body = _get(
        server,
        "/api/skill-executions/forensics-bundle?since=2026-04-27T12:00:00Z",
    )
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    manifest = json.loads(zf.read(BUNDLE_MANIFEST_NAME).decode("utf-8"))
    assert manifest["audit_count"] == 1
    assert manifest["since_filter"] == "2026-04-27T12:00:00Z"


# ─── 5. slo_history.jsonl ride-along through endpoint ─────────────


def test_slo_history_included_in_bundle(server, tmp_path):
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True, exist_ok=True)
    history_text = (
        '{"ts": "2026-04-27T13:00:00Z", "from_severity": "none", '
        '"to_severity": "red", "breach_slos": ["pass_rate"], '
        '"snapshot": {"total": 6}}\n'
    )
    (audit_dir / SLO_HISTORY_FILENAME).write_text(
        history_text, encoding="utf-8",
    )
    _, _, body = _get(server, "/api/skill-executions/forensics-bundle")
    zf = zipfile.ZipFile(io.BytesIO(body), "r")
    history_in_zip = zf.read(BUNDLE_HISTORY_NAME).decode("utf-8")
    assert history_in_zip == history_text


# ─── 6. Filename header is filesystem-safe ────────────────────────


def test_download_filename_has_no_colons(server):
    """Colons in filenames break Windows + many download UIs.
    The endpoint's suggested filename uses compact ISO without
    them."""
    _, headers, _ = _get(
        server, "/api/skill-executions/forensics-bundle",
    )
    cd = headers.get("Content-Disposition", "")
    # Extract the filename="..." part
    assert "filename=" in cd
    # Find the quoted filename
    start = cd.find('filename="') + len('filename="')
    end = cd.find('"', start)
    fname = cd[start:end]
    assert ":" not in fname
    assert fname.endswith(".zip")

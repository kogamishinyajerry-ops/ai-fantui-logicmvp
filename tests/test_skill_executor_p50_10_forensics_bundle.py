"""P50-10 — forensics bundle unit tests.

Locks down: build_bundle assembles a valid ZIP with the expected
layout (manifest/README/audits/history); since-filter drops old
audits; limit truncates newest-first; corrupt files don't block
the bundle; manifest accurately reports what was included.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.forensics_bundle import (
    BUNDLE_AUDITS_DIR,
    BUNDLE_HISTORY_NAME,
    BUNDLE_MANIFEST_NAME,
    BUNDLE_README_NAME,
    BundleManifest,
    build_bundle,
    default_bundle_filename,
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


# ─── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
    yield


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


def _audit_dir(tmp_path: Path) -> Path:
    return tmp_path / "execs"


def _open_bundle(zip_bytes: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(zip_bytes), "r")


# ─── 1. Empty audit dir → bundle still valid ──────────────────────


def test_empty_audit_dir_produces_valid_zip(tmp_path):
    """Bundle on a fresh deploy works — no audits, but the user
    might still want the manifest as proof of "nothing here yet"."""
    audit_dir = _audit_dir(tmp_path)
    audit_dir.mkdir(parents=True, exist_ok=True)
    zip_bytes, manifest = build_bundle(audit_dir)
    assert manifest.audit_count == 0
    assert manifest.history_line_count == 0
    with _open_bundle(zip_bytes) as zf:
        names = zf.namelist()
        # Always-present scaffolding
        assert BUNDLE_MANIFEST_NAME in names
        assert BUNDLE_README_NAME in names
        assert BUNDLE_HISTORY_NAME in names
        # No audit/ entries when input was empty
        assert all(not n.startswith(f"{BUNDLE_AUDITS_DIR}/") for n in names)


# ─── 2. Audits land at audits/<exec_id>.json ─────────────────────


def test_audits_included_under_subdir(tmp_path):
    _audit("EXEC-20260427T120000000001-aaaaaa")
    _audit("EXEC-20260427T120000000002-bbbbbb")
    audit_dir = _audit_dir(tmp_path)
    zip_bytes, manifest = build_bundle(audit_dir)
    assert manifest.audit_count == 2
    with _open_bundle(zip_bytes) as zf:
        audit_files = [
            n for n in zf.namelist() if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
        ]
        assert len(audit_files) == 2
        assert all(n.endswith(".json") for n in audit_files)
        # Each is independently parseable
        for n in audit_files:
            parsed = json.loads(zf.read(n).decode("utf-8"))
            assert parsed["exec_id"].startswith("EXEC-")


# ─── 3. limit truncates newest-first ──────────────────────────────


def test_limit_keeps_newest(tmp_path):
    """limit=2 over 5 audits keeps the two newest exec-ids
    (which sort lexically as the latest timestamps)."""
    for i in range(5):
        _audit(f"EXEC-20260427T12000000{i:04d}-aaaaaa")
    audit_dir = _audit_dir(tmp_path)
    zip_bytes, manifest = build_bundle(audit_dir, limit=2)
    assert manifest.audit_count == 2
    with _open_bundle(zip_bytes) as zf:
        names = sorted(
            n for n in zf.namelist()
            if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
        )
        # Newest two have the highest suffixes (0003, 0004)
        assert names[0].endswith("0003-aaaaaa.json")
        assert names[1].endswith("0004-aaaaaa.json")


def test_limit_none_keeps_everything(tmp_path):
    for i in range(7):
        _audit(f"EXEC-20260427T12000000{i:04d}-aaaaaa")
    audit_dir = _audit_dir(tmp_path)
    _, manifest = build_bundle(audit_dir, limit=None)
    assert manifest.audit_count == 7


# ─── 4. since-filter drops old audits ─────────────────────────────


def test_since_filter_drops_old_audits(tmp_path):
    """Old audit at 11:00 + new audit at 13:00 + cutoff at 12:00
    → only the newer one survives."""
    _audit(
        "EXEC-20260427T110000000000-aaaaaa",
        started_at="2026-04-27T11:00:00Z",
    )
    _audit(
        "EXEC-20260427T130000000000-bbbbbb",
        started_at="2026-04-27T13:00:00Z",
    )
    audit_dir = _audit_dir(tmp_path)
    zip_bytes, manifest = build_bundle(
        audit_dir, since="2026-04-27T12:00:00Z",
    )
    assert manifest.audit_count == 1
    with _open_bundle(zip_bytes) as zf:
        kept = [
            n for n in zf.namelist()
            if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
        ]
        assert len(kept) == 1
        assert kept[0].endswith("130000000000-bbbbbb.json")


def test_since_filter_inclusive_at_boundary(tmp_path):
    """Audit started exactly at the cutoff timestamp survives —
    avoids confusing edge-case loss when polling boundaries align."""
    _audit(
        "EXEC-20260427T120000000000-aaaaaa",
        started_at="2026-04-27T12:00:00Z",
    )
    audit_dir = _audit_dir(tmp_path)
    _, manifest = build_bundle(
        audit_dir, since="2026-04-27T12:00:00Z",
    )
    assert manifest.audit_count == 1


# ─── 5. slo_history.jsonl ride-along ──────────────────────────────


def test_history_file_included_when_present(tmp_path):
    audit_dir = _audit_dir(tmp_path)
    audit_dir.mkdir(parents=True, exist_ok=True)
    history_content = (
        '{"ts": "2026-04-27T13:00:00Z", "from_severity": "none", '
        '"to_severity": "red", "breach_slos": ["pass_rate"], '
        '"snapshot": {"total": 6}}\n'
    )
    (audit_dir / SLO_HISTORY_FILENAME).write_text(
        history_content, encoding="utf-8",
    )
    zip_bytes, manifest = build_bundle(audit_dir)
    assert manifest.history_line_count == 1
    with _open_bundle(zip_bytes) as zf:
        assert BUNDLE_HISTORY_NAME in zf.namelist()
        assert zf.read(BUNDLE_HISTORY_NAME).decode("utf-8") == history_content


def test_history_missing_treated_as_empty(tmp_path):
    """No history file (no transitions yet) → empty file in zip,
    not a missing entry; consumer can rely on its presence."""
    audit_dir = _audit_dir(tmp_path)
    audit_dir.mkdir(parents=True, exist_ok=True)
    zip_bytes, manifest = build_bundle(audit_dir)
    assert manifest.history_line_count == 0
    with _open_bundle(zip_bytes) as zf:
        assert BUNDLE_HISTORY_NAME in zf.namelist()
        assert zf.read(BUNDLE_HISTORY_NAME) == b""


# ─── 6. Manifest accuracy ──────────────────────────────────────────


def test_manifest_records_filters(tmp_path):
    audit_dir = _audit_dir(tmp_path)
    audit_dir.mkdir(parents=True, exist_ok=True)
    _, manifest = build_bundle(
        audit_dir, since="2026-04-27T11:00:00Z", limit=42,
    )
    assert manifest.since_filter == "2026-04-27T11:00:00Z"
    assert manifest.limit_filter == 42
    assert manifest.bundle_format_version == "p50-10"
    # created_at parses as ISO
    from datetime import datetime
    datetime.fromisoformat(
        manifest.created_at.replace("Z", "+00:00")
    )


def test_manifest_in_zip_matches_returned_manifest(tmp_path):
    """The manifest inside the zip is the same dict the build
    function returned — single source of truth, no drift."""
    _audit("EXEC-20260427T120000000001-aaaaaa")
    audit_dir = _audit_dir(tmp_path)
    zip_bytes, manifest = build_bundle(audit_dir)
    with _open_bundle(zip_bytes) as zf:
        in_zip = json.loads(zf.read(BUNDLE_MANIFEST_NAME).decode("utf-8"))
    assert in_zip["audit_count"] == manifest.audit_count
    assert in_zip["created_at"] == manifest.created_at
    assert in_zip["bundle_format_version"] == "p50-10"


def test_manifest_to_json_shape_stable():
    m = BundleManifest(
        created_at="2026-04-27T13:00:00Z",
        audit_count=10,
        history_line_count=3,
        since_filter="2026-04-27T11:00:00Z",
        limit_filter=100,
        audit_dir_name="execs",
    )
    j = m.to_json()
    assert set(j.keys()) == {
        "created_at", "audit_count", "history_line_count",
        "since_filter", "limit_filter", "audit_dir_name",
        "bundle_format_version",
    }


# ─── 7. README contains layout pointers ───────────────────────────


def test_readme_mentions_layout(tmp_path):
    audit_dir = _audit_dir(tmp_path)
    audit_dir.mkdir(parents=True, exist_ok=True)
    zip_bytes, _ = build_bundle(audit_dir)
    with _open_bundle(zip_bytes) as zf:
        readme = zf.read(BUNDLE_README_NAME).decode("utf-8")
    assert BUNDLE_AUDITS_DIR in readme
    assert BUNDLE_HISTORY_NAME in readme
    assert BUNDLE_MANIFEST_NAME in readme


# ─── 8. Default filename is filesystem-friendly ───────────────────


def test_default_filename_no_colons():
    """Colons break Windows + many download UIs. The default
    bundle filename uses compact ISO without them."""
    name = default_bundle_filename()
    assert name.startswith("forensics_")
    assert name.endswith(".zip")
    assert ":" not in name


# ─── 9. Corrupt audit doesn't block the bundle ────────────────────


def test_corrupt_audit_skipped(tmp_path):
    """A truncated audit JSON shouldn't break the download. The
    incident triage flow needs the bundle to be best-effort."""
    _audit("EXEC-20260427T120000000001-aaaaaa")
    # Drop a malformed file with the right name pattern
    audit_dir = _audit_dir(tmp_path)
    bad = audit_dir / "EXEC-20260427T120000000099-zzzzzz.json"
    bad.write_text("{this is not valid json", encoding="utf-8")
    # since-filter triggers per-file parse → corrupt file is dropped,
    # good file survives
    zip_bytes, manifest = build_bundle(
        audit_dir, since="2026-04-27T00:00:00Z",
    )
    assert manifest.audit_count == 1
    with _open_bundle(zip_bytes) as zf:
        kept = [
            n for n in zf.namelist()
            if n.startswith(f"{BUNDLE_AUDITS_DIR}/")
        ]
        assert len(kept) == 1
        assert "zzzzzz" not in kept[0]

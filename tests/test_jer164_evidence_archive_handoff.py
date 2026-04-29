from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_workbench_exposes_evidence_archive_handoff_controls() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'id="workbench-prepare-archive-btn"' in html
    assert 'id="workbench-download-archive-btn"' in html
    assert 'id="workbench-evidence-archive-output"' in html
    assert 'id="workbench-archive-status"' in html
    assert "Evidence archive" in html


def test_evidence_archive_manifest_includes_required_checksum_fields() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function buildWorkbenchEvidenceArchive" in js
    assert "function checksumEvidenceArchiveField" in js
    assert "function renderWorkbenchEvidenceArchive" in js
    assert "function downloadWorkbenchEvidenceArchive" in js
    assert "model_json_checksum" in js
    assert "diff_summary_checksum" in js
    assert "changerequest_body_checksum" in js
    assert "pr_proof_packet_checksum" in js
    assert "manifest_checksum" in js


def test_evidence_archive_is_draft_only_and_records_red_lines() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "missing_diff_fallback" in js
    assert "red_line_metadata" in js
    assert 'truth_level_impact: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "frozen_assets_modified: false" in js
    assert "live_linear_mutation: false" in js
    assert "No live Linear mutation" in js
    assert "api.linear.app" not in js

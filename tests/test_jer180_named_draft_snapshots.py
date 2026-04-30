from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_named_draft_snapshot_manager_controls_are_local_sandbox_only() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'id="workbench-draft-snapshot-manager"' in html
    assert 'id="workbench-draft-snapshot-name"' in html
    assert 'id="workbench-draft-snapshot-select"' in html
    assert 'id="workbench-save-draft-snapshot-btn"' in html
    assert 'id="workbench-restore-draft-snapshot-btn"' in html
    assert 'id="workbench-delete-draft-snapshot-btn"' in html
    assert 'id="workbench-draft-snapshot-status"' in html
    assert "Named snapshots are local sandbox evidence only. Truth effect: none." in html


def test_named_draft_snapshot_manifest_is_exported_and_archived() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "well-harness-editable-workbench-draft-snapshots-v1" in js
    assert "function saveNamedDraftSnapshot" in js
    assert "function restoreNamedDraftSnapshot" in js
    assert "function deleteNamedDraftSnapshot" in js
    assert "function buildDraftSnapshotManifestSummary" in js
    assert "draft_snapshot_manifest: buildDraftSnapshotManifestSummary()" in js
    assert "draft_snapshot_manifest: draftSnapshotManifest" in js
    assert "draft_snapshot_manifest_checksum" in js
    assert 'truth_level_impact: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_named_draft_snapshot_manager_has_stable_layout_styles() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert ".workbench-draft-snapshot-manager" in css
    assert ".workbench-draft-snapshot-actions" in css

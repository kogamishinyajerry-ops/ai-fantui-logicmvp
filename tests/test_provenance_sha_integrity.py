"""
P40-03 · Provenance SHA integrity regression guard (pytest default lane).

Runs scripts/verify_provenance_hashes.py as part of the default pytest suite.
Any drift in uploads/* SHA256 vs docs/provenance/sha_registry.yaml fails
immediately — no silent corruption of the provenance chain.

Three invariants enforced:
  1. sha_registry.yaml parses, version=1, files ≥ 2
  2. Every file in uploads/ is registered
  3. scripts/verify_provenance_hashes.py exits 0 (actual SHA ↔ registry match)

If this test fails, the diagnostic is actionable:
  - "verify_provenance_hashes.py exited N" + stderr shows exact file + reason
  - Triage: either the file was tampered (re-examine integrity) or the
    registry is stale (update via a dedicated Phase commit per the registry's
    head comment "Update protocol").

Authority: Kogami 2026-04-20 GATE-P40-PLAN Approved.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "docs" / "provenance" / "sha_registry.yaml"
VERIFIER_SCRIPT = REPO_ROOT / "scripts" / "verify_provenance_hashes.py"


def test_sha_registry_yaml_parses_and_has_minimum_entries() -> None:
    assert REGISTRY_PATH.exists(), (
        f"sha_registry.yaml is missing at {REGISTRY_PATH}"
    )
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data.get("version") == 1, (
        f"Registry version must be 1, got {data.get('version')!r}"
    )
    files = data.get("files")
    assert isinstance(files, list), "Registry must have `files:` list"
    assert len(files) >= 2, (
        f"Registry must register ≥ 2 uploads (P40 baseline); "
        f"got {len(files)}"
    )
    for entry in files:
        assert "path" in entry
        assert "sha256" in entry
        assert len(entry["sha256"]) == 64, (
            f"SHA256 must be 64 hex chars; got {entry['sha256']!r}"
        )


def test_all_uploads_are_registered() -> None:
    """Any file in uploads/ must appear in sha_registry.yaml `files:` list."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    registered = {f["path"] for f in data["files"]}

    uploads_dir = REPO_ROOT / "uploads"
    if not uploads_dir.exists():
        pytest.skip("uploads/ directory absent; nothing to register")

    actual_files = {
        str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        for p in uploads_dir.iterdir()
        if p.is_file()
    }

    missing = actual_files - registered
    assert not missing, (
        f"Unregistered files in uploads/: {sorted(missing)} · add entries to "
        f"docs/provenance/sha_registry.yaml (see Update protocol in head)."
    )


def test_verify_provenance_hashes_exits_clean() -> None:
    """Drives the top-level verifier script; any SHA / size drift → exit 1."""
    assert VERIFIER_SCRIPT.exists(), (
        f"verifier script missing at {VERIFIER_SCRIPT}"
    )
    result = subprocess.run(
        [sys.executable, str(VERIFIER_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"verify_provenance_hashes.py exited {result.returncode}.\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}\n"
        f"Triage: see docs/provenance/sha_registry.yaml Update protocol."
    )

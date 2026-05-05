from __future__ import annotations

from pathlib import Path

from tools.workbench_release_candidate_smoke import run_release_candidate_smoke


def test_release_candidate_smoke_exercises_core_operator_paths(tmp_path: Path) -> None:
    report = run_release_candidate_smoke(archive_root=tmp_path)

    assert report["kind"] == "well-harness-workbench-release-candidate-smoke-report"
    assert report["status"] == "pass"
    assert report["truth_level_impact"] == "none"
    assert report["certification_claim"] == "none"
    assert report["external_services"] == []

    steps = {step["name"]: step for step in report["steps"]}
    assert set(steps) == {
        "workbench_boot",
        "archive_bundle",
        "recent_archives",
        "archive_restore",
        "lever_fault_injection",
        "invalid_archive_restore",
    }
    assert all(step["ok"] for step in steps.values())
    assert steps["workbench_boot"]["status"] == 200
    assert steps["archive_restore"]["path"] == "/api/workbench/archive-restore"
    assert steps["lever_fault_injection"]["path"] == "/api/lever-snapshot"
    assert steps["invalid_archive_restore"]["status"] == 400

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_repair_slices.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_approved_repair_slices_artifact.py"
SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_repair_slices_summary_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _run_approved_repair_slices(artifact_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(artifact_dir),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_approved_repair_slices_artifact_checker_validates_summary_and_child_exports(
    tmp_path: Path,
) -> None:
    _run_approved_repair_slices(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["gate_id"] == "approved-repair-slices"
    assert payload["summary_valid"] is True
    assert payload["summary_schema_valid"] is True
    assert payload["summary_schema"] == SUMMARY_SCHEMA_ID
    assert payload["kind"] == "ai-fantui-approved-repair-slices-summary"
    assert payload["child_review_exports_valid"] is True
    assert payload["slice_order"] == [
        "first-approved-candidate-repair-slice",
        "evidence-approved-candidate-repair-slice",
    ]
    assert payload["aggregate"] == {
        "slice_count": 2,
        "passed": 2,
        "converged": 2,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["mismatches"] == []
    assert Path(payload["artifact_paths"]["summary"]).exists()


def test_approved_repair_slices_artifact_checker_reports_summary_drift(
    tmp_path: Path,
) -> None:
    _run_approved_repair_slices(tmp_path)
    summary_path = tmp_path / "approved_repair_slices_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["aggregate"]["open_findings"] = ["DRIFTED_FINDING"]
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["summary_valid"] is False
    assert payload["summary_schema_valid"] is False
    assert payload["child_review_exports_valid"] is True
    assert "aggregate.open_findings must be empty" in payload["mismatches"]

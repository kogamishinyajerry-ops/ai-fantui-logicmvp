from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_candidate_task_queue.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_approved_candidate_task_queue_artifact.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_candidate_task_queue_summary_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _run_approved_candidate_task_queue(artifact_dir: Path) -> None:
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
        timeout=90,
    )
    assert result.returncode == 0, result.stderr


def test_approved_candidate_task_queue_artifact_checker_validates_summary_and_child_exports(
    tmp_path: Path,
) -> None:
    _run_approved_candidate_task_queue(tmp_path)

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
    assert payload["gate_id"] == "approved-candidate-task-queue"
    assert payload["kind"] == "ai-fantui-approved-candidate-task-queue-summary"
    assert payload["summary_schema"] == SUMMARY_SCHEMA_ID
    assert payload["summary_schema_valid"] is True
    assert payload["summary_valid"] is True
    assert payload["child_review_exports_valid"] is True
    assert payload["queue_order"] == [
        "queue-safety-priority-repair",
        "queue-evidence-simulation-result-repair",
        "queue-evidence-test-result-missing-repair",
    ]
    assert payload["aggregate"] == {
        "task_count": 3,
        "passed": 3,
        "preflight_passed": 3,
        "executed_limited": 3,
        "converged": 3,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["mismatches"] == []
    assert Path(payload["artifact_paths"]["summary"]).exists()
    assert len(payload["artifact_paths"]["child_review_exports"]) == 3


def test_approved_candidate_task_queue_artifact_checker_reports_summary_drift(
    tmp_path: Path,
) -> None:
    _run_approved_candidate_task_queue(tmp_path)
    summary_path = tmp_path / "approved_candidate_task_queue_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["items"][0]["preflight"]["status"] = "fail"
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
    assert any("preflight.status must be pass" in item for item in payload["mismatches"])


def test_approved_candidate_task_queue_checker_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "verify-approved-candidate-task-queue-artifact" in makefile
    assert "scripts/verify_approved_candidate_task_queue_artifact.py --format json" in makefile

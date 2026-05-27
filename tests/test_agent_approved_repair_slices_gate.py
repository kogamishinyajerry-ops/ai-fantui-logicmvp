from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_repair_slices.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
APPROVED_REPAIR_SLICES_COMMAND = (
    "PYTHONPATH=src:. python3 scripts/run_approved_repair_slices.py --format json"
)
APPROVED_REPAIR_SLICES_ARTIFACT_CHECK_COMMAND = (
    "PYTHONPATH=src:. python3 scripts/verify_approved_repair_slices_artifact.py --format json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_approved_repair_slices_gate_runs_safety_then_evidence_to_summary(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
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
    assert payload["slice_order"] == [
        "first-approved-candidate-repair-slice",
        "evidence-approved-candidate-repair-slice",
    ]
    assert payload["deterministic_gates"] == {
        "safety_slice": "pass",
        "evidence_slice": "pass",
        "review_packet_exports": "pass",
        "local_gate": "pass",
    }
    assert payload["aggregate"] == {
        "slice_count": 2,
        "passed": 2,
        "converged": 2,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }

    assert [item["slice_id"] for item in payload["slices"]] == payload["slice_order"]
    assert [item["status"] for item in payload["slices"]] == ["pass", "pass"]
    assert [item["reviewer_status"] for item in payload["slices"]] == [
        "converged",
        "converged",
    ]
    assert [item["selected_task_id"] for item in payload["slices"]] == [
        "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "TASK-CE-EV-SIMULATION-RESULT-FAILED",
    ]

    summary_path = Path(payload["artifact_paths"]["summary"])
    assert summary_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8")) == payload

    for slice_summary in payload["slices"]:
        review_export_path = Path(slice_summary["artifact_paths"]["candidate_review_packet_export"])
        assert review_export_path.exists()
        review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
        validate_candidate_review_packet_export(review_export)
        assert review_export["review_packet"]["reviewer"]["status"] == "converged"


def test_approved_repair_slices_gate_is_wired_into_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "approved-repair-slices" in makefile
    assert "scripts/run_approved_repair_slices.py --format json" in makefile
    assert "verify-approved-repair-slices-artifact" in makefile
    assert "scripts/verify_approved_repair_slices_artifact.py --format json" in makefile
    assert "first-candidate-repair-slice" in makefile
    assert "evidence-candidate-repair-slice" in makefile


def test_make_test_gate_runs_artifact_checker_before_pytest() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    test_line = next(line for line in makefile.splitlines() if line.startswith("test:"))
    test_dependencies = test_line.removeprefix("test:").split()
    assert "review-packet-export-regression" in test_dependencies
    assert "verify-approved-repair-slices-artifact" in test_dependencies
    assert test_dependencies.index(
        "review-packet-export-regression"
    ) < test_dependencies.index("verify-approved-repair-slices-artifact")
    assert "python3 -m pytest tests/" in makefile

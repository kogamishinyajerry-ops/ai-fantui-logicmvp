from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_m1_review_package_v0_1.schema.json"
)
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "multi_agent_m1_review_package_v0_1.json"
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m1_review_package.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_m1_review_package.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = "https://well-harness.local/json_schema/multi_agent_m1_review_package_v0_1.schema.json"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_multi_agent_m1_review_package_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m1-review-package"
    assert fixture["package_id"] == "multi-agent-m1-review-package-v0.1"
    assert fixture["milestone"]["id"] == "M1"
    assert fixture["milestone"]["budget"] == 18
    assert fixture["milestone"]["effort_unit"] == "施工队工时"
    assert "天" not in json.dumps(fixture["milestone"], ensure_ascii=False)
    assert fixture["aggregate"] == {
        "approved_repair_slice_count": 2,
        "approved_queue_task_count": 3,
        "converged_queue_tasks": 3,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_long_running_development": True,
    }


def test_multi_agent_m1_review_package_runner_and_checker_converge(
    tmp_path: Path,
) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
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
        timeout=120,
    )

    assert run_result.returncode == 0, run_result.stderr
    run_payload = json.loads(run_result.stdout)
    assert run_payload["status"] == "pass"
    assert run_payload["package_id"] == "multi-agent-m1-review-package-v0.1"
    assert run_payload["milestone"]["budget"] == 18
    assert run_payload["deterministic_gates"] == {
        "approved_repair_slices_artifact": "pass",
        "approved_candidate_task_queue_artifact": "pass",
        "queue_expansion_contract": "pass",
        "construction_readiness": "pass",
        "local_gate_entrypoint": "pass",
    }
    package_path = Path(run_payload["artifact_paths"]["review_package"])
    assert package_path.exists()

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["schema_valid"] is True
    assert check_payload["child_artifacts_valid"] is True
    assert check_payload["boundary_valid"] is True
    assert check_payload["milestone_valid"] is True
    assert check_payload["mismatches"] == []


def test_multi_agent_m1_review_package_checker_reports_boundary_drift(
    tmp_path: Path,
) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
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
        timeout=120,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m1_review_package_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["review_boundaries"]["controller_truth_modified"] = True
    package_path.write_text(json.dumps(package), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["boundary_valid"] is False
    assert "review_boundaries.controller_truth_modified must be false" in payload["mismatches"]


def test_multi_agent_m1_review_package_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-m1-review-package" in makefile
    assert "scripts/run_multi_agent_m1_review_package.py --format json" in makefile

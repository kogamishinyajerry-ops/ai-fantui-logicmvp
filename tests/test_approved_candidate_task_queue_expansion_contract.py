from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "approved_candidate_task_queue_expansion_contract_v0_1.json"
)
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_approved_candidate_task_queue_expansion_contract.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing artifact: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_queue_expansion_contract_schema_declares_append_only_policy() -> None:
    schema = _load_json(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["title"] == "Approved Candidate Task Queue Expansion Contract v0.1"
    assert schema["properties"]["$schema"]["const"] == SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == (
        "ai-fantui-approved-candidate-task-queue-expansion-contract"
    )
    assert schema["x-well-harness-approved-candidate-task-queue-expansion"] == {
        "schema_version": "0.1",
        "scope": "append-only expansion contract for approved candidate task queues",
        "current_fixed_queue_version": "approved-candidate-task-queue-v0.1",
        "truth_effect": "none",
        "controller_truth_modified": False,
    }


def test_queue_expansion_contract_fixture_is_schema_valid_and_boundary_locked() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert fixture["current_queue_contract"] == {
        "queue_id": "approved-candidate-task-queue-v0.1",
        "summary_schema": (
            "https://well-harness.local/json_schema/"
            "approved_candidate_task_queue_summary_v0_1.schema.json"
        ),
        "summary_artifact_name": "approved_candidate_task_queue_summary.json",
        "fixed_item_count": 3,
        "mutable": False,
    }
    assert fixture["expansion_policy"]["append_only"] is True
    assert fixture["expansion_policy"]["next_queue_id"] == "approved-candidate-task-queue-v0.2"
    assert fixture["expansion_policy"]["new_task_requires"] == [
        "schema_update",
        "fixture_update",
        "checker_update",
        "focused_test",
        "make_target",
        "ci_checker_step",
        "child_review_packet_export",
        "readiness_preflight",
        "approved_task_shell",
        "boundary_check",
    ]
    assert "src/well_harness/controller.py" in fixture["forbidden_files"]
    assert "src/well_harness/editable_control_model.py" in fixture["forbidden_files"]


def test_queue_expansion_contract_checker_reports_ready() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
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
    assert payload["contract_schema_valid"] is True
    assert payload["contract_valid"] is True
    assert payload["current_queue_contract_fixed"] is True
    assert payload["append_only_ready"] is True
    assert payload["next_queue_id"] == "approved-candidate-task-queue-v0.2"
    assert payload["mismatches"] == []


def test_queue_expansion_contract_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "verify-approved-candidate-task-queue-expansion-contract" in makefile
    assert "scripts/verify_approved_candidate_task_queue_expansion_contract.py --format json" in makefile

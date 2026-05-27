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
    / "multi_agent_m6_queue_extension_template_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m6_queue_extension_template_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m6_queue_extension_template.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_m6_queue_extension_template.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m6_queue_extension_template_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_m6_queue_extension_template_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m6-queue-extension-template"
    assert fixture["package_id"] == "multi-agent-m6-queue-extension-template-v0.1"
    assert fixture["milestone"] == {
        "id": "M6",
        "name": "队列扩展模板",
        "budget": 32,
        "effort_unit": "施工队工时",
        "claim": "candidate-only approved queue extension template",
    }
    assert fixture["template_summary"] == {
        "readiness_status": "ready_for_append_only_queue_growth",
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "next_queue_id": "approved-candidate-task-queue-v0.2",
        "supported_task_classes": [
            "SafetyRepairTask",
            "EvidenceRepairTask",
            "RequirementRepairTask",
        ],
    }
    assert fixture["append_only_controls"] == {
        "current_queue_id": "approved-candidate-task-queue-v0.1",
        "next_queue_id": "approved-candidate-task-queue-v0.2",
        "preserve_existing_queue_order": True,
        "requires_new_summary_schema": True,
        "requires_fixture_migration": True,
        "requires_checker_update": True,
        "requires_child_review_export": True,
    }
    assert fixture["aggregate"] == {
        "template_count": 1,
        "supported_task_class_count": 3,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_queue_expansion": True,
    }
    assert [item["task_class"] for item in fixture["task_class_matrix"]] == [
        "SafetyRepairTask",
        "EvidenceRepairTask",
        "RequirementRepairTask",
    ]


def test_m6_queue_extension_template_runner_and_checker_converge(tmp_path: Path) -> None:
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
        timeout=60,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "multi-agent-m6-queue-extension-template-v0.1"
    assert payload["deterministic_gates"] == {
        "m5_control_plane_entrypoint": "pass",
        "queue_expansion_contract": "pass",
        "template_schema": "pass",
        "append_only_controls": "pass",
        "task_class_matrix": "pass",
        "operator_template_guide": "pass",
        "local_gate_entrypoint": "pass",
    }
    assert payload["template_summary"]["readiness_status"] == (
        "ready_for_append_only_queue_growth"
    )
    assert payload["aggregate"]["ready_for_queue_expansion"] is True

    package_path = Path(payload["artifact_paths"]["template_package"])
    guide_path = Path(payload["artifact_paths"]["operator_template_guide"])
    assert package_path.exists()
    assert guide_path.exists()
    guide_text = guide_path.read_text(encoding="utf-8")
    assert "M6 Queue Extension Template" in guide_text
    assert "SafetyRepairTask" in guide_text
    assert "RequirementRepairTask" in guide_text

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
    assert check_payload["append_only_controls_valid"] is True
    assert check_payload["task_class_matrix_valid"] is True
    assert check_payload["template_guide_valid"] is True
    assert check_payload["boundary_valid"] is True
    assert check_payload["mismatches"] == []


def test_m6_queue_extension_template_checker_reports_missing_requirement_route(
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
        timeout=60,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m6_queue_extension_template_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["task_class_matrix"] = [
        item
        for item in package["task_class_matrix"]
        if item["task_class"] != "RequirementRepairTask"
    ]
    package["template_summary"]["supported_task_classes"].remove("RequirementRepairTask")
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
    assert payload["task_class_matrix_valid"] is False
    assert "task_class_matrix must include RequirementRepairTask" in payload["mismatches"]


def test_m6_queue_extension_template_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-queue-extension-template" in makefile
    assert "scripts/run_multi_agent_m6_queue_extension_template.py --format json" in makefile
    assert "scripts/verify_multi_agent_m6_queue_extension_template.py --format json" in makefile

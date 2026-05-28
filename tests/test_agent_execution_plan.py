from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/agent_execution_plan_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "agent_execution_plan_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_execution_plan_v0_1.json"
TASK_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_task_contract_v0_1.json"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _execution_plan_module():
    try:
        return importlib.import_module("well_harness.agent_execution_plan")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_execution_plan module: {exc}")


def test_execution_plan_schema_declares_dry_run_only_contract() -> None:
    schema = _load_json(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == "ai-fantui-agent-execution-plan"
    meta = schema["x-well-harness-agent-execution-plan"]
    assert meta["schema_version"] == "0.1"
    assert meta["execution_boundary"] == {
        "dry_run_only": True,
        "execution_allowed": False,
    }
    required = set(schema["required"])
    assert {
        "$schema",
        "kind",
        "planner",
        "dry_run_only",
        "execution_allowed",
        "selected_task",
        "boundary_verdict",
        "planned_steps",
        "file_operations",
        "verification_commands",
    } <= required


def test_execution_plan_fixture_is_schema_valid_and_non_executing() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert fixture["dry_run_only"] is True
    assert fixture["execution_allowed"] is False
    assert fixture["planner"]["agent_name"] == "DeterministicExecutorAgent"
    assert fixture["boundary_verdict"]["status"] == "pass"


def test_execution_plan_validator_rejects_real_execution_authorization() -> None:
    contract = _execution_plan_module()
    fixture = _load_json(FIXTURE_PATH)
    unsafe = copy.deepcopy(fixture)
    unsafe["execution_allowed"] = True

    with pytest.raises(contract.AgentExecutionPlanError, match="dry-run only"):
        contract.validate_execution_plan(unsafe)


def test_build_execution_plan_selects_first_proposed_task_and_preserves_boundaries() -> None:
    contract = _execution_plan_module()
    task_package = _load_json(TASK_FIXTURE_PATH)

    plan = contract.build_execution_plan_from_task_package(task_package)

    contract.validate_execution_plan(plan)
    assert plan["planner"]["status"] == "dry_run_ready"
    assert plan["planner"]["selected_task_id"] == "TASK-CE-CHECK-SAFETY-PRIORITY-001"
    assert plan["selected_task"]["target_agent"] == "LogicIRRepairAgent"
    assert plan["dry_run_only"] is True
    assert plan["execution_allowed"] is False
    assert plan["boundary_verdict"] == {
        "status": "pass",
        "violations": [],
    }
    assert plan["file_operations"] == [
        {
            "operation": "candidate_patch_plan",
            "path": "src/well_harness/agent_output_contract.py",
            "allowed": True,
            "reason": "first allowed implementation file for dry-run planning",
        }
    ]
    assert any("Do not apply patches" in step for step in plan["planned_steps"])


def test_execution_plan_blocks_forbidden_or_out_of_scope_file_targets() -> None:
    contract = _execution_plan_module()
    task_package = _load_json(TASK_FIXTURE_PATH)

    plan = contract.build_execution_plan_from_task_package(
        task_package,
        proposed_files=[
            "src/well_harness/controller.py",
            "src/well_harness/static/requirements_intake/requirements_intake.css",
            "src/well_harness/agent_task_contract.py",
            "README.md",
        ],
    )

    contract.validate_execution_plan(plan)
    assert plan["planner"]["status"] == "blocked"
    assert plan["boundary_verdict"]["status"] == "blocked"
    assert plan["execution_allowed"] is False
    assert plan["file_operations"] == [
        {
            "operation": "candidate_patch_plan",
            "path": "src/well_harness/controller.py",
            "allowed": False,
            "reason": "forbidden by Chief Engineer task boundary",
        },
        {
            "operation": "candidate_patch_plan",
            "path": "src/well_harness/static/requirements_intake/requirements_intake.css",
            "allowed": False,
            "reason": "forbidden by Chief Engineer task boundary",
        },
        {
            "operation": "candidate_patch_plan",
            "path": "src/well_harness/agent_task_contract.py",
            "allowed": True,
            "reason": "allowed by Chief Engineer task boundary",
        },
        {
            "operation": "candidate_patch_plan",
            "path": "README.md",
            "allowed": False,
            "reason": "not listed in Chief Engineer allowed_files",
        },
    ]
    assert plan["boundary_verdict"]["violations"] == [
        "src/well_harness/controller.py is forbidden by task boundary",
        "src/well_harness/static/requirements_intake/requirements_intake.css is forbidden by task boundary",
        "README.md is outside task allowed_files",
    ]


def test_execution_plan_handles_no_available_task_package() -> None:
    contract = _execution_plan_module()
    task_package = _load_json(TASK_FIXTURE_PATH)
    task_package["tasks"] = []
    task_package["chief_engineer"]["status"] = "no_tasks_required"
    task_package["chief_engineer"]["task_count"] = 0

    plan = contract.build_execution_plan_from_task_package(task_package)

    contract.validate_execution_plan(plan)
    assert plan["planner"]["status"] == "no_task_available"
    assert plan["selected_task"] == {}
    assert plan["file_operations"] == []
    assert plan["planned_steps"] == []

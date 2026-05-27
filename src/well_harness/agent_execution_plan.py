"""Dry-run execution planning for Chief Engineer task packages."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from well_harness.agent_task_contract import validate_agent_task_package


AGENT_EXECUTION_PLAN_SCHEMA_ID = (
    "https://well-harness.local/json_schema/agent_execution_plan_v0_1.schema.json"
)
AGENT_EXECUTION_PLAN_SCHEMA_NAME = "agent_execution_plan_v0_1.schema.json"
AGENT_EXECUTION_PLAN_KIND = "ai-fantui-agent-execution-plan"
DEFAULT_SOURCE_TASK_PACKAGE_ID = "CHIEF_ENGINEER_TASK_PACKAGE_v0.1"
REQUIRED_EXECUTION_PLAN_FIELDS = {
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
}
REQUIRED_PLANNER_FIELDS = {
    "agent_name",
    "source_task_package_id",
    "status",
    "selected_task_id",
}
REQUIRED_BOUNDARY_VERDICT_FIELDS = {"status", "violations"}
REQUIRED_FILE_OPERATION_FIELDS = {"operation", "path", "allowed", "reason"}


class AgentExecutionPlanError(ValueError):
    """Raised when a dry-run execution plan violates execution boundaries."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / AGENT_EXECUTION_PLAN_SCHEMA_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(plan: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        if exc.name not in {None, "jsonschema"}:
            raise
        _fallback_schema_validate(plan)
        return

    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(plan)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        if "dry_run_only" in path or "execution_allowed" in path:
            raise AgentExecutionPlanError("execution plan must remain dry-run only") from exc
        raise AgentExecutionPlanError(
            f"agent execution plan schema validation failed{location}: {exc.message}"
        ) from exc


def _missing_fields(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise AgentExecutionPlanError(f"{label} missing required field(s): {', '.join(missing)}")


def _fallback_schema_validate(plan: dict[str, Any]) -> None:
    """Runtime-safe structural checks used when optional jsonschema is absent."""
    if plan.get("$schema") != AGENT_EXECUTION_PLAN_SCHEMA_ID:
        raise AgentExecutionPlanError("agent execution plan $schema is invalid")
    if plan.get("kind") != AGENT_EXECUTION_PLAN_KIND:
        raise AgentExecutionPlanError("agent execution plan kind is invalid")
    _missing_fields(plan, REQUIRED_EXECUTION_PLAN_FIELDS, "agent execution plan")
    if plan.get("dry_run_only") is not True or plan.get("execution_allowed") is not False:
        raise AgentExecutionPlanError("execution plan must remain dry-run only")

    planner = plan.get("planner")
    if not isinstance(planner, dict):
        raise AgentExecutionPlanError("planner must be an object")
    _missing_fields(planner, REQUIRED_PLANNER_FIELDS, "planner")
    if planner.get("agent_name") != "DeterministicExecutorAgent":
        raise AgentExecutionPlanError("planner.agent_name is invalid")

    boundary = plan.get("boundary_verdict")
    if not isinstance(boundary, dict):
        raise AgentExecutionPlanError("boundary_verdict must be an object")
    _missing_fields(boundary, REQUIRED_BOUNDARY_VERDICT_FIELDS, "boundary_verdict")
    if not isinstance(boundary.get("violations"), list):
        raise AgentExecutionPlanError("boundary_verdict.violations must be a list")

    for field_name in ("planned_steps", "file_operations", "verification_commands"):
        if not isinstance(plan.get(field_name), list):
            raise AgentExecutionPlanError(f"{field_name} must be a list")
    for index, operation in enumerate(plan.get("file_operations", [])):
        if not isinstance(operation, dict):
            raise AgentExecutionPlanError(f"file_operations[{index}] must be an object")
        _missing_fields(operation, REQUIRED_FILE_OPERATION_FIELDS, f"file_operations[{index}]")
        if operation.get("operation") != "candidate_patch_plan":
            raise AgentExecutionPlanError(f"file_operations[{index}].operation is invalid")
        if not isinstance(operation.get("allowed"), bool):
            raise AgentExecutionPlanError(f"file_operations[{index}].allowed must be a boolean")


def _source_task_package_id(task_package: dict[str, Any]) -> str:
    chief = task_package.get("chief_engineer")
    if isinstance(chief, dict):
        source_id = chief.get("source_artifact_id")
        if isinstance(source_id, str) and source_id.strip():
            return source_id.strip()
    return DEFAULT_SOURCE_TASK_PACKAGE_ID


def _first_proposed_task(task_package: dict[str, Any]) -> dict[str, Any]:
    tasks = task_package.get("tasks")
    if not isinstance(tasks, list):
        return {}
    for task in tasks:
        if isinstance(task, dict) and task.get("status") == "proposed":
            return task
    return {}


def _default_proposed_files(task: dict[str, Any]) -> list[str]:
    allowed = task.get("allowed_files")
    if isinstance(allowed, list):
        for path in allowed:
            if isinstance(path, str) and path.startswith("src/"):
                return [path]
    return []


def _file_operation(path: str, task: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    allowed_files = {
        item for item in task.get("allowed_files", []) if isinstance(item, str)
    }
    forbidden_files = {
        item for item in task.get("forbidden_files", []) if isinstance(item, str)
    }
    if path in forbidden_files:
        return (
            {
                "operation": "candidate_patch_plan",
                "path": path,
                "allowed": False,
                "reason": "forbidden by Chief Engineer task boundary",
            },
            f"{path} is forbidden by task boundary",
        )
    if path not in allowed_files:
        return (
            {
                "operation": "candidate_patch_plan",
                "path": path,
                "allowed": False,
                "reason": "not listed in Chief Engineer allowed_files",
            },
            f"{path} is outside task allowed_files",
        )
    reason = (
        "first allowed implementation file for dry-run planning"
        if path == next(iter(_default_proposed_files(task)), "")
        else "allowed by Chief Engineer task boundary"
    )
    return (
        {
            "operation": "candidate_patch_plan",
            "path": path,
            "allowed": True,
            "reason": reason,
        },
        None,
    )


def _selected_task_summary(task: dict[str, Any]) -> dict[str, Any]:
    if not task:
        return {}
    return {
        "task_id": task.get("task_id", ""),
        "target_agent": task.get("target_agent", ""),
        "task_type": task.get("task_type", ""),
        "priority": task.get("priority", ""),
    }


def validate_execution_plan(plan: dict[str, Any]) -> None:
    """Validate schema plus hard no-execution boundary."""
    _schema_validate(plan)
    if plan.get("dry_run_only") is not True or plan.get("execution_allowed") is not False:
        raise AgentExecutionPlanError("execution plan must remain dry-run only")


def build_execution_plan_from_task_package(
    task_package: dict[str, Any],
    *,
    proposed_files: list[str] | None = None,
) -> dict[str, Any]:
    """Create a deterministic dry-run plan without applying file changes."""
    validate_agent_task_package(task_package)
    source_package_id = _source_task_package_id(task_package)
    task = _first_proposed_task(task_package)
    if not task:
        plan = {
            "$schema": AGENT_EXECUTION_PLAN_SCHEMA_ID,
            "kind": AGENT_EXECUTION_PLAN_KIND,
            "planner": {
                "agent_name": "DeterministicExecutorAgent",
                "source_task_package_id": source_package_id,
                "status": "no_task_available",
                "selected_task_id": "",
            },
            "dry_run_only": True,
            "execution_allowed": False,
            "selected_task": {},
            "boundary_verdict": {"status": "no_task", "violations": []},
            "planned_steps": [],
            "file_operations": [],
            "verification_commands": [],
        }
        validate_execution_plan(plan)
        return plan

    candidate_files = proposed_files if proposed_files is not None else _default_proposed_files(task)
    file_operations: list[dict[str, Any]] = []
    violations: list[str] = []
    for path in candidate_files:
        if not isinstance(path, str) or not path.strip():
            continue
        operation, violation = _file_operation(path.strip(), task)
        file_operations.append(operation)
        if violation:
            violations.append(violation)

    blocked = bool(violations)
    plan = {
        "$schema": AGENT_EXECUTION_PLAN_SCHEMA_ID,
        "kind": AGENT_EXECUTION_PLAN_KIND,
        "planner": {
            "agent_name": "DeterministicExecutorAgent",
            "source_task_package_id": source_package_id,
            "status": "blocked" if blocked else "dry_run_ready",
            "selected_task_id": str(task.get("task_id", "")),
        },
        "dry_run_only": True,
        "execution_allowed": False,
        "selected_task": _selected_task_summary(task),
        "boundary_verdict": {
            "status": "blocked" if blocked else "pass",
            "violations": violations,
        },
        "planned_steps": [
            "Read selected Chief Engineer task and its findings.",
            "Do not apply patches; produce a dry-run candidate patch plan only.",
            "Run the listed verification commands after any later approved execution.",
        ],
        "file_operations": file_operations,
        "verification_commands": [
            item for item in task.get("verification_commands", []) if isinstance(item, str)
        ],
    }
    validate_execution_plan(plan)
    return plan

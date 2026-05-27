"""Approved-task execution evidence for candidate-only agent work."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from well_harness.agent_execution_plan import build_execution_plan_from_task_package
from well_harness.agent_task_contract import validate_agent_task_package


AGENT_EXECUTION_EVIDENCE_SCHEMA_ID = (
    "https://well-harness.local/json_schema/agent_execution_evidence_v0_1.schema.json"
)
AGENT_EXECUTION_EVIDENCE_SCHEMA_NAME = "agent_execution_evidence_v0_1.schema.json"
AGENT_EXECUTION_EVIDENCE_KIND = "ai-fantui-agent-execution-evidence"
REQUIRED_EXECUTION_EVIDENCE_FIELDS = {
    "$schema",
    "kind",
    "executor",
    "approval",
    "execution_boundary",
    "selected_task",
    "file_operations",
    "deterministic_gates",
    "verification_commands",
    "evidence_package",
}
REQUIRED_EXECUTOR_FIELDS = {
    "agent_name",
    "source_task_package_id",
    "status",
    "selected_task_id",
}
REQUIRED_APPROVAL_FIELDS = {
    "status",
    "approval_id",
    "approved_task_id",
    "approved_by",
    "approved_at",
}
REQUIRED_EXECUTION_BOUNDARY_FIELDS = {
    "restricted_execution",
    "restricted_execution_performed",
    "workspace_writes_performed",
    "controller_truth_modified",
    "ui_layout_modified",
}
REQUIRED_EVIDENCE_PACKAGE_FIELDS = {
    "task_package_hash",
    "execution_plan_hash",
    "evidence_material_hash",
    "machine_readable",
    "human_review_required",
    "verification_summary",
    "notes",
}


class AgentExecutionShellError(ValueError):
    """Raised when approved-task execution evidence violates boundaries."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / AGENT_EXECUTION_EVIDENCE_SCHEMA_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(evidence: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        if exc.name not in {None, "jsonschema"}:
            raise
        _fallback_schema_validate(evidence)
        return

    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(evidence)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise AgentExecutionShellError(
            f"agent execution evidence schema validation failed{location}: {exc.message}"
        ) from exc


def _missing_fields(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise AgentExecutionShellError(f"{label} missing required field(s): {', '.join(missing)}")


def _fallback_schema_validate(evidence: dict[str, Any]) -> None:
    """Runtime-safe structural checks used when optional jsonschema is absent."""
    if evidence.get("$schema") != AGENT_EXECUTION_EVIDENCE_SCHEMA_ID:
        raise AgentExecutionShellError("agent execution evidence $schema is invalid")
    if evidence.get("kind") != AGENT_EXECUTION_EVIDENCE_KIND:
        raise AgentExecutionShellError("agent execution evidence kind is invalid")
    _missing_fields(evidence, REQUIRED_EXECUTION_EVIDENCE_FIELDS, "agent execution evidence")

    executor = evidence.get("executor")
    if not isinstance(executor, dict):
        raise AgentExecutionShellError("executor must be an object")
    _missing_fields(executor, REQUIRED_EXECUTOR_FIELDS, "executor")
    if executor.get("agent_name") != "ApprovedTaskExecutionShell":
        raise AgentExecutionShellError("executor.agent_name is invalid")

    approval = evidence.get("approval")
    if not isinstance(approval, dict):
        raise AgentExecutionShellError("approval must be an object")
    _missing_fields(approval, REQUIRED_APPROVAL_FIELDS, "approval")

    boundary = evidence.get("execution_boundary")
    if not isinstance(boundary, dict):
        raise AgentExecutionShellError("execution_boundary must be an object")
    _missing_fields(boundary, REQUIRED_EXECUTION_BOUNDARY_FIELDS, "execution_boundary")
    for field_name in REQUIRED_EXECUTION_BOUNDARY_FIELDS:
        if not isinstance(boundary.get(field_name), bool):
            raise AgentExecutionShellError(f"execution_boundary.{field_name} must be a boolean")

    for field_name in ("file_operations", "deterministic_gates", "verification_commands"):
        if not isinstance(evidence.get(field_name), list):
            raise AgentExecutionShellError(f"{field_name} must be a list")

    evidence_package = evidence.get("evidence_package")
    if not isinstance(evidence_package, dict):
        raise AgentExecutionShellError("evidence_package must be an object")
    _missing_fields(evidence_package, REQUIRED_EVIDENCE_PACKAGE_FIELDS, "evidence_package")
    if evidence_package.get("machine_readable") is not True:
        raise AgentExecutionShellError("evidence_package.machine_readable must be true")
    if not isinstance(evidence_package.get("human_review_required"), bool):
        raise AgentExecutionShellError("evidence_package.human_review_required must be a boolean")
    if not isinstance(evidence_package.get("notes"), list):
        raise AgentExecutionShellError("evidence_package.notes must be a list")


def _hash_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _source_task_package_id(task_package: dict[str, Any]) -> str:
    chief = task_package.get("chief_engineer")
    if isinstance(chief, dict):
        source_id = chief.get("source_artifact_id")
        if isinstance(source_id, str) and source_id.strip():
            return source_id.strip()
    return "CHIEF_ENGINEER_TASK_PACKAGE_v0.1"


def _approval_record(
    approval: dict[str, Any] | None,
    *,
    selected_task_id: str,
) -> dict[str, str]:
    if not approval:
        return {
            "status": "missing",
            "approval_id": "",
            "approved_task_id": "",
            "approved_by": "",
            "approved_at": "",
        }

    approval_id = str(approval.get("approval_id", "")).strip()
    approved_task_id = str(approval.get("task_id", "")).strip()
    approved_by = str(approval.get("approved_by", "")).strip()
    approved_at = str(approval.get("approved_at", "")).strip()
    if approval.get("approved") is not True:
        status = "rejected"
    elif approved_task_id != selected_task_id:
        status = "task_mismatch"
    else:
        status = "approved"
    return {
        "status": status,
        "approval_id": approval_id,
        "approved_task_id": approved_task_id,
        "approved_by": approved_by,
        "approved_at": approved_at,
    }


def _approval_gate(approval: dict[str, str], selected_task_id: str) -> dict[str, str]:
    if not selected_task_id:
        return {
            "name": "approval_gate",
            "status": "pass",
            "detail": "no selected task requires approval",
        }
    if approval["status"] == "approved":
        return {
            "name": "approval_gate",
            "status": "pass",
            "detail": f"explicit approval {approval['approval_id']} accepted for {selected_task_id}",
        }
    if approval["status"] == "task_mismatch":
        return {
            "name": "approval_gate",
            "status": "block",
            "detail": f"approval targets {approval['approved_task_id']} but selected task is {selected_task_id}",
        }
    if approval["status"] == "rejected":
        return {
            "name": "approval_gate",
            "status": "block",
            "detail": "explicit approval object does not approve restricted execution",
        }
    return {
        "name": "approval_gate",
        "status": "block",
        "detail": "explicit approval object is required before restricted execution",
    }


def _verification_summary(results: list[dict[str, Any]] | None) -> dict[str, int]:
    if not results:
        return {"total": 0, "passed": 0, "failed": 0, "pending": 0}
    passed = 0
    failed = 0
    pending = 0
    for result in results:
        status = str(result.get("status", "")).strip().lower()
        if status == "pass":
            passed += 1
        elif status in {"fail", "block"}:
            failed += 1
        else:
            pending += 1
    return {"total": len(results), "passed": passed, "failed": failed, "pending": pending}


def _post_execution_gate(
    results: list[dict[str, Any]] | None,
    *,
    execution_performed: bool,
) -> dict[str, str]:
    summary = _verification_summary(results)
    if not execution_performed:
        return {
            "name": "post_execution_deterministic_gates",
            "status": "pending",
            "detail": "restricted execution did not run, so post-execution gates are pending",
        }
    if summary["total"] == 0:
        return {
            "name": "post_execution_deterministic_gates",
            "status": "pending",
            "detail": "verification commands are declared but executed results were not supplied",
        }
    status = "pass" if summary["failed"] == 0 and summary["pending"] == 0 else "fail"
    return {
        "name": "post_execution_deterministic_gates",
        "status": status,
        "detail": (
            f"{summary['total']} verification gates supplied, {summary['passed']} passed, "
            f"{summary['failed']} failed, {summary['pending']} pending"
        ),
    }


def _selected_task_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    selected = plan.get("selected_task")
    return dict(selected) if isinstance(selected, dict) else {}


def _file_operations_from_plan(
    plan: dict[str, Any],
    *,
    execution_performed: bool,
    approval: dict[str, str],
    selected_task_id: str,
) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    for item in plan.get("file_operations", []):
        if not isinstance(item, dict):
            continue
        allowed = item.get("allowed") is True
        if execution_performed and allowed:
            status = "executed"
            reason = f"approved by {approval['approved_by']} for task {selected_task_id}"
        elif not allowed:
            status = "blocked"
            reason = str(item.get("reason", "blocked by task boundary")).strip()
        else:
            status = "blocked"
            reason = "restricted execution not approved"
        operations.append(
            {
                "operation": "restricted_candidate_execution",
                "path": str(item.get("path", "")).strip(),
                "allowed": allowed,
                "execution_status": status,
                "reason": reason or "restricted execution boundary decision",
            }
        )
    return operations


def _dry_run_gate(plan: dict[str, Any]) -> dict[str, str]:
    verdict = plan.get("boundary_verdict")
    if isinstance(verdict, dict) and verdict.get("status") == "blocked":
        violations = [
            str(item).strip()
            for item in verdict.get("violations", [])
            if isinstance(item, str) and item.strip()
        ]
        return {
            "name": "dry_run_boundary",
            "status": "block",
            "detail": "; ".join(violations) or "dry-run boundary verification blocked execution",
        }
    return {
        "name": "dry_run_boundary",
        "status": "pass",
        "detail": "dry-run boundary verification passed",
    }


def _file_scope_gate(plan: dict[str, Any]) -> dict[str, str]:
    verdict = plan.get("boundary_verdict")
    if isinstance(verdict, dict) and verdict.get("status") == "blocked":
        return {
            "name": "file_scope_boundary",
            "status": "block",
            "detail": "one or more candidate file operations are outside the task boundary",
        }
    return {
        "name": "file_scope_boundary",
        "status": "pass",
        "detail": "all candidate file operations are inside the approved task boundary",
    }


def _controller_truth_gate(file_operations: list[dict[str, Any]]) -> dict[str, str]:
    executed_paths = {
        str(item.get("path", ""))
        for item in file_operations
        if item.get("execution_status") == "executed"
    }
    unsafe_paths = [
        path
        for path in sorted(executed_paths)
        if path == "src/well_harness/controller.py"
        or path == "src/well_harness/editable_control_model.py"
        or path.startswith("src/well_harness/static/requirements_intake/")
    ]
    if unsafe_paths:
        return {
            "name": "controller_truth_boundary",
            "status": "block",
            "detail": "; ".join(unsafe_paths),
        }
    return {
        "name": "controller_truth_boundary",
        "status": "pass",
        "detail": "no controller truth or UI layout path was executed",
    }


def _executor_status(
    plan: dict[str, Any],
    approval: dict[str, str],
) -> str:
    selected_task_id = str(plan.get("planner", {}).get("selected_task_id", ""))
    if not selected_task_id:
        return "no_task_available"
    if plan.get("planner", {}).get("status") == "blocked":
        return "blocked_boundary_violation"
    if approval["status"] == "task_mismatch":
        return "blocked_task_mismatch"
    if approval["status"] != "approved":
        return "blocked_missing_approval"
    return "executed_limited"


def validate_execution_evidence_package(evidence: dict[str, Any]) -> None:
    """Validate schema plus hard approved-task execution boundaries."""
    _schema_validate(evidence)
    status = evidence.get("executor", {}).get("status")
    approval_status = evidence.get("approval", {}).get("status")
    boundary = evidence.get("execution_boundary", {})
    if boundary.get("workspace_writes_performed") is not False:
        raise AgentExecutionShellError("approved task execution shell must not report workspace writes")
    if boundary.get("controller_truth_modified") is not False:
        raise AgentExecutionShellError("approved task execution shell may not modify controller truth")
    if boundary.get("ui_layout_modified") is not False:
        raise AgentExecutionShellError("approved task execution shell may not modify UI layout")
    if status == "executed_limited":
        if approval_status != "approved":
            raise AgentExecutionShellError("executed package must reference an approved task")
        if boundary.get("restricted_execution_performed") is not True:
            raise AgentExecutionShellError("executed package must record restricted execution")
        for operation in evidence.get("file_operations", []):
            if operation.get("allowed") is not True or operation.get("execution_status") != "executed":
                raise AgentExecutionShellError("executed package contains a non-executed file operation")
    else:
        if boundary.get("restricted_execution_performed") is True:
            raise AgentExecutionShellError("blocked package may not record restricted execution")
    for operation in evidence.get("file_operations", []):
        path = str(operation.get("path", ""))
        if operation.get("execution_status") == "executed" and (
            path == "src/well_harness/controller.py"
            or path == "src/well_harness/editable_control_model.py"
            or path.startswith("src/well_harness/static/requirements_intake/")
        ):
            raise AgentExecutionShellError("approved task execution may not touch controller truth or UI layout")


def build_execution_evidence_package(
    task_package: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
    proposed_files: list[str] | None = None,
    deterministic_gate_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a bounded evidence package for approved task execution.

    The shell deliberately records the approved restricted execution envelope and
    deterministic gate results without applying filesystem writes itself.
    """
    validate_agent_task_package(task_package)
    plan = build_execution_plan_from_task_package(
        task_package,
        proposed_files=proposed_files,
    )
    planner = plan.get("planner", {})
    selected_task_id = str(planner.get("selected_task_id", ""))
    approval_record = _approval_record(approval, selected_task_id=selected_task_id)
    status = _executor_status(plan, approval_record)
    execution_performed = status == "executed_limited"
    file_operations = _file_operations_from_plan(
        plan,
        execution_performed=execution_performed,
        approval=approval_record,
        selected_task_id=selected_task_id,
    )
    deterministic_gates = [
        _dry_run_gate(plan),
        _approval_gate(approval_record, selected_task_id),
        _file_scope_gate(plan),
        _controller_truth_gate(file_operations),
        _post_execution_gate(
            deterministic_gate_results,
            execution_performed=execution_performed,
        ),
    ]
    verification_summary = _verification_summary(deterministic_gate_results)
    evidence_material = {
        "executor_status": status,
        "approval": approval_record,
        "file_operations": file_operations,
        "deterministic_gates": deterministic_gates,
        "verification_summary": verification_summary,
    }
    evidence = {
        "$schema": AGENT_EXECUTION_EVIDENCE_SCHEMA_ID,
        "kind": AGENT_EXECUTION_EVIDENCE_KIND,
        "executor": {
            "agent_name": "ApprovedTaskExecutionShell",
            "source_task_package_id": _source_task_package_id(task_package),
            "status": status,
            "selected_task_id": selected_task_id,
        },
        "approval": approval_record,
        "execution_boundary": {
            "restricted_execution": bool(selected_task_id),
            "restricted_execution_performed": execution_performed,
            "workspace_writes_performed": False,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "selected_task": _selected_task_from_plan(plan),
        "file_operations": file_operations,
        "deterministic_gates": deterministic_gates,
        "verification_commands": [
            item for item in plan.get("verification_commands", []) if isinstance(item, str)
        ],
        "evidence_package": {
            "task_package_hash": _hash_json(task_package),
            "execution_plan_hash": _hash_json(plan),
            "evidence_material_hash": _hash_json(evidence_material),
            "machine_readable": True,
            "human_review_required": status != "no_task_available",
            "verification_summary": verification_summary,
            "notes": [
                "Restricted execution is candidate-contract evidence only.",
                "Controller truth and requirements-intake UI layout remain outside scope.",
            ],
        },
    }
    validate_execution_evidence_package(evidence)
    return evidence

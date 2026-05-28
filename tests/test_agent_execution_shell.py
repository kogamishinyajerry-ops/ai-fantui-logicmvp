from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/agent_execution_evidence_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "agent_execution_evidence_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_execution_evidence_v0_1.json"
TASK_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_task_contract_v0_1.json"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _execution_shell_module():
    try:
        return importlib.import_module("well_harness.agent_execution_shell")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_execution_shell module: {exc}")


def _approval(task_id: str) -> dict:
    return {
        "approval_id": "APPROVAL-HUMAN-001",
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-20T00:00:00Z",
    }


def _gate_results() -> list[dict]:
    return [
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_output_contract.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_task_contract.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_execution_plan.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_execution_shell.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_repair_loop.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_review_packet.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_requirements_intake_webui.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {
            "name": "PYTHONPATH=src:. python3 -m pytest -q tests/test_editable_control_model.py",
            "status": "pass",
            "detail": "exit 0",
        },
        {"name": "git diff --check", "status": "pass", "detail": "exit 0"},
    ]


def test_execution_evidence_schema_declares_approved_task_shell_contract() -> None:
    schema = _load_json(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == "ai-fantui-agent-execution-evidence"
    meta = schema["x-well-harness-agent-execution-evidence"]
    assert meta["schema_version"] == "0.1"
    assert meta["approval_required_before_restricted_execution"] is True
    required = set(schema["required"])
    assert {
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
    } <= required


def test_execution_evidence_fixture_is_schema_valid_and_candidate_bounded() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert fixture["executor"]["agent_name"] == "ApprovedTaskExecutionShell"
    assert fixture["executor"]["status"] == "executed_limited"
    assert fixture["approval"]["status"] == "approved"
    assert fixture["execution_boundary"] == {
        "restricted_execution": True,
        "restricted_execution_performed": True,
        "workspace_writes_performed": False,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert all(operation["allowed"] for operation in fixture["file_operations"])
    assert "src/well_harness/controller.py" not in {
        operation["path"] for operation in fixture["file_operations"]
    }


def test_execution_shell_blocks_unapproved_task_before_restricted_execution() -> None:
    shell = _execution_shell_module()
    task_package = _load_json(TASK_FIXTURE_PATH)

    evidence = shell.build_execution_evidence_package(task_package)

    shell.validate_execution_evidence_package(evidence)
    assert evidence["executor"]["status"] == "blocked_missing_approval"
    assert evidence["approval"]["status"] == "missing"
    assert evidence["execution_boundary"]["restricted_execution_performed"] is False
    assert evidence["execution_boundary"]["workspace_writes_performed"] is False
    assert evidence["deterministic_gates"][1] == {
        "name": "approval_gate",
        "status": "block",
        "detail": "explicit approval object is required before restricted execution",
    }
    assert all(
        operation["execution_status"] == "blocked" for operation in evidence["file_operations"]
    )


def test_execution_shell_executes_only_explicitly_approved_selected_task() -> None:
    shell = _execution_shell_module()
    task_package = _load_json(TASK_FIXTURE_PATH)
    task_id = task_package["tasks"][0]["task_id"]

    evidence = shell.build_execution_evidence_package(
        task_package,
        approval=_approval(task_id),
        proposed_files=["src/well_harness/agent_output_contract.py"],
        deterministic_gate_results=_gate_results(),
    )

    shell.validate_execution_evidence_package(evidence)
    assert evidence["executor"]["status"] == "executed_limited"
    assert evidence["approval"] == {
        "status": "approved",
        "approval_id": "APPROVAL-HUMAN-001",
        "approved_task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-20T00:00:00Z",
    }
    assert evidence["execution_boundary"]["restricted_execution_performed"] is True
    assert evidence["execution_boundary"]["workspace_writes_performed"] is False
    assert evidence["file_operations"] == [
        {
            "operation": "restricted_candidate_execution",
            "path": "src/well_harness/agent_output_contract.py",
            "allowed": True,
            "execution_status": "executed",
            "reason": "approved by HumanReviewAgent for task TASK-CE-CHECK-SAFETY-PRIORITY-001",
        }
    ]
    assert [gate["name"] for gate in evidence["deterministic_gates"]] == [
        "dry_run_boundary",
        "approval_gate",
        "file_scope_boundary",
        "controller_truth_boundary",
        "post_execution_deterministic_gates",
    ]
    assert evidence["evidence_package"]["verification_summary"] == {
        "total": 9,
        "passed": 9,
        "failed": 0,
        "pending": 0,
    }


def test_execution_shell_blocks_controller_truth_even_with_approval() -> None:
    shell = _execution_shell_module()
    task_package = _load_json(TASK_FIXTURE_PATH)
    task_id = task_package["tasks"][0]["task_id"]

    evidence = shell.build_execution_evidence_package(
        task_package,
        approval=_approval(task_id),
        proposed_files=["src/well_harness/controller.py"],
        deterministic_gate_results=_gate_results(),
    )

    shell.validate_execution_evidence_package(evidence)
    assert evidence["executor"]["status"] == "blocked_boundary_violation"
    assert evidence["approval"]["status"] == "approved"
    assert evidence["execution_boundary"]["restricted_execution_performed"] is False
    assert evidence["execution_boundary"]["controller_truth_modified"] is False
    assert evidence["file_operations"][0] == {
        "operation": "restricted_candidate_execution",
        "path": "src/well_harness/controller.py",
        "allowed": False,
        "execution_status": "blocked",
        "reason": "forbidden by Chief Engineer task boundary",
    }
    assert any(
        gate["name"] == "dry_run_boundary" and gate["status"] == "block"
        for gate in evidence["deterministic_gates"]
    )


def test_execution_evidence_validator_rejects_executed_package_without_approval() -> None:
    shell = _execution_shell_module()
    fixture = _load_json(FIXTURE_PATH)
    unsafe = copy.deepcopy(fixture)
    unsafe["approval"]["status"] = "missing"

    with pytest.raises(shell.AgentExecutionShellError, match="approved task"):
        shell.validate_execution_evidence_package(unsafe)

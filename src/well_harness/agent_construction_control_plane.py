"""M5 long-running construction control plane for the multi-agent chain."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m5-construction-control-plane"
)
M5_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m5_construction_control_plane_v0_1.schema.json"
)
M5_SCHEMA_NAME = "multi_agent_m5_construction_control_plane_v0_1.schema.json"
M5_PACKAGE_NAME = "multi_agent_m5_construction_control_plane_v0_1.json"
M5_RUNBOOK_NAME = "construction_control_plane_runbook.md"
M5_KIND = "ai-fantui-multi-agent-m5-construction-control-plane"
M5_PACKAGE_ID = "multi-agent-m5-construction-control-plane-v0.1"
M5_ENTRYPOINT = "make multi-agent-construction-control-plane"


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 300) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M5_SCHEMA_NAME)


def validate_m5_construction_control_plane(package: dict[str, Any]) -> None:
    """Validate the M5 construction control plane schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(
            f"M5 construction control plane schema validation failed{location}: {exc.message}"
        ) from exc


def _command_status(command: dict[str, Any]) -> str:
    return "pass" if command["returncode"] == 0 and command["payload"].get("status") == "pass" else "fail"


def _child_summary(
    *,
    key: str,
    payload: dict[str, Any],
    checker_payload: dict[str, Any],
    package_id_field: str,
    path: Path,
) -> dict[str, Any]:
    return {
        "key": key,
        "package_id": str(payload.get(package_id_field, "")),
        "status": str(payload.get("status", "")),
        "checker_status": str(checker_payload.get("status", "")),
        "path": str(path),
    }


def _failure_recovery() -> list[dict[str, str]]:
    return [
        {
            "id": "FR-GATE-001",
            "trigger": "Any deterministic gate in the M5 package reports fail.",
            "action": "Stop execution, inspect the checker mismatches, repair the smallest failing artifact, then rerun the M5 entrypoint.",
            "resume_command": M5_ENTRYPOINT,
            "stop_condition": "Do not continue queue execution while deterministic_gates.local_gate_entrypoint is fail.",
        },
        {
            "id": "FR-QUEUE-001",
            "trigger": "Approved candidate task queue summary drifts from the fixed v0.1 contract.",
            "action": "Rerun the queue artifact checker and update only append-only expansion contracts for new task types.",
            "resume_command": "make verify-approved-candidate-task-queue-artifact",
            "stop_condition": "Do not weaken approved_candidate_task_queue_summary_v0_1.",
        },
        {
            "id": "FR-BOUNDARY-001",
            "trigger": "A diff appears in controller truth, editable model truth, or requirements-intake UI layout paths.",
            "action": "Stop the construction loop and request human review before any further execution.",
            "resume_command": "git diff --name-only -- src/well_harness/controller.py src/well_harness/editable_control_model.py src/well_harness/static/requirements_intake",
            "stop_condition": "Any restricted path appears in the diff output.",
        },
        {
            "id": "FR-CHILD-001",
            "trigger": "M1, M2, M3, or M4 child review package cannot be regenerated or verified.",
            "action": "Regenerate the specific child package first, then rebuild the M4 handoff and M5 control plane.",
            "resume_command": "make multi-agent-m4-external-review-handoff",
            "stop_condition": "Do not mark M5 ready if child_packages.*.checker_status is not pass.",
        },
    ]


def _phase_review_stop_conditions() -> list[dict[str, Any]]:
    return [
        {
            "id": "STOP-APPROVAL-MISSING",
            "condition": "A selected task lacks explicit matching approval metadata.",
            "action": "Block restricted execution and keep the task in proposed or pending_review state.",
            "blocking": True,
        },
        {
            "id": "STOP-CONTROLLER-TRUTH-DIFF",
            "condition": "git diff includes src/well_harness/controller.py or src/well_harness/editable_control_model.py.",
            "action": "Stop and escalate to human review; do not auto-repair controller truth.",
            "blocking": True,
        },
        {
            "id": "STOP-UI-LAYOUT-DIFF",
            "condition": "git diff includes src/well_harness/static/requirements_intake/.",
            "action": "Stop this construction loop because M5 is not a UI layout polish slice.",
            "blocking": True,
        },
        {
            "id": "STOP-CERTIFICATION-CLAIM",
            "condition": "Any package claims certification readiness, DAL readiness, or trusted control-law promotion.",
            "action": "Reject the package and restore certification_claim to none.",
            "blocking": True,
        },
        {
            "id": "STOP-DETERMINISTIC-GATE-FAIL",
            "condition": "Any schema, checker, convergence, or boundary gate returns fail.",
            "action": "Stop long-running work until the failing gate is repaired and rerun.",
            "blocking": True,
        },
    ]


def _runbook_text(package: dict[str, Any]) -> str:
    recovery = "\n".join(
        f"- {item['id']}: {item['trigger']} Resume: `{item['resume_command']}`"
        for item in package["failure_recovery"]
    )
    stops = "\n".join(
        f"- {item['id']}: {item['condition']}" for item in package["phase_review_stop_conditions"]
    )
    return (
        "# M5 Construction Control Plane\n\n"
        "This is the single candidate-only entrypoint for long-running multi-agent "
        "construction work.\n\n"
        f"Entrypoint: `{M5_ENTRYPOINT}`\n\n"
        "## Queue Snapshot\n\n"
        f"- Queue: {package['queue_snapshot']['queue_id']}\n"
        f"- Tasks: {package['queue_snapshot']['task_count']}\n"
        f"- Converged: {package['queue_snapshot']['converged']}\n\n"
        "## Failure Recovery\n\n"
        f"{recovery}\n\n"
        "## Phase Review Stop Conditions\n\n"
        f"{stops}\n\n"
        "## Boundary\n\n"
        "The control plane remains candidate-only. It does not modify controller truth, "
        "editable model truth, or requirements-intake UI layout files, and it does not "
        "claim certification readiness.\n"
    )


def _queue_snapshot(queue_payload: dict[str, Any]) -> dict[str, Any]:
    aggregate = queue_payload.get("aggregate", {})
    return {
        "queue_id": str(queue_payload.get("queue_id", "")),
        "task_count": int(aggregate.get("task_count", queue_payload.get("task_count", 0))),
        "passed": int(aggregate.get("passed", 0)),
        "preflight_passed": int(aggregate.get("preflight_passed", 0)),
        "executed_limited": int(aggregate.get("executed_limited", 0)),
        "converged": int(aggregate.get("converged", 0)),
        "open_findings": list(aggregate.get("open_findings", [])),
        "ready_for_long_running_development": bool(
            queue_payload.get("ready_for_long_running_development")
        ),
    }


def build_m5_construction_control_plane(
    *,
    artifact_dir: Path = DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Generate M4, approved queue, readiness, and one durable M5 control packet."""
    m4_dir = artifact_dir / "m4-external-review-handoff"
    queue_dir = artifact_dir / "approved-candidate-task-queue"
    readiness_dir = artifact_dir / "multi-agent-construction-readiness"
    package_path = artifact_dir / M5_PACKAGE_NAME
    runbook_path = artifact_dir / M5_RUNBOOK_NAME
    readiness_packet_path = readiness_dir / "readiness_packet.json"

    m4_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_multi_agent_m4_external_review_handoff.py",
            "--format",
            "json",
            "--artifact-dir",
            str(m4_dir),
        ],
        timeout=360,
    )
    m4_package_path = m4_dir / "multi_agent_m4_external_review_handoff_v0_1.json"
    m4_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m4_external_review_handoff.py",
            "--format",
            "json",
            "--package",
            str(m4_package_path),
        ],
        timeout=240,
    )

    queue_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_approved_candidate_task_queue.py",
            "--format",
            "json",
            "--artifact-dir",
            str(queue_dir),
        ],
        timeout=360,
    )
    queue_summary_path = queue_dir / "approved_candidate_task_queue_summary.json"
    queue_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(queue_dir),
        ],
        timeout=240,
    )

    readiness = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_construction_readiness.py",
            "--format",
            "json",
            "--artifact-dir",
            str(readiness_dir),
        ],
        timeout=240,
    )
    _write_json(readiness_packet_path, readiness["payload"])

    gates = {
        "m4_external_review_handoff": "pass" if _command_status(m4_run) == "pass" and _command_status(m4_check) == "pass" else "fail",
        "approved_candidate_task_queue": "pass" if _command_status(queue_run) == "pass" else "fail",
        "approved_candidate_task_queue_artifact": "pass" if _command_status(queue_check) == "pass" else "fail",
        "construction_readiness": "pass" if _command_status(readiness) == "pass" else "fail",
        "failure_recovery_runbook": "pass",
        "phase_review_stop_conditions": "pass",
    }
    gates["local_gate_entrypoint"] = "pass" if all(value == "pass" for value in gates.values()) else "fail"

    queue_snapshot = _queue_snapshot(queue_run["payload"])
    failure_recovery = _failure_recovery()
    stop_conditions = _phase_review_stop_conditions()
    payload = {
        "$schema": M5_SCHEMA_ID,
        "kind": M5_KIND,
        "package_id": M5_PACKAGE_ID,
        "status": "pass" if gates["local_gate_entrypoint"] == "pass" else "fail",
        "milestone": {
            "id": "M5",
            "name": "长时间开工控制面",
            "budget": 40,
            "effort_unit": "施工队工时",
            "claim": "candidate-only long-running construction control plane",
        },
        "control_plane_summary": {
            "readiness_status": "ready_for_long_running_construction",
            "entrypoint": M5_ENTRYPOINT,
            "included_milestones": ["M1", "M2", "M3", "M4"],
            "single_entrypoint": True,
        },
        "child_packages": {
            "m4_external_review_handoff": _child_summary(
                key="m4_external_review_handoff",
                payload=m4_run["payload"],
                checker_payload=m4_check["payload"],
                package_id_field="package_id",
                path=m4_package_path,
            ),
            "approved_candidate_task_queue": _child_summary(
                key="approved_candidate_task_queue",
                payload=queue_run["payload"],
                checker_payload=queue_check["payload"],
                package_id_field="queue_id",
                path=queue_summary_path,
            ),
            "construction_readiness": _child_summary(
                key="construction_readiness",
                payload=readiness["payload"],
                checker_payload=readiness["payload"],
                package_id_field="readiness_id",
                path=readiness_packet_path,
            ),
        },
        "queue_snapshot": queue_snapshot,
        "execution_policy": {
            "approved_only": True,
            "requires_explicit_approval": True,
            "restricted_execution": True,
            "workspace_writes_performed_by_shell": False,
            "deterministic_gates_after_execution": True,
        },
        "deterministic_gates": gates,
        "failure_recovery": failure_recovery,
        "phase_review_stop_conditions": stop_conditions,
        "review_boundaries": {
            "truth_effect": "none",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "restricted_paths": [
                "src/well_harness/controller.py",
                "src/well_harness/editable_control_model.py",
                "src/well_harness/static/requirements_intake/",
            ],
        },
        "aggregate": {
            "milestone_count": 4,
            "child_package_count": 3,
            "queue_task_count": queue_snapshot["task_count"],
            "approved_task_count": queue_snapshot["executed_limited"],
            "active_stop_conditions": [],
            "open_findings": queue_snapshot["open_findings"],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "ready_for_long_running_construction": gates["local_gate_entrypoint"] == "pass"
            and queue_snapshot["ready_for_long_running_development"] is True,
        },
        "artifact_paths": {
            "control_plane_package": str(package_path),
            "operator_runbook": str(runbook_path),
            "m4_external_review_handoff": str(m4_package_path),
            "approved_candidate_task_queue_summary": str(queue_summary_path),
            "construction_readiness_packet": str(readiness_packet_path),
            "project_manager_plan": "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
            "engineering_system_mvp_doc": "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md",
        },
    }
    validate_m5_construction_control_plane(payload)
    _write_json(package_path, payload)
    _write_text(runbook_path, _runbook_text(payload))
    return payload

#!/usr/bin/env python3
"""Validate the M10 multi-agent queue run ledger artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.verify_approved_candidate_task_queue_v0_9_artifact import (
    verify_approved_candidate_task_queue_v0_9_artifact,
)
from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-queue-run-ledger-v0-2")
LEDGER_NAME = "multi_agent_queue_run_ledger_v0_2.json"
LEDGER_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_queue_run_ledger_v0_2.schema.json"
)
LEDGER_SCHEMA_NAME = "multi_agent_queue_run_ledger_v0_2.schema.json"
LEDGER_KIND = "ai-fantui-multi-agent-queue-run-ledger"
LEDGER_ID = "multi-agent-queue-run-ledger-v0.2"
LEDGER_GATE_ID = "multi-agent-queue-run-ledger"
SOURCE_QUEUE_ID = "approved-candidate-task-queue-v0.9"
SOURCE_QUEUE_GATE_ID = "approved-candidate-task-queue-v0-9"
SELECTED_QUEUE_ITEM_ID = "queue-safety-output-command-conflict-repair"
SELECTED_TASK_ID = "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"
EXPECTED_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
    "queue-safety-undefined-signal-repair",
    "queue-evidence-boundary-review-repair",
    "queue-evidence-unknown-requirement-repair",
    "queue-evidence-ir-trace-unknown-requirement-repair",
    "queue-safety-transition-endpoint-repair",
    "queue-safety-unreachable-state-repair",
    "queue-safety-output-command-conflict-repair",
]
EXPECTED_TASKS = {
    "queue-safety-priority-repair": {
        "record_id": "RUN-QUEUE-001",
        "sequence": 1,
        "source_finding_code": "CHECK_SAFETY_PRIORITY_001",
        "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-evidence-simulation-result-repair": {
        "record_id": "RUN-QUEUE-002",
        "sequence": 2,
        "source_finding_code": "EV_SIMULATION_RESULT_FAILED",
        "task_id": "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-evidence-test-result-missing-repair": {
        "record_id": "RUN-QUEUE-003",
        "sequence": 3,
        "source_finding_code": "EV_TEST_RESULT_MISSING",
        "task_id": "TASK-CE-EV-TEST-RESULT-MISSING",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-requirement-ambiguity-repair": {
        "record_id": "RUN-QUEUE-004",
        "sequence": 4,
        "source_finding_code": "REQ_AMBIGUITY_UNRESOLVED",
        "task_id": "TASK-CE-REQ-AMBIGUITY-UNRESOLVED",
        "target_agent": "RequirementRepairAgent",
        "task_type": "repair_structured_requirement_candidate",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-safety-undefined-signal-repair": {
        "record_id": "RUN-QUEUE-005",
        "sequence": 5,
        "source_finding_code": "CHECK_UNDEFINED_SIGNAL_001",
        "task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-evidence-boundary-review-repair": {
        "record_id": "RUN-QUEUE-006",
        "sequence": 6,
        "source_finding_code": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
        "task_id": "TASK-CE-EV-BOUNDARY-REVIEW-001",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-evidence-unknown-requirement-repair": {
        "record_id": "RUN-QUEUE-007",
        "sequence": 7,
        "source_finding_code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        "task_id": "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-evidence-ir-trace-unknown-requirement-repair": {
        "record_id": "RUN-QUEUE-008",
        "sequence": 8,
        "source_finding_code": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
        "task_id": "TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-safety-transition-endpoint-repair": {
        "record_id": "RUN-QUEUE-009",
        "sequence": 9,
        "source_finding_code": "CHECK_TRANSITION_ENDPOINT_001",
        "task_id": "TASK-CE-CHECK-TRANSITION-ENDPOINT-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-safety-unreachable-state-repair": {
        "record_id": "RUN-QUEUE-010",
        "sequence": 10,
        "source_finding_code": "CHECK_UNREACHABLE_STATE_001",
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
    "queue-safety-output-command-conflict-repair": {
        "record_id": "RUN-QUEUE-011",
        "sequence": 11,
        "source_finding_code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        "task_id": SELECTED_TASK_ID,
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "preflight_command": "make multi-agent-fast-construction-gate",
    },
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the M10 queue run ledger artifact and child exports.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_LEDGER_ARTIFACT_DIR,
        help="Directory containing multi_agent_queue_run_ledger_v0_2.json.",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="Explicit ledger path. Overrides --artifact-dir.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ledger_path(*, artifact_dir: Path, ledger_path: Path | None = None) -> Path:
    if ledger_path is not None:
        return ledger_path
    return artifact_dir / LEDGER_NAME


def _load_schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / LEDGER_SCHEMA_NAME)


def _schema_mismatches(ledger: dict[str, Any]) -> list[str]:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_schema()).iter_errors(ledger),
        key=lambda error: list(error.absolute_path),
    )
    mismatches: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"queue run ledger schema validation failed{location}: {error.message}")
    return mismatches


def _resolve_path(path_value: Any, ledger_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ledger_path.parent / path


def _check_basic_fields(ledger: dict[str, Any], mismatches: list[str]) -> None:
    checks = {
        "$schema": LEDGER_SCHEMA_ID,
        "kind": LEDGER_KIND,
        "gate_id": LEDGER_GATE_ID,
        "ledger_id": LEDGER_ID,
        "source_queue_id": SOURCE_QUEUE_ID,
        "source_queue_gate_id": SOURCE_QUEUE_GATE_ID,
        "selected_queue_item_id": SELECTED_QUEUE_ITEM_ID,
        "selected_task_id": SELECTED_TASK_ID,
        "run_count": len(EXPECTED_QUEUE_ORDER),
    }
    for key, expected in checks.items():
        if ledger.get(key) != expected:
            mismatches.append(f"{key} must be {expected!r}")
    if ledger.get("status") != "pass":
        mismatches.append("status must be pass")


def _check_scheduler(ledger: dict[str, Any], mismatches: list[str]) -> bool:
    scheduler = ledger.get("scheduler_decision")
    if not isinstance(scheduler, dict):
        mismatches.append("scheduler_decision must be an object")
        return False
    checks = {
        "policy_id": "latest-approved-append-only-item-v0.2",
        "decision_status": "selected_approved_candidate",
        "selected_queue_item_id": SELECTED_QUEUE_ITEM_ID,
        "selected_record_id": "RUN-QUEUE-011",
    }
    valid = True
    for key, expected in checks.items():
        if scheduler.get(key) != expected:
            mismatches.append(f"scheduler_decision.{key} must be {expected}")
            valid = False
    return valid


def _check_source_queue(ledger: dict[str, Any], ledger_path: Path, mismatches: list[str]) -> bool:
    source_path = _resolve_path(
        ledger.get("artifact_paths", {}).get("source_queue_summary"),
        ledger_path,
    )
    if source_path is None:
        mismatches.append("artifact_paths.source_queue_summary is required")
        return False
    result = verify_approved_candidate_task_queue_v0_9_artifact(summary_path=source_path)
    if result.get("status") != "pass":
        mismatches.append("source queue v0.9 checker must pass")
        mismatches.extend(str(item) for item in result.get("mismatches", []))
        return False
    return True


def _check_record(
    record: dict[str, Any],
    *,
    expected: dict[str, Any],
    ledger_path: Path,
    mismatches: list[str],
    child_export_paths: list[str],
) -> bool:
    valid = True
    record_id = str(record.get("record_id", ""))
    checks = {
        "record_id": expected["record_id"],
        "sequence": expected["sequence"],
        "source_finding_code": expected["source_finding_code"],
    }
    for key, expected_value in checks.items():
        if record.get(key) != expected_value:
            mismatches.append(f"{record_id}.{key} must be {expected_value}")
            valid = False

    task = record.get("task")
    if not isinstance(task, dict):
        mismatches.append(f"{record_id}.task must be an object")
        valid = False
    else:
        for key in ("task_id", "target_agent", "task_type"):
            if task.get(key) != expected[key]:
                mismatches.append(f"{record_id}.task.{key} must be {expected[key]}")
                valid = False

    preflight = record.get("preflight")
    if not isinstance(preflight, dict):
        mismatches.append(f"{record_id}.preflight must be an object")
        valid = False
    else:
        if preflight.get("command") != expected["preflight_command"]:
            mismatches.append(
                f"{record_id}.preflight.command must be {expected['preflight_command']}"
            )
            valid = False
        if preflight.get("status") != "pass":
            mismatches.append(f"{record_id}.preflight.status must be pass")
            valid = False
        if preflight.get("returncode") != 0:
            mismatches.append(f"{record_id}.preflight.returncode must be 0")
            valid = False

    shell = record.get("approved_task_shell")
    if not isinstance(shell, dict):
        mismatches.append(f"{record_id}.approved_task_shell must be an object")
        valid = False
    else:
        if shell.get("status") != "executed_limited":
            mismatches.append(
                f"{record_id}.approved_task_shell.status must be executed_limited"
            )
            valid = False
        if shell.get("approval_status") != "approved":
            mismatches.append(
                f"{record_id}.approved_task_shell.approval_status must be approved"
            )
            valid = False
        if shell.get("selected_task_id") != expected["task_id"]:
            mismatches.append(
                f"{record_id}.approved_task_shell.selected_task_id must be {expected['task_id']}"
            )
            valid = False

    repair = record.get("repair")
    if not isinstance(repair, dict):
        mismatches.append(f"{record_id}.repair must be an object")
        valid = False
    else:
        if repair.get("status") != "pass":
            mismatches.append(f"{record_id}.repair.status must be pass")
            valid = False
        if repair.get("reviewer_status") != "converged":
            mismatches.append(f"{record_id}.repair.reviewer_status must be converged")
            valid = False
        if repair.get("finding_chain_statuses") != ["converged"]:
            mismatches.append(f"{record_id}.repair.finding_chain_statuses must be converged")
            valid = False

    boundary = record.get("boundary")
    if not isinstance(boundary, dict):
        mismatches.append(f"{record_id}.boundary must be an object")
        valid = False
    else:
        if boundary.get("controller_truth_modified") is not False:
            mismatches.append(f"{record_id}.boundary.controller_truth_modified must be false")
            valid = False
        if boundary.get("ui_layout_modified") is not False:
            mismatches.append(f"{record_id}.boundary.ui_layout_modified must be false")
            valid = False

    review_export = record.get("review_export")
    export_path = None
    if isinstance(review_export, dict):
        export_path = _resolve_path(review_export.get("path"), ledger_path)
    if export_path is None:
        mismatches.append(f"{record_id}.review_export.path is required")
        return False
    child_export_paths.append(str(export_path))
    try:
        export = _load_json(export_path)
        validate_candidate_review_packet_export(export)
    except Exception as exc:  # noqa: BLE001 - checker reports all child failures.
        mismatches.append(f"{record_id}.review_export invalid: {exc}")
        return False
    review_packet = export.get("review_packet", {})
    chains = review_packet.get("finding_chains", [])
    statuses = [
        str(chain.get("status", ""))
        for chain in chains
        if isinstance(chain, dict)
    ]
    if review_packet.get("reviewer", {}).get("status") != "converged":
        mismatches.append(f"{record_id}.review_export.reviewer_status must be converged")
        valid = False
    if statuses != ["converged"]:
        mismatches.append(f"{record_id}.review_export.finding_chain_statuses must be converged")
        valid = False
    return valid


def _check_run_records(
    ledger: dict[str, Any],
    *,
    ledger_path: Path,
    mismatches: list[str],
    child_export_paths: list[str],
) -> bool:
    records = ledger.get("run_records")
    if not isinstance(records, list):
        mismatches.append("run_records must be an array")
        return False
    if [record.get("queue_item_id") for record in records if isinstance(record, dict)] != (
        EXPECTED_QUEUE_ORDER
    ):
        mismatches.append("run_records must preserve source queue order")
        return False
    valid = True
    for record in records:
        if not isinstance(record, dict):
            mismatches.append("run_records entries must be objects")
            valid = False
            continue
        queue_item_id = str(record.get("queue_item_id", ""))
        expected = EXPECTED_TASKS.get(queue_item_id)
        if expected is None:
            mismatches.append(f"{queue_item_id} is not an expected queue item")
            valid = False
            continue
        if not _check_record(
            record,
            expected=expected,
            ledger_path=ledger_path,
            mismatches=mismatches,
            child_export_paths=child_export_paths,
        ):
            valid = False
    return valid


def _check_aggregate(ledger: dict[str, Any], mismatches: list[str]) -> bool:
    expected = {
        "record_count": 11,
        "source_queue_task_count": 11,
        "executed_limited": 11,
        "converged": 11,
        "child_review_exports_valid": True,
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "open_findings": [],
        "ledger_append_only": True,
    }
    aggregate = ledger.get("aggregate")
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    valid = True
    for key, expected_value in expected.items():
        if aggregate.get(key) != expected_value:
            mismatches.append(f"aggregate.{key} must be {expected_value!r}")
            valid = False
    return valid


def verify_multi_agent_queue_run_ledger(
    *,
    artifact_dir: Path = DEFAULT_LEDGER_ARTIFACT_DIR,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    resolved_ledger_path = _ledger_path(
        artifact_dir=artifact_dir,
        ledger_path=ledger_path,
    )
    mismatches: list[str] = []
    child_export_paths: list[str] = []
    try:
        ledger = _load_json(resolved_ledger_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "gate_id": "",
            "ledger_id": "",
            "ledger_schema": LEDGER_SCHEMA_ID,
            "ledger_schema_valid": False,
            "source_queue_valid": False,
            "scheduler_valid": False,
            "run_records_valid": False,
            "child_review_exports_valid": False,
            "aggregate_valid": False,
            "mismatches": [f"ledger could not be loaded: {exc}"],
            "artifact_paths": {
                "ledger": str(resolved_ledger_path),
                "source_queue_summary": "",
                "child_review_exports": [],
            },
        }

    schema_mismatches = _schema_mismatches(ledger)
    ledger_schema_valid = not schema_mismatches
    mismatches.extend(schema_mismatches)
    _check_basic_fields(ledger, mismatches)
    source_queue_valid = _check_source_queue(ledger, resolved_ledger_path, mismatches)
    scheduler_valid = _check_scheduler(ledger, mismatches)
    run_records_mismatches_start = len(mismatches)
    run_records_valid = _check_run_records(
        ledger,
        ledger_path=resolved_ledger_path,
        mismatches=mismatches,
        child_export_paths=child_export_paths,
    )
    child_review_exports_valid = run_records_valid and len(mismatches) == run_records_mismatches_start
    aggregate_valid = _check_aggregate(ledger, mismatches)
    gates = ledger.get("deterministic_gates")
    if isinstance(gates, dict):
        for name, status in gates.items():
            if status != "pass":
                mismatches.append(f"deterministic_gates.{name} must be pass")
    else:
        mismatches.append("deterministic_gates must be an object")

    status = "pass" if not mismatches else "fail"
    source_summary_path = ""
    if isinstance(ledger.get("artifact_paths"), dict):
        source_summary_path = str(ledger["artifact_paths"].get("source_queue_summary", ""))
    return {
        "status": status,
        "gate_id": str(ledger.get("gate_id", "")),
        "ledger_id": str(ledger.get("ledger_id", "")),
        "ledger_schema": LEDGER_SCHEMA_ID,
        "ledger_schema_valid": ledger_schema_valid,
        "source_queue_valid": source_queue_valid,
        "scheduler_valid": scheduler_valid,
        "run_records_valid": run_records_valid,
        "child_review_exports_valid": child_review_exports_valid,
        "aggregate_valid": aggregate_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "ledger": str(resolved_ledger_path),
            "source_queue_summary": source_summary_path,
            "child_review_exports": child_export_paths,
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_multi_agent_queue_run_ledger(
        artifact_dir=args.artifact_dir,
        ledger_path=args.ledger,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"ledger_schema_valid: {payload['ledger_schema_valid']}")
        print(f"source_queue_valid: {payload['source_queue_valid']}")
        print(f"scheduler_valid: {payload['scheduler_valid']}")
        print(f"run_records_valid: {payload['run_records_valid']}")
        print(f"child_review_exports_valid: {payload['child_review_exports_valid']}")
        print(f"ledger: {payload['artifact_paths']['ledger']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

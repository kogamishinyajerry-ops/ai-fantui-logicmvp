#!/usr/bin/env python3
"""Validate approved candidate task queue v0.3 and child review exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_ARTIFACT_DIR = Path("/tmp/ai-fantui-approved-candidate-task-queue-v0-3")
QUEUE_SUMMARY_NAME = "approved_candidate_task_queue_summary_v0_3.json"
QUEUE_GATE_ID = "approved-candidate-task-queue-v0-3"
QUEUE_ID = "approved-candidate-task-queue-v0.3"
QUEUE_SUMMARY_KIND = "ai-fantui-approved-candidate-task-queue-summary"
QUEUE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_candidate_task_queue_summary_v0_3.schema.json"
)
QUEUE_SUMMARY_SCHEMA_NAME = "approved_candidate_task_queue_summary_v0_3.schema.json"
TEMPLATE_ID = "approved-candidate-repair-task-template-v0.1"
FAST_GATE_COMMAND = "make multi-agent-fast-construction-gate"
V0_2_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
]
EXPECTED_QUEUE_ORDER = [
    *V0_2_QUEUE_ORDER,
    "queue-safety-undefined-signal-repair",
]
EXPECTED_TASKS = {
    "queue-safety-priority-repair": {
        "slice_id": "first-approved-candidate-repair-slice",
        "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "task_class": "SafetyRepairTask",
        "source_finding_code": "CHECK_SAFETY_PRIORITY_001",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-evidence-simulation-result-repair": {
        "slice_id": "evidence-approved-candidate-repair-slice",
        "task_id": "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "task_class": "EvidenceRepairTask",
        "source_finding_code": "EV_SIMULATION_RESULT_FAILED",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-evidence-test-result-missing-repair": {
        "slice_id": "missing-test-result-approved-candidate-repair-slice",
        "task_id": "TASK-CE-EV-TEST-RESULT-MISSING",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "task_class": "EvidenceRepairTask",
        "source_finding_code": "EV_TEST_RESULT_MISSING",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-requirement-ambiguity-repair": {
        "slice_id": "requirement-approved-candidate-repair-slice",
        "task_id": "TASK-CE-REQ-AMBIGUITY-UNRESOLVED",
        "target_agent": "RequirementRepairAgent",
        "task_type": "repair_structured_requirement_candidate",
        "task_class": "RequirementRepairTask",
        "source_finding_code": "REQ_AMBIGUITY_UNRESOLVED",
        "preflight_command": "make multi-agent-construction-readiness",
    },
    "queue-safety-undefined-signal-repair": {
        "slice_id": "safety-undefined-signal-approved-candidate-repair-slice",
        "task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "task_class": "SafetyRepairTask",
        "source_finding_code": "CHECK_UNDEFINED_SIGNAL_001",
        "preflight_command": FAST_GATE_COMMAND,
    },
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify approved candidate task queue v0.3 summary and child review exports.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_QUEUE_ARTIFACT_DIR,
        help="Directory containing approved_candidate_task_queue_summary_v0_3.json.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Explicit queue summary path. Overrides --artifact-dir.",
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


def _summary_path(*, artifact_dir: Path, summary_path: Path | None = None) -> Path:
    if summary_path is not None:
        return summary_path
    return artifact_dir / QUEUE_SUMMARY_NAME


def _load_schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / QUEUE_SUMMARY_SCHEMA_NAME)


def _schema_mismatches(summary: dict[str, Any]) -> list[str]:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_schema()).iter_errors(summary),
        key=lambda error: list(error.absolute_path),
    )
    mismatches: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(
            f"approved candidate task queue v0.3 schema validation failed{location}: {error.message}"
        )
    return mismatches


def _expected_aggregate() -> dict[str, Any]:
    return {
        "task_count": 5,
        "passed": 5,
        "preflight_passed": 5,
        "executed_limited": 5,
        "converged": 5,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "fast_gate_used_for_new_item": True,
    }


def _expected_append_only() -> dict[str, Any]:
    return {
        "previous_queue_id": "approved-candidate-task-queue-v0.2",
        "previous_task_count": 4,
        "preserved_prefix_count": 4,
        "new_task_count": 1,
        "template_id": TEMPLATE_ID,
    }


def _resolve_artifact_path(path_value: Any, summary_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return summary_path.parent / path


def _new_safety_item_valid(item: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if item.get("queue_item_id") != "queue-safety-undefined-signal-repair":
        mismatches.append("M9 queue item must be queue-safety-undefined-signal-repair")
        return False
    contract = item.get("queue_contract")
    preflight = item.get("preflight")
    if not isinstance(contract, dict) or not isinstance(preflight, dict):
        mismatches.append("M9 queue item must include queue_contract and preflight")
        return False
    expected = EXPECTED_TASKS["queue-safety-undefined-signal-repair"]
    checks = {
        "template_id": TEMPLATE_ID,
        "source_finding_code": expected["source_finding_code"],
        "task_class": "SafetyRepairTask",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_id": "APPROVAL-SAFETY-UNDEFINED-SIGNAL-REPAIR-SLICE-001",
        "readiness_command": FAST_GATE_COMMAND,
        "runner_contract": "candidate_review_packet_export_v0_1",
    }
    for key, expected_value in checks.items():
        if contract.get(key) != expected_value:
            mismatches.append(f"M9 queue_contract.{key} must be {expected_value}")
            valid = False
    if preflight.get("command") != FAST_GATE_COMMAND:
        mismatches.append("M9 queue item must use make multi-agent-fast-construction-gate")
        valid = False
    if preflight.get("gate_id") != "multi-agent-m8-fast-construction-gate":
        mismatches.append("M9 preflight.gate_id must be multi-agent-m8-fast-construction-gate")
        valid = False
    return valid


def verify_approved_candidate_task_queue_v0_3_artifact(
    *,
    artifact_dir: Path = DEFAULT_QUEUE_ARTIFACT_DIR,
    summary_path: Path | None = None,
) -> dict[str, Any]:
    resolved_summary_path = _summary_path(
        artifact_dir=artifact_dir,
        summary_path=summary_path,
    )
    summary_mismatches: list[str] = []
    child_mismatches: list[str] = []
    child_export_paths: list[str] = []
    summary: dict[str, Any] = {}

    try:
        summary = _load_json(resolved_summary_path)
    except (OSError, json.JSONDecodeError) as exc:
        summary_mismatches.append(f"summary could not be loaded: {exc}")
        return {
            "status": "fail",
            "gate_id": "",
            "kind": "",
            "summary_schema": QUEUE_SUMMARY_SCHEMA_ID,
            "summary_schema_valid": False,
            "summary_valid": False,
            "append_only_valid": False,
            "new_safety_item_valid": False,
            "fast_gate_valid": False,
            "child_review_exports_valid": False,
            "queue_order": [],
            "aggregate": {},
            "mismatches": summary_mismatches,
            "artifact_paths": {
                "summary": str(resolved_summary_path),
                "child_review_exports": child_export_paths,
            },
        }

    summary_schema_mismatches = _schema_mismatches(summary)
    summary_schema_valid = not summary_schema_mismatches
    summary_mismatches.extend(summary_schema_mismatches)

    if summary.get("$schema") != QUEUE_SUMMARY_SCHEMA_ID:
        summary_mismatches.append(f"$schema must be {QUEUE_SUMMARY_SCHEMA_ID}")
    if summary.get("kind") != QUEUE_SUMMARY_KIND:
        summary_mismatches.append(f"kind must be {QUEUE_SUMMARY_KIND}")
    if summary.get("gate_id") != QUEUE_GATE_ID:
        summary_mismatches.append(f"gate_id must be {QUEUE_GATE_ID}")
    if summary.get("queue_id") != QUEUE_ID:
        summary_mismatches.append(f"queue_id must be {QUEUE_ID}")
    if summary.get("status") != "pass":
        summary_mismatches.append("summary.status must be pass")
    if summary.get("ready_for_long_running_development") is not True:
        summary_mismatches.append("ready_for_long_running_development must be true")

    queue_order = summary.get("queue_order")
    append_only_valid = True
    if queue_order != EXPECTED_QUEUE_ORDER:
        summary_mismatches.append("queue_order must list the approved v0.3 queue in expected order")
    if not isinstance(queue_order, list) or queue_order[:4] != V0_2_QUEUE_ORDER:
        summary_mismatches.append("v0.3 queue must preserve v0.2 queue order prefix")
        append_only_valid = False
    if summary.get("append_only") != _expected_append_only():
        summary_mismatches.append("append_only must describe one-item v0.3 growth from v0.2")
        append_only_valid = False

    aggregate = summary.get("aggregate")
    fast_gate_valid = True
    if not isinstance(aggregate, dict):
        summary_mismatches.append("aggregate must be an object")
        aggregate = {}
        fast_gate_valid = False
    else:
        for key, expected in _expected_aggregate().items():
            if aggregate.get(key) != expected:
                if key == "open_findings":
                    summary_mismatches.append("aggregate.open_findings must be empty")
                else:
                    summary_mismatches.append(f"aggregate.{key} must be {expected!r}")
                if key == "fast_gate_used_for_new_item":
                    fast_gate_valid = False

    deterministic_gates = summary.get("deterministic_gates")
    if not isinstance(deterministic_gates, dict):
        summary_mismatches.append("deterministic_gates must be an object")
        fast_gate_valid = False
    else:
        for gate_name, gate_status in deterministic_gates.items():
            if gate_status != "pass":
                summary_mismatches.append(f"deterministic_gates.{gate_name} must be pass")
                if gate_name == "m8_fast_construction_gate":
                    fast_gate_valid = False

    items = summary.get("items")
    if not isinstance(items, list):
        summary_mismatches.append("items must be an array")
        items = []
    if len(items) != len(EXPECTED_QUEUE_ORDER):
        summary_mismatches.append("items must contain exactly five queue summaries")

    item_ids = [item.get("queue_item_id") for item in items if isinstance(item, dict)]
    if item_ids != EXPECTED_QUEUE_ORDER:
        summary_mismatches.append("items must be ordered according to queue_order")

    new_safety_item_valid = False
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            summary_mismatches.append(f"items.{index} must be an object")
            continue
        queue_item_id = str(item.get("queue_item_id", ""))
        expected = EXPECTED_TASKS.get(queue_item_id, {})
        if queue_item_id == "queue-safety-undefined-signal-repair":
            new_safety_item_valid = _new_safety_item_valid(item, summary_mismatches)
            fast_gate_valid = fast_gate_valid and new_safety_item_valid
        if item.get("status") != "pass":
            summary_mismatches.append(f"{queue_item_id}.status must be pass")
        if expected and item.get("slice_id") != expected["slice_id"]:
            summary_mismatches.append(f"{queue_item_id}.slice_id must be {expected['slice_id']}")

        contract = item.get("queue_contract")
        if not isinstance(contract, dict):
            summary_mismatches.append(f"{queue_item_id}.queue_contract must be an object")
        elif expected:
            for key in ("source_finding_code", "task_class", "target_agent", "task_type"):
                if contract.get(key) != expected[key]:
                    summary_mismatches.append(
                        f"{queue_item_id}.queue_contract.{key} must be {expected[key]}"
                    )
            if contract.get("readiness_command") != expected["preflight_command"]:
                summary_mismatches.append(
                    f"{queue_item_id}.queue_contract.readiness_command must be {expected['preflight_command']}"
                )

        preflight = item.get("preflight")
        if not isinstance(preflight, dict):
            summary_mismatches.append(f"{queue_item_id}.preflight must be an object")
        else:
            if preflight.get("status") != "pass":
                summary_mismatches.append(f"{queue_item_id}.preflight.status must be pass")
            if expected and preflight.get("command") != expected["preflight_command"]:
                summary_mismatches.append(
                    f"{queue_item_id}.preflight.command must be {expected['preflight_command']}"
                )
            if preflight.get("returncode") != 0:
                summary_mismatches.append(f"{queue_item_id}.preflight.returncode must be 0")

        shell = item.get("approved_task_shell")
        if not isinstance(shell, dict):
            summary_mismatches.append(f"{queue_item_id}.approved_task_shell must be an object")
        else:
            if shell.get("status") != "executed_limited":
                summary_mismatches.append(
                    f"{queue_item_id}.approved_task_shell.status must be executed_limited"
                )
            if shell.get("approval_status") != "approved":
                summary_mismatches.append(
                    f"{queue_item_id}.approved_task_shell.approval_status must be approved"
                )
            if expected and shell.get("selected_task_id") != expected["task_id"]:
                summary_mismatches.append(
                    f"{queue_item_id}.approved_task_shell.selected_task_id must be {expected['task_id']}"
                )

        selected_task = item.get("selected_task")
        if not isinstance(selected_task, dict):
            summary_mismatches.append(f"{queue_item_id}.selected_task must be an object")
        else:
            if expected and selected_task.get("task_id") != expected["task_id"]:
                summary_mismatches.append(
                    f"{queue_item_id}.selected_task.task_id must be {expected['task_id']}"
                )
            if expected and selected_task.get("target_agent") != expected["target_agent"]:
                summary_mismatches.append(
                    f"{queue_item_id}.selected_task.target_agent must be {expected['target_agent']}"
                )

        execution = item.get("execution")
        if not isinstance(execution, dict):
            summary_mismatches.append(f"{queue_item_id}.execution must be an object")
        else:
            if execution.get("status") != "pass":
                summary_mismatches.append(f"{queue_item_id}.execution.status must be pass")
            if execution.get("reviewer_status") != "converged":
                summary_mismatches.append(
                    f"{queue_item_id}.execution.reviewer_status must be converged"
                )
            if execution.get("finding_chain_statuses") != ["converged"]:
                summary_mismatches.append(
                    f"{queue_item_id}.execution.finding_chain_statuses must be converged"
                )

        boundary = item.get("boundary")
        if not isinstance(boundary, dict):
            summary_mismatches.append(f"{queue_item_id}.boundary must be an object")
        else:
            if boundary.get("controller_truth_modified") is not False:
                summary_mismatches.append(
                    f"{queue_item_id}.boundary.controller_truth_modified must be false"
                )
            if boundary.get("ui_layout_modified") is not False:
                summary_mismatches.append(
                    f"{queue_item_id}.boundary.ui_layout_modified must be false"
                )

        artifact_paths = item.get("artifact_paths")
        review_export_path = None
        if isinstance(artifact_paths, dict):
            review_export_path = _resolve_artifact_path(
                artifact_paths.get("candidate_review_packet_export"),
                resolved_summary_path,
            )
        if review_export_path is None:
            child_mismatches.append(
                f"{queue_item_id}.artifact_paths.candidate_review_packet_export is required"
            )
            continue

        child_export_paths.append(str(review_export_path))
        try:
            review_export = _load_json(review_export_path)
            validate_candidate_review_packet_export(review_export)
        except Exception as exc:  # noqa: BLE001 - checker reports all artifact failures.
            child_mismatches.append(
                f"{queue_item_id}.candidate_review_packet_export invalid: {exc}"
            )
            continue
        review_packet = review_export.get("review_packet", {})
        if not isinstance(review_packet, dict):
            child_mismatches.append(f"{queue_item_id}.review_packet must be an object")
            continue
        if review_packet.get("reviewer", {}).get("status") != "converged":
            child_mismatches.append(
                f"{queue_item_id}.review_packet.reviewer.status must be converged"
            )
        if queue_item_id == "queue-safety-undefined-signal-repair":
            chains = review_packet.get("finding_chains")
            chain = chains[0] if isinstance(chains, list) and chains else {}
            finding = chain.get("finding") if isinstance(chain, dict) else {}
            if not isinstance(finding, dict) or finding.get("code") != "CHECK_UNDEFINED_SIGNAL_001":
                child_mismatches.append(
                    "queue-safety-undefined-signal-repair review export must include CHECK_UNDEFINED_SIGNAL_001"
                )

    if not fast_gate_valid and "M9 queue item must use make multi-agent-fast-construction-gate" not in summary_mismatches:
        summary_mismatches.append("M9 queue item must use make multi-agent-fast-construction-gate")

    mismatches = summary_mismatches + child_mismatches
    summary_valid = not summary_mismatches
    child_review_exports_valid = not child_mismatches
    status = "pass" if summary_valid and child_review_exports_valid else "fail"

    return {
        "status": status,
        "gate_id": str(summary.get("gate_id", "")),
        "kind": str(summary.get("kind", "")),
        "summary_schema": QUEUE_SUMMARY_SCHEMA_ID,
        "summary_schema_valid": summary_schema_valid,
        "summary_valid": summary_valid,
        "append_only_valid": append_only_valid,
        "new_safety_item_valid": new_safety_item_valid,
        "fast_gate_valid": fast_gate_valid,
        "child_review_exports_valid": child_review_exports_valid,
        "queue_order": list(summary.get("queue_order", [])),
        "aggregate": dict(aggregate),
        "mismatches": mismatches,
        "artifact_paths": {
            "summary": str(resolved_summary_path),
            "child_review_exports": child_export_paths,
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_approved_candidate_task_queue_v0_3_artifact(
        artifact_dir=args.artifact_dir,
        summary_path=args.summary,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"summary_valid: {payload['summary_valid']}")
        print(f"summary_schema_valid: {payload['summary_schema_valid']}")
        print(f"append_only_valid: {payload['append_only_valid']}")
        print(f"new_safety_item_valid: {payload['new_safety_item_valid']}")
        print(f"fast_gate_valid: {payload['fast_gate_valid']}")
        print(f"child_review_exports_valid: {payload['child_review_exports_valid']}")
        print(f"summary: {payload['artifact_paths']['summary']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

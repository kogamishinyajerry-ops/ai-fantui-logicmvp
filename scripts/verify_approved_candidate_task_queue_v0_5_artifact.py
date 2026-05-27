#!/usr/bin/env python3
"""Validate approved candidate task queue v0.5 and child review exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_ARTIFACT_DIR = Path("/tmp/ai-fantui-approved-candidate-task-queue-v0-5")
QUEUE_SUMMARY_NAME = "approved_candidate_task_queue_summary_v0_5.json"
QUEUE_GATE_ID = "approved-candidate-task-queue-v0-5"
QUEUE_ID = "approved-candidate-task-queue-v0.5"
QUEUE_SUMMARY_KIND = "ai-fantui-approved-candidate-task-queue-summary"
QUEUE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_candidate_task_queue_summary_v0_5.schema.json"
)
QUEUE_SUMMARY_SCHEMA_NAME = "approved_candidate_task_queue_summary_v0_5.schema.json"
FAST_GATE_COMMAND = "make multi-agent-fast-construction-gate"
V0_4_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
    "queue-safety-undefined-signal-repair",
    "queue-evidence-boundary-review-repair",
]
M17_QUEUE_ITEM_ID = "queue-evidence-unknown-requirement-repair"
EXPECTED_QUEUE_ORDER = [*V0_4_QUEUE_ORDER, M17_QUEUE_ITEM_ID]
EXPECTED_TASKS = {
    "queue-evidence-unknown-requirement-repair": {
        "slice_id": "evidence-unknown-requirement-approved-candidate-repair-slice",
        "task_id": "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "task_class": "EvidenceRepairTask",
        "source_finding_code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        "approval_id": "APPROVAL-EVIDENCE-UNKNOWN-REQUIREMENT-REPAIR-SLICE-001",
        "preflight_command": FAST_GATE_COMMAND,
    },
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify approved candidate task queue v0.5 summary and child review exports.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_QUEUE_ARTIFACT_DIR)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary_path(*, artifact_dir: Path, summary_path: Path | None = None) -> Path:
    return summary_path if summary_path is not None else artifact_dir / QUEUE_SUMMARY_NAME


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
            f"approved candidate task queue v0.5 schema validation failed{location}: {error.message}"
        )
    return mismatches


def _resolve_artifact_path(path_value: Any, summary_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    return path if path.is_absolute() else summary_path.parent / path


def _expected_aggregate() -> dict[str, Any]:
    return {
        "task_count": 7,
        "passed": 7,
        "preflight_passed": 7,
        "executed_limited": 7,
        "converged": 7,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "fast_gate_used_for_new_item": True,
        "appended_record_id": "RUN-QUEUE-007",
    }


def verify_approved_candidate_task_queue_v0_5_artifact(
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
    try:
        summary = _load_json(resolved_summary_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "gate_id": "",
            "kind": "",
            "summary_schema": QUEUE_SUMMARY_SCHEMA_ID,
            "summary_schema_valid": False,
            "summary_valid": False,
            "append_only_valid": False,
            "new_evidence_item_valid": False,
            "fast_gate_valid": False,
            "child_review_exports_valid": False,
            "queue_order": [],
            "aggregate": {},
            "mismatches": [f"summary could not be loaded: {exc}"],
            "artifact_paths": {
                "summary": str(resolved_summary_path),
                "child_review_exports": child_export_paths,
            },
        }

    schema_mismatches = _schema_mismatches(summary)
    summary_schema_valid = not schema_mismatches
    summary_mismatches.extend(schema_mismatches)

    checks = {
        "$schema": QUEUE_SUMMARY_SCHEMA_ID,
        "kind": QUEUE_SUMMARY_KIND,
        "gate_id": QUEUE_GATE_ID,
        "queue_id": QUEUE_ID,
        "status": "pass",
    }
    for key, expected in checks.items():
        if summary.get(key) != expected:
            summary_mismatches.append(f"{key} must be {expected}")
    if summary.get("ready_for_long_running_development") is not True:
        summary_mismatches.append("ready_for_long_running_development must be true")

    queue_order = summary.get("queue_order")
    append_only_valid = True
    if queue_order != EXPECTED_QUEUE_ORDER:
        summary_mismatches.append("queue_order must list the approved v0.5 queue in expected order")
    if not isinstance(queue_order, list) or queue_order[:6] != V0_4_QUEUE_ORDER:
        summary_mismatches.append("v0.5 queue must preserve v0.4 queue order prefix")
        append_only_valid = False
    append_only = summary.get("append_only")
    expected_append_only = {
        "previous_queue_id": "approved-candidate-task-queue-v0.4",
        "previous_task_count": 6,
        "preserved_prefix_count": 6,
        "new_task_count": 1,
        "template_id": "approved-candidate-repair-task-template-v0.1",
        "appended_record_id": "RUN-QUEUE-007",
    }
    if append_only != expected_append_only:
        summary_mismatches.append("append_only must describe one appended v0.5 item from v0.4")
        append_only_valid = False

    aggregate = summary.get("aggregate") if isinstance(summary.get("aggregate"), dict) else {}
    fast_gate_valid = True
    for key, expected in _expected_aggregate().items():
        if aggregate.get(key) != expected:
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
        items = []
        summary_mismatches.append("items must be an array")
    if [item.get("queue_item_id") for item in items if isinstance(item, dict)] != EXPECTED_QUEUE_ORDER:
        summary_mismatches.append("items must be ordered according to queue_order")

    new_evidence_item_valid = False
    for item in items:
        if not isinstance(item, dict):
            summary_mismatches.append("queue item must be an object")
            continue
        queue_item_id = str(item.get("queue_item_id", ""))
        expected = EXPECTED_TASKS.get(queue_item_id)
        if item.get("status") != "pass":
            summary_mismatches.append(f"{queue_item_id}.status must be pass")
        if queue_item_id == M17_QUEUE_ITEM_ID:
            if expected and item.get("slice_id") != expected["slice_id"]:
                summary_mismatches.append(f"{queue_item_id}.slice_id must be {expected['slice_id']}")
            contract = item.get("queue_contract", {})
            if not isinstance(contract, dict):
                summary_mismatches.append(f"{queue_item_id}.queue_contract must be an object")
                contract = {}
            for key in (
                "source_finding_code",
                "task_class",
                "target_agent",
                "task_type",
                "approval_id",
            ):
                if expected and contract.get(key) != expected[key]:
                    summary_mismatches.append(
                        f"{queue_item_id}.queue_contract.{key} must be {expected[key]}"
                    )
            if contract.get("readiness_command") != FAST_GATE_COMMAND:
                summary_mismatches.append(
                    f"{queue_item_id}.queue_contract.readiness_command must be {FAST_GATE_COMMAND}"
                )
                fast_gate_valid = False
            if item.get("preflight", {}).get("command") != FAST_GATE_COMMAND:
                summary_mismatches.append(f"{queue_item_id}.preflight.command must be {FAST_GATE_COMMAND}")
                fast_gate_valid = False
            if item.get("approved_task_shell", {}).get("selected_task_id") != expected["task_id"]:
                summary_mismatches.append(
                    f"{queue_item_id}.approved_task_shell.selected_task_id must be {expected['task_id']}"
                )
            if item.get("selected_task", {}).get("target_agent") != expected["target_agent"]:
                summary_mismatches.append(
                    f"{queue_item_id}.selected_task.target_agent must be {expected['target_agent']}"
                )
            new_evidence_item_valid = not any(
                mismatch.startswith(f"{queue_item_id}.") for mismatch in summary_mismatches
            )

        for section, field in (
            ("preflight", "status"),
            ("execution", "status"),
            ("approved_task_shell", "status"),
        ):
            if not isinstance(item.get(section), dict):
                summary_mismatches.append(f"{queue_item_id}.{section} must be an object")
                continue
            expected_value = "pass" if section != "approved_task_shell" else "executed_limited"
            if item[section].get(field) != expected_value:
                summary_mismatches.append(
                    f"{queue_item_id}.{section}.{field} must be {expected_value}"
                )
        if item.get("execution", {}).get("reviewer_status") != "converged":
            summary_mismatches.append(f"{queue_item_id}.execution.reviewer_status must be converged")
        if item.get("execution", {}).get("finding_chain_statuses") != ["converged"]:
            summary_mismatches.append(f"{queue_item_id}.execution.finding_chain_statuses must be converged")
        boundary = item.get("boundary", {})
        if boundary.get("controller_truth_modified") is not False:
            summary_mismatches.append(f"{queue_item_id}.boundary.controller_truth_modified must be false")
        if boundary.get("ui_layout_modified") is not False:
            summary_mismatches.append(f"{queue_item_id}.boundary.ui_layout_modified must be false")

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
        except Exception as exc:  # noqa: BLE001
            child_mismatches.append(f"{queue_item_id}.candidate_review_packet_export invalid: {exc}")
            continue
        review_packet = review_export.get("review_packet", {})
        if review_packet.get("reviewer", {}).get("status") != "converged":
            child_mismatches.append(f"{queue_item_id}.review_packet.reviewer.status must be converged")
        if queue_item_id == M17_QUEUE_ITEM_ID:
            chains = review_packet.get("finding_chains")
            chain = chains[0] if isinstance(chains, list) and chains else {}
            finding = chain.get("finding") if isinstance(chain, dict) else {}
            if not isinstance(finding, dict) or finding.get("code") != "EV_TEST_COVERS_UNKNOWN_REQUIREMENT":
                child_mismatches.append(
                    "queue-evidence-unknown-requirement-repair review export must include EV_TEST_COVERS_UNKNOWN_REQUIREMENT"
                )

    mismatches = summary_mismatches + child_mismatches
    return {
        "status": "pass" if not mismatches else "fail",
        "gate_id": str(summary.get("gate_id", "")),
        "kind": str(summary.get("kind", "")),
        "summary_schema": QUEUE_SUMMARY_SCHEMA_ID,
        "summary_schema_valid": summary_schema_valid,
        "summary_valid": not summary_mismatches,
        "append_only_valid": append_only_valid,
        "new_evidence_item_valid": new_evidence_item_valid,
        "fast_gate_valid": fast_gate_valid,
        "child_review_exports_valid": not child_mismatches,
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
    payload = verify_approved_candidate_task_queue_v0_5_artifact(
        artifact_dir=args.artifact_dir,
        summary_path=args.summary,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"summary: {payload['artifact_paths']['summary']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

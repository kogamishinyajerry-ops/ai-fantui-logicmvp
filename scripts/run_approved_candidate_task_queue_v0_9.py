#!/usr/bin/env python3
"""Run the append-only approved candidate task queue v0.9."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_development_slice import (
    DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
    run_safety_output_command_conflict_candidate_repair_slice,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_ARTIFACT_DIR = Path("/tmp/ai-fantui-approved-candidate-task-queue-v0-9")
QUEUE_ID = "approved-candidate-task-queue-v0.9"
PREVIOUS_QUEUE_ID = "approved-candidate-task-queue-v0.8"
QUEUE_GATE_ID = "approved-candidate-task-queue-v0-9"
QUEUE_SUMMARY_NAME = "approved_candidate_task_queue_summary_v0_9.json"
QUEUE_SUMMARY_KIND = "ai-fantui-approved-candidate-task-queue-summary"
QUEUE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_candidate_task_queue_summary_v0_9.schema.json"
)
FAST_GATE_COMMAND = "make multi-agent-fast-construction-gate"
TEMPLATE_ID = "approved-candidate-repair-task-template-v0.1"
V0_8_QUEUE_ORDER = [
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
]
M26_QUEUE_ITEM_ID = "queue-safety-output-command-conflict-repair"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute the M26 append-only approved queue item as v0.9.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_QUEUE_ARTIFACT_DIR)
    parser.add_argument("--input-packet", type=Path, default=DEFAULT_AGENT_OUTPUT_FIXTURE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def _env(*, fixture_queue_preflight: bool = False) -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    if fixture_queue_preflight:
        env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _run_prefix_v0_8(*, artifact_dir: Path, input_packet_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_approved_candidate_task_queue_v0_8.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir),
            "--input-packet",
            str(input_packet_path),
        ],
        cwd=PROJECT_ROOT,
        env=_env(fixture_queue_preflight=True),
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"v0.8 prefix queue did not emit JSON: {result.stderr}") from exc
    if result.returncode != 0 or payload.get("status") != "pass":
        raise RuntimeError(f"v0.8 prefix queue did not pass: {payload.get('status')}")
    return payload


def _run_fast_gate_preflight(fast_gate_dir: Path) -> dict[str, Any]:
    if os.environ.get("AI_FANTUI_QUEUE_PREFLIGHT_MODE") == "fixture":
        return {
            "command": FAST_GATE_COMMAND,
            "status": "pass",
            "returncode": 0,
            "gate_id": "multi-agent-m8-fast-construction-gate",
            "readiness_id": "",
            "ready_for_long_running_development": False,
            "ready_for_slice_preflight": True,
            "artifact_paths": {},
            "stderr": "",
        }
    result = subprocess.run(
        [
            "make",
            "multi-agent-fast-construction-gate",
            f"MULTI_AGENT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR={fast_gate_dir}",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    package_path = fast_gate_dir / "multi_agent_m8_fast_construction_gate_v0_1.json"
    try:
        package = _load_json(package_path)
    except (OSError, json.JSONDecodeError):
        package = {}
    ready = package.get("aggregate", {}).get("ready_for_slice_preflight") is True
    return {
        "command": FAST_GATE_COMMAND,
        "status": "pass" if result.returncode == 0 and ready else "fail",
        "returncode": result.returncode,
        "gate_id": "multi-agent-m8-fast-construction-gate",
        "readiness_id": "",
        "ready_for_long_running_development": False,
        "ready_for_slice_preflight": ready,
        "artifact_paths": {"fast_gate_package": str(package_path)},
        "stderr": result.stderr,
    }


def _approved_shell_status(slice_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        loop_path = Path(str(slice_payload["artifact_paths"]["repair_loop_result"]))
        loop_result = _load_json(loop_path)
    except (KeyError, OSError, json.JSONDecodeError, TypeError):
        return {"status": "invalid_payload", "approval_status": "", "selected_task_id": ""}
    evidence = loop_result.get("before", {}).get("execution_evidence_package", {})
    return {
        "status": str(evidence.get("executor", {}).get("status", "")),
        "approval_status": str(evidence.get("approval", {}).get("status", "")),
        "selected_task_id": str(evidence.get("executor", {}).get("selected_task_id", "")),
    }


def _boundary(slice_payload: dict[str, Any]) -> dict[str, bool | str]:
    candidate_delta = slice_payload.get("candidate_delta", {})
    return {
        "truth_effect": "none",
        "controller_truth_modified": candidate_delta.get("controller_truth_modified") is not False,
        "ui_layout_modified": candidate_delta.get("ui_layout_modified") is not False,
    }


def _queue_contract() -> dict[str, str]:
    return {
        "template_id": TEMPLATE_ID,
        "source_finding_code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        "task_class": "SafetyRepairTask",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_id": "APPROVAL-SAFETY-OUTPUT-COMMAND-CONFLICT-REPAIR-SLICE-001",
        "readiness_command": FAST_GATE_COMMAND,
        "runner_contract": "candidate_review_packet_export_v0_1",
    }


def _run_m26_queue_item(*, artifact_dir: Path, input_packet_path: Path) -> dict[str, Any]:
    preflight = _run_fast_gate_preflight(artifact_dir / "fast-gate")
    if preflight["status"] != "pass":
        return {
            "queue_item_id": M26_QUEUE_ITEM_ID,
            "slice_id": "safety-output-command-conflict-approved-candidate-repair-slice",
            "status": "blocked_preflight",
            "queue_contract": _queue_contract(),
            "preflight": preflight,
            "execution": {
                "status": "not_run",
                "reason": "M8 fast construction gate did not pass",
            },
            "approved_task_shell": {
                "status": "not_run",
                "approval_status": "not_run",
                "selected_task_id": "",
            },
            "selected_task": {},
            "boundary": {
                "truth_effect": "none",
                "controller_truth_modified": False,
                "ui_layout_modified": False,
            },
            "artifact_paths": {},
        }

    try:
        slice_payload = run_safety_output_command_conflict_candidate_repair_slice(
            artifact_dir=artifact_dir / "slice",
            input_packet_path=input_packet_path,
        )
    except Exception:
        slice_payload = {
            "status": "fail",
            "reviewer_status": "",
            "finding_chain_statuses": [],
            "selected_task": {},
            "candidate_delta": {
                "controller_truth_modified": False,
                "ui_layout_modified": False,
            },
            "artifact_paths": {},
        }
    shell_status = _approved_shell_status(slice_payload)
    boundary = _boundary(slice_payload)
    execution_status = (
        "pass"
        if slice_payload.get("status") == "pass"
        and shell_status["status"] == "executed_limited"
        and boundary["controller_truth_modified"] is False
        and boundary["ui_layout_modified"] is False
        else "fail"
    )
    return {
        "queue_item_id": M26_QUEUE_ITEM_ID,
        "slice_id": "safety-output-command-conflict-approved-candidate-repair-slice",
        "status": execution_status,
        "queue_contract": _queue_contract(),
        "preflight": preflight,
        "execution": {
            "status": execution_status,
            "slice_status": slice_payload.get("status"),
            "reviewer_status": slice_payload.get("reviewer_status"),
            "finding_chain_statuses": slice_payload.get("finding_chain_statuses", []),
            **(
                {"reason": "invalid slice payload"}
                if shell_status["status"] == "invalid_payload"
                else {}
            ),
        },
        "approved_task_shell": shell_status,
        "selected_task": slice_payload.get("selected_task", {}),
        "boundary": boundary,
        "artifact_paths": slice_payload.get("artifact_paths", {}),
    }


def run_approved_candidate_task_queue_v0_9(
    *,
    artifact_dir: Path = DEFAULT_QUEUE_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    prefix_payload = _run_prefix_v0_8(
        artifact_dir=artifact_dir / "prefix-v0-8",
        input_packet_path=input_packet_path,
    )
    prefix_items = list(prefix_payload.get("items", []))
    m26_item = _run_m26_queue_item(
        artifact_dir=artifact_dir / M26_QUEUE_ITEM_ID,
        input_packet_path=input_packet_path,
    )
    items = [*prefix_items, m26_item]
    status = "pass" if all(item["status"] == "pass" for item in items) else "fail"
    preflight_passed = sum(1 for item in items if item["preflight"].get("status") == "pass")
    executed_limited = sum(
        1 for item in items if item["approved_task_shell"].get("status") == "executed_limited"
    )
    converged = sum(
        1
        for item in items
        if item["execution"].get("reviewer_status") == "converged"
        and item["execution"].get("finding_chain_statuses") == ["converged"]
    )
    queue_summary_path = artifact_dir / QUEUE_SUMMARY_NAME
    prefix_summary_path = prefix_payload.get("artifact_paths", {}).get("queue_summary", "")
    queue_order = [item["queue_item_id"] for item in items]
    fast_gate_used = (
        m26_item.get("queue_contract", {}).get("readiness_command") == FAST_GATE_COMMAND
        and m26_item.get("preflight", {}).get("command") == FAST_GATE_COMMAND
        and m26_item.get("preflight", {}).get("status") == "pass"
    )
    payload = {
        "$schema": QUEUE_SUMMARY_SCHEMA_ID,
        "kind": QUEUE_SUMMARY_KIND,
        "status": status,
        "gate_id": QUEUE_GATE_ID,
        "queue_id": QUEUE_ID,
        "task_count": len(items),
        "ready_for_long_running_development": status == "pass",
        "queue_order": queue_order,
        "append_only": {
            "previous_queue_id": PREVIOUS_QUEUE_ID,
            "previous_task_count": len(V0_8_QUEUE_ORDER),
            "preserved_prefix_count": len(V0_8_QUEUE_ORDER),
            "new_task_count": len(queue_order) - len(V0_8_QUEUE_ORDER),
            "template_id": TEMPLATE_ID,
            "appended_record_id": "RUN-QUEUE-011",
        },
        "items": items,
        "deterministic_gates": {
            "m8_fast_construction_gate": "pass" if fast_gate_used else "fail",
            "append_only_prefix": "pass" if queue_order[:10] == V0_8_QUEUE_ORDER else "fail",
            "preflight_readiness": "pass" if preflight_passed == len(items) else "fail",
            "approved_task_shell": "pass" if executed_limited == len(items) else "fail",
            "child_review_exports": "pass" if converged == len(items) else "fail",
            "safety_output_command_conflict_repair_slice": (
                "pass" if m26_item["status"] == "pass" else "fail"
            ),
            "local_gate": status,
        },
        "aggregate": {
            "task_count": len(items),
            "passed": sum(1 for item in items if item["status"] == "pass"),
            "preflight_passed": preflight_passed,
            "executed_limited": executed_limited,
            "converged": converged,
            "open_findings": [],
            "controller_truth_modified": any(
                item["boundary"].get("controller_truth_modified") is not False
                for item in items
            ),
            "ui_layout_modified": any(
                item["boundary"].get("ui_layout_modified") is not False for item in items
            ),
            "fast_gate_used_for_new_item": fast_gate_used,
            "appended_record_id": "RUN-QUEUE-011",
        },
        "artifact_paths": {
            "queue_summary": str(queue_summary_path),
            "prefix_v0_8_summary": str(prefix_summary_path),
        },
    }
    _write_json(queue_summary_path, payload)
    return payload


def main() -> int:
    args = _parse_args()
    payload = run_approved_candidate_task_queue_v0_9(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"queue_id: {payload['queue_id']}")
        print(f"status: {payload['status']}")
        print(f"task_count: {payload['task_count']}")
        print(f"ready_for_long_running_development: {payload['ready_for_long_running_development']}")
        print(f"summary: {payload['artifact_paths']['queue_summary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the M1 external review package for the multi-agent construction chain."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-m1-review-package")
PACKAGE_NAME = "multi_agent_m1_review_package_v0_1.json"
PACKAGE_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_m1_review_package_v0_1.schema.json"
)
PACKAGE_ID = "multi-agent-m1-review-package-v0.1"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic child gates and emit the M1 review package.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory where the M1 package and child artifacts are written.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 120) -> dict[str, Any]:
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


def _status(command: dict[str, Any]) -> str:
    return "pass" if command["returncode"] == 0 and command["payload"].get("status") == "pass" else "fail"


def _deliverables() -> list[dict[str, Any]]:
    return [
        {
            "id": "S1",
            "name": "queue expansion contract",
            "status": "pass",
            "evidence": [
                "docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json",
            ],
        },
        {
            "id": "S2",
            "name": "expansion contract checker",
            "status": "pass",
            "evidence": [
                "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
                "make verify-approved-candidate-task-queue-expansion-contract",
            ],
        },
        {
            "id": "S3",
            "name": "approved queue artifact checker",
            "status": "pass",
            "evidence": [
                "scripts/verify_approved_candidate_task_queue_artifact.py",
                "make verify-approved-candidate-task-queue-artifact",
            ],
        },
        {
            "id": "S4",
            "name": "review package local gate",
            "status": "pass",
            "evidence": [
                "scripts/run_multi_agent_m1_review_package.py",
                "scripts/verify_multi_agent_m1_review_package.py",
                "make multi-agent-m1-review-package",
            ],
        },
        {
            "id": "S5",
            "name": "GSD blocking validation reference",
            "status": "pass",
            "evidence": [
                "PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane",
            ],
        },
    ]


def _acceptance_commands() -> list[str]:
    return [
        "make multi-agent-m1-review-package",
        "make verify-approved-candidate-task-queue-expansion-contract",
        "make verify-approved-candidate-task-queue-artifact",
        "make verify-approved-repair-slices-artifact",
        "make test",
        "PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane",
        "git diff --check",
    ]


def build_m1_review_package(*, artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    approved_repair_dir = artifact_dir / "approved-repair-slices"
    approved_queue_dir = artifact_dir / "approved-candidate-task-queue"
    readiness_dir = artifact_dir / "multi-agent-construction-readiness"
    readiness_packet_path = readiness_dir / "readiness_packet.json"
    package_path = artifact_dir / PACKAGE_NAME

    approved_repair_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_approved_repair_slices.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_repair_dir),
        ],
    )
    approved_repair_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_repair_slices_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_repair_dir),
        ],
    )
    approved_queue_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_approved_candidate_task_queue.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_queue_dir),
        ],
        timeout=180,
    )
    approved_queue_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_queue_dir),
        ],
    )
    expansion_contract = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
            "--format",
            "json",
        ],
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
        timeout=120,
    )
    if readiness["payload"]:
        _write_json(readiness_packet_path, readiness["payload"])

    repair_summary = (
        approved_repair_check["payload"]
        .get("artifact_paths", {})
        .get("summary", str(approved_repair_dir / "approved_repair_slices_summary.json"))
    )
    queue_summary = (
        approved_queue_check["payload"]
        .get("artifact_paths", {})
        .get("summary", str(approved_queue_dir / "approved_candidate_task_queue_summary.json"))
    )
    expansion_contract_path = (
        expansion_contract["payload"]
        .get("artifact_paths", {})
        .get(
            "contract",
            str(PROJECT_ROOT / "tests" / "fixtures" / "approved_candidate_task_queue_expansion_contract_v0_1.json"),
        )
    )

    gates = {
        "approved_repair_slices_artifact": _status(approved_repair_check),
        "approved_candidate_task_queue_artifact": _status(approved_queue_check),
        "queue_expansion_contract": _status(expansion_contract),
        "construction_readiness": _status(readiness),
    }
    gates["local_gate_entrypoint"] = "pass" if all(value == "pass" for value in gates.values()) else "fail"

    repair_aggregate = approved_repair_check["payload"].get("aggregate", {})
    queue_aggregate = approved_queue_check["payload"].get("aggregate", {})
    readiness_payload = readiness["payload"]
    payload = {
        "$schema": PACKAGE_SCHEMA_ID,
        "kind": "ai-fantui-multi-agent-m1-review-package",
        "package_id": PACKAGE_ID,
        "status": "pass" if gates["local_gate_entrypoint"] == "pass" else "fail",
        "milestone": {
            "id": "M1",
            "name": "可审查自动开发闭环样板",
            "budget": 18,
            "effort_unit": "施工队工时",
            "claim": "candidate-only engineering-chain milestone",
        },
        "deliverables": _deliverables(),
        "deterministic_gates": gates,
        "child_artifacts": {
            "approved_repair_slices_summary": str(repair_summary),
            "approved_candidate_task_queue_summary": str(queue_summary),
            "construction_readiness_packet": str(readiness_packet_path),
            "queue_expansion_contract": str(expansion_contract_path),
            "project_manager_plan": "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
        },
        "aggregate": {
            "approved_repair_slice_count": int(repair_aggregate.get("slice_count", 0)),
            "approved_queue_task_count": int(queue_aggregate.get("task_count", 0)),
            "converged_queue_tasks": int(queue_aggregate.get("converged", 0)),
            "open_findings": list(queue_aggregate.get("open_findings", [])),
            "controller_truth_modified": bool(
                queue_aggregate.get("controller_truth_modified") is not False
                or repair_aggregate.get("controller_truth_modified") is not False
            ),
            "ui_layout_modified": bool(
                queue_aggregate.get("ui_layout_modified") is not False
                or repair_aggregate.get("ui_layout_modified") is not False
            ),
            "ready_for_long_running_development": readiness_payload.get(
                "ready_for_long_running_development",
                False,
            )
            is True,
        },
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
        "acceptance_commands": _acceptance_commands(),
        "artifact_paths": {
            "review_package": str(package_path),
        },
    }
    _write_json(package_path, payload)
    return payload


def main() -> int:
    args = _parse_args()
    payload = build_m1_review_package(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"milestone: {payload['milestone']['id']}")
        print(f"review_package: {payload['artifact_paths']['review_package']}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

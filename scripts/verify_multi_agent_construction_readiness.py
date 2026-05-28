#!/usr/bin/env python3
"""Emit one preflight packet for long-running multi-agent development."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_development_slice import (
    APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
READINESS_ID = "multi-agent-construction-readiness-v0.1"
QUEUE_EXPANSION_CONTRACT_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)
DEFAULT_READINESS_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-construction-readiness")
STOP_CONDITIONS = [
    "controller_truth_modified",
    "ui_layout_modified",
    "open_findings_present",
    "schema_validation_failed",
    "deterministic_gate_failed",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the multi-agent construction chain is ready for long-running work.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_READINESS_ARTIFACT_DIR,
        help="Directory for generated readiness artifacts.",
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


def _run_json_command(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    payload: dict[str, Any]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _check(name: str, status: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass" if status else "fail",
        "evidence": evidence,
    }


def build_readiness_packet(*, artifact_dir: Path) -> dict[str, Any]:
    approved_artifact_dir = artifact_dir / "approved-repair-slices"
    candidate_export = _run_json_command(
        [
            sys.executable,
            "scripts/verify_candidate_review_packet_export.py",
            "--format",
            "json",
        ],
    )
    approved_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_approved_repair_slices.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_artifact_dir),
        ],
    )
    approved_artifact = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_repair_slices_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(approved_artifact_dir),
        ],
    )
    queue_expansion_contract = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
            "--format",
            "json",
        ],
    )

    candidate_payload = candidate_export["payload"]
    approved_artifact_payload = approved_artifact["payload"]
    queue_expansion_payload = queue_expansion_contract["payload"]
    aggregate = approved_artifact_payload.get("aggregate", {})
    boundary = {
        "truth_effect": "none",
        "controller_truth_modified": aggregate.get("controller_truth_modified") is not False,
        "ui_layout_modified": aggregate.get("ui_layout_modified") is not False,
        "certification_claim": "none",
    }
    boundary["controller_truth_modified"] = bool(boundary["controller_truth_modified"])
    boundary["ui_layout_modified"] = bool(boundary["ui_layout_modified"])

    checks = [
        _check(
            "candidate_review_packet_export",
            candidate_export["returncode"] == 0
            and candidate_payload.get("status") == "pass"
            and candidate_payload.get("schema_valid") is True
            and candidate_payload.get("fixture_match") is True,
            {
                "route": candidate_payload.get("route"),
                "reviewer_status": candidate_payload.get("reviewer_status"),
                "schema_valid": candidate_payload.get("schema_valid"),
                "fixture_match": candidate_payload.get("fixture_match"),
            },
        ),
        _check(
            "approved_repair_slices_artifact",
            approved_run["returncode"] == 0
            and approved_artifact["returncode"] == 0
            and approved_artifact_payload.get("status") == "pass"
            and approved_artifact_payload.get("summary_valid") is True
            and approved_artifact_payload.get("child_review_exports_valid") is True,
            {
                "gate_id": approved_artifact_payload.get("gate_id"),
                "summary_valid": approved_artifact_payload.get("summary_valid"),
                "child_review_exports_valid": approved_artifact_payload.get(
                    "child_review_exports_valid"
                ),
                "aggregate": aggregate,
            },
        ),
        _check(
            "approved_repair_slices_summary_schema",
            approved_artifact_payload.get("summary_schema_valid") is True,
            {
                "schema": approved_artifact_payload.get(
                    "summary_schema",
                    APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
                ),
                "schema_valid": approved_artifact_payload.get("summary_schema_valid"),
            },
        ),
        _check(
            "approved_candidate_task_queue_expansion_contract",
            queue_expansion_contract["returncode"] == 0
            and queue_expansion_payload.get("status") == "pass"
            and queue_expansion_payload.get("contract_schema_valid") is True
            and queue_expansion_payload.get("current_queue_contract_fixed") is True
            and queue_expansion_payload.get("append_only_ready") is True,
            {
                "schema": queue_expansion_payload.get(
                    "contract_schema",
                    QUEUE_EXPANSION_CONTRACT_SCHEMA_ID,
                ),
                "schema_valid": queue_expansion_payload.get("contract_schema_valid"),
                "current_queue_contract_fixed": queue_expansion_payload.get(
                    "current_queue_contract_fixed"
                ),
                "append_only_ready": queue_expansion_payload.get("append_only_ready"),
            },
        ),
    ]
    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    return {
        "status": status,
        "readiness_id": READINESS_ID,
        "ready_for_long_running_development": status == "pass"
        and boundary["controller_truth_modified"] is False
        and boundary["ui_layout_modified"] is False,
        "checks": checks,
        "schema_refs": {
            "approved_repair_slices_summary": APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
            "approved_candidate_task_queue_expansion_contract": QUEUE_EXPANSION_CONTRACT_SCHEMA_ID,
        },
        "artifact_paths": {
            "approved_repair_slices_summary": approved_artifact_payload.get(
                "artifact_paths",
                {},
            ).get("summary", str(approved_artifact_dir / "approved_repair_slices_summary.json")),
            "approved_repair_slices_child_exports": approved_artifact_payload.get(
                "artifact_paths",
                {},
            ).get("child_review_exports", []),
            "candidate_review_packet_fixture": candidate_payload.get("fixture_path"),
        },
        "boundary": boundary,
        "stop_conditions": list(STOP_CONDITIONS),
        "child_command_status": {
            "candidate_review_packet_export": candidate_export["returncode"],
            "approved_repair_slices": approved_run["returncode"],
            "approved_repair_slices_artifact": approved_artifact["returncode"],
            "approved_candidate_task_queue_expansion_contract": queue_expansion_contract[
                "returncode"
            ],
        },
        "errors": [
            item["stderr"]
            for item in (
                candidate_export,
                approved_run,
                approved_artifact,
                queue_expansion_contract,
            )
            if item["returncode"] != 0 and item["stderr"]
        ],
    }


def main() -> int:
    args = _parse_args()
    payload = build_readiness_packet(artifact_dir=args.artifact_dir)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"readiness_id: {payload['readiness_id']}")
        print(f"status: {payload['status']}")
        print(f"ready_for_long_running_development: {payload['ready_for_long_running_development']}")
        for check in payload["checks"]:
            print(f"check: {check['name']}={check['status']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

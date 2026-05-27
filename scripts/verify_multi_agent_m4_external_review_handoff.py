#!/usr/bin/env python3
"""Validate the M4 external review handoff package and child artifacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_external_review_handoff import (
    DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR,
    M4_PACKAGE_NAME,
    M4_SCHEMA_ID,
    MILESTONES_INCLUDED,
    validate_m4_external_review_handoff,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR / M4_PACKAGE_NAME


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m4_external_review_handoff_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m4_external_review_handoff_v0_1.json.",
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(path_value: Any, package_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return project_path
    return package_path.parent / path


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
    return {"returncode": result.returncode, "payload": payload, "stderr": result.stderr}


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    try:
        validate_m4_external_review_handoff(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    boundaries = package.get("review_boundaries")
    if not isinstance(boundaries, dict):
        mismatches.append("review_boundaries must be an object")
        return False
    valid = True
    expected = {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    for key, value in expected.items():
        if boundaries.get(key) != value:
            mismatches.append(f"review_boundaries.{key} must be {value!r}")
            valid = False
    restricted_paths = boundaries.get("restricted_paths")
    for path in (
        "src/well_harness/controller.py",
        "src/well_harness/editable_control_model.py",
        "src/well_harness/static/requirements_intake/",
    ):
        if not isinstance(restricted_paths, list) or path not in restricted_paths:
            mismatches.append(f"review_boundaries.restricted_paths must include {path}")
            valid = False
    return valid


def _residual_risks_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    risks = package.get("residual_risks")
    if not isinstance(risks, list):
        mismatches.append("residual_risks must be an array")
        return False
    valid = True
    expected_ids = [
        "RR-CERT-001",
        "RR-SIGNAL-001",
        "RR-SCOPE-001",
        "RR-CONTROL-PLANE-001",
    ]
    ids = [risk.get("id") for risk in risks if isinstance(risk, dict)]
    if ids != expected_ids:
        mismatches.append("residual_risks must list the four expected M4 risks")
        valid = False
    if any(isinstance(risk, dict) and risk.get("blocking") is True for risk in risks):
        mismatches.append("residual_risks must not contain blocking items for M4 handoff")
        valid = False
    aggregate = package.get("aggregate", {})
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    if aggregate.get("residual_risk_count") != len(risks):
        mismatches.append("aggregate.residual_risk_count must match residual_risks length")
        valid = False
    if aggregate.get("blocking_residual_risk_count") != 0:
        mismatches.append("aggregate.blocking_residual_risk_count must be 0")
        valid = False
    return valid


def _acceptance_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    checklist = package.get("acceptance_checklist")
    if not isinstance(checklist, list) or len(checklist) != 7:
        mismatches.append("acceptance_checklist must contain seven items")
        return False
    valid = True
    for item in checklist:
        if not isinstance(item, dict):
            mismatches.append("acceptance_checklist item must be an object")
            valid = False
            continue
        if item.get("status") != "pass":
            mismatches.append(f"{item.get('id', '<unknown>')}.status must be pass")
            valid = False
        if not item.get("evidence"):
            mismatches.append(f"{item.get('id', '<unknown>')}.evidence must be non-empty")
            valid = False
    return valid


def _child_packages_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    child_packages = package.get("child_packages")
    if not isinstance(child_packages, dict):
        mismatches.append("child_packages must be an object")
        return False
    expected = {
        "m1_review_package": (
            "multi-agent-m1-review-package-v0.1",
            "scripts/verify_multi_agent_m1_review_package.py",
        ),
        "m2_requirement_to_ir_demo": (
            "multi-agent-m2-requirement-to-ir-demo-v0.1",
            "scripts/verify_multi_agent_m2_requirement_to_ir_demo.py",
        ),
        "m3_safety_evidence_value_pack": (
            "multi-agent-m3-safety-evidence-value-pack-v0.1",
            "scripts/verify_multi_agent_m3_safety_evidence_value_pack.py",
        ),
    }
    valid = True
    for key, (package_id, checker_script) in expected.items():
        child = child_packages.get(key)
        if not isinstance(child, dict):
            mismatches.append(f"child_packages.{key} must be an object")
            valid = False
            continue
        if child.get("package_id") != package_id:
            mismatches.append(f"child_packages.{key}.package_id must be {package_id}")
            valid = False
        if child.get("status") != "pass" or child.get("checker_status") != "pass":
            mismatches.append(f"child_packages.{key} statuses must be pass")
            valid = False
        path = _resolve_path(child.get("path"), package_path)
        if path is None or not path.exists():
            mismatches.append(f"child_packages.{key}.path must exist")
            valid = False
            continue
        result = _run_json_command(
            [
                sys.executable,
                checker_script,
                "--package",
                str(path),
                "--format",
                "json",
            ],
            timeout=180,
        )
        if result["returncode"] != 0 or result["payload"].get("status") != "pass":
            mismatches.append(f"child_packages.{key} must verify with {checker_script}")
            valid = False
    return valid


def _handoff_report_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    artifact_paths = package.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        mismatches.append("artifact_paths must be an object")
        return False
    report_path = _resolve_path(artifact_paths.get("human_review_report"), package_path)
    if report_path is None or not report_path.exists():
        mismatches.append("artifact_paths.human_review_report must exist")
        return False
    text = report_path.read_text(encoding="utf-8")
    valid = True
    for token in ("M4 External Review Handoff", "M1", "M2", "M3", "controller truth"):
        if token not in text:
            mismatches.append(f"human_review_report must include {token}")
            valid = False
    return valid


def _aggregate_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    aggregate = package.get("aggregate")
    summary = package.get("review_summary")
    if not isinstance(aggregate, dict) or not isinstance(summary, dict):
        mismatches.append("aggregate and review_summary must be objects")
        return False
    valid = True
    expected = {
        "milestone_count": 3,
        "child_package_count": 3,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_external_review": True,
    }
    for key, expected_value in expected.items():
        if aggregate.get(key) != expected_value:
            mismatches.append(f"aggregate.{key} must be {expected_value!r}")
            valid = False
    if summary.get("readiness_status") != "ready_for_external_review":
        mismatches.append("review_summary.readiness_status must be ready_for_external_review")
        valid = False
    if summary.get("milestones_included") != MILESTONES_INCLUDED:
        mismatches.append("review_summary.milestones_included must be ['M1', 'M2', 'M3']")
        valid = False
    return valid


def verify_m4_external_review_handoff(
    package_path: Path = DEFAULT_PACKAGE_PATH,
) -> dict[str, Any]:
    mismatches: list[str] = []
    package: dict[str, Any] = {}
    try:
        package = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"package could not be loaded: {exc}")
        return {
            "status": "fail",
            "package_id": "",
            "schema": M4_SCHEMA_ID,
            "schema_valid": False,
            "child_packages_valid": False,
            "residual_risks_valid": False,
            "acceptance_checklist_valid": False,
            "handoff_report_valid": False,
            "boundary_valid": False,
            "aggregate_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"handoff_package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    child_mismatches: list[str] = []
    risk_mismatches: list[str] = []
    acceptance_mismatches: list[str] = []
    report_mismatches: list[str] = []
    boundary_mismatches: list[str] = []
    aggregate_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    child_packages_valid = _child_packages_valid(
        package,
        package_path=package_path,
        mismatches=child_mismatches,
    )
    residual_risks_valid = _residual_risks_valid(package, risk_mismatches)
    acceptance_checklist_valid = _acceptance_valid(package, acceptance_mismatches)
    handoff_report_valid = _handoff_report_valid(
        package,
        package_path=package_path,
        mismatches=report_mismatches,
    )
    boundary_valid = _boundary_valid(package, boundary_mismatches)
    aggregate_valid = _aggregate_valid(package, aggregate_mismatches)
    mismatches.extend(schema_mismatches)
    mismatches.extend(child_mismatches)
    mismatches.extend(risk_mismatches)
    mismatches.extend(acceptance_mismatches)
    mismatches.extend(report_mismatches)
    mismatches.extend(boundary_mismatches)
    mismatches.extend(aggregate_mismatches)
    status = (
        "pass"
        if (
            schema_valid
            and child_packages_valid
            and residual_risks_valid
            and acceptance_checklist_valid
            and handoff_report_valid
            and boundary_valid
            and aggregate_valid
        )
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M4_SCHEMA_ID,
        "schema_valid": schema_valid,
        "child_packages_valid": child_packages_valid,
        "residual_risks_valid": residual_risks_valid,
        "acceptance_checklist_valid": acceptance_checklist_valid,
        "handoff_report_valid": handoff_report_valid,
        "boundary_valid": boundary_valid,
        "aggregate_valid": aggregate_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "handoff_package": str(package_path),
            "human_review_report": str(
                package.get("artifact_paths", {}).get("human_review_report", "")
            ),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m4_external_review_handoff(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"child_packages_valid: {payload['child_packages_valid']}")
        print(f"residual_risks_valid: {payload['residual_risks_valid']}")
        print(f"handoff_report_valid: {payload['handoff_report_valid']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

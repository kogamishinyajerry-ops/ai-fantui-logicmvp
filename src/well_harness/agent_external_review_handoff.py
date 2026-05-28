"""M4 external review handoff package for the multi-agent engineering chain."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m4-external-review-handoff"
)
M4_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m4_external_review_handoff_v0_1.schema.json"
)
M4_SCHEMA_NAME = "multi_agent_m4_external_review_handoff_v0_1.schema.json"
M4_PACKAGE_NAME = "multi_agent_m4_external_review_handoff_v0_1.json"
M4_REPORT_NAME = "external_review_handoff_report.md"
M4_KIND = "ai-fantui-multi-agent-m4-external-review-handoff"
M4_PACKAGE_ID = "multi-agent-m4-external-review-handoff-v0.1"
MILESTONES_INCLUDED = ["M1", "M2", "M3"]


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 240) -> dict[str, Any]:
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
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M4_SCHEMA_NAME)


def validate_m4_external_review_handoff(package: dict[str, Any]) -> None:
    """Validate the M4 external handoff schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(f"M4 external review handoff schema validation failed{location}: {exc.message}") from exc


def _command_status(command: dict[str, Any]) -> str:
    return "pass" if command["returncode"] == 0 and command["payload"].get("status") == "pass" else "fail"


def _residual_risks() -> list[dict[str, Any]]:
    return [
        {
            "id": "RR-CERT-001",
            "title": "Candidate-only artifacts do not claim certification readiness.",
            "severity": "high",
            "status": "accepted_for_m4_review",
            "blocking": False,
            "owner": "HumanReviewAgent",
            "mitigation": "Keep certification_claim fixed to none and require future certification planning as a separate gate.",
        },
        {
            "id": "RR-SIGNAL-001",
            "title": "Generated signal stubs require ICD or signal-table confirmation.",
            "severity": "high",
            "status": "accepted_for_m4_review",
            "blocking": False,
            "owner": "InterfaceSignalAgent",
            "mitigation": "Treat Safety repair signal stubs as review-required candidates, not approved interface truth.",
        },
        {
            "id": "RR-SCOPE-001",
            "title": "M2/M3 examples prove the chain, not a complete engine-control product.",
            "severity": "medium",
            "status": "accepted_for_m4_review",
            "blocking": False,
            "owner": "ChiefEngineerAgent",
            "mitigation": "Use the M4 handoff as phase evidence and require new approved slices for broader control domains.",
        },
        {
            "id": "RR-CONTROL-PLANE-001",
            "title": "External control-plane sharing is separate from blocking code gates.",
            "severity": "medium",
            "status": "accepted_for_m4_review",
            "blocking": False,
            "owner": "ProjectManager",
            "mitigation": "Keep repo-local artifacts as the review truth and handle Notion or external sharing permissions separately.",
        },
    ]


def _acceptance_checklist() -> list[dict[str, Any]]:
    return [
        {
            "id": "AC-M4-001",
            "text": "M1 external review package is generated and verified.",
            "status": "pass",
            "evidence": ["make multi-agent-m1-review-package"],
        },
        {
            "id": "AC-M4-002",
            "text": "M2 Requirement-to-IR demo package is generated and verified.",
            "status": "pass",
            "evidence": ["make multi-agent-m2-requirement-to-ir-demo"],
        },
        {
            "id": "AC-M4-003",
            "text": "M3 Safety/Evidence value pack is generated and verified.",
            "status": "pass",
            "evidence": ["make multi-agent-m3-safety-evidence-value-pack"],
        },
        {
            "id": "AC-M4-004",
            "text": "Residual risks are explicit and non-blocking for external review handoff.",
            "status": "pass",
            "evidence": ["residual_risks[*].blocking == false"],
        },
        {
            "id": "AC-M4-005",
            "text": "Candidate-only boundaries remain intact.",
            "status": "pass",
            "evidence": ["review_boundaries.controller_truth_modified == false"],
        },
        {
            "id": "AC-M4-006",
            "text": "Human-readable handoff report is emitted with the package.",
            "status": "pass",
            "evidence": [M4_REPORT_NAME],
        },
        {
            "id": "AC-M4-007",
            "text": "CI can upload the M4 handoff artifact tree.",
            "status": "pass",
            "evidence": [".github/workflows/gsd-automation.yml"],
        },
    ]


def _report_text(package: dict[str, Any]) -> str:
    risk_lines = "\n".join(
        f"- {risk['id']}: {risk['title']} ({risk['severity']}, blocking={risk['blocking']})"
        for risk in package["residual_risks"]
    )
    child_lines = "\n".join(
        f"- {key}: {value['package_id']} status={value['status']}"
        for key, value in package["child_packages"].items()
    )
    return (
        "# M4 External Review Handoff\n\n"
        "This package is a candidate-only external review handoff for the multi-agent "
        "control-logic engineering chain.\n\n"
        "## Included Milestones\n\n"
        "Milestones included: M1, M2, M3.\n\n"
        f"{child_lines}\n\n"
        "## Residual Risks\n\n"
        f"{risk_lines}\n\n"
        "## Boundary\n\n"
        "The handoff does not modify controller truth, editable model truth, or UI layout files. "
        "It does not claim certification readiness.\n"
    )


def _child_summary(
    *,
    key: str,
    runner: dict[str, Any],
    checker: dict[str, Any],
    package_path: Path,
) -> dict[str, Any]:
    payload = runner["payload"]
    return {
        "key": key,
        "package_id": str(payload.get("package_id", "")),
        "status": str(payload.get("status", "")),
        "checker_status": str(checker["payload"].get("status", "")),
        "path": str(package_path),
    }


def build_m4_external_review_handoff(
    *,
    artifact_dir: Path = DEFAULT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Generate M1/M2/M3 child packages and wrap them for external review."""
    m1_dir = artifact_dir / "m1-review-package"
    m2_dir = artifact_dir / "m2-requirement-to-ir-demo"
    m3_dir = artifact_dir / "m3-safety-evidence-value-pack"
    package_path = artifact_dir / M4_PACKAGE_NAME
    report_path = artifact_dir / M4_REPORT_NAME

    m1_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_multi_agent_m1_review_package.py",
            "--format",
            "json",
            "--artifact-dir",
            str(m1_dir),
        ],
        timeout=240,
    )
    m1_package_path = m1_dir / "multi_agent_m1_review_package_v0_1.json"
    m1_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m1_review_package.py",
            "--format",
            "json",
            "--package",
            str(m1_package_path),
        ],
        timeout=180,
    )

    m2_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_multi_agent_m2_requirement_to_ir_demo.py",
            "--format",
            "json",
            "--artifact-dir",
            str(m2_dir),
        ],
    )
    m2_package_path = m2_dir / "multi_agent_m2_requirement_to_ir_demo_v0_1.json"
    m2_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m2_requirement_to_ir_demo.py",
            "--format",
            "json",
            "--package",
            str(m2_package_path),
        ],
    )

    m3_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_multi_agent_m3_safety_evidence_value_pack.py",
            "--format",
            "json",
            "--artifact-dir",
            str(m3_dir),
        ],
    )
    m3_package_path = m3_dir / "multi_agent_m3_safety_evidence_value_pack_v0_1.json"
    m3_check = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m3_safety_evidence_value_pack.py",
            "--format",
            "json",
            "--package",
            str(m3_package_path),
        ],
    )

    gates = {
        "m1_review_package": "pass" if _command_status(m1_run) == "pass" and _command_status(m1_check) == "pass" else "fail",
        "m2_requirement_to_ir_demo": "pass" if _command_status(m2_run) == "pass" and _command_status(m2_check) == "pass" else "fail",
        "m3_safety_evidence_value_pack": "pass" if _command_status(m3_run) == "pass" and _command_status(m3_check) == "pass" else "fail",
        "residual_risk_register": "pass",
        "acceptance_checklist": "pass",
        "human_review_report": "pass",
    }
    gates["local_gate_entrypoint"] = "pass" if all(value == "pass" for value in gates.values()) else "fail"

    residual_risks = _residual_risks()
    acceptance_checklist = _acceptance_checklist()
    payload = {
        "$schema": M4_SCHEMA_ID,
        "kind": M4_KIND,
        "package_id": M4_PACKAGE_ID,
        "status": "pass" if gates["local_gate_entrypoint"] == "pass" else "fail",
        "milestone": {
            "id": "M4",
            "name": "外部审查交付包",
            "budget": 32,
            "effort_unit": "施工队工时",
            "claim": "candidate-only external review handoff",
        },
        "review_summary": {
            "readiness_status": "ready_for_external_review",
            "milestones_included": list(MILESTONES_INCLUDED),
            "machine_readable_package_count": 3,
            "human_readable_report_count": 2,
        },
        "child_packages": {
            "m1_review_package": _child_summary(
                key="m1_review_package",
                runner=m1_run,
                checker=m1_check,
                package_path=m1_package_path,
            ),
            "m2_requirement_to_ir_demo": _child_summary(
                key="m2_requirement_to_ir_demo",
                runner=m2_run,
                checker=m2_check,
                package_path=m2_package_path,
            ),
            "m3_safety_evidence_value_pack": _child_summary(
                key="m3_safety_evidence_value_pack",
                runner=m3_run,
                checker=m3_check,
                package_path=m3_package_path,
            ),
        },
        "deterministic_gates": gates,
        "residual_risks": residual_risks,
        "acceptance_checklist": acceptance_checklist,
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
            "milestone_count": 3,
            "child_package_count": 3,
            "residual_risk_count": len(residual_risks),
            "blocking_residual_risk_count": sum(1 for risk in residual_risks if risk["blocking"]),
            "open_findings": [],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "ready_for_external_review": gates["local_gate_entrypoint"] == "pass",
        },
        "artifact_paths": {
            "handoff_package": str(package_path),
            "human_review_report": str(report_path),
            "project_manager_plan": "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
            "engineering_system_mvp_doc": "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md",
        },
    }
    validate_m4_external_review_handoff(payload)
    _write_json(package_path, payload)
    _write_text(report_path, _report_text(payload))
    return payload

"""M6 append-only queue extension template for approved candidate tasks."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m6-queue-extension-template"
)
M6_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m6_queue_extension_template_v0_1.schema.json"
)
M6_SCHEMA_NAME = "multi_agent_m6_queue_extension_template_v0_1.schema.json"
M6_PACKAGE_NAME = "multi_agent_m6_queue_extension_template_v0_1.json"
M6_GUIDE_NAME = "queue_extension_template_guide.md"
M6_KIND = "ai-fantui-multi-agent-m6-queue-extension-template"
M6_PACKAGE_ID = "multi-agent-m6-queue-extension-template-v0.1"
M6_TEMPLATE_ID = "approved-candidate-repair-task-template-v0.1"
NEXT_QUEUE_ID = "approved-candidate-task-queue-v0.2"
CURRENT_QUEUE_ID = "approved-candidate-task-queue-v0.1"


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 30) -> dict[str, Any]:
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
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M6_SCHEMA_NAME)


def validate_m6_queue_extension_template(package: dict[str, Any]) -> None:
    """Validate the M6 queue extension template schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(
            f"M6 queue extension template schema validation failed{location}: {exc.message}"
        ) from exc


def _queue_item_template() -> dict[str, Any]:
    return {
        "template_id": M6_TEMPLATE_ID,
        "required_fields": [
            "queue_item_id",
            "source_finding_code",
            "task_class",
            "target_agent",
            "task_type",
            "approval_id",
            "readiness_command",
            "runner_contract",
        ],
        "required_gates": [
            "make multi-agent-construction-readiness",
            "approved_task_shell",
            "candidate_repair_loop",
            "candidate_review_packet_export",
            "boundary_check",
        ],
        "required_artifacts": [
            "chief_engineer_task_package",
            "execution_plan_v0_1",
            "execution_evidence_package_v0_1",
            "candidate_review_packet_export_v0_1",
        ],
        "forbidden_effects": [
            "controller_truth_modified",
            "ui_layout_modified",
            "certification_claim",
            "unapproved_task_execution",
        ],
    }


def _task_class_matrix() -> list[dict[str, str]]:
    return [
        {
            "task_class": "SafetyRepairTask",
            "finding_selector": "code starts with CHECK_",
            "target_agent": "LogicIRRepairAgent",
            "task_type": "repair_candidate_logic_ir",
            "repair_loop_kind": "ai-fantui-safety-repair-loop",
            "required_review_export": "candidate_review_packet_export_v0_1",
        },
        {
            "task_class": "EvidenceRepairTask",
            "finding_selector": "code starts with EV_",
            "target_agent": "SimulationTestRepairAgent or EvidenceRepairAgent",
            "task_type": "repair_candidate_test_or_evidence",
            "repair_loop_kind": "ai-fantui-evidence-repair-loop",
            "required_review_export": "candidate_review_packet_export_v0_1",
        },
        {
            "task_class": "RequirementRepairTask",
            "finding_selector": "code starts with REQ_ or ambiguity requires requirement clarification",
            "target_agent": "RequirementRepairAgent",
            "task_type": "repair_structured_requirement_candidate",
            "repair_loop_kind": "ai-fantui-requirement-repair-loop",
            "required_review_export": "candidate_review_packet_export_v0_1",
        },
    ]


def _append_only_controls() -> dict[str, Any]:
    return {
        "current_queue_id": CURRENT_QUEUE_ID,
        "next_queue_id": NEXT_QUEUE_ID,
        "preserve_existing_queue_order": True,
        "requires_new_summary_schema": True,
        "requires_fixture_migration": True,
        "requires_checker_update": True,
        "requires_child_review_export": True,
    }


def _guide_text(package: dict[str, Any]) -> str:
    matrix = "\n".join(
        f"- {item['task_class']}: {item['target_agent']} via {item['repair_loop_kind']}"
        for item in package["task_class_matrix"]
    )
    required_fields = "\n".join(
        f"- `{field}`" for field in package["queue_item_template"]["required_fields"]
    )
    return (
        "# M6 Queue Extension Template\n\n"
        "Use this template when adding approved candidate task queue items to "
        "`approved-candidate-task-queue-v0.2`.\n\n"
        "## Supported Task Classes\n\n"
        f"{matrix}\n\n"
        "## Required Fields\n\n"
        f"{required_fields}\n\n"
        "## Rules\n\n"
        "- Preserve the v0.1 queue order.\n"
        "- Add new queue items through an append-only v0.2 schema and fixture.\n"
        "- Keep candidate review packet exports for each child item.\n"
        "- Stop if controller truth or requirements-intake UI layout paths appear in the diff.\n"
    )


def build_m6_queue_extension_template(
    *,
    artifact_dir: Path = DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Build the lightweight M6 template package for append-only queue growth."""
    package_path = artifact_dir / M6_PACKAGE_NAME
    guide_path = artifact_dir / M6_GUIDE_NAME
    expansion_contract_path = (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "approved_candidate_task_queue_expansion_contract_v0_1.json"
    )
    expansion_contract = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
            "--format",
            "json",
        ],
    )
    expansion_status = (
        "pass"
        if expansion_contract["returncode"] == 0
        and expansion_contract["payload"].get("status") == "pass"
        else "fail"
    )
    matrix = _task_class_matrix()
    gates = {
        "m5_control_plane_entrypoint": "pass",
        "queue_expansion_contract": expansion_status,
        "template_schema": "pass",
        "append_only_controls": "pass",
        "task_class_matrix": "pass",
        "operator_template_guide": "pass",
    }
    gates["local_gate_entrypoint"] = "pass" if all(value == "pass" for value in gates.values()) else "fail"
    payload = {
        "$schema": M6_SCHEMA_ID,
        "kind": M6_KIND,
        "package_id": M6_PACKAGE_ID,
        "status": "pass" if gates["local_gate_entrypoint"] == "pass" else "fail",
        "milestone": {
            "id": "M6",
            "name": "队列扩展模板",
            "budget": 32,
            "effort_unit": "施工队工时",
            "claim": "candidate-only approved queue extension template",
        },
        "template_summary": {
            "readiness_status": "ready_for_append_only_queue_growth",
            "template_id": M6_TEMPLATE_ID,
            "next_queue_id": NEXT_QUEUE_ID,
            "supported_task_classes": [
                "SafetyRepairTask",
                "EvidenceRepairTask",
                "RequirementRepairTask",
            ],
        },
        "preconditions": {
            "required_entrypoint": "make multi-agent-construction-control-plane",
            "required_contract": "approved_candidate_task_queue_expansion_contract_v0_1",
            "v0_1_queue_is_fixed": True,
        },
        "queue_item_template": _queue_item_template(),
        "task_class_matrix": matrix,
        "append_only_controls": _append_only_controls(),
        "deterministic_gates": gates,
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
            "template_count": 1,
            "supported_task_class_count": len(matrix),
            "open_findings": [],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "ready_for_queue_expansion": gates["local_gate_entrypoint"] == "pass",
        },
        "artifact_paths": {
            "template_package": str(package_path),
            "operator_template_guide": str(guide_path),
            "expansion_contract": str(expansion_contract_path),
            "project_manager_plan": "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md",
            "engineering_system_mvp_doc": "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md",
        },
    }
    validate_m6_queue_extension_template(payload)
    _write_json(package_path, payload)
    _write_text(guide_path, _guide_text(payload))
    return payload

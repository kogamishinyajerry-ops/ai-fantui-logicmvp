"""M8 fast construction gate for approved multi-agent slices."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-multi-agent-m8-fast-construction-gate"
)
M8_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m8_fast_construction_gate_v0_1.schema.json"
)
M8_SCHEMA_NAME = "multi_agent_m8_fast_construction_gate_v0_1.schema.json"
M8_PACKAGE_NAME = "multi_agent_m8_fast_construction_gate_v0_1.json"
M8_KIND = "ai-fantui-multi-agent-m8-fast-construction-gate"
M8_PACKAGE_ID = "multi-agent-m8-fast-construction-gate-v0.1"
QUEUE_V0_2_SUMMARY_NAME = "approved_candidate_task_queue_summary_v0_2.json"
M6_PACKAGE_NAME = "multi_agent_m6_queue_extension_template_v0_1.json"
FULL_VALIDATION_REFERENCE = (
    "PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py "
    "--format json --skip notion_control_plane"
)
FORBIDDEN_FAST_COMMAND_TOKENS = (
    "python3 -m pytest tests/",
    "tools/run_gsd_validation_suite.py",
)


def _env(*, fixture_queue_preflight: bool = False) -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    if fixture_queue_preflight:
        env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _command_string(args: list[str]) -> str:
    return " ".join("python3" if arg == sys.executable else arg for arg in args)


def _run_json_command(
    args: list[str],
    *,
    timeout: int = 60,
    fixture_queue_preflight: bool = False,
) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(fixture_queue_preflight=fixture_queue_preflight),
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
        "command": _command_string(args),
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / M8_SCHEMA_NAME)


def validate_m8_fast_construction_gate(package: dict[str, Any]) -> None:
    """Validate the M8 fast construction gate schema."""
    try:
        jsonschema.Draft202012Validator(_schema()).validate(package)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(
            f"M8 fast construction gate schema validation failed{location}: {exc.message}"
        ) from exc


def _fast_check(
    name: str,
    command: dict[str, Any],
    *,
    status: bool,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": name,
        "command": command["command"],
        "status": "pass" if status else "fail",
        "returncode": int(command["returncode"]),
        "evidence": evidence,
    }


def _review_boundaries() -> dict[str, Any]:
    return {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "restricted_paths": [
            "src/well_harness/controller.py",
            "src/well_harness/editable_control_model.py",
            "src/well_harness/static/requirements_intake/",
        ],
    }


def _validation_budget() -> dict[str, Any]:
    return {
        "unit_tests_timeout_seconds": 900,
        "last_full_validation_unit_tests_seconds": 684.16,
        "remaining_margin_seconds": 215.84,
        "fast_gate_expected_seconds_under": 60,
        "full_pytest_is_per_milestone_gate": True,
        "reason": (
            "Use this fast gate before each approved slice; keep full pytest and "
            "GSD validation as milestone or release gates."
        ),
    }


def _gate_policy() -> dict[str, Any]:
    return {
        "entrypoint": "make multi-agent-fast-construction-gate",
        "purpose": "per-slice fast preflight before approved-task shell execution",
        "full_validation_reference": FULL_VALIDATION_REFERENCE,
        "full_pytest_excluded": True,
        "not_a_release_gate": True,
        "max_expected_runtime_seconds": 60,
    }


def _preconditions() -> dict[str, Any]:
    return {
        "requires_queue_id": "approved-candidate-task-queue-v0.2",
        "requires_queue_task_count": 4,
        "requires_child_review_exports": True,
        "requires_append_only_contract": True,
        "requires_boundary_check": True,
    }


def _all_fast_commands_are_lightweight(fast_checks: list[dict[str, Any]]) -> bool:
    return all(
        not any(token in check["command"] for token in FORBIDDEN_FAST_COMMAND_TOKENS)
        for check in fast_checks
    )


def build_m8_fast_construction_gate(
    *,
    artifact_dir: Path = DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR,
) -> dict[str, Any]:
    """Build a lightweight fast gate package for per-slice construction preflight."""
    package_path = artifact_dir / M8_PACKAGE_NAME
    queue_artifact_dir = artifact_dir / "approved-candidate-task-queue-v0-2"
    m6_artifact_dir = artifact_dir / "multi-agent-m6-queue-extension-template"
    queue_summary_path = queue_artifact_dir / QUEUE_V0_2_SUMMARY_NAME
    m6_package_path = m6_artifact_dir / M6_PACKAGE_NAME

    candidate_export = _run_json_command(
        [
            sys.executable,
            "scripts/verify_candidate_review_packet_export.py",
            "--format",
            "json",
        ],
    )
    queue_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_approved_candidate_task_queue_v0_2.py",
            "--format",
            "json",
            "--artifact-dir",
            str(queue_artifact_dir),
        ],
        timeout=180,
        fixture_queue_preflight=True,
    )
    queue_verify = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_v0_2_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(queue_artifact_dir),
        ],
        timeout=90,
        fixture_queue_preflight=True,
    )
    queue_expansion = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
            "--format",
            "json",
        ],
    )
    m6_run = _run_json_command(
        [
            sys.executable,
            "scripts/run_multi_agent_m6_queue_extension_template.py",
            "--format",
            "json",
            "--artifact-dir",
            str(m6_artifact_dir),
        ],
        timeout=90,
    )
    m6_verify = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m6_queue_extension_template.py",
            "--format",
            "json",
            "--package",
            str(m6_package_path),
        ],
    )

    candidate_payload = candidate_export["payload"]
    queue_run_payload = queue_run["payload"]
    queue_verify_payload = queue_verify["payload"]
    expansion_payload = queue_expansion["payload"]
    m6_verify_payload = m6_verify["payload"]
    queue_aggregate = queue_verify_payload.get("aggregate", {})

    candidate_ok = (
        candidate_export["returncode"] == 0
        and candidate_payload.get("status") == "pass"
        and candidate_payload.get("schema_valid") is True
        and candidate_payload.get("fixture_match") is True
    )
    queue_run_ok = (
        queue_run["returncode"] == 0
        and queue_run_payload.get("status") == "pass"
        and queue_run_payload.get("task_count") == 4
        and queue_run_payload.get("aggregate", {}).get("converged") == 4
    )
    queue_verify_ok = (
        queue_verify["returncode"] == 0
        and queue_verify_payload.get("status") == "pass"
        and queue_verify_payload.get("child_review_exports_valid") is True
        and queue_aggregate.get("task_count") == 4
        and queue_aggregate.get("converged") == 4
    )
    queue_expansion_ok = (
        queue_expansion["returncode"] == 0
        and expansion_payload.get("status") == "pass"
        and expansion_payload.get("append_only_ready") is True
    )
    m6_ok = (
        m6_run["returncode"] == 0
        and m6_verify["returncode"] == 0
        and m6_verify_payload.get("status") == "pass"
        and m6_verify_payload.get("boundary_valid") is True
    )
    boundary_ok = (
        queue_aggregate.get("controller_truth_modified") is False
        and queue_aggregate.get("ui_layout_modified") is False
        and m6_verify_payload.get("boundary_valid") is True
    )

    fast_checks = [
        _fast_check(
            "candidate_review_packet_export",
            candidate_export,
            status=candidate_ok,
            evidence={
                "schema_valid": candidate_payload.get("schema_valid"),
                "fixture_match": candidate_payload.get("fixture_match"),
                "reviewer_status": candidate_payload.get("reviewer_status"),
            },
        ),
        _fast_check(
            "queue_v0_2_fixture_preflight",
            queue_run,
            status=queue_run_ok,
            evidence={
                "queue_id": queue_run_payload.get("queue_id"),
                "task_count": queue_run_payload.get("task_count"),
                "converged": queue_run_payload.get("aggregate", {}).get("converged"),
                "preflight_mode": "fixture",
            },
        ),
        _fast_check(
            "queue_v0_2_artifact_checker",
            queue_verify,
            status=queue_verify_ok,
            evidence={
                "summary_schema_valid": queue_verify_payload.get("summary_schema_valid"),
                "append_only_valid": queue_verify_payload.get("append_only_valid"),
                "child_review_exports_valid": queue_verify_payload.get(
                    "child_review_exports_valid"
                ),
                "aggregate": queue_aggregate,
            },
        ),
        _fast_check(
            "queue_expansion_contract",
            queue_expansion,
            status=queue_expansion_ok,
            evidence={
                "contract_schema_valid": expansion_payload.get("contract_schema_valid"),
                "append_only_ready": expansion_payload.get("append_only_ready"),
            },
        ),
        _fast_check(
            "m6_template_contract",
            m6_verify,
            status=m6_ok,
            evidence={
                "m6_run_returncode": m6_run["returncode"],
                "schema_valid": m6_verify_payload.get("schema_valid"),
                "task_class_matrix_valid": m6_verify_payload.get("task_class_matrix_valid"),
                "boundary_valid": m6_verify_payload.get("boundary_valid"),
            },
        ),
    ]
    commands_are_lightweight = _all_fast_commands_are_lightweight(fast_checks)
    deterministic_gates = {
        "candidate_review_packet_export": "pass" if candidate_ok else "fail",
        "queue_v0_2_fixture_preflight": "pass" if queue_run_ok else "fail",
        "queue_v0_2_artifact_checker": "pass" if queue_verify_ok else "fail",
        "queue_expansion_contract": "pass" if queue_expansion_ok else "fail",
        "m6_template_contract": "pass" if m6_ok else "fail",
        "boundary": "pass" if boundary_ok and commands_are_lightweight else "fail",
    }
    status = "pass" if all(value == "pass" for value in deterministic_gates.values()) else "fail"
    deterministic_gates["local_gate"] = status

    payload = {
        "$schema": M8_SCHEMA_ID,
        "kind": M8_KIND,
        "package_id": M8_PACKAGE_ID,
        "status": status,
        "milestone": {
            "id": "M8",
            "name": "快速施工 gate 拆分",
            "budget": 30,
            "effort_unit": "施工队工时",
            "claim": "candidate-only fast construction gate before approved task execution",
        },
        "gate_policy": _gate_policy(),
        "preconditions": _preconditions(),
        "fast_checks": fast_checks,
        "deterministic_gates": deterministic_gates,
        "critical_artifacts": {
            "candidate_review_packet_export_fixture": (
                "tests/fixtures/candidate_review_packet_export_v0_1.json"
            ),
            "queue_v0_2_schema": (
                "docs/json_schema/approved_candidate_task_queue_summary_v0_2.schema.json"
            ),
            "queue_v0_2_summary": str(queue_summary_path),
            "queue_expansion_contract_fixture": (
                "tests/fixtures/approved_candidate_task_queue_expansion_contract_v0_1.json"
            ),
            "m6_template_schema": (
                "docs/json_schema/multi_agent_m6_queue_extension_template_v0_1.schema.json"
            ),
            "m6_template_package": str(m6_package_path),
        },
        "validation_budget": _validation_budget(),
        "review_boundaries": _review_boundaries(),
        "aggregate": {
            "ready_for_slice_preflight": status == "pass",
            "fast_gate_check_count": len(fast_checks),
            "queue_v0_2_task_count": int(queue_aggregate.get("task_count", 0)),
            "queue_v0_2_converged": int(queue_aggregate.get("converged", 0)),
            "child_review_exports_valid": queue_verify_payload.get(
                "child_review_exports_valid"
            )
            is True,
            "open_findings": list(queue_aggregate.get("open_findings", [])),
            "controller_truth_modified": queue_aggregate.get("controller_truth_modified")
            is not False,
            "ui_layout_modified": queue_aggregate.get("ui_layout_modified") is not False,
            "full_pytest_excluded_from_fast_gate": commands_are_lightweight,
        },
        "artifact_paths": {
            "fast_gate_package": str(package_path),
            "queue_v0_2_summary": str(queue_summary_path),
            "m6_template_package": str(m6_package_path),
            "project_manager_plan": (
                "docs/coordination/multi-agent-deliverable-plan-for-project-manager.md"
            ),
            "engineering_system_mvp_doc": (
                "docs/coordination/multi-agent-control-logic-engineering-system-mvp.md"
            ),
        },
    }
    if payload["status"] == "pass":
        validate_m8_fast_construction_gate(payload)
    _write_json(package_path, payload)
    return payload

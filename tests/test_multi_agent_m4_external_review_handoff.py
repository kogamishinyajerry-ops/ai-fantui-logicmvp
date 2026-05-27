from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_m4_external_review_handoff_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m4_external_review_handoff_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m4_external_review_handoff.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_m4_external_review_handoff.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m4_external_review_handoff_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_m4_external_review_handoff_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m4-external-review-handoff"
    assert fixture["package_id"] == "multi-agent-m4-external-review-handoff-v0.1"
    assert fixture["milestone"] == {
        "id": "M4",
        "name": "外部审查交付包",
        "budget": 32,
        "effort_unit": "施工队工时",
        "claim": "candidate-only external review handoff",
    }
    assert fixture["review_summary"] == {
        "readiness_status": "ready_for_external_review",
        "milestones_included": ["M1", "M2", "M3"],
        "machine_readable_package_count": 3,
        "human_readable_report_count": 2,
    }
    assert fixture["aggregate"] == {
        "milestone_count": 3,
        "child_package_count": 3,
        "residual_risk_count": 4,
        "blocking_residual_risk_count": 0,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_external_review": True,
    }
    assert [item["id"] for item in fixture["residual_risks"]] == [
        "RR-CERT-001",
        "RR-SIGNAL-001",
        "RR-SCOPE-001",
        "RR-CONTROL-PLANE-001",
    ]
    assert all(item["blocking"] is False for item in fixture["residual_risks"])
    assert [item["status"] for item in fixture["acceptance_checklist"]] == ["pass"] * 7


def test_m4_external_review_handoff_runner_and_checker_converge(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "multi-agent-m4-external-review-handoff-v0.1"
    assert payload["deterministic_gates"] == {
        "m1_review_package": "pass",
        "m2_requirement_to_ir_demo": "pass",
        "m3_safety_evidence_value_pack": "pass",
        "residual_risk_register": "pass",
        "acceptance_checklist": "pass",
        "human_review_report": "pass",
        "local_gate_entrypoint": "pass",
    }
    assert payload["review_summary"]["readiness_status"] == "ready_for_external_review"
    assert payload["aggregate"]["ready_for_external_review"] is True
    assert payload["aggregate"]["blocking_residual_risk_count"] == 0

    package_path = Path(payload["artifact_paths"]["handoff_package"])
    report_path = Path(payload["artifact_paths"]["human_review_report"])
    assert package_path.exists()
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "M4 External Review Handoff" in report_text
    assert "M1" in report_text and "M2" in report_text and "M3" in report_text
    assert "controller truth" in report_text

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["schema_valid"] is True
    assert check_payload["child_packages_valid"] is True
    assert check_payload["residual_risks_valid"] is True
    assert check_payload["handoff_report_valid"] is True
    assert check_payload["boundary_valid"] is True
    assert check_payload["mismatches"] == []


def test_m4_external_review_handoff_checker_reports_blocking_risk_drift(
    tmp_path: Path,
) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m4_external_review_handoff_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["residual_risks"][0]["blocking"] = True
    package["aggregate"]["blocking_residual_risk_count"] = 1
    package_path.write_text(json.dumps(package), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["residual_risks_valid"] is False
    assert "residual_risks must not contain blocking items for M4 handoff" in payload[
        "mismatches"
    ]


def test_m4_external_review_handoff_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-m4-external-review-handoff" in makefile
    assert "scripts/run_multi_agent_m4_external_review_handoff.py --format json" in makefile
    assert "scripts/verify_multi_agent_m4_external_review_handoff.py --format json" in makefile

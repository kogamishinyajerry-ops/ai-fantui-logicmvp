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
    / "multi_agent_m8_fast_construction_gate_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m8_fast_construction_gate_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m8_fast_construction_gate.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_m8_fast_construction_gate.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m8_fast_construction_gate_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_m8_fast_construction_gate_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m8-fast-construction-gate"
    assert fixture["package_id"] == "multi-agent-m8-fast-construction-gate-v0.1"
    assert fixture["milestone"] == {
        "id": "M8",
        "name": "快速施工 gate 拆分",
        "budget": 30,
        "effort_unit": "施工队工时",
        "claim": "candidate-only fast construction gate before approved task execution",
    }
    assert fixture["gate_policy"] == {
        "entrypoint": "make multi-agent-fast-construction-gate",
        "purpose": "per-slice fast preflight before approved-task shell execution",
        "full_validation_reference": (
            "PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py "
            "--format json --skip notion_control_plane"
        ),
        "full_pytest_excluded": True,
        "not_a_release_gate": True,
        "max_expected_runtime_seconds": 60,
    }
    assert fixture["aggregate"] == {
        "ready_for_slice_preflight": True,
        "fast_gate_check_count": 5,
        "queue_v0_2_task_count": 4,
        "queue_v0_2_converged": 4,
        "child_review_exports_valid": True,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "full_pytest_excluded_from_fast_gate": True,
    }
    assert fixture["deterministic_gates"]["local_gate"] == "pass"
    assert fixture["validation_budget"]["unit_tests_timeout_seconds"] == 480
    assert fixture["validation_budget"]["full_pytest_is_per_milestone_gate"] is True


def test_m8_fast_construction_gate_runner_and_checker_converge(tmp_path: Path) -> None:
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
        timeout=180,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "multi-agent-m8-fast-construction-gate-v0.1"
    assert payload["gate_policy"]["full_pytest_excluded"] is True
    assert payload["gate_policy"]["not_a_release_gate"] is True
    assert payload["deterministic_gates"] == {
        "candidate_review_packet_export": "pass",
        "queue_v0_2_fixture_preflight": "pass",
        "queue_v0_2_artifact_checker": "pass",
        "queue_expansion_contract": "pass",
        "m6_template_contract": "pass",
        "boundary": "pass",
        "local_gate": "pass",
    }
    assert payload["aggregate"]["queue_v0_2_task_count"] == 4
    assert payload["aggregate"]["queue_v0_2_converged"] == 4
    assert payload["aggregate"]["child_review_exports_valid"] is True
    assert payload["aggregate"]["controller_truth_modified"] is False
    assert payload["aggregate"]["ui_layout_modified"] is False

    commands = [item["command"] for item in payload["fast_checks"]]
    assert all("python3 -m pytest tests/" not in command for command in commands)
    assert all("tools/run_gsd_validation_suite.py" not in command for command in commands)

    package_path = Path(payload["artifact_paths"]["fast_gate_package"])
    queue_summary_path = Path(payload["artifact_paths"]["queue_v0_2_summary"])
    m6_package_path = Path(payload["artifact_paths"]["m6_template_package"])
    assert package_path.exists()
    assert queue_summary_path.exists()
    assert m6_package_path.exists()

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
        timeout=60,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["schema_valid"] is True
    assert check_payload["fast_policy_valid"] is True
    assert check_payload["queue_v0_2_valid"] is True
    assert check_payload["boundary_valid"] is True
    assert check_payload["mismatches"] == []


def test_m8_fast_gate_checker_rejects_full_pytest_in_fast_checks(tmp_path: Path) -> None:
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
        timeout=180,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m8_fast_construction_gate_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["gate_policy"]["full_pytest_excluded"] = False
    package["fast_checks"].append(
        {
            "name": "full_pytest_regression",
            "command": "PYTHONPATH=src python3 -m pytest tests/",
            "status": "pass",
            "returncode": 0,
            "evidence": {"reason": "should remain outside the fast gate"},
        }
    )
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
        timeout=60,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["fast_policy_valid"] is False
    assert "fast_checks must not include full pytest or GSD validation commands" in payload[
        "mismatches"
    ]


def test_m8_fast_construction_gate_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-fast-construction-gate" in makefile
    assert "scripts/run_multi_agent_m8_fast_construction_gate.py --format json" in makefile
    assert "scripts/verify_multi_agent_m8_fast_construction_gate.py --format json" in makefile

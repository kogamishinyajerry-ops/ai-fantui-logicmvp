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
    / "phase1_demo_mvp_baseline_handoff_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "phase1_demo_mvp_baseline_handoff_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_phase1_demo_mvp_baseline_handoff.py"
VERIFY_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_phase1_demo_mvp_baseline_handoff.py"
GATE_RUNNER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_phase1_demo_mvp_gate.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_baseline_handoff_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _generate_gate_artifact(tmp_path: Path) -> Path:
    gate_artifact_dir = tmp_path / "phase1-demo-mvp-review-package"
    result = subprocess.run(
        [
            sys.executable,
            str(GATE_RUNNER_SCRIPT_PATH),
            "--artifact-dir",
            str(gate_artifact_dir),
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
    assert result.returncode == 0, result.stderr
    return gate_artifact_dir


def test_phase1_demo_mvp_baseline_handoff_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-phase1-demo-mvp-baseline-handoff"
    assert fixture["package_id"] == "phase1-demo-mvp-baseline-handoff-v0.1"
    assert fixture["milestone"] == {
        "id": "M13",
        "name": "Phase 1 Demo MVP Baseline Handoff",
        "effort_unit": "施工队工时",
        "claim": "demo-only baseline handoff",
    }
    assert fixture["baseline_summary"] == {
        "readiness_status": "ready_for_phase1_demo_review",
        "canonical_reference": "demo.html",
        "route": "/demo-reconstruction",
        "node_count": 20,
        "wire_count": 23,
        "deliverable_claim": "stable demo MVP console baseline",
        "non_claims": [
            "no controller truth promotion",
            "no certification claim",
            "no production readiness claim",
        ],
    }
    assert fixture["deterministic_gates"] == {
        "gate_artifact_verification": "pass",
        "artifact_contract": "pass",
        "entrypoints": "pass",
        "human_handoff_doc": "pass",
        "boundary": "pass",
    }
    assert fixture["review_boundaries"]["controller_truth_modified"] is False
    assert fixture["review_boundaries"]["certification_claim"] == "none"


def test_phase1_demo_mvp_baseline_handoff_runner_and_checker_converge(
    tmp_path: Path,
) -> None:
    gate_artifact_dir = _generate_gate_artifact(tmp_path)
    handoff_artifact_dir = tmp_path / "baseline-handoff"
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(handoff_artifact_dir),
            "--gate-artifact-dir",
            str(gate_artifact_dir),
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

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "phase1-demo-mvp-baseline-handoff-v0.1"
    assert payload["baseline_summary"]["route"] == "/demo-reconstruction"
    assert payload["baseline_summary"]["node_count"] == 20
    assert payload["baseline_summary"]["wire_count"] == 23
    assert payload["entrypoints"]["local_gate"] == "make phase1-demo-mvp-gate"
    assert payload["entrypoints"]["external_artifact_gate"] == (
        "make verify-phase1-demo-mvp-gate-artifact"
    )
    assert payload["artifact_contract"]["machine_entry"] == (
        "phase1_demo_mvp_gate_summary.json"
    )
    assert payload["artifact_contract"]["artifact_name"] == (
        "phase1-demo-mvp-review-package"
    )
    assert payload["deterministic_gates"] == {
        "gate_artifact_verification": "pass",
        "artifact_contract": "pass",
        "entrypoints": "pass",
        "human_handoff_doc": "pass",
        "boundary": "pass",
    }
    assert payload["mismatches"] == []

    package_path = Path(payload["artifact_paths"]["handoff_package"])
    report_path = Path(payload["artifact_paths"]["human_handoff_doc"])
    assert package_path.exists()
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "Phase 1 Demo MVP Baseline Handoff" in report_text
    assert "demo.html" in report_text
    assert "/demo-reconstruction" in report_text
    assert "20 nodes / 23 wires" in report_text
    assert "certification_claim: none" in report_text

    verify = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT_PATH),
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

    assert verify.returncode == 0, verify.stderr
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["kind"] == (
        "ai-fantui-phase1-demo-mvp-baseline-handoff-verification"
    )
    assert verify_payload["status"] == "pass"
    assert verify_payload["deterministic_gates"] == {
        "schema": "pass",
        "gate_artifact": "pass",
        "entrypoints": "pass",
        "human_handoff_doc": "pass",
        "boundary": "pass",
    }
    assert verify_payload["mismatches"] == []


def test_phase1_demo_mvp_baseline_handoff_checker_rejects_boundary_drift(
    tmp_path: Path,
) -> None:
    gate_artifact_dir = _generate_gate_artifact(tmp_path)
    handoff_artifact_dir = tmp_path / "baseline-handoff"
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(handoff_artifact_dir),
            "--gate-artifact-dir",
            str(gate_artifact_dir),
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
    assert result.returncode == 0, result.stderr
    package_path = handoff_artifact_dir / "phase1_demo_mvp_baseline_handoff_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["review_boundaries"]["certification_claim"] = "claimed"
    package_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    verify = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT_PATH),
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

    assert verify.returncode == 1
    payload = json.loads(verify.stdout)
    assert payload["status"] == "fail"
    assert payload["deterministic_gates"]["boundary"] == "fail"
    assert any("certification_claim" in mismatch for mismatch in payload["mismatches"])


def test_phase1_demo_mvp_baseline_handoff_is_wired_into_make_and_ci() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "PHASE1_DEMO_MVP_BASELINE_HANDOFF_ARTIFACT_DIR" in makefile
    assert "phase1-demo-mvp-baseline-handoff" in makefile
    assert "scripts/run_phase1_demo_mvp_baseline_handoff.py --format json" in makefile
    assert "scripts/verify_phase1_demo_mvp_baseline_handoff.py --format json" in makefile
    assert "Run Phase 1 demo MVP baseline handoff" in workflow
    assert "Upload Phase 1 demo MVP baseline handoff" in workflow
    assert "phase1-demo-mvp-baseline-handoff" in workflow
    assert workflow.index("Verify Phase 1 demo MVP gate artifact") < workflow.index(
        "Run Phase 1 demo MVP baseline handoff"
    )

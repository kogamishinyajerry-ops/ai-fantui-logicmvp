from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_project_owner_external_review_handoff.py"
)
VERIFY_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_project_owner_final_decision.py"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-owner-final-decision.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
REQUIRED_NON_CLAIMS = [
    "no certification or DAL readiness claim",
    "no controller truth promotion",
    "no production readiness claim",
    "no customer deployment readiness claim",
]


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _run_handoff(tmp_path: Path) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(HANDOFF_SCRIPT_PATH),
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
        timeout=600,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _write_review_result(tmp_path: Path, handoff: dict) -> Path:
    review_path = tmp_path / "project_owner_external_review_result.json"
    result = {
        "kind": "ai-fantui-project-owner-external-review-result",
        "review_mode": "read_only",
        "verdict": "accept_evidence",
        "blocking_findings": [],
        "non_blocking_findings": [],
        "boundary_assessment": "Evidence boundaries remain explicit.",
        "next_decision_recommendation": "accept",
        "reviewed_artifacts": [
            {
                "id": item["id"],
                "path": item["path"],
                "status": "reviewed",
            }
            for item in handoff["required_reading"]
        ],
        "boundary_claims": {
            "certification_claim": "none",
            "controller_truth_promotion": False,
            "production_readiness": False,
            "customer_deployment_readiness": False,
        },
    }
    review_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return review_path


def _write_decision(
    *,
    tmp_path: Path,
    decision: str = "accept",
    source_review_verdict: str = "accept_evidence",
    acknowledged_non_claims: list[str] | None = None,
) -> Path:
    decision_path = tmp_path / "project_owner_final_decision.json"
    claims = list(acknowledged_non_claims or REQUIRED_NON_CLAIMS)
    result = {
        "kind": "ai-fantui-project-owner-final-decision",
        "decision": decision,
        "rationale": "Project owner selects the verified evidence path.",
        "source_review_verdict": source_review_verdict,
        "accepted_non_claims": claims,
        "project_owner_attestation": {
            "role": "project_owner",
            "selected_option": decision,
            "decision_is_final": True,
            "acknowledged_non_claims": claims,
        },
    }
    decision_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return decision_path


def _verify(
    *,
    packet_path: Path,
    decision_path: Path,
    handoff_path: Path,
    review_path: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT_PATH),
            "--packet",
            str(packet_path),
            "--decision",
            str(decision_path),
            "--handoff",
            str(handoff_path),
            "--review",
            str(review_path),
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


def test_project_owner_final_decision_accepts_verified_external_review(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    review_path = _write_review_result(tmp_path, handoff)
    decision_path = _write_decision(tmp_path=tmp_path)

    result = _verify(
        packet_path=Path(handoff["artifact_paths"]["source_packet_json"]),
        decision_path=decision_path,
        handoff_path=Path(handoff["artifact_paths"]["handoff_json"]),
        review_path=review_path,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-project-owner-final-decision-verification"
    assert payload["status"] == "pass"
    assert payload["decision"] == "accept"
    assert payload["decision_status"] == "customer_demo_mvp_accepted"
    assert payload["final_acceptance"] == "granted_for_customer_demo_mvp_evidence_only"
    assert payload["m21_queue_unblocked"] is True
    assert payload["project_owner_required"] is False
    assert payload["external_review_result_status"] == "external_review_accepts_evidence"
    assert payload["deterministic_gates"] == {
        "project_owner_packet": "pass",
        "decision_shape": "pass",
        "project_owner_attestation": "pass",
        "external_review_result": "pass",
        "non_claim_boundaries": "pass",
        "local_gate": "pass",
    }
    assert payload["mismatches"] == []


def test_project_owner_final_decision_blocks_accept_without_external_review(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    decision_path = _write_decision(tmp_path=tmp_path)
    missing_review_path = tmp_path / "missing_external_review_result.json"

    result = _verify(
        packet_path=Path(handoff["artifact_paths"]["source_packet_json"]),
        decision_path=decision_path,
        handoff_path=Path(handoff["artifact_paths"]["handoff_json"]),
        review_path=missing_review_path,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["decision_status"] == "blocked"
    assert payload["deterministic_gates"]["external_review_result"] == "fail"
    assert "external review result verification must pass for accept" in payload[
        "mismatches"
    ]


def test_project_owner_final_decision_records_demo_polish_without_acceptance(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    decision_path = _write_decision(
        tmp_path=tmp_path,
        decision="demo_polish",
        source_review_verdict="needs_changes",
    )

    result = _verify(
        packet_path=Path(handoff["artifact_paths"]["source_packet_json"]),
        decision_path=decision_path,
        handoff_path=Path(handoff["artifact_paths"]["handoff_json"]),
        review_path=tmp_path / "not_required.json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["decision_status"] == "demo_polish_requested"
    assert payload["final_acceptance"] == "not_granted"
    assert payload["m21_queue_unblocked"] is False


def test_project_owner_final_decision_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Project Owner Final Decision" in doc
    assert "project-owner-final-decision" in doc
    assert "accept" in doc
    assert "external_review" in doc
    assert "demo_polish" in doc
    assert "external_review_accepts_evidence" in doc
    assert "granted_for_customer_demo_mvp_evidence_only" in doc
    assert "customer_demo_mvp_accepted" in doc
    assert "PROJECT_OWNER_FINAL_DECISION_PATH" in makefile
    assert "project-owner-final-decision" in makefile
    assert "scripts/verify_project_owner_final_decision.py --format json" in makefile

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
VERIFY_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_project_owner_external_review_result.py"
)
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-owner-external-review-result.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


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


def _write_review_result(
    *,
    tmp_path: Path,
    handoff: dict,
    verdict: str = "accept_evidence",
    blocking_findings: list[dict] | None = None,
    next_decision_recommendation: str = "accept",
    boundary_claims: dict | None = None,
) -> Path:
    review_path = tmp_path / "project_owner_external_review_result.json"
    result = {
        "kind": "ai-fantui-project-owner-external-review-result",
        "review_mode": "read_only",
        "verdict": verdict,
        "blocking_findings": blocking_findings or [],
        "non_blocking_findings": [],
        "boundary_assessment": (
            "Evidence boundaries are explicit; no certification, production, "
            "deployment, or controller truth promotion is claimed."
        ),
        "next_decision_recommendation": next_decision_recommendation,
        "reviewed_artifacts": [
            {
                "id": item["id"],
                "path": item["path"],
                "status": "reviewed",
            }
            for item in handoff["required_reading"]
        ],
        "boundary_claims": boundary_claims
        or {
            "certification_claim": "none",
            "controller_truth_promotion": False,
            "production_readiness": False,
            "customer_deployment_readiness": False,
        },
    }
    review_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return review_path


def _verify(handoff_path: Path, review_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT_PATH),
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


def test_project_owner_external_review_result_accepts_clean_read_only_review(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    handoff_path = Path(handoff["artifact_paths"]["handoff_json"])
    review_path = _write_review_result(tmp_path=tmp_path, handoff=handoff)

    result = _verify(handoff_path, review_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-project-owner-external-review-result-verification"
    assert payload["status"] == "pass"
    assert payload["result_status"] == "external_review_accepts_evidence"
    assert payload["review_verdict"] == "accept_evidence"
    assert payload["next_decision_recommendation"] == "accept"
    assert payload["final_acceptance"] == "not_granted"
    assert payload["project_owner_required"] is True
    assert payload["deterministic_gates"] == {
        "handoff": "pass",
        "review_shape": "pass",
        "verdict": "pass",
        "reviewed_artifacts": "pass",
        "boundary_claims": "pass",
        "local_gate": "pass",
    }
    assert payload["required_artifact_ids"] == [
        "project_owner_packet_json",
        "project_owner_packet_markdown",
        "customer_demo_closeout_json",
        "customer_demo_closeout_markdown",
        "project_status_html",
        "logic_circuit_diagram_screenshot",
        "demo_first_screen_screenshot",
    ]
    assert payload["mismatches"] == []


def test_project_owner_external_review_result_blocks_overclaiming(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    handoff_path = Path(handoff["artifact_paths"]["handoff_json"])
    review_path = _write_review_result(
        tmp_path=tmp_path,
        handoff=handoff,
        boundary_claims={
            "certification_claim": "DAL-ready",
            "controller_truth_promotion": True,
            "production_readiness": True,
            "customer_deployment_readiness": False,
        },
    )

    result = _verify(handoff_path, review_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["result_status"] == "blocked"
    assert payload["deterministic_gates"]["boundary_claims"] == "fail"
    assert "boundary_claims.certification_claim must be 'none'" in payload["mismatches"]
    assert "boundary_claims.controller_truth_promotion must be False" in payload[
        "mismatches"
    ]
    assert "boundary_claims.production_readiness must be False" in payload["mismatches"]


def test_project_owner_external_review_result_requires_blockers_for_changes(
    tmp_path: Path,
) -> None:
    handoff = _run_handoff(tmp_path)
    handoff_path = Path(handoff["artifact_paths"]["handoff_json"])
    review_path = _write_review_result(
        tmp_path=tmp_path,
        handoff=handoff,
        verdict="needs_changes",
        blocking_findings=[],
        next_decision_recommendation="accept",
    )

    result = _verify(handoff_path, review_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert "needs_changes must include at least one blocking_finding" in payload[
        "mismatches"
    ]
    assert "needs_changes must recommend demo_polish" in payload["mismatches"]


def test_project_owner_external_review_result_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Project Owner External Review Result" in doc
    assert "project-owner-external-review-result" in doc
    assert "accept_evidence" in doc
    assert "needs_changes" in doc
    assert "reject_evidence" in doc
    assert "final acceptance remains" in doc
    assert "certification_claim: none" in doc
    assert "PROJECT_OWNER_EXTERNAL_REVIEW_RESULT_PATH" in makefile
    assert "project-owner-external-review-result" in makefile
    assert "scripts/verify_project_owner_external_review_result.py --format json" in makefile

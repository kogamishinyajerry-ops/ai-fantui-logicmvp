#!/usr/bin/env python3
"""Verify a read-only external review result for project-owner evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_HANDOFF_PATH = Path(
    "/tmp/ai-fantui-project-owner-external-review-handoff/"
    "project_owner_external_review_handoff.json"
)
DEFAULT_REVIEW_PATH = Path(
    "/tmp/ai-fantui-project-owner-external-review-handoff/"
    "project_owner_external_review_result.json"
)
VALID_VERDICTS = {"accept_evidence", "needs_changes", "reject_evidence"}
VALID_NEXT_RECOMMENDATIONS = {"accept", "external_review", "demo_polish"}
EXPECTED_BOUNDARY_CLAIMS = {
    "certification_claim": "none",
    "controller_truth_promotion": False,
    "production_readiness": False,
    "customer_deployment_readiness": False,
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a project-owner external review result JSON.",
    )
    parser.add_argument("--handoff", type=Path, default=DEFAULT_HANDOFF_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _load_json(path: Path, mismatches: list[str], label: str) -> dict[str, Any]:
    if not path.exists():
        mismatches.append(f"{label} missing: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        mismatches.append(f"{label} is not valid JSON: {exc}")
        return {}


def _path_exists(path_value: Any) -> bool:
    return isinstance(path_value, str) and bool(path_value) and Path(path_value).exists()


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _required_artifact_ids(handoff: dict[str, Any]) -> list[str]:
    return [
        item.get("id", "")
        for item in handoff.get("required_reading", [])
        if isinstance(item, dict)
    ]


def _reviewed_artifacts(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = review.get("reviewed_artifacts", [])
    if not isinstance(artifacts, list):
        return {}
    return {
        item.get("id", ""): item
        for item in artifacts
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _reviewed_artifacts_valid(
    *,
    handoff: dict[str, Any],
    review: dict[str, Any],
    mismatches: list[str],
) -> bool:
    required = {
        item.get("id", ""): item
        for item in handoff.get("required_reading", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    reviewed = _reviewed_artifacts(review)
    valid = True
    if not required:
        mismatches.append("handoff.required_reading must not be empty")
        return False
    for artifact_id, required_item in required.items():
        reviewed_item = reviewed.get(artifact_id)
        if not reviewed_item:
            mismatches.append(f"reviewed_artifacts missing {artifact_id}")
            valid = False
            continue
        if reviewed_item.get("status") != "reviewed":
            mismatches.append(f"{artifact_id}.status must be reviewed")
            valid = False
        if reviewed_item.get("path") != required_item.get("path"):
            mismatches.append(f"{artifact_id}.path must match handoff required_reading")
            valid = False
        if not _path_exists(reviewed_item.get("path")):
            mismatches.append(f"{artifact_id}.path does not exist")
            valid = False
    return valid


def _boundary_claims_valid(review: dict[str, Any], mismatches: list[str]) -> bool:
    claims = review.get("boundary_claims")
    if not isinstance(claims, dict):
        mismatches.append("boundary_claims must be an object")
        return False
    valid = True
    for key, expected in EXPECTED_BOUNDARY_CLAIMS.items():
        if claims.get(key) != expected:
            mismatches.append(f"boundary_claims.{key} must be {expected!r}")
            valid = False
    return valid


def _verdict_valid(review: dict[str, Any], mismatches: list[str]) -> bool:
    verdict = review.get("verdict")
    blocking_findings = review.get("blocking_findings")
    next_recommendation = review.get("next_decision_recommendation")
    valid = True
    if verdict not in VALID_VERDICTS:
        mismatches.append("verdict must be accept_evidence, needs_changes, or reject_evidence")
        valid = False
    if next_recommendation not in VALID_NEXT_RECOMMENDATIONS:
        mismatches.append("next_decision_recommendation must be a known project-owner option")
        valid = False
    if not isinstance(blocking_findings, list):
        mismatches.append("blocking_findings must be a list")
        valid = False
    if verdict == "accept_evidence" and blocking_findings:
        mismatches.append("accept_evidence must not contain blocking_findings")
        valid = False
    if verdict in {"needs_changes", "reject_evidence"} and not blocking_findings:
        mismatches.append(f"{verdict} must include at least one blocking_finding")
        valid = False
    if verdict == "accept_evidence" and next_recommendation != "accept":
        mismatches.append("accept_evidence must recommend accept")
        valid = False
    if verdict in {"needs_changes", "reject_evidence"} and next_recommendation != "demo_polish":
        mismatches.append(f"{verdict} must recommend demo_polish")
        valid = False
    return valid


def _shape_valid(review: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if review.get("kind") != "ai-fantui-project-owner-external-review-result":
        mismatches.append("kind must be ai-fantui-project-owner-external-review-result")
        valid = False
    if review.get("review_mode") != "read_only":
        mismatches.append("review_mode must be read_only")
        valid = False
    if not isinstance(review.get("non_blocking_findings"), list):
        mismatches.append("non_blocking_findings must be a list")
        valid = False
    if not isinstance(review.get("boundary_assessment"), str) or not review.get(
        "boundary_assessment", ""
    ).strip():
        mismatches.append("boundary_assessment must be a non-empty string")
        valid = False
    return valid


def _handoff_valid(handoff: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if handoff.get("status") != "pass":
        mismatches.append("handoff.status must be pass")
        valid = False
    if handoff.get("handoff_status") != "ready_for_read_only_external_review":
        mismatches.append("handoff.handoff_status must be ready_for_read_only_external_review")
        valid = False
    if handoff.get("review_mode") != "read_only":
        mismatches.append("handoff.review_mode must be read_only")
        valid = False
    gates = handoff.get("deterministic_gates", {})
    if not isinstance(gates, dict) or gates.get("local_gate") != "pass":
        mismatches.append("handoff deterministic local_gate must be pass")
        valid = False
    return valid


def _result_status(review: dict[str, Any], status: str) -> str:
    if status != "pass":
        return "blocked"
    verdict = review.get("verdict")
    if verdict == "accept_evidence":
        return "external_review_accepts_evidence"
    if verdict == "needs_changes":
        return "external_review_needs_changes"
    if verdict == "reject_evidence":
        return "external_review_rejects_evidence"
    return "blocked"


def verify_project_owner_external_review_result(
    *,
    handoff_path: Path = DEFAULT_HANDOFF_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> dict[str, Any]:
    mismatches: list[str] = []
    handoff = _load_json(handoff_path, mismatches, "handoff")
    review = _load_json(review_path, mismatches, "review")
    gates = {
        "handoff": _gate_status(bool(handoff) and _handoff_valid(handoff, mismatches)),
        "review_shape": _gate_status(bool(review) and _shape_valid(review, mismatches)),
        "verdict": _gate_status(bool(review) and _verdict_valid(review, mismatches)),
        "reviewed_artifacts": _gate_status(
            bool(handoff)
            and bool(review)
            and _reviewed_artifacts_valid(
                handoff=handoff,
                review=review,
                mismatches=mismatches,
            )
        ),
        "boundary_claims": _gate_status(
            bool(review) and _boundary_claims_valid(review, mismatches)
        ),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in gates.items() if key != "local_gate")
        and not mismatches
        else "fail"
    )
    gates["local_gate"] = status
    payload = {
        "kind": "ai-fantui-project-owner-external-review-result-verification",
        "status": status,
        "result_status": _result_status(review, status),
        "source_handoff": str(handoff_path),
        "source_review": str(review_path),
        "review_verdict": review.get("verdict", ""),
        "next_decision_recommendation": review.get("next_decision_recommendation", ""),
        "final_acceptance": "not_granted",
        "project_owner_required": True,
        "required_artifact_ids": _required_artifact_ids(handoff),
        "deterministic_gates": gates,
        "mismatches": mismatches,
        "recommended_next_step": (
            "Project owner must still choose accept, external_review, or demo_polish."
        ),
    }
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: project-owner external review result verified")
        print(f"result_status: {payload['result_status']}")
        print(f"review_verdict: {payload['review_verdict']}")
    else:
        print(
            "FAIL: project-owner external review result failed "
            f"({', '.join(payload['mismatches'])})"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    payload = verify_project_owner_external_review_result(
        handoff_path=args.handoff,
        review_path=args.review,
    )
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

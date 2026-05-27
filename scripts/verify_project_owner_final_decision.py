#!/usr/bin/env python3
"""Verify a project-owner final decision for the Customer Demo MVP evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from verify_project_owner_external_review_result import (
    DEFAULT_HANDOFF_PATH,
    DEFAULT_REVIEW_PATH,
    verify_project_owner_external_review_result,
)


DEFAULT_PACKET_PATH = Path(
    "/tmp/ai-fantui-project-owner-external-review-handoff/"
    "project-owner-acceptance-review-packet/"
    "project_owner_acceptance_review_packet.json"
)
DEFAULT_DECISION_PATH = Path(
    "/tmp/ai-fantui-project-owner-external-review-handoff/"
    "project_owner_final_decision.json"
)
VALID_DECISIONS = {"accept", "external_review", "demo_polish"}
REQUIRED_NON_CLAIMS = {
    "no certification or DAL readiness claim",
    "no controller truth promotion",
    "no production readiness claim",
    "no customer deployment readiness claim",
}
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a project-owner final decision JSON.",
    )
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--decision", type=Path, default=DEFAULT_DECISION_PATH)
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


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _packet_valid(packet: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if packet.get("kind") != "ai-fantui-project-owner-acceptance-review-packet":
        mismatches.append("packet.kind must be ai-fantui-project-owner-acceptance-review-packet")
        valid = False
    if packet.get("status") != "pass":
        mismatches.append("packet.status must be pass")
        valid = False
    if packet.get("packet_status") != "ready_for_project_owner_decision":
        mismatches.append("packet.packet_status must be ready_for_project_owner_decision")
        valid = False
    decision_ids = [
        option.get("id")
        for option in packet.get("decision_options", [])
        if isinstance(option, dict)
    ]
    if decision_ids != ["accept", "external_review", "demo_polish"]:
        mismatches.append("packet.decision_options must be accept, external_review, demo_polish")
        valid = False
    return valid


def _decision_shape_valid(decision_doc: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if decision_doc.get("kind") != "ai-fantui-project-owner-final-decision":
        mismatches.append("decision.kind must be ai-fantui-project-owner-final-decision")
        valid = False
    if decision_doc.get("decision") not in VALID_DECISIONS:
        mismatches.append("decision must be accept, external_review, or demo_polish")
        valid = False
    if not isinstance(decision_doc.get("rationale"), str) or not decision_doc.get(
        "rationale", ""
    ).strip():
        mismatches.append("decision.rationale must be a non-empty string")
        valid = False
    return valid


def _attestation_valid(decision_doc: dict[str, Any], mismatches: list[str]) -> bool:
    attestation = decision_doc.get("project_owner_attestation")
    if not isinstance(attestation, dict):
        mismatches.append("project_owner_attestation must be an object")
        return False
    decision = decision_doc.get("decision")
    valid = True
    if attestation.get("role") != "project_owner":
        mismatches.append("project_owner_attestation.role must be project_owner")
        valid = False
    if attestation.get("selected_option") != decision:
        mismatches.append("project_owner_attestation.selected_option must match decision")
        valid = False
    if attestation.get("decision_is_final") is not True:
        mismatches.append("project_owner_attestation.decision_is_final must be true")
        valid = False
    acknowledged = attestation.get("acknowledged_non_claims")
    if not isinstance(acknowledged, list):
        mismatches.append("project_owner_attestation.acknowledged_non_claims must be a list")
        return False
    missing = REQUIRED_NON_CLAIMS.difference(str(item) for item in acknowledged)
    for claim in sorted(missing):
        mismatches.append(f"project_owner_attestation must acknowledge {claim}")
        valid = False
    return valid


def _boundary_valid(packet: dict[str, Any], decision_doc: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if packet.get("review_boundaries") != EXPECTED_REVIEW_BOUNDARIES:
        mismatches.append("packet.review_boundaries must preserve non-claim boundaries")
        valid = False
    packet_non_claims = set(str(item) for item in packet.get("non_claims", []))
    missing_packet_claims = REQUIRED_NON_CLAIMS.difference(packet_non_claims)
    for claim in sorted(missing_packet_claims):
        mismatches.append(f"packet.non_claims must include {claim}")
        valid = False
    decision_non_claims = decision_doc.get("accepted_non_claims", [])
    if not isinstance(decision_non_claims, list):
        mismatches.append("decision.accepted_non_claims must be a list")
        return False
    missing_decision_claims = REQUIRED_NON_CLAIMS.difference(
        str(item) for item in decision_non_claims
    )
    for claim in sorted(missing_decision_claims):
        mismatches.append(f"decision.accepted_non_claims must include {claim}")
        valid = False
    return valid


def _external_review_valid(
    *,
    decision_doc: dict[str, Any],
    handoff_path: Path,
    review_path: Path,
    mismatches: list[str],
) -> tuple[bool, dict[str, Any]]:
    if decision_doc.get("decision") != "accept":
        return True, {}
    review_verification = verify_project_owner_external_review_result(
        handoff_path=handoff_path,
        review_path=review_path,
    )
    valid = True
    if review_verification.get("status") != "pass":
        mismatches.append("external review result verification must pass for accept")
        valid = False
    if review_verification.get("result_status") != "external_review_accepts_evidence":
        mismatches.append("accept requires external_review_accepts_evidence")
        valid = False
    if decision_doc.get("source_review_verdict") != "accept_evidence":
        mismatches.append("decision.source_review_verdict must be accept_evidence")
        valid = False
    return valid, review_verification


def _decision_status(decision: str, status: str) -> str:
    if status != "pass":
        return "blocked"
    if decision == "accept":
        return "customer_demo_mvp_accepted"
    if decision == "external_review":
        return "external_review_requested"
    if decision == "demo_polish":
        return "demo_polish_requested"
    return "blocked"


def _final_acceptance(decision: str, status: str) -> str:
    if status == "pass" and decision == "accept":
        return "granted_for_customer_demo_mvp_evidence_only"
    return "not_granted"


def verify_project_owner_final_decision(
    *,
    packet_path: Path = DEFAULT_PACKET_PATH,
    decision_path: Path = DEFAULT_DECISION_PATH,
    handoff_path: Path = DEFAULT_HANDOFF_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> dict[str, Any]:
    mismatches: list[str] = []
    packet = _load_json(packet_path, mismatches, "packet")
    decision_doc = _load_json(decision_path, mismatches, "decision")
    external_review_ok, review_verification = _external_review_valid(
        decision_doc=decision_doc,
        handoff_path=handoff_path,
        review_path=review_path,
        mismatches=mismatches,
    )
    gates = {
        "project_owner_packet": _gate_status(bool(packet) and _packet_valid(packet, mismatches)),
        "decision_shape": _gate_status(
            bool(decision_doc) and _decision_shape_valid(decision_doc, mismatches)
        ),
        "project_owner_attestation": _gate_status(
            bool(decision_doc) and _attestation_valid(decision_doc, mismatches)
        ),
        "external_review_result": _gate_status(external_review_ok),
        "non_claim_boundaries": _gate_status(
            bool(packet)
            and bool(decision_doc)
            and _boundary_valid(packet, decision_doc, mismatches)
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
    decision = str(decision_doc.get("decision", ""))
    payload = {
        "kind": "ai-fantui-project-owner-final-decision-verification",
        "status": status,
        "decision": decision,
        "decision_status": _decision_status(decision, status),
        "final_acceptance": _final_acceptance(decision, status),
        "m21_queue_unblocked": status == "pass" and decision == "accept",
        "project_owner_required": status != "pass",
        "source_packet": str(packet_path),
        "source_decision": str(decision_path),
        "source_handoff": str(handoff_path),
        "source_review": str(review_path),
        "external_review_result_status": review_verification.get("result_status", ""),
        "deterministic_gates": gates,
        "mismatches": mismatches,
        "recommended_next_step": (
            "Continue M21 queue expansion only if decision_status is "
            "customer_demo_mvp_accepted."
        ),
    }
    return payload


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: project-owner final decision verified")
        print(f"decision_status: {payload['decision_status']}")
        print(f"final_acceptance: {payload['final_acceptance']}")
    else:
        print(
            "FAIL: project-owner final decision failed "
            f"({', '.join(payload['mismatches'])})"
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    payload = verify_project_owner_final_decision(
        packet_path=args.packet,
        decision_path=args.decision,
        handoff_path=args.handoff,
        review_path=args.review,
    )
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

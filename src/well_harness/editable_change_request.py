"""ChangeRequest handoff builders for editable workbench sandbox drafts.

These helpers produce evidence packets only. They do not mutate Linear,
controller truth, adapter status, or certified baselines.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.editable_control_model import (
    editable_control_model_hash,
    validate_editable_control_model,
    validate_editable_control_model_diff_report,
)


CHANGE_REQUEST_SCHEMA_NAME = "change_request_v0_1.schema.json"
CHANGE_REQUEST_SCHEMA_VERSION = "change_request.v0.1"
DEFAULT_CHANGE_REQUEST_OWNER = "Codex Daily Lane"
DEFAULT_LAYER = "L4"


class ChangeRequestValidationError(ValueError):
    """Raised when a ChangeRequest packet exceeds Codex lane authority."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / CHANGE_REQUEST_SCHEMA_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _change_request_id(source_ref: str, model_hash: str) -> str:
    source = "".join(char if char.isalnum() else "-" for char in source_ref.upper())
    source = source.strip("-") or "WORKBENCH"
    return f"CR-{source}-{model_hash[:8].upper()}"


def _red_line_label(red_lines: list[str]) -> str:
    if red_lines == ["none"]:
        return "none"
    return ", ".join(red_lines)


def validate_change_request(payload: dict[str, Any]) -> None:
    """Validate schema and Codex-lane invariants for ChangeRequest packets."""
    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ChangeRequestValidationError(
            f"schema validation failed{location}: {exc.message}"
        ) from exc

    handoff = payload.get("workbench_handoff")
    if not handoff:
        return
    if handoff["truth_level_impact"] != "none":
        raise ChangeRequestValidationError("workbench_handoff truth_level_impact must be none")
    if handoff["dal_impact"] != "none":
        raise ChangeRequestValidationError("workbench_handoff dal_impact must be none")
    if handoff["red_line_impact"]["touched"] != ["none"]:
        raise ChangeRequestValidationError("workbench_handoff red_line_impact must be none")
    if "Truth-level impact: certified" in handoff["pr_proof_packet"]:
        raise ChangeRequestValidationError("pr_proof_packet must not claim certified impact")
    if "sync to linear" in handoff["linear_issue_body"].lower():
        raise ChangeRequestValidationError("linear_issue_body must not claim live Linear sync")


def build_linear_issue_body(change_request: dict[str, Any]) -> str:
    """Return a Linear-ready body for manual/draft handoff."""
    handoff = change_request["workbench_handoff"]
    red_lines = _red_line_label(handoff["red_line_impact"]["touched"])
    acceptance = "\n".join(f"- {item}" for item in handoff["acceptance"])
    boundaries = "\n".join(f"- {item}" for item in handoff["boundaries"])
    evidence = "\n".join(f"- {item}" for item in handoff["evidence_required"])
    return "\n".join(
        [
            "## Outcome",
            handoff["outcome"],
            "",
            "## Context",
            handoff["context"],
            "",
            "## Acceptance",
            acceptance,
            "",
            "## Boundaries",
            boundaries,
            "",
            "## Evidence Required",
            evidence,
            "",
            "## Metadata",
            f"- ChangeRequest: {change_request['change_request_id']}",
            f"- Adapter: {handoff['adapter']}",
            f"- Layer: {handoff['layer']}",
            f"- Truth-level impact: {handoff['truth_level_impact']}",
            f"- DAL impact: {handoff['dal_impact']}",
            f"- Red lines touched: {red_lines}",
            f"- Changed model hash: {handoff['changed_model_hash']}",
            f"- Diff verdict: {handoff['diff_verdict']}",
            "- Linear mutation: draft_only / not_attempted",
            "- Agent eligible: No",
        ]
    )


def build_pr_proof_packet(
    change_request: dict[str, Any],
    *,
    test_delta: str = "targeted pytest pending / default pytest pending / GSD pending",
) -> str:
    """Return the Codex Daily Lane PR proof packet fields."""
    handoff = change_request["workbench_handoff"]
    red_lines = _red_line_label(handoff["red_line_impact"]["touched"])
    return "\n".join(
        [
            f"Linear: {change_request['origin']['source_ref']}",
            f"Adapter: {handoff['adapter']}",
            f"Layer: {handoff['layer']}",
            f"Truth-level impact: {handoff['truth_level_impact']}",
            f"Red lines touched: {red_lines}",
            f"Test delta: {test_delta}",
            "",
            f"ChangeRequest: {change_request['change_request_id']}",
            f"Changed model hash: {handoff['changed_model_hash']}",
            f"Diff verdict: {handoff['diff_verdict']}",
            "No live Linear mutation; this packet is copy-ready evidence only.",
        ]
    )


def build_editable_workbench_change_request(
    model: dict[str, Any],
    diff_report: dict[str, Any],
    *,
    title: str,
    source_ref: str,
    created_at: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    """Build a draft-only ChangeRequest from an editable workbench candidate."""
    validate_editable_control_model(model)
    validate_editable_control_model_diff_report(diff_report)
    model_hash = editable_control_model_hash(model)
    if diff_report["candidate_run"]["model_hash"] != model_hash:
        raise ChangeRequestValidationError("diff report candidate model hash does not match model hash")

    created_on = created_at or datetime.now(timezone.utc).date().isoformat()
    request_summary = summary or (
        "Draft-only workbench ChangeRequest generated from a sandbox candidate "
        f"with baseline diff verdict {diff_report['verdict']}."
    )
    handoff = {
        "mode": "draft_only",
        "mutation_status": "not_attempted",
        "source_ref": source_ref,
        "adapter": model["system_id"],
        "layer": DEFAULT_LAYER,
        "model_id": model["model_id"],
        "changed_model_hash": model_hash,
        "diff_report_hash": _hash_payload(diff_report),
        "diff_verdict": diff_report["verdict"],
        "truth_level_impact": "none",
        "dal_impact": "none",
        "red_line_impact": {
            "touched": ["none"],
            "rationale": "Sandbox candidate output does not edit controller truth, frozen adapters, C919 reference packets, truth-level, or DAL/PSSA records.",
        },
        "outcome": "Review a sandbox candidate graph against the certified thrust-reverser baseline and decide whether it merits a separate governed implementation issue.",
        "context": "Generated from the editable control workbench. Candidate edits are sandbox-only and only produce diff evidence.",
        "acceptance": [
            "Candidate model hash and diff verdict are recorded.",
            "Reviewer can reproduce the candidate-vs-baseline comparison before any implementation work.",
            "No certified truth, DAL, PSSA, frozen adapter, or controller semantics are changed by this packet.",
        ],
        "boundaries": [
            "No live Linear mutation from the workbench.",
            "No change to src/well_harness/controller.py truth semantics.",
            "No frozen adapter, hardware YAML, or C919 reference packet edits.",
            "No truth-level promotion or DAL/PSSA decision.",
        ],
        "evidence_required": [
            "Editable model JSON or exported draft snapshot.",
            "Baseline diff report with equivalent/divergent/invalid verdict.",
            "Targeted pytest for changed schema/runtime/UI surface.",
            "PR proof packet listing truth impact and red-line status.",
        ],
        "linear_issue_body": "",
        "pr_proof_packet": "",
    }
    request = {
        "schema_version": CHANGE_REQUEST_SCHEMA_VERSION,
        "change_request_id": _change_request_id(source_ref, model_hash),
        "title": title,
        "summary": request_summary,
        "authority": {
            "status": "draft_non_authoritative",
            "approval_required_before_execution": True,
            "approval_routes": ["github_pr_review", "linear_evidence_record"],
        },
        "origin": {
            "source": "linear",
            "source_ref": source_ref,
            "created_by": "codex-daily-lane",
            "created_at": created_on,
        },
        "owner": {
            "name": DEFAULT_CHANGE_REQUEST_OWNER,
            "role": "draft_author",
        },
        "status": "draft",
        "classification": "behavior_change",
        "impacts": {
            "namespaces": ["logic_truth", "ui", "test", "documentation"],
            "adapters": [model["system_id"]],
            "truth_level_impact": "none",
        },
        "dal_impact": {
            "impact": "none",
            "rationale": "The ChangeRequest packet is evidence-only and does not execute a DAL-impacting change.",
        },
        "evidence_anchors": [
            {
                "kind": "linear",
                "ref": source_ref,
                "url": f"https://linear.app/jerrykogami/issue/{source_ref}",
            },
            {
                "kind": "repo_path",
                "ref": "editable workbench ChangeRequest builder",
                "path": "src/well_harness/editable_change_request.py",
            },
        ],
        "decision_links": [],
        "workbench_handoff": handoff,
    }
    request["workbench_handoff"]["linear_issue_body"] = build_linear_issue_body(request)
    request["workbench_handoff"]["pr_proof_packet"] = build_pr_proof_packet(request)
    validate_change_request(request)
    return request

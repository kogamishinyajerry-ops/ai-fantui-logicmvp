"""Workbench-facing sandbox run orchestration.

This module turns a UI draft snapshot into a sandbox candidate run against a
fixed timeline fixture. It produces diff evidence only; it never changes
controller truth.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from well_harness.editable_control_model import (
    APPROVED_OPS,
    EditableControlModelValidationError,
    build_reference_editable_control_model,
    editable_control_model_hash,
    validate_editable_control_model,
)
from well_harness.editable_timeline_sandbox import compare_editable_timeline_to_baseline
from well_harness.timeline_engine import parse_timeline


WORKBENCH_SANDBOX_RUN_KIND = "well-harness-workbench-sandbox-run"
WORKBENCH_SANDBOX_RUN_VERSION = 1
SUPPORTED_SCENARIOS = {
    "nominal_landing": "nominal_landing.json",
}


def _timeline_dir() -> Path:
    return Path(__file__).resolve().parent / "timelines"


def _load_timeline(scenario_id: str):
    filename = SUPPORTED_SCENARIOS.get(scenario_id)
    if filename is None:
        raise KeyError(scenario_id)
    payload = json.loads((_timeline_dir() / filename).read_text(encoding="utf-8"))
    return parse_timeline(payload)


def _base_response(*, scenario_id: str, verdict: str, model_hash: str | None = None) -> dict[str, Any]:
    return {
        "kind": WORKBENCH_SANDBOX_RUN_KIND,
        "version": WORKBENCH_SANDBOX_RUN_VERSION,
        "scenario_id": scenario_id,
        "verdict": verdict,
        "model_hash": model_hash,
        "truth_level_impact": "none",
        "red_lines": {
            "controller_truth_modified": False,
            "frozen_adapter_modified": False,
            "truth_level_impact": "none",
            "dal_pssa_impact": "none",
            "product_llm_chat_restored": False,
        },
    }


def _invalid_response(
    *,
    scenario_id: str,
    verdict: str,
    message: str,
    model_hash: str | None = None,
) -> dict[str, Any]:
    response = _base_response(
        scenario_id=scenario_id,
        verdict=verdict,
        model_hash=model_hash,
    )
    response.update(
        {
            "error": message,
            "summary": {
                "first_divergence": None,
                "assertion_status": "not_run",
                "frame_count": 0,
            },
        }
    )
    return response


def _draft_object(request_payload: dict[str, Any]) -> dict[str, Any]:
    draft = request_payload.get("draft", {})
    if draft is None:
        return {}
    if not isinstance(draft, dict):
        raise EditableControlModelValidationError("draft must be a JSON object")
    return draft


def _ensure_draft_boundaries(draft: dict[str, Any]) -> None:
    if draft.get("system_id", "thrust-reverser") != "thrust-reverser":
        raise EditableControlModelValidationError("only thrust-reverser sandbox drafts are supported")
    if draft.get("truth_level_impact", "none") != "none":
        raise EditableControlModelValidationError("truth_level_impact must be none")
    if draft.get("controller_truth_modified", False) is not False:
        raise EditableControlModelValidationError("controller_truth_modified must be false")
    if draft.get("dal_pssa_impact", "none") != "none":
        raise EditableControlModelValidationError("dal_pssa_impact must be none")


def _apply_ui_draft(base_model: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    model = copy.deepcopy(base_model)
    model["model_id"] = "thrust-reverser-workbench-ui-draft-v1"
    model["view_status"] = "draft"
    nodes = {
        node["id"]: node
        for node in model["nodes"]
    }
    for update in draft.get("nodes", []):
        if not isinstance(update, dict):
            raise EditableControlModelValidationError("draft nodes must be objects")
        node_id = str(update.get("id", "")).strip()
        if not node_id:
            raise EditableControlModelValidationError("draft node id is required")
        node = nodes.get(node_id)
        if node is None:
            raise EditableControlModelValidationError(f"unknown draft node id {node_id!r}")
        if "label" in update:
            node["label"] = str(update["label"])
        if "op" in update and update["op"] is not None:
            op = str(update["op"])
            if op not in APPROVED_OPS:
                raise EditableControlModelValidationError(f"draft node {node_id} op is not approved: {op}")
            node["op"] = op
    validate_editable_control_model(model)
    return model


def _build_summary(diff_report: dict[str, Any]) -> dict[str, Any]:
    scenario_result = diff_report.get("scenario_result") or {}
    return {
        "first_divergence": diff_report.get("first_divergence"),
        "assertion_status": scenario_result.get("assertion_status", "not_run"),
        "frame_count": scenario_result.get("frame_count", 0),
        "per_signal_delta": list(diff_report.get("per_signal_delta") or []),
    }


def build_workbench_sandbox_run_response(
    request_payload: dict[str, Any],
) -> tuple[dict[str, Any], None]:
    """Build a sandbox run response for `/workbench`.

    Invalid model/scenario input is reported as a sandbox verdict instead of an
    authority-changing exception.
    """
    scenario_id = str(request_payload.get("scenario_id", "nominal_landing")).strip() or "nominal_landing"
    base_model = build_reference_editable_control_model()
    try:
        draft = _draft_object(request_payload)
        _ensure_draft_boundaries(draft)
        model = _apply_ui_draft(base_model, draft)
    except EditableControlModelValidationError as exc:
        model_hash = editable_control_model_hash(base_model)
        return (
            _invalid_response(
                scenario_id=scenario_id,
                verdict="invalid_model",
                message=str(exc),
                model_hash=model_hash,
            ),
            None,
        )

    model_hash = editable_control_model_hash(model)
    try:
        timeline = _load_timeline(scenario_id)
        diff_report = compare_editable_timeline_to_baseline(
            model,
            timeline,
            scenario_id=scenario_id,
        )
    except KeyError:
        return (
            _invalid_response(
                scenario_id=scenario_id,
                verdict="invalid_scenario",
                message=f"unsupported scenario_id {scenario_id!r}",
                model_hash=model_hash,
            ),
            None,
        )
    except (EditableControlModelValidationError, ValueError) as exc:
        return (
            _invalid_response(
                scenario_id=scenario_id,
                verdict="invalid_model",
                message=str(exc),
                model_hash=model_hash,
            ),
            None,
        )

    response = _base_response(
        scenario_id=scenario_id,
        verdict=diff_report["verdict"],
        model_hash=model_hash,
    )
    response.update(
        {
            "diff_report": diff_report,
            "summary": _build_summary(diff_report),
        }
    )
    return response, None

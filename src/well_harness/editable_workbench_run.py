"""Workbench-facing sandbox run orchestration.

This module turns a UI draft snapshot into a sandbox candidate run against a
fixed timeline fixture. It produces diff evidence only; it never changes
controller truth.
"""
from __future__ import annotations

import copy
import json
from dataclasses import replace
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
WORKBENCH_GRAPH_VALIDATION_REPORT_KIND = "well-harness-workbench-graph-validation-report"
WORKBENCH_GRAPH_VALIDATION_REPORT_VERSION = 1
GRAPH_VALIDATION_CATEGORIES = (
    "invalid_edge",
    "dangling_port",
    "duplicate_edge",
    "unsafe_op",
    "missing_node",
)
SUPPORTED_SCENARIOS = {
    "nominal_landing": "nominal_landing.json",
    "sw1_stuck_at_touchdown": "sw1_stuck_at_touchdown.json",
}
PORT_VALUE_TYPES = {"boolean", "number", "string", "state", "unknown"}
RULE_COMPARISONS = {
    "==",
    "!=",
    "<",
    "<=",
    ">",
    ">=",
    "between_lower_inclusive",
    "between_exclusive",
}


class WorkbenchGraphValidationError(EditableControlModelValidationError):
    """Validation error with structured graph evidence for `/workbench`."""

    def __init__(self, message: str, validation_report: dict[str, Any]) -> None:
        super().__init__(message)
        self.validation_report = validation_report


def _empty_validation_categories() -> dict[str, list[dict[str, Any]]]:
    return {category: [] for category in GRAPH_VALIDATION_CATEGORIES}


def _graph_validation_issue(
    *,
    category: str,
    code: str,
    message: str,
    severity: str = "error",
    node_id: str | None = None,
    edge_id: str | None = None,
    port_id: str | None = None,
    field: str | None = None,
) -> dict[str, Any]:
    if category not in GRAPH_VALIDATION_CATEGORIES:
        raise ValueError(f"unsupported graph validation category: {category}")
    issue: dict[str, Any] = {
        "category": category,
        "code": code,
        "severity": severity,
        "message": message,
    }
    optional_fields = {
        "node_id": node_id,
        "edge_id": edge_id,
        "port_id": port_id,
        "field": field,
    }
    for key, value in optional_fields.items():
        if value is not None:
            issue[key] = value
    return issue


def build_workbench_graph_validation_report(
    issues: list[dict[str, Any]] | None = None,
    *,
    status: str | None = None,
) -> dict[str, Any]:
    """Build a structured validation report for sandbox graph evidence."""
    normalized_issues = list(issues or [])
    categories = _empty_validation_categories()
    for issue in normalized_issues:
        categories[str(issue["category"])].append(issue)
    return {
        "kind": WORKBENCH_GRAPH_VALIDATION_REPORT_KIND,
        "version": WORKBENCH_GRAPH_VALIDATION_REPORT_VERSION,
        "status": status or ("fail" if normalized_issues else "pass"),
        "issue_count": len(normalized_issues),
        "categories": categories,
        "issues": normalized_issues,
        "truth_level_impact": "none",
    }


def _graph_validation_error(
    *,
    category: str,
    code: str,
    message: str,
    node_id: str | None = None,
    edge_id: str | None = None,
    port_id: str | None = None,
    field: str | None = None,
) -> WorkbenchGraphValidationError:
    issue = _graph_validation_issue(
        category=category,
        code=code,
        message=message,
        node_id=node_id,
        edge_id=edge_id,
        port_id=port_id,
        field=field,
    )
    return WorkbenchGraphValidationError(
        message,
        build_workbench_graph_validation_report([issue]),
    )


def _timeline_dir() -> Path:
    return Path(__file__).resolve().parent / "timelines"


def _load_timeline(scenario_id: str):
    filename = SUPPORTED_SCENARIOS.get(scenario_id)
    if filename is None:
        raise KeyError(scenario_id)
    payload = json.loads((_timeline_dir() / filename).read_text(encoding="utf-8"))
    return parse_timeline(payload)


def _scenario_metadata(
    scenario_id: str,
    *,
    custom_snapshot: dict[str, Any] | None = None,
    custom_snapshot_requested: bool = False,
) -> dict[str, Any]:
    snapshot = custom_snapshot or {}
    return {
        "scenario_id": scenario_id,
        "supported_scenarios": sorted(SUPPORTED_SCENARIOS),
        "custom_snapshot_applied": bool(custom_snapshot_requested),
        "custom_snapshot_keys": sorted(snapshot),
        "custom_snapshot_truth_effect": "none",
    }


def _custom_snapshot_object(request_payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    raw_snapshot = request_payload.get("custom_snapshot")
    if raw_snapshot is None or raw_snapshot == "":
        return {}, False
    if not isinstance(raw_snapshot, dict):
        raise EditableControlModelValidationError("custom_snapshot must be a JSON object")

    snapshot: dict[str, Any] = {}
    for key, value in raw_snapshot.items():
        signal_id = str(key).strip()
        if not signal_id:
            raise EditableControlModelValidationError("custom_snapshot input ids must be non-empty")
        if not isinstance(value, (bool, int, float)):
            raise EditableControlModelValidationError(
                f"custom_snapshot {signal_id!r} must be a boolean or number"
            )
        snapshot[signal_id] = value
    return snapshot, True


def _apply_custom_snapshot(timeline, custom_snapshot: dict[str, Any]):
    if not custom_snapshot:
        return timeline
    supported_inputs = set(timeline.initial_inputs)
    unsupported_inputs = sorted(set(custom_snapshot) - supported_inputs)
    if unsupported_inputs:
        raise EditableControlModelValidationError(
            f"custom_snapshot contains unsupported inputs: {unsupported_inputs}"
        )
    initial_inputs = dict(timeline.initial_inputs)
    initial_inputs.update(custom_snapshot)
    return replace(timeline, initial_inputs=initial_inputs)


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
    validation_report: dict[str, Any] | None = None,
    scenario_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = _base_response(
        scenario_id=scenario_id,
        verdict=verdict,
        model_hash=model_hash,
    )
    graph_report = validation_report or build_workbench_graph_validation_report(status="fail")
    response.update(
        {
            "error": message,
            "scenario_metadata": scenario_metadata or _scenario_metadata(scenario_id),
            "validation_report": graph_report,
            "summary": {
                "first_divergence": None,
                "assertion_status": "not_run",
                "frame_count": 0,
                "validation_issue_count": graph_report["issue_count"],
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


def _draft_node_id(raw: Any) -> str:
    node_id = str(raw or "").strip()
    if not node_id:
        raise EditableControlModelValidationError("draft node id is required")
    return node_id


def _draft_node_source_ref(update: dict[str, Any], node_id: str) -> str:
    source_ref = update.get("sourceRef", update.get("source_ref"))
    if source_ref is None:
        source_ref = f"ui_draft.nodes.{node_id}"
    return str(source_ref)


def _draft_rule_field(value: Any, *, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _draft_node_rule(
    rule: dict[str, Any],
    *,
    node_id: str,
    index: int,
) -> dict[str, Any]:
    if str(rule.get("truth_effect", "none")) != "none":
        raise EditableControlModelValidationError("draft rule truth_effect must be none")
    comparison = _draft_rule_field(rule.get("comparison"), default="==")
    if comparison not in RULE_COMPARISONS:
        raise _graph_validation_error(
            category="unsafe_op",
            code="unsupported_rule_comparison",
            message=f"draft node {node_id} rule comparison is not supported: {comparison}",
            node_id=node_id,
            field="comparison",
        )
    return {
        "name": _draft_rule_field(rule.get("name"), default=f"{node_id}_draft_rule_{index}"),
        "source_signal_id": _draft_rule_field(
            rule.get("source_signal_id", rule.get("sourceSignalId")),
            default=node_id,
        ),
        "comparison": comparison,
        "threshold_value": rule.get(
            "threshold_value",
            rule.get("thresholdValue", True),
        ),
    }


def _draft_node_rules(update: dict[str, Any], node_id: str) -> list[dict[str, Any]] | None:
    raw_rules = update.get("rules")
    if raw_rules is None:
        return None
    if not isinstance(raw_rules, list):
        raise EditableControlModelValidationError("draft node rules must be an array")
    rules: list[dict[str, Any]] = []
    for index, rule in enumerate(raw_rules, start=1):
        if not isinstance(rule, dict):
            raise EditableControlModelValidationError("draft node rules must be objects")
        rules.append(_draft_node_rule(rule, node_id=node_id, index=index))
    return rules


def _draft_node(update: dict[str, Any]) -> dict[str, Any]:
    node_id = _draft_node_id(update.get("id"))
    op = str(update.get("op", "and"))
    if op not in APPROVED_OPS:
        raise _graph_validation_error(
            category="unsafe_op",
            code="unsafe_op",
            message=f"draft node {node_id} op is not approved: {op}",
            node_id=node_id,
            field="op",
        )
    return {
        "id": node_id,
        "label": str(update.get("label") or node_id),
        "node_type": "logic",
        "op": op,
        "rules": _draft_node_rules(update, node_id) or [],
        "source_ref": _draft_node_source_ref(update, node_id),
        "editable": True,
    }


def _draft_port_field(value: Any, *, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _draft_port_value_type(value: Any, *, default: str = "boolean") -> str:
    text = str(value or "").strip()
    if text in PORT_VALUE_TYPES:
        return text
    return default if default in PORT_VALUE_TYPES else "unknown"


def _draft_port_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "required"}
    return bool(value)


def _draft_node_port_contract(update: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    contract = update.get("port_contract", update.get("portContract"))
    if contract is None:
        return None
    if not isinstance(contract, dict):
        raise EditableControlModelValidationError("port_contract must be an object")
    if str(contract.get("truth_effect", "none")) != "none":
        raise EditableControlModelValidationError("port_contract truth_effect must be none")
    return {
        "input_port_id": _draft_port_field(
            contract.get("input_port_id", contract.get("inputPortId")),
            default=f"{node_id}:in",
        ),
        "output_port_id": _draft_port_field(
            contract.get("output_port_id", contract.get("outputPortId")),
            default=f"{node_id}:out",
        ),
        "input_signal_id": _draft_port_field(
            contract.get("input_signal_id", contract.get("inputSignalId")),
            default=node_id,
        ),
        "output_signal_id": _draft_port_field(
            contract.get("output_signal_id", contract.get("outputSignalId")),
            default=node_id,
        ),
        "value_type": _draft_port_value_type(
            contract.get("value_type", contract.get("valueType")),
        ),
        "unit": str(contract.get("unit", "") or "").strip(),
        "required": _draft_port_bool(contract.get("required")),
    }


def _port_payload(
    *,
    port_id: str,
    node_id: str,
    direction: str,
    signal_id: str,
    value_type: str,
    unit: str,
    required: bool,
) -> dict[str, Any]:
    return {
        "id": port_id,
        "node_id": node_id,
        "direction": direction,
        "signal_id": signal_id,
        "value_type": value_type,
        "unit": unit,
        "required": required,
    }


def _draft_node_ports(
    node_id: str,
    contract: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    normalized = contract or {
        "input_port_id": f"{node_id}:in",
        "output_port_id": f"{node_id}:out",
        "input_signal_id": node_id,
        "output_signal_id": node_id,
        "value_type": "boolean",
        "unit": "",
        "required": False,
    }
    return [
        _port_payload(
            port_id=normalized["input_port_id"],
            node_id=node_id,
            direction="in",
            signal_id=normalized["input_signal_id"],
            value_type=normalized["value_type"],
            unit=normalized["unit"],
            required=normalized["required"],
        ),
        _port_payload(
            port_id=normalized["output_port_id"],
            node_id=node_id,
            direction="out",
            signal_id=normalized["output_signal_id"],
            value_type=normalized["value_type"],
            unit=normalized["unit"],
            required=normalized["required"],
        ),
    ]


def _has_port(model: dict[str, Any], port_id: str) -> bool:
    return any(port["id"] == port_id for port in model["ports"])


def _upsert_ui_port(model: dict[str, Any], port: dict[str, Any]) -> None:
    for existing in model["ports"]:
        if existing["id"] == port["id"]:
            existing.update(port)
            return
    model["ports"].append(port)


def _apply_node_port_contract(
    model: dict[str, Any],
    *,
    node_id: str,
    contract: dict[str, Any] | None,
) -> None:
    if contract is None:
        return
    for port in _draft_node_ports(node_id, contract):
        _upsert_ui_port(model, port)


def _apply_ui_typed_ports(model: dict[str, Any], draft: dict[str, Any]) -> None:
    node_ids = {node["id"] for node in model["nodes"]}
    candidates = []
    for key in ("typed_ports", "typedPorts"):
        raw_ports = draft.get(key)
        if isinstance(raw_ports, list):
            candidates.extend(raw_ports)
    for port in candidates:
        if not isinstance(port, dict):
            continue
        node_id = str(port.get("node_id", port.get("nodeId", ""))).strip()
        port_id = str(port.get("id", "")).strip()
        signal_id = str(port.get("signal_id", port.get("signalId", ""))).strip()
        direction = str(port.get("direction", "")).strip()
        if not node_id or node_id not in node_ids or not port_id or not signal_id:
            continue
        if direction not in {"in", "out"}:
            continue
        _upsert_ui_port(
            model,
            _port_payload(
                port_id=port_id,
                node_id=node_id,
                direction=direction,
                signal_id=signal_id,
                value_type=_draft_port_value_type(
                    port.get("value_type", port.get("valueType")),
                    default="unknown",
                ),
                unit=str(port.get("unit", "") or "").strip(),
                required=_draft_port_bool(port.get("required")),
            ),
        )


def _ensure_ui_target_port(model: dict[str, Any], *, source_node_id: str, target_node_id: str) -> str:
    preferred_port_id = f"{target_node_id}:in"
    if _has_port(model, preferred_port_id):
        return preferred_port_id
    port_id = f"{target_node_id}:in:ui_edge:{source_node_id}"
    if not _has_port(model, port_id):
        model["ports"].append(
            {
                "id": port_id,
                "node_id": target_node_id,
                "direction": "in",
                "signal_id": target_node_id,
                "value_type": "boolean",
                "unit": "",
                "required": False,
            }
        )
    return port_id


def _draft_binding_field(value: Any, *, default: str = "evidence_gap") -> str:
    text = str(value or "").strip()
    return text or default


def _draft_binding_status(value: Any) -> str:
    status = _draft_binding_field(value)
    if status in {"evidence_gap", "ui_draft", "not_recorded"}:
        return status
    return "evidence_gap"


def _draft_hardware_binding(
    *,
    model: dict[str, Any],
    binding: dict[str, Any],
    owner_kind: str,
    owner_id: str,
    index: int,
) -> dict[str, Any]:
    port_local = _draft_binding_field(
        binding.get("port_local", binding.get("portLocal"))
    )
    port_id: str | None = port_local if _has_port(model, port_local) else None
    return {
        "id": _draft_binding_field(
            binding.get("id"),
            default=f"ui-hardware-binding:{owner_kind}:{owner_id}:{index}",
        ),
        "signal_id": _draft_binding_field(binding.get("signal_id"), default=owner_id),
        "port_id": port_id,
        "hardware_id": _draft_binding_field(
            binding.get("hardware_id", binding.get("hardwareId"))
        ),
        "binding_kind": _draft_binding_field(
            binding.get("binding_kind"), default="ui_interface_binding"
        ),
        "evidence_status": _draft_binding_status(
            binding.get("evidence_status", binding.get("evidenceStatus"))
        ),
        "truth_effect": "none",
        "source_ref": _draft_binding_field(
            binding.get("source_ref", binding.get("sourceRef")),
            default="ui_draft.interface_binding",
        ),
        "owner_kind": owner_kind,
        "owner_id": owner_id,
        "cable": _draft_binding_field(binding.get("cable")),
        "connector": _draft_binding_field(binding.get("connector")),
        "port_local": port_local,
        "port_peer": _draft_binding_field(
            binding.get("port_peer", binding.get("portPeer"))
        ),
    }


def _binding_has_ui_evidence(binding: dict[str, Any]) -> bool:
    return binding["evidence_status"] == "ui_draft" or any(
        binding[field_name] != "evidence_gap"
        for field_name in (
            "hardware_id",
            "cable",
            "connector",
            "port_local",
            "port_peer",
        )
    )


def _apply_ui_hardware_bindings(model: dict[str, Any], draft: dict[str, Any]) -> None:
    seen_ids = {binding["id"] for binding in model["hardware_bindings"]}
    next_index = 1
    sources: list[tuple[dict[str, Any], str, str]] = []
    for node in draft.get("nodes", []):
        if not isinstance(node, dict):
            continue
        binding = node.get("hardware_binding", node.get("hardwareBinding"))
        if isinstance(binding, dict):
            sources.append(
                (
                    binding,
                    "node",
                    _draft_binding_field(node.get("id"), default="unknown_node"),
                )
            )
    for edge in draft.get("edges", []):
        if not isinstance(edge, dict):
            continue
        binding = edge.get("hardware_binding", edge.get("hardwareBinding"))
        if isinstance(binding, dict):
            owner_id = _draft_binding_field(
                edge.get("id"),
                default=f"{edge.get('source', 'unknown')}->{edge.get('target', 'unknown')}",
            )
            sources.append((binding, "edge", owner_id))
    for binding in draft.get("hardware_bindings", []):
        if not isinstance(binding, dict):
            continue
        owner_kind = _draft_binding_field(
            binding.get("owner_kind", binding.get("ownerKind")),
            default="draft",
        )
        owner_id = _draft_binding_field(
            binding.get("owner_id", binding.get("ownerId")),
            default=f"binding_{next_index}",
        )
        sources.append((binding, owner_kind, owner_id))

    for source, owner_kind, owner_id in sources:
        binding = _draft_hardware_binding(
            model=model,
            binding=source,
            owner_kind=owner_kind,
            owner_id=owner_id,
            index=next_index,
        )
        next_index += 1
        if binding["id"] in seen_ids or not _binding_has_ui_evidence(binding):
            continue
        seen_ids.add(binding["id"])
        model["hardware_bindings"].append(binding)


def _apply_ui_edges(model: dict[str, Any], draft: dict[str, Any]) -> None:
    node_ids = {node["id"] for node in model["nodes"]}
    for index, edge in enumerate(draft.get("edges", []), start=1):
        edge_id = f"edge[{index}]"
        if not isinstance(edge, dict):
            raise _graph_validation_error(
                category="invalid_edge",
                code="invalid_edge",
                message="draft edges must be objects",
                edge_id=edge_id,
            )
        source_node_id = str(edge.get("source", "")).strip()
        target_node_id = str(edge.get("target", "")).strip()
        edge_id = str(edge.get("id") or f"{source_node_id}_{target_node_id}_{index}").strip()
        if not source_node_id:
            raise _graph_validation_error(
                category="invalid_edge",
                code="invalid_edge",
                message=f"draft edge {edge_id!r} is missing source node",
                edge_id=edge_id,
                field="source",
            )
        if not target_node_id:
            raise _graph_validation_error(
                category="invalid_edge",
                code="invalid_edge",
                message=f"draft edge {edge_id!r} is missing target node",
                edge_id=edge_id,
                field="target",
            )
        if source_node_id not in node_ids:
            raise _graph_validation_error(
                category="missing_node",
                code="missing_source_node",
                message=f"draft edge {edge_id!r} references missing source node {source_node_id!r}",
                node_id=source_node_id,
                edge_id=edge_id,
                field="source",
            )
        if target_node_id not in node_ids:
            raise _graph_validation_error(
                category="missing_node",
                code="missing_target_node",
                message=f"draft edge {edge_id!r} references missing target node {target_node_id!r}",
                node_id=target_node_id,
                edge_id=edge_id,
                field="target",
            )
        edge_signal_id = _draft_port_field(
            edge.get("signal_id", edge.get("signalId")),
            default=f"{source_node_id}__to__{target_node_id}",
        )
        edge_value_type = _draft_port_value_type(
            edge.get("value_type", edge.get("valueType")),
        )
        edge_unit = str(edge.get("unit", "") or "").strip()
        edge_required = _draft_port_bool(edge.get("required"))
        raw_source_port_id = edge.get("source_port_id", edge.get("sourcePortId"))
        has_explicit_source_port = bool(str(raw_source_port_id or "").strip())
        source_port_id = _draft_port_field(
            raw_source_port_id,
            default=f"{source_node_id}:out",
        )
        if not _has_port(model, source_port_id):
            if has_explicit_source_port and source_port_id.startswith(f"{source_node_id}:"):
                _upsert_ui_port(
                    model,
                    _port_payload(
                        port_id=source_port_id,
                        node_id=source_node_id,
                        direction="out",
                        signal_id=edge_signal_id,
                        value_type=edge_value_type,
                        unit=edge_unit,
                        required=edge_required,
                    ),
                )
            else:
                raise _graph_validation_error(
                    category="dangling_port",
                    code="missing_source_port",
                    message=f"draft edge {edge_id!r} references missing source port {source_port_id!r}",
                    node_id=source_node_id,
                    edge_id=edge_id,
                    port_id=source_port_id,
                    field="source_port_id",
                )
        raw_target_port_id = edge.get("target_port_id", edge.get("targetPortId"))
        if raw_target_port_id:
            target_port_id = _draft_port_field(raw_target_port_id, default="")
            if not _has_port(model, target_port_id):
                if target_port_id.startswith(f"{target_node_id}:"):
                    _upsert_ui_port(
                        model,
                        _port_payload(
                            port_id=target_port_id,
                            node_id=target_node_id,
                            direction="in",
                            signal_id=edge_signal_id,
                            value_type=edge_value_type,
                            unit=edge_unit,
                            required=edge_required,
                        ),
                    )
                else:
                    raise _graph_validation_error(
                        category="dangling_port",
                        code="missing_target_port",
                        message=f"draft edge {edge_id!r} references missing target port {target_port_id!r}",
                        node_id=target_node_id,
                        edge_id=edge_id,
                        port_id=target_port_id,
                        field="target_port_id",
                    )
        else:
            target_port_id = _ensure_ui_target_port(
                model,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
            )
        canonical_edge_id = f"ui-edge:{edge_id}"
        if any(existing["id"] == canonical_edge_id for existing in model["edges"]):
            raise _graph_validation_error(
                category="duplicate_edge",
                code="duplicate_edge",
                message=f"duplicate draft edge id {canonical_edge_id!r}",
                edge_id=edge_id,
                field="id",
            )
        model["edges"].append(
            {
                "id": canonical_edge_id,
                "source_port_id": source_port_id,
                "target_port_id": target_port_id,
                "edge_type": "evidence_only",
                "evidence_only": True,
            }
        )


def canonicalize_workbench_ui_draft(base_model: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    """Convert a `/workbench` UI draft into editable_control_model_v1.

    The conversion preserves UI-only nodes/edges as sandbox evidence. It does
    not modify controller truth, adapter truth, or hardware truth.
    """
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
        node_id = _draft_node_id(update.get("id"))
        port_contract = _draft_node_port_contract(update, node_id)
        node = nodes.get(node_id)
        if node is None:
            node = _draft_node(update)
            model["nodes"].append(node)
            model["ports"].extend(_draft_node_ports(node_id, port_contract))
            nodes[node_id] = node
            continue
        _apply_node_port_contract(model, node_id=node_id, contract=port_contract)
        if "label" in update:
            node["label"] = str(update["label"])
        if "op" in update and update["op"] is not None:
            op = str(update["op"])
            if op not in APPROVED_OPS:
                raise _graph_validation_error(
                    category="unsafe_op",
                    code="unsafe_op",
                    message=f"draft node {node_id} op is not approved: {op}",
                    node_id=node_id,
                    field="op",
                )
            node["op"] = op
        draft_rules = _draft_node_rules(update, node_id)
        if draft_rules is not None:
            node["rules"] = draft_rules
    _apply_ui_typed_ports(model, draft)
    _apply_ui_edges(model, draft)
    _apply_ui_hardware_bindings(model, draft)
    source_refs = model["evidence_metadata"].setdefault("source_refs", [])
    if "ui_draft.workbench" not in source_refs:
        source_refs.append("ui_draft.workbench")
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
        model = canonicalize_workbench_ui_draft(base_model, draft)
    except EditableControlModelValidationError as exc:
        model_hash = editable_control_model_hash(base_model)
        return (
            _invalid_response(
                scenario_id=scenario_id,
                verdict="invalid_model",
                message=str(exc),
                model_hash=model_hash,
                validation_report=getattr(exc, "validation_report", None),
            ),
            None,
        )

    model_hash = editable_control_model_hash(model)
    custom_snapshot: dict[str, Any] = {}
    custom_snapshot_requested = False
    scenario_metadata = _scenario_metadata(scenario_id)
    try:
        custom_snapshot, custom_snapshot_requested = _custom_snapshot_object(request_payload)
        scenario_metadata = _scenario_metadata(
            scenario_id,
            custom_snapshot=custom_snapshot,
            custom_snapshot_requested=custom_snapshot_requested,
        )
        timeline = _load_timeline(scenario_id)
        timeline = _apply_custom_snapshot(timeline, custom_snapshot)
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
                scenario_metadata=scenario_metadata,
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
                scenario_metadata=scenario_metadata,
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
            "canonical_model_hash": model_hash,
            "canonical_model": model,
            "scenario_metadata": scenario_metadata,
            "validation_report": build_workbench_graph_validation_report(),
            "diff_report": diff_report,
            "summary": _build_summary(diff_report),
        }
    )
    return response, None

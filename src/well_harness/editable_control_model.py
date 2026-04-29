"""Editable control model contracts for sandbox workbench drafts.

The editable model is an engineering candidate graph. It is never the
certified control truth and must be compared against adapter/controller
baselines before a ChangeRequest can be reviewed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.controller_adapter import (
    REFERENCE_DEPLOY_CONTROLLER_METADATA,
    build_reference_controller_adapter,
)
from well_harness.hardware_registry import build_timeline_hardware_evidence_overlay
from well_harness.system_spec import current_reference_workbench_spec


EDITABLE_CONTROL_MODEL_SCHEMA_ID = (
    "https://well-harness.local/json_schema/editable_control_model_v1.schema.json"
)
EDITABLE_CONTROL_MODEL_DIFF_SCHEMA_ID = (
    "https://well-harness.local/json_schema/editable_control_model_diff_v1.schema.json"
)
EDITABLE_CONTROL_MODEL_KIND = "well-harness-editable-control-model"
EDITABLE_CONTROL_MODEL_DIFF_KIND = "well-harness-editable-control-model-diff"
EDITABLE_CONTROL_MODEL_VERSION = 1
APPROVED_OPS = ("and", "or", "compare", "between", "delay", "latch")
OP_CATALOG_VERSION = "editable-control-ops.v1"
REFERENCE_MODEL_ID = "thrust-reverser-derived-view-v1"


class EditableControlModelValidationError(ValueError):
    """Raised when an editable model violates sandbox contract rules."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema(name: str) -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(payload: dict[str, Any], schema_name: str) -> None:
    schema = _load_schema(schema_name)
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise EditableControlModelValidationError(
            f"schema validation failed{location}: {exc.message}"
        ) from exc


def _unique_ids(items: list[dict[str, Any]], field_name: str, label: str) -> set[str]:
    ids: list[str] = [str(item[field_name]) for item in items]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise EditableControlModelValidationError(f"duplicate {label} ids: {duplicates}")
    return set(ids)


def validate_editable_control_model(payload: dict[str, Any]) -> None:
    """Validate schema plus cross-reference invariants for sandbox models."""
    _schema_validate(payload, "editable_control_model_v1.schema.json")

    if payload["truth_status"] != "sandbox_candidate":
        raise EditableControlModelValidationError("truth_status must be sandbox_candidate")

    node_ids = _unique_ids(payload["nodes"], "id", "node")
    ports_by_id = {port["id"]: port for port in payload["ports"]}
    if len(ports_by_id) != len(payload["ports"]):
        raise EditableControlModelValidationError("duplicate port ids")
    _unique_ids(payload["edges"], "id", "edge")
    _unique_ids(payload["hardware_bindings"], "id", "hardware binding")

    for port in payload["ports"]:
        if port["node_id"] not in node_ids:
            raise EditableControlModelValidationError(
                f"port {port['id']} references missing node_id {port['node_id']}"
            )

    for edge in payload["edges"]:
        source = ports_by_id.get(edge["source_port_id"])
        if source is None:
            raise EditableControlModelValidationError(
                f"edge {edge['id']} references missing source_port_id {edge['source_port_id']}"
            )
        target = ports_by_id.get(edge["target_port_id"])
        if target is None:
            raise EditableControlModelValidationError(
                f"edge {edge['id']} references missing target_port_id {edge['target_port_id']}"
            )
        if source["direction"] != "out" or target["direction"] != "in":
            raise EditableControlModelValidationError(
                f"edge {edge['id']} must connect out -> in ports"
            )

    for binding in payload["hardware_bindings"]:
        if binding["truth_effect"] != "none":
            raise EditableControlModelValidationError(
                f"hardware binding {binding['id']} truth_effect must be none"
            )
        port_id = binding.get("port_id")
        if port_id is not None and port_id not in ports_by_id:
            raise EditableControlModelValidationError(
                f"hardware binding {binding['id']} references missing port_id {port_id}"
            )
    for node in payload["nodes"]:
        op = node.get("op")
        if op is not None and op not in APPROVED_OPS:
            raise EditableControlModelValidationError(f"node {node['id']} op is not approved: {op}")


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def editable_control_model_hash(payload: dict[str, Any]) -> str:
    """Return a deterministic hash for model provenance and diff reports."""
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _value_type_for_component(component: Any) -> str:
    if component.allowed_states:
        return "state"
    if component.allowed_range is not None:
        return "number"
    if component.state_shape == "bool":
        return "boolean"
    return "unknown"


def _component_node_type(component_id: str, downstream_component_ids: set[str]) -> str:
    if component_id in downstream_component_ids:
        return "output"
    if component_id in {"deploy_position_percent", "deploy_90_percent_vdt"}:
        return "plant_observer"
    return "input"


def _component_ports(component: Any) -> list[dict[str, Any]]:
    value_type = _value_type_for_component(component)
    return [
        {
            "id": f"{component.id}:in",
            "node_id": component.id,
            "direction": "in",
            "signal_id": component.id,
            "value_type": value_type,
            "unit": component.unit,
            "required": False,
        },
        {
            "id": f"{component.id}:out",
            "node_id": component.id,
            "direction": "out",
            "signal_id": component.id,
            "value_type": value_type,
            "unit": component.unit,
            "required": component.monitor_priority == "required",
        },
    ]


def _virtual_signal_node(signal_id: str) -> dict[str, Any]:
    return {
        "id": signal_id,
        "label": signal_id,
        "node_type": "input",
        "op": None,
        "rules": [],
        "source_ref": "control_system_spec.logic_conditions.virtual_signal",
        "editable": True,
    }


def _virtual_signal_ports(signal_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{signal_id}:in",
            "node_id": signal_id,
            "direction": "in",
            "signal_id": signal_id,
            "value_type": "unknown",
            "unit": "",
            "required": False,
        },
        {
            "id": f"{signal_id}:out",
            "node_id": signal_id,
            "direction": "out",
            "signal_id": signal_id,
            "value_type": "unknown",
            "unit": "",
            "required": True,
        },
    ]


def _logic_condition_port(logic_node: Any, condition: Any) -> dict[str, Any]:
    value_type = "boolean" if isinstance(condition.threshold_value, bool) else "unknown"
    if isinstance(condition.threshold_value, (int, float)):
        value_type = "number"
    if isinstance(condition.threshold_value, str):
        value_type = "string"
    return {
        "id": f"{logic_node.id}:in:{condition.name}",
        "node_id": logic_node.id,
        "direction": "in",
        "signal_id": condition.source_component_id,
        "value_type": value_type,
        "unit": "",
        "required": True,
    }


def _logic_condition_rule(condition: Any) -> dict[str, Any]:
    return {
        "name": condition.name,
        "source_signal_id": condition.source_component_id,
        "comparison": condition.comparison,
        "threshold_value": condition.threshold_value,
    }


def _logic_node_rules(logic_node: Any) -> list[dict[str, Any]]:
    rules = [_logic_condition_rule(condition) for condition in logic_node.conditions]
    if logic_node.id == "logic2" and not any(
        rule["name"] == "sw2_hysteresis_tra_deg" for rule in rules
    ):
        rules.append(
            {
                "name": "sw2_hysteresis_tra_deg",
                "source_signal_id": "tra_deg",
                "comparison": "<=",
                "threshold_value": -5.5,
            }
        )
    return rules


def build_reference_editable_control_model() -> dict[str, Any]:
    """Build a derived editable seed from the certified thrust-reverser adapter.

    The seed is a sandbox candidate view. It is useful for editing and diff
    preparation, but certified truth still comes from the adapter/controller.
    """
    spec = current_reference_workbench_spec()
    downstream_component_ids = {
        component_id
        for logic_node in spec.logic_nodes
        for component_id in logic_node.downstream_component_ids
    }
    nodes: list[dict[str, Any]] = []
    ports: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    known_node_ids: set[str] = set()

    for component in spec.components:
        nodes.append(
            {
                "id": component.id,
                "label": component.label,
                "node_type": _component_node_type(component.id, downstream_component_ids),
                "op": None,
                "rules": [],
                "source_ref": "control_system_spec.components",
                "editable": True,
            }
        )
        known_node_ids.add(component.id)
        ports.extend(_component_ports(component))

    for logic_node in spec.logic_nodes:
        nodes.append(
            {
                "id": logic_node.id,
                "label": logic_node.label,
                "node_type": "logic",
                "op": "and",
                "rules": _logic_node_rules(logic_node),
                "source_ref": "control_system_spec.logic_nodes",
                "editable": True,
            }
        )
        known_node_ids.add(logic_node.id)
        for condition in logic_node.conditions:
            if condition.source_component_id not in known_node_ids:
                nodes.append(_virtual_signal_node(condition.source_component_id))
                ports.extend(_virtual_signal_ports(condition.source_component_id))
                known_node_ids.add(condition.source_component_id)
            input_port = _logic_condition_port(logic_node, condition)
            ports.append(input_port)
            edges.append(
                {
                    "id": f"edge:{condition.source_component_id}:out->{input_port['id']}",
                    "source_port_id": f"{condition.source_component_id}:out",
                    "target_port_id": input_port["id"],
                    "edge_type": "input_flow",
                    "evidence_only": False,
                }
            )
        ports.append(
            {
                "id": f"{logic_node.id}:out",
                "node_id": logic_node.id,
                "direction": "out",
                "signal_id": logic_node.id,
                "value_type": "boolean",
                "unit": "",
                "required": True,
            }
        )
        for component_id in logic_node.downstream_component_ids:
            edges.append(
                {
                    "id": f"edge:{logic_node.id}:out->{component_id}:in",
                    "source_port_id": f"{logic_node.id}:out",
                    "target_port_id": f"{component_id}:in",
                    "edge_type": "command_flow",
                    "evidence_only": False,
                }
            )

    port_by_signal = {
        port["signal_id"]: port["id"]
        for port in ports
        if port["direction"] == "out"
    }
    hardware_overlay = build_timeline_hardware_evidence_overlay("thrust-reverser")
    hardware_bindings = [
        {
            "id": f"hardware-binding:{binding['signal_id']}",
            "signal_id": binding["signal_id"],
            "port_id": port_by_signal.get(binding["signal_id"]),
            "hardware_id": binding["source_hardware_id"],
            "binding_kind": "signal_carrier",
            "evidence_status": binding["evidence_status"],
            "truth_effect": "none",
            "source_ref": binding["source_ref"],
        }
        for binding in hardware_overlay["signal_bindings"]
    ]

    scenarios = [
        {
            "id": scenario.id,
            "label": scenario.label,
            "description": scenario.description,
            "timeline_ref": None,
        }
        for scenario in spec.acceptance_scenarios
    ]

    payload = {
        "$schema": EDITABLE_CONTROL_MODEL_SCHEMA_ID,
        "kind": EDITABLE_CONTROL_MODEL_KIND,
        "version": EDITABLE_CONTROL_MODEL_VERSION,
        "model_id": REFERENCE_MODEL_ID,
        "system_id": "thrust-reverser",
        "truth_status": "sandbox_candidate",
        "view_status": "derived_view",
        "source_of_truth": REFERENCE_DEPLOY_CONTROLLER_METADATA.source_of_truth,
        "nodes": nodes,
        "ports": ports,
        "edges": edges,
        "hardware_bindings": hardware_bindings,
        "scenarios": scenarios,
        "evidence_metadata": {
            "baseline_adapter_id": REFERENCE_DEPLOY_CONTROLLER_METADATA.adapter_id,
            "baseline_truth_level": REFERENCE_DEPLOY_CONTROLLER_METADATA.truth_level or "unclassified",
            "sample_pack_role": "reference_sample_pack",
            "source_refs": [
                "src/well_harness/controller.py",
                "src/well_harness/system_spec.py",
                "config/hardware/thrust_reverser_hardware_v1.yaml",
            ],
        },
        "boundaries": {
            "runtime_scope": "sandbox_only",
            "controller_truth_modified": False,
            "truth_level_impact": "none",
            "dal_pssa_impact": "none",
            "hardware_truth_effect": "none",
        },
    }
    validate_editable_control_model(payload)
    return payload


def build_editable_control_model_diff_report(
    *,
    baseline_model: dict[str, Any],
    candidate_model: dict[str, Any],
    scenario_id: str,
    verdict: str,
    first_divergence: dict[str, Any] | None = None,
    per_signal_delta: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a schema-shaped diff report between sandbox candidate models."""
    report = {
        "$schema": EDITABLE_CONTROL_MODEL_DIFF_SCHEMA_ID,
        "kind": EDITABLE_CONTROL_MODEL_DIFF_KIND,
        "version": EDITABLE_CONTROL_MODEL_VERSION,
        "baseline_run": {
            "model_id": baseline_model["model_id"],
            "model_hash": editable_control_model_hash(baseline_model),
            "system_id": baseline_model["system_id"],
            "truth_status": baseline_model["truth_status"],
            "source_of_truth": baseline_model["source_of_truth"],
        },
        "candidate_run": {
            "model_id": candidate_model["model_id"],
            "model_hash": editable_control_model_hash(candidate_model),
            "system_id": candidate_model["system_id"],
            "truth_status": candidate_model["truth_status"],
            "source_of_truth": candidate_model["source_of_truth"],
        },
        "scenario_result": {
            "scenario_id": scenario_id,
            "assertion_status": "not_run",
            "frame_count": 0,
        },
        "first_divergence": first_divergence,
        "per_signal_delta": per_signal_delta or [],
        "hardware_evidence": {
            "truth_effect": "none",
            "binding_count": len(candidate_model.get("hardware_bindings", [])),
            "evidence_gap_count": sum(
                1
                for binding in candidate_model.get("hardware_bindings", [])
                if binding.get("evidence_status") == "evidence_gap"
            ),
        },
        "verdict": verdict,
    }
    return report


def validate_editable_control_model_diff_report(payload: dict[str, Any]) -> None:
    """Validate a diff report and guard against candidate certification claims."""
    _schema_validate(payload, "editable_control_model_diff_v1.schema.json")
    if payload["candidate_run"]["truth_status"] != "sandbox_candidate":
        raise EditableControlModelValidationError(
            "candidate_run.truth_status must be sandbox_candidate"
        )
    if payload["hardware_evidence"]["truth_effect"] != "none":
        raise EditableControlModelValidationError("hardware_evidence truth_effect must be none")


def _threshold_value(raw_threshold: Any, signals: dict[str, Any]) -> Any:
    if isinstance(raw_threshold, str) and raw_threshold in signals:
        return signals[raw_threshold]
    return raw_threshold


def _evaluate_rule(rule: dict[str, Any], signals: dict[str, Any]) -> tuple[bool, Any, Any]:
    signal_id = rule["source_signal_id"]
    if signal_id not in signals:
        raise EditableControlModelValidationError(f"snapshot missing signal {signal_id}")
    current_value = signals[signal_id]
    threshold = _threshold_value(rule["threshold_value"], signals)
    comparison = rule["comparison"]
    if comparison == "==":
        return current_value == threshold, current_value, threshold
    if comparison == "!=":
        return current_value != threshold, current_value, threshold
    if comparison == "<":
        return current_value < threshold, current_value, threshold
    if comparison == "<=":
        return current_value <= threshold, current_value, threshold
    if comparison == ">":
        return current_value > threshold, current_value, threshold
    if comparison == ">=":
        return current_value >= threshold, current_value, threshold
    if comparison == "between_lower_inclusive":
        lower, upper = threshold
        return lower <= current_value < upper, current_value, threshold
    if comparison == "between_exclusive":
        lower, upper = threshold
        return lower < current_value < upper, current_value, threshold
    raise EditableControlModelValidationError(f"unsupported comparison {comparison}")


def evaluate_editable_snapshot(
    model: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one sandbox candidate graph snapshot.

    This evaluator is intentionally small and deterministic. It produces a
    candidate result for comparison; it is not certified control truth.
    """
    validate_editable_control_model(model)
    signals = dict(snapshot)
    asserted_component_values: dict[str, Any] = dict(snapshot)
    active_logic_node_ids: list[str] = []
    blocked_reasons: list[str] = []
    logic_states: dict[str, dict[str, Any]] = {}
    port_by_id = {port["id"]: port for port in model["ports"]}

    for node in model["nodes"]:
        if node["node_type"] != "logic":
            continue
        op = node["op"]
        if op not in ("and", "or"):
            raise EditableControlModelValidationError(
                f"snapshot evaluator only supports and/or logic nodes, got op {op}"
            )
        rule_results = []
        failed_rules = []
        for rule in node["rules"]:
            passed, current_value, threshold = _evaluate_rule(rule, signals)
            rule_results.append(passed)
            if not passed:
                failed_rules.append(
                    {
                        "name": rule["name"],
                        "current_value": current_value,
                        "comparison": rule["comparison"],
                        "threshold_value": threshold,
                    }
                )
        active = all(rule_results) if op == "and" else any(rule_results)
        signals[node["id"]] = active
        asserted_component_values[node["id"]] = active
        logic_states[node["id"]] = {
            "state": "active" if active else "blocked",
            "failed_rules": failed_rules,
        }
        if active:
            active_logic_node_ids.append(node["id"])
        else:
            blocked_reasons.extend(f"{node['id']}:{rule['name']}" for rule in failed_rules)

        source_port_id = f"{node['id']}:out"
        for edge in model["edges"]:
            if edge["source_port_id"] != source_port_id:
                continue
            target_signal = port_by_id[edge["target_port_id"]]["signal_id"]
            signals[target_signal] = active
            asserted_component_values[target_signal] = active

    return {
        "model_id": model["model_id"],
        "model_hash": editable_control_model_hash(model),
        "system_id": model["system_id"],
        "truth_status": model["truth_status"],
        "op_catalog_version": OP_CATALOG_VERSION,
        "active_logic_node_ids": active_logic_node_ids,
        "asserted_component_values": asserted_component_values,
        "completion_reached": bool(asserted_component_values.get("logic4")),
        "blocked_reasons": blocked_reasons,
        "logic_states": logic_states,
    }


def _logic_delta(signal_id: str, baseline_active_ids: set[str], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_value = signal_id in baseline_active_ids
    candidate_value = bool(candidate["asserted_component_values"].get(signal_id))
    return {
        "signal_id": signal_id,
        "status": "same" if baseline_value == candidate_value else "different",
        "_baseline_value": baseline_value,
        "_candidate_value": candidate_value,
    }


def compare_editable_snapshot_to_baseline(
    model: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Compare one sandbox candidate snapshot against certified baseline adapter."""
    candidate = evaluate_editable_snapshot(model, snapshot)
    baseline = build_reference_controller_adapter().evaluate_snapshot(snapshot)
    baseline_active_ids = set(baseline.active_logic_node_ids)
    raw_deltas = [
        _logic_delta(signal_id, baseline_active_ids, candidate)
        for signal_id in ("logic1", "logic2", "logic3", "logic4")
    ]
    first_divergence = None
    for delta in raw_deltas:
        if delta["status"] == "different":
            first_divergence = {
                "at_s": 0.0,
                "signal_id": delta["signal_id"],
                "baseline_value": delta["_baseline_value"],
                "candidate_value": delta["_candidate_value"],
            }
            break
    report = build_editable_control_model_diff_report(
        baseline_model={
            **model,
            "model_id": REFERENCE_DEPLOY_CONTROLLER_METADATA.adapter_id,
            "truth_status": REFERENCE_DEPLOY_CONTROLLER_METADATA.truth_level or "certified",
            "source_of_truth": REFERENCE_DEPLOY_CONTROLLER_METADATA.source_of_truth,
        },
        candidate_model=model,
        scenario_id="snapshot-default",
        verdict="divergent" if first_divergence else "equivalent",
        first_divergence=first_divergence,
        per_signal_delta=[
            {"signal_id": delta["signal_id"], "status": delta["status"]}
            for delta in raw_deltas
        ],
    )
    validate_editable_control_model_diff_report(report)
    return report

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

from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
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
    for field_name in ("baseline_run", "candidate_run"):
        truth_status = payload[field_name]["truth_status"]
        if truth_status != "sandbox_candidate":
            raise EditableControlModelValidationError(
                f"{field_name}.truth_status must be sandbox_candidate"
            )
    if payload["hardware_evidence"]["truth_effect"] != "none":
        raise EditableControlModelValidationError("hardware_evidence truth_effect must be none")

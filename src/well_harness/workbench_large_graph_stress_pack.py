from __future__ import annotations

import copy
from typing import Any


LARGE_GRAPH_STRESS_PACK_KIND = "well-harness-workbench-large-graph-stress-pack"
LARGE_GRAPH_STRESS_PACK_VERSION = "workbench-large-graph-stress-pack.v1"
LARGE_GRAPH_DEFAULT_NODE_COUNT = 16
LARGE_GRAPH_INVALID_NODE_COUNT = 12
LARGE_GRAPH_STALE_REPORT_MODEL_HASH = "ui_draft_stale_large_graph_report"


def large_sandbox_chain_draft(base: dict[str, Any], node_count: int = LARGE_GRAPH_DEFAULT_NODE_COUNT) -> dict[str, Any]:
    if node_count < 3:
        raise ValueError("large sandbox chain requires at least 3 nodes.")

    draft = copy.deepcopy(base)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for index in range(1, node_count + 1):
        node_id = f"draft_node_{index}"
        if index == 1:
            op = "input"
            label = "Large graph input"
            rule_count = "0"
        elif index == node_count:
            op = "output"
            label = "Large graph output"
            rule_count = "0"
        else:
            op = "and"
            label = f"Large graph gate {index}"
            rule_count = "2"
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "op": op,
                "ruleCount": rule_count,
                "evidence": "evidence_gap",
                "sourceRef": f"ui_draft.large_sandbox_graph.node.{index}",
                "op_catalog_entry": op,
                "port_contract": {
                    "input_port_id": f"{node_id}:in",
                    "output_port_id": f"{node_id}:out",
                    "input_signal_id": f"{node_id}_{op}_input",
                    "output_signal_id": f"{node_id}_{op}_output",
                    "value_type": "boolean",
                    "required": False,
                    "source_ref": f"ui_draft.large_sandbox_graph.port_contract.{index}",
                    "candidate_state": "sandbox_candidate",
                    "truth_effect": "none",
                },
                "rules": [],
                "x": f"{8 + ((index - 1) % 8) * 11}%",
                "y": f"{18 + ((index - 1) // 8) * 22}%",
                "draftNode": True,
            }
        )

    for index in range(1, node_count):
        source = f"draft_node_{index}"
        target = f"draft_node_{index + 1}"
        edges.append(
            {
                "id": f"edge_large_chain_{index}_{index + 1}",
                "source": source,
                "target": target,
                "source_port_id": f"{source}:out",
                "target_port_id": f"{target}:in",
                "signal_id": f"{source}_to_{target}",
                "value_type": "boolean",
                "unit": "",
                "required": True,
                "source_ref": f"ui_draft.large_sandbox_graph.edge.{index}",
                "hardware_binding": {
                    "owner_kind": "edge",
                    "owner_id": f"edge_large_chain_{index}_{index + 1}",
                    "evidence_status": "evidence_gap",
                    "source_ref": f"ui_draft.large_sandbox_graph.binding.edge.{index}",
                    "truth_effect": "none",
                },
            }
        )

    draft["canvas_authoring_mode"] = "empty_authoring"
    draft["nodes"] = nodes
    draft["edges"] = edges
    draft["selected_node_ids"] = [nodes[-1]["id"]]
    draft["selected_node"] = {"id": nodes[-1]["id"]}
    draft["hardware_bindings"] = []
    draft["typed_ports"] = []
    draft["ports"] = []
    draft["subsystem_groups"] = []
    _drop_derived_large_graph_fields(draft)
    return draft


def large_sandbox_pass_inputs() -> list[dict[str, Any]]:
    return [
        {"tick": 0, "inputs": {"draft_node_1": False}},
        {"tick": 1, "inputs": {"draft_node_1": True}},
        {"tick": 2, "inputs": {"draft_node_1": True}},
    ]


def large_sandbox_pass_assertions(node_count: int = LARGE_GRAPH_DEFAULT_NODE_COUNT) -> list[dict[str, Any]]:
    return [
        {"tick": 0, "target": f"draft_node_{node_count}:out", "expected": False},
        {"tick": 1, "target": f"draft_node_{node_count}:out", "expected": True},
        {"tick": 2, "target": f"draft_node_{node_count}:out", "expected": True},
    ]


def large_sandbox_fail_assertions(node_count: int = LARGE_GRAPH_DEFAULT_NODE_COUNT) -> list[dict[str, Any]]:
    return [
        {"tick": 1, "target": f"draft_node_{node_count}:out", "expected": False},
    ]


def large_sandbox_invalid_draft(
    base: dict[str, Any],
    node_count: int = LARGE_GRAPH_INVALID_NODE_COUNT,
) -> dict[str, Any]:
    draft = large_sandbox_chain_draft(base, node_count=node_count)
    draft["nodes"][4]["op"] = "python_eval"
    draft["nodes"][4]["op_catalog_entry"] = "python_eval"
    draft["edges"].append({**draft["edges"][0], "id": "edge_large_chain_duplicate"})
    draft["edges"].append(
        {
            "id": "edge_large_chain_dangling",
            "source": f"draft_node_{node_count}",
            "target": "draft_node_missing",
            "source_port_id": f"draft_node_{node_count}:out",
            "target_port_id": "draft_node_missing:in",
            "signal_id": f"draft_node_{node_count}_to_missing",
            "value_type": "boolean",
            "required": True,
            "source_ref": "ui_draft.large_sandbox_graph.invalid.dangling",
            "truth_effect": "none",
        }
    )
    return draft


def large_sandbox_stale_report_draft(
    base: dict[str, Any],
    node_count: int = LARGE_GRAPH_DEFAULT_NODE_COUNT,
) -> dict[str, Any]:
    draft = large_sandbox_chain_draft(base, node_count=node_count)
    draft["sandbox_test_run_report"] = {
        "kind": "well-harness-workbench-sandbox-test-run-report",
        "version": "workbench-sandbox-test-run-report.v1",
        "status": "pass",
        "assertion_status": "pass",
        "model_hash": LARGE_GRAPH_STALE_REPORT_MODEL_HASH,
        "test_case_id": "large_graph_stale_report_probe",
        "truth_effect": "none",
    }
    return draft


def large_sandbox_stress_pack(base: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": LARGE_GRAPH_STRESS_PACK_KIND,
        "version": LARGE_GRAPH_STRESS_PACK_VERSION,
        "candidate_state": "sandbox_candidate",
        "certification_claim": "none",
        "truth_effect": "none",
        "cases": {
            "pass": {
                "draft": large_sandbox_chain_draft(base),
                "inputs": large_sandbox_pass_inputs(),
                "assertions": large_sandbox_pass_assertions(),
                "expected_status": "pass",
            },
            "fail": {
                "draft": large_sandbox_chain_draft(base),
                "inputs": large_sandbox_pass_inputs(),
                "assertions": large_sandbox_fail_assertions(),
                "expected_status": "fail",
            },
            "invalid_graph": {
                "draft": large_sandbox_invalid_draft(base),
                "inputs": [{"tick": 0, "inputs": {"draft_node_1": True}}],
                "assertions": [],
                "expected_status": "invalid_scenario",
                "expected_finding_codes": ("unsupported_op", "duplicate_edge", "dangling_edge"),
                "unsupported_node_id": "draft_node_5",
                "unsupported_op": "python_eval",
            },
            "stale_report": {
                "draft": large_sandbox_stale_report_draft(base),
                "expected_preflight_code": "stale_sandbox_test_run_report",
                "expected_sandbox_report_freshness": "stale",
            },
        },
    }


def _drop_derived_large_graph_fields(draft: dict[str, Any]) -> None:
    for stale_key in (
        "editable_graph_document",
        "sandbox_test_bench",
        "sandbox_test_run_report",
        "candidate_debugger_view",
        "debug_probe_timeline",
        "preflight_analyzer_report",
        "hardware_evidence_attachment_v2",
    ):
        draft.pop(stale_key, None)

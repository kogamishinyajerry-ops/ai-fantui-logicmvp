from __future__ import annotations

import json

import pytest

from well_harness.workbench_large_graph_stress_pack import (
    LARGE_GRAPH_STALE_REPORT_MODEL_HASH,
    LARGE_GRAPH_STRESS_PACK_KIND,
    LARGE_GRAPH_STRESS_PACK_VERSION,
    large_sandbox_chain_draft,
    large_sandbox_stress_pack,
)


def _base_draft() -> dict:
    return {
        "kind": "well-harness-workbench-ui-draft",
        "version": 1,
        "nodes": [{"id": "old_node"}],
        "edges": [{"id": "old_edge"}],
        "editable_graph_document": {"stale": True},
        "sandbox_test_bench": {"stale": True},
        "sandbox_test_run_report": {"stale": True},
        "candidate_debugger_view": {"stale": True},
        "debug_probe_timeline": {"stale": True},
        "preflight_analyzer_report": {"stale": True},
        "hardware_evidence_attachment_v2": {"stale": True},
    }


def test_large_sandbox_chain_draft_is_deterministic_and_truth_neutral() -> None:
    first = large_sandbox_chain_draft(_base_draft(), node_count=16)
    second = large_sandbox_chain_draft(_base_draft(), node_count=16)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["canvas_authoring_mode"] == "empty_authoring"
    assert len(first["nodes"]) == 16
    assert len(first["edges"]) == 15
    assert first["nodes"][0]["op"] == "input"
    assert first["nodes"][-1]["op"] == "output"
    assert first["selected_node_ids"] == ["draft_node_16"]
    assert first["edges"][0]["hardware_binding"]["truth_effect"] == "none"
    assert first["nodes"][1]["port_contract"]["truth_effect"] == "none"
    for stale_key in (
        "editable_graph_document",
        "sandbox_test_bench",
        "sandbox_test_run_report",
        "candidate_debugger_view",
        "debug_probe_timeline",
        "preflight_analyzer_report",
        "hardware_evidence_attachment_v2",
    ):
        assert stale_key not in first


def test_large_sandbox_chain_rejects_too_small_graphs() -> None:
    with pytest.raises(ValueError, match="at least 3 nodes"):
        large_sandbox_chain_draft(_base_draft(), node_count=2)


def test_large_sandbox_stress_pack_covers_pass_fail_invalid_and_stale_cases() -> None:
    stress_pack = large_sandbox_stress_pack(_base_draft())
    cases = stress_pack["cases"]

    assert stress_pack["kind"] == LARGE_GRAPH_STRESS_PACK_KIND
    assert stress_pack["version"] == LARGE_GRAPH_STRESS_PACK_VERSION
    assert stress_pack["candidate_state"] == "sandbox_candidate"
    assert stress_pack["certification_claim"] == "none"
    assert stress_pack["truth_effect"] == "none"
    assert set(cases) == {"pass", "fail", "invalid_graph", "stale_report"}
    assert cases["pass"]["expected_status"] == "pass"
    assert cases["pass"]["assertions"][-1]["target"] == "draft_node_16:out"
    assert cases["fail"]["expected_status"] == "fail"
    assert cases["fail"]["assertions"][0]["expected"] is False

    invalid = cases["invalid_graph"]
    invalid_draft = invalid["draft"]
    assert invalid["expected_status"] == "invalid_scenario"
    assert set(invalid["expected_finding_codes"]) == {"unsupported_op", "duplicate_edge", "dangling_edge"}
    assert invalid["unsupported_node_id"] == "draft_node_5"
    assert invalid["unsupported_op"] == "python_eval"
    assert invalid_draft["nodes"][4]["op"] == "python_eval"
    assert any(edge["id"] == "edge_large_chain_duplicate" for edge in invalid_draft["edges"])
    assert any(edge["target"] == "draft_node_missing" for edge in invalid_draft["edges"])

    stale = cases["stale_report"]
    stale_report = stale["draft"]["sandbox_test_run_report"]
    assert stale["expected_preflight_code"] == "stale_sandbox_test_run_report"
    assert stale["expected_sandbox_report_freshness"] == "stale"
    assert stale_report["model_hash"] == LARGE_GRAPH_STALE_REPORT_MODEL_HASH
    assert stale_report["truth_effect"] == "none"

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from well_harness.editable_change_request import (
    ChangeRequestValidationError,
    build_editable_workbench_change_request,
    build_linear_issue_body,
    build_pr_proof_packet,
    validate_change_request,
)
from well_harness.editable_control_model import (
    build_reference_editable_control_model,
    compare_editable_snapshot_to_baseline,
    editable_control_model_hash,
)


FULL_CHAIN_SNAPSHOT = {
    "radio_altitude_ft": 5.0,
    "tra_deg": -14.0,
    "sw1": True,
    "sw2": True,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "n1k": 50.0,
    "max_n1k_deploy_limit": 60.0,
    "tls_unlocked_ls": True,
    "all_pls_unlocked_ls": True,
    "reverser_not_deployed_eec": True,
    "reverser_fully_deployed_eec": False,
    "deploy_position_percent": 95.0,
    "deploy_90_percent_vdt": True,
}

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_builds_schema_valid_workbench_changerequest_handoff() -> None:
    model = build_reference_editable_control_model()
    diff_report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)

    request = build_editable_workbench_change_request(
        model,
        diff_report,
        title="Review sandbox draft against certified baseline",
        source_ref="JER-159",
        created_at="2026-04-29",
    )

    validate_change_request(request)
    handoff = request["workbench_handoff"]

    assert request["schema_version"] == "change_request.v0.1"
    assert request["authority"]["status"] == "draft_non_authoritative"
    assert request["impacts"]["truth_level_impact"] == "none"
    assert request["dal_impact"]["impact"] == "none"
    assert handoff["changed_model_hash"] == editable_control_model_hash(model)
    assert handoff["truth_level_impact"] == "none"
    assert handoff["red_line_impact"]["touched"] == ["none"]
    assert "Outcome" in handoff["linear_issue_body"]
    assert "Acceptance" in handoff["linear_issue_body"]
    assert "Boundaries" in handoff["linear_issue_body"]
    assert "Evidence Required" in handoff["linear_issue_body"]
    assert "Metadata" in handoff["linear_issue_body"]
    assert "Agent eligible: No" in handoff["linear_issue_body"]
    assert "Truth-level impact: none" in handoff["pr_proof_packet"]
    assert "Red lines touched: none" in handoff["pr_proof_packet"]


def test_linear_issue_body_and_pr_packet_keep_codex_lane_fields() -> None:
    model = build_reference_editable_control_model()
    diff_report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)
    request = build_editable_workbench_change_request(
        model,
        diff_report,
        title="Review sandbox draft against certified baseline",
        source_ref="JER-159",
        created_at="2026-04-29",
    )

    issue_body = build_linear_issue_body(request)
    pr_packet = build_pr_proof_packet(request, test_delta="targeted pytest pending")

    assert "Outcome" in issue_body
    assert "Context" in issue_body
    assert "Acceptance" in issue_body
    assert "Boundaries" in issue_body
    assert "Evidence Required" in issue_body
    assert "Truth-level impact: none" in issue_body
    assert "Red lines touched: none" in issue_body
    assert "Linear: JER-159" in pr_packet
    assert "Adapter: thrust-reverser" in pr_packet
    assert "Layer: L4" in pr_packet
    assert "Truth-level impact: none" in pr_packet
    assert "Red lines touched: none" in pr_packet
    assert "Test delta: targeted pytest pending" in pr_packet


def test_change_request_validator_rejects_certified_handoff_claim() -> None:
    model = build_reference_editable_control_model()
    diff_report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)
    request = build_editable_workbench_change_request(
        model,
        diff_report,
        title="Review sandbox draft against certified baseline",
        source_ref="JER-159",
        created_at="2026-04-29",
    )
    request["workbench_handoff"]["truth_level_impact"] = "certified"

    with pytest.raises(ChangeRequestValidationError, match="truth_level_impact"):
        validate_change_request(request)


def test_builder_rejects_diff_report_for_a_different_candidate_hash() -> None:
    model = build_reference_editable_control_model()
    diff_report = compare_editable_snapshot_to_baseline(model, FULL_CHAIN_SNAPSHOT)
    edited_model = copy.deepcopy(model)
    edited_model["nodes"][0]["label"] = "candidate label drift"

    with pytest.raises(ChangeRequestValidationError, match="model hash"):
        build_editable_workbench_change_request(
            edited_model,
            diff_report,
            title="Review sandbox draft against certified baseline",
            source_ref="JER-159",
            created_at="2026-04-29",
        )


def test_changerequest_handoff_does_not_leak_into_truth_runtime_or_adapters() -> None:
    truth_runtime_paths = [
        REPO_ROOT / "src" / "well_harness" / "controller.py",
        REPO_ROOT / "src" / "well_harness" / "runner.py",
        REPO_ROOT / "src" / "well_harness" / "models.py",
    ]
    truth_runtime_paths.extend((REPO_ROOT / "src" / "well_harness" / "adapters").glob("*.py"))

    for path in truth_runtime_paths:
        text = path.read_text(encoding="utf-8")
        assert "editable_change_request" not in text
        assert "workbench_handoff" not in text
        assert "ChangeRequest Handoff" not in text

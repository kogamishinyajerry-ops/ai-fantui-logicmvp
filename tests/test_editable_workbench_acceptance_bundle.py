from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from well_harness.editable_control_model import editable_control_model_hash
from well_harness.editable_workbench_acceptance import (
    EditableWorkbenchAcceptanceError,
    apply_rule_threshold_edit,
    archive_editable_workbench_acceptance_bundle,
    build_editable_workbench_acceptance_bundle,
    derive_baseline_draft,
    validate_editable_workbench_acceptance_manifest,
)
from well_harness.timeline_engine import Timeline, parse_timeline


TIMELINE_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "src" / "well_harness" / "timelines"


def _nominal_timeline():
    return parse_timeline(json.loads((TIMELINE_FIXTURES_DIR / "nominal_landing.json").read_text()))


def _edited_candidate_model() -> dict:
    baseline = derive_baseline_draft()
    candidate = apply_rule_threshold_edit(
        baseline,
        node_id="logic3",
        rule_name="tra_deg",
        threshold_value=-11.74,
        label="L3 sandbox acceptance candidate",
    )
    candidate["model_id"] = "thrust-reverser-derived-view-v1-acceptance-candidate"
    return candidate


def test_deterministic_edit_primitive_derives_sandbox_candidate_without_mutating_baseline() -> None:
    baseline = derive_baseline_draft()
    candidate = apply_rule_threshold_edit(
        baseline,
        node_id="logic3",
        rule_name="tra_deg",
        threshold_value=-11.74,
        label="L3 sandbox acceptance candidate",
    )

    baseline_logic3 = next(node for node in baseline["nodes"] if node["id"] == "logic3")
    candidate_logic3 = next(node for node in candidate["nodes"] if node["id"] == "logic3")

    assert baseline["truth_status"] == "sandbox_candidate"
    assert candidate["truth_status"] == "sandbox_candidate"
    assert baseline_logic3["label"] != candidate_logic3["label"]
    assert candidate_logic3["label"] == "L3 sandbox acceptance candidate"
    assert editable_control_model_hash(baseline) != editable_control_model_hash(candidate)


def test_acceptance_bundle_covers_full_editable_workbench_happy_path() -> None:
    model = _edited_candidate_model()

    bundle = build_editable_workbench_acceptance_bundle(
        model,
        _nominal_timeline(),
        source_ref="JER-160",
        created_at="2026-04-29",
    )

    assert bundle["kind"] == "well-harness-editable-workbench-acceptance-bundle"
    assert bundle["workflow"]["status"] == "sandbox_candidate_acceptance"
    assert bundle["workflow"]["steps"] == [
        "derive_baseline_draft",
        "edit_candidate_graph",
        "run_sandbox_timeline",
        "compare_baseline_diff",
        "generate_changerequest",
        "generate_pr_proof_packet",
        "archive_evidence_bundle",
    ]
    assert bundle["model"]["model_hash"] == editable_control_model_hash(model)
    assert bundle["baseline_model"]["truth_status"] == "sandbox_candidate"
    assert bundle["candidate_model"]["truth_status"] == "sandbox_candidate"
    assert bundle["candidate_trace"]["frame_count"] == 180
    assert bundle["diff_report"]["verdict"] == "equivalent"
    assert bundle["change_request"]["workbench_handoff"]["layer"] == "L9"
    assert bundle["change_request"]["workbench_handoff"]["truth_level_impact"] == "none"
    assert "Linear: JER-160" in bundle["pr_proof_packet"]
    assert "Layer: L9" in bundle["pr_proof_packet"]
    assert "Truth-level impact: none" in bundle["pr_proof_packet"]
    assert bundle["frozen_references"]["c919-etras"]["access"] == "read_only_frozen"


def test_acceptance_archive_contains_required_artifacts_and_manifest_checksums(tmp_path: Path) -> None:
    bundle = build_editable_workbench_acceptance_bundle(
        _edited_candidate_model(),
        _nominal_timeline(),
        source_ref="JER-160",
        created_at="2026-04-29",
    )

    archive = archive_editable_workbench_acceptance_bundle(bundle, tmp_path)
    manifest_path = Path(archive["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert validate_editable_workbench_acceptance_manifest(manifest, manifest_path=manifest_path) == ()
    for key in (
        "bundle_json",
        "model_json",
        "candidate_trace_json",
        "diff_report_json",
        "change_request_json",
        "pr_proof_packet_markdown",
        "summary_markdown",
    ):
        assert manifest["files"][key]
        assert key in manifest["integrity"]
        assert len(manifest["integrity"][key]) == 64
        assert (manifest_path.parent / manifest["files"][key]).is_file()
    assert len(manifest["integrity"]["manifest_json"]) == 64


def test_acceptance_bundle_rejects_c919_candidate_because_reference_is_frozen() -> None:
    model = _edited_candidate_model()
    model["system_id"] = "c919-etras"

    with pytest.raises(EditableWorkbenchAcceptanceError, match="frozen"):
        build_editable_workbench_acceptance_bundle(
            model,
            _nominal_timeline(),
            source_ref="JER-160",
            created_at="2026-04-29",
        )


def test_acceptance_bundle_rejects_truth_or_dal_escalation_claims() -> None:
    truth_model = _edited_candidate_model()
    truth_model["boundaries"]["truth_level_impact"] = "certified"

    with pytest.raises(EditableWorkbenchAcceptanceError, match="truth_level"):
        build_editable_workbench_acceptance_bundle(
            truth_model,
            _nominal_timeline(),
            source_ref="JER-160",
            created_at="2026-04-29",
        )

    dal_model = _edited_candidate_model()
    dal_model["boundaries"]["dal_pssa_impact"] = "potential"

    with pytest.raises(EditableWorkbenchAcceptanceError, match="dal"):
        build_editable_workbench_acceptance_bundle(
            dal_model,
            _nominal_timeline(),
            source_ref="JER-160",
            created_at="2026-04-29",
        )


def test_acceptance_bundle_rejects_certified_truth_status_and_controller_mutation_claim() -> None:
    certified_model = _edited_candidate_model()
    certified_model["truth_status"] = "certified"

    with pytest.raises(EditableWorkbenchAcceptanceError, match="truth_status"):
        build_editable_workbench_acceptance_bundle(
            certified_model,
            _nominal_timeline(),
            source_ref="JER-160",
            created_at="2026-04-29",
        )

    controller_mutation_model = _edited_candidate_model()
    controller_mutation_model["boundaries"]["controller_truth_modified"] = True

    with pytest.raises(EditableWorkbenchAcceptanceError, match="controller_truth_modified"):
        build_editable_workbench_acceptance_bundle(
            controller_mutation_model,
            _nominal_timeline(),
            source_ref="JER-160",
            created_at="2026-04-29",
        )


def test_acceptance_bundle_rejects_non_fantui_timeline() -> None:
    timeline = Timeline(
        system="c919-etras",
        step_s=0.1,
        duration_s=0.1,
        initial_inputs={},
        events=[],
        title="frozen-c919-timeline",
    )

    with pytest.raises(EditableWorkbenchAcceptanceError, match="fantui"):
        build_editable_workbench_acceptance_bundle(
            _edited_candidate_model(),
            timeline,
            source_ref="JER-160",
            created_at="2026-04-29",
        )


def test_acceptance_archive_manifest_detects_checksum_drift(tmp_path: Path) -> None:
    bundle = build_editable_workbench_acceptance_bundle(
        _edited_candidate_model(),
        _nominal_timeline(),
        source_ref="JER-160",
        created_at="2026-04-29",
    )
    archive = archive_editable_workbench_acceptance_bundle(bundle, tmp_path)
    manifest_path = Path(archive["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = manifest_path.parent / manifest["files"]["model_json"]
    model_path.write_text(model_path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    issues = validate_editable_workbench_acceptance_manifest(
        manifest,
        manifest_path=manifest_path,
    )

    assert any("model_json" in issue and "checksum mismatch" in issue for issue in issues)


def test_acceptance_module_does_not_import_truth_runtime_or_frozen_assets() -> None:
    module_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "well_harness"
        / "editable_workbench_acceptance.py"
    )
    text = module_path.read_text(encoding="utf-8")

    assert "well_harness.controller" not in text
    assert "well_harness.runner" not in text
    assert "well_harness.models" not in text
    assert "well_harness.adapters" not in text
    assert "c919_etras" not in text
    assert "llm_client" not in text

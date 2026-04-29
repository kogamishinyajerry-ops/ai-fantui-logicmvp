from __future__ import annotations

import copy
import json
from pathlib import Path

from well_harness.editable_control_model import (
    build_reference_editable_control_model,
    validate_editable_control_model_diff_report,
)
from well_harness.editable_timeline_sandbox import (
    compare_editable_timeline_to_baseline,
    run_baseline_timeline_trace,
    run_editable_timeline_candidate,
)
from well_harness.timeline_engine import Timeline, TimelineEvent, parse_timeline


TIMELINE_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "src" / "well_harness" / "timelines"


def _event_application_timeline() -> Timeline:
    return Timeline(
        system="fantui",
        step_s=0.1,
        duration_s=0.3,
        initial_inputs={
            "radio_altitude_ft": 5.0,
            "tra_deg": 0.0,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 45.0,
            "max_n1k_deploy_limit": 60.0,
        },
        events=[
            TimelineEvent(
                t_s=0.0,
                kind="ramp_input",
                target="tra_deg",
                value=-14.0,
                duration_s=0.1,
            ),
            TimelineEvent(t_s=0.0, kind="assert_condition", target="logic1", value="active"),
            TimelineEvent(t_s=0.1, kind="set_input", target="reverser_inhibited", value=True),
            TimelineEvent(t_s=0.1, kind="assert_condition", target="logic1", value="active"),
        ],
        title="editable-event-application-smoke",
    )


def test_candidate_timeline_reuses_existing_event_application_semantics() -> None:
    model = build_reference_editable_control_model()
    timeline = _event_application_timeline()

    baseline = run_baseline_timeline_trace(timeline)
    candidate = run_editable_timeline_candidate(model, timeline, baseline_trace=baseline)

    assert candidate["model_hash"]
    assert candidate["op_catalog_version"] == "editable-control-ops.v1"
    assert candidate["frame_count"] == len(baseline.frames)
    assert candidate["frames"][0]["logic_states"]["logic1"] == "active"
    assert candidate["frames"][1]["inputs"]["reverser_inhibited"] is True
    assert candidate["frames"][1]["logic_states"]["logic1"] == "blocked"


def test_candidate_timeline_records_assertion_outcomes() -> None:
    model = build_reference_editable_control_model()
    timeline = _event_application_timeline()

    candidate = run_editable_timeline_candidate(model, timeline)

    assert candidate["assertion_status"] == "fail"
    assert [assertion["passed"] for assertion in candidate["assertions"]] == [True, False]
    assert candidate["assertions"][1]["target"] == "logic1"
    assert candidate["assertions"][1]["observed"] == "blocked"


def test_timeline_diff_reports_equivalent_for_reference_nominal_fixture() -> None:
    model = build_reference_editable_control_model()
    timeline = parse_timeline(
        json.loads((TIMELINE_FIXTURES_DIR / "nominal_landing.json").read_text())
    )

    report = compare_editable_timeline_to_baseline(
        model,
        timeline,
        scenario_id="nominal_landing",
    )

    validate_editable_control_model_diff_report(report)
    assert report["verdict"] == "equivalent"
    assert report["scenario_result"]["scenario_id"] == "nominal_landing"
    assert report["scenario_result"]["assertion_status"] == "pass"
    assert report["scenario_result"]["frame_count"] == 180
    assert all(delta["status"] == "same" for delta in report["per_signal_delta"])


def test_candidate_timeline_reuses_existing_command_assertion_targets() -> None:
    model = build_reference_editable_control_model()
    timeline = parse_timeline(
        json.loads((TIMELINE_FIXTURES_DIR / "sw1_stuck_at_touchdown.json").read_text())
    )

    candidate = run_editable_timeline_candidate(model, timeline)
    report = compare_editable_timeline_to_baseline(
        model,
        timeline,
        scenario_id="sw1_stuck_at_touchdown",
    )

    assert candidate["assertion_status"] == "pass"
    assert report["verdict"] == "equivalent"
    assert report["scenario_result"]["assertion_status"] == "pass"


def test_timeline_diff_reports_first_divergence_for_candidate_threshold_drift() -> None:
    model = copy.deepcopy(build_reference_editable_control_model())
    logic3 = next(node for node in model["nodes"] if node["id"] == "logic3")
    tra_rule = next(rule for rule in logic3["rules"] if rule["name"] == "tra_deg")
    tra_rule["threshold_value"] = -30.0
    timeline = parse_timeline(
        json.loads((TIMELINE_FIXTURES_DIR / "nominal_landing.json").read_text())
    )

    report = compare_editable_timeline_to_baseline(
        model,
        timeline,
        scenario_id="nominal_landing_drift",
    )

    validate_editable_control_model_diff_report(report)
    assert report["verdict"] == "divergent"
    assert report["first_divergence"]["signal_id"] == "logic3"
    assert report["first_divergence"]["baseline_value"] is True
    assert report["first_divergence"]["candidate_value"] is False
    assert any(
        delta["signal_id"] == "logic3" and delta["status"] == "different"
        for delta in report["per_signal_delta"]
    )

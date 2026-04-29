"""Timeline integration for editable control model sandbox candidates.

This module reuses the existing TimelinePlayer event semantics. The baseline
trace is still produced by FantuiExecutor/controller truth; the editable model
only evaluates candidate graph snapshots against the resolved frame inputs.
"""
from __future__ import annotations

from typing import Any

from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
from well_harness.editable_control_model import (
    OP_CATALOG_VERSION,
    build_editable_control_model_diff_report,
    editable_control_model_hash,
    evaluate_editable_snapshot,
    validate_editable_control_model,
    validate_editable_control_model_diff_report,
)
from well_harness.timeline_engine import AssertionResult, Timeline, TimelinePlayer
from well_harness.timeline_engine.executors.fantui import FantuiExecutor


TIMELINE_DIFF_SIGNALS = ("logic1", "logic2", "logic3", "logic4")
_FLOAT_EPS = 1e-9


def run_baseline_timeline_trace(timeline: Timeline):
    """Run the certified thrust-reverser timeline baseline."""
    if timeline.system != "fantui":
        raise ValueError(
            "editable timeline sandbox only supports fantui timelines, "
            f"got {timeline.system!r}"
        )
    return TimelinePlayer(timeline, FantuiExecutor()).run()


def _candidate_outputs(result: dict[str, Any]) -> dict[str, bool]:
    logic_outputs = {
        f"{signal_id}_active": bool(result["asserted_component_values"].get(signal_id))
        for signal_id in TIMELINE_DIFF_SIGNALS
    }
    values = result["asserted_component_values"]
    logic_outputs.update(
        {
            "tls_115vac_cmd": bool(values.get("tls_voltage_v")),
            "etrac_540vdc_cmd": bool(values.get("etrac_voltage_v")),
            "eec_deploy_cmd": bool(values.get("eec_cmd")),
            "pls_power_cmd": bool(values.get("pls_cmd")),
            "pdu_motor_cmd": bool(values.get("pdu_cmd")),
            "throttle_electronic_lock_release_cmd": bool(values.get("thr_lock")),
            "throttle_lock_release_cmd": bool(values.get("thr_lock")),
        }
    )
    return logic_outputs


def _candidate_logic_states(result: dict[str, Any]) -> dict[str, str]:
    return {
        signal_id: result["logic_states"].get(signal_id, {"state": "idle"})["state"]
        for signal_id in TIMELINE_DIFF_SIGNALS
    }


def _assertion_for_candidate(
    event,
    outputs: dict[str, Any],
    logic_states: dict[str, str],
) -> AssertionResult:
    if event.target in outputs:
        observed = outputs[event.target]
    elif event.target in logic_states:
        observed = logic_states[event.target]
    else:
        return AssertionResult(
            at_s=event.t_s,
            target=event.target,
            expected=event.value,
            observed=None,
            passed=False,
            note=(
                f"assertion target {event.target!r} not found in candidate "
                "outputs or logic_states"
            ),
        )
    return AssertionResult(
        at_s=event.t_s,
        target=event.target,
        expected=event.value,
        observed=observed,
        passed=observed == event.value,
        note=event.note,
    )


def _candidate_assertions_for_frame(
    timeline: Timeline,
    frame_t_s: float,
    outputs: dict[str, Any],
    logic_states: dict[str, str],
) -> list[AssertionResult]:
    tick_start = frame_t_s - timeline.step_s
    tick_end = frame_t_s
    return [
        _assertion_for_candidate(event, outputs, logic_states)
        for event in timeline.events
        if (
            event.kind == "assert_condition"
            and tick_start - _FLOAT_EPS <= event.t_s < tick_end - _FLOAT_EPS
        )
    ]


def _assertion_status(assertions: list[AssertionResult]) -> str:
    if not assertions:
        return "not_run"
    return "pass" if all(assertion.passed for assertion in assertions) else "fail"


def run_editable_timeline_candidate(
    model: dict[str, Any],
    timeline: Timeline,
    *,
    baseline_trace=None,
) -> dict[str, Any]:
    """Run an editable model candidate over an existing timeline trace.

    The candidate does not own plant physics or switch truth. It consumes the
    resolved inputs emitted by the baseline trace and evaluates the sandbox
    graph per frame.
    """
    validate_editable_control_model(model)
    baseline = baseline_trace or run_baseline_timeline_trace(timeline)
    model_hash = editable_control_model_hash(model)
    frames: list[dict[str, Any]] = []
    assertions: list[AssertionResult] = []

    for frame in baseline.frames:
        candidate_result = evaluate_editable_snapshot(model, frame.inputs)
        outputs = _candidate_outputs(candidate_result)
        logic_states = _candidate_logic_states(candidate_result)
        assertions.extend(
            _candidate_assertions_for_frame(timeline, frame.t_s, outputs, logic_states)
        )
        frames.append(
            {
                "tick": frame.tick,
                "t_s": frame.t_s,
                "phase": frame.phase,
                "inputs": dict(frame.inputs),
                "outputs": outputs,
                "logic_states": logic_states,
                "active_faults": list(frame.active_faults),
                "events_fired": list(frame.events_fired),
                "model_hash": model_hash,
                "op_catalog_version": OP_CATALOG_VERSION,
            }
        )

    return {
        "model_id": model["model_id"],
        "model_hash": model_hash,
        "system_id": model["system_id"],
        "truth_status": model["truth_status"],
        "op_catalog_version": OP_CATALOG_VERSION,
        "frame_count": len(frames),
        "frames": frames,
        "assertions": [
            {
                "at_s": assertion.at_s,
                "target": assertion.target,
                "expected": assertion.expected,
                "observed": assertion.observed,
                "passed": assertion.passed,
                "note": assertion.note,
            }
            for assertion in assertions
        ],
        "assertion_status": _assertion_status(assertions),
    }


def _baseline_signal_value(frame, signal_id: str) -> bool:
    return bool(
        frame.logic_states.get(signal_id) == "active"
        or frame.outputs.get(f"{signal_id}_active") is True
    )


def _candidate_signal_value(frame: dict[str, Any], signal_id: str) -> bool:
    return bool(
        frame["logic_states"].get(signal_id) == "active"
        or frame["outputs"].get(f"{signal_id}_active") is True
    )


def compare_editable_timeline_to_baseline(
    model: dict[str, Any],
    timeline: Timeline,
    *,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    """Compare candidate timeline trace against certified FantuiExecutor trace."""
    baseline_trace = run_baseline_timeline_trace(timeline)
    candidate_trace = run_editable_timeline_candidate(
        model,
        timeline,
        baseline_trace=baseline_trace,
    )
    per_signal_status = {signal_id: "same" for signal_id in TIMELINE_DIFF_SIGNALS}
    first_divergence = None

    for baseline_frame, candidate_frame in zip(baseline_trace.frames, candidate_trace["frames"]):
        for signal_id in TIMELINE_DIFF_SIGNALS:
            baseline_value = _baseline_signal_value(baseline_frame, signal_id)
            candidate_value = _candidate_signal_value(candidate_frame, signal_id)
            if baseline_value != candidate_value:
                per_signal_status[signal_id] = "different"
                if first_divergence is None:
                    first_divergence = {
                        "at_s": baseline_frame.t_s,
                        "signal_id": signal_id,
                        "baseline_value": baseline_value,
                        "candidate_value": candidate_value,
                    }

    baseline_model = {
        **model,
        "model_id": REFERENCE_DEPLOY_CONTROLLER_METADATA.adapter_id,
        "truth_status": REFERENCE_DEPLOY_CONTROLLER_METADATA.truth_level or "certified",
        "source_of_truth": REFERENCE_DEPLOY_CONTROLLER_METADATA.source_of_truth,
    }
    report = build_editable_control_model_diff_report(
        baseline_model=baseline_model,
        candidate_model=model,
        scenario_id=scenario_id or timeline.title or "timeline-default",
        verdict="divergent" if first_divergence else "equivalent",
        first_divergence=first_divergence,
        per_signal_delta=[
            {"signal_id": signal_id, "status": status}
            for signal_id, status in per_signal_status.items()
        ],
    )
    report["scenario_result"] = {
        "scenario_id": scenario_id or timeline.title or "timeline-default",
        "assertion_status": candidate_trace["assertion_status"],
        "frame_count": candidate_trace["frame_count"],
    }
    validate_editable_control_model_diff_report(report)
    return report

"""
Tests for tools/onboard_new_system_dry_run.py.

Validates that:
  - The script exits 0 when given a valid landing-gear spec
  - The script exits non-zero when the spec is invalid
  - Output JSON is well-formed
  - --format text works
  - --format json works
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = PROJECT_ROOT / "tools" / "onboard_new_system_dry_run.py"
SRC_DIR = PROJECT_ROOT / "src"

# A minimal valid spec built from the landing-gear adapter's spec dict.
# We use the landing-gear spec as the canonical "valid" reference.
LG_SPEC_DICT = {
    "$schema": "https://well-harness.local/json_schema/control_system_spec_v1.schema.json",
    "kind": "well-harness-control-system-spec",
    "version": 1,
    "system_id": "minimal_landing_gear_extension",
    "title": "Minimal Landing-Gear Extension Control",
    "objective": "Release the uplock and drive extension once the handle is selected down and hydraulic pressure is healthy.",
    "source_of_truth": "src/well_harness/adapters/landing_gear_adapter.py",
    "components": [
        {
            "id": "gear_handle_position",
            "label": "Gear Handle",
            "kind": "pilot_input",
            "state_shape": "discrete",
            "unit": "state",
            "description": "Landing-gear cockpit handle position.",
            "allowed_range": None,
            "allowed_states": ["UP", "DOWN"],
            "monitor_priority": "required",
        },
        {
            "id": "hydraulic_pressure_psi",
            "label": "Hyd Pressure",
            "kind": "sensor",
            "state_shape": "analog",
            "unit": "psi",
            "description": "Extension hydraulic pressure feeding the selector valve and actuator.",
            "allowed_range": [0.0, 3000.0],
            "allowed_states": [],
            "monitor_priority": "required",
        },
        {
            "id": "uplock_released",
            "label": "Uplock Released",
            "kind": "sensor",
            "state_shape": "binary",
            "unit": "state",
            "description": "Discrete indication that the mechanical uplock has released.",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "required",
        },
        {
            "id": "selector_valve_cmd",
            "label": "Selector Valve Command",
            "kind": "command",
            "state_shape": "binary",
            "unit": "state",
            "description": "Command sent once the handle and pressure conditions are satisfied.",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "required",
        },
        {
            "id": "extend_actuator_cmd",
            "label": "Extend Actuator Command",
            "kind": "command",
            "state_shape": "binary",
            "unit": "state",
            "description": "Extension actuator drive command after uplock release.",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "required",
        },
        {
            "id": "gear_position_percent",
            "label": "Gear Position",
            "kind": "sensor",
            "state_shape": "analog",
            "unit": "percent",
            "description": "Landing-gear extension progress.",
            "allowed_range": [0.0, 100.0],
            "allowed_states": [],
            "monitor_priority": "required",
        },
        {
            "id": "downlock_engaged",
            "label": "Downlock Engaged",
            "kind": "sensor",
            "state_shape": "binary",
            "unit": "state",
            "description": "Discrete indication that the gear reached the downlocked state.",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "required",
        },
    ],
    "logic_nodes": [
        {
            "id": "lg_l1_handle_and_pressure",
            "label": "LG-L1",
            "description": "The selector valve may energize only when the gear handle is down and hydraulic pressure is above the extension threshold.",
            "conditions": [
                {
                    "name": "gear_handle_position",
                    "source_component_id": "gear_handle_position",
                    "comparison": "==",
                    "threshold_value": "DOWN",
                    "note": "Extension starts only after the pilot selects DOWN.",
                },
                {
                    "name": "hydraulic_pressure_psi",
                    "source_component_id": "hydraulic_pressure_psi",
                    "comparison": ">=",
                    "threshold_value": 2200.0,
                    "note": "Healthy pressure is required before commanding the selector valve.",
                },
            ],
            "downstream_component_ids": ["selector_valve_cmd"],
            "evidence_priority": "high",
        },
        {
            "id": "lg_l2_extend_after_uplock_release",
            "label": "LG-L2",
            "description": "The extend actuator may drive only after the selector valve is commanded and the uplock is confirmed released.",
            "conditions": [
                {
                    "name": "selector_valve_cmd",
                    "source_component_id": "selector_valve_cmd",
                    "comparison": "==",
                    "threshold_value": 1,
                    "note": "The extension actuator depends on the upstream valve command.",
                },
                {
                    "name": "uplock_released",
                    "source_component_id": "uplock_released",
                    "comparison": "==",
                    "threshold_value": 1,
                    "note": "The gear must be mechanically released before extension drive continues.",
                },
            ],
            "downstream_component_ids": ["extend_actuator_cmd"],
            "evidence_priority": "high",
        },
    ],
    "acceptance_scenarios": [
        {
            "id": "handle_down_nominal_extension",
            "label": "Handle Down Nominal Extension",
            "description": "Nominal extension path from handle-down through full downlock.",
            "time_scale_factor": 1.0,
            "total_duration_s": 6.0,
            "monitored_signal_ids": [
                "hydraulic_pressure_psi",
                "selector_valve_cmd",
                "uplock_released",
                "extend_actuator_cmd",
                "gear_position_percent",
                "downlock_engaged",
            ],
            "transitions": [
                {
                    "signal_id": "selector_valve_cmd",
                    "start_s": 0.0,
                    "end_s": 0.5,
                    "start_value": 0.0,
                    "end_value": 1.0,
                    "unit": "state",
                    "note": "Selector valve energizes immediately after the handle/pressure conditions are satisfied.",
                },
                {
                    "signal_id": "uplock_released",
                    "start_s": 0.3,
                    "end_s": 1.0,
                    "start_value": 0.0,
                    "end_value": 1.0,
                    "unit": "state",
                    "note": "The uplock releases shortly after selector-valve command.",
                },
                {
                    "signal_id": "gear_position_percent",
                    "start_s": 1.0,
                    "end_s": 5.5,
                    "start_value": 0.0,
                    "end_value": 100.0,
                    "unit": "percent",
                    "note": "The gear extends to full downlock travel.",
                },
                {
                    "signal_id": "downlock_engaged",
                    "start_s": 5.0,
                    "end_s": 5.8,
                    "start_value": 0.0,
                    "end_value": 1.0,
                    "unit": "state",
                    "note": "The downlock indication turns on at the end of travel.",
                },
            ],
            "completion_condition": "extend_actuator_cmd == 1 and gear_position_percent >= 99 and downlock_engaged == 1",
            "steady_signals": [
                {
                    "signal_id": "gear_handle_position",
                    "value": "DOWN",
                    "unit": "state",
                    "note": "Pilot holds the gear handle DOWN for the entire extension sequence.",
                },
                {
                    "signal_id": "hydraulic_pressure_psi",
                    "value": 2850.0,
                    "unit": "psi",
                    "note": "Nominal extension pressure remains above the release threshold.",
                },
            ],
        },
    ],
    "fault_modes": [
        {
            "id": "uplock_stuck_locked",
            "target_component_id": "uplock_released",
            "fault_kind": "latched_no_unlock",
            "symptom": "Selector valve energizes but the uplock indication never releases, so extension cannot continue.",
            "reasoning_scope_component_ids": [
                "gear_handle_position",
                "hydraulic_pressure_psi",
                "selector_valve_cmd",
                "uplock_released",
            ],
            "expected_diagnostic_sections": ["symptom", "blocked_logic", "repair_hint"],
            "optimization_prompt": "Check whether uplock release timing and selector valve evidence should be correlated in future maintenance traces.",
        },
        {
            "id": "hydraulic_pressure_bias_low",
            "target_component_id": "hydraulic_pressure_psi",
            "fault_kind": "bias_low",
            "symptom": "Displayed hydraulic pressure stays below the threshold, blocking selector-valve command.",
            "reasoning_scope_component_ids": [
                "gear_handle_position",
                "hydraulic_pressure_psi",
                "selector_valve_cmd",
            ],
            "expected_diagnostic_sections": ["symptom", "blocked_logic", "repair_hint"],
            "optimization_prompt": "Track pressure-sensor calibration drift against commanded extension attempts.",
        },
    ],
    "onboarding_questions": [
        {
            "id": "source_documents",
            "prompt": "What is the format of the input documents: structured table, Markdown/Notion, PDF, or mixed?",
            "rationale": "Determines whether to build a document adapter first.",
            "required_for": "Strict acceptance and fast generalization",
        },
        {
            "id": "component_state_domains",
            "prompt": "Is each component binary, discrete, or continuous analog?",
            "rationale": "Prevents mixing different signal shapes.",
            "required_for": "Monitoring curve simulation and fault injection",
        },
        {
            "id": "timeline_rules",
            "prompt": "Is the engineer-supplied process event-driven, rate-driven, or a state machine with delays?",
            "rationale": "Determines how to convert A/B process docs into replayable timelines.",
            "required_for": "Strict acceptance simulation",
        },
        {
            "id": "fault_taxonomy",
            "prompt": "What fault injection types does the new system need: stuck, short, open, delay, drift, or other?",
            "rationale": "Determines the scope of diagnostic trees and optimization suggestions.",
            "required_for": "Fault analysis and knowledge accumulation",
        },
    ],
    "knowledge_capture": {
        "incident_fields": [
            "system_id",
            "scenario_id",
            "fault_mode_id",
            "observed_symptoms",
            "evidence_links",
        ],
        "resolution_fields": [
            "confirmed_root_cause",
            "repair_action",
            "validation_after_fix",
            "residual_risk",
        ],
        "optimization_fields": [
            "suggested_logic_change",
            "reliability_gain_hypothesis",
            "redundancy_reduction_or_guardrail_note",
        ],
    },
    "tags": ["landing-gear", "runtime-generalization-proof", "second-system"],
}

# An invalid spec — missing required fields.
INVALID_SPEC_DICT = {
    "system_id": "test-system",
    # missing kind, version, title, objective, source_of_truth,
    # components, logic_nodes, acceptance_scenarios, fault_modes,
    # onboarding_questions, knowledge_capture, tags
}


def _run_tool(spec_dict: dict, extra_args: list[str] | None = None) -> tuple[int, str, Path]:
    """
    Write spec_dict to a temp JSON file, run the tool with extra_args,
    and return (exit_code, stdout, path_to_output_json).
    """
    # Create temp directory first; it must stay alive for the subprocess lifetime.
    tmpdir = tempfile.mkdtemp()
    tmpdir_path = Path(tmpdir)
    spec_path = tmpdir_path / "spec.json"
    output_dir = tmpdir_path / "output"
    output_dir.mkdir()

    try:
        with spec_path.open("w", encoding="utf-8") as f:
            json.dump(spec_dict, f)

        args = [
            sys.executable,
            str(TOOL_PATH),
            "--spec-file", str(spec_path),
            "--output-dir", str(output_dir),
        ]
        if extra_args:
            args.extend(extra_args)

        result = subprocess.run(args, capture_output=True, text=True)
        # Read file contents while the temp dir is still alive.
        # Python's finally runs BEFORE the return value is delivered to the caller,
        # so we must read the file before the return statement triggers cleanup.
        output_json_path = output_dir / "dry_run_results.json"
        output_json_contents: dict | None = None
        if output_json_path.exists():
            with output_json_path.open(encoding="utf-8") as f:
                output_json_contents = json.load(f)
        return result.returncode, result.stdout + result.stderr, output_json_path, output_json_contents
    finally:
        # Clean up temp files only after the caller has processed the result.
        import shutil
        shutil.rmtree(tmpdir_path, ignore_errors=True)


class TestOnboardDryRunValidSpec:
    """Script exits 0 when given a valid spec."""

    def test_exit_zero_with_valid_spec(self):
        """A fully-populated landing-gear-equivalent spec passes all 4 stages."""
        exit_code, stdout, _output_path, _results = _run_tool(LG_SPEC_DICT)
        assert exit_code == 0, f"expected exit 0, got {exit_code}. output: {stdout}"

    def test_output_json_is_well_formed(self):
        """The written dry_run_results.json is valid JSON with expected top-level keys."""
        _exit_code, _stdout, _output_path, results = _run_tool(LG_SPEC_DICT)
        assert results is not None, "dry_run_results.json was not written or could not be read"
        assert isinstance(results, dict)
        assert "overall_status" in results
        assert "stages" in results
        assert "spec_file" in results
        assert "jsonschema_available" in results

    def test_all_four_stages_pass(self):
        """A valid spec passes all 4 pipeline stages."""
        _exit_code, _stdout, _output_path, results = _run_tool(LG_SPEC_DICT)
        assert results is not None
        assert results["overall_status"] == "pass"
        stage_ids = [s["stage"] for s in results["stages"]]
        assert set(stage_ids) == {"spec", "playback", "diagnosis", "knowledge"}
        for stage in results["stages"]:
            assert stage["status"] == "pass", f"stage {stage['stage']} failed: {stage.get('errors')}"

    def test_format_text(self):
        """--format text produces human-readable output."""
        exit_code, stdout, _output_path, _results = _run_tool(LG_SPEC_DICT, extra_args=["--format", "text"])
        assert exit_code == 0
        assert "PASS" in stdout or "pass" in stdout.lower()

    def test_format_json(self):
        """--format json produces a JSON blob to stdout."""
        exit_code, stdout, _output_path, _results = _run_tool(LG_SPEC_DICT, extra_args=["--format", "json"])
        assert exit_code == 0
        # stdout should be parseable as JSON
        parsed = json.loads(stdout)
        assert parsed["overall_status"] == "pass"


class TestOnboardDryRunInvalidSpec:
    """Script exits non-zero when spec is invalid."""

    def test_exit_nonzero_with_invalid_spec(self):
        """A spec missing required fields should fail."""
        exit_code, stdout, _output_path, _results = _run_tool(INVALID_SPEC_DICT)
        assert exit_code != 0

    def test_overall_status_is_fail(self):
        """An invalid spec results in overall_status == fail."""
        _exit_code, _stdout, _output_path, results = _run_tool(INVALID_SPEC_DICT)
        assert results is not None
        assert results["overall_status"] == "fail"

    def test_spec_validation_errors_are_reported(self):
        """Spec-level validation errors appear in the results."""
        _exit_code, _stdout, _output_path, results = _run_tool(INVALID_SPEC_DICT)
        assert results is not None
        assert len(results["spec_validation_errors"]) > 0 or any(
            s["status"] == "fail" for s in results["stages"]
        )

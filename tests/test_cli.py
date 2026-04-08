import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.models import DIAGNOSIS_CONTEXT_FIELDS
from well_harness.runner import SimulationRunner
from well_harness.scenarios import nominal_deploy_scenario, retract_reset_scenario

PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
JSON_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "well_harness_debug_v1.schema.json"
VALIDATION_REPORT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "validation_report_v1.schema.json"
VALIDATION_SCHEMA_RUNNER_REPORT_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "validation_schema_runner_report_v1.schema.json"
)
VALIDATION_SCHEMA_CHECKER_REPORT_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "validation_schema_checker_report_v1.schema.json"
)
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_debug_json_schema.py"
VALIDATION_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH = (
    PROJECT_ROOT / "tools" / "validate_validation_report_schema.py"
)
VALIDATION_SCHEMA_RUNNER_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH = (
    PROJECT_ROOT / "tools" / "validate_validation_schema_runner_report_schema.py"
)
VALIDATION_SCHEMA_CHECKER_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH = (
    PROJECT_ROOT / "tools" / "validate_validation_schema_checker_report_schema.py"
)
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
FORCE_SCHEMA_PATH_ENV = "WELL_HARNESS_FORCE_SCHEMA_PATH"
FORCE_CONTRACT_PATH_ENV = "WELL_HARNESS_FORCE_CONTRACT_PATH"
FAIL_CLI_CONTRACT_PATH = FIXTURES_DIR / "_validation_fail_cli_contract.json"
FAIL_INVALID_LOGIC_CONTRACT_PATH = FIXTURES_DIR / "_validation_fail_invalid_logic_contract.json"
FAIL_INVALID_SCENARIO_CONTRACT_PATH = FIXTURES_DIR / "_validation_fail_invalid_scenario_contract.json"
FAIL_UNCLASSIFIED_CONTRACT_PATH = FIXTURES_DIR / "_validation_fail_unclassified_contract.json"
MISMATCH_SCHEMA_PATH = FIXTURES_DIR / "_validation_mismatch_schema.json"
VALIDATION_REPORT_CONTRACT_PATH = FIXTURES_DIR / "validation_report_asset_v1.json"
VALIDATION_SCHEMA_RUNNER_REPORT_ASSET_PATH = (
    FIXTURES_DIR / "validation_schema_runner_report_asset_v1.json"
)
VALIDATION_SCHEMA_CHECKER_REPORT_ASSET_PATH = (
    FIXTURES_DIR / "validation_schema_checker_report_asset_v1.json"
)
CONTRACT_FIXTURE_NAMES = (
    "timeline_contract_v1.json",
    "events_contract_v1.json",
    "explain_contract_v1.json",
    "diagnose_contract_v1.json",
)
TRACE_ROW_SECTION_SCHEMA_DEFS = {
    "pilot": "pilotInputs",
    "resolved_inputs": "resolvedInputs",
    "plant_sensors": "plantSensors",
    "plant_state": "plantDebugState",
    "controller_outputs": "controllerOutputs",
    "controller_explain": "controllerExplain",
}
CONTEXT_FIELD_NAME_SCHEMA_DEFS = {
    "controller_outputs": "contextControllerOutputFieldName",
    "plant_sensors": "contextPlantSensorFieldName",
    "plant_state": "contextPlantStateFieldName",
}


def run_json_cli(args):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(args)
    return exit_code, json.loads(buffer.getvalue())


def run_cli_text(args):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(args)
    return exit_code, buffer.getvalue()


def load_contract(fixture_name):
    contract_path = FIXTURES_DIR / fixture_name
    with contract_path.open(encoding="utf-8") as contract_file:
        return json.load(contract_file)


def load_json_schema_document():
    with JSON_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def load_validation_report_schema_document():
    with VALIDATION_REPORT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def load_validation_schema_runner_report_schema_document():
    with VALIDATION_SCHEMA_RUNNER_REPORT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def load_validation_schema_checker_report_schema_document():
    with VALIDATION_SCHEMA_CHECKER_REPORT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def load_validation_report_contract():
    with VALIDATION_REPORT_CONTRACT_PATH.open(encoding="utf-8") as contract_file:
        return json.load(contract_file)


def load_validation_schema_runner_report_asset():
    with VALIDATION_SCHEMA_RUNNER_REPORT_ASSET_PATH.open(encoding="utf-8") as asset_file:
        return json.load(asset_file)


def load_validation_schema_checker_report_asset():
    with VALIDATION_SCHEMA_CHECKER_REPORT_ASSET_PATH.open(encoding="utf-8") as asset_file:
        return json.load(asset_file)


def group_context_fields(context_fields):
    grouped_fields = {}
    for field_group, field_name in context_fields:
        grouped_fields.setdefault(field_group, []).append(field_name)
    return {
        field_group: tuple(field_names)
        for field_group, field_names in grouped_fields.items()
    }


def schema_context_fields_by_group(schema_defs):
    trace_field_change = schema_defs["traceFieldValueChange"]
    fields_by_group = {}
    for branch in trace_field_change["oneOf"]:
        properties = branch["properties"]
        field_group = properties["field_group"]["const"]
        field_name_ref = properties["field_name"]["$ref"]
        definition_name = field_name_ref.rsplit("/", maxsplit=1)[-1]
        fields_by_group[field_group] = tuple(schema_defs[definition_name]["enum"])
    return fields_by_group


def format_validation_error(error):
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def validation_script_env(**overrides):
    env = dict(os.environ)
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    env.update(overrides)
    return env


def run_validation_script(args=None, **env_overrides):
    return subprocess.run(
        [sys.executable, str(VALIDATION_SCRIPT_PATH), *(args or [])],
        cwd=PROJECT_ROOT,
        env=validation_script_env(**env_overrides),
        capture_output=True,
        text=True,
        check=False,
    )


def run_validation_report_schema_script(args=None, **env_overrides):
    return subprocess.run(
        [sys.executable, str(VALIDATION_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH), *(args or [])],
        cwd=PROJECT_ROOT,
        env=validation_script_env(**env_overrides),
        capture_output=True,
        text=True,
        check=False,
    )


def run_validation_schema_runner_report_schema_script(args=None, **env_overrides):
    return subprocess.run(
        [sys.executable, str(VALIDATION_SCHEMA_RUNNER_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH), *(args or [])],
        cwd=PROJECT_ROOT,
        env=validation_script_env(**env_overrides),
        capture_output=True,
        text=True,
        check=False,
    )


def run_validation_schema_checker_report_schema_script(args=None, **env_overrides):
    return subprocess.run(
        [sys.executable, str(VALIDATION_SCHEMA_CHECKER_REPORT_SCHEMA_VALIDATION_SCRIPT_PATH), *(args or [])],
        cwd=PROJECT_ROOT,
        env=validation_script_env(**env_overrides),
        capture_output=True,
        text=True,
        check=False,
    )


def resolve_validation_contract_env(env_overrides):
    resolved = {}
    for key, value in env_overrides.items():
        if key.endswith("_PATH") and not Path(value).is_absolute():
            resolved[key] = str(PROJECT_ROOT / value)
        else:
            resolved[key] = value
    return resolved


def assert_contract_matches_payload(test_case, contract, payload):
    for field_name in contract["required_top_level_fields"]:
        test_case.assertIn(field_name, payload)
    test_case.assertEqual(payload["schema"], contract["schema"])
    test_case.assertEqual(payload["scenario_name"], contract["schema"]["scenario_name"])

    view = contract["schema"]["view"]
    if view == "timeline":
        assert_timeline_contract_matches(test_case, contract, payload)
    elif view == "events":
        assert_events_contract_matches(test_case, contract, payload)
    elif view == "explain":
        assert_explain_contract_matches(test_case, contract, payload)
    elif view == "diagnose":
        assert_diagnose_contract_matches(test_case, contract, payload)
    else:
        raise AssertionError(f"Unsupported contract view: {view}")


def assert_timeline_contract_matches(test_case, contract, payload):
    test_case.assertEqual(payload["row_count"], len(payload["rows"]))
    test_case.assertGreaterEqual(payload["row_count"], contract["min_row_count"])
    representative_row = payload["rows"][0]
    for field_name in contract["required_row_fields"]:
        test_case.assertIn(field_name, representative_row)
    for section_name, required_fields in contract["required_row_sections"].items():
        for field_name in required_fields:
            test_case.assertIn(field_name, representative_row[section_name])


def assert_events_contract_matches(test_case, contract, payload):
    test_case.assertEqual(payload["event_count"], len(payload["events"]))
    test_case.assertGreaterEqual(payload["event_count"], contract["min_event_count"])
    for event in payload["events"]:
        for field_name in contract["required_event_fields"]:
            test_case.assertIn(field_name, event)
        for change in event["changes"]:
            for field_name in contract["required_event_change_fields"]:
                test_case.assertIn(field_name, change)

    event_change_names = {
        change["field_name"]
        for event in payload["events"]
        for change in event["changes"]
    }
    for field_name in contract["required_event_change_names"]:
        test_case.assertIn(field_name, event_change_names)


def assert_explain_contract_matches(test_case, contract, payload):
    logic = payload["logic"]
    for field_name in contract["required_logic_fields"]:
        test_case.assertIn(field_name, logic)
    test_case.assertEqual(logic["logic_name"], contract["expected_logic_name"])
    for condition in logic["conditions"]:
        for field_name in contract["required_condition_fields"]:
            test_case.assertIn(field_name, condition)

    condition_names = {condition["name"] for condition in logic["conditions"]}
    for condition_name in contract["required_condition_names"]:
        test_case.assertIn(condition_name, condition_names)


def assert_diagnose_contract_matches(test_case, contract, payload):
    test_case.assertEqual(payload["diagnostic_count"], len(payload["diagnostics"]))
    test_case.assertGreaterEqual(payload["diagnostic_count"], contract["min_diagnostic_count"])

    diagnosis = payload["diagnostics"][0]
    for field_name in contract["required_diagnostic_fields"]:
        test_case.assertIn(field_name, diagnosis)

    for changed_condition in diagnosis["changed_conditions"]:
        for field_name in contract["required_changed_condition_fields"]:
            test_case.assertIn(field_name, changed_condition)

    for context_change in diagnosis["context_changes"]:
        for field_name in contract["required_context_change_fields"]:
            test_case.assertIn(field_name, context_change)

    changed_condition_names = {
        changed_condition["name"]
        for changed_condition in diagnosis["changed_conditions"]
    }
    for required_condition in contract["required_changed_conditions"]:
        test_case.assertIn(required_condition["name"], changed_condition_names)

    context_change_keys = {
        (context_change["field_group"], context_change["field_name"])
        for context_change in diagnosis["context_changes"]
    }
    for required_context_change in contract["required_context_changes"]:
        test_case.assertIn(
            (required_context_change["field_group"], required_context_change["field_name"]),
            context_change_keys,
        )


class StructuredTraceTests(unittest.TestCase):
    def test_trace_rows_include_nested_debug_sections(self):
        scenario = nominal_deploy_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))

        logic3_row = next(row for row in result.rows if row.logic3_active)

        self.assertEqual(logic3_row.pilot.tra_deg, -14.0)
        self.assertTrue(logic3_row.resolved_inputs.tls_unlocked_ls)
        self.assertGreaterEqual(logic3_row.plant_state.tls_powered_s, 0.3)
        self.assertTrue(logic3_row.controller_outputs.pls_power_cmd)
        self.assertEqual(logic3_row.deploy_position_percent, logic3_row.plant_sensors.deploy_position_percent)
        self.assertTrue(logic3_row.controller_explain.logic3.active)
        self.assertEqual(logic3_row.controller_explain.logic3.logic_name, "logic3")

    def test_events_capture_key_state_transitions(self):
        scenario = nominal_deploy_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))
        events = result.events()

        event_fields = [{change.field_name for change in event.changes} for event in events]

        self.assertIn({"sw1", "logic1_active", "tls_115vac_cmd"}, event_fields)
        self.assertIn({"deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"}, event_fields)

    def test_events_capture_initial_true_states(self):
        scenario = retract_reset_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))
        first_event_fields = {change.field_name for change in result.events()[0].changes}

        self.assertIn("sw1", first_event_fields)
        self.assertIn("logic1_active", first_event_fields)


class CliDebugOutputTests(unittest.TestCase):
    def test_json_timeline_output_contains_structured_trace(self):
        exit_code, payload = run_json_cli(["run", "nominal-deploy", "--format", "json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            payload["schema"],
            {
                "name": "well_harness.debug",
                "scenario_name": "nominal-deploy",
                "schema_version": "1.0",
                "view": "timeline",
            },
        )
        self.assertIn("rows", payload)
        self.assertIn("pilot", payload["rows"][0])
        self.assertIn("resolved_inputs", payload["rows"][0])
        self.assertIn("plant_sensors", payload["rows"][0])
        self.assertIn("plant_state", payload["rows"][0])
        self.assertIn("controller_outputs", payload["rows"][0])
        self.assertIn("controller_explain", payload["rows"][0])

    def test_json_events_output_contains_schema_metadata_and_contract_fields(self):
        exit_code, payload = run_json_cli(["run", "nominal-deploy", "--view", "events", "--format", "json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema"]["schema_version"], "1.0")
        self.assertEqual(payload["schema"]["view"], "events")
        self.assertEqual(payload["schema"]["scenario_name"], "nominal-deploy")
        self.assertIn("event_count", payload)
        self.assertIn("events", payload)

    def test_json_explain_output_contains_schema_metadata_and_contract_fields(self):
        exit_code, payload = run_json_cli(
            ["run", "nominal-deploy", "--view", "explain", "--logic", "logic3", "--time", "1.8", "--format", "json"]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema"]["schema_version"], "1.0")
        self.assertEqual(payload["schema"]["view"], "explain")
        self.assertEqual(payload["schema"]["scenario_name"], "nominal-deploy")
        self.assertIn("time_s", payload)
        self.assertIn("logic", payload)

    def test_event_view_renders_transition_lines(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["run", "nominal-deploy", "--view", "events", "--full"])

        output = buffer.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("sw1:0->1", output)
        self.assertIn("logic4_active:0->1", output)

    def test_explain_view_renders_failed_threshold_condition(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["run", "nominal-deploy", "--view", "explain", "--logic", "logic3", "--time", "1.8"])

        output = buffer.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("logic=logic3 active=0", output)
        self.assertIn("tra_deg -7 <= -11.74 0", output)
        self.assertIn("failed: tra_deg", output)

    def test_diagnose_view_renders_logic_transition_explain_delta(self):
        exit_code, output = run_cli_text(["run", "nominal-deploy", "--view", "diagnose", "--logic", "logic3", "--full"])

        self.assertEqual(exit_code, 0)
        self.assertIn("time=1.9 logic=logic3 active=0->1 rows=1.8->1.9", output)
        self.assertIn("before_failed: tra_deg", output)
        self.assertIn("after_failed: (none)", output)
        self.assertIn("changed: tra_deg:passed=0->1 current=-7->-14 threshold=-11.74", output)
        self.assertIn("context: controller_outputs.eec_deploy_cmd:0->1", output)
        self.assertIn("controller_outputs.pls_power_cmd:0->1", output)
        self.assertIn("plant_state.tls_powered_s:1.3->1.4", output)

    def test_json_diagnose_output_is_structured(self):
        exit_code, payload = run_json_cli(["run", "nominal-deploy", "--view", "diagnose", "--logic", "logic3", "--format", "json"])
        diagnosis = payload["diagnostics"][0]
        change = diagnosis["changed_conditions"][0]
        context_changes = {
            (item["field_group"], item["field_name"]): item
            for item in diagnosis["context_changes"]
        }

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema"]["schema_version"], "1.0")
        self.assertEqual(payload["schema"]["view"], "diagnose")
        self.assertEqual(payload["schema"]["scenario_name"], "nominal-deploy")
        self.assertEqual(payload["diagnostic_count"], 1)
        self.assertEqual(diagnosis["logic_name"], "logic3")
        self.assertEqual(diagnosis["before_failed_conditions"], ["tra_deg"])
        self.assertEqual(diagnosis["after_failed_conditions"], [])
        self.assertEqual(change["name"], "tra_deg")
        self.assertFalse(change["before_passed"])
        self.assertTrue(change["after_passed"])
        self.assertFalse(context_changes[("controller_outputs", "eec_deploy_cmd")]["before_value"])
        self.assertTrue(context_changes[("controller_outputs", "eec_deploy_cmd")]["after_value"])
        self.assertGreater(
            context_changes[("plant_state", "tls_powered_s")]["after_value"],
            context_changes[("plant_state", "tls_powered_s")]["before_value"],
        )

    def test_json_outputs_match_contract_assets(self):
        for fixture_name in CONTRACT_FIXTURE_NAMES:
            with self.subTest(fixture_name=fixture_name):
                contract = load_contract(fixture_name)
                exit_code, payload = run_json_cli(contract["command"])

                self.assertEqual(exit_code, 0)
                assert_contract_matches_payload(self, contract, payload)

    def test_json_schema_document_matches_contract_fixtures(self):
        schema_document = load_json_schema_document()
        schema_contract = schema_document["x-well-harness-debug"]
        schema_defs = schema_document["$defs"]
        contracts = [load_contract(fixture_name) for fixture_name in CONTRACT_FIXTURE_NAMES]
        fixture_schemas = [contract["schema"] for contract in contracts]

        self.assertEqual(schema_document["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema_contract["schema_name"], "well_harness.debug")
        self.assertEqual({item["name"] for item in fixture_schemas}, {schema_contract["schema_name"]})
        self.assertEqual({item["schema_version"] for item in fixture_schemas}, {schema_contract["schema_version"]})
        self.assertEqual({item["view"] for item in fixture_schemas}, set(schema_contract["views"]))

        schema_metadata = schema_defs["schemaMetadata"]
        self.assertEqual(schema_metadata["properties"]["name"]["const"], schema_contract["schema_name"])
        self.assertEqual(schema_metadata["properties"]["schema_version"]["const"], schema_contract["schema_version"])
        self.assertEqual(set(schema_metadata["properties"]["view"]["enum"]), set(schema_contract["views"]))

        expected_payload_defs = {
            "timeline": "timelinePayload",
            "events": "eventsPayload",
            "explain": "explainPayload",
            "diagnose": "diagnosePayload",
        }
        self.assertEqual(
            {entry["$ref"] for entry in schema_document["oneOf"]},
            {f"#/$defs/{definition_name}" for definition_name in expected_payload_defs.values()},
        )
        for contract in contracts:
            view = contract["schema"]["view"]
            payload_def = schema_defs[expected_payload_defs[view]]
            self.assertEqual(set(payload_def["required"]), set(contract["required_top_level_fields"]))

        diagnose_properties = schema_defs["logicTransitionDiagnosis"]["properties"]
        self.assertIn("context_changes", diagnose_properties)
        self.assertEqual(
            diagnose_properties["context_changes"]["items"]["$ref"],
            "#/$defs/traceFieldValueChange",
        )
        self.assertEqual(
            set(schema_defs["traceFieldValueChange"]["required"]),
            {"field_group", "field_name", "before_value", "after_value"},
        )

    def test_json_schema_nested_defs_match_contract_representative_fields(self):
        schema_document = load_json_schema_document()
        schema_defs = schema_document["$defs"]
        timeline_contract = load_contract("timeline_contract_v1.json")
        explain_contract = load_contract("explain_contract_v1.json")
        diagnose_contract = load_contract("diagnose_contract_v1.json")

        expected_defs = {
            "pilotInputs",
            "resolvedInputs",
            "plantSensors",
            "plantDebugState",
            "controllerOutputs",
            "controllerExplain",
            "logicExplain",
            "logicConditionExplain",
            "logicTransitionDiagnosis",
            "traceFieldValueChange",
            "contextControllerOutputFieldName",
            "contextPlantSensorFieldName",
            "contextPlantStateFieldName",
        }
        self.assertTrue(expected_defs.issubset(schema_defs.keys()))

        trace_row_properties = schema_defs["traceRow"]["properties"]
        for section_name, definition_name in TRACE_ROW_SECTION_SCHEMA_DEFS.items():
            self.assertEqual(
                trace_row_properties[section_name]["$ref"],
                f"#/$defs/{definition_name}",
            )

        for section_name, required_fields in timeline_contract["required_row_sections"].items():
            definition_name = TRACE_ROW_SECTION_SCHEMA_DEFS[section_name]
            section_schema = schema_defs[definition_name]
            required_field_set = set(required_fields)

            self.assertTrue(required_field_set.issubset(section_schema["required"]))
            self.assertTrue(required_field_set.issubset(section_schema["properties"]))

        logic_explain = schema_defs["logicExplain"]
        self.assertTrue(set(explain_contract["required_logic_fields"]).issubset(logic_explain["required"]))
        self.assertEqual(
            logic_explain["properties"]["conditions"]["items"]["$ref"],
            "#/$defs/logicConditionExplain",
        )
        self.assertTrue(
            set(explain_contract["required_condition_fields"]).issubset(
                schema_defs["logicConditionExplain"]["required"]
            )
        )

        diagnosis = schema_defs["logicTransitionDiagnosis"]
        self.assertTrue(set(diagnose_contract["required_diagnostic_fields"]).issubset(diagnosis["required"]))
        self.assertEqual(
            diagnosis["properties"]["context_changes"]["items"]["$ref"],
            "#/$defs/traceFieldValueChange",
        )
        self.assertTrue(
            set(diagnose_contract["required_context_change_fields"]).issubset(
                schema_defs["traceFieldValueChange"]["required"]
            )
        )

    def test_json_schema_context_field_sets_match_contract_and_runtime_fields(self):
        schema_document = load_json_schema_document()
        schema_defs = schema_document["$defs"]
        diagnose_contract = load_contract("diagnose_contract_v1.json")
        fixture_context_fields = {
            field_group: tuple(field_names)
            for field_group, field_names in diagnose_contract["supported_context_fields"].items()
        }

        schema_context_fields = schema_context_fields_by_group(schema_defs)
        runtime_context_fields = group_context_fields(DIAGNOSIS_CONTEXT_FIELDS)

        self.assertEqual(schema_context_fields, fixture_context_fields)
        self.assertEqual(schema_context_fields, runtime_context_fields)
        self.assertEqual(
            set(CONTEXT_FIELD_NAME_SCHEMA_DEFS),
            set(schema_context_fields),
        )

        trace_field_change = schema_defs["traceFieldValueChange"]
        branch_definitions = {
            branch["properties"]["field_group"]["const"]:
            branch["properties"]["field_name"]["$ref"].rsplit("/", maxsplit=1)[-1]
            for branch in trace_field_change["oneOf"]
        }
        self.assertEqual(branch_definitions, CONTEXT_FIELD_NAME_SCHEMA_DEFS)

        schema_context_change_keys = {
            (field_group, field_name)
            for field_group, field_names in schema_context_fields.items()
            for field_name in field_names
        }
        required_context_change_keys = {
            (item["field_group"], item["field_name"])
            for item in diagnose_contract["required_context_changes"]
        }
        self.assertTrue(required_context_change_keys.issubset(schema_context_change_keys))
        self.assertEqual(
            schema_defs["logicTransitionDiagnosis"]["properties"]["context_changes"]["items"]["$ref"],
            "#/$defs/traceFieldValueChange",
        )

    def test_optional_jsonschema_validates_contract_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema_document = load_json_schema_document()
        Draft202012Validator.check_schema(schema_document)
        validator = Draft202012Validator(schema_document)

        for fixture_name in CONTRACT_FIXTURE_NAMES:
            with self.subTest(fixture_name=fixture_name):
                contract = load_contract(fixture_name)
                exit_code, payload = run_json_cli(contract["command"])
                errors = sorted(
                    validator.iter_errors(payload),
                    key=lambda error: tuple(error.absolute_path),
                )

                self.assertEqual(exit_code, 0)
                self.assertEqual(
                    [],
                    errors,
                    "\n".join(format_validation_error(error) for error in errors[:10]),
                )

    def test_validation_script_smoke(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = run_validation_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: validated", result.stdout)
        self.assertNotIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)

    def test_validation_script_smoke_forced_skip(self):
        result = run_validation_script(**{FORCE_JSONSCHEMA_MISSING_ENV: "1"})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "SKIP: optional dependency 'jsonschema' is not installed",
            result.stdout,
        )
        self.assertNotIn("PASS: validated", result.stdout)

    def test_validation_script_smoke_forced_fail(self):
        missing_schema_path = PROJECT_ROOT / "tests" / "fixtures" / "_missing_debug_schema_for_smoke_test.json"
        self.assertFalse(missing_schema_path.exists())

        result = run_validation_script(**{FORCE_SCHEMA_PATH_ENV: str(missing_schema_path)})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL schema: unable to use", result.stdout)
        self.assertIn(str(missing_schema_path), result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)

    def test_validation_script_smoke_forced_cli_failure(self):
        result = run_validation_script(**{FORCE_CONTRACT_PATH_ENV: str(FAIL_CLI_CONTRACT_PATH)})

        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"FAIL explain: CLI exited with status \d+")
        self.assertIn("detail: cli_error.missing_logic_for_explain", result.stdout)
        self.assertIn(str(FAIL_CLI_CONTRACT_PATH), result.stdout)
        self.assertNotIn("--logic is required with --view explain", result.stdout)
        self.assertNotIn("usage:", result.stdout)
        self.assertNotIn("well_harness: error:", result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_script_smoke_forced_invalid_logic_choice(self):
        result = run_validation_script(**{FORCE_CONTRACT_PATH_ENV: str(FAIL_INVALID_LOGIC_CONTRACT_PATH)})

        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"FAIL explain: CLI exited with status \d+")
        self.assertIn("detail: cli_error.invalid_logic_choice", result.stdout)
        self.assertIn(str(FAIL_INVALID_LOGIC_CONTRACT_PATH), result.stdout)
        self.assertNotIn("invalid choice: 'logic9'", result.stdout)
        self.assertNotIn("usage:", result.stdout)
        self.assertNotIn("well_harness: error:", result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_script_smoke_forced_invalid_scenario_choice(self):
        result = run_validation_script(**{FORCE_CONTRACT_PATH_ENV: str(FAIL_INVALID_SCENARIO_CONTRACT_PATH)})

        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"FAIL timeline: CLI exited with status \d+")
        self.assertIn("detail: cli_error.invalid_scenario_choice", result.stdout)
        self.assertIn(str(FAIL_INVALID_SCENARIO_CONTRACT_PATH), result.stdout)
        self.assertNotIn("invalid choice: 'nominal-deploy-typo'", result.stdout)
        self.assertNotIn("usage:", result.stdout)
        self.assertNotIn("well_harness: error:", result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_script_smoke_forced_unclassified_cli_failure(self):
        result = run_validation_script(**{FORCE_CONTRACT_PATH_ENV: str(FAIL_UNCLASSIFIED_CONTRACT_PATH)})

        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"FAIL timeline: CLI exited with status \d+")
        self.assertIn("detail: cli_error.unclassified", result.stdout)
        self.assertIn(str(FAIL_UNCLASSIFIED_CONTRACT_PATH), result.stdout)
        self.assertNotIn("argument --view: invalid choice:", result.stdout)
        self.assertNotIn("usage:", result.stdout)
        self.assertNotIn("well_harness: error:", result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_script_smoke_forced_schema_validation_failure(self):
        timeline_contract_path = FIXTURES_DIR / "timeline_contract_v1.json"

        result = run_validation_script(
            **{
                FORCE_SCHEMA_PATH_ENV: str(MISMATCH_SCHEMA_PATH),
                FORCE_CONTRACT_PATH_ENV: str(timeline_contract_path),
            }
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL timeline: schema validation errors", result.stdout)
        self.assertIn("impossible_top_level_field", result.stdout)
        self.assertNotIn("PASS: validated", result.stdout)

    def test_validation_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = run_validation_script(["--format", "json"])
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
        self.assertEqual(len(payload["results"]), 4)
        self.assertEqual({item["status"] for item in payload["results"]}, {"pass"})
        self.assertEqual(
            {item["view"] for item in payload["results"]},
            {"timeline", "events", "explain", "diagnose"},
        )
        self.assertIn("tests/fixtures/timeline_contract_v1.json", {item["contract_path"] for item in payload["results"]})
        self.assertEqual(result.stderr, "")

    def test_validation_script_json_skip_output(self):
        result = run_validation_script(["--format", "json"], **{FORCE_JSONSCHEMA_MISSING_ENV: "1"})
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["status"], "skip")
        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
        self.assertEqual(payload["results"], [])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])
        self.assertEqual(result.stderr, "")

    def test_validation_script_json_fail_output(self):
        result = run_validation_script(["--format", "json"], **{FORCE_CONTRACT_PATH_ENV: str(FAIL_CLI_CONTRACT_PATH)})
        payload = json.loads(result.stdout)
        failure = payload["results"][0]

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["schema_path"], "docs/json_schema/well_harness_debug_v1.schema.json")
        self.assertEqual(payload["failure_kind"], "cli_exit")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(failure["status"], "fail")
        self.assertEqual(failure["view"], "explain")
        self.assertEqual(failure["contract_path"], "tests/fixtures/_validation_fail_cli_contract.json")
        self.assertEqual(failure["failure_kind"], "cli_exit")
        self.assertEqual(failure["detail"], "cli_error.missing_logic_for_explain")
        self.assertEqual(failure["exit_code"], 2)
        self.assertNotIn("usage:", result.stdout)
        self.assertNotIn("well_harness: error:", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_script_json_outputs_match_contract_asset(self):
        contract = load_validation_report_contract()

        for scenario in contract["scenarios"]:
            with self.subTest(scenario=scenario["name"]):
                env_overrides = resolve_validation_contract_env(scenario.get("env", {}))
                result = run_validation_script(scenario["args"], **env_overrides)
                payload = json.loads(result.stdout)

                self.assertEqual(payload["status"], scenario["expected_status"])
                self.assertEqual(
                    payload["schema_path"],
                    scenario.get("expected_schema_path", contract["schema_path"]),
                )
                for field_name in contract["required_top_level_fields"]:
                    self.assertIn(field_name, payload)

                self.assertEqual(len(payload["results"]), scenario["expected_result_count"])
                for item in payload["results"]:
                    for field_name in contract["required_result_fields"]:
                        self.assertIn(field_name, item)

                if scenario["expected_status"] == "skip":
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(scenario["expected_reason_contains"], payload["reason"])
                elif scenario["expected_status"] == "pass":
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        {item["status"] for item in payload["results"]},
                        {scenario["expected_result_status"]},
                    )
                    self.assertEqual(
                        {item["view"] for item in payload["results"]},
                        set(scenario["expected_views"]),
                    )
                    self.assertEqual(
                        {item["contract_path"] for item in payload["results"]},
                        set(scenario["expected_contract_paths"]),
                    )
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(payload["failure_kind"], scenario["expected_failure_kind"])
                    if "expected_reason_contains" in scenario:
                        self.assertIn(scenario["expected_reason_contains"], payload["reason"])
                    if "expected_result_fields" in scenario:
                        self.assertEqual(payload["results"][0], scenario["expected_result_fields"])

                self.assertEqual(result.stderr, "")

    def test_validation_report_schema_document_matches_asset(self):
        schema_document = load_validation_report_schema_document()
        schema_contract = schema_document["x-well-harness-validation-report"]
        schema_defs = schema_document["$defs"]
        asset_contract = load_validation_report_contract()

        self.assertEqual(schema_document["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_report")
        self.assertEqual(schema_contract["schema_version"], "1.0")

        self.assertEqual(
            {entry["$ref"] for entry in schema_document["oneOf"]},
            {
                "#/$defs/passReport",
                "#/$defs/skipReport",
                "#/$defs/failReport",
            },
        )

        report_base = schema_defs["reportBase"]
        result_base = schema_defs["resultBase"]

        self.assertEqual(
            set(asset_contract["required_top_level_fields"]),
            set(schema_contract["top_level_fields"]),
        )
        self.assertEqual(
            set(asset_contract["required_top_level_fields"]),
            set(report_base["required"]),
        )
        self.assertTrue(
            set(asset_contract["required_top_level_fields"]).issubset(report_base["properties"])
        )
        self.assertEqual(report_base["properties"]["schema_path"]["type"], "string")

        self.assertEqual(
            set(asset_contract["required_result_fields"]),
            set(schema_contract["result_fields"]),
        )
        self.assertEqual(
            set(asset_contract["required_result_fields"]),
            set(result_base["required"]),
        )
        self.assertTrue(
            set(asset_contract["required_result_fields"]).issubset(result_base["properties"])
        )

        self.assertEqual(
            set(schema_contract["report_statuses"]),
            {"pass", "skip", "fail"},
        )
        self.assertEqual(
            set(schema_contract["result_statuses"]),
            {"pass", "fail"},
        )
        self.assertEqual(
            set(schema_contract["failure_kinds"]),
            set(schema_defs["failureKind"]["enum"]),
        )

        skip_scenario = next(item for item in asset_contract["scenarios"] if item["name"] == "skip")
        fail_scenarios = [
            item for item in asset_contract["scenarios"]
            if item["expected_status"] == "fail"
        ]
        fail_schema_unavailable = next(
            item for item in fail_scenarios
            if item["expected_failure_kind"] == "schema_unavailable"
        )
        fail_schema_validation = next(
            item for item in fail_scenarios
            if item["expected_failure_kind"] == "schema_validation"
        )

        self.assertIn("reason", schema_defs["skipReport"]["allOf"][1]["required"])
        self.assertEqual(
            schema_defs["skipReport"]["allOf"][1]["properties"]["results"]["maxItems"],
            0,
        )
        self.assertIn(skip_scenario["expected_status"], schema_contract["report_statuses"])

        self.assertIn("failure_kind", schema_defs["failReport"]["allOf"][1]["required"])
        self.assertTrue(
            {item["expected_failure_kind"] for item in fail_scenarios}.issubset(
                schema_contract["failure_kinds"]
            )
        )
        self.assertIn("reason", report_base["properties"])
        self.assertIn(
            fail_schema_unavailable["expected_reason_contains"],
            fail_schema_unavailable["env"]["WELL_HARNESS_FORCE_SCHEMA_PATH"],
        )
        for field_name in fail_schema_validation["expected_result_fields"]:
            self.assertIn(field_name, result_base["properties"])

    def test_optional_jsonschema_validates_validation_report_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema_document = load_validation_report_schema_document()
        Draft202012Validator.check_schema(schema_document)
        validator = Draft202012Validator(schema_document)
        asset_contract = load_validation_report_contract()

        for scenario in asset_contract["scenarios"]:
            with self.subTest(scenario=scenario["name"]):
                env_overrides = resolve_validation_contract_env(scenario.get("env", {}))
                result = run_validation_script(scenario["args"], **env_overrides)
                payload = json.loads(result.stdout)
                errors = sorted(
                    validator.iter_errors(payload),
                    key=lambda error: tuple(error.absolute_path),
                )

                self.assertEqual(
                    [],
                    errors,
                    "\n".join(format_validation_error(error) for error in errors[:10]),
                )
                self.assertEqual(payload["status"], scenario["expected_status"])
                self.assertEqual(result.stderr, "")

    def test_validation_report_schema_standalone_script_smoke(self):
        result = run_validation_report_schema_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.assertIn(
                "SKIP: optional dependency 'jsonschema' is not installed",
                result.stdout,
            )
            self.assertNotIn("PASS: validated", result.stdout)
        else:
            self.assertIn("OK pass: validated validation report status=pass", result.stdout)
            self.assertIn("OK skip: validated validation report status=skip", result.stdout)
            self.assertIn("OK fail_cli: validated validation report status=fail", result.stdout)
            self.assertIn(
                "OK fail_schema_unavailable: validated validation report status=fail",
                result.stdout,
            )
            self.assertIn(
                "OK fail_schema_validation: validated validation report status=fail",
                result.stdout,
            )
            self.assertIn("PASS: validated 5 validation report payloads", result.stdout)
            self.assertIn("docs/json_schema/validation_report_v1.schema.json", result.stdout)
            self.assertNotIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_report_schema_standalone_script_forced_skip(self):
        result = run_validation_report_schema_script(**{FORCE_JSONSCHEMA_MISSING_ENV: "1"})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "SKIP: optional dependency 'jsonschema' is not installed",
            result.stdout,
        )
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_report_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        asset = load_validation_schema_runner_report_asset()
        pass_contract = asset["pass"]
        result = run_validation_report_schema_script(asset["command"])
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], pass_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(len(payload["results"]), pass_contract["expected_result_count"])
        self.assertEqual(
            {item["scenario"] for item in payload["results"]},
            set(pass_contract["expected_scenarios"]),
        )
        for item in payload["results"]:
            for field_name in asset["required_result_fields"]:
                self.assertIn(field_name, item)
            self.assertEqual(item["validation_status"], pass_contract["expected_validation_status"])
            self.assertEqual(
                item["report_status"],
                pass_contract["expected_scenario_report_statuses"][item["scenario"]],
            )
        self.assertEqual(result.stderr, "")

    def test_validation_report_schema_standalone_script_json_skip_output(self):
        asset = load_validation_schema_runner_report_asset()
        skip_contract = asset["skip"]
        result = run_validation_report_schema_script(
            asset["command"],
            **skip_contract["env"],
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], skip_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(payload["results"], [])
        self.assertEqual(len(payload["results"]), skip_contract["expected_result_count"])
        self.assertIn(skip_contract["expected_reason_contains"], payload["reason"])
        self.assertEqual(result.stderr, "")

    def test_validation_report_schema_standalone_script_json_fail_output(self):
        asset = load_validation_schema_runner_report_asset()
        fail_contract = asset["fail"]
        result = run_validation_report_schema_script(
            asset["command"],
            **fail_contract["env"],
        )
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], fail_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(payload["failure_kind"], fail_contract["expected_failure_kind"])
        self.assertEqual(len(payload["results"]), fail_contract["expected_result_count"])
        for field_name in asset["required_result_fields"]:
            self.assertIn(field_name, payload["results"][0])
        self.assertEqual(payload["results"][0], fail_contract["expected_result_fields"])
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_document_matches_asset(self):
        schema_document = load_validation_schema_runner_report_schema_document()
        schema_contract = schema_document["x-well-harness-validation-schema-runner-report"]
        schema_defs = schema_document["$defs"]
        asset = load_validation_schema_runner_report_asset()

        self.assertEqual(schema_document["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_schema_runner_report")
        self.assertEqual(schema_contract["schema_version"], "1.0")
        self.assertEqual(
            {entry["$ref"] for entry in schema_document["oneOf"]},
            {
                "#/$defs/passReport",
                "#/$defs/skipReport",
                "#/$defs/failReport",
            },
        )

        report_base = schema_defs["reportBase"]
        result_base = schema_defs["resultBase"]

        self.assertEqual(
            set(asset["required_top_level_fields"]),
            set(schema_contract["top_level_fields"]),
        )
        self.assertEqual(
            set(asset["required_top_level_fields"]),
            set(report_base["required"]),
        )
        self.assertTrue(set(asset["required_top_level_fields"]).issubset(report_base["properties"]))
        self.assertIn("failure_kind", report_base["properties"])
        self.assertIn("reason", report_base["properties"])

        self.assertEqual(
            set(asset["required_result_fields"]),
            set(schema_contract["result_fields"]),
        )
        self.assertTrue(set(asset["required_result_fields"]).issubset(result_base["properties"]))
        self.assertIn("expected_report_status", result_base["properties"])
        self.assertIn("errors", result_base["properties"])

        self.assertEqual(
            set(schema_contract["report_statuses"]),
            set(report_base["properties"]["status"]["enum"]),
        )
        self.assertEqual(
            set(schema_contract["validation_statuses"]),
            set(result_base["properties"]["validation_status"]["enum"]),
        )
        self.assertEqual(
            set(schema_contract["failure_kinds"]),
            set(schema_defs["failureKind"]["enum"]),
        )

        self.assertEqual(schema_defs["skipReport"]["allOf"][1]["properties"]["results"]["maxItems"], 0)
        self.assertIn(asset["skip"]["expected_status"], schema_contract["report_statuses"])
        self.assertIn(asset["fail"]["expected_failure_kind"], schema_contract["failure_kinds"])
        for field_name in asset["fail"]["expected_result_fields"]:
            self.assertIn(field_name, result_base["properties"])

    def test_validation_schema_checker_report_schema_document_matches_asset(self):
        schema_document = load_validation_schema_checker_report_schema_document()
        schema_contract = schema_document["x-well-harness-validation-schema-checker-report"]
        schema_defs = schema_document["$defs"]
        asset = load_validation_schema_checker_report_asset()

        self.assertEqual(schema_document["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema_contract["schema_name"], "well_harness.validation_schema_checker_report")
        self.assertEqual(schema_contract["schema_version"], "1.0")
        self.assertEqual(
            {entry["$ref"] for entry in schema_document["oneOf"]},
            {
                "#/$defs/passReport",
                "#/$defs/skipReport",
                "#/$defs/failReport",
            },
        )

        report_base = schema_defs["reportBase"]
        result_base = schema_defs["resultBase"]

        self.assertEqual(
            set(asset["required_top_level_fields"]),
            set(schema_contract["top_level_fields"]),
        )
        self.assertEqual(
            set(asset["required_top_level_fields"]),
            set(report_base["required"]),
        )
        self.assertTrue(set(asset["required_top_level_fields"]).issubset(report_base["properties"]))
        self.assertIn("failure_kind", report_base["properties"])
        self.assertIn("reason", report_base["properties"])

        self.assertEqual(
            set(asset["required_result_fields"]),
            set(schema_contract["result_fields"]),
        )
        self.assertTrue(set(asset["required_result_fields"]).issubset(result_base["properties"]))
        self.assertIn("expected_payload_status", result_base["properties"])
        self.assertIn("errors", result_base["properties"])
        self.assertIn("reason", result_base["properties"])

        self.assertEqual(
            set(schema_contract["report_statuses"]),
            set(schema_defs["reportStatus"]["enum"]),
        )
        self.assertEqual(
            set(schema_contract["payload_statuses"]),
            set(schema_defs["payloadStatus"]["enum"]),
        )
        self.assertEqual(
            set(schema_contract["validation_statuses"]),
            set(schema_defs["validationStatus"]["enum"]),
        )
        self.assertEqual(
            set(schema_contract["failure_kinds"]),
            set(schema_defs["failureKind"]["enum"]),
        )

        self.assertEqual(schema_defs["skipReport"]["allOf"][1]["properties"]["results"]["maxItems"], 0)
        self.assertIn(asset["pass"]["expected_status"], schema_contract["report_statuses"])
        self.assertIn(asset["skip"]["expected_status"], schema_contract["report_statuses"])
        self.assertIn(asset["fail"]["expected_failure_kind"], schema_contract["failure_kinds"])
        for field_name in asset["fail"]["expected_result_fields"]:
            self.assertIn(field_name, result_base["properties"])

    def test_optional_jsonschema_validates_validation_schema_runner_report_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema_document = load_validation_schema_runner_report_schema_document()
        Draft202012Validator.check_schema(schema_document)
        validator = Draft202012Validator(schema_document)
        asset = load_validation_schema_runner_report_asset()

        for scenario_name in ("pass", "skip", "fail"):
            with self.subTest(scenario=scenario_name):
                scenario_contract = asset[scenario_name]
                result = run_validation_report_schema_script(
                    asset["command"],
                    **scenario_contract.get("env", {}),
                )
                payload = json.loads(result.stdout)
                errors = sorted(
                    validator.iter_errors(payload),
                    key=lambda error: tuple(error.absolute_path),
                )

                self.assertEqual(
                    [],
                    errors,
                    "\n".join(format_validation_error(error) for error in errors[:10]),
                )
                self.assertEqual(payload["status"], scenario_contract["expected_status"])
                if scenario_contract["expected_status"] == "fail":
                    self.assertNotEqual(result.returncode, 0)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")

    def test_optional_jsonschema_validates_validation_schema_checker_report_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema_document = load_validation_schema_checker_report_schema_document()
        Draft202012Validator.check_schema(schema_document)
        validator = Draft202012Validator(schema_document)
        asset = load_validation_schema_checker_report_asset()

        for scenario_name in ("pass", "skip", "fail"):
            with self.subTest(scenario=scenario_name):
                scenario_contract = asset[scenario_name]
                result = run_validation_schema_runner_report_schema_script(
                    asset["command"],
                    **scenario_contract.get("env", {}),
                )
                payload = json.loads(result.stdout)
                errors = sorted(
                    validator.iter_errors(payload),
                    key=lambda error: tuple(error.absolute_path),
                )

                self.assertEqual(
                    [],
                    errors,
                    "\n".join(format_validation_error(error) for error in errors[:10]),
                )
                self.assertEqual(payload["status"], scenario_contract["expected_status"])
                if scenario_contract["expected_status"] == "fail":
                    self.assertNotEqual(result.returncode, 0)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")

    def test_validation_schema_checker_report_schema_standalone_script_smoke(self):
        result = run_validation_schema_checker_report_schema_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.assertIn(
                "SKIP: optional dependency 'jsonschema' is not installed",
                result.stdout,
            )
            self.assertNotIn("PASS: validated", result.stdout)
        else:
            self.assertIn("OK pass: validated validation schema checker report status=pass", result.stdout)
            self.assertIn("OK skip: validated validation schema checker report status=skip", result.stdout)
            self.assertIn("OK fail: validated validation schema checker report status=fail", result.stdout)
            self.assertIn("PASS: validated 3 validation schema checker report payloads", result.stdout)
            self.assertIn("docs/json_schema/validation_schema_checker_report_v1.schema.json", result.stdout)
            self.assertNotIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_schema_checker_report_schema_standalone_script_forced_skip(self):
        result = run_validation_schema_checker_report_schema_script(
            **{FORCE_JSONSCHEMA_MISSING_ENV: "1"}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "SKIP: optional dependency 'jsonschema' is not installed",
            result.stdout,
        )
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_standalone_script_smoke(self):
        result = run_validation_schema_runner_report_schema_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.assertIn(
                "SKIP: optional dependency 'jsonschema' is not installed",
                result.stdout,
            )
            self.assertNotIn("PASS: validated", result.stdout)
        else:
            self.assertIn("OK pass: validated validation schema runner report status=pass", result.stdout)
            self.assertIn("OK skip: validated validation schema runner report status=skip", result.stdout)
            self.assertIn("OK fail: validated validation schema runner report status=fail", result.stdout)
            self.assertIn("PASS: validated 3 validation schema runner report payloads", result.stdout)
            self.assertIn("docs/json_schema/validation_schema_runner_report_v1.schema.json", result.stdout)
            self.assertNotIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_standalone_script_forced_skip(self):
        result = run_validation_schema_runner_report_schema_script(
            **{FORCE_JSONSCHEMA_MISSING_ENV: "1"}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "SKIP: optional dependency 'jsonschema' is not installed",
            result.stdout,
        )
        self.assertNotIn("PASS: validated", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        asset = load_validation_schema_checker_report_asset()
        pass_contract = asset["pass"]
        result = run_validation_schema_runner_report_schema_script(asset["command"])
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], pass_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(len(payload["results"]), pass_contract["expected_result_count"])
        self.assertEqual(
            {item["scenario"] for item in payload["results"]},
            set(pass_contract["expected_scenarios"]),
        )
        self.assertEqual(
            {item["validation_status"] for item in payload["results"]},
            {pass_contract["expected_validation_status"]},
        )
        self.assertEqual(
            {item["payload_status"] for item in payload["results"]},
            set(pass_contract["expected_scenario_payload_statuses"].values()),
        )
        for item in payload["results"]:
            for field_name in asset["required_result_fields"]:
                self.assertIn(field_name, item)
            self.assertEqual(
                item["payload_status"],
                pass_contract["expected_scenario_payload_statuses"][item["scenario"]],
            )
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_standalone_script_json_skip_output(self):
        asset = load_validation_schema_checker_report_asset()
        skip_contract = asset["skip"]
        result = run_validation_schema_runner_report_schema_script(
            asset["command"],
            **skip_contract["env"],
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], skip_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(payload["results"], [])
        self.assertEqual(len(payload["results"]), skip_contract["expected_result_count"])
        self.assertIn(skip_contract["expected_reason_contains"], payload["reason"])
        self.assertEqual(result.stderr, "")

    def test_validation_schema_runner_report_schema_standalone_script_json_fail_output(self):
        asset = load_validation_schema_checker_report_asset()
        fail_contract = asset["fail"]
        result = run_validation_schema_runner_report_schema_script(
            asset["command"],
            **fail_contract["env"],
        )
        payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        for field_name in asset["required_top_level_fields"]:
            self.assertIn(field_name, payload)
        self.assertEqual(payload["status"], fail_contract["expected_status"])
        self.assertEqual(payload["schema_path"], asset["schema_path"])
        self.assertEqual(payload["asset_path"], asset["asset_path"])
        self.assertEqual(payload["failure_kind"], fail_contract["expected_failure_kind"])
        self.assertEqual(len(payload["results"]), fail_contract["expected_result_count"])
        for field_name in asset["required_result_fields"]:
            self.assertIn(field_name, payload["results"][0])
        self.assertEqual(payload["results"][0], fail_contract["expected_result_fields"])
        self.assertEqual(result.stderr, "")

    def test_json_output_is_deterministic_for_same_command(self):
        args = ["run", "nominal-deploy", "--view", "diagnose", "--logic", "logic3", "--format", "json"]

        first_exit_code, first_output = run_cli_text(args)
        second_exit_code, second_output = run_cli_text(args)

        self.assertEqual(first_exit_code, 0)
        self.assertEqual(second_exit_code, 0)
        self.assertEqual(first_output, second_output)


if __name__ == "__main__":
    unittest.main()

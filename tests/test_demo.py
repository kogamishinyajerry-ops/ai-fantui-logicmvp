import io
import http.client
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from well_harness import demo_server
from well_harness.cli import main
from well_harness.demo import NODE_CATALOG, answer_demo_prompt
from well_harness.demo_server import DemoRequestHandler
from well_harness.models import HarnessConfig
from well_harness.workbench_bundle import archive_workbench_bundle, build_workbench_bundle


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DEMO_JSON_OUTPUT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "demo_answer_v1.schema.json"
DEMO_ANSWER_ASSET_PATH = FIXTURES_DIR / "demo_answer_asset_v1.json"
DEMO_JSON_OUTPUT_ASSET_PATH = FIXTURES_DIR / "demo_json_output_asset_v1.json"
DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_demo_answer_schema.py"
DEMO_PATH_SMOKE_SCRIPT_PATH = PROJECT_ROOT / "tools" / "demo_path_smoke.py"
DEMO_UI_HANDCHECK_SCRIPT_PATH = PROJECT_ROOT / "tools" / "demo_ui_handcheck.py"
DEMO_PRESENTER_TALK_TRACK_PATH = PROJECT_ROOT / "docs" / "demo_presenter_talk_track.md"
DEMO_UI_STATIC_DIR = PROJECT_ROOT / "src" / "well_harness" / "static"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def load_demo_answer_asset():
    with DEMO_ANSWER_ASSET_PATH.open(encoding="utf-8") as asset_file:
        return json.load(asset_file)


def load_demo_json_output_asset():
    with DEMO_JSON_OUTPUT_ASSET_PATH.open(encoding="utf-8") as asset_file:
        return json.load(asset_file)


def load_demo_json_output_schema():
    with DEMO_JSON_OUTPUT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def assert_fragments(test_case, fragments, text):
    for fragment in fragments:
        test_case.assertIn(fragment, text)


def demo_answer_schema_script_env(env_overrides=None):
    env = dict(os.environ)
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    env.update(env_overrides or {})
    return env


def start_demo_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def monitor_track_samples(payload):
    tracks = {}
    for track in payload["series"]:
        tracks[track["id"]] = {
            round(float(sample[0]), 3): float(sample[1])
            for sample in track["samples"]
        }
    return tracks


class DemoIntentLayerTests(unittest.TestCase):
    def test_demo_answers_match_lightweight_fixture_contract(self):
        asset = load_demo_answer_asset()

        self.assertEqual(asset["name"], "well_harness.demo_answer.asset")
        self.assertEqual(asset["version"], "1.0")
        self.assertEqual(
            asset["required_answer_fields"],
            ["intent", "matched_node", "target_logic", "evidence", "outcome", "risks"],
        )

        for case in asset["cases"]:
            with self.subTest(prompt=case["prompt"]):
                answer = answer_demo_prompt(case["prompt"])
                evidence = "\n".join(answer.evidence)
                outcome = "\n".join(answer.outcome)
                possible_causes = "\n".join(answer.possible_causes)
                required_changes = "\n".join(answer.required_changes)
                risks = "\n".join(answer.risks)

                self.assertEqual(answer.intent, case["intent"])
                self.assertEqual(answer.matched_node, case["matched_node"])
                self.assertEqual(answer.target_logic, case["target_logic"])
                assert_fragments(self, case["required_evidence_fragments"], evidence)
                assert_fragments(self, case["required_outcome_fragments"], outcome)
                assert_fragments(self, case.get("required_possible_causes_fragments", ()), possible_causes)
                assert_fragments(self, case.get("required_changes_fragments", ()), required_changes)
                assert_fragments(self, case["required_risk_fragments"], risks)

    def test_demo_json_outputs_match_lightweight_fixture_contract(self):
        asset = load_demo_json_output_asset()

        self.assertEqual(asset["name"], "well_harness.demo_json_output.asset")
        self.assertEqual(asset["version"], "1.0")

        for case in asset["cases"]:
            with self.subTest(prompt=case["prompt"]):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = main(["demo", "--format", "json", case["prompt"]])
                payload = json.loads(buffer.getvalue())

                self.assertEqual(exit_code, 0)
                self.assertEqual(sorted(payload), sorted(case["required_top_level_fields"]))
                self.assertEqual(payload["intent"], case["intent"])
                self.assertEqual(payload["matched_node"], case["matched_node"])
                self.assertEqual(payload["target_logic"], case["target_logic"])

                for field_name in asset["required_array_fields"]:
                    self.assertIsInstance(payload[field_name], list)

                assert_fragments(self, case["required_evidence_fragments"], "\n".join(payload["evidence"]))
                assert_fragments(self, case["required_outcome_fragments"], "\n".join(payload["outcome"]))
                assert_fragments(
                    self,
                    case.get("required_possible_causes_fragments", ()),
                    "\n".join(payload["possible_causes"]),
                )
                assert_fragments(
                    self,
                    case.get("required_changes_fragments", ()),
                    "\n".join(payload["required_changes"]),
                )
                assert_fragments(self, case["required_risk_fragments"], "\n".join(payload["risks"]))

    def test_demo_json_output_schema_document_matches_fixture_contract(self):
        schema = load_demo_json_output_schema()
        asset = load_demo_json_output_asset()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertNotIn("status", schema["properties"])

        schema_properties = set(schema["properties"])
        schema_required = set(schema["required"])
        schema_array_fields = {
            field_name
            for field_name, definition in schema["properties"].items()
            if definition == {"$ref": "#/$defs/stringArray"}
        }
        fixture_top_level_fields = {
            field_name
            for case in asset["cases"]
            for field_name in case["required_top_level_fields"]
        }
        fixture_intents = {case["intent"] for case in asset["cases"]}

        self.assertLessEqual(fixture_top_level_fields, schema_properties)
        self.assertLessEqual(fixture_top_level_fields, schema_required)
        self.assertLessEqual(set(asset["required_array_fields"]), schema_array_fields)
        self.assertLessEqual(fixture_intents, set(schema["properties"]["intent"]["enum"]))
        self.assertEqual(
            set(schema["x-well-harness-demo-answer"]["top_level_fields"]),
            fixture_top_level_fields,
        )
        self.assertEqual(
            set(schema["x-well-harness-demo-answer"]["array_fields"]),
            set(asset["required_array_fields"]),
        )

    def test_optional_jsonschema_validates_demo_json_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_demo_json_output_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        asset = load_demo_json_output_asset()

        for case in asset["cases"]:
            with self.subTest(prompt=case["prompt"]):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = main(["demo", "--format", "json", case["prompt"]])
                payload = json.loads(buffer.getvalue())
                errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))

                self.assertEqual(exit_code, 0)
                self.assertEqual([], [f"{list(error.path)}: {error.message}" for error in errors])

    def test_demo_answer_schema_standalone_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("Install it to validate demo JSON payloads.", result.stdout)
        else:
            self.assertIn("OK logic4_thr_lock_bridge", result.stdout)
            self.assertIn("OK blocked_state", result.stdout)
            self.assertIn("OK diagnose_problem", result.stdout)
            self.assertIn("PASS: validated 3 demo JSON payloads", result.stdout)

    def test_demo_answer_schema_standalone_script_forced_skip(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
        self.assertIn("Install it to validate demo JSON payloads.", result.stdout)

    def test_demo_answer_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        asset = load_demo_json_output_asset()
        result = subprocess.run(
            [sys.executable, str(DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["schema_path"], "docs/json_schema/demo_answer_v1.schema.json")
        self.assertEqual(payload["asset_path"], "tests/fixtures/demo_json_output_asset_v1.json")
        self.assertEqual(len(payload["results"]), len(asset["cases"]))
        self.assertEqual(
            {item["prompt"] for item in payload["results"]},
            {case["prompt"] for case in asset["cases"]},
        )
        self.assertEqual(
            {item["intent"] for item in payload["results"]},
            {case["intent"] for case in asset["cases"]},
        )
        for item in payload["results"]:
            self.assertEqual(item["validation_status"], "pass")
            self.assertEqual(item["error_count"], 0)
            self.assertEqual(item["errors"], [])

    def test_demo_answer_schema_standalone_script_json_forced_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(payload["status"], "skip")
        self.assertEqual(payload["schema_path"], "docs/json_schema/demo_answer_v1.schema.json")
        self.assertEqual(payload["asset_path"], "tests/fixtures/demo_json_output_asset_v1.json")
        self.assertEqual(payload["results"], [])
        self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", payload["reason"])

    def test_demo_server_api_returns_demo_json_payload(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "logic4 和 throttle lock 有什么关系"}).encode("utf-8")
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["intent"], "logic4_thr_lock_bridge")
        self.assertEqual(payload["matched_node"], "logic4->thr_lock")
        self.assertEqual(payload["target_logic"], "logic4")
        self.assertIsInstance(payload["evidence"], list)
        self.assertIn(
            "events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True",
            "\n".join(payload["evidence"]),
        )

    def test_demo_server_api_missing_prompt_returns_readable_error_json(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps({"prompt": "   "}).encode("utf-8")
            connection.request(
                "POST",
                "/api/demo",
                body=request_body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 400)
        self.assertEqual(payload, {"error": "missing_prompt"})

    def test_demo_server_api_returns_lever_snapshot_payload_for_key_tra_values(self):
        expected_states = {
            # At TRA=0, L1 is blocked (sw1 not engaged), which cascades to L4 blocked.
            # thr_lock is "blocked" (not "inactive") because L4 has unmet conditions.
            0: {"sw1": "inactive", "logic1": "blocked", "logic3": "blocked", "thr_lock": "blocked"},
            -2: {"sw1": "active", "logic1": "active", "tls115": "active", "sw2": "inactive"},
            -7: {
                "sw1": "active",
                "sw2": "active",
                "logic2": "active",
                "etrac_540v": "active",
                "logic3": "blocked",
            },
            -14: {
                "logic3": "active",
                "eec_deploy": "active",
                "pls_power": "active",
                "pdu_motor": "active",
                "vdt90": "inactive",
                "logic4": "blocked",
                "thr_lock": "blocked",
            },
        }
        server, thread = start_demo_server()
        try:
            for tra_deg, expected in expected_states.items():
                with self.subTest(tra_deg=tra_deg):
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    request_body = json.dumps({"tra_deg": tra_deg}).encode("utf-8")
                    connection.request(
                        "POST",
                        "/api/lever-snapshot",
                        body=request_body,
                        headers={"Content-Type": "application/json"},
                    )
                    response = connection.getresponse()
                    payload = json.loads(response.read().decode("utf-8"))

                    self.assertEqual(response.status, 200)
                    self.assertEqual(payload["mode"], "canonical_pullback_scrubber")
                    self.assertEqual(payload["input"]["tra_deg"], float(tra_deg))
                    self.assertEqual(payload["input"]["radio_altitude_ft"], 5.0)
                    self.assertTrue(payload["input"]["engine_running"])
                    self.assertTrue(payload["input"]["aircraft_on_ground"])
                    self.assertFalse(payload["input"]["reverser_inhibited"])
                    self.assertTrue(payload["input"]["eec_enable"])
                    self.assertEqual(payload["input"]["n1k"], 35.0)
                    self.assertEqual(payload["input"]["max_n1k_deploy_limit"], 60.0)
                    self.assertEqual(payload["input"]["feedback_mode"], "auto_scrubber")
                    self.assertEqual(payload["input"]["deploy_position_percent"], 0.0)
                    self.assertIn("DeployController.evaluate_with_explain", "\n".join(payload["evidence"]))
                    self.assertIn("不是完整飞控实时物理仿真", payload["model_note"])
                    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
                    for node_id, state in expected.items():
                        self.assertEqual(node_states[node_id], state)
                    if tra_deg == -14:
                        self.assertFalse(payload["hud"]["deploy_90_percent_vdt"])
                        self.assertIn("deploy_90_percent_vdt", payload["summary"]["blocker"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_demo_server_api_accepts_extended_lever_snapshot_conditions(self):
        cases = [
            {
                "name": "ra_boundary_blocks_logic1",
                "request": {"tra_deg": -14, "radio_altitude_ft": 6.0},
                "logic_key": "logic1",
                "expected_failed": "radio_altitude_ft",
                "expected_node": ("logic1", "blocked"),
            },
            {
                "name": "engine_off_blocks_logic2_logic3_logic4",
                "request": {"tra_deg": -14, "engine_running": False},
                "logic_key": "logic2",
                "expected_failed": "engine_running",
                "expected_node": ("logic2", "blocked"),
            },
            {
                "name": "aircraft_not_on_ground_blocks_logic2_logic3_logic4",
                "request": {"tra_deg": -14, "aircraft_on_ground": False},
                "logic_key": "logic2",
                "expected_failed": "aircraft_on_ground",
                "expected_node": ("logic2", "blocked"),
            },
            {
                "name": "reverser_inhibited_blocks_logic1_logic2_logic3",
                "request": {"tra_deg": -14, "reverser_inhibited": True},
                "logic_key": "logic1",
                "expected_failed": "reverser_inhibited",
                "expected_node": ("logic1", "blocked"),
            },
            {
                "name": "eec_disable_blocks_logic2",
                "request": {"tra_deg": -14, "eec_enable": False},
                "logic_key": "logic2",
                "expected_failed": "eec_enable",
                "expected_node": ("logic2", "blocked"),
            },
            {
                "name": "n1k_limit_blocks_logic3",
                "request": {"tra_deg": -14, "n1k": 60.0, "max_n1k_deploy_limit": 60.0},
                "logic_key": "logic3",
                "expected_failed": "n1k",
                "expected_node": ("logic3", "blocked"),
            },
        ]

        server, thread = start_demo_server()
        try:
            for case in cases:
                with self.subTest(case=case["name"]):
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    connection.request(
                        "POST",
                        "/api/lever-snapshot",
                        body=json.dumps(case["request"]).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                    )
                    response = connection.getresponse()
                    payload = json.loads(response.read().decode("utf-8"))

                    self.assertEqual(response.status, 200)
                    self.assertEqual(payload["input"]["tra_deg"], float(case["request"]["tra_deg"]))
                    self.assertIn(
                        case["expected_failed"],
                        payload["logic"][case["logic_key"]]["failed_conditions"],
                    )
                    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
                    node_id, node_state = case["expected_node"]
                    self.assertEqual(node_states[node_id], node_state)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_demo_server_api_accepts_manual_feedback_override_for_vdt90_and_logic4(self):
        # With the causal-chain fix, deploy_position_percent override only drives VDT90
        # when L3 (pdu_motor_cmd) is active. L3 requires SW1+SW2 engaged and TRA at
        # threshold (-14°). These test cases provide full L3-enabling parameters so the
        # causal chain can be properly verified.
        cases = [
            {
                "name": "manual_override_below_vdt_threshold",
                "request": {
                    "tra_deg": -14.0,
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 50.0,
                    "sw1": True,
                    "sw2": True,
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": False,
                "expected_logic4_active": False,
                "expected_thr_lock_state": "blocked",
                "expected_logic4_failed": "deploy_90_percent_vdt",
            },
            {
                "name": "manual_override_activates_vdt90",
                "request": {
                    "tra_deg": -14.0,
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 95.0,
                    "sw1": True,
                    "sw2": True,
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": True,
                "expected_logic4_active": True,
                "expected_thr_lock_state": "active",
                "expected_logic4_failed": None,
            },
            {
                "name": "manual_override_still_blocks_logic4_on_engine",
                # With causal chain fix, engine_off makes L3 inactive so VDT90 stays False
                # (engine_running is NOT in manual override — it's a pilot input, not plant state)
                "request": {
                    "tra_deg": -14.0,
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 95.0,
                    "sw1": True,
                    "sw2": True,
                    "engine_running": False,
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": False,  # L3 inactive due to engine_running=False
                "expected_logic4_active": False,
                "expected_thr_lock_state": "blocked",
                # VDT90=True here because L3 IS active (engine_running is not an L3 gate —
                # it's a separate L4 condition), so deploy_90_percent_vdt passes.
                # engine_running=False is the first L4 blocker.
                "expected_logic4_failed": "engine_running",
            },
            {
                # NEW: verify VDT90 is blocked when L3 is inactive (causal chain fix)
                # sw1=False alone doesn't block L3 (sw1 is not an L3 condition), so use
                # a TRA value that won't satisfy L3's tra_deg condition
                "name": "manual_override_blocks_vdt90_when_l3_inactive",
                "request": {
                    "tra_deg": 0.0,  # TRA not at threshold → L3 tra_deg condition fails
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 95.0,
                    "sw1": False,
                    "sw2": True,
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": False,  # VDT90 blocked because L3 inactive (TRA not at threshold)
                "expected_logic4_active": False,
                "expected_thr_lock_state": "blocked",
                # With L3 inactive, deploy_90_percent_vdt is gated False in display even though
                # deploy_position_percent=95.0. tra_deg=0.0 fails L4's between_exclusive(-32,0)
                # check (0.0 is not < 0.0), making it the first unmet L4 condition.
                "expected_logic4_failed": "tra_deg",
            },
        ]

        server, thread = start_demo_server()
        try:
            for case in cases:
                with self.subTest(case=case["name"]):
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    connection.request(
                        "POST",
                        "/api/lever-snapshot",
                        body=json.dumps(case["request"]).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                    )
                    response = connection.getresponse()
                    payload = json.loads(response.read().decode("utf-8"))

                    self.assertEqual(response.status, 200)
                    self.assertEqual(payload["mode"], case["expected_mode"])
                    self.assertEqual(payload["input"]["feedback_mode"], "manual_feedback_override")
                    self.assertEqual(payload["input"]["deploy_position_percent"], case["request"]["deploy_position_percent"])
                    self.assertEqual(payload["hud"]["deploy_90_percent_vdt"], case["expected_vdt90"])

                    node_states = {node["id"]: node["state"] for node in payload["nodes"]}
                    self.assertEqual(node_states["vdt90"], "active" if case["expected_vdt90"] else "inactive")
                    self.assertEqual(node_states["thr_lock"], case["expected_thr_lock_state"])
                    self.assertEqual(payload["outputs"]["logic4_active"], case["expected_logic4_active"])
                    if case["expected_logic4_failed"] is None:
                        self.assertEqual(payload["logic"]["logic4"]["failed_conditions"], [])
                    else:
                        self.assertIn(
                            case["expected_logic4_failed"],
                            payload["logic"]["logic4"]["failed_conditions"],
                        )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request(
                "POST",
                "/api/lever-snapshot",
                body=json.dumps(
                    {
                        "tra_deg": -20.0,
                        "feedback_mode": "manual_feedback_override",
                        "deploy_position_percent": 50.0,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["input"]["requested_tra_deg"], -20.0)
        self.assertEqual(payload["input"]["tra_deg"], -14.0)
        self.assertEqual(payload["hud"]["tra_deg"], -14.0)
        self.assertTrue(payload["tra_lock"]["locked"])
        self.assertTrue(payload["tra_lock"]["clamped"])
        self.assertFalse(payload["tra_lock"]["unlock_ready"])
        self.assertEqual(payload["tra_lock"]["lock_deg"], -14.0)
        self.assertEqual(payload["tra_lock"]["allowed_reverse_min_deg"], -14.0)
        self.assertEqual(payload["tra_lock"]["visual_reverse_min_deg"], HarnessConfig().reverse_travel_min_deg)
        self.assertIn("deploy_90_percent_vdt", payload["tra_lock"]["unlock_blockers"])
        self.assertIn("已锁回 -14.0°", payload["tra_lock"]["message"])
        self.assertIn("当前只能在 -14.0° 到 0.0° 范围内拖动", payload["tra_lock"]["message"])
        self.assertIn("TRA 深拉区仍未开放", payload["summary"]["blocker"])
        self.assertFalse(payload["outputs"]["logic4_active"])

    def test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request(
                "POST",
                "/api/lever-snapshot",
                body=json.dumps(
                    {
                        "tra_deg": -20.0,
                        "feedback_mode": "manual_feedback_override",
                        "deploy_position_percent": 95.0,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["input"]["requested_tra_deg"], -20.0)
        self.assertEqual(payload["input"]["tra_deg"], -20.0)
        self.assertFalse(payload["tra_lock"]["locked"])
        self.assertFalse(payload["tra_lock"]["clamped"])
        self.assertTrue(payload["tra_lock"]["unlock_ready"])
        self.assertEqual(payload["tra_lock"]["allowed_reverse_min_deg"], HarnessConfig().reverse_travel_min_deg)
        self.assertEqual(payload["tra_lock"]["visual_reverse_min_deg"], HarnessConfig().reverse_travel_min_deg)
        self.assertEqual(payload["tra_lock"]["unlock_blockers"], [])
        self.assertIn("TRA 现在可以在 -32.0° 到 0.0° 区间自由拖动", payload["tra_lock"]["message"])
        self.assertTrue(payload["outputs"]["logic4_active"])
        self.assertEqual(
            {node["id"]: node["state"] for node in payload["nodes"]}["thr_lock"],
            "active",
        )

    def test_demo_server_api_unlocks_deep_range_once_l4_boundary_probe_is_ready(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request(
                "POST",
                "/api/lever-snapshot",
                body=json.dumps(
                    {
                        "tra_deg": 0.0,
                        "feedback_mode": "manual_feedback_override",
                        "deploy_position_percent": 95.0,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["input"]["tra_deg"], 0.0)
        self.assertTrue(payload["tra_lock"]["boundary_unlock_ready"])
        self.assertFalse(payload["tra_lock"]["locked"])
        self.assertTrue(payload["tra_lock"]["unlock_ready"])
        self.assertEqual(payload["tra_lock"]["allowed_reverse_min_deg"], HarnessConfig().reverse_travel_min_deg)
        self.assertEqual(payload["tra_lock"]["visual_reverse_min_deg"], HarnessConfig().reverse_travel_min_deg)
        self.assertIn("TRA 现在可以在 -32.0° 到 0.0° 区间自由拖动", payload["tra_lock"]["message"])
        self.assertFalse(payload["outputs"]["logic4_active"])

    def test_demo_server_api_returns_monitor_timeline_payload(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/api/monitor-timeline")
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["mode"], "timeline_monitor")
        self.assertEqual(payload["time_start_s"], 0.0)
        self.assertEqual(payload["time_end_s"], 7.0)
        self.assertEqual(payload["active_end_s"], 4.4)
        self.assertEqual(payload["compression_ratio"], 10.0)
        self.assertIn("整段时间已压缩为原来的 1/10", payload["model_note"])
        self.assertEqual(payload["timeline_summary"]["ra_hits_six_ft_at_s"], 1.0)
        self.assertEqual(payload["timeline_summary"]["tra_reaches_lock_at_s"], 2.4)
        self.assertEqual(payload["timeline_summary"]["vdt_reaches_100_percent_at_s"], 4.4)
        self.assertIn("VDT90", {event["label"] for event in payload["events"]})
        self.assertEqual(
            [track["id"] for track in payload["series"]],
            [
                "ra",
                "tra",
                "sw1",
                "logic1",
                "tls",
                "sw2",
                "logic2",
                "etrac",
                "logic3",
                "eec",
                "pls",
                "pdu",
                "vdt",
                "logic4",
                "thr_lock",
            ],
        )

    def test_demo_server_api_monitor_timeline_matches_key_transition_times(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/api/monitor-timeline")
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        samples = monitor_track_samples(payload)

        self.assertAlmostEqual(samples["ra"][0.0], 7.0)
        self.assertAlmostEqual(samples["ra"][1.0], 6.0)
        self.assertAlmostEqual(samples["ra"][4.4], 2.6)
        self.assertAlmostEqual(samples["ra"][7.0], 0.0)

        self.assertAlmostEqual(samples["tra"][0.0], 0.0)
        self.assertAlmostEqual(samples["tra"][1.0], 0.0)
        self.assertAlmostEqual(samples["tra"][2.4], -14.0)
        self.assertAlmostEqual(samples["tra"][7.0], -14.0)

        self.assertAlmostEqual(samples["vdt"][2.4], 0.0)
        self.assertAlmostEqual(samples["vdt"][4.2], 90.0)
        self.assertAlmostEqual(samples["vdt"][4.4], 100.0)
        self.assertAlmostEqual(samples["vdt"][7.0], 100.0)

        self.assertEqual(samples["logic4"][2.4], 0.0)
        self.assertEqual(samples["logic4"][4.2], 1.0)
        self.assertEqual(samples["thr_lock"][4.2], 1.0)
        self.assertEqual(samples["thr_lock"][7.0], 1.0)

    def test_demo_server_api_rejects_invalid_extended_lever_snapshot_input(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request(
                "POST",
                "/api/lever-snapshot",
                body=json.dumps({"tra_deg": -7, "radio_altitude_ft": "high"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 400)
        self.assertEqual(payload["error"], "invalid_lever_snapshot_input")
        self.assertEqual(payload["field"], "radio_altitude_ft")

    def test_demo_server_serves_static_shell(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/")
            response = connection.getresponse()
            html = response.read().decode("utf-8")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        # Phase A (2026-04-22): chat.html shelved.
        # Phase UI-C (2026-04-22): root URL now serves index.html (2x3 card grid
        # landing page) instead of demo.html, so user can reach all 6 surfaces.
        self.assertIn("<title>FANTUI LogicMVP · 主入口</title>", html)
        self.assertIn("/demo.html", html)
        self.assertIn("/c919_etras_workstation.html", html)
        self.assertIn("/fantui_circuit.html", html)
        self.assertIn("/c919_etras_panel/circuit.html", html)

    def test_demo_html_slim_workstation_structure(self):
        """Slim demo.html (Phase UI-D) must have: unified nav, TRA lever, condition
        panel, HUD, chain SVG with logic1-4 + thr_lock nodes, 4 output cards, 5 presets."""
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        # Unified nav
        self.assertIn('class="unified-nav"', html)
        self.assertIn('/unified-nav.css', html)
        self.assertIn('data-current="true"', html)
        # Key interactive elements
        for fragment in (
            'id="fan-tra-lever"',
            'id="fan-ra"',
            'id="fan-n1k"',
            'id="fan-vdt"',
            'id="fan-engine-running"',
            'id="fan-aircraft-on-ground"',
            'id="fan-reverser-inhibited"',
            'id="fan-eec-enable"',
            'id="fan-feedback-mode"',
            'id="fan-status-badge"',
            'id="fan-chain-svg"',
            'id="fan-out-tls115"',
            'id="fan-out-etrac"',
            'id="fan-out-eec"',
            'id="fan-out-thr"',
        ):
            self.assertIn(fragment, html, f"slim demo.html missing: {fragment}")
        # Chain SVG data-nodes: all 4 logic gates + final output
        for data_node in ("logic1", "logic2", "logic3", "logic4", "thr_lock",
                          "sw1", "sw2", "radio_altitude_ft", "tls_unlocked", "vdt90"):
            self.assertIn(f'data-node="{data_node}"', html,
                          f"chain SVG missing data-node: {data_node}")
        # Presets
        for preset in ("nominal-fwd", "landing-deploy", "max-reverse",
                       "stow-return", "inhibit-block"):
            self.assertIn(f'data-preset="{preset}"', html,
                          f"preset button missing: {preset}")
        # Must NOT contain shelved legacy panels
        for legacy in ("presenter-run-card", "chain-inspector", "landing-gear-inputs",
                       "bleed-air-inputs", "efds-inputs", "monitor-panel",
                       "system-selector", "result-grid"):
            self.assertNotIn(legacy, html,
                             f"slim demo.html must NOT contain legacy: {legacy}")

    def test_demo_js_posts_to_lever_snapshot(self):
        """demo.js should talk to /api/lever-snapshot with debounced POST."""
        js = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")
        self.assertIn('const API_URL = "/api/lever-snapshot"', js)
        self.assertIn("buildRequest()", js)
        self.assertIn("renderAll(data, payload)", js)
        # Preset keys match HTML
        for preset in ("nominal-fwd", "landing-deploy", "max-reverse",
                       "stow-return", "inhibit-block"):
            self.assertIn(f'"{preset}"', js,
                          f"demo.js missing preset logic for: {preset}")

    def test_demo_server_index_html_contains_all_six_surfaces(self):
        """index.html 2x3 grid must link to all 6 UI surfaces (or mark placeholders)."""
        html = (DEMO_UI_STATIC_DIR / "index.html").read_text(encoding="utf-8")
        for surface_href in (
            "/demo.html",
            "/c919_etras_workstation.html",
            "/fantui_circuit.html",
            "/c919_etras_panel/circuit.html",
            "http://127.0.0.1:9191/",
        ):
            self.assertIn(surface_href, html, f"index.html missing surface link: {surface_href}")
        # Unified nav must be present
        self.assertIn('class="unified-nav"', html)
        self.assertIn('/unified-nav.css', html)
        # Hero title
        self.assertIn("FANTUI LogicMVP", html)

    def test_demo_server_unified_nav_css_served(self):
        """/unified-nav.css must serve 200 for all pages that import it."""
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/unified-nav.css")
            response = connection.getresponse()
            body = response.read().decode("utf-8")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertEqual(response.status, 200)
        self.assertIn(".unified-nav", body)
        self.assertIn("--nav-height", body)

    def test_demo_server_serves_workbench_acceptance_shell(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/workbench.html")
            response = connection.getresponse()
            html = response.read().decode("utf-8")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertIn("<title>Well Harness Workbench Bundle 验收台</title>", html)
        self.assertIn("一键预设验收卡", html)
        self.assertIn("data-workbench-preset=\"ready_archived\"", html)
        self.assertIn("data-workbench-preset=\"blocked_follow_up\"", html)
        self.assertIn("一键通过验收", html)

    def test_demo_server_serves_browser_icon_and_manifest_assets(self):
        server, thread = start_demo_server()
        try:
            expectations = {
                "/favicon.ico": "image/svg+xml",
                "/apple-touch-icon.png": "image/svg+xml",
            }
            for path, expected_content_type in expectations.items():
                with self.subTest(path=path):
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    connection.request("GET", path)
                    response = connection.getresponse()
                    body = response.read()
                    connection.close()
                    self.assertEqual(response.status, 200)
                    self.assertIn(expected_content_type, response.getheader("Content-Type", ""))
                    self.assertTrue(body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_workbench_static_shell_contains_key_acceptance_sections(self):
        html = (DEMO_UI_STATIC_DIR / "workbench.html").read_text(encoding="utf-8")

        self.assertIn("连续点多个预设时，以最后一次点击结果为准。", html)
        self.assertIn("一眼看懂的验收面板", html)
        self.assertIn("第二套系统接入准备度", html)
        self.assertIn("id=\"workbench-onboarding-badge\"", html)
        self.assertIn("id=\"workbench-onboarding-docs\"", html)
        self.assertIn("id=\"workbench-onboarding-clarifications\"", html)
        self.assertIn("id=\"workbench-onboarding-unlocks\"", html)
        self.assertIn("第二套系统画像", html)
        self.assertIn("id=\"workbench-fingerprint-badge\"", html)
        self.assertIn("id=\"workbench-fingerprint-system-id\"", html)
        self.assertIn("id=\"workbench-fingerprint-doc-list\"", html)
        self.assertIn("id=\"workbench-fingerprint-signal-list\"", html)
        self.assertIn("第二套系统接入动作板", html)
        self.assertIn("id=\"workbench-actions-badge\"", html)
        self.assertIn("id=\"workbench-actions-follow-up-list\"", html)
        self.assertIn("id=\"workbench-actions-schema-list\"", html)
        self.assertIn("id=\"workbench-actions-unlock-list\"", html)
        self.assertIn("Schema 安全修复工作台", html)
        self.assertIn("id=\"workbench-schema-workspace-badge\"", html)
        self.assertIn("id=\"workbench-schema-workspace-list\"", html)
        self.assertIn("id=\"workbench-apply-schema-repairs\"", html)
        self.assertIn("Clarification 回填工作台", html)
        self.assertIn("id=\"workbench-clarification-workspace-badge\"", html)
        self.assertIn("id=\"workbench-clarification-workspace-list\"", html)
        self.assertIn("id=\"workbench-apply-clarifications\"", html)
        self.assertIn("id=\"workbench-apply-and-rerun\"", html)
        self.assertIn("id=\"workbench-history-view-status\"", html)
        self.assertIn("回到最新结果", html)
        self.assertIn("id=\"workbench-history-compare-bar\"", html)
        self.assertIn("历史回看与最新结果差异", html)
        self.assertIn("id=\"workbench-history-detail-board\"", html)
        self.assertIn("回看结果与最新结果并排对照", html)
        self.assertIn("id=\"workbench-history-detail-replay\"", html)
        self.assertIn("id=\"workbench-history-detail-latest\"", html)
        self.assertIn("最近验收结果", html)
        self.assertIn("id=\"workbench-history-cards\"", html)
        self.assertIn("点一张卡即可把那次结果重新放回主看板。", html)
        self.assertIn("id=\"workbench-visual-badge\"", html)
        self.assertIn("id=\"workbench-stage-clarification\"", html)
        self.assertIn("id=\"workbench-packet-source-status\"", html)
        self.assertIn("Packet 版本历史", html)
        self.assertIn("id=\"workbench-packet-history-status\"", html)
        self.assertIn("id=\"workbench-packet-history-return-latest\"", html)
        self.assertIn("id=\"workbench-packet-draft-status\"", html)
        self.assertIn("id=\"workbench-packet-draft-note\"", html)
        self.assertIn("id=\"workbench-save-packet-draft\"", html)
        self.assertIn("刷新页面后还会继续恢复当前 packet 工作区", html)
        self.assertIn("id=\"workbench-packet-history-compare-bar\"", html)
        self.assertIn("历史 Packet 与最新 Packet 差异", html)
        self.assertIn("id=\"workbench-packet-history-cards\"", html)
        self.assertIn("id=\"workbench-packet-json\"", html)
        self.assertIn("id=\"workbench-logic-change\"", html)
        self.assertIn("开发调试 / Raw JSON（一般不用看）", html)
        self.assertIn("id=\"run-workbench-bundle\"", html)
        self.assertIn("Optimization Record", html)
        self.assertIn("载入参考样例", html)
        self.assertIn("id=\"export-workbench-workspace\"", html)
        self.assertIn("id=\"workbench-workspace-file-input\"", html)
        self.assertIn("导入工作区快照", html)
        self.assertIn("id=\"workbench-archive-manifest-path\"", html)
        self.assertIn("id=\"restore-workbench-archive\"", html)
        self.assertIn("从 Archive 恢复工作区", html)
        self.assertIn("最近可恢复的 Archive", html)
        self.assertIn("id=\"workbench-recent-archives-list\"", html)
        self.assertIn("id=\"refresh-workbench-recent-archives\"", html)
        self.assertIn("恢复这个 Archive", html)
        self.assertIn("工作区交接摘要", html)
        self.assertIn("id=\"workbench-handoff-badge\"", html)
        self.assertIn("id=\"workbench-handoff-system\"", html)
        self.assertIn("id=\"workbench-handoff-workspace\"", html)
        self.assertIn("id=\"workbench-handoff-note\"", html)
        self.assertIn("id=\"copy-workbench-handoff-brief\"", html)
        self.assertIn("复制交接摘要", html)
        self.assertIn("导出的工作区快照也会带上它", html)

    def test_workbench_static_assets_include_history_replay_hooks(self):
        script = (DEMO_UI_STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
        stylesheet = (DEMO_UI_STATIC_DIR / "workbench.css").read_text(encoding="utf-8")

        self.assertIn("restoreWorkbenchHistoryEntry", script)
        self.assertIn("restoreLatestWorkbenchHistory", script)
        self.assertIn("当前查看：历史回看", script)
        self.assertIn("renderWorkbenchHistoryCompareBar", script)
        self.assertIn("renderWorkbenchHistoryDetailBoard", script)
        self.assertIn("detailedWorkbenchHistoryEntry", script)
        self.assertIn("renderWorkbenchPacketRevisionHistory", script)
        self.assertIn("restoreWorkbenchPacketRevisionEntry", script)
        self.assertIn("renderWorkbenchPacketRevisionCompareBar", script)
        self.assertIn("renderWorkbenchPacketDraftState", script)
        self.assertIn("saveCurrentWorkbenchPacketDraft", script)
        self.assertIn("自动保存草稿 /", script)
        self.assertIn("workbenchPacketWorkspaceStorageKey", script)
        self.assertIn("restoreWorkbenchPacketWorkspaceFromBrowser", script)
        self.assertIn("restoreWorkbenchPacketWorkspaceSnapshot", script)
        self.assertIn("persistWorkbenchPacketWorkspace", script)
        self.assertIn("normalizeWorkbenchRunHistory", script)
        self.assertIn("nextWorkbenchSequenceFromIds", script)
        self.assertIn("downloadWorkbenchWorkspaceSnapshot", script)
        self.assertIn("importWorkbenchWorkspaceSnapshot", script)
        self.assertIn("buildWorkbenchHandoffSnapshot", script)
        self.assertIn("renderWorkbenchHandoffBoard", script)
        self.assertIn("workbenchHandoffBriefText", script)
        self.assertIn("copyWorkbenchHandoffBrief", script)
        self.assertIn("当前工作区交接摘要已复制。", script)
        self.assertIn("workspace_handoff: buildWorkbenchHandoffSnapshot()", script)
        self.assertIn("workspace_snapshot: collectWorkbenchPacketWorkspaceState()", script)
        self.assertIn("workbenchArchiveRestorePath", script)
        self.assertIn("normalizeRecentWorkbenchArchiveEntries", script)
        self.assertIn("renderRecentWorkbenchArchives", script)
        self.assertIn("workbenchRecentArchivesPath", script)
        self.assertIn("refreshRecentWorkbenchArchives", script)
        self.assertIn("upsertRecentWorkbenchArchiveEntry", script)
        self.assertIn("buildRecentWorkbenchArchiveEntryFromBundlePayload", script)
        self.assertIn("buildRecentWorkbenchArchiveEntryFromRestorePayload", script)
        self.assertIn("archivePayloadFromRestoreResponse", script)
        self.assertIn("restoreWorkbenchArchiveFromManifest", script)
        self.assertIn("archive.manifest_json_path", script)
        self.assertIn("archive.workspace_handoff_json_path", script)
        self.assertIn("archive.workspace_snapshot_json_path", script)
        self.assertIn("当前工作区已经具备可交接的 packet、结果和 archive 状态", script)
        self.assertIn("当前工作区已经明确告诉你卡在哪", script)
        self.assertIn("当前只有 packet 和交接备注，还没有结果历史", script)
        self.assertIn("workspaceSnapshotDownloadName", script)
        self.assertIn("当前工作区快照已导出。", script)
        self.assertIn("已导入工作区快照和结果历史。", script)
        self.assertIn("已从 archive 恢复工作区和结果历史", script)
        self.assertIn("请先填写 archive_manifest.json 或 archive 目录路径。", script)
        self.assertIn("这些 archive 都来自默认 archive root；点卡片就会自动把它恢复回当前 workbench。", script)
        self.assertIn("最近 archive 列表已刷新。", script)
        self.assertIn("当前 Packet：历史版本", script)
        self.assertIn("点此恢复这个 Packet 版本", script)
        self.assertIn("它和最新 packet 在输入骨架上差在哪里", script)
        self.assertIn("当前草稿：有未保存改动", script)
        self.assertIn("当前草稿：JSON 待修正", script)
        self.assertIn("尚未建立版本基线", script)
        self.assertIn("已从浏览器恢复上次 packet 工作区", script)
        self.assertIn("已从浏览器恢复上次 packet 工作区和结果历史", script)
        self.assertIn("当前 Packet 草稿已保存到版本历史。", script)
        self.assertIn("renderOnboardingReadinessFromPayload", script)
        self.assertIn("renderSystemFingerprintFromPacketPayload", script)
        self.assertIn("renderSystemFingerprintFromPayload", script)
        self.assertIn("renderOnboardingActionsFromPayload", script)
        self.assertIn("renderSchemaRepairWorkspaceFromPayload", script)
        self.assertIn("runWorkbenchSchemaSafeRepair", script)
        self.assertIn("workbenchRepairPath", script)
        self.assertIn("安全 schema 修复已经写回当前 packet", script)
        self.assertIn("renderClarificationWorkspaceFromPayload", script)
        self.assertIn("applyClarificationWorkspace", script)
        self.assertIn("workbench-clarification-workspace", script)
        self.assertIn("workbench-apply-and-rerun", script)
        self.assertIn("只复用 bundle 真实返回的 follow_up_items", script)
        self.assertIn("\"workbench-handoff-note\"", script)
        self.assertIn("version: 2", script)
        self.assertIn("handoff: buildWorkbenchHandoffSnapshot()", script)
        self.assertIn("workbench-onboarding-badge", script)
        self.assertIn("可接第二套系统", script)
        self.assertIn("文档来源、控制目标和关键信号", script)
        self.assertIn("这套系统还没 ready，但动作板已经把先补什么、再补什么、补完解锁什么拆开了。", script)
        self.assertIn("你正在回看", script)
        self.assertIn("当前来源：最近验收结果回看。", script)
        self.assertIn("点此回看这次结果", script)
        self.assertIn(".workbench-history-action", stylesheet)
        self.assertIn(".workbench-history-view-bar", stylesheet)
        self.assertIn(".workbench-packet-draft-bar", stylesheet)
        self.assertIn(".workbench-packet-draft-note", stylesheet)
        self.assertIn(".workbench-archive-restore-row", stylesheet)
        self.assertIn(".workbench-recent-archives-board", stylesheet)
        self.assertIn(".workbench-recent-archives-header-actions", stylesheet)
        self.assertIn(".workbench-recent-archive-action", stylesheet)
        self.assertIn(".workbench-history-return-button", stylesheet)
        self.assertIn(".workbench-packet-history-board", stylesheet)
        self.assertIn(".workbench-history-compare-bar", stylesheet)
        self.assertIn(".workbench-history-compare-grid", stylesheet)
        self.assertIn(".workbench-history-detail-board", stylesheet)
        self.assertIn(".workbench-history-detail-grid", stylesheet)
        self.assertIn(".workbench-history-detail-value[data-diff=\"changed\"]", stylesheet)
        self.assertIn(".workbench-onboarding-board", stylesheet)
        self.assertIn(".workbench-onboarding-grid", stylesheet)
        self.assertIn(".workbench-onboarding-footer", stylesheet)
        self.assertIn(".workbench-fingerprint-board", stylesheet)
        self.assertIn(".workbench-fingerprint-meta", stylesheet)
        self.assertIn(".workbench-fingerprint-panel", stylesheet)
        self.assertIn(".workbench-fingerprint-chip", stylesheet)
        self.assertIn(".workbench-actions-board", stylesheet)
        self.assertIn(".workbench-actions-grid", stylesheet)
        self.assertIn(".workbench-actions-panel", stylesheet)
        self.assertIn(".workbench-actions-item", stylesheet)
        self.assertIn(".workbench-schema-workspace", stylesheet)
        self.assertIn(".workbench-schema-workspace-list", stylesheet)
        self.assertIn(".workbench-schema-card", stylesheet)
        self.assertIn(".workbench-schema-workspace-actions", stylesheet)
        self.assertIn(".workbench-clarification-workspace", stylesheet)
        self.assertIn(".workbench-clarification-workspace-list", stylesheet)
        self.assertIn(".workbench-clarification-card", stylesheet)
        self.assertIn(".workbench-clarification-workspace-actions", stylesheet)
        self.assertIn(".workbench-history-card[data-selected=\"true\"]", stylesheet)

    def test_workbench_static_assets_include_explain_runtime_board(self):
        html = (DEMO_UI_STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
        stylesheet = (DEMO_UI_STATIC_DIR / "workbench.css").read_text(encoding="utf-8")

        for fragment in (
            'id="workbench-explain-runtime-title"',
            'id="workbench-explain-runtime-badge"',
            'id="workbench-explain-runtime-summary"',
            'id="workbench-explain-runtime-backend"',
            'id="workbench-explain-runtime-source"',
            'id="workbench-explain-runtime-cache"',
            'id="workbench-explain-runtime-boundary"',
            "Explain 运行态",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            "function readExplainRuntimePayload(payload)",
            "function explainRuntimeBadgeText(runtime)",
            "function renderExplainRuntime(payload)",
            "verified_cache_hits",
            "expected_count",
            "boundary_note",
            "requested_backend",
            "renderExplainRuntime(payload);",
        ):
            self.assertIn(fragment, script)

        for fragment in (
            ".workbench-explain-runtime-board",
            ".workbench-explain-runtime-board .workbench-visual-badge[data-state=\"live\"]",
        ):
            self.assertIn(fragment, stylesheet)

    def test_demo_server_api_returns_workbench_bootstrap_payload(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/api/workbench/bootstrap")
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual("new_control_system_id", payload["template_packet"]["system_id"])
        self.assertEqual("custom_reverse_control_v1", payload["reference_packet"]["system_id"])
        self.assertIn("artifacts/workbench-bundles", payload["default_archive_root"])
        self.assertIn("recent_archives", payload)
        self.assertIsInstance(payload["recent_archives"], list)
        self.assertIn("explain_runtime", payload)
        self.assertIn("llm_backend", payload["explain_runtime"])
        self.assertIn("response_source", payload["explain_runtime"])

    def test_demo_server_bootstrap_lists_recent_workbench_archives(self):
        bundle = build_workbench_bundle(
            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_root = Path(temp_dir).resolve()
            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
                archive = archive_workbench_bundle(bundle, archive_root)

                payload = demo_server.workbench_bootstrap_payload()

        self.assertEqual(str(archive_root), payload["default_archive_root"])
        self.assertEqual(1, len(payload["recent_archives"]))
        recent_archive = payload["recent_archives"][0]
        self.assertEqual(str(Path(archive.archive_dir).resolve()), recent_archive["archive_dir"])
        self.assertEqual(str(Path(archive.manifest_json_path).resolve()), recent_archive["manifest_path"])
        self.assertEqual("custom_reverse_control_v1", recent_archive["system_id"])
        self.assertTrue(recent_archive["ready_for_spec_build"])

    def test_workbench_bootstrap_explain_runtime_returns_shelved_payload(self):
        # Phase A (2026-04-22): LLM features shelved. explain_runtime returns
        # a stable idle payload without consulting pitch_prewarm reports.
        payload = demo_server.workbench_bootstrap_payload()
        explain_runtime = payload["explain_runtime"]
        self.assertEqual("shelved", explain_runtime["status"])
        self.assertEqual("", explain_runtime["llm_backend"])
        self.assertEqual("", explain_runtime["llm_model"])
        self.assertEqual(0, explain_runtime["verified_cache_hits"])
        self.assertIn("LLM features shelved", explain_runtime["detail"])

    def test_workbench_js_renders_shelved_explain_runtime_with_distinct_copy(self):
        """workbench.js must short-circuit shelved status so the cache/source/backend
        cards don't misreport zero counters as observed prewarm telemetry.

        Phase A Codex review noted the payload was shelved but the renderer had no
        shelved branch — operators saw '待命 / 一旦在 chat / demo 舱发起 explain' copy
        pointing at removed flows. This regression test pins the corrective branches
        into the static asset.
        """
        script = (DEMO_UI_STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
        # Badge state + text branches
        self.assertIn('if (runtime.status === "shelved") return "shelved";', script,
                      "explainRuntimeBadgeState missing shelved branch")
        self.assertIn('if (runtime.status === "shelved") return "已搁置";', script,
                      "explainRuntimeBadgeText missing shelved branch")
        # renderExplainRuntime short-circuit
        self.assertIn('if (runtime.status === "shelved") {', script,
                      "renderExplainRuntime missing shelved short-circuit")
        # Distinct shelved copy (not the generic '待命/一旦在 chat / demo' fallback)
        self.assertIn("LLM 后端已从活跃代码库搁置", script,
                      "shelved branch must use distinct copy, not generic idle fallback")
        self.assertIn("explain 路由已移除", script,
                      "shelved branch must explain that explain routes are removed")
        self.assertIn("LLM 缓存链路已停用", script,
                      "shelved branch must explain cache pipeline is offline")

    def test_demo_server_recent_archives_api_lists_recent_workbench_archives(self):
        bundle = build_workbench_bundle(
            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_root = Path(temp_dir).resolve()
            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
                archive_workbench_bundle(bundle, archive_root)
                server, thread = start_demo_server()
                try:
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    connection.request("GET", "/api/workbench/recent-archives")
                    response = connection.getresponse()
                    payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(str(archive_root), payload["default_archive_root"])
        self.assertEqual(1, len(payload["recent_archives"]))
        self.assertEqual("custom_reverse_control_v1", payload["recent_archives"][0]["system_id"])

    def test_demo_server_api_returns_workbench_bundle_and_archive_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_root = Path(temp_dir).resolve()
            with mock.patch.object(demo_server, "default_workbench_archive_root", return_value=archive_root):
                server, thread = start_demo_server()
                try:
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                    request_body = json.dumps(
                        {
                            "packet_payload": demo_server.reference_workbench_packet_payload(),
                            "archive_bundle": True,
                            "workspace_handoff": {
                                "badgeText": "可交接",
                                "system": "custom_reverse_control_v1",
                                "packet": "2 docs / 4 logic / 1 faults",
                                "result": "通过 / ab_pressure_ramp",
                                "archive": "已留档",
                                "workspace": "3 个 packet 版本 / 2 个结果",
                                "note": "Ready archive for next engineer handoff.",
                            },
                            "workspace_snapshot": {
                                "kind": "well-harness-workbench-browser-workspace",
                                "version": 2,
                                "packetRevisionHistory": [{"id": "workbench-packet-revision-1", "title": "载入参考样例"}],
                                "runHistory": [{"id": "workbench-history-1", "title": "一键通过验收"}],
                                "handoff": {
                                    "badgeText": "可交接",
                                    "note": "Ready archive for next engineer handoff.",
                                },
                            },
                            "confirmed_root_cause": "Pressure sensor bias was confirmed during troubleshooting.",
                            "repair_action": "Recalibrated the sensor path.",
                            "validation_after_fix": "Acceptance replay completed after the repair.",
                            "residual_risk": "Watch for future sensor drift.",
                            "suggested_logic_change": "Add a pressure plausibility cross-check before enabling the deploy chain.",
                            "reliability_gain_hypothesis": "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
                            "guardrail_note": "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
                        }
                    ).encode("utf-8")
                    connection.request(
                        "POST",
                        "/api/workbench/bundle",
                        body=request_body,
                        headers={"Content-Type": "application/json"},
                    )
                    response = connection.getresponse()
                    payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)

                self.assertEqual(response.status, 200)
                self.assertEqual("full_workbench_bundle", payload["bundle"]["bundle_kind"])
                self.assertTrue(payload["bundle"]["ready_for_spec_build"])
                self.assertEqual("ab_pressure_ramp", payload["bundle"]["selected_scenario_id"])
                self.assertEqual("pressure_sensor_bias_low", payload["bundle"]["selected_fault_mode_id"])
                self.assertEqual(
                    "Add a pressure plausibility cross-check before enabling the deploy chain.",
                    payload["bundle"]["knowledge_artifact"]["optimization_record"]["suggested_logic_change"],
                )
                self.assertEqual(
                    "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
                    payload["bundle"]["knowledge_artifact"]["optimization_record"]["reliability_gain_hypothesis"],
                )
                self.assertEqual(
                    "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
                    payload["bundle"]["knowledge_artifact"]["optimization_record"][
                        "redundancy_reduction_or_guardrail_note"
                    ],
                )
                self.assertIsNotNone(payload["archive"])
                self.assertIn("explain_runtime", payload)
                self.assertIn("llm_backend", payload["explain_runtime"])
                self.assertTrue(Path(payload["archive"]["archive_dir"]).exists())
                self.assertTrue(Path(payload["archive"]["manifest_json_path"]).exists())
                self.assertTrue(Path(payload["archive"]["summary_markdown_path"]).exists())
                self.assertTrue(Path(payload["archive"]["workspace_handoff_json_path"]).exists())
                self.assertTrue(Path(payload["archive"]["workspace_snapshot_json_path"]).exists())
                manifest_payload = json.loads(Path(payload["archive"]["manifest_json_path"]).read_text(encoding="utf-8"))
                handoff_payload = json.loads(Path(payload["archive"]["workspace_handoff_json_path"]).read_text(encoding="utf-8"))
                snapshot_payload = json.loads(Path(payload["archive"]["workspace_snapshot_json_path"]).read_text(encoding="utf-8"))
                self.assertEqual("well-harness-workbench-archive-manifest", manifest_payload["kind"])
                self.assertEqual(".", manifest_payload["archive_dir"])
                self.assertEqual("workspace_snapshot.json", manifest_payload["files"]["workspace_snapshot_json"])
                self.assertEqual("可交接", handoff_payload["badgeText"])
                self.assertEqual(2, snapshot_payload["version"])
                self.assertIn(
                    "Ready archive for next engineer handoff.",
                    Path(payload["archive"]["summary_markdown_path"]).read_text(encoding="utf-8"),
                )
                self.assertEqual(str(archive_root), payload["default_archive_root"])

    def test_demo_server_api_can_restore_workbench_archive_payload(self):
        bundle = build_workbench_bundle(
            demo_server.intake_packet_from_dict(demo_server.reference_workbench_packet_payload()),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        handoff = {
            "badgeText": "可交接",
            "system": "custom_reverse_control_v1",
            "packet": "2 docs / 4 logic / 1 faults",
            "result": "通过 / ab_pressure_ramp",
            "archive": "已留档",
            "workspace": "3 个 packet 版本 / 2 个结果",
            "note": "Ready archive for next engineer handoff.",
        }
        workspace_snapshot = {
            "kind": "well-harness-workbench-browser-workspace",
            "version": 2,
            "packetRevisionHistory": [{"id": "workbench-packet-revision-1", "title": "载入参考样例"}],
            "runHistory": [{"id": "workbench-history-1", "title": "一键通过验收"}],
            "handoff": {
                "badgeText": "可交接",
                "note": "Ready archive for next engineer handoff.",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(
                bundle,
                temp_dir,
                workspace_handoff=handoff,
                workspace_snapshot=workspace_snapshot,
            )
            archive_dir = Path(archive.archive_dir)
            moved_archive_dir = Path(temp_dir) / "portable-archive"
            archive_dir.rename(moved_archive_dir)
            moved_manifest_path = moved_archive_dir / "archive_manifest.json"

            server, thread = start_demo_server()
            try:
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                request_body = json.dumps({"manifest_path": str(moved_archive_dir)}).encode("utf-8")
                connection.request(
                    "POST",
                    "/api/workbench/archive-restore",
                    body=request_body,
                    headers={"Content-Type": "application/json"},
                )
                response = connection.getresponse()
                payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertEqual(str(moved_manifest_path.resolve()), payload["manifest_path"])
        self.assertEqual(str(moved_archive_dir.resolve()), payload["archive_dir"])
        self.assertEqual("well-harness-workbench-archive-manifest", payload["manifest"]["kind"])
        self.assertEqual("full_workbench_bundle", payload["bundle"]["bundle_kind"])
        self.assertEqual(
            str((moved_archive_dir / "workspace_snapshot.json").resolve()),
            payload["resolved_files"]["workspace_snapshot_json"],
        )
        self.assertEqual("Ready archive for next engineer handoff.", payload["workspace_handoff"]["note"])
        self.assertEqual(2, payload["workspace_snapshot"]["version"])
        self.assertIn("artifacts/workbench-bundles", payload["default_archive_root"])

    def test_demo_server_api_can_apply_safe_schema_repairs_for_workbench_packet(self):
        server, thread = start_demo_server()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            request_body = json.dumps(
                {
                    "packet_payload": demo_server.workbench_bootstrap_payload()["template_packet"],
                    "apply_all_safe": True,
                }
            ).encode("utf-8")
            connection.request(
                "POST",
                "/api/workbench/repair",
                body=request_body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertIn("add_logic_node_stub", payload["applied_suggestion_ids"])
        self.assertIn("add_fault_mode_stub", payload["applied_suggestion_ids"])
        self.assertEqual(1, len(payload["packet_payload"]["logic_nodes"]))
        self.assertEqual(1, len(payload["packet_payload"]["fault_modes"]))
        self.assertEqual([], payload["intake_assessment"]["blocking_reasons"])
        self.assertEqual("blocked_by_clarifications", payload["clarification_brief"]["gate_status"])

    def test_demo_server_open_browser_helper_reports_failures(self):
        url = demo_server.demo_url("127.0.0.1", 8000)
        self.assertEqual(url, "http://127.0.0.1:8000/index.html")

        opener = mock.Mock(return_value=True)
        self.assertTrue(demo_server.open_browser(url, opener=opener))
        opener.assert_called_once_with(url)

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertFalse(demo_server.open_browser(url, opener=mock.Mock(return_value=False)))
        self.assertIn("Could not open browser automatically.", buffer.getvalue())
        self.assertIn("Open http://127.0.0.1:8000/index.html manually.", buffer.getvalue())

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertFalse(
                demo_server.open_browser(url, opener=mock.Mock(side_effect=RuntimeError("blocked")))
            )
        self.assertIn("Could not open browser automatically: blocked.", buffer.getvalue())
        self.assertIn("Open http://127.0.0.1:8000/index.html manually.", buffer.getvalue())

    def test_demo_server_help_documents_optional_open_affordance(self):
        result = subprocess.run(
            [sys.executable, "-m", "well_harness.demo_server", "--help"],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("--open", result.stdout)
        self.assertIn("standard-library", result.stdout)
        self.assertIn("webbrowser.open", result.stdout)
        self.assertIn("not browser E2E", result.stdout)
        self.assertIn("automation", result.stdout)

    def test_demo_server_main_open_affordance_uses_helper_and_continues_serving(self):
        created_servers = []

        class FakeServer:
            def __init__(self, address, handler_class):
                self.address = address
                self.handler_class = handler_class
                self.server_address = ("127.0.0.1", 8765)
                self.serve_forever_called = False
                self.server_close_called = False

            def serve_forever(self):
                self.serve_forever_called = True

            def server_close(self):
                self.server_close_called = True

        def fake_server(address, handler_class):
            server = FakeServer(address, handler_class)
            created_servers.append(server)
            return server

        with mock.patch.object(demo_server, "ThreadingHTTPServer", side_effect=fake_server):
            with mock.patch.object(demo_server, "open_browser", return_value=False) as open_browser:
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = demo_server.main(["--host", "127.0.0.1", "--port", "0", "--open"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(created_servers), 1)
        self.assertIs(created_servers[0].handler_class, DemoRequestHandler)
        self.assertTrue(created_servers[0].serve_forever_called)
        self.assertTrue(created_servers[0].server_close_called)
        open_browser.assert_called_once_with("http://127.0.0.1:8765/index.html")
        self.assertIn("Serving well-harness demo UI at http://127.0.0.1:8765/index.html", buffer.getvalue())

        with mock.patch.object(demo_server, "ThreadingHTTPServer", side_effect=fake_server):
            with mock.patch.object(demo_server, "open_browser") as open_browser:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(demo_server.main(["--host", "127.0.0.1", "--port", "0"]), 0)

        open_browser.assert_not_called()

    def test_demo_path_smoke_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_PATH_SMOKE_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        for fragment in (
            "OK demo_bridge_prompt",
            "OK lever_extreme_clamp",
            "OK lever_mode_switch_reset",
            "OK lever_l4_lock_gate",
            "OK preset_l3_waiting_vdt90",
            "OK preset_ra_blocker",
            "OK preset_n1k_blocker",
            "OK preset_vdt90_ready",
            "OK condition_toggle_sweep",
            "OK invalid_feedback_mode",
            "PASS: validated 10 demo smoke scenarios through the local HTTP demo surface.",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_path_smoke_script_json_output(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_PATH_SMOKE_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=demo_answer_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["scenario_count"], 10)
        self.assertEqual(payload["completed_scenarios"], 10)
        self.assertIsNone(payload["failed_scenario"])
        self.assertEqual(
            [
                "demo_bridge_prompt",
                "lever_extreme_clamp",
                "lever_mode_switch_reset",
                "lever_l4_lock_gate",
                "preset_l3_waiting_vdt90",
                "preset_ra_blocker",
                "preset_n1k_blocker",
                "preset_vdt90_ready",
                "condition_toggle_sweep",
                "invalid_feedback_mode",
            ],
            [scenario["name"] for scenario in payload["scenarios"]],
        )
        self.assertEqual(
            ["pass", "pass", "pass", "pass", "pass", "pass", "pass", "pass", "pass", "pass"],
            [scenario["status"] for scenario in payload["scenarios"]],
        )
        self.assertEqual(400, payload["scenarios"][-1]["http_status"])

    def test_demo_ui_handcheck_script_outputs_manual_checklist(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("manual browser hand-check helper", result.stdout)
        self.assertIn("not browser E2E automation", result.stdout)
        self.assertIn("does not start the server or drive a browser", result.stdout)
        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
        self.assertIn("standard-library webbrowser module", result.stdout)
        self.assertIn("not browser E2E automation", result.stdout)
        self.assertIn("http://127.0.0.1:8000/", result.stdout)

        for prompt in (
            "logic4 和 throttle lock 有什么关系",
            "为什么 throttle lock 没释放",
            "触发 logic3 会发生什么",
            "把 logic3 的 TRA 阈值改成 -8 会发生什么",
        ):
            self.assertIn(prompt, result.stdout)

        for observation in (
            "expected observations:",
            "intent: logic4_thr_lock_bridge",
            "logic4 / THR_LOCK bridge association",
            "matched_node=logic4->thr_lock",
            "intent: diagnose_problem",
            "possible_causes / evidence / risks",
            "intent: trigger_node",
            "logic3 plus EEC / PLS / PDU command subnodes",
            "matched_node=logic3 and target_logic=logic3",
            "intent: propose_logic_change",
            "dry-run / proposal, required_changes / risks",
            "does not directly modify controller.py",
            "not a new answer payload or control truth",
        ):
            self.assertIn(observation, result.stdout)

        for checkpoint in (
            "selected prompt state",
            "loading / ready state",
            "control chain highlight",
            "highlight explanation",
            "Answer sections summary",
            "summary chip click / focus",
            "summary chip arrow-key navigation",
            "raw JSON debug collapse / expand",
            "empty prompt error",
        ):
            self.assertIn(checkpoint, result.stdout)

        for boundary in (
            "deterministic controlled demo layer",
            "built-in nominal-deploy / retract-reset scenarios",
            "simplified first-cut plant",
            "not a full natural-language AI system",
            "not a complete physical model",
        ):
            self.assertIn(boundary, result.stdout)

    def test_demo_ui_handcheck_script_help_documents_manual_scope(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("manual browser hand-check checklist", result.stdout)
        self.assertIn("not browser E2E automation", result.stdout)
        self.assertIn("--open", result.stdout)
        self.assertIn("--walkthrough", result.stdout)
        self.assertIn("does not start the server", result.stdout)

    def test_demo_ui_handcheck_script_outputs_presenter_walkthrough(self):
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("Well Harness UI Demo Presenter Walkthrough", result.stdout)
        self.assertIn("manual presenter walkthrough", result.stdout)
        self.assertIn("not browser E2E automation", result.stdout)
        self.assertIn("not a new answer payload or control truth", result.stdout)
        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server", result.stdout)
        self.assertIn("PYTHONPATH=src python3 -m well_harness.demo_server --open", result.stdout)
        self.assertIn("standard-library browser launcher", result.stdout)
        self.assertIn("http://127.0.0.1:8000/", result.stdout)

        for prompt in (
            "logic4 和 throttle lock 有什么关系",
            "为什么 throttle lock 没释放",
            "触发 logic3 会发生什么",
            "把 logic3 的 TRA 阈值改成 -8 会发生什么",
        ):
            self.assertIn(prompt, result.stdout)

        for callout in (
            "[Input]",
            "[Chain]",
            "[Structured answer]",
            "[Raw JSON]",
            "[Safety]",
            "[Boundary]",
            "logic4 / THR_LOCK bridge highlight",
            "highlight explanation",
            "possible_causes / evidence / risks",
            "logic3 plus EEC / PLS / PDU command subnode highlights",
            "dry-run proposal, required_changes / risks",
            "does not directly modify controller.py",
            "deterministic controlled demo layer",
            "built-in nominal-deploy / retract-reset scenarios",
            "simplified first-cut plant",
            "not a full LLM",
            "not a complete physical model",
            "No screenshots or browser automation are generated",
            "docs/demo_presenter_talk_track.md",
            "Presenter readiness run card",
            "Follow the page callout labels",
            "[Highlight]",
        ):
            self.assertIn(callout, result.stdout)

    def test_demo_presenter_talk_track_covers_core_flow(self):
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")

        self.assertIn("Well Harness UI Demo Presenter Talk Track", talk_track)
        self.assertIn("manual demo guidance", talk_track)
        self.assertIn("not browser E2E automation", talk_track)
        self.assertIn("not a new answer payload or control truth", talk_track)
        self.assertIn("deterministic controlled demo layer", talk_track)
        self.assertIn("not an open-ended LLM", talk_track)
        self.assertIn("not a complete physical model", talk_track)
        self.assertIn("built-in `nominal-deploy` / `retract-reset`", talk_track)
        self.assertIn("simplified first-cut plant", talk_track)

        for prompt in (
            "logic4 和 throttle lock 有什么关系",
            "为什么 throttle lock 没释放",
            "触发 logic3 会发生什么",
            "把 logic3 的 TRA 阈值改成 -8 会发生什么",
        ):
            self.assertIn(prompt, talk_track)

        for callout in (
            "[Say]",
            "[Point]",
            "[Boundary]",
            "control chain",
            "highlight explanation",
            "structured answer",
            "raw JSON",
            "Follow the page callout labels",
            "[Input]",
            "[Chain]",
            "[Highlight]",
            "[Structured answer]",
            "[Raw JSON]",
            "logic4 / THR_LOCK",
            "possible_causes",
            "evidence",
            "risks",
            "EEC / PLS / PDU",
            "dry-run proposal",
            "required_changes",
            "does not directly modify `controller.py`",
            "loading, empty prompt, API error, or network error",
            "not a control-logic conclusion",
        ):
            self.assertIn(callout, talk_track)

    def test_demo_presenter_talk_track_includes_readiness_run_card(self):
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")

        for fragment in (
            "Presenter Readiness Run Card",
            "manual pre-demo check",
            "not browser E2E automation",
            "not an automatic readiness detector",
            "not a new answer payload or control truth",
            "PYTHONPATH=src python3 -m well_harness.demo_server",
            "PYTHONPATH=src python3 -m well_harness.demo_server --open",
            "standard-library browser launcher",
            "http://127.0.0.1:8000/",
            "logic4 和 throttle lock 有什么关系",
            "[Input]",
            "[Chain]",
            "[Highlight]",
            "[Structured answer]",
            "[Raw JSON]",
            "control chain highlights `logic4 / THR_LOCK`",
            "highlight explanation names the answer association",
            "`Answer sections` summary shows counts",
            "raw JSON debug panel",
            "loading, empty prompt, API error, or network error",
            "not a control-logic conclusion",
            "deterministic controlled demo layer",
            "built-in `nominal-deploy` / `retract-reset` scenarios",
            "simplified first-cut plant",
            "not a full LLM",
            "not a complete physical model",
        ):
            self.assertIn(fragment, talk_track)

    def test_node_catalog_covers_expected_chain_nodes(self):
        node_ids = {node.node_id for node in NODE_CATALOG}

        self.assertEqual(
            {
                "sw1",
                "logic1",
                "tls115",
                "tls_unlocked",
                "sw2",
                "logic2",
                "etrac_540v",
                "logic3",
                "eec_deploy",
                "pls_power",
                "pdu_motor",
                "vdt90",
                "logic4",
                "thr_lock",
            },
            node_ids,
        )
        catalog = {node.node_id: node for node in NODE_CATALOG}
        self.assertTrue(catalog["tls_unlocked"].blocker_hints)
        self.assertTrue(catalog["pdu_motor"].blocker_hints)
        self.assertTrue(catalog["vdt90"].blocker_hints)
        self.assertTrue(catalog["thr_lock"].blocker_hints)

    def test_trigger_logic3_answer_uses_nominal_chain_evidence(self):
        answer = answer_demo_prompt("触发 logic3 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "logic3")
        self.assertEqual(answer.target_logic, "logic3")
        self.assertIn("1.9s", evidence)
        self.assertIn("tra_deg -7.0->-14.0 <= -11.74", evidence)
        self.assertIn("controller_outputs.eec_deploy_cmd False->True", evidence)
        self.assertIn("SW1 -> logic1/TLS115", evidence)
        self.assertIn("deploy_90_percent_vdt", outcome)

    def test_trigger_logic4_answer_uses_vdt_and_throttle_lock_evidence(self):
        answer = answer_demo_prompt("触发 logic4 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "logic4")
        self.assertEqual(answer.target_logic, "logic4")
        self.assertIn("5.0s", evidence)
        self.assertIn("deploy_90_percent_vdt False->True", evidence)
        self.assertIn("controller_outputs.throttle_lock_release_cmd False->True", evidence)
        self.assertIn("THR_LOCK", outcome)

    def test_trigger_sw1_answer_uses_catalog_event_evidence(self):
        answer = answer_demo_prompt("触发 SW1 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "sw1")
        self.assertIsNone(answer.target_logic)
        self.assertIn("category=switch", evidence)
        self.assertIn("0.5s", evidence)
        self.assertIn("sw1 False->True", evidence)
        self.assertIn("logic1_active False->True", evidence)
        self.assertIn("TLS115", outcome)

    def test_trigger_tls_unlocked_answer_uses_catalog_event_evidence(self):
        answer = answer_demo_prompt("触发 TLS unlocked 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "tls_unlocked")
        self.assertIsNone(answer.target_logic)
        self.assertIn("category=sensor", evidence)
        self.assertIn("0.8s", evidence)
        self.assertIn("tls_unlocked_ls False->True", evidence)
        self.assertIn("logic3", outcome)

    def test_trigger_vdt90_answer_uses_catalog_event_evidence(self):
        answer = answer_demo_prompt("触发 VDT90 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "vdt90")
        self.assertIsNone(answer.target_logic)
        self.assertIn("category=plant_feedback", evidence)
        self.assertIn("5.0s", evidence)
        self.assertIn("deploy_90_percent_vdt False->True", evidence)
        self.assertIn("logic4_active False->True", evidence)
        self.assertIn("logic4", outcome)

    def test_trigger_thr_lock_answer_uses_catalog_event_evidence(self):
        answer = answer_demo_prompt("触发 THR_LOCK 会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)

        self.assertEqual(answer.intent, "trigger_node")
        self.assertEqual(answer.matched_node, "thr_lock")
        self.assertIsNone(answer.target_logic)
        self.assertIn("category=command", evidence)
        self.assertIn("5.0s", evidence)
        self.assertIn("throttle_lock_release_cmd False->True", evidence)
        self.assertIn("logic4_active False->True", evidence)
        self.assertIn("THR_LOCK", outcome)

    def test_non_logic_trigger_answers_include_specific_upstream_blocker_hints(self):
        cases = (
            (
                "触发 TLS unlocked 会发生什么",
                "tls_unlocked",
                ("TLS115", "logic1", "events()", "DeployController.explain(logic1)"),
            ),
            (
                "触发 PDU motor 会发生什么",
                "pdu_motor",
                ("logic3", "logic_transition_diagnostics(logic3)", "DeployController.explain(logic3)"),
            ),
            (
                "触发 VDT90 会发生什么",
                "vdt90",
                ("PDU motor", "deploy_position_percent", "events()"),
            ),
            (
                "触发 THR_LOCK 会发生什么",
                "thr_lock",
                ("logic4", "deploy_90_percent_vdt", "DeployController.explain(logic4)"),
            ),
        )

        for prompt, matched_node, expected_terms in cases:
            with self.subTest(prompt=prompt):
                answer = answer_demo_prompt(prompt)
                possible_causes = "\n".join(answer.possible_causes)

                self.assertEqual(answer.intent, "trigger_node")
                self.assertEqual(answer.matched_node, matched_node)
                for term in expected_terms:
                    self.assertIn(term, possible_causes)

    def test_non_logic_trigger_answers_include_upstream_status_table(self):
        cases = (
            (
                "触发 TLS unlocked 会发生什么",
                "tls_unlocked",
                (
                    "upstream_status: name=logic1 source=logic_diagnosis observed=True time=0.5s",
                    "upstream_status: name=tls_115vac_cmd source=event observed=True time=0.5s",
                    "upstream_status: name=plant_state.tls_powered_s source=trace_field observed=True time=0.8s value=0.3",
                    "upstream_status: name=tls_unlocked_ls source=event observed=True time=0.8s",
                ),
            ),
            (
                "触发 PDU motor 会发生什么",
                "pdu_motor",
                (
                    "upstream_status: name=logic3_active source=logic_diagnosis observed=True time=1.9s",
                    "upstream_status: name=pdu_motor_cmd source=event observed=True time=1.9s",
                ),
            ),
            (
                "触发 VDT90 会发生什么",
                "vdt90",
                (
                    "upstream_status: name=pdu_motor_cmd source=event observed=True time=1.9s",
                    "upstream_status: name=deploy_position_percent source=trace_field observed=True time=5.0s value=90",
                    "upstream_status: name=deploy_90_percent_vdt source=event observed=True time=5.0s",
                ),
            ),
            (
                "触发 THR_LOCK 会发生什么",
                "thr_lock",
                (
                    "upstream_status: name=logic4_active source=logic_diagnosis observed=True time=5.0s",
                    "upstream_status: name=deploy_90_percent_vdt source=event observed=True time=5.0s",
                    "upstream_status: name=throttle_lock_release_cmd source=event observed=True time=5.0s",
                ),
            ),
        )

        for prompt, matched_node, expected_rows in cases:
            with self.subTest(prompt=prompt):
                answer = answer_demo_prompt(prompt)
                evidence = "\n".join(answer.evidence)

                self.assertEqual(answer.intent, "trigger_node")
                self.assertEqual(answer.matched_node, matched_node)
                self.assertIn("upstream_status_table:", evidence)
                for expected_row in expected_rows:
                    self.assertIn(expected_row, evidence)

    def test_remaining_command_and_switch_triggers_include_upstream_status_table(self):
        cases = (
            (
                "触发 SW1 会发生什么",
                "sw1",
                (
                    "upstream_status: name=tra_deg source=trace_field observed=True time=0.5s value=-2",
                    "upstream_status: name=sw1 source=event observed=True time=0.5s",
                    "upstream_status: name=logic1_active source=logic_diagnosis observed=True time=0.5s",
                ),
            ),
            (
                "触发 SW2 会发生什么",
                "sw2",
                (
                    "upstream_status: name=tra_deg source=trace_field observed=True time=1.2s value=-7",
                    "upstream_status: name=sw2 source=event observed=True time=1.2s",
                    "upstream_status: name=logic2_active source=logic_diagnosis observed=True time=1.2s",
                ),
            ),
            (
                "触发 TLS115 会发生什么",
                "tls115",
                (
                    "upstream_status: name=logic1_active source=logic_diagnosis observed=True time=0.5s",
                    "upstream_status: name=tls_115vac_cmd source=event observed=True time=0.5s",
                ),
            ),
            (
                "触发 540V 会发生什么",
                "etrac_540v",
                (
                    "upstream_status: name=logic2_active source=logic_diagnosis observed=True time=1.2s",
                    "upstream_status: name=etrac_540vdc_cmd source=event observed=True time=1.2s",
                ),
            ),
            (
                "触发 EEC deploy 会发生什么",
                "eec_deploy",
                (
                    "upstream_status: name=logic3_active source=logic_diagnosis observed=True time=1.9s",
                    "upstream_status: name=eec_deploy_cmd source=event observed=True time=1.9s",
                ),
            ),
            (
                "触发 PLS power 会发生什么",
                "pls_power",
                (
                    "upstream_status: name=logic3_active source=logic_diagnosis observed=True time=1.9s",
                    "upstream_status: name=pls_power_cmd source=event observed=True time=1.9s",
                ),
            ),
        )

        for prompt, matched_node, expected_rows in cases:
            with self.subTest(prompt=prompt):
                answer = answer_demo_prompt(prompt)
                evidence = "\n".join(answer.evidence)

                self.assertEqual(answer.intent, "trigger_node")
                self.assertEqual(answer.matched_node, matched_node)
                self.assertIn("upstream_status_table:", evidence)
                for expected_row in expected_rows:
                    self.assertIn(expected_row, evidence)

    def test_blocked_state_sw1_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 SW1 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "sw1")
        self.assertEqual(answer.target_logic, "logic1")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=0.4s", evidence)
        self.assertIn("eventual_trigger=0.5s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=tra_deg source=trace_field observed=False checkpoint=0.4s value=0 required=SW1_window",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=sw1 source=trace_field observed=False checkpoint=0.4s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=logic1_active source=trace_field observed=False checkpoint=0.4s value=False required=True",
            evidence,
        )
        self.assertIn("logic1 explain@0.4s failed_conditions: radio_altitude_ft, sw1。", evidence)
        self.assertIn("events@0.5s: sw1 False->True; logic1_active False->True; tls_115vac_cmd False->True", evidence)
        self.assertIn("0.5s", outcome)
        self.assertIn("SW1", possible_causes)
        self.assertIn("switch window", possible_causes)

    def test_blocked_state_sw2_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 SW2 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "sw2")
        self.assertEqual(answer.target_logic, "logic2")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=1.1s", evidence)
        self.assertIn("eventual_trigger=1.2s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=tra_deg source=trace_field observed=False checkpoint=1.1s value=-2 required=SW2_window",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=sw2 source=trace_field observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=logic2_active source=trace_field observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn("logic2 explain@1.1s failed_conditions: sw2。", evidence)
        self.assertIn("events@1.2s: sw2 False->True; logic2_active False->True; etrac_540vdc_cmd False->True", evidence)
        self.assertIn("1.2s", outcome)
        self.assertIn("SW2", possible_causes)
        self.assertIn("switch window", possible_causes)

    def test_blocked_state_tls115_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 TLS115 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "tls115")
        self.assertEqual(answer.target_logic, "logic1")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=0.4s", evidence)
        self.assertIn("eventual_trigger=0.5s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=logic1 source=trace_field observed=False checkpoint=0.4s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=tls_115vac_cmd source=trace_field observed=False checkpoint=0.4s value=False required=True",
            evidence,
        )
        self.assertIn("logic1 explain@0.4s failed_conditions: radio_altitude_ft, sw1。", evidence)
        self.assertIn("events@0.5s: sw1 False->True; logic1_active False->True; tls_115vac_cmd False->True", evidence)
        self.assertIn("0.5s", outcome)
        self.assertIn("logic1", possible_causes)
        self.assertIn("DeployController.explain(logic1)", possible_causes)

    def test_blocked_state_logic1_uses_explain_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 logic1 还没满足")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "logic1")
        self.assertEqual(answer.target_logic, "logic1")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=0.4s", evidence)
        self.assertIn("eventual_trigger=0.5s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=radio_altitude_ft source=explain_condition observed=False checkpoint=0.4s value=10 required=< 6",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=sw1 source=explain_condition observed=False checkpoint=0.4s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=reverser_inhibited source=explain_condition observed=True checkpoint=0.4s value=False required=False",
            evidence,
        )
        self.assertIn("logic1 explain@0.4s failed_conditions: radio_altitude_ft, sw1。", evidence)
        self.assertIn("events@0.5s: sw1 False->True; logic1_active False->True; tls_115vac_cmd False->True", evidence)
        self.assertIn("0.5s", outcome)
        self.assertIn("radio_altitude_ft", possible_causes)
        self.assertIn("DeployController.explain(logic1)", possible_causes)

    def test_blocked_state_logic2_uses_explain_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 logic2 还没满足")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "logic2")
        self.assertEqual(answer.target_logic, "logic2")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=1.1s", evidence)
        self.assertIn("eventual_trigger=1.2s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=engine_running source=explain_condition observed=True checkpoint=1.1s value=True required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=sw2 source=explain_condition observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=eec_enable source=explain_condition observed=True checkpoint=1.1s value=True required=True",
            evidence,
        )
        self.assertIn("logic2 explain@1.1s failed_conditions: sw2。", evidence)
        self.assertIn("events@1.2s: sw2 False->True; logic2_active False->True; etrac_540vdc_cmd False->True", evidence)
        self.assertIn("1.2s", outcome)
        self.assertIn("sw2", possible_causes)
        self.assertIn("DeployController.explain(logic2)", possible_causes)

    def test_blocked_state_logic3_uses_explain_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 logic3 还没满足")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "logic3")
        self.assertEqual(answer.target_logic, "logic3")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=1.8s", evidence)
        self.assertIn("eventual_trigger=1.9s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=tls_unlocked_ls source=explain_condition observed=True checkpoint=1.8s value=True required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=n1k source=explain_condition observed=True checkpoint=1.8s value=35 required=< 60",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=tra_deg source=explain_condition observed=False checkpoint=1.8s value=-7 required=<= -11.74",
            evidence,
        )
        self.assertIn("logic3 explain@1.8s failed_conditions: tra_deg。", evidence)
        self.assertIn(
            "events@1.9s: logic3_active False->True; eec_deploy_cmd False->True; pls_power_cmd False->True; pdu_motor_cmd False->True",
            evidence,
        )
        self.assertIn("1.9s", outcome)
        self.assertIn("tra_deg", possible_causes)
        self.assertIn("DeployController.explain(logic3)", possible_causes)

    def test_blocked_state_logic4_uses_explain_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 logic4 还没满足")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "logic4")
        self.assertEqual(answer.target_logic, "logic4")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=4.9s", evidence)
        self.assertIn("eventual_trigger=5.0s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=deploy_90_percent_vdt source=explain_condition observed=False checkpoint=4.9s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=tra_deg source=explain_condition observed=True checkpoint=4.9s value=-14 required=between_exclusive -32..0",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=engine_running source=explain_condition observed=True checkpoint=4.9s value=True required=True",
            evidence,
        )
        self.assertIn("logic4 explain@4.9s failed_conditions: deploy_90_percent_vdt。", evidence)
        self.assertIn(
            "events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True",
            evidence,
        )
        self.assertIn("5.0s", outcome)
        self.assertIn("deploy_90_percent_vdt", possible_causes)
        self.assertIn("DeployController.explain(logic4)", possible_causes)

    def test_logic4_throttle_lock_bridge_summary_links_gate_and_release(self):
        answer = answer_demo_prompt("logic4 和 throttle lock 有什么关系")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)
        required_changes = "\n".join(answer.required_changes)
        risks = "\n".join(answer.risks)

        self.assertEqual(answer.intent, "logic4_thr_lock_bridge")
        self.assertEqual(answer.matched_node, "logic4->thr_lock")
        self.assertEqual(answer.target_logic, "logic4")
        self.assertIn("bridge=logic4->THR_LOCK; checkpoint=4.9s; eventual_trigger=5.0s", evidence)
        self.assertIn("受控 evidence bridge", evidence)
        self.assertIn("logic4 是上游 logic gate", evidence)
        self.assertIn("throttle_lock_release_cmd / THR_LOCK 是下游末端释放命令", evidence)
        self.assertIn(
            "blocked-state 解释 checkpoint gate 为什么未满足：logic4 explain@4.9s failed_conditions: deploy_90_percent_vdt。",
            evidence,
        )
        self.assertIn(
            "diagnose_problem 解释下游 release 为什么在该窗口尚未发生",
            evidence,
        )
        self.assertIn(
            "events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True",
            evidence,
        )
        self.assertIn("4.9s checkpoint", outcome)
        self.assertIn("5.0s 时 deploy_90_percent_vdt 翻转", outcome)
        self.assertIn("DeployController.explain(logic4)", possible_causes)
        self.assertIn("throttle lock 没释放", possible_causes)
        self.assertIn("不修改 controller.py", required_changes)
        self.assertIn("不是完整异常诊断", risks)

    def test_logic4_throttle_lock_bridge_summary_matches_joint_problem_prompt(self):
        answer = answer_demo_prompt("为什么 logic4 还没满足，throttle lock 也没释放")

        self.assertEqual(answer.intent, "logic4_thr_lock_bridge")
        self.assertEqual(answer.matched_node, "logic4->thr_lock")
        self.assertEqual(answer.target_logic, "logic4")

    def test_blocked_state_tls_unlocked_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 TLS unlocked 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "tls_unlocked")
        self.assertEqual(answer.target_logic, "logic1")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=0.7s", evidence)
        self.assertIn("eventual_trigger=0.8s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=logic1 source=trace_field observed=True checkpoint=0.7s value=True required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=tls_115vac_cmd source=trace_field observed=True checkpoint=0.7s value=True required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=plant_state.tls_powered_s source=trace_field observed=False checkpoint=0.7s value=0.2 required=>=0.3",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=tls_unlocked_ls source=trace_field observed=False checkpoint=0.7s value=False required=True",
            evidence,
        )
        self.assertIn("events@0.8s: tls_unlocked_ls False->True", evidence)
        self.assertIn("0.8s", outcome)
        self.assertIn("tls_115vac_cmd", possible_causes)
        self.assertIn("plant_state.tls_powered_s", possible_causes)

    def test_blocked_state_540v_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 540V 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "etrac_540v")
        self.assertEqual(answer.target_logic, "logic2")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=1.1s", evidence)
        self.assertIn("eventual_trigger=1.2s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=sw2 source=trace_field observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=logic2_active source=trace_field observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=etrac_540vdc_cmd source=trace_field observed=False checkpoint=1.1s value=False required=True",
            evidence,
        )
        self.assertIn("logic2 explain@1.1s failed_conditions: sw2。", evidence)
        self.assertIn("events@1.2s: sw2 False->True; logic2_active False->True; etrac_540vdc_cmd False->True", evidence)
        self.assertIn("1.2s", outcome)
        self.assertIn("sw2", possible_causes)
        self.assertIn("DeployController.explain(logic2)", possible_causes)

    def test_blocked_state_vdt90_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 VDT90 还没触发")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "vdt90")
        self.assertIsNone(answer.target_logic)
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=4.9s", evidence)
        self.assertIn("eventual_trigger=5.0s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=pdu_motor_cmd source=trace_field observed=True checkpoint=4.9s value=True required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=deploy_position_percent source=trace_field observed=False checkpoint=4.9s value=87 required=>=90",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=deploy_90_percent_vdt source=trace_field observed=False checkpoint=4.9s value=False required=True",
            evidence,
        )
        self.assertIn("events@5.0s: deploy_90_percent_vdt False->True", evidence)
        self.assertIn("5.0s", outcome)
        self.assertIn("deploy_position_percent", possible_causes)

    def test_blocked_state_thr_lock_uses_pre_trigger_checkpoint_comparison(self):
        answer = answer_demo_prompt("为什么 THR_LOCK 还没释放")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "blocked_state")
        self.assertEqual(answer.matched_node, "thr_lock")
        self.assertEqual(answer.target_logic, "logic4")
        self.assertIn("pre-trigger checkpoint comparison", evidence)
        self.assertIn("checkpoint=4.9s", evidence)
        self.assertIn("eventual_trigger=5.0s", evidence)
        self.assertIn("blocked_state_table:", evidence)
        self.assertIn(
            "blocked_status: name=deploy_90_percent_vdt source=trace_field observed=False checkpoint=4.9s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=logic4_active source=trace_field observed=False checkpoint=4.9s value=False required=True",
            evidence,
        )
        self.assertIn(
            "blocked_status: name=throttle_lock_release_cmd source=trace_field observed=False checkpoint=4.9s value=False required=True",
            evidence,
        )
        self.assertIn("logic4 explain@4.9s failed_conditions: deploy_90_percent_vdt。", evidence)
        self.assertIn("events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True", evidence)
        self.assertIn("5.0s", outcome)
        self.assertIn("deploy_90_percent_vdt", possible_causes)

    def test_throttle_lock_diagnosis_maps_to_logic4_blockers(self):
        answer = answer_demo_prompt("为什么 throttle lock 没释放")
        evidence = "\n".join(answer.evidence)
        possible_causes = "\n".join(answer.possible_causes)

        self.assertEqual(answer.intent, "diagnose_problem")
        self.assertEqual(answer.matched_node, "throttle_lock_release_cmd")
        self.assertEqual(answer.target_logic, "logic4")
        self.assertIn("logic4", evidence)
        self.assertIn("deploy_90_percent_vdt", evidence)
        self.assertIn("5.0s", evidence)
        self.assertIn("TRA", possible_causes)
        self.assertIn("engine_running", possible_causes)

    def test_blocked_state_does_not_break_existing_throttle_lock_diagnosis_prompt(self):
        answer = answer_demo_prompt("为什么 throttle lock 没释放")

        self.assertEqual(answer.intent, "diagnose_problem")
        self.assertEqual(answer.matched_node, "throttle_lock_release_cmd")
        self.assertEqual(answer.target_logic, "logic4")

    def test_logic3_threshold_change_is_dry_run_only(self):
        answer = answer_demo_prompt("如果把 logic3 的 TRA 阈值从 -11.74 改成 -8，会发生什么")
        evidence = "\n".join(answer.evidence)
        outcome = "\n".join(answer.outcome)
        required_changes = "\n".join(answer.required_changes)
        risks = "\n".join(answer.risks)

        self.assertEqual(answer.intent, "propose_logic_change")
        self.assertEqual(answer.matched_node, "logic3.tra_deg")
        self.assertEqual(answer.target_logic, "logic3")
        self.assertIn("阈值 -8", evidence)
        self.assertIn("1.9s", evidence)
        self.assertIn("不会改变首次满足 logic3 的 trace row", outcome)
        self.assertIn("没有修改 controller.py", required_changes)
        self.assertIn("logic4 / THR_LOCK 仍取决于 deploy_90_percent_vdt", risks)
        self.assertEqual(HarnessConfig().logic3_tra_deg_threshold, -11.74)

    def test_demo_cli_json_bridge_summary_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["demo", "--format", "json", "logic4 和 throttle lock 有什么关系"])

        payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            sorted(payload),
            [
                "evidence",
                "intent",
                "matched_node",
                "outcome",
                "possible_causes",
                "required_changes",
                "risks",
                "target_logic",
            ],
        )
        self.assertEqual(payload["intent"], "logic4_thr_lock_bridge")
        self.assertEqual(payload["matched_node"], "logic4->thr_lock")
        self.assertEqual(payload["target_logic"], "logic4")
        self.assertIsInstance(payload["evidence"], list)
        self.assertIsInstance(payload["outcome"], list)
        self.assertIsInstance(payload["possible_causes"], list)
        self.assertIsInstance(payload["required_changes"], list)
        self.assertIsInstance(payload["risks"], list)
        self.assertIn(
            "blocked-state 解释 checkpoint gate 为什么未满足：logic4 explain@4.9s failed_conditions: deploy_90_percent_vdt。",
            "\n".join(payload["evidence"]),
        )
        self.assertIn(
            "events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True",
            "\n".join(payload["evidence"]),
        )

    def test_demo_cli_json_logic4_blocked_state_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["demo", "--format", "json", "为什么 logic4 还没满足"])

        payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["intent"], "blocked_state")
        self.assertEqual(payload["matched_node"], "logic4")
        self.assertEqual(payload["target_logic"], "logic4")
        self.assertIsInstance(payload["evidence"], list)
        self.assertIn(
            "blocked_status: name=deploy_90_percent_vdt source=explain_condition observed=False checkpoint=4.9s value=False required=True",
            "\n".join(payload["evidence"]),
        )
        self.assertIn(
            "events@5.0s: deploy_90_percent_vdt False->True; logic4_active False->True; throttle_lock_release_cmd False->True",
            "\n".join(payload["evidence"]),
        )

    def test_demo_cli_renders_structured_answer(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["demo", "触发 logic3 会发生什么"])

        output = buffer.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertFalse(output.lstrip().startswith("{"))
        self.assertIn("intent: trigger_node", output)
        self.assertIn("matched_node: logic3", output)
        self.assertIn("target_logic: logic3", output)
        self.assertIn("evidence:", output)
        self.assertIn("outcome:", output)
        self.assertIn("possible_causes:", output)
        self.assertIn("required_changes:", output)
        self.assertIn("risks:", output)


if __name__ == "__main__":
    unittest.main()

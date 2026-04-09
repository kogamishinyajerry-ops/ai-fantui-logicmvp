import io
import http.client
import json
import os
import subprocess
import sys
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


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
DEMO_JSON_OUTPUT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "demo_answer_v1.schema.json"
DEMO_ANSWER_ASSET_PATH = FIXTURES_DIR / "demo_answer_asset_v1.json"
DEMO_JSON_OUTPUT_ASSET_PATH = FIXTURES_DIR / "demo_json_output_asset_v1.json"
DEMO_ANSWER_SCHEMA_VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_demo_answer_schema.py"
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
            0: {"sw1": "inactive", "logic1": "blocked", "logic3": "blocked", "thr_lock": "inactive"},
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
        cases = [
            {
                "name": "manual_override_below_vdt_threshold",
                "request": {
                    "tra_deg": -14.0,
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 50.0,
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
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": True,
                "expected_logic4_active": True,
                "expected_thr_lock_state": "active",
                "expected_logic4_failed": None,
            },
            {
                "name": "manual_override_still_blocks_logic4_on_engine",
                "request": {
                    "tra_deg": -14.0,
                    "feedback_mode": "manual_feedback_override",
                    "deploy_position_percent": 95.0,
                    "engine_running": False,
                },
                "expected_mode": "manual_feedback_override",
                "expected_vdt90": True,
                "expected_logic4_active": False,
                "expected_thr_lock_state": "blocked",
                "expected_logic4_failed": "engine_running",
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
        self.assertIn("<title>Well Harness 反推逻辑演示舱</title>", html)
        self.assertIn("id=\"demo-prompt\"", html)
        self.assertIn("logic4 和 throttle lock 有什么关系", html)
        self.assertIn("原始 JSON 调试", html)

    def test_demo_server_open_browser_helper_reports_failures(self):
        url = demo_server.demo_url("127.0.0.1", 8000)
        self.assertEqual(url, "http://127.0.0.1:8000/")

        opener = mock.Mock(return_value=True)
        self.assertTrue(demo_server.open_browser(url, opener=opener))
        opener.assert_called_once_with(url)

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertFalse(demo_server.open_browser(url, opener=mock.Mock(return_value=False)))
        self.assertIn("Could not open browser automatically.", buffer.getvalue())
        self.assertIn("Open http://127.0.0.1:8000/ manually.", buffer.getvalue())

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertFalse(
                demo_server.open_browser(url, opener=mock.Mock(side_effect=RuntimeError("blocked")))
            )
        self.assertIn("Could not open browser automatically: blocked.", buffer.getvalue())
        self.assertIn("Open http://127.0.0.1:8000/ manually.", buffer.getvalue())

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
        open_browser.assert_called_once_with("http://127.0.0.1:8765/")
        self.assertIn("Serving well-harness demo UI at http://127.0.0.1:8765/", buffer.getvalue())

        with mock.patch.object(demo_server, "ThreadingHTTPServer", side_effect=fake_server):
            with mock.patch.object(demo_server, "open_browser") as open_browser:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(demo_server.main(["--host", "127.0.0.1", "--port", "0"]), 0)

        open_browser.assert_not_called()

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

    def test_demo_static_assets_include_presenter_route_strip(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"presenter-route-strip\"",
            "aria-label=\"演示走查路径\"",
            "演示路径",
            "[输入]",
            "选问题",
            "[链路]",
            "看主板",
            "[高亮]",
            "讲关联",
            "[结果]",
            "扫证据",
            "[调试]",
            "查 JSON",
            "人工演示提示，不是自动化验收。",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".presenter-route-strip",
            ".route-strip-title",
            ".route-strip-note",
            ".route-step",
            "overflow-x: auto",
            "scroll-snap-type: x proximity",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "screenshot-free presenter route strip",
            "[Input] -> [Chain] -> [Highlight] -> [Structured answer] -> [Raw JSON]",
            "manual walkthrough guide",
            "replaces screenshot annotations",
            "not browser E2E automation",
            "not a screenshot annotation tool",
            "not a control-truth source",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "Use the screenshot-free route strip",
            "Input -> Chain -> Highlight -> Structured answer -> Raw JSON",
            "not browser E2E automation",
            "not a new answer payload or control truth",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_visible_presenter_run_card(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"panel presenter-run-card\"",
            "id=\"presenter-run-card-title\"",
            "Presenter Run Card",
            "首屏可点击演示顺序",
            "不是自动 readiness detector",
            "人工预演提示，不是浏览器自动化，也不是新的控制真值。",
            "class=\"presenter-run-card-grid\"",
            "class=\"run-card-step\"",
            "class=\"run-card-trigger is-selected\"",
            "运行桥接题",
            "运行未释放诊断",
            "运行触发题",
            "运行阈值预演",
            "`controller.py` 仍是唯一控制真值。",
            "`simplified plant feedback` 只用于演示解释，不是完整实时物理模型。",
            "Raw JSON 只是同一份 `DemoAnswer` 的调试视图",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".presenter-run-card",
            ".presenter-run-card-header",
            ".presenter-run-card-grid",
            ".run-card-step",
            ".run-card-kicker",
            ".run-card-trigger",
            ".run-card-trigger.is-selected",
            ".presenter-run-card-rails",
            ".presenter-run-card-boundary",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "Presenter Run Card",
            "four clickable bridge / diagnose / trigger / proposal steps",
            "manual presenter aid",
            "not an automatic readiness detector",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "clickable `Presenter Run Card`",
            "same bridge / diagnose / trigger / proposal order",
            "reuses the existing prompt flow and `DemoAnswer` payload",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "Use the visible Presenter Run Card",
            "bridge / diagnose / trigger / proposal sequence",
            "matching visible card on the first screen",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_lever_presenter_presets(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"lever-presets\"",
            "id=\"lever-presets-title\"",
            "id=\"lever-preset-status\"",
            "一键回填既有 `POST /api/lever-snapshot` 输入",
            "data-lever-preset=\"l3_waiting_vdt90\"",
            "data-lever-preset=\"ra_boundary_blocks_logic1\"",
            "data-lever-preset=\"n1k_limit_blocks_logic3\"",
            "data-lever-preset=\"manual_vdt90_ready\"",
            "L3 等待 VDT90",
            "RA blocker",
            "N1K blocker",
            "VDT90 ready",
            "当前场景：L3 等待 VDT90（默认演示位）。",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".lever-presets",
            ".lever-presets-header",
            ".lever-preset-status",
            ".lever-presets-grid",
            ".lever-preset-card",
            ".lever-preset-trigger",
            ".lever-preset-trigger.is-selected",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "const leverPresets = {",
            "l3_waiting_vdt90:",
            "ra_boundary_blocks_logic1:",
            "n1k_limit_blocks_logic3:",
            "manual_vdt90_ready:",
            "function applyLeverPresetPayload(payload)",
            "function syncLeverPresetSelection(presetKey)",
            "document.querySelectorAll(\"[data-lever-preset]\")",
            "applyLeverPresetPayload(leverPresets.l3_waiting_vdt90.payload);",
        ):
            self.assertIn(fragment, script)

        for fragment in (
            "visible `演示场景预设` row",
            "L3 等待 VDT90",
            "RA blocker",
            "N1K blocker",
            "VDT90 ready",
            "do not create a second state machine",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "visible `演示场景预设` buttons",
            "`L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready`",
            "do not create a second state machine",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "Use the visible lever presets",
            "L3 等待 VDT90, RA blocker, N1K blocker, and VDT90 ready",
            "without inventing a second state machine",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_audience_answer_field_legend(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "id=\"answer-field-legend\"",
            "class=\"answer-field-legend\"",
            "字段说明",
            "<dt>intent</dt>",
            "<dt>matched_node</dt>",
            "<dt>target_logic</dt>",
            "<dt>evidence</dt>",
            "<dt>outcome</dt>",
            "<dt>possible_causes</dt>",
            "<dt>required_changes</dt>",
            "<dt>risks</dt>",
            "<dt>raw JSON</dt>",
            "受控 demo 意图，不是开放式 LLM 意图识别。",
            "答案关联的 catalog 节点 / alias。",
            "答案关联的逻辑门。",
            "现有 harness evidence 摘要。",
            "受控提示，不是完整根因证明。",
            "dry-run / proposal 建议；不会直接修改 controller.py。",
            "简化模型和变更风险提示。",
            "同一份 DemoAnswer 的调试视图，不是第二套答案。",
            "不改变 UI/API payload",
            "不创建 schema",
            "不新增控制真值",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".answer-field-legend",
            ".answer-field-legend summary",
            ".answer-field-legend dl",
            ".answer-field-legend dt",
            ".answer-field-legend dd",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "Audience answer-field legend",
            "intent",
            "matched_node",
            "target_logic",
            "evidence",
            "outcome",
            "possible_causes",
            "required_changes",
            "risks",
            "raw JSON",
            "reading aid",
            "not a new schema, payload, or control truth",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "Audience answer-field legend",
            "compact answer guide",
            "Audience answer-field legend",
            "Answer sections counts",
            "Structured answer",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_compact_answer_guide_layout(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"answer-guide\"",
            "aria-label=\"答案字段与结果分区导览\"",
            "class=\"answer-guide-intro\"",
            "结果导览",
            "字段说明和数量标签都来自同一份答案。",
            "class=\"answer-guide-grid\"",
            "id=\"answer-field-legend\"",
            "id=\"answer-section-summary\"",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".answer-guide",
            ".answer-guide-intro",
            ".answer-guide-grid",
            "grid-template-columns: minmax(260px, 0.95fr) minmax(260px, 1.05fr)",
            ".answer-guide .answer-field-legend",
            ".answer-guide .answer-section-summary",
            "grid-template-columns: 1fr",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "compact answer guide",
            "legend and `Answer sections` summary",
            "same `DemoAnswer` payload",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "compact answer guide",
            "`Answer sections`",
            "without changing the `DemoAnswer` payload",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "compact answer guide",
            "Audience answer-field legend",
            "Answer sections counts",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_mobile_answer_guide_spacing(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"answer-guide\"",
            "class=\"answer-guide-grid\"",
            "id=\"answer-field-legend\"",
            "id=\"answer-section-summary\"",
            "id=\"answer-section-summary-items\"",
            "id=\"answer-section-keyboard-hint\"",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            "@media (max-width: 780px)",
            ".answer-guide",
            "gap: 12px",
            "padding: 12px",
            "border-radius: 12px",
            ".answer-guide-intro",
            "line-height: 1.45",
            ".answer-guide-grid",
            "grid-template-columns: 1fr",
            ".answer-guide .answer-field-legend",
            ".answer-guide .answer-section-summary",
            ".summary-chip",
            "min-height: 42px",
            "white-space: normal",
            "button.summary-chip",
            "text-align: left",
            "@media (max-width: 520px)",
            "width: 100%",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "mobile / narrow screens",
            "compact answer guide top-to-bottom",
            "touch-friendly scanning",
            "without changing the payload",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "narrow screens",
            "touch-friendly spacing",
            "same payload and field semantics",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "narrow screens",
            "compact answer guide top-to-bottom",
            "touch-friendly",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_showcase_surface_layout(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

        for fragment in (
            "class=\"showcase-mission\"",
            "拖动反推拉杆，实时看 SW / logic / plant feedback 如何点亮。",
            "class=\"showcase-surface\"",
            "aria-label=\"中文演示展示面\"",
            "class=\"showcase-intro\"",
            "演示流",
            "拉杆 -> HUD -> 逻辑主板 -> 当前结论",
            "class=\"showcase-grid\"",
            "class=\"panel lever-panel\"",
            "id=\"lever-tra\"",
            "class=\"condition-panel\"",
            "id=\"condition-ra\"",
            "id=\"condition-engine-running\"",
            "id=\"condition-aircraft-ground\"",
            "id=\"condition-reverser-inhibited\"",
            "id=\"condition-eec-enable\"",
            "id=\"condition-n1k\"",
            "id=\"condition-n1k-limit\"",
            "id=\"condition-feedback-mode\"",
            "id=\"condition-deploy-position\"",
            "条件面板",
            "VDT 模式",
            "VDT 反馈",
            "manual_feedback_override",
            "simplified plant diagnostic override",
            ">=90% 点亮 VDT90",
            "L1 需要 RA &lt; 6ft",
            "L3 需要 N1K &lt; limit",
            "type=\"range\"",
            "min=\"-32\"",
            "max=\"0\"",
            "SW1 -1.4° ~ -6.2°",
            "SW2 -5.0° ~ -9.8°",
            "L3 ≤ -11.74°",
            "id=\"hud-tra\"",
            "id=\"lever-result\"",
            "class=\"panel qa-drawer\"",
            "<details id=\"raw-json-details\" class=\"debug-inspector\">",
            "原始 JSON 调试",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".showcase-mission",
            ".showcase-surface",
            ".showcase-intro",
            ".showcase-kicker",
            ".showcase-grid",
            ".lever-panel",
            ".lever-console",
            ".lever-readout",
            ".lever-thresholds",
            ".condition-panel",
            ".condition-grid",
            ".condition-range",
            ".condition-toggle",
            ".condition-number",
            ".condition-select",
            ".condition-wide",
            ".feedback-override-control",
            ".hud-grid",
            ".lever-result",
            ".qa-drawer",
            "minmax(300px, 0.88fr) minmax(640px, 1.52fr)",
            "grid-template-areas:",
            "\"prompt chain\"",
            "\"answer answer\"",
            ".showcase-grid .lever-panel",
            ".showcase-grid .chain-panel",
            ".showcase-grid .result-grid",
            ".showcase-grid .grouped-examples",
            ".showcase-grid .examples button",
            "overflow-wrap: anywhere",
            ".showcase-grid textarea",
            ".logic-stage",
            ".logic-stage-wide",
            ".logic-note",
            ".chain-panel",
            "border-color: rgba(40, 244, 255, 0.36)",
            ".chain-node.is-blocked",
            ".chain-node.is-inactive",
            ".output-card",
            ".showcase-grid .highlight-explanation",
            ".raw-card .debug-inspector",
            ".raw-card pre",
            "box-shadow: none",
            "opacity: 0.68",
            "@media (max-width: 780px)",
            ".showcase-grid .grouped-examples",
            "grid-template-columns: 1fr",
            ".showcase-grid .example-group",
            "width: auto",
            "\"prompt\"",
            "\"chain\"",
            "\"answer\"",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "interactive reverse-lever cockpit",
            "lever cockpit showcase",
            "throttle lever, HUD, control chain, and current-result summary",
            "POST /api/lever-snapshot",
            "secondary drawer",
        ):
            self.assertIn(fragment, readme)

    def test_demo_static_assets_include_desktop_first_screen_density_polish(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")

        for fragment in (
            "class=\"lever-note\"",
            "class=\"condition-panel-heading\"",
            "class=\"condition-note\"",
            "反馈 / 诊断（simplified plant）",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            "@media (min-width: 1101px) and (max-height: 1120px)",
            ".hero",
            ".presenter-route-strip",
            ".showcase-surface",
            ".showcase-grid",
            ".lever-panel",
            ".lever-console,",
            ".condition-panel {",
            ".condition-grid",
            ".hud-grid div,",
            ".feedback-grid div {",
            ".lever-result {",
        ):
            self.assertIn(fragment, css)

    def test_demo_static_assets_include_cockpit_toggle_and_hud_polish(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")

        for fragment in (
            "id=\"condition-engine-running\"",
            "id=\"condition-aircraft-ground\"",
            "id=\"condition-reverser-inhibited\"",
            "id=\"condition-eec-enable\"",
            "id=\"condition-feedback-mode\"",
            "id=\"condition-deploy-position\"",
            "id=\"hud-tra\"",
            "id=\"hud-engine-ground\"",
            "id=\"hud-eec-enable\"",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".condition-toggle input[type=\"checkbox\"]",
            "appearance: none",
            ".condition-toggle input[type=\"checkbox\"]::before",
            ".condition-toggle input[type=\"checkbox\"]:checked",
            "translateX(18px)",
            ".condition-toggle input[type=\"checkbox\"]:focus-visible",
            ".hud-grid dt",
            "text-transform: uppercase",
            ".hud-grid dd",
            "font-weight: 800",
            "text-shadow: 0 0 12px rgba(40, 244, 255, 0.16)",
        ):
            self.assertIn(fragment, css)

    def test_demo_static_assets_include_interactive_lever_snapshot_wiring(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        for fragment in (
            "id=\"lever-tra\"",
            "type=\"range\"",
            "name=\"tra_deg\"",
            "name=\"radio_altitude_ft\"",
            "name=\"engine_running\"",
            "name=\"aircraft_on_ground\"",
            "name=\"reverser_inhibited\"",
            "name=\"eec_enable\"",
            "name=\"n1k\"",
            "name=\"max_n1k_deploy_limit\"",
            "id=\"lever-tra-value\"",
            "id=\"lever-status\"",
            "id=\"hud-switches\"",
            "id=\"hud-locks\"",
            "id=\"hud-position\"",
            "id=\"lever-feedback-details\"",
            "反馈 / 诊断（simplified plant）",
            "first-cut feedback / diagnostic 假设",
            "id=\"lever-evidence-details\"",
            "证据 / 风险（默认折叠）",
            "诊断问答（冻结 / 后续开发）",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".lever-panel",
            ".lever-console",
            "#lever-tra",
            ".condition-panel",
            ".condition-grid",
            ".condition-range",
            ".condition-toggle",
            ".condition-number",
            ".condition-select",
            ".feedback-override-control",
            ".hud-grid",
            ".feedback-panel",
            ".feedback-grid",
            ".lever-result",
            ".lever-evidence-details",
            ".qa-drawer",
            ".logic-note",
            ".chain-node.is-active",
            ".chain-node.is-blocked",
            ".chain-node.is-inactive",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "function syncConditionReadouts()",
            "function collectLeverSnapshotPayload(traDeg)",
            "function runLeverSnapshot(traDeg)",
            "fetch(\"/api/lever-snapshot\"",
            "radio_altitude_ft: Number(document.getElementById(\"condition-ra\").value)",
            "engine_running: document.getElementById(\"condition-engine-running\").checked",
            "aircraft_on_ground: document.getElementById(\"condition-aircraft-ground\").checked",
            "reverser_inhibited: document.getElementById(\"condition-reverser-inhibited\").checked",
            "eec_enable: document.getElementById(\"condition-eec-enable\").checked",
            "n1k: Number(document.getElementById(\"condition-n1k\").value)",
            "max_n1k_deploy_limit: Number(document.getElementById(\"condition-n1k-limit\").value)",
            "feedback_mode: document.getElementById(\"condition-feedback-mode\").value",
            "deploy_position_percent: Number(document.getElementById(\"condition-deploy-position\").value)",
            "leverInput.addEventListener(\"input\"",
            "document.querySelectorAll(\".condition-panel input, .condition-panel select\")",
            "scheduleLeverSnapshot()",
            "function applyLeverNodeStates(nodes)",
            "is-blocked",
            "is-inactive",
            "DeployController.explain",
            "不是完整实时物理仿真",
        ):
            self.assertIn(fragment, script)

        self.assertIn("<details id=\"raw-json-details\" class=\"debug-inspector\">", html)
        self.assertNotIn("id=\"raw-json-details\" class=\"debug-inspector\" open", html)
        self.assertNotIn("class=\"chain-node sub-node logic-node\"", html)

    def test_demo_static_assets_include_chain_state_truth_boundary_legend(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"chain-state-legend\"",
            "状态图例 / truth boundary",
            "Active = 当前已点亮",
            "Blocked = 等待条件",
            "Inactive = 当前路径未进入",
            "Controller truth：SW / L1-L4 / command 节点来自后端 controller snapshot。",
            "Simplified plant feedback：TLS unlock / PLS unlock / VDT90 / 位移只用于演示反馈",
            "颜色来自后端快照，不是完整因果证明。",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".chain-state-legend",
            ".chain-state-legend-header",
            ".chain-state-chip-row",
            ".state-chip",
            ".state-chip.is-active",
            ".state-chip.is-blocked",
            ".state-chip.is-inactive",
            ".truth-boundary-rails",
            ".truth-rail.controller",
            ".truth-rail.plant",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "visible `状态图例 / truth boundary`",
            "`Active` means the backend snapshot currently lights the node",
            "`Blocked` means the node is waiting on named conditions",
            "separates controller truth from simplified plant feedback",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "visible `状态图例 / truth boundary` strip",
            "Active / Blocked / Inactive",
            "distinguish controller truth from simplified plant feedback",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "Use the visible 状态图例 / truth boundary",
            "Active / Blocked / Inactive",
            "separate controller truth from simplified plant feedback",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_lever_result_reading_rails(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "class=\"lever-result-note\"",
            "Headline -> Blocker -> Next step",
            "同一份 lever snapshot",
            "class=\"lever-result-grid\"",
            "class=\"result-rail result-rail-headline\"",
            "class=\"result-rail result-rail-blocker\"",
            "class=\"result-rail result-rail-next-step\"",
            "class=\"result-rail-kicker\">1. Headline</p>",
            "class=\"result-rail-kicker\">2. Blocker</p>",
            "class=\"result-rail-kicker\">3. Next step</p>",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".lever-result-note",
            ".lever-result-grid",
            ".result-rail",
            ".result-rail-kicker",
            ".result-rail-blocker",
            ".result-rail-next-step",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "read it top-to-bottom as `Headline -> Blocker -> Next step`",
            "same lever snapshot payload",
            "not a second presenter-only explanation layer",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "fixed presenter reading rails",
            "`Headline`, `Blocker`, and `Next step`",
            "same lever snapshot payload",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "Read 当前结论 in the fixed order Headline -> Blocker -> Next step",
            "same lever snapshot payload",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_result_source_note(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "id=\"result-source-mode\"",
            "class=\"result-source-mode\"",
            "当前来源：等待 payload。",
            "id=\"result-payload-note\"",
            "结构化结果、当前结论和 Raw JSON 会共用同一份 payload。",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".result-source-mode",
            ".result-payload-note",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "function setResultSourceInfo(modeText, payloadNote)",
            "当前来源：受控 prompt / POST /api/demo / DemoAnswer。",
            "结构化结果、高亮解释和 Raw JSON 共用同一份 DemoAnswer payload。",
            "当前来源：拉杆快照 / POST /api/lever-snapshot。",
            "当前结论、折叠证据区和 Raw JSON 共用同一份 lever snapshot payload。",
            "当前来源：UI/API 错误。",
            "当前没有生成新的业务 payload；请先修复输入或网络错误。",
        ):
            self.assertIn(fragment, script)

        for fragment in (
            "visible source note in `结果摘要`",
            "`POST /api/demo / DemoAnswer` or `POST /api/lever-snapshot`",
            "share one payload",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "visible source note",
            "`POST /api/demo / DemoAnswer`",
            "`POST /api/lever-snapshot`",
            "share one payload",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "Use the visible source note in 结果摘要",
            "DemoAnswer or lever-snapshot output",
            "one payload story",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_hold_lever_result_when_demoanswer_is_active(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(DEMO_UI_HANDCHECK_SCRIPT_PATH), "--walkthrough"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")

        for fragment in (
            "id=\"lever-result-mode\"",
            "class=\"lever-result-mode\"",
            "当前结论来源：等待 lever snapshot。",
        ):
            self.assertIn(fragment, html)

        for fragment in (
            ".lever-result-mode",
            "border-radius: 999px",
            "font-family: var(--font-mono)",
        ):
            self.assertIn(fragment, css)

        for fragment in (
            "function setLeverResultMode(modeText)",
            "function setLeverResultPlaceholder(headline, blocker, nextStep, evidenceItems, modeText)",
            "当前结论来源：问答模式已激活；lever snapshot rails 已暂停。",
            "当前结果来自 DemoAnswer；如需当前结论，请重新拖动拉杆或使用场景预设。",
            "当前不是 lever snapshot。",
            "继续读 Structured answer，或重新请求 lever snapshot。",
            "当前结果区显示的是 DemoAnswer，不复用上一次 lever snapshot。",
            "当前结论来源：lever snapshot / POST /api/lever-snapshot。",
            "当前结论来源：UI/API 错误；lever snapshot rails 已暂停。",
            "当前没有新的业务 payload；请先修复错误再看当前结论。",
        ):
            self.assertIn(fragment, script)

        for fragment in (
            "lever `当前结论` rail should switch into a visible hold state",
            "stale lever evidence",
        ):
            self.assertIn(fragment, talk_track)

        for fragment in (
            "visible hold state",
            "previous lever snapshot",
            "active payload source",
        ):
            self.assertIn(fragment, readme)

        for fragment in (
            "confirm 当前结论 switches to a visible hold state",
            "stale lever snapshot text",
        ):
            self.assertIn(fragment, result.stdout)

    def test_demo_static_assets_include_presenter_callout_labels(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        talk_track = DEMO_PRESENTER_TALK_TRACK_PATH.read_text(encoding="utf-8")

        for label in (
            "[输入]",
            "[链路]",
            "[高亮]",
            "[结果]",
            "[调试]",
        ):
            self.assertIn(f"<span class=\"presenter-callout\">{label}</span>", html)

        for label in ("[Input]", "[Chain]", "[Highlight]", "[Structured answer]", "[Raw JSON]"):
            self.assertIn(label, talk_track)

        self.assertIn("提问区", html)
        self.assertIn("逻辑主板", html)
        self.assertIn("为什么高亮", html)
        self.assertIn("推理结果", html)
        self.assertIn("原始 JSON 调试", html)
        self.assertIn("page callout labels", talk_track)
        self.assertIn(".presenter-callout", css)
        self.assertIn("var(--accent-dark)", css)

    def test_demo_static_html_contains_key_ui_elements(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")

        self.assertIn("well-harness 确定性演示", html)
        self.assertIn("反推逻辑演示舱", html)
        self.assertIn("确定性演示层", html)
        self.assertIn("简化 plant", html)
        self.assertIn("SW1 -> L1/TLS115 -> TLS 解锁", html)
        self.assertIn("data-node=\"logic4\"", html)
        self.assertIn("data-node=\"vdt90\"", html)
        self.assertIn("data-prompt=\"为什么 throttle lock 没释放\"", html)
        self.assertIn("logic-note", html)
        self.assertIn("诊断问答（冻结 / 后续开发）", html)

    def test_demo_static_assets_include_polish_and_highlight_refinements(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("id=\"ui-status\"", html)
        self.assertIn("data-node=\"tls115\"", html)
        self.assertIn("data-node=\"etrac_540v\"", html)
        self.assertIn("data-node=\"eec_deploy\"", html)
        self.assertIn("data-node=\"pls_power\"", html)
        self.assertIn("data-node=\"pdu_motor\"", html)
        self.assertIn("data-node=\"thr_lock\"", html)
        self.assertIn("button:disabled", css)
        self.assertIn(".answer-section.is-error", css)
        self.assertIn(".logic-stage", css)
        self.assertIn(".logic-note", css)
        self.assertIn("确定性推理中...", script)
        self.assertIn("请输入一个受控 demo prompt", script)
        self.assertIn("network_error", script)
        self.assertIn("document.querySelectorAll(\"[data-prompt]\")", script)
        self.assertIn("\"logic4->thr_lock\": [\"logic4\", \"thr_lock\"]", script)
        self.assertIn("thr_lock: [\"thr_lock\"]", script)
        self.assertIn("logic3: [\"logic3\", \"eec_deploy\", \"pls_power\", \"pdu_motor\"]", script)

    def test_demo_static_assets_include_flow_polish_controls(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("id=\"selected-example\"", html)
        self.assertIn("class=\"is-selected\" aria-pressed=\"true\"", html)
        self.assertIn("aria-pressed=\"false\"", html)
        self.assertIn("mobile-step-rail", html)
        self.assertIn("<details id=\"raw-json-details\" class=\"debug-inspector\">", html)
        self.assertIn("<summary><span class=\"presenter-callout\">[调试]</span> 原始 JSON 调试</summary>", html)
        self.assertIn(".examples button.is-selected", css)
        self.assertIn(".raw-card summary", css)
        self.assertIn(".chain-map.mobile-step-rail", css)
        self.assertIn("overflow-x: auto", css)
        self.assertIn("scroll-snap-type: x proximity", css)
        self.assertIn("function syncSelectedPrompt(prompt)", script)
        self.assertIn("button.setAttribute(\"aria-pressed\", isSelected ? \"true\" : \"false\")", script)
        self.assertIn("当前示例：自定义问题", script)
        self.assertIn("syncSelectedPrompt(promptInput.value)", script)

    def test_demo_static_assets_include_prompt_guidance_and_keyboard_affordance(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("grouped-examples", html)
        self.assertIn("data-category=\"bridge\"", html)
        self.assertIn("data-category=\"diagnosis\"", html)
        self.assertIn("data-category=\"trigger\"", html)
        self.assertIn("data-category=\"proposal\"", html)
        self.assertIn("data-intent=\"logic4_thr_lock_bridge\"", html)
        self.assertIn("data-intent=\"diagnose_problem\"", html)
        self.assertIn("data-intent=\"trigger_node\"", html)
        self.assertIn("data-intent=\"propose_logic_change\"", html)
        self.assertIn("链路关系", html)
        self.assertIn("未释放诊断", html)
        self.assertIn("触发影响", html)
        self.assertIn("改阈值预演", html)
        self.assertIn("id=\"prompt-keyboard-hint\"", html)
        self.assertIn("按 Cmd/Ctrl+Enter 运行；普通 Enter 换行。", html)
        self.assertIn("<details id=\"demo-help\" class=\"demo-help\">", html)
        self.assertIn("不是开放式 LLM", html)
        self.assertIn("简化 plant", html)

        self.assertIn(".grouped-examples", css)
        self.assertIn(".example-group", css)
        self.assertIn(".prompt-hint", css)
        self.assertIn(".demo-help summary", css)

        self.assertIn("promptInput.addEventListener(\"keydown\"", script)
        self.assertIn("event.metaKey || event.ctrlKey", script)
        self.assertIn("event.key === \"Enter\"", script)
        self.assertIn("event.preventDefault()", script)
        self.assertIn("form.requestSubmit()", script)

    def test_demo_static_assets_include_highlight_explanation(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("id=\"highlight-explanation\"", html)
        self.assertIn("为什么高亮", html)
        self.assertIn("id=\"highlight-payload-fields\"", html)
        self.assertIn("id=\"highlight-node-list\"", html)
        self.assertIn("id=\"highlight-explanation-list\"", html)
        self.assertIn("高亮来自答案里的命中节点 / 目标逻辑", html)
        self.assertIn("不是完整因果证明", html)

        self.assertIn(".highlight-explanation", css)
        self.assertIn(".highlight-explanation h3", css)
        self.assertIn(".highlight-explanation li", css)

        self.assertIn("function highlightedNodesForPayload(payload)", script)
        self.assertIn("function renderHighlightExplanation(payload)", script)
        self.assertIn("highlightedNodesForPayload(payload)", script)
        self.assertIn("答案关联：意图=", script)
        self.assertIn("命中节点=${textOrDash(payload.matched_node)}", script)
        self.assertIn("目标逻辑=${textOrDash(payload.target_logic)}", script)
        self.assertIn("链路桥接：L4 是上游逻辑门，THR_LOCK 是下游释放命令。", script)
        self.assertIn("L3 相关答案会同时点亮 EEC / PLS / PDU 命令子节点。", script)
        self.assertIn("这里只表示答案关联，不是完整因果证明", script)
        self.assertIn("UI/API 错误时不显示链路高亮。", script)

    def test_demo_static_assets_include_answer_section_summary(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("id=\"answer-section-summary\"", html)
        self.assertIn("结果分区", html)
        self.assertIn("id=\"answer-section-keyboard-hint\"", html)
        self.assertIn("方向键可在分区标签之间移动。", html)
        self.assertIn("id=\"answer-section-summary-items\"", html)
        self.assertIn("summary-chip is-empty", html)
        self.assertIn("默认折叠；展开查看证据 / 风险。", html)

        self.assertIn(".answer-section-summary", css)
        self.assertIn(".summary-hint", css)
        self.assertIn(".summary-chips", css)
        self.assertIn(".summary-chip", css)
        self.assertIn("button.summary-chip", css)
        self.assertIn(".summary-chip.is-empty", css)
        self.assertIn(".summary-chip.is-error", css)
        self.assertIn(".summary-chip:focus-visible", css)
        self.assertIn(".answer-section:focus-visible", css)
        self.assertIn("scroll-margin-top", css)

        self.assertIn("function answerSectionId(sectionName)", script)
        self.assertIn("return `answer-section-${sectionName}`", script)
        self.assertIn("function focusAnswerSection(sectionName)", script)
        self.assertIn("document.getElementById(answerSectionId(sectionName))", script)
        self.assertIn("target.focus({preventScroll: true})", script)
        self.assertIn("target.scrollIntoView({behavior: \"smooth\", block: \"start\"})", script)
        self.assertIn("function renderAnswerSectionSummary(payload)", script)
        self.assertIn("function renderAnswerSectionSummaryUnavailable()", script)
        self.assertIn("section.id = answerSectionId(title)", script)
        self.assertIn("section.tabIndex = -1", script)
        self.assertIn("const chip = document.createElement(\"button\")", script)
        self.assertIn("chip.type = \"button\"", script)
        self.assertIn("chip.setAttribute(\"aria-controls\", answerSectionId(sectionName))", script)
        self.assertIn("chip.setAttribute(\"aria-describedby\", \"answer-section-keyboard-hint\")", script)
        self.assertIn("chip.addEventListener(\"click\", () => focusAnswerSection(sectionName))", script)
        self.assertIn("chip.addEventListener(\"keydown\", handleSummaryChipKeydown)", script)
        self.assertIn("sections.map((sectionName)", script)
        self.assertIn("Array.isArray(payload[sectionName]) ? payload[sectionName] : []", script)
        self.assertIn("${sectionLabels[sectionName] || sectionName} ${count} 条", script)
        self.assertIn("${sectionLabels[sectionName] || sectionName} 0 条 — 本答案为空", script)
        self.assertIn("UI/API 错误时分区摘要不可用。", script)
        self.assertIn("renderAnswerSectionSummary(payload)", script)
        self.assertIn("renderAnswerSectionSummaryUnavailable()", script)
        for section_name in ("evidence", "outcome", "possible_causes", "required_changes", "risks"):
            self.assertIn(f"\"{section_name}\"", script)

    def test_demo_static_assets_include_answer_section_jump_focus(self):
        css = (DEMO_UI_STATIC_DIR / "demo.css").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("function answerSectionId(sectionName)", script)
        self.assertIn("return `answer-section-${sectionName}`", script)
        self.assertIn("function focusAnswerSection(sectionName)", script)
        self.assertIn("document.getElementById(answerSectionId(sectionName))", script)
        self.assertIn("target.focus({preventScroll: true})", script)
        self.assertIn("target.scrollIntoView({behavior: \"smooth\", block: \"start\"})", script)
        self.assertIn("section.id = answerSectionId(title)", script)
        self.assertIn("section.tabIndex = -1", script)
        self.assertIn("const chip = document.createElement(\"button\")", script)
        self.assertIn("chip.type = \"button\"", script)
        self.assertIn("chip.setAttribute(\"aria-controls\", answerSectionId(sectionName))", script)
        self.assertIn("chip.addEventListener(\"click\", () => focusAnswerSection(sectionName))", script)
        self.assertIn("UI/API 错误时分区摘要不可用。", script)
        self.assertIn(".summary-chip:focus-visible", css)
        self.assertIn(".answer-section:focus-visible", css)
        self.assertIn("scroll-margin-top", css)

    def test_demo_static_assets_include_answer_section_keyboard_navigation(self):
        html = (DEMO_UI_STATIC_DIR / "demo.html").read_text(encoding="utf-8")
        script = (DEMO_UI_STATIC_DIR / "demo.js").read_text(encoding="utf-8")

        self.assertIn("id=\"answer-section-keyboard-hint\"", html)
        self.assertIn("方向键可在分区标签之间移动。", html)
        self.assertIn("function focusSummaryChip(currentChip, key)", script)
        self.assertIn("function handleSummaryChipKeydown(event)", script)
        self.assertIn("#answer-section-summary-items button.summary-chip", script)
        self.assertIn("[\"ArrowRight\", \"ArrowDown\", \"ArrowLeft\", \"ArrowUp\", \"Home\", \"End\"].includes(event.key)", script)
        self.assertIn("event.preventDefault()", script)
        self.assertIn("focusSummaryChip(event.currentTarget, event.key)", script)
        self.assertIn("ArrowRight: Math.min(currentIndex + 1, lastIndex)", script)
        self.assertIn("ArrowDown: Math.min(currentIndex + 1, lastIndex)", script)
        self.assertIn("ArrowLeft: Math.max(currentIndex - 1, 0)", script)
        self.assertIn("ArrowUp: Math.max(currentIndex - 1, 0)", script)
        self.assertIn("Home: 0", script)
        self.assertIn("End: lastIndex", script)
        self.assertIn("chips[targetIndex].focus()", script)
        self.assertIn("chip.addEventListener(\"click\", () => focusAnswerSection(sectionName))", script)
        self.assertIn("chip.addEventListener(\"keydown\", handleSummaryChipKeydown)", script)
        self.assertIn("chip.setAttribute(\"aria-describedby\", \"answer-section-keyboard-hint\")", script)
        self.assertNotIn("event.key === \" \"", script)

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

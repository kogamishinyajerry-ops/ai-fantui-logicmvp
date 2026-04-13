import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_second_system_smoke_schema.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def second_system_smoke_schema_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class SecondSystemSmokeSchemaValidationScriptTests(unittest.TestCase):
    def test_second_system_smoke_schema_standalone_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=second_system_smoke_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
            return

        self.assertIn("PASS: validated 2 second-system smoke payloads", result.stdout)
        self.assertIn("docs/json_schema/second_system_smoke_v1.schema.json", result.stdout)
        self.assertIn("minimal_landing_gear_extension", result.stdout)
        self.assertIn("adapter_runtime_proof", result.stdout)
        self.assertIn("custom_reverse_control_v1", result.stdout)
        self.assertIn("full_workbench_bundle", result.stdout)

    def test_second_system_smoke_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=second_system_smoke_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("docs/json_schema/second_system_smoke_v1.schema.json", payload["schema_path"])
        self.assertEqual(2, len(payload["results"]))
        self.assertEqual("pass", payload["results"][0]["validation_status"])
        self.assertEqual("minimal_landing_gear_extension", payload["results"][0]["system_id"])
        self.assertEqual("truth_adapter", payload["results"][0]["proof_mode"])
        self.assertTrue(payload["results"][0]["smoke_passed"])
        self.assertEqual("custom_reverse_control_v1", payload["results"][1]["system_id"])
        self.assertEqual("intake_packet", payload["results"][1]["proof_mode"])
        self.assertTrue(payload["results"][1]["smoke_passed"])

    def test_second_system_smoke_schema_standalone_script_json_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=second_system_smoke_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual("docs/json_schema/second_system_smoke_v1.schema.json", payload["schema_path"])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])


if __name__ == "__main__":
    unittest.main()

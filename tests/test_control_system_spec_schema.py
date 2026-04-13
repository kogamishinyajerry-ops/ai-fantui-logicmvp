import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_control_system_spec_schema.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def control_system_spec_schema_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class ControlSystemSpecSchemaValidationScriptTests(unittest.TestCase):
    def test_control_system_spec_schema_standalone_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=control_system_spec_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
            return

        self.assertIn("PASS: validated 3 control-system spec payloads", result.stdout)
        self.assertIn("docs/json_schema/control_system_spec_v1.schema.json", result.stdout)
        self.assertIn("system_id=reference_thrust_reverser_deploy", result.stdout)
        self.assertIn("system_id=custom_reverse_control_v1", result.stdout)

    def test_control_system_spec_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=control_system_spec_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("docs/json_schema/control_system_spec_v1.schema.json", payload["schema_path"])
        self.assertEqual(3, len(payload["results"]))
        self.assertEqual(["pass", "pass", "pass"], [item["validation_status"] for item in payload["results"]])
        self.assertIn("reference_thrust_reverser_deploy", {item["system_id"] for item in payload["results"]})
        self.assertIn("custom_reverse_control_v1", {item["system_id"] for item in payload["results"]})

    def test_control_system_spec_schema_standalone_script_json_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=control_system_spec_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual("docs/json_schema/control_system_spec_v1.schema.json", payload["schema_path"])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])


if __name__ == "__main__":
    unittest.main()

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_two_system_runtime_comparison.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def comparison_schema_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class TwoSystemRuntimeComparisonSchemaValidationScriptTests(unittest.TestCase):
    def test_two_system_runtime_comparison_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=comparison_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
            return

        self.assertIn("PASS: validated 1 two-system runtime comparison payload", result.stdout)
        self.assertIn("docs/json_schema/two_system_runtime_comparison_v1.schema.json", result.stdout)

    def test_two_system_runtime_comparison_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=comparison_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("docs/json_schema/two_system_runtime_comparison_v1.schema.json", payload["schema_path"])
        self.assertEqual(1, len(payload["results"]))
        self.assertEqual("pass", payload["results"][0]["validation_status"])
        self.assertEqual("reference_thrust_reverser_deploy", payload["results"][0]["primary_system_id"])
        self.assertEqual("minimal_landing_gear_extension", payload["results"][0]["comparison_system_id"])

    def test_two_system_runtime_comparison_script_json_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=comparison_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual("docs/json_schema/two_system_runtime_comparison_v1.schema.json", payload["schema_path"])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])


if __name__ == "__main__":
    unittest.main()

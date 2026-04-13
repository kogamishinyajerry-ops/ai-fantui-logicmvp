import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_landing_gear_playback.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def landing_gear_playback_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class LandingGearPlaybackValidationScriptTests(unittest.TestCase):
    def test_landing_gear_playback_validation_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=landing_gear_playback_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
            return

        self.assertIn("PASS: validated landing-gear adapter-backed playback proof", result.stdout)
        self.assertIn("landing_gear_adapter_backed_playback_schema", result.stdout)
        self.assertIn("landing_gear_adapter_backed_playback_alignment", result.stdout)

    def test_landing_gear_playback_validation_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=landing_gear_playback_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(
            [
                "landing_gear_adapter_backed_playback_schema",
                "landing_gear_adapter_backed_playback_alignment",
            ],
            [item["case"] for item in payload["results"]],
        )
        self.assertTrue(all(item["validation_status"] == "pass" for item in payload["results"]))

    def test_landing_gear_playback_validation_script_json_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=landing_gear_playback_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual("docs/json_schema/playback_trace_v1.schema.json", payload["schema_path"])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])


if __name__ == "__main__":
    unittest.main()

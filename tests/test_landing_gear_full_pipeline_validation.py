import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_landing_gear_full_pipeline.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def pipeline_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class LandingGearFullPipelineValidationTests(unittest.TestCase):
    def test_pipeline_script_smoke_text(self):
        """Smoke test: script exits 0 and prints PASS lines in text mode."""
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=pipeline_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

        if "SKIP: optional dependency 'jsonschema'" not in result.stdout:
            self.assertIn("PASS", result.stdout)
            self.assertIn("intake_to_spec_schema", result.stdout)
            self.assertIn("intake_to_playback_schema", result.stdout)
            self.assertIn("intake_to_diagnosis_schema", result.stdout)
            self.assertIn("intake_to_knowledge_schema", result.stdout)

    def test_pipeline_script_json_pass_output(self):
        """JSON mode: all 4 schema cases return pass and status=pass."""
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=pipeline_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        payload = json.loads(result.stdout)

        self.assertEqual("pass", payload["status"], msg=f"payload:\n{json.dumps(payload, indent=2)}")
        self.assertEqual(
            [
                "intake_to_spec_schema",
                "intake_to_playback_schema",
                "intake_to_diagnosis_schema",
                "intake_to_knowledge_schema",
            ],
            [item["case"] for item in payload["results"]],
        )
        self.assertTrue(
            all(item["validation_status"] == "pass" for item in payload["results"]),
            msg=f"Some cases did not pass: {payload['results']}",
        )

    def test_pipeline_script_json_skip_output(self):
        """When jsonschema is unavailable, script exits 0 with status=skip."""
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=pipeline_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertIn("jsonschema", payload["reason"])

    def test_pipeline_script_text_mode_output(self):
        """Text mode: emits one PASS line per stage and a final summary."""
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "text"],
            cwd=PROJECT_ROOT,
            env=pipeline_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        self.assertIn("PASS", result.stdout)

    def test_pipeline_script_bad_format_exits_2(self):
        """Bad --format argument causes exit code 2."""
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "bad"],
            cwd=PROJECT_ROOT,
            env=pipeline_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()

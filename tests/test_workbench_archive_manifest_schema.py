import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_workbench_archive_manifest_schema.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"


def workbench_archive_manifest_schema_script_env(env_overrides=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return env


class WorkbenchArchiveManifestSchemaValidationScriptTests(unittest.TestCase):
    def test_workbench_archive_manifest_schema_standalone_script_smoke(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            env=workbench_archive_manifest_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        if "SKIP: optional dependency 'jsonschema' is not installed" in result.stdout:
            self.assertIn("SKIP: optional dependency 'jsonschema' is not installed", result.stdout)
            return

        self.assertIn("PASS: validated 2 workbench archive manifest payloads", result.stdout)
        self.assertIn("docs/json_schema/workbench_archive_manifest_v1.schema.json", result.stdout)
        self.assertIn("bundle_kind=full_workbench_bundle", result.stdout)
        self.assertIn("bundle_kind=clarification_follow_up", result.stdout)

    def test_workbench_archive_manifest_schema_standalone_script_json_pass_output(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=workbench_archive_manifest_schema_script_env(),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("docs/json_schema/workbench_archive_manifest_v1.schema.json", payload["schema_path"])
        self.assertEqual(2, len(payload["results"]))
        self.assertEqual(["pass", "pass"], [item["validation_status"] for item in payload["results"]])
        self.assertIn("clarification_follow_up", {item["bundle_kind"] for item in payload["results"]})
        self.assertIn("full_workbench_bundle", {item["bundle_kind"] for item in payload["results"]})

    def test_workbench_archive_manifest_schema_standalone_script_json_skip_output(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATION_SCRIPT_PATH), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=workbench_archive_manifest_schema_script_env({FORCE_JSONSCHEMA_MISSING_ENV: "1"}),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual("docs/json_schema/workbench_archive_manifest_v1.schema.json", payload["schema_path"])
        self.assertIn("optional dependency 'jsonschema' is not installed", payload["reason"])


if __name__ == "__main__":
    unittest.main()

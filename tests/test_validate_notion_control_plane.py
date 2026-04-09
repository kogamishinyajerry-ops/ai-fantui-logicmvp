import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.validate_notion_control_plane import (
    SKIP_REASON,
    validate_control_plane,
    validate_required_keys,
)


def write_temp_config(payload):
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


class ValidateNotionControlPlaneTests(unittest.TestCase):
    def setUp(self):
        self.base_config = {
            "databases": {
                "roadmap": "roadmap-id",
                "tasks": "tasks-id",
                "sessions": "sessions-id",
                "qa": "qa-id",
                "plans": "plans-id",
                "runs": "runs-id",
                "gates": "gates-id",
                "gaps": "gaps-id",
                "decisions": "decisions-id",
                "assets": "assets-id",
            },
            "pages": {
                "constitution": "constitution-id",
                "status": "status-id",
                "control_plane": "control-plane-id",
                "opus_protocol": "opus-protocol-id",
                "opus_brief": "opus-brief-id",
            },
            "urls": {
                "github_repo": "https://github.com/example/repo",
                "github_actions": "https://github.com/example/repo/actions",
            },
            "default_plan": "P3-06 控制面自检",
            "default_review_gate": "OPUS-4.6 周期审查 Gate",
            "legacy_review_artifacts": [
                {"id": "legacy-gate-id", "kind": "gate", "title": "P1 自动化目标审查 Gate", "reason": "Superseded by the current default gate."},
                {"id": "legacy-plan-id", "kind": "plan", "title": "P1-02 消除手动浏览器 QA 依赖", "reason": "Superseded by the current review contract."},
            ],
        }

    def tearDown(self):
        for path in getattr(self, "_temp_paths", []):
            if path.exists():
                path.unlink()

    def save(self, payload):
        path = write_temp_config(payload)
        self._temp_paths = getattr(self, "_temp_paths", [])
        self._temp_paths.append(path)
        return path

    def test_validate_required_keys_flags_missing_entries(self):
        payload = dict(self.base_config)
        payload["databases"] = dict(self.base_config["databases"])
        payload["databases"].pop("qa")

        errors = validate_required_keys(payload)

        self.assertIn("missing databases.qa", errors)

    def test_validate_control_plane_skips_without_token(self):
        path = self.save(self.base_config)
        old_env = dict(os.environ)
        try:
            os.environ.pop("NOTION_API_KEY", None)
            exit_code, report, text_lines = validate_control_plane(config_path=path)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        self.assertEqual("skip", report["status"])
        self.assertEqual(SKIP_REASON, report["reason"])
        self.assertIn(SKIP_REASON, text_lines)

    def test_validate_control_plane_passes_when_pages_and_databases_are_accessible(self):
        path = self.save(self.base_config)
        seen = []

        def fake_request(token, path):
            seen.append((token, path))
            return {"id": path.rsplit("/", 1)[-1]}

        old_env = dict(os.environ)
        try:
            os.environ["NOTION_API_KEY"] = "test-token"
            exit_code, report, text_lines = validate_control_plane(
                config_path=path,
                request_get=fake_request,
            )
        finally:
            os.environ.clear()
            os.environ.update(old_env)

        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(5, report["checked_pages"])
        self.assertEqual(10, report["checked_databases"])
        self.assertEqual(2, report["checked_legacy_artifacts"])
        self.assertEqual(17, len(seen))
        self.assertIn("PASS: validated 5 pages, 10 databases, and 2 legacy artifacts", text_lines[0])


if __name__ == "__main__":
    unittest.main()

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Optional

from tools import linear_live_issue_factory as factory


PROJECT_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = PROJECT_ROOT / "tools" / "linear_live_issue_factory.py"


def sample_spec() -> factory.LiveIssueSpec:
    return factory.LiveIssueSpec(
        title="[project] [L9] [none] [DAL-TBD] Example live issue",
        repository="/tmp/repo-anchor",
        outcome="Create a bounded live issue from the repo-local template.",
        acceptance=("Dry-run output includes required AWCP sections.",),
        boundaries=("Do not mutate controller truth.",),
        evidence_required=("Factory dry-run output.",),
        repo_local_label="JER-233",
        context=("Repository is code truth.",),
    )


class LinearLiveIssueFactoryTests(unittest.TestCase):
    def test_issue_description_contains_awcp_sections_and_collision_guard(self) -> None:
        description = factory.issue_description(sample_spec())

        for heading in (
            "## Outcome",
            "## Acceptance",
            "## Boundaries",
            "## Evidence Required",
            "## Metadata",
            "## Identifier Collision Guard",
        ):
            self.assertIn(heading, description)
        self.assertIn("- Repository: /tmp/repo-anchor", description)
        self.assertIn("- Desired state: Queued", description)
        self.assertIn("- Agent eligible: Yes", description)
        self.assertIn("live Linear <identifier>", description)
        self.assertIn("repo-local historical `JER-233`", description)

    def test_missing_required_fields_are_rejected(self) -> None:
        spec = factory.LiveIssueSpec(
            title="",
            repository="/tmp/repo-anchor",
            outcome="",
            acceptance=(),
            boundaries=(),
            evidence_required=(),
        )

        with self.assertRaises(factory.IssueFactoryError) as ctx:
            factory.validate_spec(spec)

        message = str(ctx.exception)
        self.assertIn("title", message)
        self.assertIn("outcome", message)
        self.assertIn("acceptance", message)
        self.assertIn("boundaries", message)
        self.assertIn("evidence_required", message)

    def test_dry_run_payload_requires_confirm_and_never_requires_credentials(self) -> None:
        payload = factory.dry_run_payload(sample_spec(), team_key="JER", project_name="Demo Project")

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["write_requires_confirm"])
        self.assertEqual("environment", payload["credential_source"])
        self.assertFalse(payload["helper_contract"]["state_transitions"])
        self.assertFalse(payload["helper_contract"]["secret_persistence"])

    def test_cli_dry_run_outputs_json_without_linear_env(self) -> None:
        env = dict(os.environ)
        for key in ("LINEAR_API_KEY", "LINEAR_OAUTH_TOKEN", "LINEAR_TOKEN"):
            env.pop(key, None)

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--title",
                "[project] [L9] [none] [DAL-TBD] Example live issue",
                "--repository",
                "/tmp/repo-anchor",
                "--outcome",
                "Create a bounded live issue from the repo-local template.",
                "--acceptance",
                "Dry-run output includes required AWCP sections.",
                "--boundary",
                "Do not mutate controller truth.",
                "--evidence-required",
                "Factory dry-run output.",
                "--repo-local-label",
                "JER-233",
            ],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertIn("Identifier Collision Guard", payload["description"])

    def test_confirm_write_uses_issue_create_only(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("issueCreate", source)
        self.assertNotIn("issueUpdate", source)
        self.assertNotIn("stateId", source)
        self.assertNotIn("commentCreate", source)

    def test_create_live_issue_uses_context_lookup_and_create_mutation(self) -> None:
        calls: list[tuple[str, Optional[dict[str, Any]]]] = []

        def fake_graphql(query: str, variables: Optional[dict[str, Any]]) -> dict[str, Any]:
            calls.append((query, variables))
            if "LiveIssueFactoryContext" in query:
                return {
                    "teams": {
                        "nodes": [
                            {
                                "id": "team-id",
                                "key": "JER",
                                "name": "JerryKogami",
                                "projects": {
                                    "nodes": [
                                        {"id": "project-id", "name": "Demo Project", "state": "backlog", "url": "x"}
                                    ]
                                },
                            }
                        ]
                    }
                }
            return {
                "issueCreate": {
                    "success": True,
                    "issue": {"id": "issue-id", "identifier": "JER-999", "title": sample_spec().title, "url": "x"},
                }
            }

        payload = factory.create_live_issue(
            sample_spec(),
            team_key="JER",
            project_name="Demo Project",
            graphql=fake_graphql,
        )

        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual("JER-999", payload["issue"]["identifier"])
        create_variables = calls[-1][1]
        self.assertIsNotNone(create_variables)
        assert create_variables is not None
        self.assertEqual("team-id", create_variables["input"]["teamId"])
        self.assertEqual("project-id", create_variables["input"]["projectId"])
        self.assertIn("repo-local historical `JER-233`", create_variables["input"]["description"])


if __name__ == "__main__":
    unittest.main()

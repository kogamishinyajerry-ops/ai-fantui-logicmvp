import unittest

from tools.run_gsd_validation_suite import (
    DEFAULT_PYTHON_COMMAND,
    ValidationCommand,
    build_child_env,
    build_default_commands,
    run_suite,
)


class CompletedProcessStub:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ValidationSuiteTests(unittest.TestCase):
    def test_build_default_commands_uses_stable_python3_label_by_default(self):
        commands = build_default_commands()

        self.assertTrue(commands)
        self.assertEqual(DEFAULT_PYTHON_COMMAND, commands[0].argv[0])

    def test_build_default_commands_contains_expected_checks(self):
        commands = build_default_commands("/usr/bin/python3")

        self.assertEqual(
            [
                "unit_tests",
                "debug_json_schema",
                "demo_answer_schema",
                "validation_report_schema",
                "validation_schema_runner_report_schema",
                "validation_schema_checker_report_schema",
                "notion_control_plane",
            ],
            [command.name for command in commands],
        )
        self.assertEqual("/usr/bin/python3", commands[0].argv[0])

    def test_build_child_env_prepends_repo_src_to_pythonpath(self):
        env = build_child_env({"PYTHONPATH": "custom/path"})

        self.assertTrue(env["PYTHONPATH"].endswith("custom/path"))
        self.assertIn("/src", env["PYTHONPATH"])

    def test_run_suite_stops_after_first_failure(self):
        seen = []
        responses = iter(
            [
                CompletedProcessStub(0, stdout="unit ok"),
                CompletedProcessStub(1, stderr="schema failed"),
                CompletedProcessStub(0, stdout="should not run"),
            ]
        )

        def fake_runner(argv, **kwargs):
            seen.append(argv)
            return next(responses)

        report = run_suite(
            (
                ValidationCommand("unit_tests", ("python3", "-m", "unittest")),
                ValidationCommand("debug_json_schema", ("python3", "tools/validate_debug_json_schema.py")),
                ValidationCommand("demo_answer_schema", ("python3", "tools/validate_demo_answer_schema.py")),
            ),
            runner=fake_runner,
            base_env={},
        )

        self.assertEqual("fail", report["status"])
        self.assertEqual("debug_json_schema", report["failed_check"])
        self.assertEqual(2, report["completed_commands"])
        self.assertEqual(2, len(seen))

    def test_run_suite_reports_success_when_all_checks_pass(self):
        def fake_runner(argv, **kwargs):
            return CompletedProcessStub(0, stdout="ok")

        report = run_suite(
            (
                ValidationCommand("unit_tests", ("python3", "-m", "unittest")),
                ValidationCommand("debug_json_schema", ("python3", "tools/validate_debug_json_schema.py")),
            ),
            runner=fake_runner,
            base_env={},
        )

        self.assertEqual("pass", report["status"])
        self.assertIsNone(report["failed_check"])
        self.assertEqual(2, report["completed_commands"])
        self.assertEqual(["pass", "pass"], [result["status"] for result in report["results"]])


if __name__ == "__main__":
    unittest.main()

import subprocess
import unittest

from tools.run_gsd_validation_suite import (
    DEFAULT_PYTHON_COMMAND,
    DEFAULT_TIMEOUT_SECONDS,
    ValidationCommand,
    build_child_env,
    build_default_commands,
    run_suite,
    select_commands,
    split_check_names,
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
                "generator_adapter_parity",
                "debug_json_schema",
                "demo_path_smoke",
                # system_switcher_smoke: Playwright E2E test — requires localhost:7891 server, run in E2E CI only
                "demo_answer_schema",
                "second_system_smoke",
                "second_system_smoke_schema",
                "fault_taxonomy_schema",
                "control_system_spec_schema",
                "controller_truth_adapter_metadata_schema",
                "landing_gear_adapter",
                "landing_gear_playback",
                "landing_gear_diagnosis",
                "landing_gear_knowledge",
                "two_system_runtime_comparison",
                "playback_trace_schema",
                "fault_diagnosis_schema",
                "knowledge_artifact_schema",
                "workbench_bundle_schema",
                "workbench_archive_manifest_schema",
                "workbench_changerequest_handoff_schema",
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
        self.assertEqual("exit_code", report["failure_kind"])
        self.assertEqual("exit_code", report["results"][1]["failure_kind"])
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
        self.assertEqual(DEFAULT_TIMEOUT_SECONDS, report["timeout_seconds"])
        self.assertFalse(report["results"][0]["timed_out"])

    def test_run_suite_passes_timeout_to_child_runner(self):
        seen_timeouts = []

        def fake_runner(argv, **kwargs):
            seen_timeouts.append(kwargs["timeout"])
            return CompletedProcessStub(0, stdout="ok")

        report = run_suite(
            (ValidationCommand("unit_tests", ("python3", "-m", "unittest")),),
            runner=fake_runner,
            base_env={},
            timeout_seconds=12.5,
        )

        self.assertEqual("pass", report["status"])
        self.assertEqual([12.5], seen_timeouts)

    def test_run_suite_reports_timeout_instead_of_hanging_forever(self):
        def fake_runner(argv, **kwargs):
            raise subprocess.TimeoutExpired(
                cmd=argv,
                timeout=kwargs["timeout"],
                output="partial stdout",
                stderr="partial stderr",
            )

        report = run_suite(
            (
                ValidationCommand("unit_tests", ("python3", "-m", "pytest")),
                ValidationCommand("debug_json_schema", ("python3", "tools/validate_debug_json_schema.py")),
            ),
            runner=fake_runner,
            base_env={},
            timeout_seconds=0.25,
        )

        self.assertEqual("fail", report["status"])
        self.assertEqual("timeout", report["failure_kind"])
        self.assertEqual("unit_tests", report["failed_check"])
        self.assertEqual(1, report["completed_commands"])
        timeout_result = report["results"][0]
        self.assertTrue(timeout_result["timed_out"])
        self.assertEqual("timeout", timeout_result["failure_kind"])
        self.assertEqual(0.25, timeout_result["timeout_seconds"])
        self.assertIsNone(timeout_result["returncode"])
        self.assertEqual("partial stdout", timeout_result["stdout"])
        self.assertEqual("partial stderr", timeout_result["stderr"])

    def test_run_suite_can_continue_after_failure_for_isolation(self):
        responses = iter(
            [
                CompletedProcessStub(1, stderr="unit failed"),
                CompletedProcessStub(0, stdout="schema ok"),
            ]
        )

        def fake_runner(argv, **kwargs):
            return next(responses)

        report = run_suite(
            (
                ValidationCommand("unit_tests", ("python3", "-m", "pytest")),
                ValidationCommand("debug_json_schema", ("python3", "tools/validate_debug_json_schema.py")),
            ),
            runner=fake_runner,
            base_env={},
            continue_on_failure=True,
        )

        self.assertEqual("fail", report["status"])
        self.assertEqual("unit_tests", report["failed_check"])
        self.assertEqual(2, report["completed_commands"])
        self.assertEqual(["fail", "pass"], [result["status"] for result in report["results"]])

    def test_split_check_names_accepts_repeated_and_comma_separated_values(self):
        self.assertEqual(
            ("unit_tests", "debug_json_schema", "demo_path_smoke"),
            split_check_names(["unit_tests, debug_json_schema", "demo_path_smoke"]),
        )

    def test_select_commands_filters_only_and_skip(self):
        commands = (
            ValidationCommand("unit_tests", ("python3", "-m", "pytest")),
            ValidationCommand("debug_json_schema", ("python3", "tools/validate_debug_json_schema.py")),
            ValidationCommand("demo_path_smoke", ("python3", "tools/demo_path_smoke.py")),
        )

        selected = select_commands(commands, only=("unit_tests", "demo_path_smoke"), skip=("unit_tests",))

        self.assertEqual(["demo_path_smoke"], [command.name for command in selected])

    def test_select_commands_rejects_unknown_checks(self):
        with self.assertRaisesRegex(ValueError, "unknown validation check"):
            select_commands(
                (ValidationCommand("unit_tests", ("python3", "-m", "pytest")),),
                only=("missing_check",),
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from tools.run_mypy_gate import (
    build_child_env,
    build_mypy_gate_command,
    main,
    run_mypy_gate,
    summarize_mypy_output,
)


def test_official_mypy_gate_command_is_full_repo_strict() -> None:
    command = build_mypy_gate_command("python-test")

    assert command.name == "mypy_strict_full_repo"
    assert command.argv == (
        "python-test",
        "-m",
        "mypy",
        "--strict",
        "--explicit-package-bases",
        "src",
        "tests",
        "tools",
    )


def test_child_env_sets_src_and_repo_root_pythonpath() -> None:
    env = build_child_env({"PYTHONPATH": "existing"})

    assert env["PYTHONPATH"].endswith(":existing")
    assert "/src:" in env["PYTHONPATH"]


def test_mypy_success_report_is_not_a_known_blocker() -> None:
    def runner(*args: Any, **kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            returncode=0,
            stdout="Success: no issues found in 377 source files\n",
            stderr="",
        )

    report = run_mypy_gate(python_executable="python-test", runner=runner)

    assert report["status"] == "pass"
    assert report["known_baseline_blocker"] is False
    assert report["summary"]["success"] is True
    assert report["summary"]["checked_source_files"] == 377
    assert report["truth_level_impact"] == "none"
    assert report["red_lines_touched"] == []


def test_mypy_failure_report_captures_current_baseline_blocker() -> None:
    stdout = "\n".join(
        [
            "tests/test_example.py:1: error: Function is missing a return type annotation  [no-untyped-def]",
            "Found 4692 errors in 322 files (checked 377 source files)",
        ]
    )

    def runner(*args: Any, **kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=1, stdout=stdout, stderr="")

    report = run_mypy_gate(python_executable="python-test", runner=runner)

    assert report["status"] == "blocked"
    assert report["known_baseline_blocker"] is True
    assert report["baseline_issue"] == "JER-148"
    assert report["current_issue"] == "JER-171"
    assert report["summary"]["error_count"] == 4692
    assert report["summary"]["error_file_count"] == 322
    assert report["summary"]["checked_source_files"] == 377
    assert report["summary"]["no_untyped_def"] is True


def test_summarize_mypy_output_marks_import_categories() -> None:
    summary = summarize_mypy_output(
        'pkg.py:1: error: Library stubs not installed for "jsonschema"  [import-untyped]\n',
        "Found 2 errors in 1 file (checked 4 source files)",
    )

    assert summary["missing_stubs"] is True
    assert summary["import_untyped"] is True
    assert summary["error_count"] == 2


def test_report_only_main_returns_zero_for_blocked_report(capsys: Any) -> None:
    def runner(*args: Any, **kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            returncode=1,
            stdout="Found 4692 errors in 322 files (checked 377 source files)",
            stderr="",
        )

    exit_code = main(["--format", "json", "--report-only", "--python", "python-test"], runner=runner)

    assert exit_code == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "blocked"
    assert report["command"] == "python-test -m mypy --strict --explicit-package-bases src tests tools"

"""P48-03 — pytest subprocess runner + output parser.

Two layers tested:
  1. parse_pytest_output (pure function — exercise it on canned
     pytest output strings)
  2. run_tests (subprocess — exercise on a tmp_path mini-repo
     containing 1 passing + 1 failing test)
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from well_harness.skill_executor.test_runner import (
    TestRunnerError,
    parse_pytest_output,
    run_tests,
)


# ─── 1. parse_pytest_output: success cases ─────────────────────────────


def test_parse_all_pass():
    out = dedent("""
        tests/test_foo.py ...                                                    [100%]

        ============================== 5 passed in 0.12s ==============================
    """)
    result = parse_pytest_output(stdout=out, return_code=0)
    assert result.passed == 5
    assert result.failed == 0
    assert result.errors == 0
    assert result.failed_test_ids == []


def test_parse_partial_failure():
    out = dedent("""
        tests/test_foo.py ..F                                                    [100%]
        =================================== FAILURES ===================================
        FAILED tests/test_foo.py::test_bar - assert 0 == 1
        ========================== 1 failed, 2 passed in 0.50s ==========================
    """)
    result = parse_pytest_output(stdout=out, return_code=1)
    assert result.passed == 2
    assert result.failed == 1
    assert result.failed_test_ids == ["tests/test_foo.py::test_bar"]


def test_parse_skipped_present():
    out = dedent("""
        tests/test_foo.py ..s.                                                   [100%]
        ===================== 3 passed, 1 skipped in 0.20s =====================
    """)
    result = parse_pytest_output(stdout=out, return_code=0)
    assert result.passed == 3
    assert result.skipped == 1


def test_parse_multiple_failures_collected():
    out = dedent("""
        tests/x.py FFF                                                           [100%]
        =================================== FAILURES ===================================
        FAILED tests/x.py::test_one - assert False
        FAILED tests/x.py::test_two - KeyError: 'foo'
        FAILED tests/x.py::test_three - TimeoutError
        ============================ 3 failed in 1.00s =============================
    """)
    result = parse_pytest_output(stdout=out, return_code=1)
    assert result.passed == 0
    assert result.failed == 3
    assert sorted(result.failed_test_ids) == [
        "tests/x.py::test_one",
        "tests/x.py::test_three",
        "tests/x.py::test_two",
    ]


def test_parse_error_lines_join_failed_ids():
    """Pytest emits ERROR lines for collection or fixture errors —
    these belong in the same failed_test_ids list so the gate's
    'no new failures' check covers both."""
    out = dedent("""
        ERROR tests/broken_import.py - ModuleNotFoundError: x
        FAILED tests/test_foo.py::test_bar - assert 0
        ============================ 1 failed, 1 error in 0.50s =====================
    """)
    result = parse_pytest_output(stdout=out, return_code=1)
    assert result.failed == 1
    assert result.errors == 1
    assert "tests/broken_import.py" in result.failed_test_ids
    assert "tests/test_foo.py::test_bar" in result.failed_test_ids


# ─── 2. parse_pytest_output: edge cases ────────────────────────────────


def test_parse_empty_output_treated_as_runner_error_when_nonzero():
    """No summary line + nonzero exit → errors=1 + zeros elsewhere.
    Caller (the gate) sees this as a runner failure."""
    result = parse_pytest_output(stdout="", return_code=2)
    assert result.errors == 1
    assert result.passed == 0
    assert result.failed == 0


def test_parse_empty_output_zero_exit_treated_as_no_tests():
    result = parse_pytest_output(stdout="", return_code=0)
    assert result.errors == 0
    assert result.passed == 0
    assert result.failed == 0


def test_parse_dedup_failed_test_ids():
    """If pytest emits the same FAILED line twice (rare but
    possible with rerun plugins), we de-dup."""
    out = dedent("""
        FAILED tests/x.py::test_a
        FAILED tests/x.py::test_a
        ============================ 1 failed in 0.50s =============================
    """)
    result = parse_pytest_output(stdout=out, return_code=1)
    assert result.failed_test_ids == ["tests/x.py::test_a"]


def test_parse_ignores_summary_lookalikes_in_log():
    """If a logged docstring contains '5 passed in 0.1s' or
    similar, the parser must still pick the actual final summary.
    Walk-from-bottom strategy handles this."""
    out = dedent("""
        tests/test_x.py: docstring says "10 passed in 1.0s" — should be ignored
        tests/test_x.py ...                                                      [100%]
        ============================ 3 passed in 0.50s =============================
    """)
    result = parse_pytest_output(stdout=out, return_code=0)
    # The real summary at the bottom — 3 passed, not 10.
    assert result.passed == 3


# ─── 3. run_tests: real subprocess ─────────────────────────────────────


@pytest.fixture
def mini_repo(tmp_path):
    """Tiny repo with src/ + tests/ — enough for pytest to run."""
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "math_lib.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_pass.py").write_text(
        "from pkg.math_lib import add\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_fail.py").write_text(
        "from pkg.math_lib import add\n"
        "def test_broken():\n"
        "    assert add(2, 3) == 999\n",
        encoding="utf-8",
    )
    return tmp_path


def test_run_tests_picks_up_pass_and_fail(mini_repo):
    """Real pytest run on a 1-pass/1-fail mini repo. End-to-end
    smoke that the subprocess + parser combo works."""
    result = run_tests(repo_root=mini_repo)
    assert result.passed == 1
    assert result.failed == 1
    assert "tests/test_fail.py::test_broken" in result.failed_test_ids


def test_run_tests_all_pass_when_only_pass_test(mini_repo):
    # Delete the failing test
    (mini_repo / "tests" / "test_fail.py").unlink()
    result = run_tests(repo_root=mini_repo)
    assert result.passed == 1
    assert result.failed == 0
    assert result.failed_test_ids == []


def test_run_tests_raises_on_missing_repo_root(tmp_path):
    bogus = tmp_path / "does_not_exist"
    with pytest.raises(TestRunnerError):
        run_tests(repo_root=bogus)


def test_run_tests_records_duration_and_started_at(mini_repo):
    result = run_tests(repo_root=mini_repo)
    assert result.duration_sec > 0
    assert result.ran_at.endswith("Z")


def test_run_tests_sets_pythonpath_for_src_layout(mini_repo):
    """The runner exports src/ onto PYTHONPATH so tests can
    `from pkg.math_lib import add` without a setup.py. Verify by
    confirming the test import worked (pass test passed)."""
    result = run_tests(repo_root=mini_repo)
    # If PYTHONPATH wasn't set, the import would have failed →
    # we'd see an ERROR, not a pass.
    assert result.passed >= 1
    assert result.errors == 0

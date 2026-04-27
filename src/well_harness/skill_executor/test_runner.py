"""Subprocess pytest runner — produces a typed TestResult.

Why subprocess and not the pytest-as-library API: process isolation.
A test that mutates global state (e.g. `os.environ`) inside our
test session shouldn't taint the executor's own state. Subprocess
also matches what the engineer would run from a terminal
(`make test`), so the comparison is apples-to-apples.

The runner parses pytest's standard summary lines:

    `1448 passed in 132.41s`              — full pass
    `1 failed, 1447 passed in 132.41s`    — partial fail (order may vary)
    `FAILED tests/foo.py::test_bar - ...` — one line per failure

Both summary and per-failure lines are scraped. If the summary is
missing (pytest crashed during collection), TestResult.errors is
incremented and the raw stderr/stdout is captured for the audit.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.models import TestResult


_SUMMARY_PATTERN = re.compile(
    r"(?P<word>\d+)\s+(?P<status>passed|failed|skipped|errors|error)",
    re.IGNORECASE,
)
_FAILED_TEST_LINE = re.compile(r"^FAILED\s+(\S+)")
# Pytest also emits ERROR (usually for collection or fixture errors)
_ERROR_TEST_LINE = re.compile(r"^ERROR\s+(\S+)")
_DURATION_PATTERN = re.compile(r"in\s+([\d.]+)s")


class TestRunnerError(SkillExecutorError):
    """The pytest invocation itself failed in a way that isn't
    "tests failed" — e.g. python wasn't found, the workdir didn't
    exist, etc. Distinct from "tests ran and some failed", which
    is a normal TestResult."""

    # Tell pytest this is NOT a test class (the name starts with
    # "Test" so it gets auto-collected and warned-on otherwise).
    __test__ = False


def run_tests(
    *,
    repo_root: Path,
    test_paths: list[str] | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: float = 600.0,
    python_executable: str | None = None,
) -> TestResult:
    """Run pytest under `repo_root` and return a typed TestResult.

    `test_paths` defaults to ["tests/"]. `extra_args` is appended
    to the command line — useful for `-x` or `-k` during smoke
    debugging.

    `python_executable` defaults to the current process's Python.
    Tests can override to point at a venv-specific binary.

    `timeout_sec` defaults to 10 minutes; raises TestRunnerError
    on timeout (but does NOT raise on test failures — those go
    into TestResult.failed).
    """
    if not isinstance(repo_root, Path):
        repo_root = Path(repo_root)
    repo_root = repo_root.resolve()
    if not repo_root.is_dir():
        raise TestRunnerError(f"repo_root does not exist: {repo_root}")

    py_exec = python_executable or _resolve_python()
    cmd: list[str] = [py_exec, "-m", "pytest"]
    cmd.extend(test_paths or ["tests/"])
    # Default flags: terse output (-q), short tracebacks (--tb=line)
    # so failures show one line each, easy to parse.
    if extra_args is None:
        extra_args = ["-q", "--tb=line"]
    cmd.extend(extra_args)

    env = os.environ.copy()
    # Make sure pytest finds the package without requiring the
    # caller to set PYTHONPATH manually.
    src_dir = repo_root / "src"
    if src_dir.is_dir():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            str(src_dir) + (os.pathsep + existing if existing else "")
        )

    started_perf = time.monotonic()
    started_iso = _now_iso()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        raise TestRunnerError(
            f"pytest timed out after {timeout_sec}s"
        ) from exc
    except FileNotFoundError as exc:
        raise TestRunnerError(
            f"python executable not found: {py_exec}: {exc}"
        ) from exc
    finished_perf = time.monotonic()

    return parse_pytest_output(
        stdout=proc.stdout,
        stderr=proc.stderr,
        return_code=proc.returncode,
        started_at=started_iso,
        duration_sec=finished_perf - started_perf,
    )


def parse_pytest_output(
    *,
    stdout: str,
    stderr: str = "",
    return_code: int = 0,
    started_at: str = "",
    duration_sec: float = 0.0,
) -> TestResult:
    """Pull a TestResult out of pytest's text output.

    Robust to:
      - successful runs ("1448 passed in 132.41s")
      - partial fail ("1 failed, 1447 passed in 132.41s")
      - skipped ("3 passed, 2 skipped in 0.5s")
      - all-fail ("3 failed in 1.0s")
      - collection-error / pytest crash (no summary line at all —
        we fall back to errors=1 + return_code)

    Failed-test ids are pulled from the "FAILED ..." lines pytest
    emits at the end of the run. For -q output these always show
    up before the summary. Subprocess timeout / crash is handled
    by the caller (run_tests raises TestRunnerError); this parser
    assumes a complete-or-partial pytest output.
    """
    summary_counts = _parse_summary(stdout)
    failed_ids = _parse_failed_ids(stdout)

    # If the summary line wasn't found AND return code is non-zero,
    # treat as runner error rather than "0 passed". We surface that
    # via TestResult.errors so the gate can refuse without crashing.
    if not summary_counts and return_code != 0:
        return TestResult(
            passed=0,
            failed=0,
            skipped=0,
            errors=1,
            duration_sec=duration_sec,
            ran_at=started_at,
            failed_test_ids=[],
        )
    if not summary_counts and return_code == 0:
        # Empty test set — pytest exits 5 if no tests collected,
        # 0 if it found them but parsing missed (edge case).
        return TestResult(
            passed=0,
            failed=0,
            ran_at=started_at,
            duration_sec=duration_sec,
        )

    return TestResult(
        passed=summary_counts.get("passed", 0),
        failed=summary_counts.get("failed", 0),
        skipped=summary_counts.get("skipped", 0),
        errors=summary_counts.get("errors", 0) + summary_counts.get("error", 0),
        duration_sec=duration_sec,
        ran_at=started_at,
        failed_test_ids=failed_ids,
    )


def _parse_summary(stdout: str) -> dict[str, int]:
    """Find the last summary line (pytest can print multiple
    summary-looking lines during -q output; the actual one is at
    the bottom). Returns dict like {'passed': 5, 'failed': 1}."""
    lines = stdout.splitlines()
    # Walk lines from the bottom; the last line containing
    # "passed", "failed", or "error" + "in Xs" is the summary.
    for line in reversed(lines):
        if not _DURATION_PATTERN.search(line):
            continue
        if not _SUMMARY_PATTERN.search(line):
            continue
        counts: dict[str, int] = {}
        for m in _SUMMARY_PATTERN.finditer(line):
            status = m.group("status").lower()
            # Normalize "errors" / "error" → both go to errors
            if status == "error":
                status = "errors"
            counts[status] = int(m.group("word"))
        if counts:
            return counts
    return {}


def _parse_failed_ids(stdout: str) -> list[str]:
    """Pull `FAILED tests/x.py::test_y - ...` and `ERROR ...`
    lines pytest emits before the summary. De-duplicate but
    preserve order."""
    seen = set()
    out: list[str] = []
    for line in stdout.splitlines():
        m = _FAILED_TEST_LINE.match(line)
        if not m:
            m = _ERROR_TEST_LINE.match(line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(m.group(1))
    return out


def _resolve_python() -> str:
    """Return a python interpreter path. Prefer the one running
    this process (matches the user's environment); fall back to
    `python3` on PATH."""
    import sys
    if sys.executable:
        return sys.executable
    found = shutil.which("python3")
    if found:
        return found
    raise TestRunnerError("no python interpreter found")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

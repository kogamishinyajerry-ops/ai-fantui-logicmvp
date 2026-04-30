from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FORMATS = {"text", "json"}
DEFAULT_PYTHON_COMMAND = "python3"
MYPY_SCOPES = ("src", "tests", "tools")
BASELINE_ISSUE = "JER-148"
CURRENT_GATE_ISSUE = "JER-171"


@dataclass(frozen=True)
class MypyGateCommand:
    name: str
    argv: tuple[str, ...]


def clip_tail(text: str, limit: int = 8000) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"... [head truncated, last {limit} chars below]\n{stripped[-limit:]}"


def command_to_text(command: MypyGateCommand) -> str:
    return " ".join(command.argv)


def build_mypy_gate_command(python_executable: str | None = None) -> MypyGateCommand:
    python = python_executable or DEFAULT_PYTHON_COMMAND
    return MypyGateCommand(
        "mypy_strict_full_repo",
        (
            python,
            "-m",
            "mypy",
            "--strict",
            "--explicit-package-bases",
            *MYPY_SCOPES,
        ),
    )


def build_child_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    pythonpath_entries = [str(PROJECT_ROOT / "src"), str(PROJECT_ROOT)]
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath_entries.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
    return env


def summarize_mypy_output(stdout: str, stderr: str) -> dict[str, Any]:
    combined = "\n".join(part for part in (stdout, stderr) if part)
    summary: dict[str, Any] = {
        "error_count": None,
        "error_file_count": None,
        "checked_source_files": None,
        "success": "Success: no issues found" in combined,
        "missing_stubs": "Library stubs not installed" in combined,
        "duplicate_module": "Duplicate module named" in combined,
        "import_untyped": "[import-untyped]" in combined,
        "no_untyped_def": "[no-untyped-def]" in combined,
    }

    found_match = re.search(
        r"Found (?P<errors>\d+) errors? in (?P<files>\d+) files? \(checked (?P<checked>\d+) source files?\)",
        combined,
    )
    if found_match:
        summary["error_count"] = int(found_match.group("errors"))
        summary["error_file_count"] = int(found_match.group("files"))
        summary["checked_source_files"] = int(found_match.group("checked"))
        return summary

    success_match = re.search(r"Success: no issues found in (?P<checked>\d+) source files?", combined)
    if success_match:
        summary["checked_source_files"] = int(success_match.group("checked"))
    return summary


def result_payload(command: MypyGateCommand, completed: Any) -> dict[str, Any]:
    status = "pass" if completed.returncode == 0 else "blocked"
    return {
        "kind": "well-harness-mypy-gate-report",
        "version": 1,
        "status": status,
        "gate": command.name,
        "command": command_to_text(command),
        "env": {
            "PYTHONPATH": "src:.",
        },
        "returncode": completed.returncode,
        "known_baseline_blocker": completed.returncode != 0,
        "baseline_issue": BASELINE_ISSUE if completed.returncode != 0 else None,
        "current_issue": CURRENT_GATE_ISSUE,
        "summary": summarize_mypy_output(completed.stdout, completed.stderr),
        "stdout_tail": clip_tail(completed.stdout),
        "stderr_tail": clip_tail(completed.stderr),
        "truth_level_impact": "none",
        "red_lines_touched": [],
    }


def run_mypy_gate(
    *,
    python_executable: str | None = None,
    runner: Callable[..., Any] = subprocess.run,
    base_env: dict[str, str] | None = None,
    cwd: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    command = build_mypy_gate_command(python_executable)
    completed = runner(
        command.argv,
        cwd=cwd,
        env=build_child_env(base_env),
        capture_output=True,
        text=True,
        check=False,
    )
    return result_payload(command, completed)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the official Codex Daily Lane mypy strict gate.",
    )
    parser.add_argument("--format", choices=sorted(OUTPUT_FORMATS), default="text")
    parser.add_argument(
        "--python",
        default=DEFAULT_PYTHON_COMMAND,
        help="Python executable used to run `-m mypy`.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Emit the blocked/pass report but exit 0 when mypy is currently blocked.",
    )
    return parser.parse_args(list(argv))


def emit_text_report(report: dict[str, Any]) -> None:
    prefix = "PASS" if report["status"] == "pass" else "BLOCKED"
    print(f"{prefix} {report['gate']} ({report['command']})")
    print(f"returncode: {report['returncode']}")
    summary = report["summary"]
    if summary.get("error_count") is not None:
        print(
            "summary: "
            f"{summary['error_count']} errors in {summary['error_file_count']} files "
            f"(checked {summary['checked_source_files']} source files)"
        )
    elif summary.get("success"):
        print(f"summary: success in {summary.get('checked_source_files')} source files")
    if report["status"] != "pass":
        print(f"known_baseline_blocker: {report['known_baseline_blocker']} ({report['baseline_issue']})")


def emit_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    emit_text_report(report)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = run_mypy_gate(python_executable=args.python, runner=runner)
    emit_report(report, args.format)
    if report["status"] == "pass" or args.report_only:
        return 0
    return int(report["returncode"]) or 1


if __name__ == "__main__":
    raise SystemExit(main())

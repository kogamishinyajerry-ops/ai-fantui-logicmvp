from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FORMATS = {"text", "json"}


@dataclass(frozen=True)
class ValidationCommand:
    name: str
    argv: tuple[str, ...]


def clip(text: str, limit: int = 400) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 15]}... [truncated]"


def build_default_commands(python_executable: str | None = None) -> tuple[ValidationCommand, ...]:
    python = python_executable or sys.executable
    return (
        ValidationCommand(
            "unit_tests",
            (python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"),
        ),
        ValidationCommand(
            "debug_json_schema",
            (python, "tools/validate_debug_json_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "demo_answer_schema",
            (python, "tools/validate_demo_answer_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "validation_report_schema",
            (python, "tools/validate_validation_report_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "validation_schema_runner_report_schema",
            (python, "tools/validate_validation_schema_runner_report_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "validation_schema_checker_report_schema",
            (python, "tools/validate_validation_schema_checker_report_schema.py", "--format", "json"),
        ),
    )


def build_child_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
    return env


def command_to_text(command: ValidationCommand) -> str:
    return " ".join(command.argv)


def result_payload(command: ValidationCommand, completed: Any) -> dict[str, Any]:
    return {
        "name": command.name,
        "command": command_to_text(command),
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "stdout": clip(completed.stdout),
        "stderr": clip(completed.stderr),
    }


def run_suite(
    commands: Sequence[ValidationCommand],
    *,
    runner: Callable[..., Any] = subprocess.run,
    base_env: dict[str, str] | None = None,
    cwd: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failed_check: str | None = None
    child_env = build_child_env(base_env)

    for command in commands:
        completed = runner(
            command.argv,
            cwd=cwd,
            env=child_env,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = result_payload(command, completed)
        results.append(payload)
        if completed.returncode != 0:
            failed_check = command.name
            break

    status = "pass" if failed_check is None else "fail"
    return {
        "status": status,
        "command_count": len(commands),
        "completed_commands": len(results),
        "failed_check": failed_check,
        "results": results,
    }


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: run_gsd_validation_suite.py [--format text|json]")


def emit_text_report(report: dict[str, Any]) -> None:
    for result in report["results"]:
        prefix = "OK" if result["status"] == "pass" else "FAIL"
        print(f"{prefix} {result['name']} ({result['command']})")
        if result["stdout"]:
            print(f"  stdout: {result['stdout']}")
        if result["stderr"]:
            print(f"  stderr: {result['stderr']}")
    if report["status"] == "pass":
        print(f"PASS: {report['completed_commands']} validation commands succeeded.")
    else:
        print(
            "FAIL: stopped after "
            f"{report['completed_commands']} commands; first failed check was {report['failed_check']}."
        )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = run_suite(build_default_commands())
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        emit_text_report(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

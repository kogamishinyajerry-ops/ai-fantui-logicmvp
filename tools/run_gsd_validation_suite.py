from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence, cast


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FORMATS = {"text", "json"}
DEFAULT_PYTHON_COMMAND = "python3"
DEFAULT_TIMEOUT_SECONDS = 420.0


@dataclass(frozen=True)
class ValidationCommand:
    name: str
    argv: tuple[str, ...]
    timeout_seconds: float | None = None


def clip(text: str, limit: int = 400) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 15]}... [truncated]"


def tail(text: str, limit: int = 8000) -> str:
    """Last `limit` chars of `text`. For failures we want the END of
    pytest output (failure summary lives there), not the head — clip()
    gives us the head, which is just dots. P51-00 fix: when a check
    fails, report.tail captures `short test summary info` so the CI
    log actually tells us which test broke."""
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"... [head truncated, last {limit} chars below]\n{stripped[-limit:]}"


def build_default_commands(python_executable: str | None = None) -> tuple[ValidationCommand, ...]:
    python = python_executable or DEFAULT_PYTHON_COMMAND
    return (
        ValidationCommand(
            "unit_tests",
            (python, "-m", "pytest", "tests/", "-q", "--tb=no"),
        ),
        ValidationCommand(
            "generator_adapter_parity",
            (python, "tools/validate_generator_adapter.py", "--format", "json"),
        ),
        ValidationCommand(
            "debug_json_schema",
            (python, "tools/validate_debug_json_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "demo_path_smoke",
            (python, "tools/demo_path_smoke.py", "--format", "json"),
        ),
        # system_switcher_smoke: Playwright E2E test requires localhost:7891 server — run separately in E2E CI, not here
        ValidationCommand(
            "demo_answer_schema",
            (python, "tools/validate_demo_answer_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "second_system_smoke",
            (python, "-m", "well_harness.cli", "second-system-smoke", "--format", "json"),
        ),
        ValidationCommand(
            "second_system_smoke_schema",
            (python, "tools/validate_second_system_smoke_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "fault_taxonomy_schema",
            (python, "tools/validate_fault_taxonomy_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "control_system_spec_schema",
            (python, "tools/validate_control_system_spec_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "controller_truth_adapter_metadata_schema",
            (python, "tools/validate_controller_truth_adapter_metadata_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "landing_gear_adapter",
            (python, "tools/validate_landing_gear_adapter.py", "--format", "json"),
        ),
        ValidationCommand(
            "landing_gear_playback",
            (python, "tools/validate_landing_gear_playback.py", "--format", "json"),
        ),
        ValidationCommand(
            "landing_gear_diagnosis",
            (python, "tools/validate_landing_gear_diagnosis.py", "--format", "json"),
        ),
        ValidationCommand(
            "landing_gear_knowledge",
            (python, "tools/validate_landing_gear_knowledge.py", "--format", "json"),
        ),
        ValidationCommand(
            "two_system_runtime_comparison",
            (python, "tools/validate_two_system_runtime_comparison.py", "--format", "json"),
        ),
        ValidationCommand(
            "playback_trace_schema",
            (python, "tools/validate_playback_trace_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "fault_diagnosis_schema",
            (python, "tools/validate_fault_diagnosis_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "knowledge_artifact_schema",
            (python, "tools/validate_knowledge_artifact_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "workbench_bundle_schema",
            (python, "tools/validate_workbench_bundle_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "workbench_archive_manifest_schema",
            (python, "tools/validate_workbench_archive_manifest_schema.py", "--format", "json"),
        ),
        ValidationCommand(
            "workbench_changerequest_handoff_schema",
            (python, "tools/validate_workbench_changerequest_handoff_schema.py", "--format", "json"),
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
        ValidationCommand(
            "notion_control_plane",
            (python, "tools/validate_notion_control_plane.py", "--format", "json"),
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


def output_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def result_payload(
    command: ValidationCommand,
    completed: Any,
    *,
    timeout_seconds: float | None,
    duration_seconds: float,
) -> dict[str, Any]:
    # P51-00: passes use clip (compact head), failures use tail (last
    # 8KB) so pytest's `short test summary info` block survives into
    # the CI log instead of being hidden behind 400-char truncation.
    failed = completed.returncode != 0
    payload = {
        "name": command.name,
        "command": command_to_text(command),
        "status": "pass" if not failed else "fail",
        "returncode": completed.returncode,
        "stdout": tail(output_to_text(completed.stdout)) if failed else clip(output_to_text(completed.stdout)),
        "stderr": tail(output_to_text(completed.stderr)) if failed else clip(output_to_text(completed.stderr)),
        "timed_out": False,
        "timeout_seconds": timeout_seconds,
        "duration_seconds": round(duration_seconds, 3),
    }
    if failed:
        payload["failure_kind"] = "exit_code"
    return payload


def timeout_payload(
    command: ValidationCommand,
    exc: subprocess.TimeoutExpired,
    *,
    timeout_seconds: float,
    duration_seconds: float,
) -> dict[str, Any]:
    return {
        "name": command.name,
        "command": command_to_text(command),
        "status": "fail",
        "failure_kind": "timeout",
        "returncode": None,
        "stdout": tail(output_to_text(exc.stdout)),
        "stderr": tail(output_to_text(exc.stderr)),
        "timed_out": True,
        "timeout_seconds": timeout_seconds,
        "duration_seconds": round(duration_seconds, 3),
    }


def run_suite(
    commands: Sequence[ValidationCommand],
    *,
    runner: Callable[..., Any] = subprocess.run,
    base_env: dict[str, str] | None = None,
    cwd: Path = PROJECT_ROOT,
    timeout_seconds: float | None = DEFAULT_TIMEOUT_SECONDS,
    continue_on_failure: bool = False,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failed_check: str | None = None
    failure_kind: str | None = None
    child_env = build_child_env(base_env)

    for command in commands:
        command_timeout = command.timeout_seconds if command.timeout_seconds is not None else timeout_seconds
        started_at = time.monotonic()
        try:
            completed = runner(
                command.argv,
                cwd=cwd,
                env=child_env,
                capture_output=True,
                text=True,
                check=False,
                timeout=command_timeout,
            )
        except subprocess.TimeoutExpired as exc:
            duration_seconds = time.monotonic() - started_at
            payload = timeout_payload(
                command,
                exc,
                timeout_seconds=float(command_timeout or 0.0),
                duration_seconds=duration_seconds,
            )
            results.append(payload)
            if failed_check is None:
                failed_check = command.name
                failure_kind = "timeout"
            if not continue_on_failure:
                break
            continue

        duration_seconds = time.monotonic() - started_at
        payload = result_payload(
            command,
            completed,
            timeout_seconds=command_timeout,
            duration_seconds=duration_seconds,
        )
        results.append(payload)
        if completed.returncode != 0:
            if failed_check is None:
                failed_check = command.name
                failure_kind = "exit_code"
            if not continue_on_failure:
                break

    status = "pass" if failed_check is None else "fail"
    report = {
        "status": status,
        "command_count": len(commands),
        "completed_commands": len(results),
        "failed_check": failed_check,
        "timeout_seconds": timeout_seconds,
        "continue_on_failure": continue_on_failure,
        "results": results,
    }
    if failure_kind is not None:
        report["failure_kind"] = failure_kind
    return report


def split_check_names(raw_values: Sequence[str] | None) -> tuple[str, ...]:
    if not raw_values:
        return ()
    names: list[str] = []
    for raw_value in raw_values:
        for item in raw_value.split(","):
            stripped = item.strip()
            if stripped:
                names.append(stripped)
    return tuple(names)


def select_commands(
    commands: Sequence[ValidationCommand],
    *,
    only: Sequence[str] = (),
    skip: Sequence[str] = (),
) -> tuple[ValidationCommand, ...]:
    command_names = {command.name for command in commands}
    requested = set(only)
    skipped = set(skip)
    unknown = sorted((requested | skipped) - command_names)
    if unknown:
        raise ValueError(f"unknown validation check(s): {', '.join(unknown)}")

    selected = commands
    if requested:
        selected = tuple(command for command in selected if command.name in requested)
    if skipped:
        selected = tuple(command for command in selected if command.name not in skipped)
    return tuple(selected)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the repo GSD validation suite with bounded, isolatable checks."
    )
    parser.add_argument("--format", choices=sorted(OUTPUT_FORMATS), default="text")
    parser.add_argument(
        "--python",
        dest="python_executable",
        default=DEFAULT_PYTHON_COMMAND,
        help="Python executable used for child validation commands.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per-command timeout. Use 0 to disable, but Codex PR gates should keep it enabled.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Run only the named check(s). May be repeated or comma-separated.",
    )
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        help="Skip the named check(s). May be repeated or comma-separated.",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="Print available validation check names without running them.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Keep running later checks after a failure or timeout.",
    )
    return parser.parse_args(argv)


def parse_output_format(argv: list[str]) -> str:
    return cast(str, parse_args(argv).format)


def emit_text_report(report: dict[str, Any]) -> None:
    for result in report["results"]:
        prefix = "OK" if result["status"] == "pass" else "FAIL"
        if result.get("failure_kind") == "timeout":
            prefix = "TIMEOUT"
        print(f"{prefix} {result['name']} ({result['command']})")
        if result.get("timed_out"):
            print(f"  timeout_seconds: {result['timeout_seconds']}")
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
    args = parse_args(argv)
    commands = build_default_commands(args.python_executable)

    if args.list_checks:
        for command in commands:
            print(command.name)
        return 0

    try:
        selected_commands = select_commands(
            commands,
            only=split_check_names(args.only),
            skip=split_check_names(args.skip),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    timeout_seconds = None if args.timeout_seconds <= 0 else args.timeout_seconds
    report = run_suite(
        selected_commands,
        timeout_seconds=timeout_seconds,
        continue_on_failure=args.continue_on_failure,
    )
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        emit_text_report(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

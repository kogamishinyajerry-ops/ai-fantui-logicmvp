from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "validation_report_v1.schema.json"
ASSET_PATH = PROJECT_ROOT / "tests" / "fixtures" / "validation_report_asset_v1.json"
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_debug_json_schema.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to run offline JSON Schema validation."
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path) -> Path | str:
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def validation_script_env(env_overrides: dict[str, str]) -> dict[str, str]:
    env = dict(os.environ)
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    for key, value in env_overrides.items():
        if key.endswith("_PATH") and not Path(value).is_absolute():
            env[key] = str(PROJECT_ROOT / value)
        else:
            env[key] = value
    return env


def run_validation_report_scenario(scenario: dict) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, str(VALIDATION_SCRIPT_PATH), *scenario["args"]],
        cwd=PROJECT_ROOT,
        env=validation_script_env(scenario.get("env", {})),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse validation report JSON for {scenario['name']}: {exc}") from exc
    return result, payload


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def make_report(status: str = "pass") -> dict:
    return {
        "asset_path": str(relative_path(ASSET_PATH)),
        "results": [],
        "schema_path": str(relative_path(SCHEMA_PATH)),
        "status": status,
    }


def make_result(scenario: dict, report_status: str | None, validation_status: str, **extra_fields) -> dict:
    result = {
        "report_status": report_status,
        "scenario": scenario["name"],
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_reports() -> tuple[int, dict, list[str]]:
    text_lines: list[str] = []
    report = make_report()

    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        schema_document = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to use {SCHEMA_PATH}: {exc}"]

    validator = Draft202012Validator(schema_document)
    asset = load_json(ASSET_PATH)

    for scenario in asset["scenarios"]:
        try:
            result, payload = run_validation_report_scenario(scenario)
        except ValueError as exc:
            report["failure_kind"] = "report_parse"
            report["results"].append(
                make_result(scenario, None, "fail", reason=str(exc))
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {scenario['name']}: {exc}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            report["failure_kind"] = "schema_validation"
            report["results"].append(
                make_result(
                    scenario,
                    payload.get("status"),
                    "fail",
                    errors=[format_validation_error(error) for error in errors[:10]],
                )
            )
            report["status"] = "fail"
            text_lines.append(f"FAIL {scenario['name']}: validation report schema errors")
            for error in errors[:10]:
                text_lines.append(f"  - {format_validation_error(error)}")
            return 1, report, text_lines

        if payload.get("status") != scenario["expected_status"]:
            report["failure_kind"] = "status_mismatch"
            report["results"].append(
                make_result(
                    scenario,
                    payload.get("status"),
                    "fail",
                    expected_report_status=scenario["expected_status"],
                    report_exit_code=result.returncode,
                )
            )
            report["status"] = "fail"
            return 1, report, [
                f"FAIL {scenario['name']}: expected status {scenario['expected_status']} "
                f"but got {payload.get('status')}"
            ]

        if scenario["expected_status"] == "fail":
            if result.returncode == 0:
                report["failure_kind"] = "exit_code_mismatch"
                report["results"].append(
                    make_result(scenario, payload.get("status"), "fail", report_exit_code=result.returncode)
                )
                report["status"] = "fail"
                return 1, report, [f"FAIL {scenario['name']}: expected report command to fail"]
        elif result.returncode != 0:
            report["failure_kind"] = "exit_code_mismatch"
            report["results"].append(
                make_result(scenario, payload.get("status"), "fail", report_exit_code=result.returncode)
            )
            report["status"] = "fail"
            return 1, report, [
                f"FAIL {scenario['name']}: report command exited with status {result.returncode}"
            ]

        report["results"].append(
            make_result(scenario, payload["status"], "pass", report_exit_code=result.returncode)
        )
        text_lines.append(
            f"OK {scenario['name']}: validated validation report status={payload['status']}"
        )

    text_lines.append(
        f"PASS: validated {len(asset['scenarios'])} validation report payloads against "
        f"{relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_validation_report_schema.py [--format text|json]")


def emit_report(report: dict, text_lines: list[str], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for line in text_lines:
        print(line)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    exit_code, report, text_lines = validate_reports()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

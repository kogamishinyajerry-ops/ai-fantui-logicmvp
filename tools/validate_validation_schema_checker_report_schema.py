from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "validation_schema_checker_report_v1.schema.json"
ASSET_PATH = PROJECT_ROOT / "tests" / "fixtures" / "validation_schema_checker_report_asset_v1.json"
VALIDATION_SCRIPT_PATH = PROJECT_ROOT / "tools" / "validate_validation_schema_runner_report_schema.py"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
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


def run_validation_schema_checker_scenario(asset: dict, scenario_name: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    scenario = asset[scenario_name]
    result = subprocess.run(
        [sys.executable, str(VALIDATION_SCRIPT_PATH), *asset["command"]],
        cwd=PROJECT_ROOT,
        env=validation_script_env(scenario.get("env", {})),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse validation schema checker report JSON for {scenario_name}: {exc}") from exc
    return result, payload


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def validate_reports() -> tuple[int, list[str]]:
    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        return 0, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return 0, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        schema_document = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        return 1, [f"FAIL schema: unable to use {SCHEMA_PATH}: {exc}"]

    validator = Draft202012Validator(schema_document)
    asset = load_json(ASSET_PATH)
    text_lines: list[str] = []

    for scenario_name in ("pass", "skip", "fail"):
        scenario = asset[scenario_name]
        try:
            result, payload = run_validation_schema_checker_scenario(asset, scenario_name)
        except ValueError as exc:
            return 1, [f"FAIL {scenario_name}: {exc}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            text_lines.append(f"FAIL {scenario_name}: validation schema checker report schema errors")
            for formatted_error in (format_validation_error(error) for error in errors[:10]):
                text_lines.append(f"  - {formatted_error}")
            return 1, text_lines

        if payload.get("status") != scenario["expected_status"]:
            return 1, [
                f"FAIL {scenario_name}: expected status {scenario['expected_status']} "
                f"but got {payload.get('status')}"
            ]

        if scenario["expected_status"] == "fail":
            if result.returncode == 0:
                return 1, [f"FAIL {scenario_name}: expected report command to fail"]
        elif result.returncode != 0:
            return 1, [f"FAIL {scenario_name}: report command exited with status {result.returncode}"]

        text_lines.append(
            f"OK {scenario_name}: validated validation schema checker report status={payload['status']}"
        )

    text_lines.append(
        f"PASS: validated 3 validation schema checker report payloads against "
        f"{relative_path(SCHEMA_PATH)}"
    )
    return 0, text_lines


def main() -> int:
    exit_code, text_lines = validate_reports()
    for line in text_lines:
        print(line)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

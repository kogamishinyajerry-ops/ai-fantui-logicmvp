from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.cli import main as well_harness_main


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "demo_answer_v1.schema.json"
ASSET_PATH = PROJECT_ROOT / "tests" / "fixtures" / "demo_json_output_asset_v1.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate demo JSON payloads."
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path) -> Path | str:
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def run_demo_json_prompt(prompt: str) -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = well_harness_main(["demo", "--format", "json", prompt])
    try:
        payload = json.loads(buffer.getvalue())
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse demo JSON for prompt {prompt!r}: {exc}") from exc
    return exit_code, payload


def make_report(status: str = "pass") -> dict:
    return {
        "asset_path": str(relative_path(ASSET_PATH)),
        "results": [],
        "schema_path": str(relative_path(SCHEMA_PATH)),
        "status": status,
    }


def make_result(prompt: str, intent: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "intent": intent,
        "prompt": prompt,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_demo_payloads() -> tuple[int, dict, list[str]]:
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
        return 1, report, [f"FAIL schema: unable to use {relative_path(SCHEMA_PATH)}: {exc}"]

    validator = Draft202012Validator(schema_document)
    asset = load_json(ASSET_PATH)
    text_lines: list[str] = []

    for case in asset["cases"]:
        prompt = case["prompt"]
        intent = case["intent"]
        try:
            exit_code, payload = run_demo_json_prompt(prompt)
        except ValueError as exc:
            report["failure_kind"] = "payload_parse"
            report["results"].append(
                make_result(prompt, intent, "fail", error_count=1, errors=[str(exc)])
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {intent}: {exc}"]

        if exit_code != 0:
            report["failure_kind"] = "cli_exit"
            report["results"].append(
                make_result(
                    prompt,
                    intent,
                    "fail",
                    error_count=1,
                    errors=[f"demo CLI exited with status {exit_code}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {intent}: demo CLI exited with status {exit_code}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["failure_kind"] = "schema_validation"
            report["results"].append(
                make_result(
                    prompt,
                    intent,
                    "fail",
                    error_count=len(errors),
                    errors=formatted_errors,
                )
            )
            report["status"] = "fail"
            text_lines.append(f"FAIL {intent}: demo answer schema validation errors")
            for formatted_error in formatted_errors:
                text_lines.append(f"  - {formatted_error}")
            return 1, report, text_lines

        if payload.get("intent") != intent:
            report["failure_kind"] = "intent_mismatch"
            report["results"].append(
                make_result(
                    prompt,
                    intent,
                    "fail",
                    error_count=1,
                    errors=[f"expected intent {intent} but got {payload.get('intent')}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [
                f"FAIL {intent}: expected intent {intent} but got {payload.get('intent')}"
            ]

        report["results"].append(
            make_result(prompt, intent, "pass", error_count=0, errors=[])
        )
        text_lines.append(f"OK {intent}: validated demo JSON prompt={prompt!r}")

    text_lines.append(
        f"PASS: validated {len(asset['cases'])} demo JSON payloads against "
        f"{relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_demo_answer_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_demo_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

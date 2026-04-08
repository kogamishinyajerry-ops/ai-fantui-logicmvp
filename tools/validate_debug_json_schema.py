from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from well_harness.cli import main as cli_main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "well_harness_debug_v1.schema.json"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
FORCE_SCHEMA_PATH_ENV = "WELL_HARNESS_FORCE_SCHEMA_PATH"
FORCE_CONTRACT_PATH_ENV = "WELL_HARNESS_FORCE_CONTRACT_PATH"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to run offline JSON Schema validation."
)
CLI_FAILURE_DETAIL_MAPPINGS = (
    ("--logic is required with --view explain", "cli_error.missing_logic_for_explain"),
    ("argument --logic: invalid choice:", "cli_error.invalid_logic_choice"),
    ("argument scenario: invalid choice:", "cli_error.invalid_scenario_choice"),
)


def load_contracts() -> list[dict]:
    contracts = []
    override = os.environ.get(FORCE_CONTRACT_PATH_ENV)
    contract_paths = [Path(override)] if override else sorted(FIXTURES_DIR.glob("*_contract_v1.json"))
    for contract_path in contract_paths:
        with contract_path.open(encoding="utf-8") as contract_file:
            contract = json.load(contract_file)
        contract["_path"] = str(contract_path)
        contracts.append(contract)
    return contracts


def resolved_schema_path() -> Path:
    override = os.environ.get(FORCE_SCHEMA_PATH_ENV)
    return Path(override) if override else SCHEMA_PATH


def load_schema_document(schema_path: Path) -> dict:
    with schema_path.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def summarize_cli_failure(stdout_text: str, stderr_text: str) -> str | None:
    summary_lines = []
    for text in (stderr_text, stdout_text):
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("usage:"):
                continue
            if ": error:" in stripped:
                stripped = stripped.split(": error:", maxsplit=1)[1].strip()
            summary_lines.append(stripped)
    return summary_lines[-1] if summary_lines else None


def normalize_cli_failure_detail(summary_text: str | None) -> str:
    if summary_text:
        for marker, detail_token in CLI_FAILURE_DETAIL_MAPPINGS:
            if marker in summary_text:
                return detail_token
    return "cli_error.unclassified"


def run_json_cli(args: list[str]) -> tuple[int, dict, str | None]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exit_code = cli_main(args)
    except SystemExit as exc:
        exit_code = int(exc.code) if isinstance(exc.code, int) else 1
    stdout_text = stdout_buffer.getvalue()
    stderr_text = stderr_buffer.getvalue()
    if exit_code != 0:
        return exit_code, {}, normalize_cli_failure_detail(
            summarize_cli_failure(stdout_text, stderr_text)
        )
    return exit_code, json.loads(stdout_text), None


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def format_schema_path(schema_path: Path) -> Path | str:
    try:
        return schema_path.relative_to(PROJECT_ROOT)
    except ValueError:
        return schema_path


def format_contract_path(contract_path: str) -> str:
    try:
        return str(Path(contract_path).relative_to(PROJECT_ROOT))
    except ValueError:
        return contract_path


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_debug_json_schema.py [--format text|json]")


def make_contract_result(contract: dict, status: str, **extra_fields) -> dict:
    result = {
        "contract_name": contract["contract_name"],
        "contract_path": format_contract_path(contract["_path"]),
        "scenario_name": contract["schema"]["scenario_name"],
        "status": status,
        "view": contract["schema"]["view"],
    }
    result.update(extra_fields)
    return result


def validate_contracts() -> tuple[int, dict, list[str]]:
    schema_path = resolved_schema_path()
    report = {
        "results": [],
        "schema_path": str(format_schema_path(schema_path)),
        "status": "pass",
    }
    text_lines = []

    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        report["status"] = "skip"
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        text_lines.append(OPTIONAL_JSONSCHEMA_SKIP_MESSAGE)
        return 0, report, text_lines

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        report["status"] = "skip"
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        text_lines.append(OPTIONAL_JSONSCHEMA_SKIP_MESSAGE)
        return 0, report, text_lines

    try:
        schema_document = load_schema_document(schema_path)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        report["status"] = "fail"
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        text_lines.append(f"FAIL schema: unable to use {schema_path}: {exc}")
        return 1, report, text_lines

    validator = Draft202012Validator(schema_document)
    contracts = load_contracts()

    for contract in contracts:
        exit_code, payload, cli_failure_summary = run_json_cli(contract["command"])
        if exit_code != 0:
            detail_suffix = f" (detail: {cli_failure_summary})" if cli_failure_summary else ""
            report["status"] = "fail"
            report["failure_kind"] = "cli_exit"
            report["results"].append(
                make_contract_result(
                    contract,
                    "fail",
                    detail=cli_failure_summary,
                    exit_code=exit_code,
                    failure_kind="cli_exit",
                )
            )
            text_lines.append(
                f"FAIL {contract['schema']['view']}: CLI exited with status {exit_code}"
                f"{detail_suffix} for {contract['_path']}",
            )
            return 1, report, text_lines

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["status"] = "fail"
            report["failure_kind"] = "schema_validation"
            report["results"].append(
                make_contract_result(
                    contract,
                    "fail",
                    errors=formatted_errors,
                    failure_kind="schema_validation",
                )
            )
            text_lines.append(f"FAIL {contract['schema']['view']}: schema validation errors")
            for error in errors[:10]:
                text_lines.append(f"  - {format_validation_error(error)}")
            return 1, report, text_lines

        report["results"].append(make_contract_result(contract, "pass"))
        text_lines.append(
            f"OK {contract['schema']['view']}: validated "
            f"{contract['schema']['scenario_name']} via {Path(contract['_path']).name}"
        )

    text_lines.append(
        f"PASS: validated {len(contracts)} JSON payloads against {format_schema_path(schema_path)}"
    )
    return 0, report, text_lines


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

    exit_code, report, text_lines = validate_contracts()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

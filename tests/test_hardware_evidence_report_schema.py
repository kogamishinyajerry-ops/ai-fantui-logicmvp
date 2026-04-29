from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "hardware_evidence_report_v1.schema.json"
TOOL_PATH = PROJECT_ROOT / "tools" / "validate_hardware_evidence_report.py"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validator_for_hardware_evidence_report_schema():
    pytest.importorskip("jsonschema")
    from jsonschema import Draft202012Validator

    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def tool_env() -> dict[str, str]:
    env = dict(os.environ)
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    return env


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL_PATH), *args],
        cwd=PROJECT_ROOT,
        env=tool_env(),
        capture_output=True,
        text=True,
        check=False,
    )


def test_hardware_evidence_report_tool_emits_schema_valid_json() -> None:
    validator = validator_for_hardware_evidence_report_schema()
    result = run_tool("--format", "json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    errors = list(validator.iter_errors(payload))

    assert errors == []
    assert payload["status"] == "pass"
    assert payload["hardware_summary"]["system_id"] == "thrust-reverser"
    assert payload["evidence_gaps"]["total_field_count"] == 141
    assert payload["evidence_gaps"]["inferred_field_count"] == 0


def test_hardware_evidence_report_schema_rejects_missing_evidence_gap_accounting() -> None:
    validator = validator_for_hardware_evidence_report_schema()
    payload = json.loads(run_tool("--format", "json").stdout)
    payload.pop("evidence_gaps")

    errors = list(validator.iter_errors(payload))

    assert any("evidence_gaps" in error.message for error in errors)


def test_hardware_evidence_report_tool_text_output_names_checks() -> None:
    result = run_tool()

    assert result.returncode == 0
    assert "OK lru_inventory_coverage" in result.stdout
    assert "OK signal_binding_coverage" in result.stdout
    assert "OK evidence_gap_accounting" in result.stdout
    assert "PASS: hardware evidence report is deterministic and read-only." in result.stdout


def test_hardware_evidence_report_rejects_unsupported_format() -> None:
    result = run_tool("--format", "xml")

    assert result.returncode == 2
    assert "usage: validate_hardware_evidence_report.py" in result.stderr

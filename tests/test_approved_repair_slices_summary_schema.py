from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID = "https://well-harness.local/json_schema/approved_repair_slices_summary_v0_1.schema.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "approved_repair_slices_summary_v0_1.schema.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "approved_repair_slices_summary_v0_1.json"
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_repair_slices.py"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"missing fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_approved_repair_slices_summary_schema_declares_external_artifact_contract() -> None:
    schema = _load_json(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID
    assert schema["title"] == "Approved Repair Slices Summary v0.1"
    assert schema["properties"]["$schema"]["const"] == SCHEMA_ID
    assert schema["properties"]["kind"]["const"] == "ai-fantui-approved-repair-slices-summary"
    assert schema["x-well-harness-approved-repair-slices-summary"] == {
        "schema_version": "0.1",
        "scope": "CI artifact summary for approved candidate repair slices",
        "truth_effect": "none",
        "controller_truth_modified": False,
    }


def test_approved_repair_slices_summary_fixture_is_schema_valid() -> None:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fixture),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert fixture["aggregate"] == {
        "slice_count": 2,
        "passed": 2,
        "converged": 2,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_repair_slices_gate_emits_schema_valid_summary(tmp_path: Path) -> None:
    schema = _load_json(SCHEMA_PATH)
    result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.path),
    )

    assert [] == [f"{list(error.path)}: {error.message}" for error in errors]
    assert payload["$schema"] == SCHEMA_ID
    assert payload["kind"] == "ai-fantui-approved-repair-slices-summary"

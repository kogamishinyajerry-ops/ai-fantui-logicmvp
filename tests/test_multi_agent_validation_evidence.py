from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from well_harness.multi_agent_pr_preflight import build_multi_agent_pr_preflight
from well_harness.multi_agent_validation_evidence import (
    SCHEMA_ID,
    build_multi_agent_validation_evidence,
    render_multi_agent_validation_evidence_html,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_validation_evidence_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_validation_evidence.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_validation_evidence.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
EVIDENCE_DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-validation-evidence.md"
MVP_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "multi-agent-control-logic-engineering-system-mvp.md"
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _recorded_pass_results() -> list[dict]:
    preflight = build_multi_agent_pr_preflight(
        project_root=PROJECT_ROOT,
        generated_at="2026-05-27T00:00:00Z",
    )
    return [
        {
            "command_id": item["command_id"],
            "package_id": item["package_id"],
            "command": item["command"],
            "status": "pass",
            "exit_code": 0,
            "duration_seconds": 0.01,
            "output_tail": f"{item['command_id']} passed",
        }
        for item in preflight["validation_plan"]
    ]


def test_multi_agent_validation_evidence_schema_validates_payload() -> None:
    payload = build_multi_agent_validation_evidence(
        project_root=PROJECT_ROOT,
        command_results=_recorded_pass_results(),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["status"] == "pass"
    assert payload["milestone"]["id"] == "M25"
    assert payload["summary"] == {
        "dirty_worktree_policy": "ignore_unrelated_dirty_files_and_stage_only_listed_pathspecs",
        "executed_command_count": 21,
        "failed_command_count": 0,
        "package_count": 8,
        "passed_command_count": 21,
        "stage_command_count": 9,
        "validation_command_count": 21,
    }
    assert payload["inputs"]["preflight_id"] == "multi-agent-pr-preflight-v0.1"
    assert payload["validation_results"][0]["command_id"] == "multi-agent-cursor-baseline-v0-2-01"
    assert payload["validation_results"][-1]["command_id"] == "m24-pr-preflight-03"
    assert any("git add -f --" in command for command in payload["stage_commands"])
    assert any("multi-agent-validation-evidence.md" in command for command in payload["stage_commands"])
    assert "notion-control-plane-404" in payload["pr_evidence_note"]
    assert "21 validation commands passed" in payload["pr_evidence_note"]
    assert payload["blockers"][0]["status"] == "external_blocker"


def test_multi_agent_validation_evidence_html_exposes_results_and_blocker() -> None:
    payload = build_multi_agent_validation_evidence(
        project_root=PROJECT_ROOT,
        command_results=_recorded_pass_results(),
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_multi_agent_validation_evidence_html(payload)

    assert "Multi-Agent Validation Evidence" in html
    assert "multi-agent-cursor-baseline-v0-2-01" in html
    assert "m24-pr-preflight-03" in html
    assert "m25-validation-evidence" in html
    assert "notion-control-plane-404" in html
    assert "21 validation commands passed" in html


def test_multi_agent_validation_evidence_runner_and_checker_round_trip(tmp_path: Path) -> None:
    results_path = tmp_path / "recorded_results.json"
    results_path.write_text(
        json.dumps(_recorded_pass_results(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT),
            "--artifact-dir",
            str(tmp_path),
            "--command-results",
            str(results_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["artifact_paths"]["evidence_html"] == str(
        tmp_path / "multi_agent_validation_evidence_v0_1.html"
    )
    assert payload["status"] == "pass"

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            payload["artifact_paths"]["evidence_json"],
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert verify_result.returncode == 0, verify_result.stderr
    verify_payload = json.loads(verify_result.stdout)
    assert verify_payload == {
        "html_exists": True,
        "markdown_exists": True,
        "mismatches": [],
        "package_path": payload["artifact_paths"]["evidence_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_validation_evidence_is_wired_into_docs_and_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = EVIDENCE_DOC_PATH.read_text(encoding="utf-8")
    mvp_doc = MVP_DOC_PATH.read_text(encoding="utf-8")

    assert "MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR" in makefile
    assert "multi-agent-validation-evidence" in makefile
    assert "verify-multi-agent-validation-evidence" in makefile
    assert "scripts/run_multi_agent_validation_evidence.py --format json" in makefile
    assert "scripts/verify_multi_agent_validation_evidence.py --format json" in makefile

    assert "21 validation commands" in doc
    assert "9 explicit stage commands" in doc
    assert "m25-validation-evidence" in doc
    assert "notion-control-plane-404" in doc
    assert "src/well_harness/controller.py" in doc

    assert "M25" in mvp_doc
    assert "make multi-agent-validation-evidence" in mvp_doc

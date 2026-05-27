from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from well_harness.multi_agent_pr_preflight import (
    SCHEMA_ID,
    build_multi_agent_pr_preflight,
    render_multi_agent_pr_preflight_html,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_pr_preflight_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_pr_preflight.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_pr_preflight.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
PREFLIGHT_DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-pr-preflight.md"
MVP_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "multi-agent-control-logic-engineering-system-mvp.md"
)


EXPECTED_ORDER = [
    "multi-agent-cursor-baseline-v0-2",
    "project-manager-status",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
    "m24-pr-preflight",
]


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_multi_agent_pr_preflight_schema_validates_payload() -> None:
    payload = build_multi_agent_pr_preflight(
        project_root=PROJECT_ROOT,
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["status"] == "pass"
    assert payload["milestone"]["id"] == "M24"
    assert payload["summary"]["package_count"] == 6
    assert payload["summary"]["validation_command_count"] == 19
    assert payload["summary"]["stage_command_count"] == 7
    assert [package["package_id"] for package in payload["pathspec_packages"]] == EXPECTED_ORDER
    assert [item["package_id"] for item in payload["validation_plan"][:4]] == [
        "multi-agent-cursor-baseline-v0-2",
        "multi-agent-cursor-baseline-v0-2",
        "multi-agent-cursor-baseline-v0-2",
        "multi-agent-cursor-baseline-v0-2",
    ]
    assert any("git add -f --" in command for command in payload["stage_commands"])
    assert any("tests/test_multi_agent_pr_preflight.py" in command for command in payload["stage_commands"])
    assert "notion-control-plane-404" in payload["pr_body"]["body"]
    assert "make verify-multi-agent-packaging-consolidation" in payload["pr_body"]["body"]
    assert "make verify-multi-agent-pr-preflight" in payload["pr_body"]["body"]
    assert "Makefile" in payload["pr_body"]["body"]
    assert "docs/coordination/multi-agent-pr-preflight.md" in payload["pr_body"]["body"]
    assert "src/well_harness/controller.py" in payload["excluded_paths"]
    assert payload["blockers"] == [
        {
            "blocker_id": "notion-control-plane-404",
            "status": "external_blocker",
            "message": "Notion control-plane HTTP 404 remains outside this packaging slice.",
        }
    ]


def test_multi_agent_pr_preflight_html_exposes_validation_and_pr_body() -> None:
    payload = build_multi_agent_pr_preflight(
        project_root=PROJECT_ROOT,
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_multi_agent_pr_preflight_html(payload)

    assert "Multi-Agent PR Preflight" in html
    assert "multi-agent-cursor-baseline-v0-2-01" in html
    assert "ultrawork-monitor" in html
    assert "m23-packaging-consolidation" in html
    assert "m24-pr-preflight" in html
    assert "notion-control-plane-404" in html
    assert "git add -f --" in html
    assert "Browser Geometry Gate" in html


def test_multi_agent_pr_preflight_runner_and_checker_round_trip(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT),
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
        timeout=120,
    )
    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["artifact_paths"]["preflight_html"] == str(
        tmp_path / "multi_agent_pr_preflight_v0_1.html"
    )
    assert payload["status"] == "pass"

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            payload["artifact_paths"]["preflight_json"],
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
        "package_path": payload["artifact_paths"]["preflight_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_pr_preflight_is_wired_into_docs_and_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = PREFLIGHT_DOC_PATH.read_text(encoding="utf-8")
    mvp_doc = MVP_DOC_PATH.read_text(encoding="utf-8")

    assert "MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR" in makefile
    assert "multi-agent-pr-preflight" in makefile
    assert "verify-multi-agent-pr-preflight" in makefile
    assert "scripts/run_multi_agent_pr_preflight.py --format json" in makefile
    assert "scripts/verify_multi_agent_pr_preflight.py --format json" in makefile

    for marker in EXPECTED_ORDER:
        assert marker in doc
    assert "19 validation commands" in doc
    assert "git add -f --" in doc
    assert "notion-control-plane-404" in doc
    assert "src/well_harness/controller.py" in doc

    assert "M24" in mvp_doc
    assert "make multi-agent-pr-preflight" in mvp_doc

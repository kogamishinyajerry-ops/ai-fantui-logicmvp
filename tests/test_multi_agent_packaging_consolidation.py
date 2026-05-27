from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from well_harness.multi_agent_packaging_consolidation import (
    SCHEMA_ID,
    build_multi_agent_packaging_consolidation,
    render_multi_agent_packaging_html,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_packaging_consolidation_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_packaging_consolidation.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_packaging_consolidation.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
PACKAGE_DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-packaging-consolidation.md"
MVP_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "multi-agent-control-logic-engineering-system-mvp.md"
)


EXPECTED_ORDER = [
    "multi-agent-cursor-baseline-v0-2",
    "project-manager-status",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
]


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_multi_agent_packaging_consolidation_schema_validates_payload() -> None:
    payload = build_multi_agent_packaging_consolidation(
        project_root=PROJECT_ROOT,
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["status"] == "pass"
    assert payload["milestone"]["id"] == "M23"
    assert [package["package_id"] for package in payload["package_order"]] == EXPECTED_ORDER
    assert payload["summary"]["missing_pathspec_count"] == 0
    assert any("git add -f --" in command for command in payload["stage_commands"])
    assert any(
        "docs/coordination/multi-agent-operator-cockpit.md" in command
        for command in payload["stage_commands"]
    )
    assert "src/well_harness/controller.py" in payload["excluded_paths"]
    assert "src/well_harness/demo_server.py" in payload["excluded_paths"]
    assert "src/well_harness/static/**" in payload["excluded_paths"]


def test_multi_agent_packaging_consolidation_html_exposes_order_and_blocker() -> None:
    payload = build_multi_agent_packaging_consolidation(
        project_root=PROJECT_ROOT,
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_multi_agent_packaging_html(payload)

    assert "Multi-Agent Packaging Consolidation" in html
    assert "multi-agent-cursor-baseline" in html
    assert "project-manager-status" in html
    assert "ultrawork-monitor" in html
    assert "m22-operator-cockpit" in html
    assert "notion-control-plane-404" in html
    assert "git add -f --" in html


def test_multi_agent_packaging_consolidation_runner_and_checker_round_trip(
    tmp_path: Path,
) -> None:
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
    assert payload["artifact_paths"]["package_html"] == str(
        tmp_path / "multi_agent_packaging_consolidation_v0_1.html"
    )
    assert payload["status"] == "pass"

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            payload["artifact_paths"]["package_json"],
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
        "package_path": payload["artifact_paths"]["package_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_packaging_consolidation_is_wired_into_docs_and_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = PACKAGE_DOC_PATH.read_text(encoding="utf-8")
    mvp_doc = MVP_DOC_PATH.read_text(encoding="utf-8")

    assert "MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR" in makefile
    assert "multi-agent-packaging-consolidation" in makefile
    assert "verify-multi-agent-packaging-consolidation" in makefile
    assert "scripts/run_multi_agent_packaging_consolidation.py --format json" in makefile
    assert "scripts/verify_multi_agent_packaging_consolidation.py --format json" in makefile

    for marker in EXPECTED_ORDER:
        assert marker in doc
    assert "git add -f --" in doc
    assert "src/well_harness/controller.py" in doc
    assert "src/well_harness/demo_server.py" in doc
    assert "artifacts/**" in doc
    assert "notion-control-plane-404" in doc

    assert "M23" in mvp_doc
    assert "make multi-agent-packaging-consolidation" in mvp_doc

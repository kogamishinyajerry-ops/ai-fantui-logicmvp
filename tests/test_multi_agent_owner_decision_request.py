from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema
import pytest

from well_harness.multi_agent_owner_acceptance_handoff import (
    build_multi_agent_owner_acceptance_handoff,
)
from well_harness.multi_agent_owner_decision_request import (
    SCHEMA_ID,
    build_multi_agent_owner_decision_request,
    render_multi_agent_owner_decision_request_html,
    write_multi_agent_owner_decision_request_artifacts,
)
from well_harness.multi_agent_release_decision_input import build_multi_agent_release_decision_input
from well_harness.multi_agent_review_closure import build_multi_agent_review_closure


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_owner_decision_request_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_owner_decision_request.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_owner_decision_request.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-owner-decision-request.md"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _m30_pr_status() -> dict:
    return {
        "number": 271,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/271",
        "state": "OPEN",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "74a4580f82d7a86c01bf3c7e0ccea2efc7e306bc",
        "statusCheckRollup": [],
        "reviews": [],
        "comments": [
            {
                "author": {"login": "kogamishinyajerry-ops"},
                "createdAt": "2026-05-28T09:13:16Z",
                "body": (
                    "@codex review latest head "
                    "74a4580f82d7a86c01bf3c7e0ccea2efc7e306bc"
                ),
            },
            {
                "author": {"login": "chatgpt-codex-connector"},
                "createdAt": "2026-05-28T09:25:46Z",
                "body": "Codex Review: Didn't find any major issues.",
            },
        ],
    }


def _m30_thread() -> dict:
    return {
        "isResolved": False,
        "isOutdated": False,
        "path": "src/well_harness/multi_agent_review_closure.py",
        "line": 203,
        "comments": {
            "nodes": [
                {
                    "author": {"login": "chatgpt-codex-connector"},
                    "createdAt": "2026-05-28T09:06:26Z",
                    "body": "**P2 Prior issue now covered by latest clean review**",
                    "commit": {"oid": "74a4580f82d7a86c01bf3c7e0ccea2efc7e306bc"},
                }
            ]
        },
    }


def _release_decision_input() -> dict:
    closure = build_multi_agent_review_closure(
        pr_status=_m30_pr_status(),
        review_threads=[_m30_thread()],
        generated_at="2026-05-28T09:30:00Z",
    )
    return build_multi_agent_release_decision_input(
        review_closure=closure,
        generated_at="2026-05-28T09:40:00Z",
    )


def _pr_status(status_check_rollup: list[dict] | None = None) -> dict:
    return {
        "number": 271,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/271",
        "state": "OPEN",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "74a4580f82d7a86c01bf3c7e0ccea2efc7e306bc",
        "statusCheckRollup": status_check_rollup or [],
        "reviews": [],
        "comments": [],
    }


def _review_thread(*, outdated: bool = True) -> dict:
    return {
        "id": "thread-1",
        "isResolved": False,
        "isOutdated": outdated,
        "path": "scripts/verify_multi_agent_owner_acceptance_handoff.py",
        "line": None if outdated else 44,
        "comments": {"nodes": [{"body": "Informational review note"}]},
    }


def _owner_acceptance_handoff(*, checks: bool = False, blocked: bool = False) -> dict:
    release = _release_decision_input()
    if blocked:
        release["blockers"] = [
            {
                "blocker_id": "release-blocker",
                "status": "local_blocker",
                "message": "Release blocker fixture.",
            }
        ]
        release["status"] = "blocked"
    return build_multi_agent_owner_acceptance_handoff(
        release_decision_input=release,
        pr_status=_pr_status(
            status_check_rollup=[{"name": "validation", "conclusion": "SUCCESS"}] if checks else []
        ),
        review_threads=[_review_thread(outdated=True)] if not checks else [],
        generated_at="2026-05-28T10:40:00Z",
    )


def _load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "run_multi_agent_owner_decision_request",
        RUN_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_decision_request_schema_validates_warning_state() -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(),
        generated_at="2026-05-28T11:20:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["milestone"]["id"] == "M33"
    assert payload["status"] == "awaiting_owner_decision_with_warnings"
    assert payload["summary"]["decision_input_required"] is True
    assert payload["summary"]["decision_recorded"] is False
    assert payload["gates"]["remote_checks_warning"] == "warning"
    assert payload["decision_input_template"]["template_mode"] is True
    assert payload["decision_input_template"]["attestation"]["decision_is_explicit"] is False


def test_owner_decision_request_ready_when_handoff_has_green_checks() -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(checks=True),
        generated_at="2026-05-28T11:20:00Z",
    )

    assert payload["status"] == "awaiting_owner_decision"
    assert payload["gates"]["remote_checks_warning"] == "pass"
    accept_option = next(
        item for item in payload["decision_options"] if item["option_id"] == "accept_when_authorized"
    )
    assert accept_option["requires_remote_warning_acknowledgement"] is False


def test_owner_decision_request_blocks_when_m32_handoff_blocked() -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(blocked=True),
        generated_at="2026-05-28T11:20:00Z",
    )

    assert payload["status"] == "blocked"
    assert payload["gates"]["owner_acceptance_handoff"] == "fail"
    assert payload["gates"]["m32_active_blockers"] == "fail"
    assert payload["blockers"]


def test_owner_decision_request_html_exposes_no_decision_boundary() -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(),
        generated_at="2026-05-28T11:20:00Z",
    )
    html = render_multi_agent_owner_decision_request_html(payload)

    assert "Multi-Agent Owner Decision Request" in html
    assert "Decision input required" in html
    assert "Decision recorded" in html
    assert "notion_control_plane_changes" in html
    assert "external_manual_input_only" in html
    assert "Decision Input Template" in html
    assert "five_agent_context_cap" in html
    assert "PackagingPRReadinessAgent" in html
    assert 'class="gate-row"' in html
    assert 'class="option-row"' in html
    assert 'class="agent-row"' in html
    assert 'class="template-row"' in html
    assert 'class="boundary-row"' in html
    assert 'class="pathspec-item"' in html


def test_owner_decision_request_writer_and_checker_round_trip(tmp_path: Path) -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(),
        generated_at="2026-05-28T11:20:00Z",
    )
    written = write_multi_agent_owner_decision_request_artifacts(
        payload,
        artifact_dir=tmp_path / "request",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["request_json"],
            "--format",
            "json",
            "--skip-browser",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert verify_result.returncode == 0, verify_result.stderr
    result = json.loads(verify_result.stdout)
    assert result["status"] == "pass"
    assert result["html_exists"] is True
    assert result["markdown_exists"] is True
    assert result["template_exists"] is True
    assert result["browser_valid"] is False
    assert result["browser"]["status"] == "skipped"
    assert result["mismatches"] == []


@pytest.mark.e2e
def test_owner_decision_request_browser_gate_captures_geometry(
    tmp_path: Path,
) -> None:
    payload = build_multi_agent_owner_decision_request(
        owner_acceptance_handoff=_owner_acceptance_handoff(),
        generated_at="2026-05-28T11:20:00Z",
    )
    written = write_multi_agent_owner_decision_request_artifacts(
        payload,
        artifact_dir=tmp_path / "request",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["request_json"],
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
    assert verify_payload["status"] == "pass"
    assert verify_payload["browser_valid"] is True
    browser = verify_payload["browser"]
    assert browser["status"] == "pass"
    assert Path(browser["screenshots"]["desktop"]).exists()
    assert Path(browser["screenshots"]["mobile"]).exists()
    assert browser["states"]["desktop"]["noHorizontalOverflow"] is True
    assert browser["states"]["mobile"]["noHorizontalOverflow"] is True
    assert browser["states"]["desktop"]["requiredTextPresent"] is True
    assert browser["states"]["mobile"]["requiredTextPresent"] is True
    assert browser["states"]["desktop"]["gateRowCount"] == len(payload["gates"])
    assert browser["states"]["mobile"]["optionRowCount"] == len(payload["decision_options"])
    assert browser["states"]["desktop"]["agentRowCount"] == payload["agent_team"]["team_size"]
    assert browser["states"]["mobile"]["templateRowCount"] >= 4
    assert browser["states"]["desktop"]["boundaryRowCount"] == len(payload["decision_boundaries"])
    assert browser["states"]["mobile"]["pathspecItemCount"] == len(
        payload["pathspec_package"]["pathspecs"],
    )


def test_owner_decision_request_runner_uses_supplied_handoff(tmp_path: Path) -> None:
    module = _load_runner_module()
    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(json.dumps(_owner_acceptance_handoff()), encoding="utf-8")

    payload = module.run_multi_agent_owner_decision_request(
        artifact_dir=tmp_path / "run",
        owner_acceptance_handoff_path=handoff_path,
        refresh_owner_acceptance_handoff=False,
    )

    assert payload["status"] == "awaiting_owner_decision_with_warnings"
    assert payload["artifact_paths"]["request_json"].endswith(
        "multi_agent_owner_decision_request_v0_1.json"
    )
    template_path = Path(payload["artifact_paths"]["decision_input_template"])
    assert template_path.exists()
    assert json.loads(template_path.read_text(encoding="utf-8"))["template_mode"] is True


def test_owner_decision_request_makefile_and_docs_are_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "multi-agent-owner-decision-request" in makefile
    assert "verify-multi-agent-owner-decision-request" in makefile
    assert "M33" in doc
    assert "repo_github_local_artifacts_only" in doc
    assert "desktop/mobile" in doc
    assert "screenshots" in doc

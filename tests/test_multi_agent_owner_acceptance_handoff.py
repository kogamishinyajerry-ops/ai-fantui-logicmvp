from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema

from well_harness.multi_agent_owner_acceptance_handoff import (
    SCHEMA_ID,
    build_multi_agent_owner_acceptance_handoff,
    render_multi_agent_owner_acceptance_handoff_html,
    write_multi_agent_owner_acceptance_handoff_artifacts,
)
from well_harness.multi_agent_release_decision_input import (
    build_multi_agent_release_decision_input,
)
from well_harness.multi_agent_review_closure import build_multi_agent_review_closure


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_owner_acceptance_handoff_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_owner_acceptance_handoff.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_owner_acceptance_handoff.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-owner-acceptance-handoff.md"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _m30_pr_status(remote_checks: list[dict] | None = None) -> dict:
    return {
        "number": 270,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/270",
        "state": "OPEN",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "a00b9d10e254c65e005e98ad069a4f8c3e5f1e5d",
        "statusCheckRollup": remote_checks or [],
        "reviews": [],
        "comments": [
            {
                "author": {"login": "kogamishinyajerry-ops"},
                "createdAt": "2026-05-28T09:13:16Z",
                "body": (
                    "@codex review latest head "
                    "a00b9d10e254c65e005e98ad069a4f8c3e5f1e5d"
                ),
            },
            {
                "author": {"login": "chatgpt-codex-connector"},
                "createdAt": "2026-05-28T09:25:46Z",
                "body": "Codex Review: Didn't find any major issues.",
            },
        ],
    }


def _m30_thread(body: str) -> dict:
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
                    "body": body,
                    "commit": {
                        "oid": "a00b9d10e254c65e005e98ad069a4f8c3e5f1e5d",
                    },
                }
            ]
        },
    }


def _release_decision_input(*, blocker: bool = False) -> dict:
    closure = build_multi_agent_review_closure(
        pr_status=_m30_pr_status(),
        review_threads=[
            _m30_thread("**P2 Prior issue now covered by latest clean review**"),
        ],
        generated_at="2026-05-28T09:30:00Z",
    )
    if blocker:
        closure["blockers"] = [
            {
                "blocker_id": "owner-policy-blocker",
                "status": "external_blocker",
                "message": "Owner policy review is still pending.",
            }
        ]
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


def _review_thread(*, outdated: bool = True, actionable: bool = True) -> dict:
    body = (
        "**<sub><sub>![P2 Badge](https://img.shields.io/badge/P2-yellow?style=flat)</sub></sub> "
        "Review finding**"
        if actionable
        else "Informational review note"
    )
    return {
        "id": "thread-1",
        "isResolved": False,
        "isOutdated": outdated,
        "path": "scripts/verify_multi_agent_owner_acceptance_handoff.py",
        "line": None if outdated else 44,
        "comments": {
            "nodes": [
                {
                    "author": {"login": "chatgpt-codex-connector"},
                    "createdAt": "2026-05-28T10:11:31Z",
                    "body": body,
                    "commit": {"oid": "be633d0251803f3fc114c34ce1ab529d12bf74a9"},
                    "url": "https://github.com/example/review",
                }
            ]
        },
    }


def _load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "run_multi_agent_owner_acceptance_handoff",
        RUN_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_acceptance_handoff_schema_validates_ready_with_warnings() -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(),
        pr_status=_pr_status(),
        review_threads=[_review_thread(outdated=True)],
        generated_at="2026-05-28T10:40:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["milestone"]["id"] == "M32"
    assert payload["status"] == "ready_for_owner_acceptance_with_warnings"
    assert payload["gates"]["release_decision_input"] == "pass"
    assert payload["gates"]["outdated_review_threads"] == "warning"
    assert payload["gates"]["remote_checks"] == "warning"
    assert payload["summary"]["current_actionable_thread_count"] == 0
    assert payload["summary"]["outdated_unresolved_thread_count"] == 1
    assert payload["decision_boundaries"]["owner_final_decision"] == "external_manual_only"
    assert payload["agent_team"]["team_size"] == 5


def test_owner_acceptance_handoff_ready_when_checks_pass_and_no_threads() -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(),
        pr_status=_pr_status(status_check_rollup=[{"name": "validation", "conclusion": "SUCCESS"}]),
        review_threads=[],
        generated_at="2026-05-28T10:40:00Z",
    )

    assert payload["status"] == "ready_for_owner_acceptance"
    assert payload["gates"]["remote_checks"] == "pass"
    assert payload["gates"]["outdated_review_threads"] == "pass"


def test_owner_acceptance_handoff_blocks_current_actionable_review() -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(),
        pr_status=_pr_status(),
        review_threads=[_review_thread(outdated=False)],
        generated_at="2026-05-28T10:40:00Z",
    )

    assert payload["status"] == "blocked"
    assert payload["gates"]["current_actionable_reviews"] == "fail"
    assert payload["summary"]["current_actionable_thread_count"] == 1
    assert payload["blockers"][0]["blocker_id"] == "current-actionable-review-threads"


def test_owner_acceptance_handoff_blocks_release_decision_blocker() -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(blocker=True),
        pr_status=_pr_status(status_check_rollup=[{"name": "validation", "conclusion": "SUCCESS"}]),
        review_threads=[],
        generated_at="2026-05-28T10:40:00Z",
    )

    assert payload["status"] == "blocked"
    assert payload["gates"]["release_decision_input"] == "fail"
    assert payload["gates"]["release_decision_blockers"] == "fail"
    assert payload["blockers"][0]["blocker_id"] == "owner-policy-blocker"


def test_owner_acceptance_handoff_html_exposes_owner_surface() -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(),
        pr_status=_pr_status(),
        review_threads=[_review_thread(outdated=True)],
        generated_at="2026-05-28T10:40:00Z",
    )
    html = render_multi_agent_owner_acceptance_handoff_html(payload)

    assert "Multi-Agent Owner Acceptance Handoff" in html
    assert "Owner Acceptance Checklist" in html
    assert "repo_github_local_artifacts_only" in html
    assert "external_manual_only" in html
    assert "notion_control_plane_changes" in html


def test_owner_acceptance_handoff_writer_and_checker_round_trip(tmp_path: Path) -> None:
    payload = build_multi_agent_owner_acceptance_handoff(
        release_decision_input=_release_decision_input(),
        pr_status=_pr_status(),
        review_threads=[_review_thread(outdated=True)],
        generated_at="2026-05-28T10:40:00Z",
    )
    written = write_multi_agent_owner_acceptance_handoff_artifacts(
        payload,
        artifact_dir=tmp_path / "handoff",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["handoff_json"],
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
    assert json.loads(verify_result.stdout)["status"] == "pass"


def test_owner_acceptance_handoff_runner_uses_supplied_inputs(tmp_path: Path) -> None:
    module = _load_runner_module()
    release_path = tmp_path / "release.json"
    pr_path = tmp_path / "pr.json"
    threads_path = tmp_path / "threads.json"
    release_path.write_text(json.dumps(_release_decision_input()), encoding="utf-8")
    pr_path.write_text(json.dumps(_pr_status()), encoding="utf-8")
    threads_path.write_text(json.dumps({"nodes": [_review_thread(outdated=True)]}), encoding="utf-8")

    payload = module.run_multi_agent_owner_acceptance_handoff(
        artifact_dir=tmp_path / "run",
        release_decision_input_path=release_path,
        pr_status_json=pr_path,
        review_threads_json=threads_path,
        pr_number=271,
    )

    assert payload["status"] == "ready_for_owner_acceptance_with_warnings"
    assert payload["artifact_paths"]["handoff_json"].endswith(
        "multi_agent_owner_acceptance_handoff_v0_1.json"
    )


def test_owner_acceptance_handoff_makefile_and_docs_are_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "multi-agent-owner-acceptance-handoff" in makefile
    assert "verify-multi-agent-owner-acceptance-handoff" in makefile
    assert "M32" in doc
    assert "repo_github_local_artifacts_only" in doc

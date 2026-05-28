from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema

from well_harness.multi_agent_review_closure import (
    SCHEMA_ID,
    build_multi_agent_review_closure,
    render_multi_agent_review_closure_html,
    write_multi_agent_review_closure_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_review_closure_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_review_closure.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_review_closure.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-review-closure.md"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _pr_status(*, clean: bool = True) -> dict:
    comments = [
        {
            "author": {"login": "kogamishinyajerry-ops"},
            "createdAt": "2026-05-28T07:47:33Z",
            "body": (
                "@codex review latest head "
                "944a23b38245e123d70a022ef9368bd52acc011f"
            ),
        }
    ]
    if clean:
        comments.append(
            {
                "author": {"login": "chatgpt-codex-connector"},
                "createdAt": "2026-05-28T07:51:10Z",
                "body": "Codex Review: Didn't find any major issues. :+1:",
            }
        )
    return {
        "number": 270,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/270",
        "state": "OPEN",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "944a23b38245e123d70a022ef9368bd52acc011f",
        "statusCheckRollup": [],
        "reviews": [],
        "comments": comments,
    }


def _thread(
    *,
    author: str,
    body: str,
    path: str = "scripts/run_phase1_demo_mvp_review_package.py",
    line: int = 112,
) -> dict:
    return {
        "isResolved": False,
        "isOutdated": False,
        "path": path,
        "line": line,
        "startLine": None,
        "comments": {
            "nodes": [
                {
                    "author": {"login": author},
                    "createdAt": "2026-05-28T07:43:38Z",
                    "body": body,
                    "commit": {
                        "oid": "944a23b38245e123d70a022ef9368bd52acc011f",
                    },
                }
            ]
        },
    }


def _threads() -> list[dict]:
    return [
        _thread(
            author="kogamishinyajerry-ops",
            body="Fixed in 07154d0: demo_server startup no longer imports dev-only jsonschema.",
            path="src/well_harness/requirements_intake/analysis.py",
            line=20,
        ),
        _thread(
            author="chatgpt-codex-connector",
            body="**P1 Deepen checkout before diffing against push before SHA**",
            path=".github/workflows/gsd-automation.yml",
            line=41,
        ),
    ]


def _load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "run_multi_agent_review_closure",
        RUN_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_multi_agent_review_closure_schema_validates_clean_latest_head() -> None:
    payload = build_multi_agent_review_closure(
        pr_status=_pr_status(),
        review_threads=_threads(),
        generated_at="2026-05-28T08:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["milestone"]["id"] == "M30"
    assert payload["status"] == "ready_with_warnings"
    assert payload["summary"]["latest_clean_codex_result_found"] is True
    assert payload["summary"]["actionable_thread_count"] == 0
    assert payload["summary"]["owner_fixed_thread_count"] == 1
    assert payload["summary"]["covered_prior_codex_thread_count"] == 1
    assert payload["gates"]["latest_head_review"] == "pass"
    assert payload["gates"]["remote_checks"] == "warning"
    assert payload["summary"]["control_plane"] == "repo_github_local_artifacts_only"
    assert ".planning/notion_control_plane.json" in payload["pathspec_package"]["excluded_paths"]
    assert payload["agent_team"]["team_size"] == 5


def test_multi_agent_review_closure_blocks_current_codex_thread_without_clean_review() -> None:
    payload = build_multi_agent_review_closure(
        pr_status=_pr_status(clean=False),
        review_threads=[
            _thread(
                author="chatgpt-codex-connector",
                body="**P1 Fix current head issue**",
            )
        ],
        generated_at="2026-05-28T08:00:00Z",
    )

    assert payload["status"] == "blocked"
    assert payload["gates"]["latest_head_review"] == "fail"
    assert payload["gates"]["actionable_threads"] == "fail"
    assert payload["summary"]["actionable_thread_count"] == 1
    assert payload["summary"]["recommended_next_action"] == "fix_current_actionable_review_threads"


def test_multi_agent_review_closure_html_exposes_owner_handoff() -> None:
    payload = build_multi_agent_review_closure(
        pr_status=_pr_status(),
        review_threads=_threads(),
        generated_at="2026-05-28T08:00:00Z",
    )
    html = render_multi_agent_review_closure_html(payload)

    assert "Multi-Agent Review Closure" in html
    assert "Latest Codex clean" in html
    assert "Actionable threads" in html
    assert "repo_github_local_artifacts_only" in html
    assert "project_owner_acceptance_or_merge_when_authorized" in html
    assert "prior_codex_issue_covered_by_latest_clean_review" in html


def test_multi_agent_review_closure_writer_and_checker_round_trip(tmp_path: Path) -> None:
    payload = build_multi_agent_review_closure(
        pr_status=_pr_status(),
        review_threads=_threads(),
        generated_at="2026-05-28T08:00:00Z",
    )
    written = write_multi_agent_review_closure_artifacts(
        payload,
        artifact_dir=tmp_path / "closure",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["closure_json"],
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
        "package_path": written["artifact_paths"]["closure_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_review_closure_runner_uses_supplied_fixtures(tmp_path: Path) -> None:
    module = _load_runner_module()
    pr_status_path = tmp_path / "pr.json"
    threads_path = tmp_path / "threads.json"
    pr_status_path.write_text(json.dumps(_pr_status()), encoding="utf-8")
    threads_path.write_text(json.dumps(_threads()), encoding="utf-8")

    payload = module.run_multi_agent_review_closure(
        artifact_dir=tmp_path / "run",
        pr_status_json=pr_status_path,
        review_threads_json=threads_path,
        pr_number=270,
    )

    assert payload["status"] == "ready_with_warnings"
    assert payload["artifact_paths"]["closure_json"].endswith("multi_agent_review_closure_v0_1.json")


def test_multi_agent_review_closure_makefile_and_docs_are_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "multi-agent-review-closure" in makefile
    assert "verify-multi-agent-review-closure" in makefile
    assert "M30" in doc
    assert "repo_github_local_artifacts_only" in doc

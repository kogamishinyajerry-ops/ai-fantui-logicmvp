from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema

from well_harness.multi_agent_release_decision_input import (
    SCHEMA_ID,
    build_multi_agent_release_decision_input,
    render_multi_agent_release_decision_input_html,
    write_multi_agent_release_decision_input_artifacts,
)
from well_harness.multi_agent_review_closure import build_multi_agent_review_closure


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_release_decision_input_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_release_decision_input.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_release_decision_input.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-release-decision-input.md"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _pr_status() -> dict:
    return {
        "number": 270,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/270",
        "state": "OPEN",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "a00b9d10e254c65e005e98ad069a4f8c3e5f1e5d",
        "statusCheckRollup": [],
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


def _thread(
    *,
    author: str,
    body: str,
    path: str,
    line: int,
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
                    "createdAt": "2026-05-28T09:06:26Z",
                    "body": body,
                    "commit": {
                        "oid": "a00b9d10e254c65e005e98ad069a4f8c3e5f1e5d",
                    },
                }
            ]
        },
    }


def _review_closure(*, actionable: bool = False, remote_checks: list[dict] | None = None) -> dict:
    pr_status = _pr_status()
    if remote_checks is not None:
        pr_status["statusCheckRollup"] = remote_checks
    threads = [
        _thread(
            author="kogamishinyajerry-ops",
            body="Fixed in 07154d0: dependency boundary repaired.",
            path="src/well_harness/requirements_intake/analysis.py",
            line=20,
        ),
        _thread(
            author="chatgpt-codex-connector",
            body="**P2 Prior issue now covered by latest clean review**",
            path="src/well_harness/multi_agent_review_closure.py",
            line=203,
        ),
    ]
    if actionable:
        pr_status["comments"] = pr_status["comments"][:1]
        threads.append(
            _thread(
                author="chatgpt-codex-connector",
                body="**P1 Current issue still actionable**",
                path="src/well_harness/multi_agent_review_closure.py",
                line=210,
            )
        )
    return build_multi_agent_review_closure(
        pr_status=pr_status,
        review_threads=threads,
        generated_at="2026-05-28T09:30:00Z",
    )


def _load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "run_multi_agent_release_decision_input",
        RUN_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_decision_input_schema_validates_ready_with_remote_check_warning() -> None:
    payload = build_multi_agent_release_decision_input(
        review_closure=_review_closure(),
        generated_at="2026-05-28T09:40:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["milestone"]["id"] == "M31"
    assert payload["status"] == "ready_for_owner_decision_with_warnings"
    assert payload["summary"]["recommended_owner_action"] == "owner_acceptance_or_wait_for_remote_checks"
    assert payload["summary"]["actionable_thread_count"] == 0
    assert payload["gates"]["latest_head_review"] == "pass"
    assert payload["gates"]["remote_checks"] == "warning"
    assert payload["decision_boundaries"]["auto_merge"] == "forbidden"
    assert payload["decision_boundaries"]["self_approval"] == "forbidden"
    assert payload["agent_team"]["team_size"] == 5

    options = {item["option_id"]: item for item in payload["decision_options"]}
    assert options["owner_acceptance"]["enabled"] is True
    assert options["wait_for_remote_checks"]["enabled"] is True
    assert options["merge_when_authorized"]["enabled"] is False
    assert {item["automation_action"] for item in payload["decision_options"]}.isdisjoint({"merge"})


def test_release_decision_input_ready_without_warning_when_remote_checks_pass() -> None:
    payload = build_multi_agent_release_decision_input(
        review_closure=_review_closure(
            remote_checks=[{"name": "validation", "conclusion": "SUCCESS"}],
        ),
        generated_at="2026-05-28T09:40:00Z",
    )

    assert payload["status"] == "ready_for_owner_decision"
    assert payload["gates"]["remote_checks"] == "pass"
    assert payload["summary"]["recommended_owner_action"] == "owner_acceptance_when_authorized"
    options = {item["option_id"]: item for item in payload["decision_options"]}
    assert options["wait_for_remote_checks"]["enabled"] is False


def test_release_decision_input_blocks_actionable_reviews() -> None:
    payload = build_multi_agent_release_decision_input(
        review_closure=_review_closure(actionable=True),
        generated_at="2026-05-28T09:40:00Z",
    )

    assert payload["status"] == "blocked"
    assert payload["gates"]["latest_head_review"] == "fail"
    assert payload["gates"]["actionable_reviews"] == "fail"
    assert payload["summary"]["recommended_owner_action"] == "fix_current_actionable_reviews"
    options = {item["option_id"]: item for item in payload["decision_options"]}
    assert options["owner_acceptance"]["enabled"] is False
    assert options["fix_actionable_reviews"]["enabled"] is True


def test_release_decision_input_html_exposes_owner_decision_surface() -> None:
    payload = build_multi_agent_release_decision_input(
        review_closure=_review_closure(),
        generated_at="2026-05-28T09:40:00Z",
    )
    html = render_multi_agent_release_decision_input_html(payload)

    assert "Multi-Agent Release Decision Input" in html
    assert "Recommended owner action" in html
    assert "Decision Options" in html
    assert "repo_github_local_artifacts_only" in html
    assert "owner_acceptance_or_wait_for_remote_checks" in html
    assert "auto_merge" in html
    assert "disabled" in html


def test_release_decision_input_writer_and_checker_round_trip(tmp_path: Path) -> None:
    payload = build_multi_agent_release_decision_input(
        review_closure=_review_closure(),
        generated_at="2026-05-28T09:40:00Z",
    )
    written = write_multi_agent_release_decision_input_artifacts(
        payload,
        artifact_dir=tmp_path / "decision",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["decision_input_json"],
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
        "package_path": written["artifact_paths"]["decision_input_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_release_decision_input_runner_uses_supplied_review_closure(tmp_path: Path) -> None:
    module = _load_runner_module()
    closure_path = tmp_path / "closure.json"
    closure_path.write_text(json.dumps(_review_closure()), encoding="utf-8")

    payload = module.run_multi_agent_release_decision_input(
        artifact_dir=tmp_path / "run",
        review_closure_path=closure_path,
        refresh_review_closure=False,
        pr_number=270,
    )

    assert payload["status"] == "ready_for_owner_decision_with_warnings"
    assert payload["artifact_paths"]["decision_input_json"].endswith(
        "multi_agent_release_decision_input_v0_1.json"
    )


def test_release_decision_input_makefile_and_docs_are_wired() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "multi-agent-release-decision-input" in makefile
    assert "verify-multi-agent-release-decision-input" in makefile
    assert "M31" in doc
    assert "repo_github_local_artifacts_only" in doc

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema

from well_harness.multi_agent_merge_readiness import (
    SCHEMA_ID,
    build_multi_agent_merge_readiness,
    render_multi_agent_merge_readiness_html,
    write_multi_agent_merge_readiness_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_merge_readiness_v0_1.schema.json"
)
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_merge_readiness.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_multi_agent_merge_readiness.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "multi-agent-merge-readiness.md"
MVP_DOC_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "multi-agent-control-logic-engineering-system-mvp.md"
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def _validation_evidence() -> dict:
    return {
        "evidence_id": "multi-agent-validation-evidence-v0.1",
        "status": "pass",
        "summary": {
            "dirty_worktree_policy": "ignore_unrelated_dirty_files_and_stage_only_listed_pathspecs",
            "executed_command_count": 21,
            "failed_command_count": 0,
            "package_count": 8,
            "passed_command_count": 21,
            "stage_command_count": 9,
            "validation_command_count": 21,
        },
        "stage_commands": [
            "git add -- src/well_harness/demo_server.py",
            "git add -- docs/coordination/multi-agent-pr-preflight.md",
            "git add -f -- .claude/agents/ultrawork-orchestrator.md",
        ],
        "excluded_paths": [
            ".github/workflows/gsd-automation.yml",
            "artifacts/**",
            "src/well_harness/controller.py",
            "src/well_harness/runner.py",
            "src/well_harness/demo_server.py",
            "src/well_harness/static/**",
            ".planning/**",
        ],
        "blockers": [],
    }


def _pr_status() -> dict:
    return {
        "number": 269,
        "url": "https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/269",
        "state": "OPEN",
        "isDraft": False,
        "mergeable": "MERGEABLE",
        "headRefOid": "3b59f9148eb95e57e72e62733397355c82ba6869",
        "statusCheckRollup": [],
        "reviews": [],
        "comments": [],
    }


def _geometry_results(tmp_path: Path) -> list[dict]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    results = []
    for page in ["ultrawork", "cockpit", "packaging", "preflight", "evidence"]:
        for viewport in ["desktop", "mobile"]:
            screenshot = tmp_path / f"{page}-{viewport}.png"
            screenshot.write_bytes(b"png")
            results.append(
                {
                    "page": page,
                    "viewport": viewport,
                    "status": "pass",
                    "missing": [],
                    "overflow_px": 0,
                    "unique_sampled_colors": 40,
                    "screenshot": str(screenshot),
                }
            )
    return results


def _load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "run_multi_agent_merge_readiness",
        RUN_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_multi_agent_merge_readiness_schema_validates_payload(tmp_path: Path) -> None:
    payload = build_multi_agent_merge_readiness(
        validation_evidence=_validation_evidence(),
        pr_status=_pr_status(),
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(payload)
    assert payload["status"] == "ready_with_warnings"
    assert payload["milestone"]["id"] == "M29"
    assert payload["summary"]["passed_command_count"] == 21
    assert payload["summary"]["remote_checks_state"] == "no_checks_reported"
    assert payload["summary"]["review_state"] == "no_reviews_or_comments"
    assert payload["agent_team"]["mode"] == "five_agent_context_cap"
    assert payload["agent_team"]["team_size"] == 5
    assert [item["name"] for item in payload["agent_team"]["active_agents"]] == [
        "ChiefEngineerOrchestrator",
        "LogicIRRepairAgent",
        "EvidenceValidationAgent",
        "SafetyRequirementsReviewer",
        "PackagingPRReadinessAgent",
    ]
    assert payload["gates"]["validation_evidence"] == "pass"
    assert payload["gates"]["remote_checks"] == "warning"
    assert payload["gates"]["review_state"] == "warning"
    assert payload["pr_status"]["mergeable"] == "MERGEABLE"


def test_multi_agent_merge_readiness_blocks_failed_remote_checks(tmp_path: Path) -> None:
    pr_status = _pr_status()
    pr_status["statusCheckRollup"] = [
        {"name": "validation", "conclusion": "FAILURE"},
    ]

    payload = build_multi_agent_merge_readiness(
        validation_evidence=_validation_evidence(),
        pr_status=pr_status,
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert payload["gates"]["remote_checks"] == "fail"
    assert payload["summary"]["remote_checks_state"] == "fail"
    assert payload["status"] == "blocked"


def test_multi_agent_merge_readiness_marks_review_feedback_as_warning(tmp_path: Path) -> None:
    pr_status = _pr_status()
    pr_status["reviews"] = [{"state": "COMMENTED"}]

    payload = build_multi_agent_merge_readiness(
        validation_evidence=_validation_evidence(),
        pr_status=pr_status,
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert payload["gates"]["review_state"] == "warning"
    assert payload["summary"]["review_state"] == "feedback_present"
    assert payload["status"] == "ready_with_warnings"


def test_multi_agent_merge_readiness_blocks_unstaged_changed_excluded_path(
    tmp_path: Path,
) -> None:
    evidence = _validation_evidence()
    evidence["changed_paths"] = ["src/well_harness/demo_server.py"]
    evidence["stage_commands"] = [
        command
        for command in evidence["stage_commands"]
        if "src/well_harness/demo_server.py" not in command
    ]

    payload = build_multi_agent_merge_readiness(
        validation_evidence=evidence,
        pr_status=_pr_status(),
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert payload["gates"]["pathspec_boundary"] == "fail"
    assert payload["status"] == "blocked"


def test_multi_agent_merge_readiness_allows_explicitly_staged_guarded_change(
    tmp_path: Path,
) -> None:
    evidence = _validation_evidence()
    evidence["changed_paths"] = ["src/well_harness/demo_server.py"]

    payload = build_multi_agent_merge_readiness(
        validation_evidence=evidence,
        pr_status=_pr_status(),
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert payload["gates"]["pathspec_boundary"] == "pass"
    assert payload["status"] == "ready_with_warnings"


def test_multi_agent_merge_readiness_html_exposes_review_handoff(tmp_path: Path) -> None:
    payload = build_multi_agent_merge_readiness(
        validation_evidence=_validation_evidence(),
        pr_status=_pr_status(),
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_multi_agent_merge_readiness_html(payload)

    assert "Multi-Agent Merge Readiness" in html
    assert "five_agent_context_cap" in html
    assert "ChiefEngineerOrchestrator" in html
    assert "PackagingPRReadinessAgent" in html
    assert "RUN-QUEUE-011" in html
    assert "21 validation commands passed" in html
    assert "repo_github_local_artifacts" in html
    assert "MERGEABLE" in html
    assert "no_checks_reported" in html


def test_multi_agent_merge_readiness_writer_and_checker_round_trip(tmp_path: Path) -> None:
    payload = build_multi_agent_merge_readiness(
        validation_evidence=_validation_evidence(),
        pr_status=_pr_status(),
        geometry_results=_geometry_results(tmp_path),
        geometry_dir=str(tmp_path),
        generated_at="2026-05-27T00:00:00Z",
    )
    written = write_multi_agent_merge_readiness_artifacts(
        payload,
        artifact_dir=tmp_path / "readiness",
    )

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--package",
            written["artifact_paths"]["readiness_json"],
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
        "package_path": written["artifact_paths"]["readiness_json"],
        "schema_valid": True,
        "status": "pass",
    }


def test_multi_agent_merge_readiness_runner_uses_supplied_evidence_and_pr_status(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_runner_module()
    evidence_path = tmp_path / "evidence.json"
    pr_status_path = tmp_path / "pr.json"
    evidence_path.write_text(json.dumps(_validation_evidence()), encoding="utf-8")
    pr_status_path.write_text(json.dumps(_pr_status()), encoding="utf-8")

    monkeypatch.setattr(module, "_ensure_source_html", lambda: None)
    monkeypatch.setattr(module, "_changed_paths_from_worktree", lambda: [])
    monkeypatch.setattr(
        module,
        "_run_geometry_gate",
        lambda geometry_dir: _geometry_results(tmp_path / "geometry"),
    )

    payload = module.run_multi_agent_merge_readiness(
        artifact_dir=tmp_path / "run",
        validation_evidence_path=evidence_path,
        geometry_dir=tmp_path / "geometry",
        pr_status_json=pr_status_path,
        pr_number=269,
    )

    assert payload["status"] == "ready_with_warnings"
    assert payload["artifact_paths"]["readiness_html"].endswith(
        "multi_agent_merge_readiness_v0_1.html"
    )
    assert Path(payload["artifact_paths"]["readiness_json"]).exists()


def test_multi_agent_merge_readiness_changed_paths_include_dirty_worktree(
    monkeypatch,
) -> None:
    module = _load_runner_module()

    class Result:
        def __init__(self, returncode: int, stdout: str = "") -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = ""

    def fake_run(command, **_kwargs):
        if command[:3] == ["git", "diff", "--name-only"]:
            return Result(0, "docs/coordination/multi-agent-merge-readiness.md\n")
        if command[:3] == ["git", "status", "--porcelain=v1"]:
            return Result(
                0,
                " M src/well_harness/demo_server.py\n"
                "A  tests/test_multi_agent_merge_readiness.py\n"
                "?? artifacts/local-screenshot.png\n",
            )
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module._changed_paths_from_pr_status({"baseRefName": "main"}) == [
        "docs/coordination/multi-agent-merge-readiness.md",
        "src/well_harness/demo_server.py",
        "tests/test_multi_agent_merge_readiness.py",
        "artifacts/local-screenshot.png",
    ]


def test_multi_agent_merge_readiness_is_wired_into_docs_and_makefile() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
    doc = DOC_PATH.read_text(encoding="utf-8")
    mvp_doc = MVP_DOC_PATH.read_text(encoding="utf-8")

    assert "MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR" in makefile
    assert "multi-agent-merge-readiness" in makefile
    assert "verify-multi-agent-merge-readiness" in makefile
    assert "scripts/run_multi_agent_merge_readiness.py --format json" in makefile
    assert "scripts/verify_multi_agent_merge_readiness.py --format json" in makefile
    assert '"Pillow>=10"' in pyproject
    assert '"playwright>=1.45"' in pyproject

    expected_pathspecs = [
        "docs/coordination/multi-agent-merge-readiness.md",
        "docs/json_schema/multi_agent_merge_readiness_v0_1.schema.json",
        "scripts/run_multi_agent_merge_readiness.py",
        "scripts/verify_multi_agent_merge_readiness.py",
        "src/well_harness/multi_agent_team.py",
        "src/well_harness/multi_agent_merge_readiness.py",
        "tests/test_multi_agent_merge_readiness.py",
    ]
    for pathspec in expected_pathspecs:
        assert pathspec in doc

    assert "repo/GitHub/local-artifact control boundary" in doc
    assert "21 validation commands" in doc
    assert "five-agent active team" in doc
    assert "M29" in mvp_doc
    assert "five-agent active team" in mvp_doc
    assert "make multi-agent-merge-readiness" in mvp_doc

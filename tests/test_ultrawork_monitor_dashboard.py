from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from pathlib import Path

import jsonschema
import pytest

from scripts import verify_ultrawork_monitor_dashboard as ultrawork_verifier
from well_harness.ultrawork_monitor_dashboard import (
    SCHEMA_ID,
    build_ultrawork_monitor_dashboard,
    render_ultrawork_dashboard_html,
)
from well_harness.multi_agent_team import ACTIVE_AGENT_NAMES, FIVE_AGENT_TEAM_MODE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "ultrawork_monitor_dashboard_v0_1.schema.json"
CURSOR_RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_multi_agent_queue_cursor_state_v0_2.py"
RUN_SCRIPT = PROJECT_ROOT / "scripts" / "run_ultrawork_monitor_dashboard.py"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_ultrawork_monitor_dashboard.py"
AGENT_DIR = PROJECT_ROOT / ".claude" / "agents"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
PATHSPEC_PACKAGE_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "ultrawork-monitor-pathspec-package.md"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _schema() -> dict:
    return _load_json(SCHEMA_PATH)


def _run_cursor(tmp_path: Path, *, resume_mode: str) -> tuple[dict, Path]:
    artifact_dir = tmp_path / f"cursor-{resume_mode}"
    result = subprocess.run(
        [
            sys.executable,
            str(CURSOR_RUN_SCRIPT),
            "--artifact-dir",
            str(artifact_dir),
            "--resume-mode",
            resume_mode,
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=420,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    return payload, Path(payload["artifact_paths"]["cursor_state"])


def test_ultrawork_dashboard_schema_validates_ready_resume_payload(tmp_path: Path) -> None:
    cursor, cursor_path = _run_cursor(tmp_path, resume_mode="ready-to-resume")
    dashboard = build_ultrawork_monitor_dashboard(
        cursor,
        source_cursor_path=str(cursor_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    assert _schema()["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(_schema()).validate(dashboard)
    assert dashboard["summary"]["status"] == "ready_to_resume"
    assert dashboard["summary"]["next_action"] == "resume_next_open_record"
    assert dashboard["selected_next_record"]["record_id"] == "RUN-QUEUE-011"
    assert dashboard["selected_next_record"]["agent"] == "LogicIRRepairAgent"
    assert dashboard["agent_team"]["mode"] == FIVE_AGENT_TEAM_MODE
    assert dashboard["agent_team"]["team_size"] == 5
    assert len(dashboard["agent_team"]["active_agents"]) == 5
    assert {lane["agent"] for lane in dashboard["agent_lanes"]}.issubset(ACTIVE_AGENT_NAMES)
    assert "EvidenceRepairAgent" not in {lane["agent"] for lane in dashboard["agent_lanes"]}
    assert "RequirementRepairAgent" not in {lane["agent"] for lane in dashboard["agent_lanes"]}
    assert "SimulationTestAgent" not in {lane["agent"] for lane in dashboard["agent_lanes"]}
    assert dashboard["blockers"] == []


def test_ultrawork_dashboard_schema_validates_idle_payload(tmp_path: Path) -> None:
    cursor, cursor_path = _run_cursor(tmp_path, resume_mode="idle")
    dashboard = build_ultrawork_monitor_dashboard(
        cursor,
        source_cursor_path=str(cursor_path),
        generated_at="2026-05-27T00:00:00Z",
    )

    jsonschema.Draft202012Validator(_schema()).validate(dashboard)
    assert dashboard["summary"]["status"] == "idle"
    assert dashboard["summary"]["next_action"] == "wait_for_append_only_queue_growth"
    assert dashboard["summary"]["completed_count"] == 11
    assert dashboard["summary"]["open_approved_count"] == 0
    assert all(not lane["needs_operator_action"] for lane in dashboard["agent_lanes"])


def test_ultrawork_dashboard_html_exposes_lanes_gates_and_blockers(tmp_path: Path) -> None:
    cursor, cursor_path = _run_cursor(tmp_path, resume_mode="ready-to-resume")
    dashboard = build_ultrawork_monitor_dashboard(
        cursor,
        source_cursor_path=str(cursor_path),
        generated_at="2026-05-27T00:00:00Z",
    )
    html = render_ultrawork_dashboard_html(dashboard)

    assert "UltraWork Monitor" in html
    assert "five_agent_context_cap" in html
    assert "ChiefEngineerOrchestrator" in html
    assert "PackagingPRReadinessAgent" in html
    assert "RUN-QUEUE-011" in html
    assert "LogicIRRepairAgent" in html
    assert "No active blockers" in html
    assert "source_ledger_checker" in html
    assert 'class="table-scroll"' in html


def test_ultrawork_dashboard_runner_and_checker_round_trip(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT),
            "--cursor",
            str(_run_cursor(tmp_path, resume_mode="ready-to-resume")[1]),
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
        timeout=60,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["artifact_paths"]["dashboard_json"] == str(
        tmp_path / "ultrawork_monitor_dashboard_v0_1.json"
    )
    assert Path(payload["artifact_paths"]["dashboard_html"]).exists()

    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--dashboard",
            payload["artifact_paths"]["dashboard_json"],
            "--format",
            "json",
            "--skip-browser",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert verify_result.returncode == 0, verify_result.stderr
    verify_payload = json.loads(verify_result.stdout)
    assert verify_payload["status"] == "pass"
    assert verify_payload["schema_valid"] is True
    assert verify_payload["html_exists"] is True
    assert verify_payload["browser_valid"] is False
    assert verify_payload["browser"]["status"] == "skipped"
    assert verify_payload["mismatches"] == []


def test_ultrawork_browser_gate_reports_chromium_launch_failure(monkeypatch, tmp_path: Path) -> None:
    class BrokenPlaywright:
        def __enter__(self):
            chromium = types.SimpleNamespace(
                launch=lambda: (_ for _ in ()).throw(RuntimeError("missing chromium")),
            )
            return types.SimpleNamespace(chromium=chromium)

        def __exit__(self, *exc_info):
            return False

    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = lambda: BrokenPlaywright()
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)

    result = ultrawork_verifier._browser_state(
        tmp_path / "ultrawork_monitor_dashboard_v0_1.html",
        tmp_path / "screenshots",
        expected_lane_count=0,
    )

    assert result["status"] == "fail"
    assert result["screenshots"] == {}
    assert result["states"] == {}
    assert result["mismatches"] == ["chromium launch failed: missing chromium"]


@pytest.mark.e2e
def test_ultrawork_dashboard_browser_gate_captures_geometry(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT),
            "--cursor",
            str(_run_cursor(tmp_path, resume_mode="ready-to-resume")[1]),
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
        timeout=60,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    verify_result = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--dashboard",
            payload["artifact_paths"]["dashboard_json"],
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert verify_result.returncode == 0, verify_result.stderr
    verify_payload = json.loads(verify_result.stdout)
    assert verify_payload["status"] == "pass"
    assert verify_payload["browser_valid"] is True
    assert verify_payload["mismatches"] == []
    browser = verify_payload["browser"]
    assert browser["status"] == "pass"
    assert Path(browser["screenshots"]["desktop"]).exists()
    assert Path(browser["screenshots"]["mobile"]).exists()
    assert browser["states"]["desktop"]["noHorizontalOverflow"] is True
    assert browser["states"]["mobile"]["noHorizontalOverflow"] is True
    assert browser["states"]["desktop"]["requiredTextPresent"] is True
    assert browser["states"]["mobile"]["requiredTextPresent"] is True
    assert browser["states"]["desktop"]["agentRowCount"] == 5
    assert browser["states"]["mobile"]["agentRowCount"] == 5
    assert any(
        item["hasInternalOverflow"]
        for item in browser["states"]["mobile"]["scrollContainers"]
    )


def test_ultrawork_monitor_local_entry_and_pathspec_package_are_bounded() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    package = PATHSPEC_PACKAGE_PATH.read_text(encoding="utf-8")

    assert "ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR" in makefile
    assert "ultrawork-monitor-dashboard" in makefile
    assert "verify-ultrawork-monitor-dashboard" in makefile
    assert "scripts/run_ultrawork_monitor_dashboard.py --resume-mode ready-to-resume" in makefile
    assert "scripts/verify_ultrawork_monitor_dashboard.py --format json" in makefile
    assert "ultrawork_monitor_dashboard_v0_1.html" in makefile
    verifier = VERIFY_SCRIPT.read_text(encoding="utf-8")
    assert "browser_valid" in verifier
    assert "noHorizontalOverflow" in verifier

    expected_pathspecs = [
        "Makefile",
        "docs/coordination/ultrawork-monitor-pathspec-package.md",
        "docs/json_schema/ultrawork_monitor_dashboard_v0_1.schema.json",
        "scripts/run_ultrawork_monitor_dashboard.py",
        "scripts/verify_ultrawork_monitor_dashboard.py",
        "src/well_harness/multi_agent_team.py",
        "src/well_harness/ultrawork_monitor_dashboard.py",
        "tests/test_ultrawork_monitor_dashboard.py",
        ".claude/agents/ultrawork-orchestrator.md",
        ".claude/agents/ultrawork-logic-ir-agent.md",
        ".claude/agents/ultrawork-evidence-reviewer.md",
    ]
    for pathspec in expected_pathspecs:
        assert pathspec in package

    assert "git add -f --" in package
    assert "src/well_harness/controller.py" in package
    assert "src/well_harness/demo_server.py" in package
    assert "src/well_harness/static/**" in package
    assert ".planning/**" in package
    assert "Repo, GitHub, and local artifacts are the active control surfaces" in package
    assert "five-agent active team" in package


def test_project_claude_code_subagents_define_ultrawork_team() -> None:
    expected = {
        "ultrawork-orchestrator.md",
        "ultrawork-logic-ir-agent.md",
        "ultrawork-evidence-reviewer.md",
    }
    actual = {path.name for path in AGENT_DIR.glob("ultrawork-*.md")}

    assert expected.issubset(actual)
    for name in expected:
        text = (AGENT_DIR / name).read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "name:" in text
        assert "description:" in text
        assert "controller.py" in text
        assert "Do not modify" in text

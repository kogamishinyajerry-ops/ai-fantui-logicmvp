from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_customer_demo_mvp_closeout.py"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "customer-demo-mvp-closeout.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _load_closeout_runner_module():
    spec = importlib.util.spec_from_file_location(
        "customer_demo_mvp_closeout_runner",
        RUN_SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_customer_demo_mvp_closeout_boundary_checks_pr_base(monkeypatch) -> None:
    runner = _load_closeout_runner_module()
    restricted_path = "src/well_harness/static/requirements_intake/index.html"
    calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if "origin/codex/multi-agent-active-route-wiring...HEAD" in args:
            return subprocess.CompletedProcess(args, 0, restricted_path + "\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setenv("GITHUB_BASE_REF", "codex/multi-agent-active-route-wiring")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    assert runner._restricted_diff() == [restricted_path]
    assert any(
        "origin/codex/multi-agent-active-route-wiring...HEAD" in args
        for args in calls
    )


def test_customer_demo_mvp_closeout_fetches_missing_pr_base(monkeypatch) -> None:
    runner = _load_closeout_runner_module()
    restricted_path = "src/well_harness/static/requirements_intake/index.html"
    calls: list[list[str]] = []
    origin_diff_attempts = 0

    def fake_run(args, **kwargs):
        nonlocal origin_diff_attempts
        calls.append(args)
        if args[:3] == ["git", "diff", "--name-only"]:
            if "origin/codex/multi-agent-active-route-wiring...HEAD" in args:
                origin_diff_attempts += 1
                if origin_diff_attempts == 1:
                    return subprocess.CompletedProcess(args, 128, "", "fatal: bad revision")
                return subprocess.CompletedProcess(args, 0, restricted_path + "\n", "")
            if any(str(arg).endswith("...HEAD") for arg in args):
                return subprocess.CompletedProcess(args, 128, "", "fatal: bad revision")
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:4] == ["git", "fetch", "--quiet", "origin"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setenv("GITHUB_BASE_REF", "codex/multi-agent-active-route-wiring")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    assert runner._restricted_diff() == [restricted_path]
    assert [
        "git",
        "fetch",
        "--quiet",
        "origin",
        "codex/multi-agent-active-route-wiring:refs/remotes/origin/codex/multi-agent-active-route-wiring",
    ] in calls
    assert origin_diff_attempts == 2


def test_customer_demo_mvp_closeout_combines_visibility_and_demo_gates(
    tmp_path: Path,
) -> None:
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
        timeout=420,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-customer-demo-mvp-closeout"
    assert payload["status"] == "pass"
    assert payload["closeout_status"] == "ready_for_project_owner_acceptance"
    assert payload["demo_surface"] == {
        "route": "/demo-reconstruction",
        "title": "demo.html 复刻 MVP 控制台",
        "node_count": 20,
        "wire_count": 23,
    }
    assert payload["deterministic_gates"] == {
        "project_visibility_mvp_gate": "pass",
        "phase1_demo_mvp_gate": "pass",
        "phase1_gate_summary_verification": "pass",
        "m21_c919_pure_canvas_gate": "pass",
        "m21_demo_fanout_pure_canvas_gate": "pass",
        "m21_pure_canvas_acceptance": "pass",
        "m21_c919_natural_language_workbench_gate": "pass",
        "m21_demo_natural_language_workbench_gate": "pass",
        "m21_natural_language_workbench_acceptance": "pass",
        "m21_c919_natural_language_step_confirmation_gate": "pass",
        "m21_demo_natural_language_step_confirmation_gate": "pass",
        "m21_natural_language_step_confirmation_acceptance": "pass",
        "closeout_doc": "pass",
        "demo_surface": "pass",
        "embedded_light_demo": "pass",
        "screenshots": "pass",
        "boundary": "pass",
        "local_gate": "pass",
    }
    assert payload["mismatches"] == []
    assert payload["entrypoints"]["project_visibility_gate"] == (
        "make project-visibility-mvp-gate"
    )
    assert payload["entrypoints"]["phase1_demo_gate"] == "make phase1-demo-mvp-gate"
    assert payload["entrypoints"]["closeout_gate"] == "make customer-demo-mvp-closeout"
    assert payload["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["visual_evidence"]["embedded_codex_light_palette"] == "pass"
    assert payload["visual_evidence"]["embedded_palette"]["palette"] == "codex-light"
    assert payload["visual_evidence"]["embedded_palette"]["body_background"] == "rgb(247, 248, 251)"
    assert payload["visual_evidence"]["m21_natural_language_workbench_acceptance"] == "pass"
    natural_language = payload["m21_natural_language_workbench"]
    assert natural_language["c919_fanout"]["natural_language_workbench_contract"] == "pass"
    assert natural_language["demo_fanout"]["natural_language_workbench_contract"] == "pass"
    assert natural_language["c919_fanout"]["visible_button_count"] <= 3
    assert natural_language["demo_fanout"]["visible_button_count"] <= 3
    assert natural_language["c919_fanout"]["input_visible"] is True
    assert natural_language["demo_fanout"]["input_visible"] is True
    assert natural_language["c919_fanout"]["command_trigger_display"] == "none"
    assert natural_language["demo_fanout"]["command_trigger_display"] == "none"
    step = payload["m21_natural_language_step_confirmation"]
    assert step["c919_fanout"]["natural_language_streamed_confirmation_contract"] == "pass"
    assert step["demo_fanout"]["natural_language_streamed_confirmation_contract"] == "pass"
    assert step["c919_fanout"]["one_candidate_per_natural_language_submit_contract"] == "pass"
    assert step["demo_fanout"]["one_candidate_per_natural_language_submit_contract"] == "pass"
    assert step["c919_fanout"]["feedback_revision_frontstage_contract"] == "pass"
    assert step["demo_fanout"]["feedback_revision_frontstage_contract"] == "pass"
    assert step["c919_fanout"]["feedback_revision_confirmation_screenshot"] == "pass"
    assert step["demo_fanout"]["feedback_revision_confirmation_screenshot"] == "pass"
    assert step["c919_fanout"]["natural_language_step_visual_framing_contract"] == "pass"
    assert step["demo_fanout"]["natural_language_step_visual_framing_contract"] == "pass"
    assert step["c919_fanout"]["launch_source"] == "natural-language"
    assert step["demo_fanout"]["launch_source"] == "natural-language"
    assert step["c919_fanout"]["highlight_count"] > 0
    assert step["demo_fanout"]["highlight_count"] > 0
    assert step["c919_fanout"]["canvas_height_after_submit"] >= 420
    assert step["demo_fanout"]["canvas_height_after_submit"] >= 420
    assert step["c919_fanout"]["active_target_visible_in_canvas"] is True
    assert step["demo_fanout"]["active_target_visible_in_canvas"] is True
    assert step["c919_fanout"]["active_target_hit_test_visible"] is True
    assert step["demo_fanout"]["active_target_hit_test_visible"] is True
    assert step["c919_fanout"]["feedback_revision_matches"] is True
    assert step["demo_fanout"]["feedback_revision_matches"] is True
    assert step["c919_fanout"]["feedback_revision_replay_event_count"] == 1
    assert step["demo_fanout"]["feedback_revision_replay_event_count"] == 1
    assert step["c919_fanout"]["step_screenshot_clip"]["height"] <= 620
    assert step["demo_fanout"]["step_screenshot_clip"]["height"] <= 620
    assert Path(step["c919_fanout"]["step_confirmation_screenshot"]).exists()
    assert Path(step["demo_fanout"]["step_confirmation_screenshot"]).exists()
    assert Path(step["c919_fanout"]["revision_confirmation_screenshot"]).exists()
    assert Path(step["demo_fanout"]["revision_confirmation_screenshot"]).exists()

    closeout_summary = Path(payload["artifact_paths"]["closeout_summary"])
    closeout_markdown = Path(payload["artifact_paths"]["closeout_markdown"])
    embedded_light_demo = Path(payload["artifact_paths"]["embedded_light_demo_screenshot"])
    project_visibility_acceptance = Path(
        payload["artifact_paths"]["project_visibility_acceptance"]
    )
    phase1_gate_summary = Path(payload["artifact_paths"]["phase1_gate_summary"])
    phase1_release_summary = Path(payload["artifact_paths"]["phase1_release_summary"])
    assert closeout_summary.exists()
    assert closeout_markdown.exists()
    assert embedded_light_demo.exists()
    assert project_visibility_acceptance.exists()
    assert phase1_gate_summary.exists()
    assert phase1_release_summary.exists()
    assert len(payload["artifact_paths"]["screenshots"]) >= 2
    assert any("natural-language-step" in path for path in payload["artifact_paths"]["screenshots"])
    assert any("feedback-revision" in path for path in payload["artifact_paths"]["screenshots"])
    for screenshot in payload["artifact_paths"]["screenshots"]:
        path = Path(screenshot)
        assert path.exists()
        assert path.stat().st_size > 0
    assert "ready_for_project_owner_acceptance" in closeout_markdown.read_text(
        encoding="utf-8"
    )
    assert "embedded_codex_light_palette" in closeout_markdown.read_text(
        encoding="utf-8"
    )
    assert "natural_language_workbench_contract" in closeout_markdown.read_text(
        encoding="utf-8"
    )


def test_customer_demo_mvp_closeout_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Customer Demo MVP Closeout" in doc
    assert "make customer-demo-mvp-closeout" in doc
    assert "make project-visibility-mvp-gate" in doc
    assert "make phase1-demo-mvp-gate" in doc
    assert "M21 Natural Language Workbench Evidence" in doc
    assert "natural_language_workbench_contract" in doc
    assert "ready_for_project_owner_acceptance" in doc
    assert "/demo-reconstruction" in doc
    assert "CUSTOMER_DEMO_MVP_CLOSEOUT_ARTIFACT_DIR" in makefile
    assert "customer-demo-mvp-closeout" in makefile
    assert "scripts/run_customer_demo_mvp_closeout.py --format json" in makefile

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from well_harness.thrust_reverser_docx_sentence_map import (
    build_thrust_reverser_docx_sentence_circuit_map,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "demo_html_reconstruction_mvp_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "demo_html_reconstruction_mvp_v0_1.json"
)
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_demo_html_reconstruction_mvp.py"
BROWSER_CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_demo_html_reconstruction_browser_acceptance.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "demo_html_reconstruction_mvp_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_demo_html_reconstruction_mvp_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-demo-html-reconstruction-mvp"
    assert fixture["mvp_id"] == "demo-html-reconstruction-mvp-v0.1"
    assert fixture["golden_reference"]["route"] == "/demo.html"
    assert fixture["replica_surface"]["route"] == "/demo-reconstruction"
    assert fixture["replica_surface"]["surface_role"] == "mvp_reconstruction_console_surface"
    assert fixture["homepage_entry"] == {
        "route": "/demo-reconstruction",
        "element_id": "home-first-phase-demo-entry",
        "priority": "first_phase_mvp",
        "label": "打开复刻控制台",
    }
    assert fixture["contract"]["expected_node_count"] == 20
    assert fixture["contract"]["expected_wire_count"] == 23
    assert fixture["contract"]["expected_preset_count"] == 5
    assert fixture["contract"]["expected_status_output_count"] == 6
    assert fixture["contract"]["expected_output_card_count"] == 4
    assert fixture["review_boundaries"] == {
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "truth_effect": "none",
        "certification_claim": "none",
    }


def test_demo_html_reconstruction_mvp_checker_converges() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["schema_valid"] is True
    assert payload["fixture_match"] is True
    assert payload["deterministic_gates"] == {
        "golden_demo_contract": "pass",
        "replica_surface_contract": "pass",
        "homepage_entry": "pass",
        "logic_builder_bridge": "pass",
        "local_routes": "pass",
        "boundary": "pass",
    }
    assert payload["observed"]["golden_demo"]["node_count"] == 20
    assert payload["observed"]["golden_demo"]["wire_count"] == 23
    assert payload["observed"]["replica_surface"]["claimed_node_count"] == "20/20"
    assert payload["observed"]["replica_surface"]["claimed_wire_count"] == "23/23"
    assert payload["observed"]["homepage_entry"] == {
        "entry_present": True,
        "route": "/demo-reconstruction",
        "priority": "first_phase_mvp",
        "label": "打开复刻控制台",
        "appears_before_default_mode_grid": True,
    }
    assert payload["observed"]["logic_builder_bridge"]["target_route"] == "/demo-reconstruction"
    assert payload["observed"]["routes"]["demo_html_status"] == 200
    assert payload["observed"]["routes"]["demo_reconstruction_status"] == 200
    assert payload["review_boundaries"]["controller_truth_modified"] is False
    assert payload["review_boundaries"]["ui_layout_modified"] is False


def test_demo_reconstruction_route_is_main_mvp_console_not_comparison_page() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "index.html"
    ).read_text(encoding="utf-8")
    stylesheet = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.css"
    ).read_text(encoding="utf-8")
    script = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.js"
    ).read_text(encoding="utf-8")

    assert 'data-ux-page-role="demo-mvp-console"' in html
    assert 'data-demo-mvp-console="true"' in html
    assert 'id="demo-reconstruction-console-frame"' in html
    assert 'src="/demo.html?embed=1&amp;palette=codex-light"' in html
    assert 'id="demo-reconstruction-browser-evidence"' in html
    assert 'id="demo-reconstruction-docx-circuit-map"' in html
    assert 'data-source-docx-circuit-map="true"' in html
    assert "uploads/20260409-thrust-reverser-control-logic.docx" in html
    assert "demo.html 复刻 MVP 控制台" in html
    assert "原始 DOCX 逐句到完整电路" in html
    assert "<h2>原版 demo.html</h2>" not in html
    assert "<h2>当前复刻</h2>" not in html
    assert "demo-reconstruction-comparison-table" not in html
    assert "demo-reconstruction-compare-grid" not in html
    assert "DeepSeek live replay" not in script
    assert "读取 golden demo 控制台" in script
    assert "DOCX_SENTENCE_CIRCUIT_ENDPOINT" in script
    assert "/api/demo-reconstruction/docx-sentence-circuit-map" in script
    assert ".demo-reconstruction-console-stage" in stylesheet
    assert "#demo-reconstruction-console-frame" in stylesheet
    assert ".demo-reconstruction-source-map" in stylesheet


def test_demo_reconstruction_mvp_console_has_first_screen_operator_guide() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "index.html"
    ).read_text(encoding="utf-8")
    stylesheet = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.css"
    ).read_text(encoding="utf-8")

    assert 'id="demo-reconstruction-operator-guide"' in html
    assert 'data-demo-mvp-guide="first-screen"' in html
    assert "选择预设" in html
    assert "查看 HUD" in html
    assert "核对输出" in html
    assert ".demo-reconstruction-operator-guide" in stylesheet
    assert ".demo-reconstruction-guide-step" in stylesheet


def test_demo_reconstruction_docx_sentence_map_covers_complete_demo_circuit() -> None:
    payload = build_thrust_reverser_docx_sentence_circuit_map()
    entries = {entry["anchor"]: entry for entry in payload["source_entries"]}
    sequence_steps = {step["anchor"]: step for step in payload["sequence_steps"]}

    assert payload["kind"] == "ai-fantui-thrust-reverser-docx-sentence-circuit-map"
    assert payload["source"]["path"] == "uploads/20260409-thrust-reverser-control-logic.docx"
    assert payload["source"]["paragraph_count"] == 45
    assert payload["source"]["table_count"] == 2
    assert payload["source"]["table_row_count"] == 17
    assert payload["circuit_contract"]["source"] == "src/well_harness/static/demo.html#fan-chain-svg"
    assert payload["circuit_contract"]["node_count"] == 20
    assert payload["circuit_contract"]["wire_count"] == 23
    assert payload["coverage"]["covered_node_count"] == 20
    assert payload["coverage"]["covered_wire_count"] == 23
    assert payload["coverage"]["complete_demo_contract"] is True
    assert entries["P035"]["role"] == "动作顺序"
    assert "油门台内微动开关1" in entries["P035"]["text"]
    assert "工作逻辑1" in entries["P036"]["text"]
    assert "油门杆解析角度≤-11.74°" in entries["P041"]["text"]
    assert "故障注入目前暂时不考虑" in entries["P045"]["text"]
    assert "wire_logic4_thr_lock" in sequence_steps["P035-S05"]["wire_ids"]
    assert "wire_vdt90_logic4" in sequence_steps["P035-S05"]["wire_ids"]
    assert "thr_lock" in sequence_steps["P035-S05"]["node_ids"]


@pytest.mark.e2e
def test_demo_html_reconstruction_browser_acceptance_script_captures_interaction_evidence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BROWSER_CHECKER_SCRIPT_PATH),
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
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["route"] == "/demo-reconstruction"
    assert payload["screenshots"]["first_screen"].endswith(".png")
    assert payload["screenshots"]["chain_svg"].endswith(".png")
    assert payload["screenshots"]["max_reverse_outputs"].endswith(".png")
    assert payload["screenshots"]["inhibit_block_outputs"].endswith(".png")
    assert payload["pixel_visibility"]["chain_svg"]["status"] == "pass"
    assert payload["pixel_visibility"]["chain_svg"]["node_count"] == 20
    assert payload["pixel_visibility"]["chain_svg"]["wire_count"] == 23
    assert payload["first_screen_review"] == {
        "operator_guide_visible": True,
        "console_frame_visible": True,
        "evidence_rail_visible": True,
    }
    assert payload["embedded_palette"]["html_class"] is True
    assert payload["embedded_palette"]["palette"] == "codex-light"
    assert payload["embedded_palette"]["body_background"] == "rgb(247, 248, 251)"
    assert payload["embedded_palette"]["panel_background"] == "rgb(255, 255, 255)"
    assert payload["interactions"]["max-reverse"]["status_badge"] == "DEPLOYED"
    assert payload["interactions"]["max-reverse"]["hud_thr_lock"] == "RELEASED"
    assert payload["interactions"]["max-reverse"]["outputs"]["thr_lock"] == "ON"
    assert payload["interactions"]["inhibit-block"]["status_badge"] == "FAULT"
    assert payload["interactions"]["inhibit-block"]["outputs"]["thr_lock"] != "ON"
    assert payload["deterministic_gates"] == {
        "browser_boot": "pass",
        "screenshots": "pass",
        "first_screen_operator_guide": "pass",
        "embedded_codex_light_palette": "pass",
        "node_wire_pixels": "pass",
        "preset_interactions": "pass",
        "hud_output_linkage": "pass",
        "boundary": "pass",
    }


def test_demo_html_reconstruction_mvp_checker_rejects_fixture_drift(tmp_path: Path) -> None:
    drifted_fixture = tmp_path / "demo_html_reconstruction_mvp_v0_1.json"
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture["contract"]["expected_node_count"] = 21
    drifted_fixture.write_text(json.dumps(fixture), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--fixture",
            str(drifted_fixture),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["schema_valid"] is True
    assert payload["fixture_match"] is False
    assert "golden_demo.node_count" in payload["mismatches"]


def test_demo_html_reconstruction_mvp_gate_is_wired_into_make_and_ci() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    workflow = GSD_AUTOMATION_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "demo-html-reconstruction-mvp" in makefile
    assert "demo-html-reconstruction-browser-acceptance" in makefile
    assert "scripts/verify_demo_html_reconstruction_mvp.py --format json" in makefile
    assert "scripts/verify_demo_html_reconstruction_browser_acceptance.py --format json" in makefile
    assert "test: demo-html-reconstruction-mvp" in makefile
    assert "Verify demo.html reconstruction MVP" in workflow
    assert "scripts/verify_demo_html_reconstruction_mvp.py --format json" in workflow

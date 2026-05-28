from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_project_owner_acceptance_review_packet.py"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-owner-acceptance-review-packet.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_project_owner_acceptance_review_packet_is_ready_for_three_way_decision(
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
        timeout=540,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-project-owner-acceptance-review-packet"
    assert payload["status"] == "pass"
    assert payload["packet_status"] == "ready_for_project_owner_decision"
    assert payload["decision_required"] == (
        "Select exactly one: accept, external_review, or demo_polish."
    )
    assert [option["id"] for option in payload["decision_options"]] == [
        "accept",
        "external_review",
        "demo_polish",
    ]
    assert [option["label"] for option in payload["decision_options"]] == [
        "接受",
        "外部 review",
        "返回 demo polish",
    ]
    assert payload["source_closeout"]["closeout_status"] == (
        "ready_for_project_owner_acceptance"
    )
    assert payload["source_closeout"]["demo_route"] == "/demo-reconstruction"
    assert payload["source_closeout"]["node_count"] == 20
    assert payload["source_closeout"]["wire_count"] == 23
    assert payload["deterministic_gates"] == {
        "customer_demo_mvp_closeout": "pass",
        "packet_doc": "pass",
        "packet_artifacts": "pass",
        "logic_circuit_diagram": "pass",
        "m21_pure_canvas_evidence": "pass",
        "m21_natural_language_workbench_evidence": "pass",
        "m21_natural_language_step_confirmation_evidence": "pass",
        "embedded_light_demo": "pass",
        "screenshots": "pass",
        "non_claim_boundaries": "pass",
        "decision_options": "pass",
        "local_gate": "pass",
    }
    assert payload["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert "no controller truth promotion" in payload["non_claims"]
    assert payload["mismatches"] == []

    packet_json = Path(payload["packet_contents"]["packet_json"])
    packet_markdown = Path(payload["packet_contents"]["packet_markdown"])
    closeout_json = Path(payload["packet_contents"]["closeout_json"])
    closeout_markdown = Path(payload["packet_contents"]["closeout_markdown"])
    project_status_html = Path(payload["packet_contents"]["project_status_html"])
    logic_circuit = payload["packet_contents"]["logic_circuit_diagram"]
    embedded_light_demo = payload["packet_contents"]["embedded_light_demo"]
    natural_language = payload["packet_contents"]["m21_natural_language_workbench_evidence"]
    step_confirmation = payload["packet_contents"]["m21_natural_language_step_confirmation_evidence"]
    assert packet_json.exists()
    assert packet_markdown.exists()
    assert closeout_json.exists()
    assert closeout_markdown.exists()
    assert project_status_html.exists()
    assert logic_circuit["claim"] == "demo cockpit logic circuit diagram evidence"
    assert logic_circuit["node_count"] == 20
    assert logic_circuit["wire_count"] == 23
    assert Path(logic_circuit["screenshot"]).exists()
    assert embedded_light_demo["embedded_codex_light_palette"] == "pass"
    assert embedded_light_demo["embedded_palette"]["palette"] == "codex-light"
    assert Path(embedded_light_demo["screenshot"]).exists()
    assert natural_language["c919_fanout"]["natural_language_workbench_contract"] == "pass"
    assert natural_language["demo_fanout"]["natural_language_workbench_contract"] == "pass"
    assert natural_language["c919_fanout"]["visible_button_count"] <= 3
    assert natural_language["demo_fanout"]["visible_button_count"] <= 3
    assert natural_language["c919_fanout"]["command_trigger_display"] == "none"
    assert natural_language["demo_fanout"]["command_trigger_display"] == "none"
    assert step_confirmation["c919_fanout"]["natural_language_streamed_confirmation_contract"] == "pass"
    assert step_confirmation["demo_fanout"]["natural_language_streamed_confirmation_contract"] == "pass"
    assert step_confirmation["c919_fanout"]["one_candidate_per_natural_language_submit_contract"] == "pass"
    assert step_confirmation["demo_fanout"]["one_candidate_per_natural_language_submit_contract"] == "pass"
    assert step_confirmation["c919_fanout"]["feedback_revision_frontstage_contract"] == "pass"
    assert step_confirmation["demo_fanout"]["feedback_revision_frontstage_contract"] == "pass"
    assert step_confirmation["c919_fanout"]["feedback_revision_confirmation_screenshot"] == "pass"
    assert step_confirmation["demo_fanout"]["feedback_revision_confirmation_screenshot"] == "pass"
    assert step_confirmation["c919_fanout"]["natural_language_step_visual_framing_contract"] == "pass"
    assert step_confirmation["demo_fanout"]["natural_language_step_visual_framing_contract"] == "pass"
    assert step_confirmation["c919_fanout"]["launch_source"] == "natural-language"
    assert step_confirmation["demo_fanout"]["launch_source"] == "natural-language"
    assert step_confirmation["c919_fanout"]["canvas_height_after_submit"] >= 420
    assert step_confirmation["demo_fanout"]["canvas_height_after_submit"] >= 420
    assert step_confirmation["c919_fanout"]["active_target_visible_in_canvas"] is True
    assert step_confirmation["demo_fanout"]["active_target_visible_in_canvas"] is True
    assert step_confirmation["c919_fanout"]["active_target_hit_test_visible"] is True
    assert step_confirmation["demo_fanout"]["active_target_hit_test_visible"] is True
    assert step_confirmation["c919_fanout"]["feedback_revision_matches"] is True
    assert step_confirmation["demo_fanout"]["feedback_revision_matches"] is True
    assert Path(step_confirmation["c919_fanout"]["packet_screenshot"]).exists()
    assert Path(step_confirmation["demo_fanout"]["packet_screenshot"]).exists()
    assert Path(step_confirmation["c919_fanout"]["packet_revision_screenshot"]).exists()
    assert Path(step_confirmation["demo_fanout"]["packet_revision_screenshot"]).exists()
    assert "Project Manager Status Summary" in project_status_html.read_text(
        encoding="utf-8"
    )

    screenshots = payload["packet_contents"]["screenshots"]
    assert any(item["role"] == "project-status" for item in screenshots)
    assert any(item["role"] == "demo-first-screen" for item in screenshots)
    assert any(item["role"] == "m21-c919-natural-language-step" for item in screenshots)
    assert any(item["role"] == "m21-demo-natural-language-step" for item in screenshots)
    assert any(item["role"] == "m21-c919-feedback-revision" for item in screenshots)
    assert any(item["role"] == "m21-demo-feedback-revision" for item in screenshots)
    for item in screenshots:
        packet_path = Path(item["packet_path"])
        assert packet_path.exists()
        assert packet_path.stat().st_size > 0

    markdown = packet_markdown.read_text(encoding="utf-8")
    assert "Project Owner Acceptance Review Packet" in markdown
    assert "## Logic Circuit Diagram" in markdown
    assert "## M21 Natural Language Workbench Evidence" in markdown
    assert "## Embedded Demo Light Evidence" in markdown
    assert "natural_language_workbench_contract" in markdown
    assert "embedded_codex_light_palette" in markdown
    assert "20" in markdown
    assert "23" in markdown
    assert "`accept_customer_demo_mvp_candidate`" in markdown
    assert "`request_external_review_before_acceptance`" in markdown
    assert "`return_to_demo_polish`" in markdown
    assert "Do not continue M21 queue expansion" in markdown


def test_project_owner_acceptance_review_packet_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Project Owner Acceptance Review Packet" in doc
    assert "make project-owner-acceptance-review-packet" in doc
    assert "ready_for_project_owner_acceptance" in doc
    assert "logic circuit diagram screenshot" in doc
    assert "20 nodes / 23 wires" in doc
    assert "M21 Natural Language Workbench Evidence" in doc
    assert "natural_language_workbench_contract" in doc
    assert "Accept" in doc
    assert "External review" in doc
    assert "Demo polish" in doc
    assert "PROJECT_OWNER_ACCEPTANCE_REVIEW_PACKET_ARTIFACT_DIR" in makefile
    assert "project-owner-acceptance-review-packet" in makefile
    assert "scripts/run_project_owner_acceptance_review_packet.py --format json" in makefile

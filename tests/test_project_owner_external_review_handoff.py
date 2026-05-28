from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_project_owner_external_review_handoff.py"
)
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-owner-external-review-handoff.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_project_owner_external_review_handoff_is_ready_for_read_only_review(
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
        timeout=600,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-project-owner-external-review-handoff"
    assert payload["status"] == "pass"
    assert payload["handoff_status"] == "ready_for_read_only_external_review"
    assert payload["review_mode"] == "read_only"
    assert payload["source_packet_status"] == "ready_for_project_owner_decision"
    assert "accept_evidence" in payload["decision_request"]
    assert "needs_changes" in payload["decision_request"]
    assert "reject_evidence" in payload["decision_request"]
    assert payload["deterministic_gates"] == {
        "project_owner_packet": "pass",
        "logic_circuit_diagram": "pass",
        "required_artifacts": "pass",
        "review_prompt": "pass",
        "handoff_doc": "pass",
        "boundary": "pass",
        "local_gate": "pass",
    }
    assert payload["review_boundaries"] == {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["mismatches"] == []

    required_ids = [item["id"] for item in payload["required_reading"]]
    assert required_ids == [
        "project_owner_packet_json",
        "project_owner_packet_markdown",
        "customer_demo_closeout_json",
        "customer_demo_closeout_markdown",
        "project_status_html",
        "logic_circuit_diagram_screenshot",
        "demo_first_screen_screenshot",
    ]
    for item in payload["required_reading"]:
        assert Path(item["path"]).exists(), item

    assert payload["expected_review_output"] == {
        "kind": "ai-fantui-project-owner-external-review-result",
        "review_mode": "read_only",
        "verdict": "accept_evidence | needs_changes | reject_evidence",
        "blocking_findings": [],
        "non_blocking_findings": [],
        "boundary_assessment": "",
        "next_decision_recommendation": "accept | external_review | demo_polish",
        "reviewed_artifacts": [
            {
                "id": "<required_reading.id>",
                "path": "<required_reading.path>",
                "status": "reviewed",
            }
        ],
        "boundary_claims": {
            "certification_claim": "none",
            "controller_truth_promotion": False,
            "production_readiness": False,
            "customer_deployment_readiness": False,
        },
    }

    artifact_paths = payload["artifact_paths"]
    handoff_json = Path(artifact_paths["handoff_json"])
    handoff_prompt = Path(artifact_paths["handoff_prompt"])
    source_packet_json = Path(artifact_paths["source_packet_json"])
    logic_circuit_screenshot = Path(artifact_paths["logic_circuit_screenshot"])
    demo_first_screen_screenshot = Path(artifact_paths["demo_first_screen_screenshot"])
    assert handoff_json.exists()
    assert handoff_prompt.exists()
    assert source_packet_json.exists()
    assert logic_circuit_screenshot.exists()
    assert demo_first_screen_screenshot.exists()

    prompt = handoff_prompt.read_text(encoding="utf-8")
    assert "只做证据审查" in prompt
    assert "不要修改仓库" in prompt
    assert "accept_evidence" in prompt
    assert "needs_changes" in prompt
    assert "reject_evidence" in prompt
    assert "logic circuit diagram" in prompt
    assert "20 nodes / 23 wires" in prompt
    assert "certification" in prompt


def test_project_owner_external_review_handoff_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Project Owner External Review Handoff" in doc
    assert "make project-owner-external-review-handoff" in doc
    assert "ready_for_read_only_external_review" in doc
    assert "accept_evidence" in doc
    assert "needs_changes" in doc
    assert "reject_evidence" in doc
    assert "logic circuit diagram" in doc
    assert "20 nodes / 23 wires" in doc
    assert "certification" in doc
    assert "PROJECT_OWNER_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR" in makefile
    assert "project-owner-external-review-handoff" in makefile
    assert "scripts/run_project_owner_external_review_handoff.py --format json" in makefile

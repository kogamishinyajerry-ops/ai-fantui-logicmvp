from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_project_visibility_mvp_acceptance.py"
DOC_PATH = PROJECT_ROOT / "docs" / "coordination" / "project-visibility-mvp-acceptance.md"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["AI_FANTUI_QUEUE_PREFLIGHT_MODE"] = "fixture"
    return env


def test_project_visibility_mvp_acceptance_gate_captures_browser_evidence(
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
        timeout=300,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "ai-fantui-project-visibility-mvp-acceptance"
    assert payload["status"] == "pass"
    assert payload["entrypoint"]["command"] == "make project-visibility-mvp-gate"
    assert payload["entrypoint"]["html"].endswith("project_manager_status_summary.html")
    assert payload["deterministic_gates"] == {
        "project_manager_status_summary": "pass",
        "acceptance_doc": "pass",
        "html_entrypoint": "pass",
        "browser_render": "pass",
        "screenshots": "pass",
        "pixel_visibility": "pass",
        "key_content": "pass",
        "boundary": "pass",
        "local_gate": "pass",
    }
    browser = payload["checks"]["browser"]
    assert browser["observed"]["title"] == "Project Manager Status Summary"
    assert browser["observed"]["h1"] == "Project Manager Status Summary"
    assert browser["console_errors"] == []
    assert all(browser["observed"]["required_text"].values())
    assert browser["pixel_visibility"]["width"] >= 1000
    assert browser["pixel_visibility"]["height"] >= 700
    assert browser["pixel_visibility"]["sampled_unique_colors"] >= 20

    screenshot_path = Path(payload["artifact_paths"]["screenshot_desktop"])
    html_path = Path(payload["artifact_paths"]["status_summary_html"])
    acceptance_summary_path = Path(payload["artifact_paths"]["acceptance_summary"])
    assert screenshot_path.exists()
    assert screenshot_path.stat().st_size > 0
    assert html_path.exists()
    assert acceptance_summary_path.exists()


def test_project_visibility_mvp_acceptance_is_documented_and_wired() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "Project Visibility MVP Acceptance" in doc
    assert "make project-visibility-mvp-gate" in doc
    assert "project_manager_status_summary.html" in doc
    assert "RUN-QUEUE-010" in doc
    assert "CHECK_UNREACHABLE_STATE_001" in doc
    assert "Do not continue M21 immediately" in doc
    assert "PROJECT_VISIBILITY_MVP_ACCEPTANCE_ARTIFACT_DIR" in makefile
    assert "project-visibility-mvp-gate" in makefile
    assert "scripts/verify_project_visibility_mvp_acceptance.py --format json" in makefile

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_construction_readiness.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_repair_slices_summary_v0_1.schema.json"
)
QUEUE_EXPANSION_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_multi_agent_construction_readiness_script_emits_single_preflight_packet(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
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
        timeout=45,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["readiness_id"] == "multi-agent-construction-readiness-v0.1"
    assert payload["ready_for_long_running_development"] is True
    assert payload["schema_refs"]["approved_repair_slices_summary"] == SUMMARY_SCHEMA_ID
    assert (
        payload["schema_refs"]["approved_candidate_task_queue_expansion_contract"]
        == QUEUE_EXPANSION_SCHEMA_ID
    )
    assert payload["boundary"] == {
        "truth_effect": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "certification_claim": "none",
    }
    assert [check["name"] for check in payload["checks"]] == [
        "candidate_review_packet_export",
        "approved_repair_slices_artifact",
        "approved_repair_slices_summary_schema",
        "approved_candidate_task_queue_expansion_contract",
    ]
    assert [check["status"] for check in payload["checks"]] == ["pass", "pass", "pass", "pass"]
    assert Path(payload["artifact_paths"]["approved_repair_slices_summary"]).exists()
    assert payload["stop_conditions"] == [
        "controller_truth_modified",
        "ui_layout_modified",
        "open_findings_present",
        "schema_validation_failed",
        "deterministic_gate_failed",
    ]


def test_multi_agent_construction_readiness_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-construction-readiness" in makefile
    assert "scripts/verify_multi_agent_construction_readiness.py --format json" in makefile

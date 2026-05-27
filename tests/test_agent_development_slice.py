from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_first_candidate_repair_slice.py"
SAFETY_TRANSITION_ENDPOINT_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_safety_transition_endpoint_candidate_repair_slice.py"
)
SAFETY_UNREACHABLE_STATE_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_safety_unreachable_state_candidate_repair_slice.py"
)
SAFETY_OUTPUT_COMMAND_CONFLICT_SCRIPT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "run_safety_output_command_conflict_candidate_repair_slice.py"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _state_ids(packet: dict) -> list[str]:
    states = packet["agent_output"]["payload"]["logic_ir"]["states"]
    return [state if isinstance(state, str) else state["id"] for state in states]


def test_first_candidate_repair_slice_runs_approved_task_to_convergence(tmp_path: Path) -> None:
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "first-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_status": "approved",
    }
    assert payload["repair_agent"] == {
        "agent_name": "LogicIRRepairAgent",
        "status": "candidate_patch_generated",
        "action_count": 1,
    }
    assert payload["candidate_delta"] == {
        "changed_transition_ids": ["T004"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["deterministic_gates"] == {
        "safety_guardian": "pass",
        "evidence_agent": "pass",
        "candidate_review_packet": "pass",
        "candidate_review_packet_export": "pass",
        "local_gate": "pass",
    }
    assert payload["reviewer_status"] == "converged"
    assert payload["finding_chain_statuses"] == ["converged"]
    assert payload["convergence"]["after_findings"] == []
    assert payload["convergence"]["task_package_status"] == "no_tasks_required"
    assert payload["convergence"]["execution_plan_status"] == "no_task_available"
    assert payload["convergence"]["execution_evidence_status"] == "no_task_available"

    artifact_paths = payload["artifact_paths"]
    repaired_packet_path = Path(artifact_paths["repaired_candidate_packet"])
    review_export_path = Path(artifact_paths["candidate_review_packet_export"])
    assert repaired_packet_path.exists()
    assert review_export_path.exists()

    review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["reviewer"]["status"] == "converged"
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["performed"] is True
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "set_transition_priority",
            "transition_id": "T004",
            "from": "normal",
            "to": "safety",
            "reason": "CHECK_SAFETY_PRIORITY_001",
        }
    ]


def test_first_candidate_repair_slice_is_wired_into_makefile() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "first-candidate-repair-slice" in makefile
    assert "scripts/run_first_candidate_repair_slice.py --format json" in makefile


def test_safety_transition_endpoint_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SAFETY_TRANSITION_ENDPOINT_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "safety-transition-endpoint-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-CHECK-TRANSITION-ENDPOINT-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_status": "approved",
    }
    assert payload["repair_agent"] == {
        "agent_name": "LogicIRRepairAgent",
        "status": "candidate_patch_generated",
        "action_count": 1,
    }
    assert payload["candidate_delta"] == {
        "changed_state_ids": ["MISSING_STATE"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["convergence"]["before_findings"] == ["CHECK_TRANSITION_ENDPOINT_001"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    assert "MISSING_STATE" in _state_ids(repaired_packet)

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "add_candidate_state_stub",
            "state_id": "MISSING_STATE",
            "transition_id": "T_BAD_ENDPOINT",
            "endpoint": "to",
            "reason": "CHECK_TRANSITION_ENDPOINT_001",
        }
    ]


def test_safety_unreachable_state_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SAFETY_UNREACHABLE_STATE_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "safety-unreachable-state-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_status": "approved",
    }
    assert payload["repair_agent"] == {
        "agent_name": "LogicIRRepairAgent",
        "status": "candidate_patch_generated",
        "action_count": 1,
    }
    assert payload["candidate_delta"] == {
        "changed_state_ids": ["UNREACHABLE_REVIEW"],
        "removed_state_ids": ["UNREACHABLE_REVIEW"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["convergence"]["before_findings"] == ["CHECK_UNREACHABLE_STATE_001"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    assert "UNREACHABLE_REVIEW" not in _state_ids(repaired_packet)

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "remove_candidate_state_stub",
            "state_id": "UNREACHABLE_REVIEW",
            "initial_state": "IDLE",
            "reason": "CHECK_UNREACHABLE_STATE_001",
        }
    ]


def test_safety_output_command_conflict_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SAFETY_OUTPUT_COMMAND_CONFLICT_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == (
        "safety-output-command-conflict-approved-candidate-repair-slice"
    )
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
        "target_agent": "LogicIRRepairAgent",
        "task_type": "repair_candidate_logic_ir",
        "approval_status": "approved",
    }
    assert payload["repair_agent"] == {
        "agent_name": "LogicIRRepairAgent",
        "status": "candidate_patch_generated",
        "action_count": 1,
    }
    assert payload["candidate_delta"] == {
        "changed_transition_ids": ["T_CONFLICT_OPEN"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert "CHECK_OUTPUT_COMMAND_CONFLICT_001" in payload["convergence"]["before_findings"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    repaired_transition = next(
        transition
        for transition in repaired_packet["agent_output"]["payload"]["logic_ir"]["transitions"]
        if transition["id"] == "T_CONFLICT_OPEN"
    )
    assert repaired_transition["priority"] == "safety"

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "set_conflicting_transition_priority",
            "transition_id": "T_CONFLICT_OPEN",
            "paired_transition_id": "T_CONFLICT_CLOSE",
            "signal_name": "fuel_valve",
            "from": "normal",
            "to": "safety",
            "reason": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        }
    ]

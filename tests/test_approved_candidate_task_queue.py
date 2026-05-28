from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_approved_candidate_task_queue.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
QUEUE_FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "approved_candidate_task_queue_summary_v0_1.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _load_queue_module():
    spec = importlib.util.spec_from_file_location("approved_candidate_task_queue", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _normalize_summary(payload: dict) -> dict:
    return {
        "$schema": payload["$schema"],
        "kind": payload["kind"],
        "status": payload["status"],
        "gate_id": payload["gate_id"],
        "queue_id": payload["queue_id"],
        "task_count": payload["task_count"],
        "ready_for_long_running_development": payload[
            "ready_for_long_running_development"
        ],
        "queue_order": payload["queue_order"],
        "deterministic_gates": payload["deterministic_gates"],
        "aggregate": payload["aggregate"],
        "artifact_path_keys": sorted(payload["artifact_paths"].keys()),
        "items": [
            {
                "queue_item_id": item["queue_item_id"],
                "slice_id": item["slice_id"],
                "status": item["status"],
                "preflight": {
                    "command": item["preflight"]["command"],
                    "status": item["preflight"]["status"],
                    "returncode": item["preflight"]["returncode"],
                    "ready_for_long_running_development": item["preflight"][
                        "ready_for_long_running_development"
                    ],
                },
                "execution": item["execution"],
                "approved_task_shell": item["approved_task_shell"],
                "selected_task": item["selected_task"],
                "boundary": item["boundary"],
                "artifact_path_keys": sorted(item["artifact_paths"].keys()),
            }
            for item in payload["items"]
        ],
    }


def test_approved_candidate_task_queue_runs_readiness_before_each_slice(
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
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["queue_id"] == "approved-candidate-task-queue-v0.1"
    assert payload["task_count"] == 3
    assert payload["ready_for_long_running_development"] is True
    assert payload["queue_order"] == [
        "queue-safety-priority-repair",
        "queue-evidence-simulation-result-repair",
        "queue-evidence-test-result-missing-repair",
    ]

    items = payload["items"]
    assert [item["preflight"]["command"] for item in items] == [
        "make multi-agent-construction-readiness",
        "make multi-agent-construction-readiness",
        "make multi-agent-construction-readiness",
    ]
    assert [item["preflight"]["status"] for item in items] == ["pass", "pass", "pass"]
    assert [item["execution"]["status"] for item in items] == ["pass", "pass", "pass"]
    assert [item["approved_task_shell"]["status"] for item in items] == [
        "executed_limited",
        "executed_limited",
        "executed_limited",
    ]
    assert [item["selected_task"]["task_id"] for item in items] == [
        "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "TASK-CE-EV-TEST-RESULT-MISSING",
    ]
    assert [item["selected_task"]["target_agent"] for item in items] == [
        "LogicIRRepairAgent",
        "SimulationTestRepairAgent",
        "SimulationTestRepairAgent",
    ]
    assert all(item["boundary"]["controller_truth_modified"] is False for item in items)
    assert all(item["boundary"]["ui_layout_modified"] is False for item in items)
    assert Path(payload["artifact_paths"]["queue_summary"]).exists()
    assert _normalize_summary(payload) == json.loads(
        QUEUE_FIXTURE_PATH.read_text(encoding="utf-8")
    )


def test_approved_candidate_task_queue_reports_invalid_slice_payload_without_crashing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = _load_queue_module()

    def fake_preflight(_readiness_dir: Path) -> dict:
        return {
            "command": "make multi-agent-construction-readiness",
            "status": "pass",
            "returncode": 0,
            "readiness_id": "multi-agent-construction-readiness-v0.1",
            "ready_for_long_running_development": True,
            "artifact_paths": {},
            "stderr": "",
        }

    def broken_runner(**_kwargs) -> dict:
        return {
            "status": "pass",
            "reviewer_status": "converged",
            "finding_chain_statuses": ["converged"],
            "candidate_delta": {
                "controller_truth_modified": False,
                "ui_layout_modified": False,
            },
            "artifact_paths": {
                "repair_loop_result": str(tmp_path / "missing-repair-loop.json"),
            },
        }

    monkeypatch.setattr(module, "_run_readiness_preflight", fake_preflight)
    monkeypatch.setattr(
        module,
        "_queue_items",
        lambda: [
            {
                "queue_item_id": "queue-broken-evidence",
                "slice_id": "broken-evidence-slice",
                "runner": broken_runner,
            }
        ],
    )

    payload = module.run_approved_candidate_task_queue(
        artifact_dir=tmp_path / "queue",
        input_packet_path=tmp_path / "unused.json",
    )

    assert payload["status"] == "fail"
    assert payload["ready_for_long_running_development"] is False
    assert payload["items"][0]["status"] == "fail"
    assert payload["items"][0]["execution"]["reason"] == "invalid slice payload"
    assert payload["items"][0]["approved_task_shell"] == {
        "status": "invalid_payload",
        "approval_status": "",
        "selected_task_id": "",
    }


def test_approved_candidate_task_queue_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "approved-candidate-task-queue" in makefile
    assert "scripts/run_approved_candidate_task_queue.py --format json" in makefile
    assert "verify-approved-candidate-task-queue-artifact" in makefile

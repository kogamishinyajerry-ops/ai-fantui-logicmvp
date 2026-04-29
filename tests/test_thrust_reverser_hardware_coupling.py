from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.validate_thrust_reverser_hardware_coupling import (
    EXPECTED_LRU_IDS,
    EXPECTED_SIGNAL_IDS,
    validate_hardware_coupling,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_hardware_coupling_validator_passes_expected_inventory_and_bindings() -> None:
    exit_code, report, _ = validate_hardware_coupling()

    assert exit_code == 0
    assert report["status"] == "pass"
    assert report["lru_count"] == len(EXPECTED_LRU_IDS)
    assert report["signal_binding_count"] == len(EXPECTED_SIGNAL_IDS)


def test_hardware_coupling_validator_freezes_write_scope_to_thrust_reverser_yaml() -> None:
    _, report, _ = validate_hardware_coupling()
    frozen_scope = next(
        check for check in report["checks"] if check["name"] == "frozen_hardware_write_scope"
    )

    assert frozen_scope["status"] == "pass"
    assert frozen_scope["target"] == "config/hardware/thrust_reverser_hardware_v1.yaml"
    assert "config/hardware/c919_etras_hardware_v1.yaml" in frozen_scope["frozen_targets"]


def test_hardware_coupling_cli_emits_json_report() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "tools/validate_thrust_reverser_hardware_coupling.py",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["status"] == "pass"
    assert payload["lru_count"] == 11
    assert payload["signal_binding_count"] == 18

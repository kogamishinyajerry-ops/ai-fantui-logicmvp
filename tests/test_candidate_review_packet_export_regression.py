from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_candidate_review_packet_export.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
REGRESSION_COMMAND = (
    "PYTHONPATH=src:. python3 scripts/verify_candidate_review_packet_export.py --format json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_review_packet_export_regression_command_starts_server_and_matches_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--host",
            "127.0.0.1",
            "--port",
            "0",
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
    assert payload["route"] == "/logic-builder/candidate-review-packet.json"
    assert payload["schema_valid"] is True
    assert payload["fixture_match"] is True
    assert payload["reviewer_status"] == "blocked_pending_approval"
    assert payload["finding_chain_statuses"] == ["blocked_missing_approval"]
    assert payload["finding_chain_convergence"] == [{}]
    assert payload["server_started"] is True


def test_review_packet_export_regression_command_reports_fixture_drift(tmp_path: Path) -> None:
    drifted_fixture = tmp_path / "candidate_review_packet_export_v0_1.json"
    fixture = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "candidate_review_packet_export_v0_1.json"
        ).read_text(encoding="utf-8")
    )
    fixture["review_packet"]["reviewer"]["status"] = "converged"
    fixture["review_packet_ref"]["reviewer_status"] = "converged"
    drifted_fixture.write_text(json.dumps(fixture), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--host",
            "127.0.0.1",
            "--port",
            "0",
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
    assert "reviewer_status" in payload["mismatches"]


def test_demo_server_import_does_not_require_jsonschema_for_review_packet_export() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import importlib.abc
import sys

class BlockJsonschema(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "jsonschema" or fullname.startswith("jsonschema."):
            raise ModuleNotFoundError("blocked jsonschema import")
        return None

sys.meta_path.insert(0, BlockJsonschema())
from well_harness import demo_server
assert demo_server.CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE == "/logic-builder/candidate-review-packet.json"
assert "jsonschema" not in sys.modules
""",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


def test_make_test_gate_runs_review_packet_export_regression_command() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    phony_line = next(line for line in makefile.splitlines() if line.startswith(".PHONY:"))
    for target in ("dev", "test", "review-packet-export-regression", "help"):
        assert target in phony_line
    test_line = next(line for line in makefile.splitlines() if line.startswith("test:"))
    assert "review-packet-export-regression" in test_line
    assert REGRESSION_COMMAND in makefile

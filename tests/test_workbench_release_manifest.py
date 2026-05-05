from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.workbench_release_manifest import (
    MANIFEST_KIND,
    build_release_manifest,
    validate_release_manifest,
    validation_report,
)


def _fake_git(args: tuple[str, ...], repo_root: Path) -> str:
    del repo_root
    if args == ("rev-parse", "HEAD"):
        return "abc123def4567890abc123def4567890abc123de"
    if args == ("rev-parse", "--short=12", "HEAD"):
        return "abc123def456"
    if args == ("branch", "--show-current"):
        return "codex/JER-244-release-runbook-manifest"
    raise AssertionError(f"unexpected git args: {args}")


def _fixed_clock() -> datetime:
    return datetime(2026, 5, 5, 9, 0, 0, tzinfo=timezone.utc)


def _all_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_all_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_all_strings(item))
        return strings
    return []


def test_release_manifest_records_truthful_gate_statuses_without_secrets(monkeypatch: Any) -> None:
    monkeypatch.setenv("MINIMAX_API_KEY", "sk-test-secret-that-must-not-appear")

    manifest = build_release_manifest(repo_root=Path("/repo"), git_runner=_fake_git, clock=_fixed_clock)

    assert manifest["kind"] == MANIFEST_KIND
    assert manifest["version"] == 1
    assert manifest["generated_at"] == "2026-05-05T09:00:00Z"
    assert manifest["git"] == {
        "sha": "abc123def4567890abc123def4567890abc123de",
        "short_sha": "abc123def456",
        "branch": "codex/JER-244-release-runbook-manifest",
    }
    assert manifest["release_candidate"]["truth_level_impact"] == "none"
    assert manifest["release_candidate"]["certification_claim"] == "none"
    assert manifest["required_environment"]["required_env_vars_for_local_release_gates"] == []

    commands = {item["id"]: item for item in manifest["verification_commands"]}
    assert commands["release_candidate_smoke_gate"]["status"] == "pass"
    assert "workbench_release_candidate_smoke.py --format json" in commands["release_candidate_smoke_gate"]["command"]
    assert commands["full_opt_in_e2e"]["status"] == "pass"
    assert "93 passed / 3445 deselected" in commands["full_opt_in_e2e"]["evidence_summary"]
    assert commands["full_strict_mypy"]["status"] == "blocked"
    assert "4617 errors in 326 files" in commands["full_strict_mypy"]["evidence_summary"]
    assert all(command["external_services"] == [] for command in commands.values())

    not_claimed_ids = {item["id"] for item in manifest["not_claimed_gates"]}
    assert {
        "production_ready",
        "cloud_deployment_ready",
        "certification_ready",
        "full_strict_mypy_clean",
    } <= not_claimed_ids
    assert "sk-test-secret-that-must-not-appear" not in json.dumps(manifest)
    assert validate_release_manifest(manifest) == []


def test_release_manifest_validation_rejects_over_claimed_manifest() -> None:
    manifest = build_release_manifest(repo_root=Path("/repo"), git_runner=_fake_git, clock=_fixed_clock)
    manifest["not_claimed_gates"] = [
        item for item in manifest["not_claimed_gates"] if item["id"] != "production_ready"
    ]
    manifest["required_environment"]["required_env_vars_for_local_release_gates"] = ["MINIMAX_API_KEY"]

    issues = validate_release_manifest(manifest)

    assert "not_claimed_gates must include production_ready." in issues
    assert "local release gates must not require secret environment variables." in issues


def test_release_manifest_cli_outputs_valid_json() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/workbench_release_manifest.py", "--validate", "--format", "json"],
        capture_output=True,
        check=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["kind"] == "well-harness-workbench-release-evidence-manifest-validation"
    assert payload["status"] == "pass"
    assert payload["verification_command_count"] >= 4
    assert payload["not_claimed_gate_count"] >= 4


def test_release_manifest_validation_flags_secret_like_key_value_strings() -> None:
    manifest = build_release_manifest(repo_root=Path("/repo"), git_runner=_fake_git, clock=_fixed_clock)
    manifest["current_blockers"].append({"id": "bad", "summary": "API_KEY=leaked"})

    report = validation_report(manifest)

    assert report["status"] == "fail"
    assert "manifest must not embed secret-like key/value strings." in report["issues"]
    assert all("API_KEY=leaked" not in value for value in _all_strings(report))

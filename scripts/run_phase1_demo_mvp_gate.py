#!/usr/bin/env python3
"""Run the CI/local Phase 1 demo MVP gate and emit one final summary."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-gate")
GATE_SUMMARY_NAME = "phase1_demo_mvp_gate_summary.json"
RELEASE_SUMMARY_NAME = "phase1_demo_mvp_release_summary.json"
GATE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_gate_summary_v0_1.schema.json"
)
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _run_json_command(args: list[str], *, timeout: int = 180) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": payload,
    }


def _command_status(command: dict[str, Any]) -> str:
    return "pass" if command["returncode"] == 0 and command["payload"].get("status") == "pass" else "fail"


def _check_summary(command: dict[str, Any]) -> dict[str, Any]:
    payload = command["payload"]
    return {
        "status": "pass" if _command_status(command) == "pass" else "fail",
        "returncode": command["returncode"],
        "kind": payload.get("kind", ""),
        "deterministic_gates": payload.get("deterministic_gates", {}),
        "visual_evidence": payload.get("visual_evidence", {}),
        "artifact_paths": payload.get("artifact_paths", {}),
        "mismatches": payload.get("mismatches", []),
    }


def _collect_mismatches(
    *,
    gate_results: dict[str, str],
    commands: dict[str, dict[str, Any]],
) -> list[str]:
    mismatches = [f"{name}=fail" for name, status in gate_results.items() if status != "pass"]
    for name, command in commands.items():
        if command["returncode"] != 0:
            mismatches.append(f"{name}.returncode={command['returncode']}")
        for mismatch in command["payload"].get("mismatches", []):
            mismatches.append(f"{name}.{mismatch}")
    return mismatches


def run_phase1_demo_mvp_gate(*, artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    gate_summary_path = artifact_dir / GATE_SUMMARY_NAME
    release_summary_path = artifact_dir / RELEASE_SUMMARY_NAME

    release_checklist_command = _run_json_command(
        [
            sys.executable,
            "scripts/run_phase1_demo_mvp_release_checklist.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir),
        ],
        timeout=180,
    )
    release_summary_verification_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_release_summary.py",
            "--format",
            "json",
            "--summary",
            str(release_summary_path),
        ],
        timeout=60,
    )
    ci_artifact_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_ci_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir),
        ],
        timeout=60,
    )

    release_payload = release_checklist_command["payload"]
    commands = {
        "release_checklist": release_checklist_command,
        "release_summary_verification": release_summary_verification_command,
        "ci_artifact": ci_artifact_command,
    }
    release_gates = release_payload.get("deterministic_gates", {})
    gate_results = {
        "release_checklist": _command_status(release_checklist_command),
        "release_summary_verification": _command_status(release_summary_verification_command),
        "ci_artifact": _command_status(ci_artifact_command),
        "browser_acceptance": "pass" if release_gates.get("browser_acceptance") == "pass" else "fail",
        "boundary": "pass"
        if release_payload.get("review_boundaries") == EXPECTED_REVIEW_BOUNDARIES
        and release_gates.get("boundary") == "pass"
        else "fail",
    }
    mismatches = _collect_mismatches(gate_results=gate_results, commands=commands)
    status = "pass" if all(value == "pass" for value in gate_results.values()) and not mismatches else "fail"
    release_artifact_paths = release_payload.get("artifact_paths", {})
    summary = {
        "$schema": GATE_SUMMARY_SCHEMA_ID,
        "kind": "ai-fantui-phase1-demo-mvp-gate-summary",
        "version": 1,
        "status": status,
        "route": "/demo-reconstruction",
        "generated_at": _utc_now(),
        "artifact_dir": str(artifact_dir),
        "demo_surface": release_payload.get("demo_surface", {}),
        "deterministic_gates": gate_results,
        "checks": {
            "release_checklist": _check_summary(release_checklist_command),
            "release_summary_verification": _check_summary(release_summary_verification_command),
            "ci_artifact": _check_summary(ci_artifact_command),
        },
        "visual_evidence": release_payload.get("visual_evidence", {}),
        "artifact_paths": {
            "gate_summary": str(gate_summary_path),
            "release_summary": str(release_summary_path),
            **release_artifact_paths,
        },
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "mismatches": mismatches,
    }
    gate_summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the single local/CI Phase 1 demo MVP gate.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP gate passed")
    else:
        print(f"FAIL: phase1 demo MVP gate failed ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = run_phase1_demo_mvp_gate(artifact_dir=args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "$schema": GATE_SUMMARY_SCHEMA_ID,
            "kind": "ai-fantui-phase1-demo-mvp-gate-summary",
            "version": 1,
            "status": "fail",
            "route": "/demo-reconstruction",
            "artifact_dir": str(args.artifact_dir),
            "demo_surface": {},
            "deterministic_gates": {
                "release_checklist": "fail",
                "release_summary_verification": "fail",
                "ci_artifact": "fail",
                "browser_acceptance": "fail",
                "boundary": "fail",
            },
            "checks": {},
            "artifact_paths": {
                "gate_summary": str(args.artifact_dir / GATE_SUMMARY_NAME),
                "release_summary": str(args.artifact_dir / RELEASE_SUMMARY_NAME),
            },
            "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
            "mismatches": ["runtime_error"],
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

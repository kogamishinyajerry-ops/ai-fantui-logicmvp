#!/usr/bin/env python3
"""Run the Phase 1 demo MVP release gate and emit one summary artifact."""
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
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-release-checklist")
SUMMARY_NAME = "phase1_demo_mvp_release_summary.json"
RELEASE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_release_summary_v0_1.schema.json"
)
CONSUMPTION_RUNBOOK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "coordination"
    / "phase1-demo-mvp-artifact-consumption-runbook.md"
)
RELEASE_CHECKLIST_PATH = (
    PROJECT_ROOT / "docs" / "coordination" / "phase1-demo-mvp-release-checklist.md"
)
EXPECTED_DEMO_SURFACE = {
    "route": "/demo-reconstruction",
    "title": "反推控制台复刻",
    "node_count": 20,
    "wire_count": 23,
    "preset_count": 5,
    "status_output_count": 6,
    "output_card_count": 4,
}
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
        "embedded_palette": payload.get("embedded_palette", {}),
        "artifact_paths": payload.get("artifact_paths", {}),
        "artifact_dir": payload.get("artifact_dir", ""),
        "screenshots": payload.get("screenshots", {}),
    }


def _documentation_check() -> dict[str, Any]:
    consumption_exists = CONSUMPTION_RUNBOOK_PATH.exists() and CONSUMPTION_RUNBOOK_PATH.stat().st_size > 0
    checklist_exists = RELEASE_CHECKLIST_PATH.exists() and RELEASE_CHECKLIST_PATH.stat().st_size > 0
    return {
        "status": "pass" if consumption_exists and checklist_exists else "fail",
        "consumption_runbook_exists": consumption_exists,
        "release_checklist_exists": checklist_exists,
    }


def _boundary_status(*payloads: dict[str, Any]) -> str:
    for payload in payloads:
        boundaries = payload.get("review_boundaries")
        if isinstance(boundaries, dict) and boundaries != EXPECTED_REVIEW_BOUNDARIES:
            return "fail"
        gates = payload.get("deterministic_gates")
        if isinstance(gates, dict) and gates.get("boundary") == "fail":
            return "fail"
    return "pass"


def _collect_mismatches(
    *,
    gate_results: dict[str, str],
    commands: dict[str, dict[str, Any]],
    documentation: dict[str, Any],
) -> list[str]:
    mismatches = [
        f"{gate}=fail"
        for gate, status in gate_results.items()
        if status != "pass"
    ]
    for name, command in commands.items():
        if command["returncode"] != 0:
            mismatches.append(f"{name}.returncode={command['returncode']}")
        payload = command["payload"]
        for mismatch in payload.get("mismatches", []):
            mismatches.append(f"{name}.{mismatch}")
    if documentation["status"] != "pass":
        mismatches.append("documentation=fail")
    return mismatches


def _artifact_paths(
    *,
    artifact_dir: Path,
    summary_path: Path,
    review_package_payload: dict[str, Any],
    ci_artifact_payload: dict[str, Any],
) -> dict[str, Any]:
    review_paths = review_package_payload.get("artifact_paths", {})
    ci_paths = ci_artifact_payload.get("artifact_paths", {})
    return {
        "release_summary": str(summary_path),
        "standalone_browser_acceptance_dir": str(artifact_dir / "standalone-browser-acceptance"),
        "package": review_paths.get("package", str(artifact_dir / "phase1_demo_mvp_review_package_v0_1.json")),
        "markdown_report": review_paths.get("markdown_report", str(artifact_dir / "phase1_demo_mvp_review_report.md")),
        "demo_gate_json": review_paths.get("demo_gate_json", str(artifact_dir / "demo_html_reconstruction_mvp_gate.json")),
        "browser_acceptance_json": review_paths.get(
            "browser_acceptance_json",
            str(artifact_dir / "demo_html_reconstruction_browser_acceptance.json"),
        ),
        "screenshots": ci_paths.get("screenshots", []),
    }


def _visual_evidence(browser_payload: dict[str, Any]) -> dict[str, Any]:
    screenshots = browser_payload.get("screenshots", {})
    return {
        "embedded_codex_light_palette": browser_payload.get("deterministic_gates", {}).get(
            "embedded_codex_light_palette",
            "fail",
        ),
        "embedded_palette": browser_payload.get("embedded_palette", {}),
        "light_demo_first_screen": screenshots.get("first_screen", "")
        if isinstance(screenshots, dict)
        else "",
        "browser_acceptance_status": browser_payload.get("status", "fail"),
    }


def run_release_checklist(*, artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / SUMMARY_NAME
    browser_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_demo_html_reconstruction_browser_acceptance.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir / "standalone-browser-acceptance"),
        ],
        timeout=180,
    )
    review_package_command = _run_json_command(
        [
            sys.executable,
            "scripts/run_phase1_demo_mvp_review_package.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir),
        ],
        timeout=180,
    )
    review_package_verification_command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_review_package.py",
            "--format",
            "json",
            "--package",
            str(artifact_dir / "phase1_demo_mvp_review_package_v0_1.json"),
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

    documentation = _documentation_check()
    commands = {
        "browser_acceptance": browser_command,
        "review_package": review_package_command,
        "review_package_verification": review_package_verification_command,
        "ci_artifact": ci_artifact_command,
    }
    review_package_payload = review_package_command["payload"]
    browser_payload = browser_command["payload"]
    ci_artifact_payload = ci_artifact_command["payload"]
    gate_results = {
        "browser_acceptance": _command_status(browser_command),
        "review_package": _command_status(review_package_command),
        "review_package_verification": _command_status(review_package_verification_command),
        "ci_artifact": _command_status(ci_artifact_command),
        "documentation": documentation["status"],
        "boundary": _boundary_status(
            browser_command["payload"],
            review_package_payload,
            ci_artifact_payload,
        ),
    }
    mismatches = _collect_mismatches(
        gate_results=gate_results,
        commands=commands,
        documentation=documentation,
    )
    status = "pass" if all(value == "pass" for value in gate_results.values()) and not mismatches else "fail"
    summary = {
        "$schema": RELEASE_SUMMARY_SCHEMA_ID,
        "kind": "ai-fantui-phase1-demo-mvp-release-summary",
        "version": 1,
        "status": status,
        "release_status": status,
        "route": "/demo-reconstruction",
        "generated_at": _utc_now(),
        "artifact_dir": str(artifact_dir),
        "demo_surface": review_package_payload.get("demo_surface", EXPECTED_DEMO_SURFACE),
        "deterministic_gates": gate_results,
        "checks": {
            "browser_acceptance": _check_summary(browser_command),
            "review_package": _check_summary(review_package_command),
            "review_package_verification": _check_summary(review_package_verification_command),
            "ci_artifact": _check_summary(ci_artifact_command),
            "documentation": documentation,
        },
        "visual_evidence": _visual_evidence(browser_payload),
        "artifact_paths": _artifact_paths(
            artifact_dir=artifact_dir,
            summary_path=summary_path,
            review_package_payload=review_package_payload,
            ci_artifact_payload=ci_artifact_payload,
        ),
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "mismatches": mismatches,
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Phase 1 demo MVP release gate and write phase1_demo_mvp_release_summary.json.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP release checklist passed")
    else:
        print(f"FAIL: phase1 demo MVP release checklist failed ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = run_release_checklist(artifact_dir=args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "$schema": RELEASE_SUMMARY_SCHEMA_ID,
            "kind": "ai-fantui-phase1-demo-mvp-release-summary",
            "version": 1,
            "status": "fail",
            "release_status": "fail",
            "route": "/demo-reconstruction",
            "artifact_dir": str(args.artifact_dir),
            "demo_surface": EXPECTED_DEMO_SURFACE,
            "deterministic_gates": {
                "browser_acceptance": "fail",
                "review_package": "fail",
                "review_package_verification": "fail",
                "ci_artifact": "fail",
                "documentation": "fail",
                "boundary": "fail",
            },
            "checks": {},
            "artifact_paths": {
                "release_summary": str(args.artifact_dir / SUMMARY_NAME),
            },
            "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
            "mismatches": ["runtime_error"],
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

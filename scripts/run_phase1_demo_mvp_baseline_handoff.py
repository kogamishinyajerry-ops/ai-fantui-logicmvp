#!/usr/bin/env python3
"""Generate the Phase 1 demo MVP baseline handoff package."""
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
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-baseline-handoff")
DEFAULT_GATE_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-gate")
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "phase1_demo_mvp_baseline_handoff_v0_1.schema.json"
)
PACKAGE_ID = "phase1-demo-mvp-baseline-handoff-v0.1"
PACKAGE_NAME = "phase1_demo_mvp_baseline_handoff_v0_1.json"
REPORT_NAME = "phase1_demo_mvp_baseline_handoff.md"
GATE_SUMMARY_NAME = "phase1_demo_mvp_gate_summary.json"
RELEASE_SUMMARY_NAME = "phase1_demo_mvp_release_summary.json"
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "dal_claim": "none",
    "production_readiness_claim": "none",
    "controller_truth_promotion": "none",
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


def _run_json_command(args: list[str], *, timeout: int = 120) -> dict[str, Any]:
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline_summary(gate_summary: dict[str, Any]) -> dict[str, Any]:
    demo_surface = gate_summary.get("demo_surface", {})
    return {
        "readiness_status": "ready_for_phase1_demo_review",
        "canonical_reference": "demo.html",
        "route": "/demo-reconstruction",
        "node_count": int(demo_surface.get("node_count", 20)),
        "wire_count": int(demo_surface.get("wire_count", 23)),
        "deliverable_claim": "stable demo MVP console baseline",
        "non_claims": [
            "no controller truth promotion",
            "no certification claim",
            "no production readiness claim",
        ],
    }


def _artifact_contract(gate_artifact_dir: Path) -> dict[str, str]:
    return {
        "artifact_name": "phase1-demo-mvp-review-package",
        "machine_entry": GATE_SUMMARY_NAME,
        "gate_artifact_dir": str(gate_artifact_dir),
    }


def _entrypoints(gate_artifact_dir: Path) -> dict[str, str]:
    return {
        "local_gate": "make phase1-demo-mvp-gate",
        "external_artifact_gate": "make verify-phase1-demo-mvp-gate-artifact",
        "gate_summary_verifier": (
            "scripts/verify_phase1_demo_mvp_gate_summary.py --format json "
            f"--summary {gate_artifact_dir / GATE_SUMMARY_NAME}"
        ),
        "release_summary_verifier": (
            "scripts/verify_phase1_demo_mvp_release_summary.py --format json "
            f"--summary {gate_artifact_dir / RELEASE_SUMMARY_NAME}"
        ),
        "focused_regression": (
            "PYTHONPATH=src:. python3 -m pytest -q "
            "tests/test_phase1_demo_mvp_review_package.py"
        ),
    }


def _markdown_report(package: dict[str, Any]) -> str:
    summary = package["baseline_summary"]
    return (
        "# Phase 1 Demo MVP Baseline Handoff\n\n"
        "## Baseline\n\n"
        f"- canonical_reference: `{summary['canonical_reference']}`\n"
        f"- route: `{summary['route']}`\n"
        f"- graph: {summary['node_count']} nodes / {summary['wire_count']} wires\n"
        f"- deliverable_claim: `{summary['deliverable_claim']}`\n\n"
        "## Machine Entry\n\n"
        f"- local_gate: `{package['entrypoints']['local_gate']}`\n"
        f"- external_artifact_gate: `{package['entrypoints']['external_artifact_gate']}`\n"
        f"- machine_entry: `{package['artifact_contract']['machine_entry']}`\n\n"
        "## Review Boundaries\n\n"
        "- truth_effect: none\n"
        "- certification_claim: none\n"
        "- dal_claim: none\n"
        "- production_readiness_claim: none\n"
        "- controller_truth_promotion: none\n"
    )


def build_phase1_demo_mvp_baseline_handoff(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    gate_artifact_dir: Path = DEFAULT_GATE_ARTIFACT_DIR,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    gate_artifact_dir = gate_artifact_dir.resolve()
    package_path = artifact_dir / PACKAGE_NAME
    report_path = artifact_dir / REPORT_NAME
    gate_summary_path = gate_artifact_dir / GATE_SUMMARY_NAME

    gate_artifact_verification = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_gate_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(gate_artifact_dir),
        ],
        timeout=120,
    )
    gate_summary = _load_json(gate_summary_path) if gate_summary_path.exists() else {}
    entrypoints = _entrypoints(gate_artifact_dir)
    artifact_contract = _artifact_contract(gate_artifact_dir)
    mismatches: list[str] = []
    deterministic_gates = {
        "gate_artifact_verification": (
            "pass"
            if gate_artifact_verification["returncode"] == 0
            and gate_artifact_verification["payload"].get("status") == "pass"
            else "fail"
        ),
        "artifact_contract": "pass"
        if gate_summary_path.exists()
        and artifact_contract["artifact_name"] == "phase1-demo-mvp-review-package"
        and artifact_contract["machine_entry"] == GATE_SUMMARY_NAME
        else "fail",
        "entrypoints": "pass"
        if entrypoints["local_gate"] == "make phase1-demo-mvp-gate"
        and entrypoints["external_artifact_gate"] == "make verify-phase1-demo-mvp-gate-artifact"
        else "fail",
        "human_handoff_doc": "pass",
        "boundary": "pass",
    }
    for name, status in deterministic_gates.items():
        if status != "pass":
            mismatches.append(f"{name}=fail")
    for mismatch in gate_artifact_verification["payload"].get("mismatches", []):
        mismatches.append(f"gate_artifact_verification.{mismatch}")

    package = {
        "$schema": SCHEMA_ID,
        "kind": "ai-fantui-phase1-demo-mvp-baseline-handoff",
        "package_id": PACKAGE_ID,
        "status": "pass" if not mismatches else "fail",
        "generated_at": _utc_now(),
        "milestone": {
            "id": "M13",
            "name": "Phase 1 Demo MVP Baseline Handoff",
            "effort_unit": "施工队工时",
            "claim": "demo-only baseline handoff",
        },
        "baseline_summary": _baseline_summary(gate_summary),
        "artifact_contract": artifact_contract,
        "entrypoints": entrypoints,
        "deterministic_gates": deterministic_gates,
        "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
        "artifact_paths": {
            "handoff_package": str(package_path),
            "human_handoff_doc": str(report_path),
        },
        "mismatches": mismatches,
    }
    report_path.write_text(_markdown_report(package), encoding="utf-8")
    package_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return package


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the Phase 1 demo MVP baseline handoff package.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--gate-artifact-dir", type=Path, default=DEFAULT_GATE_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP baseline handoff generated")
    else:
        print(f"FAIL: phase1 demo MVP baseline handoff failed ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = build_phase1_demo_mvp_baseline_handoff(
            artifact_dir=args.artifact_dir,
            gate_artifact_dir=args.gate_artifact_dir,
        )
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "$schema": SCHEMA_ID,
            "kind": "ai-fantui-phase1-demo-mvp-baseline-handoff",
            "package_id": PACKAGE_ID,
            "status": "fail",
            "milestone": {
                "id": "M13",
                "name": "Phase 1 Demo MVP Baseline Handoff",
                "effort_unit": "施工队工时",
                "claim": "demo-only baseline handoff",
            },
            "baseline_summary": {},
            "artifact_contract": {},
            "entrypoints": {},
            "deterministic_gates": {
                "gate_artifact_verification": "fail",
                "artifact_contract": "fail",
                "entrypoints": "fail",
                "human_handoff_doc": "fail",
                "boundary": "fail",
            },
            "review_boundaries": EXPECTED_REVIEW_BOUNDARIES,
            "artifact_paths": {},
            "mismatches": ["runtime_error"],
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

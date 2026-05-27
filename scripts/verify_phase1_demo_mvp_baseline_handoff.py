#!/usr/bin/env python3
"""Verify a Phase 1 demo MVP baseline handoff package."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = (
    Path("/tmp/ai-fantui-phase1-demo-mvp-baseline-handoff")
    / "phase1_demo_mvp_baseline_handoff_v0_1.json"
)
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_baseline_handoff_v0_1.schema.json"
)
GATE_SUMMARY_NAME = "phase1_demo_mvp_gate_summary.json"
EXPECTED_BASELINE_SUMMARY = {
    "readiness_status": "ready_for_phase1_demo_review",
    "canonical_reference": "demo.html",
    "route": "/demo-reconstruction",
    "node_count": 20,
    "wire_count": 23,
    "deliverable_claim": "stable demo MVP console baseline",
    "non_claims": [
        "no controller truth promotion",
        "no certification claim",
        "no production readiness claim",
    ],
}
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "dal_claim": "none",
    "production_readiness_claim": "none",
    "controller_truth_promotion": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(path_value: Any, package_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    candidate = package_path.parent / path
    if candidate.exists():
        return candidate
    return PROJECT_ROOT / path


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
        "returncode": result.returncode,
        "payload": payload,
    }


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_json(SCHEMA_PATH)).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        mismatches.append(f"schema{'.' + path if path else ''}: {error.message}")
    return not errors


def _gate_artifact_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    contract = package.get("artifact_contract", {})
    artifact_dir = Path(str(contract.get("gate_artifact_dir", "")))
    gate_summary_path = artifact_dir / GATE_SUMMARY_NAME
    valid = True
    if contract.get("artifact_name") != "phase1-demo-mvp-review-package":
        mismatches.append("artifact_contract.artifact_name must be phase1-demo-mvp-review-package")
        valid = False
    if contract.get("machine_entry") != GATE_SUMMARY_NAME:
        mismatches.append("artifact_contract.machine_entry must be phase1_demo_mvp_gate_summary.json")
        valid = False
    if not gate_summary_path.exists():
        mismatches.append("gate artifact summary must exist")
        return False
    gate_summary = _load_json(gate_summary_path)
    if gate_summary.get("status") != "pass":
        mismatches.append("gate summary status must be pass")
        valid = False
    if package.get("baseline_summary") != EXPECTED_BASELINE_SUMMARY:
        mismatches.append("baseline_summary must match demo.html reconstruction contract")
        valid = False
    command = _run_json_command(
        [
            sys.executable,
            "scripts/verify_phase1_demo_mvp_gate_artifact.py",
            "--format",
            "json",
            "--artifact-dir",
            str(artifact_dir),
        ],
    )
    if command["returncode"] != 0 or command["payload"].get("status") != "pass":
        mismatches.append("gate artifact verifier must pass")
        valid = False
    if package.get("deterministic_gates", {}).get("gate_artifact_verification") != "pass":
        mismatches.append("deterministic_gates.gate_artifact_verification must be pass")
        valid = False
    if package.get("deterministic_gates", {}).get("artifact_contract") != "pass":
        mismatches.append("deterministic_gates.artifact_contract must be pass")
        valid = False
    return valid


def _entrypoints_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    entrypoints = package.get("entrypoints", {})
    expected = {
        "local_gate": "make phase1-demo-mvp-gate",
        "external_artifact_gate": "make verify-phase1-demo-mvp-gate-artifact",
        "focused_regression": (
            "PYTHONPATH=src:. python3 -m pytest -q "
            "tests/test_phase1_demo_mvp_review_package.py"
        ),
    }
    valid = True
    for key, value in expected.items():
        if entrypoints.get(key) != value:
            mismatches.append(f"entrypoints.{key} must be {value}")
            valid = False
    for key in ("gate_summary_verifier", "release_summary_verifier"):
        if not isinstance(entrypoints.get(key), str) or "--format json" not in entrypoints[key]:
            mismatches.append(f"entrypoints.{key} must name a JSON verifier")
            valid = False
    if package.get("deterministic_gates", {}).get("entrypoints") != "pass":
        mismatches.append("deterministic_gates.entrypoints must be pass")
        valid = False
    return valid


def _human_handoff_doc_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    report_path = _resolve_path(package.get("artifact_paths", {}).get("human_handoff_doc"), package_path)
    if report_path is None or not report_path.exists() or report_path.stat().st_size == 0:
        mismatches.append("artifact_paths.human_handoff_doc must exist")
        return False
    text = report_path.read_text(encoding="utf-8")
    valid = True
    for fragment in (
        "Phase 1 Demo MVP Baseline Handoff",
        "demo.html",
        "/demo-reconstruction",
        "20 nodes / 23 wires",
        "certification_claim: none",
    ):
        if fragment not in text:
            mismatches.append(f"human_handoff_doc must contain {fragment}")
            valid = False
    if package.get("deterministic_gates", {}).get("human_handoff_doc") != "pass":
        mismatches.append("deterministic_gates.human_handoff_doc must be pass")
        valid = False
    return valid


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    boundaries = package.get("review_boundaries")
    if boundaries != EXPECTED_REVIEW_BOUNDARIES:
        mismatches.append("review_boundaries must preserve demo-only boundaries")
        valid = False
    if isinstance(boundaries, dict) and boundaries.get("certification_claim") != "none":
        mismatches.append("review_boundaries.certification_claim must be none")
        valid = False
    if package.get("deterministic_gates", {}).get("boundary") != "pass":
        mismatches.append("deterministic_gates.boundary must be pass")
        valid = False
    return valid


def verify_baseline_handoff(package_path: Path) -> dict[str, Any]:
    mismatches: list[str] = []
    package = _load_json(package_path)
    gate_results = {
        "schema": "pass" if _schema_valid(package, mismatches) else "fail",
        "gate_artifact": "pass" if _gate_artifact_valid(package, mismatches) else "fail",
        "entrypoints": "pass" if _entrypoints_valid(package, mismatches) else "fail",
        "human_handoff_doc": "pass"
        if _human_handoff_doc_valid(package, package_path=package_path, mismatches=mismatches)
        else "fail",
        "boundary": "pass" if _boundary_valid(package, mismatches) else "fail",
    }
    status = "pass" if all(value == "pass" for value in gate_results.values()) else "fail"
    return {
        "kind": "ai-fantui-phase1-demo-mvp-baseline-handoff-verification",
        "status": status,
        "package": str(package_path),
        "mismatches": mismatches,
        "deterministic_gates": gate_results,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify phase1_demo_mvp_baseline_handoff_v0_1.json.",
    )
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP baseline handoff verified")
    else:
        print(f"FAIL: phase1 demo MVP baseline handoff drifted ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = verify_baseline_handoff(args.package)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-phase1-demo-mvp-baseline-handoff-verification",
            "status": "fail",
            "package": str(args.package),
            "mismatches": ["runtime_error"],
            "deterministic_gates": {
                "schema": "fail",
                "gate_artifact": "fail",
                "entrypoints": "fail",
                "human_handoff_doc": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

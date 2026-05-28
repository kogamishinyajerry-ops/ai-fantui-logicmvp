#!/usr/bin/env python3
"""Verify the Phase 1 demo MVP gate summary artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY_PATH = (
    Path("/tmp/ai-fantui-phase1-demo-mvp-gate")
    / "phase1_demo_mvp_gate_summary.json"
)
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_gate_summary_v0_1.schema.json"
)
EXPECTED_GATES = {
    "release_checklist": "pass",
    "release_summary_verification": "pass",
    "ci_artifact": "pass",
    "browser_acceptance": "pass",
    "boundary": "pass",
}
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_valid(summary: dict[str, Any], mismatches: list[str]) -> bool:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_json(SCHEMA_PATH)).iter_errors(summary),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        mismatches.append(f"schema{'.' + path if path else ''}: {error.message}")
    return not errors


def _gate_status_valid(summary: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if summary.get("status") != "pass":
        mismatches.append("status must be pass")
        valid = False
    if summary.get("mismatches") != []:
        mismatches.append("mismatches must be empty")
        valid = False
    return valid


def _deterministic_gates_valid(summary: dict[str, Any], mismatches: list[str]) -> bool:
    if summary.get("deterministic_gates") != EXPECTED_GATES:
        mismatches.append("deterministic_gates must all pass")
        return False
    checks = summary.get("checks", {})
    valid = True
    for name in ("release_checklist", "release_summary_verification", "ci_artifact"):
        if checks.get(name, {}).get("status") != "pass":
            mismatches.append(f"checks.{name}.status must be pass")
            valid = False
    return valid


def _resolve_path(path_value: Any, summary_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    candidates = [summary_path] if path.name == summary_path.name else []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend(
            [
                summary_path.parent / path,
                summary_path.parent / path.name,
                summary_path.parent / "browser-acceptance" / path.name,
            ]
        )
    if path.name == "phase1_demo_mvp_release_summary.json":
        candidates.append(summary_path.parent / path.name)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _artifact_paths_valid(summary: dict[str, Any], summary_path: Path, mismatches: list[str]) -> bool:
    artifact_paths = summary.get("artifact_paths", {})
    required = [
        "gate_summary",
        "release_summary",
        "package",
        "markdown_report",
        "demo_gate_json",
        "browser_acceptance_json",
    ]
    valid = True
    for key in required:
        path = _resolve_path(artifact_paths.get(key), summary_path)
        if path is None or not path.exists() or path.stat().st_size == 0:
            mismatches.append(f"artifact_paths.{key} must exist")
            valid = False
    screenshots = artifact_paths.get("screenshots")
    if not isinstance(screenshots, list) or not screenshots:
        mismatches.append("artifact_paths.screenshots must be non-empty")
        return False
    for index, screenshot in enumerate(screenshots):
        path = _resolve_path(screenshot, summary_path)
        if path is None or not path.exists() or path.stat().st_size == 0:
            mismatches.append(f"artifact_paths.screenshots[{index}] must exist")
            valid = False
    return valid


def _boundary_valid(summary: dict[str, Any], mismatches: list[str]) -> bool:
    if summary.get("review_boundaries") != EXPECTED_REVIEW_BOUNDARIES:
        mismatches.append("review_boundaries must preserve demo-only boundaries")
        return False
    return True


def verify_gate_summary(summary_path: Path = DEFAULT_SUMMARY_PATH) -> dict[str, Any]:
    mismatches: list[str] = []
    summary = _load_json(summary_path)
    gate_results = {
        "schema": "pass" if _schema_valid(summary, mismatches) else "fail",
        "gate_status": "pass" if _gate_status_valid(summary, mismatches) else "fail",
        "deterministic_gates": "pass" if _deterministic_gates_valid(summary, mismatches) else "fail",
        "artifact_paths": "pass"
        if _artifact_paths_valid(summary, summary_path, mismatches)
        else "fail",
        "boundary": "pass" if _boundary_valid(summary, mismatches) else "fail",
    }
    status = "pass" if all(value == "pass" for value in gate_results.values()) else "fail"
    return {
        "kind": "ai-fantui-phase1-demo-mvp-gate-summary-verification",
        "status": status,
        "summary": str(summary_path),
        "mismatches": mismatches,
        "deterministic_gates": gate_results,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify phase1_demo_mvp_gate_summary.json.",
    )
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP gate summary verified")
    else:
        print(f"FAIL: phase1 demo MVP gate summary drifted ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = verify_gate_summary(args.summary)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-phase1-demo-mvp-gate-summary-verification",
            "status": "fail",
            "summary": str(args.summary),
            "mismatches": ["runtime_error"],
            "deterministic_gates": {
                "schema": "fail",
                "gate_status": "fail",
                "deterministic_gates": "fail",
                "artifact_paths": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))

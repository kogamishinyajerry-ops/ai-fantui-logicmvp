#!/usr/bin/env python3
"""Verify a generated Phase 1 demo MVP review package."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = (
    Path("/tmp/ai-fantui-phase1-demo-mvp-review-package")
    / "phase1_demo_mvp_review_package_v0_1.json"
)
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_review_package_v0_1.schema.json"
)
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


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


def _restricted_diff() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *RESTRICTED_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ["<git diff failed>"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_json(SCHEMA_PATH)).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        mismatches.append(f"schema{'.' + path if path else ''}: {error.message}")
    return not errors


def _demo_gate_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if package.get("demo_surface") != {
        "route": "/demo-reconstruction",
        "title": "反推控制台复刻",
        "node_count": 20,
        "wire_count": 23,
        "preset_count": 5,
        "status_output_count": 6,
        "output_card_count": 4,
    }:
        mismatches.append("demo_surface must match demo.html reconstruction contract")
        valid = False
    if package.get("homepage_entry", {}).get("route") != "/demo-reconstruction":
        mismatches.append("homepage_entry.route must be /demo-reconstruction")
        valid = False
    if package.get("deterministic_gates", {}).get("demo_html_reconstruction_mvp") != "pass":
        mismatches.append("deterministic_gates.demo_html_reconstruction_mvp must be pass")
        valid = False
    if package.get("demo_gate", {}).get("status") != "pass":
        mismatches.append("demo_gate.status must be pass")
        valid = False
    return valid


def _browser_acceptance_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    browser = package.get("browser_acceptance", {})
    valid = True
    if package.get("deterministic_gates", {}).get("browser_acceptance") != "pass":
        mismatches.append("deterministic_gates.browser_acceptance must be pass")
        valid = False
    if browser.get("status") != "pass":
        mismatches.append("browser_acceptance.status must be pass")
        valid = False
    if browser.get("first_screen_review", {}).get("operator_guide_visible") is not True:
        mismatches.append("browser_acceptance.first_screen_review.operator_guide_visible must be true")
        valid = False
    if browser.get("deterministic_gates", {}).get("embedded_codex_light_palette") != "pass":
        mismatches.append("browser_acceptance.deterministic_gates.embedded_codex_light_palette must be pass")
        valid = False
    embedded_palette = browser.get("embedded_palette", {})
    if (
        embedded_palette.get("palette") != "codex-light"
        or embedded_palette.get("body_background") != "rgb(247, 248, 251)"
        or embedded_palette.get("panel_background") != "rgb(255, 255, 255)"
    ):
        mismatches.append("browser_acceptance.embedded_palette must prove codex-light body and panel colors")
        valid = False
    chain_svg = browser.get("pixel_visibility", {}).get("chain_svg", {})
    if chain_svg.get("status") != "pass" or chain_svg.get("node_count") != 20 or chain_svg.get("wire_count") != 23:
        mismatches.append("browser_acceptance.pixel_visibility.chain_svg must pass 20-node/23-wire check")
        valid = False
    max_reverse = browser.get("interactions", {}).get("max-reverse", {})
    inhibit = browser.get("interactions", {}).get("inhibit-block", {})
    if max_reverse.get("outputs", {}).get("thr_lock") != "ON":
        mismatches.append("browser_acceptance.max-reverse.thr_lock must be ON")
        valid = False
    if inhibit.get("outputs", {}).get("thr_lock") == "ON":
        mismatches.append("browser_acceptance.inhibit-block.thr_lock must not be ON")
        valid = False
    return valid


def _screenshots_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    screenshots = package.get("browser_acceptance", {}).get("screenshots")
    if not isinstance(screenshots, dict) or not screenshots:
        mismatches.append("browser_acceptance.screenshots must be non-empty")
        return False
    valid = True
    for key, path_value in screenshots.items():
        path = Path(path_value) if isinstance(path_value, str) else None
        if path is None or not path.exists() or path.stat().st_size == 0:
            mismatches.append(f"browser_acceptance.screenshots.{key} must exist")
            valid = False
    if package.get("deterministic_gates", {}).get("screenshots") != "pass":
        mismatches.append("deterministic_gates.screenshots must be pass")
        valid = False
    return valid


def _markdown_report_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    report_path = _resolve_path(package.get("artifact_paths", {}).get("markdown_report"), package_path)
    if report_path is None or not report_path.exists() or report_path.stat().st_size == 0:
        mismatches.append("artifact_paths.markdown_report must exist")
        return False
    text = report_path.read_text(encoding="utf-8")
    valid = True
    for fragment in ("反推控制台复刻", "非认证声明", "/demo-reconstruction", "embedded_codex_light_palette"):
        if fragment not in text:
            mismatches.append(f"markdown_report must contain {fragment}")
            valid = False
    if package.get("deterministic_gates", {}).get("markdown_report") != "pass":
        mismatches.append("deterministic_gates.markdown_report must be pass")
        valid = False
    return valid


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    expected_declaration = {
        "certification_claim": "none",
        "dal_claim": "none",
        "production_readiness_claim": "none",
        "controller_truth_promotion": "none",
    }
    if package.get("non_certification_declaration") != expected_declaration:
        mismatches.append("non_certification_declaration must preserve none claims")
        valid = False
    expected_boundaries = {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    if package.get("review_boundaries") != expected_boundaries:
        mismatches.append("review_boundaries must preserve demo-only boundaries")
        valid = False
    if _restricted_diff():
        mismatches.append("restricted diff must be empty")
        valid = False
    if package.get("deterministic_gates", {}).get("boundary") != "pass":
        mismatches.append("deterministic_gates.boundary must be pass")
        valid = False
    return valid


def verify_package(package_path: Path) -> dict[str, Any]:
    mismatches: list[str] = []
    package = _load_json(package_path)
    gate_results = {
        "schema": "pass" if _schema_valid(package, mismatches) else "fail",
        "demo_gate": "pass" if _demo_gate_valid(package, mismatches) else "fail",
        "browser_acceptance": "pass" if _browser_acceptance_valid(package, mismatches) else "fail",
        "screenshots": "pass" if _screenshots_valid(package, mismatches) else "fail",
        "markdown_report": "pass"
        if _markdown_report_valid(package, package_path=package_path, mismatches=mismatches)
        else "fail",
        "boundary": "pass" if _boundary_valid(package, mismatches) else "fail",
    }
    status = "pass" if all(value == "pass" for value in gate_results.values()) else "fail"
    return {
        "kind": "ai-fantui-phase1-demo-mvp-review-package-verification",
        "status": status,
        "package": str(package_path),
        "mismatches": mismatches,
        "deterministic_gates": gate_results,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify phase1_demo_mvp_review_package_v0_1.json.",
    )
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP review package verified")
    else:
        print(f"FAIL: phase1 demo MVP review package drifted ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = verify_package(args.package)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-phase1-demo-mvp-review-package-verification",
            "status": "fail",
            "package": str(args.package),
            "mismatches": ["runtime_error"],
            "deterministic_gates": {
                "schema": "fail",
                "demo_gate": "fail",
                "browser_acceptance": "fail",
                "screenshots": "fail",
                "markdown_report": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))

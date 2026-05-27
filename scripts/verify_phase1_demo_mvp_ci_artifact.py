#!/usr/bin/env python3
"""Verify a downloaded Phase 1 demo MVP CI artifact directory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-phase1-demo-mvp-ci-artifact")
PACKAGE_NAME = "phase1_demo_mvp_review_package_v0_1.json"
REPORT_NAME = "phase1_demo_mvp_review_report.md"
DEMO_GATE_NAME = "demo_html_reconstruction_mvp_gate.json"
BROWSER_ACCEPTANCE_NAME = "demo_html_reconstruction_browser_acceptance.json"
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "phase1_demo_mvp_review_package_v0_1.schema.json"
)
EXPECTED_DEMO_SURFACE = {
    "route": "/demo-reconstruction",
    "title": "demo.html 复刻 MVP 控制台",
    "node_count": 20,
    "wire_count": 23,
    "preset_count": 5,
    "status_output_count": 6,
    "output_card_count": 4,
}
EXPECTED_NON_CERTIFICATION_DECLARATION = {
    "certification_claim": "none",
    "dal_claim": "none",
    "production_readiness_claim": "none",
    "controller_truth_promotion": "none",
}
EXPECTED_REVIEW_BOUNDARIES = {
    "truth_effect": "none",
    "certification_claim": "none",
    "controller_truth_modified": False,
    "ui_layout_modified": False,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_artifact_path(path_value: Any, artifact_dir: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend(
            [
                artifact_dir / path,
                artifact_dir / path.name,
                artifact_dir / "browser-acceptance" / path.name,
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _file_ok(path: Path | None) -> bool:
    return path is not None and path.exists() and path.stat().st_size > 0


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_json(SCHEMA_PATH)).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        mismatches.append(f"package.schema{'.' + path if path else ''}: {error.message}")
    return not errors


def _package_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if not _schema_valid(package, mismatches):
        valid = False
    if package.get("kind") != "ai-fantui-phase1-demo-mvp-review-package":
        mismatches.append("package.kind must be ai-fantui-phase1-demo-mvp-review-package")
        valid = False
    if package.get("package_id") != "phase1-demo-mvp-review-package-v0.1":
        mismatches.append("package.package_id must be phase1-demo-mvp-review-package-v0.1")
        valid = False
    if package.get("status") != "pass":
        mismatches.append("package.status must be pass")
        valid = False
    expected_gates = {
        "demo_html_reconstruction_mvp": "pass",
        "browser_acceptance": "pass",
        "screenshots": "pass",
        "markdown_report": "pass",
        "boundary": "pass",
    }
    if package.get("deterministic_gates") != expected_gates:
        mismatches.append("package.deterministic_gates must all pass")
        valid = False
    if package.get("demo_surface") != EXPECTED_DEMO_SURFACE:
        mismatches.append("package.demo_surface must match demo.html reconstruction contract")
        valid = False
    if package.get("homepage_entry", {}).get("route") != "/demo-reconstruction":
        mismatches.append("package.homepage_entry.route must be /demo-reconstruction")
        valid = False
    return valid


def _markdown_report_valid(report_path: Path | None, mismatches: list[str]) -> bool:
    if not _file_ok(report_path):
        mismatches.append("markdown_report must exist and be non-empty")
        return False
    text = report_path.read_text(encoding="utf-8")
    valid = True
    for fragment in ("demo.html 复刻 MVP 控制台", "/demo-reconstruction", "非认证声明"):
        if fragment not in text:
            mismatches.append(f"markdown_report must contain {fragment}")
            valid = False
    return valid


def _child_json_valid(
    *,
    demo_gate_path: Path | None,
    browser_acceptance_path: Path | None,
    mismatches: list[str],
) -> bool:
    valid = True
    if not _file_ok(demo_gate_path):
        mismatches.append("child_json.demo_gate must exist and be non-empty")
        valid = False
    if not _file_ok(browser_acceptance_path):
        mismatches.append("child_json.browser_acceptance must exist and be non-empty")
        valid = False
    if not valid:
        return False
    try:
        demo_gate = _load_json(demo_gate_path)  # type: ignore[arg-type]
        browser_acceptance = _load_json(browser_acceptance_path)  # type: ignore[arg-type]
    except json.JSONDecodeError as exc:
        mismatches.append(f"child_json must parse: {exc}")
        return False
    if demo_gate.get("status") != "pass":
        mismatches.append("child_json.demo_gate.status must be pass")
        valid = False
    if browser_acceptance.get("status") != "pass":
        mismatches.append("child_json.browser_acceptance.status must be pass")
        valid = False
    return valid


def _screenshot_paths(
    package: dict[str, Any],
    artifact_dir: Path,
    mismatches: list[str],
) -> list[Path]:
    screenshots = package.get("browser_acceptance", {}).get("screenshots")
    if not isinstance(screenshots, dict) or not screenshots:
        mismatches.append("screenshots must be a non-empty browser_acceptance map")
        return []
    paths: list[Path] = []
    for key, path_value in screenshots.items():
        resolved = _resolve_artifact_path(path_value, artifact_dir)
        if not _file_ok(resolved):
            mismatches.append(f"screenshots.{key} must exist and be non-empty")
            continue
        paths.append(resolved)  # type: ignore[arg-type]
    return paths


def _browser_acceptance_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    browser = package.get("browser_acceptance", {})
    valid = True
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
    if (
        chain_svg.get("status") != "pass"
        or chain_svg.get("node_count") != 20
        or chain_svg.get("wire_count") != 23
    ):
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


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if package.get("non_certification_declaration") != EXPECTED_NON_CERTIFICATION_DECLARATION:
        mismatches.append("boundary.non_certification_declaration must preserve none claims")
        valid = False
    if package.get("review_boundaries") != EXPECTED_REVIEW_BOUNDARIES:
        mismatches.append("boundary.review_boundaries must preserve demo-only boundaries")
        valid = False
    return valid


def verify_ci_artifact(artifact_dir: Path) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    package_path = artifact_dir / PACKAGE_NAME
    report_path = artifact_dir / REPORT_NAME
    mismatches: list[str] = []
    required_files: list[Path] = [package_path, report_path]

    if not _file_ok(package_path):
        mismatches.append("package file must exist and be non-empty")
        gate_results = {
            "package": "fail",
            "markdown_report": "fail",
            "child_json": "fail",
            "screenshots": "fail",
            "browser_acceptance": "fail",
            "boundary": "fail",
        }
        return {
            "kind": "ai-fantui-phase1-demo-mvp-ci-artifact-verification",
            "status": "fail",
            "artifact_dir": str(artifact_dir),
            "artifact_paths": {
                "package": str(package_path),
                "markdown_report": str(report_path),
                "demo_gate_json": str(artifact_dir / DEMO_GATE_NAME),
                "browser_acceptance_json": str(artifact_dir / BROWSER_ACCEPTANCE_NAME),
                "screenshots": [],
            },
            "required_files": [str(path) for path in required_files],
            "mismatches": mismatches,
            "deterministic_gates": gate_results,
        }

    package = _load_json(package_path)
    artifact_paths = package.get("artifact_paths", {})
    demo_gate_path = _resolve_artifact_path(
        artifact_paths.get("demo_gate_json", DEMO_GATE_NAME),
        artifact_dir,
    )
    browser_acceptance_path = _resolve_artifact_path(
        artifact_paths.get("browser_acceptance_json", BROWSER_ACCEPTANCE_NAME),
        artifact_dir,
    )
    report_path = _resolve_artifact_path(
        artifact_paths.get("markdown_report", REPORT_NAME),
        artifact_dir,
    )
    screenshot_paths = _screenshot_paths(package, artifact_dir, mismatches)
    required_files = [
        path
        for path in [
            package_path,
            report_path,
            demo_gate_path,
            browser_acceptance_path,
            *screenshot_paths,
        ]
        if path is not None
    ]
    gate_results = {
        "package": "pass" if _package_valid(package, mismatches) else "fail",
        "markdown_report": "pass" if _markdown_report_valid(report_path, mismatches) else "fail",
        "child_json": "pass"
        if _child_json_valid(
            demo_gate_path=demo_gate_path,
            browser_acceptance_path=browser_acceptance_path,
            mismatches=mismatches,
        )
        else "fail",
        "screenshots": "pass"
        if screenshot_paths
        and len(screenshot_paths)
        == len(package.get("browser_acceptance", {}).get("screenshots", {}))
        else "fail",
        "browser_acceptance": "pass" if _browser_acceptance_valid(package, mismatches) else "fail",
        "boundary": "pass" if _boundary_valid(package, mismatches) else "fail",
    }
    status = "pass" if all(value == "pass" for value in gate_results.values()) else "fail"
    return {
        "kind": "ai-fantui-phase1-demo-mvp-ci-artifact-verification",
        "status": status,
        "artifact_dir": str(artifact_dir),
        "artifact_paths": {
            "package": str(package_path),
            "markdown_report": str(report_path) if report_path is not None else "",
            "demo_gate_json": str(demo_gate_path) if demo_gate_path is not None else "",
            "browser_acceptance_json": str(browser_acceptance_path)
            if browser_acceptance_path is not None
            else "",
            "screenshots": [str(path) for path in screenshot_paths],
        },
        "required_files": [str(path) for path in required_files],
        "mismatches": mismatches,
        "deterministic_gates": gate_results,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a downloaded phase1-demo-mvp-review-package artifact directory.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: phase1 demo MVP CI artifact directory verified")
    else:
        print(f"FAIL: phase1 demo MVP CI artifact drifted ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or [])
    try:
        payload = verify_ci_artifact(args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-phase1-demo-mvp-ci-artifact-verification",
            "status": "fail",
            "artifact_dir": str(args.artifact_dir),
            "artifact_paths": {
                "package": str(args.artifact_dir / PACKAGE_NAME),
                "markdown_report": str(args.artifact_dir / REPORT_NAME),
                "demo_gate_json": str(args.artifact_dir / DEMO_GATE_NAME),
                "browser_acceptance_json": str(args.artifact_dir / BROWSER_ACCEPTANCE_NAME),
                "screenshots": [],
            },
            "required_files": [],
            "mismatches": ["runtime_error"],
            "deterministic_gates": {
                "package": "fail",
                "markdown_report": "fail",
                "child_json": "fail",
                "screenshots": "fail",
                "browser_acceptance": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))

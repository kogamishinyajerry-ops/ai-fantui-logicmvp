#!/usr/bin/env python3
"""Validate the M24 PR preflight artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-pr-preflight")
PACKAGE_NAME = "multi_agent_pr_preflight_v0_1.json"
SCHEMA_NAME = "multi_agent_pr_preflight_v0_1.schema.json"
EXPECTED_ORDER = [
    "multi-agent-cursor-baseline-v0-2",
    "project-manager-status",
    "candidate-review-runtime-export",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
    "m24-pr-preflight",
]
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M24 multi-agent PR preflight.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--package", dest="package_path", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--skip-browser", action="store_true")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _package_path(*, artifact_dir: Path, package_path: Path | None) -> Path:
    if package_path is not None:
        return package_path
    return artifact_dir / PACKAGE_NAME


def _artifact_exists(path_value: Any) -> bool:
    if not isinstance(path_value, str) or not path_value:
        return False
    path = Path(path_value)
    return path.exists() and path.stat().st_size > 0


def _browser_skipped() -> dict[str, Any]:
    return {
        "status": "skipped",
        "mismatches": [],
        "screenshots": {},
        "states": {},
    }


def _required_browser_text(payload: dict[str, Any]) -> list[str]:
    required: list[str] = []
    gate = payload.get("browser_geometry_gate", {})
    if isinstance(gate, dict):
        for marker in gate.get("required_markers", []):
            if isinstance(marker, str) and marker:
                required.append(marker)
    for package in payload.get("pathspec_packages", []):
        if not isinstance(package, dict):
            continue
        for key in ("package_id", "label"):
            value = package.get(key)
            if isinstance(value, str) and value:
                required.append(value)
    required.extend(["Validation Plan", "Stage Commands", "Control-Plane Boundary"])
    return list(dict.fromkeys(required))


def _browser_state(
    html_path: Path,
    screenshot_dir: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    def fail(message: str) -> dict[str, Any]:
        return {
            "status": "fail",
            "mismatches": [message],
            "screenshots": {},
            "states": {},
        }

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        return fail(f"playwright is not available: {exc}")

    required_text = _required_browser_text(payload)
    expected_validation_count = int(payload.get("summary", {}).get("validation_command_count", 0))
    expected_stage_count = int(payload.get("summary", {}).get("stage_command_count", 0))
    mismatches: list[str] = []
    screenshots: dict[str, str] = {}
    states: dict[str, dict[str, Any]] = {}
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                for viewport in RESPONSIVE_VIEWPORTS:
                    page = browser.new_page(
                        viewport={"width": viewport["width"], "height": viewport["height"]},
                    )
                    try:
                        page.goto(html_path.resolve().as_uri(), wait_until="load")
                        page.wait_for_selector("h1", timeout=7000)
                        state = page.evaluate(
                            """(requiredText) => {
                                const bodyText = document.body?.innerText || "";
                                return {
                                    title: document.title,
                                    h1: document.querySelector("h1")?.textContent || "",
                                    pageWidth: document.documentElement.scrollWidth,
                                    viewportWidth: window.innerWidth,
                                    noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
                                    requiredTextPresent: requiredText.every((item) => bodyText.includes(item)),
                                    missingText: requiredText.filter((item) => !bodyText.includes(item)),
                                    packageCardCount: document.querySelectorAll(".package").length,
                                    validationCommandCount: document.querySelectorAll(".validation-command").length,
                                    stageCommandCount: document.querySelectorAll(".stage-command").length,
                                    sectionCount: document.querySelectorAll("section").length,
                                };
                            }""",
                            required_text,
                        )
                        screenshot_path = screenshot_dir / f"multi-agent-pr-preflight-{viewport['name']}.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                    except Exception as exc:
                        mismatches.append(f"{viewport['name']} browser verification failed: {exc}")
                        continue
                    finally:
                        page.close()
                    screenshots[viewport["name"]] = str(screenshot_path)
                    states[viewport["name"]] = state
                    if not state.get("noHorizontalOverflow"):
                        mismatches.append(f"{viewport['name']} viewport has horizontal page overflow")
                    if not state.get("requiredTextPresent"):
                        missing = ", ".join(state.get("missingText", []))
                        mismatches.append(f"{viewport['name']} viewport is missing required text: {missing}")
                    if state.get("packageCardCount") != len(EXPECTED_ORDER):
                        mismatches.append(f"{viewport['name']} viewport must expose all preflight package cards")
                    if state.get("validationCommandCount") != expected_validation_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all validation commands")
                    if state.get("stageCommandCount") != expected_stage_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all stage commands")
                    if int(state.get("sectionCount", 0)) < 5:
                        mismatches.append(f"{viewport['name']} viewport must expose the preflight sections")
            finally:
                browser.close()
    except Exception as exc:
        return fail(f"browser verification failed: {exc}")

    return {
        "status": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
        "screenshots": screenshots,
        "states": states,
    }


def verify_multi_agent_pr_preflight(
    package_path: Path,
    *,
    run_browser: bool = True,
) -> dict[str, Any]:
    mismatches: list[str] = []
    try:
        payload = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "package_path": str(package_path),
            "schema_valid": False,
            "html_exists": False,
            "markdown_exists": False,
            "browser_valid": False,
            "browser": _browser_skipped(),
            "mismatches": [f"package could not be loaded: {exc}"],
        }

    schema = _load_json(PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"preflight schema validation failed{location}: {error.message}")

    package_order = payload.get("pathspec_packages", [])
    observed_order = [
        package.get("package_id")
        for package in package_order
        if isinstance(package, dict)
    ]
    if observed_order != EXPECTED_ORDER:
        mismatches.append(f"pathspec package order must be {EXPECTED_ORDER!r}")

    validation_plan = payload.get("validation_plan", [])
    command_ids = [
        item.get("command_id")
        for item in validation_plan
        if isinstance(item, dict)
    ]
    if len(validation_plan) != 21:
        mismatches.append("validation_plan must contain 21 commands")
    if len(command_ids) != len(set(command_ids)):
        mismatches.append("validation command ids must be unique")
    if not all(
        isinstance(item, dict) and item.get("package_id") in EXPECTED_ORDER
        for item in validation_plan
    ):
        mismatches.append("validation commands must map to known packages")

    stage_commands = payload.get("stage_commands", [])
    if len(stage_commands) != 8:
        mismatches.append("stage_commands must contain 8 explicit commands")
    if not any(isinstance(command, str) and "git add -f --" in command for command in stage_commands):
        mismatches.append("stage commands must include git add -f for ignored Claude agents")
    protected_markers = [
        "src/well_harness/controller.py",
        "src/well_harness/runner.py",
        "src/well_harness/static/",
        "artifacts/",
        ".planning/",
    ]
    for command in stage_commands:
        if not isinstance(command, str):
            mismatches.append("stage commands must be strings")
            continue
        for marker in protected_markers:
            if marker in command:
                mismatches.append(f"stage command includes excluded marker {marker}")

    blockers = payload.get("blockers", [])
    if any(
        isinstance(item, dict)
        and "notion" in str(item.get("blocker_id", "")).lower()
        for item in blockers
    ):
        mismatches.append("external planning blockers must not be recorded as active blockers")

    pr_body = payload.get("pr_body", {})
    body = pr_body.get("body", "") if isinstance(pr_body, dict) else ""
    for marker in [
        "Repo, GitHub, and local artifacts",
        "git add -f --",
        "make verify-multi-agent-packaging-consolidation",
        "make verify-multi-agent-pr-preflight",
        "tests/test_multi_agent_pr_preflight.py",
        "docs/coordination/multi-agent-pr-preflight.md",
    ]:
        if marker not in body:
            mismatches.append(f"PR body missing marker: {marker}")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("preflight_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("preflight_markdown"))
    if not html_exists:
        mismatches.append("preflight_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("preflight_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["preflight_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent PR Preflight",
            "multi-agent-cursor-baseline-v0-2",
            "ultrawork-monitor",
            "m23-packaging-consolidation",
            "repo-github-local-artifacts",
            "git add -f --",
        ]:
            if marker not in html:
                mismatches.append(f"preflight HTML missing marker: {marker}")

    browser = _browser_skipped()
    if run_browser:
        if html_exists:
            browser = _browser_state(
                Path(str(artifact_paths["preflight_html"])),
                package_path.parent / "screenshots",
                payload,
            )
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["preflight_html artifact is unavailable"],
                "screenshots": {},
                "states": {},
            }
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])

    return {
        "status": "pass" if not mismatches else "fail",
        "package_path": str(package_path),
        "schema_valid": not errors,
        "html_exists": html_exists,
        "markdown_exists": markdown_exists,
        "browser_valid": browser["status"] == "pass",
        "browser": browser,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    result = verify_multi_agent_pr_preflight(
        _package_path(artifact_dir=args.artifact_dir, package_path=args.package_path),
        run_browser=not args.skip_browser,
    )
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for mismatch in result["mismatches"]:
            print(f"- {mismatch}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

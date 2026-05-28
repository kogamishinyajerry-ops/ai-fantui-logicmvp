#!/usr/bin/env python3
"""Validate the M23 packaging consolidation artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-packaging-consolidation")
PACKAGE_NAME = "multi_agent_packaging_consolidation_v0_1.json"
SCHEMA_NAME = "multi_agent_packaging_consolidation_v0_1.schema.json"
EXPECTED_ORDER = [
    "multi-agent-cursor-baseline-v0-2",
    "project-manager-status",
    "candidate-review-runtime-export",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "m23-packaging-consolidation",
]
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]
REQUIRED_TEXT = [
    "Multi-Agent Packaging Consolidation",
    "multi-agent-cursor-baseline-v0-2",
    "candidate-review-runtime-export",
    "ultrawork-monitor",
    "m22-operator-cockpit",
    "repo-github-local-artifacts",
    "git add -f --",
]
ALLOWED_RUNTIME_PATHSPECS = {
    "candidate-review-runtime-export": {"src/well_harness/demo_server.py"},
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M23 packaging consolidation.")
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


def _browser_state(html_path: Path, screenshot_dir: Path) -> dict[str, Any]:
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
                                    stageCommandCount: document.querySelectorAll("pre").length,
                                    sectionCount: document.querySelectorAll("section").length,
                                };
                            }""",
                            REQUIRED_TEXT,
                        )
                        screenshot_path = screenshot_dir / f"multi-agent-packaging-consolidation-{viewport['name']}.png"
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
                        mismatches.append(f"{viewport['name']} viewport must expose all packaging cards")
                    if int(state.get("stageCommandCount", 0)) < len(EXPECTED_ORDER):
                        mismatches.append(f"{viewport['name']} viewport must expose stage commands")
                    if int(state.get("sectionCount", 0)) < 4:
                        mismatches.append(f"{viewport['name']} viewport must expose the packaging sections")
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


def verify_multi_agent_packaging_consolidation(
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
        mismatches.append(f"packaging schema validation failed{location}: {error.message}")

    package_order = payload.get("package_order", [])
    observed_order = [
        package.get("package_id")
        for package in package_order
        if isinstance(package, dict)
    ]
    if observed_order != EXPECTED_ORDER:
        mismatches.append(f"package order must be {EXPECTED_ORDER!r}")

    for package in package_order if isinstance(package_order, list) else []:
        if not isinstance(package, dict):
            mismatches.append("package_order entries must be objects")
            continue
        if package.get("missing_pathspecs"):
            mismatches.append(f"{package.get('package_id')} has missing pathspecs")
        for pathspec in package.get("pathspecs", []) + package.get("forced_pathspecs", []):
            if pathspec.startswith("artifacts/") or pathspec.startswith(".planning/"):
                mismatches.append(f"{package.get('package_id')} includes excluded pathspec {pathspec}")
            package_id = str(package.get("package_id", ""))
            if pathspec in {
                "src/well_harness/controller.py",
                "src/well_harness/runner.py",
            } or (
                pathspec == "src/well_harness/demo_server.py"
                and pathspec not in ALLOWED_RUNTIME_PATHSPECS.get(package_id, set())
            ):
                mismatches.append(f"{package.get('package_id')} includes protected pathspec {pathspec}")

    excluded = payload.get("excluded_paths", [])
    for required in [
        "artifacts/**",
        "src/well_harness/controller.py",
        "src/well_harness/static/**",
        ".planning/**",
    ]:
        if required not in excluded:
            mismatches.append(f"excluded_paths must include {required}")

    blockers = payload.get("blockers", [])
    if any(
        isinstance(item, dict)
        and "notion" in str(item.get("blocker_id", "")).lower()
        for item in blockers
    ):
        mismatches.append("external planning blockers must not be recorded as active blockers")

    stage_commands = payload.get("stage_commands", [])
    if not any(isinstance(command, str) and "git add -f --" in command for command in stage_commands):
        mismatches.append("stage commands must include git add -f for ignored Claude agents")
    if not any(
        isinstance(command, str) and "docs/coordination/multi-agent-operator-cockpit.md" in command
        for command in stage_commands
    ):
        mismatches.append("stage commands must include M22 cockpit doc")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("package_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("package_markdown"))
    if not html_exists:
        mismatches.append("package_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("package_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["package_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Packaging Consolidation",
            "multi-agent-cursor-baseline-v0-2",
            "candidate-review-runtime-export",
            "ultrawork-monitor",
            "m22-operator-cockpit",
            "repo-github-local-artifacts",
        ]:
            if marker not in html:
                mismatches.append(f"package HTML missing marker: {marker}")

    browser = {
        "status": "skipped",
        "mismatches": [],
        "screenshots": {},
        "states": {},
    }
    if run_browser:
        if html_exists:
            browser = _browser_state(
                Path(str(artifact_paths["package_html"])),
                package_path.parent / "screenshots",
            )
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["package_html artifact is unavailable"],
                "screenshots": {},
                "states": {},
            }

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
    result = verify_multi_agent_packaging_consolidation(
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

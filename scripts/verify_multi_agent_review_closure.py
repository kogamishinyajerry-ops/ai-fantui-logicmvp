#!/usr/bin/env python3
"""Validate the M30 review-closure packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-review-closure")
PACKAGE_NAME = "multi_agent_review_closure_v0_1.json"
SCHEMA_NAME = "multi_agent_review_closure_v0_1.schema.json"
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M30 multi-agent review closure.")
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
    required: list[str] = [
        "Multi-Agent Review Closure",
        "Latest Codex clean",
        "Actionable threads",
    ]
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        for key in ("control_plane", "recommended_next_action", "remote_checks_state"):
            value = summary.get(key)
            if isinstance(value, str) and value:
                required.append(value)
    agent_team = payload.get("agent_team", {})
    if isinstance(agent_team, dict):
        mode = agent_team.get("mode")
        if isinstance(mode, str) and mode:
            required.append(mode)
        for agent in agent_team.get("active_agents", []):
            if isinstance(agent, dict):
                name = agent.get("name")
                if isinstance(name, str) and name:
                    required.append(name)
    for status in payload.get("gates", {}).values() if isinstance(payload.get("gates"), dict) else []:
        if isinstance(status, str) and status:
            required.append(status)
    for thread in payload.get("review_threads", []):
        if isinstance(thread, dict):
            classification = thread.get("classification")
            if isinstance(classification, str) and classification:
                required.append(classification)
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
    gates = payload.get("gates", {})
    agent_team = payload.get("agent_team", {})
    review_threads = payload.get("review_threads", [])
    pathspec_package = payload.get("pathspec_package", {})
    expected_gate_count = len(gates) if isinstance(gates, dict) else 0
    expected_agent_count = int(agent_team.get("team_size", 0)) if isinstance(agent_team, dict) else 0
    expected_thread_count = len(review_threads) if isinstance(review_threads, list) else 0
    expected_pathspec_count = (
        len(pathspec_package.get("pathspecs", []))
        if isinstance(pathspec_package, dict) and isinstance(pathspec_package.get("pathspecs", []), list)
        else 0
    )
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
                                    metricCount: document.querySelectorAll(".metric").length,
                                    gateRowCount: document.querySelectorAll(".gate-row").length,
                                    agentRowCount: document.querySelectorAll(".agent-row").length,
                                    threadRowCount: document.querySelectorAll(".thread-row").length,
                                    pathspecItemCount: document.querySelectorAll(".pathspec-item").length,
                                    tableScrollCount: document.querySelectorAll(".table-scroll").length,
                                    sectionCount: document.querySelectorAll("section").length,
                                };
                            }""",
                            required_text,
                        )
                        screenshot_path = screenshot_dir / f"multi-agent-review-closure-{viewport['name']}.png"
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
                    if state.get("metricCount") != 5:
                        mismatches.append(f"{viewport['name']} viewport must expose five summary metrics")
                    if state.get("gateRowCount") != expected_gate_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all gate rows")
                    if state.get("agentRowCount") != expected_agent_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all active agents")
                    if state.get("threadRowCount") != expected_thread_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all review thread rows")
                    if state.get("pathspecItemCount") != expected_pathspec_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all pathspec items")
                    if int(state.get("tableScrollCount", 0)) < 3:
                        mismatches.append(f"{viewport['name']} viewport must preserve scrollable tables")
                    if int(state.get("sectionCount", 0)) < 6:
                        mismatches.append(f"{viewport['name']} viewport must expose closure sections")
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


def verify_multi_agent_review_closure(
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
        mismatches.append(f"review closure schema validation failed{location}: {error.message}")

    if payload.get("status") not in {"ready_for_owner_acceptance", "ready_with_warnings"}:
        mismatches.append("review closure status must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("latest_clean_codex_result_found") is not True:
            mismatches.append("latest clean Codex result must be recorded")
        if summary.get("actionable_thread_count") != 0:
            mismatches.append("actionable_thread_count must be zero")
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must exclude external planning surfaces")
        if summary.get("recommended_next_action") not in {
            "project_owner_acceptance_or_merge_when_authorized",
        }:
            mismatches.append("recommended_next_action must be owner acceptance or authorized merge")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "latest_head_review",
            "actionable_threads",
            "pr_mergeability",
            "control_plane_boundary",
            "pathspec_boundary",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")

    agent_team = payload.get("agent_team", {})
    if not isinstance(agent_team, dict):
        mismatches.append("agent_team must be present")
    else:
        active_agents = agent_team.get("active_agents", [])
        names = {
            item.get("name")
            for item in active_agents
            if isinstance(item, dict)
        } if isinstance(active_agents, list) else set()
        if agent_team.get("mode") != "five_agent_context_cap":
            mismatches.append("agent_team.mode must be five_agent_context_cap")
        if agent_team.get("team_size") != 5 or len(names) != 5:
            mismatches.append("agent_team must define exactly five active agents")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("review closure packet must not record active blockers")

    pathspec_package = payload.get("pathspec_package", {})
    if not isinstance(pathspec_package, dict):
        mismatches.append("pathspec_package must be present")
    else:
        pathspecs = pathspec_package.get("pathspecs", [])
        if "src/well_harness/multi_agent_review_closure.py" not in pathspecs:
            mismatches.append("pathspec package must include review-closure source")
        excluded = pathspec_package.get("excluded_paths", [])
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        stage_command = str(pathspec_package.get("stage_command", ""))
        if ".planning/notion_control_plane.json" in stage_command:
            mismatches.append("stage command must not stage Notion control-plane config")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("closure_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("closure_markdown"))
    if not html_exists:
        mismatches.append("closure_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("closure_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["closure_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Review Closure",
            "Latest Codex clean",
            "Actionable threads",
            "repo_github_local_artifacts_only",
            "project_owner_acceptance_or_merge_when_authorized",
        ]:
            if marker not in html:
                mismatches.append(f"closure HTML missing marker: {marker}")

    browser = _browser_skipped()
    if run_browser:
        if html_exists:
            browser = _browser_state(
                Path(str(artifact_paths["closure_html"])),
                package_path.parent / "screenshots",
                payload,
            )
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["closure_html artifact is unavailable"],
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
    result = verify_multi_agent_review_closure(
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

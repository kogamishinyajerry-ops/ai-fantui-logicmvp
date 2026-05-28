#!/usr/bin/env python3
"""Validate the M32 owner acceptance handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-acceptance-handoff")
PACKAGE_NAME = "multi_agent_owner_acceptance_handoff_v0_1.json"
SCHEMA_NAME = "multi_agent_owner_acceptance_handoff_v0_1.schema.json"
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M32 owner acceptance handoff.")
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
        "Multi-Agent Owner Acceptance Handoff",
        "Owner Acceptance Checklist",
        "Decision Boundaries",
        "Active Agent Team",
    ]
    status = payload.get("status")
    if isinstance(status, str) and status:
        required.append(status)
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        for key in (
            "control_plane",
            "handoff_mode",
            "recommended_owner_action",
            "handoff_remote_checks_state",
        ):
            value = summary.get(key)
            if isinstance(value, str) and value:
                required.append(value)
    agent_team = payload.get("agent_team", {})
    if isinstance(agent_team, dict):
        mode = agent_team.get("mode")
        if isinstance(mode, str) and mode:
            required.append(mode)
        active_agents = agent_team.get("active_agents", [])
        if isinstance(active_agents, list):
            for agent in active_agents:
                if isinstance(agent, dict):
                    name = agent.get("name")
                    if isinstance(name, str) and name:
                        required.append(name)
    gates = payload.get("gates", {})
    if isinstance(gates, dict):
        for status_value in gates.values():
            if isinstance(status_value, str) and status_value:
                required.append(status_value)
    checklist = payload.get("owner_acceptance_checklist", [])
    if isinstance(checklist, list):
        for item in checklist:
            if isinstance(item, dict):
                for key in ("item_id", "status", "owner_action"):
                    value = item.get(key)
                    if isinstance(value, str) and value:
                        required.append(value)
    boundaries = payload.get("decision_boundaries", {})
    if isinstance(boundaries, dict):
        for key, value in boundaries.items():
            required.append(str(key))
            if isinstance(value, str) and value:
                required.append(value)
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
    checklist = payload.get("owner_acceptance_checklist", [])
    agent_team = payload.get("agent_team", {})
    boundaries = payload.get("decision_boundaries", {})
    pathspec_package = payload.get("pathspec_package", {})
    expected_gate_count = len(gates) if isinstance(gates, dict) else 0
    expected_checklist_count = len(checklist) if isinstance(checklist, list) else 0
    expected_agent_count = (
        int(agent_team.get("team_size", 0))
        if isinstance(agent_team, dict)
        else 0
    )
    expected_boundary_count = len(boundaries) if isinstance(boundaries, dict) else 0
    pathspecs = pathspec_package.get("pathspecs", []) if isinstance(pathspec_package, dict) else []
    expected_pathspec_count = len(pathspecs) if isinstance(pathspecs, list) else 0
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
                                    checklistRowCount: document.querySelectorAll(".checklist-row").length,
                                    agentRowCount: document.querySelectorAll(".agent-row").length,
                                    boundaryRowCount: document.querySelectorAll(".boundary-row").length,
                                    pathspecItemCount: document.querySelectorAll(".pathspec-item").length,
                                    tableScrollCount: document.querySelectorAll(".table-scroll").length,
                                    sectionCount: document.querySelectorAll("section").length,
                                };
                            }""",
                            required_text,
                        )
                        screenshot_path = (
                            screenshot_dir
                            / f"multi-agent-owner-acceptance-handoff-{viewport['name']}.png"
                        )
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
                    if state.get("checklistRowCount") != expected_checklist_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all checklist rows")
                    if state.get("agentRowCount") != expected_agent_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all active agents")
                    if state.get("boundaryRowCount") != expected_boundary_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all boundaries")
                    if state.get("pathspecItemCount") != expected_pathspec_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all pathspec items")
                    if int(state.get("tableScrollCount", 0)) < 4:
                        mismatches.append(f"{viewport['name']} viewport must preserve scrollable tables")
                    if int(state.get("sectionCount", 0)) < 7:
                        mismatches.append(f"{viewport['name']} viewport must expose handoff sections")
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


def verify_multi_agent_owner_acceptance_handoff(
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
        mismatches.append(f"owner acceptance handoff schema validation failed{location}: {error.message}")

    if payload.get("status") not in {
        "ready_for_owner_acceptance",
        "ready_for_owner_acceptance_with_warnings",
    }:
        mismatches.append("owner acceptance handoff must be ready, not blocked")

    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        mismatches.append("summary must be an object")
    else:
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must be repo_github_local_artifacts_only")
        if summary.get("handoff_mode") != "read_only_owner_acceptance_handoff":
            mismatches.append("handoff_mode must be read_only_owner_acceptance_handoff")
        if summary.get("current_actionable_thread_count") != 0:
            mismatches.append("current_actionable_thread_count must be zero")
        if summary.get("review_thread_fetch_error_count") != 0:
            mismatches.append("review_thread_fetch_error_count must be zero")
        if summary.get("release_decision_binding_match") is not True:
            mismatches.append("release_decision_binding_match must be true")
        if summary.get("handoff_remote_checks_state") not in {
            "pass",
            "no_checks_reported",
            "pending_or_unknown",
        }:
            mismatches.append("handoff_remote_checks_state must be pass or warning-compatible")

    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        mismatches.append("gates must be an object")
    else:
        for required in [
            "release_decision_input",
            "release_decision_binding",
            "release_decision_blockers",
            "review_thread_fetch",
            "current_actionable_reviews",
            "pr_mergeability",
            "control_plane_boundary",
            "owner_authority_boundary",
            "pathspec_boundary",
        ]:
            if gates.get(required) != "pass":
                mismatches.append(f"{required} gate must pass")
        if gates.get("remote_checks") not in {"pass", "warning"}:
            mismatches.append("remote_checks gate must be pass or warning")
        if gates.get("outdated_review_threads") not in {"pass", "warning"}:
            mismatches.append("outdated_review_threads gate must be pass or warning")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("owner acceptance handoff must not record active blockers")

    boundaries = payload.get("decision_boundaries", {})
    if not isinstance(boundaries, dict):
        mismatches.append("decision_boundaries must be present")
    else:
        expected = {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_final_decision": "external_manual_only",
            "notion_control_plane_changes": "out_of_scope",
        }
        for key, value in expected.items():
            if boundaries.get(key) != value:
                mismatches.append(f"{key} boundary must be {value}")

    checklist = payload.get("owner_acceptance_checklist", [])
    if not isinstance(checklist, list) or len(checklist) < 5:
        mismatches.append("owner_acceptance_checklist must include at least five items")
    else:
        checklist_ids = {item.get("item_id") for item in checklist if isinstance(item, dict)}
        for required in {
            "owner-review-pr-evidence",
            "owner-confirm-no-actionable-review",
            "owner-decide-remote-check-warning",
            "owner-preserve-boundary",
            "owner-final-decision-if-needed",
        }:
            if required not in checklist_ids:
                mismatches.append(f"owner_acceptance_checklist missing {required}")

    pathspec_package = payload.get("pathspec_package", {})
    if not isinstance(pathspec_package, dict):
        mismatches.append("pathspec_package must be present")
    else:
        pathspecs = pathspec_package.get("pathspecs", [])
        if "src/well_harness/multi_agent_owner_acceptance_handoff.py" not in pathspecs:
            mismatches.append("pathspec package must include M32 source")
        excluded = pathspec_package.get("excluded_paths", [])
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        if ".planning/notion_control_plane.json" in str(pathspec_package.get("stage_command", "")):
            mismatches.append("stage command must not stage Notion control-plane config")

    artifact_paths = payload.get("artifact_paths", {})
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    html_exists = _artifact_exists(artifact_paths.get("handoff_html"))
    markdown_exists = _artifact_exists(artifact_paths.get("handoff_markdown"))
    if not html_exists:
        mismatches.append("handoff_html artifact must exist and be non-empty")
    if not markdown_exists:
        mismatches.append("handoff_markdown artifact must exist and be non-empty")
    if html_exists:
        html = Path(str(artifact_paths["handoff_html"])).read_text(encoding="utf-8")
        for marker in [
            "Multi-Agent Owner Acceptance Handoff",
            "Owner Acceptance Checklist",
            "repo_github_local_artifacts_only",
            "external_manual_only",
            "notion_control_plane_changes",
        ]:
            if marker not in html:
                mismatches.append(f"handoff HTML missing marker: {marker}")

    browser = _browser_skipped()
    if run_browser:
        if html_exists:
            browser = _browser_state(
                Path(str(artifact_paths["handoff_html"])),
                package_path.parent / "screenshots",
                payload,
            )
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["handoff_html artifact is unavailable"],
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
    result = verify_multi_agent_owner_acceptance_handoff(
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

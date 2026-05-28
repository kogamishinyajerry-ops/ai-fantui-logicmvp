#!/usr/bin/env python3
"""Validate the M33 owner decision request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-owner-decision-request")
PACKAGE_NAME = "multi_agent_owner_decision_request_v0_1.json"
SCHEMA_NAME = "multi_agent_owner_decision_request_v0_1.schema.json"
TEMPLATE_NAME = "owner_decision_input_template_v0_1.json"
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify M33 owner decision request.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--package", type=Path, default=None)
    parser.add_argument("--schema", type=Path, default=PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--skip-browser", action="store_true")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        "Multi-Agent Owner Decision Request",
        "Decision input required",
        "Decision recorded",
        "Decision Input Template",
        "Active Agent Team",
    ]
    status = payload.get("status")
    if isinstance(status, str) and status:
        required.append(status)
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        for key in ("control_plane", "decision_request_mode", "remote_checks_state"):
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
    options = payload.get("decision_options", [])
    if isinstance(options, list):
        for item in options:
            if isinstance(item, dict):
                for key in ("option_id", "label", "effect"):
                    value = item.get(key)
                    if isinstance(value, str) and value:
                        required.append(value)
    template = payload.get("decision_input_template", {})
    if isinstance(template, dict):
        for key in ("template_mode", "decision", "remote_check_warning_acknowledged"):
            required.append(str(key))
            required.append(str(template.get(key)))
        attestation = template.get("attestation", {})
        if isinstance(attestation, dict):
            required.append("decision_is_explicit")
            required.append(str(attestation.get("decision_is_explicit")))
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
    options = payload.get("decision_options", [])
    agent_team = payload.get("agent_team", {})
    boundaries = payload.get("decision_boundaries", {})
    pathspec_package = payload.get("pathspec_package", {})
    expected_gate_count = len(gates) if isinstance(gates, dict) else 0
    expected_option_count = len(options) if isinstance(options, list) else 0
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
                                    optionRowCount: document.querySelectorAll(".option-row").length,
                                    agentRowCount: document.querySelectorAll(".agent-row").length,
                                    templateRowCount: document.querySelectorAll(".template-row").length,
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
                            / f"multi-agent-owner-decision-request-{viewport['name']}.png"
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
                    if state.get("optionRowCount") != expected_option_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all decision options")
                    if state.get("agentRowCount") != expected_agent_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all active agents")
                    if int(state.get("templateRowCount", 0)) < 4:
                        mismatches.append(f"{viewport['name']} viewport must expose template rows")
                    if state.get("boundaryRowCount") != expected_boundary_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all boundaries")
                    if state.get("pathspecItemCount") != expected_pathspec_count:
                        mismatches.append(f"{viewport['name']} viewport must expose all pathspec items")
                    if int(state.get("tableScrollCount", 0)) < 5:
                        mismatches.append(f"{viewport['name']} viewport must preserve scrollable tables")
                    if int(state.get("sectionCount", 0)) < 8:
                        mismatches.append(f"{viewport['name']} viewport must expose request sections")
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


def verify_multi_agent_owner_decision_request(
    package_path: Path,
    schema_path: Path,
    *,
    run_browser: bool = True,
) -> dict[str, Any]:
    """Verify schema and deterministic M33 owner decision request boundaries."""
    payload = _load_json(package_path)
    schema = _load_json(schema_path)
    mismatches: list[str] = []
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    for error in errors:
        location = f" at {'/'.join(str(part) for part in error.path)}" if error.path else ""
        mismatches.append(f"owner decision request schema validation failed{location}: {error.message}")

    if payload.get("status") not in {
        "awaiting_owner_decision",
        "awaiting_owner_decision_with_warnings",
    }:
        mismatches.append("owner decision request must await an explicit owner decision, not record one")

    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        if summary.get("decision_request_mode") != "read_only_owner_decision_request":
            mismatches.append("decision_request_mode must be read_only_owner_decision_request")
        if summary.get("decision_input_required") is not True:
            mismatches.append("decision_input_required must be true")
        if summary.get("decision_recorded") is not False:
            mismatches.append("decision_recorded must remain false")
        if summary.get("control_plane") != "repo_github_local_artifacts_only":
            mismatches.append("control_plane must stay repo_github_local_artifacts_only")
    else:
        mismatches.append("summary must be an object")

    gates = payload.get("gates", {})
    if isinstance(gates, dict):
        for required in (
            "owner_acceptance_handoff",
            "m32_active_blockers",
            "owner_decision_input_required",
            "owner_decision_authority",
            "control_plane_boundary",
            "pathspec_boundary",
        ):
            if gates.get(required) not in {"pass", "warning"}:
                mismatches.append(f"{required} gate must pass or warn")
    else:
        mismatches.append("gates must be an object")

    blockers = payload.get("blockers", [])
    if blockers:
        mismatches.append("owner decision request must not record active blockers")

    boundaries = payload.get("decision_boundaries", {})
    if isinstance(boundaries, dict):
        expected_boundaries = {
            "auto_merge": "forbidden",
            "self_approval": "forbidden",
            "resolve_review_threads": "forbidden",
            "owner_decision_recording": "external_manual_input_only",
            "notion_control_plane_changes": "out_of_scope",
        }
        for key, expected in expected_boundaries.items():
            if boundaries.get(key) != expected:
                mismatches.append(f"decision_boundaries.{key} must be {expected}")
    else:
        mismatches.append("decision_boundaries must be an object")

    options = payload.get("decision_options", [])
    option_ids = {
        item.get("option_id")
        for item in options
        if isinstance(item, dict)
    } if isinstance(options, list) else set()
    for required in (
        "accept_when_authorized",
        "wait_for_remote_checks",
        "request_review_followup",
        "return_to_development",
    ):
        if required not in option_ids:
            mismatches.append(f"decision_options missing {required}")

    template = payload.get("decision_input_template", {})
    if isinstance(template, dict):
        if template.get("template_mode") is not True:
            mismatches.append("decision_input_template must stay in template_mode")
        attestation = template.get("attestation", {})
        if not isinstance(attestation, dict) or attestation.get("decision_is_explicit") is not False:
            mismatches.append("decision_input_template must not be an explicit owner decision")
        acknowledged = set(attestation.get("acknowledged_boundaries", [])) if isinstance(attestation, dict) else set()
        if "notion_control_plane_out_of_scope" not in acknowledged:
            mismatches.append("decision_input_template must acknowledge Notion is out of scope")
    else:
        mismatches.append("decision_input_template must be an object")

    artifact_paths = payload.get("artifact_paths", {})
    if isinstance(artifact_paths, dict):
        for key in ("request_json", "request_markdown", "request_html", "decision_input_template"):
            path_value = artifact_paths.get(key)
            if not path_value or not Path(path_value).exists():
                mismatches.append(f"artifact_paths.{key} must exist")
        template_path = Path(artifact_paths.get("decision_input_template") or package_path.parent / TEMPLATE_NAME)
        if template_path.exists():
            written_template = _load_json(template_path)
            if written_template != template:
                mismatches.append("written decision input template must match package payload")
    else:
        mismatches.append("artifact_paths must be an object")

    pathspec_package = payload.get("pathspec_package", {})
    if isinstance(pathspec_package, dict):
        pathspecs = pathspec_package.get("pathspecs", [])
        excluded = pathspec_package.get("excluded_paths", [])
        if "src/well_harness/multi_agent_owner_decision_request.py" not in pathspecs:
            mismatches.append("pathspec package must include owner decision request source")
        if ".planning/notion_control_plane.json" not in excluded:
            mismatches.append("pathspec package must keep Notion control-plane config excluded")
        if ".planning/notion_control_plane.json" in str(pathspec_package.get("stage_command", "")):
            mismatches.append("stage command must not stage Notion control-plane config")
    else:
        mismatches.append("pathspec_package must be an object")

    html_path = Path(artifact_paths.get("request_html", "")) if isinstance(artifact_paths, dict) else Path()
    markdown_exists = (
        isinstance(artifact_paths, dict)
        and _artifact_exists(artifact_paths.get("request_markdown"))
    )
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        for marker in (
            "Multi-Agent Owner Decision Request",
            "Decision input required",
            "Decision recorded",
            "notion_control_plane_changes",
        ):
            if marker not in html:
                mismatches.append(f"HTML missing marker {marker!r}")

    browser = _browser_skipped()
    if run_browser:
        if html_path.exists():
            browser = _browser_state(
                html_path,
                package_path.parent / "screenshots",
                payload,
            )
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["request_html artifact is unavailable"],
                "screenshots": {},
                "states": {},
            }
            mismatches.extend([f"browser: {item}" for item in browser["mismatches"]])

    return {
        "status": "pass" if not mismatches else "fail",
        "package_path": str(package_path),
        "schema_valid": not errors,
        "html_exists": html_path.exists(),
        "markdown_exists": markdown_exists,
        "template_exists": (
            isinstance(artifact_paths, dict)
            and Path(artifact_paths.get("decision_input_template", "")).exists()
        ),
        "browser_valid": browser["status"] == "pass",
        "browser": browser,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    package_path = args.package or args.artifact_dir / PACKAGE_NAME
    result = verify_multi_agent_owner_decision_request(
        package_path,
        args.schema,
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

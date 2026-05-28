#!/usr/bin/env python3
"""Validate UltraWork monitor dashboard artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-ultrawork-monitor-dashboard")
DASHBOARD_NAME = "ultrawork_monitor_dashboard_v0_1.json"
SCHEMA_NAME = "ultrawork_monitor_dashboard_v0_1.schema.json"
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]
REQUIRED_TEXT = [
    "UltraWork Monitor",
    "five_agent_context_cap",
    "RUN-QUEUE-011",
    "LogicIRRepairAgent",
    "PackagingPRReadinessAgent",
    "No active blockers",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify an UltraWork monitor dashboard artifact.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_ARTIFACT_DIR,
        help="Directory containing ultrawork_monitor_dashboard_v0_1.json.",
    )
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=None,
        help="Explicit dashboard JSON path. Overrides --artifact-dir.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--skip-browser",
        action="store_true",
        help="Skip local HTML screenshot and geometry checks.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dashboard_path(*, artifact_dir: Path, dashboard_path: Path | None) -> Path:
    if dashboard_path is not None:
        return dashboard_path
    return artifact_dir / DASHBOARD_NAME


def _browser_state(html_path: Path, screenshot_dir: Path, *, expected_lane_count: int) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        return {
            "status": "fail",
            "mismatches": [f"playwright is not available: {exc}"],
            "screenshots": {},
            "states": {},
        }

    mismatches: list[str] = []
    screenshots: dict[str, str] = {}
    states: dict[str, dict[str, Any]] = {}
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            for viewport in RESPONSIVE_VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": viewport["width"], "height": viewport["height"]},
                )
                page.goto(html_path.resolve().as_uri(), wait_until="load")
                page.wait_for_selector("h1", timeout=7000)
                state = page.evaluate(
                    """(requiredText) => {
                        const bodyText = document.body?.innerText || "";
                        const sections = [...document.querySelectorAll("section")].map((section) => (
                            section.querySelector("h2")?.textContent || ""
                        ));
                        const scrollContainers = [...document.querySelectorAll(".table-scroll")].map((element) => {
                            const rect = element.getBoundingClientRect();
                            return {
                                width: Math.round(rect.width),
                                scrollWidth: element.scrollWidth,
                                hasInternalOverflow: element.scrollWidth > element.clientWidth + 2,
                            };
                        });
                        return {
                            title: document.title,
                            h1: document.querySelector("h1")?.textContent || "",
                            pageWidth: document.documentElement.scrollWidth,
                            viewportWidth: window.innerWidth,
                            noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
                            requiredTextPresent: requiredText.every((item) => bodyText.includes(item)),
                            missingText: requiredText.filter((item) => !bodyText.includes(item)),
                            sectionHeadings: sections,
                            metricCount: document.querySelectorAll(".metric").length,
                            agentRowCount: document.querySelectorAll("section:nth-of-type(1) tbody tr").length,
                            laneRowCount: document.querySelectorAll("section:nth-of-type(3) tbody tr").length,
                            gateCount: document.querySelectorAll("section:nth-of-type(4) li").length,
                            tableScrollCount: scrollContainers.length,
                            scrollContainers,
                        };
                    }""",
                    REQUIRED_TEXT,
                )
                screenshot_path = screenshot_dir / f"ultrawork-monitor-dashboard-{viewport['name']}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
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
                if state.get("agentRowCount") != 5:
                    mismatches.append(f"{viewport['name']} viewport must expose the five-agent team")
                if int(state.get("laneRowCount", 0)) < expected_lane_count:
                    mismatches.append(f"{viewport['name']} viewport must expose completed plus resumable lanes")
                if int(state.get("gateCount", 0)) < 5:
                    mismatches.append(f"{viewport['name']} viewport must expose all deterministic gates")
                if int(state.get("tableScrollCount", 0)) < 2:
                    mismatches.append(f"{viewport['name']} viewport must wrap wide tables in scroll containers")
                if viewport["name"] == "mobile" and not any(
                    item.get("hasInternalOverflow")
                    for item in state.get("scrollContainers", [])
                    if isinstance(item, dict)
                ):
                    mismatches.append("mobile viewport must keep wide tables inside internal scroll containers")
        finally:
            browser.close()

    return {
        "status": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
        "screenshots": screenshots,
        "states": states,
    }


def verify_ultrawork_monitor_dashboard(
    dashboard_path: Path,
    *,
    run_browser: bool = True,
) -> dict[str, Any]:
    mismatches: list[str] = []
    try:
        payload = _load_json(dashboard_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "dashboard_path": str(dashboard_path),
            "schema_valid": False,
            "html_exists": False,
            "browser_valid": False,
            "mismatches": [f"dashboard could not be loaded: {exc}"],
            "browser": {
                "status": "fail",
                "mismatches": [],
                "screenshots": {},
                "states": {},
            },
        }
    schema = _load_json(PROJECT_ROOT / "docs" / "json_schema" / SCHEMA_NAME)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"dashboard schema validation failed{location}: {error.message}")

    artifact_paths = payload.get("artifact_paths", {})
    summary = payload.get("summary", {})
    html_path = Path(str(artifact_paths.get("dashboard_html", ""))) if isinstance(artifact_paths, dict) else Path()
    html_exists = html_path.exists() and html_path.stat().st_size > 0
    if not html_exists:
        mismatches.append("dashboard_html artifact must exist and be non-empty")
    browser = {
        "status": "skipped",
        "mismatches": [],
        "screenshots": {},
        "states": {},
    }
    if run_browser:
        if html_exists:
            expected_lane_count = 0
            if isinstance(summary, dict):
                expected_lane_count = int(summary.get("completed_count", 0)) + int(
                    summary.get("open_approved_count", 0)
                )
            browser = _browser_state(
                html_path,
                dashboard_path.parent / "screenshots",
                expected_lane_count=expected_lane_count,
            )
            mismatches.extend(browser["mismatches"])
        else:
            browser = {
                "status": "fail",
                "mismatches": ["dashboard_html artifact is missing"],
                "screenshots": {},
                "states": {},
            }

    blockers = payload.get("blockers", [])
    if any(
        isinstance(item, dict)
        and "notion" in str(item.get("blocker_id", "")).lower()
        for item in blockers
    ):
        mismatches.append("external planning blockers must not be recorded as active blockers")

    agent_team = payload.get("agent_team", {})
    expected_agents = {
        "ChiefEngineerOrchestrator",
        "LogicIRRepairAgent",
        "EvidenceValidationAgent",
        "SafetyRequirementsReviewer",
        "PackagingPRReadinessAgent",
    }
    if not isinstance(agent_team, dict):
        mismatches.append("agent_team must be present")
    else:
        active_agents = agent_team.get("active_agents", [])
        if isinstance(active_agents, list):
            names = {item.get("name") for item in active_agents if isinstance(item, dict)}
        else:
            names = set()
        if agent_team.get("mode") != "five_agent_context_cap":
            mismatches.append("agent_team.mode must be five_agent_context_cap")
        if agent_team.get("team_size") != 5 or names != expected_agents:
            mismatches.append("agent_team must define exactly five active agents")

    lanes = payload.get("agent_lanes", [])
    if isinstance(summary, dict) and isinstance(lanes, list):
        expected_minimum = int(summary.get("completed_count", 0)) + int(
            summary.get("open_approved_count", 0)
        )
        if len(lanes) < expected_minimum:
            mismatches.append("agent_lanes must cover completed and open approved records")
        lane_agents = {
            item.get("agent")
            for item in lanes
            if isinstance(item, dict)
        }
        if not lane_agents.issubset(expected_agents):
            mismatches.append("agent_lanes must only use the capped five-agent team")

    return {
        "status": "pass" if not mismatches else "fail",
        "dashboard_path": str(dashboard_path),
        "schema_valid": not errors,
        "html_exists": html_exists,
        "browser_valid": browser["status"] == "pass",
        "browser": browser,
        "mismatches": mismatches,
    }


def main() -> int:
    args = _parse_args()
    result = verify_ultrawork_monitor_dashboard(
        _dashboard_path(artifact_dir=args.artifact_dir, dashboard_path=args.dashboard),
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

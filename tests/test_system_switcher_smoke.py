"""Headless Playwright smoke test for the system switcher UI at http://localhost:7891/."""

from __future__ import annotations

import json
import sys
from typing import Any


DEMO_URL = "http://localhost:7891/"

OUTPUT_FORMATS = {"text", "json"}

SYSTEMS = ("thrust-reverser", "landing-gear", "bleed-air")


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: test_system_switcher_smoke.py [--format text|json]")


def _topology_visible(page: Any, system: str) -> bool:
    """Return True if the topology for *system* is visible (display != none)."""
    locator = page.locator(f"#chain-topology-{system}")
    try:
        return locator.is_visible(timeout=3000)
    except Exception:
        return False


def _topology_hidden(page: Any, system: str) -> bool:
    """Return True if the topology for *system* is NOT visible."""
    locator = page.locator(f"#chain-topology-{system}")
    try:
        return not locator.is_visible(timeout=3000)
    except Exception:
        return True


def run_smoke() -> tuple[int, dict[str, Any], list[str]]:
    """Run the system-switcher smoke suite.

    Returns (exit_code, report, text_lines) — same contract as demo_path_smoke.run_smoke_suite().
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        report: dict[str, Any] = {
            "status": "fail",
            "error": "playwright not installed; run: pip install playwright && playwright install chromium",
            "scenarios": [],
        }
        return 1, report, ["FAIL: playwright is not installed"]

    console_errors: list[str] = []

    report = {
        "status": "pass",
        "scenario_count": 9,
        "completed_scenarios": 0,
        "failed_scenario": None,
        "scenarios": [],
        "console_errors": [],
    }
    text_lines: list[str] = []

    def _pass(name: str, detail: str) -> dict[str, Any]:
        return {"name": name, "status": "pass", "detail": detail}

    def _fail(name: str, detail: str) -> dict[str, Any]:
        return {"name": name, "status": "fail", "detail": detail}

    def _record(scenario: dict[str, Any]) -> bool:
        report["scenarios"].append(scenario)
        report["completed_scenarios"] += 1
        prefix = "OK" if scenario["status"] == "pass" else "FAIL"
        text_lines.append(f"{prefix} {scenario['name']}: {scenario['detail']}")
        return scenario["status"] == "pass"

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Capture console errors (Error level only)
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
            )

            # --- Scenario 1: Page loads ---
            try:
                page.goto(DEMO_URL, timeout=10000, wait_until="domcontentloaded")
                title = page.title()
                if title:
                    ok = _record(_pass("page_loads", f"page title is '{title}'"))
                else:
                    ok = _record(_fail("page_loads", "page title is empty after navigation"))
            except Exception as exc:
                ok = _record(_fail("page_loads", f"navigation failed: {exc}"))

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "page_loads"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 2: System selector exists ---
            selector_loc = page.locator("#system-selector")
            if selector_loc.count() > 0:
                ok = _record(_pass("system_selector_exists", "#system-selector is present in the DOM"))
            else:
                ok = _record(_fail("system_selector_exists", "#system-selector not found in the DOM"))

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "system_selector_exists"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 3: System selector has exactly 3 options with correct values ---
            options = page.locator("#system-selector option")
            option_count = options.count()
            option_values = [options.nth(i).get_attribute("value") for i in range(option_count)]
            expected_values = list(SYSTEMS)
            if option_count == 3 and option_values == expected_values:
                ok = _record(
                    _pass(
                        "system_selector_options",
                        f"3 options found with values {option_values}",
                    )
                )
            else:
                ok = _record(
                    _fail(
                        "system_selector_options",
                        f"expected 3 options {expected_values} but got {option_count}: {option_values}",
                    )
                )

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "system_selector_options"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 4: Switch to landing-gear ---
            page.select_option("#system-selector", "landing-gear")
            page.wait_for_timeout(300)
            lg_visible = _topology_visible(page, "landing-gear")
            tr_hidden = _topology_hidden(page, "thrust-reverser")
            ba_hidden = _topology_hidden(page, "bleed-air")
            if lg_visible and tr_hidden and ba_hidden:
                ok = _record(
                    _pass(
                        "switch_to_landing_gear",
                        "#chain-topology-landing-gear visible; others hidden",
                    )
                )
            else:
                ok = _record(
                    _fail(
                        "switch_to_landing_gear",
                        f"landing-gear visible={lg_visible}, thrust-reverser hidden={tr_hidden}, bleed-air hidden={ba_hidden}",
                    )
                )

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "switch_to_landing_gear"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 5: Switch to bleed-air ---
            page.select_option("#system-selector", "bleed-air")
            page.wait_for_timeout(300)
            ba_visible = _topology_visible(page, "bleed-air")
            tr_hidden2 = _topology_hidden(page, "thrust-reverser")
            lg_hidden2 = _topology_hidden(page, "landing-gear")
            if ba_visible and tr_hidden2 and lg_hidden2:
                ok = _record(
                    _pass(
                        "switch_to_bleed_air",
                        "#chain-topology-bleed-air visible; others hidden",
                    )
                )
            else:
                ok = _record(
                    _fail(
                        "switch_to_bleed_air",
                        f"bleed-air visible={ba_visible}, thrust-reverser hidden={tr_hidden2}, landing-gear hidden={lg_hidden2}",
                    )
                )

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "switch_to_bleed_air"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 6: Switch back to thrust-reverser ---
            page.select_option("#system-selector", "thrust-reverser")
            page.wait_for_timeout(300)
            tr_visible = _topology_visible(page, "thrust-reverser")
            lg_hidden3 = _topology_hidden(page, "landing-gear")
            ba_hidden3 = _topology_hidden(page, "bleed-air")
            if tr_visible and lg_hidden3 and ba_hidden3:
                ok = _record(
                    _pass(
                        "switch_back_to_thrust_reverser",
                        "#chain-topology-thrust-reverser visible; others hidden",
                    )
                )
            else:
                ok = _record(
                    _fail(
                        "switch_back_to_thrust_reverser",
                        f"thrust-reverser visible={tr_visible}, landing-gear hidden={lg_hidden3}, bleed-air hidden={ba_hidden3}",
                    )
                )

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "switch_back_to_thrust_reverser"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 7: Monitor panel visible ---
            monitor_visible = page.locator(".monitor-panel").is_visible(timeout=3000)
            if monitor_visible:
                ok = _record(_pass("monitor_panel_visible", ".monitor-panel is visible"))
            else:
                ok = _record(_fail("monitor_panel_visible", ".monitor-panel is not visible"))

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "monitor_panel_visible"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 8: Monitor checkboxes rendered ---
            # Wait briefly for JS to populate checkboxes
            page.wait_for_timeout(500)
            checkbox_count = page.locator("#monitor-series-checkboxes input[type=checkbox]").count()
            if checkbox_count > 0:
                ok = _record(
                    _pass(
                        "monitor_checkboxes_rendered",
                        f"#monitor-series-checkboxes has {checkbox_count} checkbox(es)",
                    )
                )
            else:
                ok = _record(
                    _fail(
                        "monitor_checkboxes_rendered",
                        "#monitor-series-checkboxes has 0 checkboxes (expected > 0)",
                    )
                )

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "monitor_checkboxes_rendered"
                report["console_errors"] = list(console_errors)
                return 1, report, text_lines

            # --- Scenario 9: No console errors ---
            report["console_errors"] = list(console_errors)
            if not console_errors:
                ok = _record(_pass("no_console_errors", "no browser console errors detected"))
            else:
                ok = _record(
                    _fail(
                        "no_console_errors",
                        f"{len(console_errors)} console error(s): {console_errors[:3]}",
                    )
                )

            context.close()
            browser.close()

            if not ok:
                report["status"] = "fail"
                report["failed_scenario"] = "no_console_errors"
                return 1, report, text_lines

    except Exception as exc:
        report["status"] = "fail"
        report["error"] = str(exc)
        report["console_errors"] = list(console_errors)
        text_lines.append(f"FAIL: unexpected error: {exc}")
        return 1, report, text_lines

    text_lines.append("PASS: system switcher smoke")
    return 0, report, text_lines


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    exit_code, report, text_lines = run_smoke()

    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for line in text_lines:
            print(line)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Browser gate for the compact /logic-builder surface."""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from scripts.verify_m21_streamed_authoring_revision_browser_gate import (
    _scenario_fixture,
    _seed_script,
)
from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "logic-builder-surface-gate"
SUMMARY_NAME = "logic_builder_surface_gate.json"
VIEWPORTS = (
    {"name": "desktop", "width": 1365, "height": 900},
    {"name": "mobile", "width": 390, "height": 844},
)
BANNED_VISIBLE_TEXT = (
    "模型",
    "DEEPSEEK STREAM",
    "DeepSeek 绘图回放",
    "DeepSeek V4 Pro",
    "MiniMax-M2.7-highspeed",
    "DeepSeek 绘图",
    "DeepSeek 正在绘制",
    "raw JSON",
    "导出审查包",
    "打开证据追溯",
    "打开报告预览",
    "回放报告预览",
)
EXPECTED_VISIBLE_TEXT = ("生成方式", "标准生成", "备用生成")
EXPECTED_DOM_TEXT = ("打开证据链接", "打开交付摘要", "生成交付摘要", "交付摘要预览")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _start_server() -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    return server, thread, f"http://127.0.0.1:{port}"


def _evaluate_surface(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """({banned, expectedVisible, expectedDom}) => {
          const timeline = document.querySelector("#logic-drawing-stream-timeline");
          const defaultText = document.body.innerText || "";
          const domText = document.documentElement.textContent || "";
          const defaultState = {
            tag: timeline?.tagName,
            hiddenAttr: timeline?.hasAttribute("hidden"),
            display: timeline ? getComputedStyle(timeline).display : null,
            bodyMode: document.body.dataset.logicInteractionMode,
            bannedVisible: banned.filter((needle) => defaultText.includes(needle)),
            replacementDomText: expectedDom.filter((needle) => domText.includes(needle)),
          };
          document.body.dataset.logicInteractionMode = "workbench";
          const events = document.querySelector("#logic-drawing-stream-events");
          const title = timeline?.querySelector(".logic-stream-head strong");
          const visibleText = document.body.innerText || "";
          const closedRect = timeline?.getBoundingClientRect();
          const closed = {
            open: timeline?.hasAttribute("open"),
            defaultCollapsed: timeline?.dataset.defaultCollapsed,
            title: title?.textContent?.trim(),
            eventCount: Number(timeline?.dataset.eventCount || 0),
            eventsDisplay: events ? getComputedStyle(events).display : null,
            rect: closedRect
              ? {x: closedRect.x, y: closedRect.y, width: closedRect.width, height: closedRect.height}
              : null,
            display: timeline ? getComputedStyle(timeline).display : null,
            bannedVisible: banned.filter((needle) => visibleText.includes(needle)),
            expectedVisibleText: expectedVisible.filter((needle) => visibleText.includes(needle)),
            replacementDomText: expectedDom.filter((needle) => domText.includes(needle)),
          };
          timeline.open = true;
          const openRect = timeline.getBoundingClientRect();
          const opened = {
            open: timeline.hasAttribute("open"),
            eventsDisplay: getComputedStyle(events).display,
            rect: {x: openRect.x, y: openRect.y, width: openRect.width, height: openRect.height},
          };
          return {defaultState, closed, opened};
        }""",
        {
            "banned": list(BANNED_VISIBLE_TEXT),
            "expectedVisible": list(EXPECTED_VISIBLE_TEXT),
            "expectedDom": list(EXPECTED_DOM_TEXT),
        },
    )


def _viewport_failures(observed: dict[str, Any], console_errors: list[str]) -> list[str]:
    failures: list[str] = []
    default_state = observed["defaultState"]
    closed = observed["closed"]
    opened = observed["opened"]
    if default_state.get("tag") != "DETAILS":
        failures.append("timeline is not details")
    if default_state.get("display") != "none":
        failures.append("default natural-language view exposes timeline")
    if default_state.get("bannedVisible"):
        failures.append("banned text visible by default: " + ", ".join(default_state["bannedVisible"]))
    if sorted(default_state.get("replacementDomText") or []) != sorted(EXPECTED_DOM_TEXT):
        failures.append("replacement labels missing from DOM")
    if closed.get("display") == "none":
        failures.append("workbench timeline did not become visible")
    if closed.get("open") is not False:
        failures.append("timeline not closed by default")
    if closed.get("defaultCollapsed") != "true":
        failures.append("missing default collapsed marker")
    if not re.match(r"^生成过程已完成 · [1-9][0-9]* 步$", closed.get("title") or ""):
        failures.append("unexpected closed title")
    if closed.get("eventCount", 0) < 1:
        failures.append("missing stream event count")
    if closed.get("eventsDisplay") != "none":
        failures.append("closed event list is visible")
    if not closed.get("rect") or closed["rect"]["height"] > 52:
        failures.append("closed timeline too tall")
    if closed.get("bannedVisible"):
        failures.append("banned text visible in workbench: " + ", ".join(closed["bannedVisible"]))
    if sorted(closed.get("expectedVisibleText") or []) != sorted(EXPECTED_VISIBLE_TEXT):
        failures.append("expected visible provider labels missing")
    if sorted(closed.get("replacementDomText") or []) != sorted(EXPECTED_DOM_TEXT):
        failures.append("expected replacement labels missing")
    if opened.get("open") is not True:
        failures.append("timeline did not open")
    if opened.get("eventsDisplay") == "none":
        failures.append("opened events remain hidden")
    if not opened.get("rect") or opened["rect"]["height"] <= closed["rect"]["height"]:
        failures.append("opened timeline did not expand")
    if console_errors:
        failures.append("console errors: " + " | ".join(console_errors[:3]))
    return failures


def verify_logic_builder_surface(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_stamp()
    seed_script = _seed_script(_scenario_fixture("fantui"))
    server, _thread, base_url = _start_server()
    results: dict[str, Any] = {}
    errors: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                for viewport in VIEWPORTS:
                    name = viewport["name"]
                    page = browser.new_page(
                        viewport={"width": viewport["width"], "height": viewport["height"]}
                    )
                    page.add_init_script(seed_script)
                    console_errors: list[str] = []
                    page.on(
                        "console",
                        lambda msg: console_errors.append(msg.text)
                        if msg.type == "error"
                        else None,
                    )
                    page.goto(f"{base_url}/logic-builder", wait_until="networkidle")
                    page.wait_for_selector(
                        "#logic-drawing-stream-timeline",
                        state="attached",
                        timeout=10000,
                    )
                    observed = _evaluate_surface(page)
                    screenshot_path = artifact_dir / f"logic-builder-surface-{name}-{stamp}.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    failures = _viewport_failures(observed, console_errors)
                    results[name] = {
                        **observed,
                        "screenshot": str(screenshot_path),
                        "failures": failures,
                    }
                    errors.extend(f"{name}: {failure}" for failure in failures)
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()

    gates = {
        "default_hidden": "pass"
        if all(result["defaultState"].get("display") == "none" for result in results.values())
        else "fail",
        "workbench_collapsed": "pass"
        if all(not result["closed"].get("open") for result in results.values())
        else "fail",
        "timeline_expandable": "pass"
        if all(result["opened"].get("open") for result in results.values())
        else "fail",
        "copy_boundary": "pass" if not errors else "fail",
        "responsive": "pass" if len(results) == len(VIEWPORTS) and not errors else "fail",
    }
    status = "pass" if all(value == "pass" for value in gates.values()) else "fail"
    payload = {
        "kind": "ai-fantui-logic-builder-surface-gate",
        "version": 1,
        "status": status,
        "route": "/logic-builder",
        "base_url": base_url,
        "artifact_dir": str(artifact_dir),
        "results": results,
        "screenshots": {name: result["screenshot"] for name, result in results.items()},
        "console_errors": {
            name: result["failures"]
            for name, result in results.items()
            if result["failures"]
        },
        "deterministic_gates": gates,
    }
    (artifact_dir / SUMMARY_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify compact /logic-builder surface behavior.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: /logic-builder surface gate passed")
    else:
        failed = [
            key
            for key, value in payload.get("deterministic_gates", {}).items()
            if value != "pass"
        ]
        print(f"FAIL: /logic-builder surface gate failed ({', '.join(failed)})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = verify_logic_builder_surface(args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-logic-builder-surface-gate",
            "version": 1,
            "status": "fail",
            "route": "/logic-builder",
            "error": str(exc),
            "screenshots": {},
            "console_errors": {},
            "deterministic_gates": {
                "default_hidden": "fail",
                "workbench_collapsed": "fail",
                "timeline_expandable": "fail",
                "copy_boundary": "fail",
                "responsive": "fail",
            },
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Browser acceptance for /docx-to-circuit review links."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "docx-to-circuit-review-links"
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/runner.py",
    "src/well_harness/controller_adapter.py",
    "src/well_harness/adapters",
    "docs/json_schema",
    ".planning",
    "tools/gsd_notion_sync.py",
]
RESPONSIVE_VIEWPORTS = [
    {"name": "desktop", "width": 1366, "height": 768, "expected_columns": "three"},
    {"name": "tablet", "width": 900, "height": 900, "expected_columns": "single"},
    {"name": "mobile", "width": 390, "height": 844, "expected_columns": "single"},
]


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


def _start_server() -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    return server, thread, f"http://127.0.0.1:{port}"


def _hash_params(url: str) -> dict[str, str]:
    fragment = urlparse(url).fragment
    parsed = parse_qs(fragment, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items() if values}


def _page_state(page: Any) -> dict[str, Any]:
    page.wait_for_selector('#docx-circuit-svg[data-rendered="true"]', timeout=7000)
    return page.evaluate(
        """() => ({
            hash: window.location.hash,
            activeAnchor: document.querySelector("#docx-circuit-review-panel")?.dataset.activeAnchor || null,
            sourceAnchor: document.querySelector("#docx-circuit-source-anchor")?.textContent || null,
            activeSourceEntryAnchor: document.querySelector(
                "#docx-circuit-source-index-list [data-source-entry-anchor][data-active='true']"
            )?.dataset.sourceEntryAnchor || null,
            activeSourceEntryLabel: document.querySelector("#docx-circuit-active-source-entry")?.textContent || null,
            sourceFocusVisible: (() => {
                const element = document.querySelector("#docx-circuit-source-focus");
                return Boolean(element) && element.dataset.hasSource === "true" && getComputedStyle(element).display !== "none";
            })(),
            sourceFocusButtonDisabled: document.querySelector("#docx-circuit-show-source-entry")?.disabled || false,
            focusedSourceEntryAnchor: document.activeElement?.dataset.sourceEntryAnchor || null,
            reviewPacketPreviewOpen: document.querySelector("#docx-circuit-review-packet-preview")?.open || false,
            reviewPacketPreviewFormat: document.querySelector("#docx-circuit-review-packet-preview")?.dataset.packetFormat || null,
            workbenchNavCount: document.querySelectorAll("#docx-circuit-workbench-bar a").length,
            workbenchThreeColumn: (() => {
                const stage = document.querySelector(".docx-circuit-stage");
                if (!stage) return false;
                const columns = getComputedStyle(stage).gridTemplateColumns.trim().split(/\\s+/).filter(Boolean);
                return columns.length >= 3;
            })(),
            demoPanelInline: (() => {
                const review = document.querySelector("#docx-circuit-review-panel");
                const demo = document.querySelector("#docx-circuit-demo-panel");
                if (!review || !demo) return false;
                const reviewRect = review.getBoundingClientRect();
                const demoRect = demo.getBoundingClientRect();
                return demoRect.left > reviewRect.left && demoRect.width > 320;
            })(),
            selectedElementId: document.querySelector("#docx-circuit-trace-panel")?.dataset.selectedElementId || null,
            selectedElementType: document.querySelector("#docx-circuit-trace-panel")?.dataset.selectedElementType || null,
            searchValue: document.querySelector("#docx-circuit-source-index-search")?.value || null,
            levelValue: document.querySelector("#docx-circuit-source-index-level")?.value || null,
            countText: document.querySelector("#docx-circuit-source-index-count")?.textContent || null,
            resultCount: document.querySelectorAll("#docx-circuit-source-index-list [data-source-entry-anchor]").length,
            visibleNodeCount: document.querySelectorAll("#docx-circuit-svg [data-node-id]").length,
            visibleWireCount: document.querySelectorAll("#docx-circuit-svg [data-wire-id]").length,
            hitPointCount: document.querySelectorAll("#docx-circuit-svg [data-wire-hit-id]").length,
        })"""
    )


def _state_matches(state: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(state.get(key) == value for key, value in expected.items())


def _responsive_state(page: Any) -> dict[str, Any]:
    page.wait_for_selector('#docx-circuit-svg[data-rendered="true"]', timeout=7000)
    return page.evaluate(
        """() => {
            const stage = document.querySelector(".docx-circuit-stage");
            const navLinks = [...document.querySelectorAll("#docx-circuit-workbench-bar a")];
            const navTops = new Set(navLinks.map((link) => Math.round(link.getBoundingClientRect().top)));
            const preview = document.querySelector("#docx-circuit-review-packet-preview");
            const previewText = document.querySelector("#docx-circuit-review-packet-preview-text");
            const sourceFocus = document.querySelector("#docx-circuit-source-focus");
            const review = document.querySelector("#docx-circuit-review-panel");
            const demo = document.querySelector("#docx-circuit-demo-panel");
            const columns = stage
                ? getComputedStyle(stage).gridTemplateColumns.trim().split(/\\s+/).filter(Boolean)
                : [];
            const reviewRect = review?.getBoundingClientRect();
            const demoRect = demo?.getBoundingClientRect();
            return {
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                pageWidth: document.documentElement.scrollWidth,
                noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
                workbenchNavCount: navLinks.length,
                workbenchNavRows: navTops.size,
                stageColumnCount: columns.length,
                desktopDemoInline: Boolean(
                    reviewRect && demoRect && demoRect.left > reviewRect.left && demoRect.width > 320
                ),
                sourceFocusVisible: Boolean(
                    sourceFocus
                    && sourceFocus.dataset.hasSource === "true"
                    && getComputedStyle(sourceFocus).display !== "none"
                ),
                sourceLocatorFocused: document.activeElement?.dataset.sourceEntryAnchor === "P004",
                reviewPacketPreviewOpen: Boolean(preview?.open),
                reviewPacketPreviewVisible: Boolean(
                    previewText
                    && previewText.textContent.includes("## DOCX Circuit Review Packet")
                    && previewText.getBoundingClientRect().height > 0
                ),
                visibleNodeCount: document.querySelectorAll("#docx-circuit-svg [data-node-id]").length,
                visibleWireCount: document.querySelectorAll("#docx-circuit-svg [data-wire-id]").length,
                hitPointCount: document.querySelectorAll("#docx-circuit-svg [data-wire-hit-id]").length,
            };
        }"""
    )


def _responsive_state_matches(state: dict[str, Any], expected_columns: str) -> bool:
    if expected_columns == "three":
        columns_match = state.get("stageColumnCount", 0) >= 3 and state.get("desktopDemoInline") is True
    else:
        columns_match = state.get("stageColumnCount") == 1
    return all(
        [
            columns_match,
            state.get("noHorizontalOverflow") is True,
            state.get("workbenchNavCount") == 4,
            state.get("sourceFocusVisible") is True,
            state.get("sourceLocatorFocused") is True,
            state.get("reviewPacketPreviewOpen") is True,
            state.get("reviewPacketPreviewVisible") is True,
            state.get("visibleNodeCount") == 20,
            state.get("visibleWireCount") == 23,
            state.get("hitPointCount") == 23,
        ]
    )


def _capture_responsive_state(
    context: Any,
    url: str,
    viewport: dict[str, Any],
    screenshot_path: Path,
) -> dict[str, Any]:
    page = context.new_page()
    page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
    page.goto(url, wait_until="networkidle")
    page.wait_for_selector("#docx-circuit-show-source-entry", timeout=7000)
    page.locator("#docx-circuit-review-packet-preview summary").click()
    page.wait_for_function(
        """() => {
            const preview = document.querySelector("#docx-circuit-review-packet-preview");
            const text = document.querySelector("#docx-circuit-review-packet-preview-text");
            return preview?.open && text?.textContent.includes("## DOCX Circuit Review Packet");
        }""",
        timeout=7000,
    )
    page.locator("#docx-circuit-show-source-entry").click()
    page.wait_for_function(
        """() => document.activeElement?.dataset.sourceEntryAnchor === "P004" """,
        timeout=7000,
    )
    state = _responsive_state(page)
    page.screenshot(path=str(screenshot_path), full_page=True)
    page.close()
    return state


def _review_packet_markdown_valid(value: str) -> bool:
    required = [
        "## DOCX Circuit Review Packet",
        "### Summary",
        "- Source: `P035-S01`",
        "- Selected element: `node:sw1`",
        "### P035 Evidence",
        "### DOCX Evidence",
        "### JSON",
        "```json",
        '"kind": "docx_circuit_review_packet"',
        '"id": "sw1"',
        '"truth_effect": "none"',
        '"certification_claim": "none"',
    ]
    return all(item in value for item in required) and value.rstrip().endswith("```")


def verify_review_links(artifact_dir: Path) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_stamp()
    current_review_path = artifact_dir / f"docx-to-circuit-current-review-link-{stamp}.png"
    review_packet_preview_path = artifact_dir / f"docx-to-circuit-review-packet-preview-{stamp}.png"
    source_entry_path = artifact_dir / f"docx-to-circuit-source-entry-link-{stamp}.png"
    responsive_paths = {
        item["name"]: artifact_dir / f"docx-to-circuit-responsive-{item['name']}-{stamp}.png"
        for item in RESPONSIVE_VIEWPORTS
    }
    restricted = _restricted_diff()
    console_errors: list[str] = []
    responsive_states: dict[str, dict[str, Any]] = {}

    server, thread, base_url = _start_server()
    current_link = f"{base_url}/docx-to-circuit#step=P035-S01&el=node%3Asw1&q=SW1&level=L1"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                context = browser.new_context(
                    permissions=["clipboard-read", "clipboard-write"],
                    viewport={"width": 1366, "height": 768},
                )
                page = context.new_page()
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.on(
                    "console",
                    lambda msg: console_errors.append(msg.text)
                    if msg.type in {"error"}
                    else None,
                )
                page.goto(current_link, wait_until="networkidle")
                page.wait_for_selector("#docx-circuit-copy-review-link", timeout=7000)
                page.locator("#docx-circuit-review-packet-preview summary").click()
                page.wait_for_function(
                    """() => {
                        const preview = document.querySelector("#docx-circuit-review-packet-preview");
                        const text = document.querySelector("#docx-circuit-review-packet-preview-text");
                        return preview?.open && text?.textContent.includes("## DOCX Circuit Review Packet");
                    }""",
                    timeout=7000,
                )
                preview_review_packet = page.locator("#docx-circuit-review-packet-preview-text").evaluate(
                    "element => element.textContent"
                )
                page.locator("#docx-circuit-review-packet-preview").screenshot(
                    path=str(review_packet_preview_path)
                )
                page.locator("#docx-circuit-copy-trace-packet").click()
                page.wait_for_function(
                    """() => document.querySelector("#docx-circuit-copy-status")?.textContent.includes("审阅包 Markdown 已复制")""",
                    timeout=7000,
                )
                copied_review_packet = page.evaluate("navigator.clipboard.readText()")
                page.locator("#docx-circuit-copy-review-link").click()
                page.wait_for_function(
                    """() => document.querySelector("#docx-circuit-copy-status")?.textContent.includes("链接已复制")""",
                    timeout=7000,
                )
                copied_current = page.evaluate("navigator.clipboard.readText()")
                current_page = context.new_page()
                current_page.goto(copied_current, wait_until="networkidle")
                current_state = _page_state(current_page)
                current_page.screenshot(path=str(current_review_path), full_page=True)

                page.locator('[data-source-entry-link-anchor="P004"]').click()
                page.wait_for_function(
                    """() => document.querySelector("#docx-circuit-copy-status")?.textContent.includes("P004 链接已复制")""",
                    timeout=7000,
                )
                copied_source_entry = page.evaluate("navigator.clipboard.readText()")
                source_page = context.new_page()
                source_page.goto(copied_source_entry, wait_until="networkidle")
                source_state = _page_state(source_page)
                source_page.locator("#docx-circuit-show-source-entry").click()
                source_focus_state = _page_state(source_page)
                source_page.screenshot(path=str(source_entry_path), full_page=True)
                for viewport in RESPONSIVE_VIEWPORTS:
                    responsive_states[viewport["name"]] = _capture_responsive_state(
                        context,
                        copied_source_entry,
                        viewport,
                        responsive_paths[viewport["name"]],
                    )
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    current_expected = {
        "activeAnchor": "P035-S01",
        "sourceAnchor": "P035-S01",
        "activeSourceEntryAnchor": None,
        "activeSourceEntryLabel": "未指定",
        "sourceFocusVisible": False,
        "sourceFocusButtonDisabled": True,
        "focusedSourceEntryAnchor": None,
        "selectedElementId": "sw1",
        "selectedElementType": "node",
        "searchValue": "SW1",
        "levelValue": "L1",
        "countText": "7 / 44",
        "resultCount": 7,
        "visibleNodeCount": 20,
        "visibleWireCount": 23,
        "hitPointCount": 23,
        "workbenchNavCount": 4,
        "workbenchThreeColumn": True,
        "demoPanelInline": True,
    }
    source_expected = {
        **current_expected,
        "activeSourceEntryAnchor": "P004",
        "activeSourceEntryLabel": "P004 · 源文档条目",
        "sourceFocusVisible": True,
        "sourceFocusButtonDisabled": False,
    }
    source_focus_expected = {
        **source_expected,
        "focusedSourceEntryAnchor": "P004",
    }
    current_params = _hash_params(copied_current)
    source_params = _hash_params(copied_source_entry)
    gates = {
        "browser_boot": "pass" if not console_errors else "fail",
        "current_review_link": "pass"
        if (
            copied_current == current_link
            and current_params == {
                "step": "P035-S01",
                "el": "node:sw1",
                "q": "SW1",
                "level": "L1",
            }
            and _state_matches(current_state, current_expected)
        )
        else "fail",
        "review_packet_markdown_json": "pass"
        if (
            preview_review_packet == copied_review_packet
            and _review_packet_markdown_valid(copied_review_packet)
        )
        else "fail",
        "source_entry_link": "pass"
        if (
            source_params == {
                "step": "P035-S01",
                "el": "node:sw1",
                "source": "P004",
                "q": "SW1",
                "level": "L1",
            }
            and _state_matches(source_state, source_expected)
        )
        else "fail",
        "source_entry_locator": "pass"
        if _state_matches(source_focus_state, source_focus_expected)
        else "fail",
        "screenshots": "pass"
        if all(
            path.exists() and path.stat().st_size > 0
            for path in (
                current_review_path,
                review_packet_preview_path,
                source_entry_path,
                *responsive_paths.values(),
            )
        )
        else "fail",
        "responsive_layout": "pass"
        if all(
            _responsive_state_matches(
                responsive_states.get(viewport["name"], {}),
                viewport["expected_columns"],
            )
            for viewport in RESPONSIVE_VIEWPORTS
        )
        else "fail",
        "boundary": "pass" if not restricted else "fail",
    }
    status = "pass" if all(value == "pass" for value in gates.values()) else "fail"
    return {
        "kind": "ai-fantui-docx-to-circuit-review-links",
        "version": 1,
        "status": status,
        "route": "/docx-to-circuit",
        "base_url": base_url,
        "artifact_dir": str(artifact_dir),
        "copied_urls": {
            "current_review": copied_current,
            "source_entry": copied_source_entry,
        },
        "review_packet": {
            "format": "markdown_with_json",
            "line_count": len(copied_review_packet.splitlines()),
            "contains_json_fence": "```json" in copied_review_packet,
            "preview_matches_clipboard": preview_review_packet == copied_review_packet,
        },
        "states": {
            "current_review": current_state,
            "source_entry": source_state,
            "source_entry_locator": source_focus_state,
        },
        "responsive_states": responsive_states,
        "screenshots": {
            "current_review": str(current_review_path),
            "review_packet_preview": str(review_packet_preview_path),
            "source_entry": str(source_entry_path),
            "responsive": {
                name: str(path)
                for name, path in responsive_paths.items()
            },
        },
        "console_errors": console_errors,
        "restricted_diff": restricted,
        "deterministic_gates": gates,
        "review_boundaries": {
            "controller_truth_modified": bool(
                [
                    path
                    for path in restricted
                    if path in RESTRICTED_PATHS[:3] or path.startswith("src/well_harness/adapters")
                ]
            ),
            "truth_effect": "none",
            "certification_claim": "none",
        },
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify copyable deep links for /docx-to-circuit review state.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: /docx-to-circuit review links passed")
    else:
        failed = [
            key
            for key, value in payload.get("deterministic_gates", {}).items()
            if value != "pass"
        ]
        print(f"FAIL: /docx-to-circuit review links failed ({', '.join(failed)})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = verify_review_links(args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-docx-to-circuit-review-links",
            "version": 1,
            "status": "fail",
            "route": "/docx-to-circuit",
            "screenshots": {},
            "copied_urls": {},
            "states": {},
            "console_errors": [],
            "deterministic_gates": {
                "browser_boot": "fail",
                "current_review_link": "fail",
                "review_packet_markdown_json": "fail",
                "source_entry_link": "fail",
                "source_entry_locator": "fail",
                "screenshots": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Browser-level acceptance for the demo.html reconstruction MVP console."""
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

from PIL import Image
from playwright.sync_api import sync_playwright

from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "demo-html-reconstruction-browser-acceptance"
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
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


def _pixel_visibility(path: Path, *, node_count: int, wire_count: int) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = list(image.getdata())
    reference = pixels[0] if pixels else (0, 0, 0)
    different = sum(
        1
        for pixel in pixels
        if sum(abs(pixel[index] - reference[index]) for index in range(3)) > 28
    )
    bright = sum(1 for pixel in pixels if max(pixel) > 95)
    unique_colors = len(set(pixels[:: max(1, len(pixels) // 20000)]))
    status = (
        "pass"
        if width >= 700
        and height >= 250
        and node_count == 20
        and wire_count == 23
        and different > 6000
        and bright > 800
        and unique_colors >= 12
        else "fail"
    )
    return {
        "status": status,
        "width": width,
        "height": height,
        "node_count": node_count,
        "wire_count": wire_count,
        "different_from_background_pixels": different,
        "bright_pixels": bright,
        "sampled_unique_colors": unique_colors,
    }


def _frame_text(frame: Any, selector: str) -> str:
    return frame.locator(selector).inner_text(timeout=5000).strip()


def _interaction_snapshot(frame: Any, preset: str, expected_status: str) -> dict[str, Any]:
    frame.locator(f'[data-preset="{preset}"]').click()
    frame.wait_for_function(
        """([selector, expected]) => {
            const el = document.querySelector(selector);
            return el && el.textContent.trim() === expected;
        }""",
        arg=["#fan-status-badge", expected_status],
        timeout=7000,
    )
    outputs = {
        "tls115": _frame_text(frame, "#fan-out-tls115-value"),
        "etrac": _frame_text(frame, "#fan-out-etrac-value"),
        "eec": _frame_text(frame, "#fan-out-eec-value"),
        "thr_lock": _frame_text(frame, "#fan-out-thr-value"),
    }
    return {
        "preset": preset,
        "status_badge": _frame_text(frame, "#fan-status-badge"),
        "status_summary": _frame_text(frame, "#fan-status-summary"),
        "hud_logic": _frame_text(frame, "#fan-hud-logic"),
        "hud_thr_lock": _frame_text(frame, "#fan-hud-thr-lock"),
        "outputs": outputs,
    }


def verify_browser_acceptance(artifact_dir: Path) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_stamp()
    first_screen_path = artifact_dir / f"demo-reconstruction-mvp-first-screen-{stamp}.png"
    mobile_first_screen_path = artifact_dir / f"demo-reconstruction-mvp-mobile-first-screen-{stamp}.png"
    chain_svg_path = artifact_dir / f"demo-reconstruction-mvp-chain-svg-{stamp}.png"
    keyboard_review_path = artifact_dir / f"demo-reconstruction-keyboard-review-{stamp}.png"
    max_reverse_path = artifact_dir / f"demo-reconstruction-mvp-max-reverse-{stamp}.png"
    max_reverse_outputs_path = artifact_dir / f"demo-reconstruction-mvp-max-reverse-outputs-{stamp}.png"
    inhibit_path = artifact_dir / f"demo-reconstruction-mvp-inhibit-block-{stamp}.png"
    inhibit_outputs_path = artifact_dir / f"demo-reconstruction-mvp-inhibit-block-outputs-{stamp}.png"
    restricted = _restricted_diff()
    console_errors: list[str] = []

    server, thread, base_url = _start_server()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1366, "height": 768})
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.on(
                    "console",
                    lambda msg: console_errors.append(msg.text)
                    if msg.type in {"error"}
                    else None,
                )
                page.goto(f"{base_url}/demo-reconstruction", wait_until="networkidle")
                page.wait_for_selector("#demo-reconstruction-console-frame", timeout=5000)
                page.wait_for_function(
                    """() => {
                        return document.querySelectorAll("[data-trace-card]").length >= 5
                            && document.querySelectorAll(".demo-reconstruction-source-entry").length >= 10
                            && document.querySelectorAll(".demo-reconstruction-sequence-step").length >= 5
                            && document.querySelectorAll("[data-circuit-coverage-kind='node']").length === 20
                            && document.querySelectorAll("[data-circuit-coverage-kind='wire']").length === 23;
                    }""",
                    timeout=7000,
                )
                page.screenshot(path=str(first_screen_path), full_page=True)
                first_screen_review = {
                    "source_map_visible": page.locator(
                        "#demo-reconstruction-docx-circuit-map"
                    ).is_visible(timeout=5000),
                    "trace_board_visible": page.locator(
                        "#demo-reconstruction-docx-trace-board"
                    ).is_visible(timeout=5000),
                    "operator_guide_visible": page.locator(
                        "#demo-reconstruction-operator-guide"
                    ).is_visible(timeout=5000),
                    "console_frame_visible": page.locator(
                        "#demo-reconstruction-console-frame"
                    ).is_visible(timeout=5000),
                    "evidence_rail_visible": page.locator(
                        "#demo-reconstruction-browser-evidence"
                    ).is_visible(timeout=5000),
                }
                source_map_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            sourceEntryCount: document.querySelectorAll(".demo-reconstruction-source-entry").length,
                            sequenceStepCount: document.querySelectorAll(".demo-reconstruction-sequence-step").length,
                            traceCardCount: document.querySelectorAll("[data-trace-card]").length,
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            selectedNodeChipCount: document.querySelectorAll("#demo-reconstruction-selected-nodes .demo-reconstruction-chip").length,
                            selectedWireChipCount: document.querySelectorAll("#demo-reconstruction-selected-wires .demo-reconstruction-chip").length,
                            coverageNodeButtonCount: document.querySelectorAll("[data-circuit-coverage-kind='node']").length,
                            coverageWireButtonCount: document.querySelectorAll("[data-circuit-coverage-kind='wire']").length,
                            coverageContract: text("#demo-reconstruction-coverage-contract"),
                            nodeCoverage: text("#demo-reconstruction-docx-node-coverage"),
                            wireCoverage: text("#demo-reconstruction-docx-wire-coverage"),
                            traceContract: text("#demo-reconstruction-trace-contract"),
                        };
                    }"""
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        return selected && selected.textContent.trim() === "P035-S05";
                    }""",
                    timeout=5000,
                )
                trace_selection_review = page.evaluate(
                    """() => {
                        const pressedCards = Array.from(
                            document.querySelectorAll("[data-trace-card][aria-pressed='true']")
                        );
                        const selectedCard = document.querySelector(
                            "[data-trace-card][data-trace-anchor='P035-S05']"
                        );
                        return {
                            selectedAnchorAfterClick: document
                                .querySelector("#demo-reconstruction-selected-anchor")
                                ?.textContent?.trim() || "",
                            selectedLastPressed: selectedCard?.getAttribute("aria-pressed") === "true",
                            pressedTraceCount: pressedCards.length,
                        };
                    }"""
                )
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        return nodes.length === 4 && wires.length === 3;
                    }""",
                    timeout=5000,
                )
                embedded_trace_highlight_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            selectedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            selectedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            stylePresent: !!(doc && doc.getElementById("demo-reconstruction-trace-highlight-style")),
                            statusText: text("#demo-reconstruction-embedded-highlight-status"),
                        };
                    }"""
                )
                page.locator(
                    '#demo-reconstruction-selected-nodes [data-trace-focus-kind="node"][data-trace-focus-id="logic4"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return nodes.length === 1 && wires.length === 0 && status.includes("logic4");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '#demo-reconstruction-selected-wires [data-trace-focus-kind="wire"][data-trace-focus-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return nodes.length === 0
                            && wires.length === 1
                            && status.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                embedded_trace_chip_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const nodeButton = document.querySelector(
                            '#demo-reconstruction-selected-nodes [data-trace-focus-id="logic4"]'
                        );
                        const wireButton = document.querySelector(
                            '#demo-reconstruction-selected-wires [data-trace-focus-id="wire_logic4_thr_lock"]'
                        );
                        return {
                            focusNodeChipPresent: !!nodeButton,
                            focusWireChipPresent: !!wireButton,
                            focusedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            focusedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            statusText: document
                                .querySelector("#demo-reconstruction-embedded-highlight-status")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator(
                    '[data-circuit-coverage-kind="node"][data-circuit-coverage-id="thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return nodes.length === 1 && wires.length === 0 && status.includes("thr_lock");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-circuit-coverage-kind="wire"][data-circuit-coverage-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return nodes.length === 0
                            && wires.length === 1
                            && status.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                coverage_matrix_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            nodeButtonCount: document.querySelectorAll("[data-circuit-coverage-kind='node']").length,
                            wireButtonCount: document.querySelectorAll("[data-circuit-coverage-kind='wire']").length,
                            contractText: document
                                .querySelector("#demo-reconstruction-coverage-contract")
                                ?.textContent?.trim() || "",
                            focusedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            focusedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            statusText: document
                                .querySelector("#demo-reconstruction-embedded-highlight-status")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator("#demo-reconstruction-coverage-search").fill("logic4")
                page.wait_for_function(
                    """() => {
                        const visibleNodes = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind='node']")
                        ).filter((button) => !button.hidden);
                        const visibleWires = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind='wire']")
                        ).filter((button) => !button.hidden);
                        const status = document
                            .querySelector("#demo-reconstruction-coverage-filter-status")
                            ?.textContent || "";
                        return visibleNodes.length === 1
                            && visibleWires.length === 3
                            && status.includes("4/43");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-circuit-coverage-kind="wire"][data-circuit-coverage-id="wire_logic4_thr_lock"]'
                ).click()
                coverage_filter_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const visibleNodes = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind='node']")
                        ).filter((button) => !button.hidden);
                        const visibleWires = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind='wire']")
                        ).filter((button) => !button.hidden);
                        return {
                            query: document.querySelector("#demo-reconstruction-coverage-search")?.value || "",
                            visibleNodeCount: visibleNodes.length,
                            visibleWireCount: visibleWires.length,
                            statusText: document
                                .querySelector("#demo-reconstruction-coverage-filter-status")
                                ?.textContent?.trim() || "",
                            focusedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            focusStatusText: document
                                .querySelector("#demo-reconstruction-embedded-highlight-status")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S01"]').focus()
                page.locator('[data-trace-card][data-trace-anchor="P035-S01"]').press("ArrowDown")
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const active = document.activeElement;
                        return selected
                            && selected.textContent.trim() === "P035-S02"
                            && active
                            && active.getAttribute("data-trace-anchor") === "P035-S02";
                    }""",
                    timeout=5000,
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S02"]').press("End")
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const active = document.activeElement;
                        return selected
                            && selected.textContent.trim() === "P035-S05"
                            && active
                            && active.getAttribute("data-trace-anchor") === "P035-S05";
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-circuit-coverage-kind="node"][data-circuit-coverage-id="logic4"]'
                ).focus()
                page.locator(
                    '[data-circuit-coverage-kind="node"][data-circuit-coverage-id="logic4"]'
                ).press("ArrowDown")
                page.wait_for_function(
                    """() => {
                        const active = document.activeElement;
                        return active
                            && active.getAttribute("data-circuit-coverage-id") === "wire_logic3_logic4";
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-circuit-coverage-kind="wire"][data-circuit-coverage-id="wire_logic3_logic4"]'
                ).press("ArrowDown")
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const active = document.activeElement;
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return active
                            && active.getAttribute("data-circuit-coverage-kind") === "wire"
                            && active.getAttribute("data-circuit-coverage-id") === "wire_logic4_thr_lock"
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1
                            && status.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-docx-circuit-map").screenshot(
                    path=str(keyboard_review_path)
                )
                keyboard_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const active = document.activeElement;
                        const visibleCoverageButtons = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind]")
                        ).filter((button) => !button.hidden);
                        return {
                            traceSelectedAnchor: document
                                .querySelector("#demo-reconstruction-selected-anchor")
                                ?.textContent?.trim() || "",
                            traceActiveAnchor: active && active.hasAttribute("data-trace-anchor")
                                ? active.getAttribute("data-trace-anchor")
                                : document.querySelector("[data-trace-card][tabindex='0']")
                                    ?.getAttribute("data-trace-anchor") || "",
                            traceTabStopAnchors: Array.from(
                                document.querySelectorAll("[data-trace-card][tabindex='0']")
                            ).map((button) => button.getAttribute("data-trace-anchor")),
                            coverageActiveKind: active
                                ? active.getAttribute("data-circuit-coverage-kind") || ""
                                : "",
                            coverageActiveId: active
                                ? active.getAttribute("data-circuit-coverage-id") || ""
                                : "",
                            coverageTabStopIds: visibleCoverageButtons
                                .filter((button) => button.getAttribute("tabindex") === "0")
                                .map((button) => button.getAttribute("data-circuit-coverage-id")),
                            focusedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            statusText: document
                                .querySelector("#demo-reconstruction-embedded-highlight-status")
                                ?.textContent?.trim() || "",
                            reviewAnchorText: document
                                .querySelector("#demo-reconstruction-review-anchor")
                                ?.textContent?.trim() || "",
                            reviewObjectText: document
                                .querySelector("#demo-reconstruction-review-object")
                                ?.textContent?.trim() || "",
                            reviewSyncText: document
                                .querySelector("#demo-reconstruction-review-sync")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator(
                    '.demo-reconstruction-sequence-step[data-trace-anchor="P035-S05"] [data-source-focus-kind="node"][data-source-focus-id="logic4"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        if (!doc) return false;
                        const nodes = doc.querySelectorAll(
                            "#fan-chain-svg [data-docx-trace-selected='true'][data-node]"
                        );
                        const wires = doc.querySelectorAll(
                            "#fan-chain-svg .chain-wire[data-docx-trace-selected='true']"
                        );
                        const status = document
                            .querySelector("#demo-reconstruction-embedded-highlight-status")
                            ?.textContent || "";
                        return nodes.length === 1 && wires.length === 0 && status.includes("logic4");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '.demo-reconstruction-sequence-step[data-trace-anchor="P035-S05"] [data-source-focus-kind="wire"][data-source-focus-id="wire_logic4_thr_lock"]'
                ).click()
                source_chip_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            sourceNodeFocusChipCount: document.querySelectorAll(
                                ".demo-reconstruction-source-entry [data-source-focus-kind='node'], .demo-reconstruction-sequence-step [data-source-focus-kind='node']"
                            ).length,
                            sourceWireFocusChipCount: document.querySelectorAll(
                                ".demo-reconstruction-source-entry [data-source-focus-kind='wire'], .demo-reconstruction-sequence-step [data-source-focus-kind='wire']"
                            ).length,
                            focusedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            focusedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            statusText: document
                                .querySelector("#demo-reconstruction-embedded-highlight-status")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                desktop_geometry = page.evaluate(
                    """() => ({
                        viewportWidth: window.innerWidth,
                        pageWidth: document.documentElement.scrollWidth,
                        noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
                    })"""
                )

                mobile_page = browser.new_page(viewport={"width": 390, "height": 844})
                try:
                    mobile_page.goto(f"{base_url}/demo-reconstruction", wait_until="networkidle")
                    mobile_page.wait_for_selector("#demo-reconstruction-docx-trace-board", timeout=5000)
                    mobile_page.wait_for_function(
                        """() => document.querySelectorAll("[data-trace-card]").length >= 5""",
                        timeout=7000,
                    )
                    mobile_page.screenshot(path=str(mobile_first_screen_path), full_page=True)
                    mobile_geometry = mobile_page.evaluate(
                        """() => ({
                            viewportWidth: window.innerWidth,
                            pageWidth: document.documentElement.scrollWidth,
                            noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
                            traceCardCount: document.querySelectorAll("[data-trace-card]").length,
                            sourceMapVisible: !!document.querySelector("#demo-reconstruction-docx-circuit-map"),
                        })"""
                    )
                finally:
                    mobile_page.close()

                frame_handle = page.locator("#demo-reconstruction-console-frame").element_handle()
                frame = frame_handle.content_frame() if frame_handle else None
                if frame is None:
                    raise RuntimeError("demo reconstruction console iframe did not load")
                frame.wait_for_selector("#fan-chain-svg", timeout=5000)
                embedded_palette = frame.evaluate(
                    """() => {
                        const readStyle = (selector, property) => {
                            const element = document.querySelector(selector);
                            return element ? getComputedStyle(element)[property] : "";
                        };
                        return {
                            html_class: document.documentElement.classList.contains("is-codex-light-demo"),
                            palette: document.documentElement.getAttribute("data-console-palette") || "",
                            body_background: getComputedStyle(document.body).backgroundColor,
                            panel_background: readStyle(".fan-panel", "backgroundColor"),
                            chain_node_fill: readStyle("#fan-chain-svg .chain-node rect", "fill"),
                            text_color: getComputedStyle(document.body).color,
                        };
                    }"""
                )
                frame.locator("#fan-chain-svg").screenshot(path=str(chain_svg_path))

                node_count = frame.locator("#fan-chain-svg [data-node]").count()
                wire_count = frame.locator("#fan-chain-svg .chain-wire").count()
                pixel_visibility = _pixel_visibility(
                    chain_svg_path,
                    node_count=node_count,
                    wire_count=wire_count,
                )

                max_reverse = _interaction_snapshot(frame, "max-reverse", "DEPLOYED")
                frame.locator("body").screenshot(path=str(max_reverse_path))
                frame.locator('section[aria-labelledby="outputs-heading"]').scroll_into_view_if_needed()
                frame.locator('section[aria-labelledby="outputs-heading"]').screenshot(path=str(max_reverse_outputs_path))
                inhibit = _interaction_snapshot(frame, "inhibit-block", "FAULT")
                frame.locator("body").screenshot(path=str(inhibit_path))
                frame.locator('section[aria-labelledby="outputs-heading"]').scroll_into_view_if_needed()
                frame.locator('section[aria-labelledby="outputs-heading"]').screenshot(path=str(inhibit_outputs_path))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    interaction_pass = (
        max_reverse["status_badge"] == "DEPLOYED"
        and max_reverse["hud_thr_lock"] == "RELEASED"
        and max_reverse["outputs"]["thr_lock"] == "ON"
        and inhibit["status_badge"] == "FAULT"
        and inhibit["outputs"]["thr_lock"] != "ON"
    )
    gates = {
        "browser_boot": "pass" if not console_errors else "fail",
        "screenshots": "pass"
        if all(
            path.exists() and path.stat().st_size > 0
            for path in (
                first_screen_path,
                mobile_first_screen_path,
                chain_svg_path,
                keyboard_review_path,
                max_reverse_path,
                max_reverse_outputs_path,
                inhibit_path,
                inhibit_outputs_path,
            )
        )
        else "fail",
        "first_screen_operator_guide": "pass"
        if all(first_screen_review.values())
        else "fail",
        "docx_sentence_circuit_map": "pass"
        if (
            source_map_review["sourceEntryCount"] >= 10
            and source_map_review["sequenceStepCount"] == 5
            and source_map_review["traceCardCount"] == 5
            and source_map_review["coverageNodeButtonCount"] == 20
            and source_map_review["coverageWireButtonCount"] == 23
            and source_map_review["selectedNodeChipCount"] > 0
            and source_map_review["selectedWireChipCount"] > 0
            and source_map_review["nodeCoverage"] == "20/20"
            and source_map_review["wireCoverage"] == "23/23"
        )
        else "fail",
        "trace_selection_interaction": "pass"
        if (
            trace_selection_review["selectedAnchorAfterClick"] == "P035-S05"
            and trace_selection_review["selectedLastPressed"]
            and trace_selection_review["pressedTraceCount"] == 1
        )
        else "fail",
        "embedded_trace_highlight": "pass"
        if (
            embedded_trace_highlight_review["selectedNodeCount"] == 4
            and embedded_trace_highlight_review["selectedWireCount"] == 3
            and embedded_trace_highlight_review["stylePresent"]
            and "P035-S05" in embedded_trace_highlight_review["statusText"]
        )
        else "fail",
        "embedded_trace_chip_focus": "pass"
        if (
            embedded_trace_chip_focus_review["focusNodeChipPresent"]
            and embedded_trace_chip_focus_review["focusWireChipPresent"]
            and embedded_trace_chip_focus_review["focusedNodeCount"] == 0
            and embedded_trace_chip_focus_review["focusedWireCount"] == 1
            and "wire_logic4_thr_lock" in embedded_trace_chip_focus_review["statusText"]
        )
        else "fail",
        "coverage_matrix_focus": "pass"
        if (
            coverage_matrix_review["nodeButtonCount"] == 20
            and coverage_matrix_review["wireButtonCount"] == 23
            and "20/20" in coverage_matrix_review["contractText"]
            and "23/23" in coverage_matrix_review["contractText"]
            and coverage_matrix_review["focusedNodeCount"] == 0
            and coverage_matrix_review["focusedWireCount"] == 1
            and "wire_logic4_thr_lock" in coverage_matrix_review["statusText"]
        )
        else "fail",
        "coverage_matrix_filter": "pass"
        if (
            coverage_filter_review["query"] == "logic4"
            and coverage_filter_review["visibleNodeCount"] == 1
            and coverage_filter_review["visibleWireCount"] == 3
            and "4/43" in coverage_filter_review["statusText"]
            and coverage_filter_review["focusedWireCount"] == 1
            and "wire_logic4_thr_lock" in coverage_filter_review["focusStatusText"]
        )
        else "fail",
        "keyboard_trace_navigation": "pass"
        if (
            keyboard_review["traceSelectedAnchor"] == "P035-S05"
            and keyboard_review["traceActiveAnchor"] == "P035-S05"
            and keyboard_review["traceTabStopAnchors"] == ["P035-S05"]
        )
        else "fail",
        "coverage_keyboard_navigation": "pass"
        if (
            keyboard_review["coverageActiveKind"] == "wire"
            and keyboard_review["coverageActiveId"] == "wire_logic4_thr_lock"
            and keyboard_review["coverageTabStopIds"] == ["wire_logic4_thr_lock"]
            and keyboard_review["focusedWireCount"] == 1
            and "wire_logic4_thr_lock" in keyboard_review["statusText"]
        )
        else "fail",
        "review_cursor_status": "pass"
        if (
            "P035-S05" in keyboard_review["reviewAnchorText"]
            and "wire_logic4_thr_lock" in keyboard_review["reviewObjectText"]
            and keyboard_review["reviewSyncText"]
        )
        else "fail",
        "source_chip_focus": "pass"
        if (
            source_chip_focus_review["sourceNodeFocusChipCount"] >= 20
            and source_chip_focus_review["sourceWireFocusChipCount"] >= 23
            and source_chip_focus_review["focusedNodeCount"] == 0
            and source_chip_focus_review["focusedWireCount"] == 1
            and "wire_logic4_thr_lock" in source_chip_focus_review["statusText"]
        )
        else "fail",
        "responsive_geometry": "pass"
        if (
            desktop_geometry["noHorizontalOverflow"]
            and mobile_geometry["noHorizontalOverflow"]
            and mobile_geometry["traceCardCount"] == 5
        )
        else "fail",
        "embedded_codex_light_palette": "pass"
        if (
            embedded_palette["html_class"]
            and embedded_palette["palette"] == "codex-light"
            and embedded_palette["body_background"] == "rgb(247, 248, 251)"
            and embedded_palette["panel_background"] == "rgb(255, 255, 255)"
        )
        else "fail",
        "node_wire_pixels": pixel_visibility["status"],
        "preset_interactions": "pass" if interaction_pass else "fail",
        "hud_output_linkage": "pass"
        if max_reverse["hud_thr_lock"] == "RELEASED" and max_reverse["outputs"]["thr_lock"] == "ON"
        else "fail",
        "boundary": "pass" if not restricted else "fail",
    }
    status = "pass" if all(value == "pass" for value in gates.values()) else "fail"
    return {
        "kind": "ai-fantui-demo-html-reconstruction-browser-acceptance",
        "version": 1,
        "status": status,
        "route": "/demo-reconstruction",
        "base_url": base_url,
        "artifact_dir": str(artifact_dir),
        "screenshots": {
            "first_screen": str(first_screen_path),
            "mobile_first_screen": str(mobile_first_screen_path),
            "chain_svg": str(chain_svg_path),
            "keyboard_review": str(keyboard_review_path),
            "max_reverse": str(max_reverse_path),
            "max_reverse_outputs": str(max_reverse_outputs_path),
            "inhibit_block": str(inhibit_path),
            "inhibit_block_outputs": str(inhibit_outputs_path),
        },
        "pixel_visibility": {
            "chain_svg": pixel_visibility,
        },
        "embedded_palette": embedded_palette,
        "first_screen_review": first_screen_review,
        "source_map_review": source_map_review,
        "trace_selection_review": trace_selection_review,
        "embedded_trace_highlight_review": embedded_trace_highlight_review,
        "embedded_trace_chip_focus_review": embedded_trace_chip_focus_review,
        "coverage_matrix_review": coverage_matrix_review,
        "coverage_filter_review": coverage_filter_review,
        "keyboard_review": keyboard_review,
        "source_chip_focus_review": source_chip_focus_review,
        "responsive_geometry": {
            "desktop": desktop_geometry,
            "mobile": mobile_geometry,
        },
        "interactions": {
            "max-reverse": max_reverse,
            "inhibit-block": inhibit,
        },
        "console_errors": console_errors,
        "deterministic_gates": gates,
        "review_boundaries": {
            "controller_truth_modified": bool(
                [path for path in restricted if path in RESTRICTED_PATHS[:2]]
            ),
            "ui_layout_modified": bool(
                [path for path in restricted if path.startswith("src/well_harness/static/requirements_intake")]
            ),
            "truth_effect": "none",
            "certification_claim": "none",
        },
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture browser screenshots and interaction evidence for /demo-reconstruction.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: demo.html reconstruction browser acceptance passed")
    else:
        failed = [
            key
            for key, value in payload.get("deterministic_gates", {}).items()
            if value != "pass"
        ]
        print(f"FAIL: demo.html reconstruction browser acceptance failed ({', '.join(failed)})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = verify_browser_acceptance(args.artifact_dir)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "kind": "ai-fantui-demo-html-reconstruction-browser-acceptance",
            "version": 1,
            "status": "fail",
            "route": "/demo-reconstruction",
            "screenshots": {},
            "pixel_visibility": {},
            "interactions": {},
            "console_errors": [],
            "deterministic_gates": {
                "browser_boot": "fail",
                "screenshots": "fail",
                "first_screen_operator_guide": "fail",
                "docx_sentence_circuit_map": "fail",
                "trace_selection_interaction": "fail",
                "embedded_trace_highlight": "fail",
                "embedded_trace_chip_focus": "fail",
                "coverage_matrix_focus": "fail",
                "coverage_matrix_filter": "fail",
                "source_chip_focus": "fail",
                "responsive_geometry": "fail",
                "embedded_codex_light_palette": "fail",
                "node_wire_pixels": "fail",
                "preset_interactions": "fail",
                "hud_output_linkage": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

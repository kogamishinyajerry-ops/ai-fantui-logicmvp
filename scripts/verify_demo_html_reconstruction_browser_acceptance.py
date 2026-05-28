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
    review_index_path = artifact_dir / f"demo-reconstruction-review-index-{stamp}.png"
    chain_svg_path = artifact_dir / f"demo-reconstruction-mvp-chain-svg-{stamp}.png"
    keyboard_review_path = artifact_dir / f"demo-reconstruction-keyboard-review-{stamp}.png"
    review_deep_link_path = artifact_dir / f"demo-reconstruction-review-deep-link-{stamp}.png"
    step_playback_path = artifact_dir / f"demo-reconstruction-step-playback-{stamp}.png"
    object_provenance_path = artifact_dir / f"demo-reconstruction-object-provenance-{stamp}.png"
    signal_neighborhood_path = artifact_dir / f"demo-reconstruction-signal-neighborhood-{stamp}.png"
    completion_ladder_path = artifact_dir / f"demo-reconstruction-completion-ladder-{stamp}.png"
    review_packet_path = artifact_dir / f"demo-reconstruction-review-packet-{stamp}.png"
    custody_matrix_path = artifact_dir / f"demo-reconstruction-custody-matrix-{stamp}.png"
    scenario_ledger_path = artifact_dir / f"demo-reconstruction-scenario-ledger-{stamp}.png"
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
                    "review_index_visible": page.locator(
                        "#demo-reconstruction-review-index"
                    ).is_visible(timeout=5000),
                    "source_map_visible": page.locator(
                        "#demo-reconstruction-docx-circuit-map"
                    ).is_visible(timeout=5000),
                    "trace_board_visible": page.locator(
                        "#demo-reconstruction-docx-trace-board"
                    ).is_visible(timeout=5000),
                    "operator_guide_visible": page.locator(
                        "#demo-reconstruction-operator-guide"
                    ).is_visible(timeout=5000),
                    "output_mirror_visible": page.locator(
                        "#demo-reconstruction-output-mirror"
                    ).is_visible(timeout=5000),
                    "scenario_ledger_visible": page.locator(
                        "#demo-reconstruction-scenario-ledger"
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
                            reviewIndexButtonCount: document.querySelectorAll("[data-review-index-target]").length,
                            sequenceStepCount: document.querySelectorAll(".demo-reconstruction-sequence-step").length,
                            traceCardCount: document.querySelectorAll("[data-trace-card]").length,
                            playbackStepCount: document.querySelectorAll("[data-playback-step]").length,
                            ladderStepCount: document.querySelectorAll("[data-ladder-step]").length,
                            custodyStepCount: document.querySelectorAll("[data-custody-step]").length,
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
                page.locator("#demo-reconstruction-review-index").screenshot(
                    path=str(review_index_path)
                )
                review_index_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-review-index"),
                            buttonCount: document.querySelectorAll("[data-review-index-target]").length,
                            readinessText: text("#demo-reconstruction-review-index-readiness"),
                            stepText: text("#demo-reconstruction-review-index-step"),
                            objectText: text("#demo-reconstruction-review-index-object"),
                            outputText: text("#demo-reconstruction-review-index-output"),
                            activeTargets: Array.from(
                                document.querySelectorAll("[data-review-index-target][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-review-index-target")),
                        };
                    }"""
                )
                page.locator('[data-review-index-target="demo-reconstruction-scenario-ledger"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector(
                            '[data-review-index-target="demo-reconstruction-scenario-ledger"][aria-pressed="true"]'
                        );
                        const target = document.querySelector("#demo-reconstruction-scenario-ledger");
                        return !!active && !!target && window.scrollY > 0;
                    }""",
                    timeout=5000,
                )
                review_index_navigation = page.evaluate(
                    """() => ({
                        activeTargets: Array.from(
                            document.querySelectorAll("[data-review-index-target][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-review-index-target")),
                        scrollY: window.scrollY,
                    })"""
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
                review_index_after_trace = page.evaluate(
                    """() => ({
                        stepText: document
                            .querySelector("#demo-reconstruction-review-index-step")
                            ?.textContent?.trim() || "",
                        objectText: document
                            .querySelector("#demo-reconstruction-review-index-object")
                            ?.textContent?.trim() || "",
                    })"""
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
                    '[data-circuit-coverage-kind="node"][data-circuit-coverage-id="logic4"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-provenance-object");
                        const sources = document.querySelectorAll(
                            "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                        );
                        const steps = document.querySelectorAll(
                            "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                        );
                        return object
                            && object.textContent.includes("logic4")
                            && sources.length >= 2
                            && steps.length >= 1;
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-object-provenance").screenshot(
                    path=str(object_provenance_path)
                )
                object_provenance_review = page.evaluate(
                    """() => ({
                        objectText: document
                            .querySelector("#demo-reconstruction-provenance-object")
                            ?.textContent?.trim() || "",
                        sourceCount: document.querySelectorAll(
                            "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                        ).length,
                        stepCount: document.querySelectorAll(
                            "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                        ).length,
                        sourceCountText: document
                            .querySelector("#demo-reconstruction-provenance-source-count")
                            ?.textContent?.trim() || "",
                        stepCountText: document
                            .querySelector("#demo-reconstruction-provenance-step-count")
                            ?.textContent?.trim() || "",
                        sourceItems: Array.from(
                            document.querySelectorAll(
                                "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                            )
                        ).map((item) => item.textContent.trim()),
                        stepItems: Array.from(
                            document.querySelectorAll(
                                "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                            )
                        ).map((item) => item.textContent.trim()),
                    })"""
                )
                page.locator("#demo-reconstruction-signal-neighborhood").screenshot(
                    path=str(signal_neighborhood_path)
                )
                signal_neighborhood_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            objectText: text("#demo-reconstruction-neighborhood-object"),
                            inCountText: text("#demo-reconstruction-neighborhood-in-count"),
                            outCountText: text("#demo-reconstruction-neighborhood-out-count"),
                            incomingCount: document.querySelectorAll("#demo-reconstruction-neighborhood-incoming [data-neighborhood-focus-id]").length,
                            outgoingCount: document.querySelectorAll("#demo-reconstruction-neighborhood-outgoing [data-neighborhood-focus-id]").length,
                            adjacentCount: document.querySelectorAll("#demo-reconstruction-neighborhood-adjacent [data-neighborhood-focus-id]").length,
                            incomingText: text("#demo-reconstruction-neighborhood-incoming"),
                            outgoingText: text("#demo-reconstruction-neighborhood-outgoing"),
                            adjacentText: text("#demo-reconstruction-neighborhood-adjacent"),
                        };
                    }"""
                )
                page.locator(
                    '#demo-reconstruction-neighborhood-outgoing [data-neighborhood-focus-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-neighborhood-object");
                        const incoming = document.querySelectorAll(
                            "#demo-reconstruction-neighborhood-incoming [data-neighborhood-focus-id]"
                        );
                        const outgoing = document.querySelectorAll(
                            "#demo-reconstruction-neighborhood-outgoing [data-neighborhood-focus-id]"
                        );
                        const status = document.querySelector("#demo-reconstruction-embedded-highlight-status")?.textContent || "";
                        return object
                            && object.textContent.includes("wire_logic4_thr_lock")
                            && incoming.length === 1
                            && outgoing.length === 1
                            && status.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                signal_neighborhood_wire_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            objectText: text("#demo-reconstruction-neighborhood-object"),
                            inCountText: text("#demo-reconstruction-neighborhood-in-count"),
                            outCountText: text("#demo-reconstruction-neighborhood-out-count"),
                            incomingText: text("#demo-reconstruction-neighborhood-incoming"),
                            outgoingText: text("#demo-reconstruction-neighborhood-outgoing"),
                            adjacentText: text("#demo-reconstruction-neighborhood-adjacent"),
                        };
                    }"""
                )
                page.locator("#demo-reconstruction-circuit-ladder").screenshot(
                    path=str(completion_ladder_path)
                )
                completion_ladder_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-ladder-step]").length,
                            summaryText: text("#demo-reconstruction-ladder-summary"),
                            s03Text: text('[data-ladder-step="P035-S03"]'),
                            s05Text: text('[data-ladder-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator("#demo-reconstruction-review-packet").screenshot(
                    path=str(review_packet_path)
                )
                review_packet_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        const gates = Array.from(document.querySelectorAll("[data-review-packet-gate]"));
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-review-packet"),
                            readinessText: text("#demo-reconstruction-review-packet-readiness"),
                            sourceText: text("#demo-reconstruction-review-packet-source"),
                            contractText: text("#demo-reconstruction-review-packet-contract"),
                            stepText: text("#demo-reconstruction-review-packet-step"),
                            objectText: text("#demo-reconstruction-review-packet-object"),
                            gateCount: gates.length,
                            passGateCount: gates.filter((gate) => gate.dataset.packetGateStatus === "pass").length,
                            gateLabels: gates.map((gate) => gate.textContent.trim()),
                        };
                    }"""
                )
                page.locator(
                    '[data-circuit-coverage-kind="wire"][data-circuit-coverage-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-provenance-object");
                        const sources = document.querySelectorAll(
                            "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                        );
                        const steps = document.querySelectorAll(
                            "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                        );
                        return object
                            && object.textContent.includes("wire_logic4_thr_lock")
                            && sources.length >= 2
                            && steps.length >= 1;
                    }""",
                    timeout=5000,
                )
                wire_provenance_review = page.evaluate(
                    """() => ({
                        objectText: document
                            .querySelector("#demo-reconstruction-provenance-object")
                            ?.textContent?.trim() || "",
                        sourceCount: document.querySelectorAll(
                            "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                        ).length,
                        stepCount: document.querySelectorAll(
                            "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                        ).length,
                        sourceItems: Array.from(
                            document.querySelectorAll(
                                "#demo-reconstruction-provenance-source-list .demo-reconstruction-provenance-item"
                            )
                        ).map((item) => item.textContent.trim()),
                        stepItems: Array.from(
                            document.querySelectorAll(
                                "#demo-reconstruction-provenance-step-list .demo-reconstruction-provenance-item"
                            )
                        ).map((item) => item.textContent.trim()),
                    })"""
                )
                review_packet_after_wire_focus = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        const gates = Array.from(document.querySelectorAll("[data-review-packet-gate]"));
                        return {
                            readinessText: text("#demo-reconstruction-review-packet-readiness"),
                            objectText: text("#demo-reconstruction-review-packet-object"),
                            passGateCount: gates.filter((gate) => gate.dataset.packetGateStatus === "pass").length,
                        };
                    }"""
                )
                page.locator('[data-custody-step-button="P035-S04"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const active = document.querySelector('[data-custody-step-button="P035-S04"]');
                        const status = document.querySelector("#demo-reconstruction-embedded-highlight-status")?.textContent || "";
                        return selected
                            && selected.textContent.trim() === "P035-S04"
                            && active
                            && active.getAttribute("aria-pressed") === "true"
                            && status.includes("P035-S04");
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-custody-matrix").screenshot(
                    path=str(custody_matrix_path)
                )
                custody_matrix_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-custody-step]").length,
                            activeButtonCount: document.querySelectorAll("[data-custody-step-button][aria-pressed='true']").length,
                            summaryText: text("#demo-reconstruction-custody-summary"),
                            activeText: text("#demo-reconstruction-custody-active"),
                            outputText: text("#demo-reconstruction-custody-output"),
                            s04Text: text('[data-custody-step="P035-S04"]'),
                            s05Text: text('[data-custody-step="P035-S05"]'),
                            highlightedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            highlightedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
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
                review_deep_link = page.evaluate(
                    """() => ({
                        hash: window.location.hash,
                        linkHref: document.querySelector("#demo-reconstruction-review-link")?.href || "",
                    })"""
                )
                restored_page = browser.new_page(viewport={"width": 1366, "height": 768})
                try:
                    restored_page.goto(
                        f"{base_url}/demo-reconstruction#step=P035-S05&focus=wire%3Awire_logic4_thr_lock&q=logic4",
                        wait_until="networkidle",
                    )
                    restored_page.wait_for_function(
                        """() => {
                            const frame = document.querySelector("#demo-reconstruction-console-frame");
                            const doc = frame && frame.contentDocument;
                            const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                            const search = document.querySelector("#demo-reconstruction-coverage-search");
                            const status = document.querySelector("#demo-reconstruction-embedded-highlight-status")?.textContent || "";
                            return selected
                                && selected.textContent.trim() === "P035-S05"
                                && search
                                && search.value === "logic4"
                                && doc
                                && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1
                                && status.includes("wire_logic4_thr_lock");
                        }""",
                        timeout=7000,
                    )
                    restored_page.locator("#demo-reconstruction-docx-circuit-map").screenshot(
                        path=str(review_deep_link_path)
                    )
                    restored_review = restored_page.evaluate(
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
                                selectedAnchor: document
                                    .querySelector("#demo-reconstruction-selected-anchor")
                                    ?.textContent?.trim() || "",
                                query: document.querySelector("#demo-reconstruction-coverage-search")?.value || "",
                                visibleNodeCount: visibleNodes.length,
                                visibleWireCount: visibleWires.length,
                                focusedWireCount: doc
                                    ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                    : 0,
                                objectText: document
                                    .querySelector("#demo-reconstruction-review-object")
                                    ?.textContent?.trim() || "",
                                statusText: document
                                    .querySelector("#demo-reconstruction-embedded-highlight-status")
                                    ?.textContent?.trim() || "",
                            };
                        }"""
                    )
                    review_deep_link.update(
                        {
                            "restoredSelectedAnchor": restored_review["selectedAnchor"],
                            "restoredQuery": restored_review["query"],
                            "restoredVisibleNodeCount": restored_review["visibleNodeCount"],
                            "restoredVisibleWireCount": restored_review["visibleWireCount"],
                            "restoredFocusedWireCount": restored_review["focusedWireCount"],
                            "restoredObjectText": restored_review["objectText"],
                            "restoredStatusText": restored_review["statusText"],
                        }
                    )
                finally:
                    restored_page.close()
                page.locator('[data-trace-card][data-trace-anchor="P035-S02"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        return selected && selected.textContent.trim() === "P035-S02";
                    }""",
                    timeout=5000,
                )
                trace_switch_focus_reset_review = page.evaluate(
                    """() => {
                        const visibleCoverageButtons = Array.from(
                            document.querySelectorAll("[data-circuit-coverage-kind]")
                        ).filter((button) => !button.hidden);
                        return {
                            selectedAnchor: document
                                .querySelector("#demo-reconstruction-selected-anchor")
                                ?.textContent?.trim() || "",
                            coverageTabStopIds: visibleCoverageButtons
                                .filter((button) => button.getAttribute("tabindex") === "0")
                                .map((button) => button.getAttribute("data-circuit-coverage-id")),
                            pressedCoverageIds: visibleCoverageButtons
                                .filter((button) => button.getAttribute("aria-pressed") === "true")
                                .map((button) => button.getAttribute("data-circuit-coverage-id")),
                            reviewObjectText: document
                                .querySelector("#demo-reconstruction-review-object")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-playback-step="P035-S04"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const activeStep = document.querySelector("#demo-reconstruction-playback-active-step");
                        return selected
                            && selected.textContent.trim() === "P035-S04"
                            && activeStep
                            && activeStep.textContent.includes("P035-S04")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length === 18
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 20;
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-step-playback").screenshot(
                    path=str(step_playback_path)
                )
                step_playback_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            selectedAnchor: document
                                .querySelector("#demo-reconstruction-selected-anchor")
                                ?.textContent?.trim() || "",
                            activeStep: document
                                .querySelector("#demo-reconstruction-playback-active-step")
                                ?.textContent?.trim() || "",
                            activeButtonCount: document.querySelectorAll(
                                "[data-playback-step][aria-pressed='true']"
                            ).length,
                            nodeCountText: document
                                .querySelector("#demo-reconstruction-playback-node-count")
                                ?.textContent?.trim() || "",
                            wireCountText: document
                                .querySelector("#demo-reconstruction-playback-wire-count")
                                ?.textContent?.trim() || "",
                            highlightedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length
                                : 0,
                            highlightedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            reviewObjectText: document
                                .querySelector("#demo-reconstruction-review-object")
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
                            playbackStepCount: document.querySelectorAll("[data-playback-step]").length,
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
                page.wait_for_function(
                    """() => {
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        return status
                            && status.textContent.trim() === "DEPLOYED"
                            && output
                            && output.textContent.trim() === "ON";
                    }""",
                    timeout=5000,
                )
                max_reverse_output_mirror = page.evaluate(
                    """() => ({
                        status: document.querySelector("#demo-reconstruction-output-mirror-status")?.textContent?.trim() || "",
                        logic: document.querySelector("#demo-reconstruction-output-mirror-logic")?.textContent?.trim() || "",
                        thr: document.querySelector("#demo-reconstruction-output-mirror-thr")?.textContent?.trim() || "",
                        summary: document.querySelector("#demo-reconstruction-output-mirror-summary")?.textContent?.trim() || "",
                        custody: document.querySelector("#demo-reconstruction-custody-output")?.textContent?.trim() || "",
                        outputs: {
                            tls: document.querySelector("#demo-reconstruction-output-mirror-tls")?.textContent?.trim() || "",
                            etrac: document.querySelector("#demo-reconstruction-output-mirror-etrac")?.textContent?.trim() || "",
                            eec: document.querySelector("#demo-reconstruction-output-mirror-eec")?.textContent?.trim() || "",
                            thr_lock: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                        },
                    })"""
                )
                frame.locator("body").screenshot(path=str(max_reverse_path))
                frame.locator('section[aria-labelledby="outputs-heading"]').scroll_into_view_if_needed()
                frame.locator('section[aria-labelledby="outputs-heading"]').screenshot(path=str(max_reverse_outputs_path))
                inhibit = _interaction_snapshot(frame, "inhibit-block", "FAULT")
                page.wait_for_function(
                    """() => {
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        return status
                            && status.textContent.trim() === "FAULT"
                            && output
                            && output.textContent.trim() === "BLOCKED";
                    }""",
                    timeout=5000,
                )
                inhibit_output_mirror = page.evaluate(
                    """() => ({
                        status: document.querySelector("#demo-reconstruction-output-mirror-status")?.textContent?.trim() || "",
                        logic: document.querySelector("#demo-reconstruction-output-mirror-logic")?.textContent?.trim() || "",
                        thr: document.querySelector("#demo-reconstruction-output-mirror-thr")?.textContent?.trim() || "",
                        summary: document.querySelector("#demo-reconstruction-output-mirror-summary")?.textContent?.trim() || "",
                        custody: document.querySelector("#demo-reconstruction-custody-output")?.textContent?.trim() || "",
                        outputs: {
                            tls: document.querySelector("#demo-reconstruction-output-mirror-tls")?.textContent?.trim() || "",
                            etrac: document.querySelector("#demo-reconstruction-output-mirror-etrac")?.textContent?.trim() || "",
                            eec: document.querySelector("#demo-reconstruction-output-mirror-eec")?.textContent?.trim() || "",
                            thr_lock: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                        },
                    })"""
                )
                frame.locator("body").screenshot(path=str(inhibit_path))
                frame.locator('section[aria-labelledby="outputs-heading"]').scroll_into_view_if_needed()
                frame.locator('section[aria-labelledby="outputs-heading"]').screenshot(path=str(inhibit_outputs_path))
                page.locator("#demo-reconstruction-scenario-ledger").screenshot(
                    path=str(scenario_ledger_path)
                )
                scenario_ledger_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            rowCount: document.querySelectorAll("[data-scenario-ledger-row]").length,
                            statusText: text("#demo-reconstruction-scenario-ledger-status"),
                            activeRows: Array.from(
                                document.querySelectorAll("[data-scenario-ledger-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-scenario-ledger-row")),
                            maxReverseText: text('[data-scenario-ledger-row="max-reverse"]'),
                            inhibitText: text('[data-scenario-ledger-row="inhibit-block"]'),
                        };
                    }"""
                )
                page.locator('[data-scenario-ledger-row="max-reverse"]').click()
                page.wait_for_function(
                    """() => {
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const row = document.querySelector('[data-scenario-ledger-row="max-reverse"]');
                        return status
                            && status.textContent.trim() === "DEPLOYED"
                            && output
                            && output.textContent.trim() === "ON"
                            && row
                            && row.getAttribute("aria-pressed") === "true";
                    }""",
                    timeout=5000,
                )
                scenario_ledger_outer_control = page.evaluate(
                    """() => ({
                        status: document.querySelector("#demo-reconstruction-output-mirror-status")?.textContent?.trim() || "",
                        output: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                        activeRows: Array.from(
                            document.querySelectorAll("[data-scenario-ledger-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-scenario-ledger-row")),
                        maxReverseText: document
                            .querySelector('[data-scenario-ledger-row="max-reverse"]')
                            ?.textContent?.trim() || "",
                    })"""
                )
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
                review_index_path,
                chain_svg_path,
                keyboard_review_path,
                review_deep_link_path,
                step_playback_path,
                object_provenance_path,
                signal_neighborhood_path,
                completion_ladder_path,
                review_packet_path,
                custody_matrix_path,
                scenario_ledger_path,
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
            and source_map_review["reviewIndexButtonCount"] == 7
            and source_map_review["sequenceStepCount"] == 5
            and source_map_review["traceCardCount"] == 5
            and source_map_review["playbackStepCount"] == 5
            and source_map_review["ladderStepCount"] == 5
            and source_map_review["custodyStepCount"] == 5
            and source_map_review["coverageNodeButtonCount"] == 20
            and source_map_review["coverageWireButtonCount"] == 23
            and source_map_review["selectedNodeChipCount"] > 0
            and source_map_review["selectedWireChipCount"] > 0
            and source_map_review["nodeCoverage"] == "20/20"
            and source_map_review["wireCoverage"] == "23/23"
        )
        else "fail",
        "review_index_navigation": "pass"
        if (
            review_index_review["visible"]
            and review_index_review["buttonCount"] == 7
            and review_index_review["activeTargets"] == ["demo-reconstruction-docx-circuit-map"]
            and "P035-S01" in review_index_review["stepText"]
            and review_index_navigation["activeTargets"] == ["demo-reconstruction-scenario-ledger"]
            and review_index_navigation["scrollY"] > 0
            and "P035-S05" in review_index_after_trace["stepText"]
            and "等待聚焦" in review_index_after_trace["objectText"]
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
        "trace_switch_clears_object_focus": "pass"
        if (
            trace_switch_focus_reset_review["selectedAnchor"] == "P035-S02"
            and trace_switch_focus_reset_review["coverageTabStopIds"] == ["logic4"]
            and trace_switch_focus_reset_review["pressedCoverageIds"] == []
            and "整句链路" in trace_switch_focus_reset_review["reviewObjectText"]
        )
        else "fail",
        "step_playback_cumulative_circuit": "pass"
        if (
            step_playback_review["selectedAnchor"] == "P035-S04"
            and "P035-S04" in step_playback_review["activeStep"]
            and step_playback_review["activeButtonCount"] == 1
            and step_playback_review["highlightedNodeCount"] == 18
            and step_playback_review["highlightedWireCount"] == 20
            and "18/20" in step_playback_review["nodeCountText"]
            and "20/23" in step_playback_review["wireCountText"]
            and "累计构建" in step_playback_review["reviewObjectText"]
        )
        else "fail",
        "object_provenance_traceability": "pass"
        if (
            "logic4" in object_provenance_review["objectText"]
            and object_provenance_review["sourceCount"] >= 2
            and object_provenance_review["stepCount"] >= 1
            and any("logic4" in item for item in object_provenance_review["sourceItems"])
            and any("P035-S05" in item for item in object_provenance_review["stepItems"])
            and "wire_logic4_thr_lock" in wire_provenance_review["objectText"]
            and wire_provenance_review["sourceCount"] >= 2
            and wire_provenance_review["stepCount"] >= 1
            and any(
                "logic4" in item or "thr_lock" in item
                for item in wire_provenance_review["sourceItems"]
            )
            and any("P035-S05" in item for item in wire_provenance_review["stepItems"])
        )
        else "fail",
        "signal_neighborhood_readback": "pass"
        if (
            "logic4" in signal_neighborhood_review["objectText"]
            and signal_neighborhood_review["incomingCount"] == 2
            and signal_neighborhood_review["outgoingCount"] == 1
            and signal_neighborhood_review["adjacentCount"] == 3
            and "wire_vdt90_logic4" in signal_neighborhood_review["incomingText"]
            and "wire_logic3_logic4" in signal_neighborhood_review["incomingText"]
            and "wire_logic4_thr_lock" in signal_neighborhood_review["outgoingText"]
            and "THR_LOCK" in signal_neighborhood_review["adjacentText"]
            and "wire_logic4_thr_lock" in signal_neighborhood_wire_review["objectText"]
            and "L4" in signal_neighborhood_wire_review["incomingText"]
            and "THR_LOCK" in signal_neighborhood_wire_review["outgoingText"]
        )
        else "fail",
        "completion_ladder_readback": "pass"
        if (
            completion_ladder_review["stepCount"] == 5
            and "5/5" in completion_ladder_review["summaryText"]
            and "EEC" in completion_ladder_review["s03Text"]
            and "PLS" in completion_ladder_review["s03Text"]
            and "PDU" in completion_ladder_review["s03Text"]
            and "THR_LOCK" in completion_ladder_review["s05Text"]
            and "20/20" in completion_ladder_review["s05Text"]
            and "23/23" in completion_ladder_review["s05Text"]
        )
        else "fail",
        "review_packet_readiness": "pass"
        if (
            review_packet_review["visible"]
            and review_packet_review["gateCount"] == 5
            and review_packet_review["passGateCount"] >= 4
            and review_packet_after_wire_focus["passGateCount"] == 5
            and "uploads/20260409-thrust-reverser-control-logic.docx" in review_packet_review["sourceText"]
            and "20/20" in review_packet_review["contractText"]
            and "23/23" in review_packet_review["contractText"]
            and "P035-S05" in review_packet_review["stepText"]
            and "wire_logic4_thr_lock" in review_packet_after_wire_focus["objectText"]
        )
        else "fail",
        "custody_matrix_readback": "pass"
        if (
            custody_matrix_review["stepCount"] == 5
            and custody_matrix_review["activeButtonCount"] == 1
            and "5/5" in custody_matrix_review["summaryText"]
            and "20/20" in custody_matrix_review["summaryText"]
            and "23/23" in custody_matrix_review["summaryText"]
            and "P035-S04" in custody_matrix_review["activeText"]
            and "18/20" in custody_matrix_review["activeText"]
            and "20/23" in custody_matrix_review["activeText"]
            and "18/20" in custody_matrix_review["s04Text"]
            and "20/23" in custody_matrix_review["s04Text"]
            and "THR_LOCK" in custody_matrix_review["s05Text"]
            and "20/20" in custody_matrix_review["s05Text"]
            and "23/23" in custody_matrix_review["s05Text"]
            and custody_matrix_review["highlightedNodeCount"] == 18
            and custody_matrix_review["highlightedWireCount"] == 20
        )
        else "fail",
        "review_hash_link": "pass"
        if (
            review_deep_link["hash"] == "#step=P035-S05&focus=wire%3Awire_logic4_thr_lock&q=logic4"
            and review_deep_link["linkHref"].endswith(
                "/demo-reconstruction#step=P035-S05&focus=wire%3Awire_logic4_thr_lock&q=logic4"
            )
        )
        else "fail",
        "review_hash_restore": "pass"
        if (
            review_deep_link["restoredSelectedAnchor"] == "P035-S05"
            and review_deep_link["restoredQuery"] == "logic4"
            and review_deep_link["restoredVisibleNodeCount"] == 1
            and review_deep_link["restoredVisibleWireCount"] == 3
            and review_deep_link["restoredFocusedWireCount"] == 1
            and "wire_logic4_thr_lock" in review_deep_link["restoredObjectText"]
            and "wire_logic4_thr_lock" in review_deep_link["restoredStatusText"]
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
            and mobile_geometry["playbackStepCount"] == 5
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
        "output_mirror_sync": "pass"
        if (
            max_reverse_output_mirror["status"] == "DEPLOYED"
            and max_reverse_output_mirror["outputs"]["thr_lock"] == "ON"
            and "L4:ON" in max_reverse_output_mirror["logic"]
            and inhibit_output_mirror["status"] == "FAULT"
            and inhibit_output_mirror["outputs"]["thr_lock"] == "BLOCKED"
            and "BLOCKED" in inhibit_output_mirror["thr"]
            and "DEPLOYED" in max_reverse_output_mirror["custody"]
            and "ON" in max_reverse_output_mirror["custody"]
            and "FAULT" in inhibit_output_mirror["custody"]
            and "BLOCKED" in inhibit_output_mirror["custody"]
        )
        else "fail",
        "scenario_ledger_readback": "pass"
        if (
            scenario_ledger_review["rowCount"] == 5
            and "2/5" in scenario_ledger_review["statusText"]
            and scenario_ledger_review["activeRows"] == ["inhibit-block"]
            and "DEPLOYED" in scenario_ledger_review["maxReverseText"]
            and "THR:ON" in scenario_ledger_review["maxReverseText"]
            and "FAULT" in scenario_ledger_review["inhibitText"]
            and "THR:BLOCKED" in scenario_ledger_review["inhibitText"]
            and scenario_ledger_outer_control["status"] == "DEPLOYED"
            and scenario_ledger_outer_control["output"] == "ON"
            and scenario_ledger_outer_control["activeRows"] == ["max-reverse"]
            and "DEPLOYED" in scenario_ledger_outer_control["maxReverseText"]
        )
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
            "review_index": str(review_index_path),
            "chain_svg": str(chain_svg_path),
            "keyboard_review": str(keyboard_review_path),
            "review_deep_link": str(review_deep_link_path),
            "step_playback": str(step_playback_path),
            "object_provenance": str(object_provenance_path),
            "signal_neighborhood": str(signal_neighborhood_path),
            "completion_ladder": str(completion_ladder_path),
            "review_packet": str(review_packet_path),
            "custody_matrix": str(custody_matrix_path),
            "scenario_ledger": str(scenario_ledger_path),
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
        "review_index_review": review_index_review,
        "review_index_navigation": review_index_navigation,
        "review_index_after_trace": review_index_after_trace,
        "trace_selection_review": trace_selection_review,
        "embedded_trace_highlight_review": embedded_trace_highlight_review,
        "embedded_trace_chip_focus_review": embedded_trace_chip_focus_review,
        "coverage_matrix_review": coverage_matrix_review,
        "coverage_filter_review": coverage_filter_review,
        "keyboard_review": keyboard_review,
        "trace_switch_focus_reset_review": trace_switch_focus_reset_review,
        "step_playback_review": step_playback_review,
        "object_provenance_review": object_provenance_review,
        "signal_neighborhood_review": signal_neighborhood_review,
        "signal_neighborhood_wire_review": signal_neighborhood_wire_review,
        "wire_provenance_review": wire_provenance_review,
        "completion_ladder_review": completion_ladder_review,
        "review_packet_review": review_packet_review,
        "review_packet_after_wire_focus": review_packet_after_wire_focus,
        "custody_matrix_review": custody_matrix_review,
        "scenario_ledger_review": scenario_ledger_review,
        "scenario_ledger_outer_control": scenario_ledger_outer_control,
        "review_deep_link": review_deep_link,
        "source_chip_focus_review": source_chip_focus_review,
        "responsive_geometry": {
            "desktop": desktop_geometry,
            "mobile": mobile_geometry,
        },
        "interactions": {
            "max-reverse": max_reverse,
            "inhibit-block": inhibit,
        },
        "output_mirror": {
            "max-reverse": max_reverse_output_mirror,
            "inhibit-block": inhibit_output_mirror,
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
                "review_index_navigation": "fail",
                "trace_selection_interaction": "fail",
                "embedded_trace_highlight": "fail",
                "embedded_trace_chip_focus": "fail",
                "coverage_matrix_focus": "fail",
                "coverage_matrix_filter": "fail",
                "step_playback_cumulative_circuit": "fail",
                "object_provenance_traceability": "fail",
                "signal_neighborhood_readback": "fail",
                "completion_ladder_readback": "fail",
                "review_packet_readiness": "fail",
                "custody_matrix_readback": "fail",
                "source_chip_focus": "fail",
                "responsive_geometry": "fail",
                "embedded_codex_light_palette": "fail",
                "node_wire_pixels": "fail",
                "preset_interactions": "fail",
                "hud_output_linkage": "fail",
                "output_mirror_sync": "fail",
                "scenario_ledger_readback": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

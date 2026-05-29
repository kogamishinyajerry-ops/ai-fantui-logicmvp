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
    assembly_map_path = artifact_dir / f"demo-reconstruction-assembly-map-{stamp}.png"
    logic_equation_path = artifact_dir / f"demo-reconstruction-logic-equation-board-{stamp}.png"
    topology_matrix_path = artifact_dir / f"demo-reconstruction-topology-matrix-{stamp}.png"
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
    scenario_truth_path = artifact_dir / f"demo-reconstruction-scenario-truth-table-{stamp}.png"
    operator_runway_path = artifact_dir / f"demo-reconstruction-operator-runway-{stamp}.png"
    proof_transcript_path = artifact_dir / f"demo-reconstruction-proof-transcript-{stamp}.png"
    control_strip_path = artifact_dir / f"demo-reconstruction-control-strip-{stamp}.png"
    sentence_runner_path = artifact_dir / f"demo-reconstruction-sentence-runner-{stamp}.png"
    proof_path_path = artifact_dir / f"demo-reconstruction-proof-path-{stamp}.png"
    scenario_comparator_path = artifact_dir / f"demo-reconstruction-scenario-comparator-{stamp}.png"
    review_verdict_path = artifact_dir / f"demo-reconstruction-review-verdict-{stamp}.png"
    max_reverse_path = artifact_dir / f"demo-reconstruction-mvp-max-reverse-{stamp}.png"
    max_reverse_outputs_path = artifact_dir / f"demo-reconstruction-mvp-max-reverse-outputs-{stamp}.png"
    inhibit_path = artifact_dir / f"demo-reconstruction-mvp-inhibit-block-{stamp}.png"
    inhibit_outputs_path = artifact_dir / f"demo-reconstruction-mvp-inhibit-block-outputs-{stamp}.png"
    restricted = _restricted_diff()
    console_errors: list[str] = []

    def capture_console_error(msg: Any) -> None:
        if msg.type != "error":
            return
        text = msg.text
        if text.startswith("Failed to load resource:") and "404" in text:
            return
        console_errors.append(text)

    def capture_bad_response(response: Any) -> None:
        if response.status < 400 or response.url.endswith("/favicon.ico"):
            return
        console_errors.append(f"{response.status} {response.url}")

    server, thread, base_url = _start_server()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1366, "height": 768})
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.on("console", capture_console_error)
                page.on("response", capture_bad_response)
                page.route("**/favicon.ico", lambda route: route.fulfill(status=204, body=""))
                page.goto(f"{base_url}/demo-reconstruction", wait_until="networkidle")
                page.wait_for_selector("#demo-reconstruction-console-frame", timeout=5000)
                page.wait_for_function(
                    """() => {
                        return document.querySelectorAll("[data-trace-card]").length >= 5
                            && document.querySelectorAll(".demo-reconstruction-source-entry").length >= 10
                            && document.querySelectorAll("[data-requirement-ledger-row]").length >= 60
                            && document.querySelectorAll(".demo-reconstruction-sequence-step").length >= 5
                            && document.querySelectorAll("[data-operator-runway-row]").length >= 6
                            && document.querySelectorAll("[data-proof-transcript-row]").length >= 6
                            && document.querySelectorAll("[data-control-strip-action]").length === 3
                            && document.querySelectorAll("[data-sentence-runner-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-focus-id]").length >= 5
                            && document.querySelectorAll("[data-proof-path-coverage-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-coverage-focus-id]").length >= 5
                            && document.querySelectorAll("[data-proof-path-delta-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-delta-focus-id]").length >= 5
                            && document.querySelectorAll("[data-proof-path-source-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-source-anchor]").length >= 5
                            && document.querySelectorAll("[data-proof-path-sentence-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-sentence-focus-id]").length >= 40
                            && document.querySelectorAll("[data-proof-path-predicate-step]").length === 5
                            && document.querySelectorAll("[data-proof-path-predicate-focus-id]").length >= 5
                            && document.querySelectorAll("[data-proof-path-blueprint-step]").length === 5
                            && document.querySelector("[data-proof-path-blueprint-chain='complete']")
                            && document.querySelector("[data-proof-path-review-strip='first-screen']")
                            && document.querySelector("[data-proof-path-object-inspector]")
                            && document.querySelectorAll("[data-proof-path-output-target]").length === 5
                            && document.querySelectorAll("[data-scenario-comparator-action]").length === 2
                            && document.querySelectorAll("[data-review-verdict-card]").length === 5
                            && document.querySelectorAll("[data-circuit-coverage-kind='node']").length === 20
                            && document.querySelectorAll("[data-circuit-coverage-kind='wire']").length === 23
                            && document.querySelectorAll("[data-topology-wire]").length === 23;
                    }""",
                    timeout=7000,
                )
                page.screenshot(path=str(first_screen_path), full_page=True)
                first_screen_review = {
                    "review_index_visible": page.locator(
                        "#demo-reconstruction-review-index"
                    ).is_visible(timeout=5000),
                    "assembly_map_visible": page.locator(
                        "#demo-reconstruction-assembly-map"
                    ).is_visible(timeout=5000),
                    "topology_matrix_visible": page.locator(
                        "#demo-reconstruction-topology-matrix"
                    ).is_visible(timeout=5000),
                    "source_map_visible": page.locator(
                        "#demo-reconstruction-docx-circuit-map"
                    ).is_visible(timeout=5000),
                    "requirement_ledger_visible": page.locator(
                        "#demo-reconstruction-requirement-ledger"
                    ).is_visible(timeout=5000),
                    "trace_board_visible": page.locator(
                        "#demo-reconstruction-docx-trace-board"
                    ).is_visible(timeout=5000),
                    "logic_equation_board_visible": page.locator(
                        "#demo-reconstruction-logic-equation-board"
                    ).is_visible(timeout=5000),
                    "operator_guide_visible": page.locator(
                        "#demo-reconstruction-operator-guide"
                    ).is_visible(timeout=5000),
                    "output_mirror_visible": page.locator(
                        "#demo-reconstruction-output-mirror"
                    ).is_visible(timeout=5000),
                    "control_strip_visible": page.locator(
                        "#demo-reconstruction-control-strip"
                    ).is_visible(timeout=5000),
                    "sentence_runner_visible": page.locator(
                        "#demo-reconstruction-sentence-runner"
                    ).is_visible(timeout=5000),
                    "proof_path_visible": page.locator(
                        "#demo-reconstruction-proof-path"
                    ).is_visible(timeout=5000),
                    "proof_path_review_strip_visible": page.locator(
                        "#demo-reconstruction-proof-path-review-strip"
                    ).is_visible(timeout=5000),
                    "scenario_comparator_visible": page.locator(
                        "#demo-reconstruction-scenario-comparator"
                    ).is_visible(timeout=5000),
                    "review_verdict_visible": page.locator(
                        "#demo-reconstruction-review-verdict"
                    ).is_visible(timeout=5000),
                    "scenario_ledger_visible": page.locator(
                        "#demo-reconstruction-scenario-ledger"
                    ).is_visible(timeout=5000),
                    "scenario_truth_table_visible": page.locator(
                        "#demo-reconstruction-scenario-truth-table"
                    ).is_visible(timeout=5000),
                    "operator_runway_visible": page.locator(
                        "#demo-reconstruction-operator-runway"
                    ).is_visible(timeout=5000),
                    "proof_transcript_visible": page.locator(
                        "#demo-reconstruction-proof-transcript"
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
                            requirementLedgerRowCount: document.querySelectorAll("[data-requirement-ledger-row]").length,
                            requirementLedgerMappedCount: document.querySelectorAll("[data-requirement-ledger-row][data-requirement-ledger-status='mapped']").length,
                            requirementLedgerContextCount: document.querySelectorAll("[data-requirement-ledger-row][data-requirement-ledger-status='context']").length,
                            requirementLedgerP035Count: document.querySelectorAll("[data-requirement-ledger-row][data-requirement-ledger-status='p035']").length,
                            requirementLedgerSummary: text("#demo-reconstruction-requirement-ledger-summary"),
                            requirementLedgerStatus: text("#demo-reconstruction-requirement-ledger-status"),
                            reviewIndexButtonCount: document.querySelectorAll("[data-review-index-target]").length,
                            sequenceStepCount: document.querySelectorAll(".demo-reconstruction-sequence-step").length,
                            traceCardCount: document.querySelectorAll("[data-trace-card]").length,
                            playbackStepCount: document.querySelectorAll("[data-playback-step]").length,
                            assemblyStepCount: document.querySelectorAll("[data-assembly-step]").length,
                            topologyRowCount: document.querySelectorAll("[data-topology-wire]").length,
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
                page.locator('[data-requirement-ledger-filter="context"]').click()
                page.wait_for_function(
                    """() => {
                        const rows = document.querySelectorAll("[data-requirement-ledger-row]");
                        const filter = document.querySelector('[data-requirement-ledger-filter="context"]');
                        const status = document.querySelector("#demo-reconstruction-requirement-ledger-status")?.textContent || "";
                        return rows.length === 18
                            && filter
                            && filter.getAttribute("aria-pressed") === "true"
                            && status.includes("18/67");
                    }""",
                    timeout=5000,
                )
                requirement_ledger_context_review = page.evaluate(
                    """() => ({
                        visibleRows: document.querySelectorAll("[data-requirement-ledger-row]").length,
                        selectedFilters: Array.from(
                            document.querySelectorAll("[data-requirement-ledger-filter][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-requirement-ledger-filter")),
                        statusText: document.querySelector("#demo-reconstruction-requirement-ledger-status")?.textContent?.trim() || "",
                    })"""
                )
                page.locator('[data-requirement-ledger-filter="all"]').click()
                page.locator("#demo-reconstruction-requirement-ledger-search").fill("logic4")
                page.wait_for_function(
                    """() => {
                        const rows = Array.from(document.querySelectorAll("[data-requirement-ledger-row]"));
                        const target = document.querySelector('[data-requirement-ledger-row="step:P035-S05"]');
                        const status = document.querySelector("#demo-reconstruction-requirement-ledger-status")?.textContent || "";
                        return rows.length >= 3 && target && status.includes("/");
                    }""",
                    timeout=5000,
                )
                page.locator('[data-requirement-ledger-row="step:P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const row = document.querySelector('[data-requirement-ledger-row="step:P035-S05"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true']").length >= 4;
                    }""",
                    timeout=5000,
                )
                requirement_ledger_action_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            query: document.querySelector("#demo-reconstruction-requirement-ledger-search")?.value || "",
                            visibleRows: document.querySelectorAll("[data-requirement-ledger-row]").length,
                            selectedRows: Array.from(
                                document.querySelectorAll("[data-requirement-ledger-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-requirement-ledger-row")),
                            selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                            highlightedCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true']").length
                                : 0,
                            statusText: document.querySelector("#demo-reconstruction-requirement-ledger-status")?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S01"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        return selected && selected.textContent.trim() === "P035-S01";
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-review-index").screenshot(
                    path=str(review_index_path)
                )
                page.locator("#demo-reconstruction-assembly-map").screenshot(
                    path=str(assembly_map_path)
                )
                page.locator("#demo-reconstruction-topology-matrix").screenshot(
                    path=str(topology_matrix_path)
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
                            proofPathText: text("#demo-reconstruction-review-index-proof-path"),
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
                page.locator('[data-review-index-target="demo-reconstruction-proof-path"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector(
                            '[data-review-index-target="demo-reconstruction-proof-path"][aria-pressed="true"]'
                        );
                        const target = document.querySelector("#demo-reconstruction-proof-path");
                        return !!active && !!target && window.scrollY > 0;
                    }""",
                    timeout=5000,
                )
                review_index_proof_path_navigation = page.evaluate(
                    """() => ({
                        activeTargets: Array.from(
                            document.querySelectorAll("[data-review-index-target][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-review-index-target")),
                        scrollY: window.scrollY,
                    })"""
                )
                assembly_map_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-assembly-map"),
                            itemCount: document.querySelectorAll("[data-assembly-step]").length,
                            actionCount: document.querySelectorAll("[data-assembly-step-button]").length,
                            focusChipCount: document.querySelectorAll("[data-assembly-focus-id]").length,
                            completeCount: document.querySelectorAll("[data-assembly-complete='true']").length,
                            summaryText: text("#demo-reconstruction-assembly-summary"),
                            finalText: text("#demo-reconstruction-assembly-final"),
                            s01Text: text('[data-assembly-step="P035-S01"]'),
                            s05Text: text('[data-assembly-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator("#demo-reconstruction-logic-equation-board").screenshot(
                    path=str(logic_equation_path)
                )
                logic_equation_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        const rows = Array.from(document.querySelectorAll("[data-logic-equation-row]"));
                        const items = Array.from(document.querySelectorAll("[data-logic-equation]"));
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-logic-equation-board"),
                            rowCount: rows.length,
                            passCount: items.filter((item) => item.dataset.logicEquationStatus === "pass").length,
                            summaryText: text("#demo-reconstruction-logic-equation-summary"),
                            l1Text: text('[data-logic-equation="logic1"]'),
                            l4Text: text('[data-logic-equation="logic4"]'),
                        };
                    }"""
                )
                page.locator('[data-logic-equation-row="logic4"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const row = document.querySelector('[data-logic-equation-row="logic4"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        const object = document.querySelector("#demo-reconstruction-review-object")?.textContent || "";
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && selected.trim() === "P035-S05"
                            && object.includes("wire_logic4_thr_lock")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                logic_equation_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            activeRows: Array.from(
                                document.querySelectorAll("[data-logic-equation-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-logic-equation-row")),
                            selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                            reviewObjectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                            highlightedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                        };
                    }"""
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S01"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const readback = document.querySelector("#demo-reconstruction-topology-readback")?.textContent || "";
                        return selected
                            && selected.textContent.trim() === "P035-S01"
                            && readback.includes("23/23");
                    }""",
                    timeout=5000,
                )
                topology_matrix_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-topology-matrix"),
                            rowCount: document.querySelectorAll("[data-topology-wire]").length,
                            buttonCount: document.querySelectorAll("[data-topology-wire-row]").length,
                            summaryText: text("#demo-reconstruction-topology-summary"),
                            readbackText: text("#demo-reconstruction-topology-readback"),
                            firstText: text('[data-topology-wire="wire_ra_logic1"]'),
                            s05Text: text('[data-topology-wire="wire_logic4_thr_lock"]'),
                        };
                    }"""
                )
                page.locator('[data-topology-wire-row="wire_logic4_thr_lock"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const row = document.querySelector('[data-topology-wire-row="wire_logic4_thr_lock"]');
                        const readback = document.querySelector("#demo-reconstruction-topology-readback")?.textContent || "";
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && readback.includes("P035-S05")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                topology_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            activeRows: Array.from(
                                document.querySelectorAll("[data-topology-wire-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-topology-wire-row")),
                            highlightedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            readbackText: document
                                .querySelector("#demo-reconstruction-topology-readback")
                                ?.textContent?.trim() || "",
                            reviewObjectText: document
                                .querySelector("#demo-reconstruction-review-object")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-topology-step-filter="P035-S05"]').click()
                page.locator("#demo-reconstruction-topology-search").fill("THR_LOCK")
                page.wait_for_function(
                    """() => {
                        const rows = Array.from(document.querySelectorAll("[data-topology-wire]"));
                        const visibleRows = rows.filter((row) => !row.hidden);
                        const status = document.querySelector("#demo-reconstruction-topology-filter-status")?.textContent || "";
                        const selected = document.querySelector('[data-topology-step-filter="P035-S05"][aria-pressed="true"]');
                        return selected
                            && visibleRows.length === 1
                            && visibleRows[0].getAttribute("data-topology-wire") === "wire_logic4_thr_lock"
                            && status.includes("1/23")
                            && status.includes("P035-S05");
                    }""",
                    timeout=5000,
                )
                topology_filter_review = page.evaluate(
                    """() => ({
                        query: document.querySelector("#demo-reconstruction-topology-search")?.value || "",
                        hash: window.location.hash || "",
                        statusText: document.querySelector("#demo-reconstruction-topology-filter-status")?.textContent?.trim() || "",
                        selectedFilters: Array.from(
                            document.querySelectorAll("[data-topology-step-filter][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-topology-step-filter")),
                        visibleRows: Array.from(document.querySelectorAll("[data-topology-wire]"))
                            .filter((row) => !row.hidden)
                            .map((row) => row.getAttribute("data-topology-wire")),
                        selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                    })"""
                )
                page.goto(f"{base_url}/demo-reconstruction{topology_filter_review['hash']}", wait_until="networkidle")
                page.wait_for_function(
                    """() => {
                        return document.querySelectorAll("[data-trace-card]").length >= 5
                            && document.querySelectorAll(".demo-reconstruction-source-entry").length >= 10
                            && document.querySelectorAll("[data-topology-wire]").length === 23;
                    }""",
                    timeout=7000,
                )
                page.wait_for_function(
                    """() => {
                        const rows = Array.from(document.querySelectorAll("[data-topology-wire]"));
                        const visibleRows = rows.filter((row) => !row.hidden);
                        const status = document.querySelector("#demo-reconstruction-topology-filter-status")?.textContent || "";
                        const selected = document.querySelector('[data-topology-step-filter="P035-S05"][aria-pressed="true"]');
                        const query = document.querySelector("#demo-reconstruction-topology-search")?.value || "";
                        return selected
                            && query === "THR_LOCK"
                            && visibleRows.length === 1
                            && visibleRows[0].getAttribute("data-topology-wire") === "wire_logic4_thr_lock"
                            && status.includes("1/23")
                            && status.includes("P035-S05");
                    }""",
                    timeout=5000,
                )
                topology_filter_restore_review = page.evaluate(
                    """() => ({
                        query: document.querySelector("#demo-reconstruction-topology-search")?.value || "",
                        hash: window.location.hash || "",
                        statusText: document.querySelector("#demo-reconstruction-topology-filter-status")?.textContent?.trim() || "",
                        selectedFilters: Array.from(
                            document.querySelectorAll("[data-topology-step-filter][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-topology-step-filter")),
                        visibleRows: Array.from(document.querySelectorAll("[data-topology-wire]"))
                            .filter((row) => !row.hidden)
                            .map((row) => row.getAttribute("data-topology-wire")),
                        selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                    })"""
                )
                output_path_review = page.evaluate(
                    """() => ({
                        visible: !!document.querySelector("#demo-reconstruction-output-path-lane"),
                        targetCount: document.querySelectorAll("[data-output-path-target]").length,
                        selectedTargets: Array.from(
                            document.querySelectorAll("[data-output-path-target][aria-pressed='true']")
                        ).map((button) => button.getAttribute("data-output-path-target")),
                        rowCount: document.querySelectorAll("[data-output-path-wire]").length,
                        pathOrder: Array.from(document.querySelectorAll("[data-output-path-wire]"))
                            .map((row) => row.getAttribute("data-output-path-wire")),
                        summaryText: document.querySelector("#demo-reconstruction-output-path-summary")?.textContent?.trim() || "",
                        readbackText: document.querySelector("#demo-reconstruction-output-path-readback")?.textContent?.trim() || "",
                        finalText: document.querySelector('[data-output-path-wire="wire_logic4_thr_lock"]')?.textContent?.trim() || "",
                    })"""
                )
                page.locator('[data-output-path-wire-row="wire_logic4_thr_lock"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const row = document.querySelector('[data-output-path-wire-row="wire_logic4_thr_lock"]');
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                output_path_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            activeRows: Array.from(
                                document.querySelectorAll("[data-output-path-wire-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-output-path-wire-row")),
                            highlightedWireCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length
                                : 0,
                            reviewObjectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                            topologyReadbackText: document.querySelector("#demo-reconstruction-topology-readback")?.textContent?.trim() || "",
                        };
                    }"""
                )
                output_maturity_review = page.evaluate(
                    """() => ({
                        visible: !!document.querySelector("#demo-reconstruction-output-maturity-matrix"),
                        summaryText: document.querySelector("#demo-reconstruction-output-maturity-summary")?.textContent?.trim() || "",
                        stepCount: document.querySelectorAll("[data-output-maturity-step-label]").length,
                        cellCount: document.querySelectorAll("[data-output-maturity-step][data-output-maturity-target]").length,
                        activeCellCount: document.querySelectorAll("[data-output-maturity-active='true']").length,
                        s01TlsActive: document
                            .querySelector('[data-output-maturity-step="P035-S01"][data-output-maturity-target="tls115"]')
                            ?.getAttribute("data-output-maturity-active") || "",
                        s02EtracActive: document
                            .querySelector('[data-output-maturity-step="P035-S02"][data-output-maturity-target="etrac_540v"]')
                            ?.getAttribute("data-output-maturity-active") || "",
                        s03EecActive: document
                            .querySelector('[data-output-maturity-step="P035-S03"][data-output-maturity-target="eec_deploy"]')
                            ?.getAttribute("data-output-maturity-active") || "",
                        s03PduActive: document
                            .querySelector('[data-output-maturity-step="P035-S03"][data-output-maturity-target="pdu_motor"]')
                            ?.getAttribute("data-output-maturity-active") || "",
                        s05ThrActive: document
                            .querySelector('[data-output-maturity-step="P035-S05"][data-output-maturity-target="thr_lock"]')
                            ?.getAttribute("data-output-maturity-active") || "",
                    })"""
                )
                page.locator('[data-output-maturity-step="P035-S05"][data-output-maturity-target="thr_lock"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const cell = document.querySelector(
                            '[data-output-maturity-step="P035-S05"][data-output-maturity-target="thr_lock"]'
                        );
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        return cell
                            && cell.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-node='thr_lock'][data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                output_maturity_focus_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            selectedCells: Array.from(
                                document.querySelectorAll("[data-output-maturity-step][data-output-maturity-target][aria-pressed='true']")
                            ).map((cell) => `${cell.getAttribute("data-output-maturity-step")}:${cell.getAttribute("data-output-maturity-target")}`),
                            selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                            selectedOutputTarget: Array.from(
                                document.querySelectorAll("[data-output-path-target][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-output-path-target")),
                            highlightedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-node='thr_lock'][data-docx-trace-selected='true']").length
                                : 0,
                            reviewObjectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        };
                    }"""
                )
                output_maturity_hash = page.evaluate("() => window.location.hash || ''")
                page.goto(f"{base_url}/demo-reconstruction{output_maturity_hash}", wait_until="networkidle")
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const cell = document.querySelector(
                            '[data-output-maturity-step="P035-S05"][data-output-maturity-target="thr_lock"]'
                        );
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        return cell
                            && cell.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-node='thr_lock'][data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                output_maturity_restore_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            hash: window.location.hash || "",
                            selectedCells: Array.from(
                                document.querySelectorAll("[data-output-maturity-step][data-output-maturity-target][aria-pressed='true']")
                            ).map((cell) => `${cell.getAttribute("data-output-maturity-step")}:${cell.getAttribute("data-output-maturity-target")}`),
                            selectedAnchor: document.querySelector("#demo-reconstruction-selected-anchor")?.textContent?.trim() || "",
                            highlightedNodeCount: doc
                                ? doc.querySelectorAll("#fan-chain-svg [data-node='thr_lock'][data-docx-trace-selected='true']").length
                                : 0,
                            reviewObjectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-output-path-wire-row="wire_logic4_thr_lock"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const row = document.querySelector('[data-output-path-wire-row="wire_logic4_thr_lock"]');
                        const selectedCells = document.querySelectorAll(
                            "[data-output-maturity-step][data-output-maturity-target][aria-pressed='true']"
                        );
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && selectedCells.length === 0
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 1;
                    }""",
                    timeout=5000,
                )
                output_maturity_clear_review = page.evaluate(
                    """() => ({
                        selectedCells: Array.from(
                            document.querySelectorAll("[data-output-maturity-step][data-output-maturity-target][aria-pressed='true']")
                        ).map((cell) => `${cell.getAttribute("data-output-maturity-step")}:${cell.getAttribute("data-output-maturity-target")}`),
                        activeRows: Array.from(
                            document.querySelectorAll("[data-output-path-wire-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-output-path-wire-row")),
                        reviewObjectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                    })"""
                )
                page.evaluate(
                    """async () => {
                        const response = await fetch("/api/requirements-intake/deepseek-live-demo-replay", {headers: {"Accept": "application/json"}});
                        const payload = await response.json();
                        window.localStorage.setItem(
                            "ai-fantui-logic-builder-drawing-v1",
                            JSON.stringify(payload.drawing_payload)
                        );
                    }"""
                )
                page.goto(f"{base_url}/demo-reconstruction", wait_until="networkidle")
                page.wait_for_function(
                    """() => {
                        const finalRow = document.querySelector('[data-output-path-wire="wire_logic4_thr_lock"]');
                        const summary = document.querySelector("#demo-reconstruction-output-path-summary")?.textContent || "";
                        return document.querySelectorAll("[data-output-path-wire]").length === 15
                            && finalRow
                            && finalRow.textContent.includes("P035-S05")
                            && finalRow.textContent.includes("DOCX")
                            && summary.includes("15/23");
                    }""",
                    timeout=7000,
                )
                stored_output_path_review = page.evaluate(
                    """() => ({
                        rowCount: document.querySelectorAll("[data-output-path-wire]").length,
                        summaryText: document.querySelector("#demo-reconstruction-output-path-summary")?.textContent?.trim() || "",
                        finalText: document.querySelector('[data-output-path-wire="wire_logic4_thr_lock"]')?.textContent?.trim() || "",
                    })"""
                )
                page.evaluate(
                    """() => window.localStorage.removeItem("ai-fantui-logic-builder-drawing-v1")"""
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
                        proofPathText: document
                            .querySelector("#demo-reconstruction-review-index-proof-path")
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
                        const dashboardMetrics = Array.from(document.querySelectorAll("[data-review-packet-dashboard-metric]"));
                        const dashboardChecks = Array.from(document.querySelectorAll("[data-review-packet-dashboard-check]"));
                        return {
                            visible: !!document.querySelector("#demo-reconstruction-review-packet"),
                            dashboardVisible: !!document.querySelector("#demo-reconstruction-review-packet-dashboard"),
                            dashboardSummary: text("#demo-reconstruction-review-packet-dashboard-summary"),
                            dashboardMetricCount: dashboardMetrics.length,
                            dashboardPassMetricCount: dashboardMetrics.filter((metric) => metric.dataset.dashboardMetricStatus === "pass").length,
                            dashboardChecklistCount: dashboardChecks.length,
                            dashboardPassChecklistCount: dashboardChecks.filter((check) => check.dataset.dashboardCheckStatus === "pass").length,
                            dashboardMetricLabels: dashboardMetrics.map((metric) => metric.textContent.trim()),
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
                        const dashboardMetrics = Array.from(document.querySelectorAll("[data-review-packet-dashboard-metric]"));
                        const dashboardChecks = Array.from(document.querySelectorAll("[data-review-packet-dashboard-check]"));
                        return {
                            readinessText: text("#demo-reconstruction-review-packet-readiness"),
                            dashboardSummary: text("#demo-reconstruction-review-packet-dashboard-summary"),
                            objectText: text("#demo-reconstruction-review-packet-object"),
                            passGateCount: gates.filter((gate) => gate.dataset.packetGateStatus === "pass").length,
                            dashboardPassMetricCount: dashboardMetrics.filter((metric) => metric.dataset.dashboardMetricStatus === "pass").length,
                            dashboardPassChecklistCount: dashboardChecks.filter((check) => check.dataset.dashboardCheckStatus === "pass").length,
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
                page.locator('[data-proof-path-lane-mode="matrix"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-lane-mode="matrix"]');
                        const status = document.querySelector("#demo-reconstruction-proof-path-lane-mode-status");
                        const matrix = document.querySelector("#demo-reconstruction-proof-path-coverage-grid");
                        const source = document.querySelector("#demo-reconstruction-proof-path-source-rail");
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "矩阵"
                            && matrix
                            && !matrix.hidden
                            && source
                            && source.hidden
                            && window.location.hash.includes("lane=matrix");
                    }""",
                    timeout=5000,
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
                        f"{base_url}/demo-reconstruction{review_deep_link['hash']}",
                        wait_until="networkidle",
                    )
                    restored_page.wait_for_function(
                        """() => {
                            const frame = document.querySelector("#demo-reconstruction-console-frame");
                            const doc = frame && frame.contentDocument;
                            const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                            const search = document.querySelector("#demo-reconstruction-coverage-search");
                            const status = document.querySelector("#demo-reconstruction-embedded-highlight-status")?.textContent || "";
                            const laneStatus = document.querySelector("#demo-reconstruction-proof-path-lane-mode-status");
                            const activeLane = document.querySelector('[data-proof-path-lane-mode="matrix"]');
                            const matrix = document.querySelector("#demo-reconstruction-proof-path-coverage-grid");
                            const source = document.querySelector("#demo-reconstruction-proof-path-source-rail");
                            return selected
                                && selected.textContent.trim() === "P035-S05"
                                && search
                                && search.value === "logic4"
                                && laneStatus
                                && laneStatus.textContent.trim() === "矩阵"
                                && activeLane
                                && activeLane.getAttribute("aria-pressed") === "true"
                                && matrix
                                && !matrix.hidden
                                && source
                                && source.hidden
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
                            const visible = (selector) => {
                                const element = document.querySelector(selector);
                                return Boolean(element && !element.hidden);
                            };
                            return {
                                selectedAnchor: document
                                    .querySelector("#demo-reconstruction-selected-anchor")
                                    ?.textContent?.trim() || "",
                                query: document.querySelector("#demo-reconstruction-coverage-search")?.value || "",
                                laneStatus: document
                                    .querySelector("#demo-reconstruction-proof-path-lane-mode-status")
                                    ?.textContent?.trim() || "",
                                laneActiveModes: Array.from(
                                    document.querySelectorAll("[data-proof-path-lane-mode][aria-pressed='true']")
                                ).map((button) => button.getAttribute("data-proof-path-lane-mode")),
                                laneVisibleMatrix: visible("#demo-reconstruction-proof-path-coverage-grid"),
                                laneVisibleSource: visible("#demo-reconstruction-proof-path-source-rail"),
                                stripLane: document
                                    .querySelector("#demo-reconstruction-proof-path-review-lane")
                                    ?.textContent?.trim() || "",
                                stripStep: document
                                    .querySelector("#demo-reconstruction-proof-path-review-step")
                                    ?.textContent?.trim() || "",
                                stripObject: document
                                    .querySelector("#demo-reconstruction-proof-path-review-object")
                                    ?.textContent?.trim() || "",
                                stripLinkState: document
                                    .querySelector("#demo-reconstruction-proof-path-review-link-state")
                                    ?.textContent?.trim() || "",
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
                            "restoredLaneStatus": restored_review["laneStatus"],
                            "restoredLaneActiveModes": restored_review["laneActiveModes"],
                            "restoredLaneVisibleMatrix": restored_review["laneVisibleMatrix"],
                            "restoredLaneVisibleSource": restored_review["laneVisibleSource"],
                            "restoredStripLane": restored_review["stripLane"],
                            "restoredStripStep": restored_review["stripStep"],
                            "restoredStripObject": restored_review["stripObject"],
                            "restoredStripLinkState": restored_review["stripLinkState"],
                            "restoredVisibleNodeCount": restored_review["visibleNodeCount"],
                            "restoredVisibleWireCount": restored_review["visibleWireCount"],
                            "restoredFocusedWireCount": restored_review["focusedWireCount"],
                            "restoredObjectText": restored_review["objectText"],
                            "restoredStatusText": restored_review["statusText"],
                        }
                    )
                finally:
                    restored_page.close()
                page.locator('[data-proof-path-lane-mode="blueprint"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-lane-mode="blueprint"]');
                        const status = document.querySelector("#demo-reconstruction-proof-path-lane-mode-status");
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "蓝图"
                            && !window.location.hash.includes("lane=");
                    }""",
                    timeout=5000,
                )
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
                page.locator('[data-assembly-step-button="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const activeStep = document.querySelector("#demo-reconstruction-playback-active-step");
                        const action = document.querySelector('[data-assembly-step-button="P035-S05"]');
                        return activeStep
                            && activeStep.textContent.includes("P035-S05")
                            && action
                            && action.getAttribute("aria-pressed") === "true"
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length === 20
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 23;
                    }""",
                    timeout=5000,
                )
                assembly_map_action_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        return {
                            activeStep: document
                                .querySelector("#demo-reconstruction-playback-active-step")
                                ?.textContent?.trim() || "",
                            activeButtonCount: document.querySelectorAll(
                                "[data-assembly-step-button][aria-pressed='true']"
                            ).length,
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
                page.locator("#demo-reconstruction-scenario-truth-table").screenshot(
                    path=str(scenario_truth_path)
                )
                page.locator("#demo-reconstruction-operator-runway").screenshot(
                    path=str(operator_runway_path)
                )
                page.locator("#demo-reconstruction-proof-transcript").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.locator("#demo-reconstruction-proof-transcript").screenshot(
                    path=str(proof_transcript_path)
                )
                page.locator("#demo-reconstruction-control-strip").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.locator("#demo-reconstruction-control-strip").screenshot(
                    path=str(control_strip_path)
                )
                page.locator("#demo-reconstruction-sentence-runner").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.locator("#demo-reconstruction-sentence-runner").screenshot(
                    path=str(sentence_runner_path)
                )
                page.locator("#demo-reconstruction-proof-path").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.evaluate(
                    """() => {
                        const nav = document.querySelector(".unified-nav");
                        if (nav) nav.style.setProperty("visibility", "hidden");
                    }"""
                )
                page.locator("#demo-reconstruction-proof-path").screenshot(
                    path=str(proof_path_path)
                )
                page.evaluate(
                    """() => {
                        const nav = document.querySelector(".unified-nav");
                        if (nav) nav.style.removeProperty("visibility");
                    }"""
                )
                proof_path_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-step]").length,
                            finalCount: document.querySelectorAll("[data-proof-path-final='true']").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-step")),
                            statusText: text("#demo-reconstruction-proof-path-status"),
                            readbackText: text("#demo-reconstruction-proof-path-readback"),
                            focusChipCount: document.querySelectorAll("[data-proof-path-focus-id]").length,
                            firstFocusIds: Array.from(
                                document.querySelectorAll('[data-proof-path-row="P035-S01"] [data-proof-path-focus-id]')
                            ).map((button) => button.getAttribute("data-proof-path-focus-id")),
                            finalFocusIds: Array.from(
                                document.querySelectorAll('[data-proof-path-row="P035-S05"] [data-proof-path-focus-id]')
                            ).map((button) => button.getAttribute("data-proof-path-focus-id")),
                            firstText: text('[data-proof-path-step="P035-S01"]'),
                            finalText: text('[data-proof-path-step="P035-S05"]'),
                        };
                    }"""
                )
                proof_path_lane_default_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        const visible = (selector) => {
                            const element = document.querySelector(selector);
                            return Boolean(element && !element.hidden);
                        };
                        return {
                            activeModes: Array.from(
                                document.querySelectorAll("[data-proof-path-lane-mode][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-lane-mode")),
                            statusText: document.querySelector("#demo-reconstruction-proof-path-lane-mode-status")?.textContent?.trim() || "",
                            hiddenLanes: Array.from(document.querySelectorAll("[data-proof-path-lane]"))
                                .filter((element) => element.hidden).length,
                            visibleBlueprint: visible("#demo-reconstruction-proof-path-blueprint-summary"),
                            visibleOutput: visible("#demo-reconstruction-proof-path-output-map"),
                            visibleSource: visible("#demo-reconstruction-proof-path-source-rail"),
                            visibleMatrix: visible("#demo-reconstruction-proof-path-coverage-grid"),
                            stripLaneText: text("#demo-reconstruction-proof-path-review-lane"),
                            stripStepText: text("#demo-reconstruction-proof-path-review-step"),
                            stripObjectText: text("#demo-reconstruction-proof-path-review-object"),
                            stripLinkStateText: text("#demo-reconstruction-proof-path-review-link-state"),
                        };
                    }"""
                )
                page.locator('[data-proof-path-lane-mode="all"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-lane-mode="all"]');
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && Array.from(document.querySelectorAll("[data-proof-path-lane]"))
                                .every((element) => !element.hidden);
                    }""",
                    timeout=5000,
                )
                proof_path_lane_all_review = page.evaluate(
                    """() => {
                        const visible = (selector) => {
                            const element = document.querySelector(selector);
                            return Boolean(element && !element.hidden);
                        };
                        return {
                            activeModes: Array.from(
                                document.querySelectorAll("[data-proof-path-lane-mode][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-lane-mode")),
                            statusText: document.querySelector("#demo-reconstruction-proof-path-lane-mode-status")?.textContent?.trim() || "",
                            hiddenLanes: Array.from(document.querySelectorAll("[data-proof-path-lane]"))
                                .filter((element) => element.hidden).length,
                            visibleBlueprint: visible("#demo-reconstruction-proof-path-blueprint-summary"),
                            visibleSource: visible("#demo-reconstruction-proof-path-source-rail"),
                            visibleMatrix: visible("#demo-reconstruction-proof-path-coverage-grid"),
                            visibleObject: visible("#demo-reconstruction-proof-path-object-inspector"),
                            stripLaneText: document
                                .querySelector("#demo-reconstruction-proof-path-review-lane")
                                ?.textContent?.trim() || "",
                        };
                    }"""
                )
                page.locator('[data-proof-path-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const button = document.querySelector('[data-proof-path-step="P035-S05"]');
                        const status = document.querySelector("#demo-reconstruction-proof-path-status");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-readback");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object");
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.includes("5/5")
                            && readback
                            && readback.textContent.includes("20/20")
                            && readback.textContent.includes("23/23")
                            && object
                            && object.textContent.includes("wire_logic4_thr_lock")
                            && inspector
                            && inspector.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_object_inspector_final_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            objectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                            sourceCountText: text("#demo-reconstruction-proof-path-object-inspector-source-count"),
                            stepCountText: text("#demo-reconstruction-proof-path-object-inspector-step-count"),
                            edgeCountText: text("#demo-reconstruction-proof-path-object-inspector-edge-count"),
                            coverageText: text("#demo-reconstruction-proof-path-object-inspector-coverage"),
                            summaryText: text("#demo-reconstruction-proof-path-object-inspector-summary"),
                            neighborCount: document.querySelectorAll(
                                "#demo-reconstruction-proof-path-object-inspector-neighbors [data-proof-path-inspector-focus-id]"
                            ).length,
                            neighborText: text("#demo-reconstruction-proof-path-object-inspector-neighbors"),
                        };
                    }"""
                )
                proof_path_final_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-step")),
                            statusText: text("#demo-reconstruction-proof-path-status"),
                            readbackText: text("#demo-reconstruction-proof-path-readback"),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            reviewSyncText: text("#demo-reconstruction-review-sync"),
                        };
                    }"""
                )
                page.locator(
                    '#demo-reconstruction-proof-path-object-inspector-neighbors [data-proof-path-inspector-focus-id="logic4"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-readback");
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object");
                        return object
                            && object.textContent.includes("logic4")
                            && readback
                            && readback.textContent.includes("logic4")
                            && inspector
                            && inspector.textContent.includes("logic4");
                    }""",
                    timeout=5000,
                )
                proof_path_object_inspector_neighbor_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            readbackText: text("#demo-reconstruction-proof-path-readback"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                page.locator('[data-proof-path-row="P035-S01"] [data-proof-path-focus-id="tls_unlocked"]').click()
                page.wait_for_function(
                    """() => {
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const sync = document.querySelector("#demo-reconstruction-review-sync");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-readback");
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object");
                        return selected
                            && selected.textContent.trim() === "P035-S01"
                            && object
                            && object.textContent.includes("tls_unlocked")
                            && sync
                            && sync.textContent.includes("聚焦节点")
                            && readback
                            && readback.textContent.includes("tls_unlocked")
                            && inspector
                            && inspector.textContent.includes("tls_unlocked");
                    }""",
                    timeout=5000,
                )
                proof_path_object_inspector_chip_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            objectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                            sourceCountText: text("#demo-reconstruction-proof-path-object-inspector-source-count"),
                            stepCountText: text("#demo-reconstruction-proof-path-object-inspector-step-count"),
                            edgeCountText: text("#demo-reconstruction-proof-path-object-inspector-edge-count"),
                            coverageText: text("#demo-reconstruction-proof-path-object-inspector-coverage"),
                            summaryText: text("#demo-reconstruction-proof-path-object-inspector-summary"),
                            neighborCount: document.querySelectorAll(
                                "#demo-reconstruction-proof-path-object-inspector-neighbors [data-proof-path-inspector-focus-id]"
                            ).length,
                            neighborText: text("#demo-reconstruction-proof-path-object-inspector-neighbors"),
                        };
                    }"""
                )
                proof_path_chip_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            reviewSyncText: text("#demo-reconstruction-review-sync"),
                            readbackText: text("#demo-reconstruction-proof-path-readback"),
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-step")),
                        };
                    }"""
                )
                proof_path_coverage_grid_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-coverage-step]").length,
                            focusChipCount: document.querySelectorAll("[data-proof-path-coverage-focus-id]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-coverage-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-coverage-step")),
                            statusText: text("#demo-reconstruction-proof-path-coverage-grid-status"),
                            readbackText: text("#demo-reconstruction-proof-path-coverage-grid-readback"),
                            firstText: text('[data-proof-path-coverage-step="P035-S01"]'),
                            finalText: text('[data-proof-path-coverage-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-coverage-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const button = document.querySelector('[data-proof-path-coverage-step="P035-S05"]');
                        const readback = document.querySelector("#demo-reconstruction-proof-path-coverage-grid-readback")?.textContent || "";
                        const object = document.querySelector("#demo-reconstruction-review-object")?.textContent || "";
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && readback.includes("20/20")
                            && readback.includes("23/23")
                            && readback.includes("THR_LOCK")
                            && object.includes("累计构建")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length === 20
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 23;
                    }""",
                    timeout=5000,
                )
                proof_path_coverage_grid_final_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-coverage-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-coverage-step")),
                            readbackText: text("#demo-reconstruction-proof-path-coverage-grid-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
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
                    '[data-proof-path-coverage-row="P035-S05"] [data-proof-path-coverage-focus-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-coverage-grid-readback");
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object");
                        return object
                            && object.textContent.includes("wire_logic4_thr_lock")
                            && readback
                            && readback.textContent.includes("wire_logic4_thr_lock")
                            && inspector
                            && inspector.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_coverage_grid_focus_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-coverage-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-coverage-step")),
                            activeFocusIds: Array.from(
                                document.querySelectorAll("[data-proof-path-coverage-focus-id][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-coverage-focus-id")),
                            readbackText: text("#demo-reconstruction-proof-path-coverage-grid-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                page.locator('[data-trace-card][data-trace-anchor="P035-S02"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-coverage-step="P035-S02"]');
                        const readback = document.querySelector("#demo-reconstruction-proof-path-coverage-grid-readback")?.textContent || "";
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && readback.includes("P035-S02")
                            && readback.includes("12/20")
                            && readback.includes("11/23")
                            && !readback.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_coverage_grid_trace_switch_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-coverage-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-coverage-step")),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            readbackText: text("#demo-reconstruction-proof-path-coverage-grid-readback"),
                        };
                    }"""
                )
                proof_path_delta_rail_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-delta-step]").length,
                            focusChipCount: document.querySelectorAll("[data-proof-path-delta-focus-id]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-delta-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-delta-step")),
                            statusText: text("#demo-reconstruction-proof-path-delta-rail-status"),
                            readbackText: text("#demo-reconstruction-proof-path-delta-rail-readback"),
                            firstText: text('[data-proof-path-delta-step="P035-S01"]'),
                            finalText: text('[data-proof-path-delta-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-delta-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const button = document.querySelector('[data-proof-path-delta-step="P035-S05"]');
                        const readback = document.querySelector("#demo-reconstruction-proof-path-delta-rail-readback")?.textContent || "";
                        const object = document.querySelector("#demo-reconstruction-review-object")?.textContent || "";
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && readback.includes("18->20/20")
                            && readback.includes("20->23/23")
                            && readback.includes("+2 节点")
                            && readback.includes("+3 连线")
                            && object.includes("累计构建")
                            && doc
                            && doc.querySelectorAll("#fan-chain-svg [data-docx-trace-selected='true'][data-node]").length === 20
                            && doc.querySelectorAll("#fan-chain-svg .chain-wire[data-docx-trace-selected='true']").length === 23;
                    }""",
                    timeout=5000,
                )
                proof_path_delta_rail_final_review = page.evaluate(
                    """() => {
                        const frame = document.querySelector("#demo-reconstruction-console-frame");
                        const doc = frame && frame.contentDocument;
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-delta-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-delta-step")),
                            readbackText: text("#demo-reconstruction-proof-path-delta-rail-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
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
                    '[data-proof-path-delta-row="P035-S05"] [data-proof-path-delta-focus-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-delta-rail-readback");
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object");
                        return object
                            && object.textContent.includes("wire_logic4_thr_lock")
                            && readback
                            && readback.textContent.includes("wire_logic4_thr_lock")
                            && inspector
                            && inspector.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_delta_rail_focus_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-delta-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-delta-step")),
                            activeFocusIds: Array.from(
                                document.querySelectorAll("[data-proof-path-delta-focus-id][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-delta-focus-id")),
                            readbackText: text("#demo-reconstruction-proof-path-delta-rail-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                proof_path_source_rail_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-source-step]").length,
                            anchorChipCount: document.querySelectorAll("[data-proof-path-source-anchor]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-source-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-source-step")),
                            statusText: text("#demo-reconstruction-proof-path-source-rail-status"),
                            readbackText: text("#demo-reconstruction-proof-path-source-rail-readback"),
                            firstText: text('[data-proof-path-source-step="P035-S01"]'),
                            finalText: text('[data-proof-path-source-step="P035-S05"]'),
                            finalAnchors: Array.from(
                                document.querySelectorAll('[data-proof-path-source-row="P035-S05"] [data-proof-path-source-anchor]')
                            ).map((button) => button.getAttribute("data-proof-path-source-anchor")),
                        };
                    }"""
                )
                page.locator('[data-proof-path-source-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-source-step="P035-S05"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        const readback = document.querySelector("#demo-reconstruction-proof-path-source-rail-readback")?.textContent || "";
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && readback.includes("P035-S05")
                            && readback.includes("源句命中");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-proof-path-source-row="P035-S05"] [data-proof-path-source-anchor="P035"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const readback = document.querySelector("#demo-reconstruction-proof-path-source-rail-readback")?.textContent || "";
                        return readback.includes("P035-S05")
                            && readback.includes("P035")
                            && readback.includes("油门台反推电子锁");
                    }""",
                    timeout=5000,
                )
                proof_path_source_rail_anchor_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-source-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-source-step")),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            readbackText: text("#demo-reconstruction-proof-path-source-rail-readback"),
                        };
                    }"""
                )
                proof_path_sentence_matrix_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-sentence-step]").length,
                            objectChipCount: document.querySelectorAll("[data-proof-path-sentence-focus-id]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-sentence-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-sentence-step")),
                            statusText: text("#demo-reconstruction-proof-path-sentence-matrix-status"),
                            readbackText: text("#demo-reconstruction-proof-path-sentence-matrix-readback"),
                            firstText: text('[data-proof-path-sentence-row="P035-S01"]'),
                            finalText: text('[data-proof-path-sentence-row="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-sentence-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-sentence-step="P035-S05"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        const readback = document.querySelector("#demo-reconstruction-proof-path-sentence-matrix-readback")?.textContent || "";
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && readback.includes("P035-S05")
                            && readback.includes("20/20 节点")
                            && readback.includes("23/23 连线")
                            && readback.includes("THR_LOCK");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-proof-path-sentence-row="P035-S05"] [data-proof-path-sentence-focus-id="wire_logic4_thr_lock"]'
                ).click()
                page.wait_for_function(
                    """() => {
                        const readback = document.querySelector("#demo-reconstruction-proof-path-sentence-matrix-readback")?.textContent || "";
                        const object = document.querySelector("#demo-reconstruction-review-object")?.textContent || "";
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object")?.textContent || "";
                        return readback.includes("wire_logic4_thr_lock")
                            && object.includes("wire_logic4_thr_lock")
                            && inspector.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_sentence_matrix_focus_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-sentence-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-sentence-step")),
                            activeFocusIds: Array.from(
                                document.querySelectorAll("[data-proof-path-sentence-focus-id][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-sentence-focus-id")),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            readbackText: text("#demo-reconstruction-proof-path-sentence-matrix-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                proof_path_predicate_matrix_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-predicate-step]").length,
                            focusCount: document.querySelectorAll("[data-proof-path-predicate-focus-id]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-predicate-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-predicate-step")),
                            statusText: text("#demo-reconstruction-proof-path-predicate-matrix-status"),
                            readbackText: text("#demo-reconstruction-proof-path-predicate-matrix-readback"),
                            firstText: text('[data-proof-path-predicate-row="P035-S01"]'),
                            finalText: text('[data-proof-path-predicate-row="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-predicate-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-predicate-step="P035-S05"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        const readback = document.querySelector("#demo-reconstruction-proof-path-predicate-matrix-readback")?.textContent || "";
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && readback.includes("LOGIC4")
                            && readback.includes("VDT90 AND L3")
                            && readback.includes("THR_LOCK");
                    }""",
                    timeout=5000,
                )
                page.locator(
                    '[data-proof-path-predicate-row="P035-S05"] [data-proof-path-predicate-focus-id="wire_logic4_thr_lock"]'
                ).nth(0).click()
                page.wait_for_function(
                    """() => {
                        const readback = document.querySelector("#demo-reconstruction-proof-path-predicate-matrix-readback")?.textContent || "";
                        const object = document.querySelector("#demo-reconstruction-review-object")?.textContent || "";
                        const inspector = document.querySelector("#demo-reconstruction-proof-path-object-inspector-object")?.textContent || "";
                        return readback.includes("wire_logic4_thr_lock")
                            && object.includes("wire_logic4_thr_lock")
                            && inspector.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_path_predicate_matrix_focus_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-predicate-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-predicate-step")),
                            activeFocusIds: Array.from(
                                document.querySelectorAll("[data-proof-path-predicate-focus-id][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-predicate-focus-id")),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            readbackText: text("#demo-reconstruction-proof-path-predicate-matrix-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                proof_path_blueprint_summary_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            stepCount: document.querySelectorAll("[data-proof-path-blueprint-step]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-blueprint-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-blueprint-step")),
                            statusText: text("#demo-reconstruction-proof-path-blueprint-summary-status"),
                            readbackText: text("#demo-reconstruction-proof-path-blueprint-summary-readback"),
                            chainText: text("[data-proof-path-blueprint-chain='complete']"),
                            firstText: text('[data-proof-path-blueprint-step="P035-S01"]'),
                            finalText: text('[data-proof-path-blueprint-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-blueprint-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const active = document.querySelector('[data-proof-path-blueprint-step="P035-S05"]');
                        const selected = document.querySelector("#demo-reconstruction-selected-anchor")?.textContent || "";
                        const readback = document.querySelector("#demo-reconstruction-proof-path-blueprint-summary-readback")?.textContent || "";
                        return active
                            && active.getAttribute("aria-pressed") === "true"
                            && selected.includes("P035-S05")
                            && readback.includes("20/20 节点")
                            && readback.includes("23/23 连线")
                            && readback.includes("完整 demo 电路闭合");
                    }""",
                    timeout=5000,
                )
                proof_path_blueprint_summary_final_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-proof-path-blueprint-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-blueprint-step")),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            readbackText: text("#demo-reconstruction-proof-path-blueprint-summary-readback"),
                        };
                    }"""
                )
                proof_path_output_map_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            targetCount: document.querySelectorAll("[data-proof-path-output-target]").length,
                            activeTargets: Array.from(
                                document.querySelectorAll("[data-proof-path-output-target][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-output-target")),
                            statusText: text("#demo-reconstruction-proof-path-output-map-status"),
                            readbackText: text("#demo-reconstruction-proof-path-output-map-readback"),
                            tlsText: text('[data-proof-path-output-target="tls115"]'),
                            thrText: text('[data-proof-path-output-target="thr_lock"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-path-output-target="tls115"]').click()
                page.wait_for_function(
                    """() => {
                        const output = document.querySelector('[data-proof-path-output-target="tls115"]');
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        const readback = document.querySelector("#demo-reconstruction-proof-path-output-map-readback");
                        return output
                            && output.getAttribute("aria-pressed") === "true"
                            && object
                            && object.textContent.includes("wire_logic1_tls115")
                            && readback
                            && readback.textContent.includes("TLS 115VAC");
                    }""",
                    timeout=5000,
                )
                proof_path_output_map_tls_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeTargets: Array.from(
                                document.querySelectorAll("[data-proof-path-output-target][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-proof-path-output-target")),
                            readbackText: text("#demo-reconstruction-proof-path-output-map-readback"),
                            reviewObjectText: text("#demo-reconstruction-review-object"),
                            inspectorObjectText: text("#demo-reconstruction-proof-path-object-inspector-object"),
                        };
                    }"""
                )
                page.locator("#demo-reconstruction-scenario-comparator").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.locator("#demo-reconstruction-scenario-comparator").screenshot(
                    path=str(scenario_comparator_path)
                )
                scenario_comparator_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            buttonCount: document.querySelectorAll("[data-scenario-comparator-action]").length,
                            activeActions: Array.from(
                                document.querySelectorAll("[data-scenario-comparator-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-scenario-comparator-action")),
                            statusText: text("#demo-reconstruction-scenario-comparator-status"),
                            readbackText: text("#demo-reconstruction-scenario-comparator-readback"),
                            maxText: text('[data-scenario-comparator-action="max-reverse"]'),
                            inhibitText: text('[data-scenario-comparator-action="inhibit-block"]'),
                        };
                    }"""
                )
                page.locator('[data-scenario-comparator-action="max-reverse"]').click()
                page.wait_for_function(
                    """() => {
                        const button = document.querySelector('[data-scenario-comparator-action="max-reverse"]');
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const readback = document.querySelector("#demo-reconstruction-scenario-comparator-readback");
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "DEPLOYED"
                            && output
                            && output.textContent.trim() === "ON"
                            && readback
                            && readback.textContent.includes("最大反推");
                    }""",
                    timeout=5000,
                )
                scenario_comparator_max_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeActions: Array.from(
                                document.querySelectorAll("[data-scenario-comparator-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-scenario-comparator-action")),
                            statusText: text("#demo-reconstruction-scenario-comparator-status"),
                            readbackText: text("#demo-reconstruction-scenario-comparator-readback"),
                            maxText: text('[data-scenario-comparator-action="max-reverse"]'),
                            output: text("#demo-reconstruction-output-mirror-thr-output"),
                        };
                    }"""
                )
                page.locator('[data-scenario-comparator-action="inhibit-block"]').click()
                page.wait_for_function(
                    """() => {
                        const button = document.querySelector('[data-scenario-comparator-action="inhibit-block"]');
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const readback = document.querySelector("#demo-reconstruction-scenario-comparator-readback");
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "FAULT"
                            && output
                            && output.textContent.trim() === "BLOCKED"
                            && readback
                            && readback.textContent.includes("抑制阻塞");
                    }""",
                    timeout=5000,
                )
                scenario_comparator_inhibit_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeActions: Array.from(
                                document.querySelectorAll("[data-scenario-comparator-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-scenario-comparator-action")),
                            statusText: text("#demo-reconstruction-scenario-comparator-status"),
                            readbackText: text("#demo-reconstruction-scenario-comparator-readback"),
                            inhibitText: text('[data-scenario-comparator-action="inhibit-block"]'),
                            output: text("#demo-reconstruction-output-mirror-thr-output"),
                        };
                    }"""
                )
                scenario_ledger_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            rowCount: document.querySelectorAll("[data-scenario-ledger-row]").length,
                            statusText: text("#demo-reconstruction-scenario-ledger-status"),
                            truthRowCount: document.querySelectorAll("[data-scenario-truth-row]").length,
                            truthCapturedCount: document.querySelectorAll("[data-scenario-truth-row][data-scenario-truth-captured='true']").length,
                            truthStatusText: text("#demo-reconstruction-scenario-truth-status"),
                            activeRows: Array.from(
                                document.querySelectorAll("[data-scenario-ledger-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-scenario-ledger-row")),
                            truthActiveRows: Array.from(
                                document.querySelectorAll("[data-scenario-truth-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-scenario-truth-row")),
                            maxReverseText: text('[data-scenario-ledger-row="max-reverse"]'),
                            inhibitText: text('[data-scenario-ledger-row="inhibit-block"]'),
                            truthMaxReverseText: text('[data-scenario-truth-row="max-reverse"]'),
                            truthInhibitText: text('[data-scenario-truth-row="inhibit-block"]'),
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
                        truthActiveRows: Array.from(
                            document.querySelectorAll("[data-scenario-truth-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-scenario-truth-row")),
                        maxReverseText: document
                            .querySelector('[data-scenario-ledger-row="max-reverse"]')
                            ?.textContent?.trim() || "",
                        truthMaxReverseText: document
                            .querySelector('[data-scenario-truth-row="max-reverse"]')
                            ?.textContent?.trim() || "",
                    })"""
                )
                control_strip_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            actionCount: document.querySelectorAll("[data-control-strip-action]").length,
                            activeActions: Array.from(
                                document.querySelectorAll("[data-control-strip-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-control-strip-action")),
                            statusText: text("#demo-reconstruction-control-strip-status"),
                            stepText: text("#demo-reconstruction-control-strip-step"),
                            objectText: text("#demo-reconstruction-control-strip-object"),
                            outputText: text("#demo-reconstruction-control-strip-output"),
                            pathText: text("#demo-reconstruction-control-strip-path"),
                        };
                    }"""
                )
                sentence_runner_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            buttonCount: document.querySelectorAll("[data-sentence-runner-step]").length,
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-sentence-runner-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-sentence-runner-step")),
                            statusText: text("#demo-reconstruction-sentence-runner-status"),
                            readbackText: text("#demo-reconstruction-sentence-runner-readback"),
                            firstText: text('[data-sentence-runner-step="P035-S01"]'),
                            finalText: text('[data-sentence-runner-step="P035-S05"]'),
                        };
                    }"""
                )
                page.locator('[data-sentence-runner-step="P035-S03"]').click()
                page.wait_for_function(
                    """() => {
                        const button = document.querySelector('[data-sentence-runner-step="P035-S03"]');
                        const anchor = document.querySelector("#demo-reconstruction-selected-anchor");
                        const status = document.querySelector("#demo-reconstruction-sentence-runner-status");
                        const sync = document.querySelector("#demo-reconstruction-review-sync");
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && anchor
                            && anchor.textContent.includes("P035-S03")
                            && status
                            && status.textContent.includes("3/5")
                            && sync
                            && sync.textContent.includes("17/20");
                    }""",
                    timeout=5000,
                )
                sentence_runner_s03_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-sentence-runner-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-sentence-runner-step")),
                            statusText: text("#demo-reconstruction-sentence-runner-status"),
                            readbackText: text("#demo-reconstruction-sentence-runner-readback"),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            reviewSync: text("#demo-reconstruction-review-sync"),
                        };
                    }"""
                )
                page.locator('[data-sentence-runner-step="P035-S05"]').click()
                page.wait_for_function(
                    """() => {
                        const button = document.querySelector('[data-sentence-runner-step="P035-S05"]');
                        const anchor = document.querySelector("#demo-reconstruction-selected-anchor");
                        const status = document.querySelector("#demo-reconstruction-sentence-runner-status");
                        const sync = document.querySelector("#demo-reconstruction-review-sync");
                        const controlStep = document.querySelector("#demo-reconstruction-control-strip-step");
                        return button
                            && button.getAttribute("aria-pressed") === "true"
                            && anchor
                            && anchor.textContent.includes("P035-S05")
                            && status
                            && status.textContent.includes("5/5")
                            && sync
                            && sync.textContent.includes("20/20")
                            && sync.textContent.includes("23/23")
                            && controlStep
                            && controlStep.textContent.includes("P035-S05");
                    }""",
                    timeout=5000,
                )
                sentence_runner_s05_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeSteps: Array.from(
                                document.querySelectorAll("[data-sentence-runner-step][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-sentence-runner-step")),
                            statusText: text("#demo-reconstruction-sentence-runner-status"),
                            readbackText: text("#demo-reconstruction-sentence-runner-readback"),
                            selectedAnchor: text("#demo-reconstruction-selected-anchor"),
                            reviewSync: text("#demo-reconstruction-review-sync"),
                            controlStep: text("#demo-reconstruction-control-strip-step"),
                        };
                    }"""
                )
                operator_runway_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            rowCount: document.querySelectorAll("[data-operator-runway-row]").length,
                            readyRowCount: document.querySelectorAll("[data-operator-runway-row][data-operator-runway-ready='true']").length,
                            statusText: text("#demo-reconstruction-operator-runway-status"),
                            readbackText: text("#demo-reconstruction-operator-runway-readback"),
                            l4Text: text('[data-operator-runway-row="runway-l4-thr-lock"]'),
                            inhibitText: text('[data-operator-runway-row="runway-inhibit"]'),
                        };
                    }"""
                )
                page.locator('[data-operator-runway-row="runway-l4-thr-lock"]').click()
                page.wait_for_function(
                    """() => {
                        const row = document.querySelector('[data-operator-runway-row="runway-l4-thr-lock"]');
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const step = document.querySelector("#demo-reconstruction-review-anchor");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "DEPLOYED"
                            && output
                            && output.textContent.trim() === "ON"
                            && step
                            && step.textContent.includes("P035-S05")
                            && object
                            && object.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                operator_runway_l4_review = page.evaluate(
                    """() => ({
                        activeRows: Array.from(
                            document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-operator-runway-row")),
                        statusText: document.querySelector("#demo-reconstruction-operator-runway-status")?.textContent?.trim() || "",
                        readbackText: document.querySelector("#demo-reconstruction-operator-runway-readback")?.textContent?.trim() || "",
                        stepText: document.querySelector("#demo-reconstruction-review-anchor")?.textContent?.trim() || "",
                        objectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        output: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                    })"""
                )
                page.locator('[data-operator-runway-row="runway-inhibit"]').click()
                page.wait_for_function(
                    """() => {
                        const row = document.querySelector('[data-operator-runway-row="runway-inhibit"]');
                        const status = document.querySelector("#demo-reconstruction-output-mirror-status");
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const step = document.querySelector("#demo-reconstruction-review-anchor");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && status
                            && status.textContent.trim() === "FAULT"
                            && output
                            && output.textContent.trim() === "BLOCKED"
                            && step
                            && step.textContent.includes("P035-S01")
                            && object
                            && object.textContent.includes("reverser_inhibited");
                    }""",
                    timeout=5000,
                )
                operator_runway_inhibit_review = page.evaluate(
                    """() => ({
                        activeRows: Array.from(
                            document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-operator-runway-row")),
                        statusText: document.querySelector("#demo-reconstruction-operator-runway-status")?.textContent?.trim() || "",
                        readbackText: document.querySelector("#demo-reconstruction-operator-runway-readback")?.textContent?.trim() || "",
                        stepText: document.querySelector("#demo-reconstruction-review-anchor")?.textContent?.trim() || "",
                        objectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        output: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                    })"""
                )
                proof_transcript_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            rowCount: document.querySelectorAll("[data-proof-transcript-row]").length,
                            readyRowCount: document.querySelectorAll("[data-proof-transcript-row][data-proof-transcript-ready='true']").length,
                            summaryText: text("#demo-reconstruction-proof-transcript-summary"),
                            l4Text: text('[data-proof-transcript-row="runway-l4-thr-lock"]'),
                            inhibitText: text('[data-proof-transcript-row="runway-inhibit"]'),
                        };
                    }"""
                )
                page.locator('[data-proof-transcript-row="runway-l4-thr-lock"]').click()
                page.wait_for_function(
                    """() => {
                        const row = document.querySelector('[data-proof-transcript-row="runway-l4-thr-lock"]');
                        const runway = document.querySelector('[data-operator-runway-row="runway-l4-thr-lock"]');
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && runway
                            && runway.getAttribute("aria-pressed") === "true"
                            && output
                            && output.textContent.trim() === "ON"
                            && object
                            && object.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                proof_transcript_l4_review = page.evaluate(
                    """() => ({
                        activeRows: Array.from(
                            document.querySelectorAll("[data-proof-transcript-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-proof-transcript-row")),
                        runwayActiveRows: Array.from(
                            document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-operator-runway-row")),
                        objectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        output: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                    })"""
                )
                page.locator('[data-proof-transcript-row="runway-inhibit"]').click()
                page.wait_for_function(
                    """() => {
                        const row = document.querySelector('[data-proof-transcript-row="runway-inhibit"]');
                        const runway = document.querySelector('[data-operator-runway-row="runway-inhibit"]');
                        const output = document.querySelector("#demo-reconstruction-output-mirror-thr-output");
                        const object = document.querySelector("#demo-reconstruction-review-object");
                        return row
                            && row.getAttribute("aria-pressed") === "true"
                            && runway
                            && runway.getAttribute("aria-pressed") === "true"
                            && output
                            && output.textContent.trim() === "BLOCKED"
                            && object
                            && object.textContent.includes("reverser_inhibited");
                    }""",
                    timeout=5000,
                )
                proof_transcript_inhibit_review = page.evaluate(
                    """() => ({
                        activeRows: Array.from(
                            document.querySelectorAll("[data-proof-transcript-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-proof-transcript-row")),
                        runwayActiveRows: Array.from(
                            document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                        ).map((row) => row.getAttribute("data-operator-runway-row")),
                        objectText: document.querySelector("#demo-reconstruction-review-object")?.textContent?.trim() || "",
                        output: document.querySelector("#demo-reconstruction-output-mirror-thr-output")?.textContent?.trim() || "",
                    })"""
                )
                page.locator('[data-control-strip-action="prove-thr"]').click()
                page.wait_for_function(
                    """() => {
                        const action = document.querySelector('[data-control-strip-action="prove-thr"]');
                        const runway = document.querySelector('[data-operator-runway-row="runway-l4-thr-lock"]');
                        const transcript = document.querySelector('[data-proof-transcript-row="runway-l4-thr-lock"]');
                        const output = document.querySelector("#demo-reconstruction-control-strip-output");
                        const object = document.querySelector("#demo-reconstruction-control-strip-object");
                        return action
                            && action.getAttribute("aria-pressed") === "true"
                            && runway
                            && runway.getAttribute("aria-pressed") === "true"
                            && transcript
                            && transcript.getAttribute("aria-pressed") === "true"
                            && output
                            && output.textContent.includes("THR ON")
                            && object
                            && object.textContent.includes("wire_logic4_thr_lock");
                    }""",
                    timeout=5000,
                )
                control_strip_l4_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeActions: Array.from(
                                document.querySelectorAll("[data-control-strip-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-control-strip-action")),
                            statusText: text("#demo-reconstruction-control-strip-status"),
                            stepText: text("#demo-reconstruction-control-strip-step"),
                            objectText: text("#demo-reconstruction-control-strip-object"),
                            outputText: text("#demo-reconstruction-control-strip-output"),
                            pathText: text("#demo-reconstruction-control-strip-path"),
                            runwayActiveRows: Array.from(
                                document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-operator-runway-row")),
                            transcriptActiveRows: Array.from(
                                document.querySelectorAll("[data-proof-transcript-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-proof-transcript-row")),
                        };
                    }"""
                )
                page.wait_for_function(
                    """() => {
                        const status = document.querySelector("#demo-reconstruction-review-verdict-status");
                        const focus = document.querySelector("#demo-reconstruction-review-verdict-focus");
                        const readback = document.querySelector("#demo-reconstruction-review-verdict-readback");
                        return status
                            && status.textContent.includes("5/5")
                            && focus
                            && focus.textContent.includes("wire_logic4_thr_lock")
                            && readback
                            && readback.textContent.includes("证据可审");
                    }""",
                    timeout=5000,
                )
                page.locator("#demo-reconstruction-review-verdict").evaluate(
                    """(element) => element.scrollIntoView({block: "center", inline: "nearest"})"""
                )
                page.locator("#demo-reconstruction-review-verdict").screenshot(
                    path=str(review_verdict_path)
                )
                review_verdict_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            cardCount: document.querySelectorAll("[data-review-verdict-card]").length,
                            statusText: text("#demo-reconstruction-review-verdict-status"),
                            sourceText: text("#demo-reconstruction-review-verdict-source"),
                            circuitText: text("#demo-reconstruction-review-verdict-circuit"),
                            outputsText: text("#demo-reconstruction-review-verdict-outputs"),
                            focusText: text("#demo-reconstruction-review-verdict-focus"),
                            boundaryText: text("#demo-reconstruction-review-verdict-boundary"),
                            readbackText: text("#demo-reconstruction-review-verdict-readback"),
                        };
                    }"""
                )
                page.locator('[data-control-strip-action="block-inhibit"]').click()
                page.wait_for_function(
                    """() => {
                        const action = document.querySelector('[data-control-strip-action="block-inhibit"]');
                        const runway = document.querySelector('[data-operator-runway-row="runway-inhibit"]');
                        const transcript = document.querySelector('[data-proof-transcript-row="runway-inhibit"]');
                        const output = document.querySelector("#demo-reconstruction-control-strip-output");
                        const object = document.querySelector("#demo-reconstruction-control-strip-object");
                        return action
                            && action.getAttribute("aria-pressed") === "true"
                            && runway
                            && runway.getAttribute("aria-pressed") === "true"
                            && transcript
                            && transcript.getAttribute("aria-pressed") === "true"
                            && output
                            && output.textContent.includes("THR BLOCKED")
                            && object
                            && object.textContent.includes("reverser_inhibited");
                    }""",
                    timeout=5000,
                )
                control_strip_inhibit_review = page.evaluate(
                    """() => {
                        const text = (selector) => document.querySelector(selector)?.textContent?.trim() || "";
                        return {
                            activeActions: Array.from(
                                document.querySelectorAll("[data-control-strip-action][aria-pressed='true']")
                            ).map((button) => button.getAttribute("data-control-strip-action")),
                            statusText: text("#demo-reconstruction-control-strip-status"),
                            stepText: text("#demo-reconstruction-control-strip-step"),
                            objectText: text("#demo-reconstruction-control-strip-object"),
                            outputText: text("#demo-reconstruction-control-strip-output"),
                            pathText: text("#demo-reconstruction-control-strip-path"),
                            runwayActiveRows: Array.from(
                                document.querySelectorAll("[data-operator-runway-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-operator-runway-row")),
                            transcriptActiveRows: Array.from(
                                document.querySelectorAll("[data-proof-transcript-row][aria-pressed='true']")
                            ).map((row) => row.getAttribute("data-proof-transcript-row")),
                        };
                    }"""
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
                assembly_map_path,
                logic_equation_path,
                topology_matrix_path,
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
                scenario_truth_path,
                operator_runway_path,
                proof_transcript_path,
                control_strip_path,
                sentence_runner_path,
                proof_path_path,
                scenario_comparator_path,
                review_verdict_path,
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
            and source_map_review["reviewIndexButtonCount"] == 12
            and source_map_review["sequenceStepCount"] == 5
            and source_map_review["traceCardCount"] == 5
            and source_map_review["playbackStepCount"] == 5
            and source_map_review["assemblyStepCount"] == 5
            and source_map_review["topologyRowCount"] == 23
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
        "requirement_coverage_ledger": "pass"
        if (
            source_map_review["requirementLedgerRowCount"] == 67
            and source_map_review["requirementLedgerMappedCount"] == 44
            and source_map_review["requirementLedgerContextCount"] == 18
            and source_map_review["requirementLedgerP035Count"] == 5
            and "67 条" in source_map_review["requirementLedgerSummary"]
            and "44 已映射" in source_map_review["requirementLedgerSummary"]
            and source_map_review["requirementLedgerStatus"] == "67/67 条"
            and requirement_ledger_context_review["selectedFilters"] == ["context"]
            and requirement_ledger_context_review["visibleRows"] == 18
            and "18/67" in requirement_ledger_context_review["statusText"]
            and requirement_ledger_action_review["query"] == "logic4"
            and requirement_ledger_action_review["visibleRows"] >= 3
            and requirement_ledger_action_review["selectedRows"] == ["step:P035-S05"]
            and requirement_ledger_action_review["selectedAnchor"] == "P035-S05"
            and requirement_ledger_action_review["highlightedCount"] >= 4
        )
        else "fail",
        "review_index_navigation": "pass"
        if (
            review_index_review["visible"]
            and review_index_review["buttonCount"] == 12
            and review_index_review["activeTargets"] == ["demo-reconstruction-docx-circuit-map"]
            and "P035-S01" in review_index_review["stepText"]
            and "蓝图" in review_index_review["proofPathText"]
            and review_index_navigation["activeTargets"] == ["demo-reconstruction-scenario-ledger"]
            and review_index_navigation["scrollY"] > 0
            and review_index_proof_path_navigation["activeTargets"] == ["demo-reconstruction-proof-path"]
            and review_index_proof_path_navigation["scrollY"] > 0
            and "P035-S05" in review_index_after_trace["stepText"]
            and "等待聚焦" in review_index_after_trace["objectText"]
            and "链接已同步" in review_index_after_trace["proofPathText"]
        )
        else "fail",
        "review_index_proof_path_context": "pass"
        if (
            "蓝图" in review_index_review["proofPathText"]
            and review_index_proof_path_navigation["activeTargets"] == ["demo-reconstruction-proof-path"]
            and "P035-S05" in review_index_after_trace["stepText"]
            and "链接已同步" in review_index_after_trace["proofPathText"]
        )
        else "fail",
        "logic_equation_board_readback": "pass"
        if (
            logic_equation_review["visible"]
            and logic_equation_review["rowCount"] == 4
            and logic_equation_review["passCount"] == 4
            and "4/4 方程" in logic_equation_review["summaryText"]
            and "20/20 节点" in logic_equation_review["summaryText"]
            and "23/23 连线" in logic_equation_review["summaryText"]
            and "RA < 6 ft" in logic_equation_review["l1Text"]
            and "TLS115" in logic_equation_review["l1Text"]
            and "VDT90" in logic_equation_review["l4Text"]
            and "THR_LOCK release" in logic_equation_review["l4Text"]
            and logic_equation_focus_review["activeRows"] == ["logic4"]
            and logic_equation_focus_review["selectedAnchor"] == "P035-S05"
            and "wire_logic4_thr_lock" in logic_equation_focus_review["reviewObjectText"]
            and logic_equation_focus_review["highlightedWireCount"] == 1
        )
        else "fail",
        "assembly_map_readback": "pass"
        if (
            assembly_map_review["visible"]
            and assembly_map_review["itemCount"] == 5
            and assembly_map_review["actionCount"] == 5
            and assembly_map_review["focusChipCount"] >= 43
            and assembly_map_review["completeCount"] == 1
            and "5/5" in assembly_map_review["summaryText"]
            and "20/20" in assembly_map_review["summaryText"]
            and "23/23" in assembly_map_review["summaryText"]
            and "THR_LOCK" in assembly_map_review["finalText"]
            and "完整 demo 电路闭合" in assembly_map_review["s05Text"]
            and "TLS 解锁" in assembly_map_review["s01Text"]
            and assembly_map_action_review["activeStep"] == "P035-S05"
            and assembly_map_action_review["activeButtonCount"] == 1
            and assembly_map_action_review["highlightedNodeCount"] == 20
            and assembly_map_action_review["highlightedWireCount"] == 23
            and "累计构建" in assembly_map_action_review["reviewObjectText"]
        )
        else "fail",
        "topology_matrix_readback": "pass"
        if (
            topology_matrix_review["visible"]
            and topology_matrix_review["rowCount"] == 23
            and topology_matrix_review["buttonCount"] == 23
            and "23/23" in topology_matrix_review["summaryText"]
            and "23/23" in topology_matrix_review["readbackText"]
            and "wire_ra_logic1" in topology_matrix_review["firstText"]
            and "wire_logic4_thr_lock" in topology_matrix_review["s05Text"]
            and "P035-S05" in topology_matrix_review["s05Text"]
            and topology_focus_review["activeRows"] == ["wire_logic4_thr_lock"]
            and topology_focus_review["highlightedWireCount"] == 1
            and "P035-S05" in topology_focus_review["readbackText"]
            and "wire_logic4_thr_lock" in topology_focus_review["reviewObjectText"]
        )
        else "fail",
        "topology_filter_workbench": "pass"
        if (
            topology_filter_review["query"] == "THR_LOCK"
            and "step=P035-S05" in topology_filter_review["hash"]
            and "topology=P035-S05" in topology_filter_review["hash"]
            and "tq=THR_LOCK" in topology_filter_review["hash"]
            and "focus=" not in topology_filter_review["hash"]
            and topology_filter_review["selectedFilters"] == ["P035-S05"]
            and topology_filter_review["visibleRows"] == ["wire_logic4_thr_lock"]
            and topology_filter_review["selectedAnchor"] == "P035-S05"
            and "1/23" in topology_filter_review["statusText"]
            and "P035-S05" in topology_filter_review["statusText"]
            and topology_filter_restore_review["query"] == "THR_LOCK"
            and topology_filter_restore_review["hash"] == topology_filter_review["hash"]
            and topology_filter_restore_review["selectedFilters"] == ["P035-S05"]
            and topology_filter_restore_review["visibleRows"] == ["wire_logic4_thr_lock"]
            and topology_filter_restore_review["selectedAnchor"] == "P035-S05"
            and "1/23" in topology_filter_restore_review["statusText"]
        )
        else "fail",
        "output_path_lane_readback": "pass"
        if (
            output_path_review["visible"]
            and output_path_review["targetCount"] == 5
            and output_path_review["selectedTargets"] == ["thr_lock"]
            and output_path_review["rowCount"] == 15
            and output_path_review["pathOrder"][-1] == "wire_logic4_thr_lock"
            and (
                output_path_review["pathOrder"].index("wire_pdu_vdt90")
                < output_path_review["pathOrder"].index("wire_vdt90_logic4")
            )
            and (
                output_path_review["pathOrder"].index("wire_vdt90_logic4")
                < output_path_review["pathOrder"].index("wire_logic4_thr_lock")
            )
            and "THR_LOCK" in output_path_review["summaryText"]
            and "15/23" in output_path_review["summaryText"]
            and "wire_logic4_thr_lock" in output_path_review["finalText"]
            and output_path_focus_review["activeRows"] == ["wire_logic4_thr_lock"]
            and output_path_focus_review["highlightedWireCount"] == 1
            and "wire_logic4_thr_lock" in output_path_focus_review["reviewObjectText"]
            and "P035-S05" in output_path_focus_review["topologyReadbackText"]
            and stored_output_path_review["rowCount"] == 15
            and "15/23" in stored_output_path_review["summaryText"]
            and "P035-S05" in stored_output_path_review["finalText"]
            and "DOCX" in stored_output_path_review["finalText"]
        )
        else "fail",
        "output_maturity_matrix_readback": "pass"
        if (
            output_maturity_review["visible"]
            and output_maturity_review["stepCount"] == 5
            and output_maturity_review["cellCount"] == 25
            and output_maturity_review["activeCellCount"] >= 9
            and "最终 5/5" in output_maturity_review["summaryText"]
            and output_maturity_review["s01TlsActive"] == "true"
            and output_maturity_review["s02EtracActive"] == "true"
            and output_maturity_review["s03EecActive"] == "true"
            and output_maturity_review["s03PduActive"] == "true"
            and output_maturity_review["s05ThrActive"] == "true"
            and output_maturity_focus_review["selectedCells"] == ["P035-S05:thr_lock"]
            and output_maturity_focus_review["selectedOutputTarget"] == ["thr_lock"]
            and output_maturity_focus_review["highlightedNodeCount"] == 1
            and "thr_lock" in output_maturity_focus_review["reviewObjectText"]
            and output_maturity_restore_review["selectedCells"] == ["P035-S05:thr_lock"]
            and "step=P035-S05" in output_maturity_restore_review["hash"]
            and "focus=node%3Athr_lock" in output_maturity_restore_review["hash"]
            and output_maturity_restore_review["highlightedNodeCount"] == 1
            and "thr_lock" in output_maturity_restore_review["reviewObjectText"]
            and output_maturity_clear_review["selectedCells"] == []
            and output_maturity_clear_review["activeRows"] == ["wire_logic4_thr_lock"]
            and "wire_logic4_thr_lock" in output_maturity_clear_review["reviewObjectText"]
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
            and review_packet_review["dashboardVisible"]
            and review_packet_review["dashboardMetricCount"] == 5
            and review_packet_review["dashboardPassMetricCount"] >= 4
            and review_packet_review["dashboardChecklistCount"] == 5
            and review_packet_review["dashboardPassChecklistCount"] >= 4
            and "67 覆盖项" in review_packet_review["dashboardSummary"]
            and "5/5 输出" in review_packet_review["dashboardSummary"]
            and review_packet_review["gateCount"] == 5
            and review_packet_review["passGateCount"] >= 4
            and review_packet_after_wire_focus["passGateCount"] == 5
            and review_packet_after_wire_focus["dashboardPassMetricCount"] == 5
            and review_packet_after_wire_focus["dashboardPassChecklistCount"] == 5
            and "5/5 gate" in review_packet_after_wire_focus["dashboardSummary"]
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
            "step=P035-S05" in review_deep_link["hash"]
            and "focus=wire%3Awire_logic4_thr_lock" in review_deep_link["hash"]
            and "q=logic4" in review_deep_link["hash"]
            and "lane=matrix" in review_deep_link["hash"]
            and "/demo-reconstruction#" in review_deep_link["linkHref"]
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
        "review_hash_lane_restore": "pass"
        if (
            review_deep_link["restoredLaneStatus"] == "矩阵"
            and review_deep_link["restoredLaneActiveModes"] == ["matrix"]
            and review_deep_link["restoredLaneVisibleMatrix"]
            and not review_deep_link["restoredLaneVisibleSource"]
        )
        else "fail",
        "proof_path_review_strip": "pass"
        if (
            first_screen_review["proof_path_review_strip_visible"]
            and proof_path_lane_default_review["stripLaneText"] == "蓝图"
            and proof_path_lane_default_review["stripStepText"].startswith("P035-")
            and proof_path_lane_default_review["stripLinkStateText"] in {"默认视图", "链接已同步"}
            and proof_path_lane_all_review["stripLaneText"] == "全部"
            and review_deep_link["restoredStripLane"] == "矩阵"
            and review_deep_link["restoredStripStep"] == "P035-S05"
            and "wire_logic4_thr_lock" in review_deep_link["restoredStripObject"]
            and review_deep_link["restoredStripLinkState"] == "链接已同步"
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
            and scenario_ledger_review["truthRowCount"] == 5
            and scenario_ledger_review["truthCapturedCount"] == 2
            and "2/5" in scenario_ledger_review["truthStatusText"]
            and scenario_ledger_review["activeRows"] == ["inhibit-block"]
            and scenario_ledger_review["truthActiveRows"] == ["inhibit-block"]
            and "DEPLOYED" in scenario_ledger_review["maxReverseText"]
            and "THR:ON" in scenario_ledger_review["maxReverseText"]
            and "FAULT" in scenario_ledger_review["inhibitText"]
            and "THR:BLOCKED" in scenario_ledger_review["inhibitText"]
            and "L4:ON" in scenario_ledger_review["truthMaxReverseText"]
            and "THR:ON" in scenario_ledger_review["truthMaxReverseText"]
            and "FAULT" in scenario_ledger_review["truthInhibitText"]
            and "THR:BLOCKED" in scenario_ledger_review["truthInhibitText"]
            and scenario_ledger_outer_control["status"] == "DEPLOYED"
            and scenario_ledger_outer_control["output"] == "ON"
            and scenario_ledger_outer_control["activeRows"] == ["max-reverse"]
            and scenario_ledger_outer_control["truthActiveRows"] == ["max-reverse"]
            and "DEPLOYED" in scenario_ledger_outer_control["maxReverseText"]
            and "L4:ON" in scenario_ledger_outer_control["truthMaxReverseText"]
            and "THR:ON" in scenario_ledger_outer_control["truthMaxReverseText"]
        )
        else "fail",
        "operator_runway_readback": "pass"
        if (
            operator_runway_review["rowCount"] == 6
            and operator_runway_review["readyRowCount"] == 6
            and "6/6" in operator_runway_review["statusText"]
            and "THR_LOCK" in operator_runway_review["l4Text"]
            and "BLOCKED" in operator_runway_review["inhibitText"]
            and operator_runway_l4_review["activeRows"] == ["runway-l4-thr-lock"]
            and "05/06" in operator_runway_l4_review["statusText"]
            and "P035-S05" in operator_runway_l4_review["stepText"]
            and "wire_logic4_thr_lock" in operator_runway_l4_review["objectText"]
            and operator_runway_l4_review["output"] == "ON"
            and "DEPLOYED" in operator_runway_l4_review["readbackText"]
            and operator_runway_inhibit_review["activeRows"] == ["runway-inhibit"]
            and "06/06" in operator_runway_inhibit_review["statusText"]
            and "P035-S01" in operator_runway_inhibit_review["stepText"]
            and "reverser_inhibited" in operator_runway_inhibit_review["objectText"]
            and operator_runway_inhibit_review["output"] == "BLOCKED"
            and "FAULT" in operator_runway_inhibit_review["readbackText"]
        )
        else "fail",
        "proof_transcript_readback": "pass"
        if (
            proof_transcript_review["rowCount"] == 6
            and proof_transcript_review["readyRowCount"] == 6
            and "6/6" in proof_transcript_review["summaryText"]
            and "THR_LOCK" in proof_transcript_review["l4Text"]
            and "抑制" in proof_transcript_review["inhibitText"]
            and "反推锁不释放" in proof_transcript_review["inhibitText"]
            and "RA/SW1/TLS" not in proof_transcript_review["inhibitText"]
            and proof_transcript_l4_review["activeRows"] == ["runway-l4-thr-lock"]
            and proof_transcript_l4_review["runwayActiveRows"] == ["runway-l4-thr-lock"]
            and "wire_logic4_thr_lock" in proof_transcript_l4_review["objectText"]
            and proof_transcript_l4_review["output"] == "ON"
            and proof_transcript_inhibit_review["activeRows"] == ["runway-inhibit"]
            and proof_transcript_inhibit_review["runwayActiveRows"] == ["runway-inhibit"]
            and "reverser_inhibited" in proof_transcript_inhibit_review["objectText"]
            and proof_transcript_inhibit_review["output"] == "BLOCKED"
        )
        else "fail",
        "control_strip_readback": "pass"
        if (
            control_strip_review["actionCount"] == 3
            and "THR" in control_strip_review["outputText"]
            and control_strip_l4_review["activeActions"] == ["prove-thr"]
            and "05/06" in control_strip_l4_review["statusText"]
            and "P035-S05" in control_strip_l4_review["stepText"]
            and "wire_logic4_thr_lock" in control_strip_l4_review["objectText"]
            and "THR ON" in control_strip_l4_review["outputText"]
            and "THR_LOCK" in control_strip_l4_review["pathText"]
            and control_strip_l4_review["runwayActiveRows"] == ["runway-l4-thr-lock"]
            and control_strip_l4_review["transcriptActiveRows"] == ["runway-l4-thr-lock"]
            and control_strip_inhibit_review["activeActions"] == ["block-inhibit"]
            and "06/06" in control_strip_inhibit_review["statusText"]
            and "P035-S01" in control_strip_inhibit_review["stepText"]
            and "reverser_inhibited" in control_strip_inhibit_review["objectText"]
            and "THR BLOCKED" in control_strip_inhibit_review["outputText"]
            and "BLOCKED" in control_strip_inhibit_review["pathText"]
            and control_strip_inhibit_review["runwayActiveRows"] == ["runway-inhibit"]
            and control_strip_inhibit_review["transcriptActiveRows"] == ["runway-inhibit"]
        )
        else "fail",
        "sentence_runner_readback": "pass"
        if (
            sentence_runner_review["buttonCount"] == 5
            and "P035-S01" in sentence_runner_review["firstText"]
            and "20/20 节点" in sentence_runner_review["finalText"]
            and "23/23 连线" in sentence_runner_review["finalText"]
            and sentence_runner_s03_review["activeSteps"] == ["P035-S03"]
            and "3/5" in sentence_runner_s03_review["statusText"]
            and "P035-S03" in sentence_runner_s03_review["selectedAnchor"]
            and "17/20" in sentence_runner_s03_review["reviewSync"]
            and sentence_runner_s05_review["activeSteps"] == ["P035-S05"]
            and "5/5" in sentence_runner_s05_review["statusText"]
            and "完整电路闭合" in sentence_runner_s05_review["statusText"]
            and "20/20 节点" in sentence_runner_s05_review["readbackText"]
            and "23/23 连线" in sentence_runner_s05_review["readbackText"]
            and "P035-S05" in sentence_runner_s05_review["selectedAnchor"]
            and "P035-S05" in sentence_runner_s05_review["controlStep"]
        )
        else "fail",
        "proof_path_timeline": "pass"
        if (
            proof_path_review["stepCount"] == 5
            and proof_path_review["finalCount"] == 1
            and proof_path_review["focusChipCount"] >= 10
            and "tls_unlocked" in proof_path_review["firstFocusIds"]
            and "wire_logic4_thr_lock" in proof_path_review["finalFocusIds"]
            and "P035-S01" in proof_path_review["firstText"]
            and "飞机离地小于6ft" in proof_path_review["firstText"]
            and "本句 6 节点 / 5 连线" in proof_path_review["firstText"]
            and "P035-S05" in proof_path_review["finalText"]
            and "反推电子锁解锁" in proof_path_review["finalText"]
            and "本句 4 节点 / 3 连线" in proof_path_review["finalText"]
            and "20/20 节点" in proof_path_review["finalText"]
            and "23/23 连线" in proof_path_review["finalText"]
            and proof_path_final_review["activeSteps"] == ["P035-S05"]
            and "5/5" in proof_path_final_review["statusText"]
            and "20/20 节点" in proof_path_final_review["readbackText"]
            and "23/23 连线" in proof_path_final_review["readbackText"]
            and proof_path_final_review["selectedAnchor"] == "P035-S05"
            and "wire_logic4_thr_lock" in proof_path_final_review["reviewObjectText"]
            and "聚焦连线" in proof_path_final_review["reviewSyncText"]
            and "wire_logic4_thr_lock" in proof_path_object_inspector_final_review["objectText"]
            and "连线" in proof_path_object_inspector_final_review["coverageText"]
            and proof_path_object_inspector_final_review["neighborCount"] >= 2
            and "THR_LOCK" in proof_path_object_inspector_final_review["neighborText"]
            and "logic4" in proof_path_object_inspector_neighbor_review["reviewObjectText"]
            and "logic4" in proof_path_object_inspector_neighbor_review["readbackText"]
            and "logic4" in proof_path_object_inspector_neighbor_review["inspectorObjectText"]
            and proof_path_chip_review["selectedAnchor"] == "P035-S01"
            and "tls_unlocked" in proof_path_chip_review["reviewObjectText"]
            and "聚焦节点" in proof_path_chip_review["reviewSyncText"]
            and "tls_unlocked" in proof_path_chip_review["readbackText"]
            and "tls_unlocked" in proof_path_object_inspector_chip_review["objectText"]
            and "节点" in proof_path_object_inspector_chip_review["coverageText"]
            and proof_path_object_inspector_chip_review["neighborCount"] >= 2
            and "L3" in proof_path_object_inspector_chip_review["neighborText"]
        )
        else "fail",
        "proof_path_coverage_grid": "pass"
        if (
            proof_path_coverage_grid_review["stepCount"] == 5
            and proof_path_coverage_grid_review["focusChipCount"] >= 10
            and "5/5 步" in proof_path_coverage_grid_review["statusText"]
            and "20/20 节点" in proof_path_coverage_grid_review["statusText"]
            and "23/23 连线" in proof_path_coverage_grid_review["statusText"]
            and "TLS 115VAC" in proof_path_coverage_grid_review["firstText"]
            and "THR_LOCK" in proof_path_coverage_grid_review["finalText"]
            and "20/20 节点" in proof_path_coverage_grid_review["finalText"]
            and "23/23 连线" in proof_path_coverage_grid_review["finalText"]
            and proof_path_coverage_grid_final_review["activeSteps"] == ["P035-S05"]
            and proof_path_coverage_grid_final_review["selectedAnchor"] == "P035-S05"
            and proof_path_coverage_grid_final_review["highlightedNodeCount"] == 20
            and proof_path_coverage_grid_final_review["highlightedWireCount"] == 23
            and "累计构建" in proof_path_coverage_grid_final_review["reviewObjectText"]
            and proof_path_coverage_grid_focus_review["activeSteps"] == ["P035-S05"]
            and proof_path_coverage_grid_focus_review["activeFocusIds"] == ["wire_logic4_thr_lock"]
            and "wire_logic4_thr_lock" in proof_path_coverage_grid_focus_review["readbackText"]
            and "wire_logic4_thr_lock" in proof_path_coverage_grid_focus_review["reviewObjectText"]
            and "wire_logic4_thr_lock" in proof_path_coverage_grid_focus_review["inspectorObjectText"]
            and proof_path_coverage_grid_trace_switch_review["activeSteps"] == ["P035-S02"]
            and proof_path_coverage_grid_trace_switch_review["selectedAnchor"] == "P035-S02"
            and "12/20 节点" in proof_path_coverage_grid_trace_switch_review["readbackText"]
            and "11/23 连线" in proof_path_coverage_grid_trace_switch_review["readbackText"]
            and "wire_logic4_thr_lock" not in proof_path_coverage_grid_trace_switch_review["readbackText"]
        )
        else "fail",
        "proof_path_delta_rail": "pass"
        if (
            proof_path_delta_rail_review["stepCount"] == 5
            and proof_path_delta_rail_review["focusChipCount"] >= 20
            and "5/5 步" in proof_path_delta_rail_review["statusText"]
            and "+20 节点" in proof_path_delta_rail_review["statusText"]
            and "+23 连线" in proof_path_delta_rail_review["statusText"]
            and "0->6/20 节点" in proof_path_delta_rail_review["firstText"]
            and "+6 节点" in proof_path_delta_rail_review["firstText"]
            and "18->20/20 节点" in proof_path_delta_rail_review["finalText"]
            and "20->23/23 连线" in proof_path_delta_rail_review["finalText"]
            and "+2 节点" in proof_path_delta_rail_review["finalText"]
            and "+3 连线" in proof_path_delta_rail_review["finalText"]
            and proof_path_delta_rail_final_review["activeSteps"] == ["P035-S05"]
            and proof_path_delta_rail_final_review["selectedAnchor"] == "P035-S05"
            and proof_path_delta_rail_final_review["highlightedNodeCount"] == 20
            and proof_path_delta_rail_final_review["highlightedWireCount"] == 23
            and "累计构建" in proof_path_delta_rail_final_review["reviewObjectText"]
            and proof_path_delta_rail_focus_review["activeSteps"] == ["P035-S05"]
            and proof_path_delta_rail_focus_review["activeFocusIds"] == ["wire_logic4_thr_lock"]
            and "wire_logic4_thr_lock" in proof_path_delta_rail_focus_review["readbackText"]
            and "wire_logic4_thr_lock" in proof_path_delta_rail_focus_review["reviewObjectText"]
            and "wire_logic4_thr_lock" in proof_path_delta_rail_focus_review["inspectorObjectText"]
        )
        else "fail",
        "proof_path_source_rail": "pass"
        if (
            proof_path_source_rail_review["stepCount"] == 5
            and proof_path_source_rail_review["anchorChipCount"] >= 20
            and "5/5 步" in proof_path_source_rail_review["statusText"]
            and "源句命中" in proof_path_source_rail_review["statusText"]
            and "飞机离地小于6ft" in proof_path_source_rail_review["firstText"]
            and "油门台反推电子锁" in proof_path_source_rail_review["finalText"]
            and "P035" in proof_path_source_rail_review["finalAnchors"]
            and proof_path_source_rail_anchor_review["activeSteps"] == ["P035-S05"]
            and proof_path_source_rail_anchor_review["selectedAnchor"] == "P035-S05"
            and "P035" in proof_path_source_rail_anchor_review["readbackText"]
            and "油门台反推电子锁" in proof_path_source_rail_anchor_review["readbackText"]
        )
        else "fail",
        "proof_path_sentence_matrix": "pass"
        if (
            proof_path_sentence_matrix_review["stepCount"] == 5
            and proof_path_sentence_matrix_review["objectChipCount"] >= 40
            and "5/5 句" in proof_path_sentence_matrix_review["statusText"]
            and "20/20 节点" in proof_path_sentence_matrix_review["finalText"]
            and "23/23 连线" in proof_path_sentence_matrix_review["finalText"]
            and "THR_LOCK" in proof_path_sentence_matrix_review["finalText"]
            and "wire_logic4_thr_lock" in proof_path_sentence_matrix_review["finalText"]
            and proof_path_sentence_matrix_focus_review["activeSteps"] == ["P035-S05"]
            and proof_path_sentence_matrix_focus_review["activeFocusIds"] == ["wire_logic4_thr_lock"]
            and proof_path_sentence_matrix_focus_review["selectedAnchor"] == "P035-S05"
            and "wire_logic4_thr_lock" in proof_path_sentence_matrix_focus_review["readbackText"]
            and "wire_logic4_thr_lock" in proof_path_sentence_matrix_focus_review["reviewObjectText"]
            and "wire_logic4_thr_lock" in proof_path_sentence_matrix_focus_review["inspectorObjectText"]
        )
        else "fail",
        "proof_path_predicate_matrix": "pass"
        if (
            proof_path_predicate_matrix_review["stepCount"] == 5
            and proof_path_predicate_matrix_review["focusCount"] >= 5
            and "5/5 判据" in proof_path_predicate_matrix_review["statusText"]
            and "VDT90 AND L3" in proof_path_predicate_matrix_review["finalText"]
            and "wire_logic4_thr_lock" in proof_path_predicate_matrix_review["finalText"]
            and proof_path_predicate_matrix_focus_review["activeSteps"] == ["P035-S05"]
            and proof_path_predicate_matrix_focus_review["selectedAnchor"] == "P035-S05"
            and "wire_logic4_thr_lock" in proof_path_predicate_matrix_focus_review["activeFocusIds"]
            and "wire_logic4_thr_lock" in proof_path_predicate_matrix_focus_review["readbackText"]
            and "wire_logic4_thr_lock" in proof_path_predicate_matrix_focus_review["reviewObjectText"]
            and "wire_logic4_thr_lock" in proof_path_predicate_matrix_focus_review["inspectorObjectText"]
        )
        else "fail",
        "proof_path_blueprint_summary": "pass"
        if (
            proof_path_blueprint_summary_review["stepCount"] == 5
            and "P035 -> demo.html" in proof_path_blueprint_summary_review["statusText"]
            and "L1 TLS" in proof_path_blueprint_summary_review["chainText"]
            and "L4 THR_LOCK" in proof_path_blueprint_summary_review["chainText"]
            and "20/20 节点" in proof_path_blueprint_summary_review["finalText"]
            and "23/23 连线" in proof_path_blueprint_summary_review["finalText"]
            and "THR_LOCK" in proof_path_blueprint_summary_review["finalText"]
            and proof_path_blueprint_summary_final_review["activeSteps"] == ["P035-S05"]
            and proof_path_blueprint_summary_final_review["selectedAnchor"] == "P035-S05"
            and "完整 demo 电路闭合" in proof_path_blueprint_summary_final_review["readbackText"]
        )
        else "fail",
        "proof_path_lane_density": "pass"
        if (
            proof_path_lane_default_review["activeModes"] == ["blueprint"]
            and proof_path_lane_default_review["statusText"] == "蓝图"
            and proof_path_lane_default_review["hiddenLanes"] >= 4
            and proof_path_lane_default_review["visibleBlueprint"]
            and proof_path_lane_default_review["visibleOutput"]
            and not proof_path_lane_default_review["visibleSource"]
            and proof_path_lane_all_review["activeModes"] == ["all"]
            and proof_path_lane_all_review["statusText"] == "全部"
            and proof_path_lane_all_review["hiddenLanes"] == 0
            and proof_path_lane_all_review["visibleSource"]
            and proof_path_lane_all_review["visibleMatrix"]
            and proof_path_lane_all_review["visibleObject"]
        )
        else "fail",
        "proof_path_output_map": "pass"
        if (
            proof_path_output_map_review["targetCount"] == 5
            and proof_path_output_map_review["activeTargets"] == ["thr_lock"]
            and "5/5" in proof_path_output_map_review["statusText"]
            and "wire_logic4_thr_lock" in proof_path_output_map_review["thrText"]
            and "wire_logic1_tls115" in proof_path_output_map_review["tlsText"]
            and proof_path_output_map_tls_review["activeTargets"] == ["tls115"]
            and "TLS 115VAC" in proof_path_output_map_tls_review["readbackText"]
            and "wire_logic1_tls115" in proof_path_output_map_tls_review["reviewObjectText"]
            and "wire_logic1_tls115" in proof_path_output_map_tls_review["inspectorObjectText"]
        )
        else "fail",
        "scenario_comparator_readback": "pass"
        if (
            scenario_comparator_review["buttonCount"] == 2
            and "最大反推" in scenario_comparator_review["maxText"]
            and "抑制阻塞" in scenario_comparator_review["inhibitText"]
            and scenario_comparator_max_review["activeActions"] == ["max-reverse"]
            and "/2" in scenario_comparator_max_review["statusText"]
            and "最大反推" in scenario_comparator_max_review["readbackText"]
            and "THR ON" in scenario_comparator_max_review["readbackText"]
            and scenario_comparator_max_review["output"] == "ON"
            and scenario_comparator_inhibit_review["activeActions"] == ["inhibit-block"]
            and "2/2" in scenario_comparator_inhibit_review["statusText"]
            and "抑制阻塞" in scenario_comparator_inhibit_review["readbackText"]
            and "THR BLOCKED" in scenario_comparator_inhibit_review["readbackText"]
            and scenario_comparator_inhibit_review["output"] == "BLOCKED"
        )
        else "fail",
        "review_verdict_readback": "pass"
        if (
            review_verdict_review["cardCount"] == 5
            and "5/5" in review_verdict_review["statusText"]
            and "源记录" in review_verdict_review["sourceText"]
            and "5/5" in review_verdict_review["sourceText"]
            and "20/20" in review_verdict_review["circuitText"]
            and "23/23" in review_verdict_review["circuitText"]
            and "5/5" in review_verdict_review["outputsText"]
            and "wire_logic4_thr_lock" in review_verdict_review["focusText"]
            and "控制逻辑未改动" in review_verdict_review["boundaryText"]
            and "证据可审" in review_verdict_review["readbackText"]
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
            "assembly_map": str(assembly_map_path),
            "logic_equation_board": str(logic_equation_path),
            "topology_matrix": str(topology_matrix_path),
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
            "scenario_truth_table": str(scenario_truth_path),
            "operator_runway": str(operator_runway_path),
            "proof_transcript": str(proof_transcript_path),
            "control_strip": str(control_strip_path),
            "sentence_runner": str(sentence_runner_path),
            "proof_path": str(proof_path_path),
            "scenario_comparator": str(scenario_comparator_path),
            "review_verdict": str(review_verdict_path),
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
        "requirement_ledger_context_review": requirement_ledger_context_review,
        "requirement_ledger_action_review": requirement_ledger_action_review,
        "review_index_review": review_index_review,
        "review_index_navigation": review_index_navigation,
        "review_index_proof_path_navigation": review_index_proof_path_navigation,
        "review_index_after_trace": review_index_after_trace,
        "logic_equation_review": logic_equation_review,
        "logic_equation_focus_review": logic_equation_focus_review,
        "assembly_map_review": assembly_map_review,
        "assembly_map_action_review": assembly_map_action_review,
        "topology_matrix_review": topology_matrix_review,
        "topology_focus_review": topology_focus_review,
        "topology_filter_review": topology_filter_review,
        "topology_filter_restore_review": topology_filter_restore_review,
        "output_path_review": output_path_review,
        "output_path_focus_review": output_path_focus_review,
        "stored_output_path_review": stored_output_path_review,
        "output_maturity_review": output_maturity_review,
        "output_maturity_focus_review": output_maturity_focus_review,
        "output_maturity_restore_review": output_maturity_restore_review,
        "output_maturity_clear_review": output_maturity_clear_review,
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
        "operator_runway_review": operator_runway_review,
        "operator_runway_l4_review": operator_runway_l4_review,
        "operator_runway_inhibit_review": operator_runway_inhibit_review,
        "proof_transcript_review": proof_transcript_review,
        "proof_transcript_l4_review": proof_transcript_l4_review,
        "proof_transcript_inhibit_review": proof_transcript_inhibit_review,
        "control_strip_review": control_strip_review,
        "control_strip_l4_review": control_strip_l4_review,
        "control_strip_inhibit_review": control_strip_inhibit_review,
        "sentence_runner_review": sentence_runner_review,
        "sentence_runner_s03_review": sentence_runner_s03_review,
        "sentence_runner_s05_review": sentence_runner_s05_review,
        "proof_path_review": proof_path_review,
        "proof_path_final_review": proof_path_final_review,
        "proof_path_object_inspector_final_review": proof_path_object_inspector_final_review,
        "proof_path_object_inspector_neighbor_review": proof_path_object_inspector_neighbor_review,
        "proof_path_chip_review": proof_path_chip_review,
        "proof_path_object_inspector_chip_review": proof_path_object_inspector_chip_review,
        "proof_path_coverage_grid_review": proof_path_coverage_grid_review,
        "proof_path_coverage_grid_final_review": proof_path_coverage_grid_final_review,
        "proof_path_coverage_grid_focus_review": proof_path_coverage_grid_focus_review,
        "proof_path_coverage_grid_trace_switch_review": proof_path_coverage_grid_trace_switch_review,
        "proof_path_delta_rail_review": proof_path_delta_rail_review,
        "proof_path_delta_rail_final_review": proof_path_delta_rail_final_review,
        "proof_path_delta_rail_focus_review": proof_path_delta_rail_focus_review,
        "proof_path_source_rail_review": proof_path_source_rail_review,
        "proof_path_source_rail_anchor_review": proof_path_source_rail_anchor_review,
        "proof_path_sentence_matrix_review": proof_path_sentence_matrix_review,
        "proof_path_sentence_matrix_focus_review": proof_path_sentence_matrix_focus_review,
        "proof_path_predicate_matrix_review": proof_path_predicate_matrix_review,
        "proof_path_predicate_matrix_focus_review": proof_path_predicate_matrix_focus_review,
        "proof_path_blueprint_summary_review": proof_path_blueprint_summary_review,
        "proof_path_blueprint_summary_final_review": proof_path_blueprint_summary_final_review,
        "proof_path_lane_default_review": proof_path_lane_default_review,
        "proof_path_lane_all_review": proof_path_lane_all_review,
        "proof_path_output_map_review": proof_path_output_map_review,
        "proof_path_output_map_tls_review": proof_path_output_map_tls_review,
        "scenario_comparator_review": scenario_comparator_review,
        "scenario_comparator_max_review": scenario_comparator_max_review,
        "scenario_comparator_inhibit_review": scenario_comparator_inhibit_review,
        "review_verdict_review": review_verdict_review,
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
                "requirement_coverage_ledger": "fail",
                "review_index_navigation": "fail",
                "review_index_proof_path_context": "fail",
                "logic_equation_board_readback": "fail",
                "assembly_map_readback": "fail",
                "topology_matrix_readback": "fail",
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

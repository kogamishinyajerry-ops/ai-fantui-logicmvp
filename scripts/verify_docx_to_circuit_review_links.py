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


def verify_review_links(artifact_dir: Path) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_stamp()
    current_review_path = artifact_dir / f"docx-to-circuit-current-review-link-{stamp}.png"
    source_entry_path = artifact_dir / f"docx-to-circuit-source-entry-link-{stamp}.png"
    restricted = _restricted_diff()
    console_errors: list[str] = []

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
                source_page.screenshot(path=str(source_entry_path), full_page=True)
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
        "selectedElementId": "sw1",
        "selectedElementType": "node",
        "searchValue": "SW1",
        "levelValue": "L1",
        "countText": "7 / 44",
        "resultCount": 7,
        "visibleNodeCount": 20,
        "visibleWireCount": 23,
        "hitPointCount": 23,
    }
    source_expected = {
        **current_expected,
        "activeSourceEntryAnchor": "P004",
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
        "screenshots": "pass"
        if all(
            path.exists() and path.stat().st_size > 0
            for path in (current_review_path, source_entry_path)
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
        "states": {
            "current_review": current_state,
            "source_entry": source_state,
        },
        "screenshots": {
            "current_review": str(current_review_path),
            "source_entry": str(source_entry_path),
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
                "source_entry_link": "fail",
                "screenshots": "fail",
                "boundary": "fail",
            },
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

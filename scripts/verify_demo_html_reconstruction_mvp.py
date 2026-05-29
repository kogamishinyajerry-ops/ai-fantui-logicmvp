#!/usr/bin/env python3
"""Validate that the MVP surface still reproduces the old demo.html cockpit."""
from __future__ import annotations

import argparse
import http.client
import json
import re
import subprocess
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "demo_html_reconstruction_mvp_v0_1.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "demo_html_reconstruction_mvp_v0_1.schema.json"
GOLDEN_DEMO_PATH = PROJECT_ROOT / "src" / "well_harness" / "static" / "demo.html"
REPLICA_SURFACE_PATH = PROJECT_ROOT / "src" / "well_harness" / "static" / "demo_reconstruction" / "index.html"
HOMEPAGE_PATH = PROJECT_ROOT / "src" / "well_harness" / "static" / "index.html"
LOGIC_BUILDER_PATH = PROJECT_ROOT / "src" / "well_harness" / "static" / "logic_builder" / "index.html"
RESTRICTED_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_fan_chain_svg(html: str) -> str:
    match = re.search(
        r'<svg\b[^>]*id="fan-chain-svg"[^>]*>.*?</svg>',
        html,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("fan-chain-svg not found in demo.html")
    return match.group(0)


def _extract_canvas(svg: str) -> dict[str, int]:
    match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not match:
        return {"width": 0, "height": 0}
    return {"width": int(match.group(1)), "height": int(match.group(2))}


def _extract_golden_demo(html: str) -> dict[str, Any]:
    svg = _extract_fan_chain_svg(html)
    node_ids = re.findall(r'data-node="([^"]+)"', svg)
    wires = [
        {"source": source, "target": target}
        for source, target in re.findall(
            r'class="chain-wire"[^>]*data-src="([^"]+)"[^>]*data-dst="([^"]+)"',
            svg,
        )
    ]
    preset_ids = re.findall(r'data-preset="([^"]+)"', html)
    return {
        "canvas": _extract_canvas(svg),
        "node_count": len(node_ids),
        "wire_count": len(wires),
        "preset_count": len(preset_ids),
        "node_ids": node_ids,
        "preset_ids": preset_ids,
        "wires": wires,
    }


def _extract_replica_surface(html: str) -> dict[str, Any]:
    def _text_for_id(element_id: str) -> str:
        match = re.search(
            rf'id="{re.escape(element_id)}"[^>]*>(.*?)</',
            html,
            flags=re.DOTALL,
        )
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()

    return {
        "has_console_frame": 'id="demo-reconstruction-console-frame"' in html
        and 'src="/demo.html?embed=1&amp;palette=codex-light"' in html,
        "has_browser_evidence": 'id="demo-reconstruction-browser-evidence"' in html,
        "is_main_mvp_console": 'data-ux-page-role="demo-mvp-console"' in html
        and 'data-demo-mvp-console="true"' in html,
        "comparison_table_removed": "demo-reconstruction-comparison-table" not in html
        and "demo-reconstruction-compare-grid" not in html,
        "claimed_node_count": _text_for_id("demo-reconstruction-node-count"),
        "claimed_wire_count": _text_for_id("demo-reconstruction-wire-count"),
        "claimed_preset_count": _text_for_id("demo-reconstruction-preset-count"),
        "claimed_status_count": _text_for_id("demo-reconstruction-status-count"),
        "fidelity_text": _text_for_id("demo-reconstruction-fidelity"),
        "has_node_list": 'id="demo-reconstruction-node-list"' in html,
        "has_wire_list": 'id="demo-reconstruction-wire-list"' in html,
    }


def _extract_homepage_entry(html: str) -> dict[str, Any]:
    entry_match = re.search(r'<a\b[^>]*id="home-first-phase-demo-entry"[^>]*>', html)
    entry_html = entry_match.group(0) if entry_match else ""
    href_match = re.search(r'href="([^"]+)"', entry_html)
    priority_match = re.search(r'data-home-priority="([^"]+)"', entry_html)
    label_present = "demo.html 复刻 MVP 控制台" in html
    return {
        "entry_present": bool(entry_html),
        "route": href_match.group(1) if href_match else "",
        "priority": priority_match.group(1).replace("-", "_") if priority_match else "",
        "label": "demo.html 复刻 MVP 控制台" if label_present else "",
        "appears_before_default_mode_grid": (
            'id="home-first-phase-mvp"' in html
            and 'id="home-default-mode-grid"' in html
            and html.index('id="home-first-phase-mvp"') < html.index('id="home-default-mode-grid"')
        ),
    }


def _extract_logic_builder_bridge(html: str) -> dict[str, Any]:
    bridge_match = re.search(r'<a\b[^>]*id="logic-demo-bridge"[^>]*>', html)
    bridge_html = bridge_match.group(0) if bridge_match else ""
    href_match = re.search(r'href="([^"]+)"', bridge_html)
    return {
        "bridge_present": bool(bridge_html),
        "target_route": href_match.group(1) if href_match else "",
    }


def _fetch_routes() -> dict[str, Any]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        statuses: dict[str, int] = {}
        bodies: dict[str, str] = {}
        for route in ("/demo.html", "/demo-reconstruction"):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("GET", route)
            response = conn.getresponse()
            statuses[route] = response.status
            bodies[route] = response.read().decode("utf-8")
            conn.close()
        return {
            "server_started": thread.is_alive(),
            "demo_html_status": statuses["/demo.html"],
            "demo_reconstruction_status": statuses["/demo-reconstruction"],
            "demo_html_contains_svg": 'id="fan-chain-svg"' in bodies["/demo.html"],
            "demo_reconstruction_contains_panel": (
                'id="demo-reconstruction-console-frame"' in bodies["/demo-reconstruction"]
            ),
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


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


def _compare_to_fixture(
    *,
    fixture: dict[str, Any],
    golden_demo: dict[str, Any],
    replica_surface: dict[str, Any],
    homepage_entry: dict[str, Any],
    logic_builder_bridge: dict[str, Any],
    routes: dict[str, Any],
    restricted_diff: list[str],
) -> list[str]:
    contract = fixture["contract"]
    mismatches: list[str] = []

    if golden_demo["canvas"] != contract["expected_canvas"]:
        mismatches.append("golden_demo.canvas")
    if golden_demo["node_count"] != contract["expected_node_count"]:
        mismatches.append("golden_demo.node_count")
    if golden_demo["wire_count"] != contract["expected_wire_count"]:
        mismatches.append("golden_demo.wire_count")
    if golden_demo["preset_count"] != contract["expected_preset_count"]:
        mismatches.append("golden_demo.preset_count")
    if golden_demo["node_ids"] != contract["required_node_ids"]:
        mismatches.append("golden_demo.node_ids")
    if sorted(golden_demo["preset_ids"]) != sorted(contract["required_preset_ids"]):
        mismatches.append("golden_demo.preset_ids")

    golden_html = GOLDEN_DEMO_PATH.read_text(encoding="utf-8")
    for element_id in contract["required_status_output_ids"]:
        if f'id="{element_id}"' not in golden_html:
            mismatches.append(f"golden_demo.status_output.{element_id}")
    for element_id in contract["required_output_card_ids"]:
        if f'id="{element_id}"' not in golden_html:
            mismatches.append(f"golden_demo.output_card.{element_id}")

    if replica_surface["has_console_frame"] is not True:
        mismatches.append("replica_surface.console_frame")
    if replica_surface["has_browser_evidence"] is not True:
        mismatches.append("replica_surface.browser_evidence")
    if replica_surface["is_main_mvp_console"] is not True:
        mismatches.append("replica_surface.main_mvp_console")
    if replica_surface["comparison_table_removed"] is not True:
        mismatches.append("replica_surface.comparison_page_residue")
    if replica_surface["claimed_node_count"] != "20/20":
        mismatches.append("replica_surface.claimed_node_count")
    if replica_surface["claimed_wire_count"] != "23/23":
        mismatches.append("replica_surface.claimed_wire_count")
    if replica_surface["claimed_preset_count"] != "5/5":
        mismatches.append("replica_surface.claimed_preset_count")
    if replica_surface["claimed_status_count"] != "6/6":
        mismatches.append("replica_surface.claimed_status_count")
    if "可运行电路" not in replica_surface["fidelity_text"]:
        mismatches.append("replica_surface.fidelity_text")
    if replica_surface["has_node_list"] is not True or replica_surface["has_wire_list"] is not True:
        mismatches.append("replica_surface.detail_lists")

    if homepage_entry != {
        "entry_present": True,
        "route": fixture["homepage_entry"]["route"],
        "priority": fixture["homepage_entry"]["priority"],
        "label": fixture["homepage_entry"]["label"],
        "appears_before_default_mode_grid": True,
    }:
        mismatches.append("homepage_entry")

    if logic_builder_bridge != {"bridge_present": True, "target_route": "/demo-reconstruction"}:
        mismatches.append("logic_builder_bridge")

    if routes.get("demo_html_status") != 200:
        mismatches.append("routes.demo_html_status")
    if routes.get("demo_reconstruction_status") != 200:
        mismatches.append("routes.demo_reconstruction_status")
    if routes.get("demo_html_contains_svg") is not True:
        mismatches.append("routes.demo_html_contains_svg")
    if routes.get("demo_reconstruction_contains_panel") is not True:
        mismatches.append("routes.demo_reconstruction_contains_panel")

    if restricted_diff:
        mismatches.append("boundary.restricted_diff")
    return mismatches


def verify(fixture_path: Path) -> dict[str, Any]:
    schema = _load_json(SCHEMA_PATH)
    fixture = _load_json(fixture_path)
    jsonschema.Draft202012Validator(schema).validate(fixture)

    golden_demo = _extract_golden_demo(GOLDEN_DEMO_PATH.read_text(encoding="utf-8"))
    replica_surface = _extract_replica_surface(REPLICA_SURFACE_PATH.read_text(encoding="utf-8"))
    homepage_entry = _extract_homepage_entry(HOMEPAGE_PATH.read_text(encoding="utf-8"))
    logic_builder_bridge = _extract_logic_builder_bridge(LOGIC_BUILDER_PATH.read_text(encoding="utf-8"))
    routes = _fetch_routes()
    restricted = _restricted_diff()

    mismatches = _compare_to_fixture(
        fixture=fixture,
        golden_demo=golden_demo,
        replica_surface=replica_surface,
        homepage_entry=homepage_entry,
        logic_builder_bridge=logic_builder_bridge,
        routes=routes,
        restricted_diff=restricted,
    )
    gates = {
        "golden_demo_contract": "pass",
        "replica_surface_contract": "pass",
        "homepage_entry": "pass",
        "logic_builder_bridge": "pass",
        "local_routes": "pass",
        "boundary": "pass",
    }
    if any(item.startswith("golden_demo.") for item in mismatches):
        gates["golden_demo_contract"] = "fail"
    if any(item.startswith("replica_surface.") for item in mismatches):
        gates["replica_surface_contract"] = "fail"
    if "homepage_entry" in mismatches:
        gates["homepage_entry"] = "fail"
    if "logic_builder_bridge" in mismatches:
        gates["logic_builder_bridge"] = "fail"
    if any(item.startswith("routes.") for item in mismatches):
        gates["local_routes"] = "fail"
    if any(item.startswith("boundary.") for item in mismatches):
        gates["boundary"] = "fail"

    status = "pass" if not mismatches else "fail"
    return {
        "$schema": fixture["$schema"],
        "kind": fixture["kind"],
        "mvp_id": fixture["mvp_id"],
        "status": status,
        "schema_valid": True,
        "fixture_path": str(fixture_path),
        "fixture_match": status == "pass",
        "mismatches": mismatches,
        "golden_reference": fixture["golden_reference"],
        "replica_surface": fixture["replica_surface"],
        "homepage_entry": fixture["homepage_entry"],
        "contract": fixture["contract"],
        "deterministic_gates": gates,
        "observed": {
            "golden_demo": golden_demo,
            "replica_surface": replica_surface,
            "homepage_entry": homepage_entry,
            "logic_builder_bridge": logic_builder_bridge,
            "routes": routes,
            "restricted_diff": restricted,
        },
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
        description="Validate the demo.html reconstruction MVP golden contract.",
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: demo.html reconstruction MVP matches golden contract")
    else:
        print(f"FAIL: demo.html reconstruction MVP drifted ({', '.join(payload['mismatches'])})")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        payload = verify(args.fixture)
    except Exception as exc:  # pragma: no cover - surfaced in CI logs.
        payload = {
            "status": "fail",
            "schema_valid": False,
            "fixture_match": False,
            "mismatches": ["runtime_error"],
            "error": str(exc),
        }
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

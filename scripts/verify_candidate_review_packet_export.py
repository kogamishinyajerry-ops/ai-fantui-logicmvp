#!/usr/bin/env python3
"""CI regression check for the candidate review packet export route."""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from well_harness.agent_review_packet import (
    CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE,
    validate_candidate_review_packet_export,
)
from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "candidate_review_packet_export_v0_1.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _chain_statuses(packet: dict[str, Any]) -> list[str]:
    chains = packet["review_packet"].get("finding_chains", [])
    return [str(chain.get("status", "")) for chain in chains if isinstance(chain, dict)]


def _chain_convergence(packet: dict[str, Any]) -> list[dict[str, Any]]:
    chains = packet["review_packet"].get("finding_chains", [])
    return [
        chain.get("convergence", {})
        for chain in chains
        if isinstance(chain, dict) and isinstance(chain.get("convergence", {}), dict)
    ]


def _chain_finding_codes(packet: dict[str, Any]) -> list[str]:
    chains = packet["review_packet"].get("finding_chains", [])
    codes: list[str] = []
    for chain in chains:
        if not isinstance(chain, dict):
            continue
        finding = chain.get("finding", {})
        if isinstance(finding, dict):
            codes.append(str(finding.get("code", "")))
    return codes


def _review_surface(packet: dict[str, Any]) -> dict[str, Any]:
    review_packet = packet["review_packet"]
    return {
        "reviewer_status": str(review_packet.get("reviewer", {}).get("status", "")),
        "summary": review_packet.get("summary", {}),
        "finding_codes": _chain_finding_codes(packet),
        "finding_chain_statuses": _chain_statuses(packet),
        "finding_chain_convergence": _chain_convergence(packet),
    }


def _fetch_json(url: str, *, retries: int = 20, delay_s: float = 0.05) -> dict[str, Any]:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(delay_s)
    raise RuntimeError(f"could not fetch {url}: {last_error}")


def _start_server(host: str, port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer((host, port), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def verify_export(host: str, port: int, fixture_path: Path) -> dict[str, Any]:
    server, thread = _start_server(host, port)
    actual_port = server.server_address[1]
    base_url = f"http://{host}:{actual_port}"
    url = f"{base_url}{CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE}"
    try:
        actual = _fetch_json(url)
        validate_candidate_review_packet_export(actual)
        expected = _load_json(fixture_path)
        validate_candidate_review_packet_export(expected)

        actual_surface = _review_surface(actual)
        expected_surface = _review_surface(expected)
        mismatches = [
            key
            for key in sorted(expected_surface)
            if actual_surface.get(key) != expected_surface.get(key)
        ]
        fixture_match = not mismatches
        return {
            "status": "pass" if fixture_match else "fail",
            "server_started": thread.is_alive(),
            "base_url": base_url,
            "route": CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE,
            "schema_valid": True,
            "fixture_path": str(fixture_path),
            "fixture_match": fixture_match,
            "mismatches": mismatches,
            **actual_surface,
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Start the local demo server, fetch the candidate review packet "
            "export route, validate schema, and compare regression fields "
            "against the fixture."
        )
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def _emit(result: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return
    if result["status"] == "pass":
        print(
            "PASS: candidate review packet export route matches fixture "
            f"({result['route']})"
        )
        return
    print(
        "FAIL: candidate review packet export route drifted "
        f"({', '.join(result.get('mismatches', []))})"
    )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        result = verify_export(args.host, args.port, args.fixture)
    except Exception as exc:  # pragma: no cover - surfaced for CI logs.
        result = {
            "status": "fail",
            "server_started": False,
            "route": CANDIDATE_REVIEW_PACKET_EXPORT_ROUTE,
            "schema_valid": False,
            "fixture_match": False,
            "mismatches": ["runtime_error"],
            "error": str(exc),
        }
    _emit(result, args.format)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Pitch-day explain prewarm for the canonical wow_a questions.

P25 option C recommends prewarming the two canonical explain questions before
pitch so the demo can transparently serve cached LLM explanations instead of
paying live latency during wow_a.

This script:
1. Reuses an already-running demo_server on :8799 when present, otherwise
   boots one with the chosen backend.
2. Fetches live lever-snapshots for the canonical wow_a beats to build real
   truth context.
3. Calls `/api/chat/explain-prewarm` twice:
   - warm round: populate the explain cache
   - verify round: confirm the same requests now return cache hits
4. Writes a machine-readable artefact under `runs/pitch_prewarm_<ts>/`.

Usage:
    python3 scripts/pitch_prewarm.py
    python3 scripts/pitch_prewarm.py --backend ollama

Exit codes:
    0 = cache verified (GREEN)
    1 = partial / verification failed (YELLOW)
    2 = prerequisite missing (server unreachable or invalid snapshots)
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
RUNS_DIR = REPO_ROOT / "runs"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8799
SYSTEM_ID = "thrust-reverser"
LEVER_SNAPSHOT_PATH = "/api/lever-snapshot"
CHAT_EXPLAIN_PREWARM_PATH = "/api/chat/explain-prewarm"

BEAT_EARLY = {
    "tra_deg": -5,
    "radio_altitude_ft": 2,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "n1k": 0.8,
    "feedback_mode": "auto_scrubber",
    "deploy_position_percent": 90,
}
BEAT_DEEP = {
    "tra_deg": -35,
    "radio_altitude_ft": 2,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "n1k": 0.92,
    "feedback_mode": "auto_scrubber",
    "deploy_position_percent": 95,
}
PREWARM_CASES = (
    {"name": "wow_a_logic1_active", "question": "L1门为什么active", "lever_payload": BEAT_EARLY},
    {"name": "wow_a_logic3_active", "question": "L3门为什么active", "lever_payload": BEAT_DEEP},
)


def utc_timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((DEFAULT_HOST, port)) != 0


def _wait_ready(port: int, timeout_s: float = 15.0) -> tuple[bool, float]:
    started = time.monotonic()
    deadline = started + timeout_s
    while time.monotonic() < deadline:
        try:
            status, body, _ = _post_json(DEFAULT_HOST, port, LEVER_SNAPSHOT_PATH, BEAT_EARLY, timeout=1.5)
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.3)
            continue
        if status == 200 and isinstance(body, dict) and body.get("nodes"):
            return True, (time.monotonic() - started) * 1000
        time.sleep(0.3)
    return False, (time.monotonic() - started) * 1000


def _post_json(
    host: str,
    port: int,
    path: str,
    payload: dict[str, Any],
    *,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any] | str, float]:
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    started = time.monotonic()
    try:
        connection.request(
            "POST",
            path,
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
    finally:
        connection.close()
    elapsed_ms = (time.monotonic() - started) * 1000
    try:
        parsed: dict[str, Any] | str = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw
    return response.status, parsed, elapsed_ms


def _spawn(backend: str, model: str | None, port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["LLM_BACKEND"] = backend
    if backend == "ollama" and model:
        env["OLLAMA_MODEL"] = model
    return subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _kill(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def _extract_node_states(snapshot: dict[str, Any]) -> dict[str, str]:
    node_states: dict[str, str] = {}
    for node in snapshot.get("nodes", []) or []:
        node_id = node.get("id")
        node_state = node.get("state")
        if isinstance(node_id, str) and isinstance(node_state, str):
            node_states[node_id] = node_state
    return node_states


def _active_logic_nodes(snapshot: dict[str, Any]) -> list[str]:
    logic = snapshot.get("logic", {})
    return sorted(
        gate_id
        for gate_id, info in logic.items()
        if isinstance(info, dict) and info.get("active") is True
    )


def _build_explain_request(case: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    request_payload = dict(case["lever_payload"])
    request_payload.update(
        {
            "question": case["question"],
            "system_id": SYSTEM_ID,
            "lever_snapshot": snapshot,
            "node_states": _extract_node_states(snapshot),
        }
    )
    return request_payload


def _round_summary(
    *,
    name: str,
    status: int,
    elapsed_ms: float,
    body: dict[str, Any] | str,
) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {
            "name": name,
            "status": status,
            "elapsed_ms": round(elapsed_ms, 1),
            "requested_count": 0,
            "warmed_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": [{"error": "invalid_json", "message": str(body)[:200]}],
            "results": [],
        }
    return {
        "name": name,
        "status": status,
        "elapsed_ms": round(elapsed_ms, 1),
        "requested_count": int(body.get("requested_count", 0) or 0),
        "warmed_count": int(body.get("warmed_count", 0) or 0),
        "cache_hits": int(body.get("cache_hits", 0) or 0),
        "cache_misses": int(body.get("cache_misses", 0) or 0),
        "errors": body.get("errors", []) if isinstance(body.get("errors"), list) else [],
        "results": body.get("results", []) if isinstance(body.get("results"), list) else [],
    }


def _build_report(
    *,
    backend: str,
    model: str | None,
    host: str,
    port: int,
    reused_running_server: bool,
    boot_ms: float | None,
    snapshot_results: list[dict[str, Any]],
    warm_round: dict[str, Any],
    verify_round: dict[str, Any],
    error: str | None = None,
) -> dict[str, Any]:
    expected_count = len(PREWARM_CASES)
    snapshot_ok = len(snapshot_results) == expected_count and all(item.get("status") == 200 for item in snapshot_results)
    warm_ok = (
        warm_round["status"] == 200
        and warm_round["warmed_count"] == expected_count
        and not warm_round["errors"]
    )
    verify_ok = (
        verify_round["status"] == 200
        and verify_round["cache_hits"] == expected_count
        and verify_round["warmed_count"] == expected_count
        and not verify_round["errors"]
    )
    first_result = next(iter(warm_round["results"]), {})
    requested_model = model or ""
    actual_backend = str(first_result.get("llm_backend", ""))
    actual_model = str(first_result.get("llm_model", ""))
    backend_match: bool | None
    if actual_backend:
        backend_match = actual_backend == backend and (
            not requested_model or actual_model == requested_model
        )
    else:
        backend_match = None
    effective_error = error
    if effective_error is None and backend_match is False:
        effective_error = "backend_mismatch"
    verdict = "GREEN" if snapshot_ok and warm_ok and verify_ok and not effective_error else "YELLOW"
    summary = {
        "verdict": verdict,
        "expected_count": expected_count,
        "snapshot_ok": snapshot_ok,
        "warm_ok": warm_ok,
        "verify_ok": verify_ok,
        "verified_cache_hits": verify_round["cache_hits"],
        "requested_backend": backend,
        "requested_model": requested_model,
        "llm_backend": actual_backend or backend,
        "llm_model": actual_model or requested_model,
        "backend_match": backend_match,
    }
    return {
        "generated_at": utc_now_iso(),
        "backend": backend,
        "model": model or "",
        "host": host,
        "port": port,
        "reused_running_server": reused_running_server,
        "boot_ms": round(boot_ms, 1) if boot_ms is not None else None,
        "system_id": SYSTEM_ID,
        "cases": snapshot_results,
        "rounds": [warm_round, verify_round],
        "summary": summary,
        "verdict": verdict,
        "error": effective_error,
    }


def _render_summary_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Pitch Prewarm",
        "",
        f"- **Verdict:** {'✅' if report['verdict'] == 'GREEN' else '⚠️'} **{report['verdict']}**",
        f"- **Generated:** `{report['generated_at']}`",
        f"- **Backend:** `{summary.get('llm_backend') or report.get('backend') or 'unknown'}`",
        f"- **Model:** `{summary.get('llm_model') or report.get('model') or 'unknown'}`",
        f"- **Requested backend/model:** `{summary.get('requested_backend') or report.get('backend') or 'unknown'}` / "
        f"`{summary.get('requested_model') or report.get('model') or 'auto'}`",
        f"- **Boot:** `{report.get('boot_ms') if report.get('boot_ms') is not None else 'reused-running-server'}`",
        f"- **Verified cache hits:** `{summary.get('verified_cache_hits', 0)}/{summary.get('expected_count', 0)}`",
        "",
        "## Canonical cases",
        "",
        "| Case | Question | Snapshot | Active logic | Nodes |",
        "| ---- | -------- | -------- | ------------ | ----- |",
    ]
    for case in report["cases"]:
        lines.append(
            f"| {case['name']} | {case['question']} | {case['status']} ({case['snapshot_elapsed_ms']:.1f} ms) | "
            f"{', '.join(case['active_logic']) or '—'} | {case['node_count']} |"
        )
    lines.extend(
        [
            "",
            "## Prewarm rounds",
            "",
            "| Round | Status | Elapsed (ms) | Warmed | Cache hits | Cache misses | Errors |",
            "| ----- | ------ | ------------ | ------ | ---------- | ------------ | ------ |",
        ]
    )
    for round_payload in report["rounds"]:
        lines.append(
            f"| {round_payload['name']} | {round_payload['status']} | {round_payload['elapsed_ms']:.1f} | "
            f"{round_payload['warmed_count']}/{round_payload['requested_count']} | "
            f"{round_payload['cache_hits']} | {round_payload['cache_misses']} | "
            f"{len(round_payload['errors'])} |"
        )
    if summary.get("backend_match") is False:
        lines.extend(
            [
                "",
                "## Backend mismatch",
                "",
                f"- Requested `{summary.get('requested_backend')}` / `{summary.get('requested_model') or 'auto'}` "
                f"but warmed `{summary.get('llm_backend')}` / `{summary.get('llm_model') or 'unknown'}`.",
                "- Treat this artefact as non-green and rerun against a server started with the intended backend.",
            ]
        )
    lines.extend(
        [
            "",
            "Pitch-day rule: rerun this script after any demo_server restart or backend switch, because the explain cache is process-local.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artefacts(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.md").write_text(
        _render_summary_markdown(report),
        encoding="utf-8",
    )


def _detect_backend() -> tuple[str, str | None]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", 11434)) == 0:
                return "ollama", "qwen2.5:7b-instruct"
    except OSError:
        pass
    key_path = Path.home() / ".minimax_key"
    if key_path.exists() and key_path.read_text().strip():
        return "minimax", None
    return "ollama", "qwen2.5:7b-instruct"


def run_prewarm(
    *,
    backend: str,
    model: str | None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> tuple[dict[str, Any], Path]:
    ts = utc_timestamp_slug()
    out_dir = RUNS_DIR / f"pitch_prewarm_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    proc: subprocess.Popen | None = None
    reused_running_server = not _port_free(port)
    boot_ms: float | None = None

    try:
        if reused_running_server:
            ready, boot_ms = _wait_ready(port, timeout_s=5.0)
        else:
            proc = _spawn(backend, model, port)
            ready, boot_ms = _wait_ready(port, timeout_s=15.0)
        if not ready:
            report = _build_report(
                backend=backend,
                model=model,
                host=host,
                port=port,
                reused_running_server=reused_running_server,
                boot_ms=boot_ms,
                snapshot_results=[],
                warm_round=_round_summary(name="warm", status=0, elapsed_ms=0.0, body={}),
                verify_round=_round_summary(name="verify_cache", status=0, elapsed_ms=0.0, body={}),
                error="demo_server_unreachable",
            )
            write_artefacts(report, out_dir)
            return report, out_dir

        snapshot_results: list[dict[str, Any]] = []
        explain_requests: list[dict[str, Any]] = []
        for case in PREWARM_CASES:
            status, body, elapsed_ms = _post_json(host, port, LEVER_SNAPSHOT_PATH, case["lever_payload"], timeout=30.0)
            if status == 200 and isinstance(body, dict) and body.get("nodes"):
                snapshot_results.append(
                    {
                        "name": case["name"],
                        "question": case["question"],
                        "status": status,
                        "snapshot_elapsed_ms": round(elapsed_ms, 1),
                        "node_count": len(body.get("nodes", []) or []),
                        "active_logic": _active_logic_nodes(body),
                    }
                )
                explain_requests.append(_build_explain_request(case, body))
            else:
                snapshot_results.append(
                    {
                        "name": case["name"],
                        "question": case["question"],
                        "status": status,
                        "snapshot_elapsed_ms": round(elapsed_ms, 1),
                        "node_count": 0,
                        "active_logic": [],
                    }
                )

        if len(explain_requests) != len(PREWARM_CASES):
            report = _build_report(
                backend=backend,
                model=model,
                host=host,
                port=port,
                reused_running_server=reused_running_server,
                boot_ms=boot_ms,
                snapshot_results=snapshot_results,
                warm_round=_round_summary(name="warm", status=0, elapsed_ms=0.0, body={}),
                verify_round=_round_summary(name="verify_cache", status=0, elapsed_ms=0.0, body={}),
                error="snapshot_collection_failed",
            )
            write_artefacts(report, out_dir)
            return report, out_dir

        warm_status, warm_body, warm_elapsed_ms = _post_json(
            host,
            port,
            CHAT_EXPLAIN_PREWARM_PATH,
            {"requests": explain_requests},
            timeout=120.0,
        )
        verify_status, verify_body, verify_elapsed_ms = _post_json(
            host,
            port,
            CHAT_EXPLAIN_PREWARM_PATH,
            {"requests": explain_requests},
            timeout=120.0,
        )
        report = _build_report(
            backend=backend,
            model=model,
            host=host,
            port=port,
            reused_running_server=reused_running_server,
            boot_ms=boot_ms,
            snapshot_results=snapshot_results,
            warm_round=_round_summary(
                name="warm",
                status=warm_status,
                elapsed_ms=warm_elapsed_ms,
                body=warm_body,
            ),
            verify_round=_round_summary(
                name="verify_cache",
                status=verify_status,
                elapsed_ms=verify_elapsed_ms,
                body=verify_body,
            ),
        )
        write_artefacts(report, out_dir)
        return report, out_dir
    finally:
        if not reused_running_server:
            _kill(proc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pitch-day explain prewarm")
    parser.add_argument("--backend", choices=["minimax", "ollama"], default=None, help="LLM backend to prewarm")
    parser.add_argument("--model", default=None, help="Ollama model (default: qwen2.5:7b-instruct)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="demo_server host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="demo_server port")
    args = parser.parse_args()

    backend, detected_model = _detect_backend() if args.backend is None else (args.backend, None)
    model = args.model or detected_model or ("qwen2.5:7b-instruct" if backend == "ollama" else None)
    report, out_dir = run_prewarm(
        backend=backend,
        model=model,
        host=args.host,
        port=args.port,
    )
    summary = report.get("summary", {})
    sys.stdout.write(
        f"[prewarm] wrote {out_dir / 'report.json'} verdict={report.get('verdict', 'YELLOW')} "
        f"cache_hits={summary.get('verified_cache_hits', 0)}/{summary.get('expected_count', 0)}\n"
    )
    if report.get("error") == "demo_server_unreachable":
        return 2
    return 0 if report.get("verdict") == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())

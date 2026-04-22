#!/usr/bin/env python3
"""P21-03 local model smoke test — drives /api/chat/* via Ollama.

Spins up demo_server with LLM_BACKEND=ollama and exercises the three
LLM-dependent routes (explain / operate / reason) against a local
Ollama runtime. Emits a JSON report so P21-04 docs can cite real
latency numbers.

Usage:
    # Prereqs: `ollama serve` running, candidate model pulled.
    python3 scripts/local_model_smoke.py
    python3 scripts/local_model_smoke.py --model qwen2.5:7b-instruct
    python3 scripts/local_model_smoke.py --skip-if-unreachable  # CI-friendly

The script exits 0 and writes runs/local_model_smoke_<ts>/report.json
on success. Exit 2 signals Ollama unreachable and the script was asked
to skip; exit 1 signals a real failure worth investigating.
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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SERVER_PORT = 8797
OLLAMA_PROBE_HOST = "127.0.0.1"
OLLAMA_PROBE_PORT = 11434


def _ollama_reachable() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((OLLAMA_PROBE_HOST, OLLAMA_PROBE_PORT)) == 0


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, timeout_s: float = 10.0) -> bool:
    probe = json.dumps({
        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
        "aircraft_on_ground": True, "reverser_inhibited": False,
        "eec_enable": True, "n1k": 0.5,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
    }).encode()
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            c.request("POST", "/api/lever-snapshot", body=probe,
                      headers={"Content-Type": "application/json"})
            resp = c.getresponse()
            resp.read()
            c.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.2)
    return False


def _post(port: int, path: str, payload: dict, timeout: float = 60.0) -> tuple[int, dict, float]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    start = time.monotonic()
    try:
        conn.request("POST", path,
                     body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8")
    finally:
        conn.close()
    elapsed_ms = (time.monotonic() - start) * 1000
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = {"raw": raw}
    return resp.status, body, elapsed_ms


def _spawn_server(model: str) -> subprocess.Popen:
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing_pp if existing_pp else "")
    env["LLM_BACKEND"] = "ollama"
    env["OLLAMA_MODEL"] = model
    return subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(SERVER_PORT)],
        cwd=str(REPO_ROOT), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _kill(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait(timeout=2.0)


SMOKE_CASES = [
    {
        "name": "chat_explain_l3_gate",
        "path": "/api/chat/explain",
        "payload": {
            "question": "L3门为什么active",
            "system_id": "thrust-reverser",
        },
    },
    {
        "name": "chat_operate_vdt_adjust",
        "path": "/api/chat/operate",
        "payload": {
            "question": "帮我把VDT调节到90",
            "system_id": "thrust-reverser",
        },
    },
    {
        "name": "chat_reason_thr_lock",
        "path": "/api/chat/reason",
        "payload": {
            "question": "为什么THR_LOCK是true",
            "system_id": "thrust-reverser",
        },
    },
]


def run_smoke(model: str, skip_if_unreachable: bool) -> int:
    if not _ollama_reachable():
        msg = f"[smoke] Ollama not reachable at {OLLAMA_PROBE_HOST}:{OLLAMA_PROBE_PORT}"
        print(msg, file=sys.stderr)
        if skip_if_unreachable:
            print("[smoke] --skip-if-unreachable set; exit 2 (skipped)", file=sys.stderr)
            return 2
        return 1

    if not _port_free(SERVER_PORT):
        print(f"[smoke] port {SERVER_PORT} busy; aborting", file=sys.stderr)
        return 1

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = REPO_ROOT / "runs" / f"local_model_smoke_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    proc = _spawn_server(model)
    report: dict = {
        "timestamp_utc": ts,
        "backend": "ollama",
        "model": model,
        "cases": [],
    }
    try:
        if not _wait_ready(SERVER_PORT):
            print("[smoke] demo_server did not become ready", file=sys.stderr)
            return 1

        for case in SMOKE_CASES:
            print(f"[smoke] case={case['name']} → {case['path']}")
            try:
                status, body, elapsed_ms = _post(SERVER_PORT, case["path"], case["payload"])
                ok = status == 200 and isinstance(body, dict) and "error" not in body
            except Exception as exc:
                status, body, elapsed_ms, ok = -1, {"exception": repr(exc)}, -1.0, False
            entry = {
                "name": case["name"],
                "path": case["path"],
                "status": status,
                "ok": ok,
                "elapsed_ms": round(elapsed_ms, 1),
                "body_keys": sorted(body.keys()) if isinstance(body, dict) else [],
                "error_code": body.get("error") if isinstance(body, dict) else None,
            }
            report["cases"].append(entry)
            print(f"  → status={status} ok={ok} {elapsed_ms:.0f}ms")
    finally:
        _kill(proc)

    all_ok = all(c["ok"] for c in report["cases"])
    report["verdict"] = "PASS" if all_ok else "FAIL"
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[smoke] wrote {out_dir / 'report.json'} verdict={report['verdict']}")
    return 0 if all_ok else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct"))
    parser.add_argument("--skip-if-unreachable", action="store_true")
    args = parser.parse_args()
    sys.exit(run_smoke(args.model, args.skip_if_unreachable))


if __name__ == "__main__":
    main()

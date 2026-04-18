#!/usr/bin/env python3
"""P22-01 dual-backend demo rehearsal.

Runs the立项汇报 演示 flow against BOTH backends end-to-end:
  1. Boot demo_server with LLM_BACKEND=minimax → exercise wow_a/b/c
     via /api/lever-snapshot + Monte Carlo + reverse-diagnose, then the
     three chat routes (explain/operate/reason).
  2. Kill, boot with LLM_BACKEND=ollama + OLLAMA_MODEL=qwen2.5:7b-instruct
     → re-run the same chat routes to prove continuity (wow_a/b/c are
     LLM-independent; we only re-verify they still respond post-switch).
  3. Emit combined report JSON + stable verdict.

Artefacts: runs/demo_rehearsal_dual_backend_<ts>/report.json plus the
original per-request payloads for each case. Exit 0 on full PASS,
1 on any case FAIL, 2 if a prerequisite is missing (MiniMax key,
Ollama unreachable).
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
PORT = 8799


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


def _spawn(backend: str, model: str | None) -> subprocess.Popen:
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing_pp if existing_pp else "")
    env["LLM_BACKEND"] = backend
    if backend == "ollama" and model:
        env["OLLAMA_MODEL"] = model
    return subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
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


BEAT_DEEP = {
    "tra_deg": -35, "radio_altitude_ft": 2, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.92,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
}
BEAT_EARLY = {
    "tra_deg": -5, "radio_altitude_ft": 2, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.8,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
}

WOW_CASES = [
    {"name": "wow_a_beat_deep", "path": "/api/lever-snapshot", "payload": BEAT_DEEP,
     "expect": lambda b: isinstance(b, dict) and len(b.get("nodes", [])) == 19},
    {"name": "wow_a_beat_early", "path": "/api/lever-snapshot", "payload": BEAT_EARLY,
     "expect": lambda b: isinstance(b, dict) and len(b.get("nodes", [])) == 19},
    {"name": "wow_b_monte_carlo_1k", "path": "/api/monte-carlo/run",
     "payload": {"n_trials": 1000, "seed": 42},
     "expect": lambda b: isinstance(b, dict) and "success_rate" in b},
    {"name": "wow_c_reverse_diagnose", "path": "/api/diagnosis/run",
     "payload": {"outcome": "thr_lock_active", "max_results": 10, "system_id": "thrust-reverser"},
     "expect": lambda b: isinstance(b, dict) and isinstance(b.get("results", b.get("diagnoses", [])), list)},
]

CHAT_CASES = [
    {"name": "chat_explain", "path": "/api/chat/explain",
     "payload": {"question": "L3门为什么active", "system_id": "thrust-reverser"}},
    {"name": "chat_operate", "path": "/api/chat/operate",
     "payload": {"question": "帮我把VDT调节到90", "system_id": "thrust-reverser"}},
    {"name": "chat_reason", "path": "/api/chat/reason",
     "payload": {"question": "为什么THR_LOCK是true", "system_id": "thrust-reverser"}},
]


def run_cases(cases: list[dict], with_expect: bool = False) -> list[dict]:
    results = []
    for case in cases:
        print(f"  → {case['name']} {case['path']}")
        try:
            status, body, elapsed = _post(PORT, case["path"], case["payload"])
            if with_expect and "expect" in case:
                ok = status == 200 and case["expect"](body)
            else:
                ok = status == 200 and isinstance(body, dict) and "error" not in body
        except Exception as exc:
            status, body, elapsed, ok = -1, {"exception": repr(exc)}, -1.0, False
        entry = {
            "name": case["name"], "path": case["path"],
            "status": status, "ok": ok, "elapsed_ms": round(elapsed, 1),
            "error_code": body.get("error") if isinstance(body, dict) else None,
        }
        results.append(entry)
        print(f"    status={status} ok={ok} {elapsed:.0f}ms")
    return results


def run_backend(backend: str, model: str | None) -> dict:
    if not _port_free(PORT):
        print(f"[rehearsal] port {PORT} busy — aborting", file=sys.stderr)
        sys.exit(1)

    print(f"\n[rehearsal] === backend={backend}" + (f" model={model}" if model else "") + " ===")
    proc = _spawn(backend, model)
    section = {"backend": backend, "model": model or "", "wow": [], "chat": []}
    try:
        if not _wait_ready(PORT):
            print("[rehearsal] demo_server not ready", file=sys.stderr)
            section["ready"] = False
            return section
        section["ready"] = True

        print(f"[rehearsal] wow_a/b/c cases (LLM-independent)")
        section["wow"] = run_cases(WOW_CASES, with_expect=True)

        print(f"[rehearsal] chat cases (LLM-dependent)")
        section["chat"] = run_cases(CHAT_CASES, with_expect=False)
    finally:
        _kill(proc)
    return section


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ollama-model", default="qwen2.5:7b-instruct")
    parser.add_argument("--skip-minimax-if-no-key", action="store_true")
    parser.add_argument("--skip-ollama-if-unreachable", action="store_true")
    args = parser.parse_args()

    # Prereq checks
    key_path = Path.home() / ".minimax_key"
    has_key = key_path.exists() and key_path.read_text().strip() != ""
    if not has_key and not args.skip_minimax_if_no_key:
        print("[rehearsal] MiniMax key missing at ~/.minimax_key", file=sys.stderr)
        sys.exit(2)

    ollama_reachable = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        ollama_reachable = s.connect_ex(("127.0.0.1", 11434)) == 0
    if not ollama_reachable and not args.skip_ollama_if_unreachable:
        print("[rehearsal] Ollama unreachable at 127.0.0.1:11434", file=sys.stderr)
        sys.exit(2)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_dir = REPO_ROOT / "runs" / f"demo_rehearsal_dual_backend_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {"timestamp_utc": ts, "sections": []}

    if has_key:
        report["sections"].append(run_backend("minimax", None))
    else:
        print("[rehearsal] skipping MiniMax section (no key)")
    if ollama_reachable:
        report["sections"].append(run_backend("ollama", args.ollama_model))
    else:
        print("[rehearsal] skipping Ollama section (unreachable)")

    # Verdict
    all_ok = True
    for section in report["sections"]:
        if not section.get("ready"):
            all_ok = False
        for entry in section["wow"] + section["chat"]:
            if not entry["ok"]:
                all_ok = False
    report["verdict"] = "PASS" if all_ok else "FAIL"

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[rehearsal] wrote {out_dir / 'report.json'} verdict={report['verdict']}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

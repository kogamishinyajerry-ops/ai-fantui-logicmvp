#!/usr/bin/env python3
"""P25-01 integrated timing rehearsal.

Validate pitch_script.md's hard-time section budgets against real backend
latency. For each pitch section with API needs, trigger the corresponding
cases (lever-snapshot / monte-carlo / diagnosis / chat) and aggregate
elapsed_ms per section. Compare to the section's API budget (a conservative
slice of the section's total spoken time). Emit a report with per-section
margin (positive = within budget) and an overall verdict.

Usage:
    python3 scripts/integrated_timing_rehearsal.py --backend minimax
    python3 scripts/integrated_timing_rehearsal.py --backend ollama \
        --ollama-model qwen2.5:7b-instruct

Artefacts:
    runs/integrated_timing_<backend>_<ts>/report.json
    runs/integrated_timing_<backend>_<ts>/per_section_summary.md

Exit codes:
    0 = all sections within budget (GREEN)
    1 = at least one section over budget (YELLOW — actionable but not fatal)
    2 = prerequisite missing (backend key absent / Ollama unreachable),
        or port busy
    3 = internal error (server didn't come up, unexpected crash)

The script reuses helpers from demo_rehearsal_dual_backend.py where possible
and never touches controller.py / LLM adapter / prompts / pitch_script.md.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
RUNS_DIR = REPO_ROOT / "runs"
PORT = 8799

# ── pitch_script.md section map (source of truth: docs/demo/pitch_script.md) ──
BEAT_EARLY = {
    "tra_deg": -5, "radio_altitude_ft": 2, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.8,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
}
BEAT_DEEP = {
    "tra_deg": -35, "radio_altitude_ft": 2, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.92,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
}
BEAT_INIT = {
    "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.5,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
}

SECTIONS = [
    {
        "id": 0, "name": "Opening", "duration_s": 90,
        "budget_api_ms": 0, "cases": [],
    },
    {
        "id": 1, "name": "wow_a 因果链", "duration_s": 240,
        "budget_api_ms": 15000,  # 15s total for 3 snapshots + 2 chats
        "cases": [
            {"name": "snapshot_init", "path": "/api/lever-snapshot",
             "payload": BEAT_INIT, "timing": "wow"},
            {"name": "snapshot_beat_early", "path": "/api/lever-snapshot",
             "payload": BEAT_EARLY, "timing": "wow"},
            {"name": "snapshot_beat_deep", "path": "/api/lever-snapshot",
             "payload": BEAT_DEEP, "timing": "wow"},
            {"name": "chat_explain_L1", "path": "/api/chat/explain",
             "payload": {"question": "L1门为什么active", "system_id": "thrust-reverser"},
             "timing": "chat"},
            {"name": "chat_explain_L3", "path": "/api/chat/explain",
             "payload": {"question": "L3门为什么active", "system_id": "thrust-reverser"},
             "timing": "chat"},
        ],
    },
    {
        "id": 2, "name": "wow_b 蒙特卡洛", "duration_s": 180,
        "budget_api_ms": 3000,  # 3s: 1k run + 10k run, both pure compute
        "cases": [
            {"name": "mc_1k", "path": "/api/monte-carlo/run",
             "payload": {"n_trials": 1000, "seed": 42}, "timing": "wow"},
            {"name": "mc_10k", "path": "/api/monte-carlo/run",
             "payload": {"n_trials": 10000, "seed": 42}, "timing": "wow"},
        ],
    },
    {
        "id": 3, "name": "wow_c 反诊断", "duration_s": 150,
        "budget_api_ms": 1000,  # 1s: pure enumeration
        "cases": [
            {"name": "diag_thr_lock", "path": "/api/diagnosis/run",
             "payload": {"outcome": "thr_lock_active", "max_results": 10,
                         "system_id": "thrust-reverser"}, "timing": "wow"},
        ],
    },
    {
        "id": 4, "name": "Fallback (backend switch)", "duration_s": 180,
        "budget_api_ms": 20000,  # 20s: 7B response can be 4-7s × 1-2 turns
        "cases": [
            {"name": "fallback_explain", "path": "/api/chat/explain",
             "payload": {"question": "L3门为什么active", "system_id": "thrust-reverser"},
             "timing": "chat"},
        ],
    },
    {
        "id": 5, "name": "R1–R5 总结", "duration_s": 150,
        "budget_api_ms": 0, "cases": [],
    },
    {
        "id": 6, "name": "闭场", "duration_s": 90,
        "budget_api_ms": 0, "cases": [],
    },
]


# ── Infrastructure (mirrors demo_rehearsal_dual_backend.py) ───────────────────
def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, timeout_s: float = 10.0) -> tuple[bool, float]:
    probe = json.dumps(BEAT_INIT).encode()
    deadline = time.monotonic() + timeout_s
    start = time.monotonic()
    while time.monotonic() < deadline:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            c.request("POST", "/api/lever-snapshot", body=probe,
                      headers={"Content-Type": "application/json"})
            resp = c.getresponse()
            resp.read()
            c.close()
            if resp.status == 200:
                return True, (time.monotonic() - start) * 1000
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.2)
    return False, (time.monotonic() - start) * 1000


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


# ── Case runner with degraded-response detection ─────────────────────────────
def _is_degraded(body: dict) -> str | None:
    """Return error_code if body represents a degraded/fallback response.

    Known degraded codes from llm_client / demo_server:
      minimax_api_key_missing, ollama_unreachable, llm_backend_unavailable
    """
    if not isinstance(body, dict):
        return None
    err = body.get("error")
    if isinstance(err, str) and err:
        return err
    return None


def run_section(section: dict) -> dict:
    out = {
        "id": section["id"],
        "name": section["name"],
        "duration_s": section["duration_s"],
        "budget_api_ms": section["budget_api_ms"],
        "cases": [],
        "actual_api_ms": 0,
        "degraded_case_count": 0,
    }
    if not section["cases"]:
        out["verdict"] = "no_api"
        out["margin_ms"] = 0
        return out

    total_ms = 0.0
    degraded = 0
    for case in section["cases"]:
        try:
            status, body, elapsed = _post(PORT, case["path"], case["payload"])
            deg = _is_degraded(body)
            ok = (status == 200) and (deg is None)
            if deg is not None:
                degraded += 1
            entry = {
                "name": case["name"], "path": case["path"],
                "timing_bucket": case["timing"],
                "status": status, "ok": ok,
                "elapsed_ms": round(elapsed, 1),
                "degraded_code": deg,
            }
        except Exception as exc:
            entry = {
                "name": case["name"], "path": case["path"],
                "timing_bucket": case["timing"],
                "status": -1, "ok": False,
                "elapsed_ms": -1, "degraded_code": None,
                "exception": repr(exc),
            }
        out["cases"].append(entry)
        if entry["elapsed_ms"] > 0:
            total_ms += entry["elapsed_ms"]
        print(f"    · {entry['name']:30s} {entry['path']:28s} "
              f"status={entry['status']} elapsed={entry['elapsed_ms']}ms"
              f"{' DEGRADED=' + entry['degraded_code'] if entry.get('degraded_code') else ''}")

    out["actual_api_ms"] = round(total_ms, 1)
    out["degraded_case_count"] = degraded
    out["margin_ms"] = round(section["budget_api_ms"] - total_ms, 1)
    if degraded > 0:
        out["verdict"] = "degraded"
    elif out["margin_ms"] >= 0:
        out["verdict"] = "within_budget"
    else:
        out["verdict"] = "over_budget"
    return out


# ── Main orchestration ───────────────────────────────────────────────────────
def run_backend(backend: str, model: str | None, out_dir: Path) -> dict:
    print(f"\n[timing] === backend={backend}" + (f" model={model}" if model else "") + " ===")
    if not _port_free(PORT):
        print(f"[timing] port {PORT} busy — aborting", file=sys.stderr)
        return {"backend": backend, "model": model or "", "ready": False,
                "error": "port_busy"}

    proc = _spawn(backend, model)
    report = {
        "backend": backend, "model": model or "",
        "port": PORT,
        "boot_ms": None,
        "ready": False,
        "sections": [],
        "overall_verdict": "error",
    }
    try:
        ready, boot_ms = _wait_ready(PORT)
        report["boot_ms"] = round(boot_ms, 1)
        report["ready"] = ready
        if not ready:
            print(f"[timing] demo_server not ready after {boot_ms:.0f}ms", file=sys.stderr)
            return report

        # Warmup hit to avoid cold-start bias on first measured case
        _post(PORT, "/api/lever-snapshot", BEAT_INIT, timeout=10.0)

        for sec in SECTIONS:
            print(f"\n[timing] Section {sec['id']} · {sec['name']}"
                  f" (budget_api={sec['budget_api_ms']}ms)")
            if not sec["cases"]:
                print("    · (no API calls in this section — skipped)")
                sec_result = run_section(sec)
                report["sections"].append(sec_result)
                continue
            sec_result = run_section(sec)
            print(f"[timing]   → actual_api={sec_result['actual_api_ms']}ms"
                  f" margin={sec_result['margin_ms']}ms"
                  f" verdict={sec_result['verdict']}")
            report["sections"].append(sec_result)

        # Overall verdict
        over = sum(1 for s in report["sections"] if s["verdict"] == "over_budget")
        deg = sum(1 for s in report["sections"] if s["verdict"] == "degraded")
        if over == 0 and deg == 0:
            report["overall_verdict"] = "GREEN"
        elif over == 0 and deg > 0:
            report["overall_verdict"] = "DEGRADED"
        else:
            report["overall_verdict"] = "YELLOW"
        report["over_budget_count"] = over
        report["degraded_section_count"] = deg
    finally:
        _kill(proc)
    return report


def write_artefacts(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        f"# Integrated Timing Rehearsal — backend={report['backend']}"
        + (f" model={report['model']}" if report.get("model") else ""),
        "",
        f"- boot_ms: {report.get('boot_ms')}",
        f"- ready: {report.get('ready')}",
        f"- overall_verdict: **{report.get('overall_verdict')}**",
        f"- over_budget_sections: {report.get('over_budget_count', 0)}",
        f"- degraded_sections: {report.get('degraded_section_count', 0)}",
        "",
        "## Per-section budget vs actual",
        "",
        "| 段 | 名称 | 段时长 | budget_api | actual_api | 裕度 | verdict | degraded |",
        "| -- | --- | ----- | ---------- | ---------- | ---- | ------- | -------- |",
    ]
    for s in report.get("sections", []):
        lines.append(
            f"| {s['id']} | {s['name']} | {s['duration_s']}s | "
            f"{s['budget_api_ms']}ms | {s.get('actual_api_ms', 0)}ms | "
            f"{s.get('margin_ms', 0)}ms | {s['verdict']} | "
            f"{s.get('degraded_case_count', 0)} |"
        )
    lines.append("")
    lines.append("## Per-case detail")
    lines.append("")
    for s in report.get("sections", []):
        if not s.get("cases"):
            continue
        lines.append(f"### 段 {s['id']} · {s['name']}")
        lines.append("")
        lines.append("| case | path | bucket | elapsed | status | degraded |")
        lines.append("| ---- | ---- | ------ | ------- | ------ | -------- |")
        for c in s["cases"]:
            lines.append(
                f"| {c['name']} | `{c['path']}` | {c['timing_bucket']} | "
                f"{c['elapsed_ms']}ms | {c['status']} | "
                f"{c.get('degraded_code') or '—'} |"
            )
        lines.append("")
    (out_dir / "per_section_summary.md").write_text("\n".join(lines) + "\n",
                                                     encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["minimax", "ollama"], required=True)
    parser.add_argument("--ollama-model", default="qwen2.5:7b-instruct")
    parser.add_argument("--skip-prereq-check", action="store_true",
                        help="Skip backend availability checks (for MOCK paths)")
    args = parser.parse_args()

    # Prereq check (honest: fail fast if backend truly unavailable)
    if not args.skip_prereq_check:
        if args.backend == "minimax":
            key = Path.home() / ".minimax_key"
            if not (key.exists() and key.read_text().strip()):
                print("[timing] MiniMax key missing at ~/.minimax_key", file=sys.stderr)
                return 2
        elif args.backend == "ollama":
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex(("127.0.0.1", 11434)) != 0:
                    print("[timing] Ollama unreachable at 127.0.0.1:11434",
                          file=sys.stderr)
                    return 2

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNS_DIR / f"integrated_timing_{args.backend}_{ts}"
    report = run_backend(args.backend,
                         args.ollama_model if args.backend == "ollama" else None,
                         out_dir)
    write_artefacts(report, out_dir)

    print(f"\n[timing] artefacts at: {out_dir}")
    print(f"[timing] overall verdict: {report.get('overall_verdict')}")

    verdict = report.get("overall_verdict")
    if verdict == "GREEN":
        return 0
    if verdict in ("YELLOW", "DEGRADED"):
        return 1
    return 3


if __name__ == "__main__":
    sys.exit(main())

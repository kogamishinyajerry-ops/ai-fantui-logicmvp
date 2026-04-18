"""P27 · Backend switch drill.

Measure real-world pkill + spawn + wait_ready latency for
MiniMax ↔ Ollama backend switches. Closes the unmeasured gap called
out in P25 findings § 1.3:

    "不模拟段 4 切换 backend 的真实切换步骤…没含 kill + respawn +
     wait_ready 的 5–8s"

Usage:
    python3 scripts/backend_switch_drill.py                  # full drill, N=2 per direction
    python3 scripts/backend_switch_drill.py --n-runs 3       # more samples
    python3 scripts/backend_switch_drill.py --direction a2b  # only MiniMax→Ollama
    python3 scripts/backend_switch_drill.py --skip-minimax-if-no-key
    python3 scripts/backend_switch_drill.py --skip-ollama-if-unreachable

Artefacts land in runs/backend_switch_drill_<ts>/:
    report.json   full data (per-run t_kill, t_spawn_to_ready, t_total_ms)
    summary.md    one-line verdict per direction

Exit codes:
    0 = all runs GREEN (both directions complete within budget)
    1 = YELLOW or DEGRADED (any direction slower than budget or a backend degraded)
    2 = prereq missing (Ollama unreachable, MiniMax key missing, port busy)
    3 = internal error (spawn crash, unhandled exception)

Honest boundaries:
    - Measures only the mechanical switch cost (SIGTERM → process exit →
      respawn → first /api/lever-snapshot OK). Does NOT measure the first
      post-switch chat/explain response latency; that's P25's territory.
    - First Ollama spawn after model cold-start is naturally slower
      (model load). Results split into "run 1" (cold) vs "run 2+" (warm)
      so findings can distinguish.
    - atexit hook SIGKILLs any leftover process to avoid zombies on
      port 8797.

This script does NOT modify any runtime code — only spawns the existing
demo_server module with different LLM_BACKEND env values.
"""
from __future__ import annotations

import argparse
import atexit
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
PORT = 8797  # dedicated; avoids :5173 dev, :8799 pitch, :8766 adversarial

# Budget reference from P25 findings §1.3 — "5–8s" conservative estimate.
# Anything > 8s = YELLOW, > 12s = ALERT (crosses natural talk-filler window).
BUDGET_GREEN_MS = 8000
BUDGET_YELLOW_MS = 12000

PROBE_PAYLOAD = {
    "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
    "aircraft_on_ground": True, "reverser_inhibited": False,
    "eec_enable": True, "n1k": 0.5,
    "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
}

_active_procs: list[subprocess.Popen] = []


def _cleanup_on_exit() -> None:
    for proc in _active_procs:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass


atexit.register(_cleanup_on_exit)


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _probe_ready(port: int) -> bool:
    """One-shot probe — returns True if /api/lever-snapshot returns 200."""
    try:
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
        c.request(
            "POST", "/api/lever-snapshot",
            body=json.dumps(PROBE_PAYLOAD).encode(),
            headers={"Content-Type": "application/json"},
        )
        resp = c.getresponse()
        resp.read()
        c.close()
        return resp.status == 200
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def _wait_ready_timed(port: int, timeout_s: float = 30.0) -> float | None:
    """Return ms from call until first 200, or None on timeout."""
    start = time.monotonic()
    deadline = start + timeout_s
    while time.monotonic() < deadline:
        if _probe_ready(port):
            return (time.monotonic() - start) * 1000
        time.sleep(0.1)
    return None


def _spawn(backend: str, model: str | None = None) -> subprocess.Popen:
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing_pp if existing_pp else "")
    env["LLM_BACKEND"] = backend
    if backend == "ollama" and model:
        env["OLLAMA_MODEL"] = model
    proc = subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
        cwd=str(REPO_ROOT), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    _active_procs.append(proc)
    return proc


def _kill_timed(proc: subprocess.Popen) -> float:
    """SIGTERM → wait exit; return ms from SIGTERM to exit."""
    if proc.poll() is not None:
        return 0.0
    start = time.monotonic()
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return 0.0
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait(timeout=2.0)
    return (time.monotonic() - start) * 1000


def _minimax_key_ok() -> bool:
    key_path = Path.home() / ".minimax_key"
    return key_path.exists() and key_path.stat().st_size > 0


def _ollama_reachable() -> bool:
    try:
        c = http.client.HTTPConnection("127.0.0.1", 11434, timeout=1.0)
        c.request("GET", "/")
        resp = c.getresponse()
        resp.read()
        c.close()
        return resp.status < 500
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def _one_switch(from_backend: str, to_backend: str,
                ollama_model: str) -> dict:
    """Run one switch: assume 'from' already running, kill it, spawn 'to',
    measure kill + spawn_to_ready. Caller is responsible for 'from' already
    being ready and for tearing down the 'to' proc after measurement.
    """
    result = {
        "from": from_backend, "to": to_backend,
        "t_kill_ms": None, "t_spawn_to_ready_ms": None,
        "t_total_ms": None, "verdict": "UNKNOWN",
        "error": None,
    }

    # The "from" proc is the last one in _active_procs
    from_proc = _active_procs[-1] if _active_procs else None
    if from_proc is None or from_proc.poll() is not None:
        result["error"] = "from_proc_missing"
        result["verdict"] = "DEGRADED"
        return result

    result["t_kill_ms"] = _kill_timed(from_proc)

    if not _port_free(PORT):
        time.sleep(0.5)
        if not _port_free(PORT):
            result["error"] = "port_stuck"
            result["verdict"] = "DEGRADED"
            return result

    _spawn(to_backend, model=ollama_model if to_backend == "ollama" else None)
    t_ready = _wait_ready_timed(PORT, timeout_s=30.0)
    if t_ready is None:
        result["error"] = "wait_ready_timeout"
        result["verdict"] = "DEGRADED"
        return result

    result["t_spawn_to_ready_ms"] = t_ready
    result["t_total_ms"] = result["t_kill_ms"] + t_ready
    total = result["t_total_ms"]
    if total <= BUDGET_GREEN_MS:
        result["verdict"] = "GREEN"
    elif total <= BUDGET_YELLOW_MS:
        result["verdict"] = "YELLOW"
    else:
        result["verdict"] = "ALERT"
    return result


def run_direction(from_b: str, to_b: str, n_runs: int,
                  ollama_model: str) -> list[dict]:
    """Repeatedly switch from→to→from→to...; we need a 'from' proc running
    before each cycle. For N runs we do: spawn from, switch to, kill to,
    spawn from, switch to, kill to, ... (N cycles)."""
    runs = []
    for i in range(n_runs):
        print(f"  [{from_b}→{to_b}] run {i + 1}/{n_runs}")

        # Ensure port free
        if not _port_free(PORT):
            print(f"    port {PORT} busy before run, aborting")
            runs.append({"from": from_b, "to": to_b, "verdict": "DEGRADED",
                         "error": "port_busy_at_cycle_start"})
            break

        # Spawn "from" backend, wait ready, warmup
        _spawn(from_b, model=ollama_model if from_b == "ollama" else None)
        t_from = _wait_ready_timed(PORT, timeout_s=60.0)
        if t_from is None:
            print(f"    from_backend {from_b} failed to come up")
            runs.append({"from": from_b, "to": to_b, "verdict": "DEGRADED",
                         "error": "from_backend_never_ready"})
            _kill_timed(_active_procs[-1])
            break

        # Small warmup: second probe to ensure adapter loaded
        _probe_ready(PORT)

        # Measure the switch
        r = _one_switch(from_b, to_b, ollama_model)
        r["cycle"] = i + 1
        runs.append(r)
        print(f"    kill={r['t_kill_ms']:.0f}ms spawn_to_ready="
              f"{r['t_spawn_to_ready_ms']:.0f}ms total={r['t_total_ms']:.0f}ms "
              f"verdict={r['verdict']}"
              if r["t_total_ms"] is not None
              else f"    DEGRADED ({r['error']})")

        # Teardown the 'to' proc before next cycle
        if _active_procs:
            _kill_timed(_active_procs[-1])
        time.sleep(0.5)

    return runs


def aggregate(runs: list[dict]) -> dict:
    clean = [r for r in runs if r.get("t_total_ms") is not None]
    if not clean:
        return {"n_clean": 0, "min_ms": None, "p50_ms": None,
                "max_ms": None, "overall_verdict": "DEGRADED"}
    totals = sorted(r["t_total_ms"] for r in clean)
    p50 = totals[len(totals) // 2]
    verdict_rank = {"GREEN": 0, "YELLOW": 1, "ALERT": 2, "DEGRADED": 3}
    worst = max((r["verdict"] for r in clean), key=lambda v: verdict_rank[v])
    return {
        "n_clean": len(clean), "n_total": len(runs),
        "min_ms": totals[0], "p50_ms": p50, "max_ms": totals[-1],
        "overall_verdict": worst,
    }


def write_artefacts(runs_a2b: list[dict], runs_b2a: list[dict],
                    out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "phase": "P27",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "port": PORT,
        "budget_green_ms": BUDGET_GREEN_MS,
        "budget_yellow_ms": BUDGET_YELLOW_MS,
        "minimax_to_ollama": {
            "runs": runs_a2b,
            "aggregate": aggregate(runs_a2b) if runs_a2b else None,
        },
        "ollama_to_minimax": {
            "runs": runs_b2a,
            "aggregate": aggregate(runs_b2a) if runs_b2a else None,
        },
    }
    (out_dir / "report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8",
    )

    lines = ["# Backend Switch Drill — Summary\n"]
    for label, key in (("MiniMax → Ollama", "minimax_to_ollama"),
                       ("Ollama → MiniMax", "ollama_to_minimax")):
        section = payload[key]
        agg = section["aggregate"]
        if agg is None or agg["n_clean"] == 0:
            lines.append(f"- **{label}**: SKIPPED/DEGRADED\n")
            continue
        lines.append(
            f"- **{label}**: {agg['n_clean']}/{agg['n_total']} clean · "
            f"min={agg['min_ms']:.0f}ms · p50={agg['p50_ms']:.0f}ms · "
            f"max={agg['max_ms']:.0f}ms · verdict={agg['overall_verdict']}\n"
        )
    (out_dir / "summary.md").write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="P27 backend switch drill")
    parser.add_argument("--n-runs", type=int, default=2,
                        help="runs per direction (default 2)")
    parser.add_argument("--direction", choices=["a2b", "b2a", "both"],
                        default="both",
                        help="a2b = MiniMax→Ollama; b2a = Ollama→MiniMax")
    parser.add_argument("--ollama-model", default="qwen2.5:7b-instruct")
    parser.add_argument("--skip-minimax-if-no-key", action="store_true")
    parser.add_argument("--skip-ollama-if-unreachable", action="store_true")
    args = parser.parse_args()

    # Prereq checks
    if not _port_free(PORT):
        print(f"[ERROR] port {PORT} already in use; drill aborted",
              file=sys.stderr)
        return 2

    minimax_ok = _minimax_key_ok()
    ollama_ok = _ollama_reachable()

    if not minimax_ok:
        if args.skip_minimax_if_no_key:
            print("[WARN] MiniMax key missing; skipping minimax-involved directions")
        else:
            print("[ERROR] ~/.minimax_key missing; drill aborted", file=sys.stderr)
            return 2
    if not ollama_ok:
        if args.skip_ollama_if_unreachable:
            print("[WARN] Ollama unreachable; skipping ollama-involved directions")
        else:
            print("[ERROR] Ollama 127.0.0.1:11434 unreachable; drill aborted",
                  file=sys.stderr)
            return 2

    # Decide which directions to run given backend availability
    do_a2b = args.direction in ("a2b", "both") and minimax_ok and ollama_ok
    do_b2a = args.direction in ("b2a", "both") and minimax_ok and ollama_ok
    if not (do_a2b or do_b2a):
        print("[ERROR] no feasible direction; drill aborted", file=sys.stderr)
        return 2

    print(f"=== P27 Backend Switch Drill ===")
    print(f"    port={PORT}  n_runs={args.n_runs}  "
          f"ollama_model={args.ollama_model}")
    print(f"    budgets: GREEN ≤ {BUDGET_GREEN_MS}ms · "
          f"YELLOW ≤ {BUDGET_YELLOW_MS}ms\n")

    runs_a2b: list[dict] = []
    runs_b2a: list[dict] = []

    try:
        if do_a2b:
            print("[direction] MiniMax → Ollama")
            runs_a2b = run_direction("minimax", "ollama",
                                     args.n_runs, args.ollama_model)
        if do_b2a:
            print("\n[direction] Ollama → MiniMax")
            runs_b2a = run_direction("ollama", "minimax",
                                     args.n_runs, args.ollama_model)
    except Exception as exc:  # pragma: no cover — safety net
        print(f"[FATAL] drill crashed: {exc!r}", file=sys.stderr)
        return 3

    # Artefacts
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = REPO_ROOT / "runs" / f"backend_switch_drill_{ts}"
    write_artefacts(runs_a2b, runs_b2a, out_dir)
    print(f"\n[artefacts] {out_dir.relative_to(REPO_ROOT)}/")
    print((out_dir / "summary.md").read_text(encoding="utf-8"))

    # Exit code
    def any_non_green(runs: list[dict]) -> bool:
        return any(r.get("verdict") not in ("GREEN", None) for r in runs)

    if any_non_green(runs_a2b) or any_non_green(runs_b2a):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

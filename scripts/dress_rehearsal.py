#!/usr/bin/env python3
"""P20.2 Dress Rehearsal — automated replay of 3 wow demos + timing audit.

Boots well_harness.demo_server on :8799 as a subprocess, replays the HTTP
keystroke sequences documented in docs/demo/wow_{a,b,c}_*.md, captures
per-step timing + response body, and writes a rehearsal_report.md.

Usage:
    python3 scripts/dress_rehearsal.py              # full rehearsal
    python3 scripts/dress_rehearsal.py --smoke      # 1-shot per scenario
    python3 scripts/dress_rehearsal.py --port 8799  # custom port

Outputs under runs/dress_rehearsal_<utc-timestamp>/:
    rehearsal_report.md      — human-readable PASS/FAIL + per-step timing
    wow_a_timeline.json      — machine-readable timings + response bodies
    wow_b_timeline.json
    wow_c_timeline.json
    server.log               — captured demo_server stdout/stderr
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
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8799
READY_TIMEOUT_S = 15.0

# Timing budgets (ms) per step, inherited from wow_{a,b,c}_*.md
TIMING_BUDGET_MS = {
    "wow_a_step": 500,      # single lever-snapshot warm (< 500ms)
    "wow_b_1k": 1000,       # MC 1k trials
    "wow_b_10k": 5000,      # MC 10k trials hard budget
    "wow_c_single": 1000,   # diagnosis/run single outcome
}

# Scenario keystrokes (HTTP-equivalent) — aligned to tests/e2e assertions
WOW_A_BEATS = [
    ("BEAT_EARLY", {
        "tra_deg": -5, "radio_altitude_ft": 2,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True, "n1k": 0.8,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
    }, {"logic1", "logic2"}),
    ("BEAT_DEEP", {
        "tra_deg": -35, "radio_altitude_ft": 2,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True, "n1k": 0.92,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 95,
    }, {"logic2", "logic3"}),
    ("BEAT_BLOCKED", {
        "tra_deg": -5, "radio_altitude_ft": 500,
        "engine_running": True, "aircraft_on_ground": False,
        "reverser_inhibited": False, "eec_enable": True, "n1k": 0.8,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 90,
    }, set()),
]

WOW_B_STEPS = [
    ("1k_baseline", {"system_id": "thrust-reverser", "n_trials": 1000, "seed": 42}, "wow_b_1k"),
    ("10k_highlight", {"system_id": "thrust-reverser", "n_trials": 10000, "seed": 42}, "wow_b_10k"),
    ("10k_replay", {"system_id": "thrust-reverser", "n_trials": 10000, "seed": 42}, "wow_b_10k"),
]

WOW_C_OUTCOMES = [
    "deploy_confirmed", "logic3_active", "logic1_active",
    "thr_lock_active", "tls_unlocked", "pls_unlocked",
]


@dataclass
class StepResult:
    name: str
    endpoint: str
    status: int
    elapsed_ms: float
    budget_ms: int | None
    ok: bool
    notes: str = ""
    response_summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioResult:
    scenario: str
    total_ms: float
    passed: int
    failed: int
    steps: list[StepResult] = field(default_factory=list)


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, deadline_s: float) -> bool:
    probe = json.dumps({
        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
        "aircraft_on_ground": True, "reverser_inhibited": False,
        "eec_enable": True, "n1k": 0.5,
        "feedback_mode": "auto_scrubber", "deploy_position_percent": 0,
    }).encode()
    start = time.monotonic()
    while time.monotonic() - start < deadline_s:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            c.request("POST", "/api/lever-snapshot", body=probe,
                      headers={"Content-Type": "application/json"})
            resp = c.getresponse()
            resp.read(); c.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.2)
    return False


def _spawn(port: int, logpath: Path) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    logfh = logpath.open("wb")
    return subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
        cwd=str(REPO_ROOT), env=env,
        stdout=logfh, stderr=subprocess.STDOUT,
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


def _post(port: int, path: str, payload: dict, timeout: float = 30.0) -> tuple[int, dict | str, float]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    t0 = time.monotonic()
    try:
        conn.request("POST", path, body=json.dumps(payload).encode("utf-8"),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8")
        elapsed_ms = (time.monotonic() - t0) * 1000
        try:
            body: dict | str = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return resp.status, body, elapsed_ms
    finally:
        conn.close()


def run_wow_a(port: int, smoke: bool) -> ScenarioResult:
    res = ScenarioResult(scenario="wow_a_causal_chain", total_ms=0.0, passed=0, failed=0)
    beats = WOW_A_BEATS[:1] if smoke else WOW_A_BEATS
    warm = True
    # Warmup to hit <500ms budget
    _post(port, "/api/lever-snapshot", WOW_A_BEATS[0][1])
    for name, payload, expected_active in beats:
        status, body, ms = _post(port, "/api/lever-snapshot", payload)
        budget = TIMING_BUDGET_MS["wow_a_step"]
        active = set()
        summary = {}
        ok = status == 200 and isinstance(body, dict)
        note = ""
        if ok:
            logic = body.get("logic", {})
            active = {k for k, v in logic.items() if isinstance(v, dict) and v.get("active")}
            summary = {
                "node_count": len(body.get("nodes", [])),
                "logic_active": sorted(active),
                "has_evidence": "evidence" in body,
            }
            if active != expected_active:
                ok = False
                note = f"logic mismatch: got {sorted(active)}, expected {sorted(expected_active)}"
            if ms > budget:
                ok = False
                note = (note + "; " if note else "") + f"timing {ms:.0f}ms > budget {budget}ms"
        else:
            note = f"non-200 or non-dict: status={status}"
        res.steps.append(StepResult(
            name=name, endpoint="/api/lever-snapshot",
            status=status, elapsed_ms=ms, budget_ms=budget, ok=ok,
            notes=note, response_summary=summary,
        ))
        res.total_ms += ms
        (res.passed if ok else res.failed).__add__  # no-op to silence
        if ok: res.passed += 1
        else:  res.failed += 1
    return res


def run_wow_b(port: int, smoke: bool) -> ScenarioResult:
    res = ScenarioResult(scenario="wow_b_monte_carlo", total_ms=0.0, passed=0, failed=0)
    steps = WOW_B_STEPS[:1] if smoke else WOW_B_STEPS
    replay_prev_body: dict | None = None
    for name, payload, budget_key in steps:
        status, body, ms = _post(port, "/api/monte-carlo/run", payload)
        budget = TIMING_BUDGET_MS[budget_key]
        ok = status == 200 and isinstance(body, dict)
        note = ""
        summary = {}
        if ok:
            required = {"n_trials", "n_failures", "success_rate", "failure_modes", "seed"}
            missing = required - set(body.keys())
            if missing:
                ok = False
                note = f"missing keys {missing}"
            else:
                summary = {
                    "n_trials": body["n_trials"],
                    "success_rate": round(body["success_rate"], 4),
                    "failure_modes": list(body["failure_modes"].keys()),
                    "seed": body["seed"],
                }
                if ms > budget:
                    ok = False
                    note = f"timing {ms:.0f}ms > budget {budget}ms"
                # Determinism check: 10k_replay must equal 10k_highlight exactly
                if name == "10k_replay" and replay_prev_body is not None:
                    if body != replay_prev_body:
                        ok = False
                        note = "non-deterministic: replay body differs from prior 10k"
                if name == "10k_highlight":
                    replay_prev_body = body
        else:
            note = f"non-200: status={status}"
        res.steps.append(StepResult(
            name=name, endpoint="/api/monte-carlo/run",
            status=status, elapsed_ms=ms, budget_ms=budget, ok=ok,
            notes=note, response_summary=summary,
        ))
        res.total_ms += ms
        if ok: res.passed += 1
        else:  res.failed += 1
    return res


def run_wow_c(port: int, smoke: bool) -> ScenarioResult:
    res = ScenarioResult(scenario="wow_c_reverse_diagnose", total_ms=0.0, passed=0, failed=0)
    outcomes = WOW_C_OUTCOMES[:1] if smoke else WOW_C_OUTCOMES
    for outcome in outcomes:
        payload = {"system_id": "thrust-reverser", "outcome": outcome, "max_results": 5}
        status, body, ms = _post(port, "/api/diagnosis/run", payload)
        budget = TIMING_BUDGET_MS["wow_c_single"]
        ok = status == 200 and isinstance(body, dict)
        note = ""
        summary = {}
        if ok:
            if body.get("outcome") != outcome:
                ok = False
                note = f"outcome echo mismatch"
            else:
                summary = {
                    "total_combos_found": body.get("total_combos_found"),
                    "result_count": len(body.get("results", [])),
                    "grid_resolution": body.get("grid_resolution"),
                }
                if ms > budget:
                    ok = False
                    note = f"timing {ms:.0f}ms > budget {budget}ms"
        else:
            note = f"non-200: status={status}"
        res.steps.append(StepResult(
            name=f"outcome={outcome}", endpoint="/api/diagnosis/run",
            status=status, elapsed_ms=ms, budget_ms=budget, ok=ok,
            notes=note, response_summary=summary,
        ))
        res.total_ms += ms
        if ok: res.passed += 1
        else:  res.failed += 1

    # Negative path: invalid outcome returns structured 400 (graceful degrade)
    if not smoke:
        status, body, ms = _post(port, "/api/diagnosis/run", {
            "system_id": "thrust-reverser", "outcome": "banana_outcome",
        })
        ok = status == 400 and isinstance(body, dict) and "error" in body
        res.steps.append(StepResult(
            name="invalid_outcome_graceful_400",
            endpoint="/api/diagnosis/run",
            status=status, elapsed_ms=ms, budget_ms=TIMING_BUDGET_MS["wow_c_single"],
            ok=ok, notes="" if ok else "expected 400 with error field",
            response_summary={"error": body.get("error") if isinstance(body, dict) else None},
        ))
        res.total_ms += ms
        if ok: res.passed += 1
        else:  res.failed += 1
    return res


def write_report(out_dir: Path, scenarios: list[ScenarioResult], started_utc: str,
                 ended_utc: str, wall_s: float, smoke: bool) -> Path:
    lines = []
    lines.append(f"# P20.2 Dress Rehearsal Report")
    lines.append("")
    lines.append(f"- Started UTC: `{started_utc}`")
    lines.append(f"- Ended UTC:   `{ended_utc}`")
    lines.append(f"- Wall clock:  `{wall_s:.2f}s`")
    lines.append(f"- Mode:        `{'smoke' if smoke else 'full'}`")
    total_pass = sum(s.passed for s in scenarios)
    total_fail = sum(s.failed for s in scenarios)
    verdict = "✅ PASS" if total_fail == 0 else f"❌ FAIL ({total_fail} failures)"
    lines.append(f"- Verdict:     **{verdict}**")
    lines.append(f"- Overall:     {total_pass} passed / {total_fail} failed")
    lines.append("")
    for sc in scenarios:
        v = "✅" if sc.failed == 0 else "❌"
        lines.append(f"## {v} {sc.scenario}")
        lines.append("")
        lines.append(f"Total scenario time: `{sc.total_ms:.0f}ms` · "
                     f"steps: {sc.passed} passed / {sc.failed} failed")
        lines.append("")
        lines.append("| Step | Endpoint | Status | Elapsed | Budget | OK | Notes |")
        lines.append("|---|---|---|---|---|---|---|")
        for st in sc.steps:
            budget = f"{st.budget_ms}ms" if st.budget_ms else "—"
            ok_mark = "✅" if st.ok else "❌"
            notes = (st.notes or "").replace("|", r"\|")
            lines.append(f"| `{st.name}` | `{st.endpoint}` | {st.status} | "
                         f"{st.elapsed_ms:.0f}ms | {budget} | {ok_mark} | {notes} |")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Generated by `scripts/dress_rehearsal.py` · "
                 f"Execution-by: opus47-max_")
    report_path = out_dir / "rehearsal_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true",
                        help="minimal replay (1 step per scenario) for CI")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--out-root", default=str(REPO_ROOT / "runs"))
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_root) / f"dress_rehearsal_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    server_log = out_dir / "server.log"

    if not _port_free(args.port):
        print(f"[ERROR] port {args.port} busy; aborting", file=sys.stderr)
        return 2

    print(f"[rehearsal] booting demo_server :{args.port} ...")
    proc = _spawn(args.port, server_log)
    started_monotonic = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    try:
        if not _wait_ready(args.port, READY_TIMEOUT_S):
            print(f"[ERROR] demo_server not ready within {READY_TIMEOUT_S}s", file=sys.stderr)
            return 3
        print(f"[rehearsal] server ready; starting {'smoke' if args.smoke else 'full'} run ...")

        sc_a = run_wow_a(args.port, args.smoke)
        (out_dir / "wow_a_timeline.json").write_text(
            json.dumps(asdict(sc_a), indent=2, default=str), encoding="utf-8")
        print(f"[wow_a] {sc_a.passed} pass / {sc_a.failed} fail · {sc_a.total_ms:.0f}ms")

        sc_b = run_wow_b(args.port, args.smoke)
        (out_dir / "wow_b_timeline.json").write_text(
            json.dumps(asdict(sc_b), indent=2, default=str), encoding="utf-8")
        print(f"[wow_b] {sc_b.passed} pass / {sc_b.failed} fail · {sc_b.total_ms:.0f}ms")

        sc_c = run_wow_c(args.port, args.smoke)
        (out_dir / "wow_c_timeline.json").write_text(
            json.dumps(asdict(sc_c), indent=2, default=str), encoding="utf-8")
        print(f"[wow_c] {sc_c.passed} pass / {sc_c.failed} fail · {sc_c.total_ms:.0f}ms")

        wall_s = time.monotonic() - started_monotonic
        ended_utc = datetime.now(timezone.utc).isoformat()
        scenarios = [sc_a, sc_b, sc_c]
        report = write_report(out_dir, scenarios, started_utc, ended_utc, wall_s, args.smoke)
        print(f"[rehearsal] report: {report.relative_to(REPO_ROOT)}")
        total_fail = sum(s.failed for s in scenarios)
        return 0 if total_fail == 0 else 1
    finally:
        _kill(proc)
        print(f"[rehearsal] server stopped; logs: "
              f"{server_log.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.exit(main())

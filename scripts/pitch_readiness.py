"""P29 · pre-pitch readiness aggregator.

Reads the most recent artefact per drill type from runs/, summarizes the
state into a single markdown scorecard, and returns a GREEN/YELLOW/RED
verdict Kogami can eyeball at T-0.

This does NOT re-run expensive drills. It only aggregates what's already
on disk. For live verification run the drills separately:
    python3 scripts/dress_rehearsal.py                       # ~30s
    python3 scripts/integrated_timing_rehearsal.py           # ~60s/backend
    python3 scripts/backend_switch_drill.py                  # ~90s
    python3 -m pytest                                        # ~90s
    python3 src/well_harness/static/adversarial_test.py      # ~3s

Usage:
    python3 scripts/pitch_readiness.py                       # stdout scorecard
    python3 scripts/pitch_readiness.py --out report.md       # write to file
    python3 scripts/pitch_readiness.py --stale-hours 24      # yellow if older

Exit codes:
    0 = all dimensions GREEN and fresh
    1 = at least one YELLOW (stale artefact, degraded, over budget)
    2 = at least one RED (artefact missing entirely, no evidence)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"

# (prefix, label) pairs — most recent matching dir wins
DRILL_PREFIXES = [
    ("dress_rehearsal_", "Dress Rehearsal (wow_a/b/c)"),
    ("integrated_timing_minimax_", "Integrated Timing · MiniMax"),
    ("integrated_timing_ollama_", "Integrated Timing · Ollama"),
    ("backend_switch_drill_", "Backend Switch Drill"),
    ("local_model_smoke_", "Local Model Smoke"),
    ("demo_rehearsal_dual_backend_", "Dual-Backend Rehearsal"),
]


def _latest_run_dir(prefix: str) -> Path | None:
    if not RUNS_DIR.exists():
        return None
    candidates = sorted(
        (d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith(prefix)),
        key=lambda p: p.name, reverse=True,
    )
    return candidates[0] if candidates else None


def _parse_timestamp(dirname: str) -> datetime | None:
    """Extract the 20YYMMDDTHHMMSSZ suffix from a run directory name."""
    m = re.search(r"(\d{8}T\d{6}Z)$", dirname)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def _age_hours(dir_path: Path) -> float | None:
    ts = _parse_timestamp(dir_path.name)
    if ts is None:
        return None
    delta = datetime.now(timezone.utc) - ts
    return delta.total_seconds() / 3600


def _read_dress_rehearsal(dir_path: Path) -> dict:
    report = dir_path / "rehearsal_report.md"
    out = {"verdict": "UNKNOWN", "detail": None}
    if not report.exists():
        return out
    text = report.read_text(encoding="utf-8")
    verdict_m = re.search(r"Verdict:\s*\*\*(.+?)\*\*", text)
    overall_m = re.search(r"Overall:\s*(.+)", text)
    if verdict_m:
        raw = verdict_m.group(1)
        out["verdict"] = "GREEN" if "PASS" in raw else (
            "RED" if "FAIL" in raw else "YELLOW"
        )
        out["detail"] = raw.strip()
    if overall_m:
        out["overall"] = overall_m.group(1).strip()
    return out


def _read_integrated_timing(dir_path: Path) -> dict:
    report = dir_path / "report.json"
    out = {"verdict": "UNKNOWN", "detail": None}
    if not report.exists():
        return out
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    # Aggregate section verdicts
    sections = data.get("sections", [])
    section_verdicts = [s.get("verdict") for s in sections]
    if any(v == "over_budget" for v in section_verdicts):
        out["verdict"] = "YELLOW"
    elif any(v == "degraded" for v in section_verdicts):
        out["verdict"] = "YELLOW"
    elif all(v in ("ok", "no_api", "degraded_ok", "within_budget")
             for v in section_verdicts):
        out["verdict"] = "GREEN"
    else:
        out["verdict"] = "YELLOW"
    over_budget = [s["name"] for s in sections if s.get("verdict") == "over_budget"]
    if over_budget:
        out["detail"] = f"over budget: {', '.join(over_budget)}"
    else:
        unknown = [f"{s['name']}={s.get('verdict')}"
                   for s in sections
                   if s.get("verdict") not in
                   ("ok", "no_api", "degraded_ok", "within_budget",
                    "over_budget", "degraded")]
        if unknown:
            out["detail"] = f"unknown verdict: {', '.join(unknown[:3])}"
        else:
            out["detail"] = (f"{len(sections)} sections · "
                             f"backend={data.get('backend')}")
    return out


def _read_backend_switch(dir_path: Path) -> dict:
    report = dir_path / "report.json"
    out = {"verdict": "UNKNOWN", "detail": None}
    if not report.exists():
        return out
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    parts = []
    worst = "GREEN"
    for key in ("minimax_to_ollama", "ollama_to_minimax"):
        block = data.get(key)
        if not block or not block.get("aggregate"):
            worst = "YELLOW"
            parts.append(f"{key}=MISSING")
            continue
        agg = block["aggregate"]
        v = agg.get("overall_verdict", "UNKNOWN")
        parts.append(
            f"{key}: p50={agg.get('p50_ms', 0):.0f}ms ({v})"
        )
        if v in ("YELLOW", "ALERT", "DEGRADED"):
            worst = "YELLOW" if v == "YELLOW" else "RED"
    out["verdict"] = worst
    out["detail"] = " · ".join(parts)
    return out


def _read_local_model_smoke(dir_path: Path) -> dict:
    report = dir_path / "report.json"
    out = {"verdict": "UNKNOWN", "detail": None}
    if not report.exists():
        return out
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    verdict_raw = (summary.get("verdict") or data.get("verdict")
                   or "UNKNOWN").upper()
    if verdict_raw in ("PASS", "GREEN"):
        out["verdict"] = "GREEN"
    elif verdict_raw in ("FAIL", "RED"):
        out["verdict"] = "RED"
    else:
        out["verdict"] = "YELLOW"
    out["detail"] = f"verdict={verdict_raw}"
    return out


def _read_dual_backend(dir_path: Path) -> dict:
    report = dir_path / "report.json"
    out = {"verdict": "UNKNOWN", "detail": None}
    if not report.exists():
        return out
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    overall = (data.get("verdict") or data.get("overall_verdict", "")).upper()
    if overall == "PASS":
        out["verdict"] = "GREEN"
    elif overall in ("FAIL", "DEGRADED", "RED"):
        out["verdict"] = "RED"
    else:
        out["verdict"] = "YELLOW"
    out["detail"] = f"verdict={overall or 'UNKNOWN'}"
    return out


DRILL_READERS = {
    "dress_rehearsal_": _read_dress_rehearsal,
    "integrated_timing_minimax_": _read_integrated_timing,
    "integrated_timing_ollama_": _read_integrated_timing,
    "backend_switch_drill_": _read_backend_switch,
    "local_model_smoke_": _read_local_model_smoke,
    "demo_rehearsal_dual_backend_": _read_dual_backend,
}


VERDICT_RANK = {"GREEN": 0, "YELLOW": 1, "RED": 2, "UNKNOWN": 1}

# Prefixes to merge into a single "best-of-2 backends" row.
# pitch 日只会选一个 backend（findings §5.1 推荐 Ollama 主路径），所以 overall
# 判定应取二者更 green 的那个，而不是把两个并列独立判定。
INTEGRATED_TIMING_MERGE = (
    "integrated_timing_ollama_",
    "integrated_timing_minimax_",
)


def _merge_best_of_integrated_timing(rows: list[dict]) -> list[dict]:
    """Collapse ollama + minimax integrated_timing rows into one best-of-2 row.

    - verdict: the greener of the two (GREEN > YELLOW > RED > UNKNOWN)
    - age: age of the winner
    - detail: lists both verdicts with a pointer to findings §5.1
    - label: "Integrated Timing (best-of-2 backends)"
    - If only one of the two exists (edge case), leave original rows alone.
    """
    by_prefix: dict[str, dict] = {}
    for r in rows:
        pfx = r.get("_prefix")
        if pfx in INTEGRATED_TIMING_MERGE:
            by_prefix[pfx] = r
    if len(by_prefix) != len(INTEGRATED_TIMING_MERGE):
        return rows
    ollama = by_prefix["integrated_timing_ollama_"]
    minimax = by_prefix["integrated_timing_minimax_"]
    ol_rank = VERDICT_RANK.get(ollama["verdict"], 1)
    mm_rank = VERDICT_RANK.get(minimax["verdict"], 1)
    winner, loser = (ollama, minimax) if ol_rank <= mm_rank else (minimax, ollama)
    merged_verdict = winner["verdict"]
    detail = (
        f"winner={winner['label'].split('·')[-1].strip()} {winner['verdict']} "
        f"· other={loser['label'].split('·')[-1].strip()} {loser['verdict']} "
        f"— pitch 日用 Ollama 主路径（findings §5.1）"
    )
    merged_row = {
        "label": "Integrated Timing (best-of-2 backends)",
        "run": winner["run"],
        "verdict": merged_verdict,
        "detail": detail,
        "age_h": winner["age_h"],
        "_prefix": "__merged_integrated_timing__",
    }
    out = [r for r in rows if r.get("_prefix") not in INTEGRATED_TIMING_MERGE]
    # Insert merged row at the position of the first integrated_timing row
    insert_at = next(
        (i for i, r in enumerate(rows)
         if r.get("_prefix") in INTEGRATED_TIMING_MERGE),
        len(out),
    )
    out.insert(insert_at, merged_row)
    return out


def collect_readiness(stale_hours: float) -> tuple[list[dict], int]:
    rows: list[dict] = []
    for prefix, label in DRILL_PREFIXES:
        run_dir = _latest_run_dir(prefix)
        if run_dir is None:
            rows.append({
                "label": label, "run": None, "verdict": "RED",
                "detail": "no artefact in runs/", "age_h": None,
                "_prefix": prefix,
            })
            continue
        age = _age_hours(run_dir)
        reader = DRILL_READERS.get(prefix)
        raw = reader(run_dir) if reader else {"verdict": "UNKNOWN",
                                              "detail": "no reader"}
        verdict = raw.get("verdict", "UNKNOWN")
        if age is not None and age > stale_hours and verdict == "GREEN":
            verdict = "YELLOW"
            raw["detail"] = (raw.get("detail") or "") + \
                f" · stale ({age:.1f}h > {stale_hours}h)"
        rows.append({
            "label": label, "run": run_dir.name, "verdict": verdict,
            "detail": raw.get("detail"), "age_h": age,
            "_prefix": prefix,
        })
    # Collapse ollama + minimax integrated_timing rows into best-of-2
    rows = _merge_best_of_integrated_timing(rows)
    # Compute overall worst after merge
    worst = max(
        (VERDICT_RANK.get(r["verdict"], 1) for r in rows),
        default=0,
    )
    return rows, worst


def render_scorecard(rows: list[dict], stale_hours: float,
                     worst: int) -> str:
    overall = ["GREEN", "YELLOW", "RED"][worst]
    icon = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "❌"}[overall]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Pre-Pitch Readiness Scorecard",
        "",
        f"- **Overall:** {icon} **{overall}**",
        f"- **Generated:** `{now}`",
        f"- **Staleness threshold:** {stale_hours}h",
        "",
        "## Dimension verdicts",
        "",
        "| Dimension | Verdict | Latest artefact | Age (h) | Detail |",
        "| --------- | ------- | --------------- | ------- | ------ |",
    ]
    verdict_icon = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "❌",
                    "UNKNOWN": "?"}
    for r in rows:
        age = f"{r['age_h']:.1f}" if r["age_h"] is not None else "—"
        run = r["run"] or "—"
        detail = (r["detail"] or "").replace("|", "\\|")
        lines.append(
            f"| {r['label']} | {verdict_icon[r['verdict']]} {r['verdict']} | "
            f"`{run}` | {age} | {detail} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- ✅ GREEN: artefact fresh, all sub-verdicts pass",
        "- ⚠️  YELLOW: stale (> threshold), degraded, or partial pass — still demo-able but investigate",
        "- ❌ RED: no artefact on disk OR drill reported failure — must re-run before pitch",
        "",
        "## Not covered by this scorecard",
        "",
        "- pytest suite (run `python3 -m pytest`)",
        "- adversarial 8/8 (run `python3 src/well_harness/static/adversarial_test.py`)",
        "- browser-level UI / Canvas rendering (manual eyeball)",
        "- network conditions at venue (manual check)",
        "",
        "See `docs/demo/preflight_checklist.md` for the complete 16-item T-0 list.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="P29 pre-pitch readiness aggregator")
    ap.add_argument("--stale-hours", type=float, default=24.0,
                    help="yellow warning if artefact older than this")
    ap.add_argument("--out", type=Path, default=None,
                    help="write scorecard to file (still prints to stdout)")
    args = ap.parse_args()

    rows, worst = collect_readiness(args.stale_hours)
    md = render_scorecard(rows, args.stale_hours, worst)
    sys.stdout.write(md)
    if args.out is not None:
        args.out.write_text(md, encoding="utf-8")
    return worst


if __name__ == "__main__":
    sys.exit(main())

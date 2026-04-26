"""E11-10 — Codex personas pipeline dispatch + collect tooling.

CLI helpers for the Tier-B / Tier-A persona review workflow:

    codex-persona dispatch <sub-phase> <persona> [--epic-dir DIR] [--model M]
        Run cx-auto 20 (account quota check) then codex exec on the
        persona prompt, streaming output to the canonical output path.

    codex-persona collect <sub-phase> <persona> [--epic-dir DIR]
        Parse the codex output file and emit a structured JSON summary
        with verdict, finding counts, tokens used, and a Tier-B
        acceptance bool.

    codex-persona next-persona [--epic-dir DIR]
        Read PERSONA-ROTATION-STATE.md and print the round-robin
        successor of the most recent Tier-B entry (P1->P2->...->P5->P1).

    codex-persona append-rotation <sub-phase> <persona> <tier> <reason>
        Append a one-line rotation entry in the canonical format.

This tool is stdlib-only. It does NOT replace human/Claude judgement on
prompt content, scope decisions, or merge gates — it just removes the
mechanical overhead (verdict regex parsing, round-robin arithmetic,
rotation-state templating) from each sub-phase loop.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EPIC_DIR = REPO_ROOT / ".planning" / "phases" / "E11-workbench-engineer-first-ux"
DEFAULT_MODEL = "gpt-5.4"
PERSONAS = ("P1", "P2", "P3", "P4", "P5")
VERDICTS = ("APPROVE", "APPROVE_WITH_NITS", "CHANGES_REQUIRED")
SEVERITIES = ("BLOCKER", "IMPORTANT", "NIT", "INFO")


@dataclass
class CollectResult:
    sub_phase: str
    persona: str
    output_path: str
    verdict: str | None
    finding_counts: dict[str, int]
    tokens_used: int | None
    tier_b_acceptance: bool
    notes: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


# ─── Persona prompt / output path helpers ────────────────────────────


def prompt_path(epic_dir: Path, sub_phase: str, persona: str) -> Path:
    return epic_dir / f"persona-{persona}-{sub_phase}-prompt.txt"


def output_path(epic_dir: Path, sub_phase: str, persona: str) -> Path:
    return epic_dir / f"persona-{persona}-{sub_phase}-output.md"


def rotation_state_path(epic_dir: Path) -> Path:
    return epic_dir / "PERSONA-ROTATION-STATE.md"


# ─── Verdict parser ──────────────────────────────────────────────────


_VERDICT_PATTERNS = [
    # Codex outputs verdicts in several styles:
    # 1. "**APPROVE_WITH_NITS**" on its own line
    # 2. "Verdict: APPROVE" inline
    # 3. "`APPROVE_WITH_NITS`" backticked
    re.compile(r"\*\*(APPROVE_WITH_NITS|APPROVE|CHANGES_REQUIRED)\*\*"),
    re.compile(r"`(APPROVE_WITH_NITS|APPROVE|CHANGES_REQUIRED)`"),
    re.compile(r"(?:^|\s)Verdict[:\s]+\*?\*?(APPROVE_WITH_NITS|APPROVE|CHANGES_REQUIRED)\*?\*?"),
    re.compile(r"(?:^|\n)(APPROVE_WITH_NITS|APPROVE|CHANGES_REQUIRED)(?:\s|$)"),
]


def parse_verdict(text: str) -> str | None:
    """Return the LAST verdict mention in the text, since codex tends to
    repeat the verdict at the bottom of its summary. Returns None if no
    verdict marker is found."""
    last_match = None
    for pattern in _VERDICT_PATTERNS:
        for match in pattern.finditer(text):
            verdict = match.group(1)
            if verdict in VERDICTS:
                if last_match is None or match.start() > last_match[1]:
                    last_match = (verdict, match.start())
    return last_match[0] if last_match else None


# Match `BLOCKER` / `IMPORTANT` / `NIT` / `INFO` only when used as a
# severity tag at the start of a finding bullet, not in surrounding prose
# (e.g., the word "important" in normal sentences). Codex outputs them
# inside backticks or at the start of a list item with a dash.
_FINDING_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:[-*]\s*)?`?(BLOCKER|IMPORTANT|NIT|INFO)`?\b"
)


def count_findings(text: str) -> dict[str, int]:
    """Count finding tags in the codex verdict block. Codex repeats the
    verdict block at the end of its output, so we de-duplicate by only
    counting in the LAST verdict block (everything after the last
    verdict marker)."""
    counts = {sev: 0 for sev in SEVERITIES}

    # Find the last verdict marker; count findings after that point only.
    last_verdict_pos = -1
    for pattern in _VERDICT_PATTERNS:
        for match in pattern.finditer(text):
            if match.group(1) in VERDICTS and match.start() > last_verdict_pos:
                last_verdict_pos = match.start()

    scan_text = text[last_verdict_pos:] if last_verdict_pos >= 0 else text

    for match in _FINDING_PATTERN.finditer(scan_text):
        sev = match.group(1)
        counts[sev] += 1
    return counts


_TOKENS_PATTERN = re.compile(r"tokens used\s*\n\s*(\d[\d,]*)", re.IGNORECASE)


def parse_tokens_used(text: str) -> int | None:
    """Codex emits `tokens used\\nNNNN` near end of session."""
    matches = list(_TOKENS_PATTERN.finditer(text))
    if not matches:
        return None
    return int(matches[-1].group(1).replace(",", ""))


def tier_b_accepts(verdict: str | None, finding_counts: dict[str, int]) -> bool:
    """Tier-B acceptance per constitution: 1/1 ∈ {APPROVE,
    APPROVE_WITH_NITS} AND BLOCKER == 0."""
    if verdict not in ("APPROVE", "APPROVE_WITH_NITS"):
        return False
    return finding_counts.get("BLOCKER", 0) == 0


def collect(epic_dir: Path, sub_phase: str, persona: str) -> CollectResult:
    out = output_path(epic_dir, sub_phase, persona)
    notes: list[str] = []
    if not out.exists():
        return CollectResult(
            sub_phase=sub_phase,
            persona=persona,
            output_path=str(out),
            verdict=None,
            finding_counts={sev: 0 for sev in SEVERITIES},
            tokens_used=None,
            tier_b_acceptance=False,
            notes=[f"output file does not exist: {out}"],
        )
    text = out.read_text(encoding="utf-8", errors="replace")
    verdict = parse_verdict(text)
    counts = count_findings(text)
    tokens = parse_tokens_used(text)
    if verdict is None:
        notes.append("no verdict marker found — codex may still be running")
    if tokens is None:
        notes.append("no `tokens used` marker found — codex output may be incomplete")
    return CollectResult(
        sub_phase=sub_phase,
        persona=persona,
        output_path=str(out),
        verdict=verdict,
        finding_counts=counts,
        tokens_used=tokens,
        tier_b_acceptance=tier_b_accepts(verdict, counts),
        notes=notes,
    )


# ─── Round-robin next-persona ────────────────────────────────────────


_ROTATION_LINE_PATTERN = re.compile(
    r"^E\d+-\w+:\s+Tier-(?:A|B)\s.*?Persona\s*=\s*(P[1-5])",
    re.MULTILINE,
)


def parse_rotation_state(text: str) -> list[str]:
    """Return the ordered list of personas from PERSONA-ROTATION-STATE.md.
    Tier-A entries are skipped per constitution: 'Rotation pointer
    unchanged' for Tier-A. Detect that suffix and skip those rows."""
    persona_sequence: list[str] = []
    for raw_line in text.splitlines():
        if "Tier-A" in raw_line and "Rotation pointer unchanged" in raw_line:
            continue
        match = _ROTATION_LINE_PATTERN.match(raw_line)
        if match:
            persona_sequence.append(match.group(1))
    return persona_sequence


def round_robin_successor(last: str) -> str:
    if last not in PERSONAS:
        raise ValueError(f"invalid persona: {last}; expected one of {PERSONAS}")
    idx = PERSONAS.index(last)
    return PERSONAS[(idx + 1) % len(PERSONAS)]


def next_persona(epic_dir: Path) -> str:
    state = rotation_state_path(epic_dir)
    if not state.exists():
        return "P1"  # Fresh epic — start at P1 per constitution.
    text = state.read_text(encoding="utf-8")
    sequence = parse_rotation_state(text)
    if not sequence:
        return "P1"
    return round_robin_successor(sequence[-1])


# ─── Rotation-state append helper ────────────────────────────────────


def append_rotation_entry(
    epic_dir: Path, sub_phase: str, persona: str, tier: str, reason: str
) -> str:
    if tier not in ("A", "B"):
        raise ValueError(f"tier must be 'A' or 'B', got {tier!r}")
    if persona not in PERSONAS:
        raise ValueError(f"invalid persona: {persona!r}")
    state = rotation_state_path(epic_dir)
    if not state.exists():
        raise FileNotFoundError(state)
    line = f"{sub_phase}: Tier-{tier} (Persona = {persona} — {reason})\n"
    with state.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return line


# ─── Dispatch (cx-auto + codex exec) ─────────────────────────────────


def dispatch(
    epic_dir: Path,
    sub_phase: str,
    persona: str,
    model: str = DEFAULT_MODEL,
    quota_threshold: int = 20,
    cx_auto_bin: str = "cx-auto",
    codex_bin: str = "codex",
) -> int:
    """Run cx-auto then codex exec. Returns the codex exit code.
    Streams codex output to the persona output file."""
    prompt = prompt_path(epic_dir, sub_phase, persona)
    if not prompt.exists():
        print(f"[dispatch] prompt missing: {prompt}", file=sys.stderr)
        return 2
    out = output_path(epic_dir, sub_phase, persona)

    # Step 1: account quota check (best-effort; cx-auto failure does not
    # block dispatch — codex itself will fail with a clear message).
    try:
        subprocess.run([cx_auto_bin, str(quota_threshold)], check=False)
    except FileNotFoundError:
        print(
            f"[dispatch] {cx_auto_bin} not on PATH — skipping account check",
            file=sys.stderr,
        )

    # Step 2: codex exec (synchronous; caller can wrap in &/nohup).
    prompt_text = prompt.read_text(encoding="utf-8")
    with out.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            [codex_bin, "exec", "--model", model, prompt_text],
            stdout=fh,
            stderr=subprocess.STDOUT,
        )
    return proc.returncode


# ─── CLI ─────────────────────────────────────────────────────────────


def _add_common_epic_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--epic-dir",
        type=Path,
        default=DEFAULT_EPIC_DIR,
        help=f"Epic planning directory (default: {DEFAULT_EPIC_DIR})",
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codex-persona", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dispatch = sub.add_parser("dispatch", help="cx-auto + codex exec")
    p_dispatch.add_argument("sub_phase", help="e.g. E11-15c")
    p_dispatch.add_argument("persona", choices=PERSONAS)
    p_dispatch.add_argument("--model", default=DEFAULT_MODEL)
    p_dispatch.add_argument("--quota-threshold", type=int, default=20)
    _add_common_epic_arg(p_dispatch)

    p_collect = sub.add_parser("collect", help="parse codex output → JSON")
    p_collect.add_argument("sub_phase")
    p_collect.add_argument("persona", choices=PERSONAS)
    _add_common_epic_arg(p_collect)

    p_next = sub.add_parser("next-persona", help="round-robin successor")
    _add_common_epic_arg(p_next)

    p_append = sub.add_parser("append-rotation", help="append rotation entry")
    p_append.add_argument("sub_phase")
    p_append.add_argument("persona", choices=PERSONAS)
    p_append.add_argument("tier", choices=["A", "B"])
    p_append.add_argument("reason", help="rationale for this persona pick")
    _add_common_epic_arg(p_append)

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "dispatch":
        return dispatch(
            args.epic_dir, args.sub_phase, args.persona, model=args.model,
            quota_threshold=args.quota_threshold,
        )
    if args.cmd == "collect":
        result = collect(args.epic_dir, args.sub_phase, args.persona)
        print(result.to_json())
        return 0 if result.tier_b_acceptance else 1
    if args.cmd == "next-persona":
        print(next_persona(args.epic_dir))
        return 0
    if args.cmd == "append-rotation":
        line = append_rotation_entry(
            args.epic_dir, args.sub_phase, args.persona, args.tier, args.reason
        )
        print(line, end="")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())

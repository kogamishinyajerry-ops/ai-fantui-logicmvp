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


_TOKENS_MARKER = re.compile(r"(?:^|\n)tokens used\s*\n\s*\d", re.IGNORECASE)


def _final_verdict_block(text: str) -> str:
    """Return only the text AFTER the last `tokens used\\nNNNN` marker.

    E11-10 R2 final-fix: codex's session-tail layout is reliably:
        codex
        <real narrative response with verdict + findings>
        tokens used
        <token-count number>
        <CANONICAL clean verdict block — repeated for downstream consumers>

    Parsing the post-tokens-used block avoids ALL of these earlier-noise
    sources that can false-match the parser:
      - prompt echo (`Return one of: **APPROVE** / ...`)
      - codex's own quoted source code listings
      - probe output (e.g., `collect` JSON dumped during codex's review)
      - mid-stream verdict speculation

    If `tokens used` is absent, codex hasn't completed — return empty
    string so callers see verdict=None + tier_b_acceptance=False.
    """
    matches = list(_TOKENS_MARKER.finditer(text))
    if not matches:
        return ""
    last = matches[-1]
    # Skip past the number on the line after "tokens used".
    after_marker = text[last.end():]
    # Drop the rest of the digit line.
    newline_after_number = after_marker.find("\n")
    if newline_after_number >= 0:
        return after_marker[newline_after_number + 1:]
    return ""


def parse_verdict(text: str) -> str | None:
    """Return the verdict from the post-tokens-used canonical block.

    The FIRST verdict marker in the post-tokens block is codex's canonical
    declaration. Later occurrences inside finding-evidence text (e.g.,
    "Live probe: `**APPROVE_WITH_NITS**` plus ...") must be ignored.

    Falls back to whole-text LAST-match scan if there is no `tokens used`
    marker, so legacy / partial inputs still extract *something* — but
    `collect()` will mark such results as not-yet-acceptable via the
    completeness gate.
    """
    block = _final_verdict_block(text)
    if block:
        # Post-tokens block: first verdict wins (canonical declaration).
        first_match = None
        for pattern in _VERDICT_PATTERNS:
            for match in pattern.finditer(block):
                verdict = match.group(1)
                if verdict in VERDICTS:
                    if first_match is None or match.start() < first_match[1]:
                        first_match = (verdict, match.start())
        return first_match[0] if first_match else None

    # Fallback (incomplete output): legacy last-wins scan.
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
# (e.g., the word "important" in normal sentences). Codex emits them in
# multiple decorated forms:
#   - bare:        `- BLOCKER finding`
#   - backticked:  `- \`BLOCKER\` finding`
#   - bold:        `- **BLOCKER** finding`
#   - bold+backtick combos: `- **\`BLOCKER\`** finding`
# E11-10 R2 BLOCKER #2 closure (P1 finding): the bold form was missed,
# silently zeroing BLOCKER counts and false-passing tier_b_accepts.
_FINDING_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:[-*]\s*)?(?:\*\*)?`?(?:\*\*)?(BLOCKER|IMPORTANT|NIT|INFO)(?:\*\*)?`?(?:\*\*)?\b"
)


def count_findings(text: str) -> dict[str, int]:
    r"""Count finding tags in the codex post-tokens-used canonical block.

    The post-tokens-used block is codex's clean tail copy. Within it,
    findings are bullet-anchored (`- \`BLOCKER\` ...`) so the existing
    `_FINDING_PATTERN`'s newline anchor avoids matching inline-quoted
    severity tags inside finding evidence text.

    For completeness when `tokens used` is absent (incomplete output),
    fall back to the legacy after-last-verdict-marker scoping on the
    whole text.
    """
    counts = {sev: 0 for sev in SEVERITIES}
    block = _final_verdict_block(text)
    if block:
        scan_text = block
    else:
        # Legacy fallback: scope to after the last verdict marker.
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


# MUST share the same column-0 anchor as `_TOKENS_MARKER` so completeness
# detection and post-tokens scoping agree on the boundary. R2-R3 closure
# (P1 R2 BLOCKER): allowing `parse_tokens_used` to match leading-whitespace
# variants while `_TOKENS_MARKER` required column-0 created a false-pass
# path — `collect()` would mark the file authoritative but the verdict
# parser would silently fall back to whole-file scan.
_TOKENS_PATTERN = re.compile(r"(?:^|\n)tokens used\s*\n\s*(\d[\d,]*)", re.IGNORECASE)


def parse_tokens_used(text: str) -> int | None:
    """Codex emits `tokens used\\nNNNN` at column 0 near end of session.
    The column-0 anchor MUST stay in sync with `_TOKENS_MARKER` so the
    completeness gate and the post-tokens scoping share the same
    boundary."""
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
    # E11-10 R2 BLOCKER #1 closure (P1 finding): a partial output file
    # (one-line `Verdict: APPROVE`, fenced code-block quote, or codex
    # mid-stream) must NOT pass tier_b_acceptance. Codex emits the
    # `tokens used\nNNNN` marker exactly once at the end of a session;
    # absence ⇒ output incomplete ⇒ verdict is not authoritative.
    output_complete = tokens is not None
    if verdict is None:
        notes.append("no verdict marker found — codex may still be running")
    if tokens is None:
        notes.append(
            "no `tokens used` marker found — codex output may be incomplete; "
            "tier_b_acceptance forced to false"
        )
    return CollectResult(
        sub_phase=sub_phase,
        persona=persona,
        output_path=str(out),
        verdict=verdict,
        finding_counts=counts,
        tokens_used=tokens,
        tier_b_acceptance=output_complete and tier_b_accepts(verdict, counts),
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
    """Append a canonical rotation entry. Tier-A entries automatically
    receive the `Rotation pointer unchanged` suffix that
    `parse_rotation_state` requires to skip them — this keeps `append`
    and `next-persona` semantics in sync.

    E11-10 R2 IMPORTANT closure (P1 finding): without this suffix, a
    Tier-A row appended via this function would silently consume the
    rotation pointer because parse_rotation_state would treat it as a
    normal Tier-A row that must be counted.
    """
    if tier not in ("A", "B"):
        raise ValueError(f"tier must be 'A' or 'B', got {tier!r}")
    if persona not in PERSONAS:
        raise ValueError(f"invalid persona: {persona!r}")
    state = rotation_state_path(epic_dir)
    if not state.exists():
        raise FileNotFoundError(state)
    if tier == "A":
        line = (
            f"{sub_phase}: Tier-A (Persona = {persona} — {reason}). "
            "All 5 personas dispatched. Rotation pointer unchanged.\n"
        )
    else:
        line = f"{sub_phase}: Tier-B (Persona = {persona} — {reason})\n"
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

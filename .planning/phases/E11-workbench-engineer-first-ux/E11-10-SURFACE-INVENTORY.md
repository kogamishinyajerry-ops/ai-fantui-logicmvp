# E11-10 Surface Inventory — codex personas pipeline tooling

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Pure-tooling sub-phase: removes the mechanical overhead from each
> Tier-B/Tier-A persona-review loop (verdict regex parsing, round-robin
> arithmetic, rotation-state templating, account-quota dispatch).

## Motivation

Across E11-08, E11-15, E11-15b, E11-15c, and E11-11, the per-sub-phase
review loop has the same ~10 manual steps:

1. Read `PERSONA-ROTATION-STATE.md` to derive next persona
2. Write `persona-{P}-{sub-phase}-prompt.txt`
3. `cx-auto 20`
4. `codex exec --model gpt-5.4 "$PROMPT" > output.md 2>&1` (background)
5. Wait for completion
6. Read 80–150-line output, scan for `**APPROVE**` / `BLOCKER` / etc.
7. Manually count finding severities
8. Decide Tier-B acceptance
9. Optionally close IMPORTANT pre-merge
10. Append `PERSONA-ROTATION-STATE.md` entry

Steps 1, 6, 7, 8, and 10 are mechanical. E11-10 tools them.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | `tools/codex_persona_dispatch.py` CLI with 4 subcommands | [NEW] | `tools/codex_persona_dispatch.py` | dispatch / collect / next-persona / append-rotation. Stdlib-only, ~310 LOC. |
| 2 | `tests/test_codex_persona_dispatch.py` — 34 tests | [NEW] | `tests/test_codex_persona_dispatch.py` | Verdict parser, finding counter, tokens parser, round-robin, rotation-state parse + roundtrip, end-to-end collect. |

## Subcommand contracts

### `dispatch <sub-phase> <persona> [--model M] [--quota-threshold N]`

Reads `persona-{persona}-{sub-phase}-prompt.txt`, runs
`cx-auto <quota-threshold>` (best-effort, non-blocking), then
`codex exec --model <model> "$prompt"`, streaming stdout+stderr to
`persona-{persona}-{sub-phase}-output.md`. Returns codex's exit code.

### `collect <sub-phase> <persona>` → JSON

Parses the persona output file and emits structured JSON:

```json
{
  "sub_phase": "E11-11",
  "persona": "P5",
  "output_path": "...",
  "verdict": "APPROVE_WITH_NITS" | "APPROVE" | "CHANGES_REQUIRED" | null,
  "finding_counts": {"BLOCKER": 0, "IMPORTANT": 1, "NIT": 1, "INFO": 1},
  "tokens_used": 127979,
  "tier_b_acceptance": true,
  "notes": []
}
```

Exit code 0 if Tier-B acceptance met, 1 otherwise. Notes contain
diagnostics when the codex output is incomplete (no verdict marker, no
tokens marker).

### `next-persona`

Reads `PERSONA-ROTATION-STATE.md`, returns the round-robin successor of
the most recent Tier-B entry. Tier-A entries with the canonical
"Rotation pointer unchanged" suffix are skipped per constitution.
Returns "P1" when the file is missing or empty (fresh epic).

### `append-rotation <sub-phase> <persona> <tier> <reason>`

Appends one canonical entry to `PERSONA-ROTATION-STATE.md`. Validates
persona ∈ {P1..P5} and tier ∈ {A, B}.

## Verdict-parser robustness

The codex output format varies. The parser handles:
- `**APPROVE_WITH_NITS**` (bold)
- `\`APPROVE_WITH_NITS\`` (backticked)
- `Verdict: APPROVE` (inline)
- `APPROVE` on a line by itself

Codex repeats its verdict block at the end of the output. The parser
returns the LAST verdict mention so a stale earlier one doesn't surface.
Finding counting also de-duplicates by only counting after the LAST
verdict marker.

The parser was validated against real session data:

```
$ python3 tools/codex_persona_dispatch.py collect E11-11 P5
{
  "verdict": "APPROVE_WITH_NITS",
  "finding_counts": {"BLOCKER": 0, "IMPORTANT": 1, "NIT": 1, "INFO": 1},
  "tokens_used": 127979,
  "tier_b_acceptance": true,
  ...
}
```

This matches the manual parse of P5 E11-11 output exactly.

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 0 (pure tooling)
- **[REWRITE/DELETE] count** = 0

→ **Tier-B** (1-persona review).

> **Verdict: Tier-B**. Persona = **P1 (Junior FCS Engineer)** —
> round-robin successor of E11-11's P5 AND content-fit: small focused
> tooling with regression-risk concerns (regex parsing, round-robin
> arithmetic, file-system side-effects) is exactly P1's lens.

## Behavior contract (locked by tests)

`tests/test_codex_persona_dispatch.py` (NEW, 34 tests):

1. `parse_verdict` — 6 tests covering all 4 marker styles, last-wins
   ordering, missing-verdict, CHANGES_REQUIRED
2. `count_findings` — 4 tests covering verdict-block scoping,
   bullet-form, last-block de-dup, clean-approve safety
3. `tier_b_accepts` — 5 parametrized cases covering APPROVE,
   APPROVE_WITH_NITS, BLOCKER-fails, CHANGES_REQUIRED, missing-verdict
4. `parse_tokens_used` — 3 tests covering canonical, missing, multi-match
5. `round_robin_successor` — 3 tests covering forward, wrap, invalid
6. `parse_rotation_state` — 2 tests covering Tier-A skip + empty
7. `next_persona` — 4 tests including end-to-end against real
   E11-15c PERSONA-ROTATION-STATE.md
8. `append_rotation_entry` — 3 tests including roundtrip + validation
9. `collect` — 4 tests including blocker fail, missing output, in-progress

## Truth-engine red line

Files touched:
- `tools/codex_persona_dispatch.py` — NEW (~310 LOC, stdlib-only)
- `tests/test_codex_persona_dispatch.py` — NEW (34 tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-10-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, any HTML/CSS/JS, `demo_server.py`.
Truth-engine boundary preserved. The new tool is read-only against the
production codebase; it only writes to `.planning/phases/.../*.md` files
and codex output streams.

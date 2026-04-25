# Codex Persona Review Pipeline

> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
> Date: 2026-04-25
> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6

## Purpose

5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape.

**Anti-bias model (governance bundle #2, 2026-04-25):**
- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.

See §Tier-trigger below for which tier fires when.

## Persona inventory

| ID | Persona | File |
|---|---|---|
| P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
| P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
| P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
| P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
| P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |

## Invocation

### Tier-trigger

> **Canonical rule definition lives in `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger.** This document does not redefine or paraphrase the rule. To know which tier fires, when to fire it, who selects the Tier-B persona, what the rollback condition is, or how to compute "copy diff ≥ 10 行" — read constitution. This README's only role in the rule layer is to point.
>
> History: governance bundle #2 (2026-04-25 PR #14) softened the prior 5-persona default. Decision arc: `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.

### 命令模板

```bash
# Tier-A（5 persona 并行，仅在条件满足时跑）：
for p in P1 P2 P3 P4 P5; do
  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    "$(cat .planning/codex_personas/${p}-*.md)" \
    > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
done
wait

# Tier-B（1 persona）：PERSONA-ROTATION-STATE.md 是唯一 source of truth。
#
# Step 1 — Read state file last entry (or "" if file empty / new epic):
STATE_FILE=.planning/phases/<epic>/PERSONA-ROTATION-STATE.md
LAST=$(tail -1 "$STATE_FILE" 2>/dev/null | grep -oE 'P[1-5]' || echo "")
#
# Step 2 — Compute default = round-robin successor of last (P1 if empty):
case "$LAST" in
  P1) DEFAULT=P2 ;; P2) DEFAULT=P3 ;; P3) DEFAULT=P4 ;;
  P4) DEFAULT=P5 ;; P5) DEFAULT=P1 ;; *)  DEFAULT=P1 ;;
esac
#
# Step 3 — Choose path (uncomment exactly ONE of 3a or 3b):
#
# Step 3a (DEFAULT path): take the round-robin successor as-is.
PERSONA=$DEFAULT
#
# Step 3b (OVERRIDE path): owner writes a non-default P-value motivated by
# sub-phase content (e.g., demo-arc-heavy → P3; 适航 trace heavy → P4).
# To use, comment out Step 3a above and uncomment exactly one literal line below:
# PERSONA=P1   # demo-not-applicable
# PERSONA=P2   # senior FCS deep code review
# PERSONA=P3   # demo-arc-heavy sub-phase
# PERSONA=P4   # 适航 trace / V&V heavy sub-phase
# PERSONA=P5   # customer-facing / triage scenario
#
# Hard constraint enforced by rule layer (must hold for both paths):
[ "$PERSONA" = "$LAST" ] && { echo "ERROR: PERSONA=$PERSONA equals LAST=$LAST — violates no-consecutive-repeat"; exit 1; }
#
# Step 4 — Run the chosen persona:
cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
  "$(cat .planning/codex_personas/${PERSONA}-*.md)" \
  > .planning/phases/<phase-id>/persona-${PERSONA}-output.md 2>&1
#
# Step 5 — Append the new entry to the state file (canonical write):
echo "<phase-id>: ${PERSONA} (<reason — round-robin | content-fit-override>)" >> "$STATE_FILE"
```

## Output convention

Each persona writes verdict to its own file. Closure semantics depend on which tier ran:

### Tier-A（5-persona 并行）

Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:

- 5 verdicts side-by-side
- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
- 0 BLOCKER is a phase-CLOSURE precondition

### Tier-B（1-persona 默认）

No aggregator runs (single verdict file = the review record). Closure precondition collapses to:

- 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
- Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
- 0 BLOCKER from that single persona is the phase-CLOSURE precondition
- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.

If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.

## Anti-bias safeguard

**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
2. Triggers re-run with sharpened persona contexts
3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework

**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).

## Cost / latency baseline (recorded for retro)

**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).

**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.

If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

# Codex Persona Review Pipeline

> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
> Date: 2026-04-25
> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6

## Purpose

5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).

## Persona inventory

| ID | Persona | File |
|---|---|---|
| P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
| P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
| P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
| P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
| P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |

## Invocation

```bash
# all 5 in parallel (recommended for review batch):
for p in P1 P2 P3 P4 P5; do
  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    "$(cat .planning/codex_personas/${p}-*.md)" \
    > .planning/phases/E11-workbench-engineer-first-ux/persona-${p}-output.md 2>&1 &
done
wait

# single persona (debugging persona quality):
cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
  "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
  > .planning/phases/E11-workbench-engineer-first-ux/persona-P1-output.md 2>&1
```

## Output convention

Each persona writes verdict to its own file. Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:

- 5 verdicts side-by-side
- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
- 0 BLOCKER is a phase-CLOSURE precondition

## Anti-bias safeguard

If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
2. Triggers re-run with sharpened persona contexts
3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework

## Cost / latency baseline (recorded for retro)

PR #5 R1 single Codex review: ~10min wall, ~187k tokens consumed. 5 parallel personas baseline expectation: ~10min wall (parallel), ~1M tokens (5 × 200k). If real numbers exceed by ≥50%, log a retro entry.

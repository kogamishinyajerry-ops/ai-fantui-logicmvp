# E11-13 Surface Inventory — manual_feedback_override UI trust-affordance

> Date: 2026-04-25
> Branch: `feat/e11-13-manual-feedback-trust-affordance-20260425`
> Sub-phase spec: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §3 row E11-13
> Per v2.3 §UI-COPY-PROBE §Surface Inventory + v2.4 §Recursive Coherence Drift Mitigation

## Header

`UI-Copy-Probe: 7 claims swept (7 anchored / 0 planned / 0 deleted)`
`copy_diff_lines=190 (insertions=189, deletions=1)`

Tier-trigger evaluation per `constitution.md §Codex Persona Pipeline Tier-Trigger`:

- (a) copy_diff_lines ≥ 10 → **YES** (190)
- (b) §Surface Inventory ≥ 3 [REWRITE/DELETE] → **NO** (0 — all 7 rows are pure additions, no rewrite/delete)
- Tier-trigger result: **Tier-B** (1 persona, per `PERSONA-ROTATION-STATE.md` SSOT — see `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md`)

## Inventory table

| # | Surface | Claim text | Anchor | Status |
|---|---------|-----------|--------|--------|
| 1 | Topbar chip label | "Feedback Mode" (chip eyebrow) | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode chip span) | [ANCHORED] |
| 2 | Topbar chip value | "Manual (advisory)" (chip strong) | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode chip strong) | [ANCHORED] |
| 3 | Topbar chip tooltip | "Manual feedback override is advisory — truth engine readings remain authoritative." | `src/well_harness/static/workbench.html:30-40` (#workbench-feedback-mode title attribute) | [ANCHORED] |
| 4 | Trust banner heading | "Manual feedback mode is advisory." | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner body strong) | [ANCHORED] |
| 5 | Trust banner explanation | "Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative. Your manual feedback is recorded for diff/review but does not change source-of-truth values." | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner body span) | [ANCHORED] |
| 6 | Trust banner dismiss button | "Hide for session" | `src/well_harness/static/workbench.html:46-65` (#workbench-trust-banner button) | [ANCHORED] |
| 7 | Truth-engine alt label | "Truth Engine" (chip strong when mode=truth_engine) | `src/well_harness/static/workbench.js:setFeedbackMode()` (mode === "truth_engine" branch) | [ANCHORED] |

## No-rewrite confirmation

`git diff main..HEAD -- 'src/well_harness/static/*.{html,js,css}' | grep -E '^-[^-]' | grep -v '^---'` returns no user-facing string deletions; every change is an addition. Counting `^-` lines: 1 (the topbar grid-template-columns CSS rule rewrite — non-user-facing layout token, not copy).

## Truth-affordance claim accuracy

The banner asserts: "Truth engine readings (logic gates L1–L4, controller dispatch, audit chain) remain authoritative. Your manual feedback is recorded for diff/review but does not change source-of-truth values."

Verification basis (per E11-00-PLAN §3 row E11-13 + Opus 4.7 reframe 2026-04-25):
- 873 default-lane tests + adversarial 8/8 already prove truth-engine is not actually breached when `feedback_mode = manual_feedback_override`
- E11-13 is a UI affordance fix (visualization layer), NOT an authority-chain breach fix
- No code change in `controller.py` / `runner.py` / `models.py` / `adapters/` (red-line maintained)
- E11-14 (server-side guard, follow-up) will add the actual endpoint check; E11-13 is UI-only honesty about what override means right now

## Cross-doc references resolved

- Tier-trigger rule: `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger` (canonical, governance bundle #2 landed 2026-04-25 PR #14)
- v2.3 §Surface Inventory mandate: `.planning/constitution.md §UI-COPY-PROBE`
- v2.4 §Recursive Coherence Drift Mitigation: `.planning/constitution.md §Recursive Coherence Drift Mitigation` (governance-bundle PR #15 landed 2026-04-25, but E11-13 is NOT a rule-bundle PR — no constitution rule body changes, no cross-doc pointers added)

## Drift acceptance (none required)

E11-13 is a regular code PR with all-anchored claims; no drift-acceptance declaration needed.

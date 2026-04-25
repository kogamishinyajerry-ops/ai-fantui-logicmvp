# E11-14 Surface Inventory — manual_feedback_override server-side role guard

> Date: 2026-04-25
> Branch: `feat/e11-14-manual-feedback-server-guard-20260425`
> Sub-phase spec: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §3 row E11-14
> Per v2.3 §UI-COPY-PROBE §Surface Inventory + governance bundle #2 §Codex Persona Pipeline Tier-Trigger

## Header

`UI-Copy-Probe: 1 claim swept (1 anchored / 0 planned / 0 deleted)`
`copy_diff_lines=12 (insertions=12, deletions=0)`

Tier-trigger evaluation per `constitution.md §Codex Persona Pipeline Tier-Trigger`:

- (a) copy_diff_lines ≥ 10 → **YES** (12)
- (b) §Surface Inventory ≥ 3 [REWRITE/DELETE] → **NO** (0 — sole user-visible surface is the 409 error message; no copy rewrites/deletes)
- Tier-trigger result: **Tier-B** (1 persona, per `PERSONA-ROTATION-STATE.md` — round-robin successor of E11-13 (P1) = **P2 Senior FCS Engineer**)

## Inventory table

| # | Surface | Claim text | Anchor | Status |
|---|---------|-----------|--------|--------|
| 1 | 409 error remediation message | "manual_feedback_override requires actor + ticket_id + manual_override_signoff. Acquire sign-off via Approval Center, or switch to auto_scrubber." | `src/well_harness/demo_server.py:_validate_manual_override_signoff()` reject() helper | [ANCHORED] |

## Why only 1 row

E11-14 is primarily a server-side guard, not a UI copy change. The only new user-visible string is the 409 error response's `remediation` field. Demo / test fixture sign-off fields are payload data, not user-facing copy. No banner / chip / button / label changes.

## Truth-affordance claim accuracy

The 409 response asserts: "manual_feedback_override requires actor + ticket_id + manual_override_signoff. Acquire sign-off via Approval Center, or switch to auto_scrubber."

Verification basis:
- Rule enforced in `_validate_manual_override_signoff()` — exactly the 3 required fields named (actor / ticket_id / manual_override_signoff)
- Approval Center referenced exists in workbench shell DOM (`#approval-center-entry` per workbench.html, locked by E11-09 dual-route test)
- "switch to auto_scrubber" maps to LEVER_FEEDBACK_MODES set member (`auto_scrubber` is the canonical alternative)

## Cross-doc references resolved

- Tier-trigger rule: `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger` (canonical, governance bundle #2 PR #14 landed 2026-04-25)
- v2.3 §Surface Inventory mandate: `.planning/constitution.md §UI-COPY-PROBE`
- v2.4 §Recursive Coherence Drift Mitigation: `.planning/constitution.md §Recursive Coherence Drift Mitigation` (PR #15 landed 2026-04-25). E11-14 is NOT a rule-bundle PR (no constitution rule body changes) — v6.1 Hard Stop ≥4 applies.

## Drift acceptance (none required)

E11-14 has 1 anchored claim; no drift-acceptance declaration needed. R-budget cap = v6.1 Hard Stop ≥4.

## Adapter-boundary red line

E11-14 modifies only:
- `src/well_harness/demo_server.py` (HTTP handler + parser; not a controller)
- `src/well_harness/static/demo.js` (client payload fields; not a controller invocation)
- `src/well_harness/static/adversarial_test.py` (test scaffolding)
- `tools/demo_path_smoke.py` (smoke harness)
- `tests/conftest.py` + `tests/test_*.py` (test fixtures + new guard test file)

Files NOT touched (per E11-00-PLAN §3 row E11-14 + red line at bottom of §3):
- `src/well_harness/controller.py` ✓
- `src/well_harness/runner.py` ✓
- `src/well_harness/models.py` ✓
- `src/well_harness/adapters/` ✓
- `tests/e2e/test_wow_a*` ✓

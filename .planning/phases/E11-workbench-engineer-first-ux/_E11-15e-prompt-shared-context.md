# E11-15e — shared context for Tier-A persona prompts

**Repo:** `kogamishinyajerry-ops/ai-fantui-logicmvp`
**Branch:** `feat/e11-15e-tier-a-chinese-first-bundle-20260426`
**PR:** #30
**HEAD:** `83d69e4`
**Tier:** A (copy_diff_lines ~38, REWRITE rows = 22; per constitution Tier-A iff ≥10 lines AND ≥3 REWRITE)
**Round-robin lead:** P3 (successor of E11-15d's P2)

## What E11-15e ships

Bilingualizes 22 user-visible English-only surfaces on `/workbench` enumerated by P2 during the E11-15d Tier-B review (`tests/test_workbench_approval_flow_polish.py:189-194`).

**Pattern:** `<中文> · <English>` everywhere; English suffix preserved verbatim so prior substring locks (test_workbench_trust_affordance, test_workbench_authority_banner, test_workbench_role_affordance, test_workbench_column_rename, test_workbench_state_of_world_bar) keep passing without contract churn.

## Files in scope

- `src/well_harness/static/workbench.html` — 21 REWRITE strings
- `src/well_harness/static/workbench.js` — 1 lockstep edit at line 3788 (feedback-mode chip dynamic text, both `truth_engine` and `manual_feedback_override` branches bilingualized)
- `tests/test_workbench_e11_15e_chinese_first_bundle.py` — 67 new test cases (positive bilingual locks + stale-English negative guards + English-suffix preservation + structural anchors + JS lockstep + live-served route + truth-engine red-line guard)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-15e-SURFACE-INVENTORY.md` — full surface table + out-of-scope deferred list (Section 3) + truth-engine red line + lockstep impact + persona dispatch plan

## Files explicitly NOT in scope (truth-engine red line)

`controller.py`, `runner.py`, `models.py`, `src/well_harness/adapters/`, `demo_server.py`. The new lockstep guard `test_e11_15e_does_not_touch_truth_engine_backend` scans these 4 backend files for any of the 23 Chinese display strings introduced in this sub-phase.

## Verification baseline

- 67/67 new tests pass
- 188/188 prior workbench tests pass (lockstep contracts preserved)
- 1221/1221 full suite passes (0 regressions, 35 deselected per default markers)

## Surface honesty pledge

E11-15e closes 22 surfaces. It does **NOT** close "the last" or "all". Deferred surfaces are listed in SURFACE-INVENTORY Section 3 (`<option>` system values, post-hydration JS boot status, `<pre>` phase-arrow flow diagram, eyebrow column tags, identifier sigils). The deferred list is **non-exhaustive**.

## Codex degradation contingency

If your account hits secondary-window throttle / token-refresh failure, the project memory rule "Executor 即 Gate (v3.2 治理折叠)" authorizes Claude Code Opus 4.7 to self-sign the Tier-A gate (documented in SURFACE-INVENTORY Section 6). Self-sign requires standard 1221-test green + repo-honesty self-review (already met).

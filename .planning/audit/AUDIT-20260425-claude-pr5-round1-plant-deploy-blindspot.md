# PR #5 Round 1 — Claude Plant-Deploy Blind-Spot Audit

> Authored by: Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> Date: 2026-04-25
> Governance regime: v6.1 Solo Autonomy Delegation (DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT)
> Scope: methodology calibration — *not* a code defect

## 0. Preamble — why this document exists

In PR #5 (commit `b6ca262`, "fix(wow-a): align Step 2 with post-a46e4e6 auto_scrubber reality"), I authored a coordinated test-doc update under Kogami's `[B]` directive on PR #4's inherited-blocker investigation. Codex review (round 1, 2026-04-25, account `ksnbdajdjddkdd@gmail.com`) returned `CHANGES_REQUIRED` with **2 IMPORTANT findings, both pointing to the same factual error**: my BEAT_EARLY narration claimed the plant reaches "~6% deploy" for `tra_deg=-5`, but Codex empirically probed `lever_snapshot_payload(tra_deg=-5, feedback_mode='auto_scrubber')` and observed `deploy_position_percent == 0.0`.

The fix landed verbatim in commit `ff9a126` (4 LOC across 2 files), satisfying the v6.0 verbatim-exception 5 conditions. PR #5 was Gate-Approved on commit `ff9a126` (post-rebase = `c13cb78`) and merged to main at `1258574` on 2026-04-25.

This audit logs **the methodology miss that produced the wrong claim**, so v6.1 Solo Autonomy can add the corresponding self-trigger heuristic to the Codex-call decision tree.

## 1. The miss — what I claimed vs. what was true

**My claim** (in PR #5 head `b6ca262`, both `tests/e2e/test_wow_a_causal_chain.py` file-level comment and `docs/demo/wow_a_causal_chain.md` §3 Step 1):

> BEAT_EARLY (tra_deg=-5) → logic1 + logic2 active; the canonical pullback is short for non-deep TRA so plant only reaches ~6% deploy and logic3/4 remain inactive.

**Reasoning I used (mental model, not verified):**
- canonical_pullback_sequence with `tra_deg=-5` returns ~2 final-hold ticks (the post-`a46e4e6` `else` branch keeps `final_repeats = 2`)
- `step_s` default ≈ 0.1s, `deploy_rate_percent_per_s` default ≈ 30%/s
- → 2 ticks × 0.1s × 30%/s = ~6% deploy

**What Codex actually observed by probing the running demo_server:**

```
lever_snapshot_payload(tra_deg=-5, feedback_mode='auto_scrubber') →
  time_s = 0.9
  deploy_position_percent = 0.0
  active = {logic1, logic2}
```

**Why my mental model was wrong:** I forgot that `plant.advance(plant_state, outputs, config.step_s)` (in `_simulate_lever_state`) is **gated by `outputs.pdu_motor_cmd`**, which is `explain.logic3.active`. With `tra_deg=-5` *above* the L3 threshold (`logic3_tra_deg_threshold` ≈ -12°), `logic3.active` is False, so `pdu_motor_cmd` is False, so the plant's `advance()` keeps `deploy_position_percent` at 0 regardless of how many ticks the canonical pullback runs.

The "30%/s × 2 ticks" arithmetic was correct **in isolation** but vacuous because the rate term was zero (no motor command).

## 2. Why Codex caught it and I didn't

Codex's tool log shows it ran an inline Python script:

```python
# (paraphrased from Codex stdout, full log in /tmp/codex_review_stdout.log)
from well_harness.demo_server import lever_snapshot_payload
snap = lever_snapshot_payload(tra_deg=-5, feedback_mode='auto_scrubber', ...)
print(snap['plant_state'].deploy_position_percent, snap['time_s'])
# → 0.0, 0.9
```

It probed the **actual runtime** before signing off on a docstring claim. I propagated my mental model into prose without booting the server.

## 3. v6.1 Solo Autonomy heuristic update

**New self-trigger rule (effective 2026-04-25):**

> **EMPIRICAL-CLAIM-PROBE rule.** Before writing prose (test docstring, file-level comment, demo doc, PR description) that contains a *specific numeric* claim about server-side runtime behavior — e.g. "plant deploys to N%", "~Ks of sim time", "~M ticks", "logic-X activates after Y" — Claude Code MUST do one of:
>
> 1. boot the relevant code path locally and capture the actual output (one-line probe is enough), OR
> 2. surface the claim as a *hypothesis* with a `TODO(probe-before-merge)` marker, OR
> 3. cite the source commit + line where the number is *defined* (not *implied*).
>
> Mental-model-only arithmetic is forbidden when the prose will land in a regression-locked test or a customer-facing demo doc. Codex round 1 catching one of these is a calibration miss; round 2 catching two on the same PR is a Tier-2 self-pass-rate violation.

This rule is added to the v6.1 Notion governance page (Page 11 §v6.1) in a follow-up sync.

## 4. Self-pass-rate calibration

| Round | My pre-submit self-estimate | Codex outcome | Calibration |
|---|---|---|---|
| PR #5 R1 | not declared (gap) | CHANGES_REQUIRED, 2 IMPORTANT, 1 cluster | should have been ≤80% — not declaring is itself the issue |

**Going forward (v6.1):** every PR opening prose that includes a numeric runtime claim ships with `external_gate_self_estimated_pass_rate: <0..1>` in the PR body so Codex round-1 outcomes can be calibrated against pre-submit confidence.

## 5. What this audit does NOT do

- Does not propose any code change to controller.py / 19-node / 4 gates / adapters / wow_a fixture (truth-engine red lines).
- Does not retroactively revise PR #5 (already merged, fix already in `c13cb78`).
- Does not blame Codex for being thorough — the round-1 catch was net-positive and the verbatim closure flow worked exactly as v6.0 intends.

## 6. Cross-references

- DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT (Notion 04 决策日志) — v6.1 authorization
- PR #4: `docs/workbench/inherited-logic4-blocker-investigation.md` — the bisect → `a46e4e6` analysis
- PR #5: `tests/e2e/test_wow_a_causal_chain.py` (lines 32-42) + `docs/demo/wow_a_causal_chain.md` §3 — the corrected narration
- This audit: `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`
- Notion Page 11 (模型分工与联合开发强制规则) §v6.1 — to be patched with §EMPIRICAL-CLAIM-PROBE rule in the same Sequence as this commit

---

Execution-by: claudecode-opus47 · v6.1 · solo-autonomy

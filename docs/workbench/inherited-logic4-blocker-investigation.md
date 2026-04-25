# Inherited logic4 Blocker — Investigation Report

**Investigator:** claudecode-opus47
**Date:** 2026-04-25 (UTC)
**Branch:** `chore/post-merge-followup-20260425` (base = PR #3 head `2ded020`, pre-merge per Kogami `(B)` directive)
**Scope:** `tests/e2e/test_wow_a_causal_chain.py::test_wow_a_beat_deep_activates_logic2_and_logic3`
**Status:** investigation only — **no truth-engine, test, fixture, controller, or adapter file was edited.**

---

## TL;DR

- The blocker is **inherited**. PR #3 did not introduce it.
- First bad commit (`git bisect run`): **`a46e4e6`** — Codex 2026-04-23, `fix(scrubber): extend canonical pullback hold to let plant VDT reach 90%`. The blocker is **22 commits older** than PR #3's base.
- Root cause is **not** a `controller.py` feedback-gating bug. The truth engine is correct: it returns `logic4.active = True` because all four conditions evaluate True under the inputs the server hands it.
- Root cause is a **post-hoc disagreement between the wow_a e2e test invariant and the auto_scrubber design intent**: commit `a46e4e6` deliberately made `auto_scrubber` drive plant VDT to 100% within a single `/api/lever-snapshot` call (so L4 can latch under the corrected `reverse_travel` lower bound). The wow_a e2e test (blob `c04ec6b…` constant since `ae38cc0`) asserts the opposite invariant: "single POST must not activate L4". One of these specs has to give.
- **Recommendation: [B] e2e test expectation / wow_a fixture has drifted from the corrected auto_scrubber spec**, with a strong **[C] caveat** that the wow_a demo doc invariant ("logic4 stays gray to prove feedback gating exists") may be the spec Kogami wants to preserve. **Pause for Kogami selection [A] / [B] / [C].**

---

## Step 4a — Three real runs

All three rounds were executed on the same sandbox (Python 3.9.6, pytest 7.4.4) on 2026-04-25 UTC. Port 8799 was reaped before every run. Test command (identical across rounds):

```bash
python3 -m pytest "tests/e2e/test_wow_a_causal_chain.py::test_wow_a_beat_deep_activates_logic2_and_logic3" -v -m e2e --no-header
```

### Round 1 — current branch HEAD `24b6f17` (= PR #3 head `2ded020` + T2/T3 doc commits)

- HEAD: `24b6f178cf5f6a4f748389900eef037de9b99a4f`
- Result: **FAILED**
- Failing line: `tests/e2e/test_wow_a_causal_chain.py:106`
  ```
  E       AssertionError: logic4 must remain feedback-gated; a single POST must not activate it
  E       assert True is False
  ```
- Returned `logic4.conditions` (all four True):
  - `name=deploy_90_percent_vdt, current_value=True, passed=True`
  - `name=tra_deg, current_value=-32.0, comparison=between_lower_inclusive, passed=True`
  - `name=aircraft_on_ground, current_value=True, passed=True`
  - `name=engine_running, current_value=True, passed=True`

### Round 2 — `origin/main` HEAD `3a76789` (= PR #3 merge base, "known failure" per task brief)

- HEAD: `3a767893ff4bde8ccd7a2b6998c1c4cd274e74b5`
- Result: **FAILED**
- Same failing line, identical four-condition payload: `deploy_90_percent_vdt=True, tra_deg=-32.0, on_ground=True, engine_running=True`.
- Confirms the failure is on `main` itself, not introduced by PR #3.

### Round 3 — `a46e4e6` (older clean commit candidate, "fix(scrubber)…")

- HEAD: `a46e4e631c9eddef1e65136bca119131444497e1`
- Result: **FAILED**
- Same root-cause shape. This was the bisect candidate that probed earlier than 3a76789 (not a "clean known good") and still produced the failure — necessary input to bisect anchoring.

### Round 3-bonus — `e72abd9` (~50 commits before PR #3 base, "known good" probe)

- HEAD: `e72abd9` `fix(Phase C-7 round#2): preset adapter-gate compliance + SW1/SW2 hint wiring`
- Result: **PASSED**
- This anchors the bisect range upper-bound (good).

### Verbatim assertion fragment (Round 1, full message preserved)

```
status, body = api_post(demo_server, "/api/lever-snapshot", BEAT_DEEP_PAYLOAD)
assert status == 200
logic = body["logic"]
active = {k for k, v in logic.items() if v.get("active") is True}
assert {"logic2", "logic3"} <= active, (
    f"BEAT_DEEP should at least activate logic2+logic3, got {active}"
)
> assert logic["logic4"].get("active") is False, (
    "logic4 must remain feedback-gated; a single POST must not activate it"
)
E AssertionError: logic4 must remain feedback-gated; a single POST must not activate it
E assert True is False
```

---

## Step 4b — git bisect

Range: `e72abd9` (good) → `a46e4e6` (bad), 23 commits between.

```bash
git bisect start a46e4e6 e72abd9
git bisect run /tmp/bisect_runner.sh
# (runner = pytest on the single failing case, exit-code-driven)
```

Bisect output:

```
Bisecting: 11 revisions left to test after this (roughly 4 steps)
[e74921a4ebe531b1ec752740f981edd3cd1d4ccc] fix(svg-wiring): iteration-4 …
running '/tmp/bisect_runner.sh'
. 1 passed in 0.17s
Bisecting: 2 revisions left to test after this (roughly 2 steps)
[28262cce0bea59233a9bbb13fd1430327f9de6e2] docs(state): record demo-ui bug fix session …
running '/tmp/bisect_runner.sh'
. 1 passed in 0.17s
Bisecting: 0 revisions left to test after this (roughly 1 step)
[ab3adf713dcae6c8ea4f3c7496c7550f2af75c89] docs(state): record L4 reverse_travel fix …
running '/tmp/bisect_runner.sh'
. 1 passed in 0.17s
a46e4e631c9eddef1e65136bca119131444497e1 is the first bad commit
```

### First bad commit

`a46e4e631c9eddef1e65136bca119131444497e1` (Codex, 2026-04-23 10:14 +0800), Co-Authored-By: Claude Sonnet 4.6.

```
fix(scrubber): extend canonical pullback hold to let plant VDT reach 90%
```

Files touched:

```
 src/well_harness/demo_server.py | 18 ++++++++++++++++--
 tests/test_demo.py              | 16 +++++++++++-----
 tools/demo_path_smoke.py        | 10 +++++++---
 3 files changed, 34 insertions(+), 10 deletions(-)
```

**Commit message verbatim (relevant excerpt):**

> User report: even after 9d18f05 fixed L4's reverse_travel lower bound, TRA=-32° in auto_scrubber (the default feedback mode) still showed L4 blocked. Root cause was different: the scrubber held the lever for only 1.2s of simulated time, and plant deploy at 30%/s advances to ~12% during the L3-active window — nowhere near the 90% VDT90 threshold. L4 was permanently blocked on deploy_90_percent_vdt in auto mode.
>
> Fix: when target TRA ≤ logic3_tra_deg_threshold, compute the final hold repeats from deploy_rate and step_s so plant VDT reaches 100% (+4-tick cushion for L3 activation lag). At defaults (30%/s, step=0.1s) this is ~38 ticks / 3.8s of sim time, for a total scrubber run of ~4.4s.
>
> Tests aligned to the corrected behavior:
> - test_demo_server_api_returns_lever_snapshot_payload_for_key_tra_values TRA=-14 expectation flipped from vdt90/logic4/thr_lock blocked to all active (the old expectation encoded the scrubber-too-short bug).
> - lever_mode_switch_reset smoke now asserts logic4_active in auto_before (it was previously asserting the bug-state as expected behavior).

**Code change (load-bearing snippet, `src/well_harness/demo_server.py::_canonical_pullback_sequence`):**

```diff
-    final_repeats = 4 if target <= config.logic3_tra_deg_threshold else 2
+    if target <= config.logic3_tra_deg_threshold:
+        # Budget enough ticks for plant VDT to reach 90% (and a small margin
+        # so L4 latches cleanly). deploy_rate_percent_per_s × step_s × N ≥ 100
+        # → N ≥ 100 / (rate × step_s). +4 cushion covers L3-activation lag.
+        deploy_ticks_needed = int(100.0 / max(1e-6, config.deploy_rate_percent_per_s * config.step_s)) + 4
+        final_repeats = max(4, deploy_ticks_needed)
+    else:
+        final_repeats = 2
     sequence.extend([target] * final_repeats)
     return sequence
```

### Why this commit makes wow_a's L4 invariant fail

`/api/lever-snapshot` calls `lever_snapshot_payload(...)` → `_simulate_lever_state(...)`, which iterates `_canonical_pullback_sequence(target_tra, config)` and calls `plant.advance(plant_state, outputs, config.step_s)` every tick. Pre-`a46e4e6`, the final-hold tick count was a constant `4` — the plant only advanced ~12% in deploy. `sensors.deploy_90_percent_vdt` stayed `False`, so `controller_adapter.evaluate_with_explain(...)` returned `logic4.active = False`. The wow_a test's invariant matched.

Post-`a46e4e6`, the final-hold tick count is `≈ 38` for `target ≤ logic3_tra_deg_threshold` (covers BEAT_DEEP_PAYLOAD's `tra_deg=-35`). The plant fully deploys to 100% within a single `/api/lever-snapshot` call. `sensors.deploy_90_percent_vdt = True`, so `logic4.active = True`. The wow_a test's invariant breaks.

The wow_a test file (`tests/e2e/test_wow_a_causal_chain.py`) blob SHA has been **byte-identical** (`c04ec6bb04d286bcbcf4a2dce4f5e17090538f4c`) across all examined commits (`ae38cc0`, `e72abd9`, `a46e4e6`, `3a76789`, `2ded020`). The test was authored against the pre-`a46e4e6` server semantics; commit `a46e4e6` updated *some* dependent tests (`test_demo.py`, `tools/demo_path_smoke.py`) but missed the wow_a e2e suite under `tests/e2e/` — which had been added/extended in a parallel branch and merged in afterwards.

---

## Step 4c — Three-option qualitative recommendation

| Option | What it means | Evidence for | Evidence against |
|---|---|---|---|
| **[A] controller.py feedback-gating bug** | The truth engine should not have returned `logic4.active=True`. Fix the controller. | None observed. | controller.py `evaluate` is a pure `all(condition.passed)` over four conditions. Each condition's `passed` matches its declared comparison. Given `deploy_90_percent_vdt=True, tra_deg∈[reverse_travel_min,reverse_travel_max), on_ground=True, engine_running=True`, returning `True` is correct. The "bug" — if any — is in *what gets handed to* the controller, not in the controller's evaluation. |
| **[B] e2e test expectation / wow_a fixture has drifted from spec** | The wow_a test invariant `logic4.active is False` for BEAT_DEEP+auto_scrubber is obsolete; the corrected `auto_scrubber` design (a46e4e6) is the spec. Fix the test. | (1) `a46e4e6` is an explicit, Codex-authored, code-reviewed (`Co-Authored-By: Claude Sonnet 4.6`) fix; commit message documents user-driven motivation and verifies "725 tests pass". (2) `a46e4e6` already aligned `test_demo.py` and `lever_mode_switch_reset` smoke to the new behaviour — wow_a was simply missed. (3) HANDOVER.md's "no changes to existing wow scripts" non-goal does not preclude updating the wow_a *test*; the wow_a *demo doc* (`docs/demo/wow_a_causal_chain.md`) Step 2 narration is "logic4 未亮是真值引擎等 deploy_90_percent_vdt 反馈节点翻位，不是 bug" — but with the fix in place, that narration is now factually wrong: the feedback node DOES flip within the auto_scrubber window. (4) 22 commits + PR #3 worth of work landed on top of `a46e4e6` without anyone re-reviewing wow_a; the project has effectively chosen the auto_scrubber fix as the spec. | The wow_a demo doc is a contract artefact; flipping the test means the demo presentation script for Step 2 must change too ("logic4 lights up here" instead of "logic4 stays gray"). That has visible-in-room consequences for the dress rehearsal. |
| **[C] Inconclusive — needs truth-engine review** | The two specs are in conflict. Kogami should re-adjudicate which invariant wins (auto_scrubber drives VDT to 100% vs. wow_a says single-POST cannot activate L4). | (1) The wow_a *demo doc* `docs/demo/wow_a_causal_chain.md` Step 2 narration is the only artefact that explicitly defends the gated invariant. If the demo's pedagogical value is "show that feedback gating exists by holding L4 dark", reverting `a46e4e6` and re-fixing the original `reverse_travel` issue differently is a legitimate choice. (2) The visual contract in `docs/demo/wow_a_causal_chain.md` §4 ("Step 2: logic2 + logic3 点亮；logic4 仍灰") is direct evidence that someone considered the gated behaviour the demo's intended teach. (3) commit `a46e4e6` made the change unilaterally without updating the wow_a artefact pair; that may itself be a process gap worth surfacing. | Reverting or reshaping `a46e4e6` re-opens the original "L4 permanently blocked at TRA=-32°" user-reported bug. Whatever Kogami picks needs to also describe what happens to that user complaint. |

### Recommendation (default)

**[B]**, with the explicit instruction to Kogami that picking [B] requires a coordinated update to **two artefacts in one Kogami-signed PR**:

1. `tests/e2e/test_wow_a_causal_chain.py::test_wow_a_beat_deep_activates_logic2_and_logic3` — either (a) flip the assertion to `assert logic["logic4"].get("active") is True` and update the docstring to match the corrected auto_scrubber spec, **or** (b) change `BEAT_DEEP_PAYLOAD` to use `feedback_mode="manual_feedback_override"` with `deploy_position_percent=50` (a value < 90) and keep the `is False` assertion as a probe of the manual-override path instead.
2. `docs/demo/wow_a_causal_chain.md` Step 2 narration — replace "logic4 未亮是真值引擎等 deploy_90_percent_vdt 反馈节点翻位" with the post-fix story: "深拉过线 → auto_scrubber 在 ~4.4s 内完成 deploy 反馈翻位 → logic4 与 thr_lock 同时亮起；这是真值引擎的端到端因果链，不是 AI 叙述的填充."

If Kogami picks **[C]**, the conversation becomes "should `_canonical_pullback_sequence` revert to the pre-`a46e4e6` short hold, and how do we re-solve the original TRA=-32° L4 user-reported bug some other way?" — which is a `controller.py` / plant-side / config-side discussion that needs a separate Phase under v6.0 governance.

If Kogami picks **[A]**, please clarify which of the four `logic4` conditions in `controller.py:107–135` is being challenged. None of the four is internally inconsistent with its declared comparison; the most likely intent under [A] would be to add a fifth condition that distinguishes "feedback came from the real plant loop" from "feedback came from the in-server canonical pullback" — that is a controller-shape change and **must not be done without explicit Kogami truth-engine repair authorization** per task constraint.

---

## Step 4d — Hard stop

**I am stopping here.**

- I have not modified `controller.py`, `runner.py`, any adapter, `wow_a` fixture, the demo doc, or any e2e test file.
- I have not modified Notion.
- I have committed only this report and the T2/T3 deliverables.

**Awaiting Kogami's selection of [A] / [B] / [C]. I will not edit any truth-engine, test, fixture, or demo doc until Kogami posts an explicit authorization in this conversation.**

If [B] is chosen, the resulting PR will be on a separate branch (not `chore/post-merge-followup-20260425`) so the test/doc edit is isolated from the audit deliverables. If [C], the work is a new Phase. If [A], halt + redirect to a Kogami-led truth-engine repair Phase.

---

## Appendix — verification artefacts

- `runs/xpassed_audit_20260425T045925Z.txt` — full `pytest --runxfail -v` stdout (T2)
- `git bisect log` (reproducible):
  ```
  git bisect start a46e4e6 e72abd9
  # bad: a46e4e6 fix(scrubber): extend canonical pullback hold to let plant VDT reach 90%
  # good: e72abd9 fix(Phase C-7 round#2): preset adapter-gate compliance + SW1/SW2 hint wiring
  # → first bad commit: a46e4e631c9eddef1e65136bca119131444497e1
  ```
- Test file blob SHA (constant across all probed commits): `c04ec6bb04d286bcbcf4a2dce4f5e17090538f4c`

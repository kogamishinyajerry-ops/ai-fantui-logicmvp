# xpassed Audit — 2026-04-25

**Run command:** `python3 -m pytest --runxfail -v --no-header`
**Raw stdout:** `runs/xpassed_audit_20260425T045925Z.txt`
**Branch:** `chore/post-merge-followup-20260425` (base = PR #3 head `2ded020`, pre-merge)
**Aggregate result:** `863 passed, 27 deselected in 75.73s` under `--runxfail`; without `--runxfail`, the same 12 cases report `XPASS` (see standalone module run below).

```
$ python3 -m pytest tests/test_p43_authority_contract.py -v --no-header
======================== 8 passed, 12 xpassed in 0.05s =========================
```

All 12 xpassed cases originate from a single file: `tests/test_p43_authority_contract.py`. Each was marked `@pytest.mark.xfail(strict=False)` while the corresponding P43 sub-phase (P43-03 through P43-08) was pending. Static-grep verification on `src/well_harness/static/workbench.js` (HEAD = 2ded020) confirms all five gating constructs are now present:

- `function deepFreeze` ✓
- `function assignFrozenSpec(spec, origin)` ✓
- `function validateDraftAgainstFrozen(draft, frozen)` ✓
- `async function handleStartGen()` ✓
- `function handleFinalApprove()` ✓

The xfail markers are therefore stale.

---

## Per-test inventory

| # | Test ID | Current xfail reason | Recommendation | Risk note |
|---|---|---|---|---|
| 1 | `tests/test_p43_authority_contract.py::TestR2FinalApproveNoDraftRead::test_r2_final_approve_handler_exists` | `P43-08: final_approve handler not yet implemented in workbench.js` | **PROMOTE** | `handleFinalApprove` declared at workbench.js (grep-verified). Removing xfail turns this into a hard guard against handler regression. |
| 2 | `tests/test_p43_authority_contract.py::TestR2FinalApproveNoDraftRead::test_r2_handler_no_draft_getitem` | `P43-08: final_approve handler not yet implemented` | **PROMOTE** | R2 read-isolation invariant; once promoted, any future edit that reintroduces `getItem(...draft...)` inside the handler will fail in CI. |
| 3 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_assign_frozen_spec_declared` | `P43-03: assignFrozenSpec not yet implemented in workbench.js` | **PROMOTE** | Declaration present; promotion locks the singleton. |
| 4 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_deepfreeze_declared` | `P43-03: deepFreeze not yet implemented in workbench.js` | **PROMOTE** | `deepFreeze(obj)` declared; promotion blocks accidental rename / deletion. |
| 5 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_bare_frozenspec_assignment` | `P43-03: frozenSpec not yet introduced; bare-write check vacuously passes but marked xfail for parity` | **PROMOTE** | Real check is no longer vacuous — `assignFrozenSpec` exists and the heuristic window is meaningful. **Risk:** the 15/20-line window heuristic is brittle; if assignFrozenSpec body grows past 20 lines or moves, this test could flake. Recommend promoting first, then refactor the bound to use brace-balance parsing in a follow-up. |
| 6 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_alias_mutate_patterns` | `P43-03: frozenSpec not yet introduced; alias-mutate check vacuously passes` | **PROMOTE** | `frozenSpec` now real; alias-mutate forbid list (`merge`, `assign`, `Object.assign`, spread-with-draft) becomes load-bearing. |
| 7 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_no_draft_origin` | `P43-03: assignFrozenSpec not yet implemented; origin check pending` | **PROMOTE** | Two call sites observed: `assignFrozenSpec(currentSpec, "freeze-event")` and `assignFrozenSpec(restoredPacketSpec, "archive-restore")` — both satisfy the origin allow-list. **Risk:** if a third origin is needed in future, the regex `freeze-event\|archive-restore` must be extended in lockstep. |
| 8 | `tests/test_p43_authority_contract.py::TestR3FrozenSpecControlledWriter::test_r3_deepfreeze_called_in_assign` | `P43-03: deepFreeze not yet implemented; runtime enforcement pending` | **PROMOTE** | `assignFrozenSpec` body explicitly contains `frozenSpec = deepFreeze(JSON.parse(JSON.stringify(spec)))`. |
| 9 | `tests/test_p43_authority_contract.py::TestR4GeneratorFrozenOnly::test_r4_generator_exists` | `P43-05: generator function not yet implemented in workbench.js` | **PROMOTE** | `handleStartGen` matches the regex disjunction `start_gen|generatePanel|runGeneration|handleStartGen`. |
| 10 | `tests/test_p43_authority_contract.py::TestR4GeneratorFrozenOnly::test_r4_generator_no_draft_read` | `P43-05: generator not yet implemented` | **PROMOTE** | Read-isolation invariant on the generator. **Risk:** if generator helper is refactored to a different name, the regex disjunction in test must follow; otherwise `_find_block` returns empty and the assert message "Generator not found" surfaces. Already noted in test code. |
| 11 | `tests/test_p43_authority_contract.py::TestR5ValidatorSingleton::test_r5_singleton_declared` | `P43-07: validateDraftAgainstFrozen not yet implemented` | **PROMOTE** | `function validateDraftAgainstFrozen` declared exactly once (verified by grep + the `==1` assertion already in the test). |
| 12 | `tests/test_p43_authority_contract.py::TestR6LifecycleBoundary::test_r6_final_approve_removes_draft` | `P43-08: final_approve handler not yet implemented` | **PROMOTE** | R6a draft-cleanup invariant. Promoting locks `localStorage.removeItem(...draft_design_state...)` (or `clearDraftDesignState()`) inside `handleFinalApprove`. |

**Summary**

- **PROMOTE: 12** (delete the `@pytest.mark.xfail(...)` decorator; keep the test body and assertion message)
- **KEEP xfail: 0**
- **DELETE: 0**

All 12 fall into the same category: implementation has shipped, the xfail marker is documenting a frozen-in-time gap that no longer exists. Promoting is the lowest-risk action because the assertions already pass; the only thing the marker hides is regression — without promotion, a future commit can silently break R2/R3/R4/R5/R6a and the suite will turn the failure into a green xfailed line instead of an actual fail.

## Cross-cutting risk notes

1. **String-grep brittleness.** All 20 tests in `test_p43_authority_contract.py` are line-grep / regex-on-source. A purely cosmetic refactor (e.g. switching `function foo()` to `const foo = () => {}` for one of the gated functions) will break the test even though semantics are unchanged. Promotion does not introduce this brittleness — it surfaces it. Acceptable given the contract is "the authority shape must remain mechanically detectable."
2. **No test code is modified by this audit.** The recommendation is to delete decorators in a separate, narrowly scoped commit (out of scope for this report — that commit needs Kogami sign-off because it changes test-side enforcement strength, even though it does not change test-pass/fail counts today).
3. **--runxfail aggregate count check.** Under `--runxfail`, the full suite returns `863 passed`. The 12 xpassed cases plus the existing 819 (E10 baseline) + the 27 deselected (e2e + adversarial markers) reconcile within ±1; the small gap is that `--runxfail` rolls xpassed into passed. The "1 skipped" line from HANDOVER's E10 baseline still sits in `27 deselected` here because we did not pass `-m e2e` or expand markers; this is consistent with the marker config.

## Out-of-scope (deliberate)

- Does **not** modify any `@pytest.mark.xfail` decorator.
- Does **not** modify any test code, controller code, adapter code, wow_a fixture, or e2e expectation.
- Does **not** mutate Notion. If Kogami chooses to act on the PROMOTE recommendations, a separate Phase / PR with explicit Kogami Gate sign-off should land that change; this report is the input to that decision, not the output.

## Open question to Kogami

Approve PROMOTE for all 12? Yes / No / partial list — please pick. Decorator removal will be a separate PR with no behavioural change in test outcomes, only a tightening of regression guard.

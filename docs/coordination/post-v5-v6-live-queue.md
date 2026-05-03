# Post-v5 v6 Live Queue

Status: active queue · live Linear `JER-230` seeded · live Linear `JER-232` dispatched

## Purpose

Post-v5 work must dispatch from live Linear issues, not from repo-local
historical JER labels alone. This document seeds the first executable v6 queue
after the merged Workbench v5 foundation and records the next candidate slices
in a form that Codex/Symphony can turn into live Linear issues.

## Live Issue

- Live Linear issue: `JER-230`
- Title: `[project] [L9] [none] [DAL-TBD] Post-v5 v6 live queue seed`
- URL: `https://linear.app/jerrykogami/issue/JER-230/project-l9-none-dal-tbd-post-v5-v6-live-queue-seed`
- Project: `AI FANTUI LogicMVP · Codex Daily Lane`

Identifier rule:

- `live Linear JER-230` is not the same artifact as the repo-local historical
  `JER-230` empty-canvas graph authoring slice.
- Future reports must write `live Linear JER-230` or `repo-local JER-230` when
  the distinction matters.

## Execution Policy

1. Run `linear_awcp.py discover --team-key JER` before implementation.
2. Select one eligible live Linear issue per Codex run.
3. Keep `truth_effect: none` for sandbox/workbench artifacts unless a separate
   truth-gate issue explicitly changes the boundary.
4. Keep `src/well_harness/controller.py`, frozen adapters, certified hardware
   YAML, and C919 reference packets read-only.
5. Publish Linear proof comments after validation; do not paste raw logs,
   secrets, or implicit state transitions.

## Candidate v6 Issues

Recommended first product slice:

1. `[project] [L4] [none] [DAL-TBD] Review archive library and recent restore surface`
   - Outcome: make post-v5 review archives reusable from `/workbench` by
     surfacing recent sandbox archives and reusing the existing restore
     validation/readback path.
   - Acceptance: recent archives are listed with checksum/manifest status;
     one archive can be restored into the workbench through the existing
     sandbox import path; restore evidence remains `truth_effect: none`.
   - Boundaries: no controller truth, no certified hardware YAML, no live
     Linear mutation from the browser, no e2e 49/49 or mypy-clean claim.
   - Evidence: focused browser smoke for recent-list -> restore -> readback,
     schema/static tests for archive metadata, validation-suite targeted pass.

Recommended first debt slice:

2. `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche`
   - Outcome: reduce the official mypy strict baseline without claiming full
     clean until `tools/run_mypy_gate.py` reports `pass`.
   - Acceptance: one coherent module family is typed or shielded; the official
     wrapper reports fewer actionable errors or an explicit unchanged blocker;
     PR proof remains honest.
   - Boundaries: no runtime behavior changes unless required by typing fixes;
     no broad refactor; no mypy-clean claim unless the full gate passes.
   - Evidence: focused pytest for touched modules, `run_mypy_gate.py
     --format json --report-only`, validation-suite targeted pass.

Queue infrastructure slice:

3. `[project] [L9] [none] [DAL-TBD] Live Linear issue factory and collision guard`
   - Outcome: make live Linear issue creation less ad hoc by adding a repo-local
     documented issue template or helper wrapper that marks live Linear ids
     separately from repo-local historical labels.
   - Acceptance: new live issue templates include Outcome, Acceptance,
     Boundaries, Evidence Required, Repository, Desired state, and Agent
     eligible metadata; collision language is explicit.
   - Boundaries: no autonomous agent spawning, no state transitions, no secret
     persistence.
   - Evidence: dry-run output, Linear discover proof, docs validation.

Gate-hardening slice:

4. `[project] [L9] [none] [DAL-TBD] Official e2e 49/49 readiness audit`
   - Outcome: turn the current `not_claimed` e2e status into a concrete issue
     map: passing subset, failing subset, blockers, and next minimal fix.
   - Acceptance: the audit names the command, pass/fail counts, first blocker,
     and a follow-up issue recommendation; no UI/product behavior is changed.
   - Boundaries: audit-only unless a separate implementation issue is created;
     do not rewrite e2e tests to hide failures.
   - Evidence: captured command summary, blocker classification, Linear proof.

Scale/proof slice:

5. `[project] [L6] [none] [DAL-TBD] Large sandbox graph trace stability probe`
   - Outcome: prove the v5 runner/debug/archive loop remains deterministic on a
     larger sandbox graph before adding more UI polish.
   - Acceptance: synthetic graph trace is stable across repeated runs; archive
     checksums are deterministic; invalid graph findings remain structured.
   - Boundaries: sandbox-only; no adapter/controller truth changes; no
     performance certification claim.
   - Evidence: deterministic trace tests, archive checksum tests, targeted
     validation-suite pass.

## Recommended Next Dispatch

Start with the product slice:

`[project] [L4] [none] [DAL-TBD] Review archive library and recent restore surface`

Reason: Workbench v5 ended with archive restore proof. The next useful v6 move
is to make that proof reusable from the actual workbench surface before adding
new editing features. This preserves the single-user, sandbox-only v5 boundary
and creates a visible engineering workflow improvement.

Dispatch record:

- Live Linear issue: `JER-231`
- URL: `https://linear.app/jerrykogami/issue/JER-231/project-l4-none-dal-tbd-review-archive-library-and-recent-restore`
- State after PR #224: `Done`
- Identifier rule: `live Linear JER-231` is not the same artifact as the
  repo-local historical `JER-231` canonical graph document v2 slice.

Next infrastructure dispatch:

- Live Linear issue: `JER-232`
- Title: `[project] [L9] [none] [DAL-TBD] Live Linear issue factory and collision guard`
- URL: `https://linear.app/jerrykogami/issue/JER-232/project-l9-none-dal-tbd-live-linear-issue-factory-and-collision-guard`
- State at dispatch: `In Progress`
- Identifier rule: `live Linear JER-232` is not the same artifact as the
  repo-local historical `JER-232` port drag wiring slice.
- Repo artifact: `docs/coordination/live-linear-issue-factory.md`

# Post-v5 v6 Live Queue

Status: active queue · live Linear `JER-236` closed · live Linear `JER-237` refreshing next dispatch map

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

## Closed Dispatches Through JER-236

Product dispatch:

- Live Linear issue: `JER-231`
- Title: `[project] [L4] [none] [DAL-TBD] Review archive library and recent restore surface`
- URL: `https://linear.app/jerrykogami/issue/JER-231/project-l4-none-dal-tbd-review-archive-library-and-recent-restore`
- State after PR #224: `Done`
- Identifier rule: `live Linear JER-231` is not the same artifact as the
  repo-local historical `JER-231` canonical graph document v2 slice.

Infrastructure dispatch:

- Live Linear issue: `JER-232`
- Title: `[project] [L9] [none] [DAL-TBD] Live Linear issue factory and collision guard`
- URL: `https://linear.app/jerrykogami/issue/JER-232/project-l9-none-dal-tbd-live-linear-issue-factory-and-collision-guard`
- State after PR #225: `Done`
- Identifier rule: `live Linear JER-232` is not the same artifact as the
  repo-local historical `JER-232` port drag wiring slice.
- Repo artifact: `docs/coordination/live-linear-issue-factory.md`

Quality-debt dispatch:

- Live Linear issue: `JER-233`
- Title: `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche`
- URL: `https://linear.app/jerrykogami/issue/JER-233/project-l9-none-dal-tbd-jer-171-mypy-baseline-reduction-tranche`
- State after PR #226: `Done`
- Identifier rule: `live Linear JER-233` is not the same artifact as the
  repo-local historical `JER-233` scenario test case library slice.
- Evidence target: type one coherent module family, keep focused behavior tests
  green, and reduce the official wrapper baseline without claiming full mypy
  clean. First tranche evidence: live issue factory helper/tests are focused
  strict-mypy clean, and `tools/run_mypy_gate.py --format json --report-only`
  run with the declared `typecheck` extra reports 4665 errors in 326 files
  instead of the captured 4672 errors in 327 files.

Gate audit dispatch:

- Live Linear issue: `JER-234`
- Title: `[project] [L9] [none] [DAL-TBD] Official e2e 49/49 readiness audit`
- URL: `https://linear.app/jerrykogami/issue/JER-234/project-l9-none-dal-tbd-official-e2e-4949-readiness-audit`
- State after PR #227: `Done`
- Identifier rule: `live Linear JER-234` is not the same artifact as the
  repo-local historical `JER-234` sandbox runner trace kernel v2 slice.
- Evidence target: record the real opt-in e2e command, selected-test count,
  first blocker, and follow-up recommendation without changing product
  behavior. The audit found 90 passed / 1 failed / 3439 deselected and created
  the JER-235 follow-up.

Gate-fix dispatch:

- Live Linear issue: `JER-235`
- Title: `[project] [L4] [none] [DAL-TBD] Enable captured template insertion after draft import`
- URL: `https://linear.app/jerrykogami/issue/JER-235/project-l4-none-dal-tbd-enable-captured-template-insertion-after-draft`
- State after PR #228: `Done`
- Identifier rule: `live Linear JER-235` is not the same artifact as the
  repo-local historical `JER-235` debug probe timeline v3 slice.
- Evidence target: import `component_library.captured_templates`, enable the
  captured-template insert flow, preserve remapped ids/rules, and rerun the
  full opt-in e2e command. PR #228 closed with 91 passed / 3439 deselected.

Scale/proof dispatch:

- Live Linear issue: `JER-236`
- Title: `[project] [L6] [none] [DAL-TBD] Large sandbox graph trace stability probe`
- URL: `https://linear.app/jerrykogami/issue/JER-236/project-l6-none-dal-tbd-large-sandbox-graph-trace-stability-probe`
- State after PR #229: `Done`
- Identifier rule: `live Linear JER-236` is not the same artifact as the
  repo-local historical `JER-236` hardware/interface evidence attachment v2
  slice.
- Evidence target: prove a 16-node sandbox graph produces deterministic trace
  kernels and stable archive checksums, and prove a 12-node invalid graph keeps
  structured unsupported-op, duplicate-edge, and dangling-edge findings. PR
  #229 closed with 93 passed / 3439 deselected in the full opt-in e2e suite.

Current queue refresh:

- Live Linear issue: `JER-237`
- Title: `[project] [L9] [none] [DAL-TBD] Post-JER-236 v6 queue refresh and next dispatch map`
- URL: `https://linear.app/jerrykogami/issue/JER-237/project-l9-none-dal-tbd-post-jer-236-v6-queue-refresh-and-next`
- State at dispatch: `In Progress`
- Identifier rule: `live Linear JER-237` is not the same artifact as the
  repo-local historical `JER-237` editor command palette slice.
- Evidence target: align this repo queue document with live Linear JER-234
  through JER-236 and define the next dispatch contracts before starting new
  ambiguous implementation work.

## Next Candidate Issue Contracts

Recommended next product slice:

1. `[project] [L4] [none] [DAL-TBD] Review archive restore diff drilldown`
   - Outcome: make restore/archive validation actionable by surfacing
     section-level mismatch details, checksum paths, and affected graph/test
     evidence after a local review archive restore.
   - Acceptance: a restored archive with no mismatches still reports pass; a
     deliberately mutated archive reports the mismatched section, checksum key,
     expected checksum, actual checksum, and affected evidence path; the
     surface remains local and `truth_effect: none`.
   - Boundaries: no controller truth, frozen adapter, certified hardware YAML,
     C919 packet, live Linear browser mutation, or collaboration platform work.
   - Evidence: focused e2e for pass and mutated-archive mismatch; static shell
     test for drilldown fields; targeted validation-suite pass.
   - Priority: `L4` product visibility, recommended first dispatch.

Recommended next proof slice:

2. `[project] [L6] [none] [DAL-TBD] Sandbox scenario stress pack for large graphs`
   - Outcome: add reusable large-graph scenario/test-case fixtures so the
     runner, debugger, preflight, and archive loop can be exercised without
     manually building synthetic graphs in each test.
   - Acceptance: fixture-backed scenarios cover pass, fail, invalid graph, and
     stale-report cases; archive and restore evidence remains deterministic;
     full e2e/mypy-clean claims are made only when the real commands pass.
   - Boundaries: sandbox-only; no adapter/controller truth changes; no
     performance or certification claim.
   - Evidence: fixture tests, focused e2e, archive checksum/readback tests,
     targeted validation-suite pass.
   - Priority: `L6` proof hardening, recommended second dispatch.

Recommended next debt slice:

3. `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche 2`
   - Outcome: reduce the official strict mypy baseline again by typing one
     coherent module/test family without claiming full clean until the wrapper
     reports pass.
   - Acceptance: focused strict mypy command passes for the touched family; the
     official wrapper reports fewer errors/files or an explicitly unchanged
     blocker; runtime behavior tests for touched code pass.
   - Boundaries: no broad refactor, no public schema/interface changes, no
     mypy-clean claim unless `tools/run_mypy_gate.py --format json` reports
     `pass`.
   - Evidence: focused pytest, focused strict mypy command, official wrapper
     report, targeted validation-suite pass.
   - Priority: `L9` quality debt, recommended after one product/proof slice.

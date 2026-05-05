# Post-v5 v6 Live Queue

Status: active queue · live Linear `JER-245` closed · live Linear `JER-246` implementing JER-171 mypy tranche 4

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

## Closed Dispatches Through JER-237

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

Queue refresh dispatch:

- Live Linear issue: `JER-237`
- Title: `[project] [L9] [none] [DAL-TBD] Post-JER-236 v6 queue refresh and next dispatch map`
- URL: `https://linear.app/jerrykogami/issue/JER-237/project-l9-none-dal-tbd-post-jer-236-v6-queue-refresh-and-next`
- State after PR #230: `Done`
- Identifier rule: `live Linear JER-237` is not the same artifact as the
  repo-local historical `JER-237` editor command palette slice.
- Evidence target: align this repo queue document with live Linear JER-234
  through JER-236 and define the next dispatch contracts before starting new
  ambiguous implementation work.

Product dispatch:

- Live Linear issue: `JER-238`
- Title: `[project] [L4] [none] [DAL-TBD] Review archive restore diff drilldown`
- URL: `https://linear.app/jerrykogami/issue/JER-238/project-l4-none-dal-tbd-review-archive-restore-diff-drilldown`
- State after PR #231: `Done`
- Identifier rule: `live Linear JER-238` is not the same artifact as the
  repo-local historical `JER-238` review archive restore/regression bundle v3
  slice.
- Evidence target: local review archive restore failures expose section-level
  mismatch drilldown: section, checksum key, checksum path, expected checksum,
  actual checksum, affected evidence path, and sandbox-only truth metadata.

Proof dispatch:

- Live Linear issue: `JER-239`
- Title: `[project] [L6] [none] [DAL-TBD] Sandbox scenario stress pack for large graphs`
- URL: `https://linear.app/jerrykogami/issue/JER-239/project-l6-none-dal-tbd-sandbox-scenario-stress-pack-for-large-graphs`
- State after PR #232: `Done`
- Evidence target: add reusable large-graph pass, fail, invalid graph, and
  stale-report fixtures so runner, debugger, preflight, and archive tests can
  share one deterministic stress pack.

Current quality-debt dispatch:

- Live Linear issue: `JER-240`
- Title: `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche 2`
- URL: `https://linear.app/jerrykogami/issue/JER-240/project-l9-none-dal-tbd-jer-171-mypy-baseline-reduction-tranche-2`
- State after PR #233: `Done`
- Identifier rule: `live Linear JER-240` is not the same artifact as the
  repo-local historical `JER-171` mypy wrapper blocker.
- Evidence target: keep one coherent demo fault-injection test family focused
  strict-mypy clean, preserve its runtime tests, and reduce the official
  `tools/run_mypy_gate.py --format json --report-only` baseline without
  claiming full mypy clean.
- Current branch evidence: `tests/test_demo_fault_injection.py` is focused
  strict-mypy clean; the official wrapper remains `blocked` but reports 4617
  errors in 326 files, down from this branch's starting point of 4913 errors in
  347 files.

Current queue-refresh dispatch:

- Live Linear issue: `JER-241`
- Title: `[project] [L9] [none] [DAL-TBD] Post-JER-240 production readiness queue refresh`
- URL: `https://linear.app/jerrykogami/issue/JER-241/project-l9-none-dal-tbd-post-jer-240-production-readiness-queue`
- State after PR #234: `Done`
- Identifier rule: `live Linear JER-241` is not the same artifact as any
  repo-local historical JER label; use `repo-local post-JER-240 queue refresh`
  when referring to the older planning concept.
- Evidence target: record the verified post-JER-240 state, name current
  production-readiness blockers, and define the next executable Linear issue
  contracts before more implementation starts.

Current product-readiness dispatch:

- Live Linear issue: `JER-242`
- Title: `[project] [L4] [none] [DAL-TBD] Release-candidate workbench smoke pack`
- URL: `https://linear.app/jerrykogami/issue/JER-242/project-l4-none-dal-tbd-release-candidate-workbench-smoke-pack`
- State after PR #235: `Done`
- Identifier rule: `live Linear JER-242` is not the same artifact as any
  repo-local historical JER label; use `repo-local release-candidate smoke
  pack` when referring to the older planning concept.
- Evidence target: a local smoke gate starts the demo server on an available
  port, isolates archive storage, and probes `/workbench`, archive
  bundle/list/restore/readback, lever-snapshot fault injection, and one
  invalid-input rejection without external services.
- Current branch evidence: `tools/workbench_release_candidate_smoke.py
  --format json` passes six steps and `tests/test_workbench_release_candidate_smoke.py`
  passes.

Current gate-refresh dispatch:

- Live Linear issue: `JER-243`
- Title: `[project] [L9] [none] [DAL-TBD] Post-JER-240 full opt-in e2e refresh`
- URL: `https://linear.app/jerrykogami/issue/JER-243/project-l9-none-dal-tbd-post-jer-240-full-opt-in-e2e-refresh`
- State after PR #236: `Done`
- Evidence target: rerun the official opt-in e2e command on current `main`,
  record exact pass/fail/deselected counts, and avoid any full e2e green claim
  unless the command actually passes.
- Current branch evidence: the official command passed at 93 passed / 3445
  deselected in 149.97s on `origin/main@9516fa6`; see
  `docs/coordination/JER-243-e2e-refresh.md`.

Current release-operations dispatch:

- Live Linear issue: `JER-244`
- Title: `[project] [L6] [none] [DAL-TBD] Local production runbook and release manifest`
- URL: `https://linear.app/jerrykogami/issue/JER-244/project-l6-none-dal-tbd-local-production-runbook-and-release-manifest`
- State after PR #237: `Done`
- Evidence target: a local production-readiness runbook and a machine-readable
  release evidence manifest that record setup/start/stop/verify commands,
  required environment, unsupported external dependencies, current blockers,
  pass evidence, blocked gates, and not-claimed gates without secret values.
- Current branch evidence: `docs/coordination/local-production-runbook.md`
  defines the local release path, and `tools/workbench_release_manifest.py`
  generates and validates the release evidence manifest locally.

Current quality-debt dispatch:

- Live Linear issue: `JER-245`
- Title: `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche 3`
- URL: `https://linear.app/jerrykogami/issue/JER-245/project-l9-none-dal-tbd-jer-171-mypy-baseline-reduction-tranche-3`
- State after PR #238: `Done`
- Evidence target: keep `tools/workbench_release_candidate_smoke.py` focused
  strict-mypy clean by shielding the local `well_harness` import boundary
  without changing runtime behavior.
- Current branch evidence: focused strict mypy reports success in 1 source
  file, focused smoke pytest passes, and the official wrapper moved from 4619
  errors in 327 files to 4617 errors in 326 files while still blocked.

Current quality-debt dispatch:

- Live Linear issue: `JER-246`
- Title: `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche 4`
- URL: `https://linear.app/jerrykogami/issue/JER-246/project-l9-none-dal-tbd-jer-171-mypy-baseline-reduction-tranche-4`
- State at dispatch: `In Progress`
- Evidence target: type low-risk return boundaries in
  `tools/run_gsd_validation_suite.py` and `tools/validate_notion_control_plane.py`
  without changing validation command behavior.
- Current branch evidence: focused strict mypy reports success in 2 source
  files, focused validation helper tests pass, and the official wrapper moved
  from 4617 errors in 326 files to 4614 errors in 324 files while still
  blocked.

## Next Candidate Issue Contracts

Post-JER-240 production-readiness snapshot:

- Strong evidence: `unit_tests` passed through the validation-suite gate on PR
  #233, the focused demo fault-injection test family is strict-mypy clean, and
  the archive/restore/large-graph proof slices from PR #231 and PR #232 are
  merged on `main`.
- Known blocker: JER-171 full strict mypy remains blocked. The current verified
  wrapper result is 4617 errors in 326 files, not a clean gate.
- Known blocker: the current queue does not yet contain a single release
  smoke/readiness command that starts the workbench and probes the core local
  operator flows as one production-like gate.
- Full opt-in e2e is current as of live Linear `JER-243`: 93 passed / 3445
  deselected on `origin/main@9516fa6`.
- Known blocker: deployment, packaging, and operator runbook evidence are not
  yet merged as a release gate. The repo is ready for more hardening, not for a
  production-ready claim.

Dispatched product-readiness slice:

1. `[project] [L4] [none] [DAL-TBD] Release-candidate workbench smoke pack`
   - Outcome: add one local release-candidate smoke gate that starts the demo
     server on an available port and probes the first production-like operator
     flows in sequence.
   - Acceptance: the smoke gate verifies `/workbench` boot, archive list/read
     path, restore/readback, lever snapshot fault-injection path, and one
     invalid-input rejection with actionable failure output; it runs without
     external services and does not claim certification or cloud deployment.
   - Boundaries: no controller truth, frozen adapter, certified hardware YAML,
     C919 packet, public schema, or external platform mutation.
   - Evidence: new/focused pytest or script test for the smoke gate, one manual
     command summary, `git diff --check`, and targeted validation-suite pass.
   - Priority: `L4` product confidence, dispatched as live Linear `JER-242`;
     a production path needs one repeatable operator smoke gate before more UI
     or release claims.

Dispatched gate-refresh slice:

2. `[project] [L9] [none] [DAL-TBD] Post-JER-240 full opt-in e2e refresh`
   - Outcome: rerun the official opt-in e2e surface on current `main`, record
     exact pass/fail/deselected counts, and create follow-up issues only for
     real blockers.
   - Acceptance: the report names the command, selected-test count, first
     failing test if any, and whether the last known JER-236 e2e evidence still
     holds on current `main`; no product code changes are made in the audit
     slice.
   - Boundaries: audit/report-only unless a follow-up implementation issue is
     created; do not edit tests to hide failures; do not claim current full e2e
     green unless the command passes.
   - Evidence: e2e command summary, blocker classification, queue update, and
     Linear proof comment.
   - Priority: `L9` gate confidence, dispatched as live Linear `JER-243`;
     run after the smoke-pack slice or before any production-readiness claim.

Dispatched quality-debt slice:

3. `[project] [L9] [none] [DAL-TBD] JER-171 mypy baseline reduction tranche 3`
   - Outcome: reduce the official strict mypy baseline again by typing one
     coherent fixture/helper family, preferably the smallest family visible in
     the current wrapper tail.
   - Acceptance: focused strict mypy command passes for the touched family; the
     official wrapper reports fewer errors/files or an explicitly unchanged
     blocker; runtime tests for touched helpers pass.
   - Boundaries: no broad refactor, no public schema/interface changes, no
     mypy-clean claim unless `tools/run_mypy_gate.py --format json` reports
     `pass`.
   - Evidence: focused pytest, focused strict mypy command, official wrapper
     report, targeted validation-suite pass.
   - Priority: `L9` quality debt, dispatched as live Linear `JER-245`; keep
     reducing the known JER-171 blocker in small reversible tranches.

Dispatched release-operations slice:

4. `[project] [L6] [none] [DAL-TBD] Local production runbook and release manifest`
   - Outcome: add a truthful local production-readiness runbook and a
     machine-readable release evidence manifest for clean-checkout operation.
   - Acceptance: the runbook names exact setup/start/stop/verify commands,
     required env vars, unsupported external dependencies, and current blockers;
     the manifest records git SHA, verification commands, and not-claimed gates
     without embedding secrets.
   - Boundaries: documentation and local artifact generation only; no cloud
     deploy, no new orchestration platform, no external writes from the
     workbench.
   - Evidence: generated manifest test or schema check, doc diff, `git
     diff --check`, and targeted validation-suite pass.
   - Priority: `L6` operational readiness, dispatched as live Linear
     `JER-244`; useful after a smoke gate exists so the runbook has a concrete
     command to reference.

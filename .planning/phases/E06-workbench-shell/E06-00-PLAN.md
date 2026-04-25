---
epic: E06
title: Workbench Shell + 三联视图
status: in_progress
date: 2026-04-25
branch: feat/epic06-workbench-shell-20260425-r2
baseline_commit: a6521ca
baseline:
  pytest: "796 passed, 1 skipped, 49 deselected"
  e2e: "49 passed, 797 deselected"
  adversarial: "8/8, ALL TESTS PASSED"
---

# E06-00 Plan

## Objective

Add a `/workbench` browser route for the collaboration Workbench shell. The shell must provide three independently rendered columns: control panel, document surface, and circuit surface. It also needs a top identity/ticket/system bar, a right-side Annotation Inbox skeleton, and a Kogami-only Approval Center entry in the bottom bar.

## Scope

- Mount one new `GET /workbench` route in `src/well_harness/demo_server.py`.
- Use the existing `src/well_harness/static/workbench.html`, `workbench.css`, and `workbench.js` surface as the Workbench UI entry because those files already exist in the verified baseline.
- Add focused tests under `tests/test_workbench_shell.py`.
- Add closure notes under `.planning/phases/E06-workbench-shell/E06-05-CLOSURE.md`.

## Non-Goals

- No controller, adapter truth, runner, model, or existing demo route changes.
- No real annotation persistence, approval actions, or ticket generation in E06.
- No Notion writes.
- No modifications to existing `static/index.html`.

## Counterarguments And Mitigations

1. Existing `workbench.html/css/js` may already belong to P7 bundle acceptance and replacing it could erase prior behavior.
   - Mitigation: keep the E06 shell self-contained around explicit DOM anchors and avoid touching controller-backed payload contracts.
2. A three-column browser shell can hide errors if one panel fails during initialization.
   - Mitigation: render each column from an independent bootstrap function with its own fallback state; tests assert all three anchors are present without requiring shared data.
3. A Kogami-only bottom entry is not real security if it is controlled by client-side role selection.
   - Mitigation: label it as role-scoped UI only in code semantics; real authorization is deferred to E08/E09 server-side checks.
4. Static UI tests can become brittle if they assert pixel-level design.
   - Mitigation: assert semantic anchors, route behavior, and failure isolation hooks instead of styling minutiae.

## Acceptance

- `GET /workbench` returns the Workbench shell.
- HTML contains `workbench-topbar`, `workbench-control-panel`, `workbench-document-panel`, `workbench-circuit-panel`, `annotation-inbox`, and `approval-center-entry`.
- JS exposes three independent bootstrappers so one panel failure does not block the other two.
- Fast lane and three-track baseline remain green.

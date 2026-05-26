# Functional Milestone Symphony Goal Workflow

Date: 2026-05-07
Status: proposed repo-control workflow
Scope: AI FANTUI LogicMVP post-v5 `/workbench` development

## Purpose

Future work should be driven by clear functional milestones, not by a long
sequence of historical JER labels alone. Linear remains the work-control
surface, GitHub/repo remains the code truth, Notion remains the control-plane
mirror, Codex executes bounded `/goal` runs, OpenAI Symphony coordinates issue
dispatch/review loops, and Claude Opus 4.7 reviews milestone-level risk.

This document defines the operating model for that workflow.

## Current Control State

- GitHub `origin/main` after PR #257: `b4aa51d`.
- Linear connector read path is available. `AI FANTUI LogicMVP · Codex Daily
  Lane` has no `Queued` issue at the time of this workflow slice.
- Live Linear `JER-259` is `Done`.
- Repo-local `tools/linear_live_issue_factory.py` supports dry-run issue
  bodies and requires explicit `--confirm-write` for Linear issue creation.
- The `linear-symphony-codex` helper script did not see `LINEAR_API_KEY` in the
  non-sourced shell. Use `source ~/.zshrc` before direct script mode, or use
  the Linear connector read path.

## Functional Milestones

### M1 Canvas Authoring Workbench

Value target: an engineer can create, edit, wire, group, and inspect a
control-logic graph from the `/workbench` first screen without relying on
reference nodes.

Primary surfaces:

- `src/well_harness/static/workbench.html`
- `src/well_harness/static/workbench.css`
- `src/well_harness/static/workbench.js`
- `tests/test_workbench_editable_canvas_shell.py`
- focused workbench e2e tests in `tests/e2e/test_workbench_js_boot_smoke.py`

Done when:

- Visible canvas actions are Chinese-first and Simulink-like.
- Command palette and toolbar actions preserve stable ids/keywords.
- Subsystem grouping, port wiring, and route metadata remain sandbox-only.
- Focused static tests and targeted e2e pass for touched interactions.

Opus 4.7 review trigger:

- Required before declaring the authoring surface milestone complete.
- Required earlier if UI claims imply truth, certification, or schema changes.

### M2 Simulation, Test, And Debug Loop

Value target: a sandbox graph can be run against saved scenarios, produce
deterministic traces, and show actionable failures on nodes, ports, edges, and
assertions.

Primary surfaces:

- sandbox runner/report code in `src/well_harness/static/workbench.js`
- scenario/test-case state in the editable graph document
- focused runner/debug tests and e2e smoke tests

Done when:

- Scenario library operations round-trip through export/import/archive.
- Same graph plus same inputs produces stable traces.
- Invalid ops, missing inputs, cycles, dangling ports, and failed assertions
  surface structured findings.
- Touched runner/debug paths have focused tests.

Opus 4.7 review trigger:

- Required for any claim that simulation determinism is milestone-ready.
- Required immediately if determinism failures appear.

### M3 Evidence, Archive, And Handoff Loop

Value target: an engineer can prepare review evidence from the workbench,
restore it, inspect mismatches, and produce a ChangeRequest handoff without
mutating certified truth.

Primary surfaces:

- workbench bundle/archive generation
- archive restore/readback path
- ChangeRequest handoff packet validation
- preflight and evidence inspector reports

Done when:

- Evidence archives preserve graph, tests, run reports, debug traces, hardware
  overlays, and checksums.
- Restore mismatch output names the exact section and checksum path.
- Handoff packet schema remains stable.
- `truth_effect`, `controller_truth_modified`, and `frozen_assets_modified`
  remain non-mutating for sandbox evidence.

Opus 4.7 review trigger:

- Required before any archive/handoff milestone completion claim.
- Required for any public schema/import/export contract change.

### M4 Runtime Generalization Proof

Value target: the workbench can prove reuse on another adapter-backed system
without adding hidden rule engines or UI-only truth paths.

Primary surfaces:

- `src/well_harness/controller_adapter.py`
- `src/well_harness/adapters/`
- playback/diagnosis/knowledge modules
- second-system smoke and comparison tests

Done when:

- New system behavior enters only through explicit adapter interfaces.
- Playback, diagnosis, and knowledge capture consume the same runtime contracts.
- No hardcoded truth is added outside the adapter boundary.
- Focused tests show reuse without changing reference controller truth.

Opus 4.7 review trigger:

- Required before implementation if a slice touches adapters or runtime truth.
- Required before any generalization milestone closeout.

### M5 Release Maturity And Local Operations

Value target: local operators can run, verify, package evidence, and understand
which gates are passed, warning-only, blocked, or not claimed.

Primary surfaces:

- `docs/coordination/local-production-runbook.md`
- release manifest tooling
- validation suite wrappers
- e2e and mypy gate reports

Done when:

- Release manifest records exact pass, warning, blocked, and not-claimed gates.
- Local smoke path starts the demo server and probes key workbench routes.
- Full opt-in e2e and full shared validation are treated as milestone gates.
- Strict mypy is not claimed clean until the official wrapper passes.

Opus 4.7 review trigger:

- Required before release-readiness or production-readiness language.
- Required when milestone gates disagree with PR-level evidence.

## Linear Issue Contract

One Linear issue equals one bounded Codex/Symphony run. An issue is eligible
only when it has:

- Outcome
- Repository route
- Acceptance
- Boundaries
- Evidence Required
- `Agent eligible: Yes`

If any field is missing, classify the issue as ineligible. Do not infer intent
from title alone.

Issue titles should use milestone prefixes:

- `[M1] Canvas authoring ...`
- `[M2] Simulation test debug ...`
- `[M3] Evidence archive handoff ...`
- `[M4] Runtime generalization ...`
- `[M5] Release maturity ...`

## `/goal` Run Contract

Each accepted issue becomes one `/goal` command with exactly these sections:

1. Objective
2. Scope
3. Constraints
4. Done when
5. Stop if

Every `/goal` must include a token budget inside `Constraints` because the
workspace operating rules require it. Split the run rather than letting one
goal grow across milestone boundaries.

Template:

```text
/goal Objective:
Deliver <one Linear issue outcome> for <milestone> in
/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/<worktree>.

Scope:
- Read <issue/doc paths> first and report the touched-file plan.
- Change only <allowed files/directories>.
- Keep repo truth in GitHub/repo, Linear as work control, Notion as mirror.

Constraints:
- Token budget: <N> tokens for this run; split the issue if the plan exceeds it.
- Work in a fresh worktree from current origin/main.
- Do not edit controller truth, frozen adapters, certified hardware YAML,
  C919 reference packets, public schemas, or persistent formats unless the
  issue explicitly authorizes it.
- Keep sandbox evidence truth_effect none unless a separate truth-gate issue
  authorizes promotion.
- Use focused tests for daily slices; treat full e2e, full validation, and
  strict mypy as milestone gates unless Tier 0 is triggered.

Done when:
1. <artifact or file> contains the requested behavior/documentation.
2. <focused test command> exits 0.
3. <static/type/build command> exits 0 when applicable.
4. PR body maps acceptance to evidence and states not-claimed gates honestly.
5. Linear/Notion proof is dry-run or written only with explicit confirmation.

Stop if:
- The diff touches controller truth, adapters, frozen assets, public schemas,
  or persistent formats outside scope.
- A focused test fails for the touched surface and the fix would require
  weakening assertions.
- Any result implies certification, DAL, production, or truth promotion.
- Linear or Notion write would require credentials or mutation not explicitly
  authorized for this run.
```

## Symphony Execution Loop

1. Discover Linear work.
   - Use the Linear connector first.
   - If a local helper is preferred, set `LINEAR_AWCP` to the helper script and
     run `source ~/.zshrc && python "$LINEAR_AWCP" discover --team-key JER`.
   - If no eligible issue exists, generate dry-run issue bodies only.
2. Select one issue.
   - It must map to exactly one functional milestone.
3. Create a fresh worktree from current `origin/main`.
4. Start a Codex `/goal` run from the issue contract.
5. Use subagents only when the user explicitly asks for parallel agent work.
   - `codex-5.3-spark` is appropriate for read-only review or bounded
     sidecar implementation.
6. Open a PR with focused evidence.
7. Request Opus 4.7 review at milestone gates or risk triggers.
8. Merge only after the repo's explicit merge policy is satisfied.
9. Sync proof to Notion and, when explicitly authorized, Linear.
   - Linear proof writes require a dry-run preview plus explicit
     `--confirm-write` or equivalent user authorization.
   - Linear state transitions are separate mutations and require their own
     explicit authorization.

## Gate Policy

Tier 0 hard holds stop the run:

- controller truth or adapter semantics changed without authorization;
- frozen adapters, certified hardware YAML, or C919 reference packets changed;
- public schema/import/export/archive contracts broken;
- simulation determinism broken for the same graph and input trace.

Tier 1 daily warnings are recorded but do not stop ordinary sandbox UI work
unless they reveal Tier 0:

- focused pytest/e2e;
- targeted validation suite;
- relevant adversarial or fault-injection subset;
- UI smoke for touched interaction.

Tier 2 milestone gates block milestone closeout, not every daily PR:

- full opt-in e2e;
- full shared validation suite;
- full strict mypy clean;
- release manifest and local production evidence;
- Opus/Kogami architecture or UX review.

## Immediate Next Seeds

These are dry-run candidates. Do not create them in Linear without explicit
confirmation. The first three rendered seed contracts are recorded in
`docs/coordination/functional-milestone-linear-dry-run-seeds.md`.

1. `[M1] Canvas subsystem encapsulation polish`
   - Tighten subsystem creation/rename/group feedback, preserve command ids,
     and add focused static/e2e evidence.
2. `[M1] Command palette Chinese search parity`
   - Add Chinese search keywords alongside existing English keywords and prove
     both filtering paths.
3. `[M2] Scenario run result explanation panel`
   - Make failed assertions point to the exact node/edge/port timeline frame.
4. `[M3] Archive restore review checklist`
   - Add a compact review checklist for restored archives, no schema change.
5. `[M4] Adapter-backed second-system proof packet`
   - Plan the next adapter proof before touching adapter code.

## Review Roles

- Codex: primary implementation and local verification.
- OpenAI Symphony: issue/run orchestration pattern and proof routing.
- Linear: work-control truth and issue eligibility.
- GitHub/repo: code truth, PR evidence, CI/audit gate.
- Notion: control-plane mirror and executive status.
- Claude Opus 4.7: architecture reviewer, high-risk decision maker, and final
  milestone auditor.

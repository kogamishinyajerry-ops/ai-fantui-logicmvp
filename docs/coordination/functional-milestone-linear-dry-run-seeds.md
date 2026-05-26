# Functional Milestone Linear Dry-Run Seeds

Date: 2026-05-07
Status: dry-run only; no Linear write performed

## Purpose

These seed issues show how the functional milestone workflow should enter
Linear. They were rendered with `tools/linear_live_issue_factory.py` without
`--confirm-write`, so no external Linear issue was created.

## Seed 1

Title:

`[M1] [project] [L4] [none] [DAL-TBD] Canvas subsystem encapsulation polish`

Outcome:

Make subsystem creation, rename, group feedback, and command surface
affordances feel like one Simulink-style Canvas workflow while preserving
sandbox-only metadata.

Acceptance:

- Subsystem create/rename/group feedback is visible from the workbench Canvas
  without changing command ids.
- Focused static or e2e tests cover the touched feedback path and sandbox-only
  metadata.

Boundaries:

- Do not change controller truth, runner, adapters, public schemas, certified
  assets, or export/archive contracts.
- Do not remove existing English `data-command-palette-keywords` or command
  ids.

Evidence Required:

- Focused pytest for workbench editable canvas shell.
- Targeted workbench e2e for the touched interaction when behavior changes.
- `git diff --check` and PR acceptance mapping.

Metadata:

- Repository:
  `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/<fresh-worktree-from-origin-main>`
- Desired state: Queued
- Priority: High
- Risk: Low
- Agent eligible: Yes

## Seed 2

Title:

`[M2] [project] [L4] [none] [DAL-TBD] Scenario run result explanation panel`

Outcome:

Make failed sandbox scenario assertions point to the exact node, edge, port,
and timeline frame that explains the failure.

Acceptance:

- Failed assertions show the related graph element and trace tick in the
  workbench UI.
- The same graph plus same inputs keeps deterministic run output before and
  after the UI explanation change.

Boundaries:

- Do not change controller truth, adapters, public schemas, certified assets,
  or operation semantics.
- Do not claim full e2e or strict mypy clean unless official milestone commands
  pass.

Evidence Required:

- Focused runner/debug tests for the explanation path.
- Targeted e2e smoke for a failed scenario explanation.
- `git diff --check` and PR acceptance mapping.

Metadata:

- Repository:
  `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/<fresh-worktree-from-origin-main>`
- Desired state: Queued
- Priority: High
- Risk: Low
- Agent eligible: Yes

## Seed 3

Title:

`[M3] [project] [L4] [none] [DAL-TBD] Archive restore review checklist`

Outcome:

Add a compact review checklist for restored workbench archives so engineers can
see graph, tests, traces, evidence, checksums, and handoff readiness without
changing the archive schema.

Acceptance:

- Restored archives show a review checklist derived from existing
  restore/readback evidence.
- Schema, manifest, checksum, and raw export fields remain unchanged.

Boundaries:

- Do not change public schemas, archive format, controller truth, adapters,
  certified assets, or C919 packets.

Evidence Required:

- Focused archive/restore tests or static tests for checklist rendering.
- Schema validator remains passing if touched.
- `git diff --check` and PR acceptance mapping.

Metadata:

- Repository:
  `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/<fresh-worktree-from-origin-main>`
- Desired state: Queued
- Priority: High
- Risk: Low
- Agent eligible: Yes

## Write Gate

To create any seed in Linear, rerun the corresponding command with
`--confirm-write` only after Kogami explicitly authorizes the external write.
Until then, these are repo-local dry-run issue contracts only.

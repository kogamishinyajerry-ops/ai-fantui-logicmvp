# Workbench Validation Tier Policy

Date: 2026-05-07
Scope: Canvas/workbench sandbox development, ChangeRequest handoff packets, and
Codex Daily Lane PR evidence.

## Purpose

The workbench should move faster as a reliable logic-circuit simulation surface
without letting governance artifacts become the product's main execution path.
Validation is still required, but it is tiered by risk.

## Tier 0 Hard Holds

Only these conditions block daily workbench development immediately:

- Controller truth or adapter semantics are changed without an explicit
  higher-authority task.
- Frozen adapters, certified hardware YAML, or C919 reference packets are
  edited.
- Public schema/import/export/archive contracts are broken at a repo boundary.
- Simulation determinism is broken: the same circuit plus the same input trace
  no longer produces the same result.

If a Tier 0 hard hold is triggered, stop implementation and route through a
review packet before continuing.

## Tier 1 Daily Warnings

These checks should run when relevant to the touched files, but a failure is not
automatically a truth hold if Tier 0 remains intact:

- Focused pytest for touched modules.
- Default pytest or a targeted validation-suite slice.
- Adversarial or fault-injection lanes when the touched behavior affects their
  surface.
- Workbench smoke/e2e subsets that cover the changed interaction.

Daily PRs must state which warnings were run, passed, failed, or skipped. Failed
warnings become follow-up work unless they expose a Tier 0 hard hold.

## Tier 2 Milestone Gates

These gates belong to release, maturity, certification, or milestone handoff
decisions, not to every UI iteration:

- Full opt-in e2e suite.
- Full shared validation suite.
- Full strict mypy clean.
- Release manifest and local production-readiness evidence.
- Opus/Kogami architecture or UX review.

Milestone gates may block a release claim. They should not block a local
sandbox UX slice unless their failure proves a Tier 0 issue.

## Workbench Packet Semantics

Workbench archives and ChangeRequest handoff packets remain evidence-only:

- `controller_truth_modified` stays `false`.
- `frozen_assets_modified` stays `false`.
- `truth_level_impact`, `dal_pssa_impact`, and `truth_effect` stay `none`.
- `live_linear_mutation` stays `false`.
- `mypy_strict_clean` and full e2e claims stay `not_claimed` unless their
  official commands pass for the exact release or milestone SHA.

The daily workbench path is therefore: edit sandbox graph, run focused
simulation/tests, disclose warnings, and reserve heavy proof packaging for
milestone handoff.

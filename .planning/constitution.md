# AI FANTUI LogicMVP Constitution

## Milestone Hold

**Declared:** 2026-04-13
**Scope:** Milestone 4 (Phases P4–P11)

All P0 through P11 phases are complete. The project is at a natural pause point.

### What This Hold Means

- No active development phases.
- Base code frozen; only regression fixes and documentation corrections permitted.
- Notion control tower and GitHub repo remain accessible as read-only reference.
- Opus 4.6 review gate is not active.

### Reason

All P0→P11 capabilities have been delivered:
- Deterministic control-logic analysis workbench (thrust-reverser reference system)
- Runtime generalization proof via adapter layer (landing-gear second system)
- Fully automated GSD loop with Notion writeback and GitHub Actions CI
- Third-party onboarding guide and template scaffolding
- 23-command regression suite, 0 open gaps

The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.

### Resume Criteria

Milestone Hold lifts when one or more of the following conditions are met:

1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
2. External user feedback identifies a confirmed gap that cannot be resolved within the existing frozen baseline.
3. A project sponsor or lead author formally requests a new development phase via Notion control tower or GitHub.

No development activity resumes without a documented decision in the Notion control plane.

---

## Project Identity

**Name:** AI FANTUI LogicMVP
**Type:** Deterministic control-logic analysis workbench
**First Reference System:** Thrust reverser deploy cockpit
**Generalization Proof:** Landing-gear adapter runtime (second system)

## Core Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` is the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- New system truth is allowed only through explicit adapter interfaces.
- Bypassing adapters with new hardcoded truth paths is forbidden.

## Control Plane

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan → execute → verify routing.
- Opus 4.6 is the only intended manual review gate for subjective judgment.

## Phase Registry

| Phase | Title | Status |
|-------|-------|--------|
| P0 | Control Tower And GSD Control Plane | Done |
| P1 | Automate Execution And Evidence Writeback | Done |
| P2 | Harden Opus 4.6 Review Packets | Done |
| P3 | Reduce Control-Plane Drift | Done |
| P4 | Elevate Cockpit Demo To Presenter-Ready | Done |
| P5 | Demo Polish And Edge-Case Hardening | Done |
| P6 | Reconcile Control Tower And Freeze Demo Packet | Done |
| P7 | Build A Spec-Driven Control Analysis Workbench | Done |
| P8 | Runtime Generalization Proof | Done |
| P9 | Automation Hardening & Evidence Pipeline Maturity | Done |
| P10 | Second-System Runtime Pipeline End-to-End | Done |
| P11 | Product Readiness & Third-Party Onboarding Guide | Done |

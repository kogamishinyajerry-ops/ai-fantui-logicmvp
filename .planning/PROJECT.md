# AI FANTUI LogicMVP

## Vision

Build a deterministic control-logic analysis workbench, with the current thrust reverser deploy cockpit as the first reference system.
The project now prioritizes strict acceptance playback, fault injection and diagnosis, knowledge capture, and regression-protected control truth over full physical simulation or demo-only polish.

## Product Shape

- A lightweight Python package named `well-harness`.
- A standard-library local demo server and static cockpit UI.
- Deterministic CLI and JSON outputs for debugging and automation.
- A spec-driven control-system layer that can describe components, logic gates, monitored signals, scenarios, and fault modes.
- A scenario playback engine that can turn engineer-supplied process descriptions into monitor-vs-time traces.
- A fault-analysis workflow that can inject failures, reason along the logic chain, and persist incident/repair knowledge.
- A Notion control tower that mirrors GSD state without replacing code truth.

## Non-Negotiable Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` remains the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- Any future generalized system layer must mirror or wrap confirmed control truth; it must not invent a second hidden rule engine.
- `POST /api/demo`, `POST /api/lever-snapshot`, `well_harness demo`, and `well_harness run` remain stable unless a phase explicitly changes their contracts.

## Operating Model

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan -> execute -> verify routing.
- Opus 4.6 is the only intended manual review gate for subjective architecture / UX / quality judgment.
- Any Opus 4.6 review brief must reference Notion pages and the GitHub repo only, never local terminal file paths.
- When onboarding a new control system, unresolved ambiguities must be surfaced as explicit clarification questions before implementation proceeds.

# AI FANTUI LogicMVP

## Vision

Build a deterministic cockpit-style demo for the thrust reverser deploy control logic.
The project prioritizes explainable logic, stable demo behavior, and regression-protected control truth over full physical simulation.

## Product Shape

- A lightweight Python package named `well-harness`.
- A standard-library local demo server and static cockpit UI.
- Deterministic CLI and JSON outputs for debugging and automation.
- A Notion control tower that mirrors GSD state without replacing code truth.

## Non-Negotiable Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` remains the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- `POST /api/demo`, `POST /api/lever-snapshot`, `well_harness demo`, and `well_harness run` remain stable unless a phase explicitly changes their contracts.

## Operating Model

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan -> execute -> verify routing.
- Opus 4.6 is the only intended manual review gate for subjective architecture / UX / quality judgment.

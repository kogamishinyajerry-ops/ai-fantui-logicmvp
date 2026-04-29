# AI FANTUI LogicMVP

## Vision

Build an editable, verifiable, and auditable control-logic workbench, with the
current thrust reverser deploy cockpit as the first reference sample pack.
The project now prioritizes sandbox graph editing, baseline diffing, controlled
ChangeRequest generation, and regression-protected control truth over
system-specific demo repair.
This remains a digital-twin style interface for control logic, but the main
product boundary is the workbench foundation: engineers should be able to
derive a draft graph, edit nodes/ports/edges/hardware bindings, run candidate
scenarios, and compare against certified adapter/controller baselines.

## Product Shape

- A lightweight Python package named `well-harness`.
- A standard-library local demo server and static cockpit UI.
- Deterministic CLI and JSON outputs for debugging and automation.
- A spec-driven control-system layer that can describe components, logic gates, monitored signals, scenarios, and fault modes.
- A sandbox-only editable control model layer that can describe candidate nodes,
  ports, edges, hardware bindings, scenarios, and evidence metadata.
- A scenario playback engine that can turn engineer-supplied process descriptions into monitor-vs-time traces.
- A baseline-diff path that compares editable candidates against adapter-backed
  truth without making the candidate itself certified truth.
- A fault-analysis workflow that can inject failures, reason along the logic chain, and persist incident/repair knowledge.
- A Notion control tower that mirrors GSD state without replacing code truth.
- A FlyByWire-informed reference knowledge model that teaches design patterns and safety logic without becoming a copy source.

## Non-Negotiable Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` remains the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- Any future generalized system layer must mirror or wrap confirmed control truth; it must not invent a second hidden rule engine.
- Editable graph runtime is sandbox-only; it cannot replace or promote adapter
  or controller truth.
- New system truth is allowed only through explicit adapter interfaces that publish metadata and spec payloads.
- Bypassing adapters by adding new hardcoded truth paths is forbidden.
- New work should preserve immutable typed data models wherever practical, especially for system inputs, outputs, and replay/knowledge artifacts.
- `POST /api/demo`, `POST /api/lever-snapshot`, `well_harness demo`, and `well_harness run` remain stable unless a phase explicitly changes their contracts.

## Operating Model

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- For Codex Daily Lane work, Notion is record-only; Linear issue, GitHub PR, and
  validation evidence are the daily execution gate.
- GSD owns plan -> execute -> verify routing.
- Opus 4.6 is the only intended manual review gate for subjective architecture / UX / quality judgment.
- Any Opus 4.6 review brief must reference Notion pages and the GitHub repo only, never local terminal file paths.
- When onboarding a new control system, unresolved ambiguities must be surfaced as explicit clarification questions before implementation proceeds.
- FlyByWire/A320 material is a reference knowledge base for domain understanding, architecture patterns, and test ideas, not a direct code import source.
- The validation mindset stays phase-shaped: unit, component, integration, system, boundary, fault-injection, performance, and regression evidence should remain explicit as the workbench grows.

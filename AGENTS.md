# AI FANTUI LogicMVP - Codex Project Guide

## Mission

Build a digital-twin workbench for thrust-reverser control logic, with runtime generalization proof as the current priority.
The reference thrust-reverser path remains the first truth-bearing system, and landing-gear adapter work is evidence that the workbench can generalize without forking hidden rule engines.

## Non-Negotiables

- `src/well_harness/controller.py` is the only confirmed control truth for the reference thrust-reverser system.
- `src/well_harness/runner.py` / `SimulationRunner` remains the runtime driver for simulation-style execution.
- New system truth is allowed only through explicit adapter interfaces.
- Do not add hidden hardcoded truth paths outside the adapter boundary.
- Business logic belongs in controller/truth layers, not UI or persistence layers.
- Prefer immutable typed data models.
- Every meaningful behavior change should land with focused regression coverage.

## Current Repo Mapping

The repository already exists and does not use the aspirational folder names from a greenfield layout. Map new work onto the current structure:

- Controller truth: `src/well_harness/controller.py`
- Runtime driver: `src/well_harness/runner.py`
- Adapters: `src/well_harness/controller_adapter.py` and `src/well_harness/adapters/`
- Models: `src/well_harness/models.py`
- Playback/diagnosis/knowledge: `src/well_harness/scenario_playback.py`, `src/well_harness/fault_diagnosis.py`, `src/well_harness/knowledge_capture.py`
- Browser/UI surfaces: `src/well_harness/demo_server.py`, `src/well_harness/static/`
- Planning/control plane: `.planning/` and `tools/gsd_notion_sync.py`

Do not reorganize the repo toward the aspirational layout unless a dedicated architecture slice explicitly approves that work.

## Architecture Rules

- Keep the controller layer pure and deterministic.
- Use adapters to decouple runtime truth from specific systems, sensors, and environments.
- Keep simulation/runtime orchestration in runner-style code, not in controller truth.
- Keep schema and contract layers machine-readable.
- When adding another system, prefer proving reuse through adapter-backed runtime contracts before adding UI polish.
- Treat FlyByWire as a reference knowledge base for design patterns and domain understanding, not as a copy source.

## Testing Rules

- Preserve the staged testing mindset: unit -> component -> integration -> system -> boundary -> fault injection -> performance -> regression.
- Add focused tests for new runtime slices first, then promote stable proofs into `tools/run_gsd_validation_suite.py`.
- If a generalized system proof changes the default regression count, update the suite expectation tests and state summaries in the same slice.

## Current Phase Bias

- P7 is closed as the contract/schema convergence phase.
- P8 is the active runtime generalization proof phase.
- The current high-value path is: adapter -> playback -> diagnosis -> knowledge -> then decide whether to close out P8 or continue with comparison/bundle-level proof.

## Knowledge Sources

- Prefer repo truth first.
- Use Notion as the planning/control plane, not as a substitute for code truth.
- Use FlyByWire/A320 references to inform architecture, state-machine modeling, detent logic, safety interlocks, and test design.
- When applying external reference ideas, document the adaptation instead of implying direct equivalence.

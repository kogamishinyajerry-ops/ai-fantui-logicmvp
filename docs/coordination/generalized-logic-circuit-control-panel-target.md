# Generalized Logic Circuit Control Panel Target

Date: 2026-05-22
Status: strategic target, not current closeout claim

## Target

The long-term product goal is not only to display the current demo cockpit
logic circuit. The target is a generalized requirements-to-control-panel
capability:

Given a new aircraft control-system requirements document, such as a C919 ETRAS
requirements document, the system should be able to produce a logic circuit
control panel of comparable quality to the current demo cockpit panel.

## Expected Capability

The future system should be able to:

- ingest a new requirements document;
- identify control states, guards, interlocks, signals, outputs, and evidence
  hooks;
- build a candidate logic graph or IR without hardcoding the original thrust
  reverser demo;
- render a reviewable logic circuit control panel with clear nodes, wires,
  grouped subsystems, and scenario evidence;
- support an engineer-in-the-loop streamed authoring flow where each proposed
  node or wire is confirmed before it is committed;
- preserve explicit non-claim boundaries until a trusted controller truth path
  is approved.

## Trust Model

The generalized panel should be built through visible incremental edits, not as
one opaque whole-graph generation.

- Interaction target:
  `docs/coordination/engineer-in-the-loop-streamed-logic-authoring-target.md`
- User should see the active node or wire, source document excerpt, interpreted
  logic, upstream and downstream context, and model rationale.
- User confirmation should commit exactly one candidate graph edit.
- User feedback should trigger a revised proposal.
- Requirements document edits should require a separate explicit authorization.

## Current Milestone Boundary

The current Project Visibility / Customer Demo MVP evidence proves only that:

- the `/demo-reconstruction` route has a browser-verifiable demo surface;
- the demo cockpit logic circuit diagram is present as screenshot evidence;
- the current demo surface reports 20 nodes / 23 wires;
- the project-owner acceptance packet can preserve non-claim boundaries.

It does not prove generalized generation from an arbitrary requirements
document.

## Future Acceptance Shape

A future milestone for this target should include a new-domain input, for
example a C919 ETRAS requirements document, and pass only when:

- the source document is ingested through a documented pipeline;
- extracted requirements and assumptions are visible;
- generated logic IR is machine-readable;
- graph construction can be replayed as a sequence of user-confirmed node and
  wire edits;
- the rendered panel is browser-verifiable;
- reviewer evidence shows the panel quality is comparable to the current demo;
- no hidden controller truth path is introduced.

## Non-Claims

This target does not currently claim:

- C919 ETRAS correctness;
- production or certification readiness;
- controller truth promotion;
- automatic approval of generated logic;
- automatic requirements document mutation;
- equivalence to aircraft OEM control laws.

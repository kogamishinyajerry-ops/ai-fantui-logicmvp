# Streamed Logic Authoring Multi-Agent Plan

Date: 2026-05-22
Status: planning gate definition

## Purpose

This plan turns the engineer-in-the-loop streamed logic authoring target into a
multi-agent specialist-team work package. It is a planning gate for M21, not an
implementation claim and not project-owner acceptance.

Single command:

`make multi-agent-m21-streamed-logic-authoring-plan`

Default artifact directory:

`/tmp/ai-fantui-multi-agent-m21-streamed-logic-authoring-plan`

## Activation Boundary

This package can pass as a planning package while M21 activation remains
blocked. Actual implementation queue expansion stays blocked until the
project-owner final decision verifier reports `customer_demo_mvp_accepted`.

## Five-Agent Active Team

The work must stay inside the same five-agent active team cap used by the
UltraWork Monitor and merge-readiness surfaces:

Operating anchor: `agent_team.mode = five_agent_context_cap`.

- ChiefEngineerOrchestrator: sequencing, handoffs, stop conditions, and final
  integration.
- LogicIRRepairAgent: one proposed node or wire edit at a time, machine-readable
  candidate edit state, and truth boundary enforcement.
- EvidenceValidationAgent: active edit highlight evidence, confirm/reject/revise
  replay checks, screenshots, and non-claim gates.
- SafetyRequirementsReviewer: source excerpts, assumptions, states, signals,
  guards, ambiguities, and requirements edit authorization risk.
- PackagingPRReadinessAgent: read-only review handoff before project-owner
  acceptance.

## Required Workstreams

The plan is valid only when it covers:

- source quote and interpretation contract;
- atomic graph-edit proposal;
- candidate graph commit boundary;
- active node or wire highlight;
- requirements edit authorization;
- requirements document edit proposals, where requirements document edits require explicit authorization;
- stream replay and review packet.

## Existing Reuse Anchors

The specialist team should reuse existing candidate-authoring surfaces where
possible:

- `src/well_harness/static/logic_builder/index.html`: task, generation, and
  drawing stream rails.
- `src/well_harness/static/logic_builder/logic_builder.js`: replay event
  construction, selected node/wire state, provenance rendering, and active
  circuit styling.
- `src/well_harness/requirements_intake/logic_builder.py`: existing
  `needs_user_confirmation`, `confirmed_by_user`, `truth_effect: none`, and
  `controller_truth_modified: false` boundaries.

Known gaps:

- current stream behavior is mostly replay/progress style, not hardened backend
  streaming;
- reject currently behaves like cancel/continue and is not yet a persisted
  reject event;
- pending-edit focus must be distinct from runtime active/fault state.

## Trust Boundary

The system must not accept one opaque whole-graph generation as the product
experience. The trusted path is:

1. propose one candidate edit;
2. highlight the active node or wire;
3. show source excerpt and interpreted logic;
4. wait for user confirm or feedback;
5. commit exactly one candidate graph edit only after confirmation;
6. require separate authorization for requirements document edits.

## Non-Claims

This plan does not claim:

- C919 ETRAS correctness;
- controller truth promotion;
- production readiness;
- certification or DAL readiness;
- automatic requirements document mutation;
- whole-graph black-box generation acceptance.

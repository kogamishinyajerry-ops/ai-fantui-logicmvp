# Editable Workbench v4 Authoring + Hardware Design

Workbench v4 is the next product mainline after Runtime v3. The goal is to turn
`/workbench` from a capable sandbox editor into an engineering-grade authoring
surface: high-freedom graph editing, reusable subsystem authoring,
hardware/interface design evidence, sandbox feedback, baseline diff review, and
controlled ChangeRequest handoff.

## Linear Project

`AI FANTUI LogicMVP · Editable Workbench v4 Authoring + Hardware Design`

## Launch Issue

- JER-204: Roadmap and Linear narrative refresh after Runtime v3 closure

## Seed Backlog

- JER-205: Workbench v4 authoring roadmap and acceptance model
- JER-206: Component library and reusable subsystem templates v1
- JER-207: Group/subsystem node editor v1
- JER-208: Hardware interface design model v1
- JER-209: Connector/pin map editor v1
- JER-210: Hardware evidence inspector v2
- JER-211: Scenario/debug timeline linked to selected graph elements v1
- JER-212: Candidate-to-baseline diff review workflow v2
- JER-213: ChangeRequest handoff packet from editable draft v1

## Product Target

An engineer should be able to:

- derive a sandbox draft from the certified baseline view;
- add, remove, group, and reconnect graph nodes without editing certified truth;
- instantiate reusable logic components and subsystem templates;
- attach candidate hardware/interface design records to graph elements;
- edit connector, cable, port, and pin metadata with explicit `evidence_gap`
  states for unknown values;
- run sandbox scenarios and see feedback linked to selected graph elements;
- compare candidate output against the certified adapter/controller baseline;
- export a review-ready ChangeRequest packet instead of directly mutating
  controller, adapter, DAL, PSSA, or truth-level state.

## Acceptance Ladder

- **v4.0 planning**: JER-205 defines the acceptance model and issue sequencing.
- **v4.1 authoring primitives**: JER-206 and JER-207 add reusable templates and
  subsystem grouping while preserving deterministic draft serialization.
- **v4.2 hardware/interface design**: JER-208 through JER-210 add sandbox-only
  hardware/interface records, connector/pin map editing, and inspector evidence
  coverage.
- **v4.3 feedback and review**: JER-211 and JER-212 link scenario/debug output
  to selected graph elements and make candidate-vs-baseline diff review
  archive-ready.
- **v4.4 handoff**: JER-213 emits a controlled ChangeRequest packet that can be
  used by Linear/PR workflows without claiming certification.

## Boundaries

- `src/well_harness/controller.py` remains the certified thrust-reverser
  baseline and is not semantically rewritten by v4.
- Frozen adapters, frozen hardware YAML, and the C919 reference packet remain
  read-only.
- Hardware/interface design records are evidence and review inputs only; they
  do not participate in certified truth evaluation unless a separate governed
  review authorizes that future change.
- Sandbox graph output can be `equivalent`, `divergent`, `invalid_model`, or
  `invalid_scenario`; it cannot be `certified`.
- Product LLM/chat behavior stays frozen. Codex/OpenAI/Symphony are development
  workflow tools, not product truth engines.

## Gate Policy

Every v4 PR must state:

- Linear issue ID;
- adapter and layer;
- truth-level impact;
- red lines touched;
- test delta;
- whether mypy/e2e are verified or still blocked by known baseline issues.

Do not claim e2e 49/49 or `mypy --strict` clean until those gates are
independently restored and the official commands report pass.

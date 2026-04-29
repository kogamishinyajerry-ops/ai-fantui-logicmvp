# Editable Workbench Runtime v3

Editable Workbench Runtime v3 moves the completed UI interaction layer into
canonical sandbox runtime artifacts. The goal is not to make a candidate graph
certified; it is to make every workbench edit executable, validateable, diffable,
and archivable as controlled engineering evidence.

## Linear Project

`AI FANTUI LogicMVP · Editable Workbench Runtime v3`

## Issue Chain

- JER-165: Canonicalize workbench UI draft into `editable_control_model_v1`
- JER-166: Sandbox graph validation report v1
- JER-167: Scenario selector and custom snapshot sandbox UI
- JER-168: Port-aware edge inspector v1
- JER-169: Runtime v3 acceptance bundle and regression proof

## JER-165 Rule

JER-165 converts `/workbench` UI draft snapshots into canonical
`editable_control_model_v1` payloads before sandbox runtime/diff.

The conversion is sandbox-only:

- UI draft nodes become editable sandbox nodes with approved op catalog values.
- UI edges become evidence-only canonical model edges.
- Edges to existing logic nodes may create synthetic UI target ports so graph
  structure can be preserved without changing baseline rules.
- Invalid UI graph references return `invalid_model` evidence.
- `controller_truth_modified`, `truth_level_impact`, and `dal_pssa_impact`
  remain false/none.

## JER-166 Rule

JER-166 makes graph validation evidence structured enough for the API and UI to
consume directly.

The validation report remains sandbox-only:

- Every sandbox run response carries `validation_report`.
- Valid graphs return a pass report with zero issues.
- Invalid graphs return `invalid_model` plus categorized issues for
  `invalid_edge`, `dangling_port`, `duplicate_edge`, `unsafe_op`, and
  `missing_node`.
- `/workbench` renders the issue summary inside the sandbox diff panel.
- The report is evidence for a draft candidate only; it does not certify,
  approve, or mutate truth.

## JER-167 Rule

JER-167 lets engineers choose a supported sandbox scenario and optionally add a
custom initial-input snapshot before running the candidate.

The scenario/snapshot surface is truth-neutral:

- The default scenario remains `nominal_landing`.
- Supported alternatives are explicit UI/API choices.
- Custom snapshot JSON may only override supported timeline initial inputs.
- Invalid scenario or snapshot input returns sandbox validation evidence, not a
  truth decision.
- Evidence archives include the selected scenario metadata.

## JER-168 Rule

JER-168 makes draft edges inspectable as evidence-only port/signal bindings.

The edge inspector is non-authoritative:

- Selecting an edge shows source node, target node, source port, target port,
  signal id, and validation status.
- UI edge metadata is exported with draft JSON for review evidence.
- Missing endpoint metadata is rendered as `evidence_gap`.
- Edge inspection never changes control truth or hardware truth.

## Planned Runtime Rules

- JER-169 will close the milestone with a runtime acceptance bundle.

## Boundaries

- Do not edit `src/well_harness/controller.py` truth semantics.
- Do not edit frozen adapters, frozen hardware YAML, or the C919 reference
  packet.
- Do not promote truth level or make DAL/PSSA claims.
- Do not restore product LLM/chat behavior.
- Do not let UI drafts, canonical sandbox models, validation reports, or archive
  manifests become certified truth.

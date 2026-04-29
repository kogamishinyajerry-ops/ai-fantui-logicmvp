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

## Planned Runtime Rules

- JER-166 will make graph validation structured enough for UI and API evidence.
- JER-167 will add scenario/custom snapshot selection after canonicalization is
  stable.
- JER-168 will make edge inspection port-aware.
- JER-169 will close the milestone with a runtime acceptance bundle.

## Boundaries

- Do not edit `src/well_harness/controller.py` truth semantics.
- Do not edit frozen adapters, frozen hardware YAML, or the C919 reference
  packet.
- Do not promote truth level or make DAL/PSSA claims.
- Do not restore product LLM/chat behavior.
- Do not let UI drafts, canonical sandbox models, validation reports, or archive
  manifests become certified truth.

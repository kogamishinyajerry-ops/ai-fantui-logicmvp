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

- JER-205: Workbench v4 authoring roadmap and acceptance model (Done)
- JER-206: Component library and reusable subsystem templates v1 (Done)
- JER-207: Group/subsystem node editor v1 (Done)
- JER-208: Hardware interface design model v1 (Done)
- JER-209: Connector/pin map editor v1 (Done)
- JER-210: Hardware evidence inspector v2 (Done)
- JER-211: Scenario/debug timeline linked to selected graph elements v1 (Done)
- JER-212: Candidate-to-baseline diff review workflow v2 (In review)
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

- **v4.0 planning**: JER-205 defined the acceptance model and issue sequencing.
- **v4.1 authoring primitives**: JER-206 adds reusable component templates; JER-207 adds
  subsystem grouping while preserving deterministic draft serialization.
- **v4.2 hardware/interface design**: JER-208 through JER-210 add sandbox-only
  hardware/interface records, connector/pin map editing, and inspector evidence
  coverage.
- **v4.3 feedback and review**: JER-211 and JER-212 link scenario/debug output
  to selected graph elements and make candidate-vs-baseline diff review
  archive-ready.
- **v4.4 handoff**: JER-213 emits a controlled ChangeRequest packet that can be
  used by Linear/PR workflows without claiming certification.

## Acceptance Model

Workbench v4 is accepted when the workbench can support a complete engineering
authoring loop without changing certified truth:

1. **Authoring fidelity**: graph edits, reusable templates, subsystem grouping,
   port wiring, undo/redo, import/export, and deterministic draft hashing all
   preserve a sandbox candidate model.
2. **Hardware/interface design fidelity**: candidate LRU, connector, cable,
   port, pin, provenance, and `evidence_gap` metadata can be edited and reviewed
   without entering certified truth evaluation.
3. **Sandbox feedback fidelity**: candidate graphs can run supported scenarios,
   highlight affected graph elements, and produce `equivalent`, `divergent`,
   `invalid_model`, or `invalid_scenario` baseline-diff evidence.
4. **Review handoff fidelity**: the workbench can export an archive-ready packet
   containing the candidate model, hardware/interface evidence, diff result,
   ChangeRequest body, red-line metadata, gate claims, and checksums.

The acceptance model is product-facing but not certification-facing. It proves
that engineers can explore, validate, and package candidate edits. It does not
certify the candidate, promote truth level, or make DAL/PSSA claims.

## JER-206 Closure Note

JER-206 delivers the first v4 authoring primitive. The `/workbench` editor
toolbar now includes a reusable component library with `single_and_gate`,
`compare_guard`, and `two_stage_interlock` templates. Inserting a template
creates only draft nodes and draft edges; template provenance is serialized as
`component_template` node/edge metadata and summarized in the draft/export/archive
`component_library` payload.

The slice remains sandbox-only:

- `truth_effect` remains `none` for component library metadata.
- template insert does not mutate certified baseline nodes;
- controller truth, frozen adapters, frozen YAML, and C919 packets are untouched;
- evidence archive output includes a component-library checksum for review
  reproducibility.

## JER-207 Closure Note

JER-207 delivers subsystem grouping as the second v4 authoring primitive. The
workbench can now group selected draft nodes into a named subsystem container,
rename that container, and ungroup it while preserving the original nodes,
ports, and draft edges. The canvas renders a subsystem overlay, and the right
inspector exposes group/rename/ungroup controls.

The slice remains sandbox-only:

- grouping writes `subsystem_groups` metadata and node-side `subsystem_group`
  provenance only;
- group operations do not rewrite `draftEdges`, typed ports, controller truth,
  adapters, hardware YAML, or C919 packets;
- undo/redo uses the existing editable history snapshots;
- evidence archive output includes a subsystem-group checksum for review
  reproducibility.

## JER-208 Closure Note

JER-208 delivers the first v4 hardware/interface-design foundation slice. The
repo now has `editable_hardware_interface_design_v1`, a sandbox-only model for
candidate LRUs, cables, connectors, ports, pins, signal bindings, and explicit
evidence-gap records. The model lands as a parallel artifact rather than an
extension of the existing thrust-reverser hardware parameter schema.

The slice remains sandbox-only:

- `candidate_state` must remain `sandbox_candidate`;
- truth-level, DAL/PSSA, controller truth, and runtime truth impact fields must
  remain `none` or `false`;
- signal binding `truth_effect` must remain `none`;
- reference integrity is checked for LRU, connector, port, pin, cable, and
  binding IDs, while unknown carrier data must use explicit `evidence_gap`
  markers;
- no UI, API, controller, adapter, frozen YAML, or C919 reference packet changes
  are introduced by this issue.

## JER-209 Closure Note

JER-209 delivers the first visible connector/pin authoring slice. The
workbench right inspector now has a Connector / Pin Map section that exports
rows from current sandbox hardware bindings, lets an engineer fill pin-level
metadata, applies those rows back to existing node/edge owners, and carries the
map through draft import/export and evidence archive checksums.

The slice remains sandbox-only:

- connector/pin rows are local draft evidence with `truth_effect: none`;
- missing connector, port, or pin fields stay explicit `evidence_gap` values;
- applying a map updates only existing sandbox node/edge metadata and skips
  missing owners;
- no backend API, controller, adapter, frozen YAML, C919 packet, truth-level,
  DAL, or PSSA behavior is changed.

## JER-210 Closure Note

JER-210 turns the existing inspector into a selected-owner hardware evidence
review surface. When an engineer selects a node or edge, the right panel now
shows the candidate LRU/hardware id, cable, connector, local port, peer port,
local pin, peer pin, evidence status, source ref, coverage state, connector/pin
row count, and explicit evidence-gap counts. Node selection keeps the existing
read-only hardware evidence API signal rows; edge selection uses only the
sandbox candidate edge binding because there is no certified edge-level truth
map to claim.

The slice remains sandbox-only:

- `hardware_evidence_v2` is serialized into draft export, ChangeRequest proof
  packet summaries, and evidence archives with `truth_effect: none`;
- connector/pin unknowns remain explicit `evidence_gap` values;
- the inspector does not write controller truth, backend truth, adapters,
  hardware YAML, C919 reference packets, truth-level, DAL, or PSSA state;
- archive output includes a Hardware Evidence v2 checksum for review
  reproducibility.

## JER-211 Closure Note

JER-211 links the existing sandbox workflow timeline to the selected graph
element. The bottom workbench area now includes a Selected Debug Timeline panel
that follows node and edge selection, shows the active scenario, latest diff
verdict, trace-link state, graph context, ports, and hardware overlay, and
updates after a sandbox run. The packet is review/debug evidence, not a
certification or control-truth claim.

The slice remains sandbox-only:

- `selected_debug_timeline` is serialized into draft export, ChangeRequest proof
  packet summaries, and evidence archives with `truth_effect: none`;
- running sandbox updates the selected target's debug verdict and keeps
  candidate-vs-baseline status as review evidence only;
- hardware bindings remain overlay metadata and do not participate in certified
  truth evaluation;
- no controller, adapter, backend truth, frozen YAML, C919 packet, truth-level,
  DAL, or PSSA behavior is changed.

## JER-212 Closure Note

JER-212 makes candidate-vs-certified baseline diff review explicit and
archive-ready. The right inspector now has a Diff Review v2 panel that mirrors
the latest sandbox verdict, selected graph target, active scenario, review
readiness, archive readiness, first divergence text, and certification claim.
The corresponding packet is serialized into draft export, ChangeRequest proof
packet summaries, and local evidence archives.

The slice remains sandbox-only:

- `candidate_baseline_diff_review_v2` is review evidence with
  `truth_effect: none`, `candidate_state: sandbox_candidate`, and
  `certification_claim: none`;
- `equivalent` means behavior matched the baseline for the selected scenario,
  not that the candidate is certified;
- `divergent`, `invalid_model`, and `invalid_scenario` remain review states
  that require human follow-up before any ChangeRequest implementation;
- no controller, adapter, backend truth, frozen YAML, C919 packet, truth-level,
  DAL, or PSSA behavior is changed.

## JER-205 Sequencing Contract

JER-205 is the lane-entry contract for v4. It does not add runtime behavior; it
defines how the next implementation issues become executable.

Before JER-206 through JER-213 are marked `agent:ready`, each issue must state
which acceptance state it touches:

- `clarification`: the workbench has enough evidence to ask for missing design
  input and produce a follow-up bundle.
- `ready`: the sandbox candidate has enough model, hardware/interface evidence,
  scenario output, and diff evidence to produce a full review packet.
- `archived`: the candidate review packet has been written to an archive that
  can be restored or inspected outside the browser.

Every v4 issue that touches bundle/archive behavior must preserve these
readback anchors:

- `bundle_kind` must remain non-certifying. It may describe workflow state, but
  it must not introduce a `certified` bundle kind.
- `next_actions` must remain explicit enough for an engineer to continue the
  review without guessing hidden state.
- Archive output must remain restorable and checksum-covered when the issue
  changes bundle/archive payloads.

Equivalence or divergence belongs in candidate-vs-baseline review evidence, not
in a new truth-level or certification field. If a later v4 issue needs new
wire-shape, it must land as a scoped schema change with tests rather than
hardcoding truth semantics into UI or archive text.

## Execution Sequence

| Issue | Delivery focus | Primary acceptance | Dependency |
| --- | --- | --- | --- |
| JER-205 | v4 roadmap and acceptance model | This document defines the acceptance ladder, work-item sequence, and gate policy | JER-204 merged |
| JER-206 | Component library and reusable subsystem templates | Template insert/export/archive round-trip preserves sandbox-only metadata | JER-205 |
| JER-207 | Group/subsystem node editor | Group, rename, ungroup, and undo/redo preserve ports and edges | JER-206 may run in parallel after model contract is clear |
| JER-208 | Hardware interface design model | Loader, validator, hash, and schema docs cover candidate hardware/interface records | JER-205 |
| JER-209 | Connector/pin map editor | UI edits connector/pin rows and preserves explicit `evidence_gap` states | JER-208 |
| JER-210 | Hardware evidence inspector v2 | Inspector shows coverage and gaps from candidate hardware/interface records | JER-208 |
| JER-211 | Scenario/debug timeline linkage | Scenario output highlights selected nodes, ports, edges, and hardware bindings | JER-206, JER-207, JER-208 |
| JER-212 | Candidate-to-baseline diff review v2 | Diff review is archive-ready and never marks candidate output certified | JER-211 |
| JER-213 | ChangeRequest handoff packet | Packet includes candidate model, evidence, tests, boundaries, and red-line metadata | JER-212 |

## Work-Item Contract

Each v4 implementation issue must be small enough for one Codex Daily Lane PR
and must carry these fields before `agent:ready` is applied:

- Outcome: user-visible engineering capability or review artifact.
- Acceptance: concrete behavior and data contract that can be tested.
- Boundaries: controller truth, frozen assets, truth-level, DAL/PSSA, and
  product LLM/chat exclusions.
- Evidence Required: targeted tests, readback checks, and any UI/API smoke
  relevant to the changed surface.
- Metadata: repository path, adapter/project, layer, truth-level impact, and
  known gate blockers.

JER-206 through JER-213 should not claim broad v4 completion individually. Each
issue closes one capability slice and updates this coordination note only when
the v4 acceptance ladder or sequencing changes.

## Definition Of Done

- The implementation or document change lands in one PR linked to its Linear
  issue.
- PR body includes the Codex Daily Lane proof packet.
- Changed schemas, loaders, runtime paths, or UI flows have targeted tests.
- Hardware/interface unknowns are explicit `evidence_gap` values.
- Sandbox candidates remain non-authoritative in exported data and UI copy.
- Archive or handoff artifacts include red-line metadata when they can be
  reviewed outside the browser.
- Any e2e or mypy blocker is recorded as a blocker, not hidden behind a green
  summary.

## Readback Matrix

Use these existing surfaces as the default verification map for v4 issues that
touch bundles, archives, or API readback:

- Schema: `docs/json_schema/workbench_bundle_v1.schema.json`,
  `docs/json_schema/workbench_archive_manifest_v1.schema.json`,
  `tests/test_workbench_bundle_schema.py`, and
  `tests/test_workbench_archive_manifest_schema.py`.
- Bundle/archive: `tests/test_workbench_bundle.py` for
  `build_workbench_bundle`, `archive_workbench_bundle`, `bundle_kind`,
  `next_actions`, and restore payload round-trip coverage.
- Integrity: `tests/test_archive_integrity.py` for archive checksum and
  manifest consistency.
- Restore sandbox: `tests/test_archive_restore_sandbox.py` for archive restore
  path traversal, sandbox violation, and moved-archive recovery behavior.
- API readback: `tests/test_demo.py` coverage for `/api/workbench/bootstrap`,
  `/api/workbench/recent-archives`, `/api/workbench/bundle`, and
  `/api/workbench/archive-restore`.
- Validation suite: `tools/run_gsd_validation_suite.py --format json` should
  continue to include `workbench_bundle_schema` and
  `workbench_archive_manifest_schema`; if full validation is impractical in a
  docs-only PR, the PR must say so plainly.

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

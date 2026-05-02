# Editable Workbench v5 Deep-Water Plan

Date: 2026-05-02
Status: Implementation active · JER-233 scenario test case library complete
Scope: single-user `/workbench` foundation only

## Summary

Workbench v5 moves from feature-complete foundation slices into the hard part:
making `/workbench` feel like a real single-user control-logic construction
tool. The target is still Figma/Canvas-style direct manipulation combined with
Simulink-style logic modeling, but the implementation priority is now the base
editor, runner, test bench, debugger, and archive loop rather than any
thrust-reverser or C919-specific panel.

Thrust-reverser and C919 E-TRAS remain reference/sample packs and regression
anchors. They are not v5 product drivers. A mature v5 workbench should be able
to rebuild those panels quickly from generic primitives later.

## Non-Negotiables

- Single-user first: no realtime collaboration, shared cursors, comments,
  permissions, multiplayer review, or conflict-resolution work in v5.
- Sandbox-only: editable graphs, scenarios, tests, debug traces, hardware
  evidence, and archives must keep `truth_effect: none` and
  `candidate_state: sandbox_candidate` where applicable.
- No controller truth edits: `src/well_harness/controller.py` semantics remain
  untouched.
- No frozen asset edits: frozen adapters, frozen hardware YAML, and the C919
  reference packet remain read-only.
- No certification claims: truth-level, DAL, PSSA, and certified adapter status
  are outside Codex Daily Lane authority.
- No product LLM/chat reactivation: AI remains an engineering-assistance layer,
  not a runtime truth engine inside the workbench.

## Product Objective

An engineer should be able to start from an empty or derived sandbox draft,
construct a control graph from primitives, wire explicit ports, configure node
logic, define scenario tests, run the candidate, inspect why it passed or
failed, attach hardware/interface evidence, and export one review-ready archive.

The v5 acceptance path is:

1. Create a draft from scratch or from a template.
2. Add logic nodes, ports, subsystem groups, and edges with stable positions.
3. Configure operation parameters and interface contracts through the inspector.
4. Save, restore, export, and import the same canonical graph document.
5. Define tick-based scenarios and assertions.
6. Run the sandbox candidate with the approved op catalog only.
7. Debug selected nodes, ports, edges, and assertions over a timeline.
8. Attach hardware/interface evidence gaps without mutating certified truth.
9. Generate a preflight report and review archive.
10. Restore the archive and recover the same graph, tests, reports, and proof.

## Architecture Direction

v5 should reduce dependence on the DOM as the implicit graph source of truth.
The browser can still render through existing `workbench.html`,
`workbench.css`, and `workbench.js`, but the canonical draft object should
drive creation, validation, serialization, runner input, debug traces, and
archive restore.

Preferred direction:

- Canonical graph document first: nodes, ports, edges, groups, templates,
  layout, selection-neutral state, scenarios, assertions, hardware evidence,
  workspace document metadata, and archive checksums.
- DOM adapter second: canvas elements are projections of the graph document,
  not independent truth.
- Runner/test/debug surfaces consume the canonical graph document, not
  scattered UI state.
- Hardware/interface records remain evidence overlays attached to graph
  elements.

## v5 Issue Sequence

### JER-229 · Workbench v5 deep-water roadmap and clean-lane launch

Status: Done after PR #211.

Outcome: Update repo roadmap, state, and coordination docs so v5 has a clear
single-user foundation-first execution queue after JER-228.

Acceptance:

- JER-228 is marked Done after PR #210.
- v5 is introduced as the next active milestone.
- The issue sequence below is recorded in repo truth.
- Linear write access remains read-only; live mutation is not claimed.

### JER-230 · Empty-canvas graph authoring palette v1

Status: Done after PR #212.

Outcome: Let an engineer build a small graph from primitives without relying on
the thrust-reverser seed nodes.

Acceptance:

- A new sandbox draft can start empty.
- The editor exposes primitive node templates for boolean, compare, latch,
  delay, input, and output nodes.
- Adding/removing/renaming nodes updates workspace action metadata.
- Export/import/archive preserve node counts, positions, operation metadata,
  and `truth_effect: none`.

Implementation notes:

- Empty authoring is explicit through `canvas_authoring_mode: empty_authoring`;
  it is not inferred from a transient DOM clear.
- The primitive catalog starts with input, output, boolean AND/OR, compare,
  between, delay, and latch operations.
- Imported empty-authoring drafts replace the reference sample nodes so
  `logic1` through `logic4` do not reappear during round-trip restore.
- Archive output keeps the same sandbox boundary: `truth_effect: none`,
  `controller_truth_modified: false`, and no certified asset writes.

### JER-231 · Canonical graph document v2 and DOM adapter boundary

Status: Done after PR #213.

Outcome: Make the canonical editable graph document the source object for
authoring, serialization, validation, and restore.

Acceptance:

- A `workbench-editable-graph-document.v2` draft can be derived from current v1
  state without data loss.
- The document includes graph, layout, groups, templates, scenarios, assertions,
  hardware evidence references, and workspace metadata.
- The DOM render path can rebuild visible nodes/edges from the document.
- v1 imports remain accepted through an explicit migration path.

Implementation notes:

- `editable_graph_document.version` advances to
  `workbench-editable-graph-document.v2`, while
  `workbench-editable-graph-document.v1` remains in
  `accepted_import_versions`.
- v2 carries `canonical_model` for nodes, edges, ports, typed ports,
  subsystem groups, component library, scenario/test state, hardware evidence
  references, viewport state, and workspace document reference.
- v2 carries `dom_adapter` metadata to state that the canvas DOM is a
  projection of `editable_graph_document.canonical_model`.
- Import accepts v1 top-level drafts and v2 canonical-only drafts, then exports
  the restored document as v2 sandbox evidence.

### JER-232 · Port drag wiring and route diagnostics v2

Status: Done after PR #214.

Outcome: Make wiring feel like an engineering editor: select/drag from source
port to target port, preview compatibility, create or reject edges, and retain
route metadata.

Acceptance:

- Source and target ports are explicit interaction targets.
- Compatible links create deterministic edge records.
- Dangling or incompatible links become validation findings, not graph truth.
- Disconnect/reconnect keeps undo/redo and action log metadata consistent.

Implementation notes:

- Drag starts from output port handles and renders a transient
  `.workbench-port-drag-preview` route with canvas-level compatibility status.
- Completion over an input port creates sandbox edges with
  `source_ref: ui_draft.port_drag_wiring`.
- Route metadata records `creation_tool: port_drag_wiring`,
  `compatibility_status`, source/target port ids, edge labels, and
  `truth_effect: none`.
- Rejected drags remain graph validation feedback and do not mutate controller
  truth, adapters, hardware YAML, frozen assets, DAL, or truth-level state.

### JER-233 · Scenario test case library v1

Status: Done.

Outcome: Turn the sandbox test bench from a single local form into a reusable
test-case surface.

Acceptance:

- Engineers can create, rename, duplicate, delete, and select saved scenarios.
- Each scenario stores tick inputs, assertions, expected outputs, and notes.
- Run reports reference the scenario id and graph document revision.
- Import/export/archive preserve the scenario library and last run report.

Implementation notes:

- The browser now emits `scenario_test_case_library` as
  `workbench-scenario-test-case-library.v1` with selected/active test case ids,
  saved test cases, expected outputs, notes, and sandbox-only boundary fields.
- `workbench-sandbox-test-run-report.v1` now records the selected/active test
  case id, graph document id/version, graph/workspace revision ids, and
  `scenario_test_case_library_checksum`.
- Draft export/import, local restore, `editable_graph_document.canonical_model`,
  evidence archive, and foundation review archive include the library and
  checksum coverage while legacy single-form test bench imports still restore.

### JER-234 · Sandbox runner trace kernel v2

Outcome: Produce deterministic per-tick traces for candidate nodes, ports,
edges, and assertions using only the approved sandbox op catalog.

Acceptance:

- Supported ops include the existing approved catalog only.
- Invalid ops, missing inputs, cycles, dangling ports, and invalid scenarios
  produce structured findings.
- Run output includes node/port/edge values per tick and assertion pass/fail.
- Hardware/interface evidence is visible context only and does not affect truth
  evaluation.

### JER-235 · Debug probe timeline v3

Outcome: Make failures explainable through selected graph elements.

Acceptance:

- Selecting a node, port, edge, or assertion shows watched values over ticks.
- The first failing assertion links to the related graph element when known.
- Timeline selection and graph selection stay in sync.
- Archive output includes debug probe checksums and restore readback.

### JER-236 · Hardware/interface evidence attachment v2

Outcome: Attach hardware/interface evidence gaps to generic graph elements
instead of reference-sample-specific panels.

Acceptance:

- Engineers can attach LRUs, connectors, pins, cables, and signal bindings to
  nodes, ports, edges, and subsystem groups.
- Duplicate ids and broken references are blocked locally.
- Unknown values remain explicit `evidence_gap` records.
- No certified hardware YAML or adapter files are written.

### JER-237 · Editor command palette and inspector ergonomics v1

Outcome: Improve high-frequency single-user editing flow without adding
collaboration.

Acceptance:

- Keyboard shortcuts and command palette expose create, rename, duplicate,
  group, wire, run, debug, export, import, and archive commands.
- Inspector sections stay synchronized with the current graph selection.
- Actions record workspace document metadata.
- UI changes remain inside `/workbench`.

### JER-238 · Review archive restore and regression bundle v3

Outcome: Close v5 by proving the whole authoring loop can be archived and
restored.

Acceptance:

- Archive includes graph document v2, scenario library, run reports, debug
  traces, hardware evidence, preflight findings, ChangeRequest proof, and gate
  summary.
- Restore validates checksums and red-line metadata.
- A focused e2e smoke covers create graph -> wire -> run -> debug -> attach
  evidence -> archive -> restore.
- PR proof remains honest about e2e and mypy baseline blockers.

## Test Strategy

- Schema/model slices: focused pytest for migration, canonical serialization,
  hash stability, and validation findings.
- UI authoring slices: focused browser/e2e smoke for blank draft, add node,
  connect ports, edit inspector fields, undo/redo, export/import, and archive.
- Runner/debug slices: runtime tests for supported ops, invalid ops, cycles,
  missing inputs, assertion pass/fail, trace stability, and hardware
  non-mutation.
- Every PR: `git diff --check`, red-line diff, targeted tests, and
  `tools/run_gsd_validation_suite.py` in bounded mode.
- Do not claim e2e 49/49 or mypy clean until official gates report pass.

## Linear Notes

Proposed project name:
`AI FANTUI LogicMVP · Editable Workbench v5 Deep-Water Foundation`

Linear helper mode is currently `api-read`; no live issue creation or state
mutation is claimed by this launch doc. The visible live `JER-228` identifier is
not the validation-suite issue and must not be mutated by Codex. If Linear ids
continue to collide with unrelated work, create the v5 issues under new actual
Linear identifiers while preserving the repo-local sequence above as the
implementation order.

Recommended labels for all v5 implementation issues:
`adapter:project`, `truth:none`, `phase:workbench-v5`, `red-line:none`, and
`agent:ready` only after Outcome, Acceptance, Boundaries, and Evidence Required
are complete.

Recommended issue titles:

- `[project] [L9] [none] [DAL-TBD] Workbench v5 deep-water roadmap and clean-lane launch`
- `[project] [L4] [none] [DAL-TBD] Empty-canvas graph authoring palette v1`
- `[project] [L4] [none] [DAL-TBD] Canonical graph document v2 and DOM adapter boundary`
- `[project] [L4] [none] [DAL-TBD] Port drag wiring and route diagnostics v2`
- `[project] [L6] [none] [DAL-TBD] Scenario test case library v1`
- `[project] [L6] [none] [DAL-TBD] Sandbox runner trace kernel v2`
- `[project] [L4] [none] [DAL-TBD] Debug probe timeline v3`
- `[project] [L5] [none] [DAL-TBD] Hardware/interface evidence attachment v2`
- `[project] [L4] [none] [DAL-TBD] Editor command palette and inspector ergonomics v1`
- `[project] [L9] [none] [DAL-TBD] Review archive restore and regression bundle v3`

# E07 Plan - Canvas Annotation Tools

## Objective

Add the first real annotation layer on top of the Workbench shell: point, area, link, and text-range tools across the control, document, and circuit surfaces, backed by a local `AnnotationProposal` schema and file store.

## Scope

- Add schema: `schemas/annotation_proposal.schema.json`.
- Add proposal model/store code under `src/well_harness/workbench/`.
- Add static annotation overlay controls and client behavior:
  - `src/well_harness/static/annotation_overlay.js`
  - additive changes to `workbench.html`, `workbench.css`, and `workbench.js`
- Add persistent store directory scaffolding under `data/proposals/` while ignoring runtime JSON records.
- Add focused tests for schema/store and static Workbench annotation anchors.

## Counterarguments And Mitigations

1. Counterargument: full canvas geometry could become a hidden second UI framework.
   Mitigation: keep E07 to minimal DOM overlays and normalized anchors; no rendering engine or business logic enters the static layer.

2. Counterargument: persistence can drift from the JSON schema if implemented ad hoc.
   Mitigation: the Python store validates required fields, tool enums, surface enums, status, and path-safe IDs before writing.

3. Counterargument: link and text-range annotations need richer document semantics than E07 can safely add.
   Mitigation: store stable anchors (`href`, `selector`, `start_offset`, `end_offset`, `text_quote`) but leave approval semantics to E08+.

4. Counterargument: adding JS to a large legacy workbench page risks breaking existing acceptance anchors.
   Mitigation: all UI additions are additive, the old page title and existing IDs remain untouched, and route compatibility tests stay in the fast lane.

## Success Criteria

- Four tool buttons are present and expose `data-annotation-tool` values: `point`, `area`, `link`, `text-range`.
- Control, document, and circuit surfaces expose `data-annotation-surface`.
- `annotation_overlay.js` is loaded by the Workbench page and is independent from the legacy bundle logic.
- `AnnotationProposal` schema and store tests pass.
- Existing fast-lane tests, e2e tests, and adversarial checks remain green at closure.

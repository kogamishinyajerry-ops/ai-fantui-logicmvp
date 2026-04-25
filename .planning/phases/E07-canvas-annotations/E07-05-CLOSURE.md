# E07 Closure - Canvas Annotation Tools

## What Shipped

- Added four Workbench annotation tools: `point`, `area`, `link`, and `text-range`.
- Mounted annotation-enabled surfaces on the three Workbench columns: control, document, and circuit.
- Added `src/well_harness/static/annotation_overlay.js` for local draft creation, tool switching, marker rendering, and Annotation Inbox draft updates.
- Added `schemas/annotation_proposal.schema.json` for the `AnnotationProposal` JSON contract.
- Added `src/well_harness/workbench/proposals.py` with proposal construction, validation, path-safe IDs, and local JSON persistence.
- Added `data/proposals/` scaffolding with runtime proposal JSON ignored by Git.
- Added focused schema/store/static tests.

## Verification Numbers

- Fast-lane pytest: `808 passed, 1 skipped, 49 deselected, 1 warning in 62.47s`
- E2E pytest: `49 passed, 809 deselected, 1 warning in 2.85s`
- Adversarial browser/server script: `ALL TESTS PASSED` across 8 adversarial sections
- Diff hygiene: `git diff --check` passed

The non-e2e count increased from E06 by six tests: three proposal schema/store tests and three static annotation tests.

## Open Issues

- Browser-created drafts are stored in local storage for E07; server-side submit flow is owned by E08.
- Area annotations use a normalized default rectangle from a click rather than drag-to-resize; this is enough for proposal anchoring but not a full design canvas.
- Text-range annotations capture selected text when available; richer document token offsets remain future polish.

## Handoff Notes

- E08 should reuse `ProposalStore` and the schema contract rather than creating a separate proposal path.
- Runtime proposal records belong under `data/proposals/*.json` and remain ignored by Git.
- The overlay intentionally avoids touching controller truth, adapters, or the legacy Workbench bundle flow.

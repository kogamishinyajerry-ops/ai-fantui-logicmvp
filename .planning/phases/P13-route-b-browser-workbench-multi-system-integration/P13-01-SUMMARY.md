---
phase: P13-Route-B
plan: "01"
subsystem: ui
tags: [flask, http-server, generic-truth-adapter, multi-system, browser-ui, p13]

# Dependency graph
requires: []
provides:
  - SYSTEM_REGISTRY + /api/system-snapshot endpoint for 3 systems
  - System switcher UI in demo hero
  - Data-driven chain-panel rendering from spec
  - GenericTruthEvaluation answer card for non-thrust-reverser systems
affects: [P13-02, P13-Route-B]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - SYSTEM_REGISTRY factory pattern for multi-system adapter selection
    - spec-driven chain-map rendering (no hardcoded node HTML)
    - GenericTruthEvaluation as generic answer payload for non-thrust-reverser systems

key-files:
  modified:
    - src/well_harness/demo_server.py - SYSTEM_REGISTRY, /api/system-snapshot, _spec_to_nodes, _default_snapshot_for_system
    - src/well_harness/static/demo.html - system-selector <select> in hero
    - src/well_harness/static/demo.js - handleSystemSwitch, resetUIState, renderChainMap, renderTruthEvaluation
    - src/well_harness/static/demo.css - .system-selector-wrap, .truth-eval-card styles

key-decisions:
  - "SYSTEM_REGISTRY keys match exactly what demo.js sends: 'thrust-reverser', 'landing-gear', 'bleed-air'"
  - "Condition panel hidden (display:none) for non-thrust-reverser systems, per P13 decision that it stays thrust-reverser-only"
  - "Truth evaluation card uses GenericTruthEvaluation.summary + blocked_reasons as primary answer for non-thrust-reverser"
  - "System switch calls resetUIState() before rendering new system to ensure clean state"

patterns-established:
  - "System switcher pattern: <select> -> fetch /api/system-snapshot -> resetUIState() -> renderChainMap() -> renderTruthEvaluation()"
  - "Chain-map dynamic rendering: clear innerHTML, create div.chain-node per node, add chain-arrow divs between"
  - "Non-thrust-reverser answer path: GenericTruthEvaluation card inserted at top of .result-grid"

requirements-completed: [P13-EXIT-01, P13-EXIT-02, P13-EXIT-03, P13-EXIT-04, P13-EXIT-05]

# Metrics
duration: ~15min
completed: 2026-04-13
tasks: 4
files_modified: 4
---

# Phase P13-Route-B Plan 01: Multi-System Demo UI Summary

**System switcher extends demo UI to serve landing-gear and bleed-air control systems via a shared GenericControllerTruthAdapter protocol, replacing the previous single-system-only thrust-reverser chain-panel and QA drawer.**

## Performance

- **Duration:** ~15 min
- **Tasks:** 4 completed
- **Files modified:** 4

## Accomplishments

- Added `SYSTEM_REGISTRY` dict + `GET /api/system-snapshot` endpoint serving three systems (thrust-reverser, landing-gear, bleed-air) with spec-driven nodes and truth evaluation
- Added system-switcher `<select id="system-selector">` in the demo hero with three options, styled with chip-purple accent palette
- Made chain-panel data-driven: `renderChainMap()` clears `.chain-map` and builds nodes from the API response's `nodes` array
- Added `truth-eval-card` for non-thrust-reverser systems showing `GenericTruthEvaluation.summary` + `blocked_reasons` as the answer; condition panel hidden for non-thrust-reverser

## Task Commits

Each task was committed atomically:

1. **Task 1: Add /api/system-snapshot endpoint + SYSTEM_REGISTRY** - `211ab2e` (feat)
2. **Task 2: Add system-switcher UI to demo.html hero + demo.css** - `07e015d` (feat)
3. **Task 3: Make chain-panel data-driven from spec in demo.js** - `2f818a6` (feat)
4. **Task 4: Regression + fix WORKBENCH_RECENT_ARCHIVES_PATH** - `cfc4aec` (fix)

## Files Created/Modified

- `src/well_harness/demo_server.py` - Added `SYSTEM_REGISTRY`, `SYSTEM_SNAPSHOT_PATH`, `_default_snapshot_for_system()`, `_spec_to_nodes()`, `system_snapshot_payload()`, and route in `do_GET()`
- `src/well_harness/static/demo.html` - Added `<select id="system-selector">` with 3 `<option>` elements in the hero `<section>`
- `src/well_harness/static/demo.js` - Added `handleSystemSwitch()`, `resetUIState()`, `renderChainMap()`, `renderTruthEvaluation()`, wired selector `onchange` to `handleSystemSwitch()`, bootstrapped default system
- `src/well_harness/static/demo.css` - Added `.system-selector-wrap`, `#system-selector`, `.truth-eval-card`, `.truth-eval-blocked`, `.truth-eval-active` styles

## Decisions Made

- Used factory registry pattern (`SYSTEM_REGISTRY`) matching the Research's recommendation — adding new systems requires only one dict entry
- Accepted the P13 decision that condition panel stays thrust-reverser-only; non-thrust-reverser systems show a read-only truth-eval card as their answer
- Used `GenericTruthEvaluation.to_dict()` for the truth evaluation payload — generic across all three systems without special-casing

## Deviations from Plan

**1. Rule 3 - Blocking Issue: WORKBENCH_RECENT_ARCHIVES_PATH route accidentally removed during endpoint addition**
- **Found during:** Task 4 (regression validation)
- **Issue:** The `SYSTEM_SNAPSHOT_PATH` insertion in `do_GET` accidentally replaced the `WORKBENCH_RECENT_ARCHIVES_PATH` handler block
- **Fix:** Restored the `WORKBENCH_RECENT_ARCHIVES_PATH` route immediately after `SYSTEM_SNAPSHOT_PATH`
- **Files modified:** `src/well_harness/demo_server.py`
- **Verification:** `test_demo_server_recent_archives_api_lists_recent_workbench_archives` returned to 200 OK
- **Committed in:** `cfc4aec` (part of task 4 fix commit)

**Total deviations:** 1 auto-fixed (Rule 3)

## Issues Encountered

- **WORKBENCH_RECENT_ARCHIVES_PATH route dropped during edit** — the insertion point for `SYSTEM_SNAPSHOT_PATH` was placed using `old_string` that matched within the `WORKBENCH_RECENT_ARCHIVES_PATH` block, replacing it accidentally. Fixed by restoring the route in the subsequent edit.

## Next Phase Readiness

- `SYSTEM_REGISTRY` is extensible: adding a new system only requires adding one entry to the dict
- `renderChainMap()` dynamically renders nodes for any spec shape — compatible with landing-gear (7 components + 2 logic nodes) and bleed-air (5 components + 2 logic nodes)
- Pre-existing test failure in `test_demo_static_assets_include_showcase_surface_layout` — the test checks for `"answer"` CSS fragment that does not exist in the stylesheet; this was failing before P13-01 changes and is unrelated to this plan

---
*Phase: P13-Route-B Plan 01*
*Completed: 2026-04-13*

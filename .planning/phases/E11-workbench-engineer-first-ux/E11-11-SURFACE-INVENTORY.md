# E11-11 Surface Inventory — JS-boot e2e smoke coverage + bundle-page bug fix

> Per `.planning/constitution.md §UI-COPY-PROBE` (v2.3) and §Codex Persona Pipeline Tier-Trigger.
>
> Closes deferred JS verification debt accumulated across E11-08 (role
> affordance JS toggle), E11-13 (bundle/shell sentinel), and E11-15c
> (Chinese-first DOM render). The new e2e infra immediately surfaced a
> latent bundle-page boot bug, which is fixed in lockstep.

## Discovery: bundle-page boot bug surfaced by new e2e

The first run of `test_bundle_workbench_boots_without_js_errors` failed
with `TypeError: document.createElement is not a function` at
`workbench.js:1225` inside `renderFingerprintDocumentList`. Stack:

```
TypeError: document.createElement is not a function
    at workbench.js:1225:27 (Array.map callback)
    at renderFingerprintDocumentList (workbench.js:1224)
    at renderSystemFingerprint (workbench.js:1311)
    at renderSystemFingerprintFromPacketPayload (workbench.js:1658)
    at loadBootstrapPayload (workbench.js:3502)
```

Root cause: `documents.map((document) => { ... })` shadowed the global
DOM `document`, so `document.createElement(...)` called a method on the
plain data object instead of the DOM. The bundle page silently rendered
nothing for the System Fingerprint document list. This was previously
invisible because no automated test booted JS in a real browser.

Two shadow sites fixed:
- `workbench.js:1224` — `renderFingerprintDocumentList` map callback
  (the actual crashing site)
- `workbench.js:1649` — `renderSystemFingerprintFromPacketPayload` map
  callback (didn't crash because it doesn't call `document.X`, but is
  the same anti-pattern)

Both renamed `document → doc`. Identical behavior, no API change.

## Surface diff inventory

| # | Surface | Type | Anchor | Notes |
|---|---|---|---|---|
| 1 | Playwright + Chromium e2e suite covering /workbench JS boot | [NEW] | `tests/e2e/test_workbench_js_boot_smoke.py` | 8 tests; opt-in via `pytest -m e2e`; auto-skips if Playwright/Chromium absent. |
| 2 | Static-source guard test against `document` global shadowing in workbench.js | [NEW] | `tests/test_workbench_js_no_global_shadowing.py` | 2 tests; runs in default lane so the regression is caught even without `-m e2e`. |
| 3 | Bug fix: rename loop param `document → doc` in renderFingerprintDocumentList | [BUGFIX] | `workbench.js:1224` | Closes the bundle-page boot crash. |
| 4 | Bug fix: rename loop param `document → doc` in renderSystemFingerprintFromPacketPayload | [BUGFIX] | `workbench.js:1649` | Same anti-pattern; eliminated for hygiene + to satisfy the new guard test. |

## Tier-trigger evaluation

Per `.planning/constitution.md §Codex Persona Pipeline Tier-Trigger`:

> **Tier-A** iff `copy_diff_lines ≥ 10 AND [REWRITE/DELETE] count ≥ 3`. Otherwise **Tier-B**.

- **copy_diff_lines** = 0 (no UI copy changed)
- **[REWRITE/DELETE]** = 0

→ **Tier-B** (1-persona review).

Note that this sub-phase ALSO touches `workbench.js` (>5 LOC) which
under the original v6.1 trigger list would be a Codex must-call. That's
satisfied here by the Tier-B review. Per CLAUDE.md global rules, JS
runtime fixes also benefit from Codex eyes.

> **Verdict: Tier-B**. Persona = **P5 (Apps Engineer)** — round-robin
> successor of E11-15c's P4 AND content-fit: P5 reviews end-user-facing
> reproducibility, browser boot health, and shipped-flow integrity,
> which is exactly what e2e + bundle-bug-fix needs.

## Behavior contract

**E11-11 e2e suite** (`tests/e2e/test_workbench_js_boot_smoke.py`, 8 tests):

E11-08 closure (4 tests):
- Default `/workbench` boots Kogami with Approval Center visible, affordance hidden.
- `/workbench?identity=Engineer` swaps to: entry hidden + aria-disabled, panel hidden, affordance visible.
- `window.setWorkbenchIdentity('Engineer')` flips DOM correctly.
- `window.setWorkbenchIdentity('   ')` returns false (blank guard).

E11-13 closure (2 tests):
- Shell page boots without JS errors (sentinel guard early-returns before bundle-bound handlers).
- Bundle page boots without JS errors (sentinel does NOT block it; ALL bundle-bound handlers must succeed).

E11-15c closure (2 tests):
- Real-DOM headers (h1, eyebrow, 3 column h2s, inbox h2, approval h2) all start with the correct Chinese token.
- Real-DOM control-panel + approval entry buttons render Chinese-first text.

**Static-source guard** (`tests/test_workbench_js_no_global_shadowing.py`, 2 tests):
- No arrow callback `(document) =>` shadows the global.
- No `function name(document)` parameter shadows the global.

## Truth-engine red line

Files touched:
- `src/well_harness/static/workbench.js` — 2 loop-parameter renames (BUGFIX)
- `tests/e2e/test_workbench_js_boot_smoke.py` — NEW (8 e2e tests)
- `tests/test_workbench_js_no_global_shadowing.py` — NEW (2 guard tests)
- `.planning/phases/E11-workbench-engineer-first-ux/E11-11-SURFACE-INVENTORY.md` — NEW
- `.planning/phases/E11-workbench-engineer-first-ux/PERSONA-ROTATION-STATE.md` — appended

Files NOT touched: `controller.py`, `runner.py`, `models.py`,
`src/well_harness/adapters/`, `workbench.html`, `workbench.css`,
`demo_server.py`. Truth-engine boundary preserved. The two JS edits
are pure variable-rename refactors — zero behavior change in the
non-bundle code path; the bundle code path is restored to its
intended behavior (System Fingerprint document list now renders).

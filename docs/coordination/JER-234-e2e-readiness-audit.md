# JER-234 Official E2E 49/49 Readiness Audit

Date: 2026-05-03
Live Linear issue: `JER-234`
PR baseline: `origin/main@d933cf9`

## Outcome

Current post-JER-233 `origin/main` is not ready for an `e2e 49/49` or full
opt-in e2e green claim.

The current opt-in e2e surface is also larger than the historical 49-test
claim. The audited command selected 91 e2e tests, not 49.

## Commands

Full opt-in e2e audit:

```bash
uv run --locked --extra dev --extra e2e python -m pytest tests/ -m e2e -q --tb=short
```

Focused blocker confirmation:

```bash
uv run --locked --extra dev --extra e2e python -m pytest \
  tests/e2e/test_workbench_js_boot_smoke.py::test_workbench_captured_template_remaps_overlapping_ids_and_preserves_rules \
  -m e2e -q --tb=short
```

## Result

Full command:

- Result: fail
- Passed: 90
- Failed: 1
- Deselected: 3439
- Duration: 196.49s

Focused blocker command:

- Result: fail
- Failed: 1
- Duration: 31.50s

## First Blocker

Test:

`tests/e2e/test_workbench_js_boot_smoke.py::test_workbench_captured_template_remaps_overlapping_ids_and_preserves_rules`

Failure:

`page.click("#workbench-insert-captured-template-btn")` timed out because the
button resolved but stayed disabled:

```text
<button disabled type="button" id="workbench-insert-captured-template-btn" title="Insert latest captured subsystem template">INS</button>
```

The failing test imports a draft JSON payload that already contains a captured
subsystem template, then expects the UI to enable the insert button after
`#workbench-import-draft-btn`. The current browser state does not enable that
button for this imported-template path.

## Passing Subset

The audit still proves the environment is capable of running the opt-in e2e
suite:

- Playwright dependency and Chromium launch path worked.
- The shared e2e demo server on port `8799` started successfully.
- 90 selected e2e tests passed before/around the blocker.

## Classification

This is a product/workbench UI state blocker, not an environment blocker.

Likely follow-up area:

- captured subsystem template import hydration;
- `capturedSubsystemTemplates` state after draft JSON import;
- enablement logic for `#workbench-insert-captured-template-btn`;
- checksum refresh for imported captured templates.

## Follow-Up Recommendation

Create a separate implementation issue:

Title:

`[project] [L4] [none] [DAL-TBD] Enable captured template insertion after draft import`

Outcome:

Imported draft JSON with `component_library.captured_templates` enables the
captured-template insert flow and preserves remapped ids/rules.

Acceptance:

- The focused blocker test passes.
- The full opt-in e2e command reports no failures or only separately classified
  blockers.
- No controller truth, frozen adapter, certified hardware YAML, or C919
  reference packet changes.

Boundary:

- Fix the workbench UI/import state path only.
- Do not weaken or skip the failing e2e assertion.
- Do not claim e2e 49/49 or full e2e green until the real command passes.

## Gate Decision

Do not claim:

- `e2e 49/49`
- full opt-in e2e green
- e2e readiness

until the captured-template import/insert blocker is fixed and the official
command is rerun successfully.


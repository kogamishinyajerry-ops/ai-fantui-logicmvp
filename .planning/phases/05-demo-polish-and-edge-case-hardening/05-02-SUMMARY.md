# P5-02 Summary - Latest-Interaction-Wins Demo Request Arbitration

## Outcome

`P5-02` hardened the first-screen demo shell so only the newest prompt or lever interaction can repaint the shared result surface.

## What Changed

- Added request-arbitration helpers in `src/well_harness/static/demo.js` so stale prompt or lever responses are ignored after a newer interaction starts.
- Cleared pending debounced lever work when a prompt submit becomes the newest interaction.
- Added static regression coverage for the new arbitration contract in `tests/test_demo.py`.
- Kept `P5-01`'s HTTP smoke suite and the shared validation loop intact while layering the browser-side guardrail on top.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_prefer_latest_interaction_response tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output tests.test_validation_suite`
- `python3 tools/demo_path_smoke.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- This change stays inside the existing `POST /api/demo` and `POST /api/lever-snapshot` contracts; it does not introduce browser automation, new dependencies, or a second control-truth layer.
- The next P5 slice can now focus on widening edge-case coverage instead of repairing stale-response race conditions first.

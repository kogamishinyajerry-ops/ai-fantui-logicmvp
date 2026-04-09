# P5-05 Summary - L4-Gated TRA Lock And Compact Cockpit Layout

## Outcome

`P5-05` made the cockpit behave like the requested rear-travel gate: deep reverse travel is now locked at `-14°` until `L4` is ready, and the left-side lever/condition area is denser so VDT work no longer forces as much scrolling away from the logic board.

## What Changed

- Added a demo-surface `L4` lock gate in `src/well_harness/demo_server.py` that probes the `-14°` boundary, caps deeper reverse travel when the gate is not ready, and returns a structured `tra_lock` payload to the UI.
- Updated `src/well_harness/static/demo.html`, `src/well_harness/static/demo.css`, and `src/well_harness/static/demo.js` so the browser shows the lock state and uses a denser cockpit layout.
- Added direct API regression tests for both locked and unlocked deep-reverse behavior in `tests/test_demo.py`.
- Extended `tools/demo_path_smoke.py` and its test expectations so the new `lever_l4_lock_gate` scenario is part of the GitHub-verifiable demo evidence path.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_interactive_lever_snapshot_wiring tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- The `L4` lock lives in the demo surface rather than `controller.py`, so the controller truth remains unchanged.
- The demo smoke suite now covers 10 scenarios and the shared validation baseline is 162 tests plus 8 shared validation checks.

# P5-08 Summary - Restore Live-Control Wiring For VDT And Conditional TRA Unlock

## Outcome

`P5-08` fixed the real frontend regression introduced by the recent cockpit rearrangement: the moved VDT controls are now wired back into live snapshot recomputation, so the on-screen percentage readout updates again and the TRA deep-reverse band can reopen when the `L4` boundary logic is satisfied.

## What Changed

- Updated `src/well_harness/static/demo.js` so the live-control selector now includes the VDT controls that were moved into the top lever deck, not just the remaining `.condition-panel` inputs.
- Kept the `P5-07` drag-band semantics intact: the browser still shows the full `-32° .. 0°` visual range while limiting free dragging to `-14° .. 0°` until the backend payload reports that the `L4` boundary unlock is ready.
- Extended the existing static regression checks in `tests/test_demo.py` so future layout changes must keep the `.lever-live-grid` controls attached to snapshot rescheduling.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_interactive_lever_snapshot_wiring tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- Root cause was frontend event wiring, not controller truth or backend gate semantics.
- The validated baseline remains `164 tests`, `10 demo smoke scenarios`, and `8` shared validation checks.

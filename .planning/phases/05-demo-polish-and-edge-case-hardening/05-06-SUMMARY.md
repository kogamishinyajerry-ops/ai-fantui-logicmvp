# P5-06 Summary - Finalize TRA Lock Semantics And Same-Screen Cockpit Observation

## Outcome

`P5-06` corrected the remaining behavior gap in the demo cockpit: the browser now stays locked to `-14°..0°` until the current snapshot really reaches the `-14°` lock point with `L4` active, and the desktop layout keeps the VDT controls and right-side logic board in a much more usable same-screen flow.

## What Changed

- Refined `src/well_harness/demo_server.py` so deep reverse travel still probes the `-14°` boundary for backend enforcement, but the browser only unlocks the deeper range after the current snapshot itself reaches that lock point with `L4` active.
- Reworked `src/well_harness/static/demo.html` and `src/well_harness/static/demo.css` so the VDT mode/feedback controls live in the top lever console, the condition panel is shorter, presenter presets are denser, and the desktop logic board is sticky while the left column scrolls.
- Updated `src/well_harness/static/demo.js` so the lock badge communicates the new staged unlock behavior.
- Added regression coverage in `tests/test_demo.py` and kept `tools/demo_path_smoke.py` aligned with the corrected lock semantics.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_server_api_keeps_slider_locked_until_current_snapshot_reaches_minus_14 tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_desktop_first_screen_density_polish tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_interactive_lever_snapshot_wiring tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- The controller truth still remains untouched; this change lives in the demo surface and its presentation layer.
- The validated baseline after this slice is `163 tests`, `10 demo smoke scenarios`, and `8` shared validation checks.
- `P5-07` later clarified the final intended lock interaction: the full visual range remains visible at all times, while only the deep `-32° .. -14°` band stays conditionally closed until the `L4` boundary logic is ready.

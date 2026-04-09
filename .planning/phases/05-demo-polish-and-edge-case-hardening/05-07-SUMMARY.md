# P5-07 Summary - Clarify Conditional TRA Deep-Range Drag And Relax Cockpit Density

## Outcome

`P5-07` corrected the last interaction mismatch in the demo cockpit: the TRA slider now always shows the full `-32° .. 0°` visual range, but free dragging stays inside `-14° .. 0°` until the `L4` boundary unlock is ready. The desktop cockpit was also rebalanced so the lever deck, presets, and condition area feel less crowded while keeping VDT adjustment and the right-side logic board readable together.

## What Changed

- Updated `src/well_harness/static/demo.js` so the browser now clamps live TRA dragging to the currently unlocked band instead of letting the thumb drift into the deep-reverse zone and then snapping back after the API round-trip.
- Refined `src/well_harness/static/demo.html` and `src/well_harness/static/demo.css` so the initial DOM starts in the correct locked state, the desktop cockpit allocates more breathing room to presets and condition controls, and buttons/helper copy feel less cramped.
- Kept `src/well_harness/demo_server.py` on the same `L4` boundary-gate truth model: deep reverse remains locked behind the existing `POST /api/lever-snapshot` evidence plane without changing controller truth or API contracts.
- Extended regression protection in `tests/test_demo.py` so the browser-side unlocked-band clamp and the new desktop spacing cues stay covered by static checks.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_server_api_locks_deeper_reverse_travel_until_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_server_api_unlocks_deeper_reverse_travel_after_logic4_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_server_api_unlocks_deep_range_once_l4_boundary_probe_is_ready tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_desktop_first_screen_density_polish tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_interactive_lever_snapshot_wiring tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- This slice supersedes the temporary `P5-06` interpretation that tied unlock to “the current snapshot must first sit at `-14°`”; the intended behavior is now explicit again: the deep band opens when the `-14°` boundary logic is ready, while the visual range remains full at all times.
- The validated baseline after this slice is `164 tests`, `10 demo smoke scenarios`, and `8` shared validation checks.

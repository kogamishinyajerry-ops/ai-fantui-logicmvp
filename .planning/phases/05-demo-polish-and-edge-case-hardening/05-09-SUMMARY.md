# P5-09 Summary - Restore Intuitive TRA Startup And Drag Direction Semantics

## Outcome

`P5-09` corrected the cockpit's first-contact TRA behavior: the page now starts from a neutral `0°` custom state, the slider copy matches the real left-to-deeper-reverse direction, and the `L4` gate remains intact without making the control feel permanently one-sided.

## What Changed

- Updated `src/well_harness/static/demo.html` so the TRA control now boots at `0°`, with direction labels that match the actual slider range and a startup status that explains the `-14°` conditional boundary clearly.
- Updated `src/well_harness/static/demo.js` so the cockpit initializes as a custom startup state instead of auto-applying the near-threshold `L3 等待 VDT90` preset on page load.
- Preserved the existing presenter presets for deliberate scene switching, while keeping the default page entry point focused on a clean manual drag demonstration.
- Extended the static regression checks in `tests/test_demo.py` so future UI changes must preserve the corrected startup semantics and slider-direction copy.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_lever_presenter_presets tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_showcase_surface_layout tests.test_demo.DemoIntentLayerTests.test_demo_static_assets_include_interactive_lever_snapshot_wiring`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- Root cause was startup interaction design, not a change in controller truth or the backend `L4` gate.
- The validated baseline remains `164 tests`, `10 demo smoke scenarios`, and `8` shared validation checks.

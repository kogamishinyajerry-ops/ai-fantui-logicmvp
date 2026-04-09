# P5-03 Summary - Visible Lever Preset Smoke Sweep

## Outcome

`P5-03` widened the GitHub-verifiable demo smoke suite so the first-screen visible lever presets are now validated through the same HTTP evidence plane as the rest of the presenter demo path.

## What Changed

- Extended `tools/demo_path_smoke.py` from 4 to 8 scenarios.
- Added explicit smoke checks for the visible presets:
  - `L3 等待 VDT90`
  - `RA blocker`
  - `N1K blocker`
  - `VDT90 ready`
- Updated regression tests in `tests/test_demo.py` so the smoke script output and JSON report both protect the wider preset sweep.
- Updated local control-plane state to treat `P5-03` as the active plan.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output tests.test_validation_suite`
- `python3 tools/demo_path_smoke.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- This keeps the presenter presets on the GitHub-verifiable HTTP evidence plane rather than falling back to browser-only confidence checks.
- The next P5 slice can now focus on whichever residual manual-browser expectation is still least automated, without re-proving these core preset jump points.

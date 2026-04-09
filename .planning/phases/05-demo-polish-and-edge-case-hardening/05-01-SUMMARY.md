# P5-01 Summary - GitHub-Verifiable Demo Smoke Suite

## Outcome

`P5-01` introduced `tools/demo_path_smoke.py` and wired it into the shared validation suite so the repo now produces GitHub-verifiable HTTP smoke evidence for the presenter demo path.

## What Changed

- Added a standard-library smoke runner for the local HTTP demo surface.
- Covered four high-value scenarios:
  - controlled `POST /api/demo` bridge prompt
  - clamped extreme lever inputs
  - auto/manual/auto mode switch reset behavior
  - expected invalid `feedback_mode` error handling
- Added subprocess-level regression tests for the smoke script.
- Extended `tools/run_gsd_validation_suite.py` so the smoke suite now runs in the same automation loop as unit and schema checks.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_smoke tests.test_demo.DemoIntentLayerTests.test_demo_path_smoke_script_json_output tests.test_validation_suite`
- `python3 tools/demo_path_smoke.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- The smoke suite intentionally stays on the HTTP evidence plane; it does not drive a browser and does not create a second approval workflow.
- `P5-02` should build on this by widening edge-case coverage or promoting a narrower smoke path into more explicit GitHub-backed confidence checks.

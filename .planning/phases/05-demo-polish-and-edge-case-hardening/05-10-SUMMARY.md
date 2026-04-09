# P5-10 Summary - Add Controlled State-Vs-Time Monitoring Timeline

## Outcome

`P5-10` added a dedicated monitoring surface for the logic panel: the demo now renders a backend-generated `状态 vs 时间` chart for the full `RA -> TRA -> VDT` process without squeezing the existing cockpit controls any further.

## What Changed

- Added `GET /api/monitor-timeline` in `src/well_harness/demo_server.py`, generating a deterministic monitoring trace from the user-defined `RA -> TRA -> VDT` sequence while still evaluating switch and controller states through the current backend logic.
- Added a full-width monitor panel in `src/well_harness/static/demo.html` plus new styling in `src/well_harness/static/demo.css`, so the time-series chart sits in its own roomy section instead of crowding the live cockpit area.
- Added new rendering logic in `src/well_harness/static/demo.js` to fetch the monitoring payload, render event cards, and draw multi-row timeline plots for the monitored chain.
- Extended `tests/test_demo.py` with API, key-time, and static-asset coverage for the new monitoring feature.

## Verification

- `PYTHONPATH=src python3 -m unittest tests.test_demo`
- `PYTHONPATH=src python3 tools/demo_path_smoke.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

## Notes

- `VDT` is drawn as the existing demo feedback percentage (`0% -> 100%`) because that is the current monitored feedback quantity used by the UI and controller-facing snapshot layer.
- The chart extends through the `RA=0 ft` hold segment so the full user-defined `RA` decay is visible even after the active monitoring sequence has already completed.
- The validated baseline after this slice is `167 tests`, `10 demo smoke scenarios`, and `8` shared validation checks.

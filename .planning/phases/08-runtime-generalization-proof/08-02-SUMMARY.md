# P8-02 Summary - Add Adapter-Backed Landing-Gear Playback Proof

- Added `workbench_spec_from_dict(...)` plus `build_playback_report_from_truth_adapter(...)`, so a controller adapter can now publish a spec payload and immediately feed the existing playback contract without going through intake fixtures first.
- Generalized `scenario_playback.py` so discrete states like `UP/DOWN` and compound completion conditions such as `A >= x and B == 1` compile safely into the playback engine instead of assuming every system is already a numeric reference-system clone.
- Added `tools/validate_landing_gear_playback.py` and shared-suite coverage, so the landing-gear adapter now proves an adapter-backed playback trace is both schema-valid and checkpoint-aligned with adapter truth inside the default 20-command regression gate.

## Verification

- `python3 -m py_compile src/well_harness/system_spec.py src/well_harness/scenario_playback.py tools/validate_landing_gear_playback.py tests/test_system_spec.py tests/test_scenario_playback.py tests/test_landing_gear_playback_validation.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_system_spec.py tests/test_scenario_playback.py tests/test_landing_gear_playback_validation.py tests/test_validation_suite.py`
- `python3 tools/validate_landing_gear_playback.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

# P8-06 Summary - Add A Two-System Adapter-Backed Runtime Comparison Report

- Added `well_harness.two_system_runtime_comparison`, so the repo can now emit one machine-readable report comparing the adapter-backed runtime proof chain for the reference thrust-reverser adapter and the landing-gear adapter.
- Added a CLI entrypoint, JSON schema, and validator proving both systems publish metadata/spec, reach playback completion, block their selected fault path, and emit resolved knowledge artifacts through the shared runtime contracts.
- Promoted `tools/validate_two_system_runtime_comparison.py` into `tools/run_gsd_validation_suite.py`, so the default shared suite now guards a 23-command two-system runtime-generalization baseline.

## Verification

- `python3 -m py_compile src/well_harness/system_spec.py src/well_harness/scenario_playback.py src/well_harness/two_system_runtime_comparison.py src/well_harness/cli.py tools/validate_two_system_runtime_comparison.py tests/test_system_spec.py tests/test_scenario_playback.py tests/test_two_system_runtime_comparison.py tests/test_two_system_runtime_comparison_schema.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_system_spec.py tests/test_scenario_playback.py tests/test_two_system_runtime_comparison.py tests/test_two_system_runtime_comparison_schema.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m well_harness.cli two-system-runtime-comparison --format json`
- `python3 tools/validate_two_system_runtime_comparison.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

# P8-03 Summary - Add Adapter-Backed Landing-Gear Diagnosis Proof

- Added `build_fault_diagnosis_report_from_truth_adapter(...)`, so a controller adapter can now drive the existing fault-diagnosis contract directly instead of relying on intake-only entry points.
- Generalized `fault_diagnosis.py` to handle non-numeric discrete states consistently with the playback layer, then proved the landing-gear `hydraulic_pressure_bias_low` fault now produces the expected baseline-vs-fault divergence and blocked logic chain.
- Added `tools/validate_landing_gear_diagnosis.py` plus shared-suite coverage, so adapter-backed diagnosis is now regression-protected inside the default 21-command validation gate.

## Verification

- `python3 -m py_compile src/well_harness/fault_diagnosis.py tools/validate_landing_gear_diagnosis.py tests/test_fault_diagnosis.py tests/test_landing_gear_diagnosis_validation.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_fault_diagnosis.py tests/test_landing_gear_diagnosis_validation.py tests/test_scenario_playback.py tests/test_validation_suite.py`
- `python3 tools/validate_landing_gear_diagnosis.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

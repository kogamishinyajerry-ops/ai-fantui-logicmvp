# P7-70 Summary - Add Second System Smoke Schema Validation To Shared Suite

- Added `tools/validate_second_system_smoke_schema.py`, which runs the default `second-system-smoke --format json` path and validates the resulting payload against `docs/json_schema/second_system_smoke_v1.schema.json`.
- Added `tests/test_second_system_smoke_schema.py` and updated `tests/test_validation_suite.py`, so the second-system smoke report contract is regression-protected in both standalone and shared-suite contexts.
- Updated `tools/run_gsd_validation_suite.py` so second-system-smoke schema validation now runs immediately after the default second-system smoke check.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_second_system_smoke_schema.py tests/test_validation_suite.py tests/test_second_system_smoke.py`
- `python3 tools/validate_second_system_smoke_schema.py --format json`
- `python3 -m py_compile tools/validate_second_system_smoke_schema.py tests/test_second_system_smoke_schema.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`

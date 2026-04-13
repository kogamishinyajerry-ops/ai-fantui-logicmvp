# P7-64 Summary - Add Control System Spec Schema Validation To Shared Suite

- Added `tools/validate_control_system_spec_schema.py`, which validates the CLI reference spec plus fixture/reference intake-generated specs against `docs/json_schema/control_system_spec_v1.schema.json`.
- Added `tests/test_control_system_spec_schema.py` and updated `tests/test_validation_suite.py`, so the root spec contract is regression-protected in both standalone and shared-suite contexts.
- Updated `tools/run_gsd_validation_suite.py` so control-system-spec schema validation is now a first-class shared validation check before downstream playback/diagnosis/knowledge/bundle schema checks.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_control_system_spec_schema.py tests/test_validation_suite.py tests/test_system_spec.py tests/test_document_intake.py`
- `python3 tools/validate_control_system_spec_schema.py --format json`
- `python3 -m py_compile tools/validate_control_system_spec_schema.py tests/test_control_system_spec_schema.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`

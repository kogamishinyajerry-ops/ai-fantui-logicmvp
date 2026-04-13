# P7-65 Summary - Add Fault Taxonomy Schema Validation To Shared Suite

- Added `tools/validate_fault_taxonomy_schema.py`, which validates the published fault taxonomy payload against `docs/json_schema/fault_taxonomy_v1.schema.json`.
- Added a cross-contract check proving `docs/json_schema/control_system_spec_v1.schema.json` keeps its `faultKindValue.enum` aligned with `SUPPORTED_FAULT_KINDS`.
- Added `tests/test_fault_taxonomy_schema.py` and updated `tools/run_gsd_validation_suite.py` / `tests/test_validation_suite.py`, so fault-taxonomy schema validation now runs as a shared check before the root spec schema check.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_fault_taxonomy_schema.py tests/test_validation_suite.py tests/test_fault_taxonomy.py tests/test_system_spec.py`
- `python3 tools/validate_fault_taxonomy_schema.py --format json`
- `python3 -m py_compile tools/validate_fault_taxonomy_schema.py tests/test_fault_taxonomy_schema.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`

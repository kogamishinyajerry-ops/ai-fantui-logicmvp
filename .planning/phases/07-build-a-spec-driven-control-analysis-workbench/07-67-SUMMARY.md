# P7-67 Summary - Add Controller Truth Adapter Metadata Schema Validation To Shared Suite

- Added `tools/validate_controller_truth_adapter_metadata_schema.py`, which validates the reference adapter metadata payload against `docs/json_schema/controller_truth_adapter_metadata_v1.schema.json`.
- Added a cross-contract check proving `current_reference_workbench_spec().source_of_truth` stays aligned with the reference adapter metadata's source-of-truth field.
- Added `tests/test_controller_truth_adapter_metadata_schema.py` and updated `tools/run_gsd_validation_suite.py` / `tests/test_validation_suite.py`, so controller-truth-adapter metadata schema validation now runs as a shared check.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_controller_truth_adapter_metadata_schema.py tests/test_validation_suite.py tests/test_controller_adapter.py tests/test_system_spec.py`
- `python3 tools/validate_controller_truth_adapter_metadata_schema.py --format json`
- `python3 -m py_compile tools/validate_controller_truth_adapter_metadata_schema.py tests/test_controller_truth_adapter_metadata_schema.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`

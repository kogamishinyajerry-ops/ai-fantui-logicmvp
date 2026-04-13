# P7-68 Summary - Add Workbench Archive Manifest Schema Validation To Shared Suite

- Added `tools/validate_workbench_archive_manifest_schema.py`, which generates ready and blocked workbench archives, loads their `archive_manifest.json` files, and validates them through both the internal manifest validator and `docs/json_schema/workbench_archive_manifest_v1.schema.json`.
- Added `tests/test_workbench_archive_manifest_schema.py` and updated `tests/test_validation_suite.py`, so archive manifest schema validation is regression-protected in both standalone and shared-suite contexts.
- Updated `tools/run_gsd_validation_suite.py` so workbench-archive-manifest schema validation now runs after workbench-bundle schema validation.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_archive_manifest_schema.py tests/test_validation_suite.py tests/test_workbench_bundle.py`
- `python3 tools/validate_workbench_archive_manifest_schema.py --format json`
- `python3 -m py_compile tools/validate_workbench_archive_manifest_schema.py tests/test_workbench_archive_manifest_schema.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`

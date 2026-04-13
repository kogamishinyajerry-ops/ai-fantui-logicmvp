# P7-53 Summary - Publish Reusable Fault Taxonomy Contract

- Added `src/well_harness/fault_taxonomy.py` plus `docs/json_schema/fault_taxonomy_v1.schema.json`, publishing the supported fault-kind vocabulary as a reusable machine-readable contract instead of leaving it implicit in runtime `if` chains.
- Tightened `document_intake` and `fault_diagnosis` so both intake parsing and runtime replay reuse the same taxonomy validation boundary, and unknown `fault_kind` values now fail with a helpful contract error.
- Updated `docs/json_schema/control_system_spec_v1.schema.json` and regression coverage so workbench specs now constrain `fault_kind` to the published taxonomy while existing reference and custom packets continue to validate.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_fault_taxonomy.py tests/test_document_intake.py tests/test_fault_diagnosis.py tests/test_system_spec.py`
- `python3 -m py_compile src/well_harness/fault_taxonomy.py src/well_harness/document_intake.py src/well_harness/fault_diagnosis.py tests/test_fault_taxonomy.py tests/test_document_intake.py tests/test_fault_diagnosis.py tests/test_system_spec.py`
- `python3 tools/validate_notion_control_plane.py --format json`

# P7-58 Summary - Publish Reusable Fault Diagnosis Contract

- Updated `src/well_harness/fault_diagnosis.py` so diagnosis reports now emit JSON-safe payloads with explicit `$schema`, `kind`, and `version` metadata instead of an implicit dataclass dump.
- Added `docs/json_schema/fault_diagnosis_v1.schema.json`, documenting the reusable deterministic diagnosis contract, including nested playback-trace payloads.
- Extended `tests/test_fault_diagnosis.py` so generated diagnosis payloads and CLI JSON output both prove the new contract, including optional `jsonschema` validation when available.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_fault_diagnosis.py tests/test_knowledge_capture.py tests/test_workbench_bundle.py`
- `python3 -m py_compile src/well_harness/fault_diagnosis.py tests/test_fault_diagnosis.py`

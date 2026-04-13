# P7-60 Summary - Publish Reusable Knowledge Artifact Contract

- Updated `src/well_harness/knowledge_capture.py` so knowledge artifacts now emit JSON-safe payloads with explicit `$schema`, `kind`, and `version` metadata instead of an implicit dataclass dump.
- Added `docs/json_schema/knowledge_artifact_v1.schema.json`, documenting the reusable knowledge-artifact contract, including nested fault-diagnosis payloads.
- Extended `tests/test_knowledge_capture.py` so generated knowledge payloads and CLI JSON output both prove the new contract, including optional `jsonschema` validation when available.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_knowledge_capture.py tests/test_fault_diagnosis.py tests/test_workbench_bundle.py`
- `python3 -m py_compile src/well_harness/knowledge_capture.py tests/test_knowledge_capture.py`

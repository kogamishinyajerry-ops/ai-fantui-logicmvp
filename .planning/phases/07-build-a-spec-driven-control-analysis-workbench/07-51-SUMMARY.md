# P7-51 Summary - Define System-Agnostic Control System Spec Schema v1

- Added `docs/json_schema/control_system_spec_v1.schema.json`, publishing a Draft 2020-12 contract for reusable control-system workbench specs with explicit schema metadata, components, logic, scenarios, fault modes, clarification items, and knowledge-capture shape.
- Updated `src/well_harness/system_spec.py` so exported workbench specs now include `$schema`, `kind`, and `version`, and normalize tuple-backed dataclass fields into JSON-safe arrays before the payload reaches CLI or intake consumers.
- Extended regression coverage in `tests/test_system_spec.py` and `tests/test_document_intake.py` so reference spec export, intake-generated specs, and optional `jsonschema` validation all prove the same schema-aware payload boundary.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_system_spec.py tests/test_document_intake.py tests/test_cli.py`
- `python3 -m py_compile src/well_harness/system_spec.py src/well_harness/document_intake.py src/well_harness/cli.py tests/test_system_spec.py tests/test_document_intake.py`
- `python3 tools/validate_notion_control_plane.py --format json`

# P7-41 Summary - Add Archive Manifest JSON Schema

- Added `docs/json_schema/workbench_archive_manifest_v1.schema.json` to document the archive manifest kind/version, bundle summary, file map, restore targets, and self-check metadata.
- Regression tests now assert the schema's key constants and, when `jsonschema` is installed, validate a generated archive manifest against the schema.
- The schema JSON file is syntax-checked in verification so future automation can consume it as a standard contract artifact.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py`
- `python3 -m json.tool docs/json_schema/workbench_archive_manifest_v1.schema.json >/dev/null`
- `python3 tools/validate_notion_control_plane.py --format json`

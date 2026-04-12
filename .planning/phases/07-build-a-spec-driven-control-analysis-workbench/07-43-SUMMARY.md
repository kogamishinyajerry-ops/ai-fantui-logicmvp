# P7-43 Summary - Add README Schema Reference

- Generated archive README files now include the archive manifest schema URL in the Archive Manifest section.
- The README schema line reuses the backend `ARCHIVE_MANIFEST_SCHEMA_ID` constant, keeping README prose aligned with generated manifest `$schema`.
- Regression coverage now asserts the generated README includes manifest, schema, and self-check information together.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py`
- `python3 -m json.tool docs/json_schema/workbench_archive_manifest_v1.schema.json >/dev/null`
- `python3 tools/validate_notion_control_plane.py --format json`

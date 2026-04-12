# P7-42 Summary - Add Manifest Schema Reference

- Generated archive manifests now include `$schema: https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json`.
- Manifest validation now checks `$schema` when present while remaining compatible with older manifests that lack it.
- CLI JSON/text output surfaces the schema reference, and the archive manifest JSON Schema now allows the `$schema` property.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py`
- `python3 -m json.tool docs/json_schema/workbench_archive_manifest_v1.schema.json >/dev/null`
- `python3 tools/validate_notion_control_plane.py --format json`

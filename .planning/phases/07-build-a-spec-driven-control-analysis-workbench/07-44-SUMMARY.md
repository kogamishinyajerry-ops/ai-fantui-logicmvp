# P7-44 Summary - Expose Manifest File Map In CLI JSON

- `archive-manifest --format json` now includes the full manifest `files` map, so automation can consume archive artifact paths directly from the validated CLI response.
- Text output remains compact while JSON output carries detailed machine-readable paths.
- Regression coverage now checks that CLI JSON returns the generated bundle and README path entries.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py`
- `python3 -m json.tool docs/json_schema/workbench_archive_manifest_v1.schema.json >/dev/null`
- `python3 tools/validate_notion_control_plane.py --format json`

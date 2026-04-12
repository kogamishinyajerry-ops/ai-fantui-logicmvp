# P7-36 Summary - Add Archive Manifest CLI Validation

- The CLI now includes `archive-manifest`, which validates a workbench `archive_manifest.json` file and returns exit code `0` for valid archives or `1` for invalid manifests.
- The command supports both text and JSON output, including manifest status, issues, bundle summary, file count, archive directory, and restore targets for downstream automation.
- CLI regression tests now cover valid generated archive manifests and invalid archives with missing required files.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py`
- `python3 tools/validate_notion_control_plane.py --format json`

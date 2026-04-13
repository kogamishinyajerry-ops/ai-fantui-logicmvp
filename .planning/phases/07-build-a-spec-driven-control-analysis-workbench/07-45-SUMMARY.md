# P7-45 Summary - Make Archive Manifest Paths Portable

- Newly generated workbench manifests now store `archive_dir` as `.` and keep `files` / `restore_targets` as archive-relative paths such as `bundle.json` and `workspace_snapshot.json`.
- Manifest validation and loading now resolve relative archive paths against the manifest file location, so moved archive directories still validate and self-check successfully.
- Regression coverage now proves the README self-check command still works after moving the archive directory and updates archive/demo assertions to the portable relative-path contract.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/cli.py src/well_harness/demo_server.py tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 tools/validate_notion_control_plane.py --format json`

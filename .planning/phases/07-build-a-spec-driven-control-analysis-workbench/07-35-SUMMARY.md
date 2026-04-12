# P7-35 Summary - Validate Workbench Archive Manifest

- Workbench archive manifests now have backend validation for kind/version, archive metadata, bundle identity, expected file keys, required core files, file existence, archive-directory containment, and restore-target consistency.
- `load_workbench_archive_manifest()` now reads `archive_manifest.json` and rejects malformed manifests with a clear `ValueError` before future restore/sync/audit tooling consumes them.
- Archive bundle regression tests now prove generated manifests validate and load, while missing core files or malformed metadata are flagged.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/demo_server.py`
- `python3 tools/validate_notion_control_plane.py --format json`

# P7-34 Summary - Add Archive Manifest For Workspace Artifacts

- Archive packages now include `archive_manifest.json`, which records bundle identity, archive metadata, file paths, and restore targets in one machine-readable place.
- Archive README files now explicitly point at that manifest as the single file map for restore, sync, or audit tooling.
- The browser archive file list plus archive/demo regression tests now cover the manifest path end to end.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_demo.py`

# P7-48 Summary - Connect Archive Restore In Workbench UI

- Added a browser-side archive restore field and action, so the workbench acceptance surface can now reopen a saved archive package directly from `archive_manifest.json` or the archive directory path.
- Reused the existing workspace snapshot restore path after the archive-restore API returns saved browser state, keeping packet history, result history, and handoff context aligned with the same recovery logic used for local workspace snapshots.
- Hardened the restore contract so directory inputs resolve to `archive_manifest.json`, and regression tests now cover the new UI hooks plus archive-directory restore behavior.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 tools/validate_notion_control_plane.py --format json`

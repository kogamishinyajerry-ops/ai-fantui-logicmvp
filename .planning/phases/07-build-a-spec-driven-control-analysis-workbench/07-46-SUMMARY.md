# P7-46 Summary - Resolve Archive Files And Load Workspace Metadata

- Archive helpers now resolve a validated manifest's relative `files` map into absolute artifact paths, giving restore/sync automation a direct archive file index even after the archive directory moves.
- New loader helpers can reopen `workspace_handoff.json` and `workspace_snapshot.json` through `archive_manifest.json`, so portable archive packages now preserve recoverable browser workspace metadata instead of only a human summary.
- `archive-manifest --format json` now exposes both the relative manifest `files` object and the resolved absolute `resolved_files` map, and regression tests prove the moved-archive restore flow works end to end.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/cli.py src/well_harness/demo_server.py tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 tools/validate_notion_control_plane.py --format json`

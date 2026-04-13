# P7-47 Summary - Add Workbench Archive Restore API

- Added a repo-side archive restore payload helper that reopens `archive_manifest.json` into one object containing the validated manifest, resolved file map, archived bundle JSON, and any saved workspace handoff/snapshot metadata.
- Added `POST /api/workbench/archive-restore` to `well_harness.demo_server`, so moved archive packages now have a stable server entrypoint for later browser or automation restore flows.
- Regression coverage now proves both the helper and the API can reopen a moved archive package and recover its archived browser workspace context.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 tools/validate_notion_control_plane.py --format json`

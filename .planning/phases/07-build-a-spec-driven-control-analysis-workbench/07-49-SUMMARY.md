# P7-49 Summary - List Recent Archives In Workbench UI

- Added bootstrap-side recent archive summaries from the default archive root, so the workbench now receives a live list of valid archive packages it can reopen.
- Added a “最近可恢复的 Archive” board to the browser workbench with one-click restore actions, removing the need to manually hunt for local archive paths before starting recovery.
- Regression coverage now proves recent archive summaries appear in bootstrap payloads and that the new UI hooks are present alongside the existing archive restore flow.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py tests/test_demo.py`
- `python3 tools/validate_notion_control_plane.py --format json`

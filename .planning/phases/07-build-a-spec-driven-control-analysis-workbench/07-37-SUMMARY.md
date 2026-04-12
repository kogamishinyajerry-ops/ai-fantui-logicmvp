# P7-37 Summary - Improve Archive Manifest CLI UX

- `archive-manifest` now accepts either a direct `archive_manifest.json` path or an archive directory and automatically resolves the directory input to the manifest file.
- Text output now includes restore targets, so human handoff can see the browser workspace snapshot, handoff summary, and README restore anchors without reading raw JSON.
- Regression tests cover directory input and restore-target text output while keeping the direct manifest-path command behavior intact.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py`
- `python3 tools/validate_notion_control_plane.py --format json`

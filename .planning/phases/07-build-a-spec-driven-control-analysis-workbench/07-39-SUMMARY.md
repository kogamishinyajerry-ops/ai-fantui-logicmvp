# P7-39 Summary - Add Manifest Self-Check Metadata

- `archive_manifest.json` now includes `self_check` metadata with the directory-relative validation command and the expected archive-directory working context.
- Manifest validation now checks `self_check` shape when present while remaining compatible with older manifests that do not include it.
- CLI JSON/text output now surfaces the self-check command, and regression tests cover generated metadata plus malformed self-check validation.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py`
- `python3 tools/validate_notion_control_plane.py --format json`

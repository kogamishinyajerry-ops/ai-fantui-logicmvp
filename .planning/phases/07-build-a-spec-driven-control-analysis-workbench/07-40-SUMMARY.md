# P7-40 Summary - Verify Archive README Self-Check Command

- Regression coverage now runs the advertised `python3 -m well_harness.cli archive-manifest .` command from inside a generated archive directory.
- The test verifies the command exits successfully, prints `archive_manifest: OK`, and surfaces the self-check command metadata.
- This closes the gap between README/manifest documentation and executable archive validation behavior.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py tests/test_workbench_bundle.py`
- `python3 tools/validate_notion_control_plane.py --format json`

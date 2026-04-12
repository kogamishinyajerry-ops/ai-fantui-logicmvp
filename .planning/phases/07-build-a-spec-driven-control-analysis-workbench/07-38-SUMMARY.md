# P7-38 Summary - Add Archive README Self-Check Command

- Generated archive README files now include `python3 -m well_harness.cli archive-manifest .` in the Archive Manifest section.
- The command is directory-relative, so archive consumers can validate a moved archive package from inside the archive directory without copying a machine-specific path.
- Regression coverage now asserts that generated README files include the self-check command alongside the manifest note.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_workbench_bundle.py tests/test_cli.py tests/test_demo.py`
- `python3 -m py_compile src/well_harness/cli.py src/well_harness/workbench_bundle.py src/well_harness/demo_server.py`
- `python3 tools/validate_notion_control_plane.py --format json`

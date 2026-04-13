# P7-55 Summary - Add Second-System Smoke To Shared Validation Suite

- Updated `tools/run_gsd_validation_suite.py` so the shared validation loop now runs `python3 -m well_harness.cli second-system-smoke --format json` as a ninth repo-wide check.
- Updated `tests/test_validation_suite.py` so the expected shared check inventory now includes `second_system_smoke`.
- Verified the full shared validation suite now passes with 9 checks, and the second-system smoke proof is part of that successful baseline instead of living only as a standalone command.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_validation_suite.py tests/test_second_system_smoke.py tests/test_gsd_notion_sync.py`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 tools/run_gsd_validation_suite.py --format json`
- `python3 tools/validate_notion_control_plane.py --format json`

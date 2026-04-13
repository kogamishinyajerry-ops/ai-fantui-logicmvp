# P7-57 Summary - Add Playback Trace Schema Validation To Shared Suite

- Added `tools/validate_playback_trace_schema.py`, which validates real playback payloads from both the fixture packet and the repo reference packet against `docs/json_schema/playback_trace_v1.schema.json`.
- Added `tests/test_playback_trace_schema.py` and updated `tests/test_validation_suite.py`, so the new validation entry point is regression-protected in both standalone and shared-suite contexts.
- Updated `tools/run_gsd_validation_suite.py` so playback-trace schema validation is now the tenth shared validation check, and the full repo-wide suite passes with that contract enforced.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_playback_trace_schema.py tests/test_validation_suite.py tests/test_scenario_playback.py`
- `python3 tools/validate_playback_trace_schema.py --format json`
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 tools/run_gsd_validation_suite.py --format json`

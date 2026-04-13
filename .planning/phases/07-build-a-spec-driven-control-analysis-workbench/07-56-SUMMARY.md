# P7-56 Summary - Publish Reusable Playback Trace Contract

- Updated `src/well_harness/scenario_playback.py` so playback reports now emit JSON-safe payloads with explicit `$schema`, `kind`, and `version` metadata instead of an implicit dataclass dump.
- Added `docs/json_schema/playback_trace_v1.schema.json`, documenting the reusable deterministic playback-trace contract for downstream tooling and future cross-system consumers.
- Extended `tests/test_scenario_playback.py` so the generated second-system playback payload and CLI JSON output both prove the new contract, including optional `jsonschema` validation when available.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_scenario_playback.py tests/test_workbench_bundle.py tests/test_second_system_smoke.py`
- `python3 -m py_compile src/well_harness/scenario_playback.py tests/test_scenario_playback.py`

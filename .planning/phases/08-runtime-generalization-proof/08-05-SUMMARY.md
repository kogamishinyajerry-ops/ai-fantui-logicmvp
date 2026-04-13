# P8-05 Summary - Connect Second-System Smoke To The Adapter-Backed Runtime Proof

- `well_harness.cli second-system-smoke` now defaults to the landing-gear adapter-backed runtime proof, so the shared second-system smoke entrypoint follows the active P8 chain instead of stopping at the older packet-only bundle flow.
- The smoke contract/schema now records `proof_mode` and `adapter_id`, the default report proves runtime truth alignment plus playback/diagnosis/knowledge continuity, and an explicit `--proof-mode intake-packet` path keeps the legacy packet bundle proof available.
- `tools/validate_second_system_smoke_schema.py` now validates both the new default adapter-backed smoke payload and the retained legacy packet-mode payload, while the control-plane sync text now reflects the new controller/runner/adapter/FlyByWire guardrails before Notion writeback.

## Verification

- `python3 -m py_compile src/well_harness/second_system_smoke.py src/well_harness/cli.py tools/validate_second_system_smoke_schema.py tools/gsd_notion_sync.py tests/test_second_system_smoke.py tests/test_second_system_smoke_schema.py tests/test_gsd_notion_sync.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_second_system_smoke.py tests/test_second_system_smoke_schema.py tests/test_gsd_notion_sync.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m well_harness.cli second-system-smoke --format json`
- `python3 tools/validate_second_system_smoke_schema.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

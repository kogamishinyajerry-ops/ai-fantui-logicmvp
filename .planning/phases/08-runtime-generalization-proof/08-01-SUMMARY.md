# P8-01 Summary - Implement Minimal Landing-Gear Controller Adapter

- Extended `src/well_harness/controller_adapter.py` with a backward-compatible generic truth-evaluation layer, so adapters can now publish a control-system spec and evaluate generic snapshots without disturbing the reference `DeployController` runtime path.
- Added `src/well_harness/adapters/landing_gear_adapter.py`, which publishes schema-valid metadata and a minimal landing-gear extension spec, then evaluates nominal and blocked snapshots through an adapter-only second-system truth path.
- Added `tools/validate_landing_gear_adapter.py` plus focused regression coverage, and promoted the landing-gear adapter proof into `tools/run_gsd_validation_suite.py` so the default shared suite now guards 19 commands instead of 18.

## Verification

- `python3 -m py_compile src/well_harness/controller_adapter.py src/well_harness/adapters/__init__.py src/well_harness/adapters/landing_gear_adapter.py tools/validate_landing_gear_adapter.py tests/test_controller_adapter.py tests/test_landing_gear_adapter.py tests/test_landing_gear_adapter_validation.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_controller_adapter.py tests/test_landing_gear_adapter.py tests/test_landing_gear_adapter_validation.py tests/test_validation_suite.py`
- `python3 tools/validate_landing_gear_adapter.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

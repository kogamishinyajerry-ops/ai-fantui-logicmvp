# P8-04 Summary - Add Adapter-Backed Landing-Gear Knowledge Proof

- Added `build_knowledge_artifact_from_truth_adapter(...)`, so a second-system adapter can now drive the existing knowledge-artifact contract through the diagnosis chain without relying on intake-only entry points.
- Added `tools/validate_landing_gear_knowledge.py` and regression coverage proving the landing-gear adapter produces a resolved knowledge artifact with the expected diagnosis chain embedded.
- Promoted the adapter-backed knowledge proof into `tools/run_gsd_validation_suite.py`, so the default shared suite now guards a 22-command end-to-end runtime generalization baseline.

## Verification

- `python3 -m py_compile src/well_harness/knowledge_capture.py tools/validate_landing_gear_knowledge.py tests/test_knowledge_capture.py tests/test_landing_gear_knowledge_validation.py tools/run_gsd_validation_suite.py tests/test_validation_suite.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_knowledge_capture.py tests/test_landing_gear_knowledge_validation.py tests/test_validation_suite.py`
- `python3 tools/validate_landing_gear_knowledge.py --format json`
- `python3 tools/run_gsd_validation_suite.py --format json`

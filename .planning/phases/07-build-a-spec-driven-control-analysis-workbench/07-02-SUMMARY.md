# P7-02 Summary - Add Mixed-Document Intake And Custom Signal Semantics Assessment

## What Changed

- Added `src/well_harness/document_intake.py` as the first mixed-document intake layer.
- Added a canonical JSON intake template that supports:
  - mixed document references, including PDF entries
  - system-defined signal semantics and units
  - logic nodes, acceptance scenarios, and fault modes
  - explicit clarification answers
- Added CLI commands:
  - `well_harness spec --format json`
  - `well_harness intake --template --format json`
  - `well_harness intake <packet.json> --format text|json`
- Added `tests/fixtures/system_intake_packet_v1.json` as a complete mixed-doc intake example.
- Added `tests/test_document_intake.py` to verify intake loading, readiness assessment, template rendering, and CLI output.

## Why It Matters

- The project now has a real onboarding surface for future systems instead of relying on one-off prompts or hidden assumptions.
- Mixed PDF/markdown source packets are now a first-class concept, even before automatic PDF extraction is implemented.
- The system can explicitly refuse to build a new workbench spec when required clarification answers are missing, which matches the requirement to keep asking until the system is actually understood.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_document_intake.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_system_spec.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_demo.py`

## Follow-On Work

- Add structured timeline normalization that converts intake packets directly into executable monitor-vs-time traces.
- Add diagnosis-report generation that walks the intake-defined logic graph after a fault injection.
- Add document extraction helpers for mixed sources so packet creation can be increasingly automated instead of fully manual.

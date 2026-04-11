# P7-06 Summary - Emit Clarification Follow-Up Briefs For New-System Onboarding

- Added a clarification-brief builder on top of intake assessment, so incomplete onboarding packets now emit a structured follow-up artifact with question status, rationale, gating statement, next actions, and unlock targets.
- Extended `well_harness intake` with `--follow-up`, letting engineers export either the standard readiness assessment or a dedicated clarification brief from the same intake packet.
- Added focused tests covering ready and blocked clarification flows plus the CLI JSON export path, keeping the onboarding gate reproducible and machine-readable.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_document_intake.py tests/test_scenario_playback.py tests/test_fault_diagnosis.py tests/test_knowledge_capture.py`
- `PYTHONPATH=src python3 -m well_harness.cli intake tests/fixtures/system_intake_packet_v1.json --follow-up --format text`

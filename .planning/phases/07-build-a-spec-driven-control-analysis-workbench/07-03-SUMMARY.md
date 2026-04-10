# P7-03 Summary - Compile Intake Scenarios Into Monitor-vs-Time Playback Traces

## Outcome

`P7-03` turns the intake layer into the first real playback engine: a ready mixed-doc packet can now produce deterministic monitor-vs-time traces with signal series, derived logic states, and downstream command outputs.

## What Changed

- Added explicit steady-signal support to acceptance scenarios so held inputs and ramps can coexist in one deterministic playback packet.
- Added a reusable scenario playback engine for intake packets, including time sampling, logic evaluation, downstream output derivation, and event markers.
- Added a CLI surface and focused tests so playback data can be exported as JSON or reviewed as concise text without involving the demo UI.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_document_intake.py tests/test_scenario_playback.py`
- `python3 -m well_harness.cli playback tests/fixtures/system_intake_packet_v1.json --scenario ab_pressure_ramp --sample-period 1.0 --format json`

## Notes

- This slice is intentionally limited to deterministic playback; deeper fault diagnosis and post-repair optimization layers should build on top of this evidence plane in later P7 plans.

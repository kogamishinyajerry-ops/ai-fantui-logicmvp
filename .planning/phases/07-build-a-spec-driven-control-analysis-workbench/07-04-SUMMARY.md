# P7-04 Summary - Inject Fault Modes And Emit Chain Diagnosis Reports

- Added a new `fault_diagnosis.py` engine that reuses playback traces to compare baseline vs fault-injected behavior.
- Added `well_harness diagnose-fault` so a ready intake packet can produce a JSON/text diagnosis report from `scenario_id + fault_mode_id`.
- Added focused tests proving the current mixed-doc fixture can block the logic chain under `pressure_sensor_bias_low` and report the resulting blocker path.
- Expanded intake validation so `reasoning_scope_component_ids` can reference logic nodes as well as components, keeping the spec layer usable for richer future systems.

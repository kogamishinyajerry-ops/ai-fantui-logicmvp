# P15 Pipeline Integration Methodology Note

## FBD-First UI Rule

For any new system panel or major panel revision in the demo/workbench UI:

1. Draft the IEC 61131-3 function block diagram first.
2. Make the FBD carry the exact signal names, thresholds, boolean expressions, and downstream command path taken from the active adapter/controller truth.
3. Implement the matching input panel and help/manual text only after the FBD exists, so the UI mirrors declared control logic instead of inventing hidden rules in the presentation layer.
4. Keep panel labels, thresholds, completion criteria, and monitoring copy aligned with the FBD and adapter source in the same slice.
5. If a subsystem is safety-sensitive or restricted, degrade to a non-operational safety/monitoring note rather than adding new control truth or operator guidance in the UI.

## Why This Exists

P15 connects document/pipeline work back into operator-facing demo surfaces. Requiring the FBD before panel implementation keeps pipeline-generated UI aligned with machine-readable control truth and makes review of thresholds, branch priorities, and feedback paths possible before visual polish lands.

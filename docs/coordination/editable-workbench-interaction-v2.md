# Editable Workbench Interaction v2

Editable Control Workbench Core v1 proved the sandbox model, runtime diff,
ChangeRequest handoff, and acceptance bundle. Interaction v2 makes the workbench
more usable for engineering review without changing certified truth.

## Linear Project

`AI FANTUI LogicMVP · Editable Workbench Interaction v2`

## Issue Chain

- JER-154: Evidence Inspector hardware mapping v1
- JER-161: Sandbox run panel and baseline diff UI
- JER-162: Draft import/export JSON round-trip
- JER-163: Undo/redo and node-edge editing regression v1
- JER-164: Workbench evidence archive download handoff

## JER-154 Rule

JER-154 is not a separate hardware mini-panel. It maps the read-only hardware
evidence sample pack into the `/workbench` Evidence Inspector for the selected
sandbox graph node.

The evidence mapping is overlay-only:

- `truth_effect` remains `none`.
- Unknown cable, connector, and port fields render as explicit
  `evidence_gap` / not-recorded values.
- The inspector may show LRU and signal-binding coverage counts, but those
  values never become control truth.

## JER-161 Rule

JER-161 connects `/workbench` to a deterministic sandbox run endpoint. The
endpoint may derive a sandbox candidate from UI draft metadata, run the
`nominal_landing` timeline fixture, and return a baseline diff verdict.

The result is evidence only:

- Supported verdicts are `equivalent`, `divergent`, `invalid_model`, and
  `invalid_scenario`.
- The baseline remains the certified adapter/controller path.
- Candidate output remains `sandbox_candidate` evidence with truth-level impact
  `none`.
- Invalid draft or scenario input is rendered as a sandbox verdict, not as a
  certified-truth decision.

## Boundaries

- Do not edit `src/well_harness/controller.py` truth semantics.
- Do not edit frozen adapters, frozen hardware YAML, or the C919 reference
  packet.
- Do not promote truth level or make DAL/PSSA claims.
- Do not restore product LLM/chat behavior.
- Do not let UI state, hardware evidence, or draft exports become certified
  truth.

# Editable Control Workbench Core v1 Pivot

## Decision

AI FANTUI LogicMVP now treats the editable control workbench as the product
mainline. The thrust-reverser and C919 surfaces remain valuable reference
systems, but they are no longer the product boundary.

The target product is a sandbox-first engineering workbench: engineers can
derive a draft control graph, edit nodes/ports/edges/hardware bindings, run
candidate scenarios, compare against certified adapter/controller baselines,
and export a controlled ChangeRequest package.

## Authority Boundary

- `src/well_harness/controller.py` remains the certified thrust-reverser
  baseline.
- Editable graphs are always `sandbox_candidate`.
- Hardware bindings in editable models have `truth_effect: none`.
- C919 E-TRAS and other frozen adapters remain read-only unless a separate
  truth-level / freeze review authorizes change.
- Notion is record-only for Codex Daily Lane work. GitHub PR, Linear issue,
  and validation evidence are the daily execution gate.

## Sample Pack Reclassification

JER-150 through JER-153 are reclassified as the first reference sample-pack
track:

- JER-150: read-only hardware evidence registry
- JER-151: hardware evidence report schema
- JER-152: timeline hardware evidence overlay
- JER-153: hardware evidence API endpoint

These artifacts feed the future workbench inspector and evidence panels. They
do not expand certified truth or define the product mainline by themselves.

## Linear Control Plane

Project: `AI FANTUI LogicMVP · Editable Control Workbench Core v1`

Initial issue chain:

- JER-155: pivot foundation, editable model/diff schema, validator/hash, derived seed
- JER-156: sandbox snapshot evaluator and baseline diff
- JER-157: timeline sandbox integration
- JER-158: workbench editable canvas shell v1
- JER-159: ChangeRequest and Linear handoff from draft
- JER-160: end-to-end acceptance

## Stop Rules

Stop and escalate before merging if a PR:

- edits `src/well_harness/controller.py` truth semantics
- edits frozen adapters, frozen hardware YAML, or C919 reference packet
- introduces a hidden hardcoded truth path outside adapter/controller boundaries
- claims DAL/PSSA/truth-level promotion
- lets UI, LLM, or hardware evidence become certified truth
- reports Notion/Opus review as approval for Codex Daily Lane work


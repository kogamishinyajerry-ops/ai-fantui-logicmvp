# Customer Demo MVP Closeout

Date: 2026-05-22
Status: closeout gate definition

## Purpose

This closeout decides whether the current visible demo can be treated as the
Customer Demo MVP candidate for project-owner acceptance.

It combines two gates:

- Project Visibility MVP gate:
  `make project-visibility-mvp-gate`
- Phase 1 Demo MVP gate:
  `make phase1-demo-mvp-gate`
- M21 Pure Canvas Evidence gates:
  `make m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate`
  and `make m21-streamed-authoring-demo-fanout-junction-gate`
- M21 Natural Language Workbench Evidence, extracted from the same M21 gate
  summaries.
- M21 Natural Language Step Confirmation Evidence, extracted from the same M21
  gate summaries.

Single closeout command:

`make customer-demo-mvp-closeout`

## Closeout Claim

If the closeout gate passes, the allowed claim is:

`ready_for_project_owner_acceptance`

This means the current `/demo-reconstruction` surface has a passing browser
evidence bundle, and the project owner also has a separate status entrypoint
for understanding current MVP scope and risk.

## Non-Claims

This closeout does not claim:

- production readiness
- certification or DAL readiness
- controller truth promotion
- Safety Guardian final acceptance
- customer deployment readiness
- external reviewer acceptance
- generalized generation from a new requirements document such as C919 ETRAS

## Acceptance Criteria

The closeout is accepted when:

- Project Visibility MVP gate passes.
- Phase 1 Demo MVP gate passes.
- Phase 1 gate summary verifier passes.
- Browser screenshot artifacts exist for both the project status entrypoint and
  the demo reconstruction route.
- The demo cockpit logic circuit diagram is present as screenshot evidence.
- The demo cockpit logic circuit diagram preserves the expected 20 nodes / 23
  wires surface.
- M21 Pure Canvas Evidence exists for both the C919 fan-out case and the
  demo.html fan-out junction case.
- M21 pure canvas evidence shows `default-display: logic-circuit-only` and
  passing `pure_canvas_presentation_contract` /
  `pure_canvas_framing_contract` gates.
- M21 pure canvas evidence shows no default visible node descriptions, source
  anchors, visible node IDs, or wire labels.
- M21 Natural Language Workbench Evidence shows
  `natural_language_workbench_contract: pass`, the default interaction model is
  natural language, visible action buttons are limited to three or fewer, and
  command palette / mode dock / bottom run controls are hidden by default.
- M21 Natural Language Step Confirmation Evidence shows
  `natural_language_streamed_confirmation_contract: pass` and
  `one_candidate_per_natural_language_submit_contract: pass`, with
  `natural_language_step_visual_framing_contract: pass` proving the active
  candidate is visible on the logic-circuit canvas in the screenshot gate.
- The closeout remains demo evidence only; it does not prove generalized
  requirements-to-control-panel generation.
- The demo surface remains `/demo-reconstruction`.
- Review boundaries preserve `certification_claim: none`.
- No diff appears under `src/well_harness/controller.py`,
  `src/well_harness/editable_control_model.py`, or
  `src/well_harness/static/requirements_intake/`.

## Decision After Closeout

If this gate passes, the next decision should be explicit:

- accept the Customer Demo MVP candidate for project-owner review;
- request external review before acceptance; or
- reject closeout and return to demo polish.

Do not continue M21 queue expansion until that decision is made.

## M21 Pure Canvas Evidence

This closeout also carries M21 presentation evidence. The purpose is narrow:
prove that the logic-builder can enter a pure logic-circuit screenshot mode
where the default UI shows only the circuit diagram, with minimal zoom/exit
controls.

This evidence does not promote any candidate graph into controller truth and
does not modify C919 requirements documents.

## M21 Natural Language Workbench Evidence

This closeout also carries the natural-language workbench gate result. The
purpose is narrow: prove that the default logic-builder workbench is operated
through natural language, while only a very small action surface remains
visible.

The required gate is `natural_language_workbench_contract: pass` for both the
C919 fan-out case and the demo.html fan-out junction case.

## M21 Natural Language Step Confirmation Evidence

This closeout also carries the natural-language step confirmation gate result.
The purpose is narrow: prove that a natural-language prompt opens one pending
candidate, highlights the active graph object and source/logic context, and
does not add a replay event until the engineer confirms or requests revision.

The required gates are `natural_language_streamed_confirmation_contract: pass`
and `one_candidate_per_natural_language_submit_contract: pass` for both the C919
fan-out case and the demo.html fan-out junction case.

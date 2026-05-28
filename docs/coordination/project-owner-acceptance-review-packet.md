# Project Owner Acceptance Review Packet

Date: 2026-05-22
Status: final project-owner decision packet definition

## Purpose

This packet is the final review bundle after Customer Demo MVP Closeout.
It gathers the closeout summary, project status page, screenshots, and
non-claim boundaries into one artifact directory.

Single command:

`make project-owner-acceptance-review-packet`

Default artifact directory:

`/tmp/ai-fantui-project-owner-acceptance-review-packet`

## Packet Contents

The packet must include:

- Customer Demo MVP closeout JSON
- Customer Demo MVP closeout Markdown
- project-owner status HTML page
- project-owner status screenshot
- logic circuit diagram screenshot from the demo cockpit
- demo reconstruction screenshots
- M21 Pure Canvas Evidence screenshots and gate summaries
- M21 Natural Language Workbench Evidence from the same M21 gate summaries
- M21 Natural Language Step Confirmation Evidence from the same M21 gate
  summaries
- non-claim boundary declaration
- final decision options

## Required Gates

The packet is valid only when:

- Customer Demo MVP closeout passes.
- Closeout status is `ready_for_project_owner_acceptance`.
- The project status HTML exists.
- The status screenshot exists.
- The logic circuit diagram screenshot exists.
- The logic circuit diagram evidence shows the expected 20 nodes / 23 wires
  demo surface.
- M21 Pure Canvas Evidence includes C919 fan-out and demo.html fan-out
  screenshots in pure circuit-only presentation mode.
- M21 evidence shows `default-display: logic-circuit-only`,
  `pure_canvas_presentation_contract: pass`, and
  `pure_canvas_framing_contract: pass`.
- M21 Natural Language Workbench Evidence shows
  `natural_language_workbench_contract: pass`, a default natural-language input
  model, no more than three visible action buttons, and hidden command palette /
  mode dock / bottom run controls.
- M21 Natural Language Step Confirmation Evidence shows
  `natural_language_streamed_confirmation_contract: pass` and
  `one_candidate_per_natural_language_submit_contract: pass`, plus
  `natural_language_step_visual_framing_contract: pass` so the active candidate
  remains visible on the logic-circuit canvas in review screenshots.
- At least one demo reconstruction screenshot exists.
- Review boundaries preserve `certification_claim: none`.
- No diff appears under `src/well_harness/controller.py`,
  `src/well_harness/editable_control_model.py`, or
  `src/well_harness/static/requirements_intake/`.

## Decision Options

The packet intentionally ends at a project-owner decision point:

1. Accept: accept the Customer Demo MVP candidate for project-owner review.
2. External review: request external review before acceptance.
3. Demo polish: reject closeout and return to demo polish.

Do not continue M21 queue expansion until one of these three decisions is made.

If the selected path is external review, generate the read-only handoff with:

`make project-owner-external-review-handoff`

That handoff asks the reviewer to choose exactly one of `accept_evidence`,
`needs_changes`, or `reject_evidence` without modifying the repository.

## M21 Pure Canvas Evidence

The packet carries the M21 pure-canvas gate outputs as review evidence only. It
proves that the current logic-builder can hide non-diagram UI by default in
presentation mode and show only the logic circuit diagram plus minimal zoom and
exit controls.

This packet still does not claim generalized requirements-to-control-panel
generation for new domains such as C919 ETRAS.

## M21 Natural Language Workbench Evidence

The packet also carries the M21 natural-language workbench gate outputs as
review evidence. It proves only that the current logic-builder defaults to a
natural-language input model with an intentionally small visible action surface.

The required gate is `natural_language_workbench_contract: pass` for both the
C919 fan-out case and the demo.html fan-out junction case.

## M21 Natural Language Step Confirmation Evidence

The packet also carries the M21 natural-language step confirmation gate outputs
as review evidence. It proves only that a natural-language prompt opens one
pending candidate, highlights the active graph object and source/logic context,
and leaves replay empty until the engineer makes a decision.

The required gates are `natural_language_streamed_confirmation_contract: pass`
and `one_candidate_per_natural_language_submit_contract: pass` for both the C919
fan-out case and the demo.html fan-out junction case.

## Non-Claims

This packet does not claim:

- production readiness
- certification or DAL readiness
- controller truth promotion
- Safety Guardian final acceptance
- external reviewer acceptance
- customer deployment readiness
- generalized requirements-to-control-panel generation for new domains such as
  C919 ETRAS

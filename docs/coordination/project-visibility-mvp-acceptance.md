# Project Visibility MVP Acceptance

Date: 2026-05-22
Status: formal project-owner entrypoint gate

## Purpose

This gate freezes the current project-owner entrypoint for the active MVP.
It does not promote candidate logic into controller truth and does not make a
customer-facing product claim.

Formal entrypoint:

`/tmp/ai-fantui-project-visibility-mvp-acceptance/project-manager-status-summary/project_manager_status_summary.html`

Formal command:

`make project-visibility-mvp-gate`

## Acceptance Criteria

The Project Visibility MVP is accepted when the gate proves all of these:

- The project-owner status summary generator passes.
- The HTML entrypoint exists and renders in a browser from a `file://` URL.
- A desktop screenshot is captured and is non-empty.
- The rendered page shows `Multi-Agent Candidate Repair Pipeline MVP`.
- The rendered page shows `RUN-QUEUE-010`.
- The rendered page shows `CHECK_UNREACHABLE_STATE_001`.
- The rendered page shows `Project Visibility MVP` as the recommended next
  visibility option.
- The rendered page shows the current decision: do not continue M21 immediately.
- The gate reports no controller truth or requirements-intake UI diff.

## Out Of Scope

- Editing `src/well_harness/controller.py`
- Editing `src/well_harness/editable_control_model.py`
- Editing `src/well_harness/static/requirements_intake/`
- Adding a live dashboard server
- Claiming certification, DAL readiness, or trusted controller truth
- Closing the customer-facing demo MVP

## Decision After Gate

If this gate passes, the next project decision is explicit:

- Option A: continue Project Visibility MVP with a richer dashboard shell.
- Option B: switch to Customer Demo MVP Closeout.
- Option C: continue M21 queue expansion.
- Option D: freeze and request external review.

The recommended decision remains: Do not continue M21 immediately. Finish the
visibility entrypoint first, then choose between demo closeout, external review,
or more queue depth.

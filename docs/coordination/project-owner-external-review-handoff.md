# Project Owner External Review Handoff

Date: 2026-05-22
Status: ready-for-review handoff definition

## Purpose

This handoff freezes the current project-owner acceptance packet for a
read-only external reviewer. It does not accept the MVP, approve controller
truth, or continue M21 queue expansion.

Single command:

`make project-owner-external-review-handoff`

Default artifact directory:

`/tmp/ai-fantui-project-owner-external-review-handoff`

## Handoff Contents

The handoff must include:

- project-owner acceptance packet JSON
- project-owner acceptance packet Markdown
- Customer Demo MVP closeout JSON
- Customer Demo MVP closeout Markdown
- project status HTML entrypoint
- demo first-screen screenshot
- logic circuit diagram screenshot
- copy-paste external review prompt

## Required Gates

The handoff is valid only when:

- The project-owner packet status is `ready_for_project_owner_decision`.
- The handoff status is `ready_for_read_only_external_review`.
- The logic circuit diagram screenshot exists.
- The logic circuit diagram evidence shows the expected 20 nodes / 23 wires
  demo surface.
- The `/demo-reconstruction` route has browser screenshot evidence.
- Review boundaries preserve `certification_claim: none`.
- No diff appears under `src/well_harness/controller.py`,
  `src/well_harness/editable_control_model.py`, or
  `src/well_harness/static/requirements_intake/`.

## Reviewer Contract

The reviewer must work in read-only mode:

- Do not modify repository files.
- Do not approve controller truth promotion.
- Do not claim production readiness.
- Do not claim certification or DAL readiness.
- Do not claim customer deployment readiness.
- Base findings only on the listed evidence artifacts.

The reviewer must return exactly one verdict:

- `accept_evidence`
- `needs_changes`
- `reject_evidence`

The reviewer result can be verified with:

`PROJECT_OWNER_EXTERNAL_REVIEW_RESULT_PATH=/path/to/review.json make project-owner-external-review-result`

Result-intake doc:

`docs/coordination/project-owner-external-review-result.md`

## Review Questions

1. Does the packet contain closeout JSON and Markdown?
2. Does the logic circuit diagram evidence exist and show 20 nodes / 23 wires?
3. Does the `/demo-reconstruction` route have browser screenshot evidence?
4. Are non-claims and boundaries clear enough to prevent over-claiming?
5. Is this evidence safe to send for project-owner acceptance?

## Stop Condition

Do not treat external review output as project-owner acceptance. After review,
the project owner still must choose one of `accept`, `external_review`, or
`demo_polish` from the acceptance packet.

# Project Owner Final Decision

Date: 2026-05-22
Status: final-decision gate definition

## Purpose

This gate verifies a project-owner decision JSON after the acceptance packet
and optional external review evidence are ready. It records a decision but does
not invent one.

Single command:

`PROJECT_OWNER_FINAL_DECISION_PATH=/path/to/decision.json make project-owner-final-decision`

Default decision path:

`/tmp/ai-fantui-project-owner-external-review-handoff/project_owner_final_decision.json`

## Decision Shape

The decision JSON must include:

- `kind: ai-fantui-project-owner-final-decision`
- `decision`: one of `accept`, `external_review`, or `demo_polish`
- `rationale`: non-empty string
- `source_review_verdict`: `accept_evidence` when decision is `accept`
- `accepted_non_claims`: the non-claim boundaries acknowledged for this
  decision
- `project_owner_attestation.role: project_owner`
- `project_owner_attestation.selected_option`: same value as `decision`
- `project_owner_attestation.decision_is_final: true`
- `project_owner_attestation.acknowledged_non_claims`: same non-claim boundary
  set

## Accept Rules

`accept` is valid only when:

- the project-owner acceptance packet is `ready_for_project_owner_decision`;
- external review result verification passes;
- external review result status is `external_review_accepts_evidence`;
- the project-owner attestation acknowledges there is no certification,
  production, deployment, or controller truth promotion claim.

When valid, final acceptance is:

`granted_for_customer_demo_mvp_evidence_only`

## Non-Accept Rules

`external_review` keeps final acceptance as `not_granted` and records that
external review is still requested.

`demo_polish` keeps final acceptance as `not_granted` and records that the
candidate returns to demo polish.

## Stop Condition

M21 queue expansion is unblocked only when the verified decision status is
`customer_demo_mvp_accepted`.

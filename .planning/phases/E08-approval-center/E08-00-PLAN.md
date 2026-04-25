# E08 Plan - Proposal Submit + Approval Center

## Objective

Turn E07 annotation drafts into submit-ready proposal records with a Kogami-only approval triage flow and hash-chained audit events for submitted, accepted, and rejected proposal actions.

## Scope

- Add Workbench approval endpoint logic under `src/well_harness/workbench/`.
- Add audit event append/chain support for:
  - `proposal.submitted`
  - `proposal.accepted`
  - `proposal.rejected`
- Add a Kogami-only Approval Center panel to the Workbench shell with Pending / Accept / Reject lanes.
- Add tests for proposal submit, Kogami-only triage, audit hash chaining, and static approval UI anchors.
- Create `audit/events.jsonl` with the Workbench proposal event schema extension marker.

## Counterarguments And Mitigations

1. Counterargument: the prompt asks for a submit endpoint but restricts further route mounts in `demo_server.py`.
   Mitigation: implement endpoint semantics in the new Workbench package, keep the legacy server file untouched after the E06 route alias, and document that HTTP mounting remains outside this allowed slice.

2. Counterargument: approval status could become mutable without traceability.
   Mitigation: every submit/accept/reject action appends an audit event with `previous_hash` and `event_hash`.

3. Counterargument: Kogami-only approval can be bypassed if only enforced in the UI.
   Mitigation: backend triage code rejects non-Kogami actors regardless of UI state.

4. Counterargument: committing runtime audit/proposal records may pollute source truth.
   Mitigation: only a schema-extension marker is committed in `audit/events.jsonl`; proposal JSON remains ignored under `data/proposals/`.

## Success Criteria

- Submitting a valid proposal persists it and appends `proposal.submitted`.
- Kogami can accept or reject pending proposals and emits the matching audit event.
- Non-Kogami triage attempts are rejected.
- Workbench page exposes Pending / Accept / Reject UI anchors.
- Existing fast-lane, e2e, and adversarial checks remain green at closure.

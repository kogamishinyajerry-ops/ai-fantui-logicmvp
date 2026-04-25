# E10 Plan - PR Review And Merge/Close Loop

## Objective

Close the Workbench collaboration loop with a ticket-aware PR diff reviewer, a merge/close stub, audit event expansion, and a committed demo run showing proposal -> ticket -> diff review -> close evidence.

## Scope

- Add `src/well_harness/workbench/pr_review.py` for ticket + diff verdict reports.
- Add `src/well_harness/collab/merge_close.py` as a non-mutating merge/close flow stub.
- Extend Workbench audit event support for:
  - `pr.submitted`
  - `pr.accepted`
  - `pr.rejected`
  - `ticket.closed`
- Append the E10 audit schema-extension marker to `audit/events.jsonl` without rewriting E08 content.
- Add a committed demo run under `runs/workbench_e2e_<timestamp>/`.
- Add focused PR close-loop tests.

## Counterarguments And Mitigations

1. Counterargument: a real merge bot would be more complete.
   Mitigation: implement an explicit stub that produces auditable merge/close intent without mutating GitHub state or pretending to have merged.

2. Counterargument: diff parsing can be brittle.
   Mitigation: only use stable unified diff headers (`diff --git` and `+++ b/...`) and fail closed when no files can be extracted.

3. Counterargument: verdicts could ignore ticket scope.
   Mitigation: PR review reuses the restricted-auth scope matcher and reports out-of-scope files as rejection findings.

4. Counterargument: demo evidence can become fabricated if not traceable.
   Mitigation: commit concrete ticket, proposal, diff, verdict, and close-plan artifacts in the run directory and document that no live merge occurred.

## Success Criteria

- Ticket + in-scope diff produces an accepted structured verdict report.
- Ticket + out-of-scope diff produces a rejected structured verdict report with findings.
- Merge/close stub appends PR and ticket audit events without performing a live merge.
- Demo evidence directory is committed.
- Existing fast-lane, e2e, and adversarial checks remain green at closure.

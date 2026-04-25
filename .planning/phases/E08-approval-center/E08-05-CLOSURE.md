# E08 Closure - Approval Center

## What Shipped

- Added `src/well_harness/workbench/audit.py` for hash-chained proposal audit events.
- Added `src/well_harness/workbench/approval.py` with Workbench-owned proposal submit, pending queue, accept, and reject semantics.
- Enforced Kogami-only approval/rejection in backend code through `WorkbenchPermissionError`.
- Added a Kogami Approval Center panel to the Workbench shell with Pending / Accept / Reject lanes.
- Created `audit/events.jsonl` with the E08 proposal event schema-extension marker:
  - `proposal.submitted`
  - `proposal.accepted`
  - `proposal.rejected`
- Added focused approval/audit/static tests.

## Verification Numbers

- Fast-lane pytest: `812 passed, 1 skipped, 49 deselected, 1 warning in 62.76s`
- E2E pytest: `49 passed, 813 deselected, 1 warning in 2.88s`
- Adversarial browser/server script: `ALL TESTS PASSED` across 8 adversarial sections
- Diff hygiene: `git diff --check` passed

The non-e2e count increased from E07 by four approval tests.

## Open Issues

- No new HTTP route was mounted in `demo_server.py`; the prompt allowed only the E06 `/workbench` route addition in that file. E08 therefore implements endpoint semantics in the Workbench package, ready for a future route mount if Kogami expands the allowed file domain.
- The static Approval Center exposes triage lanes but does not yet call the package endpoint over HTTP.
- The committed `audit/events.jsonl` contains only the schema-extension marker; runtime submit/triage events are created by `AuditEventLog` during local execution.

## Handoff Notes

- E09 can use proposal IDs and proposal payloads from `ProposalStore` as prompt-generator inputs.
- Keep proposal approval authority in backend code, not only in the UI.
- Do not add a second audit mechanism; extend `AuditEventLog` in E10 for PR and ticket events.

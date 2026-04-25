# Workbench Epic-06..10 Handover

## Status

Workbench Epic-06 through Epic-10 are implemented on the rolling branch `feat/epic06-workbench-shell-20260425-r2` and PR #3.

The implementation is intentionally local-first:

- no Notion writes
- no live GitHub merge
- no controller truth edits
- no adapter truth edits
- no changes to existing wow scripts, pitch materials, or Parking Lot items

## What Shipped

### Epic-06 - Workbench Shell

- `/workbench` route alias for the existing Workbench static page.
- Top bar with identity, active ticket, and system selector.
- Three independent Workbench columns:
  - control panel
  - document review surface
  - circuit review surface
- Annotation Inbox skeleton.
- Kogami-only Approval Center entry.
- Failure-isolated column boot behavior.

### Epic-07 - Canvas Annotation

- Four annotation tools:
  - point
  - area
  - link
  - text-range
- Annotation surfaces on all three Workbench columns.
- `AnnotationProposal` JSON schema.
- Local proposal model, validation, and file store.
- Runtime proposal records ignored under `data/proposals/`.

### Epic-08 - Approval Center

- Workbench-owned proposal submit semantics.
- Kogami-only accept/reject backend enforcement.
- Approval Center panel with Pending / Accept / Reject lanes.
- Hash-chained audit events for:
  - `proposal.submitted`
  - `proposal.accepted`
  - `proposal.rejected`

### Epic-09 - Prompt, Ticket, Restricted Auth

- Claude Code prompt template with required sections:
  - anchor
  - scope
  - acceptance
  - non-goals
- Proposal-to-prompt renderer.
- Local ticket publisher that writes `tickets/*.json` and prints paste-ready JSON to stdout.
- Restricted-auth middleware:
  - actor must match `Authorized Engineer`
  - changed files must match `Scope Files`
- 02 task DB schema check passed before implementation; required fields were present.

### Epic-10 - PR Review And Close Loop

- PR review CLI and library:
  - ingests ticket JSON and unified diff
  - extracts changed files
  - verifies ticket scope
  - outputs structured verdict JSON
- Merge/close stub:
  - records auditable intent
  - does not perform live merge
  - does not mutate Notion
- Audit event support for:
  - `pr.submitted`
  - `pr.accepted`
  - `pr.rejected`
  - `ticket.closed`
- Demo evidence committed at `runs/workbench_e2e_20260425T040608Z/`.

## Demo Flow

1. Open `/workbench`.
2. Use the top bar to confirm identity, ticket, and system context.
3. Pick an annotation tool and click one of the three Workbench surfaces.
4. Confirm the draft appears in the Annotation Inbox.
5. Submit/triage through the local Workbench approval semantics.
6. Generate a Claude Code prompt and ticket payload from the proposal.
7. Review a candidate PR diff against the ticket scope.
8. Produce a merge/close plan and audit chain.

The committed demo run follows the same local path:

- `runs/workbench_e2e_20260425T040608Z/proposal.json`
- `runs/workbench_e2e_20260425T040608Z/ticket.json`
- `runs/workbench_e2e_20260425T040608Z/candidate.diff`
- `runs/workbench_e2e_20260425T040608Z/verdict.json`
- `runs/workbench_e2e_20260425T040608Z/merge_close_plan.json`
- `runs/workbench_e2e_20260425T040608Z/close_result.json`
- `runs/workbench_e2e_20260425T040608Z/audit_events.jsonl`

## Validation History

- Locked baseline: `796 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`
- E06 close: `802 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`
- E07 close: `808 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`
- E08 close: `812 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`
- E09 close: `815 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`
- E10 close: `819 passed, 1 skipped, 49 deselected` / `49 passed` / adversarial `8/8`

## Known Limitations

- E08 endpoint semantics are implemented in `src/well_harness/workbench/` but not mounted into `demo_server.py`, because the allowed file domain only permitted the E06 `/workbench` route addition in that file.
- Browser-created E07 drafts are local UI drafts; server-side proposal submission is exercised through the Workbench package semantics and tests.
- Restricted auth is middleware, not an installed GitHub branch protection rule or remote Git hook.
- Merge/close is a stub that records intent and audit events; it does not merge PRs.
- Screenshots/asciinema were not committed; the evidence bundle is file-based and test-backed.

## Review Entry Points

- PR: https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/pull/3
- Branch: `feat/epic06-workbench-shell-20260425-r2`
- Workbench page: `/workbench`
- Demo evidence: `runs/workbench_e2e_20260425T040608Z/`
- Planning closures:
  - `.planning/phases/E06-workbench-shell/E06-05-CLOSURE.md`
  - `.planning/phases/E07-canvas-annotations/E07-05-CLOSURE.md`
  - `.planning/phases/E08-approval-center/E08-05-CLOSURE.md`
  - `.planning/phases/E09-prompt-ticket-auth/E09-05-CLOSURE.md`
  - `.planning/phases/E10-pr-review-close-loop/E10-05-CLOSURE.md`

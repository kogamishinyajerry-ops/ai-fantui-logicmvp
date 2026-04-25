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

## Post-merge Observation List

Three observable behaviours that the closed E06–E10 stack does not exercise in unit / e2e / adversarial coverage and that should be watched once PR #3 is merged into `main`. None are blockers for merge; each is an invariant whose breakage would surface only outside the existing test windows.

### 1. Long-idle canvas memory stability

**Why this is a gap:** The annotation overlay (`src/well_harness/static/annotation_overlay.js`) keeps draft markers and Annotation Inbox state in browser memory. Existing tests assert structural correctness over short-lived requests; nothing exercises a multi-hour idle session where the same Workbench tab keeps overlays mounted, drafts accumulate, and DOM listeners remain bound.

**When to observe:** On the next dress-rehearsal day or any demo machine that boots `/workbench` early in the morning and reaches the demo slot 4–8 hours later without page reload.

**How to observe:**

```bash
# leave Workbench open on /workbench in Chrome with DevTools Performance Monitor
# baseline at T+0, then sample at T+1h, T+4h, T+8h
# expected: JS heap growth < 25 MB across 8h with no triage actions
# escalation trigger: heap > 200 MB OR any "DOM Nodes" line monotonically rising
```

If heap creeps, capture a heap snapshot and check for retained `AnnotationDraft` instances; the prime suspect is the Inbox renderer not releasing draft references after triage.

### 2. Multi-tab restricted-auth lock convergence

**Why this is a gap:** `src/well_harness/collab/restricted_auth.py` enforces the `Authorized Engineer` + `Scope Files` invariants per call, but two tabs of `/workbench` open against the same demo_server can each generate ticket prompts concurrently. Existing tests are single-actor, single-tab. A real reviewer scenario (two reviewer tabs + one engineer tab) is not exercised.

**When to observe:** Any time more than one human is reviewing simultaneously, especially during dress rehearsal where Kogami may have the canvas open while another reviewer drives the Approval Center.

**How to observe:**

```bash
# Tab A and Tab B both load /workbench against http://127.0.0.1:8799
# Tab A: submit a proposal → ticket published
# Tab B: within 2 seconds, attempt to submit a different proposal targeting
#        an overlapping Scope File set
# expected: second submission either (a) wins cleanly with hash-chain order
#           preserved, or (b) is rejected with a structured WorkbenchPermissionError
# regression signal: silent acceptance with hash-chain fork OR last-write-wins
#                    where Tab A's proposal disappears from the pending lane
```

The audit-events.jsonl line ordering is the truth source: parse it after the test and confirm each `proposal.submitted` precedes its corresponding `proposal.accepted` / `proposal.rejected` and that no two events share the same `prev_hash`.

### 3. 02 task DB seven-field round-trip

**Why this is a gap:** E09 closure recorded a one-time schema check confirming the seven required fields exist in the 02 task DB (`Type`, `Source Proposal`, `Authorized Engineer`, `Scope Files`, `Generated Prompt`, `PR URL`, `Verdict`). The check ran against the schema, not against runtime read+write behaviour. PR #3 deliberately does not write to Notion. After merge, the first real engineer-facing run will be the first time the local ticket payload meets the live DB.

**When to observe:** First post-merge ticket flow that produces a `tickets/*.json` and is then manually mirrored into the Notion 02 task DB (per HANDOVER §Status: "no Notion writes" — sync is Kogami-driven).

**How to observe:**

```bash
# After Kogami creates the first 02 task DB row from a tickets/*.json:
# 1. Read back the Notion row and dump it as JSON.
# 2. Run a structural diff against the source ticket payload:
diff <(jq -S . tickets/<ticket_id>.json) \
     <(notion-export 02 <row_id> | jq -S 'del(.last_edited_time, .created_time)')
# expected: every key from the seven-field set round-trips byte-for-byte
#           after stripping Notion-managed timestamps
# regression signal: missing fields, type coercion (string→list, list→string),
#                    or truncated `Generated Prompt` on the Notion side
```

If the round-trip fails, the failure mode and exact field is the diagnostic — the 02 DB schema is the contract surface that future Workbench↔Notion sync work will build on, so any drift here must be caught before downstream automation is layered on top.

# P43 Workflow Automaton Contract

**Version**: 1.0  
**Authority**: P43-00 §3c · P43-02 Step 3a/A  
**Date**: 2026-04-21  
**Status**: Active — governs P43-02 through P43-10 execution  

---

## §1. Purpose

This document is the normative specification for the P43 workbench workflow state machine. It defines:

- The complete **state enum** and its semantics
- The **event list** with legal pre-state/post-state pairs
- The **transition table** (state × event legality matrix)
- The **error taxonomy** and recovery rules
- The **idempotency classification** per event
- The **persistence model** (two-source invariant)
- The **side-effect ordering** for destructive events
- The **cross-phase test ownership** map

The companion machine-readable specification is `docs/P43-workflow-automaton.yaml`.  
The authority contract (R1-R6 mechanical rules) lives in `P43-00 §3e`; tests live in `tests/test_p43_authority_contract.py` (P43-02 Step 3a/B deliverable).

---

## §2. State Enum

| State | Meaning | Entry condition |
|-------|---------|-----------------|
| `INIT` | Workbench loaded, no document imported | Session start or explicit reset |
| `INTAKED` | Document received; pre-processing queued | `import_doc` event from `INIT` |
| `PARSING` | LLM/parser extracting ambiguities from document | Internal transition from `INTAKED` or `reiterate` |
| `AWAITING_ANSWERS` | ≥1 open clarification question emitted; waiting operator | `PARSING` completes with ambiguities |
| `FREEZING` | All clarifications answered or waived; freeze guard in progress | All questions resolved in `AWAITING_ANSWERS` |
| `FROZEN` | Frozen spec produced, SHA-locked, immutable | `confirm_freeze` from `AWAITING_ANSWERS` or `FREEZING` |
| `GENERATING` | Panel SVG + wiring scaffold generation in progress | `start_gen` from `FROZEN` |
| `PANEL_READY` | Generated panel rendered; no active edits | `GENERATING` completes |
| `WIRING` | Operator actively editing signal wiring | `wire_change` from `PANEL_READY`, `WIRING`, or `DEBUGGING` |
| `DEBUGGING` | Snapshot submitted; diff/validation active | `submit_snapshot` from `WIRING` |
| `ANNOTATING` | Operator adding semantic annotations to panel | `annotate` from `PANEL_READY`, `WIRING`, or `ANNOTATING` |
| `ITERATING` | `reiterate` event fired; transitioning back to re-freeze | Transient — resolves to `PARSING` within same tick |
| `APPROVING` | `final_approve` side-effect sequence in flight (steps ①–④) | `final_approve` from `PANEL_READY` or `ANNOTATING` |
| `APPROVED` | All side-effects committed; workbench complete | Side-effect sequence ① → ④ all succeeded |
| `ARCHIVING` | `archive` event fired; bundle being written | `archive` from `APPROVED` |
| `ARCHIVED` | Bundle + manifest committed to disk/registry | `ARCHIVING` completes |
| `ERROR` | Unrecoverable fault; error taxonomy entry emitted | Any state on unhandled exception |

**Terminal states**: `APPROVED`, `ARCHIVED` (normal), `ERROR` (fault).  
`ITERATING` is a **transient state**: it MUST resolve to `PARSING` within the same event-handling tick. No async operations may be dispatched from `ITERATING`.

---

## §3. Event List

Each event lists: legal pre-states → post-state, guard condition, idempotency class.

### `import_doc`
| Field | Value |
|-------|-------|
| Legal pre-states | `INIT` |
| Post-state (success) | `INTAKED` |
| Post-state (failure) | `ERROR` (`pdf_extract_failure`) |
| Guard | File size > 0; MIME ∈ {application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document} |
| Idempotency | **Non-idempotent** — deduplication token: SHA-256 of file bytes; duplicate SHA within session → no-op + log.warning |

### `answer_question`
| Field | Value |
|-------|-------|
| Legal pre-states | `AWAITING_ANSWERS` |
| Post-state (partial) | `AWAITING_ANSWERS` (remaining open questions > 0) |
| Post-state (complete) | `FREEZING` (all questions answered or operator-waived) |
| Guard | question_id ∈ open questions set; answer non-empty string OR waive=true with operator alias |
| Idempotency | **Idempotent** — re-answering same question_id with same answer is a no-op |

### `confirm_freeze`
| Field | Value |
|-------|-------|
| Legal pre-states | `AWAITING_ANSWERS`, `FREEZING` |
| Post-state (success) | `FROZEN` |
| Post-state (failure) | `ERROR` (`ambiguity_unresolved`) |
| Guard | All questions answered OR explicitly waived with `operator_alias` field present |
| Idempotency | **Idempotent** — if already `FROZEN` with same SHA, no-op |
| Side-effect | Produce frozen spec JSON; compute SHA-256; write `docs/<system_id>/traceability_matrix.md` skeleton |

### `start_gen`
| Field | Value |
|-------|-------|
| Legal pre-states | `FROZEN` |
| Post-state (success) | `GENERATING` → `PANEL_READY` |
| Post-state (failure) | `ERROR` (`regen_failure`) |
| Guard | frozen_spec SHA present and non-null |
| Idempotency | **Non-idempotent** — each call triggers a new LLM generation; deduplication token: (frozen_spec_sha, gen_round_counter) |

### `wire_change`
| Field | Value |
|-------|-------|
| Legal pre-states | `PANEL_READY`, `WIRING`, `DEBUGGING` |
| Post-state | `WIRING` |
| Guard | Signal wiring payload non-empty; target node_id ∈ spec.components ∪ spec.logic_nodes |
| Idempotency | **Idempotent** — same (node_id, signal_value) pair → no-op |

### `submit_snapshot`
| Field | Value |
|-------|-------|
| Legal pre-states | `WIRING`, `DEBUGGING` |
| Post-state (pass) | `PANEL_READY` |
| Post-state (fail) | `DEBUGGING` |
| Guard | Snapshot dict non-empty; system_id matches current workbench system |
| Idempotency | **Non-idempotent** — each submit triggers server-side `evaluate_snapshot`; deduplication token: SHA-256(sorted snapshot JSON) |

### `annotate`
| Field | Value |
|-------|-------|
| Legal pre-states | `PANEL_READY`, `WIRING`, `ANNOTATING` |
| Post-state | `ANNOTATING` |
| Guard | annotation payload has `node_id` + `text` fields |
| Idempotency | **Idempotent** — same (node_id, text) → no-op |

### `reiterate`
| Field | Value |
|-------|-------|
| Legal pre-states | `FROZEN`, `GENERATING`, `PANEL_READY`, `WIRING`, `DEBUGGING`, `ANNOTATING`, `ITERATING` |
| Post-state | `ITERATING` → `PARSING` (resolved within same tick) |
| Guard | Operator confirms intent (destructive: discards current generated panel and draft state) |
| Idempotency | **Non-idempotent** — each call resets generation round counter and re-enters PARSING |
| Side-effect | **No write-back to frozen spec** (R3 invariant). `draft_design_state` cleared. New freeze cycle begins from PARSING. |

### `final_approve`
| Field | Value |
|-------|-------|
| Legal pre-states | `PANEL_READY`, `ANNOTATING` |
| Post-state (success) | `APPROVING` → `APPROVED` |
| Post-state (failure) | `ERROR` (`partial_approve_rollback`) |
| Guard | Panel has ≥1 truth-tracked node; no unresolved validation errors |
| Idempotency | **Non-idempotent** — side-effect sequence is destructive; deduplication token: (system_id, frozen_spec_sha) |
| **Side-effect ordering** | See §6 |

### `archive`
| Field | Value |
|-------|-------|
| Legal pre-states | `APPROVED` |
| Post-state (success) | `ARCHIVING` → `ARCHIVED` |
| Post-state (failure) | `ERROR` (`archive_write_failure`) |
| Guard | `workbench_bundle.py` `archive_workbench_bundle` callable; output path writable |
| Idempotency | **Non-idempotent** — each call appends a new manifest entry; deduplication token: (system_id, frozen_spec_sha, archive_timestamp) |

---

## §4. Transition Table

Legal (✓) / Illegal (✗) / Conditional (C) matrix. Blank = ✗.

| State \ Event | import_doc | answer_question | confirm_freeze | start_gen | wire_change | submit_snapshot | annotate | reiterate | final_approve | archive |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `INIT` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `INTAKED` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `PARSING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `AWAITING_ANSWERS` | ✗ | ✓ | C | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `FREEZING` | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `FROZEN` | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| `GENERATING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| `PANEL_READY` | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| `WIRING` | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| `DEBUGGING` | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| `ANNOTATING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ |
| `ITERATING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| `APPROVING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `APPROVED` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| `ARCHIVING` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `ARCHIVED` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `ERROR` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

**C** (Conditional) legend:
- `confirm_freeze` from `AWAITING_ANSWERS`: legal only when all_questions_answered OR all_waived_with_alias = true.

**ERROR transitions**: any state can transition to `ERROR` on unhandled exception. Recovery is not an automaton event — it is operator-initiated session reset to `INIT`.

---

## §5. Error Taxonomy

| Error code | Trigger | Recovery action |
|------------|---------|-----------------|
| `pdf_extract_failure` | `import_doc` → parser returns null or raises | Reset to `INIT`; prompt operator to re-upload or use alternate format |
| `ambiguity_unresolved` | `confirm_freeze` guard fails (unanswered questions, no alias) | Return to `AWAITING_ANSWERS`; surface unresolved question IDs |
| `regen_failure` | `start_gen` → LLM call fails or returns malformed SVG | Retry allowed ≤3 times; on 3rd failure → `ERROR`; frozen spec preserved |
| `iteration_overflow` | `reiterate` counter exceeds 10 cycles without `final_approve` | Block further `reiterate`; emit warning; require operator acknowledgment to proceed |
| `schema_drift` | Post-generation: generated node IDs not ⊆ spec.components ∪ spec.logic_nodes | Abort panel render; return to `FROZEN`; surface drift report |
| `partial_approve_rollback` | `final_approve` side-effect sequence fails at step ②, ③, or ④ | Roll back to pre-① state (`PANEL_READY` or `ANNOTATING`); log failed step; no partial commit retained |
| `archive_write_failure` | `archive` → disk write or manifest append fails | Retry once; on failure → `ERROR`; `APPROVED` state preserved for manual retry |
| `external_state_delete` | localStorage key deleted externally (DevTools, storage eviction) during active session | Detect on next read; emit warning; prompt operator to reload from last bundle |

---

## §6. Side-Effect Ordering: `final_approve`

The `final_approve` event triggers a **four-step atomic sequence**. Each step must complete before the next starts. On failure at any step, the entire sequence rolls back to the pre-① state.

```
① localStorage workspace state key → "APPROVING"
② server-side adapter.emit_adapter() + SYSTEM_REGISTRY row append  (atomic · single transaction)
③ workbench_bundle.archive_workbench_bundle() manifest append       (atomic write via existing protocol)
④ localStorage workspace state key → "APPROVED"
```

**Invariants:**
- Steps ②–③ MUST NOT be dispatched before ① completes (prevents orphaned server state).
- Step ④ MUST NOT fire if step ③ fails (prevents false APPROVED display).
- `draft_design_state` localStorage key is **deleted immediately after ④** (R6 authority rule).
- If the session crashes between ② and ③, the operator must manually invoke `workbench bundle --repair` to reconcile.

**What is NOT a side-effect of `final_approve`:**
- Writing back to `frozenSpec` (prohibited by R3).
- Creating new Python modules or files outside the P43-00 §3d whitelist.

---

## §7. Persistence Model

**Two-source invariant (P43-00 §3c · Codex r2 cut #1 · immutable):**

| Source | Owner module | Data stored | Write protocol |
|--------|-------------|-------------|----------------|
| `workbench.js` localStorage | Browser-side, key `workbench_workspace` | Current state, draft_design_state, frozen spec SHA, annotation cache, UI toggle state | Single-key atomic `localStorage.setItem` — no partial writes |
| `workbench_bundle.py` manifest | Python server-side | Bundle file list, SHA checksums, system_id, archive timestamp, operator alias | Existing `archive_workbench_bundle` atomic write protocol — append-only |

**Prohibited third sources:**
- ❌ `state.yaml` or any new YAML/JSON state file
- ❌ New SQLite / DB table for workflow state
- ❌ Server-side in-memory session dict (no new Python module for state)
- ❌ `workbench/orchestrator.py` or equivalent new persistence layer

**Crash recovery:**
- localStorage single-key write is atomic in all target browsers — no partial write recovery needed.
- Bundle manifest uses existing `workbench_bundle.py` atomic write — no new protocol.
- If `final_approve` crashes between ② and ③: bundle manifest is authoritative — re-run `workbench bundle --repair` to detect and reconcile.

---

## §8. Idempotency Classification

| Event | Class | Deduplication mechanism |
|-------|-------|------------------------|
| `import_doc` | Non-idempotent | SHA-256(file bytes) — duplicate → no-op + log.warning |
| `answer_question` | Idempotent | Same (question_id, answer) → no-op |
| `confirm_freeze` | Idempotent | Same frozen_spec SHA already in `FROZEN` → no-op |
| `start_gen` | Non-idempotent | (frozen_spec_sha, gen_round_counter) |
| `wire_change` | Idempotent | Same (node_id, signal_value) → no-op |
| `submit_snapshot` | Non-idempotent | SHA-256(sorted snapshot JSON) |
| `annotate` | Idempotent | Same (node_id, text) → no-op |
| `reiterate` | Non-idempotent | Always destructive — no dedup |
| `final_approve` | Non-idempotent | (system_id, frozen_spec_sha) — guard: not already APPROVED with same SHA |
| `archive` | Non-idempotent | (system_id, frozen_spec_sha, archive_timestamp) |

---

## §9. Authority Contract Summary (R1-R6)

Full mechanical rules and tests in `P43-00 §3e`. Summary for cross-reference:

| Rule | Invariant | Test |
|------|-----------|------|
| R1 | Only UI Steps 3/4/6 write `draft_design_state`; Python backend never writes | `test_r1_backend_no_draft_write` |
| R2 | `final_approve` handler never reads `draft_design_state` | `test_r2_final_approve_no_draft_read` |
| R3 | `frozenSpec` only set via `assignFrozenSpec(newSpec, {origin})` with `deepFreeze()`; origin ∈ {'freeze-event', 'archive-restore'} | `test_r3_controlled_writer_only`, `test_r3_no_draft_origin`, `test_r3_deepfreeze_enforced` |
| R4 | Generator reads frozen spec only, never draft | `test_r4_generator_reads_frozen_only` |
| R5 | `validateDraftAgainstFrozen()` singleton in `workbench.js` — no Python port | `test_r5_validator_singleton` |
| R6 | `final_approve` deletes `draft_design_state` immediately; archive bundle contains no draft | `test_r6_final_approval_handler_removes_draft`, `test_r6_archive_excludes_draft` |

---

## §10. Cross-Phase Test Ownership

| Transition / invariant | Owner phase | Test file |
|------------------------|-------------|-----------|
| State enum completeness (17 states) | P43-02 | `tests/test_p43_workflow_automaton.py` |
| All legal transitions succeed | P43-02 | `tests/test_p43_workflow_automaton.py` |
| All illegal transitions rejected | P43-02 | `tests/test_p43_workflow_automaton.py` |
| R1-R6 authority rules (14 tests) | P43-02 | `tests/test_p43_authority_contract.py` |
| FREEZE event + traceability_matrix emit | P43-03 | `tests/test_p43_freeze_gate.py` |
| `reiterate` → PARSING (non-FROZEN source) | P43-08 | `tests/test_p43_iteration_loop.py` |
| `final_approve` side-effect ordering | P43-08 | `tests/test_p43_approval_sequence.py` |
| `archive` backward-compat (P42 bundles) | P43-02 | `tests/test_p43_archive_backward_compat.py` |
| `ITERATING` transient resolves synchronously | P43-02 | `tests/test_p43_workflow_automaton.py` |
| `partial_approve_rollback` error recovery | P43-08 | `tests/test_p43_approval_sequence.py` |

---

## §11. Prohibited Patterns

The following patterns are unconditionally prohibited regardless of operator instruction:

1. **Draft write-back**: assigning `draft_design_state` values directly into `frozenSpec` (R3 violation).
2. **Preview bypass**: treating `PANEL_READY` → `final_approve` as equivalent to shipping a non-frozen spec (R2 violation).
3. **Third persistence source**: creating any file, DB table, or in-memory dict to store workflow state outside the two-source model (§7 violation).
4. **Backend draft emit**: any Python path that writes `draft_design_state` keys to the browser (R1 violation).
5. **Orphaned APPROVING**: allowing the `APPROVING` transient state to persist longer than the `final_approve` side-effect sequence wall time (currently capped at 30s; timeout → rollback).
6. **Archived-state mutation**: any event dispatch against a workbench in `ARCHIVED` state. Archived workbenches are read-only.

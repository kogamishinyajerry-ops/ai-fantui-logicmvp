---
doc: P43-contract-proof-report
phase: P43
sub_phase: P43-01
status: FINAL · Step G in progress · awaiting Kogami GATE-P43-01-CLOSURE
date: 2026-04-21
owner: Claude App Opus 4.7 (Solo Executor)
canonical_detailed_report: .planning/phases/P43-control-logic-workbench/reports/p43-01-contract-proof/CONTRACT-PROOF-REPORT.md
api_contract_lock: docs/P43-api-contract-lock.yaml
upstream_plan: .planning/phases/P43-control-logic-workbench/P43-01-00-PLAN.md (v5 · GATE-Approved)
---

# P43-01 · Contract Proof Report

This document is the plan-whitelisted entry point for P43-01 closure evidence (per P43-01-00-PLAN.md §2b). The full per-section evidence, code anchors, runtime dumps, Codex review trailers, and Additional Findings are captured in the detailed report at `canonical_detailed_report` above; this file is a summary + mechanical exit-criteria verification and is intentionally short.

## Executive summary

P43-01 is a **contract-proof spike** with a single thesis: prove the P15 pipeline's end-to-end contract — in both code and browser — by constructing ground-truth fixtures, running them through the real entry points, and reconciling observed behavior with the plan's §1c honesty boundary.

**What we confirmed** (five asserted_pass evidence points):
1. `run_pipeline_from_intake()` accepts a §1c-compliant intake packet (pdf via `source_documents.location` metadata only, no SHA binding) and returns the `assessment + bundle + system_snapshot` happy-path shape.
2. The blocker guard fires correctly on missing source documents, returning the `{status: "blocked", blockers: [...], message}` frontend contract.
3. The `ai-doc-analyzer.js` frontend reads `result.status === "blocked"` and `result.blockers` verbatim — alignment with the backend EMIT key is pinned by a grep-level regression test.
4. **`FileReader.readAsText` is broken for pdf binaries** — the browser silently produces `%PDF-1.7`-prefixed garbage and the analyze button stays enabled. (Scope note: only pdf was exercised by the Playwright test per plan §2c whitelist; docx behavior is predicted-broken by the same mechanism but not verified in this spike.)
5. The full `/api/workbench/*` + `/api/p15/*` surface (7 endpoints) has a locked-down YAML contract covering all documented happy paths, the blocked path, handler-specific 400 branches, and the shared structured-optional-field validation family on `/api/workbench/bundle`.

**What we fixed** (Step B · Kogami Option X expansion · 4 LOC surgical · 1 Codex review round): three critical Counter-F contract bugs in `src/well_harness/ai_doc_analyzer.py` that had silently broken the pipeline in production:
- **Bug A** · blocker guard READ side was testing `assessment.get("blockers")` while `assess_intake_packet` emits `"blocking_reasons"` — the guard silently bypassed blocked packets, which fell through to bundle building.
- **Bug B1/B2** · the happy-path return shape accessed `bundle.playback_report.scenarios` and `bundle.fault_diagnosis_report.fault_modes` — neither attribute exists on the respective singular-report dataclasses. Every valid ready packet raised `AttributeError` before the function could return.

**What we deferred**:
- **Bug D** · `_inject_clarification_answers` writes `clarify-{i}` index IDs while the consumer looks up stable question_ids. P43-03 (Q12=B+a) already planned to rewrite this path server-side with pypdf + python-docx extraction; fix lands there.
- **R7 · `generate_adapter.py`** hardcoded `max_n1k_deploy_limit=60.0` singleton + `thr_lock` terminal string-literal heuristic. Not in P43-01 scope; fix candidate for post-P43 workbench-generalization phase.
- **R8 · workbench.js + workbench_bundle.py schema inventory** is reported but unchanged; workspace-handoff dataclass promotion is a future-phase candidate.

**Why Counter-F matters**: Four bugs, one root cause — no internal contract lock between producer and consumer **within** `run_pipeline_from_intake()`'s own data path. The spike validated P43-00 §3e's thesis (ground truth via contract proof, not code polish) more strongly than the plan anticipated, because B1/B2 were not predicted by plan — they were discovered mid-Step-A with a runtime `AttributeError` on our minimal compliant fixture. Kogami arbitrated Option X to close the pipeline loop within P43-01 rather than defer.

## Exit Criteria mechanical verification (9 conditions · plan §4)

Full evidence table with commit anchors and runtime dumps is in `canonical_detailed_report` §13. Summary:

| # | Criterion | Status |
|---|-----------|--------|
| 1 | S1 asserted_pass · happy-path contract proof | **PASS** |
| 2 | S2 asserted_pass · blocked-path contract proof | **PASS** |
| 3 | S3a asserted_pass · Bug A READ fix + 4 default-lane tests + Codex Step B `可过-Gate` | **PASS** |
| 4 | S3b asserted_pass · frontend consumer grep alignment | **PASS** |
| 5 | S4 report · `readAsText` broken confirmed via Playwright evidence | **PASS (broken confirmed)** |
| 6 | S5 asserted_pass · `docs/P43-api-contract-lock.yaml` · 7 endpoints · 19 error branches | **PASS** |
| 7 | R6/R7/R8 inventory · 3 conclusions + fix checklist | **PASS** |
| 8 | Three-lane regression vs P42 baseline `a6521ca` | **PASS · default 800 passed, 1 skipped · e2e 50 passed · zero regression** |
| 9 | 2 Codex adversarial rounds (Step B + Step G) | **Step B PASS · Step G scrub round complete — verdict pending re-review on `e-scrub` commit** |

## Commit trail

| Commit | Scope |
|--------|-------|
| `48e4796` | Step A partial — fixture + report draft + Kogami escalation |
| `5d2d3ec` | Step B — Bugs A/B1/B2 surgical fix + 4 regression tests (Kogami Option X) |
| `8d76cf5` | Codex Step B review trailer + 3 optional doc polish items |
| `7fd243d` | Steps D/E/F — Playwright readAsText proof + API contract lock + R6/R7/R8 inventory |
| `4d40aee` | Step G — report finalize + exit-criteria mechanical verification |
| (this commit) | Step G scrub — Codex Step G round 1 `需修正·信号弱` → S5 YAML expanded + S4 wording narrowed + closure governance cleanup |

## P43-02+ scope recommendations (evidence-based)

- **P43-02 (workflow/orchestrator/panel)**: consume `docs/P43-api-contract-lock.yaml` as the authoritative endpoint contract. All new frontend consumers should grep-align at test time (following the S3b pattern).
- **P43-03 (document ingestion · pypdf + python-docx)**: fix Bug D (stable question_id contract in `_inject_clarification_answers` at `src/well_harness/ai_doc_analyzer.py:799`) together with the server-side extraction path decided in P43-00 Q12=B+a. Update ai-doc-analyzer's upload surface to submit the original binary to a new server endpoint, and remove the `readAsText` call entirely at `src/well_harness/static/ai-doc-analyzer.js:224`.
- **Post-P43 workbench-generalization**: revisit R7 (generate_adapter hardcode) by deriving terminal components from `packet.acceptance_scenarios[*].completion_condition` AST parsing, and promote the workspace_handoff dict to a typed dataclass (R8).
- **Test hardening (non-blocking · Codex Step B optional polish)**: replace grep-based regression tests 3/4 with AST-level or recorded-fixture-shape checks to harden against refactor-induced drift.

## Governance: this file is the plan-whitelisted canonical artifact

**This file (`docs/P43-contract-proof-report.md`) is the plan §2b-whitelisted gate artifact and the authoritative record for GATE-P43-01-CLOSURE.** It is the source of truth for the closure decision.

The more detailed report at `.planning/phases/P43-control-logic-workbench/reports/p43-01-contract-proof/CONTRACT-PROOF-REPORT.md` is a **supporting artifact**: it preserves the full arc of arbitration (Step A partial escalation → Kogami Option X → Codex Step B trailer → Codex Step G trailer) plus every runtime evidence anchor. When the two files disagree, this `docs/` summary is authoritative for exit-criteria verdicts; the supporting artifact is authoritative only for historical process detail not present here.

This inversion (relative to the pre-scrub wording) is applied in response to Codex Step G round 1 governance finding #3.

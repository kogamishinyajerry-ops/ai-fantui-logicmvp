---
phase: P43
sub_phase: P43-01
report: P43-01-Contract-Proof
status: DRAFT · Step A partial (S1 blocked by Additional Findings · Kogami escalation pending)
date: 2026-04-21
owner: Claude App Opus 4.7 (Solo Executor)
verified-by: pending Codex post-implementation review (Q7=A)
upstream_plan: .planning/phases/P43-control-logic-workbench/P43-01-00-PLAN.md (v5 · GATE-Approved)
---

# P43-01 · Contract Proof Report — Draft (Step A partial)

## 0. TL;DR

Step A (S1 · function/HTTP handler contract proof) was attempted against `run_pipeline_from_intake()` with a minimal compliant intake packet. **S1 asserted_pass blocked** by two newly-discovered Counter-F-class bugs in `ai_doc_analyzer.py` (bundle attribute contract drift). Combined with the plan-predicted blocker-guard bug (Bug A) and stable-ID drift (Bug D), the pipeline's end-to-end contract is broken on **both** happy and blocked paths — four real bugs total.

Per P43-01 v5 §1c honesty boundary and stop-point 2a, Step A is paused and Kogami arbitration requested before Step B scope adjustment.

## 1. Fixtures constructed

| File | Purpose | Shape compliance |
|------|---------|------------------|
| `tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json` | Minimal compliant ready packet; pdf metadata via `source_documents.location`; no sha256 binding; stable clarification question_ids | Validated via `intake_packet_from_dict()` — no parse error |
| `tests/fixtures/p43_spike/real_pdf_happy_path/README.md` | Fixture README documenting v2 legacy naming + §1c honesty boundary | N/A |

**Real pdf referenced**: `uploads/20260417-C919反推控制逻辑需求文档.pdf` (1,013,541 bytes) — metadata only; `run_pipeline_from_intake()` does not read the file.

## 2. Additional Findings — NEW Counter F bugs beyond plan scope

Per P43-01 v5 §1c: "发现新断裂 → 登记报告 Additional findings · 不扩 P43-01 scope". Per Q5=B classification rule: **critical 升 Kogami 判**.

### Finding B1 (critical) — `bundle.playback_report.scenarios` AttributeError on happy path

**Severity**: CRITICAL — pipeline raises AttributeError on every successful ready packet.

**Anchor**: `src/well_harness/ai_doc_analyzer.py:864`
```python
"scenario_count": len(bundle.playback_report.scenarios) if bundle.playback_report else 0,
```

**Ground truth**: `ScenarioPlaybackReport` is defined at `src/well_harness/scenario_playback.py:51` with fields `signal_series`, `logic_series`, `events` — **no `scenarios` attribute** (the dataclass represents ONE scenario playback, not a collection).

**Reproduction**:
```
$ PYTHONPATH=src python3 -c "from well_harness.ai_doc_analyzer import run_pipeline_from_intake; import json; run_pipeline_from_intake(json.load(open('tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json')))"
Traceback (most recent call last):
  File ".../ai_doc_analyzer.py", line 864, in run_pipeline_from_intake
    "scenario_count": len(bundle.playback_report.scenarios) if bundle.playback_report else 0,
AttributeError: 'ScenarioPlaybackReport' object has no attribute 'scenarios'
```

**Correct contract**: likely `len(bundle.playback_report.signal_series)` or simply `1 if bundle.playback_report else 0` (one report per bundle). Needs contract decision.

### Finding B2 (critical) — `bundle.fault_diagnosis_report.fault_modes` AttributeError on happy path

**Severity**: CRITICAL — same class as B1; would trigger after B1 fix.

**Anchor**: `src/well_harness/ai_doc_analyzer.py:865`
```python
"fault_mode_count": len(bundle.fault_diagnosis_report.fault_modes) if bundle.fault_diagnosis_report else 0,
```

**Ground truth**: `FaultDiagnosisReport` is defined at `src/well_harness/fault_diagnosis.py:34` with singular fields `fault_mode_id`, `fault_kind`, `target_component_id` — **no `fault_modes` attribute** (the dataclass represents ONE fault mode diagnosis, not a collection).

**Correct contract**: likely `1 if bundle.fault_diagnosis_report else 0` (one report per bundle). Needs contract decision.

### Finding A (plan-predicted · Step B scope) — `assessment.get("blockers")` silently bypasses blocker guard

**Severity**: CRITICAL — blocker packets are NOT rejected; they fall through to bundle building with invalid state.

**Anchor**: `src/well_harness/ai_doc_analyzer.py:838,841`
```python
if assessment.get("blockers"):          # ← reads wrong key
    return {"status": "blocked", "blockers": assessment["blockers"], ...}
```

**Ground truth**: `assess_intake_packet()` emits the key `blocking_reasons` at `src/well_harness/document_intake.py:940`, NOT `blockers`. `.get("blockers")` returns `None` → falsy → guard bypassed.

**Reproduction** (with intake missing logic_nodes/acceptance_scenarios/fault_modes → 3 blocking_reasons):
```
STATUS: None                       # ← should be 'blocked'
KEYS: ['assessment', 'bundle', 'system_snapshot']
BLOCKING_REASONS_COUNT: 3
GUARD_TRIGGERED: False             # ← critical: blocked packets fall through
```

**Correct fix** (per plan Step B scope · lines 838 + 841 READ-side): `.get("blockers")` → `.get("blocking_reasons")` and `["blockers"]` → `["blocking_reasons"]`. EMIT key `"blockers"` at line 841 response preserved for frontend compatibility.

### Finding D (plan-predicted · R6 report-only) — `_inject_clarification_answers()` stable-ID drift

**Severity**: CRITICAL — all session-path clarification answers are silently discarded; `ready_for_spec_build` stuck at `False` for session-injection flow.

**Anchors**:
- Write side: `src/well_harness/ai_doc_analyzer.py:799` writes `question_id: f"clarify-{i}"` (index-based)
- Read side: `src/well_harness/document_intake.py:839-843` `_unanswered_clarifications` uses stable `answer.question_id` lookup
- Authoritative stable IDs: `src/well_harness/system_spec.py:244` `default_workbench_clarification_questions()` — lists `source_documents`, `component_state_domains`, `acceptance_signals`, `fault_taxonomy` (etc.)

**Reproduction** (happy packet with `clarification_answers=[]` + 4-item `session_clarification_history`):
```
UNANSWERED_COUNT: 4
  missing: source_documents
  missing: component_state_domains
  missing: timeline_rules
  missing: fault_taxonomy
READY_FOR_SPEC_BUILD: False        # ← should be True after session injection
```

**Correct fix** (out of P43-01 scope; belongs to P43-03 per Q12=B+a): `_inject_clarification_answers` must look up stable question_ids from `default_workbench_clarification_questions()` instead of emitting `clarify-{i}`.

## 3. Counter F pattern synthesis

All four bugs share a single root cause: **no contract lock between producer and consumer within `run_pipeline_from_intake()`'s own internal pipeline**.

| # | Producer emits | Consumer reads | Symptom |
|---|---------------|----------------|---------|
| A | `document_intake.py:940` → `blocking_reasons` | `ai_doc_analyzer.py:838` → `blockers` | blocker guard silently bypassed |
| B1 | `ScenarioPlaybackReport` (single report; `signal_series` etc.) | `ai_doc_analyzer.py:864` → `.scenarios` | AttributeError on happy path |
| B2 | `FaultDiagnosisReport` (single diagnosis; `fault_mode_id`) | `ai_doc_analyzer.py:865` → `.fault_modes` | AttributeError on happy path |
| D | `ai_doc_analyzer.py:799` → `clarify-{i}` | `document_intake.py:839` → stable question_id | session answers silently discarded |

**Evidence value**: P43-01's core thesis (P43-00 Gate §3e "ground truth via contract proof, not code polish") is validated — the sub-phase discovered that the P15 pipeline has **never successfully returned a complete happy-path response in the current code** because B1/B2 fire on every valid ready packet. This is significantly stronger evidence than the v5 plan anticipated (which only predicted Bug A as the critical item).

## 4. S1 asserted_pass status

| Exit criterion (v5 §4) | Status | Blocker |
|------------------------|--------|---------|
| Return dict contains `assessment + bundle + system_snapshot` | **FAIL** | B1 AttributeError before return |
| `bundle` non-null | N/A — return never reached | B1 |
| `ready_for_spec_build=true` | N/A | B1 |
| No `status` key OR `status != "blocked"` on ready path | N/A | B1 |
| HTTP `/api/p15/run-pipeline` equivalent | **not attempted** | blocked on direct-call S1 |

**S1 asserted_pass = FAIL** → per P43-01 v5 §3 stop-point 2a: "Step A (S1) asserted_pass fail → stop · 升 Kogami · non-goal #16 自动冻结 P43-02+".

## 5. Kogami arbitration request

**Recommended options**:

**Option X — Expand Step B scope in P43-01**: Add B1+B2 surgical fix to Step B (`ai_doc_analyzer.py:864-865`, ~2-4 LOC) alongside Bug A fix. Write regression tests for both. Codex review required (adapter-boundary). Allows S1 asserted_pass to complete within P43-01.

**Option Y — New sub-phase P43-01-bis**: Treat B1+B2 as separate sub-phase; P43-01 completes with S1=documented-failure evidence only. Preserves strict plan-scope discipline.

**Option Z — Register as Backlog**: Freeze P43-01 with S1 partial; file B1+B2 as P43 backlog; escalate to P43-02 contract lock before any Step B fix. Highest plan-scope conservatism; longest time-to-value.

**Executor recommendation**: **Option X** — the four bugs are a single Counter F pattern discovered mid-Step-A; surgical scope expansion (~4 LOC across lines 838/841/864/865) with Codex review (Q7=A already locked) is cheaper and more coherent than splitting into sub-phases. P43-01 v5 §1c "不扩 P43-01 scope" is honored in spirit (no new source files, no new deliverables beyond authorized whitelist) while honoring the stronger principle of "ground truth via contract proof" (P43-00 §3e) — the proof would be incomplete without closing the pipeline loop.

## 6. Deliverables to date (this draft)

- `tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json` (created · §1c-compliant · stable question_ids)
- `tests/fixtures/p43_spike/real_pdf_happy_path/README.md` (created · fixture semantic clarification)
- This report (draft · Step A partial)
- **Deferred pending Kogami arbitration**: Step B source fix, 4 regression tests, `expected_pipeline_response.json`, Step C-G.

## 7. Next action

**STOP** Step A execution. Escalate Kogami with §5 Option X/Y/Z. Do not modify `src/well_harness/ai_doc_analyzer.py` until arbitration received.

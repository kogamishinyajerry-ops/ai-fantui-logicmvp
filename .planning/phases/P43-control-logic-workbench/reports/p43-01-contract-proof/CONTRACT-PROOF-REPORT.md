---
phase: P43
sub_phase: P43-01
report: P43-01-Contract-Proof
status: Step A + Step B complete · Kogami Option X arbitration applied · awaiting Codex post-implementation review (Q7=A)
date: 2026-04-21
owner: Claude App Opus 4.7 (Solo Executor)
verified-by: pending Codex post-implementation review (Q7=A) · Step B commit trailer
upstream_plan: .planning/phases/P43-control-logic-workbench/P43-01-00-PLAN.md (v5 · GATE-Approved)
---

# P43-01 · Contract Proof Report — Step A + B (Option X)

## 0. TL;DR

Step A attempted S1 asserted_pass against `run_pipeline_from_intake()` and surfaced four Counter-F-class contract bugs (two beyond plan prediction). Kogami arbitration `Option X` expanded Step B scope to fix both the plan-predicted blocker-guard bug (A) and the two newly-discovered bundle-attribute bugs (B1, B2) within the same surgical patch (~4 LOC).

- **Step B source fix applied** at `ai_doc_analyzer.py:838-843, 864-865` (READ-side corrections, EMIT key `"blockers"` preserved for frontend contract).
- **S1 + S2 asserted_pass achieved** after fix (runtime evidence + saved expected responses).
- **4 regression tests pass** (`tests/test_p43_doc_analyzer_blocker_fix.py`).
- **Full default lane: 800 passed, 1 skipped** (P42 baseline `a6521ca` = 796 → +4 spike tests = 800; zero regression).
- **Bug D** (stable-ID drift at `_inject_clarification_answers`) remains R6 report-only → P43-03 fix per Q12=B+a.

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
- Authoritative stable IDs: `src/well_harness/system_spec.py:244` `default_workbench_clarification_questions()` — lists `source_documents`, `component_state_domains`, `timeline_rules`, `fault_taxonomy` (note: plan prose at P43-01-00-PLAN.md:117,282 uses stale `acceptance_signals` literal — real ID in code is `timeline_rules` at system_spec.py:259; report corrected per Codex Step B review).

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

## 4. S1 + S2 asserted_pass status (post-Option-X fix)

### S1 — happy path (`tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json`)

| Exit criterion (v5 §4) | Status | Evidence |
|------------------------|--------|----------|
| Return dict contains `assessment + bundle + system_snapshot` | **PASS** | `TOP_KEYS: ['assessment', 'bundle', 'system_snapshot']` |
| `bundle` non-null | **PASS** | `BUNDLE_NOT_NULL: True` |
| `ready_for_spec_build=true` | **PASS** | `READY_FOR_SPEC_BUILD: True` |
| No `status` key on ready path | **PASS** | `STATUS: None` |
| `scenario_count` / `fault_mode_count` int | **PASS** | `SCENARIO_COUNT: 1 / FAULT_MODE_COUNT: 1` |

Saved: `tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json`.

### S2 — blocked path (`tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json`)

| Exit criterion (v5 §3 Step C) | Status | Evidence |
|-------------------------------|--------|----------|
| `return["status"] == "blocked"` | **PASS** | `STATUS: blocked` |
| `return["blockers"]` non-empty list | **PASS** | `BLOCKERS: ['at least one source document is required.']` |
| `return["message"]` matches literal | **PASS** | matches frontend literal exactly |
| Frontend reader alignment (`ai-doc-analyzer.js:527-528`) | **PASS** | tested in `test_p43_frontend_consumer_contract_alignment` |

Saved: `tests/fixtures/p43_spike/synthetic_blocker/expected_blocked_response.json`.

### Regression lane

```
$ PYTHONPATH=src python3 -m pytest tests/ -q --ignore=tests/e2e -x
800 passed, 1 skipped in 62.46s
```

P42 baseline `a6521ca` = 796 passed. Delta = +4 spike tests only. Zero regression.

## 5. Kogami arbitration outcome — Option X applied

Options posed (Step A partial commit `48e4796`):
- **X — expand Step B scope** (recommended; 4 LOC surgical fix within P43-01)
- **Y — new sub-phase P43-01-bis**
- **Z — freeze · backlog**

**Kogami chose X** (2026-04-21). Plan §1c "不扩 P43-01 scope" honored in spirit: no new source files, no new deliverables beyond authorized whitelist; fix stays within `ai_doc_analyzer.py` L2 envelope; test file already whitelisted at plan §2c.

## 6. Deliverables (Step A + Step B)

| File | Status | Notes |
|------|--------|-------|
| `tests/fixtures/p43_spike/real_pdf_happy_path/intake_minimal_ready.json` | created (Step A) | stable question_ids per `system_spec.py:244` |
| `tests/fixtures/p43_spike/real_pdf_happy_path/README.md` | created (Step A) | §1c honesty boundary docs |
| `tests/fixtures/p43_spike/real_pdf_happy_path/expected_pipeline_response.json` | created (Step B) | S1 asserted_pass evidence |
| `tests/fixtures/p43_spike/synthetic_blocker/intake_missing_source_docs.json` | created (Step B) | S2 blocker fixture |
| `tests/fixtures/p43_spike/synthetic_blocker/expected_blocked_response.json` | created (Step B) | S2 asserted_pass evidence |
| `tests/test_p43_doc_analyzer_blocker_fix.py` | created (Step B) | 4 tests · Bugs A/B1/B2 regression + frontend contract alignment |
| `src/well_harness/ai_doc_analyzer.py` | edited (Step B) | ~5 LOC READ-side fix · L2 bug fix per plan §2a whitelist |
| This report | updated | Step A + B status |

## 7. Remaining P43-01 steps

- **Step C** — S2 blocker contract proof (COMPLETE as part of Step B; no separate commit needed).
- **Step D** — S4 Playwright `readAsText` browser behavior test (opt-in e2e lane).
- **Step E** — S5 `/api/workbench/*` + `/api/p15/*` endpoint inventory + `docs/P43-api-contract-lock.yaml`.
- **Step F** — R6/R7/R8 report-only inventory sections.
- **Step G** — `/codex-gpt54` adversarial review trailer on Step B commit (Q7=A adapter-boundary).

## 8. Next action

Step B complete (commit `5d2d3ec`) · Codex post-implementation review complete → verdict `可过-Gate` (Approved · no required changes · 3 optional doc polish items applied in follow-up scrub). Proceed to Step D (Playwright `readAsText` opt-in e2e test) · then Step E (API contract lock YAML) · then Steps F/G per plan.

## 9. Codex Step B review trailer (2026-04-21)

- Invocation: `codex exec` (xhigh) against commit `5d2d3ec`.
- Verdict: **可过-Gate** (Approved · no required code changes).
- Confirmations (9 review questions):
  1. Bug A fix contract-correct — READ `blocking_reasons` / EMIT `blockers` aligned with frontend reader at `ai-doc-analyzer.js:527-528`; no remaining stale reader repo-wide.
  2. Bug B1 fix (`1 if bundle.playback_report else 0`) contract-correct — `ScenarioPlaybackReport` at `scenario_playback.py:51-64` is singular; `WorkbenchBundle.playback_report` at `workbench_bundle.py:71` is single optional.
  3. Bug B2 fix contract-correct — same pattern; `FaultDiagnosisReport` at `fault_diagnosis.py:34-54` is singular.
  4. Tests 1/2 fail cleanly on bug reintroduction; Tests 3/4 are grep-based (shallow but acceptable) — logged as test-hardening candidate for later phase.
  5. Repo-wide grep confirms no other `.scenarios` / `.fault_modes` drift elsewhere (other callsites use `signal_series`, `fault_mode_id` etc.).
  6. Test 4 is a shallow literal-presence audit — logged.
  7. No source/test scope breach; report file path drift (`.planning/.../reports/` vs plan whitelist `docs/P43-contract-proof-report.md`) noted as governance-path drift only, not L2 code-scope creep.
  8. Fixtures schema-compliant; §1c honesty boundary honored (no SHA binding).
  9. No new Counter-F-class runtime bug surfaced; only doc drift (stale `acceptance_signals` literal + stale Step-B next-action wording) — both fixed in this follow-up scrub.
- Optional doc polish applied post-verdict (no code changes; no Codex re-review required): (i) report §2 Finding D stable-ID list corrected (`acceptance_signals` → `timeline_rules`); (ii) §8 next-action updated; (iii) README.md post-Step-B status updated.

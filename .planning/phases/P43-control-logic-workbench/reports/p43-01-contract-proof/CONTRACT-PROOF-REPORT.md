---
phase: P43
sub_phase: P43-01
report: P43-01-Contract-Proof (supporting artifact for the plan §2b-whitelisted summary at `docs/P43-contract-proof-report.md`)
status: CLOSED · GATE-P43-01-CLOSURE Approved by Kogami 2026-04-21 · Codex Step G r4 `可过-Gate` on 9a51183 · P43-02 kickoff authorized
date: 2026-04-21
owner: Claude App Opus 4.7 (Solo Executor)
verified-by: Codex Step B `可过-Gate` (trailer §9) · Codex Step G pending round 3 re-review on scrub commit
upstream_plan: .planning/phases/P43-control-logic-workbench/P43-01-00-PLAN.md (v5 · GATE-Approved)
authoritative_summary: docs/P43-contract-proof-report.md
---

# P43-01 · Contract Proof Report — Full arc (Step A → Step G scrub round 2)

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

## 10. Step D · S4 Playwright `readAsText` browser behavior evidence

**Test**: `tests/test_p43_readAsText_browser_behavior.py` · opt-in e2e lane (`pytest -m e2e`).

**Setup**: Chromium (Playwright 1.58.0 · headless) loads `http://127.0.0.1:8797/ai-doc-analyzer.html`; real pdf `uploads/20260417-C919反推控制逻辑需求文档.pdf` (1,013,541 bytes) uploaded via `page.locator("#ai-doc-file-input").set_input_files(...)`; waits until `#ai-doc-preview.value.length > 0`; captures preview value + analyze-btn state + upload-error text.

**S4 evidence dump** (from 2026-04-21 test run):

```
preview_starts_with: '%PDF-1.7'
preview_length:      962835
analyze_btn_disabled: False
upload_error_present: False
```

**Interpretation**:
- pdf header literal `%PDF-1.7` carried verbatim into `_documentText` (`static/ai-doc-analyzer.js:214`) and displayed in `_previewTextarea` — this is the UTF-8 lossy decode of the raw pdf byte stream.
- `FileReader.readAsText` did NOT dispatch `onerror` (upload-error element is empty).
- Analyze button stayed ENABLED, meaning the analyzer pipeline is willing to submit this 962k-character garbage string to the LLM.
- `reader.readAsText(file)` at `static/ai-doc-analyzer.js:224` has no content-type guard; the absence of the guard is empirically confirmed for `.pdf` (docx is predicted-broken by the same mechanism but not exercised in this spike — see §10 Conclusion below).

**Conclusion**: Browser-side `readAsText` cannot process pdf binaries (empirically verified here). Based on the same UTF-8-lossy-decode mechanism, docx behavior is predicted-broken (zip-archive header `PK\x03\x04` would be decoded as mojibake) but was **not** exercised in this spike — the plan §2c whitelist authorized one e2e test file with one test function, and the pdf case is the ground truth. The analyzer currently has three correlated gaps that together constitute the broken path — (i) no file-content guard, (ii) silent garbage-in success, (iii) unconditional enable of the downstream LLM submit. Registered as **R6a blocker for P43-03** (Q12=B+a server-side pypdf / python-docx extraction path); P43-03 should verify docx behavior before writing the server-side extractor.

## 11. Step E · S5 API contract lock deliverable

**File**: `docs/P43-api-contract-lock.yaml` (12,351 bytes · YAML v1 parseable).

**Coverage** (7 endpoints):

| Method | Path | Handler | Response branches |
|--------|------|---------|-------------------|
| GET  | `/api/workbench/bootstrap`        | `demo_server.py:217` | 200 |
| GET  | `/api/workbench/recent-archives`  | `demo_server.py:224` | 200 |
| POST | `/api/workbench/bundle`           | `demo_server.py:343` | 200 · 19 × 400 (3 handler-specific + 15 structured-optional-field family + 1 `sample_period_s ≤ 0`) |
| POST | `/api/workbench/repair`           | `demo_server.py:350` | 200 · 4 × 400 (includes `apply_all_safe` truthiness note — handler accepts any truthy value) |
| POST | `/api/workbench/archive-restore`  | `demo_server.py:357` | 200 · 6 × 400 (includes wrong-type `manifest_path` branch distinct from missing/empty) |
| POST | `/api/p15/convert-to-intake`      | `demo_server.py:484` | 200 · 5 × 400 |
| POST | `/api/p15/run-pipeline`           | `demo_server.py:491` | 200 ready · 200 blocked · 2 × 400 |

**Global guards** (applied at `demo_server.py:291-311` before POST dispatch): 413 `payload_too_large`, 415 `unsupported_media_type`, 400 `invalid_content_length` / `invalid_json` / `invalid_json_object`, 404 `not_found`.

**Noteworthy semantic blocks embedded**:
- `/api/p15/run-pipeline` → `response_200_ready` and `response_200_blocked` documented separately with emitted key `blockers` (Bug A EMIT contract) and `scenario_count`/`fault_mode_count` ∈ {0,1} shapes (Bug B1/B2 fix contract).
- `session_id_semantics` block for `/api/p15/run-pipeline` records **Bug D** deferral: when `session_id` maps to an existing P14 session, `_inject_clarification_answers` writes `clarify-{i}` at `ai_doc_analyzer.py:799` and the stable-ID consumer at `document_intake.py:839-843` discards the answers silently. Fix owner: P43-03 (Q12=B+a).

## 12. Step F · R6 / R7 / R8 report-only inventory

### R6 — analyzer ID ↔ intake clarification ID contract (Counter F, second layer)

**Registered as Bug D** at §2 Finding D (details + reproduction there). Summary anchors:

| Layer | Code anchor | Behavior |
|-------|-------------|----------|
| Producer (session-injection write side) | `src/well_harness/ai_doc_analyzer.py:799` | Writes `question_id: f"clarify-{i}"` (index-based) in `_inject_clarification_answers()` @ `:785-806`. |
| Authoritative stable IDs | `src/well_harness/system_spec.py:244` `default_workbench_clarification_questions()` — at `:259` the id is `timeline_rules`; full set used in fixtures: `source_documents`, `component_state_domains`, `timeline_rules`, `fault_taxonomy`. |
| Consumer (read side) | `src/well_harness/document_intake.py:839-843` | `_unanswered_clarifications` keys by stable `answer.question_id`, so `clarify-{i}` never matches any required question and all session-injected answers are silently dropped. |

**Runtime evidence** (captured in §2 Finding D): happy packet with `clarification_answers=[]` + 4-item `session_clarification_history` → all 4 clarifications remain unanswered; `ready_for_spec_build=False`.

**Fix ownership**: P43-03 (per plan Q12=B+a · server-side pypdf + stable-ID contract). NOT in P43-01 scope.

### R7 — `generate_adapter.py` hardcoded runtime params

**Anchor 1** · `src/well_harness/tools/generate_adapter.py:255-257`

```python
_KNOWN_RUNTIME_PARAMS: dict[str, float] = {
    "max_n1k_deploy_limit": 60.0,  # demo_server default
}
```

- Hardcoded singleton mapping from string-threshold refs (that appear in logic node `threshold_value` fields but are not actual component IDs) to canonical numeric defaults.
- Current set = 1 entry. Only `max_n1k_deploy_limit` is honored; any other runtime-param spec string would resolve to `None`, silently falling through to whatever default the adapter assigns later.

**Anchor 2** · `src/well_harness/tools/generate_adapter.py:442-451`

```python
terminal_ln_ids: list[str] = []
for lid in last_tier_ids:
    ln = next((n for n in logic_nodes if n["id"] == lid), None)
    if ln and "thr_lock" in ln.get("downstream_component_ids", []):
        terminal_ln_ids.append(lid)
if not terminal_ln_ids:
    terminal_ln_ids = last_tier_ids[-1:] if last_tier_ids else []
```

- Hardcoded string literal `thr_lock` as the terminal-component marker.
- For any system that does NOT have a `thr_lock`-named terminal component, the block falls through to "last logic node in topological order" heuristic — not guaranteed to match intended terminal.

**Impact on non-thrust-reverser systems** (e.g. C919 ETRAS variants with different terminal naming, or a generic hydraulic actuator system with `actuator_extend` as the terminal): logic-tier termination detection degrades to a heuristic; generated adapter's `completion_reached` expression can bind to the wrong logic node silently.

**Status**: known limitation · not in P43-01 scope · fix candidate for post-P43 workbench-generalization phase (use `packet.acceptance_scenarios[*].completion_condition` AST parse to derive the terminal programmatically).

### R8 — Frontend + workbench_bundle schema inventory

**Frontend `workbench.js` persistence contract**:

| Field | Anchor | Value |
|-------|--------|-------|
| localStorage key (sole writer) | `src/well_harness/static/workbench.js:6` | `"well-harness-workbench-packet-workspace-v1"` |
| Storage op entry point | `src/well_harness/static/workbench.js:301-307` | `workbenchBrowserStorage()` returns `window.localStorage` or null on failure. |
| Write site | `src/well_harness/static/workbench.js:557` | `storage.setItem(workbenchPacketWorkspaceStorageKey, ...)` |
| Read site | `src/well_harness/static/workbench.js:583` | `storage.getItem(workbenchPacketWorkspaceStorageKey)` |

Schema drift risk: single localStorage key with no versioning guard beyond the `-v1` suffix; any future shape change requires a key migration path.

**`workbench_bundle.py` serialization contract** (workbench bundle → dict):

- Kind: `"well-harness-workbench-bundle"` @ `src/well_harness/workbench_bundle.py:26`
- Version: `1` @ `:27`
- Schema ID: `"https://well-harness.local/json_schema/workbench_bundle_v1.schema.json"` @ `:28`
- Top-level keys emitted by `workbench_bundle_to_dict` @ `:124-143`: `$schema`, `kind`, `version`, `system_id`, `system_title`, `bundle_kind`, `ready_for_spec_build`, `selected_scenario_id`, `selected_fault_mode_id`, `intake_assessment`, `clarification_brief`, `playback_report` (nullable), `fault_diagnosis_report` (nullable), `knowledge_artifact` (nullable), `next_actions`.

**Archive manifest contract**:

- Kind: `"well-harness-workbench-archive-manifest"` @ `:29`
- Schema ID: `"https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json"` @ `:31`
- Self-check command: `"python3 -m well_harness.cli archive-manifest ."` @ `:32`
- File key set @ `:43-53` (9 keys): `bundle_json`, `summary_markdown`, `intake_assessment_json`, `clarification_brief_json`, `playback_report_json`, `fault_diagnosis_report_json`, `knowledge_artifact_json`, `workspace_handoff_json`, `workspace_snapshot_json`.
- Required subset @ `:54-58`: `bundle_json`, `summary_markdown`, `intake_assessment_json`.
- Validator: `validate_workbench_archive_manifest` @ `:227` checks `kind`, `version`, `$schema`, required-file-keys, checksums.

**Workspace handoff consumer shape** (informational; derived from usage at `workbench_bundle.py:755-763`): `{badgeText, system, packet, result}` — all stringly-typed runtime dict; no dataclass guard. Fix candidate: promote to typed dataclass in a future phase.

**Status**: All three inventories report-only. No code changes attempted in P43-01.

## 13. Exit Criteria mechanical verification (Plan §4 · 9 conditions)

All 9 exit criteria asserted_pass. Evidence anchored to commits, files, and test runs.

| # | Criterion | Status | Evidence anchor |
|---|-----------|--------|-----------------|
| 1 | **S1 asserted_pass** · happy-path `run_pipeline_from_intake` contract proof | **PASS** | `tests/fixtures/p43_spike/real_pdf_happy_path/{intake_minimal_ready.json, expected_pipeline_response.json, README.md}` · committed `48e4796` (fixture) + `5d2d3ec` (expected response after fix) · default lane green. |
| 2 | **S2 asserted_pass** · blocked-path `status=blocked` contract | **PASS** | `tests/fixtures/p43_spike/synthetic_blocker/{intake_missing_source_docs.json, expected_blocked_response.json}` · committed `5d2d3ec` · default lane green. |
| 3 | **S3a asserted_pass** · `ai_doc_analyzer.py:838+841` READ side `blocking_reasons` · EMIT `blockers` preserved · 4 tests default lane · Codex "可过" | **PASS** | Source fix at `src/well_harness/ai_doc_analyzer.py:840,843` (commit `5d2d3ec`); 4 tests in `tests/test_p43_doc_analyzer_blocker_fix.py` all pass default lane; Codex Step B review `可过-Gate` (trailer at §9 · commit `8d76cf5`). |
| 4 | **S3b asserted_pass** · frontend consumer audit · alignment grep | **PASS** | `test_p43_frontend_consumer_contract_alignment` in `tests/test_p43_doc_analyzer_blocker_fix.py:133` greps `static/ai-doc-analyzer.js:527-528` for both `result.status === "blocked"` and `result.blockers`; passes. |
| 5 | **S4 report** · Playwright `readAsText` conclusion | **PASS — pdf broken empirically confirmed · docx predicted-broken (not exercised per §2c whitelist)** | `tests/test_p43_readAsText_browser_behavior.py` (commit `7fd243d`) · e2e lane green · evidence dump in §10: `preview_starts_with='%PDF-1.7'`, `preview_length=962835`, `analyze_btn_disabled=False`, `upload_error_present=False`. P43-03 must verify docx before writing server-side extractor. |
| 6 | **S5 asserted_pass** · `docs/P43-api-contract-lock.yaml` covers `/api/workbench/*` + `/api/p15/*` with success/blocked/error branches | **PASS (post-scrub)** | `docs/P43-api-contract-lock.yaml` (commit `7fd243d` · expanded in Step G scrub) · 7 endpoints · YAML parses cleanly · response-200 success variants + handler-specific 400s + structured-optional-field family on `/api/workbench/bundle` (15 field-level entries covering the `_optional_request_str/_float/_object/_string_list` validator surface) + 6 global guards documented. |
| 7 | **R6/R7/R8 report** · 3 inventory conclusions + fix checklist | **PASS** | §10 (S4) + §11 (S5) + §12 (R6/R7/R8) · each registered with code anchors and fix ownership (P43-03 for R6 Bug D · post-P43 workbench-generalization for R7 · future dataclass promotion for R8 handoff shape). |
| 8 | **Three-lane regression** vs P42 baseline `a6521ca` | **PASS** | Default pytest **800 passed, 1 skipped** (P42 baseline 796 + 4 spike default tests) · E2E **50 passed** (P42 baseline 49 + 1 Playwright readAsText e2e · includes `test_resilience_adversarial_truth_engine_still_passes` adversarial wrapper at `tests/e2e/test_demo_resilience.py:132`) · zero regression across both lanes · re-run 2026-04-21. |
| 9 | **Report complete + 2 Codex adversarial rounds** (Step B + Step G) | **PASS · Codex Step G round 4 `可过-Gate` on commit `9a51183`** | Step B `可过-Gate` (trailer §9 · commit `8d76cf5`). Step G arc (4 Codex rounds over 4 scrub commits): r1 (4d40aee) 需修正·信号弱 → scrub 1 (6729768) closing 3 fixes → r2 (6729768) 需修正·信号强 → scrub 2 (e86a8cc) closing 7 drift items → r3 (e86a8cc) 需修正·信号弱 → scrub 3 (9a51183) closing 1 trigger-text drift → **r4 (9a51183) 可过-Gate** with endorsement quoted at §14. All other round-1/2/3 fixes held across scrubs. |

**Non-goal #16 self-audit** (from P43-00 plan — "不以 '列出断裂' 为通过条件"): PASS. P43-01 did not merely list broken paths — it (a) fixed three critical Counter-F bugs (A/B1/B2) with surgical source edits and regression tests, (b) produced asserted_pass evidence on both happy and blocked paths, (c) provided a canonical API contract lock YAML for downstream phases, and (d) confirmed (not assumed) the readAsText pipeline is broken via headless-browser evidence.

## 14. Codex Step G review trailer · rounds 1–4 (2026-04-21)

Step G required Codex review per plan Q7=A (milestone-wide adapter-boundary rule). Four rounds were completed with progressive signal downgrade:

| Round | Commit reviewed | Verdict | Required fixes |
|-------|-----------------|---------|----------------|
| r1 | `4d40aee` | 需修正·信号弱 | (i) S5 YAML undersized enumeration on `/api/workbench/bundle`; (ii) S4 wording overreach beyond pdf-only test evidence; (iii) closure governance inversion (detailed-report-as-authoritative vs plan §2b-whitelisted summary). |
| r2 | `6729768` | 需修正·信号强 | 7 further drift items: (1) bundle `sample_period_s ≤ 0` branch missing; (2) archive-restore non-string manifest_path distinct branch missing; (3) repair `apply_all_safe` is truthiness not strict bool; (4) §13 count stale (19 vs actual 36+6); (5) §11 table counts stale; (6) §10 "same behavior for .pdf and .docx" overreach; (7) detailed report frontmatter stale. |
| r3 | `e86a8cc` | 需修正·信号弱 | Single finding: `/api/workbench/repair` error_branches trigger text at yaml:213-216 still said `apply_all_safe != true`; schema at yaml:193-201 correct (truthiness) but trigger text lagged. |
| r4 | `9a51183` | **可过-Gate** | No blocking findings. |

**Codex Step G round 4 verdict (`9a51183`)**, verbatim:

> No blocking findings.
>
> Verdict: `可过-Gate`.
>
> 1. `docs/P43-api-contract-lock.yaml:216` now matches the actual guard in `src/well_harness/demo_server.py:2662`: `request_payload.get("apply_all_safe", False)` rejects missing or falsy values, and truthy non-bool values do pass.
> 2. The YAML is still valid; parsed with `python3`/PyYAML, and the request schema note at `docs/P43-api-contract-lock.yaml:193` is internally consistent with the repaired error-branch text at line 216. Both now describe truthiness-based behavior rather than strict `== true`.
> 3. No new drift was introduced by `9a51183`. `git show` confirms this commit only changes `docs/P43-api-contract-lock.yaml`, and `git diff --check` is clean.
>
> `GATE-P43-01-CLOSURE: Commit 9a51183 closes the Step G contract-lock gap; /api/workbench/repair now truthfully documents apply_all_safe as a truthiness guard, the YAML remains valid and internally consistent, and no new drift was introduced.`

**Optional polish flagged by round 4** (explicitly non-blocking):
- `src/well_harness/demo_server.py:2666` error message still says `"apply_all_safe must be true"` even though the runtime guard is truthiness-based. Either soften to "must be truthy" or harden the handler to strict boolean in a later slice. **Candidate for P43-02 or a standalone cleanup slice — not in P43-01 scope.**

## 15. GATE-P43-01-CLOSURE — Approved

**Status**: **Approved by Kogami on 2026-04-21** on the basis of Codex Step G r4 `可过-Gate` verdict (commit `9a51183`). P43-02 (workflow / orchestrator / panel) kickoff authorized per plan §3 Step G item 4.

**Executor signoff** (Solo Executor v5.2 + v5.3 addendum): Steps A through G executed per plan. Kogami Option X arbitration applied at Step B. Codex rounds complete: Step B `可过-Gate`, Step G r1–r4 culminating in `可过-Gate` on `9a51183`. All 9 Exit Criteria PASS (§13). Non-goal #16 self-audit PASS. Three-lane regression green. Plan-whitelisted deliverables present (`docs/P43-contract-proof-report.md`, `docs/P43-api-contract-lock.yaml`). Bug D deferred to P43-03 per Q12=B+a. R7 deferred to post-P43 workbench-generalization. R8 inventory-only. One optional polish (`demo_server.py:2666` error message) surfaces as future-slice candidate.

**Kogami arbitration request**: Approve GATE-P43-01-CLOSURE and authorize P43-02 (workflow / orchestrator / panel) kickoff, or specify additional fixes required.

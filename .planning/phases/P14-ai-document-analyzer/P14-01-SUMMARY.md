---
phase: P14
plan: P14-01
subsystem: AI Document Analyzer
tags: [p14, ai-analysis, clarification-loop, claude-code-prompt]
dependency_graph:
  requires: []
  provides:
    - ai_doc_analyzer.py (AI analysis module)
    - /api/p14/* routes (analyze/clarify/generate)
    - ai-doc-analyzer.html (browser UI page)
    - ai-doc-analyzer.css (page styles)
    - ai-doc-analyzer.js (UI logic)
    - P14 nav links (workbench.html + demo.html)
    - test_p14_ai_doc_analyzer.py (14 tests)
tech_stack:
  added:
    - anthropic Python SDK
    - P14SessionStore singleton (thread-safe in-memory)
    - Mock mode via P14_AI_MOCK=1 env var
key_files:
  created:
    - src/well_harness/ai_doc_analyzer.py (451 lines)
    - src/well_harness/static/ai-doc-analyzer.html (188 lines)
    - src/well_harness/static/ai-doc-analyzer.css (298 lines)
    - src/well_harness/static/ai-doc-analyzer.js (480 lines)
    - tests/test_p14_ai_doc_analyzer.py (298 lines)
  modified:
    - src/well_harness/demo_server.py (+167 lines)
    - src/well_harness/static/workbench.html (+2 lines nav link)
    - src/well_harness/static/demo.html (+7 lines nav strip)
decisions:
  - id: "API design"
    description: "analyze returns first_question directly so UI can start clarification loop without extra round-trip"
  - id: "Mock mode"
    description: "P14_AI_MOCK=1 env var enables fixture data for testing without real API calls"
  - id: "Error propagation"
    description: "analyze_document/generate_prompt_document return error dicts (not exceptions) so handlers can return 400/503 with structured payload"
  - id: "Upload limit"
    description: "Server limit raised to 10MB to match JS client validation (was 500KB per initial draft)"
  - id: "Empty analysis"
    description: "Session marked complete when no ambiguities detected, preventing stuck clarification state"
metrics:
  duration: "~40 minutes"
  completed_date: "2026-04-13"
  tasks_completed: 8
  tests_added: 14
  tests_passed: 14
  pre_existing_failures: 1 (test_gsd_notion_sync, unrelated)
---

# Phase 14 Plan 01: AI Document Analyzer — Summary

## One-liner

JWT auth with refresh rotation using jose library

Full-pipeline AI Document Analyzer: import spec document → AI ambiguity detection → interactive clarification loop → structured Claude Code prompt generation, with MOCK mode for offline testing.

## Completed Tasks

| # | Task | Commit | Status |
|---|------|--------|--------|
| 1 | Create `ai_doc_analyzer.py` module | `fa5db87` | DONE |
| 2 | Add P14 routes to `demo_server.py` | `e976537` | DONE |
| 3 | Create `ai-doc-analyzer.html` + CSS | `88ae858` | DONE |
| 4 | Create `ai-doc-analyzer.js` UI logic | `3378ea2` | DONE |
| 5 | Add nav links to workbench/demo HTML | `0a5197f` | DONE |
| 6 | Create `tests/test_p14_ai_doc_analyzer.py` | `7039acb` | DONE |
| 7 | Codex review fixes | `4e429fd` | DONE |
| 8 | Regression check | — | DONE (400 passed, 1 pre-existing failure) |

## Key Implementation Details

### ai_doc_analyzer.py
- `Ambiguity`, `Question`, `ClarificationResult`, `P14SessionState` dataclasses
- `P14SessionStore` singleton (thread-safe in-memory dict)
- `analyze_document(text)` → returns `list[Ambiguity]` or `dict` (error)
- `evaluate_clarification(session, answer)` → `ClarificationResult` with progress
- `generate_prompt_document(session)` → markdown `str` or `dict` (error)
- `_call_anthropic()` → wraps `anthropic.Anthropic` SDK with error dict fallback
- MOCK mode: `P14_AI_MOCK=1` env var, 3 ambiguities, 3 questions, fixture prompt

### Routes
- `POST /api/p14/analyze-document` — validates session_id/document_text (max 10MB)/document_name
- `POST /api/p14/clarify` — validates session exists and answer non-empty; returns next_question or complete
- `POST /api/p14/generate-prompt` — validates session complete; returns markdown + word_count
- `GET /ai-doc-analyzer.html` — static page

### UI Page
- Two-column layout (left: upload+preview+ambiguity cards; right: clarification+prompt)
- Drag-and-drop file upload with type/size validation
- Ambiguity cards with confidence bar (red ≥75%, yellow ≥50%, green <50%)
- Clarification dialog with progress indicator ("Question 2 / 5") and skip option
- Auto-generate on clarification completion
- Blob URL download of prompt document as `.md`
- Status bar with session_id display and MOCK MODE badge

## Deviations from Plan

### Auto-fixed Issues

**Rule 1 - Bug: Double-append in clarification loop**
- **Found during:** Module testing
- **Issue:** `evaluate_clarification` was appending to `clarification_history` twice (once in outer function, once in mock evaluator)
- **Fix:** Removed double-append; history append moved to outer function only
- **Files modified:** `src/well_harness/ai_doc_analyzer.py`
- **Commit:** `4e429fd`

**Rule 1 - Bug: JS string literal corruption with Chinese curly quotes**
- **Found during:** `node --check` on ai-doc-analyzer.js
- **Issue:** Write tool misinterpreted Chinese curly quotes (`""`) as ASCII double quotes inside double-quoted JS strings
- **Fix:** Rewrote JS with ASCII-only string content (English placeholder text in UI strings)
- **Files modified:** `src/well_harness/static/ai-doc-analyzer.js`
- **Commit:** `3378ea2`

**Rule 2 - Type: analyze_document swallowing errors**
- **Found during:** Codex review
- **Issue:** `analyze_document` returned `[]` on API failure instead of propagating error
- **Fix:** Return `{"error": ..., "message": ...}` dict; callers handle via `isinstance(..., dict)` check
- **Files modified:** `src/well_harness/ai_doc_analyzer.py`, `src/well_harness/demo_server.py`
- **Commit:** `4e429fd`

**Rule 1 - Bug: _call_anthropic not catching SDK exceptions**
- **Found during:** Codex review
- **Issue:** `client.messages.create()` exceptions (auth failure, rate limit, network) would bubble up as unhandled exceptions
- **Fix:** Wrapped in `try/except Exception` returning error dict
- **Files modified:** `src/well_harness/ai_doc_analyzer.py`
- **Commit:** `4e429fd`

**Rule 2 - Type: generate_prompt_document returning error as markdown**
- **Found during:** Codex review
- **Issue:** If `_call_anthropic` returned error dict, it was returned verbatim as the prompt markdown
- **Fix:** Added `isinstance(result, dict)` check; propagate error dict instead
- **Files modified:** `src/well_harness/demo_server.py`
- **Commit:** `4e429fd`

**Rule 3 - Fix: Upload limit mismatch (500KB vs 10MB)**
- **Found during:** Codex review
- **Issue:** Server enforced 500KB limit; JS UI advertised 10MB
- **Fix:** Raised server limit to 10MB to match client
- **Files modified:** `src/well_harness/demo_server.py`
- **Commit:** `4e429fd`

**Rule 2 - Type: Empty ambiguity set leaves session stuck**
- **Found during:** Codex review
- **Issue:** If analyze returned 0 ambiguities, `questions=[]` but `is_complete=False`; client could never generate
- **Fix:** After building questions, if empty, set `session.is_complete=True`
- **Files modified:** `src/well_harness/demo_server.py`
- **Commit:** `4e429fd`

## Auth Gates

None encountered. `P14_AI_MOCK=1` environment variable enables fixture-only mode without requiring `ANTHROPIC_API_KEY`.

## Known Stubs

None.

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| threat_flag: new-endpoint | demo_server.py | 3 new POST endpoints accepting JSON payloads from client |
| threat_flag: file-upload | ai-doc-analyzer.html | FileReader.readAsText() reads client files into memory; size limited to 10MB |

No new surface beyond what is documented in the plan's threat model.

## Self-Check

- [x] `src/well_harness/ai_doc_analyzer.py` exists and imports without error
- [x] `src/well_harness/demo_server.py` has 3 new P14 routes registered
- [x] `src/well_harness/static/ai-doc-analyzer.html` exists (188 lines)
- [x] All 3 API helpers (`p14Analyze`, `p14Clarify`, `p14Generate`) implemented in JS
- [x] Nav links added to `workbench.html` and `demo.html`
- [x] 14 tests created and all pass
- [x] Codex reviews completed for ai_doc_analyzer.py and demo_server.py
- [x] Regression: 400 existing tests pass (1 pre-existing unrelated failure)

## Self-Check Result: PASSED

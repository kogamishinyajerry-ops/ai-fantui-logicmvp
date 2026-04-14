# P14-01 Plan Verification

## Status: CONDITIONAL PASS

The plan is well-structured with comprehensive threat modeling and clear task breakdown. However, there are several issues that require attention before execution.

---

## 1. Goal Coverage

### Exit Criteria Check

| Exit Criteria | Task(s) | Status |
|--------------|---------|--------|
| Engineer uploads via drag-drop or file picker | Task 3, Task 4 | Covered |
| AI analyzes and surfaces ambiguous sections with confidence scores | Task 1, Task 2 | Covered |
| Interactive confirmation loop (one at a time) | Task 1, Task 2, Task 4 | Covered |
| Loop terminates when AI determines information sufficient | Task 1 (evaluate_clarification) | Covered |
| Structured Claude Code prompt generated | Task 1 (generate_prompt_document) | Covered |
| Prompt document preview and export as markdown | Task 3, Task 4 (download button) | Covered |
| All existing tests continue to pass | Task 7 | Issue - see below |
| All 23 shared validation commands continue to pass | Task 7 | Issue - see below |
| Roadmap DB shows P14=Active | External | Out of scope |

Coverage: 7/9 criteria fully addressed

---

## 2. Dependency Analysis

### Dependency Graph Review

Task 1 (ai_doc_analyzer.py) ----+
                                  ├─ Task 2 (demo_server.py routes)
Task 3 (HTML/CSS) ----------------+
                                  ├─ Task 4 (JS)
Task 5 (nav links) ----------------+
                                  ├─ Task 6 (tests)
                                  |
                            Task 7 (regression)

### Issues Found

Issue 1: Wave 1 Task 5 has implicit dependency on Task 3
- Task 5 modifies workbench.html and demo.html to add links to /ai-doc-analyzer.html
- Wave 1 allows parallel execution, but nav link to non-existent page is harmless (just dead link)
- Severity: Warning - Not blocking, but ordering should be clarified

Issue 2: Task 4 depends on Task 3 HTML structure
- The JS requires the HTML panel IDs to exist
- Correctly placed in Wave 2 after Task 3
- Status: OK

Issue 3: No circular dependencies detected
- Graph is acyclic
- Status: OK

---

## 3. Validation Completeness

### Test Count Discrepancy (BLOCKER)

| Source | Test Count |
|--------|------------|
| Plan states | 92 tests |
| Actual current count | 387 tests (386 passing, 1 failing) |

The plan's regression check (Task 7) references an outdated baseline. The actual test suite has grown significantly since the baseline was established.

Impact: Task 7's verification command `python3 -m pytest tests/ -q` will report 386/387, not 92/92. The plan should update the expected count.

### Validation Suite Status (BLOCKER - Pre-existing)

The validation suite currently FAILS due to a pre-existing test failure:

FAILED tests/test_gsd_notion_sync.py::GsdNotionSyncTests::test_ensure_live_active_pages_recreates_archived_targets_and_persists_config

This failure existed before P14 development started. The plan's regression check (Task 7) will report this failure, but it is not caused by P14 implementation.

Recommendation: Either:
1. Fix the pre-existing test failure before P14 execution, OR
2. Update Task 7 to exclude this known-failing test from regression

### Mock Mode Verification

The plan defines P14_AI_MOCK=1 for testing. This pattern is consistent with other mock patterns in the codebase and allows tests without API calls.

Status: OK

---

## 4. Risk Identification

### Risk 1: PDF Parsing Not Implemented (BLOCKER)

Severity: High

Exit criteria specifies "PDF/markdown/text" support. The plan's Task 4 uses FileReader.readAsText() which:
- Works for: .md, .txt files
- Fails for: .pdf files (binary format, returns garbled text)

Fix needed: Either:
1. Add PDF.js for client-side PDF text extraction, OR
2. Add server-side PDF parsing (e.g., pypdf or pdfminer), OR
3. Document that PDF support requires pre-conversion to text

### Risk 2: Session State In-Memory Only (WARNING)

Severity: Medium

Plan specifies P14SessionStore as in-memory dict. This means:
- Server restart clears all sessions
- Multiple server instances do not share sessions
- No automatic session cleanup (memory leak potential)

Recommendation: Add session TTL or max-session limit to prevent memory growth.

### Risk 3: No API Key Rotation Handling (INFO)

Severity: Low

If ANTHROPIC_API_KEY becomes invalid mid-session, the clarification loop would fail. Plan handles missing key at startup (503 error) but not key revocation during use.

### Risk 4: AI Response Format Instability (INFO)

Severity: Medium

The plan relies on Claude API returning structured JSON. If the model changes output format, parsing fails. The plan should include error handling for malformed AI responses.

Plan already includes: try/except around JSON extraction with graceful error dict return.

### Risk 5: Mock Mode Test Completeness (WARNING)

Severity: Medium

The mock mode uses fixture data (MOCK_AMBIGUITIES, MOCK_PROMPT_DOCUMENT). If the real API behavior diverges from fixtures, tests will not catch it. Consider adding at least one integration test with real API (can be skipped in CI).

---

## 5. Wave Assignment

### Wave 1 (Parallel) - Issues Found

| Task | Dependencies | Status |
|------|-------------|--------|
| Task 1 (ai_doc_analyzer.py) | None | OK |
| Task 3 (HTML/CSS) | None | OK |
| Task 5 (nav links) | None (but links to Task 3 output) | Issue - see above |

### Wave 2

| Task | Dependencies | Status |
|------|-------------|--------|
| Task 2 (demo_server.py) | Task 1 | OK |
| Task 4 (JS) | Task 3 | OK |

### Wave 3

| Task | Dependencies | Status |
|------|-------------|--------|
| Task 6 (tests) | Task 1 + Task 2 | OK |

### Wave 4

| Task | Dependencies | Status |
|------|-------------|--------|
| Task 7 (regression) | All above | OK |

Overall: Waves correctly ordered, no blocking issues

---

## 6. Threat Model Review

### STRIDE Coverage

| Category | Threat ID | Component | Covered |
|----------|-----------|-----------|---------|
| Tampering | T-P14-01 | File upload | Yes |
| Information Disclosure | T-P14-02 | Session state | Yes |
| Spoofing | T-P14-03 | Anthropic API key | Yes |
| Repudiation | T-P14-04 | AI analysis results | Yes |
| Information Disclosure | T-P14-05 | API mock mode | Yes |
| Injection | T-P14-06 | AI-generated content | Yes |

### Missing Threats

| Threat | Category | Risk | Recommendation |
|--------|----------|------|----------------|
| XSS via confidence score display | I (Injection) | Low | Plan mitigates via text-only rendering |
| Session fixation | S (Spoofing) | Medium | Add session ID regeneration on privilege change |
| Denial of Service | D (DoS) | Medium | Max session count not specified |
| API rate limiting | D (DoS) | Low | No handling for Anthropic rate limits |

Overall: STRIDE coverage is adequate. No critical gaps.

---

## 7. Additional Verification

### Requirements Field Empty

The plan frontmatter has `requirements: []` which should reference exit criteria IDs. However, since this is a greenfield phase with no external requirements document, this is acceptable.

### Key Links Verification

All specified key links are present and traceable:

| Key Link | Pattern | Status |
|----------|---------|--------|
| HTML -> /api/p14/analyze-document | fetch() POST | Covered in Task 4 |
| HTML -> /api/p14/clarify | fetch() POST | Covered in Task 4 |
| HTML -> /api/p14/generate-prompt | fetch() POST | Covered in Task 4 |
| demo_server.py -> ai_doc_analyzer.py | Python import | Covered in Task 2 |
| ai_doc_analyzer.py -> ANTHROPIC_API_KEY | os.environ | Covered in Task 1 |

### Interface Contracts

The plan defines clear interface contracts with request/response shapes. These are implementation-ready.

---

## Issues Found

### Blockers (Must Fix Before Execution)

- [ ] Issue 1: PDF parsing not implemented
  - Task 4 uses FileReader.readAsText() which fails for binary PDFs
  - Exit criteria requires PDF support
  - Fix: Add PDF.js client-side or server-side PDF parsing, or document limitation

- [ ] Issue 2: Test baseline count incorrect
  - Plan references 92 tests, actual is 387 (386 passing)
  - Task 7 verification will show wrong count
  - Fix: Update Task 7 to expect "386/387" or current passing count

### Warnings (Should Fix)

- [ ] Issue 3: Wave 1 Task 5 has implicit dependency on Task 3
  - Nav links point to /ai-doc-analyzer.html created in Task 3
  - Dead link until Task 3 completes
  - Fix: Move Task 5 to Wave 2, or clarify dead links are acceptable during build

- [ ] Issue 4: Validation suite has pre-existing failure
  - test_gsd_notion_sync.py fails independently of P14
  - Task 7 regression check will report this failure
  - Fix: Either fix pre-existing failure or exclude from P14 regression scope

- [ ] Issue 5: Session state in-memory only
  - No TTL, cleanup, or persistence mechanism
  - Fix: Add session expiration (e.g., 1 hour TTL) to prevent memory leaks

---

## Recommendations

1. PDF Support Decision: Clarify whether PDFs must be processed client-side (PDF.js) or server-side (pypdf). This affects Task 1 (backend) and Task 4 (JS).

2. Update Test Baseline: Change Task 7 expectation from "92 tests" to "386 tests" to match current reality.

3. Session Cleanup: Add max_sessions limit or TTL-based eviction to P14SessionStore.

4. Move Task 5 to Wave 2: Prevent dead nav links during parallel execution.

5. Pre-existing Failure: Decide whether to fix test_gsd_notion_sync.py before P14 or accept it as known issue.

---

## Final Recommendation

CONDITIONAL PASS - The plan is well-structured and covers most exit criteria. However, the PDF parsing gap is a blocker since PDFs are explicitly in the exit criteria. Once PDF handling is addressed and the test baseline is corrected, the plan is ready for execution.

Required actions before execution:
1. Add PDF parsing capability (client-side or server-side)
2. Update Task 7 test count expectation
3. Resolve Wave 1 Task 5 ordering (move to Wave 2 or document acceptable dead link period)

Optional improvements:
- Session TTL/cleanup mechanism
- Pre-existing test failure resolution

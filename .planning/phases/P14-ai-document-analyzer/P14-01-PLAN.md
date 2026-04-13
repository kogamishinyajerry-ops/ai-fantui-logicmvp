---
phase: P14
plan: P14-01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/well_harness/ai_doc_analyzer.py
  - src/well_harness/demo_server.py
  - src/well_harness/static/ai-doc-analyzer.html
  - src/well_harness/static/ai-doc-analyzer.css
  - src/well_harness/static/ai-doc-analyzer.js
  - src/well_harness/static/workbench.html
  - src/well_harness/static/demo.html
  - tests/test_p14_ai_doc_analyzer.py
autonomous: false
requirements: []
user_setup:
  - service: Anthropic API
    why: "AI-powered document analysis and prompt generation"
    env_vars:
      - name: ANTHROPIC_API_KEY
        source: "Anthropic Console -> API Keys"
must_haves:
  truths:
    - Engineer can upload a file via drag-drop or file picker (PDF/markdown/text)
    - AI analysis surfaces specific ambiguous spec sections with confidence scores
    - Interactive confirmation loop presents one question at a time
    - Loop terminates when AI determines information is sufficient (no more blockers)
    - A structured Claude Code prompt document is generated
    - Prompt document can be previewed and downloaded as markdown
    - All existing 92 tests continue to pass (no regression)
  artifacts:
    - path: src/well_harness/ai_doc_analyzer.py
      provides: AI analysis module with mockable API
      min_lines: 150
    - path: src/well_harness/static/ai-doc-analyzer.html
      provides: Browser UI page
      min_lines: 200
    - path: src/well_harness/static/ai-doc-analyzer.js
      provides: UI logic + API calls
      min_lines: 200
    - path: src/well_harness/static/ai-doc-analyzer.css
      provides: Page styles
      min_lines: 50
    - path: tests/test_p14_ai_doc_analyzer.py
      provides: API route tests
      min_lines: 100
    - path: src/well_harness/demo_server.py
      provides: 3 new P14 routes + session management
      min_lines: 80
  key_links:
    - from: src/well_harness/static/ai-doc-analyzer.html
      to: /api/p14/analyze-document
      via: fetch() POST
      pattern: fetch.*api/p14/analyze-document
    - from: src/well_harness/static/ai-doc-analyzer.html
      to: /api/p14/clarify
      via: fetch() POST
      pattern: fetch.*api/p14/clarify
    - from: src/well_harness/static/ai-doc-analyzer.html
      to: /api/p14/generate-prompt
      via: fetch() POST
      pattern: fetch.*api/p14/generate-prompt
    - from: src/well_harness/demo_server.py
      to: src/well_harness/ai_doc_analyzer.py
      via: Python import
      pattern: from well_harness.ai_doc_analyzer
    - from: src/well_harness/ai_doc_analyzer.py
      to: ANTHROPIC_API_KEY
      via: os.environ
      pattern: os.environ.*ANTHROPIC_API_KEY
---

# P14-01 Plan: AI Document Analyzer — Full Pipeline

## Goal

Build a browser UI where engineers can import control-system logic circuit documents (PDF/markdown/text), trigger an AI-powered analysis pipeline that detects ambiguous spec descriptions, run a deep interactive confirmation dialogue loop to resolve ambiguities, and ultimately generate a structured Claude Code prompt document ready for new module development.

***

## Threat Model

| Boundary | Description |
|----------|-------------|
| client → server (file upload) | Untrusted file content crosses here; size-limited, type-checked |
| server → Anthropic API | API key env var; prompt injection mitigated by system prompt framing |
| server → client (generated content) | AI-generated markdown rendered in browser; no `innerHTML` with user content |

STRIDE:

| Threat ID | Category | Component | Disposition | Mitigation |
|-----------|----------|-----------|------------|------------|
| T-P14-01 | T (Tampering) | File upload | mitigate | Max file size 10MB; content-type check before processing |
| T-P14-02 | I (Information Disclosure) | Session state | mitigate | In-memory dict only; session_id scoped to single server instance |
| T-P14-03 | S (Spoofing) | Anthropic API key | mitigate | Read from `ANTHROPIC_API_KEY` env var; never log or expose |
| T-P14-04 | R (Repudiation) | AI analysis results | mitigate | All AI responses stored in session state for audit trail |
| T-P14-05 | I (Information Disclosure) | API mock mode | mitigate | `P14_AI_MOCK=1` returns fixtures only; never calls real API |
| T-P14-06 | I (Injection) | AI-generated content display | mitigate | All AI output rendered as text only; no `innerHTML` with raw content |

***

## Interface Contracts

### New P14 Routes

```
POST /api/p14/analyze-document
  Body: { "session_id": str, "document_text": str, "document_name": str }
  Returns: { "session_id": str, "ambiguities": [Ambiguity], "total_count": int }

POST /api/p14/clarify
  Body: { "session_id": str, "answer": str }
  Returns: { "session_id": str, "next_question": Question | null, "progress": { "answered": int, "remaining": int }, "is_complete": bool }

POST /api/p14/generate-prompt
  Body: { "session_id": str }
  Returns: { "session_id": str, "prompt_document": str, "word_count": int }
```

### Session State (in-memory dict keyed by session_id)

```python
@dataclass
class P14SessionState:
    session_id: str
    document_text: str
    document_name: str
    ambiguities: list[Ambiguity]
    answered_ambiguity_ids: list[str]
    clarification_history: list[tuple[str, str]]  # (question, answer)
    is_complete: bool
    generated_prompt: str | None
```

### Ambiguity Data

```python
@dataclass
class Ambiguity:
    id: str  # "amb-1", "amb-2", ...
    text_excerpt: str  # quoted snippet from document
    description: str  # what is ambiguous
    confidence_score: float  # 0.0-1.0
    suggested_clarification: str  # what to ask
```

***

## Tasks

### Task 1: Create `ai_doc_analyzer.py` module

**File:** `src/well_harness/ai_doc_analyzer.py`

**Action:** Create the AI analysis module with the following:

1. Dataclasses: `Ambiguity`, `Question`, `ClarificationResult`, `P14SessionState`
2. `P14SessionStore` class — thread-safe in-memory dict storing `session_id -> P14SessionState`
3. `analyze_document(text: str) -> list[Ambiguity]`:
   - If `P14_AI_MOCK=1` env var set, return fixture `MOCK_AMBIGUITIES`
   - Otherwise call Anthropic Messages API with `claude-opus-4-6` or `claude-sonnet-4-6`
   - System prompt: "You are a control-systems engineer reviewing logic circuit specifications..."
   - Extract ambiguities as structured JSON from response
4. `evaluate_clarification(session: P14SessionState, answer: str) -> ClarificationResult`:
   - Append (question, answer) to history
   - If `P14_AI_MOCK=1`, return mock cycle (after 3 answers → complete)
   - Otherwise call Claude API to determine if more questions needed
   - Return next question or `is_complete=True`
5. `generate_prompt_document(session: P14SessionState) -> str`:
   - If `P14_AI_MOCK=1`, return fixture prompt markdown
   - Otherwise call Claude API to synthesize all resolved content into structured prompt
   - Output: markdown with sections (system overview, logic nodes, condition rules, edge cases, implementation guidance)
6. Helper: `_call_anthropic(messages: list, system: str) -> str` — wraps `os.environ["ANTHROPIC_API_KEY"]`, uses `anthropic` Python SDK; if key missing returns error dict gracefully

**Verify:** `python3 -c "from well_harness.ai_doc_analyzer import analyze_document, P14SessionStore; print('import OK')"`

**Done:** Module imports without error; mock mode returns fixture data; session store accepts/returns session objects.

***

### Task 2: Add P14 routes to `demo_server.py`

**File:** `src/well_harness/demo_server.py`

**Action:** Add three new routes to `DemoRequestHandler`:

1. **Route constants** (near top of file):
   ```python
   P14_ANALYZE_PATH = "/api/p14/analyze-document"
   P14_CLARIFY_PATH = "/api/p14/clarify"
   P14_GENERATE_PATH = "/api/p14/generate-prompt"
   ```

2. **`do_GET` addition**: Serve `ai-doc-analyzer.html` at `GET /ai-doc-analyzer.html`

3. **`do_POST` addition**: Accept the three P14 routes in the `parsed.path not in {...}` check; route to new handler functions

4. **Handler functions** (add after existing handlers):
   - `_handle_p14_analyze(request_payload) -> tuple[dict, None] | tuple[None, dict]`
     - Validate: `session_id` (str), `document_text` (str, max 500KB), `document_name` (str, max 255 chars)
     - Create `P14SessionState`, store in `P14SessionStore`
     - Call `analyze_document(text)` → get ambiguities
     - Update session, return `{session_id, ambiguities, total_count}`
     - Error if `document_text` too large or empty
   - `_handle_p14_clarify(request_payload) -> tuple[dict, None] | tuple[None, dict]`
     - Validate: `session_id` exists in store, `answer` is non-empty string
     - Retrieve session, call `evaluate_clarification(session, answer)`
     - Update session, return `{session_id, next_question, progress, is_complete}`
   - `_handle_p14_generate(request_payload) -> tuple[dict, None] | tuple[None, dict]`
     - Validate: `session_id` exists in store, session is complete
     - Call `generate_prompt_document(session)`
     - Update session with generated prompt, return `{session_id, prompt_document, word_count}`

5. **Session store**: Instantiate `P14SessionStore` as a module-level singleton at the bottom of `demo_server.py`

6. **Error handling**: If `ANTHROPIC_API_KEY` is missing in non-mock mode, return `{"error": "anthropic_api_key_missing"}` with 503 status

**Verify:** `python3 -c "from well_harness.demo_server import P14_ANALYZE_PATH, P14_CLARIFY_PATH, P14_GENERATE_PATH; print('routes OK')"`

**Done:** Three routes are registered and route constants are importable.

***

### Task 3: Create `ai-doc-analyzer.html` + CSS

**File:** `src/well_harness/static/ai-doc-analyzer.html`

**File:** `src/well_harness/static/ai-doc-analyzer.css` (new file)

**Action:** Create a single-page browser UI:

1. **Hero section**: Page title "AI Document Analyzer", subtitle, nav strip (link back to demo.html and workbench.html)
2. **File upload zone**:
   - Drag-and-drop area (dashed border, "将文件拖到此处或点击选择" label)
   - Hidden file input (`accept=".pdf,.md,.txt"`)
   - File type/size validation (max 10MB, PDF/markdown/text)
   - Shows selected filename after selection
3. **Document preview panel**:
   - Read-only textarea showing uploaded document text
   - Character/word count display
4. **Analyze button**:
   - Primary action button: "开始 AI 分析"
   - Disabled until document is loaded
   - Shows spinner during API call
5. **Ambiguity list panel**:
   - Appears after analysis completes
   - Each ambiguity card shows: id, text excerpt (quoted), description, confidence bar (0-100%), suggested question
   - Cards styled with confidence color (red=high ambiguity, yellow=medium, green=low)
6. **Clarification dialog**:
   - Shows one question at a time
   - Text input for answer
   - "提交答案" submit button
   - Progress indicator: "问题 2 / 5"
   - "跳过" link to skip optional questions
7. **Sufficiency indicator**:
   - Progress bar or step indicator: N ambiguities answered, M remaining
   - When all resolved: "信息充分，可以生成" message
8. **Prompt document panel**:
   - Read-only textarea showing generated markdown
   - Word count display
   - "下载 Prompt 文档" button → Blob URL download as `.md`
9. **Status bar**: Shows current session_id, API mock mode indicator if active

CSS (`ai-doc-analyzer.css`): Follow existing `demo.css` patterns (CSS variables, utility classes). Two-column layout on desktop (left: upload+preview; right: analysis+clarification), single column on mobile.

**Verify:** Page loads in browser via `http://127.0.0.1:8000/ai-doc-analyzer.html` without JS console errors.

**Done:** All UI panels render; file upload shows filename; document text appears in preview textarea.

***

### Task 4: Create `ai-doc-analyzer.js`

**File:** `src/well_harness/static/ai-doc-analyzer.js`

**Action:** Create UI logic:

1. **File upload handling**:
   - `dragover`/`drop` event listeners on drop zone (preventDefault)
   - `change` event on file input
   - Use `FileReader.readAsText()` to read file content
   - Validate file type and size before reading
   - Populate document preview textarea
   - Enable analyze button

2. **API call helpers**:
   - `async function p14Analyze(sessionId, documentText, documentName)` → `POST /api/p14/analyze-document`
   - `async function p14Clarify(sessionId, answer)` → `POST /api/p14/clarify`
   - `async function p14Generate(sessionId)` → `POST /api/p14/generate-prompt`
   - All helpers parse JSON response; throw on non-2xx or `error` field

3. **Analyze flow**:
   - Generate `sessionId` (UUID via `crypto.randomUUID()`)
   - Call `p14Analyze()`
   - Render ambiguity cards with confidence bars
   - Start clarification loop (show first question)

4. **Clarification loop**:
   - Display current question in dialog panel
   - On submit: call `p14Clarify()`, receive next question or complete
   - Update progress indicator
   - If `is_complete`: show sufficiency message, auto-trigger generate

5. **Generate flow**:
   - Call `p14Generate()`
   - Populate prompt preview textarea
   - Enable download button

6. **Download**:
   - `Blob` from prompt document text
   - `URL.createObjectURL(blob)` → `<a download="logic-mvp-claude-prompt.md">` click

7. **Error display**:
   - Show inline error messages for API failures
   - For `anthropic_api_key_missing`: show setup instructions
   - For `document_too_large`: show size limit message

**Verify:** `node --check ai-doc-analyzer.js` (syntax check only, no runtime dependency)

**Done:** All API calls wired; file upload populates preview; analyze button triggers flow; clarification loop advances; download generates `.md` file.

***

### Task 5: Add nav links to `workbench.html` and `demo.html`

**File:** `src/well_harness/static/workbench.html`

**File:** `src/well_harness/static/demo.html`

**Action:**

1. In `workbench.html`: Add to the `.workbench-nav-panel` section:
   ```html
   <a class="workbench-nav-link" href="/ai-doc-analyzer.html">AI Document Analyzer</a>
   ```

2. In `demo.html`: Add to the navigation strip:
   ```html
   <a href="/ai-doc-analyzer.html">AI Document Analyzer</a>
   ```

**Verify:** Links appear in both pages; navigate to `ai-doc-analyzer.html`

**Done:** Both pages have working links to the new analyzer page.

***

### Task 6: Create `tests/test_p14_ai_doc_analyzer.py`

**File:** `tests/test_p14_ai_doc_analyzer.py`

**Action:** Create API route tests using the same HTTP server pattern as `test_demo.py`:

1. **Fixtures**: `MOCK_AMBIGUITIES` list, `MOCK_PROMPT_DOCUMENT` string

2. **Test class `P14AIAnalyzerTest`** (subclass of `unittest.TestCase` with HTTP server setup/teardown)

3. **Tests**:
   - `test_analyze_document_success` — POST valid payload, verify 200 + `ambiguities` list in response
   - `test_analyze_document_missing_session_id` — verify 400 error
   - `test_analyze_document_empty_text` — verify 400 error
   - `test_analyze_document_too_large` — send >500KB text, verify 400 error
   - `test_clarify_success` — analyze first, then clarify, verify next question returned
   - `test_clarify_session_not_found` — clarify with unknown session_id, verify 404
   - `test_clarify_empty_answer` — verify 400 error
   - `test_clarify_all_answered_then_complete` — mock cycle complete, verify `is_complete=True`
   - `test_generate_prompt_success` — complete clarification cycle, generate, verify markdown returned
   - `test_generate_prompt_session_not_found` — 404
   - `test_generate_prompt_incomplete_session` — generate before clarifying, verify 400 error
   - `test_static_page_serves` — GET `/ai-doc-analyzer.html`, verify 200

4. **Mock mode**: Set `P14_AI_MOCK=1` env var for all tests (no real API calls)

5. **HTTP server setup**: Same pattern as `test_demo.py` — start `ThreadingHTTPServer` with `DemoRequestHandler` on random port in `setUpClass`, stop in `tearDownClass`

**Verify:** `python3 -m pytest tests/test_p14_ai_doc_analyzer.py -v` — all tests pass

**Done:** All 11+ tests pass with mocked AI responses.

***

### Task 7: Regression check

**Action:** Run the full test suite and validation suite:

```bash
cd /Users/Zhuanz/20260407\ YJX\ AI\ FANTUI\ LogicMVP
python3 -m pytest tests/ -q --tb=short 2>&1 | tail -20
python3 tools/run_gsd_validation_suite.py 2>&1 | tail -20
```

**Verify:**
- All existing 92 tests pass (no new failures introduced)
- All 23 shared validation commands pass
- No import errors in `well_harness` package

**Done:** Baseline regression confirmed — 92 tests green, 23 validation commands green.

***

## Dependency Graph

```
Task 1 (ai_doc_analyzer.py) ──────┐
                                   ├─► Task 2 (demo_server.py routes)
Task 3 (HTML/CSS) ────────────────┤
                                   ├─► Task 4 (JS)
Task 5 (nav links) ───────────────┤
                                   ├─► Task 6 (tests)
                                   │
                             Task 7 (regression)
```

**Wave 1 (parallel):**
- Task 1: `ai_doc_analyzer.py` (backend module, no dependencies)
- Task 3: `ai-doc-analyzer.html` + CSS (UI layout, no dependencies)
- Task 5: Nav links (small edits, no dependencies)

**Wave 2 (after Task 1 + 2):**
- Task 2: demo_server.py routes (imports Task 1, adds routes)
- Task 4: JS (depends on Task 3 HTML structure)

**Wave 3 (after Task 2 + 4):**
- Task 6: Tests (depends on Task 2 routes + Task 1 module)

**Wave 4:**
- Task 7: Regression check (after all above)

***

## Decision Coverage Matrix

| Decision ID | Plan | Task | Full/Partial | Notes |
|-------------|------|------|--------------|-------|
| (User locked: none — no CONTEXT.md for P14) | P14-01 | All | Full | Greenfield implementation, all decisions are Claude's discretion |

***

## Validation

- [ ] `python3 -c "from well_harness.ai_doc_analyzer import *"` — no import error
- [ ] `python3 -c "from well_harness.demo_server import P14_ANALYZE_PATH"` — no import error
- [ ] All 11+ P14 tests pass: `python3 -m pytest tests/test_p14_ai_doc_analyzer.py -v`
- [ ] All 92 existing tests pass: `python3 -m pytest tests/ -q`
- [ ] All 23 shared validation commands pass: `python3 tools/run_gsd_validation_suite.py`
- [ ] `http://127.0.0.1:8000/ai-doc-analyzer.html` loads without JS errors
- [ ] File upload shows document text in preview
- [ ] Analyze button triggers AI flow (mock mode)
- [ ] Clarification loop advances through questions
- [ ] Prompt document generates and downloads as `.md`
- [ ] Nav links appear in `workbench.html` and `demo.html`

***

## Success Criteria

1. Engineer can upload a PDF/markdown/text file via drag-drop or file picker
2. AI analysis returns a list of ambiguities with confidence scores (mock or real API)
3. Clarification loop presents one question at a time; after all answered, loop terminates
4. Structured Claude Code prompt document is generated and downloadable
5. New page is accessible from `demo.html` and `workbench.html` navigation
6. All 92 existing tests pass (no regression)
7. All 23 shared validation commands pass (no regression)
8. P14 API routes have test coverage with mocked AI calls

***

## Output

After completion, create `.planning/phases/P14-ai-document-analyzer/P14-01-SUMMARY.md`

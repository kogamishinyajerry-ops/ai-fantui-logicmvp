# Shelved: LLM Features

**Shelved date:** 2026-04-22
**Reason:** User directive — 暂时把植入 LLM 的智能语言控制功能拔掉，留存在合适位置。除非 Kogami 明确声明需要接入，否则不再进入开发流程。
**Branch:** `claude/c919-etras-frozen-v1-migration`
**Related UI restructure phase:** Phase A of 3-category × 2-case workstation reorg.

---

## What was shelved

### Static frontend (6 files) — from `src/well_harness/static/`
| File | Role |
|------|------|
| `chat.html` | LLM chat UI entry point (previously default `/` route) |
| `chat.js` | Chat event handlers + calls to `/api/chat/explain,operate,reason` |
| `chat.css` | Chat styling |
| `ai-doc-analyzer.html` | P14 document analyzer drag-drop UI |
| `ai-doc-analyzer.js` | P14 event handlers + calls to `/api/p14/*` |
| `ai-doc-analyzer.css` | P14 styling |

### Python modules (2 files) — from `src/well_harness/`
| File | Role |
|------|------|
| `llm_client.py` | `LLMClient` protocol + `MiniMaxClient` + Ollama backend + `get_llm_client()` factory |
| `ai_doc_analyzer.py` | `P14SessionStore`, `analyze_document`, `evaluate_clarification`, `generate_prompt_document`, `convert_markdown_to_intake`, `run_pipeline_from_intake` |

### Tests (9 files) — from `tests/`
| File | Target |
|------|--------|
| `test_llm_client.py` | `llm_client.py` |
| `test_chat_operate.py` | `/api/chat/operate` |
| `test_chat_operate_input_validation.py` | `/api/chat/operate` input guards |
| `test_chat_reason_input_validation.py` | `/api/chat/reason` input guards |
| `test_p15_pipeline_integration.py` | `/api/p15/*` |
| `test_p43_doc_analyzer_blocker_fix.py` | P43 spike × doc analyzer |
| `test_pitch_prewarm.py` | CLI pitch prewarm (LLM-dependent) |
| `test_pitch_symbols.py` | LLMClient protocol symbol whitelist |
| `test_demo_llm_tests_snippet.py` | **Extracted from `tests/test_demo.py:870-1187`** — 7 `DemoIntentLayerTests` methods targeting chat_explain + chat.html/.js assets (not directly runnable; intended as reference for restoration) |

---

## Routes removed from `src/well_harness/demo_server.py`

### Chat/MiniMax (4 routes)
- `POST /api/chat/explain`
- `POST /api/chat/explain-prewarm`
- `POST /api/chat/operate`
- `POST /api/chat/reason`

### P14 Doc Analyzer (3 routes)
- `POST /api/p14/analyze-document`
- `POST /api/p14/clarify`
- `POST /api/p14/generate-prompt`

### P15 Pipeline (2 routes)
- `POST /api/p15/convert-to-intake`
- `POST /api/p15/run-pipeline`

---

## What remains in the active tree after Phase A

- All non-LLM demo routes: `/api/demo`, `/api/lever-snapshot`, workbench APIs, diagnosis, monte-carlo, sensitivity-sweep, hardware-schema
- `demo.html`, `workbench.html` static assets
- The P43 authority contract (R1-R6) tests + `workbench_bundle.py` logic
- C919 ETRAS frozen V1 adapter (separate from LLM)

Phase B (next) will redirect `/` from the removed `chat.html` to `/demo.html`.

---

## How to restore (if Kogami approves reintegration)

1. `git mv archive/shelved/llm-features/static/* src/well_harness/static/`
2. `git mv archive/shelved/llm-features/src/{llm_client.py,ai_doc_analyzer.py} src/well_harness/`
3. `git mv archive/shelved/llm-features/tests/test_*.py tests/` (8 files; the `_snippet.py` needs manual merge back into `test_demo.py:DemoIntentLayerTests`)
4. Restore `demo_server.py` imports, route constants, POST allowlist entries, dispatch blocks, and handler bodies (reference pre-Phase-A git history: `git log --oneline -- src/well_harness/demo_server.py`)
5. Run `pytest` and verify full suite passes

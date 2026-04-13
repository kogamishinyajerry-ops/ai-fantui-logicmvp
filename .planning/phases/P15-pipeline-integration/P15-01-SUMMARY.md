# Phase P15 Plan 01: Pipeline Integration Summary

## One-liner

P15 pipeline integration: P14 markdown document output connects to P7/P8 intake pipeline via AI-powered converter, enabling full session→intake→assessment→bundle flow.

## Metadata

| Field | Value |
|-------|-------|
| Phase | P15 |
| Plan | 01 |
| Subsystem | well_harness |
| Tags | pipeline-integration, intake-packet, P14-to-P15 |
| Dependency Graph | **Requires:** P14 (ai_doc_analyzer), P7 (document_intake), P8 (workbench_bundle) **Provides:** P15 pipeline routes, Run Pipeline UI |
| Tech Stack | Python, Flask HTTP routes, JavaScript UI, Anthropic API |
| Key Files Created | `src/well_harness/ai_doc_analyzer.py`, `src/well_harness/demo_server.py`, `src/well_harness/static/ai-doc-analyzer.html`, `src/well_harness/static/ai-doc-analyzer.js`, `src/well_harness/static/ai-doc-analyzer.css`, `tests/test_p15_pipeline_integration.py` |
| Key Files Modified | `src/well_harness/ai_doc_analyzer.py` (added P15 section), `src/well_harness/demo_server.py` (added P15 routes), `src/well_harness/static/ai-doc-analyzer.html` (added Run Pipeline section), `src/well_harness/static/ai-doc-analyzer.js` (added P15 API calls and pipeline handler), `src/well_harness/static/ai-doc-analyzer.css` (added pipeline button/result styles) |
| Duration | ~20 minutes |
| Completed | 2026-04-14 |

## Decisions Made

1. **Mock intake packet uses `open_circuit` not `signal_loss`**: `validate_fault_kind()` in `fault_taxonomy.py` only accepts the enum values. `open_circuit` is the closest semantic match for a signal loss fault mode.

2. **Empty string `unit` rejected by `document_intake`**: `unit` must be a non-empty string. Components with no unit use `"state"` as a neutral placeholder.

3. **Allowed fields must be lists not tuples**: `document_intake._tuple_or_empty()` converts lists/tuples to tuples, but the schema validation requires lists for JSON round-trip compatibility. Changed `("0", "1")` tuples to `["0", "1"]` lists and `allowed_range` to `[0, 100]`.

4. **`WorkbenchBundle` uses `fault_diagnosis_report` not `diagnosis_report`**: Fixed attribute name in `run_pipeline_from_intake()`.

## Deviation from Plan

None — plan executed exactly as written.

## Test Results

- `tests/test_p15_pipeline_integration.py`: **19 passed**
- `tests/test_p14_ai_doc_analyzer.py`: **14 passed** (no regression)
- Full suite: **345 passed** (no regression)

## Commits

| Hash | Message |
|------|---------|
| `73771db` | feat(p15): add markdown-to-intake converter and pipeline runner |
| `5052883` | feat(p15): add /api/p15/* routes to demo_server.py |
| `e72e3f3` | feat(p15): add Run Pipeline button and pipeline UI to ai-doc-analyzer |
| `4a60c19` | test(p15): add pipeline integration tests |

## Success Criteria Status

| Criterion | Status |
|-----------|--------|
| `convert_markdown_to_intake()` converts P14 markdown to valid intake packet dict | PASS |
| `run_pipeline_from_intake()` runs full P7/P8 pipeline and returns bundle | PASS |
| `/api/p15/convert-to-intake` route works | PASS |
| `/api/p15/run-pipeline` route works | PASS |
| AI-doc-analyzer.html has "Run Pipeline" button | PASS |
| P15 tests all pass (19 passed) | PASS |
| All P14 tests still pass (14 passed, no regression) | PASS |
| All Codex reviews completed | PENDING (running async) |

## Threat Flags

None — P15 adds two new HTTP routes and AI conversion logic, all within the existing well_harness boundary with no trust boundary changes.
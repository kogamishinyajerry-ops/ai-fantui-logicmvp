# P43-01 Spike · real_pdf_happy_path fixture

**Semantic meaning**: function/HTTP handler contract proof with pdf metadata reference (NOT pdf-binary-consumed).

**Directory name note**: `real_pdf_happy_path` is v2 legacy naming. Per P43-01-00-PLAN.md §1c honesty boundary, the actual scope is:
- intake_packet dict (compliant with `ControlSystemIntakePacket` dataclass)
- pdf metadata via `source_documents.location` (no SHA field — `SourceDocumentRef` dataclass does not consume `sha256`)
- `run_pipeline_from_intake()` or `/api/p15/run-pipeline` handler invocation + assert return shape

Not equivalent to: "pdf binary consumed", "full user flow pipeline proof", or "from pdf bytes to bundle".

## Files

- `intake_minimal_ready.json` — minimal compliant intake packet referencing real C919 ETRAS pdf via metadata; uses stable clarification question_ids (`source_documents`, `component_state_domains`, `timeline_rules`, `fault_taxonomy`) per `default_workbench_clarification_questions()` at `src/well_harness/system_spec.py:244`.
- `expected_pipeline_response.json` — asserted_pass evidence of S1 happy path (post-Step-B · Kogami Option X applied; Bugs A/B1/B2 fixed at `ai_doc_analyzer.py:840,843,866,867`). See `.planning/phases/P43-control-logic-workbench/reports/p43-01-contract-proof/CONTRACT-PROOF-REPORT.md` §4 for exit-criterion evidence.

## Clarification answer stable IDs

Four stable question_ids from `system_spec.py:244` are used verbatim; the fixture does NOT use the buggy `clarify-{i}` pattern written by `_inject_clarification_answers()` at `ai_doc_analyzer.py:785-806` (R6 report-only finding).

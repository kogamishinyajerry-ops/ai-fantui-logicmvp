# Pre-Pitch Readiness Scorecard

- **Overall:** ✅ **GREEN**
- **Generated:** `2026-04-19T01:28:32+00:00`
- **Staleness threshold:** 24.0h

## Dimension verdicts

| Dimension | Verdict | Latest artefact | Age (h) | Detail |
| --------- | ------- | --------------- | ------- | ------ |
| Dress Rehearsal (wow_a/b/c) | ✅ GREEN | `dress_rehearsal_20260418T063146Z` | 18.9 | ✅ PASS |
| Pitch Explain Prewarm | ✅ GREEN | `pitch_prewarm_20260419T012811Z` | 0.0 | cache verified 2/2 · backend=ollama / qwen2.5:7b-instruct |
| Integrated Timing (best-of-2 backends) | ✅ GREEN | `integrated_timing_ollama_20260418T132211Z` | 12.1 | winner=Ollama GREEN · other=MiniMax YELLOW — pitch 日用 Ollama 主路径（findings §5.1） |
| Backend Switch Drill | ✅ GREEN | `backend_switch_drill_20260418T134550Z` | 11.7 | minimax_to_ollama: p50=108ms (GREEN) · ollama_to_minimax: p50=107ms (GREEN) |
| Local Model Smoke | ✅ GREEN | `local_model_smoke_20260418T072226Z` | 18.1 | verdict=PASS |
| Dual-Backend Rehearsal | ✅ GREEN | `demo_rehearsal_dual_backend_20260418T074215Z` | 17.8 | verdict=PASS |

## Interpretation

- ✅ GREEN: artefact fresh, all sub-verdicts pass
- ⚠️  YELLOW: stale (> threshold), degraded, or partial pass — still demo-able but investigate
- ❌ RED: no artefact on disk OR drill reported failure — must re-run before pitch

## Not covered by this scorecard

- pytest suite (run `python3 -m pytest`)
- adversarial 8/8 (run `python3 src/well_harness/static/adversarial_test.py`)
- browser-level UI / Canvas rendering (manual eyeball)
- network conditions at venue (manual check)

See `docs/demo/preflight_checklist.md` for the complete 17-item T-0 list.

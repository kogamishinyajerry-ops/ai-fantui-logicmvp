# Pre-Pitch Readiness Scorecard

- **Overall:** ✅ **GREEN**
- **Generated:** `2026-04-18T14:59:41+00:00`
- **Staleness threshold:** 24.0h

## Dimension verdicts

| Dimension | Verdict | Latest artefact | Age (h) | Detail |
| --------- | ------- | --------------- | ------- | ------ |
| Dress Rehearsal (wow_a/b/c) | ✅ GREEN | `dress_rehearsal_20260418T063146Z` | 8.5 | ✅ PASS |
| Integrated Timing (best-of-2 backends) | ✅ GREEN | `integrated_timing_ollama_20260418T132211Z` | 1.6 | winner=Ollama GREEN · other=MiniMax YELLOW — pitch 日用 Ollama 主路径（findings §5.1） |
| Backend Switch Drill | ✅ GREEN | `backend_switch_drill_20260418T134550Z` | 1.2 | minimax_to_ollama: p50=108ms (GREEN) · ollama_to_minimax: p50=107ms (GREEN) |
| Local Model Smoke | ✅ GREEN | `local_model_smoke_20260418T072226Z` | 7.6 | verdict=PASS |
| Dual-Backend Rehearsal | ✅ GREEN | `demo_rehearsal_dual_backend_20260418T074215Z` | 7.3 | verdict=PASS |

## Interpretation

- ✅ GREEN: artefact fresh, all sub-verdicts pass
- ⚠️  YELLOW: stale (> threshold), degraded, or partial pass — still demo-able but investigate
- ❌ RED: no artefact on disk OR drill reported failure — must re-run before pitch

## Not covered by this scorecard

- pytest suite (run `python3 -m pytest`)
- adversarial 8/8 (run `python3 src/well_harness/static/adversarial_test.py`)
- browser-level UI / Canvas rendering (manual eyeball)
- network conditions at venue (manual check)

See `docs/demo/preflight_checklist.md` for the complete 16-item T-0 list.

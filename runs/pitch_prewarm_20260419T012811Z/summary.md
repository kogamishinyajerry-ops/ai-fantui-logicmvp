# Pitch Prewarm

- **Verdict:** ✅ **GREEN**
- **Generated:** `2026-04-19T01:28:26Z`
- **Backend:** `ollama`
- **Model:** `qwen2.5:7b-instruct`
- **Boot:** `309.9`
- **Verified cache hits:** `2/2`

## Canonical cases

| Case | Question | Snapshot | Active logic | Nodes |
| ---- | -------- | -------- | ------------ | ----- |
| wow_a_logic1_active | L1门为什么active | 200 (1.5 ms) | logic1, logic2 | 19 |
| wow_a_logic3_active | L3门为什么active | 200 (1.3 ms) | logic2, logic3 | 19 |

## Prewarm rounds

| Round | Status | Elapsed (ms) | Warmed | Cache hits | Cache misses | Errors |
| ----- | ------ | ------------ | ------ | ---------- | ------------ | ------ |
| warm | 200 | 14900.8 | 2/2 | 0 | 2 | 0 |
| verify_cache | 200 | 1.2 | 2/2 | 2 | 0 | 0 |

Pitch-day rule: rerun this script after any demo_server restart or backend switch, because the explain cache is process-local.

# Integrated Timing Rehearsal — backend=ollama model=qwen2.5:7b-instruct

- boot_ms: 209.4
- ready: True
- overall_verdict: **GREEN**
- over_budget_sections: 0
- degraded_sections: 0

## Per-section budget vs actual

| 段 | 名称 | 段时长 | budget_api | actual_api | 裕度 | verdict | degraded |
| -- | --- | ----- | ---------- | ---------- | ---- | ------- | -------- |
| 0 | Opening | 90s | 0ms | 0ms | 0ms | no_api | 0 |
| 1 | wow_a 因果链 | 240s | 15000ms | 8876.9ms | 6123.1ms | within_budget | 0 |
| 2 | wow_b 蒙特卡洛 | 180s | 3000ms | 200.6ms | 2799.4ms | within_budget | 0 |
| 3 | wow_c 反诊断 | 150s | 1000ms | 5.3ms | 994.7ms | within_budget | 0 |
| 4 | Fallback (backend switch) | 180s | 20000ms | 3281.9ms | 16718.1ms | within_budget | 0 |
| 5 | R1–R5 总结 | 150s | 0ms | 0ms | 0ms | no_api | 0 |
| 6 | 闭场 | 90s | 0ms | 0ms | 0ms | no_api | 0 |

## Per-case detail

### 段 1 · wow_a 因果链

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| snapshot_init | `/api/lever-snapshot` | wow | 1.0ms | 200 | — |
| snapshot_beat_early | `/api/lever-snapshot` | wow | 1.3ms | 200 | — |
| snapshot_beat_deep | `/api/lever-snapshot` | wow | 1.4ms | 200 | — |
| chat_explain_L1 | `/api/chat/explain` | chat | 5123.9ms | 200 | — |
| chat_explain_L3 | `/api/chat/explain` | chat | 3749.3ms | 200 | — |

### 段 2 · wow_b 蒙特卡洛

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| mc_1k | `/api/monte-carlo/run` | wow | 184.8ms | 200 | — |
| mc_10k | `/api/monte-carlo/run` | wow | 15.8ms | 200 | — |

### 段 3 · wow_c 反诊断

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| diag_thr_lock | `/api/diagnosis/run` | wow | 5.3ms | 200 | — |

### 段 4 · Fallback (backend switch)

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| fallback_explain | `/api/chat/explain` | chat | 3281.9ms | 200 | — |


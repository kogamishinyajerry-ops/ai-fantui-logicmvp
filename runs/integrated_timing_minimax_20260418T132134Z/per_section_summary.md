# Integrated Timing Rehearsal — backend=minimax

- boot_ms: 206.0
- ready: True
- overall_verdict: **YELLOW**
- over_budget_sections: 1
- degraded_sections: 0

## Per-section budget vs actual

| 段 | 名称 | 段时长 | budget_api | actual_api | 裕度 | verdict | degraded |
| -- | --- | ----- | ---------- | ---------- | ---- | ------- | -------- |
| 0 | Opening | 90s | 0ms | 0ms | 0ms | no_api | 0 |
| 1 | wow_a 因果链 | 240s | 15000ms | 18403.6ms | -3403.6ms | over_budget | 0 |
| 2 | wow_b 蒙特卡洛 | 180s | 3000ms | 168.8ms | 2831.2ms | within_budget | 0 |
| 3 | wow_c 反诊断 | 150s | 1000ms | 14.9ms | 985.1ms | within_budget | 0 |
| 4 | Fallback (backend switch) | 180s | 20000ms | 11684.7ms | 8315.3ms | within_budget | 0 |
| 5 | R1–R5 总结 | 150s | 0ms | 0ms | 0ms | no_api | 0 |
| 6 | 闭场 | 90s | 0ms | 0ms | 0ms | no_api | 0 |

## Per-case detail

### 段 1 · wow_a 因果链

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| snapshot_init | `/api/lever-snapshot` | wow | 1.1ms | 200 | — |
| snapshot_beat_early | `/api/lever-snapshot` | wow | 1.4ms | 200 | — |
| snapshot_beat_deep | `/api/lever-snapshot` | wow | 1.5ms | 200 | — |
| chat_explain_L1 | `/api/chat/explain` | chat | 9172.4ms | 200 | — |
| chat_explain_L3 | `/api/chat/explain` | chat | 9227.2ms | 200 | — |

### 段 2 · wow_b 蒙特卡洛

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| mc_1k | `/api/monte-carlo/run` | wow | 143.5ms | 200 | — |
| mc_10k | `/api/monte-carlo/run` | wow | 25.3ms | 200 | — |

### 段 3 · wow_c 反诊断

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| diag_thr_lock | `/api/diagnosis/run` | wow | 14.9ms | 200 | — |

### 段 4 · Fallback (backend switch)

| case | path | bucket | elapsed | status | degraded |
| ---- | ---- | ------ | ------- | ------ | -------- |
| fallback_explain | `/api/chat/explain` | chat | 11684.7ms | 200 | — |


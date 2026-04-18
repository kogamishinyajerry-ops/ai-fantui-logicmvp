# Rehearsal Baseline Freeze · 2026-04-18

**Freeze timestamp (UTC):** 2026-04-18T06:31:46Z
**Scope:** P20.2 立项汇报彩排冻结基线——3 wow moments × 13 steps 的 API 层真跑输出。
**Purpose:** 当演示现场任一环节失败时，此基线作为 R3 可审计证据 + 降级话术锚点。

---

## 1 · 冻结对象

| 类型 | 路径 | 说明 |
|---|---|---|
| Markdown 报告 | `runs/dress_rehearsal_20260418T063146Z/rehearsal_report.md` | 可读摘要 |
| 时间线 JSON | `runs/dress_rehearsal_20260418T063146Z/wow_a_timeline.json` | wow_a 3 步原始响应 |
| 时间线 JSON | `runs/dress_rehearsal_20260418T063146Z/wow_b_timeline.json` | wow_b 3 步 MC 原始响应 |
| 时间线 JSON | `runs/dress_rehearsal_20260418T063146Z/wow_c_timeline.json` | wow_c 7 步诊断原始响应 |
| 打包 tarball | `runs/rehearsal_20260418T063146Z_baseline.tar.gz` | 上述全部 + 可离线分发 |

**Tarball 校验：**
```
SHA-256: df00dd9b230131a07effa3092eb12481cfb34118b252f1df5f352e2253453350
Size:    1555 bytes
```

## 2 · 基线指标（硬数）

| 场景 | Steps | Pass | Fail | Scenario Wall | Notes |
|---|---|---|---|---|---|
| wow_a · causal chain | 3 | 3 | 0 | 4ms | 三拍全部 < 500ms 预算 |
| wow_b · monte carlo  | 3 | 3 | 0 | 279ms | 10k trials 48ms（预算 5s）+ 重放确定性一致 |
| wow_c · reverse diag | 7 | 7 | 0 | 72ms | 6 outcomes + invalid_outcome 400 兜底 |
| **合计** | **13** | **13** | **0** | **0.56s 全流程** | |

## 3 · 生成链路（复现步骤）

```bash
# 从冻结起点开始复现
git checkout 4098723    # HEAD at freeze time
python3 scripts/dress_rehearsal.py
# 输出会落到 runs/dress_rehearsal_<新ts>/；与冻结包逐字段对比
diff <(jq -S . runs/dress_rehearsal_20260418T063146Z/wow_a_timeline.json) \
     <(jq -S . runs/dress_rehearsal_<新ts>/wow_a_timeline.json)
```

真值引擎在相同输入下严格确定性（wow_b_10k_replay 步骤已校验），
因此 wow_a、wow_c 应逐字段一致；wow_b 的 `elapsed_ms` 字段允许抖动。

## 4 · 降级路径引用

本冻结包 + `docs/demo/disaster_runbook.md` 形成完整兜底矩阵：
- 场景 2（MC 超时）→ 展示本文件 §2 的 wow_b 基线数据
- 场景 4（server 挂掉）→ 解包 tarball 继续讲解
- 场景 6（Archive 导出失败）→ 用本 tarball 直接作为证据包

## 5 · 生命周期

- **创建：** 2026-04-18 P20.2 Tier 2/3
- **到期：** 下一次彩排冻结生效时（预期 demo 当日前 24h 再冻一次）
- **删除策略：** 保留；历史冻结包作为 R3 审计长期证据

_Freeze signed off by: Claude Code Opus 4.7 (20x Max) · Execution-by: opus47-max_

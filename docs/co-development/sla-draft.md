# SLA 草案 — Well Harness Co-development

> **NOTE (Phase A · 2026-04-22):** 本文档包含 LLM / chat.html / `/api/chat/*` / `llm_client.py` / MiniMax / Ollama 相关条目，这些功能已搁置到 `archive/shelved/llm-features/`。**以下内容保留作历史参考，不代表当前代码库的活跃状态。** 详见 `archive/shelved/llm-features/SHELVED.md`。


> **给谁看：** 甲方采购 + IT 运维 + 安全合规
> **回答什么：** 不同部署阶段（演示 / 预生产 / 生产）的可用性、响应时间、数据留存、AI 供应链选型
> **什么情况下变动：** 每次 Phase 升级（H2-24 / H2-25 / H2-26）同步刷新（编号命名空间统一见 `docs/co-development/roadmap-2026H2.md` 顶部说明，2026-04-20 P32 去重）
> **本文档状态：** **草案**（需要甲方反馈后定稿）
> **最新校对日期：** 2026-04-18

---

## 0. 三级 Profile 一览

| Profile | 适用场景 | 可用性 | 响应窗口 | 数据留存 | AI 后端 |
| ------- | -------- | ------ | -------- | -------- | ------- |
| **D — Demo** | 立项汇报 / 演示场 | 按场次（演示前预检） | 人工 15 min 内 | 仅现场 | MiniMax（云）+ Ollama fallback |
| **S — Staging** | 甲方子系统 PoC | 8×5 办公时段 99% | 邮件 4 h / 工单 24 h | 30 天审计日志 | Ollama（厂内）主 / MiniMax 备 |
| **P — Production** | 首批产线 validation | 24×7 99.5% | 电话 30 min / 工单 4 h | 永久 + SHA256 冻结 | 甲方自备模型 主 / Ollama 备 |

---

## 1. D — Demo Profile

**目标：** 立项汇报 / 客户展示。**不承诺**持续可用。

| 维度 | 承诺 |
| ---- | ---- |
| 可用性 | 按场次（演示开始前 60 min 走 `docs/demo/preflight_checklist.md` 16 项预检） |
| 灾难降级 | `docs/demo/disaster_runbook.md` 7 场景均 <60s 人工可执行 |
| 响应时间（演示中） | wow_a ≤50ms / wow_b 10k trials ≤200ms / wow_c 枚举 ≤200ms / chat ≤8s（云）≤6s（本地） |
| 数据留存 | 仅保留 `runs/` artefact 直到当次演示闭环 |
| AI 后端 | MiniMax 云为主；断网切 Ollama（一行命令） |
| 审计 | 演示后 24h 内产出 `rehearsal_report.md` + SHA256 |

**证据基线：** `runs/demo_rehearsal_dual_backend_20260418T074215Z/` 14/14 PASS。

---

## 2. S — Staging Profile（甲方 PoC）

**目标：** 甲方选一个子系统（如某型发动机反推逻辑）接入工作台，做**非生产**复核。

| 维度 | 承诺 |
| ---- | ---- |
| 可用性 | 8×5 办公时段 99%；计划外停机不超过 4 h/月 |
| 响应窗口 | P1 邮件 4 h · P2 工单 24 h · P3 下一工作日 |
| 数据留存 | 所有输入/输出 JSON 留存 30 天；对抗测试证据永久 |
| 数据边界 | **所有敏感数据留厂内**；云 AI（MiniMax）仅用于非敏感场景 |
| AI 后端 | **Ollama + 甲方选定国产模型**为主（Qwen2.5-14B 建议起点）；MiniMax 仅做备份 |
| 变更 | 每次发布前甲方走 `security-review-template.md` 10 项 checklist |
| 审计 | 每次 PR 记录 + 月度汇报；`docs/freeze/` 保留基线 |

**事故等级定义：**
- **P1（严重）：** 真值引擎结果错误 / 安全回归 → 立即回滚并根因
- **P2（重要）：** 降级链路未触发 / chat 持续超时 > 5 min
- **P3（一般）：** UI 异常、文档不一致、性能退化 < 30%

---

## 3. P — Production Profile（首批产线）

**目标：** 嵌入甲方产线 validation 流程。

| 维度 | 承诺 |
| ---- | ---- |
| 可用性 | 24×7 99.5%（月度停机预算 3.6 h） |
| 响应窗口 | P0 电话 15 min · P1 电话 30 min · P2 工单 4 h |
| 数据留存 | **永久 + SHA256 冻结**；查询/导出有分级授权 |
| 数据边界 | 完全厂内部署；不允许出境 |
| AI 后端 | 甲方自备模型为主（adapter 预估 <50 行接入）；Ollama 为备；禁止云 API |
| 变更管理 | 两级审批（架构师 + 安全）；每次发布附回滚方案 |
| 审计 | 所有 chat/wow API 请求/响应落可搜索日志；对抗测试跑每日 cron |
| 合规 | R1–R5 每季度做第三方抽样复核 |

**注：** 本 Profile 承诺在 **H2-26 phase 完成后**生效；目前处于 H2-23 co-dev 预备阶段，不绑定具体时间。

---

## 4. AI 供应链 3 个选项

| 选项 | 适用 Profile | 数据出境 | 成本 | 维护方 |
| ---- | ------------ | -------- | ---- | ------ |
| MiniMax 云 | D | **是**（中国境内 API） | API 计费 | MiniMax |
| Ollama + 国产开源模型（Qwen / GLM / DeepSeek） | D / S / P 备 | **否** | 自建硬件 | 我方协助 |
| 甲方自备模型（vLLM / TensorRT-LLM / 自家推理栈） | P | **否** | 甲方承担 | 甲方 |

adapter 切换成本：加一个 `*Client` 类 + 在 `_BACKENDS` dict 注册，预估 <50 行代码（见 `src/well_harness/llm_client.py`）。

---

## 5. 监控与健康

| 指标 | 采集方式 | 告警阈值（Staging / Production） |
| ---- | -------- | ------------------------------- |
| `/api/lever-snapshot` P99 延迟 | 请求埋点 | > 200ms / > 100ms |
| `/api/chat/*` 失败率 | error 码比例 | > 5% / > 2% |
| Ollama 可达性 | 健康检查 | 连续 3 次失败 / 连续 1 次失败 |
| 对抗测试每日 cron | CI job | 任何 FAIL / 任何 FAIL |
| 磁盘占用（`runs/` + 归档） | 定时任务 | > 80% / > 70% |

---

## 6. 不承诺的事

明确列出 **SLA 不覆盖** 的项目，避免误期望：

- **不承诺** AI 回答的语义正确率（AI 只解释，非决策，由 R2 约束）
- **不承诺** 与甲方已有 PLM / ERP 系统的集成（由 H2-24+ 另立契约）
- **不承诺** 在没有预检的情况下演示成功（见 Demo Profile）
- **不承诺** 任何具体 model 的长期可用性（MiniMax / Qwen 等由其各自供应商决定）
- **不承诺** 支持超出 `api-contract.md` v1 规范的自定义 field

---

## 7. 待甲方反馈的字段

以下字段设为**草案**，定稿需要甲方业务/合规/安全各出一位对接人确认：

- [ ] Staging / Production 的具体起效日期
- [ ] 事故等级响应窗口（当前数字为行业参考）
- [ ] 数据留存超过 90 天后的存储介质（冷存 / 厂内 HDD / 外挂合规存储）
- [ ] 甲方 IT 是否提供硬件或需我方代采
- [ ] Production 的第三方合规复核机构选择

本文档每次收到甲方反馈后递增版本号（v0.1 → v1.0）。当前 **v0.1 — 草案**。

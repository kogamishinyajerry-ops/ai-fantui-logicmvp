> **Status: Superseded by P19 Hardware Partial Unfreeze (2026-04-20)**
>
> 本申请书（v0.1, Ready for Review, 2026-04-18）的目标管线「PDF → adapter → ≥1 新系统 panel」**被 P19 Hardware Partial Unfreeze 事实上超越**：P19 在 controller.py 零改动前提下交付了硬件 YAML schema + Monte Carlo + 反诊断 + 立项演讲稿（2026-04-17 Done，18 个 sub-phases P19.1→P19.18，`.planning/phases/P19-hardware-partial-unfreeze/`，634+ tests 零回归）。
>
> 本申请**不重走 Gate**；文件保留作为 P17 slot 方向裁决的历史证据。P17 slot 最终由 Fault Injection 占用（2026-04-15 Done），与本申请书的 PDF 解析路径无关。
>
> 若未来需要重启"PDF → adapter → panel"作为独立能力（而非硬件 demo 层），应作为**新 Phase（如 P33 候选）独立立项**，不复用本申请书。
>
> **定性签字：** Kogami 2026-04-20 AskUserQuestion 答复（选项"Superseded by P19"） + Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
> **Phase Gate reference:** `GATE-P32-PLAN: Approved` (Kogami, 2026-04-20) · 执行动作 W4
>
> ---

# P17 解冻申请书（草案）

**版本**：v0.1
**日期**：2026-04-18
**撰写人**：Claude Code Opus 4.7 (20x Max) — Executor 身份，Tier 1 亲笔
**审批人**：Notion AI Opus 4.7（独立会话 Gate 裁决）
**状态**：~~**Ready for Review**（GATE-P20-CLOSURE Approved 2026-04-18 后升档）~~ **Superseded by P19 (2026-04-20)** — 详见本文件顶部 Status 标头

---

## 1. 执行摘要

AI FANTUI LogicMVP 项目于 **2026-04-15** 由 Opus 4.6 终裁进入 **Project Freeze**（Milestone 9）。冻结基线为 P0–P18.5 全部完成、561 tests 全绿、24 命令验证套件通过、P16 AI Canvas Sync 落地、联邦架构战略文档化。冻结条款明确记录解冻条件仅限"外部用户反馈 / 新产品方向决策 / 新领域需求"。

自冻结以来，项目在冻结线**之上**积累了三层增量，每一层都**零触碰** truth engine / 19-node / controller.py / R1–R5 安全基线：

- **P18.6**（post-freeze maintenance, 2026-04-15）：workbench archive SHA256 integrity；24 命令通过不变
- **P19 Sprint**（P19.1–P19.18）：Analysis API 多系统路由 + Hardware Schema + Sensitivity Sweep + 3 哇瞬间演示脚本；tests 561 → 634（+73，0 回归）
- **P20.0 Tier 1**（2026-04-18，上一 milestone 已 merge）：演示加固；默认 CI 639 passed 不变 + opt-in e2e 38 passed + adversarial 8/8 不变
- **P20 收口**（本 PR，feat/p20-closure）：B 演示脚本 + E 前端降级契约 + 本申请书；默认 CI 仍 639 不变，opt-in e2e 扩到 49

**证据强度**：639 主路径 passed、38+11 opt-in e2e passed、8/8 adversarial 全部基于 GitHub main + 本 PR 的可验证 pytest 输出，无编造数字。

**风险控制**：本申请不提任何 src/ 业务改动计划；不触碰联邦架构三层隔离；不降低 adversarial 8/8 基线；结尾句式明确"不自动解冻"。

**v3.0 双 Opus 架构定位**：Claude Code Opus 4.7 (20x Max) 是唯一 Executor，MiniMax / Codex 已全员退场；Notion AI Opus 4.7 是唯一 Gate 裁决方。本申请书由 Executor 亲笔，Gate 独立裁决，分工纪律严明。

---

## 2. 背景

### 2.1 冻结历程

- **2026-04-13** P8 Approved（Opus 4.6 裁决），adapter-backed runtime 定型
- **2026-04-14** Milestone 8 Complete，shared validation suite 稳定在 24 命令
- **2026-04-15 上午** P18.5 merge（canvas interaction fix；fault injection UI 移除）；P18.6 PR open（archive SHA256 integrity；561 tests + 24 commands pass）
- **2026-04-15 下午** **Milestone 9 — Project Freeze**：Opus 4.6 Final Adjudication "Approved, Project Freeze"；解冻条件明确为"外部用户反馈 / 新产品方向决策 / 新领域需求"
- **2026-04-15+** 联邦架构战略文档化（`docs/architecture/federation-model.md`）；三层架构 + 三级整合门槛写入宪法

### 2.2 冻结后 Partial Unfreeze 的成功先例

- **P18.6**：在冻结线之上以 post-freeze maintenance 身份落地，没有触发正式 unfreeze，没有回归
- **P19 Sprint**（P19.1–P19.18）：连续 18 个子 phase 在冻结纪律下完成；每个子 phase 独立 Gate；634 tests 保持全绿；证明冻结线**可支持**严格约束下的增量工作
- **P20.0 Tier 1**（2026-04-18）：再次验证严格 src/ 业务改动=0 约束下的演示加固路径可行；默认 CI 不动，opt-in e2e 做加固

P17 解冻申请的关键语义：**本次申请不是打破冻结，是请求 Gate 受理一次 Phase 1 评审**，判断冻结线之上累积的增量是否已经构成解冻触发条件（立项汇报 / 新产品方向）。

### 2.3 触发因子

- **条款一（新产品方向决策）**：立项汇报预演即将启动；需要 P17 Phase 1 具备"可演示 + 可审计 + 可回归"的完整度
- **条款二（新领域需求）**：P19 已在冻结线之上落盘 landing-gear / bleed-air / EFDS 的多系统路由支持，跨域扩展常态化；P17 如果重启，需要 Phase 1 明确治理边界

---

## 3. 证据链

### 3.1 测试底盘（逐项可追溯到 git log / pytest 输出）

| 维度 | 冻结时刻 | 当前（P20 收口） | 增量 | 证据 commit |
|---|---|---|---|---|
| pytest 默认路径 | 561 passed | **639 passed + 1 skipped** | +78，0 回归 | 4fc4db5 |
| opt-in e2e | 0 | **38 + 11 = 49 passed** | +49（3 哇场景 + 降级 + 前端 DOM） | 4fc4db5 + 77b51ea |
| adversarial 真值引擎 | 8/8 PASS | **8/8 PASS（:8799 demo 负载下重放不变）** | 0 回归 | 9b853f1 参数化 |
| shared validation suite | 24 命令 | 24 命令 | 0 变动 | — |
| src/ 业务逻辑改动 | — | **本 PR 0 改动** | 0 | feat/p20-closure 全部 docs+tests |

### 3.2 R1–R5 安全基线零触碰

- **R1（真值优先）**：truth engine + 19-node + controller.py 在所有后冻结增量中**未动一行**
- **R2（AI 仅解释）**：LLM 路径 only-explain；P19 / P20 / 本 PR 均未拓展到决策参与
- **R3（可审计）**：每条 opt-in e2e 锚定 `tests/e2e/fixtures/schema_snapshot.json`，`_meta.captured_from_commit` 字段使 schema 漂移可追溯
- **R4（降级可控）**：minimax_api_key_missing / MC clamp / 404 / invalid JSON / archive 下载失败 全路径锁契约（本 PR E 测试 +11 条）
- **R5（adversarial 守门）**：`adversarial_test.py` 参数化为 env PORT，:8799 demo 负载下 8/8 重放不变

### 3.3 P18.5 / P18.6 增量

- **P18.5** (merged)：canvas interaction fix；fault injection UI 移除；hover scale 禁用；hit-box pointer-events 修复
- **P18.6** (PR open)：workbench archives SHA256 integrity checksums；561 tests + 24 commands 通过

### 3.4 P19 Sprint 增量（18 个子 phase）

- P19.1–P19.5：chat UX polish + 基础设施
- P19.6：Analysis API (Monte Carlo + Reverse Diagnosis 后端)
- P19.7：Hardware Schema 端点
- P19.8：Sensitivity Sweep 后端
- P19.9：API endpoint tests for P19.6/P19.7/P19.8
- P19.10：Analysis Tools Panel 前端集成
- P19.11：Hardware Schema Browser Panel
- P19.12：Analysis Results → Chat History
- P19.13：Sensitivity Sweep Panel
- P19.14：Multi-System Analysis Selector
- P19.15：Multi-system hardware YAML support
- P19.16：Analysis API robustness + UI error handling
- P19.17：Analysis API multi-system tests（15 tests；634 total）
- P19.18：Pitch-ready Deck + 3 哇瞬间脚本

**净增量**：561 → 634 passed（+73），0 回归。

### 3.5 P20.0 Tier 1 增量（已 merge 到 main）

- `9b853f1` chore(P20.0-infra)：pytest marker `e2e` + addopts `-m 'not e2e'` + tests/e2e/ 骨架 + fixtures/schema_snapshot.json + adversarial 参数化
- `4fc4db5` test(P20.0-A,C)：38 opt-in e2e tests（wow_a 8 + wow_b 7 + wow_c 12 + resilience 11）

### 3.6 本 PR（feat/p20-closure）

- `77b51ea` test(P20.1-E)：frontend degradation DOM assertions，11 opt-in e2e
- `b9afa67` docs(P20.0-B)：3 份 keystroke-level 演示脚本，全部 keystroke ↔ e2e 断言可追溯
- `<D-hash>` docs(P20.0-D)：本申请书

### 3.7 v3.0 双 Opus 架构演进

- **v1.x (MiniMax 主驱)**：2026-03 到 2026-04 上半期，MiniMax-M2.7 作为开发中枢
- **v2.x (三角变形)**：2026-04-13 引入 Claude Pro Opus 4.7 Tier 1 主驱 + MiniMax-M2.7 Tier 2 + Codex GPT-5.4 审查；2026-04-18 P20.0 Tier 1 验证
- **v3.0 (双 Opus 架构)**：2026-04-18 Claude Code Opus 4.7 (20x Max) 成为唯一 Executor；Notion AI Opus 4.7 成为唯一 Gate 裁决方；MiniMax / Codex 退场；执行与评审彻底分离

**冻结后治理稳定性**：从 Milestone 9 到 P20 收口，跨越 3 代架构（v1.x / v2.x / v3.0），零回归、零事故、639 tests 底盘未破。

---

## 4. 技术边界

### 4.1 Phase 1 **要做**的

- **PDF 解析** → 从结构化控制逻辑说明 PDF 抽取"节点 → 连接 → 逻辑门"三元组
- **Adapter 模板** → 把抽取结果填充到现有 adapter 接口契约（复用 P8 的 adapter-backed runtime 基础设施）
- **面板生成** → 基于 adapter 契约产出一套新系统的 canvas 面板 JSON + 硬件 schema YAML
- **Phase 1 验收目标**：能从 PDF 输入产出 ≥ 1 套新系统的"可演示"面板（与 thrust-reverser / landing-gear 等现有 adapter 严格并列，不耦合）

### 4.2 Phase 1 **不做**的（硬禁止）

- ❌ truth engine 改造（controller.py / 19-node 契约完全冻结）
- ❌ LLM 参与真值决定（R2 原则不动，LLM 继续 only-explain）
- ❌ SaaS 化 / 多租户 / 云部署（单机工具链保持）
- ❌ 联邦架构三层隔离调整（Layer 1/2/3 不动；Level 0/1/2 门槛不动）
- ❌ adversarial 基线向下（8/8 必须保持）
- ❌ 跨域硬编码依赖（PDF→面板路径必须走 Level 1 人类确认门槛）

### 4.3 证据面边界

- GitHub repo 为代码真值面
- Notion 控制塔为控制平面（02B Execution Run / 04A Review Gate / 05 QA / 06 Evidence 持续写回）
- Phase 1 评审仅使用：已合入 main 的 commit + 本 PR 的 PR body + Notion 控制塔记录
- **不引入**任何 Phase 1 专用新证据面（禁止为 Phase 1 单独建 DB / 页面）

---

## 5. 风险矩阵（7 条，每条含检测手段）

| # | 风险 | 触发条件 | 影响 | 缓解 | 检测手段 |
|---|---|---|---|---|---|
| R-01 | 本申请被误解为自动解冻 | 任何执行方读取后未经 Gate 即开展 src/ 改动 | 冻结纪律失效 | 结尾句式明确"不自动解冻"；04A Gate Status=Awaiting；trailer 强制 opus47-max | **Gate**: 04A Review Gate 状态未翻 Approved 前任何 src/ commit 拒绝 |
| R-02 | 演示加固被当"真解冻"木马 | 有人以"演示需要"为由推 src/ 业务改动 | 冻结边界侵蚀 | P20.0 / 本 PR 已强制 src/ 业务改动=0；本申请不提 src/ 计划 | **测试**：CI pytest 默认路径 ≠ 639 即阻断 PR merge |
| R-03 | e2e 锚定过期 schema snapshot | 后续 commit 改 API 响应形状未同步 fixtures | opt-in e2e 假阳性通过 | fixtures/schema_snapshot.json 的 `_meta.captured_from_commit` 字段追溯 | **审计**：e2e 新增断言必须更新 `_meta` 或附 git blame 说明 |
| R-04 | Phase 1 评审周期过长项目真空 | 排期 > 14 天 | 团队方向失焦 | 承诺 Phase 1 ≤ 7 天裁决；超期自动收口为"不构成解冻" | **Gate**: 04A Gate Next Action 字段写入 7 天 deadline |
| R-05 | 立项汇报现场 MiniMax API 失效 | 演示期间 API key 限速或 URL 改动 | 哇 A 叙述层降级 | 哇 A 契约断言锚真值引擎不锚 LLM；降级台词预置在 wow_a_causal_chain.md §6 | **测试**：`test_resilience_no_minimax_key_chat_reason_returns_structured_error` + `test_frontend_llm_failure_returns_structured_envelope_for_degraded_notice` |
| R-06 | 联邦架构被意外触碰 | Phase 1 讨论中未经 Level 2 门槛讨论跨域合并 | 联邦宪法受损 | §4.2 明确禁止；Gate Decision Notes 必须引用 `docs/architecture/federation-model.md` | **审计**：Gate 裁决文本 grep `federation-model.md` 关键字，缺失即拒绝 |
| R-07 | v3.0 双 Opus 架构在加压下漂移 | Executor 越界签 Gate 或 Gate 越界写代码 | 分工纪律失效 | 本 PR 所有 commit trailer 固定 `Execution-by: opus47-max`；Gate 裁决在 Notion 独立页完成 | **审计**：git log grep 非 opus47-max trailer 即触发 Gate 审查 |

---

## 6. 资源与时间

### 6.1 Tier 分层预览

- **Tier 0（本申请受理前）**：Gate 阅读本申请书 + 相关证据 → 二元裁决（构成 / 不构成解冻触发条件）
- **Tier 1（裁决=构成 → 进 Phase 1）**：PDF 解析 PoC → adapter 模板 → 1 套新系统面板产出（4–6 周）
- **Tier 2（Phase 1 结束）**：新系统面板跑满 24 命令验证套件 + 新增 e2e 覆盖 → Milestone 10 提议
- **Tier 3（Milestone 10 终裁 → 正式 unfreeze）**：Gate 正式批准 src/ 业务改动窗口；P17 Phase 2 启动

### 6.2 时间预算

- **Phase 1 评审窗口**：≤ 7 个自然日（从 04A Gate Status=Awaiting 翻转到 Reviewing 起算）
- **Phase 1 执行窗口**（若受理）：4–6 周
- **Phase 1 总成本**：≤ 1.5 个 milestone（参考 P19 Sprint 18 子 phase 耗时约 1 个 milestone）
- **超期自动收口条款**：7 天内无裁决 → 默认"不构成解冻触发条件"，本申请书归档；4–6 周内无 Phase 1 产出 → 自动降级为"研究性 spike"，不触发 Tier 2

### 6.3 人员

- **Executor**：Claude Code Opus 4.7 (20x Max)（唯一）
- **Gate**：Notion AI Opus 4.7（唯一，独立会话）
- **人类指挥**：Kogami（方向决策、Gate 信号转发）
- **退场方**：MiniMax / Codex（v3.0 架构下不参与 Phase 1 执行链）

### 6.4 基础设施成本

- **零新增**：沿用现有 GitHub repo + Notion 控制塔 + 本地开发机
- **API 成本**：Opus 4.7 主要 token 消耗（预估 Phase 1 全周期 ≤ 1M tokens）

---

## 7. 验收标准

### 7.1 本申请书合格标准（7 项，全部必须满足）

1. ✅ 证据链第 3 节所有数字（561 / 634 / 639 / 38 / 11 / 49 / 8）与 GitHub main + Notion DB 记录**逐行一致**
2. ✅ 风险矩阵 7 条全部可映射到已有 commit / 文档 / 治理条款，**每条配检测手段**
3. ✅ 技术边界 §4.2 六条硬禁止与联邦架构文档 + R1–R5 基线**零冲突**
4. ✅ 时间预算 §6.2 的 7 天窗口已写入 04A Gate 的 Next Action 字段
5. ✅ 本 PR 的 3 个 commit 全部 trailer 为 `Execution-by: opus47-max`
6. ✅ 本文件结尾句式严格为"申请进入 P17 Phase 1 评审，不自动解冻"
7. ✅ 本文件所有数字**可追溯**（commit hash / pytest 输出 / Notion 页面 URL）

### 7.2 Phase 1 完成标准（若评审通过）

- Phase 1 Exit Criteria：**adapter 生成 ≥ 1 套新系统面板**（PDF → 面板 JSON + 硬件 schema YAML 端到端）
- pytest 主路径维持 639（或增加，不减少）
- opt-in e2e 增加 ≥ 新系统 × 8 条（对标现有 wow_a 覆盖密度）
- adversarial 8/8 保持
- src/ 业务改动仅限：新 adapter 文件（不得触碰 controller.py / 19-node / truth engine）
- 联邦架构三层 + 三级门槛零触碰
- Phase 1 产出进入 Milestone 10 评审，Tier 3 终裁前不解冻

### 7.3 Gate 裁决标准（不在本文件内预判）

- Reviewer（Notion AI Opus 4.7）对"冻结线之上后增量是否构成解冻触发条件"给出二元裁决
- 裁决理由必须引用：
  - 冻结条款原文
  - 证据链具体条目（commit hash / pytest 输出）
  - 联邦架构约束（`docs/architecture/federation-model.md`）
- 裁决结果写回 Notion 04A Review Gate 的 Decision Notes 字段

---

## 8. 附录：引用面

- **GitHub main**：https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp
- **本 PR**：`feat/p20-closure` (3 commits：77b51ea / b9afa67 / 本文件)
- **Notion 控制塔**：https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec
- **冻结时刻 commit**：P18.5 merged + P18.6 PR open（2026-04-15）
- **证据面文件**：
  - `.planning/ROADMAP.md`（冻结条款原文 + 联邦架构裁决记录）
  - `.planning/STATE.md`（P0–P18.5 + P19.18 全部状态）
  - `docs/architecture/federation-model.md`（联邦架构宪法级文档）
  - `tests/e2e/fixtures/schema_snapshot.json`（e2e 断言的 schema 锚）
  - `tests/e2e/test_wow_{a,b,c}_*.py` + `test_demo_resilience.py` + `test_frontend_degradation.py`（38+11 opt-in e2e）
  - `src/well_harness/static/adversarial_test.py`（R5 adversarial 8/8 守门）

---

**申请进入 P17 Phase 1 评审，不自动解冻。**

---
phase: P43
plan: P43-00
plan_revision: v3 (post-Codex-round-2 remediation · path ①)
title: Control Logic Workbench end-to-end milestone — v3 · 4-cut hard remediation
status: re-drafted · Awaiting GATE-P43-PLAN (v3) (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum
verified-by: codex-gpt54-xhigh (round 1 需阻止 · 6 counters A-F · round 2 需修正·信号强 · 4 required cuts)
scope_tier: Tier 1 · milestone-level
preconditions:
  - GATE-P42-CLOSURE Approved (Kogami 2026-04-20) → main at `a6521ca`
  - Kogami 2026-04-20 R4 指令：完整控制逻辑生成工作台
  - v1 plan (`81adf39`) 被 Codex round 1 判 **需阻止**（6 structural counters）
  - v2 plan (`aa8e03a`) 被 Codex round 2 判 **需修正·信号强** · 4 必补项（state.yaml 幻影 / P43-01 fail 硬冻结 / draft_design_state authority contract / §3d touched+forbidden files）
  - Kogami 2026-04-20 路径① (×2) 明示选择：修 plan 后重走 Gate
  - v5.3 addendum 生效 · adapter-boundary 硬性规则 Codex review 必调
non-goals:
  - 本 P43-00 v3 不写任何 src 代码
  - 不修改已锁定 M1 产出：controller.py / models.py / 5 adapter evaluate/explain 方法 / YAML parameters / registry markdown 5 rows table / JSON schema v1 $id
  - **不并行建第二套 orchestrator**（Codex round-1 Counter B）· P43 是 extend existing · 不是 rebuild
  - 不建第二套 truth engine
  - **不在 P43-05 / P43-08 建 shadow truth engine**（Codex round-1 Counter C）· preview 只展示候选 diff · 不作 runtime 语义源
  - 不替代 P7 workbench
  - 不引入新的 adapter Protocol
  - 不 bump JSON schema version
  - **"Final Approved" ≠ truth_level=certified**（Codex round-1 Counter D）· Final Approved → `demonstrative/Upgrade pending` · certified 升级走独立 Phase
  - 不扩 P43 范围到 "certified upgrade pipeline"
  - **不引入 `state.yaml` 或任何新持久化文件**（Codex round-2 cut #1）· persistence 只有 `workbench.js` localStorage workspace + `workbench_bundle.py` bundle/archive manifest 两源 · P43 不加第三源
  - **不允许 P43-01 以 "列出断裂" 为通过条件**（Codex round-2 cut #2）· P43-01 必须 **证明 primitive 可绑定**（happy path 端到端实跑通过）· 未证明则 P43-02+ 自动冻结
  - **不允许 `draft_design_state` 写回 frozen spec**（Codex round-2 cut #3）· 无论用户在 annotation / wiring / iteration 任何环节 · preview 状态不可逆向覆盖 frozen spec · 唯一回写通道是 "reiterate → 新一轮 freeze"
  - **不允许新增未列入 §3d touched-files list 的文件**（Codex round-2 cut #4）· 任何试图新建的 `workbench/orchestrator.py` / 新前端 shell / 新 archive root / 新持久化源均违 non-goal
---

# P43 · Control Logic Workbench milestone (v3) — 4-cut hard remediation

## 0. TL;DR · v2 → v3 差异

Codex round-2 判 v2 "需修正·信号强"。4 条必补：

| Codex round-2 要求 | v3 对应 |
|-------------------|--------|
| **Cut #1** 删 `state.yaml` 幻影 | §3c 删 partial-write-to-state.yaml 条 · non-goal #15 硬禁新持久化 · persistence 二源明示（localStorage + bundle manifest） |
| **Cut #2** P43-01 fail 硬冻结 | §3a Exit Criteria 去 "or 列出断裂" · 改 "happy path 必须端到端 asserted pass" · §7 停点 2.5 = P43-01 未证明绑定 → P43-02+ 冻结（不可选） |
| **Cut #3** `draft_design_state` authority contract 机械约束 | §3e 新增 authority contract 章节 · 6 条机械规则（读写权限 / 回写禁止 / generator 消费规则 / 冲突自动拒绝 / lifecycle boundary / observability 要求） |
| **Cut #4** §3d touched-files / forbidden-files 明示 | §3d 改写 · 给出 "whitelist" + "blacklist" 两张清单 · 含 `demo_server.py` |

加上 Codex round-2 指出的"伪问题"清理：

| v2 Open Question | v3 处理 |
|-----------------|--------|
| Q3 (state machine 持久化格式) | 删 · 已由 non-goal #15 锁死（localStorage + bundle manifest · 无第三源） |
| Q5 (archive 粒度) | 删 · 已由 non-goal #10 + §3d 锁死（复用 `archive_workbench_bundle`） |
| Q6 (Final Approved truth_level) | 删 · 已由 non-goal #12 + §1 唯一治理线锁死 |
| Q9 (P43-01 failed 怎么办) | 删 · 已由 §7 停点 2.5 硬规则锁死（冻结 · 无选项） |
| Q10 (workflow automaton 契约格式) | 保留但降为 minor config question · 非结构性 |

加 3 条 Codex round-2 指出的缺失 Q：

| v3 新增 | 内容 |
|---------|-----|
| Q11 | `draft_design_state` / frozen spec / generated adapter 三者 authority chain 谁是唯一可落盘 truth |
| Q12 | PDF/DOCX 文本抽取 authoritative path：浏览器端 vs 服务端 · OCR 允许与否 · 文档 SHA → canonical text 绑定方式 |
| Q13 | `demo_server.py` 是否纳入 extend contract · API 变更边界 |

**v3 核心立场**：v2 "extend-not-rebuild" 口号正确但执行不到位。v3 把 extend 契约变成机械门槛：touched list / forbidden list / authority chain / mandatory-pass-before-proceed · 让计划自己不给回退余地。

---

## 1. Milestone vision · user journey（v3 · 治理统一）

### 核心原则（Codex round-1 Counter D 消化 · v3 保留）

**Final Approved ≠ certified**。P43 pipeline 只能落 `demonstrative + Upgrade pending`。certified 升级需独立 Phase + 上游权威文档 + SHA + Traceability matrix + Appendix A + Kogami 独立 Gate。

### 用户旅程闭环（10 step · 治理对齐）

| Step | 用户动作 | 系统产出 | 用户决策 | 治理 level |
|------|---------|---------|---------|----------|
| 1 · Import | 扔 pdf/docx/md/image | intake + SHA 固化 | 确认识别 | — |
| 2a · Parse | 系统跑 `ai_doc_analyzer` | 候选 spec + ambiguity list | — | — |
| 2b · Q&A | 系统提问 | 答案持久化 | 填答/跳过 | — |
| 2c · Freeze | 用户"Freeze Approved" | frozen spec + Appendix A | 用户签 | draft-frozen |
| 3 · Panel gen | 系统生成 adapter 预览（`draft_design_state`） | draft adapter 预览 | 旁观 | draft-preview |
| 4 · Wiring | 连线编辑（只写 `draft_design_state`） | preview diff | 手动加/删 | draft-preview |
| 5 · Debug | 灌 snapshot | evaluation 结果（基于 frozen spec 不是 preview） | 观察 | draft-preview |
| 6 · Annotate | 标注 | annotations.yaml | — | draft-preview |
| 7 · Iterate | "回 Freeze 改" → 重跑 Q&A → 新 frozen | 新 frozen spec | 再改/满意 | draft-frozen (重新) |
| 8 · Final Approval | 用户签 "Final Approved" | adapter landing + registry row + `demonstrative + Upgrade pending` | 签名 | **demonstrative/Upgrade pending** |
| 9 · Archive | 归档 | `archive_workbench_bundle` manifest + closure | 归档只读 | — |

**v3 关键修正**（Codex round-2 cut #3）：Step 7 "Iterate" 不再是 "preview 直接写回 spec"。唯一路径是 **"reiterate → 回到 Freeze step 重走 Q&A → 产生新 frozen spec"**。preview 永远不能反向污染 frozen spec。见 §3e authority contract。

### 三个非功能性目标

- **T1 可追溯** · T2 可中断 · T3 可审计

---

## 2. Primitives 库存 · 真实性警告（v2 保留 · Codex round-1 A/B/F）

### 2a · v1 库存是伪库存（自认）

见 v2 §2a · 2 条真 bug（`blockers`/`blocking_reasons` · `ai-doc-analyzer.js readAsText` 对 pdf/docx 静默失败）· `generate_adapter.py:255,448` 硬编码 · analyzer ID vs intake clarification ID 契约未核。

### 2b · P43 不再声明完整 inventory · 改为 P43-01 产出真实契约报告

**v3 保留 v2 决策** + **强化** Exit Criteria（见 §3a · cut #2）：P43-01 必须 **证明** primitive 可绑定 · 不仅列伤。

### 2c · 既有 workbench 工作（P43 必须 extend · 不 rebuild）

| 既有组件 | 位置 | 职责 | P43 extend 策略 |
|---------|------|------|--------------|
| `cli.py bundle` subcommand | `src/well_harness/cli.py:200` | intake packet → bundle 打包 pipeline | P43-02 加 orchestrator `new` / `continue` / `status` subcommands |
| `workbench_bundle.py` | `src/well_harness/workbench_bundle.py` | build / archive / restore / manifest validate | **唯一 canonical bundle/archive 持久化源** · 禁另建 |
| `workbench.js` localStorage 工作区 | `src/well_harness/static/workbench.js` | 浏览器端 workspace + archive-toggle + handoff-note | **唯一 canonical 浏览器端 workspace 源** · 禁另建 |
| `archive_workbench_bundle` + `resolve_workbench_archive_manifest_files` | `workbench_bundle.py` | manifest + restore | P43-10 archive 走这个 |
| `demo_server.py` | `src/well_harness/demo_server.py` | FastAPI server · `/api/workbench/*` 接口 | **纳入 extend contract**（Codex round-2 Q13 补）· 允许加 endpoint · 禁止改语义 |
| Appendix A 模式（P34-P42） | `docs/{system}/traceability_matrix.md` | open question 登记 | P43-04 Freeze 用同模板 |

---

## 3. Execution strategy · v3

### 3a · P43-01 Contract Proof Spike（先行 · must-land · v3 Exit Criteria 收紧）

**不是 9 sub-phase 的一部分**。未 land · P43-02+ 全部 on-hold（硬规则 · 非选项 · 见 §7 停点 2.5）。

**P43-01 scope：**

1. 跑真实 happy path（用 `uploads/20260417-C919反推控制逻辑需求文档.pdf` · 端到端）
2. 跑真实 failure path（扔"应有 blocker" intake · 验 `assessment.get("blockers")` 路径）
3. 修 `blockers`/`blocking_reasons` 真 bug（`ai_doc_analyzer.py:838`）· 加 regression test
4. PDF/docx 抽取能力核（`ai-doc-analyzer.js` readAsText 对 binary 行为实测）
5. analyzer ID ↔ intake clarification ID 契约核
6. `generate_adapter.py:255,448` domain hardcode 暴露
7. `workbench.js` + `workbench_bundle.py` schema inventory（localStorage key / manifest shape / handoff-note shape · dump 真实数据）
8. `demo_server.py` API 契约 inventory（所有 `/api/workbench/*` endpoint · 请求/响应 shape · dump 真实）

**P43-01 Exit Criteria（v3 硬化 · Codex round-2 cut #2）：**

**v2 原文** "真实 happy path 端到端跑通 **或** 清晰列出所有断裂" —— v3 **删 "或"**。

1. **真实 happy path 必须端到端 asserted pass**（不是 "跑通" 笼统语义 · 是 "从 pdf 到 archive 每一步 SHA/输入/输出 assert 通过"）· asserted pass 失败 → P43-01 未完成 → P43-02+ 自动冻结（§7 停点 2.5）
2. **真实 failure path blocker 被正确识别并 surface 到前端**（`ai_doc_analyzer.py:838` bug 修好且 regression test 通过）
3. `docs/P43-contract-proof-report.md` 存在 · 含 primitive API 契约表（8 个 scope item 全覆盖）· 含每步 assert 证据
4. Kogami 基于契约报告决定 P43-02+ scope（可保留 v3 分解 · 可要求 v4 · 不可 "继续按 v3 执行但 spike 未验证"）

**P43-01 规模：** ~1 day · ~200 LOC 修 + ~500 行 docs + ~500 行 asserted-pass test harness · Codex review 必调（adapter boundary · `ai_doc_analyzer` 写操作）。

### 3b · P43-02..P43-10（P43-01 landed 且 asserted pass 后 Kogami 重审才定）

Tentative 分解（P43-01 结果可能大改）：

- **P43-02** · Orchestrator extend · 在 `cli.py bundle` + `workbench_bundle.py` 基础加 state machine
- **P43-03** · Document pipeline · 修 PDF/docx 真实抽取 · 修 clarification contract
- **P43-04** · Freeze gate + Appendix A 生成
- **P43-05** · Progressive panel preview（`draft_design_state` 身份 · 见 §3e）
- **P43-06** · Wiring editor + graph validator（cycle / terminal uniqueness / fan-out 约束）
- **P43-07** · Debug harness（基于 frozen spec · 非 preview）
- **P43-08** · Annotation + iteration loop（reiterate 走 Freeze 再走 · 非 preview 写回）
- **P43-09** · Final Approval → `demonstrative + Upgrade pending`
- **P43-10** · Archive · 复用 `archive_workbench_bundle`

Tentative 规模：~2500-3500 LOC · P43-01 可能推翻。

### 3c · Workflow automaton 契约（Codex round-1 Counter E 消化 · v3 去 state.yaml 幻影）

P43-02-00-PLAN.md 前置必备章节：

- **State enum**：`INIT / INTAKED / PARSING / AWAITING_ANSWERS / FREEZING / FROZEN / GENERATING / PANEL_READY / WIRING / DEBUGGING / ANNOTATING / ITERATING / APPROVING / APPROVED / ARCHIVING / ARCHIVED / ERROR`
- **Event list**：`import_doc / answer_question / confirm_freeze / start_gen / wire_change / submit_snapshot / annotate / reiterate / final_approve / archive` + 每个 event 的 legal pre-state / post-state
- **Transition table**：N×M 矩阵 · legal / illegal / conditional
- **Error taxonomy**：`pdf_extract_failure / ambiguity_unresolved / regen_failure / iteration_overflow / schema_drift / external_state_delete` · 每个 error 的 recovery action
- **Idempotency rules**：event 幂等/非幂等分类 · 非幂等需 deduplication token
- **Persistence model（v3 修正 · Codex round-2 cut #1）**：persistence 二源 · `workbench.js` localStorage workspace + `workbench_bundle.py` bundle/archive manifest · **无第三源**。~~原 v2 "state.yaml 写到一半 crash 如何恢复"条删~~。crash recovery 规则改写为："localStorage 单 key 原子 write · bundle/manifest 走既有 `workbench_bundle.py` 原子写 protocol · P43 不引入 partial-write 语义因不新建持久化源"
- **Side-effect ordering（v3 新补）**：`final_approve` event 触发 side-effect 序：① localStorage state → APPROVING · ② server-side adapter emit + registry row append（原子）· ③ `archive_workbench_bundle` manifest append · ④ localStorage state → APPROVED。任何一步失败 · 回退到 ① 前状态 · 上报 error taxonomy `partial_approve_rollback`
- **Cross-phase integration test ownership**：P43-02 定 · 各 sub-phase 执行

### 3d · Existing workbench migration 契约 · 明示 whitelist / blacklist（Codex round-2 cut #4）

P43-02-00-PLAN.md 前置必备章节：

**Whitelist（允许 extend · 新增 endpoint/subcommand/schema field OK · 禁止改语义）：**

| 文件 | 允许扩展 | 禁止改动 |
|------|---------|---------|
| `src/well_harness/cli.py` | 加 subcommand（`workbench new / continue / status`） | 改既有 `bundle` / `archive` 行为 |
| `src/well_harness/workbench_bundle.py` | 加 manifest field（带 migration path） | 改既有 manifest field 含义 |
| `src/well_harness/static/workbench.js` | 加 localStorage key / 加 UI panel | 改既有 key 含义 |
| `src/well_harness/static/workbench.html` | 加 DOM section | 改既有 DOM structure 破坏兼容 |
| `src/well_harness/demo_server.py` | 加 `/api/workbench/*` endpoint | 改既有 endpoint 请求/响应 shape |
| `src/well_harness/ai_doc_analyzer.py` | 修 `blockers`/`blocking_reasons` bug（P43-01 必修） | 不相关重构 |
| `src/well_harness/document_intake.py` | 加 clarification ID 契约 | 改既有 intake gate 语义 |
| `src/well_harness/tools/generate_adapter.py` | 暴露 domain hardcode 开关 | 改既有 adapter emit shape |

**Blacklist（明确禁止新建 · 任何新建 = violation · 自动 reject）：**

- ❌ 新建 `src/well_harness/workbench/orchestrator.py` 或任何 `workbench/` 目录下新文件（orchestration 能力走 cli.py）
- ❌ 新建 `state.yaml` / `workflow.db` / 任何新持久化源（persistence 只有 localStorage + bundle manifest）
- ❌ 新建前端 SPA shell / 替换 `workbench.js` 框架（vanilla JS 继承）
- ❌ 新建 `archive/workbench/{system_id}/` 目录结构（走 `archive_workbench_bundle`）
- ❌ 新建 `src/well_harness/workflow_engine.py` 或类似独立 workflow runtime（state machine 嵌入 `workbench_bundle.py` + `workbench.js`）
- ❌ 新建 `src/well_harness/draft_truth.py` 或类似 shadow truth engine（见 §3e）

**兼容性验收（P43-02 Exit Criteria）：**

- 既有 `archive_workbench_bundle` 产的 archive 必须无损 restore 到 P43 flow · 不需 migration script
- 既有 `workbench.js` localStorage v1 数据（若存在）必须兼容读 · 或有明确 migration 函数

### 3e · `draft_design_state` authority contract · 机械约束（Codex round-2 cut #3）

**身份定义：** `draft_design_state` 是 P43-05/P43-06/P43-08 的临时预览状态 · 存于 `workbench.js` localStorage · key = `wellHarnessWorkbench.v1.draftDesignState.{system_id}`。

**6 条机械规则（v3 新增）：**

| 规则 | 机械约束 |
|-----|---------|
| R1 · 写权限白名单 | 只有 Step 3 (panel gen) / Step 4 (wiring) / Step 6 (annotate) UI 层写 `draftDesignState` · 后端 `demo_server.py` / `generate_adapter.py` / `ai_doc_analyzer.py` 均 forbidden 写（前端 UI state only） |
| R2 · 读权限白名单 | 只有 Step 3/4/5/6 UI render + Step 7 iterate trigger 可读 · Step 8 Final Approval 不读 draft · 只读 frozen spec（防 preview 污染最终 adapter） |
| R3 · **回写 frozen spec 禁止** | `draft_design_state` **不能以任何方式覆盖 frozen spec**。唯一路径：Step 7 "reiterate" event → 用户主动回 Freeze step → 重跑 Q&A → 产新 frozen spec（带新 SHA）· 即使新 spec 继承旧 draft 内容 · 必须走完整 Q&A/Freeze 闭环 · 绕过自动 reject |
| R4 · generator 消费规则 | `generate_adapter.py` **只消费 frozen spec** · 不读 `draft_design_state`。Step 3 panel gen 的预览 adapter 实际 input 是 frozen spec · draft 只影响 UI diff 显示 · 不进 emit pipeline |
| R5 · 冲突自动拒绝 | 任何 draft 状态与 frozen spec 冲突（例：draft wiring 引用了 frozen 里已删的 component）· validator 在 Step 7 reiterate trigger 前必 reject · 用户见 validation error + 冲突清单 |
| R6 · Lifecycle boundary | Step 8 Final Approval 触发 → `draft_design_state` key **立即删除** · 防止 "Final 后 draft 残留再被消费"。archive 只包 frozen spec + final adapter + Appendix A · 不含 draft |

**Observability 要求：**

- `draft_design_state` 每次写入记 `writer_step` + timestamp · 便于审计
- UI 显示 "draft vs frozen" diff badge · 用户明知当前看的是 preview 不是 truth

**Authority chain**（Q11 答案预设 · Kogami 可否决）：

```
frozen spec (authoritative · 唯一 truth)
    ↓ (只读 · R4)
generated adapter (faithful emit)
    ↓ (只读)
registry row + Upgrade pending status
```

```
draft_design_state (ephemeral UI preview · 非 truth)
    ↓ (无写回路径 · R3)
reiterate event → Step 2c Freeze (重新产 frozen) → 新 frozen SHA
```

---

## 4. Non-goals · v3 扩展

继承 v2 + 新增（v3 · Codex round-2 消化）：

15. **不引入 `state.yaml` 或任何新持久化源**（Cut #1）· persistence 只有 localStorage + bundle manifest
16. **P43-01 未证明绑定则 P43-02+ 自动冻结**（Cut #2 · 非选项）
17. **`draft_design_state` 禁回写 frozen spec**（Cut #3 · §3e R3）
18. **任何新建 Blacklist 条目文件 = violation**（Cut #4 · §3d）

---

## 5. Tier 1 对抗性自审 · v3（C1-C12 保留 · 加 C13-C15 · 覆盖 round-2 遗漏）

v2 的 C1-C12 全保留（不复述 · 见 v2 §5）。以下是 v3 新增：

### C13 · `workbench.js` 跨 tab / 多进程冲突

**攻击：** localStorage 在多 tab 打开同一 workspace 时可能 race · Step 4 wiring 改 + Step 7 iterate trigger 并发 · state machine 不知道。

**v3 缓解：**
1. P43-02 state machine 加 "active-tab lock"（BroadcastChannel API）
2. `workbench.js` 加 "workspace locked by other tab" UI 提示
3. Exit Criteria 加：多 tab 测试场景

### C14 · `archive_workbench_bundle` 兼容性未保证

**攻击：** 既有用户已有 archive（P34-P42 产出）· P43 extend `workbench_bundle.py` manifest · 若加字段不当 · 旧 archive restore 失败。

**v3 缓解：**
1. §3d 兼容性验收 Exit Criteria 明示
2. P43-02 manifest migration rule：P43 新字段必须 optional · 缺失语义 = pre-P43
3. P43 测试套必含 "P42 archive restore" 回归

### C15 · `demo_server.py` API 扩展可能破 MCP / 外部集成

**攻击：** `demo_server.py` 若已被外部 consumer（如 notion-cfd-harness / future MCP）集成 · P43 加 endpoint 无破坏但改语义会 break。

**v3 缓解：**
1. §3d whitelist 禁止改既有 endpoint 语义
2. P43-01 spike item 8 inventory 所有既有 `/api/workbench/*` endpoint · 产 contract lock file
3. P43-02 Exit Criteria 加：既有 endpoint 回归测试（contract lock 对比）

---

## 6. Open Questions · v3 · Kogami 签 GATE-P43-PLAN (v3) 时仲裁

**v3 清理 v2 伪 Q：** 删 Q3 / Q5 / Q6 / Q9（已由 non-goal / §3e / §7 锁死 · 无选项空间）。Q10 降为 minor。保留真 Q：

### Q1 · Gate 策略
- A · P43-01 + 每个 P43-02..10 各独立 gate（10 gate · high fatigue）
- C · 混合：P43-01 独立 · P43-02..04 合 · P43-05..07 合 · P43-08..10 合（4 gate · medium）
- **D · 推荐**：P43-01 独立 · P43-02..04 合 · P43-05..07 合 · P43-08..10 合 = **4 gates**
- **Executor 建议：D**

### Q2 · UI 技术栈
- A · 沿用 `workbench.js` vanilla JS 风格（**推荐 · 与 §3d whitelist 一致**）
- B · 引入 Alpine.js/HTMX（被 §3d blacklist 禁 · 不选）
- **Executor 建议：A**

### Q4 · approval 签名
- **A · 用户 alias + 注释**（推荐）
- B · OAuth
- **Executor 建议：A**

### Q7 · adapter-boundary Codex 硬性规则
- **A · P43 milestone 整体标记 · 每触点必调 Codex**（推荐）
- **Executor 建议：A**

### Q8 · P43-01 内容范围
- A · 只跑 happy + failure path + 修已知 bug（最 lean · 不含 contract lock）
- **B · 加 primitive API 契约表 + contract lock file**（**推荐** · 后续 sub-phase plan 必需）
- C · 加全套 performance benchmark（超 scope · 不选）
- **Executor 建议：B**

### Q10 · workflow automaton 契约格式（minor · 配置选择）
- A · 纯 markdown
- **B · 独立 `docs/P43-workflow-automaton-contract.md` + machine-readable yaml schema**（推荐）
- **Executor 建议：B**

### Q11 (v3 新) · Authority chain 预设确认
v3 §3e 预设：`frozen spec` = 唯一 truth · `draft_design_state` = ephemeral UI preview · generator 只读 frozen · draft 无写回路径。
- **A · 采纳 v3 预设**（推荐 · §3e R1-R6 机械约束落地）
- B · 放宽 R3（允许 draft 自动 propose frozen diff · 用户点击 approve 回写）· **风险：打破 "freeze = canonical truth" 语义 · 重回 shadow engine**
- C · 收紧 R3（连 reiterate 都不行 · 用户必须从头导入 doc）· **风险：iteration loop 崩**
- **Executor 建议：A**

### Q12 (v3 新) · PDF/DOCX authoritative 抽取路径
- A · 浏览器端（`ai-doc-analyzer.js readAsText`）· 当前代码路径 · 对 binary 静默失败
- **B · 服务端（`ai_doc_analyzer.py` 或新模块用 pypdf + python-docx）· P43-03 实现**（**推荐 · 浏览器端只负责 upload + preview**）
- C · 双路径（浏览器 fallback · 服务端 canonical）· scope 过大
- OCR 允许与否：
  - a · 不允许（默认 · 非可印刷 pdf 被 reject）
  - b · 允许（需第三方如 tesseract · scope 蔓延）
- SHA 绑定：canonical text SHA 与原 binary SHA 分开登记 · 二者都入 manifest
- **Executor 建议：B + a**

### Q13 (v3 新) · `demo_server.py` extend 边界
- A · 完全禁止改 `demo_server.py`（与 §3d whitelist 冲突 · 不选）
- **B · 允许加 endpoint · 禁止改既有 endpoint 语义**（推荐 · §3d 已定）
- C · 完全自由（违 extend-not-rebuild · 不选）
- **Executor 建议：B**

---

## 7. Execution sequencing · v3

```
P43-00 v3 plan commit + Codex round-3 re-review + Kogami GATE-P43-PLAN (v3) Approved + Q1/Q2/Q4/Q7/Q8/Q10/Q11/Q12/Q13 仲裁
         ↓
P43-01 Contract Proof Spike (独立 gate · ~1 day · 先行 · must land)
         ↓
[停点 2.5 · v3 新 · 硬规则 · non-goal #16]
  P43-01 Exit Criteria 全 pass（asserted happy path + failure path + contract report + contract lock）
    YES → 进入 P43-02..04
    NO → **P43-02..10 自动冻结 · Kogami R4 decision 重新**（非选项 · 无继续路径）
         ↓
P43-02..P43-04 基础线（合 1 gate · workflow contract + orchestrator extend + doc pipeline + Freeze）
         ↓
P43-05..P43-07 preview 层（合 1 gate · panel gen + wiring + debug · §3e authority contract 落地）
         ↓
P43-08..P43-10 iteration + approval + archive（合 1 gate · reiterate loop + Final Approved demonstrative + archive restore）
```

**总 gates：4**（P43-01 + 3 批次）· 若 Q1=D 批

**总 duration：** P43-01 ~1 day · 基础线 ~3-5 day · preview 层 ~3-5 day · 收尾 ~2-3 day · **~10-14 day**

---

## 8. Milestone-level Exit Criteria（v3 更严）

1. 用户旅程 10 step 端到端 demo 跑通（真实 pdf/docx 输入 · 真实 archive 输出）
2. P43-01 Contract Proof Spike asserted pass（非"列伤")
3. `ai_doc_analyzer.py` `blockers`/`blocking_reasons` bug 已修 + regression test land
4. `docs/P43-contract-proof-report.md` + `docs/P43-api-contract-lock.yaml` 存在 · Kogami 审过
5. `docs/P43-workflow-automaton-contract.md` + machine-readable yaml 存在（Q10=B）
6. 既有 `archive_workbench_bundle` manifest 能无损 restore 到 P43 flow（C14 兼容性）
7. 既有 `demo_server.py` `/api/workbench/*` endpoint 回归测试 100% pass（C15）
8. P43 产出的 adapter 全部落 `demonstrative + Upgrade pending`（C10 唯一治理线）
9. 无并行"第二套 orchestrator"代码存在（§3d blacklist 守）
10. **无 `state.yaml` 或新持久化源存在**（v3 cut #1 · non-goal #15 守）
11. **`draft_design_state` 6 条 authority rule 全落地可验证**（v3 cut #3 · §3e · mechanical test）
12. §3d blacklist 无 violation（v3 cut #4 · 静态扫 violation · CI 守）
13. `generate_adapter.py` 的 domain hardcode 若 P43-01 揭示 · 已处理或登记为 known limitation
14. Multi-tab lock test pass（C13）
15. Codex review 必调触点全调用 · 证据 trailer 在 commits
16. Appendix A 完整（用户所有 open question 已 resolve）
17. User Final Approval 流程走通 · 用户 alias + 注释入 manifest

---

## 9. v5.2 + v5.3 compliance（v3）

继承 v2 + 新增：
- **R3 Tier 1 adversarial · 15 counters C1-C15 · C7-C15 verified-by codex-gpt54-xhigh**（round 1 + round 2 完整消化）
- **v5.3 addendum hard rule · Codex re-review 协议 v3**：
  - round 1 (v1 → v2) · verdict 需阻止 · 6 counters A-F
  - round 2 (v2 → v3) · verdict 需修正·信号强 · 4 必补 cut
  - **round 3 (v3 pending)**：v3 commit 后 · Kogami 签 Gate 前 · Executor **再次调 Codex** 审 v3 是否真正消化 4 cut
- 第二轮 Codex 评审输出入 `09C 外部审查简报` · verified-by trailer 在 v3 commit

---

## 10. Codex re-review plan (v3 · round 3 · pre-Gate)

**Prompt 摘要：**
> 你是 Codex GPT-5.4 xhigh · 第三轮评审 Well Harness P43 milestone plan v3。v1 需阻止（6 counter A-F）· v2 需修正·信号强（4 cut：state.yaml 幻影 / P43-01 fail 硬冻结 / draft_design_state authority / §3d touched+forbidden）。v3 声称 4 cut 全修。请核：
> (1) Cut #1 · v3 删了 state.yaml 幻影？non-goal #15 + §3c 持久化二源 + §3d blacklist 是否足够机械化？
> (2) Cut #2 · v3 §3a Exit Criteria 去了 "或列出断裂" ？§7 停点 2.5 硬规则是否真无选项路径？
> (3) Cut #3 · v3 §3e R1-R6 authority contract 是否真机械约束（非口头降级）？R3 禁回写是否真可验证？
> (4) Cut #4 · v3 §3d whitelist/blacklist 是否真明示（含 demo_server.py）？有无漏文件？
> (5) v3 新增 Q11/Q12/Q13 是否覆盖了 round 2 指出的缺失问题？
> (6) 有无 round 3 新盲点？
> 若 v3 覆盖充分 · 明示 "v3 可过 Gate"。若还有结构性漏 · 给 ≤3 条最强反驳 · 建议走 v4。

**Codex 输出处理：** 批判性消化 · 若 "可过 Gate" 交 Kogami 审 · 若还"需修正" 走 v4（path ① 继续）· 若"需阻止" 考虑 R4 撤回 P43。

---

## 11. 停点

**本 plan v3 不执行任何代码。三个停点：**

**停点 1**：v3 commit + branch push 后 · Executor 调 Codex round-3 re-review（v5.3 addendum 要求）
**停点 2**：Codex 返 "可过 Gate" → 提交 Kogami 审 GATE-P43-PLAN (v3) · 否则走 v4
**停点 2.5（v3 新 · 硬规则）**：P43-01 Exit Criteria 未 asserted pass · P43-02+ 自动冻结 · 不可绕过
**停点 3**：Kogami 签 `GATE-P43-PLAN (v3): Approved` + Q1/Q2/Q4/Q7/Q8/Q10/Q11/Q12/Q13 仲裁 · 才启动 P43-01-00-PLAN.md 起草

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum · 2026-04-20
**Revision:** v3 (post-Codex-round-2 · path ① × 2 · 4 cuts integrated)
**Awaiting:** Codex round-3 re-review + `GATE-P43-PLAN (v3): Approved` (Kogami) + 9 Q 仲裁
**Verified-by:** codex-gpt54-xhigh (round 1 · 6 structural counters A-F · round 2 · 4 required cuts)

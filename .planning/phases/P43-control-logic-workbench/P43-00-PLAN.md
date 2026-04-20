---
phase: P43
plan: P43-00
title: Control Logic Workbench end-to-end milestone — design document + sub-phase decomposition
status: drafted · Awaiting GATE-P43-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum
scope_tier: Tier 1 · milestone-level (not a single Phase)
preconditions:
  - GATE-P42-CLOSURE Approved (Kogami 2026-04-20) → main at `a6521ca`
  - Kogami 2026-04-20 R4 指令：完整控制逻辑生成工作台 · 需求文档导入 → 解析 → Q&A 闭环 → 冻结 → 面板逐步生成 → 连线 → 调试 → 标注修改 → 迭代 → 用户批准 → 归档
  - v5.3 addendum 生效 · adapter-boundary 硬性规则 Codex review 必调
non-goals:
  - 本 Phase **不写任何 src 代码**。P43-00 是 milestone 设计文档 · 实施分拆到 P43.1-P43.9 子 Phase · 每个子 Phase 独立 Gate
  - 不修改已锁定的 M1 产出：controller.py / models.py / 5 adapter evaluate/explain 方法 / YAML parameters / registry markdown 5 rows table / JSON schema v1 $id
  - 不新建第二套 truth engine（继承 P16 宪法原则：AI 不控制 Canvas · Canvas 状态来自 truth engine）
  - 不替代 P7 workbench · 本 milestone 是 P7 的上游 UX 层（P7 在"已有 spec"场景下继续有效 · P43 覆盖"spec 尚未存在"的从 0 到 1 场景）
  - 不引入新的 adapter Protocol · 生成的 adapter 走现有 GenericControllerTruthAdapter 协议
  - 不 bump JSON schema version · 任何扩展走 v5.3 C5 缓解策略（additive + to_dict 剥 None）
---

# P43 · Control Logic Workbench — 端到端 milestone 设计文档

## 0. TL;DR

Kogami 2026-04-20 R4 指令：构建一个用户可见的端到端工作台，从**一份用户扔进来的需求文档**到**一个被用户最终批准并归档的控制逻辑面板**，覆盖 9 个阶段：

```
[1] 文档导入 → [2] 解析/询问/确认/冻结 → [3] 面板逐步生成
→ [4] 连线 → [5] 面板调试 → [6] 标注修改 → [7] 迭代优化
→ [8] 用户最终批准 → [9] 归档
```

**关键洞察：** 项目已积累大量原子能力（`document_intake.py` 1118 LOC · `ai_doc_analyzer.py` 868 LOC · `generate_adapter.py` · `demo_server.py` 3677 LOC · `adapter_truth_levels.yaml` · Appendix A Q&A 模式 · `.planning/phases/Pxx/` archive 协议）· 但**没有统一的用户可见 orchestration 层**。

**P43 milestone 的唯一新增**：把已有 primitives 串成一条用户可走完的闭环 pipeline · 填补缺失的 3 类连接（用户交互 UI / 状态持久化 / 阶段间 handoff）· 不重写任何现有 primitive。

**P43-00（本文）scope：** milestone 设计文档 + sub-phase 分解 + Tier 1 adversarial + Open Questions Q1-Q7。**不写 src 代码**。落地实施等 `GATE-P43-PLAN: Approved` 后分拆到 P43.1-P43.9。

---

## 1. Milestone vision · user journey

### 用户视角闭环（单次完整使用）

| Step | 用户动作 | 系统产出 | 用户决策 |
|------|---------|---------|---------|
| 1 · Import | 用户把需求文档扔到 workbench（PDF / docx / md / image）| `uploads/` + SHA 固化 + `intake_packet` 结构体 | 确认文档识别正确 |
| 2a · Parse | 系统用 `ai_doc_analyzer` 解析文档 | 初版 `ControlSystemWorkbenchSpec` 候选 + ambiguity list | — |
| 2b · Q&A | 系统向用户提问（每 ambiguity 一问）| 用户答案持久化到 `clarification_answers.yaml` | 用户填答 / 跳过 |
| 2c · Freeze | 用户确认 spec 定稿 | spec 固化 + traceability matrix Appendix A 生成 | 用户签 "Freeze Approved" |
| 3 · Panel gen | 系统调 `generate_adapter.py` 逐步生成 adapter + 面板 | adapter.py + demo_server 注册的面板页 | 用户旁观（逐 logic_node 生成） |
| 4 · Wiring | 系统根据 `downstream_component_ids` 自动连线 | SVG 连线 + 拓扑图 | 用户可手动加/删 |
| 5 · Debug | 用户跑 snapshot 灌入面板 | `GenericTruthEvaluation` 结果 + 可视化 | 用户观察是否符合预期 |
| 6 · Annotate | 用户在面板上标注问题（哪个 logic 错了 / 哪个阈值不对）| 标注持久化到 `annotations.yaml` | — |
| 7 · Iterate | 系统根据标注 regenerate adapter · 循环 4-6 | 新版 adapter · 标注 carry forward | 用户决定 "再改 / 满意" |
| 8 · Approval | 用户签 "Final Approved" | adapter 锁定 + registry row 添加 · truth_level 升 certified | 用户签名（类 Kogami Gate）|
| 9 · Archive | 系统归档整个工作流 | `.planning/phases/Pxx-{system_id}/` 目录 + closure doc + Notion DECISION | 归档只读 |

### 三个非功能性目标

- **T1 · 可追溯**：每一步的输入输出 + 用户决策都有持久化证迹（沿用 P34-P42 的 traceability matrix + Appendix A 模式）
- **T2 · 可中断**：用户随时关闭、隔天回来、从上次位置继续（state machine 持久化）
- **T3 · 可审计**：最终 archived 工作流是一套 self-describing artifact，无需看代码就知道这个 adapter 怎么来的

---

## 2. 既有 primitives 库存 (NOT TO BE REWRITTEN)

### 已存在的原子能力

| Primitive | LOC | 当前职责 | 覆盖 Step |
|-----------|-----|---------|----------|
| `document_intake.py` | 1118 | SourceDocumentRef + intake_packet 结构 + assess_intake_packet | 1, 2a |
| `ai_doc_analyzer.py` | 868 | ambiguity detection + clarification loop + prompt gen | 2a, 2b |
| `knowledge_capture.py` | 254 | knowledge artifact 捕获 | 2c |
| `system_spec.py` | - | ControlSystemWorkbenchSpec + 所有 spec dataclass | 2c, 3 |
| `generate_adapter.py` | 671 (P42 post-fix) | spec JSON → adapter 源码（含 P42 governance defaults）| 3 |
| `controller_adapter.py` | - | ControllerTruthMetadata (P42 extended) + GenericTruthEvaluation | 3, 5 |
| `demo_server.py` | 3677 | 面板 UI server + API 路由 | 3, 5 |
| `adapter_truth_levels.yaml` | - | machine SoT registry (P42)| 8 |
| `sha_registry.yaml` | - | uploads/ SHA 固化 (P40)| 1, 9 |
| `.planning/phases/Pxx/` | - | closure doc + Gate 签字 archive | 9 |
| `docs/provenance/` | - | traceability matrix 模式 (P34-P42 成熟) | 2c, 8, 9 |
| `workbench_bundle.py` | - | bundle 聚合 | 3, 9 |

### 缺失的连接（P43 要补的）

| Gap | 描述 | 建议 sub-phase |
|-----|-----|---------------|
| **G1** · 统一 orchestrator CLI/API | 目前 primitive 散在不同 module · 没有一条命令跑完 1→9 | P43.1 |
| **G2** · 用户交互 UI（Q&A 面板）| `ai_doc_analyzer` 已生成 clarification prompts · 但没有 demo_server 对应 Q&A 页 | P43.2 |
| **G3** · state persistence 跨 session | 用户中断后从哪里接续 · 目前无 state machine 文件 | P43.1 + 所有 |
| **G4** · Freeze gate 用户签名机制 | intake 层 freeze 目前是手动改 code / YAML · 无用户可视签 | P43.3 |
| **G5** · Progressive panel generation UI | 已有 adapter 一次性生成 · 但"逐步"生成+预览能力缺失 | P43.4 |
| **G6** · wiring editor UI | 自动连线已在 demo_server 有 · 但手动加/删连接 UI 缺失 | P43.5 |
| **G7** · annotation persistence + carry-forward | 用户标注当前无持久层 · regenerate 后丢失 | P43.6 + P43.7 |
| **G8** · Final Approval signature + archive | 用户 "Approved" 签名 → registry 升 certified + 目录归档 无自动 pipeline | P43.8 + P43.9 |

**观察**：**P43 不是 build from scratch · 是 integration + UX layer**。规模估算 ~2500-3500 LOC 新增，主要在 demo_server UI (`.js/.html/.css`) + 1 orchestrator CLI + state machine + 2-3 个中间 yaml schema。

---

## 3. Sub-phase decomposition · P43.1 - P43.9

每个子 Phase 独立 Tier 1 plan + Gate · 本节仅列 scope / 依赖 / 规模预估。

### P43.1 · Orchestrator CLI + state machine（基础设施）
**Scope**：单一入口 `workbench new <doc>` → 创建 workspace 目录 + state.yaml · `workbench continue <id>` → 从 state 恢复 · `workbench status <id>` → 列当前 step。
**产出**：`src/well_harness/workbench/orchestrator.py`（~300 LOC）+ `workbench_state_v1.schema.json` + CLI integration。
**依赖**：既有 primitives 全部引用 · 不改 primitive。
**估算**：~400 LOC · 1 day · 1 Codex review。

### P43.2 · Document import + Q&A UI 闭环
**Scope**：demo_server 加 `/workbench/:id/intake` 页面（上传 doc · 触发 `document_intake.assess_intake_packet`）+ `/workbench/:id/qa` 页面（渲染 `ai_doc_analyzer` clarification prompts · 收集 user answers · 持久化）· 答案反馈 `ai_doc_analyzer` 重评。
**产出**：demo_server 2 新页 · 1 新 API 路由组 · `clarification_answers_v1.schema.json`。
**依赖**：P43.1 orchestrator 状态机 · `ai_doc_analyzer.py` 不改。
**估算**：~600 LOC（前端 400 + 后端 200）· 1-2 days · 1 Codex review。

### P43.3 · Freeze gate + Appendix A 生成
**Scope**：用户在 UI 签 "Freeze Approved" · 系统把 spec 锁定到 `workspace_frozen.yaml` · 自动生成 `traceability_matrix.md`（沿用 P34-P42 模式）· Appendix A 未决假设列表基于 ambiguity 剩余项。
**产出**：`src/well_harness/workbench/freeze.py`（~200 LOC）+ Appendix A 模板生成器。
**依赖**：P43.2 Q&A · `knowledge_capture.py` · `docs/provenance/` 模式。
**估算**：~300 LOC · 1 day · 1 Codex review。

### P43.4 · Progressive panel generation UI
**Scope**：不是一次性生成全 adapter · 而是 logic_node 逐个生成并在 UI 预览 · 用户可在每步暂停 / 回退。`generate_adapter.py` 提供 incremental mode（新加参数 · 不破 v2 既有接口）。
**产出**：demo_server 面板预览页 + generator incremental mode。
**依赖**：P43.3 frozen spec · `generate_adapter.py`（P42 扩展）。
**估算**：~500 LOC · 2 days · **1 Codex review** (adapter boundary · 硬性规则触发 · generator 接口扩展)。

### P43.5 · Wiring editor UI
**Scope**：demo_server 拓扑图节点连线可手动加/删 · 改变 persists 到 `spec.logic_nodes[*].downstream_component_ids` · 改后重跑 generator。
**产出**：demo_server 拓扑图交互 JS + API /wire。
**依赖**：P43.4 panel · controller Protocol 不变。
**估算**：~400 LOC · 1-2 days · 1 Codex review（UI 交互模式变更 · v5.3 硬性场景）。

### P43.6 · Debug harness UI
**Scope**：用户灌入 snapshot JSON · 系统跑 `adapter.evaluate_snapshot(...)` · UI 可视化 `GenericTruthEvaluation`（active nodes + blocked reasons）。沿用 adversarial_test.py 证据面模式。
**产出**：demo_server debug 页 + snapshot 模板库。
**依赖**：P43.4 panel · adapter 已生成。
**估算**：~500 LOC · 1-2 days · 不触 adapter boundary · 可不调 Codex（但建议调）。

### P43.7 · Annotation persistence + iterative regen
**Scope**：用户在面板点击 "logic2 阈值错 · 应该是 -12 不是 -11.74" → 持久化到 `annotations.yaml` · 系统把 annotation 合并回 spec · 触发 regenerate 循环。多轮迭代 state 可追溯。
**产出**：`annotations_v1.schema.json` + iteration loop logic + annotation UI。
**依赖**：P43.4/P43.5/P43.6 · 状态机跨 iteration。
**估算**：~600 LOC · 2 days · 1 Codex review（iteration state machine · 复杂度高）。

### P43.8 · Final Approval + truth_level 升 certified
**Scope**：用户签 "Final Approved" → workspace spec 锁定为新 system · 生成 `CONTROLLER_METADATA` + 添加到 `adapter_truth_levels.yaml`（truth_level=certified · status=In use）· 同步 markdown registry · 生成 adapter code 进 `src/well_harness/adapters/` · 三轨跑。
**产出**：approval pipeline + registry update 自动化 + adapter landing 脚本。
**依赖**：P43.7 · `adapter_truth_levels.yaml` + `test_metadata_registry_consistency.py`（P42 bidir guard 自动覆盖新行）。
**估算**：~400 LOC · 1 day · **1 Codex review**（直接改 registry + adapter 文件 · adapter boundary 硬性规则）。

### P43.9 · Archive + closure
**Scope**：生成 `.planning/phases/Pxx-{system_id}/` 目录 · workspace 全过程（docs 输入 + Q&A 答案 + annotations 历史 + 生成的 adapter / test · Gate 签字链）打包归档。生成 Notion DECISION 块（类 P34-P42 格式）。
**产出**：archive pipeline · Notion sync · closure doc 模板。
**依赖**：P43.8 · Notion MCP · `.planning/phases/Pxx/` 协议。
**估算**：~300 LOC · 1 day · 可不调 Codex（纯 docs/meta）。

### 总规模估算
- LOC：~4000 across 9 sub-phases
- Duration：~10-15 dev days
- Codex review 次数：7（P43.1/2/3/4/5/7/8 硬性 + P43.6 建议）
- 新 JSON schema：3（workbench_state / clarification_answers / annotations）
- 新 yaml registry：1（workspace_frozen · per-workspace not global）
- demo_server 新页：~6（intake / qa / freeze / panel / wire / debug / approval + annotation overlay）
- 新 test：~80-100（按每 sub-phase 8-15 test 估）

---

## 4. Cross-cutting non-goals（milestone-wide）

P43 milestone **不做**以下任何一条（防 scope creep）：

1. **不写 LLM agent** · `ai_doc_analyzer` 已有 prompt 生成 · 用户答案驱动 · 不引入 autonomous LLM reasoning loop
2. **不建第二套 truth engine** · 所有推理仍走 `GenericControllerTruthAdapter.evaluate_snapshot`
3. **不改 P7 workbench UX** · P7 是"已有 spec"场景入口 · P43 是"从 0 生成 spec"场景入口 · 两者并存
4. **不做权限/多用户** · 单用户单机（可扩 · 但 P43 不做）
5. **不上云 / 不上多租户** · 本地 demo_server 运行模式继承
6. **不建实时协作** · annotation 是单用户顺序操作
7. **不改 M1 任何锁定 invariants**（见 frontmatter）
8. **不改 JSON schema v1 $id 或 version const** · 所有 schema 扩展走 P42 v5.3 C5 策略
9. **不建 registry 自动升级 yaml → markdown 的双向同步** · 手动同步模式（P42 现状）保持

---

## 5. Tier 1 对抗性自审（Executor 自审 · Codex review 尚未调 · 在 Gate 前调）

### C1 · "P43 scope 太大 · 9 个 sub-phase · 10-15 天 · 超过 P31-P42 全套时长"
**承认。** 缓解：
1. P43-00 **只是 design 文档 + 分解**。实施 Gate 分拆到每个 sub-phase · Kogami 可在任意 sub-phase 后暂停 / 重新评估
2. 规模估算基于 P34-P42 真实节奏（每 Phase ~400-600 LOC · ~1 day）· P43.1-P43.9 沿用同节奏
3. 每个 sub-phase 独立 GATE-P43.x-PLAN · Kogami 有全 9 次退场机会
4. 若中间某 sub-phase 揭示原 plan 重大错判 · 走 P42-style v1→v2 path ①
5. Accepted risk · milestone 本身是大的 · 但分解后每段可控

### C2 · "既有 primitives 未必能无缝拼接 · document_intake/ai_doc_analyzer 是 P14 时代遗产 · API 与 P43 需要的可能不匹配"
**部分承认。** 缓解：
1. P43-00 的 **§2 primitives 库存表是初步扫描**。每个 sub-phase 开工前 plan 阶段 (P43.x-00) 需对所依赖的 primitive 做真实 API 核验（不走 shadow assumption）
2. 发现 API 不匹配 → sub-phase plan 加 "adapter layer" 包一层不改 primitive
3. 若 primitive 根本缺能力 → 开新 sub-phase 扩 primitive（走 Phase-级 Gate · 不擅自改 M1 锁定层）
4. P41 narrative drift 教训：起草前 grep `ControlSystemWorkbenchSpec` / `AmbiguityAssessment` 等关键类 · 穷举 callers · 在 P43.x-00 plan 登记
5. Accepted risk · 对 primitive 的真实假设由每个 sub-phase 自验 · P43-00 是乐观估算

### C3 · "用户可见 UI 质量 vs 时间 trade-off 没规定 · demo_server 已有 UI 技术债"
**承认。** 缓解：
1. 明确 **非目标**：不做 "production-grade polish"。UI 质量目标 = "用户能闭环走完 9 步" 不等于 "pixel-perfect"
2. demo_server 已有的 UI pattern 复用 · 不引入新 UI 框架（React/Vue/etc.）· 继承 vanilla JS / template string 风格
3. 每个 sub-phase 的 Exit Criteria 包含 "UI 可用性测试：用户能在 <N> 分钟完成该 step"
4. 若 UI 时间超预算 50% → sub-phase 暂停 · 升级 Kogami · 决定是否降质量
5. Accepted risk · milestone 不追求 UI 完美 · 追求闭环可走

### C4 · "iteration loop（P43.7）可能成为死循环 · 用户总在改 · 永远到不了 Final Approved"
**承认。** 缓解：
1. 明确 iteration **终止条件**：用户签 "Final Approved" · 没有 iteration 上限
2. 加 advisory：iteration 第 5 次时系统提示 "是否需要重新做 freeze 阶段 · 或者这个 system 适合 demonstrative 不升 certified"
3. P43.7 的 annotations state 必须包含 iteration_count · 持久化 · 可恢复
4. Non-goal 明示：系统不自动决定 "够了"。用户主权保留
5. Accepted risk · 死循环是用户产品决策 · 非系统 bug

### C5 · "Archive（P43.9）可能与 M1 已建立的 .planning/phases/Pxx/ 协议冲突"
**承认。** 缓解：
1. P43.9 archive 目录命名用 `Pxx-workbench-{system_id}` 模式 · 避开 Phase 数字序列冲突（不占 P44/P45/…）
2. archive 目录作为"生成物档案" · 不是 governance Phase · 不 append 到 ROADMAP.md "Phase P42 / P43 / ..." 序列
3. 区分：P43 milestone 是**开发** phase · archive 目录是**生成物** archive · 两种语义
4. Notion DECISION 块类比 P34-P42 但 tag 用 "workbench-generated"（不占 Gate 序列）
5. P43.9 plan 需要详细设计目录命名空间规则 · 独立 Open Question

### C6 · "这个 plan 本身没调 Codex · 违反 v5.3 adapter-boundary 硬性规则 · milestone 设计涉及 adapter gen/metadata 多处"
**承认。这是本 plan 自审识别的最大 gap。** 缓解：
1. **本 P43-00 plan 提交后 · Kogami 签 GATE-P43-PLAN 之前 · Executor 必调 Codex adversarial review**（与 P42 v5.3 协议一致）
2. 虽然 P43-00 不写代码 · 但它规定了 9 个 sub-phase 的 adapter boundary 边界 · 是 super-adapter-boundary 决策
3. 若 Codex 返 "需修正·信号强" · 走 P42-style path ①（plan v2）
4. 若 Codex 返 "通过" · Kogami 签 P43-00 Approved 后进 P43.1
5. Codex prompt 已准备：重点检视 §2 primitives 库存的真实性 / §3 sub-phase 分解的边界完整性 / §4 non-goals 的 scope 控制力 / §5 C1-C5 覆盖度

---

## 6. Open Questions · Kogami 签 GATE-P43-PLAN 时仲裁

### Q1 · milestone 整体 vs 分拆 Gate
- **A · 本 P43-00 一次性通过后 · P43.1-P43.9 sub-phase Gate 仍各自走**（推荐 · 灵活性 + 失败退场机会最多）
- B · P43-00 approved = 全 9 sub-phase 绑定通过 · 不单独 Gate
- C · 混合：P43.1-P43.3（基础 + Q&A + Freeze）一次 Gate 绑定 · P43.4-P43.9 分别 Gate
- **Executor 建议：A**

### Q2 · UI 技术栈
- **A · 沿用 demo_server 现 vanilla JS + template string 风格**（推荐 · 无框架引入成本 · 继承既有技术债但可控）
- B · 引入轻量框架（Alpine.js / HTMX）提升交互流畅度
- C · 全量重构到 React/Vue（**坚决不选** · 超 P43 scope）
- **Executor 建议：A**

### Q3 · state machine 持久化格式
- **A · yaml 文件 per workspace**（`workspaces/{id}/state.yaml`）· 与既有 `adapter_truth_levels.yaml` / `sha_registry.yaml` 风格一致（推荐）
- B · sqlite DB（更适合未来多用户）
- C · JSON + schema validation（严格但笨重）
- **Executor 建议：A**（**B** 留未来 milestone 扩展）

### Q4 · approval 签名机制
- **A · 用户在 UI 输入自己的 alias + 注释**（类 Git commit · 推荐）
- B · OAuth 集成（超 scope）
- C · Kogami 固定签名（单用户假设）
- **Executor 建议：A**（**C** 作为单机默认 · A 作为未来可扩）

### Q5 · archive 归档粒度
- **A · 全 workflow 归档到 `archive/workbench/{system_id}/` 单目录**（所有 iteration 历史 · annotations · Q&A 答案 · 生成物）（推荐）
- B · 只归档 final approved spec + adapter · 丢弃中间 iteration
- C · 归档到 `.planning/phases/` 与 governance Phase 混合（不推荐 · 命名冲突）
- **Executor 建议：A**

### Q6 · P43.8 登记到 registry 时 truth_level
- **A · 默认 demonstrative · 用户显式升 certified 须走 Phase upgrade（类 P36β 模板）**（推荐 · 保守 · 不 inflation）
- B · Final Approved 即自动 certified
- C · 用户选
- **Executor 建议：A**（与 P42 Q5=A `generate_adapter` 模板默认 demonstrative/Upgrade pending 哲学一致）

### Q7 · P43 milestone 是否挂 v5.3 adapter-boundary 硬性规则？
- **A · P43 milestone 整体标记为"多次触发硬性规则" · 每个 adapter-boundary 触点 sub-phase 必调 Codex**（推荐 · 已在 §3 标）
- B · milestone 级一次性 Codex review 覆盖全 9 sub-phase（省 token 但 scope 难 · 不推荐）
- **Executor 建议：A**

---

## 7. Execution sequencing

一旦 `GATE-P43-PLAN: Approved` 签出：

1. **P43.1 开工**（orchestrator + state machine · 基础设施 · 所有后续依赖）
2. **P43.2 + P43.3 串行**（intake/Q&A UI · 然后 Freeze gate）
3. **P43.4 + P43.5 + P43.6 可并行**（panel gen · wiring · debug · 各自独立 UI）·但建议串行避免 UI 冲突
4. **P43.7 pause-point**：P43.6 landed 后 Kogami 做 "milestone 中期 check" · 判断是否继续 P43.7-P43.9 或暂停评估
5. **P43.7 + P43.8 + P43.9 串行**（iteration 依赖 annotation · approval 依赖 iteration · archive 依赖 approval）

**整体 timeline 预期：** ~2-3 周（考虑每 sub-phase plan 期 · Codex review · Kogami Gate 等待）

---

## 8. Milestone-level Exit Criteria

P43 全 9 sub-phase landed 后，满足以下**全部** 才算 milestone 完成：

1. 新用户可通过 `workbench new <doc>` 单一命令启动全流程
2. 闭环 demo：选一个非 5 现有链路的新 domain（例如 "cabin pressurization" / "anti-skid braking" / 任选一个 Kogami 指定的 demo domain）· 跑完 1→9 · 产出 certified 新 adapter · 三轨绿
3. 闭环 demo 的 archive 目录自包含 · 陌生工程师 30 分钟内能看懂这个 adapter 怎么来的
4. 既有 5 adapter 的 runtime behavior 字节级不变（M1 invariants 守住）
5. default lane test 数（当前 796）+ new tests (est 80-100) ~875-900 · 无 regression
6. e2e lane + adversarial wrapper 继续全绿
7. 每 sub-phase 各自 DECISION block 已入控制塔 Notion
8. Notion `02B Execution Run` 数据库包含 9 新 runs（P43.1-P43.9 各一）
9. 05 QA / 06 Evidence 数据库同步更新
10. Milestone closure doc `.planning/milestones/M2-control-logic-workbench-CLOSURE.md` 签字

---

## 9. v5.2 + v5.3 compliance

- **R1** 不可逆 main HEAD · 每 sub-phase 独立 feature branch + Option M 非 FF merge · 每 Phase Gate 前不 push main
- **R2** 不自签 · GATE-P43-PLAN + GATE-P43.1-PLAN + ... + GATE-P43.9-CLOSURE 全部 Kogami 显式
- **R3** Tier 1 adversarial · 6 counters C1-C6 本 plan 就地缓解 · Codex review C5/C6/C7... 后续加
- **R4** 不自选 · 本 R4 方向 Kogami 明示（2026-04-20 "完整控制逻辑生成工作台"）· sub-phase 开工顺序按 §7 建议 · Kogami 可重排
- **R5** 证迹先行 · 本 plan 先于 code · 不先建 primitive / 后补 plan
- **v5.3 addendum hard rule** · adapter-boundary 硬性场景 7 次（§3 标注）· 每次必调 Codex · 结果批判性消化不直接复制 · verified-by trailer

---

## 10. Codex adversarial review plan (pre-Gate)

按 v5.3 addendum 协议 · **本 P43-00 plan 提交后 · Kogami 签 GATE-P43-PLAN 之前 · Executor 调 Codex**：

**Prompt 摘要：**
> 你是 Codex GPT-5.4 xhigh · 以 adversarial reviewer 身份评审 Well Harness P43 milestone plan (Control Logic Workbench 端到端)。重点审查以下 4 维度 · 给 ≥3 最强反驳 + 缓解建议：
> (1) §2 primitives 库存是否真实可用（假设 document_intake/ai_doc_analyzer 当前 API 与 P43 需求对得上是否过于乐观？）
> (2) §3 sub-phase 分解是否 complete（有无遗漏的 boundary · 如 state persistence 模式 / 错误恢复 / Kogami interrupt / 测试策略）
> (3) §4 non-goals 是否 scope creep 防御充分（"不建第二套 truth engine" 等硬边界是否可执行）
> (4) §5 C1-C5 Executor 自审是否覆盖 milestone 真实风险 · 有无遗漏结构性 bug 窗口

**Codex 消化流程：** 同 P42 协议（C1-C7 新增 · verified-by trailer · 不直接复制文字）。

**若 Codex 返"需修正·信号强"：** 走 path ① · v2 plan · 再次提交。Executor 不自签 Gate。

---

## 11. 停点

**本 plan v1 不执行任何代码。两个停点：**

**停点 1（等 Codex review）：** 提交此 plan v1 + branch push 后 · Executor 调 Codex adversarial review · 消化回 plan v1/v2 · 再提 Kogami 审。

**停点 2（等 Kogami Gate）：** Kogami 签 `GATE-P43-PLAN: Approved` + Q1-Q7 仲裁 · 才启动 P43.1 的 P43.1-00-PLAN.md 起草。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum · 2026-04-20
**Awaiting:** Codex adversarial review (self-initiated per v5.3) + `GATE-P43-PLAN: Approved` (Kogami) + Q1-Q7 仲裁
**Scope:** milestone-level design doc · no src code · 9 sub-phase decomposition · 4 cross-cutting non-goals · 6 self-audit counters

---
phase: P43
plan: P43-00
plan_revision: v2 (post-Codex remediation · path ①)
title: Control Logic Workbench end-to-end milestone — v2 · extend-not-rebuild + Contract Proof Spike first
status: re-drafted · Awaiting GATE-P43-PLAN (v2) (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum
verified-by: codex-gpt54-xhigh (2026-04-20 · 6 structural counters A-F integrated, 需阻止 verdict addressed via path ①)
scope_tier: Tier 1 · milestone-level
preconditions:
  - GATE-P42-CLOSURE Approved (Kogami 2026-04-20) → main at `a6521ca`
  - Kogami 2026-04-20 R4 指令：完整控制逻辑生成工作台
  - v1 plan (`81adf39`) 被 Codex 判 **需阻止**（6 structural counters · 2 条含既有 code 真 bug 作证）
  - Kogami 2026-04-20 路径① 明示选择：修 plan v2 + 插入 Contract Proof Spike
  - v5.3 addendum 生效 · adapter-boundary 硬性规则 Codex review 必调
non-goals:
  - 本 P43-00 v2 不写任何 src 代码
  - 不修改已锁定 M1 产出：controller.py / models.py / 5 adapter evaluate/explain 方法 / YAML parameters / registry markdown 5 rows table / JSON schema v1 $id
  - **不并行建第二套 orchestrator**（Codex Counter B 消化）· P43 是 extend existing (`cli.py bundle` / `workbench_bundle.py` / `workbench.js` localStorage / `archive_workbench_bundle`) · 不是 rebuild
  - 不建第二套 truth engine
  - **不在 P43-05 (progressive panel gen) / P43-08 (annotation+iteration) 建 shadow truth engine**（Codex Counter C 消化）· preview 只展示候选 diff · 不作 runtime 语义源
  - 不替代 P7 workbench
  - 不引入新的 adapter Protocol
  - 不 bump JSON schema version
  - **"Final Approved" 不等于 truth_level=certified**（Codex Counter D 消化）· Final Approved → `demonstrative/Upgrade pending` · certified 升级走独立 Phase（沿用 P36β/P38 authoritative-doc + SHA + matrix + independent-Gate 协议）
  - 不扩 P43 范围到 "certified upgrade pipeline" · 那是独立 future Phase
---

# P43 · Control Logic Workbench milestone (v2) — extend-not-rebuild + Contract Proof Spike

## 0. TL;DR · v1 → v2 差异

| 维度 | v1 plan（已废） | v2 plan（本文） |
|------|---------------|----------------|
| Primitives 库存 | 按 LOC 计 · 假设 API 对得上 | 承认 "伪库存" · **先跑 P43-01 Contract Proof Spike** 产出真实契约报告 · 再决定 P43-02+ scope |
| Orchestrator 建设策略 | 并行建新 `workbench/orchestrator.py` + 新 CLI + 新 state.yaml | **Extend existing** · 复用 `cli.py bundle` + `workbench_bundle.py` + `workbench.js` localStorage · P43 加连接不造新 |
| 治理 Final Approved 语义 | §1 用户旅程 / P43.8 明写 certified · Q6 又推 demonstrative · 自相矛盾 | **唯一治理线**：Final Approved → `demonstrative + Upgrade pending` · certified 独立 future Phase · 删所有 P43 内 certified 升级路径 |
| Progressive preview 身份 | 模糊 · 隐式充当 runtime 语义源 | 明确定位 **draft_design_state** · 非 truth · 非 runtime · 非 certifiable · 只展示候选 diff |
| Workflow 契约 | 只选存储格式 | P43-02 前先输出 **workflow automaton contract**（state enum · event · transition table · error taxonomy · recovery rules） |
| Sub-phase 分解 | P43.1-P43.9 = 9 sub · 扁平 | P43-01 Spike（先行）→ Kogami 重审 → P43-02..P43-10（10 sub）· P43-01 结果可推翻 P43-02+ 设计 |
| Self-audit counters | C1-C6 | C1-C12（6 原 + 6 新 verified-by codex-gpt54-xhigh）· 加 primitive integration proof / workflow automaton correctness / existing workbench migration / gate fatigue / doc extraction 物理能力 / governance line coherence |
| Exit 样板 demo | 新 "cabin pressurization" 等 domain | P43-01 产出后 Kogami 选（P43-01 可能揭示新 domain 不必要 · 仅 extend 即够）|
| Kogami Gate 次数 | ~18 gate (9 plan + 9 closure) · 高 fatigue 风险 | **Gate batching 选项在 Q1 下**：Q1=D（推荐）· P43-01 + P43-02 + P43-03 作为"基础线" 合 1 gate · P43-04..10 按 pair 合 gate · ~8-10 gate 总 |
| 规模 | ~4000 LOC 共 9 sub | Unknown · **P43-01 产出后重估**（可能 ~2500-3500 因 extend 复用） |
| Codex verdict on v1 | 需阻止 | v2 consumes all 6 counters via path ① · 需 Codex re-review（在 v2 commit 后 · Kogami 签 v2 Gate 前） |

**v2 核心观念**：**"先跑再建"**。v1 的致命缺陷是 Executor 读了几行 code 就自信 primitive 能串 · Codex 用 2 条真 bug 打碎。v2 先做 Contract Proof Spike · 让事实说话。

---

## 1. Milestone vision · user journey（v2 · 治理统一）

### 核心原则（Codex Counter D 消化）

**Final Approved ≠ certified**。无论用户多信任自己产出 · P43 pipeline 只能落 `demonstrative + Upgrade pending`。certified 升级是独立的、严格的、需要：
- 上游权威文档（authoritative doc · 非自述）· uploads/ 入库 · SHA 固化
- Traceability matrix（P34/P38 模式）
- Appendix A 所有 open question resolved
- 独立 Phase + Kogami GATE-Pxx-CLOSURE: Approved

**P43 milestone 产出的所有 adapter 天然是 demonstrative**（与 bleed-air / efds / landing-gear 三个 P35α 历史遗产同级）。用户若需 certified · 走 P36β-style upgrade Phase（不在 P43 scope）。

### 用户旅程闭环（10 step · 治理对齐）

| Step | 用户动作 | 系统产出 | 用户决策 | 治理 level |
|------|---------|---------|---------|----------|
| 1 · Import | 扔 pdf/docx/md/image | intake + SHA 固化 | 确认识别 | — |
| 2a · Parse | 系统跑 `ai_doc_analyzer` | 候选 spec + ambiguity list | — | — |
| 2b · Q&A | 系统提问 | 答案持久化 | 填答/跳过 | — |
| 2c · Freeze | 用户"Freeze Approved" | frozen spec + Appendix A | 用户签 | draft-frozen |
| 3 · Panel gen | 系统生成 adapter 预览 | draft adapter + 面板 | 旁观 | draft-preview |
| 4 · Wiring | 连线编辑 | 更新 spec | 手动加/删 | draft-preview |
| 5 · Debug | 灌 snapshot | evaluation 结果 | 观察 | draft-preview |
| 6 · Annotate | 标注 | annotations.yaml | — | draft-preview |
| 7 · Iterate | regenerate | 新版 draft adapter | 再改/满意 | draft-preview |
| 8 · Final Approval | 用户签 "Final Approved" | adapter landing + registry row + `demonstrative + Upgrade pending` | 签名 | **demonstrative/Upgrade pending** |
| 9 · Archive | 归档 | `archive/workbench/{system_id}/` + closure | 归档只读 | — |

### 三个非功能性目标（v2 保留）

- **T1 可追溯** · T2 可中断 · T3 可审计

---

## 2. Primitives 库存 · 真实性警告（Codex Counter A/B/F 消化）

### 2a · v1 库存是 "伪库存"（自认）

v1 §2 按 LOC 计算既有 primitives · 未核 API · Codex 指出至少 2 条**既有真 bug** + **大量 inventory 盲点**：

| Codex 指出 | 验证 |
|----------|------|
| `ai_doc_analyzer.py:838` 读 `assessment.get("blockers")` · `document_intake.py:940` 产 `"blocking_reasons": blockers` | ✅ 实证 · `run_pipeline_from_intake()` 永远找不到 blocker |
| PDF/docx 没有真实抽取 · `ai-doc-analyzer.js:191` 只是 `readAsText()` | ✅（需 P43-01 进一步核） |
| analyzer 产 `q-*` / `clarify-*` · intake gate 要固定 ID `source_documents` / `component_state_domains` · 不对接 | ✅（需 P43-01 核映射） |
| 既有 `cli.py bundle` + `workbench_bundle.py` + `archive_workbench_bundle` + `workbench.js` localStorage 工作区 v1 plan 完全未 inventory | ✅ 实证 · 见 §2c |
| `generate_adapter.py:255,448` 有 domain hardcode（`max_n1k_deploy_limit` 默认值 / `thr_lock` terminal） | 需 P43-01 核 |

### 2b · P43 不再声明完整 inventory · 改为 P43-01 产出"真实契约报告"

**v2 决策**：P43-00 不再给 §2 primitives 表打勾。所有 inventory + API 契约核验推迟到 P43-01 Contract Proof Spike 产出。P43-02 及后续子 Phase 的 plan 必须引用 P43-01 产出的契约报告 · 不能 re-invent 或 LOC-counted assumption。

### 2c · 既有 workbench 工作（P43 必须 extend · 不 rebuild）

Codex Counter B 指出 · v1 无视如下既有 orchestration 层：

| 既有组件 | 位置 | 职责 | P43 extend 策略 |
|---------|------|------|--------------|
| `cli.py bundle` subcommand | `src/well_harness/cli.py:200` | 已有 intake packet → bundle 打包 pipeline | P43-02 在此基础加 orchestrator `new` / `continue` / `status` subcommands · 不另建 CLI |
| `workbench_bundle.py` | `src/well_harness/workbench_bundle.py` | build / archive / restore / manifest validate | P43-02 的 state machine 用这个做 canonical storage · 不另建 state.yaml |
| `workbench.js` localStorage 工作区 | `src/well_harness/static/workbench.js:4,6` + `workbench.html:183` | 浏览器端 workspace · archive-toggle · handoff-note · archive restore | P43-03 的 UI 扩展这个 · 不另写前端 shell |
| `archive_workbench_bundle` + `resolve_workbench_archive_manifest_files` | `workbench_bundle.py` | manifest + restore | P43-10 archive 用这个 · 不另建 archive 目录结构 |
| Appendix A 模式（P34-P42） | `docs/{system}/traceability_matrix.md` | open question 登记 · Kogami sign-off | P43-04 Freeze 产出 Appendix A 用同模板 |

P43-01 必须 inventory 这些 + 发现所有 delta · 才能写 P43-02 plan。

---

## 3. Execution strategy · v2 重分解

### 3a · 关键新增：P43-01 Contract Proof Spike（先行 · must-land-before-anything）

**不是 9 sub-phase 的一部分**。P43-01 是 P43 能继续存在的前提条件 · 不 land · P43-02+ 全部 on-hold。

**P43-01 scope：**

1. **跑真实 happy path**：选一份真实 pdf 或 docx（例如已有 `uploads/20260409-thrust-reverser-control-logic.docx` 或 `uploads/20260417-C919反推控制逻辑需求文档.pdf`）· 从 browser 扔进 `workbench.js` · 跟到 `ai_doc_analyzer` · 跟到 `document_intake.assess_intake_packet` · 跟到 `cli.py bundle` / `workbench_bundle` · 跟到 archive · 记录每一步实际断裂点
2. **跑真实 failure path**：故意扔一份"应有 blocker" 的 intake · 验 `ai_doc_analyzer.py:838 assessment.get("blockers")` 路径是否工作（预计：不工作 · 因 key mismatch）
3. **修 `blockers`/`blocking_reasons` 真 bug**：改 `ai_doc_analyzer.py:838` 读 `blocking_reasons` · 加 regression test 防再回归
4. **PDF/docx 抽取能力核**：`ai-doc-analyzer.js:191 readAsText()` vs 实际 .docx binary · 是否 silently 失败 / 乱码 / 还是根本没跑进 parse · P43-01 要 demo 一个真实 pdf 看结果
5. **analyzer ID ↔ intake clarification ID 契约核**：`ai_doc_analyzer` 产 `q-*` · `intake` 要 `source_documents` / `component_state_domains` · 现状是否 wire · 如何 wire
6. **generator hardcode 暴露**：`generate_adapter.py:255,448` 对任意非 thrust_reverser-style spec 产出是否合法 · 产报告
7. **workbench.js 工作区 schema inventory**：`localStorage key` 名 · archive manifest 结构 · handoff-note 结构 · 用真实代码 dump

**P43-01 产出：** `docs/P43-contract-proof-report.md`（~300-500 行 · 真实断裂清单 + 修复计划 + primitive API 契约表）+ `ai_doc_analyzer.py` 真 bug 修 + regression test。

**P43-01 规模：** ~1 day · ~200 LOC 修 + ~500 行 docs · 1 Codex review（adapter boundary · `ai_doc_analyzer` 写操作）。

**P43-01 Exit Criteria：**
- 真实 happy path 端到端跑通（或清晰列出所有断裂）
- 真实 failure path 端到端验证（blocker 能被识别）
- P43 contract proof report 完整
- P43 Kogami 基于此报告决定 P43-02+ scope（可能 dramatic 改动原 v2 估算）

### 3b · P43-02..P43-10（P43-01 landed 后 Kogami 重审才定）

**v2 保留 tentative 分解 · 等 P43-01 实际结果可能大改**。Tentative list：

- **P43-02** · Orchestrator extend · 在 `cli.py bundle` + `workbench_bundle.py` 基础加 state machine + `workbench.js` 跨 step state 透明化
- **P43-03** · Document pipeline · 修 PDF/docx 真实抽取 · 修 clarification contract
- **P43-04** · Freeze gate + Appendix A 生成
- **P43-05** · Progressive panel preview（**draft_design_state** 身份 · 非 runtime 非 certifiable · 只展示候选 diff · Codex Counter C 消化）
- **P43-06** · Wiring editor + graph validator（cycle / terminal uniqueness / fan-out 约束）
- **P43-07** · Debug harness
- **P43-08** · Annotation + iteration loop（同 P43-05 · draft-preview · 不作 runtime）
- **P43-09** · Final Approval → **demonstrative + Upgrade pending**（不是 certified · Codex Counter D 消化）
- **P43-10** · Archive · 复用 `archive_workbench_bundle` · 不新建目录结构

**Tentative 规模：** ~2500-3500 LOC（v1 的 ~4000 LOC 下降 · 因 extend existing）· P43-01 可能推翻。

### 3c · Workflow automaton 契约（Codex Counter E 消化）

P43-02 plan 的前置条件：**P43-02-00-PLAN.md 必包 workflow automaton 章节**，含：

- **State enum**：`INIT / INTAKED / PARSING / AWAITING_ANSWERS / FREEZING / FROZEN / GENERATING / PANEL_READY / WIRING / DEBUGGING / ANNOTATING / ITERATING / APPROVING / APPROVED / ARCHIVING / ARCHIVED / ERROR`
- **Event list**：`import_doc / answer_question / confirm_freeze / start_gen / wire_change / submit_snapshot / annotate / reiterate / final_approve / archive` · 每个 event 的 legal pre-state + 产生的 post-state
- **Transition table**：N×M 矩阵 · N states × M events · 标 legal / illegal / conditional
- **Error taxonomy**：`pdf_extract_failure` · `ambiguity_unresolved` · `regen_failure` · `iteration_overflow` · `schema_drift` · `partial_write` · `external_state_delete` · 每个 error 的 recovery action
- **Idempotency rules**：哪些 event 幂等（可重放）· 哪些非幂等（需 deduplication token）
- **Partial write recovery**：state.yaml 写到一半 crash · 下一次启动如何识别 + 恢复
- **Cross-phase integration test ownership**：谁写 · 谁跑 · coverage 阈值 · 什么触发 regression

### 3d · Existing workbench migration 契约（Codex Counter B 消化）

P43-02 plan 的前置条件：**P43-02-00-PLAN.md 必包 migration 章节**：

- 既有 `workbench.js` localStorage v2 schema → P43 state schema 映射
- 既有 `archive_workbench_bundle` manifest → P43 archive manifest 映射
- 兼容性验收：既有 archive 必须无损 restore 到 P43 flow
- 废弃 vs 并存决策：哪些既有能力被 P43 替代（必须 deprecate）· 哪些并存（必须 migration path）

---

## 4. Non-goals · v2 扩展

继承 v1 全部 + 新增（v2 · Codex 消化）：

10. **不并行建第二套 orchestrator**（Counter B） · P43 所有 subcommands / UI / state 必须 extend existing `cli.py bundle` + `workbench_bundle` + `workbench.js` · 不另建命名空间
11. **不在 P43-05 / P43-08 建 shadow truth engine**（Counter C） · progressive preview 标记为 `draft_design_state` · 非 truth · 非 runtime · 非 certifiable · 冲突时 frozen spec 为 authoritative
12. **Final Approved ≠ certified**（Counter D） · P43 所有 pipeline 只落 `demonstrative + Upgrade pending` · certified 升级走独立 future Phase · §1 用户旅程 + §3b P43-09 + Q6 全部对齐到此唯一治理线
13. **不跳过 workflow automaton 契约**（Counter E） · P43-02 plan 起草前 `workflow automaton contract` 必须先落地 · 不是随 "各 sub-phase 自己加" 糊过
14. **不声明 primitives 库存**（Counter A） · P43-02+ 所有 sub-phase plan 必须引用 P43-01 产出的契约报告 · 不能再 "LOC counted assumption"

---

## 5. Tier 1 对抗性自审 · v2（C1-C12 · 6 原保留 + 6 新 verified-by codex-gpt54-xhigh）

### 原 6 条（v1 保留 · 均被 v2 缓解或加强）

**C1 · scope 太大** · 缓解：P43-01 先行 · 分解可能显著变小 · Kogami 每 sub-phase 退场机会保留

**C2 · primitives API assumptions may not hold** · **v2 从"部分承认"升级到"完全承认"** · P43-01 就是专门解决此 counter · 见 §3a

**C3 · UI quality vs time** · 缓解：继承 `workbench.js` 技术栈 · 不引入新框架

**C4 · iteration loop 可能死循环** · 缓解：用户主权 · 第 5 次 advisory · 加 iteration_count 上限 10（防 state 爆炸）

**C5 · archive 命名冲突** · 缓解：**archive 复用 `archive_workbench_bundle` 既有机制**（Counter B 副产）· `archive/workbench/{system_id}/` 不新建

**C6 · plan 本身没调 Codex** · **已消化**：2026-04-20 调 Codex · 返 "需阻止" · 所有 6 counter 在 v2 消化（C7-C12）

### 新 6 条（v2 · verified-by codex-gpt54-xhigh · 整合 Codex Counter A-F）

**C7 (= Codex Counter A) · §2 primitives 是伪库存**

**攻击（Codex 原话简化）：** `document_intake.py` / `ai_doc_analyzer.py` 记成"现成"但：SourceDocumentRef 只是元数据壳 · 后端只吃 `document_text` 字符串 · 前端 `.docx/.pdf` 只 readAsText() · `blockers` vs `blocking_reasons` 真 bug · PDF 抽取 / OCR / canonical text / SHA-to-text 绑定全无。

**v2 缓解：**
1. P43-01 Contract Proof Spike **先行 · 必须 land** 前无 P43-02+ 开工 · 见 §3a
2. §2 v2 明示 "伪库存警告" · 不再 LOC-counted assumption
3. P43-01 修 `ai_doc_analyzer.py:838` `blockers` → `blocking_reasons` 真 bug · 加 regression test
4. P43-01 产 `docs/P43-contract-proof-report.md` · 所有后续 sub-phase 引用此 · 不能 re-invent 假设

**C8 (= Codex Counter B) · 在并行造第二套 orchestrator**

**攻击（Codex 原话简化）：** 仓库已有 `bundle/archive/restore` CLI + `workbench.js` localStorage workspace + archive manifest + handoff snapshot · P43 却另建 state.yaml + 新 CLI + 新页面 · 结果三套 workspace 真相分叉。

**v2 缓解：**
1. non-goal #10 硬禁止并行第二套 orchestrator · 见 §4
2. §2c 既有工作 inventory 表 · P43-02 必须 extend 这些不 rebuild
3. §3d P43-02 plan 前置要求 migration contract · 既有 `workbench.js` + `archive_workbench_bundle` schema 必须映射到 P43 flow
4. 兼容性验收：既有 archive 必须无损 restore 到 P43 flow（P43-02 Exit Criteria）

**C9 (= Codex Counter C) · P43-05 + P43-08 实质在建 shadow truth engine**

**攻击（Codex 原话简化）：** `progressive panel generation + pause/rollback` + `annotation → merge back → regenerate` = 在 frozen spec 之外建可变中间语义层 · `generate_adapter.py:255,448` 已有 domain hardcode · preview truth / frozen spec / generated adapter 三套可分叉 · plan 没定 authoritative。

**v2 缓解：**
1. non-goal #11 明确 `draft_design_state` 身份 · 非 truth / 非 runtime / 非 certifiable · 冲突时 frozen spec authoritative
2. P43-05 preview 只展示"候选变更 diff" · 不作 runtime 语义来源
3. P43-06 wiring editor 前置：graph validator 先落地（cycle / terminal uniqueness / fan-out 约束 · P43-06 Exit Criteria）
4. P43-08 annotation → regen 之前必须 validator 通过 · 否则 annotation 被拒 + 用户可视反馈

**C10 (= Codex Counter D) · P43-09 认证路径与 P42 governance 正面冲突**

**攻击（Codex 原话简化）：** P43.8 原文 "Final Approved → certified/In use" · Q6 又推默认 demonstrative · 两条互斥治理线 · 且违反既有 registry 升级协议（authoritative doc + SHA + matrix + 独立 gated phase）。

**v2 缓解：**
1. non-goal #12 唯一治理线：Final Approved → `demonstrative + Upgrade pending` · certified 升级走独立 future Phase
2. §1 用户旅程 + §3b P43-09 + Q6 全部对齐到此
3. 删除所有 P43 sub-phase 内"certified"升级路径 · 即使用户签 Final Approved 也不升 · 明示
4. 独立 certified Phase 模板沿用 P36β/P38 · 不在 P43 scope

**C11 (= Codex Counter E) · §3 workflow correctness 缺失**

**攻击（Codex 原话简化）：** plan 承诺"可中断 / 可恢复 / 多轮可追溯" · 实际 P43.1 只是选存储格式 · 没 workflow automaton / state enum / transition table / idempotency / partial-write 恢复 / regen 失败回滚 / schema 变更后 resume / iteration overflow 策略 · wiring 改 downstream_component_ids 但 blocker 只查引用存在不查 cycle / terminal / fan-out。

**v2 缓解：**
1. §3c workflow automaton 契约 scope 明示 · P43-02 plan 前置必要条件
2. §3c 列 17 个 state + 10+ event + error taxonomy + idempotency rules + partial write recovery
3. §3c 要求 cross-phase integration test ownership 明示
4. P43-06 wiring graph validator 单列 scope（cycle / terminal uniqueness / fan-out）· 非"UI 前端交互"而已
5. iteration_count 上限 10 · 防 state 爆炸（C4 副产）

**C12 (= Codex Counter F) · §5 自审盲点**

**攻击（Codex 原话简化）：** C1-C6 盯 scope / UI polish / 死循环 / archive 命名 / 要不要调 Codex · 但遗漏 primitive integration proof / state machine correctness / existing workbench migration / gate fatigue · 且存在真实既有 code bug（`blockers`/`blocking_reasons`）。

**v2 缓解：**
1. 本节 §5 扩 6 新 counter（C7-C12）· 覆盖 primitive integration / state machine / existing workbench / governance / self-audit 诚实度
2. P43-01 is a real-link-report spike · 不再 "审叙事"
3. Gate fatigue 通过 Q1=D（Gate batching · 推荐）· 见 Q1
4. Primitive integration 通过 P43-01 Contract Proof Spike 证明 · 非 assumption

---

## 6. Open Questions · Kogami 签 GATE-P43-PLAN (v2) 时仲裁

### Q1 · Gate 策略（**v2 新增 option D · 推荐**）
- A · P43-00 v2 approve 后 · P43-01 + 每个 P43-02..10 各独立 gate（18 gate · high fatigue）
- B · P43-00 v2 approve = 全部绑定（0 退场机会 · 不选）
- C · 混合：P43-01 独立 · P43-02..04 合 · P43-05..07 合 · P43-08..10 合（5 gate · medium）
- **D · v2 推荐**：P43-01 独立 gate · P43-02..04 合 1 gate（基础线）· P43-05..07 合 1 gate（preview/wiring/debug）· P43-08..10 合 1 gate（iteration/approval/archive）· 共 **4 gates**（最低 fatigue · 每阶段有清晰退场点）
- **Executor 建议：D**

### Q2 · UI 技术栈（v1 同）
- A · 沿用 `workbench.js` vanilla JS 风格（推荐）
- B · 引入 Alpine.js/HTMX
- C · React/Vue（坚决不选）
- **Executor 建议：A**

### Q3 · state machine 持久化格式（v2 升级）
- A · 独立 yaml per workspace（v1 推荐）
- **B · 扩展 `workbench.js` localStorage workspace v2 schema**（v2 推荐 · 复用既有 + 加 P43 新字段）
- C · sqlite
- **Executor 建议：B**（与 non-goal #10 一致）

### Q4 · approval 签名（v1 同）
- **A · 用户 alias + 注释**（推荐）
- B · OAuth
- **Executor 建议：A**

### Q5 · archive 粒度（v2 升级）
- A · 独立 `archive/workbench/{system_id}/` 新建
- **B · 复用 `archive_workbench_bundle` + 扩 manifest schema**（v2 推荐 · 与 non-goal #10 一致）
- **Executor 建议：B**

### Q6 · Final Approved truth_level（v2 唯一治理线）
- **A · 只能落 `demonstrative + Upgrade pending`**（v2 唯一合法 · Codex Counter D 消化）
- ~~B · Final Approved → certified~~（v2 禁止）
- **Executor 建议：A**（唯一选项 · 此 Q 保留只为明示记录）

### Q7 · adapter-boundary Codex 硬性规则（v1 同）
- **A · P43 milestone 整体标记 · 每触点必调 Codex**（推荐）
- **Executor 建议：A**

### Q8 (v2 新) · P43-01 内容范围
- A · 只跑 happy + failure path + 修已知 bug（最 lean）
- **B · 额外产 primitive API 契约表（Executor 推荐）**（推荐 · 后续 sub-phase plan 必需）
- C · 加全套 performance benchmark（超 P43-01 scope）
- **Executor 建议：B**

### Q9 (v2 新) · P43-01 failed 怎么办
- A · Kogami 关 P43 milestone · 重新 R4 决策
- **B · Executor 基于 P43-01 报告输出 P43-00 v3**（推荐 · 若 spike 揭示既有工作不足 / primitive 破碎度超预期 · plan 可能 dramatic 改）
- C · 继续按 v2 分解（不基于实证 · 强行执行 · 不推荐）
- **Executor 建议：B**（反映"先跑再建"哲学）

### Q10 (v2 新) · workflow automaton 契约格式
- A · 纯 markdown 在 P43-02-00-PLAN.md §
- **B · 独立 `docs/P43-workflow-automaton-contract.md` + machine-readable yaml schema**（推荐 · 支持 runtime state validation）
- **Executor 建议：B**

---

## 7. Execution sequencing · v2

```
P43-00 v2 plan commit + Codex re-review + Kogami GATE-P43-PLAN (v2) Approved
         ↓
P43-01 Contract Proof Spike (独立 gate · ~1 day · 先行 · must land)
         ↓
[P43-01 报告审查：Kogami 决定 P43-00 v2 保留 / 改 v3 / 撤回 P43]
         ↓ (若 v2 保留)
P43-02..P43-04 基础线（合 1 gate · workflow + orchestrator extend + Q&A + Freeze）
         ↓
P43-05..P43-07 preview 层（合 1 gate · progressive panel + wiring + debug）
         ↓
P43-08..P43-10 iteration + approval + archive（合 1 gate · 收尾）
```

**总 gates：4**（P43-01 + 3 批次）· 若 Q1=D Kogami 批

**总 duration：** P43-01 ~1 day · 基础线 ~3-5 day · preview 层 ~3-5 day · 收尾 ~2-3 day · **~10-14 day**（与 v1 同量级但 Gate fatigue 降）

---

## 8. Milestone-level Exit Criteria（v2 更严）

继承 v1 10 条 + 新增：
11. `ai_doc_analyzer.py` `blockers`/`blocking_reasons` bug 已修 + regression test land（P43-01 产出）
12. `docs/P43-contract-proof-report.md` 存在 · Kogami 审过
13. `docs/P43-workflow-automaton-contract.md` + machine-readable yaml 存在（Q10=B）
14. 既有 `archive_workbench_bundle` manifest 能无损 restore 到 P43 flow（C8 兼容性验收）
15. P43 产出的 adapter 全部落 `demonstrative + Upgrade pending`（C10 唯一治理线）
16. 无并行"第二套 orchestrator"代码存在（C8 non-goal 守）
17. `generate_adapter.py` 的 domain hardcode（若 P43-01 揭示）已处理或登记为 known limitation（C9）

---

## 9. v5.2 + v5.3 compliance（v2 · 扩）

继承 v1 + 新增：
- **R3 Tier 1 adversarial · 12 counters C1-C12 · 其中 C7-C12 verified-by codex-gpt54-xhigh**（v1 的 6 counter 升 12）
- **v5.3 addendum hard rule · Codex re-review 协议 v2**：P43-00 v2 commit 后 · Kogami 签 Gate 前 · Executor **再次调 Codex** 审 v2 · 消化 "v2 是否真解决了 v1 的 6 counter" 问题 · 第二轮 Codex 输出入 `09C 外部审查简报` + verified-by trailer

---

## 10. Codex re-review plan (v2 · pre-Gate)

按 v5.3 addendum 协议 · **v2 commit 后 · Kogami 签 GATE-P43-PLAN (v2) 前 · Executor 再次调 Codex**：

**Prompt 摘要：**
> 你是 Codex GPT-5.4 xhigh · 第二轮评审 Well Harness P43 milestone plan v2。v1 你返 "需阻止"（6 structural counters A-F）· Kogami 选路径① · Executor 重写 v2。请审 v2 是否真正消化 6 个 counter：
> (1) Counter A（伪库存）→ C7 + P43-01 Contract Proof Spike 是否足够？
> (2) Counter B（二代 orchestrator）→ C8 + non-goal #10 + §2c 既有工作 inventory + §3d migration 契约是否足够？
> (3) Counter C（shadow truth engine）→ C9 + non-goal #11 + draft_design_state 定位是否足够？
> (4) Counter D（治理冲突）→ C10 + non-goal #12 + §1 + P43-09 + Q6 统一到 demonstrative 是否足够？
> (5) Counter E（workflow correctness）→ C11 + §3c workflow automaton 契约 scope 是否足够？
> (6) Counter F（self-audit 盲点）→ C12 + 6 新 counter 是否足够？
> 若还有结构性遗漏 · 给 ≤3 条最强反驳 + 缓解建议。
> 若 v2 覆盖充分 · 明示 "v2 可过 Gate" 并列 minor tweaks（若有）。

**Codex 输出处理：** 批判性消化 · 如再 "需阻止" · 走 v3 · 如 "可过 Gate" · 提交 Kogami 最终审。

---

## 11. 停点

**本 plan v2 不执行任何代码。三个停点：**

**停点 1**：v2 commit + branch push 后 · Executor 调 Codex re-review（v5.3 addendum 要求）
**停点 2**：Codex 返 "可过 Gate" 或 v3 · Executor 提交 Kogami 审 GATE-P43-PLAN (v2)
**停点 3**：Kogami 签 `GATE-P43-PLAN (v2): Approved` + Q1-Q10 仲裁 · 才启动 P43-01 的 P43-01-00-PLAN.md 起草

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum · 2026-04-20
**Revision:** v2 (post-Codex · path ① · 6 structural counters A-F integrated as C7-C12)
**Awaiting:** Codex re-review (self-initiated per v5.3) + `GATE-P43-PLAN (v2): Approved` (Kogami) + Q1-Q10 仲裁
**Verified-by:** codex-gpt54-xhigh (first-round adversarial review 2026-04-20 · verdict 需阻止 · 6 structural counters A-F integrated)

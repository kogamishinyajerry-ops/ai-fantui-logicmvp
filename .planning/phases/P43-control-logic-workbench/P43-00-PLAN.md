---
phase: P43
plan: P43-00
plan_revision: v4 (post-Codex-round-3 · path ① continuous remediation)
title: Control Logic Workbench end-to-end milestone — v4 · mechanize authority contract + close whitelist gaps
status: re-drafted · Awaiting GATE-P43-PLAN (v4) (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum
verified-by: codex-gpt54-xhigh (r1 需阻止 · r2 需修正·信号强 · r3 需修正·信号强 · cuts #1/#2 closed · cuts #3/#4 residual mechanized in v4)
scope_tier: Tier 1 · milestone-level
preconditions:
  - GATE-P42-CLOSURE Approved (Kogami 2026-04-20) → main at `a6521ca`
  - Kogami 2026-04-20 R4 指令：完整控制逻辑生成工作台
  - v1 (`81adf39`) → Codex r1 需阻止（6 counters A-F）
  - v2 (`aa8e03a`) → Codex r2 需修正·信号强（4 cuts：state.yaml 幻影 / P43-01 hard-freeze / draft_design_state authority / §3d touched+forbidden files）
  - v3 (`14131c4`) → Codex r3 需修正·信号强（cuts #1/#2 实修；cuts #3/#4 仍 paper-over：Q11 重开 authority · §3d 自撞 + 漏文件 + hardcode 开关留出口）
  - Kogami 2026-04-20 路径① 明示选择（×1 显式 + Executor 自启动 remediation iterations per v5.3 addendum）
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
  - **不引入 `state.yaml` 或任何新持久化文件**（Codex r2 cut #1）· persistence 只有 `workbench.js` localStorage workspace + `workbench_bundle.py` bundle/archive manifest 两源 · P43 不加第三源
  - **不允许 P43-01 以 "列出断裂" 为通过条件**（Codex r2 cut #2）· P43-01 必须 **证明 primitive 可绑定**（happy path 端到端实跑通过）· 未证明则 P43-02+ 自动冻结
  - **不允许 `draft_design_state` 写回 frozen spec**（Codex r2 cut #3）· 无论用户在 annotation / wiring / iteration 任何环节 · preview 状态不可逆向覆盖 frozen spec · 唯一回写通道是 "reiterate → 新一轮 freeze"
  - **不允许新增未列入 §3d touched-files list 或 Doc Deliverables Whitelist 的文件**（Codex r2 cut #4 + r3 residual）· 任何试图新建的 `workbench/orchestrator.py` / 新前端 shell / 新 archive root / 新持久化源均违 non-goal
  - **不允许在 `generate_adapter.py` 新增 domain hardcode** / 不允许暴露 "hardcode 开关"（Codex r3 · §3d whitelist 错项修正）· 既有 hardcode（`generate_adapter.py:255,448`）由 P43-01 登记为 known limitation · 处理走独立 future Phase
  - **Authority chain 不可重议**（Codex r3 · cut #3 mechanize）· `frozen spec` = 唯一 authoritative truth · `draft_design_state` = ephemeral UI preview · `generated adapter` = faithful emit of frozen spec · 三者权威顺序固化 · 不再作 open question · Q11 已删
  - **`demo_server.py` extend 边界固化**（Codex r3 · Q13 deleted）· 允许 add endpoint · 允许 field-additive + backward-compat 变更 · 禁止 rename / remove / 语义变更 既有 endpoint；规则嵌入 §3d whitelist
  - **`draft_design_state` authority contract 6 条规则（R1-R6）须可机械验证**（Codex r3 · cut #3 mechanize）· 每条规则有具体 CI / 静态扫 / 单元测试 pattern · P43-02 Exit Criteria 硬性要求 test 实装
---

# P43 · Control Logic Workbench milestone (v4) — mechanize authority + close whitelist gaps

## 0. TL;DR · v3 → v4 差异

Codex round-3 判 v3 "需修正·信号强"。v3 把 cut #1 / cut #2 关闭 · 但 cut #3 / cut #4 仍 paper-over。v4 是 path ① 连续 remediation · 把 Codex r3 指出的 7 个具体缺口机械化：

| Codex r3 残留 | v3 现状 | v4 机械化动作 |
|--------------|--------|-------------|
| Q11 重开 authority chain · 削弱 cut #3 | §3e R3 禁回写 · 但 Q11 选项 B 给放宽路径 | **删 Q11** · 提升 authority chain 为 non-goal（见新 non-goal 最后三条）· §3e 删"Kogami 可否决"语义 |
| Q13 `demo_server.py` 是伪问题 | §3d 已实质选 B | **删 Q13** · 提升为 non-goal |
| §3d "暴露 domain hardcode 开关" = 给 hardcode 留合法出口 | whitelist row 8 写 "暴露开关" | **删此 row** · 改为 non-goal "不允许新增 hardcode"；既有硬编码由 P43-01 登记为 known limitation |
| §3d 漏文件：`workbench.css` / `ai-doc-analyzer.js` / 文档锁文件 / schema+test 文件 | 8 个 entry · 缺 CSS/分析器 JS/docs/schema | **§3d 补齐** · 加 4 前端/schema/test entry；新增 "Doc Deliverables Whitelist" 专门分类（含 docs/P43-*.md 4 件 + machine-readable yaml 2 件） |
| §3d 自撞：§3a/§8 要求新增 docs/P43-*.md · 但自家规则禁任何未列文件 | 内部矛盾 | **新增 Doc Deliverables Whitelist** 显式授权 4 份 docs/P43-*.md 新建 |
| §3d API shape 规则不清（"schema field OK" 与 "endpoint request/response 禁改" 冲突） | 语义歧义 | **§3d 语义收紧** · 加 "field additive + backward-compat OK · 语义变更 / removal / rename 禁止" 三级阶梯 |
| §3e R1-R5 是 prose 不是 CI/test 契约 | 6 条规则只有 R6 可测 | **§3e 每条加 "Verification" 列** · 具体 CI / 静态扫 / test pattern · R1-R5 必须 P43-02 Exit Criteria 落地可执行 test 验证 |

加上 Codex r3 指出的自夸 language "C13-C15 覆盖 round-2 遗漏"：v4 明示 C13-C15 只是新增 blind spot · 不是 r2 三问 closure；r2 三问 closure 已由 non-goal + §3e mechanized · 不依赖 C13-C15。

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

### 3d · Existing workbench migration 契约 · whitelist / blacklist / Doc Deliverables（Codex r2 cut #4 + r3 residual）

P43-02-00-PLAN.md 前置必备章节。**v4 三级阶梯：**

#### Source Code Whitelist（允许 extend · 三级阶梯规则 · 违反 = P43 violation · CI 静态扫必 reject）

**三级阶梯（Codex r3 API shape 歧义修正）：**

1. **L1 · Additive（完全允许）**：加 subcommand / 加 endpoint / 加 optional manifest field（带 migration default）/ 加 localStorage key（带 default 回退）/ 加 DOM section
2. **L2 · Backward-compat（允许 · 附约束）**：既有 field 可以加 optional nested subfield 但不能改现有 field 含义 / 既有 endpoint 请求 body 可以加 optional param 但不能改必传参语义 / 响应 shape 可加 field 但不能 remove 或 rename
3. **L3 · Breaking（全禁）**：rename / remove / 语义变更 / 必传参签名变更 / 响应 field removal

**文件清单（12 · v4 新增 4 项）：**

| 文件 | L1 允许 | L2 允许（需 migration path） | L3 禁止 |
|------|--------|----------------------------|---------|
| `src/well_harness/cli.py` | 加 subcommand（`workbench new / continue / status`） | 既有 subcommand 加 optional flag | 改 `bundle` / `archive` 语义 |
| `src/well_harness/workbench_bundle.py` | 加 optional manifest field | 既有 field 加 nested subfield | 改 field 含义 / remove / rename |
| `src/well_harness/static/workbench.js` | 加 localStorage key | 既有 key 加 subfield | 改 key 含义 / rename |
| `src/well_harness/static/workbench.html` | 加 DOM section | 既有 section 加子节点 | 改 structure 破坏现有 selectors |
| `src/well_harness/static/workbench.css` **(v4 新增)** | 加 rule / 加 class | 既有 class 加 property | 改 class 语义 / remove |
| `src/well_harness/static/ai-doc-analyzer.html` **(v4 新增)** | 加 DOM section | — | 改 structure |
| `src/well_harness/static/ai-doc-analyzer.js` **(v4 新增 · P43-01 必须触及)** | 加 reader / 加 panel | 既有 reader 加 fallback path | 改 reader 契约 |
| `src/well_harness/static/ai-doc-analyzer.css` **(v4 新增)** | 加 rule | 既有 class 加 property | 改 class 语义 |
| `src/well_harness/demo_server.py` | 加 `/api/workbench/*` endpoint | 既有 endpoint 加 optional param / response field | rename / remove / 语义变更 |
| `src/well_harness/ai_doc_analyzer.py` | 加 PDF/DOCX server-side reader | 修 `blockers`/`blocking_reasons` bug（P43-01 必修） | 不相关重构 |
| `src/well_harness/document_intake.py` | 加 clarification ID 契约 | 既有 gate 加 optional field | 改 intake gate 语义 |
| `src/well_harness/tools/generate_adapter.py` | — | 接受 frozen spec input 的 kwargs 扩展 | **新增 domain hardcode · 暴露 "hardcode 开关" · 改 adapter emit shape**（v4 收紧 · 删 v3 错项） |

#### Doc Deliverables Whitelist（P43 必须新建的 docs/ 文件 · 显式授权 · 防 §3d 自撞）

v3 规则"未列入 touched-files 则 violation"与 §3a/§8 要求新建多份 docs/P43-*.md 自撞。v4 显式授权：

| 新建文件 | 负责 Phase | 用途 |
|---------|----------|------|
| `docs/P43-contract-proof-report.md` | P43-01 产出 | primitive API 契约 + 真实断裂清单 + asserted-pass 证据 |
| `docs/P43-api-contract-lock.yaml` | P43-01 产出 | `/api/workbench/*` endpoint contract lock（便于回归测） |
| `docs/P43-workflow-automaton-contract.md` | P43-02 产出 | state enum + event list + transition table + error taxonomy |
| `docs/P43-workflow-automaton.yaml` | P43-02 产出 | machine-readable 版本（runtime state validation 用） |
| `docs/P43-authority-contract-verification.md` | P43-02 产出 | §3e R1-R6 每条的 CI / test 方案 |
| `docs/P43-archive-compat-report.md` | P43-02 产出 | 既有 archive 向 P43 restore 回归报告 |

其他 docs/ 文件新建 = violation（防 doc 蔓延）。

#### Test Whitelist（允许新建的 tests/ 文件）

| 新建测试 | 负责 Phase | 用途 |
|---------|----------|------|
| `tests/test_p43_doc_analyzer_blocker_fix.py` | P43-01 | `blockers`/`blocking_reasons` regression |
| `tests/test_p43_authority_contract_r1_r6.py` | P43-02 | §3e R1-R6 机械验证（见下） |
| `tests/test_p43_workflow_automaton.py` | P43-02+ | state machine contract verification |
| `tests/test_p43_archive_backward_compat.py` | P43-02 | 既有 archive restore 回归 |
| `tests/test_p43_api_contract_lock.py` | P43-02 | `/api/workbench/*` endpoint shape 回归 |
| `tests/test_p43_multi_tab_lock.py` | P43-02 | C13 cross-tab lock 场景 |

其他 tests/ 文件新建需 Executor 判是否合理 · 超出列表须加 §3d 更新。

#### JSON Schema Whitelist（允许扩展的 docs/json_schema/*.schema.json）

| 允许修改（L2 backward-compat only） |
|----------------------------------|
| `docs/json_schema/workbench_bundle_v1.schema.json` — 加 optional field OK · 禁 required field / remove |
| `docs/json_schema/workbench_archive_manifest_v1.schema.json` — 加 optional field OK · 禁 required field / remove |
| `docs/json_schema/controller_truth_adapter_metadata_v1.schema.json` — **冻结**（P42 已锁 · $id 不 bump · P43 不触） |

#### Blacklist（明确禁止新建 · 任何新建 = violation · CI 静态扫 reject）

- ❌ 新建 `src/well_harness/workbench/orchestrator.py` 或任何 `workbench/` 目录下新文件（orchestration 能力走 cli.py）
- ❌ 新建 `state.yaml` / `workflow.db` / 任何新持久化源（persistence 只有 localStorage + bundle manifest · non-goal #15）
- ❌ 新建前端 SPA shell / 替换 `workbench.js` 框架（vanilla JS 继承）
- ❌ 新建 `archive/workbench/{system_id}/` 目录结构（走 `archive_workbench_bundle`）
- ❌ 新建 `src/well_harness/workflow_engine.py` 或类似独立 workflow runtime
- ❌ 新建 `src/well_harness/draft_truth.py` 或类似 shadow truth engine（见 §3e · non-goal #11）
- ❌ 在 `generate_adapter.py` **新增** domain hardcode 或暴露 "hardcode 开关"（v4 新增 · Codex r3 修正）
- ❌ 新建 JSON schema 文件或 bump 现有 $id（P42/P38 已锁）

#### 兼容性验收（P43-02 Exit Criteria）

- 既有 `archive_workbench_bundle` 产的 archive 必须无损 restore 到 P43 flow · 不需 migration script
- 既有 `workbench.js` localStorage v1 数据（若存在）必须兼容读 · 或有明确 migration 函数
- 既有 `/api/workbench/*` endpoint 回归 100% pass（contract lock 对比）
- 既有 `docs/json_schema/*_v1.schema.json` validator suite 100% pass（所有既有 archive 依然 validate）

### 3e · `draft_design_state` authority contract · 机械约束（Codex r2 cut #3 · r3 mechanized in v4）

**身份定义：** `draft_design_state` 是 P43-05/P43-06/P43-08 的临时预览状态 · 存于 `workbench.js` localStorage · key = `wellHarnessWorkbench.v1.draftDesignState.{system_id}`。

**v3 → v4 变化：** 每条规则加 **Verification** 列 · 给出具体 CI / 静态扫 / 单元测试 pattern · R1-R5 必须由 `tests/test_p43_authority_contract_r1_r6.py` 机械验证（P43-02 Exit Criteria 硬性）。v3 "Kogami 可否决" 语义删 · authority chain 固化为 non-goal（见 non-goals 最后三条）· Q11 已删。

**6 条机械规则（v4 加 Verification）：**

| 规则 | 机械约束 | Verification（机械验证 pattern） |
|-----|---------|------------------------------|
| R1 · 写权限白名单 | 只有 UI Step 3/4/6 写 `draftDesignState` · 后端 forbidden 写 | **静态扫**：grep `src/well_harness/*.py` 无 `draftDesignState` 字面量 writer；`demo_server.py` 所有 handler 函数 AST 扫无写 localStorage/draft 对象。**单元测试**：`test_r1_backend_no_draft_write` — fake intake + run all server endpoints · assert `draft_design_state` key 未被 server 侧 side-effect 写入 |
| R2 · 读权限白名单 | Step 8 Final Approval 不读 draft · 只读 frozen spec | **静态扫**：`workbench.js` 的 Final Approval handler 代码块内 grep 无 `draftDesignState` 读取。**单元测试**：`test_r2_final_approval_reads_frozen_only` — mock window scope · trigger Final Approval · assert `localStorage.getItem('draftDesignState')` 未被调用（spy 计数 = 0）· `frozen_spec` 被读取 |
| R3 · **回写 frozen spec 禁止** | 无任何自动回写路径 · 唯一路径：reiterate → Freeze | **静态扫**：`workbench.js` 全文 grep 无 `frozenSpec = draftDesignState` / `frozenSpec.merge(draft)` / `frozenSpec.assign(draft)` pattern。**单元测试**：`test_r3_no_draft_writeback` — 写 draft 数据 · trigger wire_change/annotate/iterate events · assert frozen spec SHA 未变。**Integration test**：`test_r3_reiterate_must_rewalk_freeze` — 用户点 reiterate · assert workflow state 回到 `PARSING` 或 `AWAITING_ANSWERS` · 非直接到 `FROZEN` |
| R4 · generator 消费规则 | `generate_adapter.py` 只读 frozen spec · 不读 draft | **静态扫**：`src/well_harness/tools/generate_adapter.py` AST 扫无 `draftDesignState` / `draft_design_state` 任何引用。**单元测试**：`test_r4_generator_reads_frozen_only` — 喂 generator 一份 frozen spec + 一份 draft · assert generator 输出 hash 只依赖 frozen spec · draft mutation 不影响输出 |
| R5 · 冲突自动拒绝 | validator 位置：`src/well_harness/static/workbench.js` `validateDraftAgainstFrozen()` 函数 · 输入：`{draft, frozen}` · 输出：`{ok: bool, conflicts: [{type, draft_ref, frozen_ref, message}]}` · 失败码：`DRAFT_REFERENCES_DELETED_COMPONENT` / `DRAFT_CYCLE` / `DRAFT_TERMINAL_UNIQUENESS_VIOLATION` / `DRAFT_FAN_OUT_EXCEEDED` | **单元测试**：`test_r5_validator_conflict_detection` — 构造 4 种冲突场景 · assert 每种都返对应失败码 + 冲突 ref 正确。**UI 测试**：`test_r5_ui_shows_conflict_on_reiterate` — trigger reiterate with conflicting draft · assert UI 渲染 validation-error panel with 冲突清单 |
| R6 · Lifecycle boundary | Final Approval → `draft_design_state` key 立即删 · archive 不含 draft | **单元测试**：`test_r6_final_approval_deletes_draft` — trigger Final Approval · assert `localStorage.getItem('draftDesignState')` 返 null。**Integration test**：`test_r6_archive_excludes_draft` — 完整流程 · inspect `archive_workbench_bundle` manifest 与 bundle · assert 无 `draftDesignState` key 或 reference |

**Observability 要求（mechanized）：**

- `draft_design_state` 每次写入必须调 `logDraftWrite(writer_step, timestamp, diff_summary)` · 集中到 `workbench.debug.js` 日志面板 · **Verification**: `test_observability_logs_every_draft_write`
- UI 显示 "draft vs frozen" diff badge · DOM selector `#draft-frozen-diff-badge` 存在 · CSS class 显示当前状态 · **Verification**: `test_draft_frozen_badge_renders`

**Authority chain（non-negotiable · v4 升为 non-goal · Q11 已删）：**

```
frozen spec (authoritative · 唯一 truth · 唯一持久化到 registry)
    ↓ (只读 · R4 · generator 契约)
generated adapter (faithful emit of frozen spec only)
    ↓ (只读 · manifest 固化)
registry row + truth_level=demonstrative + status=Upgrade pending
```

```
draft_design_state (ephemeral UI preview · 非 truth · 非 persistable · R6 生命周期 Final Approval 后即删)
    ↓ (无写回路径 · R3 静态扫守 · R5 validator 守)
reiterate event → 回 Step 2c Freeze (重走 Q&A) → 新 frozen SHA
```

**P43-02 Exit Criteria（硬性）：**

- 所有 R1-R6 verification test 存在 · 在默认 lane 跑通
- 静态扫规则落地为 pre-commit hook 或 CI job（`tools/check_authority_contract.py` · Doc Deliverables Whitelist 授权新建）· 见 `docs/P43-authority-contract-verification.md` 实装说明

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

## 5. Tier 1 对抗性自审 · v4（C1-C12 保留 + C13-C15 · 不是 r2 closure · 只是新增 blind spots）

**v4 诚实声明（Codex r3 tick-box 指正）：** C13-C15 不是 round-2 三问（authority chain / PDF-DOCX / `demo_server.py`）closure。那三问 closure 已由 non-goals（倒数 3 条）+ §3e R1-R6 mechanized verification + §3d L1/L2/L3 阶梯完成 · 不依赖 C13-C15。C13-C15 只是 v3 引入的新 blind spots。

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

## 6. Open Questions · v4 · Kogami 签 GATE-P43-PLAN (v4) 时仲裁

**v4 追加清理（Codex r3 伪 Q 判定）：** 删 Q11（authority chain 重议会削弱 cut #3 · 已升为 non-goal）· 删 Q13（`demo_server.py` 边界已由 §3d L1/L2/L3 阶梯 + non-goal 锁死 · 无选项空间）。

**v3 清理 v2 伪 Q（保留）：** 删 Q3 / Q5 / Q6 / Q9。Q10 保留为 minor config。

**保留真 Q（v4 = 6 条）：**

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

### ~~Q11（v3）~~ — 删除（v4 · Codex r3 修正）
`Authority chain 预设确认` 被升为 non-goal（见 non-goals 倒数第 3 条）· `frozen spec` 唯一 truth + `draft_design_state` ephemeral preview + R3 禁回写 → 不再作 open question · §3e mechanized verification 全部落地。

### Q12 · PDF/DOCX authoritative 抽取路径（v3 保留 · v4 对齐 §3d whitelist）
- A · 浏览器端（`ai-doc-analyzer.js readAsText`）· 当前代码路径 · 对 binary 静默失败
- **B · 服务端（`ai_doc_analyzer.py` 加 PDF/DOCX reader 用 pypdf + python-docx）· P43-03 实现**（**推荐 · 浏览器端只负责 upload + preview · 落点：§3d whitelist 的 `ai_doc_analyzer.py` L1 "加 PDF/DOCX server-side reader"**）
- C · 双路径（浏览器 fallback · 服务端 canonical）· scope 过大
- OCR 允许与否：
  - **a · 不允许**（**推荐 · 默认 · 非可印刷 pdf 被 reject** · 防 scope 蔓延）
  - b · 允许（需第三方如 tesseract · scope 蔓延）
- SHA 绑定：canonical text SHA 与原 binary SHA 分开登记 · 二者都入 manifest · **Verification**: `test_p43_dual_sha_manifest`
- **Executor 建议：B + a**

### ~~Q13（v3）~~ — 删除（v4 · Codex r3 修正）
`demo_server.py extend 边界` 被升为 non-goal（见 non-goals 倒数第 2 条）· §3d L1/L2/L3 阶梯已 mechanized · 无 option space。

---

## 7. Execution sequencing · v4

```
P43-00 v4 plan commit + Codex round-4 re-review + Kogami GATE-P43-PLAN (v4) Approved + Q1/Q2/Q4/Q7/Q8/Q10/Q12 仲裁（Q11/Q13 已删为 non-goal · Q3/Q5/Q6/Q9 继续删）
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

## 8. Milestone-level Exit Criteria（v4）

1. 用户旅程 10 step 端到端 demo 跑通（真实 pdf/docx 输入 · 真实 archive 输出）
2. P43-01 Contract Proof Spike asserted pass（非"列伤"）
3. `ai_doc_analyzer.py` `blockers`/`blocking_reasons` bug 已修 + regression test land
4. `docs/P43-contract-proof-report.md` + `docs/P43-api-contract-lock.yaml` 存在 · Kogami 审过
5. `docs/P43-workflow-automaton-contract.md` + machine-readable yaml 存在（Q10=B）
6. `docs/P43-authority-contract-verification.md` 存在 · R1-R6 每条验证方案落地（v4 新增 · cut #3 mechanize）
7. `docs/P43-archive-compat-report.md` 存在 · 既有 `archive_workbench_bundle` manifest 无损 restore 到 P43 flow（C14 兼容性）
8. 既有 `/api/workbench/*` endpoint contract lock 回归测试 100% pass（C15）
9. P43 产出的 adapter 全部落 `demonstrative + Upgrade pending`（C10 唯一治理线）
10. 无并行"第二套 orchestrator"代码存在（§3d blacklist · `tools/check_authority_contract.py` CI 守）
11. **无 `state.yaml` 或新持久化源存在**（v3 cut #1 · non-goal #15 · CI 静态扫守）
12. **`draft_design_state` 6 条 authority rule 全有 `tests/test_p43_authority_contract_r1_r6.py` 通过的 mechanical test**（v4 cut #3 mechanize · 非 prose）
13. §3d Source Code Whitelist / Doc Deliverables Whitelist / Test Whitelist / Blacklist 全无 violation（v4 cut #4 mechanize · CI 静态扫守）
14. `generate_adapter.py` **无新增** domain hardcode（v4 · 既有 `:255,448` 登记为 known limitation）
15. Multi-tab lock test pass（C13 · `tests/test_p43_multi_tab_lock.py`）
16. Codex review 必调触点全调用 · 证据 trailer 在 commits
17. Appendix A 完整（用户所有 open question 已 resolve）
18. User Final Approval 流程走通 · 用户 alias + 注释入 manifest

---

## 9. v5.2 + v5.3 compliance（v4）

继承 v3 + 更新：
- **R3 Tier 1 adversarial · 15 counters C1-C15 · C7-C15 verified-by codex-gpt54-xhigh**
- **v5.3 addendum hard rule · Codex re-review 协议 v4**：
  - round 1 (v1 → v2) · verdict 需阻止 · 6 counters A-F
  - round 2 (v2 → v3) · verdict 需修正·信号强 · 4 必补 cut
  - round 3 (v3 → v4) · verdict 需修正·信号强 · cuts #1/#2 closed · cuts #3/#4 residual
  - **round 4 (v4 pending)**：v4 commit 后 · Kogami 签 Gate 前 · Executor **再次调 Codex** 审 v4 是否真正机械化 cuts #3/#4 residual
- Codex 三轮输出均入 `09C 外部审查简报` · verified-by trailer 随每版 commit

---

## 10. Codex re-review plan (v4 · round 4 · pre-Gate)

**Prompt 摘要：**
> 你是 Codex GPT-5.4 xhigh · 第四轮评审 Well Harness P43 milestone plan v4。round 3 verdict 需修正·信号强 · cuts #1/#2 closed · cuts #3/#4 residual。v4 声称把 cuts #3/#4 mechanized：
> (A) Q11 删了（authority chain 升为 non-goal · 不再作 open question）· cut #3 authority contract 是否真机械闭环？
> (B) Q13 删了（demo_server.py 边界升为 non-goal + §3d L1/L2/L3 阶梯）· 是否真机械？
> (C) §3d whitelist 补了 workbench.css / ai-doc-analyzer.js / docs/P43-*.md（Doc Deliverables Whitelist）/ tests/*.py（Test Whitelist）/ json_schema 规则 · 是否还漏？
> (D) §3d "暴露 domain hardcode 开关" 删了 · 改为 non-goal + blacklist 禁止新增 hardcode · 既有登记 known limitation · 是否真收口？
> (E) §3e R1-R6 每条加 Verification 列（静态扫 / 单元测试 / integration test 具体 pattern）· 是否真 CI-enforceable？还是仍是 prose 包装？
> (F) §5 tick-box 自夸删了 · 改诚实声明 C13-C15 只是新 blind spot · 是否可接受？
> 若 v4 覆盖充分 · 明示 "v4 可过 Gate"。若还有结构性残留 · 给 ≤3 条最强反驳 + 建议走 v5 或 R4 撤回。

**Codex 输出处理：** 批判性消化 · 若 "可过 Gate" 交 Kogami 审 · 若还"需修正·信号强" 走 v5（path ① 继续 · 但须评估 diminishing returns）· 若"需阻止" 考虑 R4 撤回 P43。

---

## 11. 停点

**本 plan v4 不执行任何代码。三个停点：**

**停点 1**：v4 commit + branch push 后 · Executor 调 Codex round-4 re-review（v5.3 addendum 要求）
**停点 2**：Codex 返 "可过 Gate" → 提交 Kogami 审 GATE-P43-PLAN (v4) · 否则继续 path ① 或升级 R4 决策给 Kogami
**停点 2.5（v3 引入 · v4 保留 · 硬规则）**：P43-01 Exit Criteria 未 asserted pass · P43-02+ 自动冻结 · 不可绕过
**停点 3**：Kogami 签 `GATE-P43-PLAN (v4): Approved` + Q1/Q2/Q4/Q7/Q8/Q10/Q12 仲裁 · 才启动 P43-01-00-PLAN.md 起草

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed + v5.3 addendum · 2026-04-20
**Revision:** v4 (post-Codex-round-3 · path ① continuous · cuts #1/#2 closed · cuts #3/#4 mechanized)
**Awaiting:** Codex round-4 re-review + `GATE-P43-PLAN (v4): Approved` (Kogami) + 7 Q 仲裁
**Verified-by:** codex-gpt54-xhigh (r1 · 6 counters A-F · r2 · 4 cuts · r3 · cuts #1/#2 closed + #3/#4 residual identified)

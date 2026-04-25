# E11 — Workbench Engineer-First UX Overhaul (PLAN)

> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> **Date:** 2026-04-25
> **Governance:** v6.1 (DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT)
> **Trigger:** Kogami 2026-04-25 verbatim — "你现在的项目工作台，如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难，没有清晰的指引，面板操作困难，设计不够简约……深度思考解决方案。"
> **Truth-engine red lines:** unchanged — `controller.py` / 19-node / 4 logic gates / `adapters/` 全程不动。

---

## 0. Goal Statement

把 `/workbench` 从 Epic-06..10 留下的"功能完整但无引导的脚手架"重做为**真飞机控制逻辑工程师在 30 分钟内能产出第一份有用工作的工具**，且整个改造**完全不触碰真值层**（所有红线维持）。

成功标准（goal-backward verifier）：
1. 一个第一次接触 Workbench 的飞机控制工程师，**不读代码、不看 HANDOVER**，凭页面 affordance 能在 30 分钟内独立完成：(a) 选一个 wow-scenario 跑通，(b) 在某个 logic gate 边上贴一条 domain-anchored annotation，(c) 把这条 annotation 转成 Claude Code prompt 输出给同事。
2. Codex persona review BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2/persona。Tier 决定 + Tier-B persona 选取规则按 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger（canonical）。本 plan 不重述规则。
3. main 三轨绿（default ≥ 863 / e2e 27 passed / adversarial 8/8）。
4. truth-engine 红线 0 触碰。
5. **(v2.3) 每个子 phase 的 user-facing copy 在 §Surface Inventory 全数登记**，锚点 line 真实存在；评审者抽查 1-3 行命中率 100%。

---

## 1. Current State — 反向 audit (probed 2026-04-25, main HEAD eea8065)

| 维度 | 现状 | 工程师视角问题 |
|---|---|---|
| 页面入口 `/workbench` | 1078 行 HTML / 1717 行 CSS / 3754 行 JS / 22 个 data-attributed widgets | 信息密度过高，无层级 |
| 页面身份 | 同一页 2 个 `<h1>`：上半 "Control Logic Workbench" (Epic-06 shell) + 下半 "Workbench Bundle 验收台" (旧 bundle 页) | 分裂的产品身份，工程师无法分辨"我在哪" |
| 三列抽象 | "Scenario Control" / "Spec Review Surface" / "Logic Circuit Surface" | UI surface 命名，不是工程师任务命名 |
| Annotation 词汇 | "Point / Area / Link / Text Range" | 通用 UI primitive，无领域含义；工程师不会自然说"在 logic3 上 point" |
| 入口 button 标签 | "Load Active Ticket" / "Snapshot Current State" / "通过并留档" / "阻塞演示" / "快速通过" / "留档复跑" | 动作明显但无 `WHEN` 提示，混杂中英 |
| 角色提示 | `data-role="ENGINEER"` 在身份 chip 上 | 没有 affordance 反映 ENGINEER 实际能/不能做什么 |
| Approval Center | "Kogami Proposal Triage" 三个 lane (Pending/Accept/Reject) | 非 Kogami 角色看到 disabled UI 无解释 |
| 主流程进度 | `<aside id="annotation-inbox">` Review Queue 是个空 skeleton | 工程师不知道 annotation → proposal → ticket → PR 整条链路是怎么走的 |
| 红线告知 | 无任何 UI surface 告诉工程师"controller.py / 19-node 是只读的，你只能 propose 不能 commit" | 工程师可能误以为 button click 会改 truth；没有契约可视化 |
| Domain anchoring | wow_a/wow_b/wow_c 三个 demo scenarios 在 `docs/demo/` 但 UI 上没有"从已知场景开始"按钮 | 工程师必须自己造 lever 输入；高门槛 |
| State-of-the-world | 没有顶部 status bar 显示当前真值引擎版本、最近一次 e2e 结果、known issues | 工程师必须读 HANDOVER 才能判断 baseline 健康度 |

> **方法论备注**：以上数字均来自 `wc -l src/well_harness/static/workbench.html` 等真实 grep（满足 v6.1 EMPIRICAL-CLAIM-PROBE rule）；UI surface 的"22 widgets"来自 `grep -c "data-annotation-tool\|data-approval-action\|workbench-collab-"` 实测。

---

## 1.5 Surface Inventory（v2.3 UI-COPY-PROBE 强制）

> 凡本期引入或修改 user-facing copy（tile / label / empty state / tooltip / modal / banner / onboarding），
> 在此逐条登记，触发 v2.3 UI-COPY-PROBE。叙述形容词不登记，可定位声明必登记。
>
> 每个子 phase 结束前，必须在该子 phase 的 PR body 或专属 SURFACE-INVENTORY.md 里补完此表。
> E11-02 的 worked example 见 `E11-02-SURFACE-INVENTORY.md`。

### Format（每行一个 claim）

| # | Copy 出处 (file:line) | Claim 摘录 (≤40 字) | 类别 | Anchor / Plan-ID | 状态 |
|---|---|---|---|---|---|
| 1 | static/<file>:L<n> | "<claim>" | feature-name / field-name / behavior / role-gate / data-source / format-spec / limit / surface-location | src/<file>:L<n> 或 E11-XX | [ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE] |

### 字段约束
- **Copy 出处**：必填，file:line 必须落到本期 PR diff 内的具体行
- **Claim 摘录**：必填，剥离修饰只留可验证骨架
- **类别**（枚举）：feature-name / field-name / behavior / role-gate / data-source / format-spec / limit / surface-location
- **Anchor / Plan-ID**：[ANCHORED] 必填 src 锚点 file:line；[REWRITE] 必填 Plan-ID（如 E11-04 / E12-01）；[DELETE] 留 "—"
- **状态**（枚举）：[ANCHORED] / [REWRITE → planned for <Phase-ID>] / [DELETE]

### 总计
- ANCHORED: <N1>
- REWRITE-as-planned: <N2>  ← 写入 commit trailer
- DELETE: <N3>

### 审查锚（给 Codex / 评审者）
- 评审者从本表抽查任意 1-3 行的 src 锚点真实性
- 表为空或与本期 copy diff 行数明显不匹配 → CHANGES_REQUIRED，不进入逐条 ripgrep

---

## 2. Personas（5 个，将作为 Codex review pipeline 输入）

| ID | Persona | 背景 | 目标 | 上手 ≤ 30 分钟需要做到 |
|---|---|---|---|---|
| P1 | **Junior FCS Engineer (3-month hire)** | 航空控制专业本科 + 入职 3 月，会 Python，未读过本仓库代码 | 学习 reverser 控制链路，跑通一次 wow 场景 | 找到 Workbench 入口、选 wow_a、看到 logic1→4 因果链亮灯、贴一条 annotation |
| P2 | **Senior FCS Engineer (10y reverser exp)** | 老航空控制工程师，带过 C919 反推方案，熟悉 R1-R5 invariants | 验证 logic3/4 阈值在边界 case 是否 spec-compliant | 改 lever 输入做 what-if、找到对应 invariant 的 spec 来源、贴 spec-cited annotation |
| P3 | **Demo Presenter (立项汇报现场)** | 项目经理 + 销售工程师双角色，10 分钟讲完 3 wow 场景 | 现场零摩擦走完 wow_a → wow_b → wow_c | 一键启动 demo、清晰故事弧、AI 叙述 fallback 时也能讲 |
| P4 | **QA / V&V Engineer** | 适航认证背景，关注 traceability + audit chain | 验证某条 logic3 行为对应的 requirement 文档 | 找到 requirement → controller 代码 → e2e 测试 的三段引用链 |
| P5 | **Customer Apps Engineer** | 一线工程师与客户对接 | 接到客户报告"L4 在 X 条件下行为异常"，转成 issue | 把客户描述映射到 Workbench probe 操作、产出 ticket payload 给 dev team |

每个 persona 在 §6 会有 distinct Codex prompt。

---

## 3. Sub-phase breakdown（按依赖顺序）

| Sub-phase | 内容 | 依赖 | Truth-engine 触碰? |
|---|---|---|---|
| **E11-01** | Persona journey maps + gap audit per surface — 输出 `JOURNEYS.md` 把 5 personas × 当前 11 维度展开成 55 个 cell，标记每个 cell BLOCKED / FRICTION / OK | 无 | 不 |
| **E11-02** | Onboarding 流：新增 `/workbench/start` 路由（或 modal）— 5 秒识别角色 → 推荐 3 个起手任务 → 一键进入对应工作流 | E11-01 | 不 |
| **E11-03** | 三列重命名 + 重排 — "Scenario Control / Spec / Circuit" → 工程师任务命名（候选：「Probe & Trace」「Annotate & Propose」「Hand off & Track」），保留底层 ID 不变以免 e2e 测试失效 | E11-01 | 不 |
| **E11-04** | Domain-anchored annotation 词汇升级 — UI 仍用 point/area/link/text-range 作为底层类型，但 button label + 工具说明转为「标记信号」「圈选 logic gate」「关联 spec」「引用 requirement 段」 | E11-03 | 不 |
| **E11-05** | Canonical scenarios 起手卡 — wow_a/b/c 在顶部以 starter card 出现，一键 POST `/api/lever-snapshot` 预填 BEAT_DEEP_PAYLOAD 等 | E11-01 | 不 |
| **E11-06** | State-of-the-world status bar — 顶部 1 行：truth-engine commit SHA · 最近 e2e 结果 · adversarial 8/8 状态 · open known-issues 数 | 无 | 不 |
| **E11-07** | Authority contract banner — 在 controller / circuit 周围加一条 "🔒 Truth Engine — Read Only · Propose 不修改" 永久 banner，链接 v6.1 红线条款 | E11-03 | 不（仅 UI banner，不动 code） |
| **E11-08** | 角色 affordance — 非 Kogami 角色看到 Approval Center 时显示 "Pending Kogami sign-off" 而不是 disabled UI | 无 | 不 |
| **E11-09** | 双 h1 修复 — 把旧 "Workbench Bundle 验收台" 整页迁到 `/workbench/bundle` 子路径，主 `/workbench` 只保留 Epic-06..10 shell | 无 | 不（仅前端路由，不动 demo_server 真值出口） |
| **E11-10** | Codex persona-review pipeline — 5 个 reusable prompts 落 `.planning/codex_personas/`，并跑首轮 review on E11-02..09 阶段产出 | E11-02..09 一一就绪后逐个跑 | 不 |
| **E11-11** | E2E coverage — 增 `tests/e2e/test_e11_workbench_onboarding.py` 锁住 onboarding flow 的关键 selector 不被改坏 | E11-02 | 不 |
| **E11-12** | CLOSURE — `E11-12-CLOSURE.md` + persona review summary + 三轨证据 + 自签 GATE-E11-CLOSURE: Approved (v6.1) | E11-01..19（除 E11-12 自身外的 18 项 closed） | 不 |
| **E11-13** | manual_feedback_override **trust-affordance 修复（UI/可视化层）** — 加警示 banner + 模式标识 chip + 失谐告警，让用户*看起来不再越权*。**不是** authority-chain breach 修复（873 + adversarial 8/8 已证 truth-engine 实际未被越权），而是 UI affordance 让用户对真值失去信任的"可视污染"修复。Opus 4.7 (2026-04-25) reframe；详见 §3.5。 | E11-01（P2-1 Reading B locked） | 不 |
| **E11-14** | manual_feedback_override **服务端 role guard** — `/api/lever-snapshot` 对 manual_feedback_override 增 actor + ticket-binding 检查，未签 sign-off 时端点返回 409 而不是 200（仍不动 controller）。配合 E11-13 形成"UI 看不到 + 服务端拒绝"两道防线。 | E11-13 | 不（adapter boundary 内的 endpoint 守护，不进 controller / models / adapters/*.py 真值出口） |
| **E11-15** | UI 字符串中文优先化 sweep — 全部 user-facing label / button 默认中文，英文降为 muted sublabel；保持底层 selector ID 不变 | E11-03 | 不 |
| **E11-16** | 服务端 approval endpoint 加固 — `/api/workbench/*` approval 类 endpoint 增 actor + ticket + artifact-hash 三元绑定，与 audit chain hash 链接（不动 controller） | E11-08 | 不 |
| **E11-17** | Presenter mode toggle — 一键隐藏 annotation / approval / dev chrome；narration fallback ribbon 在 AI 服务慢/down 时显示静态文案 | E11-02 | 不 |
| **E11-18** | 逐 logic-gate trace tuple 显示 — Logic Circuit Surface 上 L1–L4 各自挂 (requirement_id, test_id, artifact_hash) 三元；annotation schema 升级要求三元 | E11-04 | 不 |
| **E11-19** | Apps-engineer 客户视图 — customer 复现面板 + repro recipe 字段 + ticket schema enrichment + 重复 case 模糊搜索 | E11-04 | 不 |

> 红线维持: E11-01..19 全部仅触碰 `src/well_harness/static/workbench.{html,css,js}`、`src/well_harness/static/annotation_overlay.js`、`src/well_harness/demo_server.py`（仅 endpoint guard，不动 controller dispatch）、新增的 e2e 测试、新增的 `.planning/` 文档。**不进入** `controller.py` / `runner.py` / `models.py` (truth-bearing) / `adapters/` / wow_a fixture。

> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。

---

## 3.5 执行排序（Opus 4.7 strategic input · 2026-04-25）

> 数据源：Notion @Opus 4.7 异步会话，2026-04-25。审查范围 = E11-02 + v2.3 governance bundle 落地后的 strategic review。
> 完整 Opus 输出存档在 PR #11 description / Notion 04 决策日志 DB。

### 排序（next 6 sub-phases）

```
E11-09 → E11-13/14 → E11-05 → E11-03 → E11-04 → E11-06
```

**逐项理由**（Opus 4.7 verbatim）：

1. **E11-09 dual-h1 修复** — 30 秒 quick win，先清债（双 h1 是身份分裂遗债），同时作为 §3.6 leading indicator 量度 governance 摊销。
2. **E11-13 + E11-14 manual_feedback_override 修复** — 提前到第 2 而非第 3。**关键 reframe**: 不是 authority-chain breach（873 + adversarial 8/8 已证 truth-engine 没被越权），是 **UI affordance 让用户*看起来*越权**——比 demo BLOCKER 更污染信任。修复在 UI / 服务端 endpoint guard 两层，不进 controller。
3. **E11-05 wow 起手卡片** — 兜 P3 demo presenter 的 BLOCKER #1（presenter 找不到 wow 入口）。
4. **E11-03 三列重命名** — P1 / P2 工程师任务命名升级。
5. **E11-04 annotation 词汇升级** — P1 / P2 / P5 domain anchoring。
6. **E11-06 status bar** — 基础设施收尾。

### Opus 4.7 拒绝的备选

- **B（直接全做 P2-1 truth-boundary fix 链 + 其他都推后）**：拒绝。错在把"看起来越权"上升为 R1-R5 红线 fix——是过度反应。
- **C（先做 E11-12 closure 收 phase 再换新 phase）**：拒绝。18 子 phase 没做先 closure 是伪闭环。

### E11-15..19 的位置

不进 next-6 排序。Opus 4.7 把它们归为"E11 closure 前置纯前端期"——E11-09 ≤ 2 轮 APPROVE 后、E11-06 完成后再启动，期间可并发开纯 spec 类 E12（不动 src/）。

---

## 3.6 Leading Indicator · E11-09 ≤ 2 Codex 轮 = governance 摊销证据

> Opus 4.7 (2026-04-25) §1 governance weight 诊断输出。

**E11-09 是 governance machinery 是否过载的实证 gate**（已 fired 2026-04-25 — §3.6.1 OUTCOME 见下）：

| E11-09 Codex 轮数 | 解读 | Action（历史决策表） |
|---|---|---|
| ≤ 2 轮 APPROVE | v2.3 已摊销 — Surface Inventory 把 honesty 反射弧前置成功 | 软化 5-persona pipeline 改 tier-trigger（landed as `governance bundle #2`, PR #14, 2026-04-25） |
| 3 轮且 round-trip 仍围绕 honesty | process bloat 实锤 | 整组规则降一档（hypothetical：5-persona 直接降为 1-persona 默认 + 其他 v2.3 子条款重审） |
| ≥ 4 轮 | governance 失效，需要 Opus 4.7 再介入诊断 | 暂停 E11 子 phase 推进 + 起 retro |

**触发条件 (landed)**：see `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger (canonical). 本节仅记录"为什么这条规则被这样写"的 leading-indicator 决策弧；规则正文、tier 触发条件、Tier-B persona 选取规则、计数命令、回滚条件全部由 constitution canonical。本节不重述。

**保留不变**：v2.2 / v2.3 / v6.1 / Surface Inventory / RETRO 序号全部保留，**不动**。

**当时未在 §3.6 立法的原因**：Opus 4.7 警告"先 codify 再实证"是 v2.3 的同一陷阱。tier-trigger 规则有效性 *曾 取决于* E11-09 结果——E11-09 跑完前不写进 constitution。E11-09 ≤2 轮 APPROVE fired 后，governance bundle #2 才作为 PR #14 落 constitution（详见 §3.6.1）。

### 3.6.1 Leading Indicator OUTCOME — fired ≤2 rounds (2026-04-25)

E11-09 PR #13 落地 = **2 轮 Codex APPROVE**（R1 BLOCKER 真实 JS bug 被抓 + R2 CLEAN APPROVE）。R1 的 BLOCKER 不是 honesty 类（不是 fabricated surface claim），是**真实 runtime bug**（workbench.js 共享 shell + bundle 但 binding bundle-only 元素无 null guard），属于 reactive review 正常工作。

**Action 触发**：governance bundle #2 已通过 PR #14 落地（2026-04-25）：

- `.planning/constitution.md` v2.3 §Codex Persona Pipeline Tier-Trigger 子节添加
- `.planning/codex_personas/README.md` §Invocation 表替换默认 5-persona 规则
- 自此**所有** E11 后续子 phase（E11-13..19）默认按 tier-trigger 跑 Codex persona review，不再 5 个并行 by default

**Tier-trigger 落地后保留不变**：v2.2 / v2.3 触发 + §Surface Inventory + §Anchor 格式细则 + v6.1 Codex 触发清单 + RETRO 序号 + Hard Stop + Verbatim Exception。仅持 5-persona 调用频率被软化。

**回滚条件（canonical = RETRO-V61-054 §6.3，constitution v2.3 §Codex Persona Pipeline Tier-Trigger 引用）**：连续两个 Tier-B 子 phase 在 post-merge 检出 ≥1 条 fabricated surface（v2.3 §UI-COPY-PROBE §失效条件） → 自动执行三项动作：(1) 接下来 3 个 user-facing 子 phase 强制回滚到默认 5-persona（不允许 Tier-B），(2) 开新 RETRO-V61-* 文件记录失败摊销并链接到 RETRO-V61-054，(3) 重新 engage Opus 4.7 strategic review 决定是否永久退役 tier-trigger 或 sharpen 触发条件。

**详细记录**：`.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6.

---

## 3.7 E12 phase 并发开启条件（Opus 4.7 conditional No）

**目前状态**：E11 closure 前**不**开 E12 src/-touching 候选（fault diagnosis MVP / multi-system generalization / OpenFOAM 联合）。

**条件解锁**：满足全部 3 条后可并发启动一个**不动 src/** 的 E12 spec phase（如 fault diagnosis 的 PRD + intake packet schema）：
1. E11-09 ≤ 2 轮 Codex APPROVE（证 v2.3 摊销）
2. E11-06 完成（E11-15..19 进入纯前端期）
3. 该 E12 候选明确不动 `src/well_harness/{controller,runner,models,plant}.py` / `adapters/` / `tests/e2e/test_wow_a*`

**理由**：并发 src/ phase 会拉高 truth-engine 触碰风险且让"v2.3 摊销 vs bloat"归因失败（两个 phase 同时跑 Codex 会污染 leading indicator 数据）。

---

## 4. Tier-1 Adversarial Self-Review（v5.2 红线 #3 强制）

> 三个最强自我反对意见 + 显式 rebuttal。

### Counterargument #1: "为什么不让真工程师上手反馈再改？"

**反对论点**: pre-emptive UX 工作可能优化错的方向。等到第一个 customer-facing 工程师 onboard 时再迭代，更省成本，避免 design-by-imagination。

**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。

### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"

**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。

**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) anti-bias safeguard 是 tier-aware；canonical 定义见 `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger 和 `.planning/codex_personas/README.md` §Anti-bias safeguard。本 PLAN 不重述。结论：bias 风险存在但已通过 distinct context + canonical tier-aware anti-bias 机制 mitigated。

### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"

**反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。

**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 19 个 sub-phase（baseline review + Opus 4.7 amendment 后）各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。

### Counterargument C-UI: "本期 copy 里我是否写了一个 src/ 还没 ship 的 surface？"

**反对论点**（v2.3 立法后强制必答）: landing / tile / banner / tooltip 的 copy 是否描述了某个 feature / field / role-gate / behavior，而该 surface 在当前 commit 的 src/ 里其实不存在或只存在于计划态？

**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。

### Counterargument C-Opus: "我是否在 governance 投资曲线已经 over-process 的情况下还在加新规则？"

**反对论点**（Opus 4.7 strategic review 后强制必答）: v6.1 + v2.2 + v2.3 + 5-persona pipeline + Surface Inventory + RETRO 序号 = 短期内累积 6 项 process artefact。是否已经 process > delivery？

**Rebuttal stage**: Opus 4.7 异步审查（2026-04-25）独立判断"正好偏过 5–10%"，不需要回滚 v2.2/v2.3/v6.1，但 5-persona pipeline 该改 tier-trigger。**当时未立即立法 tier-trigger 的原因**：Opus 警告"先 codify 再实证"是反模式（同 v2.3 PR 5 轮 round-trip 的根因）。§3.6 leading indicator (E11-09 ≤ 2 轮 = 摊销证据) 已 fired (2026-04-25)，governance bundle #2 已通过 PR #14 落 constitution（详 §3.6.1）。Phase Owner 在每个新子 phase 启动前仍必答：(a) 本子 phase 触发哪些 governance trigger？(b) trigger 数量是否大于该子 phase 实际 LOC 改动？(c) 若 (b) 是 yes，先停下来重审 process。

---

## 5. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| 改 workbench.html 大量 selector 导致 e2e + adversarial 测试失败 | High | 每 sub-phase 末跑三轨；保留底层 `id` 和 `data-*` selector 不动，只改 visible label / class / 排版 |
| 新 onboarding flow 与已有 ticket 流程冲突 | Med | E11-02 的 `/workbench/start` 单纯是入口，导向已有按钮；不替换底层 prompt/ticket 逻辑 |
| Codex persona pipeline cost — Tier-A ≈ 5 × 10min ≈ 1h CPU；Tier-B ≈ 10min CPU（governance bundle #2 后默认 Tier-B） | Low | 后台跑（已有先例），Tier-A 时 5 并发；persona 失败 retry 1 次后转 manual review |
| 工程师在 Authority Contract banner 之外仍误以为可改 truth | Med | E11-07 banner + E11-04 annotation 词汇双重锁；同时不提供任何会让工程师以为"在 UI 改 truth-engine"的 affordance |
| 角色 affordance E11-08 暴露 Kogami-only 操作的 implementation detail | Low | 仅展示 "Awaiting Kogami sign-off" 文案，不暴露内部 actor 列表 |

---

## 6. Codex Persona Review Pipeline

详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：

1. **Persona 背景** — role / experience / mental model
2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings.
   - **Tier-A only:** 必须 ≥1 finding NOT covered by other 4 personas（within-PR uniqueness 反模式同质化）
   - **Tier-B:** within-PR uniqueness N/A（仅 1 persona 跑），anti-bias 由跨-sub-phase 轮换 + §Surface Inventory 承担（详见 §3.6.1 + constitution.md §Codex Persona Pipeline Tier-Trigger）
5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"

每轮 review 跑完后（tier-aware）：
- **Tier-A**: Claude Code 汇总 5 份 verdict 进 `E11-04-PERSONA-REVIEW-RESULTS.md`（aggregator 模式）
- **Tier-B**: 单 verdict 文件 `.planning/phases/<phase-id>/persona-<P?>-output.md` 即 review 记录（无 aggregator）
- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一（Tier-A 跨 5/5；Tier-B 该 1/1）

---

## 7. Sequencing & estimated effort

| Sub-phase | Type | LOC est | Time est | Codex required? |
|---|---|---|---|---|
| E11-01 | doc | ~300 | 30min | NO |
| E11-02 | code (HTML/JS) | ~200 | 1h | YES (UI 交互模式变更) |
| E11-03 | refactor (HTML/CSS) | ~150 | 45min | YES (UI 交互模式变更) |
| E11-04 | doc + code | ~100 | 30min | NO (mechanical relabel) |
| E11-05 | code (JS) | ~150 | 1h | YES (UI 交互模式变更) |
| E11-06 | code (HTML/JS) | ~120 | 45min | YES (新 API 调用 / 状态聚合) |
| E11-07 | code (HTML/CSS) | ~80 | 30min | NO (添加 banner，无逻辑) |
| E11-08 | code (JS) | ~60 | 30min | NO (单 conditional 文案) |
| E11-09 | refactor (routing) | ~200 | 1h | YES (路由变更 → 用户导航 mode) |
| E11-10 | doc | ~600 (5 prompts) | 1.5h | self-review only |
| E11-11 | test | ~150 | 1h | YES (新 e2e 期望) |
| E11-12 | closure | ~200 | 30min | YES (Tier 1 + persona summary) |
| E11-13 | code (HTML/CSS) | ~100 | 45min | YES (UI 交互模式变更 + manual mode trust 可视化) |
| E11-14 | code (Python endpoint guard) | ~80 | 1h | YES (server-side guard, adapter boundary 内) |
| E11-15 | refactor (HTML strings) | ~250 | 1.5h | YES (UI 字符串大改 + v2.3 §Surface Inventory) |
| E11-16 | code (Python) | ~120 | 1h | YES (approval endpoint 三元绑定) |
| E11-17 | code (HTML/CSS/JS) | ~180 | 1h | YES (presenter mode toggle = UI 交互模式变更) |
| E11-18 | code (HTML/JS) | ~150 | 1h | YES (logic-gate trace tuple + schema 升级) |
| E11-19 | code (HTML/JS + schema) | ~250 | 1.5h | YES (UI 交互模式变更 + ticket schema enrichment) |

**Total: ~3330 LOC across 19 sub-phases, ~15h sequential or ~5-6h with parallelism on independent ones.** (12-row baseline expanded to 19 per E11-01 baseline review + Opus 4.7 amendment, 2026-04-25.)

---

## 8. Verification protocol (E11 closure 前必跑)

| 维度 | 标准 | 锚点 |
|---|---|---|
| Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
| E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
| Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
| Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
| Codex personas | Tier-aware: Tier-A → 5/5 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0 across all 5; Tier-B → 1/1 verdict ∈ {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER=0. Tier 由 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 规则按当期 sub-phase 决定 | Tier-A: `E11-04-PERSONA-REVIEW-RESULTS.md`. Tier-B: `.planning/phases/<phase-id>/persona-<P?>-output.md` |
| Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
| EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |

---

## 9. CLOSURE 退出条件

E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：

1. ✅ §3 中 19 sub-phase 全部 merged 到 main（E11-01..19）
2. ✅ §8 verification protocol 全部通过
3. ✅ Codex persona review 给出 0 BLOCKER（tier 决定 + persona 选取规则 canonical = `.planning/constitution.md` §Codex Persona Pipeline Tier-Trigger）
4. ✅ truth-engine 红线 0 触碰
5. ✅ E11-12-CLOSURE.md 在 `.planning/phases/E11-workbench-engineer-first-ux/` 落地
6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria
8. ✅ 每个含 user-facing copy 的子 phase 已落 `<phase-id>-SURFACE-INVENTORY.md`（v2.3 §1.5 强制）
9. ✅ §3.6 Leading Indicator 决策已 land（E11-09 ≤ 2 轮 → governance bundle #2 软化 5-persona；否则记录 retro 后维持现状）

---

## 10. Open Questions（pending Kogami input · 不阻塞启动）

1. 5 personas 的 specific company / 项目 context 要不要 fictionalize？（默认: 是，避免暗示真实客户）
2. Onboarding flow 是 modal 还是单独路由？（默认: 单独路由 `/workbench/start`，可深链可分享）
3. 三列 verb 命名候选 "Probe & Trace / Annotate & Propose / Hand off & Track" 还是更激进的 "What-If / Mark / Hand off"？（默认: 前者，与现有 button 文案对齐）
4. 双 h1 修复时把旧 bundle 验收台搬到 `/workbench/bundle` 还是直接 deprecate？（默认: 搬到子路径，保留访问路径以免破坏旧 demo 习惯）
5. Authority Contract banner 是 sticky 还是 dismissable？（默认: sticky 在 truth-engine surfaces 周围，dismissable 在其他位置以免审美干扰）

> 本 phase 启动不依赖以上 Q 解决；Q 在 E11-01 journey map 阶段会迭代回到 plan 里 confirm。

---

## 11. Trailer

```
Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
```

> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 Codex review 结果（按 §3.6 + constitution §Codex Persona Pipeline Tier-Trigger 决出的 tier；Tier-A 全 5 verdicts / Tier-B 单 verdict）。

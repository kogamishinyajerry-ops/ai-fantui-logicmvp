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
2. 5 个 Codex personas 各自跑一次 review，BLOCKER 等级问题 = 0；IMPORTANT 等级 ≤ 2 个/persona。
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
| **E11-12** | CLOSURE — `E11-05-CLOSURE.md` + 5 personas review summary + 三轨证据 + 自签 GATE-E11-CLOSURE: Approved (v6.1) | E11-01..11 | 不 |

> 红线维持: E11-01..12 全部仅触碰 `src/well_harness/static/workbench.{html,css,js}`、`src/well_harness/static/annotation_overlay.js`、新增的 e2e 测试、新增的 `.planning/` 文档。**不进入** `controller.py` / `runner.py` / `models.py` (truth-bearing) / `adapters/` / wow_a fixture。

> **(v2.3) Copy 硬约束**: 本期 user-facing copy 必须在 §1.5 Surface Inventory 全数登记，未登记的 copy 改动视为越界。每个子 phase PR body 或同级 `<phase-id>-SURFACE-INVENTORY.md` 必须含完整表 + ANCHORED/REWRITE/DELETE 三类计数 + commit trailer `UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`。E11-02 已追溯补登 `E11-02-SURFACE-INVENTORY.md`，作为模板范例。

---

## 4. Tier-1 Adversarial Self-Review（v5.2 红线 #3 强制）

> 三个最强自我反对意见 + 显式 rebuttal。

### Counterargument #1: "为什么不让真工程师上手反馈再改？"

**反对论点**: pre-emptive UX 工作可能优化错的方向。等到第一个 customer-facing 工程师 onboard 时再迭代，更省成本，避免 design-by-imagination。

**Rebuttal**: (a) Kogami 在本对话明确说"如果让一个真正的飞机控制逻辑开发工程师上手使用，一定会是一个灾难"——这本身就是 senior reverser 工程师（Kogami 即是项目主导，背景=航空控制）的 first-hand 反馈，不是想象。(b) Codex 5 personas 提供 5 个独立审查视角，等同于"asynchronous beta-test"，不需要等真人。(c) 现在 Workbench 还没有外部用户，迭代成本 ≈ 0；上线后再改成本 = onboarding 中断 + 可能的口碑损失。结论：迭代时机 = 立即。

### Counterargument #2: "Codex 的 5 personas 会不会只是 confirm Claude 自己的 bias？"

**反对论点**: 同一个 LLM 模型扮演 5 个不同角色，本质上还是同一份 weights 在 reason，可能产出 5 份相似的 review。Tier 1 adversarial 要求 ≥3 reasoned objections + rebuttal，但 Codex 是 GPT-5.4，不是 Claude；模型多样性可能不够。

**Rebuttal**: (a) Codex 是 OpenAI GPT-5.4，与 Claude Opus 4.7 是不同 family，前次 PR #5 R1 review 已经实证捕到 Claude 漏的事实错误（plant deploy 6% vs 0%），证明 inter-model 盲点不重叠。(b) 5 personas 设计中刻意拉开 background：Junior（不会 Python deep dive 的）vs QA/V&V（会跑 traceability 的）vs Demo Presenter（不关心代码只关心叙事弧的）— context 拉开后即使是 same weights 也会 surface 不同 dimension。(c) 加 anti-bias safeguard：每个 persona 必须产出 ≥1 个其他 persona 没提到的 finding，否则 review 不算 valid（pipeline 强制项）。结论：bias 风险存在但已通过 distinct context + cross-persona uniqueness 要求 mitigated。

### Counterargument #3: "这是 Phase 还是单纯一个 UX iteration？"

**反对论点**: Epic-06..10 已经把 Workbench 完整交付，再开 E11 是不是 over-engineering？应该作为 Epic-06 的 follow-up minor PR 即可。

**Rebuttal**: (a) E11 跨 5 epic 的 UI surface（onboarding 跨 06，annotation 跨 07，approval 跨 08，prompt/ticket 跨 09，PR review 跨 10）— 单 PR 解决会变成 mega-PR；分 12 个 sub-phase 各自小 PR + Codex review，可控性更高。(b) E11 引入新 governance artefact (Codex personas pipeline)，本身值得 phase-level 文档 trace。(c) v6.1 Solo Autonomy 允许 Claude Code 自启 phase，不需要怕 phase 数量；过度细分 < 过度合并造成的回退困难。结论：用 Phase 是正确粒度。

### Counterargument C-UI: "本期 copy 里我是否写了一个 src/ 还没 ship 的 surface？"

**反对论点**（v2.3 立法后强制必答）: landing / tile / banner / tooltip 的 copy 是否描述了某个 feature / field / role-gate / behavior，而该 surface 在当前 commit 的 src/ 里其实不存在或只存在于计划态？

**Rebuttal stage**: 本期作者必须在 commit 前对每条 user-facing copy claim 执行 grep 回 src/ 的 sweep，结果登记到 §1.5 Surface Inventory，三选一处置（ANCHORED / REWRITE-as-planned / DELETE）。E11-02 4 轮 Codex round-trip（详 RETRO-V61-054）证明：缺这道反射弧时，Codex 会逐条 ripgrep 在 review 阶段揭穿，付出 4 轮代价；做完反射弧后 Codex 只需抽查 inventory 1-3 行真实性即可一轮 APPROVE。结论：每个含 user-facing copy 的子 phase 必填 §Surface Inventory，不能跳过。

---

## 5. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| 改 workbench.html 大量 selector 导致 e2e + adversarial 测试失败 | High | 每 sub-phase 末跑三轨；保留底层 `id` 和 `data-*` selector 不动，只改 visible label / class / 排版 |
| 新 onboarding flow 与已有 ticket 流程冲突 | Med | E11-02 的 `/workbench/start` 单纯是入口，导向已有按钮；不替换底层 prompt/ticket 逻辑 |
| Codex 5 personas pipeline 跑一轮 ≈ 5 × 10min ≈ 1h CPU 时间 | Low | 后台跑（已有先例），分 batch；persona 失败 retry 1 次后转 manual review |
| 工程师在 Authority Contract banner 之外仍误以为可改 truth | Med | E11-07 banner + E11-04 annotation 词汇双重锁；同时不提供任何会让工程师以为"在 UI 改 truth-engine"的 affordance |
| 角色 affordance E11-08 暴露 Kogami-only 操作的 implementation detail | Low | 仅展示 "Awaiting Kogami sign-off" 文案，不暴露内部 actor 列表 |

---

## 6. Codex Persona Review Pipeline

详细 prompts 见 `.planning/codex_personas/{P1..P5}.md`（在 E11-10 落地）。每个 prompt 包含：

1. **Persona 背景** — role / experience / mental model
2. **Mission** — "你是 Pn，你被叫来 review Workbench；你 30 分钟内的目标是 X"
3. **Workbench access** — 自己 boot demo_server :8799 + curl `/workbench` HTML + 实测 selector
4. **Required output** — Verdict (APPROVE / CHANGES_REQUIRED / BLOCKER) + 5-10 numbered findings + ≥1 finding NOT covered by other personas
5. **Anti-bias hook** — 在 prompt 末附 "若你产出的 findings 全是 surface 抱怨，重做：找一个 *contract-level* 风险（authority bypass、truth drift、role escalation 等）"

每轮 review 跑完后：
- Claude Code 汇总 5 份 verdict 进 `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md`
- 每个 finding ranked: BLOCKER → 必修 / IMPORTANT → 本 phase 修 / NIT → 进 next-phase queue
- BLOCKER 数为 0 是 phase CLOSURE 必要条件之一

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

**Total: ~2200 LOC across 12 sub-phases, ~9h sequential or ~3h with parallelism on independent ones.**

---

## 8. Verification protocol (E11 closure 前必跑)

| 维度 | 标准 | 锚点 |
|---|---|---|
| Default lane | ≥ 863 passed (current main baseline) | `pytest -v --no-header` |
| E2E lane | 27+N passed (N = E11-11 新增 onboarding 测试数), 0 failed | `pytest -v -m e2e --no-header` |
| Adversarial | ALL TESTS PASSED 8/8 | `WELL_HARNESS_PORT=8799 python3 src/well_harness/static/adversarial_test.py` |
| Truth-engine 红线 | `git diff main..HEAD -- src/well_harness/controller.py src/well_harness/runner.py src/well_harness/models.py src/well_harness/adapters/` 输出空 | `git diff` |
| Codex personas | 5/5 verdict in {APPROVE, APPROVE_WITH_COMMENTS}, BLOCKER count = 0 across all | `.planning/phases/E11-workbench-engineer-first-ux/E11-04-PERSONA-REVIEW-RESULTS.md` |
| Onboarding 30 分钟基准 | (manual / next-session) | TBD via real engineer beta或 E11-12 之后再测 |
| EMPIRICAL-CLAIM-PROBE 合规 | 每个 PR 含 numeric runtime claim 必须实测 / TODO 标 / 引 commit:line | per-PR review |

---

## 9. CLOSURE 退出条件

E11 关闭需满足全部下列条件，自签 `GATE-E11-CLOSURE: Approved` (v6.1 solo-signed)：

1. ✅ §3 中 12 sub-phase 全部 merged 到 main
2. ✅ §8 verification protocol 全部通过
3. ✅ Codex 5 personas review 给出 0 BLOCKER
4. ✅ truth-engine 红线 0 触碰
5. ✅ E11-05-CLOSURE.md 在 .planning/phases/ 落地
6. ✅ Notion 同步：phase 页 + DEC-20260425-E11-WORKBENCH-UX-OVERHAUL + Roadmap 行
7. ✅ HANDOVER.md 增补 §E11 Onboarding Flow + 真实工程师 30 分钟基准 acceptance criteria

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

> 本 PLAN.md 自身被 Kogami v6.1 Solo Autonomy 授权直接落到 main 不需 Gate；E11-12 CLOSURE 时由 Claude Code 自签 GATE-E11-CLOSURE: Approved 并贴最终 5-persona Codex review 结果。

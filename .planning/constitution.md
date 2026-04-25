# AI FANTUI LogicMVP Constitution

> **Constitution version:** v2.3 (2026-04-25, UI-COPY-PROBE rule append)
>
> **Note:** 本文件保留 2026-04-13 Milestone Hold 的原始叙述作为历史证据，并在下方追加 Milestone 9 Project Freeze 的 Lifted 叙述（2026-04-15 → 2026-04-20）+ v5.2 Solo Mode 治理条款 + v6.0 Codex Joint Dev Mode（2026-04-22, Notion Page 11）+ v6.1 Solo Autonomy Delegation（2026-04-25, DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT）+ Phase Registry 更新到 P32。早期 Milestone Hold（P4–P11 范围）已于 2026-04-13 为 Milestone 6 在 P13 启动时事实上 Lifted（见 `.planning/ROADMAP.md` Milestone 6/7/8 Lifted 行）；后续 Milestone 9 Freeze 于 2026-04-20 P32 W3 中正式追认 Lifted。
>
> **v2.2 增量：** 仅追加 v6.1 Solo Autonomy 节 + 升级 Governance Mode Timeline。v5.2 / v6.0 内容不变，作为历史层叠保留。
>
> **v2.3 增量：** 在 v6.1 Codex 触发清单内追加 §UI-COPY-PROBE（与 EMPIRICAL-CLAIM-PROBE 并列触发，治 user-facing copy 中的 fabricated surface claim）。来源：E11-02 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（详 RETRO-V61-054）+ Opus 4.7 异步根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）。v6.1 五条件 verbatim exception 不变。

## Milestone Hold (historical, 2026-04-13)

**Declared:** 2026-04-13
**Scope:** Milestone 4 (Phases P4–P11)
**Status:** ~~Active~~ **Lifted in stages via Milestones 6/7/8 (2026-04-13) — see `.planning/ROADMAP.md` for per-milestone Lifted records; later replaced by Milestone 9 Project Freeze on 2026-04-15.**

All P0 through P11 phases are complete. The project is at a natural pause point.

### What This Hold Means

- No active development phases.
- Base code frozen; only regression fixes and documentation corrections permitted.
- Notion control tower and GitHub repo remain accessible as read-only reference.
- Opus 4.6 review gate is not active.

### Reason

All P0→P11 capabilities have been delivered:
- Deterministic control-logic analysis workbench (thrust-reverser reference system)
- Runtime generalization proof via adapter layer (landing-gear second system)
- Fully automated GSD loop with Notion writeback and GitHub Actions CI
- Third-party onboarding guide and template scaffolding
- 23-command regression suite, 0 open gaps

The project has reached its MVP completeness target. Continued development requires an explicit product direction decision or external user feedback that identifies a new capability gap.

### Resume Criteria

Milestone Hold lifts when one or more of the following conditions are met:

1. An explicit product direction decision nominates a new capability or system adapter as the next priority.
2. External user feedback identifies a confirmed gap that cannot be resolved within the existing frozen baseline.
3. A project sponsor or lead author formally requests a new development phase via Notion control tower or GitHub.

No development activity resumes without a documented decision in the Notion control plane.

---

## Project Identity

**Name:** AI FANTUI LogicMVP
**Type:** Deterministic control-logic analysis workbench
**First Reference System:** Thrust reverser deploy cockpit
**Generalization Proof:** Landing-gear adapter runtime (second system)

## Core Truths

- `src/well_harness/controller.py` is the confirmed control truth.
- `src/well_harness/runner.py` is the simulation coordination layer.
- The simplified plant is a first-cut feedback model, not a complete physical model.
- New system truth is allowed only through explicit adapter interfaces.
- Bypassing adapters with new hardcoded truth paths is forbidden.

## Control Plane

- GitHub / repo is the code truth plane.
- Notion is the control plane and audit cockpit.
- GSD owns plan → execute → verify routing.
- Opus 4.6 is the only intended manual review gate for subjective judgment.

## Phase Registry

| Phase | Title | Status |
|-------|-------|--------|
| P0 | Control Tower And GSD Control Plane | Done |
| P1 | Automate Execution And Evidence Writeback | Done |
| P2 | Harden Opus 4.6 Review Packets | Done |
| P3 | Reduce Control-Plane Drift | Done |
| P4 | Elevate Cockpit Demo To Presenter-Ready | Done |
| P5 | Demo Polish And Edge-Case Hardening | Done |
| P6 | Reconcile Control Tower And Freeze Demo Packet | Done |
| P7 | Build A Spec-Driven Control Analysis Workbench | Done |
| P8 | Runtime Generalization Proof | Done |
| P9 | Automation Hardening & Evidence Pipeline Maturity | Done |
| P10 | Second-System Runtime Pipeline End-to-End | Done |
| P11 | Product Readiness & Third-Party Onboarding Guide | Done |
| P12 | Third-System Onboarding Validation | Done |
| P13 | Route B — Browser Workbench Multi-System Integration | Done |
| P14 | AI Document Analyzer | Done (2026-04-13) |
| P15 | Pipeline Integration — P14 output → P7/P8 intake | Done (2026-04-14) |
| P16 | AI Canvas Sync（Opus 4.6 架构裁决） | Done (2026-04-15) |
| P17 | Fault Injection — Interactive Fault Mode | Done (2026-04-15, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P18 | Demo Cleanup & Archive Integrity | Done (2026-04-16, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P19 | Hardware Partial Unfreeze — Monte Carlo + Reverse Diagnosis + Pitch Deck | Done (2026-04-17, self-signed v4.0; provenance re-signed 2026-04-20 P32; supersedes `docs/unfreeze/P17-application-draft.md`) |
| P20 | Wow E2E Coverage + Demo Resilience + Dress Rehearsal | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P32) |
| P21 | Local Model PoC — 国产模型本地降级 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P22 | Demo Rehearsal 物料冻结 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P23 | Co-development Kit — 立项通过后首批对接物料 | Done (2026-04-18, GATE-P23-CLOSURE Approved; 对外路线图编号 H2-23 ~ H2-27) |
| P24 | 立项后视觉硬化 — Canvas UI / AI Drawer / Demo Visuals | Done (2026-04-18, GATE-P24-CLOSURE Approved) |
| P25 | 立项汇报段落级时序彩排 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P26 | 立项物料引用有效性自动验证 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P27 | Backend Switch Drill — pkill+spawn+wait_ready | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P28 | FAQ Evidence Cross-Check | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P29 | Pre-Pitch Readiness Scorecard | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P30 | Scorecard 语义与 findings §5.1 决策对齐 | Done (2026-04-18, self-signed v4.0; provenance re-signed 2026-04-20 P31 audit) |
| P31 | Explain-runtime visibility + prewarm guardrails (orphan-triage re-land) | Done (2026-04-20, v5.2 solo-signed; awaiting `P31-GATE: Approved` for FF merge to main) |
| P32 | Provenance Backfill — v4.0 追认 + Milestone 9 Lifted + constitution v2.1 | In progress (2026-04-20, v5.2 solo-signed; `GATE-P32-PLAN: Approved` 2026-04-20, awaiting `GATE-P32-CLOSURE: Approved`) |

---

## Milestone 9 — Project Freeze → Lifted

**Declared:** 2026-04-15 by Opus 4.6 Final Adjudication
**Lifted:** 2026-04-20 (retroactive provenance追认 under v5.2 Claude App Solo Mode, P32 W3)
**Scope:** Post-P16 freeze line covering all P17–P30 activity

### What Milestone 9 Meant

Opus 4.6 declared Project Freeze after P16 AI Canvas Sync (2026-04-15) with the assessment "项目已达到可泛化动力控制电路系统工作台 MVP 达标线". Freeze conditions required that continued development await one of three Resume Criteria: 外部用户反馈 / 产品方向决策 / 赞助方请求. `docs/freeze/FREEZE-RULING-2026-04-15.md` is the primary rulemaking document; `MILESTONE4/5/6-HOLD.md` are the earlier freeze-family records.

### Why It Was Lifted (retroactively 追认)

Between 2026-04-15 and 2026-04-18, under the v4.0 Extended Autonomy Mode then-in-force, **14 Phases (P17 → P30) landed above the freeze line**, each individually self-signed by the Executor (Codex / MiniMax-2.7 / Claude Code Opus 4.7) and accepted by Kogami through point-Gate decisions (`GATE-P23-CLOSURE: Approved`, `GATE-P24-CLOSURE: Approved`, etc.). These Gate approvals collectively satisfied Resume Criterion #1 「产品方向决策」 — Kogami's on-the-record directives to continue with 立项 demo hardening, co-development kit, then pitch script rehearsal constitute the required 产品方向 evidence.

**However**, the 14-Phase window **never carried an explicit Milestone 9 Lifted statement in this constitution**. That gap is what P32 W3 closes: not by retroactively re-consenting to work that already happened, but by正式 acknowledging that the freeze line was in fact crossed and the Resume Criterion path was met.

### Signatures

- **Kogami (Project Sponsor):** implicit Lifted consent via the 14 per-Phase Gate approvals (2026-04-15 → 2026-04-18); **explicit 追认 via `GATE-P32-PLAN: Approved` (2026-04-20)**
- **Claude App Opus 4.7 (Solo Executor, v5.2):** solo-signed 2026-04-20 via `.planning/phases/P32-provenance-backfill/P32-00-PLAN.md`

### What This Does NOT Mean

- Milestone 9 Lifted does **not** authorize new能力 Phases prospectively. Any new Phase (P33+) must still go through its own PLAN / CLOSURE Gate sequence under v5.2 Solo Mode.
- It does **not** imply `docs/freeze/FREEZE-RULING-2026-04-15.md` is void. That ruling stands as the 2026-04-15 factual assessment; Lifted simply记录 that the Resume Criteria were thereafter met.
- It does **not** alter any P17–P30 Phase content, tests, or code. P32 is证迹 (provenance) only.

---

## Governance Mode Timeline

- **v3.0 双 Opus (2026-04-xx → 2026-04-17):** Claude Code Opus 4.7 as Executor; Notion AI Opus 4.7 as independent Gate reviewer. Retired when v4.0 Extended Autonomy allowed Executor self-signing.
- **v4.0 Extended Autonomy (2026-04-17 → 2026-04-19):** Executor allowed to self-sign Gate within a ≥3-Phase深度验收 window when Kogami 显式 renewed the mandate. Used for P17 → P30 close-out.
- **v5.1 Pair Mode (2026-04-19 → 2026-04-20):** Short-lived dual-Executor pair (Claude App + Codex). Abandoned after orphan commit `4474505` (Codex, unsigned) triggered the P31 orphan-triage response.
- **v5.2 Claude App Solo Mode (2026-04-20 → 2026-04-22):** Claude App Opus 4.7 as sole Executor. All Gate decisions (PLAN, CLOSURE) require explicit Kogami signature; Executor never self-selects the next Phase direction.
- **v6.0 Multi-Agent × Codex Joint Dev (2026-04-22 → 2026-04-25):** Claude Code 主执行 + Codex 强制盲点审查回到清单（多文件前端 / API 契约变更 / e2e 期望变更 / UI 变更 / 用户 UX 批评后首次实现 / OpenFOAM 误差等触发硬性调用）。Verbatim exception 5 条件允许跳过 round-2。详见 Notion Page 11 v6.0 节。
- **v6.1 Solo Autonomy Delegation (2026-04-25, active):** Kogami 在 PR #5 Gate 后口头授权 Claude Code 全权（Notion + PR merge + Codex 自决 + 新 phase 启停），仅 truth-engine 红线维持。详见 v6.1 Solo Autonomy 节、DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT、Notion Page 11 §v6.1。
- **v2.3 UI-COPY-PROBE 立法 (2026-04-25, active):** v6.1 治理底色不变，追加 §UI-COPY-PROBE 规则（与 EMPIRICAL-CLAIM-PROBE 并列触发）。E11-02 4 轮 Codex round-trip 全部围绕 tile-copy fabricated surface claim → Opus 4.7 异步诊断 → 立 v2.3。详见 v2.3 节、RETRO-V61-054。

## v5.2 Claude App Solo Mode (active)

### Red Lines (five absolutes)

1. **No controller.py / 19-node / R1–R5 / irreversible main-HEAD mutation without Kogami Gate sign.** FF merges, branch deletes, force-pushes, and any action that rewrites main's history must wait for an explicit `<PHASE>-GATE: Approved` comment from Kogami.
2. **No self-signed Gate.** Executor drafts `PLAN.md` and `CLOSURE.md` but never signs `GATE-<PHASE>-PLAN: Approved` or `GATE-<PHASE>-CLOSURE: Approved`. Those two signatures are Kogami-only.
3. **Tier 1 adversarial self-review is mandatory on every PLAN.** Plans must contain a Counterargument section with ≥3 reasoned self-objections and explicit rebuttals before request-for-Gate.
4. **Executor does not self-select next Phase direction.** When a Phase closes, Executor awaits Kogami's next directive. If Executor has a recommendation, it must be offered as an `AskUserQuestion` with ≥2 options, not acted on unilaterally.
5. **证迹 (provenance) precedes 能力 (capability).** New capability work is gated on no outstanding provenance debt. If gap analysis identifies provenance debt, that debt is closed in a dedicated证迹 Phase before any能力 Phase starts (this is precisely what P32 enforces for the v4.0 window).

### DECISION Format

Every Phase closure writes a DECISION section to the Notion control tower (`33cc68942bed8136b5c9f9ba5b4b44ec`) with heading:

```markdown
## Pxx DECISION · v5.2 solo-signed (YYYY-MM-DD)
```

Body covers: direction source · scope · Kogami Gate references · Exit artefact links · Red-line compliance checklist.

### Commit Trailer

Every commit by Claude App Opus 4.7 under v5.2 must include the trailer:

```
Execution-by: opus47-claudeapp-solo · v5.2
```

Reviewer sign line (in Notion / closure docs / audit records):

```
Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · YYYY-MM-DD
```

### Sandbox Discipline

- Workspace mount `.git/*.lock` residues are known blockers. v5.2 convention: scratch clone at `/sessions/<id>/p31-work/repo` + git bundle transfer when locks persist. Bundles live under `.planning/audit/bundles/` with adjacent README import instructions.
- Workspace mount file edits only permitted on paths that do NOT coincide with files changed by a pending bundle, to avoid FF merge conflicts.

---

## v6.1 Claude Code Solo Autonomy Delegation (2026-04-25, active)

### Origin

Kogami 2026-04-25 verbatim grant, after PR #5 GATE-WOW-A-NARRATION-FIX: Approved:

> 全权授权你进行开发，根据你的建议继续执行，只有truth-engine不许动，其他权限都交给你，你可以按照分工，调用codex配合你。记得在Notion页面里更新我这次的授权，以及Claude code的权限说明

Recorded as `DEC-20260425-WOW-A-FULL-AUTONOMY-GRANT` (Notion 04 决策日志 DB) and reflected in Notion Page 11 §v6.1 Solo Autonomy Delegation. v5.2 五红线和 v6.0 联合开发 Codex 触发清单作为基线继承；v6.1 仅在其上叠加授权层。

### Allowed (without per-step Kogami sign-off)

- Git: push / rebase / force-push 仅在 Claude 自己创建的 dev 分支；main 与 reviewer 已 ack 的 PR head 仍走 PR 流程
- `gh pr merge`：合并任何 OPEN PR 到 main，前提 (1) 未触红线 (2) 三轨证据齐全 (3) Codex 已审查（如触发 v6.0 / v6.1 trigger 清单）
- Notion 写入：04 决策日志、03 会话记录、Page 11 模型分工、Roadmap、其他子页
- Codex 调用自决：`/codex-gpt54` 何时调由 Claude 判断；硬触发清单与 v6.0 一致
- 自启 Phase：写 PLAN.md / 执行 / 写 CLOSURE.md / 自签 GATE-Pxx-CLOSURE: Approved；Tier 1 adversarial self-review (≥3 反对意见 + rebuttal) 仍硬性必跑
- 测试 / 调试 / `demo_server` 启停 / git bisect

### Forbidden（红线维持，触碰即停车）

- `src/well_harness/controller.py` 任何编辑（pure truth engine）
- `src/well_harness/runner.py` truth 层 / 19-node schema / 4 logic gate 条件定义
- `src/well_harness/adapters/` truth-bearing 改动（白名单：纯 metadata / docstring）
- `runs/dress_rehearsal_*/wow_*_timeline.json` fixture 数据
- Force-push 到 main / 已 merge 分支；squash 重写 main 历史；`--no-verify` / `--no-gpg-sign`
- 假装跑了测试（数字必须来自真实 stdout 粘贴）
- 自创规则版本号（v6.1 之后下次叠加层应是 v6.2，不得跳号）

### Codex 触发清单（继承 v6.0 + V61-001 新增 + v6.1 EMPIRICAL-CLAIM-PROBE）

继承 v6.0 硬性触发：多文件前端、API 契约、e2e 期望变更、UI 交互模式、用户 UX 批评首次实现、OpenFOAM solver 报错、Phase E2E ≥3 case 连续失败、Docker+OpenFOAM 联合调试、`foam_agent_adapter.py` >5 LOC、`_generate_*.py` CFD 几何新增、GSD 产出物。

继承 RETRO-V61-001 新增：安全敏感 operator endpoint、byte-reproducibility 敏感路径、跨 ≥3 文件 API schema rename。

**v6.1 新增 EMPIRICAL-CLAIM-PROBE 规则（2026-04-25）：** PR prose（test docstring / 文件级 comment / demo doc / PR description）写下任何关于服务端 runtime 行为的具体数字（plant deploy %、sim time、tick count、logic-X activation timing 等）之前，Claude Code 必须 boot 相关代码路径在本地实测一次，或显式标 `TODO(probe-before-merge)`，或引用数字定义所在的 commit:line。仅基于 mental-model 算术得出的数字禁止落地到 regression-locked 测试或客户向 demo doc。来源：PR #5 round 1 Codex 命中 BEAT_EARLY ~6% deploy 实际 0% （详 `.planning/audit/AUDIT-20260425-claude-pr5-round1-plant-deploy-blindspot.md`）。

## v2.3 · UI-COPY-PROBE

### 触发条件
任何写入 repo 的 user-facing 自然语言文本，包括但不限于：
- 入口页 / landing 页的 tile title / tile description / hero copy
- button label / link text / empty state / tooltip / modal body
- toast / banner / inline notice
- onboarding 步骤说明 / 错误提示文案

豁免：
- 纯 a11y 标签（aria-label）若与可见 label 1:1 同步
- 自动从 schema / enum / config 渲染的字符串（值由代码生成，文案即数据）

### 强制 stage（写完之后、commit 之前必走）
对本期新增/修改的每一条 user-facing copy，作者必须执行 **claim-to-source sweep**：

1. **拆 claim**：把 copy 拆成可验证的具体声明单元（surface 名、行为、字段、角色、限制、数据来源、文件格式、SHA 类型……）。叙述性形容词（"流畅"、"清晰"）不计 claim。
2. **grep 回 src/**：每一条 claim 必须在 src/ tests/ schemas/ config/ 至少一个文件中找到 line-number 锚点；锚点要支持该 claim 当前已 ship，不是计划态。
3. **三选一处置**：
   - **[ANCHORED]** 找到锚点 → 在本期 PLAN doc 的 §Surface Inventory 登记 `claim → file:line`。
   - **[REWRITE]** 找不到锚点但功能已规划 → 文案改写为 `planned for <Phase-ID> scope` 或 `coming in <Phase-ID>`，并在 §Surface Inventory 标 `[planned:<Phase-ID>]`。
   - **[DELETE]** 找不到锚点且无规划 → 删除该 claim。

#### Anchor 格式细则

每一条 anchor 必须是 **可执行的 ripgrep / sed 命令的目标**，即 `<file>:<line>` 或 `<file>:<line-range>`。section-only 引用（如 `constitution.md §v5.2 红线`）不算 anchor，必须落到行号。

**正面 claim**（"X feature 已 ship" / "Y 字段是 N 个" / "Z 类型是 SHA256"）：anchor 指向声明该 feature/字段/类型的具体源代码行。

**负面 claim / 缺位 claim**（`behavior (negative)` / `feature-name (negative)` 类，如 "本期还没有 demo mode" / "JS 没有 approval handler"）：anchor 必须含两部分，使用 **显式 `scope=` / `peer=` 前缀** 以避免被读成"file:line-range 是 grep 的限定范围"：
- **scope=`<file>`**（必填）：声明被搜索的 file 路径，**不带 line-range**——grep 跑全文件。reviewer 必须能用 `grep <selector> <file>` 一行复跑。
- **peer=`<file>:<line-range>`**（可选但强烈推荐）：同一 file（或同一概念邻域）中*存在*的相似 feature 的 file:line，用作对照锚（"这里有 view-mode-toggle 但没有 demo-mode-toggle"）。

**absence-claim 写作模板**：

```
scope=src/well_harness/static/workbench.html (grep "demo-mode\|demo-stage" 0 hits); peer=src/well_harness/static/workbench.html:283-299 (view-mode-toggle-bar 存在，仅 beginner / expert 两键)
```

或仅 scope（无 peer 时）：

```
scope=src/well_harness/static/workbench.js (grep "approval-action\|data-approval-action" 0 hits)
```

**禁止格式**（旧版本曾使用，现在 v2.3 失效条件之一）：
- `(absence claim — verified by absence of <X> in <file>)` —— 没有可执行 grep 命令
- `<file>:<line-range> (peer description)` 不带 `scope=` 前缀 —— 容易被误读为"grep 范围"

reviewer 抽查时复跑该 grep；若 hits 数与 anchor 描述不一致 → MISMATCH，进入 v2.3 失效条件。

### 与 v2.2 EMPIRICAL-CLAIM-PROBE 的关系
- v2.2 治**数值/计算/百分比/SHA 等可量化断言**，对照源是计算复跑 / pytest / runs/。
- v2.3 治**界面/行为/字段/角色等可定位断言**，对照源是 src/ ripgrep 锚点。
- 两条并列触发，不互相覆盖；同一条 copy 同时含数值与 surface 时，必须双轨都过。

### 审查侧的展开
- 评审者（Codex / 第二视角）有权要求作者贴出 §Surface Inventory；缺失或残缺直接 CHANGES_REQUIRED，不进入逐字 ripgrep round-trip。
- 评审者抽查 §Surface Inventory 中任意一行的锚点是否真实成立；命中 fabricated 锚点 → 视为伪造证据（同 v5.2 反假装条款）。

### 失效条件
- 作者声称已做 sweep 但 §Surface Inventory 缺失 / 行数与 copy 不对应 / 锚点 line 不存在 → 当轮 review 视为未做自审，要求重做（不是逐条修）。
- 连续两期被外部 reviewer 抓出 ≥1 条 fabricated surface → 触发该 Phase Owner 的 self-pass-rate 校准复盘。

### Trailer
任何含 user-facing copy 改动的 commit，message 末尾追加：
`UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`

### 来源
- E11-02 PR #10 4 轮 Codex round-trip 全部围绕 tile-copy honesty boundary（fabricated knowledge field 名、虚构 archive 行为、虚构 role gate、SHA256 vs commit-SHA 混淆、不存在的 wow_a UI 走读 surface）
- Opus 4.7 异步根因诊断（Notion 异步 session, 2026-04-25）：C1 stage 缺位（v2.2 只触发数值类断言，UI copy 整类逃出触网）/ C2 prompt-shape 偏置（landing/tile copy 训练近邻 = marketing 文案）/ C3 Solo Autonomy 自审无 grep 强制点位
- 详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md`

### Verbatim Exception（继承 v6.0，五条件 AND）

允许跳过 Codex round 2 直接 apply 修复的条件，五条全部满足：(1) 修复逐行 diff-level 匹配 Codex `Suggested fix` bullet；(2) 总改动 ≤20 LOC；(3) 触及 ≤2 个文件；(4) 不改动任何 public API surface；(5) PR body 显式引用 round number + finding ID。

### Self-Pass-Rate 强制

任何触发 EMPIRICAL-CLAIM-PROBE 软/硬规则的 PR body 必须含 `external_gate_self_estimated_pass_rate: <0..1>`。低估 / 高估都进 retro 计分。

### Hard Stop Points

- 需要修红线 → 停 + 索取 Kogami explicit "truth-engine 修复 logic-X" 字面授权
- Codex returns BLOCKER 不能 verbatim 修 → 停 + 升级到 Kogami
- 三轨任一连续 ≥3 次新增失败且非 inherited → 停 + 写 forensics + 升级
- 意外触红线（grep 命中 `controller.py` 在 `git diff` 中）→ `git checkout` 撤销 + 立即停车汇报

### Commit Trailer (v6.1)

```
Execution-by: claudecode-opus47 · v6.1 · solo-autonomy
```

### 撤销条件

- Kogami chat 中显式 "撤销 v6.1 / 收回授权 / 暂停自驱"
- Claude Code 自评发现已超出能力边界（含红线无法绕开） → 自请暂停 + 升级

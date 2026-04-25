# RETRO-V61-054 — UI-COPY-PROBE birth (E11-02 4-round arc + Opus 4.7 root-cause)

> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> **Date:** 2026-04-25
> **Triggered by:** E11-02 PR #10 — first sub-phase to require 4 Codex rounds in this repo
> **Counter:** autonomous_governance_counter_v61 unchanged (this retro is methodology, not arc-size)
> **Output artefacts:** constitution v2.3 §UI-COPY-PROBE; E11-00-PLAN §1.5 Surface Inventory template + 3 small differentials; `E11-02-SURFACE-INVENTORY.md` worked example
> **Numbering:** This is the first formal RETRO-V61-* in `ai-fantui-logicmvp`. Number `054` chosen to slot consistently with the `cfd-harness-unified` shared series (RETRO-V61-001 / V61-053 referenced in `~/CLAUDE.md`); ai-fantui-logicmvp will use the next free integer in that pool. Not retroactively renumbering.

---

## 0. Executive summary

E11-02 was a static-only `/workbench/start` 6-tile landing page. No truth-engine touch, no controller logic, only HTML/CSS/route + tests. Yet it took **4 Codex rounds** to APPROVE. Every single round-trip was a tile-copy honesty issue: fabricated knowledge field names, virtual archive behavior, virtual role gate, SHA256-vs-commit-SHA confusion, and a non-existent UI walkthrough referenced in `/demo.html`.

This is the same root-cause family as `RETRO-V61-053` (post-R3 live-run defect category) but on a different surface — **prose claims, not numerical claims**. v2.2 EMPIRICAL-CLAIM-PROBE only reflexes on numbers; UI copy claims default-routed through "narrative layer" and slipped past every self-check.

Opus 4.7 异步会话 (Notion @Opus 4.7, 2026-04-25) returned a 3-layer causal stack and a complete v2.3 §UI-COPY-PROBE rule. This retro logs the arc, the diagnosis, and the legislative output.

---

## 1. The 4-round arc (Codex GPT-5.4, account `picassoer651@gmail.com`)

| Round | Verdict | Findings | Cumulative file diff |
|---|---|---|---|
| R1 | CHANGES_REQUIRED | 3 IMPORTANT + 2 NIT | F1 dead anchors, F2 hero copy honesty, F3 KOGAMI vs persona, F4 XSS test (verbatim), F5 nav active marker (verbatim) |
| R2 | CHANGES_REQUIRED | 1 IMPORTANT (R2-F1 reopened R1-F2) | tile-level overclaim — Codex empirically swept the served HTML and listed 5 fabricated capability claims |
| R3 | CHANGES_REQUIRED | 4 IMPORTANT | R3-F1 (P1 4/4 archive vs actual 2/4) / R3-F2 (P3 wow_a/b/c on /demo.html) / R3-F3 (KOGAMI role-gate not implemented) / R3-F4 (commit-SHA vs SHA256) |
| R4 | APPROVE_WITH_COMMENTS | 1 NIT | P5 5 vs 9 knowledge fields (Codex explicitly: "I would not reopen Round 4 for that"). Applied as verbatim per v6.1 5-condition exception. |

Net commits on the branch: 4 fix commits (R1, R2, R3, R4). All squashed to merge `384901e` on main.

### What Codex did each round
- R1: structural review (static HTML grep + nav active state + XSS reflection probe)
- R2: empirical sweep — fetched served HTML and audited every tile claim against `workbench.html` / `workbench.js` source
- R3: line-level grep — traced `archiveBundle: true/false` flags in `workbench.js:140-164`, knowledge schema in `workbench.html:506-540`, approval handler absence in `workbench.js`, archive naming in `workbench_bundle.py:99-113,853-944`
- R4: closure verification + final NIT on field count

**Codex review tokens consumed across 4 rounds:** ≈ 268k + 102k + 162k + 110k = **~642k tokens** (5× a single round's typical 130k spend). Represents the cost of catching tile-copy honesty issues at review time instead of self-time.

---

## 2. Opus 4.7 异步根因诊断 (≤200 字)

> Verbatim from Notion @Opus 4.7 session, 2026-04-25:

不是 1M context 稀释（workbench.html 单文件远低于阈值）。三层叠加，按权重排：

**(C1 主因) Stage 缺位**：v2.2 EMPIRICAL-CLAIM-PROBE 只对"数值类断言"触发反射弧，UI copy 在模型自审里被默认归为"叙述层"而非"声明层"，整类逃出触网——没有"写完先 grep 回 src/"的强制顺序。

**(C2 次因) Prompt-shape 偏置**：landing/tile copy 的训练近邻是 marketing 文案不是 spec，缺省 pull-to-"sell the feature"——把"计划做的"和"已 ship 的"在同一句里抹平。

**(C3 底色) Solo Autonomy 无外部 ground**：Codex 接入后才补上 ripgrep 视角，但已经在第 4 轮——证明 self-pass 70% vs 实际 30% 的 gap 本质是**自审缺源码 grep 工具的强制点位**，不是模型能力。

PR #5 数值漂移 + E11-02 surface 漂移是同一根因的两个表面：未被 v2.2 收口的"另一类 fabricated claim"。建议加 v2.3 而不是扩展 v2.2——两者触发条件、对照源不同，合并会稀释 v2.2 的精度。

---

## 3. v2.3 立法输出（已 land 在 constitution.md）

完整规则正文移到 `.planning/constitution.md` §v2.3 · UI-COPY-PROBE。本 retro 只记三件事：

1. **触发条件**：所有 user-facing 自然语言文本（tile / label / empty state / tooltip / modal / banner / onboarding step / error notice）。豁免 a11y 同步标签 + schema-渲染字符串。
2. **强制 stage**：写完之后、commit 之前作者必须执行 claim-to-source sweep，三选一处置 [ANCHORED] / [REWRITE → planned for `<Phase-ID>`] / [DELETE]，结果登记到本期 §Surface Inventory。
3. **commit trailer**：`UI-Copy-Probe: <N> claims swept (<A> anchored / <P> planned / <D> deleted)`

与 v2.2 EMPIRICAL-CLAIM-PROBE 并列触发，**不是替换**。两者治不同断言族（数值 vs surface），同条 copy 同时含两类时必须双轨过。

---

## 4. Self-pass-rate 校准

| 维度 | 估计值 | 实际值 | gap |
|---|---|---|---|
| 进 Codex R1 前自评 pass-rate | ~70% | 0% (R1 即 CHANGES_REQUIRED) | -70 |
| 进 R2 前自评（修完 R1 后）| ~85% | 0% (R2 仍 CHANGES_REQUIRED, R1-F2 reopened) | -85 |
| 进 R3 前自评（R2 fix tile copy 后）| ~75% | 0% (R3 仍 CHANGES_REQUIRED, 4 fresh IMPORTANTs) | -75 |
| 进 R4 前自评（R3 fix 4 IMPORTANTs 后）| ~95% | ~98% (R4 APPROVE_WITH_COMMENTS, 1 NIT) | +3 |

**校准结论**：Claude Code Opus 4.7 在 user-facing UI copy 任务上的 self-pass-rate 估计**长期偏高 50%+**。直到完成 R3 修后才进入正常预测区间。这是 prompt-shape 偏置（C2）的直接观测。v2.3 §1.5 Surface Inventory 是 corrective action — 把"自评 pass-rate"从直觉降级为"逐条 grep 命中率"。

---

## 5. 行为变更（已生效）

| 变更项 | 状态 |
|---|---|
| `.planning/constitution.md` 加 §v2.3 UI-COPY-PROBE | ✅ 本 PR |
| `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` 加 §1.5 Surface Inventory + Acceptance #5 + Scope 硬约束 + Counterargument C-UI | ✅ 本 PR |
| `E11-02-SURFACE-INVENTORY.md` 追溯补登 worked example (29 rows: 22 ANCHORED / 7 REWRITE-as-planned / 0 DELETE) | ✅ 本 PR |
| 后续所有含 user-facing copy 的子 phase（E11-03..09 / E11-13..14 等）必填 §Surface Inventory | 进入 E11 phase 总验收清单（见 E11-00-PLAN.md §0 Acceptance #5） |
| Codex review trigger 清单更新（v2.3 触发条件并列 v2.2，不互斥） | ✅ constitution.md 反映 |
| Notion sync — DEC-V61-V23-UI-COPY-PROBE | 本 PR merge 后 sync |

---

## 6. Open questions

- **Q1**：是否要把 §Surface Inventory 抽象成 `tools/inventory_check.py` 自动化校验脚本（grep 锚点行真实存在）？现状是手动 + Codex 抽查。
  - 倾向：**不要现在做**。手动表 + Codex 抽查在 E11-03..09 跑完后再决定是否需要自动化。过早自动化会让 inventory 退化成"过 lint 即可"的形式主义。
- **Q2**：v2.3 是否要回填到已合并的 PR #4 (HANDOVER 增量) / PR #8 (E11 phase 启动) / PR #9 (E11-01 baseline)？
  - 倾向：**不回填**。这三个 PR 的 user-facing copy 改动极少（HANDOVER 只是开发者文档，PR #8 / #9 都是 .planning/ 内部 doc）。E11-02 是项目第一个真正含 user-facing landing copy 的 PR，回填的 ROI 太低。
- **Q3**：v2.3 §Surface Inventory 与现有 GSD `gsd-ui-checker` agent 是否重叠？
  - 倾向：**不重叠**。`gsd-ui-checker` 验 6 维度 design contract（layout / a11y / 等），是产品质量层；§Surface Inventory 验 honesty boundary（claim → src 锚点），是事实层。两者并列存在合理。

---

## 7. Provenance

- Codex round logs (R1–R4): captured in branch `feat/E11-02-workbench-start-onboarding-20260425` PR body and merge `384901e`
- Opus 4.7 异步会话 transcript: Notion `@Opus 4.7` session 2026-04-25 (内部链接，本仓库不留 binary copy)
- Worked example: `.planning/phases/E11-workbench-engineer-first-ux/E11-02-SURFACE-INVENTORY.md`
- Constitution amendment: `.planning/constitution.md` §v2.3 (HEAD this PR)

---

## 8. Trailer

```
Authored-by:    claudecode-opus47 · v6.1 · solo-autonomy
Diagnosis-by:   opus-4.7 (Notion async session, 2026-04-25)
Legislation:    v2.2 → v2.3 (UI-COPY-PROBE)
UI-Copy-Probe:  N/A (this is a retro doc, no user-facing copy)
```

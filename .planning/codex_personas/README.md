# Codex Persona Review Pipeline

> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
> Date: 2026-04-25
> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6

## Purpose

5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape.

**Anti-bias model (governance bundle #2, 2026-04-25):**
- **Tier-A (5-parallel):** within-PR inter-persona finding uniqueness (each persona must contribute ≥1 finding NOT mentioned by other 4) mitigates same-model bias.
- **Tier-B (1-persona default):** within-PR uniqueness is **N/A by definition**. Anti-bias is delegated to (a) v2.3 §Surface Inventory grep evidence layer + (b) cross-sub-phase persona round-robin (P1→P2→P3→P4→P5→P1) so consecutive Tier-B sub-phases don't share reviewer perspective + (c) RETRO-V61-054 §6.3 rollback if two consecutive Tier-B sub-phases miss a fabricated surface claim.

See §Tier-trigger below for which tier fires when.

## Persona inventory

| ID | Persona | File |
|---|---|---|
| P1 | Junior FCS Engineer (3-month hire, learning the codebase) | `P1-junior-fcs.md` |
| P2 | Senior FCS Engineer (10y reverser experience, spec-driven) | `P2-senior-fcs.md` |
| P3 | Demo Presenter (立项汇报 stage, story-arc focused) | `P3-demo-presenter.md` |
| P4 | QA / V&V Engineer (适航 traceability, audit-chain) | `P4-qa-vv.md` |
| P5 | Customer Apps Engineer (issue triage, customer-facing) | `P5-apps-engineer.md` |

## Invocation

### Tier-trigger（governance bundle #2 落地，2026-04-25 起生效）

> **变更：** 之前默认每个 user-facing UI 子 phase 跑全 5-persona 并行 review。E11-09 ≤2 轮 Codex APPROVE 实证 v2.3 UI-COPY-PROBE 已摊销 → Opus 4.7 §1 strategic input 通过 → 5-persona 默认改为 **tier-trigger**。详见 `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §6 + `constitution.md` §v2.3 持久化条款。
>
> v2.2 / v2.3 / v6.1 / §Surface Inventory / RETRO 序号 全部保留，**不动**。本次只软化 persona pipeline 的默认调用规则，不动其他规则。

按下表决定调多少 persona：

| 子 phase 特征 | persona 数 | 选哪个 |
|---|---|---|
| user-facing copy diff ≥ 10 行 **AND** §Surface Inventory 含 ≥ 3 条 [REWRITE/DELETE] | **5（全 P1–P5 并行）** | 全跑 |
| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | **`PERSONA-ROTATION-STATE.md` 是唯一 source of truth。** 默认值 = 末行 persona 在 P1→P2→P3→P4→P5→P1 序列中的下一位（新 epic 第一行 = P1 Junior FCS）。Owner 可写入非默认值（如 demo-arc 重 → P3；适航 trace 重 → P4），唯一硬约束：写入值**不得**与上一行 Tier-B persona 相同 |

**"copy diff ≥ 10 行" 计数命令（确定性，作者必须在 PR body 引用结果）：**

```bash
# 在 PR feature branch 上跑（base = main 或当期 phase 的 trunk merge-base）：
git diff --stat $(git merge-base HEAD main)..HEAD -- \
  'src/well_harness/static/*.html' \
  'src/well_harness/static/*.js' \
  'src/well_harness/static/*.css'
```

读取最后一行 `N files changed, X insertions(+), Y deletions(-)` 中的 `X + Y`。`X + Y ≥ 10` 即满足"copy diff ≥ 10 行"条件。该数字必须出现在 PR body 的 §Surface Inventory 标题行下方（例：`copy_diff_lines=12 (insertions=8, deletions=4)`），便于 Codex / 后续 reviewer 复现。

**轮换状态记录：** 当前期 Tier-B 已用 persona 序列记录在 `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md`（owner 在每次 Tier-B sub-phase commit 后追加一行 `<sub-phase-id>: P? (<reason>)`）。新 epic 启动时序列重置为 P1。

**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory + 跑完计数命令后立刻知道 trigger 条件是否满足。

**例外（仍跑全 5）：**
- 该子 phase 触发了 v2.2 EMPIRICAL-CLAIM-PROBE 同时也是 user-facing UI 子 phase（数值+surface 双轨断言，需要全角度审）
- Phase Owner 主动声明"本子 phase 范围特别敏感"（authority chain / red-line 边界 / 适航 trace 等）

### 命令模板

```bash
# Tier-A（5 persona 并行，仅在条件满足时跑）：
for p in P1 P2 P3 P4 P5; do
  cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
    "$(cat .planning/codex_personas/${p}-*.md)" \
    > .planning/phases/<phase-id>/persona-${p}-output.md 2>&1 &
done
wait

# Tier-B（1 persona，跨-sub-phase 轮换 P1 → P2 → P3 → P4 → P5 → P1，起点 P1）：
# 启动新 epic 第一个 Tier-B sub-phase 跑 P1；后续按 PERSONA-ROTATION-STATE.md 末行下一个值轮换。
# 例：当期 epic 已记录 sub-phase X1: P1, X2: P2 → 当前 sub-phase 应跑 P3。
PERSONA=P3  # 由 .planning/phases/<epic>/PERSONA-ROTATION-STATE.md 决定，不得与上一行 Tier-B sub-phase 重复
cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
  "$(cat .planning/codex_personas/${PERSONA}-*.md)" \
  > .planning/phases/<phase-id>/persona-${PERSONA}-output.md 2>&1
# commit 后追加一行到 PERSONA-ROTATION-STATE.md：
# echo "<phase-id>: ${PERSONA} (<reason — content fit / round-robin>)" >> .planning/phases/<epic>/PERSONA-ROTATION-STATE.md
```

## Output convention

Each persona writes verdict to its own file. Closure semantics depend on which tier ran:

### Tier-A（5-persona 并行）

Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:

- 5 verdicts side-by-side
- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
- 0 BLOCKER is a phase-CLOSURE precondition

### Tier-B（1-persona 默认）

No aggregator runs (single verdict file = the review record). Closure precondition collapses to:

- 1 verdict file at `.planning/phases/<phase-id>/persona-<P?>-output.md`
- Severity-ranked findings using the same BLOCKER/IMPORTANT/NIT scale
- 0 BLOCKER from that single persona is the phase-CLOSURE precondition
- Cross-persona uniqueness check is **N/A** by definition (only 1 persona ran). Anti-bias is delegated to the v2.3 UI-COPY-PROBE §Surface Inventory grep evidence + the cross-sub-phase persona rotation rule (see §Tier-trigger above), not to within-PR multi-persona diversity.

If a Tier-B sub-phase later upgrades to Tier-A (e.g., scope expanded mid-PR to ≥10 lines copy diff + ≥3 [REWRITE/DELETE]), the previous Tier-B verdict is discarded and the full 5-persona run re-executes.

## Anti-bias safeguard

**Tier-A:** If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
2. Triggers re-run with sharpened persona contexts
3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework

**Tier-B:** Within-PR diversity check is N/A (1 persona). Anti-bias is enforced by:
1. **Cross-sub-phase rotation** — `.planning/phases/<epic>/PERSONA-ROTATION-STATE.md` is the canonical source of truth for next-persona selection. Default value = round-robin successor (P1→P2→P3→P4→P5→P1) of the last entry. Owner may write a different P-value when sub-phase content motivates it (e.g., demo-arc-heavy → P3, 适航 trace heavy → P4). Hard constraint enforced by the rule (not by owner discretion): the written value must NOT equal the immediately preceding Tier-B entry.
2. **v2.3 UI-COPY-PROBE §Surface Inventory** — grep-anchored claims act as the structural evidence layer that compensates for losing 4 perspectives.
3. **Rollback trigger** — if any post-merge fabricated surface claim slips through a Tier-B sub-phase, RETRO-V61-054 §6.3 fires (rollback for next 3 sub-phases + open successor RETRO).

## Cost / latency baseline (recorded for retro)

**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).

**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.

If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce ≥1 post-merge fabricated surface claim per v2.3 §UI-COPY-PROBE 失效条件, auto-rollback per RETRO-V61-054 §6.3 (force default 5-persona for next 3 sub-phases + open successor RETRO + re-engage Opus 4.7).

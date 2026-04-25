# Codex Persona Review Pipeline

> Authored by: Claude Code Opus 4.7 · v6.1 Solo Autonomy
> Date: 2026-04-25
> Spec source: `.planning/phases/E11-workbench-engineer-first-ux/E11-00-PLAN.md` §6

## Purpose

5 reusable Codex prompts that turn `gpt-5.4` into specific reviewer personas for Workbench UX validation. Each persona has distinct background, mission, and required-output shape. Pipeline ensures **inter-persona finding uniqueness** to mitigate same-model bias risk (Tier-1 adversarial counterargument #2 in E11 PLAN).

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
| 其他所有情形（含 doc-only / 纯 refactor / copy diff < 10 行 / 无 [REWRITE/DELETE]） | **1** | 默认 P1（junior FCS）；当期 phase owner 可按"同一 sub-phase 不重复同一 persona"原则轮换至 P2/P3/P4/P5 |

**判断时机：** 子 phase commit 之前，作者填完 §Surface Inventory 后立刻知道 trigger 条件是否满足。

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

# Tier-B（1 persona 默认 — P1 Junior FCS）：
cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
  "$(cat .planning/codex_personas/P1-junior-fcs.md)" \
  > .planning/phases/<phase-id>/persona-P1-output.md 2>&1

# Tier-B 轮换（当期 owner 选择非默认 persona，例如 P3 demo presenter）：
cx-auto 20 && codex exec --skip-git-repo-check -c 'model="gpt-5.4"' \
  "$(cat .planning/codex_personas/P3-demo-presenter.md)" \
  > .planning/phases/<phase-id>/persona-P3-output.md 2>&1
```

## Output convention

Each persona writes verdict to its own file. Aggregator (E11-04 in plan) reads all 5 and produces `E11-04-PERSONA-REVIEW-RESULTS.md` with:

- 5 verdicts side-by-side
- Cross-persona finding uniqueness check (each persona must contribute ≥1 finding NOT mentioned by other 4 — anti-bias safeguard)
- Severity-ranked findings (BLOCKER → must fix in current phase / IMPORTANT → fix this phase / NIT → next-phase queue)
- 0 BLOCKER is a phase-CLOSURE precondition

## Anti-bias safeguard

If aggregator detects that all 5 personas produce identical or near-identical finding sets, the pipeline marks the review **invalid** and:
1. Logs to `.planning/audit/AUDIT-<date>-codex-persona-degenerate.md`
2. Triggers re-run with sharpened persona contexts
3. If two consecutive re-runs degenerate, escalates to Kogami for manual persona spec rework

## Cost / latency baseline (recorded for retro)

**Pre-tier-trigger baseline (default 5-persona, deprecated 2026-04-25):**
- PR #5 R1 single Codex review: ~10min wall, ~187k tokens.
- E11-01 baseline 5-persona run: ~10min wall (parallel), ~1M tokens (5 × ~200k).

**Post-tier-trigger expected cost (governance bundle #2, 2026-04-25 起生效):**
- Tier-A (5-persona, only fires when copy diff ≥10 AND ≥3 [REWRITE/DELETE]): ~1M tokens / sub-phase. Expected frequency: ~1 in 4-5 sub-phases for E11.
- Tier-B (1-persona, default): ~200k tokens / sub-phase. Expected frequency: 4-5 in 5 sub-phases for E11.
- **Estimated savings vs default 5-persona:** ~70–80% of Codex tokens on the persona pipeline alone, while preserving anti-bias guarantee for high-honesty-risk sub-phases.

If real numbers exceed expected by ≥50%, log a retro entry. If two consecutive Tier-B sub-phases produce post-merge defects in user-facing copy, re-evaluate whether tier-trigger conditions are too lax (RETRO-V61-054 §6.2 candidate trigger).

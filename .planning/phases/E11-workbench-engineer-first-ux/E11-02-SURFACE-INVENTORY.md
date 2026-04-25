# E11-02 Surface Inventory (retroactive · v2.3 worked example)

> **Authored by:** Claude Code Opus 4.7 (1M context) · v6.1 Solo Autonomy
> **Date:** 2026-04-25
> **Status:** retroactive — E11-02 (PR #10, merge `384901e`) was completed before v2.3 立法.
> Inventory reconstructed from Codex R1–R4 ripgrep traces; serves as worked example for §1.5 template in E11-00-PLAN.md.
> **R1 amendment (2026-04-25, post v2.3 PR R1)**: Codex R1 on the v2.3 governance bundle returned BLOCKER because 6 inventory rows (#9, #11, #12, #19, #22, #25–28) were `[ANCHORED]` without concrete `file:line`. Fix landed in same PR + a v2.3 spec append clarifying absence-claim anchor format.

## 0. Why this doc exists

E11-02 took 4 Codex rounds to APPROVE. Every round-trip was a tile-copy honesty issue (fabricated surface name, virtual archive behavior, virtual role gate, SHA256-vs-commit-SHA confusion, non-existent UI walkthrough). After PR #10 merged, Opus 4.7 异步会话给出根因诊断（C1 stage 缺位 / C2 prompt-shape 偏置 / C3 Solo Autonomy 自审无 grep 强制点位）→ 立 v2.3 UI-COPY-PROBE。

This file backfills what §Surface Inventory **should have looked like at commit time** so that:
1. The format is exercised before being canonized in E11-03+ phases
2. Future reviewers can compare "what claim did the page state" vs "what does src actually expose"
3. The retroactive table itself becomes the audit residue of the 4-round arc

## 1. Inventory table (final state at PR #10 merge `384901e`)

> Copy file: `src/well_harness/static/workbench_start.html` (HEAD `955f61c` → squashed to `384901e`).
> Each row anchors against the file as it stood at merge time. Line numbers refer to the PR-merged content.

| #  | Copy 出处 (file:line) | Claim 摘录 (≤40 字) | 类别 | Anchor / Plan-ID | 状态 |
|----|---|---|---|---|---|
| 1  | workbench_start.html:30 | "/workbench 是 3 列面板，今天会承载 5 类工作" | feature-name | src/well_harness/static/workbench.html:79-105 (3-column shell ids) | [ANCHORED] |
| 2  | workbench_start.html:32 | "本期还没有按 intent 自动重排面板" | behavior (negative) | src/well_harness/demo_server.py:238-243 (route serves static, ignores ?intent=) | [ANCHORED] |
| 3  | workbench_start.html:42 | "P1–P5 是 E11-01 baseline 5-persona review 里的工程角色" | data-source | .planning/phases/E11-workbench-engineer-first-ux/E11-01-BASELINE-PERSONA-REVIEW.md:16-23 | [ANCHORED] |
| 4  | workbench_start.html:46 | "KOGAMI 是项目内部审批权限角色（仅 Kogami 可签发 proposal）" | role-gate | src/well_harness/static/workbench.html:131,142 (data-role / data-approval-role) | [ANCHORED] |
| 5  | workbench_start.html:60 | "落到「一键预设验收卡」, 4 张：通过并留档 / 阻塞演示 / 快速通过 / 留档复跑" | feature-name | src/well_harness/static/workbench.html:217 (h2 + 4 buttons :234,244,254,264) | [ANCHORED] |
| 6  | workbench_start.html:63 | "ready_archived 与 archive_retry 还会落 archive，blocked_follow_up 与 ready_preview 不落" | behavior | src/well_harness/static/workbench.js:142,149,156,163 (archiveBundle: true/false/false/true) | [ANCHORED] |
| 7  | workbench_start.html:69 | "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" | feature-name (negative) | E11-00-PLAN.md §3 row E11-05 | [REWRITE → planned for E11-05] |
| 8  | workbench_start.html:79 | "落到 control / document / circuit 三列 shell + 「Raw JSON」抽屉" | surface-location | src/well_harness/static/workbench.html:99-105 (3 panel ids) + workbench.html:1065-1070 (json-output details) | [ANCHORED] |
| 9  | workbench_start.html:81 | "TRA / RA / N1k 等 lever 调参在 /demo.html，本期 ?intent= 还没把它合入" | surface-location | src/well_harness/static/demo.html:68 (TRA lever input id="fan-tra-lever") + src/well_harness/static/workbench.html (grep "fan-tra-lever" 0 hits) | [ANCHORED] |
| 10 | workbench_start.html:84 | "L1–L4 着色 + 认证链 banner 在 E11-06/07 上线" | feature-name (negative) | E11-00-PLAN.md §3 rows E11-06,E11-07 | [REWRITE → planned for E11-06/07] |
| 11 | workbench_start.html:97 | "本期主面板还没有专门的 demo mode" | behavior (negative) | src/well_harness/static/workbench.html:275-310 (view-mode-toggle-bar 存在，beginner/intermediate/advanced；grep "demo-mode\|demo-stage" 在该 file 内 0 hits) | [ANCHORED] |
| 12 | workbench_start.html:103 | "wow_a/b/c 目前只在 tests/e2e/test_wow_a_causal_chain.py 里有，没有 UI 走读 surface" | data-source | tests/e2e/test_wow_a_causal_chain.py:38-66 (BEAT_DEEP_PAYLOAD + test functions) + src/well_harness/static/workbench.html (grep "wow_a\|wow_b\|wow_c" 0 hits) | [ANCHORED] |
| 13 | workbench_start.html:108 | "无-chrome demo mode + UI wow_a 走读 进入 E11-05/08 范围" | feature-name (negative) | E11-00-PLAN.md §3 rows E11-05,E11-08 | [REWRITE → planned for E11-05/08] |
| 14 | workbench_start.html:120 | "落到 knowledge 区。当前 schema 是 9 字段：Observed Symptoms / Evidence Links / Confirmed Root Cause / Repair Action / Validation After Fix / Residual Risk / Suggested Logic Change / Reliability Gain Hypothesis / Guardrail Note" | field-name | src/well_harness/static/workbench.html:506-540 (9 textareas) | [ANCHORED] |
| 15 | workbench_start.html:124 | "客户邮件原文 → ticket payload 字段映射工具是 E11-08 范围" | feature-name (negative) | E11-00-PLAN.md §3 row E11-08 | [REWRITE → planned for E11-08] |
| 16 | workbench_start.html:128 | "knowledge 字段已经在主面板渲染（dt/dd 列表）" | feature-name | src/well_harness/static/workbench.html:1041-1044 (dt/dd render) | [ANCHORED] |
| 17 | workbench_start.html:144 | "Approval Center · 静态 shell 占位" | surface-location | src/well_harness/static/workbench.html:139-163 (静态 lanes) | [ANCHORED] |
| 18 | workbench_start.html:145 | "label 上写 Kogami-only · 角色判定逻辑未实现" | role-gate | src/well_harness/static/workbench.html:136 (label) + grep workbench.js → no approval-action handler | [ANCHORED] |
| 19 | workbench_start.html:147 | "workbench.js 没有 approval-action handler，按钮点了不会落账（对 Kogami 也不会）" | behavior (negative) | src/well_harness/static/workbench.js (grep "approval-action\|data-approval-action" 0 hits, 对照 :3641-3642 preset-trigger handler 真实存在) | [ANCHORED] |
| 20 | workbench_start.html:152 | "data-approval-role=KOGAMI + data-approval-action 锚点已就位" | feature-name | src/well_harness/static/workbench.html:142,156,160 | [ANCHORED] |
| 21 | workbench_start.html:155 | "hash-chain 查阅 / SHA 分组 / JSONL 导出 / 状态过滤 / 角色判定 都是 E11-08 范围" | feature-name (negative) | E11-00-PLAN.md §3 row E11-08 | [REWRITE → planned for E11-08] |
| 22 | workbench_start.html:170 | "本期主面板还没有专门的 trace-matrix 视图" | behavior (negative) | src/well_harness/static/workbench.html:214-273 (preset section 存在；grep "trace-matrix\|data-trace" 在该 file 内 0 hits) | [ANCHORED] |
| 23 | workbench_start.html:174 | "archive package 自带 timestamp + slug 目录 + SHA256 文件完整性哈希（不是 git commit SHA）" | format-spec | src/well_harness/workbench_bundle.py:99-113,853-944 | [ANCHORED] |
| 24 | workbench_start.html:175 | "truth-engine SHA / adversarial 8/8 / e2e 状态条进入 E11-06 范围" | feature-name (negative) | E11-00-PLAN.md §3 row E11-06 | [REWRITE → planned for E11-06] |
| 25 | workbench_start.html:176 | "本期产出物均为内部研究证据，不构成适航合规声明" | limit | .planning/PROJECT.md:5-7 (Vision: "deterministic control-logic analysis workbench... not full physical simulation or demo-only polish") | [ANCHORED] |
| 26 | workbench_start.html:185 | "controller.py · 19-node truth engine · 4 logic gates — read-only" | role-gate | src/well_harness/controller.py:15-21 (DeployController class docstring "reflects only the confirmed logic") + .planning/constitution.md:154 (§v5.2 Red Lines #1) | [ANCHORED] |
| 27 | workbench_start.html:186 | "adapters/*.py 真值出口 — read-only" | role-gate | src/well_harness/adapters/__init__.py + .planning/constitution.md:212 (red-line clause "controller.py 任何编辑") + .planning/PROJECT.md:25-27 ("Bypassing adapters by adding new hardcoded truth paths is forbidden") | [ANCHORED] |
| 28 | workbench_start.html:187 | "已签 audit event 的 hash chain — append-only" | data-source | src/well_harness/collab/merge_close.py:34-59 (audit.append + pr_event_hash + ticket_close_event_hash chain) | [ANCHORED] |
| 29 | workbench_start.html:188 | "wow_a fixture 的 BEAT_DEEP_PAYLOAD — frozen" | data-source | tests/e2e/test_wow_a_causal_chain.py:51-58 (BEAT_DEEP_PAYLOAD constant) | [ANCHORED] |

## 2. Totals

- **ANCHORED:** 22
- **REWRITE-as-planned:** 7
- **DELETE:** 0

## 3. Commit trailer (retroactive)

If this rule had existed at commit time, the merge commit `384901e` would have carried:

```
UI-Copy-Probe: 29 claims swept (22 anchored / 7 planned / 0 deleted)
```

(retroactively logged here; not appended to the historical commit since v2.3 didn't exist yet.)

## 4. Reviewer audit hooks

Codex / Opus 4.7 / future Workbench reviewer can sample any 1-3 rows in the table and verify the anchor by:

```bash
# Sample row #6 (archiveBundle distinction):
sed -n '140,164p' src/well_harness/static/workbench.js | grep -n archiveBundle

# Sample row #14 (knowledge schema 9 fields):
sed -n '500,545p' src/well_harness/static/workbench.html | grep -c '<textarea'

# Sample row #23 (SHA256 vs commit-SHA):
grep -n 'sha256\|commit_sha' src/well_harness/workbench_bundle.py | head -10
```

Each anchor in column 5 must produce a non-empty match. Empty match = audit failure = treat as fabricated claim per v2.3 失效条件.

## 5. Provenance

- Inventory rows 1–4 / 7 / 10 / 13 / 15 / 21 / 24–25 / 26–29: derived from final-state copy at `955f61c`
- Inventory rows 5–6: anchor traced by Codex R3 finding `R3-F1` (workbench.js:140-164)
- Inventory rows 8–9: anchor traced by Codex R3 finding `R3-F2` (workbench.html 3-column ids; demo.html lever panel)
- Inventory rows 11–13: anchor traced by Codex R3 finding `R3-F2` (no demo-mode UI)
- Inventory row 14: anchor traced by Codex R4 NIT (workbench.html:506-540 — 9 textareas not 5)
- Inventory rows 17–21: anchor traced by Codex R3 finding `R3-F3` (Approval Center static shell)
- Inventory row 23: anchor traced by Codex R3 finding `R3-F4` (SHA256 not commit SHA)

Codex review log artefacts (round numbers, finding IDs) at `.planning/retrospectives/RETRO-V61-054-ui-copy-probe-birth.md` §3.

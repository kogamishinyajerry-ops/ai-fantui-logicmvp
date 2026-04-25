---
gate: GATE-P43-PLAN-v9-AMEND
parent_plan: P43-00-PLAN.md v8 → v9
requester: Claude App Opus 4.7 (Solo Executor)
triggered_by: P43-02.5-00-PLAN v4.2 (HEAD tbd · post Codex r5 需修正·信号弱 text-consistency · 3 delta batched · r3/r4/r5 required all addressed · Kogami R4 arbitration NOT needed per r5 path recommendation)
date: 2026-04-21
classification: Parent-plan §3d whitelist amend · batches Test + Docs entries (D5=A one roundtrip)
urgency: blocks Step E only · Steps B/C/D1/D2 can proceed in parallel
status: DRAFT · awaiting user submission to Kogami
---

# GATE-P43-PLAN v9 Amend Request · Batched

## Summary

P43-02.5 v4.1 plan requires **three §3d whitelist entries** that are not currently authorized by P43-00 v8 (2 Test Whitelist mandatory · 2 Docs Whitelist optional · 3 total new entries · Delta 2 groups 2 files into one logical delta). Per D5=A executor decision (v4.1 Codex r4 reconfirmed), batch all into one Kogami roundtrip to minimize amend overhead (v8 precedent set by the 8-entry Kogami Option A amend on 2026-04-21).

## Requested deltas

### Delta 1 (mandatory) — Test Whitelist +1 (unit · schema alignment)

| 新建测试 | 负责 Phase | 用途 |
|---------|----------|------|
| `tests/test_p43_02_5_c919_panel_schema_alignment.py` | P43-02.5 | 断言 `#chain-topology-c919-etras` 的 `data-node` attribute 值集合 ⊂ (spec `components` id set · 17个 ∪ spec `logic_nodes` id set · 5个) · annotation 节点 (`data-annotation="true"`) 不参与断言 · 防 YAML/adapter spec 未来改动后 panel 悄悄 drift · **静态 schema 断言 · 不覆盖运行时 DOM/event flow**（Codex r3 R3 要求用 Delta 3 补覆盖） |

**Rationale**: Codex r2 R3 发现 v2 的 Q1=B "merge 到 tests/test_c919_etras_adapter.py" 治理依据误述（父计划未授权此既有文件用于 P43-02.5 新断言）。v3 Q1=A pivot 到新建文件，严格遵循父计划 §3d:297-315 `test_p43_*` 前缀约定。文件名 `test_p43_02_5_*` 遵循 decimal-phase naming 便于与 P43-03/04 区分。

**Precedent reference**: v8 amend 新增的 `tests/test_p43_freeze_gate.py` / `test_p43_dual_sha_manifest.py` / `test_p43_clarification_stable_ids.py` 等皆 `test_p43_*` 前缀 · 此 delta 同 pattern。

### Delta 3 (mandatory · v4 新增 Codex r3 R3) — Test Whitelist +1 (E2E · deploy flow)

| 新建测试 | 负责 Phase | 用途 |
|---------|----------|------|
| `tests/e2e/test_p43_02_5_c919_panel_deploy_flow.py` | P43-02.5 | **Backend-only integration test** (v4.1 Codex r4 R1 修正 · 不走 DOM) · 使用 `tests/e2e/conftest.py` 既有 subprocess+HTTP fixture (boots demo_server on port 8799 · adapter:97 onwards)· 脚本化 Exit #25 "Unlock→deploy 完整链演示": 构造 snapshot dict (TRA=-14 + atltla=true + apwtla=true + tls_a/b unlock + pylon_unlock + pls_locked=false + tr_position=90 + trcu_power=true + lock_unlock_confirm_s=0.4 + tr_position_deployed_confirm_s=0.5 + tr_stowed_locked_confirm_s=0.0) + POST `/api/system-snapshot` → 断言 response `truth_evaluation.active_logic_node_ids` 含全 4 truth-tracked ln_* (eicu_cmd2/eicu_cmd3/tr_command3_enable/fadec_deploy_command) + `asserted_component_values.fadec_deploy_command=true` + `completion_reached=true` · 防 Q6=B 19 控件 panel 未来改动后静态 schema-alignment 漏 flow-level drift |

**Rationale**: Codex r3 明确指出 `test_p43_02_5_c919_panel_schema_alignment.py` (Delta 1) 只断言静态 `data-node ⊂ spec ids`，无法验证 unlock→deploy 运行时 flow。Delta 3 **v4.1 修正**: 文件路径从 flat `tests/` 移到 `tests/e2e/` 子树（与既有 `tests/e2e/conftest.py` fixture 同 scope · r4 指出 flat path 拿不到 subprocess+HTTP fixture）· 且改为 **backend-only integration test** 不走 DOM (repo 无 Playwright stack · `pyproject.toml:30` 确认)· 仍能覆盖 Exit #25 flow 的 adapter-boundary 部分 · UI DOM 部分通过 Exit #25 手工 browser inspection (human-eye · §4 列出) 覆盖。

### Delta 2 (optional · recommended) — Docs Whitelist +2

| 新建文件 | 负责 Phase | 用途 |
|---------|----------|------|
| `.planning/phases/P43-02.5-c919-etras-reference-panel/reference-panel.svg` | P43-02.5 | Hand-crafted SVG signal-flow 面板的独立 artifact 导出 · 供 P43-05 plan 起草时 optional diff-match 参考（P43-05 自主决定是否采纳）|
| `.planning/phases/P43-02.5-c919-etras-reference-panel/reference-panel-topology.json` | P43-02.5 | Normalized topology `{nodes:[{id,kind,col,x,y}], edges:[{from,to}]}` · 供 P43-05 plan 起草时 optional 拓扑 diff-match · 比 raw SVG DOM 更稳健 |

**Rationale**: Codex r2 P3 修正 v2 plan 错误措辞 "docs whitelist per-phase 已涵盖"。父计划 v8 §3d Docs Whitelist 实际只明授 `docs/` 下文件（P43-00:287-294）。`.planning/phases/<phase>/reports/` 路径仅是 P43-02 precedent（P43-02-00:188,254,382,481），不是 parent-plan blanket 授权。

**Alternative降级路径 (Q4=A')**: 若 Kogami 拒 Delta 2 · P43-02.5 将 artifact 改放 `reports/p43-02-5-c919-reference-panel/` 目录（precedent-backed 而非 new whitelist entry），**Test Whitelist Delta 1 + Delta 3 不受影响**（v4.1 Codex r4 Polish 修正 · 原 "Delta 1 不受影响" 遗漏 Delta 3 E2E）。

## Approval options (Kogami single choice)

- **Option A** · Approve Delta 1 + Delta 2 + Delta 3 · plan v4.2 继续执行 · Step E 可落 artifact 到 phase 文件夹 · Delta 3 backend-flow test 补运行时 flow 覆盖
- **Option B** · Approve Delta 1 + Delta 3 · skip Delta 2 · P43-02.5 plan 降级 Q4=A'（artifact 改放 reports/ precedent path）· **Executor 建议**（unit + E2E test 均必须 · docs 可降级）
- **Option C** · Approve only Delta 1 · skip Delta 2 + Delta 3 · 破 Codex r3 R3 闭环 · 不推荐
- **Option D** · Rework · Kogami 指出具体不妥之处 · executor path ① 修正后重提 v10 amend

## Impact assessment

- **Scope**: 三条 §3d whitelist 新建 entry (Delta 1 + Delta 3 mandatory · Delta 2 optional) · 不改 existing entries · 不破既有 4 gate (P43-PLAN v8 / P43-01-CLOSURE / P43-02-BATCH-PLAN-QUALITY / 本 amend)
- **Governance integrity**: Delta 1 + Delta 3 严格符 `test_p43_*` prefix 约定 · Delta 2 属 per-phase optional artifact · 均为 L1 additive
- **Precedent**: v8 一次性批准 8 个 delta · 本轮仅 3 个（保守）
- **Risk**: Delta 1 / 3 不 approve 会 block P43-02.5 Step E · 但 Steps B/C/D1/D2 可并行进行 · 不影响用户"完整开发"体验
- **Rollback**: 三 delta 均 L1 additive · 若 approve 后回滚只需 `git revert`

## Signature

**Requester**: Claude App Opus 4.7 (Solo Executor · v5.2 solo-signed + v5.3 addendum)
**Signed**: 2026-04-21
**Next action after Kogami decision**: Update `.planning/phases/P43-control-logic-workbench/P43-00-PLAN.md` v8 → v9 with approved delta(s) in §3d table · then continue P43-02.5 execution.

---
phase: P36
plan: P36-05
title: Closure — thrust-reverser docx 真实化完成，等 Kogami GATE-P36β-CLOSURE
status: drafted · Pending GATE-P36β-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P36β-PLAN Approved (Kogami 2026-04-20, Q1-Q5 全部由 Executor 推荐决定并 Kogami 批)
  - P36β-01 → P36β-04 executed in order, green
---

# P36β · thrust-reverser docx 真实化 — Closure

## 执行摘要

按 Kogami 2026-04-20 "Go P36β" 指令 + D1=A / D2=C / D3=Kogami 自裁 / D4=只登记 + Q1-Q5 全部由 Executor 推荐决定获 Kogami 批 + `GATE-P36β-PLAN: Approved`，P36β 按 Plan 顺序 P36β-01 → P36β-05 把 `Downloads/控制逻辑(1).docx` 建立为 `thrust-reverser` 链路的追溯性权威上游。

**零代码行为改动，零阈值改动，零 YAML value 改动，零既有测试断言改动。** 纯证迹升级。

**三轨回归零 delta**（default 762 / e2e 49 / adversarial 1 全部 identical vs P35 head），符合 P36β 无测试改动的设计。

升级 P35 registry row 1：`thrust-reverser | demonstrative | Upgrade pending` → `thrust-reverser | certified | In use`。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact | Commit |
|---|------|------|---------------|--------|
| P36β-00 | Tier 1 Plan doc | ✅ Done | `.planning/phases/P36-thrust-reverser-docx-backfill/P36-00-PLAN.md`（383 行 · 5 counter · Q1-Q5）| `a078b6c` |
| P36β-01 | W1 · docx 入库 + SHA | ✅ Done | `uploads/20260409-thrust-reverser-control-logic.docx` (SHA256 `6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5` · 230,930 bytes · 57 段 · 2 表 · 1 EMF 图)| `b43ac2e` |
| P36β-02 | W2 · Intake packet 精益版 | ✅ Done | `src/well_harness/adapters/thrust_reverser_intake_packet.py`（120 行 · 3 SourceDocumentRef · 业务 fields 空）| `bcdf91b` |
| P36β-03 | W3 · YAML 头 docx § 引用 | ✅ Done | `config/hardware/thrust_reverser_hardware_v1.yaml` 头 +24 行（`parameters:` 段字节级不变）| `0be39c6` |
| P36β-04 | W4 · Traceability matrix | ✅ Done | `docs/thrust_reverser/traceability_matrix.md`（241 行 · 5 表 + Appendix A 6 open assumptions）| `8198e1c` |
| P36β-05 | W5 · 收口（registry 升级 + ROADMAP + STATE + closure + Notion DECISION）| **Pending GATE-P36β-CLOSURE (Kogami)** | 本文档 + registry row 1 升级 + ROADMAP + STATE + Notion DECISION 草案 | (本 commit) |

## 三轨回归证据

### 默认 pytest lane

```
PYTHONPATH=src python3 -m pytest tests/ --tb=no -q
→ 762 passed, 1 skipped, 49 deselected, 1 warning in 95.66s (0:01:35)
```

**Delta vs P35 baseline (762 passed)：** 0 · identical · 零 delta（P36β 不加测试不改代码，identical 是预期结果）。

### Opt-in e2e lane

```
PYTHONPATH=src python3 -m pytest tests/ -m e2e --tb=no -q
→ 49 passed, 763 deselected, 1 warning in 2.89s
```

**Delta vs P35 baseline：** 0 · identical。

### Adversarial live lane（via e2e wrapper）

```
PYTHONPATH=src python3 -m pytest tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes -v -m e2e
→ 1 passed in 0.27s
```

**Delta vs P35 baseline：** 0 · identical（8/8 adversarial 断言在 wrapper 内部通过）。

## 代码侧 invariants（自审确认）

P36β 应改动的文件域：

**新增（3 files）**
- ✅ `uploads/20260409-thrust-reverser-control-logic.docx`（P36β-01, binary）
- ✅ `src/well_harness/adapters/thrust_reverser_intake_packet.py`（P36β-02, 120 行）
- ✅ `docs/thrust_reverser/traceability_matrix.md`（P36β-04, 241 行）

**修改（3 files, annotations only）**
- ✅ `config/hardware/thrust_reverser_hardware_v1.yaml`（P36β-03, +24 行头注释 · `parameters:` 段字节级不变）
- ✅ `docs/provenance/adapter_truth_levels.md`（P36β-05, row 1 in-place 升级 · 其他 4 行字节级不变）
- ✅ `.planning/ROADMAP.md` + `.planning/STATE.md`（P36β-05）+ `.planning/phases/P36-thrust-reverser-docx-backfill/P36-00-PLAN.md`（P36β-00）+ 本 closure（P36β-05）

**不应该出现 (verified 字节级不变)：**
- `src/well_harness/controller.py` —— 整个 DeployController 类
- `src/well_harness/models.py` —— 整个 HarnessConfig dataclass
- `config/hardware/thrust_reverser_hardware_v1.yaml` 的 `parameters:` 段
- `tests/test_controller*.py` 所有断言
- `src/well_harness/adapters/__init__.py`（intake packet 不注册，遵循现有 convention · 详见 P36β-02 commit message minor scope adjustment 注）
- P34 / P35 任何 commit 的文件（除 P35 registry row 1）
- demo_server / static / 前端
- JSON schema / ControllerTruthMetadata schema

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — 本 closure 不触发 main advance；P36β commit 全走 `codex/p36-thrust-reverser-docx-backfill` 独立分支；non-FF merge (Option M 保 SHA) 到 main 等 Kogami 签 `GATE-P36β-CLOSURE: Approved` 后由 Executor 执行
- ✅ **R2 不自签 Gate** — P36β-00 Plan 由 Kogami 签 `GATE-P36β-PLAN: Approved`（Q1-Q5 全 Executor 推荐 Kogami 批）；本 closure 等 `GATE-P36β-CLOSURE: Approved`
- ✅ **R3 Tier 1 adversarial** — P36β-00 Plan §4「Tier 1 对抗性自审」已交 5 条 counterargument（C1-C5）+ 就地缓解：C1（精益 certified 语义严谨性）↔ registry notes 明示 `truth lives in controller.py + yaml`；C2（docx SHA 校验）↔ SHA 固化在 5 位置；C3（Open Assumption 被视为漏洞）↔ Appendix A 公开登记；C4（code 领先 docx）↔ matrix 如实记录；C5（YAML freeze rule）↔ 只加注释不改 value
- ✅ **R4 不自选下一 Phase 方向** — P36β 由 Kogami 2026-04-20 "Go" 明示发起；下一 Phase 方向（P37 workbench spec / P38 SHA 校验 / 其他）留给 Kogami 在 P36β closeout 后**再次明示**（R4 · 不自选）
- ✅ **R5 证迹先行** — 本 Phase 是证迹先行第二轮 β 段；docx 入库建立 thrust_reverser 的真实上游；6 处 Open Assumption 在 Appendix A 明示未决是"诚实证迹"；V1 警报自我修正后确认 code/docx 实际对齐良好

## Q1-Q5 仲裁落地结果

| Open Question | Executor 推荐 · Kogami 2026-04-20 批 | 落地位置 |
|---|---|---|
| Q1 · SW2 触发角度来源 | **A** · Executor 假设镜像 SW1 (-5.0°/-9.8°) | Matrix 表 5 行 4-5 · Appendix A.1 |
| Q2 · Deploy 90% VDT 阈值来源 | **B** · 行业默认 "VDT > 90% 完全展开" | Matrix 表 5 行 9 · Appendix A.2 |
| Q3 · TLS/PLS 解锁延迟来源 | **A** · Kogami 自裁 · 待 sign-off | Matrix 表 5 行 10-11 · Appendix A.3 |
| Q4 · Deploy rate 来源 | **A** · Kogami 自裁 · 待 sign-off | Matrix 表 5 行 12 · Appendix A.4 |
| Q5 · docx authority 字段 | **A** · Kogami 自裁 · 具体签准方 Appendix A.6 待 sign-off | Intake packet notes · YAML 头 · Matrix Appendix A.6 · Registry row 1 authority 字段 |

## Tier 1 5 条反驳落地结果

| 反驳 (来自 P36β-00 Plan §4) | 缓解 |
|---|---|
| C1 · W2 精益模式下 thrust_reverser "certified" 语义不严谨 | Registry row 1 notes 明示 `truth lives in controller.py + yaml (no workbench spec per D1=A)`；535 LOC 既有测试保障 controller.py 行为；matrix 表 4 建立 docx↔code 映射；未来 P37 可独立补 workbench spec |
| C2 · docx 改动后 SHA mismatch 无 CI 校验 | SHA 固化到 **5 个位置**（W1 commit msg / W2 intake notes / W3 YAML 头 / W4 matrix / W5 registry notes）· CI-level SHA enforcement 留 P38 独立 Phase |
| C3 · Q1-Q4 Executor 假设 / Kogami 待仲裁项被视为证迹漏洞 | Appendix A 显式中英双语登记；registry row 1 notes 含 `6 Appendix A open assumptions pending sign-off` —— 诚实而非粉饰 |
| C4 · code 有 docx 没覆盖的常数 = code 实际领先 docx | Matrix 表 5 如实标"⚠️ docx 无"；Appendix A.6 请 Kogami 明示 docx authority 级别；registry authority = "Kogami 自裁" 正面承认 |
| C5 · YAML freeze rule "Do NOT modify controller.py" 会不会被违反 | **未违反**：controller.py / models.py / YAML values 字节级验证不变；只加注释；closure §代码侧 invariants 列明 |

## V1 自我修正记录（决策透明化）

P36β outline 起草时（2026-04-20 早些）报过 V1 顾虑："docx 工作逻辑 3 (6 条件 AND) 与 controller.py logic3 实现不对齐（代码可能只实现 logic1）"。

P36β-04 matrix 执行前精确对账 `controller.py:1-183`：

| 组 | docx 条件数 | code 条件数 | 实际对账 |
|----|------------|------------|---------|
| logic1 | 3 | 4 | code 多 `sw1` DIU 内部触发（docx §45 提及但放在"工作过程"而非"工作逻辑 1" list）· **层次差异，不是冲突** |
| logic2 | 5 | 5 | ✅ 完全 1:1 |
| logic3 | 6 | 6 | ✅ 完全 1:1（含 `n1k < max_n1k_deploy_limit` + `tra ≤ -11.74°`）|
| logic4 | 4 | 4 | ✅ 完全 1:1 |

**结论：** V1 警报降级为误报。`code` 与 `docx` 在 4 组工作逻辑的条件数、阈值数、语义上都对齐良好。这大幅降低了 P36β 风险。

本记录透明留存是对 "R3 Tier 1 adversarial" 要求的延伸——**Executor 承认 own 的预判不准**，纠偏过程明示审计可追。

## Notion DECISION 草案（等 GATE-P36β-CLOSURE 后贴入控制塔）

**目标页：** 控制塔 `33cc68942bed8136b5c9f9ba5b4b44ec`（P34 / P35 DECISION 同页）

**块内容：**

```markdown
## P36β DECISION · v5.2 solo-signed (2026-04-20) · thrust-reverser docx 真实化 (demonstrative → certified)

**Phase**: P36β — 证迹补完第二轮 β 段
**Status**: Executed & Green; Awaiting GATE-P36β-CLOSURE (Kogami)
**Gates**: `GATE-P36β-PLAN: Approved` (Kogami 2026-04-20, Q1-Q5 全 Executor 推荐 Kogami 批) · `GATE-P36β-CLOSURE: Pending`

### Directive context

Kogami 2026-04-20: "Go P36β" + D1=A 精益 / D2=C 混合 / D3=Kogami 自裁 / D4=只登记 + Q1-Q5 delegated to Executor recommendation.

### docx 输入证迹

- File: `uploads/20260409-thrust-reverser-control-logic.docx`
- SHA256: `6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5`
- Size: 230,930 bytes · 57 paragraphs · 2 tables · 1 media (word/media/image1.emf)
- Authority: Kogami 自裁 (具体签准方待 Appendix A.6 明示)

### Artefacts (git-tracked, branch `codex/p36-thrust-reverser-docx-backfill` base main aabc548)

- Plan: `.planning/phases/P36-thrust-reverser-docx-backfill/P36-00-PLAN.md` (383 行 · commit `a078b6c`)
- docx: `uploads/20260409-thrust-reverser-control-logic.docx` (commit `b43ac2e`)
- Intake packet: `src/well_harness/adapters/thrust_reverser_intake_packet.py` (120 行 · 3 SourceDocumentRef · 业务 fields 空 · commit `bcdf91b`)
- YAML: `config/hardware/thrust_reverser_hardware_v1.yaml` 头 +24 行 (parameters 字节级不变 · commit `0be39c6`)
- Matrix: `docs/thrust_reverser/traceability_matrix.md` (241 行 · 5 tables + Appendix A 6 open assumptions · commit `8198e1c`)
- Closure: `.planning/phases/P36-thrust-reverser-docx-backfill/P36-05-CLOSURE.md` (本文档 · commit 待 P36β-05)

### Regression evidence (三轨)

- default pytest: **762 passed** / 1 skipped / 49 deselected in 95.66s (identical to P35 baseline, zero delta)
- opt-in e2e: **49 passed** / 763 deselected in 2.89s (identical)
- adversarial wrapper: **1 passed** in 0.27s (8/8 inside identical)

### Code invariants (verified byte-level)

- controller.py / models.py: 字节级不变
- YAML parameters 段: 字节级不变
- 既有测试断言: 字节级不变

### Registry row 1 升级

(P35α 版) `thrust-reverser | demonstrative | Upgrade pending | Downloads/控制逻辑(1).docx (拟 P36β 入库) | ...`
→ (P36β 升级) `thrust-reverser | certified | In use | uploads/20260409-thrust-reverser-control-logic.docx | Kogami 自裁 | ...`

### 4 work-logic traceability (matrix 表 4)

| docx § | 条件数 (docx/code) | code location |
|--------|-------------------|---------------|
| §47 工作逻辑 1 | 3/4 (code + sw1 DIU) | controller.py:26-49 |
| §49 工作逻辑 2 | 5/5 (1:1) | controller.py:50-68 |
| §51 工作逻辑 3 | 6/6 (1:1) | controller.py:69-106 |
| §53 工作逻辑 4 | 4/4 (1:1) | controller.py:107-130 |

### 13 threshold constants (matrix 表 5)

- ✅ 7 直接 trace docx (logic1 6ft / SW1 ±1.4/-6.2° / TRA -11.74° / travel -32°/0°)
- ⚠️ 2 Executor assumed (SW2 ±5.0/-9.8° mirroring SW1) · Appendix A.1
- ⚠️ 4 Kogami 待仲裁 (deploy_90 / tls_delay / pls_delay / deploy_rate) · Appendix A.2-A.4
- ✅ 1 per-snapshot structural match (max_n1k_deploy_limit)

### Appendix A · 6 open assumptions pending sign-off

A.1 SW2 角度 · A.2 Deploy 90% VDT · A.3 TLS/PLS unlock delays · A.4 Deploy rate · A.5 Fault modes (docx §58 "不考虑") · A.6 docx authority (author/version/sign-off party)

### V1 self-correction

P36β outline-phase V1 alarm "docx logic3 与 code 不对齐" downgraded to false alarm after precise code review; 4 logic groups 在 code/docx 对齐良好。Transparency record: Executor 承认预判不准，纠偏过程审计可追。

### Tier 1 counterargument coverage

All 5 counterarguments (C1-C5) mitigated; see closure §Tier 1 5 条反驳落地结果。

### Next phase

留给 Kogami 明示（候选：P37 thrust-reverser workbench spec builder · 或 P38 CI-level provenance SHA enforcement · 或其他方向）— R4 不自选。

Execution-by: opus47-claudeapp-solo · v5.2
```

## 风险与已知 gap

| 事项 | 状态 | 处置 |
|------|------|------|
| 6 Appendix A open assumptions 待 authority sign-off | Known | 等 Kogami 未来补 · 已在 registry notes + matrix 公开登记 |
| P34 PDF 未同期入库 uploads/ (P34 intake packet 引用但路径实际不存在) | Known gap | 建议独立 Phase 处理（uploads convention 已在 P36β-01 建立, 回填 P34 PDF 技术上可行）|
| CI 无 SHA 校验 enforcement | Known | 留 P38 独立 Phase (Kogami 决策推进与否) |
| thrust_reverser 不走 workbench spec pipeline (D1=A 精益) | Design choice | 未来 P37 可补 `build_thrust_reverser_workbench_spec()` · 本 intake packet 设计为 trivially replaceable |

## 待 Kogami 的一个 Gate 签字

### `GATE-P36β-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P36β branch 可以合入 origin/main。

**Executor 在 Gate 签字后执行**（一次性脚本，同 P34 / P35 Option M 模式）：

1. `git checkout main` · `git fetch origin` · `git merge --no-ff codex/p36-thrust-reverser-docx-backfill -m "..."` · `git push origin main`（SHA 保留：`a078b6c` / `b43ac2e` / `bcdf91b` / `0be39c6` / `8198e1c` / 本 commit）
2. Notion 控制塔页 `33cc68942bed8136b5c9f9ba5b4b44ec` append 上方 "Notion DECISION 草案"（Pending）然后 flip Pending → Approved (Kogami YYYY-MM-DD)
3. 删本地 merged 分支 `codex/p36-thrust-reverser-docx-backfill`
4. 向 Kogami 请示下一 Phase 方向（候选：P37 workbench spec / P38 SHA enforcement / 其他 / R4 不自选）

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P36β-CLOSURE: Approved` (Kogami)

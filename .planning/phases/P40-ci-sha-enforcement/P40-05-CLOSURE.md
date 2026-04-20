---
phase: P40
plan: P40-05
title: Closure — CI-level SHA enforcement 完成，等 Kogami GATE-P40-CLOSURE
status: drafted · Pending GATE-P40-CLOSURE (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P40-PLAN Approved (Kogami 2026-04-20, Q1=A pytest lane · Q2=A YAML · Q3=A 硬失败)
  - P40-01 → P40-04 executed in order, green
---

# P40 · CI-level SHA enforcement — Closure

## 执行摘要

按 Kogami 2026-04-20 "继续推进" + 选 P40 作下一方向 + "Q1-Q3 由你推荐决定" 授权 + `GATE-P40-PLAN: Approved`，P40 按 Plan 顺序 P40-01 → P40-05 建立 **自动 SHA 校验** 基础设施，闭合历史 counterargument C2/C3 中反复提到的 "SHA 副本靠人工维护 · CI 无校验 · tamper 未必发现" 风险。

**核心产出：**
- `docs/provenance/sha_registry.yaml` · SoT for uploads/ SHA256 / size / authority / references
- `scripts/verify_provenance_hashes.py` · 195 行 · stream-hash + registry diff · exit 1 on drift
- `tests/test_provenance_sha_integrity.py` · 96 行 · 3 tests · default lane 每跑必检

**三轨净 +3 tests：** default 762 → **765 passed** · e2e 49 identical · adversarial 1 identical

**与前面 Phase 区别：** P40 是今日第一个 *非零 delta* 的证迹 Phase（P36β/P37/P38 都是零 delta）。+3 tests 是 P40 目的所在——CI 监控层本身就是新增功能。

## 完成的工作包

| W | 工作 | 状态 | Exit artefact | Commit |
|---|------|------|---------------|--------|
| P40-00 | Tier 1 Plan doc (379 行 · 4 counter · Q1-Q3 Executor 预签) | ✅ Done | `.planning/phases/P40-ci-sha-enforcement/P40-00-PLAN.md` | `9a589bb` |
| P40-01 | W1 · SHA registry yaml SoT | ✅ Done | `docs/provenance/sha_registry.yaml` (~45 行 · 2 files 初始条目) | `ee72271` |
| P40-02 | W2 · Verifier script | ✅ Done | `scripts/verify_provenance_hashes.py` (195 行 · stream-hash · --strict 模式) | `12f7b94` |
| P40-03 | W3 · pytest integration | ✅ Done | `tests/test_provenance_sha_integrity.py` (96 行 · 3 tests) | `bf60eb8` |
| P40-04 | 三轨回归 | ✅ Done | 本文档 §三轨证据 · default +3 符合 P40 design | (no commit) |
| P40-05 | W5 · Closure + ROADMAP + STATE + Notion DECISION | **Pending GATE-P40-CLOSURE (Kogami)** | 本文档 + ROADMAP + STATE + Notion DECISION 草案 | (本 commit) |

## 三轨回归证据

### 默认 pytest lane

```
PYTHONPATH=src python3 -m pytest tests/ --tb=no -q
→ 765 passed, 1 skipped, 49 deselected, 1 warning in 89.05s (0:01:29)
```

**Delta vs P38 baseline (762 passed)：** +3（`test_provenance_sha_integrity.py` 3 tests · 符合 P40 设计）· 零既有回归。

### Opt-in e2e lane

```
PYTHONPATH=src python3 -m pytest tests/ -m e2e --tb=no -q
→ 49 passed, 766 deselected, 1 warning in 2.61s
```

**Delta vs P38 baseline：** 0 · identical（766 deselected 是 765+1 skip 的预期计数变化，不是实测数变化）。

### Adversarial live lane（via e2e wrapper）

```
PYTHONPATH=src python3 -m pytest tests/e2e/test_demo_resilience.py::test_resilience_adversarial_truth_engine_still_passes -v -m e2e
→ 1 passed in 0.28s
```

**Delta vs P38 baseline：** 0 · identical（8/8 adversarial 内部通过）。

## 代码侧 invariants（自审确认）

**新增（3 files）：**
- ✅ `docs/provenance/sha_registry.yaml`（P40-01, 46 行）
- ✅ `scripts/verify_provenance_hashes.py`（P40-02, 195 行, 可执行）
- ✅ `tests/test_provenance_sha_integrity.py`（P40-03, 96 行）
- ✅ `.planning/phases/P40-ci-sha-enforcement/P40-00-PLAN.md` + `P40-05-CLOSURE.md`

**修改（仅 P40-05）：** `.planning/ROADMAP.md` + `.planning/STATE.md`（P40-05 本 commit）

**不应该出现 (verified 字节级不变)：**
- `src/well_harness/controller.py` / `models.py`
- `src/well_harness/adapters/*_adapter.py`（5 个真值链路 adapter 主体）
- `config/hardware/*.yaml` 任何 `parameters:` 段
- `tests/*` 既有 761 tests 断言
- `uploads/*` 任何文件内容
- 散布 SHA 文字的 5 位置（matrix / supplement / registry notes / intake notes / YAML head）—— 本 Phase 仅**校验**, 不改 SHA 文字
- 其他 P34 / P35 / P36β / P37 / P38 已签 commit 任何 artefact

## v5.2 红线合规 checklist（事后 self-verify）

- ✅ **R1 不可逆 main HEAD** — P40 commit 全走 `codex/p40-ci-sha-enforcement` 独立分支；non-FF merge (Option M) 等 Kogami 签 `GATE-P40-CLOSURE: Approved` 后由 Executor 执行
- ✅ **R2 不自签 Gate** — P40-00 Plan 由 Kogami 签 `GATE-P40-PLAN: Approved`（Q1-Q3 Executor 预签得 Kogami 明示授权）；本 closure 等 `GATE-P40-CLOSURE: Approved`
- ✅ **R3 Tier 1 adversarial** — P40-00 Plan §4 已写 4 条 counterargument（C1-C4）+ 就地缓解
- ✅ **R4 不自选下一 Phase 方向** — P40 由 Kogami 2026-04-20 从候选池中明示选（回复复制 Executor 推荐文字）；下一 Phase（P41 workbench spec · P42 runtime API · 其他）由 Kogami 在 P40 closeout 后明示
- ✅ **R5 证迹先行** — 本 Phase 是证迹先行第五轮（CI 基础设施层防 tamper · 闭合前面 Phase counter 留的基础设施债）；sha_registry.yaml 成为 uploads/ SHA 的 single source of truth，审计读 registry 一处即知所有权威 SHA

## Q1-Q3 Executor 预签 Kogami 批准结果

| Q | Executor 推荐 · Kogami 2026-04-20 批 | 落地位置 |
|---|---|---|
| Q1 · CI 集成点 | **A** · pytest default lane | `tests/test_provenance_sha_integrity.py` 3 tests 进 default lane · 无 GitHub Actions workflow 改动 |
| Q2 · SHA registry 格式 | **A** · YAML | `docs/provenance/sha_registry.yaml` · 与 hardware config 格式一致 |
| Q3 · 失败退出码 | **A** · 硬失败 exit 1 | `scripts/verify_provenance_hashes.py main()` returns 1 on any drift · pytest subprocess assert returncode==0 |

## Tier 1 4 条反驳落地结果

| 反驳（来自 P40-00 Plan §4）| 缓解 |
|---|---|
| C1 · pytest 集成 vs GitHub Actions · 细粒度差异 | pytest lane 与 762 既有 test 同 lane · 开发者本地跑即捕获 drift · 不依赖远端 workflow · 如未来需独立 GH Actions 独立 Phase 扩 |
| C2 · 散布 SHA 文字 drift 仍可能漏掉 | `references` 字段登记哪些文件应含 SHA 引用 · --strict 模式校 references 文件存在 · 散布位置 SHA 文字一致性校验留未来 Phase |
| C3 · 初始 registry SHA 信任链 | 2 文件 SHA 已在 P36β-01 + P38-01 时本地 shasum 双重校验 · 且 c919-etras PDF SHA 与 cowork P34 时期记录完全一致 · 三重验证链 |
| C4 · pyyaml 依赖 · verify script 失败时 | script 开头 `try/except ImportError` 清晰错误消息 · pyyaml 已在 pyproject.toml · P40-03 本地 `import yaml` 验证通过 |

## Registry 初始条目（P40-01 落地）

| path | sha256 | size | phase_landed | authority |
|------|--------|------|--------------|-----------|
| `uploads/20260409-thrust-reverser-control-logic.docx` | `6e457fe3…276133a5` | 230,930 | P36β | Kogami 内部自签 |
| `uploads/20260417-C919反推控制逻辑需求文档.pdf` | `dbe3f76b…276133a5` | 1,013,541 | P38 (entry via P34) | 甲方 (TRCU) 代明示 |

**Verify 结果：** 两文件 default + --strict 模式全绿。

## Update protocol（registry 头注释）

未来 `uploads/` 新增/替换文件时的刚性流程：

1. **新增文件：** 同一 Phase commit 同时加 entry 到 registry `files:` list
2. **替换文件：** 更新 SHA + size + bump `updated:` 字段 + 挂起新 Phase 解释为什么替换（绝不静默覆写）
3. **删除文件：** 一并从 registry 移除 entry + 同 Phase closure doc 说明理由

## Notion DECISION 草案（等 GATE-P40-CLOSURE 后贴入）

**目标页：** 控制塔 `33cc68942bed8136b5c9f9ba5b4b44ec`

**块内容：**

```markdown
## P40 DECISION · v5.2 solo-signed (2026-04-20) · CI-level SHA enforcement

**Phase**: P40 — 证迹补完第二轮 ε 段（CI 基础设施）
**Status**: Executed & Green; Awaiting GATE-P40-CLOSURE (Kogami)
**Gates**: `GATE-P40-PLAN: Approved` (Kogami 2026-04-20, Q1-Q3 Executor 预签授权) · `GATE-P40-CLOSURE: Pending`

### Directive context

Kogami 2026-04-20: "继续推进" 选 P40 作下一方向 + "Q1-Q3 由你推荐决定" 授权 Executor 预签.

### 核心产出

- `docs/provenance/sha_registry.yaml` (46 行 · SoT · 2 files initial) · commit `ee72271`
- `scripts/verify_provenance_hashes.py` (195 行 · stream-hash · --strict 模式) · commit `12f7b94`
- `tests/test_provenance_sha_integrity.py` (96 行 · 3 tests · default lane) · commit `bf60eb8`
- closure + ROADMAP + STATE (commit 待 P40-05)

### Regression evidence (三轨)

- default pytest: **765 passed** / 1 skipped / 49 deselected in 89.05s (+3 vs P38 baseline 762 · P40 设计预期)
- opt-in e2e: **49 passed** / 766 deselected (identical)
- adversarial wrapper: **1 passed** (8/8 inside identical)

### Code invariants (verified byte-level)

- 5 个真值链路 adapter / controller.py / models.py: 字节级不变
- uploads/* 任何文件内容: 不变
- 既有 762 tests 断言: 不变
- 散布 SHA 文字 (matrix / supplement / registry notes / intake notes / YAML head): 不变 (本 Phase 仅校验, 不改源头)

### Q1-Q3 Executor 预签 Kogami 批

- Q1=A · pytest default lane 集成
- Q2=A · YAML registry 格式
- Q3=A · 硬失败 exit 1

### Registry 初始 2 条目

| path | sha256 (short) | size | phase | authority |
|---|---|---|---|---|
| `uploads/20260409-thrust-reverser-control-logic.docx` | 6e457fe3…276133a5 | 230,930 | P36β | Kogami 内部自签 |
| `uploads/20260417-C919反推控制逻辑需求文档.pdf` | dbe3f76b…276133a5 | 1,013,541 | P38 | 甲方 (TRCU) 代明示 |

### Update protocol

新增/替换/删除 uploads/* 必须同 Phase commit 更新 registry，不能静默覆写。

### Tier 1 counterargument coverage

All 4 counterarguments (C1-C4) mitigated; see closure §Tier 1 4 条反驳落地结果。

### Next phase (R4 不自选)

- P41 · thrust-reverser workbench spec builder (补 D1=A 精益债)
- P42 · truth_level 进 ControllerTruthMetadata schema + runtime API
- P43 · adapter freeze/upgrade template 模板化
- 其他（由 Kogami 明示）

Execution-by: opus47-claudeapp-solo · v5.2
```

## 待 Kogami 的一个 Gate 签字

### `GATE-P40-CLOSURE: Approved`

触发动作：本 closure doc 被接受；P40 branch 可以合入 origin/main。

**Executor 在 Gate 签字后执行**（同 P37/P38 Option M 模式）：

1. `git checkout main` · `git merge --no-ff codex/p40-ci-sha-enforcement -m "..."` · `git push origin main`（SHA 保留：`9a589bb` / `ee72271` / `12f7b94` / `bf60eb8` / 本 commit）
2. Notion 控制塔页 append P40 DECISION（Pending）然后 flip Approved
3. 删本地 merged 分支
4. 按 P0-P4 队列请示下一方向（P40 收口后，P0-P4 队列中 P0 全部 resolved · 后续进 P1 队列）

## 风险与已知 gap（after P40）

| 事项 | 状态 | 处置 |
|------|------|------|
| 散布 SHA 文字一致性未自动校验 | Known · 明列 C2 | 未来 Phase 可扩 grep 校验，当前人工 review 在 Phase Plan/Closure |
| GitHub Actions workflow 未集成独立 step | Known · 明列 C1 | pytest lane 已足 · 未来独立 Phase 可扩 |
| thrust-reverser 无 workbench spec (D1=A) | Known | P41 候选 |
| runtime API 不感知 truth_level | Known | P42 候选 |

## 2026-04-20 全天 7 Phase 链状态

- **P31** re-land · ✅
- **P32** provenance backfill · ✅
- **P34** C919 E-TRAS adapter · ✅
- **P35α** truth-level registry + freeze banner · ✅
- **P36β** thrust-reverser docx 真实化 · ✅
- **P37** thrust-reverser 反向需求增补 · ✅
- **P38** c919-etras 证迹完整闭环 · ✅
- **P40** CI-level SHA enforcement · **Pending closure sign**

**证迹补完第二轮全套** (α→β→γ→δ→ε) **完成** · 2 certified 链路 + CI 层基础设施全整齐。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P40-CLOSURE: Approved` (Kogami)

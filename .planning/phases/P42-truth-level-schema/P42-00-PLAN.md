---
phase: P42
plan: P42-00
title: truth_level + status into ControllerTruthMetadata schema — 补 Q1=C 在 runtime 层的镜像
status: drafted · Awaiting GATE-P42-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
preconditions:
  - GATE-P41-CLOSURE Approved (Kogami 2026-04-20) → origin/main at a05bb6d
  - Kogami 2026-04-20 "连续 3 Phase" 指令第 2 位 · "GATE-P41-CLOSURE: Approved，执行 ... 进 P42"
  - P35α registry 2 维度模型 (truth_level + status) 已在 docs/provenance/adapter_truth_levels.md · 5 行已填值
  - 5 处 `ControllerTruthMetadata(...)` 实例化位置（controller_adapter.py · bleed_air / efds / landing_gear / c919_etras adapter）
non-goals:
  - 改 controller.py / models.py 任何一行（controller 真值层不动）
  - 改任何 adapter 的 eval / explain / evaluate_snapshot / load_spec 方法
  - 改 YAML parameters / 既有 docs tests 断言
  - 建 runtime API endpoint 暴露 truth_level（本 Phase 定位 schema 层 · endpoint 留 P43 或独立 Phase）
  - 改 docs/provenance/adapter_truth_levels.md 任何 5 行（schema 层与 docs 层并行 · registry 仍是 docs SoT · metadata 是 runtime 镜像）
  - rename `current_reference_workbench_spec`（P41 确认保留）
---

# P42-00 Plan · truth_level + status into ControllerTruthMetadata schema

## 0. TL;DR

Kogami 2026-04-20 "连续 3 Phase" 指令第 2 位。把 P35α registry 的 2 维 (truth_level + status) 模型镜像到 runtime schema：
- `ControllerTruthMetadata` dataclass 加 `truth_level: str` + `status: str` 字段（带默认值，向后兼容）
- JSON schema v1 extend（新增可选字段，**不 bump version**）
- 5 个 metadata instantiations 填充对应值（与 registry 表一致）
- tests 加两个断言（5 个 metadata 的 level/status 与 registry 同步）

**不做** runtime API endpoint 暴露 · 不改 controller / adapter 行为 · 不改 YAML / registry docs。

**规模：** ~200 LOC 改动 · 3 commits · ~1.5h。

## 1. 上下文

**Q1=C 在 P35α registry 的决策：** `truth_level` (enum: demonstrative / certified / placeholder) + `status` (enum: In use / Frozen / Upgrade pending / Upgrade in progress) 两维度分离。

**当前状态：**
- registry markdown (`docs/provenance/adapter_truth_levels.md`) 5 行填好
- runtime `ControllerTruthMetadata` dataclass 没有这两个字段
- 两层有 drift 风险（docs 改 registry markdown 但 metadata 还是老值）

**P42 解决：** 把 metadata 层加入字段，然后让 5 个 instantiation 填与 registry 一致的值。测试断言两层 key-value 一致（防 drift）。

## 2. Scope — 4 工作包

### W1 · `ControllerTruthMetadata` 加字段 + JSON schema extend（P42-01）

修 `src/well_harness/controller_adapter.py`:
```python
@dataclass(frozen=True)
class ControllerTruthMetadata:
    adapter_id: str
    system_id: str
    truth_kind: str
    source_of_truth: str
    description: str
    truth_level: str = "demonstrative"      # P42: default 保守 · 5 个 instance override
    status: str = "In use"                   # P42: default 多数常态 · 5 个 instance override
```

修 `docs/json_schema/controller_truth_adapter_metadata_v1.schema.json`:
- `required` 数组不变（8 项）—— 新字段 optional
- `properties` 加:
  ```json
  "truth_level": {"type": "string", "enum": ["demonstrative", "certified", "placeholder"]},
  "status": {"type": "string", "enum": ["In use", "Frozen", "Upgrade pending", "Upgrade in progress"]}
  ```
- `additionalProperties: false` 保留（新字段是 properties 里的，不破此约束）
- `$id` 不变（v1）· Schema version 不 bump
- 标题 description 加一行说明 "P42 (2026-04-20) extended with truth_level + status (both optional, backward compat)"

### W2 · 5 个 metadata instantiations 填值（P42-02）

与 registry 5 行一一对齐：

| metadata instance | file:line | truth_level | status |
|-------------------|-----------|-------------|--------|
| `REFERENCE_DEPLOY_CONTROLLER_METADATA` | controller_adapter.py:85 | `certified` | `In use` |
| `BLEED_AIR_CONTROLLER_METADATA` | bleed_air_adapter.py:60 | `demonstrative` | `Frozen` |
| `EFDS_CONTROLLER_METADATA` | efds_adapter.py:37 | `demonstrative` | `Frozen` |
| `LANDING_GEAR_CONTROLLER_METADATA` | landing_gear_adapter.py:43 | `demonstrative` | `Frozen` |
| `C919_ETRAS_CONTROLLER_METADATA` | c919_etras_adapter.py:148 | `certified` | `In use` |

**注意：** `REFERENCE_DEPLOY_CONTROLLER_METADATA` 的 `system_id` 是 `"reference_thrust_reverser_deploy"`，不是 `"thrust-reverser"`。本 Phase **不 rename** system_id（会破既有 downstream）——而是在 test 里用 map 映射。

### W3 · Tests（P42-03）

修 `tests/test_controller_truth_adapter_metadata_schema.py`:
- 加 JSON schema 断言覆盖 truth_level + status 可选字段
- 加 metadata 对象断言（`REFERENCE_DEPLOY_CONTROLLER_METADATA.truth_level == "certified"`）

新增 `tests/test_metadata_registry_consistency.py`（~60 行 · 防 drift）:
- 读 `docs/provenance/adapter_truth_levels.md` 5 行（markdown table parse）或直接 hardcode 期望 map（因为 markdown parse 脆弱 · 选 hardcode 更稳）
- 断言 5 个 metadata instance 的 (truth_level, status) 与 hardcode map 一致
- 断言 hardcode map 与 registry markdown 表格手工同步（人工 review on any change · this test 只校 runtime 层，不校 docs 层）

### W4 · 收口（P42-05）

- 三轨（期望 default 768+，新增 W3 tests 数量）
- ROADMAP + STATE + closure doc + Notion DECISION append
- push · 等 GATE-P42-CLOSURE

---

## 3. Non-goals — 严格禁止

已在 frontmatter 列。强调：
- **不**改 controller.py / models.py / current_reference_workbench_spec
- **不**改 adapter behavior（evaluate / explain / load_spec）
- **不**建 runtime API endpoint（`GET /api/adapters` 返 truth_level 等）
- **不**改 registry docs 5 行
- **不**改 JSON schema $id 或 version const（保 v1）
- **不**改 `REFERENCE_DEPLOY_CONTROLLER_METADATA` 的 system_id（避免 rename 冲击）

---

## 4. Tier 1 对抗性自审（≥3 条，交付 4 条）

### C1 · "schema extend v1 vs bump v2 · 不 bump 会有 strict 消费者 choke"

**承认。** 缓解：
1. 当前唯一消费者是 `tools/validate_controller_truth_adapter_metadata_schema.py` + `tests/test_controller_truth_adapter_metadata_schema.py` —— 都是我们自己掌控的
2. JSON schema `additionalProperties: false` 约束仍成立（新字段在 properties 里定义，不算额外字段）
3. 旧 v1 serialized payload（不含新字段）仍 validate 通过（新字段 optional）· 新 payload 有字段也 validate 通过
4. 这是 **additive backward-compatible extension** · 行业惯例允许在 v1 加 optional 字段
5. 若未来外部消费者严格 validate，独立 Phase v2 bump 可处理 · 当前 scope 不需要

### C2 · "默认值 truth_level='demonstrative' / status='In use' · 混在一起 · 不保守"

**部分承认。** 缓解：
1. 默认值只在 dataclass 签名体现，5 个 instance 都**显式传值**覆盖默认（不依赖默认）
2. 默认值是 fallback for 未来新 adapter 没想好时（encourage explicit assignment · 但允许 quick prototype）
3. Test `test_metadata_registry_consistency.py` 校 5 instance 是显式值，不 accept default（若有人新加 adapter 忘了传值 → test 红）

### C3 · "metadata 层与 registry docs 层的 drift 风险依然存在"

**承认这是 P42 不解的核心问题。** 缓解：
1. `test_metadata_registry_consistency.py` 用 hardcode map 作桥：每次 registry 改都要同步改 test hardcode 值（人工 review on any change）
2. 如果 hardcode map 与 metadata instance 不一致 → test 红
3. **未来 Phase 候选（P45 或类似）：** 让 registry yaml-ify（类似 P40 sha_registry 模式）并成为 metadata 加载源 · 这样 docs markdown 降为 readable view · runtime 消费 yaml · 单 SoT
4. 当前 P42 不走此路因为：需要 5 adapter 改为 lazy init from yaml · scope 翻倍 · Kogami "连续 3 Phase" 时间预算不够
5. Acceptable risk: hardcode map 是 low-drift 维护面 · 6 values total · 人工 sync 不重

### C4 · "test_metadata_registry_consistency.py hardcode 5 行值 · 违反 DRY · 与 registry 表重复"

**承认。** 缓解：
1. DRY 违反是为简单性 trade-off · Registry markdown 表是人类可读 · 机械解析脆弱
2. 6 values · 改动频率低 · 人工维护面可接受
3. 选项 B · 用 yaml-ify registry (pair with hardcode test hardcode) 留 P45 候选

---

## 5. Open Questions — Kogami 签 GATE-P42-PLAN 时仲裁

### Q1 · Schema extend v1 vs bump v2
- **A · Extend v1**（backward compat · 新字段 optional · `$id` 不变）
- **B · Bump v2**（strict version · 所有 payload 需带 `$schema: v2`）
- **Executor 建议：A**（additive change · 无外部 strict consumer · 省版本管理成本）

### Q2 · truth_level 默认值策略
- **A · 有默认**（`demonstrative` / `In use`）· dataclass 签名带默认 · 5 instance 显式 override · future adapter 若忘填默认非报错
- **B · required**（无默认）· future adapter 必须显式传值 · 但需破坏已有 5 adapter instantiation
- **C · 混合**（有默认 · 但 test 校 5 现有 instance 是显式值非默认 · future adapter 仍可依赖默认）
- **Executor 建议：C**（默认 for forward compat · test 强制 current 5 显式）

### Q3 · Runtime API surface 是否本 Phase 做
- **A · 本 Phase 做**（`GET /api/adapters` 返 level + status · demo_server 改 · 额外 ~2h）
- **B · 推后到独立 Phase P44**（scope 管理 · P42 聚焦 schema 层）
- **Executor 建议：B**（今日连 3 Phase 疲劳 · 独立 Phase 处理更好）

---

## 6. Sub-phase 分解

- P42-00 · Plan（本文 · 等 GATE-P42-PLAN）
- P42-01 · W1 dataclass + JSON schema extend · 约 30 min
- P42-02 · W2 5 instantiations 填值 · 约 20 min（5 个文件小改）
- P42-03 · W3 tests（metadata schema test 扩 + 新 consistency test）· 约 30 min
- P42-04 · 三轨（default 期望 ~770 · 本地验证）· 15 min
- P42-05 · 收口 · 40 min

**总 4-5 commits · ~2h**

---

## 7. Exit Criteria

- `ControllerTruthMetadata` 加 truth_level + status 字段（带默认）
- JSON schema v1 extend · 加 2 optional properties · additionalProperties: false 保
- 5 metadata instantiations 显式填值 · 与 registry 对齐
- `test_controller_truth_adapter_metadata_schema.py` 扩 · `test_metadata_registry_consistency.py` 新
- 三轨 default 768+ / e2e 49 / adversarial 1
- ROADMAP + STATE + closure · Notion DECISION · push branch

---

## 8. 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| dataclass 加默认字段破 `asdict(metadata)` 顺序 | 低 | 小 | dataclass 字段顺序保 · 新字段在最后 · asdict 返顺序稳 |
| JSON schema 消费者严格 validate 报额外字段 | 低 | 小 | 唯一消费者在我们掌控 · extend backward compat |
| controller_adapter.py REFERENCE_DEPLOY_CONTROLLER_METADATA.system_id 与 registry row 1 "thrust-reverser" 不一致（实际是 "reference_thrust_reverser_deploy"）| 已知 | 中 | test_metadata_registry_consistency 用 adapter_id → row map · 不用 system_id 做 key |
| test_metadata_registry_consistency hardcode 值写错 | 低 | 小 | 本地跑 test · 立即校 |

**回滚：** GATE-P42-CLOSURE 不批时 `git revert` 回 a05bb6d。

---

## 9. v5.2 合规

- R1 · non-FF merge 等 GATE-P42-CLOSURE
- R2 · GATE-P42-PLAN 等 Kogami 显式（含 Q1-Q3 仲裁）· GATE-P42-CLOSURE 等
- R3 · 4 条 counter 就地缓解
- R4 · Kogami 2026-04-20 "连续 3 Phase 第 2 位" 明示选 P42 · 下一 P43 已预定
- R5 · P42 对齐 runtime schema 到 P35α docs 层决策 · 消除 runtime-docs drift

---

## 10. 停点

**本 plan 不执行任何动作。等 `GATE-P42-PLAN: Approved` + Q1-Q3 仲裁。**

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P42-PLAN: Approved` (Kogami) + Q1/Q2/Q3 仲裁

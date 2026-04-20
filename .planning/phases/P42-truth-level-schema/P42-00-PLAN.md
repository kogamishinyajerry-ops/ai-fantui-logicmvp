---
phase: P42
plan: P42-00
plan_revision: v2 (post-Codex remediation)
title: truth_level + status into ControllerTruthMetadata schema — path ① full SoT + generator fix
status: re-drafted · Awaiting GATE-P42-PLAN (v2) (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
verified-by: codex-gpt54-xhigh (2026-04-20 · 3 counters integrated, 需修正 verdict resolved)
preconditions:
  - GATE-P41-CLOSURE Approved (Kogami 2026-04-20) → origin/main at a05bb6d
  - Kogami 2026-04-20 "连续 3 Phase" 指令第 2 位
  - GATE-P42-PLAN (v1) 虽已签但 Codex adversarial review 暴露 3 条结构性硬伤 · Kogami 2026-04-20 第二轮仲裁选「路径①：修 plan 后重走 GATE-P42-PLAN」
  - P35α registry 2 维度模型 (truth_level + status) 已在 docs/provenance/adapter_truth_levels.md · 5 行填值
  - P40 sha_registry.yaml 模式已验证 machine-readable SoT 是 viable 模式
non-goals:
  - 改 controller.py / models.py 任何一行（controller 真值层不动）
  - 改任何 adapter 的 eval / explain / evaluate_snapshot / load_spec 方法
  - 改 YAML parameters / 既有 docs tests 断言
  - 建 runtime API endpoint 暴露 truth_level（本 Phase 定位 schema + SoT 层 · endpoint 留 P44）
  - 改 `docs/provenance/adapter_truth_levels.md` 表格 5 行（只加"yaml 是 machine SoT" 注脚指针）
  - rename `current_reference_workbench_spec` / `REFERENCE_DEPLOY_CONTROLLER_METADATA.system_id`（P41 确认保留）
  - yaml-ify 所有 registry 列（只做核心 4 列：system_id · adapter_id · truth_level · status · 其他列留 markdown）
---

# P42-00 Plan v2 · truth_level + status — post-Codex remediation (path ①)

## 0. TL;DR · v1 → v2 差异

| 维度 | v1 plan (已废) | v2 plan (本文) |
|------|--------------|--------------|
| 默认值策略 (Q2) | C · `demonstrative` + `In use` 业务语义默认 | **D · `None` sentinel · 未赋值时序列化中消失（= pre-P42/unclassified）** |
| Schema `$id` (Q1) | A · extend v1 · description 简单记 | A · extend v1 · **明示 "字段缺失=pre-P42/unknown · 不得被下游视为已治理"** |
| registry SoT 结构 | markdown 单份 + runtime hardcode + test hardcode（三份真相） | **yaml 作 machine SoT + markdown 人类视图 + runtime 动态枚举** |
| generator (generate_adapter.py) | 未盯 | **W3 · 删 shadow class + 模板必填 truth_level/status (默认 demonstrative / Upgrade pending)** |
| consistency test | hardcode "5 已知 adapter" 行值 | **动态 importlib 扫 `ControllerTruthMetadata` 实例 + 解 yaml · 双向校** |
| 规模 | ~200 LOC · 3 commits · ~1.5h | ~380 LOC · 5-6 commits · ~3h |

**不变：** non-goals / 不改 controller.py / 不改 adapter behavior / 不改 YAML parameters / 不 rename system_id。

**v2 解决的 Codex 攻击：**
- Counter A（v1 双代语义共用一标签）→ to_dict 剥 None + schema description 明示语义修订
- Counter B（默认值把未分类伪装成已治理）→ None sentinel + generator 模板修 + dynamic inventory test
- Counter C（三份真相 · 假绿 CI）→ yaml machine SoT · markdown ↔ yaml ↔ runtime 双向闭合

---

## 1. 上下文

Kogami 2026-04-20 "连续 3 Phase" 指令第 2 位 · Q1=C (P35α 2 维模型) 要求 runtime schema 镜像 registry。

原 v1 plan 已签 GATE-P42-PLAN · Codex GPT-5.4 xhigh adversarial review（by `/codex-gpt54` · 2026-04-20 · 82,646 tokens）给出 **需修正 · 信号强** 评级 · 3 条 counter 命中：
- A：`asdict(metadata)` 真实序列化路径使 v1 extend 抹掉 provenance 语义边界
- B：业务语义默认 + `generate_adapter.py` 本地 shadow class 使新 adapter 治理缺失可静默
- C：markdown + runtime hardcode + test hardcode 三源无机器闭合 · CI 可假绿

Executor 核验 Codex 两条事实断言均真实：
- `src/well_harness/controller_adapter.py:34` 确含 `**asdict(metadata)`
- `src/well_harness/tools/generate_adapter.py:74-79` 确有 shadow class `@dataclass(frozen=True) class ControllerTruthMetadata` with 旧 5 字段 · 完全屏蔽中央定义

Executor 提路径①-③ · Kogami 2026-04-20 "路径1，修 plan 后重走 GATE-P42-PLAN" 明示选 ①。

**v2 的设计哲学：**
> runtime schema 为唯一事实表达层；yaml 为人机通读的 SoT；markdown 仅为审计版式；**三者通过 bidir test 永久绑定**。字段缺失 ≠ 字段含默认业务语义值，而是 `pre-P42/unclassified` 可被下游明确识别。

---

## 2. Scope — 6 工作包

### W1 · `ControllerTruthMetadata` 加字段 + serializer 剥 None + JSON schema extend

修 `src/well_harness/controller_adapter.py`:
```python
@dataclass(frozen=True)
class ControllerTruthMetadata:
    adapter_id: str
    system_id: str
    truth_kind: str
    source_of_truth: str
    description: str
    truth_level: str | None = None      # P42 v2: None = pre-P42/unclassified
    status: str | None = None           # P42 v2: None = pre-P42/unclassified

def controller_truth_metadata_to_dict(metadata: ControllerTruthMetadata) -> dict:
    payload = {
        "$schema": CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
        "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
        "version": CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
        **asdict(metadata),
    }
    # P42 v2: drop None governance fields to keep v1 payload shape identical
    # to pre-P42. 字段缺失 = pre-P42/unclassified · 下游不得视为已治理。
    for k in ("truth_level", "status"):
        if payload.get(k) is None:
            payload.pop(k, None)
    return payload
```

修 `docs/json_schema/controller_truth_adapter_metadata_v1.schema.json`:
- `$id` / version const 保 v1 · **required 不加新字段**
- `properties` 加:
  ```json
  "truth_level": {
    "type": "string",
    "enum": ["demonstrative", "certified", "placeholder"],
    "description": "P42 (2026-04-20) extension. 字段缺失 = pre-P42/unclassified · 下游不得视为已治理。"
  },
  "status": {
    "type": "string",
    "enum": ["In use", "Frozen", "Upgrade pending", "Upgrade in progress"],
    "description": "P42 (2026-04-20) extension. 字段缺失 = pre-P42/unclassified · 下游不得视为活跃治理链路。"
  }
  ```
- schema description head 加 "P42 (2026-04-20) extended additively in v1 · 字段缺失 semantics documented in each property's description field"

### W2 · 5 个 metadata instantiations 显式填值

与 registry 5 行严格对齐：

| instance | file | truth_level | status |
|----------|------|-------------|--------|
| `REFERENCE_DEPLOY_CONTROLLER_METADATA` | controller_adapter.py | `certified` | `In use` |
| `BLEED_AIR_CONTROLLER_METADATA` | adapters/bleed_air_adapter.py | `demonstrative` | `Frozen` |
| `EFDS_CONTROLLER_METADATA` | adapters/efds_adapter.py | `demonstrative` | `Frozen` |
| `LANDING_GEAR_CONTROLLER_METADATA` | adapters/landing_gear_adapter.py | `demonstrative` | `Frozen` |
| `C919_ETRAS_CONTROLLER_METADATA` | adapters/c919_etras_adapter.py | `certified` | `In use` |

`REFERENCE_DEPLOY_CONTROLLER_METADATA.system_id` 仍是 `"reference_thrust_reverser_deploy"`（不 rename）· registry row 1 的 `thrust-reverser` system_id 用 adapter_id 做映射桥（见 W4 yaml mapping 字段）。

### W3 · `generate_adapter.py` 模板修正（Codex Counter B 核心命中）

修 `src/well_harness/tools/generate_adapter.py`:

1. **删第 74-79 行的 shadow class 本地重定义**（`@dataclass(frozen=True) class ControllerTruthMetadata`）。`from well_harness.controller_adapter import ControllerTruthMetadata` 保留 · 模板输出直接用中央定义。
2. `GenericTruthEvaluation` 的本地 shadow class 也同样删（已有 central import）。
3. 模板 `CONTROLLER_METADATA = ControllerTruthMetadata(...)` 增强：
   ```python
   L(f"CONTROLLER_METADATA = ControllerTruthMetadata(")
   L(f'    adapter_id="{adapter_id}",')
   L(f'    system_id="{system_id}",')
   L('    truth_kind="spec-derived-generic-truth",')
   L(f'    source_of_truth="{sp}",')
   L(f'    description="Auto-generated GenericControllerTruthAdapter for {title}",')
   L('    truth_level="demonstrative",  # P42: new auto-gen adapters default demonstrative · must upgrade via Phase to certified')
   L('    status="Upgrade pending",     # P42: new auto-gen adapters start upgrade pending · NOT "In use" · forces registry + traceability work before activation')
   L(")")
   ```
4. 模板文件头 generated banner 加一行："P42 (2026-04-20): truth_level/status MUST be filled. Do not rely on dataclass defaults — new adapters start as demonstrative/Upgrade pending until upgraded via formal Phase."

**关键语义**：通过生成器产的新 adapter **必须** 显式带 `truth_level="demonstrative", status="Upgrade pending"` · 不能"In use"（防治理假阳性）· 升级流程强制走 Phase + registry 行新增。

### W4 · registry yaml machine SoT + markdown 指针（Codex Counter C 核心命中）

**新建** `docs/provenance/adapter_truth_levels.yaml`:
```yaml
# Machine-readable SoT for adapter truth-level registry.
# =======================================================================
# This file is the AUTHORITATIVE source consumed by
# tests/test_metadata_registry_consistency.py to verify three-way alignment:
#   runtime ControllerTruthMetadata instances ↔ this yaml ↔ adapter_truth_levels.md
#
# The markdown (adapter_truth_levels.md) is a human-readable VIEW; this yaml
# is the SoT. On any level/status change, edit this yaml FIRST, regenerate /
# manually sync the markdown table, and land both in one commit.
#
# Phase origin: P42 (truth_level schema + SoT alignment, 2026-04-20)
# Authority: Kogami (v5.2 Solo Mode project owner)
version: 1
updated: 2026-04-20
phase: P42
entries:
  - system_id: thrust-reverser
    adapter_id: reference_thrust_reverser_deploy_controller_v1
    metadata_const: REFERENCE_DEPLOY_CONTROLLER_METADATA
    metadata_module: well_harness.controller_adapter
    truth_level: certified
    status: In use

  - system_id: bleed-air-valve
    adapter_id: bleed_air_valve_v1
    metadata_const: BLEED_AIR_CONTROLLER_METADATA
    metadata_module: well_harness.adapters.bleed_air_adapter
    truth_level: demonstrative
    status: Frozen

  - system_id: emergency_flare_deployment_system
    adapter_id: emergency_flare_deployment_system_v1
    metadata_const: EFDS_CONTROLLER_METADATA
    metadata_module: well_harness.adapters.efds_adapter
    truth_level: demonstrative
    status: Frozen

  - system_id: minimal_landing_gear_extension
    adapter_id: minimal_landing_gear_extension_v1
    metadata_const: LANDING_GEAR_CONTROLLER_METADATA
    metadata_module: well_harness.adapters.landing_gear_adapter
    truth_level: demonstrative
    status: Frozen

  - system_id: c919-etras
    adapter_id: c919_etras_controller_v1
    metadata_const: C919_ETRAS_CONTROLLER_METADATA
    metadata_module: well_harness.adapters.c919_etras_adapter
    truth_level: certified
    status: In use
```

修 `docs/provenance/adapter_truth_levels.md` 仅加一个注脚（**不改表格 5 行**）：
```markdown
## Machine-readable SoT

This markdown is a **human-readable view**. The authoritative machine SoT is
[`adapter_truth_levels.yaml`](adapter_truth_levels.yaml) (P42, 2026-04-20).

On any registry change: edit yaml first, then sync this table. Both files
land in the same commit. `tests/test_metadata_registry_consistency.py`
enforces runtime ↔ yaml ↔ markdown-table bidirectional alignment.
```

### W5 · tests · schema extend + bidir consistency（Codex Counter C 落地）

修 `tests/test_controller_truth_adapter_metadata_schema.py`:
- 加 schema 断言覆盖 `truth_level` + `status` optional properties + 其 enum
- 加 serializer 断言：`ControllerTruthMetadata(..., truth_level=None)` → `to_dict()` 不含 `truth_level` key（保 v1 payload 形状）
- 加 serializer 断言：`ControllerTruthMetadata(..., truth_level="certified", status="In use")` → `to_dict()` 含两字段且值正确

**新建** `tests/test_metadata_registry_consistency.py` (~150 LOC · 核心 Codex Counter C 解药):
- **动态 metadata 枚举**（不 hardcode adapter list）:
  ```python
  def _discover_controller_metadata_instances() -> dict[str, ControllerTruthMetadata]:
      """Import every known adapter module, scan for module-level
      ControllerTruthMetadata instances, return {const_name: instance}."""
      # yaml 列出 entries[].metadata_module · importlib 各 module
      # 然后 inspect.getmembers(module) 筛 isinstance(x, ControllerTruthMetadata)
  ```
- **parse yaml SoT**: `yaml.safe_load("docs/provenance/adapter_truth_levels.yaml")` → entries
- **bidir assertions**:
  1. 每个 yaml entry → runtime 必有对应 metadata_const · truth_level/status 与 yaml 一致
  2. 每个 runtime discovered metadata → yaml 必有对应 entry（防"新加 adapter 忘登记"）
  3. 每个 yaml entry 的 adapter_id / system_id → markdown 表格必出现（grep 断言 · 防 markdown 忘同步）
  4. markdown 表格行数 == yaml entries 数（防漏行）
  5. 若任一 metadata instance 的 `truth_level is None` 或 `status is None` → **测试红**（生产 adapter 必填 · None 只允许给 test fixtures / pre-P42 migration state）

修 `src/well_harness/tools/test_generate_adapter.py`（若存在）或新增测试校：
- generated adapter 源码含 `truth_level="demonstrative"` + `status="Upgrade pending"`
- generated adapter 不再本地定义 `ControllerTruthMetadata` / `GenericTruthEvaluation`

### W6 · 收口

- 三轨（期望 default **767 + ~8 新增** ≈ **775**，opt-in e2e 49，adversarial wrapper 1）
- ROADMAP + STATE + closure doc + Notion DECISION append
- push `codex/p42-truth-level-schema` · 等 GATE-P42-CLOSURE

---

## 3. Non-goals — 严格禁止

已在 frontmatter 列。强调：
- **不**改 controller.py / models.py / current_reference_workbench_spec
- **不**改 adapter 行为（evaluate / explain / load_spec）
- **不**建 runtime API endpoint（留 P44）
- **不**改 registry markdown 5 行表格（只加 yaml 指针注脚）
- **不**改 JSON schema `$id` 或 version const（保 v1）
- **不** rename system_id
- **不**把 markdown registry 所有列 yaml-ify（只做 4 核心治理列 · 其他列信息密度高但 runtime 无需消费）

---

## 4. Tier 1 对抗性自审

### 原 4 条（v1 保留 · 均被 v2 缓解）

**C1 · schema extend v1 vs bump v2 · 不 bump 会有 strict 消费者 choke**
v2 缓解强化：`to_dict` 剥 None 字段使 v1 payload 形状与 pre-P42 字节一致 · schema description 文字明示 "字段缺失 = pre-P42/unclassified" · 下游消费者有明确语义线索区分。

**C2 · 默认值 `demonstrative/In use` 不保守**
v2 **推翻原方案** · 改为 None sentinel · 不再有业务语义默认 · 原 C2 攻击面直接消除。

**C3 · metadata 层与 registry docs 层 drift 风险**
v2 缓解强化：yaml 成 machine SoT · bidir test 绑定 runtime ↔ yaml ↔ markdown 三层 · drift 被动态测试拦截。

**C4 · hardcode 5 行值违反 DRY · 与 registry 重复**
v2 **推翻原方案** · 动态 importlib 扫描 + yaml 唯一 SoT · hardcode 零消失。

### v2 新增 3 条（verified-by codex-gpt54-xhigh · incorporated as C5/C6/C7）

**C5 (= Codex Counter A) · v1 双代语义共用一标签 · `asdict` 序列化路径抹 provenance 边界**
**攻击（Codex 原话简化）：** `controller_adapter.py:34 **asdict(metadata)` 真实在 payload · 旧 v1 缺字段 vs 新 v1 漏填在审计/归档/重放层面不可区分 · 签 "v1" 的消费者开始遇到语义混乱。
**v2 缓解：**
1. `to_dict` 函数在 spread 后**显式剥 None 字段** · 未治理的 metadata 序列化出来仍是 pre-P42 5 字段形状 · 下游按"字段存在 vs 字段缺失"就可识别治理状态 · 不需要 payload 层 version 升级
2. JSON schema 新字段 description 明文规定 "字段缺失 = pre-P42/unknown · 不得被下游视为已治理"
3. 未来若有外部 strict consumer → 独立 Phase 做 v2 bump · 留接口（`CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION` 常量可切）
4. Accepted risk: 字节层 pre-P42 payload 与 P42 未填 metadata 仍一致 · 用 adapter_id 做治理状态查询（查 yaml）· schema 层不承担全部识别责任

**C6 (= Codex Counter B) · 默认值把未分类伪装成已治理 · generator shadow class 使新 adapter 静默滑过**
**攻击（Codex 原话简化）：** `demonstrative/In use` 默认意味着新 adapter 忘填 = "demonstrative 活跃" 治理假阳性 · `generate_adapter.py:74-79` shadow class 还复制旧 5 字段结构 · P42 若不修 generator · 第 6 adapter 必从该洞滑过。
**v2 缓解：**
1. Q2 改 D（None sentinel）· dataclass 默认不携带业务语义 · 忘填 = 字段缺失 = 下游识别为 pre-P42/unclassified
2. W3 删 generator shadow class + 模板强制 `truth_level="demonstrative"` + `status="Upgrade pending"`（**不是** "In use"）· 新 adapter 自动进"未治理待升级"状态 · 必须走 Phase 升级才能 In use
3. W5 test 断言生产 adapter metadata instance 两字段非 None · 有人用 generator 生成但不填值 → 测试红
4. W5 test 断言 generated adapter 源码不再本地 shadow

**C7 (= Codex Counter C) · 三份真相 · CI 可假绿**
**攻击（Codex 原话简化）：** W3 旧方案 hardcode 5 行值 = runtime hardcode + markdown registry + test hardcode 三份真相 · CI 绿只证 "代码 ↔ test hardcode 一致" · 未来 registry 改某行但忘改 test hardcode · 假绿。
**v2 缓解：**
1. W4 建 `adapter_truth_levels.yaml` 作 machine SoT · 消除 "test hardcode" 这层
2. W5 test 动态 importlib 扫 metadata instance + parse yaml · 三层 (runtime ↔ yaml ↔ markdown) 双向校 · 任一层飘红立刻曝光
3. registry 改动协议加注：edit yaml first · manually sync markdown · 同 commit 落地 · 否则 CI 红

---

## 5. Open Questions — Kogami 签 GATE-P42-PLAN (v2) 时仲裁

### Q1 · Schema version 策略（v2 确认保持 A）
- **A · Extend v1 + to_dict 剥 None（v2 推荐）**：additive backward compat · 无外部 strict consumer · payload 形状等价 pre-P42 · schema description 文字规定缺失语义
- **B · Bump v2**：版本明确 · 但无外部 strict consumer → 过度工程化 · 版本管理成本高
- **Executor 建议：A + to_dict 剥 None**（v2 已消化 Codex Counter A）

### Q2 · 默认值策略（v2 从 C 改 D）
- ~~A · 有默认 `demonstrative` + `In use`~~（C6 攻击 · 推翻）
- ~~B · required 无默认~~（破 5 既有 instantiation 向后兼容 · 不选）
- ~~C · 混合~~（v1 原选 · Codex C6 证实缺陷 · 废）
- **D · `None` sentinel + to_dict 剥 None + test 强制 current 5 显式（v2 推荐）**：生产 adapter 必显式 · 未赋值时序列化中消失 · 语义清晰
- **Executor 建议：D**

### Q3 · Runtime API surface（v2 保持 B）
- A · 本 Phase 做 runtime API endpoint
- **B · 推后到独立 Phase P44**（v2 推荐 · P42 scope 已扩大 · API 留 P44）
- **Executor 建议：B**

### Q4 (v2 新增) · registry yaml 范围
- A · yaml 只含 runtime 需要的 4 列（system_id · adapter_id · truth_level · status · + metadata_const/metadata_module 引用）· 其他列（upstream_source · authority · upgrade_path · notes）留 markdown（v2 推荐 · 最小可闭合）
- B · yaml 全量 yaml-ify 所有 10 列 · markdown 成 auto-generated 视图
- **Executor 建议：A**（保 P42 scope · B 留 P45 候选）

### Q5 (v2 新增) · generator template 默认值
- A · `truth_level="demonstrative", status="Upgrade pending"`（v2 推荐 · 强制新 adapter 走 Phase 升级才 In use · 防假阳性）
- B · `truth_level=None, status=None`（依赖 bidir test 拦）
- **Executor 建议：A**（正向防御 · B 易让 generator 用户以为"None 就行"）

---

## 6. Sub-phase 分解 (v2 扩为 6)

- P42-00 · Plan v2（本文 · 等 GATE-P42-PLAN v2 · Q1-Q5 仲裁）
- P42-01 · W1 dataclass + to_dict 剥 None + JSON schema extend · ~40 min · 1 commit
- P42-02 · W2 5 metadata instantiations 显式填值 · ~20 min · 1 commit
- P42-03 · W3 generate_adapter.py 删 shadow + 模板升级 · ~30 min · 1 commit
- P42-04 · W4 yaml SoT + markdown 注脚 · ~20 min · 1 commit
- P42-05 · W5 tests（schema extend + serializer + bidir consistency + generator template）· ~50 min · 1 commit（单大 test commit 便于审）
- P42-06 · W6 三轨 + 收口 + Notion DECISION · ~40 min · 1 commit

**总 6 commits · ~3h · ~380 LOC（含 ~150 LOC 新测试）**

---

## 7. Exit Criteria (v2 扩)

- `ControllerTruthMetadata` 加 `truth_level: str | None` + `status: str | None` 字段
- `controller_truth_metadata_to_dict` 显式剥 None 字段 · pre-P42 payload 形状完全保留
- JSON schema v1 extend · 2 optional properties · enum 正确 · description 规定缺失语义 · `additionalProperties: false` 保
- 5 metadata instantiations 显式填值 · 与 yaml SoT 对齐
- `generate_adapter.py` **不再本地 shadow** `ControllerTruthMetadata` / `GenericTruthEvaluation` · 模板强制输出 `demonstrative/Upgrade pending`
- `docs/provenance/adapter_truth_levels.yaml` 存在 · 5 entries · version: 1
- `docs/provenance/adapter_truth_levels.md` 加 machine-SoT 注脚指针 · 原 5 行表格零改
- `test_controller_truth_adapter_metadata_schema.py` 扩 · 覆盖 enum + serializer 剥 None + 含值时保留
- `test_metadata_registry_consistency.py` 新 · 动态 discover + bidir 3 层校（runtime ↔ yaml ↔ markdown table 行存在性）
- generator template 测试更新（生成源码含 demonstrative/Upgrade pending + 无 shadow class）
- 三轨 default 775+ / e2e 49 / adversarial 1
- ROADMAP + STATE + closure · Notion DECISION · push branch

---

## 8. 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| dataclass 加 `None` default 字段破 `asdict()` 顺序/ pickling | 低 | 小 | dataclass 字段顺序保 · 新字段在最后 · to_dict 剥 None 后字典键顺序稳 |
| JSON schema 消费者严格 validate 报额外字段 | 低 | 小 | 唯一消费者在我们掌控 · additive + to_dict 剥 None 保 payload 一致 |
| `REFERENCE_DEPLOY_CONTROLLER_METADATA.system_id` ≠ registry row 1 "thrust-reverser" | 已知 | 中 | yaml entry `system_id: thrust-reverser` 配 `metadata_const: REFERENCE_DEPLOY_CONTROLLER_METADATA` · test 按 metadata_const 映射不按 system_id |
| dynamic importlib discover 引入循环 import 或慢启动 | 低 | 中 | 用 yaml 的 `metadata_module` 列显式 import path · 不做全包扫描 · 慢启动可接受（test 层只跑一次） |
| yaml parse 在部分环境缺 PyYAML | 低 | 中 | `pyproject.toml` / 既有 requirements 若已有 PyYAML 则免 · 否则加依赖（独立 mini-commit） |
| markdown 注脚文字与 yaml pointer 路径漂移 | 低 | 小 | bidir test 第 3 层校 markdown 表格行 · 注脚文字偏不触发 · 允许 |
| generator shadow class 删除破既有 generated adapter test（若有） | 中 | 中 | `test_generate_adapter.py` 若测 generated 源含 shadow class 字符串 → 同 commit 更新断言 |
| 三轨 default 从 767 跳到 775+ 的数量不匹配（加/减测试数） | 中 | 小 | 新加 W5 ~8 assertions · 精确计数 post-hoc · closure 列实际增量 |

**回滚：** GATE-P42-CLOSURE 不批 → `git revert` 回 a05bb6d。

---

## 9. v5.2 合规

- R1 · non-FF merge 等 GATE-P42-CLOSURE
- R2 · GATE-P42-PLAN (v2) 等 Kogami 显式 + Q1-Q5 仲裁 · GATE-P42-CLOSURE 等
- R3 · 7 条 counter（C1-C7 · 其中 C5/C6/C7 `verified-by: codex-gpt54-xhigh`）就地缓解
- R4 · Kogami 2026-04-20 「路径1」明示选 ① · 下一 P43 已预定
- R5 · P42 v2 对齐 runtime schema + generator + yaml machine SoT 到 P35α docs 层决策 · 消除 runtime-docs-generator-test 四层 drift
- **Codex 调度合规** · adapter boundary 变更硬性规则触发 · Codex 评审已做 · 结果消化 · 不直接复制文字 · verified-by trailer 标明

---

## 10. 停点

**本 plan v2 不执行任何代码/配置动作。等 Kogami 签 `GATE-P42-PLAN (v2): Approved` + Q1-Q5 仲裁。**

若 Kogami 对 Q1-Q5 任一项给出不同指示（如 Q5 选 B 而非 A），Executor 在首个对应 commit 前 README 注记修正 + 保 trace · 不默默改。

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Revision:** v2 (post-Codex adversarial review · path ① remediation)
**Awaiting:** `GATE-P42-PLAN (v2): Approved` (Kogami) + Q1/Q2/Q3/Q4/Q5 仲裁
**Codex-verified:** adversarial review 2026-04-20 · 82,646 tokens · 3 counters (A/B/C) all integrated as C5/C6/C7 with path-① mitigations

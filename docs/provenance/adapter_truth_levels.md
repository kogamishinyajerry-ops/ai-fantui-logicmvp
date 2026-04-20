# Adapter Truth-Level Registry

**Phase:** P35-01 · v5.2 solo-signed · 2026-04-20
**Authority:** Kogami (project owner), signed `GATE-P35-PLAN: Approved` 2026-04-20

## 背景

Well Harness 项目目前有 5 条真值链路（4 个 `adapters/*_adapter.py` + 1 个 `controller.py` 内的 thrust_reverser）。
在 P34 闭合（2026-04-20，`GATE-P34-CLOSURE: Approved`）之后，Q2=B 无害扫描揭示 5 条链路的**上游证迹完整度差异巨大**：

- c919_etras（P34 新增）由甲方 PDF 锚定，traceability matrix 完整
- thrust_reverser（controller.py）有内部 docx 需求，但未入库也未建 traceability
- bleed_air / efds / landing_gear 三条链路**没有上游需求文档**（Kogami 2026-04-20 chat 披露："我之前尝试随便生成的逻辑面板，我自己也没有明确的需求文档"）

本登记表把这一差异**显式固化**，并为未来的 level 升级提供锚点。

---

## Truth Level Schema

每条链路两个正交维度（Q1=C 口径：本质与状态分离）：

### `truth_level` — 本质（变更需 Kogami 签准）

| 值 | 含义 |
|----|------|
| `certified` | 有经甲方/监管/行业标准签准的上游需求文档；traceability 完整 |
| `demonstrative` | 无上游权威文档，为能力演示/占位而生；阈值与逻辑是说明性的 |
| `placeholder` | 连 demonstrative 都算不上，纯占空间（当前无此级）|

### `status` — 当前状态（随工作进展变化）

| 值 | 含义 |
|----|------|
| `In use` | 链路活跃，证迹与当前 level 匹配 |
| `Frozen` | 链路保留但不再新增真实化证迹；允许已有 smoke/API 继续运行 |
| `Upgrade pending` | 已有方向/来源，等 Phase 执行升级 |
| `Upgrade in progress` | 升级 Phase 执行中 |

---

## Registry（5 rows · as of 2026-04-20）

| system_id | truth_level | status | upstream_source | authority | frozen_as_of | upgrade_path | notes |
|-----------|-------------|--------|-----------------|-----------|--------------|--------------|-------|
| `thrust-reverser` | `certified` | `In use` | `uploads/20260409-thrust-reverser-control-logic.docx`（原 docx, 2026-04-09 · SHA256 `6e457fe3…276133a5`）+ `docs/thrust_reverser/requirements_supplement.md`（P37 反向补完, 2026-04-20）| **Kogami 内部自签**（原 docx 为内部来源历史 snapshot · supplement 为反向补完 · 非外部权威 · 见 supplement §7）| — | 已 certified · `docs/thrust_reverser/traceability_matrix.md` · **truth lives in controller.py + yaml (no workbench spec per D1=A)** · **Appendix A 6 项全部 resolved via P37 supplement**（§2-§7）· 若需外部 certification-grade authority 需新 Phase 升级 · supplement §7.3 列升级路径 | P36β (2026-04-20) 完成 intake packet 120 行精益版 + YAML 头 + matrix 241 行 · P37 (2026-04-20) 完成 supplement 297 行 + intake 加第 4 SourceDocumentRef + matrix Appendix A 6 项 ⚠️→✅ + YAML 头 supplement block · controller.py / models.py / YAML values 字节级不变 |
| `bleed-air-valve` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 未来 Kogami 提供上游需求文档后开新 Phase | bleed_air_adapter.py 602 LOC · 自述 "Simplified" · Q2=B 扫描识别为 4 个常数无来源 |
| `emergency_flare_deployment_system` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 同上 | efds_adapter.py 498 LOC · 无 intake / 无 yaml / 无 matrix · Q2=B 扫描识别为 adapter 自足 |
| `minimal_landing_gear_extension` | `demonstrative` | `Frozen` | `none` | 无 | 2026-04-20 | 同上 | landing_gear_adapter.py 362 LOC · 611 LOC tests 但基于自证 · Q2=B 扫描识别为常数无来源 |
| `c919-etras` | `certified` | `In use` | `uploads/20260417-C919反推控制逻辑需求文档.pdf`（10 页 · SHA256 `dbe3f76b…31da5` · 1,013,541 bytes · P38 物理入库 2026-04-20）| 甲方 (C919 TRCU 团队) · **Q1/Q2/Q3 sign-off 由 Kogami 2026-04-20 代 TRCU 明示接纳 (P38)** | — | 已 certified · **Appendix A Q1/Q2/Q3 全部 resolved** · 详见 `docs/c919_etras/traceability_matrix.md` Appendix A · 若未来需 TRCU 团队正式书面签准，独立 Phase 升级 sign-off 来源 | P34 完成 · 1444 LOC adapter · 712 LOC tests · 153 行 matrix · P38 (2026-04-20) PDF 物理入库 uploads/ + YAML 头 SHA 固化 + Appendix A sign-off resolved |

---

## Level 升级流程

从 `demonstrative` → `certified` 的升级必须经过以下步骤（参考 P34 模板）：

1. 获得上游权威文档（甲方 PDF / 行业标准 / 监管文件）
2. 文档入库（`uploads/{date}-{slug}.{ext}`，计算 SHA256）
3. Kogami 开 Phase 指令（指定 Phase 编号 + 方向）
4. Executor 起草 Tier 1 Plan（≥3 counterargument · Open Questions 明列）
5. Kogami 签 `GATE-Pxx-PLAN: Approved` + 仲裁 Open Questions
6. Executor 落地：
   - 更新对应 adapter 的 intake packet（加 PDF / docx 的 `SourceDocumentRef` · `kind=pdf/docx` · `role=requirement_reference`）
   - 更新 hardware YAML 头注释加上游来源 § / 段 / 行锚
   - 新建 `docs/{system}/traceability_matrix.md`（P34 格式：信号表 + 逻辑表 + Step/时间表 + 故障表 + Appendix A 未决假设登记）
   - 如有未决假设，在 Appendix A 明示登记待 authority sign-off
7. 三轨回归绿 · Kogami 签 `GATE-Pxx-CLOSURE: Approved`
8. Executor **同步更新本 registry 的对应行**：
   - `truth_level` 从 `demonstrative` 改 `certified`
   - `status` 从 `Upgrade pending`/`Upgrade in progress` 改 `In use`
   - `upstream_source` 填实际入库路径
   - `authority` 填签准方
   - `upgrade_path` 改为 "已 certified · {matrix path}"

---

## 下游使用者须知

### ✅ 允许的使用

- `certified` 链路：可在审核材料、对外文档、学习材料、客户演示中引用为真值
- `demonstrative` 链路：可在 adapter 泛化能力演示、内部 runtime 测试、smoke 套件、demo fallback 中继续使用

### ❌ 禁止的使用

- `demonstrative` 链路：**不得** 在以下场合引用为真实证迹：
  - 认证/取证材料
  - 对外文档（客户材料 / 招商物料 / 合规声明）
  - 学习/培训材料（会误导新人）
  - 测试金标准（测试可以跑，但 "passes therefore truth" 推论不成立）
  - 跨域联邦推理（Federation Level 1 触发时必须先升 certified）

---

## 治理注脚

- 本 registry 是 docs-only 防护（P35α 范围）。runtime API / 前端 / demo_server 暴露 `truth_level` 留给未来独立 Phase（拟名 P37 · Truth-Level Runtime Surface，Kogami 决定是否发）
- 本 registry 的 row 新增/删除/level 升级必须随对应 Phase 的 Gate 签字**同 commit 原子落地**，不可滞后
- 删除任何既有 row 等于撤销该链路的证迹历史——需 Kogami 签 `GATE-PROV-REVOKE-{system_id}: Approved`（未来若发生）
- 每 sub-adapter 对应的 docstring / YAML 头部 FROZEN banner 是本 registry 的"触手"，由 `tests/test_adapter_freeze_banner.py` 防回归

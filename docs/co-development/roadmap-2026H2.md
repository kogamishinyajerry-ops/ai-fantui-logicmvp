# 2026H2 路线图 — Well Harness Co-development

> **给谁看：** 甲方决策层 + 双方项目经理
> **回答什么：** 立项通过后 2–3 个季度会发生什么
> **状态：** 展望草案（每个 Phase 的 exit criteria 已可证伪，日期区间会随立项时间平移）
> **最新校对日期：** 2026-04-20（P32 W5 命名空间去重）

> **编号命名空间：** 本文件使用 `H2-XX` 前缀（原 `P23-P27` 编号于 2026-04-20 经 P32 统一去重），表示「2026H2 对外交付路线图」的 Phase。与 `.planning/ROADMAP.md` 中的 `PXX`（内部执行路线图，截至当前 P0-P32）是**两套独立命名空间**，不要混淆。Kogami 2026-04-20 AskUserQuestion 批复：外部改前缀、内部 P24-P30 不动。

> **JER-220 scope note (2026-05-01):** This is an external/co-development
> planning artifact. It is not the current in-repo v4 execution baseline. The
> active product mainline is single-user foundation-first workbench development:
> editor, runner, test bench, debugger, archive, then hardware/interface
> designer. Multi-party delivery language here must not be read as immediate
> collaboration-platform product scope.

---

## 0. 路线图总览

| Phase | 标题 | 主要交付物 | 预期时长 | 前置 |
| ----- | ---- | ---------- | -------- | ---- |
| H2-23 | Co-development Kit | API 契约 / 安全评审模板 / SLA 草案 / 本路线图 | 1–1.5 工作日 | 立项通过 |
| H2-24 | 甲方子系统接入 PoC | 甲方选一个子系统，完成 文档→spec→runtime 端到端 | 4–6 周 | H2-23 完成 |
| H2-25 | 生产前硬化 | Staging 环境 SLA 达标 + 对抗测试扩展 + 完整审计链 | 4–6 周 | H2-24 通过 |
| H2-26 | 首批产线 Validation | 嵌入真实产线流程，第一批结果可追溯 | 6–8 周 | H2-25 通过 |
| H2-27 | 季度审计包 | 第三方复核 + 合规报告 + R1–R5 稳定性证明 | 2 周 / 季 | 持续 |

**目标日期（若立项 T₀ 定于 2026-05-01）：**
- H2-23 完成：T₀ + 2 天
- H2-24 完成：T₀ + 6 周（2026-06 中旬）
- H2-25 完成：T₀ + 12 周（2026-07 下旬）
- H2-26 完成：T₀ + 20 周（2026-09 下旬）= **2026Q3 底交付首批 validation**
- H2-27 首次执行：2026-10

---

## 1. H2-24 — 甲方子系统接入 PoC

**目标：** 证明"P15 文档→spec→runtime 的链"能吃甲方真实子系统。

**输入：** 甲方提供一份子系统的技术文档（PDF / Word / DWG），提供一位对接工程师 0.5 FTE。

**产出：**
- 子系统的 `config/hardware/<system>_hardware_v1.yaml`
- `config/control_systems/<system>.json`（节点 + 逻辑门）
- 端到端 pytest（可模拟典型故障场景）
- 一次内部演示，甲方工程师独立操作 Canvas 验证逻辑

**退出条件：**
- 甲方对接工程师可以**独立**拉仓库、跑起演示、改 YAML 看到 Canvas 变化
- 主 pytest + e2e + 对抗 全绿
- 至少 3 个典型故障场景走通（甲方定义）

**风险：**
- 甲方文档质量不一 → 预留 1 周做文档 intake 清洗
- 节点规模超出 19 预期 → controller 的门函数扩展方案需要在 Phase 开始前由 Opus 4.6 审查

---

## 2. H2-25 — 生产前硬化

**目标：** 把 PoC 升级到可跑在甲方 Staging 环境 + 通过对抗基线扩展。

**产出：**
- Staging 环境部署手册（Docker / bare metal 二选一，视甲方 IT 偏好）
- 对抗测试从 8 场景扩展到 15 场景（+ 数据边界 / supply chain / prompt 越权 3 类）
- 监控与告警 wiring（Grafana / 甲方运维栈）
- SLA 草案定稿为 v1.0
- 所有 API 响应加审计 tracing

**退出条件：**
- Staging 环境 8×5 99% 连续 2 周达标
- 对抗 15/15 PASS
- 甲方安全工程团队在 Staging 上完成一次"红蓝对抗"演练

---

## 3. H2-26 — 首批产线 Validation

**目标：** 工作台的**输出**进入甲方产线 validation 流程，结果有据可查。

**产出：**
- 首批 N 个子系统（甲方选，建议 3–5 个）完成 validation 并产出合规报告
- 每条 validation 记录绑定：输入 JSON + 代码 commit SHA + 对抗测试日志 + AI 叙述（带模型/版本）
- 可由第三方独立复现任一 validation（给参数表 + seed + 一键脚本）

**退出条件：**
- 甲方产品线负责人签字接受首批结果
- 第三方复现至少 1 次 validation 字节级一致
- 审计链完整可追溯到 git commit + 真跑 artefact

---

## 4. H2-27 — 季度审计包（持续）

**目标：** 每季度产出一次"R1–R5 稳定性证明"，供合规部门存档。

**产出：**
- 季度合规报告（R1/R2/R3/R4/R5 各维度统计 + 例外清单 + 整改结论）
- 回归基线 SHA256 冻结快照（扩展自 `docs/freeze/`）
- 对抗测试年度趋势图
- AI 供应链变更记录（模型更换、API 升级、adapter 重写）

**退出条件：**
- 报告由甲方合规 + 安全双签
- 新发现的风险点全部在下个季度的路线图中有对应 Phase

---

## 5. 不在本路线图的事

明确列出 **H2 不做**的事，避免隐性期望：

- **不做** 多租户 SaaS 化（需独立商业决策）
- **不做** 取代甲方现有 PLM / MBSE 工具链（本工作台只做逻辑验证层）
- **不做** 自动生成代码到甲方嵌入式系统（只做 validation，不做 codegen）
- **不做** 规模超过 200 节点的 controller 扩展（超过需要重新评估门函数架构）
- **不做** 替换 controller.py 为 AI 推理（违反 R1 / R2，永不考虑）

---

## 6. 里程碑与付款建议（草案）

**供甲方采购参考，最终以合同为准。**

| 里程碑 | 建议付款比例 | 触发条件 |
| ------ | ------------ | -------- |
| H2-23 完成 | 10% | Co-dev kit 4 份文档签字 |
| H2-24 完成 | 25% | PoC 子系统演示通过 |
| H2-25 完成 | 25% | Staging SLA 2 周达标 |
| H2-26 完成 | 30% | 首批 validation 签字 |
| H2-27 首期 | 10% | 首个季度审计报告双签 |

---

## 7. 治理

- **变更：** 本路线图 Phase 数量或顺序变更，需双方项目经理 + 架构师三方同意
- **季度复盘：** 每个 Phase 闭合后做 1 次复盘，决定是否调整下一 Phase 的 exit criteria
- **治理：** 我方执行层按 v3.0 双 Opus + v3.1 停机白名单运作——Claude Code Opus 4.7 为 Executor，Phase 合并 Gate 由 Notion AI Opus 4.7 独立签署；甲方 PR 评审走 `security-review-template.md`

---

## 8. 索引

- 本路线图：`docs/co-development/roadmap-2026H2.md`
- API 契约：`docs/co-development/api-contract.md`
- 安全评审：`docs/co-development/security-review-template.md`
- SLA 草案：`docs/co-development/sla-draft.md`
- 项目宪法：`docs/architecture/federation-model.md` + R1–R5（见 ROADMAP.md）
- 立项物料：`docs/demo/pitch_script.md` + `faq.md` + `preflight_checklist.md` + `disaster_runbook.md`

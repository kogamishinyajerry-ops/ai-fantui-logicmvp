# AI FANTUI LogicMVP Freeze / Demo Packet

日期：2026-04-10  
适用范围：`P5 Demo Polish And Edge-Case Hardening` 收口后的当前稳定基线

## 一句话状态

当前 demo 已完成 P5 收口，可作为稳定演示与讲解基线；当前最高优先级不是继续加功能，而是对齐控制塔状态、冻结包和说明文档。

## 当前稳定证据

- 最新 P5 收口证据：GitHub Actions run `24234580061`
- 单元测试：`175 tests OK`
- demo smoke：`10 scenarios pass`
- 共享验证检查：`8 / 8 pass`
- GitHub 仓库：[ai-fantui-logicmvp](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
- GitHub Actions：[GSD Automation Loop](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)
- Notion 控制塔：[AI FANTUI LogicMVP 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)

## 当前演示面已经具备什么

- presenter-friendly 的逻辑主板与链路解释
- preset、toggle、lever snapshot 交互
- `TRA` 条件深拉语义与 `VDT` 实时联动
- `RA -> TRA -> VDT` 的受控状态监控时间线
- GitHub 可验证的 demo smoke 证据面

## 必须保持的边界

- `src/well_harness/controller.py` 仍然是唯一控制真值。
- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。
- 不新增第二套控制真值，不绕开现有 HTTP / CLI 契约。
- Opus 4.6 审查和主观判断只使用 Notion + GitHub 证据面。

## 当前最该做的事

- 对齐 `01 当前状态`、roadmap 和相关控制塔页面，让它们反映当前 `P5` 的真实证据基线。
- 把历史 `manual browser QA` 表述降级成 presenter guidance，而不是当前审批规则。
- 保持 `P7` 的早期 spec-driven groundwork 不丢失，但在 `P6` 收口前不继续扩大实现面。

## 当前不该做的事

- 不继续堆新的 demo 功能。
- 不改 controller truth、runner 编排或 API 契约。
- 不把已提前播种的 `P7` foundation 当成可以跳过 `P6` 的理由。

## 后续人工关口

当前 `P5` 已完成收口判断。后续只有当控制塔再次明确出现新的 `Awaiting Opus 4.6` gate、open gap 或新的主观裁决需求时，才需要再次手动触发 Opus 4.6。

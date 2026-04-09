# AI FANTUI LogicMVP 冻结快照

日期：2026-04-09  
冻结标签：`freeze-2026-04-09-p5-10`  
功能基线提交：`82ceb63 feat(p5-10): add controlled monitor timeline`

## 这次冻结是什么意思

这是一份“当前可用版本”的临时存档。

它冻结的是这样一个状态：

- 演示舱已经从“能跑”提升到“能讲、能演示”；
- 主要交互边角问题已经补过很多轮；
- `TRA / VDT` 相关的关键交互 bug 已经修到可用；
- 新增了按 `RA -> TRA -> VDT` 过程绘制的“状态 vs 时间”监控图。

这次冻结的目的，不是宣布项目彻底结束，而是先把一版稳定状态封存下来，方便后续回看、恢复和评审。

## 当前冻结了什么

这一版里已经包含：

- `controller.py` 中确定性的反推 deploy 逻辑；
- `SW1 / SW2` 的锁存开关模型；
- `TLS / PLS / VDT` 的简化反馈模型；
- CLI 时间线、事件、解释、诊断输出；
- 浏览器里的逻辑控制演示舱；
- 确定性的 demo 问答层；
- GitHub 可验证的 smoke 覆盖；
- Notion 控制塔联动；
- 按用户自定义监测过程生成的全宽“状态 vs 时间”监控面板。

## 当前证据基线

- 单元测试：`167 tests OK`
- 共享验证检查：`8 / 8 pass`
- demo smoke 场景：`10 pass`
- GitHub 仓库：[ai-fantui-logicmvp](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
- Notion 控制塔：[AI FANTUI LogicMVP 控制塔](https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec)

## 这次冻结保留的边界

- `src/well_harness/controller.py` 仍然是唯一控制真值。
- `src/well_harness/runner.py` 仍然是仿真编排层。
- simplified plant 仍然只是演示反馈模型，不是假装完整物理模型。
- `POST /api/demo`、`POST /api/lever-snapshot`、`GET /api/monitor-timeline`、`well_harness demo`、`well_harness run` 视为当前冻结版的有效演示接口。

## 还没有完成的人工关口

这次冻结 **不等于** 项目已经正式收口。

当前状态仍然是：

- `P5 Demo Polish And Edge-Case Hardening` 还是当前审查对象；
- 最终主观判断仍然要走 Notion 内置 Opus 4.6；
- 控制塔当前是在等 phase closeout 审查，不是在鼓励继续随意扩功能。

## 后续恢复时的建议顺序

如果后面要从这版继续往前推进，最自然的顺序是：

1. 先完成当前这轮 Opus 4.6 收口审查；
2. 再对齐控制塔里仍然过时的状态页和说明页；
3. 再补一版更完整的 freeze/demo packet；
4. 在 roadmap 没改之前，不主动继续扩产品表面功能。

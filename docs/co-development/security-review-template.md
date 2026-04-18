# 安全评审 Checklist — 甲方 PR 审查模板

> **给谁看：** 甲方安全工程团队（评审每次 PR 的审查人）
> **回答什么：** 10 项硬性 checklist，任何一项不过关即拒绝合并
> **什么情况下变动：** R1–R5 宪法或对抗测试基线扩展时同步更新
> **最新校对日期：** 2026-04-18

---

## 使用方式

1. 评审人打开 PR，在 Comment 里贴下方表格
2. 每项只能填 `PASS` / `FAIL` / `N/A`（N/A 必须附原因）
3. 有 `FAIL` → 阻止合并；`N/A > 3 项` → 复议
4. 所有 Checklist 项目对应仓库内可验证证据，不接受"应该是没问题"

---

## Checklist（10 项）

| # | 项目 | R-锚点 | PASS 信号 | FAIL 例 |
| - | ---- | ------ | --------- | ------- |
| 1 | 是否改动 `src/well_harness/controller.py`？ | R1 | 未改 / 有独立 Opus 4.6 架构审查记录 | PR 直接修改门函数但无审查 |
| 2 | 是否新增 AI 决策能力？ | R2 | AI 仅改写 `highlighted_nodes` / 叙述文本 | AI 返回的字段直接写回 Canvas 节点状态 |
| 3 | 是否改动 LLM adapter 公共契约？ | R2/R4 | `LLMClient` Protocol 签名不变 + `tests/test_llm_client.py` 通过 | 签名变动且未更新测试 |
| 4 | 是否引入新数据出境风险？ | 合规 | 无新的云 API 硬编码 / 新 prompt 不泄露机密字段 | 新增未审查的第三方 SaaS 调用 |
| 5 | 是否通过所有对抗测试？ | R5 | `adversarial_test.py` 8/8 PASS | 任一场景失败 |
| 6 | 是否通过主 pytest + e2e lane？ | 回归 | `pytest` 658+/1skip、e2e 49/49 | 有新的 red 或 xfail |
| 7 | 新增 API 是否在 `docs/co-development/api-contract.md` 有条目？ | R3 | 路径、请求/响应 schema、错误码、确定性保证全部有 | 仅代码有实现，文档空 |
| 8 | 新增 dependency 是否影响供应链审计？ | 合规 | 在 `requirements.txt` 固定版本 + license 允许 | 直接 git URL 或浮动版本 |
| 9 | 是否新增/修改 prompt injection 路径？ | R5 | 新 handler 复用 `VALID_*` 白名单清洗 | 用户输入直接拼进 system prompt |
| 10 | 是否提供降级/熔断路径？ | R4 | 至少有 error 码映射 + 灾难手册对应场景 | 新依赖挂了就整链路白屏 |

---

## 对抗测试基线（Checklist #5 的参考）

当前对抗测试（`src/well_harness/static/adversarial_test.py`）覆盖 8 个场景：

1. 幂等性 — 重复请求返回一致结果
2. 边界条件 — tra_deg 极值 / n1k=0/1 边界
3. 快速循环 — 连击按钮压力测试
4. 前端权威 — 伪造 `active_fault_node_ids` 不被接受
5. 全链路验证 — wow_a → chat 响应一致
6. Prompt injection — user message 含 `"ignore previous instructions"` 时降级
7. Schema violation — AI 返回非白名单 action 时降级
8. Resource exhaustion — 1 小时内 1000 req/min 无崩溃

新 PR 若扩展场景数，本清单同步更新基线。

---

## 常见审查陷阱（Reviewer 请留意）

- **"只是日志改动"：** 日志可能泄露 prompt / 用户数据，需确认脱敏
- **"只改前端"：** 前端改 Canvas 渲染时，核对 `active_fault_node_ids`、`highlighted_nodes` 来源仍然是后端
- **"只加 fallback 文案"：** fallback 文案不得包含"猜测结论"——必须明确告知 AI 不可用
- **"Ollama 可选"：** Ollama 不可用 ≠ adapter 可删；adapter 必须保留以便甲方自备模型时重用

---

## 评审产出要求

- PR 正文必须包含本 checklist 表（10 行）
- 至少一位甲方安全工程师签字（Slack / 工单系统均可）
- `FAIL` 项必须在下一次 push 前修复或由架构师例外批准
- 所有 `N/A` 超 3 项的 PR 由架构委员会复议

---

## 产出物审计轨迹

- 评审记录：甲方 Notion / Slack（各项目自定）
- 证据文件：PR diff + CI 记录 + 对抗测试 artefact
- 定期复审：每季度一次，对比通过率 / FAIL 分类，判断是否需要更新宪法

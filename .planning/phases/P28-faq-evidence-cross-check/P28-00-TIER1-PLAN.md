---
phase: P28
plan: P28-00-TIER1
title: FAQ 结构化符号证据交叉验证 — 让 "_BACKENDS / VALID_ACTION_TYPES / LLMClient Protocol" 类 claim 机器可证伪
status: drafted · Executor self-review under v4.0 Extended Autonomy Mode (Kogami 过 ≥3 阈值后续签)
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P26 路径引用验证器已落地（tests/test_pitch_citations.py in CI default lane）
  - P22 立项物料冻结基线未变
non-goals:
  - 修改任何立项物料 md 文档内容（含修复本 Phase 发现的 FAQ Q9 citation 错误）
  - 修改 controller / LLM adapter / prompts / wow / 前端
  - 做数字 claim 校验（line counts / test counts / latency）——那些天然会漂移，CI fail 变噪音
  - 做语义校验（代码实际行为是否匹配 FAQ 描述）——只校验"符号是否被定义"
---

# P28 · FAQ 结构化符号证据交叉验证

## Why this Phase

P26 已让"路径引用存在性"机器化（`src/foo.py` 路径必须存在）。但 FAQ 里还有一类更危险的 claim：
**符号级 claim** — "_BACKENDS dict"、"VALID_ACTION_TYPES whitelist"、"LLMClient Protocol" 这类
命名具体的代码结构承诺。若这些符号被 refactor 重命名而 FAQ 没跟改，pitch 当天甲方问 Q8
"换模型成本多大" 时，演讲者在代码里找不到 `_BACKENDS` —— 话术立刻崩。

P28 做一件具体的事：**hand-curate 一份 "pitch material 结构性 claim → 代码符号" 的映射表，
写 pytest 测试验证每个符号在被 cite 的文件里真的被定义**。进 CI default lane，每次 commit 都跑。

**Hand-curate 不 auto-extract 的理由：** FAQ prose 没有统一 citation 语法
（"`LLMClient` Protocol" vs "llm_client.py::LLMClient"）。auto-extract 要么漏（false negative）
要么胡乱命中（false positive）。Hand-curation 接受 false negative 换取零 false positive，
每条 claim 自带"来自哪份文档 · Q几"来源标注，是自文档化的。

## Scope

### 被覆盖的 claim 类别

1. **LLM adapter 结构**（faq.md Q8/Q15）：`LLMClient` Protocol · `MiniMaxClient` · `OllamaClient` · `_BACKENDS` dict · `get_llm_client()` factory
2. **Operate/Reason handler 白名单**（faq.md Q11）：`VALID_ACTION_TYPES` · `VALID_RESPONSE_TYPES`
3. **三个 chat handler 存在**（faq.md Q4/Q13）：`_handle_chat_explain` · `_handle_chat_operate` · `_handle_chat_reason`
4. **Controller 主类**（faq.md Q1）：`DeployController`
5. **运行时依赖不含 `anthropic`**（faq.md Q9）：pyproject.toml 不含该字符串

共 **11 个结构 claim** + **1 个依赖 claim** = 12 个 assertion。

### Sub-phases

| Sub | 工作 | 工期 | 产出 |
| --- | --- | ---- | ---- |
| P28-01 | `tests/test_pitch_symbols.py` — 12 claim 表 + 4 测试（meta/symbol/no-anthropic/registry-hygiene）| 0.4d | 新测试文件 + 首轮全绿 |
| P28-02 | 首轮真跑 → 意外发现 FAQ Q9 cite `requirements.txt` 但该文件不存在 → 写 `docs/demo/pitch-citations-audit.md` 归档（只报不改）| 0.1d | audit doc |
| P28-03 | closure + ROADMAP + GATE-P28-CLOSURE self-sign (v4.0 七点自审)| 0.2d | 三轨绿 + Notion sync |

**总工期：** 0.7 工作日

## Exit Criteria

- [ ] `tests/test_pitch_symbols.py` 进 pytest default lane（非 opt-in）
- [ ] 首轮真跑：12 claim 全 PASS（符号已全部验证存在）
- [ ] 意外发现的 FAQ Q9 citation drift 写进 audit doc，不自行改 faq.md
- [ ] pytest 662 → 666+（至少新增 4 个测试）·  1 skip 不变
- [ ] e2e 49/49 + adversarial 8/8 零回归
- [ ] GATE-P28-CLOSURE self-signed under v4.0

## R1–R5 合规（事前 self-audit）

| 原则 | P28 保持方式 |
| ---- | ----------- |
| R1 真值优先 | 只读代码，不改 controller / 19-node / 4 logic gates |
| R2 AI 仅解释 | 不触 LLM adapter 源码（验证层用 regex，不改 adapter） |
| R3 可审计 | 加强 R3 — 本 Phase 让 FAQ 结构性 claim 从"写了但没人核"升格为"每次 CI 都核" |
| R4 降级可控 | 无降级相关改动 |
| R5 adversarial 守门 | adversarial_test.py 零触碰；closure 跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | claim 表过度膨胀，每次 refactor 都破坏一堆测试 → 测试沦为摆设 | 中 | 长期维护性 | 严格 hand-curate；只加"若改名 pitch 话术直接失效"的 load-bearing claim；不加"这个文件里有多少行"这类噪音 |
| R2 | regex pattern 写死某个实现细节（如 `class\s+DeployController`）而合法 refactor（挪到别处）触发假 FAIL | 低 | 测试假红 | pattern 只匹配符号定义行；refactor 通常保留符号命名 |
| R3 | 发现 FAQ 有 citation drift 但本 Phase non-goal 是"不改 pitch 物料"→ 发现了也不能修 | 高（确认发生）| pitch 日风险 | 写 audit doc 交 Kogami 决策；不自行改 P22 冻结基线 |
| R4 | pyproject.toml 日后加 `anthropic` 依赖，本测试 fail，但那可能是合法业务选择 | 低 | 可能误拦 | 若未来真要加 anthropic，修 FAQ Q9 + 此测试才合并——正确阻断 |

## 治理 Gate 规则（v4.0）

- Executor 自主推进所有 3 个 sub-phase
- P28-03 closure self-sign 贴 7-checklist
- v4.0 窗口 Phase 收口计数：#4（P25=#1, P26=#2, P27=#3, P28=#4）— Kogami 2026-04-18 已主动续签越过 ≥3 阈值
- 红线：若测试意外触及 controller / LLM adapter 源码 → 立停回滚

## Scope 初审（Executor pre-review）

- 纯测试层工作，无宪法级改动 → 红线 #1 不触
- 非不可逆 → 红线 #2 不触
- 不改宪法级 Notion / v4.0 自身 → 红线 #3 不触
- 已越 ≥3 Phase 阈值但 Kogami 显式续签 → 红线 #4 已被用户覆盖

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_

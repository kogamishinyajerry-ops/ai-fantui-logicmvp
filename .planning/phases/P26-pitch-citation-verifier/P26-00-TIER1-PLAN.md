---
phase: P26
plan: P26-00-TIER1
title: 立项物料引用有效性自动验证 — 让 pitch_script / faq / preflight / runbook 的每条证据路径都可证伪
status: drafted · Executor self-review under v4.0 Extended Autonomy Mode
created: 2026-04-18
owner: Claude Code Opus 4.7 (Executor); self-signs under v4.0
preconditions:
  - P22 立项物料已冻结 (pitch_script / faq / preflight / disaster_runbook)
  - P21 local_model_poc.md 已落盘
  - P25 integrated-timing-findings.md 已落盘
non-goals:
  - 修改任何立项物料 md 文档内容
  - 修改 controller / LLM adapter / prompts / wow 脚本 / 前端 UI
  - 做任何路径规范化（如把相对路径全转绝对路径）— 只验证，不重写
---

# P26 · 立项物料引用有效性自动验证

## Why this Phase

P22 pitch_script.md 自带诚实性护栏：
> "凡本稿里写'代码行'——必有 src/ 下文件 + 函数名。凡本稿里写'真跑'——必有 runs/ 下 artefact。"

但**没有任何机器检查这条规矩被遵守**。当前 7 份立项物料（pitch_script / faq / preflight_checklist / disaster_runbook / local_model_poc / wow_a/b/c 场景卡）总共引用了 100+ 条代码路径 / artefact 路径 / 测试文件 / 配置文件。**一条都坏了，pitch 当天就翻车。**

未来不可避免会发生的事：
- 某次 refactor 重命名了某个 .py 文件 → pitch_script 里的引用静默失效
- 某个 `runs/<timestamp>/` artefact 被误删 → 灾难手册里的 fallback 链条断
- 某个 config/ 文件改名 → FAQ 里的切换命令行失效

P26 做一件具体的事：**写一个 pytest 测试，解析所有立项物料，提取每条路径引用，验证文件存在**。进 CI default lane，每次 commit 都跑。

## Scope

### 被扫描的物料（来源文件清单）

| 文件 | 用途 | 典型引用 |
| ---- | --- | -------- |
| `docs/demo/pitch_script.md` | 主话术 | `src/well_harness/controller.py` · `runs/dress_rehearsal_*/wow_a_timeline.json` |
| `docs/demo/faq.md` | 15 题 × 证据绑定 | `src/**/*.py` · `runs/**/report.json` · `config/**/*.yaml` |
| `docs/demo/preflight_checklist.md` | T-60→T-0 16 项 | `scripts/**/*.py` · `runs/**/*` |
| `docs/demo/disaster_runbook.md` | 7 场景 × 4 字段 | `config/llm/*.yaml` · `runs/local_model_smoke_*/report.json` |
| `docs/demo/local_model_poc.md` | P21 证据链 | `src/well_harness/llm_client.py` · `runs/local_model_smoke_*/` |
| `docs/demo/wow_a_causal_chain.md` | 场景 A 卡 | `src/well_harness/controller.py` 相关函数 |
| `docs/demo/wow_b_monte_carlo.md` | 场景 B 卡 | `src/well_harness/monte_carlo_engine.py` |
| `docs/demo/wow_c_reverse_diagnose.md` | 场景 C 卡 | `src/well_harness/fault_diagnosis.py` |
| `docs/demo/integrated-timing-findings.md` | P25 发现 | `archive/shelved/llm-features/scripts/integrated_timing_rehearsal.py` · `runs/integrated_timing_*/` |

### 提取规则

扫描 markdown，匹配以下模式（反引号包围或裸写都支持）：
- `src/<path>.py` · `src/<path>.py:<line>` · `src/<path>.py::<function>`
- `tests/<path>.py`
- `scripts/<path>.py`
- `runs/<ts>/<file>` · `runs/<ts>/`（目录引用）
- `docs/<path>.md`（交叉引用）
- `config/<path>.yaml` · `config/<path>.json`
- `.planning/<path>.md`
- `data/<path>.json`

提取后去重，对每条路径执行 `pathlib.Path.exists()` 校验。**容忍：** 明显是 placeholder 的路径（如 `runs/<ts>/...`、`<system>.yaml`）跳过。

### Sub-phases

| Sub | 工作 | 工作日 | 产出 |
| --- | --- | ----- | ---- |
| P26-01 | `tests/test_pitch_citations.py` — parser + verifier + 默认进 CI lane | 0.5d | 新测试文件 + 首轮全绿 |
| P26-02 | 若有引用坏，写 `docs/demo/pitch-citations-audit.md` 记录（本 Phase 不主动修复话术，只报告） | 0.1d | audit doc or "clean slate" 公告 |
| P26-03 | closure + GATE self-sign (v4.0) | 0.1d | 三轨绿 + Notion sync |

**总工期：** 0.7 工作日

## Exit Criteria

- [ ] `tests/test_pitch_citations.py` 进 pytest default lane（非 opt-in）
- [ ] 首轮真跑：9 份立项物料全部扫描，100% citation PASS 或所有 FAIL 在 audit doc 归档
- [ ] pytest 基线从 658 → 659+ (新增至少 1 个测试)，1skip 不变
- [ ] e2e 49/49 + adversarial 8/8 零回归
- [ ] GATE-P26-CLOSURE self-signed under v4.0

## R1–R5 合规（事前 self-audit）

| 原则 | P26 保持方式 |
| ---- | ------------ |
| R1 真值优先 | 只读立项物料 md 和文件系统，不改 controller.py |
| R2 AI 仅解释 | 不触 LLM adapter |
| R3 可审计 | **加强 R3** — 这 phase 的目的就是让立项物料的证据链可机器验证 |
| R4 降级可控 | 测试 FAIL 时打印明确的 FAIL 路径，不掩盖 |
| R5 adversarial 守门 | adversarial_test.py 零触碰；本轮 closure 跑 8/8 |

## 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | 正则匹配过宽，误把非路径文本（如 "src/api" 在句中）识别为路径并报假 FAIL | 中 | 测试假红 | regex 要求路径含扩展名或结尾斜杠；reject 无 extension 的裸路径 |
| R2 | 某引用在 placeholder 形式（如 `runs/<ts>/wow_a_timeline.json`）被误当真实路径 | 中 | 假 FAIL | skip 含 `<` `>` `*` 占位符的匹配 |
| R3 | CI 环境里某个 `runs/` artefact 没 commit → PASS 但本地失败 | 低 | 环境差异 | 每个被引用的 `runs/` artefact 必须 in-tree；P26-01 验证时如发现 out-of-tree 引用，报 audit |
| R4 | 测试太严（所有新增引用都必须存在），后续写文档时卡脖子 | 低 | 文档写作摩擦 | 引用必须随文档一起 commit；若引用的 artefact 尚未生成，文档不得发稿 |

## 治理 Gate 规则（v4.0）

- Executor 自主推进所有 3 个 sub-phase
- P26-03 closure self-sign 贴 7-checklist
- v4.0 窗口 Phase 收口计数：#2（P25=#1, P26=#2）
- 红线：若测试意外触及 controller / LLM / prompts → 立停回滚

## Scope 初审（Executor pre-review）

基于 v4.0 授权自主初审：
- 纯测试层工作，无宪法级改动 → 红线 #1 不触
- 非不可逆 → 红线 #2 不触
- 不改宪法级 Notion / v4.0 自身 → 红线 #3 不触
- 无深度验收触发（线性推进，无技术路线偏移）→ 红线 #4 不触

---

_Execution-by: opus47-max · v4.0 Extended Autonomy Mode · self-signed GATE_

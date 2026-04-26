# AI FANTUI Control Logic Workbench MVP — Freeze / Demo Packet

<!-- AUTO-SYNCED REPO FREEZE PACKET SNAPSHOT START -->
## 当前自动同步冻结摘要

- 当前阶段：`P43 Control Logic Workbench end-to-end milestone`
- 当前已验证 Plan：`P43-02-00 P43-02 Batch — Orchestrator + Document Pipeline + Freeze Gate`
- 最近成功执行证据：`P46-03 PR #46 merged (P46 series closes the loop: P46-01 dev-server startup script + make dev — one-command boot, MiniMax key resolved from env / ~/.zshrc / ~/.minimax_key, port-killer + state-dir setup baked in / P46-02 per-system gate synonyms — rules interpreter now covers all 4 systems with domain-honest vocabularies (L1..L4 / G1..G4 / V1..V2 / E1..E3) and unknown-system fallback / P46-03 /gsd-execute-phase-from-brief Claude Code skill spec + dev-queue brief contract test — last manual gap closed: skill picks brief, plans, asks before edit, branches + PRs; 16-test contract locks every brief field the skill parses incl. HTML schema marker for version drift; truth-engine red line preserved by always-ask + always-PR safeguards; 1348/1348 full suite, 56/56 new P46-01..03 tests; Self-Gate via Executor-即-Gate v3.2) — 2026-04-26`
- 当前 Gate：`OPUS-4.6 周期审查 Gate (Approved)`
- 当前 Opus 状态：`当前无需 Opus 审查`
- Open Gap 数量：`0`
- 当前证据模式：`repo-doc fallback mode`
- 证据模式说明：共享 Notion 数据库与活跃控制面页面当前不可达；当前快照由 repo freeze packet 与 handoff docs 恢复。
- 当前 QA 摘要：`PASS. 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
- 当前运行摘要：`Focused control-plane maintenance run passed. Carried forward the stronger shared validation baseline: 175 tests OK, 10 demo smoke scenarios pass, and 8/8 shared validation checks pass.`
- 当前冻结包继续作为稳定 demo/reference baseline；当前工程主线已转向 P7 workbench 扩展。

## 当前冻结入口

- [01 当前状态（自动同步）](https://www.notion.so/346c6894-2bed-81cf-afd0-d060768d56d7)
- [09C 当前 Opus 4.6 审查简报](https://www.notion.so/34dc6894-2bed-81fb-bf60-ea687dff25e7)
- [GitHub Repo](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp)
- [GitHub Actions](https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp/actions)

## 历史正文说明

- 下方正文保留为冻结说明，不再单独维护顶部状态摘要。
<!-- AUTO-SYNCED REPO FREEZE PACKET SNAPSHOT END -->

## 冻结期完成改进项（2026-04-15）

| 改进项 | 提交 | 说明 |
|--------|------|------|
| **P16 AI Canvas Sync** | `9845c83` | Opus 4.6 A+ 架构（truth engine 先行 + AI 标注后到）：truth engine 驱动 canvas (<100ms)，MiniMax 解释，节点叠加高亮层 `.ai-discussed`；430 tests 无回归 |
| **Aerospace Dark HUD UI 升级** | `9845c83` | 6 优先级 CSS 改造：CSS 变量重塑 + SVG 精密仪表节点 + 连接线状态 + 终端风格抽屉 + 微交互 + Truth Eval Bar HUD 化；430 tests 无回归 |
| **external_dependencies schema** | `abef4e9` | `control_system_spec_v1` 新增 `external_dependencies` 字段（含 `externalDependencySpec`），联邦架构宪法级文档就绪 |

## P44 Workbench engineer→reviewer→Claude Code loop（2026-04-26）

| 改进项 | 提交 | 说明 |
|--------|------|------|
| **P44-03 Proposals persistence + inbox** | `fd9856b` | `/api/proposals` POST/GET，文件级持久化 (`.planning/proposals/PROP-*.json`)，工程师确认 interpretation 后提交即落盘并出现在 review queue；adapter-only，truth-engine 红线由测试守护；36 new tests |
| **P44-04 Reviewer mode + glowing anchors** | `8e6cdbe` | 顶栏 `审核视角 · Review Mode` 切换；OPEN 提议在 SVG 上发光闪烁 + 每个 gate 的开 ticket 数 badge；点击门 → spotlight 工单卡，点击工单 → spotlight 门；100% static-only，32 new tests |
| **P44-05 Accept/reject + dev-queue handoff** | `daa360d` | `/api/proposals/<id>/accept|reject`：状态翻转 + 审计 history append；accept 时写 `.planning/dev_queue/PROP-XXX.md` 给 Claude Code `/gsd-execute-phase` 未来 session 接手；adapter-only；29 new tests |
| **P44-06 Panel version chip + rollback hints** | `f0f7806` | 顶栏 `📜 面板版本 · Panel Version` 芯片显示 truth-engine SHA + ACCEPTED 计数；每个 ACCEPTED 工单卡可展开 `🔁 回滚指引`，给出 `git log --grep` + `git revert` 命令；workbench 永不替工程师执行 git；frontend-only，28 new tests |

## P45 Workbench multi-system + LLM upgrade（2026-04-26）

| 改进项 | 提交 | 说明 |
|--------|------|------|
| **P45-01 Multi-system circuit routing** | `24d917a` | `/api/workbench/circuit-fragment?system=<id>`：thrust-reverser 走 `fantui_circuit.html` 的 L1..L4 SVG，其它三系统返回 placeholder SVG（命名系统、邀请提交工单、给出"如何接入"提示）；XSS-safe；下拉菜单切换即时 re-paint；13 new tests |
| **P45-02 Per-system inbox filtering** | `f94013a` | `list_proposals(system_filter=...)` + `GET /api/proposals?system=<id>`；前端 inbox 自动按当前系统过滤，header 显示 `审核队列 · Review Queue · <system>` 体现 scope；下拉切换同时刷新面板 + inbox；14 new tests |
| **P45-03 LLM interpreter via MiniMax-M2.7-highspeed** | `aa24e02` | 顶栏 `📜 规则解读 ↔ 🤖 智能解读` 切换；规则解读保持 default（零延迟、确定性），LLM 解读用 MiniMax-M2.7-highspeed（OpenAI 兼容 API at `api.minimaxi.com/v1`，stdlib `urllib.request`，零新依赖）；reasoning-style `<think>...</think>` 与 ```` ```json ```` fence 都被解析器剥离；任何失败（无 key/网络/解析）静默回退到规则解读，结果带 `interpreter_strategy` 与 `llm_error` 字段；result panel 显示绿/蓝/黄三色 badge 表明哪条路径出的结果；adapter-only，truth-engine 红线守护；27 new tests |

## P46 Workbench loop closure（2026-04-26）

| 改进项 | 提交 | 说明 |
|--------|------|------|
| **P46-01 Dev-server startup script + make dev** | `cad0b26` | `scripts/dev-serve.sh` 一条命令启动：MiniMax key 按 `MINIMAX_API_KEY` → `Minimax_API_key` → `~/.zshrc grep` → `~/.minimax_key` 顺序解析（缺 key 时降级为规则解读，server 仍启动）；`.planning/proposals` + `.planning/dev_queue` 自动创建；端口被占用时先 kill 再启动（重跑幂等）；`set -euo pipefail` 防御；`Makefile` 提供 `make dev` / `make test` / `make help` alias；20 new tests 覆盖脚本/Makefile 契约 + `bash -n` 语法守护 |
| **P46-02 Per-system gate synonyms** | `9de4e2c` | 规则解读器从"thrust-reverser-only"扩到全部 4 个 dropdown 系统：L1..L4（thrust-reverser，原版未改）/ G1..G4（landing-gear: 主起放下/收上 + 前起放下/收上）/ V1..V2（bleed-air-valve: 引气阀开启/关闭）/ E1..E3（c919-etras: ETRAS 解锁/部署/收回）；每系统独立 `_SIGNALS_BY_SYSTEM` 字典；未知 system_id 静默回退到 thrust-reverser；端点把 system_id 透传到规则路径（LLM 路径 P45-03 已支持）；back-compat 别名保持 `_GATE_SYNONYMS` / `_KNOWN_TARGET_SIGNALS` 可用；live verified 4 系统都返回正确 `affected_gates`；20 new tests |
| **P46-03 Skill spec + dev-queue brief contract** | `277b6bb` | `/gsd-execute-phase-from-brief` Claude Code skill 文件部署到 `~/.claude/commands/`（active）+ `docs/skills/` 仓内快照（discoverable），关闭"engineer accept → truth-engine commit"最后一段手工 gap：skill 拾取最旧 brief、解析 PROP-id、给出 5-bullet 计划、强制要求"Proceed?"确认（无 `--auto-merge` bypass）、走 feature branch + PR（永不直 push main）、`make test` 通过后提交、合并后删 brief；contract test 16 条锁住 `write_dev_queue_brief` 输出每个字段（含 HTML schema marker `schema v1` 用于版本漂移检测）；engineer's source_text 必须逐字保留；`docs/skills/README.md` 解释为什么是 skill 而非 script、安装/刷新方法、truth-engine 红线 |

## 当前用途

- 这个文件现在只保留“当前自动同步冻结摘要 + 当前冻结入口”。
- 当前冻结/讲解真值以顶部自动同步摘要、Notion 控制塔和 GitHub Actions 为准。

## 历史归档

- 旧的长正文已迁到 [archive/2026-04-10-freeze-demo-packet-history.md](./archive/2026-04-10-freeze-demo-packet-history.md)。
- 如果需要复盘 P5 收口时的长版冻结说明，再进入 archive 文件查看。
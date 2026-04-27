# Workbench Demo Script · v-demo-workbench-r1

> Generated 2026-04-27 as part of P51-04 dress rehearsal.
> Tag: `v-demo-workbench-r1` · main HEAD at PR #82 merge.

## 1. 演示前准备 (T-5 min)

```bash
# Terminal 1 — start the workbench backend
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8002

# Browser tab — open the dashboard
open http://127.0.0.1:8002/workbench
```

确认页面顶部能看到：

- **Plan Timeline 卡片**（上半部，待 demo 跑起来时填充）
- **Executor metrics panel**（中部，折叠）
- **Live Log Panel**（页面底部，深色终端样式）— 点开后状态应显示 `connected`

如果 Live Log Panel 显示 `disconnected` 或 `reconnecting…`：

- 检查浏览器控制台是否有 CORS / 404
- 确认 `/api/workbench/log-stream` 返回 200（curl 实测：`curl -N http://127.0.0.1:8002/api/workbench/log-stream`）

## 2. 演示流程（共 4 段，预计 8 分钟）

### 2.1 happy-path · nominal (~1.5 min)

**话术**：

> "Workbench 收到一份 ACCEPTED 提案，需要把 deploy threshold 从 0.9 调到 0.95。看左上 Plan Timeline ——5 步全程可视。"

```bash
# Terminal 2
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario nominal
```

**观察点**：

- Plan Timeline 5 步依次亮起：PLANNING → ASKING → EDITING → TESTING → PR_OPEN
- Live Log Panel 滚动出现：
  - `INIT → PLANNING (start_planning)`
  - `state_transition` × 5
  - `dry_run_complete: diff length: …`
- 终端 JSON 输出：`final_state=DRY_RUN_COMPLETE`，`plan_steps_completed=4/5`

**关键句**：dry-run 模式下，pipeline 走完了 PLANNING→EDITING→TESTING，但**没有 commit、没有 push、没有 PR**——审阅者用 `record.dry_run_diff` 预览即可决定是否真正执行。

---

### 2.2 governance pause · governance-hold (~2 min)

**话术**：

> "下一份提案触碰了 logic_truth namespace ——这是真值引擎的红线。这种修改 workbench 必须先暂停，等人类批准。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario governance-hold
```

**观察点**：

- Plan Timeline 在 PLANNING 后**先亮 GOVERNANCE_HOLD 步骤**（如果 UI 渲染了），而不是直接进 ASKING
- Live Log Panel：
  - `governance_required: …; logic_truth_namespace`（红字）
  - `governance_approved: auto-approve-mode`
- 终端 JSON：`governance_decision=approved`，`final_state=DRY_RUN_COMPLETE`
- 浏览器另开 tab： `http://127.0.0.1:8002/api/workbench/governance/history` —— 应能看到这条决策已**持久化**

**关键句**：决策不仅记到 audit JSON，也会落到 `data/governance_decisions.jsonl`，进程重启后仍可追溯。

---

### 2.3 transient retry · transient-retry (~1.5 min)

**话术**：

> "Planner 偶尔会撞上 LLM 服务的临时 5xx。我们不希望一次失败就把整条 pipeline 搞坏。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario transient-retry
```

**观察点**：

- Live Log Panel：
  - `planner_retry: attempt=1/3 delay=… reason=simulated transient 503`（黄色 warn 行）
  - `planner_retry` 之后是 `plan_ready` —— 第二次调用成功
- 终端 JSON：`llm_calls_made >= 2`，`final_state=DRY_RUN_COMPLETE`

**关键句**：retry 是**指数退避**——重试不是无脑循环，而是 P50-03 的有限次数 + 累进延迟。

---

### 2.4 hard failure + forensics · hard-failure (~1.5 min)

**话术**：

> "如果 plan 引用了一段实际不存在的代码，那就不是"重试能救的错误"——pipeline 必须停下来，把现场打包给人看。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario hard-failure
```

**观察点**：

- Plan Timeline 在 EDITING 步骤**变红停下**
- Live Log Panel：
  - `edit_error: apply: old_snippet not found …`（红底）
  - `EDITING → FAILED`
- 终端 JSON：`final_state=FAILED`，`abort_reason="apply: old_snippet not found …"`

**演示 forensics**：

```bash
# Terminal 3
curl -O http://127.0.0.1:8002/api/skill-executions/forensics-bundle
unzip -l forensics-bundle.zip | head
```

应能看到 manifest.json、README.txt、audits/、slo_history.jsonl —— **一个 zip 把现场全部打包**，团队任何一个人都能离线复现。

## 3. 时间表

| 段 | 内容 | 预算时间 |
|----|------|----------|
| 1  | 演示前准备 + 浏览器打开 dashboard | 1 min |
| 2.1 | nominal happy path | 1.5 min |
| 2.2 | governance-hold + history persistence | 2 min |
| 2.3 | transient-retry | 1.5 min |
| 2.4 | hard-failure + forensics bundle | 1.5 min |
| 3  | Q&A buffer | 2 min |
| **总计** | | **~9.5 min** |

实际单次运行均 < 1s（见 `runs/workbench_demo_rehearsal_*/summary.jsonl`），话术耗时是主成本。

## 4. 应急措施

| 情况 | 操作 |
|------|------|
| Live Log Panel 长时间 `reconnecting…` | 浏览器刷新，或在 Terminal 1 看 demo_server 是否还在 |
| Plan Timeline 不更新 | 手动 `curl http://127.0.0.1:8002/api/skill-executions` 看最新一条 record 是否带 `plan_steps` 字段 |
| 4 个 scenario 中任一报错 | 切到 Terminal 2 看完整 JSON 输出，`workspace` 字段指向 tmp 目录，`workspace/execs/` 下有 audit JSON 可读 |
| 演示场地无网络 | 整套链路是同源 + in-memory，不依赖外网；唯一需要的 `MINIMAX_API_KEY` 默认有 fake 值（conftest 设置的 demo-fake-key） |
| 错误不可复现 | `python3 scripts/workbench_demo.py --scenario X --keep-workspace`，tmp 目录会保留供 post-mortem |

## 5. 演示后清理

```bash
# Terminal 1: Ctrl+C the demo_server
# Terminal 2: 无需清理（每个 run 用独立 tmp 目录）
# 浏览器：可关闭

# 可选：清理 governance history（重置后续 demo 的 dashboard）
rm -f data/governance_decisions.jsonl
```

## 6. Rehearsal 数据参考

> 2026-04-27 dress rehearsal: 4 scenarios × N=2

| Scenario | Runs | Final state(s) | Avg wall-clock |
|----------|------|----------------|----------------|
| nominal | 2 | DRY_RUN_COMPLETE × 2 | 0.633 s |
| governance-hold | 2 | DRY_RUN_COMPLETE × 2 | 0.577 s |
| transient-retry | 2 | DRY_RUN_COMPLETE × 2 | 0.575 s |
| hard-failure | 2 | FAILED × 2 | 0.321 s |

完整数据：`runs/workbench_demo_rehearsal_20260427T121730Z/`

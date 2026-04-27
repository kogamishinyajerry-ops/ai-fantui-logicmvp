# Workbench Demo Script · v-demo-workbench-r2

> Generated 2026-04-27 as part of P52-09 dress rehearsal v2.
> Tag: `v-demo-workbench-r2` · main HEAD after PR #92 (P52-08).
> Supersedes `v-demo-workbench-r1` (P51-04 era), reflecting the
> dock + drawer UX restructure (P52-00..08).

## 1. 演示前准备 (T-5 min)

```bash
# Terminal 1 — start the workbench backend
PYTHONPATH=src python3 -m well_harness.demo_server --host 127.0.0.1 --port 8002

# Browser tab — open the dashboard
open http://127.0.0.1:8002/workbench
```

UX restructure 之后看到的初始页面：

- **左侧 64px Dock**：4 个图标按钮（新建 / 批注 / 审批 / 监控），inline SVG，currentColor
- **页面主体**：Control Logic Circuit hero（L1→L4 反推链路 SVG）—— 占据右侧主舞台
- **没有底部条 / 没有右侧 inbox**：Plan Timeline + Metrics + Live Log 全部归到 dock 的 drawer 里

要看运行细节，点 **监控（monitor）** dock 按钮：drawer 从左侧滑入，里面是 executor metrics 卡片 + 实时日志流。
要审阅工单，点 **审批（approve）**：drawer 内含 Governance Gate + Review Queue + Approval Center。
要提建议，点 **批注（annotate）**：drawer 内含 suggestion form + interpreter strategy chip + 解读结果卡。

## 2. 演示流程（共 4 段，预计 8 分钟）

### 2.1 happy-path · nominal (~1.5 min)

**话术**：

> "Workbench 收到一份 ACCEPTED 提案，需要把 deploy threshold 从 0.9 调到 0.95。点左侧 dock 的 monitor 按钮看实时执行 ——Plan Timeline + 5 步全程可视。"

```bash
# Terminal 2
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario nominal
```

**操作**：

1. 演示开始前点开 monitor drawer（保持开着便于观察）
2. 切换到 Terminal 2，跑命令
3. 回到浏览器看 monitor drawer 的 metrics + log 滚动

**观察点**：

- monitor drawer 的 metrics 卡片更新：total +1
- monitor drawer 的 live log 滚动出现：
  - `INIT → PLANNING (start_planning)`
  - `state_transition` × 5
  - `dry_run_complete: diff length: …`
- 终端 JSON：`final_state=DRY_RUN_COMPLETE`，`plan_steps_completed=4/5`

**关键句**：dry-run 模式下，pipeline 走完了 PLANNING→EDITING→TESTING，但**没有 commit、没有 push、没有 PR**。审阅者用 `record.dry_run_diff` 预览即可决定是否真正执行。

---

### 2.2 governance pause · governance-hold (~2 min)

**话术**：

> "下一份提案触碰了 logic_truth namespace ——这是真值引擎的红线。这种修改 workbench 必须先暂停，等人类批准。点 dock 的 approve 按钮，看 governance gate。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario governance-hold
```

**操作**：

1. 切到 approve drawer
2. 跑命令
3. 看 drawer 顶部 Governance Gate 区（amber 左侧 3px 长条）出现新条目

**观察点**：

- approve drawer Governance Gate panel：
  - `governance_required: …; logic_truth_namespace`（amber 提示）
  - `governance_approved: auto-approve-mode`
- 终端 JSON：`governance_decision=approved`，`final_state=DRY_RUN_COMPLETE`
- 浏览器另开 tab： `http://127.0.0.1:8002/api/workbench/governance/history` —— 应能看到这条决策已**持久化**

**关键句**：决策不仅记到 audit JSON，也会落到 `data/governance_decisions.jsonl`，进程重启后仍可追溯。

---

### 2.3 transient retry · transient-retry (~1.5 min)

**话术**：

> "Planner 偶尔会撞上 LLM 服务的临时 5xx。我们不希望一次失败就把整条 pipeline 搞坏。看 monitor drawer 的 live log。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario transient-retry
```

**观察点**：

- monitor drawer live log（已经是 monospace 字体，列对齐清晰）：
  - `planner_retry: attempt=1/3 delay=… reason=simulated transient 503`（黄色 warn 行）
  - `planner_retry` 之后是 `plan_ready` —— 第二次调用成功
- 终端 JSON：`llm_calls_made >= 2`，`final_state=DRY_RUN_COMPLETE`

**关键句**：retry 是**指数退避**——重试不是无脑循环，而是 P50-03 的有限次数 + 累进延迟。

---

### 2.4 hard failure + forensics · hard-failure (~1.5 min)

**话术**：

> "如果 plan 引用了一段实际不存在的代码，那就不是'重试能救的错误'——pipeline 必须停下来，把现场打包给人看。"

```bash
PYTHONPATH=src python3 scripts/workbench_demo.py --scenario hard-failure
```

**操作**：保持 monitor drawer 打开

**观察点**：

- monitor drawer live log：
  - `edit_error: apply: old_snippet not found …`（红底）
  - `EDITING → FAILED`
- 终端 JSON：`final_state=FAILED`，`abort_reason="apply: old_snippet not found …"`

**演示 forensics**：

```bash
# Terminal 3
curl -O http://127.0.0.1:8002/api/skill-executions/forensics-bundle
unzip -l forensics-bundle.zip | head
```

应能看到 manifest.json、README.txt、audits/、slo_history.jsonl —— **一个 zip 把现场全部打包**。

也可在 monitor drawer 顶部的 metrics summary 行看到 **📥 forensics** 链接，直接点击下载。

## 3. 演示新增亮点（v2）

| 亮点 | 在 v1 (r1) 是什么样 | v2 (r2) 现在是 |
|------|---------------------|----------------|
| 工作台第一屏 | inbox + circuit + bottom bar 全堆一起 | dock + 单一控制面板 + 抽屉 |
| 执行 metrics | 嵌在 inbox 中部，折叠 | monitor drawer 顶部，2×2 大数字 |
| Live Log | 页面底部 fixed 栏 | monitor drawer 内联，monospace 字体 |
| 审批入口 | 底部 "审批中心" 按钮 | dock approve 按钮 → 抽屉里集中三栏 |
| 批注流程 | 嵌在主流页面，scrolldown 找 | dock annotate 按钮 → 模板输入直接进入 |
| 新建电路 | "Coming soon" 占位 | 真实模板选择 + 派生 + 命名表单 |
| 键盘 a11y | dock 按钮可 Tab，但 drawer 内焦点不管理 | drawer 打开自动聚焦关闭按钮，关闭返回触发 dock 按钮 |

## 4. 时间表

| 段 | 内容 | 预算时间 |
|----|------|----------|
| 1  | 演示前准备 + 浏览器打开 dashboard | 1 min |
| 1.5 | dock 总览（演示者点击 4 个 dock 按钮各打开一次抽屉） | 0.5 min |
| 2.1 | nominal happy path（保持 monitor drawer 开） | 1.5 min |
| 2.2 | governance-hold（切到 approve drawer 看 gate） | 2 min |
| 2.3 | transient-retry（monitor drawer log） | 1.5 min |
| 2.4 | hard-failure + forensics bundle | 1.5 min |
| 3  | Q&A buffer | 1.5 min |
| **总计** | | **~9.5 min** |

实际单次运行均 < 1s（见 `runs/workbench_demo_rehearsal_v2_*/summary.jsonl`）。

## 5. 应急措施

| 情况 | 操作 |
|------|------|
| Dock 抽屉点不开 | 浏览器 console 查 `_wbDockBoot`，确认 dock element 找到了 |
| 抽屉打开但内容错位 | 检查 body[data-active-tool] 是否被设置；该 attr 驱动 CSS 显示 |
| Live Log 长时间 `reconnecting…` | 同 v1：浏览器刷新 + Terminal 1 检查 |
| Plan Timeline 不更新 | `curl http://127.0.0.1:8002/api/skill-executions` |
| 4 个 scenario 中任一报错 | 切到 Terminal 2 看完整 JSON 输出 |
| Tab 键焦点跳到外部 | 在 dock 上按 Tab 应该停在 4 个 dock 按钮内；若跳出去，检查 P52-08 focus mgmt 没回退 |

## 6. 演示后清理

```bash
# Terminal 1: Ctrl+C the demo_server
rm -f data/governance_decisions.jsonl  # 可选：清理 governance history
```

## 7. Rehearsal v2 数据参考

> 2026-04-27 dress rehearsal v2: 4 scenarios × N=2 后 P52 重构

| Scenario | Runs | Final state(s) | Avg wall-clock |
|----------|------|----------------|----------------|
| nominal | 2 | DRY_RUN_COMPLETE × 2 | 0.675 s |
| governance-hold | 2 | DRY_RUN_COMPLETE × 2 | 0.675 s |
| transient-retry | 2 | DRY_RUN_COMPLETE × 2 | 0.645 s |
| hard-failure | 2 | FAILED × 2 | 0.365 s |

完整数据：`runs/workbench_demo_rehearsal_v2_20260427T223000Z/`

时间和 r1 基本一致 —— P52 是纯 UI 重构，没动后端逻辑，所以 wall-clock 没变化。

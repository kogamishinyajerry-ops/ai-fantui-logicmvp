# Demo Disaster Runbook (P20.2)

立项汇报彩排与真实 demo 演示的灾难恢复手册。7 个失败场景，每个场景 4 字段：
**检测信号** · **立即话术（面向观众）** · **恢复动作（< 60s 可执行）** · **最坏兜底（不可恢复时的降级路径）**。

适用对象：Kogami（主讲）+ 备份操作员。所有恢复动作均已在 `scripts/dress_rehearsal.py`
或 `tests/e2e/` 中覆盖，话术经彩排验证。

---

## 场景 1 · MiniMax API key 缺失 / 超时 / 429

**检测信号**
- 聊天侧抽屉出现 `[降级]` 徽标或 `chat-degraded-notice` DOM 节点显示
- `/api/chat/reason` 返回 `{"llm_status":"degraded", ...}` 但 HTTP 200
- 控制台日志含 `minimax_api_key_missing` 或 `minimax_timeout`

**立即话术**
> "这里触发的是 R2 降级路径——AI 叙述层不可用时，真值引擎的 19 节点与 4 逻辑门依然给出结论。大家现在看到的因果链完全来自 logic1–logic4 门控，不是 LLM 生成的。"

**恢复动作（< 60s）**
1. **首选：切到本地 Ollama fallback（P21 PoC 已搭好）**
   ```bash
   export LLM_BACKEND=ollama
   export OLLAMA_MODEL=qwen2.5:7b-instruct   # 候选见 config/llm/local_model_candidates.yaml
   pkill -f well_harness.demo_server && python3 -m well_harness.demo_server &
   python3 archive/shelved/llm-features/scripts/pitch_prewarm.py
   ```
   浏览器硬刷后，聊天抽屉恢复工作；再跑一次 pitch prewarm，wow_a 的两个 canonical explain 问题会恢复为透明缓存命中。
2. 备选：`export MINIMAX_API_KEY=$BACKUP_MINIMAX_KEY`（备份 key 在 `.env.backup`）后重启 demo_server。
3. 浏览器硬刷（Cmd-Shift-R），重新触发一次 wow_a 轻触打底。

**最坏兜底**
- 跳过 LLM 叙述段，直接讲真值引擎对照：展示 `/api/lever-snapshot` 原始 JSON（浏览器 DevTools → Network）。
- 强调"AI 只解释、不决策"的 R2 原则恰好在此刻被证明。
- P21 切换细节见 `docs/demo/local_model_poc.md`。

---

## 场景 2 · 蒙特卡洛 10k 超时 / 内存尖峰

**检测信号**
- wow_b 高亮步骤进度条卡超过 5s
- `/api/monte-carlo/run` 5xx 或连接重置
- 浏览器 Tab 标题出现 "(Not Responding)"

**立即话术**
> "蒙特卡洛是纯数值通道，和 LLM 完全解耦。即便 10k trials 失败，我们降到 1k 也能给出置信区间——这是 R4 降级可控的例子。"

**恢复动作（< 60s）**
1. 切换讲解到 wow_b 的 1k baseline 结果截图（已预置于 `docs/demo/wow_b_monte_carlo.md` 附录）
2. 前端 UI 选择 `n_trials=1000` 重放一次（彩排验证 1k 稳定在 <200ms）
3. 若仍失败：跳到 wow_c 反诊断演示，蒙特卡洛延后到 Q&A

**最坏兜底**
- 打开 `runs/dress_rehearsal_20260418T063146Z/wow_b_timeline.json`，直接展示彩排基线数据。
- 口头对齐："此结果来自今晨彩排冻结基线，不是即时生成"——诚实性优先。

---

## 场景 3 · 前端白屏 / JS 崩溃

**检测信号**
- 页面整屏空白 / 骨架屏卡住
- DevTools Console 出现 uncaught TypeError 或 SVG 渲染异常
- DOM 中 `#zoom-container` 或 `#chain-topology-thrust-reverser` 缺失

**立即话术**
> "UI 层的健壮性是 P20.1 的收口重点。后端契约在这里照常输出——我们切到只读模式继续。"

**恢复动作（< 60s）**
1. 浏览器硬刷（Cmd-Shift-R），若失败继续
2. 切换到预录彩排视频回放（`docs/demo/` 未来补齐；当前用 rehearsal_report.md 展示）
3. DevTools → Network → 验证 `/api/lever-snapshot` 仍返回 19 节点，口头解释

**最坏兜底**
- 切到 `scripts/dress_rehearsal.py` 终端，现场 `python3 scripts/dress_rehearsal.py --smoke` 演示 API 层全绿
- 讲解转向架构层叙事：前后端解耦 + R1 真值优先

---

## 场景 4 · Demo server 进程挂掉（:8799 不应答）

**检测信号**
- `curl http://127.0.0.1:8799/api/lever-snapshot` 超时
- 终端看到 Traceback / OSError
- 浏览器所有 XHR 全 Failed

**立即话术**
> "这是一次典型的服务端崩溃——我们的冻结基线此刻就派上用场。"

**恢复动作（< 60s）**
```bash
cd ~/20260407\ YJX\ AI\ FANTUI\ LogicMVP
pkill -9 -f well_harness.demo_server || true
nohup python3 -m well_harness.demo_server > /tmp/demo_server.log 2>&1 &
sleep 2 && curl -sf http://127.0.0.1:8799/api/lever-snapshot -X POST -d '{}' -H 'content-type: application/json' | head -c 200
```

**最坏兜底**
- 切到备机（若有）：已预启动 :8800 镜像
- 无备机则切离线包：`tar -xf runs/rehearsal_*_baseline.tar.gz` → 用彩排输出讲解

---

## 场景 5 · 网络离线 / 会场 WiFi 故障

**检测信号**
- 浏览器右下角网络图标显示断连
- 任何外部 CDN（若有）资源 404

**立即话术**
> "本项目全栈本地运行，不依赖外网。MiniMax 叙述层降级，其余照常。"

**恢复动作（< 60s）**
1. 确认 demo_server 在 `127.0.0.1:8799`（纯本地），非 0.0.0.0 依赖 DNS
2. 若涉及 MiniMax：自动触发场景 1 降级路径
3. 切手机热点作为兜底（耗时 > 60s 则放弃，直接走兜底）

**最坏兜底**
- 完全离线讲解：打开 `runs/dress_rehearsal_*/rehearsal_report.md`（Markdown 本地渲染）+ `docs/demo/wow_{a,b,c}_*.md`
- 强调 R3 可审计：所有结果都有冻结基线，无需联网复现

---

## 场景 6 · 证据压缩包导出失败（Archive）

**检测信号**
- 点击 "导出证据包" 按钮无反应 / 报错
- `/api/archive/download` 返回 500 或缺字段

**立即话术**
> "导出路径是 R3 可审计原则的落地——即使失败，我们有 runs/ 目录下的明文冻结包。"

**恢复动作（< 60s）**
1. 直接在 Finder 打开 `runs/dress_rehearsal_20260418T063146Z/`
2. 展示 `rehearsal_report.md` + 三份 `*_timeline.json`——同等证据粒度
3. 若坚持要 tar.gz：终端 `tar -czf /tmp/demo_evidence.tar.gz runs/dress_rehearsal_20260418T063146Z/`

**最坏兜底**
- 跳过导出步骤，直接讲"证据已预冻结在 `docs/freeze/2026-04-18-rehearsal-baseline.md`"
- 将压缩包作为课后交付物补寄，不阻塞演示

---

## 场景 7 · 投屏分辨率错位 / 字体缺失 / 缩放爆掉

**检测信号**
- SVG 超出可视区 / 字符显示为方框
- 节点标签重叠成一团 / zoom-container transform 跑飞

**立即话术**
> "投影分辨率问题——我们切到演示友好布局。"

**恢复动作（< 60s）**
1. 浏览器 `Cmd-0` 重置缩放
2. 若 SVG 错位：URL 加 `?zoom=fit` 或手动调 `#zoom-container` transform（DevTools）
3. F11 全屏，消除浏览器 chrome 遮挡

**最坏兜底**
- 切到备用笔记本（1920×1080 已预先校准）
- 或改用投影仪镜像模式（非扩展），牺牲主屏但保讲台一致

---

## 通用原则（所有场景共享）

1. **先播报，后恢复**：让观众知道发生了什么，比沉默 30s 修机器专业。
2. **不假装**：R1 真值优先——如果恢复失败，直接说"切到冻结基线"，别硬撑。
3. **60s 限时**：任何单一恢复动作超过 60s 立即切最坏兜底，不要连续尝试。
4. **冻结基线是底牌**：`runs/dress_rehearsal_*` + `docs/freeze/*` 永远可用。

_Compiled by P20.2 dress rehearsal · Execution-by: opus47-max_

# 演示机预检 Checklist — 立项汇报当天

**目标：** T-60 分钟 → T-0 分钟，16 项必检；每项要么可一键执行，要么肉眼可见信号。
**一切签字签时间，如有失败立即按 `docs/demo/disaster_runbook.md` 对应场景处理。**

---

## T-60 · 硬件 + 系统层（4 项）

| # | 项目 | 一键命令 / 检查 | Pass 信号 | Fail 处置 |
| - | ---- | --------------- | --------- | --------- |
| 1 | 电源 + 充电线接好 | 肉眼检查 | 电池图标带闪电 | 换电源位 |
| 2 | 外接显示器 + HDMI | `system_profiler SPDisplaysDataType | grep Resolution` | 输出 ≥ 1920×1080 | 换线 / 重插 |
| 3 | 音频（如需要）| 试播 1s 静音视频 | 不弹错 | mute 系统 |
| 4 | 网络（MiniMax 需要）| `curl -sI https://api.minimax.chat/v1/text/chatcompletion_v2 -X POST -m 3 | head -1` | HTTP/* 返回任意状态码 | 切网络 / 切 Ollama fallback |

---

## T-50 · 仓库 + 分支（3 项）

| # | 项目 | 一键命令 | Pass 信号 | Fail 处置 |
| - | ---- | -------- | --------- | --------- |
| 5 | 当前分支 = main | `cd ~/20260407*LogicMVP && git branch --show-current` | `main` | `git checkout main` |
| 6 | main 无 uncommitted | `git status --short` | 空输出 | `git stash` 或检查原因 |
| 7 | HEAD 指向最新 closure commit | `git log -1 --oneline` | P22-05 或 PATCH commit | `git pull` |

---

## T-40 · 依赖 + API key（3 项）

| # | 项目 | 一键命令 | Pass 信号 | Fail 处置 |
| - | ---- | -------- | --------- | --------- |
| 8 | Python 3.9+ 可用 | `python3 --version` | `Python 3.9+` | 装 Python |
| 9 | MiniMax key 就位 | `test -s ~/.minimax_key && echo OK` | `OK` | 从备份 vault 恢复 |
| 10 | Ollama 服务 + 7B 模型 | `ollama list | grep -E 'qwen2.5:7b'` | 有 `qwen2.5:7b-instruct` 行 | `ollama pull qwen2.5:7b-instruct` |

---

## T-30 · 测试基线绿（3 项）

| # | 项目 | 一键命令 | Pass 信号 | Fail 处置 |
| -- | ---- | -------- | --------- | --------- |
| 11 | 主 pytest 绿 | `python3 -m pytest --tb=short -q 2>&1 | tail -3` | `passed` 数 ≥ 658 | 看回归，决定是否回退 |
| 12 | e2e 绿 | `python3 -m pytest -m e2e --tb=short -q 2>&1 | tail -3` | `49 passed` | 单独 debug 失败 case |
| 13 | 对抗绿 | 启 demo_server :8766 → `python3 src/well_harness/static/adversarial_test.py 2>&1 | tail -3` | `ALL TESTS PASSED` | 不能演对抗段 |

---

## T-20 · 双后端真跑（2 项）

| # | 项目 | 一键命令 | Pass 信号 | Fail 处置 |
| -- | ---- | -------- | --------- | --------- |
| 14 | 双后端 rehearsal | `python3 scripts/demo_rehearsal_dual_backend.py 2>&1 | tail -3` | `verdict=PASS` | Ollama 重启 / 按 disaster_runbook 场景 1 |
| 15 | Dress rehearsal（wow 轨）| `python3 scripts/dress_rehearsal.py 2>&1 | tail -3` | `13/13 pass` | 查 controller.py 回归 |

---

## T-10 · 浏览器 + 演示态（1 项）

| # | 项目 | 一键命令 / 动作 | Pass 信号 |
| -- | ---- | --------------- | --------- |
| 16 | demo_server 可访问 + Canvas 渲染 | 启 `python3 -m well_harness.demo_server --port 8799 &` → 浏览器开 `http://127.0.0.1:8799/` → 硬刷 Cmd-Shift-R | 19 节点可见 + 聊天抽屉可展开 |

---

## T-0 · 签发

- [ ] 所有 16 项 Pass
- [ ] 演讲者已读 `docs/demo/pitch_script.md` 时间表（20 分钟硬分配）
- [ ] 演讲者已扫 `docs/demo/faq.md` 关键词跳转表
- [ ] `docs/demo/disaster_runbook.md` 7 场景纸面放在桌角
- [ ] 备份方案：本机断网后直接切 Ollama；Ollama 挂时切 disaster_runbook 场景 1 最坏兜底

**签字：_______________________ 时间：_______________________**

---

## 一键预检脚本（可选加速）

如果想一次跑完 #8–#15 自动化项：

```bash
cd ~/20260407*LogicMVP

# Tests
python3 -m pytest --tb=short -q 2>&1 | tail -3
python3 -m pytest -m e2e --tb=short -q 2>&1 | tail -3

# Dual-backend rehearsal
python3 scripts/demo_rehearsal_dual_backend.py --skip-minimax-if-no-key --skip-ollama-if-unreachable 2>&1 | tail -5

# Dress rehearsal
python3 scripts/dress_rehearsal.py 2>&1 | tail -3
```

**三行绿 + verdict=PASS + 13/13 = 全部 pass。** 看到任何红即按 disaster_runbook 处置。

---

## 应急一页纸（打印版）

```
┌── DEMO EMERGENCY ────────────────────────────────┐
│                                                  │
│  1. 云 API 挂？                                   │
│     → export LLM_BACKEND=ollama                  │
│       OLLAMA_MODEL=qwen2.5:7b-instruct           │
│       pkill -f demo_server                       │
│       python3 -m well_harness.demo_server &      │
│       Cmd-Shift-R                                │
│                                                  │
│  2. Ollama 也挂？                                 │
│     → 跳过段 4；直接讲 truth engine JSON          │
│       见 docs/demo/disaster_runbook.md 场景 1     │
│                                                  │
│  3. 蒙特卡洛 10k 卡？                             │
│     → n_trials=1000；引 wow_b_timeline.json 48ms │
│                                                  │
│  4. Canvas 不渲染？                               │
│     → pkill -f demo_server && 重启 && 硬刷        │
│                                                  │
│  5. 甲方打断？                                    │
│     → docs/demo/faq.md 关键词跳转                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

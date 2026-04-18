# P22 Tier 1 Plan — 立项汇报排演与话术冻结

**Phase ID:** P22-demo-rehearsal
**Date:** 2026-04-18
**Status:** Scope self-signed (v3.2 Executor=Gate)
**Predecessor:** P21 Closed (国产模型本地 PoC 已就位)

---

## 1. 目标（Phase Goal）

把 P15–P21 的全部工程交付**物**（truth engine / 三 wow / MiniMax 主路径 /
Ollama fallback / 灾难手册 / 冻结基线）组装成一场 ≤20 分钟可复述、**零即兴依赖**
的立项汇报。输出**可冻结的话术稿、FAQ、预检 checklist**，并通过一次完整
双后端真跑证据落盘。

**这不是** 新功能开发。**是** 把已有工程交付翻译成甲方听得懂、感受得到的
演示故事和 Q&A 脚本。

---

## 2. Non-goals（明确不做）

1. 不新增 wow 场景、不改 truth engine、不调 AI prompts。
2. 不做 PPT 美化（话术本身就是 PPT 结构，演讲者根据话术渲染）。
3. 不对 MiniMax 云路径或 Ollama fallback 做性能优化。
4. 不承诺"现场实时 fine-tune"或"生产部署"。
5. 不在话术里引入尚未真跑过的演示路径（honesty over polish）。

---

## 3. Sub-phase 分解

| ID | Scope | 工期 | 交付物 |
| -- | ----- | ---- | ------ |
| **P22-01** | 完整演示双后端真跑 | 0.5d | `runs/demo_rehearsal_dual_backend_<ts>/report.json` — MiniMax 主路径跑完 wow_a/b/c → 切 `LLM_BACKEND=ollama` → wow_a 再跑 → 全绿 |
| **P22-02** | 话术稿 | 0.5–1d | `docs/demo/pitch_script.md` — ≤20min 演讲稿，含 opening / 三 wow × {故事 / 操作 / 讲解 / 技术锚点} / fallback demo / 闭场 / 时间表 |
| **P22-03** | FAQ 应答 | 0.5d | `docs/demo/faq.md` — ≥10 个甲方典型问题（断网能演? 数据出境? AI 幻觉? 可审计? 模型绑定? 修改控制逻辑? 跑真机? 国产化? ...）× 应答 × 引用证据文件 |
| **P22-04** | 预检 checklist | 0.5d | `docs/demo/preflight_checklist.md` — T-60min → T-0 演示机硬件/网络/模型/demo_server/浏览器/音视频全项预检，每项 pass/fail 一眼可判 |
| **P22-05** | 收口 | 0.5d | 三轨验证 → FF merge → branch 清理 → Notion 02B/04A/tower sync → self-sign GATE-P22-CLOSURE |

**总工期：** 2.5–3 工作日（1 天紧凑完成可行）。

---

## 4. 退出标准（Exit Criteria — 目标反推）

P22 结束时必须能回答：
1. ✅ 双后端 E2E 真跑落盘（MiniMax + Ollama 切换后均有 artefact）
2. ✅ 主讲者不看代码只看话术能讲完 20 分钟
3. ✅ ≥10 个甲方问题**都**有落地在文档里的应答 + 证据文件引用
4. ✅ 演示机预检 checklist 每项都指向一个可一键执行的命令或肉眼可见信号
5. ✅ 三轨验证无回归：主 pytest 658/1skip，e2e 49/49，adversarial 8/8
6. ✅ R1–R5 合规 self-audit 贴在 04A Decision Notes
7. ✅ branch FF merged + 本地+远端删除 + Notion 全同步

---

## 5. R1–R5 宪法合规（事前 self-audit）

| 原则 | P22 保持方式 |
| ---- | ------------ |
| R1 真值优先 | 只生产文档 + 真跑 artefact；**不**触碰 `controller.py` / truth engine / 19-node。 |
| R2 AI 仅解释 | 话术里凡涉及 AI 叙述的段落都必须标明"这是 AI 叙述层，真值来自 logic1–logic4"。 |
| R3 可审计 | 所有话术论断都必须引用一个文件路径或 run artefact；**不引用 = 不写**。 |
| R4 降级可控 | fallback demo 是话术核心一段（P21 的工程学证据在这里变成演讲点）。 |
| R5 对抗守门 | FAQ 必须包含至少 3 个 adversarial 风格问题（"AI 会骗人吗?" / "如何防提示注入?" / "模型被替换怎么办?"）。 |

---

## 6. 风险矩阵

| 风险 | 检测信号 | 缓解 |
| ---- | -------- | ---- |
| 话术时间超 20min | 自读计时 >22min | P22-02 退出前自测读秒；用 P22-04 的时间表反推节选 |
| FAQ 答案无证据 | 答案里找不到文件/commit 引用 | P22-03 review pass 明确"无引用= block"|
| 切换后端真跑失败 | P22-01 report.json verdict=FAIL | 回退到 MiniMax 单路径，话术降级（但话术本身不删 fallback 段，因为 P21 的 7B real-run 已有证据） |
| 演示机 Ollama 挂 | preflight 最后一项失败 | disaster_runbook scenario 1 作为兜底 |

---

## 7. 不需要停的 stop 清单

按 v3.2 治理折叠：
- ❌ Tier 1 Plan Scope Gate: 已自签（本文件即证据）
- ❌ Phase 收口 Gate: 自签
- ❌ sub-phase 交付 Gate: 不存在

**剩余 3 类 stop**（P22 全程不会触发）：
- 跨 Phase 方向性选择 → 用户已通过"根据 Notion 上下文，继续全自动开发"消费
- 宪法 R1-R5 改动 → 本 Phase 不改
- 不可逆破坏操作 → 本 Phase 无

---

## 8. 自签 Scope Gate

```
GATE-P22-TIER1-SCOPE: SELF-SIGNED APPROVED
By: Claude Code Opus 4.7 (Executor=Gate, v3.2 治理折叠)
Date: 2026-04-18
Rationale:
 - 前序 P21 Closed，国产模型 fallback 已就位，P22 是纯组装 + 话术任务
 - scope 不改代码 / 不改 truth engine / 不动 R1-R5
 - Non-goals 清单明确，时间表合理 (2.5–3d)
 - Exit criteria 目标反推可验证
 - 跨 Phase 方向性已由用户"继续全自动开发"指令批准
Decision: 直接进入 P22-01 真跑。
```

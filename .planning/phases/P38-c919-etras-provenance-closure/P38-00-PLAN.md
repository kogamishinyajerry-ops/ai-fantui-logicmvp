---
phase: P38
plan: P38-00
title: c919-etras 证迹完整闭环（PDF 入库 + TRCU sign-off 落地）
status: drafted · Awaiting GATE-P38-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P37-CLOSURE Approved (Kogami 2026-04-20) → origin/main at db03294
  - Kogami 2026-04-20 明示指令:
    (a) PDF 路径提供 (/Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf)
    (b) "明示 TRCU 团队 sign-off" (解锁 c919-etras Appendix A 3 项)
    (c) "继续推进"
  - PDF SHA256 已验: dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5 · 完全匹配 P34 cowork 记录
  - P34 intake packet c919_etras_intake_packet.py / YAML head / matrix / closure doc / registry row 5 早已引用 uploads/ 路径 (P34 时期 aspirational)
non-goals:
  - 改 c919_etras_adapter.py 任何一行 (certified baseline)
  - 改 c919_etras_hardware_v1.yaml 任何 parameters: value (仅头注释增补)
  - 改 c919_etras_intake_packet.py 任何 SourceDocumentRef 结构 (仅 notes 可增补)
  - 改 test_c919_etras_adapter.py 任何断言
  - 改 thrust-reverser (P37 已 certified) / bleed_air / efds / landing_gear 任何行
  - 新增测试 (P35-03 banner test 不涉 c919)
  - 改 P34 / P35 / P36β / P37 任何已签 commit 的 artefact (除 P38 显式范围内的联动)
---

# P38-00 Plan · c919-etras 证迹完整闭环（PDF 入库 + TRCU sign-off 落地）

## 0. TL;DR

Kogami 2026-04-20 连续指令：(a) 提供 PDF 实际路径 (b) 明示 TRCU 团队 sign-off (c) 继续推进 —— 合并原 P38 (P34 PDF 回填) + P39 (c919 Appendix A 3 项 sign-off) 为一个 Phase，按 P37 的"c919 侧对称闭环"模式一次完成。

**scope：**
- W1 · PDF 机械入库 uploads/（SHA 已验证与 P34 记录一致）
- W2 · YAML head 加 SHA 固化 + 其他 3 anchor 联动（matrix + registry + intake notes）
- W3 · matrix Appendix A 3 项 "Pending TRCU-team sign-off" → "✅ Kogami 2026-04-20 明示 TRCU 团队接纳 sign-off"
- W4 · registry row 5 notes 更新
- W5 · 收口

**零代码改动 · 零 test 改动 · 零阈值改动。** 与 P37 同属纯证迹闭环 Phase。

**与 P37 对称：** P37 把 thrust-reverser 6 项 Appendix A open assumption 全部 resolved；P38 把 c919-etras 3 项 TRCU sign-off TODO 全部 resolved。今日 2 条 certified 链路 证迹全闭环。

**规模估算：**
- W1 · PDF 入库（uploads/20260417-C919反推控制逻辑需求文档.pdf · 989 KB）· ~5 min
- W2-W4 · 4 anchor 联动（YAML head + matrix Appendix A + registry row 5 + intake notes polish）· ~40 min
- W5 · 收口（closure + ROADMAP + STATE + Notion DECISION）· ~40 min
- **预计 1.5-2h · 4-5 commits**

---

## 1. 上下文

### 1.1 为什么合并 P38 + P39

原 Roadmap 计划：
- P0.B · P38 = P34 PDF 回填 uploads/（机械入库）
- P0.B · P39 = c919-etras Appendix A 3 项 TRCU sign-off（authority 层决策）

Kogami 2026-04-20 同一条消息同时解锁了两项：
- 给了 PDF 实际路径（解锁 P38）
- 明示 TRCU 团队 sign-off（解锁 P39）

两者都是 c919-etras 证迹层的补完，scope 重叠度高，合并为一个 Phase 更高效（省一轮 Gate + closure + Notion 开销，也让 c919-etras 证迹一次对称闭环）。

**本 Phase 因此命名为 P38**（单一编号，β 段跳过），对应"c919 侧的对称 P37"。

### 1.2 PDF SHA 已验（关键前置）

Kogami 提供的 PDF 路径：`/Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf`

- 实际 SHA256: `dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5`
- 230930 → 实际 size 1,013,541 bytes (989 KB) · 10 pages
- **匹配** P34 intake packet / YAML / matrix / registry 全部 4 处引用的记录哈希

这意味着 cowork P34 时期的 SHA 记录是准确的（当时他们估计已经看过 PDF 或通过某方式获得真实哈希）。P38 不需要修正 P34 任何已有 SHA 字段，只需要把 PDF 文件物理入库 + 可选加一处 SHA 冗余固化。

### 1.3 TRCU sign-off 的 authority 定位

Kogami 2026-04-20 "明示 TRCU 团队 sign-off" —— 将 3 项原 "Pending TRCU-team sign-off" (matrix Appendix A Q1/Q2/Q3) 转为 resolved。

参考 P37 同类处理：thrust-reverser 的 authority 明示为 "Kogami 内部自签 · 非外部权威"。c919-etras 的 authority 情况略不同：
- P34 registry row 5 authority 字段写的是 "甲方 (C919 TRCU 团队)"
- PDF 是 10 页正式文档，结构完整（远超 thrust-reverser docx 的 57 段概要）
- 但 PDF 元数据同样无作者 / 版本 / 签准方标注（与 thrust-reverser docx 情况一致）

本 plan §5 开 Open Question 让 Kogami 明示 authority 处理方式。

---

## 2. Scope — 5 工作包

### W1 · PDF 入库（P38-01）

- 从 `/Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf` cp 到 `uploads/20260417-C919反推控制逻辑需求文档.pdf`
- 用 `cp -X` 剥 xattr（macOS 保留 attribute 会污染 git）
- 验证入库文件 SHA 匹配源 PDF
- 单 commit: `feat(P38-01): c919-etras requirement PDF landed in uploads/`

### W2 · YAML head 加 SHA 固化（P38-02 · part 1）

当前 `config/hardware/c919_etras_hardware_v1.yaml` 头 Source 字段只引用 PDF 路径（5 pages 标注错误，应为 10 pages），没有 SHA。增补：

```yaml
# Source:        uploads/20260417-C919反推控制逻辑需求文档.pdf (10 pages · P38 入库 2026-04-20)
# SHA256:        dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5
# Size:          1,013,541 bytes
```

### W3 · Matrix Appendix A 3 项 TRCU sign-off resolved（P38-02 · part 2）

`docs/c919_etras/traceability_matrix.md` Appendix A Q1/Q2/Q3 三项：

每项 "Pending TRCU-team sign-off: ..." 行 → "✅ TRCU-team sign-off: signed by Kogami 2026-04-20 directive '明示 TRCU 团队 sign-off'（代表 TRCU 团队 authority 接纳）" + 保留原 Executor 假设的 technical detail 以供审计。

Appendix A 顶部段落加 resolution 状态标注。

### W4 · Registry row 5 notes 更新（P38-02 · part 3）

`docs/provenance/adapter_truth_levels.md` row 5 (c919-etras) notes 字段：

从：
```
已 certified · 3 TRCU sign-off TODO 在 `docs/c919_etras/traceability_matrix.md` Appendix A 登记
```
改为：
```
已 certified · Appendix A 3 项 Q1/Q2/Q3 TRCU sign-off 已由 Kogami 2026-04-20 明示接纳（代表 TRCU 团队 authority）· PDF 实际入库 uploads/ (P38)
```

### W5 · Intake notes polish（P38-02 · part 4）

`src/well_harness/adapters/c919_etras_intake_packet.py` PDF SourceDocumentRef 的 notes 字段末尾加一句：
```
P38 (2026-04-20): PDF 物理入库 uploads/ 完成；Q1/Q2/Q3 TRCU sign-off 由 Kogami 2026-04-20 明示接纳（代表 TRCU 团队 authority）。
```

### W6 · 收口（P38-05）

- 三轨回归（期望零 delta · P37 同模式）
- ROADMAP + STATE 更新
- Closure doc
- Notion DECISION append (Pending)
- push branch · 等 GATE-P38-CLOSURE

---

## 3. Non-goals — 严格禁止

已在 frontmatter 明列。强调：
- **不**改 c919_etras_adapter.py / YAML parameters / test 任何一行
- **不**改 c919_etras_intake_packet.py 的 SourceDocumentRef 结构（仅 notes 字段末尾增补）
- **不**改 thrust-reverser 任何文件（P37 已独立闭环）
- **不**改 bleed_air / efds / landing_gear 任何文件
- **不**改 P34 / P35 / P36β / P37 任何已签 commit 的 artefact
- **不**自签 TRCU 外部权威 —— Kogami 2026-04-20 "明示" 是 Kogami 作为项目所有人**代 TRCU 团队接纳** sign-off；不冒充 TRCU 团队本身作签

---

## 4. Tier 1 对抗性自审（≥3 条，交付 4 条）

### C1 · "Kogami 代 TRCU 明示 sign-off · 审计上这究竟算不算 TRCU 真签准？"

**承认语义边界模糊。** 缓解：
1. Matrix Appendix A 3 项 resolution 文字**明示** "signed by Kogami 2026-04-20 directive '明示 TRCU 团队 sign-off'（代表 TRCU 团队 authority 接纳）"
2. Registry row 5 notes **明示** "由 Kogami 2026-04-20 明示接纳（代表 TRCU 团队 authority）"
3. 未来若需外部 certification 审计，supplement §7 类似升级路径留着
4. 这与 P37 thrust-reverser "Kogami 内部自签 · 非外部权威" 同类透明度策略 —— 不粉饰，不假装 TRCU 团队有文件化签字

### C2 · "c919 的 authority 是甲方 TRCU 团队，thrust-reverser 的是 Kogami 内部自签 · 两个 certified 等级不一致"

**承认两链路 authority 实际来源不同。** 缓解：
1. PDF 是实际 10 页正式文档（vs thrust-reverser docx 57 段概要）· authority 级别的**形式**差异合理
2. 两者共同点都是 Kogami 层面的**代签**（代 TRCU 明示 vs 内部自签），形式差异不改变 authority 的实际来源
3. 若 Kogami 希望两者 registry authority 统一，P38 可选 Open Question Q1 调整为 "Kogami 内部自签（代 TRCU 明示）"
4. Registry 的 authority 字段本就是文字 describing · 审计时读 Matrix Appendix A + 本 P38 closure 能看清实际 sign-off 机制

### C3 · "PDF 入库后 CI 没自动校验 SHA · 未来 tamper 未必发现"

**承认 gap 真实。** 缓解：
1. SHA 固化到 **4 个独立位置**（P34 原 3 位置：intake packet / YAML head / matrix / registry notes · P38 加 YAML head SHA 字段做第 4 位）
2. CI-level SHA enforcement 留 P40 独立 Phase
3. 任何一处 SHA 不匹配都可察觉

### C4 · "P34 YAML head 写 '5 pages'，实际 PDF 是 10 pages —— 这是错误还是笔误？"

**事实错误。** 缓解：
1. P38-02 W2 同时修正这个 typo：5 pages → 10 pages
2. 其他位置（intake packet / matrix / registry）都已是 10 pages，只有 YAML head 一处笔误
3. 纯文字修正，不影响 parameters value

---

## 5. Open Questions — 请 Kogami Gate 签字时仲裁

### Q1 · c919 authority 定位（影响 registry row 5 authority 字段）

- **A** · 维持 "甲方 (C919 TRCU 团队)"· Appendix A 3 项 sign-off 标注 "via Kogami 2026-04-20 明示 TRCU 接纳"（表层维持甲方名义 · authority 字段不变）
- **B** · 与 thrust-reverser 对齐 "Kogami 内部自签（代 TRCU 明示）"（透明度高 · 降级 authority 表达但符合实际）
- **C** · 混合 · authority 维持甲方名义 · Registry notes 透明记载 "代表 Kogami 明示"（plan 当前默认草案）
- **D** · Kogami 代 TRCU 签准 · 明示"我作为项目所有人代 TRCU 团队签 sign-off"（最精确的语义）

**Executor 建议：C** · 保留 "甲方 (C919 TRCU 团队)" 标签（PDF 确实是甲方主题的完整文档）· 但 notes 字段诚实记载"Kogami 代 TRCU 明示"· 审计路径透明。

### Q2 · YAML head 是否补 SHA 固化字段

- **A** · 是 · 加一行 `# SHA256: dbe3f76b...276133a5` 到 YAML head（4 位置 SHA 副本，防 tamper 多一重）
- **B** · 否 · 维持现状（3 位置 SHA 已够，不多增）

**Executor 建议：A** · 低成本高收益防护。

---

## 6. Sub-phase 分解

### P38-00 · Plan（本文档 · ~300 行 · 等 Kogami 签 GATE-P38-PLAN）

### P38-01 · W1 PDF 入库（约 5 min）
- `cp -X "/Users/Zhuanz/Downloads/20260417-C919反推控制逻辑需求文档.pdf" uploads/`
- `shasum -a 256 uploads/*.pdf` 验证
- 单 commit: `feat(P38-01): c919-etras requirement PDF landed in uploads/`

### P38-02 · W2-W5 联动更新（约 40 min）
- YAML head SHA 固化 + 10 pages typo 修
- Matrix Appendix A 3 项 resolution
- Registry row 5 notes 更新
- Intake packet PDF SourceDocumentRef notes 末尾增补
- 单 commit: `docs(P38-02): TRCU sign-off resolved + PDF provenance anchors updated (4 files联动)`

### P38-03 · 三轨（约 20 min）
- default 762 / e2e 49 / adversarial 1 · 期望零 delta
- 无单独 commit

### P38-05 · 收口（约 40 min）
- ROADMAP + STATE + closure doc + Notion DECISION
- 单 commit: `docs(P38-05): closure — awaiting GATE-P38-CLOSURE`

**总 3-4 commits · 1.5-2h。**

---

## 7. Exit Criteria

- `uploads/20260417-C919反推控制逻辑需求文档.pdf` 入库 · SHA 匹配
- `config/hardware/c919_etras_hardware_v1.yaml` head 加 SHA256 字段 + 10 pages typo 修
- `docs/c919_etras/traceability_matrix.md` Appendix A 3 项 "Pending TRCU-team sign-off" → "✅ TRCU signed via Kogami 明示"
- `docs/provenance/adapter_truth_levels.md` row 5 notes 更新（其他 4 行字节级不变）
- `src/well_harness/adapters/c919_etras_intake_packet.py` PDF notes 末尾增补
- 三轨回归 default 762 / e2e 49 / adversarial 1 · 零 delta
- ROADMAP + STATE 更新 · closure drafted
- Notion DECISION append (Pending)
- Branch `codex/p38-c919-etras-provenance-closure` 3-4 commits pushed

---

## 8. 风险与回滚

| 风险 | 概率 | 影响 | 缓解/回滚 |
|------|------|------|----------|
| PDF cp 后 SHA 不匹配 | 低 | 阻塞 | cp -X 剥 xattr；二次 shasum 校；失败 STOP 报 Kogami |
| YAML head 注释破坏 parse | 低 | 中 | commit 前 `yaml.safe_load` 验证 |
| c919 test (63 tests) 有隐藏对 SHA 字段的断言 | 极低 | 中 | 提前 grep 确认 test 不引用 YAML head 字段；三轨跑完复查 |
| matrix Appendix A 3 项文字大改触发 P35-03 banner test | 极低 | 小 | banner test 不扫 c919 matrix · 不影响 |
| registry row 5 notes 字段 format 破坏表格 markdown | 低 | 小 | 保持 pipe 分隔符 · 局部编辑后预览 |
| intake packet notes 字段长度超限 | 极低 | 小 | dataclass str 无长度限制 · 安全 |

**回滚：** `GATE-P38-CLOSURE` 不批时，`git revert` 回 db03294 main HEAD。

---

## 9. v5.2 红线合规预声明（plan 级）

- **R1 不可逆 main HEAD** — P38 commit 全走 `codex/p38-c919-etras-provenance-closure` 独立分支；non-FF merge (Option M) 等 `GATE-P38-CLOSURE: Approved`
- **R2 不自签 Gate** — P38-00 等 Kogami `GATE-P38-PLAN: Approved`（Q1/Q2）；P38-05 等 `GATE-P38-CLOSURE: Approved`
- **R3 Tier 1 adversarial** — §4 已写 4 条反驳（C1-C4）+ 就地缓解
- **R4 不自选下一 Phase 方向** — P38 由 Kogami 2026-04-20 三条并发指令明示发起（PDF 路径 + TRCU sign-off + 继续推进）；下一 Phase（P40 CI SHA · P41 workbench spec · 其他）由 Kogami 在 P38 closeout 后再明示
- **R5 证迹先行** — 本 Phase 是证迹先行第四轮（c919 对称闭环）；TRCU sign-off 透明标注 "由 Kogami 2026-04-20 明示接纳" · 不假装 TRCU 团队有文件化签字

---

## 10. 停点

**本 plan 不执行任何动作。等 `GATE-P38-PLAN: Approved` + Q1/Q2 仲裁。**

收到签字后 Executor：
1. P38-01 W1 PDF 入库
2. P38-02 W2-W5 联动
3. P38-03 三轨
4. P38-05 closure + ROADMAP + STATE + Notion DECISION (Pending)
5. push · 等 `GATE-P38-CLOSURE: Approved`

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P38-PLAN: Approved` (Kogami) + Q1/Q2 仲裁

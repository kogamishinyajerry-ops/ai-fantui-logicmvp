---
phase: P40
plan: P40-00
title: CI-level SHA enforcement — 自动校验 uploads/ provenance hash
status: drafted · Awaiting GATE-P40-PLAN (Kogami)
date: 2026-04-20
owner: Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed
supersedes: —
preconditions:
  - GATE-P38-CLOSURE Approved (Kogami 2026-04-20) → origin/main at 74a459a
  - Kogami 2026-04-20 directive "继续推进" 选 P40 作下一方向
  - Kogami 2026-04-20 "Q1-Q3 由你推荐决定" 授权 Executor 预签 Open Questions
  - uploads/ 当前 2 文件（thrust-reverser docx SHA `6e457fe3…276133a5` / c919-etras PDF SHA `dbe3f76b…276133a5`）已入库，各有多处 SHA 引用散布 code+docs
non-goals:
  - 改 controller.py / models.py / adapter.py 任何一行
  - 改 YAML parameters 段任何 value
  - 改既有测试断言
  - 改 5 adapter 任何 SourceDocumentRef 内容或结构
  - 改 traceability matrix / supplement / registry 任何 SHA 文字（本 Phase 只校验，不改源头 SHA 字符串）
  - 建 GitHub Actions workflow（Q1=A 选 pytest lane · runtime CI infra 留未来 Phase）
  - 改 Notion DECISION 历史（只 append P40 新 DECISION 块）
---

# P40-00 Plan · CI-level SHA enforcement — 自动校验 uploads/ provenance hash

## 0. TL;DR

按 Kogami 2026-04-20 "继续推进" + 选 P40 作下一方向 + "Q1-Q3 由你推荐决定" 授权，P40 建立 **自动 SHA 校验** 机制，闭合 P34/P36β/P37/P38 counterargument 中反复提到的"SHA 副本靠人工维护 · CI 无校验 · 未来 tamper 未必发现"风险（C2/C3 类）。

**核心设计（Q1-Q3 Executor 预签）：**
- **Q1 = A · pytest default lane 集成**（最简路径 · 与既有 762 test 体系一致 · 零新 CI infra）
- **Q2 = A · YAML 格式 SHA registry**（`docs/provenance/sha_registry.yaml` · 与 hardware config 格式一致）
- **Q3 = A · 硬失败 exit 1**（SHA mismatch 是 provenance 污染 hard signal · 不应柔性）

**核心产出：**
- `docs/provenance/sha_registry.yaml` (~40 行) · 2 文件初始条目 · SHA/size/references 单一来源
- `scripts/verify_provenance_hashes.py` (~150 行) · 读 registry + 实际 uploads/ 文件 + 对账
- `tests/test_provenance_sha_integrity.py` (~50 行) · pytest 包装，default lane 自动跑

**预计规模：**
- W1-W2: SoT registry + verify script · 约 1h
- W3: pytest 集成 · 约 15 min
- W4: 回扫初始化 + 三轨 · 约 30 min
- W5: 收口 · 约 40 min
- **总 2-2.5h · 3-4 commits · default lane 从 762 → ~765**

---

## 1. 上下文

### 1.1 当前 SHA 副本风险图

`uploads/` 入库 2 文件，各有多处 SHA 引用：

**thrust-reverser docx (`6e457fe3…276133a5`, 230930 bytes)：**
1. `config/hardware/thrust_reverser_hardware_v1.yaml` line 24 (full 64-char)
2. `docs/thrust_reverser/traceability_matrix.md` line 11 (shortened `6e457fe3…276133a5`) + line 195 (full)
3. `docs/thrust_reverser/requirements_supplement.md` line 218 (full)
4. `docs/provenance/adapter_truth_levels.md` row 1 (shortened)
5. `src/well_harness/adapters/thrust_reverser_intake_packet.py` PDF ref notes (full, via P36β-02)

**c919-etras PDF (`dbe3f76b…276133a5`, 1013541 bytes)：**
1. `config/hardware/c919_etras_hardware_v1.yaml` line 6 (full, via P38-02)
2. `docs/c919_etras/traceability_matrix.md` (full, P34 original) + (shortened)
3. `docs/provenance/adapter_truth_levels.md` row 5 (shortened)
4. `src/well_harness/adapters/c919_etras_intake_packet.py` PDF ref notes (full, via P38-02)
5. `.planning/STATE.md` (shortened) + ROADMAP (shortened) + closure docs (full)

**风险场景：**
- 某人替换 `uploads/20260409-...docx` 为不同版本 → 所有 SHA 引用都失效但无告警
- 某人只改一处 docs SHA 文字 → code 真相 vs docs 文字产生 drift
- CI 没有自动校验，回归测试全绿但证迹已污染
- "5 位置 SHA 副本" 看起来是冗余防护，其实是 5 个独立 drift 源

### 1.2 P40 的解决方案（SoT + Verifier + CI）

1. **单一来源（Single Source of Truth）：** `docs/provenance/sha_registry.yaml` 登记每个 `uploads/` 文件的权威 SHA / size / 引用位置
2. **验证器脚本（Verifier）：** `scripts/verify_provenance_hashes.py` 读 registry + 实际 uploads/ 计算 SHA 对账
3. **CI 集成：** `tests/test_provenance_sha_integrity.py` pytest wrapper · default lane 每跑必检

### 1.3 不在本 Phase scope 的问题

- `uploads/` 之外文件的 SHA 校验（本 Phase 只管 uploads/）
- 5 个散布位置的**文本完整性校验**（本 Phase 仅校验 uploads/ 实际文件 SHA 与 registry 一致 · 散布位置的 SHA 文字 drift 由人工在 Phase Plan/Closure review 时检查）
- GitHub Actions workflow 集成（pytest 集成已足够 · runtime CI infra 留未来 Phase）
- SHA 以外的签名机制（GPG / Ed25519）· 留未来 Phase

---

## 2. Scope — 5 工作包

### W1 · SHA registry 单一来源（P40-01 · 20 min）

新建 `docs/provenance/sha_registry.yaml`，示例格式：

```yaml
# SHA Registry for uploads/ provenance
# =======================================================================
# Single source of truth for SHA256 of every uploads/ file.
# Enforced by scripts/verify_provenance_hashes.py (via pytest default lane,
# tests/test_provenance_sha_integrity.py).
# Any new file added to uploads/ must also be registered here.

version: 1
updated: 2026-04-20
phase: P40

files:
  - path: uploads/20260409-thrust-reverser-control-logic.docx
    sha256: 6e457fe3c66e456d418f657975b7692453b30350b38fe91d0989e345276133a5
    size: 230930
    phase_landed: P36β
    authority: Kogami 内部自签（见 docs/thrust_reverser/requirements_supplement.md §7）
    references:  # informational; not strictly verified in P40
      - config/hardware/thrust_reverser_hardware_v1.yaml
      - docs/thrust_reverser/traceability_matrix.md
      - docs/thrust_reverser/requirements_supplement.md
      - docs/provenance/adapter_truth_levels.md
      - src/well_harness/adapters/thrust_reverser_intake_packet.py

  - path: uploads/20260417-C919反推控制逻辑需求文档.pdf
    sha256: dbe3f76b8ab0682e7ea41ab36a970ad4897c4bfc5461a60a8f0831d485631da5
    size: 1013541
    phase_landed: P38 (entry P34 / physical P38)
    authority: 甲方 (C919 TRCU 团队) · Kogami 代 TRCU 明示 sign-off
    references:
      - config/hardware/c919_etras_hardware_v1.yaml
      - docs/c919_etras/traceability_matrix.md
      - docs/provenance/adapter_truth_levels.md
      - src/well_harness/adapters/c919_etras_intake_packet.py
```

### W2 · Verifier 脚本（P40-02 · 45 min）

新建 `scripts/verify_provenance_hashes.py`，功能：

```
用法：
  PYTHONPATH=src python scripts/verify_provenance_hashes.py [--strict]

行为：
  1. 读 docs/provenance/sha_registry.yaml
  2. 列出 uploads/*（glob），对每个文件：
     a. 如果文件不在 registry → ERROR (missing registration)
     b. 如果 registry 中有 entry 但文件不存在 → ERROR (missing file)
     c. 计算 SHA256 + size，与 registry 对账 → mismatch ERROR
  3. ERROR 任何一个 → exit 1; 全绿 → exit 0
  4. --strict 额外验证 registry.references 中列出的文件都存在（防 rename 漂移）

依赖：仅标准库 (hashlib, yaml via pyyaml 已在项目依赖中)
```

架构：
- `load_registry(path: Path) -> dict`
- `discover_uploads(uploads_dir: Path) -> list[Path]`
- `verify_file(file_path: Path, expected: dict) -> list[str]`（返回 errors list）
- `verify_registry_coverage(registry, discovered) -> list[str]`
- `main()`：聚合 errors，打印，exit code

### W3 · pytest 集成（P40-03 · 15 min）

新建 `tests/test_provenance_sha_integrity.py`：

```python
"""
P40-03 · Provenance SHA Integrity Regression Guard.

Runs scripts/verify_provenance_hashes.py as part of pytest default lane.
Any drift in uploads/ vs registry produces immediate test failure.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_verify_provenance_hashes_exits_clean() -> None:
    script = REPO_ROOT / "scripts" / "verify_provenance_hashes.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"verify_provenance_hashes.py exited {result.returncode}.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


def test_sha_registry_yaml_parses() -> None:
    import yaml
    registry_path = REPO_ROOT / "docs" / "provenance" / "sha_registry.yaml"
    assert registry_path.exists()
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert len(data["files"]) >= 2  # minimum 2 files at P40 landing


def test_all_uploads_registered() -> None:
    """Any file in uploads/ must appear in registry."""
    import yaml
    registry_path = REPO_ROOT / "docs" / "provenance" / "sha_registry.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registered_paths = {f["path"] for f in data["files"]}

    uploads_dir = REPO_ROOT / "uploads"
    actual_files = {
        str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        for p in uploads_dir.iterdir()
        if p.is_file()
    }

    missing = actual_files - registered_paths
    assert not missing, f"Unregistered files in uploads/: {missing}"
```

### W4 · 回扫初始化 + 三轨（P40-04 · 30 min）

- 运行 `scripts/verify_provenance_hashes.py` 确认 2 文件 SHA 全绿
- 三轨回归：期望 **default 765 passed (762 + 3 new)** · e2e 49 identical · adversarial 1 identical

### W5 · 收口（P40-05 · 40 min）

- `.planning/ROADMAP.md` 追加 P40 段
- `.planning/STATE.md` 更新
- `.planning/phases/P40-ci-sha-enforcement/P40-05-CLOSURE.md` 新建
- Notion DECISION append (Pending) · push

---

## 3. Non-goals — 严格禁止

已在 frontmatter 明列。强调：
- **不**改 controller.py / models.py / adapter.py / YAML parameters / 既有 test 断言
- **不**改 uploads/ 任何文件内容（仅 verify）
- **不**改散布在 code/docs 的 SHA 文字（W2 strict 模式可选加 reference 存在性校验，但不校验 SHA 文字一致）
- **不**建 GitHub Actions（Q1=A pytest lane 集成已足）
- **不**引入新的外部依赖（pyyaml 已有）

---

## 4. Tier 1 对抗性自审（≥3 条，交付 4 条）

### C1 · "pytest 集成 vs GitHub Actions · pytest 只在本地/CI 跑，不如 GitHub Actions 细粒度强制"

**承认部分差异。** 缓解：
1. 本项目当前有 GitHub Actions workflow（见 .github/workflows/）——如果 workflow 跑 pytest，则 pytest 集成就是 Actions 集成。非独立 CI 步骤。
2. Pytest 集成与 762 既有 test 同 lane · 开发者本地跑测试就捕获 SHA drift · 不依赖 push 远端触发
3. 如果未来需要独立 `.github/workflows/provenance-check.yml`，独立 Phase 扩（P41+ 候选）
4. pytest 集成足以闭合 "CI 无校验" 风险

### C2 · "registry references 字段是 informational · 散布 docs/code 的 SHA 文字 drift 仍可能漏掉"

**承认。** 缓解：
1. `references` 字段登记**哪些文件应含 SHA 引用**（防止新增 reference 时漏登）
2. strict 模式 (W2 --strict) 校验 references 文件存在（防 rename/delete 漂移）
3. 散布位置 SHA 文字一致性校验**本 Phase 不做** —— Rationale: 散布位置 SHA 文字差异（short-form vs full）难机械 verify；审计由 Phase Plan/Closure review 时人工检查 · registry 保证 uploads/ 实际 SHA 就是 truth 位置
4. 未来若需扩展 reference 文字 grep 校验，独立 Phase（P41+）

### C3 · "初始 registry SHA 从哪来？信任 cowork P34 + P36β/P38 入库时的值？"

**承认有初始化信任链。** 缓解：
1. W4 执行前先手工跑 `shasum -a 256 uploads/*` 得到权威 SHA，与已有 docs/code 中的 SHA 对账
2. thrust-reverser docx SHA `6e457fe3…` 是 P36β-01 时 Executor 本地 shasum 计算得出（已验）
3. c919-etras PDF SHA `dbe3f76b…` 是 P38-01 时 Executor 本地 shasum 计算得出（已验）· 且与 cowork P34 时期记录完全一致（双重 cross-check）
4. registry 固化这些已验 SHA 作为权威 · 任何未来 drift 可查回 registry history

### C4 · "P40 引入了 pyyaml 依赖 · 虽然已在 pyproject.toml 但 verify script 失败时怎么办"

**承认需确认依赖可用。** 缓解：
1. 本地跑 `PYTHONPATH=src python -c "import yaml"` 验证（已知项目 YAML parse 大量使用）
2. 如果 yaml 不可用，fallback 用 JSON 实现（hashlib 是 stdlib · JSON 是 stdlib）
3. W4 初始化测试包括 import 验证
4. verify script 可包裹 `try: import yaml except ImportError: sys.exit(1, "pyyaml missing")` 清晰错误消息

---

## 5. Open Questions — Kogami 2026-04-20 已授权 Executor 预签

| Q | 选项 | Executor 推荐 | 理由 |
|---|------|---------------|------|
| Q1 · CI 集成点 | A pytest default lane / B GitHub Actions / C both | **A** | 最简路径 · 与既有 762 test 体系一致 · 零新 infra |
| Q2 · registry 格式 | A YAML / B JSON / C markdown | **A** | 与 hardware config 格式一致 · 人类可读 |
| Q3 · 失败退出码 | A 硬失败 exit 1 / B warning only | **A** | SHA mismatch 是 hard signal，不应柔性 |

**Kogami 2026-04-20 指令：** "Q1-Q3 由你推荐决定"· Executor 固化 Q1=A / Q2=A / Q3=A。若 Kogami 在 Gate 签时有调整可 override。

---

## 6. Sub-phase 分解

### P40-00 · Plan (本文档 · 等 Kogami 签 GATE-P40-PLAN)

### P40-01 · W1 SHA registry yaml（约 20 min）
- 新建 `docs/provenance/sha_registry.yaml` · ~40 行 · 2 文件初始条目
- 本地 `yaml.safe_load` 验证 parse 清洁
- 单 commit: `feat(P40-01): SHA registry yaml — single source of truth for uploads/`

### P40-02 · W2 Verifier 脚本（约 45 min）
- 新建 `scripts/verify_provenance_hashes.py` · ~150 行
- 本地跑 verify → 期望 exit 0
- 单 commit: `feat(P40-02): verify_provenance_hashes.py — CI-level SHA enforcement script`

### P40-03 · W3 pytest 集成（约 15 min）
- 新建 `tests/test_provenance_sha_integrity.py` · ~50 行 · 3 tests
- 本地 `PYTHONPATH=src pytest tests/test_provenance_sha_integrity.py -v` → 期望 3 passed
- 单 commit: `test(P40-03): provenance SHA integrity regression guard`

### P40-04 · 三轨（约 20 min）
- default: 期望 **765 passed** (762 + 3)
- e2e: 49 identical
- adversarial: 1 identical
- 无单独 commit

### P40-05 · 收口（约 40 min）
- ROADMAP + STATE + closure doc + Notion DECISION
- 单 commit: `docs(P40-05): closure — awaiting GATE-P40-CLOSURE`

**总 4 commits · 2-2.5h · default lane 净增 3 tests。**

---

## 7. Exit Criteria

- `docs/provenance/sha_registry.yaml` 存在 · 2 文件条目 · yaml.safe_load 清洁
- `scripts/verify_provenance_hashes.py` 存在 · 本地 exit 0
- `tests/test_provenance_sha_integrity.py` 存在 · 3 tests 本地通过
- 三轨: default **765 passed** / e2e 49 identical / adversarial 1 identical
- ROADMAP + STATE 更新 · closure drafted
- Notion DECISION append (Pending)
- Branch `codex/p40-ci-sha-enforcement` 4 commits pushed

---

## 8. 风险与回滚

| 风险 | 概率 | 影响 | 缓解/回滚 |
|------|------|------|----------|
| pyyaml 依赖不可用 | 极低 | 阻塞 | W4 前先 import 验证 · fallback JSON 备选 |
| verify script 边界 case bug（如空 uploads/ / 中文路径）| 低 | 小 | W2 写 3 个 test case 测覆盖边界 |
| 新增 3 tests 有 flakiness | 低 | 小 | 纯文件操作 · 无网络 · 无并发 · 稳 |
| registry 格式未来扩展需 migration | 中 | 小 | `version: 1` 字段已留扩展点 · schema v2 新加字段不破 v1 |
| 初始 SHA 记录错误 | 极低 | 中 | W4 前手工 `shasum -a 256` 双重校 · 记录匹配验证 |

**回滚：** `GATE-P40-CLOSURE` 不批时，`git revert` 回 `74a459a` main HEAD。P40 branch 保留作审计存证。

---

## 9. v5.2 红线合规预声明（plan 级）

- **R1 不可逆 main HEAD** — P40 commit 全走独立分支；non-FF merge (Option M) 等 `GATE-P40-CLOSURE: Approved`
- **R2 不自签 Gate** — P40-00 等 `GATE-P40-PLAN: Approved`（Kogami 已授权 Q1-Q3 Executor 预签）；P40-05 等 `GATE-P40-CLOSURE: Approved`
- **R3 Tier 1 adversarial** — §4 已写 4 条 counter（C1-C4）+ 缓解
- **R4 不自选下一 Phase 方向** — P40 由 Kogami 2026-04-20 明示选（复制 Executor 推荐文字作 directive）；下一 Phase（P41 workbench spec · P42 runtime API · 其他）由 Kogami 在 P40 closeout 后明示
- **R5 证迹先行** — 本 Phase 是证迹先行第五轮（CI 层防 tamper · 闭合历史 counter C2/C3 留的基础设施债）

---

## 10. 停点

**本 plan 不执行任何动作。等 `GATE-P40-PLAN: Approved`。**

收到签字后 Executor：
1. P40-01 W1 registry yaml
2. P40-02 W2 verify script
3. P40-03 W3 pytest wrapper
4. P40-04 三轨
5. P40-05 closure + ROADMAP + STATE + Notion DECISION (Pending)
6. push · 等 `GATE-P40-CLOSURE: Approved`

---

**Signed:** Claude App Opus 4.7 (Solo Executor) · v5.2 solo-signed · 2026-04-20
**Awaiting:** `GATE-P40-PLAN: Approved` (Kogami)

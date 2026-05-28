# Multi-Agent Engineering Deliverable Plan For Project Manager

Date: 2026-05-21
Status: project-initiation deliverable plan; current MVP focus reset to old `demo.html` cockpit reproduction
Scope: Multi-Agent Control Logic Engineering System MVP, with `demo.html` digital-twin cockpit as the first product-grade golden sample

## 给项目总管的原话

这个项目还没有正式立项，不能让团队一直等最终成品。当前应该先交付一个阶段性可验收包：它不承诺替代 Simulink，也不承诺认证级控制逻辑，而是先稳定复刻老版 `demo.html` 数字孪生反推控制台，并用多 agent 工程链路把这个 golden sample 变成可运行、可审查、可回归的 MVP。第一阶段性里程碑必须用施工队工时管理，不使用自然日估算；每一批工时都要落到可验证交付物、命令和证据包上。

## 工时单位

- 估算单位：施工队工时。
- 施工队：主实现 agent、只读审查 agent、确定性 gate、人工批准闸门的协同工作单元。
- 管理原则：不等最终成品；每个阶段都必须产出阶段性可验收包。

## 里程碑施工表

| 编号 | 阶段性成果 | 工时预算 | 退出条件 |
| --- | --- | --- | --- |
| M0 | 多 agent 工程链路基座冻结 | 0 施工队工时 | 当前 repo-local gate 已有证据，不重复施工 |
| M1 | 可审查自动开发闭环样板 | 18 施工队工时 | queue expansion contract、三类 approved slice、review export、local gate 全部可机读验证 |
| M2 | Requirement to IR 最小产品演示包 | 36 施工队工时 | 一段发动机启动需求能生成结构化需求、IR、finding、repair task、review packet |
| M3 | Safety/Evidence 工程价值增强包 | 48 施工队工时 | 至少新增两类 Safety finding 和两类 Evidence finding 的确定性修复闭环 |
| M4 | 外部审查交付包 | 32 施工队工时 | CI artifact、审查报告、回归命令、残余风险列表可由外部审查系统读取 |
| M5 | 长时间开工控制面 | 40 施工队工时 | M1-M4、approved queue、readiness、失败恢复和审查停机条件通过单一入口可回归 |
| M6 | 队列扩展模板 | 32 施工队工时 | Safety/Evidence/Requirement 三类新任务可按 append-only v0.2 模板追加 |
| M7 | 首个 v0.2 真实队列项 | 34 施工队工时 | Requirement finding 通过 v0.2 queue item、approved shell、repair loop、review export 收敛 |
| M8 | 快速施工 gate 拆分 | 30 施工队工时 | 每个后续 slice 可先跑轻量 fast gate；full pytest/GSD 保留为里程碑门 |
| M9 | 第二个 append-only 队列项 | 28 施工队工时 | Safety undefined-signal finding 通过 M8 fast gate、approved shell、repair loop、review export 收敛 |
| M10 | 队列执行调度 ledger | 30 施工队工时 | approved queue v0.3 经过 scheduler selection 生成可审计 run ledger，记录每个 run 的 preflight、approved shell、repair、review export |
| M11 | 队列 cursor / resume state | 28 施工队工时 | M10 run ledger 生成 cursor state，标记 5/5 converged，进入 idle_no_open_approved_items |
| M12 | ready-to-resume cursor 样板 | 26 施工队工时 | append-only open approved record 进入 cursor，选择 RUN-QUEUE-006 并标记 ready_to_resume |
| M13 | demo.html 复刻 MVP golden gate | 18 施工队工时 | 老 `demo.html` 控制台作为 golden reference，`/demo-reconstruction` 通过 20 节点、23 连线、5 预设、6 状态输出和本地路由回归 |
| M14 | demo.html 复刻浏览器验收 | 24 施工队工时 | `/demo-reconstruction` 成为主 MVP 控制台，Playwright 截图、像素可见性、预设交互、HUD/输出联动全部通过 |
| M15 | v0.4 resume 队列执行 | 22 施工队工时 | `RUN-QUEUE-006` 通过 fast gate、approved shell、Evidence repair loop 和 review export 收敛 |

## 当前第一阶段可演示包

项目总管当前最应该先看到的不是多 agent 内部结构，而是一个可以稳定打开、可以截图验收、可以重复回归的产品化 MVP：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| D1 | `demo.html` 复刻 MVP 控制台 | 6 施工队工时 | `/demo-reconstruction` 首屏入口、`demo.html 复刻 MVP 控制台` |
| D2 | golden contract deterministic gate | 6 施工队工时 | `make demo-html-reconstruction-mvp` 验证 20/20 节点、23/23 连线、5 个预设、6 类状态输出 |
| D3 | browser acceptance evidence | 6 施工队工时 | `make demo-html-reconstruction-browser-acceptance` 生成截图、像素可见性、预设交互和 HUD/输出联动证据 |
| D4 | external review package | 4 施工队工时 | `make phase1-demo-mvp-review-package` 生成 `phase1_demo_mvp_review_package_v0_1.json` 和 `phase1_demo_mvp_review_report.md` |

这个可演示包的产品入口固定为 `/demo-reconstruction`。它是当前对外阶段性成果；后续 M1-M12 的多 agent 队列、approved shell、repair loop 和 evidence packet 是施工队继续长期开发的工程支撑，不应该抢占第一演示入口。

## M1 交付物

M1 的目标不是最终成品，而是第一份阶段性可验收包：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | queue expansion contract | 4 施工队工时 | `docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json` |
| S2 | expansion contract checker | 4 施工队工时 | `scripts/verify_approved_candidate_task_queue_expansion_contract.py` |
| S3 | approved queue artifact checker | 3 施工队工时 | `make verify-approved-candidate-task-queue-artifact` |
| S4 | M1 external review package | 5 施工队工时 | `make multi-agent-m1-review-package` |
| S5 | GSD blocking validation | 2 施工队工时 | `tools/run_gsd_validation_suite.py --format json --skip notion_control_plane` |

## M1 验收口径

M1 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_expansion_contract.py tests/test_multi_agent_deliverable_plan.py
make verify-approved-candidate-task-queue-expansion-contract
make verify-approved-candidate-task-queue-artifact
make multi-agent-m1-review-package
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M1 不包含：

- 认证级结论
- controller truth 修改
- UI layout polish
- 完整替代 Simulink
- 未批准 task 的自动执行

## 给下一轮施工的 /goal

```text
/goal Objective:
Deliver M1 可审查自动开发闭环样板 for Multi-Agent Control Logic Engineering System in /Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/multi-agent-active-route-wiring.

Scope:
- Change only multi-agent contract, checker, fixture, coordination docs, Makefile, CI workflow, and focused tests.
- Preserve approved-candidate-task-queue-v0.1 as the fixed external review artifact.
- Add only append-only queue expansion controls for future approved task types.

Constraints:
- Do not modify src/well_harness/controller.py.
- Do not modify src/well_harness/editable_control_model.py.
- Do not modify src/well_harness/static/requirements_intake/*.
- Do not claim certification, DAL readiness, production readiness, or trusted control-law promotion.
- Use施工队工时 as planning unit; do not estimate by calendar date.

Done when:
1. docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json exists and validates its fixture.
2. scripts/verify_approved_candidate_task_queue_expansion_contract.py exits 0 with status=pass.
3. make verify-approved-candidate-task-queue-expansion-contract exits 0.
4. make verify-approved-candidate-task-queue-artifact exits 0.
5. make multi-agent-m1-review-package exits 0 and writes multi_agent_m1_review_package_v0_1.json.
6. make test exits 0.
7. PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane exits 0.
8. git diff --check exits 0.

Stop if:
- git status shows changes to src/well_harness/controller.py.
- git status shows changes to src/well_harness/editable_control_model.py.
- git status shows changes under src/well_harness/static/requirements_intake/.
- Any checker can pass after weakening approved_candidate_task_queue_summary_v0_1.
- Any M1 claim depends on an unapproved task execution.
```

## M2 交付物

M2 的目标是拿到第一条 Requirement -> IR 的产品演示链路，不是扩大到完整发动机控制系统：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | engine-start source requirement fixture | 6 施工队工时 | `source_requirement.fixture_id=engine-start-control-requirement-v0.1` |
| S2 | deterministic structured requirements | 7 施工队工时 | `REQ-START-001`、`REQ-START-002`、`REQ-SAFE-001`、`REQ-SAFE-002` |
| S3 | candidate Logic IR packet | 8 施工队工时 | `ENG_START_CTRL_M2` with 6 states and 5 transitions |
| S4 | Safety finding and approved repair task | 7 施工队工时 | `TASK-CE-CHECK-SAFETY-PRIORITY-001` through approved execution shell |
| S5 | M2 review export and checker | 8 施工队工时 | `make multi-agent-m2-requirement-to-ir-demo` |

## M2 验收口径

M2 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m2_requirement_to_ir_demo.py
make multi-agent-m2-requirement-to-ir-demo
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M2 不包含：

- 完整发动机启动控制产品
- 自由文本 LLM 自动泛化
- controller truth 修改
- UI layout polish
- 认证级结论

## M3 交付物

M3 的目标是把 Safety Guardian / Evidence Agent 从“结构接入”推进到“有工程价值的确定性 finding 闭环”：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | Safety priority repair slice | 8 施工队工时 | `CHECK_SAFETY_PRIORITY_001` -> `TASK-CE-CHECK-SAFETY-PRIORITY-001` -> converged |
| S2 | Safety undefined-signal repair slice | 10 施工队工时 | `CHECK_UNDEFINED_SIGNAL_001` -> `TASK-CE-CHECK-UNDEFINED-SIGNAL-001` -> converged |
| S3 | Evidence failed-result repair slice | 10 施工队工时 | `EV_SIMULATION_RESULT_FAILED` -> `TASK-CE-EV-SIMULATION-RESULT-FAILED` -> converged |
| S4 | Evidence missing-result repair slice | 10 施工队工时 | `EV_TEST_RESULT_MISSING` -> `TASK-CE-EV-TEST-RESULT-MISSING` -> converged |
| S5 | M3 value-pack schema/checker/CI artifact | 10 施工队工时 | `make multi-agent-m3-safety-evidence-value-pack` |

## M3 验收口径

M3 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_repair_loop.py tests/test_multi_agent_m3_safety_evidence_value_pack.py
make multi-agent-m3-safety-evidence-value-pack
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M3 不包含：

- 新的 controller truth 行为
- UI layout polish
- 认证级结论
- 未批准 task 的自动执行
- 任意 finding 的自由泛化修复

## M4 交付物

M4 的目标是把 M1/M2/M3 从“内部 gate 已通过”整理成外部审查系统和项目总管都能直接读取的交付包：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | M1/M2/M3 child package collector | 8 施工队工时 | `child_packages.m1_review_package`、`child_packages.m2_requirement_to_ir_demo`、`child_packages.m3_safety_evidence_value_pack` |
| S2 | M4 machine-readable handoff schema | 6 施工队工时 | `docs/json_schema/multi_agent_m4_external_review_handoff_v0_1.schema.json` |
| S3 | M4 verifier and Make gate | 6 施工队工时 | `make multi-agent-m4-external-review-handoff` |
| S4 | Residual risk register | 5 施工队工时 | `residual_risks` with zero blocking risks |
| S5 | Human-readable review report and CI artifact | 7 施工队工时 | `external_review_handoff_report.md` and CI upload `multi-agent-m4-external-review-handoff` |

## M4 验收口径

M4 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m4_external_review_handoff.py
make multi-agent-m4-external-review-handoff
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M4 不包含：

- controller truth 修改
- UI layout polish
- 认证级结论
- 外部规划/GitHub 权限自动写入
- 对 M1/M2/M3 子包的语义放宽

## M5 交付物

M5 的目标是让多 agent 施工队可以长时间开工，但仍然只通过 approved task、受限执行 shell、确定性 gate 和人工审查停机条件推进：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | M1-M4 gate collector | 8 施工队工时 | `child_packages.m4_external_review_handoff` and `included_milestones=["M1","M2","M3","M4"]` |
| S2 | approved queue state snapshot | 8 施工队工时 | `queue_snapshot.task_count=3` and `queue_snapshot.converged=3` |
| S3 | M5 machine-readable control-plane schema | 7 施工队工时 | `docs/json_schema/multi_agent_m5_construction_control_plane_v0_1.schema.json` |
| S4 | failure recovery runbook | 7 施工队工时 | `construction_control_plane_runbook.md` with `FR-*` recovery entries |
| S5 | phase review stop conditions | 6 施工队工时 | `STOP-CONTROLLER-TRUTH-DIFF`、`STOP-UI-LAYOUT-DIFF`、`STOP-DETERMINISTIC-GATE-FAIL` |
| S6 | M5 Make/CI entrypoint | 4 施工队工时 | `make multi-agent-construction-control-plane` and CI upload `multi-agent-m5-construction-control-plane` |

## M5 验收口径

M5 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m5_construction_control_plane.py
make multi-agent-construction-control-plane
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M5 不包含：

- controller truth 修改
- UI layout polish
- 自动合并或自批准
- 认证级结论
- 绕过 approved-task shell 的自由执行
- 外部规划/GitHub 权限自动写入

## M6 交付物

M6 的目标是让下一批真实开发 slice 不再复制粘贴三个固定样板，而是通过一个固定的 approved queue item template 追加到 `approved-candidate-task-queue-v0.2`：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | queue item template schema | 7 施工队工时 | `docs/json_schema/multi_agent_m6_queue_extension_template_v0_1.schema.json` |
| S2 | Safety/Evidence/Requirement route matrix | 7 施工队工时 | `task_class_matrix` includes `SafetyRepairTask`、`EvidenceRepairTask`、`RequirementRepairTask` |
| S3 | append-only queue controls | 5 施工队工时 | `append_only_controls.next_queue_id=approved-candidate-task-queue-v0.2` |
| S4 | M6 runner/checker and Make gate | 6 施工队工时 | `make multi-agent-queue-extension-template` |
| S5 | operator template guide and CI artifact | 4 施工队工时 | `queue_extension_template_guide.md` and CI upload `multi-agent-m6-queue-extension-template` |
| S6 | contract regression tests | 3 施工队工时 | `tests/test_multi_agent_m6_queue_extension_template.py` |

## M6 验收口径

M6 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m6_queue_extension_template.py tests/test_agent_task_contract.py tests/test_multi_agent_deliverable_plan.py
make multi-agent-queue-extension-template
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M6 不包含：

- 新增真实 v0.2 队列任务执行
- 修改 v0.1 queue summary 语义
- controller truth 修改
- UI layout polish
- 认证级结论
- 绕过 M5 construction control plane

## M7 交付物

M7 的目标是把 M6 的模板变成第一个真实 append-only v0.2 queue item。它选择 `REQ_AMBIGUITY_UNRESOLVED`，让 RequirementRepairTask 走与 Safety/Evidence 相同的 approved-task shell、candidate repair、deterministic gate、review export 路径：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | Requirement deterministic finding | 6 施工队工时 | `REQ_AMBIGUITY_UNRESOLVED` from `RequirementAnalystAgent` |
| S2 | Requirement repair loop | 8 施工队工时 | `RequirementRepairAgent` -> `repair_structured_requirement_candidate` -> converged |
| S3 | approved queue v0.2 schema/fixture | 7 施工队工时 | `approved_candidate_task_queue_summary_v0_2` preserves v0.1 prefix and appends one item |
| S4 | v0.2 runner/checker and Make gate | 7 施工队工时 | `make approved-candidate-task-queue-v0-2` and `make verify-approved-candidate-task-queue-v0-2-artifact` |
| S5 | CI artifact and contract regression | 6 施工队工时 | CI upload `approved-candidate-task-queue-v0-2` and `tests/test_approved_candidate_task_queue_v0_2.py` |

## M7 验收口径

M7 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_2.py tests/test_agent_task_contract.py tests/test_agent_repair_loop.py tests/test_agent_review_packet.py
make approved-candidate-task-queue-v0-2
make verify-approved-candidate-task-queue-v0-2-artifact
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M7 不包含：

- 第二个 v0.2 queue item
- 修改 v0.1 queue summary 语义
- controller truth 修改
- UI layout polish
- 认证级结论
- 让 RequirementRepairTask 自动写入真实需求源

## M8 交付物

M8 的目标是解决 M7 后暴露出的长 gate 压力：`unit_tests` 已经接近长回归预算，当前 GSD blocking validation 将预算稳定在 900 秒，不适合让每个小施工 slice 都先跑完整回归。M8 新增一个 fast construction gate，作为 approved task shell 的轻量前置门；它只验证 M1-M7 关键机器产物和边界，不替代 `make test` 或 GSD blocking validation。

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | M8 fast-gate schema/fixture | 6 施工队工时 | `multi_agent_m8_fast_construction_gate_v0_1` schema validates fixture |
| S2 | M8 runner/checker | 8 施工队工时 | `scripts/run_multi_agent_m8_fast_construction_gate.py` and checker converge |
| S3 | M7 queue fixture preflight reuse | 6 施工队工时 | `approved-candidate-task-queue-v0.2` runs with `AI_FANTUI_QUEUE_PREFLIGHT_MODE=fixture` |
| S4 | full pytest/GSD exclusion policy | 4 施工队工时 | checker rejects full pytest or GSD validation inside `fast_checks` |
| S5 | Make/CI/task-contract wiring | 4 施工队工时 | `make multi-agent-fast-construction-gate` and CI upload artifact |
| S6 | focused regression tests | 2 施工队工时 | `tests/test_multi_agent_m8_fast_construction_gate.py` |

## M8 验收口径

M8 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_m8_fast_construction_gate.py tests/test_agent_task_contract.py
make multi-agent-fast-construction-gate
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M8 不包含：

- 替代完整 pytest/GSD validation
- 新增第二个 v0.2 queue item
- 修改 controller truth
- UI layout polish
- 认证级结论
- 绕过 approved task shell 或人工批准状态字段

## M9 交付物

M9 的目标是证明 M8 fast gate 不是孤立 artifact，而是真的能作为后续 approved task slice 的施工前置门。它在 v0.2 四项 prefix 后追加 `queue-safety-undefined-signal-repair`，选择 `CHECK_UNDEFINED_SIGNAL_001`，让 SafetyRepairTask 通过 fast gate、approved shell、candidate repair、review export 和 artifact checker 收敛：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | v0.3 append-only schema/fixture | 6 施工队工时 | `approved_candidate_task_queue_summary_v0_3` preserves v0.2 prefix and appends one item |
| S2 | Safety undefined-signal slice | 6 施工队工时 | `CHECK_UNDEFINED_SIGNAL_001` -> `TASK-CE-CHECK-UNDEFINED-SIGNAL-001` -> converged |
| S3 | M8 fast-gate preflight binding | 5 施工队工时 | new item `readiness_command=make multi-agent-fast-construction-gate` |
| S4 | v0.3 runner/checker and Make gate | 6 施工队工时 | `make approved-candidate-task-queue-v0-3` and checker pass |
| S5 | CI artifact and focused regression | 5 施工队工时 | CI upload `approved-candidate-task-queue-v0-3` and `tests/test_approved_candidate_task_queue_v0_3.py` |

## M9 验收口径

M9 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_approved_candidate_task_queue_v0_3.py tests/test_agent_task_contract.py tests/test_agent_repair_loop.py
make approved-candidate-task-queue-v0-3
make verify-approved-candidate-task-queue-v0-3-artifact
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M9 不包含：

- 第三个 v0.3 追加项
- 修改 v0.2 queue prefix 语义
- controller truth 修改
- UI layout polish
- 认证级结论
- 绕过 M8 fast gate 或 approved task shell

## M10 交付物

M10 的目标是把 M9 的“最新 queue summary”推进成“可审计执行历史”。它不新增第三个队列项，而是在 v0.3 queue 之上生成 `multi_agent_queue_run_ledger_v0_1`，让外部审查系统可以按 run record 读取每个 approved slice 的 preflight、approved shell、repair convergence、review export 和边界状态：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | queue run ledger schema/fixture | 6 施工队工时 | `multi_agent_queue_run_ledger_v0_1` validates fixture and preserves v0.3 queue order |
| S2 | scheduler decision record | 5 施工队工时 | selected item `queue-safety-undefined-signal-repair` -> `RUN-QUEUE-005` |
| S3 | run ledger runner/checker | 8 施工队工时 | `make multi-agent-queue-run-ledger` and checker pass |
| S4 | negative checker path | 4 施工队工时 | unapproved run record is rejected by `verify_multi_agent_queue_run_ledger.py` |
| S5 | CI artifact and focused regression | 7 施工队工时 | CI upload `multi-agent-queue-run-ledger` and `tests/test_multi_agent_queue_run_ledger.py` |

## M10 验收口径

M10 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_run_ledger.py tests/test_agent_task_contract.py
make multi-agent-queue-run-ledger
make verify-multi-agent-queue-run-ledger
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M10 不包含：

- 新增第三个 v0.3 queue item
- 真实控制器写入
- UI layout polish
- 认证级结论
- 绕过 v0.3 queue checker 或 approved task shell

## M11 交付物

M11 的目标是在 M10 run ledger 之上建立可恢复施工 cursor。它不新增队列项、不执行新的控制器写入，而是把已收敛 run records 折叠为一个稳定 `multi_agent_queue_cursor_state_v0_1`，让后续长时间施工能确定性跳过已完成记录，并在没有 open approved item 时进入 idle 状态：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | queue cursor state schema/fixture | 6 施工队工时 | `multi_agent_queue_cursor_state_v0_1` validates fixture and records `idle_no_open_approved_items` |
| S2 | completed run cursor projection | 5 施工队工时 | `RUN-QUEUE-001` through `RUN-QUEUE-005` are marked `converged` in ledger order |
| S3 | cursor runner/checker | 7 施工队工时 | `make multi-agent-queue-cursor-state` and checker pass |
| S4 | negative checker path | 4 施工队工时 | false completed record status is rejected by `verify_multi_agent_queue_cursor_state.py` |
| S5 | CI artifact and focused regression | 6 施工队工时 | CI upload `multi-agent-queue-cursor-state` and `tests/test_multi_agent_queue_cursor_state.py` |

## M11 验收口径

M11 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_cursor_state.py tests/test_agent_task_contract.py tests/test_multi_agent_deliverable_plan.py
make multi-agent-queue-cursor-state
make verify-multi-agent-queue-cursor-state
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M11 不包含：

- 新增第三个 v0.3 queue item
- 跳过 M10 run ledger
- 真实控制器写入
- UI layout polish
- 认证级结论
- 在没有 approved open item 时伪造 resume task

## M12 交付物

M12 的目标是补齐 M11 没覆盖的另一半 resume 行为：当 source ledger 后面追加一个 approved open record 时，cursor gate 必须能确定性选择它，而不是继续停留在 idle。这个样板仍然是 candidate-only，不执行真实修复，只证明 Chief Engineer resume cursor 能从“已全部收敛”切到“可恢复执行”：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | ready-to-resume cursor fixture | 5 施工队工时 | `multi_agent_queue_cursor_state_ready_to_resume_v0_1` validates schema |
| S2 | resume-mode runner | 5 施工队工时 | `run_multi_agent_queue_cursor_state.py --resume-mode ready-to-resume` selects `RUN-QUEUE-006` |
| S3 | idle/ready dual-state checker | 6 施工队工时 | checker accepts idle and ready states through the same schema |
| S4 | negative selection checker | 4 施工队工时 | unselected approved open record is rejected |
| S5 | Make/CI/task contract wiring | 6 施工队工时 | `make multi-agent-queue-cursor-resume-state` is in local and CI gates |

## M12 验收口径

M12 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_queue_cursor_state.py tests/test_agent_task_contract.py tests/test_multi_agent_deliverable_plan.py
make multi-agent-queue-cursor-state
make multi-agent-queue-cursor-resume-state
make verify-multi-agent-queue-cursor-resume-state
make test
PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane
git diff --check
```

M12 不包含：

- 真实执行 `RUN-QUEUE-006`
- 新增控制器逻辑
- UI layout polish
- 认证级结论
- 将 open approved record 伪装成 converged record

## M13 交付物

M13 的目标是把施工队的当前主目标从继续扩展 agent 结构，收束到一个可验收的产品 MVP：稳定复刻老版 `demo.html` 数字孪生反推控制台。这里不重新设计 UI，不替换老 demo，而是把它设为 golden reference，并给 `/demo-reconstruction` 增加确定性回归 gate：

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | demo.html golden fixture/schema | 4 施工队工时 | `demo_html_reconstruction_mvp_v0_1` schema validates fixture |
| S2 | deterministic reconstruction checker | 6 施工队工时 | checker reads `demo.html#fan-chain-svg` and verifies 20 nodes / 23 wires |
| S3 | local route parity check | 3 施工队工时 | `/demo.html` and `/demo-reconstruction` both return HTTP 200 |
| S4 | Make/CI wiring | 3 施工队工时 | `make demo-html-reconstruction-mvp` runs locally and in CI |
| S5 | product-priority doc reset | 2 施工队工时 | MVP docs name `demo.html` cockpit as the first golden sample |

## M13 验收口径

M13 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_demo_html_reconstruction_mvp.py
make demo-html-reconstruction-mvp
git diff --check
git diff --name-only -- src/well_harness/controller.py src/well_harness/editable_control_model.py src/well_harness/static/requirements_intake
```

M13 不包含：

- 重写老版 `demo.html`
- 修改 controller truth
- 修改 requirements-intake UI layout
- 宣称认证级控制逻辑
- 把 `/demo-reconstruction` 伪装成已完成的最终产品

## M14 交付物

M14 的目标是把 M13 的机器契约推进到真实浏览器验收：`/demo-reconstruction` 不再是“原版 vs 当前复刻”的对照页，而是第一屏可演示的主 MVP 控制台。浏览器验收要证明截图可读、节点/连线像素可见、关键预设能驱动状态变化，并且 HUD 与输出卡片联动。

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | 主 MVP 控制台页面 | 5 施工队工时 | `data-ux-page-role="demo-mvp-console"` and `demo-reconstruction-console-frame` |
| S2 | 浏览器截图验收脚本 | 7 施工队工时 | `scripts/verify_demo_html_reconstruction_browser_acceptance.py` emits screenshots |
| S3 | 节点/连线像素可见性 | 4 施工队工时 | chain SVG screenshot reports `20` nodes / `23` wires and pixel status pass |
| S4 | 关键交互预设 | 4 施工队工时 | `max-reverse` and `inhibit-block` produce expected browser states |
| S5 | HUD/输出卡片联动 | 4 施工队工时 | `THR_LOCK RELEASED` matches `thr_lock ON`, inhibit keeps `thr_lock` not ON |

## M14 验收口径

M14 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_demo_html_reconstruction_mvp.py tests/test_requirements_intake_webui.py::test_demo_reconstruction_page_is_productized_main_mvp_console
PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/test_demo_html_reconstruction_mvp.py::test_demo_html_reconstruction_browser_acceptance_script_captures_interaction_evidence
make demo-html-reconstruction-mvp
make demo-html-reconstruction-browser-acceptance
git diff --check
git diff --name-only -- src/well_harness/controller.py src/well_harness/editable_control_model.py src/well_harness/static/requirements_intake
```

M14 不包含：

- 修改老版 `demo.html` 的控制逻辑
- 修改 controller truth
- 修改 requirements-intake UI layout
- 引入新的前端框架
- 宣称认证级控制逻辑

## M15 交付物

M15 的目标是补上 M12 明确排除的真实执行缺口：把 cursor 选中的 approved open record `RUN-QUEUE-006` 作为 append-only v0.4 queue item 执行。这个切片只修 evidence boundary-review candidate，不触碰控制器真相，也不把候选证据提升为认证结论。

| 编号 | 交付物 | 工时预算 | 验收证据 |
| --- | --- | --- | --- |
| S1 | Evidence boundary-review finding | 4 施工队工时 | `EV_BOUNDARY_RESULT_REVIEW_REQUIRED` is emitted for pass result without candidate-only boundary review |
| S2 | Evidence repair loop action | 5 施工队工时 | `TASK-CE-EV-BOUNDARY-REVIEW-001` records `reviewed_candidate_only` |
| S3 | append-only v0.4 runner/checker | 6 施工队工时 | `make approved-candidate-task-queue-v0-4` and checker pass |
| S4 | Make/CI wiring | 4 施工队工时 | CI runs and uploads `approved-candidate-task-queue-v0-4` |
| S5 | boundary regression | 3 施工队工时 | restricted diff guard stays empty for controller and requirements-intake UI paths |

## M15 验收口径

M15 只能在下面命令全部通过后声明完成：

```bash
PYTHONPATH=src:. python3 -m pytest -q tests/test_agent_repair_loop.py tests/test_approved_candidate_task_queue_v0_4.py
make approved-candidate-task-queue-v0-4
make verify-approved-candidate-task-queue-v0-4-artifact
git diff --check
git diff --name-only -- src/well_harness/controller.py src/well_harness/editable_control_model.py src/well_harness/static/requirements_intake
```

M15 不包含：

- controller truth 修改
- requirements-intake UI layout 修改
- 自动合并或自批准
- 认证级结论
- 对 v0.1 / v0.2 / v0.3 队列语义的重写

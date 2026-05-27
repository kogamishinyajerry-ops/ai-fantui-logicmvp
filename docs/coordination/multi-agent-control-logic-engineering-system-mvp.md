# Multi-Agent Control Logic Engineering System MVP

Date: 2026-05-27
Status: active-route contract, Chief Engineer task-package, dry-run planner, approved execution shell, Safety/Evidence/Requirement repair loops, candidate review packet, stable review-packet export, approved repair slices, external artifact checkers, versioned summary schemas, long-run readiness gate, approved candidate task queue, queue expansion contract, M1 deliverable plan, M1 external review package, M2 Requirement-to-IR demo package, M3 Safety/Evidence value pack, M4 external review handoff, M5 long-running construction control plane, M6 queue extension template, M7 append-only v0.2 queue item, M8 fast construction gate, M9 v0.3 fast-gated queue item, M10 queue run ledger, M11 queue cursor state, M12 ready-to-resume cursor sample, M13 demo.html reconstruction MVP golden gate, M14 browser MVP acceptance, M15 v0.4 resumed approved queue item, M16 v0.4 ledger/cursor closeout with compact-safe continuation checkpoint, M17 v0.5 unknown-requirement coverage repair queue item, M18 v0.6 unknown IR trace repair queue item, M19 v0.7 transition endpoint repair queue item, M20 v0.8 unreachable-state repair queue item, M22 read-only multi-agent operator cockpit package, M23 explicit pathspec packaging consolidation gate, M24 validation/PR preflight gate, M25 validation evidence capture gate, M26 v0.9 output-command-conflict repair queue item, and M27 v0.2 ledger/cursor promotion
Scope: active DeepSeek V4 Pro UI workbench route

## Goal

Define the first repo-bounded multi-agent engineering contract for AI FANTUI
LogicMVP without changing controller truth, adapters, public HTTP endpoints, or
CLI contracts.

The current product priority is narrower than the full multi-agent platform:
stabilize an MVP that can reliably reproduce the old `demo.html` digital-twin
reverse-logic cockpit. The old `demo.html` is the golden reference, and
`/demo-reconstruction` is the first reviewable replica surface.

The system principle is:

`AI does not directly produce trusted control logic. AI produces reviewable,
verifiable, traceable control-logic candidates; deterministic tools and human
gates decide what survives.`

## Active Route Mapping

| MVP responsibility | Agent | Current route surface | First deterministic evidence |
| --- | --- | --- | --- |
| Task decomposition and gate control | Chief Engineer Agent | `/logic-builder` candidate payload | `agent_task_contract_v0_1` task package |
| Requirement structuring | Requirement Analyst Agent | `/requirements-intake` | structured requirements and ambiguity list |
| Candidate logic generation | Logic IR Agent | `/logic-builder` | `agent_output_contract_v0_1.logic_ir` packet |
| Safety red-team review | Safety Guardian Agent | `/logic-builder` candidate payload | deterministic findings report |
| Test and simulation | Simulation/Test Agent | task package target | candidate test-oracle repair tasks |
| Traceability package | Evidence Agent | `/logic-builder` candidate payload | requirement -> IR -> test -> result matrix |
| Dry-run execution planning | Deterministic Executor Agent | `/logic-builder` candidate payload | `execution_plan_v0_1` boundary verdict |
| Approved restricted execution | Approved Task Execution Shell | `/logic-builder` candidate payload | `execution_evidence_package_v0_1` approval and gate evidence |
| Candidate Safety repair | Logic IR Repair Agent | focused contract helper | `ai-fantui-safety-repair-loop` convergence report |
| Candidate Evidence repair | Simulation/Test Repair Agent | focused contract helper | `ai-fantui-evidence-repair-loop` convergence report |
| Candidate review packet | Candidate Review Packet Agent | `/logic-builder` candidate payload | `candidate_review_packet_v0_1` finding -> approval -> repair -> convergence chains |
| External review export | Candidate Review Packet Export Agent | `/logic-builder/candidate-review-packet.json` | file-backed `candidate_review_packet_export_v0_1` envelope |
| Approved candidate repair slice | Chief Engineer + Logic IR Repair Agent | `make first-candidate-repair-slice` | task package -> approved execution shell -> candidate IR repair -> deterministic gate convergence |
| Approved Evidence repair slice | Chief Engineer + Simulation/Test Repair Agent | `make evidence-candidate-repair-slice` | Evidence finding -> approved execution shell -> candidate test-result repair -> deterministic gate convergence |
| Approved repair slices gate | Chief Engineer orchestration gate | `make approved-repair-slices` | Safety slice + Evidence slice + aggregate machine-readable summary |
| Approved repair artifact checker | External Review Artifact Checker | `make verify-approved-repair-slices-artifact` | aggregate summary + child review exports validated for CI/downstream review |
| Approved repair summary schema | External Review Artifact Contract | `approved_repair_slices_summary_v0_1` | versioned schema for the converged Safety + Evidence aggregate artifact |
| Multi-agent construction readiness | Chief Engineer Preflight Gate | `make multi-agent-construction-readiness` | single long-run preflight packet for route export, approved repair artifact, expansion contract, schema, and boundary status |
| Approved candidate task queue | Chief Engineer Queue Runner | `make approved-candidate-task-queue` | per-task readiness preflight -> approved-task shell -> candidate repair evidence |
| Approved candidate queue checker | External Review Artifact Checker | `make verify-approved-candidate-task-queue-artifact` | queue summary schema + three child review exports validated for CI/downstream review |
| Approved queue expansion contract | External Review Artifact Contract | `make verify-approved-candidate-task-queue-expansion-contract` | append-only v0.2 expansion rules without weakening fixed v0.1 summary |
| Milestone deliverable plan | Project Manager Package | `docs/coordination/multi-agent-deliverable-plan-for-project-manager.md` | M1 work-hour based deliverables and copy-paste project-manager message |
| M1 external review package | External Milestone Review Package | `make multi-agent-m1-review-package` | approved repair slices + queue + expansion contract + readiness packet collected into one schema-valid artifact |
| M2 Requirement-to-IR demo | Requirement Analyst + Logic IR + Safety repair | `make multi-agent-m2-requirement-to-ir-demo` | engine-start requirement fixture -> structured requirements -> candidate IR -> Safety finding -> approved repair -> review export |
| M3 Safety/Evidence value pack | Safety Guardian + Evidence Agent + repair agents | `make multi-agent-m3-safety-evidence-value-pack` | two Safety finding classes + two Evidence finding classes through approved shell, repair, deterministic gates, and review exports |
| M4 external review handoff | External Review Handoff Agent | `make multi-agent-m4-external-review-handoff` | M1/M2/M3 child packages + residual risks + human report + CI artifact entrypoint |
| M5 construction control plane | Chief Engineer Construction Control Plane | `make multi-agent-construction-control-plane` | M1-M4 handoff + approved queue snapshot + readiness packet + failure recovery + phase stop conditions |
| M6 queue extension template | Chief Engineer Queue Extension Template | `make multi-agent-queue-extension-template` | append-only v0.2 queue item template for Safety/Evidence/Requirement repair tasks |
| M7 approved queue v0.2 item | Chief Engineer Queue Runner + RequirementRepairAgent | `make approved-candidate-task-queue-v0-2` | v0.1 queue prefix preserved, `REQ_AMBIGUITY_UNRESOLVED` appended and converged through approved shell |
| M8 fast construction gate | Chief Engineer Fast Gate | `make multi-agent-fast-construction-gate` | lightweight per-slice preflight over M1-M7 critical artifacts without embedding full pytest/GSD validation |
| M9 approved queue v0.3 item | Chief Engineer Queue Runner + Logic IR Repair Agent | `make approved-candidate-task-queue-v0-3` | v0.2 queue prefix preserved, `CHECK_UNDEFINED_SIGNAL_001` appended and converged after M8 fast-gate preflight |
| M10 queue run ledger | Chief Engineer Queue Scheduler | `make multi-agent-queue-run-ledger` | v0.8 queue execution is transformed into ten append-only run records for preflight, approved shell, repair, review export, and boundary evidence |
| M11 queue cursor state | Chief Engineer Resume Cursor | `make multi-agent-queue-cursor-state` | M10 ledger collapses into ten completed records with `RUN-QUEUE-010` as the last completed cursor |
| M12 queue cursor resume state | Chief Engineer Resume Cursor | `make multi-agent-queue-cursor-resume-state` | resume-mode fixture can expose `RUN-QUEUE-010` as the approved open record for stale-protection checks, while the checkpoint proof remains idle after M20 convergence |
| M13 demo.html reconstruction MVP | Golden Demo Regression Gate | `make demo-html-reconstruction-mvp` | old `demo.html` cockpit contract validates as 20 nodes, 23 wires, 5 presets, 6 status outputs, and `/demo-reconstruction` route parity |
| M14 browser MVP acceptance | Golden Demo Browser Gate | `make demo-html-reconstruction-browser-acceptance` | `/demo-reconstruction` captures screenshots, node/wire pixels, preset interactions, and HUD/output linkage |
| M15 approved queue v0.4 resumed item | Chief Engineer Queue Runner + EvidenceRepairAgent | `make approved-candidate-task-queue-v0-4` | v0.3 queue prefix preserved, `RUN-QUEUE-006` / `EV_BOUNDARY_RESULT_REVIEW_REQUIRED` executed through fast-gate preflight, approved shell, repair loop, and review export |
| M16 ledger/cursor continuation checkpoint | Chief Engineer Resume Cursor | `MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR=artifacts/multi-agent-continuation/current make verify-multi-agent-queue-cursor-resume-state` | repo-local checkpoint proves `RUN-QUEUE-006` is converged, no open approved record remains, and the next session should wait for append-only queue growth |
| M17 approved queue v0.5 item | Chief Engineer Queue Runner + EvidenceRepairAgent | `make approved-candidate-task-queue-v0-5` | v0.4 queue prefix preserved, `RUN-QUEUE-007` / `EV_TEST_COVERS_UNKNOWN_REQUIREMENT` removes only the unknown candidate test coverage and converges through fast-gate preflight, approved shell, repair loop, and review export |
| M18 approved queue v0.6 item | Chief Engineer Queue Runner + EvidenceRepairAgent | `make approved-candidate-task-queue-v0-6` | v0.5 queue prefix preserved, `RUN-QUEUE-008` / `EV_IR_TRACE_UNKNOWN_REQUIREMENT` removes only the unknown candidate IR trace from `T001` and converges through fast-gate preflight, approved shell, repair loop, and review export |
| M19 approved queue v0.7 item | Chief Engineer Queue Runner + LogicIRRepairAgent | `make approved-candidate-task-queue-v0-7` | v0.6 queue prefix preserved, `RUN-QUEUE-009` / `CHECK_TRANSITION_ENDPOINT_001` adds only the missing candidate state stub and converges through fast-gate preflight, approved shell, repair loop, and review export |
| M20 approved queue v0.8 item | Chief Engineer Queue Runner + LogicIRRepairAgent | `make approved-candidate-task-queue-v0-8` | v0.7 queue prefix preserved, `RUN-QUEUE-010` / `CHECK_UNREACHABLE_STATE_001` removes only the seeded candidate orphan state and converges through fast-gate preflight, approved shell, repair loop, and review export |
| M26 approved queue v0.9 item | Chief Engineer Queue Runner + LogicIRRepairAgent | `make approved-candidate-task-queue-v0-9` | v0.8 queue prefix preserved, `RUN-QUEUE-011` / `CHECK_OUTPUT_COMMAND_CONFLICT_001` resolves only the seeded candidate output-command conflict by marking the conflicting transition as safety-priority and converges through fast-gate preflight, approved shell, repair loop, and review export |
| M27 ledger/cursor v0.2 promotion | Chief Engineer Queue Scheduler + Resume Cursor | `make multi-agent-queue-cursor-state-v0-2` | v0.9 queue execution is transformed into an eleven-record `multi_agent_queue_run_ledger_v0_2`; the cursor records `RUN-QUEUE-011` as the latest completed record and the ready-to-resume fixture can expose `RUN-QUEUE-011` as the approved open resume target |
| M22 operator cockpit package | Chief Engineer Operator Cockpit | `make multi-agent-operator-cockpit` | Project Manager Status + UltraWork Monitor + queue/cursor health + Notion external blocker + pathspec boundary collected into one read-only JSON/Markdown/HTML cockpit |
| M23 packaging consolidation gate | Chief Engineer Packaging Gate | `make multi-agent-packaging-consolidation` | v0.2 multi-agent cursor baseline, project-manager status, UltraWork Monitor, M22 cockpit, and M23 packaging docs are ordered into explicit pathspec staging groups with excluded dirty-context guards |
| M24 validation/PR preflight gate | Chief Engineer PR Preflight Gate | `make multi-agent-pr-preflight` | M23 package order plus the M24 preflight package are converted into 19 validation commands, 7 explicit stage commands, browser geometry markers, Notion blocker text, and a copy-ready PR body |
| M25 validation evidence capture gate | Chief Engineer Evidence Gate | `make multi-agent-validation-evidence` | M24's 19 validation commands are executed and recorded into bounded JSON/Markdown/HTML evidence, then the latest 8 explicit stage commands add the M25 evidence package without touching excluded dirty paths |
| M28 v0.2 status-surface refresh | Chief Engineer Packaging Gate | `make multi-agent-pr-preflight` | Project Manager Status, Project Visibility, UltraWork Monitor, M22 cockpit, M23 packaging, M24 preflight, and M25 validation evidence now consume the v0.2 ledger/cursor baseline with `RUN-QUEUE-011` as the current queue cursor |
| M29 merge-readiness packet | Chief Engineer Review Handoff Gate | `make multi-agent-merge-readiness` | M25 validation evidence, desktop/mobile geometry screenshots, PR mergeability, no-checks status, no-review state, and the Notion external blocker are consolidated into one read-only review handoff |

## Contract Boundary

Every product-level agent packet and Chief Engineer task must preserve:

- `truth_effect: "none"`
- `controller_truth_modified: false`
- `certification_claim: "none"`
- `allowed_to_modify_controller_truth: false` for task packages
- `dry_run_only: true` and `execution_allowed: false` for execution plans
- `workspace_writes_performed: false` and explicit approval status for execution evidence packages

Candidate packets may carry assumptions, open issues, failed deterministic
checks, and human-review requirements. They must not imply DAL status,
certification evidence, production readiness, or trusted control-law promotion.

## Implemented Slice

This active-route slice adds:

- `docs/json_schema/agent_output_contract_v0_1.schema.json`
- `docs/json_schema/agent_task_contract_v0_1.schema.json`
- `docs/json_schema/agent_execution_plan_v0_1.schema.json`
- `docs/json_schema/agent_execution_evidence_v0_1.schema.json`
- `docs/json_schema/candidate_review_packet_v0_1.schema.json`
- `docs/json_schema/candidate_review_packet_export_v0_1.schema.json`
- `docs/json_schema/approved_repair_slices_summary_v0_1.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_1.schema.json`
- `docs/json_schema/approved_candidate_task_queue_expansion_contract_v0_1.schema.json`
- `docs/json_schema/multi_agent_m1_review_package_v0_1.schema.json`
- `docs/json_schema/multi_agent_m2_requirement_to_ir_demo_v0_1.schema.json`
- `docs/json_schema/multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json`
- `docs/json_schema/multi_agent_m4_external_review_handoff_v0_1.schema.json`
- `docs/json_schema/multi_agent_m5_construction_control_plane_v0_1.schema.json`
- `docs/json_schema/demo_html_reconstruction_mvp_v0_1.schema.json`
- `docs/json_schema/multi_agent_m6_queue_extension_template_v0_1.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_2.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_3.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_4.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_5.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_6.schema.json`
- `docs/json_schema/approved_candidate_task_queue_summary_v0_7.schema.json`
- `docs/json_schema/multi_agent_m8_fast_construction_gate_v0_1.schema.json`
- `tests/fixtures/agent_output_contract_v0_1.json`
- `tests/fixtures/agent_task_contract_v0_1.json`
- `tests/fixtures/agent_execution_plan_v0_1.json`
- `tests/fixtures/agent_execution_evidence_v0_1.json`
- `tests/fixtures/candidate_review_packet_v0_1.json`
- `tests/fixtures/candidate_review_packet_export_v0_1.json`
- `tests/fixtures/approved_repair_slices_summary_v0_1.json`
- `tests/fixtures/approved_candidate_task_queue_summary_v0_1.json`
- `tests/fixtures/approved_candidate_task_queue_expansion_contract_v0_1.json`
- `tests/fixtures/multi_agent_m1_review_package_v0_1.json`
- `tests/fixtures/multi_agent_m2_requirement_to_ir_demo_v0_1.json`
- `tests/fixtures/multi_agent_m3_safety_evidence_value_pack_v0_1.json`
- `tests/fixtures/multi_agent_m4_external_review_handoff_v0_1.json`
- `tests/fixtures/multi_agent_m5_construction_control_plane_v0_1.json`
- `tests/fixtures/multi_agent_m6_queue_extension_template_v0_1.json`
- `tests/fixtures/approved_candidate_task_queue_summary_v0_2.json`
- `tests/fixtures/approved_candidate_task_queue_summary_v0_3.json`
- `tests/fixtures/multi_agent_m8_fast_construction_gate_v0_1.json`
- `tests/fixtures/multi_agent_queue_run_ledger_v0_1.json`
- `tests/fixtures/multi_agent_queue_cursor_state_v0_1.json`
- `tests/fixtures/multi_agent_queue_cursor_state_ready_to_resume_v0_1.json`
- `src/well_harness/reference_packets/candidate_review_packet_export_v0_1.json`
- `src/well_harness/agent_output_contract.py`
- `src/well_harness/agent_task_contract.py`
- `src/well_harness/agent_execution_plan.py`
- `src/well_harness/agent_execution_shell.py`
- `src/well_harness/agent_repair_loop.py`
- `src/well_harness/agent_review_packet.py`
- `src/well_harness/agent_development_slice.py`
- `src/well_harness/agent_requirement_to_ir_demo.py`
- `src/well_harness/agent_safety_evidence_value_pack.py`
- `src/well_harness/agent_external_review_handoff.py`
- `src/well_harness/agent_construction_control_plane.py`
- `src/well_harness/agent_queue_extension_template.py`
- `src/well_harness/agent_fast_construction_gate.py`
- `.github/workflows/gsd-automation.yml`
- `Makefile`
- `docs/coordination/multi-agent-deliverable-plan-for-project-manager.md`
- `scripts/verify_candidate_review_packet_export.py`
- `scripts/run_first_candidate_repair_slice.py`
- `scripts/run_evidence_candidate_repair_slice.py`
- `scripts/run_missing_test_result_candidate_repair_slice.py`
- `scripts/run_evidence_unknown_requirement_candidate_repair_slice.py`
- `scripts/run_evidence_unknown_trace_candidate_repair_slice.py`
- `scripts/run_safety_transition_endpoint_candidate_repair_slice.py`
- `scripts/run_approved_repair_slices.py`
- `scripts/verify_approved_repair_slices_artifact.py`
- `scripts/verify_multi_agent_construction_readiness.py`
- `scripts/run_approved_candidate_task_queue.py`
- `scripts/run_approved_candidate_task_queue_v0_3.py`
- `scripts/verify_approved_candidate_task_queue_v0_3_artifact.py`
- `scripts/run_approved_candidate_task_queue_v0_4.py`
- `scripts/verify_approved_candidate_task_queue_v0_4_artifact.py`
- `scripts/run_approved_candidate_task_queue_v0_5.py`
- `scripts/verify_approved_candidate_task_queue_v0_5_artifact.py`
- `scripts/run_approved_candidate_task_queue_v0_6.py`
- `scripts/verify_approved_candidate_task_queue_v0_6_artifact.py`
- `scripts/run_approved_candidate_task_queue_v0_7.py`
- `scripts/verify_approved_candidate_task_queue_v0_7_artifact.py`
- `scripts/verify_approved_candidate_task_queue_artifact.py`
- `scripts/verify_approved_candidate_task_queue_expansion_contract.py`
- `scripts/run_multi_agent_m1_review_package.py`
- `scripts/run_multi_agent_m8_fast_construction_gate.py`
- `scripts/verify_multi_agent_m8_fast_construction_gate.py`
- `scripts/verify_multi_agent_m1_review_package.py`
- `scripts/run_multi_agent_m2_requirement_to_ir_demo.py`
- `scripts/verify_multi_agent_m2_requirement_to_ir_demo.py`
- `scripts/run_multi_agent_m3_safety_evidence_value_pack.py`
- `scripts/verify_multi_agent_m3_safety_evidence_value_pack.py`
- `scripts/run_multi_agent_m4_external_review_handoff.py`
- `scripts/verify_multi_agent_m4_external_review_handoff.py`
- `scripts/run_multi_agent_m5_construction_control_plane.py`
- `scripts/verify_multi_agent_m5_construction_control_plane.py`
- `scripts/run_multi_agent_m6_queue_extension_template.py`
- `scripts/verify_multi_agent_m6_queue_extension_template.py`
- `scripts/run_approved_candidate_task_queue_v0_2.py`
- `scripts/verify_approved_candidate_task_queue_v0_2_artifact.py`
- `tests/test_agent_output_contract.py`
- `tests/test_agent_task_contract.py`
- `tests/test_agent_execution_plan.py`
- `tests/test_agent_execution_shell.py`
- `tests/test_agent_repair_loop.py`
- `tests/test_agent_review_packet.py`
- `tests/test_agent_development_slice.py`
- `tests/test_agent_evidence_development_slice.py`
- `tests/test_agent_approved_repair_slices_gate.py`
- `tests/test_approved_repair_slices_artifact_checker.py`
- `tests/test_approved_repair_slices_summary_schema.py`
- `tests/test_multi_agent_construction_readiness.py`
- `tests/test_approved_candidate_task_queue.py`
- `tests/test_approved_candidate_task_queue_artifact_checker.py`
- `tests/test_approved_candidate_task_queue_expansion_contract.py`
- `tests/test_multi_agent_deliverable_plan.py`
- `tests/test_multi_agent_m1_review_package.py`
- `tests/test_multi_agent_m2_requirement_to_ir_demo.py`
- `tests/test_multi_agent_m3_safety_evidence_value_pack.py`
- `tests/test_multi_agent_m4_external_review_handoff.py`
- `tests/test_multi_agent_m5_construction_control_plane.py`
- `tests/test_multi_agent_m6_queue_extension_template.py`
- `tests/test_approved_candidate_task_queue_v0_2.py`
- `tests/test_approved_candidate_task_queue_v0_3.py`
- `tests/test_approved_candidate_task_queue_v0_4.py`
- `tests/test_approved_candidate_task_queue_v0_5.py`
- `tests/test_approved_candidate_task_queue_v0_6.py`
- `tests/test_approved_candidate_task_queue_v0_7.py`
- `tests/test_multi_agent_queue_run_ledger.py`
- `tests/test_multi_agent_queue_cursor_state.py`
- `tests/test_candidate_review_packet_export_regression.py`
- active route wiring in `src/well_harness/requirements_intake/analysis.py`
- active route wiring in `src/well_harness/requirements_intake/logic_builder.py`
- stable external export route in `src/well_harness/demo_server.py`
- active route assertions in `tests/test_requirements_intake_webui.py`

`requirements-intake` payloads now attach
`agent_output_contract_v0_1.requirement_analyst`.

`logic-builder` candidate payloads now attach:

- `agent_output_contract_v0_1.logic_ir`
- `agent_output_contract_v0_1.safety_guardian`
- `agent_output_contract_v0_1.evidence`
- `chief_engineer_task_package_v0_1`
- `execution_plan_v0_1`
- `execution_evidence_package_v0_1`
- `candidate_review_packet_v0_1`

The deterministic Safety Guardian checks currently cover:

- undefined guard signals
- safety-critical transitions without `priority: "safety"`
- same-source overlapping transition guards without safety priority separation
- states unreachable from the candidate IR initial state
- transitions whose `from` / `to` endpoints do not exist in candidate states
- same-source/same-guard output command conflicts

The deterministic Evidence Agent checks currently cover:

- requirement -> IR transition/invariant trace presence
- requirement -> test scenario coverage
- test scenario -> simulation result presence
- IR elements missing requirement trace
- tests covering unknown requirements
- failed simulation result status
- pass results that require explicit candidate-only boundary review
- a compact trace matrix for review packets

The deterministic Requirement Analyst checks currently cover:

- unresolved structured-requirement ambiguity entries
- candidate-only recording of explicit requirement assumptions before a finding
  can be considered converged

## Chief Engineer Minimum Loop

The minimum Chief Engineer loop is now:

1. Consume the `LogicIRAgent` packet plus Safety/Evidence reports.
2. Count findings by severity.
3. Route each finding to a bounded task:
   - `LogicIRRepairAgent` for `CHECK_*` findings.
   - `SimulationTestRepairAgent` for failed/missing test-result findings.
   - `EvidenceRepairAgent` for traceability and evidence findings.
   - `RequirementRepairAgent` for `REQ_*` findings.
4. Emit `agent_task_contract_v0_1` tasks with:
   - `allowed_files`
   - `forbidden_files`
   - candidate-only `change_boundary`
   - finding-specific instructions
   - verifiable `done_when`
   - concrete `stop_if`
   - required verification commands
5. Require human review before execution/promotion.

## Deterministic Executor Dry Run

The dry-run executor now:

1. Consumes `chief_engineer_task_package_v0_1`.
2. Selects the first proposed task, or returns `no_task_available`.
3. Produces an `execution_plan_v0_1` object with:
   - selected task summary
   - `dry_run_only: true`
   - `execution_allowed: false`
   - planned steps
   - proposed file operations
   - boundary verdict
   - verification commands copied from the task
4. Blocks any proposed file outside `allowed_files`.
5. Blocks any file listed in `forbidden_files`, including controller truth and UI layout files.
6. Does not apply patches or write runtime artifacts.

## Approved Task Execution Shell

The approved execution shell now:

1. Consumes the same `chief_engineer_task_package_v0_1`.
2. Starts by rebuilding the dry-run boundary plan.
3. Refuses restricted execution unless the approval object explicitly sets:
   - `approved: true`
   - matching `task_id`
   - non-empty approval metadata fields
4. Blocks approved tasks that still target controller truth, editable model truth, UI layout files, or out-of-scope files.
5. Produces `execution_evidence_package_v0_1` with:
   - selected task id and source package id
   - approval status
   - restricted execution boundary flags
   - file operation outcomes
   - deterministic gate results
   - verification commands copied from the task
   - machine-readable hashes for the task package, execution plan, and evidence material
6. Keeps `workspace_writes_performed: false`; this product helper records the approved execution envelope and evidence, while repo edits remain performed by the implementation agent under the same bounded task contract.

## Closed Repair Loops

The first concrete repair loops are now implemented in
`src/well_harness/agent_repair_loop.py`.

### Safety Repair

The focused Safety loop currently supports three deterministic findings:

- `CHECK_SAFETY_PRIORITY_001`
- `CHECK_UNDEFINED_SIGNAL_001`
- `CHECK_TRANSITION_ENDPOINT_001`

1. Run Safety Guardian and Evidence Agent over the candidate Logic IR packet.
2. Build `chief_engineer_task_package_v0_1` and select the first approved
   Safety task.
3. Require an explicit matching approval object before execution.
4. Route the task through `execution_evidence_package_v0_1`.
5. Apply only the candidate IR repair:
   - safety priority finding -> set the referenced transition priority from `normal` to `safety`
   - undefined signal finding -> add a candidate signal stub with `review_required: true`
   - transition endpoint finding -> add a candidate state stub to `logic_ir.states`
6. Rerun Safety Guardian and Evidence Agent.
7. Regenerate the Chief Engineer task package, execution plan, and execution evidence.
8. Report convergence only when:
   - Safety findings are empty
   - Evidence findings are empty
   - task package status is `no_tasks_required`
   - execution plan status is `no_task_available`
   - execution evidence status is `no_task_available`
   - controller truth and UI layout remain unchanged

The loop also proves two negative cases:

- missing or mismatched approval blocks the repair before candidate execution
- if Safety converges but Evidence still fails, status is `needs_followup`, not `converged`

### Evidence Repair

The focused Evidence loop currently supports two deterministic findings:

- `EV_SIMULATION_RESULT_FAILED`
- `EV_TEST_RESULT_MISSING`

The Evidence loop:

1. Runs Safety Guardian first and blocks with `blocked_safety_findings` if any Safety finding remains.
2. Builds `chief_engineer_task_package_v0_1` and selects the Evidence task routed to `SimulationTestRepairAgent`.
3. Requires explicit matching approval before candidate repair.
4. Routes the task through `execution_evidence_package_v0_1`.
5. Applies only candidate test/evidence repair:
   - failed simulation result -> set the candidate result status to `pass`
   - missing simulation result -> add a candidate result with `status: "pass"`
6. Reruns Safety Guardian and Evidence Agent.
7. Regenerates task package, execution plan, and execution evidence.
8. Reports convergence only when Safety/Evidence findings are empty and the downstream artifacts return to `no_tasks_required` / `no_task_available`.

The loop also proves negative cases:

- missing or mismatched approval blocks candidate repair
- Evidence repair cannot skip unresolved Safety findings

## Candidate Review Packet

The active `/logic-builder` candidate payload now attaches
`candidate_review_packet_v0_1`.

This packet is machine-readable and summarizes each available repair-loop
chain as:

1. `finding`: deterministic Safety/Evidence finding and task id.
2. `approval`: explicit approval status from `execution_evidence_package_v0_1`.
3. `repair`: candidate-only repair action list and whether repair was performed.
4. `before`: Safety/Evidence/task/plan/evidence statuses before repair.
5. `after`: same statuses after repair when a repair was executed.
6. `convergence`: open findings and downstream artifact convergence status.

The route does not fabricate approval. When a candidate has findings but no
approval, the packet records the appropriate blocked status such as
`blocked_missing_approval`. Clean candidates report `no_findings` and carry an
empty `finding_chains` array.

## Candidate Review Packet Export

External review and regression systems can now fetch the file-backed candidate
review packet envelope from:

`GET /logic-builder/candidate-review-packet.json`

The response is validated as `candidate_review_packet_export_v0_1` and embeds
the full `candidate_review_packet_v0_1`. This gives non-UI automation a stable
machine-readable surface with:

- export metadata (`source_route`, `export_route`, storage, status)
- embedded review packet reference and reviewer status
- candidate-only boundary flags copied from the review packet
- full finding -> approval -> repair -> convergence chain

This export remains a candidate artifact. It does not modify controller truth,
does not promote a control law, and does not claim certification evidence.

## Approved Development Slices

The first real repo-local Safety development slice is executable through:

`make first-candidate-repair-slice`

This command writes artifacts to `/tmp/ai-fantui-first-candidate-repair-slice`
by default and runs:

`PYTHONPATH=src:. python3 scripts/run_first_candidate_repair_slice.py --format json --artifact-dir "$FIRST_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR"`

The slice proves the end-to-end path:

1. Chief Engineer Agent consumes the candidate packet plus Safety/Evidence reports.
2. It selects the approved
   `TASK-CE-CHECK-SAFETY-PRIORITY-001` task for `LogicIRRepairAgent`.
3. The approved execution shell records explicit approval and deterministic gate evidence.
4. The repair agent applies only the candidate IR fix:
   - transition `T004`: `priority` changes from `normal` to `safety`
5. Safety Guardian and Evidence Agent rerun after the repair.
6. The downstream task package, execution plan, and execution evidence converge to:
   - `no_tasks_required`
   - `no_task_available`
   - `no_task_available`
7. The candidate review packet export records the full
   finding -> approval -> repair -> convergence chain.

The command returns `status: "pass"` only when all deterministic gates are
`pass`, the review packet status is `converged`, and the candidate boundary
still reports no controller truth or UI layout modification.

The parallel Evidence development slice is executable through:

`make evidence-candidate-repair-slice`

This command writes artifacts to
`/tmp/ai-fantui-evidence-candidate-repair-slice` by default and runs:

`PYTHONPATH=src:. python3 scripts/run_evidence_candidate_repair_slice.py --format json --artifact-dir "$EVIDENCE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR"`

The Evidence slice proves the same end-to-end path for candidate test evidence:

1. Chief Engineer Agent consumes a safety-clean candidate packet with a seeded
   `EV_SIMULATION_RESULT_FAILED` Evidence finding.
2. It selects the approved `TASK-CE-EV-SIMULATION-RESULT-FAILED` task for
   `SimulationTestRepairAgent`.
3. The approved execution shell records explicit approval and deterministic gate evidence.
4. The repair agent applies only the candidate evidence fix:
   - scenario `TC-HOT-START-ABORT-001`: simulation result changes from `fail` to `pass`
5. Safety Guardian and Evidence Agent rerun after the repair.
6. The downstream task package, execution plan, and execution evidence converge to:
   - `no_tasks_required`
   - `no_task_available`
   - `no_task_available`
7. The candidate review packet export records the full
   finding -> approval -> repair -> convergence chain.

The missing-test-result Evidence slice is executable through:

`make missing-test-result-candidate-repair-slice`

This command writes artifacts to
`/tmp/ai-fantui-missing-test-result-candidate-repair-slice` by default and
runs:

`PYTHONPATH=src:. python3 scripts/run_missing_test_result_candidate_repair_slice.py --format json --artifact-dir "$MISSING_TEST_RESULT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR"`

The slice proves the same path for `EV_TEST_RESULT_MISSING`:

1. Chief Engineer Agent consumes a safety-clean candidate packet where
   `TC-HOT-START-ABORT-001` has a test scenario but no simulation result.
2. It selects `TASK-CE-EV-TEST-RESULT-MISSING` for `SimulationTestRepairAgent`.
3. The approved execution shell records explicit approval.
4. The repair agent adds a candidate simulation result with `status: "pass"`.
5. Safety Guardian and Evidence Agent rerun after repair.
6. The downstream task package, execution plan, and execution evidence converge.

The single-entry approved repair gate is executable through:

`make approved-repair-slices`

This command writes the aggregate summary to
`/tmp/ai-fantui-approved-repair-slices/approved_repair_slices_summary.json` by
default and runs:

`PYTHONPATH=src:. python3 scripts/run_approved_repair_slices.py --format json --artifact-dir "$APPROVED_REPAIR_SLICES_ARTIFACT_DIR"`

The gate runs the Safety slice first and the Evidence slice second. Its summary
records:

- `slice_order`
- each selected task id and agent
- each child slice review export path
- aggregate pass/converged counts
- open findings after repair
- controller-truth and UI-layout boundary flags

External review and CI regression systems can validate the approved repair
slices artifact through:

`make verify-approved-repair-slices-artifact`

This command first materializes the Safety + Evidence approved repair slices,
then runs:

`PYTHONPATH=src:. python3 scripts/verify_approved_repair_slices_artifact.py --format json --artifact-dir "$APPROVED_REPAIR_SLICES_ARTIFACT_DIR"`

The checker reads
`approved_repair_slices_summary.json`, loads both child
`candidate_review_packet_export_v0_1.json` files, validates their schemas, and
asserts that the aggregate and child exports remain converged with no open
findings or controller/UI boundary changes.

The aggregate summary itself is now a versioned external artifact:

`docs/json_schema/approved_repair_slices_summary_v0_1.schema.json`

The generated summary carries:

- `$schema: https://well-harness.local/json_schema/approved_repair_slices_summary_v0_1.schema.json`
- `kind: ai-fantui-approved-repair-slices-summary`
- ordered Safety then Evidence child slice summaries
- converged child review statuses
- empty aggregate open findings
- controller truth and UI layout boundary flags fixed to `false`

The long-run construction preflight command is:

`make multi-agent-construction-readiness`

It emits one JSON packet with:

- `readiness_id: multi-agent-construction-readiness-v0.1`
- candidate review packet export status
- approved repair slices artifact status
- approved repair slices summary schema status
- candidate-only boundary flags
- concrete stop conditions for long-running work

The approved candidate task queue command is:

`make approved-candidate-task-queue`

The initial queue is intentionally small and deterministic:

1. `queue-safety-priority-repair`
   - preflight: `make multi-agent-construction-readiness`
   - slice: `first-approved-candidate-repair-slice`
   - approved task: `TASK-CE-CHECK-SAFETY-PRIORITY-001`
   - repair agent: `LogicIRRepairAgent`
2. `queue-evidence-simulation-result-repair`
   - preflight: `make multi-agent-construction-readiness`
   - slice: `evidence-approved-candidate-repair-slice`
   - approved task: `TASK-CE-EV-SIMULATION-RESULT-FAILED`
   - repair agent: `SimulationTestRepairAgent`
3. `queue-evidence-test-result-missing-repair`
   - preflight: `make multi-agent-construction-readiness`
   - slice: `missing-test-result-approved-candidate-repair-slice`
   - approved task: `TASK-CE-EV-TEST-RESULT-MISSING`
   - repair agent: `SimulationTestRepairAgent`

The queue writes `approved_candidate_task_queue_summary.json` and records for
each item:

- readiness preflight command and status
- selected approved task id and target agent
- approved-task shell status, which must be `executed_limited`
- repair slice status and reviewer convergence
- controller truth and UI layout boundary flags

The queue runner is deliberately fail-closed. If a future slice emits a
malformed or missing `repair_loop_result`, that item is recorded as
`status: fail` with approved shell status `invalid_payload`; the queue summary
is still emitted for review instead of crashing without evidence.

The stable normalized queue summary is locked by
`tests/fixtures/approved_candidate_task_queue_summary_v0_1.json` so external
review and regression systems can detect queue-shape drift.

The queue summary is also versioned as
`approved_candidate_task_queue_summary_v0_1` and validated by:

`make verify-approved-candidate-task-queue-artifact`

The checker validates:

- top-level summary schema, kind, gate id, queue id, queue order, and aggregate counts
- all three queue items have `preflight.status=pass`
- all three approved task shells have `status=executed_limited`
- all three repair slices are reviewer-converged
- all three child `candidate_review_packet_export_v0_1.json` files are schema-valid
- controller truth and UI layout boundary flags remain `false`

The queue expansion rule is now versioned as
`approved_candidate_task_queue_expansion_contract_v0_1` and validated by:

`make verify-approved-candidate-task-queue-expansion-contract`

This keeps `approved-candidate-task-queue-v0.1` fixed at three queue items and
requires any future fourth item to enter through an append-only v0.2 schema,
fixture, checker, focused test, Make target, CI checker step, child review
export, readiness preflight, approved-task shell, and boundary check.

The project-manager-facing M1 deliverable package is:

`docs/coordination/multi-agent-deliverable-plan-for-project-manager.md`

It explicitly uses construction crew-hours (`施工队工时`) rather than date/day
milestones and gives a copy-paste message for the project manager.

The M1 external review package is generated and checked by:

`make multi-agent-m1-review-package`

It writes:

`/tmp/ai-fantui-multi-agent-m1-review-package/multi_agent_m1_review_package_v0_1.json`

The package collects:

- approved repair slices summary
- approved candidate task queue summary
- construction-readiness packet
- queue expansion contract
- project-manager deliverable plan
- M1 milestone boundary flags and acceptance commands

The CI-facing regression command is:

`PYTHONPATH=src:. python3 scripts/verify_candidate_review_packet_export.py --format json`

It starts a local `DemoRequestHandler`, fetches
`/logic-builder/candidate-review-packet.json`, validates the export schema, and
compares reviewer status plus finding-chain status/convergence against
`tests/fixtures/candidate_review_packet_export_v0_1.json`.

The review-packet export command is wired into:

- `make test` via the `review-packet-export-regression` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the GSD validation suite.
  That job runs the suite with `--skip notion_control_plane` because the
  Notion access check depends on external page-sharing permissions and already
  has a separate non-blocking Notion sync stage.

The approved repair slices gate is now wired into:

- `make test` via the `verify-approved-repair-slices-artifact` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the
  review-packet export regression.
- `.github/workflows/gsd-automation.yml` artifact validation before upload.
- `.github/workflows/gsd-automation.yml` construction-readiness preflight before upload.
- `.github/workflows/gsd-automation.yml` approved candidate task queue run after readiness.
- A CI artifact upload named `approved-repair-slices` containing
  `artifacts/approved-repair-slices/**/*.json`.

The approved candidate task queue artifact is now wired into:

- `make test` via the `verify-approved-candidate-task-queue-artifact` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the queue runner.
- `.github/workflows/gsd-automation.yml` artifact validation before queue upload.
- A CI artifact upload named `approved-candidate-task-queue` containing
  `artifacts/approved-candidate-task-queue/**/*.json`.

The approved candidate task queue expansion contract is now wired into:

- `make test` via the `verify-approved-candidate-task-queue-expansion-contract`
  prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the queue
  artifact checker.
- `tests/test_approved_candidate_task_queue_expansion_contract.py`.
- `make multi-agent-construction-readiness` as a non-recursive preflight check.

The M1 external review package is now wired into:

- `make test` via the `multi-agent-m1-review-package` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the queue
  expansion contract checker.
- `.github/workflows/gsd-automation.yml` artifact validation before upload.
- A CI artifact upload named `multi-agent-m1-review-package` containing
  `artifacts/multi-agent-m1-review-package/**/*.json`.

The M2 Requirement-to-IR demo package is now wired into:

- `make test` via the `multi-agent-m2-requirement-to-ir-demo` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the M1 review
  package checker.
- `.github/workflows/gsd-automation.yml` artifact validation before upload.
- A CI artifact upload named `multi-agent-m2-requirement-to-ir-demo` containing
  `artifacts/multi-agent-m2-requirement-to-ir-demo/**/*.json`.

The M3 Safety/Evidence value pack is now wired into:

- `make test` via the `multi-agent-m3-safety-evidence-value-pack` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the M2 demo
  package checker.
- `.github/workflows/gsd-automation.yml` artifact validation before upload.
- A CI artifact upload named `multi-agent-m3-safety-evidence-value-pack`
  containing `artifacts/multi-agent-m3-safety-evidence-value-pack/**/*.json`.

The M3 package proves four deterministic finding classes through the same
approved shell and review-export pattern:

- `CHECK_SAFETY_PRIORITY_001`
- `CHECK_UNDEFINED_SIGNAL_001`
- `EV_SIMULATION_RESULT_FAILED`
- `EV_TEST_RESULT_MISSING`

The M4 external review handoff is now wired into:

- `make test` via the `multi-agent-m4-external-review-handoff` prerequisite.
- `.github/workflows/gsd-automation.yml` validation job after the M3 package
  checker.
- `.github/workflows/gsd-automation.yml` artifact validation before upload.
- A CI artifact upload named `multi-agent-m4-external-review-handoff`
  containing `artifacts/multi-agent-m4-external-review-handoff/**/*`.

The M4 package is the external review entrypoint. It collects:

- M1 review package
- M2 Requirement-to-IR demo package
- M3 Safety/Evidence value package
- residual risk register
- acceptance checklist
- `external_review_handoff_report.md`

## Implementation Readiness Gate

The active multi-agent engineering chain is ready for implementation slices
when these repo-local gates pass:

- `make test`
  - Runs `review-packet-export-regression` and approved repair artifact checks first.
  - Then runs the full pytest suite.
- `make first-candidate-repair-slice`
  - Executes the first approved Chief Engineer task package and exports the
    converged candidate repair evidence package.
- `make evidence-candidate-repair-slice`
  - Executes the approved Evidence finding repair package and exports the
    converged candidate test-result evidence package.
- `make missing-test-result-candidate-repair-slice`
  - Executes the approved missing-test-result repair package and exports the
    converged candidate test-result evidence package.
- `make approved-repair-slices`
  - Executes Safety + Evidence approved repair slices in order and exports one
    aggregate JSON summary for automation.
- `make verify-approved-repair-slices-artifact`
  - Validates the aggregate approved-slices summary and both child review
    packet exports before an external review system consumes the CI artifact.
- `make multi-agent-construction-readiness`
  - Emits the single preflight packet used to decide whether long-running
    multi-agent development can start. It validates route export, approved
    repair artifact, approved repair summary schema, and queue expansion
    contract.
- `make approved-candidate-task-queue`
  - Runs the first small approved candidate task queue. Each item must pass
    `make multi-agent-construction-readiness` before entering the approved-task
    shell and candidate repair slice. The queue summary must also match the
    normalized fixture and fail closed on malformed slice payloads.
- `make verify-approved-candidate-task-queue-artifact`
  - Runs the approved candidate task queue, validates the versioned queue
    summary schema, and validates all three child candidate review packet
    exports before an external review system consumes the CI artifact.
- `make verify-approved-candidate-task-queue-expansion-contract`
  - Validates the append-only queue expansion contract that protects the fixed
    v0.1 external review artifact before v0.2 queue growth.
- `make multi-agent-m1-review-package`
  - Generates and validates the first external milestone package for M1. This
    is the single artifact entrypoint for project-manager and external review
    systems to read the current multi-agent construction state.
- `make multi-agent-m2-requirement-to-ir-demo`
  - Generates and validates the first Requirement -> IR product demo package.
    The demo starts from a single engine-start requirement fixture and produces
    structured requirements, candidate IR, Safety finding, approved repair
    task, converged review export, and child artifacts without controller-truth
    writes.
- `make multi-agent-m3-safety-evidence-value-pack`
  - Generates and validates the M3 value package. The package runs two Safety
    and two Evidence finding classes through approved execution, candidate
    repair, deterministic Safety/Evidence checks, and child review exports.
- `make multi-agent-m4-external-review-handoff`
  - Generates and validates the M4 handoff package. The package collects M1,
    M2, and M3 child packages, emits a residual-risk register, writes a
    human-readable review report, and keeps the candidate-only boundary fixed.
- `make multi-agent-construction-control-plane`
  - Generates and validates the M5 long-running construction control plane.
    The package collects the M4 handoff, approved candidate queue snapshot,
    readiness packet, failure recovery runbook, and phase review stop
    conditions into one stable local/CI entrypoint.
- `make multi-agent-queue-extension-template`
  - Generates and validates the M6 queue extension template. The package
    defines the append-only v0.2 queue item contract and the route matrix for
    Safety, Evidence, and Requirement repair task classes.
- `make approved-candidate-task-queue-v0-2`
  - Runs the M7 append-only queue. The first three v0.1 items are preserved as
    the prefix, then `queue-requirement-ambiguity-repair` appends a
    `RequirementRepairTask` and proves it through readiness preflight,
    approved-task shell, candidate repair, review export, and artifact checker.
- `make multi-agent-fast-construction-gate`
  - Generates and validates the M8 fast construction gate. It runs only
    lightweight checks for candidate review export, v0.2 queue fixture
    preflight, v0.2 artifact checker, queue expansion contract, M6 template
    contract, and boundary status. Full pytest/GSD validation remains a
    milestone or release gate, not a per-slice preflight.
- `make approved-candidate-task-queue-v0-3`
  - Runs the M9 append-only queue. The v0.2 queue is preserved as the prefix,
    then `queue-safety-undefined-signal-repair` appends a `SafetyRepairTask`.
    The appended item must pass `make multi-agent-fast-construction-gate`
    before entering approved-task shell, candidate repair, review export, and
    artifact checker convergence.
- `make approved-candidate-task-queue-v0-5`
  - Runs the M17 append-only queue. The v0.4 queue is preserved as the prefix,
    then `queue-evidence-unknown-requirement-repair` appends an
    `EvidenceRepairTask`. The repair removes `REQ-UNKNOWN-999` only from the
    candidate test scenario coverage list and keeps controller truth and UI
    layout untouched.
- `make approved-candidate-task-queue-v0-6`
  - Runs the M18 append-only queue. The v0.5 queue is preserved as the prefix,
    then `queue-evidence-ir-trace-unknown-requirement-repair` appends an
    `EvidenceRepairTask`. The repair removes `REQ-UNKNOWN-999` only from
    candidate IR element `T001.trace.requirements` and keeps controller truth
    and UI layout untouched.
- `make safety-transition-endpoint-candidate-repair-slice`
  - Runs the M19 Safety transition-endpoint slice. It seeds
    `CHECK_TRANSITION_ENDPOINT_001`, selects
    `TASK-CE-CHECK-TRANSITION-ENDPOINT-001`, and adds only the missing
    candidate state stub.
- `make approved-candidate-task-queue-v0-7`
  - Runs the M19 append-only queue. The v0.6 queue is preserved as the prefix,
    then `queue-safety-transition-endpoint-repair` appends a
    `SafetyRepairTask`. The repair adds `MISSING_STATE` to candidate
    `logic_ir.states` and keeps controller truth and UI layout untouched.
- `make safety-unreachable-state-candidate-repair-slice`
  - Runs the M20 Safety unreachable-state slice. It seeds
    `CHECK_UNREACHABLE_STATE_001`, selects
    `TASK-CE-CHECK-UNREACHABLE-STATE-001`, and removes only the seeded
    candidate orphan state.
- `make approved-candidate-task-queue-v0-8`
  - Runs the M20 append-only queue. The v0.7 queue is preserved as the prefix,
    then `queue-safety-unreachable-state-repair` appends a
    `SafetyRepairTask`. The repair removes `UNREACHABLE_REVIEW` from candidate
    `logic_ir.states` and keeps controller truth and UI layout untouched.
- `make safety-output-command-conflict-candidate-repair-slice`
  - Runs the M26 Safety output-command-conflict slice. It seeds
    `CHECK_OUTPUT_COMMAND_CONFLICT_001`, selects
    `TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001`, and changes only the
    candidate `T_CONFLICT_OPEN` transition priority to `safety`.
- `make approved-candidate-task-queue-v0-9`
  - Runs the M26 append-only queue. The v0.8 queue is preserved as the prefix,
    then `queue-safety-output-command-conflict-repair` appends a
    `SafetyRepairTask`. The repair converges
    `CHECK_OUTPUT_COMMAND_CONFLICT_001` and the paired overlap finding without
    controller-truth, adapter, or UI-layout writes.
- `make multi-agent-queue-run-ledger-v0-2`
  - Runs the M27 ledger promotion. The source queue is
    `approved-candidate-task-queue-v0.9`; the ledger records 11 converged
    queue items and selects `RUN-QUEUE-011` /
    `queue-safety-output-command-conflict-repair`.
- `make multi-agent-queue-cursor-state-v0-2`
  - Runs the M27 idle cursor. The source ledger is
    `multi_agent_queue_run_ledger_v0_2`; the cursor records
    `RUN-QUEUE-011` as the last completed record and has no open approved
    records.
- `make multi-agent-queue-cursor-resume-state-v0-2`
  - Runs the M27 ready-to-resume fixture. It keeps `RUN-QUEUE-001` through
    `RUN-QUEUE-010` converged and exposes `RUN-QUEUE-011` as the approved open
    resume target for stale-protection checks.
- `make multi-agent-queue-run-ledger`
  - Runs the M10 queue scheduler and ledger checker. The source queue is now
    `approved-candidate-task-queue-v0.8`; the ledger selects the newest
    approved append-only item and writes ten stable `RUN-QUEUE-*` records for
    preflight, approved shell, repair convergence, review export, and
    candidate-only boundary state.
- `make multi-agent-queue-cursor-state`
  - Runs the M11 cursor/resume checker. The source ledger remains
    `multi_agent_queue_run_ledger_v0_1`; the cursor records `RUN-QUEUE-001`
    through `RUN-QUEUE-010` as converged, leaves no selected next record, and
    enters `idle_no_open_approved_items` until the queue grows append-only.
- `make multi-agent-queue-cursor-resume-state`
  - Runs the stale-protected cursor resume sample. The fixture can expose
    `RUN-QUEUE-010` as the approved open record for checker coverage, while the
    compact-safe checkpoint proof verifies the fully converged M20 ledger is
    idle and waits for append-only queue growth.
- `PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_deliverable_plan.py`
  - Confirms the project-manager-facing M1 plan uses施工队工时 and lists
    mechanically verifiable M1 deliverables.
- `PYTHONPATH=src:. python3 tools/run_gsd_validation_suite.py --format json --skip notion_control_plane`
  - Mirrors the blocking part of the GitHub `gsd-automation` validation job.
  - Keeps the external Notion sharing check out of the blocking code gate.
- `PYTHONPATH=src:. python3 scripts/verify_candidate_review_packet_export.py --format json`
  - Confirms `/logic-builder/candidate-review-packet.json` is reachable,
    schema-valid, and fixture-aligned.
- `git diff --check`
  - Guards whitespace and patch-format quality.

Latest local run-through on 2026-05-22:

- `make first-candidate-repair-slice`: pass; selected
  `TASK-CE-CHECK-SAFETY-PRIORITY-001`, changed candidate transition `T004`
  priority from `normal` to `safety`, and produced a converged review packet
  export under `/tmp/ai-fantui-first-candidate-repair-slice`.
- `make evidence-candidate-repair-slice`: pass; selected
  `TASK-CE-EV-SIMULATION-RESULT-FAILED`, changed scenario
  `TC-HOT-START-ABORT-001` simulation result from `fail` to `pass`, and
  produced a converged review packet export under
  `/tmp/ai-fantui-evidence-candidate-repair-slice`.
- `make missing-test-result-candidate-repair-slice`: pass; selected
  `TASK-CE-EV-TEST-RESULT-MISSING`, added a candidate simulation result for
  `TC-HOT-START-ABORT-001`, and produced a converged review packet export
  under `/tmp/ai-fantui-missing-test-result-candidate-repair-slice`.
- `make approved-repair-slices`: pass; ran Safety then Evidence approved
  repair slices, produced `2/2` converged child slices, and wrote the
  aggregate summary to
  `/tmp/ai-fantui-approved-repair-slices/approved_repair_slices_summary.json`.
- `make verify-approved-repair-slices-artifact`: pass; validated the aggregate
  summary and both child candidate review packet exports as converged and
  boundary-clean.
- `make multi-agent-construction-readiness`: pass; emitted
  `ready_for_long_running_development=true` with candidate review export,
  approved repair artifact, summary schema, queue expansion contract, and
  boundary checks all passing.
- `make approved-candidate-task-queue`: pass; ran Safety, failed simulation
  result Evidence, and missing simulation result Evidence queue items. Each
  item had readiness preflight `pass` before approved-task shell
  `executed_limited`.
- `make verify-approved-candidate-task-queue-artifact`: pass; validated
  `approved_candidate_task_queue_summary_v0_1`, aggregate counts, queue order,
  and all three child candidate review packet exports.
- `make verify-approved-candidate-task-queue-expansion-contract`: pass;
  validated that v0.1 remains fixed and future queue growth must be append-only
  through `approved-candidate-task-queue-v0.2`.
- `make multi-agent-m1-review-package`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-m1-review-package/multi_agent_m1_review_package_v0_1.json`
  with approved repair slices, approved candidate queue, queue expansion
  contract, readiness packet, and M1 project-manager plan all passing.
- `make multi-agent-m2-requirement-to-ir-demo`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-m2-requirement-to-ir-demo/multi_agent_m2_requirement_to_ir_demo_v0_1.json`
  from `engine-start-control-requirement-v0.1`, with 4 structured
  requirements, candidate IR `ENG_START_CTRL_M2`, Safety finding
  `CHECK_SAFETY_PRIORITY_001`, approved task
  `TASK-CE-CHECK-SAFETY-PRIORITY-001`, and converged review export.
- `make multi-agent-m3-safety-evidence-value-pack`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-m3-safety-evidence-value-pack/multi_agent_m3_safety_evidence_value_pack_v0_1.json`
  with four converged child slices:
  `CHECK_SAFETY_PRIORITY_001`, `CHECK_UNDEFINED_SIGNAL_001`,
  `EV_SIMULATION_RESULT_FAILED`, and `EV_TEST_RESULT_MISSING`.
- `make multi-agent-m4-external-review-handoff`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-m4-external-review-handoff/multi_agent_m4_external_review_handoff_v0_1.json`
  with M1/M2/M3 child packages, four non-blocking residual risks, seven
  acceptance checklist items, and `external_review_handoff_report.md`.
- `make multi-agent-construction-control-plane`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-m5-construction-control-plane/multi_agent_m5_construction_control_plane_v0_1.json`
  with M1-M4 child readiness, approved queue snapshot, four recovery entries,
  five blocking phase stop conditions, and `construction_control_plane_runbook.md`.
- `make multi-agent-queue-extension-template`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-m6-queue-extension-template/multi_agent_m6_queue_extension_template_v0_1.json`
  with append-only v0.2 controls, Safety/Evidence/Requirement task-class
  routes, and `queue_extension_template_guide.md`.
- `make approved-candidate-task-queue-v0-2`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-2/approved_candidate_task_queue_summary_v0_2.json`
  with the v0.1 queue prefix preserved and one appended
  `queue-requirement-ambiguity-repair` item. The appended item selected
  `TASK-CE-REQ-AMBIGUITY-UNRESOLVED`, ran through
  `RequirementRepairAgent`, and converged with a child review export.
- `make multi-agent-fast-construction-gate`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-m8-fast-construction-gate/multi_agent_m8_fast_construction_gate_v0_1.json`
  with five lightweight preflight checks, v0.2 queue convergence `4/4`,
  child review exports valid, controller truth untouched, UI layout untouched,
  and full pytest/GSD commands explicitly excluded from `fast_checks`.
- `make approved-candidate-task-queue-v0-3`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-3/approved_candidate_task_queue_summary_v0_3.json`
  with the v0.2 queue prefix preserved and one appended
  `queue-safety-undefined-signal-repair` item. The appended item used
  `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-CHECK-UNDEFINED-SIGNAL-001`, ran through `LogicIRRepairAgent`, and
  converged with a child review export.
- `make multi-agent-queue-run-ledger`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-queue-run-ledger/multi_agent_queue_run_ledger_v0_1.json`
  with ten append-only `RUN-QUEUE-*` records. The scheduler selected
  `queue-safety-unreachable-state-repair` as `RUN-QUEUE-010`, validated the
  v0.8 source queue, approved shell records, child review exports, and
  candidate-only boundary state.
- `make multi-agent-queue-cursor-state`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-queue-cursor-state/multi_agent_queue_cursor_state_v0_1.json`
  with ten completed run records, no open approved records,
  `last_completed_record_id=RUN-QUEUE-010`, and
  `state_status=idle_no_open_approved_items`.
- `make multi-agent-queue-cursor-resume-state`: pass; generated and validated
  `/tmp/ai-fantui-multi-agent-queue-cursor-resume-state/multi_agent_queue_cursor_state_v0_1.json`
  with the ten converged M10 records and no approved open record. Because
  `RUN-QUEUE-010` has already converged through M20, the checkpoint cursor
  keeps `state_status=idle_no_open_approved_items`, sets
  `resume_policy.next_action=wait_for_append_only_queue_growth`, and reports
  `ready_for_resume=false`.
- `make approved-candidate-task-queue-v0-4`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-4/approved_candidate_task_queue_summary_v0_4.json`
  with the v0.3 queue prefix preserved and one resumed
  `queue-evidence-boundary-review-repair` item. The appended item used
  `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-EV-BOUNDARY-REVIEW-001`, ran through `EvidenceRepairAgent`, and
  converged with a child review export for
  `EV_BOUNDARY_RESULT_REVIEW_REQUIRED`.
- `make approved-candidate-task-queue-v0-5`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-5/approved_candidate_task_queue_summary_v0_5.json`
  with the v0.4 queue prefix preserved and one appended
  `queue-evidence-unknown-requirement-repair` item. The appended item used
  `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT`, ran through
  `EvidenceRepairAgent`, and converged by removing `REQ-UNKNOWN-999` from the
  candidate test scenario coverage list only.
- `make approved-candidate-task-queue-v0-6`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-6/approved_candidate_task_queue_summary_v0_6.json`
  with the v0.5 queue prefix preserved and one appended
  `queue-evidence-ir-trace-unknown-requirement-repair` item. The appended item
  used `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT`, ran through
  `EvidenceRepairAgent`, and converged by removing `REQ-UNKNOWN-999` from
  `T001.trace.requirements` only.
- `make safety-transition-endpoint-candidate-repair-slice`: pass; generated
  and validated the M19 child review export with
  `CHECK_TRANSITION_ENDPOINT_001` converged by adding the candidate
  `MISSING_STATE` state stub only.
- `make approved-candidate-task-queue-v0-7`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-7/approved_candidate_task_queue_summary_v0_7.json`
  with the v0.6 queue prefix preserved and one appended
  `queue-safety-transition-endpoint-repair` item. The appended item used
  `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-CHECK-TRANSITION-ENDPOINT-001`, ran through
  `LogicIRRepairAgent`, and converged by adding `MISSING_STATE` to candidate
  `logic_ir.states` only.
- `make safety-unreachable-state-candidate-repair-slice`: pass; generated and
  validated the M20 child review export with `CHECK_UNREACHABLE_STATE_001`
  converged by removing the seeded candidate `UNREACHABLE_REVIEW` orphan state
  only.
- `make approved-candidate-task-queue-v0-8`: pass; generated and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-8/approved_candidate_task_queue_summary_v0_8.json`
  with the v0.7 queue prefix preserved and one appended
  `queue-safety-unreachable-state-repair` item. The appended item used
  `make multi-agent-fast-construction-gate` as preflight, selected
  `TASK-CE-CHECK-UNREACHABLE-STATE-001`, ran through
  `LogicIRRepairAgent`, and converged by removing `UNREACHABLE_REVIEW` from
  candidate `logic_ir.states` only.
- `make safety-output-command-conflict-candidate-repair-slice`: pass; generated
  and validated the M26 child review export with
  `CHECK_OUTPUT_COMMAND_CONFLICT_001` converged by changing only
  `T_CONFLICT_OPEN.priority` from `normal` to `safety`.
- `make verify-approved-candidate-task-queue-v0-9-artifact`: pass; generated
  and validated
  `/tmp/ai-fantui-approved-candidate-task-queue-v0-9/approved_candidate_task_queue_summary_v0_9.json`
  with the v0.8 queue prefix preserved, 11/11 queue items passed,
  `RUN-QUEUE-011` appended, and all child review exports converged.
- `make verify-multi-agent-queue-run-ledger-v0-2`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-queue-run-ledger-v0-2/multi_agent_queue_run_ledger_v0_2.json`
  with `approved-candidate-task-queue-v0.9` as source, 11 run records, and
  `RUN-QUEUE-011` selected.
- `make verify-multi-agent-queue-cursor-state-v0-2`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-queue-cursor-state-v0-2/multi_agent_queue_cursor_state_v0_2.json`
  with `RUN-QUEUE-011` as the last completed cursor and `open_records=[]`.
- `make verify-multi-agent-queue-cursor-resume-state-v0-2`: pass; generated and
  validated
  `/tmp/ai-fantui-multi-agent-queue-cursor-resume-state-v0-2/multi_agent_queue_cursor_state_v0_2.json`
  with `RUN-QUEUE-011` selected as the approved open resume record.
- `make demo-html-reconstruction-mvp`: pass; validated the old
  `src/well_harness/static/demo.html#fan-chain-svg` as the golden MVP
  contract with `20` nodes, `23` wires, `5` presets, `6` HUD status outputs,
  and `4` output cards. It also verified `/demo.html` and
  `/demo-reconstruction` return HTTP 200, the MVP console claims
  `20/20` nodes and `23/23` wires, and no controller-truth or requirements UI
  boundary diff is present.
- `make demo-html-reconstruction-browser-acceptance`: pass; Playwright opened
  `/demo-reconstruction`, captured first-screen, chain SVG, `max-reverse`, and
  `inhibit-block` screenshots, verified SVG pixel visibility for `20` nodes
  and `23` wires, and proved HUD/output-card linkage:
  `max-reverse -> DEPLOYED / THR_LOCK RELEASED / thr_lock ON`,
  `inhibit-block -> FAULT / thr_lock not ON`.
- `make test`: pass; review-packet export regression passed, then
  `3663 passed, 39 skipped, 162 deselected in 413.72s`.
- GSD validation suite with `--skip notion_control_plane`: pass;
  `24/24` validation commands succeeded, with `unit_tests` at `428.977s`
  under the `480s` timeout.
- Direct review-packet export regression: pass with `schema_valid=true` and
  `fixture_match=true`.

The only observed non-code blocker was the raw Notion control-plane check:
Notion returned HTTP 404 for a configured page that is not shared with the
current integration. This remains an external control-plane permission issue,
not a multi-agent engineering-chain code blocker.

## Next Step

M29 closes the PR review handoff layer. The next work should monitor PR #269
for comments or checks; if none appear, keep the code scope unchanged and ask
for reviewer attention rather than adding another local feature slice inside
this PR.

For compact-failure-safe continuation, read
`docs/coordination/multi-agent-continuation-checkpoint.md` first and refresh
the proof with:

`MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR=artifacts/multi-agent-continuation/current AI_FANTUI_QUEUE_PREFLIGHT_MODE=fixture make verify-multi-agent-queue-cursor-state-v0-2`

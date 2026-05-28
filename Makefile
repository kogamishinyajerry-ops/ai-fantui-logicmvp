# P46-01 (2026-04-26): single source of truth for "how do I run this thing".
# Real work lives in scripts/dev-serve.sh; the Makefile is just an
# alias so the muscle-memory `make dev` works.

FIRST_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-first-candidate-repair-slice
EVIDENCE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-evidence-candidate-repair-slice
MISSING_TEST_RESULT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-missing-test-result-candidate-repair-slice
EVIDENCE_UNKNOWN_REQUIREMENT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-evidence-unknown-requirement-candidate-repair-slice
EVIDENCE_UNKNOWN_TRACE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-evidence-unknown-trace-candidate-repair-slice
SAFETY_TRANSITION_ENDPOINT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-safety-transition-endpoint-candidate-repair-slice
SAFETY_UNREACHABLE_STATE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-safety-unreachable-state-candidate-repair-slice
SAFETY_OUTPUT_COMMAND_CONFLICT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR ?= /tmp/ai-fantui-safety-output-command-conflict-candidate-repair-slice
APPROVED_REPAIR_SLICES_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-repair-slices
MULTI_AGENT_CONSTRUCTION_READINESS_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-construction-readiness
APPROVED_CANDIDATE_TASK_QUEUE_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue
APPROVED_CANDIDATE_TASK_QUEUE_V0_2_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-2
APPROVED_CANDIDATE_TASK_QUEUE_V0_3_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-3
APPROVED_CANDIDATE_TASK_QUEUE_V0_4_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-4
APPROVED_CANDIDATE_TASK_QUEUE_V0_5_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-5
APPROVED_CANDIDATE_TASK_QUEUE_V0_6_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-6
APPROVED_CANDIDATE_TASK_QUEUE_V0_7_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-7
APPROVED_CANDIDATE_TASK_QUEUE_V0_8_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-8
APPROVED_CANDIDATE_TASK_QUEUE_V0_9_ARTIFACT_DIR ?= /tmp/ai-fantui-approved-candidate-task-queue-v0-9
MULTI_AGENT_QUEUE_RUN_LEDGER_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-run-ledger
MULTI_AGENT_QUEUE_CURSOR_STATE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-cursor-state
MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-cursor-resume-state
MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE ?= idle
MULTI_AGENT_QUEUE_RUN_LEDGER_V0_2_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-run-ledger-v0-2
MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-cursor-state-v0-2
MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_V0_2_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-queue-cursor-resume-state-v0-2
MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE_V0_2 ?= ready-to-resume
PROJECT_MANAGER_STATUS_SUMMARY_ARTIFACT_DIR ?= /tmp/ai-fantui-project-manager-status-summary
PROJECT_VISIBILITY_MVP_ACCEPTANCE_ARTIFACT_DIR ?= /tmp/ai-fantui-project-visibility-mvp-acceptance
MULTI_AGENT_M1_REVIEW_PACKAGE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m1-review-package
MULTI_AGENT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m2-requirement-to-ir-demo
MULTI_AGENT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m3-safety-evidence-value-pack
MULTI_AGENT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m4-external-review-handoff
MULTI_AGENT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m5-construction-control-plane
MULTI_AGENT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m6-queue-extension-template
MULTI_AGENT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m8-fast-construction-gate
ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR ?= /tmp/ai-fantui-ultrawork-monitor-dashboard
MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-operator-cockpit
MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-packaging-consolidation
MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-pr-preflight
MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-validation-evidence
MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-merge-readiness
M21_STREAMED_AUTHORING_REVISION_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-revision-gate
M21_STREAMED_AUTHORING_MULTISTEP_QUEUE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-multistep-queue-gate
M21_STREAMED_AUTHORING_C919_QUEUE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-queue-gate
M21_STREAMED_AUTHORING_C919_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-raw-intake-gate
M21_STREAMED_AUTHORING_C919_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-real-doc-raw-intake-gate
M21_STREAMED_AUTHORING_C919_CMD3_APWTLA_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate
M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate
M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_THR_IDLE_LOCK_RELEASE_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate
M21_STREAMED_AUTHORING_C919_MLG_WOW_CMD2_CMD3_FANOUT_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate
M21_STREAMED_AUTHORING_DEMO_FANOUT_JUNCTION_GATE_ARTIFACT_DIR ?= /tmp/ai-fantui-m21-streamed-authoring-demo-fanout-junction-gate
CUSTOMER_DEMO_MVP_CLOSEOUT_ARTIFACT_DIR ?= /tmp/ai-fantui-customer-demo-mvp-closeout
PROJECT_OWNER_ACCEPTANCE_REVIEW_PACKET_ARTIFACT_DIR ?= /tmp/ai-fantui-project-owner-acceptance-review-packet
PROJECT_OWNER_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR ?= /tmp/ai-fantui-project-owner-external-review-handoff
PROJECT_OWNER_EXTERNAL_REVIEW_RESULT_PATH ?= /tmp/ai-fantui-project-owner-external-review-handoff/project_owner_external_review_result.json
PROJECT_OWNER_FINAL_DECISION_PACKET_PATH ?= /tmp/ai-fantui-project-owner-external-review-handoff/project-owner-acceptance-review-packet/project_owner_acceptance_review_packet.json
PROJECT_OWNER_FINAL_DECISION_PATH ?= /tmp/ai-fantui-project-owner-external-review-handoff/project_owner_final_decision.json
MULTI_AGENT_M21_STREAMED_LOGIC_AUTHORING_PLAN_ARTIFACT_DIR ?= /tmp/ai-fantui-multi-agent-m21-streamed-logic-authoring-plan

.PHONY: dev test demo-html-reconstruction-mvp demo-html-reconstruction-browser-acceptance review-packet-export-regression first-candidate-repair-slice evidence-candidate-repair-slice missing-test-result-candidate-repair-slice evidence-unknown-requirement-candidate-repair-slice evidence-unknown-trace-candidate-repair-slice safety-transition-endpoint-candidate-repair-slice safety-unreachable-state-candidate-repair-slice safety-output-command-conflict-candidate-repair-slice approved-repair-slices verify-approved-repair-slices-artifact multi-agent-construction-readiness approved-candidate-task-queue verify-approved-candidate-task-queue-artifact verify-approved-candidate-task-queue-expansion-contract approved-candidate-task-queue-v0-2 verify-approved-candidate-task-queue-v0-2-artifact approved-candidate-task-queue-v0-3 verify-approved-candidate-task-queue-v0-3-artifact approved-candidate-task-queue-v0-4 verify-approved-candidate-task-queue-v0-4-artifact approved-candidate-task-queue-v0-5 verify-approved-candidate-task-queue-v0-5-artifact approved-candidate-task-queue-v0-6 verify-approved-candidate-task-queue-v0-6-artifact approved-candidate-task-queue-v0-7 verify-approved-candidate-task-queue-v0-7-artifact approved-candidate-task-queue-v0-8 verify-approved-candidate-task-queue-v0-8-artifact approved-candidate-task-queue-v0-9 verify-approved-candidate-task-queue-v0-9-artifact multi-agent-queue-run-ledger verify-multi-agent-queue-run-ledger multi-agent-queue-cursor-state verify-multi-agent-queue-cursor-state multi-agent-queue-cursor-resume-state verify-multi-agent-queue-cursor-resume-state multi-agent-queue-run-ledger-v0-2 verify-multi-agent-queue-run-ledger-v0-2 multi-agent-queue-cursor-state-v0-2 verify-multi-agent-queue-cursor-state-v0-2 multi-agent-queue-cursor-resume-state-v0-2 verify-multi-agent-queue-cursor-resume-state-v0-2 project-manager-status-summary project-visibility-mvp-gate m21-streamed-authoring-revision-gate m21-streamed-authoring-multistep-queue-gate m21-streamed-authoring-c919-queue-gate m21-streamed-authoring-c919-raw-intake-gate m21-streamed-authoring-c919-real-doc-raw-intake-gate m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate m21-streamed-authoring-demo-fanout-junction-gate customer-demo-mvp-closeout project-owner-acceptance-review-packet project-owner-external-review-handoff project-owner-external-review-result project-owner-final-decision multi-agent-m21-streamed-logic-authoring-plan multi-agent-m1-review-package multi-agent-m2-requirement-to-ir-demo multi-agent-m3-safety-evidence-value-pack multi-agent-m4-external-review-handoff multi-agent-construction-control-plane multi-agent-queue-extension-template multi-agent-fast-construction-gate ultrawork-monitor-dashboard verify-ultrawork-monitor-dashboard multi-agent-operator-cockpit verify-multi-agent-operator-cockpit multi-agent-packaging-consolidation verify-multi-agent-packaging-consolidation multi-agent-pr-preflight verify-multi-agent-pr-preflight multi-agent-validation-evidence verify-multi-agent-validation-evidence multi-agent-merge-readiness verify-multi-agent-merge-readiness help

help:
	@echo "Targets:"
	@echo "  make dev                            — start /workbench dev server (delegates to scripts/dev-serve.sh)"
	@echo "  make demo-html-reconstruction-mvp   — verify old demo.html cockpit reconstruction MVP"
	@echo "  make demo-html-reconstruction-browser-acceptance — capture browser screenshots and interaction evidence for /demo-reconstruction"
	@echo "  make review-packet-export-regression — verify candidate review packet export route"
	@echo "  make first-candidate-repair-slice   — run first approved candidate repair slice"
	@echo "  make evidence-candidate-repair-slice — run approved Evidence candidate repair slice"
	@echo "  make missing-test-result-candidate-repair-slice — run missing test-result Evidence slice"
	@echo "  make evidence-unknown-requirement-candidate-repair-slice — run unknown requirement coverage Evidence slice"
	@echo "  make evidence-unknown-trace-candidate-repair-slice — run unknown requirement IR trace Evidence slice"
	@echo "  make safety-transition-endpoint-candidate-repair-slice — run missing state endpoint Safety slice"
	@echo "  make safety-unreachable-state-candidate-repair-slice — run unreachable state Safety slice"
	@echo "  make safety-output-command-conflict-candidate-repair-slice — run output command conflict Safety slice"
	@echo "  make approved-repair-slices         — run Safety + Evidence approved repair slices"
	@echo "  make verify-approved-repair-slices-artifact — validate approved repair slices CI artifact"
	@echo "  make multi-agent-construction-readiness — emit long-run multi-agent preflight packet"
	@echo "  make approved-candidate-task-queue — run approved candidate tasks behind per-task readiness"
	@echo "  make verify-approved-candidate-task-queue-artifact — validate approved candidate queue CI artifact"
	@echo "  make verify-approved-candidate-task-queue-expansion-contract — validate append-only queue expansion contract"
	@echo "  make approved-candidate-task-queue-v0-2 — run append-only v0.2 approved candidate queue"
	@echo "  make verify-approved-candidate-task-queue-v0-2-artifact — validate v0.2 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-3 — run append-only v0.3 approved candidate queue"
	@echo "  make verify-approved-candidate-task-queue-v0-3-artifact — validate v0.3 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-4 — execute the resumed evidence boundary review queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-4-artifact — validate v0.4 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-5 — append and execute unknown requirement coverage queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-5-artifact — validate v0.5 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-6 — append and execute unknown requirement IR trace queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-6-artifact — validate v0.6 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-7 — append and execute transition endpoint Safety queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-7-artifact — validate v0.7 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-8 — append and execute unreachable state Safety queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-8-artifact — validate v0.8 approved candidate queue CI artifact"
	@echo "  make approved-candidate-task-queue-v0-9 — append and execute output command conflict Safety queue item"
	@echo "  make verify-approved-candidate-task-queue-v0-9-artifact — validate v0.9 approved candidate queue artifact"
	@echo "  make multi-agent-queue-run-ledger — run the v0.8 queue scheduler and validate the run ledger"
	@echo "  make verify-multi-agent-queue-run-ledger — validate the v0.8 queue run ledger CI artifact"
	@echo "  make multi-agent-queue-cursor-state — run the v0.8 queue cursor state and validate resume status"
	@echo "  make verify-multi-agent-queue-cursor-state — validate the v0.8 queue cursor state CI artifact"
	@echo "  make multi-agent-queue-cursor-resume-state — run stale-protected cursor resume state"
	@echo "  make verify-multi-agent-queue-cursor-resume-state — validate stale-protected cursor resume state CI artifact"
	@echo "  make multi-agent-queue-run-ledger-v0-2 — run the v0.9 queue scheduler and validate the v0.2 run ledger"
	@echo "  make verify-multi-agent-queue-run-ledger-v0-2 — validate the v0.2 queue run ledger artifact"
	@echo "  make multi-agent-queue-cursor-state-v0-2 — run the v0.9 queue cursor state and validate idle status"
	@echo "  make verify-multi-agent-queue-cursor-state-v0-2 — validate the v0.2 queue cursor state artifact"
	@echo "  make multi-agent-queue-cursor-resume-state-v0-2 — run v0.9 cursor ready-to-resume state"
	@echo "  make verify-multi-agent-queue-cursor-resume-state-v0-2 — validate v0.9 cursor ready-to-resume state"
	@echo "  make project-manager-status-summary — emit project-owner JSON + Markdown + HTML status artifacts"
	@echo "  make project-visibility-mvp-gate — browser screenshot gate for the Project Visibility MVP entrypoint"
	@echo "  make m21-streamed-authoring-revision-gate — browser screenshot gate for feedback recalculation and requirements patch authorization"
	@echo "  make m21-streamed-authoring-multistep-queue-gate — browser screenshot gate for revised-confirm and next-candidate queue advance"
	@echo "  make m21-streamed-authoring-c919-queue-gate — browser screenshot gate for C919 ETRAS streamed candidate queue generalization"
	@echo "  make m21-streamed-authoring-c919-raw-intake-gate — browser screenshot gate for C919 ETRAS raw text intake into streamed queue"
	@echo "  make m21-streamed-authoring-c919-real-doc-raw-intake-gate — browser screenshot gate for real C919 V0.9 raw intake into streamed queue"
	@echo "  make m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate — browser screenshot gate for real C919 V0.9 CMD3/APWTLA streamed queue"
	@echo "  make m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate — browser screenshot gate for real C919 V0.9 Deploy CMD1 streamed queue"
	@echo "  make m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate — browser screenshot gate for real C919 V0.9 THR idle lock release streamed queue"
	@echo "  make m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate — browser screenshot gate for real C919 V0.9 MLG_WOW CMD2/CMD3 fan-out"
	@echo "  make m21-streamed-authoring-demo-fanout-junction-gate — browser screenshot gate for demo.html fan-out junction dot parity"
	@echo "  make customer-demo-mvp-closeout — combine visibility and Phase 1 demo gates into a closeout packet"
	@echo "  make project-owner-acceptance-review-packet — assemble the final three-option project-owner review packet"
	@echo "  make project-owner-external-review-handoff — generate the read-only external review handoff"
	@echo "  make project-owner-external-review-result — verify a reviewer-returned JSON result"
	@echo "  make project-owner-final-decision — verify the explicit project-owner final decision"
	@echo "  make multi-agent-m21-streamed-logic-authoring-plan — generate and verify the M21 candidate specialist-team plan"
	@echo "  make multi-agent-m1-review-package — generate and validate the M1 external review package"
	@echo "  make multi-agent-m2-requirement-to-ir-demo — generate and validate the M2 Requirement -> IR demo package"
	@echo "  make multi-agent-m3-safety-evidence-value-pack — generate and validate the M3 Safety/Evidence value pack"
	@echo "  make multi-agent-m4-external-review-handoff — generate and validate the M4 external review handoff"
	@echo "  make multi-agent-construction-control-plane — generate and validate the M5 long-running construction control plane"
	@echo "  make multi-agent-queue-extension-template — generate and validate the M6 append-only queue extension template"
	@echo "  make multi-agent-fast-construction-gate — generate and validate the M8 fast per-slice construction gate"
	@echo "  make ultrawork-monitor-dashboard — generate read-only UltraWork Monitor JSON + HTML"
	@echo "  make verify-ultrawork-monitor-dashboard — validate the UltraWork Monitor artifact"
	@echo "  make multi-agent-operator-cockpit — generate read-only M22 operator cockpit JSON + Markdown + HTML"
	@echo "  make verify-multi-agent-operator-cockpit — validate the M22 operator cockpit artifact"
	@echo "  make multi-agent-packaging-consolidation — generate read-only M23 explicit pathspec package"
	@echo "  make verify-multi-agent-packaging-consolidation — validate the M23 pathspec package"
	@echo "  make multi-agent-pr-preflight — generate read-only M24 validation and PR body packet"
	@echo "  make verify-multi-agent-pr-preflight — validate the M24 PR preflight packet"
	@echo "  make multi-agent-validation-evidence — run M24 validation commands and capture M25 evidence"
	@echo "  make verify-multi-agent-validation-evidence — validate the M25 validation evidence packet"
	@echo "  make multi-agent-merge-readiness — emit the M29 PR review and merge-readiness packet"
	@echo "  make verify-multi-agent-merge-readiness — validate the M29 merge-readiness packet"
	@echo "  make test                           — run artifact/browser gates, then full pytest"
	@echo "Override PORT for dev: PORT=9000 make dev"

dev:
	@./scripts/dev-serve.sh

demo-html-reconstruction-mvp:
	@PYTHONPATH=src:. python3 scripts/verify_demo_html_reconstruction_mvp.py --format json

demo-html-reconstruction-browser-acceptance:
	@PYTHONPATH=src:. python3 scripts/verify_demo_html_reconstruction_browser_acceptance.py --format json

review-packet-export-regression:
	@PYTHONPATH=src:. python3 scripts/verify_candidate_review_packet_export.py --format json

first-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_first_candidate_repair_slice.py --format json --artifact-dir "$(FIRST_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

evidence-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_evidence_candidate_repair_slice.py --format json --artifact-dir "$(EVIDENCE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

missing-test-result-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_missing_test_result_candidate_repair_slice.py --format json --artifact-dir "$(MISSING_TEST_RESULT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

evidence-unknown-requirement-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_evidence_unknown_requirement_candidate_repair_slice.py --format json --artifact-dir "$(EVIDENCE_UNKNOWN_REQUIREMENT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

evidence-unknown-trace-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_evidence_unknown_trace_candidate_repair_slice.py --format json --artifact-dir "$(EVIDENCE_UNKNOWN_TRACE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

safety-transition-endpoint-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_safety_transition_endpoint_candidate_repair_slice.py --format json --artifact-dir "$(SAFETY_TRANSITION_ENDPOINT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

safety-unreachable-state-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_safety_unreachable_state_candidate_repair_slice.py --format json --artifact-dir "$(SAFETY_UNREACHABLE_STATE_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

safety-output-command-conflict-candidate-repair-slice:
	@PYTHONPATH=src:. python3 scripts/run_safety_output_command_conflict_candidate_repair_slice.py --format json --artifact-dir "$(SAFETY_OUTPUT_COMMAND_CONFLICT_CANDIDATE_REPAIR_SLICE_ARTIFACT_DIR)"

approved-repair-slices:
	@PYTHONPATH=src:. python3 scripts/run_approved_repair_slices.py --format json --artifact-dir "$(APPROVED_REPAIR_SLICES_ARTIFACT_DIR)"

verify-approved-repair-slices-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_repair_slices.py --format json --artifact-dir "$(APPROVED_REPAIR_SLICES_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_repair_slices_artifact.py --format json --artifact-dir "$(APPROVED_REPAIR_SLICES_ARTIFACT_DIR)"

multi-agent-construction-readiness:
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_construction_readiness.py --format json --artifact-dir "$(MULTI_AGENT_CONSTRUCTION_READINESS_ARTIFACT_DIR)"

approved-candidate-task-queue:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-expansion-contract:
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_expansion_contract.py --format json

approved-candidate-task-queue-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_2.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_2_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-2-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_2.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_2_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_2_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_2_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-3:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_3.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_3_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-3-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_3.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_3_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_3_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_3_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-4:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_4.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_4_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-4-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_4.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_4_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_4_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_4_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-5:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_5.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_5_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-5-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_5.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_5_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_5_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_5_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-6:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_6.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_6_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-6-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_6.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_6_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_6_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_6_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-7:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_7.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_7_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-7-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_7.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_7_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_7_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_7_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-8:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_8.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_8_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-8-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_8.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_8_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_8_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_8_ARTIFACT_DIR)"

approved-candidate-task-queue-v0-9:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_9.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_9_ARTIFACT_DIR)"

verify-approved-candidate-task-queue-v0-9-artifact:
	@PYTHONPATH=src:. python3 scripts/run_approved_candidate_task_queue_v0_9.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_9_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_approved_candidate_task_queue_v0_9_artifact.py --format json --artifact-dir "$(APPROVED_CANDIDATE_TASK_QUEUE_V0_9_ARTIFACT_DIR)"

multi-agent-queue-run-ledger:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_run_ledger.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_run_ledger.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_ARTIFACT_DIR)"

verify-multi-agent-queue-run-ledger:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_run_ledger.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_run_ledger.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_ARTIFACT_DIR)"

multi-agent-queue-cursor-state:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_ARTIFACT_DIR)"

verify-multi-agent-queue-cursor-state:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_ARTIFACT_DIR)"

multi-agent-queue-cursor-resume-state:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state.py --resume-mode "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE)" --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR)"

verify-multi-agent-queue-cursor-resume-state:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state.py --resume-mode "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE)" --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_ARTIFACT_DIR)"

multi-agent-queue-run-ledger-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_run_ledger_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_V0_2_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_run_ledger_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_V0_2_ARTIFACT_DIR)"

verify-multi-agent-queue-run-ledger-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_run_ledger_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_V0_2_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_run_ledger_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_RUN_LEDGER_V0_2_ARTIFACT_DIR)"

multi-agent-queue-cursor-state-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR)"

verify-multi-agent-queue-cursor-state-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_STATE_V0_2_ARTIFACT_DIR)"

multi-agent-queue-cursor-resume-state-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state_v0_2.py --resume-mode "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE_V0_2)" --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_V0_2_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_V0_2_ARTIFACT_DIR)"

verify-multi-agent-queue-cursor-resume-state-v0-2:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_queue_cursor_state_v0_2.py --resume-mode "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_MODE_V0_2)" --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_V0_2_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_queue_cursor_state_v0_2.py --format json --artifact-dir "$(MULTI_AGENT_QUEUE_CURSOR_RESUME_STATE_V0_2_ARTIFACT_DIR)"

project-manager-status-summary:
	@PYTHONPATH=src:. python3 scripts/run_project_manager_status_summary.py --format json --artifact-dir "$(PROJECT_MANAGER_STATUS_SUMMARY_ARTIFACT_DIR)"

project-visibility-mvp-gate:
	@PYTHONPATH=src:. python3 scripts/verify_project_visibility_mvp_acceptance.py --format json --artifact-dir "$(PROJECT_VISIBILITY_MVP_ACCEPTANCE_ARTIFACT_DIR)"

m21-streamed-authoring-revision-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --format json --artifact-dir "$(M21_STREAMED_AUTHORING_REVISION_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-multistep-queue-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --format json --artifact-dir "$(M21_STREAMED_AUTHORING_MULTISTEP_QUEUE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-queue-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_QUEUE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-real-doc-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_real_doc_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_cmd3_apwtla_real_doc_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_CMD3_APWTLA_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_deploy_cmd1_real_doc_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_THR_IDLE_LOCK_RELEASE_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake --format json --artifact-dir "$(M21_STREAMED_AUTHORING_C919_MLG_WOW_CMD2_CMD3_FANOUT_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR)"

m21-streamed-authoring-demo-fanout-junction-gate:
	@PYTHONPATH=src:. python3 scripts/verify_m21_streamed_authoring_revision_browser_gate.py --scenario fantui_demo_fanout_junction --format json --artifact-dir "$(M21_STREAMED_AUTHORING_DEMO_FANOUT_JUNCTION_GATE_ARTIFACT_DIR)"

customer-demo-mvp-closeout:
	@PYTHONPATH=src:. python3 scripts/run_customer_demo_mvp_closeout.py --format json --artifact-dir "$(CUSTOMER_DEMO_MVP_CLOSEOUT_ARTIFACT_DIR)"

project-owner-acceptance-review-packet:
	@PYTHONPATH=src:. python3 scripts/run_project_owner_acceptance_review_packet.py --format json --artifact-dir "$(PROJECT_OWNER_ACCEPTANCE_REVIEW_PACKET_ARTIFACT_DIR)"

project-owner-external-review-handoff:
	@PYTHONPATH=src:. python3 scripts/run_project_owner_external_review_handoff.py --format json --artifact-dir "$(PROJECT_OWNER_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR)"

project-owner-external-review-result:
	@PYTHONPATH=src:. python3 scripts/verify_project_owner_external_review_result.py --format json --handoff "$(PROJECT_OWNER_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR)/project_owner_external_review_handoff.json" --review "$(PROJECT_OWNER_EXTERNAL_REVIEW_RESULT_PATH)"

project-owner-final-decision:
	@PYTHONPATH=src:. python3 scripts/verify_project_owner_final_decision.py --format json --packet "$(PROJECT_OWNER_FINAL_DECISION_PACKET_PATH)" --decision "$(PROJECT_OWNER_FINAL_DECISION_PATH)" --handoff "$(PROJECT_OWNER_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR)/project_owner_external_review_handoff.json" --review "$(PROJECT_OWNER_EXTERNAL_REVIEW_RESULT_PATH)"

multi-agent-m21-streamed-logic-authoring-plan:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m21_streamed_logic_authoring_plan.py --format json --artifact-dir "$(MULTI_AGENT_M21_STREAMED_LOGIC_AUTHORING_PLAN_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m21_streamed_logic_authoring_plan.py --format json --package "$(MULTI_AGENT_M21_STREAMED_LOGIC_AUTHORING_PLAN_ARTIFACT_DIR)/multi_agent_m21_streamed_logic_authoring_plan_v0_1.json"

multi-agent-m1-review-package:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m1_review_package.py --format json --artifact-dir "$(MULTI_AGENT_M1_REVIEW_PACKAGE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m1_review_package.py --format json --package "$(MULTI_AGENT_M1_REVIEW_PACKAGE_ARTIFACT_DIR)/multi_agent_m1_review_package_v0_1.json"

multi-agent-m2-requirement-to-ir-demo:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m2_requirement_to_ir_demo.py --format json --artifact-dir "$(MULTI_AGENT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m2_requirement_to_ir_demo.py --format json --package "$(MULTI_AGENT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR)/multi_agent_m2_requirement_to_ir_demo_v0_1.json"

multi-agent-m3-safety-evidence-value-pack:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m3_safety_evidence_value_pack.py --format json --artifact-dir "$(MULTI_AGENT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m3_safety_evidence_value_pack.py --format json --package "$(MULTI_AGENT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR)/multi_agent_m3_safety_evidence_value_pack_v0_1.json"

multi-agent-m4-external-review-handoff:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m4_external_review_handoff.py --format json --artifact-dir "$(MULTI_AGENT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m4_external_review_handoff.py --format json --package "$(MULTI_AGENT_M4_EXTERNAL_REVIEW_HANDOFF_ARTIFACT_DIR)/multi_agent_m4_external_review_handoff_v0_1.json"

multi-agent-construction-control-plane:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m5_construction_control_plane.py --format json --artifact-dir "$(MULTI_AGENT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m5_construction_control_plane.py --format json --package "$(MULTI_AGENT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR)/multi_agent_m5_construction_control_plane_v0_1.json"

multi-agent-queue-extension-template:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m6_queue_extension_template.py --format json --artifact-dir "$(MULTI_AGENT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m6_queue_extension_template.py --format json --package "$(MULTI_AGENT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR)/multi_agent_m6_queue_extension_template_v0_1.json"

multi-agent-fast-construction-gate:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_m8_fast_construction_gate.py --format json --artifact-dir "$(MULTI_AGENT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR)"
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_m8_fast_construction_gate.py --format json --package "$(MULTI_AGENT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR)/multi_agent_m8_fast_construction_gate_v0_1.json"

ultrawork-monitor-dashboard:
	@PYTHONPATH=src:. python3 scripts/run_ultrawork_monitor_dashboard.py --resume-mode ready-to-resume --format json --artifact-dir "$(ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR)/ultrawork_monitor_dashboard_v0_1.html"

verify-ultrawork-monitor-dashboard:
	@PYTHONPATH=src:. python3 scripts/run_ultrawork_monitor_dashboard.py --resume-mode ready-to-resume --format json --artifact-dir "$(ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_ultrawork_monitor_dashboard.py --format json --artifact-dir "$(ULTRAWORK_MONITOR_DASHBOARD_ARTIFACT_DIR)"

multi-agent-operator-cockpit:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_operator_cockpit.py --format json --artifact-dir "$(MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR)/multi_agent_operator_cockpit_v0_1.html"

verify-multi-agent-operator-cockpit:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_operator_cockpit.py --format json --artifact-dir "$(MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_operator_cockpit.py --format json --artifact-dir "$(MULTI_AGENT_OPERATOR_COCKPIT_ARTIFACT_DIR)"

multi-agent-packaging-consolidation:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_packaging_consolidation.py --format json --artifact-dir "$(MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR)/multi_agent_packaging_consolidation_v0_1.html"

verify-multi-agent-packaging-consolidation:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_packaging_consolidation.py --format json --artifact-dir "$(MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_packaging_consolidation.py --format json --artifact-dir "$(MULTI_AGENT_PACKAGING_CONSOLIDATION_ARTIFACT_DIR)"

multi-agent-pr-preflight:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_pr_preflight.py --format json --artifact-dir "$(MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR)/multi_agent_pr_preflight_v0_1.html"

verify-multi-agent-pr-preflight:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_pr_preflight.py --format json --artifact-dir "$(MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_pr_preflight.py --format json --artifact-dir "$(MULTI_AGENT_PR_PREFLIGHT_ARTIFACT_DIR)"

multi-agent-validation-evidence:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_validation_evidence.py --format json --artifact-dir "$(MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR)/multi_agent_validation_evidence_v0_1.html"

verify-multi-agent-validation-evidence:
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_validation_evidence.py --format json --artifact-dir "$(MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR)"

multi-agent-merge-readiness:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_validation_evidence.py --format json --artifact-dir "$(MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_merge_readiness.py --format json --artifact-dir "$(MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR)"
	@printf 'Open: %s\n' "$(MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR)/multi_agent_merge_readiness_v0_1.html"

verify-multi-agent-merge-readiness:
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_validation_evidence.py --format json --artifact-dir "$(MULTI_AGENT_VALIDATION_EVIDENCE_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/run_multi_agent_merge_readiness.py --format json --artifact-dir "$(MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR)" >/dev/null
	@PYTHONPATH=src:. python3 scripts/verify_multi_agent_merge_readiness.py --format json --artifact-dir "$(MULTI_AGENT_MERGE_READINESS_ARTIFACT_DIR)"

test: review-packet-export-regression verify-approved-repair-slices-artifact verify-approved-candidate-task-queue-artifact verify-approved-candidate-task-queue-expansion-contract verify-approved-candidate-task-queue-v0-2-artifact verify-approved-candidate-task-queue-v0-3-artifact verify-approved-candidate-task-queue-v0-4-artifact verify-approved-candidate-task-queue-v0-5-artifact verify-approved-candidate-task-queue-v0-6-artifact verify-approved-candidate-task-queue-v0-7-artifact verify-approved-candidate-task-queue-v0-8-artifact verify-approved-candidate-task-queue-v0-9-artifact verify-multi-agent-queue-run-ledger verify-multi-agent-queue-cursor-state verify-multi-agent-queue-cursor-resume-state verify-multi-agent-queue-run-ledger-v0-2 verify-multi-agent-queue-cursor-state-v0-2 verify-multi-agent-queue-cursor-resume-state-v0-2 multi-agent-m1-review-package multi-agent-m2-requirement-to-ir-demo multi-agent-m3-safety-evidence-value-pack multi-agent-m4-external-review-handoff multi-agent-construction-control-plane multi-agent-queue-extension-template multi-agent-fast-construction-gate
	@PYTHONPATH=src python3 -m pytest tests/

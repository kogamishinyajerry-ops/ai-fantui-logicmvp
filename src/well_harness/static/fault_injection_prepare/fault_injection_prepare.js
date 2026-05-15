(function () {
  "use strict";

  const REQUIREMENTS_KEY = "ai-fantui-requirements-intake-ready-v1";
  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const HISTORY_KEY = "ai-fantui-logic-builder-change-history-v1";
  const FAULT_DRAFT_KEY = "ai-fantui-fault-injection-preparation-v1";
  const SANDBOX_PLAN_KEY = "ai-fantui-fault-injection-sandbox-plan-v1";
  const state = {
    requirementsPayload: null,
    drawingPayload: null,
    changeHistory: [],
    faultPayload: null,
    timer: null,
    startedAt: 0,
    percent: 0,
    busy: false,
    activeFaultMatrixSelection: null,
  };
  const FAULT_SANDBOX_REVIEW_LINKS = [
    {reviewRowId: "SR-06", traceId: "ET-04", reportId: "RP-06", label: "报告可追溯"},
    {reviewRowId: "SR-04", traceId: "ET-02", reportId: "RP-05", label: "故障覆盖"},
    {reviewRowId: "SR-05", traceId: "ET-04", reportId: "RP-01", label: "回放输入"},
  ];

  const $ = (id) => document.getElementById(id);
  const provider = $("fault-provider");
  const generateButton = $("fault-generate");
  const sandboxNextButton = $("fault-sandbox-next");
  const sandboxGate = $("fault-sandbox-gate");
  const backButton = $("fault-back");
  const process = $("fault-process");
  const processTitle = $("fault-process-title");
  const processElapsed = $("fault-process-elapsed");
  const processFill = $("fault-process-fill");
  const processDetail = $("fault-process-detail");
  const steps = {
    load: $("fault-step-load"),
    model: $("fault-step-model"),
    candidates: $("fault-step-candidates"),
    boundary: $("fault-step-boundary"),
  };
  const streamChunks = $("fault-stream-chunks");
  const STREAM_CHUNK_COPY = {
    load: "已读取图纸：载入需求与链路",
    model: "DeepSeek 正在准备：生成故障候选",
    candidates: "整理候选：场景与注入点已返回",
    boundary: "边界确认：等待工程师收口",
  };
  const workflowStage = $("fault-injection-workflow-stage");
  const workflowDetail = $("fault-injection-workflow-detail");
  const workflowSteps = Array.from(document.querySelectorAll("#fault-workflow-steps .fault-workflow-step"));
  const sourceTitle = $("fault-source-title");
  const sourceSummary = $("fault-source-summary");
  const sourceMetrics = $("fault-source-metrics");
  const resultState = $("fault-result-state");
  const resultSummary = $("fault-result-summary");
  const resultFlags = $("fault-result-flags");
  const qualitySummary = $("fault-quality-summary");
  const sourceDefer = $("fault-source-defer");
  const sourceDeferSummary = $("fault-source-defer-summary");
  const blueprintCandidateActions = $("fault-blueprint-candidate-actions");
  const blueprintCandidateButton = $("fault-load-blueprint-candidate");
  const blueprintCandidateStatus = $("fault-blueprint-candidate-status");
  const burdenAction = $("fault-burden-action");
  const burdenOutputs = $("fault-burden-outputs");
  const faultDecisionCandidateSummary = $("fault-decision-candidate-summary");
  const faultDecisionBoundarySummary = $("fault-decision-boundary-summary");
  const faultDecisionNextAction = $("fault-decision-next-action");
  const repairDetails = $("fault-repair-details");
  const repairSummary = $("fault-repair-summary");
  const repairBody = $("fault-repair-body");
  const coverageEvidence = $("fault-coverage-evidence");
  const coverageEvidenceList = $("fault-coverage-evidence-list");
  const workflowNotes = $("fault-workflow-notes");
  const scenarioCount = $("fault-scenario-count");
  const scenarioChips = $("fault-scenario-chips");
  const scenarioCards = $("fault-scenario-card-list");
  const pointCount = $("fault-point-count");
  const pointChips = $("fault-point-map");
  const pointCards = $("fault-point-card-list");
  const faultCandidateMatrixCount = $("fault-candidate-matrix-count");
  const faultCandidateMatrixBody = $("fault-candidate-matrix-body");
  const boundaryProgress = $("fault-boundary-progress");
  const boundaryList = $("fault-boundary-list");
  const saveBoundariesButton = $("fault-save-boundaries");
  const saveState = $("fault-save-state");
  const contextPopover = $("fault-context-popover");
  const contextTitle = $("fault-context-title");
  const contextBody = $("fault-context-body");
  const contextClose = $("fault-context-close");
  const faultShell = document.querySelector(".fault-shell");

  function escapeText(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function sourceAnchorLabel(anchors) {
    if (!Array.isArray(anchors) || anchors.length === 0) return "模型假设";
    return anchors
      .slice(0, 2)
      .map((anchor) => `${anchor.id || "DOCX"} · ${anchor.kind || "正文条件"}`)
      .join(" / ");
  }

  function setFaultDecisionCandidateSummary(text) {
    if (faultDecisionCandidateSummary) faultDecisionCandidateSummary.textContent = text || "等待候选";
  }

  function setFaultDecisionBoundarySummary(text) {
    if (faultDecisionBoundarySummary) faultDecisionBoundarySummary.textContent = text || "0/0 已回答";
  }

  function setFaultDecisionNextAction(text) {
    if (!faultDecisionNextAction) return;
    const value = text || "等待候选";
    const pathCueByState = {
      "等待候选": "等待候选：生成后得到故障矩阵与沙盒入口。",
      "默认暂缓": "默认暂缓：源文档暂不要求故障注入，仅保留 dry-run 入口。",
      "模型处理中": "模型处理中：完成后会刷新故障矩阵与沙盒入口。",
      "需重新生成边界问题": "需重新生成边界问题：边界齐全后才能进入沙盒。",
      "需完成边界确认": "需完成边界确认：确认后把候选矩阵送入沙盒。",
      "可进入沙盒": "可进入沙盒：候选矩阵将带入审查行、证据链和报告预览。",
    };
    faultDecisionNextAction.textContent = pathCueByState[value] || value;
  }

  function isFaultDeferredBySource() {
    const requirementScope = state.requirementsPayload && state.requirementsPayload.source_scope;
    const draftScope = state.faultPayload && state.faultPayload.source_scope;
    return Boolean(
      (requirementScope && requirementScope.fault_injection && requirementScope.fault_injection.status === "source_deferred") ||
      (draftScope && draftScope.fault_injection && draftScope.fault_injection.status === "source_deferred") ||
      (state.faultPayload && state.faultPayload.status === "source_deferred")
    );
  }

  function faultDeferredReason() {
    const requirementScope = state.requirementsPayload && state.requirementsPayload.source_scope;
    const draftScope = state.faultPayload && state.faultPayload.source_scope;
    const deferred = (requirementScope && requirementScope.fault_injection) || (draftScope && draftScope.fault_injection);
    return deferred && deferred.reason_zh ? deferred.reason_zh : "源文档声明故障注入本轮暂不考虑。";
  }

  function sourceDeferredAnchors() {
    const requirementScope = state.requirementsPayload && state.requirementsPayload.source_scope;
    const draftScope = state.faultPayload && state.faultPayload.source_scope;
    const deferred = (requirementScope && requirementScope.fault_injection) || (draftScope && draftScope.fault_injection);
    return Array.isArray(deferred && deferred.source_anchors) ? deferred.source_anchors : [];
  }

  function blueprintPreviewSourceAnchors() {
    return [
      {
        id: "BP-FI-01",
        kind: "UI 蓝图",
        origin: "selected-final-set",
        quote_zh: "首次进入时加载本地 candidate-only 故障预览；不代表源文档要求故障注入。",
        requirement_level: "candidate-preview",
        confidence: "ui_blueprint",
      },
    ];
  }

  function isSourceDeferredFaultPayload(payload) {
    const scope = payload && payload.source_scope;
    return Boolean(
      payload && (
        payload.status === "source_deferred" ||
        (scope && scope.fault_injection && scope.fault_injection.status === "source_deferred")
      )
    );
  }

  function isDocxTemplateDrawing() {
    const drawing = state.drawingPayload || {};
    return Boolean(
      drawing.source_requirements_sha256 === "local-docx-l1-l4-template" ||
      (drawing.llm && drawing.llm.model === "docx-l1-l4-template")
    );
  }

  function templatePreviewSourceAnchors() {
    const drawing = state.drawingPayload || {};
    const nodes = Array.isArray(drawing.nodes) ? drawing.nodes : [];
    const anchors = [];
    nodes.forEach((node) => {
      if (!Array.isArray(node.source_anchors)) return;
      node.source_anchors.forEach((anchor) => {
        if (anchor && anchors.length < 4) anchors.push(anchor);
      });
    });
    if (anchors.length) return anchors;
    return [
      {
        id: "DOCX-L1-L4",
        kind: "DOCX 模板",
        origin: "logic-builder-template-entry",
        quote_zh: "从逻辑绘制页载入的本地 DOCX L1-L4 模板候选。",
        requirement_level: "candidate-template",
        confidence: "local_template",
      },
    ];
  }

  function drawingNodes() {
    const drawing = state.drawingPayload || {};
    const nodes = [];
    if (Array.isArray(drawing.nodes)) nodes.push(...drawing.nodes);
    const circuitNodes = drawing.circuit_view && Array.isArray(drawing.circuit_view.nodes)
      ? drawing.circuit_view.nodes
      : [];
    nodes.push(...circuitNodes);
    return nodes.filter((node) => node && node.id);
  }

  function pickDrawingNode(preferredIds, preferredKind) {
    const nodes = drawingNodes();
    for (const id of preferredIds) {
      const match = nodes.find((node) => node.id === id || node.linked_node_id === id);
      if (match) return match;
    }
    const kindMatch = nodes.find((node) => {
      const kind = node.node_kind || node.circuit_role || "";
      return preferredKind && String(kind).includes(preferredKind);
    });
    return kindMatch || nodes[0] || {};
  }

  function candidateAnchorsFor(node) {
    const anchors = Array.isArray(node && node.source_anchors) ? node.source_anchors : [];
    const deferredAnchors = sourceDeferredAnchors();
    if (anchors.length) return anchors.slice(0, 3);
    if (deferredAnchors.length) return deferredAnchors;
    return blueprintPreviewSourceAnchors();
  }

  function buildBlueprintFaultCandidate() {
    const raNode = pickDrawingNode(["radio_altitude_ft", "ra_lt_6ft", "RA", "input_ra"], "input");
    const swNode = pickDrawingNode(["sw1", "sw2"], "input");
    const outputNode = pickDrawingNode(["thr_lock", "thr_lock_rel", "output_unlock"], "output");
    const sourceScope = state.requirementsPayload && state.requirementsPayload.source_scope
      ? state.requirementsPayload.source_scope
      : {};
    const raId = raNode.id || "radio_altitude_ft";
    const swId = swNode.id || "sw1";
    const outputId = outputNode.id || "thr_lock";
    return {
      "$schema": "https://well-harness.local/json_schema/requirements_fault_injection_preparation_v1.schema.json",
      kind: "ai-fantui-fault-injection-preparation",
      version: 1,
      status: "needs_user_confirmation",
      truth_effect: "none",
      candidate_state: "fault_injection_preparation",
      certification_claim: "none",
      controller_truth_modified: false,
      ui_blueprint_preview: true,
      source_scope: sourceScope,
      source_requirements_sha256: "ui-blueprint-preview",
      source_drawing_sha256: "ui-blueprint-preview",
      source_change_history_sha256: "ui-blueprint-preview",
      summary_zh: "蓝图候选演示已载入：仅用于验证故障注入与沙盒审查 UI，不修改控制器真值。",
      fault_scenarios: [
        {
          id: "blueprint_fault_ra_low",
          label: "RA 低值卡滞候选",
          node_id: raId,
          fault_type: "sensor_stuck_low",
          severity: "medium",
          rationale_zh: "用于检查 RA 门限异常时，下游释放门和油门锁路径是否仍可追溯。",
          expected_effect_zh: "沙盒中只观察路径影响，不触发真实 tick 或控制器写入。",
          observable_signals: [raId, outputId],
          source_anchors: candidateAnchorsFor(raNode),
          provenance: "ui_blueprint_candidate_preview",
        },
        {
          id: "blueprint_fault_sw_path",
          label: "SW 路径间歇候选",
          node_id: swId,
          fault_type: "intermittent_signal",
          severity: "medium",
          rationale_zh: "用于验证开关输入路径、证据回链和审查清单在候选态下可读。",
          expected_effect_zh: "沙盒报告中回链到开关输入、观测点和人工审查行。",
          observable_signals: [swId, outputId],
          source_anchors: candidateAnchorsFor(swNode),
          provenance: "ui_blueprint_candidate_preview",
        },
      ],
      injection_points: [
        {
          id: "blueprint_inject_ra",
          node_id: raId,
          signal_name: "radio_altitude_ft",
          injection_mode: "override",
          safe_boundary_zh: "仅 dry-run 观察，RA 值限制在 0 到 20 ft，不进入真实控制。",
          constraint_zh: "truth_effect:none；controller_truth_modified:false。",
          priority: "P1",
          source_anchors: candidateAnchorsFor(raNode),
        },
        {
          id: "blueprint_inject_sw",
          node_id: swId,
          signal_name: "switch_path",
          injection_mode: "toggle_sequence",
          safe_boundary_zh: "仅用于路径高亮和审查回链，不写入控制器。",
          constraint_zh: "candidate-only sandbox review。",
          priority: "P2",
          source_anchors: candidateAnchorsFor(swNode),
        },
      ],
      boundary_questions: [
        {
          id: "blueprint_confirm_dry_run",
          prompt_zh: "确认此候选只用于 dry-run 沙盒审查？",
          rationale_zh: "蓝图验收需要保留故障注入入口，但不能触发真实控制执行。",
          blocks: "fault_injection",
        },
        {
          id: "blueprint_confirm_truth_boundary",
          prompt_zh: "确认不修改 controller truth、认证结论和生产配置？",
          rationale_zh: "所有输出保持 sandbox candidate，不进入适航或生产声明。",
          blocks: "fault_injection",
        },
      ],
      boundary_answers: [
        {
          id: "blueprint_confirm_dry_run",
          prompt_zh: "确认此候选只用于 dry-run 沙盒审查？",
          answer_zh: "确认仅用于 dry-run UI 验收。",
        },
        {
          id: "blueprint_confirm_truth_boundary",
          prompt_zh: "确认不修改 controller truth、认证结论和生产配置？",
          answer_zh: "确认不修改控制器真值和认证结论。",
        },
      ],
      coverage_completion: {
        strategy: "ui_blueprint_candidate_preview",
        completed_node_ids: [raId, swId],
        semantic_gate: "critical_node_coverage",
      },
      workflow_notes: [
        "源文档暂缓仍然保留；该候选仅用于演示蓝图 UI 的故障注入能力。",
        "进入沙盒后只呈现 dry-run 计划、观测点、审查行和证据回链。",
      ],
      llm: {
        provider: "local-ui",
        model: "blueprint-candidate-preview",
      },
    };
  }

  function buildBlueprintSandboxCandidate(faultPayload) {
    const scenarios = Array.isArray(faultPayload.fault_scenarios) ? faultPayload.fault_scenarios : [];
    const injectionPoints = Array.isArray(faultPayload.injection_points) ? faultPayload.injection_points : [];
    const firstScenario = scenarios[0] || {};
    const secondScenario = scenarios[1] || firstScenario;
    const firstPoint = injectionPoints[0] || {};
    const secondPoint = injectionPoints[1] || firstPoint;
    return {
      "$schema": "https://well-harness.local/json_schema/requirements_fault_injection_sandbox_plan_v1.schema.json",
      kind: "ai-fantui-fault-injection-sandbox-plan",
      version: 1,
      status: "ready_for_review",
      truth_effect: "none",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      controller_truth_modified: false,
      ui_blueprint_preview: true,
      first_visit_preview: Boolean(faultPayload.first_visit_preview),
      source_fault_injection_preparation_sha256: "ui-blueprint-preview",
      source_boundary_answers_sha256: "ui-blueprint-preview",
      summary_zh: "蓝图候选沙盒计划已载入：只读 dry-run 审查，不运行真实 tick。",
      execution_contract: {
        run_tick: false,
        simulate: false,
        dry_run_only: true,
      },
      sandbox_injection_plan: [
        {
          id: "blueprint_plan_ra_override",
          fault_scenario_id: firstScenario.id || "blueprint_fault_ra_low",
          node_id: firstScenario.node_id || firstPoint.node_id || "radio_altitude_ft",
          signal_name: firstPoint.signal_name || "radio_altitude_ft",
          injection_mode: firstPoint.injection_mode || "override",
          safe_range_zh: "0 到 20 ft，仅 UI dry-run。",
          expected_effect_zh: "检查 RA 候选异常是否只在沙盒证据链中呈现。",
          source_anchors: firstScenario.source_anchors || [],
        },
        {
          id: "blueprint_plan_sw_toggle",
          fault_scenario_id: secondScenario.id || "blueprint_fault_sw_path",
          node_id: secondScenario.node_id || secondPoint.node_id || "sw1",
          signal_name: secondPoint.signal_name || "switch_path",
          injection_mode: secondPoint.injection_mode || "toggle_sequence",
          safe_range_zh: "仅生成审查回放，不写入控制器。",
          expected_effect_zh: "高亮开关路径、观测点和人工审查行之间的回链。",
          source_anchors: secondScenario.source_anchors || [],
        },
      ],
      observation_points: [
        {
          id: "blueprint_observe_release_gate",
          node_id: firstScenario.node_id || "radio_altitude_ft",
          signal_name: "release_gate",
          check_zh: "确认候选异常不会绕过 TRA、SW1/SW2、VDT 与地面状态约束。",
          source_anchors: firstScenario.source_anchors || [],
        },
        {
          id: "blueprint_observe_thr_lock",
          node_id: "thr_lock",
          signal_name: "thr_lock",
          check_zh: "确认油门锁状态只作为沙盒观测输出，不生成真实控制动作。",
          source_anchors: secondScenario.source_anchors || [],
        },
      ],
      review_checklist: [
        {
          id: "blueprint_review_dry_run",
          category: "dry_run",
          condition_zh: "确认执行合同保持 run_tick:false、simulate:false、dry_run_only:true。",
          pass_criteria_zh: "审查页仅显示候选证据，不触发真实仿真 tick。",
          source_anchors: firstScenario.source_anchors || [],
        },
        {
          id: "blueprint_review_trace",
          category: "traceability",
          condition_zh: "确认计划、观测点和审查行可回链到候选节点和来源。",
          pass_criteria_zh: "点击计划、观测点、审查条目可打开证据详情。",
          source_anchors: secondScenario.source_anchors || [],
        },
      ],
      plan_coverage_completion: {
        strategy: "ui_blueprint_candidate_preview",
        completed_fault_scenario_ids: scenarios.map((item) => item.id).filter(Boolean),
        semantic_gate: "scenario_plan_coverage",
      },
      workflow_notes: [
        "该沙盒计划由前端蓝图候选演示生成，保持 candidate-only。",
        "用于验收故障注入、沙盒审查、证据追溯和报告预览 UI。",
      ],
      llm: {
        provider: "local-ui",
        model: "blueprint-candidate-preview",
      },
    };
  }

  function renderBlueprintCandidatePreview(options) {
    const opts = options || {};
    beginTask(opts.title || "载入蓝图候选", opts.detail || "正在构造 candidate-only 故障与沙盒演示草稿。");
    const faultPayload = buildBlueprintFaultCandidate();
    if (opts.firstVisit) {
      faultPayload.first_visit_preview = true;
      faultPayload.summary_zh = "首次进入已载入本地蓝图候选预览：仅用于看懂故障矩阵、边界确认和沙盒入口，不修改控制器真值。";
      faultPayload.source_scope = {
        fault_injection: {
          status: "ui_blueprint_preview",
          reason_zh: "没有已保存图纸时显示本地蓝图候选预览，作为 UI 工作台空态。",
          source_anchors: blueprintPreviewSourceAnchors(),
        },
      };
    }
    if (opts.templateDrawing) {
      faultPayload.template_preview = true;
      faultPayload.summary_zh = "DOCX L1-L4 模板候选已接入故障矩阵：仅用于查看故障准备和沙盒入口，不修改控制器真值。";
      faultPayload.source_scope = {
        fault_injection: {
          status: "ui_template_preview",
          reason_zh: "来自逻辑绘制页的 DOCX L1-L4 模板候选，作为本地 candidate-only 演示路径。",
          source_anchors: templatePreviewSourceAnchors(),
        },
      };
      faultPayload.source_drawing_sha256 = (
        state.drawingPayload && state.drawingPayload.source_requirements_sha256
      ) || "local-docx-l1-l4-template";
      faultPayload.workflow_notes = [
        "DOCX L1-L4 模板从逻辑绘制页进入故障矩阵；不调用模型和控制器。",
        "进入沙盒后只呈现 dry-run 计划、证据链、审查行和报告预览。",
      ];
    }
    const sandboxPayload = buildBlueprintSandboxCandidate(faultPayload);
    if (opts.templateDrawing) {
      sandboxPayload.template_preview = true;
      sandboxPayload.summary_zh = "DOCX L1-L4 模板候选沙盒计划已载入：只读 dry-run 审查，不运行真实 tick。";
      sandboxPayload.source_fault_injection_preparation_sha256 = "local-docx-l1-l4-template";
      sandboxPayload.plan_coverage_completion = {
        ...(sandboxPayload.plan_coverage_completion || {}),
        strategy: "ui_template_preview",
      };
      sandboxPayload.workflow_notes = [
        "该沙盒计划由逻辑绘制页 DOCX 模板候选生成，保持 candidate-only。",
        "用于验收故障矩阵、沙盒审查、证据追溯和报告预览 UI。",
      ];
    }
    setProgress(84, "候选已构造", "正在渲染故障场景、注入点和覆盖证据。", "candidates");
    window.localStorage.setItem(SANDBOX_PLAN_KEY, JSON.stringify(sandboxPayload));
    renderFaultPayload(faultPayload);
    if (opts.firstVisit || opts.templateDrawing) {
      renderSource();
    }
    saveFaultDraft();
    setProgress(96, "边界已确认", "蓝图候选已预填 dry-run 边界，可进入沙盒审查。", "boundary");
    finishTask(opts.finishTitle || "蓝图候选已载入", opts.finishDetail || "已写入本地 candidate-only 草稿；源文档暂缓状态仍保留。");
    if (blueprintCandidateStatus) {
      blueprintCandidateStatus.textContent = opts.statusText || "已载入 sandbox candidate，不改变源文档范围";
    }
  }

  function loadBlueprintCandidateDemo() {
    renderBlueprintCandidatePreview();
  }

  function loadFirstVisitBlueprintCandidatePreview() {
    renderBlueprintCandidatePreview({
      firstVisit: true,
      title: "载入首次候选预览",
      detail: "未发现已保存图纸；正在载入本地 candidate-only 蓝图预览。",
      finishTitle: "首次候选预览已载入",
      finishDetail: "默认展示故障矩阵、边界确认和沙盒入口；未调用模型或控制器。",
      statusText: "首次进入已载入 sandbox candidate，不改变源文档范围",
    });
  }

  function loadTemplateDrawingBlueprintCandidatePreview() {
    renderBlueprintCandidatePreview({
      templateDrawing: true,
      title: "载入 DOCX 模板候选",
      detail: "已发现逻辑绘制页 DOCX L1-L4 模板；正在构造 candidate-only 故障矩阵与沙盒入口。",
      finishTitle: "DOCX 模板候选已接入",
      finishDetail: "已基于本地模板候选生成故障矩阵、边界确认和沙盒入口；未调用模型或控制器。",
      statusText: "DOCX L1-L4 模板已接入 sandbox candidate，不改变控制真值",
    });
  }

  function formatElapsed(ms) {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    return `${String(Math.floor(totalSeconds / 60)).padStart(2, "0")}:${String(totalSeconds % 60).padStart(2, "0")}`;
  }

  function safeUiError(payload, fallback) {
    if (payload && payload.error === "missing_api_key") {
      return "模型密钥未读取，请检查服务端环境变量后重试。";
    }
    if (payload && payload.details && payload.details.self_repair) {
      return "模型输出仍不完整，请重新生成或切换模型。";
    }
    return fallback;
  }

  function clearChildren(element) {
    if (element) element.innerHTML = "";
  }

  function setActiveAuxPanel(name) {
    const panelName = name || "none";
    if (faultShell) {
      faultShell.dataset.activeAuxPanel = panelName;
      faultShell.dataset.unifiedInspectorState = panelName;
    }
    if (contextPopover) {
      contextPopover.dataset.unifiedPanelState = panelName === "fault-context-popover" ? "open" : "closed";
    }
  }

  function normalizeText(value) {
    return (value == null || value === "") ? "未提供" : value;
  }

  function compactCell(value, fallback) {
    const normalized = normalizeText(value || fallback).replace(/\s+/g, " ").trim();
    return normalized.length > 68 ? `${normalized.slice(0, 65)}...` : normalized;
  }

  function faultRiskLabel(severity) {
    const normalized = String(severity || "medium").toLowerCase();
    if (normalized === "high") return "高";
    if (normalized === "low") return "低";
    return "中";
  }

  function faultCoveredPathLabel(scenario, point) {
    return faultCoveredPathItems(scenario, point).join(" -> ") || "待确认路径";
  }

  function faultCoveredPathItems(scenario, point) {
    const coveredPath = Array.isArray(scenario && scenario.covered_path)
      ? scenario.covered_path.filter(Boolean)
      : [];
    if (coveredPath.length) return coveredPath.slice(0, 4);
    const signals = Array.isArray(scenario && scenario.observable_signals)
      ? scenario.observable_signals.filter(Boolean)
      : [];
    if (signals.length) return signals.slice(0, 4);
    const nodeId = point && point.node_id ? point.node_id : (scenario && scenario.node_id);
    const signal = point && point.signal_name ? point.signal_name : "";
    return [nodeId, signal].filter(Boolean);
  }

  function renderFaultPathTokens(items) {
    const pathItems = items && items.length ? items : ["待确认路径"];
    return pathItems.map((item, index) => `
      <span class="fault-matrix-path-token blueprint-row-token" data-path-index="${index + 1}">${escapeText(compactCell(item, "路径"))}</span>
    `).join('<span class="fault-matrix-path-arrow" aria-hidden="true">→</span>');
  }

  function faultMatrixEvidenceToken(scenario, point, index) {
    const scenarioAnchors = Array.isArray(scenario && scenario.source_anchors) ? scenario.source_anchors : [];
    const pointAnchors = Array.isArray(point && point.source_anchors) ? point.source_anchors : [];
    const anchor = scenarioAnchors[0] || pointAnchors[0] || {};
    return anchor.id || `SRC-${String(index + 1).padStart(2, "0")}`;
  }

  function faultSandboxLinkForMatrixRow(index) {
    return FAULT_SANDBOX_REVIEW_LINKS[index % FAULT_SANDBOX_REVIEW_LINKS.length];
  }

  function applyFaultMatrixSelectionState() {
    const activeRowId = state.activeFaultMatrixSelection ? state.activeFaultMatrixSelection.rowId : "";
    if (!faultCandidateMatrixBody) return;
    Array.from(faultCandidateMatrixBody.querySelectorAll("[data-fault-matrix-row]")).forEach((row) => {
      const isActive = row.dataset.faultMatrixRow === activeRowId;
      row.classList.toggle("is-linked-active", isActive);
      row.setAttribute("aria-selected", isActive ? "true" : "false");
    });
  }

  function setActiveFaultMatrixSelection(selection) {
    state.activeFaultMatrixSelection = selection || null;
    applyFaultMatrixSelectionState();
  }

  function renderFaultMatrixLinkSummary(selection) {
    if (!selection) return null;
    const shell = document.createElement("div");
    shell.id = "fault-context-link-summary";
    shell.className = "fault-context-link-summary";
    shell.setAttribute("data-active-fault-row", selection.rowId || "none");
    shell.setAttribute("data-active-review-row", selection.reviewRowId || "none");
    shell.setAttribute("data-active-trace-id", selection.traceId || "none");
    shell.setAttribute("data-active-report-id", selection.reportId || "none");
    shell.innerHTML = `
      <span class="fault-context-link-label">沙盒预选</span>
      <code data-link-summary-kind="review">${escapeText(selection.reviewRowId)}</code>
      <code data-link-summary-kind="trace">${escapeText(selection.traceId)}</code>
      <code data-link-summary-kind="report">${escapeText(selection.reportId)}</code>
      <span class="fault-context-link-note">${escapeText(selection.label || "审查联动")}</span>
      <span class="fault-context-link-boundary">sandbox_candidate</span>
      <span class="fault-context-link-boundary">truth_effect:none</span>
      <span class="fault-context-link-boundary">controller_truth_modified:false</span>
    `;
    return shell;
  }

  function renderContextContent(title, rows, linkSummary) {
    contextTitle.textContent = title || "详情";
    contextBody.innerHTML = "";
    const summary = renderFaultMatrixLinkSummary(linkSummary);
    if (summary) contextBody.appendChild(summary);
    if (!rows.length) {
      const para = document.createElement("p");
      para.className = "muted";
      para.textContent = "当前项未包含详细字段。";
      contextBody.appendChild(para);
    } else {
      const dl = document.createElement("dl");
      rows.forEach((row) => {
        const dt = document.createElement("dt");
        dt.textContent = row.label;
        const dd = document.createElement("dd");
        dd.textContent = row.value;
        dl.appendChild(dt);
        dl.appendChild(dd);
      });
      contextBody.appendChild(dl);
    }
    contextPopover.removeAttribute("aria-hidden");
    contextPopover.hidden = false;
    setActiveAuxPanel("fault-context-popover");
  }

  function closeContextPopover() {
    contextPopover.setAttribute("aria-hidden", "true");
    contextPopover.hidden = true;
    setActiveAuxPanel("none");
  }

  function buildContextFromScenario(item, index) {
    const signals = Array.isArray(item.observable_signals) ? item.observable_signals : [];
    const rows = [
      {label: "场景", value: normalizeText(item.label || item.id)},
      {label: "节点", value: normalizeText(item.node_id)},
      {label: "故障类型", value: normalizeText(item.fault_type)},
      {label: "严重度", value: normalizeText(item.severity || "medium")},
      {label: "序号", value: String(index + 1)},
      {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
      {label: "可观测信号", value: signals.length ? signals.map((signal) => normalizeText(signal)).join("；") : "未提供"},
      {label: "期望影响", value: normalizeText(item.expected_effect_zh)},
      {label: "模型理由", value: normalizeText(item.rationale_zh)},
      {label: "边界安全", value: normalizeText(item.safe_boundary_zh)},
    ];
    return rows;
  }

  function buildContextFromPoint(item, index) {
    return [
      {label: "注入点", value: normalizeText(item.label || item.id || index + 1)},
      {label: "节点", value: normalizeText(item.node_id)},
      {label: "信号", value: normalizeText(item.signal_name)},
      {label: "方式", value: normalizeText(item.injection_mode)},
      {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
      {label: "安全边界", value: normalizeText(item.safe_boundary_zh)},
      {label: "约束", value: normalizeText(item.constraint_zh)},
      {label: "优先级", value: normalizeText(item.priority)},
    ];
  }

  function openContextForScenario(item, index) {
    return () => {
      renderContextContent(`故障场景上下文：${normalizeText(item.label || item.id)}`, buildContextFromScenario(item, index));
    };
  }

  function openContextForPoint(item, index) {
    return () => {
      renderContextContent(`注入点上下文：${normalizeText(item.label || item.node_id || item.id || index + 1)}`, buildContextFromPoint(item, index));
    };
  }

  function loadJSON(key, fallback) {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    try {
      const payload = JSON.parse(raw);
      return payload == null ? fallback : payload;
    } catch (error) {
      return fallback;
    }
  }

  function loadFaultSourcePayload() {
    state.requirementsPayload = loadJSON(REQUIREMENTS_KEY, null);
    state.drawingPayload = loadJSON(DRAWING_KEY, null);
    const history = loadJSON(HISTORY_KEY, []);
    state.changeHistory = Array.isArray(history) ? history : [];
    return Boolean(state.requirementsPayload && state.drawingPayload);
  }

  function loadFaultDraft() {
    const draft = loadJSON(FAULT_DRAFT_KEY, null);
    return draft && typeof draft === "object" ? draft : null;
  }

  function saveFaultDraft(extra) {
    if (!state.faultPayload) return;
    const draft = {
      ...state.faultPayload,
      boundary_answers: collectBoundaryAnswers(),
      saved_at: new Date().toISOString(),
      ...(extra || {}),
    };
    window.localStorage.setItem(FAULT_DRAFT_KEY, JSON.stringify(draft));
    saveState.textContent = "已保存";
    updateSandboxGate();
  }

  function setStep(activeStep) {
    const names = Object.keys(steps);
    Object.entries(steps).forEach(([name, element]) => {
      const isComplete = names.indexOf(name) < names.indexOf(activeStep);
      element.classList.toggle("is-active", name === activeStep);
      element.classList.toggle("is-complete", isComplete);
      element.dataset.state = name === activeStep ? "active" : (isComplete ? "complete" : "idle");
    });
  }

  function resetStreamChunks() {
    if (streamChunks) streamChunks.innerHTML = "";
  }

  function appendStreamChunk(name, text, stateName) {
    if (!streamChunks || !name) return;
    let chunk = streamChunks.querySelector(`[data-stream-chunk="${name}"]`);
    if (!chunk) {
      chunk = document.createElement("span");
      chunk.className = "stream-chunk";
      chunk.dataset.streamChunk = name;
      streamChunks.appendChild(chunk);
    }
    chunk.dataset.state = stateName || "active";
    chunk.textContent = text || name;
  }

  function syncStreamChunks(activeStep) {
    const names = Object.keys(steps);
    const activeIndex = names.indexOf(activeStep);
    if (activeIndex < 0) return;
    names.forEach((name, index) => {
      if (index > activeIndex) return;
      appendStreamChunk(name, STREAM_CHUNK_COPY[name], index === activeIndex ? "active" : "complete");
    });
  }

  function markStreamChunksFailed() {
    if (!streamChunks) return;
    streamChunks.querySelectorAll(".stream-chunk").forEach((chunk) => {
      if (chunk.dataset.state === "active") chunk.dataset.state = "error";
    });
  }

  function setProgress(percent, title, detail, activeStep) {
    state.percent = Math.max(state.percent, percent);
    process.classList.remove("is-complete", "is-error");
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processFill.style.width = `${Math.min(state.percent, 96)}%`;
    setStep(activeStep);
    syncStreamChunks(activeStep);
  }

  function beginTask(title, detail) {
    clearInterval(state.timer);
    resetStreamChunks();
    state.startedAt = Date.now();
    state.percent = 6;
    processElapsed.textContent = "00:00";
    setProgress(6, title, detail, "load");
    state.timer = setInterval(() => {
      processElapsed.textContent = formatElapsed(Date.now() - state.startedAt);
      if (state.percent < 84) {
        state.percent += state.percent < 36 ? 2.4 : 0.7;
        processFill.style.width = `${Math.min(state.percent, 84)}%`;
      }
    }, 500);
  }

  function finishTask(title, detail) {
    clearInterval(state.timer);
    state.timer = null;
    state.percent = 100;
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processElapsed.textContent = formatElapsed(Date.now() - state.startedAt);
    processFill.style.width = "100%";
    process.classList.add("is-complete");
    process.classList.remove("is-error");
    Object.values(steps).forEach((element) => {
      element.classList.remove("is-active");
      element.classList.add("is-complete");
      element.dataset.state = "complete";
    });
  }

  function failTask(title, detail) {
    clearInterval(state.timer);
    state.timer = null;
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processElapsed.textContent = state.startedAt ? formatElapsed(Date.now() - state.startedAt) : "00:00";
    process.classList.add("is-error");
    process.classList.remove("is-complete");
    Object.values(steps).forEach((element) => {
      if (element.classList.contains("is-active")) element.dataset.state = "error";
    });
    markStreamChunksFailed();
  }

  function setBusy(isBusy) {
    state.busy = isBusy;
    provider.disabled = isBusy;
    generateButton.disabled = isBusy || !state.requirementsPayload || !state.drawingPayload;
    saveBoundariesButton.disabled = isBusy || !state.faultPayload;
    if (blueprintCandidateButton) {
      blueprintCandidateButton.disabled = isBusy || !isFaultDeferredBySource();
    }
    generateButton.textContent = isBusy
      ? "生成中..."
      : (isFaultDeferredBySource() && !state.faultPayload ? "检查：生成 dry-run 候选" : "检查：生成候选");
    updateSandboxGate();
  }

  function setWorkflowSteps(activeStep, completedSteps) {
    workflowSteps.forEach((element) => {
      const step = element.dataset.workflowStep || "";
      element.classList.toggle("is-active", step === activeStep);
      element.classList.toggle("is-complete", completedSteps.includes(step));
      element.classList.toggle("is-locked", !completedSteps.includes(step) && step !== activeStep);
    });
  }

  function getBoundaryCompletion() {
    const inputs = Array.from(boundaryList.querySelectorAll("textarea[data-boundary-id]"));
    const total = inputs.length;
    const answered = inputs.filter((input) => input.value.trim()).length;
    return {
      total,
      answered,
      isComplete: Boolean(state.faultPayload && total > 0 && answered === total),
    };
  }

  function updateSandboxGate() {
    const boundaryState = getBoundaryCompletion();
    let nextText = "等待候选";
    let isBlocked = true;
    if (state.busy) {
      nextText = "模型处理中";
    } else if (!state.faultPayload) {
      nextText = isFaultDeferredBySource() ? "默认暂缓" : "等待候选";
    } else if (!boundaryState.total) {
      nextText = "需重新生成边界问题";
    } else if (!boundaryState.isComplete) {
      nextText = "需完成边界确认";
    } else {
      nextText = "可进入沙盒";
      isBlocked = false;
    }
    sandboxNextButton.disabled = isBlocked;
    sandboxNextButton.title = nextText;
    sandboxGate.textContent = nextText;
    sandboxGate.classList.toggle("is-ready", !isBlocked);
    setFaultDecisionNextAction(nextText);
  }

  function renderWorkflowOverview() {
    if (state.faultPayload && state.faultPayload.template_preview) {
      workflowStage.textContent = "DOCX 模板候选";
      workflowDetail.textContent = "来自逻辑绘制页的 DOCX L1-L4 模板；当前已生成 candidate-only 故障矩阵和沙盒入口。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    if (state.faultPayload && state.faultPayload.first_visit_preview) {
      workflowStage.textContent = "蓝图候选预览";
      workflowDetail.textContent = "未发现已保存图纸，当前显示本地 candidate-only 故障矩阵和沙盒入口。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    if (state.drawingPayload && !state.requirementsPayload) {
      workflowStage.textContent = isDocxTemplateDrawing() ? "DOCX 模板候选" : "本地图纸候选";
      workflowDetail.textContent = isDocxTemplateDrawing()
        ? "已载入逻辑绘制页 DOCX L1-L4 模板，可生成本地 candidate-only 故障矩阵和沙盒入口。"
        : "已载入本地逻辑图纸；如需模型重算，请先回到需求理解页载入原需求。";
      setWorkflowSteps("drawing", ["requirements"]);
      return;
    }
    if (!state.requirementsPayload || !state.drawingPayload) {
      workflowStage.textContent = "等待逻辑图纸";
      workflowDetail.textContent = "先完成需求澄清和初版逻辑绘制，再让模型准备故障候选。";
      setWorkflowSteps("drawing", ["requirements"]);
      return;
    }
    if (state.faultPayload) {
      workflowStage.textContent = "等待边界确认";
      workflowDetail.textContent = "模型已生成故障场景和注入点候选；请确认边界后再进入沙盒注入。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    if (isFaultDeferredBySource()) {
      workflowStage.textContent = "故障注入默认暂缓";
      workflowDetail.textContent = "源文档声明本轮暂不考虑故障注入；只有点击“仍生成 dry-run 候选”才会继续。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    workflowStage.textContent = "准备生成故障候选";
    workflowDetail.textContent = "已载入需求和逻辑图纸，模型将输出候选故障、注入点和边界问题。";
    setWorkflowSteps("fault", ["requirements", "drawing"]);
  }

  function renderSource() {
    if (state.drawingPayload && !state.requirementsPayload) {
      const drawing = state.drawingPayload || {};
      sourceTitle.textContent = isDocxTemplateDrawing() ? "DOCX L1-L4 模板候选" : "本地逻辑图纸";
      sourceSummary.textContent = isDocxTemplateDrawing()
        ? "来自逻辑绘制页的 DOCX L1-L4 本地候选；不会调用模型、tick 或控制器真值。"
        : (drawing.summary_zh || "已读取本地保存的模型图纸；缺少需求 payload 时仅保持候选态展示。");
      sourceMetrics.textContent = `${(drawing.nodes || []).length} nodes · ${(drawing.edges || []).length} edges · ${(drawing.parameter_panels || []).length} panels`;
      renderSourceDeferral();
      renderBurdenSummary(state.faultPayload);
      return;
    }
    if (!state.requirementsPayload || !state.drawingPayload) {
      sourceTitle.textContent = state.faultPayload && state.faultPayload.first_visit_preview ? "蓝图候选预览" : "尚未载入";
      sourceSummary.textContent = state.faultPayload && state.faultPayload.first_visit_preview
        ? "首次进入空态使用本地 candidate-only 预览；不会调用模型、tick 或控制器真值。"
        : "需要先从逻辑绘制页生成图纸。";
      sourceMetrics.textContent = state.faultPayload && state.faultPayload.first_visit_preview
        ? "2 scenarios · 2 points · dry-run"
        : "0 nodes · 0 edges · 0 panels";
      renderSourceDeferral();
      renderBurdenSummary(state.faultPayload);
      return;
    }
    const req = state.requirementsPayload || {};
    const drawing = state.drawingPayload || {};
    const doc = req.source_document || {};
    sourceTitle.textContent = doc.name || "已载入逻辑图纸";
    sourceSummary.textContent = req.summary_zh || drawing.summary_zh || "已读取本地保存的模型图纸。";
    sourceMetrics.textContent = `${(drawing.nodes || []).length} nodes · ${(drawing.edges || []).length} edges · ${(drawing.parameter_panels || []).length} panels`;
    renderSourceDeferral();
    renderBurdenSummary(state.faultPayload);
  }

  function renderSourceDeferral() {
    if (!isFaultDeferredBySource()) {
      sourceDefer.hidden = true;
      if (blueprintCandidateActions) blueprintCandidateActions.hidden = true;
      return;
    }
    sourceDefer.hidden = false;
    if (blueprintCandidateActions) blueprintCandidateActions.hidden = false;
    sourceDeferSummary.textContent = `${faultDeferredReason()} 默认停在可选扩展，不自动生成候选。`;
  }

  function renderBurdenSummary(payload) {
    if (isFaultDeferredBySource() && !payload) {
      burdenAction.textContent = "当前只需决定是否保持暂缓。";
      burdenOutputs.innerHTML = "<li>源文档暂缓故障注入</li><li>默认不进入沙盒</li><li>可手动生成 dry-run 候选</li>";
      setFaultDecisionCandidateSummary("源文档暂缓");
      setFaultDecisionBoundarySummary("0/0 已回答");
      return;
    }
    if (!payload) {
      burdenAction.textContent = "先确认是否需要生成故障候选。";
      burdenOutputs.innerHTML = "<li>本页关键输出限制为场景、注入点、边界 3 类。</li>";
      setFaultDecisionCandidateSummary("等待候选");
      setFaultDecisionBoundarySummary("0/0 已回答");
      return;
    }
    const scenarios = Array.isArray(payload.fault_scenarios) ? payload.fault_scenarios.length : 0;
    const points = Array.isArray(payload.injection_points) ? payload.injection_points.length : 0;
    const questions = Array.isArray(payload.boundary_questions) ? payload.boundary_questions.length : 0;
    const answers = Array.isArray(payload.boundary_answers) ? payload.boundary_answers.filter((item) => item && item.answer_zh).length : 0;
    burdenAction.textContent = "先确认边界问题；场景和注入点折叠为参考。";
    burdenOutputs.innerHTML = [`${scenarios} 个故障场景`, `${points} 个注入点`, `${questions} 个边界问题`]
      .map((item) => `<li>${escapeText(item)}</li>`)
      .join("");
    setFaultDecisionCandidateSummary(`${scenarios} scenarios · ${points} points`);
    setFaultDecisionBoundarySummary(`${Math.min(answers, questions)}/${questions} 已回答`);
  }

  function renderFlags(payload) {
    resultFlags.innerHTML = "";
    const repair = payload.llm && payload.llm.self_repair;
    const flags = [
      payload.controller_truth_modified ? "需复核控制逻辑" : "未改控制逻辑",
      "故障候选",
      payload.certification_claim && payload.certification_claim !== "none" ? "含认证声明" : "无认证声明",
      (payload.llm && payload.llm.provider === "minimax") ? "MiniMax" : "DeepSeek",
    ];
    if (repair) {
      flags.push(repair.success ? "已自动整理" : "需重新生成");
    }
    if (payload.coverage_completion) {
      flags.push("自动补齐覆盖");
    }
    for (const flag of flags) {
      const span = document.createElement("span");
      span.textContent = flag;
      resultFlags.appendChild(span);
    }
  }

  function findSelfRepair(payload) {
    if (!payload || typeof payload !== "object") return null;
    if (payload.llm && payload.llm.self_repair) return payload.llm.self_repair;
    if (payload.details && payload.details.self_repair) return payload.details.self_repair;
    return null;
  }

  function addRepairRow(label, value) {
    if (value == null || value === "") return;
    const row = document.createElement("div");
    row.className = "fault-repair-row";
    const key = document.createElement("span");
    key.textContent = label;
    const val = document.createElement("code");
    val.textContent = String(value);
    row.append(key, val);
    repairBody.appendChild(row);
  }

  function renderSelfRepairDetails(payload) {
    const repair = findSelfRepair(payload);
    repairBody.innerHTML = "";
    if (!repair) {
      repairDetails.hidden = true;
      repairSummary.textContent = "模型自修复详情";
      return;
    }
    repairDetails.hidden = false;
    repairSummary.textContent = repair.success ? "模型输出已自动整理" : "模型输出需要重新生成";
    addRepairRow("处理状态", repair.success ? "已整理为可读结果" : "整理失败");
    addRepairRow("处理方式", repair.attempted ? "模型自动重试一次" : "未触发自动重试");
    if (!repair.success) addRepairRow("下一步", "重新生成或切换模型");
  }

  function addCoverageRow(label, value) {
    if (value == null || value === "") return;
    const row = document.createElement("div");
    row.className = "fault-coverage-row";
    const key = document.createElement("span");
    key.textContent = label;
    const val = document.createElement("code");
    val.textContent = String(value);
    row.append(key, val);
    coverageEvidenceList.appendChild(row);
  }

  function renderCoverageCompletionEvidence(payload) {
    const completion = payload && payload.coverage_completion;
    const completedNodeIds = Array.isArray(completion && completion.completed_node_ids)
      ? completion.completed_node_ids.filter(Boolean)
      : [];
    coverageEvidenceList.innerHTML = "";
    if (!completion || !completedNodeIds.length) {
      coverageEvidence.hidden = true;
      return;
    }
    coverageEvidence.hidden = false;
    addCoverageRow("补齐策略", completion.strategy || "deterministic_dry_run_candidate");
    addCoverageRow("补齐节点", completedNodeIds.join(", "));
    addCoverageRow("语义门", completion.semantic_gate || "critical_node_coverage");
  }

  function renderQualitySummary(payload) {
    const drawingNodes = Array.isArray(state.drawingPayload && state.drawingPayload.nodes)
      ? state.drawingPayload.nodes
      : [];
    const panels = Array.isArray(state.drawingPayload && state.drawingPayload.parameter_panels)
      ? state.drawingPayload.parameter_panels
      : [];
    const criticalNodes = new Set();
    drawingNodes.forEach((node) => {
      if (!node || !node.id) return;
      if (node.node_kind === "input" || node.node_kind === "output") criticalNodes.add(node.id);
    });
    panels.forEach((panel) => {
      if (panel && panel.node_id) criticalNodes.add(panel.node_id);
    });
    const scenarios = Array.isArray(payload.fault_scenarios) ? payload.fault_scenarios : [];
    const injectionPoints = Array.isArray(payload.injection_points) ? payload.injection_points : [];
    const coveredNodes = new Set();
    scenarios.forEach((item) => {
      if (item && item.node_id) coveredNodes.add(item.node_id);
    });
    injectionPoints.forEach((item) => {
      if (item && item.node_id) coveredNodes.add(item.node_id);
    });
    const coveredCritical = Array.from(criticalNodes).filter((nodeId) => coveredNodes.has(nodeId)).length;
    if (criticalNodes.size) {
      qualitySummary.textContent = `已覆盖 ${coveredCritical}/${criticalNodes.size} 个关键节点 · ${scenarios.length} 个故障场景 · ${injectionPoints.length} 个注入点 · 等待边界确认`;
      return;
    }
    qualitySummary.textContent = `已生成 ${scenarios.length} 个故障场景 · ${injectionPoints.length} 个注入点 · 等待边界确认`;
  }

  function renderFaultCandidateMatrix(payload) {
    const scenarios = Array.isArray(payload && payload.fault_scenarios) ? payload.fault_scenarios : [];
    const points = Array.isArray(payload && payload.injection_points) ? payload.injection_points : [];
    const rowCount = Math.max(scenarios.length, points.length);
    const previousRowId = state.activeFaultMatrixSelection ? state.activeFaultMatrixSelection.rowId : "";
    state.activeFaultMatrixSelection = null;
    if (faultCandidateMatrixCount) faultCandidateMatrixCount.textContent = `${rowCount} rows`;
    if (!faultCandidateMatrixBody) return;
    faultCandidateMatrixBody.innerHTML = "";
    if (!rowCount) {
      const row = document.createElement("tr");
      row.innerHTML = '<td colspan="9" class="fault-candidate-matrix-empty">暂无候选。等待模型或蓝图候选演示。</td>';
      faultCandidateMatrixBody.appendChild(row);
      return;
    }
    for (let index = 0; index < rowCount; index += 1) {
      const scenario = scenarios[index] || scenarios[0] || {};
      const point = points[index] || points[0] || {};
      const rowId = scenario.id || point.id || `fault_row_${index + 1}`;
      const risk = faultRiskLabel(scenario.severity);
      const coveredPathItems = faultCoveredPathItems(scenario, point);
      const coveredPathLabel = faultCoveredPathLabel(scenario, point);
      const evidenceToken = faultMatrixEvidenceToken(scenario, point, index);
      const sandboxLink = faultSandboxLinkForMatrixRow(index);
      const selection = {
        rowId,
        reviewRowId: sandboxLink.reviewRowId,
        traceId: sandboxLink.traceId,
        reportId: sandboxLink.reportId,
        label: sandboxLink.label,
      };
      const row = document.createElement("tr");
      row.className = "blueprint-row blueprint-row--fault-matrix blueprint-density-row";
      row.tabIndex = 0;
      row.setAttribute("aria-selected", "false");
      row.setAttribute("data-fault-matrix-row", rowId);
      row.setAttribute("data-blueprint-fault-row", "matrix");
      row.setAttribute("data-blueprint33-row", "fault-matrix");
      row.setAttribute("data-linked-review-row", sandboxLink.reviewRowId);
      row.setAttribute("data-linked-trace-id", sandboxLink.traceId);
      row.setAttribute("data-linked-report-id", sandboxLink.reportId);
      row.dataset.blueprintDensity = "compact-workbench";
      row.dataset.blueprintRowPattern = "shared-v1";
      row.dataset.blueprintRowRhythm = "checkbox-id-path-risk_state";
      row.dataset.blueprintColumns = "checkbox id injection-position fault-type trigger expected-effect covered-path risk state";
      row.dataset.rowScanKind = "fault-matrix";
      row.dataset.rowScanContract = "id-status-evidence-link";
      row.dataset.rowScanEvidence = evidenceToken;
      row.dataset.risk = risk;
      row.innerHTML = `
        <td class="fault-matrix-select" data-blueprint-col="checkbox"><input type="checkbox" aria-label="选择 ${escapeText(rowId)}" checked disabled></td>
        <td class="fault-matrix-id" data-blueprint-col="id"><code class="blueprint-row-token" data-row-scan-token="id">${escapeText(rowId)}</code></td>
        <td class="fault-matrix-injection-cell" data-blueprint-col="injection-position">
          <strong>${escapeText(compactCell(point.node_id || scenario.node_id, "待确认节点"))}</strong>
          <small>${escapeText(compactCell(point.signal_name, "signal"))}</small>
          <span class="fault-matrix-evidence-token blueprint-row-token" data-row-scan-token="evidence" aria-label="来源证据 ${escapeText(evidenceToken)}">${escapeText(evidenceToken)}</span>
        </td>
        <td class="fault-matrix-type" data-blueprint-col="fault-type"><span class="fault-matrix-type-pill blueprint-row-chip">${escapeText(compactCell(scenario.fault_type || point.injection_mode, "fault"))}</span></td>
        <td class="fault-matrix-trigger" data-blueprint-col="trigger"><span>${escapeText(compactCell(point.safe_boundary_zh || scenario.rationale_zh, "dry-run 条件待确认"))}</span></td>
        <td class="fault-matrix-effect" data-blueprint-col="expected-effect"><span>${escapeText(compactCell(scenario.expected_effect_zh, "观察路径影响"))}</span></td>
        <td class="fault-matrix-path" data-blueprint-col="covered-path">
          <span class="fault-matrix-path-summary blueprint-row-token" data-row-scan-token="path-summary">${escapeText(coveredPathItems.length ? `${coveredPathItems.length} 节点路径` : "路径待确认")}</span>
          <span class="fault-matrix-pathline blueprint-row-linkbar" data-blueprint39-detail="selected-only" data-row-scan-token="link" aria-label="${escapeText(coveredPathLabel)}">${renderFaultPathTokens(coveredPathItems)}</span>
        </td>
        <td class="fault-matrix-hazard-cell" data-blueprint-col="risk"><span class="fault-matrix-risk blueprint-row-chip" data-risk="${escapeText(risk)}">${escapeText(risk)}</span></td>
        <td class="fault-matrix-status-cell" data-blueprint-col="state"><span class="fault-matrix-status blueprint-row-chip" data-row-scan-token="status">已选</span></td>
      `;
      const openRowContext = () => {
        setActiveFaultMatrixSelection(selection);
        const rows = [
          ...(scenario.id ? buildContextFromScenario(scenario, index) : []),
          ...(point.id ? buildContextFromPoint(point, index) : []),
          {label: "沙盒审查行", value: sandboxLink.reviewRowId},
          {label: "证据追踪", value: sandboxLink.traceId},
          {label: "报告章节", value: sandboxLink.reportId},
        ];
        renderContextContent(`故障矩阵：${rowId}`, rows, selection);
      };
      row.addEventListener("click", openRowContext);
      row.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openRowContext();
        }
      });
      faultCandidateMatrixBody.appendChild(row);
      if (previousRowId === rowId) {
        state.activeFaultMatrixSelection = selection;
      }
    }
    applyFaultMatrixSelectionState();
  }

  function renderFaultScenarios(payload) {
    const items = payload.fault_scenarios || [];
    scenarioCount.textContent = `${items.length} scenarios`;
    clearChildren(scenarioChips);
    clearChildren(scenarioCards);
    if (!items.length) {
      scenarioCards.innerHTML = '<p class="muted">模型未返回故障场景候选。</p>';
      scenarioChips.textContent = "暂无候选";
      return;
    }
    items.forEach((item, index) => {
      const card = document.createElement("article");
      card.className = "fault-scenario-card";
      card.dataset.severity = item.severity || "medium";
      const signals = Array.isArray(item.observable_signals) ? item.observable_signals : [];
      card.innerHTML = `
        <div class="fault-scenario-head">
          <div>
            <strong>${escapeText(item.label || item.id)}</strong>
            <code>${escapeText(item.node_id || "node:none")} · ${escapeText(item.fault_type || "fault")}</code>
          </div>
          <span class="fault-scenario-severity">${escapeText(item.severity || "medium")}</span>
        </div>
        <p>${escapeText(item.rationale_zh || "模型未返回选择理由。")}</p>
        <p>${escapeText(item.expected_effect_zh || "模型未返回预期影响。")}</p>
        <p class="fault-anchor">来源：${escapeText(sourceAnchorLabel(item.source_anchors))}</p>
        <div class="fault-scenario-meta">
          ${signals.map((signal) => `<code>${escapeText(signal)}</code>`).join("")}
        </div>
      `;
      card.addEventListener("click", openContextForScenario(item, index));
      scenarioCards.appendChild(card);

      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "fault-scenario-chip";
      chip.textContent = `${item.label || item.id} · ${item.node_id || "node"} · ${item.fault_type || "fault"}`;
      chip.title = item.rationale_zh || "点击查看场景上下文";
      chip.addEventListener("click", openContextForScenario(item, index));
      scenarioChips.appendChild(chip);
    });
  }

  function renderInjectionPoints(payload) {
    const items = payload.injection_points || [];
    pointCount.textContent = `${items.length} points`;
    clearChildren(pointChips);
    clearChildren(pointCards);
    if (!items.length) {
      pointChips.textContent = "暂无注入点";
      pointCards.innerHTML = '<p class="muted">模型未返回建议注入点。</p>';
      return;
    }
    items.forEach((item, index) => {
      const chip = document.createElement("button");
      chip.className = "fault-point-chip";
      chip.type = "button";
      chip.textContent = `${item.node_id || "node"} · ${item.signal_name || "signal"} · ${item.injection_mode || "mode"}`;
      chip.title = item.safe_boundary_zh || "";
      chip.addEventListener("click", openContextForPoint(item, index));
      pointChips.appendChild(chip);

      const card = document.createElement("article");
      card.className = "fault-point-card";
      const titleText = `${item.node_id || "node"} · ${item.signal_name || "signal"}`;
      const modeText = item.injection_mode || "mode";
      const rationaleText = item.safe_boundary_zh || "未返回安全边界";
      card.innerHTML = `
        <div class="fault-point-head">
          <strong>${escapeText(titleText)}</strong>
          <code>${escapeText(modeText)}</code>
        </div>
        <p>${escapeText(rationaleText)}</p>
        <p class="fault-anchor">来源：${escapeText(sourceAnchorLabel(item.source_anchors))}</p>
      `;
      card.addEventListener("click", openContextForPoint(item, index));
      pointCards.appendChild(card);
    });
  }

  function collectBoundaryAnswers() {
    return Array.from(boundaryList.querySelectorAll("textarea[data-boundary-id]"))
      .map((input) => ({
        id: input.dataset.boundaryId || "",
        prompt_zh: input.dataset.boundaryPrompt || "",
        answer_zh: input.value.trim(),
      }))
      .filter((item) => item.answer_zh);
  }

  function updateBoundaryProgress() {
    const boundaryState = getBoundaryCompletion();
    boundaryProgress.textContent = `${boundaryState.answered}/${boundaryState.total} 已回答`;
    setFaultDecisionBoundarySummary(boundaryProgress.textContent);
    saveState.textContent = boundaryState.answered ? "有未保存回答" : "未保存";
    updateSandboxGate();
  }

  function renderBoundaryConfirmations(payload) {
    const items = payload.boundary_questions || [];
    const existingAnswers = new Map((payload.boundary_answers || []).map((item) => [item.id, item.answer_zh || ""]));
    boundaryList.innerHTML = "";
    if (!items.length) {
      boundaryProgress.textContent = "0/0 已回答";
      setFaultDecisionBoundarySummary("0/0 已回答");
      boundaryList.innerHTML = '<p class="muted">模型未返回边界确认问题。</p>';
      updateSandboxGate();
      return;
    }
    for (const item of items) {
      const article = document.createElement("article");
      article.className = "fault-boundary-item";
      const id = item.id || item.prompt_zh || "boundary";
      article.innerHTML = `
        <label>
          <strong>${escapeText(item.prompt_zh || id)}</strong>
          <p>${escapeText(item.rationale_zh || "该边界会影响后续沙盒注入范围。")}</p>
          <textarea data-boundary-id="${escapeText(id)}" data-boundary-prompt="${escapeText(item.prompt_zh || id)}" placeholder="在这里输入边界确认或限制条件。">${escapeText(existingAnswers.get(id) || "")}</textarea>
        </label>
      `;
      boundaryList.appendChild(article);
    }
    boundaryList.querySelectorAll("textarea[data-boundary-id]").forEach((input) => {
      input.addEventListener("input", updateBoundaryProgress);
    });
    updateBoundaryProgress();
  }

  function renderWorkflowNotes(payload) {
    const items = payload.workflow_notes || [];
    workflowNotes.innerHTML = "";
    if (!items.length) {
      workflowNotes.innerHTML = '<li class="muted">模型未返回后续说明。</li>';
      return;
    }
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      workflowNotes.appendChild(li);
    }
  }

  function renderFaultPayload(payload) {
    state.faultPayload = payload;
    if (isSourceDeferredFaultPayload(payload) && !(payload.fault_scenarios || []).length) {
      resultState.textContent = "源文档暂缓";
      resultSummary.textContent = payload.summary_zh || faultDeferredReason();
    } else {
      resultState.textContent = "候选已生成";
      resultSummary.textContent = payload.summary_zh || "模型已生成故障注入准备候选。";
    }
    renderFlags(payload);
    renderQualitySummary(payload);
    renderSelfRepairDetails(payload);
    renderCoverageCompletionEvidence(payload);
    renderFaultCandidateMatrix(payload);
    renderFaultScenarios(payload);
    renderInjectionPoints(payload);
    renderBoundaryConfirmations(payload);
    renderWorkflowNotes(payload);
    renderSourceDeferral();
    renderBurdenSummary(payload);
    renderWorkflowOverview();
    setBusy(false);
  }

  async function requestFaultInjection() {
    const response = await fetch("/api/requirements-intake/prepare-fault-injection", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: provider.value,
        allow_fallback: provider.value !== "deepseek",
        requirements_payload: state.requirementsPayload,
        drawing_payload: state.drawingPayload,
        change_history: state.changeHistory,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "故障候选生成失败，请重新生成或切换模型。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function generateFaultPreparation() {
    if (!state.requirementsPayload || !state.drawingPayload) {
      failTask("缺少逻辑图纸", "请先回到逻辑绘制页生成模型图纸。");
      return;
    }
    beginTask("读取逻辑图纸", "正在读取已澄清需求、模型图纸和修改历史。");
    setBusy(true);
    try {
      setProgress(28, "提交模型", "正在让模型基于当前图纸生成故障场景候选和注入点。", "model");
      const payload = await requestFaultInjection();
      setProgress(84, "生成候选", "模型已返回故障候选，正在整理场景和边界问题。", "candidates");
      renderFaultPayload(payload);
      saveFaultDraft({boundary_answers: []});
      setProgress(96, "边界确认", "故障候选已准备好，等待工程师确认注入边界。", "boundary");
      finishTask("故障准备完成", "模型已生成故障场景、注入点和边界确认问题。");
    } catch (error) {
      resultState.textContent = "生成失败";
      const message = error.message || "故障候选生成失败，请重新生成或切换模型。";
      resultSummary.textContent = message;
      renderSelfRepairDetails(error.payload);
      failTask("生成失败", message);
    } finally {
      setBusy(false);
    }
  }

  function goBackToLogicBuilder() {
    window.location.href = "/logic-builder";
  }

  function boot() {
    const hasSource = loadFaultSourcePayload();
    const hasTemplateDrawing = Boolean(state.drawingPayload && !state.requirementsPayload && isDocxTemplateDrawing());
    renderSource();
    renderWorkflowOverview();
    const draft = loadFaultDraft();
    if (draft) {
      beginTask("载入故障草稿", "正在读取上次保存的故障注入准备结果。");
      renderFaultPayload(draft);
      finishTask("已载入故障草稿", "可以继续补充边界确认回答。");
    } else if (hasSource && isFaultDeferredBySource()) {
      beginTask("读取源文档范围", "正在检查源文档是否允许推进故障注入。");
      resultState.textContent = "源文档暂缓";
      resultSummary.textContent = faultDeferredReason();
      qualitySummary.textContent = "默认不生成故障候选；需要时点击“仍生成 dry-run 候选”。";
      renderSourceDeferral();
      renderBurdenSummary(null);
      finishTask("故障注入暂缓", "源文档声明本轮暂不考虑故障注入。");
    } else if (hasSource) {
      generateFaultPreparation();
    } else if (hasTemplateDrawing) {
      loadTemplateDrawingBlueprintCandidatePreview();
    } else {
      loadFirstVisitBlueprintCandidatePreview();
    }
    setBusy(false);
  }

  contextClose.addEventListener("click", closeContextPopover);
  contextPopover.addEventListener("click", (event) => {
    if (event.target === contextPopover) {
      closeContextPopover();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !contextPopover.hidden) {
      closeContextPopover();
    }
  });

  generateButton.addEventListener("click", () => {
    window.localStorage.removeItem(FAULT_DRAFT_KEY);
    window.localStorage.removeItem(SANDBOX_PLAN_KEY);
    generateFaultPreparation();
  });
  if (blueprintCandidateButton) {
    blueprintCandidateButton.addEventListener("click", loadBlueprintCandidateDemo);
  }
  sandboxNextButton.addEventListener("click", () => {
    if (!getBoundaryCompletion().isComplete) {
      updateSandboxGate();
      return;
    }
    saveFaultDraft();
    const selection = state.activeFaultMatrixSelection;
    if (!selection || !selection.reviewRowId) {
      window.location.href = "/fault-injection-sandbox";
      return;
    }
    const target = new URL("/fault-injection-sandbox", window.location.origin);
    target.searchParams.set("review", selection.reviewRowId);
    target.searchParams.set("trace", selection.traceId);
    target.searchParams.set("report", selection.reportId);
    window.location.href = `${target.pathname}${target.search}`;
  });
  backButton.addEventListener("click", goBackToLogicBuilder);
  saveBoundariesButton.addEventListener("click", () => saveFaultDraft());
  setActiveAuxPanel("none");
  boot();
})();

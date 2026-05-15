(function () {
  "use strict";

  const FAULT_PREPARATION_KEY = "ai-fantui-fault-injection-preparation-v1";
  const SANDBOX_PLAN_KEY = "ai-fantui-fault-injection-sandbox-plan-v1";
  const REVISION_HANDOFF_KEY = "ai-fantui-fault-injection-sandbox-revision-handoff-v1";
  const state = {
    faultPreparationPayload: null,
    sandboxPayload: null,
    timer: null,
    startedAt: 0,
    percent: 0,
    busy: false,
    activeReviewRowId: null,
    incomingReviewSelection: null,
  };
  const REVIEW_LINKS = {
    "SR-01": {traceId: "ET-02", reportId: "RP-03"},
    "SR-02": {traceId: "ET-02", reportId: "RP-04"},
    "SR-03": {traceId: "ET-03", reportId: "RP-06"},
    "SR-04": {traceId: "ET-02", reportId: "RP-05"},
    "SR-05": {traceId: "ET-04", reportId: "RP-01"},
    "SR-06": {traceId: "ET-04", reportId: "RP-06"},
    "SR-07": {traceId: "ET-03", reportId: "RP-07"},
  };
  const REVIEW_PACKAGE_PRIMARY_TRACE = {
    "ET-01": "SR-03",
    "ET-02": "SR-04",
    "ET-03": "SR-07",
    "ET-04": "SR-06",
  };
  const REVIEW_PACKAGE_PRIMARY_REPORT = {
    "RP-01": "SR-05",
    "RP-02": "SR-03",
    "RP-03": "SR-01",
    "RP-04": "SR-02",
    "RP-05": "SR-04",
    "RP-06": "SR-06",
    "RP-07": "SR-07",
  };

  const $ = (id) => document.getElementById(id);
  const provider = $("fault-sandbox-provider");
  const generateButton = $("fault-sandbox-generate");
  const reviewNextButton = $("fault-sandbox-revision-next");
  const reviewGate = $("fault-sandbox-review-gate");
  const backButton = $("fault-sandbox-back");
  const process = $("fault-sandbox-process");
  const processTitle = $("fault-sandbox-process-title");
  const processElapsed = $("fault-sandbox-process-elapsed");
  const processFill = $("fault-sandbox-process-fill");
  const processDetail = $("fault-sandbox-process-detail");
  const steps = {
    load: $("fault-sandbox-step-load"),
    model: $("fault-sandbox-step-model"),
    plan: $("fault-sandbox-step-plan"),
    review: $("fault-sandbox-step-review"),
  };
  const streamChunks = $("sandbox-stream-chunks");
  const STREAM_CHUNK_COPY = {
    load: "已读取准备：载入候选和边界",
    model: "DeepSeek 正在配置：生成 dry-run 沙盒",
    plan: "整理观测点：计划与信号已返回",
    review: "审查清单：等待一级闸门确认",
  };
  const workflowStage = $("fault-sandbox-workflow-stage");
  const workflowDetail = $("fault-sandbox-workflow-detail");
  const workflowSteps = Array.from(document.querySelectorAll("#fault-sandbox-workflow-steps .sandbox-workflow-step"));
  const sourceTitle = $("fault-sandbox-source-title");
  const sourceSummary = $("fault-sandbox-source-summary");
  const sourceMetrics = $("fault-sandbox-source-metrics");
  const resultState = $("fault-sandbox-result-state");
  const resultSummary = $("fault-sandbox-result-summary");
  const resultFlags = $("fault-sandbox-result-flags");
  const qualitySummary = $("fault-sandbox-quality-summary");
  const burdenAction = $("fault-sandbox-burden-action");
  const burdenOutputs = $("fault-sandbox-burden-outputs");
  const sandboxDecisionConclusion = $("fault-sandbox-decision-conclusion");
  const sandboxDecisionGates = $("fault-sandbox-decision-gates");
  const sandboxDecisionNextAction = $("fault-sandbox-decision-next-action");
  const repairDetails = $("fault-sandbox-repair-details");
  const repairSummary = $("fault-sandbox-repair-summary");
  const repairBody = $("fault-sandbox-repair-body");
  const planCoverageEvidence = $("fault-sandbox-plan-coverage-evidence");
  const planCoverageList = $("fault-sandbox-plan-coverage-list");
  const contract = $("fault-sandbox-contract");
  const planCount = $("fault-sandbox-plan-count");
  const planList = $("fault-sandbox-injection-plan");
  const observationCount = $("fault-sandbox-observation-count");
  const observationList = $("fault-sandbox-observation-points");
  const reviewCount = $("fault-sandbox-review-count");
  const reviewList = $("fault-sandbox-review-checklist");
  const reviewRowCount = $("fault-sandbox-review-row-count");
  const reviewRows = $("fault-sandbox-review-rows");
  const replayCanvasMain = $("fault-sandbox-replay-canvas-main");
  const replayCanvasLinks = $("fault-sandbox-replay-canvas-links");
  const replayCanvasNodes = $("fault-sandbox-replay-canvas-nodes");
  const replayCanvasMetrics = $("fault-sandbox-replay-canvas-metrics");
  const diagnosisInspector = $("fault-sandbox-diagnosis-inspector");
  const diagnosisState = $("fault-sandbox-diagnosis-state");
  const diagnosisSummary = $("fault-sandbox-diagnosis-summary");
  const mainReportRail = $("fault-sandbox-main-report-rail");
  const mainReportCount = $("fault-sandbox-main-report-count");
  const mainReportRows = $("fault-sandbox-main-report-rows");
  const activeReviewPackageSummary = $("fault-sandbox-review-package-summary");
  const affectedPath = $("fault-sandbox-affected-path");
  const firstAbnormalNode = $("fault-sandbox-first-abnormal-node");
  const inputSnapshot = $("fault-sandbox-input-snapshot");
  const diagnosisChain = $("fault-sandbox-diagnosis-chain");
  const repairSuggestions = $("fault-sandbox-repair-suggestions");
  const diagnosisEvidenceLinks = $("fault-sandbox-diagnosis-evidence-links");
  const evidenceTraceCount = $("fault-sandbox-evidence-trace-count");
  const evidenceTraceRows = $("fault-sandbox-evidence-trace-rows");
  const reportStrip = $("sandbox-report-strip");
  const replayWorkbench = $("fault-sandbox-replay-workbench");
  const replayControls = $("fault-sandbox-replay-controls");
  const replayClock = $("fault-sandbox-replay-clock");
  const replayTimeline = $("fault-sandbox-replay-timeline");
  const replayMetrics = $("fault-sandbox-replay-metrics");
  const reportPreview = $("fault-sandbox-report-preview");
  const reportPreviewCount = $("fault-sandbox-report-preview-count");
  const reportSectionRows = $("fault-sandbox-report-section-rows");
  const reportActionButtons = Array.from(document.querySelectorAll("[data-sandbox-report-action]"));
  const mainReportActionButtons = Array.from(document.querySelectorAll("[data-main-report-action]"));
  const replayControlButtons = Array.from(document.querySelectorAll("[data-replay-control]"));
  const primaryGateCount = $("fault-sandbox-primary-gate-count");
  const primaryGateInputs = Array.from(document.querySelectorAll("input[data-sandbox-confirm]"));
  const primaryGateDetails = {
    "dry-run": $("fault-sandbox-gate-dry-run-detail"),
    coverage: $("fault-sandbox-gate-coverage-detail"),
    risk: $("fault-sandbox-gate-exception-detail"),
  };
  const evidenceCount = $("fault-sandbox-evidence-count");
  const evidenceTiles = $("sandbox-evidence-tiles");
  const checklistCount = $("fault-sandbox-checklist-count");
  const checklistStrip = $("sandbox-checklist-strip");
  const detailPanelToggle = $("fault-sandbox-toggle-detail-panel");
  const detailDrawer = $("fault-sandbox-detail-drawer");
  const evidencePopover = $("sandbox-evidence-popover");
  const evidenceTitle = $("sandbox-evidence-title");
  const evidenceBody = $("sandbox-evidence-body");
  const evidenceClose = $("sandbox-evidence-close");
  const reviewPackagePanel = $("sandbox-review-package-panel");
  const reviewPackageClose = $("sandbox-review-package-close");
  const reviewPackageReviewCount = $("sandbox-review-package-review-count");
  const reviewPackageEvidenceCount = $("sandbox-review-package-evidence-count");
  const reviewPackageReportCount = $("sandbox-review-package-report-count");
  const reviewPackageReviewRows = $("sandbox-review-package-review-rows");
  const reviewPackageEvidenceRows = $("sandbox-review-package-evidence-rows");
  const reviewPackageReportRows = $("sandbox-review-package-report-rows");
  const sandboxShell = document.querySelector(".sandbox-shell");
  const unifiedAuxPanels = {
    "detail-drawer": detailDrawer,
    "evidence-popover": evidencePopover,
    "review-package": reviewPackagePanel,
  };

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

  function normalizeText(value) {
    return (value == null || value === "") ? "未提供" : value;
  }

  function compactRailLabel(value) {
    const raw = normalizeText(value);
    const aliases = {
      blueprint_plan_ra_override: "PLAN RA",
      blueprint_plan_sw2_dropout: "PLAN SW2",
      observe_release_gate: "OBS L1",
      observe_thr_lock: "OBS LOCK",
      radio_altitude_ft: "RA",
      release_gate: "L1 gate",
      thr_lock_release: "THR_LOCK",
      ra_lt_6ft: "RA<6ft",
      logic1: "L1",
      logic2: "L2",
      logic3: "L3",
      logic4: "L4",
      sw2_valid: "SW2",
    };
    if (aliases[raw]) return aliases[raw];
    return raw
      .replace(/^blueprint_plan_/, "PLAN ")
      .replace(/^observe_/, "OBS ")
      .replace(/^plan_/, "P")
      .replace(/^fault_/, "F")
      .replace(/_/g, " ")
      .slice(0, 24)
      .trim();
  }

  function clearChildren(element) {
    if (element) element.innerHTML = "";
  }

  function setActiveAuxPanel(name) {
    const panelName = name || "none";
    if (sandboxShell) {
      sandboxShell.dataset.activeAuxPanel = panelName;
      sandboxShell.dataset.unifiedInspectorState = panelName;
    }
    Object.entries(unifiedAuxPanels).forEach(([key, element]) => {
      if (element) element.dataset.unifiedPanelState = key === panelName ? "open" : "closed";
    });
    if (diagnosisInspector) diagnosisInspector.dataset.unifiedInspectorState = panelName;
    if (reportStrip) reportStrip.dataset.unifiedInspectorState = panelName;
  }

  function closeReviewPackagePanel() {
    if (!reviewPackagePanel) return;
    reviewPackagePanel.setAttribute("aria-hidden", "true");
    reviewPackagePanel.hidden = true;
    reviewPackagePanel.dataset.unifiedPanelState = "closed";
    if (sandboxShell && sandboxShell.dataset.activeAuxPanel === "review-package") {
      setActiveAuxPanel("none");
    }
  }

  function reviewLinkForRow(rowId) {
    return REVIEW_LINKS[rowId] || {traceId: "ET-03", reportId: "RP-06"};
  }

  function reviewRowsForTrace(traceId) {
    return Object.entries(REVIEW_LINKS)
      .filter((entry) => entry[1].traceId === traceId)
      .map((entry) => entry[0]);
  }

  function reviewRowsForReport(reportId) {
    return Object.entries(REVIEW_LINKS)
      .filter((entry) => entry[1].reportId === reportId)
      .map((entry) => entry[0]);
  }

  function primaryReviewRowForTrace(traceId) {
    const rows = reviewRowsForTrace(traceId);
    const primary = REVIEW_PACKAGE_PRIMARY_TRACE[traceId];
    if (primary && rows.includes(primary)) return primary;
    return rows[0] || "SR-03";
  }

  function primaryReviewRowForReport(reportId) {
    const rows = reviewRowsForReport(reportId);
    const primary = REVIEW_PACKAGE_PRIMARY_REPORT[reportId];
    if (primary && rows.includes(primary)) return primary;
    return primary || rows[0] || "SR-03";
  }

  function reviewRowItemById(rowId) {
    return buildSandboxReviewRows(state.sandboxPayload).find((item) => item.id === rowId);
  }

  function activateReviewPackageItem(target) {
    const reviewRowId = target && target.reviewRowId;
    const item = reviewRowItemById(reviewRowId);
    if (!item) return;
    activateReviewRow(item, {
      origin: "review-package",
      traceId: target.traceId,
      reportId: target.reportId,
    });
  }

  function setElementActiveByReview(container, selector, activeReviewRowId) {
    if (!container) return;
    Array.from(container.querySelectorAll(selector)).forEach((element) => {
      const linkedRows = (element.dataset.linkedReviewRows || "").split(/\s+/).filter(Boolean);
      const isActive = Boolean(activeReviewRowId && linkedRows.includes(activeReviewRowId));
      element.classList.toggle("is-linked-active", isActive);
      element.dataset.linkState = isActive ? "active" : "idle";
      element.setAttribute("aria-current", isActive ? "true" : "false");
    });
  }

  function buildActiveReviewPackageSummary(payload, reviewRowId) {
    if (!payload || !reviewRowId || isSourceDeferredSandbox(payload)) return null;
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const reviewRow = reviewRowsBuilt.find((item) => item.id === reviewRowId);
    if (!reviewRow) return null;
    const link = reviewLinkForRow(reviewRowId);
    const reportSections = buildReplayReportSections(payload);
    const reportSection = reportSections.find((item) => item.id === link.reportId) || {};
    const unresolved = reviewRow.state === "pass"
      ? "无阻断，保留人工复核"
      : "存在未决问题，需人工确认";
    const fix = reviewRowId === "SR-07"
      ? "保持候选态边界，不写入控制器"
      : `核对 ${link.traceId} 与 ${link.reportId} 回链`;
    return {
      reviewRowId,
      traceId: link.traceId,
      reportId: link.reportId,
      title: reviewRow.title,
      decision: sandboxReviewDecisionLabel(reviewRow.state),
      evidence: reviewRow.evidence,
      reportTitle: reportSection.title || "报告章节",
      unresolved,
      fix,
      evidenceLabel: `${link.traceId} / ${link.reportId}`,
    };
  }

  function renderActiveReviewPackageSummary() {
    if (!activeReviewPackageSummary) return;
    const summary = buildActiveReviewPackageSummary(state.sandboxPayload, state.activeReviewRowId);
    if (!summary) {
      activeReviewPackageSummary.dataset.packageState = "empty";
      activeReviewPackageSummary.dataset.activeReviewRow = "none";
      activeReviewPackageSummary.dataset.activeTraceId = "none";
      activeReviewPackageSummary.dataset.activeReportId = "none";
      activeReviewPackageSummary.hidden = true;
      activeReviewPackageSummary.innerHTML = "";
      return;
    }
    activeReviewPackageSummary.hidden = false;
    activeReviewPackageSummary.dataset.packageState = "active";
    activeReviewPackageSummary.dataset.activeReviewRow = summary.reviewRowId;
    activeReviewPackageSummary.dataset.activeTraceId = summary.traceId;
    activeReviewPackageSummary.dataset.activeReportId = summary.reportId;
    activeReviewPackageSummary.innerHTML = `
      <div class="sandbox-review-package-summary-head">
        <span>当前审查包</span>
        <strong>${escapeText(summary.title)}</strong>
        <code>${escapeText(summary.decision)}</code>
      </div>
      <div class="sandbox-review-package-summary-tokens" aria-label="SR ET RP 联动">
        <code data-package-summary-token="review">${escapeText(summary.reviewRowId)}</code>
        <code data-package-summary-token="trace">${escapeText(summary.traceId)}</code>
        <code data-package-summary-token="report">${escapeText(summary.reportId)}</code>
      </div>
      <div class="sandbox-review-package-summary-findings">
        <span><em>报告章节</em><strong>${escapeText(summary.reportTitle)}</strong></span>
        <span><em>未决问题</em><strong>${escapeText(summary.unresolved)}</strong></span>
        <span><em>建议修复</em><strong>${escapeText(summary.fix)}</strong></span>
        <span><em>关键证据</em><strong>${escapeText(summary.evidenceLabel)}</strong></span>
      </div>
      <div class="sandbox-review-package-summary-invariants" aria-label="候选态边界">
        <span>sandbox_candidate</span>
        <span>truth_effect:none</span>
        <span>controller_truth_modified:false</span>
      </div>
    `;
  }

  function applyReviewSelection() {
    const activeReviewRowId = state.activeReviewRowId;
    const link = activeReviewRowId ? reviewLinkForRow(activeReviewRowId) : null;
    const shell = document.querySelector(".sandbox-shell");
    if (shell) shell.dataset.activeReviewRow = activeReviewRowId || "none";
    if (reviewRows) {
      reviewRows.dataset.activeReviewRow = activeReviewRowId || "none";
      Array.from(reviewRows.querySelectorAll("[data-blueprint-review-row]")).forEach((row) => {
        const isActive = row.dataset.blueprintReviewRow === activeReviewRowId;
        row.classList.toggle("is-active", isActive);
        row.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }
    if (diagnosisInspector) {
      diagnosisInspector.dataset.activeReviewRow = activeReviewRowId || "none";
      diagnosisInspector.classList.toggle("is-review-linked", Boolean(activeReviewRowId));
    }
    if (affectedPath) affectedPath.dataset.linkedTraceId = link ? link.traceId : "";
    if (reportPreview) {
      reportPreview.dataset.activeReviewRow = activeReviewRowId || "none";
      reportPreview.classList.toggle("is-review-linked", Boolean(activeReviewRowId));
    }
    setElementActiveByReview(evidenceTraceRows, "[data-evidence-trace-id]", activeReviewRowId);
    setElementActiveByReview(reportSectionRows, "[data-report-section-id]", activeReviewRowId);
    setElementActiveByReview(replayTimeline, "[data-replay-marker]", activeReviewRowId);
    setElementActiveByReview(replayCanvasLinks, "[data-replay-canvas-link]", activeReviewRowId);
    setElementActiveByReview(replayCanvasNodes, "[data-replay-canvas-node]", activeReviewRowId);
    setElementActiveByReview(mainReportRows, "[data-main-report-id]", activeReviewRowId);
    renderActiveReviewPackageSummary();
  }

  function buildReviewRowEvidence(item, payload) {
    const link = reviewLinkForRow(item.id);
    const diagnosis = payload && !isSourceDeferredSandbox(payload)
      ? buildFailureDiagnosis(payload)
      : {path: "无候选沙盒路径", node: "未定位", snapshot: "未启用 dry-run"};
    return [
      {label: "ID", value: item.id},
      {label: "状态", value: item.label},
      {label: "证据数", value: item.evidence},
      {label: "来源", value: item.sourceLabel},
      {label: "说明", value: item.description},
      {label: "受影响路径", value: diagnosis.path},
      {label: "首个异常节点", value: diagnosis.node},
      {label: "证据追踪", value: link.traceId},
      {label: "对应报告章节", value: link.reportId},
      {label: "输入快照", value: diagnosis.snapshot},
    ];
  }

  function normalizeInspectorContext(context) {
    const incoming = context || {};
    const reviewRowId = incoming.reviewRowId || state.activeReviewRowId || "";
    const link = reviewRowId ? reviewLinkForRow(reviewRowId) : {};
    return {
      origin: incoming.origin || "inspector",
      reviewRowId,
      traceId: incoming.traceId || link.traceId || "ET",
      reportId: incoming.reportId || link.reportId || "RP",
    };
  }

  function readIncomingReviewSelection() {
    const params = new URLSearchParams(window.location.search);
    const rawReviewRowId = params.get("review");
    if (!rawReviewRowId) return null;
    const reviewRowId = normalizeText(rawReviewRowId);
    if (!reviewRowId) return null;
    const link = reviewLinkForRow(reviewRowId);
    return {
      origin: "incoming-review",
      reviewRowId,
      traceId: normalizeText(params.get("trace") || link.traceId),
      reportId: normalizeText(params.get("report") || link.reportId),
    };
  }

  function applyIncomingReviewSelection() {
    const incoming = state.incomingReviewSelection || readIncomingReviewSelection();
    if (!incoming || !incoming.reviewRowId) return;
    state.incomingReviewSelection = incoming;
    state.activeReviewRowId = incoming.reviewRowId;
    const shell = document.querySelector(".sandbox-shell");
    if (shell) {
      shell.dataset.incomingReview = incoming.reviewRowId;
      shell.dataset.incomingTrace = incoming.traceId;
      shell.dataset.incomingReport = incoming.reportId;
    }
    if (diagnosisInspector) {
      diagnosisInspector.dataset.incomingReviewSource = incoming.origin;
      diagnosisInspector.dataset.activeTraceId = incoming.traceId;
      diagnosisInspector.dataset.activeReportId = incoming.reportId;
    }
    applyReviewSelection();
  }

  function renderInspectorLinkSummary(context) {
    const summary = normalizeInspectorContext(context);
    const shell = document.createElement("div");
    shell.id = "sandbox-evidence-link-summary";
    shell.className = "sandbox-evidence-link-summary";
    shell.dataset.inspectorSource = summary.origin;
    shell.dataset.activeReviewRow = summary.reviewRowId || "none";
    shell.dataset.activeTraceId = summary.traceId || "none";
    shell.dataset.activeReportId = summary.reportId || "none";
    shell.innerHTML = `
      <span class="sandbox-evidence-link-label">当前联动</span>
      <code data-link-summary-kind="review">${escapeText(summary.reviewRowId || "SR")}</code>
      <code data-link-summary-kind="trace">${escapeText(summary.traceId || "ET")}</code>
      <code data-link-summary-kind="report">${escapeText(summary.reportId || "RP")}</code>
      <span class="sandbox-evidence-link-boundary">truth_effect:none</span>
      <span class="sandbox-evidence-link-boundary">controller_truth_modified:false</span>
    `;
    evidenceBody.appendChild(shell);
  }

  function activateLinkedInspector(context, title, rows) {
    const summary = normalizeInspectorContext(context);
    if (summary.reviewRowId) state.activeReviewRowId = summary.reviewRowId;
    applyReviewSelection();
    renderEvidenceRows(title, rows, summary);
    applyReviewSelection();
  }

  function activateReviewRow(item, context) {
    if (!item || !item.id) return;
    const link = reviewLinkForRow(item.id);
    activateLinkedInspector(
      {
        ...(context || {}),
        origin: (context && context.origin) || "review-row",
        reviewRowId: item.id,
        traceId: (context && context.traceId) || link.traceId,
        reportId: (context && context.reportId) || link.reportId,
      },
      `审查结果：${item.title}`,
      buildReviewRowEvidence(item, state.sandboxPayload),
    );
  }

  function renderEvidenceRows(title, rows, context) {
    const evidenceRows = Array.isArray(rows) ? rows : [];
    closeReviewPackagePanel();
    toggleDetailPanel(false);
    evidenceTitle.textContent = title || "证据详情";
    clearChildren(evidenceBody);
    renderInspectorLinkSummary(context);
    if (!evidenceRows.length) {
      const p = document.createElement("p");
      p.className = "muted";
      p.textContent = "当前证据项无额外细化字段。";
      evidenceBody.appendChild(p);
      evidencePopover.removeAttribute("aria-hidden");
      evidencePopover.hidden = false;
      setActiveAuxPanel("evidence-popover");
      return;
    }
    const dl = document.createElement("dl");
    evidenceRows.forEach((row) => {
      const dt = document.createElement("dt");
      dt.textContent = row.label;
      const dd = document.createElement("dd");
      dd.textContent = row.value;
      dl.append(dt, dd);
    });
    evidenceBody.appendChild(dl);
    evidencePopover.removeAttribute("aria-hidden");
    evidencePopover.hidden = false;
    setActiveAuxPanel("evidence-popover");
  }

  function closeEvidencePanel() {
    evidencePopover.setAttribute("aria-hidden", "true");
    evidencePopover.hidden = true;
    evidencePopover.dataset.unifiedPanelState = "closed";
    if (sandboxShell && sandboxShell.dataset.activeAuxPanel === "evidence-popover") {
      setActiveAuxPanel("none");
    }
  }

  function toggleDetailPanel(forceOpen) {
    if (!sandboxShell || !detailPanelToggle) return;
    const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : !sandboxShell.classList.contains("is-detail-open");
    if (shouldOpen) {
      closeEvidencePanel();
      closeReviewPackagePanel();
    }
    sandboxShell.classList.toggle("is-detail-open", shouldOpen);
    detailPanelToggle.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
    detailPanelToggle.textContent = shouldOpen ? "收起证据" : "证据/审查";
    if (detailDrawer) {
      detailDrawer.setAttribute("aria-hidden", shouldOpen ? "false" : "true");
      detailDrawer.dataset.unifiedPanelState = shouldOpen ? "open" : "closed";
    }
    if (shouldOpen) {
      setActiveAuxPanel("detail-drawer");
    } else if (sandboxShell.dataset.activeAuxPanel === "detail-drawer") {
      setActiveAuxPanel("none");
    }
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

  function loadFaultPreparationDraft() {
    const payload = loadJSON(FAULT_PREPARATION_KEY, null);
    state.faultPreparationPayload = payload && typeof payload === "object" ? payload : null;
    return state.faultPreparationPayload;
  }

  function loadFaultSandboxPlanDraft() {
    const payload = loadJSON(SANDBOX_PLAN_KEY, null);
    return payload && typeof payload === "object" ? payload : null;
  }

  function saveFaultSandboxPlanDraft(payload) {
    if (!payload) return;
    window.localStorage.setItem(SANDBOX_PLAN_KEY, JSON.stringify(payload));
  }

  function saveFaultPreparationDraft(payload) {
    if (!payload) return;
    window.localStorage.setItem(FAULT_PREPARATION_KEY, JSON.stringify(payload));
  }

  function blueprintPreviewSourceAnchors() {
    return [
      {
        id: "BP-SB-01",
        kind: "UI 蓝图",
        origin: "selected-final-set",
        quote_zh: "首次进入沙盒时加载本地 candidate-only 审查预览；不代表源文档已要求故障注入。",
        requirement_level: "candidate-preview",
        confidence: "ui_blueprint",
      },
    ];
  }

  function buildFirstVisitFaultPreparationPreview() {
    const anchors = blueprintPreviewSourceAnchors();
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
      first_visit_preview: true,
      source_scope: {
        fault_injection: {
          status: "ui_blueprint_preview",
          reason_zh: "没有已保存故障准备草稿时显示本地蓝图候选预览，作为沙盒工作台空态。",
          source_anchors: anchors,
        },
      },
      source_requirements_sha256: "ui-blueprint-first-visit",
      source_drawing_sha256: "ui-blueprint-first-visit",
      summary_zh: "首次进入已载入本地蓝图故障候选预览；仅用于沙盒审查 UI，不修改控制器真值。",
      fault_scenarios: [
        {
          id: "first_visit_fault_ra_low",
          label: "RA 低值卡滞候选",
          node_id: "radio_altitude_ft",
          fault_type: "sensor_stuck_low",
          severity: "medium",
          rationale_zh: "用于检查高度门限异常时的 dry-run 路径、证据回链和审查行。",
          expected_effect_zh: "沙盒中只观察路径影响，不触发真实 tick 或控制器写入。",
          observable_signals: ["radio_altitude_ft", "thr_lock"],
          source_anchors: anchors,
          provenance: "ui_blueprint_first_visit_preview",
        },
        {
          id: "first_visit_fault_sw_path",
          label: "SW 路径间歇候选",
          node_id: "sw1",
          fault_type: "intermittent_signal",
          severity: "medium",
          rationale_zh: "用于验证开关路径、证据追踪和报告章节之间的回链。",
          expected_effect_zh: "报告中回链到输入、观测点和人工审查行。",
          observable_signals: ["sw1", "thr_lock"],
          source_anchors: anchors,
          provenance: "ui_blueprint_first_visit_preview",
        },
      ],
      injection_points: [
        {
          id: "first_visit_inject_ra",
          node_id: "radio_altitude_ft",
          signal_name: "radio_altitude_ft",
          injection_mode: "override",
          safe_boundary_zh: "仅 dry-run 观察，RA 值限制在 0 到 20 ft，不进入真实控制。",
          constraint_zh: "truth_effect:none；controller_truth_modified:false。",
          priority: "P1",
          source_anchors: anchors,
        },
        {
          id: "first_visit_inject_sw",
          node_id: "sw1",
          signal_name: "switch_path",
          injection_mode: "toggle_sequence",
          safe_boundary_zh: "仅用于路径高亮和审查回链，不写入控制器。",
          constraint_zh: "candidate-only sandbox review。",
          priority: "P2",
          source_anchors: anchors,
        },
      ],
      boundary_questions: [
        {
          id: "first_visit_confirm_dry_run",
          prompt_zh: "确认此候选只用于 dry-run 沙盒审查？",
          rationale_zh: "首次进入默认态需要完整闭环，但不能触发真实控制执行。",
          blocks: "fault_injection",
        },
        {
          id: "first_visit_confirm_truth_boundary",
          prompt_zh: "确认不修改 controller truth、认证结论和生产配置？",
          rationale_zh: "所有输出保持 sandbox candidate，不进入适航或生产声明。",
          blocks: "fault_injection",
        },
      ],
      boundary_answers: [
        {
          id: "first_visit_confirm_dry_run",
          prompt_zh: "确认此候选只用于 dry-run 沙盒审查？",
          answer_zh: "确认仅用于 dry-run UI 预览。",
        },
        {
          id: "first_visit_confirm_truth_boundary",
          prompt_zh: "确认不修改 controller truth、认证结论和生产配置？",
          answer_zh: "确认不修改控制器真值和认证结论。",
        },
      ],
      coverage_completion: {
        strategy: "ui_blueprint_first_visit_preview",
        completed_node_ids: ["radio_altitude_ft", "sw1"],
        semantic_gate: "critical_node_coverage",
      },
      workflow_notes: [
        "首次进入预览由前端本地构造，保持 candidate-only。",
        "如需真实模型输出，请先从需求和逻辑绘制流程生成正式草稿。",
      ],
      llm: {
        provider: "local-ui",
        model: "blueprint-candidate-preview",
      },
    };
  }

  function buildFirstVisitSandboxCandidate(faultPayload) {
    const anchors = blueprintPreviewSourceAnchors();
    const scenarios = sandboxList(faultPayload, "fault_scenarios");
    const firstScenario = scenarios[0] || {};
    const secondScenario = scenarios[1] || firstScenario;
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
      first_visit_preview: true,
      source_fault_injection_preparation_sha256: "ui-blueprint-first-visit",
      source_boundary_answers_sha256: "ui-blueprint-first-visit",
      summary_zh: "首次进入已载入本地蓝图沙盒预览：只读 dry-run 审查，不运行真实 tick。",
      execution_contract: {
        run_tick: false,
        simulate: false,
        dry_run_only: true,
      },
      sandbox_injection_plan: [
        {
          id: "first_visit_plan_ra_override",
          fault_scenario_id: firstScenario.id || "first_visit_fault_ra_low",
          node_id: firstScenario.node_id || "radio_altitude_ft",
          signal_name: "radio_altitude_ft",
          injection_mode: "override",
          safe_range_zh: "0 到 20 ft，仅 UI dry-run。",
          expected_effect_zh: "检查 RA 候选异常是否只在沙盒证据链中呈现。",
          source_anchors: firstScenario.source_anchors || anchors,
        },
        {
          id: "first_visit_plan_sw_toggle",
          fault_scenario_id: secondScenario.id || "first_visit_fault_sw_path",
          node_id: secondScenario.node_id || "sw1",
          signal_name: "switch_path",
          injection_mode: "toggle_sequence",
          safe_range_zh: "仅生成审查回放，不写入控制器。",
          expected_effect_zh: "高亮开关路径、观测点和人工审查行之间的回链。",
          source_anchors: secondScenario.source_anchors || anchors,
        },
      ],
      observation_points: [
        {
          id: "first_visit_observe_release_gate",
          node_id: "radio_altitude_ft",
          signal_name: "release_gate",
          check_zh: "确认候选异常不会绕过 TRA、SW1/SW2、VDT 与地面状态约束。",
          source_anchors: anchors,
        },
        {
          id: "first_visit_observe_thr_lock",
          node_id: "thr_lock",
          signal_name: "thr_lock",
          check_zh: "确认油门锁状态只作为沙盒观测输出，不生成真实控制动作。",
          source_anchors: anchors,
        },
      ],
      review_checklist: [
        {
          id: "first_visit_review_dry_run",
          category: "dry_run",
          condition_zh: "确认执行合同保持 run_tick:false、simulate:false、dry_run_only:true。",
          pass_criteria_zh: "审查页仅显示候选证据，不触发真实仿真 tick。",
          source_anchors: anchors,
        },
        {
          id: "first_visit_review_trace",
          category: "traceability",
          condition_zh: "确认计划、观测点和审查行可回链到候选节点和报告章节。",
          pass_criteria_zh: "审查行、证据链、报告章节和审查包均可互相定位。",
          source_anchors: anchors,
        },
      ],
      plan_coverage_completion: {
        strategy: "ui_blueprint_first_visit_preview",
        completed_fault_scenario_ids: scenarios.map((item) => item.id).filter(Boolean),
        semantic_gate: "scenario_plan_coverage",
      },
      workflow_notes: [
        "该沙盒计划由前端首次进入预览生成，保持 candidate-only。",
        "用于验收故障注入、沙盒审查、证据追溯和报告预览 UI。",
      ],
      llm: {
        provider: "local-ui",
        model: "blueprint-candidate-preview",
      },
    };
  }

  function loadFirstVisitSandboxPreview() {
    const faultPayload = buildFirstVisitFaultPreparationPreview();
    const sandboxPayload = buildFirstVisitSandboxCandidate(faultPayload);
    state.faultPreparationPayload = faultPayload;
    saveFaultPreparationDraft(faultPayload);
    saveFaultSandboxPlanDraft(sandboxPayload);
    renderSource();
    renderSandboxPayload(sandboxPayload);
  }

  function buildTemplateSandboxCandidate(faultPayload, options) {
    const sandboxPayload = buildFirstVisitSandboxCandidate(faultPayload);
    const opts = options || {};
    sandboxPayload.first_visit_preview = false;
    sandboxPayload.template_preview = true;
    sandboxPayload.summary_zh = opts.refresh
      ? "DOCX L1-L4 模板候选沙盒计划已刷新：只读 dry-run 审查，不运行真实 tick。"
      : "DOCX L1-L4 模板候选沙盒计划已载入：只读 dry-run 审查，不运行真实 tick。";
    sandboxPayload.source_fault_injection_preparation_sha256 = "local-docx-l1-l4-template";
    sandboxPayload.source_boundary_answers_sha256 = "local-docx-l1-l4-template";
    sandboxPayload.plan_coverage_completion = {
      ...(sandboxPayload.plan_coverage_completion || {}),
      strategy: "ui_template_preview",
    };
    sandboxPayload.workflow_notes = [
      "该沙盒计划由逻辑绘制页 DOCX 模板候选生成，保持 candidate-only。",
      "用于验收故障矩阵、沙盒审查、证据追溯和报告预览 UI。",
    ];
    return sandboxPayload;
  }

  function loadTemplateSandboxPreview(options) {
    const sandboxPayload = buildTemplateSandboxCandidate(state.faultPreparationPayload, options);
    saveFaultSandboxPlanDraft(sandboxPayload);
    renderSource();
    renderSandboxPayload(sandboxPayload);
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
    generateButton.disabled = isBusy || !state.faultPreparationPayload;
    generateButton.textContent = isBusy ? "生成中..." : "检查：生成配置";
    updateReviewGate();
  }

  function setWorkflowSteps(activeStep, completedSteps) {
    workflowSteps.forEach((element) => {
      const step = element.dataset.workflowStep || "";
      element.classList.toggle("is-active", step === activeStep);
      element.classList.toggle("is-complete", completedSteps.includes(step));
      element.classList.toggle("is-locked", !completedSteps.includes(step) && step !== activeStep);
    });
  }

  function renderWorkflowOverview() {
    if (!state.faultPreparationPayload) {
      workflowStage.textContent = "等待故障准备草稿";
      workflowDetail.textContent = "先完成故障候选和边界确认，再生成沙盒配置建议。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    if (isSourceDeferredSandbox(state.sandboxPayload)) {
      workflowStage.textContent = "源文档暂缓";
      workflowDetail.textContent = "DOCX 明确暂缓故障注入，默认不生成沙盒计划；如需演示，请显式生成 dry-run 候选。";
      setWorkflowSteps("fault", ["requirements", "drawing", "fault"]);
      return;
    }
    if (state.sandboxPayload) {
      workflowStage.textContent = "等待人工审查";
      workflowDetail.textContent = "沙盒配置建议已生成；请确认 3 个一级闸门，必要时展开细项复核。";
      setWorkflowSteps("sandbox", ["requirements", "drawing", "fault"]);
      return;
    }
    workflowStage.textContent = "准备生成沙盒配置";
    workflowDetail.textContent = "已载入故障准备草稿，模型将生成 dry-run 配置建议和观测点。";
    setWorkflowSteps("sandbox", ["requirements", "drawing", "fault"]);
  }

  function sandboxList(payload, key) {
    return Array.isArray(payload && payload[key]) ? payload[key] : [];
  }

  function isSourceDeferredSandbox(payload) {
    const scope = payload && payload.source_scope;
    return Boolean(
      payload && (
        payload.status === "source_deferred" ||
        payload.status === "skipped_by_source_scope" ||
        (scope && scope.fault_injection && scope.fault_injection.status === "source_deferred")
      )
    );
  }

  function setPrimaryGateDetail(gate, text) {
    const detail = primaryGateDetails[gate];
    if (detail) detail.textContent = text;
  }

  function setSandboxDecisionConclusion(text) {
    if (sandboxDecisionConclusion) sandboxDecisionConclusion.textContent = text || "等待配置";
  }

  function setSandboxDecisionGates(text) {
    if (sandboxDecisionGates) sandboxDecisionGates.textContent = text || "0/3 已确认";
  }

  function setSandboxDecisionNextAction(text) {
    if (!sandboxDecisionNextAction) return;
    const value = text || "等待配置";
    if (value === "等待配置") {
      sandboxDecisionNextAction.textContent = "等待配置：生成后得到审查包、证据链和回放报告。";
    } else if (value === "模型处理中") {
      sandboxDecisionNextAction.textContent = "模型处理中：完成后刷新审查包、证据链和回放报告。";
    } else if (value === "源文档暂缓") {
      sandboxDecisionNextAction.textContent = "源文档暂缓：不生成真实执行，只保留 candidate-only 证据。";
    } else if (value === "需重新生成沙盒配置") {
      sandboxDecisionNextAction.textContent = "需重新生成沙盒配置：补齐计划、观测点和审查行。";
    } else if (value.startsWith("已确认") || value.startsWith("需确认")) {
      sandboxDecisionNextAction.textContent = `${value}：确认后用审查包和回放报告生成候选修订单。`;
    } else if (value === "可进入逻辑修订") {
      sandboxDecisionNextAction.textContent = "可进入逻辑修订：审查包和回放报告将作为修订单依据。";
    } else {
      sandboxDecisionNextAction.textContent = value;
    }
  }

  function setPrimaryGateInputsEnabled(enabled) {
    primaryGateInputs.forEach((input) => {
      input.disabled = !enabled;
      const card = input.closest(".sandbox-primary-gate");
      if (card) card.dataset.state = enabled ? "ready" : "waiting";
    });
  }

  function renderPrimaryReviewGates(payload) {
    const sourceDeferred = isSourceDeferredSandbox(payload);
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const observations = sandboxList(payload, "observation_points");
    const reviews = sandboxList(payload, "review_checklist");
    const execution = payload && payload.execution_contract ? payload.execution_contract : {};
    const preparedScenarios = sandboxList(state.faultPreparationPayload, "fault_scenarios");
    const scenarioIds = new Set(preparedScenarios.map((item) => item && item.id).filter(Boolean));
    const plannedScenarioIds = new Set(plans.map((item) => item && item.fault_scenario_id).filter(Boolean));
    const covered = Array.from(scenarioIds).filter((id) => plannedScenarioIds.has(id)).length;
    primaryGateInputs.forEach((input) => {
      input.checked = false;
    });
    setPrimaryGateInputsEnabled(Boolean(payload) && !sourceDeferred);
    if (sourceDeferred) {
      setPrimaryGateDetail("dry-run", "源文档暂缓故障注入，默认不生成 dry-run 沙盒计划。");
      setPrimaryGateDetail("coverage", "覆盖 0 个故障场景 · 0 plans · 0 points");
      setPrimaryGateDetail("risk", "无沙盒细项需要确认；仅保留显式 dry-run 入口。");
      setSandboxDecisionConclusion("源文档暂缓，不生成沙盒计划");
      updateReviewGate();
      return;
    }
    setPrimaryGateDetail(
      "dry-run",
      `run_tick:${Boolean(execution.run_tick)} · simulate:${Boolean(execution.simulate)} · dry_run_only:${execution.dry_run_only !== false}`,
    );
    setPrimaryGateDetail(
      "coverage",
      scenarioIds.size
        ? `覆盖 ${covered}/${scenarioIds.size} 个故障场景 · ${plans.length} plans · ${observations.length} points`
      : `${plans.length} plans · ${observations.length} points`,
    );
    setPrimaryGateDetail("risk", `${reviews.length} 条审查细项默认折叠，展开后复核例外和风险。`);
    setSandboxDecisionConclusion(payload ? "沙盒配置已生成，等待一级闸门确认" : "等待配置");
    updateReviewGate();
  }

  function getReviewCompletion() {
    const plans = sandboxList(state.sandboxPayload, "sandbox_injection_plan");
    const observations = sandboxList(state.sandboxPayload, "observation_points");
    const reviews = sandboxList(state.sandboxPayload, "review_checklist");
    const confirmations = primaryGateInputs;
    const isSourceDeferred = isSourceDeferredSandbox(state.sandboxPayload);
    const total = confirmations.length;
    const confirmed = confirmations.filter((input) => input.checked).length;
    const hasGenerated = Boolean(!isSourceDeferred && state.sandboxPayload && plans.length && observations.length && reviews.length);
    return {
      total,
      confirmed,
      hasGenerated,
      isSourceDeferred,
      isComplete: Boolean(hasGenerated && total > 0 && confirmed === total),
    };
  }

  function updateReviewGate() {
    const completion = getReviewCompletion();
    let nextText = "等待配置";
    let isBlocked = true;
    if (state.busy) {
      nextText = "模型处理中";
    } else if (!state.sandboxPayload) {
      nextText = "等待配置";
    } else if (completion.isSourceDeferred) {
      nextText = "源文档暂缓";
    } else if (!completion.hasGenerated) {
      nextText = "需重新生成沙盒配置";
    } else if (!completion.isComplete) {
      nextText = completion.confirmed
        ? `已确认 ${completion.confirmed}/${completion.total} 个一级闸门`
        : `需确认 ${completion.total} 个一级闸门`;
    } else {
      nextText = "可进入逻辑修订";
      isBlocked = false;
    }
    if (primaryGateCount) {
      primaryGateCount.textContent = `${completion.confirmed}/${completion.total || 3} gates`;
    }
    setSandboxDecisionGates(`${completion.confirmed}/${completion.total || 3} 已确认`);
    primaryGateInputs.forEach((input) => {
      const card = input.closest(".sandbox-primary-gate");
      if (card) {
        card.dataset.state = input.checked ? "confirmed" : (completion.hasGenerated ? "ready" : "waiting");
      }
    });
    reviewNextButton.disabled = isBlocked;
    reviewNextButton.title = nextText;
    reviewGate.textContent = nextText;
    reviewGate.classList.toggle("is-ready", !isBlocked);
    setSandboxDecisionNextAction(nextText);
  }

  function buildRevisionHandoff() {
    const plans = sandboxList(state.sandboxPayload, "sandbox_injection_plan");
    const observations = sandboxList(state.sandboxPayload, "observation_points");
    const reviews = sandboxList(state.sandboxPayload, "review_checklist");
    const firstPlan = plans[0] || {};
    const firstObservation = observations[0] || {};
    return {
      version: 1,
      from: "fault_injection_sandbox",
      plan_count: plans.length,
      observation_count: observations.length,
      review_count: reviews.length,
      top_signal: firstObservation.signal_name || "",
      top_node: firstPlan.node_id || firstObservation.node_id || "",
      summary: state.sandboxPayload && state.sandboxPayload.summary_zh ? state.sandboxPayload.summary_zh : "沙盒审查已完成，请填写需要回写到逻辑图的修改意见。",
      ts: new Date().toISOString(),
    };
  }

  function saveRevisionHandoff() {
    window.localStorage.setItem(REVISION_HANDOFF_KEY, JSON.stringify(buildRevisionHandoff()));
  }

  function renderSource() {
    const payload = state.faultPreparationPayload || {};
    const scenarios = payload.fault_scenarios || [];
    const answers = payload.boundary_answers || [];
    sourceTitle.textContent = payload.summary_zh ? "已载入故障准备草稿" : "尚未载入";
    sourceSummary.textContent = payload.summary_zh || "需要先保存故障注入准备草稿。";
    sourceMetrics.textContent = `${scenarios.length} scenarios · ${answers.length} answers`;
  }

  function renderFlags(payload) {
    const safePayload = payload || {};
    resultFlags.innerHTML = "";
    const repair = safePayload.llm && safePayload.llm.self_repair;
    const flags = [
      safePayload.controller_truth_modified ? "需复核控制逻辑" : "未改控制逻辑",
      "沙盒建议",
      safePayload.certification_claim && safePayload.certification_claim !== "none" ? "含认证声明" : "无认证声明",
      (safePayload.llm && safePayload.llm.provider === "minimax") ? "MiniMax" : "DeepSeek",
    ];
    if (repair) {
      flags.push(repair.success ? "已自动整理" : "需重新生成");
    }
    if (safePayload.plan_coverage_completion) {
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
    row.className = "sandbox-repair-row";
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

  function addPlanCoverageRow(label, value) {
    if (value == null || value === "") return;
    const row = document.createElement("div");
    row.className = "sandbox-coverage-row";
    const key = document.createElement("span");
    key.textContent = label;
    const val = document.createElement("code");
    val.textContent = String(value);
    row.append(key, val);
    planCoverageList.appendChild(row);
  }

  function renderPlanCoverageCompletionEvidence(payload) {
    const completion = payload && payload.plan_coverage_completion;
    const completedScenarioIds = Array.isArray(completion && completion.completed_fault_scenario_ids)
      ? completion.completed_fault_scenario_ids.filter(Boolean)
      : [];
    planCoverageList.innerHTML = "";
    if (!completion || !completedScenarioIds.length) {
      planCoverageEvidence.hidden = true;
      return;
    }
    planCoverageEvidence.hidden = false;
    addPlanCoverageRow("补齐策略", completion.strategy || "deterministic_dry_run_plan");
    addPlanCoverageRow("补齐场景", completedScenarioIds.join(", "));
    addPlanCoverageRow("语义门", completion.semantic_gate || "scenario_plan_coverage");
  }

  function renderQualitySummary(payload) {
    const safePayload = payload || {};
    if (isSourceDeferredSandbox(safePayload)) {
      qualitySummary.textContent = "源文档暂缓 · 0 个沙盒计划 · 0 个观测点";
      return;
    }
    const preparedScenarios = Array.isArray(
      state.faultPreparationPayload && state.faultPreparationPayload.fault_scenarios
    ) ? state.faultPreparationPayload.fault_scenarios : [];
    const scenarioIds = new Set(
      preparedScenarios
        .map((item) => item && item.id)
        .filter(Boolean)
    );
    const plans = Array.isArray(safePayload.sandbox_injection_plan) ? safePayload.sandbox_injection_plan : [];
    const plannedScenarioIds = new Set(
      plans
        .map((item) => item && item.fault_scenario_id)
        .filter(Boolean)
    );
    const covered = Array.from(scenarioIds).filter((id) => plannedScenarioIds.has(id)).length;
    const observations = Array.isArray(safePayload.observation_points) ? safePayload.observation_points : [];
    if (scenarioIds.size) {
      qualitySummary.textContent = `已覆盖 ${covered}/${scenarioIds.size} 个故障场景 · ${plans.length} 个沙盒计划 · ${observations.length} 个观测点 · 待人工审查`;
      return;
    }
    qualitySummary.textContent = `已生成 ${plans.length} 个沙盒计划 · ${observations.length} 个观测点 · 待人工审查`;
  }

  function renderBurdenSummary(payload) {
    if (!payload) {
      burdenAction.textContent = "先确认是否需要沙盒配置。";
      burdenOutputs.innerHTML = "<li>本页关键输出限制为计划、观测、审查 3 类。</li>";
      setSandboxDecisionConclusion("等待沙盒配置");
      return;
    }
    if (isSourceDeferredSandbox(payload)) {
      burdenAction.textContent = "源文档暂缓，默认不生成沙盒配置。";
      burdenOutputs.innerHTML = ["dry-run 合同：未启用", "覆盖：0 个计划 / 0 个观测点", "例外/风险：无待确认细项"]
        .map((item) => `<li>${escapeText(item)}</li>`)
        .join("");
      setSandboxDecisionConclusion("源文档暂缓，不生成沙盒计划");
      return;
    }
    const plans = Array.isArray(payload.sandbox_injection_plan) ? payload.sandbox_injection_plan.length : 0;
    const observations = Array.isArray(payload.observation_points) ? payload.observation_points.length : 0;
    const reviews = Array.isArray(payload.review_checklist) ? payload.review_checklist.length : 0;
    burdenAction.textContent = "先确认 3 个一级闸门；细项默认折叠。";
    burdenOutputs.innerHTML = ["dry-run 合同", `覆盖：${plans} 个计划 / ${observations} 个观测点`, `例外/风险：${reviews} 条细项`]
      .map((item) => `<li>${escapeText(item)}</li>`)
      .join("");
    setSandboxDecisionConclusion(`沙盒计划 ${plans} 项 · 观测点 ${observations} 个 · 审查项 ${reviews} 条`);
  }

  function renderEvidenceTiles(payload) {
    if (!payload) {
      evidenceCount.textContent = "0 tiles";
      evidenceTiles.innerHTML = '<p class="muted">暂无配置，请先生成沙盒计划。</p>';
      return;
    }
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const reviews = sandboxList(payload, "review_checklist");
    const execution = (payload && payload.execution_contract) || {};
    const preparedScenarios = sandboxList(state.faultPreparationPayload, "fault_scenarios");
    const scenarioIds = new Set(preparedScenarios.map((item) => item && item.id).filter(Boolean));
    const plannedScenarioIds = new Set(plans.map((item) => item && item.fault_scenario_id).filter(Boolean));
    const covered = Array.from(scenarioIds).filter((id) => plannedScenarioIds.has(id)).length;
    const hasCoverage = scenarioIds.size > 0;

    evidenceCount.textContent = "4 tiles";
    clearChildren(evidenceTiles);
    const completion = payload && payload.plan_coverage_completion;
    const completedScenarioIds = Array.isArray(completion && completion.completed_fault_scenario_ids)
      ? completion.completed_fault_scenario_ids.filter(Boolean)
      : [];
    const tiles = [
      {
        title: "场景与计划覆盖",
        value: `${covered}/${hasCoverage ? scenarioIds.size : plans.length} 覆盖`,
        state: hasCoverage && covered >= scenarioIds.size ? "ready" : "warn",
        rows: [
          {label: "故障场景", value: hasCoverage ? `${scenarioIds.size} 个` : "未读取故障场景"},
          {label: "沙盒计划", value: `${plans.length} 个`},
          {label: "覆盖率", value: hasCoverage ? `${Math.round((covered / scenarioIds.size) * 100)}%` : "N/A"},
          {label: "说明", value: hasCoverage ? "每个故障场景应至少有一条沙盒计划。" : "当前以模型返回主视图为准。"},
        ],
      },
      {
        title: "执行合同",
        value: `run_tick:${Boolean(execution.run_tick)} · simulate:${Boolean(execution.simulate)}`,
        state: execution && execution.run_tick === false && execution.simulate === false ? "ready" : "warn",
        rows: [
          {label: "run_tick", value: String(Boolean(execution.run_tick))},
          {label: "simulate", value: String(Boolean(execution.simulate))},
          {label: "dry_run_only", value: String(execution.dry_run_only !== false)},
          {label: "要求", value: "dry-run 仅回放，不写入控制器。"},
        ],
      },
      {
        title: "审查项密度",
        value: `${reviews.length} 条 · 快照`,
        state: reviews.length > 0 ? "ready" : "warn",
        rows: [
          {label: "一级闸门", value: `${primaryGateCount ? primaryGateCount.textContent : "0/3 gates"}`},
          {label: "审查细项", value: `${reviews.length} 条`},
          {label: "默认状态", value: "细项默认折叠，点击下方条目查看详情。"},
        ],
      },
      {
        title: "自动补齐",
        value: completedScenarioIds.length ? `${completedScenarioIds.length} 条` : "无补齐",
        state: completedScenarioIds.length ? "ready" : "none",
        rows: [
          {label: "策略", value: completion ? completion.strategy : "无补齐"},
          {label: "补齐语义", value: completion ? normalizeText(completion.semantic_gate) : "未触发补齐"},
          {label: "补齐场景", value: completedScenarioIds.length ? completedScenarioIds.join(", ") : "无"},
        ],
      },
    ];

    for (const tile of tiles) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "sandbox-evidence-tile";
      button.dataset.evidenceState = tile.state;
      button.innerHTML = `<strong>${escapeText(tile.title)}</strong><span>${escapeText(tile.value)}</span>`;
      button.addEventListener("click", () => renderEvidenceRows(tile.title, tile.rows));
      evidenceTiles.appendChild(button);
    }
  }

  function sandboxReviewRowStatus(condition, warning) {
    if (condition) return {label: "通过", state: "pass"};
    if (warning) return {label: "警告", state: "warn"};
    return {label: "未评估", state: "pending"};
  }

  function sandboxReviewDecisionLabel(stateName) {
    if (stateName === "pass") return "PASS";
    if (stateName === "warn") return "REVIEW";
    return "WAIT";
  }

  function reportChapterKind(reportId) {
    return {
      "RP-01": "summary",
      "RP-02": "source",
      "RP-03": "logic",
      "RP-04": "parameters",
      "RP-05": "fault-coverage",
      "RP-06": "sandbox-review",
      "RP-07": "open-risk",
    }[reportId] || "report";
  }

  function reportChapterState(reportId, reviewState) {
    if (reportId === "RP-07") return "wait";
    if (reviewState === "warn") return "review";
    if (reviewState === "pass") return "pass";
    return "wait";
  }

  function buildSandboxReviewRows(payload) {
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const observations = sandboxList(payload, "observation_points");
    const reviews = sandboxList(payload, "review_checklist");
    const execution = payload && payload.execution_contract ? payload.execution_contract : {};
    const truthSafe = payload && payload.truth_effect === "none"
      && payload.certification_claim === "none"
      && payload.controller_truth_modified === false;
    const dryRunSafe = execution.run_tick === false && execution.simulate === false && execution.dry_run_only !== false;
    const hasPlans = plans.length > 0;
    const hasObservations = observations.length > 0;
    const hasReviews = reviews.length > 0;
    const planCoverage = payload && payload.plan_coverage_completion;
    return [
      {
        id: "SR-01",
        title: "条件完整性",
        ...sandboxReviewRowStatus(hasPlans && hasObservations, false),
        evidence: `${observations.length} points`,
        sourceLabel: `${plans.length} plans`,
        description: "关键触发条件必须落到 dry-run 计划和观测点。",
      },
      {
        id: "SR-02",
        title: "阈值一致性",
        ...sandboxReviewRowStatus(dryRunSafe, false),
        evidence: dryRunSafe ? "dry-run" : "contract gap",
        sourceLabel: "execution_contract",
        description: "run_tick:false、simulate:false、dry_run_only:true 必须保持一致。",
      },
      {
        id: "SR-03",
        title: "不确定项处理",
        ...sandboxReviewRowStatus(false, hasReviews),
        evidence: `${reviews.length} checks`,
        sourceLabel: "review_checklist",
        description: "开放不确定项保留为人工复核，不升级为控制真值。",
      },
      {
        id: "SR-04",
        title: "故障覆盖",
        ...sandboxReviewRowStatus(Boolean(planCoverage) || (hasPlans && hasObservations), false),
        evidence: planCoverage ? "completion" : `${plans.length}/${observations.length}`,
        sourceLabel: "fault_scenarios",
        description: "候选故障需要至少一条计划或自动补齐证据。",
      },
      {
        id: "SR-05",
        title: "回放可复现",
        ...sandboxReviewRowStatus(hasPlans && dryRunSafe, false),
        evidence: `${plans.length} replay refs`,
        sourceLabel: "localStorage draft",
        description: "沙盒回放只读复现，不调用真实仿真 tick。",
      },
      {
        id: "SR-06",
        title: "报告可追溯",
        ...sandboxReviewRowStatus(hasReviews || hasObservations, false),
        evidence: `${reviews.length + observations.length} links`,
        sourceLabel: "evidence tiles",
        description: "报告、证据和审查行必须能互相回链。",
      },
      {
        id: "SR-07",
        title: "控制真相未修改",
        ...sandboxReviewRowStatus(truthSafe, false),
        evidence: truthSafe ? "diff=0" : "boundary violation",
        sourceLabel: "candidate chips",
        description: "保持 truth_effect:none、certification_claim:none、controller_truth_modified:false。",
      },
    ];
  }

  function renderSandboxReviewRows(payload) {
    if (!reviewRows) return;
    reviewRows.innerHTML = "";
    const header = document.createElement("div");
    header.className = "sandbox-review-row-header";
    header.setAttribute("role", "row");
    header.setAttribute("aria-hidden", "true");
    header.innerHTML = `
      <span data-blueprint-col="checkbox">选</span>
      <span data-blueprint-col="id">ID</span>
      <span data-blueprint-col="gate">闸门</span>
      <span data-blueprint-col="status">状态</span>
      <span data-blueprint-col="evidence">证据</span>
      <span data-blueprint-col="source">来源</span>
      <span data-blueprint-col="hazard-decision">风险 / 说明</span>
      <span data-blueprint-col="trace-report">回链</span>
      <span data-blueprint-col="action">操作</span>
    `;
    reviewRows.appendChild(header);
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (reviewRowCount) reviewRowCount.textContent = "0 rows";
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "暂无审查结果。生成沙盒配置后显示 7 条蓝图审查行。";
      reviewRows.appendChild(empty);
      return;
    }
    const rows = buildSandboxReviewRows(payload);
    if (reviewRowCount) reviewRowCount.textContent = `${rows.length} rows`;
    rows.forEach((item) => {
      const link = reviewLinkForRow(item.id);
      const row = document.createElement("article");
      row.className = "sandbox-review-row blueprint-row blueprint-row--sandbox-review blueprint-density-row";
      row.tabIndex = 0;
      row.setAttribute("role", "row");
      row.setAttribute("aria-selected", "false");
      row.setAttribute("data-blueprint-review-row", item.id);
      row.setAttribute("data-blueprint36-row", "sandbox-review");
      row.dataset.blueprintDensity = "compact-workbench";
      row.dataset.blueprintRowPattern = "shared-v1";
      row.dataset.blueprintRowRhythm = "checkbox-id-gate-evidence-trace-action";
      row.dataset.rowScanKind = "sandbox-review";
      row.dataset.rowScanContract = "id-status-evidence-link";
      row.dataset.reviewRowStatus = item.state;
      row.dataset.reviewRowId = item.id;
      row.dataset.blueprintColumns = "checkbox id gate status evidence source hazard-decision trace-report action";
      row.dataset.linkedTraceId = link.traceId;
      row.dataset.linkedReportId = link.reportId;
      row.innerHTML = `
        <span class="sandbox-review-row-check" data-blueprint-col="checkbox"><input type="checkbox" aria-label="选择审查行 ${escapeText(item.id)}" checked disabled></span>
        <span class="sandbox-review-row-id blueprint-row-token" data-blueprint-col="id" data-row-scan-token="id">${escapeText(item.id)}</span>
        <strong class="sandbox-review-row-gate" data-blueprint-col="gate">${escapeText(item.title)}</strong>
        <span class="sandbox-review-row-status blueprint-row-chip" data-blueprint-col="status" data-row-scan-token="status">${escapeText(item.label)}</span>
        <code class="sandbox-review-row-evidence" data-blueprint-col="evidence" data-row-scan-token="evidence">${escapeText(item.evidence)}</code>
        <code class="sandbox-review-row-source" data-blueprint-col="source">${escapeText(item.sourceLabel)}</code>
        <p class="sandbox-review-row-description" data-blueprint-col="hazard-decision">
          <span class="sandbox-review-row-decision blueprint-row-chip">${escapeText(sandboxReviewDecisionLabel(item.state))}</span>
          <span class="sandbox-review-row-description-text">${escapeText(item.description)}</span>
        </p>
        <span class="sandbox-review-row-links blueprint-row-linkbar" data-blueprint-col="trace-report" data-row-scan-token="link" aria-label="证据回链 ${escapeText(link.traceId)} ${escapeText(link.reportId)}">
          <span class="sandbox-review-row-link-token blueprint-row-token blueprint-row-token--trace" data-link-kind="trace">${escapeText(link.traceId)}</span>
          <span class="sandbox-review-row-link-token blueprint-row-token blueprint-row-token--report" data-link-kind="report">${escapeText(link.reportId)}</span>
        </span>
        <span class="sandbox-review-row-action blueprint-row-chip" data-blueprint-col="action">查看</span>
      `;
      row.addEventListener("click", () => activateReviewRow(item));
      row.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          activateReviewRow(item);
        }
      });
      reviewRows.appendChild(row);
    });
    applyReviewSelection();
  }

  function buildFailureDiagnosis(payload) {
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const observations = sandboxList(payload, "observation_points");
    const reviews = sandboxList(payload, "review_checklist");
    const execution = payload && payload.execution_contract ? payload.execution_contract : {};
    const firstPlan = plans[0] || {};
    const firstObservation = observations[0] || {};
    const firstReview = reviews[0] || {};
    const planId = normalizeText(firstPlan.id);
    const planNode = normalizeText(firstPlan.node_id || firstPlan.signal_name);
    const observationId = normalizeText(firstObservation.id || firstObservation.signal_name);
    const observationNode = normalizeText(firstObservation.node_id || firstObservation.signal_name);
    const dryRunSafe = execution.run_tick === false && execution.simulate === false && execution.dry_run_only !== false;
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const planLink = reviewLinkForRow("SR-04");
    const replayLink = reviewLinkForRow("SR-05");
    const truthLink = reviewLinkForRow("SR-07");
    return {
      state: dryRunSafe ? "dry-run" : "待复核",
      summary: dryRunSafe
        ? `dry-run 路径就绪 · ${plans.length} plan / ${observations.length} obs / ${reviews.length} SR`
        : `沙盒合同待复核 · ${plans.length} plan / ${observations.length} obs`,
      path: plans.length
        ? `${compactRailLabel(planNode)} -> ${compactRailLabel(observationNode)}`
        : "无候选沙盒路径",
      node: compactRailLabel(planNode),
      snapshot: plans.length
        ? `${compactRailLabel(firstPlan.signal_name || firstPlan.node_id)} · ${normalizeText(firstPlan.injection_mode)} · no tick`
        : "无输入快照",
      pathNodes: [
        {
          id: planId || "plan",
          kind: "PLAN",
          title: compactRailLabel(planNode || "候选计划"),
          meta: normalizeText(firstPlan.injection_mode || firstPlan.fault_scenario_id || "dry-run"),
          reviewRowId: "SR-04",
          traceId: planLink.traceId,
          reportId: planLink.reportId,
          actionLabel: "定位",
        },
        {
          id: observationId || "observe",
          kind: "NODE",
          title: compactRailLabel(observationNode || "观测节点"),
          meta: compactRailLabel(firstObservation.signal_name || firstObservation.check_zh || "observation"),
          reviewRowId: "SR-05",
          traceId: replayLink.traceId,
          reportId: replayLink.reportId,
          actionLabel: "回放",
        },
        {
          id: "candidate-boundary",
          kind: "GATE",
          title: "candidate-only",
          meta: `${reviewRowsBuilt.length} SR rows`,
          reviewRowId: "SR-07",
          traceId: truthLink.traceId,
          reportId: truthLink.reportId,
          actionLabel: "修订",
        },
      ],
      suggestions: [
        `修订单：复核 ${compactRailLabel(planNode)} 边界。`,
        `${reviewRowsBuilt.length} 条 SR 保持 candidate-only。`,
        `人工复核：${compactRailLabel(firstReview.id || firstReview.condition_zh)}。`,
      ],
      evidence: [
        {label: "计划", value: planId, reviewRowId: "SR-04", traceId: planLink.traceId, reportId: planLink.reportId},
        {label: "观测", value: observationId, reviewRowId: "SR-05", traceId: replayLink.traceId, reportId: replayLink.reportId},
        {label: "审查", value: `${reviews.length} checklist items`, reviewRowId: "SR-07", traceId: truthLink.traceId, reportId: truthLink.reportId},
      ],
    };
  }

  function renderFailureDiagnosisInspector(payload) {
    if (!diagnosisSummary) return;
    if (!payload) {
      if (diagnosisState) diagnosisState.textContent = "等待配置";
      diagnosisSummary.textContent = "等待沙盒配置后定位首个候选异常。";
      if (affectedPath) affectedPath.textContent = "待识别";
      if (firstAbnormalNode) firstAbnormalNode.textContent = "待识别";
      if (inputSnapshot) inputSnapshot.textContent = "待载入";
      if (diagnosisChain) diagnosisChain.innerHTML = '<p class="muted">生成沙盒配置后显示路径节点、证据回链和修订动作。</p>';
      if (repairSuggestions) repairSuggestions.innerHTML = "<li>生成沙盒配置后给出候选修订方向。</li>";
      if (diagnosisEvidenceLinks) diagnosisEvidenceLinks.innerHTML = '<button type="button" class="secondary" disabled>等待证据</button>';
      return;
    }
    if (isSourceDeferredSandbox(payload)) {
      if (diagnosisState) diagnosisState.textContent = "源文档暂缓";
      diagnosisSummary.textContent = payload.summary_zh || "源文档暂缓故障注入，默认不生成诊断路径。";
      if (affectedPath) affectedPath.textContent = "源文档暂缓";
      if (firstAbnormalNode) firstAbnormalNode.textContent = "无候选异常";
      if (inputSnapshot) inputSnapshot.textContent = "未启用 dry-run";
      if (diagnosisChain) diagnosisChain.innerHTML = '<p class="muted">源文档暂缓，未启用候选失败路径。</p>';
      if (repairSuggestions) repairSuggestions.innerHTML = "<li>仅可通过显式蓝图候选演示载入 sandbox candidate。</li>";
      if (diagnosisEvidenceLinks) diagnosisEvidenceLinks.innerHTML = '<button type="button" class="secondary" disabled>源文档暂缓</button>';
      return;
    }
    const diagnosis = buildFailureDiagnosis(payload);
    if (diagnosisState) diagnosisState.textContent = diagnosis.state;
    diagnosisSummary.textContent = diagnosis.summary;
    if (affectedPath) affectedPath.textContent = diagnosis.path;
    if (firstAbnormalNode) firstAbnormalNode.textContent = diagnosis.node;
    if (inputSnapshot) inputSnapshot.textContent = diagnosis.snapshot;
    if (diagnosisChain) {
      diagnosisChain.innerHTML = "";
      diagnosis.pathNodes.forEach((item) => {
        const node = document.createElement("button");
        node.type = "button";
        node.className = "sandbox-diagnosis-chain-node blueprint-row blueprint-row--diagnosis-chain";
        node.dataset.uxActionTier = "secondary";
        node.dataset.blueprint36ChainNode = "failure-path";
        node.dataset.blueprintRowPattern = "shared-v1";
        node.dataset.reviewRowId = item.reviewRowId;
        node.dataset.linkedReviewRows = item.reviewRowId;
        node.dataset.linkedTraceId = item.traceId;
        node.dataset.linkedReportId = item.reportId;
        node.dataset.blueprintColumns = "id stage path-node evidence-link action";
        node.innerHTML = `
          <span class="sandbox-diagnosis-chain-id blueprint-row-token" data-blueprint-col="id">${escapeText(item.id)}</span>
          <strong class="sandbox-diagnosis-chain-title" data-blueprint-col="path-node">${escapeText(item.title)}</strong>
          <span class="sandbox-diagnosis-chain-stage blueprint-row-chip" data-blueprint-col="stage">${escapeText(item.kind)}</span>
          <code class="sandbox-diagnosis-chain-meta" data-blueprint-col="evidence">${escapeText(item.meta)}</code>
          <span class="sandbox-diagnosis-chain-links blueprint-row-linkbar" data-blueprint-col="evidence-link" aria-label="路径回链 ${escapeText(item.traceId)} ${escapeText(item.reportId)}">
            <span class="sandbox-diagnosis-chain-link-token blueprint-row-token blueprint-row-token--trace" data-link-kind="trace">${escapeText(item.traceId)}</span>
            <span class="sandbox-diagnosis-chain-link-token blueprint-row-token blueprint-row-token--report" data-link-kind="report">${escapeText(item.reportId)}</span>
          </span>
          <span class="sandbox-diagnosis-chain-action blueprint-row-chip" data-blueprint-col="action">${escapeText(item.actionLabel)}</span>
        `;
        node.addEventListener("click", () => {
          const row = buildSandboxReviewRows(payload).find((reviewRow) => reviewRow.id === item.reviewRowId);
          if (row) activateReviewRow(row);
        });
        diagnosisChain.appendChild(node);
      });
    }
    if (repairSuggestions) {
      repairSuggestions.innerHTML = diagnosis.suggestions
        .map((item) => `<li>${escapeText(item)}</li>`)
        .join("");
    }
    if (diagnosisEvidenceLinks) {
      diagnosisEvidenceLinks.innerHTML = "";
      diagnosis.evidence.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "secondary sandbox-diagnosis-evidence-link";
        button.dataset.blueprint36EvidenceLink = "diagnosis";
        button.dataset.linkedReviewRows = item.reviewRowId;
        button.dataset.linkedTraceId = item.traceId;
        button.dataset.linkedReportId = item.reportId;
        button.innerHTML = `
          <span>${escapeText(item.label)}</span>
          <code>${escapeText(item.traceId)} / ${escapeText(item.reportId)}</code>
        `;
        button.addEventListener("click", () => renderEvidenceRows(`诊断证据：${item.label}`, [
          {label: "失败摘要", value: diagnosis.summary},
          {label: "受影响路径", value: diagnosis.path},
          {label: item.label, value: item.value},
          {label: "审查行", value: item.reviewRowId},
          {label: "报告章节", value: item.reportId},
          {label: "修订建议", value: diagnosis.suggestions[0]},
        ]));
        diagnosisEvidenceLinks.appendChild(button);
      });
    }
  }

  function firstSourceAnchor(payload) {
    const buckets = [
      sandboxList(payload, "sandbox_injection_plan"),
      sandboxList(payload, "observation_points"),
      sandboxList(payload, "review_checklist"),
    ];
    for (const bucket of buckets) {
      for (const item of bucket) {
        const anchors = Array.isArray(item && item.source_anchors) ? item.source_anchors : [];
        if (anchors.length) return anchors[0];
      }
    }
    return null;
  }

  function buildEvidenceTraceRows(payload) {
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const observations = sandboxList(payload, "observation_points");
    const reviews = sandboxList(payload, "review_checklist");
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const reportSections = buildReplayReportSections(payload);
    const anchor = firstSourceAnchor(payload);
    const primaryPlan = plans[0] || {};
    const traceLink = (traceId, stage, actionLabel) => {
      const reviewRowId = primaryReviewRowForTrace(traceId);
      const link = reviewLinkForRow(reviewRowId);
      return {stage, actionLabel, reviewRowId, reportId: link.reportId};
    };
    return [
      {
        id: "ET-04",
        title: "报告预览",
        value: `${reportSections.length} sections linked`,
        ...traceLink("ET-04", "REPORT", "报告"),
        linkedReviewRows: reviewRowsForTrace("ET-04"),
        rows: [
          {label: "report section", value: "sandbox replay review package"},
          {label: "related run frames", value: `${observations.length} observation points`},
          {label: "related faults", value: `${plans.length} sandbox plans`},
          {label: "report sections", value: reportSections.map((item) => item.title).join(" / ")},
          {label: "controller truth", value: `controller_truth_modified:${Boolean(payload && payload.controller_truth_modified)}`},
        ],
      },
      {
        id: "ET-01",
        title: "来源锚点",
        value: anchor ? normalizeText(anchor.id || anchor.kind) : "candidate source",
        ...traceLink("ET-01", "SOURCE", "来源"),
        linkedReviewRows: reviewRowsForTrace("ET-01"),
        rows: [
          {label: "source excerpt", value: anchor ? normalizeText(anchor.quote_zh || anchor.quote || anchor.text) : "候选节点来源待人工复核。"},
          {label: "anchor ID", value: anchor ? normalizeText(anchor.id) : "ui-blueprint-preview"},
          {label: "requirement level", value: anchor ? normalizeText(anchor.requirement_level || anchor.level) : "candidate"},
          {label: "confidence", value: normalizeText(anchor && (anchor.confidence || anchor.confidence_label))},
        ],
      },
      {
        id: "ET-02",
        title: "运行帧",
        value: `${plans.length} plans / ${observations.length} points`,
        ...traceLink("ET-02", "RUN", "定位"),
        linkedReviewRows: reviewRowsForTrace("ET-02"),
        rows: [
          {label: "related run frames", value: "dry-run only"},
          {label: "primary plan", value: normalizeText(primaryPlan.id)},
          {label: "related faults", value: plans.map((item) => item && item.fault_scenario_id).filter(Boolean).join(", ") || "未提供"},
          {label: "input snapshot", value: normalizeText(primaryPlan.signal_name || primaryPlan.node_id)},
        ],
      },
      {
        id: "ET-03",
        title: "审查行",
        value: `${reviewRowsBuilt.length} review rows`,
        ...traceLink("ET-03", "REVIEW", "审查"),
        linkedReviewRows: reviewRowsForTrace("ET-03"),
        rows: [
          {label: "reviewer note", value: reviews[0] ? normalizeText(reviews[0].condition_zh || reviews[0].pass_criteria_zh) : "等待人工审查。"},
          {label: "blueprint rows", value: reviewRowsBuilt.map((item) => item.id).join(", ")},
          {label: "candidate-only", value: "truth_effect:none / certification_claim:none"},
        ],
      },
    ];
  }

  function renderEvidenceTraceRows(payload) {
    if (!evidenceTraceRows) return;
    evidenceTraceRows.innerHTML = "";
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (evidenceTraceCount) evidenceTraceCount.textContent = "0 links";
      evidenceTraceRows.innerHTML = '<p class="muted">暂无证据追踪。生成沙盒配置后显示来源、运行、审查与报告回链。</p>';
      return;
    }
    const rows = buildEvidenceTraceRows(payload);
    if (evidenceTraceCount) evidenceTraceCount.textContent = `${rows.length} links`;
    rows.forEach((item) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "sandbox-evidence-trace-row blueprint-row blueprint-row--evidence-chain";
      row.dataset.evidenceTraceId = item.id;
      row.dataset.blueprintRowPattern = "shared-v1";
      row.dataset.linkedReviewRows = (item.linkedReviewRows || []).join(" ");
      row.dataset.linkedReportId = item.reportId;
      row.dataset.blueprintColumns = "id stage title evidence review-report action";
      row.setAttribute("data-blueprint36-evidence-row", "evidence-chain");
      row.innerHTML = `
        <span class="sandbox-evidence-trace-id blueprint-row-token" data-blueprint-col="id">${escapeText(item.id)}</span>
        <strong class="sandbox-evidence-trace-title" data-blueprint-col="title">${escapeText(item.title)}</strong>
        <span class="sandbox-evidence-trace-stage blueprint-row-chip" data-blueprint-col="stage">${escapeText(item.stage)}</span>
        <code class="sandbox-evidence-trace-value" data-blueprint-col="evidence">${escapeText(item.value)}</code>
        <span class="sandbox-evidence-trace-links blueprint-row-linkbar" data-blueprint-col="review-report" aria-label="证据回链 ${escapeText(item.reviewRowId)} ${escapeText(item.reportId)}">
          <span class="sandbox-evidence-trace-link-token blueprint-row-token blueprint-row-token--trace" data-link-kind="review">${escapeText(item.reviewRowId)}</span>
          <span class="sandbox-evidence-trace-link-token blueprint-row-token blueprint-row-token--report" data-link-kind="report">${escapeText(item.reportId)}</span>
        </span>
        <span class="sandbox-evidence-trace-action blueprint-row-chip" data-blueprint-col="action">${escapeText(item.actionLabel)}</span>
      `;
      row.addEventListener("click", () => activateLinkedInspector(
        {
          origin: "evidence-trace",
          reviewRowId: item.reviewRowId,
          traceId: item.id,
          reportId: item.reportId,
        },
        `证据追踪：${item.title}`,
        item.rows,
      ));
      evidenceTraceRows.appendChild(row);
    });
    applyReviewSelection();
  }

  function buildReplayReportSections(payload) {
    const plans = sandboxList(payload, "sandbox_injection_plan");
    const observations = sandboxList(payload, "observation_points");
    const reviews = sandboxList(payload, "review_checklist");
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const execution = payload && payload.execution_contract ? payload.execution_contract : {};
    const sourceAnchor = firstSourceAnchor(payload);
    const truthSafe = payload && payload.truth_effect === "none"
      && payload.certification_claim === "none"
      && payload.controller_truth_modified === false;
    return [
      {
        id: "RP-01",
        title: "摘要",
        metric: `${plans.length} plan`,
        rows: [
          {label: "report section", value: "摘要"},
          {label: "概况", value: payload && payload.summary_zh ? payload.summary_zh : "沙盒 dry-run 候选报告。"},
          {label: "节点", value: `${observations.length} observation points`},
          {label: "事件", value: `${plans.length + reviews.length} candidate events`},
        ],
      },
      {
        id: "RP-02",
        title: "需求来源",
        metric: sourceAnchor ? normalizeText(sourceAnchor.id || sourceAnchor.kind) : "candidate",
        rows: [
          {label: "report section", value: "需求来源"},
          {label: "source excerpt", value: sourceAnchor ? normalizeText(sourceAnchor.quote_zh || sourceAnchor.quote || sourceAnchor.text) : "候选预览无直接原文摘录。"},
          {label: "anchor ID", value: sourceAnchor ? normalizeText(sourceAnchor.id) : "ui-blueprint-preview"},
          {label: "requirement level", value: sourceAnchor ? normalizeText(sourceAnchor.requirement_level || sourceAnchor.level) : "candidate"},
        ],
      },
      {
        id: "RP-03",
        title: "逻辑图",
        metric: `${observations.length} node`,
        rows: [
          {label: "report section", value: "逻辑图"},
          {label: "相关节点", value: observations.map((item) => item && item.node_id).filter(Boolean).join(", ") || "未提供"},
          {label: "相关信号", value: observations.map((item) => item && item.signal_name).filter(Boolean).join(", ") || "未提供"},
          {label: "canvas link", value: "logic-builder candidate canvas"},
        ],
      },
      {
        id: "RP-04",
        title: "仿真参数",
        metric: "dry-run",
        rows: [
          {label: "report section", value: "仿真参数"},
          {label: "run_tick", value: String(Boolean(execution.run_tick))},
          {label: "simulate", value: String(Boolean(execution.simulate))},
          {label: "dry_run_only", value: String(execution.dry_run_only !== false)},
        ],
      },
      {
        id: "RP-05",
        title: "故障覆盖",
        metric: `${plans.length}/${observations.length}`,
        rows: [
          {label: "report section", value: "故障覆盖"},
          {label: "related faults", value: plans.map((item) => item && item.fault_scenario_id).filter(Boolean).join(", ") || "未提供"},
          {label: "related run frames", value: observations.map((item) => item && item.id).filter(Boolean).join(", ") || "未提供"},
          {label: "coverage evidence", value: payload && payload.plan_coverage_completion ? normalizeText(payload.plan_coverage_completion.strategy) : "模型返回计划覆盖"},
        ],
      },
      {
        id: "RP-06",
        title: "沙盒审查",
        metric: `${reviewRowsBuilt.length} SR`,
        rows: [
          {label: "report section", value: "沙盒审查"},
          {label: "review rows", value: reviewRowsBuilt.map((item) => `${item.id}:${item.label}`).join(", ")},
          {label: "reviewer note", value: reviews[0] ? normalizeText(reviews[0].condition_zh || reviews[0].pass_criteria_zh) : "等待人工审查。"},
          {label: "candidate-only", value: "truth_effect:none / certification_claim:none"},
        ],
      },
      {
        id: "RP-07",
        title: "未决风险",
        metric: truthSafe ? "0 diff" : "risk",
        rows: [
          {label: "report section", value: "未决风险"},
          {label: "controller truth", value: `controller_truth_modified:${Boolean(payload && payload.controller_truth_modified)}`},
          {label: "certification claim", value: normalizeText(payload && payload.certification_claim)},
          {label: "next action", value: truthSafe ? "可生成候选修订单，仍需人工审查。" : "停止并复核候选态边界。"},
        ],
      },
    ];
  }

  function buildReplayTimelineEvents(payload) {
    if (!payload || isSourceDeferredSandbox(payload)) return [];
    const reportSections = buildReplayReportSections(payload);
    const reportById = Object.fromEntries(reportSections.map((item) => [item.id, item]));
    const events = [
      {id: "EV-01", time: "00:00.00", label: "仿真开始", reviewRowId: "SR-05", reportId: "RP-01", level: "start"},
      {id: "EV-02", time: "00:00.60", label: "RA 门限", reviewRowId: "SR-01", reportId: "RP-03", level: "high"},
      {id: "EV-03", time: "00:01.40", label: "SW1 接通", reviewRowId: "SR-01", reportId: "RP-03", level: "high"},
      {id: "EV-04", time: "00:01.90", label: "SW2 断开", reviewRowId: "SR-02", reportId: "RP-04", level: "low"},
      {id: "EV-05", time: "00:02.20", label: "VDT 有效", reviewRowId: "SR-04", reportId: "RP-05", level: "high"},
      {id: "EV-06", time: "00:03.24", label: "TRA 达到", reviewRowId: "SR-05", reportId: "RP-01", level: "high"},
      {id: "EV-07", time: "00:04.10", label: "L1 告警触发", reviewRowId: "SR-06", reportId: "RP-06", level: "alarm"},
      {id: "EV-08", time: "00:05.30", label: "L2 告警复核", reviewRowId: "SR-03", reportId: "RP-02", level: "warn"},
      {id: "EV-09", time: "00:14.80", label: "取消逻辑执行", reviewRowId: "SR-07", reportId: "RP-07", level: "boundary"},
      {id: "EV-10", time: "00:20.00", label: "仿真结束", reviewRowId: "SR-05", reportId: "RP-01", level: "finish"},
    ];
    return events.map((event) => {
      const link = reviewLinkForRow(event.reviewRowId);
      const report = reportById[event.reportId] || {};
      return {
        ...event,
        traceId: link.traceId,
        reportTitle: report.title || event.reportId,
        metric: report.metric || "candidate",
        linkedReviewRows: reviewRowsForReport(event.reportId).includes(event.reviewRowId)
          ? reviewRowsForReport(event.reportId)
          : [event.reviewRowId],
        rows: [
          {label: "回放事件", value: `${event.id} · ${event.time}`},
          {label: "事件节点", value: event.label},
          {label: "审查行", value: event.reviewRowId},
          {label: "证据链", value: link.traceId},
          {label: "报告章节", value: `${event.reportId} · ${report.title || "回放报告"}`},
          {label: "候选态", value: "truth_effect:none / controller_truth_modified:false"},
        ],
      };
    });
  }

  function buildReplayCanvasNodes(payload) {
    if (!payload || isSourceDeferredSandbox(payload)) return {nodes: [], links: []};
    return {
      nodes: [
        {id: "ra", label: "RA", meta: "235", x: 7, y: 16, state: "verified", reviewRowId: "SR-01", reportId: "RP-03"},
        {id: "sw1", label: "SW1", meta: "ON", x: 7, y: 38, state: "verified", reviewRowId: "SR-01", reportId: "RP-03"},
        {id: "sw2", label: "SW2", meta: "OFF", x: 7, y: 60, state: "muted", reviewRowId: "SR-02", reportId: "RP-04"},
        {id: "vdt", label: "VDT", meta: "132", x: 7, y: 82, state: "verified", reviewRowId: "SR-04", reportId: "RP-05"},
        {id: "l1-threshold", label: "L1 门限", meta: ">=250", x: 28, y: 22, state: "verified", reviewRowId: "SR-01", reportId: "RP-03"},
        {id: "l2-threshold", label: "L2 门限", meta: ">=100", x: 28, y: 50, state: "verified", reviewRowId: "SR-02", reportId: "RP-04"},
        {id: "and", label: "AND", meta: "1", x: 47, y: 36, state: "verified", reviewRowId: "SR-04", reportId: "RP-05"},
        {id: "prio", label: "PRIO", meta: "1", x: 47, y: 72, state: "warn", reviewRowId: "SR-03", reportId: "RP-02"},
        {id: "latch", label: "LATCH", meta: "1", x: 66, y: 54, state: "verified", reviewRowId: "SR-05", reportId: "RP-01"},
        {id: "l1-alarm", label: "L1 告警", meta: "CAUT1", x: 88, y: 24, state: "alarm", reviewRowId: "SR-06", reportId: "RP-06"},
        {id: "l2-alarm", label: "L2 告警", meta: "CAUT2", x: 88, y: 52, state: "warn", reviewRowId: "SR-06", reportId: "RP-06"},
        {id: "cancel", label: "取消逻辑", meta: "0", x: 88, y: 80, state: "boundary", reviewRowId: "SR-07", reportId: "RP-07"},
      ],
      links: [
        {id: "ra-l1", fromNodeId: "ra", toNodeId: "l1-threshold", state: "verified", reviewRowId: "SR-01", reportId: "RP-03", lane: "condition"},
        {id: "sw2-l2", fromNodeId: "sw2", toNodeId: "l2-threshold", state: "verified", reviewRowId: "SR-02", reportId: "RP-04", lane: "condition"},
        {id: "l1-and", fromNodeId: "l1-threshold", toNodeId: "and", state: "verified", reviewRowId: "SR-01", reportId: "RP-03", lane: "logic"},
        {id: "l2-and", fromNodeId: "l2-threshold", toNodeId: "and", state: "verified", reviewRowId: "SR-02", reportId: "RP-04", lane: "logic"},
        {id: "vdt-prio", fromNodeId: "vdt", toNodeId: "prio", state: "verified", reviewRowId: "SR-04", reportId: "RP-05", lane: "fault"},
        {id: "and-latch", fromNodeId: "and", toNodeId: "latch", state: "verified", reviewRowId: "SR-05", reportId: "RP-01", lane: "replay"},
        {id: "prio-latch", fromNodeId: "prio", toNodeId: "latch", state: "warn", reviewRowId: "SR-03", reportId: "RP-02", lane: "review"},
        {id: "latch-l1", fromNodeId: "latch", toNodeId: "l1-alarm", state: "alarm", reviewRowId: "SR-06", reportId: "RP-06", lane: "alarm"},
        {id: "latch-l2", fromNodeId: "latch", toNodeId: "l2-alarm", state: "warn", reviewRowId: "SR-06", reportId: "RP-06", lane: "alarm"},
        {id: "latch-cancel", fromNodeId: "latch", toNodeId: "cancel", state: "boundary", reviewRowId: "SR-07", reportId: "RP-07", lane: "boundary"},
        {id: "truth-boundary", fromNodeId: "prio", toNodeId: "cancel", state: "muted", reviewRowId: "SR-07", reportId: "RP-07", lane: "boundary"},
      ],
    };
  }

  function replayCanvasEdgePoint(fromRect, toRect) {
    const fromCenter = {
      x: fromRect.left + fromRect.width / 2,
      y: fromRect.top + fromRect.height / 2,
    };
    const toCenter = {
      x: toRect.left + toRect.width / 2,
      y: toRect.top + toRect.height / 2,
    };
    const dx = toCenter.x - fromCenter.x;
    const dy = toCenter.y - fromCenter.y;
    if (Math.abs(dx) < 0.01 && Math.abs(dy) < 0.01) return fromCenter;
    const scaleX = Math.abs(dx) < 0.01 ? Infinity : (fromRect.width / 2) / Math.abs(dx);
    const scaleY = Math.abs(dy) < 0.01 ? Infinity : (fromRect.height / 2) / Math.abs(dy);
    const scale = Math.min(scaleX, scaleY);
    return {
      x: fromCenter.x + dx * scale,
      y: fromCenter.y + dy * scale,
    };
  }

  function syncReplayCanvasLinks() {
    if (!replayCanvasMain || !replayCanvasLinks) return;
    const canvasBox = replayCanvasMain.getBoundingClientRect();
    if (!canvasBox.width || !canvasBox.height) return;
    const nodesById = new Map(Array.from(replayCanvasMain.querySelectorAll("[data-replay-canvas-node]")).map((node) => {
      const box = node.getBoundingClientRect();
      return [node.dataset.replayCanvasNode || "", {
        left: box.left - canvasBox.left,
        top: box.top - canvasBox.top,
        width: box.width,
        height: box.height,
      }];
    }));
    Array.from(replayCanvasLinks.querySelectorAll("[data-replay-canvas-link]")).forEach((link) => {
      const sourceRect = nodesById.get(link.dataset.sourceNode || "");
      const targetRect = nodesById.get(link.dataset.targetNode || "");
      if (!sourceRect || !targetRect) return;
      const start = replayCanvasEdgePoint(sourceRect, targetRect);
      const end = replayCanvasEdgePoint(targetRect, sourceRect);
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const length = Math.max(1, Math.hypot(dx, dy));
      const angle = Math.atan2(dy, dx) * 180 / Math.PI;
      link.style.setProperty("--x", `${start.x.toFixed(2)}px`);
      link.style.setProperty("--y", `${(start.y - 1.25).toFixed(2)}px`);
      link.style.setProperty("--w", `${length.toFixed(2)}px`);
      link.style.setProperty("--r", `${angle.toFixed(2)}deg`);
      link.dataset.startX = start.x.toFixed(2);
      link.dataset.startY = start.y.toFixed(2);
      link.dataset.endX = end.x.toFixed(2);
      link.dataset.endY = end.y.toFixed(2);
    });
  }

  function renderMainReplayCanvas(payload) {
    if (!replayCanvasNodes || !replayCanvasLinks) return;
    clearChildren(replayCanvasNodes);
    clearChildren(replayCanvasLinks);
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (replayCanvasMetrics) replayCanvasMetrics.innerHTML = "<span>节点 0/0</span><span>连线 0/0</span><span>冲突 0</span><span>待确认 0</span>";
      replayCanvasNodes.innerHTML = '<p class="muted">暂无回放节点。生成沙盒配置后显示候选回放主路径。</p>';
      return;
    }
    const canvas = buildReplayCanvasNodes(payload);
    if (replayCanvasMetrics) {
      replayCanvasMetrics.innerHTML = "<span>节点 20/20</span><span>连线 23/23</span><span>冲突 0</span><span>待确认 0</span>";
    }
    canvas.links.forEach((item, index) => {
      const linkTarget = reviewLinkForRow(item.reviewRowId);
      const link = document.createElement("span");
      link.className = "sandbox-replay-canvas-link";
      link.setAttribute("data-replay-canvas-link", item.id);
      link.setAttribute("data-replay-link-index", String(index + 1));
      link.setAttribute("aria-current", "false");
      link.dataset.canvasLinkState = item.state;
      link.dataset.canvasLinkLane = item.lane || "logic";
      link.dataset.sourceNode = item.fromNodeId || "";
      link.dataset.targetNode = item.toNodeId || "";
      link.dataset.linkedReviewRows = item.reviewRowId || "";
      link.dataset.replayTraceId = linkTarget.traceId;
      link.dataset.replayReportId = item.reportId || linkTarget.reportId;
      link.style.setProperty("--x", "0px");
      link.style.setProperty("--y", "0px");
      link.style.setProperty("--w", "0px");
      link.style.setProperty("--r", "0deg");
      link.innerHTML = `<span class="sandbox-replay-canvas-link-badge">${escapeText(String(index + 1))}</span>`;
      replayCanvasLinks.appendChild(link);
    });
    canvas.nodes.forEach((item) => {
      const link = reviewLinkForRow(item.reviewRowId);
      const node = document.createElement("button");
      node.type = "button";
      node.className = "sandbox-replay-canvas-node blueprint-row";
      node.setAttribute("data-replay-canvas-node", item.id);
      node.dataset.canvasNodeState = item.state;
      node.dataset.linkedReviewRows = item.reviewRowId;
      node.dataset.replayTraceId = link.traceId;
      node.dataset.replayReportId = item.reportId;
      node.dataset.uxActionTier = "secondary";
      node.style.setProperty("--x", `${item.x}%`);
      node.style.setProperty("--y", `${item.y}%`);
      node.innerHTML = `
        <strong>${escapeText(item.label)}</strong>
        <code>${escapeText(item.meta)}</code>
      `;
      node.addEventListener("click", () => {
        const reviewRow = buildSandboxReviewRows(state.sandboxPayload).find((row) => row.id === item.reviewRowId);
        activateLinkedInspector(
          {
            origin: "replay-main-canvas",
            reviewRowId: item.reviewRowId,
            traceId: link.traceId,
            reportId: item.reportId,
          },
          `回放节点：${item.label}`,
          reviewRow ? buildReviewRowEvidence(reviewRow, state.sandboxPayload) : [
            {label: "节点", value: item.label},
            {label: "证据链", value: link.traceId},
            {label: "报告章节", value: item.reportId},
          ],
        );
      });
      replayCanvasNodes.appendChild(node);
    });
    syncReplayCanvasLinks();
    window.requestAnimationFrame(syncReplayCanvasLinks);
    if (replayCanvasMain) replayCanvasMain.dataset.canvasState = "ready";
    applyReviewSelection();
  }

  function renderMainReportRail(payload) {
    if (!mainReportRows) return;
    clearChildren(mainReportRows);
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (mainReportCount) mainReportCount.textContent = "0 sections";
      mainReportRows.innerHTML = '<p class="muted">暂无报告章节。</p>';
      return;
    }
    const sections = buildReplayReportSections(payload);
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const statusOnly = mainReportRail && mainReportRail.dataset.blueprint39Default === "status-only";
    if (mainReportCount) {
      mainReportCount.textContent = statusOnly
        ? `1 active / ${sections.length} sections`
        : `${sections.length} sections`;
    }
    sections.forEach((item) => {
      const primaryReviewRowId = primaryReviewRowForReport(item.id);
      const primaryReviewRow = reviewRowsBuilt.find((row) => row.id === primaryReviewRowId) || {};
      const link = reviewLinkForRow(primaryReviewRowId);
      const linkedRows = reviewRowsForReport(item.id);
      if (!linkedRows.includes(primaryReviewRowId)) linkedRows.push(primaryReviewRowId);
      const chapterState = reportChapterState(item.id, primaryReviewRow.state);
      const row = document.createElement("button");
      row.type = "button";
      row.className = "sandbox-main-report-row blueprint-row";
      row.setAttribute("data-main-report-id", item.id);
      row.setAttribute("data-report-chapter-kind", reportChapterKind(item.id));
      row.setAttribute("data-report-chapter-state", chapterState);
      row.dataset.linkedReviewRows = linkedRows.join(" ");
      row.dataset.linkedTraceId = link.traceId;
      row.dataset.linkedReportId = item.id;
      row.dataset.uxActionTier = "secondary";
      row.setAttribute("aria-current", "false");
      row.innerHTML = `
        <span class="sandbox-main-report-id">${escapeText(item.id)}</span>
        <strong>${escapeText(item.title)}</strong>
        <span class="sandbox-main-report-decision">${escapeText(sandboxReviewDecisionLabel(primaryReviewRow.state))}</span>
        <span class="sandbox-main-report-status" aria-hidden="true"></span>
        <code>${escapeText(item.metric)}</code>
      `;
      row.addEventListener("click", () => activateLinkedInspector(
        {
          origin: "main-report-rail",
          reviewRowId: primaryReviewRowId,
          traceId: link.traceId,
          reportId: item.id,
        },
        `报告章节：${item.title}`,
        item.rows,
      ));
      mainReportRows.appendChild(row);
    });
    if (mainReportRail) mainReportRail.dataset.reportRailState = "ready";
    applyReviewSelection();
  }

  function renderReplayReportWorkbench(payload) {
    if (!replayTimeline) return;
    replayTimeline.innerHTML = "";
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (reportStrip) reportStrip.dataset.replayState = "empty";
      if (replayClock) replayClock.textContent = "00:00:00 / 00:20:00";
      if (replayMetrics) replayMetrics.innerHTML = "<span>节点 0/0</span><span>连线 0/0</span><span>冲突 0</span><span>待确认 0</span>";
      replayTimeline.innerHTML = '<p class="muted">暂无回放时间线。生成沙盒配置后显示可点击的 SR/ET/RP 回链。</p>';
      return;
    }
    if (reportStrip) reportStrip.dataset.replayState = "paused";
    if (replayWorkbench) replayWorkbench.dataset.blueprint37State = "seeded-replay";
    if (replayClock) replayClock.textContent = "00:03:24 / 00:20:00";
    if (replayMetrics) {
      replayMetrics.innerHTML = "<span>节点 20/20</span><span>连线 23/23</span><span>冲突 0</span><span>待确认 0</span>";
    }
    buildReplayTimelineEvents(payload).forEach((item, index) => {
      const marker = document.createElement("button");
      marker.type = "button";
      marker.className = "sandbox-replay-marker blueprint-row";
      marker.setAttribute("data-replay-marker", item.id);
      marker.setAttribute("data-blueprint37-marker", "replay-event");
      marker.setAttribute("aria-current", "false");
      marker.dataset.uxActionTier = "secondary";
      marker.dataset.replayIndex = String(index + 1);
      marker.dataset.replayTime = item.time;
      marker.dataset.replayLevel = item.level;
      marker.dataset.replayTraceId = item.traceId;
      marker.dataset.replayReportId = item.reportId;
      marker.dataset.linkedReviewRows = item.linkedReviewRows.join(" ");
      marker.dataset.blueprintRowPattern = "timeline-v37";
      marker.innerHTML = `
        <span class="sandbox-replay-marker-index">${escapeText(String(index + 1))}</span>
        <strong>${escapeText(item.label)}</strong>
        <code>${escapeText(item.time)}</code>
      `;
      marker.addEventListener("click", () => activateLinkedInspector(
        {
          origin: "replay-timeline",
          reviewRowId: item.reviewRowId,
          traceId: item.traceId,
          reportId: item.reportId,
        },
        `回放事件：${item.label}`,
        item.rows,
      ));
      replayTimeline.appendChild(marker);
    });
    applyReviewSelection();
  }

  function renderReplayReportPreview(payload) {
    if (!reportSectionRows) return;
    reportSectionRows.innerHTML = "";
    if (!payload || isSourceDeferredSandbox(payload)) {
      if (reportPreviewCount) reportPreviewCount.textContent = "0 sections";
      reportSectionRows.innerHTML = '<p class="muted">暂无报告章节。生成沙盒配置后显示可回链的报告预览。</p>';
      return;
    }
    const sections = buildReplayReportSections(payload);
    if (reportPreviewCount) reportPreviewCount.textContent = `${sections.length} sections`;
    sections.forEach((item) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "sandbox-report-section-row blueprint-row blueprint-row--replay-report";
      row.dataset.reportSectionId = item.id;
      row.dataset.blueprintRowPattern = "shared-v1";
      row.dataset.rowScanKind = "replay-report";
      row.dataset.rowScanContract = "id-status-evidence-link";
      const linkedReviewRows = reviewRowsForReport(item.id);
      const primaryReviewRowId = primaryReviewRowForReport(item.id);
      const primaryReviewRow = buildSandboxReviewRows(payload).find((rowItem) => rowItem.id === primaryReviewRowId) || {};
      const link = reviewLinkForRow(primaryReviewRowId);
      row.dataset.linkedReviewRows = linkedReviewRows.join(" ");
      row.dataset.linkedTraceId = link.traceId;
      row.dataset.linkedReportId = item.id;
      row.dataset.blueprintColumns = "id section decision evidence source trace-report action";
      row.setAttribute("data-blueprint-report-row", "review-package-section");
      row.setAttribute("data-blueprint36-report-row", "replay-report");
      row.setAttribute("data-blueprint37-report-row", "preview-rail-section");
      row.innerHTML = `
        <span class="sandbox-report-section-id blueprint-row-token" data-blueprint-col="id" data-row-scan-token="id">${escapeText(item.id)}</span>
        <strong class="sandbox-report-section-title" data-blueprint-col="section">${escapeText(item.title)}</strong>
        <span class="sandbox-report-section-decision blueprint-row-chip" data-blueprint-col="decision" data-row-scan-token="status">${escapeText(sandboxReviewDecisionLabel(primaryReviewRow.state))}</span>
        <code class="sandbox-report-section-evidence" data-blueprint-col="evidence" data-row-scan-token="evidence">${escapeText(item.metric)}</code>
        <code class="sandbox-report-section-source" data-blueprint-col="source">${escapeText(primaryReviewRowId || "SR")}</code>
        <span class="sandbox-report-section-links blueprint-row-linkbar" data-blueprint-col="trace-report" data-row-scan-token="link" aria-label="报告回链 ${escapeText(link.traceId)} ${escapeText(item.id)}">
          <span class="sandbox-report-link-token blueprint-row-token blueprint-row-token--trace" data-link-kind="trace">${escapeText(link.traceId)}</span>
          <span class="sandbox-report-link-token blueprint-row-token blueprint-row-token--report" data-link-kind="report">${escapeText(item.id)}</span>
        </span>
        <span class="sandbox-report-section-action blueprint-row-chip" data-blueprint-col="action">打开</span>
      `;
      row.addEventListener("click", () => activateLinkedInspector(
        {
          origin: "replay-report",
          reviewRowId: primaryReviewRowId,
          traceId: link.traceId,
          reportId: item.id,
        },
        `报告章节：${item.title}`,
        item.rows,
      ));
      reportSectionRows.appendChild(row);
    });
    applyReviewSelection();
  }

  function appendPackageItem(parent, className, id, title, meta, extra, target) {
    if (!parent) return;
    const linkTarget = target || {};
    const row = document.createElement("article");
    row.className = `sandbox-review-package-item blueprint-row blueprint-row--review-package ${className || ""}`.trim();
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    row.setAttribute("aria-label", `${title || id || "审查包条目"}：打开主审查联动`);
    if (id) row.dataset.packageItemId = id;
    if (linkTarget.reviewRowId) row.dataset.packageTargetReviewRow = linkTarget.reviewRowId;
    if (linkTarget.traceId) row.dataset.packageTargetTraceId = linkTarget.traceId;
    if (linkTarget.reportId) row.dataset.packageTargetReportId = linkTarget.reportId;
    row.dataset.blueprintRowPattern = "shared-v1";
    row.dataset.blueprintColumns = "id section decision evidence source trace-report action";
    row.setAttribute("data-blueprint36-package-row", linkTarget.packageKind || "package-item");
    row.classList.toggle("is-linked-active", linkTarget.reviewRowId === state.activeReviewRowId);
    const decision = linkTarget.decision || "LINK";
    const evidence = linkTarget.evidence || meta || "candidate";
    const source = linkTarget.sourceLabel || extra || "candidate-only";
    const traceId = linkTarget.traceId || "ET";
    const reportId = linkTarget.reportId || "RP";
    const actionLabel = linkTarget.actionLabel || "联动";
    row.innerHTML = `
      <span class="sandbox-review-package-id blueprint-row-token" data-blueprint-col="id">${escapeText(id || "ID")}</span>
      <strong class="sandbox-review-package-title" data-blueprint-col="section">${escapeText(title || "未命名")}</strong>
      <span class="sandbox-review-package-decision blueprint-row-chip" data-blueprint-col="decision">${escapeText(decision)}</span>
      <code class="sandbox-review-package-evidence" data-blueprint-col="evidence">${escapeText(evidence)}</code>
      <code class="sandbox-review-package-source" data-blueprint-col="source">${escapeText(source)}</code>
      <span class="sandbox-review-package-links blueprint-row-linkbar" data-blueprint-col="trace-report" aria-label="审查包回链 ${escapeText(traceId)} ${escapeText(reportId)}">
        <span class="sandbox-review-package-link-token blueprint-row-token blueprint-row-token--trace" data-link-kind="trace">${escapeText(traceId)}</span>
        <span class="sandbox-review-package-link-token blueprint-row-token blueprint-row-token--report" data-link-kind="report">${escapeText(reportId)}</span>
      </span>
      <span class="sandbox-review-package-action blueprint-row-chip" data-blueprint-col="action">${escapeText(actionLabel)}</span>
    `;
    row.addEventListener("click", () => activateReviewPackageItem(linkTarget));
    row.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      activateReviewPackageItem(linkTarget);
    });
    parent.appendChild(row);
  }

  function renderReviewPackagePanel(payload) {
    if (!reviewPackagePanel) return;
    const reviewRowsBuilt = buildSandboxReviewRows(payload);
    const evidenceRowsBuilt = buildEvidenceTraceRows(payload);
    const reportSections = buildReplayReportSections(payload);
    if (reviewPackageReviewCount) reviewPackageReviewCount.textContent = `${reviewRowsBuilt.length} review rows`;
    if (reviewPackageEvidenceCount) reviewPackageEvidenceCount.textContent = `${evidenceRowsBuilt.length} evidence links`;
    if (reviewPackageReportCount) reviewPackageReportCount.textContent = `${reportSections.length} report sections`;
    clearChildren(reviewPackageReviewRows);
    clearChildren(reviewPackageEvidenceRows);
    clearChildren(reviewPackageReportRows);
    reviewRowsBuilt.forEach((item) => {
      const link = reviewLinkForRow(item.id);
      appendPackageItem(
        reviewPackageReviewRows,
        "sandbox-review-package-review-row",
        item.id,
        item.title,
        `${item.label} · ${item.evidence}`,
        link.reportId,
        {
          reviewRowId: item.id,
          traceId: link.traceId,
          reportId: link.reportId,
          packageKind: "review-package-review",
          decision: sandboxReviewDecisionLabel(item.state),
          evidence: item.evidence,
          sourceLabel: item.sourceLabel,
          actionLabel: "查看",
        },
      );
    });
    evidenceRowsBuilt.forEach((item) => {
      const reviewRowId = primaryReviewRowForTrace(item.id);
      const link = reviewLinkForRow(reviewRowId);
      appendPackageItem(
        reviewPackageEvidenceRows,
        "sandbox-review-package-evidence-row",
        item.id,
        item.title,
        item.value,
        (item.linkedReviewRows || []).join(", ") || "review links",
        {
          reviewRowId,
          traceId: item.id,
          reportId: link.reportId,
          packageKind: "review-package-evidence",
          decision: "TRACE",
          evidence: item.value,
          sourceLabel: (item.linkedReviewRows || []).join(", ") || "review links",
          actionLabel: "证据",
        },
      );
    });
    reportSections.forEach((item) => {
      const reviewRowId = primaryReviewRowForReport(item.id);
      const link = reviewLinkForRow(reviewRowId);
      const reviewRow = reviewRowsBuilt.find((rowItem) => rowItem.id === reviewRowId) || {};
      appendPackageItem(
        reviewPackageReportRows,
        "sandbox-review-package-report-row",
        item.id,
        item.title,
        item.metric,
        reviewRowsForReport(item.id).join(", ") || "report section",
        {
          reviewRowId,
          traceId: link.traceId,
          reportId: item.id,
          packageKind: "review-package-report",
          decision: sandboxReviewDecisionLabel(reviewRow.state),
          evidence: item.metric,
          sourceLabel: reviewRowsForReport(item.id).join(", ") || "report section",
          actionLabel: "打开",
        },
      );
    });
  }

  function openReviewPackagePanel(payload) {
    if (!reviewPackagePanel) return;
    closeEvidencePanel();
    toggleDetailPanel(false);
    renderReviewPackagePanel(payload);
    reviewPackagePanel.removeAttribute("aria-hidden");
    reviewPackagePanel.hidden = false;
    setActiveAuxPanel("review-package");
    if (reviewPackageClose) reviewPackageClose.focus();
  }

  function openReportPackage(title, rows) {
    if (reportPreview) {
      reportPreview.classList.add("is-emphasized");
      window.setTimeout(() => reportPreview.classList.remove("is-emphasized"), 900);
    }
    renderEvidenceRows(title, rows);
  }

  function handleReportAction(action) {
    const payload = state.sandboxPayload;
    if (!payload || isSourceDeferredSandbox(payload)) {
      openReportPackage("报告预览：未生成", [
        {label: "状态", value: payload && payload.summary_zh ? payload.summary_zh : "暂无沙盒配置。"},
        {label: "下一步", value: "先生成或载入 sandbox candidate。"},
      ]);
      return;
    }
    const sections = buildReplayReportSections(payload);
    if (action === "evidence") {
      toggleDetailPanel(true);
      openReportPackage("报告预览：证据索引", buildEvidenceTraceRows(payload).map((item) => ({
        label: item.title,
        value: item.value,
      })));
      return;
    }
    if (action === "revision") {
      openReportPackage("报告预览：生成修订单", [
        {label: "report sections", value: `${sections.length} sections`},
        {label: "handoff", value: "候选修订单将回到 logic-builder，仍需 3 个一级闸门确认。"},
        {label: "candidate-only", value: "controller_truth_modified:false"},
      ]);
      return;
    }
    if (action === "export") {
      openReviewPackagePanel(payload);
      return;
    }
    openReportPackage("报告预览：重新运行沙盒", [
      {label: "run mode", value: "dry-run only"},
      {label: "related run frames", value: `${sandboxList(payload, "observation_points").length} observation points`},
      {label: "next action", value: "使用顶部检查按钮重新生成候选配置。"},
    ]);
  }

  function renderCompactChecklist(payload) {
    const items = sandboxList(payload, "review_checklist");
    checklistCount.textContent = `${items.length} checks`;
    clearChildren(checklistStrip);
    if (!items.length) {
      checklistStrip.innerHTML = '<p class="muted">暂无审查细项。</p>';
      return;
    }
    items.slice(0, 6).forEach((item) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "sandbox-checklist-chip";
      chip.innerHTML = `<strong>${escapeText(item.category || "review")}</strong> ${escapeText(item.condition_zh || item.id || "审查条目")}`;
      chip.addEventListener("click", () => {
        const rows = [
          {label: "条目", value: normalizeText(item.id || item.condition_zh || "review")},
          {label: "类型", value: normalizeText(item.category || "review")},
          {label: "审查条件", value: normalizeText(item.condition_zh)},
          {label: "通过标准", value: normalizeText(item.pass_criteria_zh)},
          {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
        ];
        renderEvidenceRows(`审查细项：${normalizeText(item.condition_zh || item.id || "review")}`, rows);
      });
      checklistStrip.appendChild(chip);
    });
  }

  function renderExecutionContract(payload) {
    const execution = (payload && payload.execution_contract) || {};
    contract.innerHTML = "";
    const entries = [
      `run_tick:${Boolean(execution.run_tick)}`,
      `simulate:${Boolean(execution.simulate)}`,
      `dry_run_only:${execution.dry_run_only !== false}`,
    ];
    for (const entry of entries) {
      const span = document.createElement("span");
      span.className = "sandbox-contract-pill";
      span.textContent = entry;
      contract.appendChild(span);
    }
  }

  function renderSandboxInjectionPlan(payload) {
    const items = payload && payload.sandbox_injection_plan ? payload.sandbox_injection_plan : [];
    planCount.textContent = `${items.length} plans`;
    planList.innerHTML = "";
    if (!items.length) {
      planList.innerHTML = '<p class="muted">模型未返回沙盒配置建议。</p>';
      return;
    }
    for (const item of items) {
      const card = document.createElement("article");
      card.className = "sandbox-plan-card";
      card.style.cursor = "pointer";
      card.tabIndex = 0;
      card.innerHTML = `
        <strong>${escapeText(item.id || item.fault_scenario_id)}</strong>
        <code>${escapeText(item.fault_scenario_id || "scenario")} · ${escapeText(item.node_id || "node")} · ${escapeText(item.injection_mode || "mode")}</code>
        <p>${escapeText(item.safe_range_zh || "模型未返回安全范围。")}</p>
        <p>${escapeText(item.expected_effect_zh || "模型未返回预期影响。")}</p>
        <p class="sandbox-anchor">来源：${escapeText(sourceAnchorLabel(item.source_anchors))}</p>
      `;
      card.addEventListener("click", () => {
        renderEvidenceRows(`沙盒计划：${escapeText(item.id || item.fault_scenario_id)}`, [
          {label: "节点", value: normalizeText(item.node_id)},
          {label: "信号", value: normalizeText(item.signal_name)},
          {label: "注入方式", value: normalizeText(item.injection_mode)},
          {label: "安全范围", value: normalizeText(item.safe_range_zh)},
          {label: "预期影响", value: normalizeText(item.expected_effect_zh)},
          {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
        ]);
      });
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          card.click();
        }
      });
      planList.appendChild(card);
    }
  }

  function renderObservationPoints(payload) {
    const items = payload && payload.observation_points ? payload.observation_points : [];
    observationCount.textContent = `${items.length} points`;
    observationList.innerHTML = "";
    if (!items.length) {
      observationList.innerHTML = '<p class="muted">模型未返回观测点。</p>';
      return;
    }
    for (const item of items) {
      const card = document.createElement("article");
      card.className = "sandbox-observation-card";
      card.style.cursor = "pointer";
      card.tabIndex = 0;
      card.innerHTML = `
        <strong>${escapeText(item.signal_name || item.id)}</strong>
        <code>${escapeText(item.node_id || "node:none")}</code>
        <p>${escapeText(item.check_zh || "观察该信号是否符合预期。")}</p>
      `;
      card.addEventListener("click", () => {
        renderEvidenceRows(`观测点：${escapeText(item.signal_name || item.id)}`, [
          {label: "节点", value: normalizeText(item.node_id)},
          {label: "信号", value: normalizeText(item.signal_name)},
          {label: "检查说明", value: normalizeText(item.check_zh)},
          {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
        ]);
      });
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          card.click();
        }
      });
      observationList.appendChild(card);
    }
  }

  function renderReviewChecklist(payload) {
    const items = payload && payload.review_checklist ? payload.review_checklist : [];
    reviewCount.textContent = `${items.length} checks`;
    reviewList.innerHTML = "";
    if (!items.length) {
      reviewList.innerHTML = '<p class="muted">模型未返回审查清单。</p>';
      return;
    }
    for (const item of items) {
      const card = document.createElement("article");
      card.className = "sandbox-review-item";
      card.style.cursor = "pointer";
      card.tabIndex = 0;
      card.innerHTML = `
        <strong>${escapeText(item.condition_zh || item.id)}</strong>
        <code>${escapeText(item.category || "review")}</code>
        <p>${escapeText(item.pass_criteria_zh || "需要人工确认。")}</p>
      `;
      card.addEventListener("click", () => {
        renderEvidenceRows(`审查细项：${normalizeText(item.condition_zh || item.id)}`, [
          {label: "ID", value: normalizeText(item.id)},
          {label: "类型", value: normalizeText(item.category)},
          {label: "审查条件", value: normalizeText(item.condition_zh)},
          {label: "通过标准", value: normalizeText(item.pass_criteria_zh)},
          {label: "来源", value: sourceAnchorLabel(item.source_anchors)},
        ]);
      });
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          card.click();
        }
      });
      reviewList.appendChild(card);
    }
  }

  function renderSandboxPayload(payload) {
    const safePayload = payload || {};
    state.sandboxPayload = safePayload;
    if (payload && !isSourceDeferredSandbox(safePayload) && !state.activeReviewRowId && !readIncomingReviewSelection()) {
      state.activeReviewRowId = "SR-06";
    }
    if (!payload) {
      resultState.textContent = "未生成";
      resultSummary.textContent = "等待模型生成沙盒配置。";
    } else if (isSourceDeferredSandbox(safePayload)) {
      resultState.textContent = "源文档暂缓";
      resultSummary.textContent = safePayload.summary_zh || "源文档声明故障注入本轮暂不考虑，沙盒计划未生成。";
    } else {
      resultState.textContent = "配置已生成";
      resultSummary.textContent = safePayload.summary_zh || "模型已生成沙盒故障注入配置建议。";
    }
    renderFlags(safePayload);
    renderQualitySummary(safePayload);
    renderSelfRepairDetails(safePayload);
    renderPlanCoverageCompletionEvidence(safePayload);
    renderExecutionContract(safePayload);
    renderEvidenceTiles(payload);
    renderSandboxReviewRows(safePayload);
    renderMainReplayCanvas(payload);
    renderFailureDiagnosisInspector(payload);
    renderEvidenceTraceRows(payload);
    renderMainReportRail(payload);
    renderReplayReportWorkbench(payload);
    renderReplayReportPreview(payload);
    renderCompactChecklist(safePayload);
    renderPrimaryReviewGates(safePayload);
    renderSandboxInjectionPlan(safePayload);
    renderObservationPoints(safePayload);
    renderReviewChecklist(safePayload);
    renderBurdenSummary(safePayload);
    renderWorkflowOverview();
    if (payload) {
      saveFaultSandboxPlanDraft(safePayload);
    }
    applyIncomingReviewSelection();
    setBusy(false);
  }

  async function requestFaultSandboxPlan() {
    const payload = state.faultPreparationPayload || {};
    const response = await fetch("/api/requirements-intake/prepare-fault-injection/sandbox", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: provider.value,
        allow_fallback: provider.value !== "deepseek",
        fault_injection_preparation_payload: payload,
        boundary_answers: payload.boundary_answers || [],
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(result, "沙盒配置生成失败，请重新生成或切换模型。"));
      error.payload = result;
      throw error;
    }
    return result;
  }

  async function generateSandboxPlan() {
    if (!state.faultPreparationPayload) {
      failTask("缺少故障准备草稿", "请先在故障准备页保存边界回答。");
      return;
    }
    if (state.faultPreparationPayload.first_visit_preview) {
      beginTask("刷新沙盒预览", "正在刷新本地 candidate-only 沙盒预览。");
      loadFirstVisitSandboxPreview();
      setProgress(96, "审查清单", "本地预览已生成 7 条蓝图审查行。", "review");
      finishTask("沙盒预览已刷新", "未调用模型、tick 或控制器真值。");
      return;
    }
    if (state.faultPreparationPayload.template_preview) {
      beginTask("刷新 DOCX 模板沙盒", "正在刷新本地 candidate-only 模板沙盒预览。");
      loadTemplateSandboxPreview({refresh: true});
      setProgress(96, "审查清单", "模板预览已生成 7 条蓝图审查行。", "review");
      finishTask("DOCX 模板沙盒已刷新", "未调用模型、tick 或控制器真值。");
      return;
    }
    beginTask("读取准备草稿", "正在读取故障候选、注入点和边界回答。");
    setBusy(true);
    try {
      setProgress(28, "提交模型", "正在让模型生成 dry-run 沙盒配置建议。", "model");
      const payload = await requestFaultSandboxPlan();
      setProgress(84, "生成配置", "模型已返回沙盒配置建议，正在整理观测点。", "plan");
      renderSandboxPayload(payload);
      setProgress(96, "审查清单", "审查清单已生成。", "review");
      finishTask("沙盒配置完成", "模型已生成只读沙盒配置建议。");
    } catch (error) {
      resultState.textContent = "生成失败";
      const message = error.message || "沙盒配置生成失败，请重新生成或切换模型。";
      resultSummary.textContent = message;
      renderSelfRepairDetails(error.payload);
      failTask("生成失败", message);
    } finally {
      setBusy(false);
    }
  }

  function boot() {
    state.incomingReviewSelection = readIncomingReviewSelection();
    loadFaultPreparationDraft();
    renderSource();
    renderBurdenSummary(null);
    renderWorkflowOverview();
    const draft = loadFaultSandboxPlanDraft();
    if (draft) {
      beginTask("载入沙盒草稿", "正在读取上次保存的沙盒配置建议。");
      renderSandboxPayload(draft);
      finishTask("已载入沙盒草稿", "可以继续审查该配置建议。");
    } else if (state.faultPreparationPayload) {
      generateSandboxPlan();
    } else {
      beginTask("载入首次沙盒预览", "未发现故障准备草稿；正在载入本地 candidate-only 沙盒闭环。");
      loadFirstVisitSandboxPreview();
      setProgress(96, "审查清单", "本地预览已生成审查行、证据链和报告章节。", "review");
      finishTask("首次沙盒预览已载入", "默认展示沙盒审查闭环；未调用模型、tick 或控制器。");
    }
    setBusy(false);
  }

  generateButton.addEventListener("click", () => {
    closeEvidencePanel();
    closeReviewPackagePanel();
    window.localStorage.removeItem(SANDBOX_PLAN_KEY);
    renderSandboxPayload(null);
    generateSandboxPlan();
  });
  reviewNextButton.addEventListener("click", () => {
    if (!getReviewCompletion().isComplete) {
      updateReviewGate();
      return;
    }
    saveRevisionHandoff();
    window.location.href = "/logic-builder";
  });
  backButton.addEventListener("click", () => {
    window.location.href = "/fault-injection-prepare";
  });
  if (detailPanelToggle) {
    detailPanelToggle.addEventListener("click", () => toggleDetailPanel());
  }
  reportActionButtons.forEach((button) => {
    button.addEventListener("click", () => handleReportAction(button.dataset.sandboxReportAction));
  });
  mainReportActionButtons.forEach((button) => {
    button.addEventListener("click", () => handleReportAction(button.dataset.mainReportAction));
  });
  replayControlButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (reportStrip) reportStrip.dataset.replayState = button.dataset.replayControl || "paused";
    });
  });
  evidenceClose.addEventListener("click", closeEvidencePanel);
  evidencePopover.addEventListener("click", (event) => {
    if (event.target === evidencePopover) {
      closeEvidencePanel();
    }
  });
  if (reviewPackageClose) {
    reviewPackageClose.addEventListener("click", closeReviewPackagePanel);
  }
  if (reviewPackagePanel) {
    reviewPackagePanel.addEventListener("click", (event) => {
      if (event.target === reviewPackagePanel) {
        closeReviewPackagePanel();
      }
    });
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && reviewPackagePanel && !reviewPackagePanel.hidden) {
      closeReviewPackagePanel();
      return;
    }
    if (event.key === "Escape" && !evidencePopover.hidden) {
      closeEvidencePanel();
    }
  });
  primaryGateInputs.forEach((input) => {
    input.addEventListener("change", updateReviewGate);
  });
  window.addEventListener("resize", syncReplayCanvasLinks);
  setPrimaryGateInputsEnabled(false);
  setActiveAuxPanel("none");
  boot();
})();

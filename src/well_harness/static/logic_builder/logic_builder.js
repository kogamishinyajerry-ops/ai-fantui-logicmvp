(function () {
  "use strict";

  const INPUT_KEY = "ai-fantui-requirements-intake-ready-v1";
  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const HISTORY_KEY = "ai-fantui-logic-builder-change-history-v1";
  const ANNOTATION_BATCH_KEY = "ai-fantui-logic-builder-annotation-batch-v1";
  const FAULT_DRAFT_KEY = "ai-fantui-fault-injection-preparation-v1";
  const REVISION_HANDOFF_KEY = "ai-fantui-fault-injection-sandbox-revision-handoff-v1";
  const LEVER_SNAPSHOT_API = "/api/lever-snapshot";
  const CIRCUIT_EVAL_DEBOUNCE_MS = 120;
  const CIRCUIT_SHORT_LABELS = {
    sw1: "SW1",
    sw2: "SW2",
    radio_altitude_ft: "RA<6ft",
    aircraft_on_ground: "在地",
    engine_running: "发动机运行",
    reverser_inhibited: "未抑制",
    eec_enable: "EEC允许",
    n1k: "N1K门限",
    tls115: "TLS供电",
    tls_unlocked: "TLS解锁",
    vdt90: "VDT≥90%",
    etrac_540v: "ETRAC 540V",
    eec_deploy: "EEC部署",
    pls_power: "PLS供电",
    pdu_motor: "PDU电机",
    logic1: "L1",
    logic2: "L2",
    logic3: "L3",
    logic4: "L4",
    thr_lock: "油门锁释放",
  };
  const CIRCUIT_READABLE_LANES = {
    sw1: "sw",
    sw2: "sw",
  };
  const CIRCUIT_LOCAL_COMPLETION_IDS = new Set([
    "sw1",
    "sw2",
    "radio_altitude_ft",
    "aircraft_on_ground",
    "engine_running",
    "reverser_inhibited",
    "eec_enable",
    "n1k",
    "logic1",
    "logic2",
    "logic3",
    "logic4",
    "tls115",
    "tls_unlocked",
    "vdt90",
    "etrac_540v",
    "eec_deploy",
    "pls_power",
    "pdu_motor",
    "thr_lock",
  ]);
  const CIRCUIT_PROVENANCE_FILTERS = new Set(["all", "source", "assumption", "local"]);
  const CIRCUIT_PROVENANCE_LABELS = {
    "source": "原文锚点",
    "assumption": "模型假设",
    "local": "本地补齐",
  };
  const state = {
    requirementsPayload: null,
    drawingPayload: null,
    timer: null,
    circuitEvaluationTimer: null,
    circuitEvaluationPayload: null,
    circuitEvaluationBusy: false,
    startedAt: 0,
    percent: 0,
    busy: false,
    selectedNodeId: "",
    selectedTargetType: "",
    selectedTargetId: "",
    selectedTargetLabel: "",
    interpretationPayload: null,
    changeHistory: [],
    annotationDrafts: [],
    activeChangeId: "",
    activeCircuitPreset: "",
    provenanceFilter: "all",
    revisionHandoff: null,
    annotationPopoverX: 0,
    annotationPopoverY: 0,
  };

  const $ = (id) => document.getElementById(id);
  const provider = $("logic-provider");
  const logicBottomProvider = $("logic-bottom-provider");
  const regenerate = $("logic-regenerate");
  const faultNext = $("logic-fault-next");
  const back = $("logic-back");
  const process = $("logic-process");
  const processTitle = $("logic-process-title");
  const processDetail = $("logic-process-detail");
  const processElapsed = $("logic-process-elapsed");
  const processFill = $("logic-process-fill");
  const steps = {
    load: $("logic-step-load"),
    model: $("logic-step-model"),
    layout: $("logic-step-layout"),
    render: $("logic-step-render"),
  };
  const streamChunks = $("logic-stream-chunks");
  const STREAM_CHUNK_COPY = {
    load: "已读取需求：准备生成逻辑链路",
    model: "DeepSeek 正在绘制：等待节点与连线",
    layout: "结构复核：校验 20/23 结构",
    render: "渲染电路：更新画布与验收状态",
  };
  const inputTitle = $("logic-input-title");
  const inputSummary = $("logic-input-summary");
  const resultState = $("logic-result-state");
  const resultSummary = $("logic-result-summary");
  const resultFlags = $("logic-result-flags");
  const sourceTrustSummary = $("logic-source-trust-summary");
  const statusSourceCount = $("logic-status-source-count");
  const statusLocalCount = $("logic-status-local-count");
  const statusAssumptionCount = $("logic-status-assumption-count");
  const burdenAction = $("logic-burden-action");
  const burdenOutputs = $("logic-burden-outputs");
  const workflowStage = $("logic-workflow-stage");
  const workflowDetail = $("logic-workflow-detail");
  const workflowSteps = Array.from(document.querySelectorAll("#logic-workflow-steps .logic-workflow-step"));
  const notes = $("logic-notes");
  const canvas = $("logic-canvas");
  const templateEntry = $("logic-template-entry");
  const templateActionButtons = Array.from(document.querySelectorAll("[data-template-action], [data-command-template-action]"));
  const circuitSvg = $("logic-circuit-svg");
  const svg = $("logic-svg");
  const nodeLayer = $("logic-node-layer");
  const panelLayer = $("logic-panel-layer");
  const logicCanvasToolbar = $("logic-canvas-compact-toolbar");
  const counts = $("logic-canvas-counts");
  const source = $("logic-canvas-source");
  const provenanceFilter = $("logic-provenance-filter");
  const provenanceFilterButtons = Array.from(document.querySelectorAll("[data-provenance-filter]"));
  const reconstructionModePanel = $("logic-reconstruction-mode-panel");
  const reconstructionMode = $("logic-reconstruction-mode");
  const reconstructionFidelity = $("logic-reconstruction-fidelity");
  const demoBridge = $("logic-demo-bridge");
  const drawingStreamTimeline = $("logic-drawing-stream-timeline");
  const drawingStreamEvents = $("logic-drawing-stream-events");
  const annotationPopover = $("logic-annotation-popover");
  const annotationSubmitBar = $("logic-annotation-submit-bar");
  const selectedTargetLabel = $("logic-selected-target-label");
  const annotationSource = $("logic-annotation-source");
  const annotationParams = $("logic-annotation-params");
  const nodeCommentText = $("logic-node-comment-text");
  const addAnnotationButton = $("logic-add-annotation");
  const annotationCount = $("logic-annotation-count");
  const annotationList = $("logic-annotation-list");
  const annotationSubmitState = $("logic-annotation-submit-state");
  const submitAnnotationsButton = $("logic-submit-annotations");
  const batchInterpretationPanel = $("logic-batch-interpretation-panel");
  const batchSummary = $("logic-batch-summary");
  const batchConflictSummary = $("logic-batch-conflict-summary");
  const batchProposedChanges = $("logic-batch-proposed-changes");
  const batchConfirmationQuestion = $("logic-batch-confirmation-question");
  const batchConfirmUpdateButton = $("logic-batch-confirm-update");
  const batchDismissButton = $("logic-batch-dismiss");
  const objectContextDrawer = $("logic-object-context-drawer");
  const logicContextTitle = $("logic-context-title");
  const logicContextSource = $("logic-context-source");
  const logicContextParams = $("logic-context-params");
  const logicContextCommentShortcut = $("logic-context-comment-shortcut");
  const selectedNode = $("logic-selected-node");
  const logicDetailSelectedNode = $("logic-detail-selected-node");
  const logicDetailSourceSummary = $("logic-detail-source-summary");
  const logicDetailNextAction = $("logic-detail-next-action");
  const changeText = $("logic-change-text");
  const changeLoopDetails = $("logic-change-loop-details");
  const changeHistoryDetails = $("logic-change-history-details");
  const workbenchDrawer = $("logic-workbench-drawers");
  const workbenchTabButtons = Array.from(document.querySelectorAll("[data-workbench-tab]"));
  const workbenchPanels = Array.from(document.querySelectorAll("[data-workbench-panel]"));
  const logicShell = document.querySelector(".logic-shell");
  const logicModeButtons = Array.from(document.querySelectorAll("[data-logic-mode]"));
  const commandPalette = $("logic-command-palette");
  const commandPaletteOpen = $("logic-command-palette-open");
  const commandPaletteClose = $("logic-command-palette-close");
  const commandPaletteFilter = $("logic-command-palette-filter");
  const commandPaletteStatus = $("logic-command-palette-status");
  const commandPaletteItems = Array.from(document.querySelectorAll("#logic-command-palette-list button, #logic-command-palette-list a"));
  const panelToggleButtons = Array.from(document.querySelectorAll("[data-panel-toggle]"));
  const bottomDrawer = $("logic-run-parameter-drawer");
  const bottomDrawerButtons = Array.from(document.querySelectorAll("[data-bottom-drawer-tab]"));
  const bottomDrawerPanels = Array.from(document.querySelectorAll("[data-bottom-drawer-panel]"));
  const bottomDrawerClose = $("logic-bottom-drawer-close");
  const runTimeline = $("logic-run-timeline");
  const runState = $("logic-run-state");
  const bottomRunState = $("logic-bottom-run-state");
  const bottomRunTime = $("logic-bottom-run-time");
  const bottomRunCursor = $("logic-bottom-run-cursor");
  const bottomRunNodeCount = $("logic-bottom-run-node-count");
  const bottomRunEdgeCount = $("logic-bottom-run-edge-count");
  const logicAuxPanels = {
    "left-rail": null,
    "right-inspector": null,
    "bottom-drawer": null,
    "command-palette": null,
  };
  const drawerPreset = $("logic-drawer-preset");
  const drawerInputs = {
    ra: $("logic-drawer-ra"),
    tra: $("logic-drawer-tra"),
    vdt: $("logic-drawer-vdt"),
    samplingRate: $("logic-drawer-sampling-rate"),
    stepSize: $("logic-drawer-step-size"),
    sw1: $("logic-drawer-sw1"),
    sw2: $("logic-drawer-sw2"),
  };
  const drawerReadouts = {
    ra: $("logic-drawer-ra-value"),
    tra: $("logic-drawer-tra-value"),
    vdt: $("logic-drawer-vdt-value"),
    samplingRate: $("logic-drawer-sampling-rate-value"),
    stepSize: $("logic-drawer-step-size-value"),
  };
  const revisionHandoff = $("logic-revision-handoff");
  const revisionHandoffTitle = $("logic-revision-handoff-title");
  const revisionHandoffSummary = $("logic-revision-handoff-summary");
  const revisionHandoffMetrics = $("logic-revision-handoff-metrics");
  const fillHandoffDraftButton = $("logic-fill-handoff-draft");
  const submitChangeButton = $("logic-submit-change");
  const clearChangeButton = $("logic-clear-change");
  const interpretationBox = $("logic-interpretation-box");
  const interpretationState = $("logic-interpretation-state");
  const interpretationSummary = $("logic-interpretation-summary");
  const interpretationMatch = $("logic-interpretation-match");
  const proposedChanges = $("logic-proposed-changes");
  const interpretationQuestion = $("logic-interpretation-question");
  const confirmChangeButton = $("logic-confirm-change");
  const cancelChangeButton = $("logic-cancel-change");
  const historyCount = $("logic-change-history-count");
  const historyList = $("logic-change-history-list");
  const circuitEvalPanel = $("logic-circuit-eval-panel");
  const logicCircuitInputDetails = $("logic-circuit-input-details");
  const circuitPresetStatus = $("logic-circuit-preset-status");
  const circuitStatusBadge = $("logic-circuit-status-badge");
  const circuitStatusSummary = $("logic-circuit-status-summary");
  const circuitPresetSelect = $("logic-circuit-preset-select");
  const circuitPresetButtons = Array.from(document.querySelectorAll("[data-circuit-preset]"));
  const circuitInputs = {
    tra: $("logic-circuit-tra"),
    ra: $("logic-circuit-ra"),
    n1k: $("logic-circuit-n1k"),
    vdt: $("logic-circuit-vdt"),
    engineRunning: $("logic-circuit-engine-running"),
    aircraftOnGround: $("logic-circuit-aircraft-on-ground"),
    reverserInhibited: $("logic-circuit-reverser-inhibited"),
    eecEnable: $("logic-circuit-eec-enable"),
  };
  logicAuxPanels["left-rail"] = document.querySelector(".logic-inspector");
  logicAuxPanels["right-inspector"] = objectContextDrawer;
  logicAuxPanels["bottom-drawer"] = bottomDrawer;
  logicAuxPanels["command-palette"] = commandPalette;
  const circuitReadouts = {
    traValue: $("logic-circuit-tra-value"),
    raValue: $("logic-circuit-ra-value"),
    n1kValue: $("logic-circuit-n1k-value"),
    vdtValue: $("logic-circuit-vdt-value"),
    coreTraValue: $("logic-core-tra-value"),
    coreRaValue: $("logic-core-ra-value"),
    coreN1kValue: $("logic-core-n1k-value"),
    coreVdtValue: $("logic-core-vdt-value"),
    hudSw1: $("logic-circuit-hud-sw1"),
    hudSw2: $("logic-circuit-hud-sw2"),
    hudTls: $("logic-circuit-hud-tls"),
    hudVdt90: $("logic-circuit-hud-vdt90"),
    hudLogic: $("logic-circuit-hud-logic"),
    hudThrLock: $("logic-circuit-hud-thr-lock"),
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

  function providerValue() {
    return (logicBottomProvider && logicBottomProvider.value) || (provider && provider.value) || "deepseek";
  }

  function syncProviderControls(sourceElement) {
    const value = sourceElement && sourceElement.value ? sourceElement.value : providerValue();
    if (provider && provider.value !== value) provider.value = value;
    if (logicBottomProvider && logicBottomProvider.value !== value) logicBottomProvider.value = value;
  }

  function saveAnnotationBatch(status) {
    const payload = {
      kind: "ai-fantui-logic-builder-annotation-batch",
      status: status || "draft",
      provider: providerValue(),
      updated_at: new Date().toISOString(),
      annotations: state.annotationDrafts,
    };
    if (status === "submitted") payload.submitted_at = payload.updated_at;
    window.localStorage.setItem(ANNOTATION_BATCH_KEY, JSON.stringify(payload));
    return payload;
  }

  function loadAnnotationBatch() {
    try {
      const raw = window.localStorage.getItem(ANNOTATION_BATCH_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed.annotations) ? parsed.annotations : [];
    } catch (error) {
      return [];
    }
  }

  function annotationTargetLabel(type, id, fallback) {
    if (fallback) return fallback;
    if (type === "wire") return String(id || "").replace("->", " → ");
    if (id) return String(id);
    return "未选择";
  }

  function setSourceTrustSummary(text) {
    const value = text || "来源待确认";
    if (sourceTrustSummary) sourceTrustSummary.textContent = value;
    if (logicDetailSourceSummary) logicDetailSourceSummary.textContent = value;
  }

  function setDetailNextAction(text) {
    if (logicDetailNextAction) logicDetailNextAction.textContent = text || "等待图纸";
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

  function buildDrawingStreamEvents(payload, circuitView) {
    const events = [];
    const nodes = circuitView ? (circuitView.nodes || []) : (payload.nodes || []);
    const wires = circuitView ? (circuitView.wires || []) : (payload.edges || []);
    const firstAnchor = nodes.find((node) => Array.isArray(node.source_anchors) && node.source_anchors.length);
    events.push({
      kind: "read",
      text: `读取来源：${sourceAnchorLabel(firstAnchor ? firstAnchor.source_anchors : [])}`,
    });
    nodes.slice(0, 3).forEach((node) => {
      events.push({
        kind: "node",
        text: `生成节点 ${node.id || node.label || "node"} · 来源：${sourceAnchorLabel(node.source_anchors)}`,
      });
    });
    wires.slice(0, 3).forEach((wire) => {
      const sourceId = wire.source || "";
      const targetId = wire.target || "";
      events.push({
        kind: "wire",
        text: `生成连线 ${sourceId} → ${targetId} · 来源：${wire.label || sourceId || "模型链路"}`,
      });
    });
    events.push({
      kind: "review",
      text: `修正检查：${nodes.length} 个节点 / ${wires.length} 条连线进入演示舱复核`,
    });
    return events.slice(0, 8);
  }

  function renderDrawingStreamTimeline(payload, circuitView) {
    if (!drawingStreamEvents || !drawingStreamTimeline) return;
    const events = payload ? buildDrawingStreamEvents(payload, circuitView) : [];
    drawingStreamTimeline.dataset.eventCount = String(events.length);
    drawingStreamTimeline.dataset.blueprint39Stream = events.length ? "compact-complete" : "empty";
    const streamTitle = drawingStreamTimeline.querySelector(".logic-stream-head strong");
    if (!events.length) {
      if (streamTitle) streamTitle.textContent = "DeepSeek 绘图回放";
      drawingStreamEvents.innerHTML = '<li class="logic-stream-event is-empty">等待图纸生成过程。</li>';
      return;
    }
    if (streamTitle) streamTitle.textContent = `DeepSeek 已完成 · ${events.length} steps`;
    drawingStreamEvents.innerHTML = "";
    events.forEach((event, index) => {
      const item = document.createElement("li");
      item.className = "logic-stream-event";
      item.dataset.streamEvent = event.kind;
      item.innerHTML = `<span>${String(index + 1).padStart(2, "0")}</span><p>${escapeText(event.text)}</p>`;
      drawingStreamEvents.appendChild(item);
    });
  }

  function markStreamChunksFailed() {
    if (!streamChunks) return;
    streamChunks.querySelectorAll(".stream-chunk").forEach((chunk) => {
      if (chunk.dataset.state === "active") chunk.dataset.state = "error";
    });
  }

  function renderReconstructionMode(payload, circuitView) {
    const hasCircuitView = Boolean(circuitView && circuitView.kind);
    if (reconstructionModePanel) {
      reconstructionModePanel.dataset.mode = hasCircuitView ? "demo-reconstruction" : "concept";
    }
    if (reconstructionMode) {
      reconstructionMode.textContent = hasCircuitView
        ? "当前模式：演示舱一致电路图"
        : "当前模式：概念图，尚未对齐演示舱电路";
    }
    if (reconstructionFidelity) {
      const nodeCount = hasCircuitView && Array.isArray(circuitView.nodes) ? circuitView.nodes.length : 0;
      const wireCount = hasCircuitView && Array.isArray(circuitView.wires) ? circuitView.wires.length : 0;
      reconstructionFidelity.textContent = hasCircuitView
        ? (
          nodeCount === 20 && wireCount === 23
            ? "链路覆盖：20/20 节点 · 23/23 连线"
            : `链路覆盖：${nodeCount}/20 节点 · ${wireCount}/23 连线`
        )
        : "链路覆盖：未启用";
    }
    if (demoBridge) {
      demoBridge.hidden = false;
      demoBridge.textContent = hasCircuitView ? "打开对齐视图" : "打开对照视图";
      demoBridge.setAttribute(
        "aria-label",
        hasCircuitView ? "打开演示舱对齐视图" : "打开概念图对照视图",
      );
    }
    if (canvas) {
      canvas.dataset.reconstructionMode = hasCircuitView ? "demo-reconstruction" : "concept";
    }
    void payload;
  }

  function activateWorkbenchTab(tabName) {
    const activeTab = ["notes", "change", "history"].includes(tabName) ? tabName : "none";
    if (workbenchDrawer) {
      workbenchDrawer.dataset.activeTab = activeTab;
    }
    workbenchTabButtons.forEach((button) => {
      const isActive = button.dataset.workbenchTab === activeTab;
      button.setAttribute("aria-selected", isActive ? "true" : "false");
      button.tabIndex = activeTab === "none" || isActive ? 0 : -1;
    });
    workbenchPanels.forEach((panel) => {
      panel.hidden = panel.dataset.workbenchPanel !== activeTab;
    });
  }

  function setActiveAuxPanel(name) {
    const panelName = name || "none";
    if (logicShell) {
      logicShell.dataset.activeAuxPanel = panelName;
      logicShell.dataset.unifiedInspectorState = panelName;
      logicShell.dataset.workstationState = panelName === "none" ? "primary" : panelName;
    }
    Object.entries(logicAuxPanels).forEach(([key, element]) => {
      if (element) element.dataset.unifiedPanelState = key === panelName ? "open" : "closed";
    });
  }

  function hideObjectContextDrawer() {
    if (objectContextDrawer) {
      objectContextDrawer.hidden = true;
      objectContextDrawer.dataset.unifiedPanelState = "closed";
    }
  }

  function activateBottomDrawer(tabName) {
    const activeTab = ["parameters", "run", "evidence", "report"].includes(tabName) ? tabName : "none";
    if (activeTab !== "none") {
      if (logicShell) logicShell.classList.remove("is-left-open", "is-right-open");
      hideObjectContextDrawer();
      closeCommandPalette();
      setActiveAuxPanel("bottom-drawer");
    } else if (logicShell && logicShell.dataset.activeAuxPanel === "bottom-drawer") {
      setActiveAuxPanel("none");
    }
    if (bottomDrawer) {
      bottomDrawer.dataset.activeTab = activeTab;
      bottomDrawer.hidden = activeTab === "none";
    }
    bottomDrawerButtons.forEach((button) => {
      const isActive = button.dataset.bottomDrawerTab === activeTab;
      button.setAttribute("aria-selected", isActive ? "true" : "false");
    });
    bottomDrawerPanels.forEach((panel) => {
      panel.hidden = panel.dataset.bottomDrawerPanel !== activeTab;
    });
    logicModeButtons.forEach((button) => {
      const mode = button.dataset.logicMode || "canvas";
      button.setAttribute("aria-pressed", (activeTab === "none" ? mode === "canvas" : mode === activeTab) ? "true" : "false");
    });
  }

  function closeAuxiliaryPanels() {
    if (logicShell) {
      logicShell.classList.remove("is-left-open", "is-right-open");
    }
    hideObjectContextDrawer();
    activateBottomDrawer("none");
    activateWorkbenchTab("none");
    closeCommandPalette();
    setActiveAuxPanel("none");
  }

  function openCommandPalette() {
    if (!commandPalette) return;
    if (logicShell) logicShell.classList.remove("is-left-open", "is-right-open");
    hideObjectContextDrawer();
    activateBottomDrawer("none");
    commandPalette.hidden = false;
    setActiveAuxPanel("command-palette");
    if (commandPaletteFilter) {
      commandPaletteFilter.value = "";
      filterCommandPalette("");
      commandPaletteFilter.focus();
    }
    if (commandPaletteStatus) commandPaletteStatus.textContent = "命令面板已打开。";
  }

  function closeCommandPalette() {
    if (!commandPalette) return;
    commandPalette.hidden = true;
    if (logicShell && logicShell.dataset.activeAuxPanel === "command-palette") {
      setActiveAuxPanel("none");
    }
    if (commandPaletteStatus) commandPaletteStatus.textContent = "命令面板空闲。";
  }

  function filterCommandPalette(query) {
    const normalized = String(query || "").trim().toLowerCase();
    let visible = 0;
    commandPaletteItems.forEach((item) => {
      const text = (item.textContent || "").toLowerCase();
      const isVisible = !normalized || text.includes(normalized);
      item.hidden = !isVisible;
      if (isVisible) visible += 1;
    });
    if (commandPaletteStatus) commandPaletteStatus.textContent = `${visible} 个命令可用。`;
  }

  function togglePanel(which) {
    if (!logicShell) return;
    activateBottomDrawer("none");
    closeCommandPalette();
    if (which === "left") {
      const shouldOpen = !logicShell.classList.contains("is-left-open");
      logicShell.classList.toggle("is-left-open", shouldOpen);
      logicShell.classList.remove("is-right-open");
      hideObjectContextDrawer();
      setActiveAuxPanel(shouldOpen ? "left-rail" : "none");
      return;
    }
    if (which === "right") {
      const shouldOpen = !logicShell.classList.contains("is-right-open");
      logicShell.classList.toggle("is-right-open", shouldOpen);
      logicShell.classList.remove("is-left-open");
      if (shouldOpen) {
        renderObjectContextDrawer();
        setActiveAuxPanel("right-inspector");
      } else {
        hideObjectContextDrawer();
        setActiveAuxPanel("none");
      }
    }
  }

  function focusCanvas() {
    if (!canvas) return;
    canvas.focus({preventScroll: true});
    closeAuxiliaryPanels();
  }

  function syncDrawerReadouts() {
    if (drawerReadouts.ra && drawerInputs.ra) drawerReadouts.ra.textContent = `${Number(drawerInputs.ra.value || 0).toFixed(0)} ft`;
    if (drawerReadouts.tra && drawerInputs.tra) drawerReadouts.tra.textContent = `${Number(drawerInputs.tra.value || 0).toFixed(1)}°`;
    if (drawerReadouts.vdt && drawerInputs.vdt) drawerReadouts.vdt.textContent = `${Number(drawerInputs.vdt.value || 0).toFixed(0)}%`;
    if (drawerReadouts.samplingRate && drawerInputs.samplingRate) drawerReadouts.samplingRate.textContent = `${Number(drawerInputs.samplingRate.value || 0).toFixed(0)} Hz`;
    if (drawerReadouts.stepSize && drawerInputs.stepSize) drawerReadouts.stepSize.textContent = `${Number(drawerInputs.stepSize.value || 0).toFixed(0)} ms`;
  }

  function syncDrawerToCircuitInputs() {
    if (drawerInputs.tra && circuitInputs.tra) circuitInputs.tra.value = drawerInputs.tra.value;
    if (drawerInputs.ra && circuitInputs.ra) circuitInputs.ra.value = drawerInputs.ra.value;
    if (drawerInputs.vdt && circuitInputs.vdt) circuitInputs.vdt.value = drawerInputs.vdt.value;
    if (drawerInputs.sw1 && circuitInputs.aircraftOnGround) circuitInputs.aircraftOnGround.checked = drawerInputs.sw1.checked;
    if (drawerInputs.sw2 && circuitInputs.eecEnable) circuitInputs.eecEnable.checked = drawerInputs.sw2.checked;
    state.activeCircuitPreset = "";
    if (circuitPresetStatus) circuitPresetStatus.textContent = "底部抽屉输入";
    if (circuitPresetSelect) circuitPresetSelect.value = "";
    syncDrawerReadouts();
    scheduleCircuitEvaluation();
  }

  function syncDrawerFromCircuitInputs() {
    if (drawerInputs.tra && circuitInputs.tra) drawerInputs.tra.value = circuitInputs.tra.value;
    if (drawerInputs.ra && circuitInputs.ra) drawerInputs.ra.value = circuitInputs.ra.value;
    if (drawerInputs.vdt && circuitInputs.vdt) drawerInputs.vdt.value = circuitInputs.vdt.value;
    if (drawerInputs.sw1 && circuitInputs.aircraftOnGround) drawerInputs.sw1.checked = circuitInputs.aircraftOnGround.checked;
    if (drawerInputs.sw2 && circuitInputs.eecEnable) drawerInputs.sw2.checked = circuitInputs.eecEnable.checked;
    if (drawerPreset && circuitPresetSelect) drawerPreset.value = circuitPresetSelect.value;
    syncDrawerReadouts();
  }

  function appendRunTimeline(action) {
    if (!runTimeline) return;
    const time = new Date().toISOString().slice(11, 19);
    const labels = {
      run: "运行",
      pause: "暂停",
      step: "单步",
      reset: "复位",
    };
    const li = document.createElement("li");
    li.textContent = `${time} ${labels[action] || action} · RA ${drawerInputs.ra ? drawerInputs.ra.value : "-"} ft · TRA ${drawerInputs.tra ? drawerInputs.tra.value : "-"}° · VDT ${drawerInputs.vdt ? drawerInputs.vdt.value : "-"}%`;
    runTimeline.prepend(li);
    while (runTimeline.children.length > 8) runTimeline.removeChild(runTimeline.lastElementChild);
  }

  function handleRunAction(action) {
    syncDrawerToCircuitInputs();
    if (action === "reset") {
      if (drawerInputs.ra) drawerInputs.ra.value = "100";
      if (drawerInputs.tra) drawerInputs.tra.value = "0";
      if (drawerInputs.vdt) drawerInputs.vdt.value = "0";
      if (drawerInputs.sw1) drawerInputs.sw1.checked = true;
      if (drawerInputs.sw2) drawerInputs.sw2.checked = true;
      syncDrawerToCircuitInputs();
    }
    const runLabel = ({run: "运行中", pause: "已暂停", step: "已单步", reset: "已复位"})[action] || "等待运行";
    if (runState) runState.textContent = runLabel;
    if (bottomRunState) bottomRunState.textContent = runLabel;
    if (bottomRunTime) bottomRunTime.textContent = action === "reset" ? "00:00 / 00:20" : "00:03 / 00:20";
    if (bottomRunCursor) bottomRunCursor.style.width = action === "reset" ? "0%" : (action === "step" ? "24%" : "18%");
    appendRunTimeline(action);
    if (action === "run" || action === "step" || action === "reset") evaluateCircuitNow();
  }

  function hydrateDrawerFromHash() {
    const hash = window.location.hash.replace("#", "");
    if (hash === "parameter-drawer") activateBottomDrawer("parameters");
    else if (hash === "run-drawer") activateBottomDrawer("run");
    else if (hash === "evidence") activateBottomDrawer("evidence");
    else if (hash === "report") activateBottomDrawer("report");
    else activateBottomDrawer(bottomDrawer ? bottomDrawer.dataset.activeTab : "none");
  }

  function openInspectorDetails(details) {
    if (!details) return;
    if (details.dataset && details.dataset.workbenchPanel) {
      activateWorkbenchTab(details.dataset.workbenchPanel);
    }
    if ("open" in details) details.open = true;
  }

  function sourceAnchorQuote(anchors) {
    if (!Array.isArray(anchors) || anchors.length === 0) return "";
    return anchors
      .slice(0, 2)
      .map((anchor) => anchor.quote_zh || anchor.quote || "")
      .filter(Boolean)
      .join("；");
  }

  function drawingNodeById(nodeId) {
    if (!state.drawingPayload || !Array.isArray(state.drawingPayload.nodes)) return null;
    return state.drawingPayload.nodes.find((node) => node.id === nodeId) || null;
  }

  function drawingEdgeByTargetId(edgeId) {
    if (!state.drawingPayload || !Array.isArray(state.drawingPayload.edges)) return null;
    return state.drawingPayload.edges.find((edge) => edge.id === edgeId || `${edge.source || ""}->${edge.target || ""}` === edgeId) || null;
  }

  function drawingParameterSummary(nodeId) {
    if (!state.drawingPayload || !Array.isArray(state.drawingPayload.parameter_panels)) return "暂无参数。";
    const panels = state.drawingPayload.parameter_panels.filter((panel) => panel.node_id === nodeId);
    if (!panels.length) return "暂无参数。";
    return panels
      .slice(0, 3)
      .map((panel) => {
        const value = panel.default ?? panel.min ?? "";
        const unit = panel.unit ? ` ${panel.unit}` : "";
        return `${panel.label || panel.id}: ${value}${unit}`;
      })
      .join("；");
  }

  function currentCircuitView() {
    const view = state.drawingPayload && state.drawingPayload.circuit_view;
    return view && view.kind ? view : null;
  }

  function circuitNodeBySelectableId(nodeId) {
    const view = currentCircuitView();
    if (!view || !nodeId) return null;
    return (view.nodes || []).find((node) => node.id === nodeId || node.linked_node_id === nodeId) || null;
  }

  function circuitWireByTargetId(wireId) {
    const view = currentCircuitView();
    if (!view || !wireId) return null;
    return (view.wires || []).find((wire) => {
      const pairId = `${wire.source || ""}->${wire.target || ""}`;
      return wire.id === wireId || pairId === wireId;
    }) || null;
  }

  function circuitNodeParamSummary(node) {
    if (!node) return "";
    const parts = [
      node.circuit_role ? `role:${node.circuit_role}` : "",
      node.state ? `state:${node.state}` : "",
      circuitTechnicalLabel(node),
      node.description_zh || "",
    ].filter(Boolean);
    return parts.length ? parts.join(" · ") : "暂无参数。";
  }

  function selectedTargetContext() {
    if (!state.selectedTargetId) {
      return {
        sourceText: "选择节点或连线后显示来源。",
        paramText: "暂无参数。",
      };
    }
    if (state.selectedTargetType === "wire") {
      const edge = circuitWireByTargetId(state.selectedTargetId) || drawingEdgeByTargetId(state.selectedTargetId) || {};
      const anchors = anchorsForEdge(edge);
      const sourceText = sourceAnchorQuote(anchors)
        || (edge.provenance ? `${edge.provenance}` : "")
        || sourceAnchorLabel(anchors);
      const wireLabel = `${edge.source || state.selectedTargetId.split("->")[0] || "source"} → ${edge.target || state.selectedTargetId.split("->")[1] || "target"}`;
      return {
        sourceText,
        paramText: `${wireLabel}${edge.state ? ` · state:${edge.state}` : ""}`,
      };
    }
    const circuitNode = circuitNodeBySelectableId(state.selectedTargetId);
    if (circuitNode) {
      return {
        sourceText: circuitProvenanceSummaryForNode(circuitNode),
        paramText: circuitNodeParamSummary(circuitNode),
      };
    }
    const node = drawingNodeById(state.selectedTargetId) || {id: state.selectedTargetId, label: state.selectedTargetLabel};
    return {
      sourceText: sourceAnchorQuote(anchorsForNode(node)) || sourceAnchorLabel(anchorsForNode(node)),
      paramText: drawingParameterSummary(node.id || state.selectedTargetId),
    };
  }

  function clampNumber(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function updateAnnotationPopoverPosition() {
    if (!annotationPopover || !canvas) return;
    const wrap = canvas.closest(".logic-canvas-wrap");
    if (!wrap) return;
    const wrapWidth = Math.max(360, wrap.clientWidth || 360);
    const wrapHeight = Math.max(260, wrap.clientHeight || 260);
    const popoverWidth = Math.min(320, Math.max(280, wrapWidth - 48));
    const popoverHeight = 236;
    const fallbackX = wrapWidth - popoverWidth - 24;
    const fallbackY = 58;
    const left = clampNumber(
      (state.annotationPopoverX || fallbackX) + 14,
      48,
      Math.max(48, wrapWidth - popoverWidth - 18),
    );
    const top = clampNumber(
      (state.annotationPopoverY || fallbackY) + 14,
      42,
      Math.max(42, wrapHeight - popoverHeight - 82),
    );
    annotationPopover.style.setProperty("--annotation-popover-left", `${Math.round(left)}px`);
    annotationPopover.style.setProperty("--annotation-popover-top", `${Math.round(top)}px`);
  }

  function rememberPopoverAnchor(event, targetElement) {
    if (!canvas) return;
    const wrap = canvas.closest(".logic-canvas-wrap");
    if (!wrap) return;
    const wrapBox = wrap.getBoundingClientRect();
    if (event && Number.isFinite(event.clientX) && Number.isFinite(event.clientY)) {
      state.annotationPopoverX = event.clientX - wrapBox.left;
      state.annotationPopoverY = event.clientY - wrapBox.top;
      return;
    }
    if (targetElement && typeof targetElement.getBoundingClientRect === "function") {
      const box = targetElement.getBoundingClientRect();
      state.annotationPopoverX = box.left + box.width / 2 - wrapBox.left;
      state.annotationPopoverY = box.top + box.height / 2 - wrapBox.top;
    }
  }

  function renderObjectContextDrawer() {
    if (!objectContextDrawer) return;
    if (!state.selectedTargetId) {
      objectContextDrawer.hidden = true;
      if (annotationSource) annotationSource.textContent = "选择节点或连线后显示来源。";
      if (annotationParams) annotationParams.textContent = "暂无参数。";
      return;
    }
    objectContextDrawer.hidden = false;
    const title = annotationTargetLabel(state.selectedTargetType, state.selectedTargetId, state.selectedTargetLabel);
    const context = selectedTargetContext();
    if (logicContextTitle) logicContextTitle.textContent = title;
    if (logicContextSource) logicContextSource.textContent = context.sourceText;
    if (logicContextParams) logicContextParams.textContent = context.paramText;
    if (annotationSource) annotationSource.textContent = context.sourceText;
    if (annotationParams) annotationParams.textContent = context.paramText;
  }

  function requirementNodeMap() {
    const nodes = state.requirementsPayload && Array.isArray(state.requirementsPayload.concept_logic_nodes)
      ? state.requirementsPayload.concept_logic_nodes
      : [];
    return new Map(nodes.map((node) => [node.id, node]));
  }

  function requirementEdgeMap() {
    const items = state.requirementsPayload && Array.isArray(state.requirementsPayload.concept_edges)
      ? state.requirementsPayload.concept_edges
      : [];
    return new Map(items.map((edge) => [`${edge.source}->${edge.target}`, edge]));
  }

  function anchorsForNode(node) {
    if (Array.isArray(node.source_anchors) && node.source_anchors.length) return node.source_anchors;
    const matched = requirementNodeMap().get(node.id);
    return matched && Array.isArray(matched.source_anchors) ? matched.source_anchors : [];
  }

  function anchorsForEdge(edge) {
    if (Array.isArray(edge.source_anchors) && edge.source_anchors.length) return edge.source_anchors;
    const matched = requirementEdgeMap().get(`${edge.source}->${edge.target}`);
    return matched && Array.isArray(matched.source_anchors) ? matched.source_anchors : [];
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

  function numInputValue(el, fallback) {
    if (!el) return fallback;
    const value = parseFloat(el.value);
    return Number.isFinite(value) ? value : fallback;
  }

  function checkedInput(el) {
    return Boolean(el && el.checked);
  }

  function setCircuitSlider(el, value) {
    if (el) el.value = String(value);
  }

  function setCircuitChecked(el, value) {
    if (el) el.checked = Boolean(value);
  }

  function hasCurrentCircuitView() {
    const view = state.drawingPayload && state.drawingPayload.circuit_view;
    return Boolean(view && view.kind);
  }

  const logicCircuitPresets = {
    "nominal-fwd": {
      label: "默认前向",
      apply: () => {
        setCircuitSlider(circuitInputs.tra, 0);
        setCircuitSlider(circuitInputs.ra, 100);
        setCircuitSlider(circuitInputs.n1k, 35);
        setCircuitSlider(circuitInputs.vdt, 0);
        setCircuitChecked(circuitInputs.engineRunning, true);
        setCircuitChecked(circuitInputs.aircraftOnGround, false);
        setCircuitChecked(circuitInputs.reverserInhibited, false);
        setCircuitChecked(circuitInputs.eecEnable, true);
      },
    },
    "landing-deploy": {
      label: "着陆展开全链路",
      apply: () => {
        logicCircuitPresets["nominal-fwd"].apply();
        setCircuitSlider(circuitInputs.tra, -26);
        setCircuitSlider(circuitInputs.ra, 2);
        setCircuitSlider(circuitInputs.n1k, 70);
        setCircuitSlider(circuitInputs.vdt, 0);
        setCircuitChecked(circuitInputs.aircraftOnGround, true);
      },
    },
    "max-reverse": {
      label: "最大反推（展开到位）",
      apply: () => {
        logicCircuitPresets["landing-deploy"].apply();
        setCircuitSlider(circuitInputs.tra, -32);
        setCircuitSlider(circuitInputs.n1k, 80);
        setCircuitSlider(circuitInputs.vdt, 100);
      },
    },
    "stow-return": {
      label: "收起回杆",
      apply: () => {
        logicCircuitPresets["nominal-fwd"].apply();
        setCircuitSlider(circuitInputs.tra, 0);
        setCircuitSlider(circuitInputs.ra, 2);
        setCircuitSlider(circuitInputs.n1k, 25);
        setCircuitSlider(circuitInputs.vdt, 30);
        setCircuitChecked(circuitInputs.aircraftOnGround, true);
      },
    },
    "inhibit-block": {
      label: "抑制位阻塞",
      apply: () => {
        logicCircuitPresets["landing-deploy"].apply();
        setCircuitChecked(circuitInputs.reverserInhibited, true);
      },
    },
  };

  function updateCircuitInputReadouts(snapshot) {
    const request = buildCircuitEvaluationRequest();
    const traText = `${request.tra_deg.toFixed(1)}°`;
    const raText = `${request.radio_altitude_ft.toFixed(0)} ft`;
    const n1kText = `${numInputValue(circuitInputs.n1k, 35).toFixed(0)}%`;
    if (circuitReadouts.traValue) circuitReadouts.traValue.textContent = traText;
    if (circuitReadouts.coreTraValue) circuitReadouts.coreTraValue.textContent = traText;
    if (circuitReadouts.raValue) circuitReadouts.raValue.textContent = raText;
    if (circuitReadouts.coreRaValue) circuitReadouts.coreRaValue.textContent = raText;
    if (circuitReadouts.n1kValue) circuitReadouts.n1kValue.textContent = n1kText;
    if (circuitReadouts.coreN1kValue) circuitReadouts.coreN1kValue.textContent = n1kText;
    if (circuitReadouts.vdtValue) {
      const hudVdt = snapshot && snapshot.hud && typeof snapshot.hud.deploy_position_percent === "number"
        ? snapshot.hud.deploy_position_percent
        : request.deploy_position_percent;
      const vdtText = `${hudVdt.toFixed(0)}%`;
      circuitReadouts.vdtValue.textContent = vdtText;
      if (circuitReadouts.coreVdtValue) circuitReadouts.coreVdtValue.textContent = vdtText;
    }
  }

  function buildCircuitEvaluationRequest() {
    return {
      tra_deg: numInputValue(circuitInputs.tra, 0),
      radio_altitude_ft: numInputValue(circuitInputs.ra, 100),
      n1k: numInputValue(circuitInputs.n1k, 35) / 100,
      engine_running: checkedInput(circuitInputs.engineRunning),
      aircraft_on_ground: checkedInput(circuitInputs.aircraftOnGround),
      reverser_inhibited: checkedInput(circuitInputs.reverserInhibited),
      eec_enable: checkedInput(circuitInputs.eecEnable),
      feedback_mode: "manual_feedback_override",
      actor: "Kogami",
      ticket_id: "WB-DEMO",
      manual_override_signoff: {
        signed_by: "Kogami",
        signed_at: "2026-04-25T00:00:00Z",
        ticket_id: "WB-DEMO",
      },
      deploy_position_percent: numInputValue(circuitInputs.vdt, 0),
      fault_injections: [],
    };
  }

  async function requestCircuitEvaluation() {
    const response = await fetch(LEVER_SNAPSHOT_API, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(buildCircuitEvaluationRequest()),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error("演示舱状态计算失败。");
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function visualCircuitState(value) {
    const normalized = String(value || "idle");
    if (normalized === "active" || normalized === "blocked" || normalized === "fault") return normalized;
    return "idle";
  }

  function setCircuitVisualState(element, rawState) {
    const visualState = visualCircuitState(rawState);
    element.dataset.rawState = rawState || "idle";
    element.dataset.state = visualState;
    element.classList.remove("is-active", "is-blocked", "is-fault", "is-idle");
    element.classList.add(`is-${visualState}`);
  }

  function circuitNodeActive(nodeById, nodeId) {
    const node = nodeById.get(nodeId);
    return Boolean(node && node.state === "active");
  }

  function renderCircuitEvaluationHud(snapshot, nodeById) {
    const sw1 = nodeById.get("sw1");
    const sw2 = nodeById.get("sw2");
    const tls = nodeById.get("tls_unlocked");
    const vdt90 = nodeById.get("vdt90");
    const thr = nodeById.get("thr_lock");
    if (circuitReadouts.hudSw1) circuitReadouts.hudSw1.textContent = sw1 && sw1.state === "active" ? "CLOSED" : "open";
    if (circuitReadouts.hudSw2) circuitReadouts.hudSw2.textContent = sw2 && sw2.state === "active" ? "CLOSED" : "open";
    if (circuitReadouts.hudTls) circuitReadouts.hudTls.textContent = tls && tls.state === "active" ? "UNLOCKED" : "locked";
    if (circuitReadouts.hudVdt90) circuitReadouts.hudVdt90.textContent = vdt90 && vdt90.state === "active" ? ">=90%" : "pending";
    if (circuitReadouts.hudLogic) {
      circuitReadouts.hudLogic.textContent = ["logic1", "logic2", "logic3", "logic4"].map((id, index) => {
        const node = nodeById.get(id);
        return `L${index + 1}:${node && node.state === "active" ? "ON" : "-"}`;
      }).join(" · ");
    }
    if (circuitReadouts.hudThrLock) {
      if (thr && thr.state === "active") circuitReadouts.hudThrLock.textContent = "RELEASED";
      else if (thr && thr.state === "blocked") circuitReadouts.hudThrLock.textContent = "BLOCKED";
      else circuitReadouts.hudThrLock.textContent = "-";
    }
    updateCircuitInputReadouts(snapshot);
  }

  function renderCircuitEvaluationStatus(nodeById) {
    const thr = nodeById.get("thr_lock");
    const logic4 = nodeById.get("logic4");
    const logic3 = nodeById.get("logic3");
    let status = "idle";
    let summary = "等待输入：TRA / RA / aircraft_on_ground 未满足 L1 前置条件。";
    if (checkedInput(circuitInputs.reverserInhibited)) {
      status = "fault";
      summary = "反推被抑制：reverser_inhibited=TRUE，deploy 链路阻塞。";
    } else if (thr && thr.state === "active") {
      status = "deployed";
      summary = "L4 满足，THR_LOCK 释放。油门反向段解锁。";
    } else if (logic4 && logic4.state === "blocked") {
      const blockers = (logic4.blockers || logic4.blocked_by || []).join(" / ") || "VDT90 / plant feedback";
      status = "fault";
      summary = `L4 阻塞：${blockers}。`;
    } else if (logic3 && logic3.state === "active") {
      status = "deploying";
      summary = "L3 激活：EEC deploy / PLS / PDU 通电。等待 VDT>=90% 解锁深拉区。";
    } else if (circuitNodeActive(nodeById, "logic2") || circuitNodeActive(nodeById, "logic1")) {
      status = "ready";
      summary = circuitNodeActive(nodeById, "logic2")
        ? "L2 激活：ETRAC 540VDC 已供电，等待 L3 条件。"
        : "L1 激活：TLS 115VAC 已供电，等待 L2 条件。";
    }
    if (circuitStatusBadge) {
      circuitStatusBadge.dataset.state = status;
      circuitStatusBadge.textContent = ({
        idle: "IDLE",
        ready: "READY",
        deploying: "DEPLOYING",
        deployed: "DEPLOYED",
        fault: "FAULT",
      })[status] || "IDLE";
    }
    if (circuitStatusSummary) circuitStatusSummary.textContent = summary;
  }

  function applyCircuitEvaluation(snapshot) {
    state.circuitEvaluationPayload = snapshot;
    const nodeById = new Map((Array.isArray(snapshot.nodes) ? snapshot.nodes : []).map((node) => [node.id, node]));
    circuitSvg.querySelectorAll(".logic-circuit-node").forEach((element) => {
      const nodeId = element.dataset.demoNodeId || element.dataset.nodeId || "";
      const node = nodeById.get(nodeId);
      setCircuitVisualState(element, node ? node.state : "idle");
    });
    circuitSvg.querySelectorAll(".logic-circuit-wire").forEach((wire) => {
      const src = wire.dataset.source || "";
      const dst = wire.dataset.target || "";
      const faultWire = wire.dataset.fault === "true";
      const srcActive = circuitNodeActive(nodeById, src);
      const dstActive = circuitNodeActive(nodeById, dst);
      let wireState = "idle";
      if (faultWire && srcActive) wireState = "fault";
      else if (srcActive && dstActive) wireState = "active";
      else if (srcActive) wireState = "active";
      setCircuitVisualState(wire, wireState);
      wire.setAttribute("marker-end", `url(#logic-circuit-arrow-${wireState === "fault" ? "fault" : wireState === "active" ? "active" : "idle"})`);
    });
    circuitSvg.querySelectorAll(".logic-circuit-junction").forEach((junction) => {
      const src = junction.dataset.source || "";
      const srcActive = circuitNodeActive(nodeById, src);
      const junctionState = junction.dataset.fault === "true" && srcActive ? "fault" : (srcActive ? "active" : "idle");
      setCircuitVisualState(junction, junctionState);
    });
    renderCircuitEvaluationHud(snapshot, nodeById);
    renderCircuitEvaluationStatus(nodeById);
  }

  async function evaluateCircuitNow() {
    if (!hasCurrentCircuitView() || state.circuitEvaluationBusy) return;
    state.circuitEvaluationBusy = true;
    updateCircuitEvaluationControls();
    updateCircuitInputReadouts(state.circuitEvaluationPayload);
    try {
      const payload = await requestCircuitEvaluation();
      applyCircuitEvaluation(payload);
    } catch (error) {
      if (circuitStatusBadge) {
        circuitStatusBadge.dataset.state = "fault";
        circuitStatusBadge.textContent = "ERROR";
      }
      if (circuitStatusSummary) {
        const details = error.payload && error.payload.message ? error.payload.message : error.message;
        circuitStatusSummary.textContent = details || "演示舱状态计算失败。";
      }
    } finally {
      state.circuitEvaluationBusy = false;
      updateCircuitEvaluationControls();
    }
  }

  function scheduleCircuitEvaluation() {
    if (!hasCurrentCircuitView()) return;
    clearTimeout(state.circuitEvaluationTimer);
    updateCircuitInputReadouts(state.circuitEvaluationPayload);
    state.circuitEvaluationTimer = setTimeout(() => {
      state.circuitEvaluationTimer = null;
      evaluateCircuitNow();
    }, CIRCUIT_EVAL_DEBOUNCE_MS);
  }

  function applyCircuitPreset(key) {
    const preset = logicCircuitPresets[key];
    if (!preset) return;
    preset.apply();
    state.activeCircuitPreset = key;
    if (circuitPresetStatus) circuitPresetStatus.textContent = `当前场景：${preset.label}`;
    if (circuitPresetSelect && circuitPresetSelect.value !== key) circuitPresetSelect.value = key;
    circuitPresetButtons.forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.circuitPreset === key ? "true" : "false");
    });
    updateCircuitInputReadouts(state.circuitEvaluationPayload);
    evaluateCircuitNow();
  }

  function updateCircuitEvaluationControls() {
    const enabled = hasCurrentCircuitView() && !state.busy && !state.circuitEvaluationBusy;
    Object.values(circuitInputs).forEach((element) => {
      if (element) element.disabled = !enabled;
    });
    circuitPresetButtons.forEach((button) => {
      button.disabled = !enabled;
    });
    if (circuitPresetSelect) circuitPresetSelect.disabled = !enabled;
  }

  function renderCircuitEvaluationPanel(circuitView) {
    const visible = Boolean(circuitView && circuitView.kind);
    if (circuitEvalPanel) circuitEvalPanel.hidden = !visible;
    if (!visible) {
      if (logicCircuitInputDetails) logicCircuitInputDetails.open = false;
      clearTimeout(state.circuitEvaluationTimer);
      state.circuitEvaluationTimer = null;
      state.circuitEvaluationPayload = null;
      state.activeCircuitPreset = "";
      updateCircuitEvaluationControls();
      return;
    }
    if (logicCircuitInputDetails) {
      logicCircuitInputDetails.open = window.matchMedia("(min-width: 1100px)").matches;
    }
    updateCircuitEvaluationControls();
    updateCircuitInputReadouts(state.circuitEvaluationPayload);
    evaluateCircuitNow();
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
    regenerate.disabled = isBusy;
    faultNext.disabled = isBusy || !state.drawingPayload;
    provider.disabled = isBusy;
    if (logicBottomProvider) logicBottomProvider.disabled = isBusy;
    regenerate.textContent = isBusy ? "绘制中..." : "检查：重新绘制";
    updateCircuitEvaluationControls();
    updateChangeControls();
  }

  function loadRequirementsPayload() {
    const raw = window.localStorage.getItem(INPUT_KEY);
    if (!raw) return null;
    try {
      const payload = JSON.parse(raw);
      return payload && typeof payload === "object" ? payload : null;
    } catch (error) {
      return null;
    }
  }

  function loadDrawingPayload() {
    const raw = window.localStorage.getItem(DRAWING_KEY);
    if (!raw) return null;
    try {
      const payload = JSON.parse(raw);
      return payload && typeof payload === "object" ? payload : null;
    } catch (error) {
      return null;
    }
  }

  function loadChangeHistory() {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    try {
      const payload = JSON.parse(raw);
      return Array.isArray(payload) ? payload : [];
    } catch (error) {
      return [];
    }
  }

  function loadSandboxRevisionHandoff() {
    const raw = window.localStorage.getItem(REVISION_HANDOFF_KEY);
    if (!raw) return null;
    window.localStorage.removeItem(REVISION_HANDOFF_KEY);
    try {
      const payload = JSON.parse(raw);
      if (!payload || payload.from !== "fault_injection_sandbox") return null;
      return {
        plan_count: Number(payload.plan_count) || 0,
        observation_count: Number(payload.observation_count) || 0,
        review_count: Number(payload.review_count) || 0,
        top_signal: String(payload.top_signal || "").slice(0, 80),
        top_node: String(payload.top_node || "").slice(0, 80),
        summary: String(payload.summary || "").slice(0, 220),
      };
    } catch (error) {
      return null;
    }
  }

  function renderSandboxRevisionHandoff() {
    const handoff = state.revisionHandoff;
    if (!handoff) {
      revisionHandoff.hidden = true;
      return;
    }
    const focusName = handoff.top_signal || handoff.top_node || "沙盒审查项";
    openInspectorDetails(changeLoopDetails);
    revisionHandoff.hidden = false;
    revisionHandoffTitle.textContent = "来自沙盒审查";
    revisionHandoffSummary.textContent = handoff.summary || `建议先描述 ${focusName} 是否需要回写到逻辑图。`;
    revisionHandoffMetrics.textContent = `${handoff.plan_count} 个计划 · ${handoff.observation_count} 个观测点 · ${handoff.review_count} 个审查项`;
    changeText.placeholder = `来自沙盒审查：先说明 ${focusName} 相关的逻辑修改意见。`;
    if (!changeText.value.trim()) {
      changeText.focus();
    }
  }

  function buildSandboxHandoffDraftText(handoff) {
    if (!handoff) return "";
    const focusName = handoff.top_signal || handoff.top_node || "沙盒审查项";
    const summary = handoff.summary || "收到沙盒审查结果，建议检查关键逻辑与边界条件并给出可执行修改点。";
    return `【沙盒审查草稿】本次审查建议围绕“${focusName}”推进。当前共 ${handoff.plan_count} 个计划、${handoff.observation_count} 个观测点、${handoff.review_count} 条审查项；核心结论：${summary}。请根据沙盒审查补充具体修改意见：1. 需要调整的逻辑节点；2. 需要同步的参数或边界；3. 期望模型更新后的图纸变化。`;
  }

  function fillLogicChangeFromHandoff() {
    const draftText = buildSandboxHandoffDraftText(state.revisionHandoff);
    if (!draftText) return;
    openInspectorDetails(changeLoopDetails);
    const currentText = changeText.value.trim();
    changeText.value = currentText && !currentText.includes("【沙盒审查草稿】")
      ? `${currentText}\n\n${draftText}`
      : draftText;
    changeText.focus();
    updateChangeControls();
  }

  function saveChangeHistory() {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(state.changeHistory));
  }

  function renderInput(payload) {
    if (!payload) {
      inputTitle.textContent = "没有已确认需求";
      inputSummary.textContent = "请先回到需求理解页，完成澄清并点击进入逻辑链路绘制。";
      return;
    }
    const doc = payload.source_document || {};
    inputTitle.textContent = doc.name || "已确认需求";
    inputSummary.textContent = payload.summary_zh || "已从需求理解页载入结构化需求。";
  }

  function renderTemplateEntryState(message) {
    if (!templateEntry) return;
    const hasDrawing = Boolean(state.drawingPayload);
    templateEntry.hidden = hasDrawing;
    templateEntry.dataset.templateState = hasDrawing ? "hidden" : "ready";
    if (message) templateEntry.dataset.templateMessage = message;
    if (drawingStreamTimeline) drawingStreamTimeline.hidden = !hasDrawing;
    if (reconstructionModePanel) reconstructionModePanel.hidden = !hasDrawing;
    if (annotationSubmitBar) annotationSubmitBar.hidden = !hasDrawing;
  }

  function clearDrawingSurface() {
    state.drawingPayload = null;
    window.localStorage.removeItem(DRAWING_KEY);
    window.localStorage.removeItem(FAULT_DRAFT_KEY);
    if (canvas) {
      delete canvas.dataset.viewMode;
      delete canvas.dataset.fitMode;
      delete canvas.dataset.reconstructionMode;
      canvas.style.minHeight = "";
    }
    if (circuitSvg) {
      circuitSvg.innerHTML = "";
      circuitSvg.hidden = true;
      circuitSvg.setAttribute("hidden", "");
    }
    if (svg) svg.innerHTML = "";
    if (nodeLayer) nodeLayer.innerHTML = "";
    if (panelLayer) panelLayer.innerHTML = "";
    if (counts) counts.textContent = "0 nodes · 0 edges · 0 panels";
    if (source) source.textContent = "来源待确认";
    if (bottomRunNodeCount) bottomRunNodeCount.textContent = "节点 0/0";
    if (bottomRunEdgeCount) bottomRunEdgeCount.textContent = "连线 0/0";
    renderCircuitProvenanceLegend(null);
    renderCircuitEvaluationPanel(null);
    renderDrawingStreamTimeline(null, null);
    renderBurdenSummary(null);
    renderWorkflowOverview();
    updateChangeControls();
    renderTemplateEntryState("blank");
  }

  function buildDocxTemplateCandidate() {
    const now = new Date().toISOString();
    return {
      kind: "ai-fantui-logic-link-drawing",
      status: "draft_ready",
      summary_zh: "已载入 DOCX L1-L4 官方模板候选；仅用于 UI 蓝图演示，不修改控制真值。",
      truth_effect: "none",
      candidate_state: "sandbox_candidate",
      certification_claim: "none",
      controller_truth_modified: false,
      source_requirements_sha256: "local-docx-l1-l4-template",
      generated_at: now,
      llm: {provider: "local", model: "docx-l1-l4-template"},
      canvas: {width: 980, height: 520},
      nodes: [
        {id: "ra", label: "RA 高度", node_kind: "input", x: 64, y: 76, width: 140, height: 78, description_zh: "RA < 6 ft 允许进入反推链路。", source_anchors: [{id: "L1", kind: "正文条件"}]},
        {id: "sw1", label: "SW1", node_kind: "input", x: 64, y: 176, width: 140, height: 78, description_zh: "SW1 有效。", source_anchors: [{id: "L2", kind: "正文条件"}]},
        {id: "sw2", label: "SW2", node_kind: "input", x: 64, y: 276, width: 140, height: 78, description_zh: "SW2 有效。", source_anchors: [{id: "L2", kind: "正文条件"}]},
        {id: "logic_and", label: "与门 AND1", node_kind: "logic", x: 348, y: 176, width: 150, height: 82, description_zh: "RA、SW1、SW2 和 EEC 共同成立。", source_anchors: [{id: "L3", kind: "逻辑条件"}]},
        {id: "latch", label: "反推允许 LATCH", node_kind: "logic", x: 596, y: 176, width: 168, height: 82, description_zh: "候选锁存输出。", source_anchors: [{id: "L4", kind: "输出条件"}]},
        {id: "caut", label: "L1/L2 告警", node_kind: "output", x: 836, y: 176, width: 136, height: 82, description_zh: "输出告警候选。", source_anchors: [{id: "L4", kind: "输出条件"}]},
      ],
      edges: [
        {"source": "ra", "target": "logic_and", "label": "RA -> AND1", "route": [{x: 204, y: 115}, {x: 276, y: 115}, {x: 276, y: 208}, {x: 348, y: 208}]},
        {"source": "sw1", "target": "logic_and", "label": "SW1 -> AND1", "route": [{x: 204, y: 215}, {x: 348, y: 215}]},
        {"source": "sw2", "target": "logic_and", "label": "SW2 -> AND1", "route": [{x: 204, y: 315}, {x: 276, y: 315}, {x: 276, y: 230}, {x: 348, y: 230}]},
        {"source": "logic_and", "target": "latch", "label": "AND1 -> LATCH", "route": [{x: 498, y: 217}, {x: 596, y: 217}]},
        {"source": "latch", "target": "caut", "label": "LATCH -> CAUT", "route": [{x: 764, y: 217}, {x: 836, y: 217}]},
      ],
      parameter_panels: [
        {id: "ra_threshold", node_id: "ra", label: "RA 门限", min: 0, max: 20, default: 6, unit: "ft", x: 232, y: 48, width: 140, height: 72},
        {id: "vdt_deploy", node_id: "latch", label: "VDT 部署", min: 0, max: 100, default: 90, unit: "%", x: 560, y: 300, width: 150, height: 72},
      ],
      drawing_notes: [
        "DOCX L1-L4 模板仅创建 sandbox candidate。",
        "truth_effect:none；controller_truth_modified:false。",
      ],
    };
  }

  function handleTemplateAction(action) {
    const selected = action || "blank";
    if (selected === "blank") {
      beginTask("打开空白画布", "正在清理本地图纸草稿并保留模板入口。");
      clearDrawingSurface();
      resultState.textContent = "空白画布";
      resultSummary.textContent = "已进入空白画布入口；可使用模板或回到需求页生成图纸。";
      finishTask("空白画布", "当前没有图纸候选，底部运行条保持候选态边界。");
      return;
    }
    if (selected === "docx") {
      if (state.requirementsPayload && !state.busy) {
        generateDrawing();
        return;
      }
      beginTask("载入 DOCX 模板", "正在创建本地 L1-L4 蓝图候选。");
      renderDrawing(buildDocxTemplateCandidate());
      finishTask("模板已载入", "DOCX L1-L4 官方模板已作为 sandbox candidate 展示。");
      return;
    }
    if (selected === "restore") {
      const saved = loadDrawingPayload();
      if (saved) {
        beginTask("恢复最近沙盒", "正在读取本地保存的逻辑图纸。");
        renderDrawing(saved);
        finishTask("已恢复最近沙盒", "已从本地草稿恢复最近逻辑图纸。");
        return;
      }
      beginTask("恢复最近沙盒", "未找到本地草稿，载入官方模板候选。");
      renderDrawing(buildDocxTemplateCandidate());
      finishTask("已载入恢复模板", "未找到最近草稿，已使用 DOCX L1-L4 模板作为候选起点。");
    }
  }

  async function requestDrawing() {
    if (!state.requirementsPayload) {
      throw new Error("没有可绘制的已确认需求。");
    }
    const response = await fetch("/api/requirements-intake/draw-logic", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: provider.value,
        allow_fallback: provider.value !== "deepseek",
        requirements_payload: state.requirementsPayload,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "模型绘图失败，请重新绘制或切换模型。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function requestChangeInterpretation(annotationText) {
    if (!state.requirementsPayload) {
      throw new Error("缺少原始需求上下文，请先从需求理解页进入。");
    }
    if (!state.drawingPayload) {
      throw new Error("没有可修改的逻辑图纸。");
    }
    const response = await fetch("/api/requirements-intake/interpret-logic-change", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: provider.value,
        allow_fallback: provider.value !== "deepseek",
        requirements_payload: state.requirementsPayload,
        drawing_payload: state.drawingPayload,
        target_node_id: state.selectedNodeId,
        annotation_text: annotationText,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "模型未能理解修改意见，请简化意见后重试。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function buildAnnotationBatchRequest() {
    const annotations = state.annotationDrafts.map((item) => ({...item}));
    const selectedNodes = [];
    const selectedEdges = [];
    const seenNodes = new Set();
    const seenEdges = new Set();
    for (const item of annotations) {
      if (item.target_type === "node" && item.target_id && !seenNodes.has(item.target_id)) {
        seenNodes.add(item.target_id);
        selectedNodes.push(item.target_id);
      }
      if (item.target_type === "wire" && item.target_id && !seenEdges.has(item.target_id)) {
        seenEdges.add(item.target_id);
        selectedEdges.push(item.target_id);
      }
    }
    const lines = annotations.map((item, index) => {
      const target = item.target_label || item.target_id || "未指定对象";
      const type = item.target_type === "wire" ? "连线" : "节点";
      return `${index + 1}. [${type} ${target}] ${item.text || ""}`;
    });
    return {
      target_node_id: selectedNodes[0] || (state.selectedTargetType === "node" ? state.selectedTargetId : ""),
      annotation_text: `批量标注意见：\n${lines.join("\n")}`,
      annotation_batch: annotations,
      selected_nodes: selectedNodes,
      selected_edges: selectedEdges,
    };
  }

  async function requestAnnotationBatchInterpretation(batchRequest) {
    if (!state.requirementsPayload) {
      throw new Error("缺少原始需求上下文，请先从需求理解页进入。");
    }
    if (!state.drawingPayload) {
      throw new Error("没有可修改的逻辑图纸。");
    }
    const model = providerValue();
    const response = await fetch("/api/requirements-intake/interpret-logic-change", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: model,
        allow_fallback: model !== "deepseek",
        requirements_payload: state.requirementsPayload,
        drawing_payload: state.drawingPayload,
        target_node_id: batchRequest.target_node_id,
        annotation_text: batchRequest.annotation_text,
        annotation_batch: batchRequest.annotation_batch,
        selected_nodes: batchRequest.selected_nodes,
        selected_edges: batchRequest.selected_edges,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "AI 未能归并本次标注意见，请简化批注后重试。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function requestDrawingUpdate(interpretationPayload) {
    if (!state.drawingPayload) {
      throw new Error("没有可更新的逻辑图纸。");
    }
    const confirmed = {
      ...interpretationPayload,
      status: "confirmed_by_user",
    };
    const response = await fetch("/api/requirements-intake/update-logic-drawing", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        provider: provider.value,
        allow_fallback: provider.value !== "deepseek",
        drawing_payload: state.drawingPayload,
        interpretation_payload: confirmed,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "图纸更新失败，请重新确认修改意图后重试。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function renderFlags(payload) {
    resultFlags.innerHTML = "";
    const flags = [
      payload.controller_truth_modified ? "需复核控制逻辑" : "未改控制逻辑",
      payload.status === "draft_ready" ? "初版草稿" : "等待生成",
      payload.certification_claim && payload.certification_claim !== "none" ? "含认证声明" : "无认证声明",
      (payload.llm && payload.llm.provider === "minimax") ? "MiniMax" : "DeepSeek",
    ];
    for (const flag of flags) {
      const span = document.createElement("span");
      span.textContent = flag;
      resultFlags.appendChild(span);
    }
  }

  function canvasSize(payload) {
    const raw = payload.canvas || {};
    let width = Math.max(900, Number(raw.width) || 1280);
    let height = Math.max(560, Number(raw.height) || 760);
    for (const node of payload.nodes || []) {
      width = Math.max(width, (Number(node.x) || 0) + (Number(node.width) || 180) + 72);
      height = Math.max(height, (Number(node.y) || 0) + (Number(node.height) || 104) + 72);
    }
    for (const panel of payload.parameter_panels || []) {
      width = Math.max(width, (Number(panel.x) || 0) + (Number(panel.width) || 140) + 72);
      height = Math.max(height, (Number(panel.y) || 0) + (Number(panel.height) || 76) + 72);
    }
    return {
      width,
      height,
    };
  }

  function renderBurdenSummary(payload) {
    if (!payload) {
      burdenAction.textContent = "等待图纸";
      burdenOutputs.innerHTML = "<li>本页只看初版图是否一屏可读。</li>";
      setDetailNextAction("等待图纸");
      return;
    }
    const circuitView = payload.circuit_view && payload.circuit_view.kind ? payload.circuit_view : null;
    if (circuitView) {
      const badges = Array.isArray(circuitView.badges) ? circuitView.badges.length : 0;
      const outputs = [
        `${(circuitView.rows || []).length} 行 L1-L4 电路`,
        `${(circuitView.wires || []).length} 条确定性连线`,
        badges ? "源文档暂缓项已标记" : "未发现源文档暂缓项",
      ];
      burdenAction.textContent = "先看 L1-L4 四行电路、THR_LOCK 输出和来源标记。";
      burdenOutputs.innerHTML = outputs.slice(0, 3).map((item) => `<li>${escapeText(item)}</li>`).join("");
      setDetailNextAction("看 THR_LOCK，必要时批注。");
      return;
    }
    const metrics = drawingMetrics(payload);
    const missingAnchors = (payload.nodes || []).filter((node) => !anchorsForNode(node).length).length;
    const outputs = [
      `${metrics.nodes} 个节点`,
      `${metrics.edges} 条连线`,
      missingAnchors ? `${missingAnchors} 个节点是模型假设` : "节点均带来源锚点或继承需求来源",
    ];
    burdenAction.textContent = "先确认 L1-L4 分组、输出节点和来源标记。";
    burdenOutputs.innerHTML = outputs.slice(0, 3).map((item) => `<li>${escapeText(item)}</li>`).join("");
    setDetailNextAction("确认 L1-L4 与来源。");
    setSourceTrustSummary(missingAnchors ? `${missingAnchors} 个模型假设` : "来源覆盖已确认");
  }

  function createSvgElement(name, attrs) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (value != null) {
        element.setAttribute(key, String(value));
      }
    });
    return element;
  }

  function circuitNodeColor(role) {
    if (role === "gate") return "#00e5a0";
    if (role === "final_output") return "#f5c85b";
    if (role === "intermediate" || role === "output") return "#456084";
    return "#36c6d8";
  }

  function appendCircuitText(parent, text, x, y, attrs) {
    const element = createSvgElement("text", {x, y, ...(attrs || {})});
    element.textContent = text || "";
    parent.appendChild(element);
    return element;
  }

  function appendCircuitMultilineText(parent, lines, x, y, attrs) {
    lines.forEach((line, index) => {
      appendCircuitText(parent, line, x, y + index * 9, attrs);
    });
  }

  function compactCircuitLabel(label) {
    const raw = String(label || "").trim();
    if (!raw) return "";
    const primary = raw.split("·")[0].trim();
    return (primary || raw).split("[")[0].trim();
  }

  function circuitDisplayLabel(node) {
    const id = node.id || "";
    if (CIRCUIT_SHORT_LABELS[id]) return CIRCUIT_SHORT_LABELS[id];
    return compactCircuitLabel(node.label) || id;
  }

  function circuitTechnicalLabel(node) {
    const displayLabel = circuitDisplayLabel(node);
    const parts = [];
    if (node.id) parts.push(`技术 id: ${node.id}`);
    if (node.label && node.label !== displayLabel) parts.push(`技术标签: ${node.label}`);
    if (node.linked_node_id && node.linked_node_id !== node.id) parts.push(`关联节点: ${node.linked_node_id}`);
    return parts.join(" · ");
  }

  function circuitReadableLaneForNode(node) {
    return CIRCUIT_READABLE_LANES[node.id || ""] || "";
  }

  function circuitReadableLaneForWire(wire) {
    if (CIRCUIT_READABLE_LANES[wire.source || ""] || CIRCUIT_READABLE_LANES[wire.target || ""]) return "sw";
    return "";
  }

  function circuitProvenanceKindForNode(node) {
    const explicit = String(node.provenance_kind || node.provenance || "").trim();
    if (CIRCUIT_PROVENANCE_FILTERS.has(explicit) && explicit !== "all") return explicit;
    if (anchorsForNode(node).length) return "source";
    if (
      CIRCUIT_LOCAL_COMPLETION_IDS.has(node.id || "") ||
      node.local_completion === true ||
      node.generated_by === "local_preparse" ||
      node.generated_by === "deterministic_circuit"
    ) {
      return "local";
    }
    return "assumption";
  }

  function circuitProvenanceLabel(kind) {
    return CIRCUIT_PROVENANCE_LABELS[kind] || CIRCUIT_PROVENANCE_LABELS.assumption;
  }

  function circuitProvenanceSummaryForNode(node) {
    const kind = circuitProvenanceKindForNode(node);
    if (kind === "source") {
      return sourceAnchorQuote(anchorsForNode(node)) || sourceAnchorLabel(anchorsForNode(node));
    }
    return circuitProvenanceLabel(kind);
  }

  function circuitProvenanceKindForWire(wire, provenanceById) {
    if (Array.isArray(wire.source_anchors) && wire.source_anchors.length) return "source";
    const sourceKind = provenanceById.get(wire.source || "");
    const targetKind = provenanceById.get(wire.target || "");
    if (sourceKind === "assumption" || targetKind === "assumption") return "assumption";
    if (sourceKind === "source" && targetKind === "source") return "source";
    return "local";
  }

  function circuitNodeHoverTitle(node) {
    const sourceText = circuitProvenanceSummaryForNode(node);
    return [`显示标签: ${circuitDisplayLabel(node)}`, circuitTechnicalLabel(node), `来源: ${sourceText}`]
      .filter(Boolean)
      .join("\n");
  }

  function renderCircuitNodeDetails(parent, node, x, y, width, height) {
    if (!node.id) return;
    const details = createSvgElement("g", {
      class: "logic-circuit-node-details",
      "aria-hidden": "true",
    });
    appendCircuitText(details, node.id, x + width / 2, y + height + 10, {
      class: "logic-circuit-tech-id",
      "text-anchor": "middle",
    });
    parent.appendChild(details);
  }

  function renderCircuitDefs() {
    const defs = createSvgElement("defs");
    const markerSpecs = [
      ["logic-circuit-arrow-idle", "#46597a"],
      ["logic-circuit-arrow-active", "#00e5a0"],
      ["logic-circuit-arrow-fault", "#e05555"],
    ];
    for (const [id, color] of markerSpecs) {
      const marker = createSvgElement("marker", {
        id,
        markerWidth: 8,
        markerHeight: 8,
        refX: 7,
        refY: 4,
        orient: "auto",
      });
      marker.appendChild(createSvgElement("path", {d: "M0,0 L8,4 L0,8 Z", fill: color}));
      defs.appendChild(marker);
    }
    return defs;
  }

  function renderCircuitChrome(view, size) {
    circuitSvg.appendChild(renderCircuitDefs());
    const isBlueprintFlow = document.body && document.body.dataset.primaryFlow === "deepseek-v4-pro-ui-workbench";
    const bg = createSvgElement("rect", {
      x: 0,
      y: 0,
      width: size.width,
      height: size.height,
      fill: isBlueprintFlow ? "#fbfdff" : "#071421",
    });
    circuitSvg.appendChild(bg);
    [
      [90, "INPUTS"],
      [340, "LOGIC GATES"],
      [580, "INTERMEDIATE"],
      [810, "OUTPUT"],
    ].forEach(([x, label]) => {
      appendCircuitText(circuitSvg, label, x, 28, {class: "logic-circuit-column-label", "text-anchor": "middle"});
    });
    appendCircuitText(circuitSvg, "DOCX anchored L1-L4 authority chain", 450, 388, {
      class: "logic-circuit-footer-label",
      "text-anchor": "middle",
    });
  }

  function renderCircuitLaneGuides(view, size) {
    const swNodes = (view.nodes || []).filter((node) => circuitReadableLaneForNode(node) === "sw");
    if (!swNodes.length) return;
    const swRoutes = (view.wires || [])
      .filter((wire) => circuitReadableLaneForWire(wire) === "sw")
      .flatMap((wire) => (Array.isArray(wire.route) ? wire.route : []));
    const yValues = swNodes
      .flatMap((node) => [Number(node.y) || 0, (Number(node.y) || 0) + (Number(node.height) || 28)])
      .concat(swRoutes.map((point) => Number(point.y) || 0));
    const xValues = swNodes
      .flatMap((node) => [Number(node.x) || 0, (Number(node.x) || 0) + (Number(node.width) || 120)])
      .concat(swRoutes.map((point) => Number(point.x) || 0));
    const laneX = Math.max(0, Math.min(...xValues) - 6);
    const laneY = Math.max(34, Math.min(...yValues) - 18);
    const laneRight = Math.min(size.width - 10, Math.max(...xValues) + 18);
    const laneBottom = Math.min(size.height - 34, Math.max(...yValues) + 18);
    const guide = createSvgElement("g", {
      class: "logic-circuit-lane-guide",
      "data-readable-lane": "sw",
    });
    guide.appendChild(createSvgElement("rect", {
      x: laneX,
      y: laneY,
      width: Math.max(120, laneRight - laneX),
      height: Math.max(42, laneBottom - laneY),
      rx: 5,
      class: "logic-circuit-lane-band",
    }));
    appendCircuitText(guide, "SW1/SW2 lane", laneX + 12, laneY + 14, {
      class: "logic-circuit-lane-label",
    });
    circuitSvg.appendChild(guide);
  }

  function renderCircuitProvenanceLegend(view) {
    if (!provenanceFilter) return;
    if (!view) {
      provenanceFilter.hidden = true;
      canvas.dataset.provenanceFilter = "all";
      if (statusSourceCount) statusSourceCount.textContent = "0";
      if (statusLocalCount) statusLocalCount.textContent = "0";
      if (statusAssumptionCount) statusAssumptionCount.textContent = "0";
      setSourceTrustSummary("来源待确认");
      return;
    }
    const countsByKind = {"source": 0, "assumption": 0, "local": 0};
    for (const node of view.nodes || []) {
      countsByKind[circuitProvenanceKindForNode(node)] += 1;
    }
    const total = Object.values(countsByKind).reduce((sum, value) => sum + value, 0);
    provenanceFilter.hidden = false;
    for (const button of provenanceFilterButtons) {
      const filter = button.dataset.provenanceFilter || "all";
      const count = filter === "all" ? total : countsByKind[filter] || 0;
      const countElement = button.querySelector("[data-provenance-count]");
      if (countElement) countElement.textContent = String(count);
      button.setAttribute("aria-pressed", filter === state.provenanceFilter ? "true" : "false");
    }
    if (statusSourceCount) statusSourceCount.textContent = String(countsByKind.source);
    if (statusLocalCount) statusLocalCount.textContent = String(countsByKind.local);
    if (statusAssumptionCount) statusAssumptionCount.textContent = String(countsByKind.assumption);
    setSourceTrustSummary(countsByKind.assumption ? `${countsByKind.assumption} 个模型假设` : "来源覆盖已确认");
  }

  function applyCircuitProvenanceFilter() {
    const activeFilter = CIRCUIT_PROVENANCE_FILTERS.has(state.provenanceFilter) ? state.provenanceFilter : "all";
    state.provenanceFilter = activeFilter;
    canvas.dataset.provenanceFilter = activeFilter;
    for (const button of provenanceFilterButtons) {
      button.setAttribute("aria-pressed", (button.dataset.provenanceFilter || "all") === activeFilter ? "true" : "false");
    }
    const filterIsActive = activeFilter !== "all";
    circuitSvg.querySelectorAll(".logic-circuit-node, .logic-circuit-wire, .logic-circuit-junction").forEach((element) => {
      const kind = element.dataset.provenanceKind || "";
      const matches = filterIsActive && kind === activeFilter;
      element.classList.toggle("is-provenance-match", matches);
      element.classList.toggle("is-provenance-muted", filterIsActive && !matches);
    });
  }

  function setCircuitProvenanceFilter(filter) {
    state.provenanceFilter = CIRCUIT_PROVENANCE_FILTERS.has(filter) ? filter : "all";
    applyCircuitProvenanceFilter();
  }

  function renderCircuitWire(wire, provenanceById) {
    const route = Array.isArray(wire.route) ? wire.route : [];
    if (route.length < 2) return;
    const wireId = `${wire.source || ""}->${wire.target || ""}`;
    const isFinal = wire.target === "thr_lock";
    const wireState = visualCircuitState(wire.state);
    const stateClass = wireState ? ` is-${wireState}` : "";
    const selectedClass = state.selectedTargetType === "wire" && state.selectedTargetId === wireId ? " is-selected" : "";
    const faultWire = wire.source === "reverser_inhibited";
    const readableLane = circuitReadableLaneForWire(wire);
    const provenanceKind = circuitProvenanceKindForWire(wire, provenanceById);
    const polyline = createSvgElement("polyline", {
      points: route.map((point) => `${Number(point.x) || 0},${Number(point.y) || 0}`).join(" "),
      class: isFinal ? `logic-circuit-wire is-final${stateClass}${selectedClass}` : `logic-circuit-wire${stateClass}${selectedClass}`,
      "data-source": wire.source || "",
      "data-target": wire.target || "",
      "data-wire-id": wireId,
      "data-state": wireState,
      "data-fault": faultWire ? "true" : "false",
      "data-readable-lane": readableLane || null,
      "data-provenance-kind": provenanceKind,
      "data-provenance-label": circuitProvenanceLabel(provenanceKind),
      tabindex: 0,
      "marker-end": `url(#logic-circuit-arrow-${wireState === "fault" ? "fault" : wireState === "active" ? "active" : "idle"})`,
    });
    const title = createSvgElement("title");
    title.textContent = `${wire.label || `${wire.source || ""} → ${wire.target || ""}`} · 来源: ${circuitProvenanceLabel(provenanceKind)}`;
    polyline.appendChild(title);
    polyline.addEventListener("click", (event) => {
      event.stopPropagation();
      selectAnnotationTarget("wire", wireId, `${wire.source || ""} → ${wire.target || ""}`, event, polyline);
    });
    polyline.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectAnnotationTarget("wire", wireId, `${wire.source || ""} → ${wire.target || ""}`, null, polyline);
      }
    });
    circuitSvg.appendChild(polyline);
  }

  function renderCircuitNode(node) {
    const role = node.circuit_role || "input";
    const color = circuitNodeColor(role);
    const x = Number(node.x) || 0;
    const y = Number(node.y) || 0;
    const width = Number(node.width) || 120;
    const height = Number(node.height) || 28;
    const selectableId = node.linked_node_id || node.id || "";
    const isSelected = state.selectedNodeId && (node.id === state.selectedNodeId || selectableId === state.selectedNodeId);
    const nodeState = visualCircuitState(node.state);
    const displayLabel = circuitDisplayLabel(node);
    const technicalLabel = circuitTechnicalLabel(node);
    const readableLane = circuitReadableLaneForNode(node);
    const provenanceKind = circuitProvenanceKindForNode(node);
    const group = createSvgElement("g", {
      class: `logic-circuit-node${isSelected ? " is-selected" : ""}`,
      "data-node-id": selectableId,
      "data-demo-node-id": node.id || "",
      "data-circuit-role": role,
      "data-state": nodeState,
      "data-raw-state": node.state || "idle",
      "data-readable-lane": readableLane || null,
      "data-provenance-kind": provenanceKind,
      "data-provenance-label": circuitProvenanceLabel(provenanceKind),
      "data-display-label": displayLabel,
      "data-technical-id": node.id || "",
      "data-technical-label": technicalLabel,
      "aria-label": `${displayLabel}${technicalLabel ? `，${technicalLabel}` : ""}`,
      tabindex: 0,
    });
    const title = createSvgElement("title");
    title.textContent = circuitNodeHoverTitle(node);
    group.appendChild(title);

    if (role === "gate") {
      group.appendChild(createSvgElement("rect", {
        x,
        y,
        width,
        height,
        rx: 4,
        class: "logic-circuit-gate-box",
      }));
      group.appendChild(createSvgElement("path", {
        d: `M${x + 7},${y + 5} L${x + 15},${y + 5} A6,6 0 0 1 ${x + 15},${y + 19} L${x + 7},${y + 19} Z`,
        class: "logic-circuit-gate-shape",
      }));
      appendCircuitText(group, "&", x + 16, y + 16, {
        class: "logic-circuit-gate-type",
        "text-anchor": "middle",
      });
      appendCircuitText(group, displayLabel, x + width / 2, y + 18, {
        class: "logic-circuit-gate-label logic-circuit-short-label",
        "text-anchor": "middle",
      });
      const subtitle = circuitNodeSubtitle(node);
      if (subtitle) {
        const lines = Array.isArray(subtitle) ? subtitle : [subtitle];
        appendCircuitMultilineText(group, lines, x + width / 2, y + height - (lines.length > 1 ? 18 : 8), {
          class: "logic-circuit-gate-caption",
          "text-anchor": "middle",
        });
      }
    } else {
      group.appendChild(createSvgElement("rect", {
        x,
        y,
        width,
        height,
        rx: role === "final_output" ? 4 : 3,
        class: "logic-circuit-node-box",
        stroke: color,
      }));
      appendCircuitText(group, displayLabel, x + width / 2, y + Math.min(19, height / 2 + 4), {
        class: role === "final_output"
          ? "logic-circuit-node-title logic-circuit-short-label is-final"
          : "logic-circuit-node-title logic-circuit-short-label",
        "text-anchor": "middle",
      });
      const subtitle = circuitNodeSubtitle(node);
      if (height >= 32 && subtitle) {
        appendCircuitText(group, subtitle, x + width / 2, y + height - 7, {
          class: "logic-circuit-node-subtitle",
          "text-anchor": "middle",
        });
      }
    }
    renderCircuitNodeDetails(group, node, x, y, width, height);
    group.addEventListener("click", (event) => selectNode(selectableId, event, group));
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectNode(selectableId, null, group);
      }
    });
    circuitSvg.appendChild(group);
  }

  function circuitNodeSubtitle(node) {
    const id = node.id || "";
    if (id === "logic1") return "SW1 · RA · 未抑制";
    if (id === "logic2") return "SW2 · 在地 · EEC";
    if (id === "logic3") return ["TLS/N1K/TRA", "门限成立"];
    if (id === "logic4") return "L3 · VDT90";
    if (id === "thr_lock") return "L4 成立";
    return "";
  }

  function renderCircuitJunctions(view, provenanceById) {
    for (const junction of view.junctions || []) {
      const junctionState = visualCircuitState(junction.state);
      const faultJunction = junction.source === "reverser_inhibited";
      const provenanceKind = provenanceById.get(junction.source || "") || "local";
      circuitSvg.appendChild(createSvgElement("circle", {
        cx: Number(junction.x) || 0,
        cy: Number(junction.y) || 0,
        r: 3,
        class: `logic-circuit-junction is-${junctionState}`,
        "data-source": junction.source || "",
        "data-state": junctionState,
        "data-fault": faultJunction ? "true" : "false",
        "data-provenance-kind": provenanceKind,
      }));
    }
  }

  function renderCircuitBadges(view) {
    void view;
  }

  function renderCircuitView(view, size) {
    circuitSvg.innerHTML = "";
    circuitSvg.hidden = false;
    circuitSvg.removeAttribute("hidden");
    circuitSvg.setAttribute("width", String(size.width));
    circuitSvg.setAttribute("height", String(size.height));
    circuitSvg.setAttribute("viewBox", `0 0 ${size.width} ${size.height}`);
    renderCircuitChrome(view, size);
    renderCircuitLaneGuides(view, size);
    renderCircuitProvenanceLegend(view);
    const provenanceById = new Map((view.nodes || []).map((node) => [node.id || "", circuitProvenanceKindForNode(node)]));
    for (const wire of view.wires || []) {
      renderCircuitWire(wire, provenanceById);
    }
    renderCircuitJunctions(view, provenanceById);
    for (const node of view.nodes || []) {
      renderCircuitNode(node);
    }
    renderCircuitBadges(view);
    applyCircuitProvenanceFilter();
  }

  function renderEdges(payload, size) {
    svg.innerHTML = "";
    svg.setAttribute("width", String(size.width));
    svg.setAttribute("height", String(size.height));
    svg.setAttribute("viewBox", `0 0 ${size.width} ${size.height}`);
    for (const edge of payload.edges || []) {
      const route = Array.isArray(edge.route) ? edge.route : [];
      if (route.length < 2) continue;
      const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
      polyline.setAttribute("points", route.map((point) => `${Number(point.x) || 0},${Number(point.y) || 0}`).join(" "));
      polyline.setAttribute("fill", "none");
      polyline.setAttribute("stroke", "rgba(54,198,216,0.72)");
      polyline.setAttribute("stroke-width", "2");
      polyline.setAttribute("stroke-linecap", "round");
      polyline.setAttribute("stroke-linejoin", "round");
      svg.appendChild(polyline);

      const end = route[route.length - 1];
      const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", String(Number(end.x) || 0));
      dot.setAttribute("cy", String(Number(end.y) || 0));
      dot.setAttribute("r", "3");
      dot.setAttribute("fill", "rgba(25,210,143,0.9)");
      svg.appendChild(dot);

      const mid = route[Math.max(0, Math.floor(route.length / 2) - 1)];
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", String(Number(mid.x) || 0));
      label.setAttribute("y", String((Number(mid.y) || 0) - 6));
      label.setAttribute("fill", "rgba(216,228,242,0.76)");
      label.setAttribute("font-size", "10");
      label.textContent = sourceAnchorLabel(anchorsForEdge(edge));
      svg.appendChild(label);
    }
  }

  function renderNodes(payload) {
    nodeLayer.innerHTML = "";
    for (const node of payload.nodes || []) {
      const element = document.createElement("article");
      element.className = "logic-node";
      if (node.id === state.selectedNodeId) {
        element.classList.add("is-selected");
      }
      element.dataset.nodeId = node.id || "";
      element.dataset.kind = node.node_kind || "logic";
      element.style.left = `${Number(node.x) || 0}px`;
      element.style.top = `${Number(node.y) || 0}px`;
      element.style.width = `${Number(node.width) || 180}px`;
      element.style.height = `${Math.max(72, Number(node.height) || 104)}px`;
      const anchorTitle = sourceAnchorQuote(anchorsForNode(node));
      if (anchorTitle) {
        element.title = anchorTitle;
      }
      element.innerHTML = `
        <span class="logic-node-kind">${escapeText(node.node_kind || "logic")}</span>
        <div class="logic-node-title">
          <strong>${escapeText(node.label || node.id)}</strong>
          <code>${escapeText(node.id)}</code>
        </div>
        <div class="logic-node-desc">${escapeText(node.description_zh || "")}</div>
        <div class="logic-node-anchor">来源：${escapeText(sourceAnchorLabel(anchorsForNode(node)))}</div>
      `;
      element.addEventListener("click", (event) => selectNode(node.id || "", event, element));
      nodeLayer.appendChild(element);
    }
  }

  function renderParameterPanels(payload) {
    panelLayer.innerHTML = "";
    for (const panel of payload.parameter_panels || []) {
      const min = Number(panel.min) || 0;
      const max = Number(panel.max) || Math.max(1, min);
      const value = Number(panel.default) || min;
      const unit = panel.unit ? ` ${escapeText(panel.unit)}` : "";
      const element = document.createElement("aside");
      element.className = "logic-param-panel";
      element.style.left = `${Number(panel.x) || 0}px`;
      element.style.top = `${Number(panel.y) || 0}px`;
      element.style.width = `${Number(panel.width) || 140}px`;
      element.style.height = `${Number(panel.height) || 74}px`;
      element.innerHTML = `
        <strong><span>${escapeText(panel.label || panel.id)}</span><code>${escapeText(panel.node_id)}</code></strong>
        <input type="range" min="${escapeText(min)}" max="${escapeText(max)}" value="${escapeText(value)}" disabled>
        <code>${escapeText(value)}${unit}</code>
      `;
      panelLayer.appendChild(element);
    }
  }

  function renderNotes(payload) {
    notes.innerHTML = "";
    const items = payload.drawing_notes || [];
    if (!items.length) {
      notes.innerHTML = '<li class="muted">模型未返回布局说明。</li>';
      return;
    }
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      notes.appendChild(li);
    }
  }

  function setWorkflowSteps(activeStep, completedSteps) {
    workflowSteps.forEach((element) => {
      const step = element.dataset.workflowStep || "";
      element.classList.toggle("is-active", step === activeStep);
      element.classList.toggle("is-complete", completedSteps.includes(step));
      element.classList.toggle("is-locked", !completedSteps.includes(step) && step !== activeStep);
    });
  }

  function hasUpdatedChange() {
    return state.changeHistory.some((item) => item.status === "updated");
  }

  function hasPendingChange() {
    return Boolean(state.interpretationPayload) || state.changeHistory.some((item) => item.status === "needs_confirmation");
  }

  function renderWorkflowOverview() {
    if (!state.requirementsPayload && !state.drawingPayload) {
      workflowStage.textContent = "等待需求输入";
      workflowDetail.textContent = "先从需求理解页进入；本步产出候选逻辑图，下一页生成故障矩阵。";
      setWorkflowSteps("requirements", []);
      return;
    }
    if (hasUpdatedChange()) {
      workflowStage.textContent = "图纸已更新";
      workflowDetail.textContent = "图纸已按确认意见更新；下一步把候选图纸送入故障矩阵。";
      setWorkflowSteps("fault", ["requirements", "drawing"]);
      return;
    }
    if (hasPendingChange()) {
      workflowStage.textContent = "等待用户确认修改意图";
      workflowDetail.textContent = "模型已理解批注，请确认意图后再让模型更新完整图纸。";
      setWorkflowSteps("drawing", ["requirements"]);
      return;
    }
    if (state.drawingPayload) {
      workflowStage.textContent = "初版图纸已生成";
      workflowDetail.textContent = state.revisionHandoff
        ? "已从沙盒审查返回；请把需要回写到逻辑图的意见写入修改窗口。"
        : "本步产出候选逻辑图；确认节点/连线后进入故障矩阵。";
      setWorkflowSteps("drawing", ["requirements"]);
      return;
    }
    workflowStage.textContent = "正在生成初版图纸";
    workflowDetail.textContent = "已载入澄清后的需求，等待节点、连线和参数面板形成候选逻辑图。";
    setWorkflowSteps("drawing", ["requirements"]);
  }

  function drawingMetrics(payload) {
    return {
      nodes: (payload.nodes || []).length,
      edges: (payload.edges || []).length,
      panels: (payload.parameter_panels || []).length,
    };
  }

  function changeStatusText(status) {
    if (status === "updated") return "已更新";
    if (status === "cancelled") return "已取消";
    if (status === "failed") return "失败";
    return "等待确认";
  }

  function renderChangeHistory() {
    historyCount.textContent = `${state.changeHistory.length} changes`;
    historyList.innerHTML = "";
    if (!state.changeHistory.length) {
      historyList.innerHTML = '<p class="muted">每次批注、模型理解、用户确认和图纸更新都会记录在这里。</p>';
      return;
    }
    for (const item of state.changeHistory) {
      const card = document.createElement("article");
      card.className = "logic-change-card";
      card.dataset.status = item.status || "needs_confirmation";
      const metrics = item.updated_metrics || {};
      const proposed = item.proposed_changes || [];
      card.innerHTML = `
        <div class="logic-change-card-head">
          <strong>Change ${escapeText(item.index)}</strong>
          <span>${escapeText(changeStatusText(item.status))}</span>
        </div>
        <div class="logic-change-meta">
          <span>node:${escapeText(item.target_node_id || "none")}</span>
          <span>${escapeText(item.provider || provider.value)}</span>
          ${item.annotation_batch_count ? `<span>${escapeText(item.annotation_batch_count)} notes</span>` : ""}
        </div>
        <p class="logic-change-annotation">${escapeText(item.annotation_text || "")}</p>
        <p class="logic-change-understanding">${escapeText(item.understanding_zh || "等待模型理解。")}</p>
        ${item.confirmation_question_zh ? `<p class="logic-change-question">${escapeText(item.confirmation_question_zh)}</p>` : ""}
        ${item.updated_summary_zh ? `<p class="logic-change-updated">${escapeText(item.updated_summary_zh)}</p>` : ""}
        ${metrics.nodes != null ? `<div class="logic-change-meta"><span>${escapeText(metrics.nodes)} nodes</span><span>${escapeText(metrics.edges)} edges</span><span>${escapeText(metrics.panels)} panels</span></div>` : ""}
        ${proposed.length ? `<details><summary>模型修改项</summary><ul>${proposed.map((entry) => `<li>${escapeText(entry)}</li>`).join("")}</ul></details>` : ""}
      `;
      historyList.appendChild(card);
    }
  }

  function recordChangeInterpretation(payload, annotationText, options) {
    const recordOptions = options || {};
    const annotationBatch = Array.isArray(recordOptions.annotationBatch) ? recordOptions.annotationBatch : [];
    const record = {
      id: `change_${Date.now()}_${state.changeHistory.length + 1}`,
      index: state.changeHistory.length + 1,
      status: "needs_confirmation",
      target_node_id: payload.target_node_id || state.selectedNodeId || "",
      annotation_text: annotationText,
      understanding_zh: payload.understanding_zh || "",
      requirements_match_zh: payload.requirements_match_zh || "",
      confirmation_question_zh: payload.confirmation_question_zh || "",
      affected_nodes: payload.affected_nodes || [],
      affected_edges: payload.affected_edges || [],
      affected_parameter_panels: payload.affected_parameter_panels || [],
      proposed_changes: payload.proposed_changes || [],
      provider: payload.llm ? payload.llm.provider : provider.value,
      annotation_batch_count: annotationBatch.length,
    };
    state.changeHistory.push(record);
    state.activeChangeId = record.id;
    saveChangeHistory();
    if (recordOptions.openHistory !== false) {
      openInspectorDetails(changeHistoryDetails);
    }
    renderChangeHistory();
    renderWorkflowOverview();
    return record;
  }

  function activeChangeRecord() {
    return state.changeHistory.find((item) => item.id === state.activeChangeId)
      || [...state.changeHistory].reverse().find((item) => item.status === "needs_confirmation")
      || null;
  }

  function markChangeUpdated(payload) {
    const record = activeChangeRecord();
    if (!record) return;
    record.status = "updated";
    record.updated_summary_zh = payload.summary_zh || "模型已更新图纸。";
    record.updated_metrics = drawingMetrics(payload);
    record.change_applied = payload.change_applied || {};
    state.activeChangeId = "";
    saveChangeHistory();
    openInspectorDetails(changeHistoryDetails);
    renderChangeHistory();
    renderWorkflowOverview();
  }

  function markActiveChangeCancelled(reason) {
    const record = activeChangeRecord();
    if (!record || record.status !== "needs_confirmation") return;
    record.status = "cancelled";
    record.cancel_reason = reason || "用户取消确认。";
    state.activeChangeId = "";
    saveChangeHistory();
    openInspectorDetails(changeHistoryDetails);
    renderChangeHistory();
    renderWorkflowOverview();
  }

  function markActiveChangeFailed(message) {
    const record = activeChangeRecord();
    if (!record) return;
    record.status = "failed";
    record.error_message = message || "更新失败。";
    state.activeChangeId = "";
    saveChangeHistory();
    openInspectorDetails(changeHistoryDetails);
    renderChangeHistory();
    renderWorkflowOverview();
  }

  function renderAnnotationDrafts() {
    if (annotationCount) annotationCount.textContent = `${state.annotationDrafts.length} 条标注意见`;
    if (annotationList) {
      annotationList.innerHTML = "";
      state.annotationDrafts.slice(-3).forEach((item) => {
        const li = document.createElement("li");
        li.className = "logic-annotation-item";
        li.innerHTML = `<strong>${escapeText(annotationTargetLabel(item.target_type, item.target_id, item.target_label))}</strong><span>${escapeText(item.text)}</span>`;
        annotationList.appendChild(li);
      });
    }
    if (submitAnnotationsButton) {
      submitAnnotationsButton.disabled = state.busy || state.annotationDrafts.length === 0;
    }
    if (annotationSubmitState && !state.annotationDrafts.length) {
      annotationSubmitState.textContent = state.selectedTargetId ? "已选中对象，可添加批注" : "选择节点或连线后添加批注";
    }
  }

  function updateAnnotationControls() {
    const hasTarget = Boolean(state.selectedTargetId);
    const hasText = Boolean(nodeCommentText && nodeCommentText.value.trim());
    if (annotationPopover) annotationPopover.hidden = !hasTarget;
    if (selectedTargetLabel) {
      selectedTargetLabel.textContent = annotationTargetLabel(state.selectedTargetType, state.selectedTargetId, state.selectedTargetLabel);
    }
    const context = selectedTargetContext();
    if (annotationSource) annotationSource.textContent = context.sourceText;
    if (annotationParams) annotationParams.textContent = context.paramText;
    updateAnnotationPopoverPosition();
    if (addAnnotationButton) addAnnotationButton.disabled = state.busy || !hasTarget || !hasText;
    renderAnnotationDrafts();
  }

  function selectAnnotationTarget(type, id, label, event, targetElement) {
    state.selectedTargetType = type || "";
    state.selectedTargetId = id || "";
    state.selectedTargetLabel = annotationTargetLabel(type, id, label);
    state.selectedNodeId = type === "node" ? (id || "") : "";
    rememberPopoverAnchor(event, targetElement);
    for (const element of nodeLayer.querySelectorAll(".logic-node")) {
      element.classList.toggle("is-selected", type === "node" && element.dataset.nodeId === state.selectedNodeId);
    }
    for (const element of circuitSvg.querySelectorAll(".logic-circuit-node")) {
      element.classList.toggle("is-selected", type === "node" && element.dataset.nodeId === state.selectedNodeId);
    }
    for (const element of circuitSvg.querySelectorAll(".logic-circuit-wire")) {
      element.classList.toggle("is-selected", type === "wire" && element.dataset.wireId === state.selectedTargetId);
    }
    updateChangeControls();
    updateAnnotationControls();
    renderObjectContextDrawer();
    updateAnnotationPopoverPosition();
    if (nodeCommentText && state.selectedTargetId) nodeCommentText.focus();
  }

  function addAnnotationDraft() {
    if (!state.selectedTargetId || !nodeCommentText) return;
    const text = nodeCommentText.value.trim();
    if (!text) return;
    state.annotationDrafts.push({
      id: `annotation_${Date.now()}_${state.annotationDrafts.length + 1}`,
      target_type: state.selectedTargetType || "node",
      target_id: state.selectedTargetId,
      target_label: state.selectedTargetLabel,
      text,
      provider: providerValue(),
      created_at: new Date().toISOString(),
    });
    nodeCommentText.value = "";
    saveAnnotationBatch("draft");
    if (annotationSubmitState) annotationSubmitState.textContent = "标注意见已暂存，继续选择节点或连线。";
    updateAnnotationControls();
  }

  function submitAnnotationBatch() {
    submitAnnotationBatchToAi();
  }

  function renderBatchInterpretation(payload, requestPayload) {
    state.interpretationPayload = {
      ...payload,
      annotation_batch: requestPayload && Array.isArray(requestPayload.annotation_batch) ? requestPayload.annotation_batch : payload.annotation_batch,
      selected_nodes: requestPayload && Array.isArray(requestPayload.selected_nodes) ? requestPayload.selected_nodes : payload.selected_nodes,
      selected_edges: requestPayload && Array.isArray(requestPayload.selected_edges) ? requestPayload.selected_edges : payload.selected_edges,
    };
    payload = state.interpretationPayload;
    if (batchInterpretationPanel) batchInterpretationPanel.hidden = false;
    if (batchSummary) {
      batchSummary.textContent = payload.annotation_batch_summary_zh
        || payload.understanding_zh
        || "AI 已归并本次标注意见。";
    }
    if (batchConflictSummary) {
      batchConflictSummary.textContent = payload.conflict_summary_zh || "未发现冲突。";
    }
    if (batchProposedChanges) {
      batchProposedChanges.innerHTML = "";
      const changes = Array.isArray(payload.proposed_changes) ? payload.proposed_changes : [];
      if (!changes.length) {
        batchProposedChanges.innerHTML = '<li class="muted">AI 未返回具体结构化修订建议。</li>';
      } else {
        for (const item of changes) {
          const li = document.createElement("li");
          li.textContent = item;
          batchProposedChanges.appendChild(li);
        }
      }
    }
    if (batchConfirmationQuestion) {
      batchConfirmationQuestion.textContent = payload.confirmation_question_zh || "请确认是否按本次批注生成修订版逻辑图？";
    }
    recordChangeInterpretation(
      payload,
      requestPayload && requestPayload.annotation_text ? requestPayload.annotation_text : (payload.annotation_text || "批量标注意见"),
      {openHistory: false, annotationBatch: requestPayload ? requestPayload.annotation_batch : []},
    );
    if (annotationSubmitState) annotationSubmitState.textContent = "AI 已生成结构化修订建议";
    updateChangeControls();
  }

  async function submitAnnotationBatchToAi() {
    if (!state.annotationDrafts.length) return;
    const submitted = saveAnnotationBatch("submitted");
    if (!state.requirementsPayload || !state.drawingPayload) {
      if (annotationSubmitState) annotationSubmitState.textContent = `已提交 ${submitted.annotations.length} 条标注意见`;
      if (submitAnnotationsButton) submitAnnotationsButton.disabled = true;
      return;
    }
    const requestPayload = buildAnnotationBatchRequest();
    setBusy(true);
    if (annotationSubmitState) annotationSubmitState.textContent = "AI 正在归并标注意见";
    try {
      const payload = await requestAnnotationBatchInterpretation(requestPayload);
      renderBatchInterpretation(payload, requestPayload);
    } catch (error) {
      if (annotationSubmitState) {
        annotationSubmitState.textContent = error.message || "AI 未能归并本次标注意见";
      }
    } finally {
      setBusy(false);
    }
  }

  function updateChangeControls() {
    const hasDraft = Boolean(state.drawingPayload);
    const hasRequirements = Boolean(state.requirementsPayload);
    const hasText = Boolean(changeText.value.trim());
    submitChangeButton.disabled = state.busy || !hasDraft || !hasRequirements || !hasText;
    confirmChangeButton.disabled = state.busy || !state.interpretationPayload || !hasDraft;
    faultNext.disabled = state.busy || !hasDraft;
    changeText.disabled = state.busy || !hasDraft || !hasRequirements;
    clearChangeButton.disabled = state.busy;
    cancelChangeButton.disabled = state.busy;
    if (batchConfirmUpdateButton) {
      batchConfirmUpdateButton.disabled = state.busy || !state.interpretationPayload || !hasDraft;
    }
    const selectedCopy = state.selectedTargetLabel || state.selectedNodeId || "未选择";
    selectedNode.textContent = selectedCopy;
    if (logicDetailSelectedNode) logicDetailSelectedNode.textContent = selectedCopy;
    updateAnnotationControls();
    renderWorkflowOverview();
  }

  function selectNode(nodeId, event, targetElement) {
    selectAnnotationTarget("node", nodeId || "", nodeId || "", event, targetElement);
  }

  function clearInterpretation() {
    state.interpretationPayload = null;
    interpretationBox.hidden = true;
    interpretationState.textContent = "WAITING";
    interpretationSummary.textContent = "";
    interpretationMatch.textContent = "";
    interpretationQuestion.textContent = "";
    proposedChanges.innerHTML = "";
    if (batchInterpretationPanel) batchInterpretationPanel.hidden = true;
    if (batchSummary) batchSummary.textContent = "等待提交标注意见。";
    if (batchConflictSummary) batchConflictSummary.textContent = "等待 AI 判断。";
    if (batchProposedChanges) batchProposedChanges.innerHTML = "";
    if (batchConfirmationQuestion) batchConfirmationQuestion.textContent = "";
    if (batchConfirmUpdateButton) batchConfirmUpdateButton.disabled = true;
    updateChangeControls();
  }

  function renderInterpretation(payload) {
    state.interpretationPayload = payload;
    interpretationBox.hidden = false;
    interpretationState.textContent = "需要确认";
    interpretationSummary.textContent = payload.understanding_zh || "模型已理解修改意见。";
    interpretationMatch.textContent = payload.requirements_match_zh || "";
    interpretationQuestion.textContent = payload.confirmation_question_zh || "请确认是否按此意图更新图纸？";
    proposedChanges.innerHTML = "";
    const changes = payload.proposed_changes || [];
    if (!changes.length) {
      proposedChanges.innerHTML = '<li class="muted">模型未返回具体修改项。</li>';
    } else {
      for (const item of changes) {
        const li = document.createElement("li");
        li.textContent = item;
        proposedChanges.appendChild(li);
      }
    }
    updateChangeControls();
  }

  function renderDrawing(payload) {
    state.drawingPayload = payload;
    renderTemplateEntryState();
    window.localStorage.setItem(DRAWING_KEY, JSON.stringify(payload));
    const circuitView = payload.circuit_view && payload.circuit_view.kind ? payload.circuit_view : null;
    renderReconstructionMode(payload, circuitView);
    const selectableNodes = circuitView ? (circuitView.nodes || []) : (payload.nodes || []);
    const nodeIds = new Set(selectableNodes.map((node) => node.linked_node_id || node.id));
    const selectableWires = circuitView ? (circuitView.wires || []) : (payload.edges || []);
    const wireIds = new Set(selectableWires.map((wire) => `${wire.source || ""}->${wire.target || ""}`));
    if (state.selectedNodeId && !nodeIds.has(state.selectedNodeId)) {
      state.selectedNodeId = "";
    }
    if (state.selectedTargetType === "node" && !nodeIds.has(state.selectedTargetId)) {
      state.selectedTargetType = "";
      state.selectedTargetId = "";
      state.selectedTargetLabel = "";
    }
    if (state.selectedTargetType === "wire" && !wireIds.has(state.selectedTargetId)) {
      state.selectedTargetType = "";
      state.selectedTargetId = "";
      state.selectedTargetLabel = "";
    }
    const size = circuitView && circuitView.canvas
      ? {
        width: Math.max(900, Number(circuitView.canvas.width) || 900),
        height: Math.max(400, Number(circuitView.canvas.height) || 400),
      }
      : canvasSize(payload);
    canvas.dataset.viewMode = circuitView ? "circuit" : "model";
    canvas.setAttribute("data-fit-mode", "fit-to-view");
    if (circuitView) {
      const readableLanes = new Set();
      for (const node of circuitView.nodes || []) {
        const lane = circuitReadableLaneForNode(node);
        if (lane) readableLanes.add(lane);
      }
      for (const wire of circuitView.wires || []) {
        const lane = circuitReadableLaneForWire(wire);
        if (lane) readableLanes.add(lane);
      }
      if (readableLanes.size) {
        canvas.dataset.readableLanes = Array.from(readableLanes).join(" ");
      } else {
        delete canvas.dataset.readableLanes;
      }
    } else {
      delete canvas.dataset.readableLanes;
    }
    canvas.style.minHeight = `${size.height}px`;
    canvas.style.width = "100%";
    const viewportWidth = Math.max(320, canvas.clientWidth || canvas.parentElement.clientWidth || size.width);
    const parentHeight = canvas.parentElement ? canvas.parentElement.clientHeight : size.height;
    const toolbarHeight = logicCanvasToolbar ? logicCanvasToolbar.getBoundingClientRect().height : 0;
    const viewportHeight = Math.max(360, parentHeight - toolbarHeight - 88);
    const fitScale = Math.min(
      1,
      Math.max(0.48, Math.min((viewportWidth - 18) / size.width, (viewportHeight - 18) / size.height))
    );
    canvas.dataset.fitScale = String(fitScale.toFixed(3));
    canvas.style.minHeight = `${Math.ceil(size.height * fitScale) + 24}px`;
    circuitSvg.style.width = `${size.width}px`;
    circuitSvg.style.height = `${size.height}px`;
    svg.style.width = `${size.width}px`;
    svg.style.height = `${size.height}px`;
    nodeLayer.style.width = `${size.width}px`;
    nodeLayer.style.height = `${size.height}px`;
    panelLayer.style.width = `${size.width}px`;
    panelLayer.style.height = `${size.height}px`;
    [circuitSvg, svg, nodeLayer, panelLayer].forEach((layer) => {
      layer.style.transform = `scale(${fitScale})`;
      layer.style.transformOrigin = "0 0";
    });
    if (circuitView) {
      svg.innerHTML = "";
      nodeLayer.innerHTML = "";
      panelLayer.innerHTML = "";
      svg.hidden = true;
      svg.setAttribute("hidden", "");
      renderCircuitView(circuitView, size);
      renderCircuitEvaluationPanel(circuitView);
    } else {
      circuitSvg.innerHTML = "";
      circuitSvg.hidden = true;
      circuitSvg.setAttribute("hidden", "");
      renderCircuitProvenanceLegend(null);
      renderCircuitEvaluationPanel(null);
      svg.hidden = false;
      svg.removeAttribute("hidden");
      renderEdges(payload, size);
      renderNodes(payload);
      renderParameterPanels(payload);
    }
    renderDrawingStreamTimeline(payload, circuitView);
    renderFlags(payload);
    renderNotes(payload);
    resultState.textContent = circuitView ? "电路图已完成绘制" : "模型已完成绘制";
    resultSummary.textContent = payload.summary_zh || "模型已生成初版逻辑链路图。";
    counts.textContent = circuitView
      ? `${(circuitView.rows || []).length} rows · ${(circuitView.nodes || []).length} circuit nodes · ${(circuitView.wires || []).length} wires`
      : `${(payload.nodes || []).length} nodes · ${(payload.edges || []).length} edges · ${(payload.parameter_panels || []).length} panels`;
    if (bottomRunNodeCount) {
      const nodeTotal = circuitView ? (circuitView.nodes || []).length : (payload.nodes || []).length;
      bottomRunNodeCount.textContent = `节点 ${nodeTotal}/${nodeTotal}`;
    }
    if (bottomRunEdgeCount) {
      const edgeTotal = circuitView ? (circuitView.wires || []).length : (payload.edges || []).length;
      bottomRunEdgeCount.textContent = `连线 ${edgeTotal}/${edgeTotal}`;
    }
    source.textContent = payload.source_requirements_sha256 ? "需求来源已确认" : "来源待确认";
    renderBurdenSummary(payload);
    renderObjectContextDrawer();
    updateChangeControls();
    renderWorkflowOverview();
  }

  async function generateDrawing() {
    beginTask("读取已澄清需求", "正在从需求理解页载入结构化需求。");
    setBusy(true);
    clearInterpretation();
    try {
      setProgress(18, "提交模型", "已确认需求会被发送给大模型，由模型生成节点坐标、连线路径和参数面板。", "model");
      const payload = await requestDrawing();
      setProgress(84, "生成布局", "模型已返回图纸草稿，正在按模型坐标渲染。", "layout");
      state.changeHistory = [];
      state.activeChangeId = "";
      saveChangeHistory();
      window.localStorage.removeItem(FAULT_DRAFT_KEY);
      renderChangeHistory();
      renderWorkflowOverview();
      renderDrawing(payload);
      setProgress(96, "渲染图纸", "节点、连线和参数面板已按模型输出绘制。", "render");
      finishTask("绘制完成", "初版逻辑链路图已由大模型生成。");
    } catch (error) {
      resultState.textContent = "绘制失败";
      const message = error.message || "模型绘图失败，请重新绘制或切换模型。";
      resultSummary.textContent = message;
      failTask("绘制失败", message);
    } finally {
      setBusy(false);
    }
  }

  async function submitChange() {
    const annotationText = changeText.value.trim();
    if (!annotationText) return;
    beginTask("理解修改意见", "模型正在回到原需求和当前图纸中定位这条批注。");
    setBusy(true);
    clearInterpretation();
    try {
      setProgress(28, "提交模型", "正在让模型解释修改意图，并列出受影响节点、连线和参数面板。", "model");
      const payload = await requestChangeInterpretation(annotationText);
      setProgress(88, "等待确认", "模型已返回理解结果，正在生成确认问题。", "layout");
      renderInterpretation(payload);
      recordChangeInterpretation(payload, annotationText);
      finishTask("需要用户确认", "请确认模型理解是否符合你的修改意图。");
    } catch (error) {
      interpretationBox.hidden = false;
      interpretationState.textContent = "理解失败";
      const message = error.message || "模型未能理解修改意见，请简化意见后重试。";
      interpretationSummary.textContent = message;
      interpretationMatch.textContent = "";
      interpretationQuestion.textContent = "";
      proposedChanges.innerHTML = "";
      failTask("理解失败", message);
    } finally {
      setBusy(false);
    }
  }

  async function confirmChange() {
    if (!state.interpretationPayload) return;
    beginTask("更新逻辑图纸", "用户已确认修改意图，模型正在生成完整更新后的图纸。");
    setBusy(true);
    try {
      setProgress(24, "提交模型", "正在把已确认修改意图发送给模型。", "model");
      const payload = await requestDrawingUpdate(state.interpretationPayload);
      setProgress(84, "生成布局", "模型已返回更新后的节点、连线和参数面板。", "layout");
      window.localStorage.removeItem(FAULT_DRAFT_KEY);
      renderDrawing(payload);
      markChangeUpdated(payload);
      clearInterpretation();
      changeText.value = "";
      setProgress(96, "渲染图纸", "新的草稿已保存到本地。", "render");
      finishTask("更新完成", "逻辑链路图已按确认意见由模型更新。");
    } catch (error) {
      const message = error.message || "图纸更新失败，请重新确认修改意图后重试。";
      markActiveChangeFailed(message);
      failTask("更新失败", message);
    } finally {
      setBusy(false);
    }
  }

  function boot() {
    activateWorkbenchTab(workbenchDrawer ? workbenchDrawer.dataset.activeTab : "none");
    syncDrawerFromCircuitInputs();
    hydrateDrawerFromHash();
    syncProviderControls(provider);
    state.revisionHandoff = loadSandboxRevisionHandoff();
    state.requirementsPayload = loadRequirementsPayload();
    state.drawingPayload = loadDrawingPayload();
    state.changeHistory = loadChangeHistory();
    state.annotationDrafts = loadAnnotationBatch();
    renderInput(state.requirementsPayload);
    renderBurdenSummary(state.drawingPayload);
    renderWorkflowOverview();
    if (state.requirementsPayload && state.drawingPayload && state.changeHistory.length) {
      beginTask("载入修改草稿", "正在读取上次保存的图纸和修改历史。");
      renderDrawing(state.drawingPayload);
      finishTask("已载入修改草稿", "当前图纸包含用户确认过的模型修改历史。");
    } else if (state.drawingPayload) {
      const hasRequirements = Boolean(state.requirementsPayload);
      beginTask(hasRequirements ? "载入已保存图纸" : "载入本地草稿", "正在读取上次保存的模型图纸。");
      renderDrawing(state.drawingPayload);
      finishTask(
        hasRequirements ? "已载入已保存图纸" : "已载入本地草稿",
        hasRequirements
          ? "当前图纸已从本地草稿恢复；可继续批注确认或进入故障注入准备。"
          : "当前只显示上次保存的图纸；修改闭环需要先从需求理解页载入原需求。",
      );
    } else if (state.requirementsPayload) {
      generateDrawing();
    } else {
      failTask("缺少需求输入", "请先在需求理解页完成澄清，然后点击“进入逻辑链路绘制”。");
    }
    updateChangeControls();
    renderChangeHistory();
    renderAnnotationDrafts();
    renderSandboxRevisionHandoff();
    renderWorkflowOverview();
    syncDrawerFromCircuitInputs();
    renderTemplateEntryState();
  }

  provider.addEventListener("change", () => syncProviderControls(provider));
  if (logicBottomProvider) {
    logicBottomProvider.addEventListener("change", () => syncProviderControls(logicBottomProvider));
  }
  if (commandPaletteOpen) commandPaletteOpen.addEventListener("click", openCommandPalette);
  if (commandPaletteClose) commandPaletteClose.addEventListener("click", closeCommandPalette);
  if (commandPaletteFilter) commandPaletteFilter.addEventListener("input", () => filterCommandPalette(commandPaletteFilter.value));
  logicModeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.logicMode || "canvas";
      activateBottomDrawer(mode === "canvas" ? "none" : mode);
    });
  });
  bottomDrawerButtons.forEach((button) => {
    button.addEventListener("click", () => activateBottomDrawer(button.dataset.bottomDrawerTab || "none"));
  });
  if (bottomDrawerClose) bottomDrawerClose.addEventListener("click", () => activateBottomDrawer("none"));
  panelToggleButtons.forEach((button) => {
    button.addEventListener("click", () => togglePanel(button.dataset.panelToggle || ""));
  });
  document.querySelectorAll("[data-command-open-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      activateBottomDrawer(button.dataset.commandOpenMode || "none");
      closeCommandPalette();
    });
  });
  document.querySelectorAll("[data-command-run-action]").forEach((button) => {
    button.addEventListener("click", () => {
      handleRunAction(button.dataset.commandRunAction || "run");
      closeCommandPalette();
    });
  });
  document.querySelectorAll("[data-command-focus-canvas]").forEach((button) => {
    button.addEventListener("click", () => {
      focusCanvas();
      closeCommandPalette();
    });
  });
  document.querySelectorAll("[data-command-close-panels]").forEach((button) => {
    button.addEventListener("click", () => {
      closeAuxiliaryPanels();
      closeCommandPalette();
    });
  });
  templateActionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      handleTemplateAction(button.dataset.templateAction || button.dataset.commandTemplateAction || "blank");
      closeCommandPalette();
    });
  });
  Object.values(drawerInputs).forEach((element) => {
    if (!element) return;
    const eventName = element.type === "checkbox" ? "change" : "input";
    element.addEventListener(eventName, syncDrawerToCircuitInputs);
  });
  if (drawerPreset) {
    drawerPreset.addEventListener("change", () => {
      if (drawerPreset.value) applyCircuitPreset(drawerPreset.value);
      syncDrawerFromCircuitInputs();
    });
  }
  document.querySelectorAll("[data-run-action]").forEach((button) => {
    button.addEventListener("click", () => handleRunAction(button.dataset.runAction || "run"));
  });
  regenerate.addEventListener("click", generateDrawing);
  faultNext.addEventListener("click", () => {
    window.location.href = "/fault-injection-prepare";
  });
  changeText.addEventListener("input", updateChangeControls);
  if (nodeCommentText) nodeCommentText.addEventListener("input", updateAnnotationControls);
  if (addAnnotationButton) addAnnotationButton.addEventListener("click", addAnnotationDraft);
  if (submitAnnotationsButton) submitAnnotationsButton.addEventListener("click", submitAnnotationBatch);
  if (batchConfirmUpdateButton) batchConfirmUpdateButton.addEventListener("click", confirmChange);
  if (batchDismissButton) {
    batchDismissButton.addEventListener("click", () => {
      if (batchInterpretationPanel) batchInterpretationPanel.hidden = true;
      if (nodeCommentText && state.selectedTargetId) nodeCommentText.focus();
    });
  }
  if (logicContextCommentShortcut) {
    logicContextCommentShortcut.addEventListener("click", () => {
      if (nodeCommentText) nodeCommentText.focus();
    });
  }
  fillHandoffDraftButton.addEventListener("click", fillLogicChangeFromHandoff);
  submitChangeButton.addEventListener("click", submitChange);
  confirmChangeButton.addEventListener("click", confirmChange);
  clearChangeButton.addEventListener("click", () => {
    changeText.value = "";
    markActiveChangeCancelled("用户清空修改意见。");
    clearInterpretation();
    selectAnnotationTarget("", "", "");
  });
  cancelChangeButton.addEventListener("click", () => {
    markActiveChangeCancelled("用户取消本次模型理解。");
    clearInterpretation();
  });
  Object.values(circuitInputs).forEach((element) => {
    if (!element) return;
    const eventName = element.type === "checkbox" ? "change" : "input";
    element.addEventListener(eventName, () => {
      state.activeCircuitPreset = "";
      if (circuitPresetStatus) circuitPresetStatus.textContent = "手动输入";
      if (circuitPresetSelect) circuitPresetSelect.value = "";
      circuitPresetButtons.forEach((button) => button.setAttribute("aria-pressed", "false"));
      scheduleCircuitEvaluation();
      syncDrawerFromCircuitInputs();
    });
  });
  if (circuitPresetSelect) {
    circuitPresetSelect.addEventListener("change", () => applyCircuitPreset(circuitPresetSelect.value));
  }
  circuitPresetButtons.forEach((button) => {
    button.addEventListener("click", () => applyCircuitPreset(button.dataset.circuitPreset));
  });
  workbenchTabButtons.forEach((button) => {
    button.addEventListener("click", () => activateWorkbenchTab(button.dataset.workbenchTab || "notes"));
  });
  provenanceFilterButtons.forEach((button) => {
    button.addEventListener("click", () => setCircuitProvenanceFilter(button.dataset.provenanceFilter || "all"));
  });
  if (canvas) {
    canvas.addEventListener("click", (event) => {
      const target = event.target;
      if (target && typeof target.closest === "function" && target.closest(".logic-circuit-node, .logic-circuit-wire, .logic-node")) {
        return;
      }
      selectAnnotationTarget("", "", "", event);
    });
  }
  back.addEventListener("click", () => {
    window.location.href = "/requirements-intake";
  });
  document.addEventListener("keydown", (event) => {
    const commandKey = event.metaKey || event.ctrlKey;
    if (commandKey && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (commandPalette && !commandPalette.hidden) closeCommandPalette();
      else openCommandPalette();
    } else if (event.key === "Escape") {
      closeCommandPalette();
    }
  });
  window.addEventListener("hashchange", hydrateDrawerFromHash);
  setActiveAuxPanel("none");
  boot();
})();

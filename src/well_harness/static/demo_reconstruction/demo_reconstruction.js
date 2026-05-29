(function () {
  "use strict";

  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const REPLAY_ENDPOINT = "/api/requirements-intake/deepseek-live-demo-replay";
  const DOCX_SENTENCE_CIRCUIT_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;
  const PRESETS = ["默认前向", "着陆展开", "最大反推", "收起回杆", "抑制阻塞"];
  const STATUS_OUTPUTS = ["SW1", "SW2", "TLS", "VDT90", "L1-L4", "THR_LOCK"];
  const OUTPUT_PATH_TARGETS = [
    {id: "tls115", label: "TLS 115VAC"},
    {id: "etrac_540v", label: "ETRAC 540VDC"},
    {id: "eec_deploy", label: "EEC Deploy"},
    {id: "pdu_motor", label: "PDU Motor"},
    {id: "thr_lock", label: "THR_LOCK"},
  ];
  const LOGIC_EQUATION_RECORDS = [
    {
      id: "logic1",
      anchor: "P035-S01",
      title: "L1 · TLS 解锁供电",
      expression: "RA < 6 ft AND SW1 AND NOT inhibited",
      output: "TLS115 -> TLS_Unlocked",
      focusKind: "wire",
      focusId: "wire_logic1_tls115",
      sourceNodes: ["radio_altitude_ft", "sw1", "reverser_inhibited"],
      outputNodes: ["tls115", "tls_unlocked"],
    },
    {
      id: "logic2",
      anchor: "P035-S02",
      title: "L2 · ETRAC 540VDC",
      expression: "SW2 AND ground AND engine_running AND eec_enable AND NOT inhibited",
      output: "ETRAC 540VDC",
      focusKind: "wire",
      focusId: "wire_logic2_etrac",
      sourceNodes: ["sw2", "aircraft_on_ground", "engine_running", "eec_enable", "reverser_inhibited"],
      outputNodes: ["etrac_540v"],
    },
    {
      id: "logic3",
      anchor: "P035-S03",
      title: "L3 · EEC / PLS / PDU",
      expression: "TLS_Unlocked AND TRA <= -11.74 deg AND N1K AND ground AND NOT inhibited",
      output: "EEC Deploy + PLS power + PDU motor",
      focusKind: "wire",
      focusId: "wire_logic3_pdu",
      sourceNodes: ["tls_unlocked", "n1k", "aircraft_on_ground", "reverser_inhibited"],
      outputNodes: ["eec_deploy", "pls_power", "pdu_motor"],
    },
    {
      id: "logic4",
      anchor: "P035-S05",
      title: "L4 · THR_LOCK 释放",
      expression: "VDT90 AND L3 AND reverse range AND ground AND engine_running",
      output: "THR_LOCK release",
      focusKind: "wire",
      focusId: "wire_logic4_thr_lock",
      sourceNodes: ["vdt90", "logic3", "aircraft_on_ground", "engine_running"],
      outputNodes: ["thr_lock"],
    },
  ];
  const OPERATOR_RUNWAY_RECORDS = [
    {
      id: "runway-l1-unlock",
      order: "01",
      anchor: "P035-S01",
      presetId: "landing-deploy",
      presetLabel: "着陆展开",
      title: "低空解锁",
      focusKind: "wire",
      focusId: "wire_logic1_tls115",
      readback: "RA < 6 ft 与 SW1 进入 L1，TLS 115VAC 通电。",
      output: "TLS -> ON",
    },
    {
      id: "runway-l2-power",
      order: "02",
      anchor: "P035-S02",
      presetId: "landing-deploy",
      presetLabel: "着陆展开",
      title: "ETRAC 供电",
      focusKind: "wire",
      focusId: "wire_logic2_etrac",
      readback: "SW2、地面、发动机运行和 EEC 使能进入 L2。",
      output: "ETRAC -> ON",
    },
    {
      id: "runway-l3-deploy",
      order: "03",
      anchor: "P035-S03",
      presetId: "max-reverse",
      presetLabel: "最大反推",
      title: "展开指令",
      focusKind: "wire",
      focusId: "wire_logic3_pdu",
      readback: "TLS 解锁、TRA 阈值和 N1K 限制进入 L3。",
      output: "EEC / PDU -> ON",
    },
    {
      id: "runway-vdt90",
      order: "04",
      anchor: "P035-S04",
      presetId: "max-reverse",
      presetLabel: "最大反推",
      title: "90% 展开反馈",
      focusKind: "wire",
      focusId: "wire_pdu_vdt90",
      readback: "PDU 电机带动滑动罩，形成 VDT90 反馈。",
      output: "VDT90 -> TRUE",
    },
    {
      id: "runway-l4-thr-lock",
      order: "05",
      anchor: "P035-S05",
      presetId: "max-reverse",
      presetLabel: "最大反推",
      title: "反推锁释放",
      focusKind: "wire",
      focusId: "wire_logic4_thr_lock",
      readback: "VDT90 与 L3 进入 L4，THR_LOCK 释放。",
      output: "THR_LOCK -> RELEASED",
    },
    {
      id: "runway-inhibit",
      order: "06",
      anchor: "P035-S01",
      presetId: "inhibit-block",
      presetLabel: "抑制位阻塞",
      title: "安全阻塞分支",
      focusKind: "node",
      focusId: "reverser_inhibited",
      readback: "抑制位为真时，展开链路保持阻塞。",
      output: "THR_LOCK -> BLOCKED",
    },
  ];
  const TRACE_HIGHLIGHT_STYLE_ID = "demo-reconstruction-trace-highlight-style";

  const $ = (id) => document.getElementById(id);
  const sourceState = $("demo-reconstruction-source-state");
  const fidelity = $("demo-reconstruction-fidelity");
  const nodeCount = $("demo-reconstruction-node-count");
  const wireCount = $("demo-reconstruction-wire-count");
  const presetCount = $("demo-reconstruction-preset-count");
  const statusCount = $("demo-reconstruction-status-count");
  const nodeCell = $("demo-reconstruction-node-cell");
  const wireCell = $("demo-reconstruction-wire-cell");
  const presetCell = $("demo-reconstruction-preset-cell");
  const statusCell = $("demo-reconstruction-status-cell");
  const reviewIndexReadiness = $("demo-reconstruction-review-index-readiness");
  const reviewIndexStep = $("demo-reconstruction-review-index-step");
  const reviewIndexObject = $("demo-reconstruction-review-index-object");
  const reviewIndexOutput = $("demo-reconstruction-review-index-output");
  const reviewIndexList = $("demo-reconstruction-review-index-list");
  const nodeList = $("demo-reconstruction-node-list");
  const wireList = $("demo-reconstruction-wire-list");
  const docxSourcePath = $("demo-reconstruction-docx-source-path");
  const docxCoverage = $("demo-reconstruction-docx-coverage");
  const docxCircuitContract = $("demo-reconstruction-docx-circuit-contract");
  const docxNodeCoverage = $("demo-reconstruction-docx-node-coverage");
  const docxWireCoverage = $("demo-reconstruction-docx-wire-coverage");
  const docxEntryCount = $("demo-reconstruction-docx-entry-count");
  const docxSequenceCount = $("demo-reconstruction-docx-sequence-count");
  const sourceEntryList = $("demo-reconstruction-source-entry-list");
  const sequenceStepList = $("demo-reconstruction-sequence-step-list");
  const requirementLedgerSummary = $("demo-reconstruction-requirement-ledger-summary");
  const requirementLedgerSearch = $("demo-reconstruction-requirement-ledger-search");
  const requirementLedgerFilters = $("demo-reconstruction-requirement-ledger-filters");
  const requirementLedgerStatus = $("demo-reconstruction-requirement-ledger-status");
  const requirementLedgerList = $("demo-reconstruction-requirement-ledger-list");
  const traceContract = $("demo-reconstruction-trace-contract");
  const traceCardList = $("demo-reconstruction-trace-card-list");
  const selectedAnchor = $("demo-reconstruction-selected-anchor");
  const selectedTitle = $("demo-reconstruction-selected-title");
  const selectedText = $("demo-reconstruction-selected-text");
  const selectedNodes = $("demo-reconstruction-selected-nodes");
  const selectedWires = $("demo-reconstruction-selected-wires");
  const selectedFolded = $("demo-reconstruction-selected-folded");
  const embeddedHighlightStatus = $("demo-reconstruction-embedded-highlight-status");
  const logicEquationSummary = $("demo-reconstruction-logic-equation-summary");
  const logicEquationList = $("demo-reconstruction-logic-equation-list");
  const coverageContract = $("demo-reconstruction-coverage-contract");
  const coverageSearch = $("demo-reconstruction-coverage-search");
  const coverageFilterStatus = $("demo-reconstruction-coverage-filter-status");
  const coverageNodeList = $("demo-reconstruction-coverage-node-list");
  const coverageWireList = $("demo-reconstruction-coverage-wire-list");
  const topologySummary = $("demo-reconstruction-topology-summary");
  const topologyReadback = $("demo-reconstruction-topology-readback");
  const topologySearch = $("demo-reconstruction-topology-search");
  const topologyStepFilter = $("demo-reconstruction-topology-step-filter");
  const topologyFilterStatus = $("demo-reconstruction-topology-filter-status");
  const topologyList = $("demo-reconstruction-topology-list");
  const outputPathSummary = $("demo-reconstruction-output-path-summary");
  const outputPathTargets = $("demo-reconstruction-output-path-targets");
  const outputPathReadback = $("demo-reconstruction-output-path-readback");
  const outputPathList = $("demo-reconstruction-output-path-list");
  const outputMaturitySummary = $("demo-reconstruction-output-maturity-summary");
  const outputMaturityGrid = $("demo-reconstruction-output-maturity-grid");
  const reviewAnchor = $("demo-reconstruction-review-anchor");
  const reviewObject = $("demo-reconstruction-review-object");
  const reviewSync = $("demo-reconstruction-review-sync");
  const reviewLink = $("demo-reconstruction-review-link");
  const stepPlayback = $("demo-reconstruction-step-playback");
  const playbackStepList = $("demo-reconstruction-playback-step-list");
  const playbackActiveStep = $("demo-reconstruction-playback-active-step");
  const playbackNodeCount = $("demo-reconstruction-playback-node-count");
  const playbackWireCount = $("demo-reconstruction-playback-wire-count");
  const assemblySummary = $("demo-reconstruction-assembly-summary");
  const assemblyList = $("demo-reconstruction-assembly-list");
  const assemblyFinal = $("demo-reconstruction-assembly-final");
  const ladderSummary = $("demo-reconstruction-ladder-summary");
  const ladderList = $("demo-reconstruction-ladder-list");
  const provenanceObject = $("demo-reconstruction-provenance-object");
  const provenanceSourceCount = $("demo-reconstruction-provenance-source-count");
  const provenanceStepCount = $("demo-reconstruction-provenance-step-count");
  const provenanceSourceList = $("demo-reconstruction-provenance-source-list");
  const provenanceStepList = $("demo-reconstruction-provenance-step-list");
  const neighborhoodObject = $("demo-reconstruction-neighborhood-object");
  const neighborhoodInCount = $("demo-reconstruction-neighborhood-in-count");
  const neighborhoodOutCount = $("demo-reconstruction-neighborhood-out-count");
  const neighborhoodIncoming = $("demo-reconstruction-neighborhood-incoming");
  const neighborhoodOutgoing = $("demo-reconstruction-neighborhood-outgoing");
  const neighborhoodAdjacent = $("demo-reconstruction-neighborhood-adjacent");
  const reviewPacketReadiness = $("demo-reconstruction-review-packet-readiness");
  const reviewPacketSource = $("demo-reconstruction-review-packet-source");
  const reviewPacketContract = $("demo-reconstruction-review-packet-contract");
  const reviewPacketStep = $("demo-reconstruction-review-packet-step");
  const reviewPacketObject = $("demo-reconstruction-review-packet-object");
  const reviewPacketGates = $("demo-reconstruction-review-packet-gates");
  const reviewPacketDashboardSummary = $("demo-reconstruction-review-packet-dashboard-summary");
  const reviewPacketDashboardMetrics = $("demo-reconstruction-review-packet-dashboard-metrics");
  const reviewPacketDashboardChecklist = $("demo-reconstruction-review-packet-dashboard-checklist");
  const custodySummary = $("demo-reconstruction-custody-summary");
  const custodyActive = $("demo-reconstruction-custody-active");
  const custodyOutput = $("demo-reconstruction-custody-output");
  const custodyList = $("demo-reconstruction-custody-list");
  const outputMirrorStatus = $("demo-reconstruction-output-mirror-status");
  const outputMirrorLogic = $("demo-reconstruction-output-mirror-logic");
  const outputMirrorThr = $("demo-reconstruction-output-mirror-thr");
  const outputMirrorSummary = $("demo-reconstruction-output-mirror-summary");
  const outputMirrorTls = $("demo-reconstruction-output-mirror-tls");
  const outputMirrorEtrac = $("demo-reconstruction-output-mirror-etrac");
  const outputMirrorEec = $("demo-reconstruction-output-mirror-eec");
  const outputMirrorThrOutput = $("demo-reconstruction-output-mirror-thr-output");
  const scenarioLedgerStatus = $("demo-reconstruction-scenario-ledger-status");
  const scenarioLedgerList = $("demo-reconstruction-scenario-ledger-list");
  const scenarioTruthStatus = $("demo-reconstruction-scenario-truth-status");
  const scenarioTruthBody = $("demo-reconstruction-scenario-truth-body");
  const operatorRunwayStatus = $("demo-reconstruction-operator-runway-status");
  const operatorRunwayReadback = $("demo-reconstruction-operator-runway-readback");
  const operatorRunwayList = $("demo-reconstruction-operator-runway-list");
  const consoleFrame = $("demo-reconstruction-console-frame");
  let latestDocxPayload = null;
  let sourceEntries = [];
  let traceSteps = [];
  let currentTraceStep = null;
  let selectedTraceIndex = -1;
  let currentCircuitFocus = {kind: "", id: ""};
  let requirementLedgerFilter = "all";
  let requirementLedgerSelectedKey = "";
  let activePlaybackIndex = -1;
  let topologyStepFilterAnchor = "all";
  let outputPathTargetId = "thr_lock";
  let applyingReviewHashState = false;
  let wireEndpointMap = new Map();
  let nodeLabelMap = new Map();
  let nodeKindMap = new Map();
  let outputMirrorObserver = null;
  let scenarioLedgerRecords = new Map();
  let activeOperatorRunwayId = "";

  function readJson(value) {
    try {
      return value ? JSON.parse(value) : null;
    } catch (error) {
      return null;
    }
  }

  function circuitViewFromDrawing(drawing) {
    if (!drawing || typeof drawing !== "object") return null;
    const circuit = drawing.circuit_view;
    if (circuit && circuit.kind === "ai-fantui-l1-l4-circuit-view") return circuit;
    return null;
  }

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function itemLabel(item, fallback) {
    if (!item || typeof item !== "object") return fallback;
    return item.label || item.id || fallback;
  }

  function wireLabel(wire, index) {
    if (!wire || typeof wire !== "object") return `wire_${index}`;
    const source = wire.source || "source";
    const target = wire.target || "target";
    return `${wire.id || `wire_${index}`}：${source} -> ${target}`;
  }

  function renderList(list, items, formatter) {
    if (!list) return;
    list.innerHTML = "";
    items.forEach((item, index) => {
      const li = document.createElement("li");
      li.textContent = formatter(item, index + 1);
      list.appendChild(li);
    });
  }

  function passFail(actual, expected, unit) {
    return actual === expected ? "通过" : `需复核：${actual}/${expected} ${unit}`;
  }

  function updateReviewIndexStatus() {
    if (!reviewIndexReadiness) return;
    const selectedStep = currentTraceStep && currentTraceStep.anchor
      ? `${currentTraceStep.anchor} · ${currentTraceStep.title || "工作过程片段"}`
      : "等待选择";
    const focusedObject = currentCircuitFocus.kind && currentCircuitFocus.id
      ? reviewObjectLabel(currentCircuitFocus.kind, currentCircuitFocus.id)
      : "等待聚焦";
    const status = outputMirrorStatus && outputMirrorStatus.textContent
      ? outputMirrorStatus.textContent.trim()
      : "";
    const thr = outputMirrorThrOutput && outputMirrorThrOutput.textContent
      ? outputMirrorThrOutput.textContent.trim()
      : "";
    const outputText = [status, thr].filter((value) => value && !value.startsWith("等待") && value !== "--").join(" · ");
    setText(reviewIndexReadiness, reviewPacketReadiness && reviewPacketReadiness.textContent
      ? reviewPacketReadiness.textContent.trim()
      : "等待交付读回");
    setText(reviewIndexStep, selectedStep);
    setText(reviewIndexObject, focusedObject);
    setText(reviewIndexOutput, outputText || "等待输出");
  }

  function setReviewIndexTarget(targetId) {
    if (!reviewIndexList) return;
    reviewIndexList.querySelectorAll("[data-review-index-target]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexTarget === targetId ? "true" : "false");
    });
  }

  function installReviewIndexNavigation() {
    if (!reviewIndexList) return;
    reviewIndexList.querySelectorAll("[data-review-index-target]").forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.dataset.reviewIndexTarget || "";
        const target = targetId ? document.getElementById(targetId) : null;
        setReviewIndexTarget(targetId);
        if (target && typeof target.scrollIntoView === "function") {
          target.scrollIntoView({behavior: "smooth", block: "start"});
        }
      });
    });
  }

  function appendChipGroup(container, label, values, className, highlightKind) {
    if (!container || !Array.isArray(values) || values.length === 0) return;
    const group = document.createElement("div");
    group.className = "demo-reconstruction-chip-group";
    const caption = document.createElement("span");
    caption.className = "demo-reconstruction-chip-caption";
    caption.textContent = label;
    group.appendChild(caption);
    values.forEach((value) => {
      const chip = document.createElement(highlightKind ? "button" : "span");
      chip.className = `demo-reconstruction-chip ${className}`;
      chip.textContent = value;
      if (highlightKind) {
        chip.type = "button";
        chip.dataset.sourceFocusKind = highlightKind;
        chip.dataset.sourceFocusId = value;
        chip.addEventListener("click", (event) => {
          event.stopPropagation();
          applyEmbeddedTraceFocus(highlightKind, value);
        });
      }
      group.appendChild(chip);
    });
    container.appendChild(group);
  }

  function renderInlineChips(container, values, className, emptyText, highlightKind) {
    if (!container) return;
    container.innerHTML = "";
    if (!Array.isArray(values) || values.length === 0) {
      const chip = document.createElement("span");
      chip.className = `demo-reconstruction-chip ${className}`;
      chip.textContent = emptyText;
      container.appendChild(chip);
      return;
    }
    values.forEach((value) => {
      const chip = document.createElement(highlightKind ? "button" : "span");
      chip.className = `demo-reconstruction-chip ${className}`;
      chip.textContent = value;
      if (highlightKind) {
        chip.type = "button";
        chip.dataset.traceFocusKind = highlightKind;
        chip.dataset.traceFocusId = value;
        chip.addEventListener("click", () => applyEmbeddedTraceFocus(highlightKind, value));
      }
      container.appendChild(chip);
    });
  }

  function ensureEmbeddedTraceStyle(frameDocument) {
    if (!frameDocument || frameDocument.getElementById(TRACE_HIGHLIGHT_STYLE_ID)) return;
    const style = frameDocument.createElement("style");
    style.id = TRACE_HIGHLIGHT_STYLE_ID;
    style.textContent = `
      #fan-chain-svg [data-docx-trace-selected="true"] rect {
        stroke: #2563eb;
        stroke-width: 3;
      }
      #fan-chain-svg [data-docx-trace-selected="true"] text,
      #fan-chain-svg [data-docx-trace-selected="true"] .logic-id,
      #fan-chain-svg [data-docx-trace-selected="true"] .gate-label {
        fill: #1d4ed8;
        font-weight: 700;
      }
      #fan-chain-svg .chain-wire[data-docx-trace-selected="true"] {
        stroke: #2563eb;
        stroke-width: 4;
        opacity: 1;
      }
    `;
    frameDocument.head.appendChild(style);
  }

  function updateNodeMetadataFromNodes(nodes) {
    nodeLabelMap = new Map();
    nodeKindMap = new Map();
    if (!Array.isArray(nodes)) return;
    nodes.forEach((node) => {
      if (!node || !node.id) return;
      nodeLabelMap.set(node.id, itemLabel(node, node.id));
      if (node.node_kind) nodeKindMap.set(node.id, node.node_kind);
    });
  }

  function hasRenderedNode(nodeId) {
    return Boolean(nodeId && nodeLabelMap.has(nodeId));
  }

  function updateWireEndpointMapFromWires(wires) {
    wireEndpointMap = new Map();
    if (!Array.isArray(wires)) return;
    wires.forEach((wire) => {
      if (!wire || !wire.id || !hasRenderedNode(wire.source) || !hasRenderedNode(wire.target)) return;
      wireEndpointMap.set(wire.id, [wire.source, wire.target]);
    });
  }

  function ladderMilestoneLabel(nodeId) {
    return nodeLabelMap.get(nodeId) || nodeId;
  }

  function isLadderMilestoneNode(nodeId) {
    const kind = nodeKindMap.get(nodeId);
    return kind ? kind !== "input" : true;
  }

  function wireEndpointsForId(wireId) {
    return wireEndpointMap.get(wireId) || [];
  }

  function topologyWireIds() {
    const contract = latestDocxPayload && latestDocxPayload.circuit_contract
      ? latestDocxPayload.circuit_contract
      : {};
    if (Array.isArray(contract.wire_ids) && contract.wire_ids.length) {
      return contract.wire_ids.filter((wireId) => wireEndpointMap.has(wireId));
    }
    return Array.from(wireEndpointMap.keys());
  }

  function firstTraceStepForWire(wireId) {
    return traceSteps.find((step) => Array.isArray(step && step.wire_ids) && step.wire_ids.includes(wireId)) || null;
  }

  function sourceAnchorsForWire(wireId, endpoints) {
    const endpointIds = Array.isArray(endpoints) ? endpoints : [];
    const anchors = [];
    sourceEntries.forEach((entry) => {
      if (!entry || !entry.anchor || anchors.includes(entry.anchor)) return;
      const hasWire = Array.isArray(entry.wire_ids) && entry.wire_ids.includes(wireId);
      const hasEndpoint = endpointIds.length
        && Array.isArray(entry.node_ids)
        && endpointIds.some((endpointId) => entry.node_ids.includes(endpointId));
      if (hasWire || hasEndpoint) anchors.push(entry.anchor);
    });
    return anchors.slice(0, 4);
  }

  function topologyStepForAnchor(anchor) {
    if (!anchor || anchor === "all") return null;
    return traceSteps.find((step) => step && step.anchor === anchor) || null;
  }

  function setTopologyStepFilterState(anchor) {
    document.querySelectorAll("[data-topology-step-filter]").forEach((button) => {
      const selected = button.dataset.topologyStepFilter === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function topologyWireSearchText(wireId, endpoints, step, anchors) {
    return [
      wireId,
      ...(Array.isArray(endpoints) ? endpoints : []),
      ...(Array.isArray(endpoints) ? endpoints.map(nodeDisplayLabel) : []),
      step && step.anchor ? step.anchor : "",
      step && step.title ? step.title : "",
      ...(Array.isArray(anchors) ? anchors : []),
    ].join(" ").toLowerCase();
  }

  function updateTopologyFilter() {
    if (!topologyList) return;
    const query = (topologySearch && topologySearch.value ? topologySearch.value : "").trim().toLowerCase();
    const selectedStep = topologyStepForAnchor(topologyStepFilterAnchor);
    const rows = Array.from(topologyList.querySelectorAll("[data-topology-wire]"));
    let visibleCount = 0;
    rows.forEach((row) => {
      const wireId = row.dataset.topologyWire || "";
      const endpoints = wireEndpointsForId(wireId);
      const firstStep = firstTraceStepForWire(wireId);
      const anchors = sourceAnchorsForWire(wireId, endpoints);
      const matchesStep = !selectedStep
        || (Array.isArray(selectedStep.wire_ids) && selectedStep.wire_ids.includes(wireId));
      const matchesQuery = !query || topologyWireSearchText(wireId, endpoints, firstStep, anchors).includes(query);
      const visible = matchesStep && matchesQuery;
      row.hidden = !visible;
      if (visible) visibleCount += 1;
    });
    const stepLabel = selectedStep ? selectedStep.anchor : "全部步骤";
    const queryLabel = query ? ` · ${query}` : "";
    setText(topologyFilterStatus, `${visibleCount}/${rows.length} 连线 · ${stepLabel}${queryLabel}`);
    setTopologyStepFilterState(topologyStepFilterAnchor);
  }

  function renderTopologyStepFilter(steps) {
    if (!topologyStepFilter) return;
    topologyStepFilter.innerHTML = "";
    const allButton = document.createElement("button");
    allButton.type = "button";
    allButton.dataset.topologyStepFilter = "all";
    allButton.setAttribute("aria-pressed", topologyStepFilterAnchor === "all" ? "true" : "false");
    allButton.textContent = "全部";
    allButton.addEventListener("click", () => {
      topologyStepFilterAnchor = "all";
      updateTopologyFilter();
      writeReviewHashState();
    });
    topologyStepFilter.appendChild(allButton);
    (Array.isArray(steps) ? steps : []).forEach((step) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.topologyStepFilter = step.anchor || "";
      button.setAttribute("aria-pressed", topologyStepFilterAnchor === step.anchor ? "true" : "false");
      button.textContent = `${step.anchor || "步骤"} · ${(step.wire_ids || []).length} 线`;
      button.addEventListener("click", () => {
        topologyStepFilterAnchor = step.anchor || "all";
        setSelectedTrace(step, {writeHash: false});
        updateTopologyFilter();
        writeReviewHashState();
      });
      topologyStepFilter.appendChild(button);
    });
  }

  function outputPathTargetLabel(targetId) {
    const target = OUTPUT_PATH_TARGETS.find((item) => item.id === targetId);
    return target ? target.label : nodeDisplayLabel(targetId);
  }

  function upstreamPathForTarget(targetId) {
    const wireIds = topologyWireIds();
    const seenWires = new Set();
    const seenNodes = new Set();
    const orderedWires = [];
    function visit(nodeId) {
      if (!nodeId || seenNodes.has(nodeId)) return;
      seenNodes.add(nodeId);
      wireIds.forEach((wireId) => {
        const endpoints = wireEndpointsForId(wireId);
        if (endpoints.length < 2 || endpoints[1] !== nodeId || seenWires.has(wireId)) return;
        visit(endpoints[0]);
        seenWires.add(wireId);
        orderedWires.push(wireId);
      });
    }
    visit(targetId);
    return {
      node_ids: Array.from(seenNodes),
      wire_ids: orderedWires,
    };
  }

  function setOutputPathTargetState(targetId) {
    document.querySelectorAll("[data-output-path-target]").forEach((button) => {
      const selected = button.dataset.outputPathTarget === targetId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function setOutputPathWireState(wireId) {
    document.querySelectorAll("[data-output-path-wire-row]").forEach((button) => {
      const selected = button.dataset.outputPathWireRow === wireId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function renderOutputPathTargets() {
    if (!outputPathTargets) return;
    outputPathTargets.innerHTML = "";
    OUTPUT_PATH_TARGETS.forEach((target) => {
      const path = upstreamPathForTarget(target.id);
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.outputPathTarget = target.id;
      button.setAttribute("aria-pressed", outputPathTargetId === target.id ? "true" : "false");
      button.textContent = `${target.label} · ${path.wire_ids.length} 线`;
      button.addEventListener("click", () => {
        outputPathTargetId = target.id;
        renderOutputPathLane();
      });
      outputPathTargets.appendChild(button);
    });
  }

  function renderOutputPathLane() {
    if (!outputPathList) return;
    renderOutputPathTargets();
    const path = upstreamPathForTarget(outputPathTargetId);
    const label = outputPathTargetLabel(outputPathTargetId);
    outputPathList.innerHTML = "";
    if (!path.wire_ids.length || wireEndpointMap.size === 0) {
      const empty = document.createElement("li");
      empty.textContent = "输出路径暂无数据";
      outputPathList.appendChild(empty);
      setText(outputPathSummary, `${label} · 0/${EXPECTED_WIRE_COUNT} 连线`);
      setText(outputPathReadback, "等待输出路径");
      setOutputPathTargetState(outputPathTargetId);
      setOutputPathWireState("");
      return;
    }
    path.wire_ids.forEach((wireId, index) => {
      const endpoints = wireEndpointsForId(wireId);
      const step = firstTraceStepForWire(wireId);
      const anchors = sourceAnchorsForWire(wireId, endpoints);
      const source = endpoints[0] ? nodeDisplayLabel(endpoints[0]) : "source";
      const target = endpoints[1] ? nodeDisplayLabel(endpoints[1]) : "target";
      const li = document.createElement("li");
      li.className = "demo-reconstruction-output-path-item";
      li.dataset.outputPathWire = wireId;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-output-path-row";
      button.dataset.outputPathWireRow = wireId;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        applyEmbeddedTraceFocus("wire", wireId);
        setOutputPathWireState(wireId);
      });

      const title = document.createElement("strong");
      title.textContent = `${String(index + 1).padStart(2, "0")} · ${wireId}`;
      const pathText = document.createElement("span");
      pathText.textContent = `${source} -> ${target}`;
      const meta = document.createElement("small");
      meta.textContent = `${step ? step.anchor : "待匹配"} · DOCX ${anchors.join(" / ") || "待匹配"}`;
      button.append(title, pathText, meta);
      li.appendChild(button);
      outputPathList.appendChild(li);
    });
    setText(
      outputPathSummary,
      `${label} · ${path.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${path.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`,
    );
    setText(outputPathReadback, `${label} 上游路径 · ${path.wire_ids.length} 条连线可逐条聚焦`);
    setOutputPathTargetState(outputPathTargetId);
    setOutputPathWireState(currentCircuitFocus.kind === "wire" ? currentCircuitFocus.id : "");
  }

  function setOutputMaturityCellState(stepAnchor, targetId) {
    document.querySelectorAll("[data-output-maturity-step][data-output-maturity-target]").forEach((button) => {
      const selected = button.dataset.outputMaturityStep === stepAnchor
        && button.dataset.outputMaturityTarget === targetId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function outputMaturityTargetForFocus(kind, id) {
    if (kind !== "node" || !id) return "";
    const target = OUTPUT_PATH_TARGETS.find((item) => item.id === id);
    return target ? target.id : "";
  }

  function renderOutputMaturityMatrix(steps) {
    if (!outputMaturityGrid) return;
    const items = Array.isArray(steps) ? steps : [];
    outputMaturityGrid.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("span");
      empty.textContent = "输出成熟度暂无数据";
      outputMaturityGrid.appendChild(empty);
      setText(outputMaturitySummary, "0/5 步 · 等待输出");
      return;
    }

    const corner = document.createElement("strong");
    corner.className = "demo-reconstruction-output-maturity-corner";
    corner.textContent = "步骤";
    outputMaturityGrid.appendChild(corner);
    OUTPUT_PATH_TARGETS.forEach((target) => {
      const header = document.createElement("strong");
      header.className = "demo-reconstruction-output-maturity-target";
      header.textContent = target.label;
      outputMaturityGrid.appendChild(header);
    });

    items.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const activeNodes = new Set(contract.node_ids);
      const rowLabel = document.createElement("button");
      rowLabel.type = "button";
      rowLabel.className = "demo-reconstruction-output-maturity-step";
      rowLabel.dataset.outputMaturityStepLabel = step.anchor || "";
      rowLabel.textContent = `${step.anchor || "步骤"} · ${contract.node_ids.length}/${EXPECTED_NODE_COUNT}`;
      rowLabel.addEventListener("click", () => setSelectedTrace(step));
      outputMaturityGrid.appendChild(rowLabel);

      OUTPUT_PATH_TARGETS.forEach((target) => {
        const active = activeNodes.has(target.id);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "demo-reconstruction-output-maturity-cell";
        button.dataset.outputMaturityStep = step.anchor || "";
        button.dataset.outputMaturityTarget = target.id;
        button.dataset.outputMaturityActive = active ? "true" : "false";
        button.setAttribute("aria-pressed", "false");
        button.textContent = active ? "已接入" : "待接入";
        button.addEventListener("click", () => {
          outputPathTargetId = target.id;
          setSelectedTrace(step, {writeHash: false});
          renderOutputPathLane();
          if (active) applyEmbeddedTraceFocus("node", target.id, {keepOutputMaturitySelection: true});
          setOutputMaturityCellState(step.anchor || "", target.id);
        });
        outputMaturityGrid.appendChild(button);
      });
    });

    const finalContract = cumulativeTraceContract(items.length - 1);
    const finalNodes = new Set(finalContract.node_ids);
    const finalReadyCount = OUTPUT_PATH_TARGETS.filter((target) => finalNodes.has(target.id)).length;
    setText(
      outputMaturitySummary,
      `${items.length}/5 步 · ${OUTPUT_PATH_TARGETS.length} 输出 · 最终 ${finalReadyCount}/${OUTPUT_PATH_TARGETS.length} 接入`,
    );
  }

  function traceStepByAnchor(anchor) {
    return traceSteps.find((step) => step.anchor === anchor) || null;
  }

  function logicEquationState(record) {
    const step = traceStepByAnchor(record.anchor);
    const stepIndex = step ? traceSteps.indexOf(step) : -1;
    const contract = stepIndex >= 0 ? cumulativeTraceContract(stepIndex) : {node_ids: [], wire_ids: []};
    const contractNodes = new Set(contract.node_ids || []);
    const contractWires = new Set(contract.wire_ids || []);
    const nodeReady = [...(record.sourceNodes || []), ...(record.outputNodes || [])].every((nodeId) => contractNodes.has(nodeId));
    const wireReady = record.focusKind !== "wire" || contractWires.has(record.focusId);
    return {
      step,
      contract,
      ready: Boolean(step && nodeReady && wireReady),
    };
  }

  function setLogicEquationRowState(recordId) {
    document.querySelectorAll("[data-logic-equation-row]").forEach((button) => {
      const selected = button.dataset.logicEquationRow === recordId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function activateLogicEquationRecord(record) {
    const state = logicEquationState(record);
    if (state.step) setSelectedTrace(state.step, {writeHash: false});
    applyEmbeddedTraceFocus(record.focusKind, record.focusId);
    setLogicEquationRowState(record.id);
  }

  function renderLogicEquationBoard() {
    if (!logicEquationList) return;
    logicEquationList.innerHTML = "";
    const states = LOGIC_EQUATION_RECORDS.map((record) => ({
      record,
      state: logicEquationState(record),
    }));
    const readyCount = states.filter((item) => item.state.ready).length;
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    setText(
      logicEquationSummary,
      `${readyCount}/${LOGIC_EQUATION_RECORDS.length} 方程 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );

    if (!states.length) {
      const empty = document.createElement("li");
      empty.textContent = "L1-L4 方程暂无数据";
      logicEquationList.appendChild(empty);
      return;
    }

    states.forEach(({record, state}) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-logic-equation-item";
      li.dataset.logicEquation = record.id;
      li.dataset.logicEquationAnchor = record.anchor;
      li.dataset.logicEquationStatus = state.ready ? "pass" : "wait";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-logic-equation-row";
      button.dataset.logicEquationRow = record.id;
      button.dataset.logicEquationFocusKind = record.focusKind;
      button.dataset.logicEquationFocusId = record.focusId;
      button.setAttribute("aria-pressed", currentCircuitFocus.id === record.focusId ? "true" : "false");
      button.addEventListener("click", () => activateLogicEquationRecord(record));

      const head = document.createElement("div");
      head.className = "demo-reconstruction-logic-equation-row-head";
      const title = document.createElement("strong");
      title.textContent = record.title;
      const anchor = document.createElement("span");
      anchor.textContent = record.anchor;
      head.append(title, anchor);

      const expression = document.createElement("code");
      expression.textContent = record.expression;

      const output = document.createElement("p");
      output.textContent = `${record.output} · ${record.focusId}`;

      const chips = document.createElement("div");
      chips.className = "demo-reconstruction-logic-equation-chips";
      [
        `${state.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`,
        `${state.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
        state.ready ? "可追踪" : "等待映射",
      ].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        chips.appendChild(chip);
      });

      button.append(head, expression, output, chips);
      li.appendChild(button);
      logicEquationList.appendChild(li);
    });
  }

  function setTopologyRowState(wireId) {
    document.querySelectorAll("[data-topology-wire-row]").forEach((button) => {
      const selected = button.dataset.topologyWireRow === wireId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateTopologyReadback(wireId) {
    if (!topologyReadback) return;
    if (!wireId) {
      setText(topologyReadback, "等待连线聚焦");
      setTopologyRowState("");
      return;
    }
    const endpoints = wireEndpointsForId(wireId);
    const step = firstTraceStepForWire(wireId);
    const anchors = sourceAnchorsForWire(wireId, endpoints);
    const source = endpoints[0] ? nodeDisplayLabel(endpoints[0]) : "source";
    const target = endpoints[1] ? nodeDisplayLabel(endpoints[1]) : "target";
    setText(
      topologyReadback,
      `${wireId} · ${source} -> ${target} · 首次 ${step ? step.anchor : "待匹配"} · DOCX ${anchors.join(" / ") || "待匹配"}`,
    );
    setTopologyRowState(wireId);
  }

  function resetTopologyReadback() {
    setText(topologyReadback, `${topologyWireIds().length}/${EXPECTED_WIRE_COUNT} 条 demo.html 连线可聚焦`);
    setTopologyRowState("");
  }

  function renderTopologyMatrix() {
    if (!topologyList) return;
    const wireIds = topologyWireIds();
    topologyList.innerHTML = "";
    if (!wireIds.length || wireEndpointMap.size === 0) {
      const empty = document.createElement("li");
      empty.textContent = "完整电路拓扑暂无数据";
      topologyList.appendChild(empty);
      setText(topologySummary, `${wireEndpointMap.size}/${EXPECTED_WIRE_COUNT} 连线 · 等待端点`);
      setText(topologyFilterStatus, `0/${EXPECTED_WIRE_COUNT} 连线`);
      renderOutputPathLane();
      updateTopologyReadback("");
      return;
    }

    wireIds.forEach((wireId, index) => {
      const endpoints = wireEndpointsForId(wireId);
      const step = firstTraceStepForWire(wireId);
      const anchors = sourceAnchorsForWire(wireId, endpoints);
      const source = endpoints[0] ? nodeDisplayLabel(endpoints[0]) : "source";
      const target = endpoints[1] ? nodeDisplayLabel(endpoints[1]) : "target";
      const li = document.createElement("li");
      li.className = "demo-reconstruction-topology-item";
      li.dataset.topologyWire = wireId;
      li.dataset.topologyStep = step ? step.anchor : "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-topology-row";
      button.dataset.topologyWireRow = wireId;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        applyEmbeddedTraceFocus("wire", wireId);
        updateTopologyReadback(wireId);
      });

      const head = document.createElement("div");
      head.className = "demo-reconstruction-topology-row-head";
      const title = document.createElement("strong");
      title.textContent = `${String(index + 1).padStart(2, "0")} · ${wireId}`;
      const path = document.createElement("span");
      path.textContent = `${source} -> ${target}`;
      head.append(title, path);

      const meta = document.createElement("div");
      meta.className = "demo-reconstruction-topology-meta";
      [
        `首次 ${step ? step.anchor : "待匹配"}`,
        `DOCX ${anchors.join(" / ") || "待匹配"}`,
      ].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        meta.appendChild(chip);
      });

      button.append(head, meta);
      li.appendChild(button);
      topologyList.appendChild(li);
    });

    setText(
      topologySummary,
      `${wireIds.length}/${EXPECTED_WIRE_COUNT} 连线 · ${traceSteps.length}/5 步 · ${wireEndpointMap.size}/${EXPECTED_WIRE_COUNT} 端点映射`,
    );
    if (currentCircuitFocus.kind === "wire" && currentCircuitFocus.id) {
      updateTopologyReadback(currentCircuitFocus.id);
    } else {
      setText(topologyReadback, `${wireIds.length}/${EXPECTED_WIRE_COUNT} 条 demo.html 连线可聚焦`);
      setTopologyRowState("");
    }
    updateTopologyFilter();
    renderOutputPathLane();
  }

  function refreshEmbeddedReviewFromCircuit() {
    renderTopologyMatrix();
    if (traceSteps.length) renderAssemblyMap(traceSteps);
    if (traceSteps.length) renderCircuitCompletionLadder(traceSteps);
    if (traceSteps.length) renderCustodyMatrix(traceSteps);
    if (currentCircuitFocus.kind && currentCircuitFocus.id) {
      renderObjectProvenance(currentCircuitFocus.kind, currentCircuitFocus.id);
      applyEmbeddedTraceFocus(currentCircuitFocus.kind, currentCircuitFocus.id);
    } else if (activePlaybackIndex >= 0) {
      applyEmbeddedPlaybackHighlight(cumulativeTraceContract(activePlaybackIndex));
    } else if (currentTraceStep) {
      applyEmbeddedTraceHighlight(currentTraceStep);
    }
  }

  function embeddedWireSelector(wireId) {
    const endpoints = wireEndpointsForId(wireId);
    if (!endpoints.length) return "";
    return `#fan-chain-svg .chain-wire[data-src="${endpoints[0]}"][data-dst="${endpoints[1]}"]`;
  }

  function reviewObjectLabel(kind, id) {
    if (!id) return "等待聚焦";
    if (kind === "wire") return `连线 · ${id}`;
    if (kind === "node") return `节点 · ${id}`;
    return id;
  }

  function updateKeyboardReviewStatus(details = {}) {
    const step = currentTraceStep || {};
    const anchorText = step.anchor
      ? `${step.anchor} · ${step.title || "工作过程片段"}`
      : "等待选择";
    const objectText = details.objectId
      ? reviewObjectLabel(details.objectKind, details.objectId)
      : (details.objectText || reviewObjectLabel(currentCircuitFocus.kind, currentCircuitFocus.id));
    setText(reviewAnchor, anchorText);
    setText(reviewObject, objectText);
    setText(reviewSync, details.syncText || (embeddedHighlightStatus ? embeddedHighlightStatus.textContent : "等待同步"));
    updateReviewLink();
    updateReviewPacketFromState();
  }

  function readReviewHashState() {
    const params = new URLSearchParams((window.location.hash || "").replace(/^#/, ""));
    const focus = params.get("focus") || "";
    const focusParts = focus.split(":");
    return {
      step: params.get("step") || "",
      focusKind: focusParts.length === 2 ? focusParts[0] : "",
      focusId: focusParts.length === 2 ? focusParts[1] : "",
      query: params.get("q") || "",
      topologyStep: params.get("topology") || "",
      topologyQuery: params.get("tq") || "",
    };
  }

  function reviewHashForState() {
    const params = new URLSearchParams();
    if (currentTraceStep && currentTraceStep.anchor) params.set("step", currentTraceStep.anchor);
    if (currentCircuitFocus.kind && currentCircuitFocus.id) {
      params.set("focus", `${currentCircuitFocus.kind}:${currentCircuitFocus.id}`);
    }
    const query = coverageSearch && coverageSearch.value ? coverageSearch.value.trim() : "";
    if (query) params.set("q", query);
    if (topologyStepFilterAnchor && topologyStepFilterAnchor !== "all") {
      params.set("topology", topologyStepFilterAnchor);
    }
    const topologyQuery = topologySearch && topologySearch.value ? topologySearch.value.trim() : "";
    if (topologyQuery) params.set("tq", topologyQuery);
    return params.toString();
  }

  function updateReviewLink() {
    if (!reviewLink) return;
    const hash = reviewHashForState();
    const suffix = hash ? `#${hash}` : "";
    reviewLink.href = `${window.location.pathname}${window.location.search}${suffix}`;
  }

  function cumulativeTraceContract(index) {
    const safeIndex = Math.max(0, Math.min(traceSteps.length - 1, index));
    const nodes = [];
    const wires = [];
    const seenNodes = new Set();
    const seenWires = new Set();
    traceSteps.slice(0, safeIndex + 1).forEach((step) => {
      (step.node_ids || []).forEach((nodeId) => {
        if (!seenNodes.has(nodeId)) {
          seenNodes.add(nodeId);
          nodes.push(nodeId);
        }
      });
      (step.wire_ids || []).forEach((wireId) => {
        if (!seenWires.has(wireId)) {
          seenWires.add(wireId);
          wires.push(wireId);
        }
      });
    });
    const step = traceSteps[safeIndex] || {};
    return {
      anchor: step.anchor || `S${safeIndex + 1}`,
      title: step.title || "工作过程片段",
      node_ids: nodes,
      wire_ids: wires,
      step_count: safeIndex + 1,
    };
  }

  function setPlaybackButtonState(anchor) {
    document.querySelectorAll("[data-playback-step]").forEach((button) => {
      const selected = button.dataset.playbackStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function setAssemblyButtonState(anchor) {
    document.querySelectorAll("[data-assembly-step-button]").forEach((button) => {
      const selected = button.dataset.assemblyStepButton === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateStepPlaybackSummary(contract) {
    if (!contract) return;
    setText(playbackActiveStep, contract.anchor);
    setText(playbackNodeCount, `${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`);
    setText(playbackWireCount, `${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`);
    setPlaybackButtonState(contract.anchor);
    setAssemblyButtonState(contract.anchor);
  }

  function syncStepPlaybackToTrace(step) {
    if (!step || !traceSteps.length) return;
    const index = traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    if (index < 0) return;
    updateStepPlaybackSummary(cumulativeTraceContract(index));
  }

  function applyEmbeddedPlaybackHighlight(contract) {
    if (!consoleFrame || !contract) return { nodeCount: 0, wireCount: 0, ready: false };
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.querySelector("#fan-chain-svg")) {
      setText(embeddedHighlightStatus, "等待电路图同步");
      updateKeyboardReviewStatus({
        objectText: `累计构建 · ${contract.anchor}`,
        syncText: "等待电路图同步",
      });
      return { nodeCount: 0, wireCount: 0, ready: false };
    }
    ensureEmbeddedTraceStyle(frameDocument);
    frameDocument
      .querySelectorAll("#fan-chain-svg [data-docx-trace-selected]")
      .forEach((element) => element.removeAttribute("data-docx-trace-selected"));

    let nodeCount = 0;
    let wireCount = 0;
    contract.node_ids.forEach((nodeId) => {
      frameDocument
        .querySelectorAll(`#fan-chain-svg [data-node="${nodeId}"]`)
        .forEach((element) => {
          element.setAttribute("data-docx-trace-selected", "true");
          nodeCount += 1;
        });
    });
    contract.wire_ids.forEach((wireId) => {
      const selector = embeddedWireSelector(wireId);
      if (!selector) return;
      frameDocument.querySelectorAll(selector).forEach((element) => {
        element.setAttribute("data-docx-trace-selected", "true");
        wireCount += 1;
      });
    });
    const status = `构建轨道已同步：${contract.anchor} · ${nodeCount}/${EXPECTED_NODE_COUNT} 节点 · ${wireCount}/${EXPECTED_WIRE_COUNT} 连线`;
    setText(embeddedHighlightStatus, status);
    updateKeyboardReviewStatus({
      objectText: `累计构建 · ${contract.anchor} · ${nodeCount}/${EXPECTED_NODE_COUNT} 节点 · ${wireCount}/${EXPECTED_WIRE_COUNT} 连线`,
      syncText: status,
    });
    return { nodeCount, wireCount, ready: true };
  }

  function applyStepPlayback(index) {
    if (!traceSteps.length) return;
    const safeIndex = Math.max(0, Math.min(traceSteps.length - 1, index));
    const step = traceSteps[safeIndex];
    activePlaybackIndex = safeIndex;
    setSelectedTrace(step, {writeHash: false, keepPlaybackMode: true});
    const contract = cumulativeTraceContract(safeIndex);
    updateStepPlaybackSummary(contract);
    applyEmbeddedPlaybackHighlight(contract);
    writeReviewHashState();
  }

  function renderStepPlaybackRail(steps) {
    if (!playbackStepList) return;
    playbackStepList.innerHTML = "";
    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-playback-button";
      button.dataset.playbackStep = step.anchor;
      button.setAttribute("aria-pressed", "false");

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor;
      const count = document.createElement("span");
      count.textContent = `${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      const title = document.createElement("small");
      title.textContent = step.title || "工作过程片段";
      button.append(anchor, count, title);
      button.addEventListener("click", () => applyStepPlayback(index));
      playbackStepList.appendChild(button);
    });
    if (steps.length) updateStepPlaybackSummary(cumulativeTraceContract(selectedTraceIndex >= 0 ? selectedTraceIndex : 0));
    if (stepPlayback) stepPlayback.dataset.stepPlaybackReady = steps.length ? "true" : "false";
  }

  function ladderMilestonesForStep(step) {
    const nodeIds = Array.isArray(step && step.node_ids) ? step.node_ids : [];
    return nodeIds.filter(isLadderMilestoneNode).map(ladderMilestoneLabel);
  }

  function assemblyOutputLabelForStep(step, contract) {
    const nodeIds = Array.isArray(step && step.node_ids) ? step.node_ids : [];
    const milestones = ladderMilestonesForStep(step);
    if (
      contract.node_ids.length === EXPECTED_NODE_COUNT
      && contract.wire_ids.length === EXPECTED_WIRE_COUNT
    ) {
      return "完整 demo 电路闭合 · THR_LOCK 输出可读";
    }
    if (
      nodeIds.some((value) => ["eec_deploy", "pls_power", "pdu_motor"].includes(value))
      || milestones.some((value) => value.includes("PDU") || value.includes("PLS") || value.includes("EEC"))
    ) {
      return "展开执行链路进入 EEC / PLS / PDU";
    }
    if (
      nodeIds.includes("etrac_540v")
      || milestones.some((value) => value.includes("ETRAC"))
    ) {
      return "540VDC / ETRAC 供电链路进入电路";
    }
    if (
      nodeIds.includes("tls115")
      || nodeIds.includes("tls_unlocked")
      || milestones.some((value) => value.includes("TLS"))
    ) {
      return "TLS 解锁前级进入电路";
    }
    return "前置输入链路进入电路";
  }

  function appendAssemblyChips(container, label, values, kind = "") {
    const group = document.createElement("div");
    group.className = "demo-reconstruction-assembly-group";
    const title = document.createElement("strong");
    title.textContent = label;
    const chips = document.createElement("div");
    chips.className = "demo-reconstruction-assembly-chips";
    const list = Array.isArray(values) ? values : [];
    if (!list.length) {
      const empty = document.createElement("span");
      empty.className = "demo-reconstruction-assembly-chip";
      empty.textContent = "无新增";
      chips.appendChild(empty);
    } else {
      list.forEach((value) => {
        const chip = kind ? document.createElement("button") : document.createElement("span");
        chip.className = "demo-reconstruction-assembly-chip";
        chip.textContent = value;
        if (kind) {
          chip.type = "button";
          chip.dataset.assemblyFocusKind = kind;
          chip.dataset.assemblyFocusId = value;
          chip.addEventListener("click", (event) => {
            event.stopPropagation();
            applyEmbeddedTraceFocus(kind, value);
          });
        }
        chips.appendChild(chip);
      });
    }
    group.append(title, chips);
    container.appendChild(group);
  }

  function renderAssemblyMap(steps) {
    if (!assemblyList) return;
    assemblyList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "逐句装配暂无数据";
      assemblyList.appendChild(empty);
      setText(assemblySummary, "0/5 句 · 0/20 节点 · 0/23 连线");
      setText(assemblyFinal, "等待完整电路");
      return;
    }

    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const previous = index > 0 ? cumulativeTraceContract(index - 1) : {node_ids: [], wire_ids: []};
      const previousNodes = new Set(previous.node_ids);
      const previousWires = new Set(previous.wire_ids);
      const newNodes = contract.node_ids.filter((nodeId) => !previousNodes.has(nodeId));
      const newWires = contract.wire_ids.filter((wireId) => !previousWires.has(wireId));
      const milestones = ladderMilestonesForStep(step);

      const li = document.createElement("li");
      li.className = "demo-reconstruction-assembly-item";
      li.dataset.assemblyStep = step.anchor || "";
      li.dataset.assemblyComplete = contract.node_ids.length === EXPECTED_NODE_COUNT
        && contract.wire_ids.length === EXPECTED_WIRE_COUNT
        ? "true"
        : "false";

      const card = document.createElement("div");
      card.className = "demo-reconstruction-assembly-card";

      const header = document.createElement("div");
      header.className = "demo-reconstruction-assembly-row-head";
      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const action = document.createElement("button");
      action.type = "button";
      action.className = "demo-reconstruction-assembly-step-action";
      action.dataset.assemblyStepButton = step.anchor || "";
      action.setAttribute("aria-pressed", "false");
      action.textContent = "回放";
      action.addEventListener("click", () => applyStepPlayback(index));
      header.append(anchor, title, action);

      const metrics = document.createElement("div");
      metrics.className = "demo-reconstruction-assembly-metrics";
      [
        `累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`,
        `累计 ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
        `新增 ${newNodes.length} 节点`,
        `新增 ${newWires.length} 连线`,
      ].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        metrics.appendChild(chip);
      });

      const output = document.createElement("p");
      output.textContent = assemblyOutputLabelForStep(step, contract);

      const groups = document.createElement("div");
      groups.className = "demo-reconstruction-assembly-groups";
      appendAssemblyChips(groups, "新增节点", newNodes, "node");
      appendAssemblyChips(groups, "新增连线", newWires, "wire");
      appendAssemblyChips(groups, "关键输出", milestones);

      card.append(header, metrics, output, groups);
      li.appendChild(card);
      assemblyList.appendChild(li);
    });

    const finalContract = cumulativeTraceContract(steps.length - 1);
    const finalStep = steps[steps.length - 1] || {};
    setText(
      assemblySummary,
      `${steps.length}/5 句 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    setText(
      assemblyFinal,
      `${finalStep.anchor || "P035-S05"} · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${assemblyOutputLabelForStep(finalStep, finalContract)}`,
    );
    setAssemblyButtonState(currentTraceStep && currentTraceStep.anchor ? currentTraceStep.anchor : steps[0].anchor);
  }

  function renderCircuitCompletionLadder(steps) {
    if (!ladderList) return;
    ladderList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "完成阶梯暂无数据";
      ladderList.appendChild(empty);
      setText(ladderSummary, "0/5 步 · 0/20 节点 · 0/23 连线");
      return;
    }
    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const li = document.createElement("li");
      li.className = "demo-reconstruction-ladder-item";
      li.dataset.ladderStep = step.anchor || "";
      li.dataset.ladderComplete = contract.node_ids.length === EXPECTED_NODE_COUNT
        && contract.wire_ids.length === EXPECTED_WIRE_COUNT
        ? "true"
        : "false";

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("p");
      title.textContent = step.title || "工作过程片段";

      const metrics = document.createElement("div");
      metrics.className = "demo-reconstruction-ladder-metrics";
      [`${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`, `${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        metrics.appendChild(chip);
      });

      const milestones = document.createElement("div");
      milestones.className = "demo-reconstruction-ladder-milestones";
      ladderMilestonesForStep(step).forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        milestones.appendChild(chip);
      });

      li.append(anchor, title, metrics, milestones);
      ladderList.appendChild(li);
    });
    const finalContract = cumulativeTraceContract(steps.length - 1);
    setText(
      ladderSummary,
      `${steps.length}/5 步 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
  }

  function setCustodyButtonState(anchor) {
    document.querySelectorAll("[data-custody-step-button]").forEach((button) => {
      const selected = button.dataset.custodyStepButton === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateCustodyOutputReadback() {
    if (!custodyOutput) return;
    const status = outputMirrorStatus && outputMirrorStatus.textContent
      ? outputMirrorStatus.textContent.trim()
      : "";
    const thr = outputMirrorThrOutput && outputMirrorThrOutput.textContent
      ? outputMirrorThrOutput.textContent.trim()
      : "";
    const logic = outputMirrorLogic && outputMirrorLogic.textContent
      ? outputMirrorLogic.textContent.trim()
      : "";
    const parts = [status, thr, logic].filter((value) => value && !value.startsWith("等待") && value !== "--");
    setText(custodyOutput, parts.length ? parts.join(" · ") : "等待输出镜像");
  }

  function updateCustodyActiveReadback() {
    if (!custodyActive) return;
    if (!currentTraceStep || !currentTraceStep.anchor) {
      setText(custodyActive, "等待选择");
      updateCustodyOutputReadback();
      return;
    }
    const index = activePlaybackIndex >= 0 ? activePlaybackIndex : selectedTraceIndex;
    const contract = traceSteps.length && index >= 0
      ? cumulativeTraceContract(index)
      : {
          node_ids: currentTraceStep.node_ids || [],
          wire_ids: currentTraceStep.wire_ids || [],
        };
    setText(
      custodyActive,
      `${currentTraceStep.anchor} · ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    updateCustodyOutputReadback();
  }

  function renderCustodyMatrix(steps) {
    if (!custodyList) return;
    custodyList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "交付链路暂无数据";
      custodyList.appendChild(empty);
      setText(custodySummary, "0/5 步 · 0/20 节点 · 0/23 连线");
      updateCustodyActiveReadback();
      return;
    }

    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const li = document.createElement("li");
      li.className = "demo-reconstruction-custody-item";
      li.dataset.custodyStep = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-custody-button";
      button.dataset.custodyStepButton = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyStepPlayback(index));

      const header = document.createElement("div");
      header.className = "demo-reconstruction-custody-row-head";
      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      header.append(anchor, title);

      const source = document.createElement("p");
      source.textContent = step.source_text || "";

      const metrics = document.createElement("div");
      metrics.className = "demo-reconstruction-custody-metrics";
      [`${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`, `${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        metrics.appendChild(chip);
      });
      const milestoneValues = ladderMilestonesForStep(step);
      if (milestoneValues.length) {
        milestoneValues.forEach((value) => {
          const chip = document.createElement("span");
          chip.dataset.custodyMilestone = "true";
          chip.textContent = value;
          metrics.appendChild(chip);
        });
      }

      button.append(header, source, metrics);
      li.appendChild(button);
      custodyList.appendChild(li);
    });

    const finalContract = cumulativeTraceContract(steps.length - 1);
    setText(
      custodySummary,
      `${steps.length}/5 步 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    setCustodyButtonState(currentTraceStep && currentTraceStep.anchor ? currentTraceStep.anchor : steps[0].anchor);
    updateCustodyActiveReadback();
  }

  function renderReviewPacketGates(gates) {
    if (!reviewPacketGates) return;
    reviewPacketGates.innerHTML = "";
    gates.forEach((gate) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-review-packet-gate";
      li.dataset.reviewPacketGate = gate.id;
      li.dataset.packetGateStatus = gate.pass ? "pass" : "wait";
      const title = document.createElement("strong");
      title.textContent = gate.label;
      const detail = document.createElement("span");
      detail.textContent = gate.detail;
      li.append(title, detail);
      reviewPacketGates.appendChild(li);
    });
  }

  function finalOutputReadinessCount(finalContract) {
    const finalNodes = new Set(Array.isArray(finalContract && finalContract.node_ids) ? finalContract.node_ids : []);
    return OUTPUT_PATH_TARGETS.filter((target) => finalNodes.has(target.id)).length;
  }

  function requirementLedgerStats() {
    const items = requirementLedgerItems();
    return {
      total: items.length,
      mapped: items.filter((item) => item.status === "mapped").length,
      context: items.filter((item) => item.status === "context").length,
      p035: items.filter((item) => item.status === "p035").length,
    };
  }

  function renderReviewPacketDashboard(gates, context) {
    if (!reviewPacketDashboardSummary && !reviewPacketDashboardMetrics && !reviewPacketDashboardChecklist) return;
    const ledger = requirementLedgerStats();
    const gateCount = gates.length;
    const passGateCount = gates.filter((gate) => gate.pass).length;
    const outputReadyCount = finalOutputReadinessCount(context.finalContract);
    const expectedNodes = context.expectedNodes || EXPECTED_NODE_COUNT;
    const expectedWires = context.expectedWires || EXPECTED_WIRE_COUNT;
    const coveredNodes = context.coveredNodes || 0;
    const coveredWires = context.coveredWires || 0;
    const fullCircuitReady = coveredNodes === expectedNodes && coveredWires === expectedWires;
    const ledgerExpectedCount = context.sourceCount + context.stepCount;

    setText(
      reviewPacketDashboardSummary,
      `${passGateCount}/${gateCount} gate · ${ledger.total} 覆盖项 · ${outputReadyCount}/${OUTPUT_PATH_TARGETS.length} 输出`,
    );

    if (reviewPacketDashboardMetrics) {
      reviewPacketDashboardMetrics.innerHTML = "";
      [
        {
          id: "source",
          label: "来源覆盖",
          value: `${context.sourceCount} 源记录 · ${context.stepCount}/5 步`,
          pass: context.sourceCount >= 10 && context.stepCount === 5,
        },
        {
          id: "ledger",
          label: "覆盖账本",
          value: `${ledger.total} 条 · ${ledger.mapped} 已映射 · ${ledger.context} 上下文 · ${ledger.p035} P035`,
          pass: ledger.total === ledgerExpectedCount && ledger.mapped >= coveredNodes + coveredWires,
        },
        {
          id: "circuit",
          label: "完整电路",
          value: `${coveredNodes}/${expectedNodes} 节点 · ${coveredWires}/${expectedWires} 连线`,
          pass: fullCircuitReady,
        },
        {
          id: "outputs",
          label: "输出成熟度",
          value: `${outputReadyCount}/${OUTPUT_PATH_TARGETS.length} 输出已接入`,
          pass: outputReadyCount === OUTPUT_PATH_TARGETS.length,
        },
        {
          id: "focus",
          label: "当前审阅点",
          value: context.focusedObject,
          pass: Boolean(context.hasFocusedObject),
        },
      ].forEach((metric) => {
        const item = document.createElement("div");
        item.className = "demo-reconstruction-review-packet-dashboard-metric";
        item.dataset.reviewPacketDashboardMetric = metric.id;
        item.dataset.dashboardMetricStatus = metric.pass ? "pass" : "wait";
        const label = document.createElement("span");
        label.textContent = metric.label;
        const value = document.createElement("strong");
        value.textContent = metric.value;
        item.append(label, value);
        reviewPacketDashboardMetrics.appendChild(item);
      });
    }

    if (reviewPacketDashboardChecklist) {
      reviewPacketDashboardChecklist.innerHTML = "";
      gates.forEach((gate) => {
        const li = document.createElement("li");
        li.dataset.reviewPacketDashboardCheck = gate.id;
        li.dataset.dashboardCheckStatus = gate.pass ? "pass" : "wait";
        const label = document.createElement("strong");
        label.textContent = gate.label;
        const detail = document.createElement("span");
        detail.textContent = gate.detail;
        li.append(label, detail);
        reviewPacketDashboardChecklist.appendChild(li);
      });
    }
  }

  function frameText(frameDocument, selector, fallback) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    const value = element && element.textContent ? element.textContent.trim() : "";
    return value || fallback;
  }

  function activeScenarioFromFrame(frameDocument) {
    const button = frameDocument ? frameDocument.querySelector(".fan-preset-btn[aria-pressed='true']") : null;
    if (!button || !button.dataset.preset) return null;
    return {
      id: button.dataset.preset,
      label: button.textContent ? button.textContent.trim() : button.dataset.preset,
    };
  }

  function scenarioOutputSnapshot(frameDocument) {
    return {
      status: frameText(frameDocument, "#fan-status-badge", "等待"),
      logic: frameText(frameDocument, "#fan-hud-logic", "等待逻辑"),
      thr: frameText(frameDocument, "#fan-out-thr-value", "--"),
      tls: frameText(frameDocument, "#fan-out-tls115-value", "--"),
      etrac: frameText(frameDocument, "#fan-out-etrac-value", "--"),
      eec: frameText(frameDocument, "#fan-out-eec-value", "--"),
      summary: frameText(frameDocument, "#fan-status-summary", "等待摘要"),
    };
  }

  function applyScenarioPreset(presetId) {
    if (!consoleFrame || !presetId) return;
    const frameDocument = consoleFrame.contentDocument;
    const button = frameDocument
      ? frameDocument.querySelector(`.fan-preset-btn[data-preset="${presetId}"]`)
      : null;
    if (button && typeof button.click === "function") button.click();
  }

  function renderScenarioLedger(activeId) {
    if (!scenarioLedgerList) return;
    scenarioLedgerList.innerHTML = "";
    const records = Array.from(scenarioLedgerRecords.values());
    if (!records.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.className = "demo-reconstruction-scenario-row";
      empty.dataset.scenarioLedgerRow = "empty";
      empty.textContent = "等待 demo 预设同步";
      scenarioLedgerList.appendChild(empty);
      setText(scenarioLedgerStatus, "等待预设");
      renderScenarioTruthTable("");
      return;
    }
    let captured = 0;
    records.forEach((record) => {
      if (record.captured) captured += 1;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-scenario-row";
      button.dataset.scenarioLedgerRow = record.id;
      button.setAttribute("aria-pressed", record.id === activeId ? "true" : "false");
      button.addEventListener("click", () => applyScenarioPreset(record.id));

      const head = document.createElement("div");
      head.className = "demo-reconstruction-scenario-row-head";
      const label = document.createElement("strong");
      label.textContent = record.label || record.id;
      const status = document.createElement("span");
      status.textContent = record.captured ? record.status : "未记录";
      head.append(label, status);

      const detail = document.createElement("p");
      detail.textContent = record.captured ? `${record.logic} · THR_LOCK ${record.thr}` : "点击记录该场景输出";

      const values = document.createElement("div");
      values.className = "demo-reconstruction-scenario-values";
      [
        ["TLS", record.tls],
        ["ETRAC", record.etrac],
        ["EEC", record.eec],
        ["THR", record.thr],
      ].forEach(([labelText, value]) => {
        const chip = document.createElement("span");
        chip.textContent = `${labelText}:${record.captured ? value : "--"}`;
        values.appendChild(chip);
      });

      button.append(head, detail, values);
      scenarioLedgerList.appendChild(button);
    });
    setText(scenarioLedgerStatus, `${captured}/${records.length} 已记录`);
    renderScenarioTruthTable(activeId);
  }

  function scenarioTruthTokens(record) {
    if (!record.captured) return ["L1:--", "L2:--", "L3:--", "L4:--"];
    const parts = String(record.logic || "")
      .split("·")
      .map((part) => part.trim())
      .filter(Boolean);
    return parts.length ? parts : ["L1:--", "L2:--", "L3:--", "L4:--"];
  }

  function renderScenarioTruthTable(activeId) {
    if (!scenarioTruthBody) return;
    scenarioTruthBody.innerHTML = "";
    const records = Array.from(scenarioLedgerRecords.values());
    if (!records.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.className = "demo-reconstruction-scenario-truth-row";
      empty.dataset.scenarioTruthRow = "empty";
      empty.textContent = "等待 demo 预设同步";
      scenarioTruthBody.appendChild(empty);
      setText(scenarioTruthStatus, "等待逻辑");
      return;
    }

    let captured = 0;
    records.forEach((record) => {
      if (record.captured) captured += 1;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-scenario-truth-row";
      button.dataset.scenarioTruthRow = record.id;
      button.dataset.scenarioTruthCaptured = record.captured ? "true" : "false";
      button.setAttribute("aria-pressed", record.id === activeId ? "true" : "false");
      button.addEventListener("click", () => applyScenarioPreset(record.id));

      const head = document.createElement("div");
      head.className = "demo-reconstruction-scenario-truth-row-head";
      const label = document.createElement("strong");
      label.textContent = record.label || record.id;
      const status = document.createElement("span");
      status.textContent = record.captured ? `${record.status} · THR ${record.thr}` : "未记录";
      head.append(label, status);

      const logic = document.createElement("div");
      logic.className = "demo-reconstruction-scenario-truth-logic";
      scenarioTruthTokens(record).forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        logic.appendChild(chip);
      });

      const outputs = document.createElement("p");
      outputs.textContent = record.captured
        ? `TLS:${record.tls} · ETRAC:${record.etrac} · EEC:${record.eec} · THR:${record.thr}`
        : "点击场景后记录输出";

      button.append(head, logic, outputs);
      scenarioTruthBody.appendChild(button);
    });
    setText(scenarioTruthStatus, `${captured}/${records.length} 已记录`);
  }

  function operatorRunwayRecordById(recordId) {
    return OPERATOR_RUNWAY_RECORDS.find((record) => record.id === recordId) || null;
  }

  function operatorRunwayOutputSummary() {
    const status = outputMirrorStatus && outputMirrorStatus.textContent
      ? outputMirrorStatus.textContent.trim()
      : "等待同步";
    const thr = outputMirrorThrOutput && outputMirrorThrOutput.textContent
      ? outputMirrorThrOutput.textContent.trim()
      : "--";
    return `${status} · THR ${thr}`;
  }

  function refreshOperatorRunwayReadback(record) {
    if (!operatorRunwayReadback) return;
    if (!record) {
      setText(operatorRunwayReadback, "选择一段演示路径");
      return;
    }
    setText(
      operatorRunwayReadback,
      `${record.order} · ${record.title} · ${record.readback} · ${record.output} · ${operatorRunwayOutputSummary()}`,
    );
  }

  function setOperatorRunwayState(recordId) {
    const record = typeof recordId === "string" ? operatorRunwayRecordById(recordId) : recordId;
    activeOperatorRunwayId = record ? record.id : "";
    document.querySelectorAll("[data-operator-runway-row]").forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        button.dataset.operatorRunwayRow === activeOperatorRunwayId ? "true" : "false",
      );
    });
    if (record) {
      setText(operatorRunwayStatus, `${record.order}/${String(OPERATOR_RUNWAY_RECORDS.length).padStart(2, "0")} · ${record.presetLabel}`);
      refreshOperatorRunwayReadback(record);
    }
  }

  function activateOperatorRunwayRecord(record) {
    if (!record) return;
    applyScenarioPreset(record.presetId);
    const step = traceStepByAnchor(record.anchor);
    if (step) setSelectedTrace(step, {writeHash: false});
    if (record.focusKind && record.focusId) applyEmbeddedTraceFocus(record.focusKind, record.focusId);
    setOperatorRunwayState(record);
  }

  function renderOperatorRunway() {
    if (!operatorRunwayList) return;
    operatorRunwayList.innerHTML = "";
    const readyCount = OPERATOR_RUNWAY_RECORDS.filter((record) => traceStepByAnchor(record.anchor)).length;
    if (!OPERATOR_RUNWAY_RECORDS.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.className = "demo-reconstruction-operator-runway-row";
      empty.dataset.operatorRunwayRow = "empty";
      empty.textContent = "导览路径暂无数据";
      operatorRunwayList.appendChild(empty);
      setText(operatorRunwayStatus, "等待链路");
      refreshOperatorRunwayReadback(null);
      return;
    }

    OPERATOR_RUNWAY_RECORDS.forEach((record) => {
      const step = traceStepByAnchor(record.anchor);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-operator-runway-row";
      button.dataset.operatorRunwayRow = record.id;
      button.dataset.operatorRunwayPreset = record.presetId;
      button.dataset.operatorRunwayAnchor = record.anchor;
      button.dataset.operatorRunwayFocusKind = record.focusKind;
      button.dataset.operatorRunwayFocusId = record.focusId;
      button.dataset.operatorRunwayReady = step ? "true" : "false";
      button.setAttribute("aria-pressed", record.id === activeOperatorRunwayId ? "true" : "false");
      button.addEventListener("click", () => activateOperatorRunwayRecord(record));

      const head = document.createElement("div");
      head.className = "demo-reconstruction-operator-runway-row-head";
      const order = document.createElement("span");
      order.textContent = record.order;
      const title = document.createElement("strong");
      title.textContent = record.title;
      const preset = document.createElement("em");
      preset.textContent = record.presetLabel;
      head.append(order, title, preset);

      const detail = document.createElement("p");
      detail.textContent = record.readback;

      const chips = document.createElement("div");
      chips.className = "demo-reconstruction-operator-runway-chips";
      [
        record.anchor,
        record.output,
        step ? "可演示" : "等待映射",
      ].forEach((value) => {
        const chip = document.createElement("span");
        chip.textContent = value;
        chips.appendChild(chip);
      });

      button.append(head, detail, chips);
      operatorRunwayList.appendChild(button);
    });

    if (activeOperatorRunwayId) {
      setOperatorRunwayState(activeOperatorRunwayId);
    } else {
      setText(operatorRunwayStatus, `${readyCount}/${OPERATOR_RUNWAY_RECORDS.length} 可演示`);
      refreshOperatorRunwayReadback(null);
    }
  }

  function updateScenarioLedgerFromFrame() {
    if (!scenarioLedgerList || !consoleFrame) return;
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument) {
      renderScenarioLedger("");
      return;
    }
    frameDocument.querySelectorAll(".fan-preset-btn[data-preset]").forEach((button) => {
      const id = button.dataset.preset;
      if (!id || scenarioLedgerRecords.has(id)) return;
      scenarioLedgerRecords.set(id, {
        id,
        label: button.textContent ? button.textContent.trim() : id,
        captured: false,
      });
    });
    const active = activeScenarioFromFrame(frameDocument);
    if (active) {
      const snapshot = scenarioOutputSnapshot(frameDocument);
      scenarioLedgerRecords.set(active.id, {
        ...(scenarioLedgerRecords.get(active.id) || {}),
        ...active,
        ...snapshot,
        captured: true,
      });
    }
    renderScenarioLedger(active ? active.id : "");
  }

  function updateOutputMirrorFromFrame() {
    if (!outputMirrorStatus || !consoleFrame) return;
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.querySelector("#fan-status-badge")) {
      setText(outputMirrorStatus, "等待同步");
      updateCustodyOutputReadback();
      updateScenarioLedgerFromFrame();
      refreshOperatorRunwayReadback(operatorRunwayRecordById(activeOperatorRunwayId));
      updateReviewIndexStatus();
      return;
    }
    setText(outputMirrorStatus, frameText(frameDocument, "#fan-status-badge", "IDLE"));
    setText(outputMirrorLogic, frameText(frameDocument, "#fan-hud-logic", "等待 HUD"));
    setText(outputMirrorThr, frameText(frameDocument, "#fan-hud-thr-lock", "等待 THR_LOCK"));
    setText(outputMirrorSummary, frameText(frameDocument, "#fan-status-summary", "等待摘要"));
    setText(outputMirrorTls, frameText(frameDocument, "#fan-out-tls115-value", "--"));
    setText(outputMirrorEtrac, frameText(frameDocument, "#fan-out-etrac-value", "--"));
    setText(outputMirrorEec, frameText(frameDocument, "#fan-out-eec-value", "--"));
    setText(outputMirrorThrOutput, frameText(frameDocument, "#fan-out-thr-value", "--"));
    updateCustodyOutputReadback();
    updateScenarioLedgerFromFrame();
    refreshOperatorRunwayReadback(operatorRunwayRecordById(activeOperatorRunwayId));
    updateReviewIndexStatus();
  }

  function installOutputMirrorObserver() {
    if (!consoleFrame) return;
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.body) return;
    if (outputMirrorObserver) outputMirrorObserver.disconnect();
    outputMirrorObserver = new MutationObserver(updateOutputMirrorFromFrame);
    outputMirrorObserver.observe(frameDocument.body, {
      childList: true,
      characterData: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["data-state", "class"],
    });
    updateOutputMirrorFromFrame();
    updateScenarioLedgerFromFrame();
  }

  function updateReviewPacketFromState() {
    if (!reviewPacketReadiness) return;
    const payload = latestDocxPayload || {};
    const source = payload.source || {};
    const contract = payload.circuit_contract || {};
    const coverage = payload.coverage || {};
    const expectedNodes = contract.node_count || EXPECTED_NODE_COUNT;
    const expectedWires = contract.wire_count || EXPECTED_WIRE_COUNT;
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    const sourceCount = sourceEntries.length || coverage.source_entry_count || 0;
    const stepCount = traceSteps.length || coverage.sequence_step_count || 0;
    const coveredNodes = coverage.covered_node_count || finalContract.node_ids.length;
    const coveredWires = coverage.covered_wire_count || finalContract.wire_ids.length;
    const focusedObject = currentCircuitFocus.kind && currentCircuitFocus.id
      ? reviewObjectLabel(currentCircuitFocus.kind, currentCircuitFocus.id)
      : "等待聚焦";
    const selectedStep = currentTraceStep && currentTraceStep.anchor
      ? `${currentTraceStep.anchor} · ${currentTraceStep.title || "工作过程片段"}`
      : "等待选择";

    setText(reviewPacketSource, `${source.path || "原始 DOCX"} -> /demo-reconstruction`);
    setText(
      reviewPacketContract,
      `${coveredNodes}/${expectedNodes} 节点 · ${coveredWires}/${expectedWires} 连线`,
    );
    setText(reviewPacketStep, selectedStep);
    setText(reviewPacketObject, focusedObject);

    const gates = [
      {
        id: "docx-map",
        label: "DOCX 映射",
        pass: sourceCount >= 10 && stepCount === 5,
        detail: `${sourceCount} 条源记录 · ${stepCount}/5 步`,
      },
      {
        id: "complete-circuit",
        label: "完整电路",
        pass: coveredNodes === expectedNodes && coveredWires === expectedWires,
        detail: `${coveredNodes}/${expectedNodes} 节点 · ${coveredWires}/${expectedWires} 连线`,
      },
      {
        id: "cumulative-build",
        label: "逐句累计",
        pass: finalContract.node_ids.length === EXPECTED_NODE_COUNT && finalContract.wire_ids.length === EXPECTED_WIRE_COUNT,
        detail: `${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
      },
      {
        id: "object-review",
        label: "对象反查",
        pass: Boolean(currentCircuitFocus.kind && currentCircuitFocus.id),
        detail: focusedObject,
      },
      {
        id: "read-only-boundary",
        label: "只读边界",
        pass: payload.boundary ? payload.boundary.controller_truth_modified === false : true,
        detail: "控制逻辑未改动",
      },
    ];
    const passed = gates.filter((gate) => gate.pass).length;
    setText(reviewPacketReadiness, `${passed}/${gates.length} gate`);
    renderReviewPacketGates(gates);
    renderReviewPacketDashboard(gates, {
      sourceCount,
      stepCount,
      expectedNodes,
      expectedWires,
      coveredNodes,
      coveredWires,
      finalContract,
      focusedObject,
      hasFocusedObject: Boolean(currentCircuitFocus.kind && currentCircuitFocus.id),
    });
    updateReviewIndexStatus();
  }

  function objectProvenanceRecords(kind, id) {
    if (!kind || !id) return {sourceMatches: [], stepMatches: []};
    const key = kind === "wire" ? "wire_ids" : "node_ids";
    const endpointIds = kind === "wire" ? wireEndpointsForId(id) : [];
    const sourceMatches = sourceEntries.filter((entry) => {
      if (Array.isArray(entry[key]) && entry[key].includes(id)) return true;
      if (!endpointIds.length || !Array.isArray(entry.node_ids)) return false;
      return endpointIds.some((endpointId) => entry.node_ids.includes(endpointId));
    });
    const stepMatches = traceSteps.filter((step) => Array.isArray(step[key]) && step[key].includes(id));
    return {sourceMatches, stepMatches};
  }

  function nodeDisplayLabel(nodeId) {
    return nodeLabelMap.get(nodeId) || nodeId;
  }

  function wireDisplayLabel(wireId) {
    const endpoints = wireEndpointsForId(wireId);
    if (!endpoints.length) return wireId;
    return `${wireId} · ${nodeDisplayLabel(endpoints[0])} -> ${nodeDisplayLabel(endpoints[1])}`;
  }

  function wireRecordsForNode(nodeId, direction) {
    const records = [];
    wireEndpointMap.forEach((endpoints, wireId) => {
      const [source, target] = endpoints;
      const matches = direction === "incoming" ? target === nodeId : source === nodeId;
      if (!matches) return;
      const peer = direction === "incoming" ? source : target;
      records.push({
        kind: "wire",
        id: wireId,
        label: wireDisplayLabel(wireId),
        meta: direction === "incoming" ? `来自 ${nodeDisplayLabel(peer)}` : `指向 ${nodeDisplayLabel(peer)}`,
      });
    });
    return records;
  }

  function adjacentNodeRecordsForNode(nodeId) {
    const seen = new Set();
    const records = [];
    wireEndpointMap.forEach((endpoints) => {
      const [source, target] = endpoints;
      let peer = "";
      if (source === nodeId) peer = target;
      if (target === nodeId) peer = source;
      if (!peer || seen.has(peer)) return;
      seen.add(peer);
      records.push({
        kind: "node",
        id: peer,
        label: nodeDisplayLabel(peer),
        meta: peer,
      });
    });
    return records;
  }

  function siblingWireRecordsForWire(wireId) {
    const endpoints = wireEndpointsForId(wireId);
    if (!endpoints.length) return [];
    const [source, target] = endpoints;
    const records = [];
    wireEndpointMap.forEach((candidateEndpoints, candidateWireId) => {
      if (candidateWireId === wireId) return;
      const sharesEndpoint = candidateEndpoints.includes(source) || candidateEndpoints.includes(target);
      if (!sharesEndpoint) return;
      records.push({
        kind: "wire",
        id: candidateWireId,
        label: wireDisplayLabel(candidateWireId),
        meta: "共享端点",
      });
    });
    return records;
  }

  function signalNeighborhoodRecords(kind, id) {
    if (kind === "node") {
      const incoming = wireRecordsForNode(id, "incoming");
      const outgoing = wireRecordsForNode(id, "outgoing");
      return {
        incoming,
        outgoing,
        adjacent: adjacentNodeRecordsForNode(id),
      };
    }
    if (kind === "wire") {
      const endpoints = wireEndpointsForId(id);
      const source = endpoints[0] || "";
      const target = endpoints[1] || "";
      return {
        incoming: source
          ? [{kind: "node", id: source, label: nodeDisplayLabel(source), meta: "连线起点"}]
          : [],
        outgoing: target
          ? [{kind: "node", id: target, label: nodeDisplayLabel(target), meta: "连线终点"}]
          : [],
        adjacent: siblingWireRecordsForWire(id),
      };
    }
    return {incoming: [], outgoing: [], adjacent: []};
  }

  function renderNeighborhoodList(list, records, emptyText) {
    if (!list) return;
    list.innerHTML = "";
    if (!records.length) {
      const empty = document.createElement("li");
      empty.className = "demo-reconstruction-neighborhood-item";
      empty.textContent = emptyText;
      list.appendChild(empty);
      return;
    }
    records.forEach((record) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-neighborhood-item";
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.neighborhoodFocusKind = record.kind;
      button.dataset.neighborhoodFocusId = record.id;
      const label = document.createElement("strong");
      label.textContent = record.label;
      const meta = document.createElement("span");
      meta.textContent = record.meta || record.id;
      button.append(label, meta);
      button.addEventListener("click", () => applyEmbeddedTraceFocus(record.kind, record.id));
      li.appendChild(button);
      list.appendChild(li);
    });
  }

  function renderSignalNeighborhood(kind, id) {
    if (!neighborhoodObject) return;
    if (!kind || !id) {
      setText(neighborhoodObject, "等待对象");
      setText(neighborhoodInCount, "0 上游");
      setText(neighborhoodOutCount, "0 下游");
      renderNeighborhoodList(neighborhoodIncoming, [], "聚焦对象后显示上游。");
      renderNeighborhoodList(neighborhoodOutgoing, [], "聚焦对象后显示下游。");
      renderNeighborhoodList(neighborhoodAdjacent, [], "聚焦对象后显示相邻对象。");
      return;
    }
    const records = signalNeighborhoodRecords(kind, id);
    setText(neighborhoodObject, reviewObjectLabel(kind, id));
    setText(neighborhoodInCount, `${records.incoming.length} 上游`);
    setText(neighborhoodOutCount, `${records.outgoing.length} 下游`);
    renderNeighborhoodList(neighborhoodIncoming, records.incoming, "无上游对象。");
    renderNeighborhoodList(neighborhoodOutgoing, records.outgoing, "无下游对象。");
    renderNeighborhoodList(neighborhoodAdjacent, records.adjacent, "无相邻对象。");
  }

  function renderProvenanceList(list, records, emptyText, kind, id, labelKey) {
    if (!list) return;
    list.innerHTML = "";
    if (!records.length) {
      const empty = document.createElement("li");
      empty.className = "demo-reconstruction-provenance-item";
      empty.textContent = emptyText;
      list.appendChild(empty);
      return;
    }
    records.forEach((record) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-provenance-item";
      const anchor = document.createElement("strong");
      anchor.textContent = record.anchor || "source";
      const meta = document.createElement("span");
      meta.textContent = `${record[labelKey] || "来源"} · ${kind}:${id}`;
      const text = document.createElement("p");
      text.textContent = record.text || record.source_text || "";
      li.append(anchor, meta, text);
      list.appendChild(li);
    });
  }

  function renderObjectProvenance(kind, id) {
    if (!provenanceObject) return;
    if (!kind || !id) {
      setText(provenanceObject, "等待对象");
      setText(provenanceSourceCount, "0 条 DOCX");
      setText(provenanceStepCount, "0 步");
      renderProvenanceList(provenanceSourceList, [], "聚焦节点或连线后显示源 DOCX。", "", "", "role");
      renderProvenanceList(provenanceStepList, [], "聚焦节点或连线后显示 P035 步骤。", "", "", "title");
      renderSignalNeighborhood("", "");
      return;
    }
    const {sourceMatches, stepMatches} = objectProvenanceRecords(kind, id);
    setText(provenanceObject, reviewObjectLabel(kind, id));
    setText(provenanceSourceCount, `${sourceMatches.length} 条 DOCX`);
    setText(provenanceStepCount, `${stepMatches.length} 步`);
    renderProvenanceList(
      provenanceSourceList,
      sourceMatches,
      "该对象暂无直接 DOCX 段落命中。",
      kind,
      id,
      "role",
    );
    renderProvenanceList(
      provenanceStepList,
      stepMatches,
      "该对象暂无 P035 拆解步骤命中。",
      kind,
      id,
      "title",
    );
    updateReviewPacketFromState();
    renderSignalNeighborhood(kind, id);
  }

  function writeReviewHashState() {
    if (applyingReviewHashState) {
      updateReviewLink();
      return;
    }
    const hash = reviewHashForState();
    const nextUrl = `${window.location.pathname}${window.location.search}${hash ? `#${hash}` : ""}`;
    if (`${window.location.pathname}${window.location.search}${window.location.hash}` !== nextUrl) {
      window.history.replaceState(null, "", nextUrl);
    }
    updateReviewLink();
  }

  function applyReviewHashState() {
    const state = readReviewHashState();
    if (!state.step && !state.focusId && !state.query) {
      updateReviewLink();
      return false;
    }
    applyingReviewHashState = true;
    try {
      if (coverageSearch && coverageSearch.value !== state.query) {
        coverageSearch.value = state.query;
      }
      const nextTopologyStep = topologyStepForAnchor(state.topologyStep) ? state.topologyStep : "all";
      topologyStepFilterAnchor = nextTopologyStep;
      if (topologySearch && topologySearch.value !== state.topologyQuery) {
        topologySearch.value = state.topologyQuery;
      }
      updateCoverageFilter();
      updateTopologyFilter();
      if (state.step) {
        const step = traceSteps.find((item) => item && item.anchor === state.step);
        if (step) setSelectedTrace(step, {writeHash: false});
      }
      if (state.focusKind && state.focusId) {
        applyEmbeddedTraceFocus(state.focusKind, state.focusId);
      }
      const outputMaturityTarget = outputMaturityTargetForFocus(state.focusKind, state.focusId);
      if (state.step && outputMaturityTarget) {
        setOutputMaturityCellState(state.step, outputMaturityTarget);
      }
      updateReviewLink();
    } finally {
      applyingReviewHashState = false;
    }
    return true;
  }

  function setTraceCardTabStops(anchor) {
    document.querySelectorAll("[data-trace-card]").forEach((card) => {
      const selected = card.dataset.traceAnchor === anchor;
      card.tabIndex = selected ? 0 : -1;
      card.dataset.keyboardSelected = selected ? "true" : "false";
    });
  }

  function focusTraceCard(anchor) {
    if (!anchor) return;
    const card = document.querySelector(`[data-trace-card][data-trace-anchor="${anchor}"]`);
    if (card && typeof card.focus === "function") card.focus();
  }

  function selectTraceByIndex(index, shouldFocus, options = {}) {
    if (!traceSteps.length) return;
    const nextIndex = Math.max(0, Math.min(traceSteps.length - 1, index));
    setSelectedTrace(traceSteps[nextIndex], options);
    if (shouldFocus) focusTraceCard(traceSteps[nextIndex].anchor);
  }

  function handleTraceCardKeydown(event) {
    const keys = ["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft", "Home", "End"];
    if (!keys.includes(event.key)) return;
    event.preventDefault();
    const focusedAnchor = event.currentTarget ? event.currentTarget.dataset.traceAnchor : "";
    const focusedIndex = traceSteps.findIndex((step) => step && step.anchor === focusedAnchor);
    const currentIndex = focusedIndex >= 0 ? focusedIndex : (selectedTraceIndex >= 0 ? selectedTraceIndex : 0);
    if (event.key === "Home") {
      selectTraceByIndex(0, true);
    } else if (event.key === "End") {
      selectTraceByIndex(traceSteps.length - 1, true);
    } else if (event.key === "ArrowDown" || event.key === "ArrowRight") {
      selectTraceByIndex(currentIndex + 1, true);
    } else {
      selectTraceByIndex(currentIndex - 1, true);
    }
  }

  function visibleCoverageButtons() {
    return [
      ...Array.from(coverageNodeList ? coverageNodeList.querySelectorAll("button") : []),
      ...Array.from(coverageWireList ? coverageWireList.querySelectorAll("button") : []),
    ].filter((button) => !button.hidden);
  }

  function setCoverageButtonTabStops(kind, id) {
    const visibleButtons = visibleCoverageButtons();
    let target = visibleButtons.find(
      (button) => button.dataset.circuitCoverageKind === kind && button.dataset.circuitCoverageId === id,
    );
    if (!target) target = visibleButtons[0] || null;
    visibleButtons.forEach((button) => {
      const selected = button === target;
      button.tabIndex = selected ? 0 : -1;
      button.dataset.keyboardSelected = selected ? "true" : "false";
    });
    document
      .querySelectorAll("[data-circuit-coverage-kind]")
      .forEach((button) => {
        const isCurrent = button.dataset.circuitCoverageKind === kind && button.dataset.circuitCoverageId === id;
        button.setAttribute("aria-pressed", isCurrent ? "true" : "false");
      });
  }

  function markCircuitObjectFocus(kind, id) {
    currentCircuitFocus = {kind, id};
    setCoverageButtonTabStops(kind, id);
    const equation = LOGIC_EQUATION_RECORDS.find((record) => record.focusKind === kind && record.focusId === id);
    setLogicEquationRowState(equation ? equation.id : "");
    document
      .querySelectorAll("[data-trace-focus-kind], [data-source-focus-kind]")
      .forEach((button) => {
        const chipKind = button.dataset.traceFocusKind || button.dataset.sourceFocusKind || "";
        const chipId = button.dataset.traceFocusId || button.dataset.sourceFocusId || "";
        const isCurrent = chipKind === kind && chipId === id;
        button.setAttribute("aria-pressed", isCurrent ? "true" : "false");
        button.dataset.reviewObjectSelected = isCurrent ? "true" : "false";
      });
  }

  function clearCircuitObjectFocus() {
    currentCircuitFocus = {kind: "", id: ""};
    setCoverageButtonTabStops("", "");
    resetTopologyReadback();
    setOutputPathWireState("");
    setOutputMaturityCellState("", "");
    setLogicEquationRowState("");
    renderObjectProvenance("", "");
    document
      .querySelectorAll("[data-trace-focus-kind], [data-source-focus-kind]")
      .forEach((button) => {
        button.setAttribute("aria-pressed", "false");
        button.dataset.reviewObjectSelected = "false";
      });
  }

  function handleCoverageKeyboardNavigation(event) {
    const keys = ["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft", "Home", "End"];
    if (!keys.includes(event.key)) return;
    const buttons = visibleCoverageButtons();
    const currentIndex = buttons.indexOf(event.currentTarget);
    if (currentIndex < 0) return;
    event.preventDefault();
    let nextIndex = currentIndex;
    if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = buttons.length - 1;
    } else if (event.key === "ArrowDown" || event.key === "ArrowRight") {
      nextIndex = Math.min(buttons.length - 1, currentIndex + 1);
    } else {
      nextIndex = Math.max(0, currentIndex - 1);
    }
    const target = buttons[nextIndex];
    if (!target) return;
    applyEmbeddedTraceFocus(target.dataset.circuitCoverageKind, target.dataset.circuitCoverageId);
    target.focus();
  }

  function applyEmbeddedTraceHighlight(step) {
    if (!consoleFrame || !step) return { nodeCount: 0, wireCount: 0, ready: false };
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.querySelector("#fan-chain-svg")) {
      setText(embeddedHighlightStatus, "等待电路图同步");
      return { nodeCount: 0, wireCount: 0, ready: false };
    }
    ensureEmbeddedTraceStyle(frameDocument);
    frameDocument
      .querySelectorAll("#fan-chain-svg [data-docx-trace-selected]")
      .forEach((element) => element.removeAttribute("data-docx-trace-selected"));

    let nodeCount = 0;
    let wireCount = 0;
    (step.node_ids || []).forEach((nodeId) => {
      frameDocument
        .querySelectorAll(`#fan-chain-svg [data-node="${nodeId}"]`)
        .forEach((element) => {
          element.setAttribute("data-docx-trace-selected", "true");
          nodeCount += 1;
        });
    });
    (step.wire_ids || []).forEach((wireId) => {
      const selector = embeddedWireSelector(wireId);
      if (!selector) return;
      frameDocument.querySelectorAll(selector).forEach((element) => {
        element.setAttribute("data-docx-trace-selected", "true");
        wireCount += 1;
      });
    });
    setText(
      embeddedHighlightStatus,
      `电路图已同步：${step.anchor || "当前句子"} · ${nodeCount}/${(step.node_ids || []).length} 节点 · ${wireCount}/${(step.wire_ids || []).length} 连线`,
    );
    updateKeyboardReviewStatus({
      objectText: `整句链路 · ${(step.node_ids || []).length} 节点 · ${(step.wire_ids || []).length} 连线`,
      syncText: embeddedHighlightStatus ? embeddedHighlightStatus.textContent : "",
    });
    return { nodeCount, wireCount, ready: true };
  }

  function applyEmbeddedTraceFocus(kind, id, options = {}) {
    if (!consoleFrame || !id) return { matchCount: 0, ready: false };
    activePlaybackIndex = -1;
    if (!options.keepOutputMaturitySelection) setOutputMaturityCellState("", "");
    markCircuitObjectFocus(kind, id);
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.querySelector("#fan-chain-svg")) {
      setText(embeddedHighlightStatus, "等待电路图同步");
      updateKeyboardReviewStatus({
        objectKind: kind,
        objectId: id,
        syncText: "等待电路图同步",
      });
      writeReviewHashState();
      return { matchCount: 0, ready: false };
    }
    ensureEmbeddedTraceStyle(frameDocument);
    frameDocument
      .querySelectorAll("#fan-chain-svg [data-docx-trace-selected]")
      .forEach((element) => element.removeAttribute("data-docx-trace-selected"));

    let selector = "";
    let label = "对象";
    if (kind === "node") {
      selector = `#fan-chain-svg [data-node="${id}"]`;
      label = "节点";
    } else if (kind === "wire") {
      selector = embeddedWireSelector(id);
      label = "连线";
    }
    if (!selector) {
      setText(embeddedHighlightStatus, `${label}未匹配：${id}`);
      return { matchCount: 0, ready: true };
    }

    let matchCount = 0;
    frameDocument.querySelectorAll(selector).forEach((element) => {
      element.setAttribute("data-docx-trace-selected", "true");
      matchCount += 1;
    });
    const unit = kind === "wire" ? "条匹配" : "个匹配";
    setText(embeddedHighlightStatus, `聚焦${label}：${id} · ${matchCount} ${unit}`);
    if (kind === "wire") {
      updateTopologyReadback(id);
      setOutputPathWireState(id);
    } else {
      setTopologyRowState("");
      setOutputPathWireState("");
    }
    updateKeyboardReviewStatus({
      objectKind: kind,
      objectId: id,
      syncText: embeddedHighlightStatus ? embeddedHighlightStatus.textContent : "",
    });
    renderObjectProvenance(kind, id);
    writeReviewHashState();
    return { matchCount, ready: true };
  }

  function renderCoverageButton(kind, id) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `demo-reconstruction-chip ${
      kind === "wire" ? "demo-reconstruction-wire-chip" : "demo-reconstruction-node-chip"
    }`;
    button.dataset.circuitCoverageKind = kind;
    button.dataset.circuitCoverageId = id;
    button.setAttribute("aria-pressed", "false");
    button.textContent = id;
    button.addEventListener("click", () => applyEmbeddedTraceFocus(kind, id));
    button.addEventListener("keydown", handleCoverageKeyboardNavigation);
    return button;
  }

  function updateCoverageFilter() {
    const query = (coverageSearch && coverageSearch.value ? coverageSearch.value : "").trim().toLowerCase();
    const buttons = [
      ...Array.from(coverageNodeList ? coverageNodeList.querySelectorAll("button") : []),
      ...Array.from(coverageWireList ? coverageWireList.querySelectorAll("button") : []),
    ];
    let visibleCount = 0;
    buttons.forEach((button) => {
      const matches = !query || button.textContent.toLowerCase().includes(query);
      button.hidden = !matches;
      if (matches) visibleCount += 1;
    });
    setCoverageButtonTabStops(currentCircuitFocus.kind, currentCircuitFocus.id);
    setText(coverageFilterStatus, `${visibleCount}/${buttons.length} 对象`);
  }

  function renderCoverageMatrix(payload) {
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    const nodeIds = Array.isArray(contract.node_ids) ? contract.node_ids : [];
    const wireIds = Array.isArray(contract.wire_ids) ? contract.wire_ids : [];
    setText(
      coverageContract,
      `${nodeIds.length || contract.node_count || 0}/${EXPECTED_NODE_COUNT} 节点 · ${wireIds.length || contract.wire_count || 0}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    if (coverageNodeList) {
      coverageNodeList.innerHTML = "";
      nodeIds.forEach((nodeId) => coverageNodeList.appendChild(renderCoverageButton("node", nodeId)));
    }
    if (coverageWireList) {
      coverageWireList.innerHTML = "";
      wireIds.forEach((wireId) => coverageWireList.appendChild(renderCoverageButton("wire", wireId)));
    }
    updateCoverageFilter();
  }

  function setSelectedTrace(step, options = {}) {
    if (!step || typeof step !== "object") return;
    if (!options.keepPlaybackMode) activePlaybackIndex = -1;
    clearCircuitObjectFocus();
    currentTraceStep = step;
    selectedTraceIndex = traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    syncStepPlaybackToTrace(step);
    document.querySelectorAll("[data-trace-card]").forEach((card) => {
      card.setAttribute("aria-pressed", card.dataset.traceAnchor === step.anchor ? "true" : "false");
    });
    setTraceCardTabStops(step.anchor);
    setCustodyButtonState(step.anchor);
    setText(selectedAnchor, step.anchor || "P035");
    setText(selectedTitle, step.title || "工作过程片段");
    setText(selectedText, step.source_text || "");
    renderInlineChips(selectedNodes, step.node_ids, "demo-reconstruction-node-chip", "无节点", "node");
    renderInlineChips(selectedWires, step.wire_ids, "demo-reconstruction-wire-chip", "无连线", "wire");
    renderInlineChips(selectedFolded, step.folded_predicates, "demo-reconstruction-folded-chip", "无折叠谓词");
    applyEmbeddedTraceHighlight(step);
    updateCustodyActiveReadback();
    if (options.writeHash !== false) writeReviewHashState();
  }

  function requirementLedgerItems() {
    const sourceRows = sourceEntries.map((entry) => {
      const nodeIds = Array.isArray(entry.node_ids) ? entry.node_ids : [];
      const wireIds = Array.isArray(entry.wire_ids) ? entry.wire_ids : [];
      const mapped = nodeIds.length > 0 || wireIds.length > 0;
      return {
        key: `source:${entry.anchor || ""}`,
        kind: "source",
        status: mapped ? "mapped" : "context",
        statusLabel: mapped ? "已映射" : "上下文",
        anchor: entry.anchor || "source",
        role: entry.role || "源文档条目",
        title: entry.role || "源文档条目",
        text: entry.text || "",
        nodeIds,
        wireIds,
      };
    });
    const stepRows = traceSteps.map((step) => ({
      key: `step:${step.anchor || ""}`,
      kind: "step",
      status: "p035",
      statusLabel: "P035 步骤",
      anchor: step.anchor || "P035",
      role: "工作过程拆解",
      title: step.title || "工作过程片段",
      text: step.source_text || "",
      nodeIds: Array.isArray(step.node_ids) ? step.node_ids : [],
      wireIds: Array.isArray(step.wire_ids) ? step.wire_ids : [],
    }));
    return [...sourceRows, ...stepRows];
  }

  function requirementLedgerSearchText(item) {
    return [
      item.anchor,
      item.role,
      item.title,
      item.text,
      ...(item.nodeIds || []),
      ...(item.wireIds || []),
    ].join(" ").toLowerCase();
  }

  function setRequirementLedgerRowState() {
    document.querySelectorAll("[data-requirement-ledger-row]").forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        button.dataset.requirementLedgerRow === requirementLedgerSelectedKey ? "true" : "false",
      );
    });
  }

  function activateRequirementLedgerItem(item) {
    requirementLedgerSelectedKey = item.key;
    if (item.kind === "step") {
      const step = traceSteps.find((candidate) => candidate && candidate.anchor === item.anchor);
      if (step) setSelectedTrace(step);
    } else if (item.wireIds && item.wireIds.length) {
      applyEmbeddedTraceFocus("wire", item.wireIds[0]);
    } else if (item.nodeIds && item.nodeIds.length) {
      applyEmbeddedTraceFocus("node", item.nodeIds[0]);
    } else if (item.anchor === "P035" && traceSteps.length) {
      setSelectedTrace(traceSteps[0]);
    }
    setRequirementLedgerRowState();
  }

  function renderRequirementLedgerFilters(items) {
    if (!requirementLedgerFilters) return;
    const counts = items.reduce(
      (acc, item) => {
        acc.all += 1;
        acc[item.status] = (acc[item.status] || 0) + 1;
        return acc;
      },
      {all: 0, mapped: 0, context: 0, p035: 0},
    );
    const filters = [
      {id: "all", label: `全部 ${counts.all}`},
      {id: "mapped", label: `已映射 ${counts.mapped}`},
      {id: "context", label: `上下文 ${counts.context}`},
      {id: "p035", label: `P035 ${counts.p035}`},
    ];
    requirementLedgerFilters.innerHTML = "";
    filters.forEach((filter) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.requirementLedgerFilter = filter.id;
      button.setAttribute("aria-pressed", requirementLedgerFilter === filter.id ? "true" : "false");
      button.textContent = filter.label;
      button.addEventListener("click", () => {
        requirementLedgerFilter = filter.id;
        renderRequirementLedger();
      });
      requirementLedgerFilters.appendChild(button);
    });
  }

  function renderRequirementLedgerRows() {
    if (!requirementLedgerList) return;
    const items = requirementLedgerItems();
    const query = (requirementLedgerSearch && requirementLedgerSearch.value ? requirementLedgerSearch.value : "")
      .trim()
      .toLowerCase();
    const visibleItems = items.filter((item) => {
      const matchesFilter = requirementLedgerFilter === "all" || item.status === requirementLedgerFilter;
      return matchesFilter && (!query || requirementLedgerSearchText(item).includes(query));
    });
    requirementLedgerList.innerHTML = "";
    if (!visibleItems.length) {
      const li = document.createElement("li");
      li.textContent = "没有匹配的需求覆盖记录";
      requirementLedgerList.appendChild(li);
      setText(requirementLedgerStatus, `0/${items.length} 条`);
      return;
    }
    visibleItems.forEach((item) => {
      const li = document.createElement("li");
      li.dataset.requirementLedgerItem = item.key;
      li.dataset.requirementLedgerStatus = item.status;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-requirement-ledger-row";
      button.dataset.requirementLedgerRow = item.key;
      button.dataset.requirementLedgerKind = item.kind;
      button.dataset.requirementLedgerAnchor = item.anchor;
      button.dataset.requirementLedgerStatus = item.status;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => activateRequirementLedgerItem(item));

      const topLine = document.createElement("span");
      topLine.className = "demo-reconstruction-requirement-ledger-topline";
      const anchor = document.createElement("strong");
      anchor.textContent = item.anchor;
      const role = document.createElement("span");
      role.textContent = item.role;
      topLine.append(anchor, role);

      const text = document.createElement("span");
      text.className = "demo-reconstruction-requirement-ledger-text";
      text.textContent = item.kind === "step" ? item.title : item.text;

      const meta = document.createElement("small");
      meta.textContent = `${item.statusLabel} · ${item.nodeIds.length} 节点 · ${item.wireIds.length} 连线`;

      button.append(topLine, text, meta);
      li.appendChild(button);
      requirementLedgerList.appendChild(li);
    });
    setText(requirementLedgerStatus, `${visibleItems.length}/${items.length} 条`);
    setRequirementLedgerRowState();
  }

  function renderRequirementLedger() {
    if (!requirementLedgerList) return;
    const items = requirementLedgerItems();
    const mappedCount = items.filter((item) => item.status === "mapped").length;
    const contextCount = items.filter((item) => item.status === "context").length;
    const stepCount = items.filter((item) => item.status === "p035").length;
    setText(
      requirementLedgerSummary,
      `${items.length} 条 · ${mappedCount} 已映射 · ${contextCount} 上下文 · ${stepCount} P035`,
    );
    renderRequirementLedgerFilters(items);
    renderRequirementLedgerRows();
  }

  function renderTraceBoard(payload) {
    if (!traceCardList) return;
    const steps = Array.isArray(payload && payload.sequence_steps) ? payload.sequence_steps : [];
    const coverage = payload && payload.coverage ? payload.coverage : {};
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    setText(
      traceContract,
      `${coverage.sequence_step_count || steps.length} 步 · ${coverage.covered_node_count || 0}/${contract.node_count || EXPECTED_NODE_COUNT} 节点 · ${coverage.covered_wire_count || 0}/${contract.wire_count || EXPECTED_WIRE_COUNT} 连线`,
    );
    traceSteps = steps;
    traceCardList.innerHTML = "";
    if (steps.length === 0) {
      const fallback = document.createElement("button");
      fallback.type = "button";
      fallback.className = "demo-reconstruction-trace-card";
      fallback.dataset.traceCard = "empty";
      fallback.textContent = "DOCX 链路板暂无数据";
      traceCardList.appendChild(fallback);
      return;
    }
    steps.forEach((step, index) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "demo-reconstruction-trace-card";
      card.dataset.traceCard = String(index + 1);
      card.dataset.traceAnchor = step.anchor || "";
      card.setAttribute("aria-pressed", index === 0 ? "true" : "false");
      card.tabIndex = index === 0 ? 0 : -1;

      const stepLabel = document.createElement("span");
      stepLabel.className = "demo-reconstruction-trace-step";
      stepLabel.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("strong");
      title.textContent = step.title || "工作过程片段";
      const meta = document.createElement("small");
      meta.textContent = `${(step.node_ids || []).length} 节点 · ${(step.wire_ids || []).length} 连线`;

      card.appendChild(stepLabel);
      card.appendChild(title);
      card.appendChild(meta);
      card.addEventListener("click", () => setSelectedTrace(step));
      card.addEventListener("keydown", handleTraceCardKeydown);
      traceCardList.appendChild(card);
    });
    setSelectedTrace(steps[0], {writeHash: false});
    renderStepPlaybackRail(steps);
    renderAssemblyMap(steps);
    renderCircuitCompletionLadder(steps);
    renderCustodyMatrix(steps);
    renderTopologyStepFilter(steps);
    renderTopologyMatrix();
    renderOutputMaturityMatrix(steps);
    renderOperatorRunway();
  }

  function renderSourceEntries(entries) {
    if (!sourceEntryList) return;
    sourceEntries = Array.isArray(entries) ? entries : [];
    sourceEntryList.innerHTML = "";
    if (!sourceEntries.length) {
      const li = document.createElement("li");
      li.textContent = "DOCX 逐句映射暂无数据";
      sourceEntryList.appendChild(li);
      return;
    }
    sourceEntries.forEach((entry) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-source-entry";
      li.dataset.sourceAnchor = entry.anchor || "";
      const topLine = document.createElement("div");
      topLine.className = "demo-reconstruction-entry-topline";
      const anchor = document.createElement("strong");
      anchor.textContent = entry.anchor || "source";
      const role = document.createElement("span");
      role.textContent = entry.role || "源文档条目";
      topLine.appendChild(anchor);
      topLine.appendChild(role);

      const text = document.createElement("p");
      text.textContent = entry.text || "";

      const chips = document.createElement("div");
      chips.className = "demo-reconstruction-entry-chips";
      appendChipGroup(chips, "节点", entry.node_ids, "demo-reconstruction-node-chip", "node");
      appendChipGroup(chips, "连线", entry.wire_ids, "demo-reconstruction-wire-chip", "wire");

      li.appendChild(topLine);
      li.appendChild(text);
      li.appendChild(chips);
      sourceEntryList.appendChild(li);
    });
    renderTopologyMatrix();
  }

  function renderSequenceSteps(steps) {
    if (!sequenceStepList) return;
    sequenceStepList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const li = document.createElement("li");
      li.textContent = "P035 到 L1-L4 的链路拆解暂无数据";
      sequenceStepList.appendChild(li);
      return;
    }
    steps.forEach((step) => {
      const li = document.createElement("li");
      li.className = "demo-reconstruction-sequence-step";
      li.dataset.sourceAnchor = step.anchor || "";
      li.dataset.traceAnchor = step.anchor || "";
      const title = document.createElement("strong");
      title.textContent = `${step.anchor || "step"} · ${step.title || ""}`;
      const text = document.createElement("p");
      text.textContent = step.source_text || "";

      const chips = document.createElement("div");
      chips.className = "demo-reconstruction-entry-chips";
      appendChipGroup(chips, "节点", step.node_ids, "demo-reconstruction-node-chip", "node");
      appendChipGroup(chips, "连线", step.wire_ids, "demo-reconstruction-wire-chip", "wire");
      appendChipGroup(chips, "折叠谓词", step.folded_predicates, "demo-reconstruction-folded-chip");

      li.appendChild(title);
      li.appendChild(text);
      li.appendChild(chips);
      li.addEventListener("click", () => setSelectedTrace(step));
      sequenceStepList.appendChild(li);
    });
  }

  function renderDocxSentenceCircuitMap(payload) {
    latestDocxPayload = payload || {};
    const source = payload && payload.source ? payload.source : {};
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    const coverage = payload && payload.coverage ? payload.coverage : {};
    const expectedNodes = Array.isArray(contract.node_ids) ? contract.node_ids.length : EXPECTED_NODE_COUNT;
    const expectedWires = Array.isArray(contract.wire_ids) ? contract.wire_ids.length : EXPECTED_WIRE_COUNT;

    setText(docxSourcePath, source.path || "uploads/20260409-thrust-reverser-control-logic.docx");
    setText(
      docxCoverage,
      `${coverage.paragraph_count || source.paragraph_count || 0} 段 · ${source.table_count || 0} 表 · ${coverage.source_entry_count || 0} 条`,
    );
    setText(
      docxCircuitContract,
      `${contract.node_count || EXPECTED_NODE_COUNT}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_count || EXPECTED_WIRE_COUNT}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    setText(docxNodeCoverage, `${coverage.covered_node_count || 0}/${expectedNodes}`);
    setText(docxWireCoverage, `${coverage.covered_wire_count || 0}/${expectedWires}`);
    setText(docxEntryCount, `${coverage.source_entry_count || 0} 条源文档记录`);
    setText(docxSequenceCount, `${coverage.sequence_step_count || 0} 步`);
    renderTraceBoard(payload);
    renderLogicEquationBoard();
    renderCoverageMatrix(payload);
    renderSourceEntries(payload && payload.source_entries);
    renderSequenceSteps(payload && payload.sequence_steps);
    renderRequirementLedger();
    renderTopologyMatrix();
    applyReviewHashState();
    updateReviewPacketFromState();
    updateReviewIndexStatus();
  }

  function renderCircuit(circuit, sourceLabel) {
    const nodes = Array.isArray(circuit && circuit.nodes) ? circuit.nodes : [];
    const wires = Array.isArray(circuit && circuit.wires) ? circuit.wires : [];
    const nodeText = `${nodes.length}/${EXPECTED_NODE_COUNT}`;
    const wireText = `${wires.length}/${EXPECTED_WIRE_COUNT}`;

    setText(sourceState, sourceLabel);
    setText(
      fidelity,
      nodes.length === EXPECTED_NODE_COUNT && wires.length === EXPECTED_WIRE_COUNT
        ? "复刻度：20/20 节点 · 23/23 连线"
        : `复刻度：${nodeText} 节点 · ${wireText} 连线`,
    );
    setText(nodeCount, nodeText);
    setText(wireCount, wireText);
    setText(presetCount, `${PRESETS.length}/5`);
    setText(statusCount, `${STATUS_OUTPUTS.length}/6`);
    setText(nodeCell, `${nodes.length} 个复刻节点 · ${passFail(nodes.length, EXPECTED_NODE_COUNT, "节点")}`);
    setText(wireCell, `${wires.length} 条复刻连线 · ${passFail(wires.length, EXPECTED_WIRE_COUNT, "连线")}`);
    setText(presetCell, `${PRESETS.length} 个场景可对照：${PRESETS.join(" / ")}`);
    setText(statusCell, `${STATUS_OUTPUTS.length} 类状态输出：${STATUS_OUTPUTS.join(" / ")}`);
    renderList(nodeList, nodes, (item, index) => `${String(index).padStart(2, "0")} · ${itemLabel(item, `node_${index}`)}`);
    renderList(wireList, wires, wireLabel);
    updateNodeMetadataFromNodes(nodes);
    updateWireEndpointMapFromWires(wires);
    renderTopologyMatrix();
    refreshEmbeddedReviewFromCircuit();
    renderLogicEquationBoard();
    updateReviewPacketFromState();
    updateReviewIndexStatus();
  }

  async function loadReplayCircuit() {
    const response = await fetch(REPLAY_ENDPOINT, {headers: {"Accept": "application/json"}});
    if (!response.ok) return null;
    const payload = await response.json();
    return circuitViewFromDrawing(payload && payload.drawing_payload);
  }

  async function loadDocxSentenceCircuitMap() {
    const response = await fetch(DOCX_SENTENCE_CIRCUIT_ENDPOINT, {headers: {"Accept": "application/json"}});
    if (!response.ok) return null;
    return response.json();
  }

  if (consoleFrame) {
    consoleFrame.addEventListener("load", () => {
      installOutputMirrorObserver();
      if (currentCircuitFocus.kind && currentCircuitFocus.id) {
        applyEmbeddedTraceFocus(currentCircuitFocus.kind, currentCircuitFocus.id);
      } else if (activePlaybackIndex >= 0) {
        applyEmbeddedPlaybackHighlight(cumulativeTraceContract(activePlaybackIndex));
      } else if (currentTraceStep) {
        applyEmbeddedTraceHighlight(currentTraceStep);
      }
    });
    if (consoleFrame.contentDocument && consoleFrame.contentDocument.readyState !== "loading") {
      installOutputMirrorObserver();
    }
  }
  installReviewIndexNavigation();
  updateReviewIndexStatus();
  if (coverageSearch) {
    coverageSearch.addEventListener("input", () => {
      updateCoverageFilter();
      writeReviewHashState();
    });
  }
  if (requirementLedgerSearch) {
    requirementLedgerSearch.addEventListener("input", renderRequirementLedgerRows);
  }
  if (topologySearch) {
    topologySearch.addEventListener("input", () => {
      updateTopologyFilter();
      writeReviewHashState();
    });
  }
  window.addEventListener("hashchange", applyReviewHashState);

  async function boot() {
    loadDocxSentenceCircuitMap()
      .then((payload) => {
        if (payload) {
          renderDocxSentenceCircuitMap(payload);
        } else {
          renderSourceEntries([{anchor: "DOCX", role: "接口不可用", text: "未能读取原始 DOCX 映射接口", node_ids: [], wire_ids: []}]);
          renderRequirementLedger();
        }
      })
      .catch(() => {
        renderSourceEntries([{anchor: "DOCX", role: "接口异常", text: "原始 DOCX 映射接口返回异常，完整 demo 电路仍可查看。", node_ids: [], wire_ids: []}]);
        renderRequirementLedger();
      });

    const stored = circuitViewFromDrawing(readJson(window.localStorage.getItem(DRAWING_KEY)));
    if (stored) {
      renderCircuit(stored, "读取本地复刻草稿");
      return;
    }
    try {
      const replay = await loadReplayCircuit();
      if (replay) {
        renderCircuit(replay, "读取 golden demo 控制台");
        return;
      }
    } catch (error) {
      // Keep the static acceptance text visible; the page remains read-only.
    }
    renderCircuit({nodes: [], wires: []}, "未找到本地复刻草稿");
  }

  boot();
})();

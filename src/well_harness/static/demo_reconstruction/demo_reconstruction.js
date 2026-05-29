(function () {
  "use strict";

  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const REPLAY_ENDPOINT = "/api/requirements-intake/deepseek-live-demo-replay";
  const DOCX_SENTENCE_CIRCUIT_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;
  const PRESETS = ["默认前向", "着陆展开", "最大反推", "收起回杆", "抑制阻塞"];
  const STATUS_OUTPUTS = ["SW1", "SW2", "TLS", "VDT90", "L1-L4", "THR_LOCK"];
  const SCENARIO_COMPARATOR_IDS = ["max-reverse", "inhibit-block"];
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
      proofText: "抑制位为真时，展开链路保持阻塞，反推锁不释放。",
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
  const reviewIndexCompleteAction = $("demo-reconstruction-review-index-complete-action");
  const completeModeBanner = $("demo-reconstruction-complete-mode-banner");
  const reviewIndexStep = $("demo-reconstruction-review-index-step");
  const reviewIndexObject = $("demo-reconstruction-review-index-object");
  const reviewIndexOutput = $("demo-reconstruction-review-index-output");
  const reviewIndexProofPath = $("demo-reconstruction-review-index-proof-path");
  const reviewIndexHandoffSummary = $("demo-reconstruction-review-index-handoff-summary");
  const reviewIndexHandoffList = $("demo-reconstruction-review-index-handoff-list");
  const reviewIndexGateSummary = $("demo-reconstruction-review-index-gate-summary");
  const reviewIndexGateList = $("demo-reconstruction-review-index-gate-list");
  const reviewIndexTourSummary = $("demo-reconstruction-review-index-tour-summary");
  const reviewIndexTourList = $("demo-reconstruction-review-index-tour-list");
  const reviewIndexEvidenceSummary = $("demo-reconstruction-review-index-evidence-summary");
  const reviewIndexEvidenceList = $("demo-reconstruction-review-index-evidence-list");
  const reviewIndexBuildSummary = $("demo-reconstruction-review-index-build-summary");
  const reviewIndexBuildList = $("demo-reconstruction-review-index-build-list");
  const reviewIndexEquationSummary = $("demo-reconstruction-review-index-equation-summary");
  const reviewIndexEquationList = $("demo-reconstruction-review-index-equation-list");
  const reviewIndexClosureSummary = $("demo-reconstruction-review-index-closure-summary");
  const reviewIndexClosureList = $("demo-reconstruction-review-index-closure-list");
  const reviewIndexOutputSummary = $("demo-reconstruction-review-index-output-summary");
  const reviewIndexOutputList = $("demo-reconstruction-review-index-output-list");
  const reviewIndexScenarioSummary = $("demo-reconstruction-review-index-scenario-summary");
  const reviewIndexScenarioList = $("demo-reconstruction-review-index-scenario-list");
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
  const circuitSnapshotStatus = $("demo-reconstruction-circuit-snapshot-status");
  const circuitSnapshotSource = $("demo-reconstruction-circuit-snapshot-source");
  const circuitSnapshotCircuit = $("demo-reconstruction-circuit-snapshot-circuit");
  const circuitSnapshotOutput = $("demo-reconstruction-circuit-snapshot-output");
  const circuitSnapshotReview = $("demo-reconstruction-circuit-snapshot-review");
  const circuitSnapshotChain = $("demo-reconstruction-circuit-snapshot-chain");
  const circuitSnapshotList = $("demo-reconstruction-circuit-snapshot-list");
  const circuitSnapshotReadback = $("demo-reconstruction-circuit-snapshot-readback");
  const compactRunwayStatus = $("demo-reconstruction-compact-runway-status");
  const compactRunwayState = $("demo-reconstruction-compact-runway-state");
  const compactRunwayLock = $("demo-reconstruction-compact-runway-lock");
  const compactRunwaySummary = $("demo-reconstruction-compact-runway-summary");
  const compactRunwayButtons = Array.from(document.querySelectorAll("[data-compact-runway-preset]"));
  const compactRunwayTra = $("demo-reconstruction-compact-runway-tra");
  const compactRunwayTraValue = $("demo-reconstruction-compact-runway-tra-value");
  const compactRunwayVdt = $("demo-reconstruction-compact-runway-vdt");
  const compactRunwayVdtValue = $("demo-reconstruction-compact-runway-vdt-value");
  const compactRunwayInhibit = $("demo-reconstruction-compact-runway-inhibit");
  const compactRunwayInhibitValue = $("demo-reconstruction-compact-runway-inhibit-value");
  const compactRunwayApply = $("demo-reconstruction-compact-runway-apply");
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
  const reviewVerdictStatus = $("demo-reconstruction-review-verdict-status");
  const reviewVerdictSource = $("demo-reconstruction-review-verdict-source");
  const reviewVerdictCircuit = $("demo-reconstruction-review-verdict-circuit");
  const reviewVerdictOutputs = $("demo-reconstruction-review-verdict-outputs");
  const reviewVerdictFocus = $("demo-reconstruction-review-verdict-focus");
  const reviewVerdictBoundary = $("demo-reconstruction-review-verdict-boundary");
  const reviewVerdictReadback = $("demo-reconstruction-review-verdict-readback");
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
  const controlStripStatus = $("demo-reconstruction-control-strip-status");
  const controlStripStep = $("demo-reconstruction-control-strip-step");
  const controlStripObject = $("demo-reconstruction-control-strip-object");
  const controlStripOutput = $("demo-reconstruction-control-strip-output");
  const controlStripPath = $("demo-reconstruction-control-strip-path");
  const sentenceRunnerStatus = $("demo-reconstruction-sentence-runner-status");
  const sentenceRunnerList = $("demo-reconstruction-sentence-runner-list");
  const sentenceRunnerReadback = $("demo-reconstruction-sentence-runner-readback");
  const proofPathStatus = $("demo-reconstruction-proof-path-status");
  const proofPathList = $("demo-reconstruction-proof-path-list");
  const proofPathReadback = $("demo-reconstruction-proof-path-readback");
  const proofPathCoverageGridStatus = $("demo-reconstruction-proof-path-coverage-grid-status");
  const proofPathCoverageGridList = $("demo-reconstruction-proof-path-coverage-grid-list");
  const proofPathCoverageGridReadback = $("demo-reconstruction-proof-path-coverage-grid-readback");
  const proofPathDeltaRailStatus = $("demo-reconstruction-proof-path-delta-rail-status");
  const proofPathDeltaRailList = $("demo-reconstruction-proof-path-delta-rail-list");
  const proofPathDeltaRailReadback = $("demo-reconstruction-proof-path-delta-rail-readback");
  const proofPathSourceRailStatus = $("demo-reconstruction-proof-path-source-rail-status");
  const proofPathSourceRailList = $("demo-reconstruction-proof-path-source-rail-list");
  const proofPathSourceRailReadback = $("demo-reconstruction-proof-path-source-rail-readback");
  const proofPathSentenceMatrixStatus = $("demo-reconstruction-proof-path-sentence-matrix-status");
  const proofPathSentenceMatrixList = $("demo-reconstruction-proof-path-sentence-matrix-list");
  const proofPathSentenceMatrixReadback = $("demo-reconstruction-proof-path-sentence-matrix-readback");
  const proofPathPredicateMatrixStatus = $("demo-reconstruction-proof-path-predicate-matrix-status");
  const proofPathPredicateMatrixList = $("demo-reconstruction-proof-path-predicate-matrix-list");
  const proofPathPredicateMatrixReadback = $("demo-reconstruction-proof-path-predicate-matrix-readback");
  const proofPathBlueprintSummaryStatus = $("demo-reconstruction-proof-path-blueprint-summary-status");
  const proofPathBlueprintSummaryList = $("demo-reconstruction-proof-path-blueprint-summary-list");
  const proofPathBlueprintSummaryReadback = $("demo-reconstruction-proof-path-blueprint-summary-readback");
  const proofPathLaneModeStatus = $("demo-reconstruction-proof-path-lane-mode-status");
  const proofPathLaneModeButtons = Array.from(document.querySelectorAll("[data-proof-path-lane-mode]"));
  const proofPathReviewLane = $("demo-reconstruction-proof-path-review-lane");
  const proofPathReviewStep = $("demo-reconstruction-proof-path-review-step");
  const proofPathReviewObject = $("demo-reconstruction-proof-path-review-object");
  const proofPathReviewLinkState = $("demo-reconstruction-proof-path-review-link-state");
  const proofPathObjectInspector = $("demo-reconstruction-proof-path-object-inspector");
  const proofPathObjectInspectorObject = $("demo-reconstruction-proof-path-object-inspector-object");
  const proofPathObjectInspectorSourceCount = $("demo-reconstruction-proof-path-object-inspector-source-count");
  const proofPathObjectInspectorStepCount = $("demo-reconstruction-proof-path-object-inspector-step-count");
  const proofPathObjectInspectorEdgeCount = $("demo-reconstruction-proof-path-object-inspector-edge-count");
  const proofPathObjectInspectorCoverage = $("demo-reconstruction-proof-path-object-inspector-coverage");
  const proofPathObjectInspectorSummary = $("demo-reconstruction-proof-path-object-inspector-summary");
  const proofPathObjectInspectorNeighbors = $("demo-reconstruction-proof-path-object-inspector-neighbors");
  const proofPathOutputMapStatus = $("demo-reconstruction-proof-path-output-map-status");
  const proofPathOutputMapList = $("demo-reconstruction-proof-path-output-map-list");
  const proofPathOutputMapReadback = $("demo-reconstruction-proof-path-output-map-readback");
  const scenarioComparatorStatus = $("demo-reconstruction-scenario-comparator-status");
  const scenarioComparatorReadback = $("demo-reconstruction-scenario-comparator-readback");
  const scenarioLedgerStatus = $("demo-reconstruction-scenario-ledger-status");
  const scenarioLedgerList = $("demo-reconstruction-scenario-ledger-list");
  const scenarioTruthStatus = $("demo-reconstruction-scenario-truth-status");
  const scenarioTruthBody = $("demo-reconstruction-scenario-truth-body");
  const operatorRunwayStatus = $("demo-reconstruction-operator-runway-status");
  const operatorRunwayReadback = $("demo-reconstruction-operator-runway-readback");
  const operatorRunwayList = $("demo-reconstruction-operator-runway-list");
  const proofTranscriptSummary = $("demo-reconstruction-proof-transcript-summary");
  const proofTranscriptList = $("demo-reconstruction-proof-transcript-list");
  const consoleFrame = $("demo-reconstruction-console-frame");
  const controlStripButtons = Array.from(document.querySelectorAll("[data-control-strip-action]"));
  const sentenceRunnerButtons = () => Array.from(document.querySelectorAll("[data-sentence-runner-step]"));
  const scenarioComparatorButtons = Array.from(document.querySelectorAll("[data-scenario-comparator-action]"));
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
  let proofPathCoverageAnchor = "";
  let proofPathDeltaAnchor = "";
  let proofPathSourceAnchor = "";
  let proofPathSentenceMatrixAnchor = "";
  let proofPathPredicateMatrixAnchor = "";
  let proofPathBlueprintSummaryAnchor = "";
  let circuitSnapshotAnchor = "";
  let circuitSnapshotChainAnchor = "";
  let proofPathLaneMode = "blueprint";
  let applyingReviewHashState = false;
  let wireEndpointMap = new Map();
  let nodeLabelMap = new Map();
  let nodeKindMap = new Map();
  let outputMirrorObserver = null;
  let scenarioLedgerRecords = new Map();
  let activeOperatorRunwayId = "";
  let compactRunwayMode = "";
  const PROOF_PATH_LANE_MODES = ["blueprint", "source", "matrix", "object", "all"];

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

  function proofPathLaneGroupsForMode(mode) {
    if (mode === "source") return new Set(["timeline", "source"]);
    if (mode === "matrix") return new Set(["timeline", "matrix"]);
    if (mode === "object") return new Set(["timeline", "object", "output"]);
    if (mode === "all") return new Set(["timeline", "source", "matrix", "blueprint", "object", "output"]);
    return new Set(["timeline", "blueprint", "output"]);
  }

  function proofPathLaneModeLabel(mode) {
    if (mode === "source") return "源句";
    if (mode === "matrix") return "矩阵";
    if (mode === "object") return "对象";
    if (mode === "all") return "全部";
    return "蓝图";
  }

  function normalizeProofPathLaneMode(mode) {
    return PROOF_PATH_LANE_MODES.includes(mode) ? mode : "blueprint";
  }

  function setProofPathLaneMode(mode, options = {}) {
    const nextMode = normalizeProofPathLaneMode(mode);
    const visibleGroups = proofPathLaneGroupsForMode(nextMode);
    proofPathLaneMode = nextMode;
    proofPathLaneModeButtons.forEach((button) => {
      const selected = button.dataset.proofPathLaneMode === nextMode;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    document.querySelectorAll("[data-proof-path-lane]").forEach((element) => {
      const groups = (element.getAttribute("data-proof-path-lane") || "").split(/\s+/).filter(Boolean);
      const visible = groups.some((group) => visibleGroups.has(group));
      element.hidden = !visible;
    });
    setText(proofPathLaneModeStatus, proofPathLaneModeLabel(nextMode));
    if (options.writeHash) {
      writeReviewHashState();
    } else {
      updateReviewLink();
    }
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
    const thrText = thr && !thr.startsWith("THR ") && (thr === "ON" || thr === "BLOCKED")
      ? `THR ${thr}`
      : thr;
    const outputText = [status, thrText].filter((value) => value && !value.startsWith("等待") && value !== "--").join(" · ");
    setText(reviewIndexReadiness, reviewPacketReadiness && reviewPacketReadiness.textContent
      ? reviewPacketReadiness.textContent.trim()
      : "等待交付读回");
    setText(reviewIndexStep, selectedStep);
    setText(reviewIndexObject, focusedObject);
    setText(reviewIndexOutput, outputText || "等待输出");
    setText(reviewIndexProofPath, `${proofPathLaneModeLabel(proofPathLaneMode)} · ${reviewHashForState() ? "链接已同步" : "默认视图"}`);
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

  function reviewIndexHandoffRecords() {
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    const ledgerItems = requirementLedgerItems();
    const mappedCount = ledgerItems.filter((item) => item.status === "mapped").length;
    return [
      {
        id: "source",
        title: "01 · 源证据",
        metric: `${ledgerItems.length} 条 · ${mappedCount} 映射`,
        detail: "DOCX / 表格 / P035 汇入",
      },
      {
        id: "build",
        title: "02 · 逐句生成",
        metric: `${traceSteps.length}/5 句 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`,
        detail: "P035-S01 到 P035-S05",
      },
      {
        id: "equation",
        title: "03 · 逻辑方程",
        metric: `${LOGIC_EQUATION_RECORDS.length}/4 方程 · L1-L4`,
        detail: "条件到输出可聚焦",
      },
      {
        id: "closure",
        title: "04 · 闭环电路",
        metric: `${reviewIndexClosureRecords().length}/5 闭环 · THR_LOCK`,
        detail: "L1 到反推锁释放",
      },
      {
        id: "output",
        title: "05 · 最终输出",
        metric: `${OUTPUT_PATH_TARGETS.length}/5 输出 · THR_LOCK`,
        detail: "完整 demo 输出可读",
      },
      {
        id: "scenario",
        title: "06 · 场景校验",
        metric: `${SCENARIO_COMPARATOR_IDS.length}/2 场景 · 最大/阻塞`,
        detail: "DEPLOYED / FAULT 对照",
      },
    ];
  }

  function setReviewIndexHandoffState(recordId) {
    if (!reviewIndexHandoffList) return;
    reviewIndexHandoffList.querySelectorAll("[data-review-index-handoff]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexHandoff === recordId ? "true" : "false");
    });
  }

  function applyReviewIndexHandoff(recordId) {
    if (!reviewIndexHandoffRecords().some((record) => record.id === recordId)) return;
    if (recordId === "source") {
      applyReviewIndexEvidence("docx-source");
    } else if (recordId === "build") {
      applyReviewIndexBuildStep("P035-S05");
    } else if (recordId === "equation") {
      applyReviewIndexEquation("logic4");
    } else if (recordId === "closure") {
      applyReviewIndexClosure("l4-thr-lock");
    } else if (recordId === "output") {
      applyReviewIndexOutputTarget("thr_lock");
    } else if (recordId === "scenario") {
      applyReviewIndexScenario("max-reverse");
    }
    setReviewIndexHandoffState(recordId);
  }

  function renderReviewIndexHandoffRail() {
    if (!reviewIndexHandoffList) return;
    reviewIndexHandoffList.innerHTML = "";
    const records = reviewIndexHandoffRecords();
    records.forEach((record) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexHandoff = record.id;
      button.setAttribute("aria-pressed", "false");

      const title = document.createElement("strong");
      title.textContent = record.title;
      const metric = document.createElement("span");
      metric.textContent = record.metric;
      const detail = document.createElement("small");
      detail.textContent = record.detail;

      button.append(title, metric, detail);
      button.addEventListener("click", () => applyReviewIndexHandoff(record.id));
      reviewIndexHandoffList.appendChild(button);
    });
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    setText(
      reviewIndexHandoffSummary,
      `${records.length}/6 交付 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
  }

  function setReviewIndexGateState(gateId) {
    if (!reviewIndexGateList) return;
    reviewIndexGateList.querySelectorAll("[data-review-index-gate]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexGate === gateId ? "true" : "false");
    });
  }

  function scrollToReviewIndexTarget(targetId) {
    const target = targetId ? document.getElementById(targetId) : null;
    setReviewIndexTarget(targetId);
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function applyReviewIndexGate(gateId) {
    if (gateId === "docx-map") {
      scrollToReviewIndexTarget("demo-reconstruction-docx-circuit-map");
    } else if (gateId === "complete-circuit") {
      applyReviewIndexClosure("l4-thr-lock");
    } else if (gateId === "cumulative-build") {
      applyReviewIndexBuildStep("P035-S05");
    } else if (gateId === "object-review") {
      applyReviewIndexOutputTarget("thr_lock");
    } else if (gateId === "read-only-boundary") {
      scrollToReviewIndexTarget("demo-reconstruction-review-packet");
    }
    setReviewIndexGateState(gateId);
  }

  function setCompleteModeBanner(active) {
    if (!completeModeBanner) return;
    completeModeBanner.hidden = !active;
  }

  function applyReviewIndexCompleteState() {
    setCompleteModeBanner(true);
    applyReviewIndexScenario("max-reverse");
    applyReviewIndexOutputTarget("thr_lock");
    setReviewIndexGateState("object-review");
  }

  function renderReviewIndexGateRail(gates) {
    if (!reviewIndexGateList) return;
    const gateList = Array.isArray(gates) ? gates : [];
    reviewIndexGateList.innerHTML = "";
    if (!gateList.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexGate = "empty";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "等待验收";
      reviewIndexGateList.appendChild(button);
      setText(reviewIndexGateSummary, "等待验收");
      return;
    }
    gateList.forEach((gate) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexGate = gate.id;
      button.dataset.reviewIndexGateStatus = gate.pass ? "pass" : "wait";
      button.setAttribute("aria-pressed", "false");

      const title = document.createElement("strong");
      title.textContent = gate.label;
      const status = document.createElement("span");
      status.textContent = gate.pass ? "通过" : "待补齐";
      const detail = document.createElement("small");
      detail.textContent = gate.detail;

      button.append(title, status, detail);
      button.addEventListener("click", () => applyReviewIndexGate(gate.id));
      reviewIndexGateList.appendChild(button);
    });
    const passed = gateList.filter((gate) => gate.pass).length;
    setText(reviewIndexGateSummary, `${passed}/${gateList.length} 验收 · ${gateList.length - passed} 待补齐`);
  }

  function reviewIndexTourRecords() {
    return [
      {id: "evidence", label: "1 证据", targetId: "demo-reconstruction-review-index-evidence-rail"},
      {id: "build", label: "2 逐句", targetId: "demo-reconstruction-review-index-build-ladder"},
      {id: "equation", label: "3 方程", targetId: "demo-reconstruction-review-index-equation-rail"},
      {id: "closure", label: "4 闭环", targetId: "demo-reconstruction-review-index-closure-rail"},
      {id: "output", label: "5 输出", targetId: "demo-reconstruction-review-index-output-rail"},
      {id: "scenario", label: "6 场景", targetId: "demo-reconstruction-review-index-scenario-rail"},
    ];
  }

  function setReviewIndexTourState(recordId) {
    if (!reviewIndexTourList) return;
    reviewIndexTourList.querySelectorAll("[data-review-index-tour]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexTour === recordId ? "true" : "false");
    });
  }

  function applyReviewIndexTour(recordId) {
    const record = reviewIndexTourRecords().find((item) => item.id === recordId);
    const target = record ? document.getElementById(record.targetId) : null;
    if (!record || !target) return;
    setReviewIndexTourState(record.id);
    if (typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexTourRail() {
    if (!reviewIndexTourList) return;
    reviewIndexTourList.innerHTML = "";
    const records = reviewIndexTourRecords();
    records.forEach((record) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexTour = record.id;
      button.setAttribute("aria-pressed", "false");
      button.textContent = record.label;
      button.addEventListener("click", () => applyReviewIndexTour(record.id));
      reviewIndexTourList.appendChild(button);
    });
    setText(reviewIndexTourSummary, `${records.length}/6 模块 · 证据到场景`);
  }

  function reviewIndexEvidenceRecords() {
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    const ledgerItems = requirementLedgerItems();
    const mappedCount = ledgerItems.filter((item) => item.status === "mapped").length;
    const p035Count = ledgerItems.filter((item) => item.status === "p035").length;
    const readiness = reviewPacketReadiness && reviewPacketReadiness.textContent
      ? reviewPacketReadiness.textContent.trim()
      : "等待验收";
    return [
      {
        id: "docx-source",
        title: "DOCX 源记录",
        targetId: "demo-reconstruction-requirement-ledger",
        metric: `${ledgerItems.length} 条 · ${mappedCount} 已映射`,
        detail: "段落 / 表格 / P035 可查",
      },
      {
        id: "p035-chain",
        title: "P035 逐句",
        targetId: "demo-reconstruction-docx-trace-board",
        metric: `${traceSteps.length}/5 句 · ${p035Count}/5 步`,
        detail: `${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
      },
      {
        id: "object-coverage",
        title: "对象覆盖",
        targetId: "demo-reconstruction-coverage-matrix",
        metric: `${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
        detail: "节点 / 连线可聚焦",
      },
      {
        id: "custody-chain",
        title: "交付链路",
        targetId: "demo-reconstruction-custody-matrix",
        metric: readiness,
        detail: "证据与边界可审",
      },
    ];
  }

  function setReviewIndexEvidenceState(recordId) {
    if (!reviewIndexEvidenceList) return;
    reviewIndexEvidenceList.querySelectorAll("[data-review-index-evidence]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexEvidence === recordId ? "true" : "false");
    });
  }

  function applyReviewIndexEvidence(recordId) {
    const record = reviewIndexEvidenceRecords().find((item) => item.id === recordId);
    if (!record) return;
    const target = record.targetId ? document.getElementById(record.targetId) : null;
    setReviewIndexTarget(record.targetId);
    setReviewIndexEvidenceState(record.id);
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexEvidenceRail() {
    if (!reviewIndexEvidenceList) return;
    reviewIndexEvidenceList.innerHTML = "";
    const records = reviewIndexEvidenceRecords();
    if (!records.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexEvidence = "empty";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "等待证据";
      reviewIndexEvidenceList.appendChild(button);
      setText(reviewIndexEvidenceSummary, "等待证据接入");
      return;
    }
    records.forEach((record) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexEvidence = record.id;
      button.setAttribute("aria-pressed", "false");

      const title = document.createElement("strong");
      title.textContent = record.title;
      const metric = document.createElement("span");
      metric.textContent = record.metric;
      const detail = document.createElement("small");
      detail.textContent = record.detail;

      button.append(title, metric, detail);
      button.addEventListener("click", () => applyReviewIndexEvidence(record.id));
      reviewIndexEvidenceList.appendChild(button);
    });
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    setText(
      reviewIndexEvidenceSummary,
      `${records.length}/4 证据 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
  }

  function setReviewIndexBuildState(anchor) {
    if (!reviewIndexBuildList) return;
    reviewIndexBuildList.querySelectorAll("[data-review-index-build-step]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexBuildStep === anchor ? "true" : "false");
    });
  }

  function applyReviewIndexBuildStep(anchor) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0) return;
    setProofPathLaneMode("blueprint", {writeHash: false});
    applyProofPathStep(anchor);
    setReviewIndexTarget("demo-reconstruction-proof-path");
    setReviewIndexBuildState(anchor);
    const target = $("demo-reconstruction-proof-path");
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexBuildLadder(steps) {
    if (!reviewIndexBuildList) return;
    reviewIndexBuildList.innerHTML = "";
    if (!Array.isArray(steps) || !steps.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexBuildStep = "empty";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "等待逐句构建";
      reviewIndexBuildList.appendChild(button);
      setText(reviewIndexBuildSummary, "等待 P035 构建");
      return;
    }
    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const focus = proofPathFocusTarget(step, contract);
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexBuildStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const meta = document.createElement("small");
      meta.textContent = `${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      const output = document.createElement("em");
      const outputLabel = contract.node_ids.length === EXPECTED_NODE_COUNT
        && contract.wire_ids.length === EXPECTED_WIRE_COUNT
        && focus.id === "wire_logic4_thr_lock"
        ? "完整电路闭合 · THR_LOCK 输出可读"
        : sentenceRunnerOutputLabel(step, contract);
      output.textContent = `${outputLabel} · ${focus.id ? reviewObjectLabel(focus.kind, focus.id) : "等待聚焦"}`;

      button.append(anchor, title, meta, output);
      button.addEventListener("click", () => applyReviewIndexBuildStep(step.anchor || ""));
      reviewIndexBuildList.appendChild(button);
    });
    const finalContract = cumulativeTraceContract(steps.length - 1);
    setText(
      reviewIndexBuildSummary,
      `${steps.length}/5 句 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    setReviewIndexBuildState(currentTraceStep && currentTraceStep.anchor ? currentTraceStep.anchor : steps[0].anchor || "");
  }

  function setReviewIndexEquationState(recordId) {
    if (!reviewIndexEquationList) return;
    reviewIndexEquationList.querySelectorAll("[data-review-index-equation]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexEquation === recordId ? "true" : "false");
    });
  }

  function applyReviewIndexEquation(recordId) {
    const record = LOGIC_EQUATION_RECORDS.find((item) => item.id === recordId);
    if (!record) return;
    activateLogicEquationRecord(record);
    setReviewIndexTarget("demo-reconstruction-logic-equation-board");
    setReviewIndexEquationState(record.id);
    const target = $("demo-reconstruction-logic-equation-board");
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexEquationRail() {
    if (!reviewIndexEquationList) return;
    reviewIndexEquationList.innerHTML = "";
    if (!LOGIC_EQUATION_RECORDS.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexEquation = "empty";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "等待方程";
      reviewIndexEquationList.appendChild(button);
      setText(reviewIndexEquationSummary, "等待方程接入");
      return;
    }

    const states = LOGIC_EQUATION_RECORDS.map((record) => ({
      record,
      state: logicEquationState(record),
    }));
    const readyCount = states.filter((item) => item.state.ready).length;
    states.forEach(({record, state}) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexEquation = record.id;
      button.setAttribute("aria-pressed", currentCircuitFocus.id === record.focusId ? "true" : "false");

      const title = document.createElement("strong");
      title.textContent = record.title;
      const expression = document.createElement("code");
      expression.textContent = record.expression;
      const metric = document.createElement("span");
      metric.textContent = `${state.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${state.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      const meta = document.createElement("small");
      meta.textContent = `${record.anchor} · ${record.output}`;

      button.append(title, expression, metric, meta);
      button.addEventListener("click", () => applyReviewIndexEquation(record.id));
      reviewIndexEquationList.appendChild(button);
    });
    setText(reviewIndexEquationSummary, `${readyCount}/${LOGIC_EQUATION_RECORDS.length} 方程 · L1-L4 到 THR_LOCK`);
    const activeEquation = LOGIC_EQUATION_RECORDS.find((record) => record.focusId === currentCircuitFocus.id);
    setReviewIndexEquationState(activeEquation ? activeEquation.id : "");
  }

  function reviewIndexClosureRecords() {
    return [
      {
        id: "l1-tls",
        anchor: "P035-S01",
        title: "L1 -> TLS",
        detail: "RA / SW1 / 抑制位进入 TLS 115VAC",
        focusKind: "wire",
        focusId: "wire_logic1_tls115",
      },
      {
        id: "l2-etrac",
        anchor: "P035-S02",
        title: "L2 -> ETRAC",
        detail: "SW2 / 地面 / 发动机运行进入 540VDC",
        focusKind: "wire",
        focusId: "wire_logic2_etrac",
      },
      {
        id: "l3-pdu",
        anchor: "P035-S03",
        title: "L3 -> PDU",
        detail: "TLS / TRA / N1K 形成展开指令",
        focusKind: "wire",
        focusId: "wire_logic3_pdu",
      },
      {
        id: "vdt90-feedback",
        anchor: "P035-S04",
        title: "PDU -> VDT90",
        detail: "电机带动滑动罩到 90% 反馈",
        focusKind: "wire",
        focusId: "wire_pdu_vdt90",
      },
      {
        id: "l4-thr-lock",
        anchor: "P035-S05",
        title: "L4 -> THR_LOCK",
        detail: "VDT90 与 L3 闭合，反推锁释放",
        focusKind: "wire",
        focusId: "wire_logic4_thr_lock",
      },
    ];
  }

  function setReviewIndexClosureState(recordId) {
    if (!reviewIndexClosureList) return;
    reviewIndexClosureList.querySelectorAll("[data-review-index-closure]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexClosure === recordId ? "true" : "false");
    });
  }

  function applyReviewIndexClosure(recordId) {
    const record = reviewIndexClosureRecords().find((item) => item.id === recordId);
    const step = record ? traceStepByAnchor(record.anchor) : null;
    if (!record || !step) return;
    setProofPathLaneMode("object", {writeHash: false});
    setSelectedTrace(step, {writeHash: false});
    applyEmbeddedTraceFocus(record.focusKind, record.focusId);
    setReviewIndexTarget("demo-reconstruction-proof-path");
    setReviewIndexClosureState(record.id);
    const target = $("demo-reconstruction-proof-path");
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexClosureRail() {
    if (!reviewIndexClosureList) return;
    reviewIndexClosureList.innerHTML = "";
    const records = reviewIndexClosureRecords();
    records.forEach((record, index) => {
      const step = traceStepByAnchor(record.anchor);
      const contract = step ? cumulativeTraceContract(traceSteps.indexOf(step)) : {node_ids: [], wire_ids: []};
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexClosure = record.id;
      button.setAttribute("aria-pressed", currentCircuitFocus.id === record.focusId ? "true" : "false");

      const title = document.createElement("strong");
      title.textContent = `${String(index + 1).padStart(2, "0")} · ${record.title}`;
      const metric = document.createElement("span");
      metric.textContent = `${record.anchor} · ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      const detail = document.createElement("small");
      detail.textContent = `${record.detail} · ${record.focusId}`;

      button.append(title, metric, detail);
      button.addEventListener("click", () => applyReviewIndexClosure(record.id));
      reviewIndexClosureList.appendChild(button);
    });
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    setText(
      reviewIndexClosureSummary,
      `${records.length}/5 闭环 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    const activeRecord = records.find((record) => record.focusId === currentCircuitFocus.id);
    setReviewIndexClosureState(activeRecord ? activeRecord.id : "");
  }

  function setReviewIndexOutputState(targetId) {
    if (!reviewIndexOutputList) return;
    reviewIndexOutputList.querySelectorAll("[data-review-index-output-target]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexOutputTarget === targetId ? "true" : "false");
    });
  }

  function applyReviewIndexOutputTarget(targetId) {
    const target = OUTPUT_PATH_TARGETS.find((item) => item.id === targetId);
    if (!target) return;
    const record = proofPathOutputRecord(target);
    if (record.terminalStep) {
      setSelectedTrace(record.terminalStep, {writeHash: false});
    }
    setProofPathLaneMode("object", {writeHash: false});
    applyProofPathOutputTarget(targetId);
    setReviewIndexTarget("demo-reconstruction-proof-path");
    setReviewIndexOutputState(targetId);
    const proofPath = $("demo-reconstruction-proof-path");
    if (proofPath && typeof proofPath.scrollIntoView === "function") {
      proofPath.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexOutputRail() {
    if (!reviewIndexOutputList) return;
    reviewIndexOutputList.innerHTML = "";
    if (wireEndpointMap.size === 0) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexOutputTarget = "empty";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "等待输出";
      reviewIndexOutputList.appendChild(button);
      setText(reviewIndexOutputSummary, "等待输出接入");
      return;
    }
    const records = OUTPUT_PATH_TARGETS.map((target) => proofPathOutputRecord(target));
    const readyCount = records.filter((record) => record.path.wire_ids.length > 0).length;
    records.forEach((record) => {
      const {target, path, terminalWire, terminalStep} = record;
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexOutputTarget = target.id;
      button.setAttribute("aria-pressed", outputPathTargetId === target.id ? "true" : "false");

      const title = document.createElement("strong");
      title.textContent = target.label;
      const metric = document.createElement("span");
      metric.textContent = `${path.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${path.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`;
      const meta = document.createElement("small");
      meta.textContent = `${terminalStep ? terminalStep.anchor : "待匹配"} · ${terminalWire || target.id}`;

      button.append(title, metric, meta);
      button.addEventListener("click", () => applyReviewIndexOutputTarget(target.id));
      reviewIndexOutputList.appendChild(button);
    });
    setText(reviewIndexOutputSummary, `${readyCount}/${OUTPUT_PATH_TARGETS.length} 输出 · THR_LOCK 可审`);
    setReviewIndexOutputState(outputPathTargetId);
  }

  function reviewIndexScenarioRecords() {
    return [
      {
        presetId: "max-reverse",
        recordId: "runway-l4-thr-lock",
        title: "最大反推",
        expected: "DEPLOYED · THR ON",
      },
      {
        presetId: "inhibit-block",
        recordId: "runway-inhibit",
        title: "抑制阻塞",
        expected: "FAULT · THR BLOCKED",
      },
    ];
  }

  function setReviewIndexScenarioState(presetId) {
    if (!reviewIndexScenarioList) return;
    reviewIndexScenarioList.querySelectorAll("[data-review-index-scenario]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.reviewIndexScenario === presetId ? "true" : "false");
    });
  }

  function applyReviewIndexScenario(presetId) {
    const item = reviewIndexScenarioRecords().find((record) => record.presetId === presetId);
    const runwayRecord = item ? operatorRunwayRecordById(item.recordId) : null;
    if (!runwayRecord) return;
    activateOperatorRunwayRecord(runwayRecord);
    setReviewIndexTarget("demo-reconstruction-operator-runway");
    setReviewIndexScenarioState(presetId);
    const target = $("demo-reconstruction-operator-runway");
    if (target && typeof target.scrollIntoView === "function") {
      target.scrollIntoView({behavior: "smooth", block: "start"});
    }
  }

  function renderReviewIndexScenarioRail() {
    if (!reviewIndexScenarioList) return;
    reviewIndexScenarioList.innerHTML = "";
    reviewIndexScenarioRecords().forEach((item) => {
      const runwayRecord = operatorRunwayRecordById(item.recordId);
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.reviewIndexScenario = item.presetId;
      button.setAttribute("aria-pressed", runwayRecord && runwayRecord.id === activeOperatorRunwayId ? "true" : "false");

      const title = document.createElement("strong");
      title.textContent = item.title;
      const expected = document.createElement("span");
      expected.textContent = item.expected;
      const meta = document.createElement("small");
      meta.textContent = runwayRecord
        ? `${runwayRecord.order}/06 · ${runwayRecord.anchor} · ${runwayRecord.output}`
        : "等待场景";

      button.append(title, expected, meta);
      button.addEventListener("click", () => applyReviewIndexScenario(item.presetId));
      reviewIndexScenarioList.appendChild(button);
    });
    setText(reviewIndexScenarioSummary, `${SCENARIO_COMPARATOR_IDS.length}/2 场景 · THR_LOCK 对照`);
    const activeRecord = operatorRunwayRecordById(activeOperatorRunwayId);
    setReviewIndexScenarioState(activeRecord ? activeRecord.presetId : "");
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

  function proofPathOutputRecord(target) {
    const path = upstreamPathForTarget(target.id);
    const terminalWire = path.wire_ids[path.wire_ids.length - 1] || "";
    const terminalStep = terminalWire ? firstTraceStepForWire(terminalWire) : null;
    return {
      target,
      path,
      terminalWire,
      terminalStep,
    };
  }

  function setProofPathOutputMapState(targetId) {
    document.querySelectorAll("[data-proof-path-output-target]").forEach((button) => {
      const selected = button.dataset.proofPathOutputTarget === targetId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function applyProofPathOutputTarget(targetId) {
    const target = OUTPUT_PATH_TARGETS.find((item) => item.id === targetId);
    if (!target) return;
    const record = proofPathOutputRecord(target);
    outputPathTargetId = targetId;
    renderOutputPathLane();
    setProofPathOutputMapState(targetId);
    if (record.terminalWire) {
      applyEmbeddedTraceFocus("wire", record.terminalWire);
    } else {
      applyEmbeddedTraceFocus("node", targetId);
    }
    const wireText = record.terminalWire || targetId;
    const stepText = record.terminalStep ? record.terminalStep.anchor : "待匹配";
    setText(
      proofPathOutputMapReadback,
      `${target.label} · ${record.path.wire_ids.length} 条上游连线 · ${stepText} · ${wireText}`,
    );
  }

  function renderProofPathOutputMap() {
    if (!proofPathOutputMapList) return;
    proofPathOutputMapList.innerHTML = "";
    const records = OUTPUT_PATH_TARGETS.map((target) => proofPathOutputRecord(target));
    const readyCount = records.filter((record) => record.path.wire_ids.length > 0).length;
    setText(proofPathOutputMapStatus, `${readyCount}/${OUTPUT_PATH_TARGETS.length} 输出`);
    records.forEach((record) => {
      const {target, path, terminalWire, terminalStep} = record;
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.proofPathOutputTarget = target.id;
      button.setAttribute("aria-pressed", outputPathTargetId === target.id ? "true" : "false");
      const title = document.createElement("strong");
      title.textContent = target.label;
      const metric = document.createElement("span");
      metric.textContent = `${path.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${path.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`;
      const meta = document.createElement("small");
      meta.textContent = `${terminalStep ? terminalStep.anchor : "待匹配"} · ${terminalWire || target.id}`;
      button.append(title, metric, meta);
      button.addEventListener("click", () => applyProofPathOutputTarget(target.id));
      proofPathOutputMapList.appendChild(button);
    });
    const selectedRecord = records.find((record) => record.target.id === outputPathTargetId) || records[0];
    if (selectedRecord) {
      setText(
        proofPathOutputMapReadback,
        `${selectedRecord.target.label} · ${selectedRecord.path.wire_ids.length} 条上游连线 · ${selectedRecord.terminalWire || selectedRecord.target.id}`,
      );
    }
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
      renderProofPathOutputMap();
      renderReviewIndexOutputRail();
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
    renderProofPathOutputMap();
    renderReviewIndexOutputRail();
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
    setReviewIndexEquationState(record.id);
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
    renderReviewIndexEquationRail();
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
      complete: params.get("complete") === "1",
      step: params.get("step") || "",
      focusKind: focusParts.length === 2 ? focusParts[0] : "",
      focusId: focusParts.length === 2 ? focusParts[1] : "",
      query: params.get("q") || "",
      topologyStep: params.get("topology") || "",
      topologyQuery: params.get("tq") || "",
      lane: params.get("lane") || "",
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
    if (proofPathLaneMode && proofPathLaneMode !== "blueprint") {
      params.set("lane", proofPathLaneMode);
    }
    return params.toString();
  }

  function updateReviewLink() {
    const hash = reviewHashForState();
    const suffix = hash ? `#${hash}` : "";
    if (reviewLink) {
      reviewLink.href = `${window.location.pathname}${window.location.search}${suffix}`;
    }
    updateProofPathReviewStrip(hash);
  }

  function updateProofPathReviewStrip(hash = reviewHashForState()) {
    const stepText = currentTraceStep && currentTraceStep.anchor ? currentTraceStep.anchor : "等待选择";
    const objectText = currentCircuitFocus.kind && currentCircuitFocus.id
      ? reviewObjectLabel(currentCircuitFocus.kind, currentCircuitFocus.id)
      : "等待聚焦";
    setText(proofPathReviewLane, proofPathLaneModeLabel(proofPathLaneMode));
    setText(proofPathReviewStep, stepText);
    setText(proofPathReviewObject, objectText);
    setText(proofPathReviewLinkState, hash ? "链接已同步" : "默认视图");
    setText(reviewIndexProofPath, `${proofPathLaneModeLabel(proofPathLaneMode)} · ${hash ? "链接已同步" : "默认视图"}`);
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
      `${passGateCount}/${gateCount} 验收 · ${ledger.total} 覆盖项 · ${outputReadyCount}/${OUTPUT_PATH_TARGETS.length} 输出`,
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

  function updateReviewVerdictBoard(gates, context) {
    if (!reviewVerdictStatus) return;
    const gateList = Array.isArray(gates) ? gates : [];
    const gateCount = gateList.length;
    const passCount = gateList.filter((gate) => gate.pass).length;
    const expectedNodes = context.expectedNodes || EXPECTED_NODE_COUNT;
    const expectedWires = context.expectedWires || EXPECTED_WIRE_COUNT;
    const coveredNodes = context.coveredNodes || 0;
    const coveredWires = context.coveredWires || 0;
    const outputReadyCount = finalOutputReadinessCount(context.finalContract);
    const boundaryGate = gateList.find((gate) => gate.id === "read-only-boundary");

    setText(reviewVerdictStatus, `${passCount}/${gateCount} 验收`);
    setText(reviewVerdictSource, `${context.sourceCount} 源记录 · ${context.stepCount}/5 步`);
    setText(reviewVerdictCircuit, `${coveredNodes}/${expectedNodes} 节点 · ${coveredWires}/${expectedWires} 连线`);
    setText(reviewVerdictOutputs, `${outputReadyCount}/${OUTPUT_PATH_TARGETS.length} 输出`);
    setText(reviewVerdictFocus, context.focusedObject || "等待聚焦");
    setText(
      reviewVerdictBoundary,
      boundaryGate && boundaryGate.pass ? "只读边界 · 控制逻辑未改动" : "边界待确认",
    );
    setText(
      reviewVerdictReadback,
      passCount === gateCount
        ? `证据可审 · ${coveredNodes}/${expectedNodes} 节点 · ${coveredWires}/${expectedWires} 连线 · ${outputReadyCount}/${OUTPUT_PATH_TARGETS.length} 输出`
        : `继续补齐审阅点 · ${passCount}/${gateCount} 验收`,
    );
  }

  function frameText(frameDocument, selector, fallback) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    const value = element && element.textContent ? element.textContent.trim() : "";
    return value || fallback;
  }

  function frameNumber(frameDocument, selector, fallback) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    const value = element ? Number(element.value) : Number.NaN;
    return Number.isFinite(value) ? value : fallback;
  }

  function frameChecked(frameDocument, selector, fallback = false) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    return element ? !!element.checked : fallback;
  }

  function dispatchFrameEvent(frameDocument, element, type) {
    if (!frameDocument || !element) return;
    const EventCtor = frameDocument.defaultView ? frameDocument.defaultView.Event : Event;
    element.dispatchEvent(new EventCtor(type, {bubbles: true}));
  }

  function setFrameValue(frameDocument, selector, value) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    if (element) element.value = String(value);
    return element;
  }

  function setFrameChecked(frameDocument, selector, value) {
    const element = frameDocument ? frameDocument.querySelector(selector) : null;
    if (element) element.checked = !!value;
    return element;
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

  function clearFramePresetState(frameDocument) {
    if (!frameDocument) return;
    frameDocument.querySelectorAll(".fan-preset-btn").forEach((button) => {
      button.setAttribute("aria-pressed", "false");
    });
    const status = frameDocument.querySelector("#fan-preset-status");
    if (status) status.textContent = "当前场景：手动输入";
  }

  function clearFrameFaults(frameDocument) {
    if (!frameDocument) return;
    const clearButton = frameDocument.querySelector("#fan-fault-clear");
    if (clearButton && typeof clearButton.click === "function") {
      clearButton.click();
      return;
    }
    frameDocument.querySelectorAll(".fan-fault-check").forEach((checkbox) => {
      if (checkbox.checked) {
        checkbox.checked = false;
        dispatchFrameEvent(frameDocument, checkbox, "change");
      }
    });
  }

  function applyScenarioPreset(presetId) {
    if (!consoleFrame || !presetId) return;
    const frameDocument = consoleFrame.contentDocument;
    const button = frameDocument
      ? frameDocument.querySelector(`.fan-preset-btn[data-preset="${presetId}"]`)
      : null;
    if (button && typeof button.click === "function") button.click();
  }

  function compactScenarioLabel(presetId) {
    if (presetId === "max-reverse") return "最大反推";
    if (presetId === "inhibit-block") return "抑制阻塞";
    if (presetId === "operator") return "当前输入";
    return "等待运行";
  }

  function compactStatusLabel(status) {
    if (status === "DEPLOYED") return "可用";
    if (status === "FAULT") return "阻塞";
    if (status === "IDLE") return "待命";
    return status || "等待运行";
  }

  function compactLockLabel(value) {
    if (value === "ON" || value === "RELEASED") return "释放";
    if (value === "BLOCKED") return "阻塞";
    if (value === "OFF") return "未释放";
    return value || "等待输出";
  }

  function compactSummary(snapshot, presetId) {
    if (!snapshot) return "选择演示状态";
    const state = compactStatusLabel(snapshot.status);
    const lock = compactLockLabel(snapshot.thr);
    if (presetId === "max-reverse") {
      return state === "可用" && lock === "释放" ? "最大反推链路已释放" : "等待最大反推结果";
    }
    if (presetId === "inhibit-block") {
      return state === "阻塞" && lock === "阻塞" ? "抑制生效，反推锁保持阻塞" : "等待抑制阻塞结果";
    }
    return snapshot.summary || "等待输出";
  }

  function compactOperatorSummary(snapshot) {
    if (!snapshot) return "运行当前输入";
    const state = compactStatusLabel(snapshot.status);
    const lock = compactLockLabel(snapshot.thr);
    if (state === "可用" && lock === "释放") return "当前输入允许反推锁释放";
    if (state === "阻塞" || lock === "阻塞") return "当前输入保持安全阻塞";
    if (lock === "未释放") return "当前输入未释放反推锁";
    return snapshot.summary || "当前输入等待结果";
  }

  function compactAngleLabel(value) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return "0°";
    return `${Number.isInteger(numeric) ? numeric.toFixed(0) : numeric.toFixed(1)}°`;
  }

  function updateCompactOperatorInputLabels() {
    if (compactRunwayTra && compactRunwayTraValue) {
      setText(compactRunwayTraValue, compactAngleLabel(compactRunwayTra.value));
    }
    if (compactRunwayVdt && compactRunwayVdtValue) {
      setText(compactRunwayVdtValue, `${Math.round(Number(compactRunwayVdt.value) || 0)}%`);
    }
    if (compactRunwayInhibit && compactRunwayInhibitValue) {
      setText(compactRunwayInhibitValue, compactRunwayInhibit.checked ? "开启" : "关闭");
    }
  }

  function syncCompactOperatorInputsFromFrame(frameDocument) {
    if (!frameDocument) return;
    if (compactRunwayTra) compactRunwayTra.value = String(frameNumber(frameDocument, "#fan-tra-lever", Number(compactRunwayTra.value) || 0));
    if (compactRunwayVdt) compactRunwayVdt.value = String(frameNumber(frameDocument, "#fan-vdt", Number(compactRunwayVdt.value) || 0));
    if (compactRunwayInhibit) compactRunwayInhibit.checked = frameChecked(frameDocument, "#fan-reverser-inhibited", compactRunwayInhibit.checked);
    updateCompactOperatorInputLabels();
  }

  function setCompactRunwayButtonState(activeId = "") {
    compactRunwayButtons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        button.dataset.compactRunwayPreset === activeId ? "true" : "false",
      );
    });
  }

  function updateCompactRunwayFromFrame(frameDocument) {
    if (!compactRunwayStatus || !compactRunwayState || !compactRunwayLock || !compactRunwaySummary) return;
    const active = activeScenarioFromFrame(frameDocument);
    const snapshot = scenarioOutputSnapshot(frameDocument);
    syncCompactOperatorInputsFromFrame(frameDocument);
    if (active) compactRunwayMode = active.id;
    if (!active && compactRunwayMode === "operator") {
      setCompactRunwayButtonState("");
      setText(compactRunwayStatus, compactScenarioLabel("operator"));
      setText(compactRunwayState, compactStatusLabel(snapshot.status));
      setText(compactRunwayLock, compactLockLabel(snapshot.thr));
      setText(compactRunwaySummary, compactOperatorSummary(snapshot));
      return;
    }
    if (!active) {
      setCompactRunwayButtonState("");
      setText(compactRunwayStatus, "等待运行");
      setText(compactRunwayState, "等待运行");
      setText(compactRunwayLock, "等待输出");
      setText(compactRunwaySummary, "选择演示状态");
      return;
    }
    setCompactRunwayButtonState(active.id);
    setText(compactRunwayStatus, compactScenarioLabel(active.id));
    setText(compactRunwayState, compactStatusLabel(snapshot.status));
    setText(compactRunwayLock, compactLockLabel(snapshot.thr));
    setText(compactRunwaySummary, compactSummary(snapshot, active.id));
  }

  function installCompactRunwayActions() {
    updateCompactOperatorInputLabels();
    compactRunwayButtons.forEach((button) => {
      const presetId = button.dataset.compactRunwayPreset || "";
      button.addEventListener("click", () => {
        compactRunwayMode = presetId;
        setCompactRunwayButtonState(presetId);
        setText(compactRunwayStatus, compactScenarioLabel(presetId));
        setText(compactRunwayState, "运行中");
        setText(compactRunwayLock, "等待输出");
        setText(compactRunwaySummary, "正在读取结果");
        applyScenarioPreset(presetId);
        requestAnimationFrame(updateOutputMirrorFromFrame);
      });
    });
    [compactRunwayTra, compactRunwayVdt].forEach((input) => {
      if (input) input.addEventListener("input", updateCompactOperatorInputLabels);
    });
    if (compactRunwayInhibit) {
      compactRunwayInhibit.addEventListener("change", updateCompactOperatorInputLabels);
    }
    if (compactRunwayApply) {
      compactRunwayApply.addEventListener("click", applyCompactOperatorInputs);
    }
  }

  function applyCompactOperatorInputs() {
    if (!consoleFrame) return;
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument) return;
    const tra = compactRunwayTra ? Number(compactRunwayTra.value) || 0 : -32;
    const vdt = compactRunwayVdt ? Number(compactRunwayVdt.value) || 0 : 100;
    const inhibit = compactRunwayInhibit ? compactRunwayInhibit.checked : false;
    compactRunwayMode = "operator";
    clearFramePresetState(frameDocument);
    clearFrameFaults(frameDocument);
    setOperatorRunwayState("");
    setFrameValue(frameDocument, "#fan-ra", 2);
    setFrameValue(frameDocument, "#fan-n1k", inhibit ? 70 : 80);
    setFrameChecked(frameDocument, "#fan-engine-running", true);
    setFrameChecked(frameDocument, "#fan-aircraft-on-ground", true);
    setFrameChecked(frameDocument, "#fan-eec-enable", true);
    setFrameChecked(frameDocument, "#fan-reverser-inhibited", inhibit);
    setFrameValue(frameDocument, "#fan-tra-lever", tra);
    const vdtElement = setFrameValue(frameDocument, "#fan-vdt", vdt);
    setCompactRunwayButtonState("");
    setText(compactRunwayStatus, compactScenarioLabel("operator"));
    setText(compactRunwayState, "运行中");
    setText(compactRunwayLock, "等待输出");
    setText(compactRunwaySummary, "正在读取结果");
    dispatchFrameEvent(frameDocument, vdtElement, "input");
    requestAnimationFrame(updateOutputMirrorFromFrame);
  }

  function scenarioComparatorLabel(presetId) {
    if (presetId === "max-reverse") return "最大反推";
    if (presetId === "inhibit-block") return "抑制阻塞";
    return presetId || "场景";
  }

  function scenarioComparatorExpected(presetId) {
    if (presetId === "max-reverse") return "目标 DEPLOYED · THR ON";
    if (presetId === "inhibit-block") return "目标 FAULT · THR BLOCKED";
    return "等待运行";
  }

  function scenarioComparatorSummary(presetId) {
    const record = scenarioLedgerRecords.get(presetId);
    if (!record || !record.captured) return scenarioComparatorExpected(presetId);
    return `${record.status} · THR ${record.thr}`;
  }

  function updateScenarioComparatorStatus(activeId = "") {
    if (!scenarioComparatorStatus || !scenarioComparatorReadback) return;
    let capturedCount = 0;
    SCENARIO_COMPARATOR_IDS.forEach((presetId) => {
      const record = scenarioLedgerRecords.get(presetId);
      const captured = Boolean(record && record.captured);
      if (captured) capturedCount += 1;
      const result = document.querySelector(`[data-scenario-comparator-result="${presetId}"]`);
      if (result) result.textContent = scenarioComparatorSummary(presetId);
    });
    scenarioComparatorButtons.forEach((button) => {
      const presetId = button.dataset.scenarioComparatorAction || "";
      const selected = activeId === presetId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
      button.dataset.scenarioComparatorCaptured = scenarioLedgerRecords.get(presetId)?.captured ? "true" : "false";
    });
    setText(scenarioComparatorStatus, `${capturedCount}/${SCENARIO_COMPARATOR_IDS.length} 已运行`);
    const activeRecord = SCENARIO_COMPARATOR_IDS.includes(activeId) ? scenarioLedgerRecords.get(activeId) : null;
    if (activeRecord && activeRecord.captured) {
      setText(
        scenarioComparatorReadback,
        `${scenarioComparatorLabel(activeId)} · ${activeRecord.status} · THR ${activeRecord.thr} · TLS ${activeRecord.tls} · ETRAC ${activeRecord.etrac} · EEC ${activeRecord.eec}`,
      );
    } else {
      setText(scenarioComparatorReadback, "运行最大反推和抑制阻塞，核对 THR_LOCK 输出差异");
    }
    renderReviewIndexScenarioRail();
  }

  function installScenarioComparatorActions() {
    scenarioComparatorButtons.forEach((button) => {
      const presetId = button.dataset.scenarioComparatorAction || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        updateScenarioComparatorStatus(presetId);
        applyScenarioPreset(presetId);
      });
    });
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
      updateScenarioComparatorStatus("");
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
    updateScenarioComparatorStatus(activeId);
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

  function controlStripRecordForAction(action) {
    if (action === "prove-thr") return operatorRunwayRecordById("runway-l4-thr-lock");
    if (action === "block-inhibit") return operatorRunwayRecordById("runway-inhibit");
    if (action === "start-chain") return operatorRunwayRecordById("runway-l1-unlock");
    return null;
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

  function controlStripOutputSummary() {
    const status = outputMirrorStatus && outputMirrorStatus.textContent
      ? outputMirrorStatus.textContent.trim()
      : "等待";
    const thr = outputMirrorThrOutput && outputMirrorThrOutput.textContent
      ? outputMirrorThrOutput.textContent.trim()
      : "--";
    return `${status} · THR ${thr}`;
  }

  function setControlStripActionState(recordId) {
    controlStripButtons.forEach((button) => {
      const record = controlStripRecordForAction(button.dataset.controlStripAction || "");
      const selected = Boolean(record && record.id === recordId);
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateControlStripStatus() {
    const activeRecord = operatorRunwayRecordById(activeOperatorRunwayId);
    const stepText = currentTraceStep && currentTraceStep.anchor
      ? `${currentTraceStep.anchor} · ${currentTraceStep.title || "工作过程片段"}`
      : "等待 P035";
    const objectText = reviewObjectLabel(currentCircuitFocus.kind, currentCircuitFocus.id);
    const outputText = controlStripOutputSummary();
    const pathText = activeRecord
      ? `${activeRecord.order} · ${activeRecord.title} · ${activeRecord.output}`
      : "选择 L4 证明或抑制阻塞";

    setText(controlStripStep, stepText);
    setText(controlStripObject, objectText);
    setText(controlStripOutput, outputText);
    setText(controlStripPath, pathText);
    setText(controlStripStatus, activeRecord ? `${activeRecord.order}/06 · ${activeRecord.presetLabel}` : "等待选择");
    setControlStripActionState(activeRecord ? activeRecord.id : "");
    setReviewIndexScenarioState(activeRecord ? activeRecord.presetId : "");
  }

  function activateControlStripAction(action) {
    const record = controlStripRecordForAction(action);
    if (record) activateOperatorRunwayRecord(record);
  }

  function installControlStripActions() {
    controlStripButtons.forEach((button) => {
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => activateControlStripAction(button.dataset.controlStripAction || ""));
    });
  }

  function sentenceRunnerOutputLabel(step, contract) {
    const anchor = step && step.anchor ? step.anchor : "";
    if (
      contract
      && contract.node_ids.length === EXPECTED_NODE_COUNT
      && contract.wire_ids.length === EXPECTED_WIRE_COUNT
    ) {
      return "完整电路闭合";
    }
    if (anchor === "P035-S04") return "VDT90 反馈接入";
    if (anchor === "P035-S03") return "展开指令接入";
    if (anchor === "P035-S02") return "ETRAC 供电接入";
    if (anchor === "P035-S01") return "TLS 解锁接入";
    return "等待输出";
  }

  function setSentenceRunnerState(anchor) {
    sentenceRunnerButtons().forEach((button) => {
      const selected = button.dataset.sentenceRunnerStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateSentenceRunnerStatus(step = currentTraceStep) {
    if (!sentenceRunnerStatus || !sentenceRunnerReadback) return;
    if (!step || !traceSteps.length) {
      setText(sentenceRunnerStatus, "等待 DOCX");
      setText(sentenceRunnerReadback, "等待逐句生成");
      setSentenceRunnerState("");
      return;
    }
    const index = traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    const safeIndex = index >= 0 ? index : 0;
    const contract = cumulativeTraceContract(safeIndex);
    const outputLabel = sentenceRunnerOutputLabel(step, contract);
    setText(sentenceRunnerStatus, `${safeIndex + 1}/${traceSteps.length} · ${outputLabel}`);
    setText(
      sentenceRunnerReadback,
      `${step.anchor || "P035"} · ${step.title || "工作过程片段"} · 累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );
    setSentenceRunnerState(step.anchor || "");
  }

  function applySentenceRunnerStep(anchor) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0) return;
    applyStepPlayback(index);
    updateSentenceRunnerStatus(traceSteps[index]);
  }

  function renderSentenceRunner(steps) {
    if (!sentenceRunnerList) return;
    sentenceRunnerList.innerHTML = "";
    if (!Array.isArray(steps) || !steps.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.sentenceRunnerStep = "empty";
      button.textContent = "等待 P035 拆解";
      sentenceRunnerList.appendChild(button);
      updateSentenceRunnerStatus(null);
      return;
    }
    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.sentenceRunnerStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const meta = document.createElement("small");
      meta.textContent = `${sentenceRunnerOutputLabel(step, contract)} · ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      button.append(anchor, title, meta);
      button.addEventListener("click", () => applySentenceRunnerStep(step.anchor || ""));
      sentenceRunnerList.appendChild(button);
    });
    updateSentenceRunnerStatus(currentTraceStep || steps[0]);
  }

  function proofPathFocusTarget(step, contract) {
    const nodeIds = Array.isArray(step && step.node_ids) ? step.node_ids : [];
    const wireIds = Array.isArray(contract && contract.wire_ids) ? contract.wire_ids : [];
    if (
      contract
      && contract.node_ids.length === EXPECTED_NODE_COUNT
      && contract.wire_ids.length === EXPECTED_WIRE_COUNT
      && wireIds.includes("wire_logic4_thr_lock")
    ) {
      return {kind: "wire", id: "wire_logic4_thr_lock"};
    }
    const outputPriority = [
      "vdt90",
      "pdu_motor",
      "pls_power",
      "eec_deploy",
      "etrac_540v",
      "tls_unlocked",
      "tls115",
    ];
    const nodeId = outputPriority.find((id) => nodeIds.includes(id)) || nodeIds[nodeIds.length - 1] || "";
    return nodeId ? {kind: "node", id: nodeId} : {kind: "", id: ""};
  }

  function proofPathFocusRecords(step, contract) {
    const records = [];
    const seen = new Set();
    const add = (kind, id) => {
      if (!kind || !id || seen.has(`${kind}:${id}`)) return;
      seen.add(`${kind}:${id}`);
      records.push({kind, id});
    };
    const primary = proofPathFocusTarget(step, contract);
    add(primary.kind, primary.id);
    (step.wire_ids || []).slice(-2).forEach((wireId) => add("wire", wireId));
    (step.node_ids || []).slice(-2).forEach((nodeId) => add("node", nodeId));
    return records.slice(0, 4);
  }

  function setProofPathState(anchor) {
    document.querySelectorAll("[data-proof-path-step]").forEach((button) => {
      const selected = button.dataset.proofPathStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  function updateProofPathStatus(step = currentTraceStep, focusOverride = null) {
    if (!proofPathStatus || !proofPathReadback) return;
    if (!step || !traceSteps.length) {
      setText(proofPathStatus, "等待 P035");
      setText(proofPathReadback, "等待完整电路证明");
      setProofPathState("");
      return;
    }
    const index = traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    const safeIndex = index >= 0 ? index : 0;
    const contract = cumulativeTraceContract(safeIndex);
    const focus = focusOverride || proofPathFocusTarget(step, contract);
    const focusText = focus.id ? reviewObjectLabel(focus.kind, focus.id) : "等待聚焦";
    const outputLabel = sentenceRunnerOutputLabel(step, contract);
    setText(proofPathStatus, `${safeIndex + 1}/${traceSteps.length} · ${outputLabel}`);
    setText(
      proofPathReadback,
      `${step.anchor || "P035"} · 累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${focusText}`,
    );
    setProofPathState(step.anchor || "");
  }

  function applyProofPathStep(anchor) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0) return;
    const step = traceSteps[index];
    const contract = cumulativeTraceContract(index);
    applyStepPlayback(index);
    const focus = proofPathFocusTarget(step, contract);
    if (focus.kind && focus.id) applyEmbeddedTraceFocus(focus.kind, focus.id);
    updateProofPathStatus(step);
  }

  function applyProofPathObjectJump(anchor, kind, id) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0 || !kind || !id) return;
    const step = traceSteps[index];
    applyStepPlayback(index);
    applyEmbeddedTraceFocus(kind, id);
    updateProofPathStatus(step, {kind, id});
  }

  function renderProofPathTimeline(steps) {
    if (!proofPathList) return;
    proofPathList.innerHTML = "";
    if (!Array.isArray(steps) || !steps.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.proofPathStep = "empty";
      button.textContent = "等待逐句证明路径";
      proofPathList.appendChild(button);
      updateProofPathStatus(null);
      return;
    }
    steps.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const outputLabel = sentenceRunnerOutputLabel(step, contract);
      const finalReady = contract.node_ids.length === EXPECTED_NODE_COUNT
        && contract.wire_ids.length === EXPECTED_WIRE_COUNT;
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-row";
      row.dataset.proofPathRow = step.anchor || "";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-step";
      button.dataset.proofPathStep = step.anchor || "";
      button.dataset.proofPathFinal = finalReady ? "true" : "false";
      button.setAttribute("aria-pressed", "false");

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const source = document.createElement("em");
      source.textContent = step.source_text || "等待源文证据";
      const meta = document.createElement("small");
      meta.textContent = `${outputLabel} · 本句 ${(step.node_ids || []).length} 节点 / ${(step.wire_ids || []).length} 连线 · 累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`;
      button.append(anchor, title, source, meta);
      button.addEventListener("click", () => applyProofPathStep(step.anchor || ""));
      row.appendChild(button);

      const focusList = document.createElement("div");
      focusList.className = "demo-reconstruction-proof-path-focus-list";
      focusList.dataset.proofPathFocusList = step.anchor || "";
      proofPathFocusRecords(step, contract).forEach((record) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.dataset.proofPathFocusKind = record.kind;
        chip.dataset.proofPathFocusId = record.id;
        chip.textContent = reviewObjectLabel(record.kind, record.id);
        chip.addEventListener("click", () => applyProofPathObjectJump(step.anchor || "", record.kind, record.id));
        focusList.appendChild(chip);
      });
      row.appendChild(focusList);
      proofPathList.appendChild(row);
    });
    updateProofPathStatus(currentTraceStep || steps[0]);
  }

  function proofPathCoverageOutputs(contract) {
    const activeNodes = new Set(Array.isArray(contract && contract.node_ids) ? contract.node_ids : []);
    return OUTPUT_PATH_TARGETS.filter((target) => activeNodes.has(target.id));
  }

  function setProofPathCoverageGridState(anchor) {
    document.querySelectorAll("[data-proof-path-coverage-step]").forEach((button) => {
      const selected = button.dataset.proofPathCoverageStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathCoverageAnchor = anchor || "";
  }

  function updateProofPathCoverageGridReadback(step, contract, focus = null) {
    if (!proofPathCoverageGridReadback || !step || !contract) return;
    const outputs = proofPathCoverageOutputs(contract).map((target) => target.label);
    const outputText = outputs.length ? outputs.join(" / ") : "等待输出";
    const focusText = focus && focus.id ? ` · ${reviewObjectLabel(focus.kind, focus.id)}` : "";
    setText(
      proofPathCoverageGridReadback,
      `${step.anchor || "P035"} · 累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · 输出 ${outputText}${focusText}`,
    );
  }

  function applyProofPathCoverageStep(anchor) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0) return;
    const step = traceSteps[index];
    const contract = cumulativeTraceContract(index);
    applyStepPlayback(index);
    setProofPathCoverageGridState(anchor);
    updateProofPathStatus(step);
    updateProofPathCoverageGridReadback(step, contract);
  }

  function applyProofPathCoverageObject(anchor, kind, id) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0 || !kind || !id) return;
    const step = traceSteps[index];
    const contract = cumulativeTraceContract(index);
    applyStepPlayback(index);
    applyEmbeddedTraceFocus(kind, id);
    setProofPathCoverageGridState(anchor);
    updateProofPathStatus(step, {kind, id});
    updateProofPathCoverageGridReadback(step, contract, {kind, id});
  }

  function renderProofPathCoverageGrid(steps) {
    if (!proofPathCoverageGridList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathCoverageGridList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathCoverageStep = "empty";
      empty.textContent = "等待逐句覆盖";
      proofPathCoverageGridList.appendChild(empty);
      setText(proofPathCoverageGridStatus, "等待覆盖矩阵");
      setText(proofPathCoverageGridReadback, "等待选择逐句覆盖。");
      return;
    }

    const finalContract = cumulativeTraceContract(items.length - 1);
    setText(
      proofPathCoverageGridStatus,
      `${items.length}/5 步 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );

    items.forEach((step, index) => {
      const contract = cumulativeTraceContract(index);
      const outputLabels = proofPathCoverageOutputs(contract).map((target) => target.label);
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-coverage-row";
      row.dataset.proofPathCoverageRow = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-coverage-step";
      button.dataset.proofPathCoverageStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathCoverageStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const metric = document.createElement("small");
      metric.textContent = `累计 ${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · 输出 ${outputLabels.join(" / ") || "待接入"}`;
      button.append(anchor, title, metric);
      row.appendChild(button);

      const focusList = document.createElement("div");
      focusList.className = "demo-reconstruction-proof-path-coverage-focus-list";
      proofPathFocusRecords(step, contract).forEach((record) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.dataset.proofPathCoverageFocusKind = record.kind;
        chip.dataset.proofPathCoverageFocusId = record.id;
        chip.textContent = reviewObjectLabel(record.kind, record.id);
        chip.addEventListener(
          "click",
          () => applyProofPathCoverageObject(step.anchor || "", record.kind, record.id),
        );
        focusList.appendChild(chip);
      });
      row.appendChild(focusList);
      proofPathCoverageGridList.appendChild(row);
    });

    const selectedAnchor = proofPathCoverageAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedIndex = items.findIndex((step) => step && step.anchor === selectedAnchor);
    const safeIndex = selectedIndex >= 0 ? selectedIndex : 0;
    const selectedStep = items[safeIndex];
    const selectedContract = cumulativeTraceContract(safeIndex);
    setProofPathCoverageGridState(selectedStep.anchor || "");
    updateProofPathCoverageGridReadback(selectedStep, selectedContract);
  }

  function proofPathDeltaRecord(index) {
    const step = traceSteps[index] || {};
    const contract = cumulativeTraceContract(index);
    const previous = index > 0 ? cumulativeTraceContract(index - 1) : {node_ids: [], wire_ids: []};
    const previousNodes = new Set(previous.node_ids || []);
    const previousWires = new Set(previous.wire_ids || []);
    return {
      step,
      contract,
      previous,
      newNodes: contract.node_ids.filter((nodeId) => !previousNodes.has(nodeId)),
      newWires: contract.wire_ids.filter((wireId) => !previousWires.has(wireId)),
    };
  }

  function setProofPathDeltaRailState(anchor) {
    document.querySelectorAll("[data-proof-path-delta-step]").forEach((button) => {
      const selected = button.dataset.proofPathDeltaStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathDeltaAnchor = anchor || "";
  }

  function updateProofPathDeltaRailReadback(record, focus = null) {
    if (!proofPathDeltaRailReadback || !record || !record.step) return;
    const {step, contract, previous, newNodes, newWires} = record;
    const focusText = focus && focus.id ? ` · ${reviewObjectLabel(focus.kind, focus.id)}` : "";
    setText(
      proofPathDeltaRailReadback,
      `${step.anchor || "P035"} · ${previous.node_ids.length}->${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${previous.wire_ids.length}->${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · +${newNodes.length} 节点 · +${newWires.length} 连线${focusText}`,
    );
  }

  function applyProofPathDeltaStep(anchor) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0) return;
    const record = proofPathDeltaRecord(index);
    applyStepPlayback(index);
    setProofPathDeltaRailState(anchor);
    updateProofPathStatus(record.step);
    updateProofPathDeltaRailReadback(record);
  }

  function applyProofPathDeltaObject(anchor, kind, id) {
    const index = traceSteps.findIndex((step) => step && step.anchor === anchor);
    if (index < 0 || !kind || !id) return;
    const record = proofPathDeltaRecord(index);
    applyStepPlayback(index);
    applyEmbeddedTraceFocus(kind, id);
    setProofPathDeltaRailState(anchor);
    updateProofPathStatus(record.step, {kind, id});
    updateProofPathDeltaRailReadback(record, {kind, id});
  }

  function appendProofPathDeltaChips(container, anchor, label, values, kind) {
    const group = document.createElement("div");
    group.className = "demo-reconstruction-proof-path-delta-group";
    const title = document.createElement("strong");
    title.textContent = label;
    const chips = document.createElement("div");
    chips.className = "demo-reconstruction-proof-path-delta-chips";
    const list = Array.isArray(values) ? values : [];
    if (!list.length) {
      const empty = document.createElement("span");
      empty.className = "demo-reconstruction-proof-path-delta-chip";
      empty.textContent = "无新增";
      chips.appendChild(empty);
    } else {
      list.forEach((value) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "demo-reconstruction-proof-path-delta-chip";
        chip.dataset.proofPathDeltaFocusKind = kind;
        chip.dataset.proofPathDeltaFocusId = value;
        chip.textContent = value;
        chip.addEventListener("click", () => applyProofPathDeltaObject(anchor, kind, value));
        chips.appendChild(chip);
      });
    }
    group.append(title, chips);
    container.appendChild(group);
  }

  function renderProofPathDeltaRail(steps) {
    if (!proofPathDeltaRailList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathDeltaRailList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathDeltaStep = "empty";
      empty.textContent = "等待逐句增量";
      proofPathDeltaRailList.appendChild(empty);
      setText(proofPathDeltaRailStatus, "等待增量轨道");
      setText(proofPathDeltaRailReadback, "等待选择增量轨道。");
      return;
    }

    const finalRecord = proofPathDeltaRecord(items.length - 1);
    setText(
      proofPathDeltaRailStatus,
      `${items.length}/5 步 · +${finalRecord.contract.node_ids.length} 节点 · +${finalRecord.contract.wire_ids.length} 连线`,
    );

    items.forEach((step, index) => {
      const record = proofPathDeltaRecord(index);
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-delta-row";
      row.dataset.proofPathDeltaRow = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-delta-step";
      button.dataset.proofPathDeltaStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathDeltaStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const metric = document.createElement("small");
      metric.textContent = `${record.previous.node_ids.length}->${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.previous.wire_ids.length}->${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · +${record.newNodes.length} 节点 · +${record.newWires.length} 连线`;
      button.append(anchor, title, metric);
      row.appendChild(button);

      const groups = document.createElement("div");
      groups.className = "demo-reconstruction-proof-path-delta-groups";
      appendProofPathDeltaChips(groups, step.anchor || "", "新增节点", record.newNodes, "node");
      appendProofPathDeltaChips(groups, step.anchor || "", "新增连线", record.newWires, "wire");
      row.appendChild(groups);
      proofPathDeltaRailList.appendChild(row);
    });

    const selectedAnchor = proofPathDeltaAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedIndex = items.findIndex((step) => step && step.anchor === selectedAnchor);
    const safeIndex = selectedIndex >= 0 ? selectedIndex : 0;
    setProofPathDeltaRailState(items[safeIndex].anchor || "");
    updateProofPathDeltaRailReadback(proofPathDeltaRecord(safeIndex));
  }

  function proofPathSourceRecords(step) {
    if (!step || !Array.isArray(sourceEntries)) return [];
    const stepNodes = new Set(Array.isArray(step.node_ids) ? step.node_ids : []);
    const stepWires = new Set(Array.isArray(step.wire_ids) ? step.wire_ids : []);
    const baseAnchor = typeof step.anchor === "string" ? step.anchor.split("-")[0] : "";
    const records = sourceEntries.filter((entry) => {
      if (!entry || typeof entry !== "object") return false;
      if (entry.anchor === step.anchor || entry.anchor === baseAnchor) return true;
      const entryNodes = Array.isArray(entry.node_ids) ? entry.node_ids : [];
      const entryWires = Array.isArray(entry.wire_ids) ? entry.wire_ids : [];
      return entryNodes.some((nodeId) => stepNodes.has(nodeId))
        || entryWires.some((wireId) => stepWires.has(wireId));
    });
    return records.sort((left, right) => {
      const priority = (entry) => {
        if (entry.anchor === step.anchor) return 0;
        if (entry.anchor === baseAnchor) return 1;
        if (entry.role === "动作顺序") return 2;
        return 3;
      };
      return priority(left) - priority(right);
    });
  }

  function proofPathSourceNeedle(step, sourceText) {
    const source = step && typeof step.source_text === "string" ? step.source_text.replace(/\s+/g, " ").trim() : "";
    const target = typeof sourceText === "string" ? sourceText.replace(/\s+/g, " ").trim() : "";
    if (!source || !target) return "";
    const chunks = source.split(/[，；。]/).map((chunk) => chunk.trim()).filter((chunk) => chunk.length >= 6);
    return chunks.find((chunk) => target.includes(chunk))
      || chunks.map((chunk) => chunk.slice(0, 12)).find((chunk) => target.includes(chunk))
      || "";
  }

  function proofPathSourceExcerpt(text, limit = 96, needle = "") {
    const value = typeof text === "string" ? text.replace(/\s+/g, " ").trim() : "";
    const marker = typeof needle === "string" ? needle.replace(/\s+/g, " ").trim() : "";
    if (value.length > limit && marker && value.includes(marker)) {
      const start = Math.max(0, value.indexOf(marker) - Math.floor((limit - marker.length) / 2));
      const end = Math.min(value.length, start + limit);
      const prefix = start > 0 ? "..." : "";
      const suffix = end < value.length ? "..." : "";
      return `${prefix}${value.slice(start, end)}${suffix}`;
    }
    return value.length > limit ? `${value.slice(0, limit)}...` : value;
  }

  function setProofPathSourceRailState(anchor) {
    document.querySelectorAll("[data-proof-path-source-step]").forEach((button) => {
      const selected = button.dataset.proofPathSourceStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathSourceAnchor = anchor || "";
  }

  function updateProofPathSourceRailReadback(step, sourceEntry = null) {
    if (!proofPathSourceRailReadback || !step) return;
    const records = proofPathSourceRecords(step);
    const source = sourceEntry || records[0] || {};
    const sourceAnchor = source.anchor ? ` · ${source.anchor}` : "";
    const sourceText = source.text || step.source_text || "";
    const needle = proofPathSourceNeedle(step, sourceText);
    setText(
      proofPathSourceRailReadback,
      `${step.anchor || "P035"} · ${records.length} 条源句命中${sourceAnchor} · ${proofPathSourceExcerpt(sourceText, 120, needle)}`,
    );
  }

  function applyProofPathSourceStep(anchor) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathSourceRailState(anchor);
    updateProofPathSourceRailReadback(step);
    writeReviewHashState();
  }

  function applyProofPathSourceAnchor(stepAnchor, sourceAnchor) {
    const step = traceSteps.find((item) => item && item.anchor === stepAnchor);
    if (!step) return;
    const source = proofPathSourceRecords(step).find((entry) => entry.anchor === sourceAnchor) || null;
    setSelectedTrace(step, {writeHash: false});
    setProofPathSourceRailState(stepAnchor);
    updateProofPathSourceRailReadback(step, source);
    writeReviewHashState();
  }

  function renderProofPathSourceRail(steps) {
    if (!proofPathSourceRailList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathSourceRailList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathSourceStep = "empty";
      empty.textContent = "等待源句核验";
      proofPathSourceRailList.appendChild(empty);
      setText(proofPathSourceRailStatus, "等待源句核验");
      setText(proofPathSourceRailReadback, "等待选择源句。");
      return;
    }

    const totalMatches = items.reduce((sum, step) => sum + proofPathSourceRecords(step).length, 0);
    setText(proofPathSourceRailStatus, `${items.length}/5 步 · ${totalMatches} 源句命中`);

    items.forEach((step, index) => {
      const records = proofPathSourceRecords(step);
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-source-row";
      row.dataset.proofPathSourceRow = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-source-step";
      button.dataset.proofPathSourceStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathSourceStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const excerpt = document.createElement("small");
      excerpt.textContent = proofPathSourceExcerpt(step.source_text || "", 120);
      button.append(anchor, title, excerpt);
      row.appendChild(button);

      const chips = document.createElement("div");
      chips.className = "demo-reconstruction-proof-path-source-anchors";
      records.slice(0, 6).forEach((entry) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.dataset.proofPathSourceAnchor = entry.anchor || "";
        chip.textContent = entry.anchor || "source";
        chip.addEventListener("click", () => applyProofPathSourceAnchor(step.anchor || "", entry.anchor || ""));
        chips.appendChild(chip);
      });
      if (!records.length) {
        const empty = document.createElement("span");
        empty.textContent = "等待源句命中";
        chips.appendChild(empty);
      }
      row.appendChild(chips);
      proofPathSourceRailList.appendChild(row);
    });

    const selectedAnchor = proofPathSourceAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedStep = items.find((step) => step && step.anchor === selectedAnchor) || items[0];
    setProofPathSourceRailState(selectedStep.anchor || "");
    updateProofPathSourceRailReadback(selectedStep);
  }

  function proofPathSentenceMatrixRecord(step) {
    const index = traceSteps.findIndex((item) => item && step && item.anchor === step.anchor);
    const safeIndex = index >= 0 ? index : 0;
    const contract = traceSteps.length ? cumulativeTraceContract(safeIndex) : {node_ids: [], wire_ids: []};
    const sourceRecords = proofPathSourceRecords(step);
    const outputs = ladderMilestonesForStep(step);
    return {
      contract,
      sourceRecords,
      outputText: assemblyOutputLabelForStep(step, contract),
      outputs,
    };
  }

  function setProofPathSentenceMatrixState(anchor) {
    document.querySelectorAll("[data-proof-path-sentence-step]").forEach((button) => {
      const selected = button.dataset.proofPathSentenceStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathSentenceMatrixAnchor = anchor || "";
  }

  function updateProofPathSentenceMatrixReadback(step, focus = null) {
    if (!proofPathSentenceMatrixReadback || !step) return;
    const record = proofPathSentenceMatrixRecord(step);
    const sourceAnchor = record.sourceRecords[0] && record.sourceRecords[0].anchor
      ? record.sourceRecords[0].anchor
      : "无源锚点";
    const focusText = focus && focus.id ? ` · ${focus.kind === "wire" ? "连线" : "节点"} · ${focus.id}` : "";
    setText(
      proofPathSentenceMatrixReadback,
      `${step.anchor || "P035"} · 源 ${sourceAnchor} +${Math.max(0, record.sourceRecords.length - 1)} · ${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${record.outputText}${focusText}`,
    );
  }

  function applyProofPathSentenceMatrixStep(anchor) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathSentenceMatrixState(anchor);
    updateProofPathSentenceMatrixReadback(step);
    writeReviewHashState();
  }

  function applyProofPathSentenceMatrixObject(anchor, kind, id) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step || !kind || !id) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathSentenceMatrixState(anchor);
    applyEmbeddedTraceFocus(kind, id);
    updateProofPathSentenceMatrixReadback(step, {kind, id});
  }

  function appendProofPathSentenceMatrixChips(container, anchor, label, values, kind = "") {
    const group = document.createElement("div");
    group.className = "demo-reconstruction-proof-path-sentence-matrix-group";
    const title = document.createElement("strong");
    title.textContent = label;
    const chips = document.createElement("div");
    chips.className = "demo-reconstruction-proof-path-sentence-matrix-chips";
    const list = Array.isArray(values) ? values : [];
    if (!list.length) {
      const empty = document.createElement("span");
      empty.textContent = "无";
      chips.appendChild(empty);
    } else {
      list.forEach((value) => {
        const chip = kind ? document.createElement("button") : document.createElement("span");
        chip.textContent = value;
        if (kind) {
          chip.type = "button";
          chip.dataset.proofPathSentenceFocusKind = kind;
          chip.dataset.proofPathSentenceFocusId = value;
          chip.addEventListener("click", () => applyProofPathSentenceMatrixObject(anchor, kind, value));
        }
        chips.appendChild(chip);
      });
    }
    group.append(title, chips);
    container.appendChild(group);
  }

  function renderProofPathSentenceMatrix(steps) {
    if (!proofPathSentenceMatrixList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathSentenceMatrixList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathSentenceStep = "empty";
      empty.textContent = "等待逐句矩阵";
      proofPathSentenceMatrixList.appendChild(empty);
      setText(proofPathSentenceMatrixStatus, "等待逐句矩阵");
      setText(proofPathSentenceMatrixReadback, "等待选择逐句矩阵。");
      return;
    }

    const finalContract = cumulativeTraceContract(items.length - 1);
    setText(
      proofPathSentenceMatrixStatus,
      `${items.length}/5 句 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );

    items.forEach((step, index) => {
      const record = proofPathSentenceMatrixRecord(step);
      const source = record.sourceRecords[0] || {};
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-sentence-matrix-row";
      row.dataset.proofPathSentenceRow = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-sentence-matrix-step";
      button.dataset.proofPathSentenceStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathSentenceMatrixStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("span");
      title.textContent = step.title || "工作过程片段";
      const metrics = document.createElement("small");
      metrics.textContent = `${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · 源 ${source.anchor || "无"}`;
      button.append(anchor, title, metrics);

      const sourceText = document.createElement("p");
      const sourceNeedle = proofPathSourceNeedle(step, source.text || step.source_text || "");
      sourceText.textContent = proofPathSourceExcerpt(source.text || step.source_text || "", 130, sourceNeedle);

      const output = document.createElement("p");
      output.textContent = record.outputText;

      const groups = document.createElement("div");
      groups.className = "demo-reconstruction-proof-path-sentence-matrix-groups";
      appendProofPathSentenceMatrixChips(groups, step.anchor || "", "节点", step.node_ids || [], "node");
      appendProofPathSentenceMatrixChips(groups, step.anchor || "", "连线", step.wire_ids || [], "wire");
      appendProofPathSentenceMatrixChips(groups, step.anchor || "", "输出", record.outputs);

      row.append(button, sourceText, output, groups);
      proofPathSentenceMatrixList.appendChild(row);
    });

    const selectedAnchor = proofPathSentenceMatrixAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedStep = items.find((step) => step && step.anchor === selectedAnchor) || items[0];
    setProofPathSentenceMatrixState(selectedStep.anchor || "");
    updateProofPathSentenceMatrixReadback(selectedStep);
  }

  function proofPathPredicateRecord(step) {
    const anchor = step && step.anchor ? step.anchor : "";
    if (anchor === "P035-S04") {
      return {
        gate: "VDT90",
        expression: "PDU motor energized -> VDT90 >= 90% feedback",
        output: "VDT90 feedback",
        focusKind: "wire",
        focusId: "wire_pdu_vdt90",
        sourceNodes: ["pdu_motor"],
        outputNodes: ["vdt90"],
      };
    }
    const equation = LOGIC_EQUATION_RECORDS.find((record) => record.anchor === anchor);
    if (equation) {
      return {
        gate: equation.id.toUpperCase(),
        expression: equation.expression,
        output: equation.output,
        focusKind: equation.focusKind,
        focusId: equation.focusId,
        sourceNodes: equation.sourceNodes || [],
        outputNodes: equation.outputNodes || [],
      };
    }
    return {
      gate: anchor || "P035",
      expression: step && step.source_text ? step.source_text : "等待判据",
      output: assemblyOutputLabelForStep(step || {}, {node_ids: [], wire_ids: []}),
      focusKind: "",
      focusId: "",
      sourceNodes: [],
      outputNodes: [],
    };
  }

  function setProofPathPredicateMatrixState(anchor) {
    document.querySelectorAll("[data-proof-path-predicate-step]").forEach((button) => {
      const selected = button.dataset.proofPathPredicateStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathPredicateMatrixAnchor = anchor || "";
  }

  function updateProofPathPredicateMatrixReadback(step, focus = null) {
    if (!proofPathPredicateMatrixReadback || !step) return;
    const record = proofPathPredicateRecord(step);
    const focusText = focus && focus.id ? ` · ${focus.kind === "wire" ? "连线" : "节点"} · ${focus.id}` : "";
    setText(
      proofPathPredicateMatrixReadback,
      `${step.anchor || "P035"} · ${record.gate} · ${record.expression} · 输出 ${record.output}${focusText}`,
    );
  }

  function applyProofPathPredicateMatrixStep(anchor) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathPredicateMatrixState(anchor);
    updateProofPathPredicateMatrixReadback(step);
    writeReviewHashState();
  }

  function applyProofPathPredicateMatrixFocus(anchor, kind, id) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step || !kind || !id) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathPredicateMatrixState(anchor);
    applyEmbeddedTraceFocus(kind, id);
    updateProofPathPredicateMatrixReadback(step, {kind, id});
  }

  function appendProofPathPredicateMatrixChips(container, anchor, label, values, kind = "") {
    const group = document.createElement("div");
    group.className = "demo-reconstruction-proof-path-predicate-matrix-group";
    const title = document.createElement("strong");
    title.textContent = label;
    const chips = document.createElement("div");
    chips.className = "demo-reconstruction-proof-path-predicate-matrix-chips";
    const list = Array.isArray(values) ? values : [];
    if (!list.length) {
      const empty = document.createElement("span");
      empty.textContent = "无";
      chips.appendChild(empty);
    } else {
      list.forEach((value) => {
        const chip = kind ? document.createElement("button") : document.createElement("span");
        chip.textContent = value;
        if (kind) {
          chip.type = "button";
          chip.dataset.proofPathPredicateFocusKind = kind;
          chip.dataset.proofPathPredicateFocusId = value;
          chip.addEventListener("click", () => applyProofPathPredicateMatrixFocus(anchor, kind, value));
        }
        chips.appendChild(chip);
      });
    }
    group.append(title, chips);
    container.appendChild(group);
  }

  function renderProofPathPredicateMatrix(steps) {
    if (!proofPathPredicateMatrixList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathPredicateMatrixList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathPredicateStep = "empty";
      empty.textContent = "等待判据矩阵";
      proofPathPredicateMatrixList.appendChild(empty);
      setText(proofPathPredicateMatrixStatus, "等待判据矩阵");
      setText(proofPathPredicateMatrixReadback, "等待选择判据矩阵。");
      return;
    }

    const finalContract = cumulativeTraceContract(items.length - 1);
    setText(
      proofPathPredicateMatrixStatus,
      `${items.length}/5 判据 · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );

    items.forEach((step, index) => {
      const record = proofPathPredicateRecord(step);
      const row = document.createElement("div");
      row.className = "demo-reconstruction-proof-path-predicate-matrix-row";
      row.dataset.proofPathPredicateRow = step.anchor || "";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-predicate-matrix-step";
      button.dataset.proofPathPredicateStep = step.anchor || "";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathPredicateMatrixStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const gate = document.createElement("span");
      gate.textContent = `${record.gate} · ${record.output}`;
      const expression = document.createElement("small");
      expression.textContent = record.expression;
      button.append(anchor, gate, expression);

      const focus = document.createElement("button");
      focus.type = "button";
      focus.className = "demo-reconstruction-proof-path-predicate-matrix-focus";
      focus.dataset.proofPathPredicateFocusKind = record.focusKind || "";
      focus.dataset.proofPathPredicateFocusId = record.focusId || "";
      focus.textContent = record.focusId || "等待焦点";
      focus.disabled = !record.focusKind || !record.focusId;
      focus.addEventListener("click", () => applyProofPathPredicateMatrixFocus(step.anchor || "", record.focusKind, record.focusId));

      const groups = document.createElement("div");
      groups.className = "demo-reconstruction-proof-path-predicate-matrix-groups";
      appendProofPathPredicateMatrixChips(groups, step.anchor || "", "输入", record.sourceNodes, "node");
      appendProofPathPredicateMatrixChips(groups, step.anchor || "", "输出", record.outputNodes, "node");
      appendProofPathPredicateMatrixChips(groups, step.anchor || "", "关键连线", record.focusId ? [record.focusId] : [], record.focusKind);

      row.append(button, focus, groups);
      proofPathPredicateMatrixList.appendChild(row);
    });

    const selectedAnchor = proofPathPredicateMatrixAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedStep = items.find((step) => step && step.anchor === selectedAnchor) || items[0];
    setProofPathPredicateMatrixState(selectedStep.anchor || "");
    updateProofPathPredicateMatrixReadback(selectedStep);
  }

  function proofPathBlueprintRecord(step, index) {
    const predicate = proofPathPredicateRecord(step);
    const contract = cumulativeTraceContract(index);
    const source = proofPathSourceRecords(step)[0] || {};
    const outputs = ladderMilestonesForStep(step);
    return {
      predicate,
      contract,
      sourceAnchor: source.anchor || "source",
      outputLabel: assemblyOutputLabelForStep(step, contract),
      outputs,
    };
  }

  function setProofPathBlueprintSummaryState(anchor) {
    document.querySelectorAll("[data-proof-path-blueprint-step]").forEach((button) => {
      const selected = button.dataset.proofPathBlueprintStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    proofPathBlueprintSummaryAnchor = anchor || "";
  }

  function updateProofPathBlueprintSummaryReadback(step) {
    if (!proofPathBlueprintSummaryReadback || !step) return;
    const index = traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    const safeIndex = index >= 0 ? index : 0;
    const record = proofPathBlueprintRecord(step, safeIndex);
    setText(
      proofPathBlueprintSummaryReadback,
      `${step.anchor || "P035"} · ${record.predicate.gate} · ${record.sourceAnchor} -> ${record.predicate.output} · ${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${record.outputLabel}`,
    );
  }

  function applyProofPathBlueprintSummaryStep(anchor) {
    const step = traceSteps.find((item) => item && item.anchor === anchor);
    if (!step) return;
    setSelectedTrace(step, {writeHash: false});
    setProofPathBlueprintSummaryState(anchor);
    updateProofPathBlueprintSummaryReadback(step);
    writeReviewHashState();
  }

  function renderProofPathBlueprintSummary(steps) {
    if (!proofPathBlueprintSummaryList) return;
    const items = Array.isArray(steps) ? steps : [];
    proofPathBlueprintSummaryList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.proofPathBlueprintStep = "empty";
      empty.textContent = "等待蓝图摘要";
      proofPathBlueprintSummaryList.appendChild(empty);
      setText(proofPathBlueprintSummaryStatus, "等待蓝图摘要");
      setText(proofPathBlueprintSummaryReadback, "等待选择蓝图摘要。");
      return;
    }

    const finalContract = cumulativeTraceContract(items.length - 1);
    setText(
      proofPathBlueprintSummaryStatus,
      `P035 -> demo.html · ${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`,
    );

    const chain = document.createElement("div");
    chain.className = "demo-reconstruction-proof-path-blueprint-chain";
    chain.dataset.proofPathBlueprintChain = "complete";
    chain.textContent = "L1 TLS -> L2 ETRAC -> L3 EEC/PLS/PDU -> VDT90 -> L4 THR_LOCK";
    proofPathBlueprintSummaryList.appendChild(chain);

    items.forEach((step, index) => {
      const record = proofPathBlueprintRecord(step, index);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-path-blueprint-step";
      button.dataset.proofPathBlueprintStep = step.anchor || "";
      button.dataset.proofPathBlueprintFinal = index === items.length - 1 ? "true" : "false";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyProofPathBlueprintSummaryStep(step.anchor || ""));

      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const path = document.createElement("span");
      path.textContent = `${record.sourceAnchor} -> ${record.predicate.gate} -> ${record.predicate.output}`;
      const counts = document.createElement("small");
      counts.textContent = `${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${record.outputLabel}`;
      const outputs = document.createElement("em");
      outputs.textContent = record.outputs.length ? record.outputs.join(" / ") : record.predicate.output;

      button.append(anchor, path, counts, outputs);
      proofPathBlueprintSummaryList.appendChild(button);
    });

    const selectedAnchor = proofPathBlueprintSummaryAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedStep = items.find((step) => step && step.anchor === selectedAnchor) || items[0];
    setProofPathBlueprintSummaryState(selectedStep.anchor || "");
    updateProofPathBlueprintSummaryReadback(selectedStep);
  }

  function circuitSnapshotRecord(step, index) {
    const safeIndex = Math.max(0, index);
    const contract = traceSteps.length ? cumulativeTraceContract(safeIndex) : {node_ids: [], wire_ids: []};
    const predicate = proofPathPredicateRecord(step);
    const source = proofPathSourceRecords(step)[0] || {};
    const outputs = ladderMilestonesForStep(step);
    const sourceAnchor = source.anchor || step.anchor || "P035";
    return {
      contract,
      predicate,
      sourceAnchor,
      sourceText: source.text || step.source_text || "",
      outputLabel: assemblyOutputLabelForStep(step, contract),
      outputs,
    };
  }

  function setCircuitSnapshotState(anchor) {
    document.querySelectorAll("[data-circuit-snapshot-step]").forEach((button) => {
      const selected = button.dataset.circuitSnapshotStep === anchor;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    circuitSnapshotAnchor = anchor || "";
  }

  function circuitSnapshotChainIdForStep(step) {
    const anchor = step && step.anchor ? step.anchor : "";
    if (anchor === "P035-S01") return "runway-l1-unlock";
    if (anchor === "P035-S02") return "runway-l2-power";
    if (anchor === "P035-S03") return "runway-l3-deploy";
    if (anchor === "P035-S04") return "runway-vdt90";
    if (anchor === "P035-S05") return "runway-l4-thr-lock";
    return "";
  }

  function circuitSnapshotChainRecords(finalContract) {
    const finalNodes = finalContract && Array.isArray(finalContract.node_ids) ? finalContract.node_ids : [];
    const finalWires = finalContract && Array.isArray(finalContract.wire_ids) ? finalContract.wire_ids : [];
    const outputLabel = finalNodes.length || finalWires.length
      ? `${finalNodes.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalWires.length}/${EXPECTED_WIRE_COUNT} 连线`
      : "等待完整电路";
    const runwayRecords = OPERATOR_RUNWAY_RECORDS.slice(0, 5).map((record) => ({
      id: record.id,
      order: record.order,
      anchor: record.anchor,
      label: record.title,
      detail: record.readback,
      output: record.output,
      focusKind: record.focusKind,
      focusId: record.focusId,
      variant: record.id === "runway-l4-thr-lock" ? "final" : "logic",
    }));
    return [
      {
        id: "docx-source",
        order: "00",
        anchor: "P035-S01",
        label: "DOCX 原句",
        detail: `${sourceEntries.length} 条源记录进入 P035 工作过程`,
        output: "逐句生成起点",
        focusKind: "",
        focusId: "",
        variant: "source",
      },
      ...runwayRecords,
      {
        id: "demo-output",
        order: "06",
        anchor: "P035-S05",
        label: "demo 输出",
        detail: outputLabel,
        output: "THR_LOCK / HUD / 状态输出可读",
        focusKind: "wire",
        focusId: "wire_logic4_thr_lock",
        variant: "output",
      },
    ];
  }

  function setCircuitSnapshotChainState(recordId) {
    document.querySelectorAll("[data-circuit-snapshot-chain-step]").forEach((button) => {
      const selected = button.dataset.circuitSnapshotChainStep === recordId;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    circuitSnapshotChainAnchor = recordId || "";
  }

  function applyCircuitSnapshotChainStep(recordId) {
    const finalContract = traceSteps.length ? cumulativeTraceContract(traceSteps.length - 1) : {node_ids: [], wire_ids: []};
    const record = circuitSnapshotChainRecords(finalContract).find((item) => item.id === recordId);
    if (!record) return;
    const step = traceSteps.find((item) => item && item.anchor === record.anchor);
    if (step) {
      setSelectedTrace(step, {writeHash: false});
    }
    if (record.focusKind && record.focusId) {
      applyEmbeddedTraceFocus(record.focusKind, record.focusId);
    } else {
      writeReviewHashState();
    }
    setCircuitSnapshotChainState(record.id);
    setText(circuitSnapshotReview, `${record.order} · ${record.label}`);
  }

  function renderCircuitSnapshotChain(finalContract) {
    if (!circuitSnapshotChain) return;
    if (!traceSteps.length) {
      circuitSnapshotChain.innerHTML = "";
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.circuitSnapshotChainStep = "empty";
      empty.setAttribute("aria-pressed", "false");
      empty.textContent = "等待闭环链路";
      circuitSnapshotChain.appendChild(empty);
      circuitSnapshotChainAnchor = "";
      return;
    }
    const records = circuitSnapshotChainRecords(finalContract);
    circuitSnapshotChain.innerHTML = "";
    records.forEach((record, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.circuitSnapshotChainStep = record.id;
      button.dataset.circuitSnapshotChainVariant = record.variant;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyCircuitSnapshotChainStep(record.id));

      const order = document.createElement("strong");
      order.textContent = record.order;
      const label = document.createElement("span");
      label.textContent = record.label;
      const detail = document.createElement("small");
      detail.textContent = record.detail;
      const output = document.createElement("em");
      output.textContent = record.output;
      button.append(order, label, detail, output);
      circuitSnapshotChain.appendChild(button);

      if (index < records.length - 1) {
        const connector = document.createElement("i");
        connector.className = "demo-reconstruction-circuit-snapshot-chain-connector";
        connector.setAttribute("aria-hidden", "true");
        connector.textContent = "->";
        circuitSnapshotChain.appendChild(connector);
      }
    });
    const selectedRecordId = circuitSnapshotChainAnchor
      || circuitSnapshotChainIdForStep(currentTraceStep)
      || records[1].id;
    setCircuitSnapshotChainState(selectedRecordId);
  }

  function updateCircuitSnapshotReadback(step, index = -1) {
    if (!circuitSnapshotReadback || !step) return;
    const safeIndex = index >= 0 ? index : traceSteps.findIndex((item) => item && item.anchor === step.anchor);
    const record = circuitSnapshotRecord(step, safeIndex >= 0 ? safeIndex : 0);
    setText(
      circuitSnapshotReadback,
      `${step.anchor || "P035"} · ${record.sourceAnchor} -> ${record.predicate.gate} -> ${record.predicate.output} · ${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${record.outputLabel}`,
    );
    setText(circuitSnapshotReview, `第 ${(safeIndex >= 0 ? safeIndex : 0) + 1} 步 · 可审`);
  }

  function applyCircuitSnapshotStep(anchor) {
    const index = traceSteps.findIndex((item) => item && item.anchor === anchor);
    if (index < 0) return;
    const step = traceSteps[index];
    setSelectedTrace(step, {writeHash: false});
    setProofPathLaneMode("blueprint", {writeHash: false});
    setCircuitSnapshotState(anchor);
    updateCircuitSnapshotReadback(step, index);
    writeReviewHashState();
  }

  function renderCircuitSnapshot(steps) {
    if (!circuitSnapshotList) return;
    const items = Array.isArray(steps) ? steps : [];
    circuitSnapshotList.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.dataset.circuitSnapshotStep = "empty";
      empty.setAttribute("aria-pressed", "false");
      empty.textContent = "等待步骤电路";
      circuitSnapshotList.appendChild(empty);
      setText(circuitSnapshotStatus, "等待电路");
      setText(circuitSnapshotSource, "等待来源");
      setText(circuitSnapshotCircuit, "等待电路");
      setText(circuitSnapshotOutput, "等待输出");
      setText(circuitSnapshotReview, "等待选择");
      setText(circuitSnapshotReadback, "等待生成完整电路。");
      renderCircuitSnapshotChain({node_ids: [], wire_ids: []});
      return;
    }

    const finalStep = items[items.length - 1] || {};
    const finalContract = cumulativeTraceContract(items.length - 1);
    const outputStatus = assemblyOutputLabelForStep(finalStep, finalContract)
      .replace("完整 demo 电路闭合", "完整电路闭合")
      .replace("THR_LOCK 输出可读", "反推锁可读");
    setText(circuitSnapshotStatus, `${items.length}/5 句 · 完整电路闭合`);
    setText(circuitSnapshotSource, `${sourceEntries.length} 条源记录 · ${items.length}/5 句`);
    setText(circuitSnapshotCircuit, `${finalContract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${finalContract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`);
    setText(circuitSnapshotOutput, `${OUTPUT_PATH_TARGETS.length}/5 输出 · ${outputStatus}`);
    renderCircuitSnapshotChain(finalContract);

    items.forEach((step, index) => {
      const record = circuitSnapshotRecord(step, index);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-circuit-snapshot-step";
      button.dataset.circuitSnapshotStep = step.anchor || "";
      button.dataset.circuitSnapshotFinal = index === items.length - 1 ? "true" : "false";
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => applyCircuitSnapshotStep(step.anchor || ""));

      const head = document.createElement("span");
      head.className = "demo-reconstruction-circuit-snapshot-step-head";
      const anchor = document.createElement("strong");
      anchor.textContent = step.anchor || `P035-S${String(index + 1).padStart(2, "0")}`;
      const title = document.createElement("em");
      title.textContent = step.title || "工作过程片段";
      head.append(anchor, title);

      const source = document.createElement("small");
      source.textContent = proofPathSourceExcerpt(record.sourceText || step.source_text || "", 86, proofPathSourceNeedle(step, record.sourceText));

      const path = document.createElement("span");
      path.textContent = `${record.sourceAnchor} -> ${record.predicate.gate} -> ${record.predicate.output}`;

      const counts = document.createElement("small");
      counts.textContent = `${record.contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点 · ${record.contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线 · ${record.outputLabel}`;

      const outputs = document.createElement("em");
      outputs.textContent = record.outputs.length ? record.outputs.join(" / ") : record.predicate.output;

      button.append(head, source, path, counts, outputs);
      circuitSnapshotList.appendChild(button);
    });

    const selectedAnchor = circuitSnapshotAnchor || (currentTraceStep && currentTraceStep.anchor) || items[0].anchor || "";
    const selectedIndex = items.findIndex((step) => step && step.anchor === selectedAnchor);
    const safeIndex = selectedIndex >= 0 ? selectedIndex : 0;
    setCircuitSnapshotState(items[safeIndex].anchor || "");
    updateCircuitSnapshotReadback(items[safeIndex], safeIndex);
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
    document.querySelectorAll("[data-proof-transcript-row]").forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        button.dataset.proofTranscriptRow === activeOperatorRunwayId ? "true" : "false",
      );
    });
    if (record) {
      setText(operatorRunwayStatus, `${record.order}/${String(OPERATOR_RUNWAY_RECORDS.length).padStart(2, "0")} · ${record.presetLabel}`);
      refreshOperatorRunwayReadback(record);
    } else {
      const readyCount = OPERATOR_RUNWAY_RECORDS.filter((item) => traceStepByAnchor(item.anchor)).length;
      setText(operatorRunwayStatus, `${readyCount}/${OPERATOR_RUNWAY_RECORDS.length} 可演示`);
      refreshOperatorRunwayReadback(null);
    }
    updateControlStripStatus();
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

  function proofTranscriptSourceText(record, step) {
    const sourceText = record.proofText || (step && step.source_text ? step.source_text : record.readback);
    return sourceText.length > 96 ? `${sourceText.slice(0, 96)}...` : sourceText;
  }

  function renderProofTranscript() {
    if (!proofTranscriptList) return;
    proofTranscriptList.innerHTML = "";
    const readyCount = OPERATOR_RUNWAY_RECORDS.filter((record) => traceStepByAnchor(record.anchor)).length;
    if (!OPERATOR_RUNWAY_RECORDS.length) {
      const empty = document.createElement("button");
      empty.type = "button";
      empty.className = "demo-reconstruction-proof-transcript-row";
      empty.dataset.proofTranscriptRow = "empty";
      empty.textContent = "讲解稿暂无数据";
      proofTranscriptList.appendChild(empty);
      setText(proofTranscriptSummary, "等待讲解");
      return;
    }

    OPERATOR_RUNWAY_RECORDS.forEach((record) => {
      const step = traceStepByAnchor(record.anchor);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "demo-reconstruction-proof-transcript-row";
      button.dataset.proofTranscriptRow = record.id;
      button.dataset.proofTranscriptAnchor = record.anchor;
      button.dataset.proofTranscriptPreset = record.presetId;
      button.dataset.proofTranscriptReady = step ? "true" : "false";
      button.setAttribute("aria-pressed", record.id === activeOperatorRunwayId ? "true" : "false");
      button.addEventListener("click", () => activateOperatorRunwayRecord(record));

      const head = document.createElement("div");
      head.className = "demo-reconstruction-proof-transcript-row-head";
      const order = document.createElement("span");
      order.textContent = record.order;
      const title = document.createElement("strong");
      title.textContent = record.title;
      const anchor = document.createElement("em");
      anchor.textContent = record.anchor;
      head.append(order, title, anchor);

      const quote = document.createElement("p");
      quote.textContent = proofTranscriptSourceText(record, step);

      const facts = document.createElement("div");
      facts.className = "demo-reconstruction-proof-transcript-facts";
      [
        `操作：${record.presetLabel}`,
        `输出：${record.output}`,
        `覆盖：${step ? (step.node_ids || []).length : 0} 节点 / ${step ? (step.wire_ids || []).length : 0} 连线`,
      ].forEach((value) => {
        const fact = document.createElement("span");
        fact.textContent = value;
        facts.appendChild(fact);
      });

      button.append(head, quote, facts);
      proofTranscriptList.appendChild(button);
    });
    setText(proofTranscriptSummary, `${readyCount}/${OPERATOR_RUNWAY_RECORDS.length} 段`);
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
      updateCompactRunwayFromFrame(null);
      updateCustodyOutputReadback();
      updateScenarioLedgerFromFrame();
      refreshOperatorRunwayReadback(operatorRunwayRecordById(activeOperatorRunwayId));
      updateControlStripStatus();
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
    updateCompactRunwayFromFrame(frameDocument);
    updateCustodyOutputReadback();
    updateScenarioLedgerFromFrame();
    refreshOperatorRunwayReadback(operatorRunwayRecordById(activeOperatorRunwayId));
    updateControlStripStatus();
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
    const reviewContext = {
      sourceCount,
      stepCount,
      expectedNodes,
      expectedWires,
      coveredNodes,
      coveredWires,
      finalContract,
      focusedObject,
      hasFocusedObject: Boolean(currentCircuitFocus.kind && currentCircuitFocus.id),
    };
    setText(reviewPacketReadiness, `${passed}/${gates.length} 验收`);
    renderReviewPacketGates(gates);
    renderReviewPacketDashboard(gates, reviewContext);
    updateReviewVerdictBoard(gates, reviewContext);
    renderReviewIndexHandoffRail();
    renderReviewIndexGateRail(gates);
    renderReviewIndexTourRail();
    renderReviewIndexEvidenceRail();
    renderReviewIndexClosureRail();
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

  function renderProofPathInspectorNeighbors(records) {
    if (!proofPathObjectInspectorNeighbors) return;
    proofPathObjectInspectorNeighbors.innerHTML = "";
    if (!records.length) {
      const empty = document.createElement("li");
      empty.textContent = "暂无上下游对象";
      proofPathObjectInspectorNeighbors.appendChild(empty);
      return;
    }
    records.slice(0, 4).forEach((record) => {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.proofPathInspectorFocusKind = record.kind;
      button.dataset.proofPathInspectorFocusId = record.id;
      const label = document.createElement("strong");
      label.textContent = record.label || reviewObjectLabel(record.kind, record.id);
      const meta = document.createElement("span");
      meta.textContent = record.meta || record.id;
      button.append(label, meta);
      button.addEventListener("click", () => applyProofPathInspectorJump(record.kind, record.id));
      li.appendChild(button);
      proofPathObjectInspectorNeighbors.appendChild(li);
    });
  }

  function applyProofPathInspectorJump(kind, id) {
    if (!kind || !id) return;
    applyEmbeddedTraceFocus(kind, id);
    if (currentTraceStep) updateProofPathStatus(currentTraceStep, {kind, id});
  }

  function renderProofPathObjectInspector(kind, id) {
    if (!proofPathObjectInspector) return;
    if (!kind || !id) {
      setText(proofPathObjectInspectorObject, "等待对象");
      setText(proofPathObjectInspectorSourceCount, "0 条 DOCX");
      setText(proofPathObjectInspectorStepCount, "0 步");
      setText(proofPathObjectInspectorEdgeCount, "0 上游 · 0 下游");
      setText(proofPathObjectInspectorCoverage, "等待覆盖");
      setText(proofPathObjectInspectorSummary, "选择证明路径对象后显示来源、步骤和上下游。");
      renderProofPathInspectorNeighbors([]);
      return;
    }
    const {sourceMatches, stepMatches} = objectProvenanceRecords(kind, id);
    const records = signalNeighborhoodRecords(kind, id);
    const neighborRecords = [...records.incoming, ...records.outgoing, ...records.adjacent];
    const firstStep = stepMatches[0] || currentTraceStep || {};
    const firstSource = sourceMatches[0] || {};
    const coverageText = kind === "wire"
      ? `1/${EXPECTED_WIRE_COUNT} 连线`
      : `1/${EXPECTED_NODE_COUNT} 节点`;
    const sourceAnchor = firstSource.anchor ? ` · ${firstSource.anchor}` : "";
    setText(proofPathObjectInspectorObject, reviewObjectLabel(kind, id));
    setText(proofPathObjectInspectorSourceCount, `${sourceMatches.length} 条 DOCX`);
    setText(proofPathObjectInspectorStepCount, `${stepMatches.length} 步`);
    setText(
      proofPathObjectInspectorEdgeCount,
      `${records.incoming.length} 上游 · ${records.outgoing.length} 下游 · ${records.adjacent.length} 相邻`,
    );
    setText(proofPathObjectInspectorCoverage, coverageText);
    setText(
      proofPathObjectInspectorSummary,
      `${firstStep.anchor || "P035"} · ${firstStep.title || "对象链路"}${sourceAnchor}`,
    );
    renderProofPathInspectorNeighbors(neighborRecords);
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
      renderProofPathObjectInspector("", "");
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
    renderProofPathObjectInspector(kind, id);
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
    if (!state.complete && !state.step && !state.focusId && !state.query && !state.topologyStep && !state.topologyQuery && !state.lane) {
      setProofPathLaneMode("blueprint", {writeHash: false});
      setCompleteModeBanner(false);
      updateReviewLink();
      return false;
    }
    applyingReviewHashState = true;
    try {
      if (state.complete) {
        applyReviewIndexCompleteState();
        updateReviewLink();
        return true;
      }
      setCompleteModeBanner(false);
      setProofPathLaneMode(state.lane || "blueprint", {writeHash: false});
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
    setReviewIndexEquationState(equation ? equation.id : "");
    const closureRecord = reviewIndexClosureRecords().find((record) => record.focusKind === kind && record.focusId === id);
    setReviewIndexClosureState(closureRecord ? closureRecord.id : "");
    document
      .querySelectorAll("[data-trace-focus-kind], [data-source-focus-kind], [data-proof-path-focus-kind], [data-proof-path-coverage-focus-kind], [data-proof-path-delta-focus-kind], [data-proof-path-sentence-focus-kind], [data-proof-path-predicate-focus-kind]")
      .forEach((button) => {
        const chipKind = button.dataset.traceFocusKind
          || button.dataset.sourceFocusKind
          || button.dataset.proofPathFocusKind
          || button.dataset.proofPathCoverageFocusKind
          || button.dataset.proofPathDeltaFocusKind
          || button.dataset.proofPathSentenceFocusKind
          || button.dataset.proofPathPredicateFocusKind
          || "";
        const chipId = button.dataset.traceFocusId
          || button.dataset.sourceFocusId
          || button.dataset.proofPathFocusId
          || button.dataset.proofPathCoverageFocusId
          || button.dataset.proofPathDeltaFocusId
          || button.dataset.proofPathSentenceFocusId
          || button.dataset.proofPathPredicateFocusId
          || "";
        const isCurrent = chipKind === kind && chipId === id;
        button.setAttribute("aria-pressed", isCurrent ? "true" : "false");
        button.dataset.reviewObjectSelected = isCurrent ? "true" : "false";
      });
    updateControlStripStatus();
  }

  function clearCircuitObjectFocus() {
    currentCircuitFocus = {kind: "", id: ""};
    setCoverageButtonTabStops("", "");
    resetTopologyReadback();
    setOutputPathWireState("");
    setOutputMaturityCellState("", "");
    setLogicEquationRowState("");
    setReviewIndexEquationState("");
    setReviewIndexClosureState("");
    renderObjectProvenance("", "");
    document
      .querySelectorAll("[data-trace-focus-kind], [data-source-focus-kind], [data-proof-path-focus-kind], [data-proof-path-coverage-focus-kind], [data-proof-path-delta-focus-kind], [data-proof-path-sentence-focus-kind], [data-proof-path-predicate-focus-kind]")
      .forEach((button) => {
        button.setAttribute("aria-pressed", "false");
        button.dataset.reviewObjectSelected = "false";
      });
    updateControlStripStatus();
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
    setReviewIndexBuildState(step.anchor || "");
    setCustodyButtonState(step.anchor);
    setText(selectedAnchor, step.anchor || "P035");
    setText(selectedTitle, step.title || "工作过程片段");
    setText(selectedText, step.source_text || "");
    renderInlineChips(selectedNodes, step.node_ids, "demo-reconstruction-node-chip", "无节点", "node");
    renderInlineChips(selectedWires, step.wire_ids, "demo-reconstruction-wire-chip", "无连线", "wire");
    renderInlineChips(selectedFolded, step.folded_predicates, "demo-reconstruction-folded-chip", "无折叠谓词");
    applyEmbeddedTraceHighlight(step);
    updateCustodyActiveReadback();
    updateControlStripStatus();
    updateSentenceRunnerStatus(step);
    updateProofPathStatus(step);
    setProofPathCoverageGridState(step.anchor || "");
    setProofPathDeltaRailState(step.anchor || "");
    setProofPathSourceRailState(step.anchor || "");
    setProofPathSentenceMatrixState(step.anchor || "");
    setProofPathPredicateMatrixState(step.anchor || "");
    setProofPathBlueprintSummaryState(step.anchor || "");
    setCircuitSnapshotState(step.anchor || "");
    setCircuitSnapshotChainState(circuitSnapshotChainIdForStep(step));
    if (selectedTraceIndex >= 0) {
      const contract = cumulativeTraceContract(selectedTraceIndex);
      updateProofPathCoverageGridReadback(step, contract);
      updateProofPathDeltaRailReadback(proofPathDeltaRecord(selectedTraceIndex));
      updateProofPathSourceRailReadback(step);
      updateProofPathSentenceMatrixReadback(step);
      updateProofPathPredicateMatrixReadback(step);
      updateProofPathBlueprintSummaryReadback(step);
      updateCircuitSnapshotReadback(step, selectedTraceIndex);
    }
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
    renderCircuitSnapshot(steps);
    renderReviewIndexBuildLadder(steps);
    renderSentenceRunner(steps);
    renderProofPathTimeline(steps);
    renderProofPathCoverageGrid(steps);
    renderProofPathDeltaRail(steps);
    renderProofPathSourceRail(steps);
    renderProofPathSentenceMatrix(steps);
    renderProofPathPredicateMatrix(steps);
    renderProofPathBlueprintSummary(steps);
    setProofPathLaneMode(proofPathLaneMode, {writeHash: false});
    renderStepPlaybackRail(steps);
    renderAssemblyMap(steps);
    renderCircuitCompletionLadder(steps);
    renderCustodyMatrix(steps);
    renderTopologyStepFilter(steps);
    renderTopologyMatrix();
    renderOutputMaturityMatrix(steps);
    renderOperatorRunway();
    renderReviewIndexScenarioRail();
    renderProofTranscript();
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
    sourceEntries = Array.isArray(payload && payload.source_entries) ? payload.source_entries : [];
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
  if (reviewIndexCompleteAction) {
    reviewIndexCompleteAction.addEventListener("click", applyReviewIndexCompleteState);
  }
  installControlStripActions();
  installScenarioComparatorActions();
  installCompactRunwayActions();
  proofPathLaneModeButtons.forEach((button) => {
    button.addEventListener("click", () => setProofPathLaneMode(button.dataset.proofPathLaneMode || "blueprint", {writeHash: true}));
  });
  setProofPathLaneMode(proofPathLaneMode, {writeHash: false});
  updateReviewIndexStatus();
  updateControlStripStatus();
  updateScenarioComparatorStatus("");
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
      renderCircuit(stored, "本地草稿已读取");
      return;
    }
    try {
      const replay = await loadReplayCircuit();
      if (replay) {
        renderCircuit(replay, "基准控制台已读取");
        return;
      }
    } catch (error) {
      // Keep the static acceptance text visible; the page remains read-only.
    }
    renderCircuit({nodes: [], wires: []}, "等待电路数据");
  }

  boot();
})();

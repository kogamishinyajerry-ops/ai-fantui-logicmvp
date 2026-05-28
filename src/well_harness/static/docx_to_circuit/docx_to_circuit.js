(function () {
  "use strict";

  const DOCX_MAP_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;
  const DEFAULT_STEP_ANCHOR = "P035-S05";

  const NODE_LABELS = {
    aircraft_on_ground: "GND",
    eec_deploy: "EEC DEPLOY",
    eec_enable: "EEC ENABLE",
    engine_running: "ENGINE",
    etrac_540v: "ETRAC 540V",
    logic1: "L1",
    logic2: "L2",
    logic3: "L3",
    logic4: "L4",
    n1k: "N1K",
    pdu_motor: "PDU MOTOR",
    pls_power: "PLS POWER",
    radio_altitude_ft: "RA < 6 ft",
    reverser_inhibited: "!INHIBIT",
    sw1: "SW1",
    sw2: "SW2",
    thr_lock: "THR_LOCK",
    tls115: "TLS 115VAC",
    tls_unlocked: "TLS UNLOCK",
    vdt90: "VDT90",
  };

  const LOGIC_IDS = ["logic1", "logic2", "logic3", "logic4"];
  const TRACE_KIND_LABELS = {node: "节点", wire: "线束"};
  const DEMO_SCENARIOS = {
    "P035-S01": {
      label: "L1 / TLS 解锁",
      controls: {tra: -4, ra: 2, n1k: 35, vdt: 0, engineRunning: true, aircraftOnGround: true, reverserInhibited: false, eecEnable: true},
    },
    "P035-S02": {
      label: "L2 / ETRAC 供电",
      controls: {tra: -8, ra: 2, n1k: 35, vdt: 0, engineRunning: true, aircraftOnGround: true, reverserInhibited: false, eecEnable: true},
    },
    "P035-S03": {label: "L3 展开链路", preset: "landing-deploy"},
    "P035-S04": {
      label: "VDT90 展开反馈",
      controls: {tra: -14, ra: 2, n1k: 45, vdt: 90, engineRunning: true, aircraftOnGround: true, reverserInhibited: false, eecEnable: true},
    },
    "P035-S05": {label: "最大反推（展开到位）", preset: "max-reverse"},
  };

  const CIRCUIT_NODES = [
    {id: "sw1", label: "SW1", sub: "TRA -1.4..-6.2", kind: "input", x: 10, y: 40, width: 160, height: 28},
    {id: "aircraft_on_ground", label: "GND", sub: "on ground", kind: "input", x: 10, y: 76, width: 160, height: 28},
    {id: "radio_altitude_ft", label: "RA < 6 ft", sub: "radio altitude", kind: "input", x: 10, y: 112, width: 160, height: 28},
    {id: "sw2", label: "SW2", sub: "TRA -5..-9.8", kind: "input", x: 10, y: 156, width: 160, height: 28},
    {id: "engine_running", label: "ENGINE", sub: "running", kind: "input", x: 10, y: 192, width: 160, height: 28},
    {id: "n1k", label: "N1K", sub: "< deploy limit", kind: "input", x: 10, y: 234, width: 160, height: 28},
    {id: "eec_enable", label: "EEC ENABLE", sub: "enable", kind: "input", x: 10, y: 270, width: 160, height: 28},
    {id: "reverser_inhibited", label: "!INHIBIT", sub: "not inhibited", kind: "input", x: 10, y: 306, width: 160, height: 28},
    {id: "logic1", label: "L1", sub: "TLS power", kind: "logic", x: 260, y: 70, width: 160, height: 38},
    {id: "logic2", label: "L2", sub: "ETRAC power", kind: "logic", x: 260, y: 170, width: 160, height: 38},
    {id: "logic3", label: "L3", sub: "deploy chain", kind: "logic", x: 260, y: 260, width: 160, height: 50},
    {id: "tls115", label: "TLS 115VAC", sub: "cmd", kind: "component", x: 500, y: 56, width: 160, height: 28},
    {id: "tls_unlocked", label: "TLS UNLOCK", sub: "limit switch", kind: "component", x: 500, y: 92, width: 160, height: 28},
    {id: "vdt90", label: "VDT90", sub: ">= 90%", kind: "component", x: 500, y: 128, width: 160, height: 28},
    {id: "etrac_540v", label: "ETRAC 540V", sub: "cmd", kind: "component", x: 500, y: 156, width: 160, height: 28},
    {id: "eec_deploy", label: "EEC DEPLOY", sub: "cmd", kind: "output", x: 500, y: 246, width: 160, height: 28},
    {id: "pls_power", label: "PLS POWER", sub: "power", kind: "output", x: 500, y: 282, width: 160, height: 28},
    {id: "pdu_motor", label: "PDU MOTOR", sub: "motor cmd", kind: "output", x: 500, y: 318, width: 160, height: 28},
    {id: "logic4", label: "L4", sub: "VDT90 + L3", kind: "logic", x: 720, y: 130, width: 160, height: 38},
    {id: "thr_lock", label: "THR_LOCK", sub: "release", kind: "output", x: 720, y: 200, width: 160, height: 34},
  ];

  const CIRCUIT_EDGES = [
    {id: "wire_sw1_logic1", source: "sw1", target: "logic1", route: [[170, 54], [232, 54], [232, 78], [260, 78]]},
    {id: "wire_ground_logic2", source: "aircraft_on_ground", target: "logic2", route: [[170, 90], [238, 90], [238, 184], [260, 184]]},
    {id: "wire_ra_logic1", source: "radio_altitude_ft", target: "logic1", route: [[170, 126], [232, 126], [232, 98], [260, 98]]},
    {id: "wire_logic1_tls115", source: "logic1", target: "tls115", route: [[420, 89], [460, 89], [460, 70], [500, 70]]},
    {id: "wire_tls115_tls_unlocked", source: "tls115", target: "tls_unlocked", route: [[580, 84], [580, 92]]},
    {id: "wire_sw2_logic2", source: "sw2", target: "logic2", route: [[170, 170], [234, 170], [234, 180], [260, 180]]},
    {id: "wire_engine_logic2", source: "engine_running", target: "logic2", route: [[170, 206], [234, 206], [234, 196], [260, 196]]},
    {id: "wire_tls_unlocked_logic3", source: "tls_unlocked", target: "logic3", route: [[660, 106], [702, 106], [702, 28], [246, 28], [246, 276], [260, 276]]},
    {id: "wire_logic2_etrac", source: "logic2", target: "etrac_540v", route: [[420, 189], [460, 189], [460, 170], [500, 170]]},
    {id: "wire_n1k_logic3", source: "n1k", target: "logic3", route: [[170, 248], [230, 248], [230, 270], [260, 270]]},
    {id: "wire_eec_logic2", source: "eec_enable", target: "logic2", route: [[170, 284], [240, 284], [240, 200], [260, 200]]},
    {id: "wire_engine_logic3", source: "engine_running", target: "logic3", route: [[170, 206], [244, 206], [244, 281], [260, 281]]},
    {id: "wire_ground_logic3", source: "aircraft_on_ground", target: "logic3", route: [[170, 90], [244, 90], [244, 290], [260, 290]]},
    {id: "wire_inh_logic1", source: "reverser_inhibited", target: "logic1", route: [[170, 320], [226, 320], [226, 88], [260, 88]]},
    {id: "wire_inh_logic2", source: "reverser_inhibited", target: "logic2", route: [[226, 188], [260, 188]]},
    {id: "wire_inh_logic3", source: "reverser_inhibited", target: "logic3", route: [[226, 304], [260, 304]]},
    {id: "wire_logic3_eec", source: "logic3", target: "eec_deploy", route: [[420, 279], [465, 279], [465, 260], [500, 260]]},
    {id: "wire_logic3_pls", source: "logic3", target: "pls_power", route: [[465, 279], [465, 296], [500, 296]]},
    {id: "wire_logic3_pdu", source: "logic3", target: "pdu_motor", route: [[465, 296], [465, 332], [500, 332]]},
    {id: "wire_pdu_vdt90", source: "pdu_motor", target: "vdt90", route: [[660, 332], [690, 332], [690, 142], [660, 142]]},
    {id: "wire_vdt90_logic4", source: "vdt90", target: "logic4", route: [[660, 142], [720, 142]]},
    {id: "wire_logic3_logic4", source: "logic3", target: "logic4", route: [[420, 298], [440, 298], [440, 368], [690, 368], [690, 162], [720, 162]]},
    {id: "wire_logic4_thr_lock", source: "logic4", target: "thr_lock", route: [[800, 168], [800, 200]]},
  ];

  const $ = (id) => document.getElementById(id);
  const sourcePath = $("docx-circuit-source-path");
  const sourceCount = $("docx-circuit-source-count");
  const nodeCount = $("docx-circuit-node-count");
  const wireCount = $("docx-circuit-wire-count");
  const sequenceCount = $("docx-circuit-sequence-count");
  const sequenceList = $("docx-circuit-sequence-list");
  const activeAnchor = $("docx-circuit-active-anchor");
  const reviewPanel = $("docx-circuit-review-panel");
  const prevStepButton = $("docx-circuit-prev-step");
  const nextStepButton = $("docx-circuit-next-step");
  const stepPosition = $("docx-circuit-step-position");
  const evidenceOnlyToggle = $("docx-circuit-element-evidence-only");
  const copyTracePacketButton = $("docx-circuit-copy-trace-packet");
  const copyStatus = $("docx-circuit-copy-status");
  const sourceAnchor = $("docx-circuit-source-anchor");
  const sourceTitle = $("docx-circuit-source-title");
  const sourceText = $("docx-circuit-source-text");
  const tracePanel = $("docx-circuit-trace-panel");
  const traceSelectedId = $("docx-circuit-trace-selected-id");
  const traceType = $("docx-circuit-trace-type");
  const traceLogicLevel = $("docx-circuit-trace-logic-level");
  const traceFolded = $("docx-circuit-trace-folded");
  const traceEvidenceList = $("docx-circuit-trace-evidence-list");
  const logicLadder = $("docx-circuit-logic-ladder");
  const circuitSvg = $("docx-circuit-svg");
  const circuitSvgSummary = $("docx-circuit-svg-summary");
  const nodeGrid = $("docx-circuit-node-grid");
  const wireGrid = $("docx-circuit-wire-grid");
  const demoFrame = $("docx-circuit-demo-frame");
  const demoScenario = $("docx-circuit-demo-scenario");
  const demoSyncStatus = $("docx-circuit-demo-sync-status");
  let currentPayload = null;
  let currentAnchor = DEFAULT_STEP_ANCHOR;
  let selectedElement = {kind: "wire", id: "wire_logic4_thr_lock"};

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function appendChips(container, values, kind) {
    if (!Array.isArray(values) || values.length === 0) return;
    const row = document.createElement("div");
    row.className = "docx-circuit-chip-row";
    values.forEach((value) => {
      const chip = document.createElement("span");
      chip.className = "docx-circuit-chip";
      chip.dataset.kind = kind;
      chip.textContent = value;
      row.appendChild(chip);
    });
    container.appendChild(row);
  }

  function listFrom(values) {
    return Array.isArray(values) ? values.filter(Boolean) : [];
  }

  function sequenceSteps() {
    return currentPayload && Array.isArray(currentPayload.sequence_steps)
      ? currentPayload.sequence_steps
      : [];
  }

  function currentStepIndex() {
    const steps = sequenceSteps();
    return Math.max(0, steps.findIndex((step) => step.anchor === currentAnchor));
  }

  function currentStep() {
    const steps = sequenceSteps();
    return steps[currentStepIndex()] || null;
  }

  function cumulativeIds(steps, activeIndex, key) {
    const ids = new Set();
    steps.slice(0, activeIndex + 1).forEach((step) => {
      listFrom(step[key]).forEach((id) => ids.add(id));
    });
    return ids;
  }

  function contractIds(payload, key, fallback) {
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    return listFrom(contract[key]).length > 0 ? listFrom(contract[key]) : fallback;
  }

  function makeSvgElement(name, attributes) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.entries(attributes || {}).forEach(([key, value]) => {
      element.setAttribute(key, String(value));
    });
    return element;
  }

  function routePath(route) {
    if (!Array.isArray(route) || route.length === 0) return "";
    return route
      .map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x} ${y}`)
      .join(" ");
  }

  function routeHitPoint(route) {
    const points = Array.isArray(route) ? route : [];
    if (points.length === 0) return {cx: 0, cy: 0};
    let best = {length: -1, start: points[0], end: points[0]};
    for (let index = 0; index < points.length - 1; index += 1) {
      const start = points[index];
      const end = points[index + 1];
      const length = Math.abs(end[0] - start[0]) + Math.abs(end[1] - start[1]);
      if (length > best.length) best = {length, start, end};
    }
    return {
      cx: (best.start[0] + best.end[0]) / 2,
      cy: (best.start[1] + best.end[1]) / 2,
    };
  }

  function circuitNodeById(id) {
    return CIRCUIT_NODES.find((node) => node.id === id) || null;
  }

  function circuitEdgeById(id) {
    return CIRCUIT_EDGES.find((edge) => edge.id === id) || null;
  }

  function relatedNodeIds(kind, id) {
    if (kind === "node") return [id];
    const edge = circuitEdgeById(id);
    return edge ? [edge.source, edge.target] : [];
  }

  function matchingSteps(kind, id) {
    const steps = currentPayload && Array.isArray(currentPayload.sequence_steps)
      ? currentPayload.sequence_steps
      : [];
    const key = kind === "wire" ? "wire_ids" : "node_ids";
    return steps.filter((step) => listFrom(step[key]).includes(id));
  }

  function matchingSourceEntries(kind, id) {
    const entries = currentPayload && Array.isArray(currentPayload.source_entries)
      ? currentPayload.source_entries
      : [];
    const nodeIds = relatedNodeIds(kind, id);
    return entries.filter((entry) => listFrom(entry.node_ids).some((nodeId) => nodeIds.includes(nodeId)));
  }

  function sourceEntriesForNodes(nodeIds) {
    const entries = currentPayload && Array.isArray(currentPayload.source_entries)
      ? currentPayload.source_entries
      : [];
    const ids = new Set(listFrom(nodeIds));
    return entries.filter((entry) => listFrom(entry.node_ids).some((nodeId) => ids.has(nodeId)));
  }

  function activeStepSourceEntries() {
    const step = currentStep();
    return step ? sourceEntriesForNodes(step.node_ids) : [];
  }

  function logicLevelsForElement(kind, id, entries, steps) {
    const values = new Set();
    relatedNodeIds(kind, id).forEach((nodeId) => {
      if (LOGIC_IDS.includes(nodeId)) values.add(nodeId.replace("logic", "L"));
    });
    entries.forEach((entry) => {
      const match = String(entry.role || "").match(/L[1-4]/);
      if (match) values.add(match[0]);
    });
    steps.forEach((step) => {
      const match = `${step.title || ""} ${step.source_text || ""}`.match(/L[1-4]/);
      if (match) values.add(match[0]);
    });
    return Array.from(values).sort();
  }

  function foldedPredicatesForSteps(steps) {
    const values = new Set();
    steps.forEach((step) => {
      listFrom(step.folded_predicates).forEach((predicate) => values.add(predicate));
    });
    return Array.from(values);
  }

  function elementLabel(kind, id) {
    if (kind === "wire") {
      const edge = circuitEdgeById(id);
      return edge ? `${id} · ${edge.source} -> ${edge.target}` : id;
    }
    const node = circuitNodeById(id);
    return node ? `${node.label} · ${node.id}` : id;
  }

  function setSelectedElementState(kind, id) {
    if (circuitSvg) {
      circuitSvg.dataset.selectedElementType = kind;
      circuitSvg.dataset.selectedElementId = id;
      circuitSvg.querySelectorAll("[data-node-id], [data-wire-id]").forEach((item) => {
        const itemKind = item.dataset.nodeId ? "node" : "wire";
        const itemId = item.dataset.nodeId || item.dataset.wireId || "";
        item.dataset.selected = itemKind === kind && itemId === id ? "true" : "false";
      });
    }
    [nodeGrid, wireGrid].forEach((grid) => {
      if (!grid) return;
      grid.querySelectorAll(".docx-circuit-contract-chip").forEach((item) => {
        const itemKind = item.dataset.nodeId ? "node" : "wire";
        const itemId = item.dataset.nodeId || item.dataset.wireId || "";
        item.dataset.selected = itemKind === kind && itemId === id ? "true" : "false";
      });
    });
  }

  function appendEvidenceItem(anchor, role, text, sourceKind) {
    if (!traceEvidenceList) return;
    const item = document.createElement("li");
    const label = document.createElement("strong");
    label.textContent = `${anchor} · ${role}`;
    const body = document.createElement("span");
    body.textContent = text;
    item.dataset.sourceKind = sourceKind;
    item.appendChild(label);
    item.appendChild(body);
    traceEvidenceList.appendChild(item);
  }

  function traceEvidenceForElement(kind, id) {
    const selectedOnly = !evidenceOnlyToggle || evidenceOnlyToggle.checked;
    if (selectedOnly) {
      return {
        scope: "selected_element",
        steps: matchingSteps(kind, id),
        entries: matchingSourceEntries(kind, id).slice(0, 4),
      };
    }
    const step = currentStep();
    return {
      scope: "active_sentence",
      steps: step ? [step] : matchingSteps(kind, id),
      entries: activeStepSourceEntries().slice(0, 6),
    };
  }

  function renderTracePanel(kind, id) {
    const evidence = traceEvidenceForElement(kind, id);
    const steps = evidence.steps;
    const entries = evidence.entries;
    const logicLevels = logicLevelsForElement(kind, id, entries, steps);
    const folded = foldedPredicatesForSteps(steps);

    if (tracePanel) {
      tracePanel.setAttribute("data-selected-element-type", kind);
      tracePanel.setAttribute("data-selected-element-id", id);
      tracePanel.setAttribute("data-evidence-scope", evidence.scope);
    }
    setText(traceSelectedId, elementLabel(kind, id));
    setText(traceType, TRACE_KIND_LABELS[kind] || kind);
    setText(traceLogicLevel, logicLevels.length > 0 ? logicLevels.join(" / ") : "动作链路");
    setText(traceFolded, folded.length > 0 ? folded.join("；") : "无折叠谓词");

    if (!traceEvidenceList) return;
    traceEvidenceList.innerHTML = "";
    steps.forEach((step) => {
      appendEvidenceItem(step.anchor || "P035", step.title || "P035 步骤", step.source_text || "", "sequence_step");
    });
    entries.forEach((entry) => {
      appendEvidenceItem(entry.anchor || "DOCX", entry.role || "源文档条目", entry.text || "", "source_entry");
    });
    if (traceEvidenceList.children.length === 0) {
      appendEvidenceItem("未映射", "无直接 DOCX/P035 证据", "当前选择没有命中可展示证据。", "empty");
    }
  }

  function selectCircuitElement(kind, id) {
    selectedElement = {kind, id};
    setSelectedElementState(kind, id);
    renderTracePanel(kind, id);
  }

  function installElementInteraction(element, kind, id, label) {
    element.setAttribute("role", "button");
    element.setAttribute("tabindex", "0");
    element.setAttribute("aria-label", `反查 ${TRACE_KIND_LABELS[kind] || kind} ${label || id}`);
    element.addEventListener("click", () => selectCircuitElement(kind, id));
    element.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      selectCircuitElement(kind, id);
    });
  }

  function renderSubcircuit() {
    if (!circuitSvg || circuitSvg.dataset.rendered === "true") return;
    circuitSvg.innerHTML = "";
    circuitSvg.dataset.nodeCount = String(CIRCUIT_NODES.length);
    circuitSvg.dataset.wireCount = String(CIRCUIT_EDGES.length);
    setText(circuitSvgSummary, `${CIRCUIT_NODES.length} 节点 · ${CIRCUIT_EDGES.length} 连线`);

    const defs = makeSvgElement("defs");
    const marker = makeSvgElement("marker", {
      id: "docx-circuit-arrow",
      markerWidth: 8,
      markerHeight: 8,
      refX: 7,
      refY: 4,
      orient: "auto",
    });
    marker.appendChild(makeSvgElement("path", {d: "M0,0 L8,4 L0,8 Z"}));
    defs.appendChild(marker);
    circuitSvg.appendChild(defs);

    const wireGroup = makeSvgElement("g", {class: "docx-circuit-svg-wires"});
    CIRCUIT_EDGES.forEach((edge) => {
      const pathData = routePath(edge.route);
      const path = makeSvgElement("path", {
        class: "docx-circuit-svg-wire",
        d: pathData,
        "data-wire-id": edge.id,
        "data-source-node": edge.source,
        "data-target-node": edge.target,
        "data-highlight": "idle",
        "data-current-step-match": "false",
        "marker-end": "url(#docx-circuit-arrow)",
      });
      installElementInteraction(path, "wire", edge.id, `${edge.source} -> ${edge.target}`);
      wireGroup.appendChild(path);
      const hitPoint = routeHitPoint(edge.route);
      const hitBox = makeSvgElement("circle", {
        class: "docx-circuit-svg-wire-hit",
        "data-wire-hit-id": edge.id,
        cx: hitPoint.cx,
        cy: hitPoint.cy,
        r: 10,
      });
      installElementInteraction(hitBox, "wire", edge.id, `${edge.source} -> ${edge.target}`);
      wireGroup.appendChild(hitBox);
    });
    circuitSvg.appendChild(wireGroup);

    const nodeGroup = makeSvgElement("g", {class: "docx-circuit-svg-nodes"});
    CIRCUIT_NODES.forEach((node) => {
      const group = makeSvgElement("g", {
        class: "docx-circuit-svg-node",
        transform: `translate(${node.x} ${node.y})`,
        "data-node-id": node.id,
        "data-node-kind": node.kind,
        "data-highlight": "idle",
        "data-current-step-match": "false",
      });
      group.appendChild(makeSvgElement("rect", {width: node.width, height: node.height, rx: node.kind === "logic" ? 5 : 4}));
      const label = makeSvgElement("text", {
        x: node.width / 2,
        y: node.height > 34 ? 16 : 18,
        "text-anchor": "middle",
        class: "docx-circuit-svg-node-label",
      });
      label.textContent = node.label;
      group.appendChild(label);
      if (node.sub) {
        const sub = makeSvgElement("text", {
          x: node.width / 2,
          y: node.height > 34 ? 31 : 0,
          "text-anchor": "middle",
          class: "docx-circuit-svg-node-sub",
        });
        sub.textContent = node.sub;
        if (node.height > 34) group.appendChild(sub);
      }
      installElementInteraction(group, "node", node.id, node.label);
      nodeGroup.appendChild(group);
    });
    circuitSvg.appendChild(nodeGroup);
    circuitSvg.dataset.rendered = "true";
  }

  function setSvgHighlights(cumulativeNodes, currentNodes, cumulativeWires, currentWires) {
    if (!circuitSvg) return;
    circuitSvg.dataset.activeNodeCount = String(cumulativeNodes.size);
    circuitSvg.dataset.activeWireCount = String(cumulativeWires.size);
    circuitSvg.querySelectorAll("[data-node-id]").forEach((item) => {
      const id = item.dataset.nodeId;
      item.dataset.highlight = cumulativeNodes.has(id) ? "active" : "idle";
      item.dataset.currentStepMatch = currentNodes.has(id) ? "true" : "false";
    });
    circuitSvg.querySelectorAll("[data-wire-id]").forEach((item) => {
      const id = item.dataset.wireId;
      item.dataset.highlight = cumulativeWires.has(id) ? "active" : "idle";
      item.dataset.currentStepMatch = currentWires.has(id) ? "true" : "false";
    });
  }

  function renderContractGrid(container, ids, kind) {
    if (!container) return;
    container.innerHTML = "";
    ids.forEach((id) => {
      const item = document.createElement("span");
      item.className = "docx-circuit-contract-chip";
      item.dataset[`${kind}Id`] = id;
      item.dataset.highlight = "idle";
      item.textContent = kind === "node" ? (NODE_LABELS[id] || id) : id;
      item.title = id;
      container.appendChild(item);
    });
  }

  function setGridHighlights(container, kind, cumulative, current) {
    if (!container) return;
    container.querySelectorAll(".docx-circuit-contract-chip").forEach((item) => {
      const id = item.dataset[`${kind}Id`];
      item.dataset.highlight = cumulative.has(id) ? "active" : "idle";
      item.dataset.currentStepMatch = current.has(id) ? "true" : "false";
    });
  }

  function setLogicHighlights(cumulative, current) {
    if (!logicLadder) return;
    LOGIC_IDS.forEach((id) => {
      const item = logicLadder.querySelector(`[data-logic-id="${id}"]`);
      if (!item) return;
      item.dataset.highlight = cumulative.has(id) ? "active" : "idle";
      item.dataset.currentStepMatch = current.has(id) ? "true" : "false";
    });
  }

  function writeInput(doc, id, value, eventName) {
    const input = doc.getElementById(id);
    if (!input) return false;
    if (input.type === "checkbox") input.checked = Boolean(value);
    else input.value = String(value);
    input.dispatchEvent(new Event(eventName, {bubbles: true}));
    return true;
  }

  function applyDemoScenario(step) {
    const scenario = DEMO_SCENARIOS[step.anchor] || DEMO_SCENARIOS[DEFAULT_STEP_ANCHOR];
    setText(demoScenario, scenario.label);
    if (!demoFrame || !demoFrame.contentDocument) {
      setText(demoSyncStatus, "等待 iframe 加载");
      return;
    }
    const doc = demoFrame.contentDocument;
    const presetButton = scenario.preset
      ? doc.querySelector(`.fan-preset-btn[data-preset="${scenario.preset}"]`)
      : null;
    if (presetButton) {
      presetButton.click();
      setText(demoSyncStatus, `已同步 ${scenario.label}`);
      demoFrame.dataset.activeScenario = scenario.preset;
      return;
    }
    const controls = scenario.controls || {};
    writeInput(doc, "fan-tra-lever", controls.tra, "input");
    writeInput(doc, "fan-ra", controls.ra, "input");
    writeInput(doc, "fan-n1k", controls.n1k, "input");
    writeInput(doc, "fan-vdt", controls.vdt, "input");
    writeInput(doc, "fan-engine-running", controls.engineRunning, "change");
    writeInput(doc, "fan-aircraft-on-ground", controls.aircraftOnGround, "change");
    writeInput(doc, "fan-reverser-inhibited", controls.reverserInhibited, "change");
    writeInput(doc, "fan-eec-enable", controls.eecEnable, "change");
    setText(demoSyncStatus, `已同步 ${scenario.label}`);
    demoFrame.dataset.activeScenario = step.anchor;
  }

  function setReviewNavigationState(activeIndex, steps) {
    const count = Array.isArray(steps) ? steps.length : 0;
    setText(stepPosition, count > 0 ? `${activeIndex + 1} / ${count}` : "0 / 0");
    if (prevStepButton) prevStepButton.disabled = count === 0 || activeIndex <= 0;
    if (nextStepButton) nextStepButton.disabled = count === 0 || activeIndex >= count - 1;
  }

  function primaryElementForStep(step) {
    const wires = listFrom(step && step.wire_ids);
    if (wires.length > 0) return {kind: "wire", id: wires[wires.length - 1]};
    const nodes = listFrom(step && step.node_ids);
    if (nodes.length > 0) return {kind: "node", id: nodes[nodes.length - 1]};
    return selectedElement;
  }

  function activateRelativeStep(delta) {
    const steps = sequenceSteps();
    if (steps.length === 0) return;
    const nextIndex = Math.min(steps.length - 1, Math.max(0, currentStepIndex() + delta));
    activateStep(steps[nextIndex].anchor, {selectStepElement: true});
  }

  function currentTracePacket() {
    const step = currentStep();
    const evidence = traceEvidenceForElement(selectedElement.kind, selectedElement.id);
    const logicLevels = logicLevelsForElement(selectedElement.kind, selectedElement.id, evidence.entries, evidence.steps);
    return {
      kind: "docx_circuit_review_packet",
      source: {
        path: sourcePath ? sourcePath.textContent.trim() : "",
        anchor: step ? step.anchor : currentAnchor,
        title: step ? step.title : "",
        text: step ? step.source_text : "",
      },
      selected_element: {
        type: selectedElement.kind,
        id: selectedElement.id,
        label: elementLabel(selectedElement.kind, selectedElement.id),
        logic_levels: logicLevels,
        folded_predicates: foldedPredicatesForSteps(evidence.steps),
      },
      evidence_scope: evidence.scope,
      evidence: {
        p035: evidence.steps.map((item) => ({
          anchor: item.anchor,
          title: item.title,
          text: item.source_text,
        })),
        docx: evidence.entries.map((item) => ({
          anchor: item.anchor,
          role: item.role,
          text: item.text,
        })),
      },
      circuit: {
        nodes: listFrom(step && step.node_ids),
        wires: listFrom(step && step.wire_ids),
      },
      boundary: {
        truth_effect: "none",
        certification_claim: "none",
      },
    };
  }

  async function copyText(value) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(value);
      return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "true");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand("copy");
    document.body.removeChild(textarea);
    if (!copied) throw new Error("copy failed");
  }

  async function copyTracePacket() {
    if (!copyTracePacketButton) return;
    copyTracePacketButton.dataset.copyState = "pending";
    setText(copyStatus, "复制中");
    try {
      await copyText(JSON.stringify(currentTracePacket(), null, 2));
      copyTracePacketButton.dataset.copyState = "success";
      setText(copyStatus, "已复制");
    } catch (error) {
      copyTracePacketButton.dataset.copyState = "failed";
      setText(copyStatus, "复制失败");
    }
  }

  function activateStep(anchor, options) {
    const steps = sequenceSteps();
    if (steps.length === 0) return;
    const activeIndex = Math.max(0, steps.findIndex((step) => step.anchor === anchor));
    const step = steps[activeIndex];
    currentAnchor = step.anchor;
    const currentNodes = new Set(listFrom(step.node_ids));
    const currentWires = new Set(listFrom(step.wire_ids));
    const cumulativeNodes = cumulativeIds(steps, activeIndex, "node_ids");
    const cumulativeWires = cumulativeIds(steps, activeIndex, "wire_ids");

    setText(activeAnchor, step.anchor);
    setText(sourceAnchor, step.anchor);
    setText(sourceTitle, step.title || "");
    setText(sourceText, step.source_text || "");
    if (reviewPanel) reviewPanel.dataset.activeAnchor = step.anchor;
    if (demoFrame) demoFrame.dataset.activeSequenceAnchor = step.anchor;
    setGridHighlights(nodeGrid, "node", cumulativeNodes, currentNodes);
    setGridHighlights(wireGrid, "wire", cumulativeWires, currentWires);
    setSvgHighlights(cumulativeNodes, currentNodes, cumulativeWires, currentWires);
    setLogicHighlights(cumulativeNodes, currentNodes);
    if (sequenceList) {
      sequenceList.querySelectorAll("[data-source-anchor]").forEach((item) => {
        const isActive = item.dataset.sourceAnchor === step.anchor;
        item.classList.toggle("is-active", isActive);
        item.dataset.state = isActive ? "active" : (steps.findIndex((candidate) => candidate.anchor === item.dataset.sourceAnchor) < activeIndex ? "complete" : "idle");
        const button = item.querySelector("button");
        if (button) button.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }
    applyDemoScenario(step);
    setReviewNavigationState(activeIndex, steps);
    if (options && options.selectStepElement) {
      const primary = primaryElementForStep(step);
      selectCircuitElement(primary.kind, primary.id);
    } else {
      renderTracePanel(selectedElement.kind, selectedElement.id);
    }
  }

  function renderSequence(steps) {
    if (!sequenceList) return;
    sequenceList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "未能读取 P035 到 L1-L4 的链路拆解。";
      sequenceList.appendChild(empty);
      setReviewNavigationState(0, []);
      return;
    }
    steps.forEach((step) => {
      const item = document.createElement("li");
      item.dataset.sourceAnchor = step.anchor || "";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "docx-circuit-step-button";
      button.setAttribute("data-review-anchor", step.anchor || "");
      button.setAttribute("aria-pressed", "false");
      const title = document.createElement("strong");
      title.textContent = `${step.anchor || "step"} · ${step.title || ""}`;
      const text = document.createElement("p");
      text.textContent = step.source_text || "";
      button.appendChild(title);
      item.appendChild(button);
      item.appendChild(text);
      appendChips(item, step.node_ids, "node");
      appendChips(item, step.wire_ids, "wire");
      button.addEventListener("click", () => activateStep(step.anchor, {selectStepElement: true}));
      sequenceList.appendChild(item);
    });
  }

  function renderPayload(payload) {
    const source = payload && payload.source ? payload.source : {};
    const coverage = payload && payload.coverage ? payload.coverage : {};
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    currentPayload = payload;
    setText(sourcePath, source.path || "uploads/20260409-thrust-reverser-control-logic.docx");
    setText(
      sourceCount,
      `${coverage.paragraph_count || 0} 段 · ${source.table_count || 0} 表 · ${coverage.source_entry_count || 0} 条`,
    );
    setText(nodeCount, `${coverage.covered_node_count || 0}/${contract.node_count || EXPECTED_NODE_COUNT}`);
    setText(wireCount, `${coverage.covered_wire_count || 0}/${contract.wire_count || EXPECTED_WIRE_COUNT}`);
    setText(sequenceCount, `P035 · ${coverage.sequence_step_count || 0} 步`);
    renderSequence(payload && payload.sequence_steps);
    renderSubcircuit();
    renderContractGrid(nodeGrid, contractIds(payload, "node_ids", Object.keys(NODE_LABELS).sort()), "node");
    renderContractGrid(wireGrid, contractIds(payload, "wire_ids", []), "wire");
    activateStep(currentAnchor);
    selectCircuitElement(selectedElement.kind, selectedElement.id);
  }

  async function boot() {
    try {
      const response = await fetch(DOCX_MAP_ENDPOINT, {headers: {"Accept": "application/json"}});
      if (!response.ok) throw new Error("docx map unavailable");
      renderPayload(await response.json());
    } catch (error) {
      renderSequence([]);
    }
  }

  if (demoFrame) {
    demoFrame.addEventListener("load", () => {
      if (currentPayload) activateStep(currentAnchor);
    });
  }
  if (prevStepButton) prevStepButton.addEventListener("click", () => activateRelativeStep(-1));
  if (nextStepButton) nextStepButton.addEventListener("click", () => activateRelativeStep(1));
  if (evidenceOnlyToggle) {
    evidenceOnlyToggle.addEventListener("change", () => renderTracePanel(selectedElement.kind, selectedElement.id));
  }
  if (copyTracePacketButton) copyTracePacketButton.addEventListener("click", copyTracePacket);

  boot();
})();

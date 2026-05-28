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

  const $ = (id) => document.getElementById(id);
  const sourcePath = $("docx-circuit-source-path");
  const sourceCount = $("docx-circuit-source-count");
  const nodeCount = $("docx-circuit-node-count");
  const wireCount = $("docx-circuit-wire-count");
  const sequenceCount = $("docx-circuit-sequence-count");
  const sequenceList = $("docx-circuit-sequence-list");
  const activeAnchor = $("docx-circuit-active-anchor");
  const reviewPanel = $("docx-circuit-review-panel");
  const sourceAnchor = $("docx-circuit-source-anchor");
  const sourceTitle = $("docx-circuit-source-title");
  const sourceText = $("docx-circuit-source-text");
  const logicLadder = $("docx-circuit-logic-ladder");
  const nodeGrid = $("docx-circuit-node-grid");
  const wireGrid = $("docx-circuit-wire-grid");
  const demoFrame = $("docx-circuit-demo-frame");
  const demoScenario = $("docx-circuit-demo-scenario");
  const demoSyncStatus = $("docx-circuit-demo-sync-status");
  let currentPayload = null;
  let currentAnchor = DEFAULT_STEP_ANCHOR;

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

  function activateStep(anchor) {
    if (!currentPayload || !Array.isArray(currentPayload.sequence_steps)) return;
    const steps = currentPayload.sequence_steps;
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
  }

  function renderSequence(steps) {
    if (!sequenceList) return;
    sequenceList.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      const empty = document.createElement("li");
      empty.textContent = "未能读取 P035 到 L1-L4 的链路拆解。";
      sequenceList.appendChild(empty);
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
      button.addEventListener("click", () => activateStep(step.anchor));
      sequenceList.appendChild(item);
    });
  }

  function renderPayload(payload) {
    const source = payload && payload.source ? payload.source : {};
    const coverage = payload && payload.coverage ? payload.coverage : {};
    const contract = payload && payload.circuit_contract ? payload.circuit_contract : {};
    setText(sourcePath, source.path || "uploads/20260409-thrust-reverser-control-logic.docx");
    setText(
      sourceCount,
      `${coverage.paragraph_count || 0} 段 · ${source.table_count || 0} 表 · ${coverage.source_entry_count || 0} 条`,
    );
    setText(nodeCount, `${coverage.covered_node_count || 0}/${contract.node_count || EXPECTED_NODE_COUNT}`);
    setText(wireCount, `${coverage.covered_wire_count || 0}/${contract.wire_count || EXPECTED_WIRE_COUNT}`);
    setText(sequenceCount, `P035 · ${coverage.sequence_step_count || 0} 步`);
    renderSequence(payload && payload.sequence_steps);
    renderContractGrid(nodeGrid, contractIds(payload, "node_ids", Object.keys(NODE_LABELS).sort()), "node");
    renderContractGrid(wireGrid, contractIds(payload, "wire_ids", []), "wire");
    currentPayload = payload;
    activateStep(currentAnchor);
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

  boot();
})();

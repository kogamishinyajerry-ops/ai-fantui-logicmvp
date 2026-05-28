(function () {
  "use strict";

  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const REPLAY_ENDPOINT = "/api/requirements-intake/deepseek-live-demo-replay";
  const DOCX_SENTENCE_CIRCUIT_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;
  const PRESETS = ["默认前向", "着陆展开", "最大反推", "收起回杆", "抑制阻塞"];
  const STATUS_OUTPUTS = ["SW1", "SW2", "TLS", "VDT90", "L1-L4", "THR_LOCK"];
  const TRACE_WIRE_ENDPOINTS = {
    wire_ra_logic1: ["radio_altitude_ft", "logic1"],
    wire_sw1_logic1: ["sw1", "logic1"],
    wire_inh_logic1: ["reverser_inhibited", "logic1"],
    wire_logic1_tls115: ["logic1", "tls115"],
    wire_tls115_tls_unlocked: ["tls115", "tls_unlocked"],
    wire_ground_logic2: ["aircraft_on_ground", "logic2"],
    wire_sw2_logic2: ["sw2", "logic2"],
    wire_engine_logic2: ["engine_running", "logic2"],
    wire_eec_logic2: ["eec_enable", "logic2"],
    wire_inh_logic2: ["reverser_inhibited", "logic2"],
    wire_logic2_etrac: ["logic2", "etrac_540v"],
    wire_tls_unlocked_logic3: ["tls_unlocked", "logic3"],
    wire_n1k_logic3: ["n1k", "logic3"],
    wire_engine_logic3: ["engine_running", "logic3"],
    wire_ground_logic3: ["aircraft_on_ground", "logic3"],
    wire_inh_logic3: ["reverser_inhibited", "logic3"],
    wire_logic3_eec: ["logic3", "eec_deploy"],
    wire_logic3_pls: ["logic3", "pls_power"],
    wire_logic3_pdu: ["logic3", "pdu_motor"],
    wire_pdu_vdt90: ["pdu_motor", "vdt90"],
    wire_vdt90_logic4: ["vdt90", "logic4"],
    wire_logic3_logic4: ["logic3", "logic4"],
    wire_logic4_thr_lock: ["logic4", "thr_lock"],
  };
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
  const traceContract = $("demo-reconstruction-trace-contract");
  const traceCardList = $("demo-reconstruction-trace-card-list");
  const selectedAnchor = $("demo-reconstruction-selected-anchor");
  const selectedTitle = $("demo-reconstruction-selected-title");
  const selectedText = $("demo-reconstruction-selected-text");
  const selectedNodes = $("demo-reconstruction-selected-nodes");
  const selectedWires = $("demo-reconstruction-selected-wires");
  const selectedFolded = $("demo-reconstruction-selected-folded");
  const embeddedHighlightStatus = $("demo-reconstruction-embedded-highlight-status");
  const consoleFrame = $("demo-reconstruction-console-frame");
  let currentTraceStep = null;

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

  function appendChipGroup(container, label, values, className) {
    if (!container || !Array.isArray(values) || values.length === 0) return;
    const group = document.createElement("div");
    group.className = "demo-reconstruction-chip-group";
    const caption = document.createElement("span");
    caption.className = "demo-reconstruction-chip-caption";
    caption.textContent = label;
    group.appendChild(caption);
    values.forEach((value) => {
      const chip = document.createElement("span");
      chip.className = `demo-reconstruction-chip ${className}`;
      chip.textContent = value;
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

  function embeddedWireSelector(wireId) {
    const endpoints = TRACE_WIRE_ENDPOINTS[wireId];
    if (!endpoints) return "";
    return `#fan-chain-svg .chain-wire[data-src="${endpoints[0]}"][data-dst="${endpoints[1]}"]`;
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
    return { nodeCount, wireCount, ready: true };
  }

  function applyEmbeddedTraceFocus(kind, id) {
    if (!consoleFrame || !id) return { matchCount: 0, ready: false };
    const frameDocument = consoleFrame.contentDocument;
    if (!frameDocument || !frameDocument.querySelector("#fan-chain-svg")) {
      setText(embeddedHighlightStatus, "等待电路图同步");
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
    return { matchCount, ready: true };
  }

  function setSelectedTrace(step) {
    if (!step || typeof step !== "object") return;
    currentTraceStep = step;
    document.querySelectorAll("[data-trace-card]").forEach((card) => {
      card.setAttribute("aria-pressed", card.dataset.traceAnchor === step.anchor ? "true" : "false");
    });
    setText(selectedAnchor, step.anchor || "P035");
    setText(selectedTitle, step.title || "工作过程片段");
    setText(selectedText, step.source_text || "");
    renderInlineChips(selectedNodes, step.node_ids, "demo-reconstruction-node-chip", "无节点", "node");
    renderInlineChips(selectedWires, step.wire_ids, "demo-reconstruction-wire-chip", "无连线", "wire");
    renderInlineChips(selectedFolded, step.folded_predicates, "demo-reconstruction-folded-chip", "无折叠谓词");
    applyEmbeddedTraceHighlight(step);
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
      traceCardList.appendChild(card);
    });
    setSelectedTrace(steps[0]);
  }

  function renderSourceEntries(entries) {
    if (!sourceEntryList) return;
    sourceEntryList.innerHTML = "";
    if (!Array.isArray(entries) || entries.length === 0) {
      const li = document.createElement("li");
      li.textContent = "DOCX 逐句映射暂无数据";
      sourceEntryList.appendChild(li);
      return;
    }
    entries.forEach((entry) => {
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
      appendChipGroup(chips, "节点", entry.node_ids, "demo-reconstruction-node-chip");
      appendChipGroup(chips, "连线", entry.wire_ids, "demo-reconstruction-wire-chip");

      li.appendChild(topLine);
      li.appendChild(text);
      li.appendChild(chips);
      sourceEntryList.appendChild(li);
    });
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
      appendChipGroup(chips, "节点", step.node_ids, "demo-reconstruction-node-chip");
      appendChipGroup(chips, "连线", step.wire_ids, "demo-reconstruction-wire-chip");
      appendChipGroup(chips, "折叠谓词", step.folded_predicates, "demo-reconstruction-folded-chip");

      li.appendChild(title);
      li.appendChild(text);
      li.appendChild(chips);
      li.addEventListener("click", () => setSelectedTrace(step));
      sequenceStepList.appendChild(li);
    });
  }

  function renderDocxSentenceCircuitMap(payload) {
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
    renderSourceEntries(payload && payload.source_entries);
    renderSequenceSteps(payload && payload.sequence_steps);
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
      if (currentTraceStep) applyEmbeddedTraceHighlight(currentTraceStep);
    });
  }

  async function boot() {
    loadDocxSentenceCircuitMap()
      .then((payload) => {
        if (payload) {
          renderDocxSentenceCircuitMap(payload);
        } else {
          renderSourceEntries([{anchor: "DOCX", role: "接口不可用", text: "未能读取原始 DOCX 映射接口", node_ids: [], wire_ids: []}]);
        }
      })
      .catch(() => {
        renderSourceEntries([{anchor: "DOCX", role: "接口异常", text: "原始 DOCX 映射接口返回异常，完整 demo 电路仍可查看。", node_ids: [], wire_ids: []}]);
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

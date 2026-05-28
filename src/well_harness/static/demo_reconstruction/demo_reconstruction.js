(function () {
  "use strict";

  const DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const REPLAY_ENDPOINT = "/api/requirements-intake/deepseek-live-demo-replay";
  const DOCX_SENTENCE_CIRCUIT_ENDPOINT = "/api/demo-reconstruction/docx-sentence-circuit-map";
  const EXPECTED_NODE_COUNT = 20;
  const EXPECTED_WIRE_COUNT = 23;
  const PRESETS = ["默认前向", "着陆展开", "最大反推", "收起回杆", "抑制阻塞"];
  const STATUS_OUTPUTS = ["SW1", "SW2", "TLS", "VDT90", "L1-L4", "THR_LOCK"];
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
  const coverageContract = $("demo-reconstruction-coverage-contract");
  const coverageSearch = $("demo-reconstruction-coverage-search");
  const coverageFilterStatus = $("demo-reconstruction-coverage-filter-status");
  const coverageNodeList = $("demo-reconstruction-coverage-node-list");
  const coverageWireList = $("demo-reconstruction-coverage-wire-list");
  const reviewAnchor = $("demo-reconstruction-review-anchor");
  const reviewObject = $("demo-reconstruction-review-object");
  const reviewSync = $("demo-reconstruction-review-sync");
  const reviewLink = $("demo-reconstruction-review-link");
  const stepPlayback = $("demo-reconstruction-step-playback");
  const playbackStepList = $("demo-reconstruction-playback-step-list");
  const playbackActiveStep = $("demo-reconstruction-playback-active-step");
  const playbackNodeCount = $("demo-reconstruction-playback-node-count");
  const playbackWireCount = $("demo-reconstruction-playback-wire-count");
  const provenanceObject = $("demo-reconstruction-provenance-object");
  const provenanceSourceCount = $("demo-reconstruction-provenance-source-count");
  const provenanceStepCount = $("demo-reconstruction-provenance-step-count");
  const provenanceSourceList = $("demo-reconstruction-provenance-source-list");
  const provenanceStepList = $("demo-reconstruction-provenance-step-list");
  const consoleFrame = $("demo-reconstruction-console-frame");
  let sourceEntries = [];
  let traceSteps = [];
  let currentTraceStep = null;
  let selectedTraceIndex = -1;
  let currentCircuitFocus = {kind: "", id: ""};
  let activePlaybackIndex = -1;
  let applyingReviewHashState = false;
  let wireEndpointMap = new Map();

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

  function updateWireEndpointMapFromWires(wires) {
    wireEndpointMap = new Map();
    if (!Array.isArray(wires)) return;
    wires.forEach((wire) => {
      if (!wire || !wire.id || !wire.source || !wire.target) return;
      wireEndpointMap.set(wire.id, [wire.source, wire.target]);
    });
  }

  function wireEndpointsForId(wireId) {
    return wireEndpointMap.get(wireId) || [];
  }

  function refreshEmbeddedReviewFromCircuit() {
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

  function updateStepPlaybackSummary(contract) {
    if (!contract) return;
    setText(playbackActiveStep, contract.anchor);
    setText(playbackNodeCount, `${contract.node_ids.length}/${EXPECTED_NODE_COUNT} 节点`);
    setText(playbackWireCount, `${contract.wire_ids.length}/${EXPECTED_WIRE_COUNT} 连线`);
    setPlaybackButtonState(contract.anchor);
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
      updateCoverageFilter();
      if (state.step) {
        const step = traceSteps.find((item) => item && item.anchor === state.step);
        if (step) setSelectedTrace(step, {writeHash: false});
      }
      if (state.focusKind && state.focusId) {
        applyEmbeddedTraceFocus(state.focusKind, state.focusId);
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

  function applyEmbeddedTraceFocus(kind, id) {
    if (!consoleFrame || !id) return { matchCount: 0, ready: false };
    activePlaybackIndex = -1;
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
    setText(selectedAnchor, step.anchor || "P035");
    setText(selectedTitle, step.title || "工作过程片段");
    setText(selectedText, step.source_text || "");
    renderInlineChips(selectedNodes, step.node_ids, "demo-reconstruction-node-chip", "无节点", "node");
    renderInlineChips(selectedWires, step.wire_ids, "demo-reconstruction-wire-chip", "无连线", "wire");
    renderInlineChips(selectedFolded, step.folded_predicates, "demo-reconstruction-folded-chip", "无折叠谓词");
    applyEmbeddedTraceHighlight(step);
    if (options.writeHash !== false) writeReviewHashState();
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
    renderCoverageMatrix(payload);
    renderSourceEntries(payload && payload.source_entries);
    renderSequenceSteps(payload && payload.sequence_steps);
    applyReviewHashState();
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
    updateWireEndpointMapFromWires(wires);
    refreshEmbeddedReviewFromCircuit();
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
      if (currentCircuitFocus.kind && currentCircuitFocus.id) {
        applyEmbeddedTraceFocus(currentCircuitFocus.kind, currentCircuitFocus.id);
      } else if (activePlaybackIndex >= 0) {
        applyEmbeddedPlaybackHighlight(cumulativeTraceContract(activePlaybackIndex));
      } else if (currentTraceStep) {
        applyEmbeddedTraceHighlight(currentTraceStep);
      }
    });
  }
  if (coverageSearch) {
    coverageSearch.addEventListener("input", () => {
      updateCoverageFilter();
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

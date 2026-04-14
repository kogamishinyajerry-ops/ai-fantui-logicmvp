const sections = [
  "evidence",
  "outcome",
  "possible_causes",
  "required_changes",
  "risks",
];

const sectionLabels = {
  evidence: "证据",
  outcome: "结果",
  possible_causes: "可能原因",
  required_changes: "需要变化",
  risks: "风险",
};

// ---------------------------------------------------------------------------
// Multi-system switcher support (P13)
// ---------------------------------------------------------------------------
/** Current active system_id, default thrust-reverser */
let _currentSystemId = "thrust-reverser";
/** Cached nodes from the last /api/system-snapshot call — used to re-apply truth evaluation on lever-snapshot updates. */
let _systemSnapshotNodes = [];

/**
 * Fetch /api/system-snapshot for the given systemId, then update the UI.
 * For thrust-reverser: use the existing HTML-defined parallel topology (don't rebuild from flat nodes)
 * For other systems: show the corresponding topology and apply node states
 */
async function handleSystemSwitch(systemId) {
  _currentSystemId = systemId;
  resetUIState();
  try {
    const url = `/api/system-snapshot?system_id=${encodeURIComponent(systemId)}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    // Show the correct topology, hide others
    document.querySelectorAll(".chain-topology").forEach((el) => {
      el.style.display = "none";
    });
    const topologyEl = document.getElementById(`chain-topology-${systemId}`);
    if (topologyEl) topologyEl.style.display = "";

    // Apply node states from truth evaluation to visible topology
    _systemSnapshotNodes = data.nodes || [];
    applySystemNodeStates(_systemSnapshotNodes, data.truth_evaluation?.asserted_component_values);

    // Render truth evaluation answer card
    renderTruthEvaluation(data.truth_evaluation);

    // Update hero title
    const titleEl = document.getElementById("page-title");
    if (titleEl) titleEl.textContent = data.title || systemId;

    // Show/hide condition panel based on system
    const conditionPanel = document.querySelector(".condition-panel");
    if (conditionPanel) {
      conditionPanel.style.display = systemId === "thrust-reverser" ? "" : "none";
    }

    // Show/hide lever-panel vs system-input-panel
    // lever-panel is for thrust-reverser only; others use system-input-panel
    const leverPanel = document.querySelector(".lever-panel");
    if (leverPanel) {
      leverPanel.style.display = systemId === "thrust-reverser" ? "" : "none";
    }
    document.querySelectorAll(".system-input-panel").forEach((el) => { el.style.display = "none"; });
    const lgPanel = document.getElementById("landing-gear-inputs");
    const baPanel = document.getElementById("bleed-air-inputs");
    const efdsPanel = document.getElementById("efds-inputs");
    if (lgPanel) lgPanel.style.display = systemId === "landing-gear" ? "" : "none";
    if (baPanel) baPanel.style.display = systemId === "bleed-air" ? "" : "none";
    if (efdsPanel) efdsPanel.style.display = systemId === "efds" ? "" : "none";
  } catch (err) {
    console.error("handleSystemSwitch failed:", err);
  }
}

/**
 * Collect form values from a system-specific input panel into a snapshot dict.
 */
function collectSystemSnapshotPayload(systemId) {
  const snapshot = {};
  let panel;
  if (systemId === "landing-gear") {
    panel = document.getElementById("landing-gear-inputs");
    if (!panel) return snapshot;
    snapshot.gear_handle_position = panel.querySelector("[name=gear_handle_position]")?.value || "UP";
    snapshot.hydraulic_pressure_psi = parseFloat(panel.querySelector("[name=hydraulic_pressure_psi]")?.value) || 0;
    snapshot.gear_position_percent = parseFloat(panel.querySelector("[name=gear_position_percent]")?.value) || 0;
    snapshot.uplock_released = panel.querySelector("[name=uplock_released]")?.checked || false;
    snapshot.downlock_engaged = panel.querySelector("[name=downlock_engaged]")?.checked || false;
  } else if (systemId === "bleed-air") {
    panel = document.getElementById("bleed-air-inputs");
    if (!panel) return snapshot;
    snapshot.valve_position = panel.querySelector("[name=valve_position]")?.value || "CLOSED";
    snapshot.inlet_pressure = parseFloat(panel.querySelector("[name=inlet_pressure]")?.value) || 0;
    snapshot.outlet_pressure = parseFloat(panel.querySelector("[name=outlet_pressure]")?.value) || 0;
    snapshot.control_unit_ready = panel.querySelector("[name=control_unit_ready]")?.checked || false;
  } else if (systemId === "efds") {
    panel = document.getElementById("efds-inputs");
    if (!panel) return snapshot;
    snapshot["sensor.threat.mls"] = panel.querySelector("[name=sensor.threat.mls]")?.value || "IDLE";
    snapshot["sensor.alt.radar"] = parseFloat(panel.querySelector("[name=sensor.alt.radar]")?.value) || 0;
    snapshot["sensor.alt.baro"] = parseFloat(panel.querySelector("[name=sensor.alt.baro]")?.value) || 0;
    snapshot["sensor.temp.external"] = parseFloat(panel.querySelector("[name=sensor.temp.external]")?.value) || 15;
    snapshot["pilot.arm_switch"] = panel.querySelector("[name=pilot.arm_switch]")?.value || "SAFE";
    snapshot["pilot.altitude_override"] = panel.querySelector("[name=pilot.altitude_override]")?.value || "AUTO";
    snapshot["pilot.manual_dispense"] = panel.querySelector("[name=pilot.manual_dispense]")?.value || "RELEASED";
    snapshot["logic.armed_relay"] = panel.querySelector("[name=logic.armed_relay]")?.value || "OPEN";
    snapshot["logic.crosslink_validator"] = panel.querySelector("[name=logic.crosslink_validator]")?.value || "FALSE";
    snapshot["logic.firing_channel"] = panel.querySelector("[name=logic.firing_channel]")?.value || "READY";
    // Required by efds_adapter.evaluate() but not user-editable; preserve defaults
    snapshot["actuator.flare_array"] = 24.0;
    snapshot["sensor.g.load"] = 1.0;
  }
  return snapshot;
}

/**
 * POST a user-modified snapshot to /api/system-snapshot and re-render UI.
 */
async function runSystemSnapshot(systemId) {
  const snapshot = collectSystemSnapshotPayload(systemId);
  let response;
  try {
    response = await fetch("/api/system-snapshot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ system_id: systemId, snapshot }),
    });
  } catch (err) {
    console.error("runSystemSnapshot network error:", err);
    return;
  }
  const payload = await response.json().catch(() => ({ error: "invalid_json" }));
  if (!response.ok) {
    console.error("runSystemSnapshot error:", payload);
    return;
  }
  // Re-apply node states from the updated truth evaluation
  _systemSnapshotNodes = payload.nodes || [];
  applySystemNodeStates(_systemSnapshotNodes, payload.truth_evaluation?.asserted_component_values);
  // Re-render truth evaluation card
  renderTruthEvaluation(payload.truth_evaluation);
}

/**
 * Apply node states (active/inactive) to the currently visible chain-topology.
 * Uses data-node attributes on elements to match against node ids.
 */
function applySystemNodeStates(nodes, componentValues) {
  // Build a map from node id -> state
  const stateMap = new Map();
  nodes.forEach((node) => {
    stateMap.set(node.id, node.state || "inactive");
  });

  // Build a map from signal id -> value (from componentValues)
  const nodeValueMap = new Map();
  if (componentValues) {
    Object.entries(componentValues).forEach(([signalId, value]) => {
      nodeValueMap.set(signalId, value);
    });
  }

  // Apply states to all nodes in the visible topology
  document.querySelectorAll(".chain-topology:not([style*='display: none']) [data-node]").forEach((el) => {
    const nodeId = el.dataset.node;
    // Determine effective state: override backend state with actual component value when available
    let state = stateMap.get(nodeId) || "inactive";
    if (componentValues && nodeValueMap.has(nodeId)) {
      // Input/condition nodes: derive state from actual signal value, not just logic-gate activation
      const cv = nodeValueMap.get(nodeId);
      if (typeof cv === "boolean") {
        state = cv ? "active" : "inactive";
      } else if (typeof cv === "number" && Number.isFinite(cv)) {
        // Numeric conditions (RA, N1K, TRA): non-zero = active
        state = cv !== 0 ? "active" : "inactive";
      }
    }
    el.classList.remove("is-active", "is-blocked", "is-inactive");
    el.classList.add(`is-${state}`);
    el.dataset.state = state;

    // Update the sibling <text data-value-for="..."> value display.
    // Directly query by data-value-for to avoid parent traversal ambiguity in SVG.
    // signalKey (e.g. "sw1", "radio_altitude_ft") is the backend signal ID used as the map key.
    const valueEl = el.parentElement?.querySelector(`[data-value-for="${nodeId}"]`) || el.querySelector(`[data-value-for="${nodeId}"]`);
    if (valueEl) {
      const cv = nodeValueMap.get(nodeId);
      if (cv !== undefined) {
        valueEl.textContent = formatSignalValue(cv);
      } else if (state === "active") {
        valueEl.textContent = "ON";
      } else if (state === "blocked") {
        valueEl.textContent = "WAIT";
      } else {
        valueEl.textContent = "OFF";
      }
    }
  });
}

/** Format a signal value for display in SVG text. */
function formatSignalValue(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "ON" : "OFF";
  if (typeof value === "number") {
    if (Number.isFinite(value)) {
      // Round to 1 decimal for display
      return value % 1 === 0 ? String(value) : value.toFixed(1);
    }
    return "—";
  }
  return String(value);
}

/** Clear all dynamic UI state (chain nodes, HUD values, result areas). */
function resetUIState() {
  // Clear chain-node active/inactive states
  document.querySelectorAll(".chain-node, .logic-note").forEach((el) => {
    el.classList.remove("is-active", "is-blocked", "is-inactive");
  });
  // Reset HUD values to "-"
  document.querySelectorAll(".hud-grid dd").forEach((el) => {
    el.textContent = "-";
  });
  // Clear result areas
  const structuredOutput = document.getElementById("structured-output");
  if (structuredOutput) structuredOutput.innerHTML = "";
  const leverResult = document.querySelector(".lever-result");
  if (leverResult) {
    leverResult.querySelectorAll("p[id]").forEach((p) => {
      if (p.id.startsWith("lever-")) p.textContent = "-";
    });
  }
  const truthEvalCard = document.getElementById("truth-eval-card");
  if (truthEvalCard) truthEvalCard.remove();
}

/**
 * Apply node states to the currently visible chain-topology.
 * Called by existing thrust-reverser lever-snapshot path.
 */
function renderChainMap(nodes) {
  // For thrust-reverser: use the HTML-defined topology with parallel/merge structure
  // Just apply states to visible nodes, don't rebuild
  applySystemNodeStates(nodes);
}

/**
 * Render GenericTruthEvaluation as a read-only answer card for the current system.
 * For non-thrust-reverser systems this replaces the QA drawer content.
 */
function renderTruthEvaluation(evaluation) {
  if (!evaluation) return;
  // For thrust-reverser, only render truth-eval if no full lever result is present
  // For other systems, always render as the primary answer
  const resultGrid = document.querySelector(".result-grid");
  if (!resultGrid) return;

  // Remove any existing truth-eval card
  const existing = document.getElementById("truth-eval-card");
  if (existing) existing.remove();

  const card = document.createElement("article");
  card.id = "truth-eval-card";
  card.className = "panel truth-eval-card";
  card.innerHTML = `
    <h2><span class="presenter-callout">[推理]</span> ${evaluation.system_id}</h2>
    <p class="truth-eval-summary">${evaluation.summary || "-"}</p>
    ${evaluation.blocked_reasons && evaluation.blocked_reasons.length > 0 ? `
      <dl class="truth-eval-blocked">
        <dt>阻塞原因</dt>
        ${evaluation.blocked_reasons.map((r) => `<dd>${r}</dd>`).join("")}
      </dl>
    ` : ""}
    <dl class="truth-eval-active">
      <dt>活跃逻辑节点</dt>
      <dd>${evaluation.active_logic_node_ids ? evaluation.active_logic_node_ids.join(", ") : "-"}</dd>
    </dl>
  `;
  resultGrid.insertBefore(card, resultGrid.firstChild);
}

const monitorSvgNamespace = "http://www.w3.org/2000/svg";
const monitorDefaultSeriesId = "all";
let latestMonitorPayload = null;
let selectedMonitorTrackIds = new Set(); // empty = nothing shown, "all" = all tracks

const nodeAliases = {
  "logic4->thr_lock": ["logic4", "thr_lock"],
  throttle_lock_release_cmd: ["thr_lock"],
  thr_lock: ["thr_lock"],
  logic4: ["logic4"],
  logic3: ["logic3", "eec_deploy", "pls_power", "pdu_motor"],
  "logic3.tra_deg": ["logic3"],
  pdu_motor: ["pdu_motor"],
  pls_power: ["pls_power"],
  eec_deploy: ["eec_deploy"],
  vdt90: ["vdt90"],
  etrac_540v: ["etrac_540v"],
  logic2: ["logic2", "etrac_540v"],
  tls115: ["tls115"],
  logic1: ["logic1", "tls115"],
  tls_unlocked: ["tls_unlocked"],
  sw1: ["sw1"],
  sw2: ["sw2"],
};

const nodeLabels = {
  sw1: "SW1",
  logic1: "L1",
  tls115: "TLS115",
  tls_unlocked: "TLS 解锁",
  sw2: "SW2",
  logic2: "L2",
  etrac_540v: "540V",
  logic3: "L3",
  eec_deploy: "EEC",
  pls_power: "PLS",
  pdu_motor: "PDU",
  vdt90: "VDT90",
  logic4: "L4",
  thr_lock: "THR_LOCK",
};

const leverPresets = {
  l3_waiting_vdt90: {
    label: "L3 等待 VDT90",
    status: "当前场景：L3 等待 VDT90（默认演示位，先留在 -14° 门槛内）。",
    payload: {
      tra_deg: -12,
      radio_altitude_ft: 5,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 35,
      max_n1k_deploy_limit: 60,
      feedback_mode: "manual_feedback_override",
      deploy_position_percent: 0,
    },
  },
  ra_boundary_blocks_logic1: {
    label: "RA blocker",
    status: "当前场景：RA blocker，链路会卡在 L1。",
    payload: {
      tra_deg: -12,
      radio_altitude_ft: 6,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 35,
      max_n1k_deploy_limit: 60,
      feedback_mode: "manual_feedback_override",
      deploy_position_percent: 0,
    },
  },
  n1k_limit_blocks_logic3: {
    label: "N1K blocker",
    status: "当前场景：N1K blocker，链路会卡在 L3。",
    payload: {
      tra_deg: -12,
      radio_altitude_ft: 5,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 60,
      max_n1k_deploy_limit: 60,
      feedback_mode: "manual_feedback_override",
      deploy_position_percent: 0,
    },
  },
  manual_vdt90_ready: {
    label: "VDT90 ready",
    status: "当前场景：VDT90 ready，manual override 已把 L4 / THR_LOCK 推到可演示状态，深拉区可继续向左进入。",
    payload: {
      tra_deg: -12,
      radio_altitude_ft: 5,
      engine_running: true,
      aircraft_on_ground: true,
      reverser_inhibited: false,
      eec_enable: true,
      n1k: 35,
      max_n1k_deploy_limit: 60,
      feedback_mode: "manual_feedback_override",
      deploy_position_percent: 95,
    },
  },
};

const defaultLeverStartupStatus = "当前场景：自定义起步位（先自由左拉到 -14° 门槛，再等待 L4 放开深拉区）。";

let latestInteractionRequestId = 0;

function beginInteractionRequest() {
  latestInteractionRequestId += 1;
  return latestInteractionRequestId;
}

function isLatestInteractionRequest(requestId) {
  return requestId === latestInteractionRequestId;
}

function textOrDash(value) {
  return value === null || value === undefined || value === "" ? "-" : value;
}

function formatMonitorValue(value, unit) {
  if (!Number.isFinite(value)) {
    return "-";
  }
  if (unit === "state") {
    return value >= 1 ? "1" : "0";
  }
  if (unit === "%") {
    return `${value.toFixed(0)}%`;
  }
  if (unit === "deg") {
    return `${value.toFixed(1)}°`;
  }
  if (unit === "ft") {
    return `${value.toFixed(1)} ft`;
  }
  if (unit === "V") {
    return `${value.toFixed(0)} V`;
  }
  return `${value}`;
}

function createMonitorSvgElement(tagName, attributes = {}) {
  const element = document.createElementNS(monitorSvgNamespace, tagName);
  Object.entries(attributes).forEach(([name, value]) => {
    element.setAttribute(name, String(value));
  });
  return element;
}

function buildMonitorXAxisTicks(timeStart, timeEnd) {
  const span = Math.max(0, timeEnd - timeStart);
  const tickStep = span <= 8 ? 1 : Math.max(1, Math.ceil(span / 7));
  const ticks = [];
  for (let tick = timeStart; tick <= timeEnd + 1e-6; tick += tickStep) {
    ticks.push(Number(tick.toFixed(1)));
  }
  if (!ticks.length || ticks[ticks.length - 1] !== Number(timeEnd.toFixed(1))) {
    ticks.push(Number(timeEnd.toFixed(1)));
  }
  return ticks;
}

function monitorScaleX(timeValue, timeStart, timeEnd, left, width) {
  const safeSpan = Math.max(1, timeEnd - timeStart);
  return left + ((timeValue - timeStart) / safeSpan) * width;
}

function monitorScaleY(value, valueMin, valueMax, top, height) {
  const safeSpan = Math.max(1e-6, valueMax - valueMin);
  return top + (1 - ((value - valueMin) / safeSpan)) * height;
}

function normalizedMonitorValue(track, value) {
  const displayMin = Number(track.display_min);
  const displayMax = Number(track.display_max);
  const safeSpan = Math.max(1e-6, displayMax - displayMin);
  return (Number(value) - displayMin) / safeSpan;
}

function monitorTrackOptions(payload) {
  const series = Array.isArray(payload.series) ? payload.series : [];
  return series.map((track) => ({id: track.id, label: `${track.label}（${track.unit}）`}));
}

function selectedMonitorTracks(payload) {
  const series = Array.isArray(payload.series) ? payload.series : [];
  if (selectedMonitorTrackIds.size === 0) return []; // nothing selected
  return series.filter((track) => selectedMonitorTrackIds.has(track.id));
}

function renderMonitorSummary(payload) {
  const summary = payload.timeline_summary || {};
  const compressionRatio = Number(payload.compression_ratio || 10);
  const chips = [
    `时间轴压缩 x${compressionRatio.toFixed(0)}`,
    `RA=6.0ft @ ${Number(summary.ra_hits_six_ft_at_s || 0).toFixed(1)}s`,
    `TRA=-14° @ ${Number(summary.tra_reaches_lock_at_s || 0).toFixed(1)}s`,
    `VDT90 / L4 ready @ ${Number(summary.l4_ready_at_s || summary.vdt_reaches_90_percent_at_s || 0).toFixed(1)}s`,
    `监测结束 @ ${Number(payload.active_end_s || 0).toFixed(1)}s`,
  ];
  const container = document.getElementById("monitor-summary");
  container.replaceChildren(...chips.map((label) => {
    const chip = document.createElement("span");
    chip.className = "monitor-summary-chip";
    chip.textContent = label;
    return chip;
  }));
}

function renderMonitorEvents(payload) {
  const container = document.getElementById("monitor-events");
  const events = Array.isArray(payload.events) ? payload.events : [];
  container.replaceChildren(...events.map((event) => {
    const chip = document.createElement("article");
    chip.className = "monitor-event-card";

    const time = document.createElement("span");
    time.className = "monitor-event-time";
    time.textContent = `t=${Number(event.time_s || 0).toFixed(1)}s`;

    const label = document.createElement("strong");
    label.textContent = event.label || "关键时刻";

    chip.append(time, label);
    return chip;
  }));
}

function renderMonitorSelectionNote(payload, tracks) {
  const container = document.getElementById("monitor-selection-note");
  if (tracks.length === 0) {
    container.textContent = "请从上方勾选要显示的参数（可多选）。";
    return;
  }
  if (tracks.length === 1) {
    const track = tracks[0];
    const lastSample = Array.isArray(track.samples) && track.samples.length
      ? Number(track.samples[track.samples.length - 1][1])
      : null;
    container.textContent = (
      `当前显示：${track.label} | 真实量程 `
      + `${formatMonitorValue(Number(track.display_min), track.unit)} -> ${formatMonitorValue(Number(track.display_max), track.unit)}`
      + ` | 末值 ${formatMonitorValue(lastSample, track.unit)}`
    );
    return;
  }
  const names = tracks.map((t) => t.label).join("、");
  container.textContent = `当前显示：${tracks.length} 个参数（归一化叠加）| ${names}`;
}

function populateMonitorSeriesCheckboxes(payload) {
  const container = document.getElementById("monitor-series-checkboxes");
  const options = monitorTrackOptions(payload);
  container.replaceChildren(...options.map((option) => {
    const label = document.createElement("label");
    label.className = "monitor-checkbox-label";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = option.id;
    checkbox.className = "monitor-series-checkbox";
    checkbox.setAttribute("aria-label", option.label);
    // Restore checked state if track was previously selected
    if (selectedMonitorTrackIds.has(option.id)) {
      checkbox.checked = true;
    }
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        selectedMonitorTrackIds.add(option.id);
      } else {
        selectedMonitorTrackIds.delete(option.id);
      }
      if (latestMonitorPayload) {
        renderMonitorChart(latestMonitorPayload);
      }
    });
    const text = document.createElement("span");
    text.textContent = option.label;
    label.appendChild(checkbox);
    label.appendChild(text);
    return label;
  }));
}

function buildMonitorChartSvg(payload, tracks) {
  // Empty state: no tracks selected
  if (tracks.length === 0) {
    const msg = createMonitorSvgElement("text", {
      x: 480,
      y: 130,
      "text-anchor": "middle",
      class: "monitor-axis-label",
      "font-size": "14",
    });
    msg.textContent = "请勾选上方参数以显示曲线";
    const svg = createMonitorSvgElement("svg", {
      viewBox: "0 0 960 240",
      role: "img",
      "aria-label": "监控时间线图（无选中参数）",
    });
    svg.appendChild(msg);
    return svg;
  }

  const useNormalized = tracks.length > 1;
  const svg = createMonitorSvgElement("svg", {
    viewBox: "0 0 960 240",
    role: "img",
    "aria-label": useNormalized
      ? "多参数归一化叠加监控时间线图"
      : `${tracks[0].label} 状态随时间变化图`,
  });
  const padding = {top: 18, right: 18, bottom: 28, left: 58};
  const chartWidth = 960 - padding.left - padding.right;
  const chartHeight = 240 - padding.top - padding.bottom;
  const timeStart = Number(payload.time_start_s || 0);
  const timeEnd = Number(payload.time_end_s || 0);
  const xTicks = buildMonitorXAxisTicks(timeStart, timeEnd);
  const valueMin = 0.0;
  const valueMax = 1.0;

  [0, 0.25, 0.5, 0.75, 1].forEach((fraction) => {
    const y = padding.top + chartHeight * fraction;
    svg.appendChild(createMonitorSvgElement("line", {
      x1: padding.left,
      y1: y,
      x2: padding.left + chartWidth,
      y2: y,
      class: "monitor-grid-line",
    }));
  });

  xTicks.forEach((tick) => {
    const x = monitorScaleX(tick, timeStart, timeEnd, padding.left, chartWidth);
    svg.appendChild(createMonitorSvgElement("line", {
      x1: x,
      y1: padding.top,
      x2: x,
      y2: padding.top + chartHeight,
      class: "monitor-grid-line",
    }));
    const label = createMonitorSvgElement("text", {
      x,
      y: padding.top + chartHeight + 17,
      "text-anchor": tick === timeStart ? "start" : tick === timeEnd ? "end" : "middle",
      class: "monitor-axis-label",
    });
    label.textContent = `${tick.toFixed(tick % 1 === 0 ? 0 : 1)}s`;
    svg.appendChild(label);
  });

  (payload.events || []).forEach((event) => {
    const eventTime = Number(event.time_s || 0);
    if (eventTime < timeStart || eventTime > timeEnd) {
      return;
    }
    const x = monitorScaleX(eventTime, timeStart, timeEnd, padding.left, chartWidth);
    svg.appendChild(createMonitorSvgElement("line", {
      x1: x,
      y1: padding.top,
      x2: x,
      y2: padding.top + chartHeight,
      class: "monitor-event-line",
    }));
  });

  svg.appendChild(createMonitorSvgElement("line", {
    x1: padding.left,
    y1: padding.top + chartHeight,
    x2: padding.left + chartWidth,
    y2: padding.top + chartHeight,
    class: "monitor-axis-line",
  }));

  const yLabels = useNormalized
    ? [
      {value: 1.0, text: "100% 归一化", className: "monitor-value-label is-strong"},
      {value: 0.5, text: "50% 归一化", className: "monitor-value-label"},
      {value: 0.0, text: "0% 归一化", className: "monitor-value-label"},
    ]
    : [
      {value: valueMax, text: formatMonitorValue(valueMax, tracks[0].unit), className: "monitor-value-label is-strong"},
      {value: (valueMax + valueMin) / 2, text: formatMonitorValue((valueMax + valueMin) / 2, tracks[0].unit), className: "monitor-value-label"},
      {value: valueMin, text: formatMonitorValue(valueMin, tracks[0].unit), className: "monitor-value-label"},
    ];
  yLabels.forEach(({value, text, className}) => {
    const label = createMonitorSvgElement("text", {
      x: padding.left - 8,
      y: monitorScaleY(value, valueMin, valueMax, padding.top, chartHeight) + 4,
      "text-anchor": "end",
      class: className,
    });
    label.textContent = text;
    svg.appendChild(label);
  });

  tracks.forEach((seriesTrack) => {
    const samples = Array.isArray(seriesTrack.samples) ? seriesTrack.samples : [];
    const pointString = samples.map(([timeValue, value]) => {
      const x = monitorScaleX(Number(timeValue), timeStart, timeEnd, padding.left, chartWidth);
      const plottedValue = useNormalized
        ? normalizedMonitorValue(seriesTrack, Number(value))
        : Number(value);
      const y = monitorScaleY(plottedValue, valueMin, valueMax, padding.top, chartHeight);
      return `${x},${y}`;
    }).join(" ");
    svg.appendChild(createMonitorSvgElement("polyline", {
      points: pointString,
      class: "monitor-series-line",
      stroke: seriesTrack.color || "#28f4ff",
      "data-series-id": seriesTrack.id,
    }));

    const lastSample = samples[samples.length - 1];
    if (lastSample) {
      const plottedValue = useNormalized
        ? normalizedMonitorValue(seriesTrack, Number(lastSample[1]))
        : Number(lastSample[1]);
      svg.appendChild(createMonitorSvgElement("circle", {
        cx: monitorScaleX(Number(lastSample[0]), timeStart, timeEnd, padding.left, chartWidth),
        cy: monitorScaleY(plottedValue, valueMin, valueMax, padding.top, chartHeight),
        r: useNormalized ? 3 : 4,
        fill: seriesTrack.color || "#28f4ff",
        class: "monitor-series-endpoint",
      }));
    }
  });

  return svg;
}

function renderMonitorChart(payload) {
  const container = document.getElementById("monitor-chart");
  const tracks = selectedMonitorTracks(payload);
  renderMonitorSelectionNote(payload, tracks);
  container.replaceChildren(buildMonitorChartSvg(payload, tracks));
}

function renderMonitorTimeline(payload) {
  latestMonitorPayload = payload;
  renderMonitorSummary(payload);
  renderMonitorEvents(payload);
  populateMonitorSeriesCheckboxes(payload);
  renderMonitorChart(payload);
  document.getElementById("monitor-status").textContent = payload.model_note || "监控时间线已更新。";
  document.getElementById("monitor-status").classList.remove("is-error");
}

function renderMonitorTimelineError(message) {
  latestMonitorPayload = null;
  document.getElementById("monitor-status").textContent = message;
  document.getElementById("monitor-status").classList.add("is-error");
  document.getElementById("monitor-summary").replaceChildren();
  document.getElementById("monitor-events").replaceChildren();
  document.getElementById("monitor-chart").replaceChildren();
  document.getElementById("monitor-selection-note").textContent = "监控时间线不可用。";
}

function clampLeverTraToUnlockedBand(rawValue) {
  const leverInput = document.getElementById("lever-tra");
  const visualReverseMin = Number(leverInput.min ?? -32);
  const allowedReverseMin = Number(leverInput.dataset.allowedReverseMin ?? visualReverseMin);
  const reverseMax = Number(leverInput.max ?? 0);
  const normalizedValue = Number.isFinite(rawValue) ? rawValue : Number(leverInput.value ?? 0);
  return Math.min(reverseMax, Math.max(allowedReverseMin, Math.max(visualReverseMin, normalizedValue)));
}

function answerSectionId(sectionName) {
  return `answer-section-${sectionName}`;
}

function focusAnswerSection(sectionName) {
  const target = document.getElementById(answerSectionId(sectionName));
  if (!target) {
    return;
  }
  target.focus({preventScroll: true});
  target.scrollIntoView({behavior: "smooth", block: "start"});
}

function focusSummaryChip(currentChip, key) {
  const chips = Array.from(document.querySelectorAll("#answer-section-summary-items button.summary-chip"));
  const currentIndex = chips.indexOf(currentChip);
  if (currentIndex === -1 || chips.length === 0) {
    return;
  }

  const lastIndex = chips.length - 1;
  const targetIndexByKey = {
    ArrowRight: Math.min(currentIndex + 1, lastIndex),
    ArrowDown: Math.min(currentIndex + 1, lastIndex),
    ArrowLeft: Math.max(currentIndex - 1, 0),
    ArrowUp: Math.max(currentIndex - 1, 0),
    Home: 0,
    End: lastIndex,
  };
  const targetIndex = targetIndexByKey[key];
  if (targetIndex === undefined) {
    return;
  }
  chips[targetIndex].focus();
}

function handleSummaryChipKeydown(event) {
  if (!["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"].includes(event.key)) {
    return;
  }
  event.preventDefault();
  focusSummaryChip(event.currentTarget, event.key);
}

function renderList(title, items) {
  const section = document.createElement("section");
  section.className = "answer-section";
  section.id = answerSectionId(title);
  section.tabIndex = -1;
  const hasItems = Array.isArray(items) && items.length > 0;
  section.classList.toggle("is-empty", !hasItems);

  const heading = document.createElement("h3");
  heading.textContent = sectionLabels[title] || title;
  section.appendChild(heading);

  const list = document.createElement("ul");
  const safeItems = hasItems ? items : ["本答案无内容"];
  safeItems.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
  section.appendChild(list);
  return section;
}

function renderErrorSection(payload) {
  const section = document.createElement("section");
  section.className = "answer-section is-error";

  const heading = document.createElement("h3");
  heading.textContent = "错误";
  section.appendChild(heading);

  const list = document.createElement("ul");
  [payload.message || payload.error || "Unknown UI error"].forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
  section.appendChild(list);
  return section;
}

function renderAnswerSectionSummary(payload) {
  const summaryItems = document.getElementById("answer-section-summary-items");
  summaryItems.replaceChildren(...sections.map((sectionName) => {
    const items = Array.isArray(payload[sectionName]) ? payload[sectionName] : [];
    const count = items.length;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = count > 0 ? "summary-chip" : "summary-chip is-empty";
    chip.setAttribute("aria-controls", answerSectionId(sectionName));
    chip.setAttribute("aria-describedby", "answer-section-keyboard-hint");
    chip.textContent = count > 0
      ? `${sectionLabels[sectionName] || sectionName} ${count} 条`
      : `${sectionLabels[sectionName] || sectionName} 0 条 — 本答案为空`;
    chip.addEventListener("click", () => focusAnswerSection(sectionName));
    chip.addEventListener("keydown", handleSummaryChipKeydown);
    return chip;
  }));
}

function renderAnswerSectionSummaryUnavailable() {
  const summaryItems = document.getElementById("answer-section-summary-items");
  const chip = document.createElement("span");
  chip.className = "summary-chip is-error";
  chip.textContent = "UI/API 错误时分区摘要不可用。";
  summaryItems.replaceChildren(chip);
}

function expandHighlight(value) {
  if (!value) {
    return [];
  }
  return nodeAliases[value] || [value];
}

function highlightedNodesForPayload(payload) {
  return Array.from(new Set([
    ...expandHighlight(payload.matched_node),
    ...expandHighlight(payload.target_logic),
  ]));
}

function highlightChain(payload) {
  const highlighted = new Set(highlightedNodesForPayload(payload));
  document.querySelectorAll("[data-node]").forEach((node) => {
    node.classList.remove("is-blocked", "is-inactive");
    node.classList.toggle("is-active", highlighted.has(node.dataset.node));
  });
}

function clearHighlight() {
  document.querySelectorAll("[data-node]").forEach((node) => {
    node.classList.remove("is-active", "is-blocked", "is-inactive");
  });
}

function applyLeverNodeStates(nodes) {
  const states = new Map(nodes.map((node) => [node.id, node]));
  document.querySelectorAll("[data-node]").forEach((element) => {
    const node = states.get(element.dataset.node);
    const state = node ? node.state : "inactive";
    element.classList.remove("is-active", "is-blocked", "is-inactive");
    element.classList.add(`is-${state}`);
    element.dataset.state = state;
    if (node) {
      const blockers = node.blocked_by && node.blocked_by.length
        ? ` | blocked_by=${node.blocked_by.join(",")}`
        : "";
      element.title = `${node.label} | ${node.source} | state=${state}${blockers}`;
    }
  });
}

function renderHighlightExplanation(payload) {
  const highlightedNodes = highlightedNodesForPayload(payload);
  const highlightedLabels = highlightedNodes.map((node) => nodeLabels[node] || node);

  document.getElementById("highlight-payload-fields").textContent = (
    `答案关联：意图=${textOrDash(payload.intent)}；` +
    `命中节点=${textOrDash(payload.matched_node)}；` +
    `目标逻辑=${textOrDash(payload.target_logic)}。`
  );
  document.getElementById("highlight-node-list").textContent = (
    `高亮节点：${highlightedLabels.length ? highlightedLabels.join("、") : "-"}`
  );

  const explanationItems = [
    "高亮来自答案里的命中节点 / 目标逻辑，以及现有前端别名映射。",
  ];
  if (payload.matched_node === "logic4->thr_lock") {
    explanationItems.push("链路桥接：L4 是上游逻辑门，THR_LOCK 是下游释放命令。");
  }
  if (highlightedNodes.includes("logic3")) {
    explanationItems.push("L3 相关答案会同时点亮 EEC / PLS / PDU 命令子节点。");
  }
  if (payload.matched_node === "throttle_lock_release_cmd" || highlightedNodes.includes("thr_lock")) {
    explanationItems.push("THR_LOCK 相关答案会点亮释放命令关联；证据 / 风险区给出诊断上下文。");
  }
  explanationItems.push(
    "这里只表示答案关联，不是完整因果证明或真实物理根因证明。",
  );

  const list = document.getElementById("highlight-explanation-list");
  list.replaceChildren(...explanationItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function clearHighlightExplanation() {
  document.getElementById("highlight-payload-fields").textContent = "答案关联：UI/API 错误。";
  document.getElementById("highlight-node-list").textContent = "高亮节点：-";
  const list = document.getElementById("highlight-explanation-list");
  const item = document.createElement("li");
  item.textContent = "UI/API 错误时不显示链路高亮。";
  list.replaceChildren(item);
}

function setStatus(message, mode) {
  const status = document.getElementById("ui-status");
  status.textContent = message;
  status.classList.toggle("is-loading", mode === "loading");
  status.classList.toggle("is-error", mode === "error");
}

function syncSelectedPrompt(prompt) {
  const normalizedPrompt = prompt.trim();
  let selectedPrompt = "";
  document.querySelectorAll("[data-prompt]").forEach((button) => {
    const isSelected = button.dataset.prompt.trim() === normalizedPrompt;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", isSelected ? "true" : "false");
    if (isSelected) {
      selectedPrompt = button.dataset.prompt;
    }
  });

  const selectedExample = document.getElementById("selected-example");
  selectedExample.textContent = selectedPrompt
    ? `当前示例：${selectedPrompt}`
    : "当前示例：自定义问题";
}

function setResultSourceInfo(modeText, payloadNote) {
  document.getElementById("result-source-mode").textContent = modeText;
  document.getElementById("result-payload-note").textContent = payloadNote;
}

function setLeverResultMode(modeText) {
  document.getElementById("lever-result-mode").textContent = modeText;
}

function renderTraLockState(payload) {
  const traLock = payload.tra_lock || {};
  const leverInput = document.getElementById("lever-tra");
  const badge = document.getElementById("lever-lock-badge");
  const status = document.getElementById("lever-lock-status");
  const conditionalRange = document.getElementById("lever-conditional-range");
  const boundaryUnlockReady = Boolean(traLock.boundary_unlock_ready);
  const visualReverseMin = Number(
    traLock.visual_reverse_min_deg
      ?? leverInput.min
      ?? -32,
  );
  const allowedReverseMin = Number(
    traLock.allowed_reverse_min_deg
      ?? payload.input?.tra_deg
      ?? leverInput.min
      ?? -14,
  );
  const effectiveTra = Number(
    traLock.effective_tra_deg
      ?? payload.input?.tra_deg
      ?? leverInput.value
      ?? 0,
  );
  const locked = Boolean(traLock.locked);

  leverInput.min = String(visualReverseMin);
  leverInput.value = String(effectiveTra);
  leverInput.dataset.allowedReverseMin = String(allowedReverseMin);
  leverInput.dataset.boundaryUnlockReady = boundaryUnlockReady ? "true" : "false";
  leverInput.dataset.deepRangeLocked = locked ? "true" : "false";

  badge.textContent = locked ? "深拉区关闭" : "深拉区已开放";
  badge.classList.toggle("is-locked", locked);
  badge.classList.toggle("is-unlocked", !locked);
  if (conditionalRange) {
    conditionalRange.dataset.boundaryUnlockReady = boundaryUnlockReady ? "true" : "false";
    conditionalRange.classList.toggle("is-locked", locked);
    conditionalRange.classList.toggle("is-open", !locked);
    conditionalRange.textContent = locked
      ? `条件深拉区 ${visualReverseMin.toFixed(0)}° ~ ${allowedReverseMin.toFixed(0)}°（关闭）`
      : `条件深拉区 ${visualReverseMin.toFixed(0)}° ~ -14°（已开放）`;
  }
  status.textContent = traLock.message || (
    locked
      ? "当前可以先自由左拉到 -14° 门槛；满足 L4 后才继续开放 -32° 到 -14° 深拉区。"
      : "L4 已满足：TRA 现在可以继续向左进入 -32° 深拉区，也可以自由回到 0°。"
  );
}

function setLeverResultPlaceholder(headline, blocker, nextStep, evidenceItems, modeText) {
  setLeverResultMode(modeText);
  document.getElementById("lever-headline").textContent = headline;
  document.getElementById("lever-blocker").textContent = blocker;
  document.getElementById("lever-next-step").textContent = nextStep;
  const evidenceList = document.getElementById("lever-evidence-list");
  evidenceList.replaceChildren(...evidenceItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderPayload(payload) {
  document.getElementById("intent-value").textContent = textOrDash(payload.intent);
  document.getElementById("matched-node-value").textContent = textOrDash(payload.matched_node);
  document.getElementById("target-logic-value").textContent = textOrDash(payload.target_logic);
  setResultSourceInfo(
    "当前来源：受控 prompt / POST /api/demo / DemoAnswer。",
    "结构化结果、高亮解释和 Raw JSON 共用同一份 DemoAnswer payload。",
  );
  setLeverResultPlaceholder(
    "当前结果来自 DemoAnswer；如需当前结论，请重新拖动拉杆或使用场景预设。",
    "当前不是 lever snapshot。",
    "继续读 Structured answer，或重新请求 lever snapshot。",
    ["当前结果区显示的是 DemoAnswer，不复用上一次 lever snapshot。"],
    "当前结论来源：问答模式已激活；lever snapshot rails 已暂停。",
  );

  const structuredOutput = document.getElementById("structured-output");
  renderAnswerSectionSummary(payload);
  structuredOutput.replaceChildren(...sections.map((section) => renderList(section, payload[section])));

  document.getElementById("raw-json").textContent = JSON.stringify(payload, null, 2);
  highlightChain(payload);
  renderHighlightExplanation(payload);
}

function formatBool(value) {
  return value ? "ON" : "OFF";
}

function renderLeverFoldedSections(payload) {
  const detailPayload = {
    evidence: payload.evidence || [],
    outcome: [
      payload.summary?.headline,
      payload.summary?.next_step,
    ].filter(Boolean),
    possible_causes: [payload.summary?.blocker].filter(Boolean),
    required_changes: [],
    risks: payload.risks || [],
  };
  renderAnswerSectionSummary(detailPayload);

  const details = document.createElement("details");
  details.className = "lever-folded-sections";
  const summary = document.createElement("summary");
  summary.textContent = "展开证据 / 可能原因 / 风险";
  details.appendChild(summary);
  sections.forEach((sectionName) => {
    details.appendChild(renderList(sectionName, detailPayload[sectionName]));
  });
  document.getElementById("structured-output").replaceChildren(details);
}

function renderLeverSnapshot(payload) {
  const hud = payload.hud || {};
  const outputs = payload.outputs || {};
  const summary = payload.summary || {};
  const tra = Number(hud.tra_deg ?? payload.input?.tra_deg ?? 0);
  const feedbackMode = payload.input?.feedback_mode || payload.mode || "auto_scrubber";
  const deployPosition = Number(
    feedbackMode === "manual_feedback_override"
      ? payload.input?.deploy_position_percent ?? hud.deploy_position_percent ?? 0
      : hud.deploy_position_percent ?? 0,
    );

  // Update chain topology with fresh truth evaluation from lever-snapshot.
  // active_logic_node_ids drives logic-gate node active/inactive state.
  // asserted_component_values drives input/condition node values (sw1, RA, VDT, etc.).
  const activeLogicNodeIds = [
    outputs.logic1_active && "logic1",
    outputs.logic2_active && "logic2",
    outputs.logic3_active && "logic3",
    outputs.logic4_active && "logic4",
  ].filter(Boolean);
  const truthEvaluation = {
    active_logic_node_ids: activeLogicNodeIds,
    asserted_component_values: {
      sw1: hud.sw1,
      sw2: hud.sw2,
      radio_altitude_ft: hud.radio_altitude_ft,
      engine_running: hud.engine_running,
      aircraft_on_ground: hud.aircraft_on_ground,
      reverser_inhibited: hud.reverser_inhibited,
      eec_enable: hud.eec_enable,
      n1k: hud.n1k,
      tra_deg: hud.tra_deg,
      tls_unlocked_ls: hud.tls_unlocked_ls,
      all_pls_unlocked_ls: hud.all_pls_unlocked_ls,
      deploy_90_percent_vdt: hud.deploy_90_percent_vdt,
      deploy_position_percent: hud.deploy_position_percent,
      tls_115vac_cmd: outputs.tls_115vac_cmd,
      etrac_540vdc_cmd: outputs.etrac_540vdc_cmd,
      eec_deploy_cmd: outputs.eec_deploy_cmd,
      pls_power_cmd: outputs.pls_power_cmd,
      pdu_motor_cmd: outputs.pdu_motor_cmd,
      throttle_electronic_lock_release_cmd: outputs.throttle_electronic_lock_release_cmd,
    },
  };
  applySystemNodeStates(_systemSnapshotNodes || [], truthEvaluation);

  renderTraLockState(payload);
  document.getElementById("condition-feedback-mode").value = feedbackMode;
  document.getElementById("condition-deploy-position").disabled = feedbackMode !== "manual_feedback_override";
  document.getElementById("condition-deploy-position").value = Number.isFinite(deployPosition)
    ? String(deployPosition)
    : "0";

  document.getElementById("lever-tra-value").textContent = `${tra.toFixed(1)}°`;
  document.getElementById("hud-tra").textContent = `${tra.toFixed(1)}°`;
  document.getElementById("hud-switches").textContent = `SW1 ${formatBool(hud.sw1)} / SW2 ${formatBool(hud.sw2)}`;
  document.getElementById("hud-ra").textContent = `${hud.radio_altitude_ft ?? "-"} ft`;
  document.getElementById("hud-engine-ground").textContent = `ENG ${formatBool(hud.engine_running)} / GND ${formatBool(hud.aircraft_on_ground)}`;
  document.getElementById("hud-inhibited").textContent = formatBool(hud.reverser_inhibited);
  document.getElementById("hud-eec-enable").textContent = formatBool(hud.eec_enable);
  document.getElementById("hud-n1k").textContent = `${hud.n1k ?? "-"} / ${hud.max_n1k_deploy_limit ?? "-"}`;
  document.getElementById("hud-locks").textContent = `TLS ${formatBool(hud.tls_unlocked_ls)} / PLS ${formatBool(hud.all_pls_unlocked_ls)}`;
  document.getElementById("hud-position").textContent = `${hud.deploy_position_percent ?? "-"}% / VDT90 ${formatBool(hud.deploy_90_percent_vdt)}`;
  document.getElementById("lever-status").textContent = payload.model_note || "受控拉杆轨迹快照。";
  syncConditionReadouts();

  document.getElementById("intent-value").textContent = "lever_snapshot";
  document.getElementById("matched-node-value").textContent = (
    outputs.logic4_active ? "logic4->thr_lock"
      : outputs.logic3_active ? "logic3"
        : hud.sw2 ? "sw2"
          : hud.sw1 ? "sw1"
            : "-"
  );
  document.getElementById("target-logic-value").textContent = (
    outputs.logic4_active ? "logic4"
      : outputs.logic3_active ? "logic3"
        : outputs.logic2_active ? "logic2"
          : outputs.logic1_active ? "logic1"
            : "-"
  );
  setResultSourceInfo(
    "当前来源：拉杆快照 / POST /api/lever-snapshot。",
    "当前结论、折叠证据区和 Raw JSON 共用同一份 lever snapshot payload。",
  );
  setLeverResultMode("当前结论来源：lever snapshot / POST /api/lever-snapshot。");

  document.getElementById("lever-headline").textContent = summary.headline || "拉杆快照已更新。";
  document.getElementById("lever-blocker").textContent = summary.blocker || "-";
  document.getElementById("lever-next-step").textContent = summary.next_step || "-";
  const evidenceItems = [
    ...(payload.evidence || []),
    ...(payload.risks || []).map((risk) => `risk: ${risk}`),
  ];
  const evidenceList = document.getElementById("lever-evidence-list");
  evidenceList.replaceChildren(...evidenceItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));

  applyLeverNodeStates(payload.nodes || []);
  document.getElementById("highlight-payload-fields").textContent = (
    `拉杆快照：TRA=${tra.toFixed(1)}°；mode=${payload.mode || "-"}。`
  );
  document.getElementById("highlight-node-list").textContent = (
    `点亮节点：${(payload.nodes || [])
      .filter((node) => node.state === "active")
      .map((node) => node.label)
      .join("、") || "-"}`
  );
  const list = document.getElementById("highlight-explanation-list");
  list.replaceChildren(...[
    "active / blocked / inactive 来自后端快照里的 node state。",
    "controller 条件由 DeployController.explain(...) 生成，前端不硬编码控制真值。",
    "L4 / THR_LOCK 依赖 VDT90 / deploy_90_percent_vdt 的 simplified plant feedback。",
    feedbackMode === "manual_feedback_override"
      ? "当前处于 manual feedback override：deploy feedback 由诊断演示控件覆盖，不是新的控制真值。"
      : "当前处于 auto scrubber：deploy feedback 来自受控 pullback scrubber。",
    "这是受控演示轨迹，不是完整实时物理仿真。",
  ].map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));

  renderLeverFoldedSections(payload);
  document.getElementById("raw-json").textContent = JSON.stringify(payload, null, 2);
}

function renderErrorPayload(payload, statusMessage) {
  const normalizedPayload = {
    error: payload.error || "ui_error",
    message: payload.message || statusMessage,
  };
  document.getElementById("intent-value").textContent = "ui_error";
  document.getElementById("matched-node-value").textContent = "-";
  document.getElementById("target-logic-value").textContent = "-";
  setResultSourceInfo(
    "当前来源：UI/API 错误。",
    "当前没有生成新的业务 payload；请先修复输入或网络错误。",
  );
  setLeverResultPlaceholder(
    "当前没有新的业务 payload；请先修复错误再看当前结论。",
    "当前是 UI/API 错误状态。",
    "修复输入或网络错误后，再重新请求 DemoAnswer 或 lever snapshot。",
    [normalizedPayload.message || "UI/API 错误。"],
    "当前结论来源：UI/API 错误；lever snapshot rails 已暂停。",
  );
  renderAnswerSectionSummaryUnavailable();
  document.getElementById("structured-output").replaceChildren(renderErrorSection(normalizedPayload));
  document.getElementById("raw-json").textContent = JSON.stringify(normalizedPayload, null, 2);
  clearHighlight();
  clearHighlightExplanation();
  setStatus(statusMessage, "error");
}

async function runPrompt(prompt, requestId = beginInteractionRequest()) {
  let response;
  try {
    response = await fetch("/api/demo", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({prompt}),
    });
  } catch (error) {
    if (!isLatestInteractionRequest(requestId)) {
      return {stale: true};
    }
    throw error;
  }
  const payload = await response.json().catch(() => ({
    error: "invalid_json_response",
    message: "API returned a response that was not valid JSON.",
  }));
  if (!isLatestInteractionRequest(requestId)) {
    return {stale: true};
  }
  if (!response.ok) {
    renderErrorPayload(
      payload,
      `API error ${response.status}: ${payload.message || payload.error || "request failed"}`,
    );
    return {stale: false};
  }
  renderPayload(payload);
  setStatus("答案已生成。高亮表示答案关联，不是完整因果证明。", "ready");
  return {stale: false};
}

function syncConditionReadouts() {
  const ra = Number(document.getElementById("condition-ra").value);
  const n1k = Number(document.getElementById("condition-n1k").value);
  const deployPosition = Number(document.getElementById("condition-deploy-position").value);
  const feedbackMode = document.getElementById("condition-feedback-mode").value;
  document.getElementById("condition-ra-value").textContent = `${ra.toFixed(1)} ft`;
  document.getElementById("condition-n1k-value").textContent = n1k.toFixed(1);
  document.getElementById("condition-deploy-position-value").textContent = `${deployPosition.toFixed(0)}%`;
  document.getElementById("condition-deploy-position").disabled = feedbackMode !== "manual_feedback_override";
}

function applyLeverPresetPayload(payload) {
  document.getElementById("lever-tra").value = String(clampLeverTraToUnlockedBand(Number(payload.tra_deg)));
  document.getElementById("condition-ra").value = String(payload.radio_altitude_ft);
  document.getElementById("condition-engine-running").checked = payload.engine_running;
  document.getElementById("condition-aircraft-ground").checked = payload.aircraft_on_ground;
  document.getElementById("condition-reverser-inhibited").checked = payload.reverser_inhibited;
  document.getElementById("condition-eec-enable").checked = payload.eec_enable;
  document.getElementById("condition-n1k").value = String(payload.n1k);
  document.getElementById("condition-n1k-limit").value = String(payload.max_n1k_deploy_limit);
  document.getElementById("condition-feedback-mode").value = payload.feedback_mode;
  document.getElementById("condition-deploy-position").value = String(payload.deploy_position_percent);
  document.getElementById("lever-tra-value").textContent = `${Number(payload.tra_deg).toFixed(1)}°`;
  syncConditionReadouts();
}

function syncLeverPresetSelection(presetKey) {
  const preset = leverPresets[presetKey];
  document.querySelectorAll("[data-lever-preset]").forEach((button) => {
    const isSelected = button.dataset.leverPreset === presetKey;
    button.classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", isSelected ? "true" : "false");
  });
  document.getElementById("lever-preset-status").textContent = preset
    ? preset.status
    : defaultLeverStartupStatus;
}

function collectLeverSnapshotPayload(traDeg) {
  const traValue = traDeg === undefined
    ? Number(document.getElementById("lever-tra").value)
    : Number(traDeg);
  const clampedTraValue = clampLeverTraToUnlockedBand(traValue);
  return {
    tra_deg: clampedTraValue,
    radio_altitude_ft: Number(document.getElementById("condition-ra").value),
    engine_running: document.getElementById("condition-engine-running").checked,
    aircraft_on_ground: document.getElementById("condition-aircraft-ground").checked,
    reverser_inhibited: document.getElementById("condition-reverser-inhibited").checked,
    eec_enable: document.getElementById("condition-eec-enable").checked,
    n1k: Number(document.getElementById("condition-n1k").value),
    max_n1k_deploy_limit: Number(document.getElementById("condition-n1k-limit").value),
    feedback_mode: document.getElementById("condition-feedback-mode").value,
    deploy_position_percent: Number(document.getElementById("condition-deploy-position").value),
  };
}

async function runLeverSnapshot(traDeg, requestId = beginInteractionRequest()) {
  const requestPayload = typeof traDeg === "object"
    ? traDeg
    : collectLeverSnapshotPayload(traDeg);
  let response;
  try {
    response = await fetch("/api/lever-snapshot", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(requestPayload),
    });
  } catch (error) {
    if (!isLatestInteractionRequest(requestId)) {
      return {stale: true};
    }
    throw error;
  }
  const payload = await response.json().catch(() => ({
    error: "invalid_json_response",
    message: "Lever API returned a response that was not valid JSON.",
  }));
  if (!isLatestInteractionRequest(requestId)) {
    return {stale: true};
  }
  if (!response.ok) {
    renderErrorPayload(
      payload,
      `Lever API error ${response.status}: ${payload.message || payload.error || "request failed"}`,
    );
    return {stale: false};
  }
  renderLeverSnapshot(payload);
  return {stale: false};
}

async function loadMonitorTimeline() {
  let response;
  try {
    response = await fetch("/api/monitor-timeline", {
      method: "GET",
      headers: {"Accept": "application/json"},
    });
  } catch (error) {
    renderMonitorTimelineError(
      `网络错误：UI 无法访问 GET /api/monitor-timeline。${String(error.message || error)}`,
    );
    return;
  }

  const payload = await response.json().catch(() => ({
    error: "invalid_json_response",
    message: "Monitor timeline API returned invalid JSON.",
  }));

  if (!response.ok) {
    renderMonitorTimelineError(
      `监控时间线读取失败：${payload.message || payload.error || `HTTP ${response.status}`}`,
    );
    return;
  }

  renderMonitorTimeline(payload);
}

function setBusy(isBusy) {
  const button = document.getElementById("submit-button");
  button.disabled = isBusy;
  document.querySelectorAll("[data-prompt]").forEach((exampleButton) => {
    exampleButton.disabled = isBusy;
  });
  document.body.classList.toggle("is-loading", isBusy);
  button.textContent = isBusy ? "确定性推理中..." : "运行演示";
}

document.addEventListener("DOMContentLoaded", () => {
  // P13 system switcher
  const systemSelector = document.getElementById("system-selector");
  if (systemSelector) {
    systemSelector.addEventListener("change", () => {
      handleSystemSwitch(systemSelector.value);
    });
    // Bootstrap with default system
    handleSystemSwitch(systemSelector.value);
  }

  // System-specific input panel: wire up "Apply Snapshot" buttons and live readouts
  document.querySelectorAll(".system-snapshot-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const systemId = btn.dataset.system;
      if (systemId) runSystemSnapshot(systemId);
    });
  });

  // Landing Gear: live readouts for range inputs
  const lgHydInput = document.getElementById("lg-hyd-pressure");
  const lgHydOutput = document.getElementById("lg-hyd-pressure-value");
  if (lgHydInput && lgHydOutput) {
    lgHydInput.addEventListener("input", () => { lgHydOutput.textContent = lgHydInput.value + " psi"; });
  }
  const lgPosInput = document.getElementById("lg-gear-position");
  const lgPosOutput = document.getElementById("lg-gear-position-value");
  if (lgPosInput && lgPosOutput) {
    lgPosInput.addEventListener("input", () => { lgPosOutput.textContent = lgPosInput.value + "%"; });
  }

  // Bleed Air: live readouts
  const baInletInput = document.getElementById("ba-inlet-pressure");
  const baInletOutput = document.getElementById("ba-inlet-pressure-value");
  if (baInletInput && baInletOutput) {
    baInletInput.addEventListener("input", () => { baInletOutput.textContent = parseFloat(baInletInput.value).toFixed(1) + " psi"; });
  }
  const baOutletInput = document.getElementById("ba-outlet-pressure");
  const baOutletOutput = document.getElementById("ba-outlet-pressure-value");
  if (baOutletInput && baOutletOutput) {
    baOutletInput.addEventListener("input", () => { baOutletOutput.textContent = parseFloat(baOutletInput.value).toFixed(1) + " psi"; });
  }

  // EFDS: live readouts
  const efdsRadarInput = document.getElementById("efds-alt-radar");
  const efdsRadarOutput = document.getElementById("efds-alt-radar-value");
  if (efdsRadarInput && efdsRadarOutput) {
    efdsRadarInput.addEventListener("input", () => { efdsRadarOutput.textContent = efdsRadarInput.value + " ft"; });
  }
  const efdsBaroInput = document.getElementById("efds-alt-baro");
  const efdsBaroOutput = document.getElementById("efds-alt-baro-value");
  if (efdsBaroInput && efdsBaroOutput) {
    efdsBaroInput.addEventListener("input", () => { efdsBaroOutput.textContent = efdsBaroInput.value + " ft"; });
  }
  const efdsTempInput = document.getElementById("efds-temp-ext");
  const efdsTempOutput = document.getElementById("efds-temp-ext-value");
  if (efdsTempInput && efdsTempOutput) {
    efdsTempInput.addEventListener("input", () => { efdsTempOutput.textContent = efdsTempInput.value + "°C"; });
  }

  const form = document.getElementById("demo-form");
  const promptInput = document.getElementById("demo-prompt");
  const leverInput = document.getElementById("lever-tra");
  const monitorRefreshButton = document.getElementById("monitor-refresh-button");
  const conditionInputs = Array.from(
    document.querySelectorAll(
      ".condition-panel input, .condition-panel select, .lever-live-grid input, .lever-live-grid select",
    ),
  );
  let leverSnapshotTimer = null;

  function scheduleLeverSnapshot() {
    window.clearTimeout(leverSnapshotTimer);
    syncConditionReadouts();
    document.getElementById("lever-status").textContent = "拉杆快照计算中...";
    leverSnapshotTimer = window.setTimeout(async () => {
      try {
        await runLeverSnapshot(collectLeverSnapshotPayload());
      } catch (error) {
        renderErrorPayload(
          {error: "lever_network_error", message: String(error.message || error)},
          "网络错误：UI 无法访问 POST /api/lever-snapshot。",
        );
      }
    }, 80);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) {
      renderErrorPayload(
        {error: "missing_prompt", message: "请输入一个受控 demo prompt。"},
        "请输入一个受控 demo prompt。",
      );
      return;
    }

    window.clearTimeout(leverSnapshotTimer);
    setBusy(true);
    setStatus("确定性推理中...", "loading");
    try {
      await runPrompt(prompt);
    } catch (error) {
      renderErrorPayload(
        {error: "network_error", message: String(error.message || error)},
        "网络错误：UI 无法访问 POST /api/demo。",
      );
    } finally {
      setBusy(false);
    }
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      promptInput.value = button.dataset.prompt;
      syncSelectedPrompt(promptInput.value);
      form.requestSubmit();
    });
  });

  promptInput.addEventListener("input", () => {
    syncSelectedPrompt(promptInput.value);
  });

  promptInput.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  leverInput.addEventListener("input", () => {
    syncLeverPresetSelection(null);
    const clampedValue = clampLeverTraToUnlockedBand(Number(leverInput.value));
    leverInput.value = String(clampedValue);
    document.getElementById("lever-tra-value").textContent = `${clampedValue.toFixed(1)}°`;
    scheduleLeverSnapshot();
  });
  conditionInputs.forEach((input) => {
    input.addEventListener("input", () => {
      syncLeverPresetSelection(null);
      scheduleLeverSnapshot();
    });
    input.addEventListener("change", () => {
      syncLeverPresetSelection(null);
      scheduleLeverSnapshot();
    });
  });
  document.querySelectorAll("[data-lever-preset]").forEach((button) => {
    button.addEventListener("click", async () => {
      const preset = leverPresets[button.dataset.leverPreset];
      if (!preset) {
        return;
      }
      window.clearTimeout(leverSnapshotTimer);
      applyLeverPresetPayload(preset.payload);
      syncLeverPresetSelection(button.dataset.leverPreset);
      document.getElementById("lever-status").textContent = `${preset.label} 计算中...`;
      try {
        await runLeverSnapshot(collectLeverSnapshotPayload());
      } catch (error) {
        renderErrorPayload(
          {error: "lever_network_error", message: String(error.message || error)},
          "网络错误：UI 无法访问 POST /api/lever-snapshot。",
        );
      }
    });
  });

  monitorRefreshButton?.addEventListener("click", () => {
    document.getElementById("monitor-status").textContent = "监控时间线刷新中...";
    document.getElementById("monitor-status").classList.remove("is-error");
    loadMonitorTimeline();
  });

  syncSelectedPrompt(promptInput.value);
  syncConditionReadouts();
  syncLeverPresetSelection(null);
  runLeverSnapshot(collectLeverSnapshotPayload()).catch((error) => {
    renderErrorPayload(
      {error: "lever_network_error", message: String(error.message || error)},
      "网络错误：UI 无法访问 POST /api/lever-snapshot。",
    );
  });
  loadMonitorTimeline();
});

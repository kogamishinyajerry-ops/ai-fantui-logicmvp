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

function textOrDash(value) {
  return value === null || value === undefined || value === "" ? "-" : value;
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

function renderPayload(payload) {
  document.getElementById("intent-value").textContent = textOrDash(payload.intent);
  document.getElementById("matched-node-value").textContent = textOrDash(payload.matched_node);
  document.getElementById("target-logic-value").textContent = textOrDash(payload.target_logic);

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
  renderAnswerSectionSummaryUnavailable();
  document.getElementById("structured-output").replaceChildren(renderErrorSection(normalizedPayload));
  document.getElementById("raw-json").textContent = JSON.stringify(normalizedPayload, null, 2);
  clearHighlight();
  clearHighlightExplanation();
  setStatus(statusMessage, "error");
}

async function runPrompt(prompt) {
  const response = await fetch("/api/demo", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({prompt}),
  });
  const payload = await response.json().catch(() => ({
    error: "invalid_json_response",
    message: "API returned a response that was not valid JSON.",
  }));
  if (!response.ok) {
    renderErrorPayload(
      payload,
      `API error ${response.status}: ${payload.message || payload.error || "request failed"}`,
    );
    return;
  }
  renderPayload(payload);
  setStatus("答案已生成。高亮表示答案关联，不是完整因果证明。", "ready");
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

function collectLeverSnapshotPayload(traDeg) {
  const traValue = traDeg === undefined
    ? Number(document.getElementById("lever-tra").value)
    : Number(traDeg);
  return {
    tra_deg: traValue,
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

async function runLeverSnapshot(traDeg) {
  const requestPayload = typeof traDeg === "object"
    ? traDeg
    : collectLeverSnapshotPayload(traDeg);
  const response = await fetch("/api/lever-snapshot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(requestPayload),
  });
  const payload = await response.json().catch(() => ({
    error: "invalid_json_response",
    message: "Lever API returned a response that was not valid JSON.",
  }));
  if (!response.ok) {
    renderErrorPayload(
      payload,
      `Lever API error ${response.status}: ${payload.message || payload.error || "request failed"}`,
    );
    return;
  }
  renderLeverSnapshot(payload);
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
  const form = document.getElementById("demo-form");
  const promptInput = document.getElementById("demo-prompt");
  const leverInput = document.getElementById("lever-tra");
  const conditionInputs = Array.from(document.querySelectorAll(".condition-panel input, .condition-panel select"));
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
    document.getElementById("lever-tra-value").textContent = `${Number(leverInput.value).toFixed(1)}°`;
    scheduleLeverSnapshot();
  });
  conditionInputs.forEach((input) => {
    input.addEventListener("input", scheduleLeverSnapshot);
    input.addEventListener("change", scheduleLeverSnapshot);
  });

  syncSelectedPrompt(promptInput.value);
  syncConditionReadouts();
  runLeverSnapshot(collectLeverSnapshotPayload()).catch((error) => {
    renderErrorPayload(
      {error: "lever_network_error", message: String(error.message || error)},
      "网络错误：UI 无法访问 POST /api/lever-snapshot。",
    );
  });
});

const workbenchBootstrapPath = "/api/workbench/bootstrap";
const workbenchBundlePath = "/api/workbench/bundle";
const workbenchRepairPath = "/api/workbench/repair";
const workbenchArchiveRestorePath = "/api/workbench/archive-restore";
const workbenchRecentArchivesPath = "/api/workbench/recent-archives";
const workbenchPacketWorkspaceStorageKey = "well-harness-workbench-packet-workspace-v1";
const draftDesignStateKey = "draft_design_state";
const workbenchPersistedFieldIds = [
  "workbench-scenario-id",
  "workbench-fault-mode-id",
  "workbench-sample-period",
  "workbench-archive-toggle",
  "workbench-archive-manifest-path",
  "workbench-handoff-note",
  "workbench-observed-symptoms",
  "workbench-evidence-links",
  "workbench-root-cause",
  "workbench-repair-action",
  "workbench-validation-after-fix",
  "workbench-residual-risk",
  "workbench-logic-change",
  "workbench-reliability-gain",
  "workbench-guardrail-note",
];

const defaultReferenceResolution = {
  rootCause: "Pressure sensor bias was confirmed during troubleshooting.",
  repairAction: "Recalibrated the sensor path.",
  validationAfterFix: "Acceptance replay completed after the repair.",
  residualRisk: "Watch for future sensor drift.",
  logicChange: "Add a pressure plausibility cross-check before enabling the deploy chain.",
  reliabilityGain: "A clearer plausibility guard should fail earlier and reduce ambiguity around sensor drift.",
  guardrailNote: "Emit a guardrail event when the pressure ramp diverges from the unlock chain expectation.",
};

let bootstrapPayload = null;
let latestWorkbenchRequestId = 0;
let currentWorkbenchRunLabel = "手动生成";
let workbenchRecentArchives = [];
let workbenchRunHistory = [];
let selectedWorkbenchHistoryId = "";
let workbenchHistorySequence = 0;
let currentWorkbenchViewMode = "empty";
let workbenchPacketRevisionHistory = [];
let selectedWorkbenchPacketRevisionId = "";
let workbenchPacketRevisionSequence = 0;
let suspendWorkbenchPacketWorkspacePersistence = false;
const maxWorkbenchRunHistory = 6;
const maxWorkbenchPacketRevisionHistory = 8;

function bootWorkbenchColumnSafely(columnName, bootFn) {
  try {
    bootFn();
  } catch (error) {
    const status = workbenchElement(`workbench-${columnName}-status`);
    if (status) {
      status.textContent = `${columnName} panel failed independently: ${error.message || error}`;
      status.dataset.tone = "warning";
    }
  }
}

function bootWorkbenchControlPanel() {
  const status = workbenchElement("workbench-control-status");
  if (status) {
    status.textContent = "Control panel ready. Scenario actions are staged for E07+.";
    status.dataset.tone = "ready";
  }
}

function bootWorkbenchDocumentPanel() {
  const status = workbenchElement("workbench-document-status");
  if (status) {
    status.textContent = "Document panel ready. Text-range annotation arrives in E07.";
    status.dataset.tone = "ready";
  }
}

function bootWorkbenchCircuitPanel() {
  const status = workbenchElement("workbench-circuit-status");
  if (status) {
    status.textContent = "Circuit panel ready. Overlay annotation arrives in E07.";
    status.dataset.tone = "ready";
  }
}

function bootWorkbenchShell() {
  bootWorkbenchColumnSafely("control", bootWorkbenchControlPanel);
  bootWorkbenchColumnSafely("document", bootWorkbenchDocumentPanel);
  bootWorkbenchColumnSafely("circuit", bootWorkbenchCircuitPanel);
}

// P43 authority contract — written only via assignFrozenSpec; never mutated directly
let frozenSpec = null;

// P43 workflow state machine (P43-03)
let workflowState = "INIT";

const _workflowTransitions = {
  INIT:        { confirm_freeze: "FROZEN",      load_packet: "INIT" },
  FROZEN:      { start_gen: "GENERATING",       confirm_freeze: "FROZEN",   reiterate: "INIT" },
  GENERATING:  { gen_complete: "PANEL_READY",   gen_fail: "ERROR",          reiterate: "INIT" },
  PANEL_READY: { final_approve: "APPROVING",    start_gen: "GENERATING",    reiterate: "INIT" },
  APPROVING:   { approve_ok: "APPROVED",        approve_fail: "PANEL_READY" },
  APPROVED:    { archive: "ARCHIVING" },
  ARCHIVING:   { archive_ok: "ARCHIVED",        archive_fail: "APPROVED" },
  ARCHIVED:    {},
  ERROR:       { reiterate: "INIT" },
};

function dispatchWorkflowEvent(event) {
  const next = (_workflowTransitions[workflowState] || {})[event];
  if (next === undefined) {
    return false;
  }
  workflowState = next;
  updateWorkflowUI();
  return true;
}

function updateWorkflowUI() {
  const approveBtn  = workbenchElement("workbench-final-approve");
  const startGenBtn = workbenchElement("workbench-start-gen");
  const badge       = workbenchElement("workbench-workflow-state");

  // "冻结审批 Spec" enabled when spec is not yet frozen or after generation
  const approveEnabled = ["INIT", "PANEL_READY", "ANNOTATING", "WIRING"].includes(workflowState);
  // "生成 (Frozen Spec)" enabled only when a frozen spec exists
  const startGenEnabled = workflowState === "FROZEN";

  if (approveBtn)  approveBtn.disabled  = !approveEnabled;
  if (startGenBtn) startGenBtn.disabled = !startGenEnabled;
  if (badge) {
    badge.textContent    = workflowState;
    badge.dataset.state  = workflowState.toLowerCase();
  }
}

const workbenchPresets = {
  ready_archived: {
    label: "一键通过验收",
    archiveBundle: true,
    source: "reference",
    sourceStatus: "当前样例：参考样例。系统会直接跑完整 happy path 并生成 archive。",
    preparationMessage: "参考样例已就位，系统马上开始生成 ready bundle 并留档。",
  },
  blocked_follow_up: {
    label: "一键看阻塞态",
    archiveBundle: false,
    source: "template",
    sourceStatus: "当前样例：空白模板。系统会故意演示 clarification gate 如何把不完整 packet 拦下来。",
    preparationMessage: "空白模板已就位，系统马上演示阻塞态。",
  },
  ready_preview: {
    label: "一键快速预览",
    archiveBundle: false,
    source: "reference",
    sourceStatus: "当前样例：参考样例。系统会直接跑 ready bundle，但不生成 archive。",
    preparationMessage: "参考样例已就位，系统马上生成 ready bundle 供快速查看。",
  },
  archive_retry: {
    label: "一键留档复跑",
    archiveBundle: true,
    source: "reference",
    sourceStatus: "当前样例：参考样例。这个预设适合连续复跑，archive 会自动避开重名目录。",
    preparationMessage: "参考样例已就位，系统马上做一次带 archive 的复跑。",
  },
};

function workbenchElement(id) {
  return document.getElementById(id);
}

function beginWorkbenchRequest() {
  latestWorkbenchRequestId += 1;
  return latestWorkbenchRequestId;
}

function isLatestWorkbenchRequest(requestId) {
  return requestId === latestWorkbenchRequestId;
}

function setRequestStatus(message, tone = "neutral") {
  const element = workbenchElement("workbench-request-status");
  element.textContent = message;
  element.dataset.tone = tone;
}

function setPacketSourceStatus(message) {
  workbenchElement("workbench-packet-source-status").textContent = message;
  persistWorkbenchPacketWorkspace();
}

function setResultMode(message) {
  workbenchElement("workbench-result-mode").textContent = message;
}

function prettyJson(value) {
  return JSON.stringify(value, null, 2);
}

function shortPath(path) {
  if (!path) {
    return "(none)";
  }
  const parts = String(path).split("/");
  return parts[parts.length - 1] || String(path);
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeRecentWorkbenchArchiveEntries(entries) {
  if (!Array.isArray(entries)) {
    return [];
  }
  return entries
    .filter((entry) => entry && typeof entry === "object")
    .map((entry) => ({
      archive_dir: typeof entry.archive_dir === "string" ? entry.archive_dir : "",
      manifest_path: typeof entry.manifest_path === "string" ? entry.manifest_path : "",
      created_at_utc: typeof entry.created_at_utc === "string" ? entry.created_at_utc : "",
      system_id: typeof entry.system_id === "string" ? entry.system_id : "unknown_system",
      system_title: typeof entry.system_title === "string" ? entry.system_title : "",
      bundle_kind: typeof entry.bundle_kind === "string" ? entry.bundle_kind : "",
      ready_for_spec_build: Boolean(entry.ready_for_spec_build),
      selected_scenario_id: typeof entry.selected_scenario_id === "string" ? entry.selected_scenario_id : "",
      selected_fault_mode_id: typeof entry.selected_fault_mode_id === "string" ? entry.selected_fault_mode_id : "",
      has_workspace_handoff: Boolean(entry.has_workspace_handoff),
      has_workspace_snapshot: Boolean(entry.has_workspace_snapshot),
    }))
    .filter((entry) => entry.manifest_path || entry.archive_dir);
}

function summarizeRecentWorkbenchArchive(entry) {
  const state = entry.ready_for_spec_build ? "ready" : "blocked";
  const scenario = entry.selected_scenario_id || "未选 scenario";
  const faultMode = entry.selected_fault_mode_id || "未选 fault mode";
  const workspace = entry.has_workspace_snapshot
    ? "带工作区快照"
    : (entry.has_workspace_handoff ? "仅带交接摘要" : "仅带 bundle");
  return {
    badge: state === "ready" ? "可恢复 / ready" : "可恢复 / blocked",
    summary: `${scenario} / ${faultMode}`,
    detail: `${workspace} / ${shortPath(entry.archive_dir || entry.manifest_path)}`,
  };
}

function buildRecentWorkbenchArchiveEntryFromBundlePayload(payload) {
  const archive = payload && payload.archive ? payload.archive : null;
  const bundle = payload && payload.bundle ? payload.bundle : {};
  if (!archive) {
    return null;
  }
  return {
    archive_dir: archive.archive_dir || "",
    manifest_path: archive.manifest_json_path || "",
    created_at_utc: archive.created_at_utc || "",
    system_id: bundle.system_id || "unknown_system",
    system_title: bundle.system_title || "",
    bundle_kind: bundle.bundle_kind || "",
    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
    selected_scenario_id: bundle.selected_scenario_id || "",
    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
    has_workspace_handoff: Boolean(archive.workspace_handoff_json_path),
    has_workspace_snapshot: Boolean(archive.workspace_snapshot_json_path),
  };
}

function buildRecentWorkbenchArchiveEntryFromRestorePayload(payload) {
  const bundle = payload && payload.bundle ? payload.bundle : {};
  const manifest = payload && payload.manifest ? payload.manifest : {};
  const files = manifest && typeof manifest.files === "object" ? manifest.files : {};
  return {
    archive_dir: payload.archive_dir || "",
    manifest_path: payload.manifest_path || "",
    created_at_utc: typeof manifest.created_at_utc === "string" ? manifest.created_at_utc : "",
    system_id: bundle.system_id || "unknown_system",
    system_title: bundle.system_title || "",
    bundle_kind: bundle.bundle_kind || "",
    ready_for_spec_build: Boolean(bundle.ready_for_spec_build),
    selected_scenario_id: bundle.selected_scenario_id || "",
    selected_fault_mode_id: bundle.selected_fault_mode_id || "",
    has_workspace_handoff: Boolean(files.workspace_handoff_json),
    has_workspace_snapshot: Boolean(files.workspace_snapshot_json),
  };
}

function upsertRecentWorkbenchArchiveEntry(entry) {
  if (!entry || (!entry.manifest_path && !entry.archive_dir)) {
    return;
  }
  const dedupeKey = entry.manifest_path || entry.archive_dir;
  workbenchRecentArchives = [
    entry,
    ...workbenchRecentArchives.filter((item) => (item.manifest_path || item.archive_dir) !== dedupeKey),
  ].slice(0, 6);
  renderRecentWorkbenchArchives();
}

function renderRecentWorkbenchArchives() {
  const container = workbenchElement("workbench-recent-archives-list");
  const summaryElement = workbenchElement("workbench-recent-archives-summary");
  if (!workbenchRecentArchives.length) {
    summaryElement.textContent = "这里会列出最近成功生成的 archive；你可以直接点“恢复这个 Archive”，不用再自己查本地路径。";
    container.replaceChildren((() => {
      const card = document.createElement("article");
      card.className = "workbench-history-card is-empty";
      const title = document.createElement("strong");
      title.textContent = "暂无最近 Archive";
      const detail = document.createElement("p");
      detail.textContent = "等你先生成一份 archive，或把已有 archive 放到默认目录后，这里就会出现可恢复列表。";
      card.append(title, detail);
      return card;
    })());
    return;
  }

  summaryElement.textContent = "这些 archive 都来自默认 archive root；点卡片就会自动把它恢复回当前 workbench。";
  container.replaceChildren(...workbenchRecentArchives.map((entry) => {
    const card = document.createElement("article");
    card.className = "workbench-history-card";

    const meta = document.createElement("div");
    meta.className = "workbench-history-meta";

    const systemChip = document.createElement("span");
    systemChip.className = "workbench-history-chip";
    systemChip.textContent = entry.system_id || "unknown_system";

    const stateChip = document.createElement("span");
    stateChip.className = "workbench-history-chip";
    stateChip.dataset.state = entry.ready_for_spec_build ? "ready" : "blocked";
    stateChip.textContent = entry.ready_for_spec_build ? "ready" : "blocked";

    const workspaceChip = document.createElement("span");
    workspaceChip.className = "workbench-history-chip";
    workspaceChip.textContent = entry.has_workspace_snapshot
      ? "workspace"
      : (entry.has_workspace_handoff ? "handoff" : "bundle");

    meta.append(systemChip, stateChip, workspaceChip);

    const title = document.createElement("strong");
    title.textContent = entry.system_title
      ? `${entry.system_id} - ${entry.system_title}`
      : entry.system_id;

    const summary = summarizeRecentWorkbenchArchive(entry);
    const summaryText = document.createElement("p");
    summaryText.textContent = `${summary.badge} / ${summary.summary}`;

    const detail = document.createElement("p");
    detail.textContent = `${summary.detail} / ${entry.created_at_utc || "时间未知"}`;

    const action = document.createElement("button");
    action.type = "button";
    action.className = "workbench-history-return-button workbench-recent-archive-action";
    action.textContent = "恢复这个 Archive";
    action.addEventListener("click", () => {
      workbenchElement("workbench-archive-manifest-path").value = entry.archive_dir || entry.manifest_path;
      void restoreWorkbenchArchiveFromManifest();
    });

    card.append(meta, title, summaryText, detail, action);
    return card;
  }));
}

async function refreshRecentWorkbenchArchives() {
  setRequestStatus("正在刷新最近 archive 列表...", "neutral");
  try {
    const response = await fetch(workbenchRecentArchivesPath, {method: "GET"});
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "recent archives request failed");
    }
    workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
    renderRecentWorkbenchArchives();
    if (payload.default_archive_root) {
      workbenchElement("default-archive-root").textContent = payload.default_archive_root;
    }
    setRequestStatus("最近 archive 列表已刷新。", "success");
  } catch (error) {
    setRequestStatus(`刷新最近 archive 列表失败：${String(error.message || error)}`, "error");
  }
}

// ─── P43 authority helpers ────────────────────────────────────────────────────

function deepFreeze(obj) {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }
  Object.getOwnPropertyNames(obj).forEach((name) => {
    deepFreeze(obj[name]);
  });
  return Object.freeze(obj);
}

function assignFrozenSpec(spec, origin) {  // origin: "freeze-event" | "archive-restore"
  frozenSpec = deepFreeze(JSON.parse(JSON.stringify(spec)));
}

async function handleStartGen() {
  if (frozenSpec === null) {
    setRequestStatus("未找到已冻结规格 — 请先审批 Spec 再生成。", "error");
    return;
  }
  // Write frozenSpec into the packet editor so runWorkbenchBundle() submits
  // the frozen content, never a post-approval draft edit (R4 authority boundary)
  const packetEl = workbenchElement("workbench-packet-json");
  if (packetEl) {
    packetEl.value = prettyJson(frozenSpec);
    renderWorkbenchPacketDraftState();
  }
  if (!dispatchWorkflowEvent("start_gen")) {
    setRequestStatus("当前工作流状态不允许启动生成。", "error");
    return;
  }
  setCurrentWorkbenchRunLabel("Frozen Spec 生成");
  const genOk = await runWorkbenchBundle();
  dispatchWorkflowEvent(genOk ? "gen_complete" : "gen_fail");
}

function validateDraftAgainstFrozen(draft, frozen) {
  if (frozen === null) {
    return { valid: true, deviations: [] };
  }
  if (draft === null || typeof draft !== "object" || typeof frozen !== "object") {
    return { valid: false, deviations: [{ field: "(root)", reason: "draft or frozen is not an object" }] };
  }
  const deviations = [];
  for (const key of Object.keys(frozen)) {
    if (JSON.stringify(frozen[key]) !== JSON.stringify(draft[key])) {
      deviations.push({ field: key, frozen: frozen[key], draft: draft[key] });
    }
  }
  return { valid: deviations.length === 0, deviations };
}

function handleFinalApprove() {
  const packetEl = workbenchElement("workbench-packet-json");
  const raw = packetEl ? packetEl.value : "";
  let currentSpec;
  try {
    currentSpec = JSON.parse(raw || "{}");
  } catch (error) {
    setRequestStatus(`审批失败：Packet JSON 解析错误 — ${String(error.message || error)}`, "error");
    return;
  }

  // Freeze the approved spec (R3 — only authorised write path)
  assignFrozenSpec(currentSpec, "freeze-event");

  // Delete draft immediately after freezing (R6)
  clearDraftDesignState();

  // Dispatch correct state machine event based on current state:
  // PANEL_READY/ANNOTATING → final_approve → APPROVING → approve_ok → APPROVED
  // INIT/FROZEN → confirm_freeze → FROZEN
  if (workflowState === "PANEL_READY" || workflowState === "ANNOTATING") {
    dispatchWorkflowEvent("final_approve");
    dispatchWorkflowEvent("approve_ok");
  } else {
    dispatchWorkflowEvent("confirm_freeze");
  }

  setRequestStatus("Spec 已冻结。草稿已清除。可执行生成。", "success");
}

// ─────────────────────────────────────────────────────────────────────────────

function workbenchBrowserStorage() {
  try {
    return window.localStorage;
  } catch (error) {
    return null;
  }
}

function withWorkbenchPacketWorkspacePersistenceSuspended(callback) {
  const previous = suspendWorkbenchPacketWorkspacePersistence;
  suspendWorkbenchPacketWorkspacePersistence = true;
  try {
    return callback();
  } finally {
    suspendWorkbenchPacketWorkspacePersistence = previous;
  }
}

function readWorkbenchPersistedFieldValue(id) {
  const field = workbenchElement(id);
  if (!field) {
    return null;
  }
  if (field.type === "checkbox") {
    return Boolean(field.checked);
  }
  return field.value;
}

function applyWorkbenchPersistedFieldValue(id, value) {
  const field = workbenchElement(id);
  if (!field || value === undefined || value === null) {
    return;
  }
  if (field.type === "checkbox") {
    field.checked = Boolean(value);
    return;
  }
  field.value = String(value);
}

function nextWorkbenchSequenceFromIds(entries, prefix) {
  if (!Array.isArray(entries) || !entries.length) {
    return 0;
  }
  return entries.reduce((maxValue, entry) => {
    if (!entry || typeof entry.id !== "string" || !entry.id.startsWith(prefix)) {
      return maxValue;
    }
    const sequence = Number(entry.id.slice(prefix.length));
    if (!Number.isFinite(sequence)) {
      return maxValue;
    }
    return Math.max(maxValue, sequence);
  }, 0);
}

function activeWorkbenchPacketPayload() {
  const parsed = parseWorkbenchPacketEditor();
  if (parsed.payload) {
    return parsed.payload;
  }
  const selectedEntry = selectedWorkbenchPacketRevisionEntry();
  return selectedEntry ? selectedEntry.payload : null;
}

function activeWorkbenchHistoryEntry() {
  if (!workbenchRunHistory.length) {
    return null;
  }
  if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
    return workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || latestWorkbenchHistoryEntry();
  }
  return latestWorkbenchHistoryEntry();
}

function buildWorkbenchHandoffSnapshot() {
  const packetPayload = activeWorkbenchPacketPayload();
  const packetEntry = selectedWorkbenchPacketRevisionEntry();
  const packetSummary = packetPayload ? summarizePacketPayload(packetPayload) : null;
  const resultEntry = activeWorkbenchHistoryEntry();
  const resultSnapshot = detailedWorkbenchHistoryEntry(resultEntry);
  const archive = resultEntry && resultEntry.payload ? resultEntry.payload.archive || null : null;
  const note = String(readWorkbenchPersistedFieldValue("workbench-handoff-note") || "").trim();

  let badgeState = "idle";
  let badgeText = "等待载入";
  let summary = "先载入 packet；系统才有可交接的当前状态。";

  if (currentWorkbenchViewMode === "running") {
    badgeState = "idle";
    badgeText = "正在整理";
    summary = note
      ? "当前工作区正在生成新结果；你的交接备注会和最终状态一起留在导出快照里。"
      : "当前工作区正在生成新结果；如果准备跨浏览器或交给别人，等结果出来后再补一段交接备注会更稳。";
  } else if (resultEntry && resultEntry.archived) {
    badgeState = "archived";
    badgeText = "可交接";
    summary = note
      ? "当前工作区已经带交接备注，且结果已归档；导出快照后，接手人可以直接从这份状态继续。"
      : "当前工作区已经具备可交接的 packet、结果和 archive 状态；如果要正式交接，建议再补一段备注。";
  } else if (resultEntry && resultEntry.state === "ready") {
    badgeState = "ready";
    badgeText = "可交接";
    summary = note
      ? "当前工作区已经带交接备注；虽然这次没归档也可以继续交接，但备注里最好说明下一步要不要补 archive。"
      : "当前工作区已经有 ready 结果；如果准备交给下一位，建议补一段备注说明是否还要 archive。";
  } else if (resultEntry) {
    badgeState = "blocked";
    badgeText = resultEntry.state === "failure" ? "先修正" : "待补齐";
    summary = note
      ? "当前工作区已经带交接备注；接手人打开快照后会先看到现在卡在哪、为什么卡住。"
      : "当前工作区已经明确告诉你卡在哪，但如果要跨浏览器或跨人交接，最好再补一段备注说明下一步。";
  } else if (packetPayload) {
    badgeState = "idle";
    badgeText = "待运行";
    summary = note
      ? "当前只有 packet 和交接备注，还没有结果历史；接手人需要从这个输入基线继续跑 bundle。"
      : "当前 packet 已就位，但还没有结果；如果你准备交接给下一位，建议先写备注说明为什么停在这里。";
  }

  return {
    note,
    badgeState,
    badgeText,
    summary,
    system: packetPayload ? (packetPayload.system_id || "unknown_system") : "等待载入",
    systemDetail: packetEntry
      ? `${packetEntry.title} / ${packetEntry.timeLabel}`
      : "当前输入区还没有已识别 packet 版本。",
    packet: packetSummary
      ? `${packetSummary.sourceDocuments} docs / ${packetSummary.logicNodes} logic / ${packetSummary.faultModes} faults`
      : "等待载入",
    packetDetail: packetSummary
      ? `${packetSummary.components} components / ${packetSummary.scenarios} scenarios / ${packetSummary.clarificationAnswers} answers`
      : "先载入 packet 后，这里会显示覆盖规模。",
    result: currentWorkbenchViewMode === "running"
      ? "正在生成"
      : resultSnapshot
        ? `${resultSnapshot.verdict} / ${resultSnapshot.scenario}`
        : "等待第一次结果",
    resultDetail: currentWorkbenchViewMode === "running"
      ? "系统正在生成新结果；完成后这里会自动刷新。"
      : resultSnapshot
        ? resultSnapshot.blocker
        : "还没有 bundle 结果。",
    archive: archive ? "已留档" : (currentWorkbenchViewMode === "running" ? "处理中" : "未生成"),
    archiveDetail: archive
      ? shortPath(archive.archive_dir)
      : resultSnapshot
        ? resultSnapshot.archive
        : "还没有 archive package。",
    workspace: `${workbenchPacketRevisionHistory.length} 个 packet 版本 / ${workbenchRunHistory.length} 个结果`,
    workspaceDetail:
      currentWorkbenchViewMode === "history" && resultEntry
        ? `当前在历史回看模式：${resultEntry.title} / ${resultEntry.timeLabel}`
        : currentWorkbenchViewMode === "latest" && resultEntry
          ? `当前主看板展示最新结果：${resultEntry.title} / ${resultEntry.timeLabel}`
          : currentWorkbenchViewMode === "running"
            ? "当前主看板正在生成新结果。"
            : packetEntry
              ? `当前 packet 基线：${packetEntry.title} / ${packetEntry.timeLabel}`
              : "等待第一次 packet 载入。",
  };
}

function renderWorkbenchHandoffBoard() {
  const snapshot = buildWorkbenchHandoffSnapshot();
  const badge = workbenchElement("workbench-handoff-badge");
  badge.dataset.state = snapshot.badgeState;
  badge.textContent = snapshot.badgeText;
  renderValue("workbench-handoff-summary", snapshot.summary);
  renderValue("workbench-handoff-system", snapshot.system);
  renderValue("workbench-handoff-system-detail", snapshot.systemDetail);
  renderValue("workbench-handoff-packet", snapshot.packet);
  renderValue("workbench-handoff-packet-detail", snapshot.packetDetail);
  renderValue("workbench-handoff-result", snapshot.result);
  renderValue("workbench-handoff-result-detail", snapshot.resultDetail);
  renderValue("workbench-handoff-archive", snapshot.archive);
  renderValue("workbench-handoff-archive-detail", snapshot.archiveDetail);
  renderValue("workbench-handoff-workspace", snapshot.workspace);
  renderValue("workbench-handoff-workspace-detail", snapshot.workspaceDetail);
}

function workbenchHandoffBriefText() {
  const snapshot = buildWorkbenchHandoffSnapshot();
  const lines = [
    "工作区交接摘要",
    `- 状态：${snapshot.badgeText}`,
    `- 系统：${snapshot.system}`,
    `- 系统细节：${snapshot.systemDetail}`,
    `- Packet 覆盖：${snapshot.packet}`,
    `- Packet 细节：${snapshot.packetDetail}`,
    `- 当前结果：${snapshot.result}`,
    `- 结果细节：${snapshot.resultDetail}`,
    `- Archive 状态：${snapshot.archive}`,
    `- Archive 细节：${snapshot.archiveDetail}`,
    `- 工作区规模：${snapshot.workspace}`,
    `- 工作区细节：${snapshot.workspaceDetail}`,
  ];
  if (snapshot.note) {
    lines.push(`- 交接备注：${snapshot.note}`);
  }
  return lines.join("\n");
}

async function copyWorkbenchHandoffBrief() {
  const text = workbenchHandoffBriefText();
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "true");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.append(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    setRequestStatus("当前工作区交接摘要已复制。", "success");
  } catch (error) {
    setRequestStatus(`复制交接摘要失败：${String(error.message || error)}`, "error");
  }
}

function collectWorkbenchPacketWorkspaceState() {
  return {
    kind: "well-harness-workbench-browser-workspace",
    version: 2,
    exportedAt: new Date().toISOString(),
    handoff: buildWorkbenchHandoffSnapshot(),
    packetJsonText: workbenchElement("workbench-packet-json").value,
    packetSourceStatus: workbenchElement("workbench-packet-source-status").textContent,
    currentWorkbenchRunLabel,
    selectedWorkbenchPacketRevisionId,
    packetRevisionHistory: cloneJson(workbenchPacketRevisionHistory),
    currentWorkbenchViewMode,
    selectedWorkbenchHistoryId,
    runHistory: cloneJson(workbenchRunHistory),
    fields: Object.fromEntries(workbenchPersistedFieldIds.map((id) => [id, readWorkbenchPersistedFieldValue(id)])),
  };
}

function persistWorkbenchPacketWorkspace() {
  renderWorkbenchHandoffBoard();
  if (suspendWorkbenchPacketWorkspacePersistence) {
    return;
  }
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return;
  }
  try {
    storage.setItem(
      workbenchPacketWorkspaceStorageKey,
      JSON.stringify(collectWorkbenchPacketWorkspaceState()),
    );
  } catch (error) {
    // Ignore persistence failures so the workbench stays usable in storage-limited environments.
  }
}

function clearPersistedWorkbenchPacketWorkspace() {
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return;
  }
  try {
    storage.removeItem(workbenchPacketWorkspaceStorageKey);
  } catch (error) {
    // Ignore storage cleanup failures.
  }
}

function loadPersistedWorkbenchPacketWorkspace() {
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return null;
  }
  const raw = storage.getItem(workbenchPacketWorkspaceStorageKey);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    clearPersistedWorkbenchPacketWorkspace();
    return null;
  }
}

// ─── P43 draft_design_state persistence (UI-owned, never read by backend) ─────

function saveDraftDesignState(draftObj) {
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return;
  }
  try {
    storage.setItem(draftDesignStateKey, JSON.stringify(draftObj));
  } catch (error) {
    // Ignore persistence failures so the workbench stays usable.
  }
}

function loadDraftDesignState() {
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return null;
  }
  const raw = storage.getItem(draftDesignStateKey);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    clearDraftDesignState();
    return null;
  }
}

function clearDraftDesignState() {
  const storage = workbenchBrowserStorage();
  if (!storage) {
    return;
  }
  try {
    storage.removeItem(draftDesignStateKey);
  } catch (error) {
    // Ignore cleanup failures.
  }
}

// ─────────────────────────────────────────────────────────────────────────────

function workspaceSnapshotDownloadName() {
  const now = new Date();
  const timestamp = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
    "-",
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join("");
  return `well-harness-workbench-workspace-${timestamp}.json`;
}

function packetRevisionSignature(payload) {
  return JSON.stringify(payload);
}

function nextWorkbenchHistoryId() {
  workbenchHistorySequence += 1;
  return `workbench-history-${workbenchHistorySequence}`;
}

function nextWorkbenchPacketRevisionId() {
  workbenchPacketRevisionSequence += 1;
  return `workbench-packet-revision-${workbenchPacketRevisionSequence}`;
}

function setActiveWorkbenchPreset(presetId) {
  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
    const selected = button.dataset.workbenchPreset === presetId;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  });
}

function setCurrentWorkbenchRunLabel(label) {
  currentWorkbenchRunLabel = label || "手动生成";
  persistWorkbenchPacketWorkspace();
}

function setPacketEditor(payload) {
  workbenchElement("workbench-packet-json").value = prettyJson(payload);
  persistWorkbenchPacketWorkspace();
}

function parseWorkbenchPacketEditor() {
  const raw = workbenchElement("workbench-packet-json").value;
  if (!raw.trim()) {
    return {error: "当前 Packet JSON 为空。"};
  }
  try {
    return {payload: JSON.parse(raw)};
  } catch (error) {
    return {error: String(error.message || error)};
  }
}

function renderValue(elementId, value, fallbackText = "-") {
  if (typeof value === "string") {
    const text = value.trim();
    workbenchElement(elementId).textContent = text || fallbackText;
    return;
  }
  if (value === null || value === undefined) {
    workbenchElement(elementId).textContent = fallbackText;
    return;
  }
  workbenchElement(elementId).textContent = String(value);
}

function summarizePacketPayload(payload) {
  return {
    sourceDocuments: Array.isArray(payload.source_documents) ? payload.source_documents.length : 0,
    components: Array.isArray(payload.components) ? payload.components.length : 0,
    logicNodes: Array.isArray(payload.logic_nodes) ? payload.logic_nodes.length : 0,
    scenarios: Array.isArray(payload.acceptance_scenarios) ? payload.acceptance_scenarios.length : 0,
    faultModes: Array.isArray(payload.fault_modes) ? payload.fault_modes.length : 0,
    clarificationAnswers: Array.isArray(payload.clarification_answers) ? payload.clarification_answers.length : 0,
  };
}

function packetRevisionDetailText(payload) {
  const summary = summarizePacketPayload(payload);
  return `docs=${summary.sourceDocuments} / components=${summary.components} / logic=${summary.logicNodes} / scenarios=${summary.scenarios} / faults=${summary.faultModes} / answers=${summary.clarificationAnswers}`;
}

function latestWorkbenchPacketRevisionEntry() {
  return workbenchPacketRevisionHistory.length ? workbenchPacketRevisionHistory[0] : null;
}

function selectedWorkbenchPacketRevisionEntry() {
  return workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || latestWorkbenchPacketRevisionEntry();
}

function normalizeWorkbenchPacketRevisionHistory(entries) {
  if (!Array.isArray(entries)) {
    return [];
  }
  return entries
    .filter((entry) => entry && typeof entry.id === "string" && entry.id && entry.payload)
    .map((entry) => ({
      id: entry.id,
      timeLabel: entry.timeLabel || historyTimeLabel(),
      title: entry.title || "Packet 更新",
      payload: cloneJson(entry.payload),
      summary: entry.summary || `${entry.payload.system_id || "unknown_system"} 已更新`,
      detail: entry.detail || packetRevisionDetailText(entry.payload),
      signature: packetRevisionSignature(entry.payload),
    }))
    .slice(0, maxWorkbenchPacketRevisionHistory);
}

function normalizeWorkbenchRunHistory(entries) {
  if (!Array.isArray(entries)) {
    return [];
  }
  return entries
    .filter((entry) => entry && typeof entry.id === "string" && entry.id)
    .map((entry) => ({
      id: entry.id,
      state: entry.state || "failure",
      stateLabel: entry.stateLabel || (entry.state === "ready" ? "通过" : entry.state === "blocked" ? "阻塞" : "失败"),
      archived: Boolean(entry.archived),
      timeLabel: entry.timeLabel || historyTimeLabel(),
      title: entry.title || "手动生成",
      payload: entry.payload ? cloneJson(entry.payload) : null,
      errorMessage: entry.errorMessage ? String(entry.errorMessage) : undefined,
      summary: entry.summary || "请求未完成",
      detail: entry.detail || "等待详情。",
    }))
    .slice(0, maxWorkbenchRunHistory);
}

function buildWorkbenchPacketRevisionEntry(payload, {
  title,
  summary,
  detail,
} = {}) {
  return {
    id: nextWorkbenchPacketRevisionId(),
    timeLabel: historyTimeLabel(),
    title: title || "Packet 更新",
    payload: cloneJson(payload),
    summary: summary || `${payload.system_id || "unknown_system"} 已更新`,
    detail: detail || packetRevisionDetailText(payload),
    signature: packetRevisionSignature(payload),
  };
}

function splitLines(text) {
  return text
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function setVisualBadge(state, text) {
  const element = workbenchElement("workbench-visual-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function setStageState(stageName, state, note) {
  workbenchElement(`workbench-stage-${stageName}`).dataset.state = state;
  workbenchElement(`workbench-stage-${stageName}-note`).textContent = note;
}

function setOnboardingBadge(state, text) {
  const element = workbenchElement("workbench-onboarding-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function setFingerprintBadge(state, text) {
  const element = workbenchElement("workbench-fingerprint-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function setActionsBadge(state, text) {
  const element = workbenchElement("workbench-actions-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function setSchemaRepairBadge(state, text) {
  const element = workbenchElement("workbench-schema-workspace-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function setClarificationWorkspaceBadge(state, text) {
  const element = workbenchElement("workbench-clarification-workspace-badge");
  element.dataset.state = state;
  element.textContent = text;
}

function uniqueValues(values) {
  return [...new Set(
    values
      .map((value) => (typeof value === "string" ? value.trim() : ""))
      .filter(Boolean),
  )];
}

function joinWithFallback(values, fallbackText = "-") {
  return values.length ? values.join(" / ") : fallbackText;
}

function documentKindLabel(kind) {
  const labels = {
    markdown: "Markdown",
    notion: "Notion",
    pdf: "PDF",
    spreadsheet: "表格",
  };
  return labels[kind] || kind || "未知来源";
}

function documentRoleLabel(role) {
  const labels = {
    acceptance_evidence: "验收证据",
    logic_spec: "逻辑规格",
    troubleshooting_note: "排故说明",
    timeline_note: "时间线说明",
  };
  return labels[role] || role || "未标注角色";
}

function signalKindLabel(kind) {
  const labels = {
    command: "命令",
    commanded_state: "命令状态",
    derived: "派生量",
    sensor: "传感器",
    switch: "开关",
  };
  return labels[kind] || kind || "未知类型";
}

function stateShapeLabel(stateShape) {
  const labels = {
    analog: "连续量",
    binary: "二值",
    discrete: "离散态",
  };
  return labels[stateShape] || stateShape || "未知形态";
}

function createFingerprintChip(text, tone = "neutral") {
  const chip = document.createElement("span");
  chip.className = "workbench-fingerprint-chip";
  chip.dataset.tone = tone;
  chip.textContent = text;
  return chip;
}

function createFingerprintEmptyCard(message) {
  const card = document.createElement("article");
  card.className = "workbench-fingerprint-item is-empty";

  const detail = document.createElement("p");
  detail.className = "workbench-fingerprint-empty";
  detail.textContent = message;

  card.append(detail);
  return card;
}

function createActionItemCard({
  title,
  detail,
  chipText,
  chipTone = "neutral",
}) {
  const card = document.createElement("article");
  card.className = "workbench-actions-item";

  const header = document.createElement("div");
  header.className = "workbench-actions-item-header";

  const strong = document.createElement("strong");
  strong.className = "workbench-actions-item-title";
  strong.textContent = title;

  const chip = createFingerprintChip(chipText, chipTone);

  header.append(strong, chip);

  const body = document.createElement("p");
  body.className = "workbench-actions-item-detail";
  body.textContent = detail;

  card.append(header, body);
  return card;
}

function createClarificationWorkspaceCard({
  id,
  prompt,
  rationale,
  requiredFor,
  answer = "",
  status = "needs_answer",
  editable = true,
}) {
  const card = document.createElement("article");
  card.className = "workbench-clarification-card";

  const header = document.createElement("div");
  header.className = "workbench-clarification-card-header";

  const titleGroup = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = id || "clarification";
  const promptText = document.createElement("p");
  promptText.textContent = prompt || "等待补齐说明。";
  titleGroup.append(title, promptText);

  const chip = createFingerprintChip(status === "answered" ? "已回答" : "待回答", status === "answered" ? "ready" : "blocked");
  header.append(titleGroup, chip);

  const meta = document.createElement("div");
  meta.className = "workbench-clarification-card-meta";

  const rationaleText = document.createElement("span");
  rationaleText.textContent = `为什么要补：${rationale || "等待说明。"}`;
  const requiredForText = document.createElement("span");
  requiredForText.textContent = `补齐后用于：${requiredFor || "spec_build"}`;
  meta.append(rationaleText, requiredForText);

  const textarea = document.createElement("textarea");
  textarea.className = "workbench-clarification-answer";
  textarea.dataset.questionId = id || "";
  textarea.placeholder = "在这里填写工程答案，写回 packet 后可直接重跑。";
  textarea.value = answer || "";
  textarea.disabled = !editable;

  card.append(header, meta, textarea);
  return card;
}

function createSchemaRepairCard({
  title,
  detail,
  targetPath,
  expectedEffect,
  autofixAvailable = false,
}) {
  const card = document.createElement("article");
  card.className = "workbench-schema-card";

  const header = document.createElement("div");
  header.className = "workbench-schema-card-header";

  const titleGroup = document.createElement("div");
  const strong = document.createElement("strong");
  strong.textContent = title;
  const body = document.createElement("p");
  body.textContent = detail;
  titleGroup.append(strong, body);

  const chip = createFingerprintChip(autofixAvailable ? "可自动补齐" : "需手工修复", autofixAvailable ? "ready" : "blocked");
  header.append(titleGroup, chip);

  const meta = document.createElement("div");
  meta.className = "workbench-schema-card-meta";

  const pathText = document.createElement("span");
  pathText.textContent = `目标位置：${targetPath || "packet JSON"}`;
  const effectText = document.createElement("span");
  effectText.textContent = `修复结果：${expectedEffect || "修复后再重跑验证。"}`;
  meta.append(pathText, effectText);

  card.append(header, meta);
  return card;
}

function renderFingerprintDocumentList(documents, fallbackText) {
  const container = workbenchElement("workbench-fingerprint-doc-list");
  if (!documents.length) {
    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
    return;
  }

  container.replaceChildren(...documents.map((document) => {
    const card = document.createElement("article");
    card.className = "workbench-fingerprint-item";

    const header = document.createElement("div");
    header.className = "workbench-fingerprint-item-header";

    const title = document.createElement("strong");
    title.className = "workbench-fingerprint-item-title";
    title.textContent = document.title || document.id || "未命名文档";

    const chips = document.createElement("div");
    chips.className = "workbench-fingerprint-chip-row";
    chips.append(
      createFingerprintChip(documentKindLabel(document.kind), "source"),
      createFingerprintChip(documentRoleLabel(document.role), "role"),
    );

    header.append(title, chips);

    const location = document.createElement("p");
    location.className = "workbench-fingerprint-item-detail";
    location.textContent = document.location || "未提供路径";

    card.append(header, location);
    return card;
  }));
}

function renderFingerprintSignalList(signals, fallbackText) {
  const container = workbenchElement("workbench-fingerprint-signal-list");
  if (!signals.length) {
    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
    return;
  }

  container.replaceChildren(...signals.map((signal) => {
    const card = document.createElement("article");
    card.className = "workbench-fingerprint-item";

    const header = document.createElement("div");
    header.className = "workbench-fingerprint-item-header";

    const title = document.createElement("strong");
    title.className = "workbench-fingerprint-item-title";
    title.textContent = signal.label || signal.id || "未命名信号";

    const chips = document.createElement("div");
    chips.className = "workbench-fingerprint-chip-row";
    chips.append(
      createFingerprintChip(signalKindLabel(signal.kind), "signal"),
      createFingerprintChip(stateShapeLabel(signal.state_shape), "shape"),
      createFingerprintChip(signal.unit || "无单位", "unit"),
    );

    header.append(title, chips);

    const detail = document.createElement("p");
    detail.className = "workbench-fingerprint-item-detail";
    detail.textContent = signal.id ? `signal_id = ${signal.id}` : "未提供 signal_id";

    card.append(header, detail);
    return card;
  }));
}

function renderSystemFingerprint({
  badgeState = "idle",
  badgeText = "等待生成",
  summary = "这里会直接告诉你第二套系统到底长什么样，而不只是告诉你它能不能接。",
  systemId = "-",
  objective = "-",
  sourceMode = "-",
  sourceTruth = "-",
  documents = [],
  signals = [],
  documentFallback = "还没有来源文档。",
  signalFallback = "还没有关键信号定义。",
} = {}) {
  setFingerprintBadge(badgeState, badgeText);
  renderValue("workbench-fingerprint-summary", summary);
  renderValue("workbench-fingerprint-system-id", systemId);
  renderValue("workbench-fingerprint-objective", objective);
  renderValue("workbench-fingerprint-source-mode", sourceMode);
  renderValue("workbench-fingerprint-source-truth", sourceTruth);
  renderValue("workbench-fingerprint-doc-count", `${documents.length} 份文档`);
  renderValue("workbench-fingerprint-signal-count", `${signals.length} 个信号`);
  renderFingerprintDocumentList(documents, documentFallback);
  renderFingerprintSignalList(signals, signalFallback);
}

function renderActionList(containerId, items, fallbackText) {
  const container = workbenchElement(containerId);
  if (!items.length) {
    container.replaceChildren(createFingerprintEmptyCard(fallbackText));
    return;
  }
  container.replaceChildren(...items);
}

function renderOnboardingActions({
  badgeState = "idle",
  badgeText = "等待生成",
  summary = "这里会把接入动作拆成三列：先补澄清、再补结构、最后看解锁项。",
  followUps = [],
  blockers = [],
  unlocks = [],
  followUpFallback = "运行后这里会列出需要先回答的澄清项。",
  blockerFallback = "运行后这里会列出需要补的结构问题。",
  unlockFallback = "运行后这里会列出补齐后可解锁的能力。",
} = {}) {
  setActionsBadge(badgeState, badgeText);
  renderValue("workbench-actions-summary", summary);
  renderValue("workbench-actions-follow-up-count", `${followUps.length} 项`);
  renderValue("workbench-actions-schema-count", `${blockers.length} 项`);
  renderValue("workbench-actions-unlock-count", `${unlocks.length} 项`);
  renderActionList("workbench-actions-follow-up-list", followUps, followUpFallback);
  renderActionList("workbench-actions-schema-list", blockers, blockerFallback);
  renderActionList("workbench-actions-unlock-list", unlocks, unlockFallback);
}

function setSchemaRepairActionState(disabled) {
  workbenchElement("workbench-apply-schema-repairs").disabled = disabled;
}

function renderSchemaRepairWorkspace({
  badgeState = "idle",
  badgeText = "等待生成",
  summary = "这里会把 schema blocker 里的安全 autofix 项单独挑出来。",
  cards = [],
  fallbackTitle = "等待生成",
  fallbackText = "blocked bundle 出来后，这里会显示 repair suggestions。",
  note = "只有后端标记为 safe autofix 的修复才会开放一键应用。",
  actionsDisabled = true,
} = {}) {
  setSchemaRepairBadge(badgeState, badgeText);
  renderValue("workbench-schema-workspace-summary", summary);
  renderValue("workbench-schema-workspace-note", note);
  const container = workbenchElement("workbench-schema-workspace-list");
  if (!cards.length) {
    const emptyCard = document.createElement("article");
    emptyCard.className = "workbench-schema-card is-empty";
    const title = document.createElement("strong");
    title.textContent = fallbackTitle;
    const detail = document.createElement("p");
    detail.textContent = fallbackText;
    emptyCard.append(title, detail);
    container.replaceChildren(emptyCard);
  } else {
    container.replaceChildren(...cards);
  }
  setSchemaRepairActionState(actionsDisabled);
}

function renderSchemaRepairWorkspaceFromPayload(payload) {
  const bundle = payload.bundle || {};
  const assessment = bundle.intake_assessment || {};
  const ready = Boolean(bundle.ready_for_spec_build);
  const repairSuggestions = Array.isArray(assessment.repair_suggestions) ? assessment.repair_suggestions : [];
  const safeSuggestions = repairSuggestions.filter((item) => item.autofix_available);
  const cards = repairSuggestions.map((item) => createSchemaRepairCard({
    title: item.title || item.id || "schema repair",
    detail: item.detail || item.blocking_reason || "等待修复说明。",
    targetPath: item.target_path || "packet JSON",
    expectedEffect: item.expected_effect,
    autofixAvailable: Boolean(item.autofix_available),
  }));

  if (ready) {
    renderSchemaRepairWorkspace({
      badgeState: "ready",
      badgeText: "当前无需修复",
      summary: "这次 bundle 已经没有 schema blocker 需要修复；工作台保留为空，避免把当前 ready 状态误读成还有结构问题。",
      fallbackTitle: "当前无需 schema 修复",
      fallbackText: "schema blocker 已经清空，可以继续用当前 packet 跑 playback / diagnosis / knowledge。",
      note: "当前没有安全 schema 修复要应用。",
      actionsDisabled: true,
    });
    return;
  }

  renderSchemaRepairWorkspace({
    badgeState: safeSuggestions.length ? "blocked" : "idle",
    badgeText: safeSuggestions.length ? "可安全修一点" : "暂时无安全修复",
    summary: safeSuggestions.length
      ? "这次 blocked bundle 里有后端确认安全的 schema autofix。你可以一键应用这些修复，然后马上重跑。"
      : "这次 blocked bundle 虽然还有 schema blocker，但当前没有被后端判定为 safe autofix 的修复项。",
    cards,
    fallbackTitle: "当前没有 repair suggestion",
    fallbackText: "当前没有额外 schema repair suggestion；如果仍阻塞，请直接检查 packet JSON。",
    note: safeSuggestions.length
      ? `当前共有 ${safeSuggestions.length} 条 safe autofix；工作台不会猜修复逻辑，只调用后端声明为安全的 patch。`
      : "剩余 schema blocker 需要手工修改 packet JSON 或工程语义后再重跑。",
    actionsDisabled: !safeSuggestions.length,
  });
}

function setClarificationWorkspaceActionState(disabled) {
  workbenchElement("workbench-apply-clarifications").disabled = disabled;
  workbenchElement("workbench-apply-and-rerun").disabled = disabled;
}

function renderClarificationWorkspace({
  badgeState = "idle",
  badgeText = "等待生成",
  summary = "这里会把需要补的 clarification 直接变成可填写表单，方便你写回当前 packet。",
  cards = [],
  fallbackTitle = "等待生成",
  fallbackText = "当 bundle 停在 clarification gate 时，这里会出现可直接填写的答案卡。",
  note = "先运行一次 blocked bundle，这里才会知道哪些问题还没回答。",
  actionsDisabled = true,
} = {}) {
  setClarificationWorkspaceBadge(badgeState, badgeText);
  renderValue("workbench-clarification-workspace-summary", summary);
  renderValue("workbench-clarification-workspace-note", note);
  const container = workbenchElement("workbench-clarification-workspace-list");
  if (!cards.length) {
    const emptyCard = document.createElement("article");
    emptyCard.className = "workbench-clarification-card is-empty";
    const title = document.createElement("strong");
    title.textContent = fallbackTitle;
    const detail = document.createElement("p");
    detail.textContent = fallbackText;
    emptyCard.append(title, detail);
    container.replaceChildren(emptyCard);
  } else {
    container.replaceChildren(...cards);
  }
  setClarificationWorkspaceActionState(actionsDisabled);
}

function renderClarificationWorkspaceFromPayload(payload) {
  const bundle = payload.bundle || {};
  const clarification = bundle.clarification_brief || {};
  const ready = Boolean(bundle.ready_for_spec_build);
  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  const unresolvedItems = followUpItems.filter((item) => item.status !== "answered");
  const cards = unresolvedItems.map((item) => createClarificationWorkspaceCard({
    id: item.id,
    prompt: item.prompt,
    rationale: item.rationale,
    requiredFor: item.required_for,
    answer: item.answer,
    status: item.status,
    editable: true,
  }));

  if (ready) {
    renderClarificationWorkspace({
      badgeState: "ready",
      badgeText: "澄清已放行",
      summary: "这次 bundle 已经把 clarification gate 走通了；当前无需补答，如果要改问题答案，可以直接编辑 packet JSON 后重跑。",
      fallbackTitle: "当前无需回填",
      fallbackText: "clarification 问题已经补齐，当前链路可以继续往 playback / diagnosis / knowledge 走。",
      note: "当前 packet 已 ready；工作台按钮已关闭，避免把已通过状态误当成待补状态。",
      actionsDisabled: true,
    });
    return;
  }

  renderClarificationWorkspace({
    badgeState: cards.length ? "blocked" : "idle",
    badgeText: cards.length ? "可直接回填" : "等待回填项",
    summary: cards.length
      ? "当前 bundle 停在 clarification gate；你可以直接在这里填写工程答案，写回 packet 后立即重跑。"
      : "这次虽然没 ready，但当前没有额外待回答的问题卡；如果仍阻塞，请优先看上方 schema blocker。",
    cards,
    fallbackTitle: "当前没有待答问题",
    fallbackText: "clarification 问题已经回答完毕，剩下的阻塞主要来自 schema / 结构问题。",
    note: cards.length
      ? `已加载 ${cards.length} 条待回答 clarification；“写回当前 Packet”不会新增前端规则，只会更新 packet JSON。`
      : "当前无待回答 clarification；请先修复 schema blocker 后再重跑。",
    actionsDisabled: !cards.length,
  });
}

function currentClarificationWorkspaceAnswers() {
  return [...document.querySelectorAll(".workbench-clarification-answer")]
    .map((field) => ({
      questionId: field.dataset.questionId || "",
      answer: field.value.trim(),
    }))
    .filter((item) => item.questionId);
}

function applyClarificationWorkspaceAnswersToPacket(packetPayload) {
  const nextPayload = cloneJson(packetPayload);
  const existingAnswers = Array.isArray(nextPayload.clarification_answers) ? nextPayload.clarification_answers : [];
  const answerMap = new Map(existingAnswers
    .filter((item) => item && typeof item.question_id === "string" && item.question_id.trim())
    .map((item) => [item.question_id.trim(), {
      question_id: item.question_id.trim(),
      answer: typeof item.answer === "string" ? item.answer : "",
      status: item.status || "answered",
    }]));
  const workspaceAnswers = currentClarificationWorkspaceAnswers();
  const workspaceIds = workspaceAnswers.map((item) => item.questionId);

  workspaceAnswers.forEach((item) => {
    if (!item.answer) {
      answerMap.delete(item.questionId);
      return;
    }
    answerMap.set(item.questionId, {
      question_id: item.questionId,
      answer: item.answer,
      status: "answered",
    });
  });

  nextPayload.clarification_answers = [
    ...workspaceIds
      .map((questionId) => answerMap.get(questionId))
      .filter(Boolean),
    ...[...answerMap.entries()]
      .filter(([questionId]) => !workspaceIds.includes(questionId))
      .map(([, answer]) => answer),
  ];
  return {
    packetPayload: nextPayload,
    answeredCount: workspaceAnswers.filter((item) => item.answer).length,
  };
}

async function runWorkbenchSchemaSafeRepair() {
  let packetPayload;
  try {
    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  } catch (error) {
    setRequestStatus(`当前 Packet JSON 无法应用 schema 修复：${String(error.message || error)}`, "error");
    return;
  }

  setRequestStatus("正在应用安全 schema 修复...", "neutral");
  try {
    const response = await fetch(workbenchRepairPath, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        packet_payload: packetPayload,
        apply_all_safe: true,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || payload.error || "workbench safe repair request failed");
    }
    maybeAutoSnapshotCurrentPacketDraft("应用安全 schema 修复");
    setPacketEditor(payload.packet_payload);
    setPacketSourceStatus(`当前 packet 已应用 ${payload.applied_suggestion_ids.length} 条安全 schema 修复，并准备重跑。`);
    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.packet_payload, {
      title: "Schema 安全修复",
      summary: `已应用 ${payload.applied_suggestion_ids.length} 条 safe autofix`,
      detail: payload.applied_suggestion_ids.join(" / "),
    }));
    renderSystemFingerprintFromPacketPayload(payload.packet_payload, {
      badgeState: "idle",
      badgeText: "画像已更新",
      summary: "安全 schema 修复已经写回当前 packet；系统现在会基于修复后的 packet 继续重跑 bundle。",
    });
    setCurrentWorkbenchRunLabel("Schema 安全修复并重跑");
    setActiveWorkbenchPreset("");
    await runWorkbenchBundle();
  } catch (error) {
    setRequestStatus(`安全 schema 修复失败：${String(error.message || error)}`, "error");
  }
}

async function applyClarificationWorkspace({
  rerun = false,
} = {}) {
  let packetPayload;
  try {
    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  } catch (error) {
    setRequestStatus(`当前 Packet JSON 无法写回 clarification：${String(error.message || error)}`, "error");
    return;
  }

  const {packetPayload: nextPayload, answeredCount} = applyClarificationWorkspaceAnswersToPacket(packetPayload);
  maybeAutoSnapshotCurrentPacketDraft("写回 clarification");
  setPacketEditor(nextPayload);
  setPacketSourceStatus(
    answeredCount
      ? `当前 packet 已写回 ${answeredCount} 条 clarification answer。`
      : "当前 packet 已清空这批 clarification answer。"
  );
  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(nextPayload, {
    title: "Clarification 写回",
    summary: answeredCount
      ? `已写回 ${answeredCount} 条 clarification answer`
      : "已清空当前 clarification answer",
  }));
  renderSystemFingerprintFromPacketPayload(nextPayload, {
    badgeState: "idle",
    badgeText: "画像已更新",
    summary: "clarification 答案已经写回当前 packet；如果系统画像或文档方向没问题，可以直接重跑看 gate 是否放行。",
  });
  renderValue(
    "workbench-clarification-workspace-note",
    answeredCount
      ? `已把 ${answeredCount} 条答案写回当前 packet。${rerun ? "系统现在会直接重跑。" : "如需验证是否放行，可以点右侧按钮或主运行按钮重跑。"}`
      : "已清空当前工作台里的回答并写回 packet；如需验证，请重新运行。",
  );
  setRequestStatus(
    answeredCount
      ? (rerun ? "clarification 已写回，正在重跑 bundle..." : "clarification 已写回当前 packet。")
      : "clarification 修改已写回当前 packet。",
    rerun ? "neutral" : "success",
  );

  if (rerun) {
    setCurrentWorkbenchRunLabel("Clarification 回填并重跑");
    setActiveWorkbenchPreset("");
    await runWorkbenchBundle();
  }
}

function renderSystemFingerprintFromPacketPayload(packetPayload, {
  badgeState = "idle",
  badgeText = "画像已载入",
  summary = "样例已经装载。你现在就能先看这套系统的文档来源和关键信号，不用等 bundle 跑完。",
} = {}) {
  const documents = Array.isArray(packetPayload.source_documents) ? packetPayload.source_documents : [];
  const signals = Array.isArray(packetPayload.components) ? packetPayload.components : [];
  const documentKinds = uniqueValues(documents.map((document) => document.kind));
  const sourceModeParts = [joinWithFallback(documentKinds.map(documentKindLabel), "未识别来源")];
  if (documentKinds.length > 1) {
    sourceModeParts.push("混合来源");
  }
  if (documentKinds.includes("pdf")) {
    sourceModeParts.push("含 PDF");
  }

  renderSystemFingerprint({
    badgeState,
    badgeText,
    summary,
    systemId: packetPayload.system_id || "-",
    objective: packetPayload.objective || "-",
    sourceMode: sourceModeParts.join(" / "),
    sourceTruth: packetPayload.source_of_truth || "等待工程真值说明",
    documents,
    signals,
    documentFallback: "当前 packet 还没有来源文档。",
    signalFallback: "当前 packet 还没有关键信号定义。",
  });
}

function renderOnboardingReadiness({
  badgeState = "idle",
  badgeText = "等待生成",
  summary = "这里会直接告诉你：这份 packet 现在够不够支撑第二套控制逻辑进入 spec build。",
  docs = "-",
  docsDetail = "等待生成。",
  components = "-",
  componentsDetail = "等待生成。",
  logic = "-",
  logicDetail = "等待生成。",
  scenarios = "-",
  scenariosDetail = "等待生成。",
  faults = "-",
  faultsDetail = "等待生成。",
  clarifications = "-",
  clarificationsDetail = "等待生成。",
  unlocks = "-",
  gaps = "-",
} = {}) {
  setOnboardingBadge(badgeState, badgeText);
  renderValue("workbench-onboarding-summary", summary);
  renderValue("workbench-onboarding-docs", docs);
  renderValue("workbench-onboarding-docs-detail", docsDetail);
  renderValue("workbench-onboarding-components", components);
  renderValue("workbench-onboarding-components-detail", componentsDetail);
  renderValue("workbench-onboarding-logic", logic);
  renderValue("workbench-onboarding-logic-detail", logicDetail);
  renderValue("workbench-onboarding-scenarios", scenarios);
  renderValue("workbench-onboarding-scenarios-detail", scenariosDetail);
  renderValue("workbench-onboarding-faults", faults);
  renderValue("workbench-onboarding-faults-detail", faultsDetail);
  renderValue("workbench-onboarding-clarifications", clarifications);
  renderValue("workbench-onboarding-clarifications-detail", clarificationsDetail);
  renderValue("workbench-onboarding-unlocks", unlocks);
  renderValue("workbench-onboarding-gaps", gaps);
}

function renderPreparationBoard(message) {
  setWorkbenchViewState("preparation");
  setVisualBadge("idle", "样例已就位");
  renderOnboardingReadiness({
    badgeState: "idle",
    badgeText: "样例待运行",
    summary: "样例已经装载，但还没有真正做 intake 检查；运行后这里才会告诉你第二套系统接入是否 ready。",
    gaps: "等待 intake",
  });
  renderValue("workbench-spotlight-verdict", "等待生成");
  renderValue("workbench-spotlight-verdict-detail", message);
  renderValue("workbench-spotlight-blocker", "尚未运行");
  renderValue("workbench-spotlight-blocker-detail", "点击“生成 Bundle”后，系统会告诉你卡在哪一步。");
  renderValue("workbench-spotlight-knowledge", "尚未形成");
  renderValue("workbench-spotlight-knowledge-detail", "还没有 diagnosis / knowledge 结果。");
  renderValue("workbench-spotlight-archive", "尚未归档");
  renderValue("workbench-spotlight-archive-detail", "如果勾选 archive，运行后这里会显示落档状态。");
  renderOnboardingActions({
    badgeState: "idle",
    badgeText: "等待动作生成",
    summary: "样例已经装载，但动作板还没真正跑 intake / clarification，所以先不猜下一步。",
  });
  renderSchemaRepairWorkspace({
    badgeState: "idle",
    badgeText: "等待修复项",
    summary: "样例虽然已经装载，但还没真正跑出 schema blocker，所以这里先不提前猜哪些结构问题能安全 autofix。",
    fallbackTitle: "等待第一次运行",
    fallbackText: "先跑一次 bundle；如果后端给出 repair suggestion，这里才会显示安全 schema 修复入口。",
    note: "当前只是样例准备阶段，还没有可应用的 schema repair。",
    actionsDisabled: true,
  });
  renderClarificationWorkspace({
    badgeState: "idle",
    badgeText: "等待回填项",
    summary: "样例虽然已经装载，但还没真正跑到 clarification gate，所以这里先不提前猜哪些问题要你回答。",
    fallbackTitle: "等待第一次运行",
    fallbackText: "先跑一次 bundle；如果它停在 clarification gate，这里就会出现可直接填写的答案卡。",
    note: "当前只是样例准备阶段，还没有需要写回的 clarification。",
    actionsDisabled: true,
  });
  renderValue(
    "workbench-visual-summary",
    "当前只是在准备样例。真正的验收结果会在你点击“生成 Bundle”之后出现在这里。",
  );
  setStageState("intake", "pending", "样例已装载，等待运行。");
  setStageState("clarification", "idle", "等待生成。");
  setStageState("playback", "idle", "等待生成。");
  setStageState("diagnosis", "idle", "等待生成。");
  setStageState("knowledge", "idle", "等待生成。");
  setStageState("archive", "idle", "等待生成。");
  renderWorkbenchHistoryViewBar();
  renderWorkbenchPacketHistoryViewBar();
}

function pushWorkbenchRunHistory(entry) {
  setWorkbenchViewState("latest", entry.id);
  workbenchRunHistory = [entry, ...workbenchRunHistory].slice(0, maxWorkbenchRunHistory);
  renderWorkbenchRunHistory();
  persistWorkbenchPacketWorkspace();
}

function renderWorkbenchPacketHistoryViewBar() {
  const latestEntry = latestWorkbenchPacketRevisionEntry();
  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;
  const statusElement = workbenchElement("workbench-packet-history-status");
  const returnButton = workbenchElement("workbench-packet-history-return-latest");

  if (!latestEntry) {
    statusElement.textContent = "当前 Packet：等待第一次载入";
    returnButton.disabled = true;
    renderWorkbenchPacketDraftState();
    renderWorkbenchPacketRevisionCompareBar();
    return;
  }

  if (!selectedEntry || selectedEntry.id === latestEntry.id) {
    statusElement.textContent = `当前 Packet：最新版本 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
    returnButton.disabled = true;
    renderWorkbenchPacketDraftState();
    renderWorkbenchPacketRevisionCompareBar();
    return;
  }

  statusElement.textContent = `当前 Packet：历史版本 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  returnButton.disabled = false;
  renderWorkbenchPacketDraftState();
  renderWorkbenchPacketRevisionCompareBar();
}

function setPacketDraftActionState(disabled) {
  workbenchElement("workbench-save-packet-draft").disabled = disabled;
}

function renderWorkbenchPacketDraftState() {
  const statusElement = workbenchElement("workbench-packet-draft-status");
  const noteElement = workbenchElement("workbench-packet-draft-note");
  const baselineEntry = selectedWorkbenchPacketRevisionEntry();

  if (!baselineEntry) {
    const parsed = parseWorkbenchPacketEditor();
    if (parsed.error) {
      statusElement.textContent = "当前草稿：JSON 待修正";
      noteElement.textContent = `当前输入区已经恢复了草稿文本，但它还不是合法 JSON：${parsed.error}`;
      setPacketDraftActionState(true);
      return;
    }
    if (parsed.payload) {
      statusElement.textContent = "当前草稿：尚未建立版本基线";
      noteElement.textContent = "当前输入区已经有 packet，但还没进入已保存版本历史；你可以先把它保存成草稿，再继续切换样例或重跑。";
      setPacketDraftActionState(false);
      return;
    }
    statusElement.textContent = "当前草稿：等待第一次载入";
    noteElement.textContent = "先载入一个 packet；之后直接改 JSON 但还没运行时，也可以先把当前版本存成草稿。";
    setPacketDraftActionState(true);
    return;
  }

  const parsed = parseWorkbenchPacketEditor();
  if (parsed.error) {
    statusElement.textContent = "当前草稿：JSON 暂不可保存";
    noteElement.textContent = `当前输入区还不是合法 JSON，所以版本历史暂时无法收纳它：${parsed.error}`;
    setPacketDraftActionState(true);
    return;
  }

  if (baselineEntry.signature === packetRevisionSignature(parsed.payload)) {
    statusElement.textContent = `当前草稿：已与「${baselineEntry.title}」同步`;
    noteElement.textContent = "如果接下来切换样例、恢复旧版本或应用浏览器写回，系统会先检查是否存在新的有效草稿。";
    setPacketDraftActionState(true);
    return;
  }

  statusElement.textContent = `当前草稿：有未保存改动（相对「${baselineEntry.title}」）`;
  noteElement.textContent = "你可以先手动保存这份 Packet 草稿；如果现在切换样例、恢复旧版本或应用浏览器写回，系统也会先自动保存这份有效草稿，刷新页面后也会继续恢复当前工作区。";
  setPacketDraftActionState(false);
}

function restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
  sourceStatusMessage = "已从浏览器恢复上次 packet 工作区。",
  sourceStatusMessageWithHistory = "已从浏览器恢复上次 packet 工作区和结果历史。",
  packetSourceFallback = "当前样例：已恢复工作区快照。",
  preparationMessage = "已恢复工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
  fingerprintSummary = "已恢复工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
  successMessage = "已恢复工作区快照。",
} = {}) {
  if (!workspace || typeof workspace !== "object") {
    return false;
  }

  const normalizedHistory = normalizeWorkbenchPacketRevisionHistory(workspace.packetRevisionHistory);
  const normalizedRunHistory = normalizeWorkbenchRunHistory(workspace.runHistory);
  const fallbackPacketJsonText = normalizedHistory.length
    ? prettyJson(normalizedHistory[0].payload)
    : prettyJson(bootstrapPayload.reference_packet);
  const packetJsonText = typeof workspace.packetJsonText === "string" && workspace.packetJsonText.trim()
    ? workspace.packetJsonText
    : fallbackPacketJsonText;

  withWorkbenchPacketWorkspacePersistenceSuspended(() => {
    workbenchPacketRevisionHistory = normalizedHistory;
    workbenchPacketRevisionSequence = nextWorkbenchSequenceFromIds(
      normalizedHistory,
      "workbench-packet-revision-",
    );
    workbenchRunHistory = normalizedRunHistory;
    workbenchHistorySequence = nextWorkbenchSequenceFromIds(
      normalizedRunHistory,
      "workbench-history-",
    );
    selectedWorkbenchPacketRevisionId = normalizedHistory.some((entry) => entry.id === workspace.selectedWorkbenchPacketRevisionId)
      ? workspace.selectedWorkbenchPacketRevisionId
      : (normalizedHistory[0] ? normalizedHistory[0].id : "");
    selectedWorkbenchHistoryId = normalizedRunHistory.some((entry) => entry.id === workspace.selectedWorkbenchHistoryId)
      ? workspace.selectedWorkbenchHistoryId
      : (normalizedRunHistory[0] ? normalizedRunHistory[0].id : "");
    currentWorkbenchViewMode = typeof workspace.currentWorkbenchViewMode === "string" && workspace.currentWorkbenchViewMode
      ? workspace.currentWorkbenchViewMode
      : (normalizedRunHistory.length ? "latest" : "preparation");
    currentWorkbenchRunLabel = typeof workspace.currentWorkbenchRunLabel === "string" && workspace.currentWorkbenchRunLabel.trim()
      ? workspace.currentWorkbenchRunLabel
      : "手动生成";
    workbenchElement("workbench-packet-json").value = packetJsonText;
    setPacketSourceStatus(
      typeof workspace.packetSourceStatus === "string" && workspace.packetSourceStatus.trim()
        ? workspace.packetSourceStatus
        : packetSourceFallback
    );
    const fields = workspace.fields && typeof workspace.fields === "object" ? workspace.fields : {};
    workbenchPersistedFieldIds.forEach((id) => {
      applyWorkbenchPersistedFieldValue(id, fields[id]);
    });
    renderWorkbenchPacketRevisionHistory();
  });

  const parsed = parseWorkbenchPacketEditor();
  if (parsed.payload) {
    renderSystemFingerprintFromPacketPayload(parsed.payload, {
      badgeState: "idle",
      badgeText: "画像已恢复",
      summary: fingerprintSummary,
    });
  } else {
    renderSystemFingerprint({
      badgeState: "blocked",
      badgeText: "画像待修正",
      summary: `${successMessage} 但当前 JSON 还没恢复成合法 packet：${parsed.error}`,
      documentFallback: "先修正 JSON，再显示来源文档。",
      signalFallback: "先修正 JSON，再显示关键信号。",
    });
  }
  if (!normalizedRunHistory.length) {
    renderPreparationBoard(preparationMessage);
  } else if (currentWorkbenchViewMode === "history" && selectedWorkbenchHistoryId) {
    restoreWorkbenchHistoryEntry(selectedWorkbenchHistoryId);
  } else {
    restoreLatestWorkbenchHistory();
  }
  setActiveWorkbenchPreset("");
  persistWorkbenchPacketWorkspace();
  setRequestStatus(
    normalizedRunHistory.length
      ? sourceStatusMessageWithHistory
      : sourceStatusMessage,
    "success",
  );
  return true;
}

function restoreWorkbenchPacketWorkspaceFromBrowser() {
  const workspace = loadPersistedWorkbenchPacketWorkspace();
  if (!workspace) {
    return false;
  }
  return restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
    sourceStatusMessage: "已从浏览器恢复上次 packet 工作区。",
    sourceStatusMessageWithHistory: "已从浏览器恢复上次 packet 工作区和结果历史。",
    packetSourceFallback: "当前样例：已从浏览器恢复上次 packet 工作区。",
    preparationMessage: "已从浏览器恢复上次 packet 工作区；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
    fingerprintSummary: "已从浏览器恢复上次 packet 工作区。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
    successMessage: "已从浏览器恢复上次 packet 工作区。",
  });
}

function summarizeWorkbenchPacketRevisionEntry(entry) {
  if (!entry) {
    return null;
  }
  const summary = summarizePacketPayload(entry.payload);
  return {
    systemId: entry.payload.system_id || "unknown_system",
    docs: `${summary.sourceDocuments} 份`,
    logic: `${summary.logicNodes} logic / ${summary.components} components`,
    scenarios: `${summary.scenarios} scenarios / ${summary.faultModes} faults`,
    answers: `${summary.clarificationAnswers} answers`,
  };
}

function renderWorkbenchPacketRevisionCompareBar() {
  const compareBar = workbenchElement("workbench-packet-history-compare-bar");
  const latestEntry = latestWorkbenchPacketRevisionEntry();
  const selectedEntry = workbenchPacketRevisionHistory.find((entry) => entry.id === selectedWorkbenchPacketRevisionId) || null;

  if (!latestEntry || !selectedEntry || selectedEntry.id === latestEntry.id) {
    compareBar.hidden = true;
    return;
  }

  const replay = summarizeWorkbenchPacketRevisionEntry(selectedEntry);
  const latest = summarizeWorkbenchPacketRevisionEntry(latestEntry);

  workbenchElement("workbench-packet-history-compare-summary").textContent =
    `你正在回看「${selectedEntry.title}」，下面这些卡会直接告诉你它和最新 packet 在输入骨架上差在哪里。`;
  renderValue("workbench-packet-history-compare-system", `回看：${replay.systemId}`);
  renderValue("workbench-packet-history-compare-system-detail", `最新：${latest.systemId}`);
  renderValue("workbench-packet-history-compare-docs", `回看：${replay.docs}`);
  renderValue("workbench-packet-history-compare-docs-detail", `最新：${latest.docs}`);
  renderValue("workbench-packet-history-compare-logic", `回看：${replay.logic}`);
  renderValue("workbench-packet-history-compare-logic-detail", `最新：${latest.logic}`);
  renderValue("workbench-packet-history-compare-scenarios", `回看：${replay.scenarios}`);
  renderValue("workbench-packet-history-compare-scenarios-detail", `最新：${latest.scenarios}`);
  renderValue("workbench-packet-history-compare-answers", `回看：${replay.answers}`);
  renderValue("workbench-packet-history-compare-answers-detail", `最新：${latest.answers}`);
  compareBar.hidden = false;
}

function renderWorkbenchPacketRevisionHistory() {
  const container = workbenchElement("workbench-packet-history-cards");
  if (!workbenchPacketRevisionHistory.length) {
    container.replaceChildren((() => {
      const card = document.createElement("article");
      card.className = "workbench-history-card is-empty";
      const title = document.createElement("strong");
      title.textContent = "暂无版本";
      const detail = document.createElement("p");
      detail.textContent = "先载入 reference/template、本地 JSON，或在页面里写回一次 packet。";
      card.append(title, detail);
      return card;
    })());
    renderWorkbenchPacketHistoryViewBar();
    return;
  }

  container.replaceChildren(...workbenchPacketRevisionHistory.map((entry) => {
    const card = document.createElement("button");
    const selected = entry.id === selectedWorkbenchPacketRevisionId;
    const summary = summarizePacketPayload(entry.payload);
    card.type = "button";
    card.className = "workbench-history-card";
    card.dataset.selected = selected ? "true" : "false";
    card.setAttribute("aria-pressed", selected ? "true" : "false");
    card.addEventListener("click", () => {
      restoreWorkbenchPacketRevisionEntry(entry.id);
    });

    const meta = document.createElement("div");
    meta.className = "workbench-history-meta";

    const systemChip = document.createElement("span");
    systemChip.className = "workbench-history-chip";
    systemChip.textContent = entry.payload.system_id || "unknown_system";

    const coverageChip = document.createElement("span");
    coverageChip.className = "workbench-history-chip";
    coverageChip.textContent = `${summary.logicNodes}L / ${summary.scenarios}S / ${summary.faultModes}F`;

    const timeChip = document.createElement("span");
    timeChip.className = "workbench-history-chip";
    timeChip.textContent = entry.timeLabel;

    meta.append(systemChip, coverageChip, timeChip);

    const title = document.createElement("strong");
    title.textContent = entry.title;

    const summaryText = document.createElement("p");
    summaryText.textContent = entry.summary;

    const detail = document.createElement("p");
    detail.textContent = entry.detail;

    const action = document.createElement("span");
    action.className = "workbench-history-action";
    action.textContent = selected ? "当前输入区正在使用这个 Packet 版本" : "点此恢复这个 Packet 版本";

    card.append(meta, title, summaryText, detail, action);
    return card;
  }));
  renderWorkbenchPacketHistoryViewBar();
}

function pushWorkbenchPacketRevision(entry) {
  selectedWorkbenchPacketRevisionId = entry.id;
  workbenchPacketRevisionHistory = [entry, ...workbenchPacketRevisionHistory].slice(0, maxWorkbenchPacketRevisionHistory);
  renderWorkbenchPacketRevisionHistory();
  persistWorkbenchPacketWorkspace();
}

function captureCurrentWorkbenchPacketDraft({
  title,
  summary,
  detail = null,
} = {}) {
  const parsed = parseWorkbenchPacketEditor();
  if (parsed.error) {
    renderWorkbenchPacketDraftState();
    return {
      error: parsed.error,
      changed: false,
      entry: null,
      payload: null,
    };
  }

  const baselineEntry = selectedWorkbenchPacketRevisionEntry();
  const signature = packetRevisionSignature(parsed.payload);
  if (baselineEntry && baselineEntry.signature === signature) {
    renderWorkbenchPacketDraftState();
    return {
      error: null,
      changed: false,
      entry: baselineEntry,
      payload: parsed.payload,
    };
  }

  const entry = buildWorkbenchPacketRevisionEntry(parsed.payload, {
    title: title || "手动保存 Packet 草稿",
    summary: summary || "当前 packet 草稿已保存到版本历史。",
    detail,
  });
  pushWorkbenchPacketRevision(entry);
  return {
    error: null,
    changed: true,
    entry,
    payload: parsed.payload,
  };
}

function maybeAutoSnapshotCurrentPacketDraft(reason) {
  return captureCurrentWorkbenchPacketDraft({
    title: `自动保存草稿 / ${reason}`,
    summary: `在${reason}前自动收纳当前 packet 草稿。`,
  });
}

function saveCurrentWorkbenchPacketDraft() {
  const result = captureCurrentWorkbenchPacketDraft({
    title: "手动保存 Packet 草稿",
    summary: "当前 packet 草稿已手动保存到版本历史。",
  });
  if (result.error) {
    setRequestStatus(`当前 Packet 草稿无法保存：${result.error}`, "error");
    return;
  }
  if (!result.changed) {
    setRequestStatus("当前 Packet 已和已保存版本同步，无需重复保存草稿。", "warning");
    return;
  }
  setRequestStatus("当前 Packet 草稿已保存到版本历史。", "success");
}

function downloadWorkbenchWorkspaceSnapshot() {
  const snapshot = collectWorkbenchPacketWorkspaceState();
  try {
    const blob = new Blob([prettyJson(snapshot)], {type: "application/json"});
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = workspaceSnapshotDownloadName();
    anchor.click();
    URL.revokeObjectURL(objectUrl);
    setRequestStatus("当前工作区快照已导出。", "success");
  } catch (error) {
    setRequestStatus(`导出工作区快照失败：${String(error.message || error)}`, "error");
  }
}

async function importWorkbenchWorkspaceSnapshot(file) {
  if (!file) {
    return;
  }
  try {
    const rawText = await file.text();
    const workspace = JSON.parse(rawText);
    if (!workspace || typeof workspace !== "object") {
      throw new Error("快照不是有效对象。");
    }
    if (workspace.kind && workspace.kind !== "well-harness-workbench-browser-workspace") {
      throw new Error(`不支持的快照类型：${workspace.kind}`);
    }
    if (!restoreWorkbenchPacketWorkspaceSnapshot(workspace, {
      sourceStatusMessage: "已导入工作区快照。",
      sourceStatusMessageWithHistory: "已导入工作区快照和结果历史。",
      packetSourceFallback: `当前样例：已导入工作区快照 / ${file.name}。`,
      preparationMessage: "已导入工作区快照；如需确认当前输入，可以先看 packet 历史、草稿状态和系统画像。",
      fingerprintSummary: "已导入工作区快照。你可以继续编辑、保存草稿，或直接从这个状态重新运行 bundle。",
      successMessage: "已导入工作区快照。",
    })) {
      throw new Error("快照内容不完整，无法恢复工作区。");
    }
  } catch (error) {
    setRequestStatus(`导入工作区快照失败：${String(error.message || error)}`, "error");
  }
}

function archivePayloadFromRestoreResponse(payload) {
  const resolvedFiles = payload && typeof payload.resolved_files === "object" ? payload.resolved_files : {};
  return {
    archive_dir: payload.archive_dir || "",
    manifest_json_path: payload.manifest_path || "",
    bundle_json_path: resolvedFiles.bundle_json || null,
    summary_markdown_path: resolvedFiles.summary_markdown || null,
    intake_assessment_json_path: resolvedFiles.intake_assessment_json || null,
    clarification_brief_json_path: resolvedFiles.clarification_brief_json || null,
    playback_report_json_path: resolvedFiles.playback_report_json || null,
    fault_diagnosis_report_json_path: resolvedFiles.fault_diagnosis_report_json || null,
    knowledge_artifact_json_path: resolvedFiles.knowledge_artifact_json || null,
    workspace_handoff_json_path: resolvedFiles.workspace_handoff_json || null,
    workspace_snapshot_json_path: resolvedFiles.workspace_snapshot_json || null,
  };
}

async function restoreWorkbenchArchiveFromManifest() {
  const requestId = beginWorkbenchRequest();
  const manifestPath = workbenchElement("workbench-archive-manifest-path").value.trim();
  if (!manifestPath) {
    setRequestStatus("请先填写 archive_manifest.json 或 archive 目录路径。", "warning");
    return;
  }

  setActiveWorkbenchPreset("");
  setRequestStatus("正在从 archive 恢复工作区...", "neutral");
  try {
    const response = await fetch(workbenchArchiveRestorePath, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({manifest_path: manifestPath}),
    });
    const payload = await response.json();
    if (!isLatestWorkbenchRequest(requestId)) {
      return;
    }
    if (!response.ok) {
      throw new Error(payload.message || payload.error || "workbench archive restore request failed");
    }

    workbenchElement("workbench-archive-manifest-path").value = payload.archive_dir || payload.manifest_path || manifestPath;
    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromRestorePayload(payload));
    const sourceMode = `当前来源：Archive 恢复 / ${shortPath(payload.manifest_path)}。`;
    if (payload.workspace_snapshot && restoreWorkbenchPacketWorkspaceSnapshot(payload.workspace_snapshot, {
      sourceStatusMessage: `已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
      sourceStatusMessageWithHistory: `已从 archive 恢复工作区和结果历史 / ${shortPath(payload.manifest_path)}。`,
      packetSourceFallback: `当前样例：已从 archive 恢复工作区 / ${shortPath(payload.manifest_path)}。`,
      preparationMessage: "已从 archive 恢复工作区；如需确认当前输入，可以先看 packet 历史、结果历史和交接摘要。",
      fingerprintSummary: "已从 archive 恢复工作区。你可以继续编辑、重跑 bundle，或直接沿用归档里的历史结果继续交接。",
      successMessage: "已从 archive 恢复工作区。",
    })) {
      try {
        const restoredPacketSpec = JSON.parse(payload.workspace_snapshot.packetJsonText || "{}");
        assignFrozenSpec(restoredPacketSpec, "archive-restore");
      } catch (_) {
        // Non-critical: frozen spec not updated if snapshot packet is unparseable
      }
      setResultMode(sourceMode);
      return;
    }

    renderBundleResponse(
      {
        bundle: payload.bundle,
        archive: archivePayloadFromRestoreResponse(payload),
      },
      {
        sourceMode,
        requestStatusMessage: payload.workspace_snapshot
          ? "已从 archive 恢复 bundle，但工作区快照不完整；当前只恢复了结果摘要。"
          : "已从 archive 恢复 bundle 结果。",
        requestStatusTone: payload.workspace_snapshot ? "warning" : "success",
      },
    );
  } catch (error) {
    if (!isLatestWorkbenchRequest(requestId)) {
      return;
    }
    setRequestStatus(`从 archive 恢复工作区失败：${String(error.message || error)}`, "error");
  }
}

function maybeCaptureCurrentPacketRevision({
  title,
  summary,
  detail = null,
} = {}) {
  let payload;
  try {
    payload = JSON.parse(workbenchElement("workbench-packet-json").value);
  } catch (error) {
    return null;
  }
  const latestEntry = latestWorkbenchPacketRevisionEntry();
  const signature = packetRevisionSignature(payload);
  if (latestEntry && latestEntry.signature === signature) {
    return latestEntry;
  }
  const entry = buildWorkbenchPacketRevisionEntry(payload, {
    title,
    summary,
    detail,
  });
  pushWorkbenchPacketRevision(entry);
  return entry;
}

function restoreWorkbenchPacketRevisionEntry(entryId) {
  const entry = workbenchPacketRevisionHistory.find((item) => item.id === entryId);
  if (!entry) {
    return;
  }
  maybeAutoSnapshotCurrentPacketDraft(`恢复 ${entry.title}`);
  selectedWorkbenchPacketRevisionId = entry.id;
  renderWorkbenchPacketRevisionHistory();
  setActiveWorkbenchPreset("");
  setPacketEditor(entry.payload);
  setPacketSourceStatus(`当前 packet：已恢复 ${entry.title} / ${entry.timeLabel}。建议重新运行 bundle 验证这个版本。`);
  renderPreparationBoard(`已恢复 packet 版本「${entry.title}」。重新运行后，主看板会按这个版本显示最新结果。`);
  renderSystemFingerprintFromPacketPayload(entry.payload, {
    badgeState: "idle",
    badgeText: "画像已恢复",
    summary: "你正在回看一个历史 packet 版本；如果这个版本更合适，可以直接在此基础上继续修和重跑。",
  });
  renderWorkbenchPacketRevisionHistory();
  setRequestStatus(`已恢复 packet 版本：${entry.title}`, "success");
}

function restoreLatestWorkbenchPacketRevision() {
  const latestEntry = latestWorkbenchPacketRevisionEntry();
  if (!latestEntry) {
    return;
  }
  restoreWorkbenchPacketRevisionEntry(latestEntry.id);
}

function setWorkbenchViewState(mode, historyId = "") {
  currentWorkbenchViewMode = mode;
  selectedWorkbenchHistoryId = historyId;
  persistWorkbenchPacketWorkspace();
}

function latestWorkbenchHistoryEntry() {
  return workbenchRunHistory.length ? workbenchRunHistory[0] : null;
}

function summarizeWorkbenchHistoryEntry(entry) {
  const bundle = entry && entry.payload ? entry.payload.bundle || {} : {};
  return {
    verdict: entry ? entry.stateLabel : "-",
    scenario: bundle.selected_scenario_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
    faultMode: bundle.selected_fault_mode_id || (entry && entry.state === "failure" ? "请求失败" : "(none)"),
    archive: entry && entry.archived ? "已留档" : "未留档",
  };
}

function detailedWorkbenchHistoryEntry(entry) {
  if (!entry) {
    return null;
  }
  if (!entry.payload) {
    return {
      title: `${entry.title} / ${entry.timeLabel}`,
      verdict: "失败",
      blocker: entry.detail || "请求未完成",
      scenario: "请求失败",
      faultMode: "请求失败",
      knowledge: "未生成",
      archive: "未留档",
    };
  }

  const bundle = entry.payload.bundle || {};
  const clarification = bundle.clarification_brief || {};
  const knowledge = bundle.knowledge_artifact || {};
  const archive = entry.payload.archive || null;
  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
    ? bundle.intake_assessment.blocking_reasons
    : [];
  const ready = Boolean(bundle.ready_for_spec_build);

  return {
    title: `${entry.title} / ${entry.timeLabel}`,
    verdict: ready ? "通过" : "阻塞",
    blocker: ready
      ? "当前无阻塞"
      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 仍未 ready。"),
    scenario: bundle.selected_scenario_id || "(none)",
    faultMode: bundle.selected_fault_mode_id || "(none)",
    knowledge: ready ? (knowledge.status || "已生成") : "尚未形成",
    archive: archive ? `已留档 / ${shortPath(archive.archive_dir)}` : "未留档",
  };
}

function workbenchHistoryDetailFields(snapshot, compareSnapshot) {
  const compare = compareSnapshot || {};
  return [
    {label: "结论", value: snapshot.verdict, diff: snapshot.verdict === compare.verdict ? "same" : "changed"},
    {label: "当前卡点", value: snapshot.blocker, diff: snapshot.blocker === compare.blocker ? "same" : "changed"},
    {label: "Scenario", value: snapshot.scenario, diff: snapshot.scenario === compare.scenario ? "same" : "changed"},
    {label: "Fault Mode", value: snapshot.faultMode, diff: snapshot.faultMode === compare.faultMode ? "same" : "changed"},
    {label: "知识沉淀", value: snapshot.knowledge, diff: snapshot.knowledge === compare.knowledge ? "same" : "changed"},
    {label: "归档状态", value: snapshot.archive, diff: snapshot.archive === compare.archive ? "same" : "changed"},
  ];
}

function renderWorkbenchHistoryDetailCard({
  titleElementId,
  bodyElementId,
  snapshot,
  compareSnapshot,
}) {
  workbenchElement(titleElementId).textContent = snapshot.title;
  const body = workbenchElement(bodyElementId);
  body.replaceChildren(...workbenchHistoryDetailFields(snapshot, compareSnapshot).map((field) => {
    const row = document.createElement("div");
    row.className = "workbench-history-detail-row";

    const label = document.createElement("span");
    label.className = "workbench-history-detail-label";
    label.textContent = field.label;

    const value = document.createElement("strong");
    value.className = "workbench-history-detail-value";
    value.dataset.diff = field.diff;
    value.textContent = field.value;

    row.append(label, value);
    return row;
  }));
}

function renderWorkbenchHistoryCompareBar() {
  const compareBar = workbenchElement("workbench-history-compare-bar");
  const latestEntry = latestWorkbenchHistoryEntry();
  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;

  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry) {
    compareBar.hidden = true;
    return;
  }

  const replay = summarizeWorkbenchHistoryEntry(selectedEntry);
  const latest = summarizeWorkbenchHistoryEntry(latestEntry);

  workbenchElement("workbench-history-compare-summary").textContent =
    `你正在回看「${selectedEntry.title}」，下面这 4 项会直接告诉你它和最新结果差在哪里。`;
  renderValue("workbench-history-compare-verdict", `回看：${replay.verdict}`);
  renderValue("workbench-history-compare-verdict-detail", `最新：${latest.verdict}`);
  renderValue("workbench-history-compare-scenario", `回看：${replay.scenario}`);
  renderValue("workbench-history-compare-scenario-detail", `最新：${latest.scenario}`);
  renderValue("workbench-history-compare-fault", `回看：${replay.faultMode}`);
  renderValue("workbench-history-compare-fault-detail", `最新：${latest.faultMode}`);
  renderValue("workbench-history-compare-archive", `回看：${replay.archive}`);
  renderValue("workbench-history-compare-archive-detail", `最新：${latest.archive}`);
  compareBar.hidden = false;
}

function renderWorkbenchHistoryDetailBoard() {
  const detailBoard = workbenchElement("workbench-history-detail-board");
  const latestEntry = latestWorkbenchHistoryEntry();
  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;

  if (currentWorkbenchViewMode !== "history" || !latestEntry || !selectedEntry || latestEntry.id === selectedEntry.id) {
    detailBoard.hidden = true;
    return;
  }

  const replaySnapshot = detailedWorkbenchHistoryEntry(selectedEntry);
  const latestSnapshot = detailedWorkbenchHistoryEntry(latestEntry);
  renderWorkbenchHistoryDetailCard({
    titleElementId: "workbench-history-detail-replay-title",
    bodyElementId: "workbench-history-detail-replay",
    snapshot: replaySnapshot,
    compareSnapshot: latestSnapshot,
  });
  renderWorkbenchHistoryDetailCard({
    titleElementId: "workbench-history-detail-latest-title",
    bodyElementId: "workbench-history-detail-latest",
    snapshot: latestSnapshot,
    compareSnapshot: replaySnapshot,
  });
  detailBoard.hidden = false;
}

function renderWorkbenchHistoryViewBar() {
  const latestEntry = latestWorkbenchHistoryEntry();
  const selectedEntry = workbenchRunHistory.find((entry) => entry.id === selectedWorkbenchHistoryId) || null;
  const statusElement = workbenchElement("workbench-history-view-status");
  const returnButton = workbenchElement("workbench-history-return-latest");

  if (currentWorkbenchViewMode === "running") {
    statusElement.textContent = "当前查看：正在生成新结果";
    returnButton.disabled = true;
    renderWorkbenchHistoryCompareBar();
    renderWorkbenchHistoryDetailBoard();
    return;
  }

  if (currentWorkbenchViewMode === "preparation") {
    statusElement.textContent = "当前查看：样例准备中";
    returnButton.disabled = true;
    renderWorkbenchHistoryCompareBar();
    renderWorkbenchHistoryDetailBoard();
    return;
  }

  if (!latestEntry) {
    statusElement.textContent = "当前查看：等待第一次结果";
    returnButton.disabled = true;
    renderWorkbenchHistoryCompareBar();
    renderWorkbenchHistoryDetailBoard();
    return;
  }

  if (currentWorkbenchViewMode !== "history" || !selectedEntry || selectedEntry.id === latestEntry.id) {
    statusElement.textContent = `当前查看：最新结果 / ${latestEntry.title} / ${latestEntry.timeLabel}`;
    returnButton.disabled = true;
    renderWorkbenchHistoryCompareBar();
    renderWorkbenchHistoryDetailBoard();
    return;
  }

  statusElement.textContent = `当前查看：历史回看 / ${selectedEntry.title} / ${selectedEntry.timeLabel}`;
  returnButton.disabled = false;
  renderWorkbenchHistoryCompareBar();
  renderWorkbenchHistoryDetailBoard();
}

function renderWorkbenchRunHistory() {
  const container = workbenchElement("workbench-history-cards");
  if (!workbenchRunHistory.length) {
    container.replaceChildren((() => {
      const card = document.createElement("article");
      card.className = "workbench-history-card is-empty";
      const title = document.createElement("strong");
      title.textContent = "暂无结果";
      const detail = document.createElement("p");
      detail.textContent = "先点一个一键预设或手动生成一次 bundle。";
      card.append(title, detail);
      return card;
    })());
    renderWorkbenchHistoryViewBar();
    return;
  }

  container.replaceChildren(...workbenchRunHistory.map((entry) => {
    const card = document.createElement("button");
    const selected = entry.id === selectedWorkbenchHistoryId;
    card.type = "button";
    card.className = "workbench-history-card";
    card.dataset.selected = selected ? "true" : "false";
    card.setAttribute("aria-pressed", selected ? "true" : "false");
    card.addEventListener("click", () => {
      restoreWorkbenchHistoryEntry(entry.id);
    });

    const meta = document.createElement("div");
    meta.className = "workbench-history-meta";

    const stateChip = document.createElement("span");
    stateChip.className = "workbench-history-chip";
    stateChip.dataset.state = entry.state;
    stateChip.textContent = entry.stateLabel;

    const archiveChip = document.createElement("span");
    archiveChip.className = "workbench-history-chip";
    archiveChip.dataset.state = entry.archived ? "archived" : entry.state;
    archiveChip.textContent = entry.archived ? "已留档" : "未留档";

    const timeChip = document.createElement("span");
    timeChip.className = "workbench-history-chip";
    timeChip.textContent = entry.timeLabel;

    meta.append(stateChip, archiveChip, timeChip);

    const title = document.createElement("strong");
    title.textContent = entry.title;

    const summary = document.createElement("p");
    summary.textContent = entry.summary;

    const detail = document.createElement("p");
    detail.textContent = entry.detail;

    const action = document.createElement("span");
    action.className = "workbench-history-action";
    action.textContent = selected ? "当前主看板正在显示这次结果" : "点此回看这次结果";

    card.append(meta, title, summary, detail, action);
    return card;
  }));
  renderWorkbenchHistoryViewBar();
}

function historyTimeLabel() {
  return new Date().toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function buildWorkbenchHistoryEntryFromPayload(payload) {
  const bundle = payload.bundle || {};
  const clarification = bundle.clarification_brief || {};
  const archive = payload.archive || null;
  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
    ? bundle.intake_assessment.blocking_reasons
    : [];
  const ready = Boolean(bundle.ready_for_spec_build);
  return {
    id: nextWorkbenchHistoryId(),
    state: ready ? "ready" : "blocked",
    stateLabel: ready ? "通过" : "阻塞",
    archived: Boolean(archive),
    timeLabel: historyTimeLabel(),
    title: currentWorkbenchRunLabel,
    payload: cloneJson(payload),
    summary: ready
      ? `已生成 ${bundle.bundle_kind || "bundle"}，scenario=${bundle.selected_scenario_id || "none"}`
      : `停在 ${clarification.gate_status || "clarification"}，等待补齐信息`,
    detail: ready
      ? (archive ? `archive：${shortPath(archive.archive_dir)}` : "本次未生成 archive。")
      : (blockingReasons[0] || clarification.gating_statement || "当前 packet 尚未 ready。"),
  };
}

function buildWorkbenchHistoryEntryFromFailure(message) {
  return {
    id: nextWorkbenchHistoryId(),
    state: "failure",
    stateLabel: "失败",
    archived: false,
    timeLabel: historyTimeLabel(),
    title: currentWorkbenchRunLabel,
    errorMessage: String(message),
    summary: "请求未完成",
    detail: message,
  };
}

function workbenchHistoryTone(state) {
  if (state === "ready") {
    return "success";
  }
  if (state === "blocked") {
    return "warning";
  }
  return "error";
}

function renderFailureResponse(message, {
  pushHistory = true,
  sourceMode = "当前来源：workbench bundle 请求失败。",
  requestStatusMessage = `生成失败：${String(message)}`,
  requestStatusTone = "error",
} = {}) {
  const normalizedMessage = String(message);
  setResultMode(sourceMode);
  workbenchElement("bundle-json-output").textContent = prettyJson({
    error: "workbench_bundle_failed",
    message: normalizedMessage,
  });
  renderExplainRuntime({});
  renderFailureBoard(normalizedMessage);
  if (pushHistory) {
    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromFailure(normalizedMessage));
  }
  setRequestStatus(requestStatusMessage, requestStatusTone);
}

function restoreWorkbenchHistoryEntry(entryId) {
  const entry = workbenchRunHistory.find((item) => item.id === entryId);
  if (!entry) {
    return;
  }
  setWorkbenchViewState("history", entry.id);
  renderWorkbenchRunHistory();
  setActiveWorkbenchPreset("");
  if (entry.payload) {
    renderBundleResponse(entry.payload, {
      pushHistory: false,
      sourceMode: "当前来源：最近验收结果回看。",
      requestStatusMessage: `已回看：${entry.title}`,
      requestStatusTone: workbenchHistoryTone(entry.state),
    });
    return;
  }
  renderFailureResponse(entry.errorMessage || entry.detail, {
    pushHistory: false,
    sourceMode: "当前来源：最近验收结果回看。",
    requestStatusMessage: `已回看：${entry.title}`,
    requestStatusTone: workbenchHistoryTone(entry.state),
  });
}

function restoreLatestWorkbenchHistory() {
  const latestEntry = latestWorkbenchHistoryEntry();
  if (!latestEntry) {
    return;
  }
  setWorkbenchViewState("latest", latestEntry.id);
  renderWorkbenchRunHistory();
  setActiveWorkbenchPreset("");
  if (latestEntry.payload) {
    renderBundleResponse(latestEntry.payload, {
      pushHistory: false,
      sourceMode: "当前来源：最新结果回看。",
      requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
      requestStatusTone: workbenchHistoryTone(latestEntry.state),
    });
    return;
  }
  renderFailureResponse(latestEntry.errorMessage || latestEntry.detail, {
    pushHistory: false,
    sourceMode: "当前来源：最新结果回看。",
    requestStatusMessage: `已回到最新结果：${latestEntry.title}`,
    requestStatusTone: workbenchHistoryTone(latestEntry.state),
  });
}

function renderRunningBoard(message) {
  setWorkbenchViewState("running");
  setVisualBadge("idle", "正在生成");
  renderOnboardingReadiness({
    badgeState: "idle",
    badgeText: "正在评估",
    summary: "系统正在检查这份 packet 能不能作为第二套控制逻辑的可靠起点。",
    gaps: "评估中",
  });
  renderValue("workbench-spotlight-verdict", "正在处理中");
  renderValue("workbench-spotlight-verdict-detail", message);
  renderValue("workbench-spotlight-blocker", "正在判定");
  renderValue("workbench-spotlight-blocker-detail", "系统正在检查当前 packet 是通过还是阻塞。");
  renderValue("workbench-spotlight-knowledge", "处理中");
  renderValue("workbench-spotlight-knowledge-detail", "如果 bundle ready，knowledge 结果会在本轮生成。");
  renderValue("workbench-spotlight-archive", "处理中");
  renderValue("workbench-spotlight-archive-detail", "如果本轮勾选 archive，系统会在生成后汇报落档结果。");
  renderOnboardingActions({
    badgeState: "idle",
    badgeText: "动作解析中",
    summary: "系统正在按真实 clarification / schema 结果生成动作板，不会在前端自己猜步骤。",
  });
  renderSchemaRepairWorkspace({
    badgeState: "idle",
    badgeText: "修复解析中",
    summary: "系统正在检查这次 blocked bundle 里有没有被后端判定为 safe autofix 的 schema 修复项。",
    fallbackTitle: "正在解析",
    fallbackText: "请稍等，系统正在决定这次 run 有没有可直接应用的安全 schema 修复。",
    note: "工作台只会接受后端明确给出的 repair suggestion。",
    actionsDisabled: true,
  });
  renderClarificationWorkspace({
    badgeState: "idle",
    badgeText: "回填解析中",
    summary: "系统正在读取真实 clarification gate 结果；只有后端确认的待答问题才会被放进这个回填工作台。",
    fallbackTitle: "正在解析",
    fallbackText: "请稍等，系统正在决定这次 run 有没有需要直接回填的 clarification。",
    note: "当前不会在前端凭空生成问题，只复用 bundle 真实返回的 follow_up_items。",
    actionsDisabled: true,
  });
  renderValue("workbench-visual-summary", "系统正在跑当前 bundle。以最后一次点击为准，旧响应不会覆盖新结果。");
  setStageState("intake", "pending", "正在读取当前 packet。");
  setStageState("clarification", "pending", "正在检查 clarification gate。");
  setStageState("playback", "idle", "等待前序结果。");
  setStageState("diagnosis", "idle", "等待前序结果。");
  setStageState("knowledge", "idle", "等待前序结果。");
  setStageState("archive", "idle", "等待前序结果。");
  renderWorkbenchHistoryViewBar();
}

function renderFailureBoard(message) {
  setVisualBadge("blocked", "请求失败");
  renderOnboardingReadiness({
    badgeState: "blocked",
    badgeText: "请求失败",
    summary: "这次不是 packet 本身通过或阻塞，而是请求失败了，所以还不能判断第二套系统接入准备度。",
    gaps: "先修正请求",
  });
  renderValue("workbench-spotlight-verdict", "需要修正输入");
  renderValue("workbench-spotlight-verdict-detail", message);
  renderValue("workbench-spotlight-blocker", "请求未完成");
  renderValue("workbench-spotlight-blocker-detail", "先修正输入或请求错误，再重新运行。");
  renderValue("workbench-spotlight-knowledge", "未生成");
  renderValue("workbench-spotlight-knowledge-detail", "因为请求失败，所以没有下游结果。");
  renderValue("workbench-spotlight-archive", "未生成");
  renderValue("workbench-spotlight-archive-detail", "本次没有产生 archive package。");
  renderOnboardingActions({
    badgeState: "blocked",
    badgeText: "动作未生成",
    summary: `这次不是 clarification 阻塞，而是请求本身失败了，所以动作板也还不能可靠生成：${message}`,
    followUpFallback: "先修正请求，再显示澄清动作。",
    blockerFallback: "先修正请求，再显示结构 blocker。",
    unlockFallback: "先修正请求，再显示解锁项。",
  });
  renderSchemaRepairWorkspace({
    badgeState: "blocked",
    badgeText: "暂不可修复",
    summary: "这次请求没有成功，所以还不能可靠判断哪些 schema blocker 适合安全 autofix。",
    fallbackTitle: "先修正请求",
    fallbackText: "等请求恢复成功后，这里才会出现真实 schema repair suggestion。",
    note: "当前错误优先级高于 schema repair；先把请求恢复正常。",
    actionsDisabled: true,
  });
  renderClarificationWorkspace({
    badgeState: "blocked",
    badgeText: "暂不可回填",
    summary: "这次请求没有成功，所以工作台现在也不能可靠判断应该让你回答哪些 clarification。",
    fallbackTitle: "先修正请求",
    fallbackText: "等请求恢复成功后，这里才会出现真实的 clarification 回填项。",
    note: "当前错误优先级高于 clarification 回填；先把 JSON 或请求本身修好。",
    actionsDisabled: true,
  });
  renderValue("workbench-visual-summary", "这次不是 bundle 阻塞，而是请求本身没有成功。先修正输入，再重新点击“生成 Bundle”。");
  setStageState("intake", "blocked", "输入或请求存在问题。");
  setStageState("clarification", "idle", "等待请求恢复。");
  setStageState("playback", "idle", "等待请求恢复。");
  setStageState("diagnosis", "idle", "等待请求恢复。");
  setStageState("knowledge", "idle", "等待请求恢复。");
  setStageState("archive", "idle", "等待请求恢复。");
}

function applyReferencePacketSelection({
  archiveBundle,
  sourceStatus,
  preparationMessage,
}) {
  if (!bootstrapPayload) {
    return false;
  }
  maybeAutoSnapshotCurrentPacketDraft("载入参考样例");
  setPacketEditor(bootstrapPayload.reference_packet);
  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.reference_packet, {
    title: "载入参考样例",
    summary: "reference packet 已重新载入。",
  }));
  fillReferenceResolutionDefaults();
  workbenchElement("workbench-scenario-id").value = "";
  workbenchElement("workbench-fault-mode-id").value = "";
  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  setPacketSourceStatus(sourceStatus);
  renderPreparationBoard(preparationMessage);
  renderSystemFingerprintFromPacketPayload(bootstrapPayload.reference_packet, {
    badgeState: "idle",
    badgeText: "画像已载入",
    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  });
  return true;
}

function applyTemplatePacketSelection({
  archiveBundle,
  sourceStatus,
  preparationMessage,
}) {
  if (!bootstrapPayload) {
    return false;
  }
  maybeAutoSnapshotCurrentPacketDraft("载入空白模板");
  setPacketEditor(bootstrapPayload.template_packet);
  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(bootstrapPayload.template_packet, {
    title: "载入空白模板",
    summary: "template packet 已载入，适合演示 blocked onboarding。",
  }));
  clearResolutionDefaults();
  workbenchElement("workbench-scenario-id").value = "";
  workbenchElement("workbench-fault-mode-id").value = "";
  workbenchElement("workbench-archive-toggle").checked = archiveBundle;
  setPacketSourceStatus(sourceStatus);
  renderPreparationBoard(preparationMessage);
  renderSystemFingerprintFromPacketPayload(bootstrapPayload.template_packet, {
    badgeState: "blocked",
    badgeText: "画像待补齐",
    summary: "空白模板已经装载。虽然它还没 ready，但你已经可以先确认它的文档方向、控制目标和关键信号占位是不是对的。",
  });
  return true;
}

function runWorkbenchPreset(presetId) {
  const preset = workbenchPresets[presetId];
  if (!preset) {
    return;
  }
  if (!bootstrapPayload) {
    setRequestStatus("bootstrap 尚未加载完成，请稍后再点预设。", "warning");
    return;
  }
  const applied = preset.source === "template"
    ? applyTemplatePacketSelection(preset)
    : applyReferencePacketSelection(preset);
  if (!applied) {
    setRequestStatus("当前样例还没准备好，请稍后再试。", "warning");
    return;
  }
  setActiveWorkbenchPreset(presetId);
  setRequestStatus(`${preset.label}：正在自动生成结果...`, "neutral");
  void runWorkbenchBundle();
}

function fillReferenceResolutionDefaults() {
  workbenchElement("workbench-root-cause").value = defaultReferenceResolution.rootCause;
  workbenchElement("workbench-repair-action").value = defaultReferenceResolution.repairAction;
  workbenchElement("workbench-validation-after-fix").value = defaultReferenceResolution.validationAfterFix;
  workbenchElement("workbench-residual-risk").value = defaultReferenceResolution.residualRisk;
  workbenchElement("workbench-logic-change").value = defaultReferenceResolution.logicChange;
  workbenchElement("workbench-reliability-gain").value = defaultReferenceResolution.reliabilityGain;
  workbenchElement("workbench-guardrail-note").value = defaultReferenceResolution.guardrailNote;
  workbenchElement("workbench-evidence-links").value = "";
  workbenchElement("workbench-observed-symptoms").value = "";
}

function clearResolutionDefaults() {
  [
    "workbench-root-cause",
    "workbench-repair-action",
    "workbench-validation-after-fix",
    "workbench-residual-risk",
    "workbench-logic-change",
    "workbench-reliability-gain",
    "workbench-guardrail-note",
    "workbench-evidence-links",
    "workbench-observed-symptoms",
  ].forEach((id) => {
    workbenchElement(id).value = "";
  });
}

function renderBulletList(containerId, items, fallbackText) {
  const container = workbenchElement(containerId);
  const effectiveItems = Array.isArray(items) && items.length ? items : [fallbackText];
  container.replaceChildren(
    ...effectiveItems.map((item) => {
      const li = document.createElement("li");
      li.textContent = String(item);
      return li;
    }),
  );
}

function readExplainRuntimePayload(payload) {
  const runtime = payload
    && typeof payload === "object"
    && payload.explain_runtime
    && typeof payload.explain_runtime === "object"
    && !Array.isArray(payload.explain_runtime)
    ? payload.explain_runtime
    : null;
  if (!runtime) {
    return {
      reported: false,
      status: "",
      statusSource: "",
      backend: "",
      model: "",
      source: "",
      cachedAt: "",
      observedAt: "",
      cacheHits: null,
      expectedCount: null,
      backendMatch: null,
      requestedBackend: "",
      requestedModel: "",
      detail: "",
      boundaryNote: "",
    };
  }
  const toTrimmedString = (value) => (typeof value === "string" ? value.trim() : "");
  const toNonNegativeInt = (value) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? Math.floor(parsed) : null;
  };
  return {
    reported: true,
    status: toTrimmedString(runtime.status),
    statusSource: toTrimmedString(runtime.status_source),
    backend: toTrimmedString(runtime.llm_backend),
    model: toTrimmedString(runtime.llm_model),
    source: toTrimmedString(runtime.response_source || runtime.last_response_source),
    cachedAt: toTrimmedString(runtime.cached_at),
    observedAt: toTrimmedString(runtime.observed_at_utc),
    cacheHits: toNonNegativeInt(runtime.verified_cache_hits ?? runtime.cache_hits),
    expectedCount: toNonNegativeInt(runtime.expected_count),
    backendMatch: runtime.backend_match === true ? true : (runtime.backend_match === false ? false : null),
    requestedBackend: toTrimmedString(runtime.requested_backend),
    requestedModel: toTrimmedString(runtime.requested_model),
    detail: toTrimmedString(runtime.detail),
    boundaryNote: toTrimmedString(runtime.boundary_note),
  };
}

function explainRuntimeSourceLabel(source) {
  if (source === "cached_llm") return "缓存命中";
  if (source === "live_llm") return "实时 LLM";
  if (source === "error") return "运行错误";
  return "未观察";
}

function explainRuntimeBadgeState(runtime) {
  if (runtime.status === "shelved") return "shelved";
  if (!runtime.reported) return "idle";
  if (runtime.backendMatch === false || runtime.status === "warning") return "blocked";
  if (runtime.source === "cached_llm") return "ready";
  if (runtime.source === "error") return "blocked";
  if (runtime.source === "live_llm") return "live";
  return "idle";
}

function explainRuntimeBadgeText(runtime) {
  if (runtime.status === "shelved") return "已搁置";
  if (!runtime.reported) return "未报告";
  if (runtime.backendMatch === false) return "后端不一致";
  if (runtime.status === "ready" && runtime.source === "cached_llm") return "缓存已验证";
  if (runtime.source === "live_llm") return "实时 explain";
  if (runtime.status === "warning") return "需要关注";
  return "待命";
}

function renderExplainRuntime(payload) {
  const badge = workbenchElement("workbench-explain-runtime-badge");
  const summary = workbenchElement("workbench-explain-runtime-summary");
  const backendStrong = workbenchElement("workbench-explain-runtime-backend");
  const backendDetail = workbenchElement("workbench-explain-runtime-backend-detail");
  const sourceStrong = workbenchElement("workbench-explain-runtime-source");
  const sourceDetail = workbenchElement("workbench-explain-runtime-source-detail");
  const cacheStrong = workbenchElement("workbench-explain-runtime-cache");
  const cacheDetail = workbenchElement("workbench-explain-runtime-cache-detail");
  const boundaryStrong = workbenchElement("workbench-explain-runtime-boundary");
  if (!badge || !summary || !backendStrong || !sourceStrong || !cacheStrong || !boundaryStrong) {
    return;
  }

  const runtime = readExplainRuntimePayload(payload);
  badge.dataset.state = explainRuntimeBadgeState(runtime);
  badge.textContent = explainRuntimeBadgeText(runtime);

  // Phase A (2026-04-22): LLM features shelved. Short-circuit to a clean
  // "shelved" rendering so the cache/backend/source panels don't misreport
  // zero-counters as observed prewarm telemetry.
  if (runtime.status === "shelved") {
    summary.textContent = runtime.detail || "LLM explain 功能已搁置。";
    backendStrong.textContent = "已搁置";
    backendDetail.textContent = "LLM 后端已从活跃代码库搁置，见 archive/shelved/llm-features/SHELVED.md。";
    sourceStrong.textContent = "已搁置";
    sourceDetail.textContent = "explain 路由已移除，不会产生新的观察记录。";
    cacheStrong.textContent = "已搁置";
    cacheDetail.textContent = "LLM 缓存链路已停用；无 cached_at / 命中统计。";
    boundaryStrong.textContent = runtime.boundaryNote || "LLM 已搁置 — 非控制真值";
    return;
  }

  if (!runtime.reported) {
    summary.textContent = "当前 workbench 响应还没带 explain runtime 观察值，所以这里只保留占位。";
  } else if (runtime.observedAt) {
    summary.textContent = `${runtime.detail || "已收到 explain runtime 观察值。"} 最近观测时间：${runtime.observedAt}。`;
  } else {
    summary.textContent = runtime.detail || "已收到 explain runtime 观察值。";
  }

  if (runtime.backend || runtime.model) {
    const backendText = runtime.backend || "(未知 backend)";
    const modelText = runtime.model || "(未知 model)";
    backendStrong.textContent = `${backendText} · ${modelText}`;
    if (runtime.backendMatch === false) {
      const requestedBackendText = runtime.requestedBackend || "(未声明 backend)";
      const requestedModelText = runtime.requestedModel || "(auto)";
      backendDetail.textContent = `最近 pitch_prewarm 请求的是 ${requestedBackendText} · ${requestedModelText}，但当前观察到的运行后端不是这套，需要先纠正 demo_server。`;
    } else if (runtime.observedAt) {
      backendDetail.textContent = `这是最近一次 explain runtime 观测到的后端组合。观测时间：${runtime.observedAt}。`;
    } else {
      backendDetail.textContent = "这是当前 demo_server 暴露出来的 explain 后端组合；它只是操作者运行观察值，不改变任何控制真值。";
    }
  } else {
    backendStrong.textContent = "未报告";
    backendDetail.textContent = "后端暂未在 bootstrap / bundle 响应中提供 explain_runtime.llm_backend / llm_model，前端保留占位。";
  }

  sourceStrong.textContent = explainRuntimeSourceLabel(runtime.source);
  if (runtime.backendMatch === false) {
    sourceDetail.textContent = "虽然最近预热流程有结果，但它对应的 backend / model 和当前期望不一致，所以这里会明确提醒，不把它误当成安全可用的缓存状态。";
  } else if (runtime.source === "cached_llm") {
    sourceDetail.textContent = "最近一次 explain 命中了预热缓存，说明 prewarm 生效；重启 demo_server 后需重新预热。";
  } else if (runtime.source === "live_llm") {
    sourceDetail.textContent = "最近一次 explain 走了实时 LLM（缓存未命中或未启用），请关注首次响应时延。";
  } else if (runtime.source === "error") {
    sourceDetail.textContent = "最近一次 explain 报错，详情请看 dev 抽屉 raw payload 或 server 日志。";
  } else {
    sourceDetail.textContent = "本轮还没观察到 explain 调用；一旦用户在 chat / demo 舱发起一次 explain，这里就会亮起。";
  }

  if (runtime.cachedAt) {
    const hitsPart = runtime.cacheHits !== null ? ` · 验证命中 ${runtime.cacheHits}` : "";
    const expectedPart = runtime.expectedCount !== null ? `/${runtime.expectedCount}` : "";
    cacheStrong.textContent = runtime.cachedAt;
    cacheDetail.textContent = `cached_at 上报为 ${runtime.cachedAt}${hitsPart}${expectedPart}。explain 缓存只在 demo_server 进程内有效，重启或换 backend 都会清空，需要重新预热。`;
  } else if (runtime.cacheHits !== null || runtime.expectedCount !== null) {
    const parts = [];
    if (runtime.cacheHits !== null && runtime.expectedCount !== null) {
      parts.push(`验证命中 ${runtime.cacheHits}/${runtime.expectedCount}`);
    } else if (runtime.cacheHits !== null) {
      parts.push(`验证命中 ${runtime.cacheHits}`);
    } else if (runtime.expectedCount !== null) {
      parts.push(`预期 ${runtime.expectedCount}`);
    }
    cacheStrong.textContent = parts.join(" / ") || "待命";
    cacheDetail.textContent = "尚未看到 cached_at 时间戳，但最近 pitch_prewarm 已经回传了命中统计；仍可用来判断缓存是否在服务。";
  } else {
    cacheStrong.textContent = "待命";
    cacheDetail.textContent = "尚未看到 cached_at。若刚刚跑过 prewarm，请核对 demo_server 输出；否则这里会保持“待命”直到首次 explain 观察上报。";
  }

  boundaryStrong.textContent = runtime.boundaryNote || "runtime status only";
}

function renderArchiveSummary(archive) {
  const statusElement = workbenchElement("archive-status");
  if (!archive) {
    statusElement.textContent = "本次未生成 archive package。";
    renderBulletList("archive-files", [], "勾选“同时生成 archive package”后，成功运行会显示文件列表。");
    return;
  }
  statusElement.textContent = `已生成 archive package：${archive.archive_dir}`;
  const filePaths = [
    archive.manifest_json_path,
    archive.bundle_json_path,
    archive.summary_markdown_path,
    archive.intake_assessment_json_path,
    archive.clarification_brief_json_path,
    archive.playback_report_json_path,
    archive.fault_diagnosis_report_json_path,
    archive.knowledge_artifact_json_path,
    archive.workspace_handoff_json_path,
    archive.workspace_snapshot_json_path,
  ].filter(Boolean);
  renderBulletList("archive-files", filePaths, "Archive package 已生成。");
}

function renderOnboardingReadinessFromPayload(payload) {
  const bundle = payload.bundle || {};
  const assessment = bundle.intake_assessment || {};
  const clarification = bundle.clarification_brief || {};
  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  const sourceCount = Number(assessment.source_document_count || 0);
  const componentCount = Number(assessment.component_count || 0);
  const logicCount = Number(assessment.logic_node_count || 0);
  const scenarioCount = Number(assessment.acceptance_scenario_count || 0);
  const faultCount = Number(assessment.fault_mode_count || 0);
  const openQuestionCount = Number(clarification.open_question_count || 0);
  const blockingReasonCount = Number(clarification.blocking_reason_count || 0);
  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  const answeredClarifications = followUpItems.filter((item) => item.status === "answered").length;
  const ready = Boolean(bundle.ready_for_spec_build);
  const sourceMode = sourceKinds.length ? sourceKinds.join(" + ") : "未识别来源";
  const unlocks = Array.isArray(clarification.unlocks_after_completion) && clarification.unlocks_after_completion.length
    ? clarification.unlocks_after_completion.join(" / ")
    : (ready ? "spec_build / scenario_playback / fault_diagnosis / knowledge_capture" : "spec_build");

  renderOnboardingReadiness({
    badgeState: ready ? "ready" : "blocked",
    badgeText: ready ? "可接第二套系统" : "还不能安全接入",
    summary: ready
      ? "这份 packet 已经具备进入第二套控制逻辑 spec build 的基本条件，可以继续往 playback、diagnosis、knowledge 走。"
      : "这份 packet 还不够完整。系统已经把“缺什么”拆出来了，先补齐再接第二套控制逻辑更稳。",
    docs: `${sourceCount} 份`,
    docsDetail: sourceCount
      ? `${sourceMode}${assessment.mixed_source_packet ? " / 混合来源" : ""}${assessment.includes_pdf_sources ? " / 含 PDF" : ""}`
      : "还没有来源文档。",
    components: `${componentCount} 项`,
    componentsDetail: componentCount ? "已有组件/信号定义。" : "还没有组件定义。",
    logic: `${logicCount} 个`,
    logicDetail: logicCount ? "已有逻辑节点结构。" : "还没有逻辑节点。",
    scenarios: `${scenarioCount} 个`,
    scenariosDetail: scenarioCount ? "已有可回放验收场景。" : "还没有验收场景。",
    faults: `${faultCount} 个`,
    faultsDetail: faultCount ? "已有故障模式可注入。" : "还没有故障模式。",
    clarifications: `${answeredClarifications}/${followUpItems.length || openQuestionCount || 0}`,
    clarificationsDetail: openQuestionCount
      ? `还有 ${openQuestionCount} 个澄清问题没回答。`
      : "澄清问题已补齐。",
    unlocks,
    gaps: `${blockingReasonCount} 个结构问题 / ${openQuestionCount} 个澄清问题`,
  });
}

function renderSystemFingerprintFromPayload(payload) {
  const bundle = payload.bundle || {};
  const assessment = bundle.intake_assessment || {};
  const clarification = bundle.clarification_brief || {};
  const generatedSpec = assessment.generated_workbench_spec || {};
  const ready = Boolean(bundle.ready_for_spec_build);
  const sourceKinds = Array.isArray(assessment.source_document_kinds) ? assessment.source_document_kinds : [];
  const sourceModeParts = [joinWithFallback(sourceKinds.map(documentKindLabel), "未识别来源")];

  if (assessment.mixed_source_packet) {
    sourceModeParts.push("混合来源");
  }
  if (assessment.includes_pdf_sources) {
    sourceModeParts.push("含 PDF");
  }

  renderSystemFingerprint({
    badgeState: ready ? "ready" : "blocked",
    badgeText: ready ? "画像已识别" : "画像待补齐",
    summary: ready
      ? "这套系统已经不只是“能接入”，而是连文档覆盖、控制目标、工程真值和关键信号都已经清楚摊开了。"
      : "虽然这份 packet 还没 ready，但它的系统画像已经先展开了；你可以先确认方向对不对，再补缺口。",
    systemId: bundle.system_id || assessment.system_id || workbenchElement("workbench-fingerprint-system-id").textContent,
    objective: assessment.objective || workbenchElement("workbench-fingerprint-objective").textContent,
    sourceMode: sourceModeParts.join(" / "),
    sourceTruth: generatedSpec.source_of_truth || workbenchElement("workbench-fingerprint-source-truth").textContent,
    documents: Array.isArray(clarification.source_documents) ? clarification.source_documents : [],
    signals: Array.isArray(assessment.custom_signal_semantics) ? assessment.custom_signal_semantics : [],
    documentFallback: "当前 bundle 还没有识别出来源文档。",
    signalFallback: "当前 bundle 还没有识别出关键信号。",
  });
}

function renderOnboardingActionsFromPayload(payload) {
  const bundle = payload.bundle || {};
  const assessment = bundle.intake_assessment || {};
  const clarification = bundle.clarification_brief || {};
  const ready = Boolean(bundle.ready_for_spec_build);
  const followUpItems = Array.isArray(clarification.follow_up_items) ? clarification.follow_up_items : [];
  const blockingReasons = Array.isArray(assessment.blocking_reasons) ? assessment.blocking_reasons : [];
  const unlocks = Array.isArray(clarification.unlocks_after_completion) ? clarification.unlocks_after_completion : [];

  const pendingFollowUps = followUpItems
    .filter((item) => item.status !== "answered")
    .map((item) => createActionItemCard({
      title: item.id || "clarification",
      detail: item.prompt || "等待补齐说明。",
      chipText: "待回答",
      chipTone: "blocked",
    }));

  const schemaBlockers = blockingReasons.map((reason, index) => createActionItemCard({
    title: `schema blocker ${index + 1}`,
    detail: reason,
    chipText: "待补结构",
    chipTone: "blocked",
  }));

  const unlockItems = unlocks.map((item) => createActionItemCard({
    title: item,
    detail: ready
      ? "这项能力已经放行，可以继续往下走。"
      : "把左边两列补齐后，这项能力就会被解锁。",
    chipText: ready ? "已解锁" : "待解锁",
    chipTone: ready ? "ready" : "signal",
  }));

  renderOnboardingActions({
    badgeState: ready ? "ready" : "blocked",
    badgeText: ready ? "接入路径已放行" : "接入路径待补齐",
    summary: ready
      ? "这套系统当前已经没有澄清或结构阻塞，动作板上只保留已放行的下一步能力。"
      : "这套系统还没 ready，但动作板已经把先补什么、再补什么、补完解锁什么拆开了。",
    followUps: pendingFollowUps,
    blockers: schemaBlockers,
    unlocks: unlockItems,
    followUpFallback: ready ? "澄清项都已回答。" : "当前没有待回答澄清项。",
    blockerFallback: ready ? "结构问题已补齐。" : "当前没有额外结构 blocker。",
    unlockFallback: "当前没有可展示的解锁项。",
  });
}

function renderVisualAcceptanceBoard(payload) {
  const bundle = payload.bundle || {};
  const clarification = bundle.clarification_brief || {};
  const diagnosis = bundle.fault_diagnosis_report || {};
  const knowledge = bundle.knowledge_artifact || {};
  const archive = payload.archive || null;
  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
    ? bundle.intake_assessment.blocking_reasons
    : [];
  const ready = Boolean(bundle.ready_for_spec_build);

  if (ready) {
    setVisualBadge(archive ? "archived" : "ready", archive ? "通过并已归档" : "可以验收");
    renderValue("workbench-spotlight-verdict", "链路已跑通");
    renderValue(
      "workbench-spotlight-verdict-detail",
      archive
        ? "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge，并已留下 archive。"
        : "当前样例已经完成 intake -> clarification -> playback -> diagnosis -> knowledge。"
    );
    renderValue("workbench-spotlight-blocker", "当前无阻塞");
    renderValue(
      "workbench-spotlight-blocker-detail",
      bundle.selected_fault_mode_id
        ? `当前 fault mode：${bundle.selected_fault_mode_id}，可以直接看右侧卡片做验收。`
        : "当前没有 blocking reason。"
    );
    renderValue("workbench-spotlight-knowledge", knowledge.status || "已生成");
    renderValue(
      "workbench-spotlight-knowledge-detail",
      knowledge.diagnosis_summary || diagnosis.suspected_root_cause || "知识沉淀已生成。"
    );
    renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
    renderValue(
      "workbench-spotlight-archive-detail",
      archive
        ? `目录：${shortPath(archive.archive_dir)}`
        : "本次没有生成 archive package。"
    );
    renderValue(
      "workbench-visual-summary",
      "这次 bundle 已经走完整条 engineer workflow。你现在主要看步骤状态带和聚焦卡片，不必先看 Raw JSON。"
    );
    setStageState("intake", "complete", "packet 已通过 intake 检查。");
    setStageState("clarification", "complete", clarification.gate_status || "clarification 已放行。");
    setStageState("playback", "complete", "已生成可复盘的 playback。");
    setStageState("diagnosis", "complete", diagnosis.suspected_root_cause || "已生成 diagnosis。");
    setStageState("knowledge", "complete", knowledge.status ? `knowledge=${knowledge.status}` : "已生成 knowledge artifact。");
    setStageState("archive", archive ? "complete" : "pending", archive ? "archive package 已落档。" : "本次未归档，但可随时重跑。");
    return;
  }

  setVisualBadge(archive ? "archived" : "blocked", archive ? "阻塞但已归档" : "当前阻塞");
  renderValue("workbench-spotlight-verdict", "需要补信息");
  renderValue(
    "workbench-spotlight-verdict-detail",
    "当前 packet 还没走到 playback / diagnosis / knowledge，先补齐 clarification gate 需要的信息。"
  );
  renderValue("workbench-spotlight-blocker", "Clarification Gate");
  renderValue(
    "workbench-spotlight-blocker-detail",
    blockingReasons.length ? blockingReasons[0] : clarification.gating_statement || "当前 packet 仍未 ready。"
  );
  renderValue("workbench-spotlight-knowledge", "尚未形成");
  renderValue("workbench-spotlight-knowledge-detail", "因为 clarification 还没过，所以 diagnosis / knowledge 还不会生成。");
  renderValue("workbench-spotlight-archive", archive ? "已落档" : "未落档");
  renderValue(
    "workbench-spotlight-archive-detail",
    archive
      ? `已把当前阻塞态留档到 ${shortPath(archive.archive_dir)}`
      : "如果你想保留这次阻塞态，可以勾选 archive 后重跑。"
  );
  renderValue(
    "workbench-visual-summary",
    "这次不是失败，而是系统在 clarification gate 主动停下来了。你只要看卡在哪一步，不需要读后面的专业输出。"
  );
  setStageState("intake", "complete", "packet 已被读取并检查。");
  setStageState("clarification", "blocked", clarification.gate_status || "clarification 仍未放行。");
  setStageState("playback", "idle", "clarification 未过，暂不继续。");
  setStageState("diagnosis", "idle", "clarification 未过，暂不继续。");
  setStageState("knowledge", "idle", "clarification 未过，暂不继续。");
  setStageState("archive", archive ? "complete" : "pending", archive ? "阻塞态也已成功归档。" : "当前未归档。");
}

function renderBundleResponse(payload, {
  pushHistory = true,
  sourceMode = "当前来源：`POST /api/workbench/bundle`。",
  requestStatusMessage = null,
  requestStatusTone = null,
} = {}) {
  const bundle = payload.bundle || {};
  const clarification = bundle.clarification_brief || {};
  const playback = bundle.playback_report || {};
  const diagnosis = bundle.fault_diagnosis_report || {};
  const knowledge = bundle.knowledge_artifact || {};
  const resolution = knowledge.resolution_record || {};
  const optimization = knowledge.optimization_record || {};
  const ready = Boolean(bundle.ready_for_spec_build);
  workbenchElement("bundle-kind").textContent = bundle.bundle_kind || "-";
  workbenchElement("bundle-ready-state").textContent = ready ? "Ready" : "Blocked";
  workbenchElement("bundle-ready-state").dataset.state = ready ? "ready" : "blocked";
  workbenchElement("bundle-scenario-id").textContent = bundle.selected_scenario_id || "(none)";
  workbenchElement("bundle-fault-mode-id").textContent = bundle.selected_fault_mode_id || "(none)";
  workbenchElement("clarification-gate-status").textContent = clarification.gate_status || "-";
  workbenchElement("clarification-gating-statement").textContent = clarification.gating_statement || "-";
  const blockingReasons = bundle.intake_assessment && Array.isArray(bundle.intake_assessment.blocking_reasons)
    ? bundle.intake_assessment.blocking_reasons
    : [];
  workbenchElement("bundle-blocking-reasons").textContent = blockingReasons.length
    ? blockingReasons.join(" | ")
    : "none";

  renderOnboardingReadinessFromPayload(payload);
  renderSystemFingerprintFromPayload(payload);
  renderOnboardingActionsFromPayload(payload);
  renderSchemaRepairWorkspaceFromPayload(payload);
  renderClarificationWorkspaceFromPayload(payload);
  renderVisualAcceptanceBoard(payload);
  renderBulletList("bundle-next-actions", bundle.next_actions, "当前没有 next actions。");
  renderValue("playback-scenario-label", playback.scenario_label, ready ? "未提供 playback label。" : "Blocked bundle 不包含 playback。");
  renderValue("playback-completion", playback.completion_reached, ready ? "false" : "Blocked bundle 不包含 playback。");
  renderValue("playback-sampled-signals", Array.isArray(playback.signal_series) ? playback.signal_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  renderValue("playback-sampled-logic", Array.isArray(playback.logic_series) ? playback.logic_series.length : null, ready ? "0" : "Blocked bundle 不包含 playback。");
  renderValue("diagnosis-fault-mode", diagnosis.fault_mode_id || bundle.selected_fault_mode_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  renderValue("diagnosis-target-component", diagnosis.target_component_id, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  renderValue("diagnosis-root-cause", diagnosis.suspected_root_cause, ready ? "(none)" : "Blocked bundle 不包含 diagnosis。");
  renderValue(
    "diagnosis-blocked-logic",
    Array.isArray(diagnosis.blocked_logic_node_ids) && diagnosis.blocked_logic_node_ids.length
      ? diagnosis.blocked_logic_node_ids.join(" | ")
      : null,
    ready ? "none" : "Blocked bundle 不包含 diagnosis。",
  );
  renderValue("knowledge-status", knowledge.status, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("knowledge-diagnosis-summary", knowledge.diagnosis_summary, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("knowledge-confirmed-root-cause", resolution.confirmed_root_cause, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("knowledge-repair-action", resolution.repair_action, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("knowledge-validation-after-fix", resolution.validation_after_fix, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("knowledge-residual-risk", resolution.residual_risk, ready ? "(none)" : "Blocked bundle 不包含 knowledge artifact。");
  renderValue("optimization-logic-change", optimization.suggested_logic_change, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  renderValue("optimization-reliability-gain", optimization.reliability_gain_hypothesis, ready ? "(none)" : "Blocked bundle 不包含 optimization record。");
  renderValue(
    "optimization-guardrail-note",
    optimization.redundancy_reduction_or_guardrail_note,
    ready ? "(none)" : "Blocked bundle 不包含 optimization record。",
  );
  if (pushHistory) {
    pushWorkbenchRunHistory(buildWorkbenchHistoryEntryFromPayload(payload));
  }
  if (payload.archive) {
    upsertRecentWorkbenchArchiveEntry(buildRecentWorkbenchArchiveEntryFromBundlePayload(payload));
  }
  renderArchiveSummary(payload.archive);
  renderExplainRuntime(payload);
  workbenchElement("bundle-json-output").textContent = prettyJson(payload);
  setResultMode(sourceMode);
  setRequestStatus(
    requestStatusMessage || (
      ready
        ? "Bundle 已生成，可直接拿右侧结果做验收。"
        : "Clarification follow-up bundle 已生成；当前 packet 仍被 schema / clarification gate 阻塞。"
    ),
    requestStatusTone || (ready ? "success" : "warning"),
  );
}

function collectWorkbenchRequestPayload() {
  let packetPayload;
  try {
    packetPayload = JSON.parse(workbenchElement("workbench-packet-json").value);
  } catch (error) {
    throw new Error(`packet JSON 解析失败：${String(error.message || error)}`);
  }
  return {
    packet_payload: packetPayload,
    scenario_id: workbenchElement("workbench-scenario-id").value.trim() || undefined,
    fault_mode_id: workbenchElement("workbench-fault-mode-id").value.trim() || undefined,
    sample_period_s: Number(workbenchElement("workbench-sample-period").value || "0.5"),
    archive_bundle: workbenchElement("workbench-archive-toggle").checked,
    workspace_handoff: buildWorkbenchHandoffSnapshot(),
    workspace_snapshot: collectWorkbenchPacketWorkspaceState(),
    observed_symptoms: workbenchElement("workbench-observed-symptoms").value.trim() || undefined,
    evidence_links: splitLines(workbenchElement("workbench-evidence-links").value),
    confirmed_root_cause: workbenchElement("workbench-root-cause").value.trim() || undefined,
    repair_action: workbenchElement("workbench-repair-action").value.trim() || undefined,
    validation_after_fix: workbenchElement("workbench-validation-after-fix").value.trim() || undefined,
    residual_risk: workbenchElement("workbench-residual-risk").value.trim() || undefined,
    suggested_logic_change: workbenchElement("workbench-logic-change").value.trim() || undefined,
    reliability_gain_hypothesis: workbenchElement("workbench-reliability-gain").value.trim() || undefined,
    guardrail_note: workbenchElement("workbench-guardrail-note").value.trim() || undefined,
  };
}

function checkUrlIntakeParam() {
  try {
    const params = new URLSearchParams(window.location.search);
    const intakeRaw = params.get("intake");
    let intakePacket;
    let textarea;
    if (!intakeRaw) {
      return false;
    }
    try {
      intakePacket = JSON.parse(intakeRaw);
    } catch (parseError) {
      intakePacket = JSON.parse(decodeURIComponent(intakeRaw));
    }
    if (!intakePacket || typeof intakePacket !== "object") {
      return false;
    }
    setPacketEditor(intakePacket);
    textarea = workbenchElement("workbench-packet-json");
    if (textarea) {
      textarea.scrollTop = textarea.scrollHeight;
    }
    pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(intakePacket, {
      title: "Pipeline 结果预载入",
      summary: "通过 URL intake 参数载入的 packet。",
    }));
    renderPreparationBoard("Pipeline 结果已经装载，系统会自动生成 bundle 并显示诊断结果。");
    renderSystemFingerprintFromPacketPayload(intakePacket, {
      badgeState: "idle",
      badgeText: "画像已载入",
      summary: "Pipeline 结果已经带入当前 workbench，系统会直接继续生成 bundle。",
    });
    setPacketSourceStatus("当前样例：来自 AI Document Analyzer 的 Pipeline 结果。页面会自动生成 Bundle。");
    setCurrentWorkbenchRunLabel("Pipeline 结果导入");
    setActiveWorkbenchPreset("");
    return true;
  } catch (error) {
    return false;
  }
}

async function loadBootstrapPayload() {
  setRequestStatus("正在加载 bootstrap 样例...", "neutral");
  const response = await fetch(workbenchBootstrapPath, {method: "GET"});
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "bootstrap request failed");
  }
  bootstrapPayload = payload;
  renderExplainRuntime(payload);
  workbenchRecentArchives = normalizeRecentWorkbenchArchiveEntries(payload.recent_archives);
  renderRecentWorkbenchArchives();
  workbenchElement("default-archive-root").textContent = payload.default_archive_root || "(unknown)";
  if (restoreWorkbenchPacketWorkspaceFromBrowser()) {
    return;
  }
  setPacketEditor(payload.reference_packet);
  pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(payload.reference_packet, {
    title: "默认参考样例",
    summary: "启动时自动载入的 reference packet。",
  }));
  fillReferenceResolutionDefaults();
  setPacketSourceStatus("当前样例：参考样例。适合直接点“生成 Bundle”做可视化 happy path 验收。");
  renderPreparationBoard("参考样例已经装载完毕，点击“生成 Bundle”即可进入可视化验收。");
  renderSystemFingerprintFromPacketPayload(payload.reference_packet, {
    badgeState: "idle",
    badgeText: "画像已载入",
    summary: "参考样例已经装载。你现在就能先看这套系统的文档来源、控制目标和关键信号，不必等 bundle 跑完。",
  });
  setActiveWorkbenchPreset("");
  setRequestStatus("已载入 reference packet，直接点“生成 Bundle”即可跑 happy path。", "success");
}

async function runWorkbenchBundle() {
  const requestId = beginWorkbenchRequest();
  let requestPayload;
  try {
    requestPayload = collectWorkbenchRequestPayload();
  } catch (error) {
    if (!isLatestWorkbenchRequest(requestId)) {
      return false;
    }
    renderFailureResponse(String(error.message || error), {
      sourceMode: "当前来源：输入解析失败。",
      requestStatusMessage: String(error.message || error),
    });
    return false;
  }
  maybeCaptureCurrentPacketRevision({
    title: `${currentWorkbenchRunLabel} / 运行前 Packet`,
    summary: "在本次 bundle 请求前捕获当前 packet 版本。",
  });
  renderSystemFingerprintFromPacketPayload(requestPayload.packet_payload, {
    badgeState: "idle",
    badgeText: "画像解析中",
    summary: "系统正在生成 bundle，但这套系统的文档来源、控制目标和关键信号已经先展开给你看了。",
  });
  renderRunningBoard(`${currentWorkbenchRunLabel}：正在生成 bundle，请直接看上方可视化验收板。`);
  setRequestStatus("正在生成 workbench bundle...", "neutral");
  try {
    const response = await fetch(workbenchBundlePath, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(requestPayload),
    });
    const payload = await response.json();
    if (!isLatestWorkbenchRequest(requestId)) {
      return false;
    }
    if (!response.ok) {
      throw new Error(payload.message || payload.error || "workbench bundle request failed");
    }
    renderBundleResponse(payload);
    return true;
  } catch (error) {
    if (!isLatestWorkbenchRequest(requestId)) {
      return false;
    }
    renderFailureResponse(String(error.message || error));
    return false;
  }
}

function installPacketSourceHandlers() {
  workbenchElement("load-reference-packet").addEventListener("click", () => {
    if (!applyReferencePacketSelection({
      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
      sourceStatus: "当前样例：参考样例。适合直接点 '生成 Bundle' 做可视化 happy path 验收。",
      preparationMessage: "参考样例已经装载完毕，点击 '生成 Bundle' 即可进入可视化验收。",
    })) {
      return;
    }
    setCurrentWorkbenchRunLabel("手动生成");
    setActiveWorkbenchPreset("");
    setRequestStatus("已载入 reference packet。", "success");
  });

  workbenchElement("load-template-packet").addEventListener("click", () => {
    if (!applyTemplatePacketSelection({
      archiveBundle: workbenchElement("workbench-archive-toggle").checked,
      sourceStatus: "当前样例：空白模板。适合验证 clarification gate 是否会主动拦住不完整 packet。",
      preparationMessage: "空白模板已经装载完毕，运行后通常会在 clarification gate 停下。",
    })) {
      return;
    }
    setCurrentWorkbenchRunLabel("手动生成");
    setActiveWorkbenchPreset("");
    setRequestStatus("已载入空白模板。", "warning");
  });

  workbenchElement("workbench-file-input").addEventListener("change", async (event) => {
    const input = event.currentTarget;
    const [file] = input.files || [];
    if (!file) {
      return;
    }

    const text = await file.text();
    maybeAutoSnapshotCurrentPacketDraft("导入本地 JSON / " + file.name);
    workbenchElement("workbench-packet-json").value = text;
    setPacketSourceStatus("当前样例：本地文件 " + file.name + "。如果不是在调试，可以直接点 '生成 Bundle' 看可视化结果。");
    renderPreparationBoard("本地 JSON 已装载，运行后会把当前 packet 的通过/阻塞结果显示在上方看板。");

    try {
      const packetPayload = JSON.parse(text);
      pushWorkbenchPacketRevision(buildWorkbenchPacketRevisionEntry(packetPayload, {
        title: "导入本地 JSON / " + file.name,
        summary: "本地 packet 已导入输入区。",
      }));
      renderSystemFingerprintFromPacketPayload(packetPayload, {
        badgeState: "idle",
        badgeText: "画像已载入",
        summary: "本地 JSON 已装载。你现在就能先看这套系统的大致画像，再决定要不要继续生成 bundle。",
      });
    } catch (error) {
      renderSystemFingerprint({
        badgeState: "blocked",
        badgeText: "画像未识别",
        summary: "本地 JSON 还没解析成功，所以系统画像暂时无法展开：" + String(error.message || error),
        documentFallback: "先修正 JSON，再显示来源文档。",
        signalFallback: "先修正 JSON，再显示关键信号。",
      });
    }

    setCurrentWorkbenchRunLabel("手动生成 / " + file.name);
    setActiveWorkbenchPreset("");
    setRequestStatus("已载入本地文件：" + file.name, "success");
    input.value = "";
  });
}

function installWorkspaceSnapshotHandlers() {
  workbenchElement("export-workbench-workspace").addEventListener("click", () => {
    downloadWorkbenchWorkspaceSnapshot();
  });

  workbenchElement("restore-workbench-archive").addEventListener("click", () => {
    void restoreWorkbenchArchiveFromManifest();
  });

  workbenchElement("refresh-workbench-recent-archives").addEventListener("click", () => {
    void refreshRecentWorkbenchArchives();
  });

  workbenchElement("copy-workbench-handoff-brief").addEventListener("click", () => {
    void copyWorkbenchHandoffBrief();
  });

  workbenchElement("workbench-workspace-file-input").addEventListener("change", async (event) => {
    const input = event.currentTarget;
    const [file] = input.files || [];
    if (!file) {
      return;
    }

    await importWorkbenchWorkspaceSnapshot(file);
    input.value = "";
  });
}

function installExecutionHandlers() {
  workbenchElement("run-workbench-bundle").addEventListener("click", () => {
    setCurrentWorkbenchRunLabel("手动生成");
    setActiveWorkbenchPreset("");
    void runWorkbenchBundle();
  });

  document.querySelectorAll(".workbench-preset-trigger").forEach((button) => {
    button.addEventListener("click", () => {
      setCurrentWorkbenchRunLabel(button.textContent.trim());
      runWorkbenchPreset(button.dataset.workbenchPreset || "");
    });
  });
}

function installP43Handlers() {
  const approveBtn = workbenchElement("workbench-final-approve");
  if (approveBtn) {
    approveBtn.addEventListener("click", () => { handleFinalApprove(); });
  }
  const startGenBtn = workbenchElement("workbench-start-gen");
  if (startGenBtn) {
    startGenBtn.addEventListener("click", () => { void handleStartGen(); });
  }
}

function installPersistenceHandlers() {
  workbenchElement("workbench-packet-json").addEventListener("input", () => {
    renderWorkbenchPacketDraftState();
    persistWorkbenchPacketWorkspace();
    saveDraftDesignState({
      packetJsonText: workbenchElement("workbench-packet-json").value,
      savedAt: new Date().toISOString(),
    });
  });

  workbenchPersistedFieldIds.forEach((id) => {
    const field = workbenchElement(id);
    const eventName = field && field.type === "checkbox" ? "change" : "input";
    field.addEventListener(eventName, () => {
      persistWorkbenchPacketWorkspace();
    });
  });
}

function installRecoveryAndRepairHandlers() {
  workbenchElement("workbench-history-return-latest").addEventListener("click", () => {
    restoreLatestWorkbenchHistory();
  });

  workbenchElement("workbench-packet-history-return-latest").addEventListener("click", () => {
    restoreLatestWorkbenchPacketRevision();
  });

  workbenchElement("workbench-save-packet-draft").addEventListener("click", () => {
    saveCurrentWorkbenchPacketDraft();
  });

  workbenchElement("workbench-apply-schema-repairs").addEventListener("click", () => {
    void runWorkbenchSchemaSafeRepair();
  });

  workbenchElement("workbench-apply-clarifications").addEventListener("click", () => {
    void applyClarificationWorkspace({ rerun: false });
  });

  workbenchElement("workbench-apply-and-rerun").addEventListener("click", () => {
    void applyClarificationWorkspace({ rerun: true });
  });
}

function installToolbarHandlers() {
  installPacketSourceHandlers();
  installWorkspaceSnapshotHandlers();
  installExecutionHandlers();
  installPersistenceHandlers();
  installRecoveryAndRepairHandlers();
  installP43Handlers();
}

function installViewModeHandlers() {
  function setViewMode(mode) {
    document.body.dataset.view = mode;
    workbenchElement("view-btn-beginner").classList.toggle("is-active", mode === "beginner");
    workbenchElement("view-btn-expert").classList.toggle("is-active", mode === "expert");
    workbenchElement("view-mode-hint").textContent = mode === "beginner"
      ? "— 专家工具默认折叠，适合先看结论"
      : "— 显示所有工具：JSON 编辑器 / schema repair / clarification";
  }

  const beginnerBtn = workbenchElement("view-btn-beginner");
  const expertBtn = workbenchElement("view-btn-expert");
  if (!beginnerBtn || !expertBtn) {
    return;
  }

  beginnerBtn.addEventListener("click", () => {
    setViewMode("beginner");
  });
  expertBtn.addEventListener("click", () => {
    setViewMode("expert");
  });

  setViewMode("beginner");
}

// E11-13 (2026-04-25): manual_feedback_override trust-affordance.
// Reads #workbench-feedback-mode chip's data-feedback-mode attribute; mirrors
// it onto #workbench-trust-banner so the banner shows only when mode =
// manual_feedback_override. Provides setFeedbackMode(mode) for runtime updates
// (e.g., when the snapshot endpoint reports a different mode in future
// E11-14+). Banner dismissal is session-local (sessionStorage); chip + actual
// mode value remain visible across dismissals.
function syncTrustBannerForMode(mode) {
  const banner = document.getElementById("workbench-trust-banner");
  if (banner) {
    banner.setAttribute("data-feedback-mode", mode);
  }
}

function setFeedbackMode(mode) {
  const allowed = new Set(["manual_feedback_override", "truth_engine"]);
  if (!allowed.has(mode)) {
    return false;
  }
  const chip = document.getElementById("workbench-feedback-mode");
  if (chip) {
    chip.setAttribute("data-feedback-mode", mode);
    const label = chip.querySelector("strong");
    if (label) {
      label.textContent = mode === "truth_engine" ? "Truth Engine" : "Manual (advisory)";
    }
  }
  syncTrustBannerForMode(mode);
  return true;
}

function installFeedbackModeAffordance() {
  const chip = document.getElementById("workbench-feedback-mode");
  const banner = document.getElementById("workbench-trust-banner");
  if (!chip || !banner) {
    return;
  }
  syncTrustBannerForMode(chip.getAttribute("data-feedback-mode") || "manual_feedback_override");
  if (window.sessionStorage && window.sessionStorage.getItem("workbench-trust-banner-dismissed") === "1") {
    banner.setAttribute("data-trust-banner-dismissed", "true");
  }
  const dismiss = banner.querySelector("[data-trust-banner-dismiss]");
  if (dismiss) {
    dismiss.addEventListener("click", () => {
      banner.setAttribute("data-trust-banner-dismissed", "true");
      if (window.sessionStorage) {
        window.sessionStorage.setItem("workbench-trust-banner-dismissed", "1");
      }
    });
  }
}

window.addEventListener("DOMContentLoaded", () => {
  bootWorkbenchShell();
  installViewModeHandlers();
  installFeedbackModeAffordance();

  // E11-09 (2026-04-25): bundle UI lives on /workbench/bundle, served by
  // workbench_bundle.html. The /workbench shell page (workbench.html) does
  // NOT contain bundle elements like #workbench-packet-json,
  // #load-reference-packet, #run-workbench-bundle, etc. installToolbarHandlers,
  // updateWorkflowUI, checkUrlIntakeParam, and loadBootstrapPayload all assume
  // bundle DOM exists and would throw "Cannot read properties of null" on the
  // shell page. Sentinel = bundle's textarea input. Absent → shell page →
  // skip bundle boot entirely. This script is shared between both pages.
  const onBundlePage = document.getElementById("workbench-packet-json") !== null;
  if (!onBundlePage) {
    return;
  }

  installToolbarHandlers();
  updateWorkflowUI();
  if (checkUrlIntakeParam()) {
    const bundleBtn = workbenchElement("run-workbench-bundle") || workbenchElement("workbench-bundle-btn");
    if (bundleBtn) {
      setRequestStatus("正在从 Pipeline 结果生成 Bundle...", "neutral");
      bundleBtn.click();
    }
    return;
  }
  void loadBootstrapPayload();
});

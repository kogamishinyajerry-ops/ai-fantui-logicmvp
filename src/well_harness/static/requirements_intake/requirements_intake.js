(function () {
  "use strict";

  const LOGIC_BUILDER_INPUT_KEY = "ai-fantui-requirements-intake-ready-v1";
  const LOGIC_BUILDER_DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1";
  const LOGIC_BUILDER_HISTORY_KEY = "ai-fantui-logic-builder-change-history-v1";
  const FAULT_DRAFT_KEY = "ai-fantui-fault-injection-preparation-v1";
  const SANDBOX_PLAN_KEY = "ai-fantui-fault-injection-sandbox-plan-v1";
  const REVISION_HANDOFF_KEY = "ai-fantui-fault-injection-sandbox-revision-handoff-v1";
  const REPLAY_ENDPOINT = "/api/requirements-intake/deepseek-live-demo-replay";

  const state = {
    uploadMode: "text",
    uploadBase64: "",
    lastPayload: null,
    providerLiveReady: false,
    preserveDownstreamDrafts: false,
    taskTimer: null,
    taskStartedAt: 0,
    taskPercent: 0,
    analysisRounds: [],
    lastSubmittedAnswers: [],
  };

  const $ = (id) => document.getElementById(id);
  const form = $("requirements-form");
  const dropzone = $("requirements-dropzone");
  const fileInput = $("requirements-file");
  const fileState = $("requirements-file-state");
  const documentName = $("requirements-document-name");
  const textArea = $("requirements-text");
  const provider = $("requirements-provider");
  const providerStatus = $("requirements-provider-status");
  const providerKeySource = $("requirements-provider-key-source");
  const deepseekLiveOnly = $("requirements-live-only");
  const preflightLiveCard = $("requirements-preflight-live-card");
  const preflightLiveState = $("requirements-preflight-live-state");
  const preflightReplayState = $("requirements-preflight-replay-state");
  const preflightOfflineState = $("requirements-preflight-offline-state");
  const replayImportButton = $("requirements-replay-import");
  const offlineActionButton = $("requirements-offline-action");
  const analyzeButton = $("requirements-analyze");
  const clearButton = $("requirements-clear");
  const statusLine = $("requirements-status");
  const processPanel = $("process-panel");
  const processTitle = $("process-title");
  const processElapsed = $("process-elapsed");
  const processFill = $("process-fill");
  const processDetail = $("process-detail");
  const processSteps = {
    read: $("process-step-read"),
    parse: $("process-step-parse"),
    send: $("process-step-send"),
    render: $("process-step-render"),
  };
  const streamChunks = $("requirements-stream-chunks");
  const PROCESS_STEP_ORDER = ["read", "parse", "send", "render"];
  const STREAM_CHUNK_COPY = {
    read: "读取需求：已收到输入",
    parse: "本地预解析：先生成可读候选",
    send: "DeepSeek 增强：正在补齐语义",
    render: "生成下一步：刷新可继续状态",
  };
  const resultState = $("result-state");
  const resultFlags = $("result-flags");
  const workflowStage = $("requirements-workflow-stage");
  const workflowDetail = $("requirements-workflow-detail");
  const workflowSteps = Array.from(document.querySelectorAll("#requirements-workflow-steps .workflow-step"));
  const summary = $("requirements-summary");
  const questions = $("requirements-questions");
  const clarificationList = $("clarification-list");
  const clarificationProgress = $("clarification-progress");
  const clarificationResubmit = $("clarification-resubmit");
  const logicBuilderNext = $("logic-builder-next");
  const nextStepCopy = $("next-step-copy");
  const burdenAction = $("requirements-burden-action");
  const burdenOutputs = $("requirements-burden-outputs");
  const traceCount = $("clarification-trace-count");
  const traceList = $("clarification-trace-list");
  const graph = $("requirements-graph");
  const edges = $("requirements-edges");
  const graphCounts = $("graph-counts");
  const requirementsChoiceRows = Array.from(document.querySelectorAll("[data-requirement-choice-row]"));
  const requirementsRowPopover = $("requirements-row-popover");
  const requirementsPopoverTitle = $("requirements-popover-title");
  const requirementsPopoverSource = $("requirements-popover-source");
  const requirementsPopoverParams = $("requirements-popover-params");
  const requirementsPopoverUncertain = $("requirements-popover-uncertain");
  const requirementsManualToggle = $("requirements-manual-toggle");
  const requirementsManualBubble = $("requirements-manual-bubble");
  const requirementsShell = document.querySelector(".requirements-shell");
  const requirementsAuxPanels = {
    "source-popover": requirementsRowPopover,
    "manual-bubble": requirementsManualBubble,
  };

  function setStatus(text, tone) {
    statusLine.textContent = text;
    statusLine.dataset.tone = tone || "neutral";
  }

  function setActiveAuxPanel(name) {
    const panelName = name || "none";
    if (requirementsShell) {
      requirementsShell.dataset.activeAuxPanel = panelName;
      requirementsShell.dataset.unifiedInspectorState = panelName;
      requirementsShell.dataset.workstationState = panelName === "none" ? "primary" : panelName;
    }
    Object.entries(requirementsAuxPanels).forEach(([key, element]) => {
      if (element) element.dataset.unifiedPanelState = key === panelName ? "open" : "closed";
    });
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
    const activeIndex = PROCESS_STEP_ORDER.indexOf(activeStep);
    if (activeIndex < 0) return;
    PROCESS_STEP_ORDER.forEach((name, index) => {
      if (index > activeIndex) return;
      appendStreamChunk(name, STREAM_CHUNK_COPY[name], index === activeIndex ? "active" : "complete");
    });
  }

  function markStreamChunksFailed() {
    if (!streamChunks) return;
    streamChunks.querySelectorAll(".stream-chunk").forEach((chunk) => {
      if (chunk.dataset.state === "active") chunk.dataset.state = "error";
    });
  }

  function syncUploadMode() {
    form.setAttribute("data-upload-mode", state.uploadMode);
  }

  function safeUiError(payload, fallback) {
    if (payload && payload.error === "missing_api_key") {
      return "模型密钥未读取，请检查服务端环境变量后重试。";
    }
    if (payload && payload.error === "invalid_document_payload") {
      return "文档内容无法读取，请换用 DOCX/TXT/MD 后重试。";
    }
    return fallback;
  }

  function providerDisplayName(value) {
    return String(value || "deepseek").toLowerCase() === "minimax" ? "MiniMax" : "DeepSeek";
  }

  function defaultAnalyzeLabel() {
    return provider.value === "deepseek" && !state.providerLiveReady ? "检查：本地预解析" : "检查：分析需求";
  }

  function shouldUseOfflineOnly() {
    return provider.value === "deepseek" && deepseekLiveOnly && deepseekLiveOnly.checked && !state.providerLiveReady;
  }

  function syncAnalyzeButtonLabel() {
    if (!analyzeButton.disabled) analyzeButton.textContent = defaultAnalyzeLabel();
  }

  function setPreflightLiveState(text, stateName) {
    if (preflightLiveState) preflightLiveState.textContent = text;
    if (preflightLiveCard) preflightLiveCard.dataset.state = stateName || "checking";
  }

  function setProviderStatus(text, detail, stateName) {
    if (providerStatus) {
      providerStatus.textContent = text;
      providerStatus.dataset.state = stateName || "neutral";
      providerStatus.title = detail || text || "";
      providerStatus.setAttribute("aria-label", detail ? `${text}：${detail}` : text);
    }
    if (providerKeySource) {
      providerKeySource.textContent = detail || "";
    }
  }

  function syncLiveOnlyControl() {
    if (!deepseekLiveOnly) return;
    const selected = provider.value || "deepseek";
    if (selected === "deepseek") {
      deepseekLiveOnly.disabled = false;
      if (!deepseekLiveOnly.dataset.touched) {
        deepseekLiveOnly.checked = true;
      }
      return;
    }
    deepseekLiveOnly.checked = false;
    deepseekLiveOnly.disabled = true;
  }

  async function refreshProviderStatus() {
    const selected = provider.value || "deepseek";
    syncLiveOnlyControl();
    state.providerLiveReady = false;
    setPreflightLiveState("检查中", "checking");
    syncAnalyzeButtonLabel();
    setProviderStatus(`检查 ${providerDisplayName(selected)}`, "env 状态", "checking");
    try {
      const response = await fetch(`/api/requirements-intake/provider-status?provider=${encodeURIComponent(selected)}`, {
        headers: {"Accept": "application/json"},
      });
      const payload = await response.json();
      if (!response.ok) {
        state.providerLiveReady = false;
        setPreflightLiveState("异常", "error");
        syncAnalyzeButtonLabel();
        setProviderStatus(`${providerDisplayName(selected)} 异常`, payload.message || payload.error || "状态接口错误", "error");
        return;
      }
      const name = providerDisplayName(payload.provider || selected);
      if (payload.live_ready && payload.key_available) {
        state.providerLiveReady = true;
        setPreflightLiveState("已接入", "ok");
        syncAnalyzeButtonLabel();
        setProviderStatus(`${name} 已接入`, `${payload.model || "model?"} · ${payload.key_source || "key source?"}`, "ok");
        return;
      }
      state.providerLiveReady = false;
      setPreflightLiveState("未接入", "missing");
      syncAnalyzeButtonLabel();
      setProviderStatus(`${name} 未接入`, "env key 缺失", "error");
    } catch (error) {
      state.providerLiveReady = false;
      setPreflightLiveState("未知", "error");
      syncAnalyzeButtonLabel();
      setProviderStatus(`${providerDisplayName(selected)} 未知`, "状态接口不可用", "error");
    }
  }

  function formatElapsed(ms) {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const seconds = String(totalSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function setStepState(activeStep) {
    const activeIndex = PROCESS_STEP_ORDER.indexOf(activeStep);
    Object.entries(processSteps).forEach(([name, element]) => {
      const stepIndex = PROCESS_STEP_ORDER.indexOf(name);
      const isComplete = activeIndex >= 0 && stepIndex >= 0 && stepIndex < activeIndex;
      element.classList.toggle("is-active", name === activeStep);
      element.classList.toggle("is-complete", isComplete);
      element.dataset.state = name === activeStep ? "active" : (isComplete ? "complete" : "idle");
    });
  }

  function setProgress(percent, title, detail, activeStep) {
    state.taskPercent = Math.max(state.taskPercent, percent);
    processPanel.classList.add("is-active");
    processPanel.classList.remove("is-error", "is-complete");
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processFill.style.width = `${Math.min(state.taskPercent, 96)}%`;
    setStepState(activeStep);
    syncStreamChunks(activeStep);
  }

  function beginTask(title, detail, activeStep) {
    clearInterval(state.taskTimer);
    resetStreamChunks();
    state.taskStartedAt = Date.now();
    state.taskPercent = 4;
    processElapsed.textContent = "00:00";
    processPanel.classList.add("is-active");
    processPanel.classList.remove("is-error", "is-complete");
    setProgress(4, title, detail, activeStep);
    state.taskTimer = setInterval(() => {
      processElapsed.textContent = formatElapsed(Date.now() - state.taskStartedAt);
      if (state.taskPercent < 82) {
        state.taskPercent += state.taskPercent < 35 ? 2.6 : 0.8;
        processFill.style.width = `${Math.min(state.taskPercent, 82)}%`;
      }
    }, 500);
  }

  function finishTask(title, detail) {
    clearInterval(state.taskTimer);
    state.taskTimer = null;
    state.taskPercent = 100;
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processElapsed.textContent = formatElapsed(Date.now() - state.taskStartedAt);
    processFill.style.width = "100%";
    processPanel.classList.add("is-complete");
    processPanel.classList.remove("is-error");
    Object.values(processSteps).forEach((element) => {
      element.classList.remove("is-active");
      element.classList.add("is-complete");
      element.dataset.state = "complete";
    });
  }

  function failTask(title, detail) {
    clearInterval(state.taskTimer);
    state.taskTimer = null;
    processTitle.textContent = title;
    processDetail.textContent = detail;
    processElapsed.textContent = state.taskStartedAt ? formatElapsed(Date.now() - state.taskStartedAt) : "00:00";
    processPanel.classList.add("is-active", "is-error");
    processPanel.classList.remove("is-complete");
    Object.entries(processSteps).forEach(([name, element]) => {
      if (element.classList.contains("is-active")) element.dataset.state = "error";
      else if (!element.classList.contains("is-complete")) element.dataset.state = "idle";
    });
    markStreamChunksFailed();
  }

  function setBusy(isBusy, label) {
    analyzeButton.disabled = isBusy;
    clarificationResubmit.disabled = isBusy || clarificationResubmit.dataset.ready !== "true";
    clearButton.disabled = isBusy;
    provider.disabled = isBusy;
    if (replayImportButton) replayImportButton.disabled = isBusy;
    if (offlineActionButton) offlineActionButton.disabled = isBusy;
    if (deepseekLiveOnly) deepseekLiveOnly.disabled = isBusy || provider.value !== "deepseek";
    analyzeButton.textContent = isBusy ? label : defaultAnalyzeLabel();
    clarificationResubmit.textContent = isBusy ? "处理中..." : "提交澄清并继续";
  }

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

  function sourceAnchorQuote(anchors) {
    if (!Array.isArray(anchors) || anchors.length === 0) return "";
    return anchors
      .slice(0, 2)
      .map((anchor) => anchor.quote_zh || anchor.quote || "")
      .filter(Boolean)
      .join("；");
  }

  function nodeLabelByNeedle(nodes, needles, fallback) {
    const found = nodes.find((node) => {
      const haystack = `${node.id || ""} ${node.label || ""} ${node.description_zh || ""}`.toLowerCase();
      return needles.some((needle) => haystack.includes(needle));
    });
    return found ? (found.label || found.id || fallback) : fallback;
  }

  function renderRequirementsChoiceChecklist(payload) {
    const nodes = Array.isArray(payload && payload.concept_logic_nodes) ? payload.concept_logic_nodes : [];
    const ready = Boolean(payload && payload.ready_for_logic_builder);
    const values = {
      l1: nodeLabelByNeedle(nodes, ["l1", "logic1"], ready ? "已确认" : "待确认"),
      ra: nodeLabelByNeedle(nodes, ["ra", "radio_altitude"], ready ? "RA<6ft" : "待确认"),
      sw: nodeLabelByNeedle(nodes, ["sw1", "sw2"], ready ? "SW1/SW2" : "待确认"),
      vdt: nodeLabelByNeedle(nodes, ["vdt", "90"], ready ? "VDT90" : "待确认"),
    };
    Object.entries(values).forEach(([key, value]) => {
      const target = $(`requirements-choice-${key}`);
      if (target) target.textContent = value;
    });
  }

  function hideRequirementsRowPopover() {
    if (requirementsRowPopover) requirementsRowPopover.hidden = true;
    requirementsChoiceRows.forEach((row) => row.classList.remove("is-active"));
    if (requirementsShell && requirementsShell.dataset.activeAuxPanel === "source-popover") {
      setActiveAuxPanel("none");
    } else if (requirementsRowPopover) {
      requirementsRowPopover.dataset.unifiedPanelState = "closed";
    }
  }

  function showRequirementsRowPopover(row) {
    if (!row || !requirementsRowPopover) return;
    if (requirementsManualBubble) requirementsManualBubble.hidden = true;
    if (requirementsManualToggle) requirementsManualToggle.setAttribute("aria-expanded", "false");
    requirementsChoiceRows.forEach((candidate) => candidate.classList.toggle("is-active", candidate === row));
    if (requirementsPopoverTitle) requirementsPopoverTitle.textContent = row.querySelector(".requirements-choice-title")?.textContent || "需求项";
    if (requirementsPopoverSource) requirementsPopoverSource.textContent = row.dataset.source || "来源待确认。";
    if (requirementsPopoverParams) requirementsPopoverParams.textContent = row.dataset.params || "参数待确认。";
    if (requirementsPopoverUncertain) requirementsPopoverUncertain.textContent = row.dataset.uncertain || "暂无不确定项。";
    requirementsRowPopover.hidden = false;
    setActiveAuxPanel("source-popover");
  }

  function toggleManualBubble() {
    if (!requirementsManualBubble || !requirementsManualToggle) return;
    const nextHidden = !requirementsManualBubble.hidden ? true : false;
    if (!nextHidden) hideRequirementsRowPopover();
    requirementsManualBubble.hidden = nextHidden;
    requirementsManualToggle.setAttribute("aria-expanded", String(!nextHidden));
    setActiveAuxPanel(nextHidden ? "none" : "manual-bubble");
    if (!nextHidden) {
      const input = requirementsManualBubble.querySelector("textarea");
      if (input) input.focus();
    }
  }

  function hasInvalidModelOutput(payload) {
    return Boolean(payload && payload.recovery_state && payload.recovery_state.status === "invalid_model_output");
  }

  function hasLocalPreparse(payload) {
    return Boolean(payload && payload.deterministic_preparse && payload.deterministic_preparse.available);
  }

  function isTextDocument(file) {
    return /\.(txt|md|markdown|json|yaml|yml|csv|xml)$/i.test(file.name || "");
  }

  function readTextFile(file) {
    beginTask("读取文档", "正在读取文本文件，读取完成后即可开始分析。", "read");
    const reader = new FileReader();
    reader.onload = () => {
      state.uploadMode = "text";
      state.uploadBase64 = "";
      syncUploadMode();
      documentName.value = file.name || "requirements.txt";
      textArea.value = String(reader.result || "");
      fileState.textContent = `${Math.ceil(file.size / 1024)} KB`;
      finishTask("文档已载入", "文本文件读取完成，可以点击“分析需求”。");
      setStatus("文档已载入", "ok");
    };
    reader.onerror = () => {
      failTask("文件读取失败", "浏览器未能读取该文件，请换成 DOCX/TXT/MD 文档重试。");
      setStatus("文件读取失败", "error");
    };
    reader.readAsText(file);
  }

  function readDocxFile(file) {
    beginTask("读取 DOCX", "正在读取 Word 文档并准备上传给后端解析。", "read");
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = String(reader.result || "");
      state.uploadMode = "base64";
      state.uploadBase64 = dataUrl.split(",", 2)[1] || "";
      syncUploadMode();
      documentName.value = file.name || "requirements.docx";
      textArea.value = "";
      fileState.textContent = `${Math.ceil(file.size / 1024)} KB · DOCX`;
      finishTask("DOCX 已载入", "文档读取完成，点击“分析需求”后后端会提取正文并调用模型。");
      setStatus("DOCX 已载入", "ok");
    };
    reader.onerror = () => {
      failTask("文件读取失败", "浏览器未能读取该 DOCX，请确认文件没有损坏。");
      setStatus("文件读取失败", "error");
    };
    reader.readAsDataURL(file);
  }

  function acceptFile(file) {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setStatus("文件超过 10 MB", "error");
      return;
    }
    if (/\.docx$/i.test(file.name || "")) {
      readDocxFile(file);
      return;
    }
    if (/\.pdf$/i.test(file.name || "")) {
      setStatus("当前切片不接收 PDF", "error");
      return;
    }
    if (isTextDocument(file) || file.type.startsWith("text/")) {
      readTextFile(file);
      return;
    }
    setStatus("文件类型未启用", "error");
  }

  function renderQuestions(items) {
    questions.innerHTML = "";
    if (!items || items.length === 0) {
      questions.innerHTML = '<li class="muted">当前没有模型列出的阻塞问题。</li>';
      return;
    }
    for (const item of items) {
      const li = document.createElement("li");
      li.innerHTML = `
        <strong>${escapeText(item.prompt_zh || item.prompt || item.id)}</strong>
        <span class="question-rationale">${escapeText(item.rationale_zh || item.blocks || "")}</span>
        <span class="question-action">请在上方“澄清交互窗口”对应输入框中回答。</span>
      `;
      questions.appendChild(li);
    }
  }

  function questionIdentity(item, index) {
    return item.id || `q${index + 1}`;
  }

  function updateClarificationProgress() {
    const inputs = Array.from(clarificationList.querySelectorAll("textarea[data-question-id]"));
    const answered = inputs.filter((input) => input.value.trim()).length;
    clarificationProgress.textContent = `${answered}/${inputs.length} 已回答`;
    const ready = inputs.length > 0 && answered >= inputs.length;
    clarificationResubmit.dataset.ready = ready ? "true" : "false";
    clarificationResubmit.disabled = !ready;
  }

  function renderClarificationWorkbench(payload) {
    const items = payload.open_questions || [];
    clarificationList.innerHTML = "";
    clarificationResubmit.dataset.ready = "false";
    clarificationResubmit.disabled = true;
    if (!items.length) {
      clarificationProgress.textContent = "0/0 已回答";
      if (hasInvalidModelOutput(payload)) {
        const missing = (payload.recovery_state.missing_fields || []).join(" / ") || "节点 / 连线 / 摘要";
        const localAction = hasLocalPreparse(payload)
          ? '<button type="button" class="secondary" data-recovery-action="use-local">切换到本地预解析</button>'
          : '<button type="button" class="secondary" disabled>本地预解析不可用</button>';
        clarificationList.innerHTML = `
          <article class="clarification-card recovery-card">
            <div class="clarification-card-head">
              <strong>模型输出无效</strong>
              <code>recovery</code>
            </div>
            <p>本轮没有新的问题，也没有可绘制节点或连线；缺失字段：${escapeText(missing)}。</p>
            <div class="clarification-actions recovery-actions">
              <button type="button" data-recovery-action="retry">一键重试</button>
              ${localAction}
              <button type="button" class="secondary" data-recovery-action="missing">查看缺失字段</button>
              <button type="button" class="secondary" data-recovery-action="reopen">重新打开上一轮问题</button>
            </div>
          </article>
        `;
        return;
      }
      clarificationList.innerHTML = payload.status === "ready_for_logic_builder"
        ? '<p class="muted">澄清已完成，可以进入逻辑链路绘制。</p>'
        : '<p class="muted">模型没有返回问题，但结果仍不可进入下一步。请补充输入/输出、触发条件、门限、故障边界后重新分析。</p>';
      return;
    }
    items.forEach((item, index) => {
      const id = questionIdentity(item, index);
      const card = document.createElement("article");
      card.className = "clarification-card";
      card.innerHTML = `
        <div class="clarification-card-head">
          <strong>${escapeText(item.prompt_zh || item.prompt || id)}</strong>
          <code>${escapeText(item.blocks || "logic_builder")}</code>
        </div>
        <p>${escapeText(item.rationale_zh || "该信息会影响后续概念节点、参数或连线判断。")}</p>
        <label class="requirements-field">
          <span>工程师回答</span>
          <textarea data-question-id="${escapeText(id)}" data-question-prompt="${escapeText(item.prompt_zh || item.prompt || id)}" rows="3" placeholder="在这里输入你的澄清回答。全部问题回答后，点击“提交澄清并继续”。"></textarea>
        </label>
      `;
      clarificationList.appendChild(card);
    });
    clarificationList.querySelectorAll("textarea[data-question-id]").forEach((input) => {
      input.addEventListener("input", updateClarificationProgress);
    });
    updateClarificationProgress();
  }

  function renderNextStep(payload) {
    if (!payload) {
      logicBuilderNext.disabled = true;
      nextStepCopy.textContent = "先上传需求并点击分析；本步产出需求候选与澄清清单，下一页生成逻辑画布。";
      return;
    }
    const questionsCount = (payload.open_questions || []).length;
    const nodesCount = (payload.concept_logic_nodes || []).length;
    const edgesCount = (payload.concept_edges || []).length;
    const ready = payload.status === "ready_for_logic_builder" && payload.ready_for_logic_builder;
    logicBuilderNext.disabled = !ready;
    if (ready) {
      nextStepCopy.textContent = `本步产出已就绪：${nodesCount} 个概念节点、${edgesCount} 条连线候选；下一页生成逻辑画布。`;
    } else if (questionsCount > 0) {
      nextStepCopy.textContent = `还不能进入下一步：先回答 ${questionsCount} 个澄清问题，再产出可绘制需求候选。`;
    } else {
      nextStepCopy.textContent = "还不能进入下一步。当前输出缺少可用节点或连线，请补充控制目标、输入信号、输出命令、门限和故障边界后重新分析。";
    }
  }

  function renderBurdenSummary(payload) {
    if (!payload) {
      burdenAction.textContent = "等待分析";
      burdenOutputs.innerHTML = "<li>上传需求后只看 1 件事：是否能进入初版绘图。</li>";
      return;
    }
    const burden = payload.reading_burden || {};
    const outputs = Array.isArray(burden.key_outputs_zh) && burden.key_outputs_zh.length
      ? burden.key_outputs_zh
      : [
        `${(payload.concept_logic_nodes || []).length} 个概念节点`,
        `${(payload.concept_edges || []).length} 条逻辑链路`,
        (payload.source_scope && payload.source_scope.fault_injection && payload.source_scope.fault_injection.status === "source_deferred")
          ? "故障注入已按源文档暂缓"
          : ((payload.open_questions || []).length ? `${(payload.open_questions || []).length} 个澄清问题` : "可进入下一步"),
      ];
    burdenAction.textContent = burden.current_action_zh || (payload.ready_for_logic_builder ? "检查 L1-L4 结构后进入绘图。" : "先处理阻塞问题或恢复动作。");
    burdenOutputs.innerHTML = outputs.slice(0, 3).map((item) => `<li>${escapeText(item)}</li>`).join("");
  }

  function setWorkflowSteps(activeStep, completedSteps) {
    workflowSteps.forEach((element) => {
      const step = element.dataset.workflowStep || "";
      element.classList.toggle("is-active", step === activeStep);
      element.classList.toggle("is-complete", completedSteps.includes(step));
      element.classList.toggle("is-locked", !completedSteps.includes(step) && step !== activeStep);
    });
  }

  function blockingReason(payload) {
    const questionsCount = (payload.open_questions || []).length;
    const nodesCount = (payload.concept_logic_nodes || []).length;
    const edgesCount = (payload.concept_edges || []).length;
    if (payload.status === "ready_for_logic_builder" && payload.ready_for_logic_builder) {
      return "模型判断需求已足够进入逻辑链路绘制。";
    }
    if (questionsCount > 0) {
      return `模型仍需要 ${questionsCount} 个澄清回答。`;
    }
    if (!nodesCount) {
      return "模型没有返回可用概念节点，需要补充控制对象、输入信号和输出命令。";
    }
    if (!edgesCount) {
      return "模型没有返回可用连线候选，需要补充信号因果链路或门限关系。";
    }
    return "模型未放行下一步，需要补充需求边界后重新分析。";
  }

  function renderWorkflowOverview(payload) {
    if (!payload) {
      workflowStage.textContent = "需求澄清待开始";
      workflowDetail.textContent = "上传需求文档后，模型会先判断是否需要澄清，并准备下一页逻辑画布输入。";
      setWorkflowSteps("requirements", []);
      return;
    }
    if (payload.status === "ready_for_logic_builder" && payload.ready_for_logic_builder) {
      workflowStage.textContent = "可以进入初版绘图";
      workflowDetail.textContent = `需求已澄清：${(payload.concept_logic_nodes || []).length} 个概念节点和 ${(payload.concept_edges || []).length} 条连线候选将进入逻辑画布。`;
      setWorkflowSteps("drawing", ["requirements"]);
      return;
    }
    workflowStage.textContent = "需求仍需澄清";
    workflowDetail.textContent = blockingReason(payload);
    setWorkflowSteps("requirements", []);
  }

  function resetClarificationTrace() {
    state.analysisRounds = [];
    renderClarificationTrace();
  }

  function recordAnalysisRound(payload, submittedAnswers) {
    const questionsList = (payload.open_questions || []).map((item, index) => ({
      id: questionIdentity(item, index),
      prompt_zh: item.prompt_zh || item.prompt || item.id || `q${index + 1}`,
      blocks: item.blocks || "logic_builder",
    }));
    const answers = Array.isArray(submittedAnswers) ? submittedAnswers : [];
    state.analysisRounds.push({
      round: state.analysisRounds.length + 1,
      status: payload.status || "unknown",
      ready_for_logic_builder: Boolean(payload.ready_for_logic_builder),
      blocking_reason: blockingReason(payload),
      summary_zh: payload.summary_zh || "模型未返回摘要。",
      question_count: questionsList.length,
      node_count: (payload.concept_logic_nodes || []).length,
      edge_count: (payload.concept_edges || []).length,
      questions: questionsList,
      answers: answers.map((item) => ({
        prompt_zh: item.prompt_zh || item.question_id || "",
        answer_zh: item.answer_zh || "",
      })),
    });
    renderClarificationTrace();
  }

  function renderClarificationTrace() {
    traceCount.textContent = `${state.analysisRounds.length} rounds`;
    traceList.innerHTML = "";
    if (!state.analysisRounds.length) {
      traceList.innerHTML = '<p class="muted">每轮模型分析完成后，会在这里记录问题、回答和下一步判断。</p>';
      return;
    }
    for (const round of state.analysisRounds) {
      const card = document.createElement("article");
      card.className = "trace-round-card";
      card.dataset.status = round.ready_for_logic_builder ? "ready" : "blocked";
      const questionsHtml = round.questions.length
        ? `<ol>${round.questions.map((item) => `<li>${escapeText(item.prompt_zh)}<code>${escapeText(item.blocks)}</code></li>`).join("")}</ol>`
        : '<p class="muted">本轮没有新的阻塞问题。</p>';
      const answersHtml = round.answers.length
        ? `<ul>${round.answers.map((item) => `<li><strong>${escapeText(item.prompt_zh)}</strong><span>${escapeText(item.answer_zh)}</span></li>`).join("")}</ul>`
        : '<p class="muted">本轮为初始分析，未提交澄清回答。</p>';
      card.innerHTML = `
        <div class="trace-round-head">
          <strong>Round ${escapeText(round.round)}</strong>
          <span>${escapeText(round.status)}</span>
        </div>
        <p class="trace-reason">${escapeText(round.blocking_reason)}</p>
        <div class="trace-metrics">
          <span>${escapeText(round.question_count)} questions</span>
          <span>${escapeText(round.node_count)} nodes</span>
          <span>${escapeText(round.edge_count)} edges</span>
        </div>
        <p class="trace-summary">${escapeText(round.summary_zh)}</p>
        <details>
          <summary>模型问题</summary>
          ${questionsHtml}
        </details>
        <details>
          <summary>本轮回答</summary>
          ${answersHtml}
        </details>
      `;
      traceList.appendChild(card);
    }
  }

  function parameterValue(param) {
    const raw = param.default ?? param.min ?? 0;
    const value = Number(raw);
    return Number.isFinite(value) ? value : 0;
  }

  function renderParameter(param) {
    const min = Number.isFinite(Number(param.min)) ? Number(param.min) : 0;
    const max = Number.isFinite(Number(param.max)) ? Number(param.max) : Math.max(1, parameterValue(param));
    const value = Math.min(max, Math.max(min, parameterValue(param)));
    const unit = param.unit ? ` ${escapeText(param.unit)}` : "";
    return `
      <div class="parameter-panel">
        <div class="parameter-label">
          <span>${escapeText(param.label || param.id)}</span>
          <span>${escapeText(value)}${unit}</span>
        </div>
        <input type="range" min="${escapeText(min)}" max="${escapeText(max)}" value="${escapeText(value)}" disabled aria-label="${escapeText(param.label || param.id)}">
        <p class="parameter-source">${escapeText(sourceAnchorLabel(param.source_anchors) || param.source_hint || param.id || "")}</p>
      </div>
    `;
  }

  function renderGraph(nodes) {
    graph.innerHTML = "";
    if (!nodes || nodes.length === 0) {
      graph.innerHTML = '<p class="muted">无节点候选。</p>';
      return;
    }
    for (const node of nodes) {
      const card = document.createElement("article");
      card.className = "requirements-node-card";
      card.dataset.kind = node.node_kind || "logic";
      const params = Array.isArray(node.parameters) ? node.parameters.map(renderParameter).join("") : "";
      const anchorTitle = sourceAnchorQuote(node.source_anchors);
      if (anchorTitle) {
        card.title = anchorTitle;
      }
      card.innerHTML = `
        <span class="node-kind">${escapeText(node.node_kind || "logic")}</span>
        <div class="node-title">
          <strong>${escapeText(node.label || node.id)}</strong>
          <code>${escapeText(node.id)}</code>
        </div>
        <div class="node-description">${escapeText(node.description_zh || "")}</div>
        <p class="node-anchor">来源：${escapeText(sourceAnchorLabel(node.source_anchors))}</p>
        ${params}
      `;
      graph.appendChild(card);
    }
  }

  function renderEdges(items) {
    edges.innerHTML = "";
    if (!items || items.length === 0) {
      edges.innerHTML = '<p class="muted">无连线候选。</p>';
      return;
    }
    for (const item of items) {
      const row = document.createElement("div");
      row.className = "requirements-edge";
      row.dataset.status = item.endpoint_status || "resolved";
      row.innerHTML = `
        <span>${escapeText(item.source)} → ${escapeText(item.target)}</span>
        <span class="edge-label">${escapeText(item.label || item.endpoint_status || "")} · 来源：${escapeText(sourceAnchorLabel(item.source_anchors))}</span>
      `;
      edges.appendChild(row);
    }
  }

  function renderFlags(payload) {
    resultFlags.innerHTML = "";
    const providerName = payload.llm && payload.llm.provider === "local-preparse"
      ? "本地预解析"
      : ((payload.llm && payload.llm.provider === "minimax") ? "MiniMax" : "DeepSeek");
    const flags = [
      payload.controller_truth_modified ? "需复核控制逻辑" : "未改控制逻辑",
      payload.status === "ready_for_logic_builder" ? "可进入绘图" : "等待澄清",
      payload.certification_claim && payload.certification_claim !== "none" ? "含认证声明" : "无认证声明",
      providerName,
    ];
    for (const flag of flags) {
      const span = document.createElement("span");
      span.textContent = flag;
      resultFlags.appendChild(span);
    }
  }

  function renderPayload(payload) {
    state.lastPayload = payload;
    const concept_logic_nodes = payload.concept_logic_nodes || [];
    const concept_edges = payload.concept_edges || [];
    resultState.textContent = payload.status === "ready_for_logic_builder" ? "可进入逻辑链路" : "需要澄清";
    summary.textContent = payload.summary_zh || "模型未返回摘要。";
    renderFlags(payload);
    renderQuestions(payload.open_questions || []);
    renderClarificationWorkbench(payload);
    renderNextStep(payload);
    renderBurdenSummary(payload);
    renderWorkflowOverview(payload);
    renderRequirementsChoiceChecklist(payload);
    renderGraph(concept_logic_nodes);
    renderEdges(concept_edges);
    graphCounts.textContent = `${concept_logic_nodes.length} nodes · ${concept_edges.length} edges`;
    if (payload.status === "ready_for_logic_builder" && payload.ready_for_logic_builder) {
      window.localStorage.setItem(LOGIC_BUILDER_INPUT_KEY, JSON.stringify(payload));
    }
  }

  function readJsonDraft(key) {
    try {
      const raw = window.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function hydrateStoredRequirementsDraft() {
    const payload = readJsonDraft(LOGIC_BUILDER_INPUT_KEY);
    if (!payload || payload.kind !== "ai-fantui-requirements-intake-analysis") return false;
    state.preserveDownstreamDrafts = Boolean(window.localStorage.getItem(LOGIC_BUILDER_DRAWING_KEY));
    renderPayload(payload);
    setStatus("已恢复回放草稿", "ok");
    processDetail.textContent = "已从本地草稿恢复需求理解结果，可继续进入逻辑绘制或回放后续页面。";
    if (preflightReplayState) preflightReplayState.textContent = "回放已恢复";
    return true;
  }

  function assertReplayPayload(payload) {
    const required = [
      "requirements_payload",
      "drawing_payload",
      "fault_preparation_payload",
      "sandbox_plan_payload",
    ];
    for (const key of required) {
      if (!payload || !payload[key] || typeof payload[key] !== "object") {
        throw new Error(`回放包缺少 ${key}`);
      }
    }
  }

  function writeReplayDrafts(payload) {
    const faultPayload = {
      ...payload.fault_preparation_payload,
      boundary_answers: Array.isArray(payload.boundary_answers)
        ? payload.boundary_answers
        : payload.fault_preparation_payload.boundary_answers || [],
    };
    window.localStorage.setItem(LOGIC_BUILDER_INPUT_KEY, JSON.stringify(payload.requirements_payload));
    window.localStorage.setItem(LOGIC_BUILDER_DRAWING_KEY, JSON.stringify(payload.drawing_payload));
    window.localStorage.setItem(LOGIC_BUILDER_HISTORY_KEY, JSON.stringify(Array.isArray(payload.change_history) ? payload.change_history : []));
    window.localStorage.setItem(FAULT_DRAFT_KEY, JSON.stringify(faultPayload));
    window.localStorage.setItem(SANDBOX_PLAN_KEY, JSON.stringify(payload.sandbox_plan_payload));
    window.localStorage.removeItem(REVISION_HANDOFF_KEY);
  }

  async function importRequirementsReplay() {
    beginTask("导入回放", "正在读取真实 DeepSeek 回放包，不会重新调用模型。", "read");
    setStatus("导入回放中", "busy");
    setBusy(true, "导入中...");
    try {
      const response = await fetch(REPLAY_ENDPOINT, {cache: "no-store"});
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload && payload.error ? payload.error : "回放包读取失败");
      }
      assertReplayPayload(payload);
      writeReplayDrafts(payload);
      state.preserveDownstreamDrafts = true;
      resetClarificationTrace();
      renderPayload(payload.requirements_payload);
      finishTask("回放已导入", "需求、逻辑图、故障准备和沙盒计划已写入本地草稿。");
      setStatus("回放已导入", "ok");
      if (preflightReplayState) preflightReplayState.textContent = "回放已恢复";
    } catch (error) {
      const message = error.message || "回放导入失败，请确认本地服务可读取 replay API。";
      failTask("回放导入失败", message);
      setStatus("回放导入失败", "error");
    } finally {
      setBusy(false);
    }
  }

  function requestBody() {
    const body = {
      provider: provider.value,
      allow_fallback: !deepseekLiveOnly.checked,
      document_name: documentName.value.trim() || "requirements.md",
    };
    if (state.uploadMode === "base64" && state.uploadBase64) {
      body.document_base64 = state.uploadBase64;
      return body;
    }
    body.document_text = textArea.value;
    return body;
  }

  function clarificationAnswers() {
    return Array.from(clarificationList.querySelectorAll("textarea[data-question-id]"))
      .map((input) => ({
        question_id: input.dataset.questionId || "",
        prompt_zh: input.dataset.questionPrompt || "",
        answer_zh: input.value.trim(),
      }))
      .filter((item) => item.answer_zh);
  }

  function requestBodyWithClarifications() {
    return {
      ...requestBody(),
      clarification_answers: clarificationAnswers(),
    };
  }

  function localPreparsePayload(payload) {
    if (!payload || !payload.deterministic_preparse || payload.deterministic_preparse.applied) return null;
    const nodes = payload.deterministic_preparse.nodes || payload.deterministic_preparse.candidate_nodes || [];
    const edges = payload.deterministic_preparse.edges || payload.deterministic_preparse.candidate_edges || [];
    if (!nodes.length || !edges.length) return null;
    return {
      ...payload,
      status: "ready_for_logic_builder",
      ready_for_logic_builder: true,
      open_questions: [],
      concept_logic_nodes: nodes,
      concept_edges: edges,
      summary_zh: "已切换到本地预解析的 L1-L4 结构。",
      recovery_state: null,
      deterministic_preparse: {
        ...payload.deterministic_preparse,
        applied: true,
        reason: "user_selected_local_preparse",
      },
    };
  }

  async function retryLastAnalysis() {
    beginTask("重试模型", "正在用同一份文档和上一轮澄清回答重新分析。", "send");
    setStatus("重试中", "busy");
    setBusy(true, "重试中...");
    try {
      const payload = await submitAnalysis({
        ...requestBody(),
        clarification_answers: state.lastSubmittedAnswers,
      });
      recordAnalysisRound(payload, state.lastSubmittedAnswers);
      renderPayload(payload);
      focusClarificationIfNeeded(payload);
      finishTask("重试完成", payload.ready_for_logic_builder ? "已恢复为可绘图结构。" : "仍需处理恢复动作或澄清问题。");
      setStatus("重试完成", "ok");
    } catch (error) {
      const message = error.message || "重试失败，请切换模型或使用本地预解析。";
      failTask("重试失败", message);
      setStatus("失败", "error");
    } finally {
      setBusy(false);
    }
  }

  function reopenPreviousQuestions() {
    const previous = [...state.analysisRounds].reverse().find((round) => Array.isArray(round.questions) && round.questions.length);
    if (!previous) {
      clarificationList.insertAdjacentHTML("beforeend", '<p class="muted">没有可重新打开的上一轮问题。</p>');
      return;
    }
    renderClarificationWorkbench({
      status: "needs_clarification",
      open_questions: previous.questions.map((item) => ({
        id: item.id,
        prompt_zh: item.prompt_zh,
        blocks: item.blocks,
        rationale_zh: "这是上一轮模型提出的阻塞问题，可重新填写后提交。",
      })),
    });
  }

  function handleRecoveryAction(event) {
    const button = event.target.closest("[data-recovery-action]");
    if (!button) return;
    const action = button.dataset.recoveryAction;
    if (action === "retry") {
      retryLastAnalysis();
      return;
    }
    if (action === "use-local") {
      const localPayload = localPreparsePayload(state.lastPayload);
      if (localPayload) {
        recordAnalysisRound(localPayload, state.lastSubmittedAnswers);
        renderPayload(localPayload);
        finishTask("已切换本地预解析", "本地 L1-L4 结构已作为初版绘图输入。");
      }
      return;
    }
    if (action === "missing") {
      const missing = state.lastPayload && state.lastPayload.recovery_state
        ? (state.lastPayload.recovery_state.missing_fields || []).join(" / ")
        : "";
      processDetail.textContent = missing ? `缺失字段：${missing}` : "缺失字段：节点 / 连线 / 摘要。";
      return;
    }
    if (action === "reopen") {
      reopenPreviousQuestions();
    }
  }

  function runOfflineOnly(localPayload) {
    if (localPayload && localPayload.ready_for_logic_builder) {
      finishTask("本地预解析完成", "DeepSeek 未接入，已保留本地 L1-L4 候选，可继续进入逻辑绘制。");
      setStatus("本地候选可继续", "ok");
      if (preflightOfflineState) preflightOfflineState.textContent = "本地就绪";
      return;
    }
    throw new Error("DeepSeek 未接入，且本地预解析未形成可继续结构。请导入回放或配置模型后重试。");
  }

  function preserveLocalCandidateAfterEnhancementFailure(localPayload, error) {
    if (!localPayload || !localPayload.ready_for_logic_builder) return false;
    const message = error.message || "DeepSeek 增强失败，但本地候选已保留。";
    finishTask("DeepSeek 增强失败，可稍后重试", `${message} 当前页面保留本地预解析结果，可继续进入逻辑绘制。`);
    setStatus("DeepSeek 增强失败", "ok");
    if (preflightLiveState) preflightLiveState.textContent = "增强失败";
    return true;
  }

  async function submitAnalysis(body) {
    const response = await fetch("/api/requirements-intake/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "需求解析失败，请检查文档内容或切换模型后重试。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function submitLocalPreparse(body) {
    const response = await fetch("/api/requirements-intake/local-preparse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(safeUiError(payload, "本地预解析未能读取文档。"));
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function analyze(event) {
    event.preventDefault();
    resetClarificationTrace();
    state.lastSubmittedAnswers = [];
    state.preserveDownstreamDrafts = false;
    const body = requestBody();
    const offlineOnly = shouldUseOfflineOnly();
    beginTask("本地预解析", "正在先用本地规则抽取 L1-L4、RA/SW/TRA/VDT 和来源锚点。", "parse");
    setStatus("本地预解析中", "busy");
    setBusy(true, offlineOnly ? "本地预解析中..." : "分析中...");
    let localPayload = null;
    try {
      try {
        setProgress(18, "本地预解析", "先从文档正文生成可读的 L1-L4 候选结构。", "parse");
        localPayload = await submitLocalPreparse(body);
      } catch (localError) {
        localPayload = null;
      }
      if (localPayload && localPayload.ready_for_logic_builder) {
        recordAnalysisRound(localPayload, []);
        renderPayload(localPayload);
        setProgress(42, "本地预解析已就绪", "已先渲染本地 L1-L4 结构，DeepSeek 正在后台增强。", "send");
        setStatus("本地预解析已就绪", "ok");
      } else {
        setProgress(24, "提交 DeepSeek", "本地预解析未形成完整图纸，等待 DeepSeek live 分析。", "send");
        setStatus("分析中", "busy");
      }
      if (offlineOnly) {
        runOfflineOnly(localPayload);
        return;
      }
      const payload = await submitAnalysis(body);
      setProgress(88, "生成结果", "模型已返回，正在整理澄清问题、概念节点和下一步状态。", "render");
      recordAnalysisRound(payload, []);
      renderPayload(payload);
      focusClarificationIfNeeded(payload);
      finishTask("分析完成", payload.status === "ready_for_logic_builder" ? "需求已可进入逻辑链路绘制。" : "需求仍需澄清，请回答右侧问题后继续。");
      setStatus("完成", "ok");
    } catch (error) {
      if (preserveLocalCandidateAfterEnhancementFailure(localPayload, error)) {
        return;
      }
      resultState.textContent = "分析失败";
      const message = error.message || "需求解析失败，请检查文档内容或切换模型后重试。";
      summary.textContent = message;
      failTask("分析失败", message);
      setStatus("失败", "error");
    } finally {
      setBusy(false);
    }
  }

  function focusClarificationIfNeeded(payload) {
    if ((payload.open_questions || []).length === 0) return;
    const panel = document.querySelector(".clarification-primary");
    const firstInput = clarificationList.querySelector("textarea[data-question-id]");
    if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
    if (firstInput) setTimeout(() => firstInput.focus(), 250);
  }

  async function resubmitClarifications() {
    const submittedAnswers = clarificationAnswers();
    state.lastSubmittedAnswers = submittedAnswers;
    beginTask("合并澄清", "正在把你的回答并入需求文本，并启动下一轮模型分析。", "send");
    setStatus("合并澄清中", "busy");
    setBusy(true, "等待澄清结果...");
    try {
      setProgress(30, "提交澄清", "澄清回答已提交，等待模型重新判断需求是否清楚。", "send");
      const payload = await submitAnalysis({
        ...requestBody(),
        clarification_answers: submittedAnswers,
      });
      setProgress(88, "更新结果", "模型已返回，正在更新问题、概念图和下一步入口。", "render");
      recordAnalysisRound(payload, submittedAnswers);
      renderPayload(payload);
      focusClarificationIfNeeded(payload);
      finishTask("澄清完成", payload.status === "ready_for_logic_builder" ? "澄清已足够，可以进入逻辑链路绘制。" : "仍有问题需要回答，请继续澄清。");
      setStatus("澄清已合并", "ok");
    } catch (error) {
      resultState.textContent = "分析失败";
      const message = error.message || "澄清处理失败，请简化回答或切换模型后重试。";
      summary.textContent = message;
      failTask("澄清失败", message);
      setStatus("失败", "error");
    } finally {
      setBusy(false);
      updateClarificationProgress();
    }
  }

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      fileInput.click();
    }
  });
  dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("is-dragging");
  });
  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");
    acceptFile(event.dataTransfer.files[0]);
  });
  fileInput.addEventListener("change", () => acceptFile(fileInput.files[0]));

  clearButton.addEventListener("click", () => {
    state.uploadMode = "text";
    state.uploadBase64 = "";
    syncUploadMode();
    clearInterval(state.taskTimer);
    state.taskTimer = null;
    fileInput.value = "";
    documentName.value = "requirements.md";
    textArea.value = "";
    fileState.textContent = "未选择文件";
    state.lastPayload = null;
    state.lastSubmittedAnswers = [];
    state.preserveDownstreamDrafts = false;
    window.localStorage.removeItem(LOGIC_BUILDER_INPUT_KEY);
    window.localStorage.removeItem(LOGIC_BUILDER_DRAWING_KEY);
    window.localStorage.removeItem(LOGIC_BUILDER_HISTORY_KEY);
    window.localStorage.removeItem(FAULT_DRAFT_KEY);
    window.localStorage.removeItem(SANDBOX_PLAN_KEY);
    window.localStorage.removeItem(REVISION_HANDOFF_KEY);
    resetClarificationTrace();
    renderWorkflowOverview(null);
    renderRequirementsChoiceChecklist(null);
    renderQuestions([]);
    renderClarificationWorkbench({status: "idle", open_questions: []});
    renderNextStep(null);
    renderBurdenSummary(null);
    processPanel.classList.remove("is-active", "is-complete", "is-error");
    processTitle.textContent = "等待任务";
    processDetail.textContent = "上传或粘贴需求后开始分析。";
    processElapsed.textContent = "00:00";
    processFill.style.width = "0%";
    Object.values(processSteps).forEach((element) => element.classList.remove("is-active", "is-complete"));
    setStatus("待分析", "neutral");
  });

  clarificationResubmit.addEventListener("click", resubmitClarifications);
  clarificationList.addEventListener("click", handleRecoveryAction);
  provider.addEventListener("change", refreshProviderStatus);
  if (deepseekLiveOnly) {
    deepseekLiveOnly.addEventListener("change", () => {
      deepseekLiveOnly.dataset.touched = "true";
      syncAnalyzeButtonLabel();
    });
  }
  logicBuilderNext.addEventListener("click", () => {
    if (state.lastPayload && state.lastPayload.status === "ready_for_logic_builder" && state.lastPayload.ready_for_logic_builder) {
      window.localStorage.setItem(LOGIC_BUILDER_INPUT_KEY, JSON.stringify(state.lastPayload));
      if (!state.preserveDownstreamDrafts) {
        window.localStorage.removeItem(LOGIC_BUILDER_DRAWING_KEY);
        window.localStorage.removeItem(LOGIC_BUILDER_HISTORY_KEY);
        window.localStorage.removeItem(FAULT_DRAFT_KEY);
        window.localStorage.removeItem(SANDBOX_PLAN_KEY);
        window.localStorage.removeItem(REVISION_HANDOFF_KEY);
      }
    }
    window.location.href = "/logic-builder";
  });
  if (replayImportButton) {
    replayImportButton.addEventListener("click", importRequirementsReplay);
  }
  if (offlineActionButton) {
    offlineActionButton.addEventListener("click", () => {
      form.requestSubmit();
    });
  }
  form.addEventListener("submit", analyze);
  syncUploadMode();
  refreshProviderStatus();
  if (!hydrateStoredRequirementsDraft()) {
    renderWorkflowOverview(null);
    renderRequirementsChoiceChecklist(null);
    renderBurdenSummary(null);
  }

  requirementsChoiceRows.forEach((row) => {
    row.addEventListener("click", () => showRequirementsRowPopover(row));
    row.addEventListener("mouseenter", () => showRequirementsRowPopover(row));
  });
  if (requirementsManualToggle) {
    requirementsManualToggle.addEventListener("click", toggleManualBubble);
  }
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      hideRequirementsRowPopover();
      if (requirementsManualBubble) requirementsManualBubble.hidden = true;
      if (requirementsManualToggle) requirementsManualToggle.setAttribute("aria-expanded", "false");
      setActiveAuxPanel("none");
    }
  });
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (
      requirementsRowPopover
      && !requirementsRowPopover.hidden
      && !target.closest("[data-requirement-choice-row]")
      && !target.closest("#requirements-row-popover")
    ) {
      hideRequirementsRowPopover();
    }
  });
  setActiveAuxPanel("none");
})();

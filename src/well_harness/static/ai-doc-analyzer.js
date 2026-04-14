/**
 * ai-doc-analyzer.js -- P14 AI Document Analyzer UI logic
 */

"use strict";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

/** @type {string|null} Current session ID */
let _sessionId = null;

/** @type {string|null} Current document text */
let _documentText = null;

/** @type {string|null} Current document name */
let _documentName = null;

/** @type {Object|null} Current intake packet (P15) */
let _intakePacket = null;

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

/**
 * POST /api/p14/analyze-document
 * @param {string} sessionId
 * @param {string} documentText
 * @param {string} documentName
 * @returns {Promise<Object>} JSON response
 */
async function p14Analyze(sessionId, documentText, documentName) {
  const response = await fetch("/api/p14/analyze-document", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      document_text: documentText,
      document_name: documentName,
    }),
  });
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.message || data.error || "analyze failed");
  }
  return data;
}

/**
 * POST /api/p14/clarify
 * @param {string} sessionId
 * @param {string} answer
 * @returns {Promise<Object>} JSON response
 */
async function p14Clarify(sessionId, answer) {
  const response = await fetch("/api/p14/clarify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      answer: answer,
    }),
  });
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.message || data.error || "clarify failed");
  }
  return data;
}

/**
 * POST /api/p14/generate-prompt
 * @param {string} sessionId
 * @returns {Promise<Object>} JSON response
 */
async function p14Generate(sessionId) {
  const response = await fetch("/api/p14/generate-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.message || data.error || "generate failed");
  }
  return data;
}

/**
 * POST /api/p15/convert-to-intake
 * @param {string} sessionId
 * @param {string} [systemId]
 * @returns {Promise<Object>} JSON response
 */
async function p15Convert(sessionId, systemId) {
  const response = await fetch("/api/p15/convert-to-intake", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      system_id: systemId || "generated-system",
    }),
  });
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.message || data.error || "p15 convert failed");
  }
  return data;
}

/**
 * POST /api/p15/run-pipeline
 * @param {Object} intakePacket
 * @returns {Promise<Object>} JSON response
 */
async function p15RunPipeline(intakePacket) {
  const response = await fetch("/api/p15/run-pipeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ intake_packet: intakePacket }),
  });
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.message || data.error || "p15 pipeline failed");
  }
  return data;
}

// ---------------------------------------------------------------------------
// DOM element references
// ---------------------------------------------------------------------------

const _dropZone = document.getElementById("ai-doc-drop-zone");
const _fileInput = document.getElementById("ai-doc-file-input");
const _fileMeta = document.getElementById("ai-doc-file-meta");
const _previewTextarea = document.getElementById("ai-doc-preview");
const _analyzeBtn = document.getElementById("ai-doc-analyze-btn");
const _charCount = document.getElementById("ai-doc-char-count");
const _wordCount = document.getElementById("ai-doc-word-count");
const _uploadError = document.getElementById("ai-doc-upload-error");
const _mockBadge = document.getElementById("ai-doc-mock-badge");
const _apiErrorHint = document.getElementById("ai-doc-api-error-hint");
const _ambiguityList = document.getElementById("ai-doc-ambiguity-list");
const _clarificationArea = document.getElementById("ai-doc-clarification-area");
const _sufficientMsg = document.getElementById("ai-doc-sufficient-msg");
const _promptPreview = document.getElementById("ai-doc-prompt-preview");
const _promptWordCount = document.getElementById("ai-doc-prompt-word-count");
const _promptStatus = document.getElementById("ai-doc-prompt-status");
const _downloadBtn = document.getElementById("ai-doc-download-btn");
const _generateError = document.getElementById("ai-doc-generate-error");
const _sessionDisplay = document.getElementById("ai-doc-session-display");
const _pipelineBtn = document.getElementById("ai-doc-pipeline-btn");
const _pipelineResultArea = document.getElementById("ai-doc-pipeline-result");
const _pipelineStatus = document.getElementById("ai-doc-pipeline-status");

const MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB

// ---------------------------------------------------------------------------
// File upload handling
// ---------------------------------------------------------------------------

function _showUploadError(msg) {
  _uploadError.textContent = msg;
  _uploadError.style.display = "block";
}

function _hideUploadError() {
  _uploadError.style.display = "none";
  _uploadError.textContent = "";
}

function _updateCharWordCount(text) {
  const chars = text ? text.length : 0;
  const words = text ? text.trim().split(/\s+/).filter(Boolean).length : 0;
  _charCount.textContent = chars.toLocaleString() + " characters";
  _wordCount.textContent = words.toLocaleString() + " words";
}

function _handleFile(file) {
  _hideUploadError();

  if (!file) return;

  const name = file.name.toLowerCase();
  const allowedExts = [".md", ".txt", ".docx", ".pdf"];
  const ext = allowedExts.find(function (e) { return name.endsWith(e); });
  if (!ext) {
    _showUploadError("Unsupported file type. Please upload .md, .txt, .docx, or .pdf.");
    _fileMeta.textContent = "";
    _previewTextarea.value = "";
    _documentText = null;
    _documentName = null;
    _analyzeBtn.disabled = true;
    _updateCharWordCount("");
    return;
  }

  if (file.size > MAX_FILE_BYTES) {
    _showUploadError("File too large (" + (file.size / 1024 / 1024).toFixed(1) + "MB). Maximum is 10MB.");
    return;
  }

  _fileMeta.textContent = file.name + " - " + (file.size / 1024).toFixed(1) + " KB";

  const reader = new FileReader();
  reader.onload = function (e) {
    const text = e.target.result;
    _documentText = text;
    _documentName = file.name;
    _previewTextarea.value = text;
    _updateCharWordCount(text);
    _analyzeBtn.disabled = false;
    _clearResults();
  };
  reader.onerror = function () {
    _showUploadError("Failed to read file. Please try again.");
  };
  reader.readAsText(file);
}

// Drag-and-drop
_dropZone.addEventListener("dragover", function (e) {
  e.preventDefault();
  _dropZone.classList.add("is-dragover");
});

_dropZone.addEventListener("dragleave", function (e) {
  e.preventDefault();
  _dropZone.classList.remove("is-dragover");
});

_dropZone.addEventListener("drop", function (e) {
  e.preventDefault();
  _dropZone.classList.remove("is-dragover");
  var droppedFile = e.dataTransfer.files[0];
  _handleFile(droppedFile);
});

// Keyboard accessibility
_dropZone.addEventListener("keydown", function (e) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    _fileInput.click();
  }
});

_fileInput.addEventListener("change", function () {
  _handleFile(this.files[0]);
});

// ---------------------------------------------------------------------------
// Results clearing
// ---------------------------------------------------------------------------

function _clearResults() {
  _ambiguityList.innerHTML =
    "<p style=\"color: rgba(200,240,255,0.35); font-size: 0.82rem;\">" +
    "Upload a document and click \"Start AI Analysis\" to see detection results here.</p>";
  _clarificationArea.innerHTML =
    "<div style=\"color: rgba(200,240,255,0.35); font-size: 0.82rem; padding: 1rem 0;\">" +
    "After AI analysis completes, clarification questions will appear here one by one.</div>";
  _sufficientMsg.style.display = "none";
  _promptPreview.value = "";
  _promptWordCount.textContent = "--";
  _promptStatus.textContent = "Waiting for generation";
  _generateError.style.display = "none";
  _generateError.textContent = "";
  _downloadBtn.disabled = true;
}

// ---------------------------------------------------------------------------
// Analyze flow
// ---------------------------------------------------------------------------

_analyzeBtn.addEventListener("click", async function () {
  if (!_documentText || !_documentName) return;

  _hideUploadError();
  _analyzeBtn.disabled = true;
  _analyzeBtn.classList.add("is-loading");
  _analyzeBtn.textContent = "Analyzing...";

  try {
    _sessionId = crypto.randomUUID ? crypto.randomUUID() :
      "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === "x" ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    _sessionDisplay.textContent = "Session: " + _sessionId.slice(0, 8) + "...";

    var result = await p14Analyze(_sessionId, _documentText, _documentName);

    _renderAmbiguityCards(result.ambiguities || []);
    _renderClarificationArea(result.first_question, result.progress);

    if (result.is_complete) {
      _sufficientMsg.style.display = "block";
    }

    if (result.error === "anthropic_api_key_missing") {
      _mockBadge.style.display = "inline";
      _apiErrorHint.style.display = "inline";
    }

  } catch (err) {
    _showUploadError("Analysis failed: " + err.message);
    if (err.message.indexOf("anthropic_api_key_missing") !== -1 ||
        err.message.indexOf("API Key") !== -1) {
      _mockBadge.style.display = "inline";
      _apiErrorHint.style.display = "inline";
    }
  } finally {
    _analyzeBtn.disabled = false;
    _analyzeBtn.classList.remove("is-loading");
    _analyzeBtn.textContent = "Start AI Analysis";
  }
});

// ---------------------------------------------------------------------------
// Render ambiguity cards
// ---------------------------------------------------------------------------

function _renderAmbiguityCards(ambiguities) {
  if (!ambiguities || ambiguities.length === 0) {
    _ambiguityList.innerHTML =
      "<p style=\"color: rgba(83,255,146,0.7); font-size: 0.88rem;\">" +
      "No ambiguities detected. Document is clear.</p>";
    return;
  }

  var html = ambiguities.map(function (amb) {
    var pct = Math.round(amb.confidence_score * 100);
    var levelClass = pct >= 75 ? "is-high" : pct >= 50 ? "is-medium" : "is-low";
    var barClass = pct >= 75 ? "is-high" : pct >= 50 ? "is-medium" : "is-low";

    return [
      '<div class="ai-doc-ambiguity-card ' + levelClass + '">',
      '  <div class="ai-doc-ambiguity-id">' + _escHtml(amb.id) + '</div>',
      '  <div class="ai-doc-ambiguity-excerpt">' + _escHtml(amb.text_excerpt) + '</div>',
      '  <div class="ai-doc-ambiguity-desc">' + _escHtml(amb.description) + '</div>',
      '  <div class="ai-doc-confidence-row">',
      '    <span class="ai-doc-confidence-label">Confidence</span>',
      '    <div class="ai-doc-confidence-bar-track">',
      '      <div class="ai-doc-confidence-bar-fill ' + barClass + '" style="width:' + pct + '%"></div>',
      "    </div>",
      '    <span class="ai-doc-confidence-pct">' + pct + '%</span>',
      "  </div>",
      "</div>",
    ].join("");
  }).join("");

  _ambiguityList.innerHTML = html;
}

// ---------------------------------------------------------------------------
// Render clarification area
// ---------------------------------------------------------------------------

function _renderClarificationArea(firstQuestion, progress) {
  if (!firstQuestion) {
    _clarificationArea.innerHTML =
      "<div style=\"color: rgba(83,255,146,0.7); font-size: 0.88rem;\">" +
      "All questions confirmed. No more input needed.</div>";
    return;
  }

  var answered = progress ? progress.answered : 0;
  var remaining = progress ? progress.remaining : "?";
  var total = answered + remaining + 1;
  var isOptional = firstQuestion.is_optional;

  var skipBtnHtml = isOptional ?
    '<button type="button" class="ai-doc-skip-btn" id="ai-doc-skip-btn">Skip</button>' :
    "";

  var html =
    '<div class="ai-doc-clarification-card">' +
    '  <div class="ai-doc-progress-label">Question ' + (answered + 1) + " / " + total + "</div>" +
    '  <div class="ai-doc-question-text">' + _escHtml(firstQuestion.question) + "</div>" +
    '  <input type="text" class="ai-doc-answer-input" id="ai-doc-answer-input" ' +
    '     placeholder="Enter your answer and press Enter or click Submit" ' +
    '     aria-label="Answer input" autocomplete="off">' +
    '  <div class="ai-doc-submit-row">' +
    '    <button type="button" class="ai-doc-submit-btn" id="ai-doc-submit-btn">Submit Answer</button>' +
    skipBtnHtml +
    "  </div>" +
    "</div>";

  _clarificationArea.innerHTML = html;

  // Wire events
  var submitBtn = document.getElementById("ai-doc-submit-btn");
  var answerInput = document.getElementById("ai-doc-answer-input");
  var skipBtn = document.getElementById("ai-doc-skip-btn");

  submitBtn.addEventListener("click", function () {
    var answer = answerInput.value.trim();
    if (!answer) {
      answerInput.focus();
      return;
    }
    _handleClarifyAnswer(answer);
  });

  answerInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitBtn.click();
    }
  });

  if (skipBtn) {
    skipBtn.addEventListener("click", function () {
      _handleClarifyAnswer("");
    });
  }

  answerInput.focus();
}

// ---------------------------------------------------------------------------
// Clarification loop
// ---------------------------------------------------------------------------

async function _handleClarifyAnswer(answer) {
  if (!_sessionId) return;

  var submitBtn = document.getElementById("ai-doc-submit-btn");
  var answerInput = document.getElementById("ai-doc-answer-input");
  var skipBtn = document.getElementById("ai-doc-skip-btn");

  if (submitBtn) submitBtn.disabled = true;
  if (answerInput) answerInput.disabled = true;
  if (skipBtn) skipBtn.disabled = true;

  try {
    var result = await p14Clarify(_sessionId, answer);

    if (result.is_complete) {
      _sufficientMsg.style.display = "block";
      _clarificationArea.innerHTML =
        "<div style=\"color: rgba(83,255,146,0.7); font-size: 0.88rem;\">" +
        "All questions confirmed. Generating Prompt document...</div>";
      await _triggerGenerate();
    } else if (result.next_question) {
      _renderClarificationArea(result.next_question, result.progress);
    }

  } catch (err) {
    var clarifyErr = document.createElement("div");
    clarifyErr.className = "ai-doc-error";
    clarifyErr.style.display = "block";
    clarifyErr.textContent = "Submit failed: " + err.message;
    _clarificationArea.appendChild(clarifyErr);

    // Re-enable inputs on error
    if (submitBtn) submitBtn.disabled = false;
    if (answerInput) answerInput.disabled = false;
    if (skipBtn) skipBtn.disabled = false;
  }
}

// ---------------------------------------------------------------------------
// Generate flow
// ---------------------------------------------------------------------------

async function _triggerGenerate() {
  if (!_sessionId) return;

  _generateError.style.display = "none";
  _generateError.textContent = "";
  _promptStatus.textContent = "Generating...";

  try {
    var result = await p14Generate(_sessionId);
    _promptPreview.value = result.prompt_document || "";
    _promptWordCount.textContent = (result.word_count || 0).toLocaleString() + " words";
    _promptStatus.textContent = "Generated";
    _downloadBtn.disabled = false;

    // Auto-fetch the intake packet (P15) after prompt generation
    var convertResult;
    try {
      convertResult = await p15Convert(_sessionId);
      _intakePacket = convertResult.intake_packet || null;
    } catch (e) {
      console.warn("P15 convert failed (non-fatal):", e.message);
      _intakePacket = null;
    }

    if (_intakePacket && _pipelineBtn) {
      _pipelineBtn.disabled = false;
      _pipelineStatus.textContent = "Ready to run pipeline";
    }
  } catch (err) {
    _generateError.textContent = "Generation failed: " + err.message;
    _generateError.style.display = "block";
    _promptStatus.textContent = "Generation failed";
  }
}

// ---------------------------------------------------------------------------
// P15 Run Pipeline
// ---------------------------------------------------------------------------

if (_pipelineBtn) {
  _pipelineBtn.addEventListener("click", async function () {
    if (!_intakePacket) {
      alert("Intake packet not available. Please generate the prompt document first.");
      return;
    }

    _pipelineBtn.disabled = true;
    _pipelineStatus.textContent = "Running pipeline...";

    try {
      var result = await p15RunPipeline(_intakePacket);

      var bundle = result.bundle || {};
      var snapshot = result.system_snapshot || {};
      var assessment = result.assessment || {};
      const _intakeJson = JSON.stringify(_intakePacket, null, 2);
      const _workbenchUrl = "/workbench.html?intake=" + encodeURIComponent(_intakeJson);

      var html =
        '<div class="ai-doc-pipeline-result-card">' +
        '  <div class="ai-doc-pipeline-result-title">Pipeline 执行结果</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">System ID:</span> ' + _escHtml(snapshot.system_id || "—") + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Title:</span> ' + _escHtml(snapshot.title || "—") + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Bundle Kind:</span> ' + _escHtml(bundle.bundle_kind || "—") + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Components:</span> ' + (snapshot.component_count || 0) + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Logic Nodes:</span> ' + (snapshot.logic_node_count || 0) + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Scenarios:</span> ' + (snapshot.acceptance_scenario_count || 0) + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Fault Modes:</span> ' + (snapshot.fault_mode_count || 0) + '</div>' +
        '  <div class="ai-doc-pipeline-result-row"><span class="label">Ready for Spec Build:</span> ' +
        (snapshot.ready_for_spec_build ? '<span style="color:#53ff92">Yes</span>' : '<span style="color:#ffcc53">No</span>') + '</div>';

      if (bundle.scenario_count !== undefined) {
        html += '<div class="ai-doc-pipeline-result-row"><span class="label">Playback Scenarios:</span> ' + bundle.scenario_count + '</div>';
      }

      html +=
        '  <div class="ai-doc-pipeline-result-actions">' +
        '    <a href="' + _workbenchUrl + '" target="_blank" rel="noopener noreferrer" class="ai-doc-pipeline-action-btn" style="display:inline-block;margin-top:8px;padding:6px 14px;background:rgba(40,244,255,0.12);border:1px solid rgba(40,244,255,0.4);color:#28f4ff;border-radius:6px;text-decoration:none;font-size:0.82rem">' +
        "      ↗ 在 Workbench 中查看诊断" +
        "    </a>" +
        "  </div>";

      html += "</div>";

      _pipelineResultArea.innerHTML = html;
      _pipelineResultArea.style.display = "block";
      _pipelineStatus.textContent = "Pipeline completed";
      _pipelineBtn.disabled = false;
    } catch (err) {
      _pipelineResultArea.innerHTML =
        '<div class="ai-doc-error" style="display:block;">Pipeline failed: ' + _escHtml(err.message) + '</div>';
      _pipelineResultArea.style.display = "block";
      _pipelineStatus.textContent = "Pipeline failed";
      _pipelineBtn.disabled = false;
    }
  });
}

// ---------------------------------------------------------------------------
// Download
// ---------------------------------------------------------------------------

_downloadBtn.addEventListener("click", function () {
  var text = _promptPreview.value;
  if (!text) return;

  var blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "logic-mvp-claude-prompt.md";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

/**
 * Escape HTML special characters to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function _escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
